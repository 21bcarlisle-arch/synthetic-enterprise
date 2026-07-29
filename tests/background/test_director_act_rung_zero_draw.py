"""RUNG-1c DIRECTOR-ACT RUNG ZERO draw -- R15 both-ways proof
(DIRECTOR_RULING_PHONE_SIGNER_NO_CONSOLE 2026-07-29 §2, atom `director_act_rung_zero_draw`).

The mechanism: an AUTHENTICATED director `LEVEL_UP_PROPOSED` (R16/R17 make the ledger the authority)
whose map atom has NOT been reconciled to it -- the ledger ratifies L{N} but the map still sits at
`level_current < N` -- is PRIORITY drawable work. `_director_act_rung_zero_draw()` is the detector; it
is wired as RUNG 1c of `_self_refill_draw` (below the two PRIORITY-ZERO operational rungs, ABOVE every
product/HARDEN/campaign/backlog lane) and mirrored in `_is_drained_and_gated`.

The incident this reproduces: a 2026-07-28 ~19:40 BST director console act sat UNCONSUMED for ~11
HOURS behind cooldown re-stamps / HARDEN re-verifies, because a signed director act (the scarcest
resource) had no draw rung -- it took effect only passively. §2: "A faster channel with the same
latency is worthless." This rung fixes the LATENCY.

R15 requires a control that can FAIL. These tests prove it BOTH ways:
  * MUST FIRE: ledger ratifies L3, map at L2 -> the detector returns a draw; `_self_refill_draw`
    returns it ABOVE the HARDEN/product lanes; `_is_drained_and_gated` refuses rest. Remove the rung
    (mutation) and the director act sinks behind cooldown -> these red.
  * MUST STAY SILENT (no phantom rung-zero draw): a reconciled level (map == ledger), a non-director
    (twin-forged console self-write / no-provenance) entry, a level-less entry, an atom absent from the
    map, and an absent ledger all return None.
"""
import json
from pathlib import Path

import pytest

from background import supervisor


def _write_ledger(tmp_path, entries):
    lp = tmp_path / "gate_authorizations.jsonl"
    lp.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")
    return lp


def _write_map(tmp_path, atoms):
    import yaml
    mp = tmp_path / "maturity_map.yaml"
    mp.write_text(yaml.safe_dump(atoms), encoding="utf-8")
    return mp


def _console_level_up(atom, level, ts=1000.0):
    """A genuine director-console LEVEL_UP_PROPOSED (the four checks + a non-empty atom)."""
    return {"atom": atom, "action": "LEVEL_UP_PROPOSED", "level": level, "ts": ts,
            "authorized_by": "director", "channel": "console",
            "provenance": "Director console (live session): RATIFIED, ledger-backed."}


def _atom(id_, level_current, level_target=3, **extra):
    a = {"id": id_, "level_current": level_current, "level_target": level_target,
         "lane": "W_world", "dial_inherited": 3, "loop_stage": "build"}
    a.update(extra)
    return a


# ─────────────────────────────── MUST FIRE (ledger ahead of map) ───────────────────────────────

def test_fires_when_ledger_ratifies_above_map_level(tmp_path):
    """The exact 11h gap: ledger ratifies L3, the map atom still sits at L2 (blocked_on the director
    act it is waiting on) -> the reconciliation is rung-zero work."""
    lp = _write_ledger(tmp_path, [_console_level_up("W1_9_dsr_flex_markets", 3)])
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 2, blocked_on="director_level_up")])
    msg = supervisor._director_act_rung_zero_draw(ledger_path=lp, map_path=mp)
    assert msg is not None
    assert "W1_9_dsr_flex_markets" in msg
    assert "L3" in msg and "UNCONSUMED" in msg


def test_picks_oldest_unconsumed_act_first(tmp_path):
    """When several director acts are unconsumed, the one that has waited LONGEST (smallest ts) is
    named first -- it is the worst latency."""
    lp = _write_ledger(tmp_path, [
        _console_level_up("ATOM_NEW", 2, ts=5000.0),
        _console_level_up("ATOM_OLD", 2, ts=100.0),
    ])
    mp = _write_map(tmp_path, [_atom("ATOM_NEW", 1), _atom("ATOM_OLD", 1)])
    msg = supervisor._director_act_rung_zero_draw(ledger_path=lp, map_path=mp)
    assert msg is not None
    assert "ATOM_OLD" in msg
    assert "+1 more unconsumed" in msg


