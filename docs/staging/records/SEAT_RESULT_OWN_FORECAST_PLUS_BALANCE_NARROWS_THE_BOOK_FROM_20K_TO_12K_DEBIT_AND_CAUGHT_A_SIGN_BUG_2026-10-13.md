# The third DD review rule is built, measured against its filed prediction, and caught its own sign bug

LANE 0 DELIVERY, direction item `the-dd-amount-is-set-from-the-companys-own-twelve-month-forecast-plus-the-balance`
(director, console, 2026-10-11T04:20Z). Prediction filed first:
`docs/staging/records/PREREG_OWN_FORECAST_PLUS_BALANCE_VS_THE_TWO_EXISTING_RULES_2026-10-13.md`.

## What landed

- **Knowledge (K8) first:** `docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md`
  §4.7 closed with the director's ruling; new §6 records what the build does and four named GAPs.
- **Third `REVIEW_RULES` entry, `own_forecast_plus_balance`**, in `company/billing/dd_review.py`:
  the trailing-12-month billed kWh/days priced at the known rate while the current term runs and
  the company's forward estimate beyond it (optional `term_end_iso`/`forward_rate_per_mwh_ex_vat`,
  degrading to the whole year at the known rate when absent), plus the balance the account carries
  into the review, recovered symmetrically over the same twelve months
  (`balance_to_clear_gbp`, default 0.0). `DEFAULT_REVIEW_RULE` is unchanged.
- Wired end to end for the balance half: `company/interfaces/dd_review_outcome.py` (new
  `simple_balance_after_window` door, `reviewed_standing` now forwards `**kwargs`),
  `simulation/dd_balance_book.py` (`build_dd_balance_book` computes the running balance entering
  each window and passes it to the review), `tools/dd_book_legs.py` (new `balance_recovery` leg,
  split out of `rounding` so the balance addition is not misattributed).
- Controls: `tests/company/billing/test_dd_review_own_forecast_plus_balance.py` (new),
  `tests/company/interfaces/test_the_dd_review_at_rates_in_force.py` (extended),
  `tests/company/interfaces/test_dd_review_outcome_seam.py` (mutation string updated for the new
  `**kwargs` passthrough and the new sanctioned door). 94 tests in the DD review/balance-book/legs
  area pass.

## What is NOT wired (filed as owed, not shipped as dead code)

The known/forward rate split is real and reachable — proven by a direct unit test
(`test_the_known_forward_split_is_reachable_and_moves_the_price`) — but neither
`build_dd_balance_book` nor `tools/dd_book_legs.py` supplies `term_end_iso` or
`forward_rate_per_mwh_ex_vat` from live data today, so every run prices the whole forecast year at
the known rate (identical to `consumption_at_rates_in_force`'s own price leg — confirmed below).
Wiring it needs `account_state_log`'s term records threaded into the bills-only composition root,
and a genuine `company_fwd` needs the published policy/network schedule added to the wholesale
estimate (`company_fwd` alone is wholesale-only, `renewal_desk.py:187`). Both are named in the
knowledge page §6 as owed to whoever draws that step next.

## Measured, against the filed prediction, in one process

Single-levy run `/var/tmp/single_levy/run_output_abb925ec7.json`, 2018-06, all three rules computed
in one `python3` invocation:

| rule | balance_gbp | review_lag | balance_recovery |
|---|---|---|---|
| `last_year_spend` (current default) | -20,613.59 | -17,840.37 | 0.0 |
| `consumption_at_rates_in_force` | -17,428.59 | -14,434.10 | 0.0 |
| `own_forecast_plus_balance` | **-12,594.59** | -14,434.10 | **4,758.01** |

Predictions 1 (price legs identical to `consumption_at_rates_in_force`), 2 (balance_recovery
positive), 3 (balance less negative than both existing rules) and 5 (`decompose`'s own
legs-sum-to-book-balance check passes for all three rules) all held as filed.

**A wrong prediction, corrected in the record rather than quietly fixed:** the first run of this
measurement showed `balance_recovery = -4,654.01` and the balance moving to -21,952.59 — WORSE than
either existing rule, the opposite of predictions 2 and 3. Both call sites
(`dd_balance_book.py`, `dd_book_legs.py`) had passed the running balance straight through as
`balance_to_clear_gbp` without the sign flip the two conventions need: this module's own
`balance`/`balance_entering` is negative-for-debit (`barred_at_charge_recovery`'s `-balance`
convention), while `reviewed_standing`'s `balance_to_clear_gbp` is positive-raises-the-debit by
construction (tested directly in `test_the_balance_is_recovered_over_twelve_months`). Passed
straight through, a debit LOWERED the DD instead of recovering it. Fixed by negating at both call
sites (`balance_to_clear_gbp=-balance_entering[w]`); the table above is post-fix. Left here rather
than revised quietly, per the project's own rule that a wrong prediction next to its correction is
the only evidence the measurement was designed before its answer was known.

## Switching the default

Not done here — a separate decision, deliberately. `own_forecast_plus_balance` narrows the book's
net debit by £8.0k against the shipped default and £4.8k against the already-built second rule, on
one 288-account run; it has not been checked against a pre-registered bar the way
`consumption_at_rates_in_force` was (`decisions.jsonl`'s own entry: "missed its pre-registered
£4k bar"). Whether this result clears whatever bar applies, and whether the known/forward split
(still unwired) would move the figure further, are for whoever next proposes the switch.
