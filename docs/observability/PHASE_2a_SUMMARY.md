# Phase 2a Summary — SME Segment + Context Handshake

**Run date:** 2026-06-09  
**Window:** 2016-01-01 → 2025-06-07 (9.5 years)  
**Customers:** C1–C4 (resi, PC1) + C5 (25,000 kWh SME, PC3) + C6 (45,000 kWh SME, PC3)  
**Starting treasury:** £18,416.67 (scaled from £3,250 × 85,000/15,000 EAC)  
**Architecture change vs 1e:** true chronological term interleaving; Context Handshake wired  

---

## What Was Built

- `saas/customers.py`: C5 (London small office, EAC 25,000 kWh, PC3, segment=SME) and C6 (Manchester warehouse, EAC 45,000 kWh, PC3, segment=SME) added alongside the four resi customers.  
- `sim/profile_class_3.py` + `sim/data/profile_class_3_gad.csv`: PC3 (non-domestic unrestricted) half-hourly GAD shape, sourced from the UKERC/CEDA archive (same provenance as PC1). PC3 is flatter than domestic PC1 — lower overnight trough, consistent daytime business-hours load. Daily total ~48 kWh at 1 kW average vs PC1's domestic 8–10 kWh at ~0.2 kW average — a 6× consumption differential.  
- `simulation/run_phase2a.py`: chronological term interleaving across all 6 customers. Shape routing by `profile_class` field. `RiskCommitteeMonitor` + `risk_committee_agent` wired into the treasury walk. `data_regime: "historical"` on all records.  
- `sim/cache_store.py`: lightweight JSON cache layer — simulations check before hitting live Elexon API.  
- `background/`: autonomous off-peak background worker infrastructure.  

---

## Headline Result

**SURVIVED.** Treasury £18,416.67 → £27,118.62 (+£8,701.95).

| Item | Value |
|------|-------|
| Gross margin | £25,720.70 |
| Capital costs | £17,018.75 |
| Net margin | £8,701.95 |
| Capital cost ratio | **66.2% of gross** |
| Phase 1e capital ratio (4-customer) | 37.6% |

The SME segment nearly doubled the capital cost burden as a share of gross margin. With SME customers carrying enormous naked volumes (C5: 25× a small flat; C6: 45× a small flat), the collateral requirement dominates the P&L — even in years where the trading margin is healthy, the CoC drain is persistent.

---

## Key Findings

### 1. C6 (warehouse) is net negative: capital costs exceed gross margin

| Customer | Gross margin | Capital costs | Net margin |
|----------|-------------|---------------|------------|
| C6 (SME, 45k kWh) | £5,294.05 | **£6,469.69** | **-£1,175.64** |
| C5 (SME, 25k kWh) | £11,034.74 | £7,021.53 | £4,013.21 |
| C1 (resi, 2.8k kWh) | £3,170.55 | £786.41 | £2,384.14 |

C6 destroyed more value over 9.5 years than it created. The warehouse customer is the supplier's worst account by net margin — more expensive to hold a position against than the total trading margin it generates. This is a structural finding, not a crisis-year artefact: C6 ran negative net in 2016, 2017, 2021, 2022, 2023, 2024, and 2025.

The proximate cause is C6's large EAC (45,000 kWh) combined with sigma_recent consistently above the sigma_stressed floor throughout 2016–2022 (VaR_current dominated, not the stressed floor). VaR_current reached £18,298 in 2022, driving monthly CoC well above the per-period trading margin.

**Phase 2 open question:** is C6 unviable as-priced, or does the tariff pricing model need segment-aware margin loading for high-EAC customers? The current `price_fixed_tariff()` applies the same margin scalar regardless of customer size or segment.

### 2. C6 uniquely escaped the hf=0.00 trap — and learned to over-hedge

C6's hedge_fraction trajectory inverted relative to every other customer:

| Year | C6 hf | Direction |
|------|--------|-----------|
| 2016 | 0.50 → 0.60 | ↑ |
| 2017 | 0.60 → 0.70 | ↑ |
| 2018 | 0.70 → 0.60 | ↓ (brief) |
| 2019 | 0.60 → 0.50 | ↓ |
| 2020 | 0.50 → 0.40 | ↓ |
| 2021 | 0.40 → 0.50 | ↑ |
| 2022 | 0.50 → 0.60 | ↑ |
| 2023 | 0.60 → 0.70 | ↑ |
| 2024 | 0.70 → 0.80 | ↑ |
| 2025 | 0.80 → 0.90 | ↑ |

