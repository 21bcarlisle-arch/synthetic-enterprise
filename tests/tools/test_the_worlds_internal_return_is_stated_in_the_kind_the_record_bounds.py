"""The world's internal return is compared with the published bounds in the SAME KIND of quantity.

THE DEFECT THIS EXISTS TO CATCH. `_internal_return_vs_the_published_ceiling` asserted in its own
docstring that the ceiling is the *"Same KIND of quantity as the floor and as the world, which is
what makes the band admissible at all"*, and that sentence was unguarded and false. Ofgem CIM C4's
internal row is an INCIDENCE -- one household however many times it moved -- and both bounds inherit
that kind; the world's figure is an EVENT COUNT over EXPOSURE, which can exceed 1. The two coincide
only where nobody repeats AND exposure equals headcount. The defect is publishing a verdict from the
event rate as though it were a verdict about the incidence, and it was live: the world clears the
tightest annual floor at 1.11x on the event rate and at 0.77x on the incidence, so the band straddles
that bar and the published clearance was never established.

THE SECOND DEFECT, AND IT IS THE ONE THAT WOULD SURVIVE A NAIVE REPAIR. The numerator half of the
conflation is an EQUIVALENCE on this capture -- 49 conversions by 49 distinct accounts, because a
fixed term runs about a year and a passive stint is bounded at the next anniversary, so a second
conversion inside one calendar year has nowhere to happen. A repair that concluded "the kinds agree
after all" from that would be reading a property of the world's TERM LENGTHS as a property of the
COMPARISON, and would be silently wrong the first time terms shorten. This project's own rule is
that a mutation which does not fire is a missing test or an equivalence and never the flattering
one, so `test_the_repeat_factor_is_one_by_equivalence_and_the_machinery_can_see_otherwise` both
asserts the equivalence and proves the machinery would notice it ending.

THE THIRD. Every verdict in this chain was two-valued because the world was a single number. Once
the world is a band, "the band contains the bar" is a THIRD outcome, and collapsing it into either
pass or fail is how an unestablished verdict gets published as an established one. A control that
only checked the straddle case returns `None` would pass on a function that returns `None` for
everything, so the whole partition is asserted reachable in one leg.

WHY THE LEGS ARE KEYED TO PROPERTIES AND NOT TO TODAY'S ANSWER. A leg pinned to "the band straddles
the tightest annual floor" reds when the SVT-side decision is made more aggressive, which is not a
defect and is the change this band exists to observe. What is asserted instead is the ORDERING that
makes the band meaningful (incidence <= event rate), that the band is NON-DEGENERATE so it can
straddle anything at all, that the three-valued verdict is genuinely three-valued, that the
published event rate is the band's upper endpoint rather than an independent figure, and that the
refuted sentence still carries its refutation.

REUSE
-----
REUSE: tests/tools/test_the_worlds_internal_return_is_stated_in_the_kind_the_record_bounds.py
CLASS: CUSTOM
INDEX: searched "incidence", "event count", "kind of quantity", "repeat factor", "j_svt",
       "account-years", "headcount", "straddle", "internal return".
       `tests/tools/test_annualising_the_internal_row_moves_the_floor_and_never_the_ceiling.py` is
       the nearest row and is deliberately NOT extended: every leg in it is about what the RECORD's
       arithmetic can do to the two bars, and the subject here is what the WORLD's figure counts.
       Its closing reading -- world at 1.11x the tightest annual floor -- is the number one leg
       here shows to be a band endpoint, and a correction filed inside the file it corrects is
       invisible to a reader of either.
       `test_the_worlds_internal_route_is_judged_against_a_ceiling_and_not_only_a_floor.py` holds
       the docstring this file's last leg guards, and is not extended for the same reason: its legs
       assert what the ceiling verdict IS, not what kind of quantity it is a verdict about.
"""

import json

import pytest

from tools import fit_year_level_anchor as anchor
from tools import published_route_split as split


@pytest.fixture(scope="module")
def reading() -> dict:
    """The committed capture's internal-return reading, driven once."""
    rows = json.loads(anchor.DEFAULT_TABLE.read_text())
    svt_rows, reason = anchor.load_svt_decisions(anchor.DEFAULT_TABLE)
    assert svt_rows is not None, f"the capture carries no SVT decisions to read: {reason}"
    return anchor.svt_internal_return_and_tenure(rows, svt_rows)


@pytest.fixture(scope="module")
def as_incidence(reading: dict) -> dict:
    return reading["as_an_incidence_which_is_what_the_record_bounds"]


