"""Two occupancy patterns that differ only in level do not differ in shape.

Director, 2026-09-08, refusing a published figure: *"I don't believe single and family households
have the same daily electricity shape... 'identical to four decimals' is the tell. Genuinely
different populations don't agree to four decimal places. That's the signature of two shapes
computed from the same underlying object rather than measured independently."*

He was right. `occupancy_multiplier` carries a per-pattern shape term, so the world is not simply
rescaling one curve -- but `family` and `single` are NEARLY PROPORTIONAL, and a proportional curve
is the same shape at a different level. The measurement was honest and the finding was an artefact
of what the code does rather than what households do.
"""
from __future__ import annotations

import pytest

from simulation import demand_model as dm

#: Bands `occupancy_multiplier` actually distinguishes. THREE, and the absence of a fourth is the
#: point: there is no after-school band, so a family with young children cannot carry the
#: morning-and-after-school signature the director described. `children_count` is documented in that
#: function as not moving the shape at all.
BANDS = ("morning", "day", "evening")

#: How far two patterns' multiplier ratios must spread before they are genuinely different SHAPES
#: rather than the same shape at different levels. Proportional vectors have ratio spread exactly
#: zero; `elderly` against `single` spreads 0.72; `family` against `single` spreads 0.033.
SHAPE_DIFFERENCE_FLOOR = 0.15

#: PAIRS KNOWN TO DIFFER IN LEVEL ONLY, declared so the defect cannot return silently. This is a
#: REGISTER OF A KNOWN DEFECT, not a permission: a pair listed here is one the world cannot tell
#: apart in shape, and every entry should eventually be removed by giving the pair a real curve.
LEVEL_ONLY_PAIRS = {("family", "single")}


def _multipliers(pattern: str) -> dict[str, float]:
    """The pattern's multiplier in each band, read from the function rather than restated."""
    return {
        "morning": dm.occupancy_multiplier(pattern, next(iter(dm._MORNING_PERIODS))),
        "evening": dm.occupancy_multiplier(pattern, next(iter(dm._EVENING_PERIODS))),
        "day": dm.occupancy_multiplier(
            pattern, next(p for p in range(1, 49)
                          if p not in dm._MORNING_PERIODS and p not in dm._EVENING_PERIODS)),
    }


def _ratio_spread(a: str, b: str) -> float:
    left, right = _multipliers(a), _multipliers(b)
    ratios = [left[band] / right[band] for band in BANDS]
    return max(ratios) - min(ratios)


@pytest.mark.parametrize("pair", [("elderly", "single"), ("elderly", "family")])
def test_A_PATTERN_THAT_CLAIMS_A_DIFFERENT_SHAPE_MUST_HAVE_ONE(pair):
    """A pattern whose multipliers are proportional to another's is the SAME SHAPE at a different
    level, and a share is scale-invariant so nothing downstream can tell them apart. `elderly` is
    the only pattern that genuinely reshapes -- its daytime multiplier sits ABOVE its evening one,
    which no rescaling can produce."""
    spread = _ratio_spread(*pair)
    assert spread >= SHAPE_DIFFERENCE_FLOOR, (
        f"{pair[0]} and {pair[1]} have multiplier ratios spreading only {spread:.3f}; they are "
        "proportional, so they are the same curve at different levels")


def test_THE_LEVEL_ONLY_PAIRS_ARE_DECLARED_and_still_level_only():
    """THE DEFECT, HELD AS A REGISTER RATHER THAN HIDDEN. `family` and `single` differ by ratios
    1.10 / 1.133 / 1.12 -- a spread of 0.033 -- so they produce curves whose maximum normalised
    difference is 0.0005 while their totals differ 11.9 kWh against 13.3.

    If someone gives the pair a real curve this test goes red and the entry is removed, which is
    the point: the register shrinks as the world gets better, and it cannot quietly grow."""
    for a, b in LEVEL_ONLY_PAIRS:
        spread = _ratio_spread(a, b)
        assert spread < SHAPE_DIFFERENCE_FLOOR, (
            f"{a} and {b} now spread {spread:.3f} and are no longer level-only -- remove them from "
            "LEVEL_ONLY_PAIRS, and say so, because the world just got a real shape distinction")


def test_NO_UNDECLARED_PAIR_IS_LEVEL_ONLY():
    """The class guard. Any pair that is proportional and NOT on the register is the defect
    returning under a new name."""
    patterns = ("single", "family", "elderly")
    for i, a in enumerate(patterns):
        for b in patterns[i + 1:]:
            if (a, b) in LEVEL_ONLY_PAIRS or (b, a) in LEVEL_ONLY_PAIRS:
                continue
            assert _ratio_spread(a, b) >= SHAPE_DIFFERENCE_FLOOR, (
                f"{a} and {b} are proportional and undeclared -- either give them a real curve or "
                "add them to LEVEL_ONLY_PAIRS so the gap is visible")


def test_THERE_IS_NO_AFTER_SCHOOL_BAND_and_the_absence_is_recorded():
    """The director described a family with young children as having a morning peak AND an
    after-school peak. The model has three bands and no fourth, so that signature has nowhere to
    live -- which is a limit of the vocabulary, not a finding about households."""
    assert len(BANDS) == 3
    source = (dm.__file__)
    with open(source, encoding="utf-8") as fh:
        text = fh.read()
    assert "does not currently move the shape" in text, (
        "children are documented as not moving the shape; if that changes, this control and the "
        "band list must change with it")
