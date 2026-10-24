"""tools/work_cost_estimate.py -- each test names the defect it exists to catch."""
from __future__ import annotations

import json
import time

from tools import work_cost_estimate as w


def _utc(ts: str) -> float:
    return time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M")) - time.timezone


def test_a_build_that_also_writes_its_record_is_priced_as_the_build_not_the_record():
    assert w.classify(["docs/staging/records/X_PREREG.md", "company/billing/x.py"]) == "supplier_build"
    assert w.classify(["site/knowledge/x.html", "simulation/y.py"]) == "world_build"
    assert w.classify(["site/knowledge/x.html", "site/index.html"]) == "knowledge_page"
    assert w.classify(["docs/design/x.md"]) == w.OTHER
    assert w.classify([]) == w.OTHER


def test_an_idle_atom_scoped_only_to_docs_is_priced_by_its_lane_not_as_the_cheapest_class():
    world = {"lane": "W1_market_weather", "file_scope": ["docs/design"]}
    assert w.atom_class(world) == "world_build"
    assert w.atom_class({"lane": "C_customer_ops", "file_scope": ["docs/design"]}) == "supplier_build"
    # scope that names code wins over the lane
    assert w.atom_class({"lane": "W2_customer_generator", "file_scope": ["company/x.py"]}) == "supplier_build"


def test_the_week_resets_on_monday_morning_and_not_a_minute_either_side():
    assert time.gmtime(w.last_reset(_utc("2026-10-26T01:59"))).tm_mday == 19
    assert time.gmtime(w.last_reset(_utc("2026-10-26T02:00"))).tm_mday == 26
    assert time.gmtime(w.last_reset(_utc("2026-10-24T19:00"))).tm_mday == 19


def _session(tmp_path, rows, sub_rows=()):
    root = tmp_path / "projects"
    (root / "p").mkdir(parents=True)
    main = root / "p" / "s1.jsonl"
    main.write_text("\n".join(json.dumps(r) for r in rows))
    if sub_rows:
        (root / "p" / "s1" / "subagents").mkdir(parents=True)
        (root / "p" / "s1" / "subagents" / "a.jsonl").write_text("\n".join(json.dumps(r) for r in sub_rows))
    return main


def _assistant(mid, out_tokens):
    return {"type": "assistant", "message": {"id": mid, "model": "claude-opus-5-5",
                                             "usage": {"output_tokens": out_tokens}}}


def test_a_prompt_quoting_the_landing_line_is_not_a_landing_and_a_tool_result_is(tmp_path):
    quoted = {"type": "user", "message": {"content": "earlier: [surgical-land] landed abcdef1"}}
    result = {"type": "user", "message": {"content": [
        {"type": "tool_result", "content": "[surgical-land] landed 1234567 (1 path(s))"}]}}
    path = _session(tmp_path, [quoted, result])
    assert w._session_cost_and_landings(path)[1] == ["1234567"]


def test_a_subagent_is_charged_to_its_session_and_a_repeated_message_row_is_charged_once(tmp_path):
    path = _session(tmp_path, [_assistant("m1", 1_000_000), _assistant("m1", 1_000_000)],
                    [_assistant("m2", 1_000_000)])
    usd, _ = w._session_cost_and_landings(path)
    one = w.burn._priced({"output_tokens": 1_000_000}, "claude-opus-5-5")
    assert one > 0 and abs(usd - 2 * one) < 1e-9


def test_spend_that_landed_nothing_is_charged_to_the_work_that_did():
    rows = [{"class": "harness", "usd": 10.0}] * 3
    assert w.fit(rows, 10.0)["harness"]["median"] == 1.0
    assert w.fit(rows, 10.0, overhead=1.5)["harness"]["median"] == 1.5


def test_a_class_with_few_sessions_shows_its_whole_spread_and_says_it_is_thin():
    few = w.fit([{"class": "site_page", "usd": u} for u in (1.0, 5.0, 9.0)], 1.0)["site_page"]
    assert few["thin"] and (few["low"], few["high"]) == (1.0, 9.0)
    many = w.fit([{"class": "site_page", "usd": float(u)} for u in range(1, 21)], 1.0)["site_page"]
    assert not many["thin"] and 1.0 < many["low"] < many["high"] < 20.0


def _wire(monkeypatch, tmp_path, reading):
    monkeypatch.setattr(w.burn, "usd_per_point", lambda: 10.0)
    monkeypatch.setattr(w.burn, "POINT_READINGS", (reading,))
    monkeypatch.setattr(w.burn, "weighted_usd_between", lambda a, b: 50.0)
    monkeypatch.setattr(w, "landed_sessions", lambda d, n: ([{"class": "world_build", "usd": 4.0, "shas": ["a"]}], 8.0))
    monkeypatch.setattr(w, "level_steps_since", lambda c: 1)
    monkeypatch.setattr(w, "open_atom_steps", lambda: {"world_build": 3})
    monkeypatch.setattr(w, "ADVISOR_DIR", tmp_path)


def test_a_reading_from_before_the_reset_is_never_read_as_this_weeks_use(monkeypatch, tmp_path):
    now = _utc("2026-10-24T19:00")
    _wire(monkeypatch, tmp_path, ("2026-10-24T12:47", 27.0))
    fresh = w.forecast(14, now)
    _wire(monkeypatch, tmp_path, ("2026-10-18T12:00", 90.0))
    stale = w.forecast(14, now)
    # both sides of the partition are reachable
    assert fresh["week_used_points"] == 27.0 + 5.0 and stale["week_used_points"] is None
    assert "not known" in w.render(14, now)
    # overhead 8/4 = 2: one world session of 4 USD is 0.8 points; 3 open steps, 1 session per step
    assert fresh["atom_backlog_points"] == (3 * 0.8, 3 * 0.8)


def test_no_point_conversion_refuses_with_its_reason_rather_than_pricing_at_zero(monkeypatch):
    monkeypatch.setattr(w.burn, "usd_per_point", lambda: None)
    assert w.render().startswith("NOT ESTIMATED -- no point conversion")
