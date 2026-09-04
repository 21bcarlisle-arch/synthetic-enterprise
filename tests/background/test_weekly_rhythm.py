"""THE DEFECT: rituals written as prose have no trigger, so they run only when the director remembers.

Director, 2026-09-04: *"The mothball audit has sat parked since late July. It has no trigger and no
schedule ... That is a mechanism problem, not a priority problem."* Every leg here is about a way the
rhythm could look like it was working while firing nothing — which is the failure mode of the thing
it replaces, and the only one worth controls.

The four requirements it was given, and the leg that owns each:
  * each step fires from the one before  -> test_closing_a_step_is_the_only_thing_that_arms_the_next
  * a step that did not fire is a finding -> test_a_step_still_open_the_day_after_it_was_due_is_a_finding
  * the days are the DIRECTOR's           -> test_the_day_is_londons_not_the_machines
  * no findings about itself              -> test_an_unreadable_baton_is_rebuilt_and_mints_nothing
"""
from __future__ import annotations

import json
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from background import weekly_rhythm as wr

LONDON = ZoneInfo("Europe/London")


@pytest.fixture()
def rhythm(tmp_path, monkeypatch):
    """A baton and a staging room of this test's own. Never the live ones."""
    monkeypatch.setattr(wr, "BATON", tmp_path / "baton.json")
    monkeypatch.setattr(wr, "STAGING", tmp_path / "staging")
    return tmp_path


def _at(y, m, d, hour=7):
    return datetime(y, m, d, hour, tzinfo=LONDON)


# ── the clock, which is the constraint he named twice ────────────────────────────────────────────

def test_the_day_is_londons_not_the_machines():
    """THE DEFECT THIS OWNS, and the director named it: *"You have labelled BST as UTC twice this
    week."*

    At 23:30 UTC on Sunday in British Summer Time it is already 00:30 MONDAY in London. A rhythm
    reading a UTC date fires Monday's step on Sunday evening — his anchor, missed by an hour, in the
    direction that looks like it worked.

    MUTATION: `datetime.now(timezone.utc).date()` and this fires.
    """
    sunday_night_utc = datetime(2026, 9, 6, 23, 30, tzinfo=ZoneInfo("UTC"))
    assert sunday_night_utc.date().weekday() == 6, "precondition: it is Sunday in UTC"
    assert wr.london_today(sunday_night_utc) == date(2026, 9, 7), (
        "the rhythm read the machine's day instead of the director's"
    )
    assert wr.london_today(sunday_night_utc).weekday() == wr.MONDAY


def test_the_clock_is_never_a_parsed_abbreviation():
    """`date -d "... BST"` resolves to BANGLADESH Standard Time (UTC+6) and put five hours of error
    on a live page this week. The zone is named, not parsed. MUTATION: swap `Europe/London` for a
    fixed offset and this fires in winter or in summer, whichever the offset is wrong for."""
    summer = wr.london_today(datetime(2026, 7, 1, 23, 30, tzinfo=ZoneInfo("UTC")))
    winter = wr.london_today(datetime(2026, 12, 1, 23, 30, tzinfo=ZoneInfo("UTC")))
    assert summer == date(2026, 7, 2), "BST is UTC+1; the London day had already rolled over"
    assert winter == date(2026, 12, 1), "GMT is UTC+0; it had not"


def test_the_next_step_is_strictly_after_today():
    """Closing a step on its own due date must not arm the next one for the same day. MUTATION:
    drop the `or 7` and a Monday close arms Monday, so the week collapses to one day."""
    monday = date(2026, 9, 7)
    assert wr.next_weekday_after(monday, wr.FRIDAY) == date(2026, 9, 11)
    assert wr.next_weekday_after(monday, wr.MONDAY) == date(2026, 9, 14), (
        "closing Monday armed Monday again — the same day, not the next one"
    )


# ── the chain ────────────────────────────────────────────────────────────────────────────────────

def test_closing_a_step_is_the_only_thing_that_arms_the_next(rhythm):
    """THE REQUIREMENT: *"Each step fires from the one before it, not from me remembering."*

    Monday's close arms Friday; Friday's close arms the following Monday. Nothing else arms
    anything — there is no calendar here that says "Friday happens on Fridays".

    MUTATION: arm the next step from the tick instead of from the close, and this fires — the tick
    would advance the baton while Monday's work sat undone, which is the rhythm marking its own
    homework.
    """
    wr.tick(now=_at(2026, 9, 4))                       # bootstrap, a Friday
    assert wr.read_baton()["step"] == wr.MONDAY_STEP

    armed = wr.close(wr.MONDAY_STEP, now=_at(2026, 9, 7))
    assert armed["step"] == wr.FRIDAY_STEP
    assert armed["due_on"] == "2026-09-11"
    assert armed["armed_by"] == wr.MONDAY_STEP, "the chain does not record who armed it"

    armed = wr.close(wr.FRIDAY_STEP, now=_at(2026, 9, 11))
    assert armed["step"] == wr.MONDAY_STEP and armed["due_on"] == "2026-09-14"
    assert armed["armed_by"] == wr.FRIDAY_STEP


