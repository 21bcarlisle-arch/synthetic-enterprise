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
    named paths only. The caller's real index is never opened.
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

FAIL-CLOSED, EVERYWHERE (R15: an unavailable check is a FAILED check)
---------------------------------------------------------------------
No commit is created if: the hook script is missing or unreadable; the extract cannot be
built or cannot be made a real repo; tmp has less free space than the extract needs; the hook
exits non-zero; HEAD moved under us; or the resulting tree is identical to HEAD's. Every one
of those is a REFUSAL, never a silent pass -- the failure direction that matters, because the
whole point is that this tool is the legal move and a legal move that quietly skips its check
is worse than the bypass it replaces.

R15 mutation-proven both ways in `tests/tools/test_surgical_land.py`.
Design note: `docs/design/SURGICAL_LANDING.md`.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
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

from background.tree_lock import tree_lock  # noqa: E402  (needs the path insert above)

# The gate is the repo's OWN hook, named in ONE place. Running a hand-picked subset here would
# recreate the accretion the ruling forbids: the tool must face what `git commit` faces.
HOOK_REL = "tools/git-hooks/pre-commit"

# The extract is a full tree copy. Below this, refuse -- a gate that cannot be materialised has
# not run (the publish gate's own floor, same reasoning).
MIN_FREE_MB = 500

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


# ---------------------------------------------------------------------------------------------
# Step 1-2: the resulting tree, built without opening the caller's index.
# ---------------------------------------------------------------------------------------------

def build_resulting_tree(root: Path, paths: list[str], parent: str) -> str:
    """Return the tree sha `HEAD` would have if exactly `paths` were committed from the working
    tree. The caller's index is not read, not written, and not locked."""
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
        _git_text(root, "add", "-A", "--", *paths, env=env)
        return _git_text(root, "write-tree", env=env)
    finally:
        for leftover in (idx, idx + ".lock"):
            try:
                os.unlink(leftover)
            except OSError:
                pass


def changed_paths(root: Path, parent_tree: str, result_tree: str) -> list[str]:
    """The files this commit actually changes -- expanded from the pathspec by git, not by us,
    so a directory argument is accounted for file by file in the receipt."""
    out = _git_text(root, "diff", "--name-only", parent_tree, result_tree)
    return [ln for ln in out.splitlines() if ln.strip()]


# ---------------------------------------------------------------------------------------------
# Step 3: the clean extract.
# ---------------------------------------------------------------------------------------------

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
    alternates.write_text(str((root / ".git" / "objects").resolve()) + "\n")
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
                paths: list[str]) -> None:
    """Extract `result_tree` into `checkout` and stage exactly `paths` against `parent`."""
    free = _free_mb(str(checkout))
    if free is not None and free < MIN_FREE_MB:
        raise LandingRefused(
            "REFUSED on DISK, not on code: {}MB free where the extract needs ~{}MB, so the gate "
            "could not be materialised. Nothing here says a test failed. Reclaim space and "
            "re-run.".format(free, MIN_FREE_MB))
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

