**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# The desk's account-wide closing-statement opener opens no journey on the 2016 run (2026-11-15)

At 3c1bf2654, mutating `CLOSING_STATEMENT_TERM_DAYS` to 0 in the account-wide branch of
`CollectionsJourneyDesk.advance` (`level_leave_dates(...) + term`) changed no 2016 journey. A mutation
that does not fire is a missing test or an equivalence; this note establishes which.

## Pre-registration (written before the probe ran)

Reading the code: `leg_statement_asks` does not exclude the account's LAST level leg, so when an
account leaves whole, its last leg's statement falls on the same day (`left + 28`) as the account
statement whenever that leg's scheme debit is > 0. The account branch is then the SOLE opener only when
(a) the last leg leaves with no scheme debit but the account statement still asks something (an
un-dunned returned collection, `left_level_asks`' non-carved remainder), or (b) the account left and
came BACK to level DD (`level_leave_dates` keeps that leaving; `leg_leave_dates` drops it).

Predictions for the 2016 run (phase 4c, report_end 2016-12-31):
- P1: every account-statement date either coincides with a leg-statement date of the same account,
  or has nothing owed on it, so no opener is unique to the account branch that opens a journey.
- P2: no account leaves level DD and comes back in 2016.

## Result (probe `/var/tmp/acct-stmt-probe/probe.py`, the run at 3c1bf2654 to 2016-12-31)

Ten accounts left level DD in 2016, each once. **P2 holds**: none came back.

**P1 is refuted as worded.** Five accounts are asked something on their account-statement day with no
leg statement that day, so the account branch IS their only opener for that day:

| account | left | statement due | asked that day (GBP) | leg statement | journeys opened in 2016 |
|---|---|---|---|---|---|
| SYN-2016-206 | 5 Jul | 2 Aug | 64.81 | none | 7 May |
| SYN-2016-360 | 30 Nov | 28 Dec | 87.65 | none | 6 Sep |
| SYN-2016-012 | 30 Jun | 28 Jul | 46.05 | 1 Jul, 33.60 | 12 Mar |
| SYN-2016-244 | 5 Aug | 2 Sep | 2.78 | none | 29 Jun, 19 Oct |
| SYN-2016-070 | 1 Sep | 29 Sep | 0.93 | none | 15 Jun |

The other five owe nothing on that day (171, 024, PROS-0313), or a leg statement falls on the same day
(058, 005). The account branch is still equivalent on this book: none of the five opened a journey
on the day after the statement fell due, and every one had already opened a journey earlier in 2016.
The desk skips an opener for an account whose journey is open (`advance`: `account_id not in
self._open and on not in openers`), so the likely reading is that each statement fell on an open
case. **Not measured**: whether each of those journeys was still open on that day. SYN-2016-244 opening
again on 19 Oct, after its 2 Sep statement, says at least one had closed between the two openings.

## What was done

The branch is now covered by a unit control, since no 2016 account can reach it:
`tests/company/billing/test_a_leaver_owing_only_on_its_account_statement_is_dunned_from_that_statement.py`.
In the fixture, a single-leg household is square when its collection comes back, then leaves owing
GBP 40 that only the account statement asks. The control covers both sides: unpaid opens on due+1,
paid on the due date opens nothing. Mutating the desk's term to 0 reds it, because the GBP 40 is
then never dunned.

Open, not drawn: does a statement that falls on an open journey add its GBP to that case's
`overdue_gbp`? A longer run should say, by reading SYN-2016-360's journey across 28 Dec.
