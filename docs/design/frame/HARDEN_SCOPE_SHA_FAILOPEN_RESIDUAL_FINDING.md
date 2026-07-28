# Finding — HARDEN cooldown `scope_sha` fail-open residual (empty/dir-only file_scope)

**Status:** QUEUED red-team finding (not fixed on sight — SELF_INTERRUPT_DISCIPLINE). Surfaced
2026-07-28 while red-teaming `ARCH1_internal_seams`'s HARDEN invariants under a Rule-0 self-refill draw.
**Severity:** LOW (24h-time re-offer still fires; only the *scope-change* re-offer trigger is defeated).
**Class, not instance (R10).**

## The invariant that is not delivered

`background/supervisor.py::_file_scope_sha` was built 2026-07-27 (H1 self-HARDEN red-team) to close a real
blind spot: many harness atoms SHARE a source file (e.g. `background/supervisor.py`) in `file_scope`, so a
commit that hardens a SIBLING atom moves the shared code but appends its note to the *sibling's* map entry,
leaving this atom's `_atom_content_sha` untouched. Keying the cooldown on `file_scope` *contents* is meant
to re-offer the atom on ANY change to code under its control — the docstring's stated intent, *"a commit
touched its file_scope -> re-verify."*

That guarantee is **only delivered for atoms whose `file_scope` actually names their source files.** For an
at-target atom whose `file_scope` is `[]` (or contains bare directories that don't resolve to files),
`_file_scope_sha` returns `''` (its documented FAIL-OPEN), so `_harden_in_cooldown` skips the scope check and
falls back to atom-content-note + 24h time. The fail-open direction is safe (never *suppresses* a draw), but
the atom's controlled source can regress with **no scope-triggered re-verify** — exactly the blind spot the
mechanism exists to close, still open for these atoms.

## Class members (at-target HARDEN-surface atoms, verified 2026-07-28)

Of 33 at-target surface atoms, 3 have real `.py` source in `evidence` but a `file_scope` that yields
`_file_scope_sha == ''`:

| atom | file_scope | evidence `.py` source (real, exists) |
|------|-----------|--------------------------------------|
| `ARCH1_internal_seams` | `[]` | `company/interfaces/internal_seams.py`, `tools/internal_seam_verifier.py`, `tests/tools/test_internal_seam_verifier.py` |
| `A1_learn_loop_chair` | `[]` | 2 source files |
| `G11_activity_cost_utilisation` | `['background','tools','site','docs/design']` (bare dirs) | 4 source files |

(`W3_1_price_cap_binding` also yields `''` but has NO `.py` source in evidence — no controlled code to track,
so its `''` is correct, not a gap.)

Two distinct sub-causes: **(a)** empty `file_scope` despite real source (`ARCH1`, `A1`); **(b)** bare-directory
entries that `_file_scope_sha`'s per-file `read_bytes` cannot resolve, so `saw` stays False (`G11`) — the same
bare-dir-vs-file class as the 2026-07 H6 `^(sim)/` bare-dir fail-open.

## Proposed class-fix (needs its own atom + R15 proof — do NOT drive-by)

Options, to be adjudicated when the H-lane opens:
1. **Populate `file_scope`** for `ARCH1`/`A1` from their evidence `.py` files, and expand `G11`'s bare dirs to
   the actual controlled files. Cleanest per-atom, but changes `_files_disjoint` concurrency gating
   (blast radius — must re-verify multi-atom draw disjointness).
2. **Extend `_file_scope_sha`**: when `file_scope` is empty/unresolvable, fall back to hashing the evidence
   `.py` source files; and walk bare-directory entries to their contained files. Closes the whole class
   automatically for any future atom of the same shape.

Either way the fix must ship with an R15 mutation test proving the scope-change re-offer now FIRES on a
source edit to an empty-file_scope atom (a control that cannot fail is worse than none). Option 2 is the
R10-preferred class closure (extends the mechanism so the entire class fails automatically), option 1 is the
narrower data fix.

## Why queued, not fixed now

Surfaced inside a bounded Rule-0 HARDEN tick whose drawn atom (`ARCH1`) is in fresh 24h cooldown. A
supervisor-mechanism change or a map `file_scope` edit with disjointness blast radius is not a drive-by; it
needs its own granted turn + R15 proof. Registered here + in the decision log so it is durable, not lost.
