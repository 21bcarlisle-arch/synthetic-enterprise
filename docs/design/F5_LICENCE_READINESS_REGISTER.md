# F5 — Ofgem Supply Licence Readiness Register (L1 consolidation)

**Atom:** `F5_ofgem_licence_readiness` (epoch 5, `docs/design/maturity_map.yaml`).
**Status:** L0 → **L1** this pass. This document IS the L1 deliverable: a consolidated,
auditable **licence-readiness register** built entirely from this atom's own already-complete
DISCOVER trail (`docs/market_research/ofgem_licence_readiness.md` + five map `simplifications`
addenda, 2026-07-12/13). **No new research was performed to produce it** — this is consolidation,
not discovery, matching the atom's L1 target definition (MATURITY_MAP.md §3: L1 = "has been
built," here meaning the scattered findings are turned into one structured, checkable artifact).
No SIM/company code was touched; this is a doc-only register, consistent with epoch-5 BUILD
gating (`loop_stage: idle` stays unchanged — a register is not a build against the sim/company
seam) and the epistemic wall (nothing here reads simulation internals; every row cites either a
public Ofgem source or a direct read of this repo's own existing code).

## How to read this register

Each row is one distinct Ofgem requirement or gate this atom's DISCOVER surfaced. **Status** is
one of:
- **MET** — the requirement is satisfied today by something real and citable (a design decision,
  an existing code module, or a confirmed non-overlap).
- **GAP** — a real go-live requirement with no company-side mechanism yet; correctly deferred to
  epoch-5 BUILD, named here so it isn't lost.
- **NOT-APPLICABLE-YET** — a requirement whose trigger condition (e.g. a customer-count threshold)
  the simulated company has not reached, so there is nothing to build against today.
- **OPEN/DISCREPANCY** — an honestly unresolved finding, preserved as found (R10/R9), not
  arbitrated to a single number.

## Register

| # | Requirement | Real-world citation | Status | Note / evidence |
|---|---|---|---|---|
| 1 | **SLC 4A — Operational Capability.** Supplier must have systems/processes/resources to serve its customer base competently. | Electricity/Gas Supply Standard Consolidated Licence Conditions, condition 4A (Ofgem, 2021 reforms). | **GAP** | No company-side operational-capability evidence pack exists yet. Overlaps in spirit with `H3_production_readiness_nfr_evidence`/`H4_go_live_nfr_register` (SRE-style NFRs) but those atoms model *build-machine* operational readiness, not the Ofgem-facing licence submission itself — the submission artifact is the actual gap. Deferred to epoch-5 BUILD. |
| 2 | **SLC 4B — Financial Responsibility Principle.** Supplier must responsibly manage costs that could be *mutualised* (shared across all consumers/suppliers on failure) and hold adequate financial arrangements against them. | Same SLC source; mechanism confirmed as the direct channel by which one supplier's failure becomes every surviving supplier's bill (RO buy-out shortfalls, FiT levelisation shortfalls, SoLR costs). | **GAP** | No company-side mutualised-cost-risk model exists. Distinct from `F3_obligations_register` (checked directly, see row 9) and from `B2`'s segment ROCE (see row 10) — this is its own, currently-unbuilt gap. |
| 3 | **SLC 4C — Ongoing Fit-and-Proper Requirement.** Prohibits appointing/keeping any person with Significant Managerial Responsibility or Influence (SMR&I) who is not fit and proper. Ongoing, not just at application. Scope is deliberately BROAD — confirmed to cover heads of finance, risk, operations, technology, data, compliance, trading/hedging, strategy, and marketing/CRM, and can extend to external advisors/consultants with effective decision-making authority, not board/exec-only. | SLC 4C text; Ofgem "firm on upholding rigorous company standards" publication. | **GAP** | Company has no role-holder registry or fit-and-proper coverage mechanism today. `F4_company_internal_authz` covers internal authz/segregation of duties, which is adjacent but not the same test (authz governs *what a role can do inside the system*; SLC 4C governs *whether the person in the role is fit to hold it at all*) — confirmed distinct by this atom's own DISCOVER, not assumed. Scope-sizing note for the eventual BUILD: coverage must span the wide SMR&I set above, not just directors. |
| 4 | **Minimum Capital Requirement — Capital Floor.** | Ofgem decision, 26 July 2023 ("Decision on introducing a minimum capital requirement and ring-fencing CCBs"). | **MET (floor value known, £0)** | Capital Floor = **£0** per dual-fuel-equivalent domestic customer — i.e. the floor itself imposes no capital requirement; it is the Capital Target (row 5) that is the substantive bar. No company-side capital-adequacy measurement exists yet against either figure — that measurement is epoch-5 BUILD scope, not this register. |
| 5 | **Minimum Capital Requirement — Capital Target.** | 26 July 2023 FRC Decision doc states **£130**/dual-fuel-equivalent domestic customer; a later-fetched source (`docs/market_research/energy_market_complexity_june2026.md`) states **£115** adjusted net assets per dual-fuel-equivalent customer (cross-referenced independently in `docs/market_research/company_treasury_risk.md`: "£57.50/domestic customer (= ~£115/dual-fuel customer; cf. Ofgem: £65/single-fuel, £130/dual-fuel)"). | **OPEN/DISCREPANCY — preserved, not resolved** | Two real, independently-sourced figures for the same target (£115 vs £130) were found across separate DISCOVER passes. Per this atom's own explicit finding (2026-07-13 addendum) and CLAUDE.md R9/R10, this is registered as a genuine unresolved discrepancy, not picked between arbitrarily — it may reflect different points in a phased ramp, a since-revised figure, or a measurement-convention difference (adjusted net assets vs. a simpler per-customer capital figure — the treasury-risk cross-reference suggests the £115 figure may derive from a £57.50/domestic-customer base doubled for dual-fuel-equivalence, which is a different derivation path than the FRC decision doc's own £130). **Resolving this requires reading the primary FRC decision PDF directly** (not a summary webpage) — named here as the specific next DISCOVER step if this atom is reopened for research, not undertaken in this consolidation pass. Known real-world reference point: Octopus Energy has publicly stated it met the Ofgem capital buffer target (cited by name in the 2026-07-13 DISCOVER addendum) — usable as a plausibility anchor once/if this atom builds a real measurement. |
| 6 | **Milestone assessments — customer-count-triggered, not date-based.** A licensed supplier must pause new domestic customer onboarding on each relevant gas/electricity licence at the **50,000** and **200,000** customer thresholds, pending an Ofgem assessment of operational capacity before onboarding may resume. | Confirmed via 2026-07-13 DISCOVER addendum (source: Ofgem financial-resilience/milestone-assessment guidance). | **NOT-APPLICABLE-YET** | The simulated company's population has not reached either threshold (current customer counts are far below 50,000 — see `site/data/customer_sample.json`/`dashboard.json` for current population figures). Directly relevant to this project's own growth atoms (`W2_2` population-draw/growth) if/when this atom is built out: a real supplier's growth trajectory is gated by regulatory review at these named milestones, not smooth — flagged for whichever atom eventually models customer-count growth trajectories at scale. |
| 7 | **Ring-fencing of Customer Credit Balances (CCBs).** Ofgem's power to require ring-fencing is a **directed**, company-specific power ("in certain circumstances we may tell suppliers to set aside customer credit balances... unless it is not in the consumer interest"), not a blanket universal rule. Renewables Obligation payment ring-fencing is a separate, related mechanism (money to pay RO liabilities kept segregated). | Ofgem "Financial resilience" webpage; Statutory Consultation, Strengthening Financial Resilience. | **GAP (mechanism-dependent, correctly modelled as company-specific)** | No company-side CCB ring-fencing state exists yet. Modelling note carried forward: this must be built as a *conditional, director/Ofgem-triggered state* (has Ofgem directed it, or not), never a constant-true flag for every company variant — matches this atom's own DISCOVER finding and this project's general R12/R13 discipline against modelling a variable regulatory power as a fixed constant. |
| 8 | **Licence application process.** Six-month processing timescale (reintroduced); "Criteria 3" of the application guidance specifically names applicant fitness to hold a supply licence. Confirms the licence-readiness gate is a live, current-day Ofgem process, not solely a historical 2021-22 crisis artefact. | Ofgem guidance update, 27 Feb 2026; OFG1164 application guidance PDF. | **GAP (informational — no company action required yet)** | No submission-timeline modelling exists; relevant only once/if this atom's BUILD models an actual licence-application go-live event with its own lead time. |
| 9 | **Capacity Market / Renewables Obligation registration obligations (supplier-side compliance cost).** | Named in this atom's own original registration text as in-scope. | **MET (confirmed no overlap, no double-count)** | Verified by direct code read (2026-07-13 DISCOVER addendum): `company/compliance/domain_invariants.py` (the `F3_obligations_register` implementation) has **zero references** to Capacity Market or Renewables Obligation anywhere — no existing coverage, no double-count risk. Separately confirmed the codebase's existing `company/market/flexibility_potential.py` + `flexibility_revenue_book.py` model a **completely different** real-world mechanism (the company *earning* CM revenue as a flexibility/DSR participant, ~£75/kW/yr) — not the *supplier-side registration/settlement-levy obligation* this row means. Same acronym, two genuinely distinct real mechanisms; confirmed structurally separate, not assumed. The supplier-side registration obligation itself remains an unbuilt gap (folded into row 2's SLC 4B mutualised-cost scope, since RO buy-out shortfalls are one of the named mutualisable costs) but the *overlap risk* that originally motivated flagging it is fully closed. |
| 10 | **Relationship to `B2_opex_cost_to_serve` / segment ROCE.** | Company's own `company/finance/segment_capital.py`. | **MET (confirmed genuinely independent, not merely asserted)** | Verified by direct code read (2026-07-13 DISCOVER addendum): B2's segment ROCE measures **per-segment** capital efficiency against a **director-set hurdle rate** (working capital = directly-attributable segment receivables; credit/settlement exposure and collateral = portfolio-level figures allocated pro-rata by revenue share — an explicit allocation, not a bottom-up measurement); it is an internal pricing/cross-subsidy-visibility diagnostic, R12-governed (never tuned to a target). This atom's Minimum Capital Requirement (rows 4-5) is a **regulatory, portfolio-wide, absolute floor** set externally by Ofgem. Zero code-level interaction or shared computation between the two — confirmed, not just re-asserted. Safe to build both without conflating them. |
| 11 | **Fit-and-proper vs. internal authz boundary (`F4_company_internal_authz`).** | Company's own `F4` atom scope. | **MET (confirmed distinct)** | SLC 4C (row 3) tests *whether a person is fit to hold an SMR&I role at all*; `F4` governs *what a role is permitted to do inside the system once appointed* (segregation of duties). Different tests, correctly kept as separate atoms — no overlap to resolve. |

## Summary: all four originally-named open items, closed

The atom's DISCOVER trail names four specific open items across its five `simplifications`
addenda. This register confirms all four are closed with real evidence (rows above), and
preserves the one genuine finding that DISCOVER explicitly could not resolve:

1. **Capacity Market/RO overlap with `F3_obligations_register`** — CLOSED, no overlap (row 9).
2. **Capital Target milestone-assessment mechanics** — CLOSED, customer-count-triggered at
   50k/200k, not date-based (row 6).
3. **SLC 4C detailed assessment criteria** — CLOSED, SMR&I scope confirmed broad (row 3).
4. **Relationship to B2 segment ROCE** — CLOSED, confirmed genuinely independent (row 10).
5. **£115-vs-£130 Capital Target figure** — **left open**, per R9/R10: this was never one of the
   four "named open items" the atom set out to close (it was *found*, not originally flagged),
   and it is preserved as an honest discrepancy rather than force-resolved (row 5).

## What this register is, and is not

- **Is:** a single, structured, cited, auditable readiness checklist — the L1 "consolidation"
  deliverable this atom's map entry calls for. Every row traces to a real Ofgem source or a real
  code read already performed in this atom's own DISCOVER history; nothing here is new research
  or a fabricated figure.
- **Is not:** a BUILD against the sim/company seam. No company code changed. The GAP rows (1, 2,
  3, 7, 8) remain real, unbuilt epoch-5 work — this register makes them individually trackable
  go/no-go items rather than one undifferentiated "licence readiness" blob, but building the
  actual measurement/evidence mechanisms behind each GAP row is out of scope for this pass and
  stays gated to epoch-5 BUILD (`loop_stage: idle`, `depends_on: [H3_production_readiness_nfr_evidence]`
  unchanged).
- **Is not** a resolution of the £115-vs-£130 discrepancy — resolving it needs the primary FRC
  decision PDF read directly, named here as the specific next DISCOVER step should this atom be
  reopened for further research.

## Cross-references

- `docs/market_research/ofgem_licence_readiness.md` — the original DISCOVER findings this register consolidates.
- `docs/design/maturity_map.yaml` — `F5_ofgem_licence_readiness` entry, five `simplifications` addenda (2026-07-12/13).
- `docs/design/PRODUCTION_READINESS_PARTS_BC.md` — row C6, the production-readiness framing of this same gate ("Blocker for real go-live... not a build item this epoch").
- `docs/market_research/company_treasury_risk.md:124`, `docs/market_research/energy_market_complexity_june2026.md:18` — the two independent sources behind the £115/£130 discrepancy (row 5).
- `company/compliance/domain_invariants.py` (`F3_obligations_register`) — confirmed no Capacity Market/RO overlap (row 9).
- `company/finance/segment_capital.py` (`B2_opex_cost_to_serve`) — confirmed independent from the Minimum Capital Requirement (row 10).
