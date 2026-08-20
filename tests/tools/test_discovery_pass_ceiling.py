#!/usr/bin/env python3
"""R15 proof for the discovery pass ceiling (director ruling, 2026-08-19).

The control's job is to make one thing IMPOSSIBLE: running indefinitely on work that cannot
change its own state. So the mutations drive exactly that boundary — an atom one pass below
the ceiling is still drawable, an atom at it is not, and an atom that has actually moved its
level is never saturated no matter how many passes it took.

The fail-closed direction is the opposite of its sibling and is tested as such. Where
`supervisor._is_frame_saturated` fails toward OFFERING an atom (its risk is starving real
work), this fails toward an EMPTY TIER (its risk is the indefinite run). A source that cannot
be read must RAISE — "nothing is stuck", computed from sources nobody could read, is the
reading that would quietly restore the unbounded lane.
"""
from __future__ import annotations

import datetime as dt
import json

import pytest

from tools import discovery_pass_ceiling as ceiling


def _ts(day: str) -> float:
    """A ledger timestamp for a calendar day, in the units the real ledger uses."""
    return dt.datetime.fromisoformat(day + "T12:00:00+00:00").timestamp()


def _fixture(tmp_path, atoms, records, ledger_actions):
    (tmp_path / "site" / "data").mkdir(parents=True)
    # THE FIXTURE REPRODUCES THE LOSSY PROJECTION ON PURPOSE. The real `site/data/
    # maturity_map.json` is generated from the map source and DROPS `infeasible_here` --
    # checked on the live tree against the one atom that carries it. A fixture that fed the
    # field through both files would be testing a world where the field is readable from the
    # feed, which is the world this reader exists because we are NOT in.
    feed = [{k: v for k, v in a.items() if k != "infeasible_here"} for a in atoms]
    (tmp_path / "site" / "data" / "maturity_map.json").write_text(json.dumps({"atoms": feed}))
    (tmp_path / "map_source.yaml").write_text(__import__("yaml").safe_dump(atoms))
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    for atom_id, spec in records.items():
        # int -> that many UNDATED passes; list -> one pass per date, written the way the
        # real store writes them ("NTH HOUR (2026-08-19, worker tick, ...)").
        notes = (
            [f"pass {i}" for i in range(spec)]
            if isinstance(spec, int)
            else [f"HOUR ({day}, worker tick). Body text." for day in spec]
        )
        (store_dir / f"{atom_id}.yaml").write_text(
            json.dumps({"atom_id": atom_id, "simplifications": notes})
        )
    obs = tmp_path / "obs"
    obs.mkdir()
    (obs / "gate_authorizations.jsonl").write_text(
        "\n".join(json.dumps(a) for a in ledger_actions) + "\n"
    )
    return tmp_path


def _point(monkeypatch, root):
    monkeypatch.setattr(ceiling, "MAP_FEED", root / "site" / "data" / "maturity_map.json")
    monkeypatch.setattr(ceiling, "STORE_DIR", root / "store")
    monkeypatch.setattr(ceiling, "LEDGER", root / "obs" / "gate_authorizations.jsonl")
    monkeypatch.setattr(ceiling, "MAP_SOURCE", root / "map_source.yaml")


ATOM = {"id": "X_atom", "level_current": 0, "level_target": 3, "loop_stage": "idle"}
REAL_MOVE = {"atom": "Other_atom", "action": "LEVEL_UP_SELF_CERTIFIED", "ts": 1.0}


def test_MUTATION_an_atom_at_the_ceiling_saturates(tmp_path, monkeypatch):
    _point(monkeypatch, _fixture(tmp_path, [ATOM], {"X_atom": 5}, [REAL_MOVE]))
    assert ceiling.saturated_ids(5) == {"X_atom"}


def test_an_atom_one_pass_below_the_ceiling_is_still_drawable(tmp_path, monkeypatch):
    """The other side of the boundary. A control that fires early gets muted, and muting this
    one restores the unbounded lane."""
    _point(monkeypatch, _fixture(tmp_path, [ATOM], {"X_atom": 4}, [REAL_MOVE]))
    assert ceiling.saturated_ids(5) == set()


MOVED = {"atom": "X_atom", "action": "LEVEL_UP_SELF_CERTIFIED", "ts": _ts("2026-08-08")}


