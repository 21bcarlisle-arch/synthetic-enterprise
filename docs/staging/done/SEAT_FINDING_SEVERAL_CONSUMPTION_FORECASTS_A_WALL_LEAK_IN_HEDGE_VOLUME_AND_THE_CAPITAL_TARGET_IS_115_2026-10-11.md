**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# Several consumption forecasts, a wall leak in the hedge volume, and a capital target that is £115, not £130 (2026-10-11)

**Fate (2026-10-12, clear-the-decks):** DONE -- 97e65aa2a. The company holds four consumption forecasts, not one...the capital target is GBP 115... matches exactly, same day

*Delivery seat. Found answering the director's 2026-10-11 question: "does the company hold one consumption
forecast per property used by purchasing, DD setting, unbilled estimation and customer value, or several?
Where they differ, which is best against held-back actuals?" Measured on a 40-founder production run
(164 account-years over 43 accounts; scratch at `/var/tmp/forecast_audit/`), and from the payment-plan
knowledge pass landed the same day.*

## 1. Several forecasts, not one

| # | Forecaster | Used by | Inputs | Shape |
|---|---|---|---|---|
| F1 | `company/billing/annual_consumption_estimate.estimate_annual_consumption` | opening DD; opening estimated bills | registry EAC/AQ, else Ofgem TDCV medium | annual; published monthly shares for bills |
| F2 | `simulation/run_phase2b._company_eac_estimate` (trailing 12 months settled kWh) | electricity hedge volume from term 2; churn/renewal EAC; account state | settled records | annual, **electricity only** |
| F2g | gas leg: `aq_kwh x household_demand_register.gas_eac_multiplier_for_date` | gas hedge volume, every term | registry AQ x a world-side multiplier | annual, never updated from reads |
| F3 | `company/billing/unread_month_estimate.estimate_unread_kwh` | estimated bills for unread months | last 3 actual reads / profile weight | monthly, published shares (actual-weather years, not normal weather) |
| F4 | `simulation/dd_balance_book.reviewed_standing` | DD annual review | last 12 months billed GBP (default), or billed kWh x current rates | annual, includes estimated bills |
| -- | `company/analytics/forward_clv`, `saas/clv_model` | customer value | past margin and a hazard | no consumption term |
| -- | unbilled revenue | -- | `saas/ledger.py` returns None | -- |

Nothing applies normal weather. The account's own last-year monthly shape (the best shape measured, below) is
used by nothing.

**Backtest** (forecast at each anniversary vs the next 12 months' settled kWh, same accounts for every
forecaster; MAPE / mean signed error, %):

| Fuel, period | n | F1 | F2 | F3 | F4 | hedge volume actually passed |
|---|---|---|---|---|---|---|
| Electricity, year 1 | 31 | 13.4 / -1.6 | =F1 | =F1 | =F1 | 8.8 / +8.0 |
| Electricity, later | 81 | 2.3 / -0.3 | **1.9 / -0.1** | 7.9 / +0.2 | 5.9 / -0.8 | 1.9 / 0.0 |
| Gas, year 1 | 12 | 14.2 / -4.0 | =F1 | =F1 | =F1 | 8.2 / +8.0 |
| Gas, later | 36 | 10.3 / -4.2 | **3.2 / -0.3** | 9.1 / +1.4 | 6.1 / -1.5 | 7.2 / +6.5 |

Monthly shape error (mean absolute error of monthly shares, points): published shares 1.0-1.2; flat 1.05-1.3
(electricity) and 4.5 (gas); **the account's own last year 0.54 (electricity) and 0.99 (gas)**.

**For a DD.** Worst running balance in the year as a share of the year's cost: gas first year (registry)
-13.4% on average, 33% of accounts below -15% (a perfect annual forecast still gives -9.0% and 25% -- the
seasonal swing); gas later years F2 -6.7% (14% below -15%) against the registry -10.4% (31%) and the review
rule -8.3% (17%). F2 is the best forecaster wherever a year of history exists, and it is never applied to gas.

