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
import re
import statistics
import time
from collections import defaultdict
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"

#: A turn LANDED if its tool results carry the landing door's own success line. The executor and the
#: ticks land through `tools.surgical_land`; an orientation turn never lands (its record is committed
#: for it), so its rate is reported as not applicable rather than as a false 0%.
_LANDED = re.compile(r"\[surgical-land\] landed [0-9a-f]{7,}")

#: PROMPT CHANGES UNDER MEASUREMENT (director, 2026-09-29): "compare landing rate per turn type
#: before and after in the Friday burn review, and put the capitals back if plain wording lands
#: less." A turn's variant is read from the prompt it actually RECEIVED -- its own transcript --
#: so the split needs no change timestamp and cannot mis-assign a turn that ran on a stale checkout.
PROMPT_CHANGES = (
    {"id": "prompt-audit-2026-09-29", "kind": "seat_executor",
     "old": "THIS IS WHAT THE TURN IS JUDGED ON", "new": "Run it with --work-id: that is what records",
     "reverse": "restore the capitalised line in the `background.seat_executor` CHARTER"},
    {"id": "prompt-audit-2026-09-29", "kind": "worker_tick",
     "old": "then STOP and exit cleanly", "new": "via tree_lock, and exit.",
     "reverse": "restore the capitalised `background.worker_tick` WORKER_PREAMBLE"},
)

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
    "claude-sonnet-5-5": (2.0, 10.0, 2.50, 4.0, 0.10),   # read 2026-10-23: half Opus 5.5 on every class
    "claude-sonnet-5": (2.0, 10.0, 2.50, 4.0, 0.20),
    "claude-fable-5-1": (10.0, 50.0, 12.50, 20.0, 0.25),
    # Haiku 5.5 is NOT here: its list price is tiered by prompt length (USD 0.10/0.50 input up to and
    # over 100k tokens), which one row cannot carry. A Haiku 5.5 message reads as unpriced -- counted
    # by `spend_by_route`, never silently zero.
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
    if path.suffix != ".jsonl":   # only Claude Code's own transcripts are read here
        return None
    opening, model, started, landed = None, None, None, False
    advisor_calls, advisor_model = 0, None
    seen_messages: set = set()
    tot = defaultdict(int)
    weighted = 0.0
    for line in path.read_text(errors="replace").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        started = started or row.get("timestamp")
        if row.get("type") == "user":
            content = (row.get("message") or {}).get("content")
            if opening is None:
                opening = _text(content)
            elif not landed and isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        body = block.get("content")
                        text = body if isinstance(body, str) else json.dumps(body)
                        if _LANDED.search(text or ""):
                            landed = True
        if row.get("type") != "assistant":
            continue
        msg = row.get("message") or {}
        u = msg.get("usage") or {}
        if not u:
            continue
        if msg.get("model") == "<synthetic>":   # a harness placeholder message, not a model call
            continue
        # ONE API MESSAGE IS WRITTEN AS ONE ROW PER CONTENT BLOCK, each repeating the whole message's
        # usage. Summing rows counted every message ~2.15x (11,078 rows for 5,151 messages over the
        # last 40 transcripts, 2026-10-12); every weighted figure before that date carries it.
        mid = msg.get("id")
        if mid is not None:
            if mid in seen_messages:
                continue
            seen_messages.add(mid)
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
        # An ADVISOR call is billed inside the main message, as a `usage.iterations` entry of type
        # `advisor_message` carrying its own model; the top-level counts omit it, so it is priced
        # here at the advisor's rate or the trial would read cheaper than it is.
        for it in u.get("iterations") or ():
            if not isinstance(it, dict) or it.get("type") != "advisor_message":
                continue
            advisor_calls += 1
            advisor_model = it.get("model") or advisor_model
            ap = PRICE.get(it.get("model") or "")
            icc = it.get("cache_creation") or {}
            a5 = int(icc.get("ephemeral_5m_input_tokens", 0) or 0)
            a1 = int(icc.get("ephemeral_1h_input_tokens", 0) or 0)
            if not (a5 or a1):
                a5 = int(it.get("cache_creation_input_tokens", 0) or 0)
            ai, ao, ar = (int(it.get(k, 0) or 0) for k in ("input_tokens", "output_tokens",
                                                            "cache_read_input_tokens"))
            tot["advisor_tokens"] += ai + ao + a5 + a1 + ar
            if ap:
                weighted += (ai * ap[0] + ao * ap[1] + a5 * ap[2] + a1 * ap[3] + ar * ap[4]) / 1e6
        price = PRICE.get(msg.get("model") or "")
        if price:
            pi, po, p5, p1, pr = price
            weighted += (parts["input"] * pi + parts["output"] * po + w5 * p5 + w1 * p1
                         + parts["cache_read"] * pr) / 1e6
    if opening is None or model is None:
        return None
    return {"kind": kind_of(opening), "model": model, "started": started, "weighted_usd": weighted,
            "landed": landed, "advisor_calls": advisor_calls, "advisor_model": advisor_model,
            "opening": opening[:20000], **dict(tot)}


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
                    "landed_pct": None if kind == "delivery_seat"
                    else round(100 * sum(r["landed"] for r in rs) / len(rs)),
                    "advisor_calls": sum(r.get("advisor_calls", 0) for r in rs),
                    "turns_without_advisor": sum(1 for r in rs if not r.get("advisor_calls")),
                    "week_weighted_usd": round(sum(w), 2)})
    return out


