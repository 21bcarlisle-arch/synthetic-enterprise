Phase 256 -- Day-ahead electricity trading book (N2EX/EPEX SPOT UK)

Status: PROPOSED (2026-06-26)

The day-ahead auction is the primary UK electricity market. Suppliers buy the
majority of their portfolio energy here (~60-70%) in a once-daily clearing at
~11:00-12:00 CET for the following day 48 settlement periods.

Currently the company has:
- Forward book (weeks/months ahead)          -- company/trading/forward_book.py
- Intraday continuous (Phase 249)            -- company/market/intraday_book.py
- Balancing mechanism log                    -- company/market/bm_unit_log.py

The day-ahead auction is the MISSING MIDDLE of the trading timeline:
  forwards -> [day-ahead] -> intraday -> BM

Design: company/market/day_ahead_book.py

DayAheadDirection enum: BUY / SELL

DayAheadAuction(frozen dataclass):
  auction_id, delivery_date, direction,
  volume_mwh, bid_price_gbp_per_mwh, cleared_price_gbp_per_mwh,
  auctioned_at (datetime, day before delivery ~11:00 CET)
  Properties:
    cost_gbp: volume * cleared_price (positive=cost/buy, negative=revenue/sell)
    vs_forward_spread_gbp_per_mwh: cleared - bid (excess over forward hedge price)
    is_crisis_price: cleared_price > 300 (DA crisis threshold)

DayAheadBook:
  submit_auction(auction_id, delivery_date, direction, volume_mwh,
                 bid_price, cleared_price, auctioned_at) -> DayAheadAuction
  auctions_for_month(year, month) -> List[DayAheadAuction]
  net_position_mwh(delivery_date) -> float  # BUY positive, SELL negative
  total_volume_mwh(year=None) -> float
  total_cost_gbp(year=None) -> float
  average_clearing_price(year=None) -> Optional[float]
  crisis_auctions(threshold=300.0) -> List[DayAheadAuction]
  monthly_summary(year, month) -> dict
  day_ahead_summary() -> dict

2022 crisis: DA cleared 400-600/MWh at winter peaks vs 45-55/MWh historical.

~11 tests. Closes the trading timeline gap between forwards and intraday.
