**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `price-cap` -- `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`

# The void-stub EPG fix gives households credits of about 48× the Treasury's share, and the ledger books none of it

Found by the first live read of `tools.grade_svt_invoices_over_ceiling`'s `epg_receipt` section
(`dcf5f10f3`). The read was on a full run at `c5a8090187`, the first run carrying `ce35a25e21`, which
is the void-stub estimate's EPG. The run is at `/var/tmp/se-overcap2-out/run_output_c5a8090187.json`,
and the grade is in `grade.json` beside it.

## What was measured

- **Carved ≠ booked.** £205,866.61 was taken off 3,544 household bills as the Treasury's share.
  `ledger_pnl.epg_receipt_gbp` booked £199,968.51 on 3,539 events, so £5,898.10 is unbooked. On
  `88cdf35e48`, the run before the fix, the two were equal to the penny (£199,865.32).
- **Where it is.** There are 9 estimated void-stub bills with true kWh 0 and a receipt, on 4
  incoming-occupant households, Dec 2022 to Jun 2023. The 4 gas stubs are about right (1,184 kWh,
  £76.24) and booked. **The 5 electricity stubs are not right.** Each carries a receipt of about 47.7×
  its kWh at the EPG rate, so the commodity line goes negative:

  | account | period | kWh | receipt | right receipt | bill total |
  |---|---|---|---|---|---|
  | OCC-eb8498f3f8aa | 17-31 Jan 2023 | 193.3 | £2,940.87 | £61.61 | **−£2,949.65** |
  | OCC-cc0c78690877 | Jun 2023 | 266.8 | £2,024.78 | | −£1,975.22 |
  | OCC-25ff8966357a | 24-31 Dec 2022 | 58.2 | £476.39 | | −£466.60 |
  | OCC-cc0c78690877 | 27-31 May 2023 | 46.4 | £351.81 | | −£343.31 |
  | OCC-a8253b022c52 | 28-30 Apr 2023 | 13.7 | £104.27 | | −£100.95 |

  Their receipts sum to £5,898.10, which is the unbooked amount exactly. The household is credited
  about £5,800 it never paid for, and the supplier books nothing to replace it. That is a transfer the
  world never made (M2), so it is worse than the defect it replaced.
- **The over-cap grade could not see it.** A negative bill is under the ceiling. Item 1's prediction,
  "inside the EPG windows at most 23, none an estimate on true kWh 0", reads as held (0 inside). The 9
  stubs pass by going negative, so that pass is hollow.

## What is ruled out, and what is not yet known

- `simulation.svt_product.stamp_hmt_epg_receipt` gives an electricity row in Jan 2023 a rate of
  £318.76/MWh ex-VAT, which is right.
- `company.billing.monthly_bill_assembly._estimate_records_at_tariff_rate` plus
  `saas.bill_generator.generate_bill` was run on a synthetic 720-row half-hourly void stub at that rate
  (193.28 kWh). It gives a £61.61 receipt and a +£73.59 bill, which is right.
- The real bill's revenue-rate commodity, its commodity plus its receipt, is £108.73. That equals the
  synthetic's to the penny. **Only the receipt is inflated**, so the rows the run hands the estimate
  must carry a receipt rate about 47.7× the stamp's.
- **I cannot yet say how.** It is not exactly 48. It touches electricity only, and gas is daily, so a
  half-hourly route is the lead belief, not a finding. The next step is one stub's `months[month]`
  rows at the call on line ~864, printed in a one-customer run.
- **The ledger's omission is a second question.** The 5 negative bills raise no `epg_receipt_event`.
  The 4 positive gas stubs do. If `saas.ledger` drops a bill with a negative total, that drop would
  also hide any future over-carve.

## Why BLOCKING

`ce35a25e21` is on origin. The parent finding's clearing condition, "a published run at a commit
carrying the three fixes", would publish these bills. 4 households would carry credits of up to
£2,950, and the ledger would carry a £5,898 hole in revenue and cash. A published figure would be
wrong, which is `finding_severity`'s BLOCKING. The parent's "To close" now names this file.

**To close:** once the receipt-rate route is fixed, `epg_receipt.carved_gbp == booked_gbp` must hold
on a fresh run, and no default-tariff bill may have a negative commodity line inside the windows. A
one-leg control fits that second property. It belongs in the class invariants
(`company/compliance/domain_invariants.py`) rather than in this grader.

## The rest of the fresh run's grade, against filed predictions

- Item 1, outside the windows: predicted "stays at 72 within noise". **Refuted:** 6, on 2 households,
  and none on actual-read accounts (it was 87). More than one thing changed between `88cdf35e48` and
  `c5a8090187`, so I cannot yet say why. The ToU-pair misgrade's footprint is gone. Something between
  the two commits changed the pair, or the accounts it fell on.
- Denominator: 24,592 gradeable default-tariff invoices (24,597 before), with 12,594 ungradeable.
- `unit_charge_fall` is identical to `88cdf35e48` in every quarter and fuel. The bills that carried a
  receipt before the fix are unchanged.
