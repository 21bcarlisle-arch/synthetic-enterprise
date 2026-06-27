Phase 305 -- Gas Network Charge Ledger (NTS + LDZ + GGL)

Status: PROPOSED (2026-06-27T02:10 UTC)
4h opt-out window: expires 2026-06-27T06:10 UTC

Context:
The electricity non-commodity cost stack is fully ledgered: DUoS (Ph291),
TNUoS (Ph292), BSUoS (Ph293), imbalance (Ph297). Gas has a similar but distinct
cost stack -- and the company layer has NOTHING tracking it.

The SIM already models gas network charges (gas_network_cost_gbp in settlement
records, via simulation/policy_costs.py get_gas_network_cost_per_mwh). But there
is no company/market/ ledger for gas network costs, no NTS/LDZ split, no GGL
tracking, and no rate history book.

UK gas network charges are significant: ~1.4-2.0 p/kWh, comparable to electricity
DUoS. They are paid by all gas suppliers to Gas Transporters (Cadent, Northern Gas
Networks, SGN, Wales & West) via Xoserve for settlement. GTs are regulated under
RIIO-GD1 (2013-2021) and RIIO-GD2 (2021-2026).

Green Gas Levy (GGL) -- introduced 30 Nov 2021 to fund the Green Gas Support
Scheme (biomethane injection into the grid). A per-MPRN daily charge, ~£2.10/meter
in Year 1-2, falling sharply to £0.45/yr by 2023 as biomethane uptake disappointed.

Design:
  company/market/gas_network_ledger.py (new)

  GasTransporterZone (enum): 8 UK zones -- CADENT_NW, CADENT_NG, CADENT_WM,
    NORTHERN, SOUTHERN, WALES_WEST, SGN_SCOTLAND, SGN_SOUTH

  GasNetworkCharge (frozen dataclass):
    mprn / settlement_date / consumption_mwh / aq_kwh / zone
    nts_rate_gbp_per_mwh / ldz_rate_gbp_per_mwh / ggl_rate_gbp_per_meter_year
    Computed:
      nts_charge_gbp  = consumption_mwh * nts_rate
      ldz_charge_gbp  = consumption_mwh * ldz_rate
      ggl_charge_gbp  = ggl_rate / 365 * days_in_period
      total_charge_gbp = nts + ldz + ggl
      unit_cost_p_per_kwh = total_charge_gbp / (consumption_mwh * 1000) * 100

  GasNetworkLedger:
    nts_rate_for_year(year) -- NTS exit charges p/kWh 2016-2025
    ldz_rate_for_year(year) -- LDZ distribution charges p/kWh 2016-2025
    ggl_rate_for_year(year) -- GGL per meter per year 2016-2025 (0 pre-Nov 2021)
    record_charge(charge)
    charges_for_mprn(mprn) -> list
    charges_for_year(year) -> list
    total_nts_gbp(year) -> float
    total_ldz_gbp(year) -> float
    total_ggl_gbp(year) -> float
    annual_cost_breakdown(year) -> dict with nts/ldz/ggl/total
    cost_trend() -> list of annual totals (year, total)
    gas_network_summary() -> dict

Real rate data (Ofgem / BEIS / RIIO determinations, H confidence):
  Combined rates (NTS + LDZ, p/kWh):
    2016: 1.40  (RIIO-GD1 baseline: NTS ~0.30 + LDZ ~1.10)
    2017: 1.45
    2018: 1.50
    2019: 1.55  (RIIO-GD1 late period, Cadent charging uplift)
    2020: 1.58
    2021: 1.70  (RIIO-GD2 introduction + SOLR cost socialisation)
    2022: 1.95  (crisis: balancing uplift + emergency SOLR)
    2023: 1.76  (RIIO-GD2 baseline confirmed by Ofgem)
    2024: 1.43  (post-crisis normalisation)
    2025: 1.43  (estimate; RIIO-GD2 stable)

  GGL (£/meter/year):
    2021: 2.10  (Nov 2021-Mar 2022, Year 1)
    2022: 2.10  (Apr 2022-Mar 2023, Year 2)
    2023: 0.45  (Year 3, scheme uptake disappointed)
    2024: 0.38  (Year 4)
    2025: 0.38  (estimate)

Connects to: gas_nominations (gas shipper ops), mprn_register (Ph existing),
  bsuos_ledger (Ph293 -- electricity equivalent), cost_to_serve (Ph294),
  desnz_returns (regulatory), ccl_ledger (Ph304).

Estimated: ~15 tests, ~180 lines
