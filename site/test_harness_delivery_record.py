"""R11 for the delivery record: the four questions must ARRIVE ON THE PAGE, not in a JSON file.

Director, 2026-08-25: *"I can't see any of this without someone reading git logs to me. I want to
open one page and know what the machine did, what it decided, what it got wrong, and what it's
doing next. Harness was meant to be that and isn't."*

WHY IT DRIVES THE REAL DOOR. R11 means the assertion is on the value a browser RENDERS, never on a
string in the repo. The failure this shape catches is the one that actually ships: the page
deploys fine, its feed 404s or drifts schema, and every panel sits on a placeholder forever. The
class control for that is `site/test_door_render_functions_are_wired.py`, filed the day a live
door served "Loading…" under a heading for eight days.

TWO STATES, BOTH TESTED, and the second is the one that matters more today. The seat has not run
on a fresh clone, so the panels must render an HONEST ABSENCE rather than nothing at all -- a
machine that reports no decisions and a machine that has not been asked to decide look identical
from outside unless the page says which it is.
"""
from __future__ import annotations

import html as _html
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR = SITE / "harness" / "index.html"
DATA = SITE / "data"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

#: Every feed the door boots from, as written in the page. FAIL-CLOSED: the harness rejects a url
#: the fixture did not supply, so a door that grows a fifth feed reds here instead of silently
#: testing its absence path.
FEED_FILES = {
    "../data/proof.json": "proof.json",
    "../data/delivery.json": "delivery.json",
    "../data/director_delta.json": "director_delta.json",
    "../data/director_reserved.json": "director_reserved.json",
}

PANELS = ("delivery-kpis", "delivery-did", "delivery-decided", "delivery-wrong",
          "delivery-next", "delivery-ceiling", "delivery-carbon-ceiling",
          "delivery-product-ceiling", "director-delta")


def _text(html: str) -> str:
    """Recover what a READER sees from a fragment of rendered HTML.

    UNESCAPE, OR THE CHECKER READS A DIFFERENT STRING THAN THE READER (2026-08-26). This stripped
    tags and collapsed whitespace but left HTML entities intact, so it compared an ESCAPED
    rendering against the UNESCAPED source JSON. `index.html` renders every mistake through
    `esc()` -- correctly, it assigns to `.innerHTML` -- so the moment an entry's opening 60
    characters contained a `"`, `&`, `<` or `>`, the panel carried the text, the browser showed
    the text, and this helper could not find it.

    It cost eight publish cycles: the first recorded mistake begins `Commit `03b60e1e9` announced
    in its own subject that "the fi...`, the page rendered `&quot;the fi`, and the site lane
    refused every publish commit from 04:40 UTC on. That is the same class as the docstring
    below it -- a control firing on the SUCCESS path -- one layer further down.

    ORDER MATTERS: strip tags FIRST, then unescape. Unescaping first would turn a literal
    `&lt;b&gt;` in the copy into `<b>` and let the tag-stripper eat a reader-visible string.
    """
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", html or ""))).strip()


def _render(overrides: dict | None = None) -> dict:
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing — the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    feeds = {}
    for url, name in FEED_FILES.items():
        path = DATA / name
        if not path.is_file():
            pytest.fail(f"{path} does not exist, so the page a reader gets cannot be rendered")
        feeds[url] = json.loads(path.read_text(encoding="utf-8"))
    feeds.update(overrides or {})
    proc = subprocess.run(["node", str(HARNESS), str(DOOR)],
                          input=json.dumps(feeds), capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, f"the render harness failed: {proc.stderr[-2000:]}"
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), (
        f"the door asked for a feed this test did not supply: {meta.get('unresolved')}")
    assert not meta.get("scriptError"), f"the door's own script threw: {meta.get('scriptError')}"
    return out


@pytest.fixture(scope="module")
def rendered():
    return _render()


@pytest.mark.parametrize("panel", PANELS)
def test_every_delivery_panel_actually_RENDERS(rendered, panel):
    """MUTATION (must fire): define a render function and never call it -- the exact defect that
    served a live door "Loading…" for eight days."""
    assert panel in rendered, f"#{panel} is not on the page at all"
    body = _text(rendered[panel]["innerHTML"])

    assert body, f"#{panel} rendered nothing, so a reader sees an empty heading"
    assert "Loading" not in body, f"#{panel} is still on its placeholder"


def test_the_page_answers_WHAT_IT_DID_with_work_separated_from_republishing(rendered):
    """The honest half of "what it did": an auto-process republish is not work, and a page that
    counts it as work makes a quiet day look busy."""
    kpis = _text(rendered["delivery-kpis"]["innerHTML"])

    assert "pieces of real work" in kpis
    assert "routine republishes, not counted as work" in kpis


def test_the_page_answers_WHAT_IT_DECIDED_and_shows_what_was_TURNED_DOWN(rendered):
    """The rejections are the reviewable half -- the director's own reason for asking for them:
    *"record the options you considered and why you chose as you did. That record is what I
    review, and it's what makes it safe for you not to ask."*

    MUTATION (must fire): render only the chosen focus.
    """
    decided = rendered["delivery-decided"]["innerHTML"]
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))["what_it_decided"]
    if not live.get("available"):
        # HONEST ABSENCE, not a skip. This is the state of a fresh clone and of any stretch the
        # seat has not yet oriented, so it is the state most readers will actually meet.
        assert "no valid direction record" in _text(decided)
        assert "not that it has stopped" in _text(decided), (
            "an absent direction must say the machine is still working, or a reader reads it as "
            "a stall"
        )
        return
    assert "Turned down, and why" in decided
    assert "Chose" in decided


