# Phase 1e Summary — Nine-Year Portfolio Run with Enterprise Risk Physics

## What Was Built

1. **sim/risk_engine.py** — dual-window Value-at-Risk module (delegated to qwen2.5-coder:14b, frontier-reviewed). Two volatility views: `sigma_recent` (trailing-12-month coefficient of variation of System Sell Price — PiT-safe rolling volatility, dimensionless) and `sigma_stressed` (regime-dependent regulatory floor: 0.50 before 2023-01-01, 1.50 from that date — a PiT-safe historical regulatory change the agent experiences when it happens, not foresight). Active collateral = max(VaR_current, VaR_stressed) at 90% one-tailed confidence (z=1.645). Monthly Cost of Capital = Active Collateral × WACC / 12, WACC=0.10. Delegation quirks: model drifted on function name (assess_risk→assess_term_risk), parameter order, and markdown fencing — all corrected at frontier review. Core numeric logic was correct on first generation.

2. **simulation/hedged_settlement.py** (updated — hand-written) — capital cost now folds into every half-hourly settlement period as `capital_cost_gbp` (monthly CoC allocated proportionally across actual settled periods in each calendar month, using a post-loop grouping pass so DST 46/50-period days are handled exactly) and `net_margin_gbp = margin_gbp - capital_cost_gbp`. Parameter `monthly_cost_of_capital_gbp` added to `run_hedged_term`.

3. **simulation/run_phase1e.py** (hand-written — Phase 1d lesson: orchestration touching settlement-record schemas produces wrong field names when delegated) — full 9.5-year portfolio orchestration: all four customers reset to `hedge_fraction=0.50`, shared single £3,250 treasury, true chronological interleaving of all customers' records for the administration-event trigger (sorted by settlement_date, settlement_period, customer_id), dual risk assessment per term (actual position + fully-naked counterfactual, both under the same capital physics for apples-to-apples evolution signal), Phase 1d's unchanged `evolve_hedge_fraction()`.

## Key Findings

### 1. Company survived — treasury grew from £3,250 to £9,114.38

No administration event triggered. Treasury by year-end:

| Year | Treasury £ | Net margin £ | Regime |
|------|-----------|-------------|--------|
| 2016 | 3,435.05 | +185.05 | σ_s=0.50 |
| 2017 | 3,829.00 | +393.95 | σ_s=0.50 |
| 2018 | 4,077.91 | +248.90 | σ_s=0.50 |
| 2019 | 4,548.16 | +470.26 | σ_s=0.50 |
| 2020 | 4,939.74 | +391.58 | σ_s=0.50 |
| 2021 | 4,785.10 | **-154.64** | σ_s=0.50 (crisis) |
| 2022 | 5,990.63 | +1,205.53 | σ_s=0.50 (crisis) |
| 2023 | 8,441.98 | +2,451.35 | **σ_s=1.50** |
| 2024 | 9,034.97 | +593.00 | σ_s=1.50 |
| 2025 (partial) | 9,114.38 | +79.40 | σ_s=1.50 |

Full-window portfolio:
- **Gross margin:** £9,391.91 | **Capital costs:** £3,527.54 (37.6% of gross) | **Net margin:** £5,864.38
- Per-customer net: C1 £2,384.14 | C2 £1,815.75 | C3 £514.77 | C4 £1,149.72

### 2. The central hypothesis was not confirmed — capital physics did not produce organic hedging

Phase 1e's thesis: introducing real collateral costs would make nakedness organically expensive, causing the unchanged evolution rule to discover a different (hedged) equilibrium. **This did not happen.** All four agents converged toward hf=0.00, following the same trajectory as Phase 1d — the calm 2016-2020 formative period drove the same de-hedging momentum even net of capital costs:

| Agent | Start | 2018 | 2020 | 2021 (crisis) | Final |
|-------|-------|------|------|----------------|-------|
| C1 | 0.50 | 0.30 | 0.10→**0.00** | 0.00 (trapped) | **0.00** |
| C2 | 0.50 | 0.30 | 0.10→**0.00** | 0.00 (trapped) | **0.00** |
| C3 | 0.50 | 0.30 | 0.10→0.20→**0.30** | 0.20→0.10 | **0.10** |
| C4 | 0.50 | 0.40 (hold) | 0.20→**0.30** | 0.20→0.10 | **0.10** |

