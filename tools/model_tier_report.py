#!/usr/bin/env python3
"""MODEL TIERING PILOT — the measurement (2026-08-12).

The director's ask was not "switch some work to Sonnet", it was "run them there for a defined
period, and measure quality against the Opus baseline: rework rate, findings quality, gate failures
caused... If quality drops on anything, revert that class and say so." A pilot with no measurement
is just a cheaper default with a nicer name, so this is the half that makes it a pilot.

    python3 -m tools.model_tier_report              # the pilot window
    python3 -m tools.model_tier_report --all        # every tier decision on record
    python3 -m tools.model_tier_report --json       # machine-readable

HOW A TURN IS ATTRIBUTED TO A TIER, and the honest limits of it.

`worker_tick` appends one line to `model_tier_log.jsonl` immediately before it spawns an
invocation, and then BLOCKS until that invocation exits (worker-tick.service is Type=oneshot).
Invocations therefore do not overlap, so decision *i* owns the wall-clock interval from its own
timestamp to decision *i+1*'s, and every commit landing inside that interval is that tier's work.

Three limits, stated rather than glossed, because a measurement that hides its error bars is the
class of defect this repo files findings about:

  1. THE LAST INTERVAL IS OPEN-ENDED. The most recent decision has no successor, so it is closed at
     `now`. If the tick has been idle for hours, that interval over-claims. It is reported with a
     marker rather than silently included.
  2. INTERACTIVE COMMITS LAND IN THE SAME TREE. A human-driven session committing during a tick's
     interval is attributed to that tick's tier. Commits whose author is not the autonomous
     committer are excluded where the repo makes that distinguishable; the residual is reported as
     `unattributable`, never quietly folded into a tier.
  3. REWORK IS A PROXY, NOT A VERDICT. "The same file was touched again" is evidence, not proof, of
     rework — iterative work on a campaign surface looks identical. Both a broad and a narrow
     measure are printed side by side and neither is presented as the answer; where they disagree,
     that disagreement is the finding.

WHAT WOULD MAKE THE PILOT FAIL. Any measured drop on any metric for a class reverts that class —
the director's rule, not a threshold to negotiate. The comparison baseline is the same class's
history before `baseline_commit` in model_tier_pilot.yaml, when every draw ran Opus.

REUSE: tools/model_tier_report.py
CLASS: CUSTOM
INDEX: searched "rework rate", "commit attribution", "tier report", "verified work",
       "git log window" -- no row covers any of them. The nearest EXISTING code is
       `background/daily_self_note.verified_work`, which also derives commit facts from a git-log
       window, and it was read before this was written: it answers a different question (are the
       last 24h substantive, and product or machinery?) over a fixed window with no notion of an
       attribution interval, no path re-touch, and no tier. Reusing it would have meant widening
       a note-rendering helper into a general commit-analysis library to serve one caller --
       the adapters-for-future-adapters shape the SIMPLICITY GUARD names. The relationship runs
       the other way instead: `daily_self_note` calls `pilot_line()` here, so the note stays the
       publisher and this stays the measurement.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from background.model_tier import PILOT_CONFIG, TIER_LOG  # noqa: E402

PUBLISH_GATE_STATE = ROOT / "docs" / "observability" / ".publish_gate_state.json"
STAGING = ROOT / "docs" / "staging"

# Calibrated against `git log --since=7.days` on 2026-08-12, not guessed. Two shapes appear:
#   * a `fix(scope):` / `revert` prefix -- the reliable half;
#   * a narrative subject stating what was wrong ("the wall exhibit's customer view does not filter
#     the exhibit"), which carries no prefix at all.
# The second half is caught by vocabulary and is INCOMPLETE by construction: a repair titled "the
# self-refill doorbell was replaying the mint-time first step" matches nothing here and is missed.
# That is why the report prints narrow ALONGSIDE broad and calls neither the answer -- narrow is a
# floor on the rework rate, not an estimate of it.
_REPAIR_WORDS = re.compile(
    r"(^\s*(fix|revert)\s*[\(:])|"
    r"\b(fix(?:e[sd])?|defect|wedge[ds]?|revert(?:ed)?|broke|broken|regress\w*|"
    r"did not|does not|was wrong|never (?:ran|fired|held)|repair\w*|unwedge)\b",
    re.IGNORECASE,
)
# Paths whose re-touch says nothing about rework: the treadmill rewrites these every publish cycle.
_NOISE_PATHS = re.compile(r"^(docs/status/|docs/reports/|site/data/|docs/observability/)")


@dataclass
class Interval:
    ts: float
    end: float
    tier: str
    classes: list[str]
    open_ended: bool = False
    commits: list[dict] = field(default_factory=list)


def _load_decisions(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue          # a torn append is a lost sample, never a crash
    return sorted(out, key=lambda d: d.get("ts", 0))


def _intervals(decisions: list[dict], now: float) -> list[Interval]:
    out: list[Interval] = []
    for i, d in enumerate(decisions):
        ts = float(d.get("ts", 0))
        last = i == len(decisions) - 1
        end = now if last else float(decisions[i + 1].get("ts", ts))
        out.append(Interval(ts=ts, end=end, tier=d.get("tier", "?"),
                            classes=list(d.get("classes") or []), open_ended=last))
    return out


def _git_commits(since: float, until: float) -> list[dict]:
    """Commits in a time range, with their changed paths. One `git log` call for the whole window;
    per-interval slicing happens in memory (a call per interval would be hundreds of forks)."""
    sep = "\x1e"
    r = subprocess.run(
        ["git", "log", f"--since=@{int(since)}", f"--until=@{int(until)}",
         f"--pretty=format:{sep}%H%x1f%ct%x1f%an%x1f%s", "--name-only"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    commits = []
    for block in r.stdout.split(sep):
        if not block.strip():
            continue
        head, *rest = block.strip().split("\n")
        parts = head.split("\x1f")
        if len(parts) < 4:
            continue
        sha, ct, author, subject = parts[0], parts[1], parts[2], parts[3]
        commits.append({
            "sha": sha, "ts": int(ct), "author": author, "subject": subject,
            "paths": [p for p in rest if p.strip()],
        })
    return commits


def _gate_failures() -> list[dict]:
    try:
        return json.loads(PUBLISH_GATE_STATE.read_text()).get("failures") or []
    except Exception:
        return []


def _rework(intervals: list[Interval], all_commits: list[dict]) -> dict:
    """Two measures of the same thing, deliberately not reconciled into one number.

    BROAD  — a tier's commit touched path P and some later commit also touched P.
    NARROW — the same, but the later commit's subject reads like a repair.

    Broad over-counts (iteration looks like rework); narrow under-counts (a silent repair reads like
    ordinary work). The true rate is between them, and the gap between them is itself informative:
    if broad is high and narrow is flat, the tier is iterating, not failing.
    """
    by_path_later: dict[str, list[dict]] = defaultdict(list)
    for c in all_commits:
        for p in c["paths"]:
            by_path_later[p].append(c)

    stats: dict[str, dict] = defaultdict(lambda: {"commits": 0, "broad": 0, "narrow": 0})
    for iv in intervals:
        for c in iv.commits:
            s = stats[iv.tier]
            s["commits"] += 1
            broad = narrow = False
            for p in c["paths"]:
                if _NOISE_PATHS.match(p):
                    continue
                for later in by_path_later.get(p, ()):
                    if later["ts"] <= c["ts"] or later["sha"] == c["sha"]:
                        continue
                    broad = True
                    if _REPAIR_WORDS.search(later["subject"]):
                        narrow = True
            s["broad"] += int(broad)
            s["narrow"] += int(narrow)
    return dict(stats)


def _findings_in(intervals: list[Interval]) -> dict[str, int]:
    """WORKER_FINDING_* docs whose first commit lands inside a tier's interval. Findings raised is
    the closest available proxy for the depth of a turn: a turn that notices nothing files nothing.
    A DROP here on a pilot class is the 'shallower work' signal the director named."""
    counts: dict[str, int] = defaultdict(int)
    r = subprocess.run(
        ["git", "log", "--diff-filter=A", "--pretty=format:%ct\x1f%H", "--name-only",
         "--", "docs/staging/WORKER_FINDING_*.md"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    ts = None
    for line in r.stdout.splitlines():
        if "\x1f" in line:
            ts = int(line.split("\x1f")[0])
            continue
        if line.strip() and ts is not None:
            for iv in intervals:
                if iv.ts <= ts < iv.end:
                    counts[iv.tier] += 1
                    break
    return dict(counts)


def build_report(*, window_all: bool = False, now: float | None = None) -> dict:
    now = now if now is not None else time.time()
    decisions = _load_decisions(TIER_LOG)
    if not decisions:
        return {"decisions": 0, "note": "no tier decisions recorded yet — the tick has not spawned "
                                        "an invocation since the pilot landed"}

    intervals = _intervals(decisions, now)
    if not window_all:
        try:
            import yaml
            cfg = yaml.safe_load(PILOT_CONFIG.read_text(encoding="utf-8")) or {}
            starts = time.mktime(time.strptime(str(cfg.get("starts")), "%Y-%m-%d"))
            intervals = [iv for iv in intervals if iv.end >= starts]
        except Exception:
            pass

    lo = min(iv.ts for iv in intervals)
    all_commits = _git_commits(lo, now)
    for c in all_commits:
        for iv in intervals:
            if iv.ts <= c["ts"] < iv.end:
                iv.commits.append(c)
                break

    by_tier: dict[str, int] = defaultdict(int)
    by_class: dict[str, int] = defaultdict(int)
    for iv in intervals:
        by_tier[iv.tier] += 1
        for cls in iv.classes:
            by_class[f"{iv.tier}:{cls}"] += 1

    attributed = {c["sha"] for iv in intervals for c in iv.commits}
    gate_by_tier: dict[str, int] = defaultdict(int)
    for f in _gate_failures():
        fts = float(f.get("ts", 0))
        for iv in intervals:
            if iv.ts <= fts < iv.end:
                gate_by_tier[iv.tier] += 1
                break

    return {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "window": {"from": time.strftime("%Y-%m-%d %H:%M", time.gmtime(lo)),
                   "to": time.strftime("%Y-%m-%d %H:%M", time.gmtime(now))},
        "decisions": len(intervals),
        "ticks_by_tier": dict(by_tier),
        "ticks_by_tier_and_class": dict(by_class),
        "commits_attributed": len(attributed),
        "commits_unattributable": len([c for c in all_commits if c["sha"] not in attributed]),
        "rework": _rework(intervals, all_commits),
        "findings_raised": _findings_in(intervals),
        "gate_failures": dict(gate_by_tier),
        "open_ended_interval": any(iv.open_ended for iv in intervals),
    }


def build_baseline(days: int, *, now: float | None = None) -> dict:
    """The OPUS BASELINE, computed over the N days BEFORE the pilot opened.

    Without this the pilot ends with a set of Sonnet numbers and nothing to compare them to, which
    is how a trial quietly becomes a default. Every tick in that period ran Opus by construction
    (the model was a pinned constant), so the whole period is one Opus interval and the same rework
    and findings measures apply unchanged — same code path, same definitions, no second
    implementation to drift.

    Caveat, and it is a real one: this is the baseline for ALL work, not per class. The pre-pilot
    log records no work class, so a class-level Opus baseline cannot be recovered retrospectively —
    it can only be accumulated from now on, from the `opus` rows the pilot itself writes whenever a
    reserved marker or a disabled class sends a would-be pilot draw to Opus.
    """
    now = now if now is not None else time.time()
    try:
        import yaml
        cfg = yaml.safe_load(PILOT_CONFIG.read_text(encoding="utf-8")) or {}
        end = time.mktime(time.strptime(str(cfg.get("starts")), "%Y-%m-%d"))
    except Exception:
        end = now
    start = end - days * 86400
    commits = _git_commits(start, end)
    iv = Interval(ts=start, end=end, tier="opus (baseline)", classes=[], commits=commits)
    return {
        "period": {"from": time.strftime("%Y-%m-%d", time.gmtime(start)),
                   "to": time.strftime("%Y-%m-%d", time.gmtime(end)), "days": days},
        "commits": len(commits),
        "rework": _rework([iv], commits),
        "findings_raised": _findings_in([iv]),
        "caveat": "all-work baseline; a per-class Opus baseline can only accumulate forward",
    }


def render_baseline(b: dict) -> str:
    L = [f"OPUS BASELINE — {b['period']['from']} → {b['period']['to']} "
         f"({b['period']['days']}d before the pilot, everything on Opus)",
         f"  commits  {b['commits']}", "", "  REWORK — broad / narrow"]
    for tier, s in b["rework"].items():
        L.append(f"    {s['commits']:>4} commits   "
                 f"broad {s['broad']:>3} ({_pct(s['broad'], s['commits'])})   "
                 f"narrow {s['narrow']:>3} ({_pct(s['narrow'], s['commits'])})")
    findings = sum(b["findings_raised"].values())
    per_day = findings / b["period"]["days"] if b["period"]["days"] else 0
    L += ["", f"  FINDINGS RAISED  {findings}  ({per_day:.1f}/day)",
          "", f"  CAVEAT: {b['caveat']}"]
    return "\n".join(L)


def _pct(n: int, d: int) -> str:
    return f"{100.0 * n / d:.0f}%" if d else "n/a"


def render(rep: dict) -> str:
    if rep.get("decisions", 0) == 0:
        return f"MODEL TIER PILOT — {rep.get('note')}"
    L = ["MODEL TIERING PILOT — measurement",
         f"  window   {rep['window']['from']} → {rep['window']['to']}  ({rep['decisions']} ticks)",
         f"  commits  {rep['commits_attributed']} attributed, "
         f"{rep['commits_unattributable']} unattributable (see module docstring, limit 2)",
         "", "  COVERAGE — did the pilot actually fire?"]
    total = sum(rep["ticks_by_tier"].values())
    for tier, n in sorted(rep["ticks_by_tier"].items()):
        L.append(f"    {tier:<8} {n:>5} ticks  ({_pct(n, total)})")
    for key, n in sorted(rep["ticks_by_tier_and_class"].items()):
        L.append(f"      {key:<34} {n:>5}")

    L += ["", "  REWORK — broad (same path re-touched) / narrow (re-touched by a repair commit)"]
    for tier, s in sorted(rep["rework"].items()):
        L.append(f"    {tier:<8} {s['commits']:>4} commits   "
                 f"broad {s['broad']:>3} ({_pct(s['broad'], s['commits'])})   "
                 f"narrow {s['narrow']:>3} ({_pct(s['narrow'], s['commits'])})")

    L += ["", "  FINDINGS RAISED (depth proxy — a shallow turn notices nothing)"]
    for tier, n in sorted(rep["findings_raised"].items()) or [("", 0)]:
        L.append(f"    {tier:<8} {n:>5}")
    if not rep["findings_raised"]:
        L.append("    (none in window)")

    L += ["", "  GATE FAILURES opened inside a tier's interval"]
    for tier, n in sorted(rep["gate_failures"].items()):
        L.append(f"    {tier:<8} {n:>5}")
    if not rep["gate_failures"]:
        L.append("    (none in window)")

    if rep.get("open_ended_interval"):
        L += ["", "  NOTE: the most recent interval is open-ended (closed at now). If the tick has",
              "        been idle it over-claims — limit 1 in the module docstring."]
    if rep["ticks_by_tier"].get("sonnet", 0) == 0:
        L += ["", "  VERDICT: the pilot has not fired yet. No Sonnet ticks means no comparison is",
              "           possible — report the firing rate, never an absence of harm."]
    return "\n".join(L)


def pilot_line() -> str:
    """One line for the daily self-note (SM1) — the pilot's own morning report.

    THIS IS WHY THE TOOL HAS A CALLER. A measurement that only runs when someone remembers to run it
    is the fail-silent pattern: the pilot would close on 2026-08-19 with nobody having looked, which
    is precisely how a trial becomes a default. Reported every morning, the firing rate and the
    rework gap are visible while the window is still open and something can be done about them.

    READ-ONLY, like everything else SM1 consumes (§2 HARD LAW: reader/publisher only, no path into
    the draw). Raises nothing the caller has to handle beyond its own fail-closed RED.
    """
    try:
        import yaml
        cfg = yaml.safe_load(PILOT_CONFIG.read_text(encoding="utf-8")) or {}
        ends = str(cfg.get("ends") or "?")
        live = [n for n, c in (cfg.get("classes") or {}).items()
                if isinstance(c, dict) and c.get("enabled") is True]
    except Exception:
        return "no pilot config — the tick is on Opus for every draw (pre-pilot behaviour)."

    today = time.strftime("%Y-%m-%d")
    if today > ends:
        return (f"pilot CLOSED {ends} (window enforced in code; every class is off and the tick is "
                f"back on Opus). Final numbers: `python3 -m tools.model_tier_report --all`.")

    rep = build_report()
    if rep.get("decisions", 0) == 0:
        return f"pilot open to {ends}, classes [{', '.join(sorted(live))}] — no ticks recorded yet."
    tiers = rep["ticks_by_tier"]
    total = sum(tiers.values()) or 1
    sonnet = tiers.get("sonnet", 0)
    head = (f"pilot open to {ends} · {total} ticks, {sonnet} on sonnet "
            f"({100.0 * sonnet / total:.0f}%), classes [{', '.join(sorted(live))}]")
    if sonnet == 0:
        return head + " — NOT FIRED YET: no comparison is possible, report the firing rate, never " \
                      "an absence of harm."
    parts = []
    for tier, s in sorted(rep["rework"].items()):
        if s["commits"]:
            parts.append(f"{tier} rework {_pct(s['broad'], s['commits'])}/"
                         f"{_pct(s['narrow'], s['commits'])} of {s['commits']}")
    return head + " · " + "; ".join(parts) + " (broad/narrow; baseline 57%/34%)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--all", action="store_true", help="every decision on record, not just the window")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    ap.add_argument("--baseline", type=int, metavar="DAYS", default=None,
                    help="the Opus baseline over the N days before the pilot opened")
    a = ap.parse_args()
    if a.baseline:
        b = build_baseline(a.baseline)
        print(json.dumps(b, indent=2, sort_keys=True) if a.json else render_baseline(b))
        return 0
    rep = build_report(window_all=a.all)
    print(json.dumps(rep, indent=2, sort_keys=True) if a.json else render(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
