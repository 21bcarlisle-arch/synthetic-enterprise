# B4_competitor_field — FRAME (COMPANY side)

- **id:** B4_competitor_field · **lane:** B_commercial · **dial:** 3
- **level:** current 0 → target 1 · **depends_on:** W2_3_competitor_field
- **status:** DISCOVER/FRAME only (BUILD-gated, `loop_stage: idle`) — doc, no code, level unchanged.

## 1. What this atom is & real-world grounding
B4 gives the **company** a working sense that it does not price in a vacuum: rivals exist, they publish tariffs, and those tariffs exert two forces — a **price ceiling** and an **undercut pressure**.

In the GB retail energy market a supplier's headline price is bounded above and below:
- **Ceiling (regulatory + competitive):** the Ofgem **default-tariff price cap** is a hard de-facto ceiling for standard variable tariffs, reset quarterly; above it you literally cannot bill an SVT customer. Below the cap, the *cheapest few* fixed deals on the comparison tables set a softer competitive ceiling — price materially above the visible market and acquisition dries up and churn rises.
- **Undercut pressure (acquisition + retention):** switching sites (Uswitch, MoneySuperMarket, Compare the Market, the Ofgem-accredited comparison layer) rank tariffs by annual cost. A customer's switch probability is dominated by the **gap to the cheapest visible tariff**, gated by their switching propensity (engaged vs sticky/SVT-parked). A rival dropping their acquisition tariff pulls churn up on your book and shrinks your win-rate on new business — the classic loss-leader/acquisition-cost dynamic of the 2017–2021 challenger era (and the reverse in the 2021–22 crisis when fixed deals vanished entirely).

The company must **feel** this: pricing decisions and churn/acquisition outcomes should respond to where its price sits relative to the observed competitor field, not to an internal constant.

**Epistemic wall at the market boundary:** a real supplier only ever **observes** competitors — their *published* tariffs, comparison-site rankings, and its own realised switching flows. It **cannot** see rivals' cost stacks, hedge books, margin targets, or churn models. The company's picture of "the competitor field" is therefore an *inference from observables*, and it is allowed to be wrong.

## 2. W2_3 (WORLD) vs B4 (COMPANY) split — COUPLED_TRIAD
Per COUPLED_TRIAD every capability is a 3-loop: SIM adds depth → COMPANY discovers & copes through the wall → HARNESS measures the belief-vs-truth GAP.

- **WORLD / SIM — `W2_3_competitor_field` (ground truth):** generates the actual competitor field — a set of rival suppliers with tariffs, positioning, and *moves* (cut/hold/withdraw), including their true intent and cost basis. This is ground truth; it is the thing the company cannot see directly.
- **COMPANY — `B4` (this atom):** consumes only **observables** across the wall — published competitor tariffs and switching/ranking signals — builds its own (approximate, possibly stale or biased) **model of the competitor field**, and uses it to (a) sense the ceiling and (b) feel undercut pressure in its pricing and in realised churn/acquisition. B4 may misread the field (e.g. mistake a temporary loss-leader for a permanent price level, or miss an unpublished bilateral deal) — that error is the point.
- **HARNESS — the gap:** measures **company-belief vs SIM-truth**: how far the company's inferred competitor field (implied ceiling, perceived undercut) diverges from `W2_3`'s ground-truth field, and whether the divergence produces mispricing/churn surprises. The gap is the score, reported per coupled pair.

## 3. Level decomposition (keep L1 modest and honest)
- **L0 (current):** company prices with no notion of rivals; churn/acquisition are competitor-blind.
- **L1 (target) — minimal, honest company-facing capability:**
  1. **Observe a ceiling:** the company reads an observed competitor price ceiling (a published-tariff / cap-derived reference) across the typed wall and holds it as a belief.
  2. **Feel undercut pressure:** at least one company decision path is sensitive to the gap between own price and the observed field — pricing sanity (don't price above the observed ceiling without a logged reason) **and/or** a churn/acquisition signal that moves with the own-price-vs-field gap.
  - L1 is **belief + one live coupling**, not a full competitive-response strategy engine. No optimiser, no game-theoretic reaction function, no multi-rival war-gaming — those are later levels.
- **Later (out of scope for L1):** modelling individual rivals and their move dynamics, detecting acquisition loss-leaders, elasticity-calibrated response, staleness/latency of the observed field.

## 4. Dependencies — why B4 is gated on W2_3
B4 `depends_on` W2_3_competitor_field because **the world must generate the field before the company can observe it** — there is nothing to infer from an empty market. Per COUPLED_TRIAD's two binding rules: *no world/SIM atom reaches L3 until the company has been tested against it and the gap measured*, and *no company capability is complete until it has faced a world that can defeat it*. So:
- W2_3 must exist (rivals + tariffs + at least the observable projection of the field) before B4 can reach L1 — B4 cannot observe what the SIM does not emit.
- Symmetrically, W2_3 cannot claim L3 on the strength of internal richness alone; it must have defeated a company that only sees the observable projection, with the gap measured. B4 is that company. The two advance in lockstep, gap-first.

## 5. Open questions / director gates — CURRICULUM (R13)
**Competitor aggressiveness is CURRICULUM, director-owned (R13).** How hard the field pushes — number of rivals, how aggressively they cut, whether they run acquisition loss-leaders, whether a price war erupts (e.g. a "Scenario: 2018 price war" vs a "Scenario: 2022 crisis, no fixed deals") — is a **director-authored, named, versioned scenario dial**. It is **never** tuned by the agent in response to company P&L or churn outcomes; the agent controls both sides of the wall, so the difficulty must face the director. The BASELINE projection of competitor prices (calibration to real published-tariff / cap history) may only change for **fidelity-to-reality** reasons, decided blind to company results.
Open questions for the director gate:
- What is the canonical competitor-field scenario set and its default (calm / challenger-era price war / crisis)?
- Does the observable projection include comparison-site *ranking* or only raw tariffs? (ranking is a richer, still-realistic observable.)
- Is the Ofgem cap modelled as a separate regulatory ceiling atom or folded into the competitor field's ceiling here? (recommend: cap stays its own regulatory input; B4's ceiling is competitive.)

## 6. Portability & scale-readiness (one line each)
- **Portability:** the competitor field is keyed by **market/regime** (a set of rivals + a pricing/observable convention per geography-segment-product), never hardcoded to GB retail electricity — a second market drops in behind the same seam with its own rivals, ceiling convention, and switching mechanics.
- **Scale-readiness:** competitor observations are **events arriving over time** (C-S1/C-S3) — the company must cope with tariff updates arriving one at a time, late, or out of order, and processing the same observation twice is idempotent (C-S2); no batch-completeness assumption about "the whole field this tick."

## 7. Typed-flow seam
Competitor observations cross the SIM/company wall through a **typed, versioned message adapter** (`company/interfaces/sim_interface.py` style), exposing **observables only** — published tariff level(s), an observed ceiling reference, and switching/ranking signals — and **never** rival internals (cost stack, hedge book, margin target, intent, or move rationale). The adapter is the go-live seam: swap the SIM competitor generator for a real comparison-site/tariff feed behind an unchanged interface. Request/response (e.g. "current field snapshot") are separate events in time, not same-step resolution (C-S3).
