**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** home-moves -- `docs/market_research/home_moves.md` §8.8a ("the refund and the closing balance are the same figure")

# The page re-walks the close at its own commit, so an older run's refund log meets a newer credit (2026-11-11)

*Lane-0 item `the-close-refund-page-half-cannot-ship-without-its-run-half`. It explains the cross arm the close-refund
book's grade left unexplained
(`docs/staging/records/SEAT_PREREGISTRATION_THE_FIRST_BOOK_CARRYING_THE_CLOSE_REFUND_FIX_2026-11-11.md`, "Not
predicted").*

## What was seen

`INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO`, on the publisher's page chain:

| Arm | Page code | Run JSON | Breached |
|---|---|---|---:|
| control | a481c9ab96 | D1, e1587ec5b | 3 |
| cross | 6fe7827ab2 | D1, e1587ec5b | **23** |
| arm | 6fe7827ab2 | 6fe7827ab2 | 0 |

Readings are in `/var/tmp/crbook/{control,cross,arm}/`.

## Why: 23 of 23, to the penny

The page does not read the close's credit from the run. `tools/generate_billing_ledger.py` imports
`simulation.arrears_engine` (`resolved_settlement`, `with_credits_applied`) and walks each leg's bills again **at the
page's commit**. The refund comes from the run JSON's `credit_refund_log`, which was sized by the **run's** commit's
`balance_settlement_from_outcomes`.

cab13bbd1 changed that walk. A level collection now counts as cash of its own amount, so a credit drawn against a
level-paid bill is no longer counted twice (`level_paid`, home_moves.md s.8.8c B). That makes some leavers' closing
credit larger. The D1 run predates the change and refunds the old, smaller credit. On the new page the difference
stays on the account after the 10-working-day clock.

Every one of the 23 breaches has **page credit left = new walk's refund − old walk's refund**: 23 of 23, to the penny
(`/tmp/cross23.py`, run from the cross tree). Examples:

- `OCC-01e79fcf2d4f`: the old walk closed at nil and refunded nothing. The new walk nets a credit bill against the final
  bill, prints −11.50, and the new run refunds 11.50.
- `PROS-2016-0263g`: 250.91 refunded against 394.61 owed back, so 143.70 is left.
- `SYN-2016-221`: 605.10 against 932.19, so 327.09 is left. Its refund date also moved under s.8.8d.

**The control's 3 are a subset of the 23.** They are `PROS-2016-0263g`, `PROS-2017-0351` and `SYN-2016-493`, the
cases that were the defect cab13bbd1 fixed. So the cross arm is not a new defect in either half. It is the old run's
refund sizes read against the new walk's balances. The cross arm's refund row (201 against the control's 205) and
its 193 refunded legs closing in page debit are the same mismatch in the other direction: s.8.8c A now nets credit
against the final bill on the page, while the old refund still pays the whole credit.

**Corrected beside the record's claim.** The grade record says "the page change alone" moves the row. The tools
under `tools/` did not change between a481c9ab96 and 6fe7827ab2. What changed is the simulation walk that those
tools import. "Page half" and "run half" are one function, `balance_settlement_from_outcomes`, executed twice, at two
commits.

## What it means

- **Every publish is a cross arm whenever `simulation/arrears_engine.py` or `simulation/credit_refund_events.py`
  changes between the run's `producing_commit` and the publisher's HEAD.** The publisher builds pages at HEAD, and a
  book runs for hours. ccdfb652d7 changed `arrears_engine.py` at 17:30, after the 6fe7827ab2 book was offered and
  before its publish landed (the 17:02 commit was refused for a reason unrelated to this one). The next attempt is
  therefore a cross arm. The measurement below says whether this one is harmless.
- The domain gate catches the mismatch only on rows that have an invariant: the closed-account row and the
  refund-within-credit row. A walk change that moves a figure no row grades would publish silently disagreeing halves.
- The page's 129 `sim/` and `simulation/` imports (342-file static closure of `generate_billing_ledger` and
  `generate_payment_ledger_data`, from `background.code_closure`'s graph) are the general form of the same coupling.
  The money that crosses here is the close.

## The offered book through origin's page code

Prediction, filed before the output (`/var/tmp/crbook/headcross.prediction`): origin's pages (ccdfb652d7's walk)
over run 6fe7827ab2 give closed-account **0**, refund **0**, and the gate **permits**. The reason is that ccdfb652d7
moves only the date on which the page books a repayment (to its cash day, which is earlier). Amounts do not change;
its own grade moved `balance_gbp` on 0 of 1,302 accounts.

**RESULT: HELD.** Origin ccdfb652d7's pages over run 6fe7827ab2 (`/var/tmp/crbook/headcross/`): closed-account
**0** breached (87 flagged, unchanged from the arm), refund **0** of 176 lines, refunded legs closing in debit **0**,
refund GBP 21,380.64 (the arm's figure), gate **PERMITS True**, 7 excepted. The offered book can be republished
through today's page code. This time the coupling is harmless because ccdfb652d7 moves dates, not amounts. That is
luck, not a property, so the check below still stands.

## Recommendation (for the seat; reversible, not built here)

The smallest check that can fail: the publisher refuses, and names the reason, when
`git diff --quiet <run producing_commit> HEAD -- simulation/arrears_engine.py simulation/credit_refund_events.py`
is non-empty. The two files are listed by name rather than the whole 129-file closure, because the closure would
refuse almost every publish on a tree that commits every tick. The refusal names the files and both commits. The
remedy is a fresh run at HEAD, or pages built at the run's commit. The structural alternative is for the run to emit
the walk's per-leg closing balance and credit postings, and for the page to read them instead of re-walking. That is
the right end state (one figure, one home), but it is a W7 "separate the work" change and larger than one turn. This
check belongs in `background/process_run_complete.py`, a shared file under heavy concurrent edit, so it is offered
here rather than landed blind.

## Reverse

Delete this file. Nothing outside `docs/staging/` and `/var/tmp` was touched.
