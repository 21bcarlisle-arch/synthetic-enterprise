"""THE QUANTITY IS NAMED FOR WHAT IT IS, AND A REQUIREMENT WITH NO SIGN IS REFUSED.

THE DEFECT THESE CONTROL. `renewal_churn_belief.ceiling` was published under the word "ceiling"
and the gloss "what a perfect reader of this world would get", while on this page's own rows the
belief it supposedly bounds outscored it, it failed its own null where the belief cleared, pooling
put the two on opposite sides of each other, and a second roll of the same world's dice swapped
which of them cleared. Four things a bound cannot do, on one surface, under a word that told the
reader the opposite. And the withdrawal beside it took away a reading of whether the per-customer
decision discriminates and left the reader no way to tell the company's failure from the book's.

KEYED TO THE PROPERTY, WHICH IS THE POINT OF WRITING THEM THIS WAY. Neither control pins today's
answer. `test_the_whole_partition_is_reachable` is one assertion over BOTH states, because a
verdict function that returned "not a bound" unconditionally would pass every test written about
the crossing and fail nothing -- this repository has entered that trap three times through three
different doors. The bound branch is asserted REACHABLE before anything is asserted about what the
crossing branch says.

THE SECOND PAIR IS THE SAME SHAPE ON THE REQUIREMENT. A requirement of the form
`(k / value)^2` has an upper bound only where the denominator's sign is determined, so the refusal
must fire on opposite-signed draws AND must NOT fire on same-signed ones. A refusal that refused
everything would be indistinguishable from this one on a test of the refusal alone.
"""

import pytest

from tools.generate_value_arms_data import _ceiling_is_not_a_bound, _renewal_belief_settlement


def _draw(source, auc, ceiling_auc, *, decisions=102, low=0.37, high=0.63,
          clears=True, ceiling_clears=False):
    return {"source": source, "decisions": decisions, "departures": 41, "pairs": 384,
            "auc": auc, "null_95_low": low, "null_95_high": high,
            "clears_its_own_null": clears,
            "ceiling_auc": ceiling_auc, "ceiling_clears_its_own_null": ceiling_clears}


def _crossed():
    """The state this page is actually in: every one of the four crossings holds."""
    return _ceiling_is_not_a_bound(
        belief_auc=0.6706, belief_inside=False, ceiling_auc=0.5911, ceiling_clears=False,
        ceiling_null_width=0.2760, decisions=102,
        strat={"belief_auc_pooled": 0.5940, "ceiling_auc_pooled": 0.6717},
        repetition={"draws": [_draw("first", 0.6706, 0.5911),
                              _draw("second", 0.5847, 0.6486, decisions=138,
                                    clears=False, ceiling_clears=True)]})


def _uncrossed():
    """A capture where the quantity DOES bound the belief -- nothing crosses.

    Asserted reachable before anything is asserted about the other branch. A function that could
    only ever return "not a bound" passes every crossing test ever written about it.
    """
    return _ceiling_is_not_a_bound(
        belief_auc=0.5500, belief_inside=True, ceiling_auc=0.7000, ceiling_clears=True,
        ceiling_null_width=0.2760, decisions=102,
        strat={"belief_auc_pooled": 0.5400, "ceiling_auc_pooled": 0.7200},
        repetition={"draws": [_draw("first", 0.5500, 0.7000, clears=True, ceiling_clears=True),
                              _draw("second", 0.5600, 0.7100, clears=True, ceiling_clears=True)]})


def test_the_whole_partition_is_reachable():
    """BOTH verdicts occur. The one control that a stuck answer cannot pass."""
    assert _crossed()["is_a_bound"] is False and _uncrossed()["is_a_bound"] is True


def test_a_belief_scoring_above_it_is_counted_as_a_crossing():
    crossed = _crossed()
    by_name = {row["crossing"]: row["observed"] for row in crossed["crossings"]}
    assert by_name["the_belief_reads_above_it_on_the_published_rows"] is True
    assert by_name["it_failed_its_own_null_on_a_draw_the_belief_cleared"] is True
    assert by_name["pooling_reverses_which_of_the_two_is_higher"] is True
    assert by_name["it_cleared_on_a_draw_where_the_belief_did_not"] is True
    assert crossed["crossings_observed"] == 4


