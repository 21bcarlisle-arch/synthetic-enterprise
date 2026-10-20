**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# D48's unbilled accrual: what it is in this run, and what it measured (2026-10-20)

*Delivery seat, 2026-10-20. Discharges the accrual clause of
`SEAT_FINDING_D48_THE_EXPERT_HOUR_FAILS_ON_THE_CLAIM_NOT_THE_MEASURE_2026-10-14.md` (MAJOR #2).*

## What the accrual is, before it is measured

Unbilled energy at a period end is energy the company believes was used and has not charged
anyone for. Per account, at a month end T: the company's own figure for each period up to T (the
actual read where it has one; otherwise the estimate it made for that period from its last actual
reads shaped by the published profile, or before any read from the registry EAC/AQ with the TDCV
fallback -- `unread_month_estimate.py`, already stamped on every bill as
`estimated_consumption_kwh`), less what it ISSUED bills for. Priced at the account's own unit rate.

In this run every account is billed every calendar month to the month end, so the only way a
period's energy is used and not charged is that the pre-bill gate HELD the bill
(`pre_bill_validation.validate_bills`): the ledger does not recognise it, the customer never sees
it. A held estimate stays unbilled until an actual read ends its run (the catch-up reconciles it as
"billed nothing", `monthly_bill_assembly._resolve_catchup`); that is the same "a read ends the run"
rule E3's `estimated_billing_outstanding` uses, and it is reused, not restated. A held bill on an
actual read is not in any estimated run, so no catch-up ever recovers it.

Centrica's "unread revenue" = billed-on-estimate (E3's figure) + unbilled (this). Both are now
computed; they count different bills and are never added into one number on our page.

## Pre-registration (written before any run figure was read)

1. The accrual at each year end is non-zero but small: under 1% of that year's issued kWh per fuel.
2. Most held bills are on an estimate rather than an actual read.
3. Some held ACTUAL-read bills exist on the published run, and their energy is never billed later.

## Measured

On the published run's bills (`docs/reports/run_output_latest.json`, run_output_44a21e3e8_20261020T085542Z,
38,005 bills, run end 2025-06-07), through the run's own door
(`company.interfaces.bill_assembly.billing_accuracy` -> `K1_unbilled_accrual`). 46 bills were held:
40 estimated, 6 on an actual read. Every one is electricity; gas has a measured zero at every
month end.

| Month end | Accounts | Held estimates open | Held actuals | Unbilled kWh | £ net of VAT | of which >12 months old | of which on closed accounts | Issued elec kWh that year |
|---|---|---|---|---|---|---|---|---|
| 2016-12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 444,578 |
| 2017-12 | 2 | 2 | 0 | 7,146 | 888 | 0 | 0 | 779,609 |
| 2018-12 | 3 | 6 | 1 | 18,293 | 2,539 | 0 | 12,825 | 675,392 |
| 2019-12 | 3 | 14 | 1 | 38,651 | 6,232 | 14,797 | 12,825 | 634,160 |
| 2020-12 | 3 | 7 | 1 | 19,937 | 2,873 | 14,797 | 12,825 | 617,955 |
| 2021-12 | 2 | 5 | 2 | 17,024 | 2,414 | 14,797 | 12,825 | 614,587 |
| 2022-12 | 2 | 5 | 3 | 19,186 | 3,774 | 17,024 | 12,825 | 610,865 |
| 2023-12 | 3 | 6 | 3 | 21,337 | 4,295 | 17,024 | 12,825 | 641,009 |
| 2024-12 | 2 | 5 | 3 | 19,186 | 3,774 | 19,186 | 12,825 | 686,255 |
| 2025-06 (run end) | 3 | 5 | 6 | 27,632 | 6,192 | 19,186 | 12,825 | 317,229 (half year) |

The last column is a year's FLOW beside a STOCK at one date, so their ratio is not a share of
anything; it is there for scale only.

**Pre-registration graded.**
1. REFUTED. The stock is 1-6% of the year's issued electricity kWh, not under 1%. It is
   concentrated: seven accounts across the decade, two or three at any year end.
2. CONFIRMED. 40 of 46 held bills are estimates.
3. CONFIRMED. Six held actual-read bills on two accounts, never billed later. One
   (OCC-8c6b8bb21743, 2025-01) carried a 1,266 kWh / £310 catch-up that went out with nobody.

**What it is made of.** Every held bill on this run was held by the same check: `vat_by_segment`,
a "resi" account whose metered load (2,000-4,300 kWh a month) implies a non-domestic customer. The
gate holds the bill and nothing ever resolves the hold, so the energy stays unbilled. One leaver,
PROS-2017-0117, left in April 2018 with five held estimates (12,825 kWh) and no read: the whole
"closed account" column. PROS-2017-0336 had 32 held estimates over 2017-2021, each recovered by a
later read's catch-up (subject to the 12-month bar).

**Against the one published witness.** Centrica's year-end gross unbilled is about 20 days of
revenue (§K1). Ours is near zero by construction for every ordinary account, because calendar
billing to the month end leaves no between-bill-runs part. What we have is only the
billing-failure part of K1. That gap is stated in the note's K1 row, not filled with a number.

## What this discharges, and what it leaves

- **Discharged:** MAJOR #2 of the 2026-10-14 expert hour. The accrual is computed, from the
  company's own bills only, and reached from the run through the issuance door
  (`bill_assembly.billing_accuracy` names the held bills, because issuance is decided there).
  Controls: `test_the_unbilled_accrual_takes_every_branch_and_counts_only_energy_never_issued` and
  `test_the_run_door_carries_the_accrual_and_it_counts_a_bill_the_gate_held`. Four mutations went
  red: accrual dropped from the summary, door passing no held set, the "a read ends the run" rule
  removed, and a held actual's catch-up dropped.
- **Reused, not restated:** E3's predicate is now `saas.ledger.open_estimated_bills`, the one
  statement read by both `estimated_billing_outstanding` and the accrual. The estimate per period is
  the one `unread_month_estimate.py` already stamped on the bill.
- **Still open, filed here:**
  1. `account_billing_accuracy` counts held bills in `billed_kwh` and K2's `estimated_kwh`. A held
     bill was never billed. 46 of 38,005 bills, so the published shares barely move, but "billed"
     includes bills nobody received. Fix: the same held set, passed in.
  2. A `vat_by_segment` hold is never resolved, so the same household's energy goes unbilled month
     after month. A real exception queue is worked: the account is re-segmented and billed, or
     confirmed domestic. `release_confirmed_domestic` exists for the consumption-scale hold only.
     That is a billing-operations gap, not something to fix in the measure.
  3. The accrual is not yet on the billing page (`published_view`). The summary carries it.
  4. Billed against settled (K6) stays a GAP: settled volume does not cross the seam.
