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

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

from background import gate_authorization as G

REPO = Path(__file__).resolve().parents[2]
MODULE_SOURCE = REPO / "background" / "gate_authorization.py"


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
    world = _world(tmp_path, {"gap_registers_as_mint_sources": "G_data_learning"}, {})
    G.record_level_up_self_certified("gap_registers_as_mint_sources", 3,
                                     "reader background/gap_register_scan.py + gap_register level "
                                     "wired + 12 R15 mutation tests green", path=led, **world)
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


def test_record_level_correction_writes_an_honest_envelope_and_requires_evidence(tmp_path):
    led = tmp_path / "ledger.jsonl"
    G.record_level_correction_self_certified(
        "W1_12_premise_trace_generator", 2,
        "the exit test the L3 rested on stops reproducing at population scale", path=led)
    entries = G.read_ledger(led)
    assert len(entries) == 1
    e = entries[0]
    assert e["action"] == "LEVEL_CORRECTION_SELF_CERTIFIED" and e["level"] == 2
    assert e["authorized_by"] == "agent_self_certified" and e["channel"] == "self"
    with pytest.raises(ValueError):
        G.record_level_correction_self_certified("A", 1, "", path=led)        # no evidence
    with pytest.raises(ValueError):
        G.record_level_correction_self_certified("", 1, "evidence", path=led)  # no atom
    with pytest.raises(ValueError):
        G.record_level_correction_self_certified("A", None, "evidence", path=led)  # no level
    assert len(G.read_ledger(led)) == 1  # only the valid entry was ever written


def test_a_level_correction_can_never_satisfy_a_promotion(tmp_path):
    """THE failable property of the correction row (R15). A demotion is a RECORD, never an
    authority: if `is_valid_level_up` accepted one, recording a demotion to level N would silently
    authorise a PROMOTION to level N at the commit gate.

    The row is written by the REAL recorder rather than hand-built, deliberately. A hand-built
    dict asserts this module's predicate against a literal the test itself controls, so it stays
    green no matter what `record_level_correction_self_certified` actually writes — the tautology
    class that has already been found once inside an R15 test in this codebase. Going through the
    recorder is what makes mutating the source fire this."""
    led = tmp_path / "ledger.jsonl"
    G.record_level_correction_self_certified("W1_12_premise_trace_generator", 2,
                                             "population-scale evidence did not reproduce", path=led)
    written = G.read_ledger(led)[0]
    assert G.is_valid_level_up(written) is False
    assert G.is_valid_self_certified_level_up(written) is False


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


# ══════════════════════════════════════════════════════════════════════════════════════════
# OPS11 — a live BLOCKING finding refuses new level-raises in its OWN lane, and nowhere else
# ══════════════════════════════════════════════════════════════════════════════════════════
#
# Every test below builds its OWN map and its OWN staging root under tmp_path. That is not
# tidiness: the live staging root carries 0 BLOCKING findings today and some number tomorrow,
# so a test reading it would be green or red depending on the day's queue — the control's
# subject would be the weather (`feedback_a_control_that_must_win_a_race_has_the_weather_as_
# its_subject`). The live population is measured in the atom's report, not asserted here.

#: A real, addressable test node used as discharge evidence. `parse_discharge` checks that the
#: file exists AND defines the node, so a made-up path would not release anything — which is
#: itself the property `test_a_discharge_naming_a_nonexistent_test_releases_nothing` pins.
REAL_NODE = "tests/background/test_gate_authorization.py::test_readers_fail_safe"


def _finding(severity="BLOCKING", lane="H_harness", discharged=None, header_ok=True):
    head = f"**Severity:** {severity} · **Lane:** {lane}\n" if header_ok else "no header here\n"
    release = f"**Discharged:** `{discharged}` — repaired in this commit\n" if discharged else ""
    return f"# [WORKER-FINDING] Something\n\n{head}{release}\n## The claim\nBody.\n"


