**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the end-year clamp arm, measured before any build: 2016 can take its own fleet, 2025 cannot, and the arm's control cannot fail (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 step 2 of the weather-to-price steer (BLOCKING finding,
G_data_learning). The step was set by the build-terms result
(`docs/staging/records/WORKER_RESULT_ON_THE_CHAINS_OWN_FORM_THE_DEMAND_YEAR_TERM_EXPOSES_A_PRICE_LEG_THAT_RUNS_7_POUNDS_LOW_AFTER_THE_CRISIS_2026-11-24.md`,
§Next 2): "2016 and 2025 are record years and should take their own matched fleet. The clamp is a
forward-year rule … B-P4 is its control." This record checks that sentence before anything is built.
Probe `/var/tmp/wpc_agws/probe.py` (sha256 `bf4ceede…`), run at `ea3a93cc45`, output
`/var/tmp/wpc_agws/out.json` (sha256 `ee386d46…`). One live probe of Elexon's API, described below.
**Nothing in `sim/` changes.***

## 1. The step's control cannot fail

`fleet_trajectory()` sets each year's wind fleet to that year's AGWS wind mean divided by that year's
mean curve fraction. A year that takes its own fleet therefore reproduces its own AGWS wind mean
exactly. B-P4 asks whether the chain's yearly mean matches the record's. If 2016 and 2025 take their
own fleets, B-P4's wind leg matches in both years because of how the fleet is built, so it cannot
fail. It would pass even if the 2025 fleet were wrong, and it is.

The control has to be something the fit does not touch. DUKES installed capacity
(`real_capacity_wind`) is independent: it does not come from AGWS and is not fitted.

## 2. What the fleet looks like against DUKES

| Year | Days | Months | Own fleet (MW) | Own fleet ÷ DUKES capacity | Reaches a magnitude today? |
|---|---|---|---|---|---|
| 2016 | 306 | 10 (Mar-Dec) | 6,700 | **0.415** | no → takes 2017's 8,162 (0.506 of 2016's DUKES) |
| 2017-2022 | 343-363 | 12 | 8,162-12,894 | 0.417-0.472 | yes |
| 2023 | 365 | 12 | 11,378 | 0.376 | yes |
| 2024 | 366 | 12 | 12,043 | 0.372 | yes |
| 2025 | 158 | 6 (Jan-Jun 7) | 23,712 | **0.717** | no → takes 2024's 12,043 |

- **2016 can take its own fleet.** Its 0.415 sits inside the 2017-22 range. The clamped value is
  outside it: 0.506 is about 20% above the range's middle. Ten months is enough data. In every full
  year 2017-23, a fleet fitted on March to December alone comes within 0.956-0.991 of the full-year
  fleet. 2024 reads 0.879, and §3 shows why.
- **2025 cannot take its own fleet.** A fleet of 0.717 × DUKES capacity is not a fleet. Before this
  run I took it for the six-month artefact that `_MONTHS_REQUIRED_FOR_MAGNITUDE` was written for. **That
  was wrong.** A January-June fleet runs 0.776-1.092 of the full year in every full year, so half a
  year cannot make 2×. Two inputs make it:
  - **The weather.** 2025's January-June town wind speed is 3.23 m/s, against 3.91-4.71 in
    2017-24. No break shows at the new year, and November 2024 is low as well, so this reads as a
    real calm spell rather than a source change. Through its power curve, the chain turns that
    calm into much less wind than the record shows.
  - **The 2024 fleet 2025 falls back on.** AGWS loses about half its wind for six months of 2024
    (§3), so that fleet is depressed too.
- **2023 and 2024 sit below the band** (0.376, 0.372), the only full years that do. §3 is why.

## 3. AGWS wind loses about half the metered wind in three windows

Elexon's AGWS wind (onshore plus offshore, latest publish per half-hour) compared with FUELHH `WIND`
(BM-metered, an independent dataset):

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| FUELHH ÷ AGWS | 0.725 | 0.871 | 0.942 | 1.035 | 1.020 | 0.976 | 1.077 | **1.227** | **1.223** | 0.812 |

Month by month the ratio holds at 0.8-1.2 from 2017-06 to 2023-01. It then jumps to 1.6-2.4 in three
blocks. Edges come from a seven-day rolling ratio crossing 1.45, so each is approximate to a few days:

- **April 2017** (4 Apr - 7 May; 1.83 for the month);
- **February to July 2023** (late January to early August; 1.64-2.30);
- **May to October 2024** (mid-April to mid-November; 2.10-2.42).

Inside the windows, offshore wind is what goes missing. In May 2024 AGWS offshore averages 504 MW. On
2024-05-30, FUELHH reads 9,642 MW while AGWS onshore plus offshore reads 3,990 MW.

**This is Elexon's published series, not our cache.** A live probe of
`data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type/wind-and-solar` for 2024-05-15 SP20 returns
offshore 196.561 MW. That is byte-identical to the cache, with the same publish time,
2024-05-15T10:58:08Z. On that calm half-hour the two series agree (FUELHH 1,321 MW, AGWS 1,455 MW). The
loss shows on windy periods, so it is not a fixed scale factor. *Why* AGWS loses offshore wind in
these windows is not established. It is filed as a finding (below) and was not guessed at here.

## 4. What this changes downstream

- **Item 4 step 2 should not be built as written.** For 2016 the change is sound: let a record year
  whose missing months do not bias its fleet take that fleet. For 2025 it would write a 0.717 fleet into
  the world and report success through a control that cannot fail.
- **The wind-target arm's "outside 2025" is now explained in part.** That arm mean-matched to
  FUELHH and closed the post-crisis gas-running miss everywhere except 2025. Every AGWS-fitted fleet
  for 2023-24 is depressed by §3's windows. FUELHH is the target with no holes in it, which supports
  that arm's build direction, and 2025's weather is the separate half.
- **Every grade today that put "the record's wind" in AGWS terms** carries the windows inside its
  2023 and 2024 rows. That covers the coupling, fleet-curve, gas-running and build-terms arms, and
  the electricity page's identity table: −0.89 GW crisis, −0.36 GW post, and a 2.7 GW SD. **The
  electricity page's GAP 9** ("why AGWS and FUELHH part") is now partly answered. Most of the part
  after the crisis is these two windows, not a steady offset. This is a prediction for the page
  owner to check. It is not a re-grade, and no earlier figure is restated here.
- **Other readers of AGWS** include `tools/generate_grid_intensity_feed.py` and the `ep13_*` bounds.
  Whether they are affected is not measured here and is carried by the finding.

## 5. What would refute this

- The B-P4 claim is refuted if a year can take its own fleet and still miss its own AGWS mean. The
  `wind_gen_mean_mw` stamp in `fleet_trajectory()` shows that it cannot.
- The window claim would be refuted if FUELHH `WIND` were the series with the gaps, rather than AGWS.
  **Checked, and it is not.** Each record mean was set against DUKES annual onshore plus offshore wind
  generation (`real_generation_gwh`). The record means are over the chain's aligned days, so the
  comparison is approximate where a few days are missing.

  | Year | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|---|---|---|
  | AGWS ÷ DUKES | 0.752 | 0.730 | 0.705 | 0.709 | 0.764 | 0.715 | **0.624** | **0.643** |
  | FUELHH ÷ DUKES | 0.655 | 0.688 | 0.729 | 0.723 | 0.746 | 0.770 | 0.766 | 0.786 |

  AGWS drops out of its own 2017-22 range in exactly the two window years. FUELHH carries on its
  slow rise, as embedded wind's share of DUKES shifts toward metered offshore.

Reverse: delete this record.
