"""Surgical landing: commit exactly-named paths with the gate run against the tree the
commit WOULD create (atom OPS4, DIRECTOR_RULING_HOOK_BYPASS_IS_A_WALL_2026-08-09).

WHY THIS EXISTS -- A MISSING TOOL, NOT A DISCIPLINE FAILURE
-----------------------------------------------------------
Landing an orphan lane's residue on 2026-08-09, the acting seat faced two sins and no legal
move: `git merge` would have swept 35 paths of OTHER lanes' staged work out of the shared
index into an unreviewed commit, and a `git commit-tree` construction bypassed the pre-commit
hook. It chose the second, disclosed it, and asked for the rule. The ruling: **bypass is a
wall, never a judgment call** -- and the class closes by MECHANISM, because a rule that leaves
no legal move evaporates (MAKE_IT_STICK: every rule that decayed here was an exhortation;
every rule that held was a mechanism).

This is that mechanism. With it, "bypass" stops being a concept anyone has to weigh: the
check always runs, even when the shared index is full of other lanes' work.

THE SECOND DEFECT IT CLOSES, IN THE SAME MOVE
---------------------------------------------
`tools/pre_commit_test_gate.py` SELECTS tests from the index (`git diff --cached`) and RUNS
them in the WORKING TREE. Those scopes are equal except in exactly one case -- a partial
commit -- which is the routine case on this shared tree, because CLAUDE.md's own recommended
discipline is to stage a precise pathspec. On 2026-08-09 that produced HEAD asserting an
epistemic wall that HEAD's own code violated: the working tree was green, the commit was not,
and the publish gate wedged for ~112 minutes
(WORKER_FINDING_THE_PRECOMMIT_GATE_VALIDATES_THE_TREE_NOT_THE_COMMIT_2026-08-09.md).

So the subject of the gate here is neither the index nor the working tree. It is a CLEAN
EXTRACT OF THE RESULTING TREE: the tree `HEAD` would become if exactly the named paths were
committed. Selection and execution finally share one scope.

HOW
---
1.  A THROWAWAY INDEX (`GIT_INDEX_FILE`), seeded `read-tree HEAD`, then `git add -A` for the
    named paths only. The caller's real index is never opened. A path may instead be given its
    bytes directly (`--content REPOPATH=SRCFILE`, or `content={path: bytes|None}` in-process),
    in which case the working tree copy is never read -- see THE CONTENT SOURCE below.
2.  `git write-tree` on it -> the resulting tree sha. This is the thing being judged.
3.  A STANDALONE extract of that tree in a tmpdir: `git archive | tar -x`, then `git init` +
    an `objects/info/alternates` line lending the real object store READ-ONLY, `.git/HEAD` set
    to the PARENT sha, `read-tree` of the parent, and `git add -A` of the named paths. The
    result is a repo where `git diff --cached` is exactly this commit and the working tree is
    exactly the resulting tree. (Technique ported, not invented: `process_run_complete.py::
    _head_checkout` proved it. `git worktree add` is deliberately NOT used -- it registers
    state in the real repo that survives a SIGKILL.)
4.  THE REPO'S OWN `tools/git-hooks/pre-commit`, run in that extract with `GIT_*` scrubbed.
    Not a re-implementation and not a subset: the same test gate, level-promotion gate,
    site-lane gate, coherence gate, archive-question gate, consolidation rhythm and size
    ratchet a `git commit` would face -- against the right tree this time.
5.  On green, under `tree_lock`, a compare-and-swap: refuse if HEAD moved since step 2,
    else `commit-tree` + `update-ref HEAD <new> <parent>`, then refresh the real index for
    EXACTLY the landed paths (the same post-state `git commit -- <paths>` leaves; every other
    entry, including another lane's staged work, is byte-identical).
6.  A RECEIPT in the commit message naming the parent, the tree, the path list and the gate
    command -- checkable afterwards with `--verify`, so a commit CLAIMING a gate run can be
    falsified rather than believed.

THE CONTENT SOURCE (2026-08-19, R3 redesign,
WORKER_FINDING_THREE_CONSECUTIVE_PASSES_RECORDED_A_LANDING_THAT_IS_IN_NO_COMMIT)
--------------------------------------------------------------------------------
Step 1 read the WORKING TREE, so a file carrying two lanes could only be landed by swapping the
SHARED copy to HEAD-plus-my-hunks and restoring it under a `trap`. That procedure has two exits
that are BYTE-IDENTICAL on disk -- committed-then-restored, and died-then-restored -- so a
landing that never happened leaves a tree indistinguishable from one that did. Three
consecutive passes read that tree, believed their predecessor's record, and each wrote a new
record asserting a landing that is in no commit; the detector worked every time and was only
ever pointed backwards. That is R3 (a third false completion claim on one component means
REDESIGN, not a fourth patch), and this is the redesign.

Pass the bytes instead. There is then no swap, no trap and no restore, so the only evidence of
a landing is the commit -- which is the property the whole failure turned on. It also closes
the retry hazard: `land()` re-reads its content source on every `BaseMoved` retry, and a
mapping does not change under it the way a shared worktree does. `None` commits a deletion
without removing the file from disk. Overrides must be named in the pathspec, the parent's file
mode is preserved, and the receipt names the content-sourced paths so a later reader can tell
"disk differs on purpose" from "the landing failed". R15-proven in
`tests/tools/test_surgical_land.py` -- ignoring the mapping reds six tests, hardcoding the mode
reds one, and printing the receipt line unconditionally reds its null control.

FAIL-CLOSED, EVERYWHERE (R15: an unavailable check is a FAILED check)
---------------------------------------------------------------------
No commit is created if: the hook script is missing or unreadable; the extract cannot be
built or cannot be made a real repo; tmp has less free space than the extract needs; the hook
exits non-zero; HEAD moved under us; or the resulting tree is identical to HEAD's. Every one
of those is a REFUSAL, never a silent pass -- the failure direction that matters, because the
whole point is that this tool is the legal move and a legal move that quietly skips its check
is worse than the bypass it replaces.

THE REFUSAL IN STEP 5 NEEDED A MOVE THAT TERMINATES (2026-08-13,
WORKER_FINDING_THE_LANDING_GATE_CANNOT_WIN_THE_RACE_AGAINST_HEAD)
------------------------------------------------------------------
The compare-and-swap is correct and is not weakened here. But on this box it was also
UNSATISFIABLE for expensive work: the gate ran ~9m24s while HEAD moved every 3.5-10 minutes
(publisher and daemon commits -- `chore(provenance)`, `Auto-process run complete`,
`chore(liveness)`), so three consecutive attempts were refused, NONE of them for a red test.
A rule that leaves no legal move evaporates, and the observed consequence was the finished
work sitting uncommitted in the shared tree -- the landing control MANUFACTURING the
orphaned-work class one tick at a time.

So `land()` now retries, and the retry is honest: each attempt re-reads HEAD, rebuilds the
resulting tree against the NEW parent (so the mover's commits are kept, never overwritten)
and RE-RUNS THE FULL GATE. No verdict is ever carried across a HEAD move; the wall is
untouched. Only `BaseMoved` is retried -- a GATE RED is terminal on the first attempt, because
retrying a red tree until a flaky test flips green is exactly the laundering this tool exists
to prevent. Exhausting the attempts is a REFUSAL that commits nothing, never a bypass.

R15 mutation-proven both ways in `tests/tools/test_surgical_land.py`.
Design note: `docs/design/SURGICAL_LANDING.md`.
"""
from __future__ import annotations

