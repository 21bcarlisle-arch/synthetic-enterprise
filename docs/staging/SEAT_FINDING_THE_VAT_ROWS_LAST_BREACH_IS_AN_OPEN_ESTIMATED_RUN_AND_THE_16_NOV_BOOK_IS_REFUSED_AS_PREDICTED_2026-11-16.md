**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The VAT row's last breach is an open estimated run, and the 16 Nov book is refused as predicted (2026-11-16)

*Delivery seat, claim `the-four-unexcepted-rows-on-the-16-nov-book`. Follows
`WORKER_FINDING_THE_REVENUE_ROW_READ_NO_BACK_BILLING_BAR_AND_ITS_LAST_BREACH_IS_AN_UNREAD_TAIL_2026-11-16.md`.*

## 1. The direction record's prediction, graded

Filed in `DIRECTION.yaml` before the grade: the 07:05 book on f7e17b1316 "is refused on at least
INV_OVERDUE_WITHIN_BALANCE and INV_OVERDUE_WITHIN_PAGE_BALANCE".

**Right.** process_run_complete refused it at 12:31Z and again at 13:15Z (`sim-runner-log.md`):
INV_OVERDUE_WITHIN_BALANCE 4, INV_OVERDUE_WITHIN_PAGE_BALANCE 7, INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE 1,
INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 5 (over the exception's max of 1). The seat reproduced the
same four counts at origin 2f23ad063 code on the shared tree's site data for that book
(`tools.domain_invariant_runner --ledger docs/state/billing_ledger.json --printed site/data/customers`).
The prediction was weak: the book carried none of the fixes, so it could only be right.

## 2. The VAT row's last breach: PROS-2025-0095g

**Cause, named.** The account opened 8 Apr 2025 and is still supplied at the record's end (no final
bill on its timeline). Its last actual read is May; its only later bill (1-7 Jun, the last week of the
record) is an estimate of £7.84 before VAT. The row bounded that open run's error by the run's own size
(U). The knowledge page (`unbilled_energy_and_revenue_assurance.md` §1, K2) says billed differs from
consumed "until the next actual read", either sign, with no magnitude. U-as-its-own-size is a bound
nobody established. The estimate missed by 178% of itself, and the gap is £0.79 beyond the bound.

**Fix, as a class.** A shortfall below the lower side on an account whose estimated run is still OPEN
(at least one bill after its last actual read, and no final bill closing it) is graded a **flag**, not a
breach: the record holds no read that could establish an error in either direction. A CLOSED account
keeps its breach, because its estimated final bill closed the run (§1, "An estimated final bill closes
its run"). The upper side is unchanged.

**Prediction, filed before the re-grade** (same book, same data, code changed only in this row):
INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE goes breached 1 -> 0 and flagged 0 -> 1, the flag being
PROS-2025-0095g. No other row's breached or flagged count moves.

**Result: as predicted.** INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE moves from 1 breached and 0 flagged
to 0 breached and 1 flagged. The flag is `PROS-2025-0095g gas R 151.39`, 141.25 against 142.04. Every
other row's (breached, flagged, checked) is identical. The test
`test_a_shortfall_in_an_open_estimated_run_flags_and_a_closed_one_still_breaches` covers the whole
partition in one control: open run gives a flag, a final bill gives a breach, an actual last read gives a
breach. Three mutations each turn it red: the branch removed, the final-bill check removed, and the
actual-read check removed.

**Not established.** Whether the June estimate itself is poor (12.3/day against May's actual 27.5/day).
That is `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS`'s question, and this record does not answer it.

## 3. What still refuses a book newer than 6fe7827ab2, and who owns it

Graded on f7e17b1316 at this commit's code:

| row | count | cause | owner | fixed on origin? |
|---|---|---|---|---|
| INV_OVERDUE_WITHIN_BALANCE | 4 | D5: the desk opens a journey on a scheme debit no bill asked for | `DD_seasonal_cashflow_physics` (focus item 2) | **no**: the build has not started |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 7 | D5, the same (SYN-2016-471 misdated) | `DD_seasonal_cashflow_physics` | **no** |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | 5 | 39 settled records beyond any weather cell | fc3129a86 | yes, but not in this book |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 0 (1 flag) | open estimated run (above) | this commit | yes |
| cast tariff row | 0 here | | 157e05c23 | yes |

So no book can publish until D5's build lands. A book built before then reproduces rows 4 and 7.
That is why the next book's launch condition (§4) names the D5 build as an unmet requirement and
does not leave it out.
