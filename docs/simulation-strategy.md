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
