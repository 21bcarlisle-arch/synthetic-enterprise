**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# PRE-REGISTRATION — EP1's tenure horizon on the book's life table by tenure year

Filed 2026-10-01 at `627f05756`, before the change has run on any graded row. It serves
`docs/staging/SEAT_FINDING_EP1_ALL_CAUSE_EXIT_HAZARD_IS_RIGHT_BY_DEFINITION_AND_A_YOUNG_BOOK_SHOWS_ITS_CONSTANT_HAZARD_IS_NOT_2026-10-01.md`.

## What the thing is (said before it is measured)

H2 asks how long THIS customer stays from where it now is in its tenure. The book's exits are not
spread evenly over a tenure: they cluster at anniversaries. So the hazard is indexed by **tenure
year k**, counted from the account's `acquisition_date` month (a fact known at signing):

- Tenure month i = months since the acquisition month. **Year 1 is months 0–12 and year k ≥ 2 is
  months 12(k−1)+1 … 12k.** The anniversary month belongs to the year it closes, because a term
  starting on the 1st has its last settled month the month BEFORE the anniversary and a mid-month
  term the anniversary month itself (`observed_book_renewals` already counts both as "at" the
  anniversary). Splitting them would put half the renewal spike in the following year.
- **Monthly product-limit, not exits ÷ exposure.** At month i, n_i = accounts whose settled span
  covers i; d_i = ceased accounts whose last settled month is i. h_k = 1 − Π_{i∈k}(1 − d_i/n_i).
  The item's literal "exits in year k over exposure in year k" was printed at real inputs first and
  rejected: an account censored by the snapshot mid-year contributes its quiet in-term months to the
  denominator without ever reaching the anniversary, which is the young-book defect the constant
  hazard had, moved one year along. The 2017 book under that reading: y2 = 3 exits / 44.5 years;
  under the product-limit y2 is 0.046 on months that never include a second anniversary.
- **A year is OBSERVED only when every one of its months has an account at risk.** The last year a
  snapshot reaches is censored before its anniversary in almost every snapshot (2017 y2 0.046,
  2020 y5 0.033 — both below every complete year). Years beyond the last complete year take the
  last complete year's hazard, and the output says so. With no complete year (2016) H2 is blank
  under a named reason; nothing falls back to a number.
- Forward year t for an account whose next unsettled month is j takes year(j) + t − 1.
- Survival is the product of the year hazards. The term convention is unchanged: the expected
  remaining tenure Σ_{t≥0} S(t), which is exactly 1/h under a constant hazard, with the same
  continuous fractional year the closed form uses — so a constant table reproduces
  `survival_discounted_value_gbp` exactly (a test, not a claim).

Real-book table (product-limit, `*` = incomplete, at `/tmp/ep1bk/run.pkl`):

    2017 y1 .154  y2 .046*
    2018 y1 .155  y2 .192  y3 .099*
    2019 y1 .150  y2 .191  y3 .272  y4 .109*
    2025 y1 .121  y2 .178  y3 .187  y4 .165  y5 .211  y6 .053  y7 .000  y8 .136  y9 .191  y10 .000*

## Predictions — the one-variable arm in `/tmp/se_ep1_measure.py`

Same run artefact (`b1b4c284e`, 69 graded rows), each row's own margin, ONLY the hazard changed;
the constant all-cause arm is re-run through the same machinery so the comparison is one variable.

1. **Overall gap falls below the constant all-cause arm (1.558) and below the per-anniversary arm
   (1.437): 1.20–1.45.**
2. **2017 (51 rows) improves against the constant arm**: its tail is y1 0.154 instead of 0.109,
   about the per-anniversary 0.145, so its MAE lands within 10% of the per-anniversary arm's 2017 MAE.
3. **2018–2022 rows improve or hold against the constant arm** (years 2–4 run 0.17–0.27, above the
   pooled ~0.15–0.18, so values fall, and the published values over-state).
4. **2016 (3 rows) goes blank** (no complete tenure year) and the arm keeps the published belief for
   them; reported both with and without them.
5. **Spearman moves by more than ±0.02 for the first time** — the hazard now varies by each account's
   own tenure position. Direction: low confidence; I predict up.

## RESULT, 2026-10-01, written beside the predictions and not over them

`/tmp/se_ep1_measure_lt.py` (the arm script with the life-table arm added; the constant arm now runs
through `survival_discounted_value_by_year_gbp` with a one-element table, which the reduction test
proves identical to the closed form). Same artefact, 69 graded rows, g0 356.6.

| arm | gap | MAE £ | Spearman | \|b\|>\|t\| |
|---|---|---|---|---|
| published (0.05 belief) | 2.364 | 843.0 | +0.110 | 60/69 |
| per-anniversary | 1.437 | 512.5 | +0.077 | 55/69 |
| all-cause constant | 1.558 | 555.6 | +0.096 | 54/69 |
| **life table (this)** | **1.275** | **454.6** | **+0.095** | 52/69 |

Without 2016's 3 rows: per-anniversary 1.407, constant 1.486, life table 1.238 (n 66).

| belief year | n | constant MAE | life-table MAE | per-anniversary MAE |
|---|---|---|---|---|
| 2017 | 51 | 532.4 | 449.3 | 463.8 |
| 2018 | 3 | 376.6 | 220.4 | 446.7 |
| 2019 | 3 | 395.2 | 245.1 | 552.0 |
| 2020 | 4 | 283.1 | 166.6 | 416.8 |
| 2021 | 3 | 996.6 | 929.6 | 1092.5 |
| 2022 | 2 | 696.3 | 682.5 | 765.9 |

1. **HELD.** 1.275, inside 1.20–1.45 and below both the constant (1.558) and per-anniversary
   (1.437) arms.
2. **HELD.** 2017 MAE 449.3 against per-anniversary 463.8 (3% below); against the constant 532.4.
3. **HELD.** Every year 2018–2022 improves on the constant arm.
4. **HELD.** 2016 is blank under `no_complete_tenure_year`; the arm keeps the published belief for its
   3 rows.
5. **FAILED.** Spearman +0.096 → +0.095. The reason is in the population, not the mechanism: 51 of
   69 rows are 2017 beliefs, and at 2017 the table has ONE complete year, so every 2017 account
   faces the same forward sequence [0.154] whatever its position. Position can only rank where the
   table has more than one year, which is 15 graded rows. The per-account variation exists (the
   controls show it moves value); this graded population cannot see it.

Still over-valuing: 52 of 69 beliefs exceed the realised value in magnitude. The excess that
remains is not the hazard's shape. The gap is a diagnostic, never a target (R12).

## AMENDMENT, filed before any graded row was measured

Printing the complete-year table at every cutoff showed the tail rule above fails on the real book:
at 2023 the last complete year (y7, 22 at risk) has **no exit**, so "carry the last complete year
on" claims an infinite tenure and blanks H2 for every account in that snapshot. The tail is now the
complete years from the **last year in which anyone left** onward, pooled as one annual hazard
(1 − (Π(1 − h_k))^(1/n)). The quiet years still count: they lower the tail. On every other cutoff
2016–2025 the last complete year has exits, so the amendment changes only 2023 (tail y6–y7 pooled,
≈0.035) and 2025 (y7 is no longer explicit-zero only if it sits after the last exit — it does not:
y8, y9 carry exits, so 2025 is unchanged). The predictions above stand as filed.
