"""The page's household claim must be gated on the figure that can carry one.

THE DEFECT IT SERVES.
`site/capabilities/` published `discrimination_auc` at 0.627, outside its null, under the reading
*"so on this population the belief carried real information about who stays"*. The figure is real
and the word is not. That concordance counts every ordered pair of a retained decision against a
departed one, and only 402 of the 3,320 pairs behind it -- 12% -- put two households in the SAME
YEAR. The other 88% rank one era against another, and the book's realised retention runs 0.476
(2017) to 0.929 (2025) while the median `believed_p_retain` runs 0.45 to 0.82 across the same span.
Counted within the year only, the concordance is 0.444 on 402 pairs against a permutation null of
0.376-0.619 -- INSIDE it.

WHY THAT IS NOT A STYLISTIC RE-CUT, which is the objection this control has to survive. The
artefact's estimand is `level_vs_selection`: the part of the advantage a flat rate could have
earned against the part only a per-customer view could. A signal that moves with the calendar and
not within it contributes to the FIRST by construction. So "who stays" -- a household claim -- was
resting on evidence that is, for this page's own quantity, the level. It was also the single
measured number on the artefact arguing that households differ in a way the arm can see, which
makes it the published claim closest to the director's thesis, and it was false in the flattering
direction. Measured in
`docs/staging/SEAT_RESULT_THE_SELECTION_LEG_CANNOT_BE_SPLIT_ON_THIS_ARTEFACT_AND_THE_ONE_FIGURE_ARGUING_AGAINST_A_FLAT_WORLD_IS_A_BETWEEN_YEAR_EFFECT_2026-09-10.md`.

WHY THE SUBJECT IS THE RENDERED DOM AND NOT THE JSON. Same class as its neighbours in this
directory, and for the reason they were written: a corrected sentence sat in the code, in the feed
and in the working tree for a day while nothing put it on screen, and nothing was red, because
every assertion took an in-process object as its subject. So this drives the REAL door through
`site/_live_harness.mjs` AND the REAL producer (`tools.generate_value_arms_data.generate`), so a
mutation on either surface reds here rather than only on the one this file happened to pick.

R15 -- the mutations, each naming the defect it catches:

  * drop `_within_year_clause` from `_auc_reading`'s return -> `test_the_withdrawal_reaches_the
    _rendered_page` red. The fail-silent shape: the feed keeps the stratified block and the
    reader still meets the household claim.
  * restore the old sentence in the `else` branch unconditionally -> same test red. This is the
    one that matters: the words are the defect, not the absence of a caveat beside them.
  * let `_auc_reading`'s `within` argument default to `{}` instead of computing the block ->
    `test_a_caller_that_passes_no_stratified_block_still_gets_the_stratified_clause` red. An
    optional argument whose ABSENCE restores a withdrawn claim is the fail-open this change
    exists to close, and it is reachable from any second caller.
  * render only the prose and not the second figure -> `test_the_stratified_FIGURE_and_its_null
    _render_beside_the_unstratified_one` red. Prose a reader skims past leaves the big number
    bold and alone, which is the half they take away.
  * drop the `<ul>` caveat span -> `test_the_bind_asymmetry_reaches_the_reader_at_the_selection
    _leg` red.
  * drop `objective` from `_producing_commit`'s reading -> `test_the_objective_that_priced_the
    _book_reaches_the_reader` red.
  * make `_blob_has` return False when git cannot answer -> `test_an_unreadable_blob_refuses
    _rather_than_reporting_no_departure_cost` red. Returning False publishes "the objective
    charged nothing for a departure" on the strength of a failed subprocess -- fail-open in the
    flattering direction, since the flattering reading is that the page's book is the live one.

THE NULL CONTROLS, and they are the load-bearing half. A page that ALWAYS withdraws the household
reading is telling the reader nothing, and it would go on withdrawing it on the day a run finally
earns one -- which is the outcome this work is aimed at. Three separate branches here exist to be
taken rarely, so each is asserted REACHABLE before anything is asserted about what it says:

  * `test_a_run_whose_belief_DOES_rank_within_the_year_keeps_its_household_reading`
  * `test_a_run_whose_cap_binds_BOTH_arms_carries_no_bind_caveat`
  * `test_a_book_priced_under_the_LIVE_objective_carries_no_objective_caveat`

WHY NOT PIN 0.444 OR 402. Both move the moment a larger or different run is promoted to canonical,
and a control pinned to today's answer goes red when the instrument gets BETTER and stays green
when the claim rots. Every assertion here is keyed to the property -- is the household claim made
only when the stratified figure carries it -- never to today's figure.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from test_the_published_bytes_reader import (
    published_file,
    published_json,
    refuse_working_tree_reads,
)

SITE = Path(__file__).resolve().parent
PROJECT = SITE.parent
HARNESS = SITE / "_live_harness.mjs"
# THE SUBJECTS, AS PATHS IN GIT RATHER THAN FILES ON DISK (2026-09-10). Every constant below is a
# repo-relative STRING and not a `Path`, because a door test whose subject is `SITE / "data" /
# x.json` cannot tell "the reader can see this" from "someone in this tree has fixed it and not
# landed it" -- and those are the only two states it exists to separate. Both of the most serious
# defects found in the published value-arms comparison this month were REPAIRED IN THE WORKING
# TREE and stayed invisible to every control over them for exactly that reason.
# `site/test_the_published_bytes_reader.py` holds the reader and argues why the published copy is the INDEX copy
# and not `HEAD` -- a question about `tools/surgical_land.py`'s gate extract, not a matter of taste.
#
# The producer artefacts this file drives (`gv.THREE_ARM_PATH` and its current-world twin) are
# deliberately NOT subjects here: they are the generator's INPUT, and what this file grades is
# the page a reader loads. The guard at the foot is scoped to the constants below for that reason.
DOOR_REL = "site/capabilities/index.html"
CAPS_REL = "site/data/capabilities_door.json"
GROWTH_REL = "site/data/book_growth.json"
DD_ARMS_REL = "site/data/dd_opening_arms.json"

sys.path.insert(0, str(PROJECT))

#: The exact words being withdrawn. Kept as a constant because two assertions need to agree about
#: them: the one that says a reader no longer meets them as a claim, and the one that says a run
#: which EARNS them gets them back.
HOUSEHOLD_CLAIM = "real information about who stays"


def _producer():
    """Imported inside a helper so a collection-time ImportError reports as this file's failure."""
    import tools.generate_value_arms_data as gv

    return gv


