"""The one work system's store and pick (background/work_items.py), against decision map D2 and D6.

Each property comes from the decision map, not from reading the implementation.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from background import work_items as wi

NOW = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)
SHARES = {"correctness": 0.42, "supplier_feature": 0.18, "world_feature": 0.15,
          "harness": 0.15, "knowledge": 0.10}


def item(id_, **kw):
    base = {"id": id_, "title": id_, "lane": "supplier", "kind": "correctness",
            "class": "standard", "severity": "LATENT", "source": "finding",
            "evidence": [f"docs/staging/{id_}.md"], "decider": "machine", "state": "open",
            "opened_at": "2026-11-01T00:00:00+00:00", "blocked_by": []}
    base.update(kw)
    return base


def test_the_shape_refuses_each_missing_field_and_each_state_without_its_reason():
    assert wi.validate(item("a")) == []
    for field in wi.REQUIRED:
        assert f"missing {field}" in wi.validate({**item("a"), field: None})
    assert wi.validate(item("a", state="done"))
    assert wi.validate(item("a", state="parked"))
    assert wi.validate(item("a", state="obsolete"))
    assert wi.validate(item("a", state="chosen"))
    assert wi.validate(item("a", **{"class": "dated"}))
    assert wi.validate(item("Not_A_Slug"))


def test_an_item_round_trips_through_its_file(tmp_path):
    original = item("round-trip", parked=None, director_rank=3)
    path = wi.write_item(original, tmp_path)
    assert path.name == "round-trip.yaml"
    assert wi.read_item(path) == original
    with pytest.raises(ValueError, match="refused"):
        wi.write_item(item("bad", lane="neither"), tmp_path)


def test_every_branch_of_the_pick_can_be_taken():
    """The partition control: a pick that only ever rests, or only ever expedites, fails here."""
    expedite = wi.next_item([item("x", **{"class": "stop_the_line"}), item("y")], SHARES, now=NOW)
    ranked = wi.next_item([item("y")], SHARES, now=NOW)
    rest = wi.next_item([item("y", state="done", done_evidence="abc")], SHARES, now=NOW)
    wip = wi.next_item([item("y", state="chosen", chosen_by="s")], SHARES, now=NOW, wip_limit=1)
    assert expedite.item["id"] == "x" and expedite.reason.startswith("stop the line")
    assert ranked.item["id"] == "y" and ranked.reason.startswith("row correctness")
    assert rest.item is None and rest.reason.startswith("rest")
    assert wip.item is None and wip.reason.startswith("WIP limit")


def test_stop_the_line_holds_wip_one_and_lets_the_rows_run_beside_it():
    items = [item("running", **{"class": "stop_the_line"}, state="chosen", chosen_by="s"),
             item("waiting", **{"class": "stop_the_line"}), item("ordinary")]
    assert wi.next_item(items, SHARES, now=NOW).item["id"] == "ordinary"


def test_a_blocking_item_stops_feature_work_in_its_own_lane_only():
    items = [item("blocker", severity="BLOCKING", state="chosen", chosen_by="s"),
             item("supplier-feature", kind="feature"),
             item("world-feature", kind="feature", lane="world")]
    assert wi.next_item(items, SHARES, now=NOW).item["id"] == "world-feature"


def test_the_row_furthest_below_its_share_is_drawn():
    landed = [item(f"c{n}", state="done", done_evidence="x", closed_at="2026-11-18T00:00:00+00:00")
              for n in range(5)]
    waiting = [item("more-correctness"), item("a-feature", kind="feature")]
    # Nothing landed: correctness is the largest share, so furthest below.
    assert wi.next_item(waiting, SHARES, now=NOW).item["id"] == "more-correctness"
    # Five correctness items landed this week and nothing else: correctness is over its share.
    assert wi.next_item(landed + waiting, SHARES, now=NOW).item["id"] == "a-feature"
    # Landings from last week do not count against this week's share.
    old = [{**i, "closed_at": "2026-11-10T00:00:00+00:00"} for i in landed]
    assert wi.next_item(old + waiting, SHARES, now=NOW).item["id"] == "more-correctness"


def test_within_a_row_his_rank_then_date_then_severity_then_age():
    young_blocking = item("young-blocking", severity="BLOCKING", opened_at="2026-11-19T00:00:00+00:00")
    old_latent = item("old-latent", opened_at="2026-10-01T00:00:00+00:00")
    ranked = item("ranked", severity="RECORDED", director_rank=1)
    dated = item("dated", severity="RECORDED", **{"class": "dated"}, due="2026-11-21")
    assert wi.next_item([old_latent, young_blocking], SHARES, now=NOW).item["id"] == "young-blocking"
    assert wi.next_item([old_latent, item("older", opened_at="2026-09-01T00:00:00+00:00")],
                        SHARES, now=NOW).item["id"] == "older"
    assert wi.next_item([young_blocking, dated], SHARES, now=NOW).item["id"] == "dated"
    assert wi.next_item([young_blocking, dated, ranked], SHARES, now=NOW).item["id"] == "ranked"


def test_eligibility_parked_blocked_and_his_items():
    reopened = item("reopened", state="parked", parked={"reason": "r", "revisit": "2026-11-19"})
    still_parked = item("still", state="parked", parked={"reason": "r", "revisit": "2026-12-01"})
    blocked = item("blocked", blocked_by=["prereq"])
    his = item("his", decider="director")
    assert wi.next_item([still_parked, blocked, his], SHARES, now=NOW).item is None
    assert wi.next_item([still_parked, reopened], SHARES, now=NOW).item["id"] == "reopened"
    done_prereq = item("prereq", state="done", done_evidence="x")
    assert wi.next_item([blocked, done_prereq], SHARES, now=NOW).item["id"] == "blocked"


def test_a_row_missing_from_the_share_table_is_refused_by_name():
    pick = wi.next_item([item("k", kind="knowledge")], {"correctness": 1.0}, now=NOW)
    assert pick.item is None and "knowledge" in pick.reason


FINDING = """**Severity:** {sev} · **Lane:** {lane} · **Epoch:** unassigned · **Atom:** `{atom}`

