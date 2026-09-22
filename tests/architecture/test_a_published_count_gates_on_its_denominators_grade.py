"""A published count derived from a quotient says whether its denominator can reach zero.

WHY THIS EXISTS, AND WHY IT IS A CLASS CONTROL AND NOT A FIFTH FIX. Four instances of one rule
were found and fixed one at a time -- `06e316ae4` and `5742edb1c` on two page keys, `964036259` at
the money leg's producer, `949f80894` at the rank leg's. **Every one was found by a human-ish read
of a block that happened to sit next to the last one.** Nothing in the tree could see the shape.
That is the VAT shape `CLAUDE.md` names -- one requirement, several implementations, fixed in some
and live in the rest -- and four instances stopped being evidence of four bugs somewhere around
the third. The rule and the closed set of honest declarations are stated once, in
`tools/unbounded_quotient_census.py`; this file is what makes the fifth instance impossible to
land unnoticed rather than what finds it by hand.

WHAT EACH TEST HERE NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL):

  * `test_the_undeclared_quotient_debt_only_SHRINKS` -- the defect is a count with an estimate in
    its denominator published under a name whose grammar is a plan. `seeds_needed_to_state_a_sign:
    101` sat on the live feed for a family 0.686 errors from zero: a number with no upper bound,
    telling a reader that 101 draws would settle it. A ratchet cannot fix the 16 that exist; it
    makes the 17th impossible.
  * `test_the_repaired_sites_are_an_EXACT_SET` -- the ratchet's blind side. A ratchet only catches
    INCREASES, so a mutation that breaks the classifier open drives the count down and goes green
    forever. The sites the four commits repaired are pinned by NAME, so un-gating one reds here
    rather than merely moving a number.
  * `test_a_DEGENERATE_guard_is_not_a_withholding` -- the blind side the blind side still had.
    Written only after a mutation sweep found that widening the grade vocabulary by one word left
    every other test in this file green; see the test's own docstring.
  * `test_the_scan_has_not_lost_its_SUBJECTS` -- the population floor, for the same reason
    `test_a_domain_constant_carries_its_origin` grew one: a control that counts violations reads a
    broken scan as a paid debt. If the walk stops finding published counts at all, this fires.
  * `test_an_UNPARSEABLE_file_is_reported_and_not_silently_skipped` -- the same fail-quiet one
    level down. A file that will not parse contributes no sites and can only shrink the debt.
  * `test_all_three_grades_are_REACHABLE` -- the rare-branch control `CLAUDE.md` asks for, over
    the whole partition in one assertion. A classifier that graded everything BOUNDED would pass
    every "does it refuse correctly" test written above; this is the one that notices.
  * `test_a_withholding_NAME_is_not_enough_without_a_reachable_None` -- the defect is a site that
    READS gated. `X_needed` beside `X_needed_unavailable_because`, with the count computed on
    every path, is the original defect wearing the repair's clothes, and a sibling-key test alone
    goes green on it.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. The exact set below holds SITES THAT ARE CORRECTLY
GATED, not sites that exist. Repairing a DEBT site does not red this file -- the debt falls and the
set is untouched, which is the direction a control should be silent in. It reds when a repaired
site stops being repaired, which is the direction it should be loud in.
"""
from __future__ import annotations

import ast
import textwrap

from tools import unbounded_quotient_census as census

#: THE DEBT, AND IT MAY ONLY FALL. It landed at 16 on 2026-09-22 and came down to 6 the same day
#: when `tools/inference_claim.py` -- the fifth instance, and the first this rule ever found by a
#: CONTROL rather than by reading the block next door -- was repaired along with the three keys
#: `generate_value_arms_data` republishes from it. Lowered here in the same commit as the repair,
#: because a ceiling left at the old number is a licence for ten more.
#:
#: AND TO ZERO ON 2026-09-22, when the last six were repaired: three in
#: `tools/fit_year_level_anchor.py` and three in `tools/run_value_cycle_ab.py`.
#:
#: ZERO IS NOT "FINISHED" AND THE DISTINCTION IS LOAD-BEARING. The census module's own docstring
#: names what it cannot reach -- a count assembled across two functions, or through a dict
#: round-trip, is INVISIBLE here rather than clean. `scored_decisions_needed` is one such site and
#: it is repaired; there will be others that are not. A zero on this ratchet says every site the
#: scan CAN see has been classified, which is the claim it is entitled to make and no more.
UNDECLARED_DEBT_CEILING = 0

