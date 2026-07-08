# DOMAIN_SENSE_AND_COMPLIANCE — two-sided, risk-based error prevention (P1 programme)

**Staged:** 2026-07-08 ~22:30 BST by advisor; director-approved with explicit
design principles (below). **Tier:** 2. Sequence: does not interrupt Phase 4 /
BILL_CORRECTNESS_ADDENDUM — those complete first; harness-side pieces are
background-lane eligible immediately. You propose the phase decomposition.

## Director's principles (binding)
1. **Bills must be accurate, above all.** Bill accuracy is the Tier-1 control:
   100% of bills pass preventive validation before issue; failures are HELD to
   an exception queue, never sent. Zero tolerance, continuous, not sampled.
2. **Multi-level, risk-based compliance.** Build an obligations register
   covering every applicable rule and law (Ofgem SLCs incl. billing accuracy &
   back-billing 12-month rule, GSOP auto-compensation, PSR/vulnerability duties,
   VAT law, settlement/industry-code duties, marketing/switching rules). Each
   obligation is RISK-ASSESSED: impact x likelihood, where impact ranks
   **physical harm to people worst, then financial harm to customers**, then
   licence/regulatory, then company-financial, then reputational.
3. **Depth, frequency, and visibility follow risk.** Risk tier determines:
   control type (preventive gate vs detective sampling), testing depth (100%
   vs statistical sample), testing frequency (continuous / per-bill-run /
   daily / phase-close / periodic), and reporting visibility (Tier-1 breaches
   = immediate NTFY to director + held artefact; lower tiers roll up into a
   periodic compliance report surfaced on a business page). Design the tiering;
   record the rationale per obligation in the register.

## Company-side organs (inside the wall — this is fidelity, not QA)
- **Pre-bill validation + exception queue** in the billing pipeline. Held bills
  are SIM EVENTS: billing delayed, customers chase, GSOP/compensation physics
  apply — Phase 3's unhappy paths compound naturally.
- **Compliance function**: owns the obligations register as data; monitors
  controls; produces the risk-tiered compliance report.
- **Internal audit**: independent sampling agent (institutionalise the local-
  Qwen skeptic inside the company) — samples outputs on a risk-based cycle,
  findings feed the exception/remediation flow.

## Harness-side (outside the wall — the harness plays Ofgem/external auditor)
- **Anchored domain-invariants library**: UK domain law as data — VAT by
  segment, TDCV consumption bands, YEAR-SPECIFIC plausible unit-rate/standing-
  charge ranges (sim spans 2016-26), bill-component shares — sourced by the
  discovery agent, registered in ASSUMPTIONS.md with provenance.
- **Sanity daemon** (background lane): continuously samples rendered artefacts
  and data surfaces against the library.
- **Statistical population tests**: the population must look real (consumption
  distributions vs TDCV, revenue/customer vs cap-implied bands, estimated-read
  rates vs industry norms).
- **Qwen skeptic pass at phase close**: grumpy-UK-energy-auditor prompt reads
  randomly sampled rendered artefacts; flags absurdities.

## Permanent rule R10 (CLAUDE.md)
An absurdity-class defect may NOT be closed with an instance fix. Closure
requires extending the invariant library / obligations register so the entire
class fails automatically thereafter. (Context: C6 SME-as-Household 20%-VAT
bill; 4.3x sigma; missing non-commodity revenue — same class, three instances,
never before fixed as a class.)

## DoD
Obligations register live with risk tiers + rationale; Tier-1 pre-bill gate
enforcing on every bill run with exception queue visible as an operational
surface; invariants library seeded (>=20 anchored invariants) with sanity
daemon running in background lane; R10 in CLAUDE.md; first risk-tiered
compliance report published to a business page. Evidence per 0b. One NTFY per
phase, decomposition proposed in your first.
