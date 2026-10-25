"""The pack census counts flags, skips the legend, and adds up each page's own tally."""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import pack_verification_census as pvc

PACK = "DIRECTOR_EVIDENCE_TEST_TOPIC_2026-10-25.md"


def _tree(tmp: Path, page_body: str | None) -> Path:
    adv = tmp / pvc.ADVISOR
    adv.mkdir(parents=True)
    (adv / PACK).write_text(
        "- Items marked [unverified] are not claims until you source them.\n"
        "A figure **[unverified]** and another [UNVERIFIED for GB].\n"
        "A third [unverified].\n", encoding="utf-8")
    (tmp / pvc.NOTES).mkdir(parents=True)
    if page_body is not None:
        (tmp / pvc.NOTES / "test_topic.md").write_text(
            f"**Knowledge:** test-topic\n\nDrafted from `{PACK}`.\n{page_body}", encoding="utf-8")
    return tmp


def test_the_legend_is_not_a_flag_and_every_tag_shape_is(tmp_path):
    row = pvc.build(_tree(tmp_path, None))["packs"][0]
    assert row["items"] == 3 and row["open"] == 3 and not row["drafted"]


# Every tally shape the 28 pages of 25 Oct actually use, read off the pages.
@pytest.mark.parametrize("line, want", [
    ("**Counts: 15 confirmed, 2 corrected, 4 still open.**", (15, 0, 2, 0, 4)),
    ("**Counts: confirmed 4 (1, 3, 4, 13) · corrected 2 (2, 5) · still open 7 (6-12).**", (4, 0, 2, 0, 7)),
    ("Confirmed 0, corrected 3, open 33. Corrections and checks:", (0, 0, 3, 0, 33)),
    ("**Count: 2 confirmed, 1 partly confirmed, 3 corrected, 2 still open.**", (2, 1, 3, 0, 2)),
    ("confirmed 8 (1, 2, 3, 4, 5, 6, 13, 14); partly confirmed 1 (8); still open 4 (7, 10, 11, 12); "
     "still unpublished 1 (9).", (8, 1, 0, 1, 4)),
    ("**Counts: 7 confirmed (covering 24 figures), 0 corrected, 5 still open.**", (7, 0, 0, 0, 5)),
    ("Tally for the index: confirmed 6 · corrected 3 · open 9 (incl. 2 unpublished).", (6, 0, 3, 2, 7)),
])
def test_each_tally_shape_in_use_is_read(line, want):
    got = pvc.read_tally(line)
    assert got and tuple(got[k] for k in ("confirmed", "partly_confirmed", "corrected", "unpublished",
                                          "open")) == want


def test_MUTATION_a_tally_on_the_page_moves_the_row(tmp_path):
    body = "## Verification\n\nCounts: confirmed 1, corrected 1, still open 1.\n"
    row = pvc.build(_tree(tmp_path, body))["packs"][0]
    assert (row["confirmed"], row["corrected"], row["open"], row["tally_recorded"]) == (1, 1, 1, True)
    assert row["pages"][0]["knowledge"] == "test-topic"


def test_the_last_tally_wins_so_a_later_pass_supersedes(tmp_path):
    body = "Counts: confirmed 0, corrected 0, open 3.\n\nLater pass. Counts: confirmed 3, corrected 0, open 0.\n"
    row = pvc.build(_tree(tmp_path, body))["packs"][0]
    assert (row["confirmed"], row["open"]) == (3, 0)


def test_a_page_with_no_tally_shows_every_flag_open_and_says_so(tmp_path):
    row = pvc.build(_tree(tmp_path, "This figure was confirmed by Ofgem.\n"))["packs"][0]
    assert row["drafted"] and not row["tally_recorded"] and row["open"] == 3 and row["counted"] is None


def test_an_empty_census_is_refused_not_published(tmp_path):
    (tmp_path / pvc.ADVISOR).mkdir(parents=True)
    (tmp_path / pvc.NOTES).mkdir(parents=True)
    census = pvc.build(tmp_path)
    assert census["packs"] == [] and pvc.write(census, tmp_path) is False


def test_the_real_packs_are_found_and_some_are_tallied():
    """Vacuity guard: a glob matching nothing, or a parser reading no page, would publish a census
    that says nothing was checked."""
    census = pvc.build()
    assert len(census["packs"]) >= 20
    assert any(r["tally_recorded"] for r in census["packs"])
