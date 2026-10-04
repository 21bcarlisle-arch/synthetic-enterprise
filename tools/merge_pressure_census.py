"""Which commits force the merges on origin/main, which of those merges conflict, and what they cost.

THE QUESTION, SAID BEFORE IT IS MEASURED (director, 2026-10-04: "Nothing measures which files cause
merges or what each merge costs, so the fixes went to symptoms").

A MERGE here is a commit on origin/main's history with two parents, M = merge(P1, P2). P1 is the side
that was catching up -- a lane's gated landing -- and P2 is what it caught up to. Every landing must
fast-forward origin, so a merge exists because origin moved between the lane cutting its base and the
lane pushing. The commits that moved it are the INCOMING set, `rev-list P2 ^P1 --no-merges`. Those are
what FORCED the merge: had none of them landed, the lane would have pushed without one.

Each incoming commit is put in exactly one KIND by its own path set (first match wins, in this order):

  heartbeat    every path is liveness state written on a timer (`HEARTBEAT_PATHS`)
  publish      the run-complete publish (`Auto-process run complete` subject)
  seat_record  every path is one of the delivery seat's per-orientation records (`SEAT_RECORD_PATHS`)
  work         anything else

A merge is FORCED BY a kind when every incoming commit is of that kind. `mixed` merges had more than
one kind arrive, so removing one kind would not have spared them. This is the counterfactual the
census can answer and the only one: "had this kind not committed to main, would the merge have been
needed?" -- yes for `mixed`/`work`, no for a merge forced by a single non-work kind. It does NOT model
the second-order effect (fewer merges -> fewer merge commits -> origin moves less often), which only
makes the true saving larger, so the figures here are a FLOOR.

CONFLICT is asked twice, and they are different facts:
  textual     `git merge-tree --write-tree P1 P2` refuses: git could not merge it alone
  resolved    the receipt says `conflicts-resolved:`: somebody chose the bytes

COST. Two currencies are measured; neither is estimated.
  gate_seconds   the merge commit's committer time minus P1's. It is the wait the merge added to its
                 lane's landing: the merge's own gate run plus any queueing. It is NOT pure CPU.
  tests          the receipt's `tests:` line -- how much the merge's gate actually ran.
Token cost is measured separately (`--tokens`), from session transcripts: the assistant turns whose
tool call ran a merge, and their usage. A merge driven by a script loop costs no turn at all.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Liveness state rewritten on a timer while nothing else changes.
HEARTBEAT_PATHS = frozenset({
    "site/data/tick_heartbeat.json",
    "docs/observability/agent_status.json",
    "site/data/agent_status.json",
})
#: What the delivery seat writes on every orientation (`background/delivery_seat.py`).
SEAT_RECORD_PATHS = frozenset({
    "docs/direction/DIRECTION.yaml",
    "docs/direction/decisions.jsonl",
    "docs/status/SEAT_STRETCH_LOG.md",
    "site/data/delivery.json",
    "docs/status/STARTUP_ANCHORS.md",
})
KINDS = ("heartbeat", "publish", "seat_record", "work")


def _git(*args: str, ok=(0,)) -> tuple[int, str]:
    r = subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True)
    return r.returncode, r.stdout


def kind_of(subject: str, paths: list[str]) -> str:
    if paths and set(paths) <= HEARTBEAT_PATHS:
        return "heartbeat"
    if subject.startswith("Auto-process run complete"):
        return "publish"
    if paths and set(paths) <= SEAT_RECORD_PATHS:
        return "seat_record"
    return "work"


def _commits(rev_range: list[str]) -> list[dict]:
    """Every non-merge commit in a range, with its subject and paths, in one git call."""
    _, out = _git("log", "--no-merges", "--format=\x01%H\x02%s", "--name-only", *rev_range)
    rows = []
    for block in out.split("\x01")[1:]:
        head, _, body = block.partition("\n")
        sha, _, subject = head.partition("\x02")
        rows.append({"sha": sha, "subject": subject,
                     "paths": [p for p in body.split("\n") if p.strip()]})
    return rows


_TESTS = re.compile(r"^tests: (.*)$", re.M)
_RESOLVED = re.compile(r"^conflicts-resolved: (.*)$", re.M)


def merges(since: str, ref: str = "origin/main") -> list[dict]:
    _, out = _git("log", "--merges", f"--since={since}", "--format=%H %P %ct", ref)
    rows = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue  # an octopus or a malformed line: not this census's shape, and named by count
        m, p1, p2, ct = parts
        incoming = _commits([p2, f"^{p1}"])
        kinds = Counter(kind_of(c["subject"], c["paths"]) for c in incoming)
        rc, mt = _git("merge-tree", "--write-tree", "--name-only", p1, p2)
        # `--name-only` prints the tree, the conflicted paths, a blank line, then messages.
        conflicted = (mt.split("\n\n")[0].splitlines()[1:]) if rc == 1 else []
        _, body = _git("log", "-1", "--format=%B", m)
        _, p1ct = _git("log", "-1", "--format=%ct", p1)
        tests = _TESTS.search(body)
        resolved = _RESOLVED.search(body)
        forced = (next(iter(kinds)) if len(kinds) == 1 else "mixed") if kinds else "empty"
        hot = Counter(p for c in incoming for p in set(c["paths"]))
        rows.append({
            "merge": m, "p1": p1, "p2": p2, "at": int(ct),
            "incoming": len(incoming), "kinds": dict(kinds), "forced_by": forced,
            "textual_conflict": rc == 1, "conflicted_paths": conflicted,
            "resolved": resolved.group(1).split(", ") if resolved else [],
            "gate_seconds": int(ct) - int(p1ct.strip() or ct),
            "tests": tests.group(1) if tests else None,
            "incoming_paths": dict(hot),
        })
    return rows


def _median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def summarise(rows: list[dict]) -> dict:
    by_forced = Counter(r["forced_by"] for r in rows)
    secs = defaultdict(list)
    for r in rows:
        secs[r["forced_by"]].append(r["gate_seconds"])
    # A path DRIVES a merge when it arrived in an incoming commit. Counted once per merge.
    drives = Counter(p for r in rows for p in r["incoming_paths"])
    sole = Counter()
    for r in rows:
        if r["forced_by"] in ("heartbeat", "seat_record", "publish"):
            for p in r["incoming_paths"]:
                sole[p] += 1
    tested = sum(1 for r in rows if r["tests"] and r["tests"] != "no tests selected")
    return {
        "merges": len(rows),
        "forced_by": dict(by_forced),
        "textual_conflicts": sum(r["textual_conflict"] for r in rows),
        "resolved_by_someone": sum(bool(r["resolved"]) for r in rows),
        "conflicted_paths": dict(Counter(p for r in rows for p in r["conflicted_paths"]
                                         ).most_common(15)),
        "merges_whose_gate_ran_tests": tested,
        "gate_seconds_total_by_forced": {k: sum(v) for k, v in secs.items()},
        "gate_seconds_median_by_forced": {k: _median(v) for k, v in secs.items()},
        "paths_driving_most_merges": dict(drives.most_common(20)),
        "paths_in_merges_forced_by_one_non_work_kind": dict(sole.most_common(10)),
    }


#: A tool call that runs a merge or a promotion (which merges origin in until it can push), or that
#: resolves a merge conflict. Matched against the call's own input, never the surrounding prose.
MERGE_CALL = re.compile(r"--merge\b|promote_worktree_landing|promote_any|git merge\b|merge-file|"
                        r"refresh_to_head|origin_reconcile|--resolve\b")
#: Every project directory a session working this repository writes under: the shared tree's, and
#: each worktree's (the seat executor runs from its own, and is a third of the sessions).
TRANSCRIPT_DIRS = tuple(d for d in (Path.home() / ".claude" / "projects").glob("*")
                        if d.name == "-home-rich-synthetic-enterprise" or d.name.startswith("-var-tmp-se-"))


def token_cost(since_epoch: float, dirs: tuple[Path, ...] = TRANSCRIPT_DIRS) -> dict:
    """Tokens spent by API calls whose tool call ran a merge, against all calls, since `since_epoch`.

    One API call is one `message.id`; a transcript writes one line per content block, each carrying
    the same usage, so calls are DEDUPLICATED by id or every multi-block call counts several times.
    `billed` is input + cache writes + output; cache READS are reported apart because they are the
    bulk of every long session whether or not it merges. A FLOOR: the call that reads a merge's
    result and decides what to do next is not counted, only the call that issued it."""
    calls: dict[str, dict] = {}
    for f in (f for d in dirs for f in d.glob("*.jsonl")):
        if f.stat().st_mtime < since_epoch:
            continue
        for line in f.open(errors="replace"):
            if '"assistant"' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            msg = row.get("message") or {}
            mid, usage = msg.get("id"), msg.get("usage")
            if not mid or not usage:
                continue
            try:
                ts = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")).timestamp()
            except (KeyError, ValueError):
                continue
            if ts < since_epoch:
                continue
            c = calls.setdefault(mid, {"usage": usage, "merge": False})
            for block in msg.get("content") or []:
                if block.get("type") == "tool_use" and MERGE_CALL.search(json.dumps(block.get("input"))):
                    c["merge"] = True
    out = {"calls": 0, "merge_calls": 0, "billed": 0, "merge_billed": 0,
           "cache_read": 0, "merge_cache_read": 0}
    for c in calls.values():
        u = c["usage"]
        billed = (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                  + u.get("output_tokens", 0))
        read = u.get("cache_read_input_tokens", 0)
        out["calls"] += 1
        out["billed"] += billed
        out["cache_read"] += read
        if c["merge"]:
            out["merge_calls"] += 1
            out["merge_billed"] += billed
            out["merge_cache_read"] += read
    return out


def render(days: float = 7.0) -> str:
    """The week's merge pressure as the Monday end-to-end check reads it: a few lines, every figure
    measured. Tokens are left to `--tokens` -- reading every transcript is the slow leg."""
    rows = merges(f"{min(int(days), 10000)}.days")
    if not rows:
        return "No merges on origin/main in the window."
    s = summarise(rows)
    forced = ", ".join(f"{k} {v}" for k, v in sorted(s["forced_by"].items(), key=lambda kv: -kv[1]))
    wait_h = sum(s["gate_seconds_total_by_forced"].values()) / 3600
    hot = ", ".join(f"`{p}` {n}" for p, n in list(s["conflicted_paths"].items())[:5]) or "none"
    return "\n".join([
        f"- **{s['merges']} merges**, forced by: {forced}.",
        f"- **{s['textual_conflicts']} conflicted**, {s['resolved_by_someone']} resolved by someone; "
        f"conflicted paths: {hot}.",
        f"- **Landing wait added by merges: {wait_h:.1f} h** (median per merge, by kind: "
        + ", ".join(f"{k} {v}s" for k, v in s["gate_seconds_median_by_forced"].items()) + ").",
        f"- Measured by `python3 -m tools.merge_pressure_census --since {int(days)}.days`.",
    ])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", default="14.days")
    ap.add_argument("--json", action="store_true", help="every merge row, not just the summary")
    ap.add_argument("--tokens", action="store_true", help="add the transcript token leg")
    a = ap.parse_args(argv)
    rows = merges(a.since)
    if a.tokens:
        days = float(a.since.split(".")[0])
        since = datetime.now().timestamp() - days * 86400
        print(json.dumps(token_cost(since), indent=1))
    print(json.dumps(rows if a.json else summarise(rows), indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
