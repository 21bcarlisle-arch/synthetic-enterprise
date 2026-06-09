"""Risk committee trigger and context packager — the Context Handshake infrastructure.

Phase 1e identified a structural failure mode in the evolution rule: once any
agent reaches hedge_fraction=0.00, the counterfactual comparison produces zero
signal regardless of how large capital costs grow, because both sides of the
comparison carry identical exposure. The risk committee is the escape mechanism:
an LLM agent that wakes only when hard thresholds are breached, looks at the
full treasury/VaR picture the evolution rule is blind to, and adjusts exactly
one lever (hedge_fraction) before returning to sleep.

This module handles the threshold-monitoring and context-packaging side — pure
Python, no LLM, no I/O beyond the context file it writes. The LLM agent lives
in sim/risk_committee_agent.py and is invoked only when this module returns
True from check_thresholds().

Two hard thresholds (both checked after every settlement period in the
orchestration's treasury walk):

  1. Treasury drawdown > 10% from its rolling 12-month peak — the treasury is
     visibly deteriorating; the evolution rule reacts only at term boundaries
     and is structurally blind between them.

  2. VaR_current > VaR_stressed × 1.2 — the current-conditions volatility view
     has blown through the regulatory floor by 20%; this is the forward-looking
     signal the evolution rule never sees (it only looks back at completed terms).

The Context Handshake: when either threshold is breached, this module packages
the full portfolio state into a structured Markdown summary and writes it to
docs/context-handshake-latest.md for the risk committee agent to read. Each
wake-up overwrites the file (one active context at a time — the agent acts once
and goes back to sleep before the next breach can occur).
"""

from datetime import date, timedelta
from collections import deque
import statistics

TREASURY_DRAWDOWN_THRESHOLD = 0.10    # trigger if treasury has fallen >10% from 12-month peak
VAR_BREACH_MULTIPLIER = 1.20          # trigger if VaR_current > VaR_stressed × this
PEAK_LOOKBACK_PERIODS = 365 * 48      # ~12 months of half-hourly periods for rolling peak window

HANDSHAKE_FILE = "docs/context-handshake-latest.md"


