"""Tests for background/inbound_ratification.py -- the batched inbound-ratification path
(GAP-M2 BUILD half (b)/(c), DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28 §2).

R15 both-ways is MANDATORY here and is called out explicitly:
  * MUTATION (control FIRES):   test_held_into_move_does_not_silently_land
  * PASS-THROUGH (asymmetry):   test_out_toward_mint_passes_without_escalation
  * FAIL-SAFE (ambiguous->held): test_ambiguous_direction_is_held
"""
from __future__ import annotations

import json

import pytest

from background import inbound_ratification as ir
from background.inbound_ratification import (
    BLOCKED_ON_DIRECTOR,
    DELIBERATE,
    MINT,
    NOT_WORTH,
)


@pytest.fixture
def ledger(tmp_path):
    return tmp_path / "gap_bucket_ratifications.jsonl"


@pytest.fixture
def register(tmp_path):
    return tmp_path / "action_needed_register.json"


# --------------------------------------------------------------------------- normalisation
def test_normalize_accepts_underscore_and_space_variants():
    assert ir.normalize_bucket("deliberate_and_staying") == DELIBERATE
    assert ir.normalize_bucket("  Deliberate-And-Staying ") == DELIBERATE
    assert ir.normalize_bucket("not worth the complexity") == NOT_WORTH


def test_normalize_rejects_unknown_and_nonstring():
    assert ir.normalize_bucket("closed") is None
    assert ir.normalize_bucket("") is None
    assert ir.normalize_bucket(None) is None
    assert ir.normalize_bucket(42) is None


# --------------------------------------------------------------------------- classify_move
def test_into_deliberate_unratified_is_held():
    assert ir.classify_move(DELIBERATE, None) == "held"
    assert ir.classify_move(DELIBERATE, MINT) == "held"
    assert ir.classify_move(DELIBERATE, NOT_WORTH) == "held"


def test_into_deliberate_already_ratified_is_autonomous():
    # A re-run of the method over an already director-ratified deliberate gap must NOT re-escalate.
    assert ir.classify_move(DELIBERATE, DELIBERATE) == "autonomous"


def test_out_toward_mint_passes_without_escalation():
    # PASS-THROUGH (R15): the asymmetry is real, not a blanket gate. A move OUT toward mint --
    # even from a previously-ratified deliberate disposition -- is autonomous.
    assert ir.classify_move(MINT, DELIBERATE) == "autonomous"
    assert ir.classify_move(MINT, None) == "autonomous"


def test_moves_among_other_three_buckets_are_autonomous():
    for proposed in (MINT, BLOCKED_ON_DIRECTOR, NOT_WORTH):
        for ratified in (MINT, BLOCKED_ON_DIRECTOR, NOT_WORTH, None):
            assert ir.classify_move(proposed, ratified) == "autonomous"


def test_ambiguous_direction_is_held():
    # FAIL-SAFE (R15): an unrecognizable/ambiguous proposed bucket is treated as INTO (held),
    # never autonomous -- silence never retires a red.
    assert ir.classify_move("???", None) == "held"
    assert ir.classify_move(None, MINT) == "held"
    assert ir.classify_move("", MINT) == "held"


# --------------------------------------------------------------------------- operative_bucket (HELD guarantee)
def test_held_into_move_does_not_silently_land():
    # MUTATION / control FIRES (R15): the operative disposition of a HELD into-move is the PRIOR
    # bucket, NEVER the proposed deliberate-and-staying. If the hold path were neutered (returned the
    # proposed bucket), this assertion would red -- that is the defect the control closes: an honest
    # red silently retired as "deliberate".
    assert ir.operative_bucket(DELIBERATE, MINT) == MINT
    assert ir.operative_bucket(DELIBERATE, NOT_WORTH) == NOT_WORTH
    assert ir.operative_bucket(DELIBERATE, None) == MINT  # never ratified -> prior is mint
    assert ir.operative_bucket(DELIBERATE, MINT) != DELIBERATE