def _world(tmp_path, atoms: dict, findings: dict):
    """A map of {atom: lane} and a staging root of {filename: text}. Returns the kwargs every
    OPS11 entry point takes, so a test never touches the live repo state it is not about."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    map_path = tmp_path / "map.yaml"
    map_path.write_text(yaml.safe_dump({"atoms": [
        {"id": a, "lane": lane, "level_current": 0, "loop_stage": "build"}
        for a, lane in atoms.items()
    ]}), encoding="utf-8")
    root = tmp_path / "staging"
    root.mkdir(exist_ok=True)
    for name, text in findings.items():
        (root / name).write_text(text, encoding="utf-8")
    return {"map_path": map_path, "staging_root": root, "repo_root": REPO}


def _load_mutant(tmp_path: Path, old: str, new: str, name: str):
    """Import a copy of gate_authorization with `old` replaced by `new`. Asserts the mutation
    applied — a no-op mutation makes its test pass for the wrong reason, which is how a
    mutation proof becomes theatre (the anti-pattern R15 names)."""
    source = MODULE_SOURCE.read_text(encoding="utf-8")
    assert source.count(old) == 1, f"mutation anchor is not unique: {old!r}"
    path = tmp_path / f"{name}.py"
    path.write_text(source.replace(old, new), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


# --- the two properties the mutations attack, factored so one assertion serves both ---

def _assert_in_lane_blocker_refuses(module, tmp_path, tag="clean"):
    led = tmp_path / f"{tag}_hold.jsonl"
    world = _world(tmp_path / tag, {"H99_thing": "H_harness"},
                   {"WORKER_FINDING_THE_INSTRUMENT_LIES.md": _finding()})
    with pytest.raises(module.LaneBlockedError) as exc:
        module.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)
    # Exit criterion 1: a refusal that does not name the finding cannot be discharged.
    assert "WORKER_FINDING_THE_INSTRUMENT_LIES.md" in str(exc.value)
    assert not led.exists(), "a REFUSED raise must leave no ledger row -- the row is the thing "\
                             "the commit gate later reads as authority"


def _assert_other_lane_is_untouched(module, tmp_path, tag="clean"):
    led = tmp_path / f"{tag}_pass.jsonl"
    world = _world(tmp_path / f"{tag}_other", {"D9_bill": "D_billing_metering"},
                   {"WORKER_FINDING_THE_INSTRUMENT_LIES.md": _finding(lane="H_harness")})
    module.record_level_up_self_certified("D9_bill", 2, "evidence", path=led, **world)
    written = module.read_ledger(led)
    assert len(written) == 1 and written[0]["atom"] == "D9_bill"


def test_a_live_in_lane_blocker_refuses_the_level_record(tmp_path):
    """THE hold. A BLOCKING finding in lane H_harness refuses a level-raise on an H_harness
    atom, at the place the level is actually recorded."""
    _assert_in_lane_blocker_refuses(G, tmp_path)


def test_a_blocker_in_another_lane_does_not_refuse(tmp_path):
    """THE lane scope, second direction (exit criterion 2). The same live blocker that holds
    H_harness leaves D_billing_metering completely alone -- 'progress in every other lane
    continues untouched' is the half of clause 2 a repo-wide freeze would violate."""
    _assert_other_lane_is_untouched(G, tmp_path)


def test_mutation_a_dropping_the_blocking_check_kills_a_named_test(tmp_path):
    """R15 direction 1: a mutation that lets a raise through with a live in-lane blocker."""
    mutant = _load_mutant(
        tmp_path,
        "elif parsed.is_blocking and parsed.lane == lane:",
        "elif parsed.is_blocking and False:",
        "gate_auth_mutant_fail_open",
    )
    _assert_other_lane_is_untouched(mutant, tmp_path, tag="m1")  # the clean direction survives
    # Both outcomes are the named test FAILING: `pytest.fail.Exception` is what a missing raise
    # reports as, and it does not inherit from AssertionError -- catching only the latter would
    # make this mutation proof pass for the wrong reason.
    with pytest.raises((AssertionError, pytest.fail.Exception)):
        _assert_in_lane_blocker_refuses(mutant, tmp_path, tag="m1")


