from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class MarginBridge:
    year_from: int
    year_to: int
    net_delta_gbp: float
    gross_delta_gbp: float
    bad_debt_delta_gbp: float   # negative = bad debt costs rose (worse for margin)
    capital_delta_gbp: float    # negative = capital costs rose
    policy_cost_delta_gbp: float  # negative = policy costs rose
    network_cost_delta_gbp: float  # negative = network costs rose
    portfolio_change: int         # active customer count delta
    residual_gbp: float           # net_delta minus sum of components
    direction: Literal["IMPROVEMENT", "DETERIORATION", "FLAT"]

    @property
    def year_label(self) -> str:
        return f"{self.year_from}\u2192{self.year_to}"

    @property
    def named_driver_max_gbp(self) -> float:
        """Largest absolute movement among the five *named* drivers."""
        return max(
            abs(self.gross_delta_gbp),
            abs(self.bad_debt_delta_gbp),
            abs(self.capital_delta_gbp),
            abs(self.policy_cost_delta_gbp),
            abs(self.network_cost_delta_gbp),
        )


_FLAT_THRESHOLD_GBP = 5_000

# R15 reconciliation tripwire.  The residual is `net_delta - sum(named drivers)`.
# Because net margin is DEFINED as gross minus exactly these cost lines, the
# residual is ~0 by construction -- so "residual == 0" is a TAUTOLOGY and proves
# nothing on its own (R15 killer pattern 1: checked value derived from the same
# source it checks).  The real failure it must catch is a *break* in that
# provenance -- a cost line added to `net_gbp` but not to the bridge (or a
# fail-open `.get(...,0.0)` silently zeroing a driver after a schema rename) --
# which makes the residual materially non-zero.  Above this floor the bridge has
# NOT explained the movement and must say so rather than confidently naming a
# minority driver.
_RESIDUAL_MATERIALITY_GBP = 5_000


def _direction(delta: float) -> Literal["IMPROVEMENT", "DETERIORATION", "FLAT"]:
    if delta > _FLAT_THRESHOLD_GBP:
        return "IMPROVEMENT"
    if delta < -_FLAT_THRESHOLD_GBP:
        return "DETERIORATION"
    return "FLAT"


def _build_bridge(yr_a: str, yr_b: str, data_a: dict, data_b: dict) -> MarginBridge:
    net_delta = data_b["net_gbp"] - data_a["net_gbp"]
    gross_delta = data_b["gross_gbp"] - data_a["gross_gbp"]

    # Bad debt: higher cost = lower margin.  Delta in cost terms (bad_debt is positive cost).
    bad_debt_delta = -(data_b.get("bad_debt_gbp", 0.0) - data_a.get("bad_debt_gbp", 0.0))

    capital_delta = -(data_b.get("capital_gbp", 0.0) - data_a.get("capital_gbp", 0.0))

    policy_a = data_a.get("policy_cost_gbp", 0.0) + data_a.get("gas_policy_cost_gbp", 0.0)
    policy_b = data_b.get("policy_cost_gbp", 0.0) + data_b.get("gas_policy_cost_gbp", 0.0)
    policy_delta = -(policy_b - policy_a)

    network_a = data_a.get("network_cost_gbp", 0.0) + data_a.get("gas_network_cost_gbp", 0.0)
    network_b = data_b.get("network_cost_gbp", 0.0) + data_b.get("gas_network_cost_gbp", 0.0)
    network_delta = -(network_b - network_a)

    portfolio_change = len(data_b.get("active_customer_ids", [])) - len(data_a.get("active_customer_ids", []))

    components = gross_delta + bad_debt_delta + capital_delta + policy_delta + network_delta
    residual = net_delta - components

    return MarginBridge(
        year_from=int(yr_a),
        year_to=int(yr_b),
        net_delta_gbp=net_delta,
        gross_delta_gbp=gross_delta,
        bad_debt_delta_gbp=bad_debt_delta,
        capital_delta_gbp=capital_delta,
        policy_cost_delta_gbp=policy_delta,
        network_cost_delta_gbp=network_delta,
        portfolio_change=portfolio_change,
        residual_gbp=residual,
        direction=_direction(net_delta),
    )


def build_margin_bridge_series(run_data: dict) -> list[MarginBridge]:
    years_raw = run_data.get("years", {})
    sorted_keys = sorted(years_raw.keys())
    if len(sorted_keys) < 2:
        return []
    bridges = []
    for i in range(len(sorted_keys) - 1):
        yr_a, yr_b = sorted_keys[i], sorted_keys[i + 1]
        bridges.append(_build_bridge(yr_a, yr_b, years_raw[yr_a], years_raw[yr_b]))
    return bridges


def residual_is_material(bridge: MarginBridge) -> bool:
    """R15 tripwire: True when the unexplained residual is BOTH above the
    materiality floor AND strictly larger than every named driver -- i.e. the
    bridge has failed to explain its own net-margin movement.

    Returns False on a well-reconciled bridge (residual ~0, the healthy state on
    real data).  This is deliberately a control that CAN fail: feed it a bridge
    whose net_delta no longer equals the sum of its drivers (the exact symptom of
    a dropped/fail-open cost line) and it fires -- see the mutation tests.
    """
    # Computed inline (not via the dataclass property) so this also works on the
    # lightweight attribute-only objects the report renderer reconstructs from
    # the serialised bridge dicts.
    named_max = max(
        abs(bridge.gross_delta_gbp),
        abs(bridge.bad_debt_delta_gbp),
        abs(bridge.capital_delta_gbp),
        abs(bridge.policy_cost_delta_gbp),
        abs(bridge.network_cost_delta_gbp),
    )
    r = abs(bridge.residual_gbp)
    return r > _RESIDUAL_MATERIALITY_GBP and r > named_max


def dominant_driver(bridge: MarginBridge) -> str:
    candidates = {
        "gross margin": abs(bridge.gross_delta_gbp),
        "bad debt": abs(bridge.bad_debt_delta_gbp),
        "capital costs": abs(bridge.capital_delta_gbp),
        "policy levies": abs(bridge.policy_cost_delta_gbp),
        "network costs": abs(bridge.network_cost_delta_gbp),
    }
    named = max(candidates, key=candidates.__getitem__)
    # Honesty: the residual absorbs every un-named movement.  If it strictly
    # dominates every named driver (and is material), the bridge does NOT explain
    # the change -- naming a minority named driver would be a false attribution.
    if residual_is_material(bridge):
        return "other (unexplained)"
    return named
