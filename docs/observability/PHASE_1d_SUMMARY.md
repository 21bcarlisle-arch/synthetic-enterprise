# Phase 1d Summary — Agent-Discovered, Time-Evolving Hedging Strategy

## What Was Built
- `sim/hedging.py` — `settle_hedged_period()`: pure per-settlement-period economics. Splits a period's consumption into a hedged share (priced at the forward price locked in at the contract term's start — the same synthetic number that sets the customer's tariff, keeping Law 3 self-consistent) and an unhedged share (bought at real spot), and returns the resulting revenue/cost/margin split.
- `sim/hedging_strategy.py` — the agent's entire decision-and-evolution logic, with **no pre-set strategies handed to it** (this replaced the original "test three fixed strategies" brief mid-phase): `decide_initial_hedge_fraction()` returns a neutral 50/50 starting position plus its reasoning; `evolve_hedge_fraction()` compares a just-completed term's actual margin against a naked (100%-spot) counterfactual for that exact same term and steps the position up, down, or holds — bounded (`EVOLUTION_STEP = 0.1`, clamped to [0.0, 1.0]) and deadbanded against noise (`MARGIN_TOLERANCE_GBP = 5.0`).
- `simulation/hedged_settlement.py` — `run_hedged_term()`: settles exactly **one** contract term in isolation. This is what makes "no foresight" structural rather than a documentation promise — the function has no way to see beyond the single term it's asked to settle.
- `simulation/run_phase1d.py` — orchestrates the full renewal-aware run across all four customers and the entire 2016-01-01 → 2025-06-07 window: sequences each customer's terms through decide → settle → observe → evolve, builds the naked counterfactual for every period, and reports annual P&L, year-by-year hedge-effectiveness (actual vs. naked), crisis-vs-stable totals, and the full-window/per-customer breakdown.
- `docs/data-sources/gas-nbp.md` — reference doc on UK gas/NBP pricing and the volume→energy conversion (kWh = V × CF × CV / 3.6), written for future phases that may extend the commodity model beyond power.
- `docs/instructions/MASTER_BACKLOG.md` — Phase 1d section replaced in place with the revised agent-discovered spec (the original "three fixed strategies" design was superseded before implementation began).

Tenor is held fixed at 12 months — one "annual strip" instrument matched 1:1 to the contract term, priced at the same forward price that sets the customer's tariff. This is a deliberate, documented simplification (see the `run_phase1d.py` module docstring): blending overlapping multi-tenor positions within a single contract year would require nested hedge-book tracking without changing the question this phase actually tests.

## The Agent's Initial Reasoning
> "With no track record, committing fully to either extreme (fully hedged or fully naked) would be a directional bet on prices. Starting at 50/50 allows the agent to learn from its own outcomes without making an initial assumption."

All four customers' agents started at `hedge_fraction = 0.50` — the only position that isn't already a guess about which way prices will move.

## How The Strategy Evolved, Year By Year
Every customer's agent followed the same arc: it observed the hedge underperforming the naked counterfactual on **every single completed term from 2016 through 2020**, and mechanically stepped down by 0.1 each time — reaching (or nearly reaching) fully naked *before* the 2021-2022 crisis arrived:

- **C1** (terms start late Dec/early Jan): 0.50 → 0.40 → 0.30 → 0.20 → 0.10 → **0.00 by the term starting 2020-12-30** — a full year before the first crisis term (2021-12-30, hedge price £395.88/MWh). Held at 0.00 through both crisis terms and beyond.
- **C2** (terms start late March/early April): 0.50 → 0.40 → 0.30 → 0.20 → 0.10 → **0.00 by the term starting 2020-03-31** — over a year clear of its first crisis term (2021-03-31, £206.29/MWh). Held at 0.00 throughout.
- **C3** (terms start late June/early July): 0.50 → 0.40 → 0.30 → 0.20 → **0.10, where it stalled** — terms 4 and 5 (2020-06-30 and 2021-06-30) landed inside the ±£5 noise deadband (differences of +£3.21 and +£3.17) and held the position unchanged. C3 entered **both** crisis terms (2021-06-30 at £169.62/MWh and 2022-06-30 at £253.73/MWh) still 10% hedged, and only reached 0.00 at term 7 (starts 2023-06-30) — the one customer the evolution rule moved too slowly to fully de-risk before the crisis hit.
- **C4** (terms start late Sept/early Oct): 0.50 → 0.40 → 0.30 → 0.20 → **0.10, also stalled** by a noise-band result (term 4, 2020-09-30, difference +£4.54). C4 entered its first crisis term (2021-09-30, £378.36/MWh) still at 0.10, took a -£65.48 hit relative to naked on that term, stepped down to 0.00, and rode out the second crisis term (2022-09-30, £466.04/MWh) fully naked.

