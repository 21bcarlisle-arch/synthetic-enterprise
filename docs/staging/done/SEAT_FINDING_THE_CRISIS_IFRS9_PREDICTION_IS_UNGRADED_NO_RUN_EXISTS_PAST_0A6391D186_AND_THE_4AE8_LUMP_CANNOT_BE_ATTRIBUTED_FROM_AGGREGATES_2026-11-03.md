**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series`

# The crisis IFRS 9 prediction is ungraded, and the 4ae8 lump cannot be attributed from the run output (2026-11-03)

Item: grade the prediction in `docs/staging/done/WORKER_FINDING_THE_08F267B666_PUBLISH_...` row
"crisis IFRS 9 step-up" (crisis-years charge under 1.0%, no 2022-23 year at 1.2%) on the next fresh
run, and attribute 4ae8da9b0f's 2023 lump.

## Why it is not graded

The newest committed run is 19aa987bc5 (git=0a6391d186, 2026-11-03 02:48).
*Correction (2026-11-03, beside the claim): "no run exists past 0a6391d186" was wrong when filed at
04:38. A run on 8b2a07d8dd had finished at 02:31 (`docs/staging/done/run_complete_20261103T010219Z.md`),
held for the 9 Nov publish window rather than committed. This finding read only committed runs.* It is the book the
prediction was filed against, not one after it. Neither c144971dab nor 54f76662d1 (the 2 Nov
phantom-debt and held-estimate fixes the finding names) is an ancestor of 0a6391d186, so **the next
fresh run is the first on them**. Reading 0a6391d186 again would grade a prediction on its own
baseline.

## What the two committed books show (IFRS 9 charge as % of revenue; same world digest cdba75ebb9197b33)

| | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| 4ae8da9b0f | 0.80 | 0.36 | 0.22 | 0.32 | **1.55** | 0.17 |
| 0a6391d186 | 0.86 | 0.41 | 0.21 | 0.27 | 0.38 | 0.14 |

Pay-on-receipt debt over 90 days at year end (GBP):

| | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| 4ae8da9b0f | 564 | 1,257 | 9,335 | 6,411 |
| 0a6391d186 | 687 | 1,463 | 3,348 | 3,830 |

## Attribution: I cannot yet say, and these aggregates cannot say it

- Both books step up over 90 days in 2023 (x2.3 on 0a63, x7.4 on 4ae8), so a 2023 step exists in
  both; only its size differs. The IFRS 9 charge reads it as a lump in 4ae8 because the stock
  moved in one year and then fell back.
- 4ae8's stock stays at 6,411 into 2024, so the lump was not a one-date artefact of a year-end cut.
  That fits both "accounts that never cured" (phantom debt, c144971dab's shape) and "a cast that put
  more non-payers in 2023".
- The run output carries bucket totals by date (`company_provision.by_date`), not accounts. 469
  commits separate the two books. Reading end-2023 accounts needs a re-run of 4ae8da9b0f, which is
  a full run to answer a question the next fresh run partly answers by itself.

## Prediction, unchanged and still filed before the answer

On the first run after c144971dab and 54f76662d1: crisis-years IFRS 9 charge under 1.0%, and no
single year 2022 to 2023 at 1.2% or over. **Refuting readings:** a year at or above 1.2% means the
lump is not the fixed defect (cast, or a real 2023 mechanism); 2023 pay-on-receipt over 90 days
back near 9,000 says the same. If the 2023 over-90 stock reads near 3,300 again, that favours cast
noise around a real x2 step, not defect-made debt, and the exception's ceiling stands.

Nothing here changes the named exception in `test_crisis_bad_debt_validator.py`; it is keyed to the
rate (0.3295% floor of cover), not to which book passed.

## Graded (2026-11-03): the prediction holds on the first run on both fixes

Read on `docs/reports/run_output_8b2a07d8dd_20261103T010219Z.json`. Both c144971dab and 54f76662d1
are ancestors of 8b2a07d8dd, and the world digest is the same cdba75ebb9197b33. The run is **not
published**: it was held for the Mon 9 Nov window. The prediction is about what the fixed code
produces, so publishing does not change the reading. Computed with
`crisis_bad_debt_validator.extract_series_from_run_output(run, "ifrs9_charge")`, which reproduces
0a63's row above exactly.

IFRS 9 charge as % of revenue:

| | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | crisis years (2022-23) |
|---|---|---|---|---|---|---|---|
| 0a6391d186 | 0.86 | 0.41 | 0.21 | 0.27 | 0.38 | 0.14 | 0.3295% |
| 8b2a07d8dd | 0.86 | 0.41 | 0.21 | 0.28 | 0.37 | 0.14 | 0.3284% |

Pay-on-receipt debt over 90 days at year end (GBP), from `company_provision.by_date`:

| | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| 0a6391d186 | 687 | 1,463 | 3,348 | 3,830 |
| 8b2a07d8dd | 687 | 1,542 | **3,306** | 3,775 |

- **Crisis-years charge under 1.0%: holds** (0.328%).
- **No 2022-23 year at or above 1.2%: holds** (2022 is 0.28%, 2023 is 0.37%).
- **Refuting readings did not occur.** 2023 over-90 is 3,306, not near 4ae8's 9,335. That is the
  "near 3,300" branch filed above: it favours cast noise around a real x2 step, not debt made by
  the defect. **4ae8's 2023 lump (1.55%) is not reproduced by the fixed code.** The two fixes
  barely move this book: the charge shifts by 0.001pp and over-90 debt by about 1%.
- **The named exception still covers this book.** Its ceiling in code is
  `_EXCEPTION_LOWEST_CRISIS_RATE_COVERED = 0.0032`, so the 0.3284% reading has 0.008pp of headroom.
  The comment beside it says 0.3295%. The constant is the rule and is lower than the comment, so
  this book does not "sink further" by the code's test. The strict xfail on the 2022 step (2022 at
  0.28%, under 2016-19's 0.72%) still fails as expected.

**What this does not settle.** The crisis charge stays at a third of the floor in both books. The
cause filed against the world's payment draw, which has no price input, is untouched by these
fixes. W2_38 still owns that cause.