def _feed(mutate=None, mutate_current=None, tmp_path=None) -> dict:
    """The REAL producer's output, optionally over a mutated artefact.

    TWO ARTEFACTS, TWO KNOBS, because the page reads two runs and they are not interchangeable.
    `mutate` bends the CANONICAL three-arm run, which is what `decisions` and `producing_commit`
    are drawn from. `mutate_current` bends the CURRENT-WORLD re-run, which is what
    `current_world.selection_leg` -- and so `bind_asymmetry` -- is drawn from. Bending the first
    and asserting on the second is how a fixture ends up proving nothing; this control's first
    draft did exactly that and the null test caught it.

    Each artefact is deep-copied before mutation, so a test that bends a run to reach a rare
    branch cannot leak into the next one.
    """
    gv = _producer()
    scratch = tmp_path or (PROJECT / "docs" / "observability")
    written = []

    def _stage(path: Path, mutator, name: str):
        if mutator is None:
            return None
        payload = mutator(copy.deepcopy(json.loads(path.read_text(encoding="utf-8"))))
        probe = Path(scratch) / "_door_probe_{}.json".format(name)
        probe.write_text(json.dumps(payload), encoding="utf-8")
        written.append(probe)
        return probe

    out = Path(scratch) / "_door_probe_value_arms.json"
    written.append(out)
    try:
        return gv.generate(
            out_path=out,
            three_arm_path=_stage(gv.THREE_ARM_PATH, mutate, "three_arm"),
            current_three_arm_path=_stage(
                gv.CURRENT_WORLD_THREE_ARM_PATH, mutate_current, "current_three_arm"),
        )
    finally:
        for probe in written:
            probe.unlink(missing_ok=True)


def _render(arms: dict) -> dict:
    """Drive the real door with the given arms feed and return its rendered elements.

    FAIL-CLOSED: an unresolved feed, a script error or a missing element all raise here rather
    than degrading to an empty string that a `not in` assertion would happily pass on. An
    unavailable check is a FAILED check.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and "
                    "an unavailable check is a FAILED check (R15)")
    payload = {
        "../data/value_arms.json": arms,
        "../data/capabilities_door.json": published_json(CAPS_REL),
        "../data/book_growth.json": published_json(GROWTH_REL),
        "../data/dd_opening_arms.json": published_json(DD_ARMS_REL),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(published_file(DOOR_REL))],
        input=json.dumps(payload), capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, "the render harness failed: {}".format(proc.stderr[-2000:])
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), (
        "the door asked for a feed this test did not supply ({}), so whatever it rendered is "
        "not what a browser would".format(meta.get("unresolved")))
    assert not meta.get("scriptError"), "the door's own script threw: {}".format(
        meta.get("scriptError"))
    return out


def _text(rendered: dict) -> str:
    """Every rendered string on the page, joined. The subject is what a reader can read.

    BOTH `innerHTML` AND `textContent`, because the harness reports each element as a pair and the
    figures this control asserts on are inside `<strong>` tags. Joining only one of them silently
    halves the subject -- and an assertion over an empty string passes every `not in` check it is
    given, which is the vacuous-pass shape this whole directory exists to avoid.
    """
    parts = []
    for element in rendered.values():
        if isinstance(element, str):
            parts.append(element)
        elif isinstance(element, dict):
            for key in ("innerHTML", "textContent"):
                value = element.get(key)
                if isinstance(value, str):
                    parts.append(value)
    joined = " ".join(parts)
    assert joined.strip(), (
        "the door rendered NOTHING this control can read. An assertion over an empty page passes "
        "every `not in` check it is given -- this is a failed check, not a clean one.")
    return joined


#: WHERE EACH CLAIM LANDS, because whole-page assertions on this door are TAUTOLOGICAL and the
#: poison round proved it. `withdrawn_claim.note` renders into `arms-note` and contains the words
#: "WITHDRAWN", "same year" and "cannot tell either way" in its own right -- so a whole-page check
#: for any of them passes with the READING left completely uncorrected. The first draft of this
#: file did exactly that: dropping `_within_year_clause` from `_auc_reading` fired ONE of four
#: tests that name it. Each reading-level assertion is therefore scoped to the element that
#: carries the reading.
DECISIONS = "arms-decisions"   # the concordance figures and `auc_reading`
REDRAW = "arms-redraw"         # the legs table and each leg's definition
NOTE = "arms-note"             # the run stamp, the objective clause, the withdrawal record


def _element(rendered: dict, element_id: str) -> str:
    """One element's rendered text, FAIL-CLOSED on an element the door never filled."""
    element = rendered.get(element_id)
    assert isinstance(element, dict), (
        "the door rendered no element `{}`, so the claim this control checks reaches no reader "
        "at all".format(element_id))
    text = " ".join(str(element.get(key) or "") for key in ("innerHTML", "textContent"))
    assert text.strip(), (
        "`{}` rendered EMPTY. An assertion over an empty string passes every `not in` check it "
        "is given -- this is a failed check, not a clean one.".format(element_id))
    return text


