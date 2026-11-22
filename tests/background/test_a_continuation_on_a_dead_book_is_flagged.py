"""A continuation embargoed on a book that died is flagged by name, and becomes drawable to re-arm.

The defect (22 Nov, twice in one day): `d48-grade-the-first-book-built-with-the-blend-at-0-5` said
`DO NOT DRAW BEFORE …/run_output_35316f9395_…json EXISTS`; the book died in extract_report_data and
the row would have waited unoffered until its window closed. These drive the REAL `run_simulation`
failure branch. Remove the `flag_continuations_on_unwritten_run` call from sim_runner and
`test_a_failed_run_flags_the_row_waiting_on_its_book` goes red.
"""
from __future__ import annotations

import json
import subprocess

import pytest

from background import delivery_lane, seat_continuation, sim_runner


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "sim-runner-log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "update_agent_status", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "record_run_outcome", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "imports_off_commit_at_launch",
                        lambda head, root: {"paths": []})
    store = tmp_path / "continuations.json"
    monkeypatch.setattr(seat_continuation, "STORE", store)
    return tmp_path, store


def _row(rid, book):
    return {"id": rid, "what": f"DO NOT DRAW BEFORE {book} EXISTS. Then grade it.",
            "why": "w", "done_means": "d", "written_at": 1.0}


def _child(store, *, writes: bool, rc: int):
    """A child run. When it starts, a seat hands off a grade on ITS book and another on some other."""
    real_run = subprocess.run

    def fake_run(cmd, **kwargs):
        if "--save-json" not in cmd:  # the store's own guard asks git where the shared tree is
            return real_run(cmd, **kwargs)
        book = cmd[cmd.index("--save-json") + 1]
        store.write_text(json.dumps([_row("waits-on-this-book", book),
                                     _row("waits-on-another", book.replace("abc1234", "fff9999"))]))
        if writes:
            open(book, "w").write("{}")
        return subprocess.CompletedProcess(cmd, rc, stdout="", stderr="KeyError: 'SYN-2016-144_3'\n")
    return fake_run


def _rows(store):
    return {r["id"]: r for r in json.loads(store.read_text())}


def test_a_failed_run_flags_the_row_waiting_on_its_book(runner, monkeypatch):
    tmp, store = runner
    monkeypatch.setattr(sim_runner.subprocess, "run", _child(store, writes=False, rc=1))
    assert sim_runner.run_simulation(head="abc1234", root=tmp) is False
    rows = _rows(store)
    flagged = rows["waits-on-this-book"]
    assert flagged["awaits_unwritten_run"]["path"].endswith(".json")
    assert "SYN-2016-144_3" in flagged["awaits_unwritten_run"]["reason"]
    assert flagged["what"].startswith("THE RUN THIS WAITS ON ENDED WITHOUT WRITING")
    # The flag is what lifts the embargo: the row is drawable now, to be re-armed.
    assert delivery_lane.awaited_paths(flagged) == []
    # A row on another book is untouched and still embargoed -- the branch is not "flag everything".
    other = rows["waits-on-another"]
    assert "awaits_unwritten_run" not in other
    assert delivery_lane.awaited_paths(other) != []
    log = (tmp / "sim-runner-log.md").read_text()
    assert "CONTINUATION ORPHANED -- waits-on-this-book" in log


def test_a_successful_run_flags_nothing(runner, monkeypatch):
    tmp, store = runner
    monkeypatch.setattr(sim_runner.subprocess, "run", _child(store, writes=True, rc=0))
    monkeypatch.setattr(sim_runner, "_post_success", lambda *a, **k: None, raising=False)
    try:
        sim_runner.run_simulation(head="abc1234", root=tmp)
    except Exception:  # noqa: BLE001 -- the success tail is not this test's subject
        pass
    assert all("awaits_unwritten_run" not in r for r in _rows(store).values())


def test_the_embargo_holds_before_the_flag_and_a_placeholder_awaits_nothing(tmp_path):
    book = tmp_path / "run_output_abc1234_20261122T000000Z.json"
    assert delivery_lane.awaited_paths(_row("x", book)) == [str(book)]
    placeholder = _row("y", "/home/rich/synthetic-enterprise/docs/reports/<name>")
    assert delivery_lane.awaited_paths(placeholder) == []
