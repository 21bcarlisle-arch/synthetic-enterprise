**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: what putting the switching reference on one VAT basis moves

Claim `compare-the-switching-reference-on-one-vat-basis`. Filed before either run. The parent is
handed-on item 2 of
`SEAT_FINDING_THE_SVT_SEGMENT_NOW_BILLS_EX_VAT_AND_NO_FIRST_TERM_SITS_ABOVE_THE_EX_VAT_CAP_2026-10-01.md`.

## What the item said, and what reading the code added

The item named one site: `customer_events._price_differential_vs_market` differences an ex-VAT
struck rate against the inc-VAT published SVT. Reading the chain found that the same cross-basis
comparison is made at **six** sites in the world, not one:

1. `customer_events._price_differential_vs_market`: the offer, which drives the churn roll.
2. `customer_events._reference_level_gbp_per_mwh`: the ledger's ex-VAT position goes to the rival.
   Its contract is "what a comparison site would publish", which is inc-VAT like the anchor it is
   chased from. So the rival read the company as 4.8% cheaper than it was and chased it further
   down.
3. `competitor_reference.competitor_reference_rate_gbp_per_mwh`: the rival's cost floor (wholesale,
   policy, network and margin, all ex-VAT) clamps an inc-VAT reference. So the rival could follow
   4.8% below its own costs.
4. `customer_events._svt_position`: the logged `price_differential_vs_svt`.
5. `tools/run_price_ladder._svt_position_pct`: reconciled against field 4, so it moves with it.
6. `run_phase2b._build_churn_basis_risk`: `rate_vs_svt_pct`, which `saas/reporting/annual_report`
   reads.

The change adds one helper, `price_cap_enforcement.household_price_inc_vat(ex_vat)`, which
returns `ex_vat × (1 + DOMESTIC_VAT_RATE)`. All six sites now take the gross-up from it. Leaving
4 to 6 alone would make `price_differential_vs_svt` and `price_differential_vs_market_reference`
disagree by 5% with no rival present, under two names that the 2026-08-28 reconciliation requires
to agree.

## The measurement: one variable

Both runs are the default world, `simulation.run_phase4c_on_phase2b.run_phase2b()`, from two
`git archive` extracts of origin/main `50bde35ab`. One is the base alone
(`/var/tmp/se-vatref-base`). The other is the base plus exactly this diff
(`/var/tmp/se-vatref-new`). The script is `/var/tmp/se-vatref-measure.py`, which writes
`vatref_rows.json` in each tree.

A "matched renewal" is an event with `departure_occasion == "renewal"` whose `(customer_id,
event_date, commodity, unit_rate_gbp_per_mwh)` is identical in both runs. A churn the change causes
can change what the company later books and strikes. So only matched events isolate the
instrument, and the counts are book-level.

## Printed before predicting: the curve at real inputs

`churn_position_multiplier(d)` against `d' = (1+d)·1.05 − 1`:

| d | m(d) | d' | m(d') | ratio |
|---|---|---|---|---|
| −0.20 | 0.3125 | −0.160 | 0.3641 | 1.165 |
| −0.10 | 0.5102 | −0.055 | 0.7278 | 1.427 |
| −0.05 | 0.7463 | −0.003 | 0.9833 | 1.318 |
| 0.00 | 1.0000 | 0.050 | 1.3400 | 1.340 |
| +0.10 | 1.9600 | 0.155 | 2.6900 | 1.372 |

Near parity the price factor alone rises by ×1.3–1.5. The roll then dilutes that. Elasticity
weights the factor, other factors multiply it, and the world's ceiling caps the result.

## Predictions

- **P1 (instrument, exact).** On every matched renewal, the new `price_differential_vs_svt` equals
  `round((1 + base) × 1.05 − 1, 4)` within 2e-4. The same holds for `rate_vs_svt_pct` in
  `churn_basis_risk` within 0.02.
- **P2.** `market_reference_gbp_per_mwh` never falls on a matched renewal. Its mean rises by between
  0% and 2%: the rival chases a dearer-looking company less far, and its floor is higher.
- **P3.** The mean `price_differential_vs_market_reference` over matched renewals rises by between
  +3.0 and +5.5 percentage points. The ceiling is +5 points plus scale, and P2's higher reference
  takes some of it back.
- **P4.** The mean `realized_churn_probability` over matched renewals rises by between +10% and +40%
  relative.
- **P5.** The count of renewal-occasion `churned` events rises by between +10% and +45%. Departures
  on every other occasion move by less than 15% in either direction; they reach the differential
  only through book feedback.
- **P6.** The share of matched renewals whose offer reads cheaper than the SVT
  (`price_differential_vs_svt < 0`) falls.
- **P7.** Direction: more churn, never less. The change moves against the company. It was decided
  blind to company P&L, as R13 baseline (fidelity). The world was crediting every offer with a VAT
  saving no household could bank.

If P4 or P5 comes in above its band, the curve is steeper at the book's real positions than the
table above suggests. That is a finding about the curve, not grounds to tune it.
