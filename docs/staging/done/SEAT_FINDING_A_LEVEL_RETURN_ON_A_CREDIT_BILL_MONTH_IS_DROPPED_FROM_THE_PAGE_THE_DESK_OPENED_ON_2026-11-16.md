**Severity:** RESOLVED (was LATENT) · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A level return on a credit-bill month is dropped from the page, though the desk opened on it (2026-11-16)

*LATENT: one household's statement on 8a300fa561 misplaces a return and its repayment. No gate row reads it, and
its size across the book is not yet counted.*

**Seen.** SYN-2016-215 is single-fuel and on level DD for 2016–2025 at £162.80 a month. Its ledger on 8a300fa561:

| date | what the page prints | what happened |
|---|---|---|
| 2020-06-15 | level DD £162.80, success, carrying `repayments: [2020-07-29, £162.80]` | collected |
| 2020-07-15 | **nothing** | the instalment was presented and returned (the desk's next-day opening, and the household's repayment of exactly £162.80, both say so) |
| 2020-07-16 | journey opened: "a bill is unpaid past its due date", £144.07, 1 day overdue | |
| 2020-07-29 | journey cured | household repaid £162.80 |

The July instalment's month bills as invoice 33407, a **credit bill** (−£56.33). The credit-bill branch of
`tools/generate_billing_ledger.py` (comment beginning "A level direct debit collects its amount whatever the
month's bill") appends a level collection row only when `collection_result == "success"`. Its premise for a return
is "nothing crossed and the bill owes nothing, so no case opens". On this account the desk *did* open a case on the
return, and the household *did* repay it. So the page prints neither the return nor a repayment under it. The
catch-up below it ("Every household repayment reaches the page at the cash that crossed") then hangs the £162.80 on
the latest earlier payment, June's successful one. A reader sees a successful collection that was "repaid".

**Two explanations, not yet ranked.**
1. *The page is wrong.* A level schedule is owed by the schedule, not by the month's bill, so a returned instalment
   leaves the account short even when that month's bill is a credit. The desk read it that way. The page should print
   the returned row, with no case if the desk has none, and with the repayment under it.
2. *The desk is wrong.* If the account was in credit on the day (a credit bill suggests it may have been), then
   £144.07 was not overdue, and opening a journey breached INV_NO_ARREARS_NOTICE_WHILE_THE_HOUSEHOLD_IS_IN_CREDIT's
   intent. That row did not fire, which leans toward (1).

**Next, the smallest run.** Count the legs on 8a300fa561 where a credit bill's month has no level row, a desk
journey opens within 3 days of that month's instalment date, and the leg's balance on the day before is owed rather
than in credit. Read SYN-2016-215's running balance on 2020-07-14 first, because that one figure ranks (1) against (2).
Two other legs carry a repayment on a *successful* level collection with their monthly cadence intact:
PROS-2019-0318 (2022-10-24, £65.11 repaid 2022-11-22) and SYN-2016-047 (2023-08-18, £106.30 repaid 2023-09-15).
They have no journey and no gap, so they are a different orphan-repayment shape, and they have not been read.
**Corrected below (seat executor, 16 Nov):** both *do* have a gap and a journey. They are this same class.

## Ranked and counted (seat executor, 16 Nov 2026, on `/var/tmp/grade-c915/ledger_8a30.json`)

**(1) wins: the page is wrong.** On SYN-2016-215 the balance before 15 Jul 2020 is **owed £144.07**. That is
successful payments plus repayments minus bills issued, and it equals the desk's opening figure to the penny. The
household was not in credit, so the desk's case was right and (2) is refuted. The credit bill that makes the
branch drop the row is invoice 33407, a **catch-up** (`catchup_applied`) **issued 3 Aug, 19 days after the
instalment date**. So the branch's premise "the bill owes nothing" reads a document that did not exist when the
instalment was returned.

**The class on 8a300fa561 (script `/var/tmp/grade-lrcb/count.py`).** The script takes every level-DD leg and every
credit bill whose month falls strictly inside the leg's level schedule:

| | legs |
|---|---|
| credit-bill months inside a level schedule | 206 |
| with a level row printed | 203 |
| **without one** | **3** (3 households) |
| … of which a desk journey opened 0–5 days after the instalment date | 3 |
| … balance owed the day before the instalment date | 3 |
| … the credit bill was a catch-up issued after the instalment date | 3 |

| leg | month | credit bill | issued | journey opened | owed before | repayment hung on |
|---|---|---|---|---|---|---|
| SYN-2016-215 | 2020-07 | 33407, −56.33 | 2020-08-03 | 2020-07-16, 144.07 | 144.07 | Jun 2020 row (162.80, 29 Jul) |
| PROS-2019-0318 | 2022-07 | 16445, −9.35 | 2022-08-01 | 2022-07-26, 65.11 | 191.24 | Oct 2022 row (65.11, 22 Nov; journey cured 22 Nov) |
| SYN-2016-047 | 2023-05 | 24040, −43.67 | 2023-06-01 | 2023-05-19, 170.30 | 303.84 | Aug 2023 row (106.30, 15 Sep) |

The control population: the book prints 496 returned level instalments (`outcome: failed`, `level_dd`) in months
whose bill is not a credit. So only the credit-bill branch drops a return. The defect is small (3 of 28,526 level
rows) and every instance mis-hangs a repayment on a successful collection. That makes the statement misread, so
it is still LATENT: no gate row reads it.

**What the fix is (not built here).** In the credit-bill branch of `tools/generate_billing_ledger.py`, a returned
level collection should print as a `failed` level row, exactly as the non-credit branch does. Its case and
repayment should come from the desk's figure through the existing `level_missed_on` path, so the catch-up stops
hanging the repayment on the prior success. Done means the three legs above print a July/July/May failed row
carrying its repayment, and no repayment on the book hangs on a successful level collection (on 8a300fa561 exactly these 3 do, and no others).

## Pre-registration for the fix (seat executor, 18 Nov 2026, written before the run)

The ledger is regenerated at HEAD 483d962552 from `docs/reports/run_output_8a300fa561_20261116T031305Z.json`, once
before the change and once after it, and `/var/tmp/grade-lrcb/count.py` is run on both. Predictions:
- Before: 3 of 206 credit-bill months are without their level row. These are the same three legs. (HEAD is 2 days on
  from 8a300fa561, so a different count would be a finding of its own, not a refutation.)
- After: 0 of 206. Each of the three legs prints a `failed` level row on its instalment day, carrying a case opened
  the next day for the desk's figure, capped at the instalment, and the household's repayment sits under that row.
- No repayment on the book hangs on a successful level collection whose month has a returned instalment, i.e. the
  three June/October/August rows lose their orphan repayment. Every other leg's payments are byte-identical.

## Result (seat executor, 18 Nov 2026): fixed, and every prediction held

On the 8a300fa561 run, regenerated at HEAD before and after (`/var/tmp/lrcb-fix/{before,after}.json`, diff by
`/var/tmp/lrcb-fix/diff.py`):

| | before | after |
|---|---|---|
| credit-bill months inside a level schedule without their level row | 3 of 206 | **0 of 206** |
| successful level rows carrying a repayment | 3 | **0** |
| page repayments, whole book | £92,473.33 | £92,473.33 |
| legs whose record changed | | 4 |
| any leg's `balance_gbp` | | unchanged |

Each of the three legs now prints its returned row on the instalment day. Each carries a case opened the next day
at the desk's figure, capped at the instalment, and closed `ARREARS_REPAID` by the household's own cash: SYN-2016-215
144.07 repaid 162.80 on 29 Jul 2020; PROS-2019-0318 65.11 repaid 22 Nov 2022; SYN-2016-047 106.30 (desk 170.30, capped)
repaid 15 Sep 2023. The fourth changed leg, OCC-0c74c80dee7e, is a credit-bill return at the end of its schedule, so the
count's strictly-inside window misses it. It now prints its returned 79.00 of 23 Jun 2025, and the desk had no figure,
so there is no case: the partition's other leg, live on the book.

**Corrected during the build.** The first cut matched the case's repayment by date: the leg's cash on or after the
return, up to the instalment. On SYN-2016-047 that took 43.29 of 16 Jun 2023, which the world files against the leg's
2021-07 return. The match now keys on the repayment's `settles_month`. All 1,446 truth repayments on the run carry
one, and each of the three names its own return month.

**Test:** `tests/tools/test_a_level_return_on_a_credit_bill_month_prints_as_returned.py`. It holds SYN-2016-215's shape
with a paid and an in-credit control. Its three fix legs go red with the code change reverted.

**Not touched, a sibling to check.** The scheme-credit month inside the non-credit branch (`outcome == "credit"`,
class L') also prints a returned collection as nothing. Its control test pins "returned prints no row". Whether the
desk opens on those is unmeasured.

**Unrelated reds seen in the run:** `test_reconciliation_identity_holds_across_full_live_book` and
`test_the_published_arrears_count_is_ofgems_and_never_exceeds_the_ledgers_overdue_accounts` fail identically with the
fix reverted. They read the committed live book, not this code.
