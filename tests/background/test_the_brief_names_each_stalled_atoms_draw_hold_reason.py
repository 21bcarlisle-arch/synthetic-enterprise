"""The seat's brief prints, beside each stalled atom, the draw's own reason for holding it.

The coupled-triad L3 wall removed atoms from every BUILD draw and said so only in the supervisor
journal (wrong_triage `a-coupled-triad-refusal-reaches-only-the-supervisor-log`), so the seat could
not tell a gated atom from one that was DRAWABLE and simply losing the draw.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from background import delivery_seat, supervisor

FP = "0|3|build|1|None"


def _atom(aid):
    return {"id": aid, "level_current": 2, "level_target": 3, "loop_stage": "build"}


def test_a_drawable_and_a_walled_atom_each_print_their_own_draw_reason(tmp_path, monkeypatch):
    """The partition control: both readings reach the rendered brief, so a classifier or a
    renderer that answered one reason for everything reds here."""
    atoms = [_atom("E6"), _atom("W2_41")]
    monkeypatch.setattr(delivery_seat.map_store, "load_atoms", lambda *_a, **_k: atoms)
    monkeypatch.setattr(delivery_seat.map_store, "load_live_atoms", lambda *_a, **_k: atoms)
    monkeypatch.setattr(supervisor, "_build_in_progress_ids", lambda: set())
    monkeypatch.setattr(supervisor, "_is_externally_blocked", lambda a: False)
    monkeypatch.setattr(supervisor, "_coupled_load_gap_ledger", lambda: {})
    monkeypatch.setattr(supervisor, "_coupled_world_l3_blocked",
                        lambda a, *_: (a["id"] == "W2_41", "no mature company twin"))
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".stall.json")
    now = datetime.now(timezone.utc)
    supervisor.ATOM_STALL_STATE_FILE.write_text(json.dumps({
        aid: {"fingerprint": FP, "consecutive_unchanged": 9, "stalled": True,
              "last_drawn_at": now.timestamp(), "stop_reason": "no commit touched its file_scope"}
        for aid in ("E6", "W2_41")}))

    hold = delivery_seat.atom_hold_reasons()
    assert hold["reasons"] == {"E6": "DRAWABLE",
                               "W2_41": "coupled_triad_l3_wall: no mature company twin"}
    rows = delivery_seat.atoms_stalled_with_reason(now - timedelta(hours=3), (), now, hold)
    prompt = delivery_seat._prompt({"atoms_stalled_with_reason": rows, "atom_hold_reasons": hold})
    assert "- E6 (9 unchanged draws): no commit touched its file_scope || draw: DRAWABLE" in prompt
    assert ("- W2_41 (9 unchanged draws): no commit touched its file_scope || draw: "
            "coupled_triad_l3_wall: no mature company twin") in prompt
    assert "ATOMS HELD BY THE COUPLED-TRIAD L3 WALL: 1 -- W2_41." in prompt


def test_a_failed_computation_says_so_and_never_prints_an_empty_hold(tmp_path, monkeypatch):
    def broken(*_a, **_k):
        raise OSError("map unreadable")
    monkeypatch.setattr(delivery_seat.map_store, "load_atoms", broken)
    hold = delivery_seat.atom_hold_reasons()
    assert "OSError" in hold["error"]
    rows = [{"id": "E6", "consecutive_unchanged": 3, "stop_reason": "x",
             "draw_reason": delivery_seat._draw_reason("E6", hold)}]
    prompt = delivery_seat._prompt({"atoms_stalled_with_reason": rows, "atom_hold_reasons": hold})
    assert "draw: the draw's hold reasons could not be computed (OSError: map unreadable)" in prompt
    assert "COUPLED-TRIAD L3 WALL: cannot say" in prompt
    assert "WALL: 0" not in prompt
