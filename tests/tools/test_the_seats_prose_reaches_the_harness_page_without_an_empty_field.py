"""The seat's own prose reaches the Harness page without reading as an empty field.

THE DEFECT (15 Nov 2026). Five direction landings in a row (00:54 to 15:51Z) were refused by
`site/test_no_published_page_renders_an_empty_field.py`, so origin's DIRECTION.yaml stayed a day
old. The page was `site/harness/index.html` and the text was one problem's `what`: "director_inputs
since 13 Nov 00:00Z reads [] under both ..." and "This brief's director_inputs is [], and ...". The
seat wrote a literal empty list, and the sweep's "empty brackets" shape read it as a hole, as a
reader would. The rows are append-only on origin, so `tools/generate_delivery_page.reader_text`
writes the value in words where the prose is published.

The control uses THE SWEEP'S OWN SHAPES, so it keys to the property the sweep refuses on and not to
the word "[]". Reproduced only with the candidate files STAGED: the sweep reads the git index, not
the working tree, and a run over unstaged files reads origin's bytes and passes.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site"))

from test_no_published_page_renders_an_empty_field import empty_fields  # noqa: E402

from tools import generate_delivery_page as gen  # noqa: E402

# The 15 Nov sentence, as the seat wrote it into docs/direction/decisions.jsonl.
REAL = ("THE MACHINE'S, NEW. The console capture filed the phase-close skill's own text as the "
        "director's verbatim words. 23:26 14 Nov: Corrected. director_inputs since 13 Nov 00:00Z "
        "reads [] under both origin's and the shared tree's delivery_seat.py. 00:24 15 Nov: Holds. "
        "This brief's director_inputs is [], and 98a1f7728 is on origin.")


@pytest.fixture
def published(monkeypatch):
    monkeypatch.setattr(gen.direction_mod, "read_wrong_triage", lambda: ([], "read"))

    def publish(what: str) -> str:
        out = gen.reader_feed(gen._distinct_problems([{"at": "2026-11-15T00:23:57+00:00", "what": what,
                                       "corrected": True}]))
        return out["problems"][0]["what"]
    return publish


def test_the_real_sentence_carries_the_shape_the_sweep_refuses():
    """The fixture can fail: unrendered, the 15 Nov text is exactly what the sweep refused."""
    assert [h for h in empty_fields(REAL) if h.startswith("empty brackets")], empty_fields(REAL)


def test_the_published_problem_text_shows_no_empty_field(published):
    assert empty_fields(published(REAL)) == [], published(REAL)
    assert "reads an empty list under both" in published(REAL)


def test_a_real_hole_is_not_written_over(published):
    """The renderer must not hide a hole: `( )` and `[ ]` are what an emptied slot leaves."""
    for hole in ("same houses ( ), different", "the list [ ] was"):
        assert empty_fields(published(hole)), published(hole)
    for kept in ("a call x[] stays", "nested [[]] stays"):
        assert published(kept) == kept


# 8503daa89's own subject, which quoted the 15 Nov text and so re-opened the defect on the commit
# list: every site commit was refused while it sat in the page's twelve newest (to 16 Nov ~06:50).
SUBJECT = ('The direction record lands past the empty-field sweep: the Harness page printed the '
           'seat\'s literal "reads []" in a problem\'s text, which the sweep refuses as a hole, so a '
           'bare [] is now published as "an empty list" and a control turns red if it comes back')
SECTIONS = ("what_it_did", "what_it_decided", "what_it_got_wrong", "what_next",
            "the_queues_link_to_the_map", "the_number_the_programme_rests_on",
            "the_most_a_carbon_score_could_be_worth",
            "the_most_the_products_beyond_price_could_be_worth")


def test_every_string_the_feed_publishes_reaches_the_reader_without_an_empty_field(monkeypatch):
    """Both legs over the whole feed, through `build` itself: a quoted `[]` in ANY section (a commit
    subject here) publishes as words, and a real hole (`( )`, `[ ]`) still reaches the sweep."""
    assert [h for h in empty_fields(SUBJECT) if h.startswith("empty brackets")]
    for name in SECTIONS:
        monkeypatch.setattr(gen, name, lambda: {"commits": [{"subject": SUBJECT}],
                                                "holes": ["same houses ( ), different",
                                                          "the list [ ] was"]})
    data = gen.build()
    for name in SECTIONS:
        assert empty_fields(data[name]["commits"][0]["subject"]) == [], (name, data[name])
        assert all(empty_fields(h) for h in data[name]["holes"]), (name, data[name])
