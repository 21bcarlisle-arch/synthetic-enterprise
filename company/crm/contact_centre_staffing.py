"""The supplier's phone staffing decision: how many agents to put on the phones, and what that costs.

The world draws a wait for every phone contact (`simulation/contact_centre.py`), and since
2026-11-21 it can answer a staffing plan with a wait (`phone_queue`). Nothing on the company side
chose a plan. This desk does. It is the supplier's workforce-management arithmetic, a real
supplier's own tool, and it reads only what a real supplier has: its own count of calls an hour
and its own measured handle time. It never sees the world's handle time or the propensity behind
the arrivals. Its prediction of the wait is its belief. The wait the world returns is the
outcome, and the gap between the two is the desk's error, not something to remove.

Knowledge (K8): docs/market_research/contact_centre_staffing_cost_and_call_wait_gb_energy_2026-11-21.md.
The two published wait lines are below as named targets. Which one to staff to is the company's
choice and the caller's argument. Neither is a default, because a default would be a decision
taken here without anyone deciding it.

The cost is a FLOOR, and named as one. It is the ONS median wage times paid hours, where paid
hours are answering hours grossed up for statutory leave only. Employer NI and pension (about 8%
in 2016 to 15% in 2025 at a full-time median, page s.3, rates not fetched), the rest of
shrinkage, and seat and telephony cost are all GAPs. They are carried as named omissions rather
than one loading picked to fill a slot. The floor understates the cost of staffing up, so any
gain this desk finds from more agents is overstated on the cost side.

REUSE: company/crm/contact_centre_staffing.py
CLASS: CUSTOM
INDEX: searched "contact centre staffing", "erlang", "agents", "call wait", "queue".
       `company/crm/service_quality_monitor.py` bands bill clarity and complaint rates, and
       `company/crm/customer_experience_desk.py` books how customers feel. Neither decides
       capacity, and no company module computes a queue. The world's
       `simulation.contact_centre.erlang_c` is on the other side of the wall and may not be
       imported, so the supplier keeps its own copy of the same textbook arithmetic. When the
       world gains abandonment, the two will disagree, and they should.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

# Ofgem, "Guidance on expectations for consumers to be able to contact their supplier", Apr 2025,
# para 1.53: a supplier should be able to justify "longer than a monthly average of 5 minutes".
OFGEM_JUSTIFY_LINE_SECONDS = 300.0
# Citizens Advice star rating, "How the scores are worked out": call wait 5 stars under 30 s.
CITIZENS_ADVICE_FIVE_STAR_SECONDS = 30.0

# ONS ASHE Table 14.6a, median gross hourly pay excluding overtime, UK, SOC 7211 "Call and
# contact centre occupations", revised editions as fetched 2026-11-21 (SHA-256 in the K8 page,
# s.3). SOC 2010 to 2019, SOC 2020 from 2022.
ASHE_CALL_CENTRE_MEDIAN_GBP_PER_HOUR = {
    2016: 8.72,
    2019: 9.38,
    2022: 11.27,
    2024: 13.11,
    2025: 14.26,
}
# Working Time Regulations 1998, reg 13 and 13A: 5.6 weeks' paid leave, so an agent paid for 52
# weeks answers for at most 46.4.
STATUTORY_LEAVE_WEEKS = 5.6


def wage_gbp_per_hour(year: int) -> Optional[float]:
    """The ONS median for `year`. Years between fetched editions are interpolated log-linearly.

    SIMPLIFICATION: 2017, 2018, 2020, 2021 and 2023 were not fetched. The pay sits on the
    National Living Wage, which steps once a year, so the error is a fraction of one year's rise,
    in either direction. Doing it properly is fetching those five editions. Outside 2016 to 2025
    the answer is None: nothing was fetched there to stand on.
    """
    table = ASHE_CALL_CENTRE_MEDIAN_GBP_PER_HOUR
    if year in table:
        return table[year]
    years = sorted(table)
    if year < years[0] or year > years[-1]:
        return None
    lo = max(y for y in years if y < year)
    hi = min(y for y in years if y > year)
    frac = (year - lo) / (hi - lo)
    return round(math.exp(math.log(table[lo]) * (1 - frac) + math.log(table[hi]) * frac), 2)


def erlang_c(offered_load_erlangs: float, agents: int) -> float:
    """Probability a call waits in an M/M/N queue. 1.0 when agents <= load."""
    if offered_load_erlangs <= 0:
        return 0.0
    if agents <= offered_load_erlangs:
        return 1.0
    blocking = 1.0
    for n in range(1, agents + 1):
        blocking = offered_load_erlangs * blocking / (n + offered_load_erlangs * blocking)
    rho = offered_load_erlangs / agents
    return blocking / (1.0 - rho + rho * blocking)


def predicted_mean_wait_seconds(
    calls_per_hour: float, handle_minutes: float, agents: int
) -> Optional[float]:
    """The desk's belief about the mean wait, or None when the plan cannot clear the load."""
    load = calls_per_hour * handle_minutes / 60.0
    if load == 0:
        return 0.0
    if agents <= load:
        return None
    return erlang_c(load, agents) * handle_minutes * 60.0 / (agents - load)


