# Hedging Strategy — How It Evolved, What Drove It, Whether It Improved

This document is the companion reference for `sim/hedging_strategy.py` and the Phase 1d run (`simulation/run_phase1d.py`): a focused look at the mechanics of how the agent's hedging position changed over time, what signal drove each change, and whether the strategy improved as a result. For the gate-level finding and the full nine-year P&L, see [`docs/observability/PHASE_1d_SUMMARY.md`](observability/PHASE_1d_SUMMARY.md).

## The Mechanism

The agent controls exactly one lever — `hedge_fraction`, the proportion (0.0–1.0) of a contract term's volume locked in at the forward price available on that term's start date. The remainder is bought at spot as it's delivered. There is no menu of pre-set strategies to choose between; the agent starts from a neutral prior and adjusts itself, term by term, using only information that exists at the moment it decides:

1. **Day one — `decide_initial_hedge_fraction()`.** With no track record, the agent starts at `INITIAL_HEDGE_FRACTION = 0.5`. Committing fully to either extreme on day one would be a directional bet on which way prices will move, not a grounded decision; 50/50 is the only starting point that isn't already a guess.
2. **End of each term — `evolve_hedge_fraction()`.** Once a term completes, the agent compares what it actually earned (`actual_margin_gbp`, at whatever `hedge_fraction` it used) against what a fully-naked (100%-spot) version of the *same* term would have earned (`naked_margin_gbp` — same consumption, same real spot prices, same fixed-tariff revenue, only the wholesale-sourcing differs). The difference is the cleanest possible PiT-safe read on what the hedge itself contributed:
   - `difference > +£5.00` → the hedge helped meaningfully; step `hedge_fraction` **up** by `EVOLUTION_STEP = 0.1` (capped at 1.0)
   - `difference < -£5.00` → the hedge cost meaningfully; step **down** by 0.1 (floored at 0.0)
   - otherwise → treat the difference as noise and **hold** the position

Each step is small, bounded, and gradual by design — the rule is built to avoid thrashing on any single term's result. `simulation/hedged_settlement.py::run_hedged_term()` enforces "no foresight" structurally: it settles exactly one contract term at a time and has no way to see beyond it, so `evolve_hedge_fraction()` can only ever act on a fully-completed, already-realised outcome.

## What Signal Drove Each Change

Every adjustment in the run was driven by the same single comparison — actual term margin vs. that term's naked counterfactual — and nothing else. There was no look-ahead, no portfolio-level signal, no cross-customer information sharing; each of the four customers' agents ran its own independent decide → settle → observe → evolve loop against its own contract calendar (terms starting in different quarters: C1 late Dec/early Jan, C2 late Mar/early Apr, C3 late Jun/early Jul, C4 late Sep/early Oct).

The signal was overwhelmingly one-directional through the first half of the simulation: **every customer's agent observed the hedge underperforming naked on every term from 2016 through 2020** (differences ranging from roughly -£12 to -£163), and stepped down 0.1 each time, in lockstep:

| Step | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| Initial | 0.50 | 0.50 | 0.50 | 0.50 |
| After term 0 | 0.40 | 0.40 | 0.40 | 0.40 |
| After term 1 | 0.30 | 0.30 | 0.30 | 0.30 |
| After term 2 | 0.20 | 0.20 | 0.20 | 0.20 |
| After term 3 | 0.10 | 0.10 | 0.10 | 0.10 |
| After term 4 | **0.00** | **0.00** | 0.10 (held — noise) | 0.10 (held — noise) |
| After term 5 | 0.00 (held) | 0.00 (held) | 0.10 (held — noise) | **0.00** |
| After term 6 | 0.00 (held) | 0.00 (held) | **0.00** | 0.00 (held) |

C1 and C2 reached fully naked the fastest because every one of their first five terms produced a clear, signal-sized loss relative to naked. C3 and C4 each hit one term (their fourth) where the difference happened to land inside the ±£5 noise deadband — for C3 that was the term spanning the first half of 2020 into mid-2021 (difference +£3.21, then +£3.17 again the following term), and for C4 it was the term spanning late 2020 (difference +£4.54). Those two near-zero readings were enough to stall the downward march for one extra cycle each — purely a function of where each customer's contract-renewal calendar happened to land relative to the pricing data, not a different reasoning process.

