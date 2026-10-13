**Severity:** LATENT · **Lane:** B_commercial · **Claim:** `dd-own-forecast-forward-split-wired-after-the-pile-lands`

# Pre-registration: the DD review priced at the term end and the company's own forward

Filed 2026-10-13 BEFORE the wiring is run on any book. No figure below has been computed with it.

## The change (one variable)

`own_forecast_plus_balance` (the director's rule, 2026-10-11, on origin at 2d864882e) already
carries a balance leg, and takes `term_end_iso` and `forward_rate_per_mwh_ex_vat` that no caller
supplied, so the whole forecast year priced at the known rate. Now both composition roots
(`simulation/dd_balance_book.py::build_dd_balance_book`, `tools/dd_book_legs.py`) supply them:

* **term end** -- the end of the account's own term in force on the review date, from the run's
  `account_state_log` (the company's own record of the terms it sold);
* **forward rate** -- the known unit rate on the new year's first bill, moved by the change in the
  company's OWN 12-month forward (`basis_risk_terms.company_fwd_gbp_per_mwh`, never `sim_fwd`)
  between the start of that term and the review date. A 1:1 pass-through of wholesale into the
  retail unit rate, with no losses uplift: a stated belief, not a sourced figure.

The balance leg is unchanged. The default rule is unchanged.

## The book

The single-levy run, `/var/tmp/single_levy/run_output_abb925ec7.json`, month 2018-06, all three
rules in one process (`tools/dd_book_legs`). Known from the record: `last_year_spend` review lag
-£17,840, book -£20,614; `consumption_at_rates_in_force` lag -£14,434, book -£17,429 (ab17e3136).

## Predictions

| | Prediction | Why |
|---|---|---|
| P1 | Against the same rule with the term end and forward withheld, the review lag moves by **less than £1.5k**, most likely toward zero. | ab17e3136 found about half the year's price rise comes after the review. The company's forward is an EWMA of spot (`CompanyTariffEngine`), backward-looking, so it can only see the part of the rise wholesale had already shown. |
| P2 | The term-end leg is taken (term ends inside the forecast year) on **at least 80%** of the reviews the book makes, and the forward leg (forward rate differs from known) on **at least 80%**. | Most accounts are on the default tariff by their first review, and its terms run one cap quarter. |
| P3 | `own_forecast_plus_balance` wired: book at 2018-06 between **-£6k and -£14k**. | The balance leg recovers window 0's debit over window 1. |
| P4 | The default does not switch. The bar carried from ab17e3136 (a £4k lag move) is not met by the forward split. | Follows from P1. |

A miss on P1 in either direction is the interesting result: more than £1.5k toward zero means the
company's forward carries real information about the year ahead; a move away from zero means its
seasonal swing (2016: £35-55/MWh within one year) is read as a price trend.

## Result (measured after the predictions above were written; `tools/dd_book_legs`, one process)

| 2018-06 | review lag | balance recovery | book |
|---|---|---|---|
| `last_year_spend` | -£17,840 | 0 | -£20,614 |
| `consumption_at_rates_in_force` | -£14,434 | 0 | -£17,429 |
| `own_forecast_plus_balance`, term records withheld | -£14,434 | +£4,834 | -£12,595 |
| `own_forecast_plus_balance`, wired | -£9,648 | +£4,075 | -£8,426 |

* **P1 MISSED.** The forward split moved the lag by **+£4.8k**, not under £1.5k. Toward zero, as
  guessed, but three times the bound. The company's forward carries more of 2017-18's rise than I
  credited it with: electricity's forward rose from about £45 to £55-67/MWh across the year.
* **P2 HELD.** 2,029 of 2,033 reviews split at a term end and priced a forward.
* **P3 HELD.** -£8.4k, inside -£6k to -£14k.
* **P4 MISSED on its own terms**: the £4.8k move clears the £4k bar carried from ab17e3136.

Graded per review against the rate actually billed after the term end, the forward is better than
the known rate in rising years and worse in falling ones (electricity MAPE 2019 0.072 known vs 0.090
forward, 2020 0.077 vs 0.101; gas 2018 0.055 vs 0.092). Read at each mid-year 2019-06 to 2024-06,
the wired review lag is less negative than the withheld one at every read but 2021-06 (unchanged,
-£11.3k), yet the book is MORE negative at 2020-06 (-£2.2k against +£1.3k) and 2021-06 (-£5.1k
against -£3.8k), because a higher debit in one window leaves less balance for the next review to
recover. The lag improving is the sign of this run's lag (the DD runs short every year), not
evidence the forward forecasts well. Full table: knowledge page §7.

**The default does not switch -- a decision, with its reason.** The £4k bar was set to judge one
variable against the record, and it was cleared. But the forward is a 1:1 pass-through with no
losses factor (a belief, §7's GAP), it forecasts worse than the known rate in falling years, and
the balance leg, which the same switch would turn on, over-recovers to a **+£44k credit** book at
2024-06 after 2022-23's debits (§6 GAP 2, the symmetric credit treatment, is unsourced). Switching
moves published figures on three unsourced choices at once. What would change this: the cap's losses
factor transcribed, and the rule graded against a falling-market window. Reverse: set
`DEFAULT_REVIEW_RULE` in `company/billing/dd_review.py`.
