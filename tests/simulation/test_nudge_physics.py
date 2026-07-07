from simulation.nudge_physics import (
    FramingSusceptibility,
    susceptibility_for,
    framing_effectiveness_multiplier,
)


def test_susceptibility_is_deterministic():
    assert susceptibility_for("C1") == susceptibility_for("C1")


def test_susceptibility_distribution_roughly_matches_weights():
    from collections import Counter
    counts = Counter(susceptibility_for("C" + str(i)) for i in range(1, 1001))
    total = sum(counts.values())
    loss_frac = counts[FramingSusceptibility.LOSS_AVERSE] / total
    gain_frac = counts[FramingSusceptibility.GAIN_RESPONSIVE] / total
    neutral_frac = counts[FramingSusceptibility.NEUTRAL] / total
    assert 0.35 < loss_frac < 0.55
    assert 0.25 < gain_frac < 0.45
    assert 0.10 < neutral_frac < 0.30
    assert abs((loss_frac + gain_frac + neutral_frac) - 1.0) < 1e-9


def test_matched_framing_gives_uplift():
    found_uplift = False
    for i in range(1, 200):
        cid = "C" + str(i)
        susc = susceptibility_for(cid)
        if susc == FramingSusceptibility.LOSS_AVERSE:
            mult = framing_effectiveness_multiplier(cid, "loss_framed")
            assert mult > 1.0
            assert mult <= 1.35 + 1e-9
            found_uplift = True
        elif susc == FramingSusceptibility.GAIN_RESPONSIVE:
            mult = framing_effectiveness_multiplier(cid, "gain_framed")
            assert mult > 1.0
            assert mult <= 1.35 + 1e-9
            found_uplift = True
    assert found_uplift


def test_mismatched_framing_gives_no_uplift():
    for i in range(1, 200):
        cid = "C" + str(i)
        susc = susceptibility_for(cid)
        if susc == FramingSusceptibility.LOSS_AVERSE:
            assert framing_effectiveness_multiplier(cid, "gain_framed") == 1.0
        elif susc == FramingSusceptibility.GAIN_RESPONSIVE:
            assert framing_effectiveness_multiplier(cid, "loss_framed") == 1.0


def test_neutral_susceptibility_never_uplifted():
    for i in range(1, 500):
        cid = "C" + str(i)
        if susceptibility_for(cid) == FramingSusceptibility.NEUTRAL:
            assert framing_effectiveness_multiplier(cid, "loss_framed") == 1.0
            assert framing_effectiveness_multiplier(cid, "gain_framed") == 1.0


def test_uplift_is_deterministic_across_calls():
    mult1 = framing_effectiveness_multiplier("C42", "loss_framed")
    mult2 = framing_effectiveness_multiplier("C42", "loss_framed")
    assert mult1 == mult2
