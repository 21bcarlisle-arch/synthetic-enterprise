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
import re
from pathlib import Path

import pytest

from tools import generate_value_arms_data as gva

PROJECT = Path(__file__).resolve().parent.parent.parent
THREE_ARM = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm.json"
#: THE RUN THAT STILL HAS THE STRUCTURAL PROPERTY, pinned by its DATED name (2026-08-31).
#: `THREE_ARM` is the canonical path each new run is PROMOTED to, so a test that asserts a
#: particular run's figures through it is keyed to today's answer and reds the day the world
#: improves. That is what happened when the 2026-08-31 run landed: the standard-variable product
#: shipped, the arm went from pricing 20 renewals on 10 roster accounts to 120 on 65 -- 25 of them
#: drawn households -- and six controls asserting "the method has NEVER priced a customer the
#: company won" went red for the single reason that it had. The claims were true of the run they
#: were written against and that run is still on disk, so they cite it directly. Tests of a
#: PROPERTY keep reading `THREE_ARM`; tests of a RUN read this.
THREE_ARM_20260829 = (
    PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm_20260829.json")
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


@pytest.fixture
def real_20260829() -> dict:
    """The page as built from the run whose BELIEF RANKED BACKWARDS -- see `THREE_ARM_20260829`.

    The reversal tables below are descriptions of that run and stay pinned to it. The 2026-08-31
    run ranks the right way round (AUC 0.13 -> 0.655), so asserting the reversal through the
    canonical path would be a control asserting the model stays bad.
    """
    return gva.build(_load(THREE_ARM_20260829), _load(NOISE_FLOOR), _load(RUN_OUTPUT))


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
    # PRESENCE, NOT POSITION, AND BOTH RUNGS MOVED TOGETHER (2026-09-03). Both assertions were
    # `startswith`, which was a correct proxy for presence only while nothing could precede this
    # clause. `_world_clause` now can: a run measured in a superseded world is prefixed "READ THIS
    # AS HISTORY" ahead of every other clause, deliberately, because a reader who meets the figure
    # first has already taken it as current.
    #
    # THE RUNG THAT MATTERED IS THE NEGATIVE ONE, and it is why this is not a one-line repair of
    # the assertion that went red. `not headline.startswith(...)` would have gone on passing --
    # trivially, on ANY headline carrying a world prefix, including one that went on to claim the
    # published supplier is the baseline three clauses later. The rung that reddened was the
    # honest one; the rung that stayed green was the one that had quietly become a tautology.
    # Repairing only the red one is how a control survives a composition change with its teeth
    # removed.
    assert "The comparison below is against" not in out["headline"], (
        "the headline went on claiming the published supplier is the baseline after they diverged")
    dashboard_agreeing_with(control)
    assert "The comparison below is against" in gva.build(
        _load(THREE_ARM), _load(NOISE_FLOOR), {"total_net_gbp": control})["headline"], (
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
    """A three-arm artefact whose split says exactly what these two numbers say.

    THE FLOOR IS CURRENT BY CONSTRUCTION (2026-08-31). These tests are about which DIRECTION the
    headline states, which is gated on the contrast clearing a bound -- so they need a floor that
    is not older than the run, or they measure the staleness refusal instead of the direction
    they were written for. `_floor_with_spread` is stamped far in the future for exactly this
    reason; the spread is small enough that both directions still clear it.
    """
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"],
                                     value_advantage_gbp=advantage,
                                     selection_gbp=selection)
    return gva.build(art, _floor_with_spread(100.0), _load(RUN_OUTPUT))


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
    # A REFUSAL MUST SAY SOMETHING ABOUT THE REMEDY -- but WHICH remedy is evidence, not wording.
    # This pinned the words "larger SETTLED BOOK" until 2026-08-29, which made a page that had
    # measured the remedy to be FALSE unable to say so without going red: a control keyed to
    # today's answer, red exactly when the page became more honest. `_headline_with` reads no
    # decomposition, so what it must carry is the unmeasured branch.
    assert "has not been established" in headline and "More seeds would not" in headline, (
        "the page says it cannot resolve the sign and says nothing at all about what would -- "
        "'we cannot tell' with no remedy reads as a dead end: {}".format(headline))


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
    also un-publish one silently.

    OVER THE WHOLE RECORD, NOT THE NEWEST ENTRY (2026-08-29). This read a single dict until the
    page withdrew a SECOND sentence, and a single dict is the shape in which the second correction
    silently overwrites the first -- leaving a page that claims to keep its record while keeping
    one entry of it. Asserting the property over every entry is what makes a third withdrawal
    unable to erase these two.
    """
    withdrawn = real["withdrawn_claim"]
    every = [withdrawn] + list(withdrawn.get("also_withdrawn") or [])
    assert len(every) == withdrawn["withdrawals"] >= 2, (
        "the block does not carry every withdrawal it counts")
    assert any("worth less than nothing" in claim["the_words"] for claim in every), (
        "the withdrawn direction is recorded without the words that were published")
    assert any("larger SETTLED BOOK" in claim["the_words"] for claim in every), (
        "the withdrawn REMEDY is not on the record -- the page dropped a sentence rather than "
        "withdrawing it, which is the un-publishing this test exists to stop")
    for claim in every:
        assert claim["the_words"] not in real["headline"], (
            "a sentence recorded as withdrawn is still the sentence being published: {}"
            .format(claim["the_words"]))
        assert "WITHDRAWN" in claim["note"] and claim["note"] in withdrawn["note"], (
            "an earlier withdrawal is in the feed but not in the note the page renders, so a "
            "reader sees a page that corrected itself once: {}".format(claim["withdrawn_on"]))
    assert "withdrawn, not reversed" in withdrawn["note"], (
        "the note lets a reader take the withdrawal for the opposite claim")


# ── the remedy sentence: keyed to the decomposition, never to today's wording ────────────────

def _decomposition(priced_share: float, resolvable: bool, decisive: bool = True) -> dict:
    """A floor decomposition saying which half of the spread the priced households own.

    The fields are the ones `run_value_cycle_ab.decompose_floor` publishes, and the two the remedy
    turns on are set INDEPENDENTLY here on purpose: a composer that derived one from the other
    would pass a fixture that varied them together and fail on the real artefact.

    THE BOOK IS READ OFF THE CANONICAL RUN, NOT HARD-CODED (2026-08-31). These tests are about the
    remedy's LOGIC, not about which run happens to be canonical, so the fixture declares itself
    measured on whatever book is on disk. Hard-coding `priced_decisions: 20` made every one of
    them red the moment a new run was promoted -- a control keyed to today's answer rather than to
    its property. The same-book refusal is proved instead by
    `test_a_remedy_measured_on_another_book_is_refused_rather_than_restated`, which sets the two
    books apart ON PURPOSE.
    """
    priced, offered = gva._three_arm_book(_load(THREE_ARM))
    return {
        "available": True, "seeds": 3,
        "priced_share_of_variance": priced_share,
        "share_at_which_a_bigger_book_could_resolve_it": 0.504,
        "share_is_decisive": decisive,
        "larger_settled_book_would_resolve_it": resolvable,
        "priced_decisions_needed": 54 if resolvable else None,
        "priced_decisions": priced,
        "renewals_offered": offered,
        "irreducible_sd_gbp": 1153.0 if resolvable else 2306.0,
        "contrast_gbp": 1815.79,
        "undecomposed_sd_gbp": 2577.80,
        # THE QUANTITY THE SPLIT IS OF, declared because a well-formed artefact declares it. The
        # real 2026-08-30 artefact does NOT, which is the defect
        # `test_a_remedy_that_splits_another_quantity_is_refused_rather_than_restated` exists for;
        # this fixture is the well-formed case so the OTHER controls here stay about their own
        # property instead of all reddening on a missing declaration.
        "contrast": gva.PAGE_FIGURE_CONTRAST,
    }


def _withheld_headline(decomposition):
    """A headline whose contrast is INSIDE its own floor -- the only state that names a remedy."""
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"], selection_gbp=1815.79)
    return gva.build(art, _floor_with_spread(2577.80), _load(RUN_OUTPUT), decomposition)["headline"]


def test_the_remedy_clause_follows_the_decomposition_not_the_wording():
    """THE DEFECT: the page named a remedy -- "a larger SETTLED BOOK" -- beside its refusal to
    state a direction, one day after withdrawing a different sentence for asserting more than its
    evidence carried. The remedy was the same defect one clause over: the floor it qualifies
    re-draws price sensitivity for ~2,050 households while the arm priced 20 renewals, so the
    spread has two sources with OPPOSITE remedies and nobody had separated them.

    KEYED TO THE PROPERTY. This does not pin the sentence -- a control pinned to today's wording
    goes red when the page becomes more honest, which is this project's most repeated failure. It
    pins that the book-size clause appears when, and only when, a MEASURED split says the priced
    households' half is the one that dominates.

    R15 -- the mutations, each run and reverted:
      * restore `WHAT_WOULD_RESOLVE_IT` as an unconditional constant -> the `cannot` and the
        `unmeasured` legs red (this is the defect as it shipped).
      * treat a missing decomposition as the resolvable branch -> the `unmeasured` leg reds.
      * key the clause on `priced_share_of_variance` alone, ignoring `share_is_decisive` -> the
        `undecided` leg reds.
    The null rung is `dominates`, which must keep the clause: a control that only ever demands
    the clause be ABSENT is satisfied by deleting it.
    """
    dominates = _withheld_headline(_decomposition(0.85, resolvable=True))
    assert "larger SETTLED BOOK" in dominates, (
        "the null rung: with the priced households' own draw measured as the dominant half, the "
        "book-size remedy is TRUE and withholding it would leave the refusal a dead end: {}"
        .format(dominates))
    assert "54 priced renewals" in dominates, (
        "the remedy was named without its price, which is the half a reader needs to act on it")

    cannot = _withheld_headline(_decomposition(0.20, resolvable=False))
    assert "larger SETTLED BOOK" not in cannot, (
        "the page named a book-size remedy against a split saying the rest of the book's cascade "
        "alone is wider than the contrast: {}".format(cannot))
    assert "cannot be resolved at any book" in cannot, (
        "a finding about the INSTRUMENT was measured and left off the surface (R12)")

    unmeasured = _withheld_headline(None)
    assert "larger SETTLED BOOK" not in unmeasured, (
        "with no decomposition read at all the page asserted the remedy anyway -- the exact "
        "sentence withdrawn on 2026-08-29: {}".format(unmeasured))
    assert "has not been established" in unmeasured, (
        "an unmeasured remedy must be published as unmeasured, not silently dropped: a reader "
        "who sees neither cannot tell the question was asked")

    undecided = _withheld_headline(_decomposition(0.85, resolvable=True, decisive=False))
    assert "larger SETTLED BOOK" not in undecided, (
        "a split too close to its own threshold to call was rounded into a remedy: {}"
        .format(undecided))

    # AND THE ARITHMETIC HALF IS UNCONDITIONAL, because it needs no evidence: more seeds estimate
    # this spread again whatever the split is. A repair that made the whole remedy conditional
    # would drop the one clause that was always true.
    for name, headline in (("dominates", dominates), ("cannot", cannot),
                           ("unmeasured", unmeasured), ("undecided", undecided)):
        assert "More seeds would not resolve it" in headline, (
            "the {} branch dropped the half of the remedy that is arithmetic".format(name))


def test_a_remedy_measured_on_another_book_is_refused_rather_than_restated():
    """THE DEFECT, and it shipped on 2026-08-31. The three-arm run was re-taken after the
    standard-variable product landed and the priced count went 20 -> 120, but the floor
    decomposition was not re-run. `_staleness_caveat` had been built for exactly this on the noise
    floor and the decomposition never got it -- it carries no `generated_at` and no
    `producing_commit`, so nothing could notice. The page then published both books at once:
    `decisions.value_arm_priced` read 120 while the headline, three sentences later, said "about
    27 priced renewals against this book's 20" and "all 10 accounts the arm priced are the founding
    roster ... The lever is a PRODUCT, not a size". The product had SHIPPED and the lever had
    WORKED, and the page went on naming its absence as the blocker, in the flattering-to-nobody
    direction but wrong either way.

    KEYED TO THE PROPERTY -- whether the two books are the SAME -- and not to 20, or 120, or any
    count. Re-running the decomposition on the current book clears it with no edit here, and the
    next world change that moves the counts re-arms it. A control pinned to today's numbers goes
    red when the page becomes more honest, which is this project's most repeated failure.

    R15 -- the mutations, each run and reverted:
      * return `None` unconditionally from `_decomposition_is_the_same_book` (the defect as it
        shipped) -> the `different` leg reds, the remedy comes back on the wrong book.
      * compare only `priced_decisions` and ignore `renewals_offered` -> the `same_count_different_
        book` leg reds.
      * treat missing counts as agreement (`if any(... ) : return None`) -> the `no_counts` leg
        reds, which is the FAIL-SILENT half.
    The null rung is `same`, which must KEEP the remedy: a control that only ever demands the
    remedy be absent is satisfied by deleting the remedy.
    """
    priced, offered = gva._three_arm_book(_load(THREE_ARM))

    # THE NULL RUNG. A decomposition measured on this very book must still price the remedy --
    # otherwise this control is satisfied by a page that never states one.
    same = _withheld_headline(_decomposition(0.85, resolvable=True))
    assert "larger SETTLED BOOK" in same, (
        "the null rung: a decomposition measured on the published book was refused anyway, so "
        "this control would be satisfied by deleting the remedy entirely: {}".format(same))
    assert "DIFFERENT BOOK" not in same, (
        "a decomposition measured on the published book was accused of being from another: {}"
        .format(same))

    # A DIFFERENT BOOK, which is the state that shipped.
    different = _withheld_headline(
        dict(_decomposition(0.85, resolvable=True),
             priced_decisions=priced - 100, renewals_offered=offered - 584))
    assert "larger SETTLED BOOK" not in different, (
        "a remedy priced on a book the page no longer publishes was restated as though it "
        "described this one -- the defect as it shipped: {}".format(different))
    assert "DIFFERENT BOOK" in different and "has not been established" in different, (
        "the refusal must NAME its reason and leave the remedy explicitly unestablished; a "
        "silently dropped remedy reads as a question nobody asked: {}".format(different))
    assert str(priced) in different and str(priced - 100) in different, (
        "the refusal states neither book, so a reader cannot check the very comparison it "
        "refuses on: {}".format(different))

    # THE SAME PRICED COUNT ON A DIFFERENT-SIZED BOOK. Both counts carry the identity, because a
    # remedy denominated in priced decisions is still the wrong remedy if the book around them
    # changed -- the cascade half of the floor is what the second count tracks.
    same_count_different_book = _withheld_headline(
        dict(_decomposition(0.85, resolvable=True), renewals_offered=offered + 500))
    assert "larger SETTLED BOOK" not in same_count_different_book, (
        "only the priced count was reconciled, so a decomposition from a different-sized book "
        "priced the remedy: {}".format(same_count_different_book))

    # FAIL CLOSED, not fail silent: an artefact that cannot show which book it describes is not
    # thereby current.
    no_counts = _decomposition(0.85, resolvable=True)
    no_counts.pop("renewals_offered")
    headline = _withheld_headline(no_counts)
    assert "larger SETTLED BOOK" not in headline, (
        "a decomposition that never said which book it was measured on had its remedy published "
        "as though it described this one (R15 FAIL-SILENT): {}".format(headline))
    assert "does not say which book" in headline, (
        "the silence was not named, so a reader cannot tell an unknown from an agreement")


def _priced_by(*accounts, **extra):
    """A decomposition that DOES name the book-size remedy, plus the provenance of its price."""
    art = _decomposition(0.85, resolvable=True)
    art["where_the_priced_decisions_come_from"] = {
        "accounts_the_arm_priced": list(accounts),
        "of_those_drawn": len([a for a in accounts if a.startswith("SYN-")]),
        "of_those_static_roster": len([a for a in accounts if not a.startswith("SYN-")]),
    }
    art.update(extra)
    return art


def test_the_book_size_remedy_says_whether_the_book_can_be_grown_into_it():
    """THE DEFECT: the page priced "a larger SETTLED BOOK" at N priced renewals while the producer
    had already measured that every one of the accounts the arm priced was the founding roster and
    none was a household this world draws -- so acquisition buys zero priced decisions and only
    enlarges the half of the floor that never shrinks. The price was right and the lever named
    beside it did not exist. The measurement sat unread in the artefact the sentence was built
    from, which is the whole failure: a remedy is a claim, and one a reader cannot pull is worse
    than none because it retires the question.

    KEYED TO THE PROVENANCE, NOT TO TODAY'S ROSTER -- the caveat must DISAPPEAR the day the arm
    prices a drawn household, or it is a control asserting the world stays broken.

    R15 -- the mutations, each run and reverted:
      * drop the reachability clause from the resolvable branch -> `unreachable` reds.
      * print the caveat unconditionally -> `reachable` reds (this is the control asserting the
        world stays broken, and it is the failure mode this shape exists to refuse).
      * treat a missing `where_the_priced_decisions_come_from` as reachable -> `silent` reds.
    The null rung is `reachable`, which must carry the price and NO caveat: a control that only
    ever demands the caveat be present is satisfied by printing it always.
    """
    unreachable = _withheld_headline(_priced_by("C1", "C2", "C3"))
    assert "larger SETTLED BOOK" in unreachable and "54 priced renewals" in unreachable, (
        "the null rung of the parent control: the price must still be stated: {}".format(
            unreachable))
    assert "PRODUCT, not a size" in unreachable, (
        "every priced account was the founding roster and the page still offered book growth as "
        "the lever, which is a remedy nobody can pull: {}".format(unreachable))

    reachable = _withheld_headline(_priced_by("C1", "SYN-2021-001"))
    assert "PRODUCT, not a size" not in reachable, (
        "the arm priced a DRAWN household, so acquisition does reach it -- printing the caveat "
        "anyway is a control asserting the world stays broken: {}".format(reachable))
    assert "54 priced renewals" in reachable, reachable

    silent = _withheld_headline(_decomposition(0.85, resolvable=True))
    assert "PRODUCT, not a size" not in silent, silent
    assert "not established here" in silent, (
        "an artefact carrying no provenance read as REACHABLE by omission, which is the "
        "flattering branch chosen by silence: {}".format(silent))


def test_the_remedy_is_priced_against_the_bound_the_page_actually_shows():
    """THE DEFECT: `decompose_floor` prices the remedy on the two legs' SUMMED variance, and the
    reconciliation ratio says how far that sits from the undecomposed floor the page prints as its
    +- figure. On 2026-08-30 the legs summed to 0.66x -- inside the artefact's own 0.3-3.0
    tolerance, and a factor of 1.5 in the price (1.33x this book against the legs, 2.02x against
    the published bound). Quoting only the smaller lets a spread the artefact itself calls noise
    reach the reader as a cheaper remedy. A remedy has to bring the bound a reader is SHOWN under
    the contrast, not a smaller one they are not.

    KEYED TO THE DISCREPANCY. At a reconciliation of 1.0 the two prices are one number and the
    sentence would be noise, so it fires on the GAP -- and a repair that makes the legs sum
    properly deletes it without anyone editing this test.

    R15 -- the mutations, each run and reverted:
      * print the published-floor price unconditionally -> `reconciled` reds.
      * drop the clause entirely -> `undershot` reds (the defect as it shipped).
      * fall back to the legs' price when the producer carries no published-floor figure ->
        `old_artefact` reds.
    The null rung is `reconciled`: a control that only ever demands the sentence be present is
    satisfied by printing it always.
    """
    undershot = _withheld_headline(_priced_by(
        "C1", reconciliation_ratio=0.66,
        times_this_book_on_the_published_floor=2.02,
        priced_decisions_needed_on_the_published_floor=41))
    assert "41 priced renewals" in undershot and "number to plan on" in undershot, (
        "the page quoted a remedy priced on the legs' own total while its stated +-figure was "
        "half again as wide, which under-prices the remedy in the flattering direction: {}"
        .format(undershot))

    reconciled = _withheld_headline(_priced_by(
        "C1", reconciliation_ratio=1.0,
        times_this_book_on_the_published_floor=2.7,
        priced_decisions_needed_on_the_published_floor=54))
    assert "number to plan on" not in reconciled, (
        "the legs reconciled, so the two prices are one number and the page printed a "
        "distinction that does not exist: {}".format(reconciled))

    old_artefact = _withheld_headline(_priced_by("C1", reconciliation_ratio=0.66))
    assert "number to plan on" not in old_artefact, (
        "an artefact predating the published-floor price had a figure invented for it: {}"
        .format(old_artefact))


def test_a_resolved_contrast_names_no_remedy_at_all():
    """The remedy is printed only beside something WITHHELD. Against a contrast that cleared its
    floor it would read as an apology for a figure that earned its sign -- and it would make the
    control above satisfiable by a composer that prints the clause unconditionally."""
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"],
                                     value_advantage_gbp=50_000.0, selection_gbp=50_000.0)
    headline = gva.build(art, _floor_with_spread(100.0), _load(RUN_OUTPUT),
                         _decomposition(0.85, resolvable=True))["headline"]
    assert "larger SETTLED BOOK" not in headline, headline
    assert "More seeds would not resolve it" not in headline, headline


def test_a_stated_PRICE_carries_the_distance_the_split_cleared_its_bar_by():
    """THE DEFECT: `share_is_decisive` is a threshold crossing, and the first split to reach the
    remedy branch cleared its bar by 0.005 -- 0.1550 against 0.150, on three seeds. The page would
    have published "it takes about N priced renewals" from that with nothing beside it, which
    states a resolution the instrument did not buy.

    KEYED TO THE PROPERTY, not to today's margin: whenever the clause names a price it must also
    name the sample size and the distance. R15 -- mutation: drop
    `_how_narrowly_the_split_cleared(...)` from the resolvable branch and this reds while every
    other leg of the remedy test stays green.
    """
    from tools.run_value_cycle_ab import SHARE_DECISIVE_BAR

    thin = _decomposition(0.6588, resolvable=True)
    thin["share_margin_over_threshold"] = 0.1550
    thin["share_decisive_bar"] = SHARE_DECISIVE_BAR
    headline = _withheld_headline(thin)

    assert "54 priced renewals" in headline, (
        "the null rung: a decisive split must still state its price, or this control is satisfied "
        "by deleting the remedy altogether")
    assert "0.155" in headline, (
        "the page stated a price without the distance the split cleared its own bar by, so a "
        "photo finish reads exactly like a rout: {}".format(headline))
    assert "3 seeds" in headline, (
        "the price was published without the sample size behind it: {}".format(headline))


def test_a_price_from_an_artefact_with_NO_margin_says_so_rather_than_reading_confident():
    """An artefact written before the producer carried the margin must not buy a confident sentence
    by omission. Fail closed, on the surface."""
    older = _decomposition(0.85, resolvable=True)
    older.pop("share_margin_over_threshold", None)
    older.pop("share_decisive_bar", None)
    headline = _withheld_headline(older)

    assert "was not recorded" in headline, (
        "a decomposition carrying no margin published its price as though the split had been "
        "measured against its bar: {}".format(headline))
    assert "direction and not a settled figure" in headline


def test_the_undecided_and_cannot_branches_do_NOT_gain_a_price_caveat():
    """The caveat belongs to the branch that states a price. A branch that states none and carries
    the sentence anyway is telling a reader to discount a number that is not there."""
    undecided = _withheld_headline(_decomposition(0.51, resolvable=True, decisive=False))
    assert "direction and not a settled figure" not in undecided, (
        "the too-close-to-call branch, which states no price, was given the price caveat anyway")
    cannot = _withheld_headline(_decomposition(0.20, resolvable=False))
    assert "direction and not a settled figure" not in cannot


# ── whose customers the method has actually priced ────────────────────────────────────────────
#
# THE DEFECT (2026-08-30). The page said how MANY decisions the reading rests on and never whose.
# Every renewal the arm has ever priced belongs to a founder account; the 90 the acquisition
# funnel won and the 69 the curriculum drew have never had one reach the arm, and that is a fact
# about the enterprise value claim -- the advantage is supposed to come from inference over the
# customers the method FINDS -- rather than an internal note.

def test_the_page_says_the_method_has_never_priced_a_customer_the_company_won():
    """Fires on: dropping the block, or losing the structural verdict.

    The claim is only allowed when the artefact supports it in both parts -- no won or drawn
    account priced, AND a product gate whose whole refusal is the unset label.
    """
    out = gva.build(_load(THREE_ARM_20260829), _load(NOISE_FLOOR), _load(RUN_OUTPUT))
    who = out["decisions"]["who_the_method_has_priced"]
    assert who["available"] is True
    assert who["verdict"] == "structural"
    assert who["won_or_drawn_accounts_priced"] == 0
    assert "NEVER PRICED A CUSTOMER THE COMPANY WON" in who["sentence"]
    # The GATE is named, so a reader can check it rather than take the verdict on trust.
    assert "UPLIFTABLE_TARIFF_TYPES" in who["sentence"]
    assert "no book size at which the first one is priced" in who["sentence"]


def test_pricing_one_won_account_makes_the_structural_sentence_unreachable():
    """NULL RUNG. A verdict that cannot change when its evidence changes is not a reading of the
    evidence -- the defect `_headline_reading` was repaired for on this same page, one panel up.

    Fires on: hard-coding the structural sentence, or gating it on anything but the priced set.

    THE PRICED ACCOUNT IS ADDED TO BOTH THE ROSTER AND THE WORLD'S CLASS MAP, and it has to be.
    Until 2026-08-30 the live artefact carried no `by_account_class`, so appending a `PROS-`
    prefix to the priced list was enough -- the fallback rule read the id. The run promoted that
    day carries the world's own `acquisition_type`, and against it a fabricated id is simply not
    a won account, so the mutation stopped reaching the branch it was written to test. It was
    the FIXTURE that went stale, not the property: this test still says the verdict follows the
    priced set, and it now says it through whichever basis the artefact declares.
    """
    art = _load(THREE_ARM_20260829)
    funnel = art["renewal_funnel"]["value_arm"]
    funnel["accounts_the_arm_priced"] = list(funnel["accounts_the_arm_priced"]) + ["PROS-2019-0015"]
    if (funnel.get("by_account_class") or {}).get("available"):
        by_class = dict(funnel["by_account_class"]["priced_accounts_by_class"])
        by_class["won_by_the_funnel"] = list(by_class.get("won_by_the_funnel") or []) + [
            "PROS-2019-0015"]
        funnel["by_account_class"] = dict(funnel["by_account_class"],
                                          priced_accounts_by_class=by_class)
    who = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))[
        "decisions"]["who_the_method_has_priced"]
    assert who["verdict"] == "reached"
    assert who["won_or_drawn_accounts_priced"] == 1
    assert "NEVER PRICED" not in who["sentence"]
    assert "book size, not eligibility" in who["sentence"]


def test_a_mixed_product_gate_does_not_get_the_single_cause_sentence():
    """FAIL-CLOSED on the CAUSE, not just on the verdict. The structural sentence names ONE
    mechanism -- the unset product label -- and it is only true while that label is the whole of
    the refusal. A run whose product gate also refuses `flex` terms would have the same zero
    priced-won count for two reasons, and naming one of them would be a refusal citing a cause
    the checker never observed.
    """
    art = _load(THREE_ARM_20260829)
    art["renewal_funnel"]["value_arm"]["product_not_upliftable_by_tariff_type"] = {
        "None": 400, "'flex'": 262}
    who = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))[
        "decisions"]["who_the_method_has_priced"]
    assert who["verdict"] == "unresolved"
    assert "more than one label" in who["sentence"]


def test_the_class_split_prefers_the_worlds_own_label_over_the_id_prefix():
    """MUTATION: read the prefixes even when `by_account_class` is present.

    The prefix rule is a fallback for artefacts that predate the block, and a fallback that runs
    in preference to the measurement is how a page comes to publish the guess and the evidence
    interchangeably. Here the world's own classification says a founder-looking id was won, and
    the page must follow the world.
    """
    art = _load(THREE_ARM)
    art["renewal_funnel"]["value_arm"]["by_account_class"] = {
        "available": True,
        "priced_accounts_by_class": {"won_by_the_funnel": ["C7"], "founder_hand_authored": []},
    }
    who = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))[
        "decisions"]["who_the_method_has_priced"]
    assert who["won_or_drawn_accounts_priced"] == 1
    assert "acquisition_type" in who["classification_basis"]


# ── the structural premise is measured, and can be refuted ────────────────────────────────────
#
# THE DEFECT (2026-08-30). The live sentence says "there is no book size at which the first one
# is priced", and its premise -- that the world renders `tariff_type = None` for EVERY account it
# won or drew -- was a hardcoded clause with nothing behind it. The run's stage totals cannot
# establish it: `product_not_upliftable = 662` is equally consistent with "this book happens to
# be unlabelled" and with "no book can be labelled", which are the two readings the whole
# sentence exists to separate, and the second is the one that costs a curriculum change.

def _with_census(art, **census):
    art["renewal_funnel"]["value_arm"]["product_label_by_account_class"] = {
        "available": True, **census}
    return gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))[
        "decisions"]["who_the_method_has_priced"]


def test_a_roster_census_agreeing_with_the_gate_says_the_premise_was_measured():
    """MUTATION: drop `premise_basis`, or hardcode it to the measured string.

    "Measured on this run's roster" and "argued from the code path" are different strengths of
    the same claim, and a reader deciding whether to spend a curriculum change on it needs to
    know which one they have. Without this field the page reads at the higher strength always.
    """
    who = _with_census(_load(THREE_ARM_20260829),
                       a_found_account_can_reach_the_product_gate=False,
                       found_accounts_the_guard_would_admit=[])
    assert who["verdict"] == "structural"
    assert who["premise_basis"].startswith("measured on the roster")


def test_MUTATION_a_census_that_finds_a_labelled_won_account_withdraws_the_gate_claim():
    """NULL RUNG, and the one that stops this being a conclusion that cannot change.

    The stage totals are IDENTICAL in both halves of this test -- same 662 renewals, same single
    `None` label -- so a page that read only them would print "a GATE, not a book size" over a
    roster that directly refutes it. The census is the only field that moves, and the verdict
    must move with it. R15: a control whose PASS branch is unreachable reports a constant.
    """
    who = _with_census(_load(THREE_ARM_20260829),
                       a_found_account_can_reach_the_product_gate=True,
                       found_accounts_the_guard_would_admit=["PROS-2019-0015"])
    assert who["verdict"] == "unresolved"
    assert "GATE, not a book size" not in who["sentence"]
    assert "PROS-2019-0015" in who["sentence"]


def test_an_artefact_with_no_census_keeps_the_older_reading_rather_than_upgrading_it():
    """FAIL-CLOSED, in the direction that does NOT flatter the page.

    Every artefact produced before 2026-08-30 carries no census. Treating an absent census as
    agreement would let the strongest wording ride on the weakest evidence -- the fail-open shape
    a missing field takes when it is read as a zero. The verdict is unchanged; only its stated
    basis is.

    THE ABSENCE IS CONSTRUCTED, NOT BORROWED FROM THE LIVE ARTEFACT. This test used to read the
    promoted run directly, which worked only while no promoted run carried a census -- so it went
    red on 2026-08-30 for the one reason a control must never go red: the artefact got BETTER.
    A control keyed to today's poverty reports the poverty, not the property.
    """
    art = _load(THREE_ARM_20260829)
    art["renewal_funnel"]["value_arm"].pop("product_label_by_account_class", None)
    who = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))[
        "decisions"]["who_the_method_has_priced"]
    assert who["verdict"] == "structural"
    assert who["premise_basis"].startswith("argued from the code path")


def test_a_census_present_but_unavailable_is_not_read_as_agreement():
    """MUTATION: test `census.get("a_found_account_can_reach_the_product_gate")` alone.

    A census block that failed to build renders `available: False` and carries no verdict field;
    reading the absent flag as `False` would report the roster as having AGREED with the gate
    claim when it never ran. Both halves of the guard are needed and this is the half a naive
    read drops.
    """
    art = _load(THREE_ARM)
    art["renewal_funnel"]["value_arm"]["product_label_by_account_class"] = {
        "available": False, "reason": "the roster would not import"}
    who = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))[
        "decisions"]["who_the_method_has_priced"]
    assert who["premise_basis"].startswith("argued from the code path")


# ── the AUC's own bound: the figure that went out for four days with no interval ─────────────


def _belief(auc, retained, left):
    """A `belief_vs_outcome` block at a chosen AUC and population, everything else held."""
    art = _load(THREE_ARM)
    art["belief_vs_outcome"] = dict(
        art["belief_vs_outcome"],
        discrimination_auc=auc,
        auc_population={"retained": retained, "left": left},
        priced_and_scored=retained + left,
    )
    return art


def test_the_exact_null_enumerates_the_population_it_claims():
    """THE DEFECT I SHIPPED INTO THIS FILE AND CAUGHT BY PRINTING IT AT THE REAL INPUTS.

    The first draft of `_auc_null` gave every retained renewal an independent win count, which
    enumerates (left+1)**retained arrangements rather than C(retained+left, retained): at 10-vs-10
    that is 25,937,424,601 instead of 184,756, and it published a null interval of 0.30..0.70 and
    p = 0.000088 where the truth is 0.24..0.76 and p = 0.0039. Every figure in it was plausible,
    finite, and the right shape. Nothing but the arithmetic could tell.

    So the total is asserted against the binomial coefficient, and the 10-vs-10 tail is pinned to
    its published value -- P(U <= 13) = 0.0019431 one-sided -- from a source outside this module.
    """
    bound = gva._auc_null(10, 10, 0.13)
    assert bound["available"]
    assert "184756" in bound["basis"], bound["basis"]
    assert bound["p_two_sided"] == pytest.approx(2 * 0.0019431033, rel=1e-6)
    assert (bound["null_95_low"], bound["null_95_high"]) == (0.24, 0.76)


def test_a_null_that_does_not_sum_to_its_population_is_WITHHELD_not_published():
    """R15 FAIL-OPEN. A miscounted null still returns a number, and a bound nobody can check is
    worse than no bound -- it makes an unearned direction look earned. The guard must refuse."""
    bound = gva._auc_null(10, 10, 0.13)
    assert bound["available"]
    original = gva.math.comb
    try:
        gva.math.comb = lambda n, k: original(n, k) + 1   # the enumeration is now "wrong"
        broken = gva._auc_null(10, 10, 0.13)
    finally:
        gva.math.comb = original
    assert broken["available"] is False
    assert "does not sum" in broken["reason"]


def test_a_figure_INSIDE_its_null_is_not_read_as_a_direction():
    """KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER -- and this is the mutation that matters.

    The reading this replaced was a constant string saying "below 0.50 ... worse than a coin
    flip", so the page read 0.4653 on 25 decisions and 0.13 on 20 as the SAME finding. They are
    not: 0.4653 on 16-vs-9 is two-sided p 0.80, squarely inside the interval a random signal
    reaches. Re-pin the reading to `auc < 0.5` and this test reds while the real-artefact one
    stays green -- which is exactly the pair the old string could not tell apart.
    """
    dec = gva.build(_belief(0.4652777777777778, 16, 9), _load(NOISE_FLOOR),
                    _load(RUN_OUTPUT))["decisions"]
    assert dec["auc_attribution"]["null_bound"]["inside_the_null"] is True
    assert "INSIDE" in dec["auc_reading"]
    assert "BACKWARDS" not in dec["auc_reading"], (
        "a figure inside its own null was given a direction -- the defect the constant reading had")


def test_a_figure_OUTSIDE_its_null_ABOVE_the_point_is_not_reported_as_a_failure(real):
    """THE PASS BRANCH MUST BE REACHABLE (R15). A reading that can only ever say "backwards" or
    "cannot tell" is a constant verdict wearing a gate's clothes: the day the belief ranks well on
    a book big enough to prove it, the page must say so with nobody editing a string."""
    dec = gva.build(_belief(0.95, 10, 10), _load(NOISE_FLOOR), _load(RUN_OUTPUT))["decisions"]
    assert dec["auc_attribution"]["null_bound"]["inside_the_null"] is False
    assert "carried real information" in dec["auc_reading"]
    assert "BACKWARDS" not in dec["auc_reading"]
    # AND THE OTHER BRANCH IS REACHABLE TOO, so neither is a constant verdict. This used to be
    # asserted through the LIVE run, on the assumption that it would go on ranking backwards --
    # a control resting on the model staying bad, and on 2026-08-31 it stopped being true (AUC
    # 0.13 -> 0.655 once the standard-variable product gave the arm 120 decisions instead of 20).
    # The reachability of the branch is a property of the composer, so it is proved from a
    # constructed belief, which no world change can take away.
    backwards = gva.build(_belief(0.13, 10, 10), _load(NOISE_FLOOR),
                          _load(RUN_OUTPUT))["decisions"]
    assert backwards["auc_attribution"]["null_bound"]["inside_the_null"] is False
    assert "BACKWARDS" in backwards["auc_reading"]


def test_the_endogeneity_clause_is_NOT_gated_on_the_sample_size():
    """The clause that survives a bigger book, because it is not about the book's size.

    Five of the ten accounts the arm priced left under the value arm and did NOT leave under the
    control. That makes half the positive class a product of the arm's own price rise, and a
    LARGER book makes it a larger problem rather than a smaller one. Gating it behind the null --
    the natural way to write this function -- would delete the finding on exactly the run that
    finally has the decisions to state it.
    """
    for auc, retained, left in ((0.4652777777777778, 16, 9), (0.95, 10, 10), (0.13, 10, 10)):
        decisions = gva.build(_belief(auc, retained, left), _load(NOISE_FLOOR),
                              _load(RUN_OUTPUT))["decisions"]
        reading = decisions["auc_reading"]
        assert "NOT INDEPENDENT OF THE THING BEING GRADED" in reading, (auc, retained, left)
        # THE ACCOUNTS ARE READ OFF THE ARTEFACT, NOT HARD-CODED (2026-08-31). This asserted
        # `"C2" in reading and "C9" in reading` -- the set the 2026-08-29 run drove out. The
        # 2026-08-31 run drives out `C5_2` and `C8` instead, so the hard-coded pair red-flagged a
        # composer that was working correctly. The property is that the clause NAMES the accounts
        # it is talking about, whichever they are; a reader who cannot see them cannot check it.
        drove_out = decisions["auc_attribution"]["priced_accounts_the_arm_itself_drove_out"]
        assert drove_out, "the fixture no longer exercises the endogeneity branch at all"
        for account in drove_out:
            assert account in reading, (
                "the clause claims the arm drove {} out but does not name it, so the reader "
                "cannot check the claim: {}".format(account, reading))


def test_an_unrankable_population_gets_NO_bound_rather_than_a_default_one():
    """R15 FAIL-OPEN, the empty-class shape. With one outcome class empty there is no rank
    statistic; publishing 0.5 or a full-width interval would render "we could not compute this"
    identically to "we computed it and it says nothing"."""
    dec = gva.build(_belief(None, 20, 0), _load(NOISE_FLOOR), _load(RUN_OUTPUT))["decisions"]
    assert dec["auc_attribution"]["null_bound"]["available"] is False
    assert "no direction is read from it here" in dec["auc_reading"]


def test_the_auc_history_matches_the_artefacts_it_cites():
    """A HISTORY IS EVIDENCE ONLY IF IT IS STILL TRUE OF ITS SOURCES.

    `AUC_RUN_HISTORY` is the page's whole claim that this estimator swung 0.13..0.672 in four days
    on an unchanged code path. Each entry names the artefact it was read out of; any that still
    exists is re-read here. An entry whose artefact has been archived stands as a dated record --
    but it must never be silently repaired to whatever the newest run says, so a drift between a
    LIVE artefact and the record is a failure and not an update.
    """
    checked = 0
    for entry in gva.AUC_RUN_HISTORY:
        path = PROJECT / entry["artefact"]
        if not path.is_file():
            continue
        belief = json.loads(path.read_text(encoding="utf-8")).get("belief_vs_outcome") or {}
        assert belief.get("discrimination_auc") == pytest.approx(entry["auc"]), entry["artefact"]
        assert (belief.get("auc_population") or {}).get("left") == entry["left"], entry["artefact"]
        checked += 1
    assert checked >= 2, (
        "fewer than two of the cited artefacts survive, so this control checked almost nothing "
        "-- an unavailable check is a failed check (R15)")


def test_the_withdrawn_corroboration_sentence_is_gone_from_the_LIVE_reading(real):
    """The claim this work withdrew, and the one place it is still allowed to appear.

    The page said the selection result and the belief result "corroborate each other rather than
    merely coexisting". They share a cause -- the arm's price rise drove out five of the ten
    accounts it priced -- so it was never corroboration. It stays in `withdrawn_claim`, because a
    correction a reader cannot see is one they cannot check, and it must be nowhere else.
    """
    assert "corroborate each other" in json.dumps(real["withdrawn_claim"])
    assert "corroborate each other" not in json.dumps(real["decisions"])
    assert "corroborate each other" not in json.dumps(real["method_skill"])


def test_the_independent_grade_matches_the_artefact_the_grader_wrote():
    """The figures that CLOSE two of the three branches must not rot into folklore.

    `_auc_attribution.independent_grade` is what refutes the polarity and instrument-defect
    readings of 0.13: an oracle ceiling of 0.762 says the book ranks, and two beliefs at 0.660 and
    0.534 on the same rank statistic say it is not a sign error. They are recorded as literals
    because the page must state them whether or not the grader has been re-run — and a literal
    nobody re-reads is exactly how a measured number becomes an asserted one. So they are checked
    against the artefact `tools/grade_renewal_churn_belief.py` actually wrote.

    Fires on: a re-graded run moving any of the three while the page keeps quoting the old ones.
    """
    path = PROJECT / "docs" / "observability" / "renewal_churn_belief_grade.json"
    grade = _load(path)
    recorded = gva._auc_attribution(_load(THREE_ARM), {}, [])["independent_grade"]
    assert grade["book"]["renewals_the_world_rolled"] == recorded["renewals"]
    assert grade["book"]["billing_accounts"] == recorded["accounts"]
    for key, block in (("bill_shock_model_auc", "bill_shock_model"),
                       ("company_churn_estimate_auc", "company_estimate"),
                       ("oracle_ceiling_auc", "oracle_ceiling")):
        assert grade[block]["discrimination_auc"] == pytest.approx(recorded[key], abs=5e-5), (
            "{} has moved to {} since the page recorded {}".format(
                block, grade[block]["discrimination_auc"], recorded[key]))
    assert grade["oracle_ceiling"]["discrimination_auc"] > 0.5, (
        "the oracle ceiling no longer clears the null, so the instrument-defect branch this "
        "figure closes is REOPENED and the page's attribution is stale")


def _scored(retained_flags, left_in_population=None):
    """A `belief_vs_outcome` carrying whole scored rows, at a chosen outcome pattern."""
    art = _load(THREE_ARM)
    rows = [{"account": "C{}".format(i), "term_start": "2018-04-01", "believed_p_retain": 0.6,
             "retained": flag, "chosen_margin_gbp_per_mwh": 60.0}
            for i, flag in enumerate(retained_flags, start=1)]
    art["belief_vs_outcome"] = dict(art["belief_vs_outcome"], scored_decisions=rows,
                                    auc_population={
                                        "retained": sum(retained_flags),
                                        "left": (left_in_population if left_in_population
                                                 is not None else
                                                 len(retained_flags) - sum(retained_flags))})
    return art


def test_a_run_that_cannot_name_its_departures_says_so_rather_than_naming_TEN_OF_THEM():
    """R15 FAIL-OPEN, the half-population shape -- and the version of it that LOOKS answered.

    `matched_sample` is `scored[:10]` and has been in this artefact since the statistic existed.
    Filtering it for departures would let the page print "the departures it is computed over"
    over a SLICE, and a reader would take it for the population. The absence is published
    instead, with the reason and what fixes it.

    Fires on: sourcing `the_departures` from `matched_sample`.

    THE RUN WITHOUT `scored_decisions` IS BUILT HERE. It used to be the live artefact, and on
    2026-08-30 a run carrying the field was promoted -- so this control went red because the
    thing it guards started working. `matched_sample` is left in place deliberately: that is the
    tempting wrong source, and a fixture with neither field could pass by having nothing to read.
    """
    art = _load(THREE_ARM)
    art["belief_vs_outcome"] = {k: v for k, v in art["belief_vs_outcome"].items()
                                if k != "scored_decisions"}
    assert art["belief_vs_outcome"].get("matched_sample"), (
        "the fixture lost `matched_sample` too, so this test can no longer see the fail-open "
        "source it exists to refuse")
    departures = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))[
        "decisions"]["auc_attribution"]["the_departures"]
    assert departures["available"] is False
    assert "predates" in departures["reason"]
    assert "departures" not in departures, (
        "an unavailable list published a list -- the fail-open shape this guard exists for")


def test_a_run_carrying_its_scored_rows_names_every_departure():
    """THE PASS BRANCH, driven here because no run has produced the field yet.

    `run_value_cycle_ab.belief_vs_outcome.scored_decisions` was added 2026-08-30 and needs a
    decade run to appear. Shipping the consumer untested until then is how a render nobody has
    seen goes out on the first run that carries the field.
    """
    dep = gva.build(_scored([True, False, True, False, False]), _load(NOISE_FLOOR),
                    _load(RUN_OUTPUT))["decisions"]["auc_attribution"]["the_departures"]
    assert dep["available"] is True
    assert dep["count"] == 3
    assert [r["account"] for r in dep["departures"]] == ["C2", "C4", "C5"]
    assert dep["agrees_with_auc_population"] is True


def test_a_row_list_that_disagrees_with_the_rank_statistics_own_population_says_so():
    """DETECTION BY CONTRADICTION, which is the only kind available here.

    Two fields count the departures by different routes: the AUC's own tally and the row list. If
    the rows were ever a subset -- the exact defect the absent branch above guards against -- the
    counts diverge, and a page that published the list without checking would name six departures
    under a statistic computed over ten.

    Fires on: dropping `agrees_with_auc_population`, or computing it from the row list twice.
    """
    dep = gva.build(_scored([True, False, True], left_in_population=9), _load(NOISE_FLOOR),
                    _load(RUN_OUTPUT))["decisions"]["auc_attribution"]["the_departures"]
    assert dep["available"] is True
    assert dep["count"] == 1
    assert dep["agrees_with_auc_population"] is False


def test_the_reversal_the_page_asserts_is_published_as_a_table_and_not_only_a_word(
        real_20260829):
    """"It ranked customers BACKWARDS" is an adjective over a scalar until the reader can see it.

    `the_departures` is the check they should have and it is unavailable on every artefact written
    before 2026-08-30. `by_believed_bucket` has been in this one all along and shows the reversal
    directly: the least-confident band mostly stayed, the most-confident band kept none.

    Fires on: publishing the verdict without the table it is a description of.
    """
    table = real_20260829["decisions"]["auc_attribution"]["by_believed_bucket"]
    assert table["available"] is True, table.get("reason")
    assert table["scored"] == 20 and table["agrees_with_auc_population"] is True
    rates = [b["realised_retention_rate"] for b in table["buckets"]]
    assert rates[0] > rates[-1], (
        "the table the page calls a reversal does not fall as the belief rises")


def test_the_flipped_column_ships_so_the_table_cannot_be_read_as_settling_the_sign(
        real_20260829):
    """THE TABLE ARGUES THE OPPOSITE OF THE BLOCK BESIDE IT UNLESS THE FLIP IS SHOWN.

    Flipped, this table reads monotone the right way and looks better than any belief on this
    page. A reader given only the real column can reasonably take it as evidence OF the sign error
    `polarity_check` refutes -- so the flipped rate is published beside the real one, and the
    reading says which leg settles the question.

    Fires on: dropping the flipped column, or letting the reading claim this table closes polarity.
    """
    table = real_20260829["decisions"]["auc_attribution"]["by_believed_bucket"]
    for bucket in table["buckets"]:
        assert bucket["realised_retention_rate_under_a_flipped_label"] == pytest.approx(
            1.0 - bucket["realised_retention_rate"])
    flipped = [b["realised_retention_rate_under_a_flipped_label"] for b in table["buckets"]]
    assert flipped == sorted(flipped), (
        "the flipped column is not the flattering one, so the caveat this test guards is not the "
        "caveat the table needs -- re-read the reading against the numbers")
    assert "cannot tell you the labels are the right way round" in table["reading"]


def test_buckets_that_do_not_sum_to_the_rank_statistics_own_population_are_withheld():
    """DETECTION BY CONTRADICTION, the same route `the_departures` takes.

    The buckets and `auc_population` tally one set of decisions by different routes. A run where
    they disagree is publishing a table the AUC was not computed over, and half a table under a
    statistic is the fail-open shape: it renders, it looks answered, and it is a different book.

    Fires on: publishing `buckets` without reconciling their counts, or reconciling the bucket
    counts against themselves.
    """
    art = _load(THREE_ARM)
    art["belief_vs_outcome"] = dict(art["belief_vs_outcome"],
                                    auc_population={"retained": 10, "left": 4})
    table = gva.build(art, _load(NOISE_FLOOR),
                      _load(RUN_OUTPUT))["decisions"]["auc_attribution"]["by_believed_bucket"]
    assert table["available"] is False
    assert "20 decisions" in table["reason"] and "counts 14" in table["reason"]
    assert "buckets" not in table, "an unavailable table published its rows anyway"


def test_a_run_without_the_bucket_table_says_so_rather_than_rendering_an_empty_one():
    """FAIL-CLOSED on the artefact that does not carry the field at all.

    Fires on: defaulting the missing table to `[]`, which renders as a table with no reversal in
    it -- indistinguishable, on the page, from a belief that ranked correctly.
    """
    art = _load(THREE_ARM)
    art["belief_vs_outcome"] = {k: v for k, v in art["belief_vs_outcome"].items()
                                if k != "by_believed_bucket"}
    table = gva.build(art, _load(NOISE_FLOOR),
                      _load(RUN_OUTPUT))["decisions"]["auc_attribution"]["by_believed_bucket"]
    assert table["available"] is False
    assert "no `belief_vs_outcome.by_believed_bucket`" in table["reason"]
    assert "buckets" not in table


def test_the_polarity_leg_is_computed_from_the_runs_and_not_asserted():
    """WHAT 0.13 IS NOT, on arithmetic a reader can redo.

    A flipped outcome label sends a run's realised retention rate `r` to `1 - r` and leaves the
    believed rate alone, so on any run whose outcomes are not an even split the published level
    gap and the flipped one differ -- and which is smaller says which way round the labels are.
    Every run that can discriminate must favour the published label for the branch to close.

    Fires on: returning `refuted: True` from a default rather than from the runs.
    """
    check = gva._polarity_check(gva.AUC_RUN_HISTORY)
    assert check["available"] is True
    assert check["refuted"] is True
    assert check["runs_that_can_discriminate"] == 4
    for row in check["by_run"]:
        if row["can_discriminate"]:
            assert row["level_gap_under_a_flipped_label"] > row["level_gap_as_published"], (
                "{} sits closer to the flipped label than the published one".format(row["on"]))


def test_the_run_the_figure_comes_from_cannot_vote_on_its_own_polarity():
    """THE CAVEAT THE PROSE VERSION GOT WRONG, and the reason this is computed at all.

    The 2026-08-29 run scored exactly 10 retentions against 10 departures. At `r = 0.5` the flip
    sends the realised rate to itself, so that run's level gap is IDENTICAL under the
    transformation being tested and it carries no evidence either way. A check that let it vote
    would be counting an invariant as a confirmation -- the R15 shape where the PASS branch is
    unreachable because both sides of the comparison collapse.

    Fires on: dropping `can_discriminate` and voting every run in the history.
    """
    subject = [r for r in gva._polarity_check(gva.AUC_RUN_HISTORY)["by_run"]
               if r["auc"] == pytest.approx(0.13)]
    assert len(subject) == 1
    row = subject[0]
    assert row["can_discriminate"] is False
    assert row["the_flip_moves_this_run_by"] == pytest.approx(0.0)
    assert row["level_gap_as_published"] == pytest.approx(
        row["level_gap_under_a_flipped_label"]), (
        "the subject run is not invariant under the flip, so the caveat is wrong")
    assert "invariant under the flip" in gva._polarity_check(gva.AUC_RUN_HISTORY)["reason"]


def test_a_history_that_favours_the_flipped_label_refuses_to_close_the_branch():
    """THE FAIL BRANCH, DRIVEN. `refuted` must be a measurement and not a constant: a history whose
    discriminating runs sit closer to the flipped label has to come out False and say so, or the
    field is a control whose only verdict is PASS.

    Fires on: returning `refuted: True` unconditionally.
    """
    flipped = [dict(run, believed=1.0 - run["believed"]) for run in gva.AUC_RUN_HISTORY]
    check = gva._polarity_check(flipped)
    assert check["refuted"] is False
    assert "NOT closed" in check["reason"]


def test_a_history_of_even_splits_alone_cannot_close_the_polarity_branch():
    """THE NULL RUNG. If every run were a 50/50 split, no level evidence exists and the honest
    answer is that the branch is open -- never a quiet True.

    Fires on: treating an empty voting set as unanimous (`all([])` is True, and that is exactly
    the fail-open this rung exists to catch).
    """
    check = gva._polarity_check([dict(run, realised=0.5) for run in gva.AUC_RUN_HISTORY])
    assert check["refuted"] is False
    assert "carries no evidence either way" in check["reason"]


def test_the_history_believed_and_realised_pairs_match_the_artefacts_they_cite():
    """The level comparison is only as good as the two columns it runs on, and those are literals.

    Fires on: a run's believed/realised pair drifting from the artefact that produced it.
    """
    for run in gva.AUC_RUN_HISTORY:
        path = PROJECT / run["artefact"]
        if not path.exists():
            continue
        belief = _load(path)["belief_vs_outcome"]
        assert belief["mean_believed_p_retain"] == pytest.approx(run["believed"], abs=5e-5)
        assert belief["realised_retention_rate"] == pytest.approx(run["realised"], abs=5e-5)


# ── an artefact carries the code that made it, or its counts come off the page ────────────────
#
# THE DEFECT (2026-08-30, twice in two stretches). A three-arm run takes an hour and fifty
# minutes; this tree lands population changes about every forty. So the code that DREW a run's
# book and the code ASSEMBLING its artefact are routinely two different trees, and every field
# resolved at assembly time describes the later one. Both traps were repaired by guarding the
# field the previous trap had named -- `book_identity`'s shape, then its resolution point -- and
# both repairs missed the property behind them, which is that only the producing process knows
# which tree it bound. `run_value_cycle_ab.PRODUCING_COMMIT` is resolved at import for that
# reason; these are the consumer's half.


def _stamped(art: dict, commit: str | None) -> dict:
    """`art` with a producing-commit stamp of the producer's own shape."""
    art = dict(art)
    art["producing_commit"] = {
        "commit": commit,
        "resolved_at": "2026-08-30T09:50:08Z",
        "resolved_when": "at process start",
        "unavailable_because": None if commit else "git did not answer",
    }
    return art


def test_a_run_that_cannot_name_its_producing_commit_gets_no_counts_on_the_page():
    """FAIL-CLOSED, and on the field a reader would most readily mistake for a fact.

    "167 settled billing accounts" reads as a fact about this supplier. On the run promoted
    2026-08-30 it is a fact about a population the tree no longer draws, and the artefact cannot
    say so because it predates the stamp. The counts are withheld with the reason rather than
    published unattributed.

    Fires on: publishing `book_identity.control_arm` regardless of provenance; on defaulting an
    absent stamp to "same tree"; and on leaving the same count reachable through
    `decisions.book_accounts_settled`, which is the second route to it and the one a withdrawal
    that only edits `book` would leave behind.
    """
    art = _load(THREE_ARM)
    art.pop("producing_commit", None)
    d = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))

    assert d["producing_commit"]["stated"] is False
    assert d["producing_commit"]["counts_are_labelled_by_the_code_that_made_them"] is False
    assert d["book"]["available"] is False
    assert "billing_accounts_settled_in_window" not in d["book"], (
        "the withheld count is still on the page under its own name")
    assert d["decisions"]["book_accounts_settled"] is None, (
        "the count came off `book` and stayed reachable through `decisions` -- a cosmetic "
        "withdrawal, which is the shape this control exists to refuse")
    # THE REASON IS PUBLISHED, not just the absence. A refusal that does not name its cause is
    # how this project discovered a refusal was itself wrong, within an hour of shipping.
    assert "predates the producing-commit stamp" in d["book"]["why_the_counts_are_withheld"]
    # AND THE REVIEWER'S COPY SURVIVES, under a key the door does not render.
    assert d["book"]["unlabelled_counts"]["billing_accounts_settled_in_window"] == (
        art["book_identity"]["control_arm"]["billing_accounts_settled_in_window"])