@dataclass(frozen=True)
class PhoneStaffingPlan:
    """One hour's plan. `refused` names why no plan was made, and then every number is None."""

    observed_calls_per_hour: float
    observed_handle_minutes: Optional[float]
    target_mean_wait_seconds: float
    agents: Optional[int]
    predicted_mean_wait_seconds: Optional[float]
    refused: Optional[str] = None


def plan_phone_agents(
    observed_calls_per_hour: float,
    observed_handle_minutes: Optional[float],
    target_mean_wait_seconds: float,
) -> PhoneStaffingPlan:
    """The fewest agents whose predicted mean wait is at or under the target."""
    if observed_handle_minutes is None or observed_handle_minutes <= 0:
        return PhoneStaffingPlan(
            observed_calls_per_hour, observed_handle_minutes, target_mean_wait_seconds,
            None, None,
            refused=(
                "no measured handle time: the desk sizes from its own call log, and a log "
                "without handle times cannot size a queue"
            ),
        )
    if target_mean_wait_seconds <= 0:
        return PhoneStaffingPlan(
            observed_calls_per_hour, observed_handle_minutes, target_mean_wait_seconds,
            None, None,
            refused="a zero mean wait is unreachable at any finite staffing when anyone calls",
        )
    load = observed_calls_per_hour * observed_handle_minutes / 60.0
    agents = max(1, math.floor(load) + 1)
    while True:
        wait = predicted_mean_wait_seconds(observed_calls_per_hour, observed_handle_minutes, agents)
        if wait is not None and wait <= target_mean_wait_seconds:
            return PhoneStaffingPlan(
                observed_calls_per_hour, observed_handle_minutes, target_mean_wait_seconds,
                agents, wait,
            )
        agents += 1


@dataclass(frozen=True)
class StaffingCostFloor:
    year: int
    answering_hours: float
    paid_hours: float
    wage_gbp_per_hour: Optional[float]
    cost_floor_gbp: Optional[float]
    omitted: tuple[str, ...]
    refused: Optional[str] = None


_OMITTED_FROM_THE_FLOOR = (
    "employer NI and auto-enrolment pension (K8 page s.3: about 8% in 2016 to 15% in 2025)",
    "shrinkage beyond statutory leave: training, sickness, breaks, after-call work (GAP, s.5)",
    "seat, telephony, IT and supervision cost per agent hour (GAP, s.5)",
)


def staffing_cost_floor(agent_answering_hours: float, year: int) -> StaffingCostFloor:
    """The wage floor under `agent_answering_hours` of phone cover in `year`."""
    paid_hours = agent_answering_hours * 52.0 / (52.0 - STATUTORY_LEAVE_WEEKS)
    wage = wage_gbp_per_hour(year)
    if wage is None:
        return StaffingCostFloor(
            year, agent_answering_hours, paid_hours, None, None, _OMITTED_FROM_THE_FLOOR,
            refused=f"no ONS SOC 7211 edition fetched near {year} (fetched: 2016 to 2025)",
        )
    return StaffingCostFloor(
        year, agent_answering_hours, paid_hours, wage, round(paid_hours * wage, 2),
        _OMITTED_FROM_THE_FLOOR,
    )