def test_the_band_is_ordered_and_non_degenerate(as_incidence: dict) -> None:
    """`J_touched <= E`, and the two endpoints are not the same number.

    The ordering is the claim every verdict below rests on -- a band whose endpoints crossed would
    make `_verdict_over_a_band` return nonsense while still returning booleans. The NON-degeneracy
    is the half a reader skips: a band collapsed to a point cannot straddle anything, so every
    three-valued verdict would silently become two-valued and this whole reading would be an
    expensive restatement of the event rate.
    """
    assert as_incidence["refused"] is None
    low, high = as_incidence["the_kind_matched_band"]
    assert as_incidence["the_band_is_ordered"] is True
    assert low <= high
    assert low < high, (
        "a degenerate band cannot straddle any bar, so no verdict here could ever be indeterminate"
    )
    assert as_incidence["incidence_per_svt_account_touched"] == low
    assert as_incidence["event_rate_per_svt_account_year"] == high


def test_the_published_figure_is_the_bands_upper_endpoint_and_not_a_separate_number(
    reading: dict, as_incidence: dict
) -> None:
    """The event rate this reading bands IS the one the other three comparisons judge.

    If these ever came apart, the band would be about a world nobody is grading and all three
    earlier readings would keep publishing their verdicts against a figure this correction never
    reached -- the VAT shape, one quantity with two live implementations.
    """
    published = reading["totals"]["internal_return_rate_per_svt_account_year"]
    assert published == as_incidence["event_rate_per_svt_account_year"]
    assert published == as_incidence["the_kind_matched_band"][1]
    assert reading["against_the_band_in_annual_units"]["world_per_svt_account_year"] == published


def test_the_repeat_factor_is_one_by_equivalence_and_the_machinery_can_see_otherwise(
    as_incidence: dict, reading: dict
) -> None:
    """No account converts twice in a year here -- and that is established, not assumed.

    The flattering reading of a repeat factor of exactly 1 is "the kinds agree after all". They do
    not: this is a property of the world's TERM LENGTHS, and the second half of this leg proves the
    measurement would report a different number if an account ever did convert twice. Without it,
    `repeat_factor` could be hard-wired to 1.0 and every leg above would still pass.
    """
    assert as_incidence["repeat_factor"] == 1.0
    assert as_incidence["no_account_converts_twice_in_a_year"] is True
    assert as_incidence["conversions"] == as_incidence["accounts_that_converted"]

    doubled = {
        year: dict(row, stint_fates=dict(row["stint_fates"]))
        for year, row in reading["per_year"].items()
    }
    victim = next(
        year for year, row in sorted(doubled.items()) if row["accounts_that_converted"]
    )
    doubled[victim]["stint_fates"][anchor.STINT_RETURNED] += 1
    mutated = anchor._internal_return_as_an_incidence(doubled)
    assert mutated["repeat_factor"] > 1.0, (
        "one extra conversion by an account that had already converted must move the repeat factor"
    )
    assert mutated["no_account_converts_twice_in_a_year"] is False
    assert mutated["per_year"][victim]["repeat_factor"] > 1.0


def test_a_year_with_no_conversions_reports_no_repeat_factor_rather_than_one(
    as_incidence: dict
) -> None:
    """A year that saw nothing establishes nothing about repetition.

    `0 / 0` answered as 1.0 would read as evidence the equivalence holds in a year that contains no
    evidence at all, and 2016 and 2022 are both such years on this capture.
    """
    silent = [
        year for year, row in as_incidence["per_year"].items()
        if row["accounts_that_converted"] == 0
    ]
    assert silent, "this leg needs at least one conversion-free year to be about anything"
    for year in silent:
        assert as_incidence["per_year"][year]["repeat_factor"] is None


def test_the_verdict_is_genuinely_three_valued(as_incidence: dict) -> None:
    """True, False and None are all reachable from `_verdict_over_a_band`.

    A guard that refuses everything passes every test of a refusal, and a verdict function that
    returned `None` for every input would satisfy the straddle leg below on its own. The whole
    partition is asserted in one control rather than a leg per branch.
    """
    band = as_incidence["the_kind_matched_band"]
    low, high = band
    assert anchor._verdict_over_a_band(band, low / 2.0, "FLOOR") is True
    assert anchor._verdict_over_a_band(band, high * 2.0, "FLOOR") is False
    assert anchor._verdict_over_a_band(band, (low + high) / 2.0, "FLOOR") is None
    assert anchor._verdict_over_a_band(band, high * 2.0, "CEILING") is True
    assert anchor._verdict_over_a_band(band, low / 2.0, "CEILING") is False
    assert anchor._verdict_over_a_band(band, (low + high) / 2.0, "CEILING") is None


