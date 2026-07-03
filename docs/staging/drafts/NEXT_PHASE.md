# NEXT PHASE PROPOSAL: Phase PU -- Shadow Live Operation (P4 MVP)

## Gap addressed
P4 Shadow Live Operation -- the SIM currently operates only in retrodiction mode
(2016-2025 historical settlement data). It cannot answer: what would the company do
today? A real UK supplier makes active daily decisions -- price quotes, hedge reviews,
retention offers -- against current market conditions. Phase PU wires the company layer
to today's data and produces a daily decision log.

## What real fidelity is gained
A real UK energy supply MD can say: "Our risk committee met today. Wholesale is at
GBP 82/MWh. We are 65% hedged for Q1 2027. Three I&C customers are in their renewal
window. Our proposed tariff for a 2 GWh I&C account is 9.2p/kWh." Phase PU means
the SIM's company layer can make exactly that statement -- against real market data --
and log it with a timestamp. The board section becomes a live daily operations log,
not a retrodiction of what happened.

## What this phase builds

### Part A: Company state snapshot at 2025-12-31
tools/project_portfolio_to_2026.py:
  Read run_output_latest.json -> extract portfolio as of 2025-12-31:
  - Active customers (cid / segment / eac / current_rate / term_expiry)
  - Treasury and capital position
  - Hedging ledger (hedge fractions per customer)
  Write site/state/live_portfolio.json (point-in-time state for live engine)

### Part B: Live market data connector
tools/live_market.py:
  fetch_day_ahead(date=today) -> {elec_gbp_mwh: float, gas_gbp_therm: float}
    Source: Elexon BMRS Derived Data / N2EX day-ahead (existing elexon_client.py wrappers)
    Fallback: rolling 30-day average from docs/market_data/price_feed.json
  build_live_forward_curve(date=today) -> ForwardCurve
    Use existing sim/forward_curve machinery with today as the anchor date

### Part C: Daily decision engine
tools/run_live_decisions.py:
  Loads live_portfolio.json + today's ForwardCurve
  For each customer:
    - Is term expiring within 60 days? -> compute renewal price + churn estimate
    - churn_estimate > retention threshold? -> flag for retention offer
  Risk committee check:
    - Compute VaR at current hedge fractions vs capital
    - Flag if hedge recommendation changes (increase/hold/reduce)
  Pricing desk:
    - compute_tariff(segment, eac, forward_curve_today) for new acquisition
  Write site/state/live_decisions_YYYYMMDD.json:
    {date, spot_elec_gbp_mwh, spot_gas_gbp_therm, hedge_recommendation,
     renewal_flags: [{cid, expiry, proposed_rate, churn_estimate, offer_flag}],
     acquisition_prices: {resi_dual_fuel: ..., sme_elec: ..., ic_elec: ...}}
  Also write site/state/live_decisions_latest.json (always current)

### Part D: Observable output
site/shadow/live/index.html: no-JS daily operations log page
  Today's spot price | Hedge status | Renewal queue | Acquisition price ladder
  Listed in PROJECT_STATE.txt Key Files.

### Part E: Scheduled runner
background/live_runner.py: called daily from background dispatcher
  Catches today's market data, runs decision engine, writes + commits JSON

## Architecture decision (one-way-door: Rich must approve)
The SIM portfolio is anchored at 2025-12-31. From 2026 onwards, customers are
projected (terms roll at renewal, no new customers -- existing portfolio only).
This means the live operation runs against a FROZEN population evolving forward.
Alternative: start a fresh 2026 portfolio (new customers). Recommend: frozen first,
then optionally grow. The frozen approach is reversible; the growth approach is not.

## Epistemic check
Live market data (Elexon BMRS, N2EX day-ahead) is public. Company decisions based
on observable market data. Portfolio state is company-observable. PASS.

## Test targets (~18 tests)
1. project_portfolio_to_2026 reads run_output and extracts active customers
2. project_portfolio_to_2026 includes cid / segment / eac / current_rate / term_expiry
3. fetch_day_ahead returns float pair (elec, gas) from price_feed fallback
4. fetch_day_ahead raises on network error gracefully (fallback kicks in)
5. build_live_forward_curve uses today as anchor date
6. run_live_decisions loads portfolio and produces renewal_flags list
7. renewal_flags includes customers within 60-day window
8. renewal_flags excludes customers outside window
9. churn_estimate above threshold sets offer_flag=True
10. churn_estimate below threshold sets offer_flag=False
11. hedge_recommendation HOLD when VaR within policy limits
12. hedge_recommendation INCREASE when naked position exceeds limit
13. acquisition_prices returns price per segment
14. live_decisions JSON written with today's date key
15. live_decisions_latest.json always updated
16. shadow live/index.html renders renewal queue
17. shadow live/index.html renders acquisition prices
18. live_runner.py can be called without error on stub data

## Expected key finding
Company layer makes its first forward-looking daily decision: three I&C customers
entering renewal window in Q1 2026; wholesale forward at ~GBP 82/MWh; acquisition
price for 2 GWh I&C at 9.2p/kWh. Hedge recommendation HOLD. Board sees: first live
daily operations log, timestamped, reproducible. SIM is no longer retrodiction only.
