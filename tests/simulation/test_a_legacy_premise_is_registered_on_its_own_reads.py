"""THE DEFECT (2026-11-04): the BSCP504 s3.2.6.51 rule (a settled home's registry EAC is its own
reads) reached the fabric premises only. A legacy premise kept its drawn TDCV band as its registry
EAC while its meter recorded that band plus heating, EPC band and occupancy. On the a6b7a0fd47 book
all 15 drawn electric-heated homes behind INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER were legacy
premises (SYN-2016-355: 2,468.5 kWh registered, 15-20 MWh metered); the 10 on the fabric path
breached none.

ONE control over the partition, and the property it holds: the registry follows the meter, and the
meter does not follow the registry. A rule that skips legacy premises reds the first assert; a rule
that re-registers without moving the band to the world's map reds the demand assert (the demand
rescales to the new EAC and the registry chases it); a rule that re-registers a non-domestic point
reds the last.
"""

import simulation.run_phase2b as rp
from simulation.run_phase2b import _base_profile_eac, register_legacy_premises_on_their_own_reads

_DATES = [f"2016-{m:02d}-{d:02d}" for m in range(1, 13) for d in range(1, 29)] + \
    [f"2017-{m:02d}-{d:02d}" for m in range(1, 13) for d in range(1, 29)]
_HEATING_KWH_PER_DAY = 20.0  # an electric-heated home's term on top of its band


def _shape_fn_for(customer, cid):
    level = _base_profile_eac(customer)
    return lambda date_str: [level / 365.0 / 48 + _HEATING_KWH_PER_DAY / 48] * 48


def test_the_registry_follows_the_meter_and_the_meter_does_not_follow_the_registry():
    heated = {"customer_id": "SYN-T-STORAGE", "segment": "resi", "eac_kwh": 2468.5,
              "acquisition_date": "2016-01-01"}
    office = {"customer_id": "SYN-T-SME", "segment": "SME", "eac_kwh": 20000.0,
              "acquisition_date": "2016-01-01"}
    before = sum(sum(_shape_fn_for(heated, "SYN-T-STORAGE")(d)) for d in _DATES[:365])

    moved = list(register_legacy_premises_on_their_own_reads([heated, office], _shape_fn_for, _DATES))
    try:
        assert [m[0] for m in moved] == ["SYN-T-STORAGE"], moved
        assert abs(heated["eac_kwh"] - before) < 1.0, (heated["eac_kwh"], before)
        after = sum(sum(_shape_fn_for(heated, "SYN-T-STORAGE")(d)) for d in _DATES[:365])
        assert abs(after - before) < 1e-6, f"the world's demand moved with the registry: {before} -> {after}"
        assert _base_profile_eac(heated) == 2468.5
        assert office["eac_kwh"] == 20000.0
    finally:
        rp._WORLD_BASE_EAC_KWH.clear()
