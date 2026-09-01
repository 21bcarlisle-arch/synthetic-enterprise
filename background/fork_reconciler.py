"""FORK-LIFECYCLE reconciler (director P0, 2026-07-17): every fork branch must come HOME --
merge to main on success, or be reaped on failure. No fork left orphaned in limbo. This is the
core stability fix for bounded parallel: the fragmentation disease was forks that built work and
never merged back (the 33 stranded build/*/docs/* branches).

The doorbell now STATES "merge-or-reap" (an instruction); THIS is the enforcing MECHANISM.

REAP-ONLY (director policy A, confirmed): this NEVER auto-merges unreviewed work into main --
that would route around the gate-wall ("output looks sound, land it" is the forbidden reasoning).
An orphan is salvage-tagged + reaped + LOUD; landing stays the worker's in-turn GATED job. A good
orphan is recoverable from its salvage tag and re-runnable, never silently lost.

TWO MODES (detection-before-prevention, same discipline as the gate-wall):
  report-first (DEFAULT): detect orphans + LOUD alarm, NO reaping. Proves detection on the known 33
                          before any destructive mechanism is armed.
  enforce (armed ONLY by the director flag `.fork_reap_enabled`, AFTER the 33 are triaged): salvage
          -tag then reap orphans. Salvage ALWAYS precedes reap; a reap that cannot first salvage is
          refused (never delete unsalvaged work).

LIFECYCLE STATE per non-main branch:
  MERGED     tip reachable from main -> came home -> CLEANUP_ELIGIBLE (step 6, NOT reaped here)
  IN_FLIGHT  unmerged, last commit younger than FORK_DEADLINE -> a live fork -> leave alone (silent)
  ORPHAN     unmerged, older than FORK_DEADLINE -> never came home -> salvage + reap + LOUD

REPORT ONLY except the flag-gated, salvage-first reap. Never raises (a check that cannot run must
not crash the deadman cycle).

WORKTREE DIRECTORIES (H24, 2026-07-18): a step-6 CLEANUP_ELIGIBLE (MERGED) or confirmed-salvaged
branch still leaves behind its `.claude/worktrees/agent-*` administrative DIRECTORY -- a distinct
accretion from the branch itself, observed climbing 2->7 in one session until reaped by hand.
`evaluate_worktree_reap` below is the DIRECTORY-deleting follow-on to that gap: same report-first/
enforce two-mode discipline, its OWN arming flag (`.worktree_reap_enabled`, distinct blast radius
to the branch flag), and NEVER reaps a locked/main/bare/dirty worktree or one whose branch is still
LIVE (unmerged and not yet salvaged).
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
MERGE_TARGET = "main"                       # "home" = merged into main
PROTECTED_BRANCHES = {"main"}
# A fork gets this long to come home before it counts as an orphan. Generous (a legit build fork
# is minutes; the happy path merges it in-turn) so a live fork is never mistaken for an orphan;
# genuine orphans (the 33 are days old) are caught comfortably.
FORK_DEADLINE_SECONDS = 2 * 60 * 60
# ENFORCE-mode is destructive (reaps branches) -> director-reserved, fail-safe OFF. Absent = report
# -first (detect + alarm, no reap). Same trust model as .build_executor_enabled; armed only after
# the 33 are triaged and detection is trusted.
ENFORCE_FLAG = PROJECT_DIR / "docs" / "observability" / ".fork_reap_enabled"
# Branches the director has explicitly HELD from reaping -- NEVER auto-reaped even when enforce is
# armed (e.g. an orphan not yet proven superseded, kept for a daylight look). One branch name per
# line; blank / '#' lines ignored. This is what lets enforce-mode be the STANDING mechanism (auto-
# reap new orphans going forward) while a specific undecomposed branch waits, protected.
HELD_FILE = PROJECT_DIR / "docs" / "observability" / ".fork_reap_held"


def _git(*args: str) -> str:
    """Run a read git command, return stdout ('' on any failure). Never raises."""
    try:
        r = subprocess.run(["git", *args], cwd=str(PROJECT_DIR),
                           capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


# ── pure classifier (mutation-testable core) ───────────────────────────────────────────────
def classify_branch(branch: dict, now: float, deadline: float = FORK_DEADLINE_SECONDS) -> str:
    """Pure: state of one branch {name, merged: bool, last_commit_ts: float}. No I/O.
      MERGED  came home; IN_FLIGHT  young unmerged fork; ORPHAN  old unmerged fork (never home)."""
    if branch["name"] in PROTECTED_BRANCHES:
        return "PROTECTED"
    if branch.get("merged"):
        return "MERGED"
    age = now - float(branch.get("last_commit_ts", 0))
    return "ORPHAN" if age > deadline else "IN_FLIGHT"


# ── live git scan ──────────────────────────────────────────────────────────────────────────
def scan_fork_branches() -> list[dict]:
    """Every non-main branch as {name, merged, last_commit_ts}. Two git calls total (no per-branch
    subprocess): for-each-ref for name+commit-time, `branch --merged` for the reachability set."""
    refs = _git("for-each-ref", "refs/heads/", "--format=%(refname:short)%09%(committerdate:unix)")
    merged_out = _git("branch", "--merged", MERGE_TARGET, "--format=%(refname:short)")
    merged = {ln.strip() for ln in merged_out.splitlines() if ln.strip()}
    branches: list[dict] = []
    for line in refs.splitlines():
        if "\t" not in line:
            continue
        name, ts = line.split("\t", 1)
        if name in PROTECTED_BRANCHES:
            continue
        try:
            tsf = float(ts)
        except ValueError:
            tsf = 0.0
        branches.append({"name": name, "merged": name in merged, "last_commit_ts": tsf})
    return branches


def reap_enabled(flag: Path | None = None) -> bool:
    """True only if the director flag is a readable regular file (fail-safe: absent = report-first)."""
    try:
        return (flag or ENFORCE_FLAG).is_file()
    except Exception:
        return False


def held_branches(path: Path | None = None) -> set[str]:
    """Branch names the director has HELD from reaping (never auto-reaped, even under enforce).
    One name per line; blank lines, whole-line '#' comments AND trailing '#' comments ignored.
    Empty set if the file is absent/unreadable.

    Trailing comments are stripped deliberately (2026-08-03). A held entry written as
    `worktree-agent-abc   # holds the only copy of X` previously parsed as the WHOLE line,
    which can never equal a real branch name -- so the hold silently did nothing and the
    branch was reaped on the next enforce pass. That is a FAIL-OPEN in the one control
    standing between armed reaping and real work: the failure mode of a mis-parsed hold must
    be "this branch survives", never "this branch is deleted". Annotating a held branch with
    WHY it is held is exactly what a reader needs, so the parser accommodates it rather than
    the convention forbidding it.
    """
    out: set[str] = set()
    try:
        for ln in (path or HELD_FILE).read_text().splitlines():
            ln = ln.split("#", 1)[0].strip()
            if ln:
                out.add(ln)
    except Exception:
        return set()
    return out


def salvage_and_reap(branch: str) -> dict:
    """Salvage-tag THEN reap one orphan branch. Salvage ALWAYS first: create the salvage tag,
    VERIFY it resolves to the branch tip, and ONLY then delete the branch. If salvage cannot be
    confirmed, the branch is NOT deleted (never delete unsalvaged work). Returns {branch, tag,
    reaped: bool, detail}."""
    tag = "salvage/" + branch.replace("/", "_")
    tip = _git("rev-parse", branch).strip()
    if not tip:
        return {"branch": branch, "tag": tag, "reaped": False, "detail": "branch tip unreadable — refused"}
    # create the tag if absent (idempotent); the 33 already have theirs
    if not _git("rev-parse", "-q", "--verify", f"refs/tags/{tag}").strip():
        _git("tag", tag, branch)
    # VERIFY salvage before any deletion
    tagged = _git("rev-parse", "-q", f"{tag}^{{commit}}").strip()
    if tagged != tip:
        return {"branch": branch, "tag": tag, "reaped": False,
                "detail": f"salvage tag does not match tip ({tagged[:9]} != {tip[:9]}) — reap REFUSED"}
    _git("branch", "-D", branch)
    _git("worktree", "prune")
    # VERIFY THE DELETION ACTUALLY HAPPENED (2026-08-03). `_git` returns '' on any non-zero exit
    # and never raises, so `branch -D` failing was previously indistinguishable from it working:
    # this function reported reaped=True unconditionally. Observed live the first time enforce was
    # armed -- it logged "reaped 26/26" while deleting exactly ZERO branches, because git refuses
    # to delete a branch that is CHECKED OUT IN A WORKTREE and every one of these branches still
    # had its `.claude/worktrees/agent-*` directory. That is the R15 FAIL-SILENT pattern in the
    # destructive half of the reconciler: the orphan count would never fall, the alarm would never
    # clear, and the log would assert cleanup that was not happening. Post-condition beats return
    # code -- ask git whether the ref is gone.
    if _git("rev-parse", "-q", "--verify", f"refs/heads/{branch}").strip():
        wt = _worktree_holding(branch)
        why = f" — branch is checked out in worktree {wt}; reap that DIRECTORY first " \
              f"(evaluate_worktree_reap, its own .worktree_reap_enabled flag)" if wt else ""
        return {"branch": branch, "tag": tag, "reaped": False,
                "detail": f"salvaged @ {tip[:9]} but branch still present after delete{why}"}
    return {"branch": branch, "tag": tag, "reaped": True, "detail": f"salvaged @ {tip[:9]} then reaped"}


def _worktree_holding(branch: str) -> str:
    """Path of the worktree that has `branch` checked out, or '' if none. Read-only; never raises.
    Exists to make the reap refusal above ACTIONABLE -- "still present" is a symptom, "held by this
    directory" is the thing a reader can go and fix."""
    path = ""
    for line in _git("worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            path = line[len("worktree "):].strip()
        elif line.strip() == f"branch refs/heads/{branch}":
            return path
    return ""


# ── live evaluation (report-first by default; report-only unless the flag arms reap) ────────
def evaluate_fork_lifecycle(*, branches: list[dict] | None = None, now: float | None = None,
                            enforce: bool | None = None, reaper=salvage_and_reap,
                            held: set[str] | None = None) -> dict:
    """REPORT the fork-lifecycle state. In report-first mode (default) NOTHING is reaped -- orphans
    are detected + alarmed only. In enforce mode (flag armed) each ACTIVE orphan is salvage-then-
    reaped; a HELD orphan (director-held) is NEVER reaped and reads as acknowledged (no alarm), so
    enforce can be the STANDING mechanism while a held branch waits. Never raises. Injectable."""
    if branches is None:
        branches = scan_fork_branches()
    if now is None:
        now = time.time()
    if enforce is None:
        enforce = reap_enabled()
    if held is None:
        held = held_branches()

    all_orphans, in_flight, merged = [], [], []
    for b in branches:
        state = classify_branch(b, now)
        if state == "ORPHAN":
            all_orphans.append(b["name"])
        elif state == "IN_FLIGHT":
            in_flight.append(b["name"])
        elif state == "MERGED":
            merged.append(b["name"])
    active_orphans = [o for o in all_orphans if o not in held]
    held_orphans = [o for o in all_orphans if o in held]

    reaped: list[dict] = []
    if enforce and active_orphans:
        for name in active_orphans:
            reaped.append(reaper(name))

    alarm = bool(active_orphans)          # a HELD orphan is acknowledged -> never alarms
    if active_orphans:
        mode = "ENFORCE (salvage+reap)" if enforce else "REPORT-FIRST (detect only, no reap)"
        shown = ", ".join(active_orphans[:6]) + (" …" if len(active_orphans) > 6 else "")
        detail = (f"{len(active_orphans)} orphaned fork branch(es) never merged home [{mode}]: {shown}"
                  + (f"; reaped {sum(1 for r in reaped if r['reaped'])}/{len(reaped)}" if enforce else ""))
        status = "FORK_ORPHANS"
    elif held_orphans:
        status = "FORK_HELD"
        detail = f"{len(held_orphans)} orphan(s) HELD from reap (director-held, acknowledged): " \
                 + ", ".join(held_orphans[:6])
    else:
        status = "FORK_CLEAN"
        detail = f"no orphans; {len(in_flight)} in-flight, {len(merged)} merged (cleanup-eligible)"
    return {"status": status, "alarm": alarm, "detail": detail,
            "orphans": active_orphans, "held_orphans": held_orphans,
            "in_flight": in_flight, "merged_eligible": merged,
            "reaped": reaped, "enforce": enforce}


# ── WORKTREE RECONCILE (step 4 / C1): "does this worktree belong?" ──────────────────────────
# This is the SAME mechanism as the fork lifecycle above, not a second scanner: a worktree's
# belonging is DERIVED from its branch's lifecycle state. It reuses scan_fork_branches/
# classify_branch and adds only the one thing branch data cannot give -- a `git worktree list`
# scan. Declared = the main worktree; a fork worktree BELONGS only while its branch is IN_FLIGHT
# (a live fork building). A worktree tied to an ORPHAN/MERGED/absent branch, or detached, is
# UNDECLARED accumulation -> LOUD. REPORT-ONLY (G-R3: NO prune-by-inference -- reaping an
# undeclared thing by inference is exactly what killed the director's console in the blackout).


def scan_worktrees() -> list[dict]:
    """Every registered worktree as {path, branch, head, detached, locked, locked_reason, bare}.
    Parses `git worktree list --porcelain`. `locked`/`bare` default False; `locked_reason` is the
    text after `locked` on its porcelain line, or None if locked with no reason given.

    `head` (2026-08-30) is the porcelain's own `HEAD <sha>` line, and it is here because a
    DETACHED worktree has no branch and was therefore permanently undeterminable -- see
    `classify_detached_head`. Every worktree has a HEAD; only some have a branch."""
    out = _git("worktree", "list", "--porcelain")
    wts: list[dict] = []
    cur: dict | None = None
    for line in out.splitlines():
        if line.startswith("worktree "):
            if cur:
                wts.append(cur)
            cur = {"path": line[len("worktree "):].strip(), "branch": None, "head": None,
                   "detached": False, "locked": False, "locked_reason": None, "bare": False}
        elif cur is not None and line.startswith("HEAD "):
            cur["head"] = line[len("HEAD "):].strip()
        elif cur is not None and line.startswith("branch "):
            ref = line[len("branch "):].strip()
            cur["branch"] = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
        elif cur is not None and line.strip() == "detached":
            cur["detached"] = True
        elif cur is not None and line.strip() == "bare":
            cur["bare"] = True
        elif cur is not None and (line == "locked" or line.startswith("locked ")):
            cur["locked"] = True
            reason = line[len("locked"):].strip()
            cur["locked_reason"] = reason or None
    if cur:
        wts.append(cur)
    return wts


def classify_worktree(wt: dict, main_path: str, branch_states: dict) -> str:
    """Pure: BELONGS if it is the main worktree, or a fork worktree whose branch is IN_FLIGHT (a
    live fork). PENDING_REAP if its branch has already MERGED (came home) — a benign transient in
    the normal merge→reap lifecycle window, NOT accretion (the H24 dir-reaper removes it moments
    later; flagging it pages the director on healthy churn — the transient-ping defect the advisor
    escalated 2026-07-19). UNDECLARED (genuine accretion) only for detached, no/unknown branch, or
    an ORPHAN branch (unmerged and old — never came home)."""
    if wt["path"] == main_path:
        return "BELONGS"
    bstate = branch_states.get(wt["branch"]) if wt.get("branch") else None
    if bstate == "IN_FLIGHT":
        return "BELONGS"
    if bstate == "MERGED":
        return "PENDING_REAP"
    return "UNDECLARED"


def evaluate_worktree_reconcile(*, worktrees: list[dict] | None = None,
                                branch_states: dict | None = None,
                                main_path: str | None = None, now: float | None = None) -> dict:
    """REPORT-ONLY reconcile of the worktree set vs declared. Never prunes. Never raises. Injectable
    for tests. LOUD when an undeclared (accreting) worktree is present."""
    if worktrees is None:
        worktrees = scan_worktrees()
    if branch_states is None:
        _now = now if now is not None else time.time()
        branch_states = {b["name"]: classify_branch(b, _now) for b in scan_fork_branches()}
    if main_path is None:
        main_path = str(PROJECT_DIR)

    undeclared, belongs, pending_reap = [], [], []
    for wt in worktrees:
        cls = classify_worktree(wt, main_path, branch_states)
        if cls == "BELONGS":
            belongs.append(wt["path"])
        elif cls == "PENDING_REAP":
            pending_reap.append(wt["path"])          # merged, awaiting the dir-reaper — benign transient
        else:
            bstate = ("detached" if wt.get("detached") else
                      (branch_states.get(wt["branch"], "no-branch") if wt.get("branch") else "no-branch"))
            undeclared.append({"path": wt["path"], "branch": wt.get("branch"), "branch_state": bstate})

    alarm = bool(undeclared)
    if not undeclared:
        pr = f", {len(pending_reap)} pending-reap (benign transient)" if pending_reap else ""
        return {"status": "WORKTREE_CLEAN", "alarm": False,
                "detail": f"{len(belongs)} declared worktree(s), none undeclared{pr}",
                "undeclared": [], "pending_reap": pending_reap}
    shown = ", ".join(f"{u['path'].split('/')[-1]}({u['branch_state']})" for u in undeclared[:6])
    return {"status": "WORKTREE_UNDECLARED", "alarm": True,
            "detail": f"{len(undeclared)} UNDECLARED worktree(s) (accretion, report-only): {shown}",
            "undeclared": undeclared, "pending_reap": pending_reap}


# ── WORKTREE DIRECTORY REAP (H24): the follow-on to CLEANUP_ELIGIBLE (step 6) ───────────────
# `evaluate_worktree_reconcile` above is deliberately REPORT-ONLY (G-R3: no prune-by-inference) --
# it makes accretion VISIBLE, never destructive. This is the DIRECTORY-DELETING mechanism that
# gap left open: a fork worktree whose branch already CAME HOME (MERGED) or was already
# confirmed-salvaged (branch gone, salvage tag proves `salvage_and_reap` ran) is safe to remove --
# the work is preserved (in main, or in the salvage tag), only the now-redundant worktree
# ADMINISTRATIVE DIRECTORY is stale. Same two-mode discipline as the branch reaper above:
# report-first (DEFAULT: list what WOULD be removed, remove nothing) vs enforce (armed ONLY by its
# OWN flag -- a directory delete is a different blast radius to a branch delete and gets its own
# arming switch, never silently riding on ENFORCE_FLAG). `git worktree remove` is called WITHOUT
# --force so git's own dirty/locked refusal is a SECOND, independent safety net on top of the
# classifier below -- belt and braces for a delete this size (never trust one gate alone).
#
# NEVER REAP (the load-bearing invariant): the main/primary worktree, a bare worktree, a LOCKED
# worktree (an active fork holds a lock while building), a worktree with uncommitted/untracked
# changes, or one whose branch is still LIVE (IN_FLIGHT or an as-yet-unsalvaged ORPHAN -- salvage
# always precedes reap, same floor as the branch reaper).

WORKTREE_REAP_ENFORCE_FLAG = PROJECT_DIR / "docs" / "observability" / ".worktree_reap_enabled"


# How many STRANDED worktrees before the reaper is judged to be failing rather than idling. A
# couple of dirty forks mid-build is ordinary churn; a standing population is the control-set hole.
STRANDED_WORKTREE_ALARM_AT = 5


def worktree_reap_enabled(flag: Path | None = None) -> bool:
    """True only if the director flag is a readable regular file (fail-safe: absent = report-first,
    same convention as `reap_enabled` for branches -- but its OWN flag/file, not shared with it)."""
    try:
        return (flag or WORKTREE_REAP_ENFORCE_FLAG).is_file()
    except Exception:
        return False


def _worktree_dirty(path: str) -> bool:
    """True if `path` has uncommitted/untracked changes, OR the check itself could not be run.
    Fail-SAFE: an unreadable tree is treated as dirty (never reap on an unknown state), never
    silently coerced to clean."""
    try:
        r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=path,
                           capture_output=True, text=True, timeout=30)
        return True if r.returncode != 0 else bool(r.stdout.strip())
    except Exception:
        return True


