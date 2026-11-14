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
(`docs/staging/done/SEAT_FINDING_A_LEVEL_RETURNS_REPAYMENT_NAMES_A_BILL_NOT_YET_ISSUED_2026-11-12.md`).

### 9.2 Fix 1b built and graded (seat, 12 Nov 2026)

At the no-case branch, a repayment whose cash day (`credit_period_end`) is before the returned collection's
`payment_date` is neither appended nor added to `repaid_posted`. It still uses up `room`, so no other row's amount
moves. The catch-up then posts it once, on its cash day, under its `settles_month` bill. Baseline is s.9.1's fix
ledger (code = f5d1203024); the fix ledger is `/var/tmp/f1118/fix1b.json`, from the same run. Pre-registered in
`/var/tmp/f1118/PREDICTION_1b.txt` before the build; reader `f1b.py`.

**The cut is the return day, not the issue day as the finding worded it.** A level DD can be collected before
its month's bill is issued (28 no-case rows did so even before fix 1, with 0 before their return). An issue-date
cut would also move those legitimate rows. All 58 predate both dates, so the two cuts agree on the defect.

| Row | Predicted | Read | Verdict |
|---|---|---:|---|
| P1 no-case rows dated before their return | 58 → 0 | **0** | held |
| P2 rows on no-case payments | 464 → 406 | **431** | **missed** (reader): 25 moved rows land on a `settles_month` bill that is itself a no-case return, dated after it |
| P3 all repayment rows | 548 → 490 to 548 | **527** (37 new catch-up rows, 21 merged into same-day rows) | held |
| P4 repayment GBP, customers whose total moved | 17,554.69, 0 | 17,554.69, **0** | held |
| P5 balances moved | 0 | **0** (40 records change) | held |
| P6 any page repayment dated before its own payment | 58 → 0 to 5 | **0** | held |
| P7 off-day W 55, late 113, own-late 84, inherit 6, never posted 23 | unchanged | all unchanged | held |

**Not predicted.** Settlements "on time in parts" fall 696 → 691, and never-one-entry 797 → 792: the 21 merges
make five settlements print as one entry. The cure reader is byte-identical to s.9.1 (29 holds on 11 accounts).

Test: `tests/tools/test_cash_before_a_level_return_is_not_its_repayment.py`. Both mutations kill it: refuse-nothing,
and refuse-everything. The later cash's `settles_month` names a different month on purpose, because where it
names the returned bill's own month, the catch-up files it under the same bill and refuse-all is an equivalence.

NEXT: fix 2 (`:1192-1196` / `arrears_engine.py:798`), the 55 W stages dated after their cash day

### 9.3 Fix 2 built and graded (seat, 12 Nov 2026)

A repayment whose cash day is before its case's opening (`stages[0].date`) is no longer that case's money in.
`with_credits_applied` notes it as a zero-money CREDIT_APPLIED at the opening ("the household's payment of …"),
and the case branch of `generate_billing_ledger` leaves it out of `repaid_posted` and `repaid_gbp`. So the
catch-up posts it once, on its cash day, under its `settles_month` bill, and the case's `credit_applied_gbp`
takes it. `arrears_gbp` is untouched. Baseline is s.9.2's ledger (`/var/tmp/f1118/fix1b.json`, code 18148e6b6);
the fix ledger is `/var/tmp/f2w/fix2.json` from the same run. Pre-registered in `/var/tmp/f2w/PREDICTION.txt`
before the code was written; readers `q.py`, `rda/shapes.py`, `level_dd_cure_reader`.

| Row | Predicted | Read | Verdict |
|---|---|---:|---|
| Q1 ARREARS_REPAID dated after its own cash day | 55 → 0 | **60 → 0** | held (reader: 55 counted only off-day stages; 5 more sat on a day other cash crossed) |
| Q2 CREDIT_APPLIED notes naming a household payment | 0 → 55 | **60** | held on the same reading |
| Q3 page money-in GBP; legs moved | unchanged; 0 to 3 | 94,633.76 unchanged; **0** | held |
| Q4 balances, `arrears_gbp` moved | 0, 0 | **0, 0** (40 records change) | held |
| Q5 off-day W; own-late; inherit | 55 → 0; 84 → 12 to 20; 6 → 0 to 2 | **0; 16; 0** | held |
| Q6 cure holds | 29 → 25 | **29 → 5 on 3 accounts** | **missed** |
| Q7 status moves | paid_late → settled_by_credit 1 to 55, other 0 | **11**, other 0 | held |