# --------------------------------------------------------------------------------------------
# The live page
# --------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def live() -> dict:
    return _feed()


@pytest.fixture(scope="module")
def live_render(live) -> dict:
    return _render(live)


@pytest.fixture(scope="module")
def live_page(live_render) -> str:
    """The WHOLE page. Correct subject only for "does this reach a reader anywhere" questions."""
    return _text(live_render)


@pytest.fixture(scope="module")
def live_decisions(live_render) -> str:
    """The element carrying the concordance figures and their reading."""
    return _element(live_render, DECISIONS)


@pytest.fixture(scope="module")
def live_redraw(live_render) -> dict:
    """The element carrying the legs table and each leg's definition."""
    return _element(live_render, REDRAW)


@pytest.fixture(scope="module")
def live_note(live_render) -> str:
    """The stamp line: run provenance, the objective clause, the withdrawal record."""
    return _element(live_render, NOTE)


def test_the_producer_publishes_the_stratified_twin(live):
    """The block exists, carries its own null, and names its pair count."""
    within = (live["decisions"] or {}).get("discrimination_auc_within_year") or {}
    assert within.get("available") is True, (
        "the canonical run publishes per-decision `scored_decisions`, so the concordance CAN be "
        "stratified by the term's own year and the page has no excuse to withhold it: " + str(
            within.get("reason")))
    for key in ("auc", "same_year_pairs", "all_pairs", "null_95_low", "null_95_high",
                "p_two_sided", "inside_the_null"):
        assert within.get(key) is not None, (
            "a stratified figure published without {} is the unbounded figure again under a new "
            "name".format(key))
    assert 0 < within["same_year_pairs"] < within["all_pairs"], (
        "if every pair is a same-year pair the stratification is a no-op and this whole control "
        "is measuring nothing")


def test_the_stratified_figure_renders_AS_A_FIGURE_and_not_only_inside_the_prose(
        live, live_render):
    """THE MUTATION THAT SURVIVED, and it survived because the test was missing.

    Deleting the second `<strong>` from the door left all thirteen assertions green: the reading's
    own prose repeats the same numbers ("the concordance is 0.444 ... on those 402 pairs"), so a
    substring check over the element cannot tell a RENDERED FIGURE from a MENTION. That distinction
    is the whole deliverable here -- a reader meets one bold number and skims the sentence, which
    is exactly how 0.627 came to be the page's claim in the first place. So this asserts the
    structure: the stratified figure must be marked up as a figure, in the same element and the
    same way as the unstratified one it has to be weighed against.
    """
    html = (live_render.get(DECISIONS) or {}).get("innerHTML") or ""
    assert html.strip(), "`{}` rendered no markup at all".format(DECISIONS)
    within = live["decisions"]["discrimination_auc_within_year"]
    unstratified = live["decisions"]["discrimination_auc"]
    for figure, what in ((unstratified, "unstratified"), (within["auc"], "within-year")):
        marked = "<strong>{:.3f}</strong>".format(figure)
        assert marked in html, (
            "the {} concordance ({:.3f}) does not render as a FIGURE -- it appears, if at all, "
            "only inside the prose. A reader weighs the bold numbers; a figure that is only "
            "mentioned is the half they skim past.".format(what, figure))


def test_the_stratified_FIGURE_and_its_null_render_beside_the_unstratified_one(live, live_decisions):
    """The second figure reaches the reader as a FIGURE, not only inside prose."""
    within = live["decisions"]["discrimination_auc_within_year"]
    unstratified = live["decisions"]["discrimination_auc"]
    assert "{:.3f}".format(unstratified) in live_decisions, (
        "the unstratified figure stopped rendering; this control compares two figures and one of "
        "them is gone")
    assert "{:.3f}".format(within["auc"]) in live_decisions, (
        "the WITHIN-YEAR concordance does not reach the rendered page. The reader meets the "
        "bold {:.3f} and nothing to weigh it against.".format(unstratified))
    assert "{:.3f}".format(within["null_95_low"]) in live_decisions, (
        "the stratified figure renders without its null. A figure published without the bound "
        "its sample size earns is worse than no figure.")
    assert "{:.3f}".format(within["null_95_high"]) in live_decisions
    assert str(within["same_year_pairs"]) in live_decisions, (
        "the same-year pair count does not render, so a reader cannot see how thin the "
        "stratified evidence is")