def _salvage_tag_for(branch: str) -> str | None:
    """The salvage tag name if one exists and resolves for `branch` (proof the branch was already
    confirmed-salvaged by `salvage_and_reap`), else None. Mirrors the tag-name convention there."""
    tag = "salvage/" + branch.replace("/", "_")
    return tag if _git("rev-parse", "-q", "--verify", f"refs/tags/{tag}").strip() else None


def detached_salvage_tag_name(head: str) -> str:
    """The tag name pinning a detached worktree's HEAD. One convention, one place."""
    return "salvage/detached-" + str(head)[:12]


def _detached_salvage_tag_for(head: str | None) -> str | None:
    """The salvage tag pinning this detached HEAD, if one exists and resolves. Else None."""
    if not head:
        return None
    tag = detached_salvage_tag_name(head)
    return tag if _git("rev-parse", "-q", "--verify", f"refs/tags/{tag}").strip() else None


def _head_reachable_from_main(head: str | None) -> bool:
    """True if `head` is an ancestor of main -- i.e. this commit already came home."""
    if not head:
        return False
    from subprocess import CalledProcessError, run
    try:
        r = run(["git", "-C", str(PROJECT_DIR), "merge-base", "--is-ancestor", head, "main"],
                capture_output=True, timeout=30)
    except (OSError, CalledProcessError):
        return False
    return r.returncode == 0


