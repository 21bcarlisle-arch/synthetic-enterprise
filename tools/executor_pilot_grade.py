"""Grade the P2 executor pilot against its pre-registered switch-on rule.

The rule (section 6 of docs/staging/records/SEAT_PROPOSAL_CHEAPER_PER_LANDED_RESULT_ON_THE_NEW_TIER_
2026-10-23.md, restated in docs/observability/executor_tier_pilot.yaml): after at least 20 turns in
each arm, Sonnet 5.5 stays on only if its landed share is within 10 points of the control, its rework
is no higher than the control's, and it costs at least 25% less per landed result.

One TURN is one executor run of one work id: the `RUNNING <id>` line in seat-executor-log.md up to
the next `RUNNING`. Its four facts come from four places, joined on the work id:

- ARM: the `route: seat_executor` row model_tier.log_decision wrote just before the spawn.
- LANDED: the executor's own verdict. A `LANDED NOTHING: <id>` inside the turn means it did not
  land; otherwise a `FINISHED <id>` whose bound paths moved (k of n, k > 0) means it did. A turn
  with neither yet is PENDING and is left out of n.
- COST: every priced message in the turn's transcript and its subagents, priced by
  tools/tick_burn_rate (the same prices `--routes` uses). `--routes` itself sums by route, which
  cannot split one route into its two arms, so the turn's own session is read instead. A turn
  whose transcript cannot be found is counted, not guessed.
- REWORK: the commits the turn landed (`[surgical-land] landed <sha>` in its transcript), then any
  OTHER commit on origin/main within 72 h after them that touches one of their paths and whose
  subject reads as a fix (FIX_WORDS). The shared ledgers every turn writes (SHARED_LEDGERS) are
  left out, or every turn would read as reworked by whichever lane wrote the stretch log next. A
  landed turn whose 72 h have not passed is PENDING for rework.

Both arms are graded by the same definitions, so a definition that over- or under-counts rework
moves both sides; the comparison, not the level, is what the rule reads.

    python3 -m tools.executor_pilot_grade            # the table and the verdict
    python3 -m tools.executor_pilot_grade --json
    python3 -m tools.executor_pilot_grade --placebo-since 2026-10-09   # A/A on past Opus turns
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.grade_world_debt_against_ofgem import wilson  # noqa: E402
from tools.tick_burn_rate import PROJECTS, _priced  # noqa: E402

PILOT = REPO / "docs" / "observability" / "executor_tier_pilot.yaml"
EXECUTOR_TRANSCRIPTS = PROJECTS / "-var-tmp-se-seat-executor"

#: The pre-registered thresholds. Read from the proposal, never tuned after a result.
MIN_TURNS = 20
LANDED_GAP_POINTS = 10.0
CHEAPER_BY = 0.25
REWORK_HOURS = 72

FIX_WORDS = re.compile(r"\b(fix\w*|revert\w*|regress\w*|broke|broken|repair\w*|correct(s|ed|ion)?"
                       r"|restore[sd]?|undo\w*|wrong)\b", re.I)
SHARED_LEDGERS = ("docs/observability/", "docs/status/", "docs/direction/", "docs/staging/",
                  "docs/design/maturity_map.yaml", "docs/claude/phase-history.md")

_RUNNING = re.compile(r"^- \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\] RUNNING (\S+) in ")
_FINISHED = re.compile(r"^- \[[^]]+\] FINISHED ([^:\s]+): .*?-- (\d+) of (\d+) bound path")
_NOTHING = re.compile(r"^- \[[^]]+\] LANDED NOTHING: ([^,\s]+),")
_LANDED_SHA = re.compile(r"\[surgical-land\] landed ([0-9a-f]{7,})")


def _shared(rel: str) -> Path:
    """The shared tree's copy: both logs are live records written only there."""
    try:
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=REPO,
                                capture_output=True, text=True, timeout=30).stdout.strip()
        root = (REPO / common).resolve().parent if common else REPO
    except Exception:
        root = REPO
    shared = root / rel
    return shared if shared.exists() else REPO / rel


def _stamp(s: str) -> float:
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp()


