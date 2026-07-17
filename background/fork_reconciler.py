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
    One name per line; blank / '#' lines ignored. Empty set if the file is absent/unreadable."""
    out: set[str] = set()
    try:
        for ln in (path or HELD_FILE).read_text().splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#"):
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
    return {"branch": branch, "tag": tag, "reaped": True, "detail": f"salvaged @ {tip[:9]} then reaped"}


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
    """Every registered worktree as {path, branch, detached}. Parses `git worktree list --porcelain`."""
    out = _git("worktree", "list", "--porcelain")
    wts: list[dict] = []
    cur: dict | None = None
    for line in out.splitlines():
        if line.startswith("worktree "):
            if cur:
                wts.append(cur)
            cur = {"path": line[len("worktree "):].strip(), "branch": None, "detached": False}
        elif cur is not None and line.startswith("branch "):
            ref = line[len("branch "):].strip()
            cur["branch"] = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
        elif cur is not None and line.strip() == "detached":
            cur["detached"] = True
    if cur:
        wts.append(cur)
    return wts


def classify_worktree(wt: dict, main_path: str, branch_states: dict) -> str:
    """Pure: BELONGS if it is the main worktree, or a fork worktree whose branch is IN_FLIGHT (a
    live fork). Otherwise UNDECLARED (accretion): detached, no/unknown branch, or a branch that is
    an orphan or already merged (the worktree should have been pruned when the fork came home)."""
    if wt["path"] == main_path:
        return "BELONGS"
    if wt.get("branch") and branch_states.get(wt["branch"]) == "IN_FLIGHT":
        return "BELONGS"
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

    undeclared, belongs = [], []
    for wt in worktrees:
        if classify_worktree(wt, main_path, branch_states) == "BELONGS":
            belongs.append(wt["path"])
        else:
            bstate = ("detached" if wt.get("detached") else
                      (branch_states.get(wt["branch"], "no-branch") if wt.get("branch") else "no-branch"))
            undeclared.append({"path": wt["path"], "branch": wt.get("branch"), "branch_state": bstate})

    alarm = bool(undeclared)
    if not undeclared:
        return {"status": "WORKTREE_CLEAN", "alarm": False,
                "detail": f"{len(belongs)} declared worktree(s), none undeclared", "undeclared": []}
    shown = ", ".join(f"{u['path'].split('/')[-1]}({u['branch_state']})" for u in undeclared[:6])
    return {"status": "WORKTREE_UNDECLARED", "alarm": True,
            "detail": f"{len(undeclared)} UNDECLARED worktree(s) (accretion, report-only): {shown}",
            "undeclared": undeclared}


if __name__ == "__main__":
    import json
    import sys
    r = evaluate_fork_lifecycle()
    print(json.dumps({k: (v if k != "reaped" else v) for k, v in r.items()}, indent=2))
    sys.exit(1 if r["alarm"] else 0)