def test_an_empty_WHAT_IT_GOT_WRONG_says_WHICH_kind_of_empty_it_is(rendered):
    """A machine reporting no mistakes is either not looking or not saying, and both read
    identically from outside.

    MUTATION (must fire): render an empty panel, or the word "None".

    THE EMPTY STATE IS READ FROM THE DATA, NOT GREPPED OUT OF THE HTML (2026-08-26). This
    condition was `if "recorded" in body:` -- a WORD standing in as a proxy for a STATE, on the
    reasoning that the empty-state sentence happens to contain it. On 2026-08-26 the seat had
    recorded 27 mistakes, one of which used the word "recorded" in its own prose, so a fully
    populated panel took the empty-state branch and demanded a sentence that has no business
    being there. It refused the publish commit, at 06:52, on the FIRST cycle after the map-split
    landing had cleared the real cause -- a control firing on the success path, which is the
    class this whole morning was about.

    A substring is not a state. `delivery.json` says which state it is in, so ask it.
    """
    body = _text(rendered["delivery-wrong"]["innerHTML"])
    assert body and body != "None"

    entries = (json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
               .get("what_it_got_wrong") or {}).get("entries") or []
    if entries:
        # POPULATED: the panel must actually carry the mistakes, not a summary of them. Read the
        # first entry's own words back out of the rendering, so a panel that renders the count
        # and drops the text fails here rather than passing on a plausible-looking number.
        first = _text(entries[0].get("what", ""))[:60]
        assert first and first in body, (
            "the panel has {} recorded mistake(s) and does not carry the first one's text -- a "
            "reader is being told the number and not the finding".format(len(entries))
        )
        # AND WHETHER IT WAS FIXED. Until 2026-09-03 the seat declared `corrected: true|false` on
        # every error, the field was dropped one hop out of `DIRECTION.yaml`, and this panel
        # served 212 mistakes with no correction state on any of them -- which reads from outside
        # as a machine that lists its faults and never repairs one. The three states are kept
        # apart on the surface because "we did not record whether this was fixed" is a different
        # claim from "this was not fixed", and only one of them is true of the older rows.
        for entry in entries:
            expected = {True: "corrected", False: "still open"}.get(
                entry.get("corrected"), "correction not recorded")
            assert expected in body, (
                "an entry recorded as {!r} does not say so on the rendered page".format(
                    entry.get("corrected"))
            )
            break
        return
    assert "not that nothing went wrong" in body or "no orientation has recorded" in body, (
        "the panel is EMPTY and does not say which kind of empty: a machine that found no "
        "mistakes and one that never looked read identically from outside"
    )


def test_WHAT_IT_IS_DOING_NEXT_states_that_direction_can_never_BLOCK_work(rendered):
    """The property a reader needs in order to trust the mechanism at all: a wrong instruction
    slows this machine down and can never wedge it."""
    body = _text(rendered["delivery-next"]["innerHTML"])

    assert "can never zero one" in body or "never obeyed by force" in body


def test_the_director_delta_does_not_claim_he_has_LOOKED(rendered):
    """SITE9's ruling was overturned on 2026-08-25 -- *"Rebuild the delta as a section on
    /harness/"* -- and the honesty that makes the panel publishable travels with it. The stamp
    currently reads `bootstrap-at-build-time (not a director read receipt)`: nobody has marked a
    read. A panel headed "since you last looked" over that stamp would be asserting he has.

    MUTATION (must fire): render `last_look_at` as a read receipt without checking
    `last_look_recorded_by`.
    """
    feed = json.loads((DATA / "director_delta.json").read_text(encoding="utf-8"))
    body = _text(rendered["director-delta"]["innerHTML"])

    if str(feed.get("last_look_recorded_by", "")).startswith("bootstrap"):
        assert "not a record of anyone reading anything" in body
    assert "Measured against a position recorded on" in body


def test_a_MISSING_delivery_feed_renders_a_stated_absence_and_not_a_blank_page():
    """FAIL-CLOSED at the reader, which is the only place it counts. The door's own `.catch()`
    branch must produce words; a blank panel under a live heading is the failure this whole file
    exists for.

    MUTATION (must fire): drop the `.catch()` from the delivery fetch.
    """
    out = _render({"../data/delivery.json": None})
    body = _text(out["delivery-did"]["innerHTML"])

    assert body, "a broken feed leaves the panel silently empty"


def test_the_text_extractor_reads_the_same_string_the_reader_does():
    """R15 for `_text` itself: the helper every assertion in this file routes through must
    recover the READER's string, not the markup's.

    This is the control for the 2026-08-26 wedge. `index.html` escapes every mistake through
    `esc()` before assigning to `.innerHTML`, which is correct -- a browser parsing `&quot;`
    shows `"`. A checker that skips the unescape compares against a string no reader ever sees
    and reds on a perfectly good page. Eight publish cycles were refused that way.

    MUTATION (must fire): drop the `_html.unescape(...)` call from `_text` and the entity case
    below reds. Restore it and it passes.
    """
    # The exact shape the door emits: escaped entity inside a stripped tag.
    assert _text('<p>said &quot;the fi</p>') == 'said "the fi'
    assert _text("<p>a &amp; b</p>") == "a & b"

    # ORDER: an escaped tag is reader-visible copy and must SURVIVE, not be eaten by the
    # tag-stripper. This fires if unescape is moved before the tag strip.
    assert _text("<p>use &lt;b&gt; for bold</p>") == "use <b> for bold"

    # Real tags are still removed, and whitespace still collapses.
    assert _text('<div class="card">  one   <span>two</span>  </div>') == "one two"


# ── the margins behind "worse than guessing" ─────────────────────────────────────────────────
#
# The count under "Where belief and truth diverge" is a count of THRESHOLD CROSSINGS: `value > 1`,
# a bare point estimate against exactly 1.0 with no interval. The page calls it "the one that
# matters most" and says the build queue is ordered by it. Measured 2026-08-30, the three live
# members are 1.034, 1.039 and 2.529 — so two of the three are decided three to four percent the
# wrong side of the line, one of them on twenty cells. A reader who meets "3" and nothing else has
# been told the confident half.
#
# The pair below is a PAIR on purpose: one asserts the margins reach the reader when the feed has
# them, the other that an artefact without them renders nothing rather than an empty list, because
# an empty list reads as "none of these are close to the line" — the opposite of what an absent
# field means.