def render(days: float = 7.0, now: float | None = None, root: Path = PROJECTS) -> str:
    rows = table(turns(days, now, root), days)
    if not rows:
        return f"No turns found in the last {days:g} days under `{root}` -- nothing measured, which is not zero."
    head = ("| kind | model | turns | per day | landed | median fresh tokens | median cache-read tokens "
            "| median weighted $ | total weighted $ | advisor calls (turns without) |"
            "\n|---|---|---|---|---|---|---|---|---|---|")
    body = "\n".join(f"| {r['kind']} | {r['model']} | {r['turns']} | {r['turns_per_day']} | "
                     f"{'n/a' if r['landed_pct'] is None else str(r['landed_pct']) + '%'} | "
                     f"{r['median_fresh_tokens']:,} | {r['median_cache_read_tokens']:,} | "
                     f"{r['median_weighted_usd']} | {r['week_weighted_usd']} | "
                     f"{r['advisor_calls']} ({r['turns_without_advisor']}) |" for r in rows)
    return head + "\n" + body + "\n\n" + render_changes(turns(days, now, root))


def change_effects(rows: list[dict]) -> list[dict]:
    """Per prompt change: turns and landing rate on the OLD wording against the NEW, by kind."""
    out = []
    for ch in PROMPT_CHANGES:
        arms = {}
        for arm in ("old", "new"):
            rs = [r for r in rows if r["kind"] == ch["kind"] and ch[arm] in (r.get("opening") or "")]
            arms[arm] = {"turns": len(rs),
                         "landed_pct": round(100 * sum(r["landed"] for r in rs) / len(rs)) if rs else None}
        out.append({**ch, **{f"{a}_{k}": v for a, d in arms.items() for k, v in d.items()}})
    return out


def render_changes(rows: list[dict]) -> str:
    lines = ["**Prompt changes under measurement** (landing rate on the old wording vs the new; "
             "revert a change whose new arm lands less, once both arms have turns):", ""]

    def fmt(n, p):
        return f"{n} turns, " + ("no turns yet" if p is None else f"{p}% landed")

    for e in change_effects(rows):
        lines.append(f"- `{e['id']}` {e['kind']}: old {fmt(e['old_turns'], e['old_landed_pct'])}; "
                     f"new {fmt(e['new_turns'], e['new_landed_pct'])}. To revert: {e['reverse']}.")
    return "\n".join(lines)


#: THE DIRECTOR'S USAGE READINGS (P12, his words, 2026-10-12: "I'll tell you my weekly usage reading
#: from time to time. Use it with tools/tick_burn_rate.py to work out what each kind of work costs you
#: in my points"). (UTC time, percent of the week). A point is one percent. Append a row per reading;
#: the conversion is computed from the latest two, never typed in.
#: The next reading on the new tier scores the predictions written before it, in
#: docs/staging/records/SEAT_PREREG_THE_NEW_TIER_POINT_FIT_SEPARATES_ROUNDING_FROM_MODEL_MIX_2026-10-23.md.
POINT_READINGS: tuple[tuple[str, float], ...] = (
    ("2026-10-12T13:00", 40.0),   # Monday 14:00 BST
    ("2026-10-13T07:10", 55.0),   # Tuesday 08:10 BST
    ("2026-10-13T16:00", 59.0),   # Tuesday 17:00 BST
    ("2026-10-23T05:55", 0.0),    # Friday 06:55 BST: "moved to a lower tier ... reset ... 0% usage"
    ("2026-10-23T08:45", 4.0),    # Friday 09:45 BST: "4%"
    ("2026-10-23T14:20", 8.0),    # Friday 15:20 BST: "8%. How is pace and progress?"
    ("2026-10-24T12:47", 27.0),   # Saturday 13:47 BST: "27% used"
    ("2026-10-24T21:12", 35.0),   # Saturday 22:12 BST: "35% used"
    ("2026-10-25T06:35", 44.0),   # Sunday 06:35 GMT (clocks went back): "Only 44% used"
)

#: The plan moved to a lower tier at this reading (director, 23 Oct 06:55 BST), so a point is a
#: smaller amount of work after it and the readings before it fit the old tier only.
TIER_CHANGED_AT = "2026-10-23T05:55"


