# Phase 4a Summary — Customer Value Layer

Staged instruction (`docs/staging/PHASE_4a_INSTRUCTION.md`, actioned
2026-06-13): build in order 4a-1 cost to serve, 4a-2 churn model, 4a-3 CLV
(Shifted-BG via PyMC-Marketing), 4a-4 home move win rate, 4a-5 enterprise
value function. Sub-phases are appended below as each clears its
REVIEW_GATE.

---

## 4a-1 — Cost to Serve Model

### What Was Built
- `saas/cost_to_serve.py` — new pure module, `build_cost_to_serve()` and
  `cost_to_serve_for_period()`. Adds an operational-cost layer on top of
  `simulation/portfolio_pnl.py`'s `margin_gbp` (revenue minus wholesale cost
  only), producing `net_margin_gbp = margin_gbp - cost_to_serve_gbp`.
  - **Fixed overhead**: an annual £/account figure (billing/IT/customer
    service + smart-meter operation), divided across
    `SETTLEMENT_PERIODS_PER_YEAR = 17,520` (48 x 365). resi = £55/yr,
    SME = £120/yr.
  - **Bad debt**: a flat percentage of each period's revenue. resi = 2%,
    SME = 1% (SME accounts are credit-checked at acquisition).
  - Each commodity contract (electricity or gas) is costed as its own
    account — a dual-fuel household (e.g. C1 + C1g) carries fixed overhead
    twice, mirroring separate billing/metering relationships even when
    bundled commercially.
- `tests/saas/test_cost_to_serve.py` — 5 tests: per-period arithmetic, resi
  vs SME overhead comparison, empty-input zeroing, multi-period/multi-customer
  aggregation, and unknown-customer KeyError.

### Key Decisions Made
- **Segment-keyed cost tables, not per-customer**: matches the existing
  `saas/customers.py` segment field (`"resi"` / `"SME"`) rather than adding
  new per-customer attributes — keeps the model a thin layer that's easy to
  recalibrate later.
- **Bad debt as a per-period % of revenue, not a year-end true-up**: this
  model has no arrears-ageing concept, so the simplest point-in-time-safe
  approximation is applied every period.
- **Cost-to-serve computed as a standalone aggregation over settlement
  records**, mirroring `simulation/portfolio_pnl.py`'s shape
  (`portfolio` + `by_customer`) so it composes the same way in downstream
  reporting/orchestration.

### Open Questions
- Applying this to the full Phase 2b 9.5-year settlement output (to produce
  headline net-of-cost-to-serve figures alongside the £13,970.60 net margin)
  requires re-running `simulation/run_phase2b.py` to regenerate settlement
  records — not done in this increment to avoid a multi-hour re-run; flagged
  as a follow-up for whoever next runs a full-window simulation.
- Cost figures (£55/£120 overhead, 2%/1% bad debt) are seed estimates based
  on rough UK retail cost-stack proportions, not calibrated against any real
  dataset — a future increment could calibrate against published Ofgem
  default-tariff-cap cost-stack breakdowns.
- Dual-fuel double-counting of fixed overhead (4a-1's "Key Decisions") may
  overstate cost-to-serve for C1-C4 vs a real combined-billing relationship —
  same open question raised for billing in Phase 3a, now compounding into
  cost as well as bill-shock perception.

### Token Efficiency
- Frontier (hand-written): `saas/cost_to_serve.py`,
  `tests/saas/test_cost_to_serve.py`, this summary section. Small,
  schema-adjacent pure module — same delegation calculus as
  `saas/customer_reaction.py` (Phase 3a).
