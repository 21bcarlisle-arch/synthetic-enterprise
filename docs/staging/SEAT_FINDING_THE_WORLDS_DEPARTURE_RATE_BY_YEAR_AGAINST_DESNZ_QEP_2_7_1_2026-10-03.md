# The world's departure rate by calendar year against DESNZ QEP 2.7.1

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-worlds-departure-rate-against-the-published-year` (Lane 0 delivery)

Decides whether the console seat's churn-belief calibration is fitting the world's truth or a fidelity
defect in the world's level.

## 1. Pre-registration (written 2026-10-03 ~20:30Z, BEFORE the per-year split was computed)

**What the thing is.** QEP 2.7.1: domestic ELECTRICITY changes of supplier in the calendar year, over
domestic electricity accounts held. The world's comparator: electricity accounts in the company's
book that left to another supplier in the year (renewal-route `churned` + SVT-route `churned`), over
the electricity account-years the book held in that year. Gas ids (`…g`) excluded on both sides.
Not "departures per renewal decision" — that denominator is the selected sub-population and has no
published comparator (knowledge map, *Switching rates* row).

**Source.** `docs/reports/run_output_543dcff6d_20261003T185017Z.json` (= `run_output_latest.json`,
written 20:09Z today by `tools.run_annual_report`, full window 2016-01-01 → 2025-06-07, not fast).

**What I had already seen when writing this, declared so the prediction is not read as blind:**
the run-wide totals — 62 electricity departures (26 renewal-route, 36 SVT-route), ~90 active ids a
year including gas twins, so roughly 45-50 electricity accounts. That puts the run-wide mean near
the record's run-wide mean (~13-14%). I had NOT seen any per-year count.

**Mechanism the prediction stands on.** The world carries a per-year level anchor
(`simulation/departure_level_anchor.py`; fitted 2017-21, 2023, 2024; 2016/2025 declared at 17.13,
2022 at 1.0) that was bisected onto the commons artefact's OLD bands, which DESNZ refuted on
2026-09-07 and which were never corrected (the commons is marked `superseded`, values unchanged).
Old-band midpoints vs record: 2016 17.3/15.82, 2017 13.75/18.20, 2018 19.75/19.06, 2019 21.0/20.82,
2020 22.75/20.21, 2021 18.15/15.57, 2022 3.6/3.06, 2023 10.7/6.33, 2024 14.3/9.03, 2025 16.1/10.40.

**Predictions:**

- **P1 (direction by year, on the point estimate).** World ABOVE record in 2016, 2020, 2021, 2023,
  2024, 2025; BELOW in 2017; within ±2pp in 2018, 2019, 2022.
- **P2 (resolution).** With ~45-50 electricity accounts a year the 95% bound is ±8-12pp wide, so
  the record sits INSIDE the world's bound in at least 8 of 10 years. This run cannot by itself
  convict the level in any single year; the only years with a chance are 2023-2025 (old midpoint
  ~1.5-1.7× record).
- **P3 (sign vs the console seat's belief error, believed − true P(stay)).** Positive error = belief
  under-predicts leaving. If the world's excess over the record drives it, world-above-record should
  pair with positive error. Predicted: matches in 2017 (−, world below), 2020, 2021, 2024, 2025 (+,
  world above); MISMATCH in 2018 (−0.33 while the world is about at the record) and 2019 (+0.24, world
  about at the record). 5 of 7.
- **P4 (magnitude — the one that decides the question).** Even where signs match, a whole-book excess
  of a few points cannot produce a per-decision P(stay) error of 0.24-0.64. So the calibration is
  MOSTLY fitting something other than the level defect; the 2024/25 years are the exception where a
  level defect of ~1.5× contributes materially.

## 2. Measurement — two instruments, because one run cannot convict a level

### 2a. The realised rate in the 20:09Z run (one seed, the company's own book)

Resi electricity accounts only (109 ids; 2 SME and 66 gas excluded — C5 and C6 depart but are SME).
Denominator = mean electricity accounts held in the year (account-days / days in year); numerator =
`churned` on either route in the year. No account ended any other way (0 non-switch ends). 2025 is
2025-01-01 → 2025-06-07, annualised. Bound = exact Clopper-Pearson 95% on k of round(mean held).
Script: `/tmp/deprate/measure.py` (not committed — the reading is the result; the comparable
committed instrument is 2b).

| year | departures (renewal / SVT) | mean held | world % | 95% bound | QEP 2.7.1 % | record in bound? |
|---|---|---|---|---|---|---|
| 2016 | 0 (0/0) | 35.9 | 0.0 | 0.0–9.7 | 15.82 | **OUT, low** |
| 2017 | 7 (3/4) | 62.8 | 11.1 | 4.6–21.6 | 18.20 | in |
| 2018 | 10 (2/8) | 57.1 | 17.5 | 8.7–29.9 | 19.06 | in |
| 2019 | 13 (4/9) | 51.6 | 25.2 | 14.0–38.9 | 20.82 | in |
| 2020 | 13 (6/7) | 42.6 | 30.4 | 17.1–46.0 | 20.21 | in |
| 2021 | 10 (6/4) | 39.1 | 25.6 | 13.0–42.1 | 15.57 | in |
| 2022 | 0 | 38.6 | 0.0 | 0.0–9.0 | 3.06 | in |
| 2023 | 3 (0/3) | 38.3 | 7.8 | 1.7–21.4 | 6.33 | in |
| 2024 | 2 (1/1) | 42.9 | 4.6 | 0.6–15.8 | 9.03 | in |
| 2025 (part) | 2 (2/0) | 47.5 | 9.8 | 1.2–33.1 | 10.40 | in |

Run-wide: 60 departures over 429.8 account-years = 13.96%. **2016 is out for a composition reason,
not a level one:** every account was acquired onto a first fixed term during 2016 and this world has
no departure route for a household mid-fixed-term, so a new book cannot lose anyone in its first
year. QEP's denominator includes mid-term accounts. Whether real first-year mid-term switching is
material is NOT established here — filed as a gap, no number picked.

### 2b. The EXPECTED whole-book level (`python3 -m tools.measure_departure_level`, capture `pb4_d_fourth_pass_anchor_departure_factors.json`, live anchors)

This is the level the anchor sets — a mean of probabilities, no outcome-sampling noise, and the
quantity the anchor was bisected onto. Read against QEP 2.7.1 (the instrument prints only the
refuted bands for this column; the ratio is mine):

| year | world expected % | QEP 2.7.1 % | world − record | ratio |
|---|---|---|---|---|
| 2017 | 14.00 | 18.20 | −4.2 | 0.77 |
| 2018 | 20.00 | 19.06 | +0.9 | 1.05 |
| 2019 | 21.30 | 20.82 | +0.5 | 1.02 |
| 2020 | 23.00 | 20.21 | +2.8 | 1.14 |
| 2021 | 18.40 | 15.57 | +2.8 | 1.18 |
| 2022 | 2.59 | 3.06 | −0.5 | 0.85 |
| 2023 | 8.73 | 6.33 | +2.4 | 1.38 |
| 2024 | 16.28 | 9.03 | **+7.3** | **1.80** |

2016 and 2025 are outside the capture's full years. 2025's anchor is the declared 17.128306 — the
same value as 2024's fit — so 2025 runs at 2024's level against a record of 10.40, and is the second
year most likely to be ~1.6× high. Each expected figure sits on the edge of the REFUTED band it was
fitted to, which is exactly the mechanism §1 named.

## 3. Grading

- **P1 — on the realised run: 5 of 10, i.e. noise.** Wrong on 2016 (composition, §2a), 2019, 2022,
  2024, 2025. **On the expected level (2b), which is what P1's mechanism was about: 8 of 8** —
  above in 2020, 2021, 2023, 2024; below in 2017; within 2pp in 2018, 2019, 2022. P1 was a
  prediction about the anchor and should have said which instrument it graded; it is graded here on
  both and the realised one fails.
- **P2 — HELD.** Record inside the run's bound in 9 of 10 (predicted ≥8). The run cannot convict any
  year's level; the one OUT is 2016 and it is composition.
- **P3 — 5 of 7 on both instruments, but not the five I named.** Realised: matches 2017-2021,
  mismatches 2024/25 (world below the record by point estimate, belief +). Expected: matches 2017,
  2019, 2020, 2021, 2024; mismatch 2018 (+0.9pp against −0.33). I predicted 2018/2019 mismatching and
  2024/25 matching; on the expected level 2024 matches and 2019 weakly matches.
- **P4 — HELD, with one exception sized.** First-order, scaling the world's per-renewal departure
  (`world E[depart]` renewal column) by record/world gives what P(stay) would be in a
  record-faithful world: 2020 58.7%→51.5%, a +0.07 shift against a +0.64 error; 2021 +0.09 of +0.29;
  2017 −0.07 of −0.21; 2018 +0.01 against −0.33 (wrong sign). **2024: 45.6%→25.3%, +0.20 of +0.44 —
  about HALF of the 2024 error (and by the shared anchor, 2025's) is the level defect.** This is a
  linear proportional scaling of a saturating hazard and is a size, not a measurement.

## 4. Verdict

**The console seat's level calibration is fitting truth in 2017-2021 and a fidelity defect in
2024-2025.** In 2017-2021 the world's expected whole-book level is within 0.77-1.18× of QEP 2.7.1 and
explains 0-30% of each year's belief error. In 2024 the world departs 1.80× the published rate, 2025
inherits the same anchor, and roughly half of the +0.44/+0.51 belief error there is the world being
too leaky. A belief fitted to the world's P(stay) over 2024-25 would learn that leak, and the book
would show the retention it buys as a gain. 2023 (1.38×) is in between and stands on few decisions.

## 5. Next item — the coupled correction, priced

Re-fit `simulation/departure_level_anchor.YEAR_LEVEL_ANCHOR` onto QEP 2.7.1 instead of the refuted
bands. It cannot land in pieces (`fit_year_level_anchor --internal-return` refuses against the
corrected record while the capture embeds the old one):

1. commons `gb_domestic_switching_rate.json` `rates` → QEP 2.7.1 (record correction, ~1h seat);
2. re-capture the world under the re-fit (departure-factor capture, ~1.5-2h compute) and repoint
   `measure_departure_level.DEFAULT_TABLE`;
3. the six verdict blocks that read the band;
4. **~25 value-arm controls** in `tests/tools/test_generate_value_arms_data.py` red on the new
   `world_level_identity` digest and need the arms re-taken under `tools.run_value_cycle_ab`: ≈53 min
   per seed per level-arm pass, 3 seeds ≈ 8h, split into legs under 5h each.

Total ≈ 11-12h compute and 2-3 seat turns. Also owed, separately and cheaper: a 2016 composition
note (no mid-fixed-term exit route) — a gap, not a fix. Handed on as
`refit-the-level-anchor-onto-desnz-qep-2-7-1`.

## 6. Duplicate-work disposition

The draw's duplicate-work note named a live claim under this same id. `ps` at draw time showed no
rival seat or `surgical_land` on this subject; the claim was the draw's own write. Carried on.
