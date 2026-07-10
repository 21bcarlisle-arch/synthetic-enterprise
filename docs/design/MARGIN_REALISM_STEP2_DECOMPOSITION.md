# MARGIN_REALISM Step 2 — Per-Year Margin Decomposition (Diagnosis)

**Status:** COMPLETE. Diagnosis-only, per `docs/staging/done/MARGIN_REALISM.md`'s own
sequencing ("no mechanism work lands until percentages are computed on a trustworthy
base" -- Step 1 closed this; this step decomposes WHY the corrected percentage is still
elevated, seeding Step 3 (opex) and Step 4 (hedge-tariff alignment)). No code changed.

## Data sources
`docs/reports/run_output_latest.json`: `years[yr]` (revenue_gbp, gross_gbp, capital_gbp,
bad_debt_gbp, net_gbp, policy/network cost fields, hedge_effectiveness),
`management_accounts[yr].income_statement.revenue_gbp` (total revenue, per Step 1),
`docs/market_research/ASSUMPTIONS.md` (real EDF/British Gas Customer Segmental
Statements EBIT%, Ofgem cap EBIT allowance).

## Per-year decomposition (real run data, 2026-07-10)

| Year | Total Revenue | Gross | Gross % | Net (commodity-basis) | Net %(total rev) | Hedge value-add | Hedge v-a / Gross |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2016 | 15,362 | 6,822 | 44.4% | 1,278 | 8.3% | -8,910 | -130.6% |
| 2017 | 348,631 | 123,239 | 35.3% | 31,631 | 9.1% | -82,436 | -66.9% |
| 2018 | 601,110 | 262,602 | 43.7% | 101,531 | 16.9% | -137,078 | -52.2% |
| 2019 | 1,645,470 | 702,101 | 42.7% | 234,108 | 14.2% | -584,221 | -83.2% |
| 2020 | 1,857,023 | 791,770 | 42.6% | 128,512 | 6.9% | -877,689 | -110.9% |
| 2021 | 2,415,922 | 763,155 | 31.6% | 75,232 | 3.1% | -265,535 | -34.8% |
| 2022 | 4,241,009 | 1,049,225 | 24.7% | 338,348 | 8.0% | -1,022,482 | -97.5% |
| 2023 | 3,473,230 | 955,882 | 27.5% | 144,377 | 4.2% | -839,219 | -87.8% |
| 2024 | 2,999,631 | 1,257,806 | 41.9% | 347,815 | 11.6% | -405,057 | -32.2% |
| 2025 | 1,228,035 | 518,611 | 42.2% | 120,993 | 9.9% | -220 | -0.0% |

`Net (commodity-basis)` = gross - capital(hedging cost) - bad debt. This is NOT the
Step-1-corrected `net_margin_pct` published on the Financial tab (that also nets policy/
network pass-through and is denominated against total revenue) -- shown here to isolate
the commodity-and-hedging-only drivers before touching policy/network.

**Gross margin %** (24.7%-44.4%) is broadly plausible against a real ~35-45% range, with
a real, mechanically-expected compression in 2021-2023 (the wholesale crisis years) --
this line is NOT the source of the excess margin.

**Net %(total revenue)** (3.1%-16.9%, ~8.9% average, per Step 1) remains above the
~1-3% real long-run benchmark even after the Step 1 denominator fix. The gap is
explained by two things below, not a further gauge error.

## Missing cost line: opex/cost-to-serve is NOT deducted in the annual P&L at all

`saas/cost_to_serve.py` exists (`FIXED_OVERHEAD_GBP_PER_YEAR`: resi £55, SME £120,
I&C £500/account/year -- unanchored placeholder figures, the module's own docstring
calls it "operational overheads per customer account") but it is **only ever consumed
per-customer, cumulatively life-to-date, for CLV projections** (`saas/reporting/
annual_report.py::_clv_snapshots_by_year()` and `_pricing_action()`). It is **never
subtracted from the portfolio-wide annual `net_gbp` figure that seeds the Financial
tab and the numbers decomposed above.** A real supplier's published accounts always
carry "operating costs" (billing/IT/customer service/metering/overhead) as one of the
largest single cost lines -- EDF/British Gas Customer Segmental Statements and Ofgem's
own default-tariff-cap methodology both allocate it a comparable share to network or
policy costs. This simulation's annual net-margin trend has never subtracted anything
resembling that line. **This is the single largest, clearest, structurally-missing
cost line** and is exactly what Step 3 (already amended by the director into a
three-part true-cost/dual-ledger design) is scoped to build.

## Cross-check against real external EBIT benchmarks (already in ASSUMPTIONS.md)

| Year | Sim net% (Step-1 basis) | Real published EBIT% (EDF/British Gas CSS, dom elec unless noted) |
|---|---:|---|
| 2019-2022 | 14.2% / 6.9% / 3.1% / 8.0% | Ofgem-published aggregate: negative, approx -4% to -10%/yr, sector -£4bn cumulative; sim 2021/2022 (via the separate cap-applied EBIT%, not the figure above) were -6.6%/+6.7% |
| 2023 | 4.2% | 4.2% (EDF), 7.8% (British Gas) -- both flagged in ASSUMPTIONS.md as exceptional/post-crisis, elevated by hedge gains |
| 2024 | 11.6% | 5.4% (EDF); Ofgem's own EBIT allowance built into the cap = 1.9%; ASSUMPTIONS.md's own note: "Long-run normal should be ~1.9-3%" |

The 2019-2022 comparison uses a different, already-cap-applied EBIT figure computed
elsewhere (`docs/market_research/ASSUMPTIONS.md` line 47/50) rather than the
`years[yr]` figures decomposed in this doc's main table -- both bases are shown for
transparency rather than silently picking whichever matches better. 2024 (11.6% sim
vs 1.9-5.4% real) is the cleanest like-for-like read once policy/network pass-through
genuinely nets to near-zero: still ~2-3x too high, consistent with the missing opex
line above.

## Flagged for Step 4 (hedge-tariff alignment) -- NOT investigated further here

Hedge value-add (`actual_net - naked_net`, i.e. hedged-portfolio net minus a fully
spot-exposed counterfactual) is **negative in every single year 2016-2025**, and its
worst relative reading (as a share of gross, -97.5%) falls in **2022** -- the real UK
wholesale gas/power crisis year, when a hedged supplier should show its BEST relative
performance against a naked counterfactual (naked suppliers who carried full spot
exposure in 2021-22 were the ones that went bust -- Bulb, Avro, et al.). 2021 (-34.8%)
and 2024 (-32.2%) are the least-negative years, which is at least directionally
consistent with hedging helping in the crisis's first year, but 2022 being the worst
reading of the whole decade is backwards from the expected shape and does not yet have
an explanation. This sits in the same hedge-decision code area the Tier 1 hedge-
volatility-lookback gate closed earlier this week (`docs/review_gates/done/
HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md`) -- flagged as this step's "seed" for
Step 4 per the work plan's own language, deliberately not root-caused in this diagnosis
pass to avoid scope creep into recently-touched, sensitive code ahead of its own
sequenced turn.

## Summary for Step 3/4

1. Gross margin is not the problem (plausible, real compression in crisis years).
2. The corrected (Step 1) net margin's remaining ~2-3x gap vs real ~1-3% long-run
   benchmark is best explained by a genuinely MISSING cost-to-serve/opex line in the
   annual P&L, not a further denominator error -- Step 3 is the direct next step.
3. A real, unexplained hedge value-add anomaly (worst in the actual 2022 crisis year)
   is flagged as Step 4's seed, not investigated further here.
