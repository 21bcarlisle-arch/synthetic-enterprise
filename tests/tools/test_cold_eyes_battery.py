"""R15 for `tools/cold_eyes_battery` — the control must fire on its own named defect.

The named defect is a SHIPPED one and it is still in the tree: `wall_channel_census.
cold_eyes_walk_outstanding` returns `()` on the live repository while nine of the battery's
twelve DISQUALIFYING questions do not pass. The first test below is the mutation, and it is
not a hand-built fixture — it runs both predicates against the real ledger and asserts they
disagree in the direction that matters.
"""

from __future__ import annotations

import json

import pytest

from tools import cold_eyes_battery as ceb
from tools.cold_eyes_battery import BatteryUnavailable

CAP = "EP6_wall_protocol_typing"


def _battery(*questions: tuple[int, str]) -> list[dict]:
    return [
        {"n": n, "group": "g", "question": f"q{n}", "verdict": verdict, "answer_needed": "a"}
        for n, verdict in questions
    ]


def _ledger(tmp_path, battery, capability=CAP):
    path = tmp_path / "ledger.jsonl"
    path.write_text(json.dumps({"capability": capability, "battery": battery}) + "\n")
    return path


def _recon(tmp_path, rows):
    path = tmp_path / "recon.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path


def _row(n, verdict="PASS", capability=CAP, **extra):
    return {"capability": capability, "n": n, "verdict": verdict, "evidence": "e", **extra}


# ── THE MUTATION: the shipped predicate, on the live tree ─────────────────────────────────

def test_MUTATION_the_shipped_predicate_says_unblocked_while_real_criteria_fail():
    """The defect this module exists to repair, asserted against the REAL tree.

    `cold_eyes_walk_outstanding` greens on the mere existence of a review record. Pass 33
    wrote that greening on that fact "would make the instrument a ceremony" and then shipped
    exactly that. If this test ever goes red because the two agree, the repair has landed
    somewhere else and this module is redundant — which is a fact worth being told.

    THE CLAIM IS A DIVERGENCE, NOT A COUNT (EP6 pass 48). This asserted
    `len(outstanding) >= 9` until Q10 was answered and the live set moved 9 -> 8, which
    redded the control on its own success case: the number nine was never the law, it was
    the size of the backlog on the morning the test was written, and pinning it made every
    question this battery closes look like a regression. That is this project's recorded
    COUNT-PINNED class, and the repair is to assert the thing that is actually true for as
    long as the defect exists — the two instruments DISAGREE, one reporting clear while the
    other holds real questions open. It can still fail in both of its meaningful directions:
    if the shipped predicate ever starts reporting, or if the battery ever empties.
    """
    from tools.wall_channel_census import cold_eyes_walk_outstanding

    assert cold_eyes_walk_outstanding() == (), "the shipped predicate no longer reports unblocked"

    outstanding = ceb.battery_outstanding()
    assert outstanding, "the battery is empty, so there is no divergence left to demonstrate"
    # The single sharpest one: no counterparty identity exists anywhere below the port.
    assert "Q13" in outstanding


def test_the_live_reconciliation_covers_every_disqualifying_question():
    """No question may be silently unanswered: the file is complete or the atom is blocked."""
    questions = ceb.disqualifying_questions()
    rows = ceb.load_reconciliations()
    assert set(rows) == set(questions), sorted(set(questions) - set(rows))


def test_EP6_MAY_NOT_BE_RECORDED_AT_L3_WHILE_ITS_OWN_BATTERY_IS_OUTSTANDING():
    """THE CONSUMER. Without this the reconciliation is a document, not a criterion.

    Deliberately scoped to the EVENT (a level-3 claim for this one atom) and not to every
    commit. A census half that redded while nine questions were outstanding would refuse
    every commit on the shared tree — born red, wedging every other lane, and the first
    thing anyone would do is relax it. This fires exactly once, on the move it is about.

    The failure it prevents is concrete and has already happened once in prose: pass 33 had
    a recorded walk, a predicate returning `()`, and two confirmed DISQUALIFYING failures.
    Nothing but that pass's own judgement stood between that state and a level move.
    """
    import yaml

    atoms = yaml.safe_load((ceb.PROJECT_DIR / "docs/design/maturity_map.yaml").read_text())
    if isinstance(atoms, dict):
        atoms = atoms.get("atoms")
    cell = next((a for a in atoms if a.get("id") == CAP), None)
    assert cell is not None, f"{CAP} is not in the map -- the criterion has lost its subject"

    outstanding = ceb.battery_outstanding()
    if outstanding:
        assert cell["level_current"] < 3, (
            f"{CAP} is recorded at level {cell['level_current']} while its cold-eyes battery "
            f"still has {len(outstanding)} DISQUALIFYING question(s) outstanding: "
            f"{list(outstanding)}. L3 is 'Expert Hour: this is real' and the expert's own "
            f"questions say otherwise. Answer them in "
            f"{ceb.RECONCILIATION_REL} with evidence, or move the level back."
        )


