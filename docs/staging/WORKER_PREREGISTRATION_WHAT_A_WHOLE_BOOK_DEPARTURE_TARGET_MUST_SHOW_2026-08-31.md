**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# Pre-registration: what unioning the two departure routes onto one account denominator must show

**Filed before the measurement.** The predictions below are written without their answers and are
never edited; the result is appended in its own section underneath.

Discharges item 1 of
`docs/staging/done/WORKER_FINDING_C1B_ADDED_A_DEPARTURE_ROUTE_AND_EVERY_INSTRUMENT_MEASURING_DEPARTURES_KEPT_READING_THE_OLD_POPULATION_2026-08-31.md`
— *"a whole-book departure target that both routes are fitted against together"* — which is the
one thing that finding left owed and the reason `tools/fit_year_level_anchor.py` currently refuses
to emit a constant at all.

## What is already established, and is therefore not a prediction

Measured on the committed two-route capture (`docs/reports/ladder_churn_factors.json` and its
`_svt_segment_decisions.json` sibling), 144 renewal decisions against 1,266 SVT segment decisions:

* **Departures are terminal and are counted per account.** 82 departures across 82 distinct
  accounts; no account departs twice, and no account has a decision in any year after the year it
  departed.
* **There are zero unobserved interior account-years.** Every one of the 131 accounts appears in at
  least one of the two routes in every year between its first decision and its last.

Those two facts together are what make an ACCOUNT denominator available from the capture itself —
distinct accounts with at least one decision in the year — and an account denominator is the shape
the published band's own denominator has (external changes of supplier on a domestic electricity
MPAN, over all domestic electricity accounts). Neither route alone has it: a renewal-decision
denominator counts only households at a decision point, and an SVT-segment denominator counts cap
periods, roughly eleven per account-year. **This is the whole reason the union is a repair and not
a bigger number.**

The realised whole-book counts are also already known and are not predictions.

## The change

1. `tools/departure_population.py` gains the union: whole-book departures per year over the
   declared account denominator, with the three properties above **checked rather than assumed** —
   a capture that violates any of them cannot carry an account denominator and the reading fails
   closed.
2. `tools/measure_departure_level.py` and `tools/population_anchor._churn_by_year` read it, so the
   band comparison and the board gate stop being taken on the renewal route alone.
3. `tools/fit_year_level_anchor.py` fits `YEAR_LEVEL_ANCHOR` against the whole-book target.

## The one substantive design claim, stated before it is tested

**The year level anchor must NOT scale the SVT route, and the capture says the world already
agrees.** On all 1,266 SVT segment rows, `realized_churn_probability` equals
`svt_inertia_hazard(years_on_svt, segment_days) × action_propensity` exactly — the recorded
`sim_level_anchor` is not multiplied in. `simulation/departure_risks.build_departure_risks`, by
contrast, computes `CAUSE_SVT_INERTIA = clip(level_anchor × svt_inertia × action_propensity)`.

The world's behaviour is the correct one and the composed form is the defect: `svt_inertia_hazard`
is derived from an **already-absolute published annual rate** (0.20 recent / 0.10 long-stayer),
so multiplying it by a year ancher of ~4.6 would put annual drift off SVT near 65% against a
published 20%. Anchoring an absolute published rate a second time destroys the only level anyone
could check.

So the whole-book fit solves for the **renewal route's** anchor with the SVT route's contribution
held at its own published level. That is not a convenience: it is the same separation the anchor
already claims — the record says how many households left, the hazards say which ones and why —
applied to a book with two routes instead of one.

## Predictions

**P1 — the fit is unreachable in at least one year.** The SVT route's expected departures alone,
at its own published anchor, will exceed the published whole-book band's HIGH endpoint × that
year's account count in at least one year of 2017–2024, so no renewal anchor ≥ 0 can bring the
whole book down to the record. **Named in advance: 2022**, because the published band is at its
2.9–4.3% trough that year while SVT drift is unconditional on market conditions and 2022 is the
year the capture has the most SVT segments in.
*Refuted if* every year's SVT-only floor sits at or below its band's high endpoint.

**P2 — every reachable year fits LOWER than today's constant.** The committed
`YEAR_LEVEL_ANCHOR` was solved to put the renewal route *alone* on the published rate. Under the
whole-book target the renewal route has to share that rate with the SVT route, so each reachable
year's fitted anchor will be strictly below its committed value.
*Refuted by* any reachable year fitting at or above its current value.

**P3 — the world is currently HOT on the whole book, not cold.** At the committed anchors, the
whole-book **expected** departure rate will sit ABOVE the published band in a majority (≥5) of
2017–2024. This inverts the finding the anchor was built for, which was that the world ran 3.45x
SHORT — because that reading was taken before the second route existed.
*Refuted if* ≤4 of the eight years read above their band.

**P4 — 2022 cannot be fitted on the renewal route at all, for a second and independent reason.**
The capture has **zero** renewal decisions in 2022, so that year has no renewal population to
solve an anchor against, whatever the target. A fit that returns a 2022 value anyway is reporting
a number it did not measure.
*Refuted if* the capture is found to carry renewal decisions in 2022 after all.

## What is NOT being done, and would be the failure

Widening the band. Re-fitting on the renewal route and calling it the book. Publishing a whole-book
rate whose denominator is a decision count. Emitting a 2022 anchor by interpolation. Each of these
makes the instrument agree with the world by moving the instrument.