#: AND A FLOOR UNDER THE WHOLE POPULATION. 23 sites found; a walk that finds materially fewer has
#: broken rather than been fixed, because no single commit retires a third of them.
#:
#: NOT RAISED WHEN THE DEBT WENT TO ZERO, and deliberately. The population moved 27 -> 26 in that
#: commit because two sites in `fit_year_level_anchor` collapsed into ONE shared helper, which is a
#: repair shrinking the population rather than a walk losing sites. A floor pinned to today's 26
#: would red the next honest de-duplication; this one is keyed to "the walk still works".
POPULATION_FLOOR = 19

#: THE SITES THE FOUR COMMITS REPAIRED, pinned by (file, key) and NOT by line -- a line number
#: moves whenever a neighbour gains a comment, and a control that reds on that gets deleted.
REPAIRED = {
    ("tools/generate_value_arms_data.py", "rosters_needed_to_state_a_sign"),
    ("tools/generate_value_arms_data.py", "rosters_needed_interval"),
    ("tools/generate_value_arms_data.py", "seeds_needed_interval"),
    # THE FIFTH INSTANCE, repaired 2026-09-22 and pinned for the same reason the other four are:
    # a ratchet on a count cannot see one of these quietly losing its gate.
    ("tools/inference_claim.py", "decisions_needed_for_the_observed_effect"),
    ("tools/inference_claim.py", "accounts_needed_for_the_observed_effect"),
    ("tools/inference_claim.py", "settled_accounts_needed_for_the_observed_effect"),
    ("tools/inference_claim.py", "decisions_needed"),
    ("tools/inference_claim.py", "accounts_needed"),
    # `scored_decisions_needed` IS REPAIRED TOO AND IS DELIBERATELY NOT PINNED HERE. Its value
    # arrives through a dict round-trip (`book.get(...)`), which is exactly the limit the census
    # module's own docstring names: the resolver works within one function and cannot follow a
    # value out of a dict, so the site is INVISIBLE to the scan rather than ungated by it. Pinning
    # a site the scan cannot see would red this control permanently and teach the next reader that
    # the pin means nothing. The repair is controlled instead by
    # `test_the_observed_book_price_is_WITHHELD_where_the_reading_fails_its_own_null`, which asks
    # the produced value rather than the source.
    ("tools/generate_value_arms_data.py", "same_year_pairs_needed"),
    ("tools/generate_value_arms_data.py", "priced_renewals_needed"),
    ("tools/generate_value_arms_data.py", "renewals_the_world_must_offer"),
    # THE LAST SIX, repaired 2026-09-22, taking the ratchet to zero. Five of them gate; the sixth
    # is BOUNDED and is pinned separately below, because the two declarations are different claims
    # and a set that mixed them would pass a site that swapped one for the other.
    ("tools/fit_year_level_anchor.py", "hazard_multiple_still_required_at_band_low"),
    ("tools/run_value_cycle_ab.py", "priced_decisions_needed"),
    ("tools/run_value_cycle_ab.py", "independent_draws_needed"),
    ("tools/run_value_cycle_ab.py", "priced_decisions_needed_on_the_published_floor"),
}

#: THE SITES THAT DECLARE A BOUNDED DENOMINATOR, pinned for the reason `REPAIRED` is: a `#:
#: DENOMINATOR BOUNDED:` comment is a claim about the world that a reader can delete in a tidy-up
#: without the debt count moving -- the site would simply vanish from the census's DEBT list by
#: becoming ungraded, or worse, stay BOUNDED on a marker that drifted into a neighbour's function.
#:
#: A SEPARATE SET AND NOT A MERGE WITH `REPAIRED`. Swapping a gate for a bounded declaration is
#: exactly the silent weakening this file exists to catch: the gate withholds a figure and the
#: declaration publishes it, so a control that accepted either would grade that swap as no change.
DECLARED_BOUNDED = {
    ("tools/fit_year_level_anchor.py", "required_over_re_referenced_recent"),
}


def _sites():
    unreadable: list[str] = []
    return census.census(unreadable=unreadable), unreadable