def test_a_stamped_run_published_from_the_same_tree_puts_its_counts_back():
    """THE PASS BRANCH, which is what stops this being a machine for printing a refusal.

    R15: a control whose PASS branch is unreachable reports a constant verdict. Keyed to the
    property -- the day a stamped run is promoted the counts return with nobody editing a string.

    Fires on: hard-coding the withheld branch; on a `stated` flag that cannot become true.
    """
    art = _stamped(_load(THREE_ARM), gva.PUBLISHING_TREE_COMMIT or "0" * 40)
    d = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))

    assert d["producing_commit"]["stated"] is True
    assert d["book"]["available"] is True
    assert d["book"]["billing_accounts_settled_in_window"] == (
        art["book_identity"]["control_arm"]["billing_accounts_settled_in_window"])
    assert d["decisions"]["book_accounts_settled"] == (
        d["book"]["billing_accounts_settled_in_window"])
    if gva.PUBLISHING_TREE_COMMIT:
        assert d["producing_commit"]["produced_by_the_tree_it_publishes_from"] is True
        assert "same tree" in d["producing_commit"]["reading"]


def test_a_stamped_run_published_from_a_DIFFERENT_tree_says_which_two_trees():
    """THE MIDDLE STATE, and the one the whole mechanism was built to make sayable.

    A run stamped with a commit that is not the publishing tree's is not a failure -- it is the
    normal case for any run longer than the landing cadence. The counts stay on the page BECAUSE
    they are attributable; what changes is that the page names both trees instead of letting the
    reader assume one.

    Fires on: collapsing this into either neighbour -- withholding a perfectly attributable
    count, or reporting a stale run as though it were current.
    """
    art = _stamped(_load(THREE_ARM), "f" * 40)
    d = gva.build(art, _load(NOISE_FLOOR), _load(RUN_OUTPUT))

    assert d["book"]["available"] is True
    if gva.PUBLISHING_TREE_COMMIT:
        assert d["producing_commit"]["produced_by_the_tree_it_publishes_from"] is False
        assert "the code was replaced between the run and this page" in (
            d["producing_commit"]["reading"])
        assert d["producing_commit"]["short"] == "f" * 9


