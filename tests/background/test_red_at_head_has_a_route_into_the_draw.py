"""A CONTROL THAT REPORTS AND CANNOT BE DRAWN IS DECORATION.

Director, 2026-09-02: *"Why hasn't the 830 been fixed? My reading: the HEAD-green census reports
and nothing draws it. Twelve, seventeen, thirty-three and now 830 — each announced, none worked,
while everything with a route into the draw gets done. Same shape as the reaper built in July and
never called. … Red tests at HEAD need a way into the queue with the same standing as a class
register — a named subject, a live baseline, and an end state where zero means zero."*

Three defects, one per property he named, and each test below fails if its own is reintroduced.

  NAMED SUBJECT.  The census paged a COUNT and listed ten of 830. Its full list went to a systemd
                  journal nothing reads, and no artefact kept it — so there was never anything to
                  pick up, only a number to worry about.
  LIVE BASELINE.  `head_red_baseline.json` was written 2026-08-12 and holds `known_red: []`. With
                  an empty acceptance list "not on the list" means "red", so **"newly failing" was
                  false in every message this control has ever sent** — including all four the
                  director listed back.
  ZERO IS ZERO.   Nothing persisted the observation, so no red had an age, no red had a subject,
                  and there was no state from which "fixed" could be read.

And the property that must SURVIVE the fix: the acceptance list stays human-written, because *"a
control that absorbs its own new failures into its own baseline cannot fail."* The machine writes
what it SAW; only a person writes what is FORGIVEN.
"""
from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone

from background import head_red_register as reg
from background import staging_rooms as sr
from tools import head_green_census as census

T0 = datetime(2026, 9, 1, 3, 30, tzinfo=timezone.utc)


def _run(store, failures, *, at, sha="abc123456", passed=100):
    return reg.record(failures, head_sha=sha, passed=passed, now=at, store=store)


def _empty():
    return {"runs": [], "tests": {}}


# ── A NAMED SUBJECT ─────────────────────────────────────────────────────────────────────────
def test_the_register_names_every_owed_test_not_just_a_count():
    """MUTATION: render only the count and this fails. A count is not actionable — it is the
    thing the director could only worry about."""
    store = _run(_empty(), ["tests/a.py::test_one", "tests/b.py::test_two"], at=T0)
    text = reg.render(store, accepted=[])
    assert "tests/a.py::test_one" in text and "tests/b.py::test_two" in text


def test_when_it_cannot_list_them_all_it_says_so_and_names_the_store():
    """A summary that hides its own truncation turns a named subject back into a count."""
    many = ["tests/m.py::test_{}".format(i) for i in range(reg.MAX_LISTED + 25)]
    text = reg.render(_run(_empty(), many, at=T0), accepted=[])
    assert "more not listed" in text and "head_red_observed.json" in text


def test_it_groups_by_module_because_a_whole_red_module_is_usually_one_cause():
    """820 of the 830 were in `tests/background/`, where four autouse fixtures each take
    `tmp_path` — one environmental cause, not 820 defects. A register that only listed node ids
    would hide the single most useful fact about the failure."""
    store = _run(_empty(), ["tests/x.py::a", "tests/x.py::b", "tests/y.py::c"], at=T0)
    grouped = reg.by_module(reg.owed(store, []))
    assert grouped == {"tests/x.py": ["tests/x.py::a", "tests/x.py::b"], "tests/y.py": ["tests/y.py::c"]}


# ── A LIVE BASELINE ─────────────────────────────────────────────────────────────────────────
def test_a_red_that_survives_runs_accrues_an_age():
    """The recurrence signal, and the census had none: every night's message was identical in
    shape whether a test broke last night or three weeks ago.

    MUTATION: reset `runs_red` on each run and this fails.
    """
    store = _empty()
    for day in range(3):
        store = _run(store, ["tests/a.py::old", "tests/b.py::new"] if day else ["tests/a.py::old"],
                     at=T0 + timedelta(days=day))
    assert store["tests"]["tests/a.py::old"]["runs_red"] == 3
    assert store["tests"]["tests/b.py::new"]["runs_red"] == 2
    assert store["tests"]["tests/a.py::old"]["first_seen"] < store["tests"]["tests/b.py::new"]["first_seen"]


def test_the_debt_order_is_longest_standing_first():
    store = _empty()
    for day in range(4):
        failing = ["tests/a.py::old"] + (["tests/b.py::recent"] if day >= 3 else [])
        store = _run(store, failing, at=T0 + timedelta(days=day))
    ranked = [n for n, _ in reg.oldest_first(store, reg.owed(store, []))]
    assert ranked[0] == "tests/a.py::old"


def test_a_test_that_goes_green_stops_being_owed_but_keeps_its_record():
    """Both halves matter: it must leave the draw (or zero can never be reached), and its history
    must survive (or "this one came back" is inexpressible)."""
    store = _run(_run(_empty(), ["tests/a.py::x"], at=T0), [], at=T0 + timedelta(days=1))
    assert reg.owed(store, []) == []
    assert store["tests"]["tests/a.py::x"]["runs_red"] == 1


def test_every_run_records_its_own_clock_and_head():
    """'Live' means each observation says WHEN and AGAINST WHAT. The file it replaces carried one
    undated list from three weeks earlier."""
    store = _run(_empty(), ["tests/a.py::x"], at=T0, sha="deadbeef1")
    assert store["runs"][-1]["head"] == "deadbeef1"
    assert store["runs"][-1]["at"].startswith("2026-09-01")


