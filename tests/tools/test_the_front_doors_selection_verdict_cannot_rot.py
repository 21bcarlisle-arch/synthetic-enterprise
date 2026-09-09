#!/usr/bin/env python3
"""R15 proof for the front door's selection-leg verdict.

THE DEFECT THIS CLOSES
----------------------
On 2026-09-09 a sweep of every live surface against the nine-seed floor found exactly one
page still stating the personalisation claim with no signal that the money side had been
measured: the front door. Its `NOT YET MEASURED` tag is about the CARBON score, so a reader
met "you create value fastest by knowing each household well" and had no way to tell that
the run separating *choosing better* from *charging more* had already happened and had come
back "we cannot tell". A hypothesis a reader cannot tell has been tested reads as one nobody
has tested yet, which is the more flattering of the two readings and the wrong one.

The remedy was a paragraph. A paragraph is a claim about the CURRENT state of the evidence,
so it rots -- and it rots in the flattering direction if left alone, because a page still
refusing to name a direction after the evidence resolved is understating what we know, and
nobody files a defect against modesty. So the paragraph carries `data-selection-verdict` and
`_check_front_door_selection_verdict` holds it against `value_arms.json`'s own
`current_world.selection_leg.resolved` on every publish.

WHY THE POISON ROUND COMES FIRST
--------------------------------
"The gate passed" means two opposite things -- the page agrees with the feed, or the gate
cannot see either of them. This project has entered that trap through three different doors
in one afternoon. So `test_the_gate_is_reachable_at_all` runs BEFORE any direction is
asserted and proves the gate can be made to fail on the real front door and the real feed;
every test below it is only meaningful because that one is red when poisoned.

WHAT IS CONTROLLED, AND WHAT IS NOT
-----------------------------------
This controls the GATE, not the render: it proves the published sentence cannot silently
disagree with the run. Whether that paragraph is on a page a reader can open is a separate
question and has its own control -- `PUBLISH_VERDICT_CHECKS` declares the reader-facing page
for every blocking check, and `test_publish_blockers_guard_a_reachable_page.py` fails if this
one names a page nobody can reach.
"""
from __future__ import annotations

import json

import pytest

from tools import generate_dashboard_data as gdd

WITHHELD = 'data-selection-verdict="withheld"'
RESOLVED = 'data-selection-verdict="resolved"'


def _feed(resolved):
    """The smallest feed shape the gate reads, at whichever verdict the caller wants."""
    return {"current_world": {"selection_leg": {"resolved": resolved}}}


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text)
    return p


def _feed_file(tmp_path, obj, name="value_arms.json"):
    return _write(tmp_path, name, json.dumps(obj))


# ---------------------------------------------------------------------------
# THE POISON ROUND. Nothing below this is worth reading until it passes.
# ---------------------------------------------------------------------------
def test_the_gate_is_reachable_at_all(tmp_path):
    """On the REAL front door and the REAL feed, the gate passes -- and flipping ONLY the
    feed's verdict turns it red. Two assertions, one subject: a gate that returned True
    unconditionally, or that never found the attribute, fails the second one.
    """
    assert gdd._check_front_door_selection_verdict() is True, (
        "the shipped front door disagrees with the shipped feed about the selection leg"
    )

    live = json.loads(gdd.VALUE_ARMS_FEED_PATH.read_text())
    live["current_world"]["selection_leg"]["resolved"] = "level"
    poisoned = _feed_file(tmp_path, live)
    assert gdd._check_front_door_selection_verdict(feed_path=poisoned) is False, (
        "the feed resolved the leg and the real front door still says 'withheld', and the "
        "gate did not notice -- it is reading neither side"
    )


# ---------------------------------------------------------------------------
# BOTH DIRECTIONS. The vocabulary has to be able to say what is true either way.
# ---------------------------------------------------------------------------
def test_a_withheld_page_agrees_with_an_unresolved_feed(tmp_path):
    door = _write(tmp_path, "index.html", "<p " + WITHHELD + ">we cannot tell</p>")
    assert gdd._check_front_door_selection_verdict(
        front_door_path=door, feed_path=_feed_file(tmp_path, _feed(None))
    ) is True


