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

import ast
import copy
import datetime
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
#: THE RUN THAT NAMES NO WORLD -- sole witness for every control whose subject is a run whose
#: departure level is UNKNOWN. This was `THREE_ARM` until 2026-09-09, when the 09-08b run was
#: promoted onto that path and brought a `world_identity` with it; the property was held by
#: accident and two controls lost the only subject that can reach their refusal. World stamping
#: began on 2026-09-03, so every run before it is permanently unstamped and this name cannot expire.
THREE_ARM_NO_WORLD = (
    PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm_20260831.json")
#: THE RUN THAT PREDATES THE CURRENT-WORLD RE-TAKE -- sole witness for every control that needs
#: `_current_world_clause` to actually COMPOSE something. The clause is silent unless the
#: current-world block is the LATER of the two runs the page carries, so a control asserting on
#: its prose must pair `CURRENT_WORLD_THREE_ARM_PATH` with a run stamped before it.
#:
#: THE SAME FILE AS `THREE_ARM_NO_WORLD` AND A SEPARATE NAME ON PURPOSE. What is wanted here is
#: the STAMP; what is wanted there is the absent world. Two properties that happen to live in one
#: artefact today, and reaching through one name for the other property is how a control silently
#: stops measuring what it says it measures the day the two part company. This was `THREE_ARM`
#: until 2026-09-09, which held the ordering by accident until the 21:01Z re-take was promoted
#: onto it -- and then a control went red on a page that had become more honest.
THREE_ARM_BEFORE_THE_CURRENT_WORLD_RUN = (
    PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm_20260831.json")
NOISE_FLOOR = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_noise_floor.json"



#: The run the tests below have the site publishing. The commit and the START STAMP both matter:
#: the stamp is what `_run_started_at` orders two runs by, and the order leg is the only one the
#: provenance's one-cycle lag survives.
_SHOWN = "abc1234"
_SHOWN_RUN = "run_output_abc1234_20260909T210648Z.json"


@pytest.fixture
def the_site_publishes(monkeypatch, tmp_path):
    """Point the generator's dashboard at a figure AND a run identity of the test's choosing.

    WHY THIS SHAPE (2026-09-10, second sitting). `_is_the_published_supplier`'s subject is
    `site/data/dashboard.json` now -- both the figure and the run it came from, out of the one
    committed file. Until this afternoon the figure came from here and the identity came from
    `docs/reports/run_output_latest.json`, which is in no publish, so the verdict alternated by
    which tree regenerated the feed. A test that sets a figure without setting `meta` is
    exercising the "cannot name its run" refusal and not the branch it names.
    """
    def _set(net, run_id=_SHOWN_RUN, commit=_SHOWN, commit_source="run_stamp"):
        path = tmp_path / "dashboard.json"
        meta = {"git_commit_source": commit_source}
        if run_id is not None:
            meta["source_file"] = run_id
        if commit is not None:
            meta["git_commit"] = commit
        path.write_text(json.dumps({"portfolio": {"net_margin_gbp": net}, "meta": meta}),
                        encoding="utf-8")
        monkeypatch.setattr(gva, "DASHBOARD_PATH", path)
        return path
    return _set


@pytest.fixture
def the_site_last_verified(monkeypatch, tmp_path):
    """Point the generator's publish provenance at the run the site last VERIFIED.

    NOT THE IDENTITY THE CLAIM RESTS ON, and that is an ordering fact rather than a preference:
    `record_verified` stamps this file after `value_arms.json` is generated in the same publish
    cycle, so at the moment the feed reads it, it names the PREVIOUS run. It is used for one leg
    only -- whether the dashboard's run STARTED before this one, which is the mtime-glob defect in
    `generate_dashboard_data._find_latest_run_json` becoming visible.
    """
    def _verified(run_id=_SHOWN_RUN, commit=_SHOWN):
        path = tmp_path / "publish_provenance.json"
        path.write_text(json.dumps({"showing_run": {"git_commit": commit, "run_id": run_id}}),
                        encoding="utf-8")
        monkeypatch.setattr(gva, "PUBLISH_PROVENANCE_PATH", path)
        return path
    return _verified


def _load(path: Path) -> dict:
    if not path.is_file():
        pytest.fail("{} is missing -- this control's subject is UNAVAILABLE, and an unavailable "
                    "check is a FAILED check (R15)".format(path))
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def real() -> dict:
    return gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))


@pytest.fixture
def real_20260829() -> dict:
    """The page as built from the run whose BELIEF RANKED BACKWARDS -- see `THREE_ARM_20260829`.

    The reversal tables below are descriptions of that run and stay pinned to it. The 2026-08-31
    run ranks the right way round (AUC 0.13 -> 0.655), so asserting the reversal through the
    canonical path would be a control asserting the model stays bad.
    """
    return gva.build(_load(THREE_ARM_20260829), _load(NOISE_FLOOR))


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
    out = gva.build(art, _load(NOISE_FLOOR))

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
    out = gva.build(art, _load(NOISE_FLOOR))

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
    eb = gva.build(art, _load(NOISE_FLOOR))["error_bar"]

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
    out = gva.build(artefact, None)
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
    out = gva.build(_load(THREE_ARM), None)
    eb = out["error_bar"]
    assert eb["available"] is False
    assert eb["reason"]
    assert "stdev_gbp" not in eb, "an absent noise floor still published a standard deviation"


def test_a_one_seed_noise_floor_is_not_a_spread():
    out = gva.build(_load(THREE_ARM), {"selection_gbp_spread": {"n": 1, "stdev": 0.0,
                                                               "min": -174.5, "max": -174.5}})
    assert out["error_bar"]["available"] is False, (
        "a single seed was published as a measured spread of zero")


# ── WHICH RULE ADMITTED THE FLOOR: the pairing itself, not a caveat on it ────────────────────
#
# THE DEFECT (SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_PAIRING_RULE_IS_A_
# STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09). Every directional claim this feed makes is
# gated on a floor being paired to the figure it bounds, and the pairing rule was a comparison of
# two `generated_at` stamps -- a proxy for "was this spread drawn over the book this figure is
# made of" that cannot see a book at all. `run_value_cycle_ab.floor_book_identity` answers the
# real question and had ONE caller and NO reader for a day, so the defect stayed live where a
# reader meets it. These controls are the reader.

def _declared(segments):
    """One arm's or one floor's DECLARED half, in the producer's own three fields."""
    return {"served_segments": list(segments),
            "served_segments_resolved_from": "curriculum",
            "served_segments_override_env": None}


def _floor_declaring(segments, realised=None):
    """The real nine-seed floor, given the `book_identity` block its producer now writes.

    KEYED TO THE PROPERTY AND NOT TO TODAY'S ARTEFACT. The block is the shape
    `floor_book_identity` returns, and the day a real floor carries one these read it without
    changing.

    THAT DAY WAS 2026-09-11, and the sentence this docstring used to open with -- "no floor on
    disk carries a book identity yet, every one of them predates the writer" -- went false when
    the 09-10 nine-seed floor was promoted to `NOISE_FLOOR`. It is the FIRST floor on disk to
    declare its own book. The prediction the sentence was making held exactly: these helpers read
    it without changing. What did NOT survive was a control that had quietly borrowed the absence
    as a witness -- see `_floor_without_a_book` below.
    """
    floor = copy.deepcopy(_load(NOISE_FLOOR))
    floor["book_identity"] = {
        "declared": _declared(segments),
        "seeds_reconciled": len(floor.get("seeds") or []),
        "seeds_that_recorded_no_book": 0,
        "unavailable_because": None,
        "realised_across_seeds": realised or {},
        "how_a_consumer_should_pair_this": "Pair on `declared` and never on `realised_across_seeds`.",
    }
    return floor


def _floor_without_a_book():
    """A floor that declares NO book identity -- the input the stamp-proxy branch exists for.

    WHY THIS IS A CONSTRUCTED WITNESS AND NOT THE ARTEFACT ON DISK (2026-09-11). Until the 09-10
    floor landed, every floor on disk lacked a `book_identity` block, so `_load(NOISE_FLOOR)`
    reached the proxy branch for free and the partition control below used it as its proxy
    witness. That was borrowing an ABSENCE as a witness: the moment a floor carried a book -- the
    artefact becoming MORE honest, not less -- the witness silently stopped standing for the
    branch it was there to reach, and the control went red for a reason that was not a defect.
    This helper makes the absence deliberate, so the proxy branch keeps a witness no promotion can
    take away.
    """
    floor = copy.deepcopy(_load(NOISE_FLOOR))
    floor.pop("book_identity", None)
    return floor


def _the_runs_own_segments() -> list:
    arms = _load(THREE_ARM)["book_identity"]
    return arms["control_arm"]["served_segments"]


def test_a_floor_that_declares_the_runs_OWN_book_is_admitted_ON_THE_BOOK_not_the_date():
    """The rule the stamp was standing in for, once the artefact can answer it."""
    admission = gva._floor_admission(_floor_declaring(_the_runs_own_segments()), _load(THREE_ARM))
    assert admission["rule"] == gva.ADMITTED_ON_THE_DECLARED_BOOK, (
        "a floor that names the book it was drawn over was still admitted on its date: "
        "{!r}".format(admission["rule"]))
    assert admission["admitted"] is True and admission["refusal"] is None
    assert admission["figure_declared_book"]["served_segments"] == _the_runs_own_segments()


def test_a_floor_drawn_over_a_DIFFERENT_book_is_refused_however_recent_it_is():
    """The direction the stamp proxy is wrong in that costs the page most.

    This floor is NEWER than the run it would bound, so `_staleness_caveat` admits it in silence
    and every directional claim on the page rests on a spread measured over another population.
    """
    floor = _floor_declaring(["resi"])
    three_arm = _load(THREE_ARM)
    assert gva._staleness_caveat(floor, three_arm) is None, (
        "this control's whole subject is a floor the STAMP rule admits -- if the stamp already "
        "refused it, the book rule is not what is being measured here")

    admission = gva._floor_admission(floor, three_arm)
    assert admission["admitted"] is False and admission["refusal"], (
        "a spread drawn over a different book was admitted as a confidence interval")
    assert "DIFFERENT BOOK" in admission["refusal"]

    out = gva.build(three_arm, floor)
    bounds = out["contrast_bounds"]
    assert bounds["available"] is False, (
        "the page still took a DIRECTION from a spread measured over another population")
    assert bounds["admitted_by"] == gva.ADMITTED_ON_THE_DECLARED_BOOK
    # STATES rather than refuses in the error bar, and refuses in the block that takes a sign --
    # the split `world_measured_in` already makes, for the same reason.
    assert out["error_bar"]["floor_admission"]["refusal"] == admission["refusal"]


def test_the_pairing_is_on_the_DECLARED_half_and_never_on_the_realised_counts():
    """The producer's own instruction, and a consumer that got it wrong would refuse every re-run.

    Two floors of the SAME book differ in their realised counts by construction: moving the
    price-sensitivity draw moves who churns and therefore who settles. A consumer pairing on those
    would be a control that goes red when the world behaves normally.
    """
    segments = _the_runs_own_segments()
    lean = _floor_declaring(segments, realised={"billing_accounts_settled_in_window":
                                                {"min": 180, "max": 181, "n": 9}})
    fat = _floor_declaring(segments, realised={"billing_accounts_settled_in_window":
                                               {"min": 900, "max": 1100, "n": 9}})
    three_arm = _load(THREE_ARM)
    assert (gva._floor_admission(lean, three_arm)["admitted"]
            is gva._floor_admission(fat, three_arm)["admitted"] is True), (
        "the realised account counts moved the verdict, so an honest re-run of the same book "
        "would be refused as a different one")


def test_a_run_whose_arms_disagree_about_their_book_falls_CLOSED_to_the_stamp():
    """An unestablished figure-side population must not read as agreement with the floor."""
    three_arm = copy.deepcopy(_load(THREE_ARM))
    three_arm["book_identity"]["value_arm"] = _declared(["resi"])
    admission = gva._floor_admission(_floor_declaring(_the_runs_own_segments()), three_arm)
    assert admission["rule"] == gva.ADMITTED_ON_A_STAMP_PROXY, (
        "the floor was paired to a run whose own arms declare different books")
    assert "different books between them" in admission["why_this_rule"]


def test_a_run_that_recorded_no_book_at_an_arm_falls_CLOSED_to_the_stamp():
    """`book_identity` fails closed to a `None` segment list with its reason beside it; a consumer
    that read that as "no segments" would pair on an absence."""
    three_arm = copy.deepcopy(_load(THREE_ARM))
    three_arm["book_identity"]["level_arm"] = dict(
        three_arm["book_identity"]["level_arm"], served_segments=None)
    admission = gva._floor_admission(_floor_declaring(_the_runs_own_segments()), three_arm)
    assert admission["rule"] == gva.ADMITTED_ON_A_STAMP_PROXY
    assert "level_arm" in admission["why_this_rule"]


def test_the_floor_on_disk_names_the_stamp_as_a_PROXY_rather_than_claiming_the_book(real):
    """THE STATE THE PAGE IS ACTUALLY IN, and it is published rather than assumed.

    Not pinned to that state: the day a floor carrying a book identity is promoted this control
    keeps passing, because what it asserts is that the rule is NAMED and that a proxy says it is
    one. `test_a_floor_that_declares_the_runs_OWN_book...` owns the other branch.
    """
    admission = real["error_bar"]["floor_admission"]
    assert admission["rule"] in (gva.ADMITTED_ON_THE_DECLARED_BOOK, gva.ADMITTED_ON_A_STAMP_PROXY)
    if admission["rule"] == gva.ADMITTED_ON_A_STAMP_PROXY:
        assert "proxy" in admission["why_this_rule"], (
            "the page's bound is admitted by a date and the page does not say the date is "
            "standing in for the question a reader would assume was asked")
        assert "BOTH directions" in admission["why_this_rule"]


def test_EVERY_admission_outcome_IS_REACHABLE_from_this_feeds_own_inputs():
    """One control over the whole partition, because a rule that only ever returns its fail-closed
    branch passes every per-branch test above and tells a reader nothing.

    MUTATION: make `_floor_admission` return the proxy branch unconditionally and this is the only
    control here that reds -- the four above go green on a rule that has stopped asking.

    EVERY WITNESS IS CONSTRUCTED FROM THE PROPERTY IT STANDS FOR (2026-09-11). It used to reach the
    proxy branch through `_load(NOISE_FLOOR)` unedited, which worked only because no floor on disk
    declared a book. Promoting the 09-10 floor -- which does -- moved that witness onto the
    declared-book branch and reds this control while the rule underneath it was working perfectly.
    A control that goes red when its subject gets MORE honest is keyed to today's answer, and the
    fix is `_floor_without_a_book`, not a wider expected set.
    """
    three_arm = _load(THREE_ARM)
    disagreeing = copy.deepcopy(three_arm)
    disagreeing["book_identity"]["value_arm"] = _declared(["resi"])
    outcomes = {
        (gva._floor_admission(_floor_declaring(_the_runs_own_segments()), three_arm)["rule"],
         gva._floor_admission(_floor_declaring(_the_runs_own_segments()), three_arm)["admitted"]),
        (gva._floor_admission(_floor_declaring(["resi"]), three_arm)["rule"],
         gva._floor_admission(_floor_declaring(["resi"]), three_arm)["admitted"]),
        # THE PROXY BRANCH, reached from BOTH of the two ways a pairing can fail to establish a
        # book: the FLOOR side declaring none, and the FIGURE side's own arms disagreeing. Two
        # witnesses and not one, because they are different inputs to the same fail-closed rule
        # and either could rot alone.
        gva._floor_admission(_floor_without_a_book(), three_arm)["rule"],
        gva._floor_admission(_floor_declaring(_the_runs_own_segments()), disagreeing)["rule"],
    }
    assert outcomes == {
        (gva.ADMITTED_ON_THE_DECLARED_BOOK, True),
        (gva.ADMITTED_ON_THE_DECLARED_BOOK, False),
        gva.ADMITTED_ON_A_STAMP_PROXY,
    }, "the admission rule cannot reach all three of its outcomes: {!r}".format(outcomes)


# ── WHICH CODE DREW EACH SIDE OF THE BOUND ──────────────────────────────────────────────────
#
# THE DEFECT (2026-09-09). `CURRENT_WORLD_NOISE_FLOOR_PATH` moved alone onto the nine-seed floor,
# which was the right repair for a worse defect -- two selection spreads at two sample sizes on
# one page, n=9 in `contrast_bounds` and n=3 in the leg that is the whole thesis. It left the
# floor at `c066c114b` and the arms it bounds at `04361d6c7`, and the page said nothing: the split
# was admitted in a source comment, where the measurement that sizes it (the same seed in the same
# world returns a `selection_gbp` +38.96..+61.38 apart under the two trees) is unreachable by any
# reader of the page. Seven guards ask about this pairing -- world, leg, contrast, timestamp, seed
# rows, staleness, book -- and none of them asks about the tree.


def _floor_produced_by(commit):
    """The real floor with its producing-commit stamp set, or stripped when `commit` is None.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ARTEFACTS. Both live pairings on this feed are split
    across two trees TODAY, so a control that read the artefacts as they are would be green on the
    live split and equally green on a function that returned `same_tree: False` unconditionally.
    Every case below is therefore constructed, and the wiring control further down is what ties
    the constructed cases to what the feed actually publishes.
    """
    floor = copy.deepcopy(_load(NOISE_FLOOR))
    if commit is None:
        floor.pop("producing_commit", None)
    else:
        floor["producing_commit"] = dict(floor.get("producing_commit") or {}, commit=commit)
    return floor


def _the_runs_own_commit() -> str:
    return _load(THREE_ARM)["producing_commit"]["commit"]


def test_a_bound_drawn_by_a_DIFFERENT_TREE_from_the_figure_says_so_and_names_both():
    """The live state on 2026-09-09, made reachable as a property rather than read off disk."""
    mine = _the_runs_own_commit()
    other = ("f" * 40) if mine != "f" * 40 else ("e" * 40)
    pairing = gva._floor_tree_pairing(_floor_produced_by(other), _load(THREE_ARM))
    assert pairing["same_tree"] is False, (
        "a floor and the arms it bounds came from different trees and the page called it a "
        "match: {!r}".format(pairing["same_tree"]))
    assert other[:9] in pairing["why_this_rule"] and mine[:9] in pairing["why_this_rule"], (
        "the page says the two trees differ and does not name them, so a reader cannot check "
        "which two: {!r}".format(pairing["why_this_rule"]))
    assert pairing["caveat"], "the split is stated with no reading of what it costs"


def test_a_bound_drawn_by_the_SAME_TREE_still_gets_a_sentence():
    """A reader told nothing when the trees match cannot tell that silence from an unasked
    question. This is the branch that makes the amber one legible."""
    mine = _the_runs_own_commit()
    pairing = gva._floor_tree_pairing(_floor_produced_by(mine), _load(THREE_ARM))
    assert pairing["same_tree"] is True
    assert pairing["caveat"] is None, "a matched pairing carries a caveat about nothing"
    assert mine[:9] in pairing["why_this_rule"] and "DIFFERENT CODE" not in pairing["why_this_rule"]


def test_an_UNSTAMPED_side_reads_as_UNKNOWN_and_never_as_a_match():
    """The fail-open this function would have if absence defaulted to agreement.

    The oldest artefacts on this page predate the producing-commit stamp entirely, so defaulting a
    missing stamp to `same_tree: True` would render them as the cleanest pairing on the page --
    absence wearing the flattering answer, which is this repository's own named defect.
    """
    pairing = gva._floor_tree_pairing(_floor_produced_by(None), _load(THREE_ARM))
    assert pairing["same_tree"] is None and pairing["rule"] == "unstamped"
    assert pairing["caveat"], "an unknowable pairing is published as a silence"


def test_EVERY_tree_pairing_OUTCOME_IS_REACHABLE_from_this_feeds_own_inputs():
    """One control over the whole partition, because a function that returns one branch always
    passes all three tests above.

    MUTATION: return the `same_tree: False` branch unconditionally -- the live artefacts are split
    today, so the feed looks correct, the split test above stays green, and only this reds.
    """
    mine = _the_runs_own_commit()
    other = ("f" * 40) if mine != "f" * 40 else ("e" * 40)
    arms = _load(THREE_ARM)
    outcomes = {
        (gva._floor_tree_pairing(_floor_produced_by(mine), arms)["rule"],
         gva._floor_tree_pairing(_floor_produced_by(mine), arms)["same_tree"]),
        (gva._floor_tree_pairing(_floor_produced_by(other), arms)["rule"],
         gva._floor_tree_pairing(_floor_produced_by(other), arms)["same_tree"]),
        (gva._floor_tree_pairing(_floor_produced_by(None), arms)["rule"],
         gva._floor_tree_pairing(_floor_produced_by(None), arms)["same_tree"]),
    }
    assert outcomes == {("producing_commit", True), ("producing_commit", False),
                        ("unstamped", None)}, (
        "the tree pairing cannot reach all three of its outcomes: {!r}".format(outcomes))


def _the_feed_with_its_current_world() -> dict:
    """`real` omits the two current-world artefacts, so its `current_world` is an ABSENCE.

    A wiring control run against that fixture asks nothing of the block it exists to check -- it
    would have gone green on the day the block was unavailable and on every day after. This builds
    the production shape: all four artefacts, through `build`, the same call `generate` makes.
    """
    return gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), None,
                     _load(gva.CURRENT_WORLD_THREE_ARM_PATH),
                     _load(gva.CURRENT_WORLD_NOISE_FLOOR_PATH))


def test_BOTH_bounds_on_the_real_feed_CARRY_a_tree_pairing(real):
    """WIRING, not arithmetic. Every test above calls the function directly and is blind to
    whether `build()` reaches it -- the exact shape that let `_floor_admission`'s producer-side
    answer sit built-and-unwired while the defect stayed live on the surface.

    Asserts the FIELD and its keys, never today's verdict: pinning `same_tree is False` here would
    go red on the day the arms are re-run under the floor's tree, which is the day the page gets
    MORE honest.
    """
    live = _the_feed_with_its_current_world()
    cw = live.get("current_world") or {}
    assert cw.get("available"), (
        "there is no current-world block to check, so half this control has no subject: "
        "{}".format(cw.get("why_not")))
    for where, block in (("error_bar", real.get("error_bar") or {}), ("current_world", cw)):
        key = "floor_tree_pairing" if where == "error_bar" else "bound_tree_pairing"
        pairing = block.get(key)
        assert isinstance(pairing, dict), (
            "the {} block publishes a bound and does not say which tree drew it".format(where))
        assert set(pairing) >= {"rule", "same_tree", "floor_producing_commit",
                                "figure_producing_commit", "why_this_rule", "caveat"}, (
            "{}.{} is short of the keys a reader and a control both need: {!r}".format(
                where, key, sorted(pairing)))
        assert pairing["why_this_rule"], (
            "{}.{} states no sentence, so the page asks the question and publishes no "
            "answer".format(where, key))
        assert (pairing["caveat"] is None) == (pairing["same_tree"] is True), (
            "{}.{} carries a caveat that does not follow its own verdict: {!r} / {!r}".format(
                where, key, pairing["same_tree"], pairing["caveat"]))


def test_the_tree_pairing_is_published_ONCE_per_block_and_not_once_per_leg():
    """The three legs share one floor and one arms run, so the answer is one answer.

    Rendering it per leg would put one sentence in three places, which is the shape
    `_the_legs_own_regions` in the site door already refuses for the reason it gives: a reader
    cannot tell where one leg's statement ends and the next begins.
    """
    cw = _the_feed_with_its_current_world().get("current_world") or {}
    assert cw.get("selection_leg"), "there are no legs here, so this control has no subject"
    for leg in ("selection_leg", "level_leg"):
        assert "bound_tree_pairing" not in (cw.get(leg) or {}), (
            "the tree pairing is published on {} as well as on the block, so the page states one "
            "answer three times".format(leg))


# ── THE CLAIM THAT COULD ROT: is the published supplier the baseline arm? ────────────────────

def test_the_published_supplier_claim_is_HONEST_whichever_state_the_tree_is_in(real):
    """The claim is checked and states what it can support — never an unstated pass.

    THIS USED TO PIN `same_supplier is True` as LIVE STATE, and that is the shape the day's other
    controls kept being caught by: it passes on whatever the working tree happens to hold and goes
    red when the tree becomes MORE honest. What it checks now is that the feed says the matching
    thing in each of the three cases.
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


def test_every_input_to_the_published_supplier_claim_IS_IN_THE_PUBLISH_SURFACE(real):
    """THE DEFECT THIS WHOLE REPAIR IS ABOUT, keyed to the property and not to today's bytes.

    For nine days this check read `docs/reports/run_output_latest.json` -- a path
    `background/sim_runner` refreshes on disk after every run and no publish commits. Its working
    copy was the published run; its committed copy was weeks behind; and the SAME generator on the
    SAME code published opposite sentences to the reader depending on which tree regenerated the
    feed. Six consecutive commits to `site/data/value_arms.json`: checked=False/131,289.34,
    True/147,886.78, True, False, True, False.

    So the property is not "the answer is currently X". It is that every file the claim is derived
    from is one the publish cycle COMMITS -- which is what makes the verdict a property of the
    commit rather than of the tree. This test reads the paths the module actually opens, extracts
    each one from HEAD, and requires the claim to come out the same against the committed bytes as
    against the working ones.

    Fires on: any future input to this claim that is not in the publish surface. It would have
    been red on every commit for the nine days before 2026-09-10, and it is why
    `RUN_OUTPUT_PATH` is gone from this module rather than merely demoted.
    """
    import subprocess
    paths = {"DASHBOARD_PATH": gva.DASHBOARD_PATH,
             "PUBLISH_PROVENANCE_PATH": gva.PUBLISH_PROVENANCE_PATH}
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--"]
                             + [str(p) for p in paths.values()],
                             cwd=str(PROJECT), capture_output=True, text=True)
    assert tracked.returncode == 0, (
        "an input to the published-supplier claim is not tracked by git, so the claim is a "
        "property of this working tree and not of the commit: {}".format(tracked.stderr.strip()))


def test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes(
        real, monkeypatch, tmp_path):
    """The oscillation, killed at the only place it can be proved dead: run the check against the
    bytes a CLEAN CHECKOUT would hold and require the same verdict as the shared tree gives.

    Fires on: an input reverting to a path whose committed copy differs from its working copy.
    Under the pre-2026-09-10 subject this reddened with a £16,597.44 disagreement.
    """
    import subprocess
    for name in ("DASHBOARD_PATH", "PUBLISH_PROVENANCE_PATH"):
        live = getattr(gva, name)
        rel = live.relative_to(PROJECT)
        blob = subprocess.run(["git", "show", "HEAD:{}".format(rel.as_posix())],
                              cwd=str(PROJECT), capture_output=True, text=True)
        assert blob.returncode == 0, "{} is in no commit, so this claim cannot survive a clean " \
            "checkout".format(rel)
        at_head = tmp_path / rel.name
        at_head.write_text(blob.stdout, encoding="utf-8")
        monkeypatch.setattr(gva, name, at_head)

    from_head = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))[
        "realised"]["is_the_published_supplier"]
    live = real["realised"]["is_the_published_supplier"]
    for field in ("checked", "same_supplier", "statement"):
        assert from_head[field] == live[field], (
            "the published-supplier claim answers differently against HEAD's committed bytes than "
            "against the working tree, on `{}` -- the feed oscillates by which tree regenerated "
            "it:\n  HEAD:    {!r}\n  working: {!r}".format(field, from_head[field], live[field]))


def test_a_divergent_published_run_is_reported_as_a_divergence(
        real, the_site_publishes, the_site_last_verified):
    """THE LOAD-BEARING NULL. The day the site publishes a different run, the claim must invert
    itself and name both figures -- not quietly go on asserting an identity that has lapsed."""
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    the_site_last_verified()
    the_site_publishes(control + 40_000.0)
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))
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
    the_site_publishes(control)
    assert "The comparison below is against" in gva.build(
        _load(THREE_ARM), _load(NOISE_FLOOR))["headline"], (
        "the null rung: while the two DO match, the headline must make the claim -- otherwise the "
        "assertion above passes on a headline that never carries it")


def test_an_unreadable_dashboard_claims_nothing_either_way(real, monkeypatch, tmp_path):
    """FAIL CLOSED. The site's own figure is the whole subject now, so an unreadable dashboard is
    a claim that cannot be made -- never one that is quietly assumed.

    Fires on: a missing dashboard reading as agreement.
    """
    monkeypatch.setattr(gva, "DASHBOARD_PATH", tmp_path / "nope.json")
    pub = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))[
        "realised"]["is_the_published_supplier"]
    assert pub["checked"] is False and pub["same_supplier"] is None
    assert "could not be read" in pub["statement"]
    assert "IS the baseline" not in pub["statement"], (
        "an unread dashboard was treated as agreement -- fail-open on the check itself")


def test_a_penny_of_divergence_is_still_the_same_supplier(
        real, the_site_publishes, the_site_last_verified):
    """The null on the OTHER side: both figures are pounds summed from settlement records, so
    sub-penny float noise must not be reported as two different suppliers.

    THIS IS ALSO THE GATE'S OWN NULL RUNG. A guard that refuses everything passes every test that
    asks whether it refuses correctly, and the identity gate sits ahead of every other branch
    here. This is the one control that proves the gate can be PASSED -- delete the
    `state == "established"` route and it is what reddens.
    """
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    the_site_last_verified()
    the_site_publishes(control + 0.004)
    pub = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))[
        "realised"]["is_the_published_supplier"]
    assert pub["same_supplier"] is True
    assert pub["run_identity"]["state"] == "established", (
        "the claim was made without establishing that the figure IS the site's published one")


# ── the published PRECISION: three outcomes, because the site's figure is quantised ──────────


def test_a_gap_the_SITES_OWN_PRECISION_cannot_resolve_is_not_answered_either_way(
        real, the_site_publishes, the_site_last_verified):
    """`generate_dashboard_data._fmt` rounds the published net margin to the penny, so the figure
    this check reads differs from the run's own sum by up to HALF a penny while the baseline arm
    is full precision. Against a £0.01 tolerance that leaves a band where the verdict is decided
    by which way the rounding fell -- and stating either answer there is stating a distinction
    neither figure carries.

    THE FIX WAS A THIRD ANSWER AND NOT A WIDER TOLERANCE. Fires on: raising
    `SAME_SUPPLIER_TOLERANCE_GBP` to swallow the band, which buys agreement by knowing less; and
    on deleting the band, which answers at a precision the site does not publish.
    """
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    the_site_last_verified()
    the_site_publishes(control + 0.011)
    pub = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))[
        "realised"]["is_the_published_supplier"]

    assert pub["checked"] is False and pub["same_supplier"] is None, (
        "a gap inside the site's own rounding was answered as if the precision were there")
    assert "rounded to the" in pub["statement"] and "resolve" in pub["statement"], (
        "the refusal does not name the published precision, so a reader is told the two differ "
        "without being told the difference is unreadable")
    assert "IS the baseline" not in pub["statement"]


def test_the_two_VERDICTS_are_stated_only_where_the_rounding_cannot_change_them(
        real, the_site_publishes, the_site_last_verified):
    """BOTH EDGES OF THE BAND, in one control over the whole partition. A gate that returns
    `unresolved` for everything passes every test that asks whether it withholds correctly, so
    the three answers are asserted together rather than one leg each.

    Fires on: an off-by-a-resolution at either edge, and on a gate that cannot reach all three.
    """
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    the_site_last_verified()
    seen = {}
    for gap in (0.004, 0.011, 0.020):
        the_site_publishes(control + gap)
        pub = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))[
            "realised"]["is_the_published_supplier"]
        seen[gap] = (pub["checked"], pub["same_supplier"])
    assert seen[0.004] == (True, True), "a gap inside the resolution was not stated as agreement"
    assert seen[0.011] == (False, None), "a gap inside the unreadable band was answered anyway"
    assert seen[0.020] == (True, False), "a gap the rounding cannot explain was not stated"


# ── the identity gate: the subject is the site's OWN figure, and it must name its run ────────


def test_a_dashboard_that_cannot_NAME_its_run_WITHHOLDS_rather_than_confirming(
        real, the_site_publishes, the_site_last_verified):
    """`generate_dashboard_data` publishes `_fmt(total_net_gbp or ledger.net_margin_gbp or 0)` and
    stamps `meta.git_commit_source = "unavailable"` when neither the run's stamp nor its filename
    named a commit. A figure with no run behind it is not the published run's net margin; it is a
    number. Fires on: comparing the baseline arm against an unattributed figure.
    """
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    the_site_last_verified()
    the_site_publishes(control, run_id=None, commit="unknown", commit_source="unavailable")
    pub = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))[
        "realised"]["is_the_published_supplier"]

    assert pub["checked"] is False and pub["same_supplier"] is None
    assert pub["run_identity"]["state"] == "unestablished"
    assert "does not say which run produced it" in pub["statement"], (
        "the refusal does not name which half is missing, so a reader fixes the wrong file")
    assert "IS the baseline" not in pub["statement"]


def test_a_dashboard_built_from_a_run_OLDER_than_the_last_verified_one_WITHHOLDS(
        real, the_site_publishes, the_site_last_verified):
    """THE MTIME GLOB, MADE VISIBLE. `generate_dashboard_data._find_latest_run_json()` picks the
    run the dashboard is built from by sorting `docs/reports/run_output_*[0-9Z].json` by MTIME --
    over files `.gitignore` ignores. In the shared tree that is the freshest run. In a clean
    checkout it silently picks one of four force-added JUNE 2026 artefacts by checkout mtime: the
    site's headline net margin, from a three-month-old run, with no refusal anywhere.

    This is the one leg the provenance's one-cycle lag survives, and it is why the provenance is
    read at all. Ordering by the START STAMP inside the run's own filename is what makes it
    lag-proof: a run stamped earlier than the last VERIFIED run is old however many cycles behind
    the provenance is.

    Fires on: dropping the order leg, and on comparing the two runs for EQUALITY instead -- which
    would refuse on every publish, because `record_verified` stamps the provenance after this feed
    is generated in the same cycle.
    """
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    the_site_last_verified(run_id="run_output_abc1234_20260909T210648Z.json")
    the_site_publishes(control, run_id="run_output_9999999_20260614T031500Z.json",
                       commit="9999999")
    pub = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))[
        "realised"]["is_the_published_supplier"]

    assert pub["checked"] is False and pub["same_supplier"] is None
    assert pub["run_identity"]["state"] == "stale"
    assert pub["run_identity"]["not_older_than_verified"] is False
    assert "20260614" in pub["statement"] and "20260909" in pub["statement"], (
        "the refusal names neither run, so a reader cannot tell which artefact to go and look at")
    assert "mtime" in pub["statement"], (
        "the refusal does not name the cause, so a reader is sent to re-publish a run that is "
        "not what went wrong")
    assert "IS the baseline" not in pub["statement"]


def test_a_dashboard_NEWER_than_the_last_verified_run_is_the_ORDINARY_case_and_passes(
        real, the_site_publishes, the_site_last_verified):
    """THE NULL THE ORDER LEG NEEDS, and the one that stops it being a guard that refuses
    everything. `record_verified` stamps `publish_provenance.json` AFTER `value_arms.json` is
    generated in the same publish cycle, so on every real publish the dashboard names a run that
    is NEWER than the last verified one. Evidence in the committed record at `dceedff0f`:
    `value_arms.json` says `showing_run_id: run_output_36e3ee8c4_...` while `dashboard.json` in
    the same commit says `meta.source_file: run_output_258720283_...`.

    Fires on: an order leg written as equality, or as `<=`, either of which withholds the claim on
    every publish while looking exactly like a working identity gate.
    """
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    the_site_last_verified(run_id="run_output_36e3ee8c4_20260909T210648Z.json",
                           commit="36e3ee8c4")
    the_site_publishes(control, run_id="run_output_258720283_20260910T005624Z.json",
                       commit="258720283")
    pub = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))[
        "realised"]["is_the_published_supplier"]

    assert pub["run_identity"]["state"] == "established", (
        "the one-cycle lag between the dashboard and the provenance was read as a defect, so the "
        "claim would be withheld on every publish")
    assert pub["run_identity"]["not_older_than_verified"] is True
    assert pub["same_supplier"] is True


def test_a_site_with_no_verified_run_says_the_ORDER_WAS_NOT_ASKED_rather_than_passing_it(
        real, the_site_publishes, monkeypatch, tmp_path):
    """NOT ASKED IS NOT PASSED. The subject is established by the dashboard's own stamp, so an
    unreadable provenance does not withhold the money claim -- but it must not be recorded as a
    freshness check that ran and was satisfied.

    Fires on: `not_older_than_verified` defaulting to True when the leg could not be asked.
    """
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    monkeypatch.setattr(gva, "PUBLISH_PROVENANCE_PATH", tmp_path / "gone.json")
    the_site_publishes(control)
    pub = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))[
        "realised"]["is_the_published_supplier"]

    assert pub["run_identity"]["state"] == "established"
    assert pub["run_identity"]["not_older_than_verified"] is None, (
        "a leg that could not be asked was published as a leg that passed")
    assert pub["run_identity"]["order_not_asked_because"], (
        "the unasked leg carries no reason, so a reader cannot tell it apart from a pass")
    assert pub["same_supplier"] is True


def test_run_output_latest_is_NOT_A_RUN_and_the_order_leg_refuses_to_sort_it(real):
    """`docs/reports/run_output_latest.json` is a PATH and not a run. The name carries no start
    stamp, so ordering it against anything is a comparison with nothing on one side.

    Fires on: `_run_started_at` yielding a sortable value for the un-versioned name -- which sorts
    it FIRST or LAST depending on the comparison and is the fail-open that started all of this.
    """
    assert gva._run_started_at("run_output_latest.json") is None
    assert gva._run_started_at("run_output_258720283_20260910T005624Z.json") == (
        "20260910T005624Z")
    assert gva._run_started_at(None) is None


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
    return gva.build(art, _floor_with_spread(100.0))


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
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))
    funnel = (_load(THREE_ARM)["renewal_funnel"]["value_arm"])
    assert "{:,} renewals the world offered".format(funnel["renewals_the_world_offered"]) in \
        out["headline"]
    assert "{:.2f}%".format(funnel["priced_share_of_renewals_offered"] * 100) in out["headline"]


def test_a_run_with_no_funnel_gets_no_coverage_clause_rather_than_a_guessed_one():
    """An invented coverage sentence would be worse than none — it is the sentence a reader would
    trust most. Fires on: falling back to the account count, or to a hard-coded share."""
    art = _load(THREE_ARM)
    art.pop("renewal_funnel", None)
    out = gva.build(art, _load(NOISE_FLOOR))
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
    return gva.build(art, _load(NOISE_FLOOR))


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
    out = gva.build(art, _load(NOISE_FLOOR))
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
            _load(NOISE_FLOOR))):
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

    IT CARRIES A WORLD STAMP FOR THE SAME REASON IT CARRIES A LATE TIMESTAMP (2026-09-04). Since
    `_seed_spreads` refuses every bound whose floor names no world, an unstamped fixture here
    would witness the WORLD guard on every one of the seven tests below -- each of which is about
    the DIRECTION gate, and each of which would go green for the wrong reason the day the
    direction gate broke.

    THE DIGEST IS DERIVED FROM THE RUN, NEVER TYPED, and it used to be the literal
    `"fibre"`-style constant `"fixture-world"` (2026-09-09). The reasoning beside it was that this
    helper's subject is the superseded panel, "whose bounds are admitted on naming a world and not
    on naming THIS one" -- but every caller pairs this floor with `_load(THREE_ARM)`, the LIVE
    run. So it was never the superseded panel; it was a mismatched pair, and it went green only
    because nothing compared the floor's world to the run's. On the day `_seed_spreads` gained
    that comparison, nine controls about the DIRECTION gate were refused by the WORLD gate
    instead, each reporting the failure of the guard it names rather than the one that fired.

    Exactly the shape `_stamped_after` was written for one property along, and the remedy is the
    same: what these subjects need is the PROPERTY "this floor was measured in the world of the
    figure it bounds", and a typed digest has that property only against runs that happen to
    carry it.
    """
    values = (-stdev, 0.0, stdev)
    world = ((_load(THREE_ARM).get("world_identity") or {}).get("digest")) or "fixture-world"
    return {
        # Later than any real three-arm run, so these tests exercise the direction gate and never
        # trip the separate staleness caveat.
        "generated_at": "2999-01-01T00:00:00Z",
        "world_identity": {"digest": world, "unavailable_because": None},
        "seeds": [{"seed": 11111 + i, "value_advantage_gbp": v, "level_advantage_gbp": v,
                   "selection_gbp": v} for i, v in enumerate(values)],
        "selection_gbp_spread": {"n": 3, "stdev": stdev, "mean": 0.0,
                                 "min": -stdev, "max": stdev},
    }


