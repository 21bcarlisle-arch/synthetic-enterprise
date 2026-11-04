# The household page's bill tally no longer counts credit-settled bills as missed (N15, eighth cold read O4) (2026-11-04)

**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted` (fixed). Follows `SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_N15_AND_N16_SURVIVE_ON_THE_SIX_STAGE_HOUSEHOLD_PAGE_2026-11-04.md`.

- Measured on the exported `site/data/customers` book before the change: of bills the tally called missed, 159 were credit
  bills (asked nothing) and 175 were `SETTLED_BY_CREDIT`, beside 3,246 genuine late payers.
- Fix: `tools/generate_explore_cast._settled_without_payment`. A bill with no payment by its due date is not missed if it
  asked nothing, or credit (scheme credit posted on it by then, plus credit netted off it) covers it, unless a collection on
  it was returned. Test: `tests/tools/test_the_payment_record_counts_bills_not_ledger_rows.py` (one record holding both a
  settled and a missed bill).
- Not done: credit bills still sit in D ("bills paid") because `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE` counts
  every bill as due; excluding them needs that invariant changed too. Filed as open. The site JSON regenerates on the
  next feed run; SYN-2016-592's printed figure is not re-checked here.
- Blind row owed (`company_debt_management.md`): a bill counted missed has neither payment nor credit settling it in its
  window. The test is that row's one-leg form; no register written.

**Reverse.** Revert the commit.
