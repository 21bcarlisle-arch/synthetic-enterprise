"""OPS1 sub-step 4: the committed systemd units are DERIVED from the one manifest, no drift.

The anti-drift test is the load-bearing one (same pattern as sub-steps 2/3): the committed
background/systemd/*.service files MUST equal what the generator emits from process_manifest.yaml,
so the readable-standard-systemd layer (relatable IP) can never silently diverge from the single
declaration."""
from __future__ import annotations

from pathlib import Path

from background import generate_units as G
from background import process_reconciler as R

UNITS_DIR = Path(G.__file__).resolve().parent / "systemd"


def test_committed_units_equal_regenerate_output():
    """Anti-drift: every committed unit == the generator's output, and there are no extra or
    missing committed units. If this fails, run `python3 background/generate_units.py`."""
    expected = G.regenerate()
    committed = {p.name: p.read_text() for p in UNITS_DIR.glob("*.service")}
    assert set(committed) == set(expected), (
        f"committed units {sorted(committed)} != generated {sorted(expected)} — regenerate")
    for name, text in expected.items():
        assert committed[name] == text, f"{name} drifted from the manifest — regenerate"


def test_exactly_one_unit_per_systemd_owned_entry():
    systemd_sessions = {e["session"] for e in R.load_manifest() if e.get("owner") == "systemd"}
    generated = {name[:-len(".service")] for name in G.regenerate()}
    assert generated == systemd_sessions


def test_seat_retired_and_file_api_get_no_generated_unit():
    generated = set(G.regenerate())
    assert "claude.service" not in generated            # the worker seat: not a systemd unit
    assert "autonomous-runner.service" not in generated  # retired: no unit
    assert "file-api.service" not in generated           # separately owned (schedule_manifest)


def test_every_unit_has_the_g_l3_crashloop_bound_and_soft_env():
    """G-L3 baked into every unit: StartLimitBurst/IntervalSec (a crash-loop -> `failed`, the
    32,707 lesson) and EnvironmentFile with `-` (a missing secret degrades, never crash-loops)."""
    for name, text in G.regenerate().items():
        assert f"StartLimitBurst={G.START_LIMIT_BURST}" in text, name
        assert f"StartLimitIntervalSec={G.START_LIMIT_INTERVAL}" in text, name
        assert "EnvironmentFile=-" in text, name
        assert "ExecStart=/usr/bin/python3" in text, name
        assert "WantedBy=default.target" in text, name


def test_held_and_dark_units_are_still_generated_just_not_started():
    """A HELD/DARK daemon still gets an INSTALLED unit (so it exists, readable) — the hold is
    expressed by NOT enabling/starting it (install_schedule), never by omitting the unit."""
    generated = set(G.regenerate())
    for s in ("supervisor.service", "deadmans-switch.service",
              "worker-seat-manager.service", "executor-daemon.service"):
        assert s in generated
