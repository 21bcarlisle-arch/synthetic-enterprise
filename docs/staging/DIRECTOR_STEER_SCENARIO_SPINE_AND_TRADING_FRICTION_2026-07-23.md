# [DIRECTOR-STEER] — Scenario spine, trading friction, and the pricing of forecast error (2026-07-23)

**Type:** [STEER] via advisor bridge, from a live director conversation 2026-07-23. Decisions below are DECIDED
(director's 20-year domain judgment); mechanism design is yours. Problem-and-construct framing — no filenames,
intervals, or architectures prescribed.

## Fresh-session anchor (assume zero context beyond disk)

Mission: carbon abatement via personalisation (£/tCO₂e). Epoch 2 = the commercial brain. Current state relevant
here: `docs/design/WHOLESALE_VALUE_CHAIN_FRAME.md` is done, its 2h veto lapsed, WVC_1→WVC_5 BUILD proceeds on
standing authority (benchmark = shaped annual cost, cover fan, value-add ledger). `docs/design/BOARD_SPEC_004_RECONCILIATION.md`
scored price formation 16 MET / 15 PARTIAL / 11 ABSENT, with findings F1 (spark-spread core passes
reconstructibility), F2 (regime layer on wrong axis), F3 (premium/sentiment absent SIM-side), F4 (gas ingested,
not formed — the load-bearing gap), F5 (in-window tails are real data, not formation). G4's fidelity ledger names
the spike tail (model max £574 vs real £4,038; negatives 0.013% vs 2.241%) as the top defect. The advisor's
2026-07-22 decade review found, from origin data: crisis half-life 2.7d vs calm 0.7d; the 2022 winter/summer
spread INVERTED (−£29.7, EU storage-fill panic); HDD-price corr +0.10 calm / −0.17 crisis / +0.43 post-2023.

## The governing rationale (record this; it is the frame for all wholesale work)

**The wholesale machinery exists to PRICE FORECAST ERROR.** Getting customer numbers, demand shape, or weather
response wrong becomes: a residual position settled at SSP (where the spike tail lives), or rebalancing paid
through the bid-offer spread (friction), or early cover paid for via risk premium (carry). Forecast-accuracy value
= avoided cost of the involuntary position. This gives belief-vs-truth gaps an economic denominator (gap ×
marginal cost of being wrong) — the ratified learning-value segmentation metric, now derived from market physics.

**Supplier roles are answers to physics.** Hedger ← price-volume covariance. Trader ← curve movement + friction.
Tariff designer ← customers consume a shape but pay a structure, under a cap. Risk/compliance ← absolute survival
constraint + collateral in cash. If a piece of physics is missing from the world, the corresponding organ never
develops or degenerates (costless rebalancing breeds a hyperactive fake trader — an R12 fidelity bug, not alpha).
The world forces the org design; we never script it. This is the epoch-4 tournament thesis grounded.

## Director decisions (DECIDED — transmit as decisions)

1. **Gas is split, not formed whole.** The gas TREND (level path) is an exogenous, director-authored scenario
   input (R13 curriculum). The SEASONAL/STORAGE STRUCTURE around that trend is FORMED — a European storage
   stock-and-flow state producing winter/summer spreads, contango/backwardation, and capable of the 2022-style
   inversion under a fill-mandate stress. This answers Spec 004 F4 without pretending to model global LNG.
2. **Oil is demoted** to a scenario-spine economy/energy-complex proxy. GB/EU gas is hub-priced (NBP/TTF, LNG
   arbitrage at the margin); oil indexation is not the driver. Do not build an oil→gas price mechanism.
3. **Hybrid formation confirmed:** fundamental stack (spark spread, residual-demand scarcity) + stochastic
   regime/jump layer on the residual — the FRAME §5 `SPEC004_residual_regime_process` direction stands. Neither
   pure fundamentals nor pure stochastic mean-reversion is acceptable alone (a single-regime process fit to
   2016–20 calls 2022 impossible — measured, not asserted).
4. **Scenario rotation is the resilience mechanism.** "We want resilience and the capability to endure, not pot
   luck in one world." Runs rotate through director-ratified worlds; the historical 2016–25 replay remains the
   default/baseline world (R13 baseline/curriculum split holds).
5. **Trading friction is first-class from day one.** Bid-offer spread is a surface — f(product, horizon, regime):
   front tight, far seasons wide (the spread widening toward unbounded IS the liquidity limit), peak wider than
   baseload, blow-outs under stress. Churn cost (trading churn) = volume × half-spread, per strategy. **The WVC
   value-add ledger must score achieved-vs-benchmark NET of friction from its first version** — a static,
   externally-anchored spread-by-horizon table is acceptable initially; the regime-widening surface is a
   follow-on. Scoring gross would overstate every early result and move the bar later.
6. **Named physics the chain must surface as first-class outputs:** price-volume covariance (cold snap = more
   volume exactly when spot spikes — the mechanism that actually killed 2021's suppliers); the shape/cash-out
   residual (hedged blocks vs consumed half-hourly shape, settled at SSP — where the spike tail becomes
   commercially real).

## Requirements

**A. Scenario spine (SIM-side, propose-then-proceed).** An exogenous world-state per run: gas trend path, oil/
economy factor, renewables buildout path, storage capacity path. Requirements, not design: consumed by price
formation and demand generation; hidden from the company (wall — the company discovers the world through prices
and its book, never reads scenario state); varies per run; version-pinned, director-authored curriculum artefact
(R13 — the MECHANISM is yours to build now; the scenario PARAMETER VALUES are proposed back for director
ratification before any non-baseline world enters rotation). Minimum launch set to propose: (i) NESO Future
Energy Pathways-anchored central path(s), (ii) a 2021–22 crisis-replay world, (iii) a supply-glut world.
**FRAME first; 2h director veto window on the FRAME; then BUILD on standing authority.**

**B. Friction amendment to the authorized WVC BUILD (just do it, with mitigations named).** Decision 5 amends the
WVC construct: benchmark/value-add scoring carries the friction term from first version. Anchor the initial
spread table to real sources (Ofgem GB wholesale liquidity reviews, exchange/broker GB power+NBP assessments) —
sourced, not guessed, registered in ASSUMPTIONS.md per convention.

**C. Registered follow-ons (sequenced candidates for the map — NOT built on this steer):**
   (3) Gas-balance crisis regime layer (level+vol+corr jointly, persistent) + the storage stock-and-flow of
       decision 1 — closes F2+F4; the formed seasonal spread and its inversion live here.
   (4) Curve evolution (the forward curve as a living object with stored history), risk-premium dynamics
       (widen-after-crisis/compress-in-calm, F3), liquidity horizon, and the full spread SURFACE with
       regime-widening — one object, the thing the cover fan accrues against.
   (5) Tail machinery: stochastic outage process, interconnector/French channel, renewables-surplus negative-price
       floor. Ranked last: in-window the real Elexon record supplies tails (F5); formed tails matter once
       scenario rotation leaves history.
   Also registered: the inactive carbon limb of the spark spread (engine's own named R10 — cheap, may be wired
   earlier if trivially safe); collateral/margin calls belong to the already-registered working-capital layer and
   to THIS story (2022 broke hedged suppliers on cash, not P&L). Network costs / ancillary / locational
   (postcode peak-avoidance value, UKPN-class constraints) stay PARKED, with one breadcrumb: locational value
   re-enters at the customer-personalisation layer via distribution red-band avoidance, where it meets the
   £/tCO₂e thesis.

## Decided vs open

DECIDED: everything under "Director decisions." OPEN (yours): whether the scenario spine is a new atom/lane or an
extension of the existing `sim/scenario/` generators; internal representation; where the friction table lives;
which WVC atom the friction amendment lands in. OPEN (director's, when proposed back): scenario parameter values
and which worlds enter rotation.

## Risk section (mandatory)

**Touches:** SIM-side scenario/generator machinery and the price-formation consumption path (A); WVC value-add
scoring (B). **Blast radius:** any run consuming scenario state; every trading-value figure once friction lands.
**Probable failure modes + inline mitigation:** (i) scenario spine drifting into implicit curriculum tuning
against company P&L — mitigated by R12/R13: values director-ratified, versioned, decided blind to P&L, baseline
world remains default until ratification; (ii) company-side leakage of scenario state — mitigated by a wall test
(R15-failable) proving the company cannot read it; (iii) friction term silently re-based later — mitigated by
scoring net-of-friction from first version and logging the friction line separately so gross is reconstructible;
(iv) integration blast radius on existing runs — mitigated by history-replay default: with no scenario selected,
every existing run is byte-identical (prove it, same discipline as the D3 actual-read test).

## DoD

1. Scenario-spine FRAME on origin, veto window stated, launch-world set proposed with sourced anchors.
2. Friction term live in the first value-add ledger version, spread table sourced and registered.
3. Follow-ons (3)–(5) + carbon/collateral breadcrumbs registered as map candidates with this doc cited.
4. Wall test + byte-identical-baseline test named in the FRAME as R15 obligations.
5. Governing-rationale section reflected wherever the wholesale lane states its purpose.