**The Q6 miss is this shape, under-counted.** Cause B's four left as predicted (SYN-2016-037, -380, -528,
PROS-2019-0246). So did **cause C** (PROS-2018-0016, all 11 holds), **cause D** (SYN-2016-206's 7), **cause E**
(SYN-2016-536), and SYN-2016-487. Each of those was the same defect on a leg s.9 did not count. PROS-2018-0016's
GBP 85.88 of 17 May 2020 was posted on 22 Oct, the opening of the September bill's case, and the hold sat on
17 May. SYN-2016-206's GBP 63.49 of 15 Mar 2021 was posted on 16 Jan 2024. s.9's census tagged W by "off-day",
and s.7/s.8 had given these accounts other causes from their symptoms, so they were never traced to `:798`. The
prediction trusted those cause labels. **Left: 5 holds on 3 accounts**: SYN-2016-015g (71.37, 15 Apr 2018),
SYN-2016-142g (47.11 → 44.52, 30 Apr 2020), SYN-2016-217 (3). None of them changed shape under this fix, so their
cause is untraced.

**Not predicted.** Late settlements under the cumulative rule fall 113 → 39, and "on time in parts" rises
696 → 751. The 16 own-late that remain are all closed by an on-day case stage or catch-up row on ANOTHER cash
day: one leg settling twice, where the walk gave one day's cash to the other. That is the walk's assignment
problem, not a dating problem.
*(Corrected 12 Nov, s.9.7: it was not the walk. All 16 were on SYN-2016-217g (11) and -256g (5), the two
credit-month legs whose settlement the seam dropped. The reader counted the dropped cash in the world's running
total, so every later settlement on those legs read late. When s.9.5 let that cash through, they fell 16 → 0.)*

`tests/simulation/test_a_collections_journey_opens_on_the_bill_the_ledger_made_due.py` fails on clean HEAD
(3 stray journey openings in 2016), with or without this fix.

Test: `tests/tools/test_cash_before_a_case_opened_is_credit_not_its_repayment.py`. All three mutations kill it:
refuse-nothing, refuse-everything at the ledger, and the ledger half alone (the engine still clamping).

Graded: level-dd held=6 missed=1 code=0 reader=1 regressed=0 width=1.0

NEXT: trace the 5 holds left (SYN-2016-015g, -142g, -217) from code, one cause each

### 9.4 The 5 holds left after fix 2, one cause each (seat, 12 Nov 2026)

Ledger rebuilt at 50b8feea61 from the 6fe7827ab2 run (`/var/tmp/t5h/fix2.json`); it reproduces s.9.3's 5 holds on 3
accounts byte for byte. Pre-registered in `/var/tmp/t5h/PREDICTION.txt` before any hold was traced. The desk's own
figure at each stage is on the journey record (`overdue_gbp`), so the desk and the page can be set side by side
without rerunning the world.

| Hold | Cause | Who is right | Line |
|---|---|---|---|
| SYN-2016-015g, 15 Apr 2018, 71.37 | **reader.** Gas bill 22482 due Sat 14 Apr, its DD collected, on time, Mon 16 Apr. The desk's view reads it on time (`overdue_gbp` 0, `days_overdue` -1) through `last_day_to_pay`'s Bacs-day roll. The reader read the due date alone. No failure on the leg at all. | the desk | `tools/level_dd_cure_reader.leg_position` (fixed here) |
| SYN-2016-142g, 30 Apr 2020, 44.52 | **the page's walk spends a credit the world did not.** The gas leg left level DD about GBP 127 in credit (level 50.17 against bills of 17 to 24). The engine's walk draws that surplus as kind `credit` (`credit_period_end` 2019-08-19) against the next three **paid** pay-on-receipt bills: 50.63, 61.28 and 8.58, GBP 120.49. The page prints them `settled_by_credit` with 0, 0 and 71.56 cash. The world asked and collected each bill's full face (`background/live_payment_triad.record_period`: `_leg_credit` holds credit-bill notes only, never a level surplus), on the page's own dates. The desk counted that cash, so on 30 Apr its account is in credit and bill 29866 (47.11, due 19 Apr, paid 13 Jun) is covered. On the page's figures the schedule reads short 45.00. | the desk, on the cash that crossed | the walk's draw of waiting credit against a paid bill, `simulation/arrears_engine.balance_settlement_from_outcomes` (the hypothesis the shortfall finding left "seen and not built", now traced on the book) |
| SYN-2016-217 x3, 17 Feb, 2 Jul, 26 Jul 2024 | **kind 3 at the seam.** The world settled GBP 22.00 on 15 May 2022 for gas month 2022-03, a -6.68 credit bill whose level collection was returned (`collection_result: failed`). `simulation/world_payment_truth.repayment_rows` counts a month as issued only if its row is failed, dispute or success; this row's outcome is `credit`, so the cash is dropped and never reaches the engine or the page. The desk counted it. The desk's account then sits exactly GBP 22.00 below the page's from 2022 on: 18.00 against 40.00 on 22 Jun 2024, 36.63 against 58.63 on 17 Jul. On 17 Feb the page's 12.12 is the desk's -9.88. | the desk | `world_payment_truth.repayment_rows`'s issued-month test |

**The reader fix, graded** (R1, pre-registered): holds 5 → **4**, SYN-2016-015g leaves, no hold joins, cured 807.
Held. On s.9.2's ledger the same change reads 29 → 28. Test:
`tests/tools/test_a_dd_bill_due_on_a_weekend_is_not_past_due_before_its_bacs_day.py`. Both mutations kill it:
no roll at all, and a roll for every method.

**What this closes.** Every hold left on the cure row is now the page holding money the household paid and the desk
counted. None is a premature desk cure. The level-dd cure read is therefore clean of desk defects on this book; the
4 are repayment-posting's, and they move only when the seam and the walk post the cash that crossed.

**Seam census, re-measured.** The engine drops **12 world settlements, GBP 1,029.91** (`/var/tmp/t5h/dropped.json`),
exactly the shortfall finding's kind 3. By the outcome of the month each settles: **6 credit-bill months** (the five
named there plus SYN-2016-217g) and **6 months with no bill row**. The finding called SYN-2016-217g and SYN-2016-256g
"partial on a failed month"; both settle a credit month. Corrected there.