def test_mutation_b_dropping_the_lane_scope_kills_a_named_test(tmp_path):
    """R15 direction 2: a mutation that refuses an UNAFFECTED lane. Without this direction the
    control could be 'proven' by a version that refuses everything, which is the freeze clause
    2 explicitly forbids."""
    mutant = _load_mutant(
        tmp_path,
        "parsed.is_blocking and parsed.lane == lane:",
        "parsed.is_blocking:",
        "gate_auth_mutant_no_lane_scope",
    )
    _assert_in_lane_blocker_refuses(mutant, tmp_path, tag="m2")  # the hold still holds under it
    with pytest.raises(mutant.LaneBlockedError):
        _assert_other_lane_is_untouched(mutant, tmp_path, tag="m2")


# ── R11: the RELEASE is tested, not just the hold ─────────────────────────────────────────

def test_repairing_the_finding_lets_the_next_raise_through(tmp_path):
    """RELEASE 1. The hold is real, then the document gains a CHECKED discharge line and the
    same raise goes through and lands its row. A hold whose release does nothing is the defect
    R11 names, so the release is asserted on the ledger, never on the absence of an exception."""
    led = tmp_path / "ledger.jsonl"
    world = _world(tmp_path, {"H99_thing": "H_harness"},
                   {"WORKER_FINDING_THE_INSTRUMENT_LIES.md": _finding()})
    with pytest.raises(G.LaneBlockedError):
        G.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)

    (world["staging_root"] / "WORKER_FINDING_THE_INSTRUMENT_LIES.md").write_text(
        _finding(discharged=REAL_NODE), encoding="utf-8")
    G.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)
    assert [e["atom"] for e in G.read_ledger(led)] == ["H99_thing"]


def test_recording_and_accepting_the_limitation_lets_the_next_raise_through(tmp_path):
    """RELEASE 2 -- the discharge that always exists, which is what makes the fail-closed
    direction safe rather than a wedge."""
    led = tmp_path / "ledger.jsonl"
    world = _world(tmp_path, {"H99_thing": "H_harness"},
                   {"WORKER_FINDING_THE_INSTRUMENT_LIES.md": _finding()})
    with pytest.raises(G.LaneBlockedError):
        G.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)

    G.record_limitation_accepted("H_harness", "WORKER_FINDING_THE_INSTRUMENT_LIES.md",
                                 "the raise rests on a control this finding does not touch",
                                 path=led)
    G.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)
    assert [e["action"] for e in G.read_ledger(led)] == ["LIMITATION_ACCEPTED",
                                                         "LEVEL_UP_SELF_CERTIFIED"]


def test_an_acceptance_releases_only_the_finding_it_names(tmp_path):
    """The acceptance is per-(lane, finding) for a reason: a blanket 'accept this lane' row
    would clear findings nobody enumerated, which is the fail-open shape of every rubber stamp."""
    led = tmp_path / "ledger.jsonl"
    world = _world(tmp_path, {"H99_thing": "H_harness"},
                   {"WORKER_FINDING_ONE.md": _finding(), "WORKER_FINDING_TWO.md": _finding()})
    G.record_limitation_accepted("H_harness", "WORKER_FINDING_ONE.md", "sound anyway", path=led)
    with pytest.raises(G.LaneBlockedError) as exc:
        G.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)
    assert "WORKER_FINDING_TWO.md" in str(exc.value)
    assert "WORKER_FINDING_ONE.md" not in str(exc.value)

    G.record_limitation_accepted("H_harness", "WORKER_FINDING_TWO.md", "sound anyway", path=led)
    G.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)
    assert any(e["action"] == "LEVEL_UP_SELF_CERTIFIED" for e in G.read_ledger(led))


def test_an_acceptance_survives_the_finding_being_archived(tmp_path):
    """The acceptance keys on the BASENAME, because a document moves to `done/` in the ordinary
    course of the machine and a release that evaporated on a `git mv` would un-release itself."""
    led = tmp_path / "ledger.jsonl"
    G.record_limitation_accepted("H_harness", "docs/staging/WORKER_FINDING_ONE.md", "sound",
                                 path=led)
    assert G.accepted_limitations(G.read_ledger(led)) == {("H_harness", "WORKER_FINDING_ONE.md")}


# ── fail-closed, in each of the three ways the check can be unavailable ────────────────────