def test_a_stamp_carrying_no_commit_is_not_read_as_a_commit():
    """MUTATION: `three_arm.get("producing_commit") is not None` as the whole test.

    A producer that could not reach git writes the block WITH `commit: None` and the reason. A
    consumer keyed on the block's presence rather than on the sha would read that run as fully
    attributed -- the fail-open a missing field takes when it is read as a zero -- and would
    publish the producer's own stated absence as a label. The empty string is the same shape.

    The producer's OWN reason is preferred over this file's generic one, because it is the
    specific fact: "git did not answer" and "this run predates the stamp" are different states
    and only the run knows which it was in.
    """
    for empty in (None, "", "   "):
        d = gva.build(_stamped(_load(THREE_ARM), empty), _load(NOISE_FLOOR), _load(RUN_OUTPUT))
        assert d["producing_commit"]["stated"] is False, empty
        assert d["book"]["available"] is False, empty
    assert "git did not answer" in gva.build(
        _stamped(_load(THREE_ARM), None), _load(NOISE_FLOOR), _load(RUN_OUTPUT)
    )["producing_commit"]["reason"]


def test_the_drop_out_consequence_names_the_class_that_is_ours_to_fix():
    """The unflattering half of "widenable: yes", said out loud and DERIVED from the counts.

    `the_sample_can_be_widened_from_this_book` is true whenever EITHER a join failure or a
    coverage gap is non-zero, and those are not the same news: one is our code and one is data we
    owe. A reader who meets the boolean and stops has been told the flattering half.

    Fires on: hard-coding either sentence. The join branch and the no-join branch are both driven
    here, because a control that only ever sees today's zero cannot tell a derived sentence from
    a constant.
    """
    none_ours = gva._widening_consequence({"join": 0, "coverage": 4, "eligibility": 10})
    assert "ZERO are a join we failed to make" in none_ours
    assert "cannot be widened by fixing our own code" in none_ours
    assert "4 wait on a gap in our own sourced tariff series" in none_ours
    assert "10 are decisions the world never billed" in none_ours

    ours = gva._widening_consequence({"join": 3, "coverage": 4, "eligibility": 10})
    assert "3 are a join we failed to make" in ours
    assert "cannot be widened" not in ours, (
        "a run WITH a join failure was told its sample cannot be widened -- the sentence is a "
        "constant, not a reading of the classes")
    assert "ours to fix here" in ours

    # FAIL-CLOSED on a class table that is not three integers: no sentence rather than a wrong
    # one, because this sentence is the one a reader would trust most.
    assert gva._widening_consequence({"join": 0, "coverage": 0, "eligibility": 0}) is None
    assert gva._widening_consequence({"join": None, "coverage": 4, "eligibility": 10}) is None
    assert gva._widening_consequence({}) is None


