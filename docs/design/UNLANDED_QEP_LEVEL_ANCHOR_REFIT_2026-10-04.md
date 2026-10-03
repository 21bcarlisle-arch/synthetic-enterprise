# UNLANDED: the level anchor re-fitted onto DESNZ QEP 2.7.1, waiting on its value arms

**Claim:** `refit-the-level-anchor-onto-desnz-qep-2-7-1` (Lane 0 delivery). **Written:** 2026-10-04 by the delivery seat.
**Graded result:** `docs/staging/records/SEAT_RESULT_THE_LEVEL_ANCHOR_REFIT_ONTO_DESNZ_QEP_2_7_1_2026-10-03.md`.

## Why this is not landed yet

The patch below re-sites the switching commons onto QEP 2.7.1 and lands the second QEP-pass level
block (capture G, every fitted year within 0.3pp of the record). It moves `world_level_identity`
from `cf823b185f8ca51c` to **`cdba75ebb9197b33`**, so about 20 value-arms and page controls go red
until the arms are re-taken in that world. That is the same shape as the PB4 swap
(`c3939e7b1`), and it lands the same way: one commit with the arms that bound it.

## What is running (started 2026-10-04 ~00:00Z)

From the snapshot worktree `/var/tmp/se-qep-arms` (origin `24ece7adb` plus the world files of this
patch, locked). Its `producing_commit` will read `24ece7adb` with the patch uncommitted.

1. `longjob-qep-arms-three-arm`: `python3 -m tools.run_value_cycle_ab --level-arm --out
   docs/observability/value_cycle_ab_s1_three_arm_20261004q.json`. It waits on another lane's
   `decision_probe` (pid 2873381) for memory, then about 50 minutes.
2. `longjob-qep-arms-floor-handoff` (`/var/tmp/se-qep-arms-handoff.sh`): when the three-arm unit
   exits it launches `longjob-qep-arms-floor-s11111`, then `-s22222`, then `-s33333`, one at a
   time (`--noise-floor-seeds <s> --redraw-mode all`, about 2h40m each; memory does not allow two).
   It retries a refused admission every 5 minutes. It writes `END all three seeds exited` to
   `/var/tmp/longjob-qep-arms-floor-handoff.log`.

Total about 9 hours. Re-ask with `python3 -m background.launch_liveness --check`.

## The landing sequence, when all four artefacts exist

1. Fold the floor: `python3 -m tools.run_value_cycle_ab --fold <the three s*.json> --out
   docs/observability/value_cycle_ab_s1_noise_floor_20261004q.json`.
2. In a worktree at origin, apply the patch below (`git apply --3way`), delete
   `tests/architecture/test_a_refuted_commons_artefact_cannot_quietly_become_current.py` (retired
   with its subject), copy in `docs/reports/qep_g_second_qep_pass_anchor_departure_factors*.json`
   (landed with this doc), and regenerate the six verdicts on G:
   `python3 -m tools.fit_year_level_anchor --emergent-verdict` / `--route-attribution` /
   `--svt-shortfall` / `--composition` / `--internal-return`, then
   `python3 -m tools.published_route_split --write`.
3. Move `CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH` in
   `tools/generate_value_arms_data.py` onto the `20261004q` pair; regenerate `site/data/value_arms.json`.
4. Re-key the value-arms reds the way `c3939e7b1` did: stamp the witness onto the live world where
   the world is incidental to the guard, re-pin where a control pinned the old world's answer.
   Measured red on this patch without arms: 8 in `tests/tools/test_generate_value_arms_data.py`,
   6 in `tests/tools/test_the_value_arms_pages_undriven_pointers.py`, 4 in
   `site/test_the_baseline_comparison_reaches_the_reader.py`.
5. The arms ran from `24ece7adb`; `_code_since_the_run` will name every `simulation/` and
   `company/` path that differs at the publishing HEAD. This patch's own paths
   (`simulation/departure_level_anchor.py`, `company/crm/market_conditions.py`,
   `company/market/market_report.py`) were what the run executed, uncommitted; argue them in
   `docs/design/value_arms_substrate_exemptions.json`. Any other lane's path is a real staleness.
6. Land with `surgical_land`, then `promote_worktree_landing --work-id
   refit-the-level-anchor-onto-desnz-qep-2-7-1`.

If origin moves the anchor block or the commons before then, this patch is stale: re-capture.

## The patch (code, controls, commons; against `24ece7adb`)

