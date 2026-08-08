"""H15_publish_gate_failure_alert -- mutation tests for the silent-wedge
detector in background/process_run_complete.py.

The worked incident (2026-07-14): the publish gate (fast-test suite) was
OOM-killed (rc=-9 -> "Tests FAILED - not committing") every ~10-min cycle for
~45min with run_complete markers piling up and NO alert. This suite proves the
control CAN FAIL on its own named defect (R15): it FIRES on N consecutive
failures, does NOT fire on a single transient failure or after recovery, is
re-armed by a cooldown (no spam), fails CLOSED on an unreadable gate-state, and
distinguishes an OOM/resource kill from a real test regression in the payload.
"""
import json

import pytest

import background.process_run_complete as prc


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    # Redirect the durable action_needed register to a temp path so a fired
    # alert's best-effort register_item() never touches the real file.
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


class _Sink:
    def __init__(self):
        self.messages = []

    def __call__(self, msg, *a, **k):
        self.messages.append(msg)


# ── the control FIRES on its own named defect ────────────────────────────────

def test_fires_on_n_consecutive_failures(tmp_path):
    sink = _Sink()
    # Two failures: below threshold, silent.
    r1 = prc.record_publish_gate_failure("tests failed", rc=-9, now=0, send_ntfy_fn=sink)
    r2 = prc.record_publish_gate_failure("tests failed", rc=-9, now=10, send_ntfy_fn=sink)
    assert (r1["fired"], r2["fired"]) == (False, False)
    assert sink.messages == []
    # The third consecutive failure trips the alarm -- exactly ONCE.
    r3 = prc.record_publish_gate_failure("tests failed", rc=-9, now=20, send_ntfy_fn=sink)
    assert r3["fired"] is True
    assert len(sink.messages) == 1
    assert "[ACTION NEEDED]" in sink.messages[0]
    assert "WEDGED" in sink.messages[0]


def test_mutation_a_broken_threshold_would_be_caught(tmp_path):
    """If the counter never incremented (the fail-silent mutation), three
    failures would still show count==1 and never fire -- this asserts the
    opposite, so that mutation dies here."""
    sink = _Sink()
    for t in (0, 10, 20):
        res = prc.record_publish_gate_failure("x", rc=1, now=t, send_ntfy_fn=sink)
    assert res["count"] == 3
    assert res["fired"] is True


# ── the control does NOT fire on transient noise ─────────────────────────────

def test_single_transient_failure_does_not_fire(tmp_path):
    sink = _Sink()
    res = prc.record_publish_gate_failure("one blip", rc=1, now=0, send_ntfy_fn=sink)
    assert res["fired"] is False
    assert sink.messages == []


def test_does_not_fire_after_recovery(tmp_path):
    """Two failures, then a clean publish CLEARS the streak; a subsequent
    failure is only #1 again and stays silent."""
    sink = _Sink()
    prc.record_publish_gate_failure("f", rc=1, now=0, send_ntfy_fn=sink)
    prc.record_publish_gate_failure("f", rc=1, now=10, send_ntfy_fn=sink)
    prc.record_publish_gate_success(now=20)          # a run published cleanly
    res = prc.record_publish_gate_failure("f", rc=1, now=30, send_ntfy_fn=sink)
    assert res["count"] == 1
    assert res["fired"] is False
    assert sink.messages == []


def test_failures_outside_the_window_do_not_count(tmp_path):
    """Two failures long in the past fall out of the window, so a fresh
    failure is #1, not #3 -- a slow trickle over days is not a wedge."""
    sink = _Sink()
    w = prc.PUBLISH_GATE_WINDOW_SECONDS
    prc.record_publish_gate_failure("old", rc=1, now=0, send_ntfy_fn=sink)
    prc.record_publish_gate_failure("old", rc=1, now=1, send_ntfy_fn=sink)
    res = prc.record_publish_gate_failure("new", rc=1, now=2 * w, send_ntfy_fn=sink)
    assert res["count"] == 1
    assert res["fired"] is False


# ── re-arm / cooldown: no spam ───────────────────────────────────────────────

def test_cooldown_suppresses_repeat_alerts_then_re_arms(tmp_path):
    sink = _Sink()
    for t in (0, 1, 2):
        prc.record_publish_gate_failure("f", rc=1, now=t, send_ntfy_fn=sink)
    assert len(sink.messages) == 1                    # fired at t=2
    # A further failure inside the cooldown window must NOT re-alert.
    res = prc.record_publish_gate_failure("f", rc=1, now=100, send_ntfy_fn=sink)
    assert res["threshold_met"] is True and res["fired"] is False
    assert len(sink.messages) == 1
    # After the cooldown elapses it re-arms and fires again (still wedged).
    later = 2 + prc.PUBLISH_GATE_COOLDOWN_SECONDS
    res = prc.record_publish_gate_failure("f", rc=1, now=later, send_ntfy_fn=sink)
    assert res["fired"] is True
    assert len(sink.messages) == 2


# ── FAIL-CLOSED on an unavailable gate-state (R15 fail-silent killer) ─────────