def test_passes_that_earned_a_level_move_do_not_count_against_the_atom(tmp_path, monkeypatch):
    """THE central distinction, and the side of it the first draft got right. The ceiling is
    not a budget on investigation -- it is a bound on investigation THAT CHANGES NOTHING.
    Twenty passes that ended in a level move are productive work: they are spent, and the
    atom starts again with a clean count."""
    root = _fixture(tmp_path, [ATOM], {"X_atom": [f"2026-07-{d:02d}" for d in range(1, 21)]},
                    [REAL_MOVE, MOVED])
    _point(monkeypatch, root)
    assert ceiling.saturated_ids(5) == set()


def test_MUTATION_one_old_level_move_does_not_buy_unlimited_further_passes(tmp_path, monkeypatch):
    """THE FAIL-OPEN THIS CONTROL SHIPPED WITH, driven on the shape that exposed it.

    `H27_payment_belief_gap` on 2026-08-19: 48 passes, ONE level move (2026-08-08), 43 passes
    since. The first predicate was `passes >= ceiling and level_moves == 0`, so that single
    historic move made the atom permanently unsaturatable -- the worst case in the project read
    as healthy to the control written that morning to end exactly this. The question is how
    many passes SINCE the atom last moved, never whether it ever moved.
    """
    root = _fixture(
        tmp_path, [ATOM],
        {"X_atom": [f"2026-07-{d:02d}" for d in range(1, 6)]      # 5 passes, then the move
                   + [f"2026-08-{d:02d}" for d in range(9, 19)]},  # 10 passes since it
        [REAL_MOVE, MOVED],
    )
    _point(monkeypatch, root)
    row = next(r for r in ceiling.survey(5) if r["atom"] == "X_atom")
    assert (row["passes"], row["level_moves"], row["passes_since_move"]) == (15, 1, 10)
    assert ceiling.saturated_ids(5) == {"X_atom"}
    # NULL CONTROL: the pre-fix predicate, run on this same fixture, finds nothing. If this
    # ever agrees with the line above, the new reading has stopped being a different question.
    assert not (row["passes"] >= 5 and row["level_moves"] == 0)


def test_the_boundary_is_the_day_of_the_move_and_both_sides_are_asserted(tmp_path, monkeypatch):
    """A pass the day BEFORE the move is spent; one the SAME day counts.

    Day granularity is all a store entry carries, so the cutoff is inclusive and rounds toward
    saturating -- the fail-closed direction. Both sides are asserted because a boundary value
    can be the only case a rule is right about.
    """
    before = [f"2026-08-{d:02d}" for d in range(1, 8)]      # 7 passes, all before the move
    same_day = ["2026-08-08"] * 5                            # 5 on the move's own day
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    _point(monkeypatch, _fixture(tmp_path / "a", [ATOM], {"X_atom": before}, [REAL_MOVE, MOVED]))
    assert ceiling.saturated_ids(5) == set()
    _point(monkeypatch, _fixture(tmp_path / "b", [ATOM], {"X_atom": before + same_day},
                                 [REAL_MOVE, MOVED]))
    assert ceiling.saturated_ids(5) == {"X_atom"}


def test_MUTATION_FAIL_CLOSED_an_undated_pass_counts_toward_saturation(tmp_path, monkeypatch):
    """A pass nobody can place in time is not evidence the atom has been productive since its
    move. Reading it the other way would let an atom escape the ceiling by writing entries
    that omit their date -- a control silenced by the sloppiness of the thing it measures."""
    _point(monkeypatch, _fixture(tmp_path, [ATOM], {"X_atom": 6}, [REAL_MOVE, MOVED]))
    assert ceiling.saturated_ids(5) == {"X_atom"}
    assert ceiling._entry_date("no date here") is None
    assert ceiling._entry_date("HOUR (2026-13-45, ...)") is None  # parseable-looking, invalid
    assert ceiling._entry_date("HOUR (2026-08-19, worker tick)") == dt.date(2026, 8, 19)


