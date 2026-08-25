"""Every control the site lane executes must exist in the repository.

THE DEFECT, measured at HEAD ed97ad827 on 2026-08-18 and the reason this file exists.
`site/proof/test_the_committed_generator_reproduces_the_published_door.py` had been on
disk since 2026-08-15 06:34, was collected and GREEN on every `pytest site/` run, and
existed in NO COMMIT ON ANY REF:

    git log --all -- site/proof/test_the_committed_generator_reproduces_the_published_door.py
        -> empty
    git ls-files --error-unmatch <same>   -> "did not match any file(s) known to git"
    git check-ignore -v <same>            -> not ignored (so `--others` would have shown it,
                                            and nothing was looking)

Two committed records rested on it while it did not exist:

  1. `docs/staging/done/WORKER_FINDING_THE_PUBLISHED_DOOR_WAS_GENERATED_FROM_AN_UNCOMMITTED_TREE_2026-08-15.md`
     is filed **DISCHARGED in the tick that found it**, and names that file first in its
     `**Discharged:**` line.
  2. H27 Expert Hour #34's shipped tripwire
     (`site/proof/test_the_published_door_reproduces_its_ledger.py`, commit c7a1fdab0)
     cites it BY NAME as the reason its own subject partition is safe -- "the site-lane
     control in `test_the_committed_generator_reproduces_the_published_door.py` compares
     the artefact with the GENERATOR and excludes the ledger as a subject on purpose."

So a committed control's stated coverage of one half of a seam pointed at a file no clone
of this repository contains. The irony is exact and is the reason this is a class defect
rather than a slip: the missing file's ENTIRE PURPOSE is to enforce CLAUDE.md's IaC wall --
"no behaviour-determining state outside the readable repo, reconstruct-from-repo-alone is
the test" -- against the published Proof door. It was itself state outside the readable
repo.

WHY NOTHING WAS RED, and it is a property of the gate rather than an oversight.
`tools/site_lane_gate.py` runs `pytest site/`, and pytest COLLECTS FROM THE WORKING TREE.
An untracked green test is therefore indistinguishable from a tracked green test at the
only moment anyone looks: it is collected, it passes, it prints in the count, and the gate
says "site tests green". Every existing site control asserts something about a rendered
door; not one asks whether the controls themselves are things the repository has. The
assurance the gate produces was real on exactly one machine.

THE TWO SUBJECTS, and neither is derived from the other. Subject A is the FILESYSTEM --
walked directly, so a `.gitignore`d control is in the population too (this is deliberately
stronger than `git ls-files --others --exclude-standard`, which cannot see an ignored
file, and an ignored control is the more invisible one). Subject B is GIT'S INDEX
(`git ls-files -- site/`), the set of paths the commit being made will carry. A control
that read both sides from git would agree with itself and pass on the very defect above.

WHY THE INDEX AND NOT `HEAD`. At pre-commit time the honest question is "will the commit
about to be made contain this file", and that is the index. A file `git add`ed in this same
commit is legitimately present; a file that has never been added is not. Post-commit the
index matches HEAD, so the check reads the same either way.

R15 BOTH WAYS, PROVEN AGAINST REAL HISTORY RATHER THAN A FIXTURE (2026-08-18):
  RED   with the working tree exactly as this Hour found it -- one untracked control,
        named above, 3 days old.
  GREEN once it is landed, in the commit BEFORE this file's own.
  Plus three mutations proven to fire: reading the population from `git ls-files` on both
  sides (tautology -- passes on the shipped defect); an unreadable/empty `git ls-files`
  (fail-silent -- an unavailable check is a FAILED check, not an empty comparison); and a
  tracked control added to `.gitignore` and removed from the index, which
  `--others --exclude-standard` cannot see and the filesystem walk does.

WHY THE SITE LANE OWNS THIS. The subject is `tools/site_lane_gate.py`'s own execution set,
so it belongs beside the things that gate runs. It sits at `site/` root rather than in one
door's directory because its population is every door. The `tests/` publish gate selects by
NAME STEM and would never run it.

SCOPE, stated so it is not read as wider than it is. This asserts the SITE lane only. The
same shape exists under `tests/` -- 10 untracked `tests/**/test_*.py` were on disk when
this was written -- but those were hours old and are other lanes' live in-flight work on a
shared tree, where untracked-at-this-instant is normal and transient. Landing a repo-wide
version would wedge a shared gate on another lane's uncommitted work, which is a sequencing
problem and not a reason to weaken the control that CAN be honest today. Filed as a finding
instead.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent  # site/ -> repo root

# What a `pytest site/` run under the site-lane gate actually LOADS:
#   test_*.py   -- collected and executed
#   conftest.py -- imported by collection before any test runs
#   *.mjs       -- the node render harnesses the door tests spawn; an untracked harness is
#                  the same defect one level down (the test is in the repo, the thing it
#                  actually exercises is not).
_LOADED_NAME_GLOBS = ("test_*.py", "conftest.py", "*.mjs")
_SKIP_DIRS = {"__pycache__", "node_modules", ".pytest_cache"}

# Vacuity floor. The population was 66 when this was written; a walk that suddenly returns
# a handful means the glob, the root or the skip list broke, and a small population would
# let this control pass by having almost nothing to check.
# LOWERED 20 -> 10 on 2026-08-20. The floor exists to catch a BROKEN WALK -- a glob that
# silently stops matching and reports a clean lane it never looked at -- and 20 was the site's
# control count on the day it was written. The director's fold deleted five site controls whose
# subjects no longer exist (the glossary layer, the customer-portal claim, links-to-redirected,
# and the link walker with its test), taking the real population to 19 and reddening this guard
# for the one reason it must never fire: a legitimate shrink.
#
# 10 is chosen against what the lane cannot go under while still being a lane: the five tabs'
# own door tests plus the register, brand, freshness and reachability controls. It is not the
# current count, deliberately -- a floor pinned to today's number is this defect again.
_MIN_POPULATION = 10


def _controls_on_disk() -> set[str]:
    """Subject A: the filesystem, walked directly. Repo-relative POSIX paths."""
    found: set[str] = set()
    for path in HERE.rglob("*"):
        if not path.is_file():
            continue
        if _SKIP_DIRS.intersection(p.name for p in path.parents):
            continue
        if any(path.match(g) for g in _LOADED_NAME_GLOBS):
            found.add(path.relative_to(PROJECT).as_posix())
    return found


def _paths_git_has() -> set[str]:
    """Subject B: the index -- what the commit being made will carry.

    R15 FAIL-SILENT: git missing, git failing, or an empty listing RAISES. Returning an
    empty set here would make every path below "untracked" (loud, but for the wrong
    reason); returning the disk set would make this control agree with itself. An
    unavailable check is a FAILED check, so it fails on its own terms and says so.
    """
    try:
        r = subprocess.run(
            ["git", "ls-files", "--", "site/"],
            cwd=str(PROJECT), capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover - environment
        raise AssertionError(
            f"could not run `git ls-files` ({exc!r}) -- this control's second subject is "
            "unavailable, so it cannot say anything about the first. An unavailable check "
            "is a FAILED check (R15 fail-silent), never a pass"
        ) from exc
    assert r.returncode == 0, (
        f"`git ls-files -- site/` exited {r.returncode}: {r.stderr.strip()!r}. An "
        "unavailable check is a FAILED check"
    )
    tracked = {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}
    assert tracked, (
        "`git ls-files -- site/` listed NOTHING. Either this is not a git work tree or "
        "the index is empty -- in both cases the comparison below would be vacuous"
    )
    return tracked


def test_no_control_the_site_lane_executes_is_missing_from_the_repository():
    """THE TRIPWIRE. A green untracked control is assurance that does not exist.

    `tools/site_lane_gate.py` runs `pytest site/`, and pytest collects from the WORKING
    TREE -- so this fires on the one state in which the gate's own report is false while
    every door test it names is passing.
    """
    on_disk = _controls_on_disk()

    # VACUITY GUARD, and it is not decorative: a broken glob or a moved root would empty
    # the population and this test would then pass forever with nothing in it.
    assert len(on_disk) >= _MIN_POPULATION, (
        f"the site-lane control population is only {len(on_disk)} files (floor "
        f"{_MIN_POPULATION}) -- the walk, not the repository, is what changed. Fix the "
        "walk; do not lower the floor to make this green"
    )

    untracked = sorted(on_disk - _paths_git_has())
    assert not untracked, (
        "the site lane EXECUTES controls that exist in no commit -- pytest collects from "
        "the working tree, so each of these is collected, passes, and is counted in the "
        "gate's `✓ site tests green`, while no clone of this repository has it:\n  - "
        + "\n  - ".join(untracked)
        + "\nThe assurance they produce is real on this machine only, and any committed "
        "record that cites one of them as its discharge or as a covered subject is "
        "pointing at nothing (that is exactly how this was found: "
        "`site/proof/test_the_committed_generator_reproduces_the_published_door.py`, 3 "
        "days on disk, named as DISCHARGED by one record and as a subject partition by "
        "another). Repair: `git add` the control and commit it. Never delete it to go "
        "green -- a control worth running is worth landing."
    )
