"""C2's bound must reach a reader of the DEPLOYED page -- fetched from poesys.net, not from disk.

WHAT WAS MEASURED BEFORE THIS WAS WRITTEN (2026-09-03), because the finding that drew this work
was half right and the half it got wrong matters more than the half it got right.

The lane-0 item said `site/capabilities/index.html` contains zero occurrences of "could not
react", "cannot react" or "two internal policies", and concluded the page publishes the baseline
comparison unbounded. The grep is correct. The conclusion is not: the bound is not markup. It is
composed clause-by-clause by `tools.generate_value_arms_data._reaction_sentence` from a probe of
the world's own competitor reference, delivered in `value_arms.json`, and assigned into
`#arms-market` by the door's own script. Driving the LIVE door at `https://poesys.net/capabilities/`
with its four LIVE feeds on 2026-09-03 renders, in `#arms-market`:

    "What the world could do about either arm. These are two of our own pricing policies, run
     through the same world. What that world could do about either of them is the bound on the
     comparison, and it is currently half of one. The market DOES defend ... Nothing contests the
     ceiling ... Read the comparison as an internal one."

So the sentence renders. What did NOT exist is the second half of SITE13's own done condition --
*"done means fetching the LIVE deployed surface and asserting the sentence renders, never that the
generator emits it"* -- a control that would go RED if it stopped. That is what this file is.

WHY NEITHER EXISTING CONTROL COVERS IT, and both of these were checked rather than assumed:

  * `site/test_the_baseline_comparison_reaches_the_reader.py` asserts the same property well, and
    its subject is the REPO door driven with the REPO feed. It is green on a tree that deploys
    nothing, and it is green while the edge serves an eight-hour-old copy of a feed whose schema
    has moved (`live_pixel_verify.cache_bust` records that exact outage). Repo-green and
    reader-served are different claims and this project has published the gap between them before.

  * `site/live_pixel_verify.py` DOES fetch the live surface, and it cannot see this defect. Its
    grading loop is `if not text: continue` -- an element the door left empty is dropped from the
    checked population before any assertion runs. `site/test_door_render_functions_are_wired.py`
    already records that shape in terms: *"grades only elements the page's script WROTE, so an
    element left at its shipped placeholder is outside the checked population -- fail-open for
    PARTIAL render"*. An `#arms-market` that renders nothing is precisely a partial render, so the
    one live control we own would report the door OK while the comparison went out unbounded.

KEYED TO THE PROPERTY, NEVER TO TODAY'S SENTENCE. C2's own wording -- "a market that could not
react to either" -- was HALF FALSE within half an hour of the director writing it, when
`simulation/competitor_reference.py` landed and gave the market a defence. A control pinned to
that string would today be defending a claim the world has already outgrown, and would go red for
the page becoming MORE honest. So what is asserted is: the reader is told the comparison is an
internal one between our own policies, and every clause the page states about what the world could
do AGREES, leg by leg, with what the live feed's own probe reports. Both legs can flip -- the
ceiling leg is unbuilt and will land -- and nothing here needs editing when they do.

FAIL-CLOSED, AND THE COST IS STATED RATHER THAN HIDDEN (R15). An unreachable host, a non-200 door,
a feed that will not parse, a probe that could not be driven: each is a FAILURE here, never a skip,
because "the bound is unverified" and "the bound is fine" must not report the same colour.
`live_pixel_verify` declined to be a test for this reason -- a network control in the commit path
wedges every offline commit -- and that argument was weighed and not simply inherited: it was made
for a crawler over twelve doors and every feed each one fetches, where a blip costs the whole gate.
This is one door, one panel, four feeds. The atom it discharges says R11 binds hardest here, and a
live check that passes when the network is down would discharge nothing. If it does start wedging
offline work, the reversal is to move the two live rungs behind an opt-in and leave `_judge` and
its mutation rungs where they are -- the judgement is already factored out for exactly that reason.

R15 -- the judgement is a PURE function so it can be mutated with no network at all, and each of
these was run and reverted:
  * `#arms-market` rendering empty            -> `test_MUTATION_an_empty_panel_is_a_defect_not_a_skip`
    (this is the one `live_pixel_verify` silently passes, and the reason this file exists).
  * the bound losing the word "internal"      -> `test_MUTATION_a_bound_that_never_says_internal_is_a_defect`
  * the page keeping C2's original wording
    while the probe reports a defending market -> `test_MUTATION_a_stale_bound_disagreeing_with_the_probe_is_a_defect`
  * an unavailable probe                      -> `test_MUTATION_an_unestablished_probe_is_a_defect_not_a_pass`
The null rung is `test_the_live_bound_as_served_is_judged_clean`: it must stay green through all
four, because every one of them is about a page that has gone wrong, not about this judge.
"""
from __future__ import annotations

