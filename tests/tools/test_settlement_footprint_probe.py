"""The probe that makes the producer's footprint measurable without running the job that OOMs.

The defect it serves is recorded in
`WORKER_FINDING_THE_PRODUCER_OOMS_BECAUSE_THE_BOOK_GREW_AND_SETTLEMENT_SCALES_WITH_IT_2026-08-24.md`:
the footprint repair is the only one of three that is not the director's, and its own test loop is
the 40-minute 14GB run that cannot complete. This tool measures short horizons instead.

WHAT IS UNDER TEST is mostly the REFUSAL. A probe that launches a second heavy job beside a live
producer run would compete for exactly the memory it is measuring and could cause the OOM it is
investigating -- a measurement that changed its own subject. So the guard is the load-bearing part
and it is tested in all three directions: fires, stands down, and fails CLOSED.
"""
from __future__ import annotations

import subprocess

import pytest

from tools import settlement_footprint_probe as probe


class _Proc:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


def test_the_probe_REFUSES_while_a_producer_run_is_in_flight(monkeypatch):
    """THE GUARD. Competing for the memory under measurement is how a probe causes the outage it
    is investigating."""
    monkeypatch.setattr(probe.subprocess, "run", lambda *a, **k: _Proc(stdout="2795477\n"))

    assert probe.a_run_is_in_flight() == "2795477"
    assert probe.main(["--years", "2017"]) == 2, "a refusal must be a non-zero exit"


def test_MUTATION_the_probe_stands_down_on_an_idle_box(monkeypatch):
    """R15 null control. A guard that always refused would pass the test above on a tool that
    could never run at all, which is the same as not having built it."""
    monkeypatch.setattr(probe.subprocess, "run", lambda *a, **k: _Proc(stdout="", returncode=1))
    assert probe.a_run_is_in_flight() is None

    measured = []
    monkeypatch.setattr(probe, "measure",
                        lambda y, **k: measured.append(y) or {"end_year": y, "ok": True,
                                                              "peak_rss_mb": 100.0})
    assert probe.main(["--years", "2017"]) == 0
    assert measured == [2017], "an idle box must actually be measured"


def test_the_guard_FAILS_CLOSED_when_it_cannot_tell(monkeypatch):
    """R15 fail-silent: an unavailable check is a FAILED check. The harmful direction here is
    launching a second 14GB job, not skipping a measurement, so an unusable pgrep must refuse."""
    def _boom(*a, **k):
        raise OSError("pgrep missing")

    monkeypatch.setattr(probe.subprocess, "run", _boom)
    live = probe.a_run_is_in_flight()

    assert live is not None and "refusing" in live.lower()
    assert probe.main(["--years", "2017"]) == 2


def test_force_overrides_the_guard_deliberately(monkeypatch):
    """The override exists so an idle box is not held hostage by a stale detection -- but it must
    be explicit, never the default."""
    monkeypatch.setattr(probe, "a_run_is_in_flight", lambda: "999")
    monkeypatch.setattr(probe, "measure", lambda y, **k: {"end_year": y, "ok": True,
                                                          "peak_rss_mb": 100.0})
    assert probe.main(["--years", "2017", "--force"]) == 0


def test_a_child_killed_by_the_OOM_killer_is_REPORTED_not_hidden(monkeypatch):
    """The interesting outcome, not an error to swallow. A probe that reported only successful
    horizons would derive its scaling from the survivors of the very bound it is measuring."""
    monkeypatch.setattr(probe.subprocess, "run",
                        lambda *a, **k: _Proc(returncode=-9, stderr="Maximum resident set size (kbytes): 14198884"))

    row = probe.measure(2025)
    assert row["ok"] is False
    assert row["killed_by_signal"] == 9
    assert row["peak_rss_mb"] == pytest.approx(13866.1, abs=1.0)


def test_the_scaling_separates_per_year_cost_from_fixed_cost():
    """The reading that decides whether the footprint work is worth doing: a large FIXED term means
    shortening the window will not save the producer, and the effort belongs elsewhere."""
    out = probe.summarise([
        {"end_year": 2017, "peak_rss_mb": 2000.0},
        {"end_year": 2019, "peak_rss_mb": 4000.0},
    ])

    assert out["slope_mb_per_year"] == pytest.approx(1000.0)
    assert "fixed" in out["note"]


def test_one_horizon_cannot_produce_a_scaling_law():
    """VACUITY GUARD. A slope from a single point is invented, not measured."""
    out = probe.summarise([{"end_year": 2017, "peak_rss_mb": 2000.0}])
    assert out["slope_mb_per_year"] is None
    assert "at least two" in out["note"]
