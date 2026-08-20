#!/usr/bin/env python3
"""
REUSE: background/staging_two_rooms_repair.py
CLASS: CUSTOM
INDEX: searched "two rooms", "staging duplicate", "archive", "consolidation", "resurrected".
       `background/finding_classes.py` DETECTS this exact state -- its `--check` prints "TWO
       ROOMS ... present in done AND root" and returns non-zero, which is what refuses the
       commit. It is deliberately NOT extended: detection and repair want opposite failure
       directions. A detector should be eager (report anything suspicious); a repairer that
       deletes files must be timid (act only on the provably redundant case). Folding a
       deleting action into the module whose job is to shout would make the shout load-bearing.
       `background/staging_archive_policy.py` MOVES exhaust into done/ and already refuses when
       the destination exists (returning "already_there"/"conflicts" and touching nothing),
       which is correct for it and is why the duplicate persists rather than being created by
       it. This is the missing third piece: the one that resolves what that policy declines to.

THE TWO-ROOMS STATE, REPAIRED INSTEAD OF REPORTED.

Director instruction, 2026-08-19: "the recurring fault that keeps refusing commits: the process
re-creating an archived finding hourly. Four manual clears is three too many."

WHAT HAPPENS. A finding exists in `docs/staging/` AND `docs/staging/done/`. The two rooms make
mutually exclusive claims -- live versus consumed -- and the doorbell reads the ROOT copy, so
the tree is refused by `finding_classes --check` until a human deletes one. On 2026-08-19 that
happened four times in six hours and each clear cost a gate run, because the refusal lands on
EVERY commit in the tree, including other lanes' and including the publisher's.

I DID NOT IDENTIFY WHAT RE-CREATES THE FILE, and I am not going to name a cause I cannot show.
What was ruled out, by reading the code rather than by assuming: `surgical_land` builds its tree
through a TEMPORARY index (`GIT_INDEX_FILE`) with a `read-tree` that has no `-u`, so it never
writes the working tree; `process_run_complete._refresh_checkout_to` runs `read-tree -u --reset`
against a SEPARATE checkout directory, not the repo; and `staging_archive_policy` declines to act
at all when the destination exists. What is observed: the file reappeared at 10:20 and 11:25, and
stopped reappearing once its deletion was COMMITTED rather than merely made in the working tree.
That is consistent with something restoring a tracked-but-deleted path from HEAD, and consistent
with a tick re-writing the finding, and I cannot separate the two from the evidence I have.

SO THIS REPAIRS THE STATE RATHER THAN THE WRITER. That is the weaker fix and it is the right one
to build first: it holds whichever of those two causes is real, and it holds for the next
duplicate whose cause is a third thing. If the writer is later identified, this stays useful --
a repair is not made redundant by removing one of its triggers.

TIMID BY CONSTRUCTION, because it DELETES. It acts on exactly one case: the root copy's content
is wholly contained in the archived copy, so the root file carries nothing the archive lacks.
That predicate held for both real instances -- the archived copies were the root text plus a
discharge section appended. Anything else is reported as a CONFLICT and left alone, because a
repairer that deletes on uncertainty is worse than the refusal it is fixing.

IT STAGES THE DELETION, which is the half that makes it stick. Removing the file from the
working tree alone leaves the path tracked at HEAD, and every operation that restores a tracked
path can bring it back -- which is the shape of the observed recurrence. `git rm` ends that.

THERE ARE THREE ROOMS, AND THIS KNEW TWO (2026-08-20). The name was the defect. `finding_classes`
refuses on ALL THREE PAIRINGS -- its own docstring says so, and it was widened to do that on
2026-08-12 after a hand census run root-vs-`done/` declared zero while root-vs-`in_progress/` held
one. This repairer was built on 2026-08-19, AFTER that widening, and still paired root against
`done/` only. So the room CLAUDE.md instructs you to park an open finding in was the one room the
repair could not see.

Measured live, with one duplicate of each shape present at once: the detector reported two
failures; `repair()` cleared the `done/` one and returned `{'changed': True, 'verdict': 'removed 1
redundant staging copy'}` WITH NO ALARM, while the tree stayed refused by the pairing it is blind
to. That is the fail-silent shape from R15, in the report rather than the check -- the verdict
could not distinguish "I cleared everything" from "I cleared the half I can see", and the worker
loop would have gone on reporting that success hourly.

The live instance is the one that shows why the timidity above is load-bearing. The root copy of
the ghost-pages finding was a RESURRECTION, byte-identical to the pre-move version at the parent
commit, while the `in_progress/` copy carried a prepended correction; so the root text is NOT
contained in the parked text, `classify` returns CONFLICT, and the right output is a shout, not a
delete. Widening the room set does not widen what this deletes.

`done/`-vs-`in_progress/` is the third pairing and has NO root copy to remove. Nothing here is
safely deletable, so it is reported rather than repaired -- but it must be REPORTED, because the
detector refuses the tree on it and silence from the repairer reads as "clear".
"""
from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
DONE_DIR = STAGING_DIR / "done"

#: The rooms that are not the root. Kept in step with `finding_classes.ARCHIVE_DIRNAME` /
#: `PARKED_DIRNAME` -- the detector refuses on all three pairings, so a repairer that knows
#: fewer rooms than the detector can only ever clear part of what the detector refuses on.
ARCHIVE_DIRNAME = "done"
PARKED_DIRNAME = "in_progress"
OTHER_ROOMS = (ARCHIVE_DIRNAME, PARKED_DIRNAME)