def classify_detached_head(head: str | None, *, reachable: bool, salvage_tag: str | None) -> str:
    """Pure: the lifecycle state of a DETACHED worktree's HEAD, in the same vocabulary as
    `classify_branch` uses for a branch.

    WHY THIS EXISTS (2026-08-30). `classify_worktree_reap` refused every detached worktree with
    "detached/no branch -- undetermined, never reaped", and `_LIVE_REFUSALS` scored that refusal
    as the control WORKING rather than as STRANDED. Both halves were wrong in the same direction,
    and together they made a detached worktree immortal AND invisible: `[WORKTREE UNDECLARED]`
    fired 159 times over 14.3 hours naming three of them while `refusal_is_stranded` reported the
    reaper as correctly sparing them. That is the exact accretion this module was written to stop,
    reappearing in the one population its own stranded/live split could not see -- and it is the
    reason the separation existed in the first place (H24, 26 worktrees over 16 days behind a
    green report).

    The refusal was not paranoid, it was incomplete. "Undetermined" was true of the CODE, not of
    the worktree: a detached HEAD is a commit, and a commit is determinable exactly as a branch
    tip is.

      MERGED    reachable from main -- the commit came home; removing the directory touches
                nothing that is not already on main.
      SALVAGED  not reachable, but pinned by a salvage tag -- the work is preserved and
                recoverable, so the directory is a redundant working copy.
      ORPHAN    not reachable and not pinned. Refused, and STRANDED rather than live, so it is
                reported loudly instead of being counted as correctly spared. Salvage-tagging it
                is what moves it on, and that is a deliberate act with a tag to show for it.
    """
    if reachable:
        return "MERGED"
    if salvage_tag:
        return "SALVAGED"
    return "ORPHAN"


