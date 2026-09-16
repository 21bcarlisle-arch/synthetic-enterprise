"""The headcount counterfactual's verdicts, against the three ways this seat read it wrongly.

THE DEFECT (2026-09-16, and every leg here was paid for by getting it wrong first). The harness in
`tools/headcount_counterfactual.py` grades a pre-registered prediction about what the census
headcount moves in the book. Its first version got three separate things wrong, and all three were
invisible while the grading logic lived inside `main()` beside a two-minute simulation:

1. **The kill line was on the TOTAL.** *"Total book kWh under 0.5% means the change never reached
   the settled book"* fired at n=150 (0.491%) and declared the wiring control worthless. It was
   FALSE -- the per-commodity split showed the change arriving plainly. Total kWh sums two fuels
   whose responses have OPPOSITE signs (electricity -5.5%, gas -0.05%), so it reads a real change
   as nothing happening.
2. **P1 was compared as a LEVEL against a band calibrated on the whole population.**
   `draw_premise_population(n, ...)` takes a different SAMPLE at each n rather than a subset, so
   the treatment strength varies with n: -4.9% at n=150 against -11.65% at n=1200. Grading a level
   from one experiment against a band from another compares two different things.
3. **P3 was reported as a SIGN off a number smaller than its own noise.** The gas leg read +0.302%
   (n=150), +0.098% (n=600), -0.047% (n=1200) and -0.489% (n=60). This seat took the one reading
   that matched its prediction and wrote "P3 HOLDS".

And under all three: at n=60 BOTH verdicts invert on the draw alone.

So these legs are about what the instrument may CLAIM, never about the arithmetic of the demand
path -- which has its own suites and was never in question.
"""
from __future__ import annotations

from tools import headcount_counterfactual as hc


def measured(*, head, total, elec, gas, gas_home_from=1000.0, gas_home_to=1000.0) -> dict:
    return {
        "premises": 600,
        "mean_headcount_control": 2.72,
        "mean_headcount_treated": 2.47,
        "headcount_move_pct": head,
        "total_kwh_control": 1.0,
        "total_kwh_treated": 1.0,
        "total_kwh_move_pct": total,
        "gas_kwh_move_pct": gas,
        "elec_kwh_move_pct": elec,
        "gas_per_home_control": gas_home_from,
        "gas_per_home_treated": gas_home_to,
    }


#: The real n=1200 run. Any leg below that claims to grade this must agree with what was published.
AT_N1200 = measured(head=-11.65, total=-1.541, elec=-5.546, gas=-0.046,
                    gas_home_from=9885.3, gas_home_to=9880.7)


def test_below_the_resolution_floor_it_grades_nothing(capsys):
    """The whole point. At n=60 both verdicts invert, so neither may be reported.

    Keyed to the FLOOR, not to n=60: a run at any size below it must refuse, because what the floor
    encodes is that the instrument cannot separate a weak treatment from a noisy one down there.
    """
    lines = hc.grade(AT_N1200, n=hc.RESOLUTION_FLOOR_PREMISES - 1)
    joined = "\n".join(lines)
    assert "NOT GRADED" in joined
    assert "resolution floor" in joined
    assert "P1 (" not in joined, "a refused run must not also print a P1 verdict"
    assert "P3 (" not in joined, "a refused run must not also print a P3 verdict"
    assert "P2 (margin): NOT GRADED" in joined, (
        "margin is unanswerable from the demand path at ANY n, and must say so even here"
    )
    del capsys


def test_at_or_above_the_floor_it_grades(capsys):
    """The other half of the partition -- the floor must be able to NOT fire.

    A guard that refuses everything passes every test asking whether it refuses correctly.
    """
    lines = hc.grade(AT_N1200, n=hc.RESOLUTION_FLOOR_PREMISES)
    # NOT the substring over the whole block: "P2 (margin): NOT GRADED HERE" is present at every n
    # and always should be, so a naive `not in joined` reds on the correct output.
    assert not any(ln.startswith("NOT GRADED") for ln in lines)
    joined = "\n".join(lines)
    assert "P1 (" in joined and "P3 (" in joined
    del capsys


