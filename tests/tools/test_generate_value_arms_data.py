"""`site/data/value_arms.json` must be able to say "we could not read it" and "it is worth nothing".

THE DEFECT THIS GUARDS. The feed exists to publish a comparison whose honest answer is currently
NEGATIVE -- the per-customer arm's advantage is the price level, and the choosing is worth
-£571.38 on the SETTLED-REALISED clock (restated 2026-08-28; the superseded settled-provisioned
reading of the same run was -£174.57, and both are published side by side because deleting the
flattering one would leave a reader unable to size what the clock repair moved). Note the
restatement went AGAINST the arm, which is the result and not a cue to touch it (R12).

Two failure modes would each destroy that reading while leaving a green, plausible,
fully-populated file behind:

  FAIL-OPEN ON THE POPULATION -- an unreadable or half-written artefact rendering as £0 rather
  than as an absence. "The selection leg is worth nothing" and "we could not read the file" are
  the two sentences this whole surface exists to keep apart, and a zero renders them identically.

  A CLAIM THAT ROTS -- "the supplier this site publishes IS the flat-rules baseline" is true today
  because the published run and the A/B's control arm are the same run. The site republishes every
  run. So the claim is recomputed from the published run's own `total_net_gbp` every time, and it
  must render as its own NEGATIVE the moment the two diverge.

R15 -- the mutations, each run and reverted:
  * make `_read` return `{}` instead of None on a malformed artefact -> the available=False tests
    red (the feed would publish an empty comparison).
  * default `_f` to 0.0 instead of None -> `test_a_missing_figure_is_absent_not_zero` reds.
  * widen SAME_SUPPLIER_TOLERANCE_GBP to 1e9 -> `test_a_divergent_published_run_is_reported_as_a
    _divergence` reds.
  * route the level arm by WHICH BLOCK it was found in rather than by the clock the block declares
    -> `test_a_split_on_the_superseded_clock_withholds_the_level_arm` reds (this is the mutation
    that would re-publish superseded figures under the realised heading the day the tool changed).
  * widen the split-vs-bridge agreement check to accept a clock-sized gap ->
    `test_a_split_that_disagrees_with_the_bridge_withholds_the_level_arm` reds.
  * report `stdev: 0.0` when no noise floor exists -> `test_a_missing_noise_floor_is_an_absent
    _error_bar_not_a_spread_of_zero` reds.
The null rungs -- the real artefacts, which must stay fully available with every figure present --
are `test_the_real_artefacts_publish_all_three_arms` and its siblings, and they stay green under
all five.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import generate_value_arms_data as gva

PROJECT = Path(__file__).resolve().parent.parent.parent
THREE_ARM = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm.json"
NOISE_FLOOR = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_noise_floor.json"
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"



@pytest.fixture
def dashboard_agreeing_with(monkeypatch, tmp_path):
    """Point the generator's dashboard at a figure of the test's choosing.

    WHY THIS EXISTS. `_is_the_published_supplier` now REFUSES when the run artefact it reads is not
    the figure the site publishes -- added 2026-08-28 after the check was shown to compare an A/B
    pass against its own output. Every test below that drives the match/divergence branches has to
    say which figure the site publishes, or it is exercising the refusal instead of the branch it
    names.
    """
    def _set(net):
        path = tmp_path / "dashboard.json"
        path.write_text(json.dumps({"portfolio": {"net_margin_gbp": net}}), encoding="utf-8")
        monkeypatch.setattr(gva, "DASHBOARD_PATH", path)
        return path
    return _set


def _load(path: Path) -> dict:
    if not path.is_file():
        pytest.fail("{} is missing -- this control's subject is UNAVAILABLE, and an unavailable "
                    "check is a FAILED check (R15)".format(path))
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def real() -> dict:
    return gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), _load(RUN_OUTPUT))


# ── the null rungs: the real artefacts, fully published ──────────────────────────────────────

def test_the_real_artefacts_publish_all_three_arms(real):
    assert real["available"], real.get("reason")
    for block in ("realised", "provisioned"):
        arms = real[block]["arms"]
        assert [a["key"] for a in arms] == ["control", "value", "level"], (
            "{} must publish all three arms in a fixed order -- a missing arm is what makes "
            "'the arm earned more' unanswerable".format(block))


def test_every_published_block_carries_its_clock(real):
    """R14: a financial figure without its clock is a defect, and this run HAS two that differ by
    £39,962.17. Publishing either without saying which would be the whole defect again."""
    clocks = {real["realised"]["clock"], real["provisioned"]["clock"]}
    assert clocks == {"settled-realised", "settled-provisioned"}
    for block in ("realised", "provisioned"):
        assert real[block]["clock_means"].strip(), (
            "{} names a clock a reader cannot interpret".format(block))


def test_the_level_arms_realised_net_is_published_on_the_clock_it_declares(real):
    """THE NULL RUNG THIS TEST USED TO BE THE OPPOSITE OF.

    Until the A/B was re-run on the repaired code (2026-08-28) the level arm's realised net was
    not recoverable, and this asserted its ABSENCE. The repaired run sums `total_net_gbp` from the
    mutated rows for every arm, so the figure now exists and the old assertion would have kept a
    number the site can publish off the page forever -- an absence that had quietly stopped being
    true. It is restated to the contract that actually holds, not deleted.

    The absence path is still what the two tests below exercise, so the routing rule keeps a way
    to fail: the figure is shown BECAUSE the split declares `settled-realised`, never because of
    which block it was found in.
    """
    level = [a for a in real["realised"]["arms"] if a["key"] == "level"][0]
    assert level["absent_reason"] is None, level["absent_reason"]
    assert level["net_gbp"] is not None, (
        "the level arm's realised net is recoverable from the repaired run and must be published")
    assert level["advantage_gbp"] is not None, (
        "a level arm with a net but no advantage cannot answer the question the panel is for")

    provisioned_level = [a for a in real["provisioned"]["arms"] if a["key"] == "level"][0]
    assert provisioned_level["net_gbp"] is not None, (
        "the level arm IS available on the provisioned clock -- absent there too would mean the "
        "split has no third arm at all")
    assert provisioned_level["net_gbp"] != level["net_gbp"], (
        "the two panels reported the SAME figure for the level arm, so one of them is not on the "
        "clock it names -- the whole defect this pair of panels exists to keep visible")


def test_a_split_on_the_superseded_clock_withholds_the_level_arm(real):
    """R15: the routing rule must be able to refuse. A split still on `settled-provisioned` is
    exactly the artefact this generator met before the repair, and re-stamping it as realised is
    the defect -- so it is withheld with its reason rather than shown."""
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"], clock="settled-provisioned")
    out = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))

    level = [a for a in out["realised"]["arms"] if a["key"] == "level"][0]
    assert level["net_gbp"] is None, (
        "a split declaring the SUPERSEDED clock was published under the realised heading")
    assert "settled-provisioned" in level["absent_reason"], level["absent_reason"]
    assert out["realised"]["split"]["available"] is False


def test_a_split_that_disagrees_with_the_bridge_withholds_the_level_arm(real):
    """The two realised reads of the arms they SHARE reach them by different code paths. A gap of
    clock size between them means one is on the other clock, and the third arm is not shown while
    the two it is measured against do not agree."""
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"],
                                     control_net_gbp=art["level_vs_selection"]["control_net_gbp"]
                                     + 39_962.17)
    out = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))

    level = [a for a in out["realised"]["arms"] if a["key"] == "level"][0]
    assert level["net_gbp"] is None, "the level arm was shown against two arms that disagree"
    assert "39,962.17" in level["absent_reason"], (
        "the disagreement is reported without its size: {}".format(level["absent_reason"]))


def test_the_selection_leg_and_its_error_bar_are_published_together(real):
    """The point estimate is never published without its measured spread.

    THE RELATIONSHIP BETWEEN THEM IS NO LONGER PINNED, AND THAT IS THE REPAIR. This test used to
    assert `stdev > |selection|` -- the state on the day it was written -- and the rendered
    sentence ("the point estimate sits inside that band") was a fixed string that assumed it. On
    2026-08-28 the estimate moved to -GBP 5,224 against a band of -3,705 to +5,076 and the
    assertion fired, which is the control doing its job. Pinning the new state instead would just
    re-arm the same trap, so what is checked now is that the feed KNOWS which case it is in and
    says the matching thing.

    THE SUBJECT WAS RESTATED ON 2026-08-29, NOT THE ASSERTION. It read `real["provisioned"]`,
    which is how the cross-clock pairing survived review twice: the test asked about the same
    wrong figure the generator did, so both agreed and neither was right.
    """
    sp, eb = real["realised"]["split"], real["error_bar"]
    assert sp["selection_gbp"] is not None
    assert eb["available"], "the point estimate is published with no measured spread"
    inside = eb["point_estimate_inside_the_measured_band"]
    assert inside is not None, (
        "the feed cannot say whether the estimate is inside the band its own spread was measured "
        "over -- an unknown relationship must not be published as a comfortable one")
    if inside:
        assert "sits inside that band" in eb["reading"]
    else:
        assert "OUTSIDE the band" in eb["reading"], (
            "the estimate has left the range its spread was measured over and the reading does "
            "not say so: {}".format(eb["reading"]))
        assert "not a bound on it" in eb["reading"]


def test_the_error_bar_bounds_the_FIGURE_THE_HEADLINE_STATES(real):
    """THE ERROR BAR AND THE FIGURE IT BOUNDS MUST BE ONE QUANTITY ON ONE CLOCK.

    THE DEFECT. Until 2026-08-29 `build` handed `_error_bar` the PROVISIONED selection leg while
    every row the spread is computed from is read out of `level_vs_selection`, which declares
    `settled-realised`. So the page divided a realised spread by a provisioned estimate and
    published the quotient as "about 6x the estimate itself", and answered "the point estimate
    sits inside that band" about a figure the headline does not state. The realised leg the
    headline DOES state was outside the same band. Two correct figures whose ratio is not a
    quantity, on the reassuring side.

    KEYED TO THE PROPERTY. This asserts a RECONCILIATION between two published fields -- the bar's
    declared subject against the split it must be the subject of -- and never that the subject is
    any particular number. It stays true at every future run, and it goes red for the defect
    rather than for a result.

    Fires on: restoring the provisioned point, dropping either provenance field, or pairing the
    bar with a figure from any block whose clock is not the spread's.
    """
    eb, split = real["error_bar"], real["realised"]["split"]
    assert eb["available"] and split["available"]

    assert eb["bounds_figure_gbp"] == split["selection_gbp"], (
        "the error bar is a bar on £{!r} while the headline states £{!r} -- a spread over a "
        "figure it was not measured on".format(eb["bounds_figure_gbp"], split["selection_gbp"]))
    assert eb["bounds_figure_clock"] == split["clock"] == "settled-realised", (
        "the bar declares clock {!r} against a split on {!r}".format(
            eb["bounds_figure_clock"], split["clock"]))
    # THE ONE FIGURE IT MUST NOT BE. Named explicitly because it is the figure the defect used,
    # it sits in the same payload under a near-identical key, and on this run the two differ by
    # £1,362 -- so an assertion that only checked "is a float" would have passed throughout.
    prov = real["provisioned"]["selection_gbp"]
    if abs(prov - split["selection_gbp"]) > gva.SAME_SUPPLIER_TOLERANCE_GBP:
        assert eb["bounds_figure_gbp"] != prov, (
            "the error bar is bounding the SUPERSEDED clock's selection leg (£{:,.2f}) -- the "
            "exact cross-clock pairing this control exists for".format(prov))
    # ...and the derived readings are the ones that pairing corrupts, so they are checked against
    # the subject rather than taken on trust.
    assert eb["point_estimate_inside_the_measured_band"] is (
        eb["min_gbp"] <= eb["bounds_figure_gbp"] <= eb["max_gbp"])
    assert eb["spread_to_point_estimate_ratio"] == pytest.approx(
        abs(eb["stdev_gbp"] / eb["bounds_figure_gbp"]))


def test_a_split_on_another_clock_leaves_the_bar_with_NOTHING_TO_PLACE(real):
    """The tri-state's third branch, which used to fall through the falsy edge.

    `point_estimate_inside_the_measured_band` is True/False/None, and None means "no figure on
    this spread's clock exists to place". The reading was a two-branch ternary, so None rendered
    as "the point estimate now sits OUTSIDE the band" -- an unknown published as a measurement,
    and in the fail-open direction. It must not reach for the provisioned figure either: a spread
    on one clock is not a bound on a figure from another, which is the whole subject here.

    Fires on: collapsing the three branches back to two, or filling the point from any other block.
    """
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"], clock="settled-provisioned")
    eb = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))["error_bar"]

    assert eb["available"], "the spread itself is still measured and must still be published"
    assert eb["bounds_figure_gbp"] is None and eb["bounds_figure_clock"] is None
    assert eb["point_estimate_inside_the_measured_band"] is None
    assert eb["spread_to_point_estimate_ratio"] is None, (
        "a ratio was published against a point estimate that does not exist on this clock")
    assert "no figure on this spread's own clock" in eb["reading"], eb["reading"]
    assert "OUTSIDE the band" not in eb["reading"], (
        "an UNKNOWN was published as the measured statement that the estimate left its band")
    assert eb["stdev_gbp"] is not None, (
        "the null rung: the spread must still be published as a size, or the assertions above "
        "would pass against a block that had simply gone unavailable")


def test_the_decision_count_reaches_the_feed(real):
    dec = real["decisions"]
    assert dec["available"]
    assert isinstance(dec["value_arm_priced"], int) and dec["value_arm_priced"] > 0
    assert dec["accounts_named_in_the_decision_sample"], (
        "the feed publishes a per-customer result without naming how few customers it covers")


# ── FAIL-OPEN: an unreadable or partial artefact must be an ABSENCE ──────────────────────────

@pytest.mark.parametrize("artefact", [None, {}, {"generated_at": "x"}])
def test_an_unreadable_artefact_is_unavailable_never_an_empty_comparison(artefact):
    out = gva.build(artefact, None, None)
    assert out["available"] is False
    assert out["reason"], "the feed reports unavailable without saying why"
    assert "realised" not in out and "provisioned" not in out, (
        "an unreadable artefact produced comparison blocks a reader would take as measured")


def test_a_missing_figure_is_absent_not_zero(real):
    """A string, a bool or a NaN where a figure belongs is a DEFECT, and must not render as 0."""
    assert gva._f(None) is None
    assert gva._f("113282.62") is None, "a stringified figure was accepted as a number"
    assert gva._f(True) is None, "a bool was accepted as a figure"
    assert gva._f(float("nan")) is None and gva._f(float("inf")) is None


def test_a_missing_noise_floor_is_an_absent_error_bar_not_a_spread_of_zero():
    """A spread of zero is the ONE value that would make an indistinguishable result read as a
    decisive one, so it is the one value the absent case must never produce."""
    out = gva.build(_load(THREE_ARM), None, _load(RUN_OUTPUT))
    eb = out["error_bar"]
    assert eb["available"] is False
    assert eb["reason"]
    assert "stdev_gbp" not in eb, "an absent noise floor still published a standard deviation"


def test_a_one_seed_noise_floor_is_not_a_spread():
    out = gva.build(_load(THREE_ARM), {"selection_gbp_spread": {"n": 1, "stdev": 0.0,
                                                               "min": -174.5, "max": -174.5}},
                    _load(RUN_OUTPUT))
    assert out["error_bar"]["available"] is False, (
        "a single seed was published as a measured spread of zero")


# ── THE CLAIM THAT COULD ROT: is the published supplier the baseline arm? ────────────────────

def test_the_published_supplier_claim_is_HONEST_whichever_state_the_tree_is_in(real):
    """The claim is checked and states what it can support — never an unstated pass.

    THIS USED TO PIN `same_supplier is True` as LIVE STATE, and that is the shape the day's other
    controls kept being caught by: it passes on whatever the working tree happens to hold and goes
    red when the tree becomes MORE honest. On 2026-08-28 the check gained a refusal for the case
    where the run artefact is not the figure the site publishes, and this test reddened on it.
    What it checks now is that the feed says the matching thing in each of the three cases.
    """
    pub = real["realised"]["is_the_published_supplier"]
    if pub["checked"] and pub["same_supplier"]:
        assert "IS the baseline" in pub["statement"]
    elif pub["checked"]:
        assert "is NOT the baseline arm's" in pub["statement"]
    else:
        assert "IS the baseline" not in pub["statement"], (
            "an unverifiable relationship was rendered as agreement -- fail-open on the check")
        assert pub["statement"].strip(), "the check withheld the claim and said nothing about why"


def test_a_divergent_published_run_is_reported_as_a_divergence(real, dashboard_agreeing_with):
    """THE LOAD-BEARING NULL. The day the site publishes a different run, the claim must invert
    itself and name both figures -- not quietly go on asserting an identity that has lapsed."""
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    dashboard_agreeing_with(control + 40_000.0)
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR),
                    {"total_net_gbp": control + 40_000.0})
    pub = out["realised"]["is_the_published_supplier"]

    assert pub["same_supplier"] is False
    assert "is NOT the baseline arm's" in pub["statement"]
    assert "40,000" in pub["statement"], "the divergence is reported without its size"
    assert "IS the baseline" not in pub["statement"]
    assert not out["headline"].startswith("The comparison below is against"), (
        "the headline went on claiming the published supplier is the baseline after they diverged")
    dashboard_agreeing_with(control)
    assert gva.build(_load(THREE_ARM), _load(NOISE_FLOOR),
                     {"total_net_gbp": control})["headline"].startswith(
        "The comparison below is against"), (
        "the null rung: while the two DO match, the headline must make the claim -- otherwise the "
        "assertion above passes on a headline that never carries it")


def test_an_unreadable_published_run_claims_nothing_either_way(real):
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), None)
    pub = out["realised"]["is_the_published_supplier"]
    assert pub["checked"] is False and pub["same_supplier"] is None
    assert "IS the baseline" not in pub["statement"], (
        "an unread run was treated as agreement -- fail-open on the check itself")


def test_a_penny_of_divergence_is_still_the_same_supplier(real, dashboard_agreeing_with):
    """The null on the OTHER side: both figures are pounds summed from settlement records, so
    sub-penny float noise must not be reported as two different suppliers."""
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    dashboard_agreeing_with(control + 0.004)
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), {"total_net_gbp": control + 0.004})
    assert out["realised"]["is_the_published_supplier"]["same_supplier"] is True


def test_a_run_artefact_that_is_not_the_published_figure_WITHHOLDS_the_claim(
        real, dashboard_agreeing_with):
    """THE INDEPENDENCE REPAIR (2026-08-28). `run_output_latest.json` is written by the same entry
    point the A/B calls once per arm, so an A/B pass can make this check compare its own output
    against itself. And on that day the figure the SITE published was 153,244.79 while the run
    artefact read 159,423.50 -- different runs, so the check's subject was not the published
    figure at all.

    Fires on: answering the claim from whichever file is nearer, in either direction.
    """
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    dashboard_agreeing_with(control - 6_178.71)      # what the site publishes
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), {"total_net_gbp": control})
    pub = out["realised"]["is_the_published_supplier"]
    assert pub["checked"] is False and pub["same_supplier"] is None
    assert "cannot say whether the baseline arm is the supplier the site publishes" in pub["statement"]
    assert "6,178.71" in pub["statement"], "the mismatch is reported without its size"
    assert "IS the baseline" not in pub["statement"]
    assert not out["headline"].startswith("The comparison below is against"), (
        "the headline claims the published supplier is the baseline while the check withheld it")


def test_an_unreadable_dashboard_leaves_the_original_comparison_alone(
        real, monkeypatch, tmp_path):
    """The refusal must only fire on a mismatch it can PROVE. A missing dashboard is not evidence
    of one, and inventing a mismatch from an unreadable file would be the opposite failure —
    withholding a true claim.
    """
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    monkeypatch.setattr(gva, "DASHBOARD_PATH", tmp_path / "nope.json")
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), {"total_net_gbp": control})
    assert out["realised"]["is_the_published_supplier"]["same_supplier"] is True


# ── the R12 wall, carried in the feed rather than only in a design note ──────────────────────

def test_the_feed_says_a_negative_result_is_not_a_cue_to_tune(real):
    assert real["provisional"] is True
    assert "not a cue to tune" in real["not_a_target"], (
        "the feed publishes a losing arm with no statement that losing is a permitted answer")


def test_the_generator_rides_the_publish_cycle():
    """R11 no-orphan-transition: a generated surface that does not ride the regen cycle freezes
    against its source, and this one exists precisely to track it."""
    wiring = (PROJECT / "background" / "process_run_complete.py").read_text(encoding="utf-8")
    assert "from tools.generate_value_arms_data import generate" in wiring, (
        "value_arms.json is generated by nothing on the publish path")


# ── the headline must be able to say the arm LOST ────────────────────────────────────────────

def _split_with(advantage, selection):
    """A three-arm artefact whose split says exactly what these two numbers say."""
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"],
                                     value_advantage_gbp=advantage,
                                     selection_gbp=selection)
    return gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))


def test_the_headline_says_LESS_when_the_arm_earned_less():
    """THE DEFECT. Both branches of the headline opened with "earned more than flat rules" as a
    CONSTANT — true of the run they were written against, and FALSE on 2026-08-28T12:37Z, where
    the per-customer arm earned £4,724 LESS while the published sentence said it earned more.

    The selection direction had already been made derived for exactly this reason; the
    arm-vs-control direction was left behind. Fires on: re-hardcoding either direction.
    """
    out = _split_with(-4724.01, -9626.92)
    assert "£4,724 LESS than flat rules" in out["headline"], out["headline"]
    assert "earned more than flat rules" not in out["headline"]


def test_the_headline_says_MORE_when_the_arm_earned_more():
    """The other direction, so this is a control and not a machine for printing bad news."""
    out = _split_with(4668.41, 571.38)
    assert "£4,668 MORE than flat rules" in out["headline"], out["headline"]
    assert "LESS than flat rules" not in out["headline"]


def test_an_unreported_advantage_is_its_own_sentence_and_never_the_winning_one():
    """FAIL-OPEN killer. A run that cannot supply the arm's own advantage must not default to the
    flattering clause — defaulting to "earned more" is the whole defect in miniature."""
    out = _split_with(None, -9626.92)
    assert "did not report what the per-customer decision engine earned" in out["headline"]
    assert "MORE than flat rules" not in out["headline"]
    assert "LESS than flat rules" not in out["headline"]


def test_the_headline_carries_the_coverage_bound():
    """The bound belongs in the same breath as the numbers. A reader who meets the money first and
    the 2.07% three paragraphs later has already formed the impression.

    Fires on: dropping the clause, or computing a share the funnel does not support.
    """
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), _load(RUN_OUTPUT))
    funnel = (_load(THREE_ARM)["renewal_funnel"]["value_arm"])
    assert "{:,} renewals the world offered".format(funnel["renewals_the_world_offered"]) in \
        out["headline"]
    assert "{:.2f}%".format(funnel["priced_share_of_renewals_offered"] * 100) in out["headline"]


def test_a_run_with_no_funnel_gets_no_coverage_clause_rather_than_a_guessed_one():
    """An invented coverage sentence would be worse than none — it is the sentence a reader would
    trust most. Fires on: falling back to the account count, or to a hard-coded share."""
    art = _load(THREE_ARM)
    art.pop("renewal_funnel", None)
    out = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))
    assert "renewals the world offered" not in out["headline"]
    assert "Read all of it against its size" not in out["headline"]


# ── the household side: the other column of the same comparison ──────────────────────────────
#
# THE DEFECT THESE SERVE. `company/analytics/household_value_share.py` computed what a household
# kept from the day it landed and reached NO published surface: the only consumer in the tree was
# `tools/run_price_ladder.py`, so every figure a reader met was one-sided. The mission's own
# sentence -- value is created and THEN shared, so every decision has two sides -- is a claim the
# site could not support in either direction while only our column existed. Charging a household
# the cap looks like a win on a one-sided page and reads as an obvious transfer the moment both
# columns are visible.

def _with_household(**per_arm) -> dict:
    """A three-arm artefact carrying exactly the household blocks named."""
    art = _load(THREE_ARM)
    art["household_side"] = dict(per_arm)
    return gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))


def _side(saving=1234.5, **over):
    block = {"available": True, "basis": "settled clock; counterfactual = the published cap",
             "household_saving_gbp": saving,
             "household_saving_pct_of_counterfactual": 3.5,
             "paid_gbp": 40000.0, "counterfactual_gbp": 41234.5,
             "household_share_of_the_split_pct": 40.0, "coverage_pct": 88.0,
             "customer_years": 210}
    block.update(over)
    return block


def test_the_household_side_is_published_beside_the_arms_it_belongs_to():
    """Both sides of one comparison, keyed so they can only land on the SAME row.

    Fires on: dropping the block, or keying it in a way the surface cannot join to the arms.
    """
    out = _with_household(control_arm=_side(1000.0), value_arm=_side(500.0),
                          level_arm=_side(250.0))
    hh = out["household"]
    assert hh["available"], hh.get("reason")
    assert [a["key"] for a in hh["arms"]] == [a["key"] for a in out["realised"]["arms"]], (
        "the household arms are not keyed like the company arms, so no surface can put the two "
        "sides of one arm on one row -- which is the entire claim being made")
    assert [a["household_saving_gbp"] for a in hh["arms"]] == [1000.0, 500.0, 250.0]
    assert hh["clock"] and hh["basis"], "a published financial figure with no clock or basis (R14)"


def test_a_run_without_a_household_side_publishes_an_absence_and_never_a_zero():
    """FAIL-OPEN killer, and the direction matters more than usual here.

    A household saving of £0 is EXACTLY what "we charged them the default tariff and shared
    nothing" produces -- the worst answer this figure can return. A generator that filled a
    missing block with zero would publish that answer as though it had been measured. The absence
    must be an absence, and it must name the run that fixes it.
    """
    art = _load(THREE_ARM)
    art.pop("household_side", None)
    out = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))
    hh = out["household"]
    assert hh["available"] is False
    assert "run_value_cycle_ab" in hh["reason"], (
        "the absence does not name the run that would fill it, so it reads as a permanent gap")
    # `isinstance(False, int)` is True in Python and `available: False` is the very flag that
    # says the figure is absent -- so bools are excluded here, or this assertion fires on its own
    # subject working correctly.
    numbers = [v for v in hh.values()
               if isinstance(v, (int, float)) and not isinstance(v, bool)]
    assert not any(v == 0 for v in numbers), "an unmeasured household side published a zero"
    assert "arms" not in hh, (
        "an absent household side published an arm list, which a surface would render as a "
        "column of blanks rather than as the absence it is")


def test_an_arm_the_run_did_not_score_is_absent_rather_than_borrowed_from_another():
    """No arm may be filled from another arm's figure. Fires on: falling back to the portfolio,
    to the control, or to the first available block."""
    out = _with_household(control_arm=_side(1000.0), value_arm=_side(500.0),
                          level_arm={"available": False, "reason": "this arm did not run"})
    arms = {a["key"]: a for a in out["household"]["arms"]}
    assert arms["level"]["household_saving_gbp"] is None
    assert arms["level"]["absent_reason"] == "this arm did not run"
    assert arms["control"]["household_saving_gbp"] == 1000.0


def test_a_household_side_present_but_empty_is_withheld_rather_than_part_published():
    out = _with_household(control_arm={"available": False, "reason": "no records"},
                          value_arm={"available": False, "reason": "no records"})
    assert out["household"]["available"] is False
    assert "partial column" in out["household"]["reason"]


def test_the_household_figure_states_the_two_currencies_it_does_not_reach():
    """The mission names three currencies and this figure reaches one. Carbon is designed and
    never instrumented; time does not exist anywhere in the project. A number published without
    that is a number a reader will take for the whole of "value shared".

    Asserted on the ABSENT branch too: the exclusions are true whether or not the run scored.
    """
    for out in (_with_household(control_arm=_side()), gva.build(
            {k: v for k, v in _load(THREE_ARM).items() if k != "household_side"},
            _load(NOISE_FLOOR), _load(RUN_OUTPUT))):
        states = {e["currency"]: e["state"] for e in out["household"]["excludes"]}
        assert states["money"] == "measured"
        assert states["carbon"] == "designed, never measured"
        assert states["time"] == "absent"
        assert "not value CREATED" in out["household"]["what_this_is_not"]
        assert "not a target" in out["household"]["not_a_target"].lower(), (
            "the household figure is published with no R12 statement on the surface that "
            "publishes it -- which is where it becomes temptingly steerable")


# ── A DIRECTION IS EARNED AGAINST THE FLOOR, NEVER STATED BY DEFAULT ─────────────────────────
#
# THE DEFECT. The headline composed a direction unconditionally. Given any contrast it said which
# way it went, while the error bar three paragraphs below said -- correctly -- that the same figure
# moves further than that across three re-runs which changed nothing but a dice roll. Two true
# blocks making one false page. On 2026-08-29 all three of the run's contrasts were inside their
# own seed spread and the page still named a winner.
#
# WHAT THESE TWO TESTS PIN, AND WHAT THEY DELIBERATELY DO NOT. They pin the PROPERTY -- direction
# iff the contrast clears the spread the same contrast shows across seeds -- by driving the SAME
# two figures through two different floors. A control pinned to today's "we cannot tell" would go
# red the day the book grew enough to earn a sign, which is exactly backwards and is the failure
# this project keeps repeating.

#: Every sentence on this page that names a WINNER. If a clause is added that states a direction,
#: it belongs here, or the inside-the-floor test stops covering it.
_DIRECTIONAL_CLAIMS = (
    "MORE than flat rules",
    "LESS than flat rules",
    "the per-customer choosing is worth less than nothing",
    "the choosing itself carried part of it",
)


def _floor_with_spread(stdev: float) -> dict:
    """A noise floor whose three seeds give EXACTLY `stdev` on all three contrasts.

    The values -s, 0, +s have a sample standard deviation of exactly s, so the bound under test is
    the number written at the call site and not one arrived at by arithmetic the reader of this
    test cannot see. The published spread block agrees with the rows by construction -- disagreeing
    with them is its own test below.
    """
    values = (-stdev, 0.0, stdev)
    return {
        # Later than any real three-arm run, so these tests exercise the direction gate and never
        # trip the separate staleness caveat.
        "generated_at": "2999-01-01T00:00:00Z",
        "seeds": [{"seed": 11111 + i, "value_advantage_gbp": v, "level_advantage_gbp": v,
                   "selection_gbp": v} for i, v in enumerate(values)],
        "selection_gbp_spread": {"n": 3, "stdev": stdev, "mean": 0.0,
                                 "min": -stdev, "max": stdev},
    }


def _headline_with(advantage, selection, stdev):
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"],
                                     value_advantage_gbp=advantage, selection_gbp=selection)
    return gva.build(art, _floor_with_spread(stdev), _load(RUN_OUTPUT))["headline"]


def test_a_contrast_inside_its_seed_spread_carries_no_direction():
    """£600 and £1,800 against a ±£5,000 floor: the page states both SIZES and the BOUND, and
    names no winner in either comparison.

    Fires on: restoring an unconditional direction, dropping the bound from the sentence, or
    reporting the refusal without the size a reader needs to judge it.
    """
    headline = _headline_with(advantage=600.0, selection=1800.0, stdev=5000.0)

    for claim in _DIRECTIONAL_CLAIMS:
        assert claim not in headline, (
            "the page named a winner on a contrast inside its own error bar ({!r}): {}".format(
                claim, headline))
    assert "CANNOT RESOLVE" in headline, headline
    assert "±£5,000" in headline, "the refusal was published without the bound that earned it"
    assert "£600" in headline and "£1,800" in headline, (
        "the refusal withheld the SIZES too -- 'we cannot tell' with no figure is less than the "
        "page had before")
    assert "larger SETTLED BOOK" in headline, (
        "the page says it cannot resolve the sign and does not say what would")


def test_a_contrast_outside_its_seed_spread_gets_its_direction_back():
    """THE LEG THAT STOPS THIS BEING A MACHINE FOR PRINTING "we cannot tell".

    The SAME two figures as the test above, against a floor ten times smaller. Nothing else
    differs, so a gate that has quietly become unconditional fails here and only here.
    """
    headline = _headline_with(advantage=600.0, selection=1800.0, stdev=100.0)

    assert "£600 MORE than flat rules" in headline, headline
    assert "the choosing itself carried part of it" in headline, headline
    assert "CANNOT RESOLVE" not in headline, (
        "a contrast six times its own seed spread was still refused a direction")
    assert "larger SETTLED BOOK" not in headline, (
        "a resolved contrast was published with the apology owed to an unresolved one")


def test_a_contrast_exactly_equal_to_its_spread_is_not_resolved():
    """The fail-CLOSED direction of the strict inequality. A mutation that made this `>=` would
    licence a direction on a contrast the floor exactly covers, and 1e-16 of daylight is not
    evidence (R15 -- the strict-inequality shape)."""
    headline = _headline_with(advantage=1000.0, selection=1000.0, stdev=1000.0)
    for claim in _DIRECTIONAL_CLAIMS:
        assert claim not in headline, headline


def test_a_floor_that_cannot_reproduce_its_own_published_spread_bounds_nothing():
    """RECONCILIATION, and it withholds ALL THREE bounds rather than the one that failed.

    This feed derives two of the three spreads from seed rows nobody else reads. The only check
    available on that derivation is the one contrast the producer publishes a spread for -- so if
    the rows and that figure disagree, this file is not reading the rows the spread was measured
    over and none of its three readings can be trusted. Fires on: trusting the rows, or narrowing
    the refusal to the selection leg.
    """
    floor = _floor_with_spread(1000.0)
    floor["selection_gbp_spread"] = dict(floor["selection_gbp_spread"], stdev=9999.0)
    out = gva.build(_load(THREE_ARM), floor, _load(RUN_OUTPUT))

    bounds = out["contrast_bounds"]
    assert bounds["available"] is False
    assert "contrasts" not in bounds, "a withheld bound still published the figures it withheld"
    assert "9,999" in bounds["reason"] and "1,000" in bounds["reason"], (
        "the refusal names neither figure it refused over: {}".format(bounds["reason"]))
    for claim in _DIRECTIONAL_CLAIMS:
        assert claim not in out["headline"], (
            "an unbounded contrast was published with a direction anyway: {}".format(
                out["headline"]))


def test_a_share_of_an_advantage_inside_its_own_noise_is_not_published():
    """Before dividing two numbers, say what each counts. `level_share_of_advantage` divides by
    the arm's own advantage, so a denominator inside its seed spread makes the share a rounding
    error dressed as a percentage -- -199% off a £607 denominator on the live run."""
    assert "accounts for" not in _headline_with(advantage=600.0, selection=1800.0, stdev=5000.0)
    assert "accounts for" in _headline_with(advantage=600.0, selection=1800.0, stdev=100.0), (
        "the null rung: while the denominator DOES clear its floor the share must be published, "
        "otherwise the assertion above passes against a headline that never carries it")


def test_the_superseded_clock_never_borrows_the_realised_floor():
    """The floor's seed contrasts are all on the settled-realised clock. A run whose split is not
    on that clock falls back to the provisioned panel, and it must get NO bound rather than one
    measured somewhere else -- the clock-mixing defect, committed where it is hardest to see."""
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"], clock="settled-provisioned")
    headline = gva.build(art, _floor_with_spread(100.0), _load(RUN_OUTPUT))["headline"]

    assert "superseded clock" in headline, headline
    assert "±£100" not in headline, "a provisioned figure was bounded by a realised spread"
    for claim in _DIRECTIONAL_CLAIMS:
        assert claim not in headline, (
            "an unbounded superseded figure was published with a direction: {}".format(headline))


def test_the_withdrawn_sentence_is_kept_beside_the_reading_that_replaced_it(real):
    """A correction a reader cannot see is one they cannot check. The page's claim on anyone's
    trust is that it publishes the unflattering direction, and that is worth nothing if it can
    also un-publish one silently."""
    withdrawn = real["withdrawn_claim"]
    assert "worth less than nothing" in withdrawn["the_words"], (
        "the withdrawn claim is recorded without the words that were published")
    assert withdrawn["the_words"] not in real["headline"], (
        "the sentence recorded as withdrawn is still the sentence being published")
    assert "withdrawn, not reversed" in withdrawn["note"], (
        "the note lets a reader take the withdrawal for the opposite claim")
