# Phase 43: Company Trading Desk — Forward Position Lifecycle

## Context

Phase 41-prep (forward curve reform) and Phase 42 (gas seasonal calibration) completed
the "wholesale markets and forward products" foundation Rich specified before I&C trading.

The next natural step is moving from synthetic forward pricing to a genuine company trading
desk that makes real hedging decisions — the last major SIM/company boundary to cross.

## What's wrong now

The hedge fraction (`hedge_fraction`) is set by the SIM's risk committee. In reality:
- A UK supplier's trading desk *decides* what volume to hedge and when
- The hedge is an OTC forward contract with a notional, an agreed price, and a delivery period
- That agreed price is locked at deal signing (not at delivery)
- At delivery, the company settles the difference between the locked forward and actual spot

Currently the company and SIM share the same hedge fraction — the epistemic boundary
that should separate them doesn't exist here.

## What Phase 43a would build

**Company Trading Desk (`company/trading/forward_book.py`)**
- `ForwardContract(notional_mwh, agreed_price_gbp_per_mwh, delivery_start, delivery_end)`
- `TradingBook.add_hedge(contract)` — opens a position when a new supply term is signed
- `TradingBook.settle(delivery_date, spot_price)` — daily mark-to-market; on delivery,
  realised gain/loss = (spot - agreed_price) × delivered_volume

**Company decides hedge fraction**
- On new supply term: trading desk calls `decide_hedge_fraction(customer, term)` using
  observable data only (portfolio exposure, recent VaR, forward curve state)
- Initial implementation: simple rule (85% hedge floor, matching current mandate) so the
  first run is behaviorally identical to today — but the decision lives in the company layer

**SIM sees the company's actual hedging**
- Instead of reading `hedge_fraction` from the SIM agent, `run_phase2b.py` queries the
  company's trading book for the hedge fraction that was actually applied
- Divergence between company's hedging decision and SIM's optimal is now measurable

## Scope

Phase 43a only:
1. `company/trading/forward_book.py` — `ForwardContract` + `TradingBook`
2. `company/trading/hedge_decision.py` — `decide_hedge_fraction()` (simple rule-based first)
3. `simulation/run_phase2b.py` — company provides hedge fraction instead of SIM agent
4. Tests: book lifecycle (add hedge, settle, P&L), hedge fraction rule, SIM reads company decision

Phase 43b (later): Adaptive trading desk — VaR-constrained hedge optimisation, bid-ask spread
simulation, liquidity limits, real trading P&L in annual report.

## Why this matters

- SIM/company full operational independence milestone
- Trading desk P&L becomes a new reportable item (hedge gain/loss separate from supply margin)
- Crisis 2021-2022: company trading desk would have made specific decisions; we can study them

## Fidelity delta

"The company now runs a trading book. Hedge decisions are made by the company layer, not the SIM. Trading P&L is separate from supply margin. The 2021 crisis will show the company's hedging decisions and their impact."

## Estimated cost

~8-12 new tests. Low risk — initialise with the same 85% floor rule, so run output is
numerically close to current (validates the architecture change before adding decision logic).

## Ready to proceed?

Will stage as instruction after 4 hours unless Rich redirects.
