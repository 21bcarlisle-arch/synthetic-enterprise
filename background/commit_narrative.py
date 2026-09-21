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
cannot be work-by-default the way it is under a denylist.

## AND WHY THE TREE COMPARISON IS THE WRONG QUESTION TO ASK OF A MERGE

Measured on this tree 2026-09-21, last 200 commits: 47 merges, of which 35 authored NOTHING and
this reader called every one of them work. `f56852e25` is the shape -- tree `bb737f158` against
parent trees `8b58f2e8e` and `e38e670da`, differing from both, so "differs from EVERY parent"
scored it as work, while `git show --name-only` on it is EMPTY. It is a reconciliation merge: it
took one side's file here and the other side's file there and invented nothing, and the union of
the two sides differs from each side by construction. A reconciliation merge ALWAYS differs from
every parent's tree, so the rule was not merely blind to the 35 -- it was guaranteed to be.

What a merge AUTHORS is its COMBINED DIFF: exactly the paths whose content differs from ALL of
its parents, which is the only content no parent already carried. `git diff-tree -c` computes it
and it is empty for a clean reconciliation, non-empty for a merge that resolved a conflict (12 of
the 47 -- `f0efa1a06` authored two staging files neither side had). Both halves of the work in a
clean merge are already counted, in the commits that did author them.

  ordinary commit      tree != parent                      -> WORK
  empty commit         tree == parent                      -> none: TREE_EQUALS_PARENT
  merge, conflict      combined diff non-empty             -> WORK: it authored the resolution
  merge, clean/no-op   combined diff empty                 -> none: MERGE_AUTHORED_NOTHING

The 29 are the last row, and so are a further 35 in the most recent 200. Each 29 had `p1` = the
stale local HEAD, `p2` = the previous merge, and a tree byte-identical to `p2` -- so the tree rule
did catch THAT sub-shape, and only that one. The reason is kept separate from TREE_EQUALS_PARENT
because the mechanism sentences differ and only one is true of each.

WHAT THE BRIEF'S OWN `substantive` FIELD IS NOT. `delivery_seat.commits_since` marks every merge
`files: []`, `substantive: false`, and that looked like the correct reading already computed
elsewhere. It is not: `git log --name-only` suppresses merge diffs ENTIRELY, so it says false for
the 12 that authored a conflict resolution just as loudly as for the 35 that authored nothing.
That field is silence, not agreement, and it cannot be this reader's oracle -- measured
2026-09-21: it disagrees with the combined diff on 12 of 47 merges, always in the same direction.

## THE SECOND SHAPE: A COMMIT WHOSE ONLY CONTENT IS THE PROOF IT IS ALIVE

The tree rule above is necessary and it is not sufficient, and the gap was measured on this very
tree on 2026-09-19: over the last 60 commits, TWELVE were `chore(liveness): publish heartbeat while
sim output unchanged`, every one of them read as WORK, and `shape_is_wrong` was False. The
instrument whose whole job is to notice an empty stretch reported a clean one while a fifth of it
was a timestamp moving.

It slipped all three existing legs at once, which is why it is worth naming rather than patching:

  * the TREE rule passes it -- a heartbeat really does change bytes, so the tree really does differ
    from the parent's. Structural, correct, and blind here.
  * REPETITION never fires, because the subject embeds the publishing commit's hash
    (`... (git=f8a54c985) ...`). Twelve heartbeats carry twelve DISTINCT subjects, so the leg that
    caught the 29 merges by their identical titles cannot see these at all.
  * METRONOME rides on REPETITION's runs, so it never gets asked.

    A commit carries work IFF its tree differs from every parent's AND its whole diff, against
    every parent, is NOT confined to the declared liveness surface.

KEYED TO THE PROPERTY, NOT TO TODAY'S TWO FILENAMES. The surface is read from
`process_run_complete.LIVENESS_SURFACE_FILES` -- the publisher's OWN declaration of what it commits
-- so the day a third liveness file is added it is added THERE, because the producer cannot publish
it otherwise, and this reader picks it up without being touched. A private copy of the pair here
would be a second hand-typed answer that goes stale silently, which is the defect this project has
paid for most often. If that declaration cannot be read, the stretch is NOT cleared: `findings()`
says so in the UNREADABLE class rather than quietly falling back to the flattering answer.

WHAT THIS DELIBERATELY DOES NOT CLAIM: that a heartbeat commit is a fault. It is not -- it exists
on purpose, to bound published-heartbeat staleness when the sim output is unchanged
(`_refresh_published_liveness_on_skip`). What is a fault is COUNTING it as work, because that is
what lets a stretch of pure heartbeat inflate every productivity surface the seat reads.

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
LIVENESS_ONLY = "LIVENESS_ONLY"

