**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `price-cap` -- `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`

# Pre-registration: the EPG reaches the household's bill (cause B)

Written 24 Oct 2026, BEFORE any run carries the change. Follows "Next, ranked" item 1 of
`SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_2026-10-23.md`.
Not edited after a result exists; the result goes in its own section below.

## What changes, and the one variable

A domestic account's `svt` term settled inside 2022-10-01..2023-06-30 now carries, on each
settlement record, `hmt_epg_receipt_gbp` = kWh × (Ofgem cap − min(cap, EPG)) ex-VAT for that day
and fuel (`simulation.svt_product.stamp_hmt_epg_receipt`, which reads the same accessor the SVT
segment's own split reads). `revenue_gbp` is unchanged: it is still what the supplier receives.

`saas.bill_generator.generate_bill` carves `hmt_epg_receipt_gbp` out of the household's commodity
line, the way it carves the levy line, and reports it on the bill. VAT is charged on the household's
reduced subtotal. `saas.ledger` books a `epg_receipt_event` (Treasury cash in, ex-VAT) per bill
carrying a receipt, and `derive_pnl` counts it as revenue and as cash collected.

Nothing else moves: outside the EPG windows the field is absent and every bill is byte-identical;
fixed, deemed, flex and non-domestic terms carry no receipt.

## Predictions for the next fresh run, graded on `account_state_log` with
`tools/grade_svt_invoices_over_ceiling.py`

1. **Inside the EPG windows, `svt` invoices above the household ceiling fall to at most 300** (from
   the ~2,430 the A fix leaves there: 1,817 cause B + ~620 cause-A invoices that land on B). The
   residue allowed is the 122 cause-B bills that do not reproduce their struck rate (item 3) plus
   rounding. More than 300 means the receipt does not reach the bill on some route.
2. **Total `svt` invoices above the ceiling, all years: at most 500** of the svt-invoice
   denominator, which is reported beside it. (The A-fix prediction was 2,000-3,000; this one
   removes the EPG share of it.)
3. **Supplier ex-VAT revenue (`derive_pnl.revenue_gbp`) for Oct 2022-Jun 2023 moves by under 0.5%**
   against the same run's figure with the receipt added back to the bill, because the receipt is
   booked as revenue. Billed (inc-VAT) falls by receipt × 1.05; VAT remittance falls by
   receipt × 0.05. If revenue moves by more, the receivable is leaking.
4. **Household-side figures fall in the crisis quarters, direction only:** svt-household bill
   totals Oct 2022-Jun 2023 fall by roughly 45-55% of their unit charge (EPG 34.0p against a cap of
   up to 67.47p); bad-debt provision on those bills, DD levels set from them and arrears fall. I
   cannot predict the magnitudes of arrears and bad debt: the world's payment draw has no price
   input (`91ad4cad83`), so a lower bill may move them less than proportionally or not at all. That
   is itself a reading worth having.

## Choices, and the GAPs they carry

- **The receipt is cap − min(cap, EPG) per kWh, whatever the supplier's own SVT rate.** That is the
  world's existing split identity (`unit_rate = household_charged + hmt_epg_receipt`). GAP: the EPG
  scheme text is not in the commons (knowledge page, GAPs), so the per-unit discount rule on a
  default tariff priced below the cap is this design's reading, not a quoted rule.
- **The receipt bears no VAT.** GAP: the VAT treatment of the EPG payment is not in the commons.
  Treating it as outside the household's supply keeps the supplier's ex-VAT revenue exactly whole.
- **Booked as cash at the bill's period start.** GAP: the scheme's payment timing.
- **Estimated bills** scale the receipt with the commodity (`_estimated_settlement_records`), so an
  estimate charges the household the true bill's EPG rate and carries the estimate's receipt; the
  catch-up reconciles on the household's basis. **Not covered:** a void stub estimated at the
  tariff rate (`_estimate_records_at_tariff_rate`) has 0 kWh and so no receipt, and is priced at the
  revenue rate. Rare inside the nine months; named, not fixed here.
- **Not in this increment:** the EPG on fixed terms (knowledge page GAP), and wiring
  `company/regulatory/epg_reconciliation_register.py`, which stays unreached by the run as it was.

## Result

*(empty until the fresh run exists)*
