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
    from tools import maturity_map_store as map_store

    atoms = map_store.load_atoms(ceb.PROJECT_DIR / "docs/design/maturity_map.yaml")
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


# ── pass 51: a NON-EMPTY evidence string is not a TRUE one ────────────────────────────────
#
# WORKER_FINDING_THE_BATTERY_CHECKS_THAT_ITS_EVIDENCE_IS_NON_EMPTY_NEVER_THAT_IT_IS_TRUE.
# `RECONCILIATION_KEYS` was a truthiness test, so it refused an absent evidence string and
# accepted every non-empty one. The two commits below are the real ones: `2c0ba712b` is the
# tree as it stood while pass 43's eight source files sat uncommitted, and `131b86df7` is the
# commit that landed them.

#: The tree as it stood while the defect was LIVE — pass 43's symbols authored, none committed.
PRE_LANDING = "2c0ba712b"
#: The commit that landed them. The null control's whole job: this check is not always-red.
POST_LANDING = "131b86df7"

#: The two citations the finding measured as the ONLY ones a `path::symbol` rule would have
#: caught, verbatim from pass 43's rows.
PASS_43_CITATIONS = (
    "interface/contracts/wall_envelope.py::WallNotification and "
    "simulation/payment_seam_adapter.py::MandateNotificationStream are the new primitive "
    "and its world-side stream."
)


def _commit_is_reachable(ref: str) -> bool:
    import subprocess

    return subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=str(ceb.PROJECT_DIR), capture_output=True, text=True,
    ).returncode == 0


def _repo(tmp_path, files: dict[str, str]):
    """A throwaway git repo with `files` committed, for the properties that need content."""
    import subprocess

    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    for rel, body in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"],
        cwd=root, check=True,
    )
    return root


def test_MUTATION_a_row_citing_symbols_that_are_in_no_commit_RAISES(tmp_path):
    """R15 on the real defect, at the real commit where it was live.

    Not a hand-built tree: these are pass 43's own two citations read out of `2c0ba712b`, the
    commit whose worktree held the code and whose HEAD did not.
    """
    assert _commit_is_reachable(PRE_LANDING), (
        f"{PRE_LANDING} is unreachable, so this mutation tested nothing -- an unavailable "
        f"check is a FAILED check, never a skip"
    )
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1, evidence=PASS_43_CITATIONS)])
    with pytest.raises(BatteryUnavailable, match="do not exist at"):
        ceb.battery_outstanding(
            ledger_path=ledger, reconciliation_path=recon, citation_ref=PRE_LANDING
        )


def test_NULL_CONTROL_the_same_row_clears_at_the_commit_that_LANDED_those_symbols(tmp_path):
    """The control is not always-red, and the sample moves rather than the law.

    THE FINDING'S OWN NULL CONTROL WAS STALE AND THIS IS NOT IT (measured, pass 51). It
    proposed reading the LIVE rows out of `131b86df7`; 18 of the live file's 36 citations do
    not resolve there, because passes 44-50 rewrote those rows to cite symbols authored after
    that commit. Read literally it would have looked like the control failing its own null
    control. So the sample is pinned to the two citations the finding actually measured, and
    the only thing that varies between this test and the mutation above is the REF.
    """
    assert _commit_is_reachable(POST_LANDING), f"{POST_LANDING} is unreachable"
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1, evidence=PASS_43_CITATIONS)])
    assert ceb.battery_outstanding(
        ledger_path=ledger, reconciliation_path=recon, citation_ref=POST_LANDING
    ) == ()


def test_the_LIVE_rows_all_resolve_at_HEAD_so_this_check_did_not_ship_red():
    """The subject that matters: every citation in the real reconciliation, against real HEAD.

    Fails in both directions. If a pass records a row citing code it has not committed, this
    goes red and names it. If the check were born red it would have been red the day it
    landed, which is the failure mode a register of design notes has and a resolver must not.
    """
    rows = ceb.load_reconciliations()
    assert rows, "the live reconciliation is empty, so this asserted nothing"
    checked = sum(len(ceb.cited_symbols(r["evidence"])) for r in rows.values())
    assert checked >= 10, f"only {checked} resolvable citations across {len(rows)} rows"