#: Why a commit that changed nothing worth orienting on changed nothing. Kept on the row because
#: NO_WORK's sentence asserts a MECHANISM ("its tree is identical to a parent's"), and that
#: sentence is FALSE of a liveness-only commit -- whose tree does differ. A finding that explains
#: itself wrongly is how the reader learns to stop believing the finding.
TREE_EQUALS_PARENT = "tree_equals_parent"
LIVENESS_SURFACE_ONLY = "liveness_surface_only"
#: A merge whose tree differs from every parent's and whose COMBINED DIFF is empty: it took one
#: side here and the other there and authored nothing of its own. The tree-equality sentence is
#: FALSE of it -- that is the whole reason it needs a reason of its own.
MERGE_AUTHORED_NOTHING = "merge_authored_nothing"


def _liveness_surface() -> frozenset[str] | None:
    """The publisher's OWN declaration of the files it commits as pure liveness, or None.

    Read from `process_run_complete` rather than copied, so that a third liveness file -- which
    that module must declare in order to publish it at all -- is picked up here for free. None
    means "could not read the declaration", and the callers surface that as an UNREADABLE finding
    instead of silently reverting to "nothing is liveness", which would read as a clean stretch.
    """
    try:
        from background.process_run_complete import LIVENESS_SURFACE_FILES
    except Exception:  # noqa: BLE001 - a reader must not die of a producer's import
        return None
    try:
        surface = frozenset(str(p) for p in LIVENESS_SURFACE_FILES)
    except TypeError:
        return None
    return surface or None


def _changed_paths(project: Path, rows: list[dict]) -> dict[str, set[str] | None]:
    """`sha -> the paths this commit changed against EVERY parent`, or None where unknowable.

    Single-parent commits are answered in ONE batched `diff-tree --stdin` pass. Merges are asked
    per parent, because `diff-tree` prints a merge's sha with NO PATHS UNDER IT by default -- and
    reading that silence as "changed nothing" would make every merge in the tree liveness-only,
    turning this leg into the fail-open it exists to close. Merges are a handful per stretch, so
    the extra calls are bounded; an unreadable one returns None and is never called liveness.
    """
    out: dict[str, set[str] | None] = {}
    simple = [r["sha"] for r in rows if len(r["parents"]) == 1]
    if simple:
        try:
            proc = subprocess.run(["git", "diff-tree", "--stdin", "-r", "--name-only"],
                                  cwd=str(project), input="\n".join(simple) + "\n",
                                  capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            proc = None
        if proc is None or proc.returncode != 0:
            out.update({s: None for s in simple})
        else:
            seen: dict[str, set[str]] = {}
            current: str | None = None
            for line in (proc.stdout or "").splitlines():
                if line in seen or (len(line) == 40 and all(c in "0123456789abcdef" for c in line)):
                    current = line
                    seen.setdefault(current, set())
                elif current is not None:
                    seen[current].add(line)
            # A sha git declined to answer for is UNKNOWN, never an empty change set.
            out.update({s: seen.get(s) if s in seen else None for s in simple})

    for row in rows:
        if len(row["parents"]) <= 1:
            continue
        union: set[str] | None = set()
        for parent in row["parents"]:
            try:
                proc = _git(project, "diff-tree", "-r", "--name-only", "--no-commit-id",
                            parent, row["sha"])
            except (OSError, subprocess.SubprocessError):
                union = None
                break
            if proc.returncode != 0:
                union = None
                break
            union.update(p for p in (proc.stdout or "").splitlines() if p)
        out[row["sha"]] = union
    return out


def _combined_diff(project: Path, rows: list[dict]) -> dict[str, set[str] | None]:
    """`merge sha -> the paths it AUTHORED`: those differing from ALL parents. None if unreadable.

    This is `git diff-tree -c` -- the same set `git show --name-only` prints for a merge, and the
    only content in a merge that no parent already carried. Asked per merge rather than batched
    because `--stdin` interleaves headers with paths and a mis-parse here reads as "authored
    nothing", which is the flattering answer; merges are a handful per stretch (47 in 200 measured
    on this tree) so the bounded extra calls are cheaper than that risk.

    Single-parent commits are absent from the result: the combined diff is not their question, and
    a caller must not read their absence as an empty change set.
    """
    out: dict[str, set[str] | None] = {}
    for row in rows:
        if len(row["parents"]) <= 1:
            continue
        try:
            proc = _git(project, "diff-tree", "-c", "-r", "--name-only", "--no-commit-id",
                        row["sha"])
        except (OSError, subprocess.SubprocessError):
            out[row["sha"]] = None
            continue
        out[row["sha"]] = (None if proc.returncode != 0
                           else {p for p in (proc.stdout or "").splitlines() if p})
    return out


def _is_liveness_only(paths: set[str] | None, surface: frozenset[str] | None) -> bool:
    """True only when this commit's whole diff sits inside the declared liveness surface.

    An EMPTY path set is deliberately not liveness-only: an empty diff is the tree rule's business
    and already reads as no-work there, and treating "I saw no paths" as "only liveness paths"
    is precisely the merge-shaped fail-open `_changed_paths` guards against.
    """
    if not surface or not paths:
        return False
    return paths <= surface


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
                 limit: int = 40, revs: tuple[str, ...] | None = None) -> list[dict]:
    """The stretch, as rows: sha, when, author, subject, parents, and whether it CARRIES WORK.

    `carries_work` is None -- not False -- when a parent's tree could not be resolved (a shallow
    clone, a pruned object). A control that cannot read its subject must say so rather than report
    the reassuring answer; this project has paid for the other choice three times in one day
    (`fail_closed_on_unreadable_input`).

    `revs` names what to read. It defaults to HEAD -- git's own default, and what every caller got
    before the argument existed -- but a caller judging the BRANCH rather than its own checkout
    must pass both sides, because a commit on `origin/main` that this checkout has not
    fast-forwarded to is otherwise not a commit at all as far as this reader is concerned. Several
    refs give the union reachable from any of them, de-duplicated by git.
    """
    project = project or PROJECT_DIR
    argv = ["log", "--format=%H%x00%P%x00%ct%x00%an%x00%s", "-n", str(limit), *(revs or ())]
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
    surface = _liveness_surface()
    changed = _changed_paths(project, rows) if surface else {}
    authored = _combined_diff(project, rows)
    for row in rows:
        row["tree"] = trees.get(row["sha"])
        row["carries_work"] = _carries_work(row, trees, authored)
        row["liveness_surface_known"] = surface is not None
        row["empty_because"] = (_why_no_work(row, trees) if row["carries_work"] is False
                                else None)
        # The liveness leg only ever takes an answer AWAY from "work"; it can never promote a
        # commit the tree rule refused, and it never overrides an honest None.
        if row["carries_work"] is True and _is_liveness_only(changed.get(row["sha"]), surface):
            row["carries_work"] = False
            row["empty_because"] = LIVENESS_SURFACE_ONLY
    return rows