import argparse
import atexit
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Mapping
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Run as a SCRIPT (`python3 tools/surgical_land.py ...` -- the form the usage string shows and the
# only form a seat actually types), sys.path[0] is tools/, not the repo root, so `background` is
# unimportable. Every test here calls land() IN-PROCESS from pytest, whose rootdir is the repo, so
# the whole suite was green while the entry point could not reach the one module it defers to.
# That is the "guard unreachable from its only caller" shape, and it failed in the worst place:
# _write_lock is the LAST step, so the crash landed after the full gate had already run, leaving
# the legal move unavailable exactly when someone reaches for it -- which is the pressure toward
# bypass this tool exists to remove. Bypass is a wall; the wall needs the door to open.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from background import child_diagnostics, staging_root_resurrection_watch  # noqa: E402
from background.tree_lock import (  # noqa: E402  (needs the path insert above)
    TreeLockTimeout,
    tree_lock,
)

# The gate is the repo's OWN hook, named in ONE place. Running a hand-picked subset here would
# recreate the accretion the ruling forbids: the tool must face what `git commit` faces.
HOOK_REL = "tools/git-hooks/pre-commit"

# The extract is a full tree copy. Below this, refuse -- a gate that cannot be materialised has
# not run (the publish gate's own floor, same reasoning).
MIN_FREE_MB = 500

# WORKER_FINDING_THE_ONLY_LEGAL_LANDING_MOVE_LEAKS_150MB_A_KILL_2026-08-14: every checkout is
# marked with its owning PID the instant it exists, so a sweep can tell a live extract (leave it)
# from an abandoned one (a kill that skipped `finally:`, or a dir with no marker at all -- every
# extract before this fix). The marker lives INSIDE the checkout, not beside it, so `rmtree`
# removes both in one call and there is nothing to leak twice.
OWNER_MARKER = ".owner-pid"

# WHERE AN EXTRACT LIVES -- ON DISK, NOT IN RAM (2026-08-14). This MIRRORS
# `process_run_complete.HEAD_CHECKOUT_ROOT` deliberately and for the identical reason: on this box
# `tempfile.gettempdir()` is `/tmp`, a tmpfs backed by the same 15.9G of RAM the suites need, while
# `/var/tmp` is ext4 with ~886G free. The publish gate was moved off the tmpfs on 2026-08-11; this
# tool -- the only sanctioned way to LAND that gate's own repairs -- was left behind, which is the
# sibling-half shape (`feedback_audit_sibling_half_for_hardened_class`).
#
# Its cost lands on the RECOVERY path, which is why it is worth a constant rather than a habit: a
# full tmpfs refuses EVERY commit on a dirty tree, including the commit that unwedges publishing,
# with a message that correctly says DISK and correctly says nothing failed -- observed 2026-08-14
# ("REFUSED on DISK: 352MB free where the extract needs ~500MB") at exactly the moment a tick was
# hunting the wedge's red test. Same env-var shape as the gate's, so the two agree by construction
# and can be pointed elsewhere together.
EXTRACT_ROOT = Path(os.environ.get("SE_LAND_EXTRACT_ROOT", "/var/tmp"))

# Untracked DATA the suite reads (a ~291MB Elexon/NESO cache, the npm tree). `git archive` cannot
# contain them, and a checkout without them fails ~85 tests for reasons that have nothing to do
# with whether the commit is sound. Symlinked, never copied; a named list, never "everything
# gitignored" (which would sweep .venv and reintroduce working-tree coupling).
UNTRACKED_DATA_OVERLAY = ("sim/cache", "node_modules")

RECEIPT_HEADER = "[surgical-land receipt]"
_NULL_SHA = "0" * 40


class LandingRefused(Exception):
    """Raised for every refusal. Carrying one exception type keeps the fail-CLOSED contract
    provable: `land()` either returns a commit sha or raises, and never returns None."""


class IndexNotRefreshed(LandingRefused):
    """THE COMMIT LANDED. Only the shared index was left disagreeing with it.

    This is a subclass rather than a plain `LandingRefused` because the two mean opposite things
    to a caller and the word REFUSED was being used for both. Observed 2026-09-01: a landing
    printed `REFUSED: the commit LANDED but refreshing the index for its paths failed` -- honest
    and self-contradictory in one sentence -- while its commit sat on HEAD. A daemon keying on the
    exception type concludes the work is unlanded, and either re-lands it (a duplicate commit of
    a tree that is already the parent) or reports failure for work that shipped.

    The window is not narrow. The lock is held by another lane's `git commit`, and a commit here
    is ten to fifteen minutes of gate, so this failure is available for a quarter of an hour every
    time any lane commits. `_refresh_with_retry` now outlasts the holder, and this type exists so
    that if it ever still fires, the ONE thing a caller must not do -- conclude the landing failed
    -- is impossible to do by accident.

    `sha` carries the landed commit, so a caller that catches this can record the truth.
    """

    def __init__(self, message: str, sha: str = ""):
        super().__init__(message)
        self.sha = sha


class BaseMoved(LandingRefused):
    """The ONE refusal that is retryable: HEAD moved under the gate, so the verdict describes a
    tree that is no longer the one this commit would create.

    A SUBCLASS, not a flag and not a string match on the message. The retry loop must be able to
    ask "was this the race, or was it the tree?" and get an answer that cannot drift when someone
    rewords the refusal -- and every existing caller catching `LandingRefused` still catches it.
    Nothing else inherits from this: a red gate, a missing hook, a full disk and a no-op pathspec
    are all terminal, because retrying any of them is retrying until the world agrees with you."""

    def __init__(self, message: str, parent: str, observed: str):
        super().__init__(message)
        self.parent = parent
        self.observed = observed


#: Default attempts for a landing. NOT 1: a terminating move that must be opted into with a flag
#: is prose, not mechanism (MAKE_IT_STICK), and the finding this closes was three losses in a row
#: at the DEFAULT invocation. The cost of the extra attempts is CPU, paid only when the race is
#: actually lost; the cost of not having them was measured in orphaned work.
DEFAULT_ATTEMPTS = 3


def _git(root: Path, *args: str, env: dict | None = None,
         stdin: bytes | None = None, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                          input=stdin, env=env, timeout=timeout)


def _git_text(root: Path, *args: str, env: dict | None = None) -> str:
    r = _git(root, *args, env=env)
    if r.returncode != 0:
        raise LandingRefused(
            "git {} failed rc={}: {}".format(
                " ".join(args), r.returncode, r.stderr.decode("utf-8", "replace").strip()[-400:]))
    return r.stdout.decode("utf-8", "replace").strip()


def _gitless_env(env: dict | None = None) -> dict:
    """Strip every GIT_* key. Same reasoning as the pre-commit gate's own scrub (H24): a leaked
    GIT_INDEX_FILE / GIT_DIR points at the REAL worktree and has already been observed corrupting
    it. Here it would also silently make the extract's git commands operate on the real repo,
    which would defeat the entire point of extracting."""
    src = os.environ if env is None else env
    return {k: v for k, v in src.items() if not k.startswith("GIT_")}


def _free_mb(path: str) -> int | None:
    try:
        return shutil.disk_usage(path).free // (1024 * 1024)
    except OSError:
        return None


def _dir_size_mb(path: Path) -> int:
    total = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for name in filenames:
            try:
                total += (Path(dirpath) / name).stat().st_size
            except OSError:
                pass
    return total // (1024 * 1024)


def sweep_stale_extracts(base: str | None = None) -> tuple[int, int]:
    """Remove abandoned `surgical-land-*` checkout directories and return (count, mb_freed).

    Every checkout this tool creates (`_land_once`, `tempfile.mkdtemp(prefix="surgical-land-")`)
    is stamped with `OWNER_MARKER` -- its creating PID -- before anything else touches it. A
    directory whose marker is missing, unreadable, or names a PID that is no longer alive was
    abandoned: `finally:` never ran for it, because `SIGTERM`/`SIGKILL` take no Python cleanup
    path (the routine outcome when a landing outruns a caller's timeout against the ~9.5-minute
    gate). Every extract created before this fix has no marker at all, so it sweeps too -- that
    is the 24-directory, ~3.6GB backlog this was written against.

    R15, fail-dangerous direction: a directory whose marker names a LIVE pid is left standing,
    even mid-run, even if this process cannot see why it is slow -- a sweep that deletes the tree
    a concurrent lane is being gated in is strictly worse than the leak it replaces.
    `test_a_live_extract_survives_the_sweep` pins this; `test_sweep_removes_a_dead_extract` and
    `test_sweep_removes_a_markerless_legacy_extract` pin the other direction.
    """
    # BOTH ROOTS when no explicit base is given (2026-08-14). Extracts moved from the tmpfs to
    # `EXTRACT_ROOT`, but every directory leaked BEFORE that move is still sitting in
    # `gettempdir()` -- and those are the ones filling the tmpfs that made the move necessary. A
    # sweeper that only looks where new extracts land can never reclaim the backlog that caused
    # the incident, so it looks in both and de-duplicates when they are the same path.
    if base:
        bases = [Path(base)]
    else:
        bases = [EXTRACT_ROOT]
        legacy = Path(tempfile.gettempdir())
        if legacy.resolve() != EXTRACT_ROOT.resolve():
            bases.append(legacy)
    removed = 0
    freed_mb = 0
    candidates: list[Path] = []
    for base_dir in bases:
        try:
            candidates.extend(sorted(base_dir.glob("surgical-land-*")))
        except OSError:
            continue
    for path in candidates:
        if not path.is_dir():
            # `build_resulting_tree`'s index tempfile shares the "surgical-land-index-" prefix
            # but is a FILE, unlinked immediately at creation -- never a leak source.
            continue
        pid = None
        try:
            pid = int((path / OWNER_MARKER).read_text().strip())
        except (FileNotFoundError, ValueError, OSError):
            pid = None
        alive = False
        if pid is not None:
            try:
                os.kill(pid, 0)
                alive = True
            except ProcessLookupError:
                alive = False
            except OSError:
                alive = True  # exists under another user, or unclear -- conservative: leave it
        if alive:
            continue
        freed_mb += _dir_size_mb(path)
        shutil.rmtree(path, ignore_errors=True)
        if not path.exists():
            removed += 1
    return removed, freed_mb


# Extracts belonging to THIS process, so a SIGTERM/SIGINT (not SIGKILL -- no handler catches
# that) can still clean up its own checkout even though `finally:` in `_land_once` is skipped.
# `sweep_stale_extracts` above is the other half, for the signal this can't catch.
_ACTIVE_CHECKOUTS: set[Path] = set()
_SIGNAL_HANDLERS_INSTALLED = False


def _cleanup_active_checkouts() -> None:
    for path in list(_ACTIVE_CHECKOUTS):
        shutil.rmtree(path, ignore_errors=True)
        _ACTIVE_CHECKOUTS.discard(path)


atexit.register(_cleanup_active_checkouts)


def _install_signal_handlers() -> None:
    global _SIGNAL_HANDLERS_INSTALLED
    if _SIGNAL_HANDLERS_INSTALLED:
        return

    def _handler(signum: int, _frame: object) -> None:
        _cleanup_active_checkouts()
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _handler)
        except (ValueError, OSError):
            pass  # not the main thread, or platform doesn't support it -- atexit still covers
                  # normal exceptional exit; sweep_stale_extracts covers SIGKILL either way
    _SIGNAL_HANDLERS_INSTALLED = True


