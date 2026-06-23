# Phase 43b: Adaptive Trading Desk — VaR-Constrained Hedge Optimisation

## Context

Phase 43a built the trading book infrastructure (ForwardContract + TradingBook + hedge_pnl decomposition).
The hedge fraction is still set by the same simple rule from company/risk/hedge_policy.py
(85% floor + ±10% evolution). Phase 43b makes the trading desk genuinely adaptive.

## What Phase 43b would build

**VaR-constrained hedge optimisation**
- At each term signing, the trading desk computes the hedge fraction that maximises expected margin
  subject to a VaR constraint (e.g. 95% VaR ≤ 15% of term revenue)
- Uses only company-observable inputs: portfolio exposure, term duration, recent price volatility,
  forward price (from company tariff engine), hedge cost (bid-ask spread simulation)
- Implementation: `company/trading/hedge_decision.py` — `decide_hedge_fraction(term, portfolio_state)`

**Bid-ask spread simulation**
- Real OTC forward markets have a bid-ask spread: the company buys the hedge at ask (above mid)
- `company/trading/forward_book.py`: `ForwardContract.agreed_price` = company_fwd + bid_ask_cost
- Spread calibrated to UK N2EX market microstructure: ~0.5-1.5 £/MWh for 1-year contracts

**Trading P&L in annual report**
- `saas/reporting/annual_report.py`: `_section_trading_pnl(data)` — year-by-year hedge gain/loss
  vs supply margin. Shows what the company's hedging decisions contributed separate from supply.
- Crisis 2021-22: trading desk would have locked in forward prices before the spike — this becomes
  a visible, quantified decision in the annual report.

**Liquidity limits**
- Very large I&C customers (>2 GWh/year) may not be fully hedgeable at competitive prices
- `TradingBook`: `max_hedge_mwh_per_period` constraint — excess volume unhedged or passed through

## Scope

Phase 43b:
1. `company/trading/hedge_decision.py` — `decide_hedge_fraction()` with VaR constraint
2. `company/trading/forward_book.py` — bid-ask spread cost on ForwardContract
3. `simulation/run_phase2b.py` — replace static `hf` with `decide_hedge_fraction()` output
4. `saas/reporting/annual_report.py` — `_section_trading_pnl()` 
5. Tests: VaR constraint fires at stress scenarios, bid-ask adds cost, trading P&L section

## Why this matters

- Hedge fraction becomes a genuine company decision with observable P&L consequences
- Trading desk shows up in the annual report as a separate P&L line
- Crisis visibility: can answer "did the company hedge enough before 2021?"
- Fidelity delta: "The company now optimises its hedging subject to a VaR constraint.
  Trading P&L is separated from supply margin in the annual report."

## Estimated cost

~10-15 new tests. Medium complexity — VaR constraint is straightforward with observable volatility.
First run with bid-ask costs will show a small reduction in net margin (~£0.5-1.5/MWh on hedged volume).

## Will proceed in 4 hours unless Rich redirects.
