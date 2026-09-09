#!/usr/bin/env python3
"""A page's review date must describe the body that page actually serves.

THE DEFECT THIS FIRES ON, AND IT WAS LIVE AT HEAD ON 2026-09-09 ON SIX PAGES.

`site/knowledge/review_state.py` answers one question -- when was this last checked against the
world -- from `site/data/knowledge_wholesale.json` -> `topics[].reviewed.last_verified`. The
BODY the reader is served lives somewhere else: `site/data/knowledge_<topic>.json` for most
pages, `site/data/knowledge_topics.json` for the consolidated ones. The review record is keyed
to the TOPIC; the body is keyed to a FILE. Nothing tied them.

So a body can MOVE HOUSE and the review record stays behind, still advertising a check that
covered text no reader can reach:

  * 2026-08-19 (`bedb08ea4`) -- six pages were checked against source, two of them corrected.
    The bodies checked were the entries in `knowledge_topics.json`. `reviewed.last_verified`
    became 2026-08-19 for all six.
  * 2026-08-24 (`0aa1c6d22`) -- six NEW files, `knowledge_<topic>.json`, were written "to
    replace a stub", and the pages were pointed at them. Wholly different text: 10-39% headline
    word overlap, two with a different title. The graph was not touched.
  * 2026-09-09 (`2a33bfa4f`) -- the reviewed bodies were deleted as unread second copies. That
    deletion was right, and it removed the last artefact from which this was discoverable.

Between 08-24 and today every one of the six rendered "Reviewed 2026-08-19" over a body nobody
had ever checked, citing sources fetched for a page that no longer existed. Nothing went red:
the whole `site/knowledge/` suite passed on 2026-09-09 with all six badges false, and passed
again unchanged after they were corrected. That is what a control keyed to nothing looks like.

THE RULE, and it is one comparison over data that already exists:

    if a topic advertises `reviewed.last_verified`, the body that page serves must not say it
    was `written` after that date.

Keyed to the property, not to today's answer: it stays silent while a check covers its body and
speaks the moment a body outruns its check, whoever writes it and whenever.

WHY THE UNGRADED SET IS AN EQUALITY AND NOT A SKIP. The comparison needs the body's own
`written` date, so a body that carries none cannot be graded -- which is a dodge if it is a
silent skip (drop `written`, and the page is excused forever). `test_the_ungraded_set_is_exactly
_what_it_says` pins that set by equality, so a page falling OUT of grading is itself a red. The
two that are legitimately ungraded are named there with their reasons.

NOT a check on whether a page is correct, or on whether the check was any good. It grades one
thing: that the date a reader is shown refers to the words that reader is shown.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
DATA = SITE / "data"
GRAPH = DATA / "knowledge_wholesale.json"

#: Pages whose body carries no `written` date, so the comparison has no second term. Named with
#: the reason, and held by equality below -- this is a printed gap, never a silent skip.
UNGRADED = {
    # its body IS the topic graph, which every topic's record also lives in; that file carries a
    # claim_freshness with no `written` date and a note explaining why its review date is held
    # still. Tying it to itself would grade the record against the record.
    "electricity-wholesale",
    # its body is `weather_cells.json`, a data artefact rather than a written Knowledge record;
    # it carries no claim_freshness at all, so there is no claim of authorship to compare.
    "weather-cells",
}


def _graph() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def _body_feed(slug: str) -> Path | None:
    """The single data feed a page serves its BODY from, read out of that page's own markup.

    Scanned, never listed, for the reason `test_the_consolidated_pages_render_their_own_record`
    gives: a hand-listed map is a control pinned to today's wiring, and goes quiet on exactly
    the page that moves. The topic graph is discounted because every page fetches it for the
    review badge and the nav -- it is not where any page's body comes from except one.
    """
    door = HERE / slug / "index.html"
    if not door.is_file():
        return None
    feeds = set(re.findall(r"\.\./\.\./(data/[a-z0-9_]+\.json)", door.read_text(encoding="utf-8")))
    feeds.discard("data/knowledge_wholesale.json")
    if len(feeds) == 1:
        return SITE / feeds.pop()
    return GRAPH if not feeds else None


def _written(slug: str) -> str | None:
    """The date the body this page serves says it was written, or None if it does not say."""
    feed = _body_feed(slug)
    if feed is None or not feed.is_file():
        return None
    doc = json.loads(feed.read_text(encoding="utf-8"))
    if feed.name == "knowledge_topics.json":
        doc = (doc.get("pages") or {}).get(slug) or {}
    freshness = (doc.get("meta") or {}).get("claim_freshness") or {}
    written = freshness.get("written")
    return written[:10] if isinstance(written, str) else None


def _pages() -> list[str]:
    return [t["id"] for t in _graph()["topics"] if t.get("kind") == "page"]


def _gradeable() -> list[str]:
    return [s for s in _pages() if _written(s)]


def test_the_graded_set_has_not_emptied():
    """POPULATION FLOOR. A control keyed to a structure that moved reports PASS on an empty
    subject list, and this one derives its subjects from markup and from a `written` field --
    two things that can both stop being found. Fourteen of sixteen topics are gradeable."""
    graded = _gradeable()
    assert len(graded) >= 14, f"only {len(graded)} pages gradeable: {graded}"


def test_the_ungraded_set_is_exactly_what_it_says():
    """The fail-open this closes: dropping `written` from a body would excuse that page for
    ever, silently. Falling out of grading is therefore itself a failure, and the two pages
    that legitimately cannot be graded are named in UNGRADED with their reasons."""
    ungraded = {s for s in _pages() if not _written(s)}
    assert ungraded == UNGRADED, (
        f"the set of pages that cannot be graded changed: {ungraded} != {UNGRADED}. A page that "
        "lost its body's `written` date is not excused -- give the body a written date, or say "
        "here why it cannot have one."
    )


@pytest.mark.parametrize("slug", _gradeable())
def test_no_page_advertises_a_check_older_than_the_body_it_serves(slug: str):
    """THE DEFECT, BY NAME: six pages advertised "Reviewed 2026-08-19" over bodies written
    2026-08-24, for sixteen days, with every test in this directory green."""
    reviewed = {t["id"]: t for t in _graph()["topics"]}[slug].get("reviewed") or {}
    last_verified = reviewed.get("last_verified")
    if not last_verified:
        return  # no date advertised: review_state already calls this UNCHECKED, fail-closed
    written = _written(slug)
    assert written <= last_verified[:10], (
        f"{slug} advertises a check on {last_verified[:10]} but the body it serves says it was "
        f"written on {written}. The reader is shown a date that describes different words. "
        f"Either re-check the body being served and move the date, or clear `last_verified` so "
        f"the page reads 'Written, awaiting check'."
    )


def test_MUTATION_a_check_that_predates_its_body_fires(monkeypatch):
    """Poison round, so 'passed' cannot mean 'looked at nothing'. Push one body's written date
    past its check and the comparison must red -- this is the exact shape that was live.

    THE VICTIM MUST ADVERTISE A DATE. Written first with `_gradeable()[0]`, which is
    `carbon-price` -- one of the six, whose `last_verified` this same commit cleared. The
    comparison returned early and the poison did not fire, reading exactly like a dead rule.
    That is the ambiguity a poison round exists to remove, and it removed it about itself.
    """
    graph = {t["id"]: t for t in _graph()["topics"]}
    victim = next(s for s in _gradeable()
                  if (graph[s].get("reviewed") or {}).get("last_verified"))
    monkeypatch.setitem(globals(), "_written", lambda slug: "2099-01-01")
    with pytest.raises(AssertionError, match="written on 2099"):
        test_no_page_advertises_a_check_older_than_the_body_it_serves(victim)


def test_MUTATION_the_rule_is_not_vacuous_on_the_real_record():
    """The OTHER thing 'passed' can mean: every page skipped the comparison because none of them
    advertises a date. At least eight pages must actually reach the assertion."""
    graph = {t["id"]: t for t in _graph()["topics"]}
    compared = [s for s in _gradeable() if (graph[s].get("reviewed") or {}).get("last_verified")]
    assert len(compared) >= 8, (
        f"only {len(compared)} pages carry a review date, so the comparison barely runs: {compared}"
    )
