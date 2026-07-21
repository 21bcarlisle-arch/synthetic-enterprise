# REMA Zonal / Locational Pricing — DISCOVER findings

**Atom**: W1_8_zonal_locational_pricing
**Mode**: DISCOVER only (director console, 2026-07-21) — research the REMA zonal design and
what it would change. No build, no map edit, no simulation/company code touched or read.
**Researcher**: discovery-agent
**Date**: 2026-07-21

---

## 1. What zonal pricing IS, vs today's single national price

**domain**: electricity_pricing
**assumption_tested**: GB currently has one national wholesale electricity price; REMA zonal
would replace it with several bidding zones each with its own locational marginal price (LMP).
**benchmark_value**: Confirmed — GB wholesale market is currently a single national price. The
2024 REMA options assessment models an illustrative reference case of **12 GB zones**, based on
NGESO's NOA7 refresh boundary work (via the LCP Delta/Grant Thornton "System Benefits from
Efficient Locational Signals" study, 2024), but the document explicitly states this **12-zone
figure is a modelling assumption, not a DESNZ decision on zone count or boundaries** — "does
not represent a DESNZ view on the number or location of zones... Zone boundaries will
ultimately be based around the most significant network constraints" (options assessment, §3.233).
**confidence**: H (primary DESNZ document, quantitative modelling basis stated directly)
**source**: DESNZ, "Review of Electricity Market Arrangements: Options Assessment" (PDF, published
2024-03-12, retrieved 2026-07-21) —
https://assets.publishing.service.gov.uk/media/65eb48f362ff48ff7487b30a/rema-options-assessment.pdf
(§3.198–3.235, §7 counterfactual appendix, "12 GB zones... as outlined by NGESO in their NOA7
refresh report")
**finding**: Mechanism, per the options assessment (§3.199–3.200): under national pricing, the
wholesale price is set by the single national marginal (price-setting) plant, and all other
generators earn "inframarginal rent" (the gap between their own cost and the national clearing
price). Under zonal/locational pricing, each generator instead receives only the **marginal
price within its own zone/node**; the price differential between interconnected zones is
captured by transmission owners as **congestion rent**, which can (in principle) be passed back
to consumers. So zonal pricing is fundamentally a change in **who captures the spread between
generation cost and clearing price**, not just "more prices." No build action — this confirms
the assumption is directionally correct but the specific zone count (12) must be labelled
provisional/illustrative if ever encoded, never treated as the decided figure.

---

## 2. REMA decision status and timeline

**domain**: policy_costs / electricity_pricing
**assumption_tested**: Whether/when government would decide between zonal and (reformed)
national pricing for GB, and what the current live status is (director specifically flagged
this needs checking, as of session date 2026-07-21).
**benchmark_value**: **DECIDED — 10 July 2025.** Government confirmed it will **retain a single
national, GB-wide wholesale electricity market and does NOT intend to introduce zonal pricing.**
Instead it will implement "Reformed National Pricing" (RNP) — a package of reforms (TNUoS/
connection-charge reform, the Strategic Spatial Energy Plan (SSEP), Centralised Strategic
Network Plan (CSNP), balancing/settlement reform) delivered *within* the single-price model.
As of the most recent live document (RNP Delivery Plan, published **21 April 2026** — i.e.
current as of this session's date), RNP is the active programme; there is no live zonal
consultation or reopened zonal decision.
**confidence**: H (two primary DESNZ documents, cross-dated, no conflicting later document found)
**source**:
- DESNZ, "Review of Electricity Market Arrangements (REMA): Summer update, 2025" (accessible
  webpage; datePublished 2025-07-10, retrieved 2026-07-21) —
  https://www.gov.uk/government/publications/review-of-electricity-market-arrangements-rema-summer-update-2025/review-of-electricity-market-arrangements-rema-summer-update-2025-accessible-webpage
  — ministerial foreword (Ed Miliband): *"We have decided to retain a single national GB-wide
  wholesale market... We have therefore decided not to implement zonal pricing."*
- DESNZ, "Reformed National Pricing (RNP): delivery plan" (accessible webpage; datePublished
  2026-04-21, retrieved 2026-07-21) —
  https://www.gov.uk/government/publications/reformed-national-pricing-rnp-delivery-plan/reformed-national-pricing-rnp-delivery-plan-accessible-webpage
**finding**: This is the single highest-signal finding for the atom: **the real-world REMA
decision has already been made and it went AGAINST zonal pricing.** GB will run the same
single-national-price wholesale structure the simulation already implements, for the
foreseeable delivery window (RNP legislation targeted "as soon as possible within this
Parliament, by 2029 at the very latest" for TNUoS reform; SSEP first published autumn 2027).
**Action implication**: the existing single-national-price baseline in `sim/`/`company/` is
NOT wrong or stale — it matches the real, decided regime. Zonal pricing is correctly scoped by
the director as a **curriculum/scenario** research item (a world the company could face in a
counterfactual future or an alternate-history run), not a baseline correction. See §4.

**Reasons DESNZ gave for rejecting zonal** (options assessment discounted-options section,
Summer Update 2025, "Discounted options: Zonal Pricing"), each is itself a modelling-relevant
insight if a zonal scenario is ever built:
1. Weak long-term locational investment signal — CfD-protected generators are shielded from
   locational price risk, so the actual signal comes from volume risk exposure, which "fluctuates
   on a half hourly basis" and is hard to underwrite at investment time.
2. Distributional/fairness risk across zones/regions — no simple way to guarantee all consumers
   better off; mitigations add complexity and their own distributional risk.
3. Investor uncertainty — even with mitigations, residual risk raises the cost of capital/delivery.
4. **Delivery timeline**: DESNZ assessed zonal implementation would take **~7 years assuming no
   delays** — vs. RNP being faster and less disruptive.
**confidence**: H (same primary source as above)
**source**: same as above (Summer Update 2025 §"Discounted options")

---

## 3. What zonal pricing would CHANGE for a supplier's world model

**domain**: forward_curve / electricity_pricing / credit_risk / other
**assumption_tested**: What specific deltas a zonal regime would introduce into the company's
observable price/hedging/risk world, relative to the current single-national-price model.
**benchmark_value**: Qualitative — the options assessment and REMA modelling work identify these
structural deltas (not simulation-derived; these are the real-world mechanism descriptions):
1. **Locational price divergence**: instead of one GB wholesale clearing price per settlement
   period, each zone clears at its own marginal price, driven by local generation/demand balance
   and inter-zonal transmission constraints ("boundaries... most likely to be constrained" —
   options assessment §7 counterfactual). A supplier's cost-to-serve would depend on which
   zone(s) its customer load sits in.
2. **Zone-dependent hedging/imbalance exposure**: a generator/supplier's inframarginal rent
   (today captured nationally) becomes zone-specific; congestion rent is captured by transmission
   owners at zone boundaries (§3.199). A forward-hedging book would need to be zone-aware — a
   national hedge no longer perfectly offsets a zonal exposure if the customer's zone and the
   hedge's reference zone diverge (basis risk is explicitly the mechanism DESNZ cited as the
   reason CfD-protected generators found zonal signals hard to underwrite).
3. **Regional demand/generation mismatch as a price driver**: the whole rationale for zonal is
   that "generation and demand will never perfectly match" and network build has lagged
   generation siting (RNP Delivery Plan, "historical context on constraints" section) — so a
   zonal price signal is explicitly a function of local network congestion, not just system-wide
   merit order.
4. **Merit-order → price chain**: under national pricing the clearing price is set by the single
   national marginal plant; under zonal, each zone has its own marginal (price-setting) plant,
   so the merit-order-to-price mapping becomes zone-indexed rather than GB-wide. This is the
   concrete coupling point to **W1_6** (the physics-based price signal, presumably GB-wide today)
   — a zonal regime would require that price signal to be computed per zone, which in turn
   requires a **regional generation/demand/network topology** input, coupling to **W1_4**
   (regional weather field — wind/solar output is highly regional, so weather-driven generation
   variance is a first-order driver of which zones diverge from each other).
**confidence**: M (mechanism is H-sourced from DESNZ primary docs; the specific W1_6/W1_4 coupling
claim is this researcher's inference about the atom's dependencies, not itself published anywhere
— it follows necessarily from "zonal price = f(regional generation, regional demand, network
constraints)" but is UNVERIFIED against the actual current W1_6/W1_4 implementation, which this
researcher did not and must not read.)
**source**: DESNZ options assessment (as above) §3.199–3.235; RNP Delivery Plan §"historical
context on constraints"
**finding**: The real-world REMA analysis independently arrives at the same coupling the
director already named (W1_6 price physics + W1_4 regional weather) — locational price
divergence is mechanically driven by regional generation (weather-sensitive) meeting regional
demand against a constrained network topology. This is good independent confirmation that if
this atom is ever opened for BUILD, it is correctly framed as a *dependent* extension of the
weather/price physics layer, not a standalone pricing table.

---

## 4. The R13 curriculum angle — zonal pricing as a scenario, not a baseline change

**domain**: other
**assumption_tested**: Per CLAUDE.md R13 (baseline/curriculum split), the director flagged zonal
pricing should be evaluated as a *curriculum/scenario* choice, not a silent baseline change.
**benchmark_value**: N/A (a design framing question, not an empirical benchmark) — but the
real-world facts support the framing directly: zonal pricing is **not** the enacted regime (see
§2), so encoding it as the default baseline would violate R13's "changed for fidelity-to-reality
reasons... decided blind to company P&L" rule — the real world did NOT go zonal, so the baseline
correctly stays national.
**confidence**: H (follows directly from the §2 finding)
**source**: same as §2, plus CLAUDE.md R13 text (internal, for framing only — not a market source)
**finding**: A "zonal regime" scenario, if the director authors one per R13 ("named, versioned,
director-authored artefact... never silent parameter drift"), would need at minimum:
- A **zone topology definition** (count + boundaries) — real-world precedent for an illustrative
  reference is the 12-zone NGESO NOA7-refresh-based split used in DESNZ's own modelling
  (options assessment §7), explicitly caveated as non-decisional; a scenario author should treat
  any zone count as a curriculum PARAMETER, not a discovered fact, since DESNZ itself never fixed one.
- A **customer-to-zone mapping** (which zone each simulated customer/meter sits in) — currently
  absent from a single-national-price world by construction.
- A **congestion-rent / inframarginal-rent redistribution rule** across zones, since this is the
  mechanism DESNZ modelling used to move consumer benefit (§3.199) — a scenario that only
  changes the clearing price without modelling this transfer would misrepresent the real proposal.
- A **counterfactual/what-if framing note** stating this is explicitly NOT the enacted 2025 REMA
  outcome — since the real world chose Reformed National Pricing, a zonal scenario is properly a
  "what if REMA had gone the other way" or "future re-opened decision" curriculum branch, and
  should be labelled as such to avoid being mistaken for baseline fidelity work.
**Action**: no build recommended by this DISCOVER pass; this is squarely a director-authored
curriculum artefact decision per R13, outside this agent's scope.

---

## 5. Schema/structure implications (described, not built)

**domain**: other
**assumption_tested**: What the current single-national-price data model would need to become
to represent zonal prices, per the director's "schema gate" framing.
**benchmark_value**: N/A — structural/design description only, informed by the REMA mechanism
(§1, §3) and the task's own stated interface name (`company/interfaces/sim_interface.py::
get_forward_price`), which this researcher did not read (per the epistemic constraint on this
role, sim/company/saas code is off-limits) — the description below is inferred purely from the
mechanism REMA describes plus the function name given in the task brief, not from reading the code.
**confidence**: L (structural inference only, not sourced from reading the actual schema, and
explicitly UNVERIFIED against current code)
**source**: mechanism basis per §1/§3 above (DESNZ options assessment); no code source (by design)
**finding — UNVERIFIED, needs direct code read by a BUILD-scoped agent**:
A price interface currently returning a single scalar/series per settlement period (implied by
a `get_forward_price()` signature with no zone argument) would, under a zonal regime, need to
become **zone-indexed**: the natural shape is either (a) a `zone_id` parameter added to the
existing call (backward-compatible: national price = a distinguished "GB" zone or an aggregate),
or (b) the return type widening from scalar to a `{zone_id: price}` mapping per settlement
period. Either shape change is a genuine **schema gate** (per the director's own naming) because
it touches every caller that currently assumes one price applies uniformly to every customer —
consistent with the portability design constraint already in CLAUDE.md ("no hardcoded
settlement granularity... product as first-class wherever fuel is one" — the same principle
applies to *location* as first-class wherever a customer's zone is not GB-wide). This finding
is explicitly a structural inference for planning purposes; the actual current shape of
`get_forward_price` and its callers must be confirmed by a BUILD-scoped read before any schema
change is designed in detail — **UNVERIFIED, needs BUILD-lane code read of
`company/interfaces/sim_interface.py` and its callers**.

---

## Summary of UNVERIFIED items (no fabricated figures)

1. **Exact current signature/return shape of `get_forward_price`** — not read by this
   DISCOVER-scoped agent (epistemic wall); needed before any schema design work.
2. **Whether the RNP legislative timetable (TNUoS reform "by 2029 at the very latest") has since
   slipped** beyond the 2026-04-21 delivery plan snapshot — this researcher found no document
   dated after 2026-04-21 confirming or revising that date; treat any date beyond that as
   UNVERIFIED without a fresher fetch.
3. **Final REMA cost-benefit analysis (CBA)** comparing zonal vs RNP quantitatively — the Summer
   Update 2025 says this would be "published later in the year" (i.e. later in 2025); this
   researcher did not locate that CBA document in this session and it is UNVERIFIED whether it
   has been published as of 2026-07-21 — needs a follow-up fetch of the REMA collections page
   if quantitative £-benefit figures are needed for curriculum design.

## Sources consulted (full list)
- DESNZ, REMA Options Assessment (PDF, 2024-03-12) — https://assets.publishing.service.gov.uk/media/65eb48f362ff48ff7487b30a/rema-options-assessment.pdf
- DESNZ, REMA second consultation landing page — https://www.gov.uk/government/consultations/review-of-electricity-market-arrangements-rema-second-consultation
- DESNZ, REMA collection — https://www.gov.uk/government/collections/review-of-electricity-market-arrangements-rema
- DESNZ, REMA Summer Update 2025 (accessible webpage, 2025-07-10) — https://www.gov.uk/government/publications/review-of-electricity-market-arrangements-rema-summer-update-2025/review-of-electricity-market-arrangements-rema-summer-update-2025-accessible-webpage
- DESNZ, Reformed National Pricing (RNP) Delivery Plan (accessible webpage, 2026-04-21) — https://www.gov.uk/government/publications/reformed-national-pricing-rnp-delivery-plan/reformed-national-pricing-rnp-delivery-plan-accessible-webpage
- (Referenced within DESNZ docs, not independently fetched): LCP Delta & Grant Thornton, "System
  Benefits from Efficient Locational Signals" (2024); Frontier Economics & Cornwall Insight,
  "Market Signals and Renewable Investment" (2024); FTI Consulting (2022) modelling; NGESO NOA7 refresh.

All retrieved 2026-07-21 via live `curl` fetch (network available this session).
