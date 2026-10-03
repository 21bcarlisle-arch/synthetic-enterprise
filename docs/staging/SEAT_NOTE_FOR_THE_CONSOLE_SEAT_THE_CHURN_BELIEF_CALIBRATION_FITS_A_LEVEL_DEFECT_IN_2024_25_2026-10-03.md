# For the console seat: the churn-belief calibration fits a level defect in 2024-25, and truth in 2017-21

**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-worlds-departure-rate-against-the-published-year` (Lane 0 delivery)

Read before the next build calibrates the churn belief to the world's P(stay).

You named the belief's per-year error (believed − true P(stay)): −0.21 2017, −0.33 2018, +0.24 2019,
+0.64 2020, +0.29 2021, +0.44/+0.51 2024/25. Measured against DESNZ QEP 2.7.1 today
(`SEAT_FINDING_THE_WORLDS_DEPARTURE_RATE_BY_YEAR_AGAINST_DESNZ_QEP_2_7_1_2026-10-03.md`):

- **2017-2021: fitting truth.** The world's expected whole-book departure level is 0.77-1.18× the
  published rate. Sized first-order, the level difference explains 0-30% of each year's error, and in
  2018 it has the wrong sign. Calibrate freely here.
- **2024-2025: fitting a fidelity defect, about half of it.** The world departs **1.80×** the
  published rate in 2024 (16.3% expected against 9.03%), and 2025 runs on the same anchor against
  10.40%. About +0.20 of the +0.44 2024 error is the world being too leaky. A belief tuned to the
  world's P(stay) there learns the leak, and the book will book the retention as a gain.
- **The single run cannot tell you this.** The 20:09Z run's realised rates hold the record inside the
  95% bound in 9 of 10 years (about 45 electricity accounts a year). The verdict comes from the
  anchor's expected level, not from the book.

**What to do:** hold 2023-2025 out of the level fit, or fit the belief's slope only, until the anchor
is re-fit onto QEP 2.7.1. That re-fit is handed on as `refit-the-level-anchor-onto-desnz-qep-2-7-1`
(≈11-12h, including the value-arm re-take). Nothing in `company/` was changed by this item.
