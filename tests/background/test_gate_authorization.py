"""LEVEL-RECORD ledger: what remains of gate_authorization after the permission machinery was
removed (2026-08-03, director console, finishing DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY).

WHAT THIS FILE USED TO TEST, and why it is gone. It was the GATE-WALL detection control: an
idle->build promotion with no director-console authorization ALARMED, an authorized one stayed
quiet, and an invalid/forged authorization did not silence it. Every one of those behaviours was
an answer to "has the director permitted this?", which is no longer a question the system asks --
so `evaluate_gate_wall`, `authorized_atoms`, the HELD records, the FRONT_OPEN/GATE_CLEAR family,
the twin's L1/L2 ratification and the phone-HMAC channel were all deleted, and their tests with
them.

WHAT SURVIVES, and why it is still worth a control. "Propose, record, act" keeps the RECORD: a
level move must leave an auditable trace of what moved and on what evidence (R16's real
requirement, which was never that a human authorise it). These tests hold that line -- the record
must be honest about who wrote it, must carry evidence, and must be refused when it does not.
"""
from __future__ import annotations

import pytest

from background import gate_authorization as G


def _self_cert_entry(atom="A1", level=2, provenance="tests green + R15 mutation proof"):
    return {"atom": atom, "action": "LEVEL_UP_SELF_CERTIFIED",
            "authorized_by": "agent_self_certified", "channel": "self",
            "level": level, "provenance": provenance}


# ── the record is valid at ANY level: there is no reserved tier left ───────────────────────
def test_self_certified_level_up_valid_at_any_level():
    assert G.is_valid_self_certified_level_up(_self_cert_entry(level=1)) is True
    assert G.is_valid_self_certified_level_up(_self_cert_entry(level=3)) is True
    assert G.is_valid_self_certified_level_up(_self_cert_entry(level=99)) is True
    # L3 was the director's "this is real" tier; it is now recorded like any other.
    assert G.is_valid_level_up(_self_cert_entry(level=3)) is True


# ── R15: the control FIRES on its own defect (an unevidenced or dishonest record) ──────────
def test_self_certified_needs_atom_and_nonempty_provenance():
    assert G.is_valid_self_certified_level_up(_self_cert_entry(provenance="")) is False
    assert G.is_valid_self_certified_level_up({**_self_cert_entry(), "atom": ""}) is False


def test_a_forged_record_is_not_a_record():
    """The honesty requirement is what is load-bearing now. An entry claiming to be a
    self-certification while stamping a different author/channel is NOT a valid record -- so the
    pre-commit level gate still refuses the commit that carries it."""
    forged = {**_self_cert_entry(), "authorized_by": "worker", "channel": "agent"}
    assert G.is_valid_self_certified_level_up(forged) is False
    assert G.is_valid_level_up(forged) is False


def test_legacy_director_and_twin_entries_are_history_not_authority():
    """A console LEVEL_UP_PROPOSED or a twin LEVEL_UP_TWIN already in the ledger stays readable as
    history, but is no longer a separate authority -- the mover self-certifies instead. This is the
    mutation that proves the permission path is really gone rather than merely unused."""
    console = {"atom": "A1", "action": "LEVEL_UP_PROPOSED", "authorized_by": "director",
               "channel": "console", "level": 3, "provenance": "director console 2026-07-21"}
    twin = {"atom": "A1", "action": "LEVEL_UP_TWIN", "authorized_by": "director_twin",
            "channel": "twin", "level": 2, "provenance": "twin canon verdict"}
    assert G.is_valid_level_up(console) is False
    assert G.is_valid_level_up(twin) is False


def test_record_level_up_self_certified_writes_honest_envelope_and_requires_evidence(tmp_path):
    led = tmp_path / "ledger.jsonl"
    G.record_level_up_self_certified("gap_registers_as_mint_sources", 3,
                                     "reader background/gap_register_scan.py + gap_register level "
                                     "wired + 12 R15 mutation tests green", path=led)
    entries = G.read_ledger(led)
    assert len(entries) == 1
    e = entries[0]
    assert e["authorized_by"] == "agent_self_certified" and e["channel"] == "self"
    assert e["action"] == "LEVEL_UP_SELF_CERTIFIED" and e["level"] == 3
    assert G.is_valid_level_up(e) is True
    with pytest.raises(ValueError):
        G.record_level_up_self_certified("A", 1, "", path=led)          # no evidence -> refused
    with pytest.raises(ValueError):
        G.record_level_up_self_certified("", 1, "evidence", path=led)   # no atom -> refused
    assert len(G.read_ledger(led)) == 1  # only the valid entry was ever written


def test_readers_fail_safe(tmp_path):
    assert G.read_ledger(tmp_path / "nope.jsonl") == []
    assert G.load_baseline(tmp_path / "nope.json") == {}


def test_the_permission_surface_is_gone():
    """A NAMED anti-regression: these are the entry points the ruling deleted. If any of them comes
    back, the convention has regrown -- this fails loudly rather than letting the machinery quietly
    re-gate a draw."""
    for name in ("authorized_atoms", "held_atoms", "evaluate_gate_wall", "unauthorized_promotions",
                 "is_valid_front_open", "is_valid_front_close", "is_valid_gate_clear",
                 "is_valid_twin_level_up", "record_twin_level_up", "record_front_open",
                 "record_gate_clear", "record_gate_opening", "record_hold",
                 "record_director_ntfy_ruling", "parse_ledger_directives",
                 "confirm_authenticated_release", "report_ruling_release"):
        assert not hasattr(G, name), f"{name} is permission machinery and must stay deleted"
