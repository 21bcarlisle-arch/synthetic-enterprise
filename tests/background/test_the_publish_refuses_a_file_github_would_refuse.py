"""The publish refuses, by name, a file GitHub would refuse at push (BLOCKING, 2026-10-10).

THE DEFECT. `git_commit_push` commits `docs/reports/run_output_latest.json`, and the runs grew
past GitHub's 100 MiB per-file limit (123.5 MB at indent=2). Nothing asked the size before the
landing, so the first publish after the weekly window would have gated for ten minutes and then
been refused at the push, leaving a local commit origin can never take.
See docs/staging/SEAT_FINDING_THE_PUBLISHED_RUN_OUTGREW_GITHUBS_FILE_LIMIT_2026-10-10.md.

WHAT EACH TEST KILLS:

  * `..._a_file_over_the_limit_is_refused_by_name` -- delete the `_oversized` block from
    `git_commit_push`, or make `_files_over_push_limit` return `[]`
  * `..._a_file_inside_a_staged_directory_is_seen` -- skip directories in the walk
  * `..._the_partition_is_reachable`                -- THE CONTROL OVER BOTH BRANCHES: a guard
    that refuses everything passes the first two; this one lands a file under the limit
  * `..._the_run_writer_is_compact`                 -- restore `json.dumps(data, indent=2)` in
    `save_run_output_json`
  * `..._the_committed_run_compacts_and_is_admitted` -- the real committed run, written by the
    real writer, read back equal and admitted by the real guard
"""
from __future__ import annotations

import contextlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from background import process_run_complete as prc
from tools import run_annual_report as rar

REPO = Path(__file__).resolve().parents[2]
OVER = prc.GITHUB_PUSH_FILE_LIMIT_BYTES + 1024 * 1024  # 101 MiB


