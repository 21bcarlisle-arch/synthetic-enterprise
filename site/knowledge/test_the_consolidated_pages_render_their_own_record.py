#!/usr/bin/env python3
"""Every page that READS the consolidated Knowledge record renders its own body from it.

THE DEFECT THIS FIRES ON, AND IT IS NOT HYPOTHETICAL. `acquisition-and-retention-economics`
shipped on 2026-08-28 as the first page to read `site/data/knowledge_topics.json`, and no test
anywhere named it. `grep -rln acquisition-and-retention-economics --include=*.py site/ tests/
tools/` returned nothing on 2026-08-30. The page carries a deliberate FAIL-CLOSED branch for a
missing slug -- "The page exists; its content does not." -- and nothing checked which branch it
took. So a page could be added to the record with a typo'd slug, or a page's html copied to a
new directory with its slug left pointing at the page it was copied FROM, and both ship green.
The second is not hypothetical either: it is exactly how the two pages this test was written
alongside were created.

The rule is not "the page loads". It is:

    each page that fetches the consolidated record renders THAT page's own headline -- not the
    fail-closed sentence, and not a neighbour's.

WHY THE CONSUMER SET IS SCANNED AND NEVER LISTED. A hand-listed set is a control pinned to
today's answer: migrate a page to the record and the control stays quiet on it forever. The set
is derived from the pages' own markup, so a page that starts reading the record is graded from
that moment without anyone remembering to add it. `test_the_consumer_set_has_not_emptied` is
the floor that stops the scan going quiet by finding nothing -- the failure mode where a
control keyed to a structure that moved reports PASS on an empty subject list.

WHY THE ID ASSERTION IS SEPARATE FROM THE RENDER ASSERTION. The shared harness'
`document.getElementById` autocreates a stub for any id it is asked for, so a page that DELETED
an element would still report that element rendered (`docs/staging/WORKER_FINDING_THE_RENDER_
HARNESS_AUTOCREATES_THE_ELEMENT_A_DELETED_PARAGRAPH_WOULD_LOSE_2026-08-29.md`). Every id read
here is therefore also asserted to exist in the page's own markup, against the file, before its
rendered content is judged. Without that half, deleting `<div id="r-headline">` passes.

THE SHADOW ENTRIES ARE GONE, and the exception list went with them. Six keys in `pages` used to
be rendered by nothing -- `gb-electricity-market`, `merit-order-residual-demand`,
`gas-wholesale`, `carbon-price`, `imbalance-cashout-settlement` and `hedging-forward-market`
each had a per-page json that their html actually fetches, and a SECOND, DIFFERENT body here.
Declared rather than fixed on 2026-08-30 (`WORKER_FINDING_THE_CONSOLIDATED_KNOWLEDGE_RECORD_
HOLDS_A_SECOND_STALER_COPY_OF_SIX_PAGES_2026-08-30.md`) so the gap was a number this file
printed. Re-measured 2026-09-09: still all seven rungs differing on all six, two of them
differing in the page TITLE, and the per-page copy carrying every field its shadow did -- so
the six were DELETED from the record rather than kept under a declaration.

Why deletion beat declaration. A declared exception makes the trap visible; it does not disarm
it. The record's own `_note` invites the migration, and the body a migrator would reach for was
the older draft sitting right there under the right key. Nothing published was ever wrong --
the reader always got the newer text -- and that is precisely what made it dangerous, because
the copy nobody reads is the copy that can rot with no reader to notice. Removing it collapses
one fact to one home, which is the only remedy this project has ever found for that shape.

What replaced the list is a STRONGER claim, not a weaker one: the record's key set must EQUAL
the scanned consumer set. Before, six named keys were permitted to render nowhere and a seventh
would have been caught; now none is permitted. A future migration is still welcome and is still
a content change -- register the page's key here with the body its page serves TODAY, never the
body git shows used to be here.

R15 MUTATIONS, all run against a copy of the tree:
  * point one page's `pages[...]` lookup at another page's slug ->
    `test_each_page_renders_its_own_headline_and_not_a_neighbours` reds; the fail-closed branch
    does not catch it, because the fetch succeeded and a body rendered.
  * delete `<div id="r-headline">` from one page -> `test_every_rendered_id_exists_in_the_markup`
    reds while every render assertion still passes, which is the whole reason that test exists.
  * add a key to `pages` that no page fetches -> `test_the_record_holds_exactly_the_pages_that
    _render_it` reds. This is the leg that used to be satisfiable by writing the new key into
    SHADOW_ENTRIES, and it is why the exception list had to go rather than be emptied in place.
  * drop a consumer's key from `pages` -> the SAME test reds on the other side, before the
    render tests reach it. Both directions of one equality, proven separately, because a
    subset test in either direction passes the mutation aimed at the other.

NOT a check on the CONTENT of any page. What a page says is graded by its sources; this grades
only that what it says reaches the reader.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
LIVE_HARNESS = SITE / "_live_harness.mjs"
RECORD = SITE / "data" / "knowledge_topics.json"
GRAPH = SITE / "data" / "knowledge_wholesale.json"

#: The ids the shared page template writes into, and which a reader loses if any goes missing.
RENDERED_IDS = ("hero-sub", "r-headline", "r-plain", "r-theory", "r-shape",
                "r-evidence", "r-residuals", "r-scope", "wall-note")

#: The page's own fail-closed text, quoted so a page taking that branch is caught by name
#: rather than by a blank string an empty rung would also produce.
FAIL_CLOSED = "is not in the consolidated Knowledge file"

#: There is deliberately NO exception set here. Six keys once sat in one and were deleted from
#: the record on 2026-09-09; see the module docstring. A key that renders nowhere is now a red,
#: not a row.


def _record() -> dict:
    return json.loads(RECORD.read_text())


def _consumers() -> list[str]:
    """Pages whose OWN markup fetches the consolidated record. Scanned, never listed."""
    found = []
    for door in sorted(HERE.glob("*/index.html")):
        if "knowledge_topics.json" in door.read_text():
            found.append(door.parent.name)
    return found


def _render(slug: str) -> dict:
    """Drive the LIVE html for `slug` with the LIVE record, through the shared harness."""
    door = HERE / slug / "index.html"
    assert door.is_file(), f"{slug} reads the record but has no page at {door}"
    feeds = {
        "../../data/knowledge_topics.json": json.loads(RECORD.read_text()),
        "../../data/knowledge_wholesale.json": json.loads(GRAPH.read_text()),
    }
    proc = subprocess.run(
        ["node", str(LIVE_HARNESS), str(door)],
        input=json.dumps(feeds), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[:600]
    return json.loads(proc.stdout)


def test_the_consumer_set_has_not_emptied():
    """POPULATION FLOOR, raised 2026-09-09: five pages read the record. It was three.

    A scan that finds nothing passes every parametrized test below by having no subjects. This
    is the one assertion that cannot be satisfied by the scan's own blindness. Raise the floor
    when pages are migrated; never lower it without saying which page stopped reading the record.

    Raised on the ordinary ground that five is the measured truth and three was two years of
    slack. NOT, as this docstring first claimed, because the equality above would otherwise pass
    vacuously on an emptied record: poisoned on 2026-09-09 by emptying `pages` in a clean
    extract, the equality reds on all five consumers and THIS test still passes. The consumer
    set is scanned from html and does not empty when the record does, so the equality has no
    vacuous case for this floor to cover. Kept as written, with the wrong reason recorded beside
    the right one -- the floor's real job is the parametrized tests below, which genuinely do
    pass by having no subjects.
    """
    consumers = _consumers()
    assert len(consumers) >= 5, f"only {len(consumers)} pages read the record: {consumers}"


def test_the_record_holds_exactly_the_pages_that_render_it():
    """The record's key set EQUALS the scanned consumer set. No exceptions, either direction.

    Keyed to the property, not to today's answer, and to BOTH halves of it because a subset
    test in one direction is blind to the mutation aimed at the other:

      * a key no page fetches is a second home for a fact -- the shape that put six stale
        bodies in here for eleven days with no reader to notice them rotting;
      * a consumer with no key takes the page's fail-closed branch, which the render tests
        below also catch, but this one names the cause instead of the symptom.

    Neither side can pass vacuously, and that was poisoned rather than assumed: emptying
    `pages` in a clean extract reds this test on all five consumers, because the consumer set
    comes from the pages' own html and does not empty when the record does.
    """
    keys = set(_record()["pages"])
    consumers = set(_consumers())
    assert keys == consumers, (
        f"keys no page renders: {sorted(keys - consumers)}; "
        f"pages fetching the record with no key: {sorted(consumers - keys)}. "
        f"An unrendered key is a second home for a fact -- delete it, or migrate its page and "
        f"copy the body that page serves TODAY. A missing key is a fail-closed page.")


@pytest.mark.parametrize("slug", _consumers())
def test_every_rendered_id_exists_in_the_markup(slug: str):
    """The harness autocreates ids, so existence is checked against the FILE, not the render."""
    html = (HERE / slug / "index.html").read_text()
    for element_id in RENDERED_IDS:
        assert re.search(rf'id="{re.escape(element_id)}"', html), (
            f"{slug}/index.html has no element with id={element_id!r}; the harness would "
            f"autocreate it and report it rendered")


@pytest.mark.parametrize("slug", _consumers())
def test_each_page_renders_its_own_headline_and_not_a_neighbours(slug: str):
    """The page reaches its OWN entry in the record -- not a neighbour's, not the error branch."""
    out = _render(slug)
    headline = out.get("r-headline", {}).get("innerHTML", "")
    assert headline, f"{slug} rendered nothing into r-headline"
    assert FAIL_CLOSED not in headline, (
        f"{slug} took its fail-closed branch: its slug is not a key of the record's `pages`")

    own = _record()["pages"][slug]["rungs"]["headline"]["body"]
    #: Compared on a distinctive prefix rather than the whole body, because the template
    #: html-escapes what it writes and the raw body carries characters escaping changes.
    unescaped = headline.replace("&#39;", "'").replace("&amp;", "&").replace("&quot;", '"')
    assert own[:40] in unescaped, (
        f"{slug} rendered a headline that is not its own: {headline[:160]!r}")


@pytest.mark.parametrize("slug", _consumers())
def test_every_rung_reaches_the_reader(slug: str):
    """All seven rungs render something. An empty rung is a page that lost half its argument."""
    out = _render(slug)
    for element_id in RENDERED_IDS:
        body = out.get(element_id, {}).get("innerHTML", "")
        assert body.strip(), f"{slug} rendered nothing into {element_id}"


@pytest.mark.parametrize("slug", _consumers())
def test_the_page_is_in_the_topic_graph(slug: str):
    """A page absent from the graph renders with no review badge and no neighbours."""
    ids = {t["id"] for t in json.loads(GRAPH.read_text())["topics"]}
    assert slug in ids, f"{slug} is a written page with no entry in the topic graph"
