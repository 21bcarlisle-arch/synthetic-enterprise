"""The world's SVT->fixed rate must be judged against a bound on THAT route, not on the mixed row.

THE DEFECT THIS EXISTS TO CATCH. `fit_year_level_anchor._internal_return_vs_record` compares this
world's internal re-contract rate -- which counts ONLY SVT stints returning to a fixed term --
against Ofgem CIM C4's internal-switching row `I`, which `published_route_split`'s own identity makes
`s*J_svt + (1-s)*0.35*(1-phi)`: this route PLUS fixed-term active renewal. One numerator, two routes
in the denominator's filler, and a `world_below_record` verdict biased toward True for a reason that
is not about the world. That comparison was the only one available when it was written; `b721b6acf`
landed `svt_internal_conversion_floor`, a bound on `J_svt` alone, and
`_internal_return_vs_the_published_floor` is the un-mixed comparison it made possible.

WHY THE LEGS ARE KEYED TO THE PROPERTY AND NOT TO TODAY'S ANSWER. The world currently clears the
binding floor 4.14x in total and falls below it in 2016, 2017 and 2022. A leg pinned to "clears" goes
red when the world is made MORE honest and a leg pinned to "3 years below" goes red when the capture
is regenerated -- both backwards. What is asserted instead is which denominator the reading uses,
which published quantity it is judged against, that BOTH verdicts are reachable, and that it fails
closed when the record establishes no floor.

REUSE
-----
REUSE: tests/tools/test_the_worlds_internal_route_is_judged_against_the_floor_for_that_route.py
CLASS: CUSTOM
INDEX: searched "internal return", "conversion floor", "svt internal", "j_svt", "internal
       switching", "route split", "against the record".
       `tests/tools/test_the_svt_conversion_floor_is_a_bound_and_not_a_number.py` is the nearest row
       and is deliberately not extended: it holds the FLOOR's own properties -- that it stays a bound
       and never becomes `SVT_INTERNAL_CONVERSION_RATE` -- and knows nothing about any world. This
       file holds the JOIN between that bound and a captured world, which is a different subject
       with a different way of failing, and folding them together would give one file two.
       `tests/architecture/test_switching_rate_commons.py` holds the wall legs that keep
       `tools.published_*` out of `simulation/`. Those are what make this reading's home correct and
       they are cited here rather than restated.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools.fit_year_level_anchor as fitter
import tools.published_route_split as split

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _per_year(rate: float | None, *, returns: int = 3, account_years: float = 30.0) -> dict:
    """One per-year row in the shape `svt_internal_return_and_tenure` builds.

    `of_the_whole_book` is set to the OPPOSITE side of the floor from `per_svt_account_year` in the
    callers that care, which is what makes the denominator leg able to fail.
    """
    return {
        "svt_account_years": account_years,
        "accounts_on_book": 50,
        "stint_fates": {
            fitter.STINT_RETURNED: returns,
            fitter.STINT_DEPARTED: 1,
            fitter.STINT_CENSORED: 0,
        },
        "internal_return_rate": {"per_svt_account_year": rate, "of_the_whole_book": None},
        "long_stayer_share_of_svt_account_days": 0.3,
        "blended_annual_rate_at_this_mix": 0.17,
    }


@pytest.fixture(scope="module")
def floor() -> float:
    value = split.svt_internal_conversion_floor()["binding_floor"]
    assert value is not None and value > 0.0, (
        "the record establishes no binding floor, so every leg below would be vacuous."
    )
    return value


def test_both_verdicts_are_reachable(floor):
    """MUTATION: freeze `clears_the_binding_floor` to True (or to False) and this fires.

    THE RULE THIS OBEYS IS CLAUDE.md's: when a branch exists to be taken rarely, assert it CAN be
    taken before asserting what it does. A reading whose verdict is a constant passes every leg that
    only ever hands it today's capture -- and today's capture clears in 7 of 10 years, so a frozen
    True would look exactly like the mechanism working. One control over the whole partition, rather
    than a leg per branch.
    """
    above = fitter._internal_return_vs_the_published_floor(
        {"2019": _per_year(floor * 2.0)}, floor * 2.0
    )
    below = fitter._internal_return_vs_the_published_floor(
        {"2019": _per_year(floor / 2.0)}, floor / 2.0
    )
    assert above["clears_the_binding_floor"] is True
    assert below["clears_the_binding_floor"] is False
    assert above["per_year"]["2019"]["clears_the_binding_floor"] is True
    assert below["per_year"]["2019"]["clears_the_binding_floor"] is False
    assert above["years_below_the_floor"] == [] and above["years_clearing_the_floor"] == ["2019"]
    assert below["years_below_the_floor"] == ["2019"] and below["years_clearing_the_floor"] == []


def test_the_verdict_at_the_exact_floor_is_clearing_and_the_boundary_is_not_strict(floor):
    """MUTATION: write `rate > floor` instead of `rate >= floor` and this fires.

    A BOUND IS INCLUSIVE. `svt_internal_conversion_floor` publishes the LEAST conversion the record
    can bear, so a world sitting exactly on it has not failed to reach it. A strict comparison turns
    the one value the bound actually names into the one value it refuses.
    """
    exact = fitter._internal_return_vs_the_published_floor({"2019": _per_year(floor)}, floor)
    assert exact["clears_the_binding_floor"] is True
    assert exact["per_year"]["2019"]["clears_the_binding_floor"] is True


def test_the_denominator_is_svt_exposure_and_not_the_whole_book(floor):
    """MUTATION: read `of_the_whole_book` instead of `per_svt_account_year` and this fires.

    THE TWO ARE DIFFERENT QUANTITIES AND ONLY ONE IS COMPARABLE TO THE FLOOR. `of_the_whole_book`
    divides conversions by every account on the book; the floor divides by SVT households. Judging a
    whole-book rate against a per-SVT-household bound is the mixed-denominator comparison this
    reading exists to replace, and it would make the world look short by the SVT share -- roughly a
    factor of five on this capture -- for a reason that is arithmetic and not behaviour.

    `of_the_whole_book` is set BELOW the floor while `per_svt_account_year` is above it, so a reading
    that picked the wrong key would invert the verdict rather than merely shift it.
    """
    row = _per_year(floor * 3.0)
    row["internal_return_rate"]["of_the_whole_book"] = floor / 10.0
    reading = fitter._internal_return_vs_the_published_floor({"2019": row}, floor * 3.0)
    assert reading["per_year"]["2019"]["clears_the_binding_floor"] is True, (
        "the reading followed the whole-book denominator, which the floor's base is not."
    )
    assert reading["per_year"]["2019"]["world_per_svt_account_year"] == floor * 3.0


def test_the_bar_is_the_floor_and_not_the_mixed_internal_row(floor):
    """MUTATION: judge against `SwitcherSplitObservation.internal_rate_of_all_households` and fires.

    `I` IS THE MIXED QUANTITY AND THE FLOOR IS `I` WITH THE OTHER ROUTE NETTED OFF. Every wave's raw
    internal rate is strictly above the binding floor -- that is what the netting does -- so a
    reading that swapped one for the other would publish a harsher bar under a bound's name and
    would report a world BELOW the record that is above the bound the record actually establishes.

    The leg is the RELATION, not the values: it asserts the bar equals the floor AND that the floor
    is strictly below every raw internal row, so correcting any wave leaves it green and swapping the
    quantity does not.
    """
    reading = fitter._internal_return_vs_the_published_floor({"2019": _per_year(floor)}, floor)
    assert reading["binding_floor"] == floor
    raw = [o.internal_rate_of_all_households for o in split.SWITCHER_SPLIT_OBSERVATIONS]
    assert raw, "the CIM register has been emptied; this leg would be vacuous."
    assert all(rate > floor for rate in raw), (
        "a raw internal-switching row is at or below the binding floor, so the netting that makes "
        "the floor a bound on THIS route alone has stopped subtracting anything."
    )
    assert reading["the_point_estimate_is_still"] is None, (
        "the reading is publishing a point estimate for J_svt. The gap is "
        "`SVT_INTERNAL_CONVERSION_RATE` and it is None."
    )


def test_a_record_with_no_floor_is_refused_and_never_passed(monkeypatch, floor):
    """MUTATION: return `clears_the_binding_floor = True` when the floor is None and this fires.

    FAIL CLOSED, AND SAY SO ON THE SURFACE. "We cannot tell" is a result. A `None` floor with a
    `True` verdict is the shape that reads as a world clearing a bar nobody set -- and a comparison
    against `None` raises in Python, so the tempting repair is a `try` that returns the flattering
    branch. The refusal must be a named field, not a silence.
    """
    monkeypatch.setattr(
        split, "svt_internal_conversion_floor",
        lambda: {
            "binding_floor": None,
            "binding_floor_unit": "n/a",
            "source": "test",
            "waves_with_a_floor": 0,
            "the_point_estimate_is": None,
        },
    )
    reading = fitter._internal_return_vs_the_published_floor(
        {"2019": _per_year(floor * 5.0)}, floor * 5.0
    )
    assert reading["refused"], "no floor and no refusal: the reading is silent where it cannot tell."
    assert reading["clears_the_binding_floor"] is None
    assert reading["per_year"]["2019"]["clears_the_binding_floor"] is None
    assert reading["years_scored"] == [] and reading["years_below_the_floor"] == []
    assert reading["the_verdict_is_not_uniform"] is False


def test_a_year_with_no_measurable_rate_is_scored_as_neither(floor):
    """MUTATION: treat a `None` per-year rate as 0.0 and this fires by calling it below the floor.

    AN ABSENT YEAR AND A YEAR IN WHICH NOBODY CONVERTED PRODUCE THE SAME COUNT OTHERWISE -- the rule
    `_internal_return_vs_record` already states for its refused waves. `per_svt_account_year` is
    `None` when a year carries no SVT exposure at all, and reading that as a zero rate would publish
    a behavioural finding about a year the capture cannot see.
    """
    reading = fitter._internal_return_vs_the_published_floor(
        {"2019": _per_year(None, returns=0, account_years=0.0), "2020": _per_year(floor * 2.0)},
        floor * 2.0,
    )
    assert reading["per_year"]["2019"]["clears_the_binding_floor"] is None
    assert reading["years_scored"] == ["2020"]
    assert "2019" not in reading["years_below_the_floor"]


def test_the_uniformity_flag_is_derived_and_not_declared(floor):
    """MUTATION: hard-code `the_verdict_is_not_uniform = True` and this fires on a uniform capture.

    IT IS TRUE ON TODAY'S CAPTURE, which is exactly why it needs a leg that hands the reading a
    capture where it is false. A flag frozen to the current answer is the shape that goes green when
    the claim rots: the day every year clears, a hard-coded True would still be advertising a spread
    that no longer exists.
    """
    mixed = fitter._internal_return_vs_the_published_floor(
        {"2019": _per_year(floor * 2.0), "2020": _per_year(floor / 2.0)}, floor
    )
    all_clear = fitter._internal_return_vs_the_published_floor(
        {"2019": _per_year(floor * 2.0), "2020": _per_year(floor * 3.0)}, floor * 2.0
    )
    all_below = fitter._internal_return_vs_the_published_floor(
        {"2019": _per_year(floor / 2.0), "2020": _per_year(floor / 3.0)}, floor / 2.0
    )
    assert mixed["the_verdict_is_not_uniform"] is True
    assert all_clear["the_verdict_is_not_uniform"] is False
    assert all_below["the_verdict_is_not_uniform"] is False


def test_the_committed_artefact_carries_the_comparison_recomputed_and_not_cached(floor):
    """MUTATION: copy the per-year verdicts off the artefact instead of deriving them, and fires.

    THE ARTEFACT IS THE THING A READER OPENS, so a reading that exists only in the function is a
    reading nobody sees. This leg re-derives every per-year verdict from the artefact's OWN rate
    column against the live floor and requires the stored verdict to agree -- so a floor that moves
    without the artefact being regenerated is a red here rather than a stale page.

    It also holds that the mixed comparison is still present and now SAYS it is mixed: the correction
    for `_internal_return_vs_record` was recorded beside that reading rather than over it, and a
    later tidy-up that deleted the caveat would leave the misleading verdict with nothing against it.
    """
    # THE SUFFIX IS NAMED HERE, IN THE SCOPE THAT READS IT, rather than at a module-level path
    # constant. A module-level constant leaves this function reading a file whose KIND cannot be seen
    # from inside it, which is how `substring_source_scan_census` scored this scope
    # `subject=unknown` -- it fails closed when path evidence is absent, and rightly. Saying `.json`
    # where the read happens is what makes "this is not Python source being scanned as text"
    # checkable rather than asserted, and it is what a reader of this function wants to know anyway.
    artefact = _REPO_ROOT / "docs" / "reports" / "svt_internal_return_and_tenure.json"
    if not artefact.exists():  # pragma: no cover - committed in this repo
        pytest.skip(f"{artefact.relative_to(_REPO_ROOT)} is not present")
    reading = json.loads(artefact.read_text())
    if "refused" in reading and "per_year" not in reading:  # pragma: no cover
        pytest.skip("the committed capture produced a refusal, which carries no comparison")
    block = reading["against_the_floor_for_this_route"]
    assert block["binding_floor"] == floor, (
        f"the artefact was built against a floor of {block['binding_floor']} and the record now "
        f"establishes {floor}. Regenerate: "
        f"python3 -m tools.fit_year_level_anchor --internal-return"
    )
    checked = 0
    for year, cell in block["per_year"].items():
        stored = reading["per_year"][year]["internal_return_rate"]["per_svt_account_year"]
        assert cell["world_per_svt_account_year"] == stored, (
            f"{year}: the comparison's rate does not match the reading's own column."
        )
        if stored is None:
            assert cell["clears_the_binding_floor"] is None
            continue
        checked += 1
        assert cell["clears_the_binding_floor"] == (stored >= floor), (
            f"{year}: stored verdict {cell['clears_the_binding_floor']} against a rate of {stored} "
            f"and a floor of {floor}."
        )
    assert checked >= 5, f"only {checked} years carry a rate; the reading has been emptied."
    assert reading["against_the_record"]["this_comparison_is_against_the_MIXED_quantity"].strip(), (
        "the mixed-quantity caveat has gone from `against_the_record`, leaving its "
        "`world_below_record` verdict with nothing beside it to say what it is comparing."
    )


def test_the_reading_names_which_direction_its_bar_flatters(floor):
    """MUTATION: delete `the_bar_is_weak_in_this_direction` and this fires.

    A SIX-MONTH FLOOR USED AS AN ANNUAL BAR IS LOWER THAN THE TRUE ANNUAL BAR, so "the world clears"
    is the flattering verdict here and "the world is below" is the strong one. A reader handed a
    4.14x multiple and no statement of that direction will read it as headroom. This is the leg that
    keeps the caveat attached to the number rather than in a commit message, and it checks the
    SUBJECT of the caveat -- the unit mismatch -- and not merely that some prose exists.
    """
    reading = fitter._internal_return_vs_the_published_floor({"2019": _per_year(floor)}, floor)
    weak = reading["the_bar_is_weak_in_this_direction"].lower()
    assert "six-month" in weak or "six month" in weak, (
        "the weakness statement does not name the six-month/annual mismatch that causes it."
    )
    assert "annual" in weak
    assert "six" in reading["binding_floor_unit"].lower()
    counts = reading["what_each_number_counts"]
    assert counts["world"].strip() and counts["floor"].strip()
    assert counts["the_two_mismatches_that_are_named_and_not_corrected"].strip(), (
        "the population and window mismatches are not stated, so a reader cannot tell the "
        "comparison is between a survey of GB households and this book's electricity accounts."
    )