C3 and C4 were the partial exception: their July and October renewal dates meant crisis-era terms were still being settled while hedge fractions > 0.10 were in place. They temporarily climbed toward 0.30 during 2020-2021. Neither approached the 40-60% zone the brief was testing for, and both reverted post-crisis.

### 3. The self-reinforcing trap: evolution rule is mathematically blind at hf=0.00

**The most architecturally significant finding.** Once any agent reaches hf=0.00:

- Actual naked volume = EAC × (1 - 0.00) = EAC
- Counterfactual naked volume = EAC (by definition of fully-naked counterfactual)
- Therefore: same VaR → same collateral → same CoC → `actual_net - naked_net = 0.00`
- The evolution signal is zero. The rule holds position.

**This means capital cost increases are structurally invisible to a fully-naked agent.** The 2023 regulatory regime change (σ_stressed: 0.50→1.50), which tripled collateral requirements for naked books, was completely undetectable by C1 and C2:

- C2 in 2025: active_collateral=£2,414 | monthly_coc=**£20.12** (£241/year) — yet hf=0.00, evolution signal=0, no change.

Once established, the fully-naked equilibrium is self-reinforcing regardless of how large the capital cost grows — the rule has no mechanism to escape it without external intervention.

### 4. Capital costs were substantial and regime-shifted sharply in 2023

Year-by-year capital costs and their relationship to gross margin:

| Year | Gross £ | Capital £ | Net £ | Capital/Gross |
|------|---------|-----------|-------|--------------|
| 2016 | 272.72 | 87.66 | 185.05 | 32.1% |
| 2017 | 541.75 | 147.80 | 393.95 | 27.3% |
| 2018 | 369.73 | 120.83 | 248.90 | 32.7% |
| 2019 | 555.83 | 85.58 | 470.26 | 15.4% |
| 2020 | 500.32 | 108.74 | 391.58 | 21.7% |
| **2021** | **300.45** | **455.10** | **-154.64** | **151.4%** |
| 2022 | 2,206.55 | 1,001.01 | 1,205.53 | 45.4% |
| 2023 | 3,176.79 | 725.45 | 2,451.35 | 22.8% |
| 2024 | 1,115.37 | 522.37 | 593.00 | 46.8% |
| 2025 | 352.39 | 272.99 | 79.40 | 77.5% |

**2021** was the only net-loss year: the energy crisis began building σ_recent (spiking to 1.3-1.6 across all four customers), driving VaR and CoC to record levels for the fully/mostly-naked books, while gross margins were compressed relative to the crisis windfall that came in 2022. The portfolio survived because the £4,785 treasury buffer (accumulated from profitable 2016-2020 years) could absorb the £154 net loss.

**2023 regime change** (σ_stressed: 0.50→1.50) immediately caused all renewal assessments to switch from [CURRENT binds] to [STRESSED binds] — collateral sized at 3× the pre-reform floor for all remaining terms. The capital cost impact was partially masked by strong 2023 gross margins (£3,177) driven by the crisis-era tariff pricing.

### 5. σ_recent was consistently above σ_stressed in 2016-2022

The stressed regulatory floor was non-binding throughout the calm period **and** the crisis years:

- **2016:** σ_recent = 1.0–1.6 — far above the 0.50 floor. The initial post-P305 data was extremely volatile (market formation effect), making early CoV measurements inflated. CURRENT always bound.
- **2017-2019:** σ_recent fell to 0.5–0.8 as prices stabilised. The regulatory floor first started binding in 2019 for C2 and C3 terms (σ_recent=0.42 and 0.46, below the 0.50 floor). First STRESSED binds observed.
- **2020-2022:** σ_recent spiked back above the floor as energy crisis volatility built. CURRENT binds throughout.
- **2023 onward:** The regime change to σ_stressed=1.50 made the floor definitively binding for every single assessment — no observed σ_recent exceeded 1.0 post-crisis.

The 2023 change was the ONLY mechanism that permanently flipped the binding constraint — and it arrived after C1/C2 had fully converged.

### 6. C3 shows partial crisis learning — a timing effect