def test_the_margins_behind_WORSE_THAN_GUESSING_reach_the_reader(rendered):
    """Each crossing's distance from the line, and its sample size or the absence of one.

    Fires on: dropping the `marginsNote` call, or rendering the count without the margins.
    """
    proof = json.loads((DATA / "proof.json").read_text(encoding="utf-8"))
    gaps = _find_gap_block(proof)
    margins = (gaps or {}).get("worse_than_blind_margins")
    if not margins:
        pytest.skip("this artefact carries no margins; the absence branch is the other half")

    body = _text(rendered["gap-note"]["innerHTML"])
    for m in margins:
        assert str(m["percent_past_the_line"]) in body, (
            f"{m['world_atom']} is counted as worse than guessing and the page does not say it is "
            f"only {m['percent_past_the_line']}% past the line")
        if m["sample_size"] is None:
            assert "how many cases it rests on" in body, (
                "a crossing with no sample size anywhere in the record renders as though it were "
                "bounded")
        else:
            # THE PHRASE, NOT THE BARE NUMBER. Asserting `str(n) in body` passes on any body
            # containing that digit anywhere -- "20" is inside "152.9%" -- so it survived the
            # mutation that reports an unknown sample as 0 and renders "on 0 cases".
            assert f"on {m['sample_size']} cases" in body

    # AND AN UNKNOWN SAMPLE IS NONE, NEVER ZERO. "We do not know how many cases this rests on" and
    # "it rests on no cases" are different sentences, and a producer returning 0 for the first
    # would put the second on the page -- the fail-open direction, because a reader who meets
    # "0 cases" concludes the crossing is meaningless rather than unbounded.
    for m in margins:
        assert m["sample_size"] is None or m["sample_size"] > 0, (
            f"{m['world_atom']} reports a sample size of {m['sample_size']!r}; an unknown "
            "population must be None so the page can say it is unknown")


def test_an_artefact_with_NO_margins_says_nothing_rather_than_an_empty_list():
    """THE OTHER HALF. Every artefact produced before 2026-08-30 carries no margins at all. An
    empty list rendered as a list reads as "none of them are close to the line", which is a claim,
    and the absence of the field is not that claim.

    Fires on: rendering the margins block unconditionally.
    """
    proof = json.loads((DATA / "proof.json").read_text(encoding="utf-8"))
    stripped = json.loads(json.dumps(proof))
    gaps = _find_gap_block(stripped)
    if gaps is None:
        pytest.skip("this artefact carries no gap block to strip")
    gaps.pop("worse_than_blind_margins", None)

    body = _text(_render({"../data/proof.json": stripped})["gap-note"]["innerHTML"])

    assert "past the line" not in body, (
        "the page discusses margins for an artefact that carries none")
    # And the block it belongs to still renders, so this is an absence and not a blank panel.
    assert "worse than guessing" in body


def _find_gap_block(obj):
    """The gap block, wherever `generate_proof_data` nests it — found by its own key rather than
    by a path, so a re-nesting moves it without silently emptying this control."""
    if isinstance(obj, dict):
        if "worse_than_blind_count" in obj:
            return obj
        for value in obj.values():
            found = _find_gap_block(value)
            if found is not None:
                return found
    if isinstance(obj, list):
        for value in obj:
            found = _find_gap_block(value)
            if found is not None:
                return found
    return None


def test_the_gating_FIGURE_arrives_with_the_correction_that_moved_it(rendered):
    """R1's ceiling gates a whole programme (`A49`), and for two days it was published as a bound
    while being the winner of a 45-way search graded against the null of ONE comparison.

    MUTATION (must fire): render only the corrected number. A reader who is shown the right figure
    and not the wrong one cannot tell that the wrong one was ever published, and the panel's whole
    reason for existing is that it was.
    """
    body = _text(rendered["delivery-ceiling"]["innerHTML"])
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
    c = live.get("the_number_the_programme_rests_on") or {}
    if not c.get("available"):
        assert "not the same as the bound being zero" in body, (
            "an absent ceiling must say so in a way that cannot be read as a measured zero")
        return

    assert "As published (wrong)" in rendered["delivery-ceiling"]["innerHTML"]
    assert "Corrected" in rendered["delivery-ceiling"]["innerHTML"]
    for figure in (c["reported_ceiling"], c["bound_p95"], c["p_value"]):
        assert f"{float(figure):.4f}" in body, (
            f"{figure} is in the feed and not on the page a reader gets")
    assert str(c["candidates_searched"]) in body, (
        "the number of candidates searched is what makes the correction legible, and it is absent")


def test_the_ceiling_panel_states_WHAT_THE_VERDICT_DOES_NOT_SAY(rendered):
    """Fail closed, on the surface. A refusal read as "there is nothing there", and a marginal pass
    read as "the bound is established", are the same failure from opposite sides.

    MUTATION (must fire): drop `what_it_does_not_say` from the render.
    """
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
    c = live.get("the_number_the_programme_rests_on") or {}
    if not c.get("available"):
        pytest.skip("no ceiling measurement in this tree; the absence path is covered above")
    body = _text(rendered["delivery-ceiling"]["innerHTML"])

    assert "What this does not say" in body
    # The caveat BRANCHES with the verdict -- one sentence cannot carry both readings.
    assert (("does not establish a bound" in body) if c["corrected_verdict"]
            else ("refusal to distinguish" in body)), (
        "the caveat on the page does not match the verdict beside it")


def test_an_absent_ceiling_measurement_does_not_render_as_a_measured_zero():
    """The state a fresh clone and every linked worktree is actually in: the instrument's artefact
    is absent, and "no bound was measured" must not read as "the bound is zero".

    MUTATION (must fire): render `0.0000` (or an empty panel) when the feed says unavailable.
    """
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
    live["the_number_the_programme_rests_on"] = {
        "available": False,
        "why": "the inference-ceiling instrument has not been run in this tree, so no bound is "
               "shown. That is not the same as the bound being zero.",
    }
    body = _text(_render({"../data/delivery.json": live})["delivery-ceiling"]["innerHTML"])

    assert "not the same as the bound being zero" in body
    assert "0.0000" not in body


