"""The curve-position split's inversion is exact, and its censoring is declared.

Subject: `tools/split_price_response_by_curve_position.py`, which answers the question C3's
pre-registration left owed -- *did the departure level move because of where households sat on
`_savings_to_rate`'s piecewise curve?* -- and answers it NO: within a price side every segment
carries the same sign, so curve position sets the size of a household's move and the company's own
price side sets its direction.

WHY THIS FILE EXISTS AT ALL. The tool recovers "how many pounds were on this household's table" by
INVERTING `churn_position_multiplier`, because the captured factor tables carry the response and
not the bill. An inversion is exactly the kind of code that is silently wrong: it agrees with
itself, produces plausible numbers, and nothing downstream can tell. The first draft WAS silently
wrong -- it extrapolated the last graduated segment across the jump discontinuity at 400 GBP and
reported a mean of 520 for a bucket whose every member is censored at 400. That defect reached a
printed table and was caught by printing the curve at real inputs, not by any test. This is the
test that would have caught it.

R15: every control here names the mutation that must make it fire.
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import pytest

import tools.split_price_response_by_curve_position as split
from simulation.market_switching_propensity import (
    _CALIBRATED_SAVINGS_CEILING_GBP,
    _MAX_RATE,
    _PARITY_RATE,
    _savings_to_rate,
    churn_position_multiplier,
)

#: Bills and differentials spanning both branches of `churn_position_multiplier`, every segment of
#: `_savings_to_rate`, and the extrapolation above the calibrated ceiling. Chosen to CROSS the
#: boundaries rather than to sit inside them -- a round-trip that never approaches a segment edge
#: cannot see an off-by-one-segment inversion, which is the defect that actually happened.
_BILLS = (400.0, 900.0, 1700.0, 3200.0)
_DIFFERENTIALS = (-0.45, -0.30, -0.15, -0.08, -0.03, -0.01, 0.0, 0.01, 0.05, 0.12, 0.25, 0.42)

#: The tool reads the response as the captured tables store it: rounded to 6 decimals.
_CAPTURED_DECIMALS = 6


def test_the_inversion_recovers_the_pounds_the_forward_function_was_given():
    """MUTATION: move any segment boundary in `pounds_on_the_table` -- or restore the first
    draft's `rate < _MAX_RATE` test in place of `rate >= _LAST_GRADUATED_RATE` -- and this fires.

    THE ROUND TRIP IS THE ONLY THING THAT CAN CHECK AN INVERSION. `pounds_on_the_table` is asserted
    against `churn_position_multiplier` itself, not against a table of expected answers: a
    recalibration of `_savings_to_rate` moves both together and this stays green, while an
    inversion that stops being the forward function's inverse goes red. Keyed to the property.

    Tolerance is 1 GBP because the captured response carries only 6 decimals; the recovered pounds
    inherit that rounding through a slope of order 3e-4 per GBP.
    """
    checked = 0
    for bill in _BILLS:
        for differential in _DIFFERENTIALS:
            response = round(churn_position_multiplier(differential, bill), _CAPTURED_DECIMALS)
            recovered, censored = split.pounds_on_the_table(response, differential)
            expected = abs(differential) * bill
            if censored:
                assert recovered == _CALIBRATED_SAVINGS_CEILING_GBP
                assert expected >= _CALIBRATED_SAVINGS_CEILING_GBP, (
                    f"differential={differential} bill={bill}: reported CENSORED at {expected:.1f} "
                    f"GBP, below the {_CALIBRATED_SAVINGS_CEILING_GBP} GBP shelf -- the inversion "
                    f"is discarding a value it could have recovered"
                )
            else:
                assert recovered == pytest.approx(expected, abs=1.0), (
                    f"differential={differential} bill={bill}: forward gave {response}, inverse "
                    f"recovered {recovered:.1f} GBP against {expected:.1f} GBP put in"
                )
            checked += 1
    assert checked == len(_BILLS) * len(_DIFFERENTIALS)


def test_the_saturated_shelf_is_declared_censored_and_never_reported_as_a_value():
    """MUTATION: return `censored=False` on the shelf, or return the extrapolated 520 the first
    draft produced, and this fires.

    THE DEFECT THAT REACHED A PRINTED TABLE. On the cheaper side `_savings_to_rate` is FLAT at
    `_MAX_RATE` above 400 GBP, so every household with a perceived saving of 400 GBP or more
    produces the identical response and the pounds are UNRECOVERABLE -- the answer is a floor. A
    tool that returns a number there is publishing a censored quantity as a measured one, and the
    reader has no way to know. So the flag is the assertion, not the value.

    The dearer side has no shelf: `churn_position_multiplier` keeps climbing at the last informed
    slope, which is invertible, so those must NOT be censored. Both directions are checked --
    a flag that is always True is as useless as one that is never set.
    """
    # Cheaper and deep into saturation: unrecoverable, must say so.
    for saving in (400.0, 600.0, 1200.0):
        response = round(churn_position_multiplier(-saving / 1700.0, 1700.0), _CAPTURED_DECIMALS)
        pounds, censored = split.pounds_on_the_table(response, -saving / 1700.0)
        assert censored, f"a perceived saving of {saving} GBP sits on the flat shelf and cannot "
        assert pounds == _CALIBRATED_SAVINGS_CEILING_GBP

    # Cheaper but below the shelf: recoverable, must NOT be flagged.
    for saving in (50.0, 150.0, 300.0, 399.0):
        response = round(churn_position_multiplier(-saving / 1700.0, 1700.0), _CAPTURED_DECIMALS)
        _pounds, censored = split.pounds_on_the_table(response, -saving / 1700.0)
        assert not censored, (
            f"a perceived saving of {saving} GBP is on a graduated segment and IS recoverable; "
            f"flagging it censored throws away a measurement"
        )

    # Dearer above the ceiling: the extrapolation is invertible, so nothing is censored.
    for shortfall in (500.0, 900.0):
        differential = shortfall / 1700.0
        response = round(churn_position_multiplier(differential, 1700.0), _CAPTURED_DECIMALS)
        pounds, censored = split.pounds_on_the_table(response, differential)
        assert not censored
        assert pounds == pytest.approx(shortfall, abs=1.0)


def test_the_curve_really_does_jump_at_the_ceiling_which_is_why_the_inversion_must_gap_it():
    """MUTATION: make `_savings_to_rate` continuous at 400 GBP and this fires.

    NOT A TEST OF THE TOOL BUT OF ITS PREMISE, and it is here because the tool's correctness
    depends on it. `_savings_to_rate` steps from 0.18 to 0.22 at exactly 400 GBP, so rates in
    [0.18, 0.22) are UNREACHABLE by the forward function. That gap is why the inversion must not
    run the last graduated formula up to `_MAX_RATE` -- doing so maps the shelf onto a fictitious
    520 GBP. If the curve is ever made continuous this test goes red and the inversion's gapping
    logic must be revisited rather than silently left in place.
    """
    assert _savings_to_rate(400.0 - 1e-9) == pytest.approx(0.18, abs=1e-6)
    assert _savings_to_rate(400.0) == _MAX_RATE
    assert _MAX_RATE - _savings_to_rate(400.0 - 1e-9) == pytest.approx(0.04, abs=1e-6)
    assert split._LAST_GRADUATED_RATE < _MAX_RATE, (
        "the inversion's cut-off must sit BELOW _MAX_RATE, or the shelf is inverted through a "
        "formula that does not apply there"
    )


def test_within_a_price_side_the_response_moves_monotonically_with_perceived_pounds():
    """THE FINDING'S OWN CLAIM, HELD AS A PROPERTY. MUTATION: flip the expected direction for
    either side, and this fires.

    This is what refuted the C3 write-up's saturation hypothesis. `churn_position_multiplier` is
    monotone in the pounds within a side, so changing a household's PERCEIVED bill can only move
    its response one way: fewer perceived pounds makes a household MORE switchy where the company
    undercuts the market (the saving that was holding them shrinks) and LESS switchy where the
    company prices above it (the shortfall driving them away shrinks). Curve position therefore
    sets the SIZE of the move and cannot set its DIRECTION -- which is why the aggregate sign is a
    fact about the company's price position and not about the curve.

    Measured over the two committed captures: 422 decisions moved, ZERO violations.

    Keyed to the property, not to today's answer: it asserts the direction rule holds, never that
    the totals are +100.75 and -53.99. A re-capture that changes every number passes; an inversion
    or a seam that breaks the monotone relationship does not.
    """
    pairs = split.load_pairs(split.DEFAULT_BASELINE, split.DEFAULT_ARM)
    assert len(pairs) >= 400, (
        f"only {len(pairs)} paired decisions -- a split over an emptied population reports a "
        f"constant PASS"
    )
    moved = violations = 0
    for pair in pairs:
        d_pounds = pair["pounds_arm"] - pair["pounds_base"]
        d_response = pair["arm"]["sim_price_response"] - pair["base"]["sim_price_response"]
        if abs(d_pounds) < 1e-9 or abs(d_response) < 1e-9:
            continue
        moved += 1
        cheaper = pair["arm_side"].startswith("CHEAPER")
        expect_more_switchy = (d_pounds < 0) if cheaper else (d_pounds > 0)
        if (d_response > 0) != expect_more_switchy:
            violations += 1
    assert moved >= 300, f"only {moved} decisions moved; too few to hold the direction rule"
    assert violations == 0, (
        f"{violations} of {moved} moved decisions break the direction rule. Either the inversion "
        f"is no longer the inverse of `churn_position_multiplier`, or the seam that computes the "
        f"perceived bill has stopped being monotone in the pounds -- and if the latter, the "
        f"finding that C3's sign is the company's price side needs re-deriving, not patching."
    )


def test_the_split_runs_over_the_committed_captures_and_declares_what_it_dropped():
    """MUTATION: drop the unmatched-decision line, or make `load_pairs` difference against a
    missing decision instead of skipping it, and this fires.

    A price change RE-TIMES some renewals, so the two captures do not hold the same decisions.
    Differencing a decision against nothing is how a re-timing gets published as an attrition
    effect, and a silent drop reads as "covered everything" when it did not. So the tool must
    report the count it dropped, and the population must be the intersection.
    """
    out = io.StringIO()
    with redirect_stdout(out):
        assert split.main(["split_price_response_by_curve_position"]) == 0
    text = out.getvalue()

    assert "dropped as unmatched" in text, (
        "the split no longer says how many decisions it dropped; a silent truncation reads as "
        "full coverage"
    )
    for expected in ("CHEAPER", "DEARER", "SATURATED", "cens", "Violations"):
        assert expected in text, f"the split's report no longer carries {expected!r}"

    pairs = split.load_pairs(split.DEFAULT_BASELINE, split.DEFAULT_ARM)
    keys = {(p["base"]["customer_id"], p["base"]["event_date"]) for p in pairs}
    assert len(keys) == len(pairs), "load_pairs returned the same decision twice"
    for pair in pairs:
        assert pair["base"]["customer_id"] == pair["arm"]["customer_id"]
        assert pair["base"]["event_date"] == pair["arm"]["event_date"]


def test_every_paired_decision_lands_in_exactly_one_segment_and_one_side():
    """MUTATION: overlap two `_SEGMENTS` ranges, or drop the `>=400` catch-all, and this fires.

    A household that falls through the segment table would be silently absent from every bucket
    while still counting in the side total, so the columns would stop summing to the total they
    sit under -- the quiet way a decomposition stops being a decomposition.
    """
    pairs = split.load_pairs(split.DEFAULT_BASELINE, split.DEFAULT_ARM)
    names = [name for _lo, _hi, name in split._SEGMENTS]
    assert len(set(names)) == len(names), "two segments share a label; buckets would merge"

    ranges = {name: (lo, hi) for lo, hi, name in split._SEGMENTS}
    per_segment: dict[str, int] = {name: 0 for name in names}
    for pair in pairs:
        assert pair["segment"] in per_segment, (
            f"decision at {pair['pounds_base']:.1f} GBP fell outside every segment"
        )
        # MEMBERSHIP IS RANGE-CHECKED, not merely non-empty. `segment_of` ends in a catch-all
        # `return _SEGMENTS[-1][2]`, so deleting the `>=400` bucket does NOT leave a decision
        # unfiled -- it quietly files every saturated household under `250-400`, and a test that
        # only counted members stayed green through exactly that. Proven: with the last segment
        # removed, a 900 GBP decision reports as `250-400 flattening`. The label must therefore
        # be checked against the range it names.
        lo, hi = ranges[pair["segment"]]
        assert lo <= pair["pounds_base"] < hi, (
            f"a decision at {pair['pounds_base']:.1f} GBP is filed under {pair['segment']!r}, "
            f"whose range is [{lo}, {hi}). The segment table no longer covers the population and "
            f"the catch-all is silently absorbing what it dropped."
        )
        per_segment[pair["segment"]] += 1
        assert pair["arm_side"] in (
            "CHEAPER (we undercut the market)",
            "DEARER (we price above it)",
        )
    assert sum(per_segment.values()) == len(pairs), (
        "the segments do not partition the population -- the columns no longer sum to the total"
    )
    assert all(n > 0 for n in per_segment.values()), (
        f"an empty segment: {per_segment}. A bucket with no members cannot show a sign, and the "
        f"claim that every segment within a side agrees would be vacuous for it"
    )


def test_the_side_is_read_from_the_price_position_and_not_from_the_response(tmp_path):
    """MUTATION: classify the side by `sim_price_response > 1.0` instead of by the differential,
    and this fires -- but ONLY on the crafted rows below, and that is the point of them.

    THE MUTATION DOES NOT FIRE ON REAL DATA, AND I ESTABLISHED THAT RATHER THAN ASSUMING THE
    FLATTERING ANSWER. `churn_position_multiplier` is monotone in the differential and passes
    through EXACTLY 1.0 at parity, so `response > 1.0` and `differential > 0.0` agree on every row
    the world can produce -- checked over 4,004 (differential, bill) points, zero disagreements.
    Classifying by the response is therefore an EQUIVALENCE on today's captures, not a defect the
    real tables can expose.

    It is still the wrong source, and this leg still earns its place: the response is the quantity
    the split EXPLAINS, so deriving the side from it would make the finding circular -- the two
    sides would be guaranteed to differ in response because they were defined by it. The
    equivalence is a property of the current seam, not a guarantee; C3 itself changes which bill
    the response is computed at, and a future seam that decouples them would turn a silent
    circularity into a published one.

    So the fixture asserts the SOURCE FIELD by feeding rows where the two rules disagree by
    construction: a differential saying we undercut, next to a response saying otherwise. Only a
    classifier reading the differential gets these right.

    At parity the differential is 0.0 and the household belongs to the CHEAPER side by the tool's
    `<= 0` convention -- stated so the edge is a decision on the record, not an accident.
    """
    assert churn_position_multiplier(0.0, 1700.0) == pytest.approx(1.0)
    assert _savings_to_rate(0.0) == _PARITY_RATE

    def row(cid, differential, response):
        return {
            "customer_id": cid, "event_date": "2020-06-30",
            "price_differential_vs_market_reference": differential,
            "sim_price_response": response,
            "realized_churn_probability": 0.1, "event_type": "renewed",
        }

    # Rows where "response > 1" and "differential > 0" DISAGREE. The world cannot make these; the
    # fixture can, which is the only way this leg gets a real fail branch.
    crafted = [
        row("X1", -0.10, 2.00),   # we undercut, yet a dearer-looking response
        row("X2", 0.10, 0.50),    # we price above, yet a cheaper-looking response
        row("X3", 0.0, 1.00),     # exact parity -> CHEAPER by the tool's convention
    ]
    baseline = tmp_path / "baseline.json"
    arm = tmp_path / "arm.json"
    baseline.write_text(json.dumps(crafted))
    arm.write_text(json.dumps(crafted))

    sides = {p["base"]["customer_id"]: p["arm_side"] for p in split.load_pairs(baseline, arm)}
    assert sides["X1"] == "CHEAPER (we undercut the market)", (
        "a decision whose differential says we undercut was filed as DEARER -- the side is being "
        "read from the response, which is the quantity the split exists to explain"
    )
    assert sides["X2"] == "DEARER (we price above it)"
    assert sides["X3"] == "CHEAPER (we undercut the market)"

    # And the real captures still agree with their own differentials.
    for pair in split.load_pairs(split.DEFAULT_BASELINE, split.DEFAULT_ARM):
        differential = pair["base"]["price_differential_vs_market_reference"]
        expected = (
            "CHEAPER (we undercut the market)"
            if differential <= 0.0
            else "DEARER (we price above it)"
        )
        assert pair["arm_side"] == expected