# ---------------------------------------------------------------------------------------------
# Step 1-2: the resulting tree, built without opening the caller's index.
# ---------------------------------------------------------------------------------------------

def _mode_at(root: Path, parent: str, path: str) -> str:
    """The file mode `path` has in `parent`, or the regular-file default when it is new there.

    Read from the PARENT COMMIT and never from the filesystem: a content-sourced landing exists
    precisely because the working-tree copy is somebody else's, so its permission bits are
    somebody else's too. Preserving the parent's mode is what keeps a content landing of a
    committed executable (a hook, a script) from silently de-executing it."""
    out = _git_text(root, "ls-tree", parent, "--", path)
    return out.split(" ", 1)[0] if out else "100644"


def build_resulting_tree(root: Path, paths: list[str], parent: str,
                         content: Mapping[str, bytes | None] | None = None) -> str:
    """Return the tree sha `HEAD` would have if exactly `paths` were committed from the working
    tree. The caller's index is not read, not written, and not locked.

    `content` OVERRIDES THE CONTENT SOURCE for the paths it names: each key is committed with
    exactly the given bytes (or, for a `None` value, committed as a DELETION), and its working
    tree copy is never read. Every other path in `paths` still comes from the working tree.

    This parameter is the R3 redesign of 2026-08-19
    (`WORKER_FINDING_THREE_CONSECUTIVE_PASSES_RECORDED_A_LANDING_THAT_IS_IN_NO_COMMIT`). Before
    it, a file carrying two lanes could only be landed by swapping the SHARED worktree copy to
    HEAD-plus-my-hunks and restoring it under a `trap` -- which gave the procedure two exits that
    are byte-identical on disk (committed-then-restored, and died-then-restored), so a landing
    that never happened left a tree indistinguishable from one that did. Three consecutive passes
    read that tree, believed their predecessor, and recorded a landing that is in no commit. With
    the bytes passed in, there is no swap, no trap, and no restore, so the only evidence of a
    landing is the commit itself. It also removes the retry hazard: `land()` re-reads its content
    source on each `BaseMoved` retry, and a mapping does not change under it the way a shared
    worktree does.

    Keys must be named verbatim in `paths`. A content override outside the pathspec would be a
    change the receipt does not account for, which is the property the whole tool exists to keep.
    """
    content = dict(content or {})
    stray = sorted(k for k in content if k not in set(paths))
    if stray:
        raise LandingRefused(
            "content given for path(s) not named in the pathspec: {}. A content override is "
            "still a landed change, so it must be named like every other one.".format(
                ", ".join(stray)))
    fd, idx = tempfile.mkstemp(prefix="surgical-land-index-")
    os.close(fd)
    os.unlink(idx)  # git wants to create it itself
    env = _gitless_env()
    env["GIT_INDEX_FILE"] = idx
    try:
        _git_text(root, "read-tree", parent, env=env)
        # A DELETION must land as a deletion: a tool that could only add would leave the
        # deleting half of a two-part change silently uncommitted, which is the wedge shape in
        # the other direction. `-A` is EXPLICIT, not load-bearing -- a pathspec'd `git add` has
        # covered removals since git 2.0, and dropping it changes nothing (measured; the
        # deletion test survives the edit). It is written so a later reader narrowing this to
        # `--update` or `--ignore-removal` has to notice they are changing the contract.
        from_worktree = [p for p in paths if p not in content]
        if from_worktree:
            _git_text(root, "add", "-A", "--", *from_worktree, env=env)
        for path, blob in content.items():
            if blob is None:
                _git_text(root, "update-index", "--force-remove", "--", path, env=env)
                continue
            r = _git(root, "hash-object", "-w", "--stdin", "--path", path, env=env, stdin=blob)
            if r.returncode != 0:
                raise LandingRefused("hashing the content for {} failed rc={}: {}".format(
                    path, r.returncode, r.stderr.decode("utf-8", "replace").strip()[-300:]))
            sha = r.stdout.decode("ascii").strip()
            _git_text(root, "update-index", "--add", "--cacheinfo",
                      "{},{},{}".format(_mode_at(root, parent, path), sha, path), env=env)
        return _git_text(root, "write-tree", env=env)
    finally:
        for leftover in (idx, idx + ".lock"):
            try:
                os.unlink(leftover)
            except OSError:
                pass


def _conflicted_paths(lines: list[str]) -> list[str]:
    """The conflicted PATHS from `merge-tree --write-tree --name-only` output.

    The format is: the tree sha, then one path per line, then a BLANK LINE, then git's
    informational messages ("Auto-merging x", "CONFLICT (content): Merge conflict in x").

    THE BLANK LINE IS THE WHOLE POINT, and the refusal that predates this function did not stop
    at it — it took everything after the tree sha, so a ONE-file conflict was reported as
    **"4 conflicted path(s)"** with `Auto-merging ...` listed as if it were a filename. Harmless
    while the number was only prose in a refusal; load-bearing the moment a resolution has to be
    matched against the set, because a caller resolving the one real path would be told two
    informational lines were still unresolved.
    """
    paths: list[str] = []
    for raw in lines[1:]:
        if not raw.strip():
            break
        paths.append(raw.strip())
    return paths


def _overlay_on_tree(root: Path, base_tree: str, content: Mapping[str, bytes]) -> str:
    """`base_tree` with `content`'s bytes written over the paths it names. Returns the new tree.

    The same plumbing `build_resulting_tree` uses -- a scratch index, never the caller's -- so the
    shared index is not opened here either. Split out because two callers now need it and a second
    copy of index handling is how the two would drift.
    """
    fd, idx = tempfile.mkstemp(prefix="surgical-land-index-")
    os.close(fd)
    os.unlink(idx)
    env = _gitless_env()
    env["GIT_INDEX_FILE"] = idx
    try:
        _git_text(root, "read-tree", base_tree, env=env)
        for path, blob in content.items():
            r = _git(root, "hash-object", "-w", "--stdin", "--path", path, env=env, stdin=blob)
            if r.returncode != 0:
                raise LandingRefused("hashing the resolution for {} failed rc={}: {}".format(
                    path, r.returncode, r.stderr.decode("utf-8", "replace").strip()[-300:]))
            sha = r.stdout.decode("ascii").strip()
            _git_text(root, "update-index", "--add", "--cacheinfo",
                      "{},{},{}".format(_mode_at(root, base_tree, path), sha, path), env=env)
        return _git_text(root, "write-tree", env=env)
    finally:
        for leftover in (idx, idx + ".lock"):
            try:
                os.unlink(leftover)
            except OSError:
                pass


def build_merge_tree(root: Path, parent: str, other: str,
                     resolutions: Mapping[str, bytes] | None = None) -> str:
    """Return the tree a merge of `other` into `parent` would produce. Refuses on conflict.

    WHY THIS EXISTS (2026-09-01, the Lane 0 reconciliation). `git merge` commits THE SHARED
    INDEX. On this tree that index routinely holds another lane's staged work -- 40 paths of the
    gap-ledger lane's, the morning this was written -- so a `git merge` here does the exact thing
    the wall forbids and `land()` was built to avoid: it sweeps work nobody reviewed into a
    commit. Git's own answer is to refuse the merge outright, which leaves the two histories
    diverged and every "uncommitted work" alarm on this machine reading a stale base.

    So the merge needs the same treatment a partial commit already gets: compute the tree
    WITHOUT opening the caller's index, then gate THAT tree and commit it. `--write-tree` does
    exactly that -- it reads the two commits and writes a tree to the object store, touching
    neither the index nor the working tree. Writing loose objects that no ref yet reaches is not
    a mutation of anything a reader can see; only `_commit_and_swap` moves a ref.

    THIS IS NOT THE BYPASS THE WALL NAMES. The forbidden shape is a HAND-BUILT merge whose commit
    never faces the hook. Here the merged tree goes through `materialise` + `run_gate` like every
    other resulting tree, and a red gate refuses it. The tree is built by plumbing for the same
    reason `build_resulting_tree` is: so the shared index is never opened.

    A CONFLICT IS A REFUSAL UNLESS THE CALLER RESOLVES IT BY NAME, and until 2026-09-02 there was
    no way to resolve one at all. That was a wall with a hole in it (director's words): the only
    sanctioned merge door refused on conflict, `git merge` is forbidden on a shared tree whose
    index holds other lanes' work, and hook-bypass is a wall — so a conflicting reconciliation had
    NO legal route and had to be done by hand in a worktree. Hit twice in one morning on one file,
    both times blocking every landing and the publish path behind it.

    `resolutions` closes it, under four rules that keep it a RESOLUTION and not a smuggling route:

      1. **Only a path that actually conflicted may be resolved.** This is the load-bearing one.
         Without it, `--merge --content` becomes a way to put arbitrary bytes into a merge commit
         under the cover of resolving something, and the receipt would say "merge" while the tree
         said otherwise.
      2. **Every conflicted path must be resolved, or it refuses.** A partial resolution leaves
         git's conflict markers in the committed tree — a broken file that passed a gate.
      3. **The bytes come from OUTSIDE the repo**, exactly as `--content` already requires, so the
         shared worktree is never swapped and the two-exits hazard of the 2026-08-19 finding
         cannot return.
      4. **The gate still runs on the resulting tree**, unchanged. Resolving a conflict does not
         buy an exemption from anything; it only makes the tree expressible.

    WHAT THIS DOES NOT DO: choose. The caller supplies the bytes, because which side wins is a
    judgement about two lanes' intent that belongs to a person reading both. `origin_reconcile`
    therefore still refuses on conflict and always will — an automatic reconciler must not pick.
    """
    resolutions = dict(resolutions or {})
    r = _git(root, "merge-tree", "--write-tree", "--name-only", parent, other)
    out = r.stdout.decode("utf-8", "replace").strip().splitlines()
    if r.returncode == 1:
        conflicted = _conflicted_paths(out)
        if not resolutions:
            raise LandingRefused(
                "MERGE CONFLICT between {} and {} -- {} conflicted path(s), nothing was committed:\n"
                "  {}\nA conflict is two lanes disagreeing about one file; resolve it by reading "
                "both sides, not by re-running this. To land a resolution, pass the chosen bytes "
                "with --resolve <path>=<file-outside-the-repo> for EVERY path above.".format(
                    parent[:9], other[:9], len(conflicted),
                    "\n  ".join(conflicted) if conflicted else "(git named none)"))
        stray = sorted(k for k in resolutions if k not in set(conflicted))
        if stray:
            raise LandingRefused(
                "resolution given for path(s) that did NOT conflict: {}. A resolution may only "
                "settle a real disagreement -- allowing one anywhere else would make --resolve a "
                "way to put arbitrary bytes into a merge commit whose receipt says 'merge'.".format(
                    ", ".join(stray)))
        missing = sorted(set(conflicted) - set(resolutions))
        if missing:
            raise LandingRefused(
                "{} conflicted path(s) left unresolved: {}. A partial resolution commits git's "
                "conflict markers into the tree -- a broken file that passed a gate.".format(
                    len(missing), ", ".join(missing)))
        if not out or not out[0].strip():
            raise LandingRefused(
                "`merge-tree` reported a conflict but wrote no tree to resolve against.")
        return _overlay_on_tree(root, out[0].strip(), resolutions)
    if resolutions:
        raise LandingRefused(
            "resolutions given but the merge of {} into {} has NO conflict. A resolution with "
            "nothing to resolve is a content change wearing a merge's receipt.".format(
                other[:9], parent[:9]))
    if r.returncode != 0 or not out:
        raise LandingRefused(
            "`git merge-tree --write-tree {} {}` failed rc={}: {}".format(
                parent[:9], other[:9], r.returncode,
                r.stderr.decode("utf-8", "replace").strip()[-400:]))
    return out[0].strip()


