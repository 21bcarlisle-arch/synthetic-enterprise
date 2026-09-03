"""A refusal by a NON-TEST gate must name that gate and retire the previous cycle's reds.

THE DEFECT THIS CLOSES (2026-09-02, 18.7 hours of publishing down, 33 markers queued).
`tools/artefact_rerun_diff.py` sat staged and unfrozen, so the orphan ratchet refused every
publish commit in the tree. The publisher printed the banner verbatim --
`orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS` -- and two lines later logged
`Publish commit REFUSED with no FAILED/ERROR summary ... recording NO blocking test`.

Two things then went wrong, and they are separate defects with separate controls below:

  * NOTHING NAMED THE GATE. The banner was in the very buffer the classifier was parsing.
    "No blocking test" is true and sends the reader nowhere.
  * THE STALE LIST SURVIVED. The outcome was recorded as `publish_cause.GATE_REFUSAL`, whose
    whole contract is "the hook chain judged, so a named red is real evidence about THIS
    cycle". Nothing had been judged. `no_test_was_judged` answered False, the suppression in
    `record_publish_gate_failure` never fired, and `.publish_gate_state.json` went on naming
    five tests in `test_a_staged_document_no_longer_blocks_every_landing.py` as the blockers.
    Those five were GREEN -- 20 passed in 0.09s -- left behind by an earlier cycle at a
    different commit. Every reader was sent to run a suite that was never the problem.

R15, and the direction of each leg is the point:
  * FIRES     -- a known banner with no red names its gate, and the cause it records is one
                 `no_test_was_judged` answers True for.
  * SUPPRESSES-- on that cause a carried-forward blocking list is dropped from the record.
  * FAIL-SAFE -- an unknown banner names NOTHING. A parser that always finds something is the
                 fail-open twin of the fail-silent it replaces.
  * DOES NOT OVER-CORRECT -- a refusal that DID name reds still reports `GATE_REFUSAL` and
                 still keeps its list. Suppressing a real red would tell a reader not to look
                 for it, which is the unsafe direction.
"""
import json

import pytest

import background.process_run_complete as prc
import background.publish_cause as pc


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


#: The refusal as the hook chain actually printed it on 2026-09-02. No pytest summary section
#: anywhere in it, because the ratchet short-circuits the chain before the test gate runs.
ORPHAN_RATCHET_OUTPUT = (
    "[site-lane] 527 passed in 31.02s\n"
    "\norphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS.\n\n"
    "  tools.artefact_rerun_diff\n\n"
    "Nothing imports these, and no committed systemd unit, timer or git hook runs them.\n"
)

#: A real red, for the leg that must NOT change behaviour.
RED_OUTPUT = (
    "........F\n"
    "=========================== short test summary info ============================\n"
    "FAILED tests/background/test_forward_attachment_register.py::test_a_thing\n"
    "1 failed, 343 passed\n"
)


# ── FIRES: the gate gets named ───────────────────────────────────────────────────────────────

def test_the_refusing_gate_is_named_from_the_output_the_classifier_already_read():
    """Defect: the banner sat in the parsed buffer and no reader was ever told which gate."""
    assert prc._parse_refusing_gate(ORPHAN_RATCHET_OUTPUT) == "orphan-ratchet"


def test_the_named_gate_reaches_the_log_a_reader_actually_opens():
    """Defect: `recording NO blocking test` was the whole message -- true, and useless."""
    prc._record_commit_refusal_reds(ORPHAN_RATCHET_OUTPUT, "", git_hash="abc1234")

    logged = (prc.LOG_FILE.read_text() if prc.LOG_FILE.exists() else "")
    assert "orphan-ratchet" in logged, "the refusing gate is still unnamed in the record"
    assert "running the test suite will not clear it" in logged, (
        "the reader is not told the suite is the wrong place to look -- which is what they did")


# ── FAIL-SAFE: an unknown gate is named as unnameable, never guessed ─────────────────────────

def test_an_output_with_no_known_banner_names_no_gate():
    """Defect (fail-open twin): a parser that always answers would misattribute every
    refusal to whichever gate sat first in the table."""
    assert prc._parse_refusing_gate("git: some failure nobody has a banner for") is None
    assert prc._parse_refusing_gate("") is None
    assert prc._parse_refusing_gate(None) is None


def test_an_unnameable_refusal_says_so_and_warns_off_the_stale_list():
    """Defect: an unnameable refusal read as five green tests for hours."""
    prc._record_commit_refusal_reds("git exploded in a way nobody has a banner for", "",
                                    git_hash="abc1234")

    logged = (prc.LOG_FILE.read_text() if prc.LOG_FILE.exists() else "")
    assert "UNNAMEABLE" in logged
    assert "earlier cycle's blocking list" in logged, (
        "nothing warns the reader off the record that is about to mislead them")


