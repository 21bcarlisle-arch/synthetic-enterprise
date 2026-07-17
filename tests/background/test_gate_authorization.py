"""GATE-WALL detection control (OPS1, director P0 2026-07-17).

R15 mutation coverage: a control that never fires is theatre. These prove the wall FIRES on its
own defect (an idle->build promotion with no director-console authorization) and stays QUIET on
an authorized one -- and that an INVALID authorization (a twin/machine self-write, non-console,
or no-provenance) does NOT silence it ("not marking your own homework").

PRINCIPLE under test (director): self-SUSTAIN through an open gate is fine; self-PROMOTE across a
gate (idle->build) without the director's authenticated console act is what this catches.
"""
from __future__ import annotations

import json

import pytest

from background import gate_authorization as G


def _write_baseline(tmp_path, stages):
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps({"genesis_commit": "TEST", "stages": stages}))
    return p


def _write_ledger(tmp_path, entries):
    p = tmp_path / "ledger.jsonl"
    p.write_text("".join(json.dumps(e) + "\n" for e in entries))
    return p


def _valid_entry(atom):
    return {"atom": atom, "action": "BUILD_OPEN", "authorized_by": "director",
            "channel": "console", "provenance": "director console message 2026-07-17: open BUILD"}


def _hold_entry(atom):
    return {"atom": atom, "action": "HELD_PENDING_VERIFICATION", "authorized_by": "director",
            "channel": "console", "provenance": "director console msg 2026-07-17: HOLD pending L3 run"}


def _eval(tmp_path, baseline, current, ledger):
    bp = _write_baseline(tmp_path, baseline)
    lp = _write_ledger(tmp_path, ledger)
    cur = tmp_path / "map.yaml"
    # write a minimal map yaml the current_loop_stages reader can parse
    cur.write_text("atoms:\n" + "".join(
        f"  - id: {a}\n    loop_stage: {s}\n" for a, s in current.items()))
    return G.evaluate_gate_wall(map_path=cur, baseline_path=bp, ledger_path=lp)


# ── the mutation: fires on the defect, quiet when authorized ───────────────────────────────
def test_unauthorized_promotion_ALARMS(tmp_path):
    r = _eval(tmp_path, baseline={"A": "idle"}, current={"A": "build"}, ledger=[])
    assert r["status"] == "GATE_VIOLATION" and r["alarm"] is True
    assert [u["atom"] for u in r["unauthorized"]] == ["A"]


def test_authorized_promotion_is_QUIET(tmp_path):
    # THE mutation: the SAME promotion, now with a valid director-console authorization -> silent.
    r = _eval(tmp_path, baseline={"A": "idle"}, current={"A": "build"}, ledger=[_valid_entry("A")])
    assert r["status"] == "GATE_CLEAN" and r["alarm"] is False


def test_invalid_authorization_does_NOT_silence_the_alarm(tmp_path):
    """A twin/machine self-write cannot authorize: non-console channel, missing provenance, or
    authorized_by != director does NOT count. 'Not marking your own homework.'"""
    bad_channel = {**_valid_entry("A"), "channel": "doorbell"}       # worker self-write
    no_prov = {**_valid_entry("A"), "provenance": ""}                # bare / no trace
    not_director = {**_valid_entry("A"), "authorized_by": "twin"}    # twin is a voice, not a hand
    for bad in (bad_channel, no_prov, not_director):
        r = _eval(tmp_path, baseline={"A": "idle"}, current={"A": "build"}, ledger=[bad])
        assert r["status"] == "GATE_VIOLATION" and r["alarm"] is True, bad


def test_grandfathered_active_atom_and_docwork_stay_quiet(tmp_path):
    # B was already active at genesis -> grandfathered (not a promotion). C stayed idle (doc-only
    # DISCOVER/FRAME work is allowed and does not flip loop_stage) -> not a promotion.
    r = _eval(tmp_path, baseline={"B": "build", "C": "idle"},
              current={"B": "harden", "C": "idle"}, ledger=[])
    assert r["status"] == "GATE_CLEAN" and r["alarm"] is False


def test_mixed_one_authorized_one_not(tmp_path):
    r = _eval(tmp_path, baseline={"A": "idle", "D": "idle"},
              current={"A": "build", "D": "build"}, ledger=[_valid_entry("A")])
    assert r["alarm"] is True
    assert [u["atom"] for u in r["unauthorized"]] == ["D"]           # only the unauthorized one


# ── HELD: red but acknowledged (no alarm), never treated as authorized ─────────────────────
def test_held_promotion_is_RED_but_no_alarm(tmp_path):
    r = _eval(tmp_path, baseline={"A": "idle"}, current={"A": "build"}, ledger=[_hold_entry("A")])
    assert r["status"] == "GATE_HELD" and r["alarm"] is False   # acknowledged -> no page
    assert [h["atom"] for h in r["held"]] == ["A"]              # ...but still tracked red, NOT cleared


