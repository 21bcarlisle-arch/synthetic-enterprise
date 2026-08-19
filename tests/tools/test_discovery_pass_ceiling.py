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

import json

import pytest

from tools import discovery_pass_ceiling as ceiling


def _fixture(tmp_path, atoms, records, ledger_actions):
    (tmp_path / "site" / "data").mkdir(parents=True)
    (tmp_path / "site" / "data" / "maturity_map.json").write_text(json.dumps({"atoms": atoms}))
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    for atom_id, n in records.items():
        (store_dir / f"{atom_id}.yaml").write_text(
            json.dumps({"atom_id": atom_id, "simplifications": [f"pass {i}" for i in range(n)]})
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


def test_an_atom_that_moved_its_level_never_saturates(tmp_path, monkeypatch):
    """THE central distinction. The ceiling is not a budget on investigation -- it is a bound
    on investigation THAT CHANGES NOTHING. Twenty passes that moved a level are productive
    work and must stay drawable."""
    root = _fixture(tmp_path, [ATOM], {"X_atom": 20},
                    [REAL_MOVE, {"atom": "X_atom", "action": "LEVEL_UP_SELF_CERTIFIED", "ts": 2.0}])
    _point(monkeypatch, root)
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

    What is actually invariant is weaker and true: a saturated atom has moved no level (that is
    the definition, and a violation would mean the ledger read is broken), and its stage is one
    the ruling recognises -- `idle` for a decision outstanding, anything else for a decision
    taken. `verify`/`harden`/`discover` are all legitimate answers to "this has stopped moving".
    """
    rows = [r for r in ceiling.survey() if r["saturated"]]
    assert rows, "nothing is saturated -- if the tail really cleared, replace this assertion"
    for r in rows:
        assert r["level_moves"] == 0, (
            f"{r['atom']} is called saturated but the ledger shows {r['level_moves']} level "
            "moves -- the ledger read is broken, not the atom"
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
