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
GOOD_RECOMMENDATION = "I recommend a learned split; holding the fixed one until he rules"


def _record(**over) -> dict:
    base = {"version": 1, "oriented_at": datetime.now(timezone.utc).isoformat(),
            "thesis_read": "reading", "focus": [{"id": "atom-a", "why": "because", "side": "supplier"},
                      {"id": "atom-b", "why": "because", "side": "supplier"}],
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
    # `orient()` also grades `wrong` against the triage register; keep the real one out.
    monkeypatch.setattr(d, "WRONG_TRIAGE_PATH", tmp_path / "wrong_triage.yaml")
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
        row = dc.raise_concern(kind, what, proposal, "docs/design/THE_MODEL_ON_A_PAGE.md",
                               recommendation=GOOD_RECOMMENDATION)
        assert row["status"] == "open" and row["id"] and row["raised"]
        assert dc.open_rows(dc.read_raw()) == [row]
        assert d.validate(dc.read_raw()) == []
    else:
        with pytest.raises(dc.ConcernRefused, match=refused_for):
            dc.raise_concern(kind, what, proposal, recommendation=GOOD_RECOMMENDATION)
        assert record_file.read_text(encoding="utf-8") == before, "a refusal still wrote"


# The row that sat open for a day before the 23 Oct ruling, in its own words.
SWITCH_WHAT = ("The estimated bill can read the customer's annualised advance (D48, built default "
               "off). Its pre-registered arm pair is graded and the rule is met.")
SWITCH_PROPOSAL = ("Turn DecisionPolicy.bill_estimate_reads_the_annualised_advance on by default, "
                   "for every standing policy.")


@pytest.mark.parametrize("kind, proposal, refused", [
    ("strategy", SWITCH_PROPOSAL, True),                                   # the machine's own call
    ("strategy", SWITCH_PROPOSAL + " Outside the 23 Oct ruling: it changes a curriculum value.",
     False),                                                               # says why it is his
    ("reserved", SWITCH_PROPOSAL, False),                                  # a reserved act is his
    ("strategy", GOOD_PROPOSAL, False),                                    # not a switch-on at all
])
def test_a_switch_on_the_23_oct_ruling_made_the_machines_is_REFUSED_at_raise(record_file, kind,
                                                                             proposal, refused):
    """Defect: a default-off switch whose pre-registered rule is met is raised for the director, and
    a better bill estimate waits on him for a day -- his 23 Oct ruling made it the machine's call.
    One control over the partition: the refusal fires, names the ruling, writes nothing; and the
    escape clause, a reserved kind and an unrelated concern each still reach the list.

    MUTATION (must fire): drop the `switch_on_refusal` call in `raise_concern` (row 1 goes green
    where it must refuse), or make it return its reason unconditionally (rows 2-4 refuse)."""
    before = record_file.read_text(encoding="utf-8")
    what = SWITCH_WHAT if proposal != GOOD_PROPOSAL else GOOD_WHAT
    g5 = "real_money" if kind == "reserved" else None
    if refused:
        with pytest.raises(dc.ConcernRefused, match="ruling of 23 Oct"):
            dc.raise_concern(kind, what, proposal, recommendation=GOOD_RECOMMENDATION, g5_class=g5)
        assert record_file.read_text(encoding="utf-8") == before, "a refusal still wrote"
    else:
        row = dc.raise_concern(kind, what, proposal, recommendation=GOOD_RECOMMENDATION,
                               g5_class=g5)
        assert dc.open_rows(dc.read_raw())[-1] == row


@pytest.mark.parametrize("kind, g5_class, refused_for", [
    ("reserved", "real_money", None),                                  # the passing branch
    ("reserved", None, "names its G5 class"),
    ("reserved", "a_judgement_call", "names its G5 class"),
    ("strategy", "real_money", "carries no G5 class"),
    ("strategy", None, None),                                          # still reaches the list
])
def test_a_reserved_concern_names_its_G5_class_or_is_not_raised(record_file, kind, g5_class,
                                                                refused_for):
    """Defect (advisor steer 26 Oct): thirteen questions waited on the director and nine were the
    seat's own calls, because nothing made a raise say which reserved action it was. One partition:
    a reserved raise without a valid G5 class refuses and writes nothing, a class on another kind
    refuses, and the two passing rows are written; `validate` flags an open reserved row with none.

    MUTATION (must fire): drop the class check in `raise_concern` (rows 2-3 go green), or the
    `g5_classes` clause in `_concern_problems` (the validate leg)."""
    before = record_file.read_text(encoding="utf-8")
    if refused_for:
        with pytest.raises(dc.ConcernRefused, match=refused_for):
            dc.raise_concern(kind, GOOD_WHAT, GOOD_PROPOSAL, recommendation=GOOD_RECOMMENDATION,
                             g5_class=g5_class)
        assert record_file.read_text(encoding="utf-8") == before, "a refusal still wrote"
    else:
        row = dc.raise_concern(kind, GOOD_WHAT, GOOD_PROPOSAL, recommendation=GOOD_RECOMMENDATION,
                               g5_class=g5_class)
        assert row.get("g5_class") == g5_class and d.validate(dc.read_raw()) == []
    bare = {"id": "x", "what": "w", "proposal": "p", "status": "open", "kind": "reserved"}
    assert any("names no G5 class" in p for p in d._concern_problems([bare]))
    assert d._concern_problems([dict(bare, g5_class="real_money")]) == []


def test_raising_edits_ONLY_the_concerns_block_and_ids_stay_unique(record_file):
    """Defect: the CLI re-dumps the whole record, rewriting the seat's prose and comments under a
    concurrent reader. Everything outside `for_the_director` must be byte-identical."""
    before = record_file.read_text(encoding="utf-8")
    head = before.split("for_the_director:")[0]
    a = dc.raise_concern("vision", GOOD_WHAT, GOOD_PROPOSAL, recommendation=GOOD_RECOMMENDATION)
    b = dc.raise_concern("vision", GOOD_WHAT, GOOD_PROPOSAL, recommendation=GOOD_RECOMMENDATION)
    after = record_file.read_text(encoding="utf-8")
    assert after.startswith(head), "the edit touched the record outside its own block"
    assert a["id"] != b["id"] and b["id"].startswith(a["id"])


def test_answering_and_withdrawing_need_a_resolution(record_file):
    row = dc.raise_concern("strategy", GOOD_WHAT, GOOD_PROPOSAL, recommendation=GOOD_RECOMMENDATION)
    with pytest.raises(dc.ConcernRefused, match="needs a resolution"):
        dc.resolve(row["id"], "answered", " ")
    with pytest.raises(dc.ConcernRefused, match="no concern with id"):
        dc.resolve("not-a-row", "answered", "his words", no_action="none owed")
    done = dc.resolve(row["id"], "answered", "Rich 2026-10-04: the split is learned, go on",
                      no_action="the code already learns it")
    assert done["status"] == "answered" and done["resolved"]
    assert dc.open_rows(dc.read_raw()) == [] and d.validate(dc.read_raw()) == []


def test_the_cli_refuses_with_a_named_reason_and_prints_the_pathspec(record_file, capsys):
    assert dc.main(["--raise", "--kind", "strategy", "--what", GOOD_WHAT]) == 2
    assert "needs a proposal" in capsys.readouterr().err
    assert dc.main(["--raise", "--kind", "strategy", "--what", GOOD_WHAT,
                    "--proposal", GOOD_PROPOSAL, "--recommendation", GOOD_RECOMMENDATION]) == 0
    out = capsys.readouterr().out
    assert "open:" in out and "surgical_land" in out and "DIRECTION.yaml" in out
    assert dc.main(["--list"]) == 0 and GOOD_PROPOSAL in capsys.readouterr().out


@pytest.mark.parametrize("recommendation, refused_for", [
    (GOOD_RECOMMENDATION, None),                                       # the passing branch
    ("", "has no recommendation"),
    ("Options: hold 400 supply points, or count households", "recommends nothing"),
])
def test_a_concern_with_no_recommendation_is_REFUSED_at_raise_and_FLAGGED_by_the_watcher(
        record_file, recommendation, refused_for):
    """Defect (director, 19 Oct 16:38: *"Even items that are reserved for me I'd prefer it to make
    a considered recommendation"*): a row reaches him with a holding position or a neutral list of
    options and no view on the question. One partition over both legs: the raise refuses it and
    writes nothing, and the staging watcher flags an open row carrying the same text; the passing
    row is written and flagged by neither, so neither leg refuses everything.

    MUTATION (must fire): return None from `direction.concern_lacks_recommendation`, or drop its
    `_RECOMMENDS` clause, or drop the call in `raise_concern`."""
    from background import staging_watcher as sw

    before = record_file.read_text(encoding="utf-8")
    row = dict(_OPEN, recommendation=recommendation)
    flagged = sw.flag_concerns_without_recommendation(_record(for_the_director=[row]))
    if refused_for is None:
        written = dc.raise_concern("reserved", GOOD_WHAT, GOOD_PROPOSAL,
                                   recommendation=recommendation, g5_class="real_money")
        assert dc.read_raw()["for_the_director"][-1]["recommendation"] == GOOD_RECOMMENDATION
        assert written["status"] == "open" and flagged == []
    else:
        with pytest.raises(dc.ConcernRefused, match=refused_for):
            dc.raise_concern("reserved", GOOD_WHAT, GOOD_PROPOSAL, recommendation=recommendation,
                             g5_class="real_money")
        assert record_file.read_text(encoding="utf-8") == before, "a refusal still wrote"
        assert len(flagged) == 1 and refused_for in flagged[0] and "canon-split" in flagged[0]
    closed = dict(row, status="answered", resolution="Rich: yes")
    assert sw.flag_concerns_without_recommendation(_record(for_the_director=[closed])) == [], (
        "an answered row was flagged: he has already ruled on it")


def test_a_carried_row_may_GAIN_a_recommendation_but_never_lose_one():
    """The 19 Oct backfill adds a recommendation to rows already waiting; a later rewrite that
    drops or rewords it is refused like a reworded `what`. MUTATION (must fire): drop the
    `("recommendation",)` clause from `carry_problems`."""
    bare, rec = dict(_OPEN), dict(_OPEN, recommendation=GOOD_RECOMMENDATION)
    assert dc.carry_problems(_record(for_the_director=[bare]),
                             _record(for_the_director=[rec])) == []
    lost = dc.carry_problems(_record(for_the_director=[rec]), _record(for_the_director=[bare]))
    assert len(lost) == 1 and "rewrote the open concern" in lost[0]


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
    dc.raise_concern("canon_intent", GOOD_WHAT, GOOD_PROPOSAL, recommendation=GOOD_RECOMMENDATION)
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
    dc.raise_concern("vision", GOOD_WHAT, GOOD_PROPOSAL, recommendation=GOOD_RECOMMENDATION)
    rows = dc.open_rows(dc.read_raw())
    text = seat._prompt({"previous_for_the_director": rows, "shape": {}, "running": {},
                         "ended": {}})
    assert "CARRY EVERY ONE FORWARD" in text and rows[0]["id"] in text and GOOD_PROPOSAL in text
    assert text.index(rows[0]["id"]) < text.index("THE STRETCH, assembled from git")
    assert "NO OPEN CONCERNS" in seat._prompt({"shape": {}, "running": {}, "ended": {}})


def test_a_session_that_did_not_run_is_REFUSED_PAGED_and_lands_NOTHING(monkeypatch, record_file):
    """11:24Z 2026-10-07: the spawn died, the untouched working copy validated, the row read
    `oriented` and that stale copy was landed over origin. Both branches through `orient()`: a
    session that ran is oriented and committed; one that did not is refused, paged, uncommitted.
    MUTATION (must fire): drop the `if not ran` return from `orient`."""
    commits: list = []
    pages: list = []
    row = _drive_orient(monkeypatch, record_file, _record(), pages)
    monkeypatch.setattr(seat, "commit_direction", lambda: (commits.append(1), (True, "x"))[1])
    row = seat.orient()
    assert row["outcome"] == "oriented" and commits == [1], "the ran branch must stay reachable"

    commits.clear()
    pages.clear()
    monkeypatch.setattr(seat, "run_session", lambda b: (
        False, "spawn failed: OSError(7, 'Argument list too long')"))
    row = seat.orient()
    assert commits == [], "a session that never ran had its working copy landed as direction"
    last = d.read_decisions(limit=1)[0]
    assert last["outcome"] == "refused" and last["ran"] is False
    assert "Argument list too long" in last["problems"][0]
    assert [p[1] for p in pages] == ["blocked_work"]


# ── A close that commits is checked against done (director steer, 28 Oct) ─────────────────────

READER_ID = "reading-reviewer-trial-your-08-56-yes"
#: The reader close as it stood in DIRECTION.yaml at ba60f147d2^, trimmed to the graded fields.
READER_CLOSE = {
    "id": READER_ID, "kind": "strategy", "status": "withdrawn", "resolved": "2026-10-26",
    "resolution": "Withdrawn 2026-10-26: not a G5-reserved action ... Closed on the seat's own "
                  "recommendation: the two-reader blind non-blocking review trial as proposed",
    "recommendation": "I recommend the trial as proposed: two blind non-blocking Opus readers"}
READER_COMMITMENT = {"work_id": "the-two-reader-review-runs-on-every-qualifying-commit",
                     "done_means": "two blind readers have run on a qualifying commit",
                     "due": "2026-10-27"}


def _no_landing(work_id):
    return 0.0, []


def test_the_26_oct_reader_close_COMES_BACK_OVERDUE_had_the_rule_been_live(monkeypatch):
    """The steer's own proof case. Closed 26 Oct as "the trial as proposed"; by 28 Oct nothing
    bound to its work had landed (the live ledger holds no landing for that id). Under the rule,
    with the commitment the close should have named, it is OVERDUE on 28 Oct; with neither field it
    is UNSTATED -- still the machine's debt. With the rule dated as shipped, the same historical
    row is not graded at all, which is what keeps the 28 pre-rule closes from returning as noise.

    MUTATION (must fire): grade `met` on any landing (drop `>= closed_on`), or drop the
    `due < today` leg -- the first leg below goes green or pending."""
    monkeypatch.setattr(dc, "CLOSE_COMMITMENT_FROM", "2026-10-26")
    committed = {READER_ID: {**READER_CLOSE, "commitment": READER_COMMITMENT,
                             "closed_on": "2026-10-26"}}
    [graded] = dc.close_debts(committed, today="2026-10-28", landing=_no_landing)
    assert graded["state"] == "overdue" and graded["due"] == "2026-10-27"
    landed_before = lambda w: (datetime(2026, 10, 20, tzinfo=timezone.utc).timestamp(), ["x"])  # noqa: E731
    assert dc.close_debts(committed, today="2026-10-28", landing=landed_before)[0]["state"] \
        == "overdue", "a landing from before the close met a commitment made after it"
    bare = {READER_ID: {**READER_CLOSE, "closed_on": "2026-10-26"}}
    assert dc.close_debts(bare, today="2026-10-28", landing=_no_landing)[0]["state"] == "unstated"

    monkeypatch.setattr(dc, "CLOSE_COMMITMENT_FROM", "2026-10-28")
    assert dc.close_debts(bare, today="2026-11-02", landing=_no_landing) == []


def test_every_grade_of_a_close_is_REACHABLE_in_one_partition():
    """One control over the whole partition: a grader that can only say one thing passes any
    single-leg test of it."""
    def landing(work_id):
        return ((datetime(2026, 10, 29, tzinfo=timezone.utc).timestamp(), ["p"])
                if work_id == "w-met" else (0.0, []))

    def close(rid, **kw):
        return {"id": rid, "status": "answered", "closed_on": "2026-10-28", **kw}

    commit = lambda w, due: {"work_id": w, "done_means": "it landed", "due": due}  # noqa: E731
    closes = {"a": close("a", commitment=commit("w-met", "2026-10-30")),
              "b": close("b", commitment=commit("w-none", "2026-11-30")),
              "c": close("c", commitment=commit("w-none", "2026-10-29")),
              "d": close("d"),
              "e": close("e", no_action="nothing to build")}
    states = {g["id"]: g["state"] for g in
              dc.close_debts(closes, today="2026-11-01", landing=landing)}
    assert states == {"a": "met", "b": "pending", "c": "overdue", "d": "unstated",
                      "e": "no_action"}


def test_a_close_made_BETWEEN_orientations_is_found_in_the_committed_revisions():
    """The reader-case shape: the decisions history last saw the row open, the live record no
    longer holds it, and only a committed revision of DIRECTION.yaml carries the close. An undated
    close takes the first day it was seen closed rather than escaping the rule."""
    history = [{"at": "2026-10-28T09:00:00+00:00",
                "for_the_director": [{"id": "r1", "status": "open"}, "a legacy bare string"]},
               {"at": "2026-10-29T09:00:00+00:00", "closes": [
                   {"id": "r2", "status": "answered", "resolution": "his yes"}]}]
    revisions = [("2026-10-28", {"for_the_director": [
        {"id": "r1", "status": "withdrawn", "resolution": "seat call", "resolved": "2026-10-28",
         "commitment": {"work_id": "w", "done_means": "d", "due": "2026-10-29"}}]})]
    closes = dc.closes_on_record(history=history, revisions=revisions, records=(None, None),
                                 today="2026-10-31")
    assert set(closes) == {"r1", "r2"}
    assert closes["r2"]["closed_on"] == "2026-10-29"
    states = {g["id"]: g["state"] for g in
              dc.close_debts(closes, today="2026-10-31", landing=_no_landing)}
    assert states == {"r1": "overdue", "r2": "unstated"}


@pytest.mark.parametrize("kw, refused_for", [
    ({}, "commits the machine to"),
    ({"commitment": {"work_id": "w", "done_means": "", "due": "2026-11-01"}}, "no done_means"),
    ({"commitment": {"work_id": "w", "done_means": "d", "due": "soon"}}, "not a date"),
    ({"commitment": {"work_id": "w", "done_means": "d", "due": "2026-10-01"}}, "before the close"),
    ({"commitment": {"work_id": "w", "done_means": "d", "due": "2026-11-01"}}, None),
    ({"no_action": "the ruling changes nothing"}, None),
])
def test_closing_from_the_rules_start_names_its_commitment_or_why_none(record_file, kw,
                                                                         refused_for):
    row = dc.raise_concern("strategy", GOOD_WHAT, GOOD_PROPOSAL, recommendation=GOOD_RECOMMENDATION)
    now = datetime(2026, 10, 28, 9, tzinfo=timezone.utc)
    if refused_for:
        with pytest.raises(dc.ConcernRefused, match=refused_for):
            dc.resolve(row["id"], "answered", "his yes", now=now, **kw)
        assert dc.open_rows(dc.read_raw()), "a refused close still closed the row"
    else:
        done = dc.resolve(row["id"], "answered", "his yes", now=now, **kw)
        assert done["status"] == "answered" and d.validate(dc.read_raw()) == []


def test_the_monday_note_has_four_sections_and_says_none_when_one_is_empty():
    now = datetime(2026, 11, 2, 7, tzinfo=timezone.utc)
    closes = {
        "his": {"id": "his", "status": "answered", "closed_on": "2026-10-30",
                "resolution": "Director: yes, do it",
                "commitment": {"work_id": "w", "done_means": "the thing landed",
                               "due": "2026-10-31"}},
        "seat": {"id": "seat", "status": "withdrawn", "closed_on": "2026-10-29",
                 "resolution": "Withdrawn: a seat call", "recommendation": "I recommend X",
                 "no_action": "nothing to build"},
        "old": {"id": "old", "status": "answered", "closed_on": "2026-10-01", "resolution": "x"}}
    note = dc.monday_note(now, closes=closes, open_rows_now=[], landing=_no_landing)
    heads = [ln for ln in note.splitlines() if ln.startswith("## ")]
    assert len(heads) == 4
    waiting = note.split("## Waiting on you")[1].split("## ")[0]
    assert waiting.strip() == "None."
    assert "**his**" in note and "OVERDUE since 2026-10-31" in note
    assert "**seat**: I recommend X" in note
    assert "**old**" not in note, "a close from before this week was reported as this week's"
    overdue = note.split("## Overdue")[1]
    assert "**his**" in overdue and "**seat**" not in overdue


def test_one_answer_to_several_questions_is_printed_once_with_each_question_beneath_it():
    """The 26 Oct ruling closed four rows with one resolution; the first live note printed its
    opening 220 characters four times and named none of the four questions.

    MUTATION (must fire): render each answered row on its own line again."""
    now = datetime(2026, 11, 2, 7, tzinfo=timezone.utc)
    ruling = "Director: " + "hide the link and keep the tracker " * 12
    closes = {rid: {"id": rid, "status": "answered", "closed_on": "2026-10-26",
                    "resolution": ruling, "what": f"Question {rid} about the front door"}
              for rid in ("q1", "q2", "q3")}
    closes["solo"] = {"id": "solo", "status": "answered", "closed_on": "2026-10-28",
                      "resolution": "Yes", "what": "a question of its own"}
    note = dc.monday_note(now, closes=closes, open_rows_now=[], landing=_no_landing)
    decided = note.split("## What you decided this week")[1].split("## ")[0]
    assert decided.count("Director: hide") == 1, decided
    assert "One answer to 3 questions" in decided
    for rid in ("q1", "q2", "q3"):
        assert f"**{rid}**: Question {rid} about the front door" in decided
    assert "**solo**: Yes" in decided
    shown = decided.split("questions**: ")[1].split("...")[0]
    assert (ruling.split() + [""])[len(shown.split()) - 1] == shown.split()[-1], \
        "a truncation cut a word in half"


def test_one_quoted_ruling_with_a_different_outcome_per_question_prints_each_outcome():
    """The live 26 Oct shape: one quoted ruling, then each row's own outcome past character 220.
    Keyed on the whole text, the four never grouped, so the 2 Nov dry run printed the same cut-off
    quote four times and none of "Declined", "Ruled: ...", "Deferred".

    MUTATION (must fire): group on the whole resolution instead of the line the reader sees."""
    now = datetime(2026, 11, 2, 7, tzinfo=timezone.utc)
    quote = 'Answered 26 Oct: "' + "hide the link and keep the tracker " * 8 + '"'
    outcomes = {"q1": "Declined: no link from any page.", "q2": "Ruled: analytics stay.",
                "q3": "Deferred, not open: the token waits."}
    closes = {rid: {"id": rid, "status": "answered", "closed_on": "2026-10-26",
                    "resolution": f"{quote} {own}", "what": f"Question {rid}"}
              for rid, own in outcomes.items()}
    note = dc.monday_note(now, closes=closes, open_rows_now=[], landing=_no_landing)
    decided = note.split("## What you decided this week")[1].split("## ")[0]
    assert decided.count("Answered 26 Oct") == 1 and "One answer to 3 questions" in decided, decided
    for rid, own in outcomes.items():
        assert f"**{rid}**: Question {rid} -- {own}" in decided, decided


def test_an_orientation_RECORDS_the_closes_it_was_handed(monkeypatch, record_file):
    """The decisions-history half: a row closed between orientations and dropped by the session is
    still on the append-only record, with its commitment.

    MUTATION (must fire): drop the `closes` key from the decision row in `orient`."""
    monkeypatch.setattr(dc, "read_origin_raw", lambda root=None: None)
    row = dc.raise_concern("strategy", GOOD_WHAT, GOOD_PROPOSAL, recommendation=GOOD_RECOMMENDATION)
    dc.resolve(row["id"], "answered", "his yes", commitment={**READER_COMMITMENT,
                                                            "due": "2099-12-31"})
    out = _drive_orient(monkeypatch, record_file, _record(), [])
    assert out["outcome"] == "oriented"
    [handed] = out["closes"]
    assert handed["id"] == row["id"] and handed["commitment"]["work_id"] == READER_COMMITMENT[
        "work_id"]