import html as html_lib
import json
import re
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE))

from live_pixel_verify import (  # noqa: E402
    CANONICAL_HOST,
    LiveCheckUnavailable,
    _http_get,
    _resolve,
    feed_urls,
    run_harness,
)

#: The door the baseline comparison is published on, and the element the bound is assigned into.
DOOR_PATH = "/capabilities/"
PANEL = "arms-market"


def _text(fragment: str) -> str:
    """What a READER sees: tags stripped and entities decoded.

    The door escapes everything through its own `esc()` before assigning, so asserting against raw
    innerHTML reports a correct page red on `&quot;` and `&mdash;` that are never on the screen.
    """
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _judge(rendered: str, reaction: dict) -> list[str]:
    """Every way the served bound can be wrong, as a list of defects. Empty list = clean.

    PURE, and that is the design rather than tidiness: the live rungs below apply it to bytes off
    the wire, and the mutation rungs apply it to constructed inputs with no network at all. A judge
    that could only be exercised through a fetch could only be proven able to fail by breaking the
    live site, which is not a mutation anyone would run.

    `reaction` is the LIVE feed's own `market_reaction` block -- the same bytes the browser got,
    not the repo's copy. That is what makes leg agreement a real check: page and probe are fetched
    independently and a stale edge copy of either makes them disagree.
    """
    defects: list[str] = []
    text = rendered.strip()

    # THE FAIL-OPEN THIS FILE EXISTS FOR. An empty panel is the defect, not an absence of subject.
    if not text:
        defects.append(
            "#{} rendered NOTHING on the deployed page, so a reader met the baseline comparison "
            "with no statement of what the world could do about either arm -- an unbounded "
            "internal comparison is exactly the reading the block exists to prevent".format(PANEL))
        return defects

    low = text.lower()

    # The one clause that must survive every flip of both legs: a reader is told what CLASS of
    # comparison this is. Whatever the world turns out to be able to do, it is still our own two
    # policies being compared, and that is the half C2 says the evidence cannot carry without.
    if "internal" not in low:
        defects.append(
            "the served bound never tells the reader the comparison is an internal one between "
            "two of our own policies: {!r}".format(text))

    if not reaction:
        defects.append(
            "the live feed carries no `market_reaction` block at all, so nothing establishes "
            "whether the bound the page served is the one the world earned")
        return defects

    if not reaction.get("available"):
        # R15: an unavailable probe is an unavailable control. Reported, never skipped -- the page
        # still bounds the comparison on this branch, but nobody can say the bound is true.
        defects.append(
            "the world's competitive reference could not be driven for the publish now being "
            "served ({}), so the served bound is UNESTABLISHED rather than clean".format(
                reaction.get("reason")))
        return defects

    # Leg agreement, in BOTH directions. This is what stops the sentence drifting off the world:
    # apologising for a world that has stopped needing it, or claiming a pressure that is not there.
    if reaction.get("defends"):
        if "does defend" not in low:
            defects.append(
                "the live probe found a market that DEFENDS and the served page does not say so "
                "-- the bound is overstating the gap the arms were measured across: {!r}".format(
                    text))
    elif not ("nothing" in low and "defend" in low):
        defects.append(
            "the live probe found nothing defending and the served page does not say so: "
            "{!r}".format(text))

    if reaction.get("contests_the_ceiling"):
        if "ceiling is contested" not in low:
            defects.append(
                "the live probe found a CONTESTED ceiling and the served page still tells a "
                "reader that over-pricing is free: {!r}".format(text))
    elif "no competitive consequence" not in low:
        defects.append(
            "the live probe found nothing contesting the ceiling, so the served page must say "
            "over-pricing carries no competitive consequence: {!r}".format(text))

    return defects


