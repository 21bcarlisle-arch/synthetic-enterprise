"""STATUS-DOC HONESTY gate (director P0, 2026-07-17, step 5).

R15 mutation coverage: the gate must CATCH a narrative that asserts a non-running daemon / retired
governance model as current (tonight's exact failure: twin-approver / three-lanes / A3), and must
NOT flag an honest historical incident record -- a false positive would wedge the publish path.
"""
from __future__ import annotations

from background import status_honesty as H

# Tonight's actual stale prose (verbatim shapes from the committed LATEST.md header).
TONIGHT_STALE = (
    "## Epoch-2 BUILD live via the twin-approver seat: A3 approval interface banked, THREE LANES\n"
    "self-driving BUILD lane open (DIRECTOR_TWIN standing-approver, canon v2 §3a). "
    "Two forks in flight (one BUILD, one Expert Hour)."
)
TRUTHFUL = (
    "Serial self-sustaining pull loop; 3 systemd daemons (worker-seat-manager, supervisor, "
    "deadmans-switch). BUILD-open across a gate is authorized by a director console act (the "
    "gate-wall); the twin is a voice-not-hand. Parallelism is bounded to 3 disjoint forks, each "
    "merged to main or reaped."
)
HISTORICAL = (
    "Root cause: session_watchdog fired /usage via a raw send-keys once per cycle; FIXED. "
    "The reaper was deleted; executor-daemon is dark and autonomous-runner is retired."
)


def test_catches_tonights_stale_model_claims():
    r = H.check_status_honesty(TONIGHT_STALE)
    assert r["status"] == "STALE" and r["honest"] is False
    claims = {c["claim"] for c in r["stale_claims"]}
    # the exact things that made the director misread the system tonight
    assert "twin-approver seat" in claims
    assert "DIRECTOR_TWIN standing-approver" in claims
    assert "self-driving BUILD lane" in claims
    assert "forks in flight" in claims
    assert "A3 approval interface" in claims


def test_truthful_running_system_is_HONEST():
    assert H.check_status_honesty(TRUTHFUL)["honest"] is True


def test_honest_historical_incident_record_is_NOT_flagged():
    # A past-tense record naming retired/dark daemons must PASS -- a false positive would wedge the
    # publish path (every LATEST.md commit refused).
    r = H.check_status_honesty(HISTORICAL)
    assert r["honest"] is True, r["stale_claims"]


def test_non_running_daemon_asserted_as_running_is_flagged():
    r = H.check_status_honesty("the executor-daemon is live and driving the loop right now")
    assert r["honest"] is False
    assert any(c["claim"] == "executor-daemon" for c in r["stale_claims"])


def test_non_running_daemon_with_historical_marker_is_exempt():
    assert H.check_status_honesty("executor-daemon is retired -- superseded, no longer runs")["honest"] is True


def test_deadman_fires_status_stale_transition_only(tmp_path, monkeypatch):
    from background import deadmans_switch as D
    import background.notify as N
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    monkeypatch.setattr(D, "LOG_FILE", tmp_path / "log.md")
    calls = []
    monkeypatch.setattr(N.ntfy_utils, "send_ntfy", lambda msg, **k: calls.append(msg) or "id")
    monkeypatch.setattr(
        "background.status_honesty.evaluate_status_honesty",
        lambda: {"status": "STALE", "honest": False, "detail": "2 stale claim(s)",
                 "stale_claims": [{"claim": "twin-approver seat", "why": "x"}]},
    )
    D._check_status_honesty()
    assert len(calls) == 1 and "STATUS STALE" in calls[0]
    D._check_status_honesty()
    assert len(calls) == 1                               # transition-only (R5)


def test_live_gate_wrapper_is_well_formed_and_fail_safe(tmp_path):
    r = H.evaluate_status_honesty(tmp_path / "missing.md")   # unreadable -> not a staleness finding
    assert r["honest"] is True
    good = tmp_path / "good.md"
    good.write_text(TRUTHFUL)
    assert H.evaluate_status_honesty(good)["honest"] is True
    bad = tmp_path / "bad.md"
    bad.write_text(TONIGHT_STALE)
    assert H.evaluate_status_honesty(bad)["honest"] is False
