**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# B11 slice 2: the late-cut loss is the crisis margin carried forward, and the two books' verdicts drift apart over many commits rather than flipping at one

Claim `b11-second-slice-attribute-the-two-books-verdicts`. The pre-registration, written before
any number here, is
`docs/staging/records/SEAT_PREREG_B11_SECOND_SLICE_ATTRIBUTE_THE_TWO_BOOKS_VERDICTS_2026-10-05.md`.
Built: `run_backtest(..., margin_fit_end_year=)` in `company/analytics/forward_clv.py`, which
takes the per-customer deviation from an earlier window and keeps the level fitted through the
cut. Four tests; four mutations, each red.

## Test 1: the filed hypothesis HOLDS for the arm that tests it

Cut 2022, graded 2023-01 to 2025-06. Paired over the same accounts; negative favours
per-customer.

| book | arm | n | margin diff £/acct (95% CI) | verdict |
|---|---|---|---|---|
| A (`77bf72bab`) | shipped (deviation fitted through 2022) | 48 | +115.4 (+17.1, +213.7) | flat better |
| A | **(b) deviation from 2016–20** | 48 | **−13.5 (−28.5, +1.4)** | cannot tell |
| A | (b′) deviation from 2016–21 | 48 | +43.6 (+13.3, +73.9) | flat better |
| A | (a) literal: whole margin from 2016–20 | 48 | −200.3 (−229.7, −170.9) | per-customer |
| B (tracked blob `d57fe7f88`) | shipped | 71 | +30.8 (−32.2, +93.8) | cannot tell |
| B | **(b) deviation from 2016–20** | 71 | **−28.3 (−46.0, −10.5)** | per-customer better |
| B | (b′) deviation from 2016–21 | 71 | +1.5 (−40.3, +43.2) | cannot tell |
| B | (a) literal | 71 | −78.3 (−127.4, −29.1) | per-customer |

- **Prediction (b), loss disappears: CONFIRMED on both books.** The effect scales with exposure.
  Adding 2021 alone back into the deviation window brings the loss back on A. Where an account
  sits relative to its segment in 2021–22 does not persist into 2023–25. Where it sat in 2016–20
  does, at least enough not to lose. 8 of A's 48 accounts and 15 of B's 71 joined after 2020,
  carry no early deviation, and get their segment's value.
- **Prediction (a), worse than (b): REFUTED.** It is the best arm on both books. That is the
  LEVEL, not knowledge of the customer. At cut 2022 the flat rule forecasts £7,433 against
  £65,722 realised on A, short by £1,214 an account (−1,422, −1,007), because 2021–22 margins
  were near zero. A 2016–20 level is closer to 2023–25. So (a) shows that the flat rule's level
  through a regime change is badly wrong. It says nothing about whether per-customer placement
  helps.
- **What this means for the method:** at a cut inside or just after a regime change, the
  per-customer deviation must come from a window that excludes it. Arm (b) is the rule to carry
  into any per-customer lever graded at a late cut. Who decides which window counts as "the
  regime" is a judgement the backtest cannot make for itself. Here it was taken from the
  published record (the 2021–22 wholesale crisis), not fitted.

## Test 2: where book A and book B part company, across 226 per-commit runs

Each production run on disk from 2026-09-08 to 2026-10-05, graded at cut 2020. Point estimates
are taken where the graded set or the estimate changes:

| from run | graded | margin diff (95% CI) | Brier diff |
|---|---|---|---|
| 09-08 `9a280c876` … 09-11 `f434e28b5` | 68→67 | −40.9 … −39.8 (CI excludes 0) | ≈0 |
| 09-15 `0142fc891` | 65 | −20.4 (−48.3, +7.4) | +0.023 flat |
| 09-16 `edded3973` | 51 | +29.5 (−6.2, +65.1) | +0.122 flat |
| 09-16 → 10-02, 20 further steps | 56–64 | between −4.8 and +32.5, none excluding 0 | ≤ +0.04 |
| 10-02 `ed7e89d0e` (book 164→123 accounts) | 49 | −11.2 (−53.7, +31.3) | −0.013 |
| 10-03 `5583b9121` … 10-04 `7234966b2` | 48 | +31.0 (+5.5, +56.6) flat better | +0.080 flat |
| 10-04 `bd316cdcd` | 51 | +20.2 (−7.3, +47.7) | +0.048 flat |
| 10-05 `70dee3c7c` / `77bf72bab` (book A) | 53 | +1.2 (−26.5, +29.0) | +0.011 flat |
| 10-05 `7a3cdd060` | 56 | −22.2 (−58.3, +14.0) | −0.016 |

- **Prediction (flip at one or two book-changing commits): REFUTED in its strong form.** Two
  steps take the per-customer lead away. At 09-15 the settled book is re-chosen (`3957ba848`, 164
  → 154 accounts). At 09-16 gas-only accounts can leave (`9fd8ca3c3`) and the gas leg rolls onto
  the cap (`dcb8c6d10`). Both change book composition, as predicted. After them, though, the
  estimate walks over about 20 commits in a band from −22 to +32. Several of those steps leave
  the graded count unchanged: `d993a9797` moves −1.9 to +10.2 at n=62, and `a7cdb6fc9` moves
  +6.0 to +21.7 at n=64. The commit-to-commit swing is about the width of the paired interval.
- **Book B is not `fe895db3a`'s run.** Its own stamp says the bytes were landed by `0247f3061`
  (2026-09-01) and their producing commit is unrecorded. It agrees with the 09-08 to 09-11
  hourly runs: per-customer better, with a CI that excludes 0. The first-slice finding's "book
  B, last committed `fe895db3a`" names the commit that last touched the path, not the run.
- **A run's commit stamp does not fully identify the code that ran.** `edded3973` → `2ec310fd8`
  touched no run code (only `tools/stale_copy_refusal.py`), yet graded moved 51→57 and realised
  £59.6k→£75.8k. `producing_commit` is HEAD at process start, and runs execute in the shared
  working tree, which can hold uncommitted bytes. So any single step in this table can carry
  work that is not in the named commit. The band is unaffected; individual attributions are.

## What this can and cannot yet say

- **The cut-2022 loss: attributed.** It is the 2021–22 account deviation carried forward. Taken
  from 2016–20 instead, the loss goes away on both books.
- **The cut-2020 reversal between A and B: cannot be attributed to one variable, and does not
  need to be.** The early-September lead (−40, CI excluding 0) ended over the two days the
  settled book's composition changed. Since then every book this code has produced lies within
  one interval-width of zero, on either side. Both "flat better" and "per-customer better" have
  appeared at single commits, and each would have been read as a verdict. On this book size the
  cut-2020 margin comparison cannot be separated from which ~55 accounts happen to be graded.
- **Book count is therefore the binding variable.** This is evidence for the director's open
  `whether-per-customer-pricing-beats-a-flat` / EP17 row: it is filed against that row, not acted
  on. The default book was not varied (EP17's book seeds are his, and the activation file does
  not exist). The between-commit walk is a lower bound on the spread a book seed would show,
  because successive commits share most of their households.
- **Not published.** DIRECTION.yaml keeps the backtest off the site until it is a quantity. This
  slice confirms that.