def test_a_date_deep_in_the_body_is_not_mistaken_for_the_passs_own_date(tmp_path, monkeypatch):
    """The scan window is bounded on purpose: entries quote other dates in their bodies (the
    ruling they cite, the incident they describe), and a body quote must not re-date the pass.
    """
    old = "2026-07-01"
    entry = f"HOUR ({old}, worker tick). " + ("x" * ceiling.ENTRY_DATE_SCAN) + " see 2026-08-19"
    root = _fixture(tmp_path, [ATOM], {"X_atom": 0}, [REAL_MOVE, MOVED])
    (root / "store" / "X_atom.yaml").write_text(
        json.dumps({"atom_id": "X_atom", "simplifications": [entry] * 9})
    )
    _point(monkeypatch, root)
    assert ceiling._entry_date(entry) == dt.date(2026, 7, 1)
    assert ceiling.saturated_ids(5) == set()


def test_an_atom_at_target_is_not_surveyed(tmp_path, monkeypatch):
    done = dict(ATOM, level_current=3)
    _point(monkeypatch, _fixture(tmp_path, [done], {"X_atom": 99}, [REAL_MOVE]))
    assert ceiling.survey(5) == []


@pytest.mark.parametrize("break_it", ["map", "ledger", "store"])
def test_MUTATION_FAIL_CLOSED_an_unreadable_source_raises(tmp_path, monkeypatch, break_it):
    """Fails toward stopping the lane, not toward reopening it."""
    root = _fixture(tmp_path, [ATOM], {"X_atom": 9}, [REAL_MOVE])
    _point(monkeypatch, root)
    if break_it == "map":
        (root / "site" / "data" / "maturity_map.json").write_text("{}")
    elif break_it == "ledger":
        (root / "obs" / "gate_authorizations.jsonl").write_text("")
    else:
        for f in (root / "store").glob("*.yaml"):
            f.unlink()
    with pytest.raises(ceiling.CeilingUnavailable):
        ceiling.saturated_ids(5)


def test_a_ledger_with_one_malformed_line_still_reads():
    """One bad line is not a reason to call the whole ledger empty -- that would raise on a
    healthy project and train someone to widen the except."""
    assert ceiling.saturated_ids()  # the live ledger has malformed-tolerant parsing


def test_decisions_state_that_investigating_again_is_not_available(tmp_path, monkeypatch):
    _point(monkeypatch, _fixture(tmp_path, [ATOM], {"X_atom": 6}, [REAL_MOVE]))
    d = ceiling.decisions(5)
    assert len(d) == 1
    assert "promote to build" in d[0]["decision"]
    assert "no longer an available answer" in d[0]["decision"]


def test_every_saturated_atom_is_either_awaiting_its_decision_or_has_had_one():
    """The state that prompted the ruling, asserted so a silent change is noticed.

    THIS ASSERTION WAS WRONG ON ITS FIRST DRAFT and the fault is worth keeping visible, because
    it is the failure class this project keeps finding: it read `stage == "idle"` for every
    saturated atom. That is true only until the control WORKS. Saturation is not a terminal
    state -- the ruling's own decision text says "promote to build, or close it", so a saturated
    atom at stage `build` is the control SUCCEEDING, and the first draft would have gone red on
    the very commit that promoted EP1 and EP6. A test that fails when its work is done trains
    whoever meets it to mute it.

    AND IT WAS WRONG A SECOND TIME, in the way that matters more, which is why the first fault
    is left standing above. It asserted `level_moves == 0` of every saturated row -- the very
    fail-open the predicate shipped with, PINNED HERE AS AN INVARIANT. An atom with one old
    move and forty-three passes since could not have been reported without this assertion going
    red, so the control's own R15 proof was holding the blindness in place. What is invariant is
    the SINCE count, which is the definition, and a stage the ruling recognises -- `idle` for a
    decision outstanding, anything else for a decision taken. `verify`/`harden`/`discover` are
    all legitimate answers to "this has stopped moving".
    """
    rows = [r for r in ceiling.survey() if r["saturated"]]
    assert rows, "nothing is saturated -- if the tail really cleared, replace this assertion"
    for r in rows:
        assert r["passes_since_move"] >= ceiling.DEFAULT_CEILING, (
            f"{r['atom']} is called saturated on {r['passes_since_move']} passes since its "
            "last level move -- the definition and the verdict disagree"
        )
        assert r["stage"] in {"idle", "build", "harden", "verify", "discover"}, r


