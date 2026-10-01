# Pre-registration — both standing-charge pairs retaken without the look-ahead

Written 2026-10-01 ~20:20 BST, before any arm ran. Claim
`retake-the-renewal-feedback-attribution-without-the-look-ahead`. Base: `cd0c7c39c` (the portfolio
premium reads only terms that had ended before the renewal starts). Script: `/var/tmp/se-retake/`
(the instrumented `/var/tmp/se-sc-attr2/measure.py` plus a third arm). One default world per arm.

Arms, by standing-charge table patched in:
- `old` — the pre-ex-VAT table (2016-2024, 2025 clamps to 2024's 61p / 31p);
- `exvat` — the ex-VAT cap-model table, 2016-2024 only (2025 clamps to 57.11p / 28.57p);
- `new25` — `exvat` plus the 2025 rows (51.23p / 29.58p), i.e. HEAD's table.

## Pair A: `exvat` vs `new25` (the 2025 row; the whole-run leak test)

- **A1.** 0 account-term-years dated before 2025 move, in revenue or in standing charge. Before the
  fix 12 moved (renewals starting 2024-07-01 and 2024-10-01). A non-zero count means something still
  reads a margin the company could not yet have seen.
- **A2.** 2025 standing charge: electricity −£665 ± £30, gas +£91 ± £10. The band is wider than the
  first pair's because the book's margins changed under the fix.
- **A3.** 2025 unit revenue moves by less than £15 in absolute value. Before the fix it was +£10.43.
  Only renewals starting in 2025 can now read a 2025-affected margin, and only through terms that
  had ended by then.
- **A4.** kWh identical on every key.

## Pair B: `old` vs `exvat` (re-taking the 12% attribution)

The finding being re-taken measured +£1,356.19 of unit revenue, with portfolio premium carrying
+£1,040.51 (876 renewals) and margin surcharge +£320.63 (222 renewals).

- **B1.** First terms move by exactly £0.00; kWh identical on every key; `struck` identical on every
  renewal.
- **B2.** Portfolio premium Δ is **smaller** than +£1,040.51, between +£500 and +£1,040. The SC
  change spans every year, so a lag of about one term should cut the recovered amount only in
  part. Low confidence in the band, moderate in the sign of the change.
- **B3.** Margin surcharge Δ is between +£250 and +£400. `prior_term_margin_gbp` was not touched by
  `cd0c7c39c`. If it moves outside this band, the prior-term reading has its own timing question.
- **B4.** Total unit revenue Δ is between +£800 and +£1,400, i.e. the feedback fraction stays
  between about 7% and 12%.