The evolution rule is working correctly for C6: because C6's naked counterfactual carries vastly larger capital costs than its partially-hedged actual position, the rule consistently sees `naked_net << actual_net` and votes to increase hedging. By 2025 C6 is heading towards fully hedged (hf=0.90→0.90 projected). The rule can self-correct for very large naked volumes — it only fails at hf=0.00 (the self-referential trap) or at very small naked positions where the capital signal is weak relative to noise.

This is architecturally important: the hf=0.00 trap is not universal. It only bites customers whose EAC and capital costs are both too small for the signal to overcome the noise in the comparison. The warehouse customer (45,000 kWh) generates a signal strong enough to keep the rule away from 0.00.

### 3. C5 (25,000 kWh) hit the hf=0.00 trap — same pathology as resi

C5 followed the identical downward spiral as C1–C4 resi customers: monotonically reduced hedging 0.50→0.40→0.30→0.20→0.10→0.00 (2016–2020), then trapped at 0.00 despite VaR_current reaching £21,461 in 2021.

The threshold for the trap appears somewhere between 25k–45k kWh EAC at prevailing price levels. C5's capital costs were large enough to dominate the balance sheet but not large enough to consistently show `naked_net << actual_net` once hedging reduced the naked volume sufficiently. By 2019 (hf=0.10), actual naked volume was only 2,500 kWh — VaR signal too weak relative to term-level trading noise.

**Net margin note:** C5's strong 2022-2023 performance (£474 + £2,661 = £3,135 in two crisis/recovery years, naked) partially redeemed its earlier trajectory. Even trapped at hf=0.00, C5 generated positive net margin in those years because the high tariff rates locked in during 2021-2022 renewals far exceeded the falling 2022-2023 spot prices.

### 4. Capital cost ratio doubled vs Phase 1e — the SME tax

Phase 1e (4 resi customers): 37.6% capital cost ratio.  
Phase 2a (4 resi + 2 SME): 66.2% capital cost ratio.

C5 and C6 together contributed £13,491 of the total £17,019 capital costs (79.3%) on 82.4% of portfolio EAC. Their sigma_recent VaR was consistently well above the sigma_stressed floor (ratio 2–4×) throughout 2016–2022, meaning active collateral = VaR_current (not the stressed floor). The stressed floor only bound in 2023–2025 when spot price volatility fell sharply post-crisis.

**For Phase 2b (gas dual-fuel):** if the gas commodity follows a similar volatility profile, adding even a single large gas SME customer could further overwhelm the resi P&L. Segment-aware margin loading may be a prerequisite for gas customers.

### 5. Context Handshake: mechanism exercised, agent invocations all failed (401)

The monitor fired every ~30 days throughout the entire simulation — the VaR_current > VaR_stressed × 1.20 threshold was met continuously because sigma_recent was consistently above 1.20 × 0.50 = 0.60 (the pre-2023 floor). The context file was written on every trigger. All agent invocations failed with HTTP 401: the `ANTHROPIC_API_KEY` environment variable is not exported to subprocesses launched outside Claude Code's managed environment.

**No actual adjustments landed.** The simulation ran without any risk committee intervention — effectively the same as Phase 1e. The `committee_wake_ups` count is 0 (populated only on successful invocations). The evolution rule ran unchecked.

**Two fixes needed before Phase 2b or any future run:**