def test_the_route_out_of_the_withdrawal_reaches_the_reader_in_the_same_element(
        live, live_decisions):
    """A withdrawal with no route out is where an inferential claim goes quietly to die.

    THE DEFECT. From 2026-09-10 this page withdrew its only measured evidence that the arm can tell
    households apart -- the thesis's own central claim -- and said, of what it would take to earn it
    back, only that "about four times as many would halve the interval". No book size, no cost, and
    that sentence was itself indexed on the wrong unit. The selection leg on the same page got its
    route (2.8x or 44.9x, priced, with the cost named); the more important leg got a shrug.

    THE SUBJECT IS THE SAME ELEMENT AS THE WITHDRAWAL, not the page. A remedy rendered three
    panels down is a remedy the reader who met the withdrawal never sees, and `_element` is the
    only assertion shape that can tell those apart.
    """
    within = live["decisions"]["discrimination_auc_within_year"]
    remedy = within.get("what_would_settle_it") or {}
    assert remedy.get("available") is True, (
        "the run carries a permuted interval and a sample size, so what would settle it is "
        "arithmetic and not a judgement: " + str(remedy.get("reason")))
    required = remedy["the_requirement"]["scored_decisions_needed"]
    assert str(required) in live_decisions, (
        "the number of scored decisions that would settle this figure ({}) does not render beside "
        "the withdrawal".format(required))
    assert str(remedy["in_same_year_pairs"]["same_year_pairs_needed"]) in live_decisions, (
        "the requirement renders in decisions and not in the PAIRS the reader met the figure in, "
        "so the two counts a reader would confuse are not both on the page")
    assert str(remedy["the_book"]["renewals_the_world_must_offer"]) in live_decisions, (
        "the page prices the instrument and never the book, so 'can this world supply it' is left "
        "to the reader")


def test_the_page_says_re_running_seeds_does_not_buy_the_missing_evidence(live, live_decisions):
    """DEFECT: the cheap route agrees with the arithmetic right up to the point it stops.

    4.75 pooled seeds supply 584 rows, and five copies of this run's own 123 rows -- containing not
    one new observation -- put the unchanged figure OUTSIDE its null. A reader with a machine and
    the requirement above will reach for seeds first, so the refusal has to be where the
    requirement is, not in a note.
    """
    seeds = (live["decisions"]["discrimination_auc_within_year"]
             .get("what_would_settle_it") or {}).get("run_seeds") or {}
    assert seeds.get("supplies_it") is False, seeds
    lowered = live_decisions.lower()
    assert "seed" in lowered, (
        "nothing on the page tells a reader whether re-running seeds supplies this book, and the "
        "arithmetic beside it says it does")
    assert "0.444030" in live_decisions or "no new information" in lowered, (
        "the refusal renders as an assertion with its demonstration stripped -- the unchanged "
        "figure under replication IS the argument")


def test_the_page_says_a_bigger_book_would_not_make_the_grading_population_independent(
        live, live_decisions):
    """DEFECT: a reader who meets a priced requirement takes away that a bigger book fixes it.

    It does not. Four of the accounts the concordance is graded on left under the value arm and not
    under the control, so the arm's own price rise manufactured part of the outcome it is scored
    against -- and no sample size touches that. Both halves have to be in the same block or the
    first reads as the whole answer.
    """
    gap = (live["decisions"]["discrimination_auc_within_year"]
           .get("the_grading_population_is_not_independent") or {})
    assert gap.get("available") is True, gap
    moved = gap["outcome_moved_by_the_arms_own_price"]
    assert str(moved["departures_on_those_accounts"]) in live_decisions
    # NOT PINNED TO FALSE. The published feed says whether the independent grading exists yet;
    # this door's subject is that the reader meets the population caveat EITHER WAY, because a
    # bigger book fixes neither branch. A `is False` here would go red the day the run supplies
    # the grading, which is the outcome the block exists to make worth having.
    assert isinstance(gap["is_it_available_today"], bool)
    # The REFUSAL of the obvious repair, not merely the statement of the problem. Naming the
    # contaminated accounts without refusing "drop them" invites exactly that edit.
    assert "post-treatment" in live_decisions, (
        "the page names the contaminated accounts and does not tell the reader why removing them "
        "is not the repair, which is the edit a careful reader would make next")


def test_the_page_never_prices_a_larger_book_it_cannot_price(live, live_decisions):
    """FAIL-OPEN, and in the flattering direction. One clean probe point multiplied by the book
    multiple reads exactly like a measured cost, and it would let this page tell a reader what
    settling the thesis costs on the strength of a gradient nobody has measured."""
    cost = ((live["decisions"]["discrimination_auc_within_year"].get("what_would_settle_it") or {})
            .get("the_cost") or {})
    assert cost.get("available") is True, cost
    here = cost["this_book"]
    assert "{:.1f}".format(here["machine_hours_at_least"]) in live_decisions, (
        "the cost of the run we HAVE does not reach the page, so 'at least this much' has no "
        "anchor")
    if not cost["a_larger_book"].get("available"):
        assert "not established" in live_decisions.lower(), (
            "the page prices a larger book from a probe that declares no slope")


