"""Domestic hot water is modelled once, and the model reproduces the measurement it cites.

REUSE: tests/simulation/test_hot_water_has_one_implementation.py
CLASS: CUSTOM
INDEX: searched "hot water", "dhw", "premise trace", "occupancy", "litres".
       `tests/tools/test_hot_water_base.py` grades the PARAMETER against the measured marginal and
       knows nothing about production. `tests/simulation/test_premise_trace*.py` cover the trace's
       shape and events, not the volume relationship. Nothing compared the two implementations,
       which is exactly why they diverged.

THE DEFECT THIS EXISTS FOR
--------------------------
There were two hot-water models. `simulation/premise_trace` -- on the shipped settlement path --
used **40 litres per person with no fixed term at a 45 K rise**, under a comment citing SAP.
`tools/hot_water_base` used SAP's actual **36 + 25N at an implied 37.6 K**, sourced and corroborated
against 45,000 metered homes. The sourced one did not run.

**They agree EXACTLY at the average occupancy and nowhere else**: 40 x 2.4 = 96 litres and
36 + 25 x 2.4 = 96 litres. That is why it survived -- any check at the mean passes. Production
emitted 1.4-1.6x the measured median and gave a four-versus-two ratio of 2.00 where the standard it
cited gives 1.58, putting a four-person household above the measured p75 for the whole stock.

So `test_THE_MODEL_IS_NOT_CHECKED_ONLY_AT_THE_MEAN` is the control that would have caught it, and it
is deliberately the first one here.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from simulation import premise_trace as pt  # noqa: E402
from tools import hot_water_base as hw  # noqa: E402

#: DESNZ March 2024, 45,000 metered homes on gas combi boilers. Median daily hot-water GAS at the
#: two published seasonal points, and the interquartile range at each.
_MEASURED_MEDIAN_GAS = (3.9, 4.5)
_MEASURED_IQR = (1.9, 8.0)          # widest published bounds across the two seasons


def _metered_gas_kwh_per_day(people: float) -> float:
    """What production actually emits for a gas-heated household of this size."""
    thermal = pt.dhw_daily_litres(people) * pt._DHW_KWH_PER_LITRE
    return thermal / pt._DHW_COMBI_EFFICIENCY


def test_THE_MODEL_IS_NOT_CHECKED_ONLY_AT_THE_MEAN():
    """The control the divergence needed, and the reason it is first.

    Two models that agree at the reference occupancy and nowhere else pass every mean-based check
    ever written. This asserts the SHAPE across the whole range a real book contains."""
    low, high = _MEASURED_IQR
    for people in (1, 2, 3, 4, 5):
        emitted = _metered_gas_kwh_per_day(people)
        assert low <= emitted <= high, (
            f"a {people}-person household is given {emitted:.2f} kWh/day of hot-water gas, outside "
            f"the measured interquartile range {low}-{high}. The OLD model put a four-person "
            "household at 10.45, above the measured p75 for the entire stock.")


def test_THE_REFERENCE_OCCUPANCY_REPRODUCES_THE_MEASURED_MEDIAN():
    """The anchor itself, and it tests the DERIVATION rather than the volume.

    WHAT THIS CANNOT CATCH, MEASURED RATHER THAN ASSUMED: restoring the old 40-litres-no-fixed-term
    model leaves this control GREEN. That is not a weakness to fix, it is the finding restated --
    the rise is derived from the volume AT THE REFERENCE OCCUPANCY, and both models give 96 litres
    there, so the derivation self-compensates and the median comes out right either way. A poison
    round confirmed it: the old constants red `test_THE_MODEL_IS_NOT_CHECKED_ONLY_AT_THE_MEAN` and
    `test_THE_OCCUPANCY_RELATIONSHIP_IS_SUB_LINEAR` and leave this one passing.

    So this fails only if the derivation is replaced by a chosen number, which is what it is for."""
    emitted = _metered_gas_kwh_per_day(pt._DHW_REFERENCE_OCCUPANCY)
    low, high = _MEASURED_MEDIAN_GAS
    assert low <= emitted <= high, (
        f"at the reference occupancy the model emits {emitted:.2f} kWh/day against a measured "
        f"median of {low}-{high}. The old model emitted 6.27 -- 1.4-1.6x the measurement.")


def test_THE_OCCUPANCY_RELATIONSHIP_IS_SUB_LINEAR_as_the_cited_standard_says():
    """SAP's structure is a fixed draw-off plus a per-person one, so four people use about 1.58x
    what two do. The old model was strictly proportional at 2.00 while citing SAP -- it quoted the
    standard and implemented a relationship the standard does not contain."""
    ratio = pt.dhw_daily_litres(4) / pt.dhw_daily_litres(2)
    assert 1.45 < ratio < 1.75, (
        f"four people use {ratio:.3f}x the hot water of two. Strict proportionality gives 2.00 and "
        "is what this replaced; a ratio at or near it means the fixed term has gone.")
    assert pt._DHW_FIXED_LITRES_PER_DAY > 0.0, (
        "the fixed draw-off is zero, so the relationship is proportional again whatever the "
        "per-person figure says")


def test_THE_TEMPERATURE_RISE_IS_DERIVED_AND_PHYSICALLY_PLAUSIBLE():
    """It is computed from the measurement, not chosen -- and the fact that it lands on a blended
    draw-off temperature is the check that the frame is right rather than a coincidence.

    A shower runs at about 40 C. The old 45 K was a STORAGE temperature applied to a DELIVERED
    volume, which is one of the two reasons the old model over-read."""
    delivered_c = 10.0 + pt._DHW_DELTA_T_K
    assert 35.0 <= delivered_c <= 50.0, (
        f"the derived rise implies water delivered at {delivered_c:.1f} C from a 10 C main. "
        "Outside a plausible blended draw-off range the anchoring is wrong, not merely imprecise.")


def test_THE_INSTRUMENT_DOES_NOT_CARRY_ITS_OWN_COPY():
    """One implementation. `tools/hot_water_base` imports production's constants rather than
    re-declaring them, so the two cannot drift apart again -- which they did, silently, for as long
    as both existed."""
    assert hw.HOT_WATER_FIXED_LITRES_PER_DAY is pt._DHW_FIXED_LITRES_PER_DAY
    assert hw.HOT_WATER_LITRES_PER_PERSON_PER_DAY is pt._DHW_LITRES_PER_PERSON_DAY
    assert hw.REFERENCE_OCCUPANCY is pt._DHW_REFERENCE_OCCUPANCY

    for people in (1, 2, 4, 5):
        assert hw.HOT_WATER_FIXED_LITRES_PER_DAY + \
            hw.HOT_WATER_LITRES_PER_PERSON_PER_DAY * people == \
            pytest.approx(pt.dhw_daily_litres(people)), (
                "the instrument and production disagree about the volume for a "
                f"{people}-person household")
