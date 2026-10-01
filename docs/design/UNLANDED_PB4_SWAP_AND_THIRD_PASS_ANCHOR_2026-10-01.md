# Unlanded: the PB4 bill-shock swap and the third-pass level anchor (2026-10-01)

**Status: built, controlled and measured. Not landed, because a level refit changes the world
identity and the value-arms page then refuses every bound it publishes.**
Claim `swap-pb4-bill-shock-base-onto-the-experienced-shock`, base `e9b79073d`.

## What the patch does

- `simulation/customer_events.py`: `_bill_shock_base` becomes
  `churn_probability(1 if experienced shock else 0) * (1 - win_probability)`, with the passive cap
  unchanged. That is one event a year, where it used to be shocked months. The retired base rides
  on the event as `sim_month_count_bill_shock_base`.
- `simulation/departure_level_anchor.py`: the third-pass block, fitted by `fit_whole_book` on the
  swapped capture B.
- `tests/simulation/test_experienced_bill_shock.py`: a control that a year-one shocked and
  unshocked pair now differ in base by `churn_probability(1)/churn_probability(0)`. The month count
  reads them as equal. Mutation-proven: setting the base back to the month count reds it.
- The ground-truth guard learns the new field, and the module docstring says the shock now drives
  the hazard.

Measured results, pre-registered: `docs/staging/done/SEAT_PREREGISTRATION_WHAT_THE_PB4_BILL_SHOCK_SWAP_MUST_MOVE_2026-10-01.md`.

## What blocks landing it

Applied at `e9b79073d`, the patch reds 26 controls:

- **25 in `tests/tools/test_generate_value_arms_data.py`.** The one read in full says *"NO BOUND ON
  THIS PAGE WAS MEASURED IN THIS WORLD"*. `world_level_identity` digests the anchor block, so a
  refit makes every committed floor and three-arm run belong to another world. That is the design
  working: the page must not bound a figure with a spread from a world it no longer runs. The
  controls assert that the real feed carries a bound, so they red until the arms are re-measured.
- **`test_switching_rate_commons.py::test_the_capture_the_band_verdict_is_read_from_was_produced_by_the_live_anchor`.**
  `measure_departure_level.DEFAULT_TABLE` still names `c6`. It must be repointed at a committed
  capture taken under the new block. `pb4_c_third_pass_anchor_departure_factors.json` is that
  capture for this block.

## The landing sequence

1. Optionally run a fourth pass first: apply the C-fitted values (in the pre-registration's C
   table) and capture D. 2020 and 2021 sat low on C.
2. Re-take the value arms in the new world (`python3 -m tools.run_value_cycle_ab`, the same
   procedure as the 2026-09-08 current-world re-take) and promote them through the generator's
   path constants.
3. Land the patch, the repointed `DEFAULT_TABLE` and the re-taken arms as one commit.

The patch (`git apply` from the repo root):

