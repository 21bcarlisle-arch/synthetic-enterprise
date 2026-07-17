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
                            enforce: bool | None = None, reaper=salvage_and_reap) -> dict:
    """REPORT the fork-lifecycle state. In report-first mode (default) NOTHING is reaped -- orphans
    are detected + alarmed only. In enforce mode (flag armed) each orphan is salvage-then-reaped.
    Never raises. Injectable (branches/now/enforce/reaper) for deterministic tests."""
    if branches is None:
        branches = scan_fork_branches()
    if now is None:
        now = time.time()
    if enforce is None:
        enforce = reap_enabled()

    orphans, in_flight, merged = [], [], []
    for b in branches:
        state = classify_branch(b, now)
        if state == "ORPHAN":
            orphans.append(b["name"])
        elif state == "IN_FLIGHT":
            in_flight.append(b["name"])
        elif state == "MERGED":
            merged.append(b["name"])

    reaped: list[dict] = []
    if enforce and orphans:
        for name in orphans:
            reaped.append(reaper(name))

    alarm = bool(orphans)
    if not orphans:
        status = "FORK_CLEAN"
        detail = f"no orphans; {len(in_flight)} in-flight, {len(merged)} merged (cleanup-eligible)"
    else:
        mode = "ENFORCE (salvage+reap)" if enforce else "REPORT-FIRST (detect only, no reap)"
        shown = ", ".join(orphans[:6]) + (" …" if len(orphans) > 6 else "")
        detail = (f"{len(orphans)} orphaned fork branch(es) never merged home [{mode}]: {shown}"
                  + (f"; reaped {sum(1 for r in reaped if r['reaped'])}/{len(reaped)}" if enforce else ""))
        status = "FORK_ORPHANS"
    return {"status": status, "alarm": alarm, "detail": detail,
            "orphans": orphans, "in_flight": in_flight, "merged_eligible": merged,
            "reaped": reaped, "enforce": enforce}


if __name__ == "__main__":
    import json
    import sys
    r = evaluate_fork_lifecycle()
    print(json.dumps({k: (v if k != "reaped" else v) for k, v in r.items()}, indent=2))
    sys.exit(1 if r["alarm"] else 0)
