# F5 — Simulated Competitor Field (DISCOVER)

**Track:** F5, Forward-Discovery Register (mission-required × high).
**Status:** DISCOVER-only. No build, no new map atoms. Names candidate atoms as *proposals* only.
**Date:** 2026-07-22. **Author:** autonomous worker (forward-discovery tick).

**Provenance & honesty (R9).** Written without live network access (autonomous run). Quantitative
market-structure figures below are **author domain knowledge, recalled — labelled `[recall, validate]`**
and must be validated against the named independent sources before any figure is used in a build or a
board figure. Structural claims (archetypes, behaviours, the regime shift) are well-established and
low-risk; the market-share *numbers* are the part that needs a fetch. Register unverified figures in
`ASSUMPTIONS.md` on graduation, exactly as `COMPETITOR_PLATFORMS_2026.md` did.

---

## 1. The gap, stated precisely

The register's framing — "pricing/retention decisions currently face **no opposition**" — is confirmed
by the code. The competitor field today is a **scalar, not a field**:

- SIM side: `simulation/market_switching_propensity.py` → `MARKET_SAVINGS_BY_YEAR` (an exogenous
  £/yr series 2016–2025) feeding a piecewise savings-elasticity curve.
- Company side: `company/crm/market_conditions.py` → `MARKET_SWITCHING_MULTIPLIER_BY_YEAR` (a
  year-indexed multiplier, independently reimplemented from the same public DESNZ/Ofgem series —
  correctly walled).
- Observable-tariff plumbing already exists and is **correctly walled**:
  `company/market/tariff_benchmarking.py` reads only public sources (Ofgem comparison tool, uSwitch,
  DUKES, press notices). Nothing to fix on the wall here.

**The defect is not a wall violation — it is a missing feedback edge.** The "savings available" a
customer compares against is a *fixed historical series*, not the output of competitors reacting to
our tariff. Consequences that make retention meaningless:

1. **No price response.** If the company cuts price, no competitor matches; if it raises price, the
   best-alternative rate the customer sees does not move — churn rises per a fixed elasticity but no
   *named opponent* harvests the churn or defends its own book.
2. **No strategic share war.** A challenger burning capital for acquisition share (2016–2020) and an
   incumbent defending a fat back-book (SVT-anchored) are indistinguishable — both collapse to the
   same scalar.
3. **No regime interaction.** The scalar *encodes* the 2022 "nowhere cheaper to go" regime as a
   number (0.44), but the company can't *discover* that regime by watching competitor tariffs move —
   it's handed the answer. The coupled-triad GAP (belief vs truth) is therefore untestable here.

This is the minimum a competitor model must add: **make the best-alternative rate endogenous to (a)
wholesale/cap physics and (b) at least one competitor archetype that responds to our pricing.**

---

## 2. The real UK household competitor field (anchor)

Two structurally distinct eras, both inside our 2016–2025 baseline window — the model must be
**regime-aware** or it will be wrong in one era:

**Era A — challenger boom (≈2016–2020).** 50–70+ active domestic suppliers `[recall, validate]`.
Price competition intense; "tease-and-squeeze" the dominant challenger tactic (cheap 12-month
acquisition fix → roll to expensive SVT). Savings available £150–£350/yr. This is the era the model
must let a *strategic entrant* exist in.