def test_a_straddled_bar_is_indeterminate_and_the_event_rate_alone_would_call_it_cleared(
    as_incidence: dict
) -> None:
    """The defect, reproduced: judging the upper endpoint alone turns `None` into `True`.

    This is the leg the whole file exists for. The tightest annual floor sits inside the band, so
    the honest verdict is that the record cannot tell -- and the published reading called it cleared
    because it only ever looked at the event rate. The mutation collapses the band to that endpoint
    and shows the verdict flipping, which is what makes this control able to fail.
    """
    band = as_incidence["the_kind_matched_band"]
    bar = as_incidence["the_tightest_annual_floor"]
    assert bar is not None
    assert band[0] < bar <= band[1], "this leg is about a bar the band straddles"
    assert as_incidence["clears_the_tightest_annual_floor"] is None
    assert "the_tightest_annual_floor" in as_incidence["bars_this_band_cannot_decide"]

    event_rate_only = [band[1], band[1]]
    assert anchor._verdict_over_a_band(event_rate_only, bar, "FLOOR") is True, (
        "the event rate alone clears this bar -- that is the verdict the conflation published"
    )


def test_the_bound_actually_in_force_is_decided_by_both_endpoints(as_incidence: dict) -> None:
    """The `r = 1` corner is cleared whichever kind the world is read in, and says so.

    The tightest annual floor is the `r = 0` corner of a family whose `r` is a declared `None`, so
    failing to establish clearance of it refutes nothing. The bound the record actually makes is
    the other corner, and a reader who took the indeterminate verdict above as a refutation would
    have this backwards. Keyed to the corner's IDENTITY with the landed floor, not to its value.
    """
    assert split.REPEAT_INTERNAL_SWITCH_SHARE_WITHIN_A_YEAR is None
    annual = split.svt_internal_conversion_annualisation()
    assert as_incidence["the_floor_in_force"] == annual[
        "the_floor_in_force_is_the_total_repetition_corner"
    ]
    assert annual["the_r_1_corner_reproduces_the_landed_floor"] is True
    assert as_incidence["clears_the_floor_in_force"] is True
    assert "the_floor_in_force" not in as_incidence["bars_this_band_cannot_decide"]


def test_the_ceiling_verdict_is_unharmed_because_the_world_is_the_upper_endpoint(
    reading: dict, as_incidence: dict
) -> None:
    """A world within the ceiling on the EVENT rate is within it on the incidence too.

    The correction bites on the floor and not on the ceiling, and the reason is structural rather
    than lucky: the event rate is the band's TOP, so the ceiling's strong verdict survives being
    restated in the record's kind. A repair that had moved both verdicts in the same direction
    would be the error `svt_internal_conversion_ceiling` had to invert three choices to avoid,
    arriving once more through a new door.
    """
    assert as_incidence["within_the_tightest_annual_ceiling"] is True
    assert reading["against_the_ceiling_for_this_route"]["clears_the_binding_ceiling"] is True


def test_fails_closed_on_a_missing_bar_or_a_missing_endpoint() -> None:
    """Nothing here answers `True` on absent evidence."""
    assert anchor._verdict_over_a_band([0.1, 0.2], None, "FLOOR") is None
    assert anchor._verdict_over_a_band([None, 0.2], 0.05, "FLOOR") is None
    assert anchor._verdict_over_a_band([0.1, None], 0.05, "CEILING") is None
    empty = anchor._internal_return_as_an_incidence({})
    assert empty["refused"] is not None
    assert empty["clears_the_tightest_annual_floor"] is None
    assert empty["within_the_tightest_annual_ceiling"] is None
    assert empty["the_band_is_ordered"] is None


def test_the_refuted_kind_sentence_still_carries_its_refutation() -> None:
    """The false clause is kept verbatim and the correction sits beside it.

    Keyed to the PROPERTY -- a refuted claim carries its refutation -- and not to today's wording:
    the leg only requires the correction while the claim is still there. Deleting the correction
    and leaving the claim is the state this catches, and it is the state a tidying pass produces.
    """
    doc = anchor._internal_return_vs_the_published_ceiling.__doc__ or ""
    claim = "Same KIND of quantity as the floor and as the world"
    if claim in doc:
        assert "CORRECTED 2026-09-19" in doc, (
            "the kind claim is refuted; a reader of this docstring must meet the refutation"
        )
        assert "as_an_incidence_which_is_what_the_record_bounds" in doc, (
            "the correction must name the measurement that replaces the claim"
        )