# ─────────────────────────────────────────────────────────────────────────────────────────────
# WHETHER THE WORLD THESE FIGURES WERE MEASURED IN IS STILL THE WORLD
#
# THE DEFECT (2026-09-03). Every leg above asks whether a figure is arithmetically right, whether
# its clock is declared, whether its bound predates it, whether its book matches. None asked
# whether the WORLD it was measured in still existed. The published beat -- £12,071 over a
# flat-rule baseline -- was measured 2026-08-31; `simulation/departure_level_anchor.py` was
# re-fitted twice afterwards, and on the arms' own capture population that swap moves whole-book
# expected departure +19.06pp summed across 2017-2024 against published bands 0.5-3.6pp wide.
# Every artefact read the same and every control stayed green.
#
# R15 -- the mutations, each run and reverted:
#   * return `superseded: False` instead of `None` when no artefact carries a stamp ->
#     `test_a_run_that_cannot_name_its_world_is_an_absence_not_a_clean_bill` reds. This is the
#     fail-open shape: a consumer treating the block as a boolean would read "not superseded".
#   * drop the `unstamped` branch and compare digests only ->
#     `test_a_run_that_cannot_name_its_world_is_an_absence_not_a_clean_bill` reds, because
#     every artefact on disk today has no stamp and would compare equal to nothing.
#   * make `_world_clause` return its sentence unconditionally ->
#     `test_a_run_in_the_live_world_gets_no_history_clause` reds (the constant-verdict shape:
#     a clause that always fires is not a reading of the provenance).
#   * make `_world_clause` return "" unconditionally ->
#     `test_a_superseded_world_reaches_the_headline_and_not_only_the_payload` reds.
#   * key the digest to the commit hash rather than the anchor block ->
#     `test_the_world_digest_tracks_the_departure_level_and_not_the_commit` reds.