C3's July renewal dates produced a natural experiment:
- Term 4 (2020-06-30, hf=0.10): actual_net=−£42.69 vs naked_net=−£48.54 → hedge beat naked by £5.85 → UP to 0.20
- Term 5 (2021-06-30, hf=0.20): actual_net=−£94.43 vs naked_net=−£126.30 → hedge beat naked by £31.87 → UP to 0.30 (peak)
- Term 6 (2022-06-30, hf=0.30): actual_net=£165.36 vs naked_net=£215.04 → hedge underperformed by £49.67 → DOWN to 0.20

C3 climbed during the crisis because its mid-year renewals coincided with significant crisis-era settled periods (July 2020 captured COVID volatility; July 2021 captured early energy spike). But once conditions normalised and naked delivered better net returns in 2022, the evolution reverted. This is consistent with the rule operating exactly as designed — it has no memory of whether the formative period was representative.

## Key Decisions

1. **Counterfactual capital cost priced symmetrically** — the fully-naked counterfactual carries its own (larger) capital cost in the evolution signal comparison. This was the core architecture decision enabling Phase 1e's test. The finding that it was insufficient to flip the equilibrium is a discovery, not a design error — the mechanism worked correctly.

2. **Phase 1d's evolution rule carried over completely unchanged** — per the backlog spec. The structural blindness at hf=0.00 is a property of the rule as designed, now documented precisely.

3. **Delegation boundary worked** — risk engine (pure numeric functions) delegated to qwen2.5-coder:14b; orchestration hand-written. The delegation produced correct core math; the frontier corrected name drift and markdown fencing at review. Zero schema-related field-name errors (the failure pattern that motivated hand-writing orchestration in Phase 1d).

4. **Shared single-pool treasury** required chronological interleaving — the architecture correctly sorts all four customers' records by (date, period, customer_id) before the treasury walk, which is the only way an administration event can be triggered correctly when capital costs from four concurrent books share one balance sheet.

## Open Questions

1. **How should the hf=0.00 trap be broken?** Three options documented in `docs/simulation-strategy.md`: (a) minimum hedge floor (hf never below 0.10), (b) direct capital-cost awareness term in the evolution signal, (c) risk-committee agent waking on hard thresholds (treasury −10%, VaR > stressed floor × 1.2). Option (c) — the Context Handshake execution model — is documented in MASTER_BACKLOG.md and is the natural Phase 2 architecture direction.

2. **Was £3,250 starting treasury the right stress level?** The company survived comfortably. £500-1,000 would likely have triggered administration in 2021. The administration-event mechanism was validated as implemented but not stress-tested in practice.

3. **Is the 2021 VaR calculation meaningful when all books are nearly naked?** In the fully-naked state, collateral requirements scale linearly with EAC. C4 (5,500 kWh, largest book) carried active_collateral of £3,806 in a single term (2021-09-30) — larger than the entire portfolio starting treasury. In a real company, capital would be managed at portfolio level with netting effects; per-customer capital stacking is conservative.

4. **What would a higher WACC or tighter sigma_stressed do?** These parameters were set at mid-range (WACC=0.10, σ_stressed=1.50). A higher effective WACC (e.g. 0.15 for a thin-margin supplier with expensive debt) would have increased the capital drag enough that the 2021 net loss would have been larger. Phase 3 calibration should test parameter sensitivity.

## Token Efficiency

Phase 1e session token breakdown (frontier + local, approximate):
- Frontier (this session, ongoing — see token-log.md for end-of-session entry): TBD
- Local (qwen2.5-coder:14b): 2,301 prompt / 2,112 eval (risk_engine.py delegation)
- Local (qwen2.5:7b): ~1,200 prompt / ~900 eval (this summary draft — reviewed and substantially rewritten by frontier)

---

*Drafted by qwen2.5:7b (local, via tools/delegate_ollama.py --task-type analysis), reviewed, edited, and extended by the frontier orchestrator — Phase 1e analysis increment. qwen draft provided structural skeleton (What Was Built, Key Decisions, Open Questions); frontier added findings 3-6 in full, rewrote finding 2 agent-trajectory table, and added capital cost data tables, σ_recent regime analysis, and the compound Phase 1d→1e finding statement.*
