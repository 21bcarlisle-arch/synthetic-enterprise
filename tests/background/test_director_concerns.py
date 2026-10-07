"""The director's concerns list: raised with a proposal, carried until answered, paged once.

Director, 2026-10-04: *"Escalate with a proposal, and don't wait ... An open question to me sits in
a list and never blocks the queue."* The list lives in `DIRECTION.yaml`, which the orienting seat
REWRITES every stretch, so the defects these controls exist for are: a concern raised without a
proposal; a concern lost at the next rewrite; and a carried concern re-paging him every stretch.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
import yaml

from background import delivery_seat as seat
from background import direction as d
from background import director_concerns as dc

GOOD_WHAT = "The canon reads value-sharing as a fixed split; the code learns it per household."
GOOD_PROPOSAL = "investigate: whether the canon meant a fixed split"


def _record(**over) -> dict:
    base = {"version": 1, "oriented_at": datetime.now(timezone.utc).isoformat(),
            "thesis_read": "reading", "focus": [{"id": "atom-a", "why": "because"}],
            "not_now": [{"what": "x", "why": "y"}], "wrong": [], "for_the_director": []}
    base.update(over)
    return base


@pytest.fixture()
def record_file(tmp_path, monkeypatch):
    path = tmp_path / "DIRECTION.yaml"
    path.write_text("# a hand comment the CLI must not touch\n" + yaml.safe_dump(
        _record(), sort_keys=False), encoding="utf-8")
    monkeypatch.setattr(d, "DIRECTION_PATH", path)
    monkeypatch.setattr(d, "DECISIONS_PATH", tmp_path / "decisions.jsonl")
    return path


# ── raising ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("kind, what, proposal, refused_for", [
    ("canon_intent", GOOD_WHAT, GOOD_PROPOSAL, None),                  # the passing branch
    ("strategy", GOOD_WHAT, "", "needs a proposal"),
    ("strategy", "", GOOD_PROPOSAL, "needs a what"),
    ("tactics", GOOD_WHAT, GOOD_PROPOSAL, "kind must be one of"),
    ("strategy", "Is the canon wrong about the split?", "investigate: the split", "bare ask"),
])
def test_raising_REFUSES_a_concern_with_no_proposal_or_a_bare_ask(record_file, kind, what,
                                                                  proposal, refused_for):
    """Defect: a concern enters the list as a bare ask. One control over the partition -- the
    passing row is written and each refusing branch is reached with its own reason, and a refusal
    writes NOTHING.

    MUTATION (must fire): drop the `check_message` call, or the empty-proposal clause."""
    before = record_file.read_text(encoding="utf-8")
    if refused_for is None:
        row = dc.raise_concern(kind, what, proposal, "docs/design/THE_MODEL_ON_A_PAGE.md")
        assert row["status"] == "open" and row["id"] and row["raised"]
        assert dc.open_rows(dc.read_raw()) == [row]
        assert d.validate(dc.read_raw()) == []
    else:
        with pytest.raises(dc.ConcernRefused, match=refused_for):
            dc.raise_concern(kind, what, proposal)
        assert record_file.read_text(encoding="utf-8") == before, "a refusal still wrote"


def test_raising_edits_ONLY_the_concerns_block_and_ids_stay_unique(record_file):
    """Defect: the CLI re-dumps the whole record, rewriting the seat's prose and comments under a
    concurrent reader. Everything outside `for_the_director` must be byte-identical."""
    before = record_file.read_text(encoding="utf-8")
    head = before.split("for_the_director:")[0]
    a = dc.raise_concern("vision", GOOD_WHAT, GOOD_PROPOSAL)
    b = dc.raise_concern("vision", GOOD_WHAT, GOOD_PROPOSAL)
    after = record_file.read_text(encoding="utf-8")
    assert after.startswith(head), "the edit touched the record outside its own block"
    assert a["id"] != b["id"] and b["id"].startswith(a["id"])


def test_answering_and_withdrawing_need_a_resolution(record_file):
    row = dc.raise_concern("strategy", GOOD_WHAT, GOOD_PROPOSAL)
    with pytest.raises(dc.ConcernRefused, match="needs a resolution"):
        dc.resolve(row["id"], "answered", " ")
    with pytest.raises(dc.ConcernRefused, match="no concern with id"):
        dc.resolve("not-a-row", "answered", "his words")
    done = dc.resolve(row["id"], "answered", "Rich 2026-10-04: the split is learned, go on")
    assert done["status"] == "answered" and done["resolved"]
    assert dc.open_rows(dc.read_raw()) == [] and d.validate(dc.read_raw()) == []


def test_the_cli_refuses_with_a_named_reason_and_prints_the_pathspec(record_file, capsys):
    assert dc.main(["--raise", "--kind", "strategy", "--what", GOOD_WHAT]) == 2
    assert "needs a proposal" in capsys.readouterr().err
    assert dc.main(["--raise", "--kind", "strategy", "--what", GOOD_WHAT,
                    "--proposal", GOOD_PROPOSAL]) == 0
    out = capsys.readouterr().out
    assert "open:" in out and "surgical_land" in out and "DIRECTION.yaml" in out
    assert dc.main(["--list"]) == 0 and GOOD_PROPOSAL in capsys.readouterr().out


# ── carrying ─────────────────────────────────────────────────────────────────

_OPEN = {"id": "canon-split", "kind": "canon_intent", "what": GOOD_WHAT, "proposal": GOOD_PROPOSAL,
         "status": "open", "resolution": ""}


@pytest.mark.parametrize("after_rows, refused_for", [
    ([dict(_OPEN)], None),                                                          # carried
    ([dict(_OPEN, status="answered", resolution="Rich: yes")], None),               # answered
    ([dict(_OPEN, status="withdrawn", resolution="measured: not a canon question")], None),
    ([], "dropped the open concern"),                                               # dropped
    ([dict(_OPEN, what="reworded")], "rewrote the open concern"),                   # reworded
    ([dict(_OPEN, proposal="something else")], "rewrote the open concern"),
])
def test_a_new_record_that_DROPS_or_REWORDS_an_open_concern_is_refused(after_rows, refused_for):
    """Defect: the seat rewrites the record every stretch, so an open concern can vanish at the
    next rewrite with nothing noticing. Partition over carried / answered / withdrawn (pass) and
    dropped / reworded (refuse).

    MUTATION (must fire): return [] from `carry_problems`, or drop its reword clause."""
    problems = dc.carry_problems(_record(for_the_director=[dict(_OPEN)]),
                                 _record(for_the_director=after_rows))
    if refused_for is None:
        assert problems == []
    else:
        assert problems and refused_for in problems[0]


def test_paging_is_once_per_id_and_not_once_per_stretch():
    """Defect: the seat paged on every record whose list was non-empty, so a carried concern would
    re-page him every three hours. MUTATION: ignore `previous_ids` and this fires."""
    after = _record(for_the_director=[dict(_OPEN), dict(_OPEN, id="new-one")])
    assert dc.new_open_ids(["canon-split"], after) == ["new-one"]
    assert dc.new_open_ids(["canon-split", "new-one"], after) == []
    assert dc.new_open_ids([], _record(for_the_director=[dict(
        _OPEN, status="answered", resolution="x")])) == [], "an answered row is never paged"


# ── the seat, end to end ─────────────────────────────────────────────────────


def _drive_orient(monkeypatch, record_file, written: dict, pages: list) -> dict:
    """`orient()` with only its outside world replaced: the session writes `written`."""
    from background import tick_mode
    from tools import generate_delivery_page

    brief = {"since": "2026-10-04T00:00:00+00:00", "commit_count": 1, "substantive_count": 1,
             "previous_focus_drawn": None}
    monkeypatch.setattr(seat, "build_brief", lambda now: brief)
    monkeypatch.setattr(seat, "is_material", lambda b: (True, "one commit"))
    monkeypatch.setattr(seat, "map_levels", lambda: {})
    monkeypatch.setattr(tick_mode, "gate", lambda route: (True, "normal", ""))
    monkeypatch.setattr(tick_mode, "note_spawn", lambda route: None)
    monkeypatch.setattr(seat, "run_session", lambda b: (record_file.write_text(
        yaml.safe_dump(written, sort_keys=False), encoding="utf-8"), (True, "ran"))[1])
    monkeypatch.setattr(seat, "write_stretch_entry", lambda row: True)
    monkeypatch.setattr(generate_delivery_page, "generate", lambda: None)
    monkeypatch.setattr(seat, "commit_direction", lambda: (True, "stubbed"))
    monkeypatch.setattr(seat, "out_of_scope_writes", lambda: [])
    monkeypatch.setattr(seat.direction_path_check, "concerns", lambda raw: [])
    monkeypatch.setattr(seat, "_log", lambda m: None)
    monkeypatch.setattr(seat, "_notify", lambda msg, topic_class: pages.append((msg, topic_class)))
    return seat.orient()


def test_the_seat_REFUSES_and_RESTORES_a_record_that_drops_an_open_concern(monkeypatch,
                                                                           record_file):
    """The enforcement in code, through `orient()` itself. Both branches: a record that drops the
    open row is refused AND the previous bytes are restored (so the concern is not lost to the
    overwrite and read as never-raised next stretch); a record that carries it is filed, and the
    carried row is not re-paged.

    MUTATION (must fire): drop `+ dropped` from the problems in `orient`, or the restore."""
    dc.raise_concern("canon_intent", GOOD_WHAT, GOOD_PROPOSAL)
    raised = record_file.read_bytes()
    pages: list = []

    row = _drive_orient(monkeypatch, record_file, _record(), pages)
    assert row["outcome"] == "refused"
    assert any("dropped the open concern" in p for p in row["problems"])
    assert record_file.read_bytes() == raised, "the dropped concern was lost to the overwrite"

    carried = _record(for_the_director=dc.rows_of(yaml.safe_load(raised)))
    pages.clear()
    row = _drive_orient(monkeypatch, record_file, carried, pages)
    assert row["outcome"] == "oriented"
    assert row["for_the_director"][0]["proposal"] == GOOD_PROPOSAL
    assert [p[1] for p in pages] == ["decision_waiting"] and GOOD_PROPOSAL in pages[0][0], (
        "a concern new since the last oriented row must page once, with its proposal")

    pages.clear()
    row = _drive_orient(monkeypatch, record_file, carried, pages)
    assert row["outcome"] == "oriented" and pages == [], "a carried concern re-paged him"


def test_a_record_that_did_not_reach_origin_ends_the_orientation_REFUSED_and_PAGED(
        monkeypatch, record_file):
    """Through `orient()`: when `commit_direction` refuses, the last decisions row reads `refused`
    with the reason and the director is paged; when it lands, neither happens. MUTATION (must
    fire): drop the `record_landing_refused` call from `orient`."""
    pages: list = []
    row = _drive_orient(monkeypatch, record_file, _record(), pages)
    assert row["committed"] is True and pages == []
    assert d.read_decisions(limit=1)[0]["outcome"] == "oriented"

    monkeypatch.setattr(seat, "commit_direction",
                        lambda: (False, "landing refused (DirectionNotLanded): origin moved"))
    monkeypatch.setattr(seat, "_notify", lambda msg, topic_class: pages.append((msg, topic_class)))
    seat.orient()
    last = d.read_decisions(limit=1)[0]
    assert last["outcome"] == "refused" and "origin moved" in last["landing_refused"]
    assert [p[1] for p in pages] == ["blocked_work"]


def test_the_brief_and_prompt_hand_the_open_concerns_back(record_file):
    """Defect: the carry check refuses a dropped concern the session was never shown. The open
    rows reach the prompt as a sentence ABOVE the truncated JSON, as `previous_wrong` does."""
    dc.raise_concern("vision", GOOD_WHAT, GOOD_PROPOSAL)
    rows = dc.open_rows(dc.read_raw())
    text = seat._prompt({"previous_for_the_director": rows, "shape": {}, "running": {},
                         "ended": {}})
    assert "CARRY EVERY ONE FORWARD" in text and rows[0]["id"] in text and GOOD_PROPOSAL in text
    assert text.index(rows[0]["id"]) < text.index("THE STRETCH, assembled from git")
    assert "NO OPEN CONCERNS" in seat._prompt({"shape": {}, "running": {}, "ended": {}})
