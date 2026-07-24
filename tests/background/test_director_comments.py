"""Retirement proof for the director page-comment channel.

DIRECTOR RULING — DIRECTOR_RULING_RETIRE_PAGE_COMMENT_CHANNEL_2026-07-24.md: the
PIN-authenticated page-comment channel is decommissioned as a director-authority
path, PERMANENTLY. `background/director_comments.py` is now a safe-no-op tombstone
with the intake authority path deleted.

This module is the R15 proof (both ways) that the channel is INERT and its
retirement is the EXPECTED state the reconciler protects — not a live daemon that
merely happens to be down. It replaces the old intake tests (a channel that no
longer exists cannot be unit-tested for correct staging).

R15 both ways:
  - INERT: the authority path (`_write_comment_to_staging`), the poll (`check_once`)
    and the parser (`parse_comment_submission`) are GONE from the module, and a
    bare `main()` stages nothing. If any of those names is re-added, these tests
    FAIL — a silent revival of the authority path is caught.
  - CANNOT-RESURRECT: the reconciler treats `retired`+not-running as OK (no MISSING
    drift alarm — retirement is expected), and `retired`+running as RETIRED_RUNNING
    (an alarm) — so a self-healing reconciler can never quietly bring it back.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from background import director_comments as dc
from background import process_reconciler as R
from background import generate_units as G

MANIFEST_ENTRY = "director-comments"


# ── INERT: the authority path is deleted, not merely disabled ─────────────────
def test_authority_path_functions_are_deleted():
    """The intake authority path, the poll and the parser must NOT exist on the
    retired module. Re-adding any of them (a silent revival) fails here."""
    for gone in ("_write_comment_to_staging", "check_once", "parse_comment_submission",
                 "intake_locked", "STAGING_DIR", "COMMENTS_TOPIC", "COMMENTS_PIN"):
        assert not hasattr(dc, gone), f"retired channel must not expose {gone!r} — authority path revived?"


def test_module_declares_itself_retired():
    assert getattr(dc, "RETIRED", False) is True
    assert "RETIRED" in dc.RETIRED_NOTICE.upper()


def test_main_is_a_safe_noop_that_stages_nothing(tmp_path, monkeypatch):
    """A bare launch of the retired daemon stages NOTHING and exits 0 — even if a
    real staging dir exists. (Ruling point 1: the daemon is a safe no-op.)"""
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(dc, "LOG_FILE", tmp_path / "log.md")
    rc = dc.main()
    assert rc == 0
    # Nothing staged anywhere the module could reach.
    assert list(staging.iterdir()) == []
    assert not any(staging.glob("from_rich_comment_*"))


# ── The manifest declares retirement (so the reconciler expects it down) ──────
def test_manifest_entry_is_retired_with_no_generated_unit():
    entry = next(e for e in R.load_manifest() if e["session"] == MANIFEST_ENTRY)
    assert entry["state"] == "retired"
    assert entry["owner"] != "systemd", "a retired daemon must not be systemd-owned (no unit)"
    # reason+flip are mandatory for a non-enabled entry (schema) and must name the ruling.
    assert "RETIRE" in entry["reason"].upper()
    assert entry["flip"]
    # generate_units emits NO unit for it (retired == no committed unit).
    assert f"{MANIFEST_ENTRY}.service" not in G.regenerate()


# ── CANNOT-RESURRECT: reconciler R15 both ways ────────────────────────────────
def _status_for(session: str, tmux_running: set[str]) -> dict:
    results = R.reconcile(unit_states={}, seat_active=False, tmux_running=tmux_running)
    return next(r for r in results if r["session"] == session)


def test_reconciler_retired_and_down_is_expected_not_missing():
    """Ruling point 2: retirement is the EXPECTED state — a not-running retired
    channel must classify OK, never MISSING (no standing drift alarm)."""
    r = _status_for(MANIFEST_ENTRY, tmux_running=set())
    assert r["status"] == "OK"
    assert r["alarm"] is False


def test_reconciler_alarms_if_the_retired_channel_is_ever_running():
    """The mutation half: if the retired authority path is ever observed running
    (a resurrection), the reconciler alarms RETIRED_RUNNING — it can never be
    silently brought back."""
    r = _status_for(MANIFEST_ENTRY, tmux_running={MANIFEST_ENTRY})
    assert r["status"] == "RETIRED_RUNNING"
    assert r["alarm"] is True


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
pytestmark = pytest.mark.operational
