**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** back-billing-and-liability

# C7 and 286 other runs over twelve months: none is billed past the 12-month bar, and nothing in the company asks for a read (2026-10-16)

*Worker tick, 2026-10-16, for the direction item `c7-fifty-months-unread-is-graded-against-the-read-duty-and-the-back-billing-bar`.
Run `run_output_2248e3baf_20261013T134447Z` (the published run), read in a fresh origin worktree. No
ledger was regenerated. This answers item 4 ("not checked") of
`WORKER_FINDING_D48_ELECTRICITYS_PRE_2020_UNDER_BILL_IS_ONE_UNREAD_EV_HOME_BILLED_ON_THE_TDCV_FALLBACK_2026-10-16.md`.*

**Knowledge first (K8).** The commons had no SLC 21B/21BA text, so the item's instruction to read it
there could not be followed as written. It now does: `docs/domain_artefact_library/regulatory/slc_21b_21ba_reads_and_back_billing.md`,
assembled from the [H] quotations already on the two knowledge pages. `docs/market_research/back_billing_and_liability.md`
§5 was stale (it still called the DD comparator wrong; that was fixed on 2026-10-06), and is corrected
in place. The census is summarised there in a new §13. The published topic note carried the same
stale sentence and is corrected too.

## Pre-registration

Seen before writing this down: the bill schema, the catch-up code path, and the fact that no
company code reads `consecutive_estimated_count`.

> Pre-registered 2026-10-16T14:34:58Z, before any census row was computed. Seen beforehand: the bill schema, the
> catch-up code path, and that no company code reads consecutive_estimated_count.
> 
> Population: every run of estimated bills longer than 12 bills, ended by an actual-read bill
> (read_true_up_periods > 12) or still open at the account's last bill.
> 
> - Q1. It is a class, not one account: at least 10 such runs across both fuels.
> - Q2. Every pay-on-bill undercharge catch-up over 12 months has back_billing_cap_applied true,
>   written_off_gbp > 0 and read_true_up_barred_kwh > 0. No pay-on-bill catch-up bills past the bar.
> - Q3. Every direct-debit run over 12 months is on the basis direct_debit_barred_at_the_charge_recovery_action,
>   writes nothing off on the catch-up bill and carries barred_kwh None.
> - Q4. C7's barred share of its catch-up kWh is between 0.70 and 0.80 (39 of 51 months, by days), if Q2 covers it.
> - Q5. No run carries any company read-attempt record. There is no mechanism to record one.

