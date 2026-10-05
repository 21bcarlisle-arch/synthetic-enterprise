**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** B11_forward_clv_backtested_on_held_back_history

# The per-customer forward value does not yet beat the flat rule on the current book, and the verdict reverses between runs

Draw: LANE 0 DELIVERY `b11-first-slice-forward-clv-backtest-against-the-flat-rule`, worker tick
2026-10-05. Built: `company/analytics/forward_clv.py`, tested in
`tests/company/analytics/test_forward_clv_backtest.py` (8 tests; the leakage, censoring,
tail-fold and pooling guards were each mutated and each mutation went red).

## What is forecast

For each billing account (fuels merged) on supply in December of the cut year: the sum over the
held-back months of P(still supplied) × the monthly settlement-record net margin. Graded against
what the account actually earned in those months. Margin here is before cost-to-serve and bad
debt, because the monthly ledger carries neither. The departure is all-cause. **Departures
cannot yet be split into switches and moves**, and that limitation is carried on every result.

- **Per-customer:** the account's own monthly margin, shrunk toward its segment's by an
  empirical-Bayes weight n/(n+k), where k is within-account variance over between-account
  variance in the fit years (the book sets it, nobody picks it). The hazard is a life table by
  contract year of tenure, multiplied by the segment's observed/expected exit ratio.
- **Flat:** one monthly margin and one monthly hazard per segment (resi/SME × elec/gas/dual).

**Cut year 2020.** It is the last full year before the 2021–22 crisis, and the hardest honest
test this book allows. Grading is paired over the same accounts with a normal 95% interval on
the mean difference. Negative favours per-customer.

## Results

Book A: `docs/reports/run_output_77bf72bab_20261005T054613Z.json` (the shared tree's current
`run_output_latest.json`), cut 2020, 53 accounts graded:

| | per-customer | flat | difference (95% CI) | verdict |
|---|---|---|---|---|
| abs margin error £/acct | 857.7 | 856.5 | +1.2 (−26.5, +29.0) | cannot tell |
| departure Brier | 0.271 | 0.260 | +0.011 (+0.0004, +0.022) | **flat better** |

Aggregate: realised £38,458. Forecast £27,312 (per-customer) and £26,025 (flat). Mean bias
−£210/acct (−663, +242) and −£235/acct (−675, +206): both short, and neither is distinguishable
from zero. Departures were 22 realised against 27.0 ± 3.6 and 26.3 ± 3.6 expected.

Book B: the copy of `run_output_latest.json` tracked at HEAD (blob `d57fe7f88`, last committed
`fe895db3a` 2026-09-09), cut 2020, 72 graded:

| | per-customer | flat | difference (95% CI) | verdict |
|---|---|---|---|---|
| abs margin error £/acct | 628.8 | 688.3 | −59.4 (−89.3, −29.6) | **per-customer better** |
| departure Brier | 0.174 | 0.184 | −0.009 (−0.029, +0.011) | cannot tell |

Cut sweep on book A, as (margin verdict / departure verdict): 2018 tie/tie, 2019 tie/tie,
2020 tie/flat, **2021 flat by £74 (38, 111)/flat**, **2022 flat by £115 (17, 214)**/tie. The later
the cut, the worse the per-customer margin does.

## What this means, and what I cannot yet say

- **The loss to the flat rule is the result on the current book.** At the stated cut, knowing
  each customer adds nothing to the margin forecast and slightly worsens the departure forecast.
- **I cannot yet say why the two books disagree.** They differ in run code, in world, and in
  book size (53 accounts graded against 72). That is more than one variable, so no cause is
  attributed. The one-variable version would be the same code on two seeds, then the same seed
  on the two commits.
- **This hypothesis is unverified, and is recorded so it can be refuted:** the per-customer
  margin gets worse as the cut moves into 2021–22 because its credibility weight (~0.8 at
  n≈60 months, k≈12–14) carries each account's crisis-year margin forward, and that margin does
  not persist. A test of it: fit the per-customer margin on 2016–2020 only, with cut 2022, and
  check whether the 2022-cut loss disappears.
- **Departure grading is all-cause.** No lever that acts on switching alone can be judged
  against this hazard until the book records the reason supply ended.

## Continuation

The module has no production caller yet. It is frozen into `docs/design/orphan_baseline.json`
as deliberately dormant, in the same commit. Publishing the backtest on the site (cut, both
verdicts, the bound) is the next increment. So is a seed sweep that would let the two books'
disagreement be attributed.

## Disposition (2026-10-05)

Answered by `docs/staging/SEAT_FINDING_B11_THE_LATE_CUT_LOSS_IS_THE_CRISIS_CARRY_FORWARD_AND_THE_TWO_BOOKS_ARE_A_WALK_NOT_A_FLIP_2026-10-05.md`.
The hypothesis held: the 2022-cut loss goes when the deviation comes from 2016–20. The two
books' disagreement is a walk over about 20 commits, not a single flip. Correction: book B is
not `fe895db3a`'s run. Its stamp says `0247f3061` landed the bytes, and the producer was not
recorded.