```diff
diff --git a/company/crm/market_conditions.py b/company/crm/market_conditions.py
index 94b90d978..226c5f049 100644
--- a/company/crm/market_conditions.py
+++ b/company/crm/market_conditions.py
@@ -110,7 +110,9 @@ def _load_published_rate_pct() -> dict[int, float]:
                 f"switching commons entry for {entry.get('year')} has band ({lo}, {hi}), which "
                 "is not an ordered rate range"
             )
-        series[int(entry["year"])] = round((lo + hi) / 2.0, 2)
+        # Three places, the precision the commons publishes since version 2 (2026-10-03): its
+        # bands are a published count's rounding, ~0.004pp wide, and a 2dp midpoint falls outside.
+        series[int(entry["year"])] = round((lo + hi) / 2.0, 3)
     return series
 
 
@@ -139,9 +141,9 @@ def market_conditions_multiplier(renewal_year: int | None) -> float:
     """Return the published market-switching-opportunity multiplier for `renewal_year`.
 
     Normalised so `MULTIPLIER_REFERENCE_YEAR` (2024, post-fairer-pricing-rule) = 1.0. Below 1.0
-    means the published record shows less switching than that baseline (2022 crisis: 0.25, on a
-    published 2.9-4.3%); above 1.0 means more (2020 high-water mark: 1.59, on a published
-    22.5-23.0%).
+    means the published record shows less switching than that baseline (2022 crisis: 0.34, on a
+    published 3.06%); above 1.0 means more (2019: 2.31, on a published 20.82%). DESNZ QEP 2.7.1,
+    via the commons.
 
     Returns DEFAULT_MULTIPLIER (1.0) for `None` or a year outside the published window.
     """
diff --git a/company/market/market_report.py b/company/market/market_report.py
index 5548834da..663b2ba1a 100644
--- a/company/market/market_report.py
+++ b/company/market/market_report.py
@@ -56,9 +56,13 @@ _UK_DOMESTIC_ACCOUNTS_M: dict[int, float] = {
 # or retired before anything calibrated against it; nothing had. It reached no caller, so no shipped
 # figure moves -- but it is exactly the clean importable accessor a future build would have reached
 # for as a calibration target, which is what §9 predicted and why it is corrected rather than left.
+#
+# RE-READ 2026-10-03 ONTO DESNZ QEP 2.7.1 (the commons' version 2). The midpoints above were of
+# bands the publisher refuted in 8 of 10 years. These are the published rates themselves --
+# electricity transfers over that year's electricity customers -- to the precision the band bears.
 _UK_SWITCHING_RATE_PCT: dict[int, float] = {
-    2016: 17.3, 2017: 13.8, 2018: 19.8, 2019: 21.0, 2020: 22.8,
-    2021: 18.2, 2022: 3.6,  2023: 10.7, 2024: 14.3, 2025: 16.1,
+    2016: 15.816, 2017: 18.195, 2018: 19.064, 2019: 20.822, 2020: 20.213,
+    2021: 15.569, 2022: 3.056,  2023: 6.332,  2024: 9.028,  2025: 10.400,
 }
 
 
diff --git a/docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json b/docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json
index 79b6673fc..6409adcf7 100644
--- a/docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json
+++ b/docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json
@@ -1,113 +1,123 @@
 {
   "artefact": "gb_domestic_switching_rate",
-  "version": 1,
+  "version": 2,
   "published_by": "DESNZ (Quarterly Domestic Energy Switching Statistics) and Energy UK, with Ofgem Retail Market Indicators as the live monthly series",
   "what_this_is": "THE PUBLISHED RECORD, NOT A READING OF IT. How many GB domestic electricity accounts changed supplier in each year, and how many accounts there were to change. Nothing here converts that into a supplier's book loss rate, a hazard, a per-renewal probability or a multiplier -- those are READINGS and each lane owns its own. The whole reason this artefact exists is that the world's departure LEVEL had never been compared with it: see docs/market_research/gb_switching_rate_denominators.md.",
   "basis": {
     "numerator": "EXTERNAL changes of supplier on a GB domestic ELECTRICITY meter point (MPAN), counted once per transfer. NOT tariff switches within the same supplier, which Ofgem's survey instruments do count and which are a different quantity.",
     "denominator": "ALL GB domestic electricity accounts, whether or not the account was at a decision point that year. A household mid-way through a fixed term is in the denominator and cannot be in the numerator. Any comparison that narrows the denominator to accounts AT a renewal point is measuring something else and will read high.",
     "units": "per cent of domestic electricity accounts per calendar year",
-    "denominator_count_millions": 28.0,
-    "denominator_count_note": "CORRECTED 2026-09-07, AND THE CORRECTION IS LEFT BESIDE THE CLAIM IT REPLACES. This field used to say GB domestic electricity accounts sat between 27.5m and 28.3m across 2016-2025 (company/market/market_report.py::_UK_DOMESTIC_ACCOUNTS_M, from Ofgem Retail Market Indicators), and that a 28.0m flat denominator moves any year by less than 0.4pp. BOTH ARE FALSE against the publisher. DESNZ QEP table 2.7.1 publishes the denominator on the same table as the numerator, and it runs 27.947m (2016) to 30.249m (2025) -- 2025 is 1.9m outside the old stated band, and the flat 28.0m moves 2025 by 0.84pp. The annual figure is the mean of that year's four quarters, which is the right convention for a whole-year rate. `denominator_count_millions` is deliberately NOT changed here: it is part of the band repair described in `source_check.checked_for_supersession`, which must land with the re-fit rather than piecemeal.",
+    "denominator_count_millions": null,
+    "denominator_count_note": "PER YEAR SINCE VERSION 2: each row carries `accounts_millions`, the publisher's own denominator from the same table as the numerator (27.947m in 2016 to 30.249m in 2025). The flat 28.0m version 1 held moved 2025 by 0.84pp and is retired.",
     "what_this_is_NOT": "A supplier's churn rate is not read off this for free ONLY in the cross-sectional sense: switching is concentrated in engaged households, so individual suppliers vary. In AGGREGATE the identity is exact -- total switches equals the sum of suppliers' external losses, and total accounts equals the sum of their books, so the account-weighted mean supplier loss rate IS this rate. An average-engagement book loses at this rate; it is not an upper bound on one."
   },
-  "series_source": "REFUTED 2026-09-07 AS A READING OF DESNZ SWITCHING STATISTICS -- see `source_check`. The table number was wrong at the root: the derivation cites 'DESNZ Quarterly Energy Prices Table 2.1', which is a PRICES table; the switching table is 2.7.1, and its figures disagree with this series in 8 of 10 years. Kept verbatim below because it is what these `rates` were built from and the band has not yet been re-sited. Original: docs/market_research/churn_price_elasticity.md section 1 (DESNZ Quarterly Energy Prices Table 2.1; Energy UK switching statistics; Ofgem State of the Market). That series was live-adjudicated against Energy UK and GOV.UK in docs/market_research/f5_simulated_competitor_field.md section 9, which confirmed 2020 ~5.9m and 2021 5.1m switches and DISCONFIRMED the competing in-repo series by ~3x at 2021.",
-  "band_meaning": "lo and hi are the range the published record bears for that year, not a confidence interval. Where the source states a switch COUNT the band is that count over the denominator with a rounding allowance; where it states a range of counts the band is that range. A reading inside the band is consistent with the published record; a reading outside it is not.",
+  "series_source": "DESNZ Quarterly Energy Prices table 2.7.1 (Annual sheet), edition 2026-06-30 (data to Jan-Mar 2026), sha256 6cd4dee481faf8f71068fa1ca7f86ef9cf049e546336d93c54d35368740c75b4: 'Electricity Transfers' over 'Total Electricity Customers'. RE-SITED 2026-10-03. Version 1's rates came from docs/market_research/churn_price_elasticity.md section 1, which cited 'DESNZ Quarterly Energy Prices Table 2.1' (a PRICES table) and disagreed with the publisher in 8 of 10 years; that refutation is in docs/staging/done/SEAT_FINDING_THE_SWITCHING_BANDS_OWN_PUBLISHER_DISAGREES_WITH_IT_IN_EIGHT_OF_TEN_YEARS_2026-09-07.md and the retired bands are in git history at version 1.",
+  "band_meaning": "lo and hi are the range the published COUNT bears at the precision DESNZ prints it (thousands of transfers), over that year's published accounts. They are not a confidence interval and not a statement about revisions: DESNZ revises the rolling table quarterly, and `source_check.how_to_recheck` is what notices.",
   "provenance_legend": {
-    "primary": "the value was read from the PUBLISHER's own release for THIS year -- a named DESNZ Quarterly Domestic Energy Switching Statistics edition, or the Energy UK release for that year -- during the pass that wrote the entry. NO ENTRY IN THIS FILE IS PRIMARY, and the level is defined here because reaching it is this artefact's own stated open job: `how_to_recheck` already says this file cites a derivation and not an edition, and names the missing thing as the specific DESNZ release each rate was read from.",
-    "secondary": "the band was taken from the in-repo derivation named in `series_source` (docs/market_research/churn_price_elasticity.md section 1, itself built from a DESNZ quarterly series), not from the publisher's own release for that year. Two years were separately live-adjudicated against Energy UK and GOV.UK -- 2020 at ~5.9m switches and 2021 at 5.1m, which also DISCONFIRMED a competing in-repo series by ~3x -- and that is why the series is believed. It is not why any single entry would be primary. EVERY ENTRY IN THIS FILE IS SECONDARY.",
+    "primary": "the value was read from the PUBLISHER's own table -- DESNZ QEP 2.7.1, a single rolling table whose Annual sheet carries every year, so there is no per-year edition and the edition read is named in `series_source`. EVERY ENTRY IN THIS FILE IS PRIMARY since version 2.",
+    "secondary": "the band was taken from an in-repo derivation rather than the publisher. Version 1 was entirely secondary and was refuted by the publisher; none remain.",
     "recalled": "author recall, NEVER fetched. There are none in this file. The level is kept so that an unsourced year added later has somewhere honest to go instead of taking the strongest level in the file because it is the only one defined."
   },
   "rates": [
     {
       "year": 2016,
-      "switches_millions_lo": 4.76,
-      "switches_millions_hi": 4.93,
-      "rate_pct_lo": 17.0,
-      "rate_pct_hi": 17.6,
-      "provenance": "secondary",
-      "note": "4.82m stated; peak challenger era."
+      "switches_millions_lo": 4.4195,
+      "switches_millions_hi": 4.4205,
+      "accounts_millions": 27.947,
+      "rate_pct_lo": 15.813,
+      "rate_pct_hi": 15.818,
+      "provenance": "primary",
+      "note": "4.420m electricity transfers over 27.947m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m). peak challenger era."
     },
     {
       "year": 2017,
-      "switches_millions_lo": 3.78,
-      "switches_millions_hi": 3.92,
-      "rate_pct_lo": 13.5,
-      "rate_pct_hi": 14.0,
-      "provenance": "secondary",
-      "note": "3.84m stated; market consolidation."
+      "switches_millions_lo": 5.1175,
+      "switches_millions_hi": 5.1185,
+      "accounts_millions": 28.129,
+      "rate_pct_lo": 18.192,
+      "rate_pct_hi": 18.197,
+      "provenance": "primary",
+      "note": "5.118m electricity transfers over 28.129m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m). a RISE on 2016, not consolidation -- the retired band held 3.84m here."
     },
     {
       "year": 2018,
-      "switches_millions_lo": 5.46,
-      "switches_millions_hi": 5.6,
-      "rate_pct_lo": 19.5,
-      "rate_pct_hi": 20.0,
-      "provenance": "secondary",
-      "note": "5.54m stated; pre-cap surge."
+      "switches_millions_lo": 5.4015,
+      "switches_millions_hi": 5.4025,
+      "accounts_millions": 28.336,
+      "rate_pct_lo": 19.062,
+      "rate_pct_hi": 19.066,
+      "provenance": "primary",
+      "note": "5.402m electricity transfers over 28.336m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m). pre-cap surge."
     },
     {
       "year": 2019,
-      "switches_millions_lo": 5.8,
-      "switches_millions_hi": 5.96,
-      "rate_pct_lo": 20.7,
-      "rate_pct_hi": 21.3,
-      "provenance": "secondary",
-      "note": "5.88m stated, corroborated live by Energy UK. Default Tariff Cap live from January."
+      "switches_millions_lo": 5.9455,
+      "switches_millions_hi": 5.9465,
+      "accounts_millions": 28.556,
+      "rate_pct_lo": 20.82,
+      "rate_pct_hi": 20.824,
+      "provenance": "primary",
+      "note": "5.946m electricity transfers over 28.556m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m). Default Tariff Cap live from January; the record's high-water mark on this table."
     },
     {
       "year": 2020,
-      "switches_millions_lo": 6.3,
-      "switches_millions_hi": 6.44,
-      "rate_pct_lo": 22.5,
-      "rate_pct_hi": 23.0,
-      "provenance": "secondary",
-      "note": "6.39m stated, corroborated live (~5.9m on the Energy UK count). The record's high-water mark."
+      "switches_millions_lo": 5.8105,
+      "switches_millions_hi": 5.8115,
+      "accounts_millions": 28.749,
+      "rate_pct_lo": 20.211,
+      "rate_pct_hi": 20.215,
+      "provenance": "primary",
+      "note": "5.811m electricity transfers over 28.749m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m)."
     },
     {
       "year": 2021,
-      "switches_millions_lo": 5.01,
-      "switches_millions_hi": 5.15,
-      "rate_pct_lo": 17.9,
-      "rate_pct_hi": 18.4,
-      "provenance": "secondary",
-      "note": "5.06m stated; Energy UK 5.1m, '14% lower than 2020'. H2 near zero as suppliers withdrew products."
+      "switches_millions_lo": 4.5015,
+      "switches_millions_hi": 4.5025,
+      "accounts_millions": 28.916,
+      "rate_pct_lo": 15.567,
+      "rate_pct_hi": 15.571,
+      "provenance": "primary",
+      "note": "4.502m electricity transfers over 28.916m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m). H2 near zero as suppliers withdrew products."
     },
     {
       "year": 2022,
-      "switches_millions_lo": 0.8,
-      "switches_millions_hi": 1.2,
-      "rate_pct_lo": 2.9,
-      "rate_pct_hi": 4.3,
-      "provenance": "secondary",
-      "note": "The crisis trough. Nothing was cheaper than a capped SVT, so there was nowhere to go."
+      "switches_millions_lo": 0.8925,
+      "switches_millions_hi": 0.8935,
+      "accounts_millions": 29.224,
+      "rate_pct_lo": 3.053,
+      "rate_pct_hi": 3.058,
+      "provenance": "primary",
+      "note": "0.893m electricity transfers over 29.224m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m). The crisis trough. Nothing was cheaper than a capped SVT, so there was nowhere to go."
     },
     {
       "year": 2023,
-      "switches_millions_lo": 2.5,
-      "switches_millions_hi": 3.5,
-      "rate_pct_lo": 8.9,
-      "rate_pct_hi": 12.5,
-      "provenance": "secondary",
-      "note": "Recovery begins; fairer-pricing rule in force."
+      "switches_millions_lo": 1.8665,
+      "switches_millions_hi": 1.8675,
+      "accounts_millions": 29.487,
+      "rate_pct_lo": 6.329,
+      "rate_pct_hi": 6.334,
+      "provenance": "primary",
+      "note": "1.867m electricity transfers over 29.487m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m). Recovery begins; fairer-pricing rule in force."
     },
     {
       "year": 2024,
-      "switches_millions_lo": 3.5,
-      "switches_millions_hi": 4.5,
-      "rate_pct_lo": 12.5,
-      "rate_pct_hi": 16.1,
-      "provenance": "secondary",
-      "note": "Post-ban equilibrium. Ofgem describes switching as still below pre-crisis levels, and it is -- against a 2020 of 23%."
+      "switches_millions_lo": 2.6805,
+      "switches_millions_hi": 2.6815,
+      "accounts_millions": 29.695,
+      "rate_pct_lo": 9.026,
+      "rate_pct_hi": 9.031,
+      "provenance": "primary",
+      "note": "2.681m electricity transfers over 29.695m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m). Post-ban; still about half the pre-crisis rate."
     },
     {
       "year": 2025,
-      "switches_millions_lo": 4.0,
-      "switches_millions_hi": 5.0,
-      "rate_pct_lo": 14.3,
-      "rate_pct_hi": 17.9,
-      "provenance": "secondary",
-      "note": "Continued normalisation."
+      "switches_millions_lo": 3.1455,
+      "switches_millions_hi": 3.1465,
+      "accounts_millions": 30.249,
+      "rate_pct_lo": 10.398,
+      "rate_pct_hi": 10.402,
+      "provenance": "primary",
+      "note": "3.146m electricity transfers over 30.249m electricity customers (mean of the year's quarters), DESNZ QEP 2.7.1 (Annual), edition 2026-06-30. Band = the published count's rounding (+/-0.0005m). Continued normalisation."
     }
   ],
   "unreconciled_cross_check": {
@@ -126,138 +136,9 @@
     "version_token_is": "publisher_page_date",
     "how_to_recheck": "GET https://www.gov.uk/api/content/government/statistical-data-sets/quarterly-domestic-energy-switching-statistics and read `public_updated_at`; a value later than `version_token` means a new quarter has been published. THE ATTACHMENT URL IS A ROLLING ASSET AND MUST NOT BE THE KEY -- take `details.attachments[0].url` from that same response rather than storing it, because the asset hash changes at every edition (the RO artefact's rolling-window failure, one publication over). The workbook states its own edition on the Cover Sheet -- publication date, data period, next update -- so an edition read from the file needs no page metadata to be stamped. The figures are on the '2.7.1 (Annual)' sheet: 'Electricity Transfers' over 'Total Electricity Customers', both of which are GB domestic meter points (Note 4), non-domestic filtered since April 2016 (Note 5), NI excluded. NOT A PER-YEAR RELEASE: DESNZ publishes one rolling table revised quarterly whose Annual sheet carries every year from 2003, so there is no 'edition for 2019' to fetch and the `provenance_legend.primary` definition, which asks for one, is unreachable as written.",
     "checked_for_supersession": {
-      "on": "2026-09-07",
-      "found": "superseded",
-      "note": "SETTLED FROM `cannot_tell` ON 2026-09-07 BY FETCHING THE PUBLISHER, AND THE ANSWER IS WORSE THAN A STALE EDITION -- the publisher's own figures fall OUTSIDE the band in 8 of the 10 years, including every year from 2020 on. Edition read: publication date 30/06/2026, data period Jan-Mar 2026, sha256 6cd4dee481faf8f71068fa1ca7f86ef9cf049e546336d93c54d35368740c75b4. Published rates, electricity transfers over that year's electricity customers: 2016 15.82, 2017 18.19, 2018 19.06, 2019 20.82, 2020 20.21, 2021 15.57, 2022 3.06, 2023 6.33, 2024 9.03, 2025 10.40. Only 2019 and 2022 are inside. THE VERDICT IS ROBUST TO BOTH OBVIOUS RESCUES, CHECKED BEFORE IT WAS CLAIMED: against this artefact's own flat 28.0m denominator it is still 8 of 10 outside and the same 8 years; read as both fuels it is 8 of 10 outside too, and inside on DIFFERENT years (2023, 2024) than the electricity reading (2019, 2022). 2017 is not merely off but inverted -- the artefact holds 3.84m and calls it consolidation, the publisher has 5.118m, a 16 per cent RISE. THE BAND IS NOT REPAIRED IN THIS PASS AND THAT IS A JUDGEMENT: simulation/departure_level_anchor.py's YEAR_LEVEL_ANCHOR is fitted to each band's HIGH endpoint with 0.00pp of room above in all ten years, the new figures sit 3.5-7.1pp below it in 2023-2025, and re-siting `rates` without a re-capture and re-fit would put a whole-tree red at HEAD and wedge every lane. The band change and the re-fit are one atom and must land together.",
-      "open_finding": "docs/staging/done/SEAT_FINDING_THE_SWITCHING_BANDS_OWN_PUBLISHER_DISAGREES_WITH_IT_IN_EIGHT_OF_TEN_YEARS_2026-09-07.md"
+      "on": "2026-10-03",
+      "found": "current",
+      "note": "Version 2's rates ARE the edition read on 2026-09-07 (publication 30/06/2026, sha256 above), so they agree with it by construction. The refutation of version 1 that stood here, and the machine-readable `values_refuted_by_the_publisher` block, are retired with the values they refuted."
     }
-  },
-  "values_refuted_by_the_publisher": {
-    "what_this_is": "THE MACHINE-READABLE FORM of the refutation stated in prose in `source_check.checked_for_supersession.note`, added 2026-09-07 by a second lane that reached the same conclusion independently and concurrently. It is not a second opinion and it does not restate the verdict -- it exists so the claim can be CHECKED rather than read. `tests/architecture/test_a_refuted_commons_artefact_cannot_quietly_become_current.py` recomputes every flag below from the bands in `rates` on every run.",
-    "why_it_is_not_redundant": "A refutation written as prose beside the values it refutes goes stale silently and in the flattering direction. The cheapest way to make this finding disappear is not to correct a value -- it is to WIDEN one band until it swallows the publisher's figure, which moves no rate and reads as a refinement. Nothing held that shut. The control also fires the other way: when the real repair lands, every flag flips true and it forces this block to be regenerated or removed rather than left accusing the file of a defect it has fixed.",
-    "headline": "8 of 10 bands do not contain the publisher's own figure for that year.",
-    "comparison": [
-      {
-        "year": 2016,
-        "published_switches_millions": 4.42,
-        "published_accounts_millions": 27.947,
-        "published_gas_switches_millions_not_in_numerator": 3.347,
-        "published_rate_pct": 15.816,
-        "this_files_band_pct": [
-          17.0,
-          17.6
-        ],
-        "band_contains_the_publisher": false
-      },
-      {
-        "year": 2017,
-        "published_switches_millions": 5.118,
-        "published_accounts_millions": 28.129,
-        "published_gas_switches_millions_not_in_numerator": 4.144,
-        "published_rate_pct": 18.195,
-        "this_files_band_pct": [
-          13.5,
-          14.0
-        ],
-        "band_contains_the_publisher": false
-      },
-      {
-        "year": 2018,
-        "published_switches_millions": 5.402,
-        "published_accounts_millions": 28.336,
-        "published_gas_switches_millions_not_in_numerator": 4.517,
-        "published_rate_pct": 19.064,
-        "this_files_band_pct": [
-          19.5,
-          20.0
-        ],
-        "band_contains_the_publisher": false
-      },
-      {
-        "year": 2019,
-        "published_switches_millions": 5.946,
-        "published_accounts_millions": 28.556,
-        "published_gas_switches_millions_not_in_numerator": 4.822,
-        "published_rate_pct": 20.822,
-        "this_files_band_pct": [
-          20.7,
-          21.3
-        ],
-        "band_contains_the_publisher": true
-      },
-      {
-        "year": 2020,
-        "published_switches_millions": 5.811,
-        "published_accounts_millions": 28.749,
-        "published_gas_switches_millions_not_in_numerator": 4.336,
-        "published_rate_pct": 20.213,
-        "this_files_band_pct": [
-          22.5,
-          23.0
-        ],
-        "band_contains_the_publisher": false
-      },
-      {
-        "year": 2021,
-        "published_switches_millions": 4.502,
-        "published_accounts_millions": 28.916,
-        "published_gas_switches_millions_not_in_numerator": 3.082,
-        "published_rate_pct": 15.569,
-        "this_files_band_pct": [
-          17.9,
-          18.4
-        ],
-        "band_contains_the_publisher": false
-      },
-      {
-        "year": 2022,
-        "published_switches_millions": 0.893,
-        "published_accounts_millions": 29.224,
-        "published_gas_switches_millions_not_in_numerator": 0.566,
-        "published_rate_pct": 3.056,
-        "this_files_band_pct": [
-          2.9,
-          4.3
-        ],
-        "band_contains_the_publisher": true
-      },
-      {
-        "year": 2023,
-        "published_switches_millions": 1.867,
-        "published_accounts_millions": 29.487,
-        "published_gas_switches_millions_not_in_numerator": 1.195,
-        "published_rate_pct": 6.332,
-        "this_files_band_pct": [
-          8.9,
-          12.5
-        ],
-        "band_contains_the_publisher": false
-      },
-      {
-        "year": 2024,
-        "published_switches_millions": 2.681,
-        "published_accounts_millions": 29.695,
-        "published_gas_switches_millions_not_in_numerator": 2.092,
-        "published_rate_pct": 9.028,
-        "this_files_band_pct": [
-          12.5,
-          16.1
-        ],
-        "band_contains_the_publisher": false
-      },
-      {
-        "year": 2025,
-        "published_switches_millions": 3.146,
-        "published_accounts_millions": 30.249,
-        "published_gas_switches_millions_not_in_numerator": 2.474,
-        "published_rate_pct": 10.4,
-        "this_files_band_pct": [
-          14.3,
-          17.9
-        ],
-        "band_contains_the_publisher": false
-      }
-    ],
-    "what_this_block_does_not_settle": "Anything about the world. The world reads `rate_pct_hi` live, so the repair drops its target 16.1% on the mean and 42-49% in 2023-2025, and simulation/departure_level_anchor.py records six of seven fitted years BELOW their band by 3.3-9.0pp -- so the record is about to move TOWARD the world and part of that standing gap is this file being wrong rather than the world being wrong. HOW MUCH IS NOT ESTABLISHED AND MUST NOT BE GUESSED. Written down before the re-capture runs so it cannot be filed as a prediction afterwards, and so that a gap shrinking because its target moved is not read as the mechanism improving."
   }
-}
\ No newline at end of file
+}
diff --git a/simulation/departure_level_anchor.py b/simulation/departure_level_anchor.py
index 5f01a8d94..32697245c 100644
--- a/simulation/departure_level_anchor.py
+++ b/simulation/departure_level_anchor.py
@@ -240,14 +240,31 @@ NO_LEVEL_CORRECTION = 1.0
 #: standing-charge change did not move this fit. 2020, 2021 and 2024 now all stand above 17, on
 #: 8-12 renewal decisions each. The values are graded on capture D:
 #: `docs/staging/records/SEAT_PREREGISTRATION_THE_PB4_FOURTH_PASS_IN_THE_EX_VAT_STANDING_CHARGE_WORLD_2026-10-01.md`.
+#: ─────────────────────────────────────────────────────────────────────────────────────────────
+#: FIFTH AND SIXTH PASSES, 2026-10-03, AND THE TARGET ITSELF MOVED. The commons was re-sited from
+#: the refuted version-1 bands onto DESNZ QEP 2.7.1 (`gb_domestic_switching_rate.json` version 2),
+#: so every block above was fitted to a record the publisher contradicts in 8 of 10 years. The
+#: correction reaches the world twice: `market_departure_rate` (this fit's target) fell in every
+#: year but 2017, and `market_switching_multiplier`, a ratio over 2024, roughly doubled in
+#: 2017-2021 because 2024 fell the most. So the world departs harder before 2022 at ANY anchor,
+#: the book is smaller after it (2024: 49 accounts and 4 renewal decisions, against 65 and 12 under
+#: the fourth pass), and 2024's anchor ROSE although its target fell 16.1 -> 9.03.
+#: Captured E (new record, fourth-pass block), fitted, captured F, re-fitted 2021 and 2024 only
+#: (2017-2020 sat on target to 0.01pp), captured G. On G every fitted year is within 0.3pp of the
+#: record, which is under 0.15 of one expected departure on its book. 2023 now has NO renewal
+#: decisions in the capture and sits at its SVT floor, 4.52% against 6.33%, LOW, with no lever;
+#: its value is kept and multiplies nothing. 2024's 20.8 stands on 4 renewal decisions: the clamp
+#: carries more of the level than ever, and that is the rung-1 debt, stated. Captures and grades:
+#: `docs/staging/records/SEAT_PREREGISTRATION_THE_LEVEL_ANCHOR_REFIT_ONTO_DESNZ_QEP_2_7_1_2026-10-03.md`
+#: and its sibling result.
 YEAR_LEVEL_ANCHOR: dict[int, float] = {
-    2017: 6.990171,
-    2018: 5.269958,
-    2019: 8.583067,
-    2020: 19.550406,
-    2021: 18.474462,
+    2017: 6.202429,
+    2018: 4.295421,
+    2019: 8.081564,
+    2020: 8.402043,
+    2021: 7.733780,
     2023: 2.033232,
-    2024: 17.128306,
+    2024: 20.817509,
 }
 
 #: `{year inside the published record with no fitted anchor: WHY}`. This is the half of the
@@ -299,7 +316,9 @@ UNFITTED_YEARS: dict[int, str] = {
         "ANCHOR still does not reach `svt_inertia` -- `departure_risks`'s `CAUSE_SVT_INERTIA` line "
         "carries no `level_anchor`. THE FLOOR IS WHAT MOVED. `c628cb37d` gave `svt_inertia_hazard` "
         "a required `market_switching_multiplier`, and recomputed under that hazard its SVT floor "
-        "is 2.54% against a published 4.30% ceiling -- BELOW the target, not 7.8pp above it. THAT "
+        "was 2.54% against a published 4.30% ceiling -- BELOW the target, not 7.8pp above it. "
+        "Since the commons moved onto DESNZ QEP 2.7.1 (2026-10-03) the same rows give: SVT floor "
+        "is 1.94% against a published 3.06% ceiling -- still BELOW, so the conclusion stands. THAT "
         "FIGURE READ 2.34% UNTIL 2026-09-02 AND ITS CAPTURE WAS NOT COMMITTED: it was re-driven "
         "from `c2_departure_factors.json` paired with an UNTRACKED SVT sibling, which is why the "
         "leg holding it was green in one worktree and red at clean HEAD in every other. It is now "
diff --git a/tests/architecture/test_switching_rate_commons.py b/tests/architecture/test_switching_rate_commons.py
index eda2c4e04..479deb4ef 100644
--- a/tests/architecture/test_switching_rate_commons.py
+++ b/tests/architecture/test_switching_rate_commons.py
@@ -317,8 +317,14 @@ def test_the_commons_declares_both_a_numerator_and_a_denominator():
     number says so. An artefact that omits either half is not a record, it is a decoration.
     """
     basis = _commons()["basis"]
-    for key in ("numerator", "denominator", "units", "denominator_count_millions"):
+    for key in ("numerator", "denominator", "units"):
         assert basis.get(key), f"the commons basis omits {key!r}: a figure without its basis is R14"
+    # The denominator's SIZE, flat in `basis` (version 1) or per year on every row (version 2,
+    # the publisher's own column). MUTATION: drop `accounts_millions` from one row and this fires.
+    rows_without = [r["year"] for r in _commons()["rates"] if not r.get("accounts_millions")]
+    assert basis.get("denominator_count_millions") or not rows_without, (
+        f"the commons states no denominator count, flat or for years {rows_without}: R14"
+    )
     assert "electricity" in basis["numerator"].lower()
     assert "electricity" in basis["denominator"].lower()
 
@@ -4160,26 +4166,32 @@ def test_a_joint_phi_above_one_is_not_reported_as_a_refusal(tmp_path, monkeypatc
     nothing.
     """
     split = _split_module()
-    live_straddles, live_above = _assert_the_two_phi_refusals_are_distinct(_joint(), split)
-
-    straddles, above = live_straddles, live_above
-    source = json.loads(split.COMPOSITION_ARTEFACT.read_text())
-    for scale in (0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1):
-        perturbed = json.loads(json.dumps(source))
-        for row in perturbed["per_year"].values():
-            for basis in row["bases"].values():
-                for endpoint in basis.values():
-                    for accounting in ("renewal_rescaled", "renewal_held"):
-                        cell = endpoint[accounting]
-                        if cell["hazard_multiple_still_required_at_band_low"] is not None:
-                            cell["hazard_multiple_still_required_at_band_low"] *= scale
-        moved = tmp_path / f"composition_{scale}.json"
-        moved.write_text(json.dumps(perturbed))
-        monkeypatch.setattr(split, "COMPOSITION_ARTEFACT", moved)
-        s, a = _assert_the_two_phi_refusals_are_distinct(split.where_the_worlds_joint_point_falls(),
-                                                         split)
+    original = split.COMPOSITION_ARTEFACT
+    straddles = above = 0
+    # And on a band with width too: on the live QEP record no perturbation of the composition
+    # alone produces a straddle (measured 2026-10-03).
+    for band in _band_sources(monkeypatch):
+        monkeypatch.setattr(split, "COMPOSITION_ARTEFACT", original)
+        s, a = _assert_the_two_phi_refusals_are_distinct(_joint(), split)
         straddles += s
         above += a
+        source = json.loads(original.read_text())
+        for scale in (0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1):
+            perturbed = json.loads(json.dumps(source))
+            for row in perturbed["per_year"].values():
+                for basis in row["bases"].values():
+                    for endpoint in basis.values():
+                        for accounting in ("renewal_rescaled", "renewal_held"):
+                            cell = endpoint[accounting]
+                            if cell["hazard_multiple_still_required_at_band_low"] is not None:
+                                cell["hazard_multiple_still_required_at_band_low"] *= scale
+            moved = tmp_path / f"composition_{band}_{scale}.json"
+            moved.write_text(json.dumps(perturbed))
+            monkeypatch.setattr(split, "COMPOSITION_ARTEFACT", moved)
+            s, a = _assert_the_two_phi_refusals_are_distinct(
+                split.where_the_worlds_joint_point_falls(), split)
+            straddles += s
+            above += a
     assert straddles, (
         "no phi interval straddles 1.0 anywhere in the live reading or its perturbations, so a flag "
         "that fired on 'phi reaches above 1' would be indistinguishable from one that fires on 'phi "
@@ -4339,6 +4351,29 @@ def _carrying() -> dict:
     return _split_module().how_much_of_the_records_move_the_share_series_can_carry()
 
 
+#: A BAND WITH WIDTH, for the reachability arms of the legs below and for nothing else. Since
+#: 2026-10-03 the commons states each year as DESNZ QEP 2.7.1 prints it, a published count's
+#: rounding about 0.004pp wide, so on the live record the phi spans have almost no width and
+#: several branches these legs must prove reachable cannot be reached from live data at all
+#: (measured: all six went red on that edit alone). These are the commons' version-1 bands, retired
+#: as a RECORD because the publisher refuted them in 8 of 10 years, and kept here only as an input
+#: whose width is known to reach both branches. Every value check still runs on the live record.
+_A_BAND_WITH_WIDTH = {
+    2016: (17.0, 17.6), 2017: (13.5, 14.0), 2018: (19.5, 20.0), 2019: (20.7, 21.3),
+    2020: (22.5, 23.0), 2021: (17.9, 18.4), 2022: (2.9, 4.3), 2023: (8.9, 12.5),
+    2024: (12.5, 16.1), 2025: (14.3, 17.9),
+}
+
+
+def _band_sources(monkeypatch):
+    """Yield `"live"`, then `"with_width"` with the route split reading `_A_BAND_WITH_WIDTH`."""
+    yield "live"
+    monkeypatch.setattr(
+        _split_module(), "published_departure_band", lambda: dict(_A_BAND_WITH_WIDTH)
+    )
+    yield "with_width"
+
+
 def test_the_phi_span_widens_with_the_segment_band():
     """MUTATION: swap the endpoints in `phi_span_at_a_segment_band` and this fires.
 
@@ -4383,7 +4418,7 @@ def test_the_phi_span_widens_with_the_segment_band():
     )
 
 
-def test_the_constant_phi_verdict_is_recomputed_from_the_published_series():
+def test_the_constant_phi_verdict_is_recomputed_from_the_published_series(monkeypatch):
     """MUTATION: write any intersection down, drop a band, or key a verdict to today's answer.
 
     THE LEG THAT HOLDS §13's HEADLINE. Every verdict is recomputed longhand here from
@@ -4397,49 +4432,52 @@ def test_the_constant_phi_verdict_is_recomputed_from_the_published_series():
     be, because a constant would break the other band in the same run.
     """
     split = _split_module()
-    reading = _constant_phi()
     seen_verdicts = set()
-    for basis in split.BASES:
-        for band_name, band in reading["published_segment_bands"].items():
-            for set_name, years in reading["year_sets"].items():
-                cell = reading["verdicts"][basis][band_name][set_name]
-                assert cell["years"] == years, (
-                    f"{basis}/{band_name}/{set_name}: the intersected year set is not the one the "
-                    f"reading declares it is."
-                )
-                spans = []
-                for year_s in years:
-                    year = int(year_s)
-                    r_lo, r_hi = split.published_departure_band()[year]
-                    s_band = split.default_tariff_share(year, basis)
-                    phis = [
-                        (r / 100.0 - s * h)
-                        / ((1.0 - s) * split.FIXED_ACTIVE_RENEWAL_SHARE)
-                        for r in (r_lo, r_hi) for s in s_band for h in band
-                    ]
-                    longhand = [round(min(phis), 6), round(max(phis), 6)]
-                    assert reading["per_year"][year_s][basis][band_name] == longhand, (
-                        f"{year_s}/{basis}/{band_name}: the published phi span is not the one the "
-                        f"identity gives at the corners of the two published bands."
+    # Both branches were live on version 1's bands; on the QEP record every verdict refuses
+    # (2026-10-03), so the pass branch is reached on a band with width.
+    for _source in _band_sources(monkeypatch):
+        reading = _constant_phi()
+        for basis in split.BASES:
+            for band_name, band in reading["published_segment_bands"].items():
+                for set_name, years in reading["year_sets"].items():
+                    cell = reading["verdicts"][basis][band_name][set_name]
+                    assert cell["years"] == years, (
+                        f"{basis}/{band_name}/{set_name}: the intersected year set is not the one the "
+                        f"reading declares it is."
                     )
-                    spans.append(longhand)
-                lo, hi = max(s[0] for s in spans), min(s[1] for s in spans)
-                assert cell["intersection"] == [round(lo, 6), round(hi, 6)], (
-                    f"{basis}/{band_name}/{set_name}: the intersection was written down rather "
-                    f"than taken over the per-year spans."
-                )
-                assert cell["is_non_empty"] == (lo <= hi), (
-                    f"{basis}/{band_name}/{set_name}: the verdict disagrees with the interval it "
-                    f"is read off."
-                )
-                seen_verdicts.add(cell["is_non_empty"])
-                for a, b in cell["minimal_refusing_pairs"]:
-                    pa = reading["per_year"][str(a)][basis][band_name]
-                    pb = reading["per_year"][str(b)][basis][band_name]
-                    assert max(pa[0], pb[0]) > min(pa[1], pb[1]), (
-                        f"{basis}/{band_name}/{set_name}: {a}/{b} is listed as a refusing pair and "
-                        f"its two spans overlap."
+                    spans = []
+                    for year_s in years:
+                        year = int(year_s)
+                        r_lo, r_hi = split.published_departure_band()[year]
+                        s_band = split.default_tariff_share(year, basis)
+                        phis = [
+                            (r / 100.0 - s * h)
+                            / ((1.0 - s) * split.FIXED_ACTIVE_RENEWAL_SHARE)
+                            for r in (r_lo, r_hi) for s in s_band for h in band
+                        ]
+                        longhand = [round(min(phis), 6), round(max(phis), 6)]
+                        assert reading["per_year"][year_s][basis][band_name] == longhand, (
+                            f"{year_s}/{basis}/{band_name}: the published phi span is not the one the "
+                            f"identity gives at the corners of the two published bands."
+                        )
+                        spans.append(longhand)
+                    lo, hi = max(s[0] for s in spans), min(s[1] for s in spans)
+                    assert cell["intersection"] == [round(lo, 6), round(hi, 6)], (
+                        f"{basis}/{band_name}/{set_name}: the intersection was written down rather "
+                        f"than taken over the per-year spans."
+                    )
+                    assert cell["is_non_empty"] == (lo <= hi), (
+                        f"{basis}/{band_name}/{set_name}: the verdict disagrees with the interval it "
+                        f"is read off."
                     )
+                    seen_verdicts.add(cell["is_non_empty"])
+                    for a, b in cell["minimal_refusing_pairs"]:
+                        pa = reading["per_year"][str(a)][basis][band_name]
+                        pb = reading["per_year"][str(b)][basis][band_name]
+                        assert max(pa[0], pb[0]) > min(pa[1], pb[1]), (
+                            f"{basis}/{band_name}/{set_name}: {a}/{b} is listed as a refusing pair and "
+                            f"its two spans overlap."
+                        )
     assert seen_verdicts == {True, False}, (
         f"only {seen_verdicts} appears across every band, basis and year set. One of the two "
         f"branches is unreachable, and a control whose pass branch cannot be reached reports a "
@@ -4447,7 +4485,7 @@ def test_the_constant_phi_verdict_is_recomputed_from_the_published_series():
     )
 
 
-def test_a_structural_break_is_excluded_by_name_and_still_reported():
+def test_a_structural_break_is_excluded_by_name_and_still_reported(monkeypatch):
     """MUTATION: drop 2022 from the scored set, or from `STRUCTURAL_BREAK_YEARS`, and this fires.
 
     Excluding a year from a headline is a judgement, and this repository's rule for one is that it
@@ -4458,40 +4496,43 @@ def test_a_structural_break_is_excluded_by_name_and_still_reported():
     exactly the scored set less the named breaks.
     """
     split = _split_module()
-    reading = _constant_phi()
-    breaks = reading["structural_breaks"]
-    assert breaks, "the structural-break register is empty; an exclusion with no reason is a drop."
-    scored = reading["year_sets"]["every_scored_year"]
-    headline = reading["year_sets"]["every_scored_year_less_structural_breaks"]
-    assert headline == [y for y in scored if y not in breaks], (
-        "the headline year set is not the scored set less exactly the NAMED breaks. Either a year "
-        "is being excluded without a reason or a named break is still in the headline."
-    )
-    for year_s, reason in breaks.items():
-        assert year_s in reading["per_year"], (
-            f"{year_s} is excluded from the headline and its own reading is not published. An "
-            f"exclusion the reader cannot check is an assertion."
+    changed = []
+    # On the QEP record no verdict turns on the break (2026-10-03); on a band with width one does.
+    for _source in _band_sources(monkeypatch):
+        reading = _constant_phi()
+        breaks = reading["structural_breaks"]
+        assert breaks, "the structural-break register is empty; an exclusion with no reason is a drop."
+        scored = reading["year_sets"]["every_scored_year"]
+        headline = reading["year_sets"]["every_scored_year_less_structural_breaks"]
+        assert headline == [y for y in scored if y not in breaks], (
+            "the headline year set is not the scored set less exactly the NAMED breaks. Either a year "
+            "is being excluded without a reason or a named break is still in the headline."
         )
-        assert reading["per_year"][year_s]["is_a_structural_break"], (
-            f"{year_s} is in the break register and its own row does not say so."
-        )
-        assert len(reason) > 80 and "." in reason, (
-            f"{year_s}'s exclusion reason is too short to be one."
-        )
-        for basis in split.BASES:
-            span = reading["per_year"][year_s][basis]["tenure_composed"]
-            assert span is not None, f"{year_s}/{basis}: the excluded year has no published span."
-    # AND THE EXCLUSION HAS TO MATTER. If the break years did not change the verdict there would be
-    # nothing to justify, and a register nobody's answer turns on is a register that will rot.
-    changed = [
-        (basis, band)
-        for basis in split.BASES
-        for band in reading["published_segment_bands"]
-        if reading["verdicts"][basis][band]["every_scored_year"]["is_non_empty"]
-        != reading["verdicts"][basis][band]["every_scored_year_less_structural_breaks"][
-            "is_non_empty"
+        for year_s, reason in breaks.items():
+            assert year_s in reading["per_year"], (
+                f"{year_s} is excluded from the headline and its own reading is not published. An "
+                f"exclusion the reader cannot check is an assertion."
+            )
+            assert reading["per_year"][year_s]["is_a_structural_break"], (
+                f"{year_s} is in the break register and its own row does not say so."
+            )
+            assert len(reason) > 80 and "." in reason, (
+                f"{year_s}'s exclusion reason is too short to be one."
+            )
+            for basis in split.BASES:
+                span = reading["per_year"][year_s][basis]["tenure_composed"]
+                assert span is not None, f"{year_s}/{basis}: the excluded year has no published span."
+        # AND THE EXCLUSION HAS TO MATTER. If the break years did not change the verdict there would be
+        # nothing to justify, and a register nobody's answer turns on is a register that will rot.
+        changed += [
+            (basis, band)
+            for basis in split.BASES
+            for band in reading["published_segment_bands"]
+            if reading["verdicts"][basis][band]["every_scored_year"]["is_non_empty"]
+            != reading["verdicts"][basis][band]["every_scored_year_less_structural_breaks"][
+                "is_non_empty"
+            ]
         ]
-    ]
     assert changed, (
         "excluding the structural break changes no verdict on any band or basis. Either the "
         "exclusion is doing nothing and should go, or the year sets have been wired to the same "
@@ -4499,7 +4540,7 @@ def test_a_structural_break_is_excluded_by_name_and_still_reported():
     )
 
 
-def test_the_mix_dependence_flag_is_derived_and_not_frozen():
+def test_the_mix_dependence_flag_is_derived_and_not_frozen(monkeypatch):
     """MUTATION: freeze `verdict_is_mix_dependent`, either way, and this fires.
 
     §11 built this flag and §12's one-phi reading never applied it to itself. §13's headline turns
@@ -4511,23 +4552,25 @@ def test_the_mix_dependence_flag_is_derived_and_not_frozen():
     year, where 2022 refuses on both bands -- so a constant of either polarity breaks this.
     """
     split = _split_module()
-    reading = _constant_phi()
     seen = set()
-    for basis in split.BASES:
-        flags = reading["verdicts"][basis]["verdict_is_mix_dependent"]
-        assert set(flags) == set(reading["year_sets"]), (
-            f"{basis}: the mix-dependence flag does not cover every year set."
-        )
-        for set_name, flag in flags.items():
-            expected = (
-                reading["verdicts"][basis]["tenure_composed"][set_name]["is_non_empty"]
-                != reading["verdicts"][basis]["mix_free_envelope"][set_name]["is_non_empty"]
-            )
-            assert flag == expected, (
-                f"{basis}/{set_name}: the mix-dependence flag disagrees with the two verdicts it "
-                f"is supposed to be derived from. It has been written down."
+    # True is unreachable on the QEP record (2026-10-03); a band with width reaches it.
+    for _source in _band_sources(monkeypatch):
+        reading = _constant_phi()
+        for basis in split.BASES:
+            flags = reading["verdicts"][basis]["verdict_is_mix_dependent"]
+            assert set(flags) == set(reading["year_sets"]), (
+                f"{basis}: the mix-dependence flag does not cover every year set."
             )
-            seen.add(flag)
+            for set_name, flag in flags.items():
+                expected = (
+                    reading["verdicts"][basis]["tenure_composed"][set_name]["is_non_empty"]
+                    != reading["verdicts"][basis]["mix_free_envelope"][set_name]["is_non_empty"]
+                )
+                assert flag == expected, (
+                    f"{basis}/{set_name}: the mix-dependence flag disagrees with the two verdicts it "
+                    f"is supposed to be derived from. It has been written down."
+                )
+                seen.add(flag)
     assert seen == {True, False}, (
         f"the mix-dependence flag takes only {seen} across every basis and year set, so a frozen "
         f"constant would satisfy every assertion above."
@@ -4573,7 +4616,7 @@ def test_the_constant_pair_sweep_reports_its_slack_and_not_only_its_verdict():
         ), f"{basis}: the constant-pair verdict disagrees with its own count."
 
 
-def test_a_pair_the_record_requires_no_move_from_is_not_counted_as_carried():
+def test_a_pair_the_record_requires_no_move_from_is_not_counted_as_carried(monkeypatch):
     """MUTATION: count every pair in the denominator and this fires.
 
     THE PASS BRANCH THAT COULD NOT FAIL, caught on this reading's first run and repaired rather
@@ -4587,40 +4630,42 @@ def test_a_pair_the_record_requires_no_move_from_is_not_counted_as_carried():
     named in the exclusion list, and the count must be over what is left.
     """
     split = _split_module()
-    carrying = _carrying()
     vacuous_seen = False
-    for band_name, by_basis in carrying["by_band"].items():
-        for basis in split.BASES:
-            cell = by_basis[basis]
-            pairs = cell["pairs"]
-            for name, pair in pairs.items():
-                lo, hi = pair["record_move_pp"]
-                requires = not (lo <= 0.0 <= hi)
-                assert pair["record_requires_a_move"] == requires, (
-                    f"{band_name}/{basis}/{name}: `record_requires_a_move` disagrees with whether "
-                    f"the record's own move interval {pair['record_move_pp']} contains zero."
-                )
-                if not requires:
-                    vacuous_seen = True
-                    assert name in cell["pairs_excluded_because_the_record_requires_no_move"], (
-                        f"{band_name}/{basis}/{name}: the record requires no move here and the "
-                        f"pair is not in the exclusion list. It will be counted as carried."
+    # A ~0.004pp QEP band requires a move from every pair (2026-10-03); a band with width does not.
+    for _source in _band_sources(monkeypatch):
+        carrying = _carrying()
+        for band_name, by_basis in carrying["by_band"].items():
+            for basis in split.BASES:
+                cell = by_basis[basis]
+                pairs = cell["pairs"]
+                for name, pair in pairs.items():
+                    lo, hi = pair["record_move_pp"]
+                    requires = not (lo <= 0.0 <= hi)
+                    assert pair["record_requires_a_move"] == requires, (
+                        f"{band_name}/{basis}/{name}: `record_requires_a_move` disagrees with whether "
+                        f"the record's own move interval {pair['record_move_pp']} contains zero."
                     )
-            judged = {
-                k: v for k, v in pairs.items()
-                if v["record_requires_a_move"] and not v["spans_a_gap"]
-            }
-            assert cell["n_pairs_judged"] == len(judged), (
-                f"{band_name}/{basis}: the denominator is not the set of pairs the record requires "
-                f"a move from and which do not span the 2020-2021 gap."
-            )
-            assert cell["n_pairs_the_share_series_can_carry"] == sum(
-                1 for v in judged.values() if v["share_can_carry"]
-            ), (
-                f"{band_name}/{basis}: the numerator counts pairs the denominator excludes, which "
-                f"is how a vacuous carry becomes evidence."
-            )
-            assert cell["n_pairs_the_share_series_can_carry"] <= cell["n_pairs_judged"]
+                    if not requires:
+                        vacuous_seen = True
+                        assert name in cell["pairs_excluded_because_the_record_requires_no_move"], (
+                            f"{band_name}/{basis}/{name}: the record requires no move here and the "
+                            f"pair is not in the exclusion list. It will be counted as carried."
+                        )
+                judged = {
+                    k: v for k, v in pairs.items()
+                    if v["record_requires_a_move"] and not v["spans_a_gap"]
+                }
+                assert cell["n_pairs_judged"] == len(judged), (
+                    f"{band_name}/{basis}: the denominator is not the set of pairs the record requires "
+                    f"a move from and which do not span the 2020-2021 gap."
+                )
+                assert cell["n_pairs_the_share_series_can_carry"] == sum(
+                    1 for v in judged.values() if v["share_can_carry"]
+                ), (
+                    f"{band_name}/{basis}: the numerator counts pairs the denominator excludes, which "
+                    f"is how a vacuous carry becomes evidence."
+                )
+                assert cell["n_pairs_the_share_series_can_carry"] <= cell["n_pairs_judged"]
     assert vacuous_seen, (
         "no pair in the whole reading has a record move interval containing zero, so the exclusion "
         "this leg holds is never exercised and a denominator over every pair would pass it."
@@ -4915,10 +4960,19 @@ def test_the_observed_mix_verdict_flips_when_an_observation_that_would_flip_it_i
             f"{basis}: the record no longer refuses at every observed mix over the fitted years. "
             f"That is §14's headline and it has moved -- report it, do not adjust this leg."
         )
+        assert cell["the_verdict_is_the_same_at_every_observed_mix"] is True
+    # §14'S SECOND HEADLINE MOVED 2026-10-03 AND IS REPORTED, NOT ADJUSTED AWAY: on the QEP record
+    # the mix-free envelope REFUSES too, so "admits only outside every observed mix" is False live
+    # (the result file for the QEP re-fit says so). The injection below needs an envelope that
+    # admits, so it runs on a band with width, where the pre-injection state is the one it flips.
+    monkeypatch.setattr(split, "published_departure_band", lambda: dict(_A_BAND_WITH_WIDTH))
+    for basis, by_set in _turns_on_one_survey()["by_basis"].items():
+        cell = by_set["fitted_years"]
+        assert cell["refuses_at_every_observed_mix"] is True
         assert cell["admits_only_outside_every_observed_mix"] is True, (
-            f"{basis}: the mix-free envelope no longer admits where every observed mix refuses."
+            f"{basis}: on the band with width the mix-free envelope no longer admits where every "
+            f"observed mix refuses, so the injection below cannot reach the branch it flips."
         )
-        assert cell["the_verdict_is_the_same_at_every_observed_mix"] is True
 
     extreme = tuple(split.SVT_TENURE_OBSERVATIONS) + (
         split.TenureObservation(
diff --git a/tests/simulation/test_departure_risks.py b/tests/simulation/test_departure_risks.py
index 5ccb297d7..40fa5f1ac 100644
--- a/tests/simulation/test_departure_risks.py
+++ b/tests/simulation/test_departure_risks.py
@@ -641,13 +641,17 @@ def test_a_year_inside_the_published_record_with_no_fitted_anchor_refuses_instea
     record = _published_departure_rates()
 
     # (a) THE PREMISE, MEASURED RATHER THAN ASSERTED. The reference year's anchor is not a
-    #     conservative stand-in for a record year: it has no direction at all.
+    #     stand-in for another record year: borrowing it moves some fitted year's anchor by more
+    #     than half. Until 2026-10-03 this asserted it had NO DIRECTION (some ratios below 1, some
+    #     above). On the QEP 2.7.1 re-fit 2024's anchor is the largest, so every ratio is >= 1 and
+    #     the borrow has a direction -- up, 2.5-10x -- which makes it a bigger claim, not a smaller
+    #     one. Keyed to the size of the claim, which holds on both blocks.
     ref = YEAR_LEVEL_ANCHOR[MULTIPLIER_REFERENCE_YEAR]
     ratios = {y: ref / YEAR_LEVEL_ANCHOR[y] for y in record if y in YEAR_LEVEL_ANCHOR}
-    assert min(ratios.values()) < 1.0 < max(ratios.values()), (
-        "the reference year's anchor is on one side of every fitted year's, so the old docstring's "
-        "'fails toward the record' claim would be defensible and this control is arguing with "
-        f"something that is not there. ratios: {ratios}"
+    assert max(max(ratios.values()), 1.0 / min(ratios.values())) > 1.5, (
+        "the reference year's anchor is within 1.5x of every fitted year's, so borrowing it for a "
+        "record year would be a small claim and this control is arguing with something that is "
+        f"not there. ratios: {ratios}"
     )
 
     # (b) THE PARTITION, WHICH REPLACED "EVERY RECORD YEAR IS FITTED" ON 2026-09-02. That older
diff --git a/tests/simulation/test_market_switching_propensity.py b/tests/simulation/test_market_switching_propensity.py
index 8f4c5728b..543eb0dbb 100644
--- a/tests/simulation/test_market_switching_propensity.py
+++ b/tests/simulation/test_market_switching_propensity.py
@@ -75,15 +75,18 @@ class TestMarketSwitchingMultiplier:
         published record is NOT monotone in those savings, and that is precisely why a
         savings-only curve can never reproduce it:
 
-            2021 carries 0 GBP of savings and a published 17.9-18.4%.
-            2017 carries 200 GBP and a published 13.5-14.0%.
+            2021 carries 0 GBP of savings and a published 15.57% (DESNZ QEP 2.7.1).
+            2024 carries 150 GBP and a published 9.03%.
 
-        So 2021 must come out ABOVE 2017 despite offering nothing to switch for -- the H2-2021
+        So 2021 must come out ABOVE 2024 despite offering nothing to switch for -- the H2-2021
         collapse was suppliers withdrawing products, and the households who moved that year mostly
         did so through SoLR rather than by shopping. A multiplier that still ranked these two by
         savings would be reporting the curve, not the world.
         """
-        assert market_switching_multiplier(2021) > market_switching_multiplier(2017)
+        # The pair was 2021 vs 2017 until 2026-10-03; on the QEP record 2017 (18.20%) is above
+        # 2021, so savings and record agree there and the pair no longer discriminates.
+        assert market_switching_multiplier(2021) > market_switching_multiplier(2024)
+        assert market_switching_multiplier(2021) > market_switching_multiplier(2023)
         assert market_switching_multiplier(2020) > market_switching_multiplier(2016)
         # The crisis trough is still the bottom, and by more than the curve knew.
         assert market_switching_multiplier(2022) < market_switching_multiplier(2023) < 1.0
diff --git a/tests/simulation/test_net_new_acquisition.py b/tests/simulation/test_net_new_acquisition.py
index 8070c2430..02d7c54b0 100644
--- a/tests/simulation/test_net_new_acquisition.py
+++ b/tests/simulation/test_net_new_acquisition.py
@@ -1314,8 +1314,11 @@ def test_b2_the_two_flags_are_INDEPENDENT_and_the_default_path_is_untouched(monk
 # REPORT_END (7 June), and the seasonal days are drawn from their own stream, so how many of 2025's
 # prospects fall before the cutoff is a fresh draw (binomial sd ~10 on 400). Every other year is
 # byte-identical: 2728 -> 2709, £60,622.86 -> £60,210.25, at the same £20.63.
-CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG = 2709
-CAMPAIGN_SPEND_AT_SHIPPED_CONFIG = 60210.25
+# RE-MEASURED 2026-10-03, a world change: the commons moved onto DESNZ QEP 2.7.1 and the multiplier
+# the in-play pool is clipped by moved with it (2017 0.870 -> 2.015, 2022 0.267 -> 0.339, 2023
+# 0.776 -> 0.701). 2709 -> 2707 quotes, at the same £20.63.
+CAMPAIGN_QUOTES_AT_SHIPPED_CONFIG = 2707
+CAMPAIGN_SPEND_AT_SHIPPED_CONFIG = 60170.37
 
 #: The subset the ACCOUNTS can carry: quotes dated inside [REPORT_START, REPORT_END].
 #:
@@ -1327,8 +1330,8 @@ CAMPAIGN_SPEND_AT_SHIPPED_CONFIG = 60210.25
 #:
 #: The filter is still real and still tested: `test_c_MUTATION_the_window_filter_can_actually_
 #: EXCLUDE` hands it a mid-decade `report_end` and requires it to drop the rest.