def test_a_probe_that_HAS_a_slope_takes_the_refusal_off_the_page(live):
    """THE NULL CONTROL, and the branch above is worthless without it.

    A page that says "not established" whatever the probe reports is not reporting, it is decorating
    -- and it would go on saying it on the day `settlement_ceiling_probe` lands its second clean
    point, which is the outcome this block exists to make worth having. The refusal must be keyed
    to the probe's own `recommendation.decidable` and not to today's answer, so this asserts the
    OTHER branch is reachable before anything is asserted about the one that is live.
    """
    feed = copy.deepcopy(live)
    cost = (feed["decisions"]["discrimination_auc_within_year"]["what_would_settle_it"]
            ["the_cost"])
    assert cost["a_larger_book"].get("available") is False, (
        "this machine's probe now declares a slope, so the fixture below is bending a branch that "
        "is already live and the test has stopped measuring anything")
    cost["a_larger_book"] = {"available": True, "clean_points": 2, "marginal": []}
    page = _element(_render(feed), DECISIONS)
    assert "not established" not in page.lower(), (
        "the page still refuses to price a larger book after the probe supplied a slope -- the "
        "refusal is pinned to a string and not to the probe's own verdict")
    assert "2 clean points" in page, (
        "the refusal came off and nothing replaced it, so a reader who could have been told what "
        "the larger book costs is told nothing at all")


def test_the_withdrawal_reaches_the_rendered_page(live, live_decisions):
    """A reader must not meet the household claim as a CLAIM while the stratified figure is inside
    its null.

    THE ASSERTION IS ASYMMETRIC ON PURPOSE. The withdrawn words are allowed to appear -- quoted,
    beside the word WITHDRAWN -- because this page's whole claim on anyone's trust is that it
    keeps its corrections visible. What is forbidden is the sentence standing as the page's own
    reading, which is what `so on this population the belief carried ...` was.
    """
    within = live["decisions"]["discrimination_auc_within_year"]
    if not within.get("inside_the_null"):
        pytest.skip("this run's stratified figure clears its null, so there is nothing to "
                    "withdraw -- covered by the null control below")
    assert "WITHDRAWN" in live_decisions, (
        "the stratified figure sits inside its null and the page says nothing about the "
        "household reading it was carrying")
    assert "the belief carried " + HOUSEHOLD_CLAIM not in live_decisions, (
        "the page still states the household claim as its own reading. The words are the defect, "
        "not the absence of a caveat beside them.")


def test_the_reader_is_told_the_pairs_compare_eras(live_decisions):
    """The REASON, not just the verdict. A reader told only "withdrawn" cannot check it."""
    lowered = live_decisions.lower()
    assert "same year" in lowered or "same-year" in lowered, (
        "the page withdraws the claim without telling the reader that the pairs behind it "
        "compare eras, which is the only fact that makes the withdrawal checkable")


def test_the_reading_a_reader_meets_is_the_one_the_producer_DECLARES(live, live_decisions):
    """The claim sentence is PINNED to the producer's own constant, so a reword cannot be silent.

    THIS IS THE LEG `HOUSEHOLD_CLAIM` STRUCTURALLY COULD NOT BE. That assertion forbids one
    sentence, not the claim the sentence makes. On 2026-09-10 a poison restating the same household
    claim in different words -- "the belief told us which individual households would leave and
    which would not", a STRONGER claim than the withdrawn one -- left this file at 14 passed, with
    the literal guard green throughout.

    No control can grep for paraphrase, and a wordlist would be the same blindness in a longer
    form. What a control CAN require is that the sentence a reader meets is the one the producer
    DECLARES for the branch this run took. That is a property rather than today's answer, and it
    converts a silent upward reword into a deliberate edit to a named constant whose own comment
    says what it must not become.

    Residual, stated rather than hidden: editing the constant itself still passes here. That is the
    intended remaining surface -- deliberate, reviewable, and beside the reason -- not a gap this
    leg pretends to close.
    """
    gv = _producer()
    within = live["decisions"]["discrimination_auc_within_year"]
    earned = bool(within.get("available")
                  and not within.get("inside_the_null")
                  and (within.get("auc") or 0.0) >= 0.5)

    assert gv._EARNED_CLAIM_SENTENCE != gv._UNEARNED_CLAIM_SENTENCE, (
        "the two readings collapsed to one string, so this control can no longer tell an earned "
        "household claim from an unearned one -- and neither could a reader")

    expected = gv._EARNED_CLAIM_SENTENCE if earned else gv._UNEARNED_CLAIM_SENTENCE
    forbidden = gv._UNEARNED_CLAIM_SENTENCE if earned else gv._EARNED_CLAIM_SENTENCE

    assert expected in live_decisions, (
        "the reading on the page is not the sentence the producer declares for this run "
        "(household reading earned: {}). A reword that reaches a reader without reaching the "
        "constant is exactly the drift this leg exists to catch.".format(earned))
    assert forbidden not in live_decisions, (
        "the page carries the other branch's reading as well as the one this run earned "
        "(household reading earned: {}), so a reader meets both claims at once".format(earned))


