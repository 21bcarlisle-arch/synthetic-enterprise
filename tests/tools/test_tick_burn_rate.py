"""A turn's cost, per kind and model, from Claude Code's own transcripts."""
from __future__ import annotations

import json
import os
import time

from tools import tick_burn_rate as B


def _session(path, opening, model, usage):
    rows = [{"type": "user", "timestamp": "2026-09-27T10:00:00Z", "message": {"content": opening}},
            {"type": "assistant", "message": {"model": model, "usage": usage}},
            {"type": "assistant", "message": {"model": "<synthetic>", "usage": {"input_tokens": 999}}}]
    path.write_text("\n".join(json.dumps(r) for r in rows))


def test_every_kind_is_read_and_priced_per_model(tmp_path):
    d = tmp_path / "proj"
    d.mkdir()
    u = {"input_tokens": 1000, "output_tokens": 1000, "cache_read_input_tokens": 1_000_000,
         "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 1000}}
    _session(d / "a.jsonl", "You are the autonomous worker, woken by a scheduled tick ...", "claude-opus-5", u)
    _session(d / "b.jsonl", "You are the autonomous worker, woken by a scheduled tick ...", "claude-opus-5-5", u)
    _session(d / "c.jsonl", "Something no seat writes", "claude-opus-5-5", u)
    rows = {(r["kind"], r["model"]): r for r in B.table(B.turns(7, root=tmp_path), 7)}
    # A synthetic placeholder is never counted as a model, and an unknown opening is kept as `other`.
    assert set(rows) == {("worker_tick", "claude-opus-5"), ("worker_tick", "claude-opus-5-5"),
                         ("other", "claude-opus-5-5")}, rows
    # Priced at each model's own list: 5 = 1000*5 + 1000*25 + 1000*10 + 1e6*0.50 per M = $0.54;
    # 5.5 = 1000*4 + 1000*20 + 1000*8 + 1e6*0.20 per M = $0.232. The two must not be priced alike.
    assert rows[("worker_tick", "claude-opus-5")]["median_weighted_usd"] == 0.54
    assert rows[("worker_tick", "claude-opus-5-5")]["median_weighted_usd"] == 0.232
    assert rows[("worker_tick", "claude-opus-5")]["median_fresh_tokens"] == 3000


def test_an_old_session_is_outside_the_window(tmp_path):
    d = tmp_path / "proj"
    d.mkdir()
    f = d / "old.jsonl"
    _session(f, "You hold the DELIVERY SEAT on this project", "claude-opus-5", {"input_tokens": 1})
    old = time.time() - 30 * 86400
    os.utime(f, (old, old))
    assert B.turns(7, root=tmp_path) == []
    assert "nothing measured" in B.render(7, root=tmp_path)


def test_the_friday_review_carries_the_burn_and_monday_does_not():
    from datetime import date

    from background import weekly_rhythm as W
    friday = W._step_body(W.FRIDAY_STEP, date(2026, 10, 2), [])
    monday = W._step_body(W.MONDAY_STEP, date(2026, 9, 28), [])
    assert "## Burn per kind of turn, this week" in friday
    assert "enact them unless" not in monday and "Burn per kind" not in monday
    assert "Propose, then enact unless the director disagrees" in friday


def _turn_with(path, opening, landed_line):
    rows = [{"type": "user", "message": {"content": opening}},
            {"type": "assistant", "message": {"model": "claude-opus-5-5", "usage": {"input_tokens": 1}}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "content": landed_line}]}}]
    path.write_text("\n".join(json.dumps(r) for r in rows))


