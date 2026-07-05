## Phase QN COMPLETE -- Customer Portal Per-Fuel Depth
Last updated: 2026-07-05T03:25:46Z

**Status:** COMPLETE. 15,436 tests passed (fast suite). Epistemic: PASS.

**Phase QN -- Per-Fuel Legs (PRIORITIES.md P1, WEEKEND_ACCELERATION.md Q5):**
- tools/generate_shadow_html.py: removed the `if cid.endswith("g"): continue` skip that was
  dropping every gas leg of a dual-fuel account from the Customers tab
- Both fuel legs now shown as separate accounts; Combined Roll-Up table added as an explicit
  optional secondary view (dual-fuel customers only)
- _per_fuel_case_study(): real per-leg invoice/arrears/failed-payment history from billing_ledger.json

**KEY FINDING:**
- C_IC3's electricity leg is billed/paid exactly (0 failed payments, 0 arrears)
- Its gas leg (C_IC3g) carries 1 failed payment and a live -£89,641 arrears case
- A combined roll-up would have netted this into one number and hidden which fuel is causing the friction

**Remaining scope (PRIORITIES.md P1):** design-system unification across all four shadow sections + customer portal.

**Prior milestone:** Phase QM (Retention as Deferral, H1 vs H2) -- docs/claude/phase-history.md.


**Latest simulation results (2016–2025)** — auto-processed (499s / 8 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 14 offers, 14/14 retained | 6 no-offer churns | 6 total churned accounts