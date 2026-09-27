**Severity:** LATENT · **Lane:** A_strategy_governance · **Atom:** `value-arms-error-bar` · **Class:** `measurements_that_mirror`

# The balance-at-close write-off rule, run alone: the amount does not move, so the selection sign does not either

**2026-09-27.** The build of
`docs/staging/SEAT_DESIGN_THE_WRITE_OFF_RULE_RE_KEYED_TO_THE_BALANCE_AT_CLOSE_2026-09-27.md`, graded
against `SEAT_PREREG_THE_BALANCE_AT_CLOSE_WRITE_OFF_RULE_ONE_VARIABLE_RUN_2026-09-27.md`, which was
filed before the rule was written. It sits beside
`SEAT_RESULT_THE_SELECTION_SWITCH_IS_ONE_ACCOUNTS_CHURN_ROLL_AND_ITS_MONEY_IS_THE_WRITE_OFF_RULE_2026-09-27.md`.

## What is built

In `simulation/arrears_engine.py`, `balance_write_offs` is now the single source for which failed
bills are written off and when. `compute_emergent_bad_debt`, `compute_debt_recovery` and
`tools.generate_billing_ledger` all read it.

- A failed or disputed bill adds to the account's running balance.
- At close, the balance is written off, dated at the final bill's due date. That date is the C4
  convention, `WRITE_OFF_DATE_CONVENTION`.
- A live balance with no payment for six years is statute-barred. That is leg 4a, `STATUTE_BAR_YEARS`
  (s.5, s.29(5)). A payment restarts the clock.
- Leg 4b is `STAYER_ARREARS_PROVISION_RATE = None`. `BAD_DEBT_BASIS` says the line counts
  write-offs only.
- A statute-barred balance gets no DCA stage.
- C1, C2b and C3b stay None, so there is no re-presentation and no paydown.

Controls are in `tests/simulation/test_balance_at_close_write_off.py`:

- One fixture reaches all four fates, and the statute-bar leg is asserted reachable first.
- Mutations were run: with no clock restart, 2 tests go red; with the bar never firing, 2 go red;
  with the fold removed, 1 goes red.

## The one-variable run

Old rule (HEAD `a53326372`, loaded from `git show`) against the new rule, in one process, over
`docs/reports/run_output_latest.json`: 10,681 bills, 90 churned accounts, seed 42. Bills,
behaviour and churn set are identical between the two.

| | old rule | new rule |
|---|---|---|
| leaver write-off (book) | £19,135.30 | **£19,135.30** |
| accounts whose total differs | — | **0** |
| write-off £ dated in a LATER year | — | £15,077.50 (79%) |
| write-off £ dated in an EARLIER year | — | £0.00 |
| DCA / sale recovery | £3,311.68 | £2,855.75 (−13.8%) |
| statute bars fired | — | 0 |
| stayer cost booked | £0 | £0 |
| stayer failed £ still open at run end (the leg 4b gap) | (called "resolved") | **£37,109.27** |
| write-off £ in a year after the account's last billed year | £246.54 (5 cases) | £3,487.73 (51 cases) |

## Predictions graded, wrong ones kept

| | prediction | result |
|---|---|---|
| **D1** (design) | the leaver's write-off falls | **REFUTED.** Identical to the penny, account by account. |
| **D2** (design) | the stayer's cost is unchanged at zero | **HELD.** |
| **D3** (design) | the selection sign moves toward retention | **REFUTED by construction** (S5). |
| **S1** | leaver write-off identical for all 90 churned accounts | **CONFIRMED.** 0 accounts differ. |
| **S2** | nothing moves earlier; a positive share moves later | **CONFIRMED.** 79% moves later. |
| **S3** | recovery within 10% of the old rule | **FAILED.** −13.8%. `debt_archetype` is read at the write-off year. At close, recent-onset debt no longer reads OVERWHELMED (30% recovery): OVERWHELMED £ falls from £4,518.84 to £290.73, and NEUTRAL and AVOIDANT take it. I predicted the channel but under-sized it. |
| **S4** | 0 statute bars, stayer cost zero | **CONFIRMED.** |
| **S5** | `PROS-2016-0098`'s £6,766.59 write-off swing is unchanged in amount | **CONFIRMED by construction.** The account is a leaver in both fates, and a leaver's write-off is the sum of its failed bills under both rules (S1). Its recovery can move by at most the spread of recovery rates, 25.5% − 12% of the write-off, which is ±£913. That cannot turn a −£5,344 net positive, so the sign of the published selection figure does not move. |
| **S6** | a non-zero amount lands in a year with no record | **CONFIRMED, and larger than I guessed:** 14× the old rule's. `apply_emergent_bad_debt` and `apply_debt_recovery` dropped such a figure silently. Both now book it on the account's last record (`_row_for`). Without that, this rule would have cut booked bad debt by 18% through a fail-open. |

## What it means

**The design's lever is not the write-off's key; it is the cure.** A failed bill is written off at
close for the same amount it used to be written off for at due+90, because nothing in the world
reduces a balance:

- re-presentation (C2) waits on C1 and C2b;
- arrangement paydown (C3) waits on C3b;
- a later payment pays its own bill, and on a running account that does not touch the arrears.

The design said the build "can keep today's draw and treat a failed bill as a balance
contribution". It is right that this is the conservative reading. Its prediction assumed a cure
the same build does not have.

**What does move the selection figure is leg 4b.** The book's stayers hold £37,109.27 of failed
bills that the old rule, and the ledger still, call "cleared via payment plan". That is about twice
what all leavers write off. The selection figure differences a leaver's written-off history against
a stayer's zero. Until C6 (a provision rate by age × method) is sourced, the gap between the two is
set by what the world does not charge the stayer, not by what it charges the leaver.

## Found on the way, not fixed here

- **The ledger and the P&L do not agree on the real book, at HEAD as well.** The ledger reports
  £17,359.26 and the engine £19,135.30, with 7 keys disagreeing at HEAD and 6 after this change.
  The 203 bills held by the ledger's pre-bill validation gate are written off in the P&L but
  absent from the ledger. A credit bill (`PROS-2018-0002`, −£33.77) is "failed" in the engine and
  skipped by the ledger. The fixture test agrees only because its bills are not held.
- **The ledger's non-written-off case still renders `RESOLVED — Arrears cleared via payment plan`.**
  Under the balance rule that case is an open balance. Changing it moves the payment-ledger and
  invoice surfaces, and belongs with leg 4b.

## Not done

The old-rule baseline is now measured. `longjob-two-state-diff-rerun-20260927` finished at 20:41
(`/var/tmp/se-two-state-diff-rerun/account_diff.json`):

- `PROS-2016-0098` carries **−£5,349.74** of the −£5,344.10 state distance.
- That is 99.7% of gross movement, a Herfindahl of 0.994.
- No other account moves more than £3.10.

The same two-seed run under the new rule was not launched from this bounded turn. It needs a HEAD
extract that contains this commit, and it takes about 2.7h. It is handed on.

S5 settles the write-off leg by construction. The prediction for that run is that `PROS-2016-0098`'s
state move stays within ±£913 of −£5,349.74 (the recovery bound), and that the sign does not
change.

## Reproduce

    git show a53326372:simulation/arrears_engine.py > /tmp/arrears_engine_old.py
    python3 /tmp/wo_onevar.py   # scratch: imports both modules and prints every row of the table above