def test_unpayable_here_is_a_strict_subset_of_outstanding_on_the_live_tree():
    outstanding = set(ceb.battery_outstanding())
    unpayable = set(ceb.unpayable_here())
    assert unpayable <= outstanding
    assert unpayable == {"Q9", "Q15"}, unpayable


# ── FAIL-OPEN: the reassuring answers a broken read produces ──────────────────────────────

def test_FAIL_OPEN_a_battery_with_no_disqualifying_questions_RAISES(tmp_path):
    """Zero disqualifying questions is what a flawless capability looks like AND what a
    broken parse looks like. They are not the same, so it is refused."""
    ledger = _ledger(tmp_path, _battery((1, "SUPPORTING"), (2, "SUPPORTING")))
    with pytest.raises(BatteryUnavailable, match="ZERO DISQUALIFYING"):
        ceb.battery_outstanding(ledger_path=ledger)


def test_FAIL_OPEN_a_recorded_walk_with_an_empty_battery_RAISES(tmp_path):
    ledger = tmp_path / "l.jsonl"
    ledger.write_text(json.dumps({"capability": CAP, "battery": []}) + "\n")
    with pytest.raises(BatteryUnavailable, match="no readable battery"):
        ceb.battery_outstanding(ledger_path=ledger)


def test_FAIL_OPEN_an_absent_reconciliation_blocks_every_question(tmp_path):
    """Silence must BLOCK. This is the direction that makes the authored file safe."""
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING"), (2, "DISQUALIFYING")))
    out = ceb.battery_outstanding(
        ledger_path=ledger, reconciliation_path=tmp_path / "does_not_exist.jsonl"
    )
    assert out == ("Q1", "Q2")


def test_FAIL_SILENT_an_unreadable_ledger_RAISES(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text("{not json\n")
    with pytest.raises(BatteryUnavailable, match="could not be read"):
        ceb.battery_outstanding(ledger_path=bad)


def test_FAIL_SILENT_an_unreadable_reconciliation_RAISES(tmp_path):
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    bad = tmp_path / "bad.jsonl"
    bad.write_text("{not json\n")
    with pytest.raises(BatteryUnavailable, match="not readable JSON"):
        ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=bad)


# ── the vocabulary and the join, both fail-closed ─────────────────────────────────────────

def test_a_row_missing_its_evidence_RAISES(tmp_path):
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    recon = _recon(tmp_path, [{"capability": CAP, "n": 1, "verdict": "PASS"}])
    with pytest.raises(BatteryUnavailable, match="missing"):
        ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=recon)


def test_an_unrecognised_verdict_is_not_a_pass(tmp_path):
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1, verdict="PARTIAL")])
    with pytest.raises(BatteryUnavailable, match="outside"):
        ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=recon)


def test_two_rows_for_one_question_RAISES_rather_than_taking_either(tmp_path):
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1, verdict="FAIL"), _row(1, verdict="PASS")])
    with pytest.raises(BatteryUnavailable, match="SECOND row"):
        ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=recon)


def test_DRIFT_a_row_for_a_question_the_battery_does_not_carry_RAISES(tmp_path):
    """An answer to a question nobody asked would sit there looking like progress."""
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1), _row(99)])
    with pytest.raises(BatteryUnavailable, match="drifted"):
        ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=recon)


def test_a_row_for_another_capability_is_ignored_not_counted(tmp_path):
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1, capability="SOMETHING_ELSE")])
    assert ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=recon) == ("Q1",)


# ── NULL CONTROLS: the success case must be reachable, and must need work ─────────────────

def test_NULL_CONTROL_every_question_passing_clears_the_criterion(tmp_path):
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING"), (2, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1), _row(2)])
    assert ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=recon) == ()


def test_NULL_CONTROL_a_supporting_question_left_unanswered_does_not_block(tmp_path):
    """The reviewer's own DISQUALIFYING/SUPPORTING split is respected, not overridden."""
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING"), (2, "SUPPORTING")))
    recon = _recon(tmp_path, [_row(1)])
    assert ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=recon) == ()


def test_no_walk_recorded_reports_the_walk_itself_as_the_criterion(tmp_path):
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")), capability="OTHER_ATOM")
    assert ceb.battery_outstanding(ledger_path=ledger) == (ceb.COLD_EYES_WALK_CRITERION,)


# ── the epoch_gated flag can narrow, never widen ──────────────────────────────────────────

def test_epoch_gated_on_a_PASSING_question_does_not_make_it_unpayable(tmp_path):
    """The flag is consulted only on questions already outstanding, so it cannot invent one."""
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1, verdict="PASS", epoch_gated=True)])
    assert ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=recon) == ()
    assert ceb.unpayable_here(ledger_path=ledger, reconciliation_path=recon) == ()


def test_an_ungated_failure_is_outstanding_but_not_unpayable(tmp_path):
    """The distinction the pair exists for: ordinary build work must keep being drawn."""
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING"), (2, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1, verdict="FAIL"), _row(2, verdict="FAIL", epoch_gated=True)])
    assert ceb.battery_outstanding(ledger_path=ledger, reconciliation_path=recon) == ("Q1", "Q2")
    assert ceb.unpayable_here(ledger_path=ledger, reconciliation_path=recon) == ("Q2",)