By 2024 every customer's hedge_fraction had settled at 0.00 and stayed there — every subsequent term shows `difference = £0.00 (tied)`, because a fully-naked position is *definitionally* identical to its own naked counterfactual.

## The Nine-Year P&L Outcome
**Hedge effectiveness — agent's actual margin vs. naked (100% spot) counterfactual:**

| Year | Actual | Naked | Difference | Verdict |
|---|---|---|---|---|
| 2016 | £272.68 | £500.11 | -£227.43 | naked would have won |
| 2017 | £541.75 | £879.77 | -£338.02 | naked would have won |
| 2018 | £372.65 | £524.32 | -£151.66 | naked would have won |
| 2019 | £571.24 | £730.15 | -£158.92 | naked would have won |
| 2020 | £510.71 | £585.07 | -£74.36 | naked would have won |
| 2021 (crisis) | £333.68 | £345.61 | -£11.92 | naked would have won |
| 2022 (crisis) | £2,364.33 | £2,411.31 | -£46.99 | naked would have won |
| 2023 | £3,461.76 | £3,487.85 | -£26.10 | naked would have won |
| 2024 | £1,177.67 | £1,177.67 | £0.00 | tied |
| 2025 | £360.33 | £360.33 | -£0.00 | tied |

- **Crisis years (2021-2022) combined:** actual = £2,698.01, naked = £2,756.92, difference = **-£58.91** — small, because by the time the crisis hit, three of the four agents had already de-hedged.
- **Stable years (everything else) combined:** actual = £7,268.78, naked = £8,245.28, difference = **-£976.49** — the overwhelming majority of the "cost of learning" was paid during the calm years, while the agent was still carrying the larger hedge positions it started with.
- **Full nine-year window:** the agent's actual margin = **£9,966.79** versus a naked-only baseline of **£11,002.20** — a **-£1,035.41 "cost of learning"** (revenue £23,023.39, cost £13,056.60, 142,004.24 kWh consumed across 635,225 settlement records).
- **Per-customer margins:** C1 = £3,170.51, C2 = £2,882.31, C3 = £1,148.07 (lowest — the customer whose evolution stalled longest at 0.10 and whose 2018 term also carried unusually high wholesale costs), C4 = £2,765.90.

**Naked beat actual in every single year from 2016 to 2023.** This is not a quirk of one customer or one period — it is the dominant pattern across the entire book, for the entire pre-2024 window.

## Key Decisions Made
- **Replaced the original "test three fixed strategies" design with an agent that discovers and evolves its own position**, per Rich's revised brief — no strategy was pre-selected or compared; the only thing handed to the agent was a single lever (`hedge_fraction`), a neutral starting prior, and a PiT-safe learning signal.
- **Chose the naked counterfactual as the evolution signal** specifically because it is derivable entirely from a term's own already-realised, completed history — same consumption, same real spot prices, same fixed-tariff revenue, the only variable being how the wholesale side was sourced. This isolates exactly what the hedge itself contributed, with zero foresight.
- **Made "no foresight" structural, not just documented**: `run_hedged_term()` settles one isolated term and physically cannot see beyond it; `run_customer_book()`'s sequencing guarantees `evolve_hedge_fraction()` is only ever called once a term's full outcome is known, and its result only ever affects the *next* term.
- **Held tenor fixed at the 12-month annual strip** rather than modelling the instrument menu's full day-ahead-to-Cal+1 spread — a deliberate scope simplification that keeps the single-lever model clean and answerable, with multi-tenor blending left as a natural future extension.

