**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `G14_half_hourly_grid_carbon_intensity_aligned_to_settlement` · **Claim:** `g14-rebase-history-on-neso-historic-mix-and-relabel-generation-basis`

# G14 rebased onto NESO's Historic GB Generation Mix, and relabelled generation basis

At draw time the duplicate-work note named this same id as already held. `ps` showed no rival seat
and no `surgical_land` on G14, so the note was the draw's own write. This item is the one the
2020-04-27 step finding handed on (`SEAT_FINDING_G14_NESOS_2020_04_28_LEVEL_STEP_2026-10-05.md`).

## Pre-registration (written 2026-10-05, before any measurement in this turn)

Input: `df_fuel_ckan.csv`, NESO Open Data Portal, *Historic GB Generation Mix*, fetched 2026-10-05.

- **Q1. Clock of `DATETIME`.** Prediction: UTC half-hour START. Test: rows per GB local day on
  clock-change days come out 46 and 50 only if it is UTC; best lag-correlation against the API
  `actual` is 0 under UTC keying.
- **Q2. What the historic mix counts (reviewer condition).** Prediction: `GENERATION` = the sum of
  the fuel columns, including `WIND_EMB`, `SOLAR` (embedded estimates) and `IMPORTS`, with storage
  clamped. `CARBON_INTENSITY` reproduces as Σ MW × NESO factor / `GENERATION` within ~3 g RMS once
  imports carry one blended factor. If it needs a multiplier near 1.1 to fit, the file is NOT the
  generation basis, and the rebase stops here.
- **Q3. Historic mix vs the API.** Prediction: API/historic ≈ 1.10-1.15 before 2020-04-27 P34 and
  ≈ 1.00-1.05 after (the step finding measured 1.151 → 1.048 over 28 days).
- **Q4. Coverage 2016-2025.** Prediction: fewer than 100 missing or null half hours.

## Result: all four held. The rebase is done, and the relabel landed with it

- **Q1 held.** `DATETIME` is the UTC start. Keyed that way, 2016-03-27 and 2020-03-29 carry 46
  periods, and 2016-10-30 and 2024-10-27 carry 50. Correlation with the API in 2021 is 0.9932 at
  lag 0, against 0.9920 at +1 and 0.9840 at -1.
- **Q2 held.** `GENERATION` equals the sum of the fuel columns within 2 MW, with `WIND_EMB`, `SOLAR`
  and `IMPORTS` inside it. Implied factors by year: gas 391-403, coal 932-997 (2025, with almost no
  coal, reads 1,449 and is unidentified), biomass 89-133. That is NESO's table, 394 / 937 / 120,
  with no loss multiplier. RMS 3.7-8.1 g, with imports at one blended factor of 63-202 g. So **the
  historic mix is generation basis**, the reviewer's embedded and imports condition is answered,
  and the rebase went ahead.
- **Q3 held.** API / historic mix, summed: 1.1446 before 2020-04-27 P34 (34,043 half hours) and
  1.0198 from it (99,150). By year: 2018-05..12 1.176, 2019 1.126, 2020-01..04 1.134; then
  2020-05..12 1.045, 2021 1.022, 2022 1.010, 2023 1.021, 2024 1.009, 2025 1.018. 2018 is above the
  predicted band. 2020-05..12 sits about 2-3 points above later years, and why is not established.
- **Q4 held: zero missing rows and zero null or zero intensities in 2016-2025.** A signature
  nothing had predicted: on 20 half hours transmission WIND and HYDRO both read exactly 0 MW while
  gas and nuclear carry on. Five of them are on 2023-06-07, the FUELHH all-zero day, where the
  historic mix's 179-185 g is a mix with its wind missing. They are refused as outage signatures,
  on an exact test with no threshold. All 20 are also FUELHH holes, so they are gaps with both
  reasons. The partial drop at 2023-06-07 P22 (wind about 60% of normal) is not caught by either
  signature, as before.

**What changed, landed together** (the relabel could not go first: it would have meant writing a
two-basis label, then rewriting it):

- `sim/grid_carbon_history.py`: three sources (`neso_historic_mix`, `fuelmix_fill`, `gap`). The
  1.1287 scale, `fuelmix_estimate` and `fit_scale` are gone. The API is the cross-check
  (`api_versus_historic_mix`, `api_step`), and the file's last half hour names the edition.
- `sim/grid_carbon_future.py`: the fit's target is the historic mix, so a future continues the
  history's basis. `FROZEN` was refitted: 0.7-1.4% lower at real inputs, and `monthly_level_sd`
  went from 11.3 to 11.6. The rolling-origin rules now tie (30.8 / 30.8 / 30.2). On the API they
  were 32.0 / 32.3 / 34.6, so the API's step had been charging the long window for a level the
  fleet never had.
- Feed (`docs/market_data/grid_intensity_feed.json`) regenerated. Annual levels: 2016 273.4,
  2017 252.0, 2018 224.5, 2019 197.1, 2020 175.4, 2021 189.8, 2022 185.3, 2023 154.9, 2024 131.9.
  The named gaps now carry losses-not-included, the point-in-time edition caveat, the API's step,
  and imports at NESO's fixed factors (Expert Hour MINOR). `versus_published` is now two NESO
  series (`shape_is_neso`), not an identity.
- Explore (`site/data/explore_carbon.json`, `site/explore/index.html`): a third branch, NESO
  against NESO. On 5 household-days the two NESO series give timing effects 1.5 pp apart on
  average and 3.1 pp at the widest, with no sign flips.
- Relabelled generation basis, T&D losses not included: `PUBLISHED_BASIS` now states the API's two
  bases, plus `HISTORY_BASIS`, `ANNUAL_LEVEL_BASIS`, `FOOTPRINT_BASIS`, `ELECTRICITY_LEG_BASIS`,
  `NOT_INCLUDED` (new line), `GRID_INTENSITY_PROVENANCE`, the billing unit, the carbon register and
  the annual report. The two tests that pinned "loss-corrected" now pin its absence. The feed has
  a control that no basis string says it.
- Knowledge: the household-carbon page's same-day correction is withdrawn in place, and its NESO
  columns were recomputed (2016 PC1-weighted 312 → 286 g; the gas/electricity ratio in 2016 is
  2.7×, not 2.5×). The "within 2 g" claim is now 2.5 g, because 2022 is 2.3 g. The G14 and EP13
  pages were corrected beside their claims.

**Not done, and why.** The EP13 observability JSONs (`docs/observability/ep13_*.json`) still embed
the old `PUBLISHED_BASIS` text. They are the recorded outputs of a parked atom's instruments, and
they will carry the new text when those instruments next run. Rewriting a recorded measurement
by hand is not a correction. **Whether household figures ADD losses** is a definition decision,
raised to the director with a recommendation: a separate named line at DESNZ's T&D factor, never
folded in.

G14 stays at L2. The Expert Hour's two MAJORs are addressed in code, and L3 needs a re-take.

**Redrawn after landing (2026-10-05, afternoon).** The lane offered this claim again after
`cd30ba424` was on origin/main. I re-measured it, and there is nothing left to build. Outside the
negations, the only `loss-corrected` in `sim/`, `tools/`, `company/`, `saas/` and `tests/` is CARB-2 in
`tests/domain/battery_register.yaml`. That is a verbatim quote of the carbon advisor brief, not a
basis label. Disposition: released. The remainder is carried by the continuation
`g14-expert-hour-retake-on-the-historic-mix`.