def executor_turns(log_text: str) -> list[dict]:
    """Every RUNNING turn in the executor log, with its verdict: landed True/False, or None."""
    turns: list[dict] = []
    for line in log_text.splitlines():
        m = _RUNNING.match(line)
        if m:
            turns.append({"work_id": m.group(2), "start": _stamp(m.group(1)), "landed": None,
                          "nothing": False, "end": None})
            continue
        if not turns:
            continue
        cur = turns[-1]
        stamp = re.match(r"^- \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\]", line)
        n = _NOTHING.match(line)
        if n and n.group(1) == cur["work_id"]:
            cur["nothing"], cur["landed"] = True, False
            cur["end"] = _stamp(stamp.group(1))
        f = _FINISHED.match(line)
        if f and f.group(1) == cur["work_id"]:
            if not cur["nothing"]:
                cur["landed"] = int(f.group(2)) > 0
            cur["end"] = _stamp(stamp.group(1))
    return turns


def arm_rows(tier_log_text: str, starts: str, ends: str) -> list[dict]:
    rows = []
    for line in tier_log_text.splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("route") != "seat_executor" or r.get("arm") not in ("sonnet", "control"):
            continue
        day = dt.datetime.fromtimestamp(float(r.get("ts", 0)), dt.timezone.utc).strftime("%Y-%m-%d")
        if starts <= day <= ends and r.get("work_id"):
            rows.append(r)
    return rows


def join(rows: list[dict], turns: list[dict]) -> list[dict]:
    """Each arm decision to the first RUNNING of its work id at or after it (minute stamps, so a
    minute of slack). A turn is claimed by one decision only."""
    used: set[int] = set()
    out = []
    for r in sorted(rows, key=lambda r: r["ts"]):
        for i, t in enumerate(turns):
            if i not in used and t["work_id"] == r["work_id"] and t["start"] >= r["ts"] - 60:
                used.add(i)
                out.append({**t, "arm": r["arm"], "model": r.get("model")})
                break
        else:
            out.append({"work_id": r["work_id"], "arm": r["arm"], "model": r.get("model"),
                        "start": r["ts"], "end": None, "landed": None, "nothing": False})
    return out


def _iso(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def transcript_of(turn: dict, root: Path = EXECUTOR_TRANSCRIPTS) -> Path | None:
    """The executor session that opened inside this turn and names its work id."""
    lo = _iso(turn["start"] - 120)
    hi = _iso((turn["end"] or turn["start"] + 6 * 3600) + 120)
    for path in sorted(root.glob("*.jsonl")):
        with path.open(errors="replace") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("type") != "user":
                    continue
                ts = row.get("timestamp") or ""
                content = (row.get("message") or {}).get("content")
                text = content if isinstance(content, str) else json.dumps(content)
                if lo <= ts[:19] <= hi and turn["work_id"] in text:
                    return path
                break
    return None


def cost_and_shas(session: Path) -> tuple[float, list[str]]:
    seen: set = set()
    usd, shas = 0.0, []
    for path in [session, *sorted(session.parent.glob(f"{session.stem}/subagents/*.jsonl"))]:
        for line in path.read_text(errors="replace").splitlines():
            if path == session:
                shas += [s for s in _LANDED_SHA.findall(line) if s not in shas]
            if '"assistant"' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            msg = row.get("message") or {}
            if row.get("type") != "assistant" or not msg.get("usage"):
                continue
            if msg.get("model") == "<synthetic>" or msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            usd += _priced(msg["usage"], msg.get("model"))
    return usd, shas


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                          timeout=120).stdout


def reworked(shas: list[str], now: float) -> bool | None:
    """True/False, or None while the 72 h window is still open or none of the commits reached
    origin. A sha that did not reach origin (a retried or superseded landing) is dropped: 36 of 40
    landed turns read as unknown in the first A/A run because one such sha vetoed the rest."""
    paths: set[str] = set()
    last = 0.0
    full = []
    shas = [sha for sha in shas if subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, "origin/main"], cwd=REPO,
        capture_output=True).returncode == 0]
    if not shas:
        return None
    for sha in shas:
        full.append(_git("rev-parse", sha).strip())
        last = max(last, float(_git("log", "-1", "--format=%ct", sha).strip() or 0))
        paths |= {p for p in _git("show", "--name-only", "--format=", sha).split()
                  if not p.startswith(SHARED_LEDGERS)}
    if not paths:
        return False
    if now < last + REWORK_HOURS * 3600:
        return None
    log = _git("log", "origin/main", f"--since=@{int(last)}", f"--until=@{int(last) + REWORK_HOURS * 3600}",
               "--format=%H\t%s", "--", *sorted(paths))
    return any(h not in full and FIX_WORDS.search(s)
               for h, _, s in (ln.partition("\t") for ln in log.splitlines() if ln))


