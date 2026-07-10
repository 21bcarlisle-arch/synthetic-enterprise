"""Tests for tools/test_execution_metric.py -- the cumulative tests EXECUTED
metric (2026-07-10, director page comment on /project/: "Don't we want
cumulative tests run, not the growth in the standard test set"). Forward-only
instrumentation: no historical log exists, so nothing here fabricates a past
total -- these tests use tmp_path log files throughout, never the real
docs/observability/test_execution_log.jsonl.
"""
import json

from tools.test_execution_metric import (
    count_executed_tests,
    record_execution,
    cumulative_tests_executed,
)


def test_count_executed_tests_sums_all_outcome_kinds():
    stats = {
        "passed": [1, 2, 3],
        "failed": [1],
        "error": [],
        "skipped": [1, 2],
        "xfailed": [1],
        "xpassed": [],
    }
    assert count_executed_tests(stats) == 3 + 1 + 0 + 2 + 1 + 0


def test_count_executed_tests_ignores_unrelated_stats_keys():
    stats = {"passed": [1], "deselected": [1, 2, 3, 4, 5]}
    assert count_executed_tests(stats) == 1


def test_count_executed_tests_empty_stats_returns_zero():
    assert count_executed_tests({}) == 0


def test_record_execution_writes_one_line(tmp_path):
    log_path = tmp_path / "log.jsonl"
    record_execution({"passed": [1, 2, 3]}, log_path=log_path)
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["test_count"] == 3
    assert "timestamp" in rec


def test_record_execution_noop_on_zero_tests(tmp_path):
    log_path = tmp_path / "log.jsonl"
    record_execution({}, log_path=log_path)
    assert not log_path.exists()


def test_record_execution_appends_across_multiple_sessions(tmp_path):
    log_path = tmp_path / "log.jsonl"
    record_execution({"passed": [1, 2]}, log_path=log_path)
    record_execution({"passed": [1, 2, 3]}, log_path=log_path)
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 2


def test_cumulative_tests_executed_missing_log_returns_zero(tmp_path):
    result = cumulative_tests_executed(log_path=tmp_path / "nonexistent.jsonl")
    assert result == {"cumulative_total": 0, "since": None, "session_count": 0}


def test_cumulative_tests_executed_sums_across_sessions(tmp_path):
    log_path = tmp_path / "log.jsonl"
    record_execution({"passed": [1, 2]}, log_path=log_path)
    record_execution({"passed": [1, 2, 3, 4]}, log_path=log_path)
    result = cumulative_tests_executed(log_path=log_path)
    assert result["cumulative_total"] == 6
    assert result["session_count"] == 2
    assert result["since"] is not None


def test_cumulative_tests_executed_since_is_earliest_timestamp(tmp_path):
    log_path = tmp_path / "log.jsonl"
    log_path.write_text(
        json.dumps({"timestamp": "2026-07-10T10:00:00+00:00", "test_count": 5}) + "\n"
        + json.dumps({"timestamp": "2026-07-09T08:00:00+00:00", "test_count": 3}) + "\n"
    )
    result = cumulative_tests_executed(log_path=log_path)
    assert result["since"] == "2026-07-09T08:00:00+00:00"
    assert result["cumulative_total"] == 8


def test_cumulative_tests_executed_skips_malformed_lines(tmp_path):
    log_path = tmp_path / "log.jsonl"
    log_path.write_text(
        json.dumps({"timestamp": "2026-07-10T10:00:00+00:00", "test_count": 5}) + "\n"
        + "not valid json\n"
        + "\n"
    )
    result = cumulative_tests_executed(log_path=log_path)
    assert result["cumulative_total"] == 5
    assert result["session_count"] == 1
