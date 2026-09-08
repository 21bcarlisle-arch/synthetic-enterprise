"""The sampling knowledge page renders, from the file the site actually reads.

THE DEFECT IT SERVES, and it is the one the director named in advance: *"check it actually reaches
the site once that clears rather than assuming."*

The page was written, reviewed and held for a red lane for a day. It would not have rendered if it
had landed. `site/knowledge/how-many-synthetic-households/index.html` fetched a per-page feed of its
own -- `site/data/knowledge_how_many_synthetic_households.json` -- while the knowledge index and
every page written since 2026-08-28 read the CONSOLIDATED `knowledge_topics.json`, whose own note
records the decision to stop growing one file per page. A slug absent from that file is a page that
does not exist as far as the site is concerned.

**The separate feed was not a smaller version of being published. It was not being published.** And
nothing was red, because every check on that page took the per-page JSON as its subject -- the
file that was correct, complete, and read by nobody.

So this drives the REAL door through `site/_live_harness.mjs` against the REAL consolidated feed on
disk. Building a feed here would control the RENDER and say nothing about whether the page is WIRED
to what the site serves, which is the entire defect.

R15 -- the mutations, each naming the defect it catches:

  * remove the `how-many-synthetic-households` key from `knowledge_topics.json` ->
    `test_the_headline_reaches_the_rendered_page` red. This is the exact live defect.
  * repoint the door's fetch back at a per-page feed -> same test red, because the harness
    reports the unresolved url rather than rendering.
  * publish the sample size without the reference population it was measured against ->
    `test_no_sample_size_is_published_without_the_reference_it_was_scored_against` red.

KNOWN BLIND SPOT, inherited and not fixed here: `_live_harness.mjs` AUTO-CREATES any element the
page asks for, so a door that has LOST an element renders perfectly here and blank in a browser.
Filed as `WORKER_FINDING_THE_RENDER_HARNESS_AUTOCREATES_THE_ELEMENT_A_DELETED_PARAGRAPH_WOULD_LOSE`.
`test_the_slug_fails_closed_in_the_doors_own_source` therefore takes the door's SOURCE as its
subject, because the rendered DOM cannot see that class of loss.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR = SITE / "knowledge" / "how-many-synthetic-households" / "index.html"
TOPICS = SITE / "data" / "knowledge_topics.json"
GRAPH = SITE / "data" / "knowledge_wholesale.json"

SLUG = "how-many-synthetic-households"


def _render(topics: dict | None = None) -> dict:
    """Drive the real door and return what it rendered.

    FAIL-CLOSED: a missing harness, an unresolved feed or a script error all raise here. An
    unavailable check is a FAILED check.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    if not DOOR.is_file():
        pytest.fail(f"{DOOR} does not exist, so there is no page to render")

    payload = {
        # THE REAL FILE ON DISK unless a mutation supplies otherwise. This is the whole point:
        # a test-built feed proves the template works and says nothing about whether the page is
        # connected to what the site serves.
        "../../data/knowledge_topics.json": (
            topics if topics is not None else json.loads(TOPICS.read_text(encoding="utf-8"))),
        "../../data/knowledge_wholesale.json": json.loads(GRAPH.read_text(encoding="utf-8")),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(DOOR)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, f"the render harness failed: {proc.stderr[-2000:]}"
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), (
        f"the door asked for a feed this test did not supply ({meta.get('unresolved')}). For THIS "
        "page that is the defect itself: it means the door is still pointed at a per-page feed "
        "rather than the consolidated file the site reads.")
    assert not meta.get("scriptError"), f"the door's own script threw: {meta.get('scriptError')}"
    return out


def _text(element_id: str, topics: dict | None = None) -> str:
    """What the reader meets, taken from innerHTML.

    The template ASSIGNS innerHTML, so `textContent` is empty for every element on every page here
    -- the first version of this file read `textContent` and reported a correctly-rendering page as
    blank. A control that reads the wrong property is indistinguishable from the defect it is
    looking for, which is why it is worth naming."""
    el = _render(topics).get(element_id)
    assert el is not None, f"the door has no `{element_id}` element at all"
    return (el.get("innerHTML") or el.get("textContent") or "").strip()


def test_the_headline_reaches_the_rendered_page():
    """The control the page did not have: does a reader meet any of this?"""
    body = _text("r-headline")
    assert len(body) > 200, (
        f"the headline rendered {len(body)} characters. The page's entry is missing from "
        "`knowledge_topics.json`, so the door fell through to its fail-closed branch and a "
        "reader meets an apology instead of the page.")
    assert "not in the consolidated Knowledge file" not in body, (
        "the door rendered its OWN fail-closed message, which is what a page absent from "
        f"`knowledge_topics.json` looks like. Register {SLUG!r} under `pages`.")


