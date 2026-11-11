# The level direct debit area, function by function: what each one moves, which ledger it reads, and where the 8 misses sit (2026-11-11)

*Seat executor, 11 Nov 2026, Lane-0 item `the-level-dd-area-is-mapped-before-another-fix`. Read from the code at origin
318d97fb72, not from memory or from the 10 Nov map. The 10 Nov map (`LEVEL_DD_AREA_MAP.md`) is organised by the
household's state (S1 to S10). This one is organised by the function that moves the money, because every miss below
came from a function whose twin on another ledger nobody had listed. Use the two together: a fix names its S-number
there and its function rows here.*

## 0. The four ledgers, said before any function

A level-DD figure is only meaningful once you say which ledger it is read from. There are four, and **none of them is
derived from another at run time**:

| Ledger | Where it lives | Built from | Who reads it |
|---|---|---|---|
| **T** the world's per-leg contract rows | `LivePaymentTriad._leg_rows` (`background/live_payment_triad.py:1742-1757`, `:1102-1105`) | level months at the **collection amount**, other bills at face, credits, repayments | the world's own settlement sizing (`open_on_contract_gbp`) and the credit-wait rule (`_leg_owed_on`) |
| **E** the run's settlement walk | `simulation/arrears_engine.py:1141` `balance_settlement_from_outcomes` | resolved bills at **face**, plus `level_collection_difference` | the page's cash, closing balances, refunds, close write-offs, P&L bad debt |
| **K** the desk's ledger | `company/billing/*` via `PaymentObservationConsumer.ledger_book` | bill debits at face, credit notes, cash the company **observed** (ARUDD, settlements), plan instalments, desk write-offs | the desk's view, journeys, cures, desk write-off |
| **P** the page | `tools/generate_billing_ledger.py`, `tools/generate_payment_ledger_data.py` | E's cash and closing, the level schedule, K's journeys and figures | the publisher's gate rows and every grading reader (`split.py`, `compose.py`, `wo_owed.py`) |

**The one sentence this map exists for:** the desk decides a cure on **K**, the world sizes the household's repayment
on **T**, and the grader measures "owed at the cure" on **P**. Three ledgers, three walks, and no code that makes them
agree on a level leg. Every cure held over a debt is a day on which K reads nothing owed and P reads something owed
(section 3).

## 1. Every function that moves level-DD money, with the ledger it reads

`£` is the money the function moves or decides. "Reads" is the ledger its inputs come from.

### 1a. World: setting the schedule (`simulation/`)