def _world_stamped(artefact: dict, digest) -> dict:
    """The artefact with a world stamp, or with none at all when `digest` is None."""
    out = dict(artefact)
    if digest is None:
        out.pop("world_identity", None)
    else:
        out["world_identity"] = {"digest": digest, "unavailable_because": None}
    return out


def _live_digest() -> str:
    from simulation.departure_level_anchor import world_level_identity

    return world_level_identity()["digest"]


def test_a_run_that_cannot_name_its_world_is_an_absence_not_a_clean_bill():
    """An unstamped run must not read as one measured in the live world.

    THIS IS THE STATE EVERY ARTEFACT ON DISK IS IN TODAY, so it is the live branch and not an
    edge case. `superseded` must be None -- never False -- because a consumer that treats the
    block as a boolean would otherwise get the flattering branch from an absence.

    Fires on: returning False for "cannot tell", or dropping the unstamped branch so that a
    missing digest compares equal to nothing and falls through to the clean return.
    """
    verdict = gva._world_provenance(
        ("the three-arm run", _world_stamped(_load(THREE_ARM), None)),
        ("the noise floor", _world_stamped(_load(NOISE_FLOOR), None)))
    assert verdict["available"] is False
    assert verdict["superseded"] is None, (
        "an artefact that does not say which world it ran in was reported as NOT superseded -- "
        "an absence rendering as a clean bill of health")
    assert "DO NOT SAY WHICH WORLD" in verdict["reason"]
    # The runs are named by the CALLER's label, never by a slice of their own prose.
    named = verdict["runs_that_cannot_name_their_world"]
    assert any("the three-arm run" in run for run in named), named
    assert not any("selection-figure" in run for run in named), (
        "a run was named by a fragment of its own `what_this_is` prose")

    # AN ABSENCE IS NOT A DISAGREEMENT, and this is the sole witness for that. This branch sets no
    # `one_world_across_every_figure` at all, so a mixed-world test keyed on FALSINESS rather than
    # `is False` would read the missing key as "these legs disagree" and tell a reader the figure
    # and its bound came from different worlds -- a specific false claim, made where the honest
    # verdict is that we cannot tell. Mutation-checked: without this the falsiness variant
    # survives the whole file.
    clause = gva._world_clause(verdict)
    assert "DIFFERENT WORLDS" not in clause, (
        "runs that cannot name their world were reported as having named two different ones: "
        + clause[:160])
    assert clause.startswith("READ THIS AS HISTORY"), clause[:160]


