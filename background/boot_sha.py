"""Booted-SHA stamping (OPS1 sub-step 5 — deployment-by-construction, G-D1/G-D3).

docs/design/OPERATIONAL_LAYER_DESIGN.md §2.2. Each systemd daemon stamps the git HEAD it BOOTED
from (as its unit's ExecStartPre); the reconciler compares the stamp against current HEAD, so a
daemon running STALE code is flagged by construction. This GENERALISES the prior stale-detection
(health_check.stale_daemon_sessions was mtime-of-the-daemon's-OWN-top-level-script only): a boot
SHA older than HEAD means stale no matter WHICH file changed — including an imported module the
daemon depends on, the gap the mtime check silently missed.

The stamp is written by the systemd unit (declared in generate_units.py, committed IaC) — NO
daemon source is touched. The boot record is runtime state (gitignored, like a pidfile); the
MECHANISM (stamper + unit ExecStartPre + reconcile) is committed.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
BOOT_DIR = _REPO / "docs" / "observability" / ".daemon_boot"


def current_head() -> str | None:
    """The repo's current HEAD SHA, or None if git is unavailable (never raises)."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, text=True, timeout=5
        ).strip() or None
    except Exception:
        return None


def dirty_blobs() -> dict[str, str] | None:
    """`{path: content hash}` for every tracked file that differs from HEAD right now, or None if
    git cannot answer.

    THE DEFECT THIS EXISTS FOR, measured 2026-09-04. A daemon boots from a WORKING TREE and a stamp
    could only record a COMMIT, so every uncommitted edit present at boot was reported for ever as
    code the daemon did not have -- when the daemon had loaded exactly those bytes off the disk. On
    a tree several lanes keep ~185 files dirty in, that is not an edge case: all thirteen staleness
    causes across four daemons were of this kind, none was a commit any daemon had missed, and a
    restart could never clear one of them. G-D2 restarted those four every ten minutes for eight
    hours on it.

    So the stamp records what the daemon actually loaded: HEAD, plus the content of everything that
    differed from HEAD at that instant.
    """
    sha = current_head()
    if not sha:
        return None
    paths = _diff_names(sha)
    return None if paths is None else _content_map(sorted(paths))


#: A path in the diff that does not exist on disk. It needs a VALUE, not a failure: `git
#: hash-object` cannot hash a deleted file, and the first draft let that turn the whole map into
#: None -- so on this tree, which always carries deletions, the stamp recorded nothing and the
#: comparison fell back to the over-report it was written to remove. Measured: the fix appeared to
#: change no daemon's count at all, which is how it was caught.
ABSENT = "absent"