def test_a_tick_alone_never_advances_the_baton(rhythm):
    """THE NULL CONTROL for the leg above. If ticking advanced the step, every leg about the chain
    would still pass while the rhythm marked itself done. Seven ticks, no close, same step."""
    wr.tick(now=_at(2026, 9, 4))
    before = wr.read_baton()
    for day in range(5, 12):
        wr.tick(now=_at(2026, 9, day))
    after = wr.read_baton()
    assert after["step"] == before["step"] and after["due_on"] == before["due_on"], (
        "a tick advanced the rhythm without the work being done"
    )


def test_closing_the_wrong_step_is_refused(rhythm):
    """Closing a step that is not the armed one would silently skip the one that is."""
    wr.tick(now=_at(2026, 9, 4))
    with pytest.raises(ValueError, match="waiting on"):
        wr.close(wr.FRIDAY_STEP, now=_at(2026, 9, 7))


# ── a step that did not fire ─────────────────────────────────────────────────────────────────────

def test_a_step_still_open_the_day_after_it_was_due_is_a_finding(rhythm):
    """THE REQUIREMENT: *"If a step has not fired when it should have, that is a finding."*

    MUTATION: make the finding branch unreachable (`today > due_on` -> `today > due_on + 7`) and
    this fires. That mutation is the shape this repo has paid for most: a branch that exists, reads
    as caution, and can never be taken."""
    wr.tick(now=_at(2026, 9, 4))
    opened = wr.tick(now=_at(2026, 9, 7))
    assert opened["action"] == "OPENED"

    late = wr.tick(now=_at(2026, 9, 8))
    assert late["action"] == "FINDING" and late["days_late"] == 1
    body = (rhythm / "staging").joinpath(late["doc"].split("/")[-1]).read_text()
    assert "**Severity:** LATENT" in body, "a finding with no severity is not in the ladder"
    assert "has not fired" in body and "2026-09-07" in body, (
        "the finding must name the step's own due date, or it cannot be discharged against it")
    assert "weekly_rhythm --close" in body, "the finding must name its own repair"


def test_the_finding_is_filed_once_not_once_a_day(rhythm):
    """A step left open for a fortnight must not mint fourteen documents. That would be the rhythm
    producing sediment — the exact failure the director forbade. MUTATION: drop the
    `finding_filed_for` guard and this fires."""
    wr.tick(now=_at(2026, 9, 4))
    wr.tick(now=_at(2026, 9, 7))
    actions = [wr.tick(now=_at(2026, 9, day))["action"] for day in (8, 9, 10, 11, 12)]
    assert actions.count("FINDING") == 1, f"one finding per due date, got {actions}"
    findings = list((rhythm / "staging").glob("SEAT_FINDING_*"))
    assert len(findings) == 1


def test_the_step_document_is_written_once(rhythm):
    """Same property on the other document. MUTATION: drop the `opened_at` guard and every tick
    rewrites the staged doc, which re-grants the seat a turn on work already in hand."""
    wr.tick(now=_at(2026, 9, 4))
    first = wr.tick(now=_at(2026, 9, 7))
    again = wr.tick(now=_at(2026, 9, 7, hour=12))
    assert first["action"] == "OPENED" and again["action"] == "WAITING"
    assert len(list((rhythm / "staging").glob("WEEKLY_RHYTHM_*"))) == 1


# ── what the ranking is given ────────────────────────────────────────────────────────────────────

def test_a_ritual_that_never_ran_is_distinguishable_from_one_that_ran_long_ago(rhythm, monkeypatch):
    """THREE STATES, and the third is the director's actual complaint: the pruning ritual was
    adopted and has NEVER fired. A mechanism that reported it as merely stale would be describing a
    smaller problem, and one that skipped it for having no artefact would miss it entirely.

    MUTATION: return `date.min` instead of None for a ritual with no evidence and this fires — it
    would read as "overdue by 700,000 days", which is a number nobody can act on."""
    monkeypatch.setattr(wr, "RITUALS", (
        {"id": "never_ran", "every_days": 30, "lane": "L", "glob": "no/such/path/*.md", "what": "x"},
        {"id": "ran_recently", "every_days": 30, "lane": "L", "glob": "docs/design/MOTHBALL_*.md",
         "what": "y"},
    ))
    rows = {r["id"]: r for r in wr.overdue_rituals(date(2026, 8, 1))}
    assert rows["never_ran"]["last_done"] is None and rows["never_ran"]["why"] == "never run"
    assert "ran_recently" not in rows, "a ritual inside its cadence is not overdue"

    later = {r["id"]: r for r in wr.overdue_rituals(date(2026, 12, 1))}
    assert later["ran_recently"]["days_over"] > 0
    assert "last run" in later["ran_recently"]["why"], "an overdue ritual must say since when"