def _determine_detached(wt: dict, reachable_fn, detached_tag_fn) -> str | None:
    """The detached-HEAD state for `wt`, or None if it is not detached (so the branch path runs).

    One place, so `evaluate_worktree_reap` and `reap_one_worktree` cannot disagree about whether
    a worktree is reapable -- the pair of them disagreeing is how a directory gets removed by one
    door and refused by the other.
    """
    if not (wt.get("detached") or not wt.get("branch")):
        return None
    head = wt.get("head")
    return classify_detached_head(
        head, reachable=reachable_fn(head), salvage_tag=detached_tag_fn(head))


def salvage_detached_head(head: str) -> dict:
    """Pin a detached worktree's HEAD with a salvage tag, so the directory becomes reapable.

    The detached counterpart of `salvage_and_reap`, and it exists so the route out of a
    `detached ORPHAN` refusal is a MECHANISM rather than a hand-typed `git tag`. Without it the
    classifier names a condition nothing can clear, which is the shape that produced the
    159-repeat alarm in the first place -- a refusal with no door beside it is a stall wearing a
    control's clothes.

    Salvage-first, never reap: this only creates and VERIFIES the tag. Whether the directory then
    goes is `evaluate_worktree_reap`'s decision on its next pass, under its own arming flag.
    Returns {"head", "tag", "salvaged": bool, "detail"}. Never raises.
    """
    tag = detached_salvage_tag_name(head)
    resolved = _git("rev-parse", "-q", "--verify", f"{head}^{{commit}}").strip()
    if not resolved:
        return {"head": head, "tag": tag, "salvaged": False,
                "detail": f"{head} does not resolve to a commit -- nothing to salvage"}
    existing = _git("rev-parse", "-q", "--verify", f"refs/tags/{tag}").strip()
    if existing:
        return {"head": head, "tag": tag, "salvaged": existing == resolved,
                "detail": ("already tagged" if existing == resolved else
                           f"tag {tag} exists but points at {existing[:12]}, not {resolved[:12]}")}
    _git("tag", tag, resolved)
    # VERIFY, exactly as `salvage_and_reap` does: an unverified tag is not a salvage, and the
    # whole safety argument for removing the directory rests on the commit being pinned.
    check = _git("rev-parse", "-q", "--verify", f"refs/tags/{tag}").strip()
    ok = check == resolved
    return {"head": head, "tag": tag, "salvaged": ok,
            "detail": "tagged and verified" if ok else "tag did not verify -- NOT salvaged"}


# A refusal reason is either LIVE -- the worktree is legitimately in use and keeping it is the
# control WORKING -- or STRANDED: the control cannot act on it and never will without a change.
# Separating these is what makes "0 eligible" interpretable; conflating them is what let 26
# worktrees accumulate over 16 days behind a green WORKTREE_REAP_CLEAN (H24, 2026-08-03).
#: `detached/no branch` was removed from this tuple on 2026-08-30. It had been scoring the one
#: population that was actually accumulating as "the control working" -- see
#: `classify_detached_head`. A detached HEAD that is unreachable and unpinned is now
#: `detached ORPHAN`, which this tuple does NOT match, so it reports STRANDED and loud.
#:
#: `live writer` WAS MISSING FROM THIS TUPLE FOR A DAY (added 2026-09-01). The refusal was written
#: on 2026-08-31, at both reap doors, correctly -- and the vocabulary that decides what a refusal
#: MEANS was not told about it. So the one refusal that is most emphatically the control working
#: ("it is in use, not abandoned") scored as the control being STUCK: five live-writer worktrees
#: counted toward `STRANDED_WORKTREE_ALARM_AT`, which is the alarm for a reaper that cannot do its
#: job. Harmless while nothing acted on the stranded set; the moment `advance_stranded` did, it
#: would have committed into a live writer's tree -- which is the exact 2026-08-31 incident that
#: prompted the live-writer refusal in the first place, arriving by the other door.
#:
#: A new refusal reason must be classified here in the same change that introduces it. There is no
#: default that is safe for both halves: unlisted means STRANDED, which over-reports a live
#: refusal, and listing everything means a genuinely stuck reaper reads as healthy.
#: `declared daemon` was added 2026-09-01 with the refusal it names, in the SAME change -- which is
#: what this tuple's own note above demands, and the first draft still got it wrong: the token read
#: `declared home` against a reason saying `a declared daemon's home worktree`, so it matched
#: nothing and the refusal scored STRANDED. The class control
#: `test_every_refusal_the_classifier_can_emit_is_deliberately_classified` caught it before it ran.
_LIVE_REFUSALS = ("main worktree", "bare worktree", "locked", "IN_FLIGHT", "live writer",
                  "declared daemon")


