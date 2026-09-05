"""The defect each test here names: a JSONL carrier the self-clearing-alarm census
dispositioned `benign` on the strength of "the readers parse PER LINE, so a corrupt line costs
one entry and never the file" -- a claim that was verified for exactly ONE reader
(`notification_digest._read_queue`) and asserted of four others by family resemblance.

Opened 2026-09-05. It was false for both readers of `site/state/live_decisions_log.jsonl`, and
false in the expensive direction:

  * `run_live_decisions.append_decision_log` builds its once-per-day idempotency set with an
    unguarded `json.loads(line)["decision_run_at"]`. One torn line raised out of the APPENDER,
    so the day's decision was never logged -- and neither was any later day's, because the bad
    line stays on disk. A corrupt line cost the file, permanently, on the WRITE path.
  * `generate_track_record_scorecard._load_log` had the same unguarded parse, so one torn line
    blanked the entire published predicted-vs-realised scorecard (the publish cycle's
    `except Exception` logs it as "generation failed" and moves on). A line that parsed to a
    non-dict got further and raised AttributeError from the sort key instead.

These are controls over the PROPERTY the disposition claims -- "a corrupt line costs one entry,
never the file" -- not over today's answer, so they stay honest if either reader is rewritten.
"""
import json

import pytest

from tools import generate_track_record_scorecard as scorecard
from tools import run_live_decisions as rld

_GOOD = {"decision_run_at": "2026-09-01T00:00:00Z", "renewal_flags": [],
         "hedge_recommendation": "hold"}


def _log(tmp_path, *lines):
    p = tmp_path / "live_decisions_log.jsonl"
    p.write_text("".join(line + "\n" for line in lines))
    return p


# ── the appender ──────────────────────────────────────────────────────────────────────────

def test_a_torn_line_does_not_stop_the_decision_log_growing_forever(tmp_path):
    """THE DEFECT: one half-written row raised out of append_decision_log, so no decision was
    ever appended again. The append is what the whole track record is built from."""
    log = _log(tmp_path, json.dumps(_GOOD), '{"decision_run_at": "2026-09-0')

    assert rld.append_decision_log({"decision_run_at": "2026-09-05T00:00:00Z"}, log) is True

    written = log.read_text().splitlines()
    assert len(written) == 3, "the new decision must reach the file past the torn line"
    assert json.loads(written[-1])["decision_run_at"] == "2026-09-05T00:00:00Z"


def test_the_torn_line_costs_only_its_own_days_idempotency_and_no_others(tmp_path):
    """The skip must stay NARROW. Dropping the unreadable line must not drop the READABLE
    days with it -- if it did, every past day would re-append on the next run and the log
    would stop being one row per day, which is the property the guard exists to keep."""
    log = _log(tmp_path, json.dumps(_GOOD), "not json at all")

    # The day that IS readable in the log is still refused a second row.
    assert rld.append_decision_log({"decision_run_at": "2026-09-01T09:00:00Z"}, log) is False
    assert len(log.read_text().splitlines()) == 2


def test_a_line_that_is_valid_json_but_not_a_record_does_not_stop_the_appender(tmp_path):
    """`json.loads` succeeds for `"abc"` and for `5`; the subscript after it is what raised.
    A guard written only around the parse would still have let this through."""
    log = _log(tmp_path, json.dumps(_GOOD), '"abc"', "5", "[]", "{}")

    assert rld.append_decision_log({"decision_run_at": "2026-09-06T00:00:00Z"}, log) is True
    assert json.loads(log.read_text().splitlines()[-1])["decision_run_at"].startswith("2026-09-06")


# ── the published scorecard ───────────────────────────────────────────────────────────────

def test_a_torn_line_does_not_blank_the_published_scorecard(tmp_path):
    """THE DEFECT: one byte in the log removed the entire predicted-vs-realised record from
    the public Method page, and the publish cycle logged it as a generation failure."""
    log = _log(tmp_path, json.dumps(_GOOD), '{"decision_run_at": "2026-09-0')

    result = scorecard.generate(log_path=log, portfolio_path=tmp_path / "absent.json",
                                out_path=tmp_path / "out.json")

    assert result["log_entry_count"] == 1
    assert result["clock_started"] == "2026-09-01"


def test_a_non_dict_line_does_not_reach_the_sort_key(tmp_path):
    """`entries.sort(key=lambda e: e.get(...))` raised AttributeError for a bare JSON scalar:
    the shape where a method answers for something that is not the record at all."""
    log = _log(tmp_path, json.dumps(_GOOD), '"abc"', "5")

    result = scorecard.generate(log_path=log, portfolio_path=tmp_path / "absent.json",
                               out_path=tmp_path / "out.json")

    assert result["log_entry_count"] == 1


@pytest.mark.parametrize("bad, expected", [
    ([], 0),
    (['{"decision_run_at": "2026-09-0'], 1),
    (['"abc"', "5", "{"], 3),
])
def test_the_scorecard_publishes_how_many_lines_it_could_not_read(tmp_path, bad, expected):
    """A count dropped silently is fail-open on a PUBLISHED figure: every number on the
    scorecard would then be computed over a partial log with nothing saying so. The count
    rides on the artefact itself, and 0 must be a real answer and not merely the absence of
    the field -- otherwise a reader cannot tell a clean log from an unasked question."""
    log = _log(tmp_path, json.dumps(_GOOD), *bad)

    result = scorecard.generate(log_path=log, portfolio_path=tmp_path / "absent.json",
                                out_path=tmp_path / "out.json")

    assert result["log_lines_unreadable"] == expected
    assert json.loads((tmp_path / "out.json").read_text())["log_lines_unreadable"] == expected


def test_the_clean_log_is_still_read_whole(tmp_path):
    """The control over the whole partition: a tolerant reader that silently dropped GOOD
    rows would pass every test above. Assert the undamaged case reaches full count."""
    log = _log(tmp_path, json.dumps(_GOOD),
               json.dumps({**_GOOD, "decision_run_at": "2026-09-02T00:00:00Z"}),
               json.dumps({**_GOOD, "decision_run_at": "2026-09-03T00:00:00Z"}))

    result = scorecard.generate(log_path=log, portfolio_path=tmp_path / "absent.json",
                                out_path=tmp_path / "out.json")

    assert result["log_entry_count"] == 3
    assert result["log_lines_unreadable"] == 0
    assert rld.append_decision_log({"decision_run_at": "2026-09-03T18:00:00Z"}, log) is False