def test_the_tell_INSIDE_the_published_figure_reaches_the_reader():
    """The winner scores better out of sample than in it, and for two days nothing said so.

    The instrument's docstring names this as "a fit scoring three times better on households it
    never saw, which no real fit does" -- and the control named for it, keyed to MOST pairs, read
    green while the WINNER on the page showed it at 3.66x. A reader given "clears, marginally" and
    not this cannot judge the number.

    MUTATION (must fire): render the panel without the tell. Both sides of the partition are
    asserted, because a sentence the panel always emits is boilerplate, not evidence.
    """
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
    c = dict(live.get("the_number_the_programme_rests_on") or {})
    if not c.get("available"):
        pytest.skip("no ceiling measurement in this tree; the absence path is covered above")

    c["winner_outscores_its_own_fit"] = True
    c["winner_held_out_over_in_sample"] = 3.66
    live["the_number_the_programme_rests_on"] = c
    shown = _text(_render({"../data/delivery.json": live})["delivery-ceiling"]["innerHTML"])
    assert "3.66" in shown, "how far the inversion goes is what makes it judgeable"
    # THE DISCRIMINATOR HAS TO BE UNIQUE TO THE BLOCK, and the obvious phrase is not: the
    # instrument's own `what_it_does_not_say` already contains "never saw", and the panel renders
    # that string on every branch. Keying the partition to it would have passed both legs and
    # proved nothing about the block being tested. "does not overturn" is emitted here and nowhere
    # else on the page.
    assert "does not overturn" in shown, (
        "the tell is in the feed and not on the page a reader gets")

    c["winner_outscores_its_own_fit"] = False
    hidden = _text(_render({"../data/delivery.json": live})["delivery-ceiling"]["innerHTML"])
    assert "does not overturn" not in hidden, (
        "the panel emits the tell regardless of the property, so its presence says nothing")


def test_whether_the_gating_figure_SURVIVES_A_REDRAW_reaches_the_reader():
    """A49 gates R3 and R4 on this figure, and the figure changes side across draws of the same
    book. Until this landed the page carried the PREDICTION that it "will move with the next draw"
    while the record already held the observation that it had -- a hedge standing in for evidence
    we own.

    ALL THREE STATES ARE ASSERTED, not just the interesting one. A panel that emits the instability
    sentence unconditionally is boilerplate; a panel that renders "unmeasured" as agreement is the
    fail-open this whole repair exists to prevent. The unmeasured leg is the one that would rot
    silently -- every linked worktree is in it.

    MUTATION (must fire): render the panel without the redraw block, or render `measured: false`
    as though the verdict were stable.
    """
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
    c = dict(live.get("the_number_the_programme_rests_on") or {})
    if not c.get("available"):
        pytest.skip("no ceiling measurement in this tree; the absence path is covered above")

    def shown(panel):
        c["does_the_verdict_survive_a_redraw"] = panel
        live["the_number_the_programme_rests_on"] = c
        return _text(_render({"../data/delivery.json": live})["delivery-ceiling"]["innerHTML"])

    # LEG 1 -- it moved. The reader must be told the verdict is not a property of the world.
    moved = shown({
        "measured": True, "runs_measured": 32, "verdict_is_the_same_on_every_run": False,
        "clears_count": 19, "cannot_tell_count": 13,
        "verdict_is_a_step_function_of_coverage": True,
        "coverage_regimes": [{"households_in_rung": 71, "verdict": "cannot tell"},
                             {"households_in_rung": 69, "verdict": "clears"}],
    })
    assert "cannot gate a programme" in moved, (
        "the verdict changes side across draws and the page does not say so")
    assert "not a property of the world" in moved
    # The STEP is the stronger claim and must be distinguishable from "19 of 32 cleared", which
    # reads as noise that more draws would settle. It would not: there is no scatter inside a group.
    assert "step, not scatter" in moved

    # LEG 2 -- it held. The same panel must NOT emit the instability language, or leg 1 proves
    # nothing about the property and only that the block renders.
    held = shown({
        "measured": True, "runs_measured": 32, "verdict_is_the_same_on_every_run": True,
        "clears_count": 32, "cannot_tell_count": 0,
    })
    assert "cannot gate a programme" not in held, (
        "the panel emits the instability regardless of the measurement, so it says nothing")
    assert "consistency check and not a bound" in held, (
        "a stable verdict across draws of ONE book must not be published as if it widened the claim")

    # LEG 3 -- it was never measured. This must read as UNKNOWN and never as agreement, and it is
    # the state every linked worktree and fresh clone is actually in.
    unmeasured = shown({"measured": False, "why": "the stability rung has not been run in this tree."})
    assert "unknown" in unmeasured.lower(), (
        "an unmeasured stability rung must say so; silence here reads as a stable verdict")
    assert "cannot gate a programme" not in unmeasured
    assert "consistency check and not a bound" not in unmeasured, (
        "an unrun rung rendered as a passed consistency check is the fail-open this control exists for")


