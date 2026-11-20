**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# Billing property tests find a pound-a-month DD overcharge (fixed) and three VAT readings that disagree (2026-11-20)

**Origin.** Item 2 of the director's 20 Nov steer
(`docs/staging/advisor/done/DIRECTOR_STEER_GATES_JUDGE_FROM_THE_BASE_PROPERTY_TESTS_FOR_BILLING_AND_DIFF_TRIGGERED_CHECKS_2026-11-20.md`).
Hypothesis 6.170.17 is now a test dependency (`requirements.txt`). The properties are in
`tests/company/billing/test_billing_and_payment_properties.py`, and each one is taken from the
16 Nov declared lifecycle (5bf7e7c872), VAT Notices 701/19 and 700, or the director's 1 Sep
"annualised plan" correction. None is read off the code under test. There are 10 tests, run
derandomised with no example database, and they take about 2 s.

## What the properties found

1. **FIXED: a reviewed DD was a pound a month over whenever the year was an odd whole number of
   pounds times twelve.** `dd_review._recommended_monthly` used `round(monthly + 0.5)` and called
   it "ceiling to the pound". Python rounds a half to the even number, so £120 a year gives £10 a
   month, but £132 gives £12 instead of £11, and £156 gives £14 instead of £13. It is now
   `math.ceil`. The stated property (the DD covers the year, and is less than £1 a month over it)
   is pinned with `@example(actual=132.0)`.
   - The defect is reachable only when the annual figure is an exact multiple of £12, so its
     effect on published books is expected to be close to zero. That has not been measured on a
     book.
   - Random generation over pennies did not hit the case. Inspection found it, and the property
     now draws whole-pound multiples of twelve as well. A sparse defect class needs its boundary
     drawn on purpose.
2. **FIXED 20 Nov (see Resolution): an SME period with no length is billed at 5% but checked at 20%.**
   `dual_fuel_bill.vat_rate_for_supply("SME", fuel, kwh, days<=0)` falls to
   `VAT_RATE_BY_MARKET["SME"]`, which is 0.05. `domain_invariants.vat_rate_for_segment("SME")` is
   0.20, and `check_vat("SME", 0.05)` with no volume returns False, so the checker refuses what
   the biller charges.
   - It can be reached through `monthly_bill_assembly._vat_rate_of`, which uses
     `bill.get("days_in_period") or 0`. `generate_bill` always has days of 1 or more.
   - Which rate is right when the volume is unknown is a reading of 701/19: the de minimis is a
     relief that has to be shown. The recommendation is 20%, which `vat_rate_for_segment`
     already says.
3. **FIXED 20 Nov: the invoice fallback ignores the de minimis.** `invoice._vat_rate` charges an
   SME bill 20% at any volume. This applies only on the fallback path, which is a bill with no
   line items (`invoice.py` already states that narrowness).
4. **FIXED 20 Nov for calendar months: the biller has no date, so the dated domestic-electricity zero rate is not
   applied.** `vat_rate_for_segment("resi", fuel="electricity", on=2026-11-01)` is 0.0 (SI
   2026/987, 1 Oct 2026 to 31 Mar 2027), but `vat_rate_for_supply("resi", "electricity", ...)` is
   0.05. Every day of 2016-2025 agrees, so the property is scoped to that window. A forward year
   priced through the biller would be wrong.

## Which past defects these properties would have caught

Each "yes" was shown by putting a mutation of that defect's shape into the code and seeing the
named test fail. Eleven mutations were tried and all eleven failed. The ninth candidate, an unpinned
gzip mtime, is an equivalence on Python 3.14, because `gzip.compress` defaults to `mtime=0`. Its
real shape (`mtime=None`) is caught by a test that moves the clock between two writes.

| Past defect | Caught? | By |
|---|---|---|
| Opening DD set from the first (stub) bill, 2 Sep | yes | `test_the_first_review_starts_from_the_opening_amount_not_the_first_bill` |
| Gas tested against electricity's de minimis; SME charged 20% under the de minimis | yes | `test_every_vat_reading_of_one_period_agrees_with_the_notice` |
| Standing charge billed twice, 11 Jul | yes | `test_a_bill_is_its_lines_plus_vat_on_all_of_them_at_the_notices_rate` (standing charge = days x rate, and the lines sum to what was received) |
| Levies billed on top of all-in revenue, 10 Oct | yes | the same test (the subtotal equals what was received) |
| Double-posted ledger event moving the balance | yes | `test_one_balance_is_debits_less_credits_whatever_the_order_or_repeats` |
| Review depending on bill arrival order | yes (mutation) | `test_a_review_run_twice_or_on_reordered_bills_equals_one_run` |
| Bill shock measured as one percentage for two populations | **no** | This was a definition error. No invariant over the code catches a quantity nobody defined. |
| Half-month first DD as a *frame* (no such instrument exists) | **only after the practitioner's correction** | The property encodes his rule. It could not have produced that rule. |
| NaN amount passing reconcile | no (not generated) | The generator draws pennies. A non-finite amount is refused at `LedgerEvent.__post_init__` and has its own test. |

That is 6 of 9 by shape. The two definition and frame defects are the ones a property test cannot
reach, which matches the 16 Nov lifecycle result (10 of 34 exposed by a declared diagram).

## Next

Rows 2-4 are one `vat-one-reading-without-volume-and-forward-dates` item: make the biller take a
date, and have both readings agree when there is no volume. The properties above go red when that
is done wrong.

## Resolution of rows 2-4 (20 Nov, `vat-one-reading-without-volume-and-forward-dates`)

The K8 reading is `docs/market_research/back_billing_and_liability.md` s18.
- **Row 2.** A business period with no length is now standard-rated (`VAT_RATE_BY_MARKET["SME"]`),
  which matches the checker.
- **Row 3.** `invoice._vat_rate` now reads through `vat_rate_for_supply`.
- **Row 4.** `vat_rate_for_supply` takes `on=` (the period's first day), and `check_vat` accepts the
  same date.

Reading Brief 10 found two more things:
- **The zero rate also covers SME electricity under the de minimis.** Brief 10 zero-rates every
  supply that "would previously have qualified for the reduced rate", so the biller does this too.
  The predicted `vat_rate_for_segment` scope (resi only) was too narrow.
- **The zero rate now ends 30 June 2027, not 31 March.** Notice 701/19 (updated 28 Oct 2026) says
  so; the commons does not. The properties now draw dates to 31 Mar 2027 and leave Apr-Jun 2027
  undrawn, without pinning either answer. Correcting the commons and its four readers is
  `vat-zero-rate-extended-to-june-2027`.