## Result

*Appended after the measurement. Nothing above this line is edited.*

Measured on `docs/reports/ladder_churn_factors.json` + its `_svt_segment_decisions.json` sibling,
2026-08-31, through `tools/measure_departure_level.py` and `tools/fit_year_level_anchor.py`.

### The whole book, at the committed anchors

| year | published band | SVT floor % | expected % | realised % | accounts | dep ren | dep SVT |
|---|---|---|---|---|---|---|---|
| 2017 | 13.5–14.0 | 9.27 | **14.26** | 17.54 | 57 | 5 | 5 |
| 2018 | 19.5–20.0 | 11.36 | **22.52** | 41.51 | 53 | 9 | 13 |
| 2019 | 20.7–21.3 | 11.60 | 18.94 | 12.82 | 39 | 2 | 3 |
| 2020 | 22.5–23.0 | 9.85 | 20.33 | 14.58 | 48 | 4 | 3 |
| 2021 | 17.9–18.4 | 9.62 | 16.73 | 20.37 | 54 | 5 | 6 |
| 2022 | 2.9–4.3 | **12.80** | **12.80** | 7.27 | 55 | 0 | 4 |
| 2023 | 8.9–12.5 | 12.43 | **17.36** | 20.37 | 54 | 1 | 10 |
| 2024 | 12.5–16.1 | 9.12 | **16.62** | 12.96 | 54 | 2 | 5 |

**P1 — CONFIRMED, in the year named in advance.** 2022's SVT route alone expects 12.80% against a
published band topping out at 4.30%. No renewal anchor ≥ 0 can bring the whole book down to the
record: the fit refuses that year and names the cause rather than clamping.

**P2 — REFUTED, and the refutation is the more useful result.** Only four of the nine years with a
renewal population fit *lower* (2017, 2018, 2023, 2024); five fit *higher* (2016, 2019, 2020, 2021,
2025).

The prediction saw one of two effects. Sharing the target with the SVT route does push the renewal
anchor down — but the **denominator also moves**, from renewal decisions to accounts, and that
pushes it up. 2020 is the clean case: the old fit put the mean over **17 renewal decisions** at
23%, about 3.9 expected departures. The whole-book fit needs 23% of **48 accounts** less the SVT
route's 4.7, which is 6.3 departures out of the same 17 decisions — a mean of 37%, so the anchor
rises from 4.43 to 5.85. **Which effect wins is a per-year fact about how much of the book reaches
a renewal roll**, and no single-signed prediction about the direction of the re-fit was available
to be made. Recorded rather than revised, per CLAUDE.md: a prediction filed after the answer is not
a prediction.

**P3 — CONFIRMED, and only just: exactly 5 of 8.** 2017, 2018, 2022, 2023 and 2024 read above their
band's high endpoint; 2019, 2020 and 2021 read below. The margin being one year wide is worth
saying out loud — the prediction would have been refuted by a single year moving, so it is weak
evidence for the "hot" reading and strong evidence only for the narrower claim that **the world is
no longer uniformly cold**, which is what the pre-C1b 3.45x-short finding asserted.

**P4 — CONFIRMED.** Zero renewal decisions in 2022. The fit refuses that year for this reason *and*
for P1's, and reports both: a reader shown only "no renewal decisions" would go looking for renewal
decisions, which would not help, because the SVT floor binds independently.

### The fitted whole-book anchors

    2017: 4.027397   2018: 2.538637   2019: 4.348151   2020: 5.849491
    2021: 4.042171   2023: 0.029981   2024: 2.800513

2016, 2022 and 2025 are absent on purpose and must not be interpolated;
`year_level_anchor` already falls back to the reference year, and that fallback is declared where
an invented value would not be.

**2023 is a near-miss worth flagging rather than shipping quietly.** Its SVT floor is 12.43%
against a target of 12.50%, so the fitted anchor is 0.03 — the renewal route is being asked to
contribute essentially nothing. That value is arithmetically correct and substantively a warning:
it says the SVT route very nearly exhausts 2023's published rate on its own.

### These numbers are NOT written into `simulation/departure_level_anchor.py`, and why

Two named causes, either of which alone is sufficient:

1. **The capture's producing code is not in this tree.** C1b's SVT departure roll and its
   `_svt_decisions` recorder were parked in the shared tree as another lane's uncommitted work
   (the finding says so in its own words). `simulation/run_phase2b.py` at this HEAD contains no SVT
   route. So the constant would be **unreproducible from the commit that carries it** — capture →
   fit → capture cannot even be started from here.
2. **The world and the composed form disagree about whether the anchor scales the SVT route**, and
   fitting under one reading while the world runs the other lands the world nowhere in particular.
   Filed separately as
   `WORKER_FINDING_THE_WORLD_AND_THE_COMPOSED_FORM_DISAGREE_ABOUT_WHETHER_THE_LEVEL_ANCHOR_REACHES_THE_SVT_ROUTE_2026-08-31.md`.

What *has* landed is the instrument: the union, the account denominator with its three enabling
properties checked, the whole-book fit with per-year named refusals, and a control whose seven
mutations all fire. **The re-fit is done and printable; pasting its output into the world waits on
the capture being reproducible.** Widening the band remains the thing that is never the answer.