def test_parked_work_is_found_by_its_own_open_note_not_by_a_hand_list(rhythm, tmp_path):
    """THE SUBJECT IS DERIVED. The director's own example — the mothball audit — is not overdue on
    any cadence; it is parked mid-way and its parked note says so. A registry of three ritual names
    would have missed it and would go stale the first time a fourth thing parked itself.

    MUTATION: match on filename instead of on the OPEN note and this fires — the doc that states
    nothing would be surfaced alongside the one that states what remains."""
    room = tmp_path / "docs" / "staging" / "in_progress"
    room.mkdir(parents=True)
    (room / "PARKED_WITH_A_STATED_ITEM_2026-07-29.md").write_text(
        "<!-- PARKED 2026-07-29 — OPEN: execute the verdict rows, reversible throughout. -->\n# x\n")
    (room / "PARKED_SAYING_NOTHING_2026-07-01.md").write_text("# just parked\n")

    rows = wr.parked_with_open_item(date(2026, 9, 7), root=tmp_path)
    assert [r["name"] for r in rows] == ["PARKED_WITH_A_STATED_ITEM_2026-07-29.md"]
    assert rows[0]["age_days"] == 40
    assert "execute the verdict rows" in rows[0]["open"]
    assert "-->" not in rows[0]["open"], "the raw comment terminator reached a document a person reads"


def test_the_parked_room_is_reported_as_a_count_never_as_a_list(rhythm, tmp_path):
    """120 documents in a weekly ranking is a pile, not a rhythm, and the bulk drain is already
    declined in DIRECTION.yaml's `not_now` with a reason that stands. MUTATION: return the names
    and this fires."""
    room = tmp_path / "docs" / "staging" / "in_progress"
    room.mkdir(parents=True)
    for day in range(1, 9):
        (room / f"PARKED_2026-08-0{day}.md").write_text("# x\n")
    measured = wr.parked_room(root=tmp_path)
    assert measured["documents"] == 8
    assert set(measured) == {"documents", "oldest_days"}, "the room's contents leaked into the report"


# ── it must not become the noise it replaces ─────────────────────────────────────────────────────

def test_an_unreadable_baton_is_rebuilt_and_mints_nothing(rhythm):
    """THE CONSTRAINT: *"If the rhythm starts producing findings about itself, it has failed."*

    A corrupt baton is a fault in this module, not in the work. It is rebuilt and reported in the
    tick's own return value; it must never reach the staging room.

    MUTATION: raise instead of rebuilding, or file a finding about the baton, and this fires."""
    wr.BATON.parent.mkdir(parents=True, exist_ok=True)
    wr.BATON.write_text("{ this is not json")
    result = wr.tick(now=_at(2026, 9, 4))
    assert result["action"] == "BOOTSTRAP"
    staged = (rhythm / "staging")
    assert not staged.exists() or not list(staged.glob("*.md")), (
        "a fault in the rhythm reached the staging room as a document")
    assert json.loads(wr.BATON.read_text())["step"] == wr.MONDAY_STEP


def test_six_days_in_seven_the_tick_does_nothing(rhythm):
    """The cost of the rhythm on an ordinary day is reading one file. A mechanism that watches the
    work must be cheaper than the work. MUTATION: open the step whenever the baton exists and this
    fires on the Tuesday."""
    wr.tick(now=_at(2026, 9, 4))
    for day in (5, 6):
        assert wr.tick(now=_at(2026, 9, day))["action"] == "WAITING"
    assert wr.tick(now=_at(2026, 9, 7))["action"] == "OPENED"


def test_every_disposition_is_reachable(rhythm):
    """THE HABIT THIS REPO PAID FOR THREE TIMES IN ONE AFTERNOON: when a branch exists to be taken
    rarely, assert it CAN be taken before asserting what it does. All four of BOOTSTRAP, WAITING,
    OPENED and FINDING must be producible, or some leg above is testing a permanent no-op."""
    seen = {wr.tick(now=_at(2026, 9, 4))["action"],
            wr.tick(now=_at(2026, 9, 5))["action"],
            wr.tick(now=_at(2026, 9, 7))["action"],
            wr.tick(now=_at(2026, 9, 8))["action"]}
    assert seen == {"BOOTSTRAP", "WAITING", "OPENED", "FINDING"}