| | Result |
|---|---|
| Q1 | **Held.** There are 287 runs on 245 accounts. 262 last 13-23 months, 21 last 24-35, and 4 last 36 or more. 11 are never read by the run's end |
| Q2 | **Held.** All 21 pay-on-bill undercharge catch-ups read on or after 2018-05-01 have the cap applied and something written off. They carry 4,695 barred kWh and £472.21 written off. Charged past the bar: none (-£26.74 by my day count, which ends at the read date and not at the last period's end). None of the 27 runs read before the rule began was barred, as designed |
| Q3 | **Held.** All 182 direct-debit runs with a catch-up are on `direct_debit_barred_at_the_charge_recovery_action`. Each writes £0 off at the catch-up and carries barred kWh None |
| Q4 | **The route was refuted; the number held.** C7 pays by direct debit, so Q2 does not cover it. Its catch-up carries no barred kWh. The money bar at its final bill is £4,581.30 of £5,984.42, which is 76.6%. Its old share by days is 76.5% |
| Q5 | **Held.** No run carries a read-attempt record, because no mechanism makes one |

## How the census was taken

- **Population.** Per supply point and fuel, every run of more than 12 consecutive estimated bills.
  A run is either ended by an actual-read bill, or still open at the account's last bill.
- **Catch-up figures.** Read off the bill that ends the run:
  - `read_true_up_*` for energy;
  - `catchup_*` for money;
  - `catchup_back_billing_basis` for which comparator applied.
- **Old share.** The share of the run's days before the date 365 days ahead of the catch-up bill.
- **Direct-debit demand.** `simulation.dd_balance_book.build_dd_balance_book` rebuilt from the
  committed bills, `opening_dd_by_customer`, and every supply point whose last bill falls before the
  run's last month.
  - **It reproduces the published line exactly:** £33,769.60 barred at final bills, 153 accounts,
    and £50,296.79 open exposure.
  - The churn roster alone does not reproduce it. It gives £22,927.99, because the roster does not
    hold every supply point that stops billing.
  - The DD bar is per **account**: all of its unrecovered old charge, not only this run's. So it can
    exceed one run's catch-up, as for SYN-2016-471.

## What each payment route does with a long run (catch-ups read after 1 May 2018)

| Route, direction | Runs | Catch-up kWh | Catch-up £ | Written off at the catch-up £ | Where the bar is taken |
|---|---|---|---|---|---|
| Pay on bill, undercharge | 21 | 16,695 | 1,500.50 | 472.21 | At the catch-up: the bill is the demand |
| Pay on bill, overcharge | 38 | -24,128 | -2,608.14 | 0 | Never: a refund is not capped |
| Direct debit, undercharge | 91 | 125,955 | 20,052.32 | 0 | At the account's demand. 40 accounts are closed and barred £11,549.36 at their final bills. 51 are open with £15,890.14 of exposure and no demand yet |
| Direct debit, overcharge | 76 | -79,394 | -8,154.64 | 0 | Never |
| Immaterial (under £5) | 23 | 40 | 0 | 0 | Not billed |

Of the direct-debit undercharge catch-up money, £9,635.18 by days is for energy used more than 12
months before the catch-up statement. None of it was demanded at the statement.

## Every run of 24 months or more, and C7

| Account | Fuel | Months | Run start | Catch-up bill | Pays by | Catch-up kWh | Catch-up £ | Old share (days) | Written off at the catch-up £ | The account's demand |
|---|---|---|---|---|---|---|---|---|---|---|
| C7 | electricity | 50 | 2016-01-01 | 2020-03-31 | direct_debit | 41,778 | 5,984.42 | 76% | 0.00 | final bill, £4,581.30 barred |
| OCC-d8eede6baeb5 | electricity | 48 | 2016-06-14 | 2020-06-20 | standard_credit | 69 | — | 75% | — | — |
| SYN-2016-167 | gas | 47 | 2016-04-01 | 2020-03-30 | direct_debit | 2,645 | 86.46 | 75% | 0.00 | final bill, £56.40 barred |
| SYN-2016-471 | gas | 37 | 2018-02-01 | 2021-03-11 | direct_debit | 6,122 | 225.68 | 68% | 0.00 | final bill, £358.60 barred |
| OCC-49cf03d82fea | gas | 34 | 2022-03-01 | 2025-01-31 | direct_debit | 1,606 | 132.97 | 66% | 0.00 | none yet, £273.58 exposure |
| PROS-2016-0324 | electricity | 32 | 2016-10-27 | 2019-06-30 | prepayment | -155 | -22.35 | 63% | 0.00 | — |
| PROS-2018-0003 | electricity | 32 | 2018-01-03 | 2020-09-30 | direct_debit | 131 | 19.10 | 64% | 0.00 | none yet, £311.59 exposure |
| PROS-2020-0190g | gas | 32 | 2021-10-01 | 2024-06-30 | prepayment | -1,765 | -166.77 | 64% | 0.00 | — |
| SYN-2016-538 | electricity | 30 | 2018-06-01 | 2020-12-31 | direct_debit | 18 | — | 61% | — | none yet, £177.25 exposure |
| SYN-2016-168 | electricity | 29 | 2019-04-01 | 2021-09-30 | direct_debit | 39 | 6.30 | 60% | 0.00 | final bill, £281.13 barred |
| SYN-2016-010 | electricity | 28 | 2017-01-01 | 2019-05-31 | direct_debit | -4 | — | 59% | — | final bill, £35.39 barred |
| PROS-2020-0190 | electricity | 28 | 2022-02-01 | 2024-06-30 | prepayment | 170 | 27.56 | 59% | 16.70 | — |
| SYN-2016-110 | electricity | 27 | 2016-03-06 | 2018-06-30 | direct_debit | -25 | -5.81 | 57% | 0.00 | final bill, £86.68 barred |
| PROS-2017-0237 | electricity | 27 | 2019-12-01 | 2022-03-31 | direct_debit | 149 | 21.94 | 57% | 0.00 | final bill, £130.33 barred |
| PROS-2019-0310 | electricity | 27 | 2022-07-01 | 2024-10-11 | direct_debit | 160 | 27.24 | 56% | 0.00 | final bill, £215.28 barred |
| SYN-2016-187 | electricity | 26 | 2017-04-01 | 2019-06-30 | direct_debit | 35 | — | 55% | — | final bill, £543.98 barred |
| SYN-2016-085 | electricity | 25 | 2022-06-01 | 2024-07-31 | direct_debit | 9 | -28.05 | 54% | 0.00 | none yet, £163.21 exposure |
| PROS-2018-0176 | electricity | 25 | 2020-08-01 | 2022-09-30 | prepayment | -114 | -22.84 | 54% | 0.00 | — |
| SYN-2016-385 | gas | 24 | 2017-06-01 | 2019-06-30 | prepayment | -821 | -29.38 | 52% | 0.00 | — |
| SYN-2016-492 | electricity | 24 | 2016-10-31 | 2018-10-31 | direct_debit | 17 | — | 50% | — | final bill, £0.80 barred |
| PROS-2017-0233 | electricity | 24 | 2017-08-03 | 2019-08-31 | direct_debit | 6,161 | 897.47 | 52% | 0.00 | final bill, £931.37 barred |
| PROS-2018-0292 | electricity | 24 | 2021-06-01 | 2023-06-30 | direct_debit | 179 | 46.17 | 52% | 0.00 | none yet, £557.43 exposure |
| OCC-6b0458fec686 | gas | 24 | 2020-06-01 | 2022-06-30 | direct_debit | -1,200 | -42.18 | 52% | 0.00 | — |
| PROS-2019-0180 | electricity | 24 | 2020-02-01 | 2022-02-28 | direct_debit | 855 | 116.72 | 52% | 0.00 | final bill, £0.00 barred |
| PROS-2021-0217 | electricity | 24 | 2023-06-01 | 2025-06-07 | direct_debit | -55 | -12.84 | 50% | 0.00 | none yet, £385.79 exposure |

"—" in the money columns: there was no material catch-up, or no DD balance book (prepayment, standard
credit, or an OCC account with no opening DD).

## What this says

1. **No catch-up crosses the bar, and no fix is owed in `company/billing/`.**
   - The pay-on-bill route writes off the old part at the catch-up.
   - The direct-debit route puts the catch-up on a statement, which is not a demand (Ombudsman
     stance). It then bars the old part at the account's first demand, its final bill.
   - The existing control for the pay-on-bill side is
     `company/compliance/domain_invariants.check_back_billing_cap_respected`. For the direct-debit
     side it is `tests/simulation/test_dd_back_billing_at_charge_recovery_actions.py`.
   - So the "control that reds on a catch-up charging energy older than 12 months" exists for both
     routes, and no second one was written.
2. **C7 is the far end of a class of 287, not a one-off.** Only 4 runs reach 36 months.
   - C7's 41,778 kWh is a third of all 91 DD undercharge catch-ups (125,955 kWh).
   - So it is the class's outlier in size, not in kind. *(Corrected before landing: a draft said it
     was more than the other 90 together. It is not.)*