def weighted_usd_between(t0: str, t1: str, root: Path = PROJECTS) -> float:
    """Every assistant message priced between two UTC instants, across EVERY transcript: the
    sessions and their subagents (`*/*/subagents/*.jsonl`), each message once by id. The first
    calibration (2026-10-12) read only sessions that STARTED in the window and no subagents, and
    ran about 40% low against the director's readings."""
    seen: set = set()
    total = 0.0
    paths = list(root.glob("*/*.jsonl")) + list(root.glob("*/*/subagents/*.jsonl"))
    for path in paths:
        for line in path.read_text(errors="replace").splitlines():
            if '"assistant"' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            ts = row.get("timestamp") or ""
            msg = row.get("message") or {}
            if row.get("type") != "assistant" or not (t0 <= ts < t1) or not msg.get("usage"):
                continue
            if msg.get("model") == "<synthetic>" or msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            total += _priced(msg["usage"], msg.get("model"))
    return total


def _priced(u: dict, model: str | None) -> float:
    price = PRICE.get(model or "")
    usd = 0.0
    if price:
        cc = u.get("cache_creation") or {}
        w5 = int(cc.get("ephemeral_5m_input_tokens", 0) or 0)
        w1 = int(cc.get("ephemeral_1h_input_tokens", 0) or 0)
        if not (w5 or w1):
            w5 = int(u.get("cache_creation_input_tokens", 0) or 0)
        usd = (int(u.get("input_tokens", 0) or 0) * price[0] + int(u.get("output_tokens", 0) or 0) * price[1]
               + w5 * price[2] + w1 * price[3] + int(u.get("cache_read_input_tokens", 0) or 0) * price[4]) / 1e6
    for it in u.get("iterations") or ():
        if isinstance(it, dict) and it.get("type") == "advisor_message":
            ap = PRICE.get(it.get("model") or "")
            if ap:
                usd += (int(it.get("input_tokens", 0) or 0) * ap[0] + int(it.get("output_tokens", 0) or 0) * ap[1]
                        + int(it.get("cache_read_input_tokens", 0) or 0) * ap[4]) / 1e6
    return usd


def usd_per_point(readings=POINT_READINGS, root: Path = PROJECTS,
                  since: str = TIER_CHANGED_AT) -> float | None:
    """Weighted USD per point of the director's weekly allowance, from his latest two readings on
    the current tier. None when there are fewer than two, or no points passed between them."""
    readings = tuple(r for r in readings if r[0] >= since)
    if len(readings) < 2:
        return None
    (t0, p0), (t1, p1) = readings[-2], readings[-1]
    if p1 <= p0:
        return None
    return weighted_usd_between(t0, t1, root) / (p1 - p0)


def spend_by_route(t0: str, t1: str, root: Path = PROJECTS) -> dict:
    """Every priced message between two UTC instants, attributed to the ROUTE that spent it: its
    session's kind, or that kind plus ` / subagent` for a fork or subagent transcript, which is
    filed under its parent session's directory. Per route: weighted USD by token class, the
    sessions that spent inside the window, and how many of them landed. Counted once per message
    id, exactly as `weighted_usd_between` counts, so the routes sum to its total."""
    sessions: dict[str, tuple[str, bool]] = {}
    for path in root.glob("*/*.jsonl"):
        t = read_turn(path)
        if t is None:
            sessions[path.stem] = ("other", False)
            continue
        # An executor turn drawn from the advisor channel is its own route: the director asked for
        # "advisor draws" beside the lanes, and the drawn prompt names the advisor file it acts on.
        advisor = t["kind"] == "seat_executor" and "docs/staging/advisor/" in t.get("opening", "")
        sessions[path.stem] = (t["kind"] + (" (advisor item)" if advisor else ""), t["landed"])
    out: dict = defaultdict(lambda: {"usd": defaultdict(float), "sessions": set(), "landed": set(),
                                     "unpriced_messages": 0})
    seen: set = set()
    paths = [(p, False) for p in root.glob("*/*.jsonl")] + [(p, True) for p in root.glob("*/*/subagents/*.jsonl")]
    for path, sub in paths:
        sid = path.parent.parent.name if sub else path.stem
        kind, landed = sessions.get(sid, ("other", False))
        r = out[kind + (" / subagent" if sub else "")]
        for line in path.read_text(errors="replace").splitlines():
            if '"assistant"' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            ts, msg = row.get("timestamp") or "", row.get("message") or {}
            if row.get("type") != "assistant" or not (t0 <= ts < t1) or not msg.get("usage"):
                continue
            if msg.get("model") == "<synthetic>" or msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            price, u = PRICE.get(msg.get("model") or ""), msg["usage"]
            r["sessions"].add(sid)
            if landed and not sub:
                r["landed"].add(sid)
            if not price:
                r["unpriced_messages"] += 1
                continue
            cc = u.get("cache_creation") or {}
            w5 = int(cc.get("ephemeral_5m_input_tokens", 0) or 0)
            w1 = int(cc.get("ephemeral_1h_input_tokens", 0) or 0)
            if not (w5 or w1):
                w5 = int(u.get("cache_creation_input_tokens", 0) or 0)
            for cls, n, p in (("input", u.get("input_tokens"), price[0]), ("output", u.get("output_tokens"), price[1]),
                              ("write_5m", w5, price[2]), ("write_1h", w1, price[3]),
                              ("cache_read", u.get("cache_read_input_tokens"), price[4])):
                r["usd"][cls] += int(n or 0) * p / 1e6
    return {k: {"usd": round(sum(v["usd"].values()), 2), "by_class": {c: round(x, 2) for c, x in v["usd"].items()},
                "sessions": len(v["sessions"]), "landed": len(v["landed"]),
                "unpriced_messages": v["unpriced_messages"]} for k, v in out.items() if v["sessions"]}


