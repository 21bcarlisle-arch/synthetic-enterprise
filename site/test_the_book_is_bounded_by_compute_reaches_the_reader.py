"""A reader of the growth curve must be told its height is a COMPUTE budget, not commerce.

THE DEFECT IT SERVES.
`site/data/book_growth.json` already tells a reader that our settlement engine refused four wins
in five, and `engine_bound_statement` already reaches the rendered page. What neither said is
WHAT KIND OF LIMIT that engine is. Its words are *"the SHAPE of this curve is commercial; its
HEIGHT is our machine"* -- and "our machine" is not a checkable claim. A reader who takes it as
"the simulation is complicated" reads a flattened growth curve the way they would read a supplier
that ran out of money, which is precisely the reading the director ruled out on 2026-08-24:
*"a growth curve that's an artefact of our engine is an inconsistency, not a result."*

The two readings carry OPPOSITE instructions. A supplier that ran out of money is a result to be
reported. A box that ran out of wall clock is a harness limit to be lifted. The page could not
distinguish them, so this file makes the page say which one it is.

WHY THE SUBJECT IS THE RENDERED DOM AND NOT THE JSON. Same class as
`test_published_caveat_reaches_the_reader.py` and its neighbour
`test_growth_learned_rate_caveat_reaches_the_reader.py`: for a day a corrected sentence sat in
the code, in the feed and in the working tree while nothing put it on screen, and nothing was
red, because every assertion took an in-process object as its subject. So this drives the REAL
door through `site/_live_harness.mjs` and asserts on what the page actually rendered -- and it
drives the REAL producer (`tools.generate_book_growth_data.build`) to make the feed, so a
mutation on EITHER surface reds here rather than only on the one this file happened to pick.

R15 -- the mutations, each naming the defect it catches:

  * delete the assignment in the door's script -> `test_the_basis_reaches_the_rendered_page`
    red. This is the fail-silent shape: the feed keeps carrying the sentence and no reader
    ever meets it.
  * delete the `<p id="growth-basis">` ELEMENT -> `test_the_paragraph_EXISTS_in_the_doors_own
    _source` red, and NOTHING ELSE IN THIS FILE. That second clause is not a limitation, it is
    a finding about the harness, and it was measured rather than assumed: `_live_harness.mjs`
    line 104 is `getElementById(id) { return (elements[id] ||= stub(id)); }` -- it AUTO-CREATES
    any element the page asks for. So a door that has lost its paragraph renders perfectly
    under the harness and blank in a browser, where `getElementById` returns null and the
    assignment throws inside a `.then()` that nothing catches, taking the rest of that IIFE's
    render down with it. Every `_reaches_the_reader` control in this directory shares the blind
    spot; filed as
    `WORKER_FINDING_THE_RENDER_HARNESS_AUTOCREATES_THE_ELEMENT_A_DELETED_PARAGRAPH_WOULD_LOSE`.
    The assertion below is on the door's SOURCE precisely because the rendered DOM cannot see
    it -- two subjects, because one of them is compromised.
  * say only "our machine" and drop "compute" / "not a commercial one" ->
    `test_the_rendered_basis_names_the_limit_as_COMPUTE_and_not_commerce` red. A sentence that
    hedges the kind of limit leaves both readings open, which is the original defect.
  * fill in a ceiling the probe has not established ("1,200 is right") ->
    `test_the_page_refuses_to_publish_a_ceiling_it_has_not_measured` red. The basis is the
    deliverable and the number is not: a slope needs two clean points and there is one
    (`docs/design/SETTLEMENT_CEILING_REMEASURED_2026-08-29.md` §6). "We cannot yet say" is a
    result and it belongs on the surface.
  * derive the interval from `PUBLISH_CADENCE_SECONDS` and say the page checks it against the
    measured cadence -> `test_the_rendered_basis_does_not_rest_on_the_measured_cadence` red.
    That quantity is the rate runs actually arrive and run duration is what sets arrival, so it
    moves with the answer and in the flattering direction.
  * say it unconditionally, on every run -> `test_a_run_our_engine_did_NOT_bound_makes_NO_compute
    _claim` red. THE NULL CONTROL AND THE LOAD-BEARING ONE: a page that always says "bounded by
    compute" is telling the reader nothing, and it would go on saying it on the day the ceiling
    is lifted far enough to settle every win -- which is the outcome this work is aimed at.
  * claim either way when the record cannot support either ->
    `test_a_record_that_cannot_say_refuses_to_say` red.

WHY NOT PIN THE LIVE FEED'S NUMBERS. The refusal count moves every publish cycle and the ceiling
is under active measurement. A control pinned to 415-of-505 goes red when the ceiling becomes
MORE honest and stays green when the claim rots -- backwards, and this project has paid for it
repeatedly. Every assertion here is keyed to the PROPERTY (does the page name the kind of limit,
and only when there is one), never to today's answer.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
PROJECT = SITE.parent
HARNESS = SITE / "_live_harness.mjs"
DOOR = SITE / "capabilities" / "index.html"
FEED = SITE / "data" / "book_growth.json"
CAPS = SITE / "data" / "capabilities_door.json"
ARMS = SITE / "data" / "value_arms.json"

sys.path.insert(0, str(PROJECT))


def _build(**kw) -> dict:
    """The REAL producer's output for a campaign we control.

    Imported inside the helper so a collection-time ImportError in the tools package reports as
    this file's failure rather than taking the whole selection down with it.
    """
    import tools.generate_book_growth_data as gb

    sample_rate = kw.pop("sample_rate", 0.2)
    refused = kw.pop("refused", 8)
    campaign = {
        "by_year": [
            {"year": 2016 + i, "quotes_issued": 50, "wins": 2, "funnel_wins": 2 + refused,
             "wins_refused_by_settlement_budget": refused, "accounts_after": 20 + i,
             "book_after": 20 + i, "spend_gbp": 100.0, "binding": "growth_rate",
             "homes_in_market": 400, "switching_multiplier": 1.0, "believed_win_rate": 0.2,
             "realised_win_rate_used": None, "planning_on": "belief"}
            for i in range(3)
        ],
        "notes": [], "quotes": 150, "wins": 6, "spend_gbp": 300.0,
        "customer_years_committed": 1195.4, "customer_year_budget": 1200.0,
    }
    if sample_rate is not None:
        campaign["settlement_sample_rate"] = sample_rate
    campaign.update(kw)
    return gb.build(campaign)


def _render(growth: dict) -> dict:
    """Drive the real door with the given growth feed and return its rendered elements.

    FAIL-CLOSED: an unresolved feed, a script error or a missing element all raise here rather
    than degrading to an empty string that a `not in` assertion would happily pass on. An
    unavailable check is a FAILED check.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and "
                    "an unavailable check is a FAILED check (R15)")
    payload = {
        "../data/book_growth.json": growth,
        "../data/capabilities_door.json": json.loads(CAPS.read_text(encoding="utf-8")),
        "../data/value_arms.json": json.loads(ARMS.read_text(encoding="utf-8")),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(DOOR)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, "the render harness failed: {}".format(proc.stderr[-2000:])
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), (
        "the door asked for a feed this test did not supply ({}), so whatever it rendered is "
        "not what a browser would".format(meta.get("unresolved"))
    )
    assert not meta.get("scriptError"), "the door's own script threw: {}".format(
        meta.get("scriptError"))
    return out