def test_the_rhythm_is_live_on_the_daily_tick(monkeypatch, tmp_path):
    """ABSORPTION, not consumption. The mechanism is worth nothing if nothing calls it, and the one
    thing that must never happen is the rhythm quietly not running — which is indistinguishable from
    the prose ritual it replaces.

    THE FIRST VERSION OF THIS LEG WAS THE DEFECT IT WAS WRITTEN AGAINST. It grepped
    `daily_self_note.py` for the string `weekly_rhythm.tick()` — and the block above the call
    EXPLAINS the call, in a comment, using those exact characters. Deleting the wire entirely left
    this test green: a control satisfied by prose ABOUT the wire cannot tell the wire from the prose.
    Proven by breaking it (B7): the whole call site removed, 17 of 17 still passing.

    So it runs the tick and asserts the rhythm was CALLED. MUTATION: delete the call from
    `daily_self_note.run()` and this fires.
    """
    from background import daily_self_note

    called = []
    monkeypatch.setattr(daily_self_note, "already_ran_today", lambda now: False)
    monkeypatch.setattr(daily_self_note, "render_note", lambda *a, **k: "note")
    monkeypatch.setattr(daily_self_note, "publish", lambda *a, **k: None)
    monkeypatch.setattr(wr, "BATON", tmp_path / "baton.json")
    monkeypatch.setattr(wr, "STAGING", tmp_path / "staging")
    monkeypatch.setattr(wr, "tick", lambda *a, **k: called.append(True) or {"action": "WAITING"})

    assert daily_self_note.run(_runner=lambda *a: ("abc", "")) == "published"
    assert called, (
        "the daily 07:00 local tick did not call the weekly rhythm, so nothing fires it and it is "
        "exactly the prose ritual it was built to replace"
    )


def test_the_rhythm_can_never_take_the_daily_note_down(monkeypatch, tmp_path):
    """It is a passenger on someone else's tick. An observer that can red its subject is the defect
    this project names first. MUTATION: remove the try/except around the call and this fires."""
    from background import daily_self_note

    monkeypatch.setattr(daily_self_note, "already_ran_today", lambda now: False)
    monkeypatch.setattr(daily_self_note, "render_note", lambda *a, **k: "note")
    monkeypatch.setattr(daily_self_note, "publish", lambda *a, **k: None)
    monkeypatch.setattr(wr, "tick", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))

    assert daily_self_note.run(_runner=lambda *a: ("abc", "")) == "published"


def test_friday_can_find_the_monday_it_is_reviewing(rhythm):
    """Friday's whole job is reviewing against Monday's ranking, so it must be able to FIND it.

    LOOKED UP BY ITS OWN WEEK, never by "the newest Monday document". A Friday review that ran late
    must review the week it belongs to; taking the newest would silently review a week that started
    after it. MUTATION: return the newest match instead and this fires.
    """
    staging = rhythm / "staging"
    staging.mkdir(parents=True, exist_ok=True)
    mine = staging / "WEEKLY_RHYTHM_MONDAY_RANKING_2026-09-07.md"
    mine.write_text("# mine\n")
    (staging / "WEEKLY_RHYTHM_MONDAY_RANKING_2026-09-14.md").write_text("# a later week\n")

    assert wr.monday_document_for(date(2026, 9, 11), staging=staging) == mine
    assert wr.monday_document_for(date(2026, 9, 18), staging=staging) == (
        staging / "WEEKLY_RHYTHM_MONDAY_RANKING_2026-09-14.md"), "each Friday takes its own Monday"
    assert wr.monday_document_for(date(2026, 9, 25), staging=staging) is None, (
        "a Friday with no Monday behind it must say so, not borrow another week's ranking")


def test_a_friday_with_no_monday_says_so_rather_than_inventing_one(rhythm):
    """The fail-closed direction. A review with no ranking to review IS the finding, and the
    document must say that rather than inviting a reconstruction from memory."""
    wr.tick(now=_at(2026, 9, 4))
    wr.close(wr.MONDAY_STEP, now=_at(2026, 9, 7))          # closed without ever opening a document
    opened = wr.tick(now=_at(2026, 9, 11))
    assert opened["action"] == "OPENED"
    body = (rhythm / "staging" / opened["doc"].split("/")[-1]).read_text()
    assert "NOT FOUND" in body and "reconstructing it from memory" in body


def test_mondays_document_carries_a_place_for_the_ranking(rhythm):
    """The ranking lives HERE, not in DIRECTION.yaml, whose focus expires in 12 hours. MUTATION:
    drop the ranking section and Monday produces a briefing with nowhere to write the answer."""
    wr.tick(now=_at(2026, 9, 4))
    opened = wr.tick(now=_at(2026, 9, 7))
    body = (rhythm / "staging" / opened["doc"].split("/")[-1]).read_text()
    assert "## The ranking for this week" in body
    assert "### Deliberately not this week, and why" in body
    assert "FOCUS_MAX_AGE_HOURS" in body, (
        "the document must say why the ranking is not in DIRECTION.yaml, or the next reader moves it "
        "there and it expires by Monday evening")
