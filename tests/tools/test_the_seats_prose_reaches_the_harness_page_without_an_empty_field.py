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
        out = gen._distinct_problems([{"at": "2026-11-15T00:23:57+00:00", "what": what,
                                       "corrected": True}])
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