| Function | file:line | Moves | Reads |
|---|---|---|---|
| `build_dd_level_collection_book` | `simulation/dd_level_collection_book.py:175` | **Sets** every level collection: `amount_gbp = DD2 collected_gbp`, on the staggered Bacs day (`level_collection_dates`, `:149`). Re-levels happen here only, as DD2's trajectory changes month to month. | DD2 balance book (world) |
| `level_dd_collections` | `simulation/dd_level_collection_book.py:211` | **Selects** who pays level (`pays_level`, the world's mandate draw). The one schedule the triad, E and P all read. | world draw |

### 1b. World: presenting, missing, repaying (`background/live_payment_triad.py`, the world's side of the seam)

| Function | file:line | Moves | Reads |
|---|---|---|---|
| `record_period`, level selection | `:1334-1335` | **Collects** the level amount when method is DD, a level row exists and it is **not** a mover's final month. A final month goes back to the bill path (the world's only "leaving" is `level is None`). | schedule (1a) |
| `record_period`, credit wait | `:1357-1361` | A level month takes the level amount whatever the bill (`waiting = 0`); `ask_gbp = level amount`. | T |
| `record_period`, credit bill waits | `:1474-1482` (D1, b47832f7e1) | Off level only: a credit bill waits for the next bill, net of `_leg_owed_on`. | T and K (`_leg_owed_on` reads the **desk's** ledger book, `:1219-1247`) |
| `record_period`, outcome draw | `payment_outcome` `simulation/arrears_engine.py:536` via the triad | **Misses**: a return is the level amount. | world stress |
| `record_period`, tells the desk | `:1555` | `note_level_collection_request`: the company learns it asked a level amount (its own act). | — |
| `record_period`, leg rows | `:1742-1757` | Writes **T**: a level month is a row **at the collection amount**, `method=None`. Named in the code: "the desk caps its figure at the debit balance, and this walk does not" (K4 gap, D6 in the 10 Nov map). | — |
| `record_period`, walk floor | `:1786-1790` | `_leg_level_floor`: the journey walk on a level leg is bounded at the month end (`_walk_bound`, `:1033`). | — |
| `_cross_settlement` | `:1066-1127` | **Repays** a returned collection: `cash = min(event.amount_gbp, open_on_contract_gbp(leg_rows, settled_on))`. The repayment is sized on **T**, cut to the balance T shows. | **T** |
| `open_on_contract_gbp` | `simulation/arrears_engine.py:1382` | Runs E's walk over T's rows **without** `level_dd_collections`, so a level month reads as a bill at its collection amount paid at that amount. | T |
| `close_account`, `write_off_closed_balances` | `:1139`, `:934` | Close: no more settlements after the final bill (`_after_final_bill`, `:1147`). | T / K |

### 1c. World: the run's walk, refund and close write-off (`simulation/`)

| Function | file:line | Moves | Reads |
|---|---|---|---|
| `level_collection_pairs` | `simulation/arrears_engine.py:1089` | Pairs each DD bill and each presented credit month with its level collection (class L / L′). | E rows + schedule |
| `level_collection_difference` | `:1120` | Per leg: Σ(bill face − level collection) over **paid** months, and the last collection date. | E |
| `balance_settlement_from_outcomes` | `:1141`; level repayment branch `:1313-1320`; closing `:1357-1366` | The page's cash per bill, the leaver's **closing** = outstanding − waiting credit + difference. | E |
| close write-off (s.8.8b choice 4) | `:1367-1378` | **Writes off** at a year after the final bill, at most `max(0, closing)` on a level leg. | E |
| `generate_credit_refund_log` | `simulation/credit_refund_events.py:48` | **Refunds** every leaver whose E closing is negative, clock from max(final bill, last collection). This is where s.8.8c/8.8d act. | E closing |

### 1d. Desk: on level, owed, opened, cured, left, written off (`company/`)

| Function | file:line | Moves / decides | Reads |
|---|---|---|---|
| `note_level_collection_request` | `company/billing/payment_observation_consumer.py:1264` | Records each level request `(date, £, ref)`. | own acts |
| `level_schedule_of` | `:1275` | Builds `LevelSchedule`: requests, `other_asks` (every non-level bill at what it asked, due +14 d), `nil_refs`. | K |
| `level_returns_of` | `:1292` | ARUDD return dates: the only days a level journey can open on a collection. | K |
| `_collections_view` | `:2228` | Chooses which ageing applies: level shortfall while `on_level_dd`, else `left_level_asks`. | K |
| `on_level_dd` | `company/billing/arrears_engine.py:268` | **Account** is on level if **any** leg's latest asking bill is level-paid. | K |
| `level_shortfall` | `:292-336` | **Owed** = `max(0, min(Σasked − Σreceived, ledger.balance))`, aged from the oldest request cash has not met. `received` is **every** PAYMENT_CREDIT on the account; the cap is the **whole account's** K balance. | K |
| `level_leave_dates` / `left_level_on` | `:351`, `:342` | **Leaves** on the first day no leg's latest asking bill is level-paid. A final bill is a leaving (D5). | K |
| `leg_leave_dates` / `leg_statement_asks` | `:404`, `:452` | Per leg: scheme debit = Σcharged − credited − asked over the level era; asked on a statement +28 d. | K |
| `left_level_asks` / `unpaid_asks` / `age_left_level` | `:504`, `:579`, `:595` | What a leaver owes and from when; a journey open on the day of leaving keeps the missed instalment's date. | K |
| `CollectionsJourneyDesk.advance` | `company/billing/collections_journey.py:479-568` | Opening days: returns (+1 d), unpaid non-level bills, statements (+28 d +1). | K |
| `_step`, open | `:578-584` | **Opens** when the view reads overdue and no plan holds it. | K view |
| `_step`, cure | `:592-603` | **Cures** when the view reads nothing overdue AND (on level: `level_shortfall is None`; off level: no bill/ask due by today is unpaid). | K |
| `_write_off_if_closed` | `:633-652` with `closed_balance_due_for_write_off` `arrears_engine.py:1343` | **Writes off** the K balance a year after the final bill. | K |
| `_write_off_if_barred` | `:654` | Statute-bar write-off. | K |

### 1e. Page and rows (`tools/`), which decide nothing but are what every grade reads

| Function | file:line | Moves | Reads |
|---|---|---|---|
| page level pairing | `tools/generate_billing_ledger.py:509-512`, `:1029-1075` | Prints `level_dd: true` payments at the collection amount; must pair the same months as `level_collection_pairs` (held by `test_the_walk_and_the_page_pair_the_same_level_collections.py`). | schedule + E |
| `desk_overdue_on` / `taken_in_journey` | `:519-525`, `:1091-1093` | A returned collection's case at the **desk's** figure. | K journeys |
| `leaver_closing_statement` | `:365` | Statement only with ≥2 paid bills after the last level one (D5). | P |
| refunds | `:1313-1319` | Posts E's refund log. | E |
| `desk_write_off_postings` | `tools/generate_payment_ledger_data.py:245` | Posts the desk's write-off on the page. | K |

## 2. The 8 graded misses, each placed

`git log --grep "Graded: level-dd"` returns two commits carrying three tables: c8382169ff (the dca2ea1e7f and
068b5e3cc8 grades, 5 code misses) and e58699ec9c (the D1 book, 3 reader misses). 34 predictions: 9 + 11 + 14.

| # | Book, row | Class | What actually moved | The map line that would have predicted it |
|---|---|---|---|---|
| 1 | dca2ea1e7f, written-off printing owed (30 → 32, regressed) | **code** | the page was credited (47fdeacd5e) while the stale refund stayed | The write-off is decided **twice**: K's `_write_off_if_closed` on the K balance, and E's close write-off at `max(0, closing)` (1c, `:1367-1378`), with the page printing E's balance less E's refund. A fix on P/E cannot move K's write-off figure, so "written off yet owed" moves the wrong way whenever E's balance rises. |
| 2 | dca2ea1e7f, cure holds on mixed accounts | **code** | the rebase assumed every mixed account moved | `on_level_dd` is **per account, any leg** (1d, `:268`); `level_shortfall` caps at the **account** balance. A per-leg change moves only accounts whose *last* level leg changed state. |
| 3 | 068b5e3cc8, written-off printing owed (27 → 29, regressed) | **code** | as 1 | as 1 |
| 4 | 068b5e3cc8, class L run half (left-level closed £3,748.17 → £4,110.76, regressed) | **code** | pairing a credit month moved E's `difference`, hence `closing`, hence the **refund** | `level_collection_pairs` → `level_collection_difference` → `closing` → `generate_credit_refund_log` (1c). Any pairing change is a refund change. The map makes the chain one line; the prediction treated class L as page-only. |
| 5 | 068b5e3cc8, cure holds on mixed accounts | **code** | as 2, filed again | as 2 |
| 6 | D1 book, row 4 (the gate) | **reader** | graded on the raw-export runner; the publisher's gate also reads the refund and closed-account rows | 1e: the gate reads rows built from E's refunds (`:1313`) and closing; a level-DD book is graded on **P through the publisher's chain**, never a scratch runner. |
| 7 | D1 book, row 14 | **reader** | as 6 | as 6 |
| 8 | D1 book, row 6 (549g's page payments) | **reader** | D1 moves the ask (`ask_gbp`, the credit wait), and the page prints E's cash, which is unchanged | 1b `:1474-1482` writes only T's credit wait and the desk's `asked`; P's payments come from E (1c). A T-only change cannot move P's payments. |

**A ninth miss the trailer did not count (corrected here, against the thesis, F11).** e58699ec9c's row 7 fell
(SYN-2016-380's renewal rates moved by 0.001p to 0.01p on 341 invoices) and was labelled "model", but the trailer
reads `code=0`. 1b69ca1270 later attributed it to D1 feeding back through the treasury, not run nondeterminism. That
is a model-of-code miss, so the D1 grade should read `code=1`, and the week is **9** code-or-reader misses in 34,
not 8. No row in sections 1a to 1e predicts it: **the map has no line for the treasury feedback**, and that is a
gap in the map, not in the code. Any change to when cash crosses moves the treasury, which moves renewal rates, which
moves the bill face by pennies on legs the change never touched. Section 4 sizes it from the books.

**W1, graded.** c8382169ff predicted "at most 2 model misses in the next 9 graded level-DD predictions … refuted if
3 or more of those 9 miss for code or reader". The D1 book graded 14, and 4 of them missed (3 reader, 1 code). **W1
is refuted.** The 10 Nov map did not stop reader misses because it mapped states, not the ledger each grader reads.

## 3. The cures held over a debt, explained from the map

**What is counted.** `split.py` (`/var/tmp/grade-dca2-scripts/split.py`) takes every desk journey that exits
`cured` (807 on the control) and asks the **page** what the account owed on the cure day: on a level leg
`max(0, min(page balance past due, requested − received on the page))`. 116 of 807 read more than £0.005 (control:
the D1 book e1587ec5b through a481c9ab96's publisher chain, `/var/tmp/crbook/control/split.txt`). **The 347 in
the drawn item is the 298149a1fc reading, four fixes old**; the pre-registration already corrected it beside the
claim. The series on the same reader is 347 → 193 → 116 (dca2) → 119 (068b5e3cc8) → 116 (D1).

**Why they exist, from section 1.** The cure is K (`_step` `:592-603`, `level_shortfall` capped at the K balance).
The hold is P. They disagree whenever the K balance or K cash on the cure day differs from P's. Three shapes on the
control, counted (`/var/tmp/crbook/control/tree`, read today):

| Shape on the cure day | Holds | Map lines |
|---|---:|---|
| Level, a level collection or payment succeeded that day | 37 | The next instalment's cash lands on K and meets the oldest request first (`level_shortfall`), and the cap at the K balance reads ≤ 0, while P still carries the returned month. The 10 Nov D3. |
| Level, no cash on the page that day | 37 | K moved without P: cash K observed that P never prints, or the K balance (bills at face, credit notes) is lower than P's balance (E's walk with `difference`). Unresolved which, per account. |
| Level, a return part-repaid that day | 19 | `_cross_settlement` sizes the repayment on **T** (`open_on_contract_gbp` over level rows at the collection amount). PROS-2016-0098: £75.33 returned on 15 Nov 2018, T sized the repayment at **£0.22**, K cured that day, P owed £29.29. T's walk and P's balance are two walks, and nothing ties them on a level leg (D6). |
| Off level (left), a payment that day | 21 | `left_level_asks`/`unpaid_asks` on K against `fifo` on P. |
| Off level, no cash | 2 | as above |

**Two facts the census gives that the prediction rests on.** Of the 116, **0** cure on or after any refund on the
account, and **0** on or after the account's last invoice. 26 of the 70 accounts have a refund at all, and every one
of their holds is earlier.

## 4. Pre-registration: the cure count on the next book, from this map alone

*Filed before the close-refund book has launched. At 12:10 GMT the launcher `longjob-launcher-crbook` is still
waiting, `/var/tmp/crbook/arm` does not exist, and `tests/simulation/test_a_level_leavers_final_bill_meets_its_credit_before_the_refund.py`
is not on origin.*

**The reasoning.** The close-refund fix (s.8.8c) and its wiring (s.8.8d) act in `generate_credit_refund_log` and the
E closing, which section 1c places **at close**: after the final bill. Section 3 says no hold sits on or after a
refund or a final bill. So the fix cannot reach a hold through any line in section 1. It can reach them only through
the line the map does **not** have, the treasury feedback (section 2, the ninth miss). Fewer refunds change when cash
leaves, which moves renewal rates by pennies, which moves bill faces, which moves K and P by pennies on legs that hold
a debt. The size of that coupling is measured: consecutive books whose fixes touched no cure line read 116, 119 and
116, a spread of 3.

| Row | Control (D1 book) | Predicted | Refuted if |
|---|---:|---|---|
| Cures held over a debt (`compose.py`, first line) | 116 on 70 accounts | **116, within 112 to 120** | outside 112 to 120 |
| …of which level at the cure (`split.py`) | 93 | **89 to 97** | outside |
| Holds dated on or after the account's first refund, or its last invoice | 0 | **0** | any |
| Desk cures in total (`split.py` "cured") | 807 | **800 to 814** | outside |

The same column applies whether or not item 1's wiring is in the book. This is narrower than the pre-registration's
row 11 (106 to 126). That row stays as filed. **If this row falls and row 11 holds, the map is wrong**: something
in the close-refund fix reaches a cure that section 1 says it cannot, and that is the next thing to trace. If the
count stays at 116, the map's claim is that **no fix in the refund or close lines will ever move it**. The holds are a
K-against-P (and T-against-P) disagreement during the life of the account, and the next level-DD fix that touches
cures must name which of the three shapes in section 3 it moves, and on which ledger.

**How it is graded (armed 11 Nov, 12:45 GMT; the book has not launched).** `/var/tmp/crbook-scripts/cure_row.py <grade
dir>` reads all four rows and row 11 from the publisher chain's own `split.txt`, `compose.txt` and ledger. It refuses
if compose and split disagree on the count. On the control it reads 116 on 70 / 93 / 0 / 807, all held. The refund leg
can fire: dating every refund to 2000 reads 37, so a 0 is a measurement. The unit `longjob-crbook-cure-row` waits for
`/var/tmp/crbook/arm/DONE` and writes `/var/tmp/crbook/arm/cure_row.tsv`. At 12:30 the fix was not on origin, and the
first launcher's 8 h deadline falls at 13:40 *(corrected 12:40: "about 13:02" was wrong; it started at 05:40)*. If
that launcher ends without launching, the unit re-arms it once. **Two arming defects, fixed at 12:40 before the unit
started.** (1) The unit gave the first launcher only 3,600 s, so a start before 12:40 would have re-armed a second
launcher beside a live first. It now waits 9 h and refuses to re-arm while the first is alive. (2) The launcher
checked only for the fix's test file, so the engine could launch the book before the 6-line `money_in` run
wiring, grading s.8.8d code the run never calls. The re-armed launcher also requires `money_in` in origin's
`run_phase4c_on_phase2b.py`. The first launcher still runs its old bytes, so if the engine reaches origin before
13:40 without the wiring, that book is unwired and its cure row reads nothing about s.8.8d. The verdict goes here,
beside this table, when the TSV exists.

## 5. What this changes

- **Before a level-DD prediction is filed, name the ledger it is read from (T, E, K or P) and the ledger the fix
  writes.** Every one of the 8 placed misses (and the ninth) was a fix written on one ledger and graded on another.
- **Grade on P through the publisher's chain only** (`/var/tmp/crbook-scripts/grade_one.sh`). Misses 6 and 7.
- **Any change to when cash crosses predicts a ±3-hold drift and a pennies-level rate drift on untouched legs**
  (the treasury line). Write that row into the table, or the row is a miss when it moves.
- **The next level-DD fix, by evidence:** the 19 part-repaid holds (T sizes the repayment on a walk P does not use)
  are the one shape with a single named line (`_cross_settlement` `:1096` reading `open_on_contract_gbp` without the
  level schedule). It is not drawn now. The 11 Nov ruling puts everything on the close-refund book first.
- The 10 Nov map's §5 trailer rule stands. This map adds no new trailer.
