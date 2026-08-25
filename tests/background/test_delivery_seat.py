"""R15 contract for the delivery seat — the periodic session that ORIENTS instead of executing.

Design: `docs/design/THE_DELIVERY_SEAT.md`. Director, 2026-08-25: *"What you don't have is
anything that orients ... My advisor and I have been doing that in a chat window, by hand. That's
the most expensive way it could possibly be done and it stops now."*

WHAT THESE TESTS ARE ACTUALLY GUARDING. A thing that decides what the machine works on is exactly
the shape of component that goes wrong quietly. Three failure modes, and every test below is one
of them:

  1. IT STARTS WRITING CODE. Then it is a second writer on a tree that already documents three,
     and the cheap-to-correct output (direction) has become the expensive kind.
  2. IT STARTS SETTING TARGETS. Then the work bends toward a number the machine chose for itself,
     which is R12's entire subject and the inversion this project exists to avoid.
  3. IT STOPS BITING, AND NOTHING SAYS SO. `d7d36b46a` records two soft guards composing into a
     no-op while an atom sat through 1,307 unchanged draws. A steer that quietly does nothing is
     indistinguishable, from outside, from one that was taken.

The fourth mode — it gates the draw and empties the feasible set — is a Rule-0 violation and is
prevented by construction rather than by policy: direction MULTIPLIES weights and the multiplier
is never below 1.0.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from background import direction as d
from background import delivery_seat as seat

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)


def _record(**over) -> dict:
    base = {
        "version": 1,
        "oriented_at": NOW.isoformat(),
        "thesis_read": "the belief is finally load-bearing and the baseline is not yet credible",
        "focus": [{"id": "C1_pricing", "what": "a credible flat control", "why": "the arm cannot"
                                                                                " be scored against a straw man"}],
        "not_now": [{"what": "wiring the value arm", "why": "it would be scored against a control"
                                                            " that is not average behaviour"}],
    }
    base.update(over)
    return base


def _write(tmp_path, record) -> "object":
    import yaml
    path = tmp_path / "DIRECTION.yaml"
    path.write_text(yaml.safe_dump(record), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# Mode 3 (and Rule 0): a weight, never a gate                                  #
# --------------------------------------------------------------------------- #

def test_direction_can_NEVER_make_an_atom_harder_to_draw():
    """THE RULE-0 PROPERTY, and the reason this is a weight rather than a filter. An empty
    feasible set is a defect in the dials; a filter is a dial that can empty one. A multiplier
    that is always >= 1.0 cannot.

    MUTATION (must fire): return anything below 1.0 for a non-focus atom.
    """
    focus = ("A", "B", "C", "D", "E")
    for atom in ("A", "B", "C", "D", "E", "Z", ""):
        assert d.focus_multiplier(atom, focus) >= 1.0


def test_direction_cannot_shorten_the_candidate_list():
    """The supervisor builds `candidates` and THEN asks for weights, so this function is
    structurally unable to change who is eligible. Pinned anyway, because the obvious
    'improvement' to this design is to filter."""
    candidates = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
    weights = [1.0, 5.0, 2.0]

    assert len(d.focus_weights(candidates, weights)) == len(candidates)


def test_a_named_atom_actually_becomes_more_likely_and_the_steer_BITES(tmp_path):
    """A steer too polite to change a draw is the failure mode of this whole design. Rank 1 is
    four times its dial, which is enough to beat a one-dial difference and not enough to make the
    rest of the map unreachable.

    MUTATION (must fire): set every multiplier to 1.0 ("neutral"), which is what a cautious edit
    would do and would leave a mechanism that runs and does nothing.
    """
    path = _write(tmp_path, _record(focus=[{"id": "B", "what": "x", "why": "y"}]))
    candidates = [{"id": "A"}, {"id": "B"}]
    biased = d.focus_weights(candidates, [3.0, 1.0], path=path, now=NOW)

    assert biased[0] == 3.0, "an atom the direction does not name must keep its own weight exactly"
    assert biased[1] > 3.0, "the named atom is not preferred over a higher-dialled one"


def test_focus_that_was_never_DRAWN_is_reported_rather_than_assumed():
    """THE CONTROL ON THE CONTROL. Every orientation records whether the previous one's focus
    reached the draw, because a steer that silently does nothing looks identical to one that was
    followed.

    MUTATION (must fire): return `steered: True` unconditionally.
    """
    missed = d.focus_was_drawn(("A", "B"), ["C1", "D2"])
    hit = d.focus_was_drawn(("A", "B"), ["A", "D2"])

    assert missed["steered"] is False and "NONE of it was drawn" in missed["note"]
    assert hit["steered"] is True and hit["drawn"] == ["A"]


# --------------------------------------------------------------------------- #
# Fail-soft: advice that goes missing must not touch the draw                  #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("payload", [
    "",                                   # empty file
    "this: [is: not: yaml",               # malformed
    "version: 1\nfocus: []\nnot_now: []", # structurally invalid
    "- a\n- list\n- not\n- a\n- mapping",
])
def test_a_BROKEN_direction_record_leaves_the_draw_byte_identical(tmp_path, payload):
    """DELIBERATELY THE OPPOSITE OF THE REST OF THIS TREE. Most controls here fail CLOSED because
    an unavailable check is a failed check. Direction is not a check -- it is advice -- and advice
    that wedges the draw when it goes missing is worse than no advice.

    MUTATION (must fire): raise instead of returning the original weights.
    """
    path = tmp_path / "DIRECTION.yaml"
    path.write_text(payload, encoding="utf-8")
    weights = [1.0, 7.0, 3.0]

    assert d.focus_weights([{"id": "A"}, {"id": "B"}, {"id": "C"}], weights, path=path) == weights
    assert d.current_focus(path) == ()


def test_a_MISSING_record_is_not_an_error(tmp_path):
    missing = tmp_path / "nothing-here.yaml"

    assert d.read_direction(missing) is None
    assert d.current_focus(missing) == ()


def test_direction_EXPIRES_so_stale_advice_stops_steering_on_its_own(tmp_path):
    """Stale direction is worse than none: it points at what mattered yesterday with all the
    confidence of what matters now. It has to expire by itself, because the failure mode is
    precisely that nobody is watching.

    MUTATION (must fire): drop the age check from `current_focus`.
    """
    old = NOW - timedelta(hours=d.FOCUS_MAX_AGE_HOURS + 1)
    path = _write(tmp_path, _record(oriented_at=old.isoformat()))

    assert d.current_focus(path, now=NOW) == ()
    assert d.focus_weights([{"id": "C1_pricing"}], [2.0], path=path, now=NOW) == [2.0]

    fresh = _write(tmp_path, _record())
    assert d.current_focus(fresh, now=NOW) == ("C1_pricing",)


# --------------------------------------------------------------------------- #
# Mode 2: it may say what to work on, never what counts as success             #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("key", sorted(d.FORBIDDEN_KEYS))
def test_a_record_carrying_a_TARGET_is_refused_whatever_it_is_called(key):
    """THE ONE DISTINCTION THE DESIGN HANGS OFF (THE_DELIVERY_SEAT.md section 2). Priority is a
    judgement about attention and is what a delivery seat is for. A target is a number the work
    then bends toward, which is R12.

    MUTATION (must fire): empty `FORBIDDEN_KEYS`, or check only the top level.
    """
    problems = d.validate(_record(focus=[{"id": "A", "what": "x", "why": "y", key: 12}]))

    assert any("target-shaped" in p for p in problems), problems


def test_the_refusal_reaches_ARBITRARY_depth():
    nested = _record(stretch_reviewed={"since": "x", "detail": {"nested": {"kpi": 3}}})

    assert any("target-shaped" in p for p in d.validate(nested))


def test_a_measurement_quoted_in_a_WHY_is_not_a_target():
    """The check is on the KEY, not the prose. Forbidding numbers outright would only buy vagueness,
    and a `why` that cites what was measured is exactly what good direction looks like."""
    assert d.validate(_record(focus=[
        {"id": "A", "what": "credible control",
         "why": "the belief error is +0.5pp and the control charges GBP 6.20/yr"}])) == []


def test_a_direction_that_REJECTED_NOTHING_is_refused():
    """The director's own instruction, made mechanical: *"record the options you considered and
    why you chose as you did. That record is what I review, and it's what makes it safe for you
    not to ask."* A record listing only what was chosen hides the judgement it exists to expose.

    MUTATION (must fire): accept an empty `not_now`.
    """
    problems = d.validate(_record(not_now=[]))

    assert any("rejected nothing" in p for p in problems), problems


def test_a_direction_that_NAMES_NO_WORK_is_refused():
    assert any("names no work" in p for p in d.validate(_record(focus=[])))


def test_the_refusal_says_WHY_rather_than_returning_a_boolean():
    """A control that refuses and cannot say why is the fail-silent shape this project keeps
    finding in its own controls. The seat pages with these strings and the page prints them."""
    problems = d.validate({"version": 1})

    assert len(problems) >= 3 and all(isinstance(p, str) and p for p in problems)


# --------------------------------------------------------------------------- #
# Mode 1: it may not write code                                                #
# --------------------------------------------------------------------------- #

def test_the_write_scope_is_CLOSED_and_holds_no_code_path():
    """`git add` takes this tuple and nothing else, so anything the orienting session touched
    outside it is simply not in its commit. The pathspec is the mechanism -- the same reason
    CLAUDE.md gives for committing by pathspec under concurrent writers.

    MUTATION (must fire): add a code path to `WRITE_SCOPE`.
    """
    assert set(d.WRITE_SCOPE) == {
        "docs/direction/DIRECTION.yaml",
        "docs/direction/decisions.jsonl",
        "site/data/delivery.json",
    }
    for path in d.WRITE_SCOPE:
        assert not path.endswith(".py")
        assert not path.startswith(("company/", "saas/", "simulation/", "sim/", "tests/",
                                    "background/", "tools/"))


def test_the_seat_COMMITS_only_its_write_scope():
    """Source-level, because the alternative is running a commit inside a test. The defect this
    guards is a session that edits code and a seat that then sweeps it up -- the exact
    cross-lane sweep CLAUDE.md documents three separate times.

    MUTATION (must fire): replace the pathspec with `git add -A`.
    """
    import inspect

    source = inspect.getsource(seat.commit_direction)

    assert "direction_mod.WRITE_SCOPE" in source
    assert "-A" not in source and "--all" not in source


def test_out_of_scope_writes_are_REPORTED_and_never_reverted():
    """Reverting would stamp on whatever concurrent lane is legitimately mid-edit, which is the
    second-writer problem one worse rather than solved."""
    import inspect

    source = inspect.getsource(seat.out_of_scope_writes)

    assert "checkout" not in source and "reset --hard" not in source and "clean" not in source


# --------------------------------------------------------------------------- #
# Severance: the draw reads a file, never the thing that wrote it              #
# --------------------------------------------------------------------------- #

def test_the_supervisor_reads_DIRECTION_and_never_the_SEAT():
    """`background/daily_self_note.py` carries a HARD LAW that a self-measurement may never touch
    the draw. This seat touches the draw on purpose, so the severance it keeps is a different one:
    the draw imports the READ side and has no path to the session that writes it.

    MUTATION (must fire): import `delivery_seat` in the supervisor for convenience.
    """
    import re
    from pathlib import Path

    source = Path(seat.PROJECT_DIR / "background" / "supervisor.py").read_text(encoding="utf-8")
    # IMPORT LINES ONLY. A bare substring search reds on the comment that EXPLAINS the severance,
    # which would make documenting the rule break the rule -- the same shape as the site lane's
    # `_strip_comments` lesson (a commented-out call must not count as wiring, and a comment
    # naming a module must not count as importing it).
    imports = [ln for ln in source.splitlines()
               if re.match(r"\s*(import |from )", ln)]

    assert "from background import direction as _direction" in source
    assert not [ln for ln in imports if "delivery_seat" in ln], (
        "the supervisor imports the session that WRITES direction; it may only read the record"
    )


def test_EVERY_weighted_draw_reads_direction_not_just_the_build_lane():
    """R10: a class fix, not an instance fix. There are four dial-weighted draws -- BUILD, the two
    idle DISCOVER/FRAME lanes and SITE -- and direction that steered only one of them would be a
    steering wheel connected to one wheel.

    MUTATION (must fire): wire only the BUILD draw.
    """
    from pathlib import Path

    source = Path(seat.PROJECT_DIR / "background" / "supervisor.py").read_text(encoding="utf-8")

    assert source.count("_direction.focus_weights(candidates, weights)") == 4
    assert source.count('weights = [max(1, a.get("dial_inherited", 1)) for a in candidates]') == 4


# --------------------------------------------------------------------------- #
# The skip rule                                                                #
# --------------------------------------------------------------------------- #

def _brief(**over) -> dict:
    base = {
        "substantive_count": 0, "levels_moved": {}, "director_inputs": [],
        "findings": {"available": True, "blocking": []},
        "live_direction_age_hours": 1.0,
    }
    base.update(over)
    return base


def test_a_QUIET_stretch_is_SKIPPED_and_the_skip_says_why():
    """R5: state transitions, not heartbeats. Orienting over a stretch with nothing in it produces
    a confident restatement of the last direction with a fresh timestamp, which reads downstream
    exactly like a decision. The skip is recorded with its reason, never silent.

    MUTATION (must fire): always orient.
    """
    material, why = seat.is_material(_brief())

    assert material is False
    assert "nothing this stretch to orient on" in why


@pytest.mark.parametrize("brief,expected", [
    (_brief(substantive_count=3), "substantive commit"),
    (_brief(levels_moved={"A": [1, 2]}), "level(s) moved"),
    (_brief(director_inputs=["from_rich_x.md"]), "the director spoke"),
    (_brief(findings={"available": True, "blocking": ["x.md"]}), "BLOCKING"),
    (_brief(live_direction_age_hours=None), "no live direction"),
    (_brief(live_direction_age_hours=99.0), "expired"),
])
def test_every_material_change_WAKES_it(brief, expected):
    material, why = seat.is_material(brief)

    assert material is True and expected in why


def test_an_EXPIRED_direction_is_itself_a_reason_to_orient():
    """Otherwise the steer disarms silently: the record ages out, the draw quietly reverts to
    unbiased, and nothing ever says the seat stopped steering."""
    assert seat.is_material(_brief(live_direction_age_hours=99.0))[0] is True


# --------------------------------------------------------------------------- #
# The record                                                                   #
# --------------------------------------------------------------------------- #

def test_the_drawn_atom_check_reads_the_DRAWS_OWN_TRACKER_not_commit_subjects(monkeypatch, tmp_path):
    """THE CONTROL ALMOST BECAME THE DEFECT IT WATCHES FOR. The first version of this took the
    first word of each commit subject as an atom id -- on this project that is "company:" or
    "world:" and never an atom id, so the steer-effectiveness check would have reported "focus
    never drawn" every single time, and the one control designed to catch a no-op steer would
    itself have been one.

    `docs/observability/.atom_stall_tracker.json` already carries `last_drawn_at` per atom because
    the anti-livelock guard needs it, so nothing new is measured for this.

    MUTATION (must fire): infer drawn atoms from commit subjects again.
    """
    import json as _json
    from background import supervisor

    tracker = tmp_path / ".atom_stall_tracker.json"
    now = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)
    tracker.write_text(_json.dumps({
        "RECENT": {"last_drawn_at": (now - timedelta(minutes=30)).timestamp()},
        "OLD": {"last_drawn_at": (now - timedelta(days=9)).timestamp()},
        "MALFORMED": "not a row",
    }), encoding="utf-8")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tracker)

    assert seat.atoms_drawn_since(now - timedelta(hours=2)) == ["RECENT"]


def test_a_MISSING_draw_tracker_reports_nothing_drawn_rather_than_crashing(monkeypatch, tmp_path):
    """It under-reports rather than over-reports, which is the safe direction for a control whose
    job is to notice a steer that is NOT biting: a missing tracker makes the seat MORE likely to
    say the steer failed, never less."""
    from background import supervisor

    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / "absent.json")

    assert seat.atoms_drawn_since(NOW) == []


def test_the_decision_log_is_APPEND_ONLY(tmp_path):
    path = tmp_path / "decisions.jsonl"
    d.append_decision({"at": "1", "outcome": "skipped"}, path)
    d.append_decision({"at": "2", "outcome": "oriented"}, path)

    assert len(path.read_text(encoding="utf-8").strip().splitlines()) == 2
    assert [r["at"] for r in d.read_decisions(path=path)] == ["2", "1"]


def test_a_CORRUPT_line_does_not_blank_the_record(tmp_path):
    """A page that shows nothing because one line is malformed reads, to a director, exactly like
    a machine that did nothing."""
    path = tmp_path / "decisions.jsonl"
    path.write_text('{"at": "1"}\nnot json at all\n{"at": "2"}\n', encoding="utf-8")

    assert [r["at"] for r in d.read_decisions(path=path)] == ["2", "1"]


def test_the_brief_assembles_from_REAL_state_without_spawning_anything():
    """`--dry-run` must be genuinely dry: it reads git, the staging root and the map, decides
    whether it WOULD orient, and spawns nothing.

    MUTATION (must fire): let the dry run reach `run_session`.
    """
    import inspect

    source = inspect.getsource(seat.orient)
    dry_branch = source[source.index("if dry_run:"):source.index("before =")]

    assert "run_session" not in dry_branch
    assert "would-orient" in dry_branch


def test_the_page_answers_the_DIRECTORS_FOUR_QUESTIONS_and_not_a_fifth():
    """*"I want to open one page and know what the machine did, what it decided, what it got
    wrong, and what it's doing next."* Four questions, four keys, in that order.

    MUTATION (must fire): rename or drop one, or bolt a fifth panel onto the feed.
    """
    from tools.generate_delivery_page import build

    payload = build()
    keys = [k for k in payload if k.startswith("what")]

    assert keys == ["what_it_did", "what_it_decided", "what_it_got_wrong", "what_next"]


def test_an_empty_wrong_panel_says_WHICH_kind_of_empty_it_is():
    """A machine reporting no mistakes is either not looking or not saying, and both read
    identically from outside."""
    from tools.generate_delivery_page import what_it_got_wrong

    panel = what_it_got_wrong()

    assert "entries" in panel
    if not panel["entries"]:
        assert panel["empty_means"], "an empty panel that does not say why it is empty"


def test_the_page_generator_DERIVES_nothing_and_reads_the_record():
    """A generator that computes its own numbers becomes a second opinion, and the first time it
    disagrees with the record nobody can tell which is wrong."""
    import inspect

    from tools import generate_delivery_page as page

    source = inspect.getsource(page)

    assert "read_decisions" in source and "read_direction" in source
    assert "_is_substantive_file" in source, (
        "the commit split must reuse the daily self-note's classifier rather than growing a "
        "second one that will disagree with it"
    )


def test_the_seat_is_DECLARED_in_the_schedule_manifest():
    """IaC, and R15's fail-silent pattern: an orienting seat nobody schedules is the chat window
    it replaces. Reconstruct-from-repo-alone is the test.

    MUTATION (must fire): ship the units without declaring them, and the drift reconciler flags
    them as undeclared instead.
    """
    import yaml

    manifest = yaml.safe_load(
        (seat.PROJECT_DIR / "background" / "schedule_manifest.yaml").read_text(encoding="utf-8"))
    units = {u["name"]: u for u in manifest["systemd_units"]}

    assert "delivery-seat.timer" in units and units["delivery-seat.timer"]["active"] is True
    assert "delivery-seat.service" in units
    for name in ("delivery-seat.service", "delivery-seat.timer"):
        assert (seat.PROJECT_DIR / units[name]["unit_file"]).exists()


def test_the_charter_carries_the_directors_words_and_not_a_paraphrase():
    """The seat's brief is a standing duty stated by the director. A summary of it drifts; the
    verbatim text cannot."""
    flat = " ".join(seat.CHARTER.split())
    for phrase in ("translating direction into priorities",
                   "When priorities conflict, you decide rather than ask",
                   "That record is what I review",
                   "The advantage must come from INFERENCE, never from ACCESS"):
        assert phrase in flat


def test_the_charter_FORBIDS_code_edits_in_words_as_well_as_in_the_pathspec():
    """Belt and brace, and they fail differently: the pathspec stops the commit, the charter stops
    the work being done at all. Neither alone is enough -- a session told nothing would waste a
    turn writing code that is silently dropped."""
    assert "DOES NOT WRITE CODE" in seat.CHARTER
    assert "docs/direction/DIRECTION.yaml" in seat.CHARTER


def test_orientation_is_never_tiered_down_to_a_cheaper_model():
    """CLAUDE.md's routing rule puts judgement on the OPUS tier. Orientation is judgement about
    what matters; it runs on a timer, which is exactly the property that would tempt someone to
    class it as mechanical volume."""
    assert seat.MODEL == "claude-opus-5"
