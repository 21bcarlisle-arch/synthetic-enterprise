#!/usr/bin/env python3
"""READ the last stretch of commits the way a person reads it, and say when the shape is wrong.

Director, 2026-09-02, after a daemon put 29 empty merges on origin over three and a quarter hours:

    "Every instrument you have counts commits, gates them or receipts them. None reads them. Twelve
     identical titles in an hour was visible at a human glance and invisible to you by construction,
     because nothing asks whether a commit carries any work -- so a daemon producing empty merges
     lit up every liveness surface you have."

That is the whole finding, and it held on three separate surfaces at once:

  * `deadmans_switch._is_non_progress_commit` decides work by a DENYLIST OF SUBJECT PREFIXES
    (`chore(`, auto-process, HARDEN). "merge origin/main: automatic reconciliation in an isolated
    worktree" matched none of them, so 29 no-op commits refreshed the liveness clock and the STALL
    alarm stayed clear through the entire outage. A denylist of names is fail-open on the next
    name -- the same shape as the one refused at the door of `company/billing/raw_account_export`
    this morning, arrived at independently six hours apart.
  * `delivery_seat.commits_since` decides work by FILENAME, and `git log --name-only` prints no
    filenames at all for a merge. So every merge scored `substantive: False`, `is_material` read
    the stretch as EMPTY, and the seat SKIPPED orientation -- a machine spinning at full tilt is
    indistinguishable from a quiet night.
  * the publish path and the gate counted, receipted and refused against those commits without
    once asking what was in them.

## THE RULE, AND WHY IT IS STRUCTURAL RATHER THAN LEXICAL

    A commit carries work IFF its tree differs from EVERY one of its parents' trees.

Nothing about a subject line, an author or a path is consulted, so a new class of no-op commit
cannot be work-by-default the way it is under a denylist. It is exactly right on the four cases:

  ordinary commit      tree != parent                      -> WORK
  empty commit         tree == parent                      -> none
  substantive merge    tree differs from both parents      -> WORK (it resolved something)
  trivial/no-op merge  tree == one parent's tree           -> none: it recorded topology only

The 29 merges are the last row. Each had `p1` = the stale local HEAD, `p2` = the previous merge,
and a tree byte-identical to `p2` -- a commit that changed nothing about the repository's content
and existed only to move a ref.

## WHAT IT CLAIMS AND WHAT IT DOES NOT

It claims that a stretch of commits carrying no work is a FINDING ABOUT THE MACHINE. It does not
claim the reverse: a commit that carries work may still be worthless, and this cannot tell. It is a
floor under noise, not a measure of value.

And a QUIET stretch is not this. No commits at all is a different reading with different causes
(nobody working, a wedged gate, a stopped daemon), and conflating the two is what would make this
instrument fire on every genuinely idle night. `narrative()` reports the two separately and the
callers act on them separately.
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

#: A run of identical subjects this long is a loop rather than a coincidence. Three is the smallest
#: number that cannot be two people naming a thing the same way, which does happen.
REPEAT_RUN = 3

#: How many commits a stretch needs before "none of them carried work" is a statement about the
#: machine rather than about a single housekeeping commit.
NO_WORK_RUN = 3

#: Consecutive intervals within this fraction of each other read as a CADENCE -- a timer, not a
#: person. 29 merges arrived 6m20s apart to within a few seconds.
METRONOME_TOLERANCE = 0.25
METRONOME_RUN = 4

REPETITION = "REPETITION"
NO_WORK = "NO_WORK"
METRONOME = "METRONOME"
UNREADABLE = "UNREADABLE"


def _git(project: Path, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(project), capture_output=True, text=True,
                          timeout=timeout)


def _trees(project: Path, shas: list[str]) -> dict[str, str]:
    """`sha -> tree sha` for every sha given, in ONE `cat-file --batch-check` pass.

    Parents routinely fall outside the window being read, so this has to answer for arbitrary shas
    rather than only for the commits listed. A sha git cannot resolve is simply absent from the
    result, and `carries_work` treats an unresolvable parent as "cannot tell" rather than as
    agreement -- see there.
    """
    if not shas:
        return {}
    query = "".join("{}^{{tree}}\n".format(s) for s in shas)
    try:
        proc = subprocess.run(["git", "cat-file", "--batch-check"], cwd=str(project),
                              input=query, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return {}
    if proc.returncode != 0:
        return {}
    out: dict[str, str] = {}
    for sha, line in zip(shas, (proc.stdout or "").splitlines()):
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "tree":
            out[sha] = parts[0]
    return out


def read_commits(project: Path | None = None, *, since_hours: float | None = None,
                 limit: int = 40) -> list[dict]:
    """The stretch, as rows: sha, when, author, subject, parents, and whether it CARRIES WORK.

    `carries_work` is None -- not False -- when a parent's tree could not be resolved (a shallow
    clone, a pruned object). A control that cannot read its subject must say so rather than report
    the reassuring answer; this project has paid for the other choice three times in one day
    (`fail_closed_on_unreadable_input`).
    """
    project = project or PROJECT_DIR
    argv = ["log", "--format=%H%x00%P%x00%ct%x00%an%x00%s", "-n", str(limit)]
    if since_hours is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
        argv.insert(1, "--since={}".format(cutoff.isoformat()))
    try:
        proc = _git(project, *argv)
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []

    rows: list[dict] = []
    for line in (proc.stdout or "").splitlines():
        if line.count("\x00") < 4:
            continue
        sha, parents, when, author, subject = line.split("\x00", 4)
        rows.append({"sha": sha, "short": sha[:9], "parents": parents.split() if parents else [],
                     "epoch": int(when), "author": author, "subject": subject})

    wanted = {r["sha"] for r in rows} | {p for r in rows for p in r["parents"]}
    trees = _trees(project, sorted(wanted))
    for row in rows:
        row["tree"] = trees.get(row["sha"])
        row["carries_work"] = _carries_work(row, trees)
    return rows


def _carries_work(row: dict, trees: dict[str, str]) -> bool | None:
    """The rule: the tree differs from EVERY parent's tree.

    A root commit (no parents) carries work if it has a tree at all. An unresolvable tree anywhere
    in the comparison yields None -- unknown -- because "I could not read it" and "it changed
    nothing" are different answers and only one of them is a defect report.
    """
    mine = trees.get(row["sha"])
    if mine is None:
        return None
    if not row["parents"]:
        return True
    for parent in row["parents"]:
        theirs = trees.get(parent)
        if theirs is None:
            return None
        if theirs == mine:
            return False
    return True


def _runs(rows: list[dict], key) -> list[list[dict]]:
    """Maximal runs of CONSECUTIVE rows agreeing on `key`. Rows arrive newest-first from git log;
    order is preserved so a reported run reads in the same direction as the log a person would."""
    out: list[list[dict]] = []
    for row in rows:
        if out and key(out[-1][-1]) == key(row):
            out[-1].append(row)
        else:
            out.append([row])
    return out


def _is_metronome(run: list[dict]) -> float | None:
    """The mean interval, if this run arrived on a TIMER rather than from a person.

    A person's commits are irregular by nature. Intervals that agree to within a quarter of their
    mean are a cadence, and naming that is what turns "lots of similar commits" into "a daemon is
    looping" -- the difference between a smell and a diagnosis.
    """
    if len(run) < METRONOME_RUN:
        return None
    stamps = sorted(r["epoch"] for r in run)
    gaps = [b - a for a, b in zip(stamps, stamps[1:])]
    if not gaps or min(gaps) <= 0:
        return None
    mean = sum(gaps) / len(gaps)
    if mean <= 0:
        return None
    if max(abs(g - mean) for g in gaps) / mean > METRONOME_TOLERANCE:
        return None
    return mean


def findings(rows: list[dict]) -> list[dict]:
    """What is WRONG WITH THE SHAPE of this stretch. `[]` means it reads like real work.

    Every finding names the commits it is about, because "830 red tests" with no named test is the
    thing the director already ruled is not actionable -- *"there's nothing to fix, only a number to
    worry about."* A shape finding with no shas would be the same defect wearing a new subject.
    """
    out: list[dict] = []
    if not rows:
        return out

    for run in _runs(rows, lambda r: r["subject"]):
        if len(run) < REPEAT_RUN:
            continue
        shas = [r["short"] for r in run]
        empty = [r for r in run if r["carries_work"] is False]
        mean = _is_metronome(run)
        detail = "{} consecutive commits carry the identical subject {!r}".format(
            len(run), run[0]["subject"][:80])
        if len(empty) == len(run):
            detail += ", and NONE of them changed anything: every tree equals a parent's"
        elif empty:
            detail += ", {} of which changed nothing".format(len(empty))
        out.append({"kind": REPETITION, "commits": shas, "count": len(run), "detail": detail,
                    "subject": run[0]["subject"]})
        if mean is not None:
            out.append({
                "kind": METRONOME, "commits": shas, "count": len(run),
                "interval_seconds": round(mean),
                "detail": "those {} arrived every {:.0f}s to within {:.0%} -- a timer, not a "
                          "person; look for the daemon on that cadence".format(
                              len(run), mean, METRONOME_TOLERANCE),
                "subject": run[0]["subject"]})

    for run in _runs(rows, lambda r: r["carries_work"] is False):
        if run[0]["carries_work"] is not False or len(run) < NO_WORK_RUN:
            continue
        out.append({
            "kind": NO_WORK, "commits": [r["short"] for r in run], "count": len(run),
            "detail": "{} consecutive commits changed NOTHING -- each tree is identical to one of "
                      "its own parents, so the repository's content is exactly what it was {} "
                      "commits ago".format(len(run), len(run)),
            "subject": run[0]["subject"]})

    unknown = [r["short"] for r in rows if r["carries_work"] is None]
    if unknown:
        out.append({"kind": UNREADABLE, "commits": unknown, "count": len(unknown),
                    "detail": "{} commit(s) could not be read for content, so this stretch was "
                              "NOT cleared -- absence of a finding here is not evidence".format(
                                  len(unknown)),
                    "subject": ""})
    return out


def narrative(project: Path | None = None, *, since_hours: float | None = None,
              limit: int = 40) -> dict:
    """The stretch and what is wrong with its shape, in the form a caller records.

    `quiet` and a NO_WORK finding are DELIBERATELY DIFFERENT ANSWERS. No commits at all has its own
    causes -- a stopped daemon, a wedged gate, a night off -- and firing the loop alarm on silence
    would make this instrument cry wolf on every idle stretch, which is how an instrument gets
    ignored before the one time it is right.
    """
    rows = read_commits(project, since_hours=since_hours, limit=limit)
    found = findings(rows)
    worked = [r for r in rows if r["carries_work"] is True]
    return {
        "commits": rows,
        "count": len(rows),
        "carrying_work": len(worked),
        "quiet": not rows,
        "findings": found,
        "shape_is_wrong": bool([f for f in found if f["kind"] != UNREADABLE]),
    }


def render(state: dict, *, width: int = 96) -> str:
    """The stretch as a person would read it: what landed, what it was, whether the shape is right.

    The LIST comes first and the verdict second, deliberately. The director saw this at a glance
    from a list; a summary line that said "29 commits, 0 substantive" would have been true all
    afternoon and read as a statistic. Twelve identical titles in a column reads as a fault.
    """
    lines: list[str] = []
    if state["quiet"]:
        lines.append("no commits in the stretch -- quiet, which is not the same as spinning")
    for row in state["commits"]:
        when = datetime.fromtimestamp(row["epoch"], timezone.utc).strftime("%H:%M")
        mark = {True: "  ", False: "!!", None: " ?"}[row["carries_work"]]
        subject = row["subject"]
        room = width - 24
        lines.append("{} {} {} {}".format(mark, when, row["short"],
                                          subject if len(subject) <= room
                                          else subject[:room - 1] + "…"))
    if state["commits"]:
        lines.append("")
        lines.append("{} commit(s), {} carrying work ({} changed nothing at all)".format(
            state["count"], state["carrying_work"],
            sum(1 for r in state["commits"] if r["carries_work"] is False)))
    for finding in state["findings"]:
        lines.append("")
        lines.append("[{}] {}".format(finding["kind"], finding["detail"]))
        lines.append("    {}".format(" ".join(finding["commits"][:12])
                                     + (" ..." if len(finding["commits"]) > 12 else "")))
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    import json
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hours", type=float, default=None, help="read this far back instead of -n")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    state = narrative(since_hours=args.hours, limit=args.limit)
    if args.json:
        print(json.dumps(state, indent=2, default=str))
    else:
        print(render(state))
    return 1 if state["shape_is_wrong"] else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
