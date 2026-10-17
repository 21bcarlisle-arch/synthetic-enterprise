**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity` (row untouched) · **Subjects:** `EP17_varied_population_draw` · **Claim:** `the-worlds-switching-gradient-by-payment-and-tariff` (Lane 0 delivery)

# The world loses the payment gradient on its SVT drift route, and its tariff gradient is a matter of era, not of selection

**DEVELOPMENT.** One book, one seed. Measurement only: no world value changed, and none will before
the 19 Oct publish.

Predictions were filed first, at
`docs/staging/records/SEAT_PREREG_THE_WORLDS_SWITCHING_GRADIENT_BY_PAYMENT_AND_TARIFF_2026-10-17.md`
(landed `74cf99e7e`). The prereg was written to disk before any outcome was read. Its commit landed
while the first measurement was running, so the commit time comes after the file, not before it.

## The answer

| gradient | published | world, realised 2016–25 (95%) | world, drawn 2016–25 | world, drawn 2024–25 | where it is lost |
|---|---|---|---|---|---|
| prepayment vs DD | 0.55 (CIM w6) | 1.07 (0.78, 1.46) | 0.88 | 0.81 | **(b)**: the draw assigns it and the gate carries it, but ~3/4 of switches come through a route with no channel term |
| standard credit vs DD | 1.02 | 1.26 (0.92, 1.71) | 1.00 | 1.12 | **not lost** |
| fixed vs default | 2.8 (CIM w6, 2025) | 0.94 (0.74, 1.19) | 0.93 | **2.61** | **mostly none of (a), (b) or (c). It is the era.** The world gives about 2.6 in the years the survey was fielded and about 0.6 in 2016–20. (c) adds a little. |

"Drawn" means the sum of each decision's own departure probability (`realized_churn_probability`) over
account-years. It is the world's expectation without the noise of the roll. "Realised" counts the
switches that happened. A switch is any departure that is not a home move.

## Where the payment gradient goes (prepayment)

The code path and the numbers agree:

1. **(a) is refuted. The draw assigns the gradient.** Mean drawn active-renewal probability is
   PPM 0.196 against DD 0.380, a ratio of **0.52**. That is the CIM factor (0.59) times the
   archetype mix of this book. The 115 PPM accounts are 39% active against 48% for DD.
2. **The gate fires.** The realised active share at a fixed term end is PPM 19/107 = 0.178 against
   DD 197/654 = 0.301, a ratio of **0.59**.
3. **On the fixed-term-end route, the published gradient comes through almost exactly.** Drawn
   switches per account-year are PPM 0.0197 against DD 0.0393, a ratio of **0.50**, against the
   published 0.55. Given that it is looking, P(switch | active renewal) does not depend on channel:
   DD 0.155, PPM 0.149.
4. **(b): the SVT drift route carries none of it, and it carries most of the switching.** Drawn
   switches per SVT account-year are PPM 0.1335 against DD 0.1361, a ratio of **0.98**. That route
   is 71% of DD's drawn switches and 83% of PPM's. `inertia_hazard_for_term` reads the archetype,
   years on SVT and action propensity. It does not read the channel. Action propensity is flat by
   channel: 0.967, 0.971 and 0.981.
5. **A second leak on the same route.** At an SVT anniversary, an active household **converts onto
   our fix and never rolls departure** (`departure_rolled_at_renewal`, mirrored in
   `coin_drawn_decision_set.py`). This happens 328 times on this book. So where E is highest on the
   default tariff, it buys retention, not switching away. A low-E PPM household stays on the drift
   hazard longer: mean years on SVT 2.06 against DD 1.85.

Net: the gate moves a PPM household from one exit to another of similar size. The whole-book ratio
lands at 0.88 drawn and 1.07 realised. The published 0.55 lies **outside** the realised 95%
interval (lower end 0.78).

**Standard credit is not lost.** It is 1.00 drawn against the published 1.02. Its parts offset: the
renewal route reads 1.31, because P(switch | active) is 0.22 against DD's 0.155, plausibly the
standard-credit bill-shock population, where the bill itself is the shock. The SVT route reads
0.87, because the book's SC accounts are 24% disengaged against DD's 18%.

## Where the tariff gradient goes

1. **The draw selects, a little. This is (c), and it is small.** Exposure-weighted drawn
   active-renewal probability is 0.42 on renewal-chosen fixes, 0.35 on first-term fixes and 0.34 on
   default. Realised switch rates:
   - renewal-chosen fixed against default: 1.02 (0.76, 1.38);
   - first-term fixed against default: 0.86 (0.62, 1.18).

   Selecting the population the survey describes lifts the ratio by about 0.16. It does not reach
   2.8.
2. **The era is most of it.** Drawn fixed against default, by period:

   | period | fixed /yr | default /yr | ratio |
   |---|---|---|---|
   | 2016–20 | 0.120 (643 yrs) | 0.205 (933 yrs) | **0.59** |
   | 2021–23 | 0.117 (107 yrs) | 0.067 (667 yrs) | 1.74 |
   | 2024–25 | 0.183 (82 yrs) | 0.070 (316 yrs) | **2.61** |

   CIM w6 was fielded in 2025, and in those years the world gives 2.6 against the published 2.8.
   Slice 10 fitted its ratios over windows that start in 2016, where the world's default drift runs
   at about 20% per SVT-year: the top of the inferred 15–20% band, taken under the §7 tie-break
   (`departure_risks.SVT_INERTIA_ANNUAL_RECENT`). That is above the world's fixed-term rate. So
   slice 10's "fixed below one on both causes" is a pooled-decade ratio set against a one-wave 2025
   ratio. Neither is wrong, and they are not the same quantity.

   **CORRECTED 2026-10-17, same day, beside the claim:** the world's drawn ratio and the survey's
   are not the same quantity **in any era**, so 2.61 against 2.8 is not agreement. CIM records
   tariff at interview (A13, now verified), and its ratio is an identity in where switchers land,
   `L(1−F)/((1−L)F)`. The pre-switch gradient does not enter it. The CMA's 2015 survey (supplier
   records, also post-switch) gives 1.9–4.3 pre-crisis by the same identity. On that instrument the
   world's pre-crisis rates read about 1.0–1.95, and its 2024–25 rates read well above 2.8. See
   `docs/market_research/switching_gradient_by_tariff_and_payment_what_the_record_can_grade.md` §1.
   **MEASURED 2026-10-17:** the "about 1.0–1.95" above was arithmetic and is wrong. Emulated, the
   pre-crisis world reads 1.98–3.70, inside the CMA's band, and the instrument cannot see the
   pre-switch gradient: `SEAT_FINDING_READ_THROUGH_THE_SURVEY_INSTRUMENT_THE_PRE_CRISIS_WORLD_SITS_INSIDE_THE_CMA_BAND_AND_THE_INSTRUMENT_CANNOT_SEE_THE_GRADIENT_2026-10-17.md`.
3. **Whether the world's pre-crisis default rate is too high is a GAP, not a finding.** The source
   behind the inertia band says *"Direct published SVT vs fixed churn rates by tariff type are not
   available"* (`svt_rates_active_passive_2016_2025.md` §4, confidence M). CIM w6 is the first split
   on file, and it is for 2025 only. A world that runs 0.6 pre-crisis and 2.6 in 2025 is consistent
   with everything on file. So is a world that runs 2.8 throughout.
4. **A reading of the survey itself, not checked this turn.** C4 asks whether the household switched
   "in the past 6 months" and cuts the answer by the household's tariff type. If that is the tariff
   at interview, a household that has just switched is likely to be on a new fix. Part of the 2.8
   would then be switchers landing on fixes, which no losing supplier sees beforehand. The workbook
   is not on disk and this pass did not re-fetch it. Labelled **unverified**.
   **VERIFIED 2026-10-17:** tariff type is A13, asked in the present tense at interview. The
   contamination is total rather than partial: see the knowledge page's §1a.

## Each prediction beside its result (wrong ones kept)

- **P1 HELD.** PPM over DD drawn active-renewal probability is 0.516, inside 0.45–0.75. SC over DD
  is 0.974, inside 0.85–1.20.
- **P2 HELD.** The realised active share at fixed ends, PPM over DD, is 0.59, below 0.85.
- **P3 HELD.** SVT-route realised per SVT-year, PPM over DD, is 1.22 (0.86, 1.72), inside 0.70–1.40
  with an interval that covers 1. Drawn, it is 0.98.
- **P4 HELD.** Whole-book realised PPM over DD is 1.07 (0.78, 1.46), above 0.75. On world truth it
  agrees with slice 10's company-side 0.98 and 1.16.
- **P5 HELD.** Renewal-chosen fixed carries 0.422 against first-term fixed's 0.350, a gap of
  +0.072, above the 0.03 bar.
- **P6 HELD on all three points. None clears its bound.**
  - First-term fixed against default: 0.86 (0.62, 1.18).
  - Renewal-chosen against first-term: 1.19 (0.80, 1.78).
  - Renewal-chosen against default: 1.02, inside 0.6–1.8.
- **P7 WRONG.**
  - Its premise fails: 328 of 770 residential accounts (43%) **open on the default tariff**. So "every
    customer starts on a fixed term" was false. Slice 10's addendum asserted it too, and that is
    corrected here.
  - First terms are 50% of fixed account-years, not the predicted 60% or more.
  - The main locus of the loss is not (c) but the era of the comparison, which the prereg's grading
    rule did not list.

## What this means for the thesis

Per-customer targeting by payment method is graded in a world where the observable carries
**half** the published gradient at the one decision the company can price (the fixed-term end) and
**none** on the route that does most of the switching. That is rigged against the published
record, and it is the 2026-10-08 worry confirmed for one observable.

The tariff observable is not rigged in the same way. In the years matching the survey, the world
carries about 2.6. A ratio fitted over a decade window that starts in 2016 is dominated by years
where nothing on file says what the real split was.

## The world changes this implies: filed for after the publish, NOT built

**W-A. The payment channel on the SVT drift hazard. Recommended; no new number.**

- Change: apply `engagement_multiplier_for_channel` to `inertia_hazard_for_term`. It is the same
  normalised CIM w6 factor the gate already uses, and it is mean-preserving over the drawn channel
  mix, so the year level anchor is untouched to first order.
- Evidence: CIM w6's 0.55 is an all-tariff population rate, including the households on a variable
  tariff that are this world's SVT stock.
- Prediction, filed now, to be graded on a fresh run of the same seed:
  - whole-book drawn PPM over DD moves from 0.88 into 0.50–0.70;
  - SC over DD stays within 0.85–1.20;
  - the book's total drawn switches move by less than 3%.
- Budget: the value-arms retake that any world-digest change costs (an anchor refit reds about 25
  value-arms controls).

**W-B. Active off the default: convert or shop. Named, with no proposal yet.**

- An active household at an SVT anniversary converts to our fix with certainty.
- The published φ (the external/internal switcher split, `gb_domestic_switcher_split_cim_2022_2025.md`)
  is the evidence that would set what share of those households shop and leave instead.
- Knowledge page first (K8), then a prereg.

**W-C. The pre-crisis fixed vs default split. A GAP to research, not a change.**

- Find a published fixed vs SVT switching split for 2016–2020: Ofgem's 2016–2019 engagement surveys,
  or CMA Appendix 9.1.
- **Done 2026-10-17. Neither has a pre-switch split, and no consumer survey can supply one.** The GAP
  stands with a proved reason. The admissible test is to emulate the instrument in the world
  (knowledge page §1c).
- Do this before touching `SVT_INERTIA_ANNUAL_RECENT`.

## Method, for the next session

- Book: `/home/rich/synthetic-enterprise/docs/reports/run_output_latest.json`, `producing_commit`
  `78f77c34e`. It is generated and not committed.
- Population: the 770 residential billing accounts.
- World channel and archetype: `payment_channel_for_customer` and `engagement_level_for_customer`,
  both keyed on the account id. The run's own `world_payment_truth` methods agree for every account
  that has them, apart from 8 with a mixed or changed method.
- Exposure: `account_state_log` rows on the decision leg (electricity if the account has it), cut at
  2026-01-01. A term's cell is first-term fixed (a fixed row that is the account's first row),
  renewal-chosen fixed (any other fixed row) or default (an SVT row).
- A renewal decision is placed on the row that ends on its `event_date`, on its own commodity.
  - Renewals off a default row (328) never carry a departure.
  - Switches are `customer_events` churns off fixed rows (96) plus `svt_decisions` churns (236).
- Intervals: Wilson–Hilferty Poisson intervals on rates, and log-ratio intervals on ratios.
