# PREREG — `own_forecast_plus_balance` against the two existing review rules, single-levy book, 2018-06

*Filed before running `tools/dd_book_legs.py` with the third rule, per the director's work item
(`the-dd-amount-is-set-from-the-companys-own-twelve-month-forecast-plus-the-balance`). Run:
`/var/tmp/single_levy/run_output_abb925ec7.json`, all three rules computed in one Python process
so the comparison is not a before/after over a tree that could move between runs.*

## What is built, and what is not (stated so the prediction is honest about what it tests)

The known/forward rate-split half of the director's design (price at the known rate while the
current term runs, the company's forward estimate beyond it) is NOT wired to live term data in
this run — `build_dd_balance_book` and `tools/dd_book_legs.py` both call `reviewed_standing` from
bills alone, and neither supplies `term_end_iso`/`forward_rate_per_mwh_ex_vat`. So in THIS
measurement, `own_forecast_plus_balance`'s price leg degrades to exactly
`consumption_at_rates_in_force`'s own price leg — same trailing-12-month kWh, same known rate, for
the whole forecast year. The only mechanism this measurement can exercise is the balance-recovery
addition. The split is real and reachable (direct unit test against `reviewed_standing`), just not
through this run.

## Prediction

1. **`opening_sizing`, `seasonal_phase`, `estimate_vs_actual`, `review_lag` are IDENTICAL between
   `consumption_at_rates_in_force` and `own_forecast_plus_balance`**, to the penny. Nothing about
   the price leg changes between the two rules in this run; only `rounding` and the new
   `balance_recovery` leg can differ, and only because `rounding`'s balance-free remainder is now
   split out.
2. **`balance_recovery` is non-zero and POSITIVE in aggregate.** The book is in net debit at
   2018-06 (-£20.6k under `last_year_spend`, 2018-06, `SEAT_FINDING_EVERY_SETTLED_BILL_CHARGED_THE_LEVIES_TWICE_2026-10-10.md`); recovering a
   negative (debit) balance over twelve months RAISES the standing DD, which is a positive
   contribution to the figure recovered — the leg should read positive on the portfolio sum even
   though individual credit accounts contribute a negative share.
3. **The portfolio balance under `own_forecast_plus_balance` is LESS NEGATIVE (closer to zero)
   than under `consumption_at_rates_in_force`** at 2018-06 — recovering the debit raises
   collections in the window(s) after it is observed, which is the whole point of the rule the
   director named ("why it never shows the summer credit a real one holds").
4. **No sign on the SIZE of the gap is predicted** — the single-levy run's account population and
   window timing were not hand-checked before filing this, so a number would be invented rather
   than derived. The size is reported as measured, against this prediction's direction only.
5. **`decompose()`'s own balance-sum check passes for all three rules** (if it did not, the book
   and the legs tool would disagree, and nothing below would mean anything).

— delivery seat, 2026-10-13T01:10Z
