# COMPETITOR_LANDSCAPE_GAP_CHECK — desk work only (P3, token-cheap)

**Staged:** 2026-07-08 by advisor, director-approved.
**Tier:** 2 — bounded desk analysis, no build work, no external network calls.
**Token economy note:** This is deliberately cheap work. One analysis pass, one
output document, one NTFY. Do NOT start any implementation from its findings —
findings feed the ranked backlog for director review, nothing more.

## Source material
A companion document is being staged alongside this instruction:
`docs/market_research/COMPETITOR_PLATFORMS_2026.md` — a survey of the major real
energy-retail software platforms (MaxBill, Gorilla, Gentrack g2, Kraken, Kaluza,
Axle/Amber, SAP+Salesforce two-tier).

**Provenance rule (ASSUMPTIONS.md discipline):** the survey is an unsourced,
AI-assisted compilation supplied by the director. Every quantitative claim in it
(e.g. "30-40% cost-to-serve reduction", "17+ production AI agents", "400+ OEM
integrations") is UNVERIFIED. Treat the document as a *structural* reference —
what functions real platforms perform — not as a source of figures. Register it
in ASSUMPTIONS.md accordingly.

## The task (one pass)
Cross-check the Phase RW SaaS Estate Coverage Map (22 categories:
eliminated/recreated/interfaced) against the functional inventories in the survey.
For each platform capability that maps to something a real UK domestic supplier
must do, classify it:

- **COVERED** — exists in the estate map (cite the category/module).
- **PLANNED** — already on the strategic roadmap or ranked backlog (cite where).
- **GAP** — a function real platforms treat as core that Poesys neither has nor
  has planned. For each gap, one line on what fidelity it would add and roughly
  what it would touch.
- **OUT-OF-SCOPE** — real-platform capability that does not apply to the sim's
  mission (e.g. multi-play telco bundling, physical field-service logistics).
  Say why, briefly.

Capabilities to make sure the sweep covers (from the survey): dunning &
algorithmic payment plans; retroactive bill recalculation; MHHS half-hourly
settlement; market messaging / switching flows (DCC-analogue); broker & partner
commission (PRM); portfolio recosting / margin leakage detection; forecast-driven
hedge volume dictation; DERMS/flex & export credits; pass-through (Amber-style)
tariff as a product-range candidate; migration tooling.

## Output
One document: `docs/market_research/ESTATE_GAP_ANALYSIS.md` — the four-way
classification table plus a short ranked list of the GAP items by fidelity value.
That ranked list feeds the P-5 backlog for the director's next re-rank; it does
not authorise any build.

## Definition of done
Document committed + one NTFY summarising: counts per classification and the top
3 gaps by fidelity value. Nothing else.
