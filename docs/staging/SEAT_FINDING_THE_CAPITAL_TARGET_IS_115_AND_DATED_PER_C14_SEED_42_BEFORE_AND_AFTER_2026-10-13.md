# The capital target lands at £115 and is dated per C14: seed 42 before and after

**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

Filed by the delivery seat (executor), 2026-10-13, with the landing of the £115 correction and
the C14 dating (`saas/growth_mandate.py::capital_target_gbp_per_account`), from origin
`a810dcf3c`.

## What the landing is

A factual correction, not a growth fix. Ofgem's decision of 26 July 2023 set the Capital Target
at £115 per domestic dual-fuel-equivalent account, binding from 31 March 2025. £130 was the April
2023 consultation figure the decision cut. Six modules carried £130. C14 (canon, ruled 12 Oct)
dates the figure: none before the decision, plan-ahead between the decision and 31 March 2025,
binding after that. The director's open concern (8e8a1c10a) measured that capital never binds
growth at £0, £115 or £130, so this landing must not be read as moving growth.

## Pre-registration (written 2026-10-13 ~06:25 BST, BEFORE the measurement below was run)

Subject: seed 42's growth campaign (`simulation.live_population._resolve_campaign`,
`persist=False`), run twice in ONE process over the same pre-growth book. BEFORE: the capital
figure is £130 for every plan year, which is the old behaviour. AFTER: the landed code, with £0 for
plan years before 26 July 2023 and £115 from then on.

Already known, so not a prediction: total quotes go from 3345 to 3373. The test header in
`tests/simulation/test_net_new_acquisition.py` measured this, and it said one capital-bound year
(2025) lifted.

Predictions:

- **P1. Funnel wins:** total wins rise by between 0 and 10. That is about the 28 extra quotes
  times a win rate near 0.2.
- **P2. Where the change falls:** no plan year before 2025 changes its quotes or wins. Dating the
  figure to £0 before mid-2023 moves nothing, because capital did not bind in those years at £130.
  Plan year 2025 carries the whole change.
- **P3. Settled book:** the number of distinct won accounts the run would settle moves by the same
  amount as P1, no more.

Refutation: any plan year before 2025 changes its binding reason or its quotes, or wins rise by
more than 10.

## Result

*(below, after the run; the predictions above were not edited)*
Measured in one process (`/tmp/capt115_measure2.py`) with three arms: BEFORE, BEFORE again as a
placebo, and AFTER. The placebo matched BEFORE row for row, so the comparison is deterministic and
the difference belongs to the capital figure alone.

| | BEFORE (£130 flat) | AFTER (£0 → £115, C14) | Δ |
|---|---|---|---|
| quotes issued | 3360 | 3395 | +35 |
| funnel wins | 608 | 619 | +11 |
| settled winners | 215 | 216 | **+1** |
| wins refused by the settlement budget | 393 | 403 | +10 |

Per plan year, quotes issued and funnel wins are **identical for 2016–2024**. Only 2025 moves.
Its binding reason goes from `capital` to `prospect_ceiling`, quotes go 327 → 400, and funnel wins
go 28 → 39. In 2016–2023 the headroom rises to the full £250k (no target before the decision) and
the affordable quote count rises with it, but no such year was capital-bound, so nothing is
quoted that was not quoted before.

Against the predictions:

- **P1 refuted, narrowly.** Funnel wins rose by 11, against a predicted ceiling of 10. Removing
  the 2025 cap freed 73 quotes, not the 28 the test header suggested. The header's 3345 → 3373 is
  measured on its own book, which is a different book from seed 42's `_pre_growth_book` (3360 →
  3395).
- **P2 holds for quotes and funnel wins:** nothing before 2025 moved. It **fails for settled wins
  per year** (for example, 2016 goes 29 → 32 and 2020 goes 23 → 21). The cause is the settlement
  sampler, not capital. The customer-year budget (5000) is spread across every year at one rate
  (0.3651 → 0.3641), so 11 extra 2025 funnel wins re-draw which wins settle everywhere.
- **P3 refuted.** The settled book moves by +1, not +11. The settlement budget, not capital, is
  what limits the settled book, and the extra wins mostly land in `wins_refused_by_settlement_budget`.

**Reading.** This agrees with 8e8a1c10a. On seed 42 capital binds only in the last plan year at
£130, and nowhere at £115. The correction moves the run's settled book by one account. This is a
fact about the company's capital reporting (solvency ratio, free equity and the annual report all
read £115 now). It is not a growth lever, and it must not be reported as one. Because the
settlement re-draw reshuffles which wins settle in which year, any per-year figure published from
a seed-42 run before this landing will differ slightly after it, even in years the capital figure
never touched.

**Also corrected in this landing:** `tests/saas/reporting/test_annual_report.py::
test_solvency_signal_below_target_shows_gap` was a tautology. Its "30" and "below" were both
satisfied by the section's header text ("£130", "below regulatory floor"), and the section prints
no gap. It now asserts the ratio row computed from the figure. Mutation check: putting
`MCR_FLOOR_GBP_PER_CUSTOMER` back to 130.0 makes it fail.