def _boot_ratio(turns: list[dict], seed: int = 0, n: int = 2000) -> tuple[float, float] | None:
    """90% bootstrap interval on $ per landed result, resampling turns."""
    costed = [t for t in turns if t.get("usd") is not None]
    if not costed or not any(t["landed"] for t in costed):
        return None
    rng, vals = random.Random(seed), []
    for _ in range(n):
        s = [rng.choice(costed) for _ in costed]
        k = sum(1 for t in s if t["landed"])
        if k:
            vals.append(sum(t["usd"] for t in s) / k)
    vals.sort()
    return (vals[int(0.05 * len(vals))], vals[int(0.95 * len(vals)) - 1]) if vals else None


def summarise(turns: list[dict]) -> dict:
    graded = [t for t in turns if t["landed"] is not None]
    k = sum(1 for t in graded if t["landed"])
    costed = [t for t in graded if t.get("usd") is not None]
    landed_costed = sum(1 for t in costed if t["landed"])
    rw_known = [t for t in graded if t["landed"] and t.get("rework") is not None]
    rw = sum(1 for t in rw_known if t["rework"])
    lo, hi = wilson(k, len(graded))
    rlo, rhi = wilson(rw, len(rw_known))
    return {
        "turns_logged": len(turns), "pending": len(turns) - len(graded), "n": len(graded),
        "landed": k, "landed_share": k / len(graded) if graded else None, "landed_bound": [lo, hi],
        "usd": round(sum(t["usd"] for t in costed), 2), "uncosted": len(graded) - len(costed),
        "usd_per_landed": (sum(t["usd"] for t in costed) / landed_costed) if landed_costed else None,
        "usd_per_landed_bound": _boot_ratio(graded),
        "rework_n": len(rw_known), "reworked": rw,
        "rework_share": rw / len(rw_known) if rw_known else None, "rework_bound": [rlo, rhi],
        "rework_pending": sum(1 for t in graded if t["landed"] and t.get("rework") is None),
    }


def verdict(s: dict, c: dict) -> dict:
    """The three conditions on point estimates, as pre-registered. None = cannot yet say."""
    if s["n"] < MIN_TURNS or c["n"] < MIN_TURNS:
        return {"ready": False, "why": f"needs {MIN_TURNS} graded turns per arm; "
                                       f"sonnet {s['n']}, control {c['n']}"}
    landed = (c["landed_share"] - s["landed_share"]) * 100 <= LANDED_GAP_POINTS
    rework = (None if s["rework_share"] is None or c["rework_share"] is None
              else s["rework_share"] <= c["rework_share"])
    cheaper = (None if not s["usd_per_landed"] or not c["usd_per_landed"]
               else s["usd_per_landed"] <= (1 - CHEAPER_BY) * c["usd_per_landed"])
    conds = {"landed_within_10_points": landed, "rework_no_higher": rework,
             "at_least_25pct_cheaper_per_landed": cheaper}
    if any(v is False for v in conds.values()):
        call = "REVERT"
    elif all(v is True for v in conds.values()):
        call = "SWITCH ON"
    else:
        call = None
    return {"ready": True, **conds, "call": call}


def placebo_rows(log_text: str, since: str, one_in: int = 4) -> list[dict]:
    """An A/A test: every executor turn since `since` (all Opus, before the pilot) given the arm
    model_tier.executor_arm's hash would have given its work id. The grader should find no gap
    beyond its bounds; one it does find is a defect in the grader or a hash that is not neutral."""
    import hashlib
    rows = []
    for t in executor_turns(log_text):
        if dt.datetime.fromtimestamp(t["start"], dt.timezone.utc).strftime("%Y-%m-%d") < since:
            continue
        bucket = int(hashlib.sha256(t["work_id"].encode("utf-8")).hexdigest(), 16) % one_in
        rows.append({"ts": t["start"], "work_id": t["work_id"], "model": "claude-opus-5-5",
                     "arm": "control" if bucket else "sonnet"})
    return rows


