**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
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

## Cause found and fixed (2026-10-24, delivery seat)

- **The route.** `simulation.settlement_daily.fold_to_days` folds a term's half-hours into daily rows
  and sums every numeric field not on its carried list. `hmt_epg_receipt_gbp_per_mwh`, added by
  `ce35a25e21`, was not on that list, so each electricity daily row carried 48 x 318.76 =
  15,300.57 GBP/MWh. Gas is settled daily, which is why the gas stubs were right.
  `_estimate_records_at_tariff_rate` then priced the estimate's receipt off the summed rate. The
  run's 47.7, not 48, is still unexplained (a stub whose days are not all 48 periods is the lead
  belief). The probe below gives 48.0 on full days.
- **Measured at real inputs, with the run's own functions** (void, stamp, fold, estimate,
  `generate_bill`), 17-31 Jan 2023, 193.28 kWh: origin's fold gave a GBP 2,957.29 receipt and a
  GBP -2,968.26 bill. The fixed fold gives the **GBP 61.61** receipt and a GBP 72.21 bill. It is
  not a one-customer run: the tree has no one-customer flag, and an incoming occupier exists only
  inside a whole-population run.
- **The fix is a class fix.** A field named `*_per_mwh`, `*_per_kwh` or `*_per_day` is a rate, and
  it is carried from the day's first record whatever list it is on. Two other fields were also
  being summed 48 times: `flex_reference_price_gbp_per_mwh` and `flex_markup_per_mwh`. No reader
  outside tests takes them from the folded book. Control:
  `tests/simulation/test_settlement_daily.py::test_a_field_named_per_unit_is_carried_even_off_the_carried_list`.
  Removing the rule reds it.
- **The ledger drops nothing by sign.** `saas.ledger.build_ledger` books a receipt on every bill
  that carries one. The 5 negative bills were held by `validate_bills` (SLC 6.7: a line item is
  negative), and `accounting_close` hands the ledger only the issued ones. Not booking a bill that
  was never sent is right. The gap between carved and booked was the inflated receipt, and the hold
  is what kept the credit off the household's account.
- **The grader now refuses.** `tools.grade_svt_invoices_over_ceiling` lists `defects` and exits 1
  when any is present: carved != booked, a receipt carved outside the windows, or an estimated bill
  below zero. On `c5a8090187`'s output it names both defects: "carved GBP 205,866.61 != booked GBP
  199,968.51" and "5 estimated bill(s) below zero, worst OCC-eb8498f3f8aa 2023-01-17 GBP -2,949.65".
  On `88cdf35e48`'s output it names none.

**To close:** a fresh full run at a commit carrying the fold fix, graded with `defects == []`.
Prediction, filed before that run: carved equals booked to the penny, no estimated bill is below
zero, and the 5 electricity stubs carry receipts of about 1/48 of the table above (OCC-eb8498f3f8aa
about GBP 61). LATENT until that run exists, because no published run carries the defect yet. The
`domain_invariants` leg the section above proposed is not built: the grader's leg covers the same
property on every graded run.

## The closing run, in flight (24 Oct, 19:10 BST)

The s14clean arms finished at 15:36Z. The closing run was launched through `launch_long_job` as
`epgfold-fresh-1c30d6c728`, at `1c30d6c728`, which carries `3a31999db`. It runs in its own worktree
`/var/tmp/se-epgfold-1c30d6c728` and wrote to `/var/tmp/se-epgfold-out/`: the run's JSON, `run.rc`,
`grade.json` and `grade.rc` (the grader's own exit, 1 on any defect). The prediction above stands as
filed. It is graded here when `grade.json` exists.

## Graded, and closed (25 Oct, delivery seat)

The closing run finished (`run.rc` 0, `grade.rc` 0). `grade.json` at `1c30d6c728`:

- **Carved equals booked: GBP 200,091.73 = GBP 200,091.73,** on 3,544 bills carrying a receipt. None
  was carved outside the windows.
- **`negative_estimated_bills` is empty, and `defects` is `[]`.** The closing condition above is met.
- `unit_charge_fall` is unchanged in every quarter and fuel: 2022-Q4 elec 0.345 / gas 0.301, 2023-Q1
  0.496 / 0.396, and 2023-Q2 0.328 / 0.182.
- **Over the ceiling, 6 of 24,597 graded default-tariff invoices** (12,589 ungradeable). They sit on 2
  households, all outside the EPG windows (2019: 2, 2024: 4), and 0 are on actual-read accounts.

**The prediction held on every leg.** The five electricity stubs now carry the right receipts:

| account | stub start | receipt before | receipt now | bill total now |
|---|---|---|---|---|
| OCC-eb8498f3f8aa | 2023-01-17 | GBP 2,940.87 | GBP 61.61 | GBP 73.57 |
| OCC-cc0c78690877 | 2023-06-01 | GBP 2,024.78 | GBP 42.18 | GBP 106.51 |
| OCC-25ff8966357a | 2022-12-24 | GBP 476.39 | GBP 9.92 | GBP 23.18 |
| OCC-cc0c78690877 | 2023-05-27 | GBP 351.81 | GBP 7.33 | GBP 18.39 |
| OCC-a8253b022c52 | 2023-04-28 | GBP 104.27 | GBP 2.17 | GBP 6.25 |

Four of the five old receipts are 48.0× the new ones. The fifth, OCC-eb8498f3f8aa's January stub, is
47.73×. That stub's new receipt equals the probe's (GBP 61.61), so the 47.7 was a property of the old
over-carve alone. It no longer bears on anything, and it stays unexplained.

**The six over the ceiling** are neither a ToU pair nor an incoming occupant. They are a third cause:
a gas SVT term that starts off a cap quarter is billed at the mean of every rate it has carried. It is
filed as `SEAT_FINDING_A_GAS_SVT_TERM_STARTED_OFF_A_CAP_QUARTER_IS_BILLED_AT_THE_MEAN_OF_EVERY_RATE_IT_HAS_CARRIED_2026-10-25.md`.
