"""Self-Governance Scope Model — the reconciler that catches the autonomous loop crossing a gate
it does not own (SELF_GOVERNANCE_SCOPE_MODEL.md §5, sub-steps 1-5).

R15 mutation coverage (a control that cannot FIRE is theatre — worse than none). M1-M7 each prove
the alarm fires on its OWN named defect and stays quiet on the authorized case; the *_independence
tests neuter the predicate to always-pass and assert the finding DISAPPEARS (so the alarm is not
vacuous). Both fronts are HELD throughout — the mechanism is proven while it authorizes NOTHING.
"""
from __future__ import annotations

import json

import pytest

from background import fronts_reconciler as FR
from background import gate_authorization as GW


# ── fixtures ────────────────────────────────────────────────────────────────────────────────
GATES = [
    {"id": "one_way_doors", "kind": "predicate", "predicate": "one_way_door.classify_action"},
    {"id": "epoch_boundary", "kind": "epoch_ceiling"},
    {"id": "level_promotion", "kind": "level_gate"},
    {"id": "stage_advance", "kind": "stage_gate"},
    {"id": "schema_sim_structure", "kind": "gated_atoms_and_paths",
     "gated_atoms": ["W4_1_typed_adapters", "G2_event_log_shared_with_spine"],
     "gated_paths": ["company/interfaces/sim_interface.py", "docs/design/maturity_map.yaml"]},
    {"id": "values_decisions", "kind": "gated_atoms",
     "gated_atoms": ["A4_sim_approver", "A5_tournament_fitness_mortality"]},
]


def _front(fid, state, lanes, ceiling=3, opened_by=None, include_atoms=None, include_paths=None):
    f = {"id": fid, "state": state, "lanes": list(lanes), "epoch_ceiling": ceiling}
    if include_atoms:
        f["include_atoms"] = list(include_atoms)
    if include_paths:
        f["include_paths"] = list(include_paths)
    if state == "open":
        f["opened_by"] = opened_by or "ledger FRONT_OPEN 2026-07-18T00:00Z"
    else:
        f["reason"] = "held for the test"
        f["flip"] = "director FRONT_OPEN console act"
        f["opened_by"] = None
    return f


def _decl(fronts, gates=None):
    return {"fronts": list(fronts), "gates": list(gates if gates is not None else GATES)}


def _atom(aid, lane, epoch, loop_stage, level, file_scope=None):
    a = {"id": aid, "lane": lane, "epoch": epoch, "loop_stage": loop_stage, "level_current": level}
    if file_scope:
        a["file_scope"] = list(file_scope)
    return a


def _build_open(atom):
    return {"atom": atom, "action": "BUILD_OPEN", "authorized_by": "director",
            "channel": "console", "provenance": "director console 2026-07-18: open BUILD"}


def _front_open(front):
    return {"front": front, "action": "FRONT_OPEN", "authorized_by": "director",
            "channel": "console", "provenance": "director console 2026-07-18: open front"}


def _front_close(front, ts=None):
    e = {"front": front, "action": "FRONT_CLOSE", "authorized_by": "director",
         "channel": "console", "provenance": "director console: close front"}
    if ts is not None:
        e["ts"] = ts
    return e


def _gate_clear(atom, gate=None):
    e = {"atom": atom, "action": "GATE_CLEAR", "authorized_by": "director",
         "channel": "console", "provenance": "director console: clear the gate"}
    if gate is not None:
        e["gate"] = gate
    return e


def _level_up(atom, level=None):
    e = {"atom": atom, "action": "LEVEL_UP_PROPOSED", "authorized_by": "director",
         "channel": "console", "provenance": "director+advisor console: move the cell"}
    if level is not None:
        e["level"] = level
    return e


def _forged(entry):
    """A worker self-write: it declares itself but is NOT a console act."""
    e = dict(entry)
    e["channel"] = "agent"
    e["authorized_by"] = "worker"
    return e


def _classify(atom, *, fronts, ledger, from_stage="idle", from_level=None, action_desc=""):
    decl = _decl(fronts)
    return FR.classify_atom(
        atom, from_stage=from_stage, to_stage=atom.get("loop_stage"),
        from_level=from_level, to_level=atom.get("level_current"),
        fronts=decl["fronts"], open_ids=FR.open_front_ids(decl["fronts"], ledger),
        gate_index=FR._gate_index(decl["gates"]), ledger=ledger, action_desc=action_desc)