**Limits.** Registry figures here are the world's own level, so year-one error is understated (owed: a
world-side true EAC distinct from the declaration). F2 reads daily settled kWh, cleaner than a real
supplier's reads for a non-half-hourly meter. Small book (5-6 gas accounts per cell): indicative.

## 2. A wall leak: the hedge volume reads world-side multipliers

The year-1 electricity fallback and every gas term multiply by `simulation/household_demand.py`'s household
multipliers -- a quantity no real supplier can see. It also overshoots (+8 to +12%). **Owed:** the hedge volume
reads the company's own forecast (F2, or the one forecast below), never a world multiplier.

**Closed 2026-10-11 (claim `the-hedge-volume-reads-only-what-the-company-holds`).** Both fuels' volume
now comes from `company/interfaces/sim_interface.supplier_annual_volume_kwh`. It is handed only the
register reads that ARRIVED before the term (the change-of-supply opening read included) and the
registry EAC/AQ. It annualises the advance nearest a year, from 6 to 24 months, on the published
profile. The world's gas demand still takes the multiplied AQ: that is the household's use, not
the company's belief. `demand_estimation_log.error_pct` now grades the year that FOLLOWED.

One seed, 606 graded hedges: pooled MAPE fell from 10.4% to 5.8%, but the pooled bias rose from
+1.4% to +3.4%. `total_capital` rose 0.2% where I predicted a fall of 2-8%. The old trailing sum had
been UNDER-stating later electricity terms (-4.1%) whenever the window held less than a year.
Prediction and result, graded:
`docs/staging/records/SEAT_PREREG_THE_HEDGE_VOLUME_READS_ONLY_WHAT_THE_COMPANY_HOLDS_2026-10-11.md`.
Control: `tests/simulation/test_the_hedge_volume_reads_only_what_the_company_holds.py`, with four
mutations proven. Still owed: the +3-4% over-statement of the profile-annualised advance (the season
finding), and `household_demand_register.eac_multiplier_for_date` and `_derive_eac_from_settlement`,
which now have no production caller.

## 3. The capital target is £115, and the code says £130

Ofgem's financial resilience decision of 26 July 2023: "The Capital Floor will be £0 Adjusted Net Assets per
dual fuel customer equivalent and the Capital Target will be £115 per domestic dual fuel equivalent customer";
licence: "'Capital Target' means licensee Adjusted Net Assets of £57.50 per Domestic Customer"; binding from
31 March 2025; CMA upheld 19 January 2024; no indexation (`docs/market_research/bad_debt_provisioning.md`,
"Capital target: the conflict settled"). £130 / £65 was the April 2023 consultation figure. The knowledge page
`ofgem_regulation.md` is corrected (2026-10-11). **The code still carries £130:**
`company/finance/treasury.py::MCR_PER_ACCOUNT`, `saas/capital/solvency.py::MCR_FLOOR_GBP_PER_CUSTOMER`,
`company/risk/independent_amount.py::MCR_GBP_PER_ACCOUNT` (whose docstring attributes £130 to the July 2023
decision). **It is load-bearing:** `saas/growth_mandate.py` bounds the campaign's quote budget by capital per
account, so the correction relaxes the growth ceiling and changes the book -- to be landed as its own measured
step (before/after on the same seed).

**And a question for the director (curriculum):** the requirement was decided in 2023 and binds from 2025, but
the run applies it from 2016. A supplier in 2016-2022 faced no such target. Proposal: apply the Capital Target
from its binding date (31 March 2025; or from the July 2023 decision as the date a prudent supplier began to
plan for it), and before that only the floor a real supplier faced (none) -- which would loosen early growth
and is the director's to rule, because it changes which world the company lives through.

## 4. What this sets for the payment plan

The director's target is one forecast per property: the next twelve months with its seasonal shape and normal
weather, priced at known rates where fixed and forecast rates beyond, plus the balance to clear. The measured
best ingredients are F2's level and the account's own last-year shape; normal weather is not built anywhere.
The payment-plan design takes this as its forecast input.