def test_unreadable_state_fails_closed_and_fires_immediately(tmp_path):
    prc.PUBLISH_GATE_STATE_FILE.write_text("{ this is not valid json")
    sink = _Sink()
    res = prc.record_publish_gate_failure("f", rc=1, now=0, send_ntfy_fn=sink)
    assert res["threshold_met"] is True
    assert res["fired"] is True
    assert len(sink.messages) == 1
    assert "fail-closed" in sink.messages[0]


def test_state_roundtrips_and_prunes_on_disk(tmp_path):
    prc.record_publish_gate_failure("f", rc=1, now=0)
    prc.record_publish_gate_failure("f", rc=1, now=10)
    on_disk = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert len(on_disk["failures"]) == 2
    assert on_disk["alerted_at"] is None


# ── OOM vs regression distinction in the payload ─────────────────────────────

def test_classify_resource_kill_vs_regression():
    assert prc._classify_gate_failure(-9) == "resource_kill"
    assert prc._classify_gate_failure(-15) == "signal_kill"
    assert prc._classify_gate_failure(1) == "test_regression"
    assert prc._classify_gate_failure(0) == "pass"
    assert prc._classify_gate_failure(None) == "unknown"


def test_payload_names_oom_for_sigkill(tmp_path):
    sink = _Sink()
    for t in (0, 1, 2):
        prc.record_publish_gate_failure("tests OOM-killed", rc=-9, now=t, send_ntfy_fn=sink)
    assert "OOM" in sink.messages[0]
    assert "rc=-9" in sink.messages[0]


def test_payload_names_regression_for_positive_rc(tmp_path):
    sink = _Sink()
    for t in (0, 1, 2):
        prc.record_publish_gate_failure("tests failed", rc=1, now=t, send_ntfy_fn=sink)
    assert "regression" in sink.messages[0].lower()


# ── recovery clears a durable action_needed item ─────────────────────────────

def test_success_resolves_open_action_needed_item(tmp_path):
    import background.action_needed as an
    sink = _Sink()
    for t in (0, 1, 2):
        prc.record_publish_gate_failure("f", rc=1, now=t, send_ntfy_fn=sink)
    # The fired alert registered a durable open item.
    assert any(i["item_id"] == prc.PUBLISH_GATE_ITEM_ID for i in an.open_items())
    prc.record_publish_gate_success(now=100)
    assert not any(i["item_id"] == prc.PUBLISH_GATE_ITEM_ID for i in an.open_items())


# ══════════════════════════════════════════════════════════════════════════════
# EPISODE MEMORY + ALARM→DIAL — R15 both-ways
# (2026-08-09, DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH, draw 2)
#
# The named defect: on 2026-08-08 ten alarms fired across a SEVEN-HOUR live episode
# and every one of them described "3 failures in the last 60 min" — truthful, and
# indistinguishable from hour one. Meanwhile the cure sat filed in docs/staging/ as
# WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD and lost every draw to feature work.
#
# Each test below is the MUTATION of one of those two properties: strip the episode
# state (or the filed finding) and the assertion must go red, which is the whole
# point — a payload field nothing asserts is a field that silently disappears.
# ══════════════════════════════════════════════════════════════════════════════

def _fire_and_capture(prc_mod, sink, *, n=3, t0=1000.0, step=600.0):
    """Drive a real streak through record_publish_gate_failure and return the alarm text."""
    for i in range(n):
        prc_mod.record_publish_gate_failure(
            "process_run_complete rc=1 on run_complete_%d.md" % i,
            rc=1, git_hash="cafe%d" % i, now=t0 + i * step, send_ntfy_fn=sink)
    assert sink.messages, "the streak should have fired exactly one alarm"
    return sink.messages[-1]


def test_alarm_carries_the_episode_not_just_the_window(tmp_path, monkeypatch):
    """A 7h episode must NARRATE as 7h — the exact 2026-08-08 defect."""
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    sink = _Sink()
    t0 = 1_800_000_000.0
    # The real 2026-08-08 shape: a marker every ~10 min for ~7 hours. The 1h window trim
    # means `failures` never holds more than ~6 of them, so ONLY episode memory can
    # describe the real span — which is exactly why ten pages all read as one hour.
    for i in range(42):
        prc.record_publish_gate_failure("rc=1 marker %d" % i, rc=1, git_hash="abc",
                                        now=t0 + i * (10 * 60), send_ntfy_fn=sink)
    msg = sink.messages[-1]
    assert "EPISODE:" in msg, "no episode memory in the alarm payload"
    assert "wedged since" in msg
    # Asserted as a PROPERTY, not a pinned string: the alarm is re-armed on an hourly
    # cooldown, so the last one fired mid-episode. What must hold is that whichever page
    # the director is looking at describes HOURS and the whole streak — never the window.
    import re as _re
    m = _re.search(r"(\d+)h(\d\d)m and (\d+) consecutive failures in THIS episode", msg)
    assert m, msg
    hours, episode_n = int(m.group(1)), int(m.group(3))
    window_n = int(_re.search(r"failed (\d+) time\(s\)", msg).group(1))
    assert hours >= 6, f"a 7h episode narrated as {hours}h — the defect is back: {msg}"
    assert episode_n > window_n * 4, (
        f"episode count {episode_n} vs in-window {window_n}: the alarm is still only "
        f"describing the window"
    )
    state = json.loads((tmp_path / ".publish_gate_state.json").read_text())
    assert state["episode_failures"] == 42
    assert len(state["failures"]) < 42, (
        "premise check: the window trim must actually be dropping entries, or this "
        "test proves nothing about episode-vs-window"
    )


