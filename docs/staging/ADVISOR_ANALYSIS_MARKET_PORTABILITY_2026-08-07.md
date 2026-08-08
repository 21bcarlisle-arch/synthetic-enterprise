# [ADVISOR-ANALYSIS] — Market portability: where this travels, what travels, what rebuilds (2026-08-07)

**Type:** [ANALYSIS — director-commissioned early view, advisor-authored]. The geographic/segment dimension of the traffic-and-sophistication forecast: which markets can host this company, what is invariant, what parameterises, what rebuilds. Method: structural comparison from the machine's own architecture outward, on advisor domain knowledge (early 2026); country spot-figures are `~` and get a GB-style verification sweep only when a market is actually picked. Refute with evidence.

## The preconditions, derived from our own architecture (a market must supply ALL of these)
P1 **A supplier role** — retail competition with a licensed entity owning tariff, bill, and relationship. No supplier role, no company.
P2 **Granular consumption data, supplier-accessible** — HH/15-min per customer. The personalisation engine's oxygen.
P3 **A time-varying cost stack reaching retail** — wholesale shape and/or ToU network charges. Flat regulated retail kills the abatement engine: nothing to shift against.
P4 **Market processes** — switching/registration/CoT machinery (the unhappy-path physics generalises; registries differ).
P5 **A carbon signal** — grid intensity data and/or a carbon price to anchor the abatement ledger.
Fail any of P1–P3 and the model does not degrade — it dies. That boundary excludes vertically-integrated and fully-regulated retail everywhere (most US states, most of Asia ex-Japan, much of the Gulf/Africa).

## What travels — the portability decomposition of Poesys
**INVARIANT (ships untouched — this is the durable IP, now provably so):** the harness and method (agents, gates, ratchets, Birth Certificates, characterization discipline); the epistemic wall as LAW — its test simply parameterises: *"could a real {market} supplier know this?"*; the bitemporal event spine and three-clocks discipline (every settling market reconciles on billed/settled/banked); population/life-event machinery (re-anchored, not rewritten); affordability/collections psychology (human constants); the value-cycle framing; the map/index/naming governance.
**PARAMETERISE (tables, not code):** cost-stack line items (every market = network + policy + market lines; the TABLE swaps, the SHAPE holds), tariff structures, cap-analogues, calendars, losses factors, typical-consumption anchors, weather physics (already hierarchical by design — re-anchor the data).
**ADAPTER-SWAP (the wall pays its second dividend):** the counterparty set behind the seam — settlement body, metering/data infrastructure, switching registry, payment rails, market comms. Go-live was defined as "swap sim adapters for real endpoints"; **multi-market is the identical operation with a different endpoint set.** The architecture chosen for Epoch-5 is, unchanged, the architecture for geography.
**REBUILD (accept it, per market):** compliance organs against each regulator's rulebook; consumer-protection surfaces; language/cultural interaction layers; local credit/debt law in collections.

## Segment first: GB non-domestic (SME → I&C) — the cheapest extension that exists
Same MPANs, same Elexon, same MHHS (which deliberately unifies settlement across segments), same wall. What changes: no domestic cap (micro-business protections and SLC 7A back-billing instead; deemed rates exist); **CCL replaces parts of the domestic levy set** (with CCA/EII reliefs); a whole new counterparty CLASS — **the TPI/broker layer** (commission disclosure, a fresh unhappy-path family); explicit MOP/DC/DA-successor contracts; credit risk and security deposits; multi-site portfolios; SIC-code load-shape archetypes replacing household segments; flex/basket/corporate-PPA product shapes. Reuse estimate: **~70–80% of the company as-is**; the deepening register gains rows rather than the architecture gaining organs. Abatement leverage: one mid-size I&C site ≈ 10–100 households. **Verdict: do this before any border.**

## The scorecard — early view (● strong ◐ partial ○ weak against P1–P5)
| Market | P1 | P2 | P3 | P4 | P5 | Adapter set to build | Note |
|---|---|---|---|---|---|---|---|
| **GB SME/I&C** | ● | ● | ● | ● | ● | TPI layer, CCL line | ~70–80% reuse; first move |
| **Australia (NEM)** | ● | ◐→● | ● | ● | ● | AEMO MSATS/B2B, NMI, DNSP tariffs, DMO/VDO | ~**5-minute settlement** + **CDR energy** = statutory data right; solar/battery/VPP makes personalisation value extreme. Best foreign fit |
| **Texas (ERCOT)** | ● | ● | ● | ● | ◐ | ERCOT/Smart Meter Texas, TDU tariffs, POLR | ~near-100% smart in competitive areas, 15-min; scarcity pricing = shape value; lighter consumer-protection surface. US = state-by-state, each its own market |
| **Nordics (NO/DK/FI/SE)** | ● | ● | ● | ● | ● | One central **datahub per country** (Elhub etc.) | ~hourly-billing norm, spot-linked retail proven (the Tibber existence-proof); small books |
| **Netherlands** | ● | ● | ● | ● | ● | EDSN hub, SEPA DD | clean single-hub adapter; dynamic-tariff boom; small |
| **Spain** | ● | ● | ● | ● | ◐ | Datadis, distributor APIs | ~smart ≈100% for years; hourly default (PVPC); regulated/free duality to navigate |
| **Ireland** | ● | ◐ | ● | ● | ● | SEM, ESBN | Anglophone, familiar code culture; small |
| **Germany** | ● | ○→◐ | ◐ | ● | ● | MaKo/EDIFACT comms, SMGW metering | the big prize with the big rebuild: ~smart laggard, heavy market-comms; §14a flexible-load signals emerging |
| **France** | ◐ | ● | ◐ | ● | ● | Enedis APIs | ~Linky ≈ full — superb data; but regulated-tariff gravity thins the supplier economics |
| **Italy / Japan** | ● | ◐ | ◐ | ● | ◐ | per-market | liberalised, workable, adapter-heavy; second wave |
**Ranking for the mission (abatement per unit of build):** 1 GB-SME/I&C · 2 Australia · 3 Texas · 4 Nordics+NL (proof-density) · 5 Spain · then Germany as the strategic heavy lift. EU expansion carries one systemic simplifier: **SEPA Direct Debit is one payments adapter for ~20 markets.**

## One design-law candidate (the forecast's "preclude nothing," applied to geography)
Introduce **`market` as an explicit dimension at the seams NOW** — a market identifier in the event/context types and adapter interfaces. Cost today: near zero (single-valued: GB). What it prevents: GB assumptions metastasising through the core as unmarked constants — the geographic equivalent of the structure that dies at 10⁵. Deepening-register logic exactly: seam wide now, internals single-market. Worker sequences; director corrects retrospectively.

## Verify-before-picking shortlist (the GB-style sweep, run per chosen market)
smart-penetration %, settlement granularity/timetable, data-access regime (CDR/datahub/API), default-offer mechanism, payment-rail specifics, switching-registry interface, carbon-signal source. `~` marks above are exactly this class.

— Advisor analysis, 2026-08-07. Companion to the traffic forecast; feeds TARGET_DESIGN's portability section and, in time, an Epoch-6 question.
