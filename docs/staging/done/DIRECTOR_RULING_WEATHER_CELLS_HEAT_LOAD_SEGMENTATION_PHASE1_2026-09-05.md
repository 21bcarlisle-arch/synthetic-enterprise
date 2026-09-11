**Severity:** RECORDED · **Lane:** W1_market_weather (regional layer) + knowledge layer · **Priority:** P1, director-prioritised · **Proportionality:** reversible / narrow — just do it

# [DIRECTOR-RULING][ADVISOR-STAGED] Weather cells for household heat load — phase 1 (2026-09-05)

**Decided by the director in the advisor channel, 2026-09-05. Transmitted as decisions. The mechanism is yours.**

## 0. Zero-context orientation

The parked `docs/staging/in_progress/WEATHER_PHYSICS_HIERARCHY.md` (director-decided 2026-07-13) defines four layers: national weather → local/regional weather → premise shape → price. Its BUILD is epoch-gated; its DISCOVER/FRAME is not ("thinking is never gated"). **Layer 2 has never been defined: nobody has said what the regions are.** Today the SIM carries four weather nodes (London, Manchester, Glasgow, Cotswolds) chosen by convenience, not derived.

This ruling commissions the derivation. It is **knowledge work whose primary deliverable is a knowledge page**, built to the existing knowledge-layer canon (`docs/staging/done/ADVISOR_PILOT_KNOWLEDGE_PAGE_WHOLESALE_2026-07-28.md`: six-rung anatomy, Fact/Choice/Wiring claim classes, rate-of-change class, typed edges, stubs as a legitimate state, external register). The cells it produces are the cells the SIM will simulate weather on when the hierarchy's BUILD opens.

**Director's framing, verbatim:** *"What I'm trying to do is divide the UK up into clusters of similar primary weather drivers. Same temp vs mean, windchill, same solar. I imagine big populations in cities will be very similar. So the question is how much granularity is needed to capture, say 99%, versus 95 or 90% of the variation for households across these primary heat load variables… I want this as a piece of knowledge and primary driver of the maximum level of simplicity that can be achieved whilst still capturing fidelity for the vast majority of households."*

## 1. The problem

Find the smallest set of weather cells that captures the vast majority of **household-weighted** (not area-weighted) variation in the primary drivers of household heat load across GB, so that the SIM can simulate weather per cell rather than per house, and so that the fidelity cost of any chosen simplification is a stated number rather than a hope.

Property-side variables (house type, orientation, exposure, heating system, occupancy) are **out of scope** — they are a separate axis that will be crossed with these cells later. A hillside facing the prevailing wind is a property-level exposure attribute applied to its cell's wind, not a reason for a finer cell.

## 2. Decisions already made — transmit as decisions, do not relitigate

