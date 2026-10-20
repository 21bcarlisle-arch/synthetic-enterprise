"""C34 decided at the renewal notice, per household, and recorded. The engine reaches it through
`company/interfaces/renewal_advice.py`.

REUSE: company/crm/renewal_advice_desk.py
CLASS: CUSTOM
INDEX: searched "renewal", "next_best_action", "advice", "decide" under company/interfaces/ and
       company/crm/. `next_best_action` holds the rule (`decide`, `states_for_decision`) and had no
       engine caller; `tools/retention_rise_count` drives the same rule from a probe file, which is
       a harness reading, not a run. `contact_programme` is the only engine door into
       `next_best_action`, and it answers a coin, not a decision.

WHERE AND WHY (`docs/market_research/next_best_action_and_cross_sell.md` §6.1, "Where a real
supplier makes this decision"). The renewal notice (SLC 22C.3 -> 31I) is the one contact every
fixed-term household receives, and the only place a bespoke retention price is lawful, so it is
where a supplier decides whether to add advice. A dual-fuel household gets one notice, so the
decision is the household's.

In: per leg, the account, the term start, the fuel, our monthly contribution
(`term_contribution_per_month`) and the company's own churn belief for the renewal. The leg
carrying the household's departure arrives at the roll; the other leg arrives when it is priced on the same start, and only if the household stayed. Out, at
the end of the run: one row per household per stated advice effect.

The hazard is the company's belief, `h = 1 - (1 - p)^(1/12)` over a 12-month term (B11's shape).
Nothing here reaches the world: the rows are a record, and nothing is sent.
"""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from company.crm.next_best_action import (
    AccountState,
    Action,
    ActionEstimate,
    decide,
    states_for_decision,
)
from company.pricing.renewal_desk import pre_margin_unit_rate
from saas.cost_to_serve import FIXED_OVERHEAD_GBP_PER_YEAR

if TYPE_CHECKING:
    from company.policy.decision_policy import DecisionPolicy

__all__ = ["RenewalAdviceDesk", "STATED_ADVICE_EFFECTS", "term_contribution_per_month"]

# The horizon C34 was graded on: docs/market_research/next_best_action_and_cross_sell.md §6.1
# ("48 months") and a_retention_price_that_shares_the_value_an_action_creates.md §4.
HORIZON_MONTHS = 48

# The three advice effects as (GBP/month given up, monthly hazard cut): the stated range in
# docs/market_research/a_retention_price_that_shares_the_value_an_action_creates.md §4. Not an
# estimate: the company's holdout cannot decide one at this book size (next_best_action_and_cross_sell.md
# §6.2), so every row is a decision under one point of the range and says so.
STATED_ADVICE_EFFECTS = ((2.0, 0.001), (2.0, 0.003), (3.0, 0.003))

_EFFECT_SOURCE = ("stated range, a_retention_price_that_shares_the_value_an_action_creates.md §4; "
                  "no company estimate (the holdout cannot decide one at this book size)")


def term_contribution_per_month(
    *, unit_rate_gbp_per_mwh: float, term_start: str, company_forward_per_mwh: float | None,
    locked_policy_cost_per_mwh: float | None, locked_network_cost_per_mwh: float | None,
    company_eac_kwh: float, segment: str = "resi",
) -> float | None:
    """What this leg contributes to us a month: the unit rate over the term's own pre-margin cost,
    on the company's volume, less a year's cost to serve the leg, over 12.

    Not `unit_rate - forward`: that spread still carries the network, policy and capital costs the
    rate passes through (§6.1, amended 2026-10-20). The standing charge is left out as a stated GAP
    there, because the cap builds it to carry the network residual. `None` where the term does not
    record its locked costs, so the leg is counted rather than priced on a guess.
    """
    cost = pre_margin_unit_rate(company_forward_per_mwh, term_start,
                                locked_policy_cost_per_mwh, locked_network_cost_per_mwh)
    if cost is None:
        return None
    return ((unit_rate_gbp_per_mwh - cost) * company_eac_kwh / 1000.0
            - FIXED_OVERHEAD_GBP_PER_YEAR[segment]) / 12.0