def test_the_generator_LIFTS_the_only_rung_that_can_carry_a_magnitude():
    """The instrument's artefact held an unbiased magnitude and the panel A49 reads said `null`.

    THE DEFECT, and it is a LIFT defect rather than a render one, which is why this control calls
    the generator against the REAL artefact instead of a fixture. `whole_book_pair_rung` landed on
    2026-09-06 carrying the same pair search restricted to the observables the company holds for
    every account on supply -- so its population is the whole book rather than the winning pair's
    renewing subset, and it is the only rung on this book whose fit fold can hold populations.
    `tools/r1_inference_ceiling` computed it, printed it to stdout and wrote it to the artefact.
    `the_number_the_programme_rests_on` lifted the two rungs beside it and not this one, so the
    delivery feed published `magnitude: null` while the artefact on disk held +0.2513 at p=0.01.
    A fixture-fed render test cannot see that at all: it would supply the field the generator never
    produced and pass on both legs.

    KEYED TO THE PROPERTY AND NOT TO TODAY'S ANSWER. It asserts the panel carries WHAT THE ARTEFACT
    HOLDS, whichever way that falls -- including a refusal. Pinning +0.2513 would go red the day the
    book grows and green the day the lift silently returns a stale constant, which is backwards.

    MUTATION (must fire): drop `the_whole_book_rung` from the returned panel, or lift the headline
    rung's magnitude into it.
    """
    from tools.generate_delivery_page import PROJECT, the_number_the_programme_rests_on

    artefact = PROJECT / "docs" / "observability" / "r1_inference_ceiling.json"
    # TRACKED, so its absence is a defect and not a reason to skip. A skip here would be the
    # fail-silent this control exists to catch: the panel would publish `null` and nothing would say
    # whether that was the measurement or the lift.
    assert artefact.is_file(), (
        f"{artefact} is tracked and missing, so what the panel publishes cannot be checked against "
        "what the instrument measured")
    held = json.loads(artefact.read_text(encoding="utf-8"))
    rung = held.get("whole_book_pair_rung")
    if not rung:
        pytest.skip("this artefact predates the whole-book rung; there is nothing to lift")

    panel = the_number_the_programme_rests_on()
    assert panel.get("available"), "the artefact is present and the panel withheld it"
    lifted = panel.get("the_whole_book_rung")
    assert lifted, "the artefact carries the whole-book rung and the panel does not lift it"

    mag = rung.get("magnitude_three_way_split") or {}
    assert lifted["magnitude"] == mag.get("estimate"), (
        f"the artefact's whole-book magnitude is {mag.get('estimate')!r} and the panel publishes "
        f"{lifted['magnitude']!r}")
    assert lifted["magnitude_refused"] == mag.get("refused")
    assert lifted["households"] == (rung.get("best_pair") or {}).get("n")
    # THE RUNG'S OWN CEILING VERDICT HAS TO TRAVEL WITH ITS MAGNITUDE. On this book the two
    # disagree -- the selected maximum cannot be told from chance while the de-biased estimate
    # clears its floor -- and a magnitude published without it reads as a bound the rung has not
    # earned.
    assert lifted["corrected_verdict"] == rung.get("clears_the_selection_corrected_null")
    # AND IT MUST NOT BE THE HEADLINE RUNG WEARING A NEW NAME. Same population, same number, and
    # the panel would be publishing one measurement twice.
    assert lifted["households"] != panel.get("households_in_the_rung") or (
        lifted["magnitude"] == (held.get("magnitude_three_way_split") or {}).get("estimate")), (
        "the whole-book rung and the headline rung report the same population, so the restriction "
        "this panel claims to apply is not being applied")


def test_the_WHOLE_BOOK_magnitude_and_its_disagreeing_verdict_reach_the_reader():
    """Both legs, because a sentence the panel always emits is boilerplate rather than evidence.

    The headline rung refuses a magnitude for want of households per cell, and for a day the page
    carried that refusal alone -- so a reader was told R1 has no unbiased magnitude when the book
    had bought one on a rung the page did not render. The honest publication is BOTH: the narrower
    rung's estimate AND the fact that its own selected-maximum verdict disagrees with it, because
    showing the estimate alone converts "a magnitude over this population" into "a bound".

    MUTATION (must fire): render the estimate without the disagreement, or emit the block
    unconditionally so a refused rung reads like an answered one.
    """
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
    c = dict(live.get("the_number_the_programme_rests_on") or {})
    if not c.get("available"):
        pytest.skip("no ceiling measurement in this tree; the absence path is covered above")

    def shown(rung):
        # SCOPED TO THIS BLOCK, because the FIGURE is not unique to it (corrected 2026-09-07). Two
        # other things on the same panel carry +0.2513: the sibling `the_a49_gate` block, which
        # renders the magnitude of whichever rung it gates on -- and on this book that IS this rung
        # -- and `on_the_magnitude`, a SENTENCE lifted verbatim from the instrument's own artefact.
        # So LEG 2's `"0.2513" not in refused` was unsatisfiable the moment the feed carried a live
        # gate, whatever this block rendered. It read green only because the committed
        # `delivery.json` predated both fields; regenerating the feed is what surfaced it.
        #
        # The repair is in two parts and the second is the load-bearing one: blank the sibling so
        # the panel holds one rendering of this rung, and assert on the BLOCK'S OWN PHRASE rather
        # than on a number that prose can reintroduce. A control keyed to a figure it does not own
        # is keyed to today's artefact text.
        c["the_a49_gate"] = None
        c["the_whole_book_rung"] = rung
        live["the_number_the_programme_rests_on"] = c
        return _text(_render({"../data/delivery.json": live})["delivery-ceiling"]["innerHTML"])

    # LEG 1 -- the rung carries a magnitude, and its ceiling verdict does NOT clear. Both figures
    # and the disagreement have to be on the page.
    answered = shown({
        "fields": ["a", "b"], "pairs_scored": 15, "households": 164,
        "reported_ceiling": 0.1963, "corrected_verdict": False, "p_value": 0.4726,
        "magnitude": 0.2513, "magnitude_noise_floor": 0.1628, "magnitude_p_value": 0.01,
        "magnitude_refused": None, "households_per_cell_on_the_fit_fold": 13.75,
    })
    assert "0.2513" in answered, "the only unbiased magnitude this book buys is not on the page"
    assert "164" in answered, (
        "a magnitude without the population it is over is not a judgeable figure")
    assert "0.4726" in answered, (
        "the rung's own ceiling verdict disagrees with its magnitude and the page does not say so")
    # The discriminator is unique to this block: "readings disagree" appears nowhere else on the
    # page, whereas "cannot be told from chance" and "noise floor" are emitted by the headline and
    # by `what_it_does_not_say` on every branch.
    assert "readings disagree" in answered, (
        "the estimate is rendered as a bound: nothing on the page says the two readings of this "
        "rung point opposite ways")

    # LEG 2 -- the rung refuses too. The refusal must be the thing rendered, and no figure invented.
    refused = shown({
        "fields": ["a", "b"], "pairs_scored": 15, "households": 164,
        "reported_ceiling": 0.1963, "corrected_verdict": False, "p_value": 0.4726,
        "magnitude": None, "magnitude_noise_floor": None, "magnitude_p_value": None,
        "magnitude_refused": "not enough households per cell on the fit fold",
        "households_per_cell_on_the_fit_fold": 5.0,
    })
    assert "not enough households per cell" in refused
    assert "readings disagree" not in refused, (
        "the panel emits the disagreement regardless of whether there is a magnitude to disagree "
        "with, so its presence says nothing")
    # NO MAGNITUDE IS INVENTED FOR A RUNG THAT REFUSED ONE. Keyed to the block's own answered-branch
    # wording rather than to `0.2513`: the figure appears in the instrument's prose too, so the
    # number cannot discriminate, and this phrase is emitted only when this block renders an
    # estimate. A mutation that renders some other rung's magnitude here brings the phrase with it.
    assert "carry the three-way split the headline rung cannot" not in refused, (
        "the block renders an estimate for a rung that refused one")

    # LEG 3 -- an artefact with no whole-book rung at all renders nothing rather than an empty
    # claim. Every tree holding a pre-2026-09-06 artefact is in this state.
    absent = shown(None)
    assert "restricted to what the company holds" not in absent, (
        "a rung the artefact does not carry is being described to the reader anyway")


