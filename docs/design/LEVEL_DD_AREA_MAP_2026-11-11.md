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
| *Corrected 11 Nov (s.6): the row above is wrong about T.* | | The world crossed PROS-2016-0098's **whole £75.33** on 29 Nov (`world_payment_truth.repayments`); £0.22 is what the page put on the level row. On 6fe7827ab2 no hold's settlement was cut below its collection (0 of 56). The ledger that dated the cash wrong is **P**: the case's ARREARS_REPAID was dated when E's face walk met the cash with the bill (16 Dec), not the day it arrived. |
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

**Verdict (graded 11 Nov, 15:59 GMT): all five rows HELD.** The first launcher ended without launching (deadline
13:41); the re-armed one launched `6fe7827ab2` at 14:07, which carries the `money_in` wiring (`cab13bbd18` is an
ancestor, and `money_in` is in that commit's `run_phase4c_on_phase2b.py`). So this grades s.8.8d code the run calls.
Source: `/var/tmp/crbook/arm/cure_row.tsv`.

| Row | Control | Predicted | Read | Verdict |
|---|---:|---|---:|---|
| Cures held over a debt | 116 on 70 | 112 to 120 | **113 on 69** | HELD |
| Pre-registration row 11 (same reader) | 116 | 106 to 126 | **113** | HELD |
| …of which level at the cure | 93 | 89 to 97 | **90** | HELD |
| Holds on or after first refund or last invoice | 0 | 0 | **0** (every hold found its ledger leg) | HELD |
| Desk cures in total | 807 | 800 to 814 | **807** | HELD |

The map's row held, so there is no close-refund line to trace. The fix did reach the refunds: 176 refund lines on
176 legs (£21,380.64), and no refunded leg closes in page debit. The total of desk cures did not move. The held
count fell by 3 (one account), which is the treasury coupling's measured spread, and nothing on any line in section
1. This is one book. It does not establish that refund or close fixes "never" move the count; it fails to refute it.
The next level-DD fix that touches cures still has to name its shape from section 3 and its ledger.

## 5. What this changes

- **Before a level-DD prediction is filed, name the ledger it is read from (T, E, K or P) and the ledger the fix
  writes.** Every one of the 8 placed misses (and the ninth) was a fix written on one ledger and graded on another.
- **Grade on P through the publisher's chain only** (`/var/tmp/crbook-scripts/grade_one.sh`). Misses 6 and 7.
- **Any change to when cash crosses predicts a ±3-hold drift and a pennies-level rate drift on untouched legs**
  (the treasury line). Write that row into the table, or the row is a miss when it moves.
- *(Corrected 11 Nov, s.6: T cut none of them; the defect was P's dating, and is fixed there.)* **The next level-DD fix, by evidence:** the 19 part-repaid holds (T sizes the repayment on a walk P does not use)
  are the one shape with a single named line (`_cross_settlement` `:1096` reading `open_on_contract_gbp` without the
  level schedule). It is not drawn now. The 11 Nov ruling puts everything on the close-refund book first.
- The 10 Nov map's §5 trailer rule stands. This map adds no new trailer.

## 6. The "part-repaid" holds: T was not the cause, P's dating was (worker, 11 Nov 2026)

**Measured before any change, on the close-refund book 6fe7827ab2** (`/var/tmp/ldpr/census.py`, which reads the
world's own crossings, `per_customer_behavioral[*].world_payment_truth.repayments`, against `split.txt`'s holds).
Of 113 holds, 56 are on a day the world crossed a settlement of a returned level collection, and **every one of the
56 crossed the whole collection**. 0 were cut below it. So `_cross_settlement`'s `open_on_contract_gbp` cut
(`background/live_payment_triad.py:1096`) reaches no hold, and the fix s.5 drew (give T the level schedule) would
move nothing, or would start cutting cash that now crosses whole. It is not built.

**What happened on PROS-2016-0098.** The £75.33 collection was returned on 15 Nov 2018, and the household repaid it
whole on 29 Nov. The bill that collection paid for (INV 10033, face £89.15) falls due on 16 Dec. E opens a bill on
its due date, so it held the cash as waiting credit and met it with the bill on 16 Dec. `with_credits_applied`
dated the ARREARS_REPAID stage on that netting day. The account page posts that stage as `payment_received` on its
date. So on the 29 Nov cure day the page held only the £0.22 of `rest` (the same cash, posted on the right day), and
owed £29.29. K saw the cash on 29 Nov and was right to cure.

**The fix (P only).** `simulation/arrears_engine.with_credits_applied` dates a repayment on the day its cash
arrived (`credit_period_end`), never before the case opened, and orders the running "left owed" notes the same way.
Credit bills are not money in, so they keep the day they were netted. Control:
`tests/simulation/test_a_repayment_is_dated_the_day_its_cash_arrived.py`. The partition is asserted in one test:
cash dated on its day, cash before the case held at the opening, credit bill unmoved. Two mutations:
- the stage dated at the netting day again: red, on 2 tests;
- credit bills sorted by their period: did not fire at first. That was a **missing test**, not an equivalence: it
  reorders the notes when a credit and a repayment net on one day. The third test now covers it, and it fires.

**Graded on the 6fe7827ab2 book.** The page was regenerated in a copy of the arm's own tree with only this patch,
so the arm's grade is the one-variable control (`/var/tmp/ldpr/arm/`). Prediction filed before the run:
`/var/tmp/ldpr/PREDICTION.txt`.

| Row | Control | Predicted | Read | Verdict |
|---|---:|---|---:|---|
| P1 holds on a day a whole level collection crossed | 56 | 0 to 15 | **17** | **FELL** |
| P2 holds with no settlement that day | 55 | 52 to 58 | **52** | held |
| P3 cures held over a debt (`split.py` first line) | 113 on 69 | 55 to 75 | **71 on 38** | held |
| …level at the cure | 90 | (not predicted) | 48 | |
| P4 desk cures in total | 807 | 807 | **807** | held |
| P5 customers whose `balance_gbp` or `total_paid_gbp` moved | 0 | 0 | **0 of 1,302** | held |

**Why P1 fell, as far as it is known.** Most of the 17 fell partway: SYN-2016-525 went from 115.10 to 23.84, and
SYN-2016-037 from 61.93 to 13.47. There the crossed cash is now on the right day, and what is left is an older debt
the cash met first. SYN-2016-380 (102.00, unchanged) and SYN-2016-499 (25.27, a July collection settled in
November) are not traced. I cannot yet say which shape each of the 17 is in.

**Not changed.** The desk (K), the world's cash (T) and E's walk are untouched, so the run's figures do not move.
This is a page-and-reader fix. It moves the publisher's rows on the next regeneration of any book, and the chain
reads those rows.

*(Superseded by s.7: SYN-2016-380 is cause B. The page posts the £102 on 18 Apr, 17 days after it crossed.)*

## 7. The 71 holds left after ccdfb652d, each given one cause (worker, 11 Nov 2026, evening)

**Why this section exists.** The learning loop stopped level-DD at 25 held of 34, with 8 code-or-reader misses in
7 days. Three fixes in a row moved the cure row by less than their predictions. So no fix is built here. This
section maps the 71 holds first and names the next fix from the map.

**The book.** `87e00e1458` is the first book that carries ccdfb652d. Its `per_customer_behavioral` and
`level_dd_collections` are byte-identical (md5) to `6fe7827ab2`'s. The run's figures do not move, because ccdfb652d
is a page fix. So the 87e read is the 6fe arm read under the same page code. Readers:
`/var/tmp/ld71/classify.py` (one cause per hold, in priority order), `acct.py` (each leg's page balance past due,
and the account sum), `lag.py` (when the page posts a crossed repayment).

**Pre-registered at 22:24 GMT, before any cause reader had run on either book** (`/var/tmp/ld71/PREDICTION.txt`).
`split.txt` and `compose.txt` (the 71 rows and their level, left and never split) had already been read. Cash on
the day, returned collections, world crossings and the account sums had not.

| Row (classifier partition, first match wins) | Predicted | 6fe arm | 87e (publisher chain) | Verdict |
|---|---|---:|---:|---|
| R0: 87e reads exactly what 6fe did (71 on 38, 48 level, 807 cures, every row below) | equal | | **71 on 38, 48, 807; every cause line identical** | held |
| C1 level; a level instalment succeeded on the account that day | 10 to 25 | 19 | 19 | held |
| C2 level; the world crossed a repayment that day | 5 to 17 | 16 | 16 | held |
| C3 level; no cash on the page or in the world that day | 10 to 25 | **0** | **0** | **missed** (code: s.3's 37 "no cash" holds are all gone, and the cause is not traced, so F11) |
| C4 the owing leg is off level, and its sibling is on level | 10 to 20 | 13 | 13 | held |
| C5 every leg off level | 22 exactly | **23** | **23** | **missed** (reader: my classifier puts the never-level hold SYN-2016-015 here, and compose did not) |
| C6 a reader misread, not a debt the page holds | 0 to 10 | **35** | **35** | **missed** (reader, below) |

**The finding that reorders the area: 35 of the 71 are a reader misread.** `split.py` takes each level leg at
`max(0, …)` and then sums the legs. So one fuel's credit never offsets the other fuel's debt. On off-level legs it
does net them (SYN-2016-217 and SYN-2016-487 hold only their net). The desk works on the billing account
(`billing_account_of`). The 25 Oct design builds it that way: "the company's ledger is the billing account … one
account in arrears gets one reminder ladder and one statement of what is owed across both fuels". See
`docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`, rows "One
collections journey?" and "Collections" (SLC 27.8D set-off since 22 Jan 2021). On these 35 cure days, the sum of the
page legs' past-due balances is at most £0. On the account the desk works and the statement prints, nothing is
owed, so the desk was right to cure. The reader held two rules for one account.

**The 71, one cause each** (the account sums are in `/var/tmp/ld71/acct_6fe.txt`; every line is listed there):

| Cause | Holds | Accounts | Kind | Code path |
|---|---:|---:|---|---|
| **A. A sibling fuel's credit covers the debt.** The page account is at most £0 past due, and the reader keeps the debit leg. | **35** | 24 | **Reader** | `split.py` `leg_owed` clamps level legs per leg. The desk (`billing_account_of`) is right. 17 of the classifier's C1, 6 of C2 and 12 of C4. Examples: PROS-2018-0043 (gas +215.31, elec −308.90), and SYN-2016-334 ×9 (elec off level owes up to 562.96, gas level −588.38). |
| **B. The page posts a crossed repayment days late.** The world crossed it on the cure day, and the account is in debit. | **10** | 10 | **Code (P)** | The page carries the crossed amount as `payment_received` 3 to 19 days later (SYN-2016-380: £102 crossed 1 Apr 2019, posted 18 Apr; PROS-2019-0246: £330.42 crossed 1 Sep 2021, posted 20 Sep). Across all 17 crossings on C2 days, 12 post later, 1 posts the same day, and 4 never post as a single entry (`/var/tmp/ld71/lag`). This is the residue of s.6's P1, which read 17 where 0 to 15 was predicted. ccdfb652d dated the ARREARS_REPAID **stage**. The **payment row** for the same cash still carries its own later date. **I cannot yet say which line writes that date.** |
| **C. A failed bill's remainder that the page carries and the desk does not.** | **10** | 1 | **Code (K or P)** | PROS-2018-0016: invoice 13762 (£138.87, DD failed 22 Feb 2021) is £12.42 outstanding to run end. The desk opens and cures 10 journeys from 2022 to 2025 without it. One account, so one trace. |
| **D. An off-level leg where the desk's ask is below the page's past due.** | **14** | 6 | **Undecided, so code (F11)** | `unpaid_asks` (per bill, on K) against P's FIFO walk, as s.3's off-level row named. SYN-2016-206 ×7: the gas leg pays each bill about 6 weeks late. The desk opens at £16.94 when the page holds two bills past due. Also SYN-2016-015, SYN-2016-217 ×3, SYN-2016-487, SYN-2016-142 (2020) and PROS-2018-0016 (May 2020). Not traced to a line. |
| **E. The 10 Nov D3 proper.** The next instalment cures while the account is still in debit. | **2** | 2 | **Code (K)** | `level_shortfall` meets the oldest request with new cash, capped at the K balance. SYN-2016-488 (£20.16) and SYN-2016-536 (Oct 2019, £7.87 on the account). |
| **Total** | **71** | 38 | 35 reader, 36 code | |

**What this corrects.** s.3's three shapes and s.6's P1 read every hold as K against P. Half were the reader
against the design. The 10 Nov map's D3 ("8 legs") and s.3's "37 next-instalment" row were mostly cause A: the
instalment that "cured" was the **other** fuel's, and the account was in credit. D3 proper is 2. *Caveat, not
resolved:* 19 of the 35 cure before 22 Jan 2021, when SLC 27.8D gave the customer the set-off right. For those, the
netting rests on the design's choice and the supplier's terms, not the licence. The knowledge page already carries
this as GAP ("how often suppliers net unprompted").

**The next fix, named and not built.**
1. **The reader, not the area:** `split.py` reads the billing account, with one rule for level and off-level legs.
   Its prediction on this same book is exact: **71 → 36 on 18 accounts** (cause A leaves, and every other line is
   unchanged). It moves no code that the household or the run sees. After it, the filed 0 to 3 for the cure row is
   compared against 36. Every one of those 36 is a code defect or undecided.
2. **The first code fix, by count:** cause B (10 accounts). Trace one account first (SYN-2016-380): which writer
   dates the payment row of a repaid level collection, and against which ledger. The prediction names P alone.
   Then C (one account, 10 holds), D, then E.

Graded: level-dd held=4 missed=3 code=1 reader=2 regressed=0 width=0.86

NEXT: rebuild split.py to read the billing account, and grade it against 71 → 36 on the 87e00e1458 book.

## 8. The cure reader on the billing account, graded; cause B traced on SYN-2016-380 (seat, 12 Nov 2026)

**The reader is committed:** `tools/level_dd_cure_reader.py` (test:
`tests/tools/test_the_cure_reader_nets_the_billing_account.py`). It groups legs by
`billing_account_of` and applies one rule to every leg at the cure date. A leg contributes its signed
past-due balance. A leg on level DD contributes no more than its schedule shortfall,
`min(past_due, max(0, requested − received))`. The account owes the sum. `--legacy` reproduces the
scratch `split.py` (level legs clamped at zero per leg), so the two can be printed side by side.

**Graded on `87e00e1458`** (ledger rebuilt in an origin/main worktree at 39744630a1; `--legacy` reads
**71 on 38, 48 level, 807 cures**, exactly s.7's, so the page code has not moved under the grade):

| s.7's prediction | Predicted | Read | Verdict |
|---|---|---:|---|
| Holds on the billing account | 36 on 18 | **33 on 15** (10 level at cure) | **missed** (reader, below) |
| Cause A leaves | 35 → 0 | 0 | held |
| Cause B unchanged | 10 | **7** | **missed** (reader, below) |
| Cause C unchanged | 10 (PROS-2018-0016) | 10 | held |
| Cause D unchanged | 14 | 14 | held |
| Cause E unchanged | 2 (SYN-2016-488, -536) | 2 | held |

**Why 36 became 33.** The prediction was computed with `acct.py`. That script sums each leg's RAW
past-due balance, and it is not the rule `split.py` itself applied to a level leg (the schedule-shortfall
cap). The three that leave are all s.7 cause B: SYN-2016-094 (31 Oct 2022), SYN-2016-191 (3 Apr 2023)
and SYN-2016-404 (31 Jul 2017). On each, the level leg's debit balance is far above its shortfall:
£0.63, £18.59 and £12.30 against balances of £204, £455 and £50. The sibling's credit (£87.34, £100.98,
£49.92) covers that shortfall. So each is a cause-A hold that the prediction's arithmetic hid. The
committed reader is the consistent one. Under Ofgem's level-DD rule, a debit balance on a level plan is
not past due, and only the shortfall is. The miss is the prediction's, kept here beside it. Cause B is
now **7 holds on 7 accounts**: PROS-2019-0246, SYN-2016-031, -037, -253, -380, -525, -528.

**Cause B on SYN-2016-380, from code.** The world record (`world_payment_truth.repayments`): a
settlement of **£102 on 1 Apr 2019 for bill month 2019-03**. That is the March level collection (bill
42056), returned on 18 Mar 2019. The desk saw the cash and cured on 1 Apr. **s.7's reading is
corrected here:** the £102 `payment_received` on 18 Apr is NOT this cash posted late. It is the April
level instalment (bill 42057, collected on schedule). `lag.py` matched it on amount alone. The page
posts the 1 Apr cash on **19 Sep 2019, 171 days late, against a different bill**:

1. **Which bill: the engine's walk** (`simulation.arrears_engine.resolved_settlement`, called at
   `tools/generate_billing_ledger.py:448`). Bill 42056 had already been met by the 2017-10-31 credit
   bill (its case: `CREDIT_APPLIED`, £102 credit, `repaid_gbp` 0). So the walk held the 1 Apr cash as
   waiting credit and met the next failed bill with it: 42062, whose level collection was returned on
   18 Sep 2019.
2. **The page books it to that case:** `tools/generate_billing_ledger.py:1192-1196` counts the
   repayment against case `ARR-SYN-2016-380-2019-09-30` and marks `(SYN-2016-380, 2019-04-01)` as
   posted. So the catch-up loop at `:1249-1263` ("every household repayment reaches the page …
   once") finds nothing left and puts nothing on 42056's payment row.
3. **The line that dates it:** `simulation/arrears_engine.py:798`, in `with_credits_applied`:
   `"date": max(_on(c), opened)`. `_on(c)` is the cash's own day (2019-04-01, ccdfb652d's fix), but
   `opened` is the case's DD_FAILED day (2019-09-19). The `max` clamps the cash forward to the day
   the case it was matched to opened. The stage's own note still says "received 2019-04-01".
4. **The posting:** `tools/generate_payment_ledger_data.py:151-157` turns ARREARS_REPAID into a
   `payment_received` at the stage date, on the page's (P) ledger for that leg.

**The ledger it dates against** is P: the page's per-leg ledger, inside the case of a LATER bill. K
(the desk) counted the cash on its day. So on 1 Apr P still holds the March return as £102 short,
and the desk was right to cure. ccdfb652d dated the stage by the cash. It left the clamp to the
case's opening and the walk's choice of bill, and those are what carry this account's hold. Cause B
is therefore "P posts the cash against the bill the walk chose, from the day that bill's case
opened", not "the payment row is dated late". **Not built here.** Whether the other six cause-B holds
share this shape (an older credit met the returned bill, so the cash waited for a later one) is
unmeasured. The next item should count it on the 7 before choosing between a fix at `:798` and a fix
in the walk.

Graded: level-dd held=4 missed=3 code=0 reader=3 regressed=0 width=0

NEXT: count the 7 cause-B holds by shape (cash matched to a later bill's case vs. dated late on its own bill), then fix the shape that holds most.

## 9. How a repayment is dated and assigned (seat, 12 Nov 2026)

**Why this section exists.** Two learning-loop areas are on STOP: level-dd (s.7, s.8) and repayment-posting (the
shortfall read in `docs/staging/SEAT_FINDING_THE_DESKS_WRITE_OFF_OF_A_CLOSED_ACCOUNT_NEVER_REACHED_THE_PAGE_2026-11-10.md`,
804e627de). Each area's last read named a writer line. Here both lines are mapped as one area. Nothing is fixed.

**The two writer lines.**

- **N, `tools/generate_billing_ledger.py:1118`.** A level return that opens no case. Its repayment share goes on the
  returned payment's `repayments` row and is dated `c["date"]`, the day the walk netted the credit against a bill.
  The cash's own day is `c["credit_period_end"]`, and the loop already keys `repaid_posted` by that day.
- **W, `tools/generate_billing_ledger.py:1192-1196` with `simulation/arrears_engine.py:798`.** The walk
  (`resolved_settlement`) gives the cash to the case of a failed bill. The page books it to that case's
  ARREARS_REPAID stage and marks it posted. `with_credits_applied` then dates the stage `max(_on(c), opened)`, so
  cash that arrived before the case opened is moved forward to the opening day. The stage note keeps the true day
  ("received …"). `generate_payment_ledger_data.py:151-157` posts the stage as `payment_received` on its date.

**Books and readers.** Rows and settlements: the published ledger of the 6fe7827ab2 book (`/var/tmp/rsf6/ledger.json`,
as in 804e627de). Holds: the 87e00e1458 ledger that s.8 graded (`/var/tmp/ldcr/ledger.json`). Both read the same
world payment truth (s.7 R0). Every count below is identical on both ledgers (`/var/tmp/rda/check87e.txt`). Readers:
`/var/tmp/rda/shapes.py`, `ownbill.py` and `holds.py`. Each row is tagged by its **writer**, which is fixed by where
the row sits, not by its date. A `repayments` row on a failed level payment whose invoice has no case is written at
`:1118`. Any other `repayments` row comes from the catch-up loop at `:1249-1263`, which dates it on the cash day. An
ARREARS_REPAID stage is written at `:798`. A row is **off-day** when no cash crossed on its leg that day. A stage
counts as W when it is dated after the "received" day in its own note, and at its case's opening. A settlement is
**late** under the shortfall read's own rule (`own.py`): by the end of its cash day, the page has not posted all the
cash the leg has received. It is **inherited** when an older gap on the same leg is still open. A late settlement is
attributed to the writers of the rows that close its gap.

**Pre-registered before any reader in `/var/tmp/rda` ran** (`/var/tmp/rda/PREDICTION.txt`):

| Row | Predicted | Read | Verdict |
|---|---|---:|---|
| P1 the 7 cause-B holds (87e): N | 2 to 5 | **3** (+1 both) | held |
| P1 W (SYN-2016-380 is W) | 1 to 4 | **3** (+1 both) | held |
| P1 other | 0 to 1 | 0 | held |
| P2 the off-day `repayments` rows written at `:1118` | 140 to 145 | **146** (GBP 4,973.88), every one from `:1118`, none from the catch-up | **missed** (reader: the range copied 804e627de's 145, which counted rows "on a later bill's due day". One `:1118` row, GBP 10.80, is off-day but not on a due day) |
| P3 the 55 off-day stages are W | 45 to 55 | **55** (GBP 1,433.24) | held |
| P4 the 193 late settlements: N carries late cash | 110 to 150 | **121** (113 N only, 8 both) | held |
| P4 W carries late cash | 30 to 60 | **80** (70 W only, 8 both, 2 W plus a catch-up row) | **missed** |
| P4 neither line | 0 to 15 | **0** | held |
| P5 the 787 never-one-entry: a part on an N row | 100 to 140 | **92** of the 157 own-late (84 N only, 8 both) | **missed** |
| P5 a part on a W stage | 15 to 45 | **73** (64 W only, 8 both, 1 W plus catch-up) | **missed** |
| P5 all parts on the cash day (neither line) | 620 to 660 | **607** | **missed** |

**What the misses say.** P4 and P5 under-predicted W. I priced W by its 55 rows and its GBP 1,433. But one W stage
closes the gap of every partly posted settlement before it on the leg, so 55 stages close 80 late settlements. P5's
third row also left out two groups that are inside the 787 and that neither line explains: **11 inherit** an older
gap, and **12 are partly missing** at the seam (`world_payment_truth.repayment_rows`, the finding's kind 3). The
partition reconciles: 607 + 157 + 11 + 12 = 787. No row read was code that the map did not already name, and the
reader miss is P2's.

**Each count, attributed to one line:**

| Population | N (`:1118`) only | W (`:1192`/`:798`) only | Both | Unexplained |
|---|---:|---:|---:|---:|
| 201 off-day page rows (GBP 6,407.12) | 146 | 55 | | 0 |
| 7 cause-B holds | 3: SYN-2016-031, -253g, -525 | 3: SYN-2016-037, -380, -528 | 1: PROS-2019-0246 (74.83 W and 195.11 N, which sum to its 269.94) | 0 |
| 193 own-late settlements | 113 | 72 (2 of them also closed by a catch-up row) | 8 | 0 |
| 14 inherited-late | 6 | 6 | 2 | 0 |
| 787 never-one-entry | 84 of the 157 late | 65 of the 157 late | 8 | none. 607 are a harmless split, every part on the cash day. 11 inherit. 12 partly missing at the seam |

**The assignment is the deeper half.** `ownbill.py` sets each off-day row's cash beside the bill month its settlement
was for:
- **All 55 W stages** sit on a **later** bill's case. The walk met the returned bill with older credit, or capped
  that bill's case at the desk's shortfall. It then held the excess as waiting credit for the next failed bill.
- **110 of the 146 N rows** are on the **bill the cash settled**. The household repaid before that bill's netting
  day, so for these the defect is the date alone.
- **36 N rows** match cash for an earlier month, which is the walk's choice again. The match is on amount, so 36 is
  an upper bound.
- **All 7 cause-B holds** have this one shape. The cash day posts the returned bill's own case share. The **excess
  above that share** (6.21, 13.47, 26.92, 23.84, 1.06, 102.00, and 74.83 + 195.11) goes to a later bill. N or W then
  dates it at that bill's netting or opening day. So a date fix alone would put cash on its true day, but against a
  bill not yet issued.

**The fix each line needs (not built here):**
1. **`:1118`:** date the share `c["credit_period_end"]`, the key `repaid_posted` already uses. That covers the 110
   own-bill rows. For cash whose settled month is earlier than the receiving bill's, take the same route as fix 2.
   Prediction: off-day N rows 146 → 0 to 5. Holds SYN-2016-031, -253g and -525 leave. Own-late settlements
   193 → 70 to 85, which leaves W's share.
2. **`:1192-1196` / `:798`:** dropping the `max` alone would date a stage before its case opened, which the clamp
   exists to refuse. The coherent shape: a repayment whose cash predates the case it was walked to is **not** that
   case's money in. Leave it out of `repaid_posted`, so the catch-up at `:1249-1263` posts it once, on its cash day,
   against the month it settled (`settles_month`). Then record it at `:798` as CREDIT_APPLIED, the zero-amount note
   (`_NOTE_STAGES`), dated at the opening. Credit already on the account meets the new case; it is not new cash. The
   case's `arrears_gbp` does not move, because it already nets the credit. Prediction: off-day stages 55 → 0. Holds
   SYN-2016-037, -380 and -528 leave. With fix 1, PROS-2019-0246 leaves too, and cause B goes 7 → 0.
3. Build them **one at a time**, fix 1 first: it is the larger count and a one-variable change. Then fix 2. Then
   grade the cure row against s.8's 33. s.8 predicts 33 → 26, cause B gone.

**The blind row that grades both:** `INV_A_REPAYMENT_IS_ON_THE_PAGE_BY_ITS_OWN_DAY`. For each leg and each world
settlement dated on or before the book date, the page's cumulative repayment money-in by the end of that day is at
least the leg's cumulative world settlement cash, less settlements the seam drops (kind 3, a separate defect with its
own row). It is keyed to the property, not to either line. On the 6fe7827ab2 ledger it reads **193 own-late + 14
inherited** today. Its control is a synthetic leg whose excess is walked to a later case: the row must fire on the
current code and pass when the cash is posted on its day. A second leg checks that the row **can** pass: a level
return repaid on the cash day, through its own case, must read clean.

Graded: level-dd held=3 missed=0 code=0 reader=0 regressed=0 width=1.2
Graded: repayment-posting held=3 missed=5 code=0 reader=1 regressed=0 width=0.32

NEXT: date the `:1118` share by `credit_period_end` (fix 1), and grade it against off-day N 146 → 0 to 5 and own-late 193 → 70 to 85 on the 6fe7827ab2 ledger

### 9.1 Fix 1 built and graded (seat, 12 Nov 2026)

`tools/generate_billing_ledger.py:1120` (was `:1118`) now dates the no-case share `c["credit_period_end"]`, the
key `repaid_posted` already used. One variable; `:798` and the walk are untouched. Both ledgers were built at
0367c57375 from the 6fe7827ab2 run (`07111cd8b4:docs/reports/run_output_latest.json.gz`), baseline and fix, in
`/var/tmp/f1118`. The baseline reproduces s.9's every count, so the page code had not moved under the grade.
Pre-registered in `/var/tmp/f1118/PREDICTION.txt` before either ledger was built.

| Row | Predicted | Read | Verdict |
|---|---|---:|---|
| F1 off-day N rows | 146 → 0 to 5 | **0** | held |
| F1 off-day W stages | 55 → 55 | 55 | held |
| F2 own-late settlements | 193 → 70 to 85 | **84** (68 W only, 16 closed on another cash day) | held |
| F3 inherited-late | 14 → 6 to 8 | **6** (all W) | held |
| F4 `:1118` rows dated before their own returned payment | 0 to 36 | **58** (GBP in `f45.txt`) | **missed** (reader) |
| F5 balances moved at the book date | 0 to 3 | **0** (91 records change, dates only) | held |
| F6 cure holds (`level_dd_cure_reader`) | -031, -253g, -525 leave; -037, -380, -528 stay; PROS-2019-0246 to its W half | all as predicted: 33 → **29**, PROS-2019-0246 269.94 → 74.83 | held |

**Not predicted.** SYN-2016-488 also leaves the holds. Its gas leg's 2017-02-23 cash (20.47) had been netted against
a bill of April 2025 and was dated 2025-05-17, so the page showed it owed from 2019. On its cash day, it no longer is.

**The F4 miss.** All 58 rows are dated before the receiving bill was even **issued**: the walk netted older cash
against a later return, and the date fix exposes the assignment. s.9 priced this as "36 N rows, an upper bound" by
amount match. Both halves of that were the reader: 38 of the 58 were off-day on the baseline (above the "upper
bound"), and 20 were tagged on-day because the netting day happened to be another cash day on the leg. So the
off-day tag undercounts misdated rows wherever a leg settles often.

**What the page now shows for those 58.** "Payment received towards a returned collection" on the true cash day,
under the later bill's invoice number. Money in is now on its day, which is what F2, F3 and F6 measure, but the line
names a bill that does not yet exist. That is the assignment half, and it takes fix 2's route: cash whose day
predates the receiving bill stays out of `repaid_posted`, so the catch-up posts it against `settles_month`
(`docs/staging/SEAT_FINDING_A_LEVEL_RETURNS_REPAYMENT_NAMES_A_BILL_NOT_YET_ISSUED_2026-11-12.md`).

NEXT: fix 1b, the 58 rows that predate their receiving bill go through the catch-up against `settles_month`, graded 58 → 0 with F1 to F6 unmoved, then fix 2