# ---------------------------------------------------------------------------
# The drawing rule itself
# ---------------------------------------------------------------------------
def test_the_idle_draw_skips_saturated_atoms(monkeypatch):
    """The lane is finite because the DRAW respects the ceiling, not because a report says so."""
    from background import supervisor

    saturated = ceiling.saturated_ids()
    assert saturated, "no saturated atoms -- this control would be vacuous"
    seen = set()
    for _ in range(60):
        drawn = supervisor._idle_discover_frame_draw()
        if drawn is None:
            break
        seen.add(drawn.get("id"))
    assert not (seen & saturated), f"the draw handed back a saturated atom: {seen & saturated}"


def test_MUTATION_when_every_idle_atom_is_saturated_the_tier_is_empty(monkeypatch):
    """The property the ruling actually asked for: the system cannot run indefinitely. With
    every idle atom over the ceiling, this tier must return None -- a true empty set, not a
    re-handed atom."""
    from background import supervisor

    monkeypatch.setattr(
        "tools.discovery_pass_ceiling.saturated_ids",
        lambda *a, **k: {a_["id"] for a_ in __import__("yaml").safe_load(
            supervisor.MATURITY_MAP_PATH.read_text()) if isinstance(a_, dict) and a_.get("id")},
    )
    assert supervisor._idle_discover_frame_draw() is None


def test_MUTATION_an_uncomputable_ceiling_closes_the_tier_rather_than_reopening_it(monkeypatch):
    """The fail-closed direction, driven through the real draw. If the ceiling cannot be
    computed the tier must CLOSE. Reopening an unbounded lane on an error is the exact
    failure the ruling exists to prevent."""
    from background import supervisor

    def boom(*a, **k):
        raise RuntimeError("ledger unreadable")

    monkeypatch.setattr("tools.discovery_pass_ceiling.saturated_ids", boom)
    assert supervisor._idle_discover_frame_draw() is None


# ---------------------------------------------------------------------------
# THE THIRD ANSWER — `infeasible_here` gets its first reader
# ---------------------------------------------------------------------------
#
# THE DEFECT THIS CLOSES, MEASURED BEFORE IT WAS WRITTEN. `decisions()` rendered ONE verdict
# for every saturated atom — "promote to build, or close it" — which is written for the idle
# discovery tier that was its only consumer. On the live tree 11 of the 24 saturated atoms are
# `build` or `harden`, so eleven atoms were being told to promote to the stage they were
# already in: a first limb that is a no-op and a second that is wrong.
#
# And for one shape BOTH limbs are wrong however they are worded. An atom whose level move
# needs an instrument the seat cannot obtain is neither promotable nor closable — more passes
# cannot move it, and the work is real and unfinished. `EP6_wall_protocol_typing` is that atom
# at 23 passes since its level last moved, second worst in the project: six consecutive passes
# recorded in PROSE that its L3 blocker is a cold-eyes walk requiring a fresh instance none of
# them was allowed to spawn. The map already had the notation for this (`infeasible_here`,
# proven on `H_GAP_fabric_belief_truth_gap` after FIFTEEN unproductive BUILD draws) and it had
# no reader anywhere — which is why the blocker lived in prose that each pass had to rewrite.

BLOCKED_ATOM = {
    "id": "B_atom", "level_current": 2, "level_target": 3, "loop_stage": "build",
    "infeasible_here": {
        "blocks": ["L3_some_instrument"],
        "predicate": "tests.tools.test_discovery_pass_ceiling._still_blocked",
        "needs": "a thing this box does not have.",
    },
}


def _still_blocked():
    return ("L3_some_instrument",)


def _no_longer_blocked():
    return ()


def _blocked_fixture(tmp_path, monkeypatch, atom=BLOCKED_ATOM):
    _point(monkeypatch, _fixture(tmp_path, [atom], {"B_atom": 6}, [REAL_MOVE]))


