# Ofgem supply licence readiness — DISCOVER findings

**Atom:** `F5_ofgem_licence_readiness` (epoch 5, `docs/design/maturity_map.yaml`, `provenance: proposal`).
**Status:** DISCOVER only, per RERANK_AND_PROVISIONAL_PLAN.md ("ACCEPT, DISCOVER now, build gated to
Epoch 5"). No FRAME or BUILD in this pass. `level_current` unchanged (0) — DISCOVER work does not move
levels (MATURITY_MAP.md §3: L1 requires having been *built*).

## Why this atom exists

None of the map's existing epoch-5 atoms model whether the simulated company could actually **hold**
an Ofgem electricity/gas supply licence in the first place:
- `H3_production_readiness_nfr_evidence`/`H4_go_live_nfr_register` — non-functional/operational
  readiness (SRE-style: availability, security, capacity).
- `F3_obligations_register` — ongoing per-transaction compliance invariants (already built, L3).
- `F4_company_internal_authz` — internal authz/segregation of duties.

The licence-holding question is a distinct, prior gate: a real supplier's board treats "are we
licensed to operate at all" as decided by Ofgem's licensing function, not its own ops/security
review. The director's own re-rank reasoning: *"the licence path IS the gate between 'simulation'
and 'company' ... what it turns up may CONSTRAIN Epoch-3 design, so discovering it late is
expensive."*

## Findings (real, sourced — WebSearch/WebFetch against ofgem.gov.uk, 2026-07-12)

### 1. The three ongoing licence conditions (Standard Licence Conditions 4A–4C)

Both the Electricity Supply and Gas Supply Standard Consolidated Licence Conditions carry three
linked conditions, introduced 2021 in direct response to the supplier-failure wave:

- **SLC 4A — Operational Capability.** The supplier must have the systems, processes and resources
  needed to serve its customer base competently (not just financially — operationally).
- **SLC 4B — Financial Responsibility Principle.** Requires suppliers "at all times to manage
  responsibly costs that could be mutualised (shared across consumers), to take appropriate action
  to minimise such costs, and at all times to have adequate financial arrangements in place to meet
  their costs at risk of being mutualised." "Mutualised costs" is the direct mechanism by which one
  supplier's failure becomes every surviving supplier's (and ultimately every customer's) bill —
  Renewables Obligation buy-out shortfalls, Feed-in Tariff levelisation shortfalls, and Supplier of
  Last Resort (SoLR) costs are all socialised this way when a failed supplier can't pay.
- **SLC 4C — Ongoing Fit and Proper Requirement.** SLC 4C.1 prohibits appointing or keeping in post
  any person with Significant Managerial Responsibility or Influence who is not "fit and proper."
  This is *ongoing*, not just an application-time gate — a real supplier can lose its licence
  eligibility through a later appointment, not only at inception.

Source: [Electricity Supply Standard Consolidated Licence Conditions](https://www.ofgem.gov.uk/sites/default/files/2025-08/Electricity-Supply-Standard-Consolidated-Licence-Conditions.pdf),
[Gas Supply Standard Consolidated Licence Conditions](https://www.ofgem.gov.uk/sites/default/files/2025-08/Gas-Supply-Standard-Consolidated-Licence-Conditions.pdf),
[Ofgem: firm on upholding rigorous company standards](https://www.ofgem.gov.uk/publications/ofgem-firm-upholding-rigorous-company-standards-behalf-energy-customers),
[Supplier Licensing Review decision doc, Nov 2020](https://www.ofgem.gov.uk/sites/default/files/docs/2020/11/201117_-_slr_decision_doc_final_v.2.pdf).

### 2. Minimum Capital Requirement (quantified, real figures)

Following the 2021–22 collapse of 30+ suppliers (Ofgem's own figure: cost to consumers/taxpayers of
~£10bn via SoLR/mutualisation), Ofgem's 26 July 2023 decision introduced, for domestic suppliers:
- **Capital Floor: £0.**
- **Capital Target: £130 per dual-fuel-equivalent domestic customer.**
- Phased in via **milestone assessments** (Ofgem checks suppliers' progress toward the target at
  defined checkpoints, not a single pass/fail date) — the exact milestone dates were not resolved by
  this pass's sources and are a named open item below.

Source: [Decision on introducing a minimum capital requirement and ringfencing CCBs](https://www.ofgem.gov.uk/decision/decision-introducing-minimum-capital-requirement-and-ringfencing-customer-credit-balances-direction),
[FRC Decision doc, July 2023](https://www.ofgem.gov.uk/sites/default/files/2023-07/FRC%20Decision%20doc%20-%20July%202023.pdf),
[Financial resilience in the energy retail market](https://www.ofgem.gov.uk/energy-regulation/business-resilience/financial-resilience-energy-retail-market).

### 3. Ring-fencing of Customer Credit Balances (CCBs) — a *directed*, not blanket, power

Ofgem's power here is a **direction**, not a flat universal rule: "in certain circumstances we may
tell suppliers to set aside customer credit balances from other financial resources ... unless it
is not in the consumer interest." This matters for modelling: a real supplier's CCB ring-fencing
status is a company-specific regulatory state (has Ofgem directed it, or not), not a constant true
for every supplier. Renewables Obligation payment ring-fencing is named as a separate, related
mechanism on the same Ofgem page (money to pay RO liabilities kept segregated).

Source: [Financial resilience | Ofgem](https://www.ofgem.gov.uk/energy-regulation/business-resilience/financial-resilience)
(webpage), [Statutory Consultation: Strengthening Financial Resilience](https://www.ofgem.gov.uk/consultation/statutory-consultation-strengthening-financial-resilience-ringfencing-customer-credit-balances-and-introducing-minimum-capital-requirement).

### 4. Licence application process (current, not just historical)

As of Ofgem's own 27 February 2026 guidance update, licence applications carry a reintroduced
**six-month processing timescale**, with "Criteria 3" of the application guidance specifically
naming fitness of the applicant to hold a supply licence. This confirms the licence-readiness gate
is a live, current-day Ofgem process, not a historical artefact of the 2021-22 crisis alone.

Source: [Gas and electricity licence application guidance and forms](https://www.ofgem.gov.uk/guidance/gas-and-electricity-licence-application-guidance-and-forms),
[OFG1164 application guidance PDF](https://www.ofgem.gov.uk/sites/default/files/2025-06/Guidance_on_how_to_apply_for_a_gas_or_electricity_licence.pdf).

## What this does NOT yet cover (honest open items for the next DISCOVER pass)

- **Capacity Market / Renewables Obligation registration duties** — named in this atom's original
  registration text as in-scope, but not independently re-verified this pass; `F3_obligations_register`
  may already cover some of this ground (its `real_world_twin` is "Ofgem licence obligations
  register") — the overlap/boundary between F3 (ongoing per-transaction invariants) and F5 (the
  licence-holding gate itself) needs an explicit FRAME-stage decision on where SLC 4B's
  mutualised-cost obligations are modelled, not assumed disjoint.
- **Milestone assessment dates/mechanics** for the Capital Target phase-in were not resolved by the
  sources fetched this pass (the FRC decision doc PDF itself would need a direct read, not just the
  summary webpage).
- **Quantified fit-and-proper test criteria** (what specifically Ofgem checks for SLC 4C) — the
  search surfaced the condition's existence and its target (Significant Managerial Responsibility or
  Influence holders) but not Ofgem's detailed assessment criteria.
- No comparison yet to how this atom's future BUILD would interact with the company's *existing*
  capital-employed/ROCE modelling (`company/finance/segment_capital.py`, B2 atom) — the Minimum
  Capital Requirement is a licence-level absolute floor, distinct from segment-level ROCE, and the
  two should not be conflated when this atom eventually frames its own target-level definitions.

These are genuine next-DISCOVER-pass items, not silently dropped scope (R10).
