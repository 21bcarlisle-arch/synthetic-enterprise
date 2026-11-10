# The level direct debit area map: each state, the code on each side that decides it, and where the sides disagree (2026-11-10)

*Worker tick, 10 Nov 2026 ~22:00 GMT. Written because the stop condition in
`docs/staging/SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_SO_ITS_PAGE_PRINTS_OVERDUE_WHILE_IN_CREDIT_2026-11-07.md`
fired. Over 8 to 10 Nov, 34 of 80 graded level-DD predictions missed, and 18 of those missed because our model of our
own code was wrong (W1, `docs/institutional/ways_of_working.md`). No further level-DD fix is drawn until this page
exists. Once it exists, a level-DD prediction names the state it is about (section 4). Code read at origin c5732f9b95.*

## 1. What a level DD leg owes, said before any code

From `docs/market_research/payments_and_direct_debit_2026-10-25.md`, "What a level direct debit must be" and "What is
owed":
- **The schedule.** A level leg owes its scheduled collection. No single bill falls due by direct debit. The bill posts
  at its face, and the balance carries the difference.
- **A debt.** A level customer is in debt only by "defaulting on one or more payments" (Ofgem letter of 20 Sep 2011,
  App. 2 para 2.8). The debt is a missed instalment not made good, capped at the debit balance. A seasonal debit with
  every collection taken is not a debt.
- **Leaving.** The debit the scheme ran up is asked for once, on a closing statement due 28 days later
  (`CLOSING_STATEMENT_TERM_DAYS`; the range 14 to 28 days is GAP 1). A final bill states the closing balance itself.
- **Closed.** A closed account still unpaid is written off a year after its final bill (`debt_and_collections.md`
  s.7.3).

## 2. The sides, and which one decides

There are **five** places that hold an idea of what a level account owes, not four. The page does not work out the
cash itself. It reads the **world's own arrears engine**, and that is a fifth place, apart from the triad.

| Side | Module | What it decides |
|---|---|---|
| **W** World: schedule | `simulation/dd_level_collection_book.py` (`build_dd_level_collection_book`, `level_dd_collections`) | The amount and the Bacs day of every level collection. Sized from DD2's `collected_gbp`. |
| **T** World: what crossed | `background/live_payment_triad.py` (`LivePaymentTriad.record_period`) | Whether a collection was presented (`level`), what was asked (`ask_gbp`), its outcome, and its later settlement. It also decides whether a credit bill waits for the next bill (`_leg_credit`) and the walk bound (`_leg_level_floor`). It tells the desk `note_level_collection_request`. |
| **E** World: settlement walk | `simulation/arrears_engine.py` (`balance_settlement_from_outcomes`, `level_collection_difference`) | The cash the **page** posts against each bill, and the write-offs the P&L books. |
| **K** Desk | `company/billing/arrears_engine.py` (`LevelSchedule`, `on_level_dd`, `level_shortfall`, `level_leave_dates`, `leg_leave_dates`, `left_level_asks`, `unpaid_asks`); `company/billing/collections_journey.py` (`_walk`, `_step`, `_owes_a_bill_due_by`, `_write_off_if_closed`); `company/billing/payment_observation_consumer.py` (`level_schedule_of`, line ~2230) | Whether the account is on level, what it owes, when a journey opens and cures, and the write-off. Built only from what the company asked and what came back (ARUDD). |
| **P** Page | `tools/generate_billing_ledger.py` (the `level_dd` pop at ~1014 and ~1042, `desk_overdue_on` at ~498, `leaver_closing_statement` at 365); `tools/generate_payment_ledger_data.desk_write_off_postings` | What the household is shown: the level payment row (`level_dd: true`), a returned collection's case (the desk's figure), repayments, the closing statement, the write-off. |
| **R** Rows | `tools/domain_invariant_runner.py`: `INV_OVERDUE_WITHIN_BALANCE`, `INV_OVERDUE_WITHIN_PAGE_BALANCE`, `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE`, `INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE` | Whether the page and the desk are consistent. These rows read the page and the desk. They never read the world. |

**Which side decides each state.** The world (T) decides every state the *household* is in: whether money crossed, and
whether the leg is still collected by level DD. The desk (K) decides every state the *company* believes in: on level,
owed, cured, left, written off. The page (P) decides nothing. It prints T's cash through E's walk and K's figures. So
when P disagrees with K, the defect is in the reading P takes, or in E having a rule of its own. It is never "the page's
opinion".

## 3. The states, the code for each on each side, and the newest book

**Book:** `run_output_dca2ea1e7f_20261110T185708Z.json`, the newest graded book, at page ledger
`/var/tmp/grade-dca2/arm/ledger.json`. **Census:** `/var/tmp/lvlmap-trace/census.py` (per page leg, 743 of 1,302 legs
carry a level payment). Each count is legs, not accounts. A **DISAGREE** count is a candidate, read crudely. Its example
was checked by hand, and the rest were not.