def test_mutation_episode_start_missing_is_declared_not_guessed(tmp_path, monkeypatch):
    """FAIL-OPEN proof: with no recorded start the alarm must SAY so, never imply hour one."""
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    phrase = prc._episode_phrase(None, 12, 1_800_000_000.0)
    assert "unrecorded" in phrase and "cannot bound the episode" in phrase
    assert "0h00m" not in phrase, "an unknown start must never render as a fresh episode"


def test_episode_counter_survives_the_window_trim_but_clears_on_recovery(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    sink = _Sink()
    t0 = 1_800_000_000.0
    for i in range(5):
        prc.record_publish_gate_failure("rc=1", rc=1, now=t0 + i * (50 * 60), send_ntfy_fn=sink)
    assert json.loads((tmp_path / ".publish_gate_state.json").read_text())["episode_failures"] == 5
    prc.record_publish_gate_success(now=t0 + 6 * 3600)
    after = json.loads((tmp_path / ".publish_gate_state.json").read_text())
    assert after["episode_failures"] == 0 and after["wedge_since"] is None, (
        "a clean publish ends the EPISODE, not just the window"
    )


def test_markers_pending_is_measured_independently_of_the_gate_state(tmp_path, monkeypatch):
    """Anti-tautology (R15): the backlog is counted off the real staging directory, so a
    gate-state file that lies cannot make the pile-up look small."""
    staging = tmp_path / "staging"
    staging.mkdir()
    for i in range(4):
        (staging / ("run_complete_2026080%dT000000Z.md" % i)).write_text("x")
    (staging / "from_rich_notamarker.md").write_text("x")
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    assert prc.pending_run_complete_markers() == 4
    msg = _fire_and_capture(prc, _Sink())
    assert "Markers pending: 4" in msg, msg


def test_markers_pending_unknown_is_not_zero(tmp_path, monkeypatch):
    """FAIL-OPEN proof: an unreadable staging dir must read 'unknown', never '0' — zero
    and unknown are opposite facts and this repo has shipped that confusion before."""
    def _raiser(self, pattern):
        raise OSError("staging unreadable")

    monkeypatch.setattr(prc.Path, "glob", _raiser)
    assert prc.pending_run_complete_markers() is None, (
        "an unreadable staging directory must read as UNKNOWN, never as an empty backlog"
    )
    assert prc.filed_findings() == [], "the citation degrades quietly; the alarm still goes out"


# ── ALARM → DIAL: the alarm names its own cure, and persists it for the draw ──

def test_alarm_cites_filed_findings_and_persists_them_for_the_draw(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD_2026-08-08.md").write_text("x")
    (staging / "WORKER_FINDING_RELATIVE_HOOK_PATHS_WEDGE_SESSION_2026-08-08.md").write_text("x")
    (staging / "ADVISOR_SCOPE_BRIEF_GAS_2026-08-04.md").write_text("x")  # not a finding
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    msg = _fire_and_capture(prc, _Sink())
    assert "FILED FINDINGS ALREADY HOLDING SUSPECTS" in msg, msg
    assert "WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD_2026-08-08.md" in msg
    assert "ADVISOR_SCOPE_BRIEF_GAS" not in msg, "only filed FINDINGS are cures, not scope briefs"
    # The draw reads the STATE FILE, not the NTFY — so the citation must be persisted.
    state = json.loads((tmp_path / ".publish_gate_state.json").read_text())
    assert "WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD_2026-08-08.md" in state["cited_findings"]


def test_mutation_no_filed_findings_no_citation(tmp_path, monkeypatch):
    """The other way (R15): with nothing filed the clause must be ABSENT, not an empty
    'draw these: .' — a control that always emits its own success text cannot fail."""
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    msg = _fire_and_capture(prc, _Sink())
    assert "FILED FINDINGS" not in msg
    assert json.loads((tmp_path / ".publish_gate_state.json").read_text())["cited_findings"] == []


def test_archived_findings_are_not_cited(tmp_path, monkeypatch):
    """A finding moved to done/ has been dispositioned — citing it would re-raise the
    priority of work that is already closed."""
    staging = tmp_path / "staging"
    (staging / "done").mkdir(parents=True)
    (staging / "done" / "WORKER_FINDING_OLD_2026-07-01.md").write_text("x")
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    assert prc.filed_findings() == []


def test_citation_is_bounded(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    staging.mkdir()
    for i in range(20):
        (staging / ("WORKER_FINDING_X%02d_2026-08-08.md" % i)).write_text("x")
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    cited = prc.filed_findings()
    assert len(cited) == prc.PUBLISH_GATE_MAX_CITED_FINDINGS, (
        "an unbounded citation list turns the page back into noise"
    )