def test_the_undeclared_quotient_debt_only_SHRINKS():
    """DEFECT: a count with an estimate in its denominator, published as a plan."""
    sites, _ = _sites()
    owed = [s for s in sites if s.grade == "DEBT"]
    assert len(owed) <= UNDECLARED_DEBT_CEILING, (
        "{} published counts now carry a measured denominator with neither a withholding sibling "
        "nor a `#: DENOMINATOR BOUNDED:` declaration, against a ceiling of {}. A count that "
        "scales as (bar/estimate)^2 has NO UPPER BOUND where the estimate's interval contains "
        "zero, which is exactly the state a reader asks it in. Either gate it and name the "
        "withholding, or declare at the site why this denominator cannot approach zero.\n  "
        "{}".format(len(owed), UNDECLARED_DEBT_CEILING,
                    "\n  ".join("{}:{} {}".format(s.path, s.line, s.key) for s in owed)))


def test_the_repaired_sites_are_an_EXACT_SET():
    """DEFECT: a repaired site quietly losing its gate, which no ratchet on a count can see."""
    sites, _ = _sites()
    gated = {(s.path, s.key) for s in sites if s.grade == "GATED"}
    assert REPAIRED <= gated, (
        "these sites were repaired by 06e316ae4 / 5742edb1c / 964036259 / 949f80894 and no longer "
        "grade GATED: {}. A count whose denominator is an estimate the same artefact grades "
        "against its own bar must be withheld where that grade fails, with a sibling key naming "
        "why -- and the value must actually be able to reach None.".format(
            sorted(REPAIRED - gated)))


def test_a_bounded_declaration_cannot_quietly_become_a_gate_OR_VANISH():
    """DEFECT: a `#: DENOMINATOR BOUNDED:` claim deleted, or swapped for a withholding."""
    sites, _ = _sites()
    bounded = {(s.path, s.key) for s in sites if s.grade == "BOUNDED"}
    assert DECLARED_BOUNDED <= bounded, (
        "these sites declared their denominator BOUNDED and no longer grade BOUNDED: {}. Either "
        "the `#: DENOMINATOR BOUNDED:` comment was removed -- in which case the claim that the "
        "denominator cannot approach zero is gone and the count is undeclared again -- or the "
        "site now GATES instead, which is a different and weaker statement: a gate withholds the "
        "figure, a bounded declaration publishes it on every path.".format(
            sorted(DECLARED_BOUNDED - bounded)))


def test_the_scan_has_not_lost_its_SUBJECTS():
    """DEFECT: the debt reading as paid because the walk stopped finding anything."""
    sites, _ = _sites()
    assert len(sites) >= POPULATION_FLOOR, (
        "the census found {} published plan-grammar counts and the floor is {}. A scan that loses "
        "its subjects reports every ratchet above as green, which is how this project's counting "
        "controls have failed before.".format(len(sites), POPULATION_FLOOR))


def test_an_UNPARSEABLE_file_is_reported_and_not_silently_skipped():
    """DEFECT: a file that will not parse contributing no sites and shrinking the debt."""
    sites, unreadable = _sites()
    assert not unreadable, (
        "these files under the censused roots would not parse, so they contributed no sites and "
        "could only make the debt look smaller: {}".format(unreadable))
    assert sites, "the census returned nothing at all, which is not a clean tree"


def test_all_three_grades_are_REACHABLE():
    """DEFECT: a classifier stuck on one verdict, which passes every refusal test above.

    ONE ASSERTION OVER THE WHOLE PARTITION, per `CLAUDE.md`: a guard that refuses everything, or
    grades everything BOUNDED, satisfies each per-grade test written separately. Asked of
    SYNTHETIC source rather than the tree, so retiring the last DEBT site -- which is the point of
    the ratchet -- does not red the control that proves DEBT is reachable.
    """
    source = textwrap.dedent('''
        import math
        TOLERANCE = 0.05
        def bounded_case(spread):
            return {"draws_needed": math.ceil((spread / TOLERANCE) ** 2)}
        def debt_case(bar, estimate):
            return {"draws_needed": math.ceil((bar / estimate) ** 2)}
        def gated_case(bar, estimate, clears):
            count = math.ceil((bar / estimate) ** 2)
            return {"draws_needed": count if clears else None,
                    "draws_needed_unavailable_because": None if clears else "no upper bound"}
    ''')
    graded = {s.key + "@" + str(s.line): s.grade
              for s in census.census_file("synthetic.py", source)}
    grades = set(graded.values())
    assert grades == {"BOUNDED", "DEBT", "GATED"}, (
        "the classifier reached only {} over source written to exercise all three. A grade that "
        "cannot be reached makes every assertion resting on it vacuous.".format(sorted(grades)))