def changed_paths(root: Path, parent_tree: str, result_tree: str) -> list[str]:
    """The files this commit actually changes -- expanded from the pathspec by git, not by us,
    so a directory argument is accounted for file by file in the receipt."""
    out = _git_text(root, "diff", "--name-only", parent_tree, result_tree)
    return [ln for ln in out.splitlines() if ln.strip()]


# ---------------------------------------------------------------------------------------------
# Step 3: the clean extract.
# ---------------------------------------------------------------------------------------------

def _object_store(root: Path) -> Path:
    """The repo's real object directory, ASKED FOR rather than assumed to be `root/.git/objects`.

    WHY THIS IS A FUNCTION AND NOT A PATH JOIN (2026-08-31). It was the join, and it made this
    whole door unusable from a `git worktree`: a linked worktree's `.git` is a FILE containing
    `gitdir: <path>`, not a directory, so `root/.git/objects` does not exist and the alternates
    line written from it sent git looking for the parent commit in a directory that was never
    there:

        error: unable to normalize alternate object path: <worktree>/.git/objects
        fatal: failed to unpack tree object <sha>

    It refused rather than mis-committing, which is the right failure -- but it made two of this
    project's own rules mutually exclusive. Hook-bypass is a wall and this is the only legal door;
    the shared working tree is a known collision surface and `git worktree` is the standard remedy.
    Any writer that isolated itself therefore had no way to commit at all, which is why the
    delivery seat could not be given its own tree.

    `git rev-parse --git-common-dir` answers for BOTH layouts, and the COMMON dir is the right one
    rather than `--git-dir`: a worktree's own gitdir (`.git/worktrees/<name>`) holds its HEAD and
    index and NOT the objects, which live once in the shared store. Lending the per-worktree dir
    would produce the same missing-objects failure one directory down.

    It returns `.git` (relative) in a normal repo and an absolute path from a worktree.
    `Path(root, common)` is correct for both -- an absolute right-hand side wins, a relative one
    joins -- so the normal path is byte-identical to what it was before.
    """
    common = _git_text(root, "rev-parse", "--git-common-dir", env=_gitless_env())
    return (Path(root, common) / "objects").resolve()


def _make_standalone_repo(root: Path, checkout: Path, parent: str) -> None:
    """Turn an extracted tree into a real standalone repo whose HEAD is the PARENT commit.

    A checkout with no history is not a checkout (R10 closure already paid for once in the
    publish gate): tests that ask git a question -- blame, rev-parse, is-this-tree-clean -- die
    with `fatal: not a git repository` rather than saying anything about the code. HEAD is the
    parent and the index is read from it, so `git diff --cached` in step 4 reads as THIS COMMIT."""
    env = _gitless_env()
    _git_text(checkout, "init", "-q", env=env)
    alternates = checkout / ".git" / "objects" / "info" / "alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_text(str(_object_store(root)) + "\n")
    (checkout / ".git" / "HEAD").write_text(parent + "\n")
    _git_text(checkout, "read-tree", parent, env=env)


def _overlay_untracked_data(root: Path, checkout: Path) -> None:
    """Symlink the machine's untracked DATA in. Never raises: a missing overlay makes tests fail
    loudly inside the gate, which is a better failure than the gate refusing to run at all."""
    for rel in UNTRACKED_DATA_OVERLAY:
        src, dst = root / rel, checkout / rel
        if not src.exists() or dst.exists():
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.symlink_to(src.resolve(), target_is_directory=src.is_dir())
        except OSError:
            pass


def materialise(root: Path, checkout: Path, result_tree: str, parent: str,
                paths: list[str], swept: tuple[int, int] = (0, 0)) -> None:
    """Extract `result_tree` into `checkout` and stage exactly `paths` against `parent`.

    `swept` is (count, mb_freed) from this call's own `sweep_stale_extracts()`, run by the
    caller just before this. It is folded into the disk-refusal message so a refusal names what
    it found, not just the symptom (WORKER_FINDING_THE_ONLY_LEGAL_LANDING_MOVE_LEAKS_150MB_A_
    KILL_2026-08-14, point 4 -- the refusal that sent that finding looking at the wrong thing
    first)."""
    free = _free_mb(str(checkout))
    if free is not None and free < MIN_FREE_MB:
        swept_count, swept_mb = swept
        raise LandingRefused(
            "REFUSED on DISK, not on code: {}MB free where the extract needs ~{}MB, so the gate "
            "could not be materialised. Nothing here says a test failed. Swept {} stale "
            "surgical-land extract(s) first, reclaiming {}MB -- still short. Reclaim more space "
            "and re-run.".format(free, MIN_FREE_MB, swept_count, swept_mb))
    archive = _git(root, "archive", result_tree)
    if archive.returncode != 0:
        raise LandingRefused("`git archive {}` failed rc={}: {}".format(
            result_tree[:9], archive.returncode,
            archive.stderr.decode("utf-8", "replace").strip()[-400:]))
    untar = subprocess.run(["tar", "-x", "-C", str(checkout)], input=archive.stdout,
                           capture_output=True, timeout=600)
    if untar.returncode != 0:
        raise LandingRefused("extracting the resulting tree failed rc={}: {}".format(
            untar.returncode, untar.stderr.decode("utf-8", "replace").strip()[-400:]))
    _make_standalone_repo(root, checkout, parent)
    # ORDER IS LOAD-BEARING: stage FIRST, overlay SECOND. The extract's working tree is the
    # resulting tree and its index is the parent, so the staged set comes out equal to this
    # commit either way -- but symlinking a 291MB cache and node_modules in BEFORE the `add`
    # would stage the whole overlay and hand every staging-aware gate a fabricated scope. (The
    # `-- *paths` pathspec is belt-and-braces on the same property; it is the ORDER that a
    # mutation can actually break, so that is what `test_the_untracked_overlay_is_symlinked_
    # AFTER_staging` pins.)
    _git_text(checkout, "add", "-A", "--", *paths, env=_gitless_env())
    _overlay_untracked_data(root, checkout)


# ---------------------------------------------------------------------------------------------
# Step 4: the gate, against the extract.
# ---------------------------------------------------------------------------------------------

def run_gate(checkout: Path, hook_rel: str = HOOK_REL) -> tuple[int, str, str]:
    """Run the repo's own pre-commit hook inside the extract. Returns (rc, stdout, stderr).

    THE TWO STREAMS ARE KEPT APART, and that is load-bearing rather than tidy (2026-08-24,
    WORKER_FINDING_THE_GATES_REFUSAL_QUOTES_SIX_GREEN_LINES_WHEN_A_NON_PYTEST_GATE_REDS). This
    returned `stdout + stderr` for a year. The hook is a `cmd || exit 1` chain of twelve gates,
    so it stops at the first failure and whichever gate reds writes the END of stdout -- which
    makes the tail of STDOUT the one read that names the refusing gate without needing to know
    twelve vocabularies. Concatenating stderr onto it destroyed exactly that property: the tail
    of the joined stream is import-time SyntaxWarnings, every time, and the refusal that
    reached a reader was six green ticks under the word REFUSED.

    FAIL-CLOSED: a hook that is missing, unreadable or un-runnable raises rather than returning
    0. This is the branch that decides whether the tool is a gate or a rubber stamp."""
    hook = checkout / hook_rel
    if not hook.is_file():
        raise LandingRefused(
            "the gate is UNAVAILABLE: {} does not exist in the resulting tree. An unavailable "
            "check is a FAILED check (R15) -- refusing rather than landing ungated.".format(
                hook_rel))
    try:
        r = subprocess.run(["sh", hook_rel], cwd=str(checkout), env=_gitless_env(),
                           capture_output=True, text=True, timeout=3600)
    except (OSError, subprocess.SubprocessError) as exc:
        raise LandingRefused(
            "the gate could not be EXECUTED ({}) -- refusing rather than landing ungated.".format(
                exc)) from exc
    return r.returncode, (r.stdout or ""), (r.stderr or "")


