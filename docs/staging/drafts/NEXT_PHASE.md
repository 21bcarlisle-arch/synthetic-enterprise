Phase 145 -- Prepayment Meter (PPM) Management

Status: PROPOSED (2026-06-26)

PPM is referenced by credit_scoring (HIGH_RISK -> PPM recommended) and meter_assets
(PPM as meter type), but there is no operational model. ~4M UK customers use PPM.
The 2022 crisis created a wave of self-disconnection when customers could not afford
to top up. Ofgem tightened PPM installation rules in 2023 as a direct consequence.

Design: company/billing/prepayment.py

PPMAccount(customer_id, meter_id, balance_gbp, emergency_credit_limit_gbp=5.0,
           debt_recovery_rate=0.5, is_vulnerable=False)
- balance_gbp: current credit on meter (can go negative = drawing emergency credit)
- emergency_credit_limit_gbp: 5 GBP standard, 10 GBP for vulnerable customers
- debt_recovery_rate: fraction of top-up withheld for debt (default 0.50)
- debt_gbp: outstanding debt being recovered via top-ups

PPMBook:
- register(account) -> record in portfolio
- top_up(account_id, amount_gbp, date) -> if debt: withhold rate*amount for debt,
  remainder to balance. If debt-free: full amount to balance.
- consume_daily(account_id, kwh, rate_gbp_per_kwh, sc_gbp_per_day, date) -> deduct
  from balance; when balance hits zero, draw emergency credit (up to limit)
- is_friendly_hours(dt) -> bool: Ofgem rule no disconnect 10pm-6am or weekends
- is_self_disconnected(account_id, dt) -> bool: balance < -emergency_credit_limit
  AND NOT friendly_hours(dt) -- exhausted emergency credit, customer cut off
- portfolio_summary() -> total_accounts, self_disconnected, avg_balance_gbp,
  total_debt_gbp, pct_in_emergency_credit

2022 dynamic: NBP gas +10x, SSP electricity +3x -> daily deduction rises sharply ->
emergency credit exhausted in days not weeks -> self-disconnection surge matches Ofgem data.

Vulnerable customers: emergency_credit_limit 10 GBP (vs 5), debt_recovery_rate capped 0.25.

~11 tests. Closes the gap between credit_scoring PPM recommendation and actual PPM operations.