**Era B — post-crisis consolidation (≈2022–present).** **29 suppliers failed Jul 2021–May 2022**
`[VALIDATED 2026-07-22 against independent already-fetched repo sources — not SIM ground truth]`:
`company_commercial_strategy.md:103` (Ofgem SotM 2025 / NAO), `energy_market_complexity_june2026.md:99`,
and `svt_rates_active_passive_2016_2025.md:75` all independently record **29 failures / ~4M customers
into SoLR**; SoLR mutualisation **~£2.7bn / ~£94/household** (`company_commercial_strategy.md:103`,
`energy_market_complexity_june2026.md:16,98`); ~one-third of customers back on fixed deals by Jul 2025,
matching the pre-crisis ~35% engaged share (`svt_rates_active_passive_2016_2025.md:80`, Ofgem SotM
Jan 2026). (`ofgem_regulation.md:84` says "28 by December 2021" — a consistent by-that-date subset of
the full Jul-21→May-22 wave, not a conflict.) The field collapsed to a post-consolidation oligopoly.
Approximate per-supplier household-supply shares below remain `[recall, validate — STILL OPEN: no
per-firm % share table exists in the already-fetched repo corpus; needs a live fetch of Ofgem *State
of the Market* retail-market-share data]`:

| Archetype | Real exemplar(s) | ~share | Pricing behaviour |
|---|---|---|---|
| SVT-anchored incumbent | British Gas (Centrica) | ~20–24% | Prices at/near cap; heavy back-book; low acquisition appetite; high base inertia |
| Efficient tech challenger | Octopus Energy (absorbed Bulb) | ~20%+ | Thin margin, high NPS/service, tracker/Agile products; retention via service not just price |
| Consolidated incumbent | E.ON Next (+npower book), EDF, OVO (+SSE retail), ScottishPower | ~8–18% each | Cap-following fixed deals; moderate acquisition |
| Prepayment / PAYG specialist | Utilita | ~3–4% | Distinct segment, distinct cost-to-serve; largely off the switching-savings axis |
| Green-premium (values-led) | Good Energy, Ecotricity | small | Prices *above* market; retention via values, low price-elasticity |

Regulatory events that reshape competitor *behaviour* (already in `churn_price_elasticity.md`, restated
as behaviour-drivers): **Default Tariff Cap** (Jan 2019, compresses the acquisition/back-book gap);
**Acquisition Tariff Ban** (Apr 2022); **"Fairer for existing customers"** rule (~2023, *permanently*
removes new-customer exclusives → kills tease-and-squeeze, shifts competition from price to service).

---

## 3. The two poles the register names — and the minimum between them

The register asks for "tariff-following vs strategic entrants." These are the two poles; the minimum
useful model is a **two-tier field**, not 60 named firms:

**Tier 1 — deterministic tariff-follower band (the majority).** Best-alternative rate =
`f(price_cap, wholesale_forward, fixed_spread, era_regime)`. Does *not* react to our moves. Cheap.
Its value over the current scalar: the best-alternative rate becomes **endogenous to wholesale/cap
physics** rather than a hardcoded series, so the 2022 "nowhere cheaper to go" regime *emerges* from
the cap sitting below the wholesale-driven fixed price, instead of being asserted as `0.44`.

**Tier 2 — 1–3 strategic archetypes that respond.** A small set of agents with:
- an **acquisition appetite** (capital-backed for the challenger; back-book-defending for the incumbent),
- a **response function** on the gap between our tariff and theirs (undercut, match, or harvest),
- a **regime gate** (a capital-burning challenger only exists in Era A; the ban/fairer-pricing rule
  switches its tactic off in Era B).

This is what makes retention *meaningful*: underprice → an entrant matches and the share war costs us
margin, not just customers; overprice → an entrant harvests our churn and we can *observe* the loss.

**Simplicity guard (C-S / SIMPLICITY GUARD).** The minimum is a response *function* plus a regime
gate — not a multi-agent auction, not per-firm cost stacks for all 60. Resist building the boom-era
firm-by-firm; model the *band* + a handful of *archetypes*.

---

## 4. The epistemic wall (binding)

The competitor field is **SIM-side ground truth.** The company observes it only through the same
interfaces a real supplier has:

| The company MAY observe (public / own data) | The company may NEVER read (SIM internal) |
|---|---|
| Competitor **published tariffs** (PCW/Ofgem tool/press) — already `tariff_benchmarking.py` | Competitor **cost stacks, hedge books, capital positions** |
| Its **own** customer gains/losses (win/loss flows) | Competitor **churn curves / acquisition strategy / response function** |
| Published market-share stats (Ofgem SotM, lagged) | Which competitor a leaving customer went to *and why* (only aggregate, lagged) |

