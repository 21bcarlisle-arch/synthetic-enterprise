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

THE TWO READERS NEEDED OPPOSITE REPAIRS, and this file asserted the wrong one for the appender
until 2026-09-05, when a concurrent lane's fix for the same defect was merged. The scorecard is a
pure READER: it drops the bad line, keeps the rest, and publishes `unreadable_log_lines` so the
drop is stated on the surface. The appender is a WRITER, and skipping there is not the same act at
all -- the realistic torn line is the most recent write, which is TODAY'S own row, so skipping it
drops today out of `existing_dates`, the guard reports "not logged yet", and a re-run appends a
SECOND row for the same day. That is the exact duplicate the one-entry-per-day rule exists to
forbid, and `generate_track_record_scorecard` would grade both. So the appender fails CLOSED on
the day question and names its reason on stderr. Nothing is lost by refusing: the day's decision
is already on disk in `live_decisions_<date>.json` before this is ever called.

The integrity of the published track record beats its continuity. A record that stopped growing
behind a named, greppable refusal is honest; one that quietly gained a second row for a day is a
plausible number with a hole in it, which is the failure this project keeps paying for.

These are controls over the PROPERTY each disposition claims, not over today's answer, so they
stay honest if either reader is rewritten.
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

def test_a_torn_line_refuses_the_append_rather_than_risking_a_duplicate_day(tmp_path, capsys):
    """THE DEFECT was an unguarded parse that raised out of the appender. THE REPAIR IS NOT THE
    REFLEX. This test asserted the skip until 2026-09-05 and it was wrong: a torn line is a write
    killed mid-flight, so the likeliest one is today's own row, and skipping it is what MANUFACTURES
    the duplicate day. Refusing cannot -- see the module docstring for why nothing is lost by it.

    MUTATION: replace the `return False` with `continue` and the second row lands -- `len == 2`
    reds, which is the duplicate itself."""
    log = _log(tmp_path, json.dumps(_GOOD), '{"decision_run_at": "2026-09-0')

    assert rld.append_decision_log({"decision_run_at": "2026-09-05T00:00:00Z"}, log) is False

    assert len(log.read_text().splitlines()) == 2, "nothing may be appended past a line we cannot read"
    err = capsys.readouterr().err
    assert "REFUSING" in err and "2026-09-05" in err, (
        "a refusal that does not name its reason is how the refusal itself never gets corrected"
    )


def test_the_refusal_does_not_depend_on_which_day_is_being_appended(tmp_path):
    """The refusal is keyed to "the log cannot be read", NOT to the incoming day. A guard that
    only refused days it had already seen would let an unseen day through the same hole."""
    log = _log(tmp_path, json.dumps(_GOOD), "not json at all")

    assert rld.append_decision_log({"decision_run_at": "2026-09-01T09:00:00Z"}, log) is False
    assert rld.append_decision_log({"decision_run_at": "2027-01-01T09:00:00Z"}, log) is False
    assert len(log.read_text().splitlines()) == 2


def test_a_line_that_is_valid_json_but_not_a_record_refuses_too(tmp_path, capsys):
    """`json.loads` succeeds for `"abc"` and for `5`; the subscript after it is what raised.
    A guard written only around the parse would still have let this through -- and a line that
    parses but carries no date is exactly as unreadable, for the day question, as a torn one."""
    log = _log(tmp_path, json.dumps(_GOOD), '"abc"', "5", "[]", "{}")

    assert rld.append_decision_log({"decision_run_at": "2026-09-06T00:00:00Z"}, log) is False
    assert "REFUSING" in capsys.readouterr().err


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

    assert result["unreadable_log_lines"] == expected
    assert json.loads((tmp_path / "out.json").read_text())["unreadable_log_lines"] == expected


def test_the_clean_log_is_still_read_whole(tmp_path):
    """The control over the whole partition: a tolerant reader that silently dropped GOOD
    rows would pass every test above. Assert the undamaged case reaches full count."""
    log = _log(tmp_path, json.dumps(_GOOD),
               json.dumps({**_GOOD, "decision_run_at": "2026-09-02T00:00:00Z"}),
               json.dumps({**_GOOD, "decision_run_at": "2026-09-03T00:00:00Z"}))

    result = scorecard.generate(log_path=log, portfolio_path=tmp_path / "absent.json",
                                out_path=tmp_path / "out.json")

    assert result["log_entry_count"] == 3
    assert result["unreadable_log_lines"] == 0
    # THE CONTROL LEG FOR THE WHOLE APPENDER PARTITION. Every other appender test above asserts
    # `is False`, so an `append_decision_log` that refused unconditionally -- the failure mode a
    # fail-closed repair actually has -- would pass all of them. The undamaged log must still
    # refuse a REPEAT day and still accept a NEW one.
    assert rld.append_decision_log({"decision_run_at": "2026-09-03T18:00:00Z"}, log) is False
    assert rld.append_decision_log({"decision_run_at": "2026-09-04T09:00:00Z"}, log) is True
    assert len(log.read_text().splitlines()) == 4