def _sparse(path: Path, size: int) -> None:
    """A file whose st_size is `size` without writing `size` bytes to the disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle:
        handle.truncate(size)


class _Done:
    returncode, stdout, stderr = 0, "", ""


@pytest.fixture
def publish(tmp_path, monkeypatch):
    """Drive `git_commit_push` in a scratch tree; returns (run, landed, alarms)."""
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "docs" / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "docs" / "staging" / "done")
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "docs" / "status" / "LATEST.md")
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", tmp_path / ".last_push_time.json")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / ".last_publish_cause.json")
    monkeypatch.setattr(prc, "tree_lock", lambda: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: 0)
    monkeypatch.setattr(prc, "_MARKERS_ARCHIVED_BY_THIS_RUN", [])
    monkeypatch.setattr(prc.subprocess, "run", lambda cmd, **kw: _Done())
    for rel in ("docs/reports/ANNUAL_REPORT.md", "docs/status/LATEST.md",
                "site/data/dashboard.json"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("{}")

    landed: list[list[str]] = []
    alarms: list[str] = []

    def fake_land(pathspec, msg, git_hash):
        landed.append(list(pathspec))
        return {"sha": "0" * 40, "refusal": "", "lost": []}

    monkeypatch.setattr(prc, "_land_publish_commit", fake_land)
    import background.notify as notify_mod
    # Only the size refusal's own page: a landed cycle goes on to the push leg, which pages too.
    monkeypatch.setattr(notify_mod, "notify",
                        lambda msg, **kw: alarms.append(msg) if "TOO LARGE" in msg else None)

    def run():
        outcome: dict = {}
        prc.git_commit_push("abc1234", 1000.0, outcome=outcome)
        return outcome

    return run, landed, alarms


def test_a_file_over_the_limit_is_refused_by_name(publish, tmp_path):
    run, landed, alarms = publish
    _sparse(tmp_path / "site" / "data" / "run_sized.json", OVER)

    outcome = run()

    assert landed == [], "a 101 MiB file reached the landing; GitHub would refuse the push"
    assert outcome["reason"] == prc.COMMIT_REFUSED
    assert prc.COMMIT_REFUSED not in prc.RETRYABLE_PUBLISH_OUTCOMES  # the next cycle retries
    assert len(alarms) == 1, "the refusal must reach the seat's surface (NTFY), not the log alone"
    for fact in ("site/data/run_sized.json", "{:,}".format(OVER),
                 "{:,}".format(prc.GITHUB_PUSH_FILE_LIMIT_BYTES)):
        assert fact in alarms[0], "the refusal does not name {!r}: {}".format(fact, alarms[0])


def test_a_file_inside_a_staged_directory_is_seen(publish, tmp_path):
    run, landed, alarms = publish
    (tmp_path / "site" / "data" / "customers.json").write_text("{}")
    _sparse(tmp_path / "site" / "data" / "customers" / "c1.json", OVER)

    run()

    assert landed == [] and "site/data/customers/c1.json" in alarms[0]


def test_the_partition_is_reachable(publish, tmp_path):
    """THE CONTROL OVER BOTH BRANCHES: at the limit lands, one byte over refuses."""
    run, landed, alarms = publish
    big = tmp_path / "site" / "data" / "run_sized.json"
    _sparse(big, prc.GITHUB_PUSH_FILE_LIMIT_BYTES)
    run()
    _sparse(big, prc.GITHUB_PUSH_FILE_LIMIT_BYTES + 1)
    run()

    assert len(landed) == 1 and str(big) in landed[0] and len(alarms) == 1


def test_the_run_writer_is_compact(tmp_path, monkeypatch):
    data = {"_cache_meta": {"git_commit": "abc1234", "generated_at_utc": "20261010T000000Z"},
            "bills": [{"a": 1, "b": [1, 2]}]}
    monkeypatch.setattr(rar, "extract_report_data", lambda run_output: run_output)
    monkeypatch.setattr(rar, "reconcile_and_stamp", lambda d: d)
    monkeypatch.setattr(rar, "RUN_OUTPUT_LATEST_PATH", tmp_path / "run_output_latest.json")
    monkeypatch.setattr(rar, "RUN_OUTPUT_VERSIONED_DIR", tmp_path / "versioned")

    latest, versioned = rar.save_run_output_json(data)

    expected = json.dumps(data, separators=(",", ":"))
    assert latest.read_text() == expected and versioned.read_text() == expected


def test_the_committed_run_compacts_and_is_admitted(tmp_path):
    """The real committed run, through the real writer, read back equal, admitted by the guard."""
    shown = subprocess.run(["git", "show", "HEAD:" + str(rar.RUN_OUTPUT_LATEST_PATH)],
                           cwd=REPO, capture_output=True, timeout=120)
    if shown.returncode != 0:
        pytest.skip("no run_output_latest.json at HEAD: {}".format(shown.stderr[:200]))
    data = json.loads(shown.stdout)
    out = tmp_path / "run_output_latest.json"
    out.write_text(rar.dump_run_output(data))

    assert json.loads(out.read_text()) == data
    assert os.path.getsize(out) < len(shown.stdout) or b"\n" not in shown.stdout
    assert prc._files_over_push_limit([str(out)]) == []


def test_the_save_json_path_sim_runner_takes_is_compact(tmp_path, monkeypatch):
    """`sim_runner` runs `tools.run_annual_report --save-json <out>` and byte-copies <out> onto
    run_output_latest.json, so THIS write is the one that publishes. MUTATION: restore
    `json.dumps(data, indent=2)` in `main` -> fails."""
    data = {"years": [], "bills": [{"a": 1}]}
    out = tmp_path / "run_output_x.json"
    monkeypatch.setenv("SIM_FAST_MODE", "1")  # `--fast` writes it; this restores it after
    monkeypatch.setattr(rar, "_git_commit_hash", lambda: "abc1234")
    monkeypatch.setattr(rar, "run_phase4c_on_phase2b", lambda report_end=None: {})
    monkeypatch.setattr(rar, "extract_report_data", lambda raw: data)
    monkeypatch.setattr(rar, "reconcile_and_stamp", lambda d, **kw: d)
    monkeypatch.setattr(rar, "generate_annual_report", lambda d: "report")
    monkeypatch.setattr("sys.argv", ["run_annual_report", "--fast", "--save-json", str(out),
                                     "--output", str(tmp_path / "r.md")])

    rar.main()

    assert out.read_text() == json.dumps(data, separators=(",", ":"))