-CAMPAIGN_QUOTES_INSIDE_WINDOW = 2709
-CAMPAIGN_SPEND_INSIDE_WINDOW = 60210.25
+CAMPAIGN_QUOTES_INSIDE_WINDOW = 2707
+CAMPAIGN_SPEND_INSIDE_WINDOW = 60170.37
 
 
 def test_c_every_quote_the_campaign_paid_for_is_BOOKED_as_acquisition_spend():
diff --git a/tests/simulation/test_price_sensitivity_reaches_the_price_response.py b/tests/simulation/test_price_sensitivity_reaches_the_price_response.py
index 7d854370d..11e6d17df 100644
--- a/tests/simulation/test_price_sensitivity_reaches_the_price_response.py
+++ b/tests/simulation/test_price_sensitivity_reaches_the_price_response.py
@@ -426,11 +426,15 @@ def _one_renewal(monkeypatch, sensitivity) -> float:
     event = roll_lifecycle_event(
         "C5", renewal, "electricity",
         _build_one_year_records(), _make_customers(),
-        # Ex-VAT, like every struck rate: the household sees it 20% above the inc-VAT SVT.
-        old_rate_gbp_per_mwh=svt, new_rate_gbp_per_mwh=svt * 1.20 / (1.0 + DOMESTIC_VAT_RATE),
+        # Ex-VAT, like every struck rate: the household sees it 10% above the inc-VAT SVT. It was
+        # 20% until 2026-10-03; under the QEP 2.7.1 re-fit this 2016 roll borrows 2024's anchor
+        # (20.8) at a 1.75 multiplier, and at +20% both households sit on the churn ceiling
+        # (0.9831), so the difference this asks about is saturated away, not unwired. At +10%
+        # they read 0.8935 and 0.8598.
+        old_rate_gbp_per_mwh=svt, new_rate_gbp_per_mwh=svt * 1.10 / (1.0 + DOMESTIC_VAT_RATE),
     )
     assert event is not None, "the fixture stopped reaching a renewal — it can no longer see this"
