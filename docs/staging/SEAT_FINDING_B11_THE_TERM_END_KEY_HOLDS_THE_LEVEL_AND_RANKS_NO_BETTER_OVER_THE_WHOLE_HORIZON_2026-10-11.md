**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# B11 slice 9 result: the term-end key holds the flat level and ranks no better over the whole held-back horizon

Claim `b11-term-end-hazard-standardised-for-calendar-year`. The predictions and the code that
measures them landed first, as `49802cc9d`:
`docs/staging/records/SEAT_PREREG_B11_NINTH_SLICE_THE_TERM_END_HAZARD_STANDARDISED_FOR_CALENDAR_YEAR_2026-10-11.md`.
This file grades them and leaves them as written.

## The rule

`run_backtest(tenure_key="term_end")`: the per-customer hazard is the segment's flat hazard times
the ratio of its term phase (the term-end month, tenure 12, 24, …; or in term) to its calendar
year's rate, fitted on the fit window. The term-end month leaves at about 4.1× its calendar
year's rate at every cut (4.17 (3.44, 5.02) at 2020). In-term months leave at 0.75×.

## The measurement

Book `/var/tmp/b11s5_run/run_output_b11s5.json`, whole fit window, move register applied.
Level is mean p minus the realised rate. AUC compares departers against stayers. Brackets are 95%.

| cut | graded / left | level: term end | level: flat | level: contract year | AUC: term end | AUC: flat | AUC: contract year |
|---|---|---|---|---|---|---|---|
| 2020 | 247 / 106 | +0.255 (0.193, 0.317) | +0.241 (0.180, 0.303) | +0.361 (0.299, 0.423) | 0.533 (0.461, 0.605) | 0.524 | 0.515 |
| 2022 | 253 / 63 | +0.180 (0.126, 0.233) | +0.169 (0.116, 0.223) | +0.023 (−0.035, 0.081) | 0.483 (0.404, 0.563) | 0.481 | 0.485 |
| 2023 | 260 / 52 | +0.063 (0.015, 0.112) | +0.057 (0.008, 0.106) | −0.013 (−0.062, 0.037) | 0.509 (0.424, 0.594) | 0.446 | 0.530 |

The paired AUC differences, term end against flat and term end against contract year, cannot tell
at any cut. The largest is term end − flat at 2023: +0.063 (−0.019, 0.145).

## The predictions, graded

- **P1 (the level sits within ±0.02 of flat, with the same sign, and over-predicts at 2020 and
  2022): HELD.** The differences are +0.014, +0.011 and +0.006.
- **P2 (no AUC difference against flat can be told): HELD** at all three cuts.
- **P3 (the AUC interval includes 0.5 at 2020 and 2022; at 2023 the point is above 0.5 and the
  interval still includes it): HELD.** 2023 reads 0.509 (0.424, 0.594).
- **P4 (no Brier difference against flat can be told): REFUTED at 2020 and 2022.** Flat is better
  by +0.0075 (0.0051, 0.0098) and +0.0043 (0.0019, 0.0066). At 2023 the difference cannot be told.
  The cause is the level, not the ranking. The term-end rule's mean p sits slightly above flat's,
  because the held-back horizon has a larger share of term-end months than the fit window, where
  every year-0 month is in term. Over-predicting by slightly more costs a little Brier. Slice 6
  found the same thing: a Brier score here grades the level.

## The decision, by the rule written before the run

The default changes to `term_end` only if it ranks no worse than the contract-year key at any cut
(that held: none can be told) AND its |level miss| is no larger than the contract-year key's at
two of the three cuts. **That held at 2020 only.** At 2022 and 2023 the contract-year key's level
is closer. **So the default stays `contract_year`**, and `term_end` stays reachable as an argument.

Read that against slice 7. At 2022 and 2023 the contract-year rule's level is good because its
oldest contract year is fitted on the cut year alone, which is the collapsed-switching year. That
is recency, not tenure. The rule did what was written, and it chose the better level for a
reason that does not carry. That is what a pre-registered rule is for, so it stands. But no reader
should take the 2022 and 2023 level as evidence for the contract-year table.

## What this says about the instrument, which P2 and P3 predicted

Over 18 to 54 held-back months, every account passes nearly the same number of anniversaries. So
the term-end key separates accounts by about 0.02 in p (sd). There is nothing for it to rank with.
The full-horizon AUC asks the wrong question of a term-end key. What a supplier acts on is the
**next** term end.

**Not pre-registered: a diagnostic.** Under the term-end key at 2020, switchers rank above stayers
at 0.597 (0.513, 0.681), and movers at 0.446 (0.352, 0.540). Slice 6 had switchers at about 0.58
to 0.59 under both of the older rules, so this is the segment, not the key.

## Proposed next slice (10), for the seat to order

Grade departure over each account's **next term end only**, a 12-month horizon from the cut. In
that window the key separates accounts whose term ends early from those whose term ends late, and
it is the decision a retention lever acts on. Grade it at the same three cuts, with the level and
the ranking kept separate and the predictions written first. The switch term alone is the subject,
because a retention offer does not act on moves. This needs a horizon argument on `run_backtest`.
Nothing else is needed.
