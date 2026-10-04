"""A caller that redirects the dashboard's output must not rewrite a tracked file.

THE DEFECT IT SERVES. `generate()` wrote `site/data/dd_opening_arms.json` to an absolute path of
its own, so the three tests that redirect `OUTPUT_PATH` to `tmp_path` and call it --
`test_website_integrity_fix.py` (two), `test_generate_dashboard_mgmt.py`, `test_query_interface.py`
-- rewrote the tracked feed in whatever tree they ran in. On 2026-10-04 that dirtied the head-red
bisect's extract and killed it at its first `git checkout`. Every extract-based census (the gate,
the bisect, the publish gate) inherits the same fragility.

WHY A WRITE RECORDER AND NOT `git status --porcelain`. At origin the rewritten bytes are identical
to HEAD's, because the feed is a pure function of a committed artefact, so `git status` reads clean
there. A status census passes on that coincidence, and fails only when the bisect has checked out
a commit whose artefact and feed disagree. The property is that the write happens at all, so the
recorder asks that directly.

SCOPE: tracked paths. `simulation.live_population` also writes two UNTRACKED run-output records
under `docs/observability/` while the book is resolved. They cannot block a checkout, and they
belong to the world side, so this control does not grade them.

MUTATION (run, seen red, reverted): restore `_write_dd_opening_arms_feed(DD_ARMS_FEED)` in
`generate()` -> `test_generate_writes_no_tracked_path_when_its_output_is_redirected` reds, naming
`site/data/dd_opening_arms.json`.
"""
from __future__ import annotations

import builtins
import io
import json
import os
import subprocess
from pathlib import Path

import pytest

import tools.generate_dashboard_data as gdd

PROJECT = Path(gdd.PROJECT).resolve()


def _tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=PROJECT, capture_output=True, check=True)
    return {p for p in out.stdout.decode().split("\0") if p}


@pytest.fixture
def writes(tmp_path, monkeypatch):
    """Every path `generate()` opens for writing or replaces into, resolved."""
    seen: list[Path] = []
    real_open, real_replace = builtins.open, os.replace

    def recording_open(file, mode="r", *a, **k):
        if isinstance(file, (str, os.PathLike)) and any(c in mode for c in "wax+"):
            seen.append(Path(file).resolve())
        return real_open(file, mode, *a, **k)

    def recording_replace(src, dst, *a, **k):
        seen.append(Path(dst).resolve())
        return real_replace(src, dst, *a, **k)

    run_json = tmp_path / "run_output_test.json"
    run_json.write_text(json.dumps({"total_net_gbp": 100.0, "_cache_meta": {"git_commit": "x"}}))
    monkeypatch.setattr(gdd, "OUTPUT_PATH", tmp_path / "dashboard.json")
    monkeypatch.setattr(gdd, "load_spot_monthly", lambda: {})
    # `Path.write_text` reaches `io.open`, a separate binding from `builtins.open`.
    monkeypatch.setattr(builtins, "open", recording_open)
    monkeypatch.setattr(io, "open", recording_open)
    monkeypatch.setattr(os, "replace", recording_replace)
    gdd.generate(run_json)
    monkeypatch.undo()
    return seen


def test_the_recorder_sees_the_writes_generate_makes(writes, tmp_path):
    """THE CONTROL MUST BE ABLE TO SEE A WRITE. A recorder that catches nothing passes the census
    below whatever `generate()` does, so both files it writes must be in the record, at the
    redirected location."""
    assert (tmp_path / "dashboard.json").resolve() in writes
    assert (tmp_path / gdd.DD_ARMS_FEED.name).resolve() in writes, (
        "the opening-DD feed was not written beside the redirected dashboard")


def test_generate_writes_no_tracked_path_when_its_output_is_redirected(writes):
    tracked = _tracked()
    offenders = sorted(
        rel for rel in (
            p.relative_to(PROJECT).as_posix() for p in writes if p.is_relative_to(PROJECT))
        if rel in tracked)
    assert not offenders, (
        "generate() rewrote tracked file(s) {} although its output was redirected to a tmp dir, "
        "so any test that calls it dirties the extract it runs in".format(offenders))