def test_a_withholding_NAME_is_not_enough_without_a_reachable_None():
    """DEFECT: the original bug wearing the repair's clothes.

    `X_needed` beside `X_needed_unavailable_because`, with the count computed unconditionally, is
    a reason key sitting reassuringly next to a figure that is always published. A control asking
    only for the sibling key goes green on precisely the defect it was written for, so this asks
    the arithmetic too.
    """
    source = textwrap.dedent('''
        import math
        def reassuring(bar, estimate):
            return {"draws_needed": math.ceil((bar / estimate) ** 2),
                    "draws_needed_unavailable_because": "a string that is always absent"}
    ''')
    sites = census.census_file("synthetic.py", source)
    assert [s.grade for s in sites] == ["DEBT"], (
        "a site naming a withholding it never performs graded {} -- the sibling key was taken as "
        "the repair. What makes it a repair is that the count CAN be None.".format(
            [s.grade for s in sites]))
    assert "cannot perform" in sites[0].why, (
        "the grade is right but the reason does not tell the reader which of the two halves is "
        "missing, and a refusal that does not name its cause is how a wrong refusal survives")


def test_a_DEGENERATE_guard_is_not_a_withholding():
    """DEFECT: the grade vocabulary widened until it waves everything through.

    FOUND BY MUTATION AND NOT BY DESIGN, 2026-09-22, and it is the sharpest thing in this file.
    Adding one degenerate-guard name to `GRADE_VOCAB` left all six tests above GREEN, because
    every consequence of a too-wide vocabulary moves the DEBT count DOWN: the ratchet only catches
    increases, the repaired set is a subset and stays satisfied, and the synthetic DEBT case has
    no gate of any kind so it is graded DEBT whatever the vocabulary says. A classifier that
    breaks open reports the debt paid and every leg stays quiet -- which is the exact failure
    `test_a_domain_constant_carries_its_origin` records having built into its own first draft.

    So this pins the DISTINCTION rather than the count, over the real shape that caused it. The
    guard below mirrors `_rosters_to_state_a_sign`'s `price_at`: a helper returning `None` at the
    exactly-zero input. That `None` is a guard against division by zero -- a measure-zero case
    nobody meets -- and NOT a statement that the estimate failed its bar, which is the entire
    state a reader asks the count in. Read as a withholding it hides the defect it resembles.
    """
    source = textwrap.dedent('''
        import math
        def looks_gated(bar, distance):
            def price_at(d):
                return None if d == 0 else math.ceil((bar / d) ** 2)
            return {"draws_needed": price_at(distance),
                    "draws_needed_unavailable_because": "a reason that never fires"}
    ''')
    sites = census.census_file("synthetic.py", source)
    assert [s.grade for s in sites] == ["DEBT"], (
        "a count withheld only where its denominator is EXACTLY zero graded {}. A divide-by-zero "
        "guard and a withholding on a failed bar are different statements, and taking the first "
        "for the second is how the un-gating of a repaired site went unnoticed by this very "
        "control until it was mutated.".format([s.grade for s in sites]))


def test_the_census_reads_python_as_CODE_and_not_as_text():
    """DEFECT: a substring scan calling a key in a docstring a published count.

    The four fixed sites are discussed at length in prose in the very files they live in --
    `_seed_price_interval`'s docstring names `seeds_needed_to_state_a_sign` five times. A text
    scan would grade those mentions and the debt would be noise.
    """
    source = textwrap.dedent('''
        """A docstring naming draws_needed and a quotient bar / estimate at length."""
        def f(bar, estimate):
            # draws_needed = bar / estimate, discussed but not published
            return {"unrelated": 1}
    ''')
    assert census.census_file("synthetic.py", source) == []
    assert isinstance(ast.parse(source), ast.Module)