def run_gate(checkout: Path, hook_rel: str = HOOK_REL) -> tuple[int, str]:
    """Run the repo's own pre-commit hook inside the extract. Returns (rc, combined output).

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
    return r.returncode, (r.stdout or "") + (r.stderr or "")


_PYTEST_SUMMARY = re.compile(r"^.*\b(\d+ (?:passed|failed|error)[^\n]*)$", re.M)


def _test_summary(output: str) -> str:
    """Best-effort one-line count from the gate's own pytest output, for the receipt. Purely
    descriptive -- nothing branches on it, so a parse miss degrades to 'not parsed', never to a
    wrong pass/fail claim (the receipt's falsifiable fields are the shas and the path list)."""
    hits = _PYTEST_SUMMARY.findall(output)
    return hits[-1].strip() if hits else "not parsed"


# ---------------------------------------------------------------------------------------------
# Step 5-6: the compare-and-swap landing, and the receipt.
# ---------------------------------------------------------------------------------------------

def build_receipt(parent: str, result_tree: str, files: list[str], gate_rc: int,
                  tests: str, hook_rel: str = HOOK_REL) -> str:
    lines = [
        RECEIPT_HEADER,
        "tool: tools/surgical_land.py",
        "parent: {}".format(parent),
        "tree: {}".format(result_tree),
        "gate: sh {} (run in a clean extract of tree {})".format(hook_rel, result_tree[:9]),
        "gate-rc: {}".format(gate_rc),
        "tests: {}".format(tests),
        "paths: {}".format(len(files)),
    ]
    lines += ["  - {}".format(p) for p in files]
    return "\n".join(lines)


def _refresh_index_for(root: Path, result_tree: str, files: list[str]) -> None:
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
    r = _git(root, "update-index", "--index-info", stdin=payload.encode())
    if r.returncode != 0:
        raise LandingRefused(
            "the commit LANDED but refreshing the index for its paths failed rc={}: {}. The "
            "index now disagrees with HEAD for those paths -- run `git reset -- <paths>` before "
            "committing again.".format(r.returncode,
                                       r.stderr.decode("utf-8", "replace").strip()[-300:]))


@contextmanager
def _write_lock(root: Path):
    if root.resolve() != ROOT:
        yield
        return
    with tree_lock():
        yield


def _commit_and_swap(root: Path, result_tree: str, parent: str, message: str,
                     files: list[str]) -> str:
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
            raise LandingRefused(
                "HEAD moved from {} to {} while the gate ran, so the gated tree is no longer the "
                "tree this commit would create. Nothing was committed; re-run and it will gate "
                "the new base.".format(parent[:9], now[:9]))
        new = _git_text(root, "commit-tree", result_tree, "-p", parent, "-m", message)
        _git_text(root, "update-ref", "-m", "surgical-land", "HEAD", new, parent)
        _refresh_index_for(root, result_tree, files)
        return new


def land(root: Path, paths: list[str], message: str, hook_rel: str = HOOK_REL) -> str:
    """Land exactly `paths`. Returns the new commit sha, or raises LandingRefused."""
    if not paths:
        raise LandingRefused("no paths given -- a surgical landing names its paths explicitly.")
    parent = _git_text(root, "rev-parse", "HEAD")
    parent_tree = _git_text(root, "rev-parse", "HEAD^{tree}")
    result_tree = build_resulting_tree(root, paths, parent)
    if result_tree == parent_tree:
        raise LandingRefused(
            "the named paths are already at HEAD -- the resulting tree is identical, so there is "
            "nothing to land. (If you expected a change, check the pathspec.)")
    files = changed_paths(root, parent_tree, result_tree)
    checkout = Path(tempfile.mkdtemp(prefix="surgical-land-"))
    try:
        materialise(root, checkout, result_tree, parent, paths)
        rc, output = run_gate(checkout, hook_rel)
        tests = _test_summary(output)
        if rc != 0:
            raise LandingRefused(
                "GATE RED on the resulting tree (rc={}). This is the tree the commit WOULD "
                "create, not the working tree -- a working tree that passes here means the "
                "unstaged half is what makes it pass.\n{}".format(rc, output[-4000:]))
    finally:
        shutil.rmtree(checkout, ignore_errors=True)
    receipt = build_receipt(parent, result_tree, files, rc, tests, hook_rel)
    return _commit_and_swap(root, result_tree, parent, message + "\n\n" + receipt, files)


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
    ap.add_argument("paths", nargs="*", help="the exact paths to land")
    args = ap.parse_args(argv)
    if args.verify:
        rc, text = verify(ROOT, args.verify)
        print(text)
        return rc
    if not args.message:
        ap.error("-m/--message is required when landing")
    try:
        sha = land(ROOT, args.paths, args.message)
    except LandingRefused as exc:
        sys.stderr.write("[surgical-land] REFUSED: {}\n".format(exc))
        return 1
    print("[surgical-land] landed {} ({} path(s))".format(sha[:9], len(args.paths)))
    print("[surgical-land] verify with: python3 -m tools.surgical_land --verify {}".format(
        sha[:9]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
