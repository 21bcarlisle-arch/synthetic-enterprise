"""PUBLISH SURFACE GATE -- the gate for a content publish, whose subject is exactly what ships.

DIRECTOR RULING, 2026-08-17 (console, approving the R3 redesign proposed after the three-day
content freeze): *"Eliminate the whole-repo hook from the content publish path -- on one
condition: whatever replaces it takes as its subject exactly the surfaces that ship, is provably
failable, and fails closed if it can't run."* This module is that replacement, and the three
clauses are its three sections below.

WHY THE OLD ARRANGEMENT FROZE THE SITE FOR THREE DAYS
-----------------------------------------------------
`background/process_run_complete.py::git_commit_push` committed with a bare `git commit`, which
fires the whole-repo hook chain. That chain's test gate (`tools/pre_commit_test_gate.py`) maps
STAGED PATHS to tests -- and the publish stages far more than it ships: `docs/design/
maturity_map.yaml` (the pre-gate atom_status inbox fold, `git add -A`), the derived design
artefacts, and `docs/staging/done/`. Measured on the real index, the map's derived answer ALONE is
50 test files; the whole publish selected ~780.

So the content publish was gated on the repo's DESIGN hygiene. Of the six reds that held it from
2026-08-14T07:04Z: two were an atom mint's missing store rows, one a stale design projection, two
a lint import-sort ratchet, one a control that had gone red because the map IMPROVED. Not one of
them was about whether the published figures were correct. The site was three days stale because
somebody's `notes_rehomed:` declaration disagreed with a YAML file the reader never sees.

THE ORPHAN THIS CLOSES, and it was already written down
-------------------------------------------------------
`pre_commit_test_gate.PUBLISHED_OUTPUT_ROOTS = ("site/", "docs/reports/", "docs/status/")` skips
test derivation for those roots, commented "regenerated output, gated elsewhere". `site/` really
is gated elsewhere (`tools/site_lane_gate.py`). **`docs/reports/` and `docs/status/` were gated by
nothing at all** -- `ANNUAL_REPORT.md` and, apart from its header honesty check, `LATEST.md` had no
gate on any path. That is an R11 orphan transition: an exclusion whose promised counterpart does
not exist. `PUBLISH_SURFACE_ROOTS` below is asserted to COVER `PUBLISHED_OUTPUT_ROOTS` by a test,
so a future root added to that exclusion without being added here fails at commit time rather than
quietly joining the orphan.

CLAUSE 1 -- THE SUBJECT IS EXACTLY WHAT SHIPS, and the gate proves it before trusting itself.
Scope is derived from the STAGED shipping paths, never from the working tree's modification set,
and `subject_is_the_commits_tree()` REFUSES when a staged shipping path differs between the index
and the tree the gate is reading. That is the precise defect that made the old arrangement
unfixable: the freeze's one genuinely-new violation lived in another lane's uncommitted file, so
the gate failed on content the commit was not making. Run under `tools/surgical_land`, the working
tree IS a clean extract of the tree the commit creates and the check passes by construction; run
against a dirty shared tree it refuses, loudly, instead of judging the wrong thing.

CLAUSE 2 -- PROVABLY FAILABLE. `tests/tools/test_publish_surface_gate.py` drives every refusal
below RED by mutation and asserts the honest path GREEN first, so a permanently-red gate cannot
masquerade as a working one (R15 doctrine). The three killers are addressed by construction:
TAUTOLOGY -- the scope is derived by asking the repo which tests NAME the shipped paths, never
from a list this module also authors; FAIL-OPEN -- an empty derived scope over a non-empty staged
surface is a REFUSAL, not a pass; FAIL-SILENT -- see clause 3.

CLAUSE 3 -- FAILS CLOSED WHEN IT CANNOT RUN. Every one of `git` unavailable, the grep erroring,
`pytest` unavailable, a declared floor control missing from disk, a collapsed scope, and a subject
mismatch returns REFUSE. An unavailable check is a FAILED check. Note the deliberate asymmetry
with `pre_commit_test_gate.data_surface_tests`, whose erroring grep returns nothing and is
bounded by other surfaces: here the derivation is the ONLY thing standing between a bad figure and
the public site, so it has no fail-open branch at all.

WHAT THIS GATE DELIBERATELY DOES NOT DO. It does not run the safety-control set, the level
surface, the store contract, the lint ratchets or the design projections. Those still gate every
commit that stages a code or design path -- including the publisher's own BOOKKEEPING commit,
which is where the map fold, the derived artefacts and the done-markers now go. A content publish
that ships correct figures is no longer blocked by repo hygiene, and repo hygiene is no less
gated than it was.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The roots a content publish SHIPS to a reader. Asserted (in this module's tests) to cover
# `pre_commit_test_gate.PUBLISHED_OUTPUT_ROOTS`, so the exclusion and its counterpart cannot drift
# apart again. `docs/shadow/` and `docs/state/` are the GitHub-Pages mirrors of `site/` and are
# shipped by the same commit, so they belong here even though the exclusion list predates them.
PUBLISH_SURFACE_ROOTS = (
    "site/",
    "docs/reports/",
    "docs/status/",
    "docs/shadow/",
    "docs/state/",
)

# The surface-integrity controls that run on EVERY content publish regardless of what the
# derivation returns -- the floor, and the reason a collapsed derivation is detectable rather than
# quiet. These are the tests that ask whether the PUBLISHED artefact is internally honest (its
# provenance real, its freshness stamp moving, its rendered figures reconciling), as opposed to
# whether some module that reads it is correct. A missing one is a REFUSAL: the control's own
# subject has vanished, which is exactly the fail-silent pattern R15 bans.
SURFACE_FLOOR_TESTS = (
    "tests/background/test_published_provenance_is_real.py",
    "tests/background/test_publish_freshness.py",
    "tests/tools/test_published_provenance_is_real.py",
    "tests/tools/test_website_integrity_fix.py",
    "tests/tools/test_site_reachability.py",
)

# Exit codes, distinguished so a caller can tell "your content is wrong" from "I could not judge
# it". Both refuse the commit; only the first is a statement about the content.
EXIT_OK = 0
EXIT_RED = 1          # the surface's own tests failed
EXIT_CANNOT_RUN = 2   # the gate could not produce a verdict -- fail closed


def _git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd or ROOT), capture_output=True, text=True, timeout=120,
    )


def staged_shipping_paths(cwd: Path | None = None) -> tuple[list[str], str | None]:
    """The staged paths that are SHIPPING surfaces. Returns (paths, error).

    `error` non-None means the gate could not determine its own subject and must refuse -- never
    an empty list standing in for "nothing staged", which is the fail-open this returns a distinct
    signal to avoid.
    """
    if shutil.which("git") is None:
        return [], "git is not available -- the gate cannot read its own subject"
    proc = _git("diff", "--cached", "--name-only", "--diff-filter=ACMRT", cwd=cwd)
    if proc.returncode != 0:
        return [], f"`git diff --cached` failed rc={proc.returncode}: {proc.stderr.strip()}"
    staged = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    return [p for p in staged if p.startswith(PUBLISH_SURFACE_ROOTS)], None


def subject_is_the_commits_tree(paths: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """CLAUSE 1. Does the tree this gate is about to READ equal the tree the commit will CREATE,
    over the shipping paths?

    `git diff --name-only -- <paths>` compares the WORKING TREE to the INDEX. Any output means a
    staged shipping file has been modified since it was staged, so the tests below would be
    judging bytes the commit is not making. That is not a red -- it is an unjudgeable subject, and
    it refuses as one.
    """
    if not paths:
        return True, "no shipping paths staged"
    proc = _git("diff", "--name-only", "--", *paths, cwd=cwd)
    if proc.returncode != 0:
        return False, f"`git diff` over the staged surface failed rc={proc.returncode}"
    drifted = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    if drifted:
        return False, (
            "the working tree and the index disagree on {} staged shipping path(s) -- the gate "
            "would judge content this commit is not making: {}".format(
                len(drifted), ", ".join(sorted(drifted)[:5])
            )
        )
    return True, "subject is the tree this commit creates"


def _tests_naming(needle: str, cwd: Path | None = None) -> tuple[set[str], str | None]:
    """Test files under `tests/` that NAME `needle`. Returns (files, error); an erroring grep is
    an ERROR here, never an empty set -- see clause 3 on the asymmetry with the sibling gate."""
    proc = _git("grep", "-l", "-F", "--", needle, "--", "tests/", cwd=cwd)
    # rc 1 is git-grep's "no matches", which is a real answer; anything else is a broken check.
    if proc.returncode not in (0, 1):
        return set(), f"`git grep` for {needle!r} failed rc={proc.returncode}: {proc.stderr.strip()}"
    found = {
        ln.strip() for ln in proc.stdout.splitlines()
        if ln.strip().endswith(".py") and Path(ln.strip()).name.startswith("test_")
    }
    return found, None


def derive_scope(
    paths: list[str], cwd: Path | None = None
) -> tuple[list[str], list[str], str | None]:
    """The tests that guard these shipping surfaces. Returns (derived, floor, error).

    DERIVED AND FLOOR ARE RETURNED SEPARATELY, and that is load-bearing rather than tidy. The
    first version of this function unioned them and then asked whether the RESULT was empty --
    which it never can be while the floor exists, so the vacuity refusal below was unreachable
    code pretending to be a control. That is the very pattern R15 bans, authored by accident
    inside the gate written to honour R15. The caller now tests the DERIVED half for collapse,
    which is the half that can actually collapse.

    DERIVED, NOT LISTED (the tautology killer): the repo is asked which of its own test files name
    each staged shipping path. Both routes are unioned -- the full repo path AND the bare basename
    -- for the same reason the sibling gate unions them: a test may cite `docs/status/LATEST.md`
    while the module-level fixture that actually reads it writes `LATEST_MD.name`, and basename-as-
    fallback selects the citer and drops the reader.
    """
    root = cwd or ROOT
    derived: set[str] = set()
    for p in paths:
        for needle in (p, Path(p).name):
            found, err = _tests_naming(needle, cwd=cwd)
            if err is not None:
                return [], [], err
            derived |= found
    missing_floor = [t for t in SURFACE_FLOOR_TESTS if not (root / t).exists()]
    if missing_floor:
        return [], [], (
            "declared surface-integrity control(s) absent from the tree: {} -- an unavailable "
            "check is a FAILED check, so this refuses rather than running a smaller floor".format(
                ", ".join(missing_floor)
            )
        )
    return (
        sorted(t for t in derived if (root / t).exists()),
        list(SURFACE_FLOOR_TESTS),
        None,
    )


def evaluate(cwd: Path | None = None) -> tuple[int, str, list[str]]:
    """The whole verdict as data: (exit_code, reason, scope). Pure enough to drive from a test
    fixture with a synthetic repo, which is how every branch below is mutation-proven."""
    root = cwd or ROOT
    paths, err = staged_shipping_paths(cwd=cwd)
    if err is not None:
        return EXIT_CANNOT_RUN, err, []
    if not paths:
        return EXIT_OK, "no shipping surface staged -- nothing for this gate to judge", []

    ok, why = subject_is_the_commits_tree(paths, cwd=cwd)
    if not ok:
        return EXIT_CANNOT_RUN, why, []

    derived, floor, err = derive_scope(paths, cwd=cwd)
    if err is not None:
        return EXIT_CANNOT_RUN, err, []
    if not derived:
        return EXIT_CANNOT_RUN, (
            "VACUITY: {} shipping path(s) staged and NO test in the repo names any of them -- the "
            "floor would still run and report green, which is green over nothing. A surface this "
            "commit ships to a reader with no test that mentions it is the orphan class, not a "
            "fast path: {}".format(len(paths), ", ".join(sorted(paths)[:5]))
        ), floor
    scope = sorted(set(derived) | set(floor))

    probe = subprocess.run(
        [sys.executable, "-m", "pytest", "--version"],
        cwd=str(root), capture_output=True, text=True, timeout=120,
    )
    if probe.returncode != 0:
        return EXIT_CANNOT_RUN, (
            "pytest is not runnable here (rc={}): {}".format(probe.returncode, probe.stderr.strip())
        ), scope

    run = subprocess.run(
        [sys.executable, "-m", "pytest", *scope, "-q", "--tb=short", "-p", "no:cacheprovider"],
        cwd=str(root), capture_output=True, text=True, timeout=1800,
    )
    tail = "\n".join((run.stdout or "").splitlines()[-25:])
    if run.returncode != 0:
        return EXIT_RED, "the published surface's own tests are RED:\n" + tail, scope
    return EXIT_OK, "surface green over {} test file(s)".format(len(scope)), scope


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    code, reason, scope = evaluate()
    label = {EXIT_OK: "✓", EXIT_RED: "❌", EXIT_CANNOT_RUN: "⛔"}.get(code, "?")
    if "--scope" in argv:
        for t in scope:
            print(t)
        return EXIT_OK
    print(f"[publish-surface] {label} {reason}")
    if code == EXIT_CANNOT_RUN:
        print("[publish-surface] REFUSED -- the gate could not produce a verdict, so it does not "
              "give one. An unavailable check is a FAILED check.", file=sys.stderr)
    elif code == EXIT_RED:
        print("[publish-surface] REFUSED -- the figures this commit would publish are not "
              "trustworthy. Fix the surface, not the gate.", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
