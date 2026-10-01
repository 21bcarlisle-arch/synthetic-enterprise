# Unlanded: the PB4 bill-shock swap and the third-pass level anchor (2026-10-01)

**Status (updated 2026-10-01 17:05 BST): fourth pass done, value arms re-taking in world D. Not landed, because a level refit changes the world
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

**Updated 2026-10-01 ~17:05 BST (claim `land-pb4-swap-with-value-arms-retaken-in-the-new-world`).
Step 1 is done and step 2 is running. The patch below is now the FOURTH-pass block (world digest
`cf823b185f8ca51c`), and it supersedes the third-pass patch this file first carried.**

1. **Done: the fourth pass.** It was taken in origin `0407ce0e3`'s world, where the standing charge
   is ex-VAT. C2 (third block, current world) sat within 0.07pp of C in every year. Refitted on C2,
   and D was captured under that block. D lands 2017-2021 at their targets. 2024 is 16.28 against
   a band top of 16.1: 0.18pp, or about 0.12 of one expected departure on 65 accounts. 2023 is
   still unfittable. That is 5 of 6 in band, against C's 4. Captures:
   `docs/reports/pb4_c2_ex_vat_standing_charge_departure_factors.json` and
   `docs/reports/pb4_d_fourth_pass_anchor_departure_factors.json`, each with its SVT sibling. Graded in
   `docs/staging/records/SEAT_RESULT_THE_PB4_FOURTH_PASS_LANDS_FIVE_OF_SIX_YEARS_IN_BAND_2026-10-01.md`.
2. **Running: the value arms in world D.** They run from the scratch worktree `/home/rich/wt-pb4-land`,
   which is origin `0407ce0e3` plus the patch below. Do not move or reset it until both artefacts exist.
   * `longjob-pb4-three-arm-d` writes `docs/observability/value_cycle_ab_s1_three_arm_20261001.json`
     (`--level-arm`, about 50 min, started 17:04 BST).
   * `longjob-pb4-floor-d-s123` writes `docs/observability/value_cycle_ab_s1_noise_floor_20261001.json`
     (`--noise-floor-seeds 11111,22222,33333 --redraw-mode all`, 3 passes per seed, so about
     8h). It starts when the three-arm pid exits.
   * Re-ask both with `python3 -m background.launch_liveness --check`.
3. **Then promote.** Copy both artefacts into the shared tree. Repoint `CURRENT_WORLD_THREE_ARM_PATH`
   and `CURRENT_WORLD_NOISE_FLOOR_PATH` in `tools/generate_value_arms_data.py`, plus every other
   constant whose artefact now names world `39a192ce04c1eda8`. Regenerate `site/data/value_arms.json`
   and run `tests/tools/test_generate_value_arms_data.py`. The 25 reds listed above are the
   checklist. Some of them assert TODAY's answer (for example "the level leg's family straddles
   zero", or the 154/164-run selector). Where the new world's answer differs, re-key the control to
   the property; do not re-run until it agrees. If n=3 cannot satisfy a control that needs a
   family, extend the floor with more seeds and `--fold`.
4. Land the patch, the re-taken arms and the generator's repointed constants as one commit.

The patch (`git apply` from the repo root, at `0407ce0e3` or later):

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
index 13a8a49a8..4688b85eb 100644
--- a/simulation/departure_level_anchor.py
+++ b/simulation/departure_level_anchor.py
@@ -221,14 +221,33 @@ NO_LEVEL_CORRECTION = 1.0
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
+#: FOURTH PASS, the same day, and these are the values below. One pass does not reach the fixed
+#: point, because the anchor changes who is left on the book. The third-pass capture left 2020 and
+#: 2021 low. Refitted on C2, which is origin `0407ce0e3` (the ex-VAT standing charge) plus the swap
+#: under the third-pass block. C2's level sat within 0.07pp of C's in every year, so the
+#: standing-charge change did not move this fit. 2020, 2021 and 2024 now all stand above 17, on
+#: 8-12 renewal decisions each. The values are graded on capture D:
+#: `docs/staging/records/SEAT_PREREGISTRATION_THE_PB4_FOURTH_PASS_IN_THE_EX_VAT_STANDING_CHARGE_WORLD_2026-10-01.md`.
 YEAR_LEVEL_ANCHOR: dict[int, float] = {
-    2017: 7.372584,
-    2018: 2.945347,
-    2019: 6.637286,
-    2020: 6.359296,
-    2021: 5.641346,
+    2017: 6.990171,
+    2018: 5.269958,
+    2019: 8.583067,
+    2020: 19.550406,
+    2021: 18.474462,
     2023: 2.033232,
-    2024: 4.259915,
+    2024: 17.128306,
 }
 
 #: `{year inside the published record with no fitted anchor: WHY}`. This is the half of the
diff --git a/simulation/experienced_bill_shock.py b/simulation/experienced_bill_shock.py
index ecf30ea31..040d16046 100644
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
diff --git a/tools/measure_departure_level.py b/tools/measure_departure_level.py
index 04e040e79..a211f7160 100644
--- a/tools/measure_departure_level.py
+++ b/tools/measure_departure_level.py
@@ -92,7 +92,11 @@ COMMONS = PROJECT / "docs" / "domain_artefact_library" / "regulatory" / "gb_dome
 #: other judging a world it did not come from. `c6_second_pass_departure_factors.json` is the
 #: capture of the twice-fitted world — 133 renewal and 1,313 SVT decisions, both halves tracked
 #: in this commit, both executed under the block this commit lands.
-DEFAULT_TABLE = PROJECT / "docs" / "reports" / "c6_second_pass_departure_factors.json"
+#: REPOINTED 2026-10-01 FOR THE PB4 SWAP, same reason again: the bill-shock base changed and the
+#: block was refitted twice (third and fourth pass). `pb4_d_fourth_pass_anchor_departure_factors.json`
+#: is the capture under the fourth block that lands with it. It has 104 renewal and 2,013 SVT
+#: decisions, and both halves are tracked.
+DEFAULT_TABLE = PROJECT / "docs" / "reports" / "pb4_d_fourth_pass_anchor_departure_factors.json"
 
 #: Active domestic electricity accounts per year in the live run, from the opening finding's own
 #: table. NOT re-derived here: the factor table holds renewals, not the active book, so the
```
