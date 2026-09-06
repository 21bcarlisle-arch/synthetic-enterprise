**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** EP13_adapter_carbon_intensity
· **Class:** no_caller_and_never_runs

# RESULT: the producer of a published artefact now runs, and one of its first controls was an equivalence

**Measured and built 2026-09-06, delivery seat, lane 0 claim
`ep13-embedded-generation-measure-has-no-test`. Pre-registered at
`docs/staging/SEAT_PREREG_WHAT_A_CONTROL_OVER_EP13S_MEASURE_COSTS_AND_WHAT_SHAPE_THAT_LICENSES_2026-09-06.md`,
with its poison-round-B addendum registered before that round ran.**

Discharges the defect named at the foot of
`SEAT_RESULT_THE_TENTH_SUITE_CANNOT_SEE_THE_SUBJECT_AND_THE_CALLER_IT_TESTS_HAS_NO_TEST_OF_THE_PATH_THAT_CALLS_IT_2026-09-06.md`:

> `tools/ep13_embedded_generation_bound.measure()` is executed by nothing but `main()`, and no
> test runs `main()`.

## What was built

`tests/tools/test_ep13_embedded_generation_bound_measure.py` — 17 tests, **331s**, executing the
real thing: the Elexon demand and AGWS caches load, `generate_grid_intensity_feed.fuel_mix()` is
called and its seven-tuple unpacked, both NESO series are read, the year intersection is taken,
`main()` writes the artefact, and the committed
`docs/observability/ep13_embedded_generation_bound.json` is compared against that run.

A **separate file** from the 623-second suite beside it, and that is the point rather than a
filing convenience. The old file's own helper `_measure` — six call sites, `measure_year` on
synthetic worlds — is what made a grep for coverage of `measure` come back satisfied for months.
Six more tests inside it would have rebuilt the ambiguity that hid the gap.

`measure()` gained `only_years`, `grids` and `null_seeds`. `main()` passes none of them, so the
published artefact is unchanged.

## What the numbers are

| quantity | reading |
|---|---|
| unbounded `measure()` | **> 3,000s**, killed at its 50-minute timeout without finishing |
| the bounded control suite | **331.6s** green, 344.6s under poison |
| poison leg cost (no `measure_year` at all) | **2.8s** — the 137 MB of cache parsing is not the cost |
| `ceiling_3d` for 2024, fresh run vs committed artefact | identical to 1e-9 |

**Prediction 1 held** (> 600s; it is more than five times that). **Prediction 2 was not
separable** — the poison legs prove the loads cost ~1s each, so the 20–90s band was far too
generous and the load is not where the time goes. **Prediction 3 held in direction and was wrong
in magnitude**: dropping the sweep to one grid does not put the run inside 120s, because a single
real `measure_year` is ~160s. Two of those is the whole bill.

The artefact reproduces exactly, so it is **not stale** — which was not knowable before, because
nothing re-ran its producer.

## THE FINDING THIS PRODUCED: the first draft's load-bearing control was an equivalence

The bounded design rests on `only_years` **filtering** the year intersection rather than
**selecting** from it — a selector would make every assertion in the file a statement about its
own argument. The first draft asserted that property directly, by asking for `1999` alongside a
year that must exist, and named the test after it.

**It cannot fail.** Replace the filter with `years = list(only_years)` and the returned dict is
byte-identical: `measure_year("1999", …)` finds no fit half hours, raises
`NesoIntensityUnavailable`, and the year loop's `except …: continue` swallows it. The selector
mutation is an *equivalence*, not a survivor, and the swallow is why. Nothing short of `measure`
reporting the intersection it took can distinguish the two — and adding that would change a
published artefact's schema to prove a property of a test's argument.

The leg was kept and **renamed to what it does kill**: narrow that `except` tuple and the same
call raises instead of returning a row short. The class docstring states the limit in full rather
than leaving it to a reader, because *choosing a mutation and then working out what it touches*
is the order that produces flattering rounds — and this file caught itself doing the opposite in
its own addendum, where `PLACEBO_SEED` was registered as poison B and then withdrawn, before the
run, on noticing it reaches `placebo_shuffled` and nothing any reproduction leg reads.

## The poison rounds, both banked

| round | mutation | predicted | observed |
|---|---|---|---|
| A | `fuel_mix()` failure swallowed inside `measure` | the `fuel_mix` leg reds, the demand leg does not | exactly that, 2.78s |
| B | top-level `"grid"` renamed `"grid_spec"` | two named tests red, 15 green, both reproduction legs green | exactly that, 344.6s |

Round A is what the `fuel_mix` contract battery was looking for and could not find: a suite that
**demonstrably reaches** `fuel_mix` through this caller. Round B is the one that matters more,
because it proves the 5½-minute module fixture is read rather than merely computed.

## What is NOT established

- **That the other five years still measure.** The control runs the artefact's last year only.
  A cache that broke 2019 alone would not red anything here.
- **That `only_years` filters.** Argued in the docstring, unprovable from outside, stated as such
  above.
- **That the sweep's other four grids still run.** `grids` is bounded to the published one; a
  defect reachable only at 24x5x5 is outside this control by construction.
- **The unbounded runtime.** It is a lower bound of 3,000s, not a measurement — the run was
  killed by its own timeout, not finished.
