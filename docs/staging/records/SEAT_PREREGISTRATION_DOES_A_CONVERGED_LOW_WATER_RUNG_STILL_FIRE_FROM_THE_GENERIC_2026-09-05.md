# PRE-REGISTRATION — does a converged low-water rung still fire when the GENERIC is mutated?

**Severity: INFO** — a pre-registration, filed before the measurement it names. No claim yet.

**Written 2026-09-05, before any of the two re-points below were made.**

## The work this is registered against

`converge-three-low-water-implementations`. Three hand-written implementations of one control:

| implementation | home | landed |
|---|---|---|
| `removed_dispositions` | `background/self_clearing_alarm_census.py` | `dc5fcbbc8` |
| `removed_claims` | `tools/canon_drift_check.py` | `605ec3995` |
| `removed_rows` / `keys_at_head` | `background/register_low_water.py` | `6f4e6b1f4` |

Each carries its own copy of three repairs: the `or ""`-before-`str` null-reason treatment, the
None-is-never-`frozenset()` refusal, and the no-subject-gone-exception argument. That is the VAT
shape — one rule, several implementations, a defect repaired in one and live in another — on a
control whose entire subject is registers that silently lose repairs.

The premise's third leg is **SPENT**: `docs/design/maturity_map.yaml` is already wired, at
`tools/level_promotion_gate.low_water_failures()` with its retirement reasons in
`docs/design/maturity_map_retired.yaml`, and that is on `origin/main` (`173abcf60` == `origin/main`
at draw time). Recorded here rather than done twice.

## The hazard this measurement exists to catch

There is a named failure of exactly this refactor in the catalogue: **a control that calls the
shared helper instead of the caller survives mutation of the caller.** Converging turns two
mutation-proved controls into two *call sites*, and a call site can be mutation-proved by the
generic's tests while its own tests have quietly become assertions about `register_low_water`
rather than about the census or the canon.

The inverse hazard is as real: a refusal message is reformatted by the convergence, and the tests
that assert its shape are relaxed until they pass. `out[0].startswith("gone.json")` is keyed to
today's formatting, not to the property, and "relax it until green" is how a refactor eats a
control.

## THE PREDICTIONS, written before the runs

**P1.** After the census is re-pointed, deleting `or ""` from **`register_low_water.removed_rows`**
(not from the census — there will be no copy left there) reds
`tests/background/test_the_register_can_lose_a_row_and_take_the_alarm_with_it.py::test_an_EMPTY_OR_NULL_retired_reason_does_not_open_the_hatch[None]`.
If it does not, the census's own tests have stopped reaching the mechanism.

**P2.** After the census is re-pointed, changing `removed_rows`'s `baseline is None` branch to
`return []` reds that file's `test_an_UNESTABLISHABLE_baseline_is_a_REFUSAL_not_a_clean_result`.

**P3.** The same two mutations, after the canon is re-pointed, red the corresponding two legs of
`tests/tools/test_the_canon_register_can_lose_a_claim_and_take_the_drift_with_it.py`.

**P4.** Mutating `keys_at_head`'s `return None` (the `returncode != 0` leg) to `return frozenset()`
reds `test_THE_HEAD_READER_ITSELF_returns_None_and_never_an_empty_set` in the canon file. This is
the leg that was *added* because it was missing, and it is the one most likely to be lost at the
seam.

**P5 — the one I expect to be refuted.** After both re-points, each mutation above reds tests in
**more than one** of the three suites, because all three now share the mechanism. If any mutation
reds only ONE suite, the other call site is not reaching the code I think it is reaching.

**What refutes the whole convergence:** any mutation of the generic that leaves every census and
canon test green. That would mean the two re-points are decorative and the controls now live
entirely in the generic's own fixtures.

## What I will NOT do

Relax an assertion to make it pass. Where the refusal text legitimately changes (the generic
prefixes each line with the register's name so a mixed report says which register spoke), the
assertion is to be made **stronger** — the register name AND the key — rather than dropped.

---
*Result filed beside this, in the same directory, after the runs.*