def test_the_page_does_NOT_claim_the_belief_is_uninformative(live_decisions):
    """The mirror-image overclaim, which would be just as unearned.

    A within-year figure inside its null establishes that the sample cannot tell IN EITHER
    DIRECTION. Reading it as "the belief knows nothing" is the same error with the sign flipped,
    and it is the one a page correcting itself is most tempted into.
    """
    lowered = live_decisions.lower()
    for overclaim in ("the belief is uninformative",
                      "the belief carries no information",
                      "knows nothing about who stays"):
        assert overclaim not in lowered, (
            "the page swapped one overclaim for its mirror image: " + overclaim)
    assert "cannot tell in either direction" in lowered or "either way" in lowered, (
        "the page withdraws the claim without saying that this sample cannot settle it in "
        "either direction, which is what 402-odd same-year pairs actually support")


def test_the_bind_asymmetry_reaches_the_reader_at_the_selection_leg(live, live_redraw):
    """`selection_gbp` is not the value of choosing per customer, and the reader must meet that
    where they meet the leg."""
    leg = (live["current_world"] or {}).get("selection_leg") or {}
    bind = leg.get("bind_asymmetry") or {}
    assert bind.get("available") is True, (
        "the run publishes a priced count and a ceiling-bound count for both arms, so the "
        "asymmetry is measurable: " + str(bind.get("reason")))
    if not bind.get("asymmetric"):
        pytest.skip("the cap binds both arms on this run -- covered by the null control below")
    assert str(bind["value_arm_ceiling_bound"]) in live_redraw, (
        "how many of the value arm's decisions the cap binds does not reach the reader")
    assert str(bind["level_arm_priced"]) in live_redraw, (
        "the level arm's priced count does not reach the reader, so the 0-bound half of the "
        "asymmetry cannot be checked")
    assert "NOT THE VALUE OF CHOOSING PER CUSTOMER" in live_redraw, (
        "the reader meets the choosing leg with no statement that the contrast is between an arm "
        "the cap binds and an arm it never binds -- a confound in the QUANTITY, which is the one "
        "kind no larger book removes")


def test_the_objective_that_priced_the_book_reaches_the_reader(live, live_note):
    """Which pricing RULE drew these figures, not merely which commit."""
    objective = (live["producing_commit"] or {}).get("objective") or {}
    assert objective.get("established") is True, (
        "this publish could not read the renewal objective at both commits: " + str(
            objective.get("reason")))
    if not objective.get("objective_moved_since_the_run"):
        pytest.skip("the book was priced under the live objective -- covered by the null control")
    assert "OBJECTIVE MOVED" in live_note, (
        "the page tells a reader the CODE was replaced, which reads as a refactor, and never that "
        "the ARM described is not the arm running")
    assert "departure" in live_note.lower(), (
        "the objective clause reaches the page without naming what actually changed")


def test_a_caller_that_passes_no_stratified_block_still_gets_the_stratified_clause(live):
    """THE FAIL-OPEN THIS CHANGE EXISTS TO CLOSE.

    `_auc_reading`'s `within` argument is optional. An optional argument whose ABSENCE restores a
    withdrawn claim is a defect reachable from any second caller, and this file's own producer is
    not the only one: `_method_skill` reads the same figure under a second key.
    """
    gv = _producer()
    three = json.loads(gv.THREE_ARM_PATH.read_text(encoding="utf-8"))
    belief = three["belief_vs_outcome"]
    attribution = gv._auc_attribution(three, belief, None)
    bare = gv._auc_reading(belief, attribution)
    assert "WITHDRAWN" in bare or "within the year" in bare, (
        "called without the stratified block, the reading fell back to the pre-2026-09-10 "
        "sentence. The default has to COMPUTE the block, never skip the clause.")


def test_the_second_key_carries_the_stratified_twin_too(live):
    """`churn_auc_for_contrast` is the SAME figure under another name.

    Gating one key and leaving the other bare puts the withdrawn claim back on the page through
    the other door -- the shape `_book` records against itself for the settled-book counts.
    """
    skill = live.get("method_skill") or {}
    if skill.get("churn_auc_for_contrast") is None:
        pytest.skip("this run publishes no contrast AUC under the second key")
    twin = skill.get("churn_auc_within_year") or {}
    assert twin.get("available") is True, (
        "`churn_auc_for_contrast` is published without its stratified twin, so the unstratified "
        "figure reaches the page unchallenged by a second route")
    assert twin.get("auc") == live["decisions"]["discrimination_auc_within_year"]["auc"], (
        "the two keys carry DIFFERENT stratified figures, so the page holds two answers to one "
        "question")


# --------------------------------------------------------------------------------------------
# The null controls -- every rare branch asserted REACHABLE before anything is asserted about it
# --------------------------------------------------------------------------------------------

