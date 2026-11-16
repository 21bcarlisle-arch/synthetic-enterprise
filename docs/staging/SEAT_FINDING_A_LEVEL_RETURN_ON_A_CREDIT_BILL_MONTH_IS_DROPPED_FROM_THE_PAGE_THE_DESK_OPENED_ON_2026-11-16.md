**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

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