Graded: level-dd held=2 missed=1 code=0 reader=1 regressed=0 width=1.0

NEXT: kind-3 credit months: let `world_payment_truth.repayment_rows` count a credit-bill month whose level collection was returned, then grade SYN-2016-217's 3 holds and the 6 credit-month settlements

### 9.5 Kind 3 credit months reach the engine (seat, 12 Nov 2026)

`simulation/world_payment_truth.repayment_rows` now counts a credit-bill month as issued, so it knows the month's
commodity. Its negative face stays out of `amount_by_month`: a plan instalment is a share of what was asked, and a
settlement carries its own cash. Baseline is s.9.4's ledger (`/var/tmp/t5h/fix2.json`). The fix ledger is
`/var/tmp/k3c/fix.json`, from the same 6fe7827ab2 run. Pre-registered in `/var/tmp/k3c/PREDICTION.txt` before the
change was run.

| Row | Predicted | Read | Verdict |
|---|---|---:|---|
| P1/P3 settlements reaching the page; legs moved | the 6 credit months; those 6 legs | **6 legs**, exactly the 6 | held |
| P2 page money-in | +446.13 | 94,633.76 → **95,079.89** (+446.13) | held |
| P4 cure holds | 4 → 1, SYN-2016-217's 3 leave, -142g stays | **4 → 1** (cured 807) | held |
| P5 records changed | ≤ 12 | **6** | held |

**Not predicted.** Every changed balance moves by exactly its settlement's cash. SYN-2016-217g's case on bill 33999
falls 23.98 → 1.98. Three SYN-2016-256g bills move `paid_late` → `settled_by_credit` (its 46.00 now meets them). Two
leavers, PROS-2019-0318 and SYN-2016-047, close on the rebuilt page holding 65.17 and 106.30 of credit. That is an
artefact of the rebuild. The refund log comes from the old run, and the engine's closing balance on this code is
-176.50 (111.33 + 65.17) and -417.44 (311.14 + 106.30), with `money_in` on the settlement day. So a fresh run refunds
the credit (`/var/tmp/k3c/closing.py`).

