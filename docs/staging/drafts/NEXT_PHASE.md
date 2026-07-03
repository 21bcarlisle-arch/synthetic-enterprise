# NEXT PHASE PROPOSAL: Phase NT — Year-on-Year Margin Bridge (P1: Observability)

## Gap addressed
P1: Observability (from 2026-07-03 PRIORITIES.md refresh).

The board report currently shows absolute net margin per year, but cannot answer:
"Why did margin change in 2022?" A real UK supplier CFO produces a bridge/waterfall
analysis for the MD every year: starting from prior-year net, decomposing the delta
into attributable cost and revenue drivers.

Currently: board sees £1.4M net. It cannot see that -£280k came from bad debt surge,
-£90k from capital cost spike, -£40k from policy levy increase, +£120k from new I&C win.
That causal chain is the observability gap.

## What this phase builds

### Part A: Margin attribution module
`saas/reporting/margin_attribution.py`:

`MarginBridge` dataclass (frozen):
- `year_from`: int (e.g. 2021)
- `year_to`: int (e.g. 2022)
- `net_delta_gbp`: net_gbp[to] - net_gbp[from]  -- total change
- `gross_delta_gbp`: gross_gbp[to] - gross_gbp[from]  -- commodity + unit economics change
- `bad_debt_delta_gbp`: bad_debt_gbp[from] - bad_debt_gbp[to]  -- sign: negative = costs rose
- `capital_delta_gbp`: capital_gbp[from] - capital_gbp[to]   -- sign: negative = capital costs rose
- `policy_cost_delta_gbp`: total policy levies delta (ro + cfd + ccl + cm + fit + mutualization)
- `network_cost_delta_gbp`: (network_cost + gas_network_cost) delta
- `portfolio_change`: active customer count delta (int)
- `residual_gbp`: net_delta minus sum of components (should be near-zero)
- `direction`: Literal["IMPROVEMENT", "DETERIORATION", "FLAT"]  -- net_delta sign + £5k threshold

`build_margin_bridge_series(run_data: dict) -> list[MarginBridge]`:
- Iterates sorted year keys from run_data["years"]
- Returns one MarginBridge per adjacent year pair
- Empty list if fewer than 2 years

`dominant_driver(bridge: MarginBridge) -> str`:
- Returns label of the component with the largest absolute contribution
- Candidates: "gross margin", "bad debt", "capital costs", "policy levies", "network costs"

### Part B: Board section
`saas/reporting/annual_report.py`: `_section_margin_bridge(data: dict) -> str`

Table per year-transition showing: Net delta, Gross delta, Bad Debt delta, Capital delta,
Policy delta, Network delta, Portfolio change, Primary Driver. RAG: GREEN (net_delta > 0),
AMBER (within -10% of prior year), RED (<-10%). Summary line: most damaging year and best year.

### Part C: Expose in run output
`extract_report_data` includes `margin_bridge_series` key. Each bridge serialised as dict.

## Why this has real fidelity value
- Every real UK supplier CFO presents a year-on-year P&L bridge to the MD/board
- 2022 crisis: bad debt 2.5x, capital VaR spike, policy levies shifted -- attribution matters
- Board currently sees absolute numbers, not causes; a real board demands "why?"
- Closes P1 observability gap: MD can trace any year to its causal drivers
- No new sim instrumentation needed -- all data in run_data["years"] per-year dicts
- Epistemic: company observes its own P&L components -- zero sim barrier issues

## Test targets (~16 tests)
- MarginBridge computes net_delta correctly (to minus from)
- bad_debt_delta_gbp negative when bad debt costs rose
- capital_delta_gbp negative when capital costs rose
- residual_gbp near-zero when all components wired correctly
- direction IMPROVEMENT when net_delta > 5000
- direction DETERIORATION when net_delta < -5000
- direction FLAT within +/-5k
- build_margin_bridge_series returns N-1 bridges for N years
- build_margin_bridge_series returns [] for single-year input
- dominant_driver returns "bad debt" when bad_debt_delta is largest absolute contributor
- dominant_driver returns "gross margin" when gross_delta dominates
- Board section renders GREEN row for positive net_delta
- Board section renders RED row when net_delta < -10% of prior year net
- Board section summary line names most damaging year
- policy_cost_delta sums all six levy components correctly
- portfolio_change matches active customer count delta