| # | State | T world | K desk | P page | R rows | Legs on dca2 | Sides agree? |
|---|---|---|---|---|---|---:|---|
| S1 | **On level, collected** | `record_period`: `level` set when method is DD, a level row exists, and it is not a mover's final month. `ask_gbp` = level amount. | `on_level_dd`: the leg's latest bill that asked something is a level request. `level_shortfall` is None. | A `level_dd: true` payment at the level amount on `collection_date`. | `INV_PAYMENT_RECORD_*` reads it on time on its own day. | 743 | Yes. 0 breaches on the still-level steps. |
| S2 | **Instalment returned, account in credit or at 0** | The outcome draw is the collection's. A return is the level amount (`record_period`). | `level_shortfall` = `min(asked - received, balance)` ≤ 0, so no journey opens. | Outcome failed, `level_dd`, with **no case** (`desk_overdue_on` has no figure that day). | `INV_OVERDUE_WITHIN_PAGE_BALANCE` | within 204 | Yes on the rows. The 204 legs mix S2 with S3b (a return inside an already-open journey), and the census does not split them. |
| S3 | **Instalment returned, owed (missed)** | As S2. | A journey opens on `missed_payment` with the account's capped shortfall (`_step`). | A case at the desk's figure, less what the other leg's case already took (`taken_in_journey`), capped at the bill. | `INV_OVERDUE_WITHIN_BALANCE` | 139 | **No: D2.** |
| S3b | **Returned while a journey is already open** | As S2. | The journey's figure rises. No new opening. | No new case. "a journey already open carries the debt". | | (in the 204) | Not separated. |
| S4 | **Return made good (repaid)** | A settlement row for the level amount. `leg_rows` keeps the collection, so a repaid return repays that amount. This walk does **not** cap at the debit balance (the K4 gap named in the triad). | `PAYMENT_CREDIT` counts as received in `level_shortfall`. | `repayments` on the payment (no case) or `repaid_gbp` on the case. | | n/a | Not traced. |
| S5 | **Cured** | (none: the world keeps no journey) | `_step`: on a level account, only once `level_shortfall` is None. Off level, once `_owes_a_bill_due_by` is False. | Nothing is printed. A cure shows only as the journey's `cured` stage. | (the desk-cure ledger leg, sister finding) | 199 | **No: D3.** |
| S6 | **Credit bill in a level month** | The level collection is still presented, and the credit is **not** queued in `_leg_credit` (`level is None` guard). | The credit note is on the ledger and meets the oldest debt first. | A paid level row is posted when E's row has `collection_result` (fix 6fb708f3a, class L). | `INV_OVERDUE_WITHIN_PAGE_BALANCE` | n/a | Yes since class L. |
| S7 | **Leaving with a debit** | The leg leaves when `level` is None for a DD-collected month: DD stopped, mandate cancelled, meter changed, or no level row. The world has no "leaving" event. | `level_leave_dates`, `leg_leave_dates` (per leg) and `left_level_asks`: the scheme debit is due on the statement, 28 days after leaving. The journey opens only once that is missed. | `leaver_closing_statement`: needs **2 or more** paid bills after the last level one. The statement asks the page balance the day before, less open cases. | `INV_OVERDUE_WITHIN_BALANCE` (`_left_level_owed`) | 489 left; 34 with a page statement | **No: D1 and D5.** |
| S7c | **Credit bill after leaving with a debit** | `_leg_credit` lets the whole credit wait when no failed bill stands unsettled. It reads level months at the level amount, so the scheme debit is invisible to it. | `unpaid_asks` meets the credit against the earliest due, which is the statement. | E's walk nets the credit against the old debt first (SLC 27.16). | `INV_OVERDUE_WITHIN_PAGE_BALANCE` | 1 (SYN-2016-549g) | **No: D1.** |
| S8 | **Left in credit** | No refund modelled at leaving. A refund happens only at closing (E, `level_collection_difference`). | `left_level_asks` carries `carried_credit`. | `refunds` (228 legs carry one, of every kind). | | not split | Not traced. |
| S9 | **Leaving on the final bill only** | A mover's final month keeps the bill path (`final_month`), so `level` is None. | `on_level_dd` reads the final bill as leaving, and `left_level_asks` asks the scheme debit due 28 days later. **No final-bill carve.** | No statement: "a final bill states the closing balance itself". | | 436 | **No: D5** (when it is dunned, not measured). |
| S10 | **Closed, written off** | E: no more is written off than the one closing balance owes (s.8.8b choice 4). | `_write_off_if_closed`, a year after the last bill (`closed_account_write_off_date`). | `desk_write_offs` (`desk_write_off_postings`). | (written-off-printing-owed, not a gate row) | 183 | **No: D4.** |

## 4. Where the sides disagree: the next fixes, each named by its state

Each is a fix candidate. Under the stop condition, a fix is drawn from this list, and its prediction names the state.

- **D1 (S7c): a credit bill after leaving with a debit.** T lets it wait for the next bill, while E nets it against
  the scheme debit. On dca2 it is 22 page-balance steps, all on SYN-2016-549g (GBP 53.98). This is the gate's only
  unexcepted class. Owner: `a-credit-bill-meets-the-scheme-debit-before-the-next-bill`
  (`SEAT_FINDING_A_CREDIT_BILL_WAITS_FOR_THE_NEXT_BILL_IN_THE_WORLD_AND_MEETS_THE_SCHEME_DEBIT_ON_THE_PAGE_2026-11-10.md`).
  Read on this map: T and E hold **two rules for one credit**, and the fix puts one rule in one place.
