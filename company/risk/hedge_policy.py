"""Company hedging policy — Phase 22b.

The company owns the decision of HOW MUCH to hedge. This module contains
the policy logic that the company applies at each contract renewal: given
what just happened on the completed term, should the hedge fraction go up,
down, or stay the same for the next one?

The decision uses only company-observable data:
- actual_net: observed from the company's own P&L records (billing minus cost)
- naked_net: computed by the company from its own volume data + observable
  market spot prices (NOT a SIM-internal oracle — spot prices are published
  market data that any supplier can look up)

This closes the Level 2 (decision boundary) separation for hedging.
Previously evolve_hedge_fraction lived in sim/hedging_strategy.py; that
module remains for the historical Phase 1d-2a runners. Phase 2b and later
use this module for hedging decisions.
"""

# Minimum hedge mandate: a real energy supplier manages a supply obligation
# first, not a speculative position. The company never hedges less than
# MIN_HEDGE_FLOOR regardless of how the active-position signal fires.
COMPANY_MIN_HEDGE_FLOOR = 0.85

COMPANY_EVOLUTION_STEP = 0.1
COMPANY_MARGIN_TOLERANCE_GBP = 5.0


def company_evolve_hedge_fraction(
    current_hedge_fraction: float,
    naked_net_gbp: float,
    actual_net_gbp: float,
) -> tuple[float, str]:
    """Adjust hedge fraction for the next term from completed-term outcomes.

    naked_net_gbp: what the company computes it would have made with no
        hedge — revenue minus (volume × actual spot price). Observable: the
        company has its own volume data and can look up realised spot prices.
    actual_net_gbp: what the company actually made — direct from P&L.

    Decision rule (same as the historical sim.hedging_strategy logic, now
    in the company layer where it belongs):
      difference = actual_net_gbp - naked_net_gbp
      > TOLERANCE  → hedge beat naked → raise fraction (capped at 1.0)
      < -TOLERANCE → naked beat hedge → trim fraction (floored at COMPANY_MIN_HEDGE_FLOOR)
      otherwise   → noise, hold position
    """
    difference = actual_net_gbp - naked_net_gbp

    if difference > COMPANY_MARGIN_TOLERANCE_GBP:
        new_hf = min(1.0, current_hedge_fraction + COMPANY_EVOLUTION_STEP)
        reason = (
            f"Actual £{actual_net_gbp:.2f}, naked £{naked_net_gbp:.2f}, "
            f"diff £{difference:.2f} — hedge beat naked; raise to {new_hf:.2f}"
        )
    elif difference < -COMPANY_MARGIN_TOLERANCE_GBP:
        new_hf = max(COMPANY_MIN_HEDGE_FLOOR, current_hedge_fraction - COMPANY_EVOLUTION_STEP)
        reason = (
            f"Actual £{actual_net_gbp:.2f}, naked £{naked_net_gbp:.2f}, "
            f"diff £{difference:.2f} — naked beat hedge; trim to {new_hf:.2f}"
        )
    else:
        new_hf = current_hedge_fraction
        reason = (
            f"Actual £{actual_net_gbp:.2f}, naked £{naked_net_gbp:.2f}, "
            f"diff £{difference:.2f} — within tolerance; hold at {new_hf:.2f}"
        )

    return new_hf, reason