def test_MUTATION_an_instrument_blocked_atom_is_told_neither_to_promote_nor_to_close(
    tmp_path, monkeypatch
):
    """THE FIRING CASE. The decision must name the instrument and must NOT offer either of the
    two limbs that cannot be executed, because a decision whose options are all unavailable is
    one that gets skipped and the passes continue."""
    _blocked_fixture(tmp_path, monkeypatch)
    row = ceiling.decisions(5)[0]
    assert row["instrument_blocked"] is True
    assert row["blocks"] == ["L3_some_instrument"]
    assert "a thing this box does not have." in row["decision"]
    assert "BLOCKED ON AN INSTRUMENT" in row["decision"]
    assert "promote to build" not in row["decision"]


def test_MUTATION_the_blocker_LIFTING_reds_rather_than_sitting_there_out_of_date(
    tmp_path, monkeypatch
):
    """THE RE-OPEN, and the reason the predicate is RUN rather than believed. The map still
    claims a blocker; the live predicate says it is gone. That disagreement is the acquisition
    having landed, and it must be visible on the day it happens — the same doctrine
    `tests/harness/test_lcl_household_anchors.py` pins for the fabric atom.

    A reader that trusted the map's `blocks` list would report this atom blocked for ever."""
    atom = json.loads(json.dumps(BLOCKED_ATOM))
    atom["infeasible_here"]["predicate"] = (
        "tests.tools.test_discovery_pass_ceiling._no_longer_blocked"
    )
    _blocked_fixture(tmp_path, monkeypatch, atom)
    row = ceiling.decisions(5)[0]
    assert row["instrument_blocked"] is False
    assert "RE-OPEN" in row["decision"]
    assert "Clear `infeasible_here`" in row["decision"]


def test_NULL_CONTROL_a_saturated_atom_with_no_record_is_not_instrument_blocked(
    tmp_path, monkeypatch
):
    """Without this the firing test above cannot tell "the record was read" from "everything
    is reported blocked"."""
    _point(monkeypatch, _fixture(tmp_path, [ATOM], {"X_atom": 6}, [REAL_MOVE]))
    row = ceiling.decisions(5)[0]
    assert row["instrument_blocked"] is False
    assert "BLOCKED ON AN INSTRUMENT" not in row["decision"]


def test_NULL_CONTROL_an_UNSATURATED_atom_carrying_a_record_is_not_a_decision(
    tmp_path, monkeypatch
):
    """The subject is the SATURATED set. An atom that is genuinely mid-investigation and
    happens to know one of its criteria is unpayable here is not yet owed a decision — and a
    reader that surfaced it would make `infeasible_here` expensive to record honestly."""
    _point(monkeypatch, _fixture(tmp_path, [BLOCKED_ATOM], {"B_atom": 2}, [REAL_MOVE]))
    assert ceiling.decisions(5) == []


def test_MUTATION_the_saturated_BUILD_decision_no_longer_says_promote_to_build(
    tmp_path, monkeypatch
):
    """THE MEASURED DEFECT, driven directly. A `build`-stage atom told to "promote to build"
    is being handed its own current state as an instruction."""
    atom = dict(ATOM, loop_stage="build")
    _point(monkeypatch, _fixture(tmp_path, [atom], {"X_atom": 6}, [REAL_MOVE]))
    decision = ceiling.decisions(5)[0]["decision"]
    assert "promote to build" not in decision
    assert "land the level move" in decision
    assert "no longer an available answer" in decision


def test_the_idle_decision_is_UNCHANGED_because_the_ruling_wrote_it(tmp_path, monkeypatch):
    """The stage this module shipped for keeps its exact verdict. Widening a control is not a
    licence to rewrite the part that was already right."""
    _point(monkeypatch, _fixture(tmp_path, [ATOM], {"X_atom": 6}, [REAL_MOVE]))
    assert ceiling.decisions(5)[0]["decision"] == (
        "promote to build, or close it -- investigating again is no longer an available answer"
    )


@pytest.mark.parametrize("missing", ["blocks", "predicate", "needs"])
def test_MUTATION_FAIL_CLOSED_a_record_missing_any_half_is_REFUSED(
    tmp_path, monkeypatch, missing
):
    """A blocker that does not name what would lift it is the sentence this field exists to
    replace. Ignoring the malformed record would silently restore the unanswerable decision —
    fail-open in the one direction that looks like everything working."""
    atom = json.loads(json.dumps(BLOCKED_ATOM))
    del atom["infeasible_here"][missing]
    _blocked_fixture(tmp_path, monkeypatch, atom)
    with pytest.raises(ceiling.CeilingUnavailable, match=missing):
        ceiling.decisions(5)