def test_RESIDUE_3_a_PASS_row_citing_no_path_is_left_alone_deliberately(tmp_path):
    """Q17's shape: the reviewer pre-authorised an ABSENCE as the right answer.

    A rule requiring every PASS to cite a resolvable symbol would red the one question whose
    correct answer is "they don't, they're outside this". The ref here resolves nothing at
    all, and the row still clears — because it claims nothing resolvable.
    """
    ledger = _ledger(tmp_path, _battery((17, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(17, evidence="The honest 'they don't, they're outside this'.")])
    assert ceb.battery_outstanding(
        ledger_path=ledger, reconciliation_path=recon, citation_ref=PRE_LANDING
    ) == ()


def test_a_symbol_only_MENTIONED_IN_A_COMMENT_does_not_resolve(tmp_path):
    """The fail-open a substring search would carry, which is why this parses rather than greps.

    Both halves in one repo so the difference is the symbol and nothing else: `Real` is
    defined, `OnlyInAComment` appears in the same file as text and is not.
    """
    root = _repo(tmp_path, {"m.py": "# OnlyInAComment is discussed here\nclass Real:\n    pass\n"})
    assert ceb.unresolved_citations("m.py::Real", "HEAD", root) == ()
    bad = ceb.unresolved_citations("m.py::OnlyInAComment", "HEAD", root)
    assert len(bad) == 1 and "not defined" in bad[0], bad


def test_RESIDUE_2_a_dotted_tail_verifies_the_top_level_name_only(tmp_path):
    """Pinned as behaviour, not left as prose: `X.method` checks `X`.

    Both directions, so the residue cannot widen or narrow unnoticed: the tail is ignored
    even when it names nothing, and the head is still enforced.
    """
    root = _repo(tmp_path, {"m.py": "class Register:\n    def real(self):\n        pass\n"})
    assert ceb.unresolved_citations("m.py::Register.no_such_method", "HEAD", root) == ()
    assert ceb.unresolved_citations("m.py::NoSuchClass.real", "HEAD", root)


def test_a_cited_file_absent_at_the_ref_names_the_FILE_not_the_symbol(tmp_path):
    root = _repo(tmp_path, {"m.py": "X = 1\n"})
    bad = ceb.unresolved_citations("gone/away.py::Thing", "HEAD", root)
    assert len(bad) == 1 and "no such file" in bad[0], bad


def test_FAIL_SILENT_an_unresolvable_ref_blames_the_REF_not_the_evidence(tmp_path):
    """git being unavailable and a lane fabricating evidence must not share a message.

    An unreadable ref is a FAILED check either way — but reported as a false claim it would
    accuse a lane of inventing evidence on the strength of a broken checkout.
    """
    root = _repo(tmp_path, {"m.py": "X = 1\n"})
    with pytest.raises(BatteryUnavailable, match="does not resolve"):
        ceb.unresolved_citations("m.py::X", "no-such-ref", root)


def test_the_citation_check_is_reached_through_the_LOADER_not_only_directly(tmp_path):
    """A control whose only caller is its own test is an orphan. This asserts the wiring."""
    ledger = _ledger(tmp_path, _battery((1, "DISQUALIFYING")))
    recon = _recon(tmp_path, [_row(1, evidence="interface/contracts/wall_envelope.py::Nope")])
    with pytest.raises(BatteryUnavailable, match="question 1"):
        ceb.load_reconciliations(path=recon)
    with pytest.raises(BatteryUnavailable, match="question 1"):
        ceb.unpayable_here(ledger_path=ledger, reconciliation_path=recon)
