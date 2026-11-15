**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# Does a closing statement that falls due on an open journey add its GBP to that case? (2026-11-15)

Follows `docs/staging/done/SEAT_FINDING_THE_ACCOUNT_WIDE_CLOSING_STATEMENT_OPENER_IS_UNEXERCISED_ON_THE_2016_RUN_2026-11-15.md`,
which left this open: five 2016 leavers (SYN-2016-206, -360, -012, -244, -070) were asked GBP 0.93 to
87.65 on their account statement's due date while a journey opened earlier was probably still open.
The desk skips an opener for an account it holds open, so only the open case can carry that debt.

## What "adds its GBP to the case" means

The case is the open journey. It carries a debt in two places, and both are tested:
1. **What it reads as owed.** The view the desk steps on (`_collections_view` -> `collections_snapshot`
   with `left_level`, aged by `age_left_level`) must count the statement's unpaid GBP as overdue from
   the day after its due date, and not before.
2. **What holds it open.** The case may not cure while the statement is unpaid
   (`_owes_a_bill_due_by(..., left_level)` reads `unpaid_asks`), and must cure once it is paid.

The journey record shows `overdue_gbp` only on the day a stage is entered, so (1) is read off the
view on the desk's step, not off the record.

## Pre-registration (written before the probe ran, reading the code at 7c89a8d351)

- P1: of the five, at least SYN-2016-360 (journey opened 6 Sep) is still open on 29 Dec 2016.
  SYN-2016-244 is not open on 3 Sep (it re-opened 19 Oct, so it had closed).
- P2: for every one of the five open on its statement's due+1, the desk steps on that day, and the
  view's `undisputed_overdue_gbp` there exceeds its value on the due date by the statement's unpaid
  GBP, less cash that landed on due+1.
- P3: none of them cures on a day the statement is still unpaid.

## Result (probe `/var/tmp/stmt-open-probe/probe.py`, the 2016 run at 7c89a8d351 to 2016-12-31)

The probe wraps the desk's `_step` for the five accounts. It records the view's
`undisputed_overdue_gbp` and the `unpaid_asks` of the `left_level` the desk itself built (with
`dunned_at`), and it records whether the case was open.

| account | statement due | open on due+1 | overdue on due -> due+1 (GBP) | on the statement, as the desk read it |
|---|---|---|---|---|
| SYN-2016-360 | 28 Dec | yes (opened 6 Sep) | 146.19 -> 146.19 | nothing: carved onto the 9 Aug request already dunned |
| SYN-2016-206 | 2 Aug | yes (opened 7 May) | 71.19 -> 71.19 | nothing: carved onto the missed request |
| SYN-2016-070 | 29 Sep | yes (opened 15 Jun) | 93.80 -> 93.80 | nothing: GBP 0.93 met by cash |
| SYN-2016-012 | 28 Jul | yes (opened 12 Mar) | 169.01 -> 179.58 | GBP 10.57 remainder, added on due+1 |
| SYN-2016-244 | 2 Sep | no (cured 19 Aug) | 0 -> 0 | nothing: paid by the 19 Aug cash |

- **P1 holds.** SYN-2016-360 is open on 29 Dec, and SYN-2016-244 is closed on 3 Sep.
- **P2 holds where it can be tested, but is mostly vacuous.** Only SYN-2016-012 had anything left on
  its statement once the desk had read it. The case added exactly that GBP 10.57 on due+1, and no
  cash landed that day.
- **P3 holds.** No case cured while its statement was unpaid.

**Correction to the earlier finding, beside its claim.** Its table, "asked that day GBP 0.93 to
87.65", was computed by calling `left_level_asks` without the desk's `dunned_at`. For an account
whose journey was open on the day it left, the desk keeps the unpaid shortfall owed from the request
it missed, where the case was already dunning it. The shortfall does not go on the statement
(`left_level_asks` docstring: "leaving does not cure a case being dunned"). So SYN-2016-360's
GBP 87.65 was never a new debt on 28 Dec: it was already overdue on the open case, dated 9 Aug. The
note is corrected in `docs/staging/done/`.

## What was done

`tests/company/billing/test_a_closing_statement_due_on_an_open_case_adds_its_debt_to_that_case.py`.
In the fixture, a returned collection opens a case on a household in debt. The household leaves
with the case open: the GBP 50 shortfall stays owed from its request, and GBP 60 goes on the
statement. The control pins:
1. One case, still open past the statement.
2. The view reads 50 on the due date and 110 the day after.
3. Paying the 50 alone after the due date leaves the case open with 60 overdue; paying 110 cures it
   that day.
4. The other side of the partition: paying 50 before the due date cures the case, and the unpaid
   statement opens its own case on due+1 at GBP 60.

Mutations, all of which red it:
- `_owes_a_bill_due_by` ignores `left_level`;
- `age_left_level` drops the statement's GBP from the past-due asks;
- the desk takes an opener for an account it already holds open.

company/ is unchanged.