1. **Phase 1 variables:** mean temperature (heating degree days), mean wind speed, solar (global irradiance — serving both passive solar gain and PV yield). All **at house height**, not sea level: elevation-corrected per postcode.
2. **Phase 2 (decided, not authorised to start; opens when phase 1 lands):** cold-water / ground temperature (hot-water load), day length (lighting load and evening shape), summer temperature (cooling and appliance load; the futures engine needs it).
3. **Phase 3 (decided, not authorised; opens when the drawn population's heat-pump share makes it material, or the fabric layer takes on solid-wall moisture):** relative humidity (heat-pump defrost regime, jointly with temperature), wind direction (needed once property orientation is crossed with cells), driving rain.
4. **Two cell properties are in phase 1, not deferred:** cold-spell **persistence** (a five-day cold snap costs more than the same degree-days spread thin) and **cross-cell synchrony** (when Glasgow is cold, is London? — this is what turns household weather into portfolio risk). They are the "shape" half of the director's question and the hierarchy's own COHERENT/aggregation-consistency requirement.
5. **The answer is a curve, not a number.** Household-weighted variation explained versus number of cells, computed separately for **level** (annual heat load) and **shape** (cold-and-still versus mild-and-windy months), because two places with the same annual load can have different demand shapes.
6. **The clustering is blind to industry boundaries.** LDZ (13 gas zones), GSP groups (14 electricity regions) and SAP's 21 climate regions are **comparators**, overlaid afterwards, with a stated figure for how well each approximates the derived cells. LDZ and GSP matter because the company will receive settlement and network data on those boundaries.
7. **GB only.** Northern Ireland is a separate energy market.
8. **Authoritative weather source is Met Office HadUK-Grid at 1 km** (Open Government Licence; v1.3.2.ceda, June 2026, to end-2025). Monthly for the three phase-1 variables; daily temperature for persistence. Open-Meteo/ERA5, already in the repo, may be used for cross-checks but is not the anchor.
9. **Household weights come from the censuses** (England & Wales 2021, Scotland 2022) via postcode, not from the SIM's drawn population.
10. **Validation is independent of the weather data.** DESNZ sub-national gas consumption at small-area level is the check that the cells explain *real heat demand*, not merely weather. Generation and validation from separate sources — the World Validation Ladder rule.

## 3. Deliverables

1. **The knowledge page** — topic: what weather drives a household's energy use, and how it varies across Britain. All six rungs. The **expected-shape block** states the phase-1 findings falsifiably (e.g. "N cells capture ≥95% of household-weighted variation in annual heating degree days; the north–south gradient dominates solar; winter temperature and wind are positively correlated"). The cell definitions are a **Choice-class** claim, versioned, so phase 2's revision lands in place with both clocks. Rate-of-change class: settled/slow (climate normals). Typed edges to existing pages; **stubs minted now** for the phase-2 and phase-3 topics (hot water and inlet temperature; lighting and daylight; summer load; heat-pump performance in damp cold) so the page can point forward honestly.
2. **The evidence beneath it**, rendered from the pipeline, never static images: GB-level monthly means over recent decades; scatter plots of the correlations between the drivers; maps and tables by derived cell, LDZ and GSP; the two explained-variation curves; the cell sets at 90 / 95 / 99% named and compared to LDZ, GSP and SAP-21; persistence and synchrony reported per cell.
3. **The registers updated:** sourced figures as rows in `docs/market_research/ASSUMPTIONS.md` and `docs/institutional/knowledge_map.md`; the working research doc under `docs/market_research/`; the cell definitions as a machine-readable artefact the SIM will consume when the hierarchy's BUILD opens.
4. **Report back to the director, plain English:** the curve, the recommended cell count, what it would cost in fidelity to go coarser, and the one or two places where the data forced a choice.

Charts diagnose and communicate; numbers prove.

## 4. Non-negotiables

- **The data pull happens first, before any analysis, and within 72 hours of this ruling's timestamp.** CEDA access is via a personal token that expires ~3 days from 2026-09-05 mid-morning. Credentials are at `~/.config/synthetic-enterprise/.env.ceda` on Skynet (`CEDA_USERNAME`, `CEDA_PASSWORD`, `CEDA_TOKEN`). The token was proven this morning against `…/HadUK-Grid/v1.3.2.ceda/1km/tas/mon/` (41,400,415-byte file landed). CEDA's token-minting API (`https://services.ceda.ac.uk/api/token/create/`, basic auth) currently returns 500 for this account with correct credentials: try it — if it works, self-mint and never depend on the manual token again; if it does not, use `CEDA_TOKEN`, and if that has expired before the pull completes, **NTFY the director for a fresh one** (two minutes for him) rather than improvising. HadUK-Grid is a once-a-year release; note the annual refresh need on the page.
- **Raw grids stay on Skynet, never in the repo.** Several GB. Only derived artefacts (cell definitions, curves, chart data) are committed.
- **No fabricated coefficients.** Every threshold, weight and conversion traces to a published source; where none exists (e.g. a sunshine-hours-to-irradiance conversion, if HadUK's sunshine is used rather than a direct irradiance source), the choice is registered as a Choice with its source and its alternative named. HadUK publishes **sunshine duration, not irradiance** — choosing the irradiance source is yours, and it must be stated.
- **Elevation per postcode from Ordnance Survey open terrain data** (or an equivalently published source), so "house height" is real, not the 1 km cell's mean altitude.
- **External register on the page:** no atom names, rung numbers, lane labels or rule numbers. A company explaining the world.
- **This ruling registers phases 2 and 3; it does not authorise them.** Do not start them.

## 5. Priority and parallelism (director's instruction)

The director asked for this to be **prioritised and, where possible, worked in parallel**. His words: *"Can we stage this but prioritise it or get it working in parallel on it?"*

- It is **product** (a public knowledge page and a SIM-consumed artefact), and today's product-and-machinery canon governs: product work may win the draw against machinery.
- Its file scope is **disjoint from everything in flight** — new files under `docs/market_research/`, `docs/institutional/`, `site/knowledge/`, `site/data/`, plus a new local data cache. It is DISCOVER/FRAME-class, which the weather hierarchy ruling says is never gated. It therefore qualifies as a **parallel fork** under the bounded fan-out rule; run it that way if the bound allows, and say so if it does not.
- **Sequencing inside the fork:** pull → validate the pull → analysis → page. Do not let the page wait on a perfect pull; do not let the pull wait on anything.
- Draw it ahead of the next un-drawn product item. If something currently in flight is genuinely more urgent, say what and why in the NTFY — the director will re-rank, but the default is this first.

## 6. Risk

**What it touches:** new files only; no billing, no wall, no company-side code, no SIM runtime (the SIM does not consume the cells until the hierarchy's BUILD opens).
**Blast radius:** nil on published figures; the knowledge site gains a page and stubs.
**Probable failure modes:** (a) token expiry mid-pull — mitigated by pull-first ordering and the NTFY fallback above; (b) an irradiance source that is unpublished or unlicensed — mitigated by requiring the choice to be stated as a Choice with alternatives; (c) household weights taken from the SIM's own population instead of the census — forbidden above; (d) the page thinning to machinery — the knowledge canon's DoD 0 applies: **the page must genuinely explain**, and if the mechanics threaten the content, the content wins.
**Note on current machine state:** the publishing path is wedged today (origin fork not advancing; consistency gate red). This work does not depend on publishing to proceed; the page becomes visible when the wedge clears. Do not let this ruling be the reason the wedge is skipped — reconcile that as its own item.

## 7. WORK THIS CREATES

- One knowledge page (full depth) + four stubs, per §3.1.
- One research/analysis pass with the artefacts in §3.2–3.3.
- Registration of phases 2 and 3 as decided-not-authorised follow-ons on the map, with their opening conditions from §2.2–2.3.
- One plain-English report to the director, per §3.4.