def test_an_absent_staging_root_refuses_and_is_still_dischargeable(tmp_path):
    """FAIL-CLOSED (R15 killer pattern 3): an unavailable severity index is a FAILED check, not
    a clear lane. The second half is what stops that being a wedge -- the UNKNOWN reads under a
    stable identity that record-and-accept can release."""
    led = tmp_path / "ledger.jsonl"
    world = _world(tmp_path, {"H99_thing": "H_harness"}, {})
    world["staging_root"] = tmp_path / "does_not_exist"
    with pytest.raises(G.LaneBlockedError) as exc:
        G.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)
    assert G.UNREADABLE_INDEX_FINDING in str(exc.value)

    G.record_limitation_accepted("H_harness", G.UNREADABLE_INDEX_FINDING,
                                 "index unavailable in this environment; move reviewed by hand",
                                 path=led)
    G.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)
    assert any(e["action"] == "LEVEL_UP_SELF_CERTIFIED" for e in G.read_ledger(led))


def test_an_unclassified_document_refuses_every_lane(tmp_path):
    """A document whose severity cannot be read might BE the blocker, and its lane is unknown.
    Attributing it to no lane would make mangling a header the cheapest way to clear a hold."""
    led = tmp_path / "ledger.jsonl"
    world = _world(tmp_path, {"D9_bill": "D_billing_metering"},
                   {"WORKER_FINDING_NO_HEADER.md": _finding(header_ok=False)})
    with pytest.raises(G.LaneBlockedError) as exc:
        G.record_level_up_self_certified("D9_bill", 2, "evidence", path=led, **world)
    assert "UNCLASSIFIED" in str(exc.value)


def test_an_atom_with_no_lane_in_the_map_is_refused_under_unknown_lane(tmp_path):
    """'I cannot tell which lane this is' is not evidence that the lane is clear. If it were,
    deleting an atom's lane would be the cheapest escape from every hold."""
    led = tmp_path / "ledger.jsonl"
    world = _world(tmp_path, {"OTHER": "H_harness"}, {})
    with pytest.raises(G.LaneBlockedError) as exc:
        G.record_level_up_self_certified("H99_absent_from_map", 2, "evidence", path=led, **world)
    assert G.UNKNOWN_LANE in str(exc.value)
    assert not led.exists()


# ── the acceptance row cannot be a rubber stamp ───────────────────────────────────────────

def test_an_acceptance_requires_lane_finding_and_a_stated_reason(tmp_path):
    led = tmp_path / "ledger.jsonl"
    for bad in (("", "F.md", "why"), ("H_harness", "", "why"), ("H_harness", "F.md", "  ")):
        with pytest.raises(ValueError):
            G.record_limitation_accepted(*bad, path=led)
    assert not led.exists()


def test_a_forged_acceptance_releases_nothing():
    """Same honesty envelope as every other row: a hand-stamped 'director'/'console' acceptance
    is not one, so a forged row clears no lane -- exactly as a forged level record clears none."""
    honest = {"action": "LIMITATION_ACCEPTED", "authorized_by": "agent_self_certified",
              "channel": "self", "lane": "H_harness", "finding": "F.md", "provenance": "why"}
    assert G.is_valid_limitation_acceptance(honest) is True
    for forged in ({**honest, "authorized_by": "director"}, {**honest, "channel": "console"},
                   {**honest, "provenance": ""}, {**honest, "action": "LEVEL_UP_SELF_CERTIFIED"}):
        assert G.is_valid_limitation_acceptance(forged) is False


def test_a_discharge_naming_a_nonexistent_test_releases_nothing(tmp_path):
    """The repair release is only as good as its evidence check. A discharge line citing a test
    node that does not exist leaves the finding BLOCKING and the lane held."""
    led = tmp_path / "ledger.jsonl"
    world = _world(tmp_path, {"H99_thing": "H_harness"}, {
        "WORKER_FINDING_ONE.md": _finding(discharged="tests/nope/test_nothing.py::test_absent")})
    with pytest.raises(G.LaneBlockedError):
        G.record_level_up_self_certified("H99_thing", 2, "evidence", path=led, **world)
