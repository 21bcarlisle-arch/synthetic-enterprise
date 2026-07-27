# FINDING — `_file_scope_sha` is inert for directory-scoped atoms (H1 harden-rotation control)

**Status:** QUEUED (SELF_INTERRUPT_DISCIPLINE — registered, not fixed on sight). Not a blocker; fails SAFE.
**Found:** 2026-07-27, during the Rule-0 HARDEN re-verify of `G11_activity_cost_utilisation`.
**Component:** `background/supervisor.py::_file_scope_sha` (the second change-signal of the HARDEN-cooldown rotation, landed in commit `2caa174e5` as the H1 self-HARDEN red-team fix).
**Class label (R9):** observed-with-evidence.

## The claim the fix makes
`2caa174e5` added `_file_scope_sha(atom)` so the HARDEN-cooldown rotation re-offers an
at-target atom when the CODE under its `file_scope` changes — even if a *sibling* atom's
commit moved shared code (e.g. many harness atoms share `background/supervisor.py`) and only
appended its note to the sibling's map entry, leaving this atom's `_atom_content_sha` untouched.
The docstring states this "closes a real blind spot … keying on file_scope contents re-offers
on ANY such change — exactly the docstring's stated intent."

## The defect (observed with evidence)
`_file_scope_sha` calls `read_bytes()` on each `file_scope` entry. When an entry is a
**directory** (`background`, `tools`, `site`, `docs/design`, `simulation`, `interface`, …),
`read_bytes()` raises `IsADirectoryError` (an `OSError`), the entry is skipped, `saw` stays
`False`, and the function returns `""` — the documented FAIL-OPEN. So for every atom whose
`file_scope` lists directories rather than individual files, the new "shared-code moved →
re-offer" signal is **silently inert**; the cooldown falls back to atom-content + the 6h timer,
i.e. the exact blind spot `2caa174e5` claims to have closed.

Measured against the live map (2026-07-27):
- **21 of 135** atoms with a non-empty `file_scope` get an empty `scope_sha` (signal inert),
  including `G11`, `H14`, `H17`, `H18`, `H20`, `H21`, `H22`, `H23`, `G4`, `G7`–`G11`, `A8`,
  `SITE1`, `W2_11`, `W4_4`, `B5`, and more.
- These are disproportionately the **harness atoms that share `background/supervisor.py`** —
  precisely the shared-code population the fix was built to protect. `H1` itself works only
  because its `file_scope` happens to name individual `.py` files; the sibling atoms that share
  the same code do not.

The failure direction is SAFE: an inert signal *under-offers* a re-verify (suppresses for up to
`HARDEN_COOLDOWN_HOURS`), it never over-claims freshness. So this is not a WALL and not a
blocker — but the docstring's honesty claim ("closes the blind spot / re-offers on ANY change")
is FALSE for directory scopes, and the sibling-shared-code case it was written for is exactly
where it stays inert.

## Proposed fix (for a future H1 BUILD draw, with R15)
When a `file_scope` entry is a directory, hash the directory's tracked files (e.g. walk
`git ls-files <dir>` and fold each blob) rather than skipping it. Keep the FAIL-OPEN `""` only
for a genuinely absent/empty scope. **R15 requirement:** a mutation test must prove the signal
FIRES — a commit that touches a shared directory-scoped file must flip `scope_sha` for a
directory-scoped atom (today it does not), and the current all-directories-return-`""` behaviour
must be shown to FAIL that test before the fix.

## Why not fixed here
This was found while HARDEN-re-verifying `G11` (a different atom); the fix is BUILD on the H1
rotation mechanism and needs its own R15 mutation proof. SELF_INTERRUPT_DISCIPLINE: QUEUE by
default, INTERRUPT only when the machine is genuinely blocked — it is not (fails safe). Sibling
to [[feedback_audit_sibling_half_for_hardened_class]]: the H1 fix hardened the file-scoped half;
this is the un-hardened directory-scoped half of the same signal.
