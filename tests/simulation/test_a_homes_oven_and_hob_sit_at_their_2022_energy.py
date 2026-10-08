"""An electric oven and hob use HES's 2010-11 energy carried to 2022, not HES's own year.

DESNZ ECUK 2023 Electrical Products tables (A1 GWh over A2 stock, refreshed 2017): an oven falls
120 -> 96 kWh/yr per appliance from 2011 to 2022 (x0.80), a hob 232 -> 194 (x0.84). Only the
ratios are carried, because ECUK's levels are modelled and are not HES's. The world's oven and hob
are a power at nameplate times a duration, so the ratio lands on the duration.

Paired over 2,921 gas-heated no-PV homes (seeds 17, 29, 41; C1 2022) the cut took 61 kWh off the
annual median, inside the filed 35-65. That run is in
docs/staging/SEAT_FINDING_A_GAS_HOMES_ELECTRICITY_LEVEL_SPLIT_INTO_THE_CRISIS_AND_A_LEVEL_EXCESS_2026-10-08.md.
"""

import pytest

import simulation.premise_trace as pt

HES_KWH_PER_USE = {"oven": 2.0 * 0.75, "hob": 1.8 * 0.35}
ECUK_RATIO_TO_2022 = {"oven": 96 / 120, "hob": 194 / 232}


def _spec(name: str) -> pt.ApplianceSpec:
    (spec,) = [s for s in pt.APPLIANCE_CATALOGUE if s.name == name]
    return spec


@pytest.mark.parametrize("name", ["oven", "hob"])
def test_each_use_is_hes_carried_to_2022_by_ecuk(name):
    # Defect it catches: the row drifting back to HES's 2010-11 energy (oven 1.50, hob 0.63 kWh).
    spec = _spec(name)
    assert spec.power_kw * spec.duration_hours == pytest.approx(
        HES_KWH_PER_USE[name] * ECUK_RATIO_TO_2022[name], rel=0.01
    )


@pytest.mark.parametrize("name", ["oven", "hob"])
def test_the_ratio_shortens_the_use_and_leaves_nameplate_and_frequency(name):
    # Defect it catches: the ratio typed the wrong way up (1/0.80), or landed on events_per_day,
    # which would also move the evening timing draw the paired run held fixed.
    spec = _spec(name)
    assert spec.power_kw * spec.duration_hours < HES_KWH_PER_USE[name]
    assert (spec.power_kw, spec.events_per_day) == {"oven": (2.0, 0.55), "hob": (1.8, 0.70)}[name]