_PYTEST_SUMMARY = child_diagnostics.PYTEST_SUMMARY


def _test_summary(output: str) -> str:
    """Best-effort one-line count from the gate's own pytest output, for the receipt. Purely
    descriptive -- nothing branches on it, so a parse miss degrades to 'not parsed', never to a
    wrong pass/fail claim (the receipt's falsifiable fields are the shas and the path list)."""
    hits = _PYTEST_SUMMARY.findall(output)
    return hits[-1].strip() if hits else "not parsed"


# THE SELECTOR MOVED (2026-08-24), and the move IS the class fix (R10). This refusal header
# and the publisher's refusal header in `background_worker` had the SAME defect for the SAME
# reason -- an excerpt chosen by POSITION out of a stream whose tail is written by whatever the
# runtime did last -- and only this one was repaired. Fixing the sibling by copying this
# function would have left two vocabularies to keep in step, so the predicate and the budgeting
# now live once, in `background.child_diagnostics`, and both refusal headers call it. The names
# below stay as this module's own handles on that shared implementation.
_VERDICT_TRUNCATED = child_diagnostics.VERDICT_TRUNCATED
_NO_OUTPUT = child_diagnostics.NO_OUTPUT
_is_verdict_line = child_diagnostics.is_verdict_line

#: The markers that make a stream the one carrying a REFUSAL, as opposed to a stream that
#: happens to be non-empty. A gate prints a ✓ per check it clears, so "stdout is non-empty"
#: says only that some check passed -- and sizing the stderr budget off that starves the
#: diagnostic in proportion to how much of the gate WORKED.
_VERDICT_MARKERS = ("❌", "✗", "FAILED", "REFUSED", "BREACH", "Traceback", "ERROR")


def _carries_a_verdict(text: str) -> bool:
    """Does this stream name a failure, or has it only reported successes?

    Deliberately a fixed marker list rather than "anything that is not a ✓": a gate is free
    to print prose, and prose that happens to lack a tick is not a verdict. Adding a new
    refusal shape to a gate means adding its marker here, and
    `test_a_new_refusal_shape_that_is_not_in_the_marker_list_is_caught_by_the_fallback`
    pins the safe direction -- an unrecognised refusal falls back to giving stderr the FULL
    budget, never to hiding it.
    """
    return any(marker in text for marker in _VERDICT_MARKERS)


