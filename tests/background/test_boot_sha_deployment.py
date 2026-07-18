"""OPS1 sub-step 5 — deployment-by-construction (G-D1/G-D3): booted-SHA stamp + drift reconcile.

R15 mutation coverage: a daemon running code OLDER than HEAD must be FLAGGED as stale. This
generalises the prior own-script-mtime check (which missed imported-module drift). The tests
inject a stale boot-SHA and assert it is flagged; a current one and a fail-safe unknown stay
silent — a drift control that never fires (or fires on a current daemon) is the disease.
"""
from __future__ import annotations

from background import boot_sha
from background.process_reconciler import boot_sha_drift


def test_stamp_and_read_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(boot_sha, "BOOT_DIR", tmp_path / "boot")
    monkeypatch.setattr(boot_sha, "current_head", lambda: "deadbeefcafe")
    boot_sha.stamp("sim-runner")
    assert boot_sha.read_boot_sha("sim-runner") == "deadbeefcafe"
    assert boot_sha.read_boot_sha("never-stamped") is None       # absent -> None, never raises


def test_current_head_is_a_sha_or_none():
    h = boot_sha.current_head()
    assert h is None or (len(h) >= 7 and all(c in "0123456789abcdef" for c in h))


def test_drift_flags_a_stale_running_daemon():
    # a booted OLD, b booted current, c never stamped -> only a is stale
    stale = boot_sha_drift("HEAD1", {"a": "OLD", "b": "HEAD1", "c": None}, ["a", "b", "c"])
    assert stale == ["a"]                                          # THE mutation: stale MUST flag


def test_drift_is_fail_safe_on_missing_stamp_and_missing_head():
    assert boot_sha_drift("HEAD1", {"a": None}, ["a"]) == []       # no stamp -> not a false 'stale'
    assert boot_sha_drift(None, {"a": "OLD"}, ["a"]) == []          # git unavailable -> can't judge


def test_drift_only_considers_running_daemons():
    # 'a' has a stale stamp but is NOT running -> a stopped daemon is not "running stale code"
    assert boot_sha_drift("HEAD1", {"a": "OLD"}, []) == []


def test_generated_units_stamp_boot_sha_before_execstart():
    from background import generate_units as G
    units = G.regenerate()
    assert units, "expected generated systemd units"
    for fname, text in units.items():
        session = fname[: -len(".service")]
        assert f"ExecStartPre=-/usr/bin/python3 -m background.boot_sha {session}" in text
        # G-D3: the stamp must run BEFORE the daemon starts, or it records the wrong SHA
        assert text.index("ExecStartPre") < text.index("ExecStart=")

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
