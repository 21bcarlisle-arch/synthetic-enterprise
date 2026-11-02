**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** none — Lane 0 `the-fresh-run-after-the-pc2-and-gas-fixes`

# Pre-registration: the fresh run at 85b044be54 is the first book with both the PC2 fixes and the gas volume build (2026-11-02)

Under the correctness stretch (`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`).
Filed before the run produced anything. The grade will be a separate record and will not edit this file's predictions.

## What the run carries, against the last graded book (cd4fc5b8d8)

Code commits to `company/`, `simulation/`, `saas/` and the runner since cd4fc5b8d8:

- **89220b9ddc**: the PC2 fixes (per-register estimate scaler, the estimate row graded per register on PC2's shape,
  void days drop band kWh, the page writes `profile_class`). Predictions:
  `SEAT_PREREGISTRATION_THE_PC2_FIXES_PREDICTED_PER_ROW_FOR_THE_NEXT_FRESH_RUN_2026-10-30.md`.
- **34b764a0fd**: the gas volume build (N11 C1-C3). Predictions:
  `SEAT_PREREGISTRATION_A_GAS_READ_IS_A_VOLUME_ON_A_REPLAY_AND_THE_NEXT_FRESH_RUN_2026-10-30.md`, item 4.
- **8b046d4130**: the SVT one-price row grouped by metering arrangement (a row fix, not a bill change).
- **59bde3e790**: W2_37, `simulation/complaint_generation.py`. **This is the confound.** If it draws from a stream
  that other world processes share, any row can move for a reason that is neither fix. A row that moves where
  neither fix predicts a move is attributed to it, or to nondeterminism, and not to the fixes.

## Pretest at 85b044be54 (read before launch)

- `tests/company/billing` run whole, cache provider on: **2,536 passed, 0 failed** (158 s). The 41 order-dependent reds
  of `SEAT_FINDING_TESTS_COMPANY_BILLING_RUN_WHOLE_REDS_41_TESTS_THAT_PASS_ALONE_2026-10-30.md` do not reproduce.
- `tests/simulation` run whole: recorded in the grade, as it is the launch gate.

## Predictions (cd4fc5b8d8 count -> predicted on this book)

The PC2 rows restate the PC2 pre-registration's table without change:

| Row | cd4fc5b8d8 | Predicted | Source |
|---|---:|---:|---|
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 4 | <= 1 | PC2 prereg |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 120 | <= 6 | PC2 prereg |
| INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 / _ON_THE_BILL | 21 / 21 | 6 / 6 | PC2 prereg |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 170 | <= 10 | PC2 prereg |
| INV_E7_METER_BILLED_ON_TWO_REGISTERS (the E7 row) | 4 | 0 | PC2 prereg, point 5 |
| INV_TOU_BANDS_SUM_TO_THE_TOTAL | 2 | 0 | PC2 prereg, point 5 |
| INV_PERIODS_CONTIGUOUS | 2 | 0 | PC2 prereg, point 6 |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 4 | <= 4 | PC2 prereg |
| INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF | UNCHECKABLE | 0 | gas prereg, item 4 |
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | 0 (after the row fix) | 0 | 8b046d4130 |
| INV_METER_SERIAL_ONE_SUPPLY_POINT (N10) | 0 | 0 | held twice |
| F/VAT: reads left uncorrected; catch-ups off the VAT line | 0; 0 | 0; 0 | held twice |
| desk-cure P1: `cured` at `days_overdue == 0` | 0 | 0 | held twice |
| INV_UNIT_RATE_EPG_HOUSEHOLD | 350 | <= 350 | excepted ceiling |
| INV_PPM_NOT_CREDIT_BILLED | <= 12 | <= 12 | excepted ceiling |
| Storage-heating Explore slot | empty | fills | PC2 prereg, point 7 |

Gas energy: the gas prereg's item 4 says gas billed energy matches a run without the build bill for bill. That
cannot be graded bill for bill against cd4fc5b8d8 if W2_37 moves the world. Book-level gas kWh within 0.26% of
cd4fc5b8d8's is the weaker test I will grade, and I will say which it is.

**Debt survivors.** PROS-2025-0013 ("the story outruns its own page") and PROS-2020-0191 (cause not established)
both survive as "cleared while still owed" if the debt code is unchanged, and none of the commits above touches it.
Predicted: both survive, no new one.

**Refutation.** A row above its predicted count refutes the claim that its fix explains it, and is traced again,
not re-explained.