def _basis(feed: dict) -> str:
    el = _render(feed).get("growth-basis")
    assert el is not None, (
        "the door has no `growth-basis` element at all, so the kind of limit binding this book "
        "is nowhere on the page a reader reads"
    )
    return (el.get("textContent") or "").strip()


# ── the sentence reaches the reader ──────────────────────────────────────────────────────────

def test_the_basis_reaches_the_rendered_page():
    feed = _build()
    rendered = _basis(feed)

    assert rendered, (
        "the door rendered NOTHING where the compute-budget basis goes. The feed can carry the "
        "sentence and the reader still never meet it -- that is the whole class this file guards"
    )
    assert rendered == (feed.get("engine_bound_basis") or "").strip(), (
        "the page is serving a different sentence from the one the generator authored"
    )


def test_the_paragraph_EXISTS_in_the_doors_own_source():
    """The half of the render the harness structurally cannot check.

    `_live_harness.mjs` auto-creates any element the page asks for
    (`getElementById(id) { return (elements[id] ||= stub(id)); }`), so a door that has lost its
    `<p id="growth-basis">` renders the sentence under the harness and renders NOTHING in a
    browser -- where `getElementById` returns null, the assignment throws inside an uncaught
    `.then()`, and the rest of that IIFE (the growth table included) dies with it.

    So the subject here is the door's SOURCE, not its rendered DOM. Both are asserted because
    each is blind to the other's failure: the source cannot tell you the sentence is right, and
    the DOM cannot tell you the element is there.
    """
    src = DOOR.read_text(encoding="utf-8")

    assert 'id="growth-basis"' in src, (
        "the door has no `<p id=\"growth-basis\">` element. The render harness will not tell "
        "you: it auto-creates the element, so every DOM assertion in this file passes while a "
        "browser shows nothing and throws before it draws the growth table"
    )
    assert 'engine_bound_basis' in src, (
        "the door never reads `engine_bound_basis` from the feed, so the element is empty "
        "furniture"
    )


