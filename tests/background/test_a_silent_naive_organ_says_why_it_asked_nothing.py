"""The naive organ wrote nothing from 2026-11-02T11:30Z, with its daemon alive. Run in-process on
2026-11-03 it fired 11 triggers and every one was debounced by an `open` question asked in July or
August that nobody had answered (104 open, newest 2026-08-10). Silence from a backlog could not be
told apart from the twelve-week fault, because nothing recorded why a cycle wrote nothing.

Each cycle now overwrites `.naive_organ_last_cycle.json` beside the log with its tally. This test
first shows a cycle on today's LATEST.md CAN ask, then that the re-run refuses and names why.
"""
import json

from background import naive_organ as organ


def _cycle(tmp_path, monkeypatch, log):
    # Only the real LATEST.md is read; every other surface is absent and the commit clock is now.
    for name in ("RUN_HISTORY_PATH", "RUN_INSIGHTS_PATH", "AGENT_STATUS_PATH", "IDLE_COUNTER_PATH",
                 "MATURITY_MAP_PATH"):
        monkeypatch.setattr(organ, name, tmp_path / "absent")
    monkeypatch.setattr(organ, "_last_commit_epoch", organ.time.time)
    monkeypatch.setattr(organ.subprocess, "run", lambda *a, **k: type("R", (), {"stdout": ""})())
    written = organ.run_organ_cycle(invoke_fn=lambda prompt: "Which run shows it?", log_path=log,
                                    max_new=None)
    return written, json.loads(organ.last_cycle_path(log).read_text())


def test_a_cycle_on_todays_latest_can_ask_and_a_rerun_names_why_it_asks_nothing(tmp_path,
                                                                                monkeypatch):
    log = tmp_path / "naive_organ_log.jsonl"

    first, tally = _cycle(tmp_path, monkeypatch, log)
    assert tally["asked"] >= 1, tally
    assert [r for r in first if r["verdict"] == "open"]
    assert tally["asked"] + tally["declined"] == len(first)

    second, tally = _cycle(tmp_path, monkeypatch, log)
    assert second == []
    assert tally["fired"] >= 1 and tally["asked"] == 0, tally
    assert tally["already_open"] + tally["already_declined"] == tally["fired"], tally
    assert tally["open_backlog"] == len(organ.open_questions(log_path=log))
    assert tally["oldest_open_asked_at"] is not None
