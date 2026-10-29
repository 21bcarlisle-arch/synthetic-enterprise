**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A catch-up is added to the bill gross, and its VAT never reaches the bill's VAT line (2026-10-29)

**Item:** `the-fresh-run-at-9553d403b7-is-graded` (Lane 0, correctness stretch). Found while classing the 25
`INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` breaches on the fresh 9553d403b7 book.

## The defect

`company/billing/monthly_bill_assembly.build_monthly_bills`, at the actual read that ends an estimate run:

```python
bill["total_amount_gbp"] = round(bill["total_amount_gbp"] + catchup["chargeable_gbp"], 2)
```

`chargeable_gbp` is gross: `_resolve_catchup` takes it from the run's fully priced totals, VAT included (its
docstring says so). `bill["vat_gbp"]` is never touched. So every bill carrying a catch-up:
- prints a VAT figure that leaves out the VAT on the correction;
- has a before-VAT amount (`total − vat`) that counts that VAT as the supplier's own charge.

The same VAT rule now has one more home. This is the shape CLAUDE.md cites, of one legal requirement with several
implementations.

## Measured (9553d403b7 book, `/var/tmp/clse/`)

| quantity | value |
|---|---|
| bills carrying an applied catch-up | 3,705 (3,701 domestic, 4 SME), on 809 accounts |
| VAT missing from those bills' VAT line (absolute, at the segment's rate) | about £5,568 domestic, £132 SME |
| revenue-row breaches explained wholly by it, to the penny | 7 of 25: SYN-2016-469g (32.59 = VAT on 684.21), PROS-2025-0106 (28.55 on 599.49), PROS-2017-0233 (44.01 of 44.65, the rest an open estimate tail), SYN-2016-153g, OCC-6b934fa268b1, OCC-2e29bf263cb4, PROS-2018-0002g |

**Correction, beside the earlier claim.**
`SEAT_FINDING_THREE_SMALL_EXCEPTIONS_TRACED_ON_THE_209C_BOOK_..._2026-10-29.md` said that on 469g, 153g,
PROS-2017-0233 and PROS-2025-0106 "the gap is the catch-up's kWh billed at that bill's rate, not the rates of the
months used". That is refuted. The catch-up is priced at the months' own rates. The gap is the catch-up's VAT,
counted as before-VAT revenue. The class (d) gap on PROS-2025-0106 is the same thing (599.49 − 599.49/1.05 = 28.55).

## Fix (not built here)

Carry the run's VAT delta, Σ(true `vat_gbp` − billed `vat_gbp`) over `pending_run`, scaled by
`chargeable/raw` where a back-billing write-off barred part of the delta, onto `bill["vat_gbp"]`. A test should
assert, for a domestic catch-up bill, that `vat_gbp` equals the VAT on the bill's own month plus the VAT on the
correction. The page (`tools/generate_billing_ledger.py`) and the payment ledger read the bill's `vat_gbp`, so they
follow. Whether the company's VAT return reads the bill or settlement has not been checked. Read it before
claiming any P&L or VAT liability effect.

Predicted after the fix, on a replay of this book: the 7 accounts above leave the revenue row. The 17 accounts of
`SEAT_FINDING_AN_ACTUAL_READ_UNDER_FIVE_POUNDS_OFF_THE_ESTIMATES_NEVER_CORRECTS_THEM_..._2026-10-29.md` do not.

## Built (2026-10-29), not yet graded on a run

The knowledge came first: `docs/market_research/back_billing_and_liability.md` §15.
- `_resolve_catchup` returns `chargeable_vat_gbp`: Σ(true `vat_gbp` − billed `vat_gbp`) over the run,
  scaled by chargeable/raw. The estimated bills now carry `true_vat_gbp` for it.
- The bill's `catchup_adjustment_gbp` is now the correction **before VAT**, and `catchup_vat_gbp` is
  its VAT. `catchup_vat_gbp` is added to `vat_gbp`. The total does not move, and footing holds with
  the same five lines.
- The readers that need the gross movement add the two fields together. These are
  `dd_balance_book`, `dd_review`, the ledger's restatement memo, `invoice` unit-rate netting and the
  Explore cast.
- The pre-bill VAT rate check takes the catch-up line into its base.
- The statement export and `bill_validation_comparison` read the line's `vat_basis`. A ledger from
  before the split still prints the old VAT-inclusive shape and is read as such.
- Test: `tests/company/billing/test_a_catch_ups_vat_is_on_the_vat_line.py`.

**Not checked yet:** whether the company's VAT return reads the bill or settlement. The prediction
above still stands to be graded on a fresh run: the 7 accounts leave the revenue row.

## Done (2026-10-29)

Built in 789d0a6d2 (above). It was graded on the 9553d403b7 book by replay, together with the class F fix:
`docs/staging/records/SEAT_PREREGISTRATION_EVERY_READ_NETS_ITS_RUN_AND_THE_CATCH_UP_VAT_ON_THE_VAT_LINE_2026-10-29.md`.
All 7 accounts leave the revenue row, as predicted. 3,705 bills carried a catch-up without its VAT on the VAT line,
and after the fix none do. The queued continuation `the-catch-up-vat-reaches-the-vat-line` is retired as premise
spent, naming 789d0a6d2.
**Residue, named:** the company's VAT return was not checked, so it is still unknown whether it reads the bill or
settlement. No P&L or VAT-liability effect is claimed.
