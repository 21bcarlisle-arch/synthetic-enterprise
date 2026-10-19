# Pre-registration: how many dual households hold a credit on one fuel and a debt on the other, on the publish run

**Written 2026-10-18 ~17:30Z. No dual-fuel run output has been read for this prereg.** Claim
`may-a-supplier-net-one-fuels-credit-against-the-others-debt` (Lane 0, seat). The knowledge is
`docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md` §8b:
from 22 Jan 2021 the customer has a licence-backed right to offset one contract's credit against
another's debt (SLC 27.8D). The question here is how much of the book that right touches. Today the
DD book and collections keep one balance per supply point and never net (finding
`WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_…_2026-10-18.md` §2, §4 item 3).

## 0. Which run, and what is read

- **The run** is the one `SEAT_PREREG_B11_C35_C34_ON_THE_FIRST_PUBLISHED_DUAL_FUEL_RUN_2026-10-18.md`
  §0 names: the first `run_output_<sha>_20261019T*.json` processed after the 19 Oct 03:00Z publish
  window opens, the one committed as `run_output_latest.json.gz`.
- **The book** is `simulation.dd_balance_book.build_dd_balance_book(bills, opening, closed,
  seek_balance_at_review=<the run's own setting>, **forecast_inputs_from_run(run))`, with `closed`
  built as `review_arms_from_run` builds it (a leg is closed when its last bill predates the run's
  last billed month). A leg's balance is `BalancePoint.balance_gbp` (+ = credit held, − = debit).
- **A dual household** is a `saas.customer_reaction._billing_account_id` with a trajectory on
  **both** legs (`X` and `Xg`). A household with one leg not on DD, or with no opening DD, has one
  trajectory or none and is outside the population. That is what a supplier sees.
- **Opposite signs** means one leg > +£1 and the other < −£1 in the same `month`. The ±£1 band keeps
  rounding noise out.

## 1. What the definition means before anything is counted

The netting question exists only where one leg is in credit and the other is in debit **in the same
month**. Two legs in credit, or two in debit, raise no netting question, however large they are. So
the three readings below count household-months and households with that state, not balance sizes.
The amount netting would move is the smaller of the two magnitudes, `min(credit, |debit|)`.

## 2. Predictions

**N1. Population.** Dual households with both legs on a DD trajectory, over the whole run:
**200–270 (point 240).** Why: 341 of 447 live-book households are dual (finding §5). The DD channel
is drawn once per household with U < 0.72 for electricity and U < 0.75 for gas
(`household_segments.payment_channel_for_customer`), so about 72% have both on DD, which is 245.
Of those, **both legs open at run end: 80–230 (point 150).** That width is honest: I have not read
how many dual homes leave over the window.

**N2. At run end** (the last billed month; `REPORT_END` is 2025-06-07, so May or June 2025), the
share of the run-end population with opposite signs: **0.10–0.35 (point 0.20).** Why it is low:
both legs start at zero on one acquisition date and share one seasonal phase, so the seasonal part
of each balance has the same sign. Without a balance-seeking review, the drift is the review's lag
behind price moves: a DD set on last year's spend over-collects when prices fall. Prices fell on
both fuels through 2023–25, so I expect most households to be in credit on both legs at run end.
**Of the opposite-sign households at run end, more than half have gas in credit and electricity in
debit,** because gas prices fell further.

**N3. Across the run.** Of the household-months where both legs are open on DD, the share with
opposite signs: **0.15–0.40 (point 0.27).** The opposite-sign months with gas in debit fall mostly
in **December to April: at least 60% of them.** The cause is gas's larger winter draw.

**N4. Ever.** The share of the N1 population with opposite signs in at least one month: **0.70–0.98
(point 0.85).** Why: over several years, one leg's small seasonal swing (electricity) and the other's
large one (gas) cross zero at different times, unless the drift is large.

**N5. What netting would move at run end:** the median of `min(credit, |debit|)` over the N2
households is **£15–£90 (point £40).** The electricity leg is usually the smaller magnitude.

## 3. What would refute the reasoning, and what voids a reading

- If **N2 is above 0.35**, the drift is not shared between the fuels as I assumed. The next reading
  is each leg's DD set against its own year's spend, split by fuel.
- If **N4 is below 0.70**, the two legs' trajectories move together more than the seasonal argument
  allows. Read whether the opening DDs are sized from one household figure.
- **Seek-balance switch.** These predictions are for `seek_balance_at_review = False`, which is
  `REVIEW_SEEKS_BALANCE` today (`company/billing/dd_review.py:148`). If the publish run has it on,
  the review pulls each leg toward zero every year. Then the grade reads **both** arms, takes these
  predictions against the off arm, and states the on arm only as a result. For the on arm I predict
  only that N5 falls (point ≤ £30).