def monthly_hazard(renewal_churn_belief: float) -> float:
    """The company's P(leave at this renewal), spread evenly over a 12-month term."""
    p = min(max(renewal_churn_belief, 0.0), 1.0)
    return 1.0 - (1.0 - p) ** (1.0 / 12.0)


class RenewalAdviceDesk:
    def __init__(self, policy: "DecisionPolicy") -> None:
        self._policy = policy
        self._legs: dict[tuple[str, str], list[AccountState]] = {}
        self._fuels: dict[tuple[str, str], list[str]] = {}
        # Legs that arrived with no contribution (the term recorded no locked costs), by kind.
        self.legs_without_contribution = {"roll": 0, "riding": 0}

    def observe_roll(self, *, account_id: str, term_start: str, fuel: str,
                     monthly_margin_gbp: float | None, renewal_churn_belief: float) -> None:
        """The leg the household's departure is decided on, at its renewal roll.

        The notice carries the fix as first offered. A declined fix is spliced into default-tariff
        segments on the same start, and those are not a second notice, so the first roll held stands.
        """
        key = (account_id, term_start)
        if key in self._legs:
            return
        if monthly_margin_gbp is None:
            self.legs_without_contribution["roll"] += 1
            return
        self._legs[key] = [AccountState(account_id, monthly_margin_gbp,
                                        monthly_hazard(renewal_churn_belief), 0, ())]
        self._fuels[key] = [fuel]

    def observe_riding_leg(self, *, account_id: str, term_start: str, fuel: str,
                           monthly_margin_gbp: float | None) -> bool:
        """The household's other leg, priced on the roll's start. False if no roll is held for it."""
        key = (account_id, term_start)
        legs = self._legs.get(key)
        # Once per fuel: a declined fix re-enters on the same start as default-tariff segments.
        if legs is None or fuel in self._fuels[key]:
            return False
        if monthly_margin_gbp is None:
            self.legs_without_contribution["riding"] += 1
            return False
        legs.append(dataclasses.replace(legs[0], monthly_margin_gbp=monthly_margin_gbp))
        self._fuels[key].append(fuel)
        return True

    def decisions(self) -> list[dict]:
        rows = []
        for (account_id, term_start), legs in self._legs.items():
            fuels = self._fuels[(account_id, term_start)]
            states = states_for_decision(legs, self._policy)
            # Merged, one state carries every leg; unmerged, each state is one leg, in order.
            carried = [fuels] if len(states) == 1 else [[f] for f in fuels]
            for state, its_fuels in zip(states, carried):
                for give_up, cut in STATED_ADVICE_EFFECTS:
                    # The cut is clamped at the household's own hazard, so the hazard with advice stays >= 0.
                    est = ActionEstimate(Action.TARIFF_ADVICE, give_up * 12.0, -give_up,
                                         -min(cut, state.monthly_departure_hazard))
                    d = decide(dataclasses.replace(state, estimates=(est,)), HORIZON_MONTHS,
                               self._policy)
                    rows.append({
                        "account_id": account_id,
                        "term_start": term_start,
                        "fuels": its_fuels,
                        "legs": len(its_fuels),
                        "monthly_margin_gbp": round(state.monthly_margin_gbp, 4),
                        "monthly_hazard": round(state.monthly_departure_hazard, 6),
                        "effect_gives_up_gbp_per_month": give_up,
                        "effect_hazard_cut": cut,
                        "effect_source": _EFFECT_SOURCE,
                        "action": d.action.value,
                        "advised": d.action is Action.TARIFF_ADVICE,
                        "value_change_gbp": round(d.value_change_gbp, 4),
                        "reason": d.reason,
                        "unscored": [[a.value, why] for a, why in d.unscored],
                    })
        return rows