def test_operative_autonomous_move_applies_as_proposed():
    assert ir.operative_bucket(MINT, DELIBERATE) == MINT
    assert ir.operative_bucket(BLOCKED_ON_DIRECTOR, MINT) == BLOCKED_ON_DIRECTOR
    # Already-ratified deliberate re-proposed as deliberate applies (it is autonomous, no re-hold).
    assert ir.operative_bucket(DELIBERATE, DELIBERATE) == DELIBERATE


def test_ambiguous_operative_falls_back_to_mint():
    # Ambiguous proposed -> held -> prior bucket; unknown prior falls back to mint (Rule-0 direction).
    assert ir.operative_bucket("???", None) == MINT
    assert ir.operative_bucket("???", NOT_WORTH) == NOT_WORTH


# --------------------------------------------------------------------------- classify_triage_run
def test_classify_triage_run_partitions_and_annotates_prior():
    rows = [
        {"gap_id": "G1", "proposed_bucket": DELIBERATE, "argument": "small", "measured_bound": "<1%"},
        {"gap_id": "G2", "proposed_bucket": MINT},
        {"gap_id": "G3", "proposed_bucket": DELIBERATE},  # already ratified below
        {"gap_id": "G4", "proposed_bucket": "garbage"},   # ambiguous -> held
    ]
    ratifications = {"G3": DELIBERATE, "G1": NOT_WORTH}
    parts = ir.classify_triage_run(rows, ratifications=ratifications)
    held_ids = {r["gap_id"] for r in parts["held"]}
    auto_ids = {r["gap_id"] for r in parts["autonomous"]}
    assert held_ids == {"G1", "G4"}
    assert auto_ids == {"G2", "G3"}
    g1 = next(r for r in parts["held"] if r["gap_id"] == "G1")
    assert g1["prior_bucket"] == NOT_WORTH  # stays in its last ratified bucket
    g4 = next(r for r in parts["held"] if r["gap_id"] == "G4")
    assert g4["prior_bucket"] == MINT  # never ratified -> mint


# --------------------------------------------------------------------------- batching
def test_empty_batch_is_none():
    assert ir.build_ratification_batch([]) is None


def test_batch_carries_required_fields():
    held = [{"gap_id": "G1", "prior_bucket": MINT, "argument": "arg", "measured_bound": "<2%"}]
    batch = ir.build_ratification_batch(held)
    assert batch["kind"] == "inbound-ratification-batch"
    assert batch["count"] == 1
    row = batch["rows"][0]
    assert row["gap_id"] == "G1"
    assert row["prior_bucket"] == MINT
    assert row["proposed_bucket"] == DELIBERATE
    assert row["argument"] == "arg"
    assert row["measured_bound"] == "<2%"


# --------------------------------------------------------------------------- escalation (channel C)
def test_empty_batch_escalates_nothing():
    sent = []
    assert ir.escalate_batch(None, send_ntfy_fn=lambda m, **k: sent.append(m) or "id") is False
    assert ir.escalate_batch({"rows": []}, send_ntfy_fn=lambda m, **k: sent.append(m) or "id") is False
    assert sent == []  # no empty-batch noise


def test_escalate_batch_sends_via_act_once_then_silent(register):
    sent = []

    def fake_send(msg, **kwargs):
        sent.append(msg)
        return "posted-id"

    batch = ir.build_ratification_batch(
        [{"gap_id": "G1", "prior_bucket": MINT, "argument": "a", "measured_bound": "<1%"}]
    )
    first = ir.escalate_batch(batch, register_path=register, send_ntfy_fn=fake_send, now="2026-07-28T10:00:00+00:00")
    assert first is True
    assert len(sent) == 1
    assert sent[0].startswith("[ACTION NEEDED] " + ir.ACT_ITEM_ID)
    # Same cycle again -> fire-once-then-daily: registered but NOT re-sent (never the window either).
    second = ir.escalate_batch(batch, register_path=register, send_ntfy_fn=fake_send, now="2026-07-28T10:01:00+00:00")
    assert second is False
    assert len(sent) == 1


def test_failed_send_leaves_item_due(register):
    # A send returning no id must NOT advance the send-clock (register-vs-sent discipline).
    batch = ir.build_ratification_batch([{"gap_id": "G1", "prior_bucket": MINT}])
    result = ir.escalate_batch(batch, register_path=register, send_ntfy_fn=lambda m, **k: None,
                               now="2026-07-28T10:00:00+00:00")
    assert result is False
    from background import action_needed
    assert action_needed.should_notify(ir.ACT_ITEM_ID, path=register, now="2026-07-28T10:05:00+00:00") is True


