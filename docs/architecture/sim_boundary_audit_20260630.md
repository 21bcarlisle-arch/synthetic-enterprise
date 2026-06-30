# SIM/Company Boundary Audit 2026-06-30

Requested by: Rich (docs/staging/Sim_boundary.md)
Status: DIAGNOSTIC COMPLETE

## TL;DR

company/market/ (79 modules): FULLY CLEAN -- zero direct sim/ imports.
Violations found: 3 semantic + 2 structural, all in saas/reporting/ (not market/).
forward_curve.py: NOT read by company code.
interface/contracts/: exists but EMPTY.
Epistemic verifier gap: does not scan saas/.

---

## 1. company/market/ -- All 79 Modules: OBSERVABLE

None of the 79 modules in company/market/ import from sim/ directly.

Categories confirmed clean:
  Settlement/BSC: bm_unit_log, imbalance_ledger, settlement_reconciler, bsc_settlement_*
  Network charges: bsuos_ledger, duos_ledger, tnuos_ledger, network_charge_ledger
  Metering/data: mpan_register, mpas_registry, hh_data_quality, metering_contracts
  Gas market: gas_nominations, gas_otc_book, gas_network_ledger, gas_storage, gas_interruption
  Flexibility/DSR: dsr_book, dsr_portfolio, flexibility_potential, flexible_asset
  Capacity/CfD: capacity_market, capacity_market_register, cfd_levy
  Trading/hedging: hedge_performance, hedging_schedule, day_ahead_book, intraday_book
  Market data feeds: price_feed, curve_monitor, rate_comparison, price_monitor
  Company demand models: ev_demand_forecast, load_forecast, seasonal_demand (all use public UK data)
  Registers/admin: 24 additional registers

Three hybrid candidates reviewed and confirmed OBSERVABLE:
  ev_demand_forecast.py -- uses DVLA EV registrations and smart meter patterns; no sim access
  load_forecast.py -- uses published UK average consumption by segment
  seasonal_demand.py -- uses seasonal indices from published UK data

price_feed.py: reads docs/market_data/price_feed.json only. No SIM modules accessed.

---

## 2. forward_curve.py -- Company Does NOT Read It

sim/forward_curve.py exists. Company code does not import it.

Company forward prices arrive via:
  Path A: company/market/price_feed.py -> docs/market_data/price_feed.json (file, not module)
  Path B: company/interfaces/sim_interface.py LiveSimInterface.get_forward_price()
           -> CompanyTariffEngine + public Elexon/NBP spot history

No company/ or market/ module imports sim.forward_curve. CONFIRMED CLEAN.

---

## 3. company/interfaces/sim_interface.py -- Seam Assessment

Architecturally correct. LiveSimInterface._load_price_records() uses sim/ as infrastructure
for PUBLIC market data (not sim internals):
  sim.cache_store.get_cached_prices() -- cached Elexon spot prices (public)
  sim.system_prices_history.get_system_prices_range() -- Elexon historical prices (public)
  sim.gas_prices_history.load_nbp_history() -- NBP/TTF prices (public)

Module docstring: "infrastructure convenience, not for SIM internals."
ASSESSMENT: BORDERLINE -- not a semantic violation. Public data via sim infrastructure.
Could be moved to company/ for architectural cleanliness, but no epistemic breach.

---

## 4. Violations -- saas/reporting/ (NOT caught by epistemic verifier)

The epistemic verifier scans company/ only. saas/ is not scanned.

SEMANTIC VIOLATIONS:

1. saas/reporting/segment_report.py:23
   from simulation.segments import SEGMENT_BY_ID, SEGMENTS
   SEVERITY: HIGH
   Company reporting uses SIM-internal customer segment definitions.
   A real supplier derives segments from observable CRM data, not the SIM synthetic model.

2. saas/reporting/annual_report.py:41
   from simulation.tou_periods import is_peak_period
   SEVERITY: MEDIUM
   ToU period classification is an observable market convention (Elexon settlement periods),
   but reads a SIM module. Should live in company/.

3. saas/reporting/annual_report.py:3905 (inside function, guarded by try/except)
   from sim.scenario.bimodal_generator import SCENARIOS
   SEVERITY: HIGH
   Report labels forward-run sections using SIM internal scenario parameters.
   The company cannot know the synthetic parameters used by the SIM.

STRUCTURAL ISSUES (orchestration, not epistemic):

4. saas/reporting/annual_report.py:40
   from simulation.run_phase4c_on_phase2b import main
   saas/ directly drives a SIM runner. Pipeline architecture concern.

5. saas/reporting/segment_report.py:450 (inside function)
   from simulation.run_segments import main as run_segments
   Same: saas/ directly calls the segment simulation runner.

---

## 5. interface/contracts/ -- EMPTY

interface/contracts/ has no contracts. README: "Empty for now -- Phase 0a."
The seam is enforced by convention + epistemic verifier (company/ only).

---

## 6. Event Ledger SOURCE Stamping -- NOT IMPLEMENTED

company/core/event_ledger.py exists (Phase DZ, 18 tests).
No SOURCE field (MARKET_OBSERVABLE / SIM_INTERNAL) exists on events.
Requested in this audit -- does not exist.

---

## 7. Epistemic Verifier Gap

tools/epistemic_verifier.py: COMPANY_PATHS = ["company/"] only.
The 3 semantic violations in saas/reporting/ are not caught.
saas/ must be added to scan scope.

---

## Recommendations (priority order)

1. Add saas/ to epistemic verifier scope
2. Fix violation 1 (HIGH): Remove simulation.segments from segment_report.py.
   Derive segments from observable CRM attributes (consumption tier, tenure, channel).
3. Fix violation 3 (HIGH): Remove sim.scenario.bimodal_generator from annual_report.py.
   Pass scenario metadata via run output JSON, not SIM internal module.
4. Fix violation 2 (MEDIUM): Move tou_periods.is_peak_period to company/.
5. Fix violations 4 and 5 (structural): Route sim runners via orchestration layer.
6. Event SOURCE stamping: Add source field to EventLedger entries.

---

## Summary counts

company/market/ (79 modules): ALL OBSERVABLE -- 0 violations, 0 sim imports
Hybrid modules needing split in market/: 0
saas/reporting/ semantic violations: 3 (in 2 files)
saas/reporting/ structural issues: 2 (in 2 files)
interface/contracts/: EMPTY
Epistemic verifier scope gap: saas/ not scanned
