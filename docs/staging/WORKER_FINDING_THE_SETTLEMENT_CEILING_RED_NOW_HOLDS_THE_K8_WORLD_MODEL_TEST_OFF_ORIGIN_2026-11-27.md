**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome`

# The settlement-ceiling HEAD red now holds the K8 world-model test off origin

Found 27 Nov 2026 by the worker landing `k8-covers-world-models-one-leg-test` (director commitment,
due 2 Dec).

## What happened

The K8 one-leg test (`tests/architecture/test_a_world_model_cites_its_knowledge_page.py`, in the
shared tree, not landed) redded 19 of 25 world modules under L3+ atoms. All 19 docstrings were
fixed. The gate on the whole set refused on one test only:
`tests/simulation/test_net_new_acquisition.py::test_the_ceiling_still_fits_the_peak_systemds_own_journal_reports_today`.
The convention map selects it because `simulation/net_new_acquisition.py` is one of the 19.

That test is already on `HEAD_RED_REGISTER.md`, red for 7 census runs since 2 Oct. It is not caused
by the docstring. It re-prices the ceiling from the systemd journal over the last 24h:

| Run (sim-runner) | Code | Largest process peak | cgroup peak |
|---|---|---|---|
| 26 Nov 21:32 UTC | 2100f84f85 | 6,523.8 MB | 7.8G |
| 27 Nov 01:18 UTC | 601887d76a | 6,260.2 MB | 8.2G (692.7M swap) |

On those peaks the curve supports 7,183 customer-years. The director's budget is 7,700
(`DIRECTOR_RULING_FOUNDER_HOUSEHOLDS_WITH_BUDGET_RAISED_2026-10-20.md`). When it was re-measured
(b60a0cd8a5, 25 Oct), 7,699.3 cy cost 5,555.9 MB at 7a692b47ae. So the program has grown about 1 GB
heavier per run since then, at the same budget.

## What landed and what waits

The 18 other docstrings landed alone in d2a469644. The test and
`simulation/net_new_acquisition.py` have to land together. Without that module, the test reds on it.
Without the test, nothing holds the module's docstring line. Both are in the shared tree. The
landing bytes are the working-tree copies.

## The explanations the evidence allows, ranked

1. **Code got heavier between 25 Oct and 26 Nov.** The test's own docstring names this as the defect
   it exists to catch. Most likely: a month of world builds landed in between, including the EPC
   register, the fabric terms and the half-hourly texture. To settle it: rerun the curve's probe at
   origin. If one commit carries the step, bisect it.
2. **A book run is not the curve's shape.** These are published-book runs, and the curve may be a
   settlement-only probe. b60a0cd8a5 says it was measured "with the parent", so this is less likely.
   It is worth one read of what the curve measures before re-measuring.
3. **The budget no longer fits.** That is the director's number. If (1) shows a real, wanted growth,
   the change goes to him with a recommendation. The ceiling is never raised to fit.

## What would close this

The ceiling test goes green at origin, by any of the three routes above. Then land
`tests/architecture/test_a_world_model_cites_its_knowledge_page.py` and
`simulation/net_new_acquisition.py` together. The gate already passed the other 1,715 selected tests.

## Resolved by route 3, under the director's own rule (worker, 27 Nov)

The journal now shows more than one heavy run. The largest process was 5,750.2 MB on 20 Nov. It
then ran 5,920.3-6,057.8 MB on seven runs between 24 and 27 Nov, and 6,260.2 and 6,523.8 MB on two
more. Even the typical 6,050 MB prices 7,658 cy, so the red would not have aged out. Every one of
those peaks is above the 6,008 MB allowance itself, not merely within 5% of it.

The 20 Oct ruling already said what to do in that case (step 3): "go back to 400 supply points for
production. Then bring a proposal that closes the gap." So `founder_unit` is back to
`supply_points` and the budget is back to 5,000. Both land in one commit with the K8 test and this
module's GAP line. The ceiling, the 0.25 share and the headroom are untouched. The proposal is the
`for_the_director` row `your-20-oct-stop-rule-fired-production`: attribute the growth first, then
fix it by R8 or R6.

Correction to route 1 above: what this note calls "the program grew about 1 GB" is two numbers.
About 300-500 MB is steady growth in the typical run. The 6,524 MB run sits on top of that.