def test_a_run_in_the_live_world_gets_no_history_clause():
    """THE PASS BRANCH MUST BE REACHABLE, or the verdict is a constant.

    A control whose clean branch can never fire reports the same answer forever and would go on
    printing "read this as history" over a run that IS current -- which trains a reader to skip
    the one sentence that matters. This drives the live-world case explicitly.

    Fires on: `_world_clause` returning its sentence unconditionally.
    """
    live = _live_digest()
    verdict = gva._world_provenance(
        ("the three-arm run", _world_stamped(_load(THREE_ARM), live)),
        ("the noise floor", _world_stamped(_load(NOISE_FLOOR), live)))
    assert verdict["available"] is True
    assert verdict["superseded"] is False
    assert verdict["one_world_across_every_figure"] is True
    assert verdict["reason"] is None
    assert gva._world_clause(verdict) == "", (
        "a run measured in the live world was still prefixed 'READ THIS AS HISTORY' -- the "
        "clause is a constant, not a reading of the provenance")


def test_a_superseded_world_reaches_the_headline_and_not_only_the_payload():
    """A caveat in the payload that never reaches the sentence a reader reads is not a caveat.

    The headline is where the £12,071 is stated, so it is where the world it was measured in has
    to be stated too -- ahead of the figure, because a reader who meets the number first has
    already taken it as current.

    Fires on: `_world_clause` returning "" unconditionally, or the clause being appended after
    the advantage sentence instead of before it.
    """
    stale = _world_stamped(_load(THREE_ARM), "0000000000000000")
    verdict = gva._world_provenance(("the three-arm run", stale))
    assert verdict["superseded"] is True
    assert verdict["live_world"] != "0000000000000000"

    built = gva.build(stale, _world_stamped(_load(NOISE_FLOOR), "0000000000000000"),
                      _load(RUN_OUTPUT))
    assert built["world_provenance"]["superseded"] is True
    assert built["headline"].startswith("READ THIS AS HISTORY"), (
        "the world caveat did not reach the headline, or reached it after the figure it "
        "qualifies: " + built["headline"][:120])
    # The figures themselves are KEPT. Superseded-with-provenance is the correction; deletion
    # is not -- so the advantage must still be stated, under its caveat.
    assert "12,071" in built["headline"]


def test_a_superseded_run_that_names_its_world_still_puts_its_date_in_the_clause():
    """The date must survive the branch where every artefact IS stamped.

    SOLE WITNESS FOR THE UNIFORM-SUPERSEDED BRANCH: both legs carry the SAME non-live digest, so
    `one_world_across_every_figure` is True and the mixed branch below cannot also satisfy this.

    THE DEFECT. `_world_clause` harvested its date by regexing
    `runs_that_cannot_name_their_world` -- a key only the UNSTAMPED branch sets. Every artefact on
    disk today predates the world stamp, so that branch is the live one and its coverage read as
    coverage of both; the moment stamped artefacts go stale, the clause rendered "READ THIS AS
    HISTORY" with no date at all, contradicting `_world_clause`'s own docstring and the drawn
    direction's done-condition ("the date each figure was measured is on the surface a reader
    sees").

    Fires on: dropping `runs_measured_in_a_superseded_world` from `_world_provenance`, or
    reverting `_world_clause` to harvest dates from the unstamped key alone.
    """
    verdict = gva._world_provenance(
        ("the three-arm run", _world_stamped(_load(THREE_ARM), "0000000000000000")),
        ("the noise floor", _world_stamped(_load(NOISE_FLOOR), "0000000000000000")))
    assert verdict["superseded"] is True
    assert verdict["one_world_across_every_figure"] is True, (
        "this subject must witness the UNIFORM branch, or it grades the mixed one by accident")
    named = verdict["runs_measured_in_a_superseded_world"]
    assert any("the three-arm run" in run for run in named), named
    assert any("the noise floor" in run for run in named), named

    clause = gva._world_clause(verdict)
    assert clause.startswith("READ THIS AS HISTORY")
    assert re.search(r"\d{4}-\d{2}-\d{2}", clause), (
        "the history clause named no date, so a reader is told these figures are old and given "
        "nothing to place them by: " + clause[:160])


def test_a_live_figure_bounded_by_a_stale_spread_is_not_reported_as_history():
    """Mixed worlds get their own verdict, because the remedy differs.

    SOLE WITNESS FOR THE MIXED BRANCH: the three-arm leg carries the LIVE digest and the floor
    leg does not, so `one_world_across_every_figure` is False and the uniform branch above cannot
    also satisfy this.

    THE DEFECT. Both branches collapsed into "READ THIS AS HISTORY ... these figures were measured
    over a departure level that is no longer the one this world runs at" -- FALSE about the leg
    that is current, and false in the direction that stops a reader asking WHICH figure is stale,
    when which figure is stale is the whole question. A point estimate in this world bounded by a
    spread from another is `c30b98048`, filed 2026-08-31 on this very artefact. The verdict that
    separates them, `one_world_across_every_figure`, was computed and read by nothing that
    publishes.

    Fires on: `_world_clause` losing its mixed branch; `_world_provenance` reporting one reason for
    both states; keying the mixed branch on falsiness rather than `is False`, which would drag the
    unstamped branch (no such key) onto the mixed sentence.
    """
    live = _live_digest()
    verdict = gva._world_provenance(
        ("the three-arm run", _world_stamped(_load(THREE_ARM), live)),
        ("the noise floor", _world_stamped(_load(NOISE_FLOOR), "0000000000000000")))
    assert verdict["superseded"] is True
    assert verdict["one_world_across_every_figure"] is False, (
        "this subject must witness the MIXED branch, or it grades the uniform one by accident")
    assert any("the noise floor" in run
               for run in verdict["runs_measured_in_a_superseded_world"])
    assert any("the three-arm run" in run
               for run in verdict["runs_measured_in_the_live_world"])
    assert "DIFFERENT WORLDS" in verdict["reason"]

    clause = gva._world_clause(verdict)
    assert "DIFFERENT WORLDS" in clause, (
        "a figure measured in the live world and a bound measured in another rendered as the "
        "undifferentiated history caveat: " + clause[:160])
    assert "READ THIS AS HISTORY" not in clause, (
        "the page told a reader that a run measured in the LIVE world was history")
    assert re.search(r"\d{4}-\d{2}-\d{2}", clause), (
        "the mixed clause named no date, so a reader cannot tell which leg is the stale one: "
        + clause[:160])


def test_a_live_leg_beside_an_UNSTAMPED_one_is_mixed_and_never_history():
    """The OTHER way a page is mixed, and until 2026-09-03 nothing could say so.

    SOLE WITNESS: the three-arm leg carries the LIVE digest and the floor carries NO
    `world_identity` at all. That combination reaches the unstamped early return, not the
    all-stamped branch the rung above witnesses -- so neither of the two existing subjects can
    satisfy this one, and this one cannot be graded by accident.

    THE DEFECT. `_world_provenance` returned from the unstamped branch without setting
    `one_world_across_every_figure`, and `_world_clause` reads that key with `is False`; an absent
    key therefore selected "READ THIS AS HISTORY". So a run measured in the LIVE world, published
    beside a floor that predates the world stamp, was announced to the reader as history. It had
    never fired because every artefact on disk predated the stamp, making this branch uniformly
    old and its neighbour's coverage read as coverage of both.

    IT IS ALSO THE STATE THE PAGE IS ACTUALLY IN. The arms were re-run in the live world on
    2026-09-03; the floor legs for that world are still running. So this is not a hypothetical
    combination -- it is the live one.

    Fires on: the unstamped branch dropping `one_world_across_every_figure`; setting it to a bare
    `False` when NO leg is live (which would call a uniformly-old page mixed); or `available`
    turning True, which would claim a page that cannot name one of its worlds is current.
    """
    live = _live_digest()
    unstamped_floor = {k: v for k, v in _load(NOISE_FLOOR).items() if k != "world_identity"}
    verdict = gva._world_provenance(
        ("the three-arm run", _world_stamped(_load(THREE_ARM), live)),
        ("the noise floor", unstamped_floor))

    # STILL AN ABSENCE. A page that cannot name one of its worlds cannot be shown to be current,
    # so the fix must not buy a clean bill -- it buys only an honest verdict.
    assert verdict["available"] is False, (
        "a page holding a leg that names no world at all was reported as able to name its world")
    assert verdict["superseded"] is None, "an unknown world must not resolve to a boolean"
    assert verdict["one_world_across_every_figure"] is False, (
        "a live leg beside an unstamped one is MIXED, and this branch reported no verdict at all")
    assert any("the three-arm run" in run
               for run in verdict["runs_measured_in_the_live_world"])
    assert any("the noise floor" in run
               for run in verdict["runs_that_cannot_name_their_world"])
    assert "MIXED, NOT UNIFORMLY OLD" in verdict["reason"], (
        "the reason did not say which leg is current: " + verdict["reason"][:200])

    clause = gva._world_clause(verdict)
    assert "DIFFERENT WORLDS" in clause, (
        "a live figure beside an unstamped bound rendered as the undifferentiated history "
        "caveat: " + clause[:160])
    assert "READ THIS AS HISTORY" not in clause, (
        "the page told a reader that a run measured in the LIVE world was history")


def test_an_all_unstamped_page_is_still_history_and_not_called_mixed():
    """The complement, so the fix above cannot have bought its verdict by always saying MIXED.

    SOLE WITNESS: NO leg carries a `world_identity`, so `runs_measured_in_the_live_world` is empty
    and the page is uniformly old rather than mixed. Without this rung, setting
    `one_world_across_every_figure` to a constant `False` on the unstamped branch would pass the
    rung above and silently retire the history verdict for every page that deserves it.
    """
    strip = lambda art: {k: v for k, v in art.items() if k != "world_identity"}  # noqa: E731
    verdict = gva._world_provenance(
        ("the three-arm run", strip(_load(THREE_ARM))),
        ("the noise floor", strip(_load(NOISE_FLOOR))))
    assert verdict["available"] is False
    assert verdict["one_world_across_every_figure"] is None, (
        "a page with no live leg at all was reported as MIXED, which tells a reader some figure "
        "here is current when none is")
    assert verdict["runs_measured_in_the_live_world"] == []
    assert "MIXED" not in verdict["reason"]
    assert "READ THIS AS HISTORY" in gva._world_clause(verdict)


def test_a_current_world_block_refuses_a_run_that_names_another_world():
    """The current-world figure is admitted on its DIGEST, never on its filename.

    SOLE WITNESS FOR THE REFUSAL. The artefact committed at the path the page reads happens to BE
    the live world today, so removing the digest check changes nothing about the published feed --
    an equivalence, not a passing control. These subjects are the only ones that can tell the two
    apart: one stamped with a foreign digest, one carrying no stamp at all.

    THE DEFECT IT PREVENTS. `current_world` is the block that says "in the world as it is now", so
    a stale artefact admitted here is not a wrong number, it is a wrong number wearing the label
    that stops a reader checking. The flattering reading of a file at a path called
    `..._20260903.json` is that it is current; only the digest can refuse it.

    Fires on: dropping the `ran_in != live` guard; comparing dates or commits instead of the
    digest; or returning `available: True` with a `why_not` beside it.
    """
    live = _live_digest()
    current = _load(THREE_ARM)

    foreign = gva._current_world_contrast(_world_stamped(current, "0000000000000000"), None)
    assert foreign["available"] is False, (
        "a run measured in another world was published as the figure for the world as it is now")
    assert foreign["resolved"] is None
    assert "0000000000000000" in foreign["why_not"] and live in foreign["why_not"], (
        "the refusal named neither the world the run was in nor the live one, so a reader cannot "
        "tell how far off it is: " + foreign["why_not"])

    unstamped = gva._current_world_contrast(
        {k: v for k, v in current.items() if k != "world_identity"}, None)
    assert unstamped["available"] is False, (
        "a run that names NO world was accepted as the current-world one, which is the "
        "fail-silent branch: unknown provenance reads as fine unless something says so")

    missing = gva._current_world_contrast(None, None)
    assert missing["available"] is False and missing["resolved"] is None
    assert missing["why_not"], "an absent run refused without saying why"

    # THE PASS BRANCH IS REACHABLE, or every assertion above is graded by a function that can only
    # ever refuse -- the constant-verdict shape this file records elsewhere.
    admitted = gva._current_world_contrast(_world_stamped(current, live), None)
    assert admitted["available"] is True, (
        "no subject reaches the admitting branch, so the refusals above prove nothing")
    assert admitted["resolved"] is None, (
        "a figure with no same-world bound was reported as resolved; `None` is the honest state")
    # NO CURRENT-WORLD FLOOR WAS SUPPLIED, so there is no bound. Keyed to the ARGUMENT, not to
    # today's disk: this stays true when the live-world floor lands, because this call still
    # passes none.
    assert admitted["bound_available"] is False
    assert "NO BOUND ON THIS PAGE WAS MEASURED IN THIS WORLD" in admitted["why_no_bound"]


