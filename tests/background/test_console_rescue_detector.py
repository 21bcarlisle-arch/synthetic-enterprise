"""R15 both-ways proof for HX2 event E1 -- console_rescue_active().

FIRES: a console sanctified AFTER an already-escalated STUCK streak began.
STAYS SILENT (the R15-required benign look-alike): a console sanctified BEFORE the
stall began -- a routine long-lived director session must never be mistaken for a
rescue of a stall it predates.
Guards the three R15 killer patterns explicitly:
  TAUTOLOGY  -- the detector reads two files NEITHER of which it writes itself.
  FAIL-OPEN  -- a corrupt-but-present state file raises, not silently 'clear'.
  FAIL-SILENT (module-level, proven by test_stall_class_register.py) -- an exception
              from this detector must classify as 'unavailable', never 'clear', at
              the register layer.
"""
import json
import time

import pytest

from background.console_rescue_detector import (
    StallDetectorUnavailable,
    console_rescue_active,
)

HOUR = 3600


def _write(path, obj):
    path.write_text(json.dumps(obj))


def test_fires_when_console_sanctified_after_escalated_stall(tmp_path):
    now = time.time()
    stuck_path = tmp_path / "stuck.json"
    reg_path = tmp_path / "registry.json"
    first_seen_at = now - 2 * HOUR
    _write(stuck_path, {"key": "some-work", "first_seen_at": first_seen_at, "escalated": True})
    marked_at = _iso(first_seen_at + 600)  # console opened 10 min AFTER the stall began
    _write(reg_path, {"12345": {"start_ticks": 1, "marked_at": marked_at}})

    result = console_rescue_active(now=now, sanctity_registry_path=reg_path, stuck_state_path=stuck_path)

    assert result is not None
    assert "CONSOLE RESCUE" in result
    assert "12345" in result


def test_silent_when_console_predates_the_stall(tmp_path):
    """THE benign look-alike: a console already open BEFORE the stall began, still
    sanctified while the stuck streak later escalates, must NOT read as a rescue."""
    now = time.time()
    stuck_path = tmp_path / "stuck.json"
    reg_path = tmp_path / "registry.json"
    first_seen_at = now - 2 * HOUR
    _write(stuck_path, {"key": "some-work", "first_seen_at": first_seen_at, "escalated": True})
    marked_at = _iso(first_seen_at - HOUR)  # console opened BEFORE the stall began
    _write(reg_path, {"999": {"start_ticks": 1, "marked_at": marked_at}})

    result = console_rescue_active(now=now, sanctity_registry_path=reg_path, stuck_state_path=stuck_path)

    assert result is None


def test_silent_when_no_stuck_state_file(tmp_path):
    reg_path = tmp_path / "registry.json"
    _write(reg_path, {"1": {"start_ticks": 1, "marked_at": _iso(time.time())}})
    result = console_rescue_active(
        now=time.time(), sanctity_registry_path=reg_path, stuck_state_path=tmp_path / "missing.json",
    )
    assert result is None


def test_silent_when_stuck_but_not_yet_escalated(tmp_path):
    now = time.time()
    stuck_path = tmp_path / "stuck.json"
    reg_path = tmp_path / "registry.json"
    _write(stuck_path, {"key": "some-work", "first_seen_at": now - 60, "escalated": False})
    _write(reg_path, {"1": {"start_ticks": 1, "marked_at": _iso(now)}})

    result = console_rescue_active(now=now, sanctity_registry_path=reg_path, stuck_state_path=stuck_path)

    assert result is None


def test_silent_when_escalated_but_no_console_ever_sanctified(tmp_path):
    now = time.time()
    stuck_path = tmp_path / "stuck.json"
    _write(stuck_path, {"key": "x", "first_seen_at": now - 2 * HOUR, "escalated": True})
    result = console_rescue_active(
        now=now, sanctity_registry_path=tmp_path / "missing_registry.json", stuck_state_path=stuck_path,
    )
    assert result is None


# ── FAIL-OPEN guard: a state file that EXISTS but is corrupt must not read as clear ──

def test_unavailable_when_stuck_state_is_corrupt_json(tmp_path):
    stuck_path = tmp_path / "stuck.json"
    stuck_path.write_text("{not valid json")
    reg_path = tmp_path / "registry.json"
    _write(reg_path, {})

    with pytest.raises(StallDetectorUnavailable):
        console_rescue_active(now=time.time(), sanctity_registry_path=reg_path, stuck_state_path=stuck_path)


def test_unavailable_when_registry_is_corrupt_json(tmp_path):
    now = time.time()
    stuck_path = tmp_path / "stuck.json"
    _write(stuck_path, {"key": "x", "first_seen_at": now - 2 * HOUR, "escalated": True})
    reg_path = tmp_path / "registry.json"
    reg_path.write_text("[]")  # valid JSON, but not an object -- must still raise

    with pytest.raises(StallDetectorUnavailable):
        console_rescue_active(now=now, sanctity_registry_path=reg_path, stuck_state_path=stuck_path)


def test_unavailable_when_escalated_with_no_numeric_first_seen_at(tmp_path):
    stuck_path = tmp_path / "stuck.json"
    _write(stuck_path, {"key": "x", "first_seen_at": "not-a-number", "escalated": True})
    reg_path = tmp_path / "registry.json"
    _write(reg_path, {})

    with pytest.raises(StallDetectorUnavailable):
        console_rescue_active(now=time.time(), sanctity_registry_path=reg_path, stuck_state_path=stuck_path)


def _iso(epoch: float) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()