**Still open.** All 6 settle a month whose bill the company owed the household. On SYN-2016-217g and -256g a returned
level collection explains the cash. On the other 4 nothing yet does: SYN-2016-215 paid 156.87 against a -56.37 credit. The cash crossed and the desk counted it, so the page must carry it
(F11). Whether the world should send it at all is the shortfall finding's item 2, untraced. The 6 no-bill-row
settlements (GBP 583.78) are still dropped.

Test: `tests/simulation/test_a_settlement_of_a_credit_month_reaches_the_engine.py`. Three mutations kill it: the
old guard, the credit face added to the asked amounts, and a guard that passes every settlement.

Graded: level-dd held=4 missed=0 code=0 reader=0 regressed=0 width=1.0

NEXT: SYN-2016-142g, the walk's draw of level surplus credit against a paid bill (s.9.4, the last hold)

### 9.6 The last hold: the close's credit meets the final bill only (seat, 12 Nov 2026)

SYN-2016-142g's 2019-08-19 "credit" is not a credit bill. It comes from the level-leaver close
(`balance_settlement_from_outcomes`, home_moves.md s.8.8c choice 14). That rule nets the closing credit against
every paid non-level bill after the last level collection. 142g's collections were returned in Sep and Oct
2019, and the leg then paid on receipt for a year before it closed in Oct 2020. The world asked each of those
bills at its face. The rule now nets the leg's final bill only, and choice 14 is corrected beside the claim.
Pre-registered in `/var/tmp/l142/PREDICTION.txt`. Baseline is s.9.5's ledger (`/var/tmp/k3c/fix.json`); the fix
ledger is `/var/tmp/l142/fix.json`, from the same 6fe7827ab2 run.

| Row | Predicted | Read | Verdict |
|---|---|---:|---|
| P0 non-final nettings on the base engine | 142g's 3 among them, on 5-40 legs | **5 bills, GBP 297.64, 3 legs** (142g, PROS-2021-0117, PROS-2023-0013g) | missed (fewer legs) |
| P1 cure holds | 1 → 0, no joiner | **1 → 0** (cured 807) | held |
| P2 page money-in | rises by the removed nettings less what moves onto final bills, ≥ 0 | **+253.63** (297.64 − 44.01, which moves onto 2 final bills) | held |
| P3 write-offs; closings | write-offs unchanged; closing grows on the moved legs | write-offs identical. Closing grows on 2 legs: 142g by 120.49, PROS-2021-0117 by 133.14. PROS-2023-0013g's 19.73 moves onto its final bill, so its closing does not move | held, except PROS-2023-0013g |
| P4 records changed | only the census legs | **3**, exactly those | held |

The rebuilt page ends 142g and PROS-2021-0117 holding 120.49 and 133.14. As in s.9.5, the refund log is from
the old run. The engine's closing on this code is −120.49 and −133.14, so a fresh run refunds them.

**Still open.** The world settles a mover's final month at the bill's face (`live_payment_triad`,
`final_month`), so choice 14's netting of the final bill is also the page's alone: 195 legs, GBP 4,715.67. That
is G8.15 and a payment-truth change, filed as
`docs/staging/SEAT_FINDING_A_LEVEL_LEAVERS_FINAL_BILL_IS_NETTED_ON_THE_PAGE_AND_COLLECTED_AT_FACE_BY_THE_WORLD_2026-11-12.md`.

Test: `tests/simulation/test_a_level_leavers_final_bill_meets_its_credit_before_the_refund.py::test_a_bill_paid_on_receipt_before_the_final_bill_keeps_its_cash`.
Two mutations kill it: removing the final-bill filter, and a filter that matches nothing.

Graded: level-dd held=4 missed=1 code=0 reader=0 regressed=0 width=1.0

NEXT: none -- the level-dd cure row reads 0 holds; the final-bill netting against the world's face collection is the filed finding's, a payment-truth change

