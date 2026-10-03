# Result: same-day renewals do not covary, so flow does not cause the variance, and five to nine accounts set the sd

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` ·
**Claim:** `flow-how-many-renewal-decisions-are-independent`

Written 2026-10-03. Nothing new was run for the measurement. It reads only artefacts already on disk:
`/var/tmp/se-depthwidth-out/depth_{2019,2022}_*.json` (six seeds each), `width125_61001_61002.json`
(two seeds), and `/var/tmp/se-ab6-out/run{P1,P2,X1}.json` (the six 2025 seeds behind the 1.02) plus
`runB6.json`. All of them are commit a322166cc, world digest 39a192ce04c1eda8. The scripts are in
`/var/tmp/se-flow/` (`deff.py`, `run.py`, `run2.py`).

## What "flow" is taken to mean here

The director named flow as one of three causes of the selection residual's noise. Here it means
**the timing of the book's renewals through the year**: whether renewals that fall on the same
day, or in the same batch, move together and so count as fewer independent decisions than there
are rows. It does NOT mean book width (more accounts). The width125 family addresses width, and
two seeds cannot grade a variance.

## The book was batched: renewals by calendar month (value arm, mean per seed)

| family | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| to 2019 | 12 | 13 | 15 | 13 | 4 | 6 | 6 | 5 | 2 | 0 | 0 | 4 |
| to 2022 | 17 | 17 | 22 | 14 | 6 | 7 | 9 | 9 | 2 | 1 | 0 | 5 |
| width125 | 31 | 34 | 24 | 18 | 18 | 15 | 22 | 24 | 3 | 2 | 0 | 6 |
| 2025 (ab6) | 22 | 19 | 26 | 14 | 11 | 10 | 12 | 13 | 5 | 1 | 0 | 7 |
| B6 | 21 | 18 | 14 | 18 | 15 | 10 | 7 | 12 | 6 | 1 | 0 | 6 |

By acquisition cohort (2025, per seed): SYN-2016 drawn founders 63, hand-authored cast 16,
PROS-2016..2024 campaign wins 12/11/3/9/8/10/5/3/2. On every family, September to November is
almost empty. That is the founder truncation de903961c removed at 03:01 today. These artefacts
predate it. The cast also stacks on 04-01 and 12-31 by hand.

Unit of clustering: a renewal on a 12-month term recurs on the same anniversary day every year.
The 2025 book has 73 accounts that ever renew, on 59 distinct anniversary days: 47 days hold one
account, 10 hold two and 2 hold three. The 93 accounts that never renew carry 0.0-0.1% of the
variance.

## Prediction (filed 2026-10-03, before any date-clustered figure was computed)

Already seen when this was written, so it is not predicted: renewal dates by month and cohort (the
table above), and the account-level design effect with this estimator: 1.022 on the six 2025
seeds (reproduces the pre-registration's 1.02 exactly), 0.955 on the six 2019-end seeds, and
**2.009 on the six 2022-end seeds**.

The estimator: per family the book is the same on every seed, and only the churn rolls differ.
For account i, V_i is the variance of its selection contribution across seeds. D_account =
Var(S)/sum V_i. D_date = sum over clusters of Var(cluster sum)/sum V_i. A cluster is every
account whose renewal falls on one anniversary day (mm-dd of its first renewal, and a 12-month
term keeps that day every year). D_date - 1 is the within-date covariance share, and
D_account - D_date is the between-date share.

- **F1.** D_date lies in [0.8, 1.3] on the 2025 family. Each account gets its own roll. What a
  date shares is the market price, and that moves the MEAN of a split, not its spread. There
  are about two accounts per anniversary day, so even a strong within-date correlation can only
  add a fraction.
- **F2.** On the 2022 family, where D_account is 2.0, less than half of the excess sits within
  dates (D_date - 1 < 0.5). In 2022 the covariance is between dates (one regime moving every
  account), not within one day's batch.
- **F3.** D_month (calendar month of the anniversary) lies in [0.7, 1.6] on 2025.
- **F4.** The effective number of independent decisions per seed, renewal decisions / D_date,
  is within 25% of the raw count on 2025 (about 140). The count that actually sets the sd is the
  variance-weighted Kish count (sum V)^2 / sum V^2. It is far smaller, at most 15. Variance is
  CONCENTRATED in a few large split accounts, and not CORRELATED across them.
- **F5.** So "flow", in the sense of batched dates inflating variance, does not hold. Spreading
  acquisition through the year, either uniformly (de903961c) or by the DESNZ monthly weights,
  will not reduce the residual's sd by more than 10% beyond seed noise. Pre-registered for the
  first post-change family: sd(S) / sqrt(sum V_i) stays within the permutation null's 90% band.
  Any change in sd(S) comes from WHICH households are founders, through V_i, and not from dates.

*(The prediction section above is verbatim. It was written at 2026-10-03T02:41:57Z with sha256
`74c2185b469cecbc43cf1aca5fff80366286f6953782e5fec18748d8f8c3b1ed`, before `run.py` first
computed a clustered figure.)*

## Result

The 90% band beside each figure is a permutation null: each account's six seed values are
shuffled independently, which keeps every V_i and destroys every covariance (2,000 draws).

| family (6 seeds) | D_account (null 90%) | **D_date** (null 90%) | D_month (null 90%) | D_cohort | renewal decisions / seed | **effective independent / seed** | Kish variance-effective accounts |
|---|---|---|---|---|---|---|---|
| 2025 | 1.022 (0.25-2.12) | **0.993** (0.89-1.09) | 0.731 (0.72-1.35) | 1.010 | 140 | **141** | **8.6** |
| to 2019 | 0.955 (0.25-1.99) | **0.737** (0.76-1.23) | 0.641 (0.72-1.30) | 0.843 | 80 | **108** | **4.9** |
| to 2022 | 2.009 (0.27-2.08) | **0.970** (0.89-1.11) | 0.881 (0.76-1.30) | 1.331 | 109 | **112** | **4.2** |

D_date uses the pre-registered key, each account's first-renewal mm-dd. A robustness re-key on
the mode of every logged renewal mm-dd, which dates one more account, gives
0.944 / 0.737 / 0.922.

**Where the within-date covariance comes from.** It is not batching. The largest within-date
term in every family is **C5 with C5_2**, an account and its own successor on 12-31 (2·cov/ΣV =
-0.05, -0.165 and -0.065). That pair is mechanically anti-correlated, because C5_2 exists in an arm
only when C5 left it. That pair alone puts 2019 below its null band. The other cast pairs on
04-01 (C6, C6_2, C8) net to about zero. Excluding successor pairs, same-day covariance is
indistinguishable from zero in all three families.

## Grading

- **F1 HELD.** D_date is 0.993 on 2025, inside [0.8, 1.3] and inside its own null band.
- **F2 HELD.** On 2022, D_date - 1 = -0.03, so none of the excess sits within a date. But the
  premise behind F2 was weaker than I wrote it: **2022's D_account of 2.009 is itself inside its
  null band (0.27-2.08)**. At six seeds, the account-level design effect cannot tell 2.0 from 1.0.
  The same holds for the 1.02 the split-path pre-registration relied on. Its null band is
  0.25-2.12, so "1.02 hints that same-day renewals do not inflate variance" was a hint the
  estimator could not give. The date-clustered estimator can, because it sums only within-cluster
  pairs, and its null band is about ±0.1.
- **F3 HELD, at the edge.** D_month is 0.731 on 2025, at the lower edge of both my range and its
  null.
- **F4 HELD.** Effective independent decisions per seed = decisions / D_date = **141 of 140** on
  2025 (108 of 80 and 112 of 109 elsewhere, all above the raw count because D_date < 1). The
  Kish variance-effective count is **8.6** (4.9, 4.2), at or under 15. In 2025 PROS-2016-0098
  alone carries 26% of ΣV, and in 2022 it carries 44%.
- **F5** is the pre-registered prediction for the change below and is not yet graded.

## Answer to the director

**Of your three causes, flow is the wrong one for variance.** Renewals that fall on the same day
do not move together. Each seed holds about 140 renewal decisions (2025 book) and about 140 of
them are independent. The residual is noisy because its variance is **concentrated**: five to
nine accounts' worth of independent coin flips per seed, one account carrying a quarter to a
half. Those are the split accounts, where the shared roll falls between the two arms' P(stay)
and one arm keeps a whole remaining life that the other loses. Spreading the dates does not
touch that. Changing how much one split is worth (a split-path control variate, the
pre-registration of 2026-10-03), or holding more such accounts (width), does.

## What was built anyway, and why it is not a result-driven change

The book WAS batched, and the batching contradicts the published record, so it is a fidelity
defect on its own terms. That is decided on the DESNZ series, not on any company result. This
result says it should not move the residual's sd, which is the opposite of a reason chosen to
flatter it.

- de903961c (03:01, another landing on this same question) removed the founder truncation.
- **This landing** draws each acquisition day in proportion to that year's published GB domestic
  switches by month (DESNZ QEP Table 2.7.1, combined electricity + gas transfer events, each year's
  own row; `simulation/population_draw.GB_DOMESTIC_TRANSFERS_BY_MONTH_THOUSANDS`). It is turned
  on for the drawn founders (2016: January is the trough at 437k, October the peak at 871k) and the
  trickle (2021-2025). The uniform draw is still consumed, so every other attribute is
  byte-identical. Measured on 109 candidates, only the acquisition date and the premise's EPC
  lodgement date move, because the lodgement date is drawn relative to it. Thinning is positional,
  so the founders are **the same households**, on new dates. A year outside 2016-2025 is refused
  rather than given an invented shape.
- Drawn founders by month after the change, seed 61001: [4,8,3,3,10,4,4,5,4,5,5,7] (62 founders,
  so the 2016 shape is only visible pooled).
- Controls: `tests/simulation/test_acquisition_dates_follow_the_published_switching_months.py`,
  mutation-proven. Dropping the founders' flag reds the caller control. A flat year reds the
  month-share control on all three years. Not consuming the uniform draw reds only-the-date-moves.

**F5, restated for the first post-change family:** sd(S)/sqrt(ΣV_i) stays inside the permutation
null's 90% band, and D_date stays inside its null. A change in sd(S) against these families is
attributed to V_i (which households split, and when in the price path), never to the dates.

**Not done, named:** the campaign's own wins (PROS-*) are also front-loaded, with first renewals
by month [7,5,3,3,3,2,2,2,2,1,0,1]. When a campaign runs is the company's decision, and when a
prospect is in the market is the world's. Whether the world should gate a win on the household
being in-market in that month is a separate fidelity question, not one taken here. The
hand-authored cast's 04-01 / 12-31 stacking is narrative core and is untouched.

The split-path pre-registration file this cites
(`SEAT_PREREG_A_SPLIT_PATH_CONTROL_VARIATE_FOR_THE_SELECTION_RESIDUAL_2026-10-03.md`) is
untracked in the shared tree, held by the lane that wrote it. It is not landed here.
