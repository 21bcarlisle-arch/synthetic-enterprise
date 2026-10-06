**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# B11 slice 3: the deviation window's end, read from the wholesale record, keeps slice 2's result

Claim `b11-deviation-window-from-the-published-regime-boundary`. Pre-registration, written before
any number here:
`docs/staging/records/SEAT_PREREG_B11_THIRD_SLICE_DEVIATION_WINDOW_READ_FROM_THE_PUBLISHED_RECORD_2026-10-06.md`.
Its rule was corrected once, in the same session and before any backtest ran. The correction sits
in that file beside the first draft.

## What was built

- `company/analytics/forward_clv.py::regime_boundary_month`: the first month, on or after the
  cap began (2019-01), in which wholesale gas sets an all-time high over the whole record before
  it. It reads nothing past the cut. `run_backtest(..., wholesale_gas_by_month=)` ends the
  deviation window the month before that. With no high by the cut, the window is the fit window,
  which is the rule as shipped. A chosen year and a read series together are refused.
  `backtest_run_output` takes the series from its caller. *Corrected at landing: the built version imported `LiveSimInterface` inside `forward_clv` to read it by default, and `tools/company_network_isolation` refused that as a new route out of the company. The seam's price loader can fall back to a live fetch. The caller now passes `SimInterface.monthly_wholesale_prices("gas")`.* `Backtest.margin_deviation_window_reason` says
  which source set the window.
- `LiveSimInterface.monthly_wholesale_prices(fuel)`: the same published price history
  `get_forward_price` already reads, as monthly means. Observable; any participant can download
  it.
- On the record held, the boundary is **2021-06** (27.5 against 2018-09's 25.4), so the window
  ends **2021-05**. The anchor is not load-bearing: 2018-10, 2019-01, 2020-06 and 2021-05 all
  read the same month.
- Two tests. Four mutations, each red: the bar set before the anchor, the cut's read limit, the
  minus-one, and ignoring the boundary. A fifth line, the running-max update inside the loop, was
  an equivalence. The loop returns at the first new high, so the update could never change
  anything. It was deleted rather than tested.

## Results against the predictions

Paired over the same accounts; negative favours per-customer.

| book | cut | deviation window | n | margin diff £/acct (95% CI) | verdict |
|---|---|---|---|---|---|
| A (`77bf72bab`) | 2020 | read → fit window (no high by the cut) | 53 | +1.2 (−26.5, +29.0) | cannot tell |
| A | 2022 | shipped (through 2022-12) | 48 | +115.4 (+17.1, +213.7) | flat better |
| A | 2022 | **read: through 2021-05** | 48 | **−2.1 (−19.5, +15.4)** | cannot tell |
| A | 2022 | chosen 2020 (slice 2) | 48 | −13.5 (−28.5, +1.4) | cannot tell |
| B (blob `d57fe7f88`) | 2020 | read → fit window | 72 | −59.4 (−89.3, −29.6) | per-customer better |
| B | 2022 | shipped | 71 | +30.8 (−32.2, +93.8) | cannot tell |
| B | 2022 | **read: through 2021-05** | 71 | **−28.8 (−46.8, −10.7)** | per-customer better |
| B | 2022 | chosen 2020 (slice 2) | 71 | −28.3 (−46.0, −10.5) | per-customer better |

1. **Cut 2020 identical to the shipped rule on both books: CONFIRMED** to the last digit.
2. **Book A, cut 2022, at or below +15 and straddling zero: CONFIRMED** at −2.1.
3. **Book B, cut 2022, at or below 0: CONFIRMED** at −28.8, with a CI that excludes 0.

Departure Brier is unchanged in every arm, as it must be. The window moves only the margin
deviation.

## How near the edge the read window sits (descriptive, after the fact, not a selection)

Cut 2022, margin diff by the deviation window's last month:

| last month | 2020-12 | 2021-02 | 2021-04 | **2021-05** | 2021-06 | 2021-08 | 2021-09 | 2021-10 | 2021-12 |
|---|---|---|---|---|---|---|---|---|---|
| A | −14 | −9 | −7 | **−2** | +1 | +6 | +12 | +21 (−2, +44) | +44 (+13, +74) |
| B | −28 | −29 | −29 | **−29** | −28 | −26 | −26 | −22 (−43, +0) | +1 |

The loss comes back only when the window takes in Oct–Dec 2021, the peak of the crisis. Every
window end from 2020-12 to 2021-09 leaves A at "cannot tell" and B at per-customer better. So
slice 2's conclusion does not hang on its hand-picked month. **The read rule makes slice 2
evidence.** The deviation must exclude the crisis months, and a boundary taken from the
published wholesale record does that without looking at the answer.

## What this does not say

- It does not say per-customer beats flat. On book A, at both cuts, the answer is "cannot
  tell". On ~50 graded accounts, book count is still the binding variable. That is filed against
  the director's open `whether-per-customer-pricing-beats-a-flat` / EP17 row and not acted on
  here.
- The series is the IMF/FRED TTF proxy for NBP (`sim/gas_prices_history.py`), not NBP itself.
  The boundary month would need re-reading on a true NBP series.
- Not published. `forward_clv` still has no production caller. B11 stays at L1.

## How it landed, and the earlier slice-3 commit it supersedes

The invocation that built this ended (02:22Z) before its landing finished. `fork_salvage`
preserved the bytes in `dd8e522d0`. A later draw of the same claim re-ran all four book/cut
cells from those bytes, got the same numbers to the last digit, and landed them unchanged
apart from this section. An earlier slice-3 commit, `c5770c404` (00:41Z), sits on fork branch
`worktree-agent-ac24ddfbb7f67a9e9` and is NOT on origin. It took the regime's START from the
NAO's "since July 2021" and carried the end as a named gap. This rule supersedes it: the
pre-registration above rejects the commons' prose datings because they disagree with each
other by six months. Do not promote `c5770c404`.