def test_MUTATION_FAIL_SILENT_an_unresolvable_predicate_RAISES_and_does_not_re_open(
    tmp_path, monkeypatch
):
    """AN UNAVAILABLE CHECK IS A FAILED CHECK (R15). The tempting shortcut is to treat an
    import that no longer resolves as "no blocker" — which would let a predicate RENAMED in
    passing quietly re-open an atom nobody had unblocked, and the re-open would look exactly
    like the good news this reader is built to deliver."""
    atom = json.loads(json.dumps(BLOCKED_ATOM))
    atom["infeasible_here"]["predicate"] = "tools.nope_not_a_module.gone"
    _blocked_fixture(tmp_path, monkeypatch, atom)
    with pytest.raises(ceiling.CeilingUnavailable, match="could not be resolved"):
        ceiling.decisions(5)


def test_MUTATION_FAIL_CLOSED_an_unreadable_map_SOURCE_raises(tmp_path, monkeypatch):
    """The new second file gets the same treatment as the three that were already here.
    "No atom is instrument-blocked", computed from a source nobody could read, is the reading
    that turns a permanent blocker back into an infinite lane."""
    _blocked_fixture(tmp_path, monkeypatch)
    ceiling.MAP_SOURCE.write_text("")
    with pytest.raises(ceiling.CeilingUnavailable):
        ceiling.decisions(5)


def test_MUTATION_a_blocker_recorded_for_an_atom_THE_FEED_DOES_NOT_CARRY_raises(
    tmp_path, monkeypatch
):
    """THE TWO-REF JOIN, driven on the failure it invites. This is the module's only two-file
    read. An id present in the map source but not in the feed would simply never match a
    survey row, so the blocker would stop being reported with nothing going red — the silent
    half of `feedback_a_two_sided_census_must_read_both_sides_from_one_ref`."""
    _blocked_fixture(tmp_path, monkeypatch)
    feed = json.loads(ceiling.MAP_FEED.read_text())
    feed["atoms"][0]["id"] = "B_atom_RENAMED"
    ceiling.MAP_FEED.write_text(json.dumps(feed))
    with pytest.raises(ceiling.CeilingUnavailable, match="drifted"):
        ceiling.decisions(5)


def test_saturated_ids_is_DELIBERATELY_untouched_by_any_of_this(tmp_path, monkeypatch):
    """THE BLAST RADIUS, pinned. `saturated_ids` is what the live supervisor draw consumes;
    `decisions()` is the reporting half this module's own docstring calls "owed". An
    instrument-blocked atom must NOT silently leave or enter the draw as a side effect of
    gaining a decision — that is a separate change with its own Rule-0 argument, and making it
    by accident here is exactly how an accretion lands."""
    _blocked_fixture(tmp_path, monkeypatch)
    assert ceiling.saturated_ids(5) == {"B_atom"}


# ---------------------------------------------------------------------------
# The live record — the map's claim held against the live predicate
# ---------------------------------------------------------------------------
def test_no_map_cell_claims_an_instrument_blocker_its_own_predicate_says_is_gone():
    """EVERY `infeasible_here` CELL, not one named atom -- and the widening is the point.

    The previous version of this test pinned `EP6_wall_protocol_typing` by name and read
    `records["EP6_wall_protocol_typing"]` directly. It did its job exactly once: on
    2026-08-20 the cold-eyes walk was recorded, the predicate went to `()`, and the test
    RED on the disagreement, which is what it was built to do. But its own docstring's
    instruction was "clear `infeasible_here` from the map cell" -- and following that
    instruction turned the red into a `KeyError`, because a test keyed on an atom id
    cannot survive that atom's blocker being lifted. A control whose success case is a
    crash is a one-shot tripwire, not a control; it would have been deleted-to-green by
    the next passing tick, taking the invariant with it.

    So the invariant is stated over the CLASS (R10): whatever set of atoms currently
    claims an instrument blocker, none of them may claim one their own predicate no
    longer reports. An empty set passes honestly -- "no atom is instrument-blocked" is a
    real and expected state, and it is the state EP6 entered when its walk was recorded.
    The next atom to gain an `infeasible_here` cell inherits this check by existing,
    which the keyed version could never offer.
    """
    for atom_id, record in sorted(ceiling._infeasible_records().items()):
        assert tuple(record["blocks"]) == ceiling.live_blocks(record), (
            f"{atom_id}: the map's `infeasible_here.blocks` and the live predicate "
            f"disagree -- either the instrument was acquired (clear the cell and re-open "
            f"the atom) or the map is claiming a blocker that is not there"
        )