def _verdict_excerpt(stdout: str, stderr: str = "", limit: int = 4000) -> str:
    """Why a red gate refused, from BOTH of its streams, labelled.

    Each stream is excerpted on its own: the tail (which, for a `cmd || exit 1` chain, is
    written by whichever gate went red) plus any earlier verdict lines that tail would lose
    (the individual FAILED nodes of a pytest run that printed 200 lines after them). The
    reasoning, and both incidents that produced it, are documented once on
    `child_diagnostics.verdict_excerpt`.

    STDERR IS SHOWN, NOT DROPPED, and gets the smaller share. It is where a gate that died on
    a traceback says so, and a refusal that hid that would be the mirror of the defect this
    replaced -- but it is also where the library warnings live, so it must never be able to
    crowd out stdout's verdict. Hence the split budget rather than a preference.

    Character-budgeted rather than line-budgeted because a refusal MESSAGE has a size; the
    publisher's log header wants lines. That is the whole difference between the two callers,
    and it is a parameter rather than a fork of the code."""
    reserve = max(400, limit // 5)
    out_text, _ = child_diagnostics.verdict_excerpt(
        stdout, max_chars=limit - reserve, empty_marker=child_diagnostics.NO_OUTPUT)
    parts = ["  gate stdout (the verdict, and the tail the refusing gate wrote):", out_text]
    # STDERR NEVER OUTWEIGHS THE STREAM THAT CARRIES THE VERDICT. A fixed reserve is wrong at
    # both ends: a gate that refuses in three lines would be buried under 400 characters of
    # SyntaxWarning -- visually the same defect as the one this replaced -- while a gate that
    # dies on a traceback and says nothing on stdout needs the whole budget over here. So the
    # cap is the size of the stdout section, except when that section carries no verdict.
    #
    # "NO STDOUT SECTION" WAS THE WRONG TEST, and it cost a refusal that named nothing
    # (2026-08-26, landing 416 archived findings). The gate had printed exactly one line
    # before dying -- `[test-gate] ✓ finding-class consolidation holds`, a check that
    # PASSED -- so `said_nothing` was False, the stderr budget collapsed to the 45
    # characters of that tick, and the ❌ block naming the real refusal was truncated to a
    # fragment of its own elision notice. A passing tick is not a verdict. Sizing the
    # diagnostic off stdout's LENGTH rather than its CONTENT means the more checks a gate
    # clears before failing, the less of the failure a reader is shown -- the control
    # degrading exactly as the thing it watches gets closer to working, which is the same
    # class as `child_diagnostics._elide_long` earlier the same day.
    said_nothing = (out_text.strip() in ("", child_diagnostics.NO_OUTPUT)
                    or not _carries_a_verdict(out_text))
    err_budget = limit if said_nothing else min(reserve, len(out_text))
    err_text, _ = child_diagnostics.verdict_excerpt(stderr, max_chars=err_budget,
                                                    empty_marker="")
    if err_text.strip():
        parts += ["  gate stderr (usually library noise -- read it when stdout names nothing):",
                  err_text]
    return "\n".join(parts)


# ---------------------------------------------------------------------------------------------
# Step 5-6: the compare-and-swap landing, and the receipt.
# ---------------------------------------------------------------------------------------------

def build_receipt(parent: str, result_tree: str, files: list[str], gate_rc: int,
                  tests: str, hook_rel: str = HOOK_REL,
                  content_sourced: list[str] | None = None,
                  merge_parent: str | None = None,
                  resolved: list[str] | None = None) -> str:
    lines = [
        RECEIPT_HEADER,
        "tool: tools/surgical_land.py",
        "parent: {}".format(parent),
    ]
    if merge_parent:
        # `verify` re-derives `parent` as `<commit>^`, which is the FIRST parent, so it keeps
        # working on a merge unchanged. This line is what tells a reader the second one exists --
        # a receipt naming one parent on a two-parent commit would understate the scope.
        lines.append("merge-parent: {}".format(merge_parent))
    lines += [
        "tree: {}".format(result_tree),
        "gate: sh {} (run in a clean extract of tree {})".format(hook_rel, result_tree[:9]),
        "gate-rc: {}".format(gate_rc),
        "tests: {}".format(tests),
    ]
    if content_sourced:
        # Named because these are exactly the paths whose committed bytes are NOT the working
        # tree's, so a later reader diffing the tree against disk must not read the difference
        # as a failed landing. Emitted ABOVE the `paths:` block so it cannot be mistaken for a
        # path entry by `parse_receipt` (which keys the path set on the "- " prefix).
        lines.append("content-sourced: {}".format(", ".join(sorted(content_sourced))))
    if resolved:
        # A RESOLVED MERGE SAYS SO, BY NAME. These paths conflicted and a person chose the bytes,
        # so the tree at them is neither side's -- and a reader diffing this merge against either
        # parent will find a difference that is neither a mistake nor a third lane. Recording it
        # here is what makes "somebody decided" part of the record rather than folklore, and it is
        # the difference between a resolution and a smuggled change.
        lines.append("conflicts-resolved: {}".format(", ".join(sorted(resolved))))
    lines.append("paths: {}".format(len(files)))
    lines += ["  - {}".format(p) for p in files]
    return "\n".join(lines)


def merge_dispositions(root: Path, files: list[str]) -> tuple[list[str], list[str]]:
    """Split a merge's changed paths by what the SHARED working tree is already doing with them.

    Returns (index_refreshable, worktree_writable).

    A pathspec landing changes only paths its caller named, so its post-state is simple. A merge
    changes whatever the other history changed -- here, 97 paths across three lanes' live work --
    and the shared tree has an opinion about some of them. Three cases, and the difference
    between them is whose bytes get destroyed:

    STAGED BY ANOTHER LANE (index differs from HEAD): refresh neither index nor working tree.
      Their staged bytes are a decision they have not committed yet; overwriting the index entry
      would delete it with no reflog and no diff to find it in. Left alone, `git status` reports
      it as a staged modification against the new HEAD -- which is exactly what it now is.
    MODIFIED IN THE WORKING TREE (unstaged): refresh the index, leave the file.
      The index must move or `git status` would read the whole merge as a staged REVERT and the
      next commit would undo 23 commits of other lanes' work. The file must NOT move: those
      bytes are someone's uncommitted edit, and this is the `git checkout <path>` that the wall
      forbids for exactly that reason.
    CLEAN: refresh the index and write the file.
      This is the only case where the working tree can safely be moved to the merged content,
      and it is what makes the merge visible on disk rather than only in the history.

    Untracked ('??') counts as modified, not clean: a merge that adds a path someone is already
    holding untracked bytes for must not overwrite them.
    """
    if not files:
        return [], []
    r = _git(root, "status", "--porcelain", "-z", "--no-renames", "--", *files)
    if r.returncode != 0:
        raise LandingRefused(
            "could not read the working tree's disposition for the merge's {} path(s) rc={}: {}. "
            "Refusing rather than guessing -- guessing here overwrites another lane's "
            "uncommitted work.".format(
                len(files), r.returncode, r.stderr.decode("utf-8", "replace").strip()[-300:]))
    staged, modified = set(), set()
    for entry in r.stdout.decode("utf-8", "replace").split("\0"):
        if len(entry) < 4:
            continue
        x, y, path = entry[0], entry[1], entry[3:]
        if x not in " ?":
            staged.add(path)
        if y != " ":
            modified.add(path)
    refreshable = [f for f in files if f not in staged]
    writable = [f for f in refreshable if f not in modified]
    return refreshable, writable


def _write_worktree_from_tree(root: Path, result_tree: str, paths: list[str]) -> None:
    """Put `paths` on disk as `result_tree` has them, via a THROWAWAY index.

    `git checkout-index` is the only plumbing that writes tracked content to the working tree
    without an opinion about HEAD, and pointing it at a scratch index keeps the real one shut --
    the same discipline as `build_resulting_tree`. The caller has already established that every
    path here is clean, so nothing being overwritten is anybody's uncommitted work."""
    if not paths:
        return
    fd, idx = tempfile.mkstemp(prefix="surgical-land-merge-index-")
    os.close(fd)
    os.unlink(idx)
    env = _gitless_env()
    env["GIT_INDEX_FILE"] = idx
    try:
        _git_text(root, "read-tree", result_tree, env=env)
        listing = _git_text(root, "ls-tree", "-r", "--name-only", "--full-name", result_tree,
                            "--", *paths, env=env)
        present = {ln for ln in listing.splitlines() if ln.strip()}
        write = [p for p in paths if p in present]
        if write:
            _git_text(root, "checkout-index", "-f", "--", *write, env=env)
        # The merge's deletions. A path the other history removed has to leave the disk too, or
        # the next `git add -A` in this tree resurrects it as a new file.
        for gone in (p for p in paths if p not in present):
            try:
                (root / gone).unlink()
            except OSError:
                pass
    finally:
        for leftover in (idx, idx + ".lock"):
            try:
                os.unlink(leftover)
            except OSError:
                pass


def _refresh_index_for(root: Path, result_tree: str, files: list[str], sha: str = "") -> None:
    """Bring the REAL index into line for exactly the landed paths -- the same post-state
    `git commit -- <paths>` produces.

    Not doing this is not "leaving the index alone", it is corrupting it: the index would still
    hold the PARENT's content for those paths, so `git status` would show the landing as a
    staged REVERT and the next commit would undo it. Every entry outside `files` -- including
    another lane's staged work -- is untouched, which is the property the tool exists to
    protect and which its own test asserts byte-for-byte."""
    if not files:
        return
    listing = _git_text(root, "ls-tree", "-r", "--full-name", result_tree, "--", *files)
    present = {}
    for ln in listing.splitlines():
        meta, _, path = ln.partition("\t")
        mode, _, rest = meta.partition(" ")
        _, _, sha = rest.partition(" ")
        present[path] = (mode, sha.strip())
    payload = "".join(
        "{} {}\t{}\n".format(*present[f], f) if f in present
        else "0 {}\t{}\n".format(_NULL_SHA, f)
        for f in files
    )
    r = _refresh_with_retry(root, payload.encode())
    if r.returncode != 0:
        raise IndexNotRefreshed(
            "THE COMMIT LANDED as {}. Only the index refresh failed, rc={}: {}. The index now "
            "disagrees with HEAD for those paths -- run `git reset -- <paths>`. Do NOT re-land: "
            "the work is on HEAD.".format(sha or "(sha unavailable)", r.returncode,
                                          r.stderr.decode("utf-8", "replace").strip()[-300:]),
            sha=sha)


#: HOW LONG TO WAIT FOR `.git/index.lock`, and why waiting is the right answer rather than a
#: bigger refusal. The lock is held by another lane's `git commit`, and on this repo a commit is
#: ten to fifteen minutes of gate. So the window in which this call fails is not a rare race -- it
#: is open for a quarter of an hour every time any lane commits, which is most of the day. The
#: holder is a process that WILL finish and release; the only thing worth doing is to outlast it.
#:
#: Bounded, and the bound is a deadline the caller cannot outlive rather than a retry count: this
#: runs AFTER the commit is already on HEAD, so a long wait costs nothing anybody is waiting on,
#: and an unbounded one would hang a daemon behind a crashed git.
_INDEX_LOCK_DEADLINE_S = 1200.0
_INDEX_LOCK_POLL_S = 5.0


def _refresh_with_retry(root: Path, payload: bytes):
    """`update-index --index-info`, retried while the failure is a held lock.

    Only a LOCK failure is retried, and it is identified from git's own message rather than from
    the return code, because rc=128 covers everything from a held lock to a corrupt object. Any
    other failure returns immediately -- retrying a genuine error would turn one bad landing into
    twenty minutes of silence.
    """
    deadline = time.monotonic() + _INDEX_LOCK_DEADLINE_S
    while True:
        r = _git(root, "update-index", "--index-info", stdin=payload)
        if r.returncode == 0:
            return r
        stderr = r.stderr.decode("utf-8", "replace")
        if "index.lock" not in stderr and "File exists" not in stderr:
            return r
        if time.monotonic() >= deadline:
            return r
        time.sleep(_INDEX_LOCK_POLL_S)


#: How long the commit-and-swap waits for the tree lock, and why it is not `tree_lock`'s own
#: 60s default. By the time we reach the swap the gate has ALREADY PASSED -- on this repo that
#: is ten to fifteen minutes of tests -- and the swap itself is three git plumbing calls, so
#: milliseconds. Failing the whole landing because a publisher happened to hold the lock for a
#: minute discards a green verdict that cost more than the wait ever could, and it is not a
#: safety trade: `BaseMoved` still refuses if HEAD actually moved, whether we waited or not.
#: Observed twice on 2026-08-24, both times with the gate green and the daemons mid-publish.
#: Kept FINITE rather than blocking forever so a genuinely wedged lock still surfaces.
COMMIT_SWAP_LOCK_TIMEOUT_SECONDS = 900.0


@contextmanager
def _write_lock(root: Path):
    if root.resolve() != ROOT:
        yield
        return
    # `held` is what keeps this `except` honest: the body below the yield is `_commit_and_swap`'s
    # git plumbing, and if IT ever raised TreeLockTimeout we would report "could not acquire" for
    # something that had already acquired. Only a timeout raised before the lock was ever held
    # gets the friendly refusal; anything after it propagates as itself.
    held = False
    try:
        with tree_lock(timeout=COMMIT_SWAP_LOCK_TIMEOUT_SECONDS):
            held = True
            yield
    except TreeLockTimeout as exc:
        if held:
            raise
        # NOT a bare traceback. This refusal is the one that says "your change is fine" -- the
        # gate passed and nothing about the commit is wrong -- and a stack trace ending in
        # `fcntl.flock` says the opposite to whoever reads it next.
        raise LandingRefused(
            "the gate PASSED and the commit was NOT made: another writer held the tree lock for "
            "the whole {:.0f}s wait ({}). Nothing is wrong with the change. Find the holder "
            "(`ps aux | grep python3`, the publisher and sim_runner are the usual two), let it "
            "finish, and re-run the same command -- the gate will simply run again.".format(
                COMMIT_SWAP_LOCK_TIMEOUT_SECONDS, exc)) from exc


def _commit_and_swap(root: Path, result_tree: str, parent: str, message: str,
                     files: list[str], merge_parent: str | None = None) -> str:
    """commit-tree + a compare-and-swap ref update, under the tree lock.

    The CAS is what makes the gate's verdict still true at the moment of landing: on this shared
    tree a concurrent writer can move HEAD while the gate runs, and a commit whose parent moved
    was gated against a tree that no longer exists. Refuse, don't guess.

    The lock is taken only for the REAL shared tree. `tree_lock` exists to serialise the several
    daemons that write THIS working tree; a scratch repo has no other writers, and taking the
    live lock from a test would block on whatever publisher happens to hold it."""
    with _write_lock(root):
        now = _git_text(root, "rev-parse", "HEAD")
        if now != parent:
            raise BaseMoved(
                "HEAD moved from {} to {} while the gate ran, so the gated tree is no longer the "
                "tree this commit would create. Nothing was committed; re-run and it will gate "
                "the new base.".format(parent[:9], now[:9]), parent, now)
        # READ THE DISPOSITIONS BEFORE THE REF MOVES, and that ordering is the whole correctness
        # of it. `git status` answers against HEAD; once HEAD is the merge commit every path the
        # merge changed reports as a STAGED difference (the index still holds the parent's), so
        # asking afterwards classifies all of them as another lane's staged work and the merge
        # lands with an index and a working tree that were never moved. Both of this module's
        # merge post-state tests fail on that mistake, which is how it was found.
        dispositions = merge_dispositions(root, files) if merge_parent else None
        extra = ["-p", merge_parent] if merge_parent else []
        new = _git_text(root, "commit-tree", result_tree, "-p", parent, *extra, "-m", message)
        _git_text(root, "update-ref", "-m", "surgical-land", "HEAD", new, parent)
        if dispositions is not None:
            # A merge moves paths this caller never named, so unlike a pathspec landing it has to
            # ask the shared tree what it is holding before touching anything. See
            # `merge_dispositions` for why the two lists differ and what each one protects.
            refreshable, writable = dispositions
            _refresh_index_for(root, result_tree, refreshable, sha=new)
            _write_worktree_from_tree(root, result_tree, writable)
        else:
            _refresh_index_for(root, result_tree, files, sha=new)
        return new


def land(root: Path, paths: list[str], message: str, hook_rel: str = HOOK_REL,
         attempts: int = DEFAULT_ATTEMPTS, on_lost: Callable[[int, BaseMoved], None] | None = None,
         content: Mapping[str, bytes | None] | None = None,
         merge: str | None = None,
         resolutions: Mapping[str, bytes] | None = None) -> str:
    """Land exactly `paths`, re-gating against the new base when the race is lost.

    Returns the new commit sha, or raises LandingRefused. `attempts` bounds the loop; `on_lost`
    is called with (attempt_number, exc) after each lost race, which is how the CLI reports the
    cadence the finding had to reconstruct by hand from `git log`.

    THE LOOP IS ONLY OVER `BaseMoved`. Every other refusal propagates on the first attempt --
    including, especially, GATE RED. That asymmetry is the whole safety argument: a lost race
    means the verdict was about the wrong tree and must be recomputed, while a red gate means the
    verdict was about the right tree and was NO. Retrying the second is how a flaky test becomes
    a landed regression, so the code must not be able to confuse them (hence a subclass rather
    than a message match).

    Each pass through `_land_once` re-reads HEAD, so the new attempt's parent IS the mover's
    commit and its resulting tree is built by overlaying only `paths` onto that new parent --
    the mover's work is preserved, not reverted, and the gate runs again in full.

    `content` (see `build_resulting_tree`) is passed to every attempt unchanged, which is what
    makes the retry safe for a two-lane file: a worktree-sourced retry re-reads whatever the
    other lane has since written, a content-sourced one commits the same bytes it was given."""
    if attempts < 1:
        raise LandingRefused(
            "attempts={} would run no gate at all; a landing with no gate is the bypass this "
            "tool replaces.".format(attempts))
    lost: list[BaseMoved] = []
    for attempt in range(1, attempts + 1):
        try:
            sha = _land_once(root, paths, message, hook_rel, content, merge, resolutions)
            announce_landing(sha, message, paths, merge=merge)
            return sha
        except BaseMoved as exc:
            lost.append(exc)
            if on_lost is not None:
                on_lost(attempt, exc)
    raise LandingRefused(
        "HEAD moved under the gate on all {} attempt(s), so no verdict ever described the tree "
        "it would have committed. Nothing was committed.\n{}\n"
        "The gate is longer than the gap between commits on this tree, which is a defect in the "
        "GATE'S COST, not in the refusal -- raise --attempts to spend more CPU on the race, or "
        "cut what the gate selects.".format(
            len(lost),
            "\n".join("  attempt {}: {} -> {}".format(i + 1, e.parent[:9], e.observed[:9])
                      for i, e in enumerate(lost))))


def announce_landing(sha: str, message: str, paths: list[str], *,
                     merge: str | None = None, _notify=None) -> str | None:
    """Tell the channel that a piece of work LANDED. Never raises.

    WHY A LANDING HAD NEVER REACHED THE CHANNEL (2026-09-01, director: *"the channel under-reports
    you. Eight commits this evening produced no message, while divergence and publishing alarms
    filled the mirror. I've read that as a stall twice today when you were working normally."*).

    Measured, from the outbound mirror and the digest queue on the day he wrote it: 64 messages, of
    which 27 were one tree-divergence condition and 20 were publishing. Landings: **zero**, out of
    nineteen commits. Not batched-and-delayed -- `routine_landing` had no producer at all, in three
    weeks, anywhere. The channel carried what was WRONG and nothing of what was DONE, so working
    normally and being stuck looked identical from his phone.

    HERE, BECAUSE THIS IS THE ONE DOOR. `--no-verify` is a wall and `surgical_land` is the only
    legal move, so every landing this project makes passes through this function -- a producer
    anywhere else would report the landings that particular caller happened to make. It is placed
    after the compare-and-swap succeeded, so it announces a commit that EXISTS.

    BATCHED, NOT PAGED. `routine_landing` is one of the director's own four deferrable categories
    (2026-08-12: *"batch and summarise everything that isn't action-needed"*), and a landing is not
    action-needed. It rides the digest, which now leads with what was done rather than burying it
    behind whatever was filed.

    NEVER RAISES, and the reason is the whole safety argument: a landing has already happened when
    this runs, so an exception here could only turn a successful commit into a caller-visible
    failure -- a notifier that can fail a landing is a defect, not an observer.

    BUT IT NEVER FAILS QUIETLY EITHER, and the first version of this function did, within minutes of
    shipping. `background/ntfy_utils` raises at IMPORT time when `SE_NTFY_TOPIC` is unset -- so
    `background.notify` is not importable outside a daemon's environment, including for a DEFERRED
    notification that never touches the wire. This tool is run by hand, by every lane, from ordinary
    shells that never sourced `start_worker.sh`. The very commit that added the producer therefore
    landed and announced nothing, and the `except` below swallowed the reason.

    A producer that is structurally unable to produce AND structurally unable to say so is the exact
    shape this function was written to report, arriving inside the reporting of it. So: the topic is
    loaded from the file the daemons already read (topic ONLY -- `load_secret_env` refuses the
    signing key whatever a caller asks for), and any remaining failure goes to STDERR beside the
    landing line, where the operator is already looking.
    """
    try:
        if _notify is None:
            from background.secrets_location import load_secret_env
            load_secret_env()          # topic only; no-op when the environment already has it
            from background.notify import notify as _notify
        from background import notification_digest
        subject = str(message or "").strip().splitlines()
        scope = ("merge {}".format(merge) if merge
                 else "{} path(s)".format(len(paths)))
        return _notify(
            "[LANDED] {} — {} ({})".format(sha[:9], (subject[0] if subject else "")[:140], scope),
            kind="work_done", topic_class=notification_digest.ROUTINE_LANDING,
            # No transition key. Every landing is a distinct event and must never be suppressed as
            # a repeat of another one -- see the `work_done` note in `background/notify.py` for why
            # `real_alarm`'s auto-keying would have done exactly that.
        )
    except Exception as exc:  # noqa: BLE001 -- see NEVER RAISES above
        sys.stderr.write(
            "[surgical-land] LANDED {} but could NOT announce it: {}: {}\n"
            "[surgical-land] The commit is fine. The CHANNEL did not hear about it, which is the "
            "defect this producer exists to fix -- say so rather than swallow it.\n".format(
                sha[:9], type(exc).__name__, str(exc).strip()[:200]))
        sys.stderr.flush()
        return None


def _land_once(root: Path, paths: list[str], message: str, hook_rel: str = HOOK_REL,
               content: Mapping[str, bytes | None] | None = None,
               merge: str | None = None,
               resolutions: Mapping[str, bytes] | None = None) -> str:
    """ONE attempt: read HEAD, build the resulting tree, gate it, compare-and-swap."""
    if merge is None and not paths:
        raise LandingRefused("no paths given -- a surgical landing names its paths explicitly.")
    parent = _git_text(root, "rev-parse", "HEAD")
    parent_tree = _git_text(root, "rev-parse", "HEAD^{tree}")
    merge_parent = None
    if merge is not None:
        if paths or content:
            raise LandingRefused(
                "--merge takes no pathspec and no content override: a merge lands whatever the "
                "other history changed, so a pathspec here would claim a scope the commit does "
                "not have and the receipt would be a lie. To settle a CONFLICT, use --resolve, "
                "which may only name paths git itself reports as conflicted.")
        merge_parent = _git_text(root, "rev-parse", "{}^{{commit}}".format(merge))
        if _git(root, "merge-base", "--is-ancestor", merge_parent, parent).returncode == 0:
            raise LandingRefused(
                "{} ({}) is already an ancestor of HEAD -- there is nothing to merge.".format(
                    merge, merge_parent[:9]))
        result_tree = build_merge_tree(root, parent, merge_parent, resolutions)
        paths = changed_paths(root, parent_tree, result_tree)
    elif resolutions:
        raise LandingRefused(
            "--resolve is only meaningful with --merge: outside a merge there is no conflict to "
            "settle, and the bytes would just be an unnamed content change.")
    else:
        result_tree = build_resulting_tree(root, paths, parent, content)
    if result_tree == parent_tree:
        # For a merge this is the already-up-to-date case that `--is-ancestor` did not catch:
        # the other history's content is all here, but its COMMITS are not, so the merge is
        # still worth making. Only a pathspec landing has nothing to do.
        if merge_parent is None:
            raise LandingRefused(
                "the named paths are already at HEAD -- the resulting tree is identical, so "
                "there is nothing to land. (If you expected a change, check the pathspec.)")
    files = changed_paths(root, parent_tree, result_tree)
    EXTRACT_ROOT.mkdir(parents=True, exist_ok=True)
    checkout = Path(tempfile.mkdtemp(prefix="surgical-land-", dir=str(EXTRACT_ROOT)))
    # Marker written FIRST, before anything else can fail or take long: this is what makes the
    # sweep below (and any concurrent lane's sweep) leave THIS checkout alone.
    (checkout / OWNER_MARKER).write_text(str(os.getpid()))
    _install_signal_handlers()
    _ACTIVE_CHECKOUTS.add(checkout)
    swept = sweep_stale_extracts()
    try:
        materialise(root, checkout, result_tree, parent, paths, swept=swept)
        # The gate is the window archived run markers have been observed returning to the staging
        # root inside (WORKER_FINDING_ARCHIVED_RUN_MARKERS_RETURN_TO_THE_STAGING_ROOT..._2026-08-20:
        # ten files, one shared mtime, forty seconds before this tool's own reflog entry). This
        # bracket does not prevent that and does not claim a cause; it records the reappearance
        # against THIS landing so the next occurrence names its own window. It cannot fail the
        # landing -- every error inside it is swallowed and the body's exceptions pass through.
        with staging_root_resurrection_watch.bracket(
                root, "surgical-land gate: " + message.splitlines()[0][:80]):
            rc, gate_out, gate_err = run_gate(checkout, hook_rel)
        tests = _test_summary(gate_out + gate_err)
        if rc != 0:
            raise LandingRefused(
                "GATE RED on the resulting tree (rc={}). This is the tree the commit WOULD "
                "create, not the working tree -- a working tree that passes here means the "
                "unstaged half is what makes it pass.\n{}".format(
                    rc, _verdict_excerpt(gate_out, gate_err)))
    finally:
        shutil.rmtree(checkout, ignore_errors=True)
        _ACTIVE_CHECKOUTS.discard(checkout)
    receipt = build_receipt(parent, result_tree, files, rc, tests, hook_rel,
                            content_sourced=sorted(content or ()), merge_parent=merge_parent,
                            resolved=sorted(resolutions or ()))
    return _commit_and_swap(root, result_tree, parent, message + "\n\n" + receipt, files,
                            merge_parent=merge_parent)


# ---------------------------------------------------------------------------------------------
# --verify: the receipt is falsifiable, or it is decoration.
# ---------------------------------------------------------------------------------------------

def parse_receipt(message: str) -> dict | None:
    if RECEIPT_HEADER not in message:
        return None
    block = message.split(RECEIPT_HEADER, 1)[1]
    out: dict = {"paths": []}
    for raw in block.splitlines():
        ln = raw.strip()
        if ln.startswith("- "):
            out["paths"].append(ln[2:].strip())
            continue
        key, _, val = ln.partition(":")
        if key.strip() == "conflicts-resolved":
            out["conflicts_resolved"] = [x.strip() for x in val.split(",") if x.strip()]
            continue
        if key.strip() in ("parent", "tree", "gate-rc", "tests"):
            out[key.strip()] = val.strip()
    return out


def verify(root: Path, commit: str) -> tuple[int, str]:
    """Check a commit against its own receipt. rc 0 consistent, 1 FALSIFIED, 2 no receipt.

    What this can actually catch: a receipt hand-written onto a commit it does not describe.
    The three claims are all independently re-derivable from the object store -- the tree sha,
    the parent sha, and the exact set of files the commit changes -- so a receipt asserting a
    gate run over a different tree or a different path set cannot survive. It does NOT prove the
    gate was green at the time (nothing can, after the fact); it proves the receipt is ABOUT
    this commit, which is what makes the claim falsifiable rather than merely present."""
    message = _git_text(root, "log", "-1", "--format=%B", commit)
    receipt = parse_receipt(message)
    if receipt is None:
        return 2, "no surgical-land receipt on {}".format(commit)
    problems = []
    actual_tree = _git_text(root, "rev-parse", "{}^{{tree}}".format(commit))
    if receipt.get("tree") != actual_tree:
        problems.append("receipt tree {} != actual {}".format(receipt.get("tree"), actual_tree))
    actual_parent = _git_text(root, "rev-parse", "{}^".format(commit))
    if receipt.get("parent") != actual_parent:
        problems.append("receipt parent {} != actual {}".format(
            receipt.get("parent"), actual_parent))
    actual_files = set(changed_paths(root, actual_parent, actual_tree))
    if set(receipt["paths"]) != actual_files:
        problems.append("receipt path set != the {} file(s) the commit changes ({})".format(
            len(actual_files),
            ", ".join(sorted(set(receipt["paths"]) ^ actual_files))[:300]))
    if problems:
        return 1, "RECEIPT FALSIFIED for {}:\n  - {}".format(commit, "\n  - ".join(problems))
    return 0, "receipt consistent for {}: tree {}, {} path(s), gate-rc {}".format(
        commit, actual_tree[:9], len(actual_files), receipt.get("gate-rc"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="surgical_land",
        description="Commit exactly-named paths with the pre-commit gate run against the tree "
                    "the commit would create. Bypass is a wall; this is the legal move.")
    ap.add_argument("-m", "--message", help="commit message (the receipt is appended)")
    ap.add_argument("--verify", metavar="COMMIT",
                    help="check a commit against its own receipt and exit")
    ap.add_argument("--attempts", type=int, default=DEFAULT_ATTEMPTS, metavar="N",
                    help="re-gate against the new base up to N times when HEAD moves under the "
                         "gate (default {}). A RED gate is never retried.".format(
                             DEFAULT_ATTEMPTS))
    ap.add_argument("--content", action="append", default=[], metavar="REPOPATH=SRCFILE",
                    help="commit REPOPATH with the bytes of SRCFILE instead of its working-tree "
                         "copy (repeatable). This is how a file carrying two lanes is landed "
                         "WITHOUT swapping the shared worktree: keep SRCFILE outside the repo. "
                         "REPOPATH must also appear in the positional paths.")
    ap.add_argument("--content-remove", action="append", default=[], metavar="REPOPATH",
                    help="commit REPOPATH as a DELETION without removing it from the working "
                         "tree (repeatable). The mapping's None case.")
    ap.add_argument("--merge", metavar="REF",
                    help="land a MERGE of REF into HEAD instead of a pathspec. The merged tree "
                         "is computed by plumbing (the shared index is never opened, so another "
                         "lane's staged work cannot be swept into it), gated like any other "
                         "resulting tree, and committed with REF as a second parent. Refuses on "
                         "conflict unless every conflicted path is settled with --resolve. Takes "
                         "no paths and no --content.")
    ap.add_argument("--resolve", action="append", default=[], metavar="REPOPATH=SRCFILE",
                    help="settle a CONFLICTED path in a --merge with the bytes of SRCFILE "
                         "(repeatable). Only with --merge, only for paths git itself reports as "
                         "conflicted, and EVERY conflicted path must be given or the merge is "
                         "refused. Keep SRCFILE outside the repo, as with --content: the shared "
                         "worktree is never swapped. The gate still runs on the resulting tree.")
    ap.add_argument("paths", nargs="*", help="the exact paths to land")
    args = ap.parse_args(argv)
    if args.verify:
        rc, text = verify(ROOT, args.verify)
        print(text)
        return rc
    if not args.message:
        ap.error("-m/--message is required when landing")

    content: dict[str, bytes | None] = {}
    for spec in args.content:
        repo_path, sep, src = spec.partition("=")
        if not sep or not repo_path or not src:
            ap.error("--content wants REPOPATH=SRCFILE, got {!r}".format(spec))
        try:
            content[repo_path] = Path(src).read_bytes()
        except OSError as exc:
            ap.error("--content source unreadable: {}".format(exc))
    for repo_path in args.content_remove:
        content[repo_path] = None

    resolutions: dict[str, bytes] = {}
    for spec in args.resolve:
        repo_path, sep, src = spec.partition("=")
        if not sep or not repo_path or not src:
            ap.error("--resolve wants REPOPATH=SRCFILE, got {!r}".format(spec))
        # OUTSIDE THE REPO, refused here rather than trusted: a resolution read from inside the
        # working tree reintroduces the swap-and-restore hazard `--content` was built to remove,
        # where a landing that never happened leaves a tree indistinguishable from one that did.
        try:
            resolved = Path(src).resolve()
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            pass
        except OSError as exc:
            ap.error("--resolve source unreadable: {}".format(exc))
        else:
            ap.error("--resolve source {} is INSIDE the repository. Keep the chosen bytes outside "
                     "it, so the shared worktree is never swapped and the only evidence of a "
                     "landing is the commit.".format(src))
        try:
            resolutions[repo_path] = resolved.read_bytes()
        except OSError as exc:
            ap.error("--resolve source unreadable: {}".format(exc))

    def report_lost(attempt: int, exc: BaseMoved) -> None:
        # stderr and FLUSHED: this is the diagnostic that had to be reconstructed from `git log`
        # last time, and a block-buffered pipe is where it would be lost again.
        sys.stderr.write(
            "[surgical-land] attempt {}/{} lost the race: HEAD {} -> {}; re-gating the new "
            "base.\n".format(attempt, args.attempts, exc.parent[:9], exc.observed[:9]))
        sys.stderr.flush()

    try:
        sha = land(ROOT, args.paths, args.message, attempts=args.attempts, on_lost=report_lost,
                   content=content or None, merge=args.merge,
                   resolutions=resolutions or None)
    except LandingRefused as exc:
        sys.stderr.write("[surgical-land] REFUSED: {}\n".format(exc))
        return 1
    if args.merge:
        print("[surgical-land] landed MERGE {} ({} into HEAD)".format(sha[:9], args.merge))
    else:
        print("[surgical-land] landed {} ({} path(s))".format(sha[:9], len(args.paths)))
    print("[surgical-land] verify with: python3 -m tools.surgical_land --verify {}".format(
        sha[:9]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
