# Pre-registration: D48's direct-debit money line beside K3

**Filed 2026-10-06, before any measurement below was run.** Atom `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`; claim `d48-the-direct-debit-line-beside-k3`. To be measured over the bills in `docs/reports/run_output_latest.json`, re-building `simulation/dd_balance_book` with the review as built (`seek_balance_at_review=False`), its `opening_dd_by_customer` and `churned_billing_accounts`.

**What the line is.** For a direct-debit account, a charge recovery action is the final bill of an account that left (the review counts only under the toggle). The line is the money that action could not ask for because SLC 21BA bars it: the balance the action sought that pays for energy used more than 12 months earlier, once the debit's collections have paid the oldest charges first. It is in £, gross of VAT. It is not energy, so it is never added to K3. An open account's figure is an exposure, not a loss, and it is shown separately.

Predictions:
- **P1.** The barred total at final bills is between £14k and £17k. The last slice measured £15,447 on this file.
- **P2.** Between 20 and 60 of the DD accounts that met a final bill carry a bar. The 95% interval on that share is no narrower than ±8 percentage points, because the population is under 100.
- **P3.** The mean bar per account that met a final bill has a 95% interval whose half-width is more than 30% of the mean. A few under-sized debits through 2022 carry most of the money.
- **P4.** K3 (`by_fuel`) is byte-identical with and without the DD line supplied.

**Scored after measuring (same day).** 45 DD accounts met a final bill on this file, not the 87 named in the finding; that count came from an older run output.
- **P1 right:** £15,446.94.
- **P2 right:** 27 of 45 carry a bar, 60.0% (95% 45.5% to 73.0%), a half-width of about 14 points.
- **P3 right:** £343 per account (95% £165 to £521). The half-width is 52% of the mean.
- **P4 right:** `by_fuel` is identical with and without the line.
