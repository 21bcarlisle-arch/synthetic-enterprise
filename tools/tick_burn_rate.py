"""What each kind of unattended Claude turn costs, per model, read from Claude Code's own transcripts.

THE DIRECTOR'S QUESTION (2026-09-27): *"We also need to see the burn rate for each of the ticks with
opus 5.5. We should review this towards the end of each week."* It is answered for the Friday review
(`background.weekly_rhythm`), which states the week's table and proposes changes.

WHAT THIS IS NOT. It does not measure, estimate or forecast the director's remaining allowance, and
nothing may read it as a reason to slow down: that mechanism was mothballed by him ("better to hit
the limit"; `token-proxy` is `retired` in `background/process_manifest.yaml`). This measures what a
TURN costs, so that a change to cadence, model or effort can be judged on evidence.

THE SOURCE is the transcript Claude Code writes for every session
(`~/.claude/projects/<cwd-slug>/<session>.jsonl`): each assistant message carries `model` and
`usage`. Nothing is added to any daemon. A turn's KIND is read from its opening prompt, the one
thing each seat writes identically every time.

THE WEIGHTED FIGURE prices each token class at the model's published list price, so that Opus 5 and
5.5 are comparable on one number (5.5's cache reads cost 5% of input where 5's cost 10%). It is a
relative measure of burn, not a bill: these turns run on a subscription.

REUSE: tools/tick_burn_rate.py
CLASS: CUSTOM
INDEX: searched "tick burn rate", "token usage per session", "transcript usage" --
       `background/token_proxy.py` measured tokens at the network and is retired by the director;
       `tools/console_instruction_record.py` reads the transcripts for the director's own words
       and never their usage; `tools/model_tier_report.py` reports which tier was DRAWN, not what
       a turn cost. Nothing reads per-turn usage.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"

#: A turn's kind, from the first words of its opening prompt. Unknown openings are counted, never
#: dropped, so a new seat shows up as `other` rather than vanishing from the table.
KINDS = (
    ("worker_tick", "You are the autonomous worker, woken by a scheduled tick"),
    ("seat_executor", "You are the delivery seat, continuing work autonomously"),
    ("delivery_seat", "You hold the DELIVERY SEAT on this project"),
    ("worker_seat", "Worker seat (re)started under systemd"),
)

#: $ per million tokens, Anthropic's published list (platform.claude.com/docs/en/about-claude/pricing,
#: read 2026-09-27): input, output, 5-minute cache write, 1-hour cache write, cache read.
PRICE = {
    "claude-opus-5-5": (4.0, 20.0, 5.0, 8.0, 0.20),
    "claude-opus-5": (5.0, 25.0, 6.25, 10.0, 0.50),
    "claude-sonnet-5": (2.0, 10.0, 2.50, 4.0, 0.20),
    "claude-haiku-4-5-20251001": (1.0, 5.0, 1.25, 2.0, 0.10),
}


def kind_of(opening: str) -> str:
    text = opening.strip()
    for kind, prefix in KINDS:
        if text.startswith(prefix):
            return kind
    return "other"


def _text(content) -> str:
    if isinstance(content, str):
        return content
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            return block.get("text", "")
    return ""


def read_turn(path: Path) -> dict | None:
    """One session file -> {kind, model, tokens by class, weighted $, started}; None if it is not a turn."""
    opening, model, started = None, None, None
    tot = defaultdict(int)
    weighted = 0.0
    for line in path.read_text(errors="replace").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        started = started or row.get("timestamp")
        if row.get("type") == "user" and opening is None:
            opening = _text((row.get("message") or {}).get("content"))
        if row.get("type") != "assistant":
            continue
        msg = row.get("message") or {}
        u = msg.get("usage") or {}
        if not u:
            continue
        if (msg.get("model") or "").startswith("<"):   # `<synthetic>`: a harness placeholder, not a model call
            continue
        model = msg.get("model") or model
        cc = u.get("cache_creation") or {}
        w5 = int(cc.get("ephemeral_5m_input_tokens", 0) or 0)
        w1 = int(cc.get("ephemeral_1h_input_tokens", 0) or 0)
        if not (w5 or w1):
            w5 = int(u.get("cache_creation_input_tokens", 0) or 0)
        parts = {"input": int(u.get("input_tokens", 0) or 0), "output": int(u.get("output_tokens", 0) or 0),
                 "cache_write": w5 + w1, "cache_read": int(u.get("cache_read_input_tokens", 0) or 0)}
        for k, v in parts.items():
            tot[k] += v
        price = PRICE.get(msg.get("model") or "")
        if price:
            pi, po, p5, p1, pr = price
            weighted += (parts["input"] * pi + parts["output"] * po + w5 * p5 + w1 * p1
                         + parts["cache_read"] * pr) / 1e6
    if opening is None or model is None:
        return None
    return {"kind": kind_of(opening), "model": model, "started": started, "weighted_usd": weighted,
            **dict(tot)}


def turns(days: float = 7.0, now: float | None = None, root: Path = PROJECTS) -> list[dict]:
    cutoff = (now or time.time()) - days * 86400
    out = []
    for path in root.glob("*/*.jsonl"):
        if path.stat().st_mtime < cutoff:
            continue
        turn = read_turn(path)
        if turn is not None:
            out.append(turn)
    return out


def table(rows: list[dict], days: float) -> list[dict]:
    groups = defaultdict(list)
    for r in rows:
        groups[(r["kind"], r["model"])].append(r)
    out = []
    for (kind, model), rs in sorted(groups.items()):
        w = [r["weighted_usd"] for r in rs]
        fresh = [r.get("input", 0) + r.get("cache_write", 0) + r.get("output", 0) for r in rs]
        out.append({"kind": kind, "model": model, "turns": len(rs), "turns_per_day": round(len(rs) / days, 1),
                    "median_fresh_tokens": int(statistics.median(fresh)),
                    "median_cache_read_tokens": int(statistics.median(r.get("cache_read", 0) for r in rs)),
                    "median_weighted_usd": round(statistics.median(w), 3),
                    "week_weighted_usd": round(sum(w), 2)})
    return out


def render(days: float = 7.0, now: float | None = None, root: Path = PROJECTS) -> str:
    rows = table(turns(days, now, root), days)
    if not rows:
        return f"No turns found in the last {days:g} days under `{root}` -- nothing measured, which is not zero."
    head = ("| kind | model | turns | per day | median fresh tokens | median cache-read tokens "
            "| median weighted $ | total weighted $ |\n|---|---|---|---|---|---|---|---|")
    body = "\n".join(f"| {r['kind']} | {r['model']} | {r['turns']} | {r['turns_per_day']} | "
                     f"{r['median_fresh_tokens']:,} | {r['median_cache_read_tokens']:,} | "
                     f"{r['median_weighted_usd']} | {r['week_weighted_usd']} |" for r in rows)
    return head + "\n" + body


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=float, default=7.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.json:
        print(json.dumps(table(turns(a.days), a.days), indent=1))
    else:
        print(render(a.days))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