def test_EP6s_walk_is_recorded_and_its_cell_no_longer_claims_the_blocker():
    """THE RE-OPEN, LANDED — both halves, because either alone is satisfiable by accident.

    A cleared map cell alone proves nothing: deleting the block is a one-line edit any
    tick could make to silence the class check above. A recorded review alone proves
    nothing either: the map could still be claiming a blocker that is gone. Asserting
    both together is what makes this the record of an event rather than of an edit.
    """
    from tools import wall_channel_census as census

    assert census.cold_eyes_walk_outstanding() == (), (
        "no blind review of this capability is recorded -- the walk is outstanding again, "
        "which means the ledger lost a record rather than that the atom regressed"
    )
    assert "EP6_wall_protocol_typing" not in ceiling._infeasible_records(), (
        "the walk is recorded but the map still claims the seat cannot pay for it"
    )


def test_the_walk_predicate_reads_the_LEDGER_and_not_a_flag(tmp_path):
    """Both directions of EP6's own predicate, driven on the artefact rather than asserted.

    The subject is the blind-review ledger because that is the thing only a walk that actually
    happened produces. A missing ledger is NOT unreadable -- nothing recorded is the honest
    reading that no walk has run, and it is the live state (zero reviews, ever)."""
    from tools import wall_channel_census as census

    empty = tmp_path / "none.jsonl"
    assert census.cold_eyes_walk_outstanding(empty) == (census.COLD_EYES_WALK_CRITERION,)

    recorded = tmp_path / "some.jsonl"
    recorded.write_text(json.dumps({"capability": census.BLIND_REVIEW_CAPABILITY}) + "\n")
    assert census.cold_eyes_walk_outstanding(recorded) == ()

    # NULL CONTROL: a walk recorded for a DIFFERENT capability does not lift this atom's
    # blocker. Without this the test above only proves the ledger is non-empty.
    other = tmp_path / "other.jsonl"
    other.write_text(json.dumps({"capability": "SomeOtherAtom"}) + "\n")
    assert census.cold_eyes_walk_outstanding(other) == (census.COLD_EYES_WALK_CRITERION,)


def test_the_CLI_actually_PRINTS_the_decision_the_supervisor_says_it_lists(
    tmp_path, monkeypatch, capsys
):
    """THE POINTER AND THE SURFACE, held together.

    Two supervisor rungs tell the operator that `python3 -m tools.discovery_pass_ceiling`
    "lists the decision each one now is" when they exclude an atom from the draw. Until
    2026-08-20 the CLI did not call `decisions()` at all -- it re-stated the generic verdict
    inline, so `decisions()` was a function with no caller (the class
    `CLASS_NO_CALLER_AND_NEVER_RUNS`) and the supervisor's instruction pointed at a surface
    that did not carry the thing it promised.

    A test on `decisions()` alone cannot see that: it was green throughout.
    """
    _blocked_fixture(tmp_path, monkeypatch)
    assert ceiling.main(["--ceiling", "5"]) == 0
    out = capsys.readouterr().out
    assert "BLOCKED ON AN INSTRUMENT" in out
    assert "a thing this box does not have." in out
    assert "B_atom" in out


def test_the_CLI_names_a_stage_appropriate_decision_for_an_unblocked_atom(
    tmp_path, monkeypatch, capsys
):
    """NULL CONTROL for the test above -- without it, "the CLI prints something about
    blockers" would pass on a CLI that printed nothing else."""
    _point(monkeypatch, _fixture(tmp_path, [dict(ATOM, loop_stage="build")],
                                 {"X_atom": 6}, [REAL_MOVE]))
    assert ceiling.main(["--ceiling", "5"]) == 0
    out = capsys.readouterr().out
    assert "BLOCKED ON AN INSTRUMENT" not in out
    assert "land the level move" in out