# ── M1: gated-atom promotion, no clear -> GATE_CROSSED (+ independence) ─────────────────────
def _m1_atom_and_fronts():
    # an epoch-4 atom INSIDE an OPEN front: the epoch gate is the ONLY thing that can make it loud,
    # so neutering the gate must turn it quiet (ON_FRONT) — a clean independence demonstration.
    atom = _atom("W2_3_competitor_field", "W2_customer_generator", epoch=4, loop_stage="build", level=1)
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather", "W2_customer_generator"])]
    ledger = [_front_open("SIM_ACTORS")]
    return atom, fronts, ledger


def test_M1_gated_promotion_no_clear_ALARMS():
    atom, fronts, ledger = _m1_atom_and_fronts()
    r = _classify(atom, fronts=fronts, ledger=ledger)
    assert r["status"] == "GATE_CROSSED" and r["alarm"] is True
    assert "epoch_boundary" in r["detail"]


def test_M1_gate_cleared_by_console_act_is_QUIET():
    atom, fronts, ledger = _m1_atom_and_fronts()
    ledger = ledger + [_gate_clear("W2_3_competitor_field", "epoch_boundary")]
    r = _classify(atom, fronts=fronts, ledger=ledger)
    assert r["alarm"] is False and r["status"] == "ON_FRONT"


def test_M1_independence_neuter_gate_predicate_makes_finding_DISAPPEAR(monkeypatch):
    atom, fronts, ledger = _m1_atom_and_fronts()
    # sanity: fires before the mutation
    assert _classify(atom, fronts=fronts, ledger=ledger)["status"] == "GATE_CROSSED"
    # MUTATION: the gate predicate always-passes (never finds a gate) -> the finding must vanish
    monkeypatch.setattr(FR, "crosses_static_gate", lambda *a, **k: None)
    r = _classify(atom, fronts=fronts, ledger=ledger)
    assert r["status"] != "GATE_CROSSED"   # would be RED if the alarm were vacuous
    assert r["status"] == "ON_FRONT" and r["alarm"] is False


# ── M2: atom in no open front promoted -> DRAW_OFF_FRONT ────────────────────────────────────
def test_M2_promotion_off_every_front_ALARMS():
    atom = _atom("Z9_rogue", "Z_unknown_lane", epoch=2, loop_stage="build", level=1)
    fronts = [_front("SIM_ACTORS", "held", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[])
    assert r["status"] == "DRAW_OFF_FRONT" and r["alarm"] is True


def test_M2_off_front_atom_with_per_atom_BUILD_OPEN_is_QUIET():
    atom = _atom("Z9_rogue", "Z_unknown_lane", epoch=2, loop_stage="build", level=1)
    fronts = [_front("SIM_ACTORS", "held", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[_build_open("Z9_rogue")])
    assert r["alarm"] is False and r["status"] == "ON_FRONT"


# ── M3: in-region, non-gated, valid FRONT_OPEN -> QUIET (no false-positive treadmill) ───────
def test_M3_in_open_front_nongated_is_QUIET():
    atom = _atom("W1_3_national_weather_signal", "W1_market_weather", epoch=3, loop_stage="build", level=1)
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[_front_open("SIM_ACTORS")])
    assert r["alarm"] is False and r["status"] == "ON_FRONT"


def test_M3_open_front_needs_BOTH_yaml_state_and_ledger_act():
    atom = _atom("W1_3_national_weather_signal", "W1_market_weather", epoch=3, loop_stage="build", level=1)
    # yaml says open, but NO FRONT_OPEN in the ledger -> the front is NOT open (independence).
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[])
    assert r["status"] == "GATE_CROSSED" and r["alarm"] is True  # advanced a not-actually-open front


# ── M4: forged authorization does NOT clear the gate ───────────────────────────────────────
def test_M4_forged_gate_clear_does_NOT_silence():
    atom, fronts, _ = _m1_atom_and_fronts()
    ledger = [_front_open("SIM_ACTORS"), _forged(_gate_clear("W2_3_competitor_field", "epoch_boundary"))]
    r = _classify(atom, fronts=fronts, ledger=ledger)
    assert r["status"] == "GATE_CROSSED" and r["alarm"] is True


def test_M4_forged_front_open_does_NOT_open_the_front():
    atom = _atom("W1_3_national_weather_signal", "W1_market_weather", epoch=3, loop_stage="build", level=1)
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[_forged(_front_open("SIM_ACTORS"))])
    assert r["alarm"] is True   # self-declared console channel is not authorization