### 9.7 Repayment-posting graded at origin, and each shape left traced to a line (seat, 12 Nov 2026)

**Why.** Repayment-posting's last grade is s.9's (held 3, missed 5). Fix 1, fix 1b, fix 2, the credit-month seam
fix (s.9.5) and the final-bill netting (s.9.6) have all landed on its paths since. Design only: nothing is built
here. **Book:** run 6fe7827ab2 (`07111cd8b4:docs/reports/run_output_latest.json.gz`). **Ledger:** rebuilt with
origin/main 1c66aceab6's code (`/var/tmp/rpg/ledger.json`). **Readers:** `/var/tmp/rda/shapes.py` (the blind row,
using the cumulative rule), `/var/tmp/repay-truth/desk.py` and `/var/tmp/desk29/s/{trace,classify,resid}.py`
(desk-written-off accounts), plus the engine probes in this section. Pre-registered in `/var/tmp/rpg/PREDICTION.txt`
before the ledger was built.

| Row | Predicted | Read | Verdict |
|---|---|---:|---|
| R0 the ledger reproduces s.9.6's | 0 records differ | **0 of 1,302** | held |
| R1 settlements the seam drops (`world_payment_truth.repayment_rows`) | 12 → 6, GBP 583.78, all on months with no bill row | **6, GBP 583.78**, all six | held |
| R2 blind row `INV_A_REPAYMENT_IS_ON_THE_PAGE_BY_ITS_OWN_DAY`: own-late | 16 → 14 to 18 | **0** | **missed** (reader, below) |
| R2 inherited-late | 0 to 2 | 0 | held |
| R2 never on the page by the book date | the 6 dropped (5 to 7) | **6**, exactly the dropped | held |
| R3 off-day N rows; stages dated after their cash day | 0; 0 | 0; 0 | held |
| R4 own-late closed on another cash day of the same leg | ≥ 12 | **0** | **missed** (reader, the same cause as R2) |
| R5 desk-written-off accounts still printing owed (was 37, GBP 2,281.34 on 78f82e4242) | 12 to 24, GBP 300 to 1,200 | **28, GBP 1,130.68** | count **missed** (code), amount held |
| R5 classes: R (a refund the desk never sees) the majority; L 0 to 3 | | R on **18**; L on **0** | held |
| R6 the dropped legs among the owing accounts | 0 to 3 | 0 | held |

**The R2/R4 miss.** s.9.3 said the 16 own-late left after fix 2 were the walk's assignment problem. I copied
that into the prediction. Running the same reader on each intermediate ledger shows that fix 1b, fix 2 and the
reader fix (s.9.4) all read 16, and that s.9.5's seam fix took them to **0**. All 16 sat on SYN-2016-217g (11)
and -256g (5). The blind row's own definition leaves out "settlements the seam drops". `shapes.py` did not, so
the 22.00 and 46.00 that the seam dropped stayed in each leg's cumulative world cash, and every later settlement
on those legs read late. That is the reader, not the walk. It is corrected beside s.9.3. The blind row now reads
**0 late** except the 6 the seam drops. Dating and assignment are clean on this book.

**What is left: three shapes, each traced to one account and one line.**

