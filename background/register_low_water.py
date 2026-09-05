"""THE LOW-WATER MARK OF A REGISTER — the third question to ask of any control shaped
`for key in register`.

WHY THIS EXISTS. `removed_dispositions()` landed on the alarm census on 2026-09-05
(`dc5fcbbc8`) after a measurement showed that deleting a disposition row AND its hit together
returned clean from all five rungs then in place. Its argument was never about the census: any
control written as `for key in register` has **the register as its subject set**, so a key in
neither the derived hits nor the stored rows is the subject of nothing. The register is a
high-water mark, and nothing keeps a high-water mark from falling.

THE SECOND-ORDER SHAPE, which is why this is worth centralising rather than a missing rung
somewhere. Where a sibling control REFUSES on a row — `MISSING CLASS DOC`, `UNBOUND`, an
eroded hit — **deleting that row is the cure for the refusal.** A red clearable by deleting
the evidence is a fail-open with an extra step, and every other rung goes on reporting a clean
class. It has already happened here twice: `9857c0edb` rewrote the census register from a
pre-sweep copy and deleted 33 annotations while every rung stayed green.

MEASURED 2026-09-05, before this module existed, on the four registers the direction named:

  docs/design/canon_claims.yaml   PROTECTED, but only in the test suite. `canon_drift_check`
                                  itself exits 0 after a claim is deleted (measured: 14 claims
                                  -> 13, drift []). `EXPECTED_CLAIM_IDS` in
                                  `tests/tools/test_canon_drift_check.py` is a literal pin and
                                  it does catch the deletion. Crude — it refuses ADDITIONS too,
                                  deliberately — but it is a real low-water mark, so this module
                                  does not wire it and the pin stays as the one that guards it.
                                  CORRECTED 2026-09-05, beside the row rather than over it: read
                                  that verdict as TOOL HOLED / SUITE PINNED. "Protected" read the
                                  strongest control over the register and never asked which one
                                  the enforcement path reaches. Another lane wired
                                  `removed_claims()` into `canon_drift_check` in `605ec3995`
                                  while this measurement was in flight, so the tool is no longer
                                  blind — but it was, and the recommendation above was wrong.
                                  CORRECTED AGAIN 2026-09-05, beside both rows rather than over
                                  them: "this module does not wire it" is no longer true either.
                                  `removed_claims()` was a hand-rolled SECOND implementation of
                                  everything below, and it now calls `removed_rows()`/
                                  `keys_at_head()`. The literal pin in the suite stays as the
                                  crude second belt it always was.
  background/finding_classes.py   HOLED, with the second-order shape intact. Deleting a class
                                  from `CLASSES` returned `check()` clean. Delete the class
                                  DOCUMENT and `check()` refuses `MISSING CLASS DOC`; delete the
                                  class row as well and the refusal goes. Wired here.
  docs/design/maturity_map.yaml   HOLED for a leaf. 314 atoms, 175 of which nothing names in
                                  `depends_on`/`couples_with`/`blocked_on`; deleting one
                                  returned 0 violations from all five facet checks. The map is
                                  protected only by the ACCIDENT of an atom being referenced,
                                  which is not a control. CORRECTED 2026-09-05: this row said
                                  "Wired here" on the day it landed and nothing wired it —
                                  `grep -rn register_low_water` returned `finding_classes` and a
                                  test, and the same commit's own message said, correctly,
                                  "measured and written up, NOT wired". The claim is now TRUE by
                                  the work rather than by the sentence: wired at
                                  `tools/level_promotion_gate.low_water_failures()`, whose
                                  baseline is the UNION of the map's two halves (the live half
                                  alone reads the 2026-08-26 split as 224 deletions and every
                                  honest `refile()` as one more), with the retirement reason
                                  living in `docs/design/maturity_map_retired.yaml`. That file is
                                  itself append-only, escapable only by the atom returning to the
                                  map, which is what stops the regress of a reason for retiring a
                                  reason. Measured over 1,023 map revisions before building: the
                                  union had already fallen 22 atoms in 3 commits, two of them
                                  unmentioned anywhere.
  tools/domain_constant_origins   NOT THIS SHAPE, and saying so is the finding. Its subject set
                                  is derived from `scan()` over the source, so "deleting a row"
                                  means deleting the constant — the carrier itself. That is an
                                  honest change, not the erasure of the record that a carrier
                                  ever existed. Nothing is wired for it.

NO SUBJECT-SHAPE EXCEPTION, AND THAT IS THE DESIGN. The tempting rule is "allow the removal if
the register's subject is gone from the tree anyway". That is exactly the fail-open above: a
genuinely retired subject and a derivation gone blind are the same observation from the
register alone. Only an authored sentence separates them, so the only way out is a retirement
reason. Same shape, and the same argument, as `_retired` on the census.

WHERE IT BITES. The baseline is HEAD, so this is a commit-time ratchet against the WORKING
copy: you cannot drop a row in a commit without saying why. Once a bad commit has landed, HEAD
contains the loss and this goes quiet — said plainly rather than implied, because the gates run
pre-commit on the working tree and that is the whole enforcement point.

THE FOUR CALL SITES, as of 2026-09-05. There is one implementation of this mechanism and this is
it; a fifth register joins by CALLING, never by copying.

  docs/design/self_clearing_alarm_dispositions.json  self_clearing_alarm_census.removed_dispositions
  background/finding_classes.py CLASSES              finding_classes.removed_classes
  docs/design/maturity_map.yaml                      level_promotion_gate.low_water_failures
  docs/design/canon_claims.yaml                      canon_drift_check.removed_claims

WHAT THE CONVERGENCE ITSELF MEASURED, because it is not what convergence is usually sold on.
Mutating `keys_at_head`'s `return None` to `return frozenset()` — the never-empty contract, the
whole difference between "HEAD's register was empty" and "I cannot answer" — SURVIVED in all four
suites while the canon still had its own copy of the reader. The one test of that contract in the
tree was pointed at the copy. Re-pointing the canon did not just delete a duplicate; it moved the
only proof of this module's central refusal onto the reader every register now shares. Written up
in docs/staging/records/SEAT_RESULT_THE_CONVERGENCE_PROVED_A_CONTRACT_THAT_HAD_BEEN_PROVED_NOWHERE_2026-09-05.md.

SUPERSEDED 2026-09-05, beside the paragraph rather than over it, because the paragraph above is
what a later direction was drawn from and the direction is now WRONG. That record closed by saying
the coverage "rests on a test living in the CANON's file", and that MOVING it beside this module
was "a small honest tidy that nothing here depends on". Both halves have since stopped being true,
and moving it would now DELETE a proof rather than relocate one.

  WHAT CLOSED THE GAP. `38871422b` added
  `tests/background/test_the_shared_low_water_reader_refuses_rather_than_reading_empty.py`, which
  drives this reader directly. Re-measured 2026-09-05 against that file ALONE, each mutation
  applied singly with its anchor asserted present-and-unique and `__pycache__` cleared between
  runs: `except (OSError, SubprocessError)`, `returncode != 0`, `except Exception` and
  `keys is None` — all four `return None` branches — each RED it. Nothing about this module's
  never-empty contract depends on the canon's file any more.

  WHY THE MOVE IS NOW A REGRESSION, which is the part no reading of the file would tell you.
  `test_THE_HEAD_READER_ITSELF_returns_None_and_never_an_empty_set` changed SUBJECT under the
  convergence. It no longer proves what this reader returns — the file above does that. It is the
  only thing in the tree that proves the canon's SEAM (`canon_drift_check._claim_ids_at_head`)
  carries the refusal THROUGH instead of swallowing it. Measured: re-hand-roll that seam to
  `frozenset() if out is None else out` and it is the sole test that reds, while the shared file
  stays green throughout. A test whose subject is the seam belongs in the seam's suite. The
  equivalent leg for the class register's seam exists and was confirmed by the same method
  (`test_an_unestablishable_baseline_is_a_refusal_and_never_a_clean_result`).

  STILL OPEN, and named rather than implied: the census seam `_dispositions_at_head` has not been
  put to the same question. It could not be this turn — another lane holds
  `self_clearing_alarm_census.py` dirty in the shared tree with `removed_dispositions` deleted
  locally (14 red), so any mutation verdict from its suite is uninterpretable. Ask it once that
  lane lands. Measurements written up in
  docs/staging/records/SEAT_RESULT_THE_TEST_THE_DIRECTION_WANTED_MOVED_HAD_ALREADY_CHANGED_SUBJECT_2026-09-05.md.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Iterable

PROJECT_DIR = Path(__file__).resolve().parent.parent


def keys_at_head(rel_path: str,
                 extract: Callable[[str], Iterable[str] | None],
                 *,
                 project_dir: Path | None = None) -> frozenset[str] | None:
    """The register's key set as HEAD has it, or None when that cannot be established.

    RETURNS None, NEVER `frozenset()`. The two are opposite claims: an empty set says "HEAD's
    register was empty, so nothing can have been removed" and would report clean on every tree
    without git, which is the fail-silent shape this module exists to refuse. The caller turns
    None into a refusal that names itself.

    `git show HEAD:<path>`, not a working-tree read: the point is to compare the working copy
    against the last committed judgement, and it resolves correctly from a linked worktree,
    which is the only environment `seat_executor` runs in.

    `extract` is handed HEAD's raw TEXT and must not import or exec it — a register that lives
    in a Python module is parsed, never executed, because running HEAD's copy of a module to
    find out what HEAD's copy declares is a route for HEAD to decide whether it is checked.
    """
    root = PROJECT_DIR if project_dir is None else Path(project_dir)
    try:
        proc = subprocess.run(["git", "show", "HEAD:{}".format(rel_path)],
                              cwd=root, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        keys = extract(proc.stdout)
    except Exception:
        # An unparseable baseline is an UNESTABLISHED baseline, not an empty one. Swallowing the
        # exception into `frozenset()` here would be the fail-silent this module refuses, one
        # level down from the caller that is careful about it.
        return None
    if keys is None:
        return None
    return frozenset(keys)


def removed_rows(*,
                 register: str,
                 current: Iterable[str],
                 baseline: frozenset[str] | None,
                 retired: dict[str, str] | None,
                 row_is: str,
                 retire_with: str) -> list[str]:
    """Keys that were in the register at HEAD and are not in it now, without a named reason.

    `register` names the register in the refusal so a reader of a mixed report knows which one
    spoke. `row_is` says in one clause what a row RECORDS, because the whole argument for
    refusing a deletion is that the row is the only record its subject was ever in the class.
    `retire_with` names the exact escape hatch to add, since a refusal that does not say how to
    clear itself gets cleared the wrong way.
    """
    if baseline is None:
        return ["{}: the register's baseline at HEAD could not be established (git show "
                "failed, or HEAD's copy is absent or unparseable), so whether a row has been "
                "removed cannot be answered -- this is a refusal, not a clean result".format(
                    register)]
    ret = retired or {}
    out: list[str] = []
    for key in sorted(baseline - set(current)):
        # `or ""` BEFORE `str`, not `.get(key, "")`: a retirement entry carrying an explicit
        # JSON/YAML `null` stringifies to "None", which is truthy, and the reason requirement
        # falls open. The same slip was live in three census rungs until 2026-09-05; an
        # absurdity is fixed as a class, so this escape hatch is born with the treatment.
        if not str(ret.get(key) or "").strip():
            out.append(
                "{}: `{}` was in the register at HEAD and is not in it now, and nothing says "
                "why. {} Removing the row removes the only alarm that its subject went. "
                "Restore it, or add {} naming what took the subject out of the tree.".format(
                    register, key, row_is, retire_with.format(key=key)))
    return out