@pytest.fixture(scope="module")
def served() -> tuple[str, dict]:
    """(rendered #arms-market text, live market_reaction) -- both off the wire, from poesys.net.

    The door is fetched, its feed urls are read from the markup the host actually served, those
    feeds are fetched, and the door's OWN boot path is driven with them. Nothing here reads
    `site/` off disk except the harness that does the driving.

    Every failure mode fails: unreachable host, non-200 door, non-200 or unparseable feed, a feed
    the door asked for that this fixture never supplied, and a script error inside the door.
    """
    try:
        status, body = _http_get(CANONICAL_HOST + DOOR_PATH)
    except LiveCheckUnavailable as exc:
        pytest.fail(
            "the deployed door could not be reached ({}) -- reported as a FAILURE and never "
            "skipped, because 'the published bound is unverified' and 'the published bound is "
            "fine' must not report the same colour (R15)".format(exc))
    assert status == 200, (
        "{}{} did not serve 200 directly (got {}), so whatever a reader met there, it was not "
        "the bounded comparison".format(CANONICAL_HOST, DOOR_PATH, status))
    html = body.decode("utf-8", errors="replace")
    assert html.strip(), "the deployed door served an empty body"

    feeds: dict[str, object] = {}

    def _load(url: str) -> None:
        if url in feeds:
            return
        try:
            fstatus, fbody = _http_get(_resolve(DOOR_PATH, url))
        except LiveCheckUnavailable as exc:
            pytest.fail("live feed {} could not be reached ({})".format(url, exc))
        assert fstatus == 200, (
            "the door fetches {} and the host served {} -- the page a reader opened had a feed "
            "missing under it".format(url, fstatus))
        try:
            feeds[url] = json.loads(fbody.decode("utf-8", errors="replace"))
        except json.JSONDecodeError as exc:
            pytest.fail("live feed {} did not parse as JSON: {}".format(url, exc))

    for url in feed_urls(html):
        _load(url)

    # Two passes, for the reason `live_pixel_verify.verify_door` documents: a static scan of the
    # markup only finds urls written literally, and a door that builds one from a variable would
    # otherwise be reported as a live outage against this checker's own blind spot.
    rendered = run_harness(html, feeds)
    discovered = [u for u in (rendered.get("_meta") or {}).get("requested", []) if u not in feeds]
    if discovered:
        for url in discovered:
            _load(url)
        rendered = run_harness(html, feeds)

    meta = rendered.pop("_meta", None) or {}
    assert not meta.get("scriptError"), (
        "the deployed door's own script threw ({}), so nothing below it rendered for a "
        "reader".format(meta.get("scriptError")))
    assert not meta.get("unresolved"), (
        "the deployed door fetched {}, which was not live -- what it rendered is not what a "
        "browser would".format(meta.get("unresolved")))

    element = rendered.get(PANEL) or {}
    text = _text(element.get("innerHTML") or "") or _text(element.get("textContent") or "")

    arms = feeds.get("../data/value_arms.json") or {}
    return text, (arms.get("market_reaction") or {})


def test_the_live_bound_as_served_is_judged_clean(served):
    """THE PROPERTY, on the surface a reader actually receives: the published baseline comparison
    never reaches a live reader without the bound C2 requires, and the bound agrees with the world.

    This is the null rung for the four mutations below -- it must stay green through every one of
    them, because each of those is about a page that has gone wrong and this one is about the page
    that is served.
    """
    text, reaction = served
    defects = _judge(text, reaction)
    assert not defects, "the deployed comparison reached a reader defective:\n  - " + "\n  - ".join(
        defects)


def test_the_bound_reaches_the_live_reader_beside_the_figures_it_bounds(served):
    """A bound on a different page, or below the fold of a reader's patience, is not a bound.

    The comparison's own figures and the qualification on them must be assigned by the same boot
    path of the same door -- which is what the fixture establishes by driving one page -- and the
    bound must be prose a reader can act on rather than a token. Fires on the bound being reduced
    to a link, a label or a pill.
    """
    text, _ = served
    assert len(text.split()) >= 25, (
        "the served bound is {} words -- too short to be the qualification the comparison needs "
        "rather than a label pointing at one: {!r}".format(len(text.split()), text))
    assert "policies" in text.lower(), (
        "the served bound never names WHAT is being compared, so a reader cannot tell an internal "
        "policy comparison from a claim about this supplier: {!r}".format(text))


# ── R15: the judge can fail, on each defect it names, with no network at all ──────────────────

_DEFENDING_WORLD = {"available": True, "defends": True, "contests_the_ceiling": False}

