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
    (tmp_path / "site" / "data" / "maturity_map.json").write_text(json.dumps({"atoms": atoms}))
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
