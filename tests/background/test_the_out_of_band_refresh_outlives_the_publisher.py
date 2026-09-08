"""The publish cycle's one detached spawn, and the cgroup that was going to kill it.

THE DEFECT THIS EXISTS FOR, found by censusing the tree for the shape after the launcher was
built. `_trigger_frozen_baseline_refresh_out_of_band` spawned a multi-minute decade replay with
`start_new_session=True`, under the comment *"so it outlives this publish process"* -- the exact
claim three launches of one measurement refuted. Every user unit on this machine is
KillMode=control-group; `setsid` changes the session and the process group, and a cgroup is
neither. Both streams went to DEVNULL, so a death and a success left the identical trace and
nothing could ever have noticed.

WHY THE CONTROL IS ON THE PUBLISH PATH AND NOT ON THE LAUNCHER. `tests/background/
test_launch_long_job.py` already proves the launcher detaches; a control that called it again here
would be blind to the only thing in question, which is whether THIS caller goes through it.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]


@pytest.fixture
def publisher():
    sys.path.insert(0, str(PROJECT))
    from background import process_run_complete
    return process_run_complete


def test_the_stale_refresh_goes_through_the_one_launcher(publisher, monkeypatch):
    """Fires on: a refresh spawned by any route that does not put it in a cgroup of its own.

    Asserted against the CALL the publish path makes, because that is the whole question here --
    the launcher's own detach is proved in its own suite, and re-proving it would say nothing
    about this caller. The artefact matters as much as the route: a record without one can never
    settle to FINISHED, so a completed refresh would read as an unexplained death forever.
    """
    from background import launch_long_job

    seen = {}

    def _fake_launch(job, command, **kw):
        seen.update(job=job, command=command, **kw)
        return {"unit": f"longjob-{job}", "log": "/var/tmp/x.log", "claim": "live"}

    monkeypatch.setattr(launch_long_job, "launch", _fake_launch)
    monkeypatch.setattr("tools.run_frozen_baseline.should_refresh_baseline", lambda: True)
    monkeypatch.setattr(publisher, "log", lambda *a, **k: None)
    monkeypatch.setattr(subprocess, "Popen", _never_popen)

    publisher._trigger_frozen_baseline_refresh_out_of_band()

    assert seen["command"][1:] == ["-m", "tools.run_frozen_baseline", "--if-stale"]
    assert seen["artefact"].endswith("site/state/frozen_policy_baseline.json"), seen["artefact"]
    assert seen["job"], "a launch with no job name cannot be recorded or re-asked"


def _never_popen(*a, **k):
    raise AssertionError(
        "the out-of-band refresh spawned a process directly. A setsid/Popen detach dies with the "
        "publisher's cgroup -- launch it through background.launch_long_job.")


def test_a_refused_launch_never_reaches_the_publish_path(publisher, monkeypatch):
    """Fires on: a launcher exception escaping into the publish cycle.

    The stated contract of this spawn has always been that publishing NEVER blocks on it, and the
    change that fixed the cgroup death is exactly the kind that could quietly take that away --
    the old code could not raise, and the new one calls something that refuses by design (a unit
    of that name already live, no systemd-run, an unwritable record). A refresh that cannot start
    must cost a log line, not a publish cycle.
    """
    from background import launch_long_job

    def _refuse(*a, **k):
        raise launch_long_job.LaunchRefused("a live unit already holds the name")

    lines = []
    monkeypatch.setattr(launch_long_job, "launch", _refuse)
    monkeypatch.setattr("tools.run_frozen_baseline.should_refresh_baseline", lambda: True)
    monkeypatch.setattr(publisher, "log", lambda msg, *a, **k: lines.append(str(msg)))

    publisher._trigger_frozen_baseline_refresh_out_of_band()  # must not raise

    assert any("NOT launched" in ln for ln in lines), lines
    assert any("existing baseline" in ln for ln in lines), (
        "a refusal must say what publishing did instead, or the log records a non-event")


def test_a_fresh_baseline_launches_nothing_at_all(publisher, monkeypatch):
    """THE PARTITION. Fires on: a caller that launches unconditionally.

    Without this leg, both tests above would pass on a publisher that started a decade replay
    every single cycle -- which is a far more expensive defect than the one being fixed, and one
    the staleness check is the only thing preventing.
    """
    from background import launch_long_job

    monkeypatch.setattr(launch_long_job, "launch", _never_popen)
    monkeypatch.setattr("tools.run_frozen_baseline.should_refresh_baseline", lambda: False)
    monkeypatch.setattr(publisher, "log", lambda *a, **k: None)

    publisher._trigger_frozen_baseline_refresh_out_of_band()