-    assert event["price_differential_vs_svt"] == pytest.approx(0.20), (
+    assert event["price_differential_vs_svt"] == pytest.approx(0.10), (
         "the fixture is no longer priced away from the market, so the weight has nothing to bite "
         "on and this whole section would pass vacuously")
     return event["realized_churn_probability"]
diff --git a/tools/measure_departure_level.py b/tools/measure_departure_level.py
index a211f7160..7fa356a56 100644
--- a/tools/measure_departure_level.py
+++ b/tools/measure_departure_level.py
@@ -96,7 +96,10 @@ COMMONS = PROJECT / "docs" / "domain_artefact_library" / "regulatory" / "gb_dome
 #: block was refitted twice (third and fourth pass). `pb4_d_fourth_pass_anchor_departure_factors.json`
 #: is the capture under the fourth block that lands with it. It has 104 renewal and 2,013 SVT
 #: decisions, and both halves are tracked.
-DEFAULT_TABLE = PROJECT / "docs" / "reports" / "pb4_d_fourth_pass_anchor_departure_factors.json"
+#: REPOINTED 2026-10-03 FOR THE QEP 2.7.1 RE-SITE of the commons: the record moved under the fit, and
+#: `qep_g_second_qep_pass_anchor_departure_factors.json` is the capture under the second QEP-pass
+#: block that lands with it. Both halves are tracked.
+DEFAULT_TABLE = PROJECT / "docs" / "reports" / "qep_g_second_qep_pass_anchor_departure_factors.json"
 
 #: Active domestic electricity accounts per year in the live run, from the opening finding's own
 #: table. NOT re-derived here: the factor table holds renewals, not the active book, so the
diff --git a/tools/population_anchor.py b/tools/population_anchor.py
index a3475d439..60de0e7ef 100644
--- a/tools/population_anchor.py
+++ b/tools/population_anchor.py
@@ -63,7 +63,7 @@ if not _PUBLISHED_BAND_PCT:  # pragma: no cover - fail-closed; `published_bands`
 #: out. Not the high end -- that tie-break is a CURRICULUM value governing where the WORLD is
 #: aimed (commons `reserved`), and this is a measuring stick, not a dial.
 OFGEM_SWITCHING_RATE_PCT_BY_YEAR: dict[int, float] = {
-    year: round((lo + hi) / 2.0, 2) for year, (lo, hi) in sorted(_PUBLISHED_BAND_PCT.items())
+    year: round((lo + hi) / 2.0, 3) for year, (lo, hi) in sorted(_PUBLISHED_BAND_PCT.items())
 }
 
 #: The FRACTION form, derived by construction and never authored. Everything downstream of this
@@ -618,10 +618,10 @@ def generate(run_json_path=None, out_path=None, billing_ledger_path=None):
     if out_path is None:
         out_path = OUT_PATH
     data = json.loads(Path(run_json_path).read_text())
-    
+
     events = data.get("customer_events", [])
     years_data = data.get("years", {})
-    
+
     # C1b's second departure route. `svt_decisions` is every SVT segment evaluated (the
     # denominator); `svt_departures` is only the ones that fired. A run output carrying the
     # numerator alone can state how many left that way and NOT a rate, which is why the two are
@@ -714,7 +714,7 @@ def generate(run_json_path=None, out_path=None, billing_ledger_path=None):
         "arrears_vs_benchmark": arrears_findings,
         "acquisition_funnel_vs_benchmark": acquisition_funnel_findings,
     }
