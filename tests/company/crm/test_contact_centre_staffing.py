"""The supplier's phone staffing desk (company/crm/contact_centre_staffing.py).

Each test names the defect it catches."""
import ast
import pathlib

import pytest

from company.crm.contact_centre_staffing import (
    ASHE_CALL_CENTRE_MEDIAN_GBP_PER_HOUR,
    CITIZENS_ADVICE_FIVE_STAR_SECONDS,
    OFGEM_JUSTIFY_LINE_SECONDS,
    plan_phone_agents,
    predicted_mean_wait_seconds,
    staffing_cost_floor,
    wage_gbp_per_hour,
)


def test_a_plan_and_a_refusal_are_both_reachable():
    """Defect: a desk that refuses everything passes every refusal test."""
    made = plan_phone_agents(120, 8, OFGEM_JUSTIFY_LINE_SECONDS)
    no_aht = plan_phone_agents(120, None, OFGEM_JUSTIFY_LINE_SECONDS)
    no_target = plan_phone_agents(120, 8, 0)
    assert made.refused is None and made.agents
    assert no_aht.agents is None and "handle time" in no_aht.refused
    assert no_target.agents is None and "unreachable" in no_target.refused


@pytest.mark.parametrize("aht", [4, 6, 8, 10, 12])
@pytest.mark.parametrize("calls", [30, 120, 600])
@pytest.mark.parametrize("target", [OFGEM_JUSTIFY_LINE_SECONDS, CITIZENS_ADVICE_FIVE_STAR_SECONDS])
def test_the_plan_is_the_fewest_agents_that_meet_the_target(aht, calls, target):
    """Defect: an off-by-one overstaffs (cost the book does not owe) or understaffs (a wait it
    did not plan for)."""
    plan = plan_phone_agents(calls, aht, target)
    assert plan.predicted_mean_wait_seconds <= target
    fewer = predicted_mean_wait_seconds(calls, aht, plan.agents - 1)
    assert fewer is None or fewer > target


def test_five_stars_costs_proportionally_less_on_a_bigger_book():
    """Defect: the premium is read as a constant share. K8 page s.4 item 2: queues pool."""
    def premium(calls):
        o = plan_phone_agents(calls, 8, OFGEM_JUSTIFY_LINE_SECONDS).agents
        c = plan_phone_agents(calls, 8, CITIZENS_ADVICE_FIVE_STAR_SECONDS).agents
        return c / o - 1
    assert premium(30) > premium(120) > premium(600) > 0


def test_the_wage_is_the_published_figure_where_one_was_fetched_and_none_outside():
    """Defect: an extrapolated wage outside 2016-2025 reads as established."""
    for year, wage in ASHE_CALL_CENTRE_MEDIAN_GBP_PER_HOUR.items():
        assert wage_gbp_per_hour(year) == wage
    assert wage_gbp_per_hour(2015) is None and wage_gbp_per_hour(2026) is None
    between = [wage_gbp_per_hour(y) for y in range(2016, 2026)]
    assert all(b > a for a, b in zip(between, between[1:]))


def test_the_cost_is_a_floor_that_names_what_it_leaves_out():
    """Defect: the floor is read as the whole cost, or the leave gross-up is dropped."""
    floor = staffing_cost_floor(1000, 2024)
    assert floor.cost_floor_gbp > 1000 * 13.11
    assert floor.paid_hours == pytest.approx(1000 * 52 / 46.4)
    assert len(floor.omitted) == 3 and any("NI" in o for o in floor.omitted)
    assert staffing_cost_floor(1000, 2014).refused


def test_the_desk_reads_nothing_from_the_world():
    """Defect: the desk imports the world's queue, so its belief is the world's truth."""
    src = pathlib.Path(__file__).resolve().parents[3] / "company/crm/contact_centre_staffing.py"
    for node in ast.walk(ast.parse(src.read_text())):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = node.module if isinstance(node, ast.ImportFrom) else node.names[0].name
            assert not (mod or "").startswith(("simulation", "sim")), mod