SAFE = "redundant"
CONFLICT = "conflicts"


def duplicates(staging: Path | None = None) -> list[tuple[str, Path, Path]]:
    """(name, root_copy, other_copy) for every doc present in the ROOT and some other room.

    One row per PAIRING, so a doc sitting in all three rooms yields two rows; `repair` groups
    them back by root copy. Only pairings involving the root are returned, because the root copy
    is the only one this may delete -- it is the room that rings the doorbell and wins draws.
    """
    root_dir = Path(staging) if staging is not None else STAGING_DIR
    out = []
    for p in sorted(root_dir.glob("*.md")):
        for room in OTHER_ROOMS:
            other = root_dir / room / p.name
            if other.is_file():
                out.append((p.name, p, other))
    return out


def unrepairable_pairings(staging: Path | None = None) -> list[str]:
    """Names present in `done/` AND `in_progress/` but NOT in the root.

    The third pairing. There is no root copy to remove, so nothing here is deletable by a
    repairer this timid -- but the detector refuses every commit in the tree on it, so it is
    carried into `conflicts` to be shouted. Passing over it silently is what makes a repair
    report indistinguishable from a clean tree.
    """
    root_dir = Path(staging) if staging is not None else STAGING_DIR
    done_dir, parked_dir = root_dir / ARCHIVE_DIRNAME, root_dir / PARKED_DIRNAME
    if not (done_dir.is_dir() and parked_dir.is_dir()):
        return []
    return sorted(
        p.name for p in done_dir.glob("*.md")
        if (parked_dir / p.name).is_file() and not (root_dir / p.name).is_file()
    )


def classify(root_copy: Path, archived: Path) -> str:
    """SAFE only when the archived copy already contains everything the root copy says."""
    try:
        r = root_copy.read_text(encoding="utf-8", errors="replace").strip()
        a = archived.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return CONFLICT
    if not r:
        return SAFE
    return SAFE if r in a else CONFLICT


def _git_rm(path: Path) -> bool:
    """Stage the removal so the path stops being tracked. Falls back to unlink for a file git
    does not know about, which is not an error -- an untracked duplicate is still a duplicate."""
    try:
        r = subprocess.run(["git", "rm", "-q", "-f", "--", str(path.relative_to(PROJECT_DIR))],
                           cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            return True
    except Exception:  # noqa: BLE001
        pass
    try:
        path.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def repair(staging: Path | None = None) -> dict:
    """Resolve every SAFE duplicate; report the rest. Never raises into a caller's path."""
    repaired, conflicts = [], []
    # Read the third pairing BEFORE the loop below deletes anything. It keys on the ABSENCE of a
    # root copy, and a successful repair creates exactly that absence -- so scanning afterwards
    # makes every all-three-rooms repair re-report as an unrepairable pairing, a control reding
    # on its own success case. The question is what the tree looked like when we found it.
    rootless = unrepairable_pairings(staging)
    by_root: dict[tuple[str, Path], list[Path]] = {}
    for name, root_copy, other in duplicates(staging):
        by_root.setdefault((name, root_copy), []).append(other)
    for (name, root_copy), others in by_root.items():
        # SAFE against ANY room is enough: that room already holds everything the root says,
        # so the root copy carries nothing that deleting it would lose.
        if any(classify(root_copy, o) == SAFE for o in others):
            if _git_rm(root_copy):
                repaired.append(name)
            else:
                conflicts.append(name)
        else:
            conflicts.append(name)
    conflicts.extend(rootless)
    return {"repaired": sorted(repaired), "conflicts": sorted(set(conflicts))}


def observe() -> dict:
    """Worker-loop entry, shaped like the headroom governors. R5: silent when nothing moved."""
    try:
        res = repair()
    except Exception as exc:  # noqa: BLE001 - a repair must never take the worker down
        return {"changed": True, "alarm": f"TWO-ROOMS REPAIR FAILED: {exc}"}
    if not res["repaired"] and not res["conflicts"]:
        return {"changed": False}
    out = {"changed": True, "verdict": f"{len(res['repaired'])} repaired"}
    if res["repaired"]:
        out["verdict"] = (
            f"removed {len(res['repaired'])} redundant staging copy/copies already archived: "
            + ", ".join(res["repaired"])
        )
    if res["conflicts"]:
        out["alarm"] = (
            "TWO ROOMS, NOT SAFELY REPAIRABLE (no copy is provably redundant -- either the root "
            "copy carries text the other room lacks, or the pair is done/-vs-in_progress/ with "
            "no root copy to remove): " + ", ".join(res["conflicts"])
            + " -- resolve by hand; every commit in the tree is refused until then."
        )
    return out


def main() -> int:
    import sys
    res = repair() if "--repair" in sys.argv else {
        "repaired": [],
        "conflicts": [n for n, r, a in duplicates() if classify(r, a) == CONFLICT],
    }
    if "--repair" not in sys.argv:
        dupes = duplicates()
        print(f"{len(dupes)} duplicate(s) across both staging rooms.")
        for name, r, a in dupes:
            print(f"  {classify(r, a):10s} {name}")
        return 1 if dupes else 0
    for n in res["repaired"]:
        print(f"repaired (removed redundant root copy, deletion staged): {n}")
    for n in res["conflicts"]:
        print(f"CONFLICT (left alone, resolve by hand): {n}")
    return 1 if res["conflicts"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
