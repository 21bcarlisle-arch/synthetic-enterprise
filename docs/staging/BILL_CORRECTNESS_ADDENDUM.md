# BILL_CORRECTNESS_ADDENDUM — director-found defects, binds Phase 4 (P1)

**Staged:** 2026-07-08 ~21:50 BST. Director inspected a live portal bill
(C6, poesys.net/customers) and found domain-law violations. These bind Phase 4.

## Defect 1 (P1, fix first): segment/VAT/label incoherence
C6 renders as "Household / Residential" on the portal but is SME in
customer_sample.json; its bill charges VAT at 20% (£191 on £956) with 34.37p/kWh
and 2,346.8 kWh/MONTH (~28 MWh/yr). Root-cause the mislabel (data or render
layer), then add DOMAIN-INVARIANT tests so this class can never recur:
- VAT: domestic = 5%; business = 20% (+CCL where applicable). Assert per bill.
- Segment coherence: residential consumption within plausible annual bands
  (elec ~1.8-7 MWh, gas ~5-20 MWh); label, VAT rate, and tariff family must
  agree. Any bill violating an invariant fails the suite.
Sweep ALL customers for the same incoherence, not just C6.

## Defect 2: bills lack period + reads
Every bill must state: billing period start/end; opening & closing reads with
read type (A=actual, E=estimated — Phase 3's estimation physics should surface
here); meter serial + MPAN/MPRN; per-fuel breakdown. This is core Phase 4 scope
— confirming it explicitly since current bills omit all of it.

## Defect 3: bill lines must be register/period-structured (ToU-ready)
Usage as one flat line cannot carry ToU. Structure bill lines as
consumption-by-register/period (single-register today = one line, but the
SCHEMA supports N registers), so ToU tariffs bill correctly when they arrive on
the roadmap. Do not build ToU now — build the line structure that permits it.

## Defect 4: cross-surface reconciliation broken
Portal 2024 bills for C6 total ~£13k; customer_sample.json annual_pnl records
~£1.5k gross for 2024. Establish which is authoritative (ledger), define what
annual_pnl gross means, reconcile, and add bills-vs-ledger-vs-sample to the
consistency gate (page-level reconciliation law).

## Defect 5 (register, do not build now): I&C billing model
I&C should ultimately bill on HH data with capacity/DUoS-style components, not
domestic-shaped bills at scale. Register in PRIORITIES.md for director re-rank
alongside WALLED_INTERFACES (natural pairing: HH settlement flows arrive
through the wall).

## Method fix (permanent, CLAUDE.md)
Add to phase definition-of-done for any customer-facing artefact: render one
real instance and inspect it against domain law (the "read one bill as a human"
check), alongside the automated invariants above.

## DoD
Defect 1 root-caused + swept + invariant tests green; 2-4 delivered within
Phase 4; 5 registered; method rule added. Evidence: a corrected C6 (or
re-segmented equivalent) bill AND one true residential bill, both opening
correctly on the deployed portal. One NTFY.
