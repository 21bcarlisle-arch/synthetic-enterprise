# Phase AH: Company Portfolio Intelligence Pack

**Status:** Draft proposal — 4h opt-out gate.
**Proposed by:** Claude Code autonomous session, 2026-06-30

---

## Context

Phases AD/AC/AB/AA built rich CRM intelligence books (churn risk, repricing,
EAC drift, flexibility potential). Phase AG made flexibility revenue visible in
the annual report. But the CRM intelligence books are NOT wired into the report
pipeline — their outputs never appear in the annual report.

The result: the company has intelligence, but no board-level synthesis.
A real UK energy supplier's board pack would say:
- "3 customers are CRITICAL repricing priorities (£X margin at risk)"
- "Portfolio churn rate is 14%, concentrated in bill-shock accounts"
- "Flexibility enrollment at 40% of potential; DFS gap = £X/yr"
- "ToU launch HOLD: EV cross-subsidy exceeds £500 threshold"

None of this is currently visible.

---

## What Phase AH does

Add a `_section_portfolio_intelligence_pack(data)` function to annual_report.py
that synthesizes observable intelligence from EXISTING pipeline data:

### 1. Retention Intelligence
From `retention_log` and `no_offer_churn_log`:
- Retention coverage rate (offers made / at-risk events)
- Offer acceptance rate
- Total margin protected by retention offers
- No-offer churns by reason (blind miss vs deliberate pass)
- Estimated margin loss from avoidable churns

### 2. Flexibility Revenue Intelligence
From `flexibility_revenue_summary` (wired in Phase AG):
- Year-on-year enrollment growth rate
- Revenue per enrolled customer (CM vs DFS)
- Enrolled vs theoretical maximum (based on portfolio size)
- Strategic: "DFS growing X%/yr since launch; prioritise EV customer acquisition"

### 3. Churn Pattern Analysis
From `company_event_log`:
- Churn by trigger: bill_shock vs home_move vs competition
- Which years had highest churn pressure (company-visible metric)
- Post-retention survival: did retained customers stay?

### 4. Strategic Outlook (final year)
Computed from portfolio trends:
- EV penetration trajectory (% per year from flex_by_year enrolled data)
- Flexibility revenue growth rate (CAGR since DFS launch 2022)
- Net retention signal: is the portfolio growing or shrinking?

### 5. Board Recommendations
2-3 bullet point strategic recommendations derived from the above:
- "Churn risk: X% of accounts have estimated loss >£Y — prioritise retention outreach"
- "Flexibility: enrol additional Z customers to close £A/yr revenue gap"
- "ToU: signal HOLD correct; revisit when EV penetration exceeds 50%"

---

## Files

- `saas/reporting/annual_report.py`: `_section_portfolio_intelligence_pack(data)` + wire after executive summary
- `tests/saas/reporting/test_phase_ah_intelligence_pack.py`: ~10 tests

---

## Tests (~10)

1. Returns empty when no retention log
2. Retention coverage rate computed correctly
3. Offer acceptance rate computed correctly
4. Flexibility enrollment growth rate non-zero when multi-year data
5. Revenue per enrolled customer computed from per_year data
6. Board recommendations section present
7. Churn trigger breakdown includes bill_shock category
8. No-offer churns counted correctly
9. Strategic outlook includes EV penetration metric
10. Graceful degradation when event log empty

---

## Fidelity delta

The board pack section transforms the annual report from a financial record into
a company intelligence output. For the first time, the company-layer analytics
produce actionable synthesis rather than individual metrics. This is the moment
the company stops being a ledger and starts being an operating business that knows
what it should do next.

---

## Gate

4h opt-out from proposal time (~2026-06-30T00:00Z). Auto-proceed at ~04:00 UTC.