def render_routes(t0: str, t1: str, root: Path = PROJECTS) -> str:
    routes = spend_by_route(t0, t1, root)
    total = sum(r["usd"] for r in routes.values()) or 1.0
    lines = [f"Spend by route, {t0} to {t1} UTC (weighted USD, every transcript and subagent):", "",
             "| route | weighted $ | share | sessions | landed | $ per landed | output / 1h write / 5m write / read | unpriced msgs |",
             "|---|---|---|---|---|---|---|---|"]
    for k, r in sorted(routes.items(), key=lambda kv: -kv[1]["usd"]):
        c = r["by_class"]
        mix = " / ".join(f"{round(100 * c.get(x, 0) / (r['usd'] or 1))}%" for x in ("output", "write_1h", "write_5m", "cache_read"))
        per = f"{r['usd'] / r['landed']:.2f}" if r["landed"] else "n/a"
        lines.append(f"| {k} | {r['usd']:.1f} | {100 * r['usd'] / total:.1f}% | {r['sessions']} | {r['landed']} | {per} | {mix} | {r['unpriced_messages']} |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------------------
# WHERE READING TOKENS GO (director steer 7 Nov, released 14 Nov: "Measure it"). Measurement only.
#
# WHAT A READ COSTS. A tool result enters the context once and is then resent with every later call
# of that context: it is CACHE-WRITTEN on the first call after it and CACHE-READ on each call after
# that, until the context is compacted. So a read's cost is its size times the calls that carry it,
# and a 20k-token read early in a 150-call session is 3m tokens of cache read. Fresh input and
# output are not where a read lands; they are reported as the measured totals they are.
#
# ITS SIZE IN TOKENS is chars x a ratio MEASURED here from the same transcripts: across pairs of
# consecutive calls whose only addition is a large tool result, how much the measured context grew
# per character added. No ratio is typed in.
#
# THE CLASSES OVERLAP (a whole-file re-read of a generated JSON file is in three), so they are
# ranked by their own measured share of the window's context tokens and never summed.
# ---------------------------------------------------------------------------------------------------

#: Bytes a program writes rather than a person: the observability stores, the site's data feeds, the
#: market feeds and any JSON/JSONL file. A path, not a judgement about whether the read was useful.
_GENERATED = re.compile(r"(?:^|/)(?:docs/observability|site/data|docs/market_data)/|\.jsonl?(?::|$)")
#: A shell command's KIND is its first verb after any `cd`: one kind per call, so a test run piped
#: through grep is a test run, not a search.
_BASH_KINDS = (
    ("file read (cat/head/tail/sed/awk)", re.compile(r"^(?:cat|head|tail|sed|awk|less|nl|jq)\b")),
    ("search/census (grep/find/ls/wc/git log...)", re.compile(
        r"^(?:grep|rg|egrep|find|ls|wc|du|tree|git (?:log|grep|ls-files|status|show|diff|blame))\b")),
    ("test run (pytest)", re.compile(r"^(?:python3? -m pytest|pytest|timeout \S+ python3? -m pytest)\b")),
    ("python run (a tool, daemon or inline script)", re.compile(r"^(?:timeout \S+ )?python3?\b")),
    ("git write/sync (commit/fetch/merge/push...)", re.compile(r"^git\b")),
)
_FILE_ARGS = re.compile(r"^(?:cat|head|tail|sed -n '[^']*'|sed -n \S+|nl|less)\s+(?:-\S+\s+)*([^\s|;&<>]+)")


def bash_kind(cmd: str) -> str:
    for seg in re.split(r"&&|;|\|\||\n", cmd or ""):
        seg = seg.strip().lstrip("(").strip()
        if not seg or seg.startswith(("cd ", "export ", "#", "set ", "echo ", "for ", "do ", "done")):
            continue
        for kind, rx in _BASH_KINDS:
            if rx.search(seg):
                return kind
        return "other shell"
    return "other shell"


def bash_read_path(cmd: str) -> str:
    """The one file a shell read prints, when its first verb is a reader with exactly one file."""
    for seg in re.split(r"&&|;|\n", cmd or ""):
        seg = seg.strip()
        if not seg or seg.startswith("cd "):
            continue
        first = seg.split("|")[0].strip()
        m = _FILE_ARGS.match(first)
        rest = first[m.end():].strip() if m else ""
        return m.group(1) if m and not rest else ""
    return ""
#: The opening reminder names CLAUDE.md by its checkout's path, which differs per worktree.
_CLAUDE_MD = re.compile(r"Contents of \S+/CLAUDE\.md \(project instructions")
_MEMORY_MD = "memory/MEMORY.md (user's auto-memory"
#: A context that shrinks by more than this between consecutive calls was compacted or cleared; what
#: was in it before stops being carried. The count of such drops is printed beside the figures.
_COMPACTED = 0.8


def _block_text(content) -> tuple[str, int]:
    """(text, image blocks) of a tool result; an image is counted, never measured as base64 chars."""
    if isinstance(content, str):
        return content, 0
    texts, images = [], 0
    for b in content or ():
        if isinstance(b, dict) and b.get("type") == "image":
            images += 1
        elif isinstance(b, dict):
            texts.append(str(b.get("text") or b.get("content") or ""))
    return "\n".join(texts), images


def _strings(node):
    """Every string inside a parsed transcript row, depth first."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def _lead_path(line: str) -> str:
    """The path a grep/ls/find output line starts with (`path:12:...`, `./path`), or ''."""
    words = line.split(":", 1)[0].split()
    return words[0] if words else ""


def _slice(text: str, marker: str) -> int:
    """Characters of one always-loaded file inside the opening reminder, from its marker to the next."""
    i = text.find(marker)
    if i < 0:
        return 0
    ends = [j for j in (text.find("\nContents of ", i + 1), text.find("</system-reminder>", i)) if j > i]
    return (min(ends) if ends else len(text)) - i


def _read_context(path: Path) -> dict:
    """One transcript -> its calls (timestamp, context tokens, usage, model) and what entered it."""
    calls, uses, pieces, seen = [], {}, [], set()
    loaded = {"claude_md": 0, "memory_md": 0, "opening": None}
    for line in path.open(errors="replace"):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        t = row.get("type")
        if not loaded["claude_md"] and "/CLAUDE.md (project instructions" in line:
            text = next((x for x in _strings(row) if _CLAUDE_MD.search(x)), "")
            m = _CLAUDE_MD.search(text)
            loaded["claude_md"] = _slice(text, m.group(0)) if m else 0
            loaded["memory_md"] = _slice(text, _MEMORY_MD)
        if t == "attachment":
            att = row.get("attachment") or {}
            if att.get("type") == "nested_memory":   # a path-scoped rule, loaded on an edit
                body = (att.get("content") or {}).get("content", "")
                pieces.append({"after": len(calls), "chars": len(body), "tool": "rule",
                               "path": att.get("path", ""), "input": {}, "lines": []})
            continue
        msg = row.get("message") or {}
        if t == "user" and loaded["opening"] is None:
            loaded["opening"] = len(_text(msg.get("content")))
        if t == "assistant":
            u = msg.get("usage") or {}
            if u and msg.get("model") != "<synthetic>" and msg.get("id") not in seen:
                seen.add(msg.get("id"))
                cw = int(u.get("cache_creation_input_tokens", 0) or 0)
                if not cw:
                    cc = u.get("cache_creation") or {}
                    cw = int(cc.get("ephemeral_5m_input_tokens", 0) or 0) + int(cc.get("ephemeral_1h_input_tokens", 0) or 0)
                parts = {"input": int(u.get("input_tokens", 0) or 0), "cache_write": cw,
                         "cache_read": int(u.get("cache_read_input_tokens", 0) or 0),
                         "output": int(u.get("output_tokens", 0) or 0)}
                calls.append({"ts": row.get("timestamp") or "", "model": msg.get("model") or "",
                              "ctx": parts["input"] + cw + parts["cache_read"], **parts})
            for b in msg.get("content") or ():
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    uses[b.get("id")] = (b.get("name") or "", b.get("input") or {}, len(calls))
        elif t == "user" and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if not (isinstance(b, dict) and b.get("type") == "tool_result"):
                    continue
                text, _images = _block_text(b.get("content"))
                name, inp, after = uses.get(b.get("tool_use_id"), ("?", {}, len(calls)))
                pieces.append({"after": after, "chars": len(text), "tool": name, "input": inp,
                               "path": str(inp.get("file_path") or inp.get("path") or ""),
                               "lines": text.splitlines() if name in ("Grep", "Glob", "Bash") else []})
    return {"calls": calls, "pieces": pieces, "loaded": loaded}


def tokens_per_char(contexts: list[dict], min_chars: int = 20_000) -> tuple[float, float, float, int] | None:
    """Measured: across consecutive calls whose gap carries at least `min_chars` of tool result (so a
    call's own output is small beside it), context growth less the call's output, per char added.
    (median, lower quartile, upper quartile, pairs); the median, so one gap that also carried a large
    attachment does not move it."""
    ratios = []
    for c in contexts:
        calls, added = c["calls"], defaultdict(int)
        for p in c["pieces"]:
            added[p["after"]] += p["chars"]
        for k in range(1, len(calls)):
            n = added.get(k, 0)
            d = calls[k]["ctx"] - calls[k - 1]["ctx"] - calls[k - 1]["output"]
            if n >= min_chars and d > 0:
                ratios.append(d / n)
    if len(ratios) < 4:
        return None
    q = statistics.quantiles(ratios, n=4)
    return statistics.median(ratios), q[0], q[2], len(ratios)


#: One file has one name whatever checkout read it: the shared tree, a seat's worktree, a trial tree.
_REPO_ROOT = re.compile(r"^(?:/home/rich/synthetic-enterprise|/var/tmp/fable-trial/x/[^/]+/tree|/var/tmp/se-[^/]+"
                        r"|/var/tmp/third-arm/[^/]+|/tmp/naive-organ-scratch-[^/]+)/")


def _classes_of(piece: dict, read_before: set, model: str) -> list[str]:
    tool, inp = piece["tool"], piece["input"]
    path = _REPO_ROOT.sub("", piece["path"])
    out = []
    if tool == "rule":
        return ["always-loaded: path-scoped rules (.claude/rules)"]
    cmd = str(inp.get("command") or "")
    kind = bash_kind(cmd) if tool == "Bash" else ""
    if tool == "Bash":
        out.append("Bash: " + kind)
        bp = bash_read_path(cmd)
        if bp and bp in read_before:
            out.append("repeat read of a file already read in this context")
        if kind.startswith("file read") and bp and not re.search(r"\|\s*(?:head|tail|sed|grep)|sed -n", cmd):
            out.append("whole-file read (Read without offset/limit, or a bare cat)")
        if _GENERATED.search(bp):
            out.append("generated data: a generated file read whole or in part")
    if tool == "Read":
        out.append("all Read results")
        if path in read_before:
            out.append("repeat read of a file already read in this context")
        if not (inp.get("offset") or inp.get("limit")):
            out.append("whole-file read (Read without offset/limit, or a bare cat)")
        if _GENERATED.search(path):
            out.append("generated data: a generated file read whole or in part")
    is_search = tool in ("Grep", "Glob") or kind.startswith("search")
    if is_search:
        out.append("search/census in an Opus context" if "opus" in model or "fable" in model
                   else "search/census in a Haiku/Sonnet context")
    if tool in ("Grep", "Glob", "Bash"):
        out.append(f"all {tool} results" if tool != "Glob" else "all Grep results")
    elif tool not in ("Read", "rule"):
        out.append("other tool results (Agent, Edit, Write, Skill...)")
    return out


def reading_tokens(t0: str, t1: str, root: Path = PROJECTS) -> dict:
    """Context tokens by reading class between two UTC instants, over every session and subagent
    transcript, per seat kind. Each class: tokens cache-written and cache-read, and its share of the
    window's measured context tokens (fresh input + cache write + cache read)."""
    paths = [(p, False) for p in root.glob("*/*.jsonl")] + [(p, True) for p in root.glob("*/*/subagents/*.jsonl")]
    lo = time.mktime(time.strptime(t0[:16], "%Y-%m-%dT%H:%M")) - 86400
    paths = [(p, s) for p, s in paths if p.stat().st_mtime >= lo]
    kinds = {}
    for p, sub in paths:
        if not sub:
            t = read_turn(p)
            kinds[p.stem] = t["kind"] if t else "other"
    ctxs = []
    for p, sub in paths:
        c = _read_context(p)
        c["route"] = kinds.get(p.parent.parent.name if sub else p.stem, "other") + (" / subagent" if sub else "")
        c["session"] = p.parent.parent.name if sub else p.stem
        ctxs.append(c)
    fit = tokens_per_char(ctxs)
    ratio = fit[0] if fit else None
    totals = defaultdict(lambda: defaultdict(int))     # route -> token class -> tokens
    cls = defaultdict(lambda: defaultdict(float))      # (route, class) -> write/read tokens
    files = defaultdict(lambda: {"read": 0.0, "write": 0.0, "reads": 0, "sessions": set()})
    drops = calls_in = 0
    for c in ctxs:
        calls, route = c["calls"], c["route"]
        inw = [t0 <= x["ts"] < t1 for x in calls]
        if not any(inw):
            continue
        seg, s = [], 0
        for k, x in enumerate(calls):
            if k and x["ctx"] < _COMPACTED * calls[k - 1]["ctx"]:
                s += 1
                drops += inw[k]
            seg.append(s)
        for k, x in enumerate(calls):
            if inw[k]:
                calls_in += 1
                for tc in ("input", "cache_write", "cache_read", "output"):
                    totals[route][tc] += x[tc]
        model = next((x["model"] for x in calls if x["model"]), "")

        def carry(after: int) -> tuple[int, int]:
            if after >= len(calls):
                return 0, 0
            home = seg[after]
            n = sum(1 for j in range(after, len(calls)) if seg[j] == home and inw[j])
            return (1 if inw[after] else 0), max(n - (1 if inw[after] else 0), 0)

        # The first call's whole context, and the always-loaded files inside it, ride every call of
        # the context's first segment and are reloaded after each compaction: carried by every call.
        n_in = sum(inw)
        segs_in = len({seg[j] for j in range(len(calls)) if inw[j]})
        base = calls[0]["ctx"]
        cls[(route, "always-loaded: the first call's whole context (system, tools, CLAUDE.md, memory, prompt)")]["write"] += base * segs_in
        cls[(route, "always-loaded: the first call's whole context (system, tools, CLAUDE.md, memory, prompt)")]["read"] += base * (n_in - segs_in)
        if ratio:
            for key, name in (("claude_md", "always-loaded: CLAUDE.md"), ("memory_md", "always-loaded: MEMORY.md index"),
                              ("opening", "always-loaded: the opening prompt (a tick's drawn work, a seat's charter)")):
                tok = (c["loaded"][key] or 0) * ratio
                cls[(route, name)]["write"] += tok * segs_in
                cls[(route, name)]["read"] += tok * (n_in - segs_in)
        read_before: set = set()
        for p in c["pieces"]:
            if not ratio:
                break
            w, r = carry(p["after"])
            tok = p["chars"] * ratio
            for name in _classes_of(p, read_before, model):
                cls[(route, name)]["write"] += tok * w
                cls[(route, name)]["read"] += tok * r
            if p["lines"]:
                gen = sum(len(ln) for ln in p["lines"] if _GENERATED.search(_lead_path(ln)))
                if gen:
                    name = f"generated data: lines naming a generated path in {p['tool']} output"
                    cls[(route, name)]["write"] += gen * ratio * w
                    cls[(route, name)]["read"] += gen * ratio * r
            fp = p["path"] if p["tool"] == "Read" else (
                bash_read_path(str(p["input"].get("command") or "")) if p["tool"] == "Bash" else "")
            if fp:
                fp = _REPO_ROOT.sub("", fp)
                read_before.add(fp)
                f = files[fp]
                f["write"] += tok * w
                f["read"] += tok * r
                f["reads"] += 1
                f["sessions"].add(c["session"])
    return {"tokens_per_char": ratio, "fit": fit, "calls": calls_in, "compactions": drops,
            "totals": {k: dict(v) for k, v in totals.items()},
            "classes": {k: dict(v) for k, v in cls.items()},
            "files": files}


def render_reading(t0: str, t1: str, root: Path = PROJECTS, top: int = 15) -> str:
    m = reading_tokens(t0, t1, root)
    if not m["totals"]:
        return f"No calls between {t0} and {t1} under `{root}` -- nothing measured, which is not zero."
    tot = defaultdict(int)
    for v in m["totals"].values():
        for k, n in v.items():
            tot[k] += n
    ctx = tot["input"] + tot["cache_write"] + tot["cache_read"] or 1
    ratio, fit = m["tokens_per_char"], m["fit"]
    lines = [f"Reading tokens, {t0} to {t1} UTC: {m['calls']:,} calls over every session and subagent; "
             f"{m['compactions']} compaction drops; tokens per char of tool result measured at "
             + (f"{fit[0]:.3f} (quartiles {fit[1]:.3f}-{fit[2]:.3f}, {fit[3]} gaps of 20k+ chars)."
                if ratio else "NOTHING (fewer than 4 calibration gaps) -- the classes below are not measured."), "",
             "**Measured totals, by token class** (every call in the window):", "",
             "| route | calls' fresh input | cache write | cache read | output |", "|---|---|---|---|---|"]
    for route, v in sorted(m["totals"].items(), key=lambda kv: -kv[1].get("cache_read", 0)):
        lines.append(f"| {route} | {v.get('input', 0):,} | {v.get('cache_write', 0):,} | {v.get('cache_read', 0):,} | {v.get('output', 0):,} |")
    lines.append(f"| **all** | {tot['input']:,} | {tot['cache_write']:,} | {tot['cache_read']:,} | {tot['output']:,} |")
    by = defaultdict(lambda: {"write": 0.0, "read": 0.0})
    for (route, name), v in m["classes"].items():
        by[name]["write"] += v.get("write", 0)
        by[name]["read"] += v.get("read", 0)
    lines += ["", "**By reading class, ranked by share of the window's context tokens** (fresh input + cache "
              "write + cache read; classes OVERLAP and do not sum; a read adds no output and ~no fresh input):", "",
              "| class | cache write | cache read | share of context tokens | share of cache write |", "|---|---|---|---|---|"]
    for name, v in sorted(by.items(), key=lambda kv: -(kv[1]["write"] + kv[1]["read"])):
        lines.append(f"| {name} | {int(v['write']):,} | {int(v['read']):,} | "
                     f"{100 * (v['write'] + v['read']) / ctx:.1f}% | {100 * v['write'] / (tot['cache_write'] or 1):.1f}% |")
    # Every tool result and the first call's context are disjoint; what they leave is the model's own
    # output carried forward (thinking, tool calls, text) and harness attachments. Printed so a class
    # that silently over-attributes shows as a remainder below zero.
    disjoint = ("all Bash results", "all Read results", "all Grep results", "other tool results (Agent, Edit, Write, Skill...)",
                "always-loaded: path-scoped rules (.claude/rules)",
                "always-loaded: the first call's whole context (system, tools, CLAUDE.md, memory, prompt)")
    covered = sum(by[n]["write"] + by[n]["read"] for n in disjoint if n in by)
    lines.append(f"| *remainder: the model's own output carried forward, and attachments (disjoint check)* | | | "
                 f"{100 * (1 - covered / ctx):.1f}% | |")
    many = [f for f in m["files"].values() if len(f["sessions"]) >= 10]
    lines.append(f"| repeat across sessions: every read of a file read in 10+ sessions ({len(many)} files) | "
                 f"{int(sum(f['write'] for f in many)):,} | {int(sum(f['read'] for f in many)):,} | "
                 f"{100 * sum(f['write'] + f['read'] for f in many) / ctx:.1f}% | |")
    routes = sorted(m["totals"], key=lambda r: -m["totals"][r].get("cache_read", 0))
    keyc = [n for n, _ in sorted(by.items(), key=lambda kv: -(kv[1]["write"] + kv[1]["read"]))][:8]
    lines += ["", "**Per seat kind: each class's share of that route's own context tokens:**", "",
              "| route | " + " | ".join(keyc) + " |", "|---" * (len(keyc) + 1) + "|"]
    for route in routes:
        v = m["totals"][route]
        rc = v.get("input", 0) + v.get("cache_write", 0) + v.get("cache_read", 0) or 1
        cells = [f"{100 * sum(m['classes'].get((route, n), {}).get(x, 0) for x in ('write', 'read')) / rc:.0f}%" for n in keyc]
        lines.append(f"| {route} | " + " | ".join(cells) + " |")
    lines += ["", f"**The {top} files whose Read results cost most** (write + read tokens carried; reads; sessions):", "",
              "| file | cache write | cache read | reads | sessions |", "|---|---|---|---|---|"]
    for path, f in sorted(m["files"].items(), key=lambda kv: -(kv[1]["write"] + kv[1]["read"]))[:top]:
        lines.append(f"| `{path.replace('/home/rich/synthetic-enterprise/', '')}` | {int(f['write']):,} | "
                     f"{int(f['read']):,} | {f['reads']} | {len(f['sessions'])} |")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=float, default=7.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--points", action="store_true",
                    help="the USD-per-point conversion from the director's last two readings")
    ap.add_argument("--routes", nargs=2, metavar=("FROM", "TO"),
                    help="spend by route between two UTC instants, e.g. 2026-10-16T05:55 2026-10-23T05:55")
    ap.add_argument("--reading", nargs=2, metavar=("FROM", "TO"),
                    help="where reading tokens go between two UTC instants, by class and seat kind")
    a = ap.parse_args(argv)
    if a.reading:
        print(render_reading(*a.reading))
        return 0
    if a.routes:
        print(render_routes(*a.routes))
        return 0
    if a.points:
        per = usd_per_point()
        print(f"no conversion: fewer than two readings on the tier since {TIER_CHANGED_AT}" if per is None
              else f"one point = USD {per:.1f} weighted (from {POINT_READINGS[-2][0]} "
                   f"to {POINT_READINGS[-1][0]}, all transcripts and subagents)")
        return 0
    if a.json:
        print(json.dumps(table(turns(a.days), a.days), indent=1))
    else:
        print(render(a.days))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