#: The sentence the live page serves today, as the four clauses `_reaction_sentence` composed for
#: a world that defends and does not contest the ceiling. Held here as a MUTATION SUBJECT only --
#: nothing above compares the served text to it, because a control pinned to today's wording goes
#: red when the page becomes more honest, which is this project's most repeated control defect.
_SERVED_TODAY = (
    "What the world could do about either arm. These are two of our own pricing policies, run "
    "through the same world. What that world could do about either of them is the bound on the "
    "comparison, and it is currently half of one. The market DOES defend: undercut it and the "
    "rival follows the price down within a quarter, so a 10% price advantage is worth -5.3% by "
    "the time it has re-priced once. A price advantage decays here instead of persisting. Nothing "
    "contests the ceiling: at or above the published cap the reference does not move at all, so "
    "over-pricing still carries no competitive consequence in this world and no rival targets "
    "this book. An arm that earns by charging more is reading that absence correctly, which is a "
    "fact about the world and not a result about the arm. Read the comparison as an internal one.")


def test_the_mutation_subject_is_itself_clean():
    """The vacuity guard. Every mutation below is "take a clean input and break ONE thing" -- if
    the starting point were already defective, each of them would pass for the wrong reason and
    this file would prove nothing.
    """
    assert _judge(_SERVED_TODAY, _DEFENDING_WORLD) == [], (
        "the mutation subject is already judged defective, so every mutation below is vacuous")


def test_MUTATION_an_empty_panel_is_a_defect_not_a_skip():
    """THE ONE THAT MATTERS. `live_pixel_verify.verify_door` does `if not text: continue` on this
    exact input and reports the door OK -- an element the door left empty never enters the checked
    population. That is the fail-open recorded in `test_door_render_functions_are_wired.py` and it
    is the reason a live crawler could not discharge SITE13.
    """
    defects = _judge("", _DEFENDING_WORLD)
    assert defects, "an #arms-market that rendered nothing was judged clean -- the same fail-open"
    assert "NOTHING" in defects[0], (
        "the empty panel was caught but not named as an empty panel, so the reason a reader met an "
        "unbounded comparison is not on the failure: {}".format(defects))


def test_MUTATION_a_bound_that_never_says_internal_is_a_defect():
    """The half of C2 that survives both legs flipping. A page can describe the market accurately
    and still leave a reader thinking they have been shown evidence about this supplier's
    performance -- which is the misreading the director's correction is about.
    """
    without = _SERVED_TODAY.replace("Read the comparison as an internal one.", "").replace(
        "internal", "in-house")
    defects = _judge(without, _DEFENDING_WORLD)
    assert any("internal one between" in d for d in defects), (
        "a bound that never tells the reader the comparison is internal was judged clean: "
        "{}".format(defects))


def test_MUTATION_a_stale_bound_disagreeing_with_the_probe_is_a_defect():
    """C2's own wording, against the world as it now is. This is the exact string the drawn item
    asked to be put on the page, and putting it there TODAY would be publishing a correction to a
    defect the world has already half fixed -- the market defends now.

    That is why the control is keyed to leg agreement and not to the sentence: the flattering
    failure and the apologetic one are the same shape, and only the probe can tell them apart.
    """
    stale = ("These are two internal policies compared in a market that could not react to "
             "either, so nothing contests the ceiling and over-pricing carries no competitive "
             "consequence. Read the comparison as an internal one.")
    defects = _judge(stale, _DEFENDING_WORLD)
    assert any("DEFENDS" in d for d in defects), (
        "the page served C2's original bound while the probe reported a defending market, and the "
        "judge did not notice the page and the world had come apart: {}".format(defects))


def test_MUTATION_an_unestablished_probe_is_a_defect_not_a_pass():
    """FAIL-CLOSED on the probe itself. The door renders a stated absence on this branch -- which
    is right, and is what stops a missing bound reading like a comparison that never needed one --
    but a bound nobody could establish is not a bound anybody has checked.
    """
    absent = ("WHETHER THE WORLD COULD ANSWER EITHER ARM COULD NOT BE ESTABLISHED for this "
              "publish, so read the comparison as an internal one between two of our own pricing "
              "policies and not as evidence about this supplier.")
    defects = _judge(absent, {"available": False, "reason": "the reference could not be driven"})
    assert any("UNESTABLISHED" in d for d in defects), (
        "a publish whose probe could not be driven was judged clean, so an unavailable control "
        "reported as a passing one: {}".format(defects))
    assert _judge(absent, {}) , (
        "a feed carrying no reaction block at all was judged clean")