- **D2 (S3, two-leg accounts): the desk opens on the account's figure, and the leg that returned has no page case.**
  On PROS-2017-0393g, the gas leg's level collections of 7 Nov and 7 Dec 2018 (GBP 24.34 and 25.30) are returned. The
  desk opens on 8 Dec 2018 at GBP 38.26. The gas page carries **no case**. The electricity leg's case (13638) opens on
  11 Dec at GBP 14.27. So the page prints 14.27 in cases where the desk says 38.26 is owed. 6 legs show this shape.
  **I cannot yet say** why the gas leg took no case. One candidate: `desk_overdue_on` is keyed on
  `billing_account_of(cid)` and that day, and the shortfall left after `taken_in_journey` or the cap at `asked` is 0. Not
  traced. Trace this first, with the page generator on this one account.
- **D3 (S5): the desk cures while a returned instalment is still owed on the page.** On PROS-2020-0191, the journey
  cures on 2 Oct 2023 at GBP 0. Case 17821 (GBP 39.10, returned on 2 Sep 2023) is never repaid, and it is written off
  on 1 Apr 2026. The page balance is GBP -177.44. 8 legs show this shape. This is the sister finding's class
  (`WORKER_FINDING_A_LEVEL_DD_JOURNEY_CURES_ON_THE_NEXT_INSTALMENT_WHILE_THE_MISSED_ONE_IS_NEVER_MADE_GOOD_2026-11-09.md`)
  surviving d8264b525e. **I cannot yet say** whether `level_shortfall`'s cap at the balance or the next instalment's
  cash meeting the old request is the cause.
- **D4 (S10): the desk wrote off, and the page still owes.** 32 legs on the census. The seat's account-level count is
  32 accounts and GBP 2,142.37. Owner: `desk-write-off-reaches-the-page`
  (`SEAT_FINDING_THE_DESKS_WRITE_OFF_OF_A_CLOSED_ACCOUNT_NEVER_REACHED_THE_PAGE_2026-11-10.md`). It grades on the head
  book 068b5e3cc8.
- **D5 (S7 and S9): two definitions of leaving.** The desk leaves on the **first** bill that asks something and is not
  level-paid, per account (`level_leave_dates`) and per leg (`leg_leave_dates`). The page leaves only when there are
  **2 or more** paid bills after the last level one, per page leg. The page also filters on the *payment amount*, and
  the desk on the *ask* (`nil_refs`). 436 legs leave on their final bill only. There the desk asks a scheme debit due
  28 days after leaving, while the page states it on the final bill, due 14 days after issue. Not yet measured: whether
  any journey opens on that ask. The definition question comes first. **Is a final bill a leaving at all?** The
  knowledge page says the final bill states the balance (home_moves.md, "Debt prevention at move-out"). If so, the
  desk's `level_leave_dates` should not read a final bill as a leaving.
- **D6 (S4): a repaid return is capped on one side only.** The desk caps what is owed at the debit balance. T's walk
  does not, so a household in credit can still "repay" a returned collection. The triad's own comment names this, and
  it is the K4 practitioner gap in "What is owed". It is not counted on any book.

## 5. What this map changes in how the area is worked

- A level-DD prediction names its state (S1 to S10) and the sides it expects to move. A prediction that moves a state
  this map says one side alone decides, and finds another side moved, is a model miss. It is counted for W1.
- A fix that touches a state names the code on **every** side in that state's row, and says why the others do not
  change. Most of the 18 model misses were a fix to one side whose twin on another side was not known. Examples: the
  gas-leg drop, the cure on the next instalment, and the credit bill read two ways.
- **Order, by evidence:** D1 holds the gate and has an owner, so it goes first. D2 and D3 are the next two to trace.
  Each is one account, through the page generator and through a desk replay. D5 is a definition, so it goes to the
  knowledge page first (K8). D6 waits on the practitioner (K4).
- **A commit that grades a level-DD table carries one trailer per table:**
  `Graded: level-dd held=<n> missed=<n> code=<n> reader=<n> regressed=<n> width=<x>`. `code` and `reader` are
  the misses caused by our model of our code or of the reader; a miss whose cause is undecided counts as `code`
  (F11). `width` is the median filed range width over its centre, an "at most N" row reading 2.0 and a point
  0. Without it the grade is invisible to the draw (`background/learning_loop.py`), and W1 cannot be graded.

## 6. What this map does not yet do

- S2 and S3b are not separated, and S4 and S8 are not traced on a household. The census reads page legs, so an
  account-level state (on level while another leg has left) shows on both legs.
- The DISAGREE counts come from a crude reader, written today and not mutation-checked. Each example was checked by
  hand, and the others were not. Treat each count as at most the true number until a second reader agrees.
- The map is of origin c5732f9b95. A landed fix that changes a state's code updates that row in the same commit.
