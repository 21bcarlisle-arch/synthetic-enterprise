**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# Pre-registration: B11 slice 3, the deviation window's end read from the published wholesale record

Written 2026-10-06 before any number for the new window was computed. Claim
`b11-deviation-window-from-the-published-regime-boundary`. Results go in a separate finding. This
file is not edited after the runs.

## Why slice 2's window is a fitted choice

Slice 2 (`4e4637853`) took each account's margin deviation from 2016-2020. That gave -13.5
(-28.5, +1.4) at cut 2022 on book A. With 2016-2021 it gave +43.6. The year end was picked after
both were seen, so the slice-2 gain is a choice made on the backtest's answer.

## The rule, chosen before the run and not tuned

**The regime ends in the month before wholesale gas, on or after the default tariff cap began
(2019-01), first sets an all-time high: a monthly price above every month of the whole record
before it (the series starts 2016-01).**

*Corrected before any backtest ran (same session): the first draft said "above every monthly
price since 2019-01". That is a different rule. Its maximum is 2019-01's own 19.1, which 2021-01
(19.5) beats, so it reproduces slice 2's hand-picked 2020-12 by a margin of 0.4 and moves with
the anchor. The all-time-high rule is the one computed below and the one that is anchor-robust.* The deviation window runs from the book's
first month to that month. If no such month falls on or before the cut, the window is the fit
window, which is the rule as first shipped.

- Series: the company's own observable gas history (`SimInterface` historical prices, the IMF/FRED
  TTF proxy, monthly). It is public and was published before each cut.
- Anchor: the cap's launch, 2019-01-01 (Ofgem's published window schedule in the commons). **The
  anchor is not load-bearing.** The highest price in the record before 2021 is 2018-09. So any
  anchor from 2018-10 to 2021-05 gives the same first record month.
- What the rule reads (computed before this file, from the series alone; anchors 2018-10,
  2019-01, 2020-06 and 2021-05 all give the same month): the first month above
  the post-anchor maximum is **2021-06**. The deviation window ends **2021-05**.

Rejected before running, with the reason:
- *A first cap move larger than every move before it* (cap-window artefact): with only 6 prior
  moves it fires on noise. Gas Oct-2019 (-11.8% log) already beats Apr-2019 (+10.4%).
- *A running record over the whole series from 2016-01*: it fires on 2016-18 records that a
  three-year-old series always produces.
- *A high since the anchor only* (the first draft's wording): see the correction above.
- The commons' prose datings ("wholesale surge Jan-Sep 2021", `ofgem_regulation.md`; "failures
  Jul 2021-May 2022", `svt_rates_active_passive_2016_2025.md`) disagree with each other by six
  months. They are prose, not a series.

## Predictions

Paired over the same accounts; negative favours per-customer. Books: A =
`docs/reports/run_output_77bf72bab_20261005T054613Z.json`, B = blob `d57fe7f88`.

1. **Cut 2020, both books: identical to the shipped rule, to the last digit.** By construction:
   no month up to 2020-12 is above the post-anchor maximum. This is a control on the
   implementation, not a claim about the world.
2. **Cut 2022, book A, window to 2021-05:** the point estimate lies between slice 2's -13.5 and
   +43.6, at **+15 or below**, and the interval straddles zero ("cannot tell"). Confidence about
   60%. Reasoning: Jan-May 2021 gas sat inside the 2018 range, so the sim's retail margins in
   those months should not yet be crisis-shaped, and five months of ~65 dilute little.
   **Refuted if** flat is better with a CI that excludes 0. That would mean the early-2021
   months already carry the non-persistent deviation, and slice 2's -13.5 depended on cutting
   them out by hand.
3. **Cut 2022, book B, window to 2021-05:** point estimate at or below 0 (slice 2: -28.3 for
   2016-20, +1.5 for 2016-21). Confidence about 55%.
