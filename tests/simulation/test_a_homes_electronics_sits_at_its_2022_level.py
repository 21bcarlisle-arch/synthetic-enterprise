"""A home's electronics on-mode sits at HES's 2010-11 level carried to 2022, not at HES's own year.

HES (Intertek R66141) Tables 26 and 29 less standby: AV 478 + computing 193 = 671 kWh/yr per
household (651 at the low end). DESNZ ECUK 2023 Electrical Products tables carry each to 2022: AV
x0.52 (TVs to 2022, other consumer electronics held at its 2019, the last year published),
computing x0.70. Until 2026-10-08 the world sat at HES's 2010-11 level, ~300 kWh/yr above 2022.

The world's electronics load is linear in `_ELECTRONICS_KW_PER_PERSON`: measured over the 163
gas-heated no-PV homes (seed 17, C1 2022), 0.055 gave a mean of 673 kWh/yr, and 0.031 cut the mean
meter by 294. That measured slope is what turns the constant into kWh here; a year of traces per
test run would cost minutes.
"""

import pytest

import simulation.premise_trace as pt

HES_AV_ON_MODE = 478.0
HES_COMPUTING_ON_MODE = 193.0
ECUK_AV_RATIO_TO_2022 = 0.52
ECUK_COMPUTING_RATIO_TO_2022 = 0.70
WORLD_KWH_PER_UNIT_CONSTANT = 673.0 / 0.055


def _trended_2022_kwh() -> float:
    return HES_AV_ON_MODE * ECUK_AV_RATIO_TO_2022 + HES_COMPUTING_ON_MODE * ECUK_COMPUTING_RATIO_TO_2022


def test_the_worlds_electronics_year_is_hes_carried_to_2022():
    # Defect it catches: the constant drifting back to HES's 2010-11 level (0.055 gives 673).
    world = pt._ELECTRONICS_KW_PER_PERSON * WORLD_KWH_PER_UNIT_CONSTANT
    assert world == pytest.approx(_trended_2022_kwh(), rel=0.05)


def test_the_2022_level_is_a_fall_from_hes_not_a_rise():
    # Defect it catches: a ratio typed the wrong way up (e.g. 1/0.52) would move the target ABOVE
    # HES's own year and the first test would follow it there.
    assert _trended_2022_kwh() < 0.65 * (HES_AV_ON_MODE + HES_COMPUTING_ON_MODE)