def test_a_resolved_page_agrees_with_a_resolved_feed(tmp_path):
    """The `resolved` half of the grammar is WRITABLE from the day this ships. Its absence
    is the defect this file's sibling gate carried for six days in August: the mix-claim
    refusal offered only `gt` while the book was domestic, so the true claim could not be
    written and the refusal read as "you typed it wrong".
    """
    door = _write(tmp_path, "index.html", "<p " + RESOLVED + ">the level explains it</p>")
    assert gdd._check_front_door_selection_verdict(
        front_door_path=door, feed_path=_feed_file(tmp_path, _feed("level"))
    ) is True


@pytest.mark.parametrize(
    "page_attr,feed_resolved,why",
    [
        (WITHHELD, "level", "the run named a direction and the page still refuses to"),
        (RESOLVED, None, "the page names a direction the run does not support"),
    ],
)
def test_a_page_that_disagrees_with_the_run_fails(tmp_path, page_attr, feed_resolved, why):
    door = _write(tmp_path, "index.html", "<p " + page_attr + ">a claim</p>")
    assert gdd._check_front_door_selection_verdict(
        front_door_path=door, feed_path=_feed_file(tmp_path, _feed(feed_resolved))
    ) is False, why


# ---------------------------------------------------------------------------
# FAIL-CLOSED. "Cannot check" is never "check passed" -- R15's fail-silent killer.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "page_html,why",
    [
        ("<p>we cannot tell</p>", "no attribute at all -- the paragraph was rewritten"),
        ('<p data-selection-verdict="probably">x</p>', "a word outside the vocabulary"),
        ('<p data-selection-verdict="">x</p>', "an empty verdict"),
    ],
)
def test_an_unwritable_or_missing_claim_fails(tmp_path, page_html, why):
    """A claim the gate cannot parse must read as NO CLAIM FOUND and fail. If it read as a
    pass, deleting the attribute would be the cheapest way to silence the gate -- and the
    paragraph would go on making its claim to every reader with nothing holding it.
    """
    door = _write(tmp_path, "index.html", page_html)
    assert gdd._check_front_door_selection_verdict(
        front_door_path=door, feed_path=_feed_file(tmp_path, _feed(None))
    ) is False, why


@pytest.mark.parametrize(
    "feed_text,why",
    [
        ("{ not json", "an unparseable feed"),
        (json.dumps({}), "a feed with no current_world"),
        (json.dumps({"current_world": {"selection_leg": {}}}),
         "a selection_leg carrying no `resolved` field -- absence of the field is NOT "
         "absence of a claim on the page"),
    ],
)
def test_an_unreadable_feed_fails(tmp_path, feed_text, why):
    door = _write(tmp_path, "index.html", "<p " + WITHHELD + ">we cannot tell</p>")
    assert gdd._check_front_door_selection_verdict(
        front_door_path=door, feed_path=_write(tmp_path, "value_arms.json", feed_text)
    ) is False, why


def test_a_missing_front_door_fails(tmp_path):
    assert gdd._check_front_door_selection_verdict(
        front_door_path=tmp_path / "nope.html",
        feed_path=_feed_file(tmp_path, _feed(None)),
    ) is False, "an unreadable front door is a FAILED check, not a pass"


def test_a_missing_feed_fails(tmp_path):
    door = _write(tmp_path, "index.html", "<p " + WITHHELD + ">we cannot tell</p>")
    assert gdd._check_front_door_selection_verdict(
        front_door_path=door, feed_path=tmp_path / "nope.json"
    ) is False, "an unreadable feed is a FAILED check, not a pass"


# ---------------------------------------------------------------------------
# IT ACTUALLY BLOCKS. A gate nothing consults is a gate that cannot fail.
# ---------------------------------------------------------------------------
def test_the_gate_is_declared_as_a_publish_blocker():
    """Keyed to the DECLARATION, not to a copy of the conjunction: the sibling control
    `test_publish_blockers_guard_a_reachable_page.py` parses generate()'s verdict out of the
    source and fails if a blocking check is undeclared or a declaration is stale. This one
    only asserts the entry exists and names a page, so the two do not become two definitions
    of one list.
    """
    entry = gdd.PUBLISH_VERDICT_CHECKS.get("_check_front_door_selection_verdict")
    assert entry is not None, (
        "the selection-verdict gate is in generate()'s verdict but declares no reader-facing "
        "page, so nothing can tell whether it guards anybody"
    )
    page, what = entry
    assert page == "/" and what
