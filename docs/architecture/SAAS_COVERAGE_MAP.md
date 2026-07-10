# SaaS Estate Coverage Map

Standing artifact (refreshed at retro cadence, ~every 50 phases). Answers one question for an
investor or architect: **of the ~20+ SaaS categories a real UK energy supplier assembles to run
its business, how much does Poesys's architecture eliminate outright, how much does it recreate
natively, and how much stays a real-world boundary it must interface with?**

Context: a real UK supplier is typically a patchwork of retail core (Kraken/ENSEK/Gentrack), ETRM
(Brady/EnergyOne/ION), market messaging (ElectraLink DTS/DIP), a data platform (Snowflake/dbt/BI),
finance ERP (NetSuite/SAP), an engagement CDP (Braze/Segment), a debt ecosystem (collections
platforms, DCA panels, debt sale, credit bureaux), process mining (Celonis), energy margin
analytics (Gorilla's "Energy Margin Intelligence" -- a venture-funded category for exactly the
margin-in-every-decision consistency Poesys builds natively), CX/contact AI, iPaaS, ITSM/
observability, KYC, and ESG reporting -- 15-20+ separately licensed, separately integrated
products, each a fragmentation tax.

## The taxonomy

Every category below, and every Poesys module it maps to, sorts into exactly one bucket:

- **A -- ELIMINATED BY ARCHITECTURE.** Software that exists only to compensate for fragmentation
  (CDP, iPaaS, process mining, margin intelligence, most BI). An event-native, single-data-model
  company does not need a separate product for these -- the unified model makes the problem the
  category solves not exist in the first place. Poesys does not recreate these; it makes them
  unnecessary.
- **B -- RECREATED, INTEGRATED.** Native functions Poesys builds itself (billing, CRM, ETRM/
  hedging/risk, finance core, collections, engagement decisioning, regulatory stack, ESG). Spans
  both retail AND trading in one codebase, which no vendor in the market does today.
- **C -- INTERFACED AT THE BOUNDARY.** Real-world rails that are neither recreated nor eliminated
  -- credit bureaux, payment/PSP, DCC smart-meter comms, message delivery, KYC, external property
  data. These become epistemic-boundary adapters at go-live, the same pattern as the swappable
  market-feed adapter (Phase PV, `tools/market_data_port.py`).

## What this map does NOT claim (2026-07-10, director page comment: "we are over claiming here")

Director feedback, correctly: listing real market leaders (Kraken, Gentrack, Brady, NetSuite --
production systems each serving real customers at real scale, hardened through real incidents,
real regulatory audits, real security certification, real SLAs) in the same row as a Poesys
module is easy to misread as a claim of *parity*. It is not one, and this map should say so
plainly rather than let the reader infer it:

- **Bucket B ("recreated") means the same architectural FUNCTION exists as real, working code**
  -- a `company/billing/` invoice run genuinely executes; it does not mean that code has the
  production depth, edge-case coverage, scale-testing, security hardening, or multi-tenant
  reliability of a system that has run millions of real customer accounts for years.
- The "no vendor does both retail and trading in one codebase" observation is an architectural
  fact about how this project is structured, not a claim that this project's trading or retail
  depth individually matches a vendor that specializes in only one.
- Where the real gap is is precisely the point, not something to obscure: it IS the roadmap.
  Every Bucket-B row above is honestly a "this pattern works, now go deepen it" item, not a
  "solved" one -- see PRIORITIES.md and CORE_FIDELITY_BEFORE_LOOPS.md for what deepening is
  actually queued next.

## Category landscape