def test_landing_is_read_from_tool_results_and_split_by_the_prompt_the_turn_received(tmp_path):
    """The before/after the director asked for: a turn's arm is the wording it actually received.
    Both arms and both outcomes are exercised, so a split that lumped everything into one arm, or a
    detector that called every turn landed, fails."""
    d = tmp_path / "proj"
    d.mkdir()
    base = "You are the autonomous worker, woken by a scheduled tick ... "
    _turn_with(d / "o1.jsonl", base + "then STOP and exit cleanly", "[surgical-land] landed abc1234 (2 path(s))")
    _turn_with(d / "o2.jsonl", base + "then STOP and exit cleanly", "REFUSED: nothing to land")
    _turn_with(d / "n1.jsonl", base + "via tree_lock, and exit.", "[surgical-land] landed def5678 (1 path(s))")
    rows = B.turns(7, root=tmp_path)
    tick = next(e for e in B.change_effects(rows) if e["kind"] == "worker_tick")
    assert (tick["old_turns"], tick["old_landed_pct"]) == (2, 50), tick
    assert (tick["new_turns"], tick["new_landed_pct"]) == (1, 100), tick
    # The landing line in the PROMPT is not a landing: only tool results count.
    _turn_with(d / "o3.jsonl", base + "then STOP and exit cleanly [surgical-land] landed 0000000", "nothing")
    tick = next(e for e in B.change_effects(B.turns(7, root=tmp_path)) if e["kind"] == "worker_tick")
    assert (tick["old_turns"], tick["old_landed_pct"]) == (3, 33), tick


def test_one_message_split_across_block_rows_is_counted_once_and_its_advisor_call_is_priced(tmp_path):
    """Fires on the ~2.15x overcount (summing every block row of one message) and on an advisor
    call left unpriced, which would make the advisor trial read cheaper than it is."""
    d = tmp_path / "proj"
    d.mkdir()
    adv = {"type": "advisor_message", "model": "claude-opus-5-5", "input_tokens": 10_000,
           "output_tokens": 100, "cache_read_input_tokens": 0}
    u = {"input_tokens": 1000, "output_tokens": 1000, "cache_read_input_tokens": 0,
         "iterations": [{"type": "message", "input_tokens": 1000}, adv]}
    plain = {"input_tokens": 1000, "output_tokens": 0}
    rows = [{"type": "user", "timestamp": "2026-10-12T10:00:00Z", "message": {"content": "x"}}]
    rows += [{"type": "assistant", "message": {"id": "m1", "model": "claude-sonnet-5", "usage": u}}] * 3
    rows += [{"type": "assistant", "message": {"id": "m2", "model": "claude-sonnet-5", "usage": plain}}] * 2
    (d / "a.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    t = B.read_turn(d / "a.jsonl")
    assert t["input"] == 2000 and t["advisor_calls"] == 1, t
    # Sonnet 5: 2000*2 + 1000*10 = $0.014; the Opus 5.5 advisor: 10000*4 + 100*20 = $0.042.
    assert round(t["weighted_usd"], 6) == 0.056, t


def test_the_points_conversion_counts_subagents_and_sessions_started_before_the_window(tmp_path):
    """Fires on the first calibration's two misses: a subagent transcript, and a session whose first
    row predates the window but whose messages fall inside it."""
    d = tmp_path / "proj"
    (d / "sess" / "subagents").mkdir(parents=True)
    msg = lambda i, ts: {"type": "assistant", "timestamp": ts,  # noqa: E731
                         "message": {"id": i, "model": "claude-opus-5-5",
                                     "usage": {"input_tokens": 0, "output_tokens": 1_000_000}}}
    (d / "a.jsonl").write_text("\n".join(json.dumps(r) for r in (
        msg("early", "2026-10-12T10:00:00Z"), msg("m1", "2026-10-12T14:00:00Z"),
        msg("m1", "2026-10-12T14:00:01Z"))))
    (d / "sess" / "subagents" / "x.jsonl").write_text(json.dumps(msg("s1", "2026-10-12T15:00:00Z")))
    # Opus 5.5 output is USD 20 per million: m1 and s1 count once each, the early message not at all.
    assert B.weighted_usd_between("2026-10-12T13:00", "2026-10-13T07:10", tmp_path) == 40.0
    pair = (("2026-10-12T13:00", 40.0), ("2026-10-13T07:10", 42.0))
    assert B.usd_per_point(pair, tmp_path, since="") == 20.0
    assert B.usd_per_point((("2026-10-12T13:00", 40.0),), tmp_path, since="") is None
    # A reading from before the tier change is the old tier's and never fits the new one.
    assert B.usd_per_point(pair, tmp_path, since="2026-10-12T14:00") is None
