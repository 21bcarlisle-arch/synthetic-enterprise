# Decomposition proposal — hub / children / stubs for wholesale price formation

**Deliverable #3** of `DIRECTOR_RULING_KPILOT_SCOPE_FIRST_2026-07-28.md` (ruling §4). Proposes the
information architecture for the price-formation topic: which topic is the **hub**, which are
**children** (full pages), which are **stubs**, and where the current page's content belongs. FRAME /
doc-only — no page rewrite here (the rewrite is #4/#5's assembly against the brief).

Argued against the scope brief (deliverable #1) and the page reconciliation (deliverable #2): every
required section S1–S15 maps to a slot below; nothing is orphaned.

## The problem being fixed (ruling §4)

The current IA is a single page that "tried to be a hub and a full treatment simultaneously and
achieved neither." Confirmed on disk: `site/knowledge/` contains **only** `wholesale-price-formation`;
its 7 topic-graph "stubs" (gas-price, carbon-price, merit-order-residual-demand,
imbalance-cashout-settlement, hedging-forward-market, price-cap, gb-electricity-market) are **graph
nodes with no pages behind them**. So today the topic is *one over-loaded page + seven empty
pointers* — too big (one page can't treat 14 phenomena) and too small (each phenomenon gets a
sentence) at once.

## Design principle — do not repeat the "too big" failure

The director's warning cuts both ways: a decomposition that mints 12 full child pages at once would
fail the *same* way (breadth with no depth, twelve thin pages). So the proposed cut is **deliberately
narrow on full children and honest on stubs**:

- The **hub** stops trying to be a full treatment. It carries the spine claim (marginal pricing), a
  one-paragraph orientation to each child, the shared rung-5 charts, the belief-revision, and — the
  pilot's real output — the **named-gap delta** (#5).
- Only the **highest-value, director-named, currently-absent** phenomena become **full children now**.
- Everything else is a **named stub**: a real node that says what it will cover and states, on the
  page, that it is not yet written. **A named stub IS a published gap** — it feeds the delta (#5) and
  the backlog (`DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG`). A silent omission is the defect; a
  named stub is not.

This is the argued cut the ruling invites ("If you judge a different cut better than hub-and-children,
argue it"): hub + a *small* set of full children + honestly-named stubs, phased — not hub + 12
children.

## Proposed architecture

### HUB — `/knowledge/wholesale-price-formation/` (the existing URL)
- **Carries:** S1 (the marginal-price principle) as the spine; a short orientation paragraph linking
  each child/stub; the **rung-5 charts** (S15 — price series, merit-order stack, seasonal shape,
  negative-price frequency) as the shared evidence surface; the belief-revision block; and the
  **brief-vs-assembly delta** (#5) — the named gaps, published as the finding.
- **Current-page content lands here:** `headline`, `plain`, `theory`/SRMC + worked example, the
  `expected_shape` bands, `live_evidence`, `residuals`, `revision` — the strong marginal-principle
  spine stays on the hub; the four already-named machinery gaps stay in "Where our picture is still
  weak."
- **Stops doing:** exhaustively treating gas formation, regimes, seasonality etc. in-line — those move
  to children/stubs.

### TIER-1 CHILDREN — full pages now (5)
Chosen because each is (a) director-named or a Spec 004 architecture-disqualifier, (b) currently
absent-unnamed, and (c) load-bearing for the spine:

| Child page | Scope-brief section | Why a full page now | Existing node |
|---|---|---|---|
| **The structure of wholesale prices** (baseload/peak, seasons/quarters/months, day-ahead/within-day) | **S2** | Director's #1 ("possibly the most important thing we use"); wholly absent today (#2 row). | NEW |
| **The gas price** (NBP/TTF, LNG marginal cargo, storage, the global anchor) | **S4** | Page says "gas sets power" but never *how gas is priced*; the global channel is the 2021–22 mechanism. | promote `gas-price` stub |
| **Merit order & residual demand** (the SRMC stack, both ends) | **S3** | The mechanism the whole page rests on; deserves the full stack treatment the hub can't hold. | promote `merit-order-residual-demand` stub |
| **Negative prices & scarcity** (the two ends of the stack, the hockey stick) | **S9 + S10** | The "interesting behaviour lives at the ends" (Spec 004 §1); negative-price frequency currently unquantified, scarcity mechanism absent. | NEW |
| **Regimes & the 2021–22 exhibit** (reversion to a level that jumps) | **S12** | Spec 004's sharpest architecture disqualifier (#5/#12); entirely absent today. | NEW |

### TIER-2 STUBS — named, not yet full (each a published gap)
Real nodes with a one-line "what this will cover" + an on-page "not yet written" marker. These ARE the
delta's named gaps:

| Stub | Scope-brief section | Existing node |
|---|---|---|
| The carbon price (CPS + traded ETS; stack reordering) | S5 | promote note on `carbon-price` (partly on hub) |
| Weather & the joint driver (demand ↑, wind ↓, gas-burn ↑, prices ↑ together) | S6 | NEW |
| Interconnectors & imports (the French channel) | S7 | NEW |
| CfDs & renewable support (merit order AND consumer cost) | S8 | NEW |
| Seasonality & storage (winter–summer spread, injection/withdrawal) | S11 | NEW |
| Forwards, risk premia & hedging (forward ≠ forecast) | S13 | keep `hedging-forward-market` stub |
| The structural transition (bimodal distribution) | S14 | NEW |
| Imbalance & cash-out (up to the £6,000/MWh ceiling) | (S10 detail) | keep `imbalance-cashout-settlement` stub |
| The retail price cap (how wholesale reaches the bill) | downstream | keep `price-cap` stub |
| The GB electricity market (the settled market these prices live in) | parent context | keep `gb-electricity-market` stub |

## Completeness check — every scope-brief section has a slot

S1 → hub · **S2 → Tier-1 child (structure)** · S3 → Tier-1 child (merit order) · S4 → Tier-1 child
(gas) · S5 → Tier-2 stub (carbon) · S6 → Tier-2 stub (weather/joint driver) · S7 → Tier-2 stub
(interconnectors) · S8 → Tier-2 stub (CfDs) · **S9 → Tier-1 child (negative & scarcity)** · **S10 →
Tier-1 child (negative & scarcity)** · S11 → Tier-2 stub (seasonality/storage) · **S12 → Tier-1 child
(regimes/2021–22)** · S13 → Tier-2 stub (forwards) · S14 → Tier-2 stub (transition) · S15 → hub
(shared charts). **No section orphaned.**

## Reconciliation with the live IA (exit criterion)

- Slots into the existing single-page graph rather than a greenfield one: 3 of the 5 Tier-1 children
  **promote existing stub nodes** (gas-price, merit-order-residual-demand — plus the hedging stub
  stays as a Tier-2 stub); 4 existing stubs (carbon, imbalance-cashout, price-cap, gb-electricity-
  market) are retained as stubs; 2 Tier-1 children are new (structure, regimes) and 1 combines the
  ends of the stack (negative & scarcity).
- The generated sidebar/backlinks/`topics`+`edges` in `site/data/knowledge_wholesale.json` already
  model these nodes; the decomposition changes each node's **`kind`** (page vs stub) and adds the two
  NEW nodes — it does not rebuild the graph mechanic (ruling §6: keep the machinery).
- **Not built here:** the actual page files and the `topics`/`edges` edits — that is assembly (#4/#5)
  against this decomposition, gated by the SITE/BUILD front.

## Open decision left to the director (latitude, ruling §4)

The Tier-1 vs Tier-2 line (5 full children now, rest as named stubs) is the agent's judgment under the
ruling's explicit latitude. If the director judges a different cut better — e.g. structure-only as the
single first child, or gas+structure — the phasing narrows further; the *set* of slots (S1–S15
mapped) does not change, only how many are full pages in the first assembly pass. Recorded as a
proposal, reversible.

---

*Provenance: deliverable #3, FRAME / doc-only IA proposal, no maturity-map level claimed. Deps #1
(scope brief) met — unblocked. Argued against #1 + #2. Blocks #4 (charts land on decided pages) and #5
(delta on the hub). 2026-07-28.*