def test_A_MISSING_SLUG_FAILS_CLOSED_rather_than_rendering_a_blank_page_that_looks_written():
    """The mutation that reproduces the live defect, run as a control.

    A page whose data has gone should SAY so. The failure that would matter is a page that renders
    empty and reads as written -- an absence indistinguishable from a short answer."""
    topics = json.loads(TOPICS.read_text(encoding="utf-8"))
    topics["pages"].pop(SLUG, None)
    body = _text("r-headline", topics=topics)
    assert "not in the consolidated Knowledge file" in body, (
        "with its entry removed the door rendered something OTHER than its fail-closed message, "
        f"so a missing {SLUG!r} would reach a reader as a blank page rather than as an absence")


def test_the_slug_fails_closed_in_the_doors_own_source():
    """SUBJECT IS THE SOURCE, because the render harness cannot see this class of loss.

    `_live_harness.mjs` auto-creates any element the page asks for, so an element deleted from the
    door renders fine here and blank in a browser. Two subjects, because one is compromised."""
    source = DOOR.read_text(encoding="utf-8")
    assert "knowledge_topics.json" in source, (
        "the door does not read the consolidated file at all, so nothing it renders is what the "
        "site serves")
    assert SLUG in source, f"the door does not name its own slug {SLUG!r}"
    assert "not in the consolidated Knowledge file" in source, (
        "the door has no fail-closed branch, so a missing entry would render a blank page")


def test_no_sample_size_is_published_without_the_reference_it_was_scored_against():
    """Every financial figure carries its clock; a sample size carries its reference population.

    This page's own history is the reason. Figures measured against 12,000, 20,000, 40,000 and
    120,000-household references, at two different tolerances, were quoted in one column as though
    they were a series. The count is meaningless without the population it reproduces -- at a
    20,000 reference the sample was 34% of it, which is not a compression at all."""
    page = json.loads(TOPICS.read_text(encoding="utf-8"))["pages"][SLUG]
    prose = " ".join(r["body"] for r in page["rungs"].values()) + page["meta"]["one_line"]

    headline = _text("r-headline")
    assert "120,000" in headline, (
        "the rendered headline states a sample size without the reference population it was "
        "measured against, which is the figure's clock")

    # A four-digit count anywhere in the page must have a reference or a tolerance near it.
    for match in re.finditer(r"\b(\d,\d{3})\b", prose):
        window = prose[max(0, match.start() - 400):match.end() + 400]
        assert ("reference" in window or "120,000" in window or "20,000" in window
                or "tolerance" in window or "40,000" in window or "12,000" in window), (
            f"the figure {match.group(1)} appears with no reference population or tolerance "
            "within 400 characters of it, so a reader cannot tell what it is a count against")


def test_the_superseded_figure_is_marked_superseded_and_not_offered_as_the_answer():
    """The director refused 243 as an answer: *"report it as a floor for a partial vector, not an
    answer, and say so wherever it's published."* It may appear; it may not lead."""
    headline = _text("r-headline")
    if "243" not in headline:
        return
    before = headline[:headline.index("243")]
    assert any(w in before.lower() for w in ("earlier", "partial", "superseded", "floor")), (
        "243 appears in the headline with nothing before it marking it as the earlier, partial "
        "figure, so a reader meets it as the answer")


def test_THE_PAGE_CARRIES_NO_UNRENDERED_MARKUP(topics=None):
    """The template renders NEITHER markdown NOR HTML -- it wraps paragraphs in <p> and stops.

    THE DEFECT: this page was drafted with markdown tables and **bold** throughout, because that is
    what every other artefact in this repository uses. It would have published as literal asterisks
    and pipe characters on a page with the company's name on it. Nothing caught it: the content was
    correct, the feed was valid JSON, the page rendered without error, and the check that found it
    was rendering the thing and LOOKING at the output.

    All ten pages that were already registered carry zero markdown, which is the convention this
    makes enforceable rather than tribal."""
    pages = json.loads(TOPICS.read_text(encoding="utf-8"))["pages"]
    offenders = {}
    for slug, page in pages.items():
        body = " ".join(r.get("body", "") for r in (page.get("rungs") or {}).values())
        marks = {"**": body.count("**"), "|": body.count("|"),
                 "`": body.count("`"), "<": body.count("<")}
        bad = {k: v for k, v in marks.items() if v}
        if bad:
            offenders[slug] = bad
    assert not offenders, (
        f"unrendered markup in the consolidated Knowledge file: {offenders}. The shared template "
        "renders neither markdown nor HTML, so each of these reaches a reader as the literal "
        "character.")
