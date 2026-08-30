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

THE SHADOW ENTRIES, and why they are a measurement rather than an exclusion. Six keys in
`pages` are rendered by nothing: `gb-electricity-market`, `merit-order-residual-demand`,
`gas-wholesale`, `carbon-price`, `imbalance-cashout-settlement` and `hedging-forward-market`
each have a per-page json that their html actually fetches, and a SECOND, DIFFERENT body in the
consolidated file. Measured 2026-08-30: all seven rungs differ on all six pages, and the
consolidated copies are the older draft (`last_verified` 2026-08-19 against the live pages'
2026-08-24). Nothing published is wrong today -- the reader gets the newer text -- but anyone
completing the migration the record's own `_note` invites would silently revert six pages to a
draft eleven days stale. Filed as `WORKER_FINDING_THE_CONSOLIDATED_KNOWLEDGE_RECORD_HOLDS_A_
SECOND_STALER_COPY_OF_SIX_PAGES_2026-08-30.md`, not fixed on sight. They are enumerated here so
that the gap is a NUMBER this file prints rather than an absence nobody counts.

R15 MUTATIONS, both run against a copy of the tree:
  * point one page's `pages[...]` lookup at another page's slug ->
    `test_each_page_renders_its_own_headline_and_not_a_neighbours` reds; the fail-closed branch
    does not catch it, because the fetch succeeded and a body rendered.
  * delete `<div id="r-headline">` from one page -> `test_every_rendered_id_exists_in_the_markup`
    reds while every render assertion still passes, which is the whole reason that test exists.

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

#: Keys in the record that NO page renders, each with a per-page json its html fetches instead.
#: See the module docstring. Shrinking this set is the migration; growing it is a regression.
SHADOW_ENTRIES = {
    "gb-electricity-market",
    "merit-order-residual-demand",
    "gas-wholesale",
    "carbon-price",
    "imbalance-cashout-settlement",
    "hedging-forward-market",
}


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
    """POPULATION FLOOR, dated 2026-08-30: three pages read the record.

    A scan that finds nothing passes every parametrized test below by having no subjects. This
    is the one assertion that cannot be satisfied by the scan's own blindness. Raise the floor
    when pages are migrated; never lower it without saying which page stopped reading the record.
    """
    consumers = _consumers()
    assert len(consumers) >= 3, f"only {len(consumers)} pages read the record: {consumers}"


def test_the_shadow_entries_are_exactly_the_unrendered_keys():
    """Every key in the record is either rendered by a page or a DECLARED shadow entry.

    Keyed to the property, not to today's answer: adding a page renders it or forces it to be
    declared, and migrating a page forces the declaration to be withdrawn -- at which point
    whoever migrates it is looking at this docstring, which tells them the consolidated copy is
    the older draft and that the migration is a content change, not a plumbing change.
    """
    keys = set(_record()["pages"])
    unrendered = keys - set(_consumers())
    assert unrendered == SHADOW_ENTRIES, (
        f"unrendered record keys are {sorted(unrendered)}, declared {sorted(SHADOW_ENTRIES)}; "
        f"a new undeclared key renders nowhere, and a withdrawn one is a content change")


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
