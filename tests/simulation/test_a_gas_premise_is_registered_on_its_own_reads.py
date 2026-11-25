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
from simulation.run_phase2b import _world_gas_aq, register_gas_premises_on_their_own_reads

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
            [heat_pump, epc_e, shop], _multiplier, "2016-01-01"))
        assert [m[0] for m in moved] == ["PROS-T-HP", "SYN-T-E"], moved
        # The year before acquisition, half of it on the boiler: the meter's own weather-normal year.
        assert heat_pump["aq_kwh"] == _OWN, heat_pump["aq_kwh"]
        # Acquired inside the run's first year: the first year is the window.
        assert epc_e["aq_kwh"] == 15000.0, epc_e["aq_kwh"]
        assert _world_gas_aq(heat_pump) == 9542.5, "the world's demand level moved with the registry"
        assert shop["aq_kwh"] == 40000.0 and _world_gas_aq(shop) == 40000.0
        list(register_gas_premises_on_their_own_reads([heat_pump, epc_e], _multiplier, "2016-01-01"))
        assert (heat_pump["aq_kwh"], _world_gas_aq(heat_pump)) == (_OWN, 9542.5), \
            "a second run in the same process compounded the rewrite"
    finally:
        rp._WORLD_BASE_AQ_KWH.clear()
        rp._AQ_REWRITTEN.clear()