| Shape | Size | Traced on | Writer line | Side | Who is right |
|---|---|---|---|---|---|
| **F. A leaver's final bill is netted on the page and collected at face by the world** | 25 nettings on 24 of the 28 owing accounts, **GBP 633.16**. This is the whole desk-below-page residual, to the penny. **All 25 are on a leaver's final bill.** 19 (GBP 317.61) draw the level surplus (the s.9.6 branch). **6 (GBP 315.55, on 5 accounts) draw credit-bill credit** | SYN-2016-225: the final bill 34430 (159.55, Sep 2018). The walk netted two credit-bill credits against it, 96.52 (2017-10) and 62.68 (2018-07), so the page prints 0.35 cash and still owes 159.20 after marking it `paid`. The world's month 2018-09 is `success`, and the DD book took **159.55** on 31 Oct 2018. The desk's write-off (510.78, `company/billing/collections_journey.py:640`, `closed_balance_due_for_write_off` on the company's own ledger) is the page's 669.98 less exactly that 159.20 | `simulation/arrears_engine.balance_settlement_from_outcomes`. The level-surplus nettings come from the leaver branch (`:1391-1420`). The credit-bill nettings come from the paid-bill draw (`:1330-1341`, "the bill asks for what is owed", SLC 31H.12). The world collects the final month at its face (`background/live_payment_triad`, `final_month`) | world/tools | the desk, on the cash that crossed |
| **R. One leg's credit is refunded while the account's other leg owes** | 18 accounts, **GBP 497.52**. Every one is per-leg. The stale part is 0 on this book, as the class-R note predicted | SYN-2016-037g: 73.20 refunded at close while the electricity leg owes | `simulation/credit_refund_events.py`, which runs after the run, so the desk never sees it | world/tools | neither yet: SLC 27.16 treats the account as one balance. This is N29's subject (claim `the-n29-netted-set-off-reaches-origin-from-its-salvage`), so it is not this item's |
| **S. A settlement for a month before the supplier's first issued bill** | the 6 dropped, **GBP 583.78**, all on occupier legs | OCC-c2c2a33d47d7: the world's records start at 2020-04 and the level schedule at 358.47. The world recorded May as `failed` and a settlement of 358.47 on 4 Jun 2020. The supplier's first issued bill is 2020-07. The same holds on all 6: the world's month is 1 to 3 months before the first issued bill | the seam (`world_payment_truth.repayment_rows`) refuses it correctly: there is no bill to settle. The world presents and records on its own bill rows (`background/live_payment_triad.record_period`, `:1261`), not the issued ones. I have not traced which input sets its first month | world | the company side: a supplier cannot be paid for a bill it did not issue. The world should not present that collection |

R and F overlap on 14 accounts: 18 + 24 − 28. GBP 497.52 + 633.16 = 1,130.68, so no account is unexplained. 37 →
28 is not a fix count: 37 was on book 78f82e4242, and this is a later run.

**What the F census changes for the claim that holds the fix.** `level-dd-final-bill-world-nets-level-surplus`
makes the world net a level leaver's surplus on its final bill. On this book that clears 19 of the 25 nettings. The
other 6, GBP 315.55 on 5 accounts (SYN-2016-037, -225 twice, -333, -444, -482), are **credit-bill credit** that
the page nets on the same final bill. The world collected them at face too. A world fix that nets only the level
surplus leaves those 5 accounts printing owed after the desk wrote them off. **GAP:** the DD book
(`dd_collection_book.attempts`) records credit bills as negative collections (255 of them, GBP -17,497.90). It
also records level months at the bill's face where `level_dd_collections` has the level amount (SYN-2016-225,
Oct 2017: 128.33 against 108.00). So it is not a clean witness for whether a credit bill's credit was paid out or
left waiting. Its final-bill rows agree with the world's outcome, and that is all this section relies on.

**Not on the list.** The 4 cure holds that s.9.4 handed to repayment-posting have left (s.9.5, s.9.6). The cure
row reads 0.

Graded: repayment-posting held=8 missed=3 code=1 reader=2 regressed=0 width=0.5

NEXT: the final bill nets every waiting credit in the world as on the page, the credit-bill credit as well as the level surplus (24 accounts, GBP 633.16), under the claim already holding it, `level-dd-final-bill-world-nets-level-surplus`


### 9.8 The written-off accounts still printing owed, after N29, and the world's final-bill net (seat, 12 Nov 2026)

**Why.** s.9.7 left 28 desk-written-off accounts printing owed (GBP 1,130.68): F (24, 633.16) and R (18, 497.52).
N29's set-off (3af02a2dd) is on origin for R. The world's final-bill net (claim
`level-dd-final-bill-world-nets-level-surplus`) is for F. Its first landing died; three holders were swept back
with its 18 lines uncommitted in the shared tree. Those bytes are landed unchanged, just before this section, under
claim `the-written-off-accounts-printing-owed-are-read-after-n29-and-the-final-bill-net`. **Book:** run 6fe7827ab2 (`/var/tmp/rpg/run.json`). **Code:** origin/main 282510e8d8. The refunds are
replayed with origin's `generate_credit_refund_log` (`/var/tmp/n29/scripts/replay.py`) and the ledger is rebuilt
(`/var/tmp/r98/ledger.json`). **Reader:** `/var/tmp/repay-truth/desk.py`, unchanged from s.9.7. Pre-registered in
`/var/tmp/r98/PREDICTION.txt` (18:52Z) by the holder swept back at 21:21Z, before its ledger was built (18:53Z).
I re-ran the reader at origin bb10c3a5d5 (no change to `simulation/`, `company/billing`, `company/interfaces` or the
two ledger generators since 282510e8d8) and it reads the same: 24, GBP 633.16. The owing set against s.9.7's
(`/var/tmp/rpg/ledger.json.desk.json`): 4 left, none joined. **This book cannot grade the world net.** The world's
collections are fixed in the run, so F is read here as it stands, and the net is graded on the next fresh book.

