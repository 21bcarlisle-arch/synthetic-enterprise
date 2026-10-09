"""The front-door diagram stays a picture: no statistic joins it.

The director, 2026-10-09 (docs/staging/DIRECTOR_RULING_FRONT_DOOR_STAYS_SIMPLE_AND_EXPLORATION_
GOES_DEEPER_2026-10-09.md, item 1): "I don't want the diagram to be full of stats -- just a simple
visual way to understand what we are doing." No counter, tally or finding count joins it, ever;
depth goes into L2 sheets behind each band, not onto the door.

WHAT A STATISTIC IS HERE. A number that counts or measures something: "168k periods", "~200
homes", "9-year". Not a statistic: a date or a span of years ("2016-25", "2021-22", a canon stamp)
and a label that happens to carry a digit ("Tier-1", "v4"). Those are stripped first; whatever
digit is left is a statistic.

THE FOUR ALREADY THERE. The director-approved SVG (72bbc9339, 2026-07-23) carried four before the
ruling. The ruling says nothing numeric is ADDED; it does not order these out, so they are listed
below rather than deleted from his diagram. The list may only shrink: removing one stays green,
and a new one, or one of these four reworded into a different number, is refused.
"""
from __future__ import annotations

import re

from test_the_published_bytes_reader import published_blob, refuse_working_tree_reads

DIAGRAM_REL = "site/assets/model-on-a-page.svg"

PRESENT_BEFORE_THE_RULING = frozenset({"168k", "~200", "~12", "9-year"})

_TEXT = re.compile(r"<text\b[^>]*>(.*?)</text>", re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_DATE = re.compile(r"\b(?:19|20)\d\d(?:[-–](?:\d\d){1,2}){0,2}\b")
_LABEL = re.compile(r"\b(?:Tier|v)-?\d+\b")
_STATISTIC = re.compile(r"[~≈<>]?\d[\d,.]*(?:[kKmM%]|-\w+)?")


def statistics_in(text: str) -> list[str]:
    """Every number in `text` that counts or measures something, in order of appearance."""
    text = _LABEL.sub(" ", _DATE.sub(" ", text))
    return _STATISTIC.findall(text)


def diagram_text(svg: str) -> str:
    return "\n".join(_TAG.sub("", t) for t in _TEXT.findall(svg))


def test_the_detector_can_say_yes_and_can_say_no():
    assert statistics_in("Coverage knees measured: ~200 homes, ~12 segments.") == ["~200", "~12"]
    assert statistics_in("42 findings open") == ["42"]
    assert statistics_in("a 9-year record of 168k periods") == ["9-year", "168k"]
    assert statistics_in("2016–25 record · Collateral death loop (2021–22 replay)") == []
    assert statistics_in("director-canon 2026-07-23 · v4 · Tier-1 bill accuracy") == []


def test_the_published_diagram_has_text_to_read():
    texts = _TEXT.findall(published_blob(DIAGRAM_REL))
    assert len(texts) > 20, (
        "{} has {} <text> elements; the diagram's words are no longer where this control reads "
        "them, so it would pass on any picture".format(DIAGRAM_REL, len(texts)))


def test_no_statistic_joins_the_front_door_diagram():
    found = statistics_in(diagram_text(published_blob(DIAGRAM_REL)))
    new = sorted(set(found) - PRESENT_BEFORE_THE_RULING)
    assert not new, (
        "the front-door diagram now carries {} -- a statistic the director ruled off the door on "
        "2026-10-09 ('just a simple visual way to understand what we are doing'). Put the number "
        "on the band's L2 sheet or the surface that holds it, not on the picture.".format(new))


def test_no_subject_of_this_file_is_read_from_the_working_tree():
    refuse_working_tree_reads(__file__, (DIAGRAM_REL,))