def declared_daemon_homes() -> tuple[str, ...]:
    """Worktree paths a DECLARED daemon owns as its home, resolved. Never raises.

    NOT ACCRETION, AND THE DIFFERENCE IS THE WHOLE POINT (2026-09-01). This reaper exists to stop
    an UNBOUNDED population of worktrees growing. A daemon's declared home is bounded at exactly
    one by construction: `seat_executor.ensure_worktree` creates it if absent and RESETS it if
    present, so reaping it between turns does not reduce anything -- it makes the next turn
    re-create it, and leaves a salvage tag behind each time. On a 30-minute timer that is roughly
    fifty tags a day: the same disease with a smaller footprint, which is not tidying.

    Between turns such a worktree is IDLE, not abandoned. `worktree_is_live` answers a different
    question -- is a writer working in it *right now* -- and it correctly says no.

    NOTHING IS LOST BY SPARING IT, and the owning module says so itself: *"this worktree holds no
    history worth keeping between turns. Anything it landed was promoted at the end of the turn
    that landed it, and anything it did not land was not finished."* That is the same reasoning
    `fork_salvage` already cites for skipping a live writer, applied to the gap between turns.

    ASKED OF THE MODULE THAT DECLARES IT, never a path literal here. A path typed into this file is
    a copy of someone else's declaration and goes stale silently -- which is the defect that put
    five worktrees beyond every control on this machine for a day.
    """
    homes: list[str] = []
    try:
        from background.seat_executor import WORKTREE
        homes.append(str(Path(WORKTREE).resolve()))
    except Exception:  # noqa: BLE001 - an unimportable owner declares no home; the reaper still runs
        pass
    return tuple(homes)


def refusal_is_stranded(reason: str) -> bool:
    """True if a kept-worktree reason means the reaper is STUCK on it rather than correctly
    sparing it. Dirty and ORPHAN are the two stranded classes: a fork in this project dies dirty,
    so `MERGED and CLEAN` is unsatisfiable for the real population -- a control-SET hole, not a
    guard defect."""
    r = str(reason or "")
    return not any(tok in r for tok in _LIVE_REFUSALS)


def classify_worktree_reap(wt: dict, main_path: str, branch_state: str | None, *,
                           dirty: bool, salvage_tag: str | None,
                           detached_head_state: str | None = None,
                           declared_homes: tuple[str, ...] = ()) -> dict:
    """Pure: given one worktree {path, branch, detached, locked, locked_reason, bare}, its branch's
    lifecycle state (None if the branch ref no longer exists at all -- e.g. already salvage-reaped),
    whether the worktree has uncommitted/untracked changes, and whether a matching salvage tag
    exists -- decide REAP eligibility. No I/O -- the mutation-testable core (mirrors
    `classify_branch` / `classify_worktree` above). Returns {"eligible": bool, "reason": str}."""
    if wt["path"] == main_path:
        return {"eligible": False, "reason": "main worktree -- never reaped"}
    if wt.get("bare"):
        return {"eligible": False, "reason": "bare worktree -- never reaped"}
    if wt.get("locked"):
        reason = wt.get("locked_reason") or "no reason given"
        return {"eligible": False, "reason": f"locked ({reason}) -- never reaped"}
    if declared_homes:
        try:
            here = str(Path(wt["path"]).resolve())
        except (OSError, ValueError):
            here = str(wt["path"])
        if here in declared_homes:
            return {"eligible": False,
                    "reason": "a declared daemon's home worktree -- bounded at one by its owner, "
                              "which recreates and resets it every turn; idle between turns is not "
                              "abandoned. See `declared_daemon_homes`."}
    branch = wt.get("branch")
    if wt.get("detached") or not branch:
        # A DETACHED HEAD IS A COMMIT, AND A COMMIT IS DETERMINABLE. See `classify_detached_head`
        # for why this was a blanket refusal until 2026-08-30 and what that cost. `dirty` is
        # still checked below on the eligible paths -- a detached worktree with uncommitted work
        # is refused for the same reason any other one is.
        if detached_head_state == "MERGED":
            head_ok, head_reason = True, "detached HEAD reachable from main -- already came home"
        elif detached_head_state == "SALVAGED":
            head_ok, head_reason = (
                True,
                f"detached HEAD unmerged but confirmed-salvaged (tag "
                f"{detached_salvage_tag_name(wt.get('head') or '')}) -- directory is a "
                f"redundant copy")
        elif detached_head_state == "ORPHAN":
            head_ok, head_reason = (
                False,
                "detached ORPHAN: HEAD is unreachable from main and carries no salvage tag -- "
                "refused until it is tagged, and STRANDED, not correctly spared")
        else:
            # No state supplied at all -- the caller did not determine it. Refuse, and say that
            # it is the DETERMINATION that is missing rather than implying the worktree is live.
            head_ok, head_reason = (
                False,
                "detached HEAD state not determined by the caller -- refused, and STRANDED")
        if not head_ok:
            return {"eligible": False, "reason": head_reason}
        if dirty:
            return {"eligible": False, "reason": "uncommitted/untracked changes -- never reaped"}
        return {"eligible": True, "reason": head_reason}
    if branch_state == "MERGED":
        branch_ok, branch_reason = True, "branch MERGED into main"
    elif branch_state is None:
        if salvage_tag:
            branch_ok, branch_reason = True, f"branch already confirmed-salvaged+reaped (tag {salvage_tag})"
        else:
            branch_ok, branch_reason = False, "branch ref absent, no salvage tag -- undetermined, never reaped"
    elif branch_state == "ORPHAN" and salvage_tag:
        # BREAKS THE DEADLOCK (2026-08-03). Before this, an ORPHAN branch and its worktree could
        # never be cleaned up in either order: `salvage_and_reap` cannot delete a branch that is
        # CHECKED OUT in a worktree (git refuses), and this classifier would not release the
        # worktree until the branch was already gone. Neither could go first, so the pair was
        # immortal -- which is the actual mechanism behind the accretion this module was written
        # to stop, and why `refusal_is_stranded` already scores ORPHAN as STRANDED rather than
        # correctly-spared. The cycle is safe to cut HERE, on the directory side, because a
        # VERIFIED salvage tag means the fork's work is committed to the branch and pinned by the
        # tag: the directory is then a redundant working copy, and removing it touches no commit.
        # The branch ref itself survives this -- it is reaped separately, on the next pass, and
        # only if it is not HELD. Deliberately narrow: still requires a salvage tag (an unsalvaged
        # orphan falls through to the refusal below) and still requires CLEAN (checked next).
        branch_ok, branch_reason = True, f"branch ORPHAN but confirmed-salvaged (tag {salvage_tag}) -- directory is a redundant copy"
    else:  # IN_FLIGHT, or an as-yet-UNSALVAGED ORPHAN -- branch still live/undecided, a real fork's home
        branch_ok, branch_reason = False, f"branch is {branch_state} -- live/undecided fork, never reaped"
    if not branch_ok:
        return {"eligible": False, "reason": branch_reason}
    if dirty:
        return {"eligible": False, "reason": "uncommitted/untracked changes -- never reaped"}
    return {"eligible": True, "reason": branch_reason}