| Row | Predicted | Read | Verdict |
|---|---|---:|---|
| P0 replay: refund set and days unchanged | asserts hold | 176 refunds, 42 with a set-off, GBP 1,339.69 set off | held |
| P1 R5 accounts still printing owed | 12 to 24, GBP 450 to 800 | **24, GBP 633.16** | held (at the edge) |
| P2 class R (a leg refunded cash while another leg owes) | 18 → 0 to 3 | **0** | held |
| P3 class F unchanged where N29 does not reach | 24, GBP 633.16 | **24, GBP 633.16**, to the penny: the owing set is s.9.7's F set exactly | held |
| P4 the 5 credit-bill-credit accounts | 3 to 5 still owed | **5 of 5** (SYN-2016-037 44.49, -225 159.20, -333 7.18, -444 71.45, -482 33.23) | held |

**Who left** (read against s.9.7's owing set). The 4 accounts that were R and not F leave: PROS-2017-0056, PROS-2019-0318, SYN-2016-182 and
SYN-2016-368. None joins. On the 14 that were both R and F, the set-off takes the whole credit (refund 0.00 on each).
The debt leg still prints owed by the F netting. So the residual is now one shape, on one writer line.

**R5 does not read 0 to 3 on this book, so each account left is named, with its writer line.** All 24 are F. On each, the page nets a level leaver's final bill
against credit (`simulation/arrears_engine.balance_settlement_from_outcomes`, s.8.8c choice 14). The world
collected that bill at its face (`background/live_payment_triad.record_period`, `final_month`). The desk counted
the cash and wrote off the rest. Owed on the page: PROS-2016-0067 16.60, PROS-2016-0349g 9.26, PROS-2017-0038g
12.38, PROS-2017-0199 7.92, PROS-2017-0249 12.90, PROS-2018-0359 24.93, SYN-2016-007g 9.20, -037 44.49, -080g 11.24,
-091 23.55, -151 35.71, -155g 5.09, -225 159.20, -333 7.18, -342 22.49, -418g 21.55, -444 71.45, -455 7.15, -482
33.23, -507g 4.99, -552g 61.49, -557g 2.89, -563 4.25, -584 24.02.

**The world net, built.** On a final month, a leg that has presented a level collection now waits the larger of
its credit-bill excess and the credit on its own ledger (`_leg_balance_on`: bills at face, cash, credit notes).
A credit bill posts a GBP 0 face and a credit note (`run_phase2b`, `credit_gbp=max(0, -ask)`), so that ledger
credit already holds the credit-bill half. That makes s.9.7's NEXT one build, not two: the 5 credit-bill accounts
are covered by the same line. Test: `tests/background/test_a_level_leavers_final_bill_asks_its_face_less_the_schedules_surplus.py`,
4 cases, including the credit-bill case. Removing the branch fails 3 of them. The never-level control passes
either way. Dropping the `_legs_ever_level` guard is equivalent on that fixture: a leg paid at face holds no
ledger credit. It is kept to scope the change to the legs the page nets.

**For the next fresh book** (pre-registered, same file): W1 world final-bill nettings on level legs 170 to 215
legs, GBP 4,200 to 5,200. W2 class F 24 → 0 to 3, with all 5 credit-bill accounts clear. W3 R5 0 to 3. A
consequence to watch: s.8.8d choice 20's SYN-2016-244 (a level leg whose last level collection is years old) is
on `_legs_ever_level` too, so its final bill now nets in the world. Where the page does not net it, that
appears as a new F-shaped disagreement in the other direction.

**W4, pre-registered 12 Nov 23:30Z, before the book exists** (drawn early: the item had no not-before guard, unlike
its sibling `n29-ceiling-graded-on-the-16-nov-book`). The page's close nets every paid non-level bill after the last
level collection, so the final bill of a leg long off its schedule is in the page's net too. The world now waits the
leg's ledger credit on the same bill. Prediction: reverse-F accounts (the world asks less than the page nets to, so
the page prints a credit the world never left) **0 to 3**; SYN-2016-244's final bill is asked **GBP 30 to 45**
(choice 20's 35.68), not 77.82, and its late refund of the repayment credit is gone. A reverse-F count above 3 means
the world's ledger credit and the page's close credit are different quantities, and that is the next item.

**Amendment, 2026-11-14: what the insulation change (e17ebc596) moves in W1–W4, before the book exists.** This
amendment is about e17ebc596 only. It changes the world's insulation draw after W1–W4 were filed. The one-variable book A/B, e17ebc596^ against e17ebc596, same seed, neither arm carrying ceeefa5960 or 69866925b (`docs/staging/records/SEAT_RECORD_WHAT_THE_INSULATION_CHANGE_CAN_MOVE_IN_THE_16_NOV_PREREGISTRATIONS_2026-11-13.md`). W1–W4 are
kept as filed above.
- **W1, fabric can move it:** proxy (an ever-level closed leg whose last bill carries `credit_applied_gbp`) 246 of 485,
  GBP 6,579.51 → 244 of 481, GBP 6,317.04. Now predicts **168 to 213 legs, GBP 4,030 to 4,990** (shifts of −2 legs
  and −4.0%).
- **W2/W3, fabric can move it:** R5 30, GBP 699.65 → 27, GBP 674.59. PROS-2016-0067, PROS-2017-0038g and
  PROS-2017-0249 leave s.9.8's F list because they are not on the new book. PROS-2019-0318 leaves (POOR → PARTIAL).
  PROS-2019-0125 joins. Now predicts W2 F and W3 R5 **0 to 3, unchanged**: the band is a floor that fabric
  shifts by −3, so the bound stays. The 5 credit-bill accounts are SYN founders whose homes do not change.
- **W4, fabric cannot move it:** SYN-2016-244 is a founder whose home does not change, and its final bill reads
  77.82 asked at both commits. GBP 30 to 45 stands.

A read, not a grade: both arms carry 37d934286 and still read R5 27 to 30 and SYN-2016-244 at 77.82, against
W3's 0 to 3 and W4's GBP 30 to 45. So if W3 or W4 misses on 16 Nov, the cause is not fabric.

**Amendment, 2026-11-14 (later, still before the 16 Nov book): can S6b or the statement walk move it too?** **No for W1–W4, on both counts.** `REPAYMENT_POSTING_AREA_MAP_2026-11-14.md` s.6: "None of W1–W4 is about S1, S4 or S6b". W1–W4 are S6a/S9/S7–S8 figures. S6b (69866925b) changes one thing: a leaver's money-in day, which only `generate_credit_refund_log` reads, to date the refund's paid day. The set-offs take that date too. On the r98 replay (`docs/design/REPAYMENT_POSTING_AREA_MAP_2026-11-14.md` s.8, P4/P5) the closing balance is identical on all 850 legs and the refund amount is identical on all 178 refunds. 3 paid days move, every one earlier. None of the 3 carries a set-off. W1–W4 read amounts and balances, never a refund's paid day. The statement walk (84a44b51c) changes only `statement_export.account_events`. Its own measurement found `tools/domain_invariant_runner.py --ledger` byte-identical, because the runner reads `raw_account_export.account_events`. It also found `statement_digest` moving on the 84 set-off legs only. No W1–W4 figure reads the statement walk.

The account-page wrong row is **not** moved to corrected: its 24 accounts clear only on a book whose world
carries the net. That is the 16 Nov 04:00 book. New books are held until then.

Graded: repayment-posting held=5 missed=0 code=0 reader=0 regressed=0 width=0.5

NEXT: none -- W1 to W3 are graded on the first fresh book that carries the net (the 16 Nov publish)