def grade(now: float | None = None, placebo_since: str | None = None) -> dict:
    import time

    import yaml
    now = time.time() if now is None else now
    cfg = yaml.safe_load(PILOT.read_text(encoding="utf-8")) if PILOT.exists() else {}
    starts, ends = str(cfg.get("starts") or ""), str(cfg.get("ends") or "")
    tier_log = _shared("docs/observability/model_tier_log.jsonl")
    exec_log = _shared("docs/observability/seat-executor-log.md")
    exec_text = exec_log.read_text(errors="replace") if exec_log.exists() else ""
    if placebo_since:
        starts, ends = placebo_since, "placebo (A/A: both arms Opus)"
        rows = placebo_rows(exec_text, placebo_since, int(cfg.get("one_in") or 4))
    else:
        rows = arm_rows(tier_log.read_text(errors="replace") if tier_log.exists() else "", starts, ends)
    turns = join(rows, executor_turns(exec_text))
    for t in turns:
        if t["landed"] is None:
            continue
        session = transcript_of(t)
        t["usd"], shas = cost_and_shas(session) if session else (None, [])
        t["rework"] = reworked(shas, now) if t["landed"] and shas else (None if t["landed"] else False)
    arms = {a: summarise([t for t in turns if t["arm"] == a]) for a in ("sonnet", "control")}
    return {"window": [starts, ends], "decisions_logged": len(rows), "arms": arms,
            "verdict": verdict(arms["sonnet"], arms["control"]), "turns": turns}


def _pct(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


def _bound(b):
    return "n/a" if not b or b[0] is None else f"{100 * b[0]:.0f}-{100 * b[1]:.0f}%"


def render(g: dict) -> str:
    lines = [f"P2 executor pilot, window {g['window'][0]} to {g['window'][1]}: "
             f"{g['decisions_logged']} arm decision(s) logged with route=seat_executor.", "",
             "| arm | graded n (pending) | landed | 95% bound | $ per landed | 90% bound | uncosted "
             "| rework | 95% bound | rework pending |", "|---|---|---|---|---|---|---|---|---|---|"]
    for arm, s in g["arms"].items():
        per = "n/a" if s["usd_per_landed"] is None else f"{s['usd_per_landed']:.2f}"
        pb = s["usd_per_landed_bound"]
        pbs = "n/a" if not pb else f"{pb[0]:.2f}-{pb[1]:.2f}"
        lines.append(f"| {arm} | {s['n']} ({s['pending']}) | {s['landed']} ({_pct(s['landed_share'])}) "
                     f"| {_bound(s['landed_bound'])} | {per} | {pbs} | {s['uncosted']} "
                     f"| {s['reworked']} of {s['rework_n']} ({_pct(s['rework_share'])}) "
                     f"| {_bound(s['rework_bound'])} | {s['rework_pending']} |")
    v = g["verdict"]
    lines.append("")
    if not v["ready"]:
        lines.append(f"Verdict: cannot yet say -- {v['why']}.")
    else:
        lines.append(f"Landed share within {LANDED_GAP_POINTS:.0f} points: {v['landed_within_10_points']}; "
                     f"rework no higher: {v['rework_no_higher']}; at least {CHEAPER_BY:.0%} cheaper per "
                     f"landed: {v['at_least_25pct_cheaper_per_landed']}.")
        lines.append(f"Verdict: {v['call'] or 'cannot yet say (a condition is not yet measurable)'}. "
                     "Point estimates, as pre-registered; read the bounds beside them.")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--placebo-since", metavar="YYYY-MM-DD",
                    help="A/A test on past all-Opus turns, armed by the pilot's own hash")
    a = ap.parse_args(argv)
    g = grade(placebo_since=a.placebo_since)
    print(json.dumps(g, indent=1, default=str) if a.json else render(g))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