def test_held_does_not_count_as_authorization(tmp_path):
    # A hold must NOT clear the atom to green. Only a BUILD_OPEN does. (Don't wave it through.)
    r = _eval(tmp_path, baseline={"A": "idle"}, current={"A": "build"}, ledger=[_hold_entry("A")])
    assert r["status"] != "GATE_CLEAN"


def test_held_plus_a_real_violation_STILL_alarms(tmp_path):
    # A held atom does not mask a DIFFERENT unauthorized promotion -> the wall still alarms on B.
    r = _eval(tmp_path, baseline={"A": "idle", "B": "idle"},
              current={"A": "build", "B": "build"}, ledger=[_hold_entry("A")])
    assert r["status"] == "GATE_VIOLATION" and r["alarm"] is True
    assert [u["atom"] for u in r["unauthorized"]] == ["B"]


def test_record_hold_then_wall_is_held_not_clean(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    G.record_hold("A", "director console msg 2026-07-17: HOLD A pending live L3 verification", path=lp)
    entries = G.read_ledger(lp)
    assert entries and all(G._is_valid_hold(e) for e in entries)
    r = _eval(tmp_path, baseline={"A": "idle"}, current={"A": "build"}, ledger=entries)
    assert r["status"] == "GATE_HELD"


# ── pure predicates ────────────────────────────────────────────────────────────────────────
def test_promotions_since_baseline_pure():
    proms = G.promotions_since_baseline(
        current={"A": "build", "B": "harden", "C": "idle", "E": "build"},
        baseline={"A": "idle", "B": "build", "C": "idle"})        # E absent from baseline -> ignored
    atoms = {p["atom"] for p in proms}
    assert atoms == {"A"}          # A idle->build; B grandfathered; C stayed idle; E new (not baseline)


def test_valid_authorization_predicate():
    assert G._is_valid_authorization(_valid_entry("A")) is True
    assert G._is_valid_authorization({**_valid_entry("A"), "channel": "ntfy"}) is False
    assert G._is_valid_authorization({**_valid_entry("A"), "provenance": "  "}) is False
    assert G._is_valid_authorization({"atom": "A"}) is False
    assert G._is_valid_authorization(None) is False


# ── the record path end to end ─────────────────────────────────────────────────────────────
def test_record_gate_opening_then_wall_is_clean(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    G.record_gate_opening(["A", "D"], "director console msg 2026-07-17: open BUILD on A,D", path=lp)
    entries = G.read_ledger(lp)
    assert {e["atom"] for e in entries} == {"A", "D"}
    assert all(G._is_valid_authorization(e) for e in entries)
    r = _eval(tmp_path, baseline={"A": "idle"}, current={"A": "build"}, ledger=entries)
    assert r["status"] == "GATE_CLEAN"


def test_readers_fail_safe(tmp_path):
    assert G.read_ledger(tmp_path / "nope.jsonl") == []
    assert G.load_baseline(tmp_path / "nope.json") == {}
    assert G.current_loop_stages(tmp_path / "nope.yaml") == {}


# ── the deadman fires it (the running home) -- transition-only ─────────────────────────────
def test_deadman_fires_gate_violation_and_is_transition_only(monkeypatch):
    from background import deadmans_switch as D
    calls = []
    monkeypatch.setattr(D, "send_ntfy", lambda msg, *a, **k: calls.append(msg))
    monkeypatch.setattr(
        "background.gate_authorization.evaluate_gate_wall",
        lambda: {"status": "GATE_VIOLATION", "alarm": True,
                 "detail": "1 BUILD promotion with no director-console authorization: X",
                 "unauthorized": [{"atom": "X", "from": "idle", "to": "build"}]},
    )
    D._last_gate_violation_ts = None
    D._check_gate_wall()
    assert len(calls) == 1 and "GATE VIOLATION" in calls[0]      # the alarm fires
    D._check_gate_wall()
    assert len(calls) == 1                                        # ...once -- transition-only (R5)


def test_deadman_silent_when_gate_clean(monkeypatch):
    from background import deadmans_switch as D
    calls = []
    monkeypatch.setattr(D, "send_ntfy", lambda msg, *a, **k: calls.append(msg))
    monkeypatch.setattr(
        "background.gate_authorization.evaluate_gate_wall",
        lambda: {"status": "GATE_CLEAN", "alarm": False, "detail": "clean", "unauthorized": []},
    )
    D._last_gate_violation_ts = None
    D._check_gate_wall()
    assert calls == []                                           # a clean wall never pages


# ── real-defect smoke: the LIVE wall must be well-formed (report-only, never raises) ───────
def test_live_wall_is_well_formed_and_never_raises():
    r = G.evaluate_gate_wall()
    assert set(r) >= {"status", "alarm", "detail", "unauthorized"}
    assert isinstance(r["alarm"], bool)
    assert r["status"] in ("GATE_CLEAN", "GATE_VIOLATION")