So the company must **infer** competitor strategy from observed tariffs + its own flows — and is
**allowed to be wrong** (the coupled-triad GAP). `company/market/market_share_estimator.py` already
does this inference shape; the field would give it something real to be wrong about. A modelled
competitor "acquisition appetite" is SIM truth; the company's *estimate* of it is a separate, walled
belief.

**No new wall crossing needed:** the observable feed already exists and is walled. The field lives
entirely behind the existing `tariff_benchmarking` observable — the company sees prices move, not the
strategy that moved them.

---

## 5. Independence & validation

- **Validation status (2026-07-22 tick, no live network — cross-checked against already-fetched,
  independent, published-source repo docs; the SIM scalar was NOT used as a check):**
  - **CLOSED — market structure:** the SoLR-failure count (**29 / ~4M / ~£2.7bn / ~£94/hh**), the
    post-2023 re-fixing (~one-third), and the two-era shape are now corroborated by ≥3 independent
    Ofgem/NAO-anchored docs (cited inline in §2). These no longer need a fetch.
  - **STILL OPEN — per-supplier % shares:** the §2 table's per-firm percentages (British Gas ~20–24%,
    Octopus ~20%+, etc.) have **no independent corroborating source in the repo corpus** and remain
    `[recall, validate]` pending a live fetch of Ofgem *State of the Market* retail-market-share data.
    This is the *only* remaining fetch-gated item in F5; the rest of the artefact stands on validated
    or structural (low-risk) claims.
- The market-share table (§2) must be validated against **Ofgem *State of the Market* / retail market
  share data** and the SoLR-failure count against **Ofgem's SoLR record** — never against SIM ground
  truth (the scalar series is *not* an independent check; it is the thing being replaced).
- The savings-elasticity anchoring (`churn_price_elasticity.md`, DESNZ/Ofgem) is the **demand-side**
  half and stays authoritative — F5 supplies the **supply-side** rate the elasticity acts on. The two
  must reconcile: the field's best-alternative rate, run through the existing elasticity curve, must
  reproduce the observed 2016–2025 switching series **for fidelity reasons only** (R13 baseline wall —
  calibrate the field to reality, never to company P&L).

---

## 6. Candidate graduation shape (PROPOSAL ONLY — not map-registered)

If the director graduates F5, the natural minimal build (one coupled triad, per COUPLED_TRIAD doctrine):

- **SIM:** a two-tier competitor field (deterministic tariff-follower band + 1–3 regime-gated
  strategic archetypes) emitting a per-year best-alternative tariff behind the existing observable.
- **COMPANY:** consumes the observable tariff feed (unchanged wall), estimates competitor appetite
  from own win/loss, prices/retains against it — allowed to misread.
- **HARNESS:** measures the belief-vs-truth GAP (company's estimated competitor response vs the SIM's
  true response function) and asserts the field, run through the existing elasticity, reproduces the
  real 2016–2025 switching series.

No atom is opened here. This is the DISCOVER artefact only; BUILD-open is a director/twin call.

---

## 7. One-line finding

**The competitor field is a scalar, not a field:** best-alternative rate is a fixed historical series,
so pricing/retention face a non-reactive opponent. The observable-tariff wall is already correct; the
missing piece is a *response edge* — the minimum being a cap/wholesale-endogenous follower band plus
1–3 regime-gated strategic archetypes. Market *structure* figures (29 supplier failures / ~4M customers
/ ~£2.7bn SoLR mutualisation / post-2023 re-fixing) are now **validated** against independent
already-fetched repo sources (§5); only the per-supplier **% shares** remain `[recall, validate]`
pending a live fetch of Ofgem *State of the Market*.