def test_self_refill_returns_it_above_the_harden_lane(tmp_path, monkeypatch):
    """The rung is wired ABOVE the RULE-0 HARDEN treadmill and every product lane: even with a HARDEN
    candidate available (the state that produced the 11h latency), the unconsumed director act draws
    FIRST. This is the ordering proof -- remove RUNG 1c and the HARDEN string would return instead."""
    lp = _write_ledger(tmp_path, [_console_level_up("W1_9_dsr_flex_markets", 3)])
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 2, blocked_on="director_level_up")])
    from background import gate_authorization as ga
    monkeypatch.setattr(ga, "LEDGER_PATH", lp)
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", mp)
    # Neutralise the two higher PRIORITY-ZERO operational rungs.
    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_operational_red_persistent_draw", lambda *a, **k: None)
    # A HARDEN candidate is available (what the tick WOULD otherwise draw) -- the rung must beat it.
    monkeypatch.setattr(supervisor, "_rule0_harden_draw", lambda *a, **k: {"id": "SOME_AT_TARGET"})
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    out = supervisor._self_refill_draw()
    assert out is not None
    assert "DIRECTOR-ACT RUNG ZERO" in out
    assert "W1_9_dsr_flex_markets" in out
    assert "SOME_AT_TARGET" not in out


def test_is_drained_and_gated_refuses_rest_while_act_unconsumed(tmp_path, monkeypatch):
    """Rest is never legitimate while a signed director act sits unconsumed -- the mirror rung must
    flip `_is_drained_and_gated` to False even with every lower lane empty."""
    lp = _write_ledger(tmp_path, [_console_level_up("W1_9_dsr_flex_markets", 3)])
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 2, blocked_on="director_level_up")])
    from background import gate_authorization as ga
    monkeypatch.setattr(ga, "LEDGER_PATH", lp)
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", mp)
    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_operational_red_persistent_draw", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_site_lane_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_idle_discover_frame_draw_concurrent", lambda *a, **k: [])
    assert supervisor._is_drained_and_gated() is False


# ───────────────────────── MUST STAY SILENT (no phantom rung-zero draw) ─────────────────────────

def test_silent_when_map_reconciled(tmp_path):
    """Ledger L3, map already at L3 -> the act is CONSUMED, no rung. (Live-state invariant: every
    current ratified level-up is reconciled, so this rung is silent on the real map today.)"""
    lp = _write_ledger(tmp_path, [_console_level_up("W1_9_dsr_flex_markets", 3)])
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 3)])
    assert supervisor._director_act_rung_zero_draw(ledger_path=lp, map_path=mp) is None


def test_silent_on_twin_forged_console_selfwrite(tmp_path):
    """A machine self-write self-declaring channel==console but authorized_by!=director is NOT a
    director act -- it can never mint a rung-zero draw (independence / not-marking-own-homework)."""
    forged = _console_level_up("W1_9_dsr_flex_markets", 3)
    forged["authorized_by"] = "twin"  # not the director
    lp = _write_ledger(tmp_path, [forged])
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 2)])
    assert supervisor._director_act_rung_zero_draw(ledger_path=lp, map_path=mp) is None


def test_silent_on_missing_provenance(tmp_path):
    """No provenance -> fails the four-check console predicate -> not an act."""
    e = _console_level_up("W1_9_dsr_flex_markets", 3)
    e["provenance"] = ""
    lp = _write_ledger(tmp_path, [e])
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 2)])
    assert supervisor._director_act_rung_zero_draw(ledger_path=lp, map_path=mp) is None


def test_silent_on_levelless_entry(tmp_path):
    """A LEVEL_UP with no integer `level` cannot be compared against the map -> no phantom draw."""
    e = _console_level_up("W1_9_dsr_flex_markets", 3)
    del e["level"]
    lp = _write_ledger(tmp_path, [e])
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 2)])
    assert supervisor._director_act_rung_zero_draw(ledger_path=lp, map_path=mp) is None


def test_silent_when_atom_absent_from_map(tmp_path):
    """A ratified level-up for an atom not on the map cannot be a reconciliation gap -> silent."""
    lp = _write_ledger(tmp_path, [_console_level_up("GHOST_ATOM", 3)])
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 2)])
    assert supervisor._director_act_rung_zero_draw(ledger_path=lp, map_path=mp) is None


def test_silent_on_absent_ledger(tmp_path):
    lp = tmp_path / "does_not_exist.jsonl"
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 2)])
    assert supervisor._director_act_rung_zero_draw(ledger_path=lp, map_path=mp) is None


def test_failed_read_of_nonempty_ledger_does_not_phantom_draw(tmp_path, monkeypatch):
    """FAIL-SILENT guard (R15): a non-empty ledger file that parses to zero entries is a FAILED read,
    not 'no acts' -- it is logged loudly and returns None, never a phantom rung-zero draw."""
    lp = tmp_path / "gate_authorizations.jsonl"
    lp.write_text("{ this is not valid json at all\n", encoding="utf-8")
    mp = _write_map(tmp_path, [_atom("W1_9_dsr_flex_markets", 2)])
    logs = []
    monkeypatch.setattr(supervisor, "log", lambda m, *a, **k: logs.append(m))
    assert supervisor._director_act_rung_zero_draw(ledger_path=lp, map_path=mp) is None
    assert any("FAILED read" in m for m in logs)
