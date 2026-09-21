"""`required_customer_years_smallest_leg` is a PRODUCT OF TWO FACTORS, and they must be one book.

THE DEFECT THIS EXISTS FOR, and it was made by this seat rather than found in someone else's
code. `can_a_book_that_size_be_built` publishes `required_multiple_smallest_leg` -- a multiple of
the book the floor spread was measured on -- and `this_book_customer_years`, and multiplies them.
On 2026-09-21 a staging record took that multiple (2.8198526) and carried it to the PROMOTED run's
1,029 customer-years, publishing 2,902 and "2.42x the capacity" beside the block's own 3,163.9 and
2.64x. The two readings were then filed as "one denominator is a run stale". NEITHER WAS STALE.
The product had crossed two runs, which asks how many customer-years of one book equal a multiple
of a different one, and that is not a quantity.

WHAT A CONTROL CAN ACTUALLY HOLD HERE. It cannot stop prose in a staging document from
re-scaling a published multiple. What it CAN hold is the thing whose absence made that re-scaling
look legitimate: the block never said which book its own multiple belonged to, while the page named
other panels' stamps a few keys away (`superseded_generated_at`), so a reader had every reason to
think the newer book was the right one to carry it to. So these legs assert the STAMP EXISTS, that
it names the run the factors actually came from, and that the published product is the product of
THAT stamp's customer-years -- not of any other book on the page.

KEYED TO THE PROPERTY AND NOT TO TODAY'S ANSWER. Nothing here pins 1,122, 164, 2.8198526 or
2026-09-08. A run that settles a different book moves every one of those and every leg still holds;
a producer that ever re-denominates the multiple onto a second run reds `test_the_published_product
_is_the_stamped_book_s_own`, which is the only change that makes the published figure wrong again.

THE HALF-LANDED SHAPE IS WHY THE FEED LEG IS HERE. When this was written the stamp was live in
`site/data/value_arms.json` at origin/main and the producer hunk that emits it had never been
committed -- it sat dirty in the shared tree, the auto-process ran it, and the pathspec commit took
the feed and not the code. The next regeneration from a clean tree would have dropped the stamp
silently and re-opened the hole, with the published bytes still showing it had been fixed.
`test_the_stamp_in_the_published_feed_is_one_the_producer_can_still_emit` is the leg that would
have caught that, and it is the reason this file names the feed at all.

REUSE: searched "denominated", "this_book_customer_years", "required_customer_years",
"can_a_book_that_size_be_built", "book_these_figures" across tests/ and tools/.
CLASS: CUSTOM. `tests/tools/test_generate_value_arms_data.py` is the producer's own suite and has
no leg on this block's provenance -- its `_CLEARS_ZERO_KEYS` registry grades leaf VALUES for
zero-clearing, which is a different question and cannot see a missing key at all. Nothing else in
the tree asserts that a published multiple names its own denominator.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools.generate_value_arms_data as gva

PROJECT = Path(__file__).resolve().parents[2]
FEED = PROJECT / "site" / "data" / "value_arms.json"


#: A run the producer can read, small enough to be read at a glance and shaped like the real
#: artefact at exactly the four places `_can_this_book_be_built` reaches into it. The numbers are
#: deliberately NOT the live book's: a fixture that reproduces today's feed cannot tell a producer
#: that reads its stamp from the run apart from one that hard-codes the published values.
A_RUN = {
    "generated_at": "2026-01-02T03:04:05Z",
    "book_identity": {"control_arm": {"billing_accounts_settled_in_window": 71}},
    "household_side": {"control_arm": {"customer_years": 500.0}},
    "gross_to_net_bridge": {"control_arm": {"records": 150_000}},
}

#: Two priced rows, so `smallest` and `largest` are distinguishable and a leg that read the wrong
#: one is visible. Only `times_this_book` is read.
PRICED_ROWS = [{"times_this_book": 2.0}, {"times_this_book": 9.0}]


@pytest.fixture(scope="module")
def built():
    block = gva._can_this_book_be_built(A_RUN, PRICED_ROWS)
    assert block.get("available") is True, (
        "the fixture run no longer satisfies the producer, so every leg below would be asserting "
        "about a refusal rather than about a verdict: {!r}".format(block.get("reason")))
    return block


def test_the_block_names_the_run_its_multiple_is_a_multiple_of(built):
    """MUTATION: delete `the_book_these_figures_are_denominated_in` from the producer.

    That is the state this block shipped in until 2026-09-21, and it is what let a later reader
    carry the multiple to a different run in good faith.
    """
    stamp = built.get("the_book_these_figures_are_denominated_in")
    assert isinstance(stamp, dict), (
        "`can_a_book_that_size_be_built` publishes a multiple of a book and does not say which "
        "book -- the absence that let 2.8198526 be re-scaled onto another run's customer-years")
    assert stamp.get("run_generated_at") == A_RUN["generated_at"], (
        "the stamp must name the run the factors were read from, not the run the page was "
        "published from; got {!r}".format(stamp.get("run_generated_at")))
    assert stamp.get("accounts") == 71
    assert stamp.get("customer_years") == 500.0


def test_the_published_product_is_the_stamped_book_s_own(built):
    """The two factors are ONE book, asserted as arithmetic rather than as a comment.

    MUTATION: multiply `required_multiple_smallest_leg` by any other run's customer-years -- the
    exact move the staging record made -- and this leg reds. It is the whole defect, stated as the
    only thing about it a machine can check.
    """
    stamp = built["the_book_these_figures_are_denominated_in"]
    assert built["this_book_customer_years"] == stamp["customer_years"], (
        "`this_book_customer_years` and the stamp disagree, so the block is describing two books "
        "and a reader cannot tell which one the multiple belongs to")
    assert built["required_customer_years_smallest_leg"] == pytest.approx(
        built["required_multiple_smallest_leg"] * stamp["customer_years"]), (
        "the published requirement is not this book's multiple times THIS book's customer-years, "
        "so it is a ratio across two runs and not a quantity")


def test_the_block_says_a_later_run_needs_the_multiple_RE_COMPUTED_not_re_scaled(built):
    """The refusal names its reason, which is how a reader learns the move is illegal at all.

    A stamp alone is inert: it tells you which book, not that carrying the multiple to another one
    is forbidden. This leg holds the sentence that says so, keyed to the two words that carry it.
    """
    why = built.get("why_the_multiple_cannot_be_re_denominated") or ""
    assert "RE-COMPUTED" in why, (
        "the block stamps its book but never says what a reader with a newer run should do, which "
        "leaves re-scaling the obvious move")
    assert "not a quantity" in why


def test_the_stamp_in_the_published_feed_is_one_the_producer_can_still_emit():
    """THE HALF-LANDED LEG. The feed carried this stamp while no committed code emitted it.

    Reds if the published block has a stamp the producer would not write, or has lost one the
    producer does write -- either direction being the feed and the code disagreeing about what is
    published. It reads the KEYS, never the values: the feed's book is a different run from the
    fixture's by construction.
    """
    if not FEED.exists():
        pytest.skip("no published value_arms feed in this tree")
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    block = (((feed.get("current_world") or {}).get("selection_leg") or {})
             .get("what_would_settle_the_sign") or {}).get("can_a_book_that_size_be_built") or {}
    if not block.get("available"):
        pytest.skip("this feed publishes no buildability verdict to check the stamp of")
    emitted = set(gva._can_this_book_be_built(A_RUN, PRICED_ROWS))
    published = set(block)
    assert "the_book_these_figures_are_denominated_in" in emitted, (
        "the producer no longer emits the stamp the published feed carries -- the feed was landed "
        "and the code was not, so the next regeneration drops it silently")
    assert not (published - emitted), (
        "the published block carries keys no committed producer emits, which is the half-landed "
        "shape this leg exists for: {}".format(sorted(published - emitted)))


@pytest.mark.parametrize("what_is_missing, run", [
    ("no run at all", None),
    ("customer-years", dict(A_RUN, household_side={"control_arm": {}})),
    ("the retained-record count", dict(A_RUN, gross_to_net_bridge={"control_arm": {}})),
    ("the whole household side", dict(A_RUN, household_side={})),
])
def test_no_refusal_anywhere_in_the_partition_carries_a_stamp(what_is_missing, run):
    """FAILS CLOSED, over the WHOLE refusal partition rather than one leg per branch.

    A stamp naming a book whose size could not be read is worse than no stamp: it certifies
    provenance for a figure that was never computed. So the property is over every way this
    function can refuse, not over the one a single fixture happens to reach.

    WRITING IT PER-BRANCH IS WHAT FOUND THE DEAD ONE. The first draft drove only the missing
    customer-years case and its mutation -- default the missing value and disable the guard --
    stayed GREEN. It was not an equivalence and it was not a missing assertion: the guard is
    UNREACHABLE. `_can_this_book_be_built` calls `retained_settlement_records_per_customer_year`
    two statements earlier, and that function reads `household_side.control_arm.customer_years`
    too and raises on exactly the same condition, so the later `if not customer_years` branch and
    the reason it names -- "this run publishes no `household_side.control_arm.customer_years`" --
    can never be emitted by any input. The branch is left in place as a guard against the rate
    function ever changing which arm it reads; what is NOT left is a leg implying it was tested.
    Recorded here rather than in a comment on the producer because this is where the evidence is.
    """
    block = gva._can_this_book_be_built(run, PRICED_ROWS)
    assert block.get("available") is False, (
        "a run missing {} produced a verdict rather than a refusal".format(what_is_missing))
    assert block.get("reason"), "a refusal that does not name its reason cannot be checked"
    assert "the_book_these_figures_are_denominated_in" not in block, (
        "this refusal carries a provenance stamp for a book it could not size")