def test_WHICH_RUNG_THE_PROGRAMME_IS_GATED_ON_reaches_the_reader():
    """Both rungs were on this page and the CHOICE between them was still nobody's.

    They answer different questions over different populations -- what can be recovered about every
    account on supply, versus about the accounts that reached a priced renewal -- and only one of
    them carries an unbiased magnitude on this book. A page that shows both and names neither as
    the gate leaves the reader to pick, and in practice that means picking whichever one has a
    number: the outcome-driven selection the scope mechanism exists to prevent. So the decision is
    rendered, with its reason and its falsifier, beside whatever the chosen rung says.

    ALL THREE STATES, because a block the panel always emits says nothing. A gate with headroom, a
    gate that refuses, and an artefact carrying no gate at all are three different claims.

    MUTATION (must fire): drop the gate block; render the reason without the reading; render the
    reading without the reason; emit it unconditionally so an absent gate reads like a decided one.
    """
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
    c = dict(live.get("the_number_the_programme_rests_on") or {})
    if not c.get("available"):
        pytest.skip("no ceiling measurement in this tree; the absence path is covered above")

    def shown(gate):
        # SAME CORRECTION AS THE TEST ABOVE, from the other side (2026-09-07). `the_whole_book_rung`
        # renders the same magnitude this gate reads, and `on_the_magnitude` carries it in prose, so
        # LEG 2's `"0.2513" not in shut` was asking the whole panel a question only this block can
        # answer. Blanking the sibling and keying LEG 2 to this block's own wording is what makes
        # "a figure the gating rung did not produce" a claim about the gating rung.
        c["the_whole_book_rung"] = None
        c["the_a49_gate"] = gate
        live["the_number_the_programme_rests_on"] = c
        return _text(_render({"../data/delivery.json": live})["delivery-ceiling"]["innerHTML"])

    base = {
        "rung": "whole_book_pair_rung",
        "why": "R3 and R4 are delivered to every account on supply.",
        "what_would_move_it": "a change of SCOPE, never a change of reading.",
        "population": 164, "book": 164,
        "and_its_own_ceiling_verdict": {"clears": False, "p_value": 0.4726},
        "the_rung_it_is_not": {"rung": "all_candidate_pair_rung", "population": 69,
                               "answers": "what can be recovered about the households that "
                                          "reached a priced renewal."},
    }

    # LEG 1 -- the gate is open. The rung, its population, the figure, the reason and the falsifier
    # all have to be on the page: a named gate with no reason is an assertion, and a reason with no
    # falsifier is not a decision anyone can overturn.
    open_gate = shown({**base, "magnitude": 0.2513, "noise_floor": 0.1628, "p_value": 0.01,
                       "refused": None, "exceeds_its_own_noise_floor": True,
                       "consequence": "R3 and R4 are NOT retired by R1."})
    assert "gated on, and why it is this rung" in open_gate, "the gate block is not rendered at all"
    assert "whole_book_pair_rung" in open_gate, "the page does not name the rung it gates on"
    assert "0.2513" in open_gate and "0.1628" in open_gate
    assert "every account on supply" in open_gate, (
        "the page names a gate and not the reason it is that one, which is an assertion")
    assert "What would move it" in open_gate, (
        "a decision published without its falsifier cannot be overturned by evidence")
    assert "all_candidate_pair_rung" in open_gate and "69" in open_gate, (
        "the losing rung is deleted rather than carried, so the choice is invisible")
    assert "NOT retired" in open_gate
    # THE GATING RUNG'S OWN VERDICT DISAGREES WITH ITS MAGNITUDE ON THIS BOOK, and the reader has
    # to be told, or the magnitude reads as a bound this rung has not earned.
    assert "0.4726" in open_gate and "does not clear" in open_gate

    # LEG 2 -- the gating rung refuses. The refusal is what is rendered, and NO figure is invented
    # from the rung that was not chosen.
    shut = shown({**base, "magnitude": None, "noise_floor": None, "p_value": None,
                  "refused": "three-way split needs 8 households per cell on the fit fold",
                  "exceeds_its_own_noise_floor": False,
                  "consequence": "WE CANNOT TELL what R3 and R4 could be worth."})
    assert "carries no magnitude on this book" in shut
    assert "8 households per cell" in shut
    assert "WE CANNOT TELL" in shut
    # Keyed to the open-gate branch's own wording, not to `0.2513` -- see `shown` above for why the
    # number cannot discriminate. This phrase is emitted only when the gate renders a reading, so a
    # mutation that supplies one from the rung that was NOT chosen still fires it.
    assert "while its own selected-maximum verdict" not in shut, (
        "a figure the gating rung did not produce is on the page")

    # LEG 3 -- an artefact with no gate renders nothing rather than a decided-looking blank. Every
    # tree holding an artefact from before 2026-09-07 is in this state.
    absent = shown(None)
    assert "gated on, and why it is this rung" not in absent, (
        "a gate the feed does not carry is being described to the reader anyway")


