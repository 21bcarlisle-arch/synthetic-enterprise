# W3 — Industry Systems: lane charter

**Dial reached 2 (SPIKE_WEEKEND charter flood, 2026-07-11)** — this lane's atoms sit below the
map's own standard "3+" charter threshold, but are named explicitly in the director-decided
SPIKE_WEEKEND directive ("DISCOVER/FRAME charter flood: every lane at dial≥2 lacking one").

## Mission

The company must operate inside the real institutional machinery of the GB energy industry, not
a simplified stand-in for it: a real regulatory price ceiling that genuinely binds what a
supplier can charge, and a real multi-stage settlement process that restates historical figures
for months after the fact. Both are real_world_twins already named in
`docs/design/maturity_map.yaml`: "the real Ofgem default tariff cap has bound SVT pricing since
2019" (W3_1) and "Elexon's SBP/SSP settlement run timetable" (W3_2).

## Sub-capability tree

- **W3_1_price_cap_binding** — the Ofgem Default Tariff Cap as a genuine ceiling on deemed/SVT
  billing, not just a reference lookup used elsewhere for sanity-checking.
- **W3_2_settlement_timetable** — the real Elexon multi-run settlement process (Initial → Interim
  Informative → Final) as an explicit world mechanism, feeding the same bitemporal
  reveal-over-time spine as lane W1 (`company/interfaces/bitemporal_event_log.py`) and lane D
  (`D2_three_clocks`, `docs/design/charters/D_billing_metering.md`) — a third face of the same
  architecture, not a separate one.

## What L2/L3/L4 mean in this lane's terms

### W3_1_price_cap_binding (AT TARGET, level 2/2, `loop_stage: harden`)

Built 2026-07-11 (SPIKE_WEEKEND item 1, MARGIN_REALISM Step 5). The real gap: `run_deemed_term()`
(`simulation/hedged_settlement.py`) computed `spot_price * (1 + deemed_premium)` with zero
reference to the cap — completely unbound, unlike the existing fixed-tariff clamp (Phase 47a,
`simulation/run_phase2b.py`). Fixed: `billed_rate = min(spot * (1 + premium), cap)` for resi
customers from 2019 onward, matching the real UK deemed/SVT mechanism that squeezed suppliers
buying at spot while capped on the sell side through the 2021-22 crisis — margin can now
legitimately go negative on a capped settlement period.

**"Harden" here means:** resolving one named architectural oddity, not adding new mechanism.
`simulation/hedged_settlement.py` now imports `company.pricing.ofgem_price_cap` — a SIM module
reading a COMPANY module, backwards from the SIM being the "real world" the company is supposed
to discover, not the reverse. This is NOT a point-in-time-blindfold violation (the cap figures
are static, real, historical — not derived from anything a real company couldn't independently
know), and it extends a pre-existing precedent (`run_phase2b.py` already did this for fixed
tariffs) rather than introducing a new pattern. Registered as portability/layering debt to
resolve if this module is ever refactored, not urgent on its own.

### W3_2_settlement_timetable (genuinely unbuilt, level 0 → 2)

- **L1 (current):** no settlement-timetable concept exists at all — every settlement figure in
  this codebase is treated as instantaneous and final, with no notion that a real Elexon
  settlement run restates it later.
- **L2:** a real settlement-run timetable object exists — Initial, Interim Informative (II), and
  Final (SF) runs at their real T+X delays (see Named best-practice references below) — proven
  correct in isolation, populating the bitemporal event log's `transaction_time` axis
  (`company/interfaces/bitemporal_event_log.py::BitemporalRecord`, already built) for at least
  one real fact type (candidate: settled consumption, which genuinely gets revised between runs).
- **L3:** at least one company-side decision (a margin or revenue figure) demonstrably uses the
  correct settlement-run-as-of-a-given-decision-date view via `PointInTimeView`
  (`company/interfaces/point_in_time_view.py`), not a naive frozen/final figure.
- **L4:** the full real Elexon settlement calendar is modelled, and the company can be shown
  making a genuinely different — and provably correct — decision when a later settlement run
  restates an earlier figure, exactly the reveal-over-time spine's own L4 target
  (`docs/design/charters/W1_market_weather.md`).

## Named best-practice references

- **Ofgem Default Tariff Cap, real legislative/regulatory history** — the Domestic Gas and
  Electricity (Tariff Cap) Act came into force 19 July 2018; Ofgem's final decision on cap design
  was published 6 November 2018; the cap itself took effect 1 January 2019 at £1,137/year for a
  typical dual-fuel direct-debit customer, reviewed twice yearly thereafter. Sources: Ofgem,
  "Default tariff cap: decision – overview"
  (https://www.ofgem.gov.uk/decision/default-tariff-cap-decision-overview); Ofgem, "Energy price
  cap (default tariff) levels"
  (https://www.ofgem.gov.uk/energy-regulation/domestic-and-non-domestic/energy-pricing-rules/energy-price-cap/energy-price-cap-default-tariff-levels);
  House of Commons Library, "Energy bills and the price cap"
  (https://commonslibrary.parliament.uk/research-briefings/cbp-8081/).
- **Elexon's real multi-run settlement timetable** — the legacy timetable runs an Interim
  Information run at approximately 5 working days (no payment date attached), an Initial
  Settlement Run at approximately 16 working days (payment at ~20–21 working days), and a Final
  Reconciliation Settlement Run at 14 months. Elexon has a planned transition from this legacy
  14-month timetable to a new 4-month timetable, cutover 2 July 2027 (Market-wide Half-Hourly
  Settlement programme). Source: Elexon/MHHS Programme, "BSCP01: Overview of Trading
  Arrangements" and the MHHS transition design document
  (https://www.elexon.co.uk/csd/bscp01-overview-of-trading-arrangements/,
  https://www.mhhsprogramme.co.uk/api/documentlibrary/Design%20Documents/MHHHS-DEL1590_MHHSP_Transition_to_new_Settlement_%20Timetable%20v2.3%20Approved.pdf).
  Honest limitation: the exact modern-day run-count/naming (this project's own CLAUDE.md
  shorthand of "Initial/II/IF/SF") was not independently re-verified run-by-run against a single
  canonical Elexon source in this pass beyond the timings above — a closer read of BSCP01 itself
  is the natural follow-up before building L2.

## Lane roadmap

1. **DONE (W3_1, this session):** Ofgem cap now binds deemed/SVT billing for real, 6 new tests,
   `docs/design/maturity_map.yaml` level 1 → 2 (AT TARGET).
2. **Next (not started, blocked):** W3_2's actual build — a real settlement-run timetable object
   — depends on `D2_three_clocks` (Epoch-2 core) and is explicitly blocked pending the advisor's
   epoch-sequencing framing, per the same standing instruction covering W1/D2/B1/E2/G2. Do not
   start the build before that framing names its turn.
3. **When unblocked:** populate the bitemporal event log with one real fact type's real
   settlement-run restatement timing (candidate: settled consumption) as the concrete first
   target, per L2 above.

## Simplifications register

- W3_1's `simulation/hedged_settlement.py` → `company/pricing/ofgem_price_cap.py` import
  direction is a real, named architectural oddity (see "harden" note above) — registered, not
  silently left unexplained, and not urgent to fix on its own.
- W3_2 has zero code today — `evidence: []` in the maturity map is accurate, not an oversight.
- No independent re-verification of the exact modern Elexon run-timetable beyond the timings
  cited above — BSCP01 itself is the natural next source to read in full before any L2 build.
