# [WORKER FINDING] The selection leg is inside its own noise, and the harness that would have said so was patched onto a dead symbol

**Severity:** RECORDED · **Lane:** H_harness · **Date:** 2026-08-27

## Class registration

Belongs to `controls_that_cannot_fail` (`CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`). The
mechanism is R15's FAIL-SILENT shape: a measurement harness keyed to a structure that moved,
returning a plausible number from a measurement of nothing.

## The headline, in one line

**`selection_gbp` has a standard deviation of £3,121 across four seeds and a mean of −£166. The
published figure is −£1,388.80. The selection leg is not distinguishable from zero, and every
reading built on it needs that caveat.**

## What was published

`WORKER_FINDING_THE_VALUE_ARMS_ADVANTAGE_IS_THE_LEVEL_NOT_THE_SELECTION_2026-08-27.md`, full
decade: control £111,269.70, value £118,335.56 (**+£7,065.86**), level £119,724.66
(**+£8,454.96**), so **selection = −£1,388.80** and **level share = 119.7%**. That £1,388.80 is a
difference between two arms over roughly thirty renewals, and no error bar had ever been put on it.

## What the four seeds actually did (observed)

Four completed sweeps, each a full three-arm decade run with **only** the per-household elasticity
assignment re-drawn — same book, same weather, same settlement data, population draw off.

| seed | control | value | level | adv_value | adv_level | **selection** | level share |
|---|---|---|---|---|---|---|---|
| 11111 | 110,164.55 | 116,827.49 | 120,495.69 | +6,662.93 | +10,331.14 | **−3,668.21** | 155.1% |
| 22222 | 112,198.80 | 123,663.31 | 119,816.93 | +11,464.52 | +7,618.14 | **+3,846.38** | 66.5% |
| 33333 | 114,299.45 | 122,175.07 | 121,991.16 | +7,875.62 | +7,691.71 | **+183.91** | 97.7% |
| 44444 | 110,443.07 | 117,508.93 | 118,534.31 | +7,065.86 | +8,091.24 | **−1,025.38** | 114.5% |

- `selection_gbp`: mean **−165.83**, sd **3,121.20**, range **7,514.59** (−3,668.21 … +3,846.38).
  SEM over four seeds is £1,560.60, so |mean| is **0.11 SEM** — indistinguishable from zero.
- `level_share_of_advantage`: mean 1.08, range **0.66 … 1.55**. The published 119.7% sits inside
  a band that spans "the selection is worth a third of the advantage" to "the level overshoots by
  half". The share cannot currently order those readings.
- `adv_value` itself: mean 8,267, sd 2,190. The value arm's advantage is better resolved than the
  split, but not by much.

**This does not overturn the published direction.** Three of four seeds still put the level at or
above the value arm, and the sign of the mean is unchanged. What it overturns is the *precision*:
−£1,388.80 was reported as a quantity, and it is not one at this seed count.

## The mechanism — why nobody had this number

The measurement existed only as a `/tmp` scratchpad, so no commit reproduced it and nothing tested
it. Its first version patched `simulation.population_draw.price_sensitivity_for_customer`. On
2026-08-27 the churn decision moved to a continuous per-household elasticity and
`simulation/customer_events.py:313` now imports `price_elasticity_for_customer` instead;
`price_elasticity_for_customer` reaches `_draw_curriculum_axis` directly and never routes through
the old name. So the patch reached **nothing**: every seed ran a byte-identical world, and the
harness would have reported a noise floor of exactly **zero** — the most flattering answer
available, produced by measuring nothing. `inferred`: the identical-worlds reading is reconstructed
from the code path and from the scratchpad's own later comment, not observed in a surviving log —
the four logs above post-date the repair and vary correctly. `observed`: the disconnection itself,
from the two function definitions and the single import at `customer_events.py:313`.

Two further defects carried across at the same time:

1. **The scratchpad pinned the level arm at `renewal_margin_flat_level_gbp_per_mwh=44.5`**, a
   remembered constant. The committed runner reads the value arm's own realised median off the
   same run, so the scratchpad was measuring the noise floor of a *different instrument* from the
   one that publishes. The committed mode re-reads the median per seed.
2. **`price_sensitivity_for_customer` had no live caller** and read as a live name. It is now
   documented in its own docstring as the SEGMENT-LEVEL accessor, explicitly not what the price
   response calls, with a pointer to the resolver. It is retained rather than deleted because the
   cohort-agreement controls over the three-level segment are its real consumers — and because
   re-wiring the elasticity path through it would destroy the R15 mutation below.

## What was built

`tools/run_value_cycle_ab.py` gains a committed **noise-floor mode**:

    python3 -m tools.run_value_cycle_ab --noise-floor-seeds 11111,22222,33333,44444

- `resolve_elasticity_symbol()` parses `simulation/customer_events.py` and returns the single name
  it imports from `simulation.population_draw`. **The name is read, never written down**, so a
  rename that moves both sides is followed automatically and a decision that stops importing from
  the draw module **raises** instead of measuring a disconnected symbol.
- A **per-seed fire counter**: a rebind that reaches no call site raises rather than reporting a
  spread of zero. This is the floor on the tool's own subject.
- Reports `selection_gbp` and `level_share_of_advantage` spread, SEM, and
  `selection_distinguishable_from_zero`, to `docs/observability/value_cycle_ab_noise_floor.json`.
- Refuses a single seed: one seed is a run, not a spread.

## R15 — proven both ways

`tests/tools/test_value_cycle_ab_noise_floor.py`, 9 tests, all green.

- **Positive:** a correctly resolved patch fires 40× per seed and moves `selection_gbp` — three
  seeds, three distinct figures, non-zero spread.
- **The named mutation:** pointing the mode at the retired `price_sensitivity_for_customer` must
  raise, not report zero. `test_the_retired_symbol_would_report_a_floor_of_zero` first *shows* the
  old name yields byte-identical selection figures across seeds, then
  `test_pointing_the_noise_floor_at_the_retired_symbol_raises` asserts the refusal.
- **Mutation verified red, not asserted:** disabling the fire counter
  (`if calls["n"] == 0:` → `if False:`) was applied and run — `1 failed, 8 passed`, the failure
  being `DID NOT RAISE`. Restored, 9 passed.

## Open, not resolved

Seed 44444's `adv_value` is **7,065.86** — equal to the published figure to the penny, while its
control and value nets each sit £826.63 below the published run's. An exact 2dp agreement on a
~£7,000 difference is unlikely to be coincidence, and it is not explained here. It does not affect
the spread above (which is computed from the four sweeps on their own terms), but it wants an
explanation before the published run's provenance is relied on again. Filed as `inferred`,
unexplained.

Four seeds is also a small n. The finding is that the instrument's error bar **exceeds the effect
it publishes**; narrowing it is a matter of more seeds, and that is now a one-command run.

## What this does NOT license

Re-running until a seed agrees with the published number (R12). A selection leg inside its own
noise is a complete result about the instrument, not a cue to tune the arm.