def test_p1_is_graded_on_the_scaled_treatment_and_not_on_the_raw_level():
    """A level from a weak-treatment run must not be compared to a population-calibrated band.

    Same underlying elasticity, two treatment strengths: both must reach the same verdict. If the
    grading used the raw level, the weak run would read -0.49% and the strong one -1.54%, and only
    the arithmetic accident of where the band sits would decide whether they agreed.
    """
    weak = measured(head=-4.91, total=-0.491, elec=-2.413, gas=0.302)
    strong = measured(head=-11.65, total=-1.541, elec=-5.546, gas=-0.046)
    weak_line = next(ln for ln in hc.grade(weak, n=600) if ln.startswith("P1 ("))
    strong_line = next(ln for ln in hc.grade(strong, n=600) if ln.startswith("P1 ("))
    assert "REFUTED" in weak_line and "REFUTED" in strong_line
    assert "scales to" in weak_line, "the scaling must be shown, not just applied"

    # And it must be ABLE to say HOLDS -- a P1 that can only ever be refuted proves nothing.
    real = measured(head=-10.0, total=-3.0, elec=-8.0, gas=-0.5)
    assert "HOLDS" in next(ln for ln in hc.grade(real, n=600) if ln.startswith("P1 ("))


def test_the_kill_line_is_on_electricity_and_not_on_the_cancelling_total():
    """The exact false reading of 2026-09-16: a real change reported as never having arrived.

    Electricity moves 5.5%; the total moves 0.4% because gas cancels it. The old kill line fired on
    the total and called the wiring control worthless. The new one must not.
    """
    cancelling = measured(head=-11.65, total=-0.4, elec=-5.546, gas=+5.0)
    line = next(ln for ln in hc.grade(cancelling, n=600) if ln.startswith("KILL LINE"))
    assert "not breached" in line, (
        "a 5.5% electricity move was reported as 'the change never reached the book' because the "
        "total happened to cancel -- that is the defect this file exists for"
    )

    # ...and it must still be able to fire, on the leg that actually carries the effect.
    absent = measured(head=-11.65, total=-0.05, elec=-0.05, gas=-0.05)
    fired = next(ln for ln in hc.grade(absent, n=600) if ln.startswith("KILL LINE"))
    assert "BREACHED" in fired


def test_a_gas_reading_inside_the_noise_floor_is_not_reported_as_a_sign():
    """+0.098% was called 'P3 HOLDS'. The same quantity had already read -0.489% on another sample.

    Inside the floor the verdict must name the CANCELLATION and carry the caveat, whichever side of
    zero the reading happens to land on -- otherwise the note is decoration and the sign is still
    doing the talking.
    """
    for gas_to in (1000.1, 999.9):  # +0.01% and -0.01%, both inside the floor
        lines = hc.grade(measured(head=-11.65, total=-1.5, elec=-5.5, gas=-0.05,
                                  gas_home_from=1000.0, gas_home_to=gas_to), n=600)
        joined = "\n".join(lines)
        assert "REFUTED -- gas per home does not rise" in joined
        assert "noise floor" in joined
        assert "look identical here" in joined, (
            "the caveat must say that two effects netting to zero and one effect being absent are "
            "indistinguishable; without it the reader takes the verdict as a measured mechanism"
        )


def test_a_gas_move_outside_the_noise_floor_is_reported_as_a_sign():
    """The floor must not swallow a real effect -- that would be the mirror defect.

    A control that reports 'cannot resolve' for every input is as useless as one that reports a
    sign for every input, and this is the leg that tells them apart.
    """
    big_rise = measured(head=-11.65, total=-1.5, elec=-5.5, gas=2.0,
                        gas_home_from=1000.0, gas_home_to=1020.0)  # +2%
    joined = "\n".join(hc.grade(big_rise, n=600))
    assert "-> HOLDS" in joined
    assert "noise floor" not in joined


def test_a_treatment_that_moved_no_headcount_grades_nothing():
    """Fails closed on the one input that makes every ratio below meaningless.

    Not a division guard: a run whose two arms drew the same households has no treatment, and
    dividing by it would manufacture an elasticity out of rounding.
    """
    joined = "\n".join(hc.grade(measured(head=0.0, total=-1.5, elec=-5.5, gas=-0.05), n=600))
    assert "NOT GRADED" in joined and "no headcount" in joined
