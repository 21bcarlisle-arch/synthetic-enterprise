# The repayment-posting area, state by state: where a household's repayment cash can be, which function decides it, who reads it, and where the 15 misses sit (2026-11-14)

*Seat executor, 13–14 Nov 2026, Lane-0 item `repayment-posting-area-map`. This follows `ways_of_working` W1
(`docs/design/THE_LEARNING_LOOP_ON_HOW_WE_WORK.md` §7). The learning loop reads STOP on repayment-posting: 24 held of
39 over the last 7 days, with 15 misses, 11 of them from our model of the code or of the reader. W1 says the area's map
comes before the next fix. This page is that map. **No fix is written here.** Read from the code at origin 83991f5fef.
The template is `LEVEL_DD_AREA_MAP_2026-11-11.md`, which is organised by function. This page is organised by **state**,
because each of the 15 misses came from a state that its reader or its prediction had left out. Ledgers T, E, K and P
are as defined in that map's s.0.*

**Book.** Run 6fe7827ab2 with N29's set-off replay (`/var/tmp/r98/run_setoff.json`, the same run s.9.8 read). Ledger
rebuilt at 83991f5fef (`/var/tmp/rpam/ledger.json`). The page code has three changes since s.9.8's 282510e8d8:
ceeefa5960 (reg 6D clock starts at the issue day), f0bca8e355 (SME VAT lines) and 37d9342869 (the world's final-bill
net). The third changes the world. It acts only on a fresh run, so this book cannot show it.
**Readers:** `/var/tmp/rpam/s/trace.py` (one leg, every state in order), `census.py` (each state's size),
`offday.py` and `stmt.py`, plus the existing `/var/tmp/repay-truth/measure.py` and `desk.py`.
**Pre-registered:** `/var/tmp/rpam/PREDICTION.txt`, written before the ledger was built; graded in s.5.

## 0. The unit, said before any state

The unit is **one household settlement**: one row of `per_customer_behavioral[*].world_payment_truth.repayments`. On
this book every row is kind `settlement`; no plan instalments cross. Its cash is GBP. From that row on, the cash is in
exactly one of the states below. A settlement can be **split** across states: part goes to one bill and the rest is held.
Each state is therefore sized in GBP and in rows, never as a share of settlements.

Plain level direct-debit collections are **not** repayments. They are money in on their own day (the level-DD map,
s.1b). A repayment is cash the household sends to settle a returned collection or a failed bill.

## 1. The states

| # | State | Decided by (file:line) | Read by | Size on this book (to 2025-07-04) | Traced on |
|---|---|---|---|---|---|
| **S0** | **Paid in the world**: the household's cash crossed | `background/live_payment_triad.py:1068` `_cross_settlement`. The cash is `min(asked, open_on_contract_gbp(T rows))` (`:1094`), so it is sized on **T** | the desk (K) through `observe_hand_over` (`:1110`); the world record `world_payment_truth.build` | **1,423 settlements, GBP 95,163.69** | every leg below |
| S0′ | *Not crossed*: lost after the final bill, withdrawn by a plan, already cleared, cut to the balance, early-contact withdrawn | `_cross_settlement` `:1072-1100` (the counters `_n_settlements_*`) | **no reader**: the counters are not in the run output | **GAP**: not exported, so no number can be given | — |
| **S1** | **Dropped at the seam**: crossed, but no issued bill for its month | `simulation/world_payment_truth.py:150` `repayment_rows`. The drop is at `:178` (`commodity is None`) | E never sees it, so P never does. `measure.py`'s T is taken **after** this line. The shortfall read's T (`/var/tmp/rsf6/read.py`) is taken **before** it | **6, GBP 583.78** (all on months with no bill row; the 6 credit-month ones left at s.9.5) | OCC-c2c2a33d47d7 |
| **S2** | **Allocated to an open bill on its cash day** | `simulation/arrears_engine.py:1365-1405`, the walk's repayment branch. Bills on the same fuel are taken oldest first. Off level, the walk prices at `min(asked, open)`. On level, it takes the cash (`:1369`) | P: a case's `ARREARS_REPAID` (`with_credits_applied`, `arrears_engine.py:777`), or a no-case level return's `payments[*].repayments` (`tools/generate_billing_ledger.py:1160-1164`). The desk's cure reader, `level_dd_cure_reader` | **1,870 entries, GBP 79,412.07** (level 1,368 / 46,001.18 on 178 legs; off level 502 / 33,410.89 on 107) | OCC-1bb3be076448; SYN-2016-139's 2.15 |
| **S3** | **Held as credit**: the excess over what is open, or cash for a bill not yet open. It waits in the walk's pool as kind `repayment` | `arrears_engine.py:1407` (`pool.setdefault(..., "repayment")`) | **not in E's `credits_applied`** until it is drawn. The page posts it on its cash day through the **catch-up** (`generate_billing_ledger.py:1301-1311`), under the `settles_month` bill or else the latest bill | **127 legs, GBP 5,543.17** of T − E at the book date. 58 of those legs are leavers (GBP 1,930.95) | SYN-2016-139's 28.85 for 11 months |
| **S4** | **Netted later from held credit against a failed bill** | `arrears_engine.py:1336` (`_net` on a failed bill's arrival) and `:1346` (after a credit bill) | P: a zero-money `CREDIT_APPLIED` note at the case's opening when the cash predates it (`with_credits_applied` `:803`; the page leaves it out of `repaid_posted`, `generate_billing_ledger.py:1239`). A no-case return skips it (`:1160`, fix 1b). The cash itself is already on the page from S3's catch-up | **278 entries, GBP 9,624.67, 154 legs, every one a level leg** | SYN-2016-256g (46.00 of Nov 2020, netted Sep 2022 and Aug 2023); SYN-2016-380 |
| S5 | **Drawn by a later paid bill** (SLC 31H.12: the bill asks its charges less the credit) | `arrears_engine.py:1360`. On level, `("credit",)` only, so held repayment credit is never drawn here | P: the paid bill's `amount` falls. The cash is on the page from S3's catch-up | **0** on this book. Off level, no leg held repayment credit when a paid bill arrived | none (named in code, never taken on this book) |
| **S6a** | **Netted at close: a level leaver's final bill takes the closing credit** (s.8.8c) | `arrears_engine.py:1413-1444`. This draws from `closing`, not from the pool, and is listed as kind `credit` | P prints a smaller final payment. The world collected the bill at its **face** until 37d9342869 (shape F, s.9.7) | 24 accounts still owed after the desk wrote them off, GBP 633.16 (s.9.8 P1; read again, s.5 P3) | SYN-2016-225: closing 669.98, desk write-off 510.78 |
| **S6b** | **Held credit dated as money in at close**: a netting day is taken as the day the cash arrived | `arrears_engine.py:1445-1472`. `arrived` takes every repayment credit's **netting** `date` (`:1457`), not its `credit_period_end` | `credit_refund_events.generate_credit_refund_log` `:107` (the refund clock); the reg 6D breach row | **24 of 66** leavers with a money-in day have it set by a netting day later than the cash. On **4** it sets the refund request day: PROS-2019-0318, SYN-2016-093, SYN-2016-139, SYN-2016-360 | SYN-2016-139 (below) |
| **S7** | **Set off against the other fuel's closing debt** (s.8.8e, N29) | `credit_refund_events.py:50` (`set_off_gbp`), then `arrears_engine.py:1475` nets it in the debt leg's walk | P: `set_offs` (`generate_billing_ledger.py:428`; `generate_payment_ledger_data.py:214`). **Not** read by `company/billing/statement_export.account_events` (s.3) | 42 set-offs, GBP 1,339.69 | SYN-2016-037g 73.20 → SYN-2016-037 |
| **S8** | **Refunded** | `credit_refund_events.py:50`, from E's `closing < 0`. It runs **after** the run, so the desk never sees it | P: `refunds` → `refund_debit` (`generate_payment_ledger_data.py:225`); `statement_export:324` | 150 refunds, GBP 20,040.95 | SYN-2016-139 32.04 on 12 May 2022 |
| **S9** | **Written off**: by the engine at close or by the statute bar, or by the desk | engine `arrears_engine.py:1496` (at most `max(0, closing)` on a level leg) and `_bar`; desk `generate_payment_ledger_data.py:276` `desk_write_off_postings` | P `WRITTEN_OFF` stage and `desk_write_offs`; `desk.py`; `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` (`tools/domain_invariant_runner.py:1843`) | 159 desk write-off accounts; 24 still print owed (S6a) | PROS-2016-0117: engine 7.56, desk 8.24 |
| S10 | **Still held at the book date on a live account** | S3 with no later failed bill and no close | the page shows it as credit; no reader separates it from S3 | inside S3's 127 legs (69 stayers, GBP 3,612.22) | SYN-2016-256g's 66.91 of 24 Feb 2024 waited to Apr 2025 |

**The census reconciles.** E = S2 + S4 = 79,412.07 + 9,624.67 = **89,036.74**, which is `measure.py`'s E to the penny.
T after the seam is 94,579.91 = 95,163.69 − S1's 583.78. T − E = 5,543.17 is S3 + S10 at the book date. The page (P) is
94,579.91, the same as T after the seam, on every leg: every held GBP reaches the page on its cash day through the
catch-up, even where E has not yet drawn it.

**States the item's list missed:** S0′ (not crossed: the world never records it), S1 (dropped at the seam), S4 as a
state separate from S2 (the same cash is allocated twice, first as held and later as netted, and the page prints the
second only as a zero-money note), S5 (in the code, empty on this book), S6b (the netting day used as the arrival day),
S7 (set-off) and S10 (held at the book date).

## 2. Each state traced on one household

**SYN-2016-139** (electricity, level leaver). The item named it among the 249-leg and 194-leg shortfall legs. **It is
not among them:** `measure.py` on 78f82e4242 lists 157 short legs and 29 over, and SYN-2016-139 is in neither list. It
is the reg 6D refund-clock leg (`SEAT_FINDING_OLD_CREDIT_NETTED_AT_CLOSE_STARTS_THE_REFUND_CLOCK_LATE_2026-11-12.md`).
It is still the best single trace, because one settlement passes through six states:

| Day | State | What happens |
|---|---|---|
| 7 May 2021 | S0 → S2 + S3 | The household settles the returned April 2021 collection: **31.00** crosses. The April bill is not yet due (its due date is 18 May), so the walk has nothing open, and all 31.00 goes to the pool as `repayment` |
| 7 May 2021 | P | The catch-up posts **2.15 + 28.85 = 31.00** on 7 May against INV 29525, the April return. **The page is right on the day** |
| 18 May 2021 | S4 | The April bill (31.46) arrives as failed. `_net` draws oldest first: 12.29 (Mar 2017 credit bill), 17.01 (Aug 2020 credit bill), then **2.15** of the repayment. That leaves **28.85 held** |
| May 2021 to Apr 2022 | S3 | The 28.85 waits. On level, a paid bill cannot draw repayment credit (`:1360`) |
| 27 Apr 2022 | S4 at close | The final bill INV 29537 (11.52) is returned. `_net` takes **11.52** of the held 28.85. On the page this is a zero-money CREDIT_APPLIED note ("the household's payment of 2021-05-07") |
| close | S6b | `money_in_out` reads the 11.52's **netting day**, 27 Apr 2022, as the day the money arrived. Closing −32.04 (the 17.33 still held plus the level difference) |
| 12 May 2022 | S8 | Refund **32.04**. The request day is 27 Apr, so `breached_reg_6d_deadline` is False. Counted from the issue day (13 Apr), the refund is late |

**OCC-c2c2a33d47d7** (S1). The world settles May 2020 for 358.47 on 4 Jun 2020. The leg's first issued bill is Jul 2020,
so `repayment_rows` has no commodity for the month and drops the settlement. The trace has a WORLD row and nothing after
it: no SEAM, WALK or PAGE row.

**OCC-1bb3be076448** (S2, level). It settles the Apr 2023 return for 27.00 on 18 Aug 2023. The walk credits **27.00**,
the cash, not the 49.38 face (that was the defect on 78f82e4242). The page posts an ARREARS_REPAID of 27.00 on 18 Aug.

**SYN-2016-256g** (S3 → S4 → S10, a stayer; the largest leg in the 78f82e4242 shortfall: T 820.40, page 576.40). Its
46.00 of 5 Nov 2020 settles the Jul 2020 month. The walk nets **41.87** of it against the Sep 2022 return (on 16 Oct
2022) and **4.13** against Aug 2023. The page posts the 46.00 on 5 Nov 2020 (catch-up) and prints two CREDIT_APPLIED
notes at those cases' openings. Its 24 Feb 2024 pair (138.37 + 134.99) posts as one 273.36 row that day. 66.91 of it
is still held until a 2025-03 return nets it on 15 Apr 2025 (S10 until then). **Today the page and T agree on this leg
(0 short).**

**SYN-2016-380** (S4, the s.9 cause-B leg). Its 102.00 of 1 Apr 2019 is netted against the Sep 2019 case on
19 Sep 2019. The page posts 102.00 on 1 Apr 2019 under INV 42056 (Mar 2019). The Sep case prints a zero-money
CREDIT_APPLIED. 11 netting entries on this leg, every one with its cash on the page on its cash day.

**SYN-2016-225** (S6a → S9). The page nets credit against the final bill, while the world collected that bill at face.
Closing **669.98**; the desk writes off 510.78 on 30 Sep 2019, and the leg still prints 159.20 owed (s.9.7).

**SYN-2016-037 / -037g** (S2, S4, S7, S9). The 61.93 of 28 May 2018 splits: 48.46 goes to its own case (ARREARS_REPAID
on its day) and 13.47 is held. That 13.47 is netted against the Mar 2019 case and posted under INV 23833 on its cash
day by the catch-up. The gas leg closes −73.20, and **all 73.20 is set off** against the electricity leg on 14 May 2020
(refund 0.00). The electricity leg's close write-off is 66.18, and the desk writes off 9.24 more.

**PROS-2016-0117** (S2 on a no-case return, then S9). The 30.00 of 6 Nov 2017 posts as a `payments[*].repayments` row on
its day. The engine's close write-off is 7.56, the desk's 8.24. The page posts the desk's 8.24, and the 0.68 difference
is the engine-versus-desk write-off reconciliation (`desk_write_off_postings`). It is not a repayment state.

## 3. What the census found that no item asked for

1. **S6b is wider than the one breach.** The refund-clock finding counted 1 breach and said it had "not counted the
   legs where the same rule moves the request day". 24 of 66 leavers with a money-in day have it set by a netting
   day after the cash. On 4 it **is** the refund request day. *(Corrected 2026-11-14, s.8: **3**, not 4. PROS-2019-0318's 12 Jun 2023 is also the day its returned final bill was part-paid, so a real arrival sets it as well; the census flagged the netting day without checking whether another arrival shared it. The 24 is 23 for the same reason.)* SYN-2016-139 is the one that breaches. On the other 3
   (PROS-2019-0318: cash 22 Nov 2022, request 12 Jun 2023; SYN-2016-093: cash 13 Sep 2016, request 1 Sep 2017;
   SYN-2016-360: cash 16 Feb 2017, request 19 Oct 2017) the refund lands inside a clock that started too late. Each
   reads clean, with no row able to see it, exactly as the finding said. The refund log here is the replay's, written
   at 282510e8d8, which is before ceeefa5960 moved the clock's start to the issue day. The 4 are counted against that
   log.
2. **The statement walk does not carry S7.** `desk.py` reads "statement walk vs page disagree: **84 of 1,302**". Earlier
   books read 0. All 84 legs carry a set-off, and each residual is ± that leg's set-off (OCC-01e79fcf2d4f +11.50 and
   its gas leg −11.50). `company/billing/statement_export.account_events` reads `refunds` (`:324`) but not
   `set_offs`, which N29 added to the page. It reads the same on s.9.8's ledger, so it has been live since N29 landed.
   Filed: `docs/staging/SEAT_FINDING_THE_STATEMENT_WALK_DOES_NOT_CARRY_THE_CLOSING_SET_OFF_2026-11-14.md`.
3. **S1 has two readers with opposite definitions of T.** The shortfall read (`rsf6/read.py`, `rda/shapes.py`) takes T
   **before** the seam. `measure.py` (the reader behind 249 and 194) takes it **after**. So `measure.py` cannot see S1,
   and `shapes.py` counted it as late. Five of the 15 misses (s.4), and this map's own P1 miss (s.5), sit on that one
   line.
4. **S0′ has no reader.** The triad counts settlements it withdrew, cut or lost at close, but the run output does not
   carry the counters. A household that would have paid, and whose payment the world cut, leaves no trace. **GAP.**

## 4. The 15 missed repayment-posting predictions this week, each placed on a state

The five grading commits the loop reads: 804e627de4 (5 missed), b2f8e23fc0 (5), f5d1203024 (1), 18148e6b6e (1),
eb89cfd46b (3). "Missed by" is each commit's own trailer split; 11 of the 15 are code or reader.

| Commit | Row | Missed by | State that explains it | How |
|---|---|---|---|---|
| 804e627de4 | S0 legs where the page posts less than the cash: 12 against 0–10 | code | **S1** | all 12 were seam drops (6 with no bill row, 6 credit months) |
| 804e627de4 | S1 posted on the cash day as one entry: 40.2% against 60–90% | reader | **S2 + S3** | a settlement is split into the walk's share (S2) plus the catch-up's `rest` (S3). "One settlement, one row" is not the shape |
| 804e627de4 | S2 posted later as one entry: 2.7%, median 26.5 days | reader | **S4** | at that code, netting from held credit was dated at its netting day |
| 804e627de4 | S3 never one entry: 55.3% against 2–15% | reader | **S2 + S3** | as row 2 |
| 804e627de4 | S4 money missing: GBP 1,029.91 against under 500 | code | **S1** | the same 12 drops |
| b2f8e23fc0 | P2 off-day `:1118` rows: 146 against 140–145 | reader | **none** | a counting definition: the range copied 145 rows "on a due day", and one off-day row was not on a due day. No state is involved |
| b2f8e23fc0 | P4 W carries late cash: 80 against 30–60 | other (its trailer counts 1 code-or-reader, P2) | **S4** | one W stage closes the cumulative gap of every earlier partly posted settlement on the leg |
| b2f8e23fc0 | P5 a part on an N row: 92 against 100–140 | other (its trailer counts 1 code-or-reader, P2) | **S4** + **S1** | the partition also held 12 seam drops and 11 inherited gaps that the ranges left out |
| b2f8e23fc0 | P5 a part on a W stage: 73 against 15–45 | other (its trailer counts 1 code-or-reader, P2) | **S4** | as P4 |
| b2f8e23fc0 | P5 all parts on the cash day: 607 against 620–660 | other (its trailer counts 1 code-or-reader, P2) | **S1** | the 12 seam drops and 11 inherited gaps were outside the range |
| f5d1203024 | F4 `:1118` rows dated before their own return: 58 against 0–36 | reader | **S3 → S4** | the walk nets old held cash (S3) against a later return (S4). Moving the date to the cash day put it before the bill it was filed under |
| 18148e6b6e | P2 rows on no-case payments: 431 against 406 | reader | **S3 (catch-up)** | the catch-up files under the `settles_month` bill, and 25 of those bills are themselves no-case returns |
| eb89cfd46b | R2 own-late: 0 against 14–18 | reader | **S1** | the 16 were seam-dropped cash the reader kept in the world's total. s.9.5 let it through |
| eb89cfd46b | R4 own-late closed on another cash day: 0 against ≥12 | reader | **S1** | the same cause as R2 |
| eb89cfd46b | R5 desk-written-off accounts still owed: 28 against 12–24 | code | **S6a + S7/S8** | F (final-bill netting) on 24 accounts, R (refund while the other leg owes) on 18, overlapping on 14 |

**Explained: 14 of 15. Not explained by any state: 1** (b2f8e23fc0 P2, a counting definition). By state: S1 explains
**5** whole and 1 in part; S4 5; S2 + S3 2; S3 (the catch-up) 1; S6a + S7/S8 1. **S1, the one line with two readers,
is the largest single source.** S4, the state that allocates the same cash twice, is the second. Neither was on the
item's list.

## 5. Pre-registration graded (`/var/tmp/rpam/PREDICTION.txt`)

| Row | Predicted | Read | Verdict |
|---|---|---:|---|
| P1 `measure.py`: legs where page < cash | 6, GBP 583.78 (the seam drops) | **0** | **missed** (reader: `measure.py`'s T is taken after the seam, so S1 is invisible to it. The same cause as s.4's five) |
| P2 SYN-2016-139's 11.52: netting, page row, money-in day, refund | as s.2 | as s.2. The cash posts on 7 May 2021 as 2.15 + 28.85, not as one 11.52 row | held |
| P3 `desk.py` still owed | 24, GBP 633.16 | 24, GBP 633.16 | held (it reproduces s.9.8) |
| P4 page repayment rows on a day no cash crossed | 0 | **0 of 2,275** | held (it reproduces s.9.7 R3) |
| P5 the 84 statement-walk disagreements are the set-off legs | 84 = 2 × 42 | all 84 carry a set-off, residual ± the set-off | held (filed after P1–P4 were read, before this check) |

P2–P4 reproduce answers already on the record (s.9.7, s.9.8), so they are **not** counted in the trailer: counting
them would raise the hit rate without testing anything (R12). The trailer grades P1 and P5 only.

## 6. Which state each 16 Nov prediction is about

The 16 Nov 04:00 book is the first fresh run that carries 37d9342869 (the world's final-bill net). It grades
s.9.8's W1–W4:

| Prediction | State | What a miss would mean |
|---|---|---|
| W1 world final-bill nettings on level legs: 170 to 215 legs, GBP 4,200 to 5,200 | **S6a**, world side | the world's ledger credit (`_leg_balance_on`, K) and the page's closing credit (E) are different quantities |
| W2 class F 24 → 0 to 3, all 5 credit-bill accounts clear | **S6a** → **S9** | the world nets a different credit from the page on the final bill |
| W3 R5 (desk-written-off accounts printing owed) 0 to 3 | **S9**, with **S6a** and **S7/S8** feeding it | a set-off or refund the desk never sees (S8 runs after the run) |
| W4 reverse-F 0 to 3; SYN-2016-244's final bill asked GBP 30 to 45 | **S6a** (the world asks less than the page nets) and **S8** (the late refund of repayment credit) | the same as W1 |

None of W1–W4 is about S1, S4 or S6b. **S6b will still be on the 16 Nov book.** No change touches `:1457`. Predicted
for that book: request days set by a netting day, **3 to 6** (4 here, and the population moves with the run).
*Amended 2026-11-14, before the 16 Nov book (s.8). The S6b change now touches `:1457`. If the book's code is at or
after that commit, the prediction is **0** request days set by a netting day alone. A leg may still be flagged by the
census where a real arrival falls on the netting day, like PROS-2019-0318; count those apart. If the book predates
the commit, the original 3 to 6 stands. Read the book's code commit first, and grade only the branch it is on.*
*Amended 2026-11-14, before the 16 Nov book: what fabric (e17ebc596) moves in this line. The prediction above stands. Fabric cannot move the post-S6b 0: no population can set a request day by a netting day once the money-in day ignores it. Fabric can move the coincident-arrival count kept apart. The census on the fabric A/B arms (pre-S6b code at both) reads 22 of 66 → 22 of 69 netting-dated money-in days, and 0 → 0 request days set by one. So the pre-S6b 3 to 6 branch would already have missed on those arms. The 16 Nov book also carries ceeefa5960 (refund clock), so read the census at the book's own code root. The statement walk (84a44b51c) cannot move this line: the census reads the walk, not the statement. Detail: `docs/staging/records/SEAT_RECORD_WHAT_THE_INSULATION_CHANGE_CAN_MOVE_IN_THE_16_NOV_PREREGISTRATIONS_2026-11-13.md`.*

## 7. What this changes

- **Before the next fix in this area,** its prediction names a state from s.1 and the reader's definition of T
  (before or after the seam). Five misses this week, and this map's own, would have been avoided by that one sentence.
- **S6b is the next code item.** It is a world fix, recommended by the refund-clock finding and not built here:
  `money_in_out` reads the cash day (`credit_period_end`) of a repayment credit, not its netting day. On this book,
  4 request days move. The page has dated the same cash by its cash day since fix 2.
- **The set-off on the statement (s.3.2)** is a reader of S7 that was never told about it.
- **W1's second firing.** The loop's rule says that once a second area fires, the stop condition is built into the
  draw. Repayment-posting is that second area. The hand-off carries it.

Graded: repayment-posting held=1 missed=1 code=0 reader=1 regressed=0 width=0

## 8. S6b built: `money_in_out` reads the cash day (2026-11-14)

`arrears_engine.py`'s `arrived` loop now takes a repayment credit's `credit_period_end`, its cash day, where it
took the netting `date`. `home_moves.md` s.8.8d choice 18 was amended first (K8). The control is
`tests/simulation/test_a_close_refund_waits_for_the_money_it_pays_out.py`. EARLY_REPAID's money-in day is 16 Feb,
its cash day, and its refund no longer moves. Reverting the line turns it red.

**Pre-registration** (`/var/tmp/s6b/PREDICTION.txt`, written before the build). State **S6b**; the reader's T is
**after** the seam (`money_in_out` reads `repayment_rows` output, so an S1 drop never reaches it). Measured by
re-walking the r98 replay with the code before and after (`/var/tmp/s6b/diff.py`) and the census's S6 lines.

| Row | Predicted | Read | Verdict |
|---|---|---|---|
| P1 census: money-in days set by a netting day after the cash | 24 of 66 → 0 of 66 | **1 of 66** (PROS-2019-0318) | **missed**, reader: its day is also its part payment's day, which the census flag never checked |
| P2 money-in days that move | exactly the 24, each earlier | **23**, each earlier, none later, none vanish | **missed**, reader, the same cause as P1 |
| P3 the 4 named legs' new money-in day | at or before each cash day | SYN-2016-139 → 7 May 2021 and SYN-2016-093 → 13 Sep 2016 held. SYN-2016-360 → **14 Oct 2017**, a later real arrival, not its 16 Feb cash. PROS-2019-0318 did not move | **missed**, reader: I took the cash day to become the latest arrival |
| P4 recomputed refund log | amounts unchanged; paid days earlier or unmoved; at most 24 move | 178 refunds, amounts identical, **3** paid days earlier: SYN-2016-139 12 May → 29 Apr 2022, SYN-2016-093 15 Sep → 4 Sep 2017, SYN-2016-360 2 Nov → 27 Oct 2017 | held |
| P5 closing balances | identical | identical on all 850 legs | held |
| P6 EARLY_REPAID control | goes red, rewritten to the cash day | red. Its fixture repayment row also had `due_date` 14 days after its cash day, which the world never builds (`repayment_rows` sets both to the cash day), so the row was corrected to the world's shape | held |

**W1's first test.** The map's sentence held: the prediction named the state and the side of the seam, and
neither was the miss. All three misses are one reader slip on the census's own flag, which s.3 published. A
map row that counts by a filter needs the filter's partition checked: a coincident real arrival is the leg it
did not see.

SYN-2016-139's refund is now paid 29 Apr 2022, inside reg 6D's ten working days from 13 Apr. The
`DOMAIN_INVARIANT_EXCEPTIONS.yaml` row for it stays at its ceiling until a fresh book carries this change: the
16 Nov 04:00 run is built from an earlier commit.

Graded: repayment-posting held=3 missed=3 code=0 reader=3 regressed=0 width=0

NEXT: none -- S6b is built (s.8). The 16 Nov book's census reads it; the SYN-2016-139 exception is dropped once a fresh book shows the refund on time
