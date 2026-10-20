# Pre-registration: the retention guard's offers once it weighs the term's contribution

**Written 2026-10-20, before any run carrying the change has been launched.** Claim
`one-contribution-margin-for-every-renewal-decision` (Lane 0, seat direction), which subsumes
`c34-renewal-margin-net-of-pass-through`. The findings are
`SEAT_FINDING_THE_RETENTION_GUARD_WEIGHS_THE_SPREAD_OVER_WHOLESALE_AS_THE_VALUE_IT_PROTECTS_2026-10-20.md`
and the C34 finding it shares a cause with.

## What changes, said first

The retention guard's `expected_margin` and the missed-retention log's `expected_term_margin_gbp`
were `(unit rate − company forward) × company EAC / 1000`. Both become `term_contribution_per_year`
(`company/crm/renewal_advice_desk.py`), the function C34's `term_contribution_per_month` is now
that value over 12:
`(unit rate − pre_margin_unit_rate) × company EAC / 1000 − FIXED_OVERHEAD_GBP_PER_YEAR[segment]`.
The standing charge stays out as the GAP §6.1 states. Where the term records no locked costs the
value is `None`: the guard already makes no offer there (both cut sizings need the same floor), and
the missed log carries `None`, which `counterfactual_retention` counts as unpriced.

This is the default policy. The off book moves.

## What the inputs say before the run

`/var/tmp/se-ret-margin/reconstruct.py` rebuilt each of the published off book's 92 offered rows
(19 Oct 15:02Z book) outside the run: EAC from the logged cost and discount, the forward from the
logged margin, and the locked costs from the published schedules on the term start, with the notice
taken as start − 42 days. It is an approximation used only to predict.
- Old margin, median GBP 290 a year. New contribution, median −GBP 31.
- 11 of the 92 offers still pass `contribution + acq_cost_saved > retention cost`: 11 electricity,
  0 of 2 gas. They are rows whose strike an upstream writer raised above cost, or very large accounts.
- Under the old margin nothing could fail the value test, because the spread always exceeded a cut
  floored at cost. So no row the old guard refused can pass the new one at the same inputs.

## Predictions, on the full window and default seed, with only this change added

- **R1. Retention offers (`retention_log`) fall from 92 to between 3 and 30.**
  Point estimate: 11.
- **R2. Retention spend (sum of `retention_cost_gbp`) falls from GBP 2,559 to below GBP 1,300.**
  The surviving offers include the large accounts, so spend falls by less than the count does.
- **R3. Churned-with-no-offer rows (`no_offer_churn_log`) rise from 36 to between 55 and 140.**
  The 34 who churned despite an offer now churn without one. Some of the 58 who were retained
  also go.
- **R4. The missed log's median `expected_term_margin_gbp` (non-`None`) falls from GBP 222 to
  below GBP 0.**
- **R5. No offered row has a `None` margin.** This is the control that the floor gate and the
  value gate agree.

I cannot yet say which way the book's total net margin moves. Fewer discounts and more churn pull
in opposite directions, and the churn is on legs whose contribution is mostly negative. The run
reports it; it is not predicted.

**C34's P2′ band** (`SEAT_PREREG_C34_P2_ON_THE_TERMS_CONTRIBUTION_2026-10-20.md`, 0–10 advised of
about 978) **is restated unchanged** for the on-arm run on this book. The guard change moves which
households are on the book at each roll, but not the contribution any one of them carries.

## What each refutation would mean

- **R1 above 30.** The upstream writers raise strikes above cost far more often than the 19 Oct
  book showed, or the reconstruction's locked costs are too high. Print `expected_term_margin_gbp`
  on the offered rows before reading anything else.
- **R1 below 3.** Either the floor or the overhead is double-counted somewhere. Check that the guard's
  contribution and `_cut_inputs["cost_floor"]` read the same `pre_margin_unit_rate`.
- **R5 fails.** The guard can offer on a term that has no floor. That is a defect in the cut sizings,
  not in this change.