# ── R3 and R4: the other two ceilings A49 exists for ─────────────────────────────────────────────
#
# Both instruments landed on 2026-09-07 and both wrote their readings into a file nobody opens: run
# on demand, reachable from no committed schedule, reported as orphans. A bound that reaches no
# reader cannot retire a candidate programme, which is the entire thing a ceiling is for -- EP13 ran
# twelve passes and the discipline arrived at pass seven, retiring five programmes that would
# otherwise have been built first and measured afterwards.
#
# Each control below drives the REAL door and asserts on the string a reader gets. The shape they
# all share: a figure is never enough. A ceiling published without the kind of bound it is, the
# population it is over, or the assumption its denominator rests on is a number a reader will quote
# and cannot judge.


def test_the_CARBON_ceiling_reaches_the_reader_with_the_assumption_it_rests_on(rendered):
    """R3's headline is at a shiftable share of 1.0 -- EVERY kilowatt-hour in the home moved --
    because no published source establishes a domestic shiftable share.

    The figure alone is the misleading publication: 91.7 kgCO2e per household-year reads as what a
    household would get, and it is what a household would get if it moved all of its load, which no
    household does. So the curve has to be on the page beside it, and the missing number has to be
    named as a gap rather than quietly filled.

    MUTATION (must fire): render the headline without the share curve, or without the sentence
    naming the share as unestablished.
    """
    body = _text(rendered["delivery-carbon-ceiling"]["innerHTML"])

    assert "91.7" in body, "R3's ceiling figure is not on the page at all"
    assert "4.03" in body, "the value of that carbon at the traded price is not on the page"
    # THE ASSUMPTION, NOT ONLY THE NUMBER. This is the load-bearing half.
    assert "every kilowatt-hour in the home can move" in body, (
        "the ceiling is published without the assumption its denominator rests on, so it reads as "
        "what a household would actually get")
    assert "No published source establishes" in body, (
        "the unestablished shiftable share is filled rather than named as a gap")
    # The curve, so a reader can scale it themselves rather than take 1.0 or nothing.
    assert "9.2" in body and "10%" in body, (
        "the share curve is absent, so the only reading offered is the one no household achieves")


def test_the_CARBON_ceiling_says_WHAT_KIND_of_bound_it_is_and_what_it_does_not_cover(rendered):
    """A CEILING retires a candidate outright; a FLOOR retires nothing. Conflating them is the
    error EP13's tenth pass made and its eleventh corrected, so the kind travels with the reading.

    And the scope travels too: R3 bounds the TIMING lever on ELECTRICITY, and names six levers it
    says nothing about. A reader shown "91.7 kg" without those would read a bound on the whole
    carbon programme.

    MUTATION (must fire): drop `bound_kind` from the render, or drop `not_bounded_by_this`.
    """
    body = _text(rendered["delivery-carbon-ceiling"]["innerHTML"])

    assert "CEILING" in body, "the page does not say what kind of bound this is"
    assert "what a bad reading would have proved" in body, (
        "the kind is rendered as a label rather than as the claim it makes")
    assert "TIMING lever on ELECTRICITY" in body, "the scope of the bound is not on the page"
    assert "does not retire" in body, (
        "the page does not say whether this reading retires the candidate")
    # The levers it is silent about, or the bound reads as covering the whole programme.
    assert "reduction -- using less" in body or "reduction — using less" in body, (
        "the levers this bound does NOT cover are absent, so it reads wider than it is")


def test_the_CARBON_ceiling_carries_the_HANDICAPS_and_the_TREND(rendered):
    """Two things a reader cannot reconstruct from the headline and needs to judge it.

    THE LADDER: perfect foreknowledge (40.7 g) -> what the published forecast actually captures
    (85.85%) -> divided by the feed's own measured within-day overstatement (1.47x) -> 23.8 g. A
    reader shown only the corrected figure cannot tell which step they disagree with.

    THE TREND decides WHEN rather than WHETHER: a programme worth 42.1% less than it was in 2016 is
    a different decision from a small one.

    MUTATION (must fire): render the corrected figure without the ladder, or drop the trend block.
    """
    body = _text(rendered["delivery-carbon-ceiling"]["innerHTML"])

    assert "40.7" in body, "the un-handicapped hindsight figure is not shown"
    assert "85.9%" in body or "85.85" in body, "the forecast capture handicap is not shown"
    assert "1.47" in body, "the within-day overstatement handicap is not shown"
    assert "23.8" in body, "the figure the handicaps land on is not shown"
    # The null, or "clears" is a claim against nothing a reader can see.
    assert "8.5" in body and "4.82" in body, (
        "the skill-free null and the margin over it are not both on the page")
    assert "It is shrinking" in body and "42.1" in body, (
        "the trend is absent, so a programme that is worth less every year reads as a static one")