def test_a_run_whose_belief_DOES_rank_within_the_year_keeps_its_household_reading():
    """THE LOAD-BEARING NULL CONTROL.

    A page that always withdraws is telling the reader nothing, and would go on withdrawing on
    the day a run earns a household reading -- which is the outcome this work aims at. The
    fixture makes the belief rank perfectly WITHIN each year, so the stratified figure clears its
    null on the page's own arithmetic rather than on a number typed here.
    """
    def rank_within_year(three: dict) -> dict:
        rows = three["belief_vs_outcome"]["scored_decisions"]
        for row in rows:
            # Perfect within-year separation: retained households believed above every departed
            # one in the same year, with the LEVEL held flat across years so the between-year
            # component contributes nothing. This is the mirror of the live run.
            row["believed_p_retain"] = 0.9 if row["retained"] else 0.1
        return three

    feed = _feed(mutate=rank_within_year)
    within = feed["decisions"]["discrimination_auc_within_year"]
    assert within["available"] is True
    assert within["inside_the_null"] is False, (
        "the fixture was supposed to make the belief rank households within their own year and "
        "it did not clear the null -- this control cannot prove the branch is reachable, so it "
        "is measuring nothing (AUC {:.3f}, null {:.3f}-{:.3f})".format(
            within["auc"], within["null_95_low"], within["null_95_high"]))
    assert within["auc"] > 0.5

    page = _element(_render(feed), DECISIONS)
    assert "the belief carried " + HOUSEHOLD_CLAIM in page, (
        "a run whose belief DOES rank one household against another within a year was still "
        "refused its household reading. The gate is refusing everything, which passes every "
        "test of a guard and guards nothing.")
    assert "are WITHDRAWN" not in page, (
        "the page withdrew a claim the stratified figure supports")


def test_a_run_whose_cap_binds_BOTH_arms_carries_no_bind_caveat():
    """The bind caveat must come OFF when the partition exists on both sides."""
    def bind_both(three: dict) -> dict:
        for key in ("decision_shape", "level_arm_decision_shape"):
            shape = three.get(key) or {}
            if shape.get("priced"):
                shape["ceiling_bound"] = max(1, int(shape["priced"] * 0.5))
        return three

    # THE CURRENT-WORLD ARTEFACT, not the canonical one: `current_world.selection_leg` is drawn
    # from the re-run, and this control's first draft bent the canonical run and asserted on the
    # re-run's block. It failed loudly, which is the only reason the fixture is right now.
    feed = _feed(mutate_current=bind_both)
    bind = feed["current_world"]["selection_leg"]["bind_asymmetry"]
    assert bind.get("available") is True, (
        "the mutated re-run publishes both counts, so the block must be available: "
        + str(bind.get("reason")))
    assert bind["asymmetric"] is False, (
        "both arms carry a bound partition and the block still calls the leg asymmetric -- the "
        "predicate is pinned to today's answer rather than to the property")
    assert "NOT THE VALUE OF CHOOSING PER CUSTOMER" not in _element(_render(feed), REDRAW), (
        "the caveat stayed on the page after the confound it describes was removed. A control "
        "that cannot go quiet is decoration.")


def test_a_book_priced_under_the_LIVE_objective_carries_no_objective_caveat():
    """The objective clause must come OFF when the run and the tree price the same rule."""
    gv = _producer()
    head = gv.PUBLISHING_TREE_COMMIT
    if not head:
        pytest.skip("this tree could not resolve its own HEAD, so the two sides cannot be paired")

    def produced_at_head(three: dict) -> dict:
        three.setdefault("producing_commit", {})["commit"] = head
        return three

    feed = _feed(mutate=produced_at_head)
    objective = feed["producing_commit"]["objective"]
    assert objective["established"] is True, str(objective.get("reason"))
    assert objective["objective_moved_since_the_run"] is False, (
        "a run produced at the publishing tree's own commit was still reported as priced under a "
        "different objective -- the comparison is not reading the blobs it claims to")
    assert "OBJECTIVE MOVED" not in _element(_render(feed), NOTE), (
        "the staleness caveat stayed on the page for a book the live objective priced")


def test_an_unreadable_blob_refuses_rather_than_reporting_no_departure_cost():
    """FAIL-CLOSED, and in the direction that costs us.

    A shallow clone, a garbage-collected commit or a moved path all make git unable to answer.
    Returning False there would publish "the objective charged nothing for a departure" on the
    strength of a failed subprocess -- and since the FLATTERING reading is that the page's book is
    the live one, a fail-open here is a fail-open toward flattery in both directions at once.
    """
    gv = _producer()
    absent = "0" * 40
    assert gv._blob_has(absent, gv._RENEWAL_OBJECTIVE_PATH, gv._DEPARTURE_TERM) is None, (
        "an unreadable commit returned a BOOLEAN, so the page will state which objective priced "
        "the book on the strength of a failed git call")
    assert gv._blob_has(None, gv._RENEWAL_OBJECTIVE_PATH, gv._DEPARTURE_TERM) is None

    moved = gv._renewal_objective_moved(absent, gv.PUBLISHING_TREE_COMMIT)
    assert moved["established"] is False
    assert "unestablished" in (moved.get("clause") or "").lower(), (
        "a comparison that could not be made must say so on the surface -- 'we cannot tell' is a "
        "result and it belongs on the page")


#: A grading the artefact could carry, shaped exactly as `run_value_cycle_ab
#: .belief_against_control_outcomes` returns it on its available branch. The figures are
#: deliberately unlike anything else on the page so an assertion cannot pass on a coincidence:
#: 0.583 appears nowhere in the live feed, and neither does a 117/79/38 population.
_GRADED = {
    "available": True,
    "discrimination_auc": 0.583,
    "auc_population": {"retained": 79, "left": 38},
    "priced_and_scored": 117,
    "population_terms_absent_from_the_control_world": 6,
    "scored_share_of_priced": 0.87,
}


