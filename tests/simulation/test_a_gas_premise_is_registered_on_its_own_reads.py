"""THE DEFECT (2026-11-25): a gas premise's registry AQ was its drawn level, while the world settled
its meter on that level times the household's gas multiplier (0.12 for a heat-pump home). PROS-2021-0100
was handed 9,542.5 kWh against a meter drawing ~1,150, and the estimator held on it for five months
(docs/staging/SEAT_FINDING_THE_ESTIMATE_AGAINST_THE_METER_ON_F2C6979D01_IS_7_OF_4250_AND_ONE_IS_A_GAS_AQ_EIGHT_TIMES_ITS_METER_2026-11-25.md).

ONE control over the partition: the registry follows the meter, the meter does not follow the
registry, a non-domestic point is untouched, and a second run in the same process does not compound.
A rule that skips gas reds the first assert. One that leaves the drawn level off the world's map reds
the demand assert. One that averages after acquisition, not before, reds the trailing-window assert.
One that re-reads its own output as the drawn level reds the last.
"""

import simulation.run_phase2b as rp
from simulation.gas_settlement import GAS_HDD_REFERENCE_ANNUAL
from simulation.run_phase2b import _world_gas_aq, register_gas_premises_on_their_own_reads

_NORMAL_DAY = GAS_HDD_REFERENCE_ANNUAL / 365  # a cell exactly on the normal, every day


def _normal_cell(_date_str, _cid):
    return _NORMAL_DAY


def _normal_station(_days):
    return 1.0

_FITTED_ON = "2021-01-01"  # a heat pump replaces the boiler 181 days before acquisition
_OWN = round(9542.5 * (181 * 0.12 + 184 * 1.0) / 365, 1)  # the trailing year, part boiler


def _multiplier(cid, date_str):
    if cid == "PROS-T-HP":
        return 0.12 if date_str >= _FITTED_ON else 1.0
    return 1.25


def test_the_registry_aq_follows_the_meter_and_the_meter_does_not_follow_the_registry():
    heat_pump = {"customer_id": "PROS-T-HP", "segment": "resi", "aq_kwh": 9542.5,
                 "acquisition_date": "2021-07-01"}
    epc_e = {"customer_id": "SYN-T-E", "segment": "resi", "aq_kwh": 12000.0,
             "acquisition_date": "2016-01-01"}
    shop = {"customer_id": "SYN-T-SME", "segment": "SME", "aq_kwh": 40000.0,
            "acquisition_date": "2016-01-01"}
    try:
        moved = list(register_gas_premises_on_their_own_reads(
            [heat_pump, epc_e, shop], _multiplier, "2016-01-01",
            hdd_for=_normal_cell, station_departure_over=_normal_station))
        assert [m[0] for m in moved] == ["PROS-T-HP", "SYN-T-E"], moved
        # The year before acquisition, half of it on the boiler: the meter's own weather-normal year.
        assert abs(heat_pump["aq_kwh"] - _OWN) <= 0.1, heat_pump["aq_kwh"]
        # Acquired inside the run's first year: the first year is the window.
        assert abs(epc_e["aq_kwh"] - 15000.0) <= 0.1, epc_e["aq_kwh"]
        assert _world_gas_aq(heat_pump) == 9542.5, "the world's demand level moved with the registry"
        assert shop["aq_kwh"] == 40000.0 and _world_gas_aq(shop) == 40000.0
        list(register_gas_premises_on_their_own_reads(
            [heat_pump, epc_e], _multiplier, "2016-01-01",
            hdd_for=_normal_cell, station_departure_over=_normal_station))
        assert abs(heat_pump["aq_kwh"] - _OWN) <= 0.1 and _world_gas_aq(heat_pump) == 9542.5, \
            "a second run in the same process compounded the rewrite"
    finally:
        rp._WORLD_BASE_AQ_KWH.clear()
        rp._AQ_REWRITTEN.clear()


def test_the_aq_keeps_the_meters_own_climate_and_divides_out_only_the_station_year():
    """THE DEFECT (26 Nov 2026): the AQ was the meter's year on the national 1991-2020 normal, so a
    meter on a cell 10% warmer than normal was handed ~8.5% more than it uses in a normal year
    (docs/staging/done/SEAT_FINDING_IS_A_GAS_PREMISES_REGISTERED_AQ_ITS_FIRST_YEAR_OF_TRUE_USE_2026-11-26.md:
    first year median 0.915 of the AQ). Xoserve's AQ divides out only the STATION's departure from its
    normal (knowledge page s.5), so the meter's own offset stays in it.

    Case 1, a warm cell in a normal station year: the AQ is the cell's own year, 0.85 x 0.9 + 0.15 of
    the national-normal level. A rule that puts the meter back on the national normal reds it.
    Case 2, a year where the station ran 10% warm and the cell with it: the departure is divided out
    and the AQ is the normal-year level. A rule that hands over the raw read year reds it.
    """
    warm_cell = lambda _d, _c: 0.9 * _NORMAL_DAY  # noqa: E731
    try:
        for station, want in ((1.0, 12000.0 * (0.85 * 0.9 + 0.15)), (0.9, 12000.0)):
            premise = {"customer_id": "SYN-T-W", "segment": "resi", "aq_kwh": 12000.0,
                       "acquisition_date": "2016-01-01"}
            list(register_gas_premises_on_their_own_reads(
                [premise], lambda _c, _d: 1.0, "2016-01-01",
                hdd_for=warm_cell, station_departure_over=lambda _days, s=station: s))
            assert abs(premise["aq_kwh"] - want) <= 0.1, (station, premise["aq_kwh"], want)
            assert _world_gas_aq(premise) == 12000.0, "the world's demand level moved"
            rp._AQ_REWRITTEN.clear()
    finally:
        rp._WORLD_BASE_AQ_KWH.clear()
        rp._AQ_REWRITTEN.clear()


def test_the_gb_station_departure_is_the_observed_year_over_the_normal():
    """2016's GB year (ET 7.1, 2,021 HDD) over the 1991-2020 normal (2,060.9), and a year the
    table does not hold raises rather than taking the normal."""
    from datetime import date, timedelta

    import pytest

    from sim.weather_hdd import gb_hdd_departure_over
    days_2016 = [(date(2016, 1, 1) + timedelta(days=i)).isoformat() for i in range(366)]
    assert abs(gb_hdd_departure_over(days_2016) - 2021.0 / 2060.9) < 0.003
    with pytest.raises(KeyError):
        gb_hdd_departure_over(["2031-01-15"])
