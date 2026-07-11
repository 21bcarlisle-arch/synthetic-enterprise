**PARKED IN PROGRESS (2026-07-11):** Pass 1 built — `docs/domain_artefact_library/`
(INDEX.md + 3 real sourced entries: PowerTAC 2020, Kill Bill/Lago, TigerBeetle/XTDB), see
PRIORITIES.md's own entry for the full verdict summary. ~17 sources remain un-surveyed
(this instruction's own scope is genuinely multi-session). Moved here rather than left in
the staging root per the 2026-07-11 in_progress/ convention. Move to `done/` once the
survey and all required outputs (a)-(f) are judged sufficiently complete — no fixed
threshold set, agent's own call per the instruction's "designs the approach... depth per
source" delegation.

---

# INSTRUCTION: DOMAIN_ARTEFACT_LIBRARY — external codification discovery pass

**Place in the epoch arc:** Cross-epoch enabler, anchored in Core Fidelity. Extends the invariant library and ASSUMPTIONS.md lineage now (R10 fuel), pre-seeds Epoch 2 (settlement/three-clock design references, cost-stack benchmarks), Epoch 3 (adapter-schema candidates — the wall IS the go-live seam), and Epoch 4 (tournament prior art). Discovery work, background-lane compatible: metric = anchors produced.

## Problem

We are building processes and interfaces that the UK energy market and the wider software world have already codified publicly. We are not leveraging this. Three classes of external artefact exist:

1. Published UK market specifications and design artefacts that define, with typed schemas and process maps, exactly what a supplier's boundary and obligations look like.
2. Regulatory codifications of corporate processes (billing content, complaints lifecycle, collections ladder, DD failure vocabularies, cost-stack models, comparator accounts).
3. Open-source domain models and simulations (retail-market simulation, billing engines, ERP/CRM/ticketing data models, ledger/bitemporal database design patterns) representing decades of prior art.

Director decision: mine these deliberately rather than reinvent.

## Required outcome

A curated, versioned domain reference library in the repo, and derived artefacts flowing from it into existing programmes.

## Non-negotiables

1. **Provenance tagging on every artefact**, three permitted-use tags:
   - `company-knowable` — passes the "could a real UK supplier know this?" test; may inform organs inside the wall.
   - `generator-anchor` — may shape SIM generation.
   - `validator-anchor` — may feed the invariant library / sanity daemon / population tests.

   `generator-anchor` and `validator-anchor` are **mutually exclusive per source** — the independence rule (no marking-own-homework). `company-knowable` may combine with `validator-anchor`. The company's runtime must never consume generator- or validator-tagged material.

2. **R9 applies:** every library entry cites source, URL, version/date. No narrative claims about what a spec says without the fetched evidence.

3. **No dependency adoption.** Borrowing schemas, data models, enumerations, and design patterns is in scope. Adopting external code as a runtime dependency is out of scope and requires a separate proposal. Record the licence of anything whose design is borrowed.

4. **One open question to register, not answer:** whether the go-live company runs real open-source corporate machinery (ERP/CRM) behind the wall versus bespoke organs shaped like them. Log it for the WALLED_INTERFACES framing.

## Survey scope (indicative, not exhaustive — extend where valuable)

- **UK market specs:** REC / Energy Market Data Specification / DTC flow catalogue; MHHS Programme baselined design artefacts (TOM, interface catalogues, method statements); Elexon BSC + BSCPs; Smart Energy Code / DCC DUIS; CSS switching schedules.
- **Regulatory process codifications:** Ofgem SLCs (bill content, back-billing, debt path, PSR); Complaints Handling Standards Regulations; Bacs DD failure/cancellation reason-code sets; Ofgem price cap model (published cost stack); Consolidated Segmental Statements and challenger Companies House accounts as comparator benchmarks.
- **Open-source domain models:** PowerTAC (retail-market simulation, customer/tariff models, tournament and replay design — the versioned 2020 game specification paper is the priority artefact, ahead of the Java; also note the default-broker/fallback-supplier mechanism and tariff lifecycle state machine as design references); Kill Bill / Lago (billing, dunning, invoicing entity models); ERPNext / Odoo (GL, AR/AP, reconciliation); open CRM/ticketing (complaints/contact-centre entity design); TigerBeetle / XTDB (double-entry and bitemporal design patterns, for Epoch 2 reference).
- **Process taxonomies:** APQC PCF (utilities) and TM Forum eTOM — used to audit the module tree for functions a real supplier performs that we don't yet model.

## Required outputs

(a) The tagged library itself, in-repo, with an index.
(b) Anchor candidates promoted into the ASSUMPTIONS.md lineage, tags carried.
(c) Adapter-schema candidates registered as inputs to the WALLED_INTERFACES programme.
(d) Invariant-library extension candidates (R10 class-level, validator-tagged sources only).
(e) A coverage-gap report: module tree mapped against the external taxonomies, gaps ranked by materiality, delivered as evidence for the Epoch-2 framing.
(f) A per-source **adopt / adapt / skip** verdict table with one-line rationale each — so leverage decisions are explicit and reviewable, not implicit in what got copied.

## Sequencing

Background-lane discovery. Must not displace DOMAIN_SENSE_AND_COMPLIANCE or BILL_CORRECTNESS_ADDENDUM. Agent designs the approach, storage format, and depth per source; nothing above prescribes mechanism.