#: THE LEG WHOSE SPREAD DOES NOT BOUND THE PUBLISHED FIGURE, and which is on disk in the live
#: world while the undecomposed one is still being measured. Sole witness for the leg guard.
NOISE_FLOOR_ONLY_LIVE = (
    PROJECT / "docs" / "observability" / "value_cycle_ab_s1_noise_floor_only_20260903.json")


def test_the_current_world_bound_takes_only_the_undecomposed_leg_of_this_world():
    """A bound is admitted on the floor's WORLD and its LEG, and each guard has a sole witness.

    THE DEFECT IT PREVENTS, and it is two defects that look like one. The page states a verdict on
    the current-world contrast only from a floor measured in that world -- and only from the
    UNDECOMPOSED leg, because `only` and `except` partition that variance between them and neither
    half bounds the whole. Both wrong subjects exist today: the superseded floor is the right leg
    with no world, and the `only` leg is the right world with the wrong leg. Admitting either
    publishes a verdict priced against a spread that does not bound the figure, in the flattering
    direction both times -- the `only` leg's variance was about half the undecomposed one's on the
    single seed family where all three legs have been measured.

    SOLE WITNESSES, so neither guard is an equivalence the other covers for. No subject here
    satisfies both alternations: `NOISE_FLOOR` is mode `all` and names no world; the `only` leg
    names the live world and is the wrong mode. Drop the world check and the first is admitted;
    drop the leg check and the second is.

    Fires on: dropping either guard; reading a bound from the superseded `floor` argument;
    admitting a refusal stub with no `generated_at`; or bounding the contrast with the floor's
    published `selection_gbp_spread` instead of this contrast's own spread.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    only_leg = _load(NOISE_FLOOR_ONLY_LIVE)

    # SOLE WITNESS FOR THE WORLD GUARD: the undecomposed leg, naming no world.
    assert (superseded.get("redraw_scope") or {}).get("mode") == gva.BOUNDING_REDRAW_MODE, (
        "this subject no longer isolates the WORLD guard -- it must be the right leg so that only "
        "the world check can refuse it")
    stale = gva._current_world_contrast(current, superseded, superseded)
    assert stale["bound_available"] is False, (
        "a floor from the superseded world bounded a figure measured in this one -- the "
        "c30b98048 defect, and the ratio it forms is not a quantity")
    assert stale["resolved"] is None

    # SOLE WITNESS FOR THE LEG GUARD: the live world, and the half that does not bound the whole.
    assert ((only_leg.get("world_identity") or {}).get("digest")) == live, (
        "this subject no longer isolates the LEG guard -- it must name the live world so that "
        "only the mode check can refuse it")
    wrong_leg = gva._current_world_contrast(current, superseded, only_leg)
    assert wrong_leg["bound_available"] is False, (
        "the `only` leg bounded the published contrast; it re-draws the priced roster alone and "
        "its spread is half the undecomposed floor's, so the verdict would be too confident")
    assert wrong_leg["resolved"] is None
    assert "WRONG LEG" in wrong_leg["why_no_bound"] and "only" in wrong_leg["why_no_bound"], (
        "the refusal did not name which leg it got, so a reader cannot tell it apart from the "
        "world refusal: " + wrong_leg["why_no_bound"])

    # A DEAD RUN IS NOT A FLOOR. The leg has been OOM-killed once; a refusal written at `--out`
    # parses and carries no timestamp.
    stub = {k: v for k, v in only_leg.items() if k != "generated_at"}
    stub["redraw_scope"] = dict(only_leg["redraw_scope"], mode=gva.BOUNDING_REDRAW_MODE)
    assert gva._current_world_contrast(current, superseded, stub)["bound_available"] is False, (
        "a refusal stub with no `generated_at` was read as a completed floor")

    # THE PASS BRANCH IS REACHABLE, or every refusal above is graded by a function that can only
    # refuse -- the constant-verdict shape this whole control was written to remove.
    admitted = dict(only_leg, redraw_scope=dict(only_leg["redraw_scope"],
                                                mode=gva.BOUNDING_REDRAW_MODE))
    bounded = gva._current_world_contrast(current, superseded, admitted)
    assert bounded["bound_available"] is True, (
        "no subject reaches the bounding branch, so `bound_available` is still a constant and the "
        "floor leg now running cannot ever reach the page")
    # THE BOUND IS CONSUMED, in one of the two ways that are not silence. Keyed to the property
    # and not to "a verdict is stated": on 2026-09-03 this block began WITHHOLDING a verdict its
    # own floor's re-draws reverse, which is strictly more honest, and an assertion pinned to
    # today's answer would have gone red for the page improving. What must never happen is a
    # bound read and nothing said off it -- that is the state the block was in before.
    assert bounded["resolved"] in (True, False) or bounded["verdict_withheld_because"], (
        "a bound was read and neither a verdict nor a named reason for withholding one came of "
        "it, which is the state the block was in before")
    assert bounded["bound_contrast"] == "value_advantage_gbp"

    # THE BOUND IS THIS CONTRAST'S OWN SPREAD, never the floor's published `selection_gbp_spread`.
    # The two differ by 2.6x on the 2026-08-29 family, and reaching for the scalar the producer
    # happens to publish is the cross-contrast pairing this page exists to keep off the surface.
    published_selection = (only_leg.get("selection_gbp_spread") or {}).get("stdev")
    assert bounded["bound"]["stdev_gbp"] != pytest.approx(published_selection), (
        "the contrast was bounded by the floor's SELECTION spread, which counts a different "
        "quantity -- two correct numbers whose ratio is not one")


def test_the_generator_reads_the_current_world_floor_from_its_own_constant(tmp_path, monkeypatch):
    """`generate()` must actually READ the live-world floor, not merely accept one as an argument.

    THE DEFECT IT PREVENTS, and it is the one that produced this whole claim twice. A refusal
    added to the control and not to `main()` leaves the printed page failing open: every guard in
    `_current_world_bound` can be perfect and the page still publishes "no bound was measured in
    this world" forever, because nothing hands it the artefact. That is exactly what happened to
    the contrast itself -- the arms were re-run, landed, and `generate()` did not read them -- and
    the commit that repaired it moved the three-arm path and left the floor path beside it.

    ASSERTED THROUGH THE DEFAULT, which is the branch the site runs. Passing the path explicitly
    would prove only that the parameter exists; the fail-open is in what `None` resolves to. So
    the module's own constant is redirected and `generate()` called with no path at all.

    Fires on: dropping the `_read(CURRENT_WORLD_NOISE_FLOOR_PATH ...)` argument; passing `None`
    for it; or reading it into a variable `build` never receives.
    """
    live = _live_digest()
    only_leg = _load(NOISE_FLOOR_ONLY_LIVE)
    # THE LEG THE PAGE IS WAITING FOR, synthesised. The real one is still being measured; this
    # control is about the WIRING and must not wait on a run to be able to fail.
    undecomposed = dict(only_leg, redraw_scope=dict(only_leg["redraw_scope"],
                                                    mode=gva.BOUNDING_REDRAW_MODE))
    floor_path = tmp_path / "floor_all_live_world.json"
    floor_path.write_text(json.dumps(undecomposed), encoding="utf-8")
    monkeypatch.setattr(gva, "CURRENT_WORLD_NOISE_FLOOR_PATH", floor_path)

    three_arm_path = tmp_path / "three_arm_live.json"
    three_arm_path.write_text(
        json.dumps(_world_stamped(_load(gva.CURRENT_WORLD_THREE_ARM_PATH), live)),
        encoding="utf-8")
    monkeypatch.setattr(gva, "CURRENT_WORLD_THREE_ARM_PATH", three_arm_path)

    data = gva.generate(out_path=tmp_path / "value_arms.json")
    cw = data["current_world"]
    assert cw["available"] is True, "the synthesised current-world run was not admitted at all"
    assert cw["bound_available"] is True, (
        "`generate()` did not read the current-world floor from its own constant, so the page "
        "stays unbounded however many floor legs land: " + str(cw.get("why_no_bound"))[:200])
    # Either a verdict or a named withholding -- see the sibling control for why this is not
    # `resolved is not None`. The wiring defect this test exists for is the floor never being
    # READ, and both outcomes prove it was.
    assert cw["resolved"] is not None or cw["verdict_withheld_because"], (
        "the floor was read and the block neither stated a verdict nor named why it withheld "
        "one, so nothing downstream can tell a bound from no bound")


def test_MUTATION_the_leg_guard_and_the_world_guard_each_fail_alone():
    """Each guard must red on its own witness when removed, or it is not a control.

    Run here rather than trusted: the previous version of this block asserted a constant, and a
    constant satisfies any assertion written against it. These two mutations are the ones a
    well-meaning edit makes -- "the artefact on disk is the live world, so the digest check is
    redundant", and "we only ever write one floor, so the mode check is redundant" -- and each is
    true of one subject and false of the other.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    only_leg = _load(NOISE_FLOOR_ONLY_LIVE)

    # MUTATION 1: the world guard drops. The superseded floor -- right leg, no world -- is the
    # only subject that tells the mutated function from the real one.
    world_blind = gva._current_world_bound(
        dict(superseded, world_identity={"digest": live}), current, live)
    assert world_blind["bound_available"] is True, (
        "the superseded floor does not become admissible when its digest is faked to the live "
        "one, so it cannot witness the removal of the world guard")
    assert gva._current_world_bound(superseded, current, live)["bound_available"] is False, (
        "the world guard is not what refuses the superseded floor")

    # MUTATION 2: the leg guard drops. The `only` leg -- live world, wrong mode -- is the only
    # subject that tells that mutation from the real function.
    leg_blind = gva._current_world_bound(
        dict(only_leg, redraw_scope=dict(only_leg["redraw_scope"],
                                         mode=gva.BOUNDING_REDRAW_MODE)), current, live)
    assert leg_blind["bound_available"] is True, (
        "the `only` leg does not become admissible when its mode is relabelled, so it cannot "
        "witness the removal of the leg guard")
    assert gva._current_world_bound(only_leg, current, live)["bound_available"] is False, (
        "the leg guard is not what refuses the `only` leg")


def _floor_with_advantages(floor: dict, values: list) -> dict:
    """The same floor with its per-seed `value_advantage_gbp` replaced, and nothing else touched.

    The bound is DERIVED from these rows, so substituting them moves the spread as well as the
    verdicts -- which is the point: a witness has to be a floor that could really have been
    measured, not a spread pasted next to values that never produced it.
    """
    seeds = [dict(seed, value_advantage_gbp=value)
             for seed, value in zip(floor["seeds"], values)]
    return dict(floor, seeds=seeds)