def test_the_live_feed_carries_it_too():
    """The fixture proves the wiring; this proves the SHIPPED artefact went through it.

    A control that only ever drives its own fixture certifies the code path and not the page a
    reader actually loads. Reported as a failure, never skipped: a growth feed that has gone
    unavailable is a finding about the publisher, not a reason to stop checking.
    """
    if not FEED.is_file():
        pytest.fail("site/data/book_growth.json is missing -- the published page has no feed")
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    if not feed.get("available"):
        pytest.fail("the published growth feed is unavailable, so the door renders no curve and "
                    "this control cannot run -- reported as a failure, never skipped")

    assert (feed.get("engine_bound_basis") or "").strip(), (
        "the SHIPPED feed carries no `engine_bound_basis`. Regenerate it: the sentence is in the "
        "producer and has not reached the artefact the site serves"
    )
    assert _basis(feed), "the shipped feed's basis sentence rendered as nothing"


# ── it says WHICH KIND of limit, which is the whole point ────────────────────────────────────

def test_the_rendered_basis_names_the_limit_as_COMPUTE_and_not_commerce():
    """Both halves are asserted because either alone leaves the misreading open.

    Naming it a compute budget without denying the commercial reading still lets a reader take
    "compute budget" as a euphemism for the supplier's cost base -- which is a commercial
    constraint and the exact confusion. Denying commerce without naming compute tells them what
    it is not and leaves them nowhere.
    """
    rendered = _basis(_build()).lower()

    assert "compute" in rendered, (
        "the basis never says the limit is a COMPUTE budget, so a reader is left with 'our "
        "machine' -- uncheckable, and readable as a supplier that ran out of money"
    )
    assert "not a commercial one" in rendered or "not commercial" in rendered, (
        "the basis does not rule OUT the commercial reading. A flattened growth curve reads as "
        "a supplier's limit by default; the page has to say it is not"
    )
    assert "supplier in the modelled world" in rendered, (
        "the basis does not say that no supplier in the modelled world faces this limit, which "
        "is the sentence that puts it on our side of the wall rather than the company's"
    )


def test_the_rendered_basis_says_what_the_budget_is_a_budget_OF():
    """The director's ask, 2026-08-29: *"state what SETTLEMENT_CUSTOMER_YEAR_BUDGET is a budget
    OF, in one sentence a reader can check."* Checkable means it names the constant, the unit it
    is denominated in, and the two things it is traded against."""
    rendered = _basis(_build())

    assert "SETTLEMENT_CUSTOMER_YEAR_BUDGET" in rendered, (
        "the basis does not name the constant, so a reader cannot go and check it"
    )
    assert "customer-years" in rendered, "the basis does not say what unit the budget is in"
    assert "memory" in rendered.lower(), (
        "the basis omits the memory leg -- and memory is the ONLY bound here that is external "
        "evidence, because a slower run does not make the box bigger"
    )
    assert "publish" in rendered.lower() or "cycle" in rendered.lower(), (
        "the basis omits the time leg, which is the one that actually binds today"
    )


def test_the_rendered_basis_does_not_rest_on_the_measured_cadence():
    """The circularity, kept out of the published sentence.

    `suite_duration_watch.PUBLISH_CADENCE_SECONDS` is by its own comment *"a measurement of how
    often runs actually arrive"*. Run duration sets marker inter-arrival, so a ceiling argued
    against it raises the bound it is checked against, in the flattering direction. The page has
    to present the interval as CHOSEN. This asserts the property (chosen, ours) rather than
    banning a word, so it survives the sentence being rewritten.
    """
    rendered = _basis(_build()).lower()

    assert "choose" in rendered or "chosen" in rendered or "we allow" in rendered, (
        "the basis does not present the publish interval as something we CHOOSE. Presented as "
        "something measured, it is circular: the measurement is the arrival rate this very "
        "budget sets"
    )
    assert "how often runs arrive" not in rendered and "arrival rate" not in rendered, (
        "the published basis rests on the measured arrival rate -- the circular quantity"
    )


def test_the_page_refuses_to_publish_a_ceiling_it_has_not_measured():
    """FAIL CLOSED, ON THE SURFACE. The deliverable is the basis; the number needs a cost curve,
    a cost curve needs two clean points, and there is one. A page that answered "1,200 is right"
    off a basis that does not yet reach a number would be publishing an invented constant with a
    freshly-written justification attached -- worse than publishing nothing, because the
    justification is what makes it durable."""
    rendered = _basis(_build())

    assert "NOT YET KNOWN" in rendered, (
        "the basis does not tell the reader that the ceiling this basis supports is still "
        "unmeasured. 'We cannot tell' is a result and it belongs on the page, not in a footnote"
    )


# ── the null controls: it must NOT say this when it is not true ──────────────────────────────