class RiskCommitteeMonitor:
    """Stateful threshold monitor — instantiated once per simulation run, updated
    every settlement period. Call update() after each period's treasury delta;
    if it returns True, call build_handshake_context() and then invoke the agent.

    Deliberately has no knowledge of the LLM agent — it only packages context and
    raises a flag. The orchestration decides when to invoke the agent.
    """

    def __init__(self, starting_treasury_gbp: float):
        self._treasury = starting_treasury_gbp
        self._peak = starting_treasury_gbp
        # Rolling deque of (date_str, treasury_balance) tuples for the 12-month window
        self._history: deque = deque()
        self._triggered_this_period = False

    def update(
        self,
        new_treasury_gbp: float,
        settlement_date: str,
        settlement_period: int,
        var_current_gbp: float,
        var_stressed_gbp: float,
        portfolio_state: dict,
        system_price_records: list[dict],
    ) -> bool:
        """Update monitor state with the current period's values. Returns True if
        either threshold is breached and the risk committee should be invoked.

        portfolio_state must be a dict with keys:
          customers: list of {customer_id, hedge_fraction, eac_kwh, active_collateral_gbp,
                              monthly_cost_of_capital_gbp, var_current_gbp, var_stressed_gbp}
          gross_margin_ytd_gbp: float
          net_margin_ytd_gbp: float
          capital_costs_ytd_gbp: float
          sigma_recent: float   (portfolio-weighted average, or latest single-customer value)
          forward_price_gbp_per_mwh: float  (representative forward price, latest term)
        """
        self._treasury = new_treasury_gbp
        self._history.append((settlement_date, new_treasury_gbp))

        # Maintain rolling 12-month peak window
        cutoff = (date.fromisoformat(settlement_date) - timedelta(days=365)).isoformat()
        while self._history and self._history[0][0] < cutoff:
            self._history.popleft()

        rolling_peak = max(b for _, b in self._history) if self._history else new_treasury_gbp
        self._peak = rolling_peak

        drawdown_pct = (rolling_peak - new_treasury_gbp) / rolling_peak if rolling_peak > 0 else 0.0
        var_breach_ratio = var_current_gbp / var_stressed_gbp if var_stressed_gbp > 0 else 0.0

        treasury_breached = drawdown_pct > TREASURY_DRAWDOWN_THRESHOLD
        var_breached = var_breach_ratio > VAR_BREACH_MULTIPLIER

        if treasury_breached or var_breached:
            trigger_description = []
            if treasury_breached:
                trigger_description.append(
                    f"treasury drawdown {drawdown_pct:.1%} from 12-month peak £{rolling_peak:.2f}"
                )
            if var_breached:
                trigger_description.append(
                    f"VaR_current £{var_current_gbp:.2f} exceeds VaR_stressed £{var_stressed_gbp:.2f} × {VAR_BREACH_MULTIPLIER} (ratio {var_breach_ratio:.2f})"
                )

            self._write_handshake_context(
                settlement_date=settlement_date,
                settlement_period=settlement_period,
                trigger_description=" | ".join(trigger_description),
                drawdown_pct=drawdown_pct,
                rolling_peak=rolling_peak,
                var_current_gbp=var_current_gbp,
                var_stressed_gbp=var_stressed_gbp,
                var_breach_ratio=var_breach_ratio,
                portfolio_state=portfolio_state,
            )
            return True

        return False

    def _write_handshake_context(
        self,
        settlement_date: str,
        settlement_period: int,
        trigger_description: str,
        drawdown_pct: float,
        rolling_peak: float,
        var_current_gbp: float,
        var_stressed_gbp: float,
        var_breach_ratio: float,
        portfolio_state: dict,
    ) -> None:
        """Write the structured context summary to HANDSHAKE_FILE. Overwrites any
        existing content — one active context at a time; the agent acts and the
        file is stale until the next breach.
        """
        regime = "post-2023 (σ_stressed = 1.50)" if settlement_date >= "2023-01-01" else "pre-2023 (σ_stressed = 0.50)"
        customers = portfolio_state.get("customers", [])

        per_customer_hf = " ".join(
            f"{c['customer_id']}={c['hedge_fraction']:.2f}" for c in customers
        )
        per_customer_collateral = " ".join(
            f"{c['customer_id']}: collateral=£{c['active_collateral_gbp']:.2f} coc=£{c['monthly_cost_of_capital_gbp']:.4f}/mo"
            for c in customers
        )

        # Identify which customers triggered the VaR threshold
        triggered_customers = [
            c["customer_id"] for c in customers
            if c.get("var_current_gbp", 0) > c.get("var_stressed_gbp", 0) * VAR_BREACH_MULTIPLIER
        ]
        if not triggered_customers:
            triggered_customers = [c["customer_id"] for c in customers]

        content = f"""## Risk Committee Wake-Up — {settlement_date} period {settlement_period}
Trigger: {trigger_description}
Treasury balance: £{self._treasury:.2f} (12-month peak: £{rolling_peak:.2f}, drawdown: {drawdown_pct:.1%})
Portfolio gross margin YTD: £{portfolio_state.get('gross_margin_ytd_gbp', 0):.2f} | Net margin YTD: £{portfolio_state.get('net_margin_ytd_gbp', 0):.2f}
Capital costs YTD: £{portfolio_state.get('capital_costs_ytd_gbp', 0):.2f}
VaR_current: £{var_current_gbp:.2f} | VaR_stressed: £{var_stressed_gbp:.2f} | Ratio: {var_breach_ratio:.2f}
Per-customer hedge_fraction: {per_customer_hf}
Per-customer collateral: {per_customer_collateral}
Rolling 12m SSP: σ_recent = {portfolio_state.get('sigma_recent', 0):.3f} | Forward price: £{portfolio_state.get('forward_price_gbp_per_mwh', 0):.2f}/MWh
Regime: {regime}
Recommendation requested: adjust hedge_fraction for {", ".join(triggered_customers)}
Constraint: minimum adjustment +0.10, maximum single adjustment +0.30 | never decrease hedge_fraction
"""
        with open(HANDSHAKE_FILE, "w") as f:
            f.write(content)
