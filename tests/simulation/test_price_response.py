"""Controls on the 2022 price response (`simulation.price_response`) and its hook in the fabric path.

Each control names the defect it exists to catch. The expected multipliers are computed from the
world's own cap rates, never typed as literals, so a re-pinned cap moves the control with it.
"""

from __future__ import annotations

import datetime as dt
import statistics as st

import pytest

from simulation import fabric_demand_path as fdp
from simulation import premise_trace as pt
from simulation import price_response as pr
from simulation.svt_rates import (
    get_svt_elec_rate_charged_to_household_gbp_per_mwh as elec_rate,
)
from simulation.svt_rates import (
    get_svt_gas_rate_charged_to_household_gbp_per_mwh as gas_rate,
)
from tests.simulation.test_premise_trace import make_household

DAYS = [dt.date(2021, 1, 1) + dt.timedelta(days=i) for i in range(4 * 365 + 1)]


def _winter_mean(rate_fn, year: int) -> float:
    days = pr._winter_days(year)
    return sum(rate_fn(d.isoformat()) for d in days) / len(days)


def test_the_partition_is_reachable_no_response_a_cut_and_a_rise():
    """A guard that answers 1.0 everywhere passes every 'it does not respond early' test. So first:
    over the same window, a negative draw is cut, a positive draw (SERL's upper electricity quartile
    is positive) uses more, and the days before the first response year are untouched."""
    cut = pr.response_multipliers(DAYS, -0.071, gas_rate)
    rise = pr.response_multipliers(DAYS, 0.016, elec_rate)
    assert cut["2021-12-01"] == 1.0 and cut["2022-11-01"] < 1.0 and rise["2022-11-01"] > 1.0


def test_nothing_responds_before_april_2022_and_the_cap_change_is_answered_the_day_it_lands():
    """The prebound leg cut gas in winter 2021/22 because it held one constraint per CALENDAR year
    and carried April's rise back into January. The response must start on the cap's own day."""
    m = pr.response_multipliers(DAYS, -0.071, gas_rate)
    assert all(m[d.isoformat()] == 1.0 for d in DAYS if d < dt.date(2022, 4, 1))
    assert m["2022-04-01"] < 1.0
    assert m["2022-09-30"] != m["2022-10-01"], "the October 2022 cap change was not re-evaluated"


def test_winter_2022_23_is_the_elasticity_times_the_change_against_winter_2021_22():
    """The form SERL's own numbers support: e x the %-change against the prior winter's mean rate."""
    e = -0.071
    expected = 1 + e * (gas_rate("2022-11-15") / _winter_mean(gas_rate, 2021) - 1)
    assert pr.response_multipliers(DAYS, e, gas_rate)["2022-11-15"] == pytest.approx(expected)


def test_the_cut_is_carried_into_2023_24_and_partly_decays():
    """Two defects in one control. With no chain, a falling price against winter 22/23 reads as
    a RISE above the no-response world. With a fixed reference, the cut never decays. The 23/24
    level must sit between the 22/23 level and no response at all."""
    m = pr.response_multipliers(DAYS, -0.071, gas_rate)
    w2223, w2324 = m["2023-02-01"], m["2024-02-01"]
    assert w2223 < w2324 < 1.0


def test_in_february_the_prior_winter_is_the_last_complete_one_not_the_one_in_progress():
    """Feb 2024 sits inside winter 23/24, so the household's prior winter is 22/23. A calendar
    response year answers it against 23/24, its own winter. That is invisible while a winter's cap is
    flat (22/23 at the EPG), so the control reads a winter whose cap moved in January."""
    e = -0.071
    level_2022 = 1 + e * (_winter_mean(gas_rate, 2022) / _winter_mean(gas_rate, 2021) - 1)
    expected = level_2022 * (1 + e * (gas_rate("2024-02-01") / _winter_mean(gas_rate, 2022) - 1))
    assert gas_rate("2024-02-01") != gas_rate("2023-11-01"), "the control needs a winter that moved"
    assert pr.response_multipliers(DAYS, e, gas_rate)["2024-02-01"] == pytest.approx(expected)


def test_a_missing_rate_raises_rather_than_reading_as_no_response():
    with pytest.raises(ValueError, match="no household-facing rate"):
        pr.response_multipliers(DAYS, -0.071, lambda _d: None)


def test_the_draw_reproduces_serls_quartiles_for_both_fuels():
    draws = [pr.draw_elasticity(f"premise-{i}", 2016) for i in range(4000)]
    for fuel, published in (
        ("gas", pr.SERL_GAS_ELASTICITY_QUARTILES),
        ("electricity", pr.SERL_ELECTRICITY_ELASTICITY_QUARTILES),
    ):
        got = st.quantiles([getattr(d, fuel) for d in draws], n=4)
        for g, p in zip(got, published):
            assert g == pytest.approx(p, abs=0.012), f"{fuel}: {got} against SERL {published}"


def test_the_two_fuels_are_drawn_independently_and_the_draw_is_deterministic():
    """The joint is not published. One uniform for both fuels would make every household a
    comonotone cutter, which SERL Fig. 3 contradicts."""
    draws = [pr.draw_elasticity(f"premise-{i}", 2016) for i in range(2000)]
    assert abs(st.correlation([d.gas for d in draws], [d.electricity for d in draws])) < 0.1
    assert pr.draw_elasticity("C1", 2016) == pr.draw_elasticity("C1", 2016)
    assert pr.draw_elasticity("C1", 2016) != pr.draw_elasticity("C1", 2017)


def test_the_split_normal_refuses_quartiles_out_of_order():
    with pytest.raises(ValueError):
        pr.split_normal_quantile(0.5, (0.1, 0.0, 0.2))


# ---------------------------------------------------------------------------
# The hook in the fabric path
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def spring_2022_pair():
    weather = pt.load_trace_weather("C1", start=dt.date(2022, 3, 25), end=dt.date(2022, 4, 6))
    household = make_household("C1")
    kwargs = dict(customer_id="C1", household_at_date=lambda _d: household, weather=weather,
                  latitude_deg=53.0)
    return (fdp.build_fabric_series(**kwargs),
            fdp.build_fabric_series(**kwargs, price_response=False),
            fdp.build_fabric_series(**kwargs, price_response=True))


def test_off_is_the_world_as_it_was(spring_2022_pair):
    default, off, _ = spring_2022_pair
    assert default.gas_kwh == off.gas_kwh and default.gross_electricity_kwh == off.gross_electricity_kwh


def test_on_scales_each_fuel_by_its_own_multiplier_from_the_cap_day(spring_2022_pair):
    _, off, on = spring_2022_pair
    dates = [dt.date.fromisoformat(k) for k in off.dates()]
    m = pr.household_multipliers("C1", dates, seed=fdp.DEFAULT_TRACE_SEED)
    assert on.gas_kwh["2022-03-31"] == off.gas_kwh["2022-03-31"]
    for fuel, attr in (("gas", "gas_kwh"), ("electricity", "gross_electricity_kwh")):
        ratio = sum(getattr(on, attr)["2022-04-02"]) / sum(getattr(off, attr)["2022-04-02"])
        assert ratio == pytest.approx(m[fuel]["2022-04-02"], rel=1e-5) and ratio != 1.0
    assert on.gas_space_heating_kwh["2022-04-02"] == pytest.approx(
        off.gas_space_heating_kwh["2022-04-02"] * m["gas"]["2022-04-02"], rel=1e-5)