def test_the_first_banner_in_the_chains_order_wins():
    """Defect: the chain short-circuits, so a later banner is downstream noise. Naming the
    last match would report a gate that never got to run."""
    both = ORPHAN_RATCHET_OUTPUT + "\nFINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED\n"
    assert prc._parse_refusing_gate(both) == "orphan-ratchet"


# ── THE CAUSE: a non-test gate judged nothing, and the vocabulary must say so ────────────────

def test_a_non_test_gate_refusal_is_a_cause_on_which_no_test_was_judged():
    """Defect: recorded as GATE_REFUSAL, whose contract is that the hook chain DID judge --
    so the suppression that exists for exactly this could never fire."""
    assert pc.no_test_was_judged(pc.NON_TEST_GATE_REFUSAL) is True


def test_a_gate_refusal_that_named_reds_still_counts_as_judged():
    """Defect in the OPPOSITE direction: over-correcting would suppress a real red and tell
    the reader not to go looking for it. The fail-safe direction is toward showing."""
    assert pc.no_test_was_judged(pc.GATE_REFUSAL) is False


def test_the_new_cause_is_writable_at_all():
    """Defect: `record_cause` silently writes NOTHING for a cause outside `CAUSES`, so a name
    added to the module without being added to the set is a no-op that looks like a fix."""
    assert pc.NON_TEST_GATE_REFUSAL in pc.CAUSES


# ── SUPPRESSES: end to end, the five green tests leave the register ──────────────────────────

def _seed_a_stale_blocking_record(git_hash="0ldc0mm1t"):
    """What an EARLIER cycle at a DIFFERENT commit left behind -- the real shape."""
    prc._write_blocking_tests(
        ["FAILED tests/background/test_a_staged_document_no_longer_blocks_every_landing.py"
         "::test_a_fork_is_closed_automatically"],
        git_hash, census=prc.CENSUS_HOOK_CHAIN)


def test_a_stale_blocking_list_does_not_survive_a_non_test_gate_refusal():
    """THE DEFECT, whole: five green tests named as the blockers of an orphan-ratchet wedge."""
    _seed_a_stale_blocking_record()

    prc.record_publish_gate_failure(
        "process_run_complete rc=1 on run_complete_20260902T212239Z.md", rc=1,
        git_hash="new0comm", cause=pc.NON_TEST_GATE_REFUSAL,
        cause_evidence="the orphan-ratchet refused; 0 red test(s)", send_ntfy_fn=lambda *a, **k: "x")

    state = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert state["blocking_tests"] == [], (
        "the register still names an earlier cycle's tests as this refusal's blockers")
    assert state["total_red"] == 0, (
        "a depth claim about reds that were never this cycle's is still a claim")
    assert state["suspects"] == {}, "suspects derived from a stale red are a stale blame trail"


def test_a_real_red_is_still_carried_so_the_fix_cannot_blind_the_alarm():
    """Defect: a suppression keyed to the wrong property would retire REAL reds too, which is
    the failure mode that matters more than the one being fixed."""
    prc._write_blocking_tests(["FAILED tests/x.py::test_y"], "new0comm",
                              census=prc.CENSUS_HOOK_CHAIN)

    prc.record_publish_gate_failure(
        "process_run_complete rc=1", rc=1, git_hash="new0comm", cause=pc.GATE_REFUSAL,
        cause_evidence="the hook chain named 1 red test(s)", send_ntfy_fn=lambda *a, **k: "x")

    state = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert state["blocking_tests"] == ["FAILED tests/x.py::test_y"], (
        "a genuinely red test was suppressed -- the alarm is now blind to the thing it exists for")


# ── THE TWO PARSERS MUST NEVER DISAGREE ABOUT WHAT A RED IS ─────────────────────────────────

def test_the_gate_namer_never_speaks_for_output_that_named_a_red():
    """Defect: two parsers over one buffer eventually disagree, and then the record carries
    both a red test AND a gate name -- two answers to a question that has one. The gate namer
    is only ever consulted when `_parse_failed_node_ids` returned nothing; this pins that the
    red path still finds its red, so the guard condition cannot silently invert."""
    assert prc._parse_failed_node_ids(RED_OUTPUT), (
        "the red path stopped finding reds -- the gate namer would now speak for a real red")
    assert prc._parse_failed_node_ids(ORPHAN_RATCHET_OUTPUT) == [], (
        "the orphan-ratchet output is being read as a red, so the non-test branch is dead code")


def test_a_refusal_that_named_a_red_keeps_naming_it():
    """Defect: the non-test branch swallowing the judged case would lose the real diagnostic."""
    reds = prc._record_commit_refusal_reds(RED_OUTPUT, "", git_hash="abc1234")

    assert reds == ["FAILED tests/background/test_forward_attachment_register.py::test_a_thing"]
    node_ids, gh = prc.last_blocking_tests()
    assert node_ids == reds and gh == "abc1234"