**Fix 1 — API key propagation:** The simplest fix is to read the API key at the start of `main()` using an alternative mechanism (e.g., from a `.env` file, a config file, or the Anthropic SDK's default key file location) and pass it explicitly as an environment variable to the agent subprocess. Alternatively, switch `risk_committee_agent.py` to use the Anthropic Python SDK (`anthropic.Anthropic()`) which auto-discovers credentials from `~/.anthropic/` or the standard `ANTHROPIC_API_KEY` env var.

**Fix 2 — VaR trigger recalibration:** The VaR trigger (ratio > 1.20) is too sensitive for this portfolio. It fires continuously even when treasury is healthy and growing, not just when risk is elevated. Two options:
- (a) Add a treasury-health gate: VaR trigger only fires if treasury is ALSO below some threshold (e.g., 12 months of expected running margin), preventing committee wake-ups during good years.
- (b) Raise the ratio threshold from 1.20 to something like 2.0 — only trigger when volatility is truly extreme.
- (c) Make the threshold dynamic: VaR trigger only fires if VaR_current > VaR_stressed × ratio AND current treasury < 1.5 × starting_treasury.

The treasury drawdown threshold (>10% from 12-month peak) is well-calibrated — it correctly tracked the 2021 treasury drawdown from ~£21,900 peak to the ~£19,900 trough. The VaR trigger needs the redesign.

### 6. Year-by-year portfolio P&L

| Year | Gross | Capital | Net | Treasury | Regime |
|------|-------|---------|-----|----------|--------|
| 2016 | 1,067 | 778 | 290 | 18,973 | pre-2023 |
| 2017 | 1,737 | 893 | 845 | 19,644 | pre-2023 |
| 2018 | 895 | 516 | 379 | 20,296 | pre-2023 |
| 2019 | 1,474 | 406 | 1,068 | 21,330 | pre-2023 |
| 2020 | 1,367 | 552 | 815 | 21,611 | pre-2023 |
| **2021** | **685** | **2,285** | **-1,600** | **20,454** | CRISIS |
| **2022** | **6,355** | **5,108** | **1,248** | **23,736** | CRISIS |
| 2023 | 8,417 | 3,290 | 5,127 | 27,195 | post-2023 (×3σ) |
| 2024 | 2,817 | 2,151 | 666 | 27,192 | post-2023 (×3σ) |
| 2025 | 905 | 1,040 | -135 | 27,119 | post-2023 |

2021 net margin: -£1,600 (Phase 1e was -£154). The SME segment made 2021 dramatically worse — C6's 2021 net alone was -£985, C5 was -£661. The large naked SME positions carried enormous capital costs during the energy crisis.

2023 was the redemption year: £5,127 net — the post-2023 sigma_stressed tripling (0.50 → 1.50) forced capital costs through the stressed floor for the first time, but gross margin was so strong (crisis-era tariffs vs falling post-crisis spot) that net margin was the highest of any year.

---

## Key Decisions

- **C6 pricing model inadequacy confirmed:** The current `price_fixed_tariff()` flat-margin model is insufficient for large SME customers. C6's gross margin never covered its capital costs — it required a higher tariff loading to be viable. This is a Phase 2+ decision for Rich.
- **Context Handshake API key fix:** Must be resolved before any run that expects committee interventions. Add API key to a persistent credentials file readable by subprocess, or switch to SDK-based invocation.
- **VaR trigger threshold:** Needs recalibration before Phase 2b. Current 1.20 threshold fires every cooldown period. Proposed range: 2.0–3.0, plus a treasury-health gate.
- **Cooldown adequacy:** 1440-period (~30 day) cooldown is appropriate in principle but produces too many wake-up attempts given the over-sensitive trigger. Once threshold is recalibrated, cooldown may need extending to quarterly (4,320 periods).

---

## Open Questions

1. **Is C6 unviable at current pricing, or is this a margin-loading failure?** If the tariff margin were scaled up for high-EAC SME customers, C6 could be profitable. But the current `price_fixed_tariff()` has no segment/size signal.
2. **Is the hf=0.00 trap size-dependent?** C6 (45k kWh) escaped it; C5 (25k kWh) didn't. Is there an EAC threshold? Or is it about the ratio of CoC signal to term-level trading noise?
3. **API key mechanism for background simulations:** How should frontier LLM agents be invoked from non-interactive processes? Options: SDK auto-discovery from `~/.anthropic/`, explicit credentials file, or delegating risk committee decisions back to the main session via a file-based handoff.
4. **Should Phase 2b start given C6's net-negative outcome?** Adding a gas dual-fuel product requires a working risk committee (so the Committee can flag unhedgeable gas exposure). Starting Phase 2b before fixing the committee invocation would produce the same silent failure.

---

## Token Efficiency

| Activity | Tokens (frontier) | Tokens (local) |
|----------|------------------|----------------|
| Orchestration (run_phase2a.py, hand-written) | ~4,000 | 0 |
| profile_class_3.py (delegated to qwen2.5-coder:14b) | ~800 (review) | ~3,500 |
| PHASE_2a_SUMMARY.md (this doc, hand-written) | ~3,500 | 0 |
| Background worker files | ~2,000 | 0 |
| Data provenance doc | ~1,200 | 0 |
| **Session total (estimated)** | **~11,500** | **~3,500** |

Deliverables: 6 new files committed, 4 modified, 1 full simulation run, 1 background worker infrastructure. No speculative dead-ends.