| Category | Market leaders | Poesys mapping | Bucket |
|---|---|---|---|
| Retail core / CIS (billing, contracts, meter points) | Kraken (Octopus), ENSEK, Gentrack | `company/billing/` (54+ modules: invoice, contract, meter_points, direct_debit, dual_fuel_bill) | B |
| ETRM / CTRM (trading, hedging, risk) | Brady, EnergyOne (Allegro), ION | `company/trading/`, `company/risk/`, `sim/hedging.py`, `sim/risk_committee.py` | B |
| Finance / ERP core | NetSuite, SAP, Oracle Fusion | `company/finance/double_entry.py`, `saas/ledger.py` | B |
| Collections / arrears workflow | Aryza, in-house DCA tooling | `simulation/arrears_engine.py`, `company/billing/collections.py`, `company/billing/debt_referral.py` | B |
| CX / engagement decisioning | Braze, Salesforce Marketing Cloud | `saas/contact_model.py`, `company/crm/`, `company/policy/decision_policy.py` | B |
| Regulatory compliance stack | Gentrack Regulatory, bespoke in-house | `company/regulatory/` (62 wired schemes, Phase OL), `company/compliance/` | B |
| ESG / carbon reporting | Position Green, Workiva, Diligent ESG | `company/sustainability/`, `company/billing/carbon_footprint.py` | B |
| Demand response / flexibility | Kaluza Flex, Limejump | `saas/demand_response.py` | B |
| Nudge / behavioural engagement physics | Opower (social norms), in-house | `simulation/nudge_physics.py`, `company/analytics/nudge_discovery.py` (Phase RV) | B |
| Customer Data Platform (CDP) | Segment, Braze CDP, Tealium | none needed -- single event-native data model (`site/data/*.json`) replaces the stitching problem a CDP solves | A |
| iPaaS / integration middleware | MuleSoft, Boomi, Workato | none needed -- one codebase, direct module imports, no point-to-point integration surface | A |
| Process mining | Celonis | none needed -- `company/analytics/decision_event_ledger.py` gives native, real-time process visibility; nothing to mine after the fact | A |
| Energy margin analytics / margin intelligence | Gorilla Energy ("Energy Margin Intelligence") | none needed -- `saas/cost_to_serve.py` + pricing consistency gates make margin-truth a property of every decision, not a bolt-on analytics layer | A |
| BI / data warehouse (Snowflake/dbt/Looker) | Snowflake, dbt Labs, Looker/Power BI | none needed -- `tools/generate_dashboard_data.py` and friends compute board-grade analytics directly off the operational data model, no separate warehouse/ETL | A |
| ITSM / observability | ServiceNow, Datadog, PagerDuty | `background/session_watchdog.py`, `background/health_check.py`, `docs/observability/agent_status.json` | B |
| Credit bureau / KYC | Experian, Equifax, TransUnion | `tools/credit_bureau_port.py` (LIVE epistemic-boundary adapter, Phase QR) | C |
| Payment service provider (PSP) | Stripe, GoCardless, Worldpay | adapter PLANNED (`site/platform` adapter registry) -- payment behaviour currently modelled directly, not yet via a swappable PSP boundary | C |
| Smart meter comms (DCC) | DCC, Landis+Gyr, Siemens | adapter PLANNED -- HH smart-meter data currently generated directly rather than read through a DCC-shaped boundary | C |
| Market messaging (DTS/DIP) | ElectraLink | not yet a named adapter -- settlement/registration data currently flows directly from Elexon ingestion (`sim/`), no DTS-shaped boundary modelled | C |
| Message delivery (email/SMS/post) | Twilio, SendGrid, Royal Mail Mailmark | not yet built -- comms are logged as decision events, not dispatched through a real delivery rail | C |
| Debt sale / DCA placement | Lowell, Cabot, DCA panels | `simulation/arrears_engine.py` write-off is the current terminal state; placement/sale economics are backlog (item 1 below) | C |
| Property / EPC data | GOV.UK EPC register, Rightmove | not yet wired -- backlog (PRIORITIES.md: EPC-calibrated consumption distributions) | C |

**Headline metric** (computed fresh by `tools/generate_saas_coverage_data.py` from the table
above, not hand-typed): of 22 categories, **5 eliminated by architecture (22.7%)**, **10 recreated
integrated (45.5%)**, **7 interfaced at the boundary (31.8%)**.

## Transferability audit frame

This combines with the Platform section's existing universal/market/UK-specific module tagging
(`tools/generate_platform_data.py`, `LAYER_TAGS`/`COMPANY_DOMAIN_TAGS`) into one architecture
story: the **A-bucket** claims here are the "this fragmentation tax disappears entirely" half;
the universal/market/UK tags are the "and here is how much of what's left is UK-specific vs.
portable to another liberalized energy market" half. Kraken ($8.65B spinout of the integrated-
retail-platform thesis) and Gorilla (a venture-funded standalone category for margin-truth-in-
every-decision) are the two external existence proofs referenced in the deck-refresh backlog --
Poesys claims both, plus trading integration, plus autonomy, plus the simulation moat.

## Backlog (queued behind current threads, do not interrupt)

1. **Debt journey extension:** write-off is not terminal in reality -- add DCA-placement/debt-sale
   stage economics (placement windows, recovery-rate, sale-price-vs-book haircut) to the debt
   process. Fits the `PROCESS_NOT_EVENTS.md` debt branch.
2. **Credit bureau as collections-strategy feed:** the credit bureau adapter (`tools/
   credit_bureau_port.py`) currently feeds only acquisition credit checks (Phase QR); it does not
   yet also feed collections strategy with the same purchased, imperfect external read.