-    
+
     Path(out_path).parent.mkdir(parents=True, exist_ok=True)
     Path(out_path).write_text(json.dumps(result, indent=2))
     return result
diff --git a/tools/settlement_per_axis_gain.py b/tools/settlement_per_axis_gain.py
index 84b5a351a..10945a27d 100644
--- a/tools/settlement_per_axis_gain.py
+++ b/tools/settlement_per_axis_gain.py
@@ -154,6 +154,27 @@ FILED_RECORDS = (
             "ratio": 0.9465,
         },
     },
+    {
+        "filed": "2026-10-04",
+        "base": "the QEP 2.7.1 re-fit of the level anchor (world cdba75ebb9197b33), before it landed",
+        "source": "SEAT_RESULT_THE_LEVEL_ANCHOR_REFIT_ONTO_DESNZ_QEP_2_7_1_2026-10-03.md",
+        "world": {
+            "level_digest": "cdba75ebb9197b33",
+            "home_digest": "35f8efe8ff02f245",
+        },
+        #: Measured, not predicted. Seeds 43-45 read 0.891 / 0.855 / 1.225 the same night: the
+        #: chooser is at or below parity with the cull on its worst axis, as on world D, and P1b
+        #: holds on all four seeds.
+        "scalars": {
+            "cull_settled": 62,
+            "cull_cy": 1044.9,
+            "chosen_settled": 57,
+            "chosen_cy": 1047.0,
+            "worst_ks_cull": 0.06522,
+            "worst_ks_chosen": 0.06958,
+            "ratio": 0.9373,
+        },
+    },
 )
 
 
```