# --------------------------------------------------------------------------- ledger read/record
def test_record_ratification_flips_and_stops_reescalation(ledger):
    # Before ratification an into-move is HELD; after the director ratifies, a re-run is autonomous.
    rows = [{"gap_id": "G1", "proposed_bucket": DELIBERATE, "argument": "a", "measured_bound": "<1%"}]
    assert ir.classify_triage_run(rows, ledger_path=ledger)["held"]
    ir.record_ratification("G1", DELIBERATE, authorized_by="director",
                           provenance="console 2026-07-28", path=ledger)
    parts = ir.classify_triage_run(rows, ledger_path=ledger)
    assert parts["held"] == []
    assert {r["gap_id"] for r in parts["autonomous"]} == {"G1"}


def test_record_ratification_last_line_wins(ledger):
    ir.record_ratification("G1", MINT, authorized_by="director", provenance="p1", path=ledger)
    ir.record_ratification("G1", DELIBERATE, authorized_by="director", provenance="p2", path=ledger)
    assert ir.load_ratifications(ledger)["G1"] == DELIBERATE


def test_record_ratification_requires_authority(ledger):
    with pytest.raises(ValueError):
        ir.record_ratification("G1", DELIBERATE, authorized_by="", provenance="p", path=ledger)
    with pytest.raises(ValueError):
        ir.record_ratification("G1", DELIBERATE, authorized_by="director", provenance="  ", path=ledger)
    with pytest.raises(ValueError):
        ir.record_ratification("G1", "not-a-bucket", authorized_by="director", provenance="p", path=ledger)


def test_load_ratifications_failsafe_on_unreadable(tmp_path):
    assert ir.load_ratifications(tmp_path / "missing.jsonl") == {}  # missing -> empty (hold-safe)
    garbled = tmp_path / "garbled.jsonl"
    garbled.write_text("not json\n{\"gap_id\": \"G1\", \"bucket\": \"mint\"}\n{bad\n", encoding="utf-8")
    # The one valid line is read; the garbled lines are skipped, never trusted.
    assert ir.load_ratifications(garbled) == {"G1": MINT}


def test_load_ratifications_ignores_unknown_bucket_line(ledger):
    ledger.write_text(json.dumps({"gap_id": "G1", "bucket": "closed"}) + "\n", encoding="utf-8")
    assert ir.load_ratifications(ledger) == {}  # unknown bucket -> not a valid ratification


# --------------------------------------------------------------------------- end-to-end entrypoint
def test_process_triage_run_holds_escalates_and_reports_operative(ledger, register):
    sent = []
    rows = [
        {"gap_id": "G1", "proposed_bucket": DELIBERATE, "argument": "a", "measured_bound": "<1%"},
        {"gap_id": "G2", "proposed_bucket": MINT},
    ]
    out = ir.process_triage_run(
        rows, ledger_path=ledger, register_path=register,
        send_ntfy_fn=lambda m, **k: sent.append(m) or "id", now="2026-07-28T10:00:00+00:00",
    )
    assert {r["gap_id"] for r in out["held"]} == {"G1"}
    assert {r["gap_id"] for r in out["autonomous"]} == {"G2"}
    assert out["escalated"] is True and len(sent) == 1
    # HELD guarantee: G1's operative disposition is its prior bucket (mint), NOT deliberate.
    assert out["operative"] == {"G1": MINT, "G2": MINT}


def test_process_triage_run_no_into_moves_is_silent(ledger, register):
    sent = []
    rows = [{"gap_id": "G2", "proposed_bucket": MINT}, {"gap_id": "G3", "proposed_bucket": BLOCKED_ON_DIRECTOR}]
    out = ir.process_triage_run(
        rows, ledger_path=ledger, register_path=register,
        send_ntfy_fn=lambda m, **k: sent.append(m) or "id",
    )
    assert out["held"] == []
    assert out["batch"] is None
    assert out["escalated"] is False
    assert sent == []