def reap_worktree_dir(path: str) -> dict:
    """Remove ONE worktree directory. No --force: git's own refusal on dirty/locked state is a
    second, independent safety net over the classifier above. Prunes stale admin state after a
    successful remove. Returns {"path", "removed": bool, "detail"}. Never raises."""
    try:
        r = subprocess.run(["git", "worktree", "remove", path], cwd=str(PROJECT_DIR),
                           capture_output=True, text=True, timeout=60)
    except Exception as e:
        return {"path": path, "removed": False, "detail": f"exception: {e}"}
    if r.returncode != 0:
        return {"path": path, "removed": False,
                "detail": (r.stderr or r.stdout or "git worktree remove failed").strip()}
    _git("worktree", "prune")
    return {"path": path, "removed": True, "detail": "removed"}


def _live_writer_default(path: str) -> bool:
    """Is a writer's process alive inside this worktree? Delegates to the module that owns it."""
    try:
        from background.seat_executor import worktree_is_live
    except Exception:  # noqa: BLE001 - a broken import must not stop the reaper working
        return False
    return worktree_is_live(path)


def _why_stranded(stranded: list[dict]) -> str:
    """The tally of WHY the reaper is stuck, as one phrase. One implementation because both modes
    ask the same question and a status that differs by mode is how the enforce branch came to print
    CLEAN over six stranded worktrees while report-first printed STRANDED over the same six."""
    from collections import Counter
    why = Counter(
        "dirty" if "uncommitted" in k.get("reason", "") else
        "orphan-branch" if "ORPHAN" in k.get("reason", "") else
        "undetermined"
        for k in stranded
    )
    return ", ".join(f"{n} {w}" for w, n in why.most_common())


def advance_stranded(kept: list[dict], *, salvage_dirty=None, salvage_detached=None,
                     head_of=None, live_writer_fn=None) -> list[dict]:
    """Take the ONE preserving step that moves each STRANDED worktree along its lifecycle.

    WHY THE LIFECYCLE HAD NO TERMINAL STATE (2026-09-01, director: "six undeclared worktrees are
    accreting and being reported rather than cleared -- that's the isolation machinery working with
    nothing tidying up behind it. Give them a lifetime.").

    Every refusal above is individually correct and every one of them is a dead end. A dirty
    worktree is never reaped -- and nothing was cleaning it. A detached ORPHAN is "refused until it
    is tagged" -- and nothing was tagging it. `salvage_detached_head` was written as the door out of
    that exact refusal, with a docstring saying so, and it has never had a caller. So the six
    accreted: each one correctly refused, forever, by a control that named the remedy and did not
    apply it.

    This is the applying. It is deliberately NOT the reaping: salvage strictly precedes reap here as
    everywhere in this module, and separating them by one pass means the log reads SALVAGED then
    REAPED rather than presenting a preservation and a deletion as one event. The cycle is minutes.

    NOTHING HERE DESTROYS ANYTHING. `salvage_worktree` commits a dirty tree to its own HEAD;
    `salvage_detached_head` creates a verified tag. Both only ever ADD a ref. That is why running
    them automatically is safe in a way that automatic reaping is not, and it is why the arming flag
    still governs the step after this one.

    Returns one row per worktree acted on: {path, step, ok, detail}. Never raises -- a salvage that
    fails leaves the worktree stranded and loud, which is the state it was already in.
    """
    if salvage_dirty is None:
        from background.fork_salvage import salvage_worktree as salvage_dirty
    salvage_detached = salvage_detached or salvage_detached_head
    head_of = head_of or (lambda p: _git("-C", p, "rev-parse", "HEAD").strip())
    live_writer_fn = live_writer_fn or _live_writer_default

    out: list[dict] = []
    for k in kept:
        reason = str(k.get("reason", ""))
        if not refusal_is_stranded(reason):
            continue                      # locked / live / main -- correctly spared, not stuck
        path = k["path"]
        # ASKED AGAIN, INDEPENDENTLY. `refusal_is_stranded` already excludes a live writer, and
        # that is a check on a STRING this function did not produce: it was wrong for a full day
        # (see `_LIVE_REFUSALS`). Committing into a live writer's tree is the one irreversible
        # mistake available here, so it gets the same belt-and-braces the reap itself gets from
        # git's own no-force refusal -- never trust one gate alone.
        if live_writer_fn(path):
            out.append({"path": path, "step": "none", "ok": False,
                        "detail": "a live writer holds this worktree -- not advanced"})
            continue
        try:
            if "uncommitted" in reason:
                # DIRT FIRST, because a dirty worktree cannot be tagged into a stable state: the
                # tag would pin a commit that does not contain the uncommitted work beside it.
                r = salvage_dirty({"path": path, "branch": k.get("branch")})
                ok = r.get("action") in ("SALVAGED", "NOOP")
                out.append({"path": path, "step": "salvage_dirty", "ok": ok,
                            "detail": f"{r.get('action')}: {r.get('sha') or r.get('reason', '')}"})
            elif "detached ORPHAN" in reason:
                head = head_of(path)
                r = salvage_detached(head)
                out.append({"path": path, "step": "salvage_detached", "ok": bool(r.get("salvaged")),
                            "detail": f"{r.get('tag')}: {r.get('detail')}"})
            else:
                # A stranded refusal with no step behind it. Named rather than skipped silently --
                # a lifecycle with an unreachable state is exactly the defect this function exists
                # to close, and a new one must not be able to hide inside it.
                out.append({"path": path, "step": "none", "ok": False,
                            "detail": f"no advancing step for this refusal: {reason[:120]}"})
        except Exception as e:  # noqa: BLE001 - a failed salvage must not stop the sweep
            out.append({"path": path, "step": "error", "ok": False, "detail": f"{type(e).__name__}: {e}"})
    return out