def _carries_work(row: dict, trees: dict[str, str],
                  authored: dict[str, set[str] | None] | None = None) -> bool | None:
    """The rule: the tree differs from every parent's, AND a merge authored something of its own.

    A root commit (no parents) carries work if it has a tree at all. For a MERGE the tree
    comparison is necessary and nowhere near sufficient -- a reconciliation merge differs from
    every parent by construction -- so the answer is its COMBINED DIFF, which is what it authored
    that no parent already carried. See the module docstring for the measurement.

    Three-valued throughout. An unresolvable tree, or a combined diff git declined to print,
    yields None -- unknown -- because "I could not read it" and "it changed nothing" are different
    answers and only one of them is a defect report. `authored` omitted means the merge leg cannot
    run, so a merge is UNKNOWN rather than quietly falling back to the tree comparison this exists
    to replace.
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
    if len(row["parents"]) > 1:
        paths = (authored or {}).get(row["sha"])
        if paths is None:
            return None
        return bool(paths)
    return True


def _why_no_work(row: dict, trees: dict[str, str]) -> str:
    """WHICH mechanism made this commit empty -- asked only of a row already answered False.

    The two sentences are not interchangeable and a finding that explains itself wrongly teaches
    the reader to stop believing findings: an empty commit repeats a parent's tree exactly, and a
    reconciliation merge's tree matches NO parent at all.
    """
    mine = trees.get(row["sha"])
    if any(trees.get(p) == mine for p in row["parents"]):
        return TREE_EQUALS_PARENT
    return MERGE_AUTHORED_NOTHING


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
            # The clause names the MECHANISM, so it has to be true of this run: a run of
            # reconciliation merges changed nothing and its trees match NO parent.
            detail += (", and NONE of them changed anything: "
                       + ("every tree equals a parent's"
                          if {r.get("empty_because") for r in empty} == {TREE_EQUALS_PARENT}
                          else "not one of them authored any content"))
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
        # The sentence must fit the run it is about: a liveness-only commit's tree does NOT equal
        # its parent's, so the mechanism clause is only stated where it is actually true.
        reasons = {r.get("empty_because") for r in run}
        if reasons == {TREE_EQUALS_PARENT}:
            why = ("each tree is identical to one of its own parents, so the repository's content "
                   "is exactly what it was {} commits ago".format(len(run)))
        elif reasons == {LIVENESS_SURFACE_ONLY}:
            why = "every one of them changed only the liveness surface -- a timestamp moving"
        elif reasons == {MERGE_AUTHORED_NOTHING}:
            why = ("every one is a merge that authored nothing: each took one side's file here "
                   "and the other side's there, so its combined diff is empty and no content in "
                   "the repository originates in any of these {} commits".format(len(run)))
        else:
            why = ("each either repeats a parent's tree exactly, authored nothing of its own as "
                   "a merge, or moves only the liveness surface")
        out.append({
            "kind": NO_WORK, "commits": [r["short"] for r in run], "count": len(run),
            "detail": "{} consecutive commits carried no work -- {}".format(len(run), why),
            "subject": run[0]["subject"]})

    for run in _runs(rows, lambda r: r.get("empty_because") == LIVENESS_SURFACE_ONLY):
        if run[0].get("empty_because") != LIVENESS_SURFACE_ONLY or len(run) < NO_WORK_RUN:
            continue
        out.append({
            "kind": LIVENESS_ONLY, "commits": [r["short"] for r in run], "count": len(run),
            "detail": "{} consecutive commits published ONLY the liveness surface: the machine "
                      "proved it was alive {} times and produced nothing else. Their subjects "
                      "differ (each names its own publishing hash), so no repetition leg sees "
                      "them".format(len(run), len(run)),
            "subject": run[0]["subject"]})

    # Scattered heartbeats are the COMMON shape -- measured 12 in 60 on this tree with a longest
    # run of 2 -- so the run leg above would not have fired on the live case it was written for.
    # The count is what carries that one, and it is stated rather than left to the reader.
    scattered = [r["short"] for r in rows if r.get("empty_because") == LIVENESS_SURFACE_ONLY]
    if scattered and not any(f["kind"] == LIVENESS_ONLY for f in out):
        out.append({
            "kind": LIVENESS_ONLY, "commits": scattered, "count": len(scattered),
            "detail": "{} of {} commits in this stretch changed only the liveness surface. They "
                      "are not consecutive, so no run leg names them, and each carries a distinct "
                      "subject -- they inflate any count of commits that is read as "
                      "productivity".format(len(scattered), len(rows)),
            "subject": ""})

    # Only rows that actually CARRY the key are making a claim about the surface. Synthetic rows
    # from a caller testing the shape legs assert nothing about it and must not be answered for.
    declares = [r for r in rows if "liveness_surface_known" in r]
    if declares and not any(r["liveness_surface_known"] for r in declares):
        out.append({
            "kind": UNREADABLE, "commits": [r["short"] for r in rows][:12], "count": len(rows),
            "detail": "the liveness surface declaration could not be read, so commits that change "
                      "only a heartbeat were NOT separated from work and this stretch is not "
                      "cleared",
            "subject": ""})

    unknown = [r["short"] for r in rows if r["carries_work"] is None]
    if unknown:
        out.append({"kind": UNREADABLE, "commits": unknown, "count": len(unknown),
                    "detail": "{} commit(s) could not be read for content, so this stretch was "
                              "NOT cleared -- absence of a finding here is not evidence".format(
                                  len(unknown)),
                    "subject": ""})
    return out


def narrative(project: Path | None = None, *, since_hours: float | None = None,
              limit: int = 40, revs: tuple[str, ...] | None = None) -> dict:
    """The stretch and what is wrong with its shape, in the form a caller records.

    `quiet` and a NO_WORK finding are DELIBERATELY DIFFERENT ANSWERS. No commits at all has its own
    causes -- a stopped daemon, a wedged gate, a night off -- and firing the loop alarm on silence
    would make this instrument cry wolf on every idle stretch, which is how an instrument gets
    ignored before the one time it is right.
    """
    rows = read_commits(project, since_hours=since_hours, limit=limit, revs=revs)
    found = findings(rows)
    worked = [r for r in rows if r["carries_work"] is True]
    return {
        "commits": rows,
        "count": len(rows),
        "carrying_work": len(worked),
        "liveness_only": sum(1 for r in rows if r.get("empty_because") == LIVENESS_SURFACE_ONLY),
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
        tail = ""
        if state.get("liveness_only"):
            tail = ", {} of those only a heartbeat".format(state["liveness_only"])
        lines.append("{} commit(s), {} carrying work ({} changed nothing at all{})".format(
            state["count"], state["carrying_work"],
            sum(1 for r in state["commits"] if r["carries_work"] is False), tail))
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
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/commit_narrative.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("commit_narrative")
    import sys
    sys.exit(main())