def test_a_run_our_engine_did_NOT_bound_makes_NO_compute_claim():
    """THE LOAD-BEARING NULL CONTROL.

    Every assertion above would pass on a producer that emitted the compute-budget sentence
    unconditionally -- and such a producer would go on emitting it on the day the ceiling is
    lifted far enough to settle every win, which is the outcome this whole line of work is
    aimed at. A control that cannot go quiet is a control that carries no information.
    """
    rendered = _basis(_build(sample_rate=1.0, refused=0))

    assert rendered, "a fully-settled run should still say something, not render blank"
    # THE ASSERTION IS ON THE CLAIM, NOT ON THE WORDS. A bare `"compute budget" not in ...`
    # fails on the correct null sentence, which says "NO compute budget bound this book" -- the
    # substring appears inside its own negation. Matching the affirmative clause is what
    # distinguishes the two, and getting this wrong the first time is why it is written down.
    assert "limit is a compute budget" not in rendered.lower(), (
        "our engine settled every account the company won, and the page still told the reader "
        "its book was bounded by a compute budget"
    )
    assert "no compute budget bound" in rendered.lower(), (
        "a fully-settled run should say plainly that nothing here is our machine's limit, not "
        "just omit the claim -- an absent sentence reads as a page that forgot to check"
    )
    assert "commercial" in rendered.lower(), (
        "with nothing refused, the height of the curve IS commercial and the page should say so"
    )
    assert "NOT YET KNOWN" not in rendered, (
        "there is no unmeasured ceiling to warn about on a run nothing was refused from"
    )


def test_the_published_no_freshness_requirement_claim_is_STILL_TRUE():
    """The page's load-bearing premise, checked against the constants it rests on.

    The basis sentence tells a reader *"the reported window reached Elexon Final Reconciliation
    on 2026-08-07 and none of its figures can change again, so there is no data-freshness
    requirement to set [a publish interval] from."* That is what breaks the circularity: a
    requirement of ZERO cannot move when this ceiling moves, which is exactly what
    `PUBLISH_CADENCE_SECONDS` could not promise.

    IT IS TRUE ONLY WHILE `REPORT_END` STAYS PUT, and the research that established it says so
    in terms: *"the same question asked in July would have had the opposite answer, and asking
    it again is only safe while REPORT_END stays put"*
    (`docs/market_research/elexon_settlement_run_timetable_verified.md`). Extend the reported
    window past `today - RF_MONTHS` and new Elexon reconciliation CAN revise figures inside it,
    the external requirement stops being zero, and the sentence on the page becomes false --
    with nothing else in the tree noticing, because the sentence is prose and the window is a
    string constant twelve modules away.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. It does not pin `REPORT_END == "2025-06-07"`
    (which would red on any legitimate window change and tell the reader nothing about the
    claim) and it does not pin the date in the sentence. It asks the one question the claim
    depends on: has the reported window finished reconciling? A window extension is not a defect
    -- it is a signal that the published basis needs re-deriving, and this is what says so.
    """
    import datetime as dt

    from simulation.run_phase2b import REPORT_END
    from simulation.settlement_timetable import RF_MONTHS

    window_end = dt.date.fromisoformat(REPORT_END)
    # Whole months, added the boring way rather than via a dateutil dependency.
    y, m = divmod((window_end.year * 12 + window_end.month - 1) + RF_MONTHS, 12)
    rf_complete = window_end.replace(year=y, month=m + 1)
    today = dt.date.today()

    assert rf_complete <= today, (
        "THE PUBLISHED BASIS IS NO LONGER TRUE. The book-growth page tells a reader there is no "
        "data-freshness requirement on our publish interval because the reported window has "
        "finished reconciling. It has not: REPORT_END is {} and Final Reconciliation for it "
        "lands {} (+{} months), which is {} days away. Until then new Elexon data CAN revise "
        "figures inside the reported window, so the external requirement is not zero and the "
        "publish interval is no longer a free choice. Re-derive the basis in "
        "`tools/generate_book_growth_data.py::engine_bound_basis` and in "
        "`simulation/net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET`'s note before "
        "shipping this window.".format(
            REPORT_END, rf_complete, RF_MONTHS, (rf_complete - today).days)
    )


def test_a_record_that_cannot_say_refuses_to_say():
    """A campaign record with no sample rate cannot support EITHER claim, and the page must say
    that rather than defaulting to one. Missing-key-reads-as-false is how a control ends up
    certifying exactly the runs it could not see."""
    rendered = _basis(_build(sample_rate=None))

    assert "CANNOT BE READ" in rendered, (
        "the record does not say what share of wins reached the book, and the page picked an "
        "answer anyway"
    )
    assert "compute budget, not a commercial one" not in rendered.lower(), (
        "the page asserted a compute bound from a record that cannot establish one"
    )