## Did The Strategy Improve?

**By the agent's own learning signal, yes — every step moved in the direction the evidence pointed, consistently and without thrashing.** The deadband held the position steady on the two occasions the signal was ambiguous (both for C3 and C4, both correctly identified as noise — the differences were ±£3-5 against term margins in the hundreds). No customer's agent ever reversed course or oscillated.

**By realised nine-year P&L, the answer is more interesting: the strategy converged on what turned out to be the *better* position for this dataset, but arrived there mostly by accident of timing rather than foresight.** The full-window numbers in the Phase 1d summary show naked beat actual in *every single year* from 2016 to 2023 — meaning a hypothetical agent that had simply started at 0.0 and never moved would have outperformed every one of these four agents over the whole window. The agents that moved to 0.0 fastest (C1, C2) minimised their "cost of learning"; the one that moved slowest (C3) paid for it with the lowest margin in the book (£1,148.07 vs. C1's £3,170.51). So: the *direction* of the evolution was correct for this market regime, the *speed* of getting there determined how much each customer paid to find that out, and the underlying rule had no way to know in advance that naked would keep winning — it only ever found out one term at a time, the hard way.

This is the central tension the gate review should weigh: a rule that reacts only to its own recent, realised outcomes will reliably converge toward "what has been working" — but in a market that experienced one sustained regime (calm, falling prices) for the agent's entire formative period and then a sharp regime change (the 2021-2022 crisis) right as several agents were finishing their transition to fully naked, "what has been working" and "what protects against the thing that's about to happen" pointed in opposite directions. See the Phase 1d summary's Open Questions section for the full discussion of this recency-bias / regime-change-blindness finding and its implications for Phase 1e.

---

## Phase 1e — Capital Physics, Same Rule, Different Incentives

Phase 1e ran the same evolution rule (completely unchanged) against the same nine-year window, with one structural difference: **holding naked wholesale-price exposure now costs money.** A real supplier carrying unhedged volume must post collateral against the Value-at-Risk of that exposure, and that collateral has an opportunity cost (WACC=10%, annualised). `sim/risk_engine.py` prices this from real historical SSP volatility — dual-window VaR (σ_recent coefficient of variation vs. σ_stressed regulatory floor), monthly cost of capital deducted from the shared portfolio treasury every period.

The four agents were reset to hf=0.50 (Phase 1d's converged 0.00 was a lesson documented, not a position to inherit). Starting treasury: £3,250.

### What Changed — And What Didn't

The evolution rule's comparison now sees **net-of-capital-cost margins** on both sides:

- `actual_term_margin_net` = gross trading margin − actual position's monthly CoC × months in term
- `naked_term_margin_net` = 100%-spot gross margin − fully-naked counterfactual's monthly CoC × months in term

Pricing the counterfactual symmetrically (its own, larger, capital cost for its own, larger, naked exposure) is what makes the signal honest: a naked counterfactual that ignores its own capital burden would overstate how good being naked looks, exactly perpetuating Phase 1d's structural blind spot rather than correcting it.

### What the Run Found

**The central hypothesis was not confirmed.** Capital physics did not produce organic hedging. All four agents converged toward hf=0.00 following the same trajectory as Phase 1d, and arrived there before the crisis arrived:

| | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| Start | 0.50 | 0.50 | 0.50 | 0.50 |
| End of 2017 | 0.30 | 0.40 | 0.40 | 0.40 |
| End of 2019 | 0.10 | 0.10 | 0.10 | 0.30 |
| End of 2021 | 0.00 | 0.00 | 0.30 (crisis peak) | 0.20 |
| Final | 0.00 | 0.00 | 0.10 | 0.10 |

C3 and C4 showed crisis-period hedging signals (their mid-year renewal dates meant crisis exposure was observed while they still had meaningful hedge fractions) and temporarily climbed toward 0.30. But both reverted once conditions normalised, and neither approached the 40-60% "optimal zone" the brief was testing for.

**Why the capital signal was insufficient:**

1. **The self-reinforcing trap at hf=0.00.** Once any agent reached fully naked, the capital cost differential between actual and counterfactual was zero — same exposure → same VaR → same CoC → zero signal. The evolution rule is mathematically blind at the boundary. The 2023 regulatory regime change (σ_stressed: 0.50→1.50, tripling collateral requirements) was completely invisible to C1 and C2 for this reason.

2. **Signal magnitude vs. trading margin noise.** In calm years, the per-term capital cost differential between "partial hedge" and "fully naked" was typically £10–50. The trading margin difference (hedge at forward vs. buy at spot) in the same calm-price years was £15–130 in naked's favour. Capital physics narrowed the gap but didn't flip the sign.

3. **Formative-period learning locked in before crisis.** By mid-2020, C1 and C2 were already at hf=0.00, making the 2021-2022 crisis signals invisible. The same structural recency bias as Phase 1d operated here — capital costs were real, but the calm formative period's verdict was "naked is better" even net of capital, and that verdict was entrenched before the regime changed.

### What Capital Costs Actually Did

Capital costs were **substantial**: £3,527 over 9.5 years (37.6% of gross margin £9,392). Year-by-year gross vs. net:

| Year | Gross | Capital | Net | Regime |
|---|---|---|---|---|
| 2016 | £272 | £88 | £185 | σ_s=0.50 |
| 2017 | £542 | £148 | £394 | σ_s=0.50 |
| 2018 | £370 | £121 | £249 | σ_s=0.50 |
| 2019 | £556 | £86 | £470 | σ_s=0.50 |
| 2020 | £500 | £109 | £392 | σ_s=0.50 |
| 2021 | £300 | **£455** | **-£155** | σ_s=0.50 |
| 2022 | £2,207 | £1,001 | £1,206 | σ_s=0.50 |
| 2023 | £3,177 | £725 | £2,451 | **σ_s=1.50** |
| 2024 | £1,115 | £522 | £593 | σ_s=1.50 |
| 2025 (part) | £352 | £273 | £79 | σ_s=1.50 |

The only net-loss year was 2021 — capital costs (driven by high σ_recent as the energy crisis began building) ate through a compressed gross margin. The portfolio survived because the 2022-2023 crisis windfall (high tariff-forward prices that proved profitable even with spot buying) more than compensated.

The σ_stressed regime change (2023-01-01) immediately flipped all assessments from [CURRENT binds] to [STRESSED binds] — every renewal from that point carried 3× the collateral of the pre-reform era. For fully-naked books (C1, C2), this meant monthly CoC of £17-20/month by 2023-2025, but zero evolution signal to escape it.

### Compound Finding: The Evolution Rule Needs Escape Mechanism

Phase 1e adds a specific, testable architectural constraint to what Phase 1d found about recency bias:

> **Phase 1d finding:** A single-signal momentum rule that only learns "what just happened in one term" cannot distinguish "this cost money because prices fell" from "this protects against a tail risk I haven't seen yet." It converges on what's worked historically, blind to what will work next.
>
> **Phase 1e addition:** Once fully naked (hf=0.00), the capital physics signal disappears entirely — the counterfactual comparison is self-referential. A rule without a floor or an external threshold trigger CANNOT self-correct from full nakedness under the current architecture, regardless of how high capital costs rise. The regulatory regime change proved this: 3× higher collateral, zero behavioural change.

This is the open question Phase 2 must answer: does the Context Handshake model (agent wakes on threshold breach, adjusts one lever, returns to sleep) provide the "escape mechanism" the momentum rule lacks? A risk-committee agent that wakes when treasury drops 10%, or when VaR exceeds stressed floor by 20%, could force partial hedging without needing to compare a current term to an unknowable counterfactual.

### Treasury and Survival

The company survived. Treasury grew from £3,250 to £9,114.38 across 9.5 years. The starting capital was never under serious threat — the worst moment was 2021 (the net-loss year), after which treasury still stood at £4,785.10. The £3,250 floor was set deliberately small; its real purpose was to make administration a *plausible* outcome rather than a guaranteed survival or certain failure, so the administration-event mechanism could be validated. No administration occurred, which means the mechanism was not stress-tested beyond detection. A smaller treasury (£500-1,000) would likely have triggered administration in 2021.