def test_the_verdict_is_withheld_when_the_floors_own_redraws_reverse_it():
    """A verdict is stated only if it survives being asked of a different draw of the quantity.

    THE DEFECT IT PREVENTS. `value_advantage_gbp` is a SINGLE realisation; the bound beside it is
    how far that same quantity moves across the floor's re-draws. Comparing the two answers "did
    this draw land more than a spread from zero", not "is this figure distinguishable from zero".
    On the live world the answer moves with the seed -- £1,467.23 and £2,433.70 clear £991.46 and
    £450.99 does not -- so the page published `resolved: True` off a verdict a third of the
    re-draws reverse, with the number that reverses it two lines below in the same payload.

    WHY EVERY EARLIER CONTROL MISSED IT. Five mutation-proven guards sit on this block and all
    five ask whether the bound is the RIGHT bound: right world, right leg, right contrast, real
    timestamp, real seed rows. Every one is about the denominator's provenance. Nothing asked what
    the NUMERATOR is, so a correct bound correctly attached to a single draw passes all of them.

    TWO SUBJECTS, AND THE SECOND IS THE ONE THAT MAKES THIS A CONTROL. The straddling floor alone
    would be satisfied by a function that withheld unconditionally -- "never state a verdict"
    passes any assertion that no verdict was stated. The unanimous floor is the sole witness that
    the withholding is a JUDGEMENT and not a constant, and it is the direct analogue of the world
    and leg guards' sole witnesses in the sibling control.

    Fires on: withholding unconditionally; withholding only the unflattering direction; folding
    the withheld state into `bound_available: False` so a reader cannot tell "never measured"
    from "one draw's"; or dropping the range from the reason.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    admitted = dict(_load(NOISE_FLOOR_ONLY_LIVE),
                    redraw_scope=dict(_load(NOISE_FLOOR_ONLY_LIVE)["redraw_scope"],
                                      mode=gva.BOUNDING_REDRAW_MODE))

    # WITNESS A -- the re-draws straddle the bound they generate. These are the live artefact's
    # own three rows, which is why this needs no new compute leg.
    straddling = _floor_with_advantages(admitted, [1467.230551, 2433.696987, 450.9949])
    withheld = gva._current_world_contrast(current, superseded, straddling)
    assert withheld["bound_available"] is True, (
        "the straddling floor was refused outright, so this subject is witnessing the world or "
        "leg guard rather than the stability one: " + str(withheld.get("why_no_bound"))[:160])
    assert withheld["resolved"] is None, (
        "the page stated a verdict off a floor whose own re-draws reverse it -- the verdict is a "
        "property of which draw the three-arm run made, not of the company")
    assert withheld["verdict_withheld_because"], (
        "the verdict was withheld with no reason, so `resolved: None` now means both 'never "
        "measured' and 'one draw's' and a reader cannot tell them apart")
    # THE RANGE THAT REVERSES IT REACHES THE READER, not just the fact of withholding.
    for edge in ("£451", "£2,434"):
        assert edge in withheld["verdict_withheld_because"], (
            "the reason withheld the range that reverses the verdict: "
            + withheld["verdict_withheld_because"])

    # WITNESS B -- SOLE WITNESS THAT THE WITHHOLDING IS A JUDGEMENT. Every re-draw clears its own
    # spread by two orders of magnitude, so there is nothing unstable to find and a verdict is due.
    unanimous = _floor_with_advantages(admitted, [10000.0, 10100.0, 10200.0])
    stated = gva._current_world_contrast(current, superseded, unanimous)
    assert stated["bound_available"] is True, (
        "the unanimous floor was refused, so it cannot witness that withholding is conditional")
    assert stated["resolved"] in (True, False), (
        "no verdict was stated off a floor whose every re-draw agrees, so the block withholds "
        "unconditionally and the guard above is an equivalence")
    assert stated["verdict_withheld_because"] is None, (
        "a reason for withholding was published beside a stated verdict")


def test_MUTATION_the_stability_guard_fails_on_its_own_witness_and_only_there():
    """Removing the stability guard must red on the straddling floor and change nothing else.

    Run rather than argued: this block's history is a control that asserted a constant, and a
    constant satisfies any assertion written against it. The mutation modelled here is the
    well-meaning one -- "the bound is the right bound, so the verdict follows" -- which is exactly
    the reasoning that shipped `resolved: True` on 2026-09-03.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    admitted = dict(_load(NOISE_FLOOR_ONLY_LIVE),
                    redraw_scope=dict(_load(NOISE_FLOOR_ONLY_LIVE)["redraw_scope"],
                                      mode=gva.BOUNDING_REDRAW_MODE))
    straddling = _floor_with_advantages(admitted, [1467.230551, 2433.696987, 450.9949])
    unanimous = _floor_with_advantages(admitted, [10000.0, 10100.0, 10200.0])

    # THE MUTANT'S ANSWER, computed the way the block did before the guard existed: the raw
    # comparison of the point estimate to the spread, with no question asked of its stability.
    bound = gva._current_world_bound(straddling, current, live)
    unguarded = gva._resolvable(current["level_vs_selection"]["value_advantage_gbp"],
                                bound.get("bound"))
    assert unguarded is True, (
        "the straddling floor does not resolve even without the guard, so it cannot witness the "
        "guard's removal -- this subject proves nothing")
    assert gva._current_world_contrast(current, superseded, straddling)["resolved"] is None, (
        "the stability guard is not what withholds the verdict on the straddling floor")

    # AND THE GUARD IS SILENT WHERE IT SHOULD BE. Same mutation, unanimous witness, no change --
    # which is what stops the guard being "withhold everything" wearing a reason.
    assert gva._verdict_stability(unanimous, gva._current_world_bound(
        unanimous, current, live).get("bound"))["stable"] is True, (
        "the guard reports the unanimous floor unstable, so it fires on every subject and its "
        "red on the straddling one carries no information")
    assert gva._current_world_contrast(current, superseded, unanimous)["resolved"] is not None, (
        "the guard withheld a verdict on a floor whose re-draws all agree")


def test_the_world_digest_tracks_the_departure_level_and_not_the_commit(monkeypatch):
    """The digest must move when the LEVEL moves, and only then.

    A hash of the commit would differ from HEAD for a docstring edit -- the ordinary case,
    carrying no signal -- while a re-fit that changed every departure rate on the same commit
    would pass. Keyed to the property: the digest covers every year the accessor answers for.

    Fires on: digesting anything that is not the anchor block; or excluding the DECLARED years,
    which would make a change to 2022's `NO_LEVEL_CORRECTION` invisible.
    """
    from simulation import departure_level_anchor as dla

    before = dla.world_level_identity()["digest"]
    assert dla.world_level_identity()["digest"] == before, "the digest is not stable"

    moved = {**dla.YEAR_LEVEL_ANCHOR, 2019: dla.YEAR_LEVEL_ANCHOR[2019] + 0.5}
    monkeypatch.setattr(dla, "YEAR_LEVEL_ANCHOR", moved)
    assert dla.world_level_identity()["digest"] != before, (
        "moving a fitted anchor by 0.5 left the world digest unchanged -- the digest is not "
        "keyed to the departure level")

    # A DECLARED year counts too: 2022 takes `NO_LEVEL_CORRECTION`, and a change there moves the
    # world exactly as a fitted year does.
    monkeypatch.setattr(dla, "YEAR_LEVEL_ANCHOR", dict(dla.YEAR_LEVEL_ANCHOR))
    monkeypatch.setattr(dla, "NO_LEVEL_CORRECTION", 1.5)
    assert dla.world_level_identity()["digest"] != before, (
        "a change to the value a DECLARED year takes left the world digest unchanged")


def test_a_remedy_that_splits_another_quantity_is_refused_rather_than_restated():
    """THE DEFECT (2026-09-03): the page reconciled the floor decomposition against the run on the
    BOOK and on the WORLD, and never on the QUANTITY it decomposes. Both passed, their conjunction
    read as "this evidence describes this figure", and the split published was of `selection_gbp`
    while the figure it sat beside -- and the bound `_current_world_contrast` puts under it since
    `a70cc11e1` -- was `value_advantage_gbp`.

    IT IS NOT A ROUNDING DIFFERENCE. On the 08-29 family, the one seed family where all three floor
    legs exist, the rest-of-book leg's spread is 0.21 on `selection_gbp` and 554.21 on
    `value_advantage_gbp`: `irreducible_sd_gbp` quoted across the two is out by 2,623x, and
    `priced_share_of_variance` falls from 1.000000 to 0.359106.

    TWO GUARDS, EACH WITH A SOLE WITNESS, so neither is an equivalence the other covers -- and BOTH
    witnesses are measured on THIS page's book, so the book reconciliation passes on each and this
    control is the only thing that can red:
      * MISSING    -- no `contrast` key at all. This is the real artefact's state.
      * MISMATCHED -- declares `selection_gbp` against a `value_advantage_gbp` page.

    INDEPENDENT OF THE BOOK CAVEAT ON PURPOSE. `measured_on_this_page_s_book` is false today, so
    the book guard already withholds the remedy and nothing a reader sees is wrong because of this.
    The book guard is what MASKS it: re-running the decomposition on the current book is owed work,
    and the moment it lands the book caveat lifts and the remedy publishes on the wrong quantity
    with nothing left withholding it. That is why the fixtures here set the books EQUAL.

    R15 -- the mutations, each run and reverted under `python3 -B`:
      * return `None` unconditionally from `_decomposition_is_the_same_contrast` (the defect as it
        shipped) -> both the missing and mismatched legs red, the remedy comes back on the wrong
        quantity.
      * treat an absent declaration as agreement (`if declared is None: return None`) -> the
        MISSING leg reds and the MISMATCHED leg does not, which is the FAIL-SILENT half and the
        state the real artefact is actually in.
      * infer the contrast from the `what_this_is` prose instead of the declaration -> the MISSING
        leg reds, because a declaration nobody made is manufactured from a sentence.
      * drop the `different_contrast` refusal from `_what_would_resolve_it` and leave the keys on
        the payload -> both legs red, which is the point: a verdict computed and never read by
        anything that publishes is a fail-silent, not a control.
    The null rung is `declared`, which must KEEP the remedy: a control that only ever demands the
    remedy be absent is satisfied by deleting the remedy.
    """
    # THE NULL RUNG. A decomposition of this page's own contrast must still price the remedy.
    declared = _withheld_headline(_decomposition(0.85, resolvable=True))
    assert "larger SETTLED BOOK" in declared, (
        "the null rung: a decomposition of this page's own contrast was refused anyway, so this "
        "control would be satisfied by deleting the remedy entirely: {}".format(declared))
    assert "DIFFERENT QUANTITY" not in declared and "WHICH QUANTITY" not in declared, (
        "a decomposition of this page's own contrast was accused of splitting another: {}"
        .format(declared))

    # SOLE WITNESS 1 -- MISSING. The real artefact's state: same book, no declaration.
    missing = dict(_decomposition(0.85, resolvable=True))
    missing.pop("contrast")
    assert gva._decomposition_is_the_same_book(missing, _load(THREE_ARM)) is None, (
        "the fixture must pass the BOOK guard, or this control is not the sole reason it reds")
    missing_headline = _withheld_headline(missing)
    assert "larger SETTLED BOOK" not in missing_headline, (
        "a remedy whose evidence never said which quantity it splits was restated as though it "
        "described this page's figure -- the defect as it shipped: {}".format(missing_headline))
    assert "WHICH QUANTITY" in missing_headline and "has not been established" in missing_headline, (
        "the refusal must NAME its reason and leave the remedy explicitly unestablished; a "
        "silently dropped remedy reads as a question nobody asked: {}".format(missing_headline))

    # SOLE WITNESS 2 -- MISMATCHED. Same book, a declaration, and it is the wrong quantity.
    mismatched = dict(_decomposition(0.85, resolvable=True), contrast="selection_gbp")
    assert gva._decomposition_is_the_same_book(mismatched, _load(THREE_ARM)) is None, (
        "the fixture must pass the BOOK guard, or this control is not the sole reason it reds")
    assert gva._decomposition_contrast(mismatched) == "selection_gbp", (
        "the mismatched witness must CARRY a declaration, or it is a second copy of the missing "
        "one and one of these two legs is an equivalence")
    mismatched_headline = _withheld_headline(mismatched)
    assert "larger SETTLED BOOK" not in mismatched_headline, (
        "a remedy priced on a quantity this page does not publish was restated as though it "
        "described the one it does: {}".format(mismatched_headline))
    assert "DIFFERENT QUANTITY" in mismatched_headline, (
        "the refusal must name that the quantity differs: {}".format(mismatched_headline))
    assert ("selection_gbp" in mismatched_headline
            and gva.PAGE_FIGURE_CONTRAST in mismatched_headline), (
        "the refusal states neither quantity, so a reader cannot check the comparison it refuses "
        "on: {}".format(mismatched_headline))


def test_the_contrast_reconciliation_is_published_beside_the_book_one_not_folded_into_it():
    """The two reconciliations must reach the payload as SEPARATE verdicts.

    THE DEFECT THIS WOULD CATCH. Folding the quantity question into `measured_on_this_page_s_book`
    would make re-running the decomposition on the current book -- which is owed, and which this
    lane is doing -- clear BOTH, and the cross-contrast read would ship the moment the book caveat
    lifted. Two questions, two answers, on the surface.

    R15: merge the two caveats into one key -> this reds. Publish the contrast verdict but stop
    reading it in `_what_would_resolve_it` -> the sibling test above reds.
    """
    art = _load(THREE_ARM)
    same_book_wrong_contrast = dict(_decomposition(0.85, resolvable=True),
                                    contrast="selection_gbp")
    block = gva.build(art, _floor_with_spread(2577.80), _load(RUN_OUTPUT),
                      same_book_wrong_contrast)["floor_decomposition"]
    assert block["measured_on_this_page_s_book"] is True, (
        "the fixture is on this page's book; if this is False the sole-witness property is gone")
    assert block["measured_on_this_page_s_contrast"] is False, (
        "the page published a decomposition of another quantity without saying so")
    assert block["contrast_it_decomposes"] == "selection_gbp", (
        "the page does not say which quantity the split below it is of")
    assert block["different_book_caveat"] is None, (
        "the book caveat fired on a same-book fixture, so the two verdicts are not independent")
    assert block["different_contrast_caveat"], (
        "the contrast verdict was computed and left empty -- a verdict nothing publishes is a "
        "fail-silent, not a control")