```diff
diff --git a/simulation/customer_events.py b/simulation/customer_events.py
index 8f329974d..1e7c770cd 100644
--- a/simulation/customer_events.py
+++ b/simulation/customer_events.py
@@ -28,7 +28,7 @@ from collections.abc import Container
 from datetime import date
 
 from company.crm.churn_model import estimate_churn_probability
-from saas.churn_model import build_churn_risk
+from saas.churn_model import build_churn_risk, churn_probability
 from saas.home_move_win_rate import build_home_move_win_rates
 from simulation.departure_level_anchor import year_level_anchor
 from simulation.departure_risks import (
@@ -589,10 +589,21 @@ def roll_lifecycle_event(
     # `renewal_data["churn_probability"]` (the raw base rate on the event) is NOT the number the
     # chain starts from, which is `1 - effective_retention_probability`, and the difference is
     # exactly the quantity the P0 calibration is fitted against.
-    _bill_shock_base = 1.0 - effective_p_retain
+    _month_count_bill_shock_base = 1.0 - effective_p_retain
     _experienced_shock = experienced_bill_shock_at_renewal(
         customer_id, commodity, term_month, records_so_far, customers,
     )
+    # PB4 SWAP (2026-10-01): the base counts ONE experienced shock per year, not shocked months.
+    # The month count was blind in a household's first year and carried the world's whole tenure
+    # gradient (0 vs 6.86 months); the experienced shock fires at a first renewal. Same uplift,
+    # same win leg, same passive cap -- only the count changed, so `year_level_anchor` is refitted
+    # against the published band rather than this tree's own output. A `None` shock (prepayment,
+    # no sign-up quote, unobserved prior year) adds no uplift, and its reason travels on the event.
+    _p_churn_shock = churn_probability(1 if _experienced_shock["shocked"] else 0) * (
+        1.0 - renewal_data["win_probability"])
+    if passive_churn_cap is not None:
+        _p_churn_shock = min(_p_churn_shock, passive_churn_cap)
+    _bill_shock_base = _p_churn_shock
     _market_opportunity = 1.0
     _price_response = 1.0
     _action_propensity = 1.0
@@ -900,8 +911,9 @@ def roll_lifecycle_event(
         "sim_level_anchor": round(_level_anchor, 6),
         # PB4: the bill shock this household EXPERIENCED, by `what_bill_shock_is.md`'s definition
         # (DD reset for direct debit, the bill for standard credit, out of scope for prepayment;
-        # the quote is the reference in year one). Ground truth beside `sim_bill_shock_base`, NOT
-        # yet what the hazard reads -- see `simulation/experienced_bill_shock.py` for why the swap
-        # waits for one run that measures it first.
+        # the quote is the reference in year one). Since the PB4 swap it is what
+        # `sim_bill_shock_base` counts; the retired month-count base rides beside it so a capture
+        # can attribute the swap without a second run.
         "sim_experienced_bill_shock": _experienced_shock,
+        "sim_month_count_bill_shock_base": round(_month_count_bill_shock_base, 6),
     }
diff --git a/simulation/departure_level_anchor.py b/simulation/departure_level_anchor.py
index 13a8a49a8..bbfa923cf 100644
--- a/simulation/departure_level_anchor.py
+++ b/simulation/departure_level_anchor.py
@@ -221,14 +221,26 @@ NO_LEVEL_CORRECTION = 1.0
 #: exists to stop. So the clamp stays, DECLARED, until the mechanism under it has a source -- and
 #: the verdict file is what stops the clamped number travelling alone in the meantime.
 #: ─────────────────────────────────────────────────────────────────────────────────────────────
+#: ─────────────────────────────────────────────────────────────────────────────────────────────
+#: THIRD PASS, RE-FITTED 2026-10-01 FOR THE PB4 SWAP. The bill-shock base now counts one experienced
+#: shock a year instead of shocked months, which cut the renewal route's mean base about fourfold
+#: (0.100 -> 0.026 at later renewals) and lowered the whole book in all seven fitted years on a
+#: one-variable pair (`e9b79073d` with and without the swap, same seed). Fitted by `fit_whole_book`
+#: on the swapped capture. Six anchors rise and 2017 falls (7.372584 -> 7.031166), because 2017
+#: already sat 0.39pp over its target before the swap. 2023 keeps its value: on both captures the
+#: fit refuses it (the renewal route cannot carry the residual at any anchor), so the swap did not
+#: create that gap. 2020 and 2024 now stand above 15 on 13-14 renewal decisions each, so the clamp
+#: is carrying more of the level than before. That is the cost of the swap, and it is stated rather
+#: than smoothed. Pre-registration and grading:
+#: `docs/staging/done/SEAT_PREREGISTRATION_WHAT_THE_PB4_BILL_SHOCK_SWAP_MUST_MOVE_2026-10-01.md`.
 YEAR_LEVEL_ANCHOR: dict[int, float] = {
-    2017: 7.372584,
-    2018: 2.945347,
-    2019: 6.637286,
-    2020: 6.359296,
-    2021: 5.641346,
+    2017: 7.031166,
+    2018: 5.295245,
+    2019: 8.556731,
+    2020: 16.29343,
+    2021: 12.208051,
     2023: 2.033232,
-    2024: 4.259915,
+    2024: 15.43806,
 }
 
 #: `{year inside the published record with no fitted anchor: WHY}`. This is the half of the
diff --git a/simulation/experienced_bill_shock.py b/simulation/experienced_bill_shock.py
index ecf30ea31..26cce29ac 100644
--- a/simulation/experienced_bill_shock.py
+++ b/simulation/experienced_bill_shock.py
@@ -22,10 +22,11 @@ bill-size gradients (`docs/staging/WORKER_FINDING_THE_WORLDS_BILL_SHOCK_COUNT_IS
 HOUSEHOLDS_FIRST_YEAR_AND_CARRIES_THE_WHOLE_TENURE_GRADIENT_2026-10-01.md`). Widening that window to
 reach year one would keep the wrong quantity.
 
-**This module is emitted as ground truth on each renewal event and does NOT yet drive the hazard.**
-Swapping the base moves the departure LEVEL as well as its gradients -- `year_level_anchor` was
-fitted against the old month count -- and two changes in one run cannot be attributed. The next
-pass measures this quantity's tenure gradient on a run, then swaps the base.
+**Since the PB4 swap (2026-10-01) this drives the hazard.** `customer_events` counts ONE event per
+year -- shocked or not -- where it used to count shocked months, and `year_level_anchor` was
+refitted against the published band, because swapping the base moves the departure LEVEL as well as
+its gradients. The month-count base still rides on the event as `sim_month_count_bill_shock_base`.
+The pair and the refit: `docs/staging/done/SEAT_PREREGISTRATION_WHAT_THE_PB4_BILL_SHOCK_SWAP_MUST_MOVE_2026-10-01.md`.
 
 A FALL IS NOT A SHOCK. Every trigger the page names is a rise: cold weather, a usage rise, a
 catch-up after estimates, a renewal price rise, a DD increase, and Ofgem's own 2022 escalation was
diff --git a/tests/architecture/test_the_departure_cause_never_reaches_the_company.py b/tests/architecture/test_the_departure_cause_never_reaches_the_company.py
index 6df0a843b..6081d4e3e 100644
--- a/tests/architecture/test_the_departure_cause_never_reaches_the_company.py
+++ b/tests/architecture/test_the_departure_cause_never_reaches_the_company.py
@@ -45,6 +45,8 @@ C2_GROUND_TRUTH_FIELDS = frozenset({
     # The world computes it with the household's payment channel; it is B8's forbidden target --
     # a company fitting it would learn the world's hazard rather than its customers.
     "sim_experienced_bill_shock",
+    # The retired month-count base, kept beside the new one so the PB4 swap can be attributed.
+    "sim_month_count_bill_shock_base",
 })
 
 
diff --git a/tests/simulation/test_experienced_bill_shock.py b/tests/simulation/test_experienced_bill_shock.py
index 6966c103c..0bf26232d 100644
--- a/tests/simulation/test_experienced_bill_shock.py
+++ b/tests/simulation/test_experienced_bill_shock.py
@@ -146,3 +146,23 @@ def test_a_year_billed_EXACTLY_as_quoted_reads_NO_rise():
     # The round-up to the pound is at most £1 on a ~£50 payment.
     assert 0.0 <= shock["rise_fraction"] < 0.025, shock
     assert shock["shocked"] is False
+
+
+def test_the_HAZARD_BASE_counts_one_experienced_shock_a_year_and_so_moves_in_year_one():
+    """The defect is the swap not having happened: the hazard read shocked MONTHS, which are 0 at
+    every first renewal, so a household shocked in year one was exactly as likely to leave as one
+    that was not. Both legs of the partition are asserted reachable before the ratio is read."""
+    from saas.churn_model import churn_probability
+
+    customers = [{"customer_id": "C1", "commodity": "electricity", "segment": "resi",
+                  "epc_rating": "D", "acquisition_date": "2021-10-01", "eac_kwh": 2700}]
+    shocked = roll_lifecycle_event("C1", "2022-10-01", "electricity",
+                                   _year_one_records("2021-10", 200.0, 400.0), customers)
+    quiet = roll_lifecycle_event("C1", "2022-10-01", "electricity",
+                                 _year_one_records("2021-10", 200.0, 200.0), customers)
+    assert shocked["sim_experienced_bill_shock"]["shocked"] is True
+    assert quiet["sim_experienced_bill_shock"]["shocked"] is False
+    # The retired month count cannot tell them apart in year one -- that is the blindness.
+    assert shocked["sim_month_count_bill_shock_base"] == quiet["sim_month_count_bill_shock_base"]
+    ratio = shocked["sim_bill_shock_base"] / quiet["sim_bill_shock_base"]
+    assert abs(ratio - churn_probability(1) / churn_probability(0)) < 1e-3, ratio
```
