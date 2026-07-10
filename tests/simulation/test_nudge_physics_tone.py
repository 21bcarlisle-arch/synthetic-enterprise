"""NUDGE_PHYSICS.md remaining mechanism: debt-collection letter tone/framing
(2026-07-10). Tests simulation/nudge_physics.py's ToneSusceptibility/
tone_susceptibility_for/tone_effectiveness_multiplier -- same style as
test_nudge_physics.py's Layer 1 framing tests.
"""
from simulation.nudge_physics import (
    ToneSusceptibility,
    tone_susceptibility_for,
    tone_effectiveness_multiplier,
)


def test_tone_susceptibility_is_deterministic():
    assert tone_susceptibility_for("C1") == tone_susceptibility_for("C1")


def test_tone_susceptibility_distribution_roughly_matches_weights():
    from collections import Counter
    counts = Counter(tone_susceptibility_for("C" + str(i)) for i in range(1, 1001))
    total = sum(counts.values())
    empathetic_frac = counts[ToneSusceptibility.EMPATHETIC_RESPONSIVE] / total
    firm_frac = counts[ToneSusceptibility.FIRM_RESPONSIVE] / total
    neutral_frac = counts[ToneSusceptibility.NEUTRAL] / total
    assert 0.35 < empathetic_frac < 0.55
    assert 0.25 < firm_frac < 0.45
    assert 0.10 < neutral_frac < 0.30
    assert abs((empathetic_frac + firm_frac + neutral_frac) - 1.0) < 1e-9


def test_matched_tone_gives_uplift():
    found_uplift = False
    for i in range(1, 200):
        cid = "C" + str(i)
        susc = tone_susceptibility_for(cid)
        if susc == ToneSusceptibility.EMPATHETIC_RESPONSIVE:
            mult = tone_effectiveness_multiplier(cid, "empathetic_toned")
            assert mult > 1.0
            assert mult <= 1.10 + 1e-9  # Cabinet Office/BIT anchor: +3 to +10pp
            found_uplift = True
        elif susc == ToneSusceptibility.FIRM_RESPONSIVE:
            mult = tone_effectiveness_multiplier(cid, "firm_toned")
            assert mult > 1.0
            assert mult <= 1.10 + 1e-9
            found_uplift = True
    assert found_uplift


def test_mismatched_tone_gives_no_uplift():
    for i in range(1, 200):
        cid = "C" + str(i)
        susc = tone_susceptibility_for(cid)
        if susc == ToneSusceptibility.EMPATHETIC_RESPONSIVE:
            assert tone_effectiveness_multiplier(cid, "firm_toned") == 1.0
        elif susc == ToneSusceptibility.FIRM_RESPONSIVE:
            assert tone_effectiveness_multiplier(cid, "empathetic_toned") == 1.0


def test_neutral_tone_susceptibility_never_uplifted():
    for i in range(1, 500):
        cid = "C" + str(i)
        if tone_susceptibility_for(cid) == ToneSusceptibility.NEUTRAL:
            assert tone_effectiveness_multiplier(cid, "firm_toned") == 1.0
            assert tone_effectiveness_multiplier(cid, "empathetic_toned") == 1.0


def test_tone_uplift_is_deterministic_across_calls():
    mult1 = tone_effectiveness_multiplier("C42", "firm_toned")
    mult2 = tone_effectiveness_multiplier("C42", "firm_toned")
    assert mult1 == mult2