3. **Read duty (SLC 21B.4): the company makes no attempt.**
   - Nothing in `company/` reads `consecutive_estimated_count` or acts on a run of estimates.
   - A read arrives only when the world's two-class draw (`simulation/meter_reads.py`) sends one.
   - The licence cost of that falls on the supplier through 21BA, and the census shows it is paid.
   - The duty of effort itself is unmodelled. The sister page records why: the world has no
     read-access response, so a request has nothing to act on (`read_access_and_theft_duties.md`,
     "What this says about the order of work", item 3).
4. **The smallest company mechanism (built 2026-10-16; graded below).**
   - A 21B.4 register: one row per account each time a run of estimates reaches 12 months without
     a read. The company can see it from `consecutive_estimated_count`, and the trigger is the
     licence's own year, not a picked number.
   - It records the duty's breach. It changes no read, and needs no world change.
   - It would publish the count of accounts a year past their last read, which K2's snapshot only
     counts at one month.
   - The chase that should come before the year is a practitioner GAP: when in a run a supplier
     first asks, and by letter, call, visit or smart offer. It waits for the world's read-access
     mechanism, which is what would let a request change anything.
5. **K1 now carries its concentration.**
   - `estimated_billing_outstanding_grade` names the graded run with the largest true-up, its share
     of the net, and the net without it.
   - `published_view` grades K1 from the run's own bills at publish time, so the published run
     carries the figure now. The /capabilities/ table shows both columns.
   - On the published run:

