# SUPPLIER_REPORTING_STANDARD — report like a real at-scale UK supplier

**Staged by advisor, director-decided 2026-07-11.** Source: research pass over Ofgem CSS guidance (OFG1163, Oct 2025 revision), Centrica/British Gas ARA 2024–25, Octopus Energy Group FY25, AGL FY25/HY26, NRG/Vistra retail segment reporting.

## Place in the epoch arc
Epoch 2 (the value cycle / commercial brain): the reporting artefacts below are the *output surface* of the close→learn loop — they exercise revenue, fuel cost, non-commodity split, indirect costs, volumes, and meter counts end to end. Items in §4 extend the DOMAIN_SENSE_AND_COMPLIANCE obligations register (in-flight P1).

## Sequencing (binding)
Subordinate to DOMAIN_SENSE_AND_COMPLIANCE and anything ahead of it in PRIORITIES.md. Batch at a phase boundary; do not interrupt in-flight work. Nothing here is urgent.

---

## 1. DECIDED: a CSS-shaped segmental statement as the annual report backbone

**Problem.** The current annual report is management-accounts-shaped. Real UK suppliers above threshold (50k domestic meter points, or just 10 non-domestic) must publish a Consolidated Segmental Statement in a regulator-defined format. Poesys should report in that format because (a) it is the exact "how would a real supplier report" answer, (b) at go-live it becomes a genuine licence obligation (SLC 19A), and (c) producing it honestly stress-tests the value cycle.

**Requirements (this is the domain spec, from Ofgem's own template — not an architecture choice):**
- Four segments: electricity-domestic, electricity-non-domestic, gas-domestic, gas-non-domestic, plus an aggregate column.
- P&L lines per segment: revenue from sale of electricity/gas; other revenue; direct fuel costs; transportation costs (TNUoS/DUoS/BSUoS/gas transportation); environmental & social obligation costs (RO, FiT, CfD, CM, ECO, WHD); other direct costs; indirect costs; EBITDA; depreciation & amortisation; EBIT.
- Operational lines per segment: volume at the meter point net of losses (TWh / MThms); WACOE/WACOG (= direct fuel costs ÷ volume, £/MWh and p/th); meter points as a 12-month average of monthly closing counts.
- A reconciliation table from CSS figures to the "statutory" management accounts, with each reconciling item named.
- A short hedging-policy note: hedging applied to default vs fixed-term tariffs, and who bears volume risk.

**Known gap this forces:** indirect costs must decompose (at minimum: bad debt, metering, customer service, sales & marketing/acquisition, central overhead — CSS guidance also names PSR cost-to-serve and R&D). Today cost-to-serve is a single fixed-overhead line; bad debt exists separately via the arrears ledger. How to decompose is the agent's call; *that* it decomposes is the requirement. Where a component genuinely doesn't exist yet, report it as an honest named gap, never a fabricated allocation.

**Non-negotiables:** epistemic wall unaffected (the CSS is the company's own publication — company-knowable by definition). Every line must reconcile to the ledger; no hand-typed figures.

## 2. DECIDED: a board-grade KPI block beside the financials

Real supplier reports pair the P&L with a small, stable KPI set. Poesys already computes most inputs. Required set:
- Churn % of average customers over the year (Centrica's definition).
- Complaints per 1,000 customers (the Ofgem/Citizens Advice league-table metric).
- Margin and revenue per customer (ARPU) by segment.
- CSAT/NPS from the existing satisfaction/survey machinery (measured, not SIM-true — company side of the wall).
- Direct Debit share, estimated-read rate, GSOP/SLC14 payment counts — all already computed somewhere; this consolidates them onto one board surface.

**Registered, not built:** relative metrics (churn spread vs rest-of-market, price vs cap positioning — the best-in-class AGL/Octopus pattern) are blocked on the simulated competitor field, an already-identified Epoch-2 missing piece. Name them in the KPI block's design as "awaiting market backdrop" rather than omitting silently.

## 3. DECIDED: Fuel Mix Disclosure + carbon intensity of supplied energy

A standing annual licence obligation for every GB supplier: publish the fuel mix of electricity supplied and its CO2 intensity (g/kWh). This is the honest carbon story for a retailer — the footprint that matters is the energy sold, not the office. Computable from settlement volumes × published grid generation/intensity data (NESO publishes this; the project already uses the NESO CKAN portal — a generator/validator-anchor candidate, provenance-tag it accordingly). Absent REGO purchases, the disclosed mix is the residual mix — model that honestly rather than claiming green supply. Connects to the existing green-claims obligation in the register.

Corporate carbon boilerplate (SECR, TCFD, transition plans) is explicitly OUT — low fidelity value for this simulation.

## 4. DECIDED: three obligations-register additions

Extend the DOMAIN_SENSE_AND_COMPLIANCE register (risk-tiered per its own method; MANUAL status is fine where no tracker exists yet):
1. **Capital adequacy** — Ofgem framework: Capital Floor (positive adjusted net assets = net assets less intangibles/goodwill) and Capital Target (£115 adjusted net assets per dual-fuel customer). No cash/balance-sheet layer exists yet to check it against — register the obligation now; it becomes checkable when the Epoch-2 cash/collateral/working-capital layer lands, and is a design input to that layer.
2. **Fuel Mix Disclosure** — the §3 obligation itself.
3. **Cyber baseline (NIS/CSRB)** — Ofgem is competent authority under NIS Regulations 2018; direction of travel (Cyber Security & Resilience Bill + live DESNZ/Ofgem consultation) is baseline cyber requirements for ALL licensees. Not sim physics — a register entry and a go-live checklist item.

## Explicitly out of scope
- Cross-sell/bundling metrics (services per customer, order intake, subscription MRR): real churn-physics lever, but hard-blocked by PORTABILITY_DESIGN_CONSTRAINTS until post-Epoch-3. Do not build, stub, or scaffold.
- US/Australian report formats beyond the lessons already folded in above.

## Open (director or agent judgement, not decided)
- Weather-normalised margin commentary (US-retailer pattern; the harness knows the weather draw, so Poesys could do this natively and honestly). Cheap if it falls out of existing data; skip if not.
- Where the CSS surface lives (annual report vs Supplier tab) — agent's call under existing site design laws.