- A commit that changes the DD book, the review, the payment-channel draw or the population draw
  between now and the publish run's sha does not void a level reading: these are levels, not
  differences. It does mean the grade must name that sha.

## 4. Grade

To be graded by the reader of the publish run. Write the result **below** this line, and do not
edit the predictions above.

*Instrument, built 2026-10-18 before the publish run and tested on synthetic fixtures only:
`python3 -m tools.dual_leg_opposite_signs <the §0 run>` prints N1 to N5 on both arms. The book's
closed set cannot move these readings (bars are taken after the balance points are written).*

**Book note, 2026-10-19 (seat).** The 19 Oct publish run (`8b6fea024`) predates `30246d6f0`, so its campaign wins are dual on **every** gas home: 172 of 172, 0 gas-only, against about 0.906 at the published rate. The readings here are taken on that always-dual campaign book. It holds about 413 dual households where the split rate gives about 397, roughly 4% fewer. Do not difference a later run's dual counts against these readings as if only the company changed. Reading and prediction: `docs/staging/records/SEAT_PREREG_THE_FIRST_RUN_WITH_SPLIT_CAMPAIGN_HOMES_AGAINST_THE_ALWAYS_DUAL_CAMPAIGN_BOOK_THE_19_OCT_RUN_CARRIES_2026-10-19.md`.

**Grade, 2026-10-19 (seat).** The run is `8b6fea024` (`run_output_8b6fea024_20261019T033010Z.json`,
the file the `2a195224b` publish committed). The instrument is
`python3 -m tools.dual_leg_opposite_signs <that file>`. Run end is 2025-06. The run records no
`seek_balance_at_review` (`null`), and `REVIEW_SEEKS_BALANCE` is False at `8b6fea024`. So the
predictions are graded on the never-seeks arm, and the seeks arm is stated as a result only.

| | never seeks (graded) | seeks (result) |
|---|---|---|
| N1 population / open at run end | 289 / 114 | 289 / 114 |
| N2 opposite at run end | 12 of 114 = 0.105; gas credit + electricity debit 2 of 12 (0.167) | 0.105; 0 of 12 |
| N3 opposite household-months | 2,100 of 11,693 = 0.180; gas-debit months Dec–Apr 0.560 | 0.240; 0.567 |
| N4 ever opposite | 250 of 289 = 0.865 | 0.886 |
| N5 median nettable at run end | £43.05; electricity the smaller 0.917 | £38.88; 0.833 |

- **N1 (200–270): WRONG, too low.** The reading is 289. The DD share I reasoned from held: the run
  has **407** dual households with an opening DD on both legs, and 289/407 is 0.71, against the
  0.72 I predicted. What was wrong is the household count. I took 341 from an earlier live book,
  and this run's campaign is dual on every gas home (book note above). **Open at run end
  (80–230): HELD** at 114.
- **N2 share (0.10–0.35): HELD**, at the bottom edge (0.105). **Direction (more than half have gas
  in credit and electricity in debit): WRONG.** It is 2 of 12. At June 2025, 10 of the 12
  opposite-sign households have *gas* in debit. My reasoning was that gas prices fell further, so
  gas would over-collect. The run end disagrees. I cannot yet say why: 12 households is too few to
  split, and N3's monthly reading is the one to read next.
- **N3 share (0.15–0.40): HELD** at 0.180. **Gas-debit months in Dec–Apr at least 60%: WRONG**, but
  close, at 0.560. 44% of the gas-debit opposite months fall from May to November, so a winter-only
  reason explains just over half of them.
- **N4 (0.70–0.98): HELD** at 0.865. Over the run, 250 of 289 dual DD households hold opposite
  signs at least once.
- **N5 (£15–£90): HELD** at £43.05. Electricity is the smaller magnitude in 11 of 12 (0.917):
  HELD. **The seeks arm (N5 ≤ £30): WRONG.** It falls to £38.88, but not below £30. The seeks arm
  also *raises* the opposite share across the run (0.180 → 0.240). Pulling each leg towards zero
  makes small balances of either sign more common.

**What this says about SLC 27.8D.** The offset right touches 86.5% of dual DD households at some
point, but only about 1 in 10 at any given month-end, and then a median of about £43. The duty is
real for most of the dual book and small in money. That bears on
`honour-the-dual-customers-offset-right-in-collections`: what the remedy needs is a correct offset
when one is asked for, and the book is not owed a large sum.
