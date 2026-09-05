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
  background/finding_classes.py   HOLED, with the second-order shape intact. Deleting a class
                                  from `CLASSES` returned `check()` clean. Delete the class
                                  DOCUMENT and `check()` refuses `MISSING CLASS DOC`; delete the
                                  class row as well and the refusal goes. Wired here.
  docs/design/maturity_map.yaml   HOLED for a leaf. 314 atoms, 175 of which nothing names in
                                  `depends_on`/`couples_with`/`blocked_on`; deleting one
                                  returned 0 violations from all five facet checks. The map is
                                  protected only by the ACCIDENT of an atom being referenced,
                                  which is not a control. Wired here.
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