def _headline_with(advantage, selection, stdev):
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"],
                                     value_advantage_gbp=advantage, selection_gbp=selection)
    return gva.build(art, _floor_with_spread(stdev))["headline"]


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
    out = gva.build(_load(THREE_ARM), floor)

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
    headline = gva.build(art, _floor_with_spread(100.0))["headline"]

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
    """A headline whose contrasts are INSIDE their own floor -- the only state that names a remedy.

    BOTH LEGS ARE PUT INSIDE THE FLOOR, AND UNTIL 2026-09-04 ONLY ONE WAS. This helper set the
    selection leg to £1,816 against a ±£2,578 floor and left the advantage at the canonical run's
    £12,071, which CLEARS that floor -- so every remedy test below ran on a page that had withheld
    `selection_gbp` alone while `_decomposition` declares a split of `value_advantage_gbp`. The
    fixture was the defect `test_a_remedy_priced_on_a_leg_the_page_resolved_is_refused` exists for:
    the price the assertions checked was for the one leg the page had just given a direction to.
    A shared fixture that embeds the defect makes every control keyed to it green for the wrong
    reason, so it is fixed here rather than worked around at the seven call sites.

    The advantage is set to the SAME £1,816 rather than to some other inside-the-floor number so
    that the two legs' withholding cannot be told apart by size, and any test that passes only
    because one leg is bigger fails here instead of on the real page.
    """
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"],
                                     value_advantage_gbp=1815.79, selection_gbp=1815.79)
    return gva.build(art, _floor_with_spread(2577.80), decomposition)["headline"]


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