# {title}

body
"""


def _staging(tmp_path, docs):
    root = tmp_path / "docs" / "staging"
    root.mkdir(parents=True)
    for name, text in docs.items():
        (root / name).write_text(text, encoding="utf-8")
    return root


def test_each_classified_finding_becomes_one_item_and_the_rest_are_refused_by_name(tmp_path):
    root = _staging(tmp_path, {
        "SEAT_FINDING_A_WORLD_THING_2026-11-18.md":
            FINDING.format(sev="BLOCKING", lane="W2_customer_generator", atom="W2_30_x", title="World"),
        "SEAT_FINDING_A_HARNESS_THING_2026-11-19.md":
            FINDING.format(sev="LATENT", lane="H_harness", atom="unminted", title="Harness"),
        "SEAT_FINDING_NO_HEADER_2026-11-19.md": "# nothing\n",
        "run_complete_123.md": "doorbell",
    })
    items, refused = wi.items_from_staging(root)
    by_id = {i["id"]: i for i in items}
    assert set(by_id) == {"seat-finding-a-world-thing", "seat-finding-a-harness-thing"}
    world = by_id["seat-finding-a-world-thing"]
    assert (world["lane"], world["kind"], world["severity"], world["atom"]) == (
        "world", "correctness", "BLOCKING", "W2_30_x")
    assert world["evidence"] == ["docs/staging/SEAT_FINDING_A_WORLD_THING_2026-11-18.md"]
    assert world["opened_at"].startswith("2026-11-18")
    harness = by_id["seat-finding-a-harness-thing"]
    assert (harness["lane"], harness["kind"], harness["atom"]) == ("building", "harness", None)
    assert all(wi.validate(i) == [] for i in items)
    assert len(refused) == 1 and "SEAT_FINDING_NO_HEADER" in refused[0]


def test_every_finding_lane_has_a_side():
    from background.finding_severity import LANES
    assert set(LANES) == set(wi.FINDING_LANE_TO_SIDE)
    assert set(wi.FINDING_LANE_TO_SIDE.values()) <= set(wi.LANES)


def test_a_written_item_shadows_the_derived_one(tmp_path):
    root = _staging(tmp_path, {"SEAT_FINDING_X_2026-11-18.md":
                               FINDING.format(sev="LATENT", lane="D_billing_metering", atom="unminted",
                                              title="X")})
    items_dir = tmp_path / "items"
    wi.write_item(item("seat-finding-x", state="obsolete", obsolete="fixed elsewhere"), items_dir)
    merged = wi.all_items(root, items_dir)
    assert [i["state"] for i in merged] == ["obsolete"]


def test_shadow_logs_beside_the_ladder_and_off_logs_nothing(tmp_path):
    root = _staging(tmp_path, {"SEAT_FINDING_X_2026-11-18.md":
                               FINDING.format(sev="LATENT", lane="D_billing_metering", atom="unminted",
                                              title="X")})
    flag = tmp_path / "cutover.yaml"
    log = tmp_path / "shadow.jsonl"
    common = dict(log_path=log, cutover_path=flag, staging_root=root,
                  priority_path=wi.PRIORITY_ORDER, items_dir=tmp_path / "items", now=NOW)

    flag.write_text("staging_findings: off\n")
    assert wi.shadow_record("ladder", **common) is None and not log.exists()
    flag.write_text("staging_findings: on\n")  # not a mode yet: reads off
    assert wi.shadow_record("ladder", **common) is None

    flag.write_text("staging_findings: shadow\n")
    rec = wi.shadow_record("drew SEAT_FINDING_X_2026-11-18.md", **common)
    assert rec["pick"] == "seat-finding-x" and rec["ladder_names_pick"] is True
    assert rec["ladder_names_any_finding"] is True
    rec = wi.shadow_record("drew something else", **common)
    assert rec["ladder_names_pick"] is False and rec["ladder_names_any_finding"] is False
    assert [json.loads(line)["pick"] for line in log.read_text().splitlines()] == ["seat-finding-x"] * 2
    report = wi.compare(log)
    assert "the ladder named the new pick's document in 1 of 2" in report
    assert "the ladder named any staging finding in 1 of 2" in report


def test_the_live_share_table_covers_every_row_and_sums_to_one():
    shares = wi.load_shares()
    assert set(shares) == {"correctness", "supplier_feature", "world_feature", "harness", "knowledge"}
    assert abs(sum(shares.values()) - 1.0) < 1e-9


def test_the_supervisor_draw_is_shadowed_and_a_failing_shadow_never_changes_it(monkeypatch):
    from background import supervisor
    seen = []
    monkeypatch.setattr(supervisor, "_self_refill_draw_unshadowed", lambda: "the ladder's draw")
    monkeypatch.setattr(wi, "shadow_record", lambda drawn: seen.append(drawn))
    assert supervisor._self_refill_draw() == "the ladder's draw"
    assert seen == ["the ladder's draw"]

    def boom(drawn):
        raise RuntimeError("shadow broke")
    monkeypatch.setattr(wi, "shadow_record", boom)
    assert supervisor._self_refill_draw() == "the ladder's draw"


def test_a_test_process_cannot_write_the_live_shadow_log(tmp_path):
    from background.live_ledger_guard import LiveLedgerWriteUnderTest
    flag = tmp_path / "cutover.yaml"
    flag.write_text("staging_findings: shadow\n")
    with pytest.raises(LiveLedgerWriteUnderTest):
        wi.shadow_record("ladder", cutover_path=flag)


def _share_table(tmp_path, body):
    path = tmp_path / "priority_order.yaml"
    path.write_text(body)
    return path


def test_a_share_table_refuses_a_row_at_zero(tmp_path):
    """Defect named: a lane switched off by a share of zero, which the 21 Nov ruling forbids."""
    path = _share_table(tmp_path, "weekly_split:\n  floor: 5\n  shares: {correctness: 60, harness: 40, knowledge: 0}\n")
    with pytest.raises(ValueError, match="knowledge=0"):
        wi.load_shares(path)


def test_a_share_table_refuses_a_row_below_its_floor_and_a_table_with_no_floor(tmp_path):
    """Defect named: a floor that is stated but not enforced, or silently absent."""
    below = _share_table(tmp_path, "weekly_split:\n  floor: 5\n  shares: {correctness: 97, knowledge: 3}\n")
    with pytest.raises(ValueError, match="below the 5.0% floor"):
        wi.load_shares(below)
    none = _share_table(tmp_path, "weekly_split:\n  shares: {correctness: 90, knowledge: 10}\n")
    with pytest.raises(ValueError, match="states no floor"):
        wi.load_shares(none)
    ok = _share_table(tmp_path, "weekly_split:\n  floor: 5\n  shares: {correctness: 95, knowledge: 5}\n")
    assert wi.load_shares(ok) == {"correctness": 0.95, "knowledge": 0.05}