def _with_grading(block: dict):
    """Bend the THREE-ARM artefact, never the page feed, and let the real producer read it.

    The distinction is the whole value of these two controls. Hand-writing
    `the_grading_population_is_not_independent` into the feed would assert that the render can
    display a dict I built to be displayable -- a fixture fitted to its own conclusion. Putting
    the block where the RUN puts it makes `_independent_grading_today` the subject too, so the
    producer and the door are proved on one path.
    """
    def mutate(three_arm: dict) -> dict:
        three_arm["belief_against_control_outcomes"] = copy.deepcopy(block)
        return three_arm

    return mutate


def test_a_run_that_HAS_the_independent_grading_puts_the_figure_on_the_page():
    """DEFECT: the page had ONE branch, and it was the one that says the figure does not exist.

    `_independent_grading_today` was re-keyed on 2026-09-10 to read `available` off the artefact
    instead of publishing a hard-coded False. The door that consumes it was not. So the first run
    to write `belief_against_control_outcomes` would have produced a page that silently dropped
    the sentence explaining the absence, went on listing the remedy as still REQUIRED, and
    rendered the grading nowhere -- `esc(undefined)` is the empty string, so nothing would have
    looked broken to anyone reading the page or the diff.

    That is the pointer-with-two-ends shape: the producer end was un-pinned and the render end
    stayed keyed to today's answer. A control on the producer alone cannot see it.
    """
    page = _element(_render(_feed(mutate=_with_grading(_GRADED))), DECISIONS)
    assert "0.583" in page, (
        "the artefact carries an independent grading and the reader never meets the figure -- the "
        "one number the whole block exists to make checkable renders nowhere")
    assert "117" in page and "79" in page and "38" in page, (
        "the figure reached the page without the population behind it. A concordance whose "
        "retained/left counts are not stated is a number nobody can weigh")
    # THE CAVEAT SURVIVES THE FIGURE ARRIVING, and this is the half most likely to be lost in a
    # later tidy-up. The OUTCOME becomes independent of the belief; the POPULATION does not.
    assert "population" in page.lower() and "value-arm survival" in page.lower(), (
        "the independent figure is published without the caveat that the POPULATION is still the "
        "value arm's priced set, so a reader takes independence of the outcome for independence "
        "of the grading")
    assert "6" in page, "the terms absent from the control world are not counted on the page"
    # THE TENSE FLIPS WITH THE BRANCH. `what_an_independent_population_must_look_like` is phrased
    # as a requirement. Rendered unchanged beside a delivered grading it reads as still-outstanding
    # work, which is the stale-in-the-pessimistic-direction half of the same defect.
    assert "and what this run supplies" in page, (
        "the requirements list is introduced as something still to be met while the run beside it "
        "meets them")
    # ...AND THE ABSENCE SENTENCE GOES, because leaving it beside the figure tells the reader the
    # thing in front of them does not exist.
    assert "no (account, term, retained) list" not in page.lower(), (
        "the page still explains why the grading is unavailable while displaying it")


def test_a_run_WITHOUT_it_still_says_why_and_does_not_show_a_figure():
    """THE NULL CONTROL, and the test above is worth nothing without it.

    A door that renders the grading paragraph unconditionally would pass every assertion above
    while telling a reader on a run that has no such grading that one exists. Both branches are
    driven over ONE artefact differing in ONE field, which is the only way to show the render is
    keyed to the run's own `available` rather than to the shape of whatever fixture arrived.
    """
    refused = {"available": False,
               "why_not": "this fixture's control arm published no customer_events"}
    page = _element(_render(_feed(mutate=_with_grading(refused))), DECISIONS)
    assert "0.583" not in page, (
        "the page shows an independent concordance for a run that refused to compute one")
    # THE HEADING, NOT ONLY THE NUMBER, and this is the assertion that gives the null control its
    # teeth. Rendering the grading paragraph unconditionally puts no false FIGURE on the page --
    # the fields are absent, so it degrades to "no figure" -- and would survive an assertion that
    # only looked for 0.583. It would still announce to the reader that this run's belief has been
    # graded against an independent outcome, which it has not.
    assert "Graded against an outcome its own price did not cause" not in page, (
        "the page announces an independent grading for a run that has none -- the paragraph is "
        "rendered unconditionally rather than keyed to the run's own `available`")
    assert "no customer_events" in page, (
        "the run named its own reason for refusing and the reader gets none of it -- a refusal "
        "that does not say why is how the refusal itself stops being checkable")
    # The remedy stays phrased as OUTSTANDING here, which is exactly what it is on this branch.
    assert "would have to be" in page.lower(), (
        "the unavailable branch dropped the clause naming what would have to be recorded")


def test_no_subject_of_this_file_is_read_from_the_working_tree():
    """THE RELAPSE GUARD: this file's own AST, rather than my having been careful.

    The defect is one line long and looks completely ordinary -- a `SITE / "data" / x.json`
    constant plus `.read_text()` -- which is why it survived here for weeks after the first door
    was fixed. The subjects come from the `*_REL` constants, so a feed added to the render payload
    is covered the day it is added. The scanner's own teeth are proved in
    `site/test_the_published_bytes_reader.py`.
    """
    refuse_working_tree_reads(__file__, (DOOR_REL, CAPS_REL, GROWTH_REL, DD_ARMS_REL))