def test_a_quantity_that_bounds_nothing_says_so_and_one_that_bounds_says_nothing():
    """The prose is tied to the verdict at BOTH ends, so neither can go stale against it."""
    crossed, uncrossed = _crossed(), _uncrossed()
    assert crossed["not_a_bound_because"]
    # IT NAMES THE COUNT IT DERIVED, so a sentence claiming four crossings beside a block that
    # found two cannot ship -- the rot this same panel's "these same 144 decisions" already was.
    assert "did 4 things" in crossed["not_a_bound_because"]
    assert "no longer called a ceiling" in crossed["not_a_bound_because"]
    assert "scored on one draw" in crossed["the_name_it_has_earned"]
    # AND THE OTHER WAY. A capture that bounds must not carry a refusal sentence, or the page
    # would publish "it is not a ceiling" beside a quantity that is one.
    assert uncrossed["not_a_bound_because"] is None
    assert "scored on one draw" not in uncrossed["the_name_it_has_earned"]


def test_an_undecidable_crossing_is_not_read_as_a_clean_bound():
    """`None` in, `None` out. An unaskable question must not resolve to the flattering answer."""
    undecidable = _ceiling_is_not_a_bound(
        belief_auc=None, belief_inside=None, ceiling_auc=None, ceiling_clears=None,
        ceiling_null_width=None, decisions=None, strat={}, repetition={})
    assert undecidable["is_a_bound"] is None
    assert undecidable["not_a_bound_because"] is None


# ---------------------------------------------------------------------------
# THE REQUIREMENT: refused where the sign is undetermined, priced where it is not.
# ---------------------------------------------------------------------------

def _settlement(second_ceiling):
    return _renewal_belief_settlement({
        "available": True,
        "draws": [_draw("first", 0.6706, 0.5911),
                  _draw("second", 0.5847, second_ceiling, decisions=138,
                        low=0.3928, high=0.6216, clears=False, ceiling_clears=True)]})


def _gap_question(block):
    return next(q for q in block["questions"]
                if q["question"] == "does_the_belief_reach_what_the_world_orders_by")


def test_both_sign_verdicts_are_reachable():
    """The partition again, on the requirement. An always-refusing gate passes no version of this."""
    opposite = _gap_question(_settlement(0.6486))      # gaps +0.0795 and -0.0640
    same = _gap_question(_settlement(0.5000))          # gaps +0.0795 and +0.0847
    assert opposite["the_sign_is_determined_across_draws"] is False
    assert same["the_sign_is_determined_across_draws"] is True


def test_an_undetermined_sign_publishes_no_requirement_at_all():
    """Not a large number -- NO number. `(k / value)^2` over a sign-free estimate is unbounded."""
    block = _settlement(0.6486)
    gap = _gap_question(block)
    assert gap["settled_by_a_finite_book"] is False
    assert block["verdict"] == "no_finite_book_settles_this_from_this_estimate"
    assert all(row["decisions_needed"] is None for row in gap["per_draw"])
    assert "NO UPPER BOUND" in gap["why"]


def test_the_reachable_counts_are_published_beside_the_refusal():
    """"No finite book" alone reads as "we need an enormous book". The counts say otherwise."""
    block = _settlement(0.6486)
    assert block["what_binds_is_not_the_book"]
    assert "the book is not what binds" in block["what_binds_is_not_the_book"].lower()
    # AND THEY ARE MARKED AS BORROWED. The difference of two AUCs carries no permutation null of
    # its own, so the width used to price it is the belief's -- quoting the count without that is
    # quoting an interval the quantity never had.
    gap = _gap_question(block)
    assert gap["carries_a_permutation_null_of_its_own"] is False
    assert all(row["count_is_on_a_borrowed_width"] for row in gap["per_draw"])


def test_the_two_questions_are_named_before_either_is_priced():
    """"Does it discriminate" is two quantities. One figure covering both is a figure of neither."""
    block = _settlement(0.6486)
    assert [q["question"] for q in block["questions"]] == [
        "does_the_belief_order_departures_at_all",
        "does_the_belief_reach_what_the_world_orders_by"]
    chance = block["questions"][0]
    assert chance["carries_a_permutation_null_of_its_own"] is True
    assert chance["the_sign_is_determined_across_draws"] is True


@pytest.mark.parametrize("repetition,expected", [
    ({"available": False}, "could not be read"),
    ({"available": True, "draws": [_draw("only", 0.6706, 0.5911)]}, "fewer than two draws"),
])
def test_one_draw_prices_nothing_and_says_which_reason(repetition, expected):
    """A requirement priced from a single draw is the shape this block exists to refuse."""
    block = _renewal_belief_settlement(repetition)
    assert block["available"] is False
    assert expected in block["why"]
