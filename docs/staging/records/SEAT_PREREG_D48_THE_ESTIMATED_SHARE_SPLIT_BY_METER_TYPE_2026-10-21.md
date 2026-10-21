**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# Pre-registration: the estimated share split by meter type, by year (2026-10-21)

*Worker tick, 2026-10-21, written before any figure below was read. It answers the "measure first" line of
`docs/staging/done/SEAT_FINDING_D48_THE_ESTIMATED_SHARE_FALLS_ONLY_TEN_POINTS_THROUGH_THE_SMART_ROLL_OUT_2026-10-14.md`.*

**Question.** Is the flat estimated share (about 67% of billed kWh on both fuels, 2016-2025) caused by
the book's smart share staying flat, or by smart accounts being billed on estimates anyway?

**Instrument.** The bills of the published run (`run_output_8b6fea024_20261019T033010Z`, read through
`tools/run_output_store.load_run_output`), grouped by period-end year and fuel. Each bill's meter type is
whatever the bill or the account record states. If no per-bill or per-period meter type exists, the
account's type stamped at acquisition is used, and that is said beside the table.

**Predictions.**
1. The smart share among billed accounts rises by less than 25 points from 2016 to 2024. The meter type is
   stamped at acquisition, so the book follows its acquisition cohorts and not the national roll-out.
2. Smart accounts' estimated share of billed kWh is under 20% in every year from 2019. Traditional
   accounts' share is 65% or more in every year.
3. Hence the flat trend is the book's composition (a world question: are meters ever exchanged after
   acquisition?), and not the read model.

**Refutation.** If smart accounts' estimated share is 40% or more in any year from 2019, prediction 3 is
refuted. Then the read model fails to reach smart reads, and the defect is in the read path, not in the
book's composition.

## Graded (same tick, after the predictions above)

All three held. The figures and the cause are in
`docs/staging/WORKER_FINDING_D48_THE_ESTIMATED_SHARE_IS_FLAT_BECAUSE_NO_METER_IS_EVER_EXCHANGED_AFTER_ACQUISITION_2026-10-21.md`.