def test_a_remedy_whose_OTHER_HALF_IS_EMPTY_is_refused_and_not_rounded_to_zero_percent():
    """THE DEFECT THIS BRANCH EXISTS FOR, and it is one the producer's repair CREATED.

    `decompose_floor` now withdraws `priced_share_of_variance` and `share_is_decisive` when the
    rest-of-book leg carried no variance -- the identity case filed on 2026-09-10. Without a branch
    here the page falls into "too close to call", whose two `or 0.0` fallbacks would then print
    "0% of it is the priced households' own draw ... too close to the 0% it would have to clear":
    two fabricated figures standing exactly where a withdrawal belongs, on the sentence the page's
    remedy is stapled to. A withdrawal upstream that arrives downstream as a zero is worse than the
    figure it replaced, because the zero looks measured.

    KEYED TO THE ARTEFACT'S OWN FLAG, NOT TO THE WORDING. A decomposition whose other half DID move
    keeps its price with no edit here, which is the null rung below -- a control that only ever
    demands the remedy be absent is satisfied by deleting the remedy.
    """
    ordinary = _withheld_headline(_decomposition(0.85, resolvable=True))
    empty = _withheld_headline(dict(
        _decomposition(0.85, resolvable=True),
        rest_of_book_half_is_degenerate=True,
        priced_share_of_variance=None, share_is_decisive=None,
        share_margin_over_threshold=None, larger_settled_book_would_resolve_it=None,
        irreducible_sd_gbp=None, priced_decisions_needed=None,
        why_those_keys_are_withdrawn=(
            "The `except` leg returned the IDENTICAL `value_advantage_gbp` on all 3 seeds, so its "
            "variance is exactly zero, measured over 5 accounts."),
        what_would_make_the_rest_of_book_half_measurable=(
            "Not more seeds: the roster swallows the complement it re-draws.")))

    # THE NULL RUNG FIRST -- the branch is reachable only if the other side of it still runs.
    assert "larger SETTLED BOOK" in ordinary and "54 priced renewals" in ordinary

    assert "larger SETTLED BOOK" not in empty, (
        "the page priced a remedy off a split whose other half carried no variance: {}"
        .format(empty))
    assert "0% of it is the priced households" not in empty, (
        "the producer's withdrawal arrived on the page as a measured-looking 0% -- the `or 0.0` "
        "fallback in the undecided branch: {}".format(empty))
    assert "too close" not in empty, (
        "an EMPTY half was published as a close call, which says the instrument nearly worked")
    # THE REASON IS THE PRODUCER'S OWN WORDS, so the page cannot drift into its own account of why.
    assert "IDENTICAL" in empty and "5 accounts" in empty, (
        "the refusal names no cause a reader can check it against: {}".format(empty))
    assert "roster swallows the complement" in empty, (
        "the page refused the remedy and named nothing that would fix it, which reads as 'wait "
        "for a bigger book' -- the one thing that makes this half less measurable")
    assert "More seeds would not resolve it" in empty


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
    # RE-KEYED 2026-09-04, and the re-keying is itself the point. This asserted the literal
    # phrase "PRODUCT, not a size" -- the closing clause of a sentence that also claimed drawn
    # households' renewals stop "for want of a standard-variable product to be moved off". That
    # cause was false from 2026-08-30 and this control was GREEN on it, because it was keyed to
    # the words of the remedy rather than to the property the remedy exists for: that the page
    # must not offer book growth as a lever no acquisition can pull. `NOT reachable by acquiring
    # customers` is that property, and it survives the cause being restated or withdrawn.
    _CAVEAT = "NOT reachable by acquiring customers"
    assert _CAVEAT in unreachable, (
        "every priced account was the founding roster and the page still offered book growth as "
        "the lever, which is a remedy nobody can pull: {}".format(unreachable))

    reachable = _withheld_headline(_priced_by("C1", "SYN-2021-001"))
    assert _CAVEAT not in reachable, (
        "the arm priced a DRAWN household, so acquisition does reach it -- printing the caveat "
        "anyway is a control asserting the world stays broken: {}".format(reachable))
    assert "54 priced renewals" in reachable, reachable

    silent = _withheld_headline(_decomposition(0.85, resolvable=True))
    assert _CAVEAT not in silent, silent
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
    headline = gva.build(art, _floor_with_spread(100.0),
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
    out = gva.build(_load(THREE_ARM_20260829), _load(NOISE_FLOOR))
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
    who = gva.build(art, _load(NOISE_FLOOR))[
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
    who = gva.build(art, _load(NOISE_FLOOR))[
        "decisions"]["who_the_method_has_priced"]
    assert who["verdict"] == "unresolved"
    # KEYED TO THE PROPERTY, NOT TO THE WORDING (re-keyed 2026-09-04). This asserted the literal
    # phrase "more than one label", which was a sentence that COUNTED nothing -- it said "more
    # than one" while holding the labels in its hand, and it fired identically whether the gate
    # had refused two products or twelve. The property is: the refusal names every label it saw
    # and claims no single mechanism.
    assert "does not claim a single cause" in who["sentence"]
    for label in ("None", "flex"):
        assert label in who["sentence"], (
            "the refusal withholds a cause and does not name the labels it withheld it over, so a "
            "reader cannot tell which products it could not read")


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
    who = gva.build(art, _load(NOISE_FLOOR))[
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
    return gva.build(art, _load(NOISE_FLOOR))[
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
    who = gva.build(art, _load(NOISE_FLOOR))[
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
    who = gva.build(art, _load(NOISE_FLOOR))[
        "decisions"]["who_the_method_has_priced"]
    assert who["premise_basis"].startswith("argued from the code path")


# ── the AUC's own bound: the figure that went out for four days with no interval ─────────────


def _belief(auc, retained, left):
    """A `belief_vs_outcome` block at a chosen AUC and population, everything else held.

    AND IT NAMES A WORLD (2026-09-04). Every control built on this fixture is about the composer's
    DIRECTIONAL branches -- does a figure outside its null above the point get reported as clearing,
    does one below it get reported as backwards, is the endogeneity clause ungated. Since
    `_auc_null` began withholding a direction whose departure level is unknown, an unstamped
    fixture makes all of those branches unreachable, and the reds it produced were procedural
    rather than substantive: `test_a_figure_OUTSIDE_its_null_ABOVE_the_point_is_not_reported_as_a
    _failure` went red saying `None is False` about a composer that had not changed.

    The stamp goes HERE and not in those tests because the reachability property they assert is
    meant to be one "no world change can take away" -- their own words, at the `backwards` witness
    below. The world guard's own witness is the REAL unstamped artefact, in
    `test_an_auc_null_from_a_run_that_names_no_world_withholds_its_direction_and_keeps_its_numbers`,
    which is where a fixture that quietly stopped exercising the refusal would be caught.

    AND ITS PER-DECISION RECORDS AGREE WITH ITS HEADLINE (2026-09-10). Until the within-year
    concordance landed, this fixture set `discrimination_auc` to whatever a test asked for and left
    `scored_decisions` as the REAL run's -- so a fixture claiming 0.95 carried records that score
    0.627 across eras and 0.444 within a year. Nothing read the records, so nothing noticed. The
    stratified reading reads them, and an internally contradictory fixture made the pass branch
    unreachable for a composer that was working correctly -- the same class of procedural red the
    world stamp above was added to stop.

    So the records are rebuilt to match the requested direction: retained believed above departed
    (or below it, when the caller asks for a backwards figure), spread across three years so
    same-year pairs exist on both sides. The BETWEEN-year component is held flat deliberately --
    every year gets the same two belief levels -- so the fixture exercises the household branch
    rather than the calendar one, which is the whole distinction the reading now turns on.
    """
    art = _world_stamped(_load(THREE_ARM), "fixture-world")
    ranks_forward = auc is None or auc >= 0.5
    high, low = (0.9, 0.1) if ranks_forward else (0.1, 0.9)
    years = ("2021", "2022", "2023")
    records = []
    for index in range(retained):
        records.append({"account": "FIX-R{}".format(index),
                        "term_start": "{}-06-01".format(years[index % len(years)]),
                        "believed_p_retain": high, "retained": True,
                        "chosen_margin_gbp_per_mwh": 20.0})
    for index in range(left):
        records.append({"account": "FIX-L{}".format(index),
                        "term_start": "{}-06-01".format(years[index % len(years)]),
                        "believed_p_retain": low, "retained": False,
                        "chosen_margin_gbp_per_mwh": 20.0})
    art["belief_vs_outcome"] = dict(
        art["belief_vs_outcome"],
        discrimination_auc=auc,
        auc_population={"retained": retained, "left": left},
        priced_and_scored=retained + left,
        scored_decisions=records,
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
    dec = gva.build(_belief(0.4652777777777778, 16, 9), _load(NOISE_FLOOR))["decisions"]
    assert dec["auc_attribution"]["null_bound"]["inside_the_null"] is True
    assert "INSIDE" in dec["auc_reading"]
    assert "BACKWARDS" not in dec["auc_reading"], (
        "a figure inside its own null was given a direction -- the defect the constant reading had")


def test_a_figure_OUTSIDE_its_null_ABOVE_the_point_is_not_reported_as_a_failure(real):
    """THE PASS BRANCH MUST BE REACHABLE (R15). A reading that can only ever say "backwards" or
    "cannot tell" is a constant verdict wearing a gate's clothes: the day the belief ranks well on
    a book big enough to prove it, the page must say so with nobody editing a string."""
    dec = gva.build(_belief(0.95, 10, 10), _load(NOISE_FLOOR))["decisions"]
    assert dec["auc_attribution"]["null_bound"]["inside_the_null"] is False
    assert "carried real information" in dec["auc_reading"]
    assert "BACKWARDS" not in dec["auc_reading"]
    # AND THE OTHER BRANCH IS REACHABLE TOO, so neither is a constant verdict. This used to be
    # asserted through the LIVE run, on the assumption that it would go on ranking backwards --
    # a control resting on the model staying bad, and on 2026-08-31 it stopped being true (AUC
    # 0.13 -> 0.655 once the standard-variable product gave the arm 120 decisions instead of 20).
    # The reachability of the branch is a property of the composer, so it is proved from a
    # constructed belief, which no world change can take away.
    backwards = gva.build(_belief(0.13, 10, 10), _load(NOISE_FLOOR))["decisions"]
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
        decisions = gva.build(_belief(auc, retained, left), _load(NOISE_FLOOR))["decisions"]
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
    dec = gva.build(_belief(None, 20, 0), _load(NOISE_FLOOR))["decisions"]
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
    departures = gva.build(art, _load(NOISE_FLOOR))[
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
    dep = gva.build(_scored([True, False, True, False, False]), _load(NOISE_FLOOR))["decisions"]["auc_attribution"]["the_departures"]
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
    dep = gva.build(_scored([True, False, True], left_in_population=9), _load(NOISE_FLOOR))["decisions"]["auc_attribution"]["the_departures"]
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

    BOTH COUNTS ARE READ, NEVER WRITTEN DOWN (2026-09-09). The bucket total used to be the literal
    "20 decisions", which is what the 2026-08-31 run happened to carry; `THREE_ARM` is the path each
    new run is promoted to, so the 09-08b promotion took the same table to 123 and reddened a
    control whose subject had changed rather than whose code had. The population side is the test's
    own injection and stays a literal, because a literal there is the contradiction being staged.
    """
    art = _load(THREE_ARM)
    art["belief_vs_outcome"] = dict(art["belief_vs_outcome"],
                                    auc_population={"retained": 10, "left": 4})
    in_the_buckets = sum(row["n"] for row
                         in (art["belief_vs_outcome"].get("by_believed_bucket") or []))
    assert in_the_buckets != 14, (
        "the promoted run's buckets happen to tally the injected population, so the two routes "
        "agree and this subject stages no contradiction at all")
    table = gva.build(art, _load(NOISE_FLOOR))["decisions"]["auc_attribution"]["by_believed_bucket"]
    assert table["available"] is False
    assert "{} decisions".format(in_the_buckets) in table["reason"], (
        "the refusal does not name what the buckets actually tally, so a reader cannot tell which "
        "of the two routes to go and look at: " + table["reason"])
    assert "counts 14" in table["reason"]
    assert "buckets" not in table, "an unavailable table published its rows anyway"


def test_the_bucket_readings_direction_is_read_off_the_bands_and_never_written_down():
    """The sentence under this table must say what THIS run's bands do, not what one run's did.

    THE DEFECT (2026-09-09, found by promoting, not by reading). The reading was authored against
    the 2026-08-31 run and asserted four things about it in prose: the least-confident band mostly
    stayed, the most confident "kept none of them", flipping the labels reads monotone the right
    way, and every band is single-digit. `THREE_ARM_PATH` is the path each new run is PROMOTED to,
    so the 09-08b promotion put a table realising 63/53/74/77 on 8/40/23/52 decisions under all
    four claims and made every one of them false. No clock, world or staleness guard on this page
    can see a stale SENTENCE, so the miss was structural rather than careless.

    BOTH DIRECTIONS ARE WITNESSED, because a reading that always says "backwards" passes any
    assertion written against a reversed table, and that is the shape the hard-coded sentence had.

    Fires on: writing the direction down; reading it off the wrong end; claiming the flipped column
    is monotone when the real one does not fall at every band; or reciting a band size.
    """
    def reading(rates, sizes=(9, 9, 9)):
        return gva._bucket_reading([
            {"believed_from": lo, "believed_to": lo + 0.2, "n": n,
             "realised_retention_rate": rate}
            for lo, rate, n in zip((0.2, 0.4, 0.6), rates, sizes)])

    reversed_table = reading((0.9, 0.5, 0.1))
    assert "BACKWARDS" in reversed_table, reversed_table
    assert "90%" in reversed_table and "10%" in reversed_table, (
        "the two ends' own rates are not in the sentence, so a reader cannot check the direction "
        "it states against the table it sits under: " + reversed_table)
    assert "monotone the right way" in reversed_table, (
        "the flipped column rises at every band here and the reading does not say so")

    # THE OTHER DIRECTION, and it is the live one since 2026-09-08b. A reading that cannot say this
    # is the hard-coded sentence with extra steps.
    agreeing = reading((0.63, 0.53, 0.77))
    assert "SAME way" in agreeing and "BACKWARDS" not in agreeing, agreeing
    assert "does not make it monotone either" in agreeing, (
        "the real column does not fall at every band, so the flipped one is not monotone -- and "
        "the reading still offers the flip as the tidy reading: " + agreeing)

    # THE SIZE CLAIM IS READ, not recited: "every band is single-digit" was true of one run.
    assert "rests on 40 decisions" in reading((0.63, 0.53, 0.77), sizes=(52, 40, 61)), (
        "the smallest band's size is not read off the bands")

    # THE REFUSAL SURVIVES EVERY BRANCH -- it is a property of the table, not of a run's answer.
    for sentence in (reversed_table, agreeing, reading((0.5, 0.5, 0.5))):
        assert "settled on the LEVEL beside it and not here" in sentence, (
            "a branch dropped the one claim this table can actually support")


def test_a_run_without_the_bucket_table_says_so_rather_than_rendering_an_empty_one():
    """FAIL-CLOSED on the artefact that does not carry the field at all.

    Fires on: defaulting the missing table to `[]`, which renders as a table with no reversal in
    it -- indistinguishable, on the page, from a belief that ranked correctly.
    """
    art = _load(THREE_ARM)
    art["belief_vs_outcome"] = {k: v for k, v in art["belief_vs_outcome"].items()
                                if k != "by_believed_bucket"}
    table = gva.build(art, _load(NOISE_FLOOR))["decisions"]["auc_attribution"]["by_believed_bucket"]
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
    d = gva.build(art, _load(NOISE_FLOOR))

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
    d = gva.build(art, _load(NOISE_FLOOR))

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
    d = gva.build(art, _load(NOISE_FLOOR))

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
        d = gva.build(_stamped(_load(THREE_ARM), empty), _load(NOISE_FLOOR))
        assert d["producing_commit"]["stated"] is False, empty
        assert d["book"]["available"] is False, empty
    assert "git did not answer" in gva.build(
        _stamped(_load(THREE_ARM), None), _load(NOISE_FLOOR)
    )["producing_commit"]["reason"]


def test_the_per_leg_conditioning_is_withheld_on_a_run_that_did_not_measure_it():
    """FAIL CLOSED, and the absence here is the one that would read as an ANSWER.

    An absent split defaulted to `available: True` with empty legs renders, on the page, as every
    cut seeing zero departures -- which is "all four cuts are survivor cuts", the claim this
    block was built to refute. So the refusal is the default and it names whose problem it is.

    AND THE FINDING'S OWN VERDICT MUST NOT BE INLINED. "The estimand admits the departures" is
    true of every run measured so far and is not a property of the mechanism; writing it here
    would publish it for runs that never measured it -- the same defect `_skill_survivorship` was
    written to avoid, arriving on the block that carries the flattering direction.

    Fires on: defaulting an absent block to available; on the generic reason swallowing the run's
    own; on the finding's sentence being typed into the passthrough.
    """
    absent = gva._skill_leg_conditioning({})
    assert absent["available"] is False
    assert "predates the per-leg conditioning split" in absent["reason"]
    assert "admits" not in absent["reason"], (
        "the page stated the estimand's verdict for a run that never measured it")
    assert "by_leg" not in absent

    # A run that TRIED and could not: its own reason wins, because "predates the split" and
    # "published no event log" are different states and only one of them is ours to fix.
    refused = gva._skill_leg_conditioning({"leg_conditioning": {
        "available": False, "why_not": "the run published no `customer_events`"}})
    assert refused["available"] is False
    assert "no `customer_events`" in refused["reason"]

    # AND A REAL ONE PASSES THROUGH UNCHANGED -- the residue with it, which is the field a
    # passthrough would most plausibly drop as detail. Asserted after the refusals, so a pass is
    # evidence of a passthrough rather than of a constant.
    measured = gva._skill_leg_conditioning({"leg_conditioning": {
        "available": True,
        "priced_decisions_the_world_recorded_as_a_departure": 40,
        "by_leg": {"every_priced_decision_pounds_outcome": {
            "of_those_the_world_recorded_as_a_departure": 37,
            "conditioned_on_survival": False}},
        "the_estimand_admits_the_departures": True,
        "departures_the_estimand_cannot_see": 3,
        "why_the_estimand_cannot_see_them": {
            "horizon_open_at_the_end_of_the_settled_book": 3},
        "reading": "IT IS NOT UNCONDITIONED",
    }})
    assert measured["available"] is True
    assert measured["the_estimand_admits_the_departures"] is True
    assert measured["departures_the_estimand_cannot_see"] == 3
    assert measured["why_the_estimand_cannot_see_them"] == {
        "horizon_open_at_the_end_of_the_settled_book": 3}
    assert measured["reading"] == "IT IS NOT UNCONDITIONED"


def test_the_survivorship_split_is_withheld_on_a_run_that_did_not_measure_it():
    """FAIL CLOSED, and the leg that stops this page carrying a finding its run never made.

    THE DEFECT THIS IS AIMED AT is the one the finding itself is about. `drop_out` tells a reader
    the sample "can only be widened by a LARGER settled book"; the measurement says the class IS
    the departures, so a larger book buys none of them back. The temptation is to write the
    corrected sentence here, where it would appear on every page including the ones produced from
    runs predating the split -- a claim about a run the run never made, which is the shape this
    file exists to refuse.

    Fires on: defaulting an absent block to `available: True`, or inlining the finding's sentence
    instead of reading the run's own.
    """
    absent = gva._skill_survivorship({})
    assert absent["available"] is False
    assert "predates the survivorship split" in absent["reason"]
    assert "conditioned" not in absent["reason"], (
        "the page stated the finding's verdict for a run that never measured it")

    # A run that TRIED and could not -- its own reason is preferred over the generic one, because
    # "predates the split" and "published no event log" are different states.
    refused = gva._skill_survivorship({"survivorship": {
        "available": False, "why_not": "the run published no `customer_events`"}})
    assert refused["available"] is False
    assert "no `customer_events`" in refused["reason"]

    # AND IT PASSES A REAL ONE THROUGH UNCHANGED, verdict and counts both. Asserted after the two
    # refusals so a pass here is evidence of a passthrough rather than of a constant.
    measured = gva._skill_survivorship({"survivorship": {
        "available": True,
        "decisions_dropped_for_no_settled_row": 40,
        "of_those_the_world_recorded_as_a_departure": 40,
        "of_those_not_attributable_to_a_departure": 0,
        "scored_decisions_the_world_recorded_as_a_departure": 0,
        "the_concordance_is_conditioned_on_survival": True,
        "reading": "A LARGER BOOK DOES NOT FIX THIS",
    }})
    assert measured["available"] is True
    assert measured["of_those_the_world_recorded_as_a_departure"] == 40
    assert measured["the_concordance_is_conditioned_on_survival"] is True
    assert measured["reading"] == "A LARGER BOOK DOES NOT FIX THIS"

    # ...and a run whose split REFUTES the reading is passed through refuting it, not smoothed.
    refuted = gva._skill_survivorship({"survivorship": {
        "available": True,
        "decisions_dropped_for_no_settled_row": 40,
        "of_those_the_world_recorded_as_a_departure": 39,
        "of_those_not_attributable_to_a_departure": 1,
        "scored_decisions_the_world_recorded_as_a_departure": 2,
        "the_concordance_is_conditioned_on_survival": False,
        "reading": "refutes the survivorship reading",
    }})
    assert refuted["the_concordance_is_conditioned_on_survival"] is False
    assert refuted["of_those_not_attributable_to_a_departure"] == 1
    assert refuted["scored_decisions_the_world_recorded_as_a_departure"] == 2


def _sample_size_ms(head=(0.45, 0.55), head_n=168, head_inside=True,
                    leg=(0.446, 0.554), leg_n=161, leg_inside=False, leg_available=True):
    """A run's method-skill block with the two intervals this comparison reads, and nothing else.

    Both legs are parameters because the verdict is a comparison and a fixture that could only
    produce one side of it would make every assertion below vacuous.
    """
    legs = {}
    if leg_available:
        legs[gva.UNCONDITIONED_LEG] = {
            "decisions": leg_n,
            "null_spread": {"available": True, "null_95_interval": list(leg),
                            "observed_inside_the_null_interval": leg_inside},
        }
    else:
        legs[gva.UNCONDITIONED_LEG] = {"decisions": leg_n, "null_spread": {"available": False}}
    return {
        "decisions_scored": head_n,
        "null_spread": {"available": True, "null_95_interval": list(head),
                        "observed_inside_the_null_interval": head_inside},
        "fixed_horizon": {"legs": legs},
    }


def test_the_sample_size_explanation_refuses_before_it_asserts():
    """POISON ROUNDS FIRST. "Refuted" is the answer this book happens to give, and a block that
    returned it on every input would pass a control written only against today's run.

    THE DEFECT (2026-09-09, Lane 0, item 4 of the survivorship finding). The producer's own
    inside-the-null reading ended "that is a statement about how few decisions there are, not
    about the method" -- an attribution one interval cannot support, and one this run refutes from
    its own second cut. This block decides between the causes where BOTH cuts are in hand and
    refuses where they are not.

    Fires on: defaulting an absent or unaskable comparison to a verdict; on answering "the
    sentence is fine" where the honest answer is "nobody checked".
    """
    # (1) NO HEADLINE INTERVAL -- there is no "we cannot tell" whose cause could be named.
    nothing = gva._skill_sample_size_explanation({})
    assert nothing["available"] is False
    assert "no interval on the headline" in nothing["reason"]

    # (2) THE HEADLINE CLEARS ITS OWN NULL -- it is not saying "we cannot tell", so no
    #     explanation is owed and finding a defect here would be finding one in a page with none.
    cleared = gva._skill_sample_size_explanation(_sample_size_ms(head_inside=False))
    assert cleared["available"] is False
    assert "outside its own null" in cleared["reason"]

    # (3) NO SECOND CUT TO COMPARE AGAINST -- the claim is UNCHECKED, and says so. A silent
    #     absence here renders as "the sentence above is fine", which is the one reading it
    #     cannot support.
    unchecked = gva._skill_sample_size_explanation(_sample_size_ms(leg_available=False))
    assert unchecked["available"] is False
    assert "CANNOT BE CHECKED" in unchecked["reason"]
    assert "too few decisions" not in unchecked["reason"].replace(
        "whether too few decisions is", "")


def test_the_sample_size_explanation_needs_BOTH_legs_of_its_power_comparison():
    """The verdict turns on a conjunction, so each half is driven to fail on its own.

    A second cut that distinguishes itself from chance refutes "too few decisions" ONLY if it did
    so with no more decisions AND no narrower an interval. Either one failing means it simply had
    more power, which explains its own verdict and says nothing about the first -- and widening
    one predicate of an ANDed pair catches nothing, so both are driven here separately.

    Fires on: dropping either predicate; on reading "the other cut distinguishes" as the whole
    test.
    """
    refuted = gva._skill_sample_size_explanation(_sample_size_ms())
    assert refuted["verdict"] == "refuted_by_this_run"
    assert refuted["too_few_decisions_survives_as_the_explanation"] is False
    assert "TOO FEW DECISIONS IS NOT WHY" in refuted["sentence"]
    assert "161" in refuted["sentence"] and "168" in refuted["sentence"]

    # MORE DECISIONS: the second cut outranks the first on n, so its verdict is unsurprising.
    bigger = gva._skill_sample_size_explanation(_sample_size_ms(leg_n=200))
    assert bigger["verdict"] == "not_settled_the_other_cut_had_more_power"
    assert bigger["too_few_decisions_survives_as_the_explanation"] is True
    assert "NOT settled here" in bigger["sentence"]

    # NARROWER INTERVAL: same n, more power per decision -- same refusal, for the other reason.
    tighter = gva._skill_sample_size_explanation(_sample_size_ms(leg=(0.47, 0.53)))
    assert tighter["verdict"] == "not_settled_the_other_cut_had_more_power"
    assert tighter["it_did_so_on_no_more_decisions_and_no_narrower_an_interval"] is False

    # AND THE OTHER VERDICT ENTIRELY: neither cut clears its null, so the explanation stands.
    both_silent = gva._skill_sample_size_explanation(_sample_size_ms(leg_inside=True))
    assert both_silent["verdict"] == "still_live"
    assert both_silent["too_few_decisions_survives_as_the_explanation"] is True
    assert "remains a live explanation" in both_silent["sentence"]
    assert "TOO FEW DECISIONS IS NOT WHY" not in both_silent["sentence"]


def test_the_sample_size_explanation_reads_the_published_runs_own_two_intervals():
    """AGAINST THE REAL ARTEFACT, and keyed to the property rather than to today's verdict.

    The expected verdict is derived here from the run's own two intervals rather than written
    down, so this stays green the day an honest run changes the answer and goes red the day the
    block stops reading the run.

    Fires on: computing the comparison from anything but the run's own permutations.
    """
    ms = _load(THREE_ARM)["method_skill"]
    block = gva._skill_sample_size_explanation(ms)
    head = ms["null_spread"]
    leg = (ms["fixed_horizon"]["legs"] or {}).get(gva.UNCONDITIONED_LEG) or {}
    if not (head.get("available") and (leg.get("null_spread") or {}).get("available")
            and head.get("observed_inside_the_null_interval")):
        assert block["available"] is False
        return
    head_lo, head_hi = head["null_95_interval"]
    leg_lo, leg_hi = leg["null_spread"]["null_95_interval"]
    distinguishes = not leg["null_spread"]["observed_inside_the_null_interval"]
    less_power = (leg["decisions"] <= ms["decisions_scored"]
                  and (leg_hi - leg_lo) >= (head_hi - head_lo))
    expected = ("refuted_by_this_run" if distinguishes and less_power
                else "not_settled_the_other_cut_had_more_power" if distinguishes
                else "still_live")
    assert block["available"] is True
    assert block["verdict"] == expected
    assert block["headline_decisions"] == ms["decisions_scored"]
    assert block["unconditioned_decisions"] == leg["decisions"]


def test_the_page_publishes_the_runs_own_sentence_beside_the_verdict_and_never_instead_of_it():
    """THE DISAGREEMENT IS THE EVIDENCE, so neither sentence is allowed to eat the other.

    The finding this closes left the producer's claim standing on purpose: correcting it in the
    same commit as the block that refutes it would leave nothing able to show the two disagreed.
    A generator that rewrote `reading` would destroy the same evidence a commit later.

    Fires on: editing or dropping the run's own reading; on publishing the verdict without it.
    """
    built = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR))["method_skill"]
    assert built["reading"] == _load(THREE_ARM)["method_skill"]["null_spread"]["reading"], (
        "the page edited the run's own sentence instead of publishing a verdict beside it")
    assert built["the_sample_size_explanation"], (
        "the run's reading is published with nothing checking the cause it names")


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


_ALL_ELIGIBILITY = {"join": 0, "coverage": 4, "eligibility": 10}


def test_the_page_stops_promising_a_bigger_book_when_nothing_measured_it():
    """THE DEFECT (2026-09-08, Lane 0), on the surface a reader actually meets.

    This sentence is rendered in amber directly above the concordance interval and it closed
    "The interval above is what this book can earn, and only a larger settled book moves it."
    The class counts support the first half and say NOTHING about the second: measured, the
    eligibility class IS the churn class, so a bigger book drops the same share.

    Fires on: any remedy composed from `by_class` alone.
    """
    withheld = gva._widening_consequence(_ALL_ELIGIBILITY)
    assert "only a larger settled book moves it" not in withheld
    assert "NOT ESTABLISHED by this run" in withheld
    # The measured half must survive the correction.
    assert "cannot be widened by fixing our own code" in withheld


@pytest.mark.parametrize("split,expected,forbidden", [
    ({"available": True, "decisions_dropped_for_no_settled_row": 40,
      "of_those_not_attributable_to_a_departure": 0,
      "the_concordance_is_conditioned_on_survival": True},
     "does NOT move it", "may move it"),
    ({"available": True, "decisions_dropped_for_no_settled_row": 40,
      "of_those_not_attributable_to_a_departure": 7,
      "the_concordance_is_conditioned_on_survival": False},
     "moves at most part of it", "does NOT move it"),
    ({"available": True, "decisions_dropped_for_no_settled_row": 0,
      "of_those_not_attributable_to_a_departure": 0,
      "the_concordance_is_conditioned_on_survival": False},
     "may move it", "does NOT move it"),
])
def test_the_bigger_book_clause_moves_with_the_split(split, expected, forbidden):
    """R15: three states, each driven, so the clause cannot be a constant wearing a reading's
    clothes — which is precisely what the sentence it replaces was.

    The survivor-conditioned world and the recoverable-residue world are the Lane 0 item's own
    two hypotheses, and the page has to be able to say either.
    """
    rendered = gva._widening_consequence(_ALL_ELIGIBILITY, split)
    assert expected in rendered
    assert forbidden not in rendered
    assert "NOT ESTABLISHED" not in rendered


def test_the_consequence_reads_the_RUNS_split_and_not_a_second_idea_of_it():
    """THE WIRING. `_widening_consequence` being right proves nothing about whether the feed
    hands it the split — and a funnel and a split disagreeing on one page is the whole defect.

    Driven through the producer, so a fixture that typed the split would prove only that the
    function renders what a test gave it.
    """
    from tools.run_value_cycle_ab import _survivorship

    produced = _survivorship(
        [{"reason": "the_priced_term_carried_no_settled_row", "account": "A1",
          "term_start": "2023-01-01"}],
        [{"account": "A2", "term_start": "2023-02-01"}],
        {("A1", "2023-01-01")})
    assert produced["the_concordance_is_conditioned_on_survival"] is True

    funnel = gva._skill_drop_out({
        "drop_out": {"available": True, "reconciles": True, "priced_decisions": 14,
                     "decisions_scored": 4, "dropped_by_reason": {"declined": 0},
                     "dropped_by_class": _ALL_ELIGIBILITY, "what_each_class_means": {},
                     "what_each_reason_means": {}},
        "survivorship": produced,
    })
    assert "does NOT move it" in funnel["consequence"]
    assert "NOT ESTABLISHED" not in funnel["consequence"]


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

    built = gva.build(stale, _world_stamped(_load(NOISE_FLOOR), "0000000000000000"))
    assert built["world_provenance"]["superseded"] is True
    assert built["headline"].startswith("READ THIS AS HISTORY"), (
        "the world caveat did not reach the headline, or reached it after the figure it "
        "qualifies: " + built["headline"][:120])
    # The figures themselves are KEPT. Superseded-with-provenance is the correction; deletion
    # is not -- so the advantage must still be stated, under its caveat.
    #
    # KEYED TO THE RUN'S OWN ADVANTAGE, NOT TO £12,071 (2026-09-08). This read `assert "12,071" in
    # built["headline"]`, which is a control pinned to today's answer: `THREE_ARM_PATH` is the path
    # the newest run is PROMOTED onto, so the assertion went red on the day the page became MORE
    # current while saying nothing about the property it exists for. What must hold is that
    # whatever advantage the subject carries reaches the headline.
    stated = gva._f((stale.get("level_vs_selection") or {}).get("value_advantage_gbp"))
    assert stated is not None, "the subject artefact carries no advantage to state"
    assert gva._gbp(stated) in built["headline"], (
        "the superseded run's own advantage was dropped from the headline rather than kept under "
        "its caveat -- deletion is not the correction: " + built["headline"][:200])


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
#: SOLE WITNESS FOR THE WORLD GUARD: the right LEG (`all`) naming NO world, so only the world check
#: can refuse it.
#:
#: NAMED DIRECTLY, NOT REACHED THROUGH `NOISE_FLOOR` (2026-09-09). This was `NOISE_FLOOR` -- the
#: canonical path -- which held exactly this artefact's bytes and therefore had the property by
#: accident. `NOISE_FLOOR` is where the newest floor is PROMOTED to, so on 2026-09-09 it became a
#: live-world floor and the world guard correctly admitted it, reddening a test whose subject had
#: silently changed under it. A witness for "names no world" has to be a file that will never gain
#: a world stamp, which is a dated copy and never a moving pointer.
NOISE_FLOOR_NO_WORLD = (
    PROJECT / "docs" / "observability" / "value_cycle_ab_s1_noise_floor_20260831.json")


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
    satisfies both alternations: `NOISE_FLOOR_NO_WORLD` is mode `all` and names no world; the
    `only` leg names the live world and is the wrong mode. Drop the world check and the first is
    admitted; drop the leg check and the second is.

    Fires on: dropping either guard; reading a bound from the superseded `floor` argument;
    admitting a refusal stub with no `generated_at`; or bounding the contrast with the floor's
    published `selection_gbp_spread` instead of this contrast's own spread.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    no_world = _load(NOISE_FLOOR_NO_WORLD)
    only_leg = _load(NOISE_FLOOR_ONLY_LIVE)

    # SOLE WITNESS FOR THE WORLD GUARD: the undecomposed leg, naming no world.
    assert (no_world.get("redraw_scope") or {}).get("mode") == gva.BOUNDING_REDRAW_MODE, (
        "this subject no longer isolates the WORLD guard -- it must be the right leg so that only "
        "the world check can refuse it")
    assert ((no_world.get("world_identity") or {}).get("digest")) is None, (
        "this subject now names a world, so the world guard has nothing to refuse it for and the "
        "leg below would pass vacuously")
    stale = gva._current_world_contrast(current, superseded, no_world)
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
    admitted = _stamped_after(
        dict(only_leg, redraw_scope=dict(only_leg["redraw_scope"],
                                         mode=gva.BOUNDING_REDRAW_MODE)), current)
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
    point = _world_stamped(_load(gva.CURRENT_WORLD_THREE_ARM_PATH), live)
    # THE LEG THE PAGE IS WAITING FOR, synthesised. The real one is still being measured; this
    # control is about the WIRING and must not wait on a run to be able to fail.
    #
    # STAMPED FORWARD ONTO THE POINT ESTIMATE'S OWN CLOCK, for the same reason the world digest is
    # stamped forward one line up, and it is not cosmetic. `_staleness_caveat` withholds the bound
    # whenever the floor's `generated_at` PREDATES the three-arm run's -- correctly, and it went
    # from silent to firing on 2026-09-08 the moment `CURRENT_WORLD_THREE_ARM_PATH` moved to a
    # re-take later than any floor on disk. A synthetic floor left on the 09-03 clock therefore
    # makes `bound_available` false through the AGE guard while the wiring under test is perfect,
    # so the assertion below would red for a reason this control does not name. Both stamps say
    # the same thing: this fixture stands in for the floor leg that is owed, and the wiring is
    # what is on trial.
    undecomposed = dict(only_leg, redraw_scope=dict(only_leg["redraw_scope"],
                                                    mode=gva.BOUNDING_REDRAW_MODE),
                        generated_at=point["generated_at"])
    floor_path = tmp_path / "floor_all_live_world.json"
    floor_path.write_text(json.dumps(undecomposed), encoding="utf-8")
    monkeypatch.setattr(gva, "CURRENT_WORLD_NOISE_FLOOR_PATH", floor_path)

    three_arm_path = tmp_path / "three_arm_live.json"
    three_arm_path.write_text(json.dumps(point), encoding="utf-8")
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
    # BOTH WITNESSES ARE STAMPED AFTER THE RUN THEY BOUND, so the guard named in each leg is the
    # one that can refuse. A dated fixture against a promoted run is refused by the STALENESS guard
    # first, and a mutation battery whose witnesses die on a third guard reports SURVIVED for both.
    no_world = _stamped_after(_load(NOISE_FLOOR_NO_WORLD), current)
    only_leg = _stamped_after(_load(NOISE_FLOOR_ONLY_LIVE), current)

    # MUTATION 1: the world guard drops. The superseded floor -- right leg, no world -- is the
    # only subject that tells the mutated function from the real one.
    world_blind = gva._current_world_bound(
        dict(no_world, world_identity={"digest": live}), current, live)
    assert world_blind["bound_available"] is True, (
        "the superseded floor does not become admissible when its digest is faked to the live "
        "one, so it cannot witness the removal of the world guard")
    assert gva._current_world_bound(no_world, current, live)["bound_available"] is False, (
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
    from "one draw's"; reporting a family the floor's own rows do not give; or a reason that
    withholds a verdict without placing the published draw in the family that reverses it.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    admitted = _stamped_after(
        dict(_load(NOISE_FLOOR_ONLY_LIVE),
             redraw_scope=dict(_load(NOISE_FLOOR_ONLY_LIVE)["redraw_scope"],
                               mode=gva.BOUNDING_REDRAW_MODE)), current)

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
    # THE RANGE THAT REVERSES IT REACHES THE READER -- FROM THE FIELDS, which is where the page
    # now reads it. Until 2026-09-08 this asserted the literal strings "£451" and "£2,434" inside
    # the reason: two homes for one fact, and the assertion here was keyed to TODAY'S ANSWER as
    # well, so it would have gone red on a re-run that moved the family and green on a page that
    # dropped the band table entirely. `#arms-redraw` renders these three from
    # `verdict_stability.*` as cells that fail one at a time; what this rung owes is that the
    # block the cells come from is CARRIED and correct.
    #
    # AND THE CENTRE IS THE ONE THAT PLACES THE SURVIVING POINT ESTIMATE. A range says how far the
    # quantity moves; only the mean says the published £2,336 is the high end of its own re-draws
    # rather than their middle. Withholding the binary and leaving that unsaid is the flattering
    # reading one layer along.
    rows = (1467.230551, 2433.696987, 450.9949)
    stability = withheld["verdict_stability"]
    for edge, expected in (("redraw_min_gbp", min(rows)),
                           ("redraw_mean_gbp", sum(rows) / len(rows)),
                           ("redraw_max_gbp", max(rows))):
        assert stability[edge] == pytest.approx(expected), (
            "the reported {} is not {} of the rows it claims to summarise, so the band table "
            "renders a family this floor did not produce".format(edge, edge.split("_")[1]))
    # AND THE REASON SENDS THE READER TO IT rather than reciting it a second time. Read from the
    # block this same call composed, so a reworded pointer stays green and a reason that stops
    # pointing anywhere reds.
    assert withheld["redraw_band"] and withheld["redraw_band"] in (
            withheld["verdict_withheld_because"]), (
        "the reason withheld a verdict for a family and did not place the published draw in it "
        "or say where the family is: " + withheld["verdict_withheld_because"])
    # THE DIRECTION IS COMPOSED, NOT HARD-CODED. £2,335.87 is above the £1,450.64 mean, so this
    # subject must say ABOVE -- and the low-draw subject below is the sole witness that the
    # sentence is capable of saying the unflattering thing about a DIFFERENT draw. Without it,
    # "ABOVE" is a constant that happens to be true of today's artefact.
    assert "ABOVE" in withheld["verdict_withheld_because"], (
        "the published draw sits above its family's mean and the reason did not say so")
    # £1,200 is chosen to clear the £991 spread (so the withheld branch is still REACHED -- a
    # subject that failed `_resolvable` would exit through `resolved: None` and witness nothing)
    # while sitting under the £1,451 mean. Both margins are ~£200, not ~£9.
    low_draw = dict(current, level_vs_selection=dict(
        current["level_vs_selection"], value_advantage_gbp=1200.0))
    low = gva._current_world_contrast(low_draw, superseded, straddling)
    assert low["verdict_withheld_because"] and "BELOW" in low["verdict_withheld_because"], (
        "a draw of £1,200 sits below the £1,451 mean of the same family and the page still said "
        "ABOVE, so the placement is hard-coded to today's artefact rather than measured: "
        + str(low.get("verdict_withheld_because")))

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


def _floor_with_n_advantages(floor: dict, values: list) -> dict:
    """The same floor re-seeded to ANY number of rows, with its published spread moved to match.

    WHY THE ROW COUNT HAS TO BE A PARAMETER. `_floor_with_advantages` zips against the artefact's
    existing three seeds, so it can only ever produce a three-row family -- and three rows is
    exactly the count at which the property under test below is arithmetically unreachable. A
    witness for the n>=5 branch has to be able to add rows.

    `selection_gbp_spread` MOVES WITH THE ROWS, because `_seed_spreads` reconciles the spread it
    derives from the seed rows against the one the floor publishes and withholds ALL THREE
    contrasts when they disagree. A fixture that added rows and left that block alone would be
    refused by the reconciliation guard, and the control above it would then report the failure of
    the guard it names rather than the one that actually fired -- the shape `_stamped_after`
    documents ten instances of. The recomputation here is the artefact's own definition, so what
    this builds is a floor that could really have been measured.
    """
    template = floor["seeds"][0]
    seeds = [dict(template, value_advantage_gbp=value) for value in values]
    selections = [seed["selection_gbp"] for seed in seeds]
    mean = sum(selections) / len(selections)
    stdev = (sum((s - mean) ** 2 for s in selections) / (len(selections) - 1)) ** 0.5
    return dict(floor, seeds=seeds,
                selection_gbp_spread=dict(floor.get("selection_gbp_spread") or {}, stdev=stdev))


def test_a_leg_whose_own_redraws_straddle_zero_states_no_direction_however_stable():
    """A quantity that changes sign across re-draws of itself has no direction to state.

    THE DEFECT (2026-09-09, Lane 0, the director's reading of the live page). The selection leg --
    the ONLY figure on this page that could be value CREATED rather than moved, and therefore the
    one a reader will quote -- publishes +GBP 270.21 over a family running from -GBP 3,075 to
    +GBP 1,199 whose CENTRE is -GBP 481. The page withheld its verdict, correctly, and every word
    of the refusal was about STABILITY: "it is a single draw", "a property of which draw was made".
    Nothing on the page said the quantity has no sign, and nothing said the centre of its own
    family is on the other side of zero from the published figure. "No verdict, +GBP 270" and "no
    verdict, and this leg's own re-draws centre below zero" are different pages.

    WHY `stable` COULD NOT CATCH IT AND NEVER WILL. Every verdict in `_verdict_stability` goes
    through `_resolvable`, which takes `abs()`. It asks how FAR from zero a draw fell, never which
    SIDE. A family unanimous about clearing its own spread can be unanimous about nothing else.

    THE EQUIVALENCE IS THE POINT OF THE THIRD WITNESS, and it was established before the gate was
    written rather than discovered afterwards as a dead branch. At three rows -- today's seed count
    -- a family that straddles zero CANNOT be verdict-stable: with two draws at +a and one at -b the
    sample standard deviation is (a+b)/sqrt(3), and min(a, b) > 0.577(a+b) has no solution. The same
    holds at four. So on today's artefact this gate can only ever fire where `stable` is already
    False, and a control resting on the live floor alone would be asserting an equivalence while
    reading like a gate. It becomes reachable at n>=5, which is a floor re-run with more seeds and
    nothing more exotic than that, and WITNESS C is that floor.

    Fires on: dropping the sign clause; folding it into the stability reason so one deletes the
    other; keying it to the figure being small or negative rather than to the family straddling
    zero; hard-coding the centre's side; or letting the stated-verdict branch keep a direction on a
    family with no sign.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    admitted = _admitted_live_floor(current)

    # WITNESS A -- the live artefact, unedited, on the leg the director was reading. The selection
    # leg's own three rows straddle zero, so the clause is due on the page as it stands today.
    block = gva._current_world_contrast(current, superseded, admitted, later_runs=[])
    leg = block["selection_leg"]
    assert leg["verdict_stability"]["sign_determined"] is False, (
        "the live selection leg's re-draws no longer straddle zero, so this subject cannot "
        "witness the sign gate -- re-point it at a leg that does rather than deleting the rung")
    assert leg["no_sign"], (
        "the selection leg's family straddles zero and the feed composed no sentence saying so, "
        "so a reader meets a positive figure whose own re-draws change sign with nothing on the "
        "page telling them")
    assert leg["no_sign"] in leg["verdict_withheld_because"], (
        "the sign clause was composed and never reached the published reason, so it renders "
        "nowhere a reader looks")
    # BOTH CAUSES SURVIVE. This leg is withheld for stability AND for sign, and a reason that
    # dropped either is a reason that deleted a finding from the surface.
    # KEYED TO THERE BEING TWO CAUSES, NOT TO EITHER ONE'S WORDS. Take the sign clause out of the
    # published reason and what is left must still say something -- that is the stability refusal,
    # whatever it is currently worded as, and a producer that reworded it stays green while one
    # that substituted one cause for the other reds.
    assert leg["verdict_withheld_because"].replace(leg["no_sign"], "").strip(), (
        "the stability reason was replaced by the sign one rather than joined to it")
    # THE CENTRE'S SIDE IS COMPOSED, NOT ASSERTED -- AND KEYED TO THE PROPERTY, NOT TO WHICH SIDE
    # THE LIVE DRAW HAPPENS TO BE ON (repaired 2026-09-11).
    #
    # WHAT THIS RUNG USED TO SAY, AND WHY IT WAS WRONG. It asserted the clause is PRESENT, on the
    # reasoning "-GBP 481 against a published +GBP 270, so this subject must say the centre is on
    # the other side". True of the artefact it was written against and false as a control: the
    # clause is CONDITIONAL on the draw and the centre straddling zero between them, and the live
    # draw's side is a property of which run is promoted to `THREE_ARM_PATH`. Promoting the 09-10
    # run moved the canonical selection leg from +GBP 319 to -GBP 333, onto the SAME side as its
    # family's centre -- so the clause correctly fell silent and this rung went red reporting a
    # defect that did not exist. The page had become more consistent, not less.
    #
    # So the rung now asserts the BICONDITIONAL the producer actually implements: the clause is
    # present exactly when the two sides disagree. That stays green through any promotion and reds
    # on a producer that composes the clause unconditionally, drops it, or inverts it.
    centre = leg["verdict_stability"]["redraw_mean_gbp"]
    draw = leg["figure_gbp"]
    opposite_sides = (centre > 0) != (draw > 0) and centre != 0
    assert ("CENTRE of that family is on the other side of zero" in leg["no_sign"]) is opposite_sides, (
        "the centre clause and the numbers disagree: the published draw is GBP {:.2f}, the centre "
        "of its own re-draw family is GBP {:.2f}, so the clause is {} and the page says otherwise"
        .format(draw, centre, "due" if opposite_sides else "not due"))

    # WITNESS A2 -- THE CENTRE CLAUSE FIRING, kept reachable by construction rather than by which
    # run is canonical today. The same leg with only the published draw reflected across zero, so
    # the draw and the family's centre must disagree whichever side the live run put them on. This
    # is the rung the biconditional above would otherwise let go vacuous: a producer that never
    # composes the clause satisfies the biconditional whenever the live numbers happen to agree.
    reflected = dict(current, level_vs_selection=dict(
        current["level_vs_selection"], selection_gbp=-draw))
    across = gva._current_world_contrast(reflected, superseded, admitted, later_runs=[])["selection_leg"]
    assert across["verdict_stability"]["sign_determined"] is False, (
        "reflecting the published draw changed the FAMILY's sign verdict, so this witness moved "
        "more than the one thing it exists to move")
    assert "CENTRE of that family is on the other side of zero" in across["no_sign"], (
        "the draw was placed on the opposite side of zero from the centre of its own family and "
        "the page still did not say so, so the clause is unreachable and says nothing anywhere")

    # WITNESS B -- SOLE WITNESS THAT THE CLAUSE IS A JUDGEMENT. The same rows shifted so every
    # draw is on one side of zero, and nothing else touched. A family with a sign gets no sign
    # clause, and the stated-verdict branch stays exactly as it was.
    one_sided = _floor_with_advantages(admitted, [10000.0, 10100.0, 10200.0])
    stated = gva._current_world_contrast(current, superseded, one_sided, later_runs=[])
    assert stated["verdict_stability"]["sign_determined"] is True, (
        "a family every one of whose draws is positive was read as having no sign")
    assert not stated["no_sign"], (
        "a sign clause was published about a family that holds one sign, so the clause is "
        "unconditional and WITNESS A carries no information")
    assert stated["resolved"] in (True, False) and not stated["verdict_withheld_because"], (
        "the sign gate withheld a verdict on a family with a sign: "
        + str(stated.get("verdict_withheld_because"))[:200])

    # WITNESS C -- THE GATE FIRING ALONE, which needs five rows and cannot be built with three.
    # Every draw here clears the family's own GBP 8.06 spread, so `stable` is True and the
    # stability gate is silent; four of the five are negative and one is positive, so the quantity
    # has no sign. Without this branch the whole gate is an equivalence at today's seed count and
    # this control would be asserting one while reading like a gate.
    straddling = _floor_with_n_advantages(
        admitted, [-9.676, -9.785, -8.095, 8.400, -8.754])
    low_draw = dict(current, level_vs_selection=dict(
        current["level_vs_selection"], value_advantage_gbp=-9.0))
    alone = gva._current_world_contrast(low_draw, superseded, straddling, later_runs=[])
    stability = alone["verdict_stability"]
    assert stability["checked"] is True and alone["bound_available"] is True, (
        "the five-row floor was refused before the sign gate could be reached, so this witness "
        "is measuring another guard: " + str(alone.get("why_no_bound"))[:200])
    assert stability["stable"] is True, (
        "the five draws do not all agree about clearing their own spread, so the stability gate "
        "is what withholds here and this witness cannot show the sign gate doing work of its own")
    assert stability["sign_determined"] is False, (
        "four negative draws and one positive were read as holding a sign")
    assert alone["resolved"] is None and alone["no_sign"], (
        "a direction was stated on a quantity whose own re-draws change sign, on the one branch "
        "where nothing else would have caught it")
    assert alone["verdict_withheld_because"] == alone["no_sign"], (
        "the sign gate fired alone and the published reason is not the sign clause, so the page "
        "states a refusal whose cause it cannot name")
    # AND THE HEADLINE CANNOT RECITE THE STABILITY SENTENCE HERE. Every draw clears the spread, so
    # "N of the M re-draws clear that spread and the rest do not" would be a falsehood -- which is
    # what an unconditional recital of that sentence would print.
    rendered = gva._leg_clause(alone, "LEAD. ", resolved_tail=". ")
    assert "STATES NO VERDICT" in rendered and alone["no_sign"] in rendered, (
        "the headline withheld the verdict without telling the reader the quantity has no sign")
    assert "the rest do not" not in rendered, (
        "the headline recited the stability refusal on a family whose draws all clear their own "
        "spread, so the page states as fact something its own numbers contradict")


def test_the_redraw_family_reaches_the_headline_on_the_branch_that_states_a_verdict():
    """A STATED verdict places its draw in its family and sends the reader to it, not only a
    withheld one -- AND STATES THE FAMILY'S NUMBERS NOWHERE, because they have one home.

    THE DEFECT THIS CLOSES (2026-09-08). The band -- span, mean, and where in it this draw fell --
    reached the headline through `verdict_withheld_because`, so it rendered on exactly the branch
    that refuses to state a direction. Let the seeds agree and the page prints "That figure CLEARS
    the £X this contrast moves across N seed re-draws" and the family vanishes: the reader meets
    the WINNER of the re-draw, told it won, and is never shown the re-draw. That is the failure
    `_verdict_stability` exists to prevent, surviving into the one branch where a direction is
    asserted out loud and so where it costs most.

    AND THE SECOND HALF, LATER THE SAME DAY. The fix above put the family in the headline as a
    RECITAL of min, max and mean -- beside `#arms-redraw`, which renders the same three from
    `verdict_stability.*` as structured cells, per contrast, each failable on its own. One fact,
    two homes, edited on different days for different reasons: the VAT shape CLAUDE.md names by
    its cost. The prose home was retired because it is the one that cannot be partially failed --
    the mean was deletable from it with all 84 door rungs green, measured before it was fixed.

    SO THE ABSENCE IS ASSERTED HERE AND NOT AT THE DOOR, and that placement is the whole reason
    this rung can hold it. The subject's family is SUBSTITUTED (£20,000/£20,100/£20,200) and
    cannot collide with any other figure the clause composes, so "this number is not in this
    sentence" means what it says. Against the live page, `£451` is a substring of `£12,451` and
    the same assertion would be a coin toss on the next re-run.

    THE UNANIMOUS FLOOR IS THE WITNESS AND IT HAS TO BE, because the committed artefacts withhold:
    every control over this could be satisfied by the withheld branch alone, and a control that
    can only be exercised on the branch that was already right proves nothing about the one that
    was wrong. £20,000/£20,100/£20,200 clear their own £100 spread by two orders of magnitude, so
    `resolved` is True, `verdict_withheld_because` is None, and the stated branch is REACHED --
    asserted here rather than assumed, because a subject that quietly withheld would make every
    assertion below a re-test of the branch that already passed.

    AND THAT FAMILY IS PLACED ABOVE THE PUBLISHED DRAW ON PURPOSE. The subject's point estimate
    is this artefact's £12,071, so a family centred on £20,100 makes the honest sentence the
    UNFLATTERING one -- see the placement assertion at the foot of this test for why a witness
    that could only say "ABOVE" would leave the direction a constant.

    KEYED TO THE PROPERTY. The figures are read from the stability block the same build produced,
    never typed, so this does not red when the arms are re-run -- it reds when a verdict branch
    stops placing the draw in its family, and when the retired recital comes back.

    Fires on: dropping `redraw_band` from the stated branch of `_leg_clause`; composing it only
    inside `verdict_withheld_because` again; reporting a family whose edges the block does not
    carry; or restoring the min/max/mean recital to the clause so the band has two homes again.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    admitted = _stamped_after(
        dict(_load(NOISE_FLOOR_ONLY_LIVE),
             redraw_scope=dict(_load(NOISE_FLOOR_ONLY_LIVE)["redraw_scope"],
                               mode=gva.BOUNDING_REDRAW_MODE)), current)
    unanimous = _floor_with_advantages(admitted, [20000.0, 20100.0, 20200.0])
    stated = gva._current_world_contrast(current, superseded, unanimous)
    assert stated["resolved"] is not None and not stated["verdict_withheld_because"], (
        "the unanimous floor did not reach the stated-verdict branch, so this subject re-tests "
        "the withheld one and witnesses nothing")

    clause = gva._current_world_clause(stated)
    assert "CLEARS" in clause or "DOES NOT CLEAR" in clause, (
        "the headline states no verdict off a floor whose every re-draw agrees, so the branch "
        "under test was not rendered")
    stability = stated["verdict_stability"]
    assert stability["checked"], "the unanimous floor produced no stability block to render"
    # THE STATED BRANCH CARRIES THE POINTER. Read from the block the same build produced rather
    # than matched against words this test wrote: `redraw_band` is what `_redraw_band_clause`
    # composed for this contrast, and the property is that the stated branch renders it -- which
    # is exactly what it did not do before 2026-09-08.
    band = stated["redraw_band"]
    assert band and band in clause, (
        "the headline stated a verdict without the sentence placing that figure in its own "
        "family -- the reader is handed a direction and never told the direction came out of a "
        "family, nor where the rest of it is")
    # AND IT CARRIES THE POINTER INSTEAD OF THE NUMBERS, not as well as. The three edges live in
    # `#arms-redraw` as cells that fail one at a time; a recital here is a second home for one
    # fact, and the two are edited on different days for different reasons.
    for edge in ("redraw_min_gbp", "redraw_mean_gbp", "redraw_max_gbp"):
        assert gva._gbp(stability[edge]) not in clause, (
            "the headline recites {} ({}) as well as pointing at the band table, so one fact has "
            "two homes again and only one of them can be partially failed".format(
                edge, gva._gbp(stability[edge])))

    # AND THE PLACEMENT IS MEASURED, NOT ASSERTED FROM TODAY'S DRAW. The published £12,071 sits
    # below the £20,100 centre of this substituted family, so this subject must say BELOW -- the
    # sole witness that the sentence is capable of the unflattering direction on the stated
    # branch. The live artefact draws ABOVE its family, so a witness built from it would leave
    # "ABOVE" a constant that happens to be true rather than a reading that was taken.
    assert "BELOW the centre of its own family" in clause, (
        "the published draw sits under this family's mean and the stated branch did not say so, "
        "so the placement is a constant that happens to be true of the withheld artefact")


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
    admitted = _stamped_after(
        dict(_load(NOISE_FLOOR_ONLY_LIVE),
             redraw_scope=dict(_load(NOISE_FLOOR_ONLY_LIVE)["redraw_scope"],
                               mode=gva.BOUNDING_REDRAW_MODE)), current)
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


def _headline_withholding_only_the_selection_leg(decomposition):
    """The advantage CLEARS its floor and the selection leg does not -- one withheld leg, not two.

    £12,071 is the canonical run's own advantage and it clears ±£2,578; £1,816 is inside it. So a
    remedy appended to this page is appended to a refusal about `selection_gbp` alone, and
    `_decomposition` declares a split of `value_advantage_gbp`. Both other quantity guards pass on
    it by construction: the book is this page's book and the declared contrast IS
    `PAGE_FIGURE_CONTRAST`.
    """
    art = _load(THREE_ARM)
    art["level_vs_selection"] = dict(art["level_vs_selection"],
                                     value_advantage_gbp=12071.08, selection_gbp=1815.79)
    return gva.build(art, _floor_with_spread(2577.80), decomposition)["headline"]


def test_a_remedy_priced_on_a_leg_the_page_resolved_is_refused_rather_than_restated():
    """THE DEFECT (2026-09-04): the page attached a price for resolving one leg to its refusal to
    resolve a DIFFERENT one.

    `_selection_sentence` appended the remedy when `withheld` was true, and that flag was an
    `any(...)` over two contrasts. The quantity guard beside it asked about one -- the module
    constant `PAGE_FIGURE_CONTRAST`. So the OR could be true for the selection leg while the split
    priced the advantage, and nothing anywhere compared the two.

    IT WAS NOT HYPOTHETICAL: IT WAS THIS FILE'S OWN SHARED FIXTURE. `_withheld_headline` withheld
    `selection_gbp` alone against the canonical run's £12,071 advantage, which clears the same
    ±£2,578 floor. Every remedy control here ran on that page, and the page said "it takes about
    54 priced renewals against this book's 120 to bring the bar under the gap" -- a price derived
    from a `value_advantage_gbp` split, printed under a refusal about `selection_gbp`, with "the
    gap" left for the reader to bind. The fixture is corrected in `_withheld_headline`; this test
    holds the property so it cannot come back.

    WHY THE 2026-09-03 GUARD DOES NOT COVER IT. `_decomposition_is_the_same_contrast` was written
    against a page that bounded ONE figure, where "is this the page's figure?" and "is this the
    withheld figure?" were the same question. `5ce6b0f9b` and `074a2c2db` gave the selection and
    level legs bounds of their own and the page now states three. That is the R15 shape "a control
    over a mixed subject reports the OR", arrived at by the subject widening under a control that
    did not move.

    SOLE WITNESS. One leg withheld, the split declaring the OTHER leg, same book, and the declared
    contrast IS `PAGE_FIGURE_CONTRAST` -- so the book guard and the 09-03 contrast guard both pass
    and this control is the only thing that can red.

    R15 -- the mutations, each run and reverted under `python3 -B`:
      * `_decomposition_prices_a_withheld_leg` returns `None` unconditionally (the defect as it
        shipped) -> the witness reds.
      * `_selection_sentence` passes `(gva.PAGE_FIGURE_CONTRAST,)` instead of the legs it actually
        withheld -- the parameter accepted and ignored, which is how a signature-keyed refusal
        lifts -> the witness reds.
      * drop `_which_leg_this_remedy_prices` from the admitting branches -> the naming rung reds.
    The null rung is `both`, which must KEEP the remedy: a control that only ever demands the
    remedy be absent is satisfied by deleting the remedy.
    """
    dec = _decomposition(0.85, resolvable=True)
    assert gva._decomposition_contrast(dec) == gva.PAGE_FIGURE_CONTRAST, (
        "the witness must satisfy the 09-03 contrast guard, or that guard is what reds and this "
        "control is an equivalence of it")
    assert gva._decomposition_is_the_same_book(dec, _load(THREE_ARM)) is None, (
        "the witness must satisfy the BOOK guard, or this control is not the sole reason it reds")

    # SOLE WITNESS. Only `selection_gbp` was withheld; the split prices `value_advantage_gbp`.
    only_selection = _headline_withholding_only_the_selection_leg(dec)
    assert "clearing the ±£2,578" in only_selection, (
        "the witness must have the advantage CLEARING its floor -- otherwise both legs are "
        "withheld, the split does price a withheld leg, and there is no defect to catch: {}"
        .format(only_selection))
    assert "larger SETTLED BOOK" not in only_selection, (
        "the page priced resolving a leg it had just given a direction to -- the defect as it "
        "shipped: {}".format(only_selection))
    assert "DID NOT WITHHOLD" in only_selection, (
        "the refusal must NAME its reason; a silently dropped remedy reads as a question nobody "
        "asked: {}".format(only_selection))
    assert (gva.SELECTION_CONTRAST in only_selection
            and gva.PAGE_FIGURE_CONTRAST in only_selection), (
        "the refusal states neither quantity, so a reader cannot check the pairing it refuses "
        "on: {}".format(only_selection))

    # THE NULL RUNG. Both legs withheld: the split DOES price one of them, so the remedy stands.
    both = _withheld_headline(dec)
    assert "larger SETTLED BOOK" in both, (
        "the null rung: a remedy that prices a leg this page actually withheld was refused "
        "anyway, so this control would be satisfied by deleting the remedy: {}".format(both))
    assert "DID NOT WITHHOLD" not in both, (
        "a remedy priced on a withheld leg was accused of pricing a resolved one: {}".format(both))
    # AND IT NAMES WHICH LEG, because two were withheld and the price is for one of them.
    assert "for that leg alone" in both and gva.SELECTION_CONTRAST in both, (
        "two legs were withheld and the price is for one; the page named neither, so a reader "
        "cannot tell which figure the price resolves: {}".format(both))


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
    block = gva.build(art, _floor_with_spread(2577.80),
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


def _floor_with_selection(floor: dict, values: list) -> dict:
    """The same floor with its per-seed `selection_gbp` replaced AND the published
    `selection_gbp_spread` recomputed from those rows.

    BOTH, because `_seed_spreads` admits no bound on the page unless its own reading of the seed
    rows reproduces the producer's published scalar to the penny. A witness that moved only the
    rows would be witnessing that reconciliation guard rather than the one under test -- the same
    trap `_floor_with_advantages` avoids by not needing to touch the block at all.
    """
    seeds = [dict(seed, selection_gbp=value) for seed, value in zip(floor["seeds"], values)]
    mean = sum(values) / len(values)
    stdev = (sum((v - mean) ** 2 for v in values) / (len(values) - 1)) ** 0.5
    return dict(floor, seeds=seeds,
                selection_gbp_spread={"n": len(values), "stdev": stdev, "mean": mean,
                                      "min": min(values), "max": max(values)})


def test_the_creation_leg_carries_its_own_live_world_bound_and_not_the_advantages():
    """THE DEFECT (2026-09-04): `selection_gbp` reached the reader as a bare point estimate.

    `value_advantage_gbp` is level PLUS selection, and a level advantage is a price charged --
    it moves value, it does not make any. `selection_gbp` is the only leg on this page that could
    be value CREATED, so it is the thesis itself. It was published at +£2,177 with no bound, while
    the only selection spread anywhere on the page was ±£3,776 from the floor that names no world
    -- under a headline declaring that world dead. The floor measured IN this world centres the
    same quantity at -£1,861 across -£8,634 to +£2,350, and one of its three re-draws clears.

    WHY THE SIBLING CONTROLS MISSED IT. Every guard on this block -- world, leg, timestamp, seed
    rows, re-draw stability, five of them, each mutation-proven -- was written against the module
    constant `PAGE_FIGURE_CONTRAST`. All five are correct and all five answer for one leg. The
    repair that bounded the advantage in `a70cc11e1` is the same repair this leg needed, and it
    could not reach here because it was written against a constant instead of a parameter.

    FOUR SUBJECTS, EACH SOLE WITNESS TO ONE THING:
      * LIVE      -- the real artefacts. The bound exists, in this world, on this leg.
      * BORROWED  -- the advantage leg's own bound, asserted DIFFERENT. £991.46 against £5,923.04
        is 6.0x, so a leg that reached for the neighbour's spread would state a verdict the
        neighbour earned. This is the sole witness that the two are separately derived.
      * WORLD     -- the floor stamped into another world. The leg must refuse, which is what
        stops the parameterisation quietly dropping the guard it inherited.
      * UNANIMOUS -- selection rows that all clear their own spread. The verdict must come BACK,
        which is what stops every assertion above being satisfied by "never state a verdict".
    """
    live = _live_digest()
    current = _load(gva.CURRENT_WORLD_THREE_ARM_PATH)
    superseded = _load(NOISE_FLOOR)
    floor_live = _load(gva.CURRENT_WORLD_NOISE_FLOOR_PATH)
    assert ((current.get("world_identity") or {}).get("digest")) == live, (
        "the committed current-world run no longer names the live world, so this control's "
        "subject is gone -- re-run the arms rather than re-pointing the constant")

    # STALE -- the age guard, on a floor stamped BEFORE the run it bounds.
    #
    # WHY THIS IS SYNTHESISED AND NO LONGER READ FROM DISK (2026-09-08). This leg used to assert
    # the REAL pairing was refused for age, and it was: `CURRENT_WORLD_THREE_ARM_PATH` had moved
    # to the 09-08 re-take while every floor on disk predated it. Its own comment said re-running
    # the floor would make it go quiet, and its own message said to drop the leg when that
    # happened. Then the floor landed -- same world, same commit as the arms, 04:10:26Z against
    # their 00:19:54Z -- and the leg reddened for the one reason a control must never redden: the
    # page got a BETTER bound. Dropping it would have taken the only witness that the age guard
    # fires at all, so the subject is manufactured instead of found. Same move the LIVE block
    # below makes, one hour the other way, and it holds whichever artefact's clock leads.
    stale_at = (datetime.datetime.strptime(current["generated_at"], "%Y-%m-%dT%H:%M:%SZ")
                - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    as_found = gva._current_world_contrast(
        current, superseded, dict(floor_live, generated_at=stale_at))["selection_leg"]
    assert as_found["bound_available"] is False, (
        "a floor stamped an hour BEFORE the run it bounds was accepted, so the page can publish "
        "a spread measured on code that predates the figure it claims to bound")
    assert "OLDER THAN THE FIGURE IT BOUNDS" in str(as_found.get("why_no_bound")), (
        "the creation leg is unbounded on a deliberately-stale floor for a reason OTHER than its "
        "age, so this leg witnesses the age guard no longer: "
        + str(as_found.get("why_no_bound"))[:300])

    # LIVE. The creation leg is bounded, in the world it was measured in, on its own contrast --
    # on a floor stamped onto the point estimate's clock, so the wiring is what answers here.
    floor_live = dict(floor_live, generated_at=current["generated_at"])
    block = gva._current_world_contrast(current, superseded, floor_live)
    leg = block["selection_leg"]
    assert leg["bound_available"] is True, (
        "the creation leg carries no bound in the live world: " + str(leg.get("why_no_bound")))
    assert leg["bound_contrast"] == gva.SELECTION_CONTRAST
    assert leg["floor_ran_in_world"] == live
    assert leg["figure_gbp"] == block["selection_gbp"], (
        "the leg block bounds a different number than the one the payload publishes beside it")

    # BORROWED. The two legs' spreads must not be the same number.
    whole = leg["bound"]["stdev_gbp"], block["bound"]["stdev_gbp"]
    assert abs(whole[0] - whole[1]) > 1.0, (
        "the creation leg's bound equals the whole advantage's ({} against {}) -- a spread "
        "measured on one quantity published as a bound on another".format(*whole))

    # THE FAMILY REACHES THE READER, and the count and the placement are in the headline. The
    # placement is the half a range alone will not tell you: this draw is +£2,177 and its own
    # family averages BELOW zero.
    # THE PANEL RUN IS PINNED BY ITS STAMP, not read off `THREE_ARM` (2026-09-09). This composed
    # its headline from the canonical path, which is the PROMOTION TARGET -- so when the 21:01Z
    # re-take was copied onto it, the panel below became LATER than the current-world run, the
    # currency clause went correctly silent, and the count below had nowhere to render. Red on a
    # page that had become more honest, which is the same shape the comment above records this
    # control being bitten by once already. The clause needs the current-world block to be the
    # later of the two, so the pairing is named here instead of inherited from today's release.
    headline = gva.build(_load(THREE_ARM_BEFORE_THE_CURRENT_WORLD_RUN), superseded, None, current, floor_live)["headline"]
    assert leg["verdict_withheld_because"], (
        "a verdict was stated on a leg whose own re-draws reverse it, or withheld with no reason")
    # DERIVED FROM THE FLOOR, NOT WRITTEN DOWN. Until 2026-09-08 these four were the literals
    # "-£8,634", "£2,350", "-£1,861" and "1 of the 3" -- the 09-03 floor's own figures. That made
    # the control keyed to THAT DAY'S ANSWER: re-pointing the constants at a floor measured in the
    # same world, on the same commit as the arms it bounds -- the strictly more honest pairing this
    # file exists to make safe -- turned it red, and nothing about the property had changed. A
    # control that goes red when the page gets a BETTER bound is backwards.
    #
    # AND THE THREE EDGES ARE NO LONGER ASSERTED AGAINST THE HEADLINE, later the same day. They
    # were recited there AND rendered as cells in `#arms-redraw`; one fact with two homes gets
    # edited on two days for two reasons, and the prose home is the one that cannot be partially
    # failed. So the edges are asserted here to be CARRIED -- the table renders what this block
    # holds, and `site/test_the_baseline_comparison_reaches_the_reader.py` asserts each one
    # reaches the reader, per contrast, in that contrast's own row. What the headline still owes
    # is the count and the pointer that places this draw in the family.
    stability = leg["verdict_stability"]
    for edge in ("redraw_min_gbp", "redraw_mean_gbp", "redraw_max_gbp"):
        assert isinstance(stability.get(edge), (int, float)), (
            "the creation leg's verdict was withheld for a family carrying no {}, so the band "
            "table has nothing to render and the refusal is unfalsifiable".format(edge))
    count = "{} of the {}".format(stability["redraw_resolving"], stability["n"])
    assert count in headline, (
        "the creation leg's resolving count ({}) is not on the surface -- the reader is told the "
        "verdict is one draw's and not how many draws disagree".format(count))
    assert leg["redraw_band"] and leg["redraw_band"] in headline, (
        "the creation leg's point estimate reached the reader with nothing placing it in its own "
        "family and no route to the rest of that family")
    # AND THE CENTRE IS NOT THE PUBLISHED DRAW. The whole reason the placement is on the surface
    # is that a single draw can sit anywhere in its own family; a control satisfied by "a number
    # appears" would pass if the page printed the point estimate three times.
    assert gva._gbp(stability["redraw_mean_gbp"]) != gva._gbp(leg["figure_gbp"]), (
        "the family centre renders identically to the published draw, so this control cannot "
        "tell the two apart and the reader cannot either")

    # WORLD. The inherited guard still bites on the parameterised leg.
    elsewhere = gva._current_world_contrast(
        current, superseded, _world_stamped(floor_live, "another-world"))["selection_leg"]
    assert elsewhere["bound_available"] is False and elsewhere["resolved"] is None, (
        "a floor from another world bounded the creation leg -- the world guard did not survive "
        "being given a contrast parameter")

    # UNANIMOUS. The null rung: a leg whose re-draws agree gets its verdict back.
    agreeing = gva._current_world_contrast(
        current, superseded,
        _floor_with_selection(floor_live, [8000.0, 9000.0, 10000.0]))["selection_leg"]
    assert agreeing["resolved"] is not None, (
        "the creation leg withheld a verdict on a floor whose re-draws all agree, so every "
        "assertion above is satisfied by a block that never states one")


#: Every sterling amount this page composes carries its sign OUTSIDE the symbol. Asserted as the
#: shape and not as a list of figures, so a lead written next month is covered without editing
#: this control -- `£-` can only ever be produced by a bare `"£{:,.0f}"` over a signed quantity.
SIGN_INSIDE_THE_SYMBOL = "£-"


def test_a_negative_leg_in_the_headline_puts_its_sign_outside_the_pound():
    """THE DEFECT (2026-09-04, LATENT): the two point estimates a reader quotes could print `£-`.

    `_gbp` was written the day the creation leg reached the headline, and its docstring names
    these two figures as the reason: the leg's own re-draw family in this world centres BELOW
    zero and its range cannot be `abs()`-ed away, so the sign is the finding. It reached the
    RANGE under each lead and NEITHER LEAD -- `_current_world_clause` formatted both point
    estimates through a bare `£{:,.0f}`. So on the day either draw comes out negative the
    sentence reads `£-1,861` while the range three clauses later reads `-£8,634` correctly: two
    renderings of one quantity's sign, inside one sentence, and the wrong one on the half a
    reader quotes.

    NEITHER FIGURE IS A MAGNITUDE, WHICH IS WHY THIS IS NOT PEDANTRY. Every other sterling amount
    on this page is either a spread (non-negative) or passed through `abs()` with the direction
    said in words. These two are signed by construction: the advantage's own re-draws in this
    world span £451 to £2,434 and the creation leg's CENTRE across the same three draws is
    -£1,861 -- the page already prints that figure, so the negative branch is measured, not
    hypothetical.

    LATENT, AND THAT IS EXACTLY WHY IT NEEDS A CONTROL RATHER THAN AN EYE. Today's published
    draws are both positive, so the repair moves no rendered value and no amount of looking at
    the live page could reach the branch.

    THE NULL RUNG IS THE SECOND HALF. A control that only demands `£-` be absent is satisfied by
    deleting the figures, so both leads must still CARRY their amount, in `_gbp`'s rendering.

    Fires on: reverting either lead in `_current_world_clause` to `£{:,.0f}`.
    """
    block = gva._current_world_contrast(
        _load(gva.CURRENT_WORLD_THREE_ARM_PATH), _load(NOISE_FLOOR),
        _load(gva.CURRENT_WORLD_NOISE_FLOOR_PATH))
    assert block.get("available"), (
        "there is no live-world block to render, so this control has no subject: {}".format(
            block.get("why_not")))

    # THE REAL BLOCK WITH TWO SIGNS FLIPPED, never a hand-built stub: every other key stays
    # exactly what the live artefacts produced, so what this renders is the sentence the page
    # would compose on the day the draw came out the other way and nothing else.
    negative = copy.deepcopy(block)
    negative["value_advantage_gbp"] = -abs(block["value_advantage_gbp"])
    negative["selection_leg"]["figure_gbp"] = -abs(block["selection_leg"]["figure_gbp"])
    clause = gva._current_world_clause(negative)

    assert SIGN_INSIDE_THE_SYMBOL not in clause, (
        "a negative amount reached the headline with its sign inside the pound: {}".format(
            clause[:400]))
    for figure in (negative["value_advantage_gbp"], negative["selection_leg"]["figure_gbp"]):
        assert gva._gbp(figure) in clause, (
            "the lead dropped its own amount rather than rendering it -- {} is not in the "
            "clause, so the assertion above is satisfied by a sentence with no figure in "
            "it".format(gva._gbp(figure)))

    # AND THE POSITIVE CASE IS UNCHANGED. `_gbp` emits no leading `+`, so the live page's own
    # wording must not have moved -- a sign fix that silently restyled the published sentence
    # would be a different change wearing this one's name.
    assert gva._gbp(block["value_advantage_gbp"]) in gva._current_world_clause(block), (
        "the published positive draw stopped rendering in the words it was published in")


def test_a_bound_whose_floor_names_no_world_is_refused_and_the_refusal_reaches_the_reader():
    """THE DEFECT (2026-09-04): the page contradicted itself inside one paragraph.

    The headline led with "no contrast below may have its direction read as resolved" -- derived
    from `_world_provenance` -- and then, two sentences later, stated "£12,071 MORE than flat
    rules, clearing the ±£2,291 this figure moves across 3 seed re-draws". Both sentences were
    derived; neither was wrong about its own input; and the second took its bound from a floor
    whose `world_identity` is null. Every guard on `_seed_spreads` was about the BOOK -- whether
    the floor predates the point estimate, whether its rows reproduce its published spread. None
    could see the world, so an unstamped spread licensed a direction on the one page whose whole
    purpose is to be able to return an unflattering answer.

    A DIGEST IS REQUIRED, NOT THE LIVE ONE. This block bounds the SUPERSEDED panel, which is
    published on purpose beside the live one -- demanding equality with the live world here would
    refuse a pairing the page makes deliberately. `_current_world_bound` is where equality is
    demanded, and it still is.

    TWO SUBJECTS. The real superseded floor is the sole witness that the refusal fires; the same
    floor stamped with the RUN'S OWN world is the null rung, and it must put the direction BACK --
    otherwise this is a control satisfied by a feed that refuses everything for ever.

    THE NULL RUNG USED TO SAY "any digest at all" AND THAT IS NOW FALSE (2026-09-09), which is
    the point rather than an inconvenience. `_seed_spreads` gained the comparison this docstring's
    second paragraph never made: not equality with the LIVE world -- that is still refused, and
    `_current_world_bound` is still where it is demanded -- but equality with the world of the
    FIGURE this spread would bound. A floor stamped `"any-world"` against a run in
    `39a192ce04c1eda8` is exactly the pair that block was measured admitting, one second of stamp
    order being all it asked for. So the rung is stamped with the run's own digest: it still
    proves the guard is the world-naming and not a machine for refusing, and it no longer proves
    it by licensing the mismatch.
    """
    # THE WITNESS IS A DATED FLOOR, NEVER THE CANONICAL PATH (2026-09-09). This read `NOISE_FLOOR`,
    # which HELD these bytes and therefore had the property by accident; promoting the 09-08b floor
    # onto that path gave it a world digest and this control lost the only subject that can reach
    # its refusal. A witness for "names no world" has to be a file that can never gain a stamp.
    # Stamped forward so the AGE guard is not what refuses it -- the world guard is on trial.
    floor = _stamped_after(_load(NOISE_FLOOR_NO_WORLD), _load(THREE_ARM))
    assert ((floor.get("world_identity") or {}).get("digest")) is None, (
        "the superseded floor now names a world, so this control has lost its witness -- the "
        "refusal it guards can no longer be reached from the real artefact")

    refused = gva._seed_spreads(floor, _load(THREE_ARM))
    assert refused["available"] is False, (
        "bounds were published from a floor that names no world it was measured in")
    assert refused["world_measured_in"] is None
    assert "world" in refused["reason"], (
        "the refusal does not name its cause, so a reader is sent to re-run a floor that has "
        "already been run rather than to stamp the one on disk")

    # AND IT REACHES THE PAGE, not just the payload. A refusal computed and never rendered is a
    # fail-silent: the direction would still be on the surface with the block below saying no.
    headline = gva.build(_load(THREE_ARM), floor)["headline"]
    for claim in _DIRECTIONAL_CLAIMS:
        assert claim not in headline, (
            "the headline still states a direction off an unstamped bound: " + claim)
    assert "names no world it was measured in" in headline

    # THE NULL RUNG. Stamp it with the run's own world and the direction comes back with nothing
    # else edited, which is what proves the guard is the world and not a machine for refusing.
    run = _load(THREE_ARM)
    stamped = gva._seed_spreads(
        _world_stamped(floor, run["world_identity"]["digest"]), run)
    assert stamped["available"] is True, str(stamped.get("reason"))[:200]
    # ...AND A WORLD THAT IS NOT THE RUN'S DOES NOT. The two rungs together are what separate
    # "names a world" from "names the figure's world": before 2026-09-09 this leg was the null
    # rung, and it passed.
    mismatched = gva._seed_spreads(_world_stamped(floor, "any-world"), run)
    assert mismatched["available"] is False, (
        "a floor stamped with a world that is not the figure's published its spread as the bound "
        "on that figure, which is the fail-open the age guard was the only thing standing in "
        "front of")
    assert stamped["world_measured_in"] == run["world_identity"]["digest"], (
        "the admitting branch does not publish which world these bounds describe, so the pairing "
        "is checkable only from a docstring")
    back = gva.build(_load(THREE_ARM),
                     _world_stamped(floor, run["world_identity"]["digest"]))["headline"]
    assert any(claim in back for claim in _DIRECTIONAL_CLAIMS), (
        "a stamped floor still states no direction, so this guard refuses regardless of its "
        "subject and its red above carries no information")


def _floor_with_level_legs(floor: dict, values: list) -> dict:
    """The same floor with its per-seed level leg replaced, and the share it implies moved with it.

    THE SHARE MOVES TOO, ON PURPOSE. `level_share_of_advantage` is the level leg over the whole
    advantage in the SAME row, so a fixture that changed the numerator and left the share alone
    would be a floor that could never have been measured -- and the control would then pass on a
    subject the producer cannot emit. The denominator is left exactly as the live artefact has it.
    """
    seeds = []
    for seed, value in zip(floor["seeds"], values):
        whole = seed["value_advantage_gbp"]
        seeds.append(dict(seed, level_advantage_gbp=value,
                          level_share_of_advantage=value / whole,
                          selection_gbp=whole - value))
    return dict(floor, seeds=seeds)


def _stamped_after(floor: dict, run: dict | None = None) -> dict:
    """The same floor, stamped LATER than the run it will bound.

    THE FIXTURE FLOORS ON DISK ARE DATED AND `THREE_ARM` IS A MOVING POINTER (2026-09-09). Every
    subject in this file pairs a dated floor artefact with whatever run is currently promoted to the
    canonical path, and `_staleness_caveat` refuses a bound stamped before the figure it bounds --
    correctly, and it is one of this page's load-bearing refusals. So the day the 2026-09-08b run
    was promoted, ten controls whose subject is the WORLD guard, the LEG guard or the STABILITY
    guard were refused by the STALENESS guard instead, and each of them reported the failure of the
    guard it names rather than the one that fired. A green suite would have told the same lie in
    reverse the day the floor artefact was newer by accident.

    THE STAMP IS DERIVED FROM THE RUN, NEVER READ OFF THE ARTEFACT. What these subjects need is the
    PROPERTY "this floor postdates the figure it bounds", and a fixed date has that property only
    against the runs that happen to predate it.
    """
    when = ((run if isinstance(run, dict) else _load(THREE_ARM)) or {}).get("generated_at")
    if not isinstance(when, str) or not when:
        return dict(floor)
    later = (datetime.datetime.fromisoformat(when.replace("Z", "+00:00"))
             + datetime.timedelta(hours=1))
    return dict(floor, generated_at=later.strftime("%Y-%m-%dT%H:%M:%SZ"))


def _admitted_live_floor(run: dict | None = None) -> dict:
    """The live-world floor relabelled to the bounding leg -- the subject the world/leg guards pass.

    Stamped after the run it bounds by `_stamped_after`, so the staleness guard is not what refuses
    it; see that helper for the ten controls that went red reporting the wrong guard.
    """
    only_live = _load(NOISE_FLOOR_ONLY_LIVE)
    return _stamped_after(
        dict(only_live, redraw_scope=dict(only_live["redraw_scope"],
                                          mode=gva.BOUNDING_REDRAW_MODE)), run)


def test_the_level_leg_carries_its_own_bound_measured_in_this_world():
    """The THIRD leg reaches the bound apparatus, instead of being published as a bare number.

    THE DEFECT IT SERVES. `a70cc11e1` bounded `value_advantage_gbp`. The 2026-09-04 repair made
    the contrast a parameter so `selection_gbp` could reach the same machinery. Both times
    `level_advantage_gbp` was left one line below as a bare point estimate -- the identical
    omission, a third time, on the leg a reader is LEAST likely to question because "a price
    charged" sounds like something the company controls.

    IT IS NOT THE SAFE LEG. On this world's own floor the level leg runs -£882.45 to +£9,085.08
    across three re-draws and changes sign, against a point estimate of £159.21: the least
    determined of the three figures on the page.

    Fires on: dropping the leg; flattening it over `selection_leg` (the two share key names, so a
    spread would silently bound the wrong figure); or reaching for a bound the world/leg guards
    would have refused.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    block = gva._current_world_contrast(current, _load(NOISE_FLOOR), _admitted_live_floor())

    leg = block["level_leg"]
    assert leg["bound_available"] is True, (
        "the level leg reaches no bound: " + str(leg.get("why_no_bound"))[:200])
    assert leg["bound_contrast"] == gva.LEVEL_CONTRAST, (
        "the level leg is bounded by another contrast's spread -- the exact defect nesting the "
        "legs exists to prevent")
    assert leg["figure_gbp"] == current["level_vs_selection"]["level_advantage_gbp"]
    # AND IT IS NOT THE SELECTION LEG'S BOUND WEARING ITS NAME.
    assert leg["bound"]["stdev_gbp"] != block["selection_leg"]["bound"]["stdev_gbp"], (
        "the level and selection legs report an identical spread, so one is being bounded by the "
        "other's -- which is what flattening these blocks would produce")


def test_the_level_share_is_refused_when_its_numerator_has_no_sign():
    """A share whose numerator changes sign across re-draws of it is not a composition.

    THE DEFECT IT SERVES, and it is the residue `09009c236` named as still unwritten. The page
    published 78.7% in the superseded panel and left 6.8% derivable from `current_world` and
    stated nowhere, with nothing beside either saying that a share of the advantage mostly reads
    how much book there is to win or lose -- the world's departure level and price response --
    rather than the company's skill.

    KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. The refusal fires on the level leg not being
    sign-determined across the floor's own re-draws, not on the share being small. Repair the
    mechanism so the leg holds a sign and the refusal lifts by itself -- which is the direction a
    control is supposed to move in.

    TWO SUBJECTS, AND THE SECOND IS WHAT MAKES THIS A CONTROL. The live floor alone would be
    satisfied by a block that refused unconditionally; the sign-stable floor is the sole witness
    that the refusal is a judgement. Its rows are the live artefact's own, shifted by a constant
    large enough to put every draw on one side of zero and nothing else touched.

    Fires on: refusing unconditionally; reading the share as a composition; dropping the
    two-worlds sentence from either branch; or re-dividing the two figures here instead of
    reading the share the producer already computed behind its own guard.

    `later_runs=[]` ON EVERY SUBJECT, AND IT IS THE SUBJECT DECLARING ITSELF. Since 2026-09-07 the
    block carries a SECOND, independent refusal -- a later run over the same world disagreeing
    about which leg the advantage is made of -- and on the real directory it fires, because one
    does. Left to scan, WITNESS B would be refused for that reason and this control would report
    "refuses regardless of its subject" about a block that does not. The empty census is what
    isolates the sign property being tested here; the other property has its own control,
    `test_a_later_run_in_this_world_that_disagrees_about_the_split_refuses_the_composition`.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    admitted = _admitted_live_floor()

    # WITNESS A -- the live artefact's own rows: -882.45, +1,733.38, +9,085.08. No sign.
    refused = gva._current_world_contrast(current, superseded, admitted, later_runs=[],
                                          superseded_split={"level_share_of_advantage": 0.7867})
    comp = refused["composition"]
    assert comp["available"] is True, str(comp.get("reason"))[:200]
    assert comp["readable"] is False, (
        "the page read a share whose numerator changes sign across its own re-draws")
    assert "CHANGES SIGN" in comp["why_not_readable"]
    assert comp["level_share_of_advantage"] == pytest.approx(
        current["level_vs_selection"]["level_share_of_advantage"]), (
        "the share was re-derived here instead of read from the run, so the producer's "
        "undefined-denominator guard now has a second implementation")

    # WITNESS B -- the sole witness that the refusal is a judgement. Same rows, shifted so every
    # draw is positive; nothing else edited.
    stable = _floor_with_level_legs(admitted, [1_000.0, 1_733.378959, 9_085.082015])
    allowed = gva._current_world_contrast(current, superseded, stable, later_runs=[],
                                          superseded_split={"level_share_of_advantage": 0.7867})
    assert allowed["composition"]["readable"] is True, (
        "a floor whose level leg holds one sign is still refused, so this block refuses "
        "regardless of its subject and its red above carries no information: "
        + str(allowed["composition"].get("why_not_readable"))[:200])

    # WITNESS C -- THE THIRD STATE, NAMED. A floor with no level-leg rows has not shown the share
    # unreadable; it could not be asked. Folding that into `readable: False` would tell a reader
    # "we measured it and it has no sign" when nothing was measured -- and written after the sign
    # test it was an unreachable branch that crashed on an empty range, which this file's own
    # suite caught on the foreign-world subject.
    unasked = gva._current_world_contrast(current, superseded, dict(admitted, seeds=[]),
                                          later_runs=[],
                                          superseded_split={"level_share_of_advantage": 0.7867})
    assert unasked["composition"]["readable"] is None, (
        "a floor that could not be asked is reported as an answer")
    assert "not asked" in unasked["composition"]["why_not_readable"]

    # THE SUPERSEDED-PANEL SENTENCE IS ON EVERY BRANCH, because it is true whichever way the
    # refusal above fell and it is the sentence the discharge named as missing.
    #
    # ITS ATTRIBUTION CLAUSE IS NOW KEYED TO A COUNT AND NOT TO PROSE (2026-09-08). This loop used
    # to assert the literal "DIFFERENT WORLDS" and "more than one thing changed" -- a control
    # pinned to today's answer, and pinned to an answer that was already wrong: the sentence said
    # the two runs were measured in different worlds while the canonical 2026-08-31 artefact
    # carries no `world_identity` at all, so the page could not establish either world. The three
    # subjects above pass no superseded RUN, so the honest branch for them is "not established";
    # what the sentence must carry on every branch is the SHARE and the refusal to read it as
    # company skill.
    for block in (comp, allowed["composition"], unasked["composition"]):
        assert "78.7%" in block["against_the_superseded_panel"]
        assert ("may not be read as the company having got better or worse"
                in block["against_the_superseded_panel"]), (
            "the branch dropped the director's own refusal, so a reader meets a moved share with "
            "nothing beside it: " + block["against_the_superseded_panel"])
        assert "has not established which of the world" in block[
            "against_the_superseded_panel"], (
            "a block built with no superseded run still asserted what differs between the two "
            "runs: " + block["against_the_superseded_panel"])


def _run_stamped(world: str | None, when: str, commit: str | None) -> dict:
    """A run carrying only the three fields the attribution count reads. `None` omits the field."""
    run = {"generated_at": when}
    if world is not None:
        run["world_identity"] = {"digest": world}
    if commit is not None:
        run["producing_commit"] = {"commit": commit}
    return run


def test_the_superseded_panels_attribution_is_COUNTED_and_the_whole_partition_is_reachable():
    """The two panels' difference is attributed from a count of what differs, never from prose.

    THE LIVE DEFECT IT FIRES ON, and it was published, not hypothetical. On 2026-09-08 the feed's
    own headline read: "IN THE WORLD AS IT IS NOW, the same comparison gives £17,739 ... It is a
    SMALLER advantage than the £12,071 below, not a larger one: what moved is the floor, which fell
    further than the advantage did." £17,739 is LARGER than £12,071. The literal, the direction and
    the cause were all typed in when the current-world figure was £2,336; `CURRENT_WORLD_THREE_ARM_PATH`
    was moved to the 2026-09-08 run in `8e90037a5` and the sentence describing the pair was not, so
    the page asserted the opposite of the arithmetic between the two figures it names and
    foreclosed the correct reading in the same breath. Beside it, `against_the_superseded_panel`
    said the two were "measured in DIFFERENT WORLDS" while the canonical artefact carries no
    `world_identity` at all.

    ONE CONTROL OVER THE WHOLE PARTITION, not a leg per branch. A count that returned "two or more"
    for everything would satisfy every individual branch assertion that mattered on the day it was
    written -- which is exactly how the sentence above survived. So the reachability of all four
    states is asserted together, and the direction clause is asserted to TRACK the arithmetic
    rather than to hold any particular value.

    Fires on: hard-coding any figure or direction back into either sentence; collapsing the
    same-run branch into the two-or-more branch; or counting an ABSENT field as differing or as
    matching.
    """
    a = _run_stamped("world_aaaa", "2026-09-08T21:01:30Z", "commit_aaa")
    # THE FOUR STATES, each differing from `a` in exactly what its name says.
    three = _run_stamped("world_bbbb", "2026-08-31T03:47:57Z", "commit_bbb")
    one = _run_stamped("world_aaaa", "2026-09-08T21:01:30Z", "commit_bbb")
    same = _run_stamped("world_aaaa", "2026-09-08T21:01:30Z", "commit_aaa")
    blind = _run_stamped(None, "2026-09-08T21:01:30Z", "commit_aaa")

    counts = {name: gva._what_differs_between_two_runs(a, other)
              for name, other in (("three", three), ("one", one),
                                  ("same", same), ("blind", blind))}

    # THE PARTITION, IN ONE ASSERT. Every state must be reachable; a counter stuck on any single
    # answer fails here rather than passing three of four assertions elsewhere.
    assert (counts["three"]["how_many_differ"] == 3
            and counts["one"]["how_many_differ"] == 1
            and counts["same"]["the_same_run"] is True
            and counts["blind"]["unestablished"] == ["the world it ran in"]), (
        "the attribution count cannot reach all four of its states, so whichever sentence it "
        "publishes is a constant: " + repr({k: v for k, v in counts.items()}))
    # AN ABSENT FIELD IS NEITHER, and that is the load-bearing case: counted as differing it
    # manufactures the refusal, counted as matching it manufactures a one-variable claim.
    assert counts["blind"]["how_many_differ"] == 0
    assert counts["blind"]["the_same_run"] is False, (
        "two runs agreeing on the fields a third could not be read from were called the same run")

    sentences = {name: gva._against_the_superseded_panel(0.7867, count)
                 for name, count in counts.items()}
    assert "more than one thing changed" in sentences["three"]
    assert "exactly ONE differs" in sentences["one"]
    assert "SAME RUN" in sentences["same"]
    assert "could not be read at all" in sentences["blind"]
    # THE DIRECTOR'S REFUSAL IS ON EVERY BRANCH, because it is a property of the quantity.
    for name, sentence in sentences.items():
        assert "may not be read as the company having got better or worse" in sentence, name
        assert "DIFFERENT WORLDS" not in sentence, (
            name + ": a world difference is asserted in prose again")

    # AND THE HEADLINE'S DIRECTION TRACKS THE ARITHMETIC of the two figures it names.
    def clause(now, before):
        return gva._against_the_panels_figure(
            now, {"superseded_value_advantage_gbp": before})

    assert "LARGER" in clause(17_738.64, 12_071.08), (
        "the published pair that made the old sentence false still does not read as larger")
    assert "SMALLER" in clause(2_335.87, 12_071.08)
    assert "SAME advantage" in clause(17_452.61, 17_452.61), (
        "one run promoted to both paths still reads as a comparison of two measurements")
    # NO CAUSE IS CLAIMED. The old sentence attributed the move to the floor falling further than
    # the advantage; that was measured for one pair and cannot be true of every pair.
    for pair in ((17_738.64, 12_071.08), (2_335.87, 12_071.08)):
        assert "what moved is the floor" not in clause(*pair)
    assert "no comparison" in clause(17_452.61, None), (
        "a panel that states no advantage still had one compared against it"
    )


def test_the_level_legs_family_is_POINTED_AT_by_the_share_refusal_and_never_recited_beside_it():
    """The band's FOURTH home, closed. The refusal names the table; the table holds the numbers.

    THE DEFECT IT SERVES. `656a45f54` moved the re-draw family's three edges out of `_leg_clause`
    into `#arms-redraw`, where each is a cell that reds on its own column, and retired the prose
    home rather than leaving it alongside — one fact with two homes gets edited on two days for
    two reasons, which is this repository's named VAT shape. Its own message recorded the residue:
    `_composition_in_this_world` recited the LEVEL leg's min and max in prose of its own, over the
    same floor rows, beside that leg's own row in the same table. A fourth home, a different
    producer, its own controls, and out of scope that day.

    IT WAS LATENT, NOT LIVE, AND THAT IS WHY THE SUBJECT IS SUBSTITUTED. On the published world
    the level leg is sign-stable, so the refusal does not fire and no reader has ever met the
    duplicate. It arms itself on any world whose level leg straddles zero — which is the state
    `NOISE_FLOOR_ONLY_LIVE` is in, and that floor is this rung's witness.

    THE POINTER IS ASSERTED NOT TO BE A LIE, which is the leg that makes this more than a
    substring check. A sentence sending a reader to a table holding DIFFERENT numbers is worse
    than the recital it replaced, so the family the sign test ran over and the family the table
    renders are asserted to be the same two edges, off the floor's own rows. Two routes to one
    number is exactly what the collapse was for.

    KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. Every figure is read from the block the build
    produced. A re-run that moves every re-draw leaves this green; what reds is a number appearing
    in two places at once.

    Fires on: restoring the min/max recital beside the pointer; pointing at the table from the
    branch where that table's row carries no family; rendering the level row from another
    contrast's family; or letting the mean leak into a sentence that never held it.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded = _load(NOISE_FLOOR)
    admitted = _admitted_live_floor()

    built = gva._current_world_contrast(current, superseded, admitted, later_runs=[],
                                        superseded_split={"level_share_of_advantage": 0.7867})
    comp, leg = built["composition"], built["level_leg"]
    said = comp["why_not_readable"] or ""
    assert comp["readable"] is False and "CHANGES SIGN" in said, (
        "the straddling floor did not reach the refusing branch, so this subject witnesses "
        "nothing: " + str(comp.get("readable")))
    stability = leg["verdict_stability"]
    assert stability.get("checked"), (
        "the band table's price-level row carries no family on this subject, so the branch under "
        "test is the fallback and not the pointer: " + str(stability.get("why_not"))[:160])

    # THE POINTER IS NOT A LIE. The refusal's own sign test runs over the floor's `level_gbp`
    # rows; the table's price-level row renders `_verdict_stability`'s reduction of those SAME
    # rows. Asserted off the floor rather than taken from either, so a producer that quietly
    # bounded one leg with another's family reds here rather than shipping a sentence that sends
    # the reader to numbers the refusal was never computed from.
    rows = sorted(float(seed[gva.LEVEL_CONTRAST]) for seed in admitted["seeds"])
    assert (stability["redraw_min_gbp"], stability["redraw_max_gbp"]) == (rows[0], rows[-1]), (
        "the table's price-level row and this refusal are reading different families ({} vs {}), "
        "so the sentence points a reader at numbers it was not computed from".format(
            (stability["redraw_min_gbp"], stability["redraw_max_gbp"]), (rows[0], rows[-1])))

    # ONE HOME. The edges live in `#arms-redraw` as cells that fail one at a time; a recital here
    # is the second home, and the mean was never in this sentence at all — it must not arrive.
    for edge in ("redraw_min_gbp", "redraw_mean_gbp", "redraw_max_gbp"):
        assert gva._gbp(stability[edge]) not in said, (
            "the share refusal recites {} ({}) as well as pointing at the band table, so the "
            "level leg's family has two homes again and only one of them can be partially "
            "failed".format(edge, gva._gbp(stability[edge])))
    assert "band table" in said, (
        "the refusal states neither the numbers nor a route to them, so a reader is told the leg "
        "changes sign and given no way to see by how much")

    # THE PARTITION, AND `level_stability` IS THE ONLY THING THAT MOVES BETWEEN THE TWO SUBJECTS.
    # Nothing else can explain a difference. The fallback is not tidiness: `_verdict_stability`
    # refuses when no bound was read in this world, and the refusal's own `measured` drops short
    # rows instead — so it can hold two straddling draws where the table's row renders NOT
    # RE-DRAWN. Pointing there would send the reader to the gap, so the numbers must stay.
    contrast = current["level_vs_selection"]
    pointed = gva._composition_in_this_world(contrast, admitted, 0.7867, live, later_runs=[],
                                             level_stability=stability)
    recited = gva._composition_in_this_world(
        contrast, admitted, 0.7867, live, later_runs=[],
        level_stability={"checked": False, "why_not": "no bound was read in this world"})
    assert pointed["why_not_readable"] == said, (
        "the direct call does not reproduce what the build published, so the two subjects below "
        "differ by more than the one thing this rung moves")
    for edge in ("redraw_min_gbp", "redraw_max_gbp"):
        assert gva._gbp(stability[edge]) in recited["why_not_readable"], (
            "the band table's price-level row carries no family and the refusal points at it "
            "anyway, so {} reaches no reader in either place".format(edge))
    assert gva._gbp(stability["redraw_mean_gbp"]) not in recited["why_not_readable"], (
        "the fallback recites a centre this sentence has never carried and the table cannot "
        "render, which is a third statement of the family rather than the only one")
    assert pointed["why_not_readable"] != recited["why_not_readable"], (
        "the pointer and the fallback render identically, so one of the two branches is "
        "unreachable and every assertion above holds of a single sentence")

    # AND THE WIRING, WHICH THE PAIR ABOVE IS BLIND TO. Calling the producer directly proves the
    # sentence can fall back; it cannot prove the BUILD hands over the price-level row's own
    # family rather than some other checked one. Measured, not argued: substituting the whole
    # advantage's `verdict_stability` at the call site left the whole of this file green, because
    # on the subject above both families are checked and the pointer branch reads no number out
    # of either. So the witness is a floor where they DISAGREE — one seed row short of the level
    # contrast, nothing else touched, which is enough for `_verdict_stability` to refuse that leg
    # while the advantage's own family still checks. Handing the wrong one over then prints a
    # pointer at an amber NOT RE-DRAWN cell, and the two edges reach no reader anywhere.
    short = dict(admitted, seeds=[
        {k: v for k, v in seed.items() if not (i == 1 and k == gva.LEVEL_CONTRAST)}
        for i, seed in enumerate(admitted["seeds"])])
    crossed = gva._current_world_contrast(current, superseded, short, later_runs=[],
                                          superseded_split={"level_share_of_advantage": 0.7867})
    assert crossed["verdict_stability"]["checked"] and not (
        crossed["level_leg"]["verdict_stability"]["checked"]), (
        "the two families agree about being checked on this subject, so it cannot witness which "
        "of them the build hands over")
    fell_back = crossed["composition"]["why_not_readable"] or ""
    assert "CHANGES SIGN" in fell_back, (
        "the short floor did not reach the refusing branch, so nothing below is a witness")
    for edge in ("redraw_min_gbp", "redraw_max_gbp"):
        assert gva._gbp(stability[edge]) in fell_back, (
            "the build pointed at the band table while the price-level row of that table carries "
            "no family, so {} is on no surface at all: the reader is told the leg changes sign "
            "and shown nothing that says by how much".format(edge))


DOOR = PROJECT / "site" / "capabilities" / "index.html"

#: The band table every pointer below sends a reader to.
_THE_BAND_TABLE = "arms-redraw"

#: WHAT A POINTER IS ALLOWED TO SAY, and what each phrase CLAIMS about where that table sits.
#: The first element is the anchor the claim is relative to; `None` means "relative to wherever
#: this sentence happens to render", which is the shape that broke -- a producer does not know how
#: many homes its own output has, and this one had two on opposite sides of the table.
#:
#: `higher up this section` is RETIRED and kept here on purpose. Dropping it would make restoring
#: the old wording red as an unrecognised phrase rather than as the lie it was, and a refusal that
#: names the wrong reason is how a correct fix gets reverted.
_POINTER_PHRASES = {
    "directly below this headline": ("arms-headline", "below"),
    "under the headline figure": ("arms-headline", "below"),
    "higher up this section": (None, "above"),
}

#: The words that make a sentence a POINTER at all, rather than prose that happens to mention the
#: table. Scoped deliberately wide: a sentence naming the table and giving no direction is caught
#: by the fail-closed leg below, not waved through.
_POINTS_AT_THE_TABLE = "band table"


def _the_doors_reading_order() -> dict:
    """`{anchor id: position}` in the order a reader scrolls the section, from the door itself.

    SOURCE ORDER IS THE SUBJECT, and it is the right one here because every anchor this reads is a
    static element of `site/capabilities/index.html` -- the door assigns `innerHTML` into them and
    never reorders them, so document order IS what a reader meets. A control that drove the render
    would measure the same thing through a node process and could not see an anchor the JS never
    fills, which is exactly the state a moved block would be in.
    """
    html = DOOR.read_text(encoding="utf-8")
    order, seen_twice = {}, set()
    for position, match in enumerate(re.finditer(r'id="(arms-[a-z-]+)"', html)):
        anchor = match.group(1)
        if anchor in order:
            seen_twice.add(anchor)
        else:
            order[anchor] = position
    assert not seen_twice, (
        "the door declares {} more than once, so 'where it sits' has no answer and every pointer "
        "below is judged against an arbitrary one of them".format(sorted(seen_twice)))
    return order


def _the_regions_a_sentence_reaches(sentence: str, built: dict) -> set:
    """Which page regions a producer's sentence actually renders in -- DERIVED, never declared.

    THIS IS THE HALF THAT WAS MISSING. `_the_level_legs_family`'s own docstring declared its home
    ("`#arms-composition` sits BELOW `#arms-redraw`") and reasoned from it; the declaration was
    true and incomplete, and nothing could notice because nothing else in the tree held an opinion
    about where that sentence rendered. So the homes are taken by running the composers the door
    reads from: `_current_world_clause` is what `#arms-headline` renders, and
    `composition.why_not_readable` is what `#arms-composition` renders. A producer that gains a
    third home gains it here too, without anyone remembering to edit a list.
    """
    homes = set()
    if sentence and sentence in (gva._current_world_clause(built) or ""):
        homes.add("arms-headline")
    if sentence and sentence in (((built.get("composition") or {}).get("why_not_readable")) or ""):
        homes.add("arms-composition")
    return homes


def _pointer_defects(sentence: str, homes: set, order: dict) -> list:
    """Every way one pointer sentence can be false, judged in EVERY region it renders in."""
    defects = []
    if _POINTS_AT_THE_TABLE not in sentence:
        return ["the sentence does not point at the band table at all: " + sentence[:120]]
    if _THE_BAND_TABLE not in order:
        return ["the door no longer declares #{}, so the sentence points at nothing".format(
            _THE_BAND_TABLE)]
    said = [phrase for phrase in _POINTER_PHRASES if phrase in sentence]
    # FAIL CLOSED ON A PHRASE NOBODY REGISTERED. A pointer reworded past this vocabulary is not a
    # pointer this control has checked, and reading that silence as a pass is the fail-open the
    # whole rung exists against.
    if not said:
        defects.append(
            "the sentence sends a reader to the band table in words this control does not know, "
            "so its direction is unchecked -- add the phrase to `_POINTER_PHRASES` with what it "
            "claims: " + sentence[:160])
        return defects
    if len(said) > 1:
        defects.append("one sentence claims {} directions at once: {}".format(len(said), said))
    if not homes:
        defects.append(
            "the sentence renders in none of the regions this control knows about, so it is "
            "judged nowhere: " + sentence[:120])
    for phrase in said:
        landmark, direction = _POINTER_PHRASES[phrase]
        # A LANDMARK CLAIM IS ABSOLUTE and holds wherever it renders; a `None` landmark is a claim
        # about "here", so it is re-asked once per home. That distinction IS the defect this rung
        # closed: the same "here" sentence was true in one home and false in the other.
        against = [landmark] if landmark else sorted(homes)
        for anchor in against:
            if anchor not in order:
                defects.append("{!r} is measured against #{}, which the door no longer "
                               "declares".format(phrase, anchor))
                continue
            actually = "below" if order[_THE_BAND_TABLE] > order[anchor] else (
                "above" if order[_THE_BAND_TABLE] < order[anchor] else "at")
            if actually != direction:
                defects.append(
                    "{!r} tells a reader at #{} that the band table is {} them, and it is {}: "
                    "the pointer misdirects".format(phrase, anchor, direction, actually))
    return defects


def _every_pointer_this_page_can_publish() -> dict:
    """`{name: (sentence, homes)}` for every band-table pointer the producers can emit.

    BOTH BRANCHES OF BOTH PRODUCERS, off real builds rather than hand-written stability blocks,
    because the homes have to be derived and a home is a property of the BUILD.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    superseded, admitted = _load(NOISE_FLOOR), _admitted_live_floor()
    split = {"level_share_of_advantage": 0.7867}

    # THE POINTING BRANCH -- the straddling floor refuses the share while the table's price-level
    # row still carries a family, which is the only state in which the refusal points rather than
    # recites. Same subject as the rung above it.
    pointed = gva._current_world_contrast(current, superseded, admitted, later_runs=[],
                                          superseded_split=split)
    # THE FALLBACK BRANCH -- one seed row short of the level contrast, nothing else touched, so
    # `_verdict_stability` refuses that leg and the refusal states the numbers instead. It carries
    # a pointer too ("stated here rather than in ..."), and that pointer was equally untied.
    short = dict(admitted, seeds=[
        {k: v for k, v in seed.items() if not (i == 1 and k == gva.LEVEL_CONTRAST)}
        for i, seed in enumerate(admitted["seeds"])])
    fell_back = gva._current_world_contrast(current, superseded, short, later_runs=[],
                                            superseded_split=split)

    # THE SUBJECT IS THE COMPOSED STRING THE BUILD PUBLISHES, not a fresh call to the producer.
    # `_the_level_legs_family`'s fallback interpolates the floor's own edges, so a hand-fed call
    # returns a sentence that is nowhere in the feed -- and deriving homes by substring would then
    # report none and this rung would judge nothing. What a reader meets is the refusal, so the
    # refusal is what is judged; the leg below ties it back to the producer.
    pointers = {}
    for name, built, sentence in (
            ("_redraw_band_clause", pointed, pointed.get("redraw_band") or ""),
            ("_the_level_legs_family, pointing at the table", pointed,
             (pointed.get("composition") or {}).get("why_not_readable") or ""),
            ("_the_level_legs_family, stating the numbers", fell_back,
             (fell_back.get("composition") or {}).get("why_not_readable") or "")):
        pointers[name] = (sentence, _the_regions_a_sentence_reaches(sentence, built))

    # AND THE MIDDLE SUBJECT IS THIS PRODUCER'S, asserted rather than assumed. Without it the two
    # composition subjects are just "some refusal the build emitted", and a refactor that stopped
    # calling `_the_level_legs_family` altogether would leave this rung green over prose it was
    # never written about.
    from_the_producer = gva._the_level_legs_family(
        [-1.0, 1.0], (pointed.get("level_leg") or {}).get("verdict_stability"))
    assert from_the_producer and from_the_producer in pointers[
        "_the_level_legs_family, pointing at the table"][0], (
        "the published refusal does not carry `_the_level_legs_family`'s own sentence, so the "
        "subject below is not this producer's output: " + from_the_producer[:160])
    return pointers


def test_a_sentence_pointing_at_the_band_table_is_true_from_EVERY_region_it_renders_in():
    """A pointer at `#arms-redraw` must be true in every place a reader can meet it.

    THE DEFECT IT SERVES (2026-09-08, found by building this rung). `656a45f54` and `ea6101870`
    collapsed the re-draw family's NUMBERS into one home. The DESCRIPTION of that home then had
    two, in two producers, edited on different days -- the same shape one layer along -- and the
    drawn item asked whether that was worth a control. It was, and not for the reason the item
    gave: the answer was not a latent drift hazard but a live falsehood.

    `_the_level_legs_family` said the family was in "the re-draw band table HIGHER UP THIS
    SECTION". That sentence lands in `composition.why_not_readable`, which has TWO homes:
    `#arms-composition` renders it, and `_current_world_clause` composes it into `headline`, which
    `#arms-headline` renders. `#arms-redraw` sits BELOW the headline (position 1 against 0) and
    ABOVE the composition panel (1 against 7). So one of the two readers was sent the wrong way up
    the page. Every existing control over that sentence asked whether it said "band table"; none
    asked where the table was, and the producer's own docstring asserted the single home it knew
    about. The fix is a LANDMARK -- "under the headline figure" -- which is true from anywhere and
    cannot rot into a lie by the sentence gaining a third home.

    KEYED TO THE PROPERTY, NOT TO TODAY'S DOM. Nothing here pins a position. The door's own reading
    order is read at run time and each sentence's homes are derived by running the composers the
    door reads from, so moving `#arms-redraw` above the headline reds this, moving the composition
    panel above it reds this, and rewording a pointer past the registered vocabulary reds this
    fail-closed rather than passing on silence.

    Fires on: reordering the section so a pointer's direction stops holding; giving a `here`-
    relative pointer a second home on the other side of the table; restoring "higher up this
    section" to `_the_level_legs_family`; rewording a pointer into unregistered words; declaring
    two directions in one sentence; or dropping the `#arms-redraw` anchor while the prose still
    sends readers to it.
    """
    order = _the_doors_reading_order()
    assert _THE_BAND_TABLE in order and "arms-headline" in order, (
        "the door declares neither the band table nor the headline, so this rung has no subject")

    pointers = _every_pointer_this_page_can_publish()
    defects = []
    for name, (sentence, homes) in pointers.items():
        assert sentence, (
            "{} emitted nothing on the branch this rung drives, so its pointer is unwitnessed "
            "and every assertion below skips it".format(name))
        assert homes, (
            "{} renders in no region this control can see, so it is judged nowhere -- either the "
            "door stopped rendering it or `_the_regions_a_sentence_reaches` has gone blind".format(
                name))
        defects.extend("{}: {}".format(name, d) for d in _pointer_defects(sentence, homes, order))
    assert not defects, "the page misdirects its own readers:\n  " + "\n  ".join(defects)

    # THE QUANTIFIER NEEDS A WITNESS. "True in EVERY region" is the whole claim, and on a set of
    # sentences that each render once it is indistinguishable from "true somewhere". At least one
    # pointer must reach two regions, or this rung has quietly become the weaker check it replaced.
    assert any(len(homes) > 1 for _, homes in pointers.values()), (
        "no pointer reaches more than one region any more, so the per-home loop above is never "
        "exercised and this rung cannot tell a landmark claim from a 'here'-relative one")


def test_MUTATION_a_pointer_that_misdirects_is_CAUGHT_and_both_directions_are_reachable():
    """The rung above must be failable by the page being wrong, not only by it being right.

    POISONED IN TWO PLACES, because the claim has two halves and a control that only holds one is
    the fail-open. The SENTENCE is poisoned back to its pre-fix wording against the real door
    order; the ORDER is poisoned by moving `#arms-redraw` below the composition panel against the
    real sentences. Each must red, and the honest pair of each must not -- otherwise the judge
    refuses everything, which is what a guard that refuses its whole partition also does.

    AND THE TWO KINDS OF CLAIM FAIL ON DIFFERENT MOVES, which is why both are poisoned. A LANDMARK
    pointer survives the table being pushed to the foot of the section and breaks when it goes
    above the landmark; a `here`-relative one breaks on exactly the move the landmark survives.
    The first draft of leg B asserted the opposite and reported the judge blind while the judge was
    right -- the sentence said "under the headline figure" and the table was still under it.

    R15, run and reverted:
      * restore "higher up this section" to `_the_level_legs_family` -> the rung above reds on
        `#arms-headline`, naming the direction it claims and the direction that holds.
      * move the `#arms-redraw` div above `#arms-headline` in the door -> the rung above reds on
        both landmark pointers.
      * delete the `#arms-redraw` div -> reds on the pointer having nothing to point at.
    """
    order = _the_doors_reading_order()
    honest = "the re-draw band table under the headline figure"
    poisoned = "the re-draw band table higher up this section"

    # A. THE SENTENCE IS WRONG, THE PAGE IS NOT. Judged in both homes the live producer has.
    both_homes = {"arms-headline", "arms-composition"}
    assert not _pointer_defects(honest, both_homes, order), (
        "the landmark wording is reported as a misdirection, so the judge refuses correct prose "
        "and every red it raises is uninformative")
    caught = _pointer_defects(poisoned, both_homes, order)
    assert any("arms-headline" in d for d in caught), (
        "the retired wording -- which was live and false in the headline until 2026-09-08 -- is "
        "not caught, so the rung above passes on the very defect it was written for: " + str(caught))
    # AND IT IS CAUGHT FOR BEING FALSE, NOT FOR BEING UNKNOWN. A fail-closed red on an unregistered
    # phrase would satisfy the line above while saying nothing about direction.
    assert not any("this control does not know" in d for d in caught), (
        "the poison reds as an unrecognised phrase rather than as a misdirection, so the "
        "direction half of this control is untested")
    # THE OTHER HALF OF THE PARTITION. Rendered ONLY below the table, "higher up" is TRUE -- so the
    # judge is reading the sentence against the region and not banning a word.
    assert not _pointer_defects(poisoned, {"arms-composition"}, order), (
        "'higher up this section' is refused even from a region below the table, so the judge "
        "rejects the phrase rather than judging the claim")

    # B. THE PAGE IS WRONG, THE SENTENCE IS NOT. The move has to break the claim the sentence
    # actually makes: a LANDMARK pointer at the headline survives the table being pushed to the
    # foot of the section -- correctly, it is still under the headline -- and stops holding only
    # when the table goes ABOVE the landmark. Getting this backwards was the first draft of this
    # leg, and it reported the control blind when the control was right.
    hoisted = dict(order, **{_THE_BAND_TABLE: order["arms-headline"] - 1})
    assert _pointer_defects(honest, both_homes, hoisted), (
        "the band table moved above the headline it names as its landmark and the pointer still "
        "reads true, so this control is blind to the page being reordered under it")
    # AND THE `here`-RELATIVE HALF, which IS the one a move within the section breaks. Pushing the
    # table below the composition panel makes that panel's "higher up" false where the landmark
    # pointer is untouched -- so the two kinds of claim are shown to fail on different moves.
    sunk = dict(order, **{_THE_BAND_TABLE: order["arms-composition"] + 1})
    assert not _pointer_defects(honest, both_homes, sunk), (
        "a landmark pointer reds on a move that leaves it true, so the judge is keyed to the "
        "table's position rather than to what the sentence claims")
    assert _pointer_defects(poisoned, {"arms-composition"}, sunk), (
        "the table moved below the panel whose sentence says it is higher up, and nothing said "
        "so -- the 'here'-relative claim is not being re-asked against the order")
    gone = {k: v for k, v in order.items() if k != _THE_BAND_TABLE}
    assert _pointer_defects(honest, both_homes, gone), (
        "the anchor a reader is being sent to is not on the page and nothing said so")

    # C. A REWORDING IS NOT A PASS.
    reworded = "the same three are in the re-draw band table, over that way somewhere"
    assert any("does not know" in d for d in _pointer_defects(reworded, both_homes, order)), (
        "a pointer in unregistered words is waved through, which is the fail-open this vocabulary "
        "exists to close")


def test_every_band_table_pointer_in_the_producer_is_one_this_control_judges():
    """A fourth producer must not be able to arrive untied. The census, not a memory of one.

    THE SHAPE THIS FILE KEEPS PAYING FOR. The re-draw family had four homes and each was found by
    tripping over it: `_leg_clause`'s recital, then `#arms-redraw`, then `_composition_in_this
    _world`'s, then the pointer prose. The rung above judges the pointers it is HANDED; nothing in
    it would notice a fifth sentence in a new producer, and "I grepped once" is not a control.

    SCOPED TO THE MODULE THAT OWNS THIS PAGE'S PROSE, and to string literals rather than the file's
    text, so the docstrings that discuss the pointers -- including the one recording the defect --
    do not have to be written around a regex.

    Fires on: a new producer emitting a band-table pointer without registering its wording; and,
    by construction, on any of the three registered ones being reworded past the vocabulary.
    """
    source = (PROJECT / "tools" / "generate_value_arms_data.py")
    tree = ast.parse(source.read_text(encoding="utf-8"))
    docstrings = {id(node.body[0].value) for node in ast.walk(tree)
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                       ast.Module))
                  and node.body and isinstance(node.body[0], ast.Expr)
                  and isinstance(node.body[0].value, ast.Constant)
                  and isinstance(node.body[0].value.value, str)}
    unjudged = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if id(node) in docstrings or _POINTS_AT_THE_TABLE not in node.value:
            continue
        if not any(phrase in node.value for phrase in _POINTER_PHRASES):
            unjudged.append("line {}: {}".format(node.lineno, node.value[:120]))
    assert not unjudged, (
        "tools/generate_value_arms_data.py sends a reader to the band table in words no rung "
        "checks the direction of, so a fifth home for one fact can arrive with nothing red:\n  "
        + "\n  ".join(unjudged))


def test_the_shares_refusal_reaches_the_headline_and_not_only_the_payload():
    """A refusal computed and never rendered is a fail-silent.

    THE DEFECT IT SERVES. `site/capabilities/index.html` renders the composed `headline` and the
    superseded split's own `level_share_of_advantage` -- so a reader meets 78.7% on the page. A
    refusal that lived only in `current_world.composition` would leave that number on the surface
    with the correction three blocks down, which is the failure `_current_world_clause` was
    written for, one figure along.

    Fires on: computing the refusal and not composing it; or composing it without the
    two-worlds sentence, which is the half that says the movement is not the company's doing.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    clause = gva._current_world_clause(
        gva._current_world_contrast(current, _load(NOISE_FLOOR), _admitted_live_floor(),
                                    superseded_split={"level_share_of_advantage": 0.7867}))
    assert "CHANGES SIGN" in clause, (
        "the share's refusal never reaches the sentence a reader meets")
    assert "may not be read as the company having got better or worse" in clause


def _a_later_run(when: str, world: str, share: float, whole: float = 10_000.0) -> dict:
    """One more A/B artefact over a named world -- the shape the census admits rows from.

    THE WHOLE IS HELD AND THE SHARE MOVES, so the two legs below differ in exactly the quantity
    under test and in nothing else. `level_advantage_gbp` is the share of the whole by definition
    and `selection_gbp` is the rest, which is how the producer emits them.
    """
    return {
        "generated_at": when,
        "producing_commit": {"commit": "deadbeef" + when[-6:].replace(":", "")},
        "world_identity": {"digest": world},
        "level_vs_selection": {
            "available": True,
            "clock": "settled-realised",
            "value_advantage_gbp": whole,
            "level_advantage_gbp": whole * share,
            "selection_gbp": whole * (1.0 - share),
            "level_share_of_advantage": share,
            "share_undefined_reason": None,
        },
    }


def test_a_later_run_in_this_world_that_disagrees_about_the_split_refuses_the_composition(tmp_path):
    """The page may not publish the older answer as the current one when a later run contradicts it.

    THE DEFECT IT SERVES (2026-09-07, director, lane 0). `site/data/value_arms.json` published a
    6.8% level share dated 2026-09-03 as the world as it is now -- the advantage is mostly the
    CHOOSING, which is the flattering reading, because choosing is value MADE and a price level is
    value MOVED. Three later runs over the SAME world sat unread in `docs/observability/`, one of
    them at 93.9%: mostly the level, mostly transfer. Nothing in this module could see them,
    because `CURRENT_WORLD_THREE_ARM_PATH` is a constant and a constant cannot notice a newer file.

    KEYED TO THE PROPERTY, NEVER TO TODAY'S 6.8%. The refusal fires when a later run over the same
    world puts the advantage on the OTHER SIDE of which leg is bigger. Re-run the arms so they
    agree and it lifts by itself; land a newer disagreeing run tomorrow and it fires on a figure
    nobody has seen. Both directions are what a control pinned to 6.8% would get backwards.

    FOUR WITNESSES, AND THE SECOND IS WHAT MAKES IT A CONTROL RATHER THAN A REFUSAL. An agreeing
    later run must NOT refuse -- otherwise the red carries no information; a later run in ANOTHER
    world must not be admitted at all (a figure from another departure level says nothing about
    this one, which is this page's oldest finding); and an EARLIER run must not be admitted either,
    or every superseded artefact in the directory would refuse the page forever.

    Fires on: refusing unconditionally; refusing never; admitting a foreign world; admitting an
    earlier run; dropping the director's words; naming only the runs that flip and hiding the rest;
    or differencing the runs into a trend.
    """
    live = _live_digest()
    current = _world_stamped(_load(THREE_ARM), live)
    published_share = current["level_vs_selection"]["level_share_of_advantage"]
    assert gva._which_leg(published_share) == "level", (
        "this subject no longer publishes a level-dominant share, so the disagreeing witness "
        "below is no longer on the other side and proves nothing")
    superseded, stable = _load(NOISE_FLOOR), _floor_with_level_legs(
        _admitted_live_floor(), [1_000.0, 1_733.378959, 9_085.082015])

    # WITNESS A -- a later run in THIS world on the other side of which-leg-is-bigger. The floor is
    # the sign-STABLE one on purpose: it is the subject on which the other refusal does not fire,
    # so a red here can only be this one.
    flips = _a_later_run("2099-01-01T00:00:00Z", live, 0.10)
    agrees = _a_later_run("2099-01-02T00:00:00Z", live, 0.80)
    # THROUGH THE CENSUS AND NOT AROUND IT. The rows are built by the same scan production uses, so
    # a census that stopped admitting rows would take these legs red with it rather than leaving
    # them green on hand-built input.
    rows = gva._later_runs_in_this_world(current, live, _dir_of(tmp_path, [flips, agrees]))
    refused = gva._current_world_contrast(
        current, superseded, stable, later_runs=rows,
        superseded_split={"level_share_of_advantage": 0.7867})
    comp = refused["composition"]
    assert comp["readable"] is False, (
        "a later run in this world says the advantage is mostly the other leg and the page "
        "published a composition anyway")
    said = comp["why_not_readable"]
    assert gva.CANNOT_TELL_SELECTION_OR_LEVEL.upper() in said, (
        "the refusal does not carry the words the director asked for: " + said[:300])
    # EVERY LATER RUN IS NAMED, NOT ONLY THE ONE THAT FLIPS. A reader handed the flipping run alone
    # has been shown a two-figure disagreement with the third figure withheld.
    assert "10.0%" in said and "80.0%" in said, (
        "a later run in this world is missing from the sentence: " + said[:400])
    assert "2099-01-01T00:00:00Z" in said and "2099-01-02T00:00:00Z" in said, (
        "a figure is published without the run date it was measured on")
    assert "NOT differenced into a trend" in said, (
        "the sentence does not say the runs are not a trend, which is the one reading the "
        "director named as forbidden -- more than one thing changed between them")
    assert comp["later_runs_disagree"]["later_runs_that_disagree"] == [
        r for r in comp["later_runs_in_this_world"]
        if r["artefact"] == "value_cycle_ab_run_0.json"], (
        "the agreeing run was counted as a disagreement, so the gate is 'a later run exists' and "
        "not 'a later run disagrees'")

    # WITNESS B -- THE SOLE WITNESS THAT THE REFUSAL IS A JUDGEMENT. Same everything, except the
    # later run falls on the same side of which-leg-is-bigger as the published one.
    allowed = gva._current_world_contrast(
        current, superseded, stable,
        later_runs=gva._later_runs_in_this_world(current, live, _dir_of(tmp_path, [agrees])),
        superseded_split={"level_share_of_advantage": 0.7867})
    assert allowed["composition"]["readable"] is True, (
        "a later run AGREEING about which leg is bigger still refuses, so this block refuses "
        "regardless of its subject: "
        + str(allowed["composition"].get("why_not_readable"))[:300])
    assert allowed["composition"]["later_runs_disagree"] is None
    assert allowed["composition"]["later_runs_in_this_world"], (
        "the census went silent on the agreeing branch, so a reader cannot tell 'we looked and "
        "nothing disagrees' from 'nobody looked'")

    # WITNESS C -- THE SCOPE, BOTH WAYS. A flipping run in ANOTHER world, and a flipping run that
    # is EARLIER, are each ignored: the first because a figure from another departure level bounds
    # nothing here, the second because it is what the page already supersedes.
    elsewhere = _a_later_run("2099-01-01T00:00:00Z", "0000000000000000", 0.10)
    earlier = _a_later_run("2000-01-01T00:00:00Z", live, 0.10)
    for name, artefact in (("another world", elsewhere), ("an earlier run", earlier)):
        scoped = gva._later_runs_in_this_world(current, live, _dir_of(tmp_path, [artefact]))
        assert scoped == [], "{} was admitted to the census".format(name)

    # WITNESS D -- THE CENSUS REACHES THE REAL DIRECTORY. Every leg above is on injected rows; a
    # scan that could not find the artefacts that caused this finding would leave the production
    # path fail-open with four green legs above it.
    #
    # ASKED FROM A FIXED OLDER VANTAGE, NOT FROM WHATEVER THE PAGE PUBLISHES. The first draft asked
    # for rows later than the PUBLISHED run and asserted it found some -- which is satisfiable only
    # while the defect is present. The remedy for the defect is to publish the newest run, and
    # nothing on disk is later than the newest thing on disk, so this leg reddened on the day the
    # page became correct and would have gone green again the moment it fell behind. That is the
    # control keyed to today's answer instead of to its property, which is the shape this file's
    # own docstrings price. The property is that the scan can READ `OBSERVABILITY_DIR` and admit
    # what is in it; the vantage below is a committed artefact this world's later runs are all
    # after, so rows must come back whichever run the constant names.
    vantage = gva._read(gva.OBSERVABILITY_DIR / _CENSUS_VANTAGE_ARTEFACT)
    assert (vantage.get("world_identity") or {}).get("digest") == live, (
        "the census vantage no longer names the live world, so the rows below would be scoped out "
        "for that reason alone and this leg would pass for the wrong one")
    live_rows = gva._later_runs_in_this_world(vantage, live, gva.OBSERVABILITY_DIR)
    assert live_rows, (
        "the census finds nothing on the real directory, so nothing here is wired to the directory "
        "the defect was found in")
    assert all(r["ran_in_world"] == live and r["generated_at"] > vantage["generated_at"]
               for r in live_rows)
    # AND IT ADMITS THE ARTEFACT THE PAGE ITSELF PUBLISHES -- the one file whose absence from the
    # scan would leave the production path blind in exactly the direction that flatters it. A glob
    # or a reader that could not take the published run would show up here and nowhere else.
    published = _read_current_world_run()
    assert published["generated_at"] > vantage["generated_at"], (
        "the page publishes a run at or before the census vantage, so the leg below is vacuous -- "
        "and a constant that moved BACKWARDS is the flattering resolution this control exists to "
        "refuse")
    assert gva.CURRENT_WORLD_THREE_ARM_PATH.name in {r["artefact"] for r in live_rows}, (
        "the census cannot see the artefact the page publishes, so the production scan is blind to "
        "the run the reader is looking at")


#: The vantage WITNESS D takes the real census from. A COMMITTED artefact over the live world that
#: every later run in that world is after -- deliberately not `CURRENT_WORLD_THREE_ARM_PATH`, whose
#: whole job is to move forward to the newest run and which therefore has nothing after it.
_CENSUS_VANTAGE_ARTEFACT = "value_cycle_ab_s1_three_arm_20260903.json"


def _read_current_world_run() -> dict:
    """The artefact the page actually publishes as the current-world run."""
    return gva._read(gva.CURRENT_WORLD_THREE_ARM_PATH)


def _dir_named(tmp_path, artefacts: dict):
    """A directory holding these artefacts under names the CALLER chose.

    `_dir_of` numbers its files, which is right for every leg that only needs the glob to admit
    them and useless for the one leg where the FILENAME is the subject -- the promoted copy and its
    dated twin have to be named to be told apart.
    """
    room = tmp_path / "named{}".format(len(list(tmp_path.glob("named*"))))
    room.mkdir()
    for name, artefact in artefacts.items():
        (room / name).write_text(json.dumps(artefact), encoding="utf-8")
    return room


def test_the_promoted_copy_and_its_dated_twin_are_one_row_in_the_census_not_two(tmp_path):
    """One RUN on disk under two names may not be published as two later runs disagreeing.

    THE DEFECT (2026-09-09, Lane 0, found by promoting). Promotion here is a FILE COPY -- the
    2026-09-08b run was copied onto `THREE_ARM_PATH` and its dated original stayed on disk, which
    is how this project keeps superseded-with-provenance. The census globs `value_cycle_ab*.json`,
    so it took BOTH copies, and `current_world.composition.later_runs_in_this_world` came back with
    two rows carrying identical figures. `_the_later_runs_disagree`'s sentence counts those rows:
    it would have told a reader "2 later runs over the SAME world exist and are not published
    above" and then printed one run's figures twice. The convention that creates the twin is
    permanent, so this fires on every future promotion, not on this one.

    THE POISON ROUND IS FIRST AND IT IS NOT DECORATION. "One row" is the answer a dedupe that
    collapses EVERYTHING also gives, and a census that returned one row for two genuinely different
    runs would be a fail-closed blindness with the same green as the fix. So two distinct runs are
    asserted to stay two rows before the twin is shown at all.

    THE SURVIVING NAME IS THE DATED ONE, and that is the substance rather than a tidy-up.
    `THREE_ARM_PATH` is a moving pointer -- a reader who follows it next week reads a different run
    beside these figures -- so naming it against a run is a name that expires. The losing name is
    kept in `also_on_disk_as`: dropping it would be this module choosing which copy a reader may
    know about.

    Fires on: counting files instead of runs; collapsing two distinct runs; surviving under the
    moving pointer's name; discarding the other name; or folding two UNSTAMPED files together on a
    shared date, which is the flattering reading of a missing `producing_commit`.
    """
    live = _live_digest()
    vantage = {"generated_at": "2000-01-01T00:00:00Z"}
    promoted = gva.THREE_ARM_PATH.name
    dated = "value_cycle_ab_s1_three_arm_29990101b.json"

    # POISON ROUND -- two genuinely different runs must still be two rows.
    two = gva._later_runs_in_this_world(
        vantage, live,
        _dir_named(tmp_path, {promoted: _a_later_run("2099-01-01T00:00:00Z", live, 0.10),
                              dated: _a_later_run("2099-01-02T00:00:00Z", live, 0.80)}))
    assert len(two) == 2, (
        "the census collapsed two DIFFERENT runs, so the one-row leg below would pass for a "
        "dedupe that has gone blind rather than for one that works")

    # THE SUBJECT -- one run, two filenames, exactly as a promotion leaves the directory.
    run = _a_later_run("2099-01-01T00:00:00Z", live, 0.10)
    rows = gva._later_runs_in_this_world(
        vantage, live, _dir_named(tmp_path, {promoted: run, dated: run}))
    assert len(rows) == 1, (
        "one run on disk under two names is published as {} later runs, and the sentence a reader "
        "meets counts these rows".format(len(rows)))
    assert rows[0]["artefact"] == dated, (
        "the census named the promoted path, which is a pointer that will hold a different run "
        "next week, over the dated copy that still identifies this one")
    assert promoted in rows[0].get("also_on_disk_as", []), (
        "the other copy's name was discarded rather than shown, so the row hides that the run is "
        "on disk twice")

    # UNSTAMPED FILES ARE NOT ONE RUN. Same date, no commit either side: nothing establishes they
    # are the same run, and folding them would hide a second run behind the first.
    unstamped = _a_later_run("2099-01-01T00:00:00Z", live, 0.10)
    unstamped.pop("producing_commit")
    other = _a_later_run("2099-01-01T00:00:00Z", live, 0.80)
    other.pop("producing_commit")
    assert len(gva._later_runs_in_this_world(
        vantage, live,
        _dir_named(tmp_path, {promoted: unstamped, dated: other}))) == 2, (
        "two runs with no producing commit were folded together on a shared date, which reads a "
        "missing stamp as evidence of sameness")


def _dir_of(tmp_path, artefacts: list):
    """A directory holding exactly these artefacts, under names the census's glob admits.

    NUMBERED IN ORDER so a control can name one back, and re-made per call so no leg inherits
    another's files -- a census fixture that accumulated would make the scope legs vacuous.
    """
    room = tmp_path / "obs{}".format(len(list(tmp_path.glob("obs*"))))
    room.mkdir()
    for index, artefact in enumerate(artefacts):
        (room / "value_cycle_ab_run_{}.json".format(index)).write_text(
            json.dumps(artefact), encoding="utf-8")
    return room


def test_an_auc_null_from_a_run_that_names_no_world_withholds_its_direction_and_keeps_its_numbers():
    """THE DEFECT (2026-09-04): the last unstamped bound on this page, and it was the flattering one.

    The 2026-09-04 walk of "no bound on that page is unstamped" reached `contrast_bounds`, the
    error bar, all three `current_world` legs and `_svt_drift_belief`. It missed the two AUC nulls
    because an AUC null is COMBINATORIAL -- a function of `retained` and `left` alone -- so it
    reads as world-invariant and it is. The COMPARISON is not: the observed 0.655 is how much churn
    signal exists at a particular departure level. So the page rendered, in the amber it reserves
    for a figure that clears its null, "the belief carried real information about who stays"
    (two-sided p 0.009) from the one run `world_provenance` lists in
    `runs_that_cannot_name_their_world`, two paragraphs under a headline whose first sentence is
    "no contrast below may have its direction read as resolved".

    THE ASYMMETRY IS THE PROPERTY, and it is what this control is keyed to -- not to today's
    answer. A refusal ("we cannot tell") needs no world and must survive; a direction needs one.
    A guard that withheld both would replace a caveat with a silence, which is the failure
    `_svt_drift_belief` names when it deliberately leaves its arms' `inside_the_null` alone.

    FOUR WITNESSES, and the last two are what stop this being a machine for refusing:
      A -- the real three-arm run on disk: names no world, clears its null. Direction withheld.
      B -- THE SENTENCE. The refusal must reach `_auc_reading`, whose two-branch `if` sent the
           withheld case down the falsy edge and printed the exact claim being withheld.
      C -- the same run stamped with any world at all: the direction must come BACK.
      D -- a run that names no world and does NOT clear its null: "we cannot tell" must still go
           out. This is the branch a guard keyed to the world alone would wrongly silence.
    """
    three_arm = _load(THREE_ARM_NO_WORLD)
    assert ((three_arm.get("world_identity") or {}).get("digest")) is None, (
        "the three-arm run now names a world, so this control has lost its witness -- the refusal "
        "it guards can no longer be reached from the real artefact")

    population = ((three_arm.get("belief_vs_outcome") or {}).get("auc_population") or {})
    observed = (three_arm.get("belief_vs_outcome") or {}).get("discrimination_auc")
    retained, left = population.get("retained"), population.get("left")

    # WITNESS A -- the real artefact. Its figure clears its null, and its world is unknown.
    withheld = gva._auc_null(retained, left, observed)
    assert withheld["available"] is True, str(withheld.get("reason"))[:200]
    assert withheld["inside_the_null"] is None, (
        "a direction was read off a comparison whose departure level is unknown")
    assert withheld["measured_in_world"] is None
    assert "NAMES NO WORLD" in withheld["verdict_withheld_because"]
    # EVERY NUMBER STAYS. Withholding the measurement as well as the verdict would be the page
    # deleting evidence rather than declining to read a direction off it.
    for key in ("null_95_low", "null_95_high", "null_point", "p_two_sided", "basis"):
        assert withheld.get(key) is not None, (
            "the withheld branch dropped `{}`, so a verdict's refusal took the measurement with "
            "it".format(key))

    # WITNESS B -- IT REACHES THE SENTENCE. `_auc_reading` is what the page renders as
    # `auc_reading`; a refusal that stopped at the payload would leave the claim on the surface.
    reading = gva._auc_reading(three_arm.get("belief_vs_outcome") or {},
                               {"null_bound": withheld, "priced_accounts": 0})
    assert "carried real information about who stays" not in reading, (
        "the withheld direction is still printed in the sentence a reader meets -- the tri-state "
        "fell down a two-branch `if`: " + reading[:300])
    assert "NAMES NO WORLD" in reading

    # WITNESS C -- THE NULL RUNG. Stamp it, any world, nothing else edited: the direction returns.
    stamped = gva._auc_null(retained, left, observed, measured_in_world="any-world")
    assert stamped["inside_the_null"] is False, (
        "a stamped run still states no direction, so this guard refuses regardless of its subject "
        "and its red above carries no information")
    assert stamped["measured_in_world"] == "any-world"
    assert stamped["verdict_withheld_because"] is None
    # KEYED TO THE DIRECTION, NOT TO THE HOUSEHOLD WORD (2026-09-10). This asserted "carried real
    # information about who stays" -- and since the stratified reading landed, that sentence turns
    # on a SECOND and independent gate: whether the within-year concordance clears its own null.
    # This artefact's does not, so the household phrasing is withheld here for a reason that has
    # nothing to do with the world stamp, and asserting it would make this control red whenever
    # the OTHER gate fired. What Witness C exists to prove is that stamping a run brings its
    # DIRECTION back, so that is what is asserted.
    stamped_reading = gva._auc_reading(
        three_arm.get("belief_vs_outcome") or {},
        {"null_bound": stamped, "priced_accounts": 0})
    assert "OUTSIDE it and above the null" in stamped_reading, (
        "the direction did not come back when the run was stamped, so the world guard refuses "
        "regardless of its subject: " + stamped_reading[:300])
    assert "NAMES NO WORLD" not in stamped_reading

    # WITNESS D -- A REFUSAL NEEDS NO WORLD. An observed value sitting inside its own interval says
    # "we cannot tell", and that must go out unstamped: withholding it would silence the one
    # reading that cannot mislead upward. `null_point` is inside every two-sided 95% interval by
    # construction, so this subject cannot drift into the clearing branch.
    cannot_tell = gva._auc_null(retained, left, withheld["null_point"])
    assert cannot_tell["inside_the_null"] is True, (
        "the world guard swallowed a refusal as well as a direction, so an unstamped run that "
        "cannot tell now says nothing at all")
    assert cannot_tell["verdict_withheld_because"] is None
    assert "INSIDE that interval" in gva._auc_reading(
        {"discrimination_auc": withheld["null_point"], "auc_population": population},
        {"null_bound": cannot_tell, "priced_accounts": 0})


def test_both_auc_nulls_on_the_page_name_the_same_world_as_the_run_they_came_from():
    """One rule, two call sites, and they publish the same null a few hundred pixels apart.

    `method_skill.churn_auc_null` and `decisions.auc_attribution.null_bound` are the SAME exact
    null over the SAME population, read from the same run. One naming its world while the other did
    not is the one-legal-rule-many-implementations shape this repository's own CLAUDE.md prices --
    and it is the shape that let the selection leg go unbounded while the advantage beside it was
    bounded, in this same file, last stretch.

    KEYED TO AGREEMENT WITH THE RUN, not to today's `None`. When the arms are re-run in a tree that
    stamps `world_identity`, both blocks must pick the stamp up and this control stays green.

    THE SUBJECT IS STAMPED, AND THE FIRST DRAFT OF THIS CONTROL WAS NOT -- it read the real
    artefact, whose digest is `None`, so `block["measured_in_world"] == ran_in` compared `None` to
    `None` and PASSED with one call site's kwarg deleted. A control whose two sides are both the
    absent value proves nothing about the wiring between them; it is this file's own "two correct
    figures whose ratio is not a quantity" one layer up, and it was caught by mutating the call
    site rather than by reading the assertion. The unstamped case is a separate witness below,
    where the claim is that BOTH withhold rather than that both name a world.
    """
    stamped = _world_stamped(_load(THREE_ARM), "one-world")
    ran_in = ((stamped.get("world_identity") or {}).get("digest"))
    assert ran_in, "the stamped subject lost its stamp, so the equality below is vacuous"
    feed = gva.build(stamped, _load(NOISE_FLOOR))

    blocks = {
        "method_skill.churn_auc_null": (feed.get("method_skill") or {}).get("churn_auc_null") or {},
        "decisions.auc_attribution.null_bound": (
            ((feed.get("decisions") or {}).get("auc_attribution") or {}).get("null_bound") or {}),
    }
    for name, block in blocks.items():
        if not block.get("available"):
            continue
        assert "measured_in_world" in block, (
            "`{}` publishes a null with no world key at all, so a reader cannot place it against "
            "`current_world.live_world`".format(name))
        assert block["measured_in_world"] == ran_in, (
            "`{}` names world {} and the run it was read from names {}".format(
                name, block["measured_in_world"], ran_in))
        # AND THE TWO AGREE WITH EACH OTHER, which is the half that catches one call site being
        # wired and the other left behind -- exactly how this defect was born one leg down.
        assert block["inside_the_null"] == blocks[
            "method_skill.churn_auc_null"]["inside_the_null"], (
            "the two renderings of one null disagree on their verdict")

    # THE UNSTAMPED CASE, as its own witness. Here the claim is not that both name a world -- there
    # is none to name -- but that both WITHHOLD. One call site wired and the other not shows up as
    # one block refusing while its twin, over the same population, states a direction.
    # THE SUBJECT IS THE DATED UNSTAMPED RUN, not the canonical path: promotion put a world digest
    # on `THREE_ARM` on 2026-09-09, and "there is none to name" stopped being true of it.
    bare = gva.build(_load(THREE_ARM_NO_WORLD), _load(NOISE_FLOOR_NO_WORLD))
    both = [(bare.get("method_skill") or {}).get("churn_auc_null") or {},
            ((bare.get("decisions") or {}).get("auc_attribution") or {}).get("null_bound") or {}]
    for block in both:
        if not block.get("available"):
            continue
        assert block["measured_in_world"] is None
        assert block["inside_the_null"] is None, (
            "one of the two renderings of the same unstamped null still states a direction while "
            "the other withholds it")


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# THE PUBLISHED CAUSE UNDER THE LARGEST DROP IN THE FUNNEL (2026-09-04)
# ═══════════════════════════════════════════════════════════════════════════════════════════════
#
# THE DEFECT THESE EXIST FOR. `site/data/value_arms.json` published, under 1,223 of 1,953
# renewals -- 62.6% of everything the arm did not price -- that the cause was `tariff_type = None`
# because "the world has no standard-variable product to set it to". The world had had one since
# 2026-08-30 (`simulation/svt_product.py`), `build_renewal_schedule` delegated to it, and the
# artefact the page was generated FROM said `product_not_upliftable_by_tariff_type =
# {"'svt'": 1223}` -- not one `None` among them. The page named a closed plumbing defect as the
# largest single cause of its own blindness, and the measurement that refuted it was four lines
# away in the file it was reading.
#
# The defect was that the cause was a STRING authored when the run was written, and a string about
# the world cannot go stale loudly. So the cause is now DERIVED from the run's own per-product
# counts at publish time, and these are the legs that hold it there.
#
# R15 -- the mutations, each run and reverted:
#   * make `_exclusions` fall back to the artefact's `means` for `product_not_upliftable` (the
#     pre-fix behaviour) -> `test_the_product_gate_cause_follows_the_run_not_the_artefacts_prose`
#     reds, because the fixture's `means` is the false sentence and its breakdown is `svt`.
#   * default an unrecognised product's `is_a_defect` to False instead of None ->
#     `test_a_product_this_page_has_no_reading_for_is_named_and_not_folded_in` reds.
#   * return the confident SVT sentence when the breakdown is absent ->
#     `test_a_run_with_no_breakdown_refuses_to_name_a_cause` reds.
# The leg that stops this becoming a control pinned to today's answer is
# `test_an_unlabelled_breakdown_is_still_published_as_our_own_defect`: feed it the OLD world and
# the page must go back to calling it a defect, with nobody editing a sentence.

_FALSE_MEANS = (
    "A term carrying `None` is a DRAWN account, and the field is unset because the world has no "
    "standard-variable product to set it to.")


def _funnel(by_tariff_type, means=_FALSE_MEANS, count=1223):
    """A funnel whose PROSE and whose COUNTS disagree -- the exact shape that shipped."""
    return {
        "stages": [
            {"stage": "acquisition_term", "count": 252, "share_of_renewals_offered": 0.129,
             "means": "term 0"},
            {"stage": "product_not_upliftable", "count": count,
             "share_of_renewals_offered": 0.6262, "means": means},
            {"stage": "priced", "count": 120, "share_of_renewals_offered": 0.0614,
             "means": "priced"},
        ],
        "product_not_upliftable_by_tariff_type": by_tariff_type,
    }


def _gate_row(funnel):
    rows = [r for r in gva._exclusions(funnel) if r["stage"] == "product_not_upliftable"]
    assert rows, "the product gate row vanished from the published exclusions"
    return rows[0]


def test_the_product_gate_cause_follows_the_run_not_the_artefacts_prose():
    """The published cause is read off the counts, not off the sentence the run was born with.

    THE WHOLE DEFECT IN ONE ASSERTION. This fixture is the state the feed was actually in on
    2026-09-04: a `means` string saying the world has no standard-variable product, sitting in the
    same block as a breakdown saying every refusal was ON that product.
    """
    row = _gate_row(_funnel({"'svt'": 1223}))
    assert "no standard-variable product" not in row["why"], (
        "the page is still republishing the artefact's own prose, so a cause written before a "
        "world change survives it")
    assert "svt" in row["why"], "the published cause does not name the product it is about"
    assert row["by_tariff_type"] == [
        {"tariff_type": "svt", "count": 1223, "share_of_the_refusals": 1.0,
         "is_a_defect": False, "what_it_is": row["by_tariff_type"][0]["what_it_is"]}], (
        "the evidence the cause is derived from is not published beside it, so a reader cannot "
        "check the sentence against the run -- which is the only reason the last false cause was "
        "catchable at all")


def test_an_svt_only_breakdown_is_the_arms_ceiling_and_never_our_defect():
    """Households on a product with no renewal are not a plumbing gap, and the split says so."""
    funnel = _funnel({"'svt'": 1223})
    row = _gate_row(funnel)
    assert row["exclusion_class"] == gva._CLASS_WORLD_PRODUCT_MIX
    assert row["by_design"] is False, (
        "an SVT household is not the arm's deliberate scope -- the arm would price it if it had a "
        "renewal -- and reporting it as by-design hides that the ceiling is the world's")
    sentence = gva._attribution_sentence(gva._exclusions(funnel), 1953)
    assert "NONE of them is reachable by fixing this company's own code" in sentence, (
        "the attribution still offers the reader a repair that does not exist")
    assert "plumbing gap" not in sentence and "product-label gap" not in sentence


def test_an_unlabelled_breakdown_is_still_published_as_our_own_defect():
    """KEYED TO THE PROPERTY. Feed it the old world and the old, correct verdict comes back.

    Without this leg the fix above is a control pinned to today's answer: it would go on saying
    "the arm's ceiling, nothing to repair" the day the labelling defect returned, which is exactly
    backwards and is the shape this repository has shipped before.
    """
    funnel = _funnel({"None": 1223})
    row = _gate_row(funnel)
    assert row["exclusion_class"] == gva._CLASS_COMPANY_DEFECT
    assert "OUR defect" in row["why"] or "our defect" in row["why"].lower()
    sentence = gva._attribution_sentence(gva._exclusions(funnel), 1953)
    assert "1,223 of them are reachable by fixing this company's own code" in sentence


def test_a_mixed_breakdown_reports_the_two_halves_apart():
    """Two causes under one count is R15's mixed-subject shape; the OR of them is not a reading."""
    row = _gate_row(_funnel({"'svt'": 1000, "None": 223}, count=1223))
    assert row["exclusion_class"] == gva._CLASS_MIXED
    assert "1,000" in row["why"] and "223" in row["why"], (
        "a mixed breakdown published one number, so the reader cannot tell what is reachable")


def test_a_run_with_no_breakdown_refuses_to_name_a_cause():
    """FAIL CLOSED. Every run before 2026-08-30 is this case, and none of them may read as clean."""
    row = _gate_row(_funnel(None))
    assert row["exclusion_class"] == gva._CLASS_NOT_ESTABLISHED
    assert "NOT established" in row["why"] or "not established" in row["why"], (
        "an artefact that recorded no breakdown is being given a confident cause anyway")
    assert row["breakdown_available"] is False


def test_a_product_this_page_has_no_reading_for_is_named_and_not_folded_in():
    """An unexplained label at the largest drop in the funnel is the finding, not a footnote."""
    funnel = _funnel({"'green_tracker'": 1223})
    row = _gate_row(funnel)
    assert row["exclusion_class"] == gva._CLASS_NOT_ESTABLISHED
    assert "green_tracker" in row["why"], "the unrecognised product is not even named"
    assert row["by_tariff_type"][0]["is_a_defect"] is None, (
        "an unknown product defaulted to `not a defect`, which is the flattering branch and the "
        "reason `is_a_defect` is three-valued")


def test_the_remedy_under_the_product_gate_asks_for_work_that_is_not_already_done():
    """`what_is_owed` is a claim and rots like one. It asked for a shipped product for five days."""
    from tools.product_gate_refusal import refusal_breakdown
    owed = gva._what_is_owed_at_the_product_gate(refusal_breakdown({"'svt'": 1223}))
    assert "the world has no standard-variable product" not in owed
    assert "NOTHING, and that is the finding" in owed, (
        "the page still describes the arm's ceiling as a shortfall someone can close")
    # ...and the other side, so this is not pinned either.
    owed_old = gva._what_is_owed_at_the_product_gate(refusal_breakdown({"None": 1223}))
    assert "ours to close" in owed_old


def test_a_gate_refusing_only_real_products_says_ceiling_and_not_gate():
    """The branch the live run will reach the moment the last unlabelled record is gone.

    THE DEFECT THIS EXISTS FOR. Before it, a run whose product gate refused only products the
    world had really settled fell through to the `unresolved` sentence -- "the product gate
    refused renewals under more than one label" -- which was false about the count and silent
    about the only thing that mattered: that these households have no renewal for any arm to
    price, so the arm's reach is a ceiling and not a backlog. This is the branch that says so,
    and without this leg it is a published sentence that has never run.

    Fires on: routing an all-real-product breakdown back through `unresolved`, and on the
    ceiling sentence being reachable when any refusal IS a missing label (which is the leg above,
    `test_the_structural_claim_needs_both_halves_of_its_evidence`).
    """
    art = _load(THREE_ARM_20260829)
    funnel = art["renewal_funnel"]["value_arm"]
    funnel["product_not_upliftable_by_tariff_type"] = {"'svt'": 600, "'flex'": 62}
    who = gva.build(art, _load(NOISE_FLOOR))[
        "decisions"]["who_the_method_has_priced"]
    assert who["verdict"] == "the_arms_ceiling", who["verdict"]
    assert "NOT A GATE WE CAN OPEN" in who["sentence"]
    assert "not one of the 662 renewals refused at the product gate is a missing label" in (
        who["sentence"].replace("but not", "not"))
    assert "`svt`" in who["sentence"] and "`flex`" in who["sentence"], (
        "the ceiling is claimed without naming the products it rests on")
    assert "NOTHING, and that is the finding" in who["what_is_owed"]

    # THE OTHER SIDE, so this is not pinned: put one unlabelled term back and the ceiling claim
    # must be withdrawn, because then part of the refusal IS ours.
    funnel["product_not_upliftable_by_tariff_type"] = {"'svt'": 600, "None": 62}
    who = gva.build(art, _load(NOISE_FLOOR))[
        "decisions"]["who_the_method_has_priced"]
    assert who["verdict"] != "the_arms_ceiling", (
        "62 terms the world never decided a product for, and the page still tells the reader "
        "there is nothing here to repair")


def _spread_leg(concordance, decisions, low, high, *, p=0.4, accounts=None, null_point=0.5):
    """A producer leg carrying the interval its own sample earns.

    Written as a helper rather than repeated inline because the shape is the CONTRACT between
    `_horizon_leg` and `_horizon_leg_published`, and four hand-copied dicts is four places for it
    to drift. `accounts` defaults to half the decisions, which is roughly this book's real rate
    and is never asserted on -- it exists so the detectability arithmetic has a denominator.
    """
    return {
        "what_it_is": "a leg of the bridge",
        "decisions": decisions,
        "accounts": accounts if accounts is not None else max(1, decisions // 2),
        "concordance": concordance,
        "null_constant_signal_concordance": null_point,
        "comparable_pairs": decisions * (decisions - 1) // 2,
        "pairs_tied_on_outcome": 0,
        "null_spread": {"available": True, "null_95_interval": [low, high], "p_two_sided": p,
                        "observed_inside_the_null_interval": low <= concordance <= high,
                        "draws": 20000, "seed": 20260828},
    }


def test_no_cut_of_this_bridge_is_published_without_the_interval_its_OWN_sample_earns():
    """THE PROPERTY, on the publisher: a concordance without a bound on its own n is WITHHELD.

    THE DEFECT (2026-09-09). This block published four concordances over four populations and no
    interval at all, while `_method_skill` a few lines above published the survivor cut's 0.5338
    with [0.4494, 0.5503], a p and a detectability block. The estimand's 0.4209 on 161 decisions
    went out bare. A reader with both on one page reads the unbounded number against the bounded
    one's interval, which is two correct figures whose relationship is not a quantity -- this
    project's most expensive recurring shape.

    BOTH SIDES ARE DRIVEN, because a rule that withholds everything passes every one-sided test.
    A leg WITH its spread publishes its number, its interval, its p and a reading; a leg WITHOUT
    one publishes no number at all and names what is missing.

    AND THE ESTIMAND TAKES THE WHOLE BLOCK WITH IT. It is this block's headline, so a run that
    ranked its priced decisions and permuted none of them has no publishable estimand and the
    block reports the absence -- the same fail-closed rule `_method_skill` applies to the survivor
    cut, arriving on the cut whose direction is the unflattering one.

    Fires on: publishing `concordance` from a leg with no spread; on defaulting a missing interval
    to the headline's; on the estimand's absence being tolerated while its legs render.
    """
    full = {
        "available": True, "reconciles": True, "decisions_priced": 214, "decisions_scored": 161,
        "reconciliation": "161 scored + 53 excluded = 214 against 214 priced",
        "legs": {
            "the_published_population_ratio_outcome": _spread_leg(
                0.5338, 168, 0.4494, 0.5503, p=0.192),
            "settled_only_ratio_outcome": _spread_leg(0.4993, 124, 0.4415, 0.5585),
            "settled_only_pounds_outcome": _spread_leg(0.5130, 124, 0.4415, 0.5585),
            "every_priced_decision_pounds_outcome": _spread_leg(
                0.4209, 161, 0.4480, 0.5520, p=0.014),
        },
    }
    published = gva._skill_fixed_horizon({"fixed_horizon": full})

    assert published["available"] is True
    for name, leg in published["legs"].items():
        assert leg["available"] is True, name
        assert leg["concordance"] is not None, name
        assert leg["null_95_low"] is not None and leg["null_95_high"] is not None, name
        assert leg["reading"]["sentence"], name
    # THE INTERVALS ARE THE LEGS' OWN and not one number four times -- the shape a broadcast
    # bound would take, and the cheap wrong fix for the defect above.
    assert (published["legs"]["the_published_population_ratio_outcome"]["null_95_low"]
            != published["legs"]["every_priced_decision_pounds_outcome"]["null_95_low"])
    # ...and the headline of the block is the ESTIMAND's, bound and all.
    assert published["concordance"] == pytest.approx(0.4209)
    assert published["null_95_low"] == pytest.approx(0.4480)
    assert published["p_two_sided"] == pytest.approx(0.014)
    assert published["reading_of_the_estimand"]["reading"] == "worse_than_chance"
    assert published["what_it_could_have_detected"]["available"] is True
    assert published["what_it_could_have_detected"]["decisions_scored"] == 161, (
        "the detectability block was computed on a population other than this cut's")

    # ONE LEG LOSES ITS SPREAD: that leg alone is withheld and the others are untouched.
    one_short = copy.deepcopy(full)
    one_short["legs"]["settled_only_pounds_outcome"].pop("null_spread")
    partial = gva._skill_fixed_horizon({"fixed_horizon": one_short})
    bare = partial["legs"]["settled_only_pounds_outcome"]
    assert bare["available"] is False and bare["withheld"] is True
    assert bare["concordance"] is None, "a leg with no interval published its number anyway"
    assert bare["concordance_withheld"] == pytest.approx(0.5130)
    assert "124 decisions" in bare["reason"]
    assert partial["legs"]["every_priced_decision_pounds_outcome"]["concordance"] is not None, (
        "one leg's absence withheld a leg that had its own bound")

    # THE ESTIMAND LOSES ITS SPREAD: the whole block is withheld, headline and legs.
    no_estimand = copy.deepcopy(full)
    no_estimand["legs"]["every_priced_decision_pounds_outcome"]["null_spread"] = {
        "available": False, "reason": "fewer than three ranked decisions"}
    withheld = gva._skill_fixed_horizon({"fixed_horizon": no_estimand})
    assert withheld["available"] is False and withheld["withheld"] is True
    assert "concordance" not in withheld, "a withheld estimand published its headline anyway"
    assert withheld["concordance_withheld"] == pytest.approx(0.4209)
    assert "no bound of its own" in withheld["reason"]
    assert "fewer than three ranked decisions" in withheld["reason"], (
        "the refusal did not carry the run's own reason for it")


def test_the_three_readings_a_reader_would_conflate_are_told_APART_by_the_publisher():
    """CARRIES NO INFORMATION, WORSE THAN CHANCE, AND WE CANNOT TELL ARE THREE ANSWERS.

    A reader arriving at 0.4209 has three live possibilities and they need three different things.
    *Inside its own interval* means a larger book. *Below it* means the arm's ranking is real and
    inverted -- the director's own case, and the finding this instrument exists to be able to
    report. *No interval at all* means running something, costs nothing to establish, and says
    nothing whatever about the method.

    ONE CONTROL OVER THE WHOLE PARTITION rather than a leg per branch, because a publisher that
    returned "we cannot tell" for everything would pass every single-branch test. All four
    readings are driven from the same producer shape with only the numbers moved, so a verdict
    pinned to today's answer cannot survive here.

    Fires on: `reading` hard-coded; on the below-interval case rendering as "we cannot tell",
    which is the flattering error and therefore the one nobody checks.
    """
    def _estimand(concordance, low, high):
        return gva._skill_fixed_horizon({"fixed_horizon": {
            "available": True, "reconciles": True, "decisions_scored": 161,
            "legs": {"every_priced_decision_pounds_outcome": _spread_leg(
                concordance, 161, low, high)}}})["reading_of_the_estimand"]

    flat = _estimand(0.5100, 0.4480, 0.5520)
    assert flat["reading"] == "not_distinguishable_from_no_information"
    assert flat["distinguishable_from_no_information"] is False
    assert gva.CANNOT_TELL in flat["sentence"]

    worse = _estimand(0.4209, 0.4480, 0.5520)
    assert worse["reading"] == "worse_than_chance"
    assert worse["distinguishable_from_no_information"] is True
    assert gva.CANNOT_TELL not in worse["sentence"]
    assert "INVERTED" in worse["sentence"]

    better = _estimand(0.6100, 0.4480, 0.5520)
    assert better["reading"] == "better_than_chance"
    assert "INVERTED" not in better["sentence"]

    # ...AND THE FOURTH: no interval at all. It arrives through the withheld branch, so the
    # question a reader asks -- "is this flat or is there no instrument?" -- is answered by the
    # refusal rather than by a sentence that reads like a flat result.
    undecidable = gva._skill_fixed_horizon({"fixed_horizon": {
        "available": True, "reconciles": True, "decisions_scored": 161,
        "legs": {"every_priced_decision_pounds_outcome": dict(
            _spread_leg(0.4209, 161, 0.448, 0.552),
            null_spread={"available": False, "reason": "the spread is absent"})}}})
    assert undecidable["available"] is False
    assert "reading_of_the_estimand" not in undecidable
    assert "no bound of its own" in undecidable["reason"]

    # THE THREE SENTENCES ARE THREE SENTENCES. A page that rendered any two of them identically
    # would tell a reader the wrong thing a third of the time.
    assert len({flat["sentence"], worse["sentence"], better["sentence"]}) == 3


def test_the_fixed_horizon_estimand_is_withheld_on_a_run_that_did_not_measure_it():
    """FAIL CLOSED, and it is the leg that keeps this page from inventing a population.

    THE TEMPTATION THIS REFUSES. `decision_shape.priced` and `method_skill.decisions_scored` are
    on every artefact ever produced, so a "survivorship-free" headline could be assembled here by
    treating the difference as zeros. That would publish a coverage gap and a censored horizon as
    outcomes the world produced -- the exact substitution the estimand exists to refuse -- on
    every page including the ones from runs that never measured it.

    Fires on: defaulting an absent block to available; on synthesising the estimand from counts
    that predate it; on inlining this docstring's reading.
    """
    absent = gva._skill_fixed_horizon({})
    assert absent["available"] is False
    assert "predates the fixed-horizon estimand" in absent["reason"]
    assert "departure" not in absent["reason"], (
        "the page stated the estimand's verdict for a run that never computed it")

    # A POPULATION THAT DOES NOT ADD UP IS WITHHELD, headline and all. The whole claim of this
    # estimand is about its denominator, so a broken denominator is not a caveat on the figure.
    broken = gva._skill_fixed_horizon({"fixed_horizon": {
        "available": True, "reconciles": False,
        "reconciliation": "4 scored + 1 excluded = 5 against 9 priced",
        "legs": {"every_priced_decision_pounds_outcome": {"concordance": 0.9}}}})
    assert broken["available"] is False
    assert "does not add up" in broken["reason"]
    assert "9 priced" in broken["reason"], "the run's own arithmetic is the reader's evidence"
    assert "concordance" not in broken, "a withheld estimand published its headline anyway"

    # AND A REAL ONE PASSES THROUGH UNCHANGED -- counts, legs, bridge and verdict. Asserted after
    # the two refusals so a pass here is evidence of a passthrough rather than of a constant.
    #
    # EVERY LEG CARRIES A `null_spread` FROM 2026-09-09, and this fixture gained them the day the
    # contract did. A leg with a concordance and no interval on its own n is now WITHHELD rather
    # than published -- see `test_no_cut_of_this_bridge_is_published_without_...` below, which
    # drives that branch on purpose. Without the spreads here this fixture would exercise the
    # refusal and prove nothing about the passthrough.
    measured = gva._skill_fixed_horizon({"fixed_horizon": {
        "available": True, "reconciles": True,
        "horizon_days": 365, "observation_end": "2025-12-31",
        "decisions_priced": 214, "decisions_scored": 200,
        "decisions_scored_at_zero_because_the_term_settled_nothing": 40,
        "decisions_excluded": 14,
        "excluded_by_reason": {"no_published_counterfactual_rate_for_the_term": 6},
        "zero_outcomes_the_world_recorded_as_a_departure": 40,
        "reconciliation": "200 scored + 14 excluded = 214 against 214 priced",
        "legs": {"settled_only_ratio_outcome": _spread_leg(0.5334, 124, 0.44, 0.56),
                 "settled_only_pounds_outcome": _spread_leg(0.5100, 124, 0.44, 0.56),
                 "every_priced_decision_pounds_outcome": _spread_leg(
                     0.4700, 161, 0.45, 0.55, p=0.021)},
        "reading": "Admitting the departures LOWERS the figure",
    }})
    assert measured["available"] is True
    assert measured["decisions_priced"] == 214
    assert measured["decisions_scored_at_zero_because_the_term_settled_nothing"] == 40
    assert measured["concordance"] == pytest.approx(0.47)
    assert measured["legs"]["settled_only_ratio_outcome"]["concordance"] == pytest.approx(0.5334)
    assert measured["excluded_by_reason"]["no_published_counterfactual_rate_for_the_term"] == 6
    assert "LOWERS the figure" in measured["reading"]

    # ...and a run that could rank NOTHING says so, rather than publishing a null or a bare zero.
    # "The method has no skill" and "there was nothing to measure" must never read the same.
    unrankable = gva._skill_fixed_horizon({"fixed_horizon": {
        "available": False, "reconciles": True, "decisions_scored": 40,
        "legs": {"every_priced_decision_pounds_outcome": {"concordance": None}}}})
    assert unrankable["available"] is False
    assert unrankable["concordance"] is None
    assert "nothing could be ranked" in unrankable["reason"]
    assert unrankable["decisions_scored"] == 40


def test_the_page_carries_BOTH_populations_and_names_each_one():
    """THE WIRING, and the item's own acceptance test: a rung reported alone is a rung chosen.

    `_skill_fixed_horizon` being right proves nothing about whether `_method_skill` reaches it,
    and the whole point of this change is that the survivor-only figure and the whole-population
    figure appear TOGETHER. A page carrying only the concordance is the state this replaced; a
    page carrying only the fixed horizon would be the same defect facing the other way.

    Fires on: the estimand being computed and not published; on either cut displacing the other.
    """
    skill = gva._method_skill(_load(THREE_ARM))
    assert "concordance" in skill
    assert "survivorship" in skill
    assert "fixed_horizon" in skill
    horizon = skill["fixed_horizon"]
    # The artefact on disk may or may not predate the estimand -- either way the block is PRESENT
    # and states which population it speaks for. That is the property; the value is the run's.
    assert isinstance(horizon, dict) and "available" in horizon
    assert horizon.get("reason") or horizon.get("what_this_is"), (
        "the block neither published a population nor said why it could not")


# ── which of the two panels is the LATER run, and what the headline may say about it ──────────
#
# WHAT THIS PARTITION IS FOR (2026-09-09, Lane 0). `_current_world_contrast` had four guards and
# every one of them asked about the WORLD -- does this run name the live digest, is its floor the
# live digest, is the floor the undecomposed leg. None could ask whether the run offered as "the
# world as it is now" is actually the more recent of the two on the page, because for as long as
# the block existed it always was: the panel below was the 2026-08-31 canonical run and anything
# in the live world postdated it by construction. Promoting the 21:01Z re-take onto
# `value_cycle_ab_s1_three_arm.json` ended that, and the composed headline read "IN THE WORLD AS
# IT IS NOW, the same comparison gives £17,739, measured 2026-09-08T00:19:54Z ... It is a LARGER
# advantage than the £17,453 below" -- with the figure below measured TWENTY-ONE HOURS LATER.
# Every world guard passed, and `_later_runs_in_this_world` named the later run in its own census
# in the same feed while the headline went on claiming currency. A footnote is not a withdrawal.
#
# ONE CONTROL OVER THE WHOLE PARTITION, and not a leg per branch. `is_the_later_run` is a boolean
# on a rarely-taken branch, and a field that were always False would satisfy every assertion about
# the refusal while making the page permanently silent about its own current-world run. So both
# sides are driven here, from artefacts on disk, in one test.


def test_which_panel_is_the_LATER_run_decides_whether_the_headline_may_claim_currency():
    """Both sides of `is_the_later_run`, from three real runs, and the clause that follows each.

    THE SUBJECTS ARE ON DISK AND THEY DIFFER ONLY IN THEIR STAMP. `current` is the 00:19Z
    live-world re-take in both legs. What changes is which run it is published beside: the
    2026-08-31 run (earlier, so the current-world block IS the later one) and the 21:01Z re-take
    (later, so it is NOT). Nothing else about the two legs differs, which is what makes the field
    attributable to the ordering rather than to anything else about the artefacts.

    BOTH SUBJECTS ARE PINNED BY THEIR DATED NAMES, and `THREE_ARM` -- the canonical path -- is
    deliberately not used for either. That path is the PROMOTION TARGET: bytes are copied onto it,
    so which run it holds is a property of the last release and not of this control. Naming it for
    the `earlier` leg is how this control would silently invert, because on 2026-09-09 it holds
    the 21:01Z re-take and would have made both legs the same comparison.

    AND IT ASSERTS THE POSITIVE LEG RESOLVES, which is what keeps the negative one from being
    vacuous. If the live world ever moves off these artefacts' digest, the world guard refuses
    first and `available` goes False -- so the negative leg would pass for the wrong reason and
    nothing would say so. The positive leg fails loudly instead.

    Fires on: hard-coding `is_the_later_run`; comparing the stamps the wrong way round; letting
    `_current_world_clause` compose "IN THE WORLD AS IT IS NOW" over the older of the two runs;
    withdrawing the block's figures instead of only its currency claim.
    """
    obs = PROJECT / "docs" / "observability"
    current = _load(obs / "value_cycle_ab_s1_three_arm_20260908.json")
    earlier = _load(obs / "value_cycle_ab_s1_three_arm_20260831.json")   # 2026-08-31T03:47:57Z
    later = _load(obs / "value_cycle_ab_s1_three_arm_20260908b.json")    # 2026-09-08T21:01:30Z
    assert earlier["generated_at"] < current["generated_at"] < later["generated_at"], (
        "the three subjects no longer straddle the current-world run's stamp, so this control "
        "cannot drive both sides of the partition and is measuring nothing")

    floor = _load(gva.CURRENT_WORLD_NOISE_FLOOR_PATH)
    against_earlier = gva._current_world_contrast(current, {}, floor, superseded_run=earlier)
    against_later = gva._current_world_contrast(current, {}, floor, superseded_run=later)

    # THE POSITIVE LEG. Published, the later of the two, and the headline says so.
    assert against_earlier["available"], (
        "the 00:19Z re-take no longer names the live world, so every leg below would pass by "
        "refusing and this control would be measuring the world guard instead: {}".format(
            against_earlier.get("why_not")))
    assert against_earlier["is_the_later_run"] is True
    assert against_earlier["why_the_headline_omits_it"] is None
    spoken = gva._current_world_clause(against_earlier)
    assert "IN THE WORLD AS IT IS NOW" in spoken

    # THE NEGATIVE LEG. Still published, still bounded, still composed -- and silent in the
    # headline. Withdrawing the block instead was tried and reverted: `composition` lives in this
    # payload, so an unavailable block takes the mission's own question off the page with it.
    assert against_later["available"] is True, (
        "the block was withdrawn rather than quietened, which takes `composition` -- value made "
        "or value moved -- off the page along with the currency claim that was the actual defect")
    assert against_later["is_the_later_run"] is False
    assert "NOT THE LATER OF THE TWO" in (against_later["why_the_headline_omits_it"] or "")
    assert later["generated_at"] in against_later["why_the_headline_omits_it"], (
        "the refusal does not name the stamp it lost to, so a reader cannot check it")
    assert gva._current_world_clause(against_later) == "", (
        "the headline still composes a currency claim over the older of the two runs")

    # ...and the two legs are the SAME MEASUREMENTS either way. The figures were honestly taken
    # and the ordering does not touch them -- only what may be said about them.
    for key in ("value_advantage_gbp", "selection_gbp", "level_advantage_gbp", "generated_at"):
        assert against_earlier[key] == against_later[key], (
            "the ordering changed {}, so it is doing more than withdrawing a claim".format(key))


def test_the_sources_a_reader_would_check_are_the_files_the_page_actually_opens():
    """`sources[]` is derived from the constants `generate` reads, never typed beside them.

    THE DEFECT (2026-09-09). Four literals stood here and only two were true. It cited
    `value_cycle_ab_s1_three_arm_20260903.json`, which `generate` never opens, and it named
    NEITHER current-world path -- the two artefacts the whole current-world block is built from.
    A page citing an artefact it does not read and omitting two it does, in the one field a
    reader would use to check it.

    KEYED TO THE PROPERTY. This asserts the citation matches what `generate` opens, not that it
    equals today's five names, so it stays true through every constant move and every
    promote-by-copy and goes red only when the two genuinely diverge.

    Fires on: re-typing any entry as a literal; dropping a path `generate` reads; adding one it
    does not.
    """
    cited = gva.build({}, {})["sources"]
    opened = [gva.THREE_ARM_PATH, gva.NOISE_FLOOR_PATH, gva.CURRENT_WORLD_THREE_ARM_PATH,
              gva.CURRENT_WORLD_NOISE_FLOOR_PATH, gva.DECOMPOSITION_PATH,
              # THE SIXTH, added 2026-09-10 with the second draw of the choosing leg. `generate`
              # opens it every publish, so a reader checking the move against the artefacts named
              # has to be sent to it -- and this list is the assertion, not a copy of the code.
              gva.DEPARTURE_TERM_RERUN_PATH]
    assert cited == [str(p.relative_to(PROJECT)) for p in opened], (
        "the page cites {} and reads {}, so a reader checking the figures against the artefacts "
        "named would open the wrong files".format(cited, [p.name for p in opened]))
    # ...and every cited file is ON DISK. A citation naming a path that does not exist is worse
    # than none: it reads as provenance and cannot be followed.
    for name in cited:
        assert (PROJECT / name).is_file(), (
            "the page cites {}, which is not in the tree -- provenance a reader cannot "
            "follow".format(name))


def _pair_for_staleness(floor_at: str, point_at: str, floor_world: str, point_world: str):
    """The two artefacts `_staleness_caveat` reads, cut down to exactly what it looks at.

    A THREE-FIELD FIXTURE AND NOT A LOADED ARTEFACT, deliberately. This function reads two stamps
    and two digests and nothing else, so a fixture carrying a whole run would let a later reader
    believe some other field was on trial here. It also cannot be re-tuned into agreement: there
    is nothing in it to tune.
    """
    return ({"generated_at": floor_at, "world_identity": {"digest": floor_world}},
            {"generated_at": point_at, "world_identity": {"digest": point_world}})


def test_the_staleness_refusal_reaches_every_branch_of_its_own_partition():
    """REACHABILITY FIRST, over the whole partition, before any leg is asserted about.

    A guard that refused EVERYTHING would pass each of the three legs below written separately,
    and a guard that cleared everything would pass none of them in a way anybody would notice --
    `_staleness_caveat` returning `None` unconditionally makes the two firing legs red with a
    message about wording rather than about the guard. So the partition is asserted as one
    control: the clean branch, the same-world refusal and the different-world refusal are all
    reachable from the same function on the same day.
    """
    clean = gva._staleness_caveat(*_pair_for_staleness(
        "2026-09-09T14:00:00Z", "2026-09-09T06:57:00Z", "39a192ce04c1eda8", "39a192ce04c1eda8"))
    same_world = gva._staleness_caveat(*_pair_for_staleness(
        "2026-09-09T06:57:00Z", "2026-09-09T14:00:00Z", "39a192ce04c1eda8", "39a192ce04c1eda8"))
    other_world = gva._staleness_caveat(*_pair_for_staleness(
        "2026-08-27T00:00:00Z", "2026-08-28T12:37:00Z", "aaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb"))
    assert clean is None and same_world and other_world, (
        "the three branches of the staleness partition are not all reachable -- clean={!r}, "
        "same_world={!r}, other_world={!r}. Every leg below is vacuous until they are".format(
            clean, bool(same_world), bool(other_world)))
    assert same_world != other_world, (
        "the two refusing branches return the identical sentence, so the digests reach the "
        "reader nowhere and the composition below is decoration")


def test_a_stale_bound_in_one_world_does_not_tell_the_reader_the_world_changed():
    """THE DEFECT, and it would have shipped on this turn's own promotion (2026-09-09).

    The clause returned here asserted, on EVERY firing, "and something did, on 2026-08-28: the
    market gained the ability to DEFEND against a company that undercuts it". That is the
    incident the guard was built for, typed into a refusal that fires on any ordering. The
    leg-conditioning re-run of 2026-09-09 is stamped seven hours after the floor it is published
    beside, in the same world, from a tree whose diff against the floor's touches no simulation
    file -- and the page would have told a reader the market gained a capability inside those
    seven hours. A refusal whose reason is false is worse than no refusal: the reason is the part
    a reader acts on.

    KEYED TO THE PROPERTY, which is what the two artefacts establish and not what happened in
    August. Same digest: the departure surface did not move, and the page says so and says what
    is still unknown -- that the floor names no book identity, so it cannot be shown to have been
    drawn over the decisions the figure is made of. That last clause is why this is not a
    softening: the refusal STANDS on it.

    R15 -- the mutations, each run and reverted:
      * restore the hardcoded "on 2026-08-28 ... DEFEND" clause -> this leg reds on the first
        assertion, which is the defect exactly as it stood.
      * return `None` on a shared digest (the cheap "same world, so it's fine" widening) ->
        `test_the_staleness_refusal_reaches_every_branch_of_its_own_partition` reds, and the
        fail-open it would have bought is named in the docstring above.
      * drop the digest from the sentence -> the third assertion reds.
    """
    caveat = gva._staleness_caveat(*_pair_for_staleness(
        "2026-09-09T06:57:00Z", "2026-09-09T14:00:00Z", "39a192ce04c1eda8", "39a192ce04c1eda8"))
    assert "2026-08-28" not in caveat and "DEFEND" not in caveat, (
        "the page tells a reader the market gained a capability between two runs seven hours "
        "apart in one world, because the reason is typed rather than composed: " + caveat)
    assert "OLDER THAN THE FIGURE IT BOUNDS" in caveat, (
        "the ordering refusal itself was softened, which is not what this repair is: " + caveat)
    assert "39a192ce04c1eda8" in caveat, (
        "the page refuses the bound without naming the world both runs agree on, so a reader "
        "cannot tell this refusal from the one where they disagree: " + caveat)
    assert "book" in caveat.lower(), (
        "the refusal drops the reason it still STANDS -- that the floor names no book identity, "
        "so a shared world does not establish a shared book: " + caveat)


def test_a_stale_bound_across_two_worlds_names_both_of_them():
    """The strong branch, and the one the 2026-08-28 pair would have rendered.

    Two different digests is the state the typed sentence was describing, and it is the one state
    where the page may say the world moved between the runs. It names BOTH digests rather than
    asserting a change in the abstract, so a reader can check the claim against
    `world_provenance` on the same page.

    Fires on: collapsing the two branches back into one sentence, or naming one digest.
    """
    caveat = gva._staleness_caveat(*_pair_for_staleness(
        "2026-08-27T00:00:00Z", "2026-08-28T12:37:00Z", "aaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb"))
    assert "DIFFERENT WORLDS" in caveat, caveat
    assert "aaaaaaaaaaaaaaaa" in caveat and "bbbbbbbbbbbbbbbb" in caveat, (
        "the page says the two runs are different worlds without naming them, so the claim "
        "cannot be checked against anything: " + caveat)


def test_an_unnamed_world_on_a_stale_bound_is_not_read_as_agreement():
    """FAIL-SILENT killer. An artefact with no digest must not fall to the reassuring branch.

    "Both runs carry the same world digest" is the softer of the two sentences, and the one an
    absent digest would reach if the test were `floor_world == point_world` -- `None == None`.
    """
    caveat = gva._staleness_caveat(*_pair_for_staleness(
        "2026-08-27T00:00:00Z", "2026-08-28T12:37:00Z", None, None))
    assert "same world digest" not in caveat, (
        "two artefacts that name NO world were reported as agreeing about it: " + caveat)
    assert "no digest at all" in caveat, (
        "the refusal does not say the worlds are unnamed, so unknown provenance reads as "
        "known: " + caveat)


def test_a_spread_from_another_world_bounds_nothing_however_it_is_stamped():
    """THE FAIL-OPEN HALF of the pairing rule, measured before it was fixed (2026-09-09).

    `_seed_spreads` gates every directional claim on this page, and until this control it asked
    two questions of the floor -- is it newer than the run, and does it name A world -- and never
    whether that world is the RUN's. So a floor measured somewhere else, stamped one second after
    the run, published its spread and the page stated directions off it. The age test was the
    only thing standing between a mismatched pair and a stated direction, and one second of stamp
    order is all it asks for.

    THE MIRROR OF THE OTHER HALF, and they are one defect. `_staleness_caveat` refuses a pair
    that is provably the same world for being a few hours out of order, and this admitted a pair
    that is provably NOT. Fixing only the noisy direction is the asymmetry this project keeps
    paying for: the false positive gets a comment and the fail-open gets nothing.

    NOT the live-world claim `_seed_spreads` deliberately declines to make. That asks whether the
    floor's world is TODAY's; this asks whether it is the world of the figure it bounds. The
    superseded panel keeps its own bound, which is what the `same_world` leg below witnesses.

    R15 -- the mutations, each run and reverted:
      * delete the new gate -> the `mismatched` leg reds, which is the defect as it shipped.
      * refuse whenever the run names no world -> the `run_names_no_world` leg reds, and the
        page would lose its bound for a fact about the RUN that this block cannot act on.
      * compare against the LIVE world digest instead of the run's -> SURVIVED on the first pass,
        and it is an EQUIVALENCE rather than a missing test, established rather than assumed:
        every three-arm artefact on disk today is in the live world, so no pair the tree holds
        can tell the two rules apart. Recorded here because the flattering reading is that the
        control caught it. The `third_world` leg below is the one that separates them -- a floor
        and a run agreeing with each other in a world that is NOT the live one, which is a state
        this tree will reach the next time the world moves and the pair is re-run together. With
        that leg the mutation reds.
    """
    floor = _load(NOISE_FLOOR)
    three_arm = _load(THREE_ARM)
    same_world = gva._seed_spreads(floor, three_arm)
    assert same_world.get("available") is True, (
        "the live pair lost its bound, so every leg below measures that instead: {}".format(
            str(same_world.get("reason"))[:300]))

    elsewhere = dict(floor,
                     generated_at="2999-01-01T00:00:00Z",
                     world_identity=dict(floor["world_identity"], digest="ffffffffffffffff"))
    mismatched = gva._seed_spreads(elsewhere, three_arm)
    assert mismatched.get("available") is False, (
        "a spread measured in world ffffffffffffffff was published as the bound on a figure from "
        "world {}, because it was stamped later".format(three_arm["world_identity"]["digest"]))
    assert "ffffffffffffffff" in str(mismatched.get("reason")) and \
        three_arm["world_identity"]["digest"] in str(mismatched.get("reason")), (
        "the refusal does not name the two worlds it is between, so a reader cannot tell it from "
        "the age refusal: {}".format(str(mismatched.get("reason"))[:300]))

    # AND IT DOES NOT FIRE ON A FACT ABOUT THE RUN. A three-arm artefact naming no world is a gap
    # in the RUN, and refusing the bound for it would take the page's directions away for
    # something this block cannot establish either way.
    run_names_no_world = gva._seed_spreads(floor, dict(three_arm, world_identity={}))
    assert run_names_no_world.get("available") is True, (
        "the bound was withdrawn because the RUN names no world, which this block cannot act on: "
        "{}".format(str(run_names_no_world.get("reason"))[:300]))

    # THE PAIR IS WHAT IS ASKED ABOUT, NOT THE LIVE WORLD, and this is the only leg that can tell
    # those two rules apart -- see the equivalence recorded in the docstring. A floor and a run
    # that agree with EACH OTHER in some world neither is today's must keep their bound: that is
    # the superseded panel's whole shape, published on purpose beside the live one.
    third = "cccccccccccccccc"
    both_elsewhere = gva._seed_spreads(
        dict(floor, world_identity=dict(floor["world_identity"], digest=third)),
        dict(three_arm, world_identity=dict(three_arm["world_identity"], digest=third)))
    assert both_elsewhere.get("available") is True, (
        "a floor and a run measured in the SAME world lost their bound because that world is not "
        "today's -- which is the live-world claim this block declines to make: {}".format(
            str(both_elsewhere.get("reason"))[:300]))


# ── what would settle the sign of the leg the thesis turns on ────────────────────────────────
#
# THE DEFECT THESE GUARD (2026-09-09). The page bounded the selection leg, found its nine re-draws
# straddle zero, said so -- and stopped. The only remedy arithmetic it carried, `floor_decomposition`,
# refuses itself twice for good reasons: it was measured where the arm priced 104 of 2,009 renewals
# against this page's 214 of 2,035, and it splits `value_advantage_gbp` and not this leg. So the
# page's central refusal was a dead end, and `current_world.what_would_answer_it` was `None` --
# which reads as "nothing left to answer" beside a leg with no direction.
#
# R15 -- the mutations, each run and reverted:
#   * price the remedy off `remedy_price_table(..., shares=(0.5,))` instead of `(1.0,)`
#     -> `test_the_book_a_sign_would_need_is_a_lower_bound_over_every_split` reds: the number stops
#        being a bound over the family and becomes one guess inside it.
#   * read the funnel off the module's own `THREE_ARM_PATH` instead of the run passed in
#     -> `test_the_price_is_on_the_book_this_page_publishes` reds.
#   * publish only the published draw's row and drop the family centre
#     -> `test_both_figures_a_reader_could_mean_are_priced_and_they_disagree` reds.
#   * return the block unconditionally instead of gating on `sign_determined is False`
#     -> `test_a_leg_that_carries_a_direction_is_priced_no_remedy` reds.
#   * leave `what_would_answer_it` as the two-branch original
#     -> `test_a_panel_that_can_state_no_direction_says_what_would_give_it_one` reds.
# The null rung is `test_the_real_page_prices_the_selection_legs_sign`: on the artefacts actually
# on disk the block must be available with both rows priced, and it stays green under all five.


@pytest.fixture(scope="module")
def real_current_world() -> dict:
    """The page as `generate` actually builds it -- current-world run AND current-world floor.

    THE `real` FIXTURE ABOVE CANNOT SERVE THIS. It passes neither, so `_current_world_contrast`
    gets no floor, every leg refuses its bound, and a control reading the selection leg's remedy
    through it would be reading the no-bound refusal while asserting on the priced branch.
    """
    return gva.build(_load(THREE_ARM), _load(NOISE_FLOOR),
                     current_three_arm=_load(gva.CURRENT_WORLD_THREE_ARM_PATH),
                     current_floor=_load(gva.CURRENT_WORLD_NOISE_FLOOR_PATH))


def _settle(page: dict) -> dict:
    return ((page.get("current_world") or {}).get("selection_leg") or {}).get(
        "what_would_settle_the_sign") or {}


def test_the_real_page_prices_the_selection_legs_sign(real_current_world):
    """THE NULL RUNG. On the artefacts on disk the page must say what would settle the sign."""
    leg = (real_current_world["current_world"] or {})["selection_leg"]
    assert (leg.get("verdict_stability") or {}).get("sign_determined") is False, (
        "this control's subject is a leg whose SIGN IS UNDETERMINED, and this leg now carries one "
        "-- so the remedy branch below is unreachable and the assertion under it would pass "
        "vacuously. Re-point it at whichever leg is signless, or retire it.")
    block = _settle(real_current_world)
    assert block.get("available") is True, (
        "the page states no price for settling the sign of the only leg that could be value "
        "CREATED: {}".format(str(block.get("why_not"))[:300]))
    priced = [row for row in block["rows"] if row.get("times_this_book")]
    assert len(priced) == len(gva._SIGN_REMEDY_FIGURES), (
        "only {} of {} figures a reader could mean was priced, so the page answers one reading of "
        "its own refusal and leaves the other".format(len(priced), len(gva._SIGN_REMEDY_FIGURES)))
    for row in priced:
        assert row["priced_decisions_needed"] > 0 and row["renewals_the_world_must_offer"] > 0, (
            "the {} row carries a multiplier and no counts, so a reader is handed a ratio with no "
            "unit".format(row["which_figure"]))


def test_the_book_a_sign_would_need_is_a_lower_bound_over_every_split(real_current_world):
    """THE MATHEMATICAL CLAIM, RE-ASKED OF THE PRODUCER THE PAGE SHARES WITH THE ARTEFACT.

    The block publishes the corner where the whole spread is the priced households' own draw. Its
    whole licence to be published without the two missing floor legs is that this corner is the
    SMALLEST member of the family: `m = (V - V_rest)/(c^2 - V_rest)` rises with `V_rest`. If that
    is false the number is not a bound, it is a guess wearing a bound's words -- and the page says
    "the real book is LARGER than this, never smaller" underneath it.

    KEYED TO THE PROPERTY AND NOT TO 44.9x. Asserting today's multiplier would go red the day the
    floor is re-measured and stay green if the direction inverted, which is exactly backwards.
    """
    block = _settle(real_current_world)
    variance, book = block["floor_variance_gbp2"], block["book"]
    checked = [r for r in block["rows"] if r.get("times_this_book")]
    # THE LOOP MUST RUN, AND THIS LINE IS NOT DECORATION. Caught in this control's own poison
    # round: pricing at share 0.5 instead of 1.0 drives BOTH rows' headroom negative, every
    # multiplier becomes `None`, and the comparison below iterates over nothing and passes. A
    # mutation that empties a control's subject is indistinguishable from one it survives.
    assert len(checked) == len(gva._SIGN_REMEDY_FIGURES), (
        "{} of {} rows carry a multiplier, so the comparison below would run over a subset of the "
        "family it claims to bound -- and over none of it if the count is zero".format(
            len(checked), len(gva._SIGN_REMEDY_FIGURES)))
    for row in checked:
        ladder = gva.remedy_price_table(
            variance, row["contrast_gbp"], book["priced_decisions"],
            book["priced_share_of_renewals_offered"], shares=(1.0, 0.9, 0.7, 0.5))
        priced_at = [r["times_this_book"] for r in ladder if r["times_this_book"]]
        assert row["times_this_book"] == min(priced_at), (
            "the {} row publishes {:.2f}x as a lower bound and a split with MORE of the spread in "
            "the rest of the book prices at {:.2f}x, which is smaller -- so the published figure "
            "bounds nothing".format(row["which_figure"], row["times_this_book"], min(priced_at)))
        assert block["is_a_lower_bound"] is True


def test_an_ATTAINED_bound_stops_promising_a_bigger_number_and_a_run_that_cannot_happen():
    """THE DEFECT, live on `capabilities/index.html` until 2026-09-10.

    The block prices the `V_rest = 0` corner and printed underneath it "the real book is LARGER
    than this, never smaller", plus the work that would pin it down: "the `only` and `except` floor
    legs re-run on this book at these nine seeds -- nine full three-arm passes each, not yet run."
    The MATHS is right -- the corner is the family's minimum. Both INFERENCES are wrong here. A
    full instrumented pass counted 298 elasticity draws in this world with ZERO outside the
    100-account priced roster, so `V_rest` is identically zero: the corner is where this book
    actually sits, nothing is coming to raise it, and the nine-seed `except` run launched that
    morning refused on its first seed after 39 minutes because the set it re-draws is empty. A
    remedy naming work that cannot be done is worse than none -- it reads as a plan.

    KEYED TO THE PROBE, NOT TO THE WORDING OR TO 44.9x. Feed it a probe that finds households
    outside the roster and the ordinary lower-bound reading must come back, with no edit here.

    THE BOOLEAN DOES NOT FLIP EITHER WAY: `is_a_lower_bound` stays True in both, because `m` is
    still the minimum over the family. A repair that reported an attained bound as "not a bound"
    would say the arithmetic was wrong, and it is not.
    """
    leg = {"verdict_stability": {"sign_determined": False},
           "bound": {"stdev_gbp": 1000.0, "mean_gbp": -400.0, "n": 9}}
    current = {"world_identity": {"digest": "w1"},
               "renewal_funnel": {"value_arm": {
                   "priced": 200, "renewals_the_world_offered": 2000,
                   "priced_share_of_renewals_offered": 0.1,
                   "accounts_the_arm_priced": ["A{}".format(i) for i in range(100)]}}}

    def _probe(outside, **over):
        return dict({"world_digest": "w1", "roster_size": 100, "elasticity_calls": 298,
                     "accounts_that_drew": 67,
                     "accounts_that_drew_outside_the_roster": outside}, **over)

    empty = gva._the_complement_this_bound_rests_on(current, _probe(0))
    peopled = gva._the_complement_this_bound_rests_on(current, _probe(5))
    assert empty["empty"] is True and peopled["empty"] is False, (
        "the probe reader does not separate an empty complement from a peopled one, so every "
        "sentence keyed to it says the same thing whatever was measured")

    # FAIL CLOSED, THREE WAYS. A probe that cannot be shown to describe THIS book must leave the
    # ordinary reading standing -- which asks for a bigger book than needed, the safe direction.
    for name, probe in (("another world", _probe(0, world_digest="w2")),
                        ("another roster", _probe(0, roster_size=67)),
                        ("no count at all", _probe(None))):
        assert gva._the_complement_this_bound_rests_on(current, probe)["empty"] is None, (
            "a probe from {} was read as describing this book -- the page would then call its "
            "bound exact on evidence measured somewhere else".format(name))
    assert gva._the_complement_this_bound_rests_on(current, None)["empty"] is None

    # AND THE BLOCK'S PROSE FOLLOWS IT. Both readings are driven through the module's own file
    # read, so the two differ in the PROBE and in nothing else -- a fixture that changed the world
    # or the book alongside it could not attribute which one moved the sentence.
    import unittest.mock as _mock
    with _mock.patch.object(gva, "_read", lambda p: _probe(0)):
        block = gva._what_would_settle_the_sign(leg, current, 250.0)
    assert block["the_bound_is_attained"] is True, (
        "the page did not read the probe at all, so the branch below is unreachable")
    assert block["is_a_lower_bound"] is True, (
        "an attained bound was reported as not a bound, which says the arithmetic was wrong")
    assert "the real book is LARGER" not in block["why_it_is_a_lower_bound"], (
        "the page promised a bigger number that no measurement on this instrument can produce")
    assert "not yet run" not in block["why_it_is_a_lower_bound"], (
        "the page still directs a reader at floor legs that refuse on this book")
    assert "attained" in block["why_it_is_a_lower_bound"].lower()
    assert "298" in block["why_it_is_a_lower_bound"], (
        "the claim is stated with none of the counts it rests on, so a reader cannot check it")
    assert "cannot be run as a distinct leg" in block["why_no_account_column"], (
        "the account column is still withheld pending a leg that cannot exist here")
    assert "the real one is larger" not in block["sentence"], (
        "the takeaway line kept the inference the block above withdrew -- and the line is the "
        "half a reader carries away: {}".format(block["sentence"]))
    assert "read them as exact" in block["sentence"]

    # THE NULL RUNG: a peopled complement restores every original sentence, with no edit here.
    with _mock.patch.object(gva, "_read", lambda p: _probe(5)):
        ordinary = gva._what_would_settle_the_sign(leg, current, 250.0)
    assert ordinary["the_bound_is_attained"] is False
    assert "the real book is LARGER" in ordinary["why_it_is_a_lower_bound"], (
        "the lower-bound reading was deleted rather than made conditional, so a book whose "
        "complement is peopled would be told its bound is exact")
    assert "the real one is larger" in ordinary["sentence"]
    assert "not yet run" in ordinary["why_it_is_a_lower_bound"]


def test_the_price_is_on_the_book_this_page_publishes():
    """THE RECONCILIATION THE EXISTING DECOMPOSITION FAILS, which is why this block exists at all.

    A remedy priced on another book is not a weaker remedy, it is a price for another question --
    the page already refuses `floor_decomposition` on exactly that ground. So the counts here must
    MOVE when the book under them moves. A block that reads its funnel from a module constant
    rather than from the run it was handed would pass every other control in this section.
    """
    leg = {"verdict_stability": {"sign_determined": False},
           "bound": {"stdev_gbp": 1000.0, "mean_gbp": -400.0, "n": 9}}
    small = gva._what_would_settle_the_sign(
        leg, {"renewal_funnel": {"value_arm": {
            "priced": 200, "renewals_the_world_offered": 2000,
            "priced_share_of_renewals_offered": 0.1}}}, 250.0)
    large = gva._what_would_settle_the_sign(
        leg, {"renewal_funnel": {"value_arm": {
            "priced": 400, "renewals_the_world_offered": 4000,
            "priced_share_of_renewals_offered": 0.1}}}, 250.0)
    assert small["available"] and large["available"]
    assert small["rows"][0]["times_this_book"] == large["rows"][0]["times_this_book"], (
        "the MULTIPLE moved when only the book's size did. It is scale-free by construction -- "
        "n0 cancels -- so a multiplier that moves means the two sides are indexed differently.")
    assert large["rows"][0]["priced_decisions_needed"] == \
        2 * small["rows"][0]["priced_decisions_needed"], (
        "the same multiple over a book twice the size gave the same COUNT, so the count is not "
        "this page's book wearing the multiple -- it is a number from somewhere else")


def test_both_figures_a_reader_could_mean_are_priced_and_they_disagree(real_current_world):
    """ONE CONTROL OVER THE WHOLE PARTITION, because the finding IS the disagreement.

    The published draw and the centre of its own re-draw family are on opposite sides of zero on
    this page, and they are answered by books an order of magnitude apart. A page that priced only
    one would be picking which reading of its own refusal to answer -- this project's most
    expensive recurring shape, arriving on the sentence written to end it.
    """
    block = _settle(real_current_world)
    figures = {row["which_figure"]: row for row in block["rows"]}
    assert set(figures) == {label for label, _, _, _ in gva._SIGN_REMEDY_FIGURES}
    multiples = sorted(row["times_this_book"] for row in figures.values()
                       if row.get("times_this_book"))
    assert len(multiples) > 1 and multiples[0] != multiples[-1], (
        "the two figures priced to the same book, so nothing here tells a reader the choice "
        "between them matters: {}".format(multiples))
    assert block["the_two_figures_disagree"] is True, (
        "the rows price to {} and the block reports no disagreement, so the caveat a reader needs "
        "is missing from the one payload that carries it".format(multiples))
    for row in figures.values():
        assert row["what_this_figure_counts"], (
            "the {} row is a number with no statement of what it counts, which is the division "
            "this page refuses everywhere else".format(row["which_figure"]))


def test_a_leg_that_carries_a_direction_is_priced_no_remedy():
    """THE REFUSAL BRANCH, AND IT MUST BE REACHABLE. A remedy for a question already answered is
    noise at best; a control that never drove this branch would not notice the gate was gone."""
    current = {"renewal_funnel": {"value_arm": {
        "priced": 200, "renewals_the_world_offered": 2000,
        "priced_share_of_renewals_offered": 0.1}}}
    bound = {"stdev_gbp": 1000.0, "mean_gbp": -400.0, "n": 9}
    signless = gva._what_would_settle_the_sign(
        {"verdict_stability": {"sign_determined": False}, "bound": bound}, current, 250.0)
    signed = gva._what_would_settle_the_sign(
        {"verdict_stability": {"sign_determined": True}, "bound": bound}, current, 250.0)
    unmeasured = gva._what_would_settle_the_sign(
        {"verdict_stability": {"checked": False}, "bound": bound}, current, 250.0)
    unbounded = gva._what_would_settle_the_sign(
        {"verdict_stability": {"sign_determined": False}, "bound": {}}, current, 250.0)
    assert signless["available"] is True, "the branch this block exists for is unreachable"
    assert signed["available"] is False and signed["why_not"], (
        "a leg that already carries a direction was handed a price for earning one")
    assert unmeasured["available"] is False, (
        "a leg whose sign was never CHECKED was priced as though it had been measured and found "
        "signless -- 'we did not ask' and 'we asked and could not tell' are different states")
    assert unbounded["available"] is False and "spread" in unbounded["why_not"], (
        "a leg with no measured spread was priced anyway, so the floor under the arithmetic was "
        "an absence read as a number")


def test_a_panel_that_can_state_no_direction_says_what_would_give_it_one(real_current_world):
    """`what_would_answer_it` must distinguish its two causes, and know it still has one.

    THE DEFECT. That key was `None` exactly when all three bounds existed -- so the floor legs
    landing emptied it while the panel still could not state a direction for the leg the thesis
    turns on. Reading `None` as "nothing left to answer" was the page's own dead end.
    """
    bounded = {"bound_available": True, "verdict_stability": {"sign_determined": True}}
    signless = {"bound_available": True, "verdict_stability": {"sign_determined": False}}
    unbounded = {"bound_available": False}
    assert gva._what_would_answer_it(bounded, bounded, bounded) is None, (
        "a panel where every leg carries a direction still asks for work, so the key can never "
        "empty and a reader learns to skip it")
    no_bound = gva._what_would_answer_it(unbounded, bounded, bounded)
    assert no_bound and "noise-floor leg" in no_bound, (
        "the missing-bound cause stopped naming the floor leg that would fix it: {}".format(
            str(no_bound)[:200]))
    no_sign = gva._what_would_answer_it(bounded, signless, bounded)
    assert no_sign and "what_would_settle_the_sign" in no_sign, (
        "a panel with every bound measured and a leg with no sign points at nothing: {}".format(
            str(no_sign)[:200]))
    assert no_sign != no_bound, (
        "the two causes read identically, so a reader cannot tell 'run the floor leg' from "
        "'grow the book' -- different work, one sentence")
    live = (real_current_world["current_world"] or {}).get("what_would_answer_it")
    assert live and "what_would_settle_the_sign" in live, (
        "the real page's panel cannot state a direction for the selection leg and still names "
        "nothing that would give it one: {}".format(str(live)[:300]))


# ── the second draw of the choosing leg ──────────────────────────────────────────────────────
#
# THE DEFECT THESE EXIST FOR. On 2026-09-09 the renewal objective was made to pay for the
# departures it causes and the arms were re-run: the choosing leg went from +£319.10 to -£335.40,
# THROUGH ZERO. Published bare, that reads as the arm's choosing turning worthless. The same
# figure re-drawn across nine seeds in the same world runs -£3,036..+£1,261, so a £655 move is a
# third of one standard deviation and settles nothing. Every rung below is about keeping those two
# facts in the same paragraph, and about the four things that must be established before the two
# runs may be differenced at all.

DEPARTURE_RERUN = (
    PROJECT / "docs" / "observability"
    / "value_cycle_ab_s1_three_arm_departure_20260909.json")


def _rerun_block(rerun=None, floor=None, three_arm=None) -> dict:
    return gva._departure_term_rerun(
        _load(THREE_ARM) if three_arm is None else three_arm,
        _load(NOISE_FLOOR) if floor is None else floor,
        _load(DEPARTURE_RERUN) if rerun is None else rerun)


def test_the_second_draw_is_placed_against_THE_SAME_spread_the_page_publishes():
    """The null rung: the real pair, differenced only after four identities are established."""
    block = _rerun_block()
    assert block["available"] and block["comparable"], (
        "the real pair cannot be compared, so every mutation below is vacuous: {}".format(
            block.get("not_comparable_because")))
    floor_spread = _load(NOISE_FLOOR)["selection_gbp_spread"]
    assert block["spread"]["stdev_gbp"] == floor_spread["stdev"], (
        "the move is placed against a spread this page does not publish -- a move judged small "
        "against a bar the reader never sees is the two-figures-from-two-worlds shape")
    assert block["moved_gbp"] == pytest.approx(
        block["selection_gbp_after"] - block["selection_gbp_before"]), (
        "the stated move is not the difference between the two figures beside it")
    assert block["move_is_inside_one_spread"] is True
    assert block["changes_no_sign"] is True and block["family_straddles_zero"] is True
    assert "ONE DRAW" in block["sentence"], (
        "the sentence a reader meets does not say this is one draw: {}".format(
            block["sentence"][:300]))


def test_a_move_LARGER_than_the_spread_is_not_called_one_draw():
    """R15 reachability: the block must be ABLE to say a move is bigger than the bar.

    A control that only ever prints "one draw inside the bar" would be green on a re-run that
    genuinely moved the answer, which is the only case where this block matters.
    """
    rerun = copy.deepcopy(_load(DEPARTURE_RERUN))
    rerun["level_vs_selection"]["selection_gbp"] = 99_000.0
    block = _rerun_block(rerun=rerun)
    assert block["move_is_inside_one_spread"] is False, (
        "a £98,681 move was called one draw of a £1,811 spread")
    assert "ONE DRAW" not in block["sentence"] and "LARGER" in block["sentence"], (
        "the sentence still reads as a move inside the bar: {}".format(block["sentence"][:300]))


def test_a_seed_family_wholly_on_ONE_side_of_zero_stops_the_no_sign_claim():
    """Keyed to the family, not to today's answer. The day the floor earns a sign, this stops.

    `changes_no_sign` is true because the nine-seed family straddles zero and for no other reason.
    A family that does not straddle zero must not get the same sentence -- that would be a control
    printing "we cannot tell" through the moment the instrument got good enough to tell.
    """
    floor = copy.deepcopy(_load(NOISE_FLOOR))
    spread = floor["selection_gbp_spread"]
    spread["min"], spread["max"] = 200.0, 4_000.0
    block = _rerun_block(floor=floor)
    assert block["family_straddles_zero"] is False and block["changes_no_sign"] is False, (
        "a re-draw family that never crosses zero still had its move called signless")
    assert "does NOT straddle zero" in block["sentence"], (
        "the sentence kept the no-sign reading on a family that has a sign: {}".format(
            block["sentence"][:300]))


def test_a_rerun_from_ANOTHER_WORLD_states_no_move_at_all():
    """Two figures from two worlds are not a quantity, so no difference is published."""
    rerun = copy.deepcopy(_load(DEPARTURE_RERUN))
    rerun["world_identity"]["digest"] = "0000deadbeef0000"
    block = _rerun_block(rerun=rerun)
    assert block["comparable"] is False and block["moved_gbp"] is None, (
        "a run from another world was differenced against this page's figure")
    assert "SAME world" in (block["not_comparable_because"] or ""), (
        "the refusal does not name the world as its reason: {}".format(
            str(block.get("not_comparable_because"))[:300]))
    assert "NO MOVE IS STATED" in block["sentence"]


def test_a_rerun_over_a_DIFFERENT_BOOK_states_no_move_at_all():
    """The other identity that makes the difference a quantity, and it is not the world."""
    rerun = copy.deepcopy(_load(DEPARTURE_RERUN))
    rerun["book_identity"]["control_arm"]["billing_accounts_settled_in_window"] = 3
    block = _rerun_block(rerun=rerun)
    assert block["same_book"] is False and block["comparable"] is False, (
        "a run scored over a different book was differenced against this one")
    assert block["moved_gbp"] is None


def test_the_objective_difference_is_read_from_the_TREES_and_never_from_the_filename():
    """The subject of this block is a claim, and the artefact's NAME is not evidence for it.

    POISON ROUND FIRST, because "returns False" has two causes and only one of them is the
    control working: the baseline tree's copy of the module DOES contain the word `departure`
    (in a docstring), so a substring scan answers True there. What decides it is whether the
    objective can be HANDED the cost.

    THE WITNESS IS A NAMED COMMIT AND NOT `THREE_ARM`'S (repaired 2026-09-11). This rung used to
    read its no-departure tree off whatever run was promoted to `THREE_ARM_PATH`. That is not a
    property of the tree it is asking about -- it is a property of which run is canonical this
    week -- and promoting the 09-10 run, drawn at `9cf9d16ed`, moved the witness onto a tree that
    DOES price departures. The rung went red while `_objective_pays_for_departures` was answering
    every question correctly.

    A FIXED COMMIT IS THE RIGHT KEY HERE, and it is the only place in this file where one is. The
    question "could this tree hand the objective a departure cost" is a fact about an immutable
    object; a pointer that moves makes the poison round evaporate silently, which is exactly what
    happened. The poison precondition below is still asserted, so a witness that stops being
    poisonous fails loudly instead of passing for the wrong reason.
    """
    # `8b846013e` -- the 2026-09-09 three-arm run's own tree, canonical until the 09-10 promotion.
    # Chosen because its copy of the objective module contains the word `departure` and cannot be
    # handed the cost, which is the whole point of the poison round.
    baseline_commit = "8b846013ead420257a76bd65bbe7d552b69a72bd"
    rerun_commit = _load(DEPARTURE_RERUN)["producing_commit"]["commit"]
    import subprocess
    shown = subprocess.run(
        ["git", "show", "{}:{}".format(baseline_commit, gva._OBJECTIVE_MODULE)],
        capture_output=True, text=True, timeout=30, cwd=str(PROJECT))
    if shown.returncode != 0:
        pytest.fail("the baseline run's own tree could not be read, so this control's poison "
                    "round is UNAVAILABLE and an unavailable check is a failed one (R15)")
    assert "departure" in shown.stdout, (
        "the poison round is spent: the baseline tree no longer contains the word this control "
        "exists to prove it does not match on")
    assert gva._objective_pays_for_departures(baseline_commit) is False, (
        "the tree that could NOT price a departure was read as one that could -- the word is "
        "there and the argument is not")
    assert gva._objective_pays_for_departures(rerun_commit) is True
    assert gva._objective_pays_for_departures("not-a-commit") is None, (
        "an unreadable tree reported an answer instead of an absence")


def test_an_unestablished_objective_difference_is_a_second_draw_and_NOT_an_experiment(monkeypatch):
    """"We could not read the two trees" must never render as "the departure term did this"."""
    monkeypatch.setattr(gva, "_objective_pays_for_departures", lambda commit: None)
    block = _rerun_block()
    assert block["objective_difference"]["established"] is False
    assert block["objective_difference"]["unavailable_because"], (
        "the block reports an unestablished difference with no reason beside it")
    assert "departures it causes" not in block["what_this_is"], (
        "the page claims the objective was changed on trees it could not read")
    assert "LATER TREE" in block["sentence"]


def test_a_missing_rerun_artefact_is_an_absence_and_not_a_silence():
    block = _rerun_block(rerun={})
    assert block["available"] is False and block["reason"], (
        "an unreadable re-run left the page saying nothing rather than saying it read nothing")


def test_the_bound_reading_says_what_the_objective_could_not_reach():
    """The operative reading: a price pinned to the cap cannot hear a changed objective."""
    block = _rerun_block()
    ba = block["bound_attribution"]
    assert ba["decided_by_a_bound_after"] == (
        _load(DEPARTURE_RERUN)["bound_attribution"]["decided_by_the_lawful_ceiling"]
        + _load(DEPARTURE_RERUN)["bound_attribution"]["decided_by_the_model_support_bound"]), (
        "the count of bound-decided prices is not the run's own two bounds summed")
    assert str(ba["decided_by_a_bound_after"]) in ba["reading"]
    assert "at most {}".format(ba["priced_after"] - ba["decided_by_a_bound_after"]) in ba[
        "reading"], "the reading does not say how many decisions a changed objective can reach"


def test_a_rerun_whose_ranking_LEAVES_the_null_is_read_differently():
    """R15 reachability on the skill leg: both verdicts must be reachable."""
    rerun = copy.deepcopy(_load(DEPARTURE_RERUN))
    rerun["method_skill"]["null_spread"]["observed_inside_the_null_interval"] = False
    block = _rerun_block(rerun=rerun)
    assert "OUTSIDE" in block["method_skill"]["reading"], (
        "a ranking that cleared the no-information interval still read as 'we cannot tell'")
    assert "cannot tell" in _rerun_block()["method_skill"]["reading"], (
        "the real pair's reading no longer withholds the verdict it must withhold")


# ---------------------------------------------------------------------------
# A SPLIT WHOSE TWO HALVES RE-DREW DIFFERENT QUANTITIES
# ---------------------------------------------------------------------------

def test_a_mixed_key_split_states_the_verdict_and_never_a_share():
    """The empty-half defect, re-entered through a door that did not exist when it was closed.

    THE DEFECT, REPRODUCED BEFORE IT WAS FIXED. From 2026-09-10 a floor leg names the quantity it
    re-drew (`redraw_key`), because the `except` half had to be re-keyed to the churn roll -- the
    rest of the book never takes the elasticity draw. Two legs on two keys do not partition each
    other, so `decompose_floor` withdraws every key running through `v_only + v_except`. That
    leaves `rest_of_book_half_is_degenerate` FALSE (the `except` leg carried real variance) and
    `share_is_decisive` None, and the page fell straight through to the threshold branch and
    published:

        "The spread HAS now been split -- 0% of it is the priced households' own draw ...
         too close to the 0% it would have to clear"

    Two fabricated figures out of `or 0.0`, under a sentence asserting a split that was not made.

    AND THE HALF THAT MUST SURVIVE. `irreducible_sd_gbp` is the `except` leg's own spread and needs
    no sum, so the verdict on whether a bigger book resolves this IS available -- withholding it
    would suppress the one answer the re-keying was done to get. Both verdict branches are
    asserted, so a fix that simply says nothing on a mixed key cannot pass.
    """
    resolvable = dict(_decomposition(0.85, resolvable=True),
                      legs_share_one_call_stream=False,
                      priced_share_of_variance=None, share_is_decisive=None,
                      share_at_which_a_bigger_book_could_resolve_it=None,
                      priced_decisions_needed=None,
                      why_the_partition_keys_are_withdrawn=(
                          "The legs re-drew DIFFERENT quantities (except=churn_roll, "
                          "only=elasticity, undecomposed=elasticity)."))
    hopeless = dict(resolvable, larger_settled_book_would_resolve_it=False,
                    irreducible_sd_gbp=2306.0)

    for name, split in (("resolvable", resolvable), ("hopeless", hopeless)):
        said = gva._what_would_resolve_it(
            split, _load(THREE_ARM), withheld_contrasts=(gva.PAGE_FIGURE_CONTRAST,))
        assert "0%" not in said, (
            "the {} mixed-key split published a fabricated 0% where a withdrawal belongs: {}"
            .format(name, said))
        assert "HAS now been split" not in said, (
            "the page asserted a split that was not made on the {} fixture: {}".format(name, said))
        # THE REASON IS READ OUT OF THE ARTEFACT, never restated here, so the page cannot drift
        # into its own account of why the producer withheld.
        assert "churn_roll" in said and "elasticity" in said, (
            "the page withheld the share and never named the two keys, so a reader cannot tell "
            "this from a shortage of seeds: {}".format(said))

    # AND THE VERDICT SURVIVES, IN BOTH DIRECTIONS -- a fix that withheld everything fails here.
    yes = gva._what_would_resolve_it(
        resolvable, _load(THREE_ARM), withheld_contrasts=(gva.PAGE_FIGURE_CONTRAST,))
    no = gva._what_would_resolve_it(
        hopeless, _load(THREE_ARM), withheld_contrasts=(gva.PAGE_FIGURE_CONTRAST,))
    assert "WOULD bring the bar under the gap" in yes, (
        "the rest-of-book half is under the contrast and the page did not say a bigger book "
        "helps -- that verdict needs only the `except` leg: {}".format(yes))
    assert "would NOT resolve it" in no, (
        "the rest-of-book half exceeds the contrast and the page did not say so: {}".format(no))
    assert "1,153" in yes and "2,306" in no, (
        "the measured rest-of-book spread -- the figure that DOES survive a mixed key -- reached "
        "neither sentence")


def test_a_split_that_predates_the_key_field_takes_the_ORDINARY_path():
    """`legs_share_one_call_stream` is checked with `is False`, not for falsiness.

    Every floor leg written before 2026-09-10 predates the field and reads None. Those are
    single-key by construction -- there was one key -- so they must take the ordinary priced-share
    path. A falsy check would divert every artefact on disk into the withholding branch and silence
    a remedy the page has been correctly stating for weeks.
    """
    legacy = _decomposition(0.85, resolvable=True)
    assert "legs_share_one_call_stream" not in legacy
    said = gva._what_would_resolve_it(
        legacy, _load(THREE_ARM), withheld_contrasts=(gva.PAGE_FIGURE_CONTRAST,))
    assert "larger SETTLED BOOK" in said and "85%" in said, (
        "an artefact predating the key field was diverted into the mixed-key withholding: {}"
        .format(said))
