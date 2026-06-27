Phase 306 -- Gas Shipper Imbalance Ledger

Status: PROPOSED (2026-06-27T02:05 UTC)
4h opt-out window: expires 2026-06-27T06:05 UTC

Context:
Phase 297 built the electricity Imbalance Ledger -- electricity cashout when
metered != contracted (SBP/SSP). Gas has a parallel mechanism: UK gas shippers
must balance their portfolios against their nominations or face Within-Day
imbalance charges settled at the NBP (National Balancing Point) cash price.

During 2021-22, NBP spiked from ~40p/therm to >400p/therm (10x). Shippers
caught short on gas faced ruinous balancing costs -- this killed several suppliers
(Igloo, People's Energy, etc). The company has no tracking for this exposure.

Gas balancing works differently from electricity:
- Shipper submits nominations (gas_nominations.py already models this)
- Mismatch between nominated and actual offtake = imbalance
- Long: surplus sold into system at System Sell Price (SSP)
- Short: deficit bought from system at System Buy Price (SBP)
- Daily linepack tolerance: +/-1% before imbalance charges apply
- NBP Day-Ahead is the reference for SBP/SSP

Design:
  company/market/gas_imbalance_ledger.py (new)

  GasImbalanceDirection (enum): LONG / SHORT / FLAT

  GasImbalanceRecord (frozen dataclass):
    mprn / trade_date / nominated_mwh / metered_mwh
    sbp_gbp_per_mwh / ssp_gbp_per_mwh
    Computed:
      imbalance_mwh = metered_mwh - nominated_mwh (+ = long, - = short)
      direction (LONG/SHORT/FLAT; FLAT if abs(imbalance) < tolerance 1%)
      imbalance_charge_gbp:
        LONG: sold at SSP (positive cash in)
        SHORT: bought at SBP (negative, cash out)
        FLAT: 0.0
      is_crisis_price: SBP > 100 GBP/MWh (10p/therm ~ crisis threshold)
      cashout_spread: sbp - ssp

  GasImbalanceLedger:
    nbp_sbp_for_month(year, month) -- approximate SBP GBP/MWh 2016-2025
    nbp_ssp_for_month(year, month) -- approximate SSP GBP/MWh (SSP < SBP)
    record(record: GasImbalanceRecord)
    records_for_date(date) -> list
    records_for_mprn(mprn) -> list
    net_imbalance_cost_gbp(year) -> float
    crisis_periods() -> list of records where is_crisis_price
    short_periods() -> list of SHORT records
    mean_cashout_spread(year) -> float
    gas_imbalance_summary() -> dict

Real NBP price data (approximate annual averages GBP/MWh):
  2016: 12.0  2017: 16.0  2018: 22.0  2019: 15.0  2020: 9.0
  2021: 45.0  2022: 180.0  2023: 65.0  2024: 35.0  2025: 30.0

SBP/SSP relationship: SBP = NBP + 5%, SSP = NBP - 5% (cash-out spread widens
in crisis periods). 2022: SBP occasionally > 500 GBP/MWh (is_crisis_price threshold).

Connects to: gas_nominations (nominations vs metered), gas_network_ledger (Ph305),
  imbalance_ledger (Ph297 -- electricity parallel), cost_to_serve (Ph294).

Estimated: ~15 tests, ~130 lines