def evaluate_worktree_reap(*, worktrees: list[dict] | None = None, branch_states: dict | None = None,
                           main_path: str | None = None, now: float | None = None,
                           enforce: bool | None = None, dirty_fn=None, salvage_tag_fn=None,
                           remover=None, reachable_fn=None, detached_tag_fn=None,
                           live_writer_fn=None, advance=None) -> dict:
    """REPORT the worktree-DIRECTORY reap state. Report-first by default (list what WOULD be
    removed, remove nothing); enforce (armed by `WORKTREE_REAP_ENFORCE_FLAG`) actually removes each
    eligible worktree dir + prunes, serialized through `shared_tree_lock` (this mutates the SHARED
    git-common-dir worktree admin state, visible from every worktree -- the cross-worktree lock,
    not the per-tree one). Never raises. Fully injectable for tests -- NEVER call this in enforce
    mode against the real repo's worktrees outside a throwaway fixture."""
    if worktrees is None:
        worktrees = scan_worktrees()
    if main_path is None:
        main_path = str(PROJECT_DIR)
    if branch_states is None:
        _now = now if now is not None else time.time()
        branch_states = {b["name"]: classify_branch(b, _now) for b in scan_fork_branches()}
    if enforce is None:
        enforce = worktree_reap_enabled()
    dirty_fn = dirty_fn or _worktree_dirty
    salvage_tag_fn = salvage_tag_fn or _salvage_tag_for
    remover = remover or reap_worktree_dir
    reachable_fn = reachable_fn or _head_reachable_from_main
    detached_tag_fn = detached_tag_fn or _detached_salvage_tag_for
    # INJECTABLE LIKE EVERY OTHER PROBE HERE, and defaulted to the executor's own answer rather
    # than a copy of it -- `seat_executor` owns `WORKTREE` and `PID_FILE`, so it owns the question.
    # An unimportable executor reads as "no live writer": this reaper must not stop working because
    # a module it does not depend on is broken, and the DIRTY check still stands behind it.
    live_writer_fn = live_writer_fn or _live_writer_default
    homes = declared_daemon_homes()

    eligible, kept = [], []
    for wt in worktrees:
        branch = wt.get("branch")
        bstate = branch_states.get(branch) if branch else None
        tag = salvage_tag_fn(branch) if branch else None
        dirty = dirty_fn(wt["path"])
        dstate = _determine_detached(wt, reachable_fn, detached_tag_fn)
        # A LIVE WRITER'S WORKTREE IS NOT ABANDONED (2026-08-31). Decided HERE and not inside
        # `classify_worktree_reap`, which is documented as pure and I/O-free and is the
        # mutation-testable core -- a liveness probe belongs on this side of that line.
        #
        # THE REAPER WAS ARMED AND HAD NOT FIRED ONLY BY LUCK. It refuses a DIRTY worktree, and the
        # seat executor is dirty for most of a turn -- but there is a window at the start of every
        # turn, after `ensure_worktree` resets and cleans and before the first edit, when its tree
        # is clean and detached at `origin/main`: MERGED, and by this classifier's own rules
        # eligible. `git worktree remove` on a live writer is the whole turn gone, and the writer
        # was armed this afternoon. Its sibling `fork_salvage` had already collided with it four
        # minutes into the first run, which is what prompted looking here at all.
        if live_writer_fn(wt["path"]):
            result = {"eligible": False,
                      "reason": "a live writer holds this worktree -- never reaped while its "
                                "process is alive; it is in use, not abandoned"}
        else:
            result = classify_worktree_reap(wt, main_path, bstate, dirty=dirty, salvage_tag=tag,
                                            detached_head_state=dstate, declared_homes=homes)
        entry = {"path": wt["path"], "branch": branch, **result}
        (eligible if result["eligible"] else kept).append(entry)

    reaped: list[dict] = []
    if enforce and eligible:
        try:
            from background.tree_lock import shared_tree_lock
            with shared_tree_lock():
                for e in eligible:
                    reaped.append(remover(e["path"]))
        except Exception as e:
            reaped = [{"path": e["path"], "removed": False, "detail": f"lock/import error: {e}"}
                      for e in eligible]

    # THE STRANDED SET GETS ITS ONE PRESERVING STEP, under the same arming flag as the reap it
    # leads to. Run AFTER the classification so `advance_stranded` acts on this pass's verdicts,
    # and deliberately WITHOUT re-reaping in the same pass -- see that function's docstring.
    advanced: list[dict] = []
    if enforce:
        try:
            advanced = (advance or advance_stranded)(kept)
        except Exception as e:  # noqa: BLE001 - never let the advance take the report down
            advanced = [{"path": "*", "step": "error", "ok": False,
                         "detail": f"{type(e).__name__}: {e}"}]

    failed = [r for r in reaped if not r["removed"]]
    _stranded_now = [k for k in kept if refusal_is_stranded(k.get("reason", ""))]
    # Eligible-but-not-yet-enforced is routine housekeeping, not a problem -- only a genuine
    # failure to remove something the classifier already proved safe is worth alarming on.
    # A standing stranded population is a REAL alarm: the control is running, reporting, and
    # unable to do its job. Previously only an enforce-mode removal failure alarmed, so the
    # unsatisfiable-conjunction case was silent by construction.
    alarm = bool(enforce and failed) or len(_stranded_now) >= STRANDED_WORKTREE_ALARM_AT
    if enforce:
        removed_n = sum(1 for r in reaped if r["removed"])
        if failed:
            status = "WORKTREE_REAP_FAILED"
            detail = (f"removed {removed_n}/{len(eligible)} eligible worktree dir(s); "
                      f"{len(failed)} FAILED to remove: "
                      + ", ".join(f"{f['path']} ({f['detail']})" for f in failed[:4]))
        elif removed_n:
            status = "WORKTREE_REAPED"
            detail = f"removed {removed_n} eligible worktree dir(s), 0 failures"
        elif len(_stranded_now) >= STRANDED_WORKTREE_ALARM_AT:
            # THE SAME FAIL-SILENT DEFECT, ON THE OTHER BRANCH (found 2026-09-01, by running the
            # reaper for the first time). The 2026-08-03 repair below made WORKTREE_REAP_CLEAN
            # unreachable while a stranded population exists -- and only in REPORT-FIRST mode. In
            # enforce mode "removed nothing" still printed CLEAN, so the first live enforce pass
            # reported `WORKTREE_REAP_CLEAN` over six stranded worktrees, with `alarm` True beside
            # it. A status and an alarm that disagree is worse than either being wrong.
            #
            # The fix took the branch it was looking at as its subject rather than the property:
            # "reaped nothing while unable to act" means the same thing in both modes.
            status = "WORKTREE_REAP_STRANDED"
            detail = (f"removed 0; {len(_stranded_now)} STRANDED worktree dir(s) the reaper cannot "
                      f"act on ({_why_stranded(_stranded_now)}); "
                      f"{len(kept) - len(_stranded_now)} legitimately kept (locked/live/main).")
        else:
            status = "WORKTREE_REAP_CLEAN"
            detail = (f"no reapable worktree dirs; {len(kept)} kept (locked/live/dirty/main), "
                      f"{len(_stranded_now)} stranded (under the alarm threshold)")
    elif eligible:
        status = "WORKTREE_REAP_ELIGIBLE"
        shown = ", ".join(Path(e["path"]).name for e in eligible[:6]) + (" …" if len(eligible) > 6 else "")
        detail = f"{len(eligible)} worktree dir(s) reapable [REPORT-FIRST, none removed]: {shown}"
    else:
        # FAIL-SILENT FIX (H24, 2026-08-03, director console: "your worktree reaper can't reap
        # itself, which is why those strays never clear"). `eligible == 0` was reported as CLEAN
        # unconditionally -- indistinguishable from "nothing to do" -- so a population the control
        # is STRUCTURALLY unable to touch read as health for 16 days while 26 worktrees piled up.
        # An unavailable check is a FAILED check (R15 fail-silent): say which it is.
        if len(_stranded_now) >= STRANDED_WORKTREE_ALARM_AT:
            status = "WORKTREE_REAP_STRANDED"
            detail = (
                f"0 reapable but {len(_stranded_now)} STRANDED worktree dir(s) the reaper cannot "
                f"act on ({_why_stranded(_stranded_now)}); "
                + f"{len(kept) - len(_stranded_now)} legitimately kept (locked/live/main). "
                "Eligibility requires MERGED-and-CLEAN, but a fork here dies DIRTY, so the "
                "conjunction is unsatisfiable for the real population -- salvage the content to a "
                "ref first, then the worktree is clean and removable with nothing lost. ARM the "
                "reap flag and the cycle now walks that route itself (advance_stranded)."
            )
        else:
            status = "WORKTREE_REAP_CLEAN"
            detail = (f"no reapable worktree dirs; {len(kept)} kept "
                      f"({len(_stranded_now)} stranded, under the alarm threshold)")

    if advanced:
        moved = sum(1 for a in advanced if a["ok"])
        detail += (f" ADVANCED {moved}/{len(advanced)} stranded worktree(s) one preserving step "
                   f"(salvage before reap; the reap itself is the next pass).")
    return {"status": status, "alarm": alarm, "detail": detail, "eligible": eligible, "kept": kept,
            "reaped": reaped, "advanced": advanced, "enforce": enforce}