def test_the_PRODUCT_ceiling_shows_the_CEILING_FLOOR_SPLIT_and_not_a_list_of_numbers(rendered):
    """R4's split IS the deliverable: three products we can bound from above, three we can only
    bound from below because the company holds no property attribute at all.

    A table of six numbers with no kind beside each one is exactly the publication A49 forbids --
    a negative on a floor retires nothing, and a reader who cannot tell which is which will read
    every small figure as a retirement.

    MUTATION (must fire): render the arms without their `bound_kind` column, or render a floor's
    `None` as 0.
    """
    body = _text(rendered["delivery-product-ceiling"]["innerHTML"])

    for product in ("tariff_fit", "time_shifting", "advice",
                    "efficiency_fabric", "solar", "heat_pump"):
        assert product in body, f"{product} is missing from the product table"
    assert "CEILING" in body and "FLOOR" in body, (
        "the arms are rendered without the kind of bound each one is")
    assert "3 / 6" in body, "the split is not shown as a count a reader can see at a glance"
    # AN UNMEASURED ARM IS NOT A ZERO. This is the one substitution that would invert the finding.
    assert "£0.00" not in body, (
        "an arm we cannot bound is rendered as a measured zero, which is the opposite claim")
    assert "no total" in body, (
        "the page does not say it refuses to total, so a reader will add two currencies across "
        "non-disjoint products")


def test_the_PRODUCT_ceiling_publishes_THE_CANONS_OWN_CHARGE_as_arithmetic(rendered):
    """*"The company can make a household cheaper and never greener."*

    That is the canon's charge against this company, and R4 turns it into arithmetic: the bounded
    arm that saves money (tariff fit) abates exactly zero by the director's standing rule, and the
    bounded arm that abates (time-shifting) saves no money at all. Everything that would really cut
    a household's carbon is a FLOOR for want of property data.

    This is the single most decision-relevant sentence either instrument produced and it belongs
    where he can read it, not in an artefact.

    MUTATION (must fire): render the arms table without this block, or state one side of it only.
    """
    body = _text(rendered["delivery-product-ceiling"]["innerHTML"])

    assert "the part that cannot cut carbon" in body, (
        "the two-sided finding A49 was minted for is not on the page")
    assert "tariff_fit" in body and "time_shifting" in body
    assert "never from discounting" in body, (
        "the reason tariff fit's carbon is zero is a RULE, and without it the zero reads as a "
        "measurement that came out small")
    # The acquisition, because it changes the shape of the programme rather than its size.
    assert "a data acquisition, not a model" in body, (
        "the page does not say what stands between R4 and a real bound")
    assert "0" in body and "29 logs" in body, (
        "the census behind the floor verdict is not shown, so the floors read as an opinion")


def test_the_MISSING_TARIFF_that_makes_time_shifting_half_a_product_reaches_the_reader(rendered):
    """The gap NEITHER instrument was looking for, and the reason it is published rather than filed.

    This book holds NO time-of-use tariff, so a shifted kilowatt-hour is not cheaper. R3 measures
    value CREATED and there is no instrument of SHARING it -- which is the mission's own
    two-sidedness ("value is created and THEN shared") showing up as a missing product rather than
    a missing measurement.

    A reader who sees time-shifting's £ column as "—" and is told nothing will read it as an arm
    that was measured and came out at nothing. It is the opposite: it was measured, it is worth
    real carbon, and there is currently no way to turn any of that into money for anyone.

    MUTATION (must fire): render the £ column as "—" without the explanation beside it.
    """
    body = _text(rendered["delivery-product-ceiling"]["innerHTML"])

    assert "no way to share the value" in body, (
        "the missing half of the mission's two-sidedness is not on the page")
    assert "time-of-use tariff and this book holds none" in body, (
        "the page does not say WHY time-shifting has no pounds, so the blank reads as a zero")
    assert "half a product" in body, (
        "the consequence is not stated: a lever with a carbon ceiling and no bill-saving ceiling "
        "is not a product yet")


@pytest.mark.parametrize("panel,key,marker", [
    ("delivery-carbon-ceiling", "the_most_a_carbon_score_could_be_worth", "91.7"),
    ("delivery-product-ceiling", "the_most_the_products_beyond_price_could_be_worth", "tariff_fit"),
])
def test_an_UNRUN_ceiling_instrument_renders_a_stated_absence_and_not_a_measured_zero(
        panel, key, marker):
    """FAIL CLOSED, AND SAY SO ON THE SURFACE. Both instruments are run on demand, so a tree
    without their artefacts is the ordinary case, not the exotic one.

    "We have not measured this" and "this is worth nothing" are opposite claims about a candidate
    programme, and a blank panel under a live heading renders as the second. This is the same class
    as the live door that served "Loading…" for eight days.

    MUTATION (must fire): return an empty dict from the panel builder instead of an
    `available: False` with a reason, or render the absence as an empty string.
    """
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
    live[key] = {"available": False,
                 "why": "the instrument has not been run in this tree, so no bound is shown."}
    body = _text(_render({"../data/delivery.json": live})[panel]["innerHTML"])

    assert body, "an unrun instrument leaves a live heading with nothing under it"
    assert "has not been run in this tree" in body, (
        "the panel does not say WHY it is empty, so absence reads as a measured zero")
    assert marker not in body, (
        "a figure from the live artefact is rendered even though the panel reports no measurement")


def test_the_two_ceiling_panels_are_WIRED_and_not_merely_defined():
    """The defect this whole file exists for, applied to the two panels added on 2026-09-07: a
    render function that is defined and never called serves a live heading forever.

    It is also the reason the generator IMPORTS both instruments rather than restating their
    artefact paths -- until this landed, `tools/r3_carbon_score_ceiling.py` and
    `tools/r4_product_ceiling.py` were reachable from no committed schedule and the orphan ratchet
    listed both. An instrument whose reading nobody sees is an orphan in the sense that matters.

    MUTATION (must fire): drop `renderCarbonCeiling(d)` from the fetch chain and this reds while
    the function itself still parses.
    """
    door = DOOR.read_text(encoding="utf-8")

    for fn in ("renderCarbonCeiling", "renderProductCeiling"):
        assert f"function {fn}" in door, f"{fn} is not defined"
        # Defined AND invoked: two occurrences minimum, the definition and at least one call.
        assert door.count(fn) >= 2, f"{fn} is defined and never called"

    from tools import generate_delivery_page as gen

    assert gen.R3_ARTEFACT.name == "r3_carbon_score_ceiling.json"
    assert gen.R4_ARTEFACT.name == "r4_product_ceiling.json"
