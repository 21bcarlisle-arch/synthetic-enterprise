**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` — direction item `b11-the-within-segment-term-says-whether-per-customer-clears-flat`

# Pre-registration: the within-segment term on 8b6fea024 and ad8afadc5, at 2020, 2022 and 2023

**Written 2026-10-19 18:42 BST, before the term existed in code and before any cell below was read.**
Subject: `docs/staging/WORKER_FINDING_THE_SWITCH_KEYS_WHOLE_BOOK_GAIN_OVER_FLAT_WAS_TWO_THIRDS_FLATS_OWN_INVERTED_GAS_SEGMENT_2026-10-19.md`.

## What is measured, said before it is counted

The reading is `backtest_run_output(path, cut, switch_on_default=True, rescale_over="fit_window")` —
the key the finding graded, unchanged. **The within-segment term** is the key's AUC minus flat's AUC
over departer–stayer pairs whose two accounts share a `segment` label. Flat gives one p per segment,
so its within-segment AUC is exactly 0.5 and the term is the key's own information.

**The interval is a stratified DeLong, not a bootstrap.** Segments hold disjoint accounts, so their
AUC estimates are independent; the term is the pair-weighted mean of per-segment paired differences
(weight `m_s·n_s / Σ m·n`), and its variance is `Σ w_s² var_s`, each `var_s` the paired DeLong this
module already uses. That is deterministic (no seed in a published figure), reuses the code the
whole-book figure is graded with, so the two intervals differ only in which pairs they count, and
costs nothing. Its cost: weights are taken as fixed given the segment counts, and a segment with
fewer than two departers or two stayers has no DeLong variance. **Those segments are excluded from
the term and counted beside it**, not silently folded in.

Runs: `run_output_8b6fea024_20261019T033010Z.json` (published 19 Oct) and
`run_output_ad8afadc5_20261019T132751Z.json` (**unpublished**, the first run with split campaign
homes, read from the shared tree).

## Predictions

Known before writing: 8b6fea024 at 2023, within point +0.075 (the finding's own decomposition).
That point is not a prediction; its interval is.

- **P1.** 8b6fea024 2023: half-width 0.08…0.13, lower bound below 0. **Cannot tell.**
- **P2.** 8b6fea024 2020 and 2022: each point in −0.05…+0.10, each **cannot tell**.
- **P3.** ad8afadc5 2023: point within ±0.05 of +0.075; **cannot tell**.
- **P4.** ad8afadc5 2020 and 2022: **cannot tell** each.
- **P5.** Of the six cells, none clears on the within term. B11's statement will be
  "cannot tell at this width". (~70%: one cell clearing by chance or by a real effect is the
  rest.)
- **P6.** ad8afadc5 returns gas-only homes to the book, so flat's cross-segment ordering degrades
  again: at 2023 on ad8afadc5, whole-book difference minus within term is > 0. (~60%.)
- **P7.** The within half-width is at least the whole-book half-width in ≥5 of the 6 cells
  (fewer pairs; ~65%).
- **P8.** Pairs excluded (segments with <2 departers or <2 stayers) are under 10% of the
  within-segment pairs in every cell.

## Grade

*Appended below after the reading. No line above is to be edited.*

### Read 2026-10-19 ~18:55 BST (worker). Nothing above was edited

The term `Backtest.departure_ranking_within_segment` (stratified DeLong) and its control landed with
this grade. The reading was `backtest_run_output(path, cut, switch_on_default=True,
rescale_over="fit_window")` with today's code, and the script was a loop printing both fields.

| run | cut | graded / departed | whole: key − flat | within: key − flat | within pairs / excluded / cross |
|---|---|---|---|---|---|
| 8b6fea024 | 2020 | 184 / 75 | +0.046 (−0.011, +0.102) | **+0.061 (+0.002, +0.120)** | 4,772 / 5 / 3,398 |
| 8b6fea024 | 2022 | 192 / 42 | +0.032 (−0.036, +0.100) | +0.035 (−0.038, +0.109) | 3,565 / 0 / 2,735 |
| 8b6fea024 | 2023 | 201 / 32 | +0.075 (−0.013, +0.162) | +0.075 (−0.016, +0.165) | 3,264 / 0 / 2,144 |
| ad8afadc5 *(unpublished)* | 2020 | 184 / 75 | +0.046 (−0.015, +0.107) | **+0.065 (+0.005, +0.125)** | 4,489 / 0 / 3,686 |
| ad8afadc5 *(unpublished)* | 2022 | 192 / 42 | +0.030 (−0.041, +0.101) | +0.036 (−0.038, +0.109) | 3,459 / 0 / 2,841 |
| ad8afadc5 *(unpublished)* | 2023 | 201 / 32 | +0.074 (−0.016, +0.164) | +0.074 (−0.015, +0.164) | 3,168 / 0 / 2,240 |

The segments graded are `resi dual` and `resi electricity` (and `resi gas`, 2 departers and 6 stayers,
on ad8afadc5 at 2020 only). `resi gas` is excluded in the other five cells: it had 1 departer at 2020
on 8b6fea024 and none at the later cuts.

- **P1 HELD.** Half-width 0.090, lower bound −0.016. Cannot tell.
- **P2 HALF WRONG.** Both points are in range (+0.061, +0.035). **2020 clears**, by a lower bound of
  +0.002. 2022 cannot tell.
- **P3 HELD.** +0.074.
- **P4 HALF WRONG.** 2020 clears (+0.005). 2022 cannot tell.
- **P5 WRONG.** Two of the six cells clear, both at 2020.
- **P6 WRONG.** At 2023 on ad8afadc5 the whole-book and within terms are equal (+0.074 each). The
  split campaign homes did not put a gas-only segment back into the graded book at the cut: `resi gas`
  has no departer there. On both runs flat's cross-segment ordering is at or above chance at every cut.
  At 2020 the cross pairs favour **flat**: within exceeds whole by 0.015 and 0.019.
- **P7 HELD.** The within half-width is at least the whole-book one in 5 of 6 cells. The exception is
  ad8afadc5 2020, at 0.060 against 0.061.
- **P8 HELD.** At most 5 of 4,772 pairs are excluded.

### The B11 statement

**Per cut: 2020 clears; 2022 and 2023 cannot tell at this width.** Across the three cuts the statement
is **"cannot tell at this width"**, for three reasons, all stated after the reading:
1. The 2020 clearance is marginal on both runs (lower bounds +0.002 and +0.005).
2. The two runs are not two observations. They grade the same 184/192/201 accounts with
   near-identical counts, so they are one book read twice.
3. Three cuts were read. A 98.3% interval (Bonferroni over three) puts 2020's half-width at ≈0.072,
   wider than the +0.061 point.

The sign is positive in all six cells, and the key's within-segment AUC is 0.535–0.575 at every cut.
That is weak, consistent evidence of per-customer information, not a demonstrated clearance. The
inverted-segment credit the finding named is absent on these books: whole ≈ within at 2022 and 2023,
and whole < within at 2020. **So on the dual books the whole-book figure under-states the key at
2020 rather than flattering it.**

The next width-reducer is the varied-draws grade
(`PREREG_B11_PER_CUSTOMER_AGAINST_FLAT_ON_VARIED_DRAWS_2026-10-16.md`), read on the within-segment
term. Independent books are what can shrink this interval. A second read of the same book cannot.