# ── SINGLE-WORKTREE SANCTIONED REAP (H24 gap-close): the guarded replacement for raw
# `git worktree remove --force` ────────────────────────────────────────────────────────────────
# Real incident this session: an orchestrator ran raw `--force` removes on three LIVE build-fork
# worktrees using false-death inference (no `ps` match / frozen output-file mtime / 0 commits ahead
# -- every one of those is a FALSE NEGATIVE for a live fork; ps/mtime/commit-count say nothing about
# whether a fork is still working). ~24 min of fully-green, uncommitted work lost per fork, twice.
# `evaluate_worktree_reap` above is already safe (no --force, refuses locked/dirty/main/bare/live),
# but it is a BATCH scanner -- there was no sanctioned way to reap ONE worktree by path, so the
# orchestrator reached for the raw, unguarded command. This closes that gap: the ONLY blessed
# single-path entrypoint, reusing `classify_worktree_reap` for eligibility (no duplicated logic) and
# `reap_worktree_dir` for the actual remove (still no --force -- git's own dirty/locked refusal
# stays a second, independent safety net). The ONLY authoritative done-signal for a fork is its own
# completion notification -- ps/mtime/commit-count are not it, so an unmerged branch is a LIVE fork
# by construction and is NEVER reaped here, regardless of how "dead" it looks from the outside.
def reap_one_worktree(path: str, *, worktrees: list[dict] | None = None,
                      branch_states: dict | None = None, main_path: str | None = None,
                      now: float | None = None, dirty_fn=None, salvage_tag_fn=None,
                      remover=None, reachable_fn=None, detached_tag_fn=None,
                      live_writer_fn=None) -> dict:
    """Reap ONE worktree by path -- the ONLY sanctioned way to do this (never call raw
    `git worktree remove --force` directly). Runs the EXISTING `classify_worktree_reap` for `path`
    and refuses LOUDLY (never calls the remover, never raises) unless it says eligible: not a
    registered worktree, locked, live/undecided branch (IN_FLIGHT or unsalvaged ORPHAN -- the real
    fork-killing case, since a live fork's worktree is never `locked` by the harness), dirty, main,
    or bare. Eligible removal is serialized through `shared_tree_lock` (same cross-worktree lock as
    `evaluate_worktree_reap`) and delegates to `reap_worktree_dir` (no --force). Fully injectable,
    same DI style as `evaluate_worktree_reap`. Returns {"path", "removed": bool, "refused": bool,
    "loud": bool, "reason"/"detail"}. Never raises."""
    if worktrees is None:
        worktrees = scan_worktrees()
    if main_path is None:
        main_path = str(PROJECT_DIR)
    if branch_states is None:
        _now = now if now is not None else time.time()
        branch_states = {b["name"]: classify_branch(b, _now) for b in scan_fork_branches()}
    dirty_fn = dirty_fn or _worktree_dirty
    salvage_tag_fn = salvage_tag_fn or _salvage_tag_for
    remover = remover or reap_worktree_dir
    reachable_fn = reachable_fn or _head_reachable_from_main
    detached_tag_fn = detached_tag_fn or _detached_salvage_tag_for
    # INJECTABLE LIKE EVERY OTHER PROBE HERE, and defaulted to the executor's own answer rather
    # than a copy of it -- `seat_executor` owns `WORKTREE` and `PID_FILE`, so it owns the question.
    # An unimportable executor reads as "no live writer": this reaper must not stop working because
    # a module it does not depend on is broken, and the DIRTY check still stands behind it.
    live_writer_fn = live_writer_fn or _live_writer_default

    wt = next((w for w in worktrees if w["path"] == path), None)
    if wt is None:
        return {"path": path, "removed": False, "refused": True, "loud": True,
                "reason": "not a registered worktree — refused"}

    branch = wt.get("branch")
    bstate = branch_states.get(branch) if branch else None
    tag = salvage_tag_fn(branch) if branch else None
    dirty = dirty_fn(path)
    dstate = _determine_detached(wt, reachable_fn, detached_tag_fn)
    # BOTH REAP DOORS ASK THE SAME QUESTION. `test_both_reap_doors_determine_a_detached_worktree
    # _the_same_way` exists because a rule enforced at one door and not the other is a rule with a
    # way round it, and a live writer's worktree is exactly that kind of subject: this door is the
    # one an operator calls by hand.
    if live_writer_fn(path):
        result = {"eligible": False,
                  "reason": "a live writer holds this worktree -- never reaped while its process "
                            "is alive; it is in use, not abandoned"}
    else:
        result = classify_worktree_reap(wt, main_path, bstate, dirty=dirty, salvage_tag=tag,
                                        detached_head_state=dstate,
                                        declared_homes=declared_daemon_homes())
    if not result["eligible"]:
        return {"path": path, "removed": False, "refused": True, "loud": True, "reason": result["reason"]}

    try:
        from background.tree_lock import shared_tree_lock
        with shared_tree_lock():
            removed = remover(path)
    except Exception as e:
        return {"path": path, "removed": False, "refused": False, "loud": True,
                "reason": f"lock/import error: {e}"}
    ok = bool(removed.get("removed"))
    return {"path": path, "removed": ok, "refused": False, "loud": not ok,
            "reason": result["reason"], "detail": removed.get("detail")}


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/fork_reconciler.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("fork_reconciler")
    import json
    import sys
    r = evaluate_fork_lifecycle()
    print(json.dumps({k: (v if k != "reaped" else v) for k, v in r.items()}, indent=2))
    sys.exit(1 if r["alarm"] else 0)