# ── ZERO MEANS ZERO ─────────────────────────────────────────────────────────────────────────
def test_nothing_owed_leaves_the_draw_entirely(tmp_path, monkeypatch):
    """THE END STATE, enforced in the splice rather than promised in the document.

    MUTATION: splice the register unconditionally and this fails — the queue gains a permanent
    item that can never be discharged, which is the accretion `KIND_REFERENCE` was invented to
    stop and the reason a register was not drawable in the first place.
    """
    ref = tmp_path / sr.REFERENCE_DIRNAME
    ref.mkdir(parents=True)
    (ref / reg.REGISTER_NAME).write_text("# [REGISTER] Tests red at HEAD\n")
    monkeypatch.setattr(reg, "drawable", lambda root=None: [])
    assert [i for i in sr._with_the_head_red_register(tmp_path, []) if i.kind == sr.KIND_HEAD_RED] == []
    monkeypatch.setattr(reg, "drawable", lambda root=None: ["tests/a.py::x"])
    drawn = [i for i in sr._with_the_head_red_register(tmp_path, []) if i.kind == sr.KIND_HEAD_RED]
    assert len(drawn) == 1 and drawn[0].rank == sr.ORDER[sr.KIND_HEAD_RED]


def test_the_register_says_zero_means_zero_when_nothing_is_owed():
    text = reg.render(_run(_empty(), [], at=T0), accepted=[])
    assert "ZERO MEANS ZERO" in text


def test_it_ranks_below_a_class_register_and_above_a_finding():
    """A class register argues about a pattern still producing instances; this is a list of things
    broken right now at committed HEAD. It beats a finding because a finding describes something
    that MIGHT be wrong and this is something that IS."""
    assert sr.ORDER[sr.KIND_CLASS_DEBT] < sr.ORDER[sr.KIND_HEAD_RED] < sr.ORDER[sr.KIND_FINDING]


def test_the_register_lives_in_reference_and_never_migrates():
    """Its ROOM must not change with its RANK. A document that moves folders as its state changes
    is how the class register came to need a lookup spanning two rooms."""
    assert sr.room_for(sr.kind_of(reg.REGISTER_NAME)) == sr.REFERENCE_DIRNAME
    assert sr.room_for(sr.KIND_HEAD_RED) == sr.REFERENCE_DIRNAME


# ── THE PROPERTY THAT MUST SURVIVE: the machine cannot forgive itself ───────────────────────
def test_recording_an_observation_never_reduces_what_is_owed():
    """*"A control that absorbs its own new failures into its own baseline cannot fail."* The
    observation store is machine-written and the acceptance list is not, so the ONLY input that
    shrinks the owed set is a human decision.

    MUTATION: have `record` add the run's failures to the accepted set and this fails.
    """
    store = _run(_empty(), ["tests/a.py::x", "tests/b.py::y"], at=T0)
    assert len(reg.owed(store, accepted=[])) == 2
    assert len(reg.owed(store, accepted=["tests/a.py::x"])) == 1
    # `record` may not write ANY file: it returns the new store and the caller saves it. That is
    # what keeps the whole ageing rule testable without a filesystem, and it is also the structural
    # reason this function cannot reach the acceptance list.
    assert ".write_text" not in inspect.getsource(reg.record)
    # And exactly two functions in the module write anything at all, to the two paths this
    # module owns. The register PROSE names the acceptance file on purpose — a reader has to be
    # told where to accept a test — so the check is on what the code WRITES, not what it mentions.
    import ast
    writers = {n.name for n in ast.walk(ast.parse(inspect.getsource(reg)))
               if isinstance(n, ast.FunctionDef) and ".write_text" in ast.unparse(n)}
    assert writers == {"save_observed", "write_register"}, writers


def test_an_unproven_run_is_not_allowed_to_mark_every_red_as_fixed():
    """A run whose suite did not execute has observed no test to be green. Folding its empty
    failure list in would clear the whole register on an OUTAGE — a control booking its own
    downtime as progress.

    MUTATION: drop the UNPROVEN guard in `_record_observation` and this fails.
    """
    note = census._record_observation({"status": "UNPROVEN", "failures": [], "passed": None})
    assert "observed nothing" in note


def test_a_register_that_cannot_be_written_is_reported_not_swallowed(monkeypatch):
    """The census's verdict must not depend on its artefact — and a silent failure here would
    recreate, one layer down, the exact defect this register exists to fix."""
    monkeypatch.setattr(reg, "record", lambda *a, **k: (_ for _ in ()).throw(OSError("disk")))
    note = census._record_observation({"status": "NEW_RED", "failures": ["a::b"], "passed": 1})
    assert "register NOT updated" in note and "OSError" in note


# ── AND THE WORD THAT WAS FALSE EVERY NIGHT ─────────────────────────────────────────────────
def test_the_verdict_states_both_numbers_and_names_each_population():
    """"830 test(s) newly failing" against an empty acceptance list is not a delta — every red is
    "not on the list", every night, forever. Four such messages read as a rising delta when they
    were absolute counts wearing a delta's word.

    MUTATION: restore the "newly failing" wording and this fails.
    """
    status, reason = census.verdict(
        {"new_red": ["a::x", "b::y"], "still_red": ["c::z"], "fixed": []}, passed_count=10)
    assert status == "NEW_RED"
    assert "newly failing" not in reason
    assert "neither fixed nor accepted" in reason
    assert "accepted by name" in reason
    assert census.HEAD_RED_REGISTER_NAME in reason, "the message must point at the named subjects"