def test_M4_forged_build_open_does_NOT_silence_off_front():
    atom = _atom("Z9_rogue", "Z_unknown_lane", epoch=2, loop_stage="build", level=1)
    fronts = [_front("SIM_ACTORS", "held", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[_forged(_build_open("Z9_rogue"))])
    assert r["status"] == "DRAW_OFF_FRONT" and r["alarm"] is True


# ── M5: replay the real incident — a self-advance of a held/gated atom fires ────────────────
def test_M5_self_advance_of_held_front_atom_ALARMS():
    # The 2026-07-18 incident: the orchestrator self-advanced W1 (DISCOVER) -> BUILD, no console act.
    atom = _atom("W1_6_physics_price_signal", "W1_market_weather", epoch=3, loop_stage="build", level=0)
    fronts = [_front("SIM_ACTORS", "held", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[], from_stage="idle")
    assert r["status"] == "GATE_CROSSED" and r["alarm"] is True
    assert "self-advance" in r["detail"]


def test_M5_same_atom_with_BUILD_OPEN_is_QUIET():
    atom = _atom("W1_6_physics_price_signal", "W1_market_weather", epoch=3, loop_stage="build", level=0)
    fronts = [_front("SIM_ACTORS", "held", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[_build_open("W1_6_physics_price_signal")])
    assert r["alarm"] is False and r["status"] == "ON_FRONT"


# ── M6: the LEVEL gate (§10.1) ─────────────────────────────────────────────────────────────
def test_M6_level_self_promotion_no_auth_ALARMS():
    atom = _atom("W1_4_regional_weather_field", "W1_market_weather", epoch=3, loop_stage="build", level=2)
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[_front_open("SIM_ACTORS")], from_level=1)
    assert r["status"] == "LEVEL_SELF_PROMOTION" and r["alarm"] is True


def test_M6_director_advisor_authorized_level_up_is_QUIET():
    atom = _atom("W1_4_regional_weather_field", "W1_market_weather", epoch=3, loop_stage="build", level=2)
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather"])]
    ledger = [_front_open("SIM_ACTORS"), _level_up("W1_4_regional_weather_field", level=2)]
    r = _classify(atom, fronts=fronts, ledger=ledger, from_level=1)
    assert r["alarm"] is False


def test_M6_level_up_bounded_to_target_does_not_clear_a_higher_jump():
    atom = _atom("W1_4_regional_weather_field", "W1_market_weather", epoch=3, loop_stage="build", level=3)
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather"])]
    ledger = [_front_open("SIM_ACTORS"), _level_up("W1_4_regional_weather_field", level=2)]  # only to L2
    r = _classify(atom, fronts=fronts, ledger=ledger, from_level=1)   # but it jumped to L3
    assert r["status"] == "LEVEL_SELF_PROMOTION" and r["alarm"] is True


def test_M6_forged_level_up_does_NOT_clear():
    atom = _atom("W1_4_regional_weather_field", "W1_market_weather", epoch=3, loop_stage="build", level=2)
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather"])]
    ledger = [_front_open("SIM_ACTORS"), _forged(_level_up("W1_4_regional_weather_field", level=2))]
    r = _classify(atom, fronts=fronts, ledger=ledger, from_level=1)
    assert r["status"] == "LEVEL_SELF_PROMOTION" and r["alarm"] is True


def test_M6_independence_neuter_level_predicate_makes_finding_DISAPPEAR(monkeypatch):
    atom = _atom("W1_4_regional_weather_field", "W1_market_weather", epoch=3, loop_stage="build", level=2)
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather"])]
    ledger = [_front_open("SIM_ACTORS")]
    assert _classify(atom, fronts=fronts, ledger=ledger, from_level=1)["status"] == "LEVEL_SELF_PROMOTION"
    # MUTATION: _level_cleared always-passes -> the level alarm must vanish
    monkeypatch.setattr(FR, "_level_cleared", lambda *a, **k: True)
    r = _classify(atom, fronts=fronts, ledger=ledger, from_level=1)
    assert r["status"] != "LEVEL_SELF_PROMOTION"   # would be RED if the level gate were vacuous


# ── M7: loop_stage — a DISCOVER atom is DISCOVER/FRAME only, never a BUILD candidate ────────
def test_M7_discover_stage_atom_is_not_build_authorized_when_front_held():
    # A W1 atom (SIM_ACTORS held) is NOT build-authorized (the draw filter drops it).
    atom = _atom("W1_10_ev_heatpump_geography", "W1_market_weather", epoch=3, loop_stage="build", level=0)
    decl = _decl([_front("SIM_ACTORS", "held", ["W1_market_weather"])])
    assert FR.is_build_authorized(atom, fronts_decl=decl, ledger=[]) is False
    # ... but becomes authorized the moment the front is OPEN (region authorization).
    decl_open = _decl([_front("SIM_ACTORS", "open", ["W1_market_weather"])])
    assert FR.is_build_authorized(atom, fronts_decl=decl_open, ledger=[_front_open("SIM_ACTORS")]) is True


def test_M7_filter_drops_held_front_build_candidates():
    cands = [
        _atom("W1_10_ev_heatpump_geography", "W1_market_weather", epoch=3, loop_stage="build", level=0),
        _atom("W2_x", "W2_customer_generator", epoch=3, loop_stage="build", level=0),
    ]
    decl = _decl([_front("SIM_ACTORS", "held", ["W1_market_weather", "W2_customer_generator"])])
    assert FR.filter_build_candidates(cands, fronts_decl=decl, ledger=[]) == []


def test_M7_synthetic_self_advance_to_build_no_console_ALARMS():
    atom = _atom("W1_10_ev_heatpump_geography", "W1_market_weather", epoch=3, loop_stage="build", level=0)
    fronts = [_front("SIM_ACTORS", "held", ["W1_market_weather"])]
    r = _classify(atom, fronts=fronts, ledger=[], from_stage="idle")
    assert r["status"] == "GATE_CROSSED" and r["alarm"] is True


def test_M7_independence_neuter_makes_stage_finding_DISAPPEAR(monkeypatch):
    atom = _atom("W1_10_ev_heatpump_geography", "W1_market_weather", epoch=3, loop_stage="build", level=0)
    fronts = [_front("SIM_ACTORS", "held", ["W1_market_weather"])]
    assert _classify(atom, fronts=fronts, ledger=[])["status"] == "GATE_CROSSED"
    # MUTATION: treat the atom as if the front were OPEN (membership always authorizes) — the
    # stage-advance finding must vanish. We neuter open_front_ids to include the front.
    monkeypatch.setattr(FR, "open_front_ids", lambda fronts, ledger: {"SIM_ACTORS"})
    r = _classify(atom, fronts=fronts, ledger=[])
    assert r["status"] != "GATE_CROSSED" and r["alarm"] is False


# ── sub-step 1: fronts.yaml loader ─────────────────────────────────────────────────────────
def test_real_fronts_yaml_loads_and_both_are_HELD():
    decl = FR.load_fronts()
    states = {f["id"]: f["state"] for f in decl["fronts"]}
    assert states == {"SIM_ACTORS": "held", "SUPPLIER": "held"}
    # this build authorizes NOTHING: no front is open
    assert FR.open_front_ids(decl["fronts"], GW.read_ledger()) == set()


def test_loader_rejects_open_front_with_null_opened_by(tmp_path):
    bad = tmp_path / "fronts.yaml"
    bad.write_text(json.dumps({"version": 1, "fronts": [
        {"id": "X", "state": "open", "lanes": ["L"], "epoch_ceiling": 3, "opened_by": None}]}))
    with pytest.raises(FR.FrontsError, match="opened_by"):
        FR.load_fronts(bad)


def test_loader_rejects_held_front_without_reason_flip(tmp_path):
    bad = tmp_path / "fronts.yaml"
    bad.write_text(json.dumps({"version": 1, "fronts": [
        {"id": "X", "state": "held", "lanes": ["L"], "epoch_ceiling": 3}]}))
    with pytest.raises(FR.FrontsError):
        FR.load_fronts(bad)


def test_loader_rejects_empty_and_bad_state(tmp_path):
    empty = tmp_path / "e.yaml"
    empty.write_text(json.dumps({"version": 1, "fronts": []}))
    with pytest.raises(FR.FrontsError):
        FR.load_fronts(empty)


# ── sub-step 3: ledger record types validate through the SAME four console checks ──────────
def test_record_types_validity_predicates():
    assert GW.is_valid_front_open(_front_open("SIM_ACTORS")) is True
    assert GW.is_valid_front_open(_forged(_front_open("SIM_ACTORS"))) is False
    assert GW.is_valid_front_close(_front_close("SIM_ACTORS")) is True
    assert GW.is_valid_gate_clear(_gate_clear("A", "epoch_boundary")) is True
    assert GW.is_valid_gate_clear(_forged(_gate_clear("A"))) is False
    assert GW.is_valid_level_up(_level_up("A", 2)) is True
    assert GW.is_valid_level_up(_forged(_level_up("A", 2))) is False
    # a FRONT_OPEN with no front id is not valid
    assert GW.is_valid_front_open({"action": "FRONT_OPEN", "authorized_by": "director",
                                   "channel": "console", "provenance": "x"}) is False


def test_console_writers_roundtrip(tmp_path):
    p = tmp_path / "ledger.jsonl"
    GW.record_front_open("SIM_ACTORS", "director console act", path=p)
    GW.record_gate_clear("W2_3", "epoch_boundary", "director console act", path=p)
    GW.record_level_up("W1_4", 2, "director+advisor act", path=p)
    GW.record_front_close("SIM_ACTORS", "director console act", ts=999, path=p)
    entries = GW.read_ledger(p)
    assert GW.is_valid_front_open(entries[0]) and entries[0]["front"] == "SIM_ACTORS"
    assert GW.is_valid_gate_clear(entries[1]) and entries[1]["gate"] == "epoch_boundary"
    assert GW.is_valid_level_up(entries[2]) and entries[2]["level"] == 2


def test_FRONT_CLOSE_refreezes_the_region_R11(tmp_path):
    # open then later close -> open_front_ids reports the front NOT open (the release has a real effect)
    ledger = [dict(_front_open("SIM_ACTORS"), ts=1), _front_close("SIM_ACTORS", ts=2)]
    fronts = [_front("SIM_ACTORS", "open", ["W1_market_weather"])]
    assert FR.open_front_ids(fronts, ledger) == set()
    # and an in-region atom advancing after the close alarms again
    atom = _atom("W1_3_national_weather_signal", "W1_market_weather", 3, "build", 1)
    r = _classify(atom, fronts=fronts, ledger=ledger)
    assert r["alarm"] is True


# ── sub-step 4: transition-only typed real-alarm wiring (R5) ───────────────────────────────
def test_run_pages_once_on_transition_then_suppresses_and_clears(tmp_path, monkeypatch):
    from background import notify as N
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".transitions.json")
    sends = []
    monkeypatch.setattr(N.ntfy_utils, "send_ntfy",
                        lambda msg, **k: sends.append((msg, k)) or "sent-id")

    drift_ev = {"status": "SCOPE_VIOLATION", "alarm": True, "level_baseline_available": True,
                "signature": ["DRAW_OFF_FRONT:Z9_rogue"],
                "alarms": [{"atom": "Z9_rogue", "status": "DRAW_OFF_FRONT", "alarm": True,
                            "detail": "drew off-front"}]}
    monkeypatch.setattr(FR, "evaluate", lambda: drift_ev)

    r1 = FR.run()
    assert r1["paged"] is True and len(sends) == 1
    assert sends[0][1]["headers"]["Tags"] == "rotating_light"     # typed real-alarm

    r2 = FR.run()                                                 # unchanged -> R5 suppress
    assert r2["paged"] is False and len(sends) == 1

    clean_ev = {"status": "SCOPE_CLEAN", "alarm": False, "level_baseline_available": True,
                "signature": [], "alarms": []}
    monkeypatch.setattr(FR, "evaluate", lambda: clean_ev)
    r3 = FR.run()                                                 # drift -> clean transition
    assert r3["paged"] is True and len(sends) == 2
    assert sends[1][1]["headers"]["Tags"] == "white_check_mark"


def test_run_does_not_page_on_steady_clean(tmp_path, monkeypatch):
    from background import notify as N
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".transitions.json")
    sends = []
    monkeypatch.setattr(N.ntfy_utils, "send_ntfy", lambda msg, **k: sends.append(msg) or "id")
    monkeypatch.setattr(FR, "evaluate", lambda: {"status": "SCOPE_CLEAN", "alarm": False,
                                                 "level_baseline_available": True,
                                                 "signature": [], "alarms": []})
    assert FR.run()["paged"] is False and sends == []


def test_page_decision_pure():
    assert FR.page_decision([], []) == (False, None, False)
    assert FR.page_decision([], ["GATE_CROSSED:X"])[0] is True
    assert FR.page_decision(["GATE_CROSSED:X"], ["GATE_CROSSED:X"]) == (False, None, False)
    assert FR.page_decision(["GATE_CROSSED:X"], []) == (True, "white_check_mark", True)


# ── the live state must be CLEAN (no false alarm on today's authorized reality) ────────────
def test_live_reconciler_is_CLEAN():
    ev = FR.evaluate()
    assert ev["alarm"] is False, f"unexpected live alarms: {ev['signature']}"
    assert ev["status"] == "SCOPE_CLEAN"
    assert ev["level_baseline_available"] is True     # git baseline read succeeded


def test_evaluate_never_raises_and_is_report_only():
    ev = FR.evaluate()
    assert set(["status", "alarm", "signature", "results"]).issubset(ev.keys())
