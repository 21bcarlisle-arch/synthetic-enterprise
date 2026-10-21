"""A traditional meter already on supply is exchanged for a smart one (W2 for D48, knowledge s.4e).

Before this, the meter was drawn once at acquisition and never changed, so a 2016 cohort stayed at
2016's 10.6% smart for the whole decade and the book was 29% smart in 2024 against 68.9% nationally.
The defect each test names is in its own docstring.
"""

from __future__ import annotations

import datetime as dt
import math

from simulation import meter_reads
from simulation.life_events import smart_meter_exchange_hazard, smart_meter_installed_event
from simulation.meter_reads import SimulatedReadFeed, simulate_read
from simulation.population_draw import _draw_smart_meter
from simulation.premise_population import smart_meter_penetration

SEED = 42


def _smart_share_at_end_of(year: int, acquired_year: int, n: int, exchange: bool) -> float:
    smart = 0
    for i in range(n):
        cid = f"PROS-{acquired_year}-{i:05d}"
        at_acquisition = _draw_smart_meter(cid, SEED, acquired_year, "resi")
        event = (smart_meter_installed_event(cid, SEED, dt.date(acquired_year, 6, 1), at_acquisition)
                 if exchange else None)
        smart += at_acquisition or (event is not None and int(event.event_date[:4]) <= year)
    return smart / n


def test_every_cohort_reaches_the_national_2024_smart_share():
    """Defect: the hazard is the stock's increment, not conditioned on still being traditional.

    The book's 2024 share would then fall short of DESNZ's 68.9% for every cohort, by more the
    earlier it was acquired. The band is four binomial standard errors. The no-exchange arm is the
    world before this build, and it must sit outside the band, or the control could not fail.
    """
    target = smart_meter_penetration(2024)
    n = 4000
    band = 4 * math.sqrt(target * (1 - target) / n)
    for acquired_year in range(2016, 2024):
        share = _smart_share_at_end_of(2024, acquired_year, n, exchange=True)
        assert abs(share - target) <= band, (acquired_year, share, target, band)
    stuck = _smart_share_at_end_of(2024, 2016, n, exchange=False)
    assert stuck < target - band, stuck


def test_the_hazard_is_conditional_on_the_meter_still_being_traditional():
    """Defect: a hazard above the stock's raw increment is not conditional, or it is negative."""
    for year in range(2017, 2025):
        increment = smart_meter_penetration(year) - smart_meter_penetration(year - 1)
        assert smart_meter_exchange_hazard(year) > increment > 0
    assert smart_meter_exchange_hazard(2025) == 0.0  # the series is held flat after 2024


def _customer(cid: str, smart: bool, commodity: str = "electricity") -> dict:
    return {"customer_id": cid, "acquisition_date": "2016-03-01", "smart_meter": smart,
            "commodity": commodity, "segment": "resi"}


def _read_types(feed: SimulatedReadFeed, customer: dict) -> list[str]:
    passed = feed.meter_type_for(customer)
    return [feed.read_for(customer["customer_id"], f"{y}-{m:02d}-28", passed, 300.0, 0).meter_type
            for y in range(2016, 2026) for m in range(1, 13)]


def test_the_switch_is_off_by_default_and_reads_are_untouched():
    """Defect: the exchange acts with the switch off, moving the world digest under the arms."""
    assert meter_reads.SMART_METER_EXCHANGE is False
    feed = SimulatedReadFeed()
    for i in range(200):
        cid = f"PROS-2016-{i:05d}"
        customer = _customer(cid, smart=False)
        assert feed.meter_type_for(customer) == "traditional"
        for period_end in ("2018-01-31", "2024-12-31"):
            assert feed.read_for(cid, period_end, "traditional", 300.0, 0) == simulate_read(
                cid, period_end, "traditional", 300.0, 0, commodity="electricity", aq_kwh=None,
                half_hourly=False, must_read_arm="register")


def test_with_the_switch_on_a_meter_reads_traditional_until_its_exchange_and_smart_after():
    """Defect: the read feed keeps the acquisition stamp, or flips a meter before its exchange date.

    The partition is asserted whole: some meters are exchanged, some never are, and a meter smart
    at acquisition stays smart. A guard that exchanged nothing, or everything, fails here.
    """
    feed = SimulatedReadFeed(smart_meter_exchange=True, base_seed=SEED)
    exchanged = never = 0
    for i in range(200):
        cid = f"PROS-2016-{i:05d}"
        types = _read_types(feed, _customer(cid, smart=False))
        event = smart_meter_installed_event(cid, SEED, dt.date(2016, 3, 1), False)
        if event is None:
            never += 1
            assert set(types) == {"traditional"}
            continue
        exchanged += 1
        first_smart = types.index("smart")
        assert set(types[:first_smart]) == {"traditional"} and set(types[first_smart:]) == {"smart"}
        y, m = 2016 + first_smart // 12, first_smart % 12 + 1
        assert f"{y}-{m:02d}-28" >= event.event_date
    assert exchanged and never, (exchanged, never)
    assert set(_read_types(feed, _customer("PROS-2016-SMART", smart=True))) == {"smart"}


def test_a_dual_fuel_homes_two_meters_are_exchanged_in_one_visit():
    """Defect: the gas leg `<id>g` draws its own exchange, so one home's meters change apart."""
    feed = SimulatedReadFeed(smart_meter_exchange=True, base_seed=SEED)
    for i in range(50):
        cid = f"PROS-2016-{i:05d}"
        assert (_read_types(feed, _customer(cid, smart=False))
                == _read_types(feed, _customer(f"{cid}g", smart=False, commodity="gas")))
