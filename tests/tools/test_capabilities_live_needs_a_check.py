"""A capability with no linked test can never compute as Live on the Capabilities page.

Director, 24 Oct 2026 (DIRECTOR_STEER_CAPABILITIES_SHORTER_AND_ITS_GAPS_ARE_A_FIX_LIST): five
functions read Live beside "Nothing published yet shows how this is checked". A level is the map's
word; Live is a claim to a reader, and a claim with no check behind it is not Live (C1, H1).

WHAT EACH CONTROL WOULD CATCH:

  * `test_the_rule_takes_both_branches` -- the partition in one control: an at-target item WITH a
    cited test stays Live, the same item WITHOUT one computes as Building and says why. MUTATION:
    delete the demotion -> the uncited entry reads Live and this reds. MUTATION: demote every Live
    entry -> the cited one reads Building and this reds.
  * `test_the_published_feed_carries_no_live_function_without_a_check` -- the property on the real
    record, keyed to the property and not to today's five names.
  * `test_a_segment_the_curriculum_suspends_is_said_on_the_row` -- the business row says which
    segment is not served, read from the director's curriculum file. MUTATION: drop the
    `not_served` branch -> reds.
"""
from __future__ import annotations

from tools import capabilities_page_figures as figures
from tools import generate_capabilities_door as door

_TEST = "tests/sim/test_w2_6_sme_distress.py"
_AT_TARGET = {"X_cited": {"level_current": 3, "level_target": 3},
              "X_uncited": {"level_current": 3, "level_target": 3}}
_RECORDS = {"X_cited": {"evidence_entries": [_TEST]},
            "X_uncited": {"evidence_entries": ["docs/design/COUPLED_TRIAD_DESIGN.md"]}}


def test_the_rule_takes_both_branches():
    rows = door._entries([("cited", "a", ["X_cited"]), ("uncited", "b", ["X_uncited"])],
                         _AT_TARGET, {}, _RECORDS)
    by = {r["name"]: r for r in rows}
    assert by["cited"]["status"] == door.LIVE and by["cited"]["checks"]
    assert by["uncited"]["status"] == door.BUILDING and by["uncited"]["held_from_live"]
    html = figures._item(by["uncited"])
    assert "Shown as building" in html, "the page must say why it is not Live"


def test_the_published_feed_carries_no_live_function_without_a_check():
    feed = door.build()
    bare = [e["name"] for side in ("world", "supplier") for e in feed[side]["entries"]
            if e["status"] == door.LIVE and not e["checks"]]
    assert not bare, "Live with no linked test: {}".format(bare)


def test_a_segment_the_curriculum_suspends_is_said_on_the_row(monkeypatch):
    monkeypatch.setattr(door, "_served_segments", lambda: ("resi", "SME"))
    name = "Business customers that fail like businesses"
    row = door._entries([(name, "b", ["X_cited"])], _AT_TARGET, {}, _RECORDS)[0]
    assert row["not_served"] == ["I&C"]
    assert "I&amp;C accounts are suspended" in figures._item(row)


def test_the_specification_column_takes_all_three_branches_and_each_record_exists():
    """24 Oct: "Specification: not read" for sources the run reads every day. The column now says
    read / read for what the run uses / not read. MUTATION: drop the `used` branch from
    `render_golive` -> the Elexon row reads "not read" again and this reds."""
    seams = [dict(s, counterparty=s["who"], status="Planned") for s in door.GO_LIVE_SEAMS]
    rows = figures.render_golive({"seams": seams}).splitlines()
    assert any("spec-read" in r for r in rows)
    assert any("spec-used" in r for r in rows)
    assert any("spec-unread" in r for r in rows)
    assert "spec-used" in next(r for r in rows if "Elexon" in r)
    for s in door.GO_LIVE_SEAMS:
        for record in (s.get("spec"), s.get("used")):
            if record:
                assert (door.PROJECT / record["where"]).exists(), record["where"]


def test_one_piece_of_work_is_never_stated_on_both_sides():
    """24 Oct: "a consistency check that goes red ... when the world and the supplier state the
    same capability differently". Both branches, then the real register. MUTATION: return [] from
    `stated_on_both_sides` -> the first assert reds; compare by name instead of work -> the second
    reds."""
    world = [{"name": "Settlement", "rests_on": ["W3_2"]}]
    assert door.stated_on_both_sides(world, [{"name": "Settling", "rests_on": ["EP5", "W3_2"]}]) \
        == ["W3_2"]
    assert door.stated_on_both_sides(world, [{"name": "Settlement", "rests_on": ["EP5"]}]) == []
    ids = lambda reg: [{"rests_on": r[2]} for r in reg]  # noqa: E731
    assert door.stated_on_both_sides(ids(door.WORLD), ids(door.SUPPLIER)) == []


def test_the_fixed_strip_dates_from_git_and_drops_what_has_aged_out(tmp_path):
    """The strip is generated: the date is the commit's, the window is applied at publish, and a
    commit nobody can find stops the feed. MUTATION: skip the window test -> the aged-out row stays
    and the first assert reds; swallow the unresolved commit -> the raise is not met."""
    import json

    import pytest

    head = door._git("rev-parse", "HEAD")
    at = int(door._git("show", "-s", "--format=%ct", head))
    rec = tmp_path / "fixed.json"
    rec.write_text(json.dumps({"window_days": 7, "fixes": [{"commit": head, "what": "w"}]}))
    dash = tmp_path / "dash.json"
    dash.write_text(json.dumps({"meta": {"git_commit": head}}))
    assert door.fixed_this_week(now=at + 8 * 86400, record=rec, dashboard=dash)["items"] == []
    got = door.fixed_this_week(now=at + 60, record=rec, dashboard=dash)["items"]
    assert len(got) == 1 and got[0]["in_published_run"] is True
    rec.write_text(json.dumps({"window_days": 7, "fixes": [{"commit": "0" * 40, "what": "w"}]}))
    with pytest.raises(door.CapabilitySourceUnavailable):
        door.fixed_this_week(now=at, record=rec, dashboard=dash)


def test_the_fixed_record_resolves():
    feed = door.fixed_this_week(now=4102444800)  # far future: every row ages out, none may raise
    assert feed["items"] == []
