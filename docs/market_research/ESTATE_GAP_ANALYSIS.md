# Estate Gap Analysis — Poesys vs. Real Platform Functional Inventories

Desk analysis (COMPETITOR_LANDSCAPE_GAP_CHECK.md, P3, token-cheap, no build work). Cross-checks
the Phase RW SaaS Estate Coverage Map (`docs/architecture/SAAS_COVERAGE_MAP.md`, 22 categories)
against the functional inventories in `docs/market_research/COMPETITOR_PLATFORMS_2026.md` (an
unsourced, AI-assisted survey — treated as structural reference only, see ASSUMPTIONS.md's
provenance entry; no quantitative claim from it is used as a figure below).

Every capability the companion instruction named to sweep is classified against Poesys's actual
codebase (verified by grep/read against real modules, not recalled from memory).

## Classification table

| Capability | Classification | Evidence |
|---|---|---|
| Dunning & algorithmic payment plans | **COVERED** | `simulation/arrears_engine.py` (missed-payment → notice cascade → payment plan → write-off), `company/billing/payment_deferral.py`, `company/billing/collections.py` (Phase QD emergent bad debt — real, not injected) |
| Retroactive bill recalculation | **COVERED** | `company/billing/smart_meter_reconciliation.py` (estimated-AQ-vs-actual-reads reconciliation, credits/debits) + `company/billing/back_billing.py` (SLC 31A 12-month recovery cap enforced on top of it) — the two together are the same "estimate now, true-up later, capped by law" mechanic MaxBill's engine describes |
| MHHS half-hourly settlement | **COVERED** | `company/market/mhhs_tracker.py` (Market-wide Half-Hourly Settlement programme milestone tracking) — the underlying settlement itself has been HH from day one (the sim's whole premise); this module tracks the *reform programme* specifically |
| Market messaging / switching flows (DCC-analogue) | **GAP** (already named) | `SAAS_COVERAGE_MAP.md` already classifies this bucket C, not yet a named adapter — settlement/registration data flows directly from Elexon ingestion, no DTS/DIP-shaped boundary modelled. Confirmed still true, no change. |
| Broker & partner commission (PRM) | **COVERED** | `company/crm/tpi_book.py` (Phase OA, I&C Broker/TPI Commission Model — Standard Energy Broker registered at a real Ofgem-calibrated rate) |
| Portfolio recosting / margin leakage detection | **COVERED, different mechanism — genuine partial gap noted** | `saas/cost_to_serve.py` + the consistency-gate discipline make margin-truth a property recomputed from real settlement data every run (the architectural bet `SAAS_COVERAGE_MAP.md` already stakes — bucket A, "eliminated by architecture," not recreated as a bolt-on analytics layer). What is genuinely absent: a *live, per-event* trigger — Gorilla's specific claim is that a mid-contract usage-pattern change instantly recosts that one contract and surfaces the leakage before the next bill; Poesys recomputes at report-generation time (per run), not on a live customer-level event. Worth naming as a real, narrow gap distinct from the batch-vs-real-time architecture debate the estate map already resolved. |
| Forecast-driven hedge volume dictation | **COVERED** | `company/market/hedging_schedule.py` (forward delivery vs open position by tenor) + `company/market/portfolio_position.py` + the existing hedge-fraction evolution/risk-committee machinery (`sim/hedging.py`, `sim/risk_committee.py`) — hedge volume is driven by portfolio demand forecast, not a fixed policy |
| DERMS / flex & export credits | **COVERED** | `saas/demand_response.py`, `company/market/ic_flexibility_revenue.py` (Phase NX/NY, I&C demand response + capacity-market/DFS revenue), `company/billing/seg_register.py` (Smart Export Guarantee register, SI 2020/1297), `company/billing/fit_legacy_register.py` (legacy FiT export payments pre-SEG) |
| Pass-through (Amber-style) tariff as a product-range candidate | **COVERED** | `simulation/hedged_settlement.py::run_flex_term()` (Phase 41a) already implements the core pattern: no locked unit rate, customer settles against a rolling reference price + a fixed markup, supplier hedges at the same reference — structurally the same rate design as Amber's pass-through model. Device-level automated price-response (Amber's "SmartShift" halting EV charging / forcing battery export at price spikes) is NOT modelled — that is a genuine, separate gap (see below), distinct from the tariff/rate-design question this item actually asked about. |
| Migration tooling | **OUT-OF-SCOPE (for now)** | No real customer base exists to migrate from — this is explicitly a go-live-analysis-phase concern (Home/Project pages' own roadmap framing: "the final phase... is a go-live analysis"), not a simulation-fidelity gap today |

## Additional finding: one existing estate-map backlog item is stale

`docs/architecture/SAAS_COVERAGE_MAP.md`'s own backlog item 1 ("Debt journey extension:
write-off is not terminal... add DCA-placement/debt-sale stage economics") is now **DONE** —
Phase QS (2026-07-08) built exactly this (`WRITTEN_OFF → PLACED_WITH_DCA → RECOVERED|SOLD` with
real recovery-rate/commission/haircut economics, `simulation/arrears_engine.py`). Backlog item 2
(credit bureau as a collections-strategy feed, not just acquisition) remains genuinely open. The
estate map document itself needs a one-line refresh at its next retro-cadence pass — not done
here, flagged only (this task is desk analysis, not a build).

## Ranked GAP items by fidelity value

1. **Device-level automated price-response for flex/pass-through customers** (the Amber
   "SmartShift" pattern: auto-halt EV charging / force battery export at price spikes). The
   *rate design* is already covered (`run_flex_term`); what's missing is the demand-response
   *automation layer* reacting to the household's own tariff in real time. Would touch
   `simulation/household_demand.py` / `saas/demand_response.py`. Fidelity value: meaningful for
   any future domestic flex-tariff storyline, low urgency while the portfolio stays I&C-dominated.
2. **Live per-event portfolio-margin-leakage trigger** (vs. the current per-run batch recompute).
   Would touch `saas/cost_to_serve.py` + the decision-event ledger to fire a flagged event when a
   mid-contract consumption-pattern shift crosses a leakage threshold. Fidelity value: makes the
   "margin truth in every decision" architectural claim demonstrably *live*, not just
   *recomputed-fresh* — closes the one real distinction between Poesys's bucket-A claim and
   Gorilla's actual product behaviour.
3. **Market messaging / DCC-analogue boundary adapter** (unchanged from the existing estate-map
   backlog — re-surfaced here because it's the only capability in this sweep still genuinely
   unbuilt with no partial coverage). Fidelity value: this is the last of the four planned-boundary
   adapters (credit bureau is live; PSP, DCC comms, and this one remain interfaces-not-yet-built)
   named in the estate map's own bucket-C list — a real go-live-path item, not urgent pre-scale.

Nothing above authorises implementation. These three feed the P-5 backlog for the director's
next re-rank.
