## BILL_CORRECTNESS_ADDENDUM CLOSED IN FULL (Defects 1-4)
Last updated: 2026-07-12T12:45:39Z

**Status:** COMPLETE. 834 tools/ tests pass, 16,026+ full suite, epistemic PASS.

**Defect 1** (commit 32ab2a4c): C6's "Household / Residential" mislabel root-caused as a pure
portal render-layer bug -- its 20% VAT and ~28MWh/yr were already correct for its true SME segment.
Fixed with an explicit per-segment badge/label lookup. Sweeping for the same class found a second
real bug: saas/non_commodity.py's VAT_RATE was missing an "I&C" key, silently undercharging I&C
accounts 5% domestic VAT instead of the legally-required 20%.

**Defect 2** (commit 6f176f87): every bill now states billing period, opening/closing meter reads
with A(ctual)/E(stimated) type (Phase 3's meter_read_log, previously computed but never surfaced),
meter serial, and MPAN/MPRN. Running cumulative register value chains correctly across each
account's bill history.

**Defect 3** (commit e93a4b96): consumption restructured as a register/period list (ToU-ready
schema -- single "Anytime" register today, array shape supports N). ToU itself not built, per the
addendum's own instruction.

**Defect 4** (commit 10d13544): root-caused the "£13k billed vs £1.5k gross" observation as a
definitional mismatch, not a bug -- annual_pnl's gross_gbp is the SIM's internal commodity trading
margin, not a bill total. Added a permanent consistency-gate test sweeping every real
customer-year (billed total must never be less than gross margin -- holds cleanly across all 143
live pairs) plus an inline portal note.

**Method rule 0c added to CLAUDE.md** per the addendum's own instruction: any customer-facing
artefact's definition-of-done now includes rendering one real instance and inspecting it against
domain law by eye, alongside automated invariants.

Real pipeline regenerated and verified directly (commit 8494b61b): C6 (SME) now opens correctly
with all new fields at its real 2,346.8 kWh/month (matches the addendum's own cited figure); C1
(residential) shows the same fields at a plausible ~440 kWh/month.

Defect 5 (I&C billing model) registers to backlog alongside WALLED_INTERFACES per its own "do not
build now" instruction. Front of queue next: DOMAIN_SENSE_AND_COMPLIANCE.md (P1 compliance
programme), recorded in the open agenda for the next session/supervisor cycle to pick up.

**Prior:** THE SUPERVISOR architecture rebuild (doorbell failure #4, R3) -- see
docs/retrospectives/2026-07-09-doorbell-failure-4-supervisor.md. Wake-doorbell strike 3 fix -- see
docs/retrospectives/2026-07-08-wake-doorbell-third-strike.md.

**Latest simulation results (2016–2025)** — auto-processed (489s / 8 min):
- Net margin: £1,524,057.56 | Gross: £6,477,859.06 | Capital: £51,377
- Treasury: £2,466,636 → £3,902,095 | 38 committee interventions | 1588 bills issued
- Enterprise value: £7,730,031.11 | Net after CTS: £6,407,919
- Retention: 12 offers, 12/12 retained | 5 no-offer churns | 5 total churned accounts