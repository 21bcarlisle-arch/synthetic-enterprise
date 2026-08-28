"""`site/data/value_arms.json` must be able to say "we could not read it" and "it is worth nothing".

THE DEFECT THIS GUARDS. The feed exists to publish a comparison whose honest answer is currently
NEGATIVE -- the per-customer arm's advantage is the price level, and the choosing is worth
-£174.57. Two failure modes would each destroy that reading while leaving a green, plausible,
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
  * fill the level arm's realised net from the provisioned scalar ->
    `test_the_level_arms_realised_net_is_absent_with_its_reason` reds.
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


def test_the_level_arms_realised_net_is_absent_with_its_reason(real):
    """The artefact's gross-to-net bridge never walked the level arm, so its realised net is not
    recoverable. Filling it from the superseded scalar would mix the two clocks silently -- the
    exact defect the A/B was repaired for on 2026-08-28."""
    level = [a for a in real["realised"]["arms"] if a["key"] == "level"][0]
    assert level["net_gbp"] is None, (
        "the level arm was given a realised net margin the run never computed")
    assert level["absent_reason"], "the absence is published without its reason"

    provisioned_level = [a for a in real["provisioned"]["arms"] if a["key"] == "level"][0]
    assert provisioned_level["net_gbp"] is not None, (
        "the level arm IS available on the provisioned clock -- absent there too would mean the "
        "split has no third arm at all")


def test_the_selection_leg_and_its_error_bar_are_published_together(real):
    sp, eb = real["provisioned"], real["error_bar"]
    assert sp["selection_gbp"] is not None
    assert eb["available"], "the point estimate is published with no measured spread"
    assert eb["stdev_gbp"] > abs(sp["selection_gbp"]), (
        "on this reading the spread is WIDER than the estimate; if that stops being true the "
        "sentence the surface renders about it must be re-read, not silently kept")
    assert eb["distinguishable_from_zero"] is False


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

def test_the_published_supplier_claim_is_true_today_and_checked(real):
    pub = real["realised"]["is_the_published_supplier"]
    assert pub["checked"] is True
    assert pub["same_supplier"] is True, (
        "the published run and the A/B's control arm have diverged -- which is a real finding, "
        "not a test to relax: the surface's claim that they are the same supplier must be "
        "re-read before this assertion is changed")
    assert "IS the baseline" in pub["statement"]


def test_a_divergent_published_run_is_reported_as_a_divergence(real):
    """THE LOAD-BEARING NULL. The day the site publishes a different run, the claim must invert
    itself and name both figures -- not quietly go on asserting an identity that has lapsed."""
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR),
                    {"total_net_gbp": control + 40_000.0})
    pub = out["realised"]["is_the_published_supplier"]

    assert pub["same_supplier"] is False
    assert "is NOT the baseline arm's" in pub["statement"]
    assert "40,000" in pub["statement"], "the divergence is reported without its size"
    assert "IS the baseline" not in pub["statement"]
    assert not out["headline"].startswith("The comparison below is against"), (
        "the headline went on claiming the published supplier is the baseline after they diverged")
    assert gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), _load(RUN_OUTPUT))["headline"].startswith(
        "The comparison below is against"), (
        "the null rung: while the two DO match, the headline must make the claim -- otherwise the "
        "assertion above passes on a headline that never carries it")


def test_an_unreadable_published_run_claims_nothing_either_way(real):
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), None)
    pub = out["realised"]["is_the_published_supplier"]
    assert pub["checked"] is False and pub["same_supplier"] is None
    assert "IS the baseline" not in pub["statement"], (
        "an unread run was treated as agreement -- fail-open on the check itself")


def test_a_penny_of_divergence_is_still_the_same_supplier(real):
    """The null on the OTHER side: both figures are pounds summed from settlement records, so
    sub-penny float noise must not be reported as two different suppliers."""
    control = [a for a in real["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    out = gva.build(_load(THREE_ARM), _load(NOISE_FLOOR), {"total_net_gbp": control + 0.004})
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