## Open Questions — The Gate-Relevant Finding
**Does the agent's evolution logic make domain sense? Yes — and that is exactly what makes the outcome instructive.**

The rule is simple, internally consistent, well-documented, and genuinely PiT-safe: compare what just happened to a clean counterfactual, nudge gently toward what worked, ignore noise. Nothing about it is unreasonable for an agent with no other information.

But it has a **structural blind spot**: a "did this just work" momentum signal cannot distinguish *"this hedge cost money because prices happened to be calm and falling"* from *"this hedge protects against tail risk I haven't experienced yet."* Because every agent's formative experience (2016-2020) was a calm, gently-falling-price period, every agent learned the same lesson — "hedging costs money, naked is better" — and had substantially or fully de-risked by the time the 2021-2022 crisis arrived, precisely when carrying a hedge would have helped most.

The numbers bear this out with unusual clarity: the crisis-year gap between actual and naked margin (-£58.91) is an order of magnitude *smaller* than the stable-year gap (-£976.49) — not because hedging stopped mattering in the crisis, but because three of the four agents had already abandoned it by the time the crisis tested it. C3, the one customer whose evolution stalled at 0.10 (purely by chance — its terms 4 and 5 happened to land inside the noise deadband) carried the most hedge exposure into the crisis and is also the lowest-margin customer in the book.

This is **recency bias / regime-change blindness**, discovered organically by a from-first-principles learning rule rather than asserted by the brief — a genuinely useful lesson about the limits of "watch your own results and adjust" as a strategy-formation mechanism, and a strong candidate for what a more sophisticated Phase 2+ agent design should address (e.g. weighting tail-risk outcomes more heavily than routine ones, or not fully trusting a position formed entirely within one market regime).

**Open question for Rich:** should Phase 1e's design build on this exact agent (carrying its now-converged 0.00 position forward), or should the gate finding above prompt a revision to the evolution rule itself before moving on?

## Token Efficiency
- **Local model calls:** 3 — `qwen2.5-coder:14b` via `tools/delegate_ollama.py`:
  - `sim/hedging.py` (pure per-period economics, exact-algorithm spec) — math correct first try; required hand-rewriting the docstring and removing three now-obsolete `STRATEGY_*` constants after the brief changed mid-flight
  - `sim/hedging_strategy.py` (full module from a structured spec with placeholder reasoning strings to fill in) — correct first try, no fixes needed; unit-tested clamping at 0.0/1.0 and tolerance-band hold, all verified
  - `simulation/run_phase1c_renewals.py` (copy-and-modify, carried over from the renewal increment that preceded this phase) — Qwen substituted wrong field names (`record['date']`/`record['revenue']` instead of the actual `settlement_date`/`revenue_gbp` schema) and invented broken aggregation logic despite an explicit "leave the rest exactly as is" instruction; fixed by hand-splicing the verified-correct top half onto the original bottom half
- **Hand-written:** `simulation/hedged_settlement.py` and `simulation/run_phase1d.py` — both mirror existing, already-proven structures (`run_settlement` and the renewal-run orchestration respectively) closely enough that delegation would have cost more in spec-writing than it saved; both passed their smoke tests cleanly on the first run
- **Notes:** **the spec/implementation race condition is now a confirmed, named risk** — `sim/hedging.py`'s spec was written and sent to the local model *before* Rich's message replacing the entire Phase 1d design arrived, so its math came back wrapped in obsolete "three fixed strategies" framing that had to be hand-stripped. No logic was lost (the underlying per-period calculation is identical regardless of which strategy framework wraps it), but it's a reminder to re-check in-flight delegation specs against the latest brief before integrating their output. Separately, **"copy this file, change only X" continues to reliably produce wrong results when the unstated "leave the rest untouched" requirement collides with the model's tendency to regenerate code it half-recognises** — this is now observed often enough (3rd occurrence) to treat as a structural delegation-pattern limitation rather than a one-off, and argues for either much smaller diffs or hand-writing orchestration scripts that touch existing schemas directly.