def _diff_names(rev: str) -> list[str] | None:
    try:
        r = subprocess.run(["git", "diff", "--name-only", rev, "--"],
                           cwd=_REPO, capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return [line.strip() for line in (r.stdout or "").splitlines() if line.strip()]


def _content_map(paths: list[str]) -> dict[str, str] | None:
    """`{path: content hash}`, with deleted paths mapped to ABSENT rather than dropped."""
    present = [p for p in paths if (_REPO / p).is_file()]
    digests: list[str] = []
    if present:
        try:
            # One batched call, not one fork per path: this runs in ExecStartPre and several
            # hundred forks is a boot delay a reader would notice.
            r = subprocess.run(["git", "hash-object", "--stdin-paths"], cwd=_REPO,
                               input="\n".join(present) + "\n", capture_output=True,
                               text=True, timeout=60)
        except Exception:
            return None
        if r.returncode != 0:
            return None
        digests = [d for d in (r.stdout or "").splitlines() if d.strip()]
        if len(digests) != len(present):
            return None  # cannot pair them: an unpaired map is worse than no map
    out = dict(zip(present, digests))
    for p in paths:
        out.setdefault(p, ABSENT)
    return out


def stamp(session: str) -> None:
    """Record the tree this daemon booted from. Runs as the unit's ExecStartPre (prefixed `-`
    there, so a stamp failure never blocks the daemon). Never raises."""
    sha = current_head()
    blobs = dirty_blobs()
    try:
        BOOT_DIR.mkdir(parents=True, exist_ok=True)
        record = {"session": session, "sha": sha, "ts": time.time()}
        if blobs is not None:
            # ABSENT, never empty-on-failure: `{}` means "nothing was dirty" and None means "could
            # not tell", and a reader that cannot distinguish them under-reports staleness.
            record["dirty_blobs"] = blobs
        (BOOT_DIR / f"{session}.json").write_text(json.dumps(record))
    except Exception:
        pass


def read_boot_sha(session: str) -> str | None:
    """The SHA a daemon booted from (last stamp), or None if never stamped/unreadable."""
    try:
        return json.loads((BOOT_DIR / f"{session}.json").read_text()).get("sha")
    except Exception:
        return None


def read_boot_blobs(session: str) -> dict[str, str] | None:
    """What was dirty when this daemon booted, or None if the stamp predates the field or could not
    say. None must degrade to today's OVER-reporting, never to under-reporting: an unknown boot
    tree makes every difference count, which costs a needless restart and never a missed one."""
    try:
        value = json.loads((BOOT_DIR / f"{session}.json").read_text()).get("dirty_blobs")
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def changed_paths_since(sha: str, boot_blobs: dict[str, str] | None = None) -> set[str] | None:
    """Repo-relative paths that differ between `sha` and the CURRENT WORKING TREE, or None if
    the SHA is unknown to git / git is unavailable.

    Working tree, not HEAD: a daemon loads files off the disk it booted from, so an UNCOMMITTED
    edit to a module it imports is genuinely code the daemon does not have — that is exactly the
    caller/callee split (`sim_runner.py` argv) that ran for ten hours on 2026-08-09.

    …AND THAT ARGUMENT HAS A SECOND HALF THAT WAS MISSING UNTIL 2026-09-04. It is true of an edit
    made AFTER the daemon booted. An edit already on the disk when it booted was LOADED, so the
    daemon has it — and a commit SHA cannot say which was which. Measured: all thirteen staleness
    causes across four daemons were uncommitted edits present at boot, not one was a commit any
    daemon had missed, and G-D2 restarted those four every ten minutes for eight hours trying to
    clear a condition a restart cannot clear. Pass `boot_blobs` (from `read_boot_blobs`) and the
    comparison becomes content against content, which is the question that was always meant.

    None means UNRESOLVED, which callers must treat as a failed check (R15 fail-silent), never as
    an empty diff — an unanswerable question is not a green answer.
    """
    if not sha:
        return None
    try:
        r = subprocess.run(["git", "diff", "--name-only", sha, "--"],
                           cwd=_REPO, capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    candidates = {line.strip() for line in (r.stdout or "").splitlines() if line.strip()}
    if not boot_blobs:
        # None = the boot tree is unknown; {} = nothing was dirty at boot. Either way every
        # candidate is a real difference, so the set stands: this degrades to OVER-reporting, which
        # costs a needless restart, and never to under-reporting, which costs a stale daemon.
        #
        # AND THIS IS AN OPTIMISATION, NOT A BRANCH — established, not assumed, because a mutation
        # that folded None into {} SURVIVED the suite. Measured on the live tree: 427 candidates,
        # and `None` and `{}` both return all 427, because an empty map makes `boot_blobs.get(p)`
        # None for every path and every real hash differs from None. Deleting this line changes no
        # answer; it only spends 427 hash-object entries to reach the same set. Said plainly rather
        # than left to a reader, since the flattering reading of a surviving mutation is that a
        # test is missing.
        return candidates

    now = _content_map(sorted(candidates))
    if now is None:
        return candidates  # cannot compare content -> keep the honest over-report
    return {p for p in candidates if now.get(p) != boot_blobs.get(p)}