| Year end | Electricity net | Largest run, share of net | Net without it |
|---|---|---|---|
| 2016-12 | +9.3% | C7, 106% | -0.5% |
| 2017-12 | +11.0% | C7, 85% | +1.7% |
| 2018-12 | +9.1% | C7, 112% | -1.2% |
| 2019-12 | +8.1% | C7, 129% | -2.5% |
| 2020-12 | -0.4% | PROS-2017-0336, -260% | -1.5% |
| 2021-12 | +1.8% | PROS-2017-0336, 140% | -0.8% |
| 2022-12 | +1.7% | PROS-2017-0336, 153% | -1.0% |
| 2023-12 | +2.7% | PROS-2017-0336, 71% | +0.8% |
| 2024-12 | +4.8% | PROS-2017-0336, 91% | +0.5% |

   **New, not chased here.** After C7, one account still sets electricity's net. PROS-2017-0336 is
   the account whose held estimates were the BLOCKING finding's subject
   (`WORKER_FINDING_NINE_CUSTOMER_YEARS_BILL_LESS_THAN_THEIR_GROSS_MARGIN_AT_ORIGIN_2026-10-14.md`).
   Without it, electricity's year-end net is within ±1.5% from 2020. Gas is less concentrated, but
   at 2016-12, 2017-12 and 2020-12 a single run is over 100% of a near-zero net in size (329%, -133% and -469%).

## By-products

- **Prepayment accounts on long runs of estimated bills.** There are 37 such runs (3 never read), with catch-ups
  graded pay-on-bill. 21B.4 and 21B.5 exclude prepayment, and a prepayment customer pays at the
  meter, so an estimated *bill* for one is a question in itself. Not traced.

## The 21B.4 register: prediction before it was run (item 4 built)

> Pre-registered 2026-10-16T17:35:34Z, before the register was run on the published run
> `run_output_2248e3baf_20261013T134447Z`. Seen beforehand: this finding's census (287 runs over
> 12 bills, on 245 accounts; 37 of them on prepayment) and the bill fields
> (`consecutive_estimated_count`, `payment_channel`). No count of runs of exactly 12 was taken.
>
> The register writes a row on the bill whose `consecutive_estimated_count` reaches 12: a year of
> monthly bills since the last actual read, or since supply began. A run of 12 estimates means the
> next read can come no sooner than 13 months after the last one, so it is past the licence's year.
> The census counted runs of MORE than 12 (`read_true_up_periods > 12`, or open at the end).
>
> - P1. Rows = 287 + the runs of exactly 12 estimates. So rows > 287, and I expect 300-345.
> - P2. Accounts with a row >= 245, and I expect 250-290.
> - P3. Every census run gets exactly one row, and no row falls on a run the census did not count
>   other than a run of exactly 12.
> - P4. Rows on prepayment, where 21B.4 does not apply, are >= 37 (the census's prepayment runs plus
>   any of exactly 12). They are kept but not counted as the duty's.

| | Result |
|---|---|
| P1 | **The identity held; the range was refuted.** Rows = 355 = 287 + 68 runs of exactly 12. I expected 13-58 runs of exactly 12 and there are 68, so 355 is above my 300-345 range. Runs of exactly 12 are the commonest length past the year, which the census's 262 runs of 13-23 months did not show because it started at 13 |
| P2 | **Held.** 285 accounts, inside 250-290 |
| P3 | **Held.** An independent walk of each account's bills, counting estimates in a row, finds 355 runs of 12 or more and agrees with `consecutive_estimated_count` on every estimated bill. Each run gets one row, at its 12th estimate |
| P4 | **Held.** 45 rows are on prepayment (32 electricity, 13 gas), above the census's 37, and are kept out of the duty's count |

**What is published.** Within the duty: 310 rows on 248 accounts (electricity 196 on 158, gas 114
on 90). The /capabilities/ page shows these beside K2's snapshot, which at 2025-06 finds 6 of 195
electricity and 7 of 113 gas accounts on supply with no read bill in their last 12. The snapshot
asks of one month. The register counts every year that passed over the run. The feed
(`site/data/billing_accuracy.json`) was regenerated from the published run by `published_view` and
changed by that key alone. No ledger was regenerated.

**What it is not.** It records the year. It does not make the effort the duty asks for, and no bill
or read changed. The chase before the year is the GAP on `read_access_and_theft_duties.md` §2.6.
Mechanism: `company/billing/read_duty_register.py`. Control:
`tests/company/billing/test_read_duty_register.py` (runs of 11, 12 and 13 through
`build_monthly_bills`; the trigger at 11 or 13, and `<` for `!=`, each red it).
