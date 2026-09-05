"""A red that keeps refusing the publisher must gain an AGE and a route into the draw.

THE DEFECT EACH CONTROL HERE NAMES. `_write_blocking_tests` records the hook chain's node ids in a
SNAPSHOT that is overwritten every cycle and deleted on green. So a red that has refused the
publisher twenty-four consecutive cycles is, at every reader in this system, indistinguishable from
one that broke a minute ago. Measured: 82.9% of multi-cycle publish outage is redness STANDING
(988270c2e); RED TEST is 28.3% of all bounded outage, 67.8h against 5.1h for the next gate; and 0 of
7 same-test re-arrivals ever demonstrably re-broke, so every one was persistence (e0cc653c9).
Nothing acted on any of it.

THE FAIL-OPEN THIS SUITE EXISTS TO REFUSE, and it is the first control below. The obvious
implementation reuses `head_red_register.record`, which sets `currently_red = False` for every test
NOT in the failing set. That is correct for a nightly census, which runs the whole suite. The hook
chain is FAIL-FAST: a refusal naming test B does not make test A green, it means pytest stopped
before it reached A. Adopting the census rule would let one fail-fast refusal mark the entire
backlog fixed, and the register would go quiet at exactly the moment the publisher was most wedged.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from background import publish_standing_red as psr
from background import staging_rooms as sr

A = "tests/foo/test_a.py::test_one"
B = "tests/bar/test_b.py::test_two"


@pytest.fixture()
def paths(tmp_path):
    return {"ledger_path": tmp_path / "ledger.json", "register_path": tmp_path / "REG.md"}


# ── the asymmetry: appearing ADDS, absence does NOTHING, only a landing discharges ────────────
def test_a_later_refusal_naming_a_different_test_does_not_discharge_the_first():
    """DEFECT: absence read as green. The hook chain is fail-fast, so a refusal naming B says
    NOTHING about A -- pytest stopped before it got there. If this ever passes by A being dropped,
    one refusal has silently retired every subject behind the first red."""
    led = psr.record_refusal([A], now=None)
    led = psr.record_refusal([B], ledger=led)
    assert set(led["tests"]) == {A, B}, "a fail-fast refusal must not discharge what it did not reach"
    assert led["tests"][A]["cycles_blocked"] == 1
    assert led["tests"][B]["cycles_blocked"] == 1


def test_re_naming_the_same_test_ages_it_rather_than_restating_it():
    """DEFECT: the snapshot's actual behaviour -- the second refusal overwrites the first and the
    age is lost. One red in the real log was retried 24 times and read as new every time."""
    led = None
    for _ in range(3):
        led = psr.record_refusal([A], ledger=led)
    assert led["tests"][A]["cycles_blocked"] == 3
    assert psr.worst(led) == 3


def test_only_a_landing_discharges_and_it_discharges_everything():
    """DEFECT: a ledger with no exit. A register nobody can empty is a register nobody reads, and
    it would be strictly worse than the snapshot it replaces."""
    led = psr.record_refusal([A, B])
    assert led["tests"], "precondition: something must be tracked for the discharge to be visible"
    led = psr.record_landing(git_hash="abc123", ledger=led)
    assert led["tests"] == {}, "a passing hook chain must clear every tracked red"
    assert led["landings"] == 1
    # and the evidence that it ever reduced is kept, which is what makes the counting checkable
    assert sorted(r["node"] for r in led["discharged"]) == sorted([A, B])


def test_a_red_whose_message_changes_every_cycle_still_ages():
    """DEFECT, CAUGHT WHILE WIRING THIS UP: `_parse_failed_node_ids` returns the FULL summary line
    including the assertion text, so a red whose message carries a varying number would be a new
    string every cycle and could never age past one. That is `alarm_repetition`'s founding incident
    re-entered through a different door -- six identical pages that no dedup caught because each
    carried `after {elapsed:.0f}s`. A ledger built to detect "the same red, again" that is blind to
    exactly the reds that recur would still LOOK like it was working, because it would fill up."""
    led = psr.record_refusal(["FAILED {} - AssertionError: 0.31 != 0.29".format(A)])
    led = psr.record_refusal(["FAILED {} - AssertionError: 0.44 != 0.29".format(A)], ledger=led)
    assert list(led["tests"]) == [A], "the identity must be the node id, never the message"
    assert psr.standing(led) == [A]
    # the message is kept where a reader can see it, and no counter is keyed to it
    assert led["tests"][A]["last_detail"].endswith("0.44 != 0.29")


def test_a_refusal_naming_no_test_counts_as_a_refusal_and_folds_no_subject():
    """DEFECT: inventing a subject for a non-test gate. On 2026-09-02 five GREEN tests were
    published as the blockers of an orphan-ratchet refusal, and it cost an 18.7h wedge. A parser
    that always finds something is the fail-open twin of the fail-silent it replaces."""
    led = psr.record_refusal([])
    assert led["refusals"] == 1, "the refusal happened and the denominator must see it"
    assert led["tests"] == {}, "a refusal with no test verdict has no test subject"
    assert psr.standing(led) == []


# ── the escalation branch, asserted REACHABLE over one partition, not one leg per branch ──────
def test_the_standing_branch_can_be_taken_and_the_not_yet_branch_can_too():
    """DEFECT: a threshold that no observation can ever cross, or one that everything crosses.
    Every test of a threshold asks "does it refuse correctly" -- and a threshold that refuses
    EVERYTHING passes all of them. One control over the whole partition, in one assertion."""
    led = psr.record_refusal([A, B])          # both at 1
    led = psr.record_refusal([A], ledger=led)  # A at 2, B still at 1
    assert psr.standing(led) == [A], (
        "A crossed the threshold and B did not -- both sides of the branch reachable in one "
        "ledger, so neither side can be an artefact of the fixture")


def test_the_threshold_is_the_measured_one_and_not_a_larger_picked_number():
    """DEFECT: a number picked because a number was needed. 0 of 7 same-test re-arrivals in the
    real log re-broke, so the observed base rate of "the second refusal is a NEW failure" is zero
    -- and nothing in this project establishes a higher bar. Keyed to the ORIGIN, not to today's
    ledger: this reddens if someone widens the threshold without bringing new evidence."""
    assert psr.STANDING_AFTER_CYCLES == 2
    src = Path(psr.__file__).read_text()
    assert "0 of 7" in src or "**0 of 7**" in src, (
        "the threshold's origin measurement must be cited beside it, or the next reader has a "
        "bare constant and no way to tell it was established rather than chosen")


# ── zero means zero, enforced in the DRAW and not promised in the document ────────────────────
def test_the_register_leaves_the_queue_when_the_ledger_is_discharged(tmp_path, monkeypatch):
    """DEFECT: a permanent parked item. `head_red_register`'s sibling defect -- a register that is
    always drawn stops meaning anything, and it outranks real findings while doing it."""
    root = tmp_path / "staging"
    (root / sr.REFERENCE_DIRNAME).mkdir(parents=True)
    reg = root / sr.REFERENCE_DIRNAME / psr.REGISTER_NAME
    ledger = tmp_path / "ledger.json"
    monkeypatch.setattr(psr, "LEDGER_PATH", ledger)

    psr.save_ledger(psr.record_refusal([A], ledger=psr.record_refusal([A])), ledger)
    psr.write_register(psr.load_ledger(ledger), path=reg)
    drawn = [i for i in sr._with_the_standing_red_register(root, [])
             if i.kind == sr.KIND_PUBLISH_STANDING_RED]
    assert len(drawn) == 1 and drawn[0].rank == sr.ORDER[sr.KIND_PUBLISH_STANDING_RED]

    psr.save_ledger(psr.record_landing(ledger=psr.load_ledger(ledger)), ledger)
    assert [i for i in sr._with_the_standing_red_register(root, [])
            if i.kind == sr.KIND_PUBLISH_STANDING_RED] == [], (
        "one landing must take this straight back out of the queue")


def test_the_register_outranks_a_finding_and_yields_to_a_person(tmp_path):
    """DEFECT: the 2026-08-25 shape -- machine-authored work at the head of the draw, pushing a
    person's ask to position 43 of 48."""
    assert (sr.ORDER[sr.KIND_CLASS_DEBT]
            < sr.ORDER[sr.KIND_PUBLISH_STANDING_RED]
            < sr.ORDER[sr.KIND_HEAD_RED]
            < sr.ORDER[sr.KIND_FINDING])
    assert sr.ORDER[sr.KIND_DIRECTIVE] < sr.ORDER[sr.KIND_PUBLISH_STANDING_RED]
    assert sr.room_for(sr.KIND_PUBLISH_STANDING_RED) == sr.REFERENCE_DIRNAME


# ── the document names its subject, and says so where it cannot ──────────────────────────────
def test_the_register_names_the_tests_rather_than_counting_them():
    """DEFECT: the census's own failure -- paging a COUNT. There is nothing in a number a person
    can pick up and fix."""
    led = psr.record_refusal([A], ledger=psr.record_refusal([A]))
    text = psr.render(led)
    assert A in text and "BLOCKING" in text
    assert "ZERO MEANS ZERO" not in text


def test_a_clean_ledger_renders_zero_means_zero_rather_than_an_empty_table():
    led = psr.record_landing(ledger=psr.record_refusal([A]))
    text = psr.render(led)
    assert "ZERO MEANS ZERO" in text and "RECORDED" in text


def test_the_register_declares_its_own_truncation(monkeypatch):
    """DEFECT: a summary that hides its own truncation turns a named subject back into a count."""
    monkeypatch.setattr(psr, "MAX_LISTED", 2)
    nodes = ["tests/t.py::test_{}".format(i) for i in range(5)]
    led = psr.record_refusal(nodes, ledger=psr.record_refusal(nodes))
    text = psr.render(led)
    assert "more not listed" in text and "publish_standing_reds.json" in text


# ── the wiring: an unwired mechanism is this project's most expensive recurring shape ─────────
def test_the_publishers_refusal_path_actually_folds_into_the_ledger(tmp_path, monkeypatch):
    """DEFECT: the mechanism exists and nothing calls it. `saas/opex_ledger.py` held a sourced,
    cited, tested constant that reached no code for seven weeks. This asserts the fold happens
    from the publisher's OWN refusal function, over its OWN parser, with no help from the test."""
    from background import process_run_complete as prc

    ledger = tmp_path / "ledger.json"
    monkeypatch.setattr(psr, "LEDGER_PATH", ledger)
    monkeypatch.setattr(psr, "REGISTER_PATH", tmp_path / "REG.md")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / "blocking.json")

    # The publisher's real output shape: its parser is scoped to the LAST short-summary section.
    hook_output = ("=========================== short test summary info "
                   "============================\n"
                   "FAILED {} - AssertionError: boom\n1 failed, 3 passed\n".format(A))
    reds = prc._record_commit_refusal_reds(hook_output, "", "deadbee")
    assert reds and reds[0].startswith("FAILED {}".format(A)), (
        "precondition: the publisher's own parser must have named the test")
    assert psr.load_ledger(ledger)["tests"][A]["cycles_blocked"] == 1

    prc._record_commit_refusal_reds(hook_output, "", "deadbee")
    assert psr.standing(psr.load_ledger(ledger)) == [A], (
        "two refusals naming the same test must escalate it, through the publisher's real path")


def test_the_publishers_pass_path_actually_discharges_the_ledger(tmp_path, monkeypatch):
    """DEFECT: an accumulate-only ratchet. The counterpart of the control above, and it is the one
    that would go unnoticed -- a register that only grows still LOOKS like it is working."""
    from background import process_run_complete as prc

    ledger = tmp_path / "ledger.json"
    monkeypatch.setattr(psr, "LEDGER_PATH", ledger)
    monkeypatch.setattr(psr, "REGISTER_PATH", tmp_path / "REG.md")
    psr.save_ledger(psr.record_refusal([A], ledger=psr.record_refusal([A])), ledger)
    assert psr.standing(psr.load_ledger(ledger)) == [A], "precondition: something to discharge"

    assert prc._record_commit_hook_pass("deadbee") == 1
    assert psr.load_ledger(ledger)["tests"] == {}


def test_every_function_that_folds_a_refusal_also_records_a_pass():
    """DEFECT: the two halves drifting apart. A commit path that folds refusals in and never
    records its own pass turns the ledger into a ratchet for that path alone, and the register
    would name a red that a DIFFERENT path had already cleared.

    Keyed to the PROPERTY -- "these two calls are paired" -- and not to today's two call sites, so
    a third refusal path added next month is covered without this test being edited."""
    from background import process_run_complete as prc

    tree = ast.parse(Path(prc.__file__).read_text())
    folds, passes = set(), set()
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        called = {n.func.id for n in ast.walk(fn)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        if "_record_commit_refusal_reds" in called:
            folds.add(fn.name)
        if "_record_commit_hook_pass" in called:
            passes.add(fn.name)
    assert folds, "precondition: the refusal fold must have at least one caller to be checkable"
    assert folds <= passes, (
        "these commit path(s) fold a refusal into the standing-red ledger and never record the "
        "hook chain passing, so the ledger can only ever grow from them: {}".format(
            sorted(folds - passes)))


# ── failing to observe must never break the thing being observed ─────────────────────────────
def test_a_broken_ledger_cannot_take_the_publish_cycle_down(tmp_path, monkeypatch):
    """DEFECT: a diagnostic that reds the path it observes. The publisher is mid-refusal when this
    runs; a ledger that raised would convert a recoverable refusal into a dead cycle."""
    monkeypatch.setattr(psr, "LEDGER_PATH", tmp_path / "nope" / "x" / "ledger.json")
    monkeypatch.setattr(psr, "REGISTER_PATH", tmp_path)  # a directory: write_text will raise
    assert psr.note_refusal([A], "deadbee") == []
    assert psr.note_landing("deadbee") == 0
    assert psr.drawable() == []


# ── the replay, over a synthetic log in the real log's own shape ─────────────────────────────
#
# NOT over the real 24MB log, deliberately. That file is on the shared tree, is rewritten every
# publish cycle, and is truncated in a HEAD extract — so a control reading it would grade a moving
# subject and would red in the clean-extract check used to prove reds pre-existing. The real
# replay's numbers live in the finding; what is asserted HERE is the property, over a fixture whose
# answer is known by construction.
_STAMP = "- [2026-08-13 {} UTC] [process_run] {}"
_SUMMARY = "=========================== short test summary info ============================"


def _cycle(hhmm, failed=None):
    """One publish cycle in the runner log's real shape. `failed=None` means it LANDED.

    The shape is load-bearing and is copied from the live log, not invented: the hook block opens
    on a TIMESTAMPED `Nothing to commit or commit failed` line, runs as untimestamped output, and
    its verdict is the next timestamped line. `_hook_blocks` finds the block that way and
    `_body_at` will only pair it with a verdict within three lines, so a fixture that gets this
    wrong silently produces `UNATTRIBUTABLE` and folds nothing — which is exactly the false green
    these two controls would otherwise report."""
    out = [_STAMP.format(hhmm, "Committing and pushing")]
    if failed is None:
        return out
    out.append(_STAMP.format(hhmm, "Nothing to commit or commit failed (rc=1)"))
    if failed:
        out.append(_SUMMARY)
        out += ["FAILED {} - AssertionError: boom".format(n) for n in failed]
        out.append("{} failed, 3 passed in 12.0s".format(len(failed)))
    else:
        # A NON-TEST GATE THAT NAMES A SUBJECT, copied from the live log verbatim. The first draft
        # of this fixture used a banner with no parseable subject, and a mutation that folded
        # EVERY gate's subject into the ledger SURVIVED — because with nothing to fold, the
        # `cause == RED_TEST` guard was never exercised. It is not an equivalence: on the real log
        # the level gate names an atom id, the finding-class gate names `.md` files and the
        # orphan-ratchet names modules, and folding any of them would put a non-test into a
        # register of red TESTS and age it as one.
        out += ["[level-gate] ❌ COMMIT REFUSED (a level move must be BUILT in the commit that "
                "declares it):",
                "§0: level_current 2->3 on H_GAP_fabric_belief_truth_gap declares a level for "
                "source this commit does NOT contain"]
    out.append(_STAMP.format(hhmm, "Commit/push failed (commit_refused)"))
    return out


def test_the_replay_reaches_escalation_discharge_and_a_subjectless_refusal():
    """DEFECT: a replay whose interesting branches are unreachable, reporting zeroes that read as
    'nothing to see'. One control over the whole partition — if any of these three is 0 the replay
    is not measuring what it claims, and a green suite would say otherwise.

    These are the three of the four pre-registered predictions the replay's own shape can prove.
    The fourth (the magnitude) is a fact about the real log and belongs in the finding, not here,
    where pinning it would key this control to yesterday's answer."""
    log = "\n".join(
        _cycle("01:00", [A])          # A at 1
        + _cycle("02:00", [A])        # A at 2 -> ESCALATES
        + _cycle("03:00", [])         # a non-test gate: refuses, folds no subject
        + _cycle("04:00")             # LANDS -> discharges a non-empty ledger
        + _cycle("05:00", [B]))       # B at 1, alone in a fresh ledger
    rep = psr.replay(log)
    assert rep["escalated_distinct"] == 1 and rep["escalation_events"] == 1
    assert rep["worst_cycles_blocked"] == 2
    assert rep["landings_that_discharged_something"] == 1, (
        "the discharge leg must be reachable, or 'zero means zero' has no evidence behind it")
    assert rep["refusals_that_folded_no_subject"] == 1, (
        "a non-test gate must fold nothing — a parser that always finds a subject is the "
        "fail-open twin of the fail-silent this replaces")
    assert rep["peak"][A] == 2 and rep["peak"][B] == 1
    # …and the non-test gate's OWN subject must not have been folded as if it were a test. The
    # level gate named an atom id; a register of red tests that ages an atom id is measuring a
    # population it cannot name.
    assert "H_GAP_fabric_belief_truth_gap" not in rep["peak"], (
        "only a RED TEST refusal has a test subject — every other gate's subject is a different "
        "kind of thing and must not enter this ledger")


def test_the_replay_does_not_carry_a_red_across_a_landing():
    """DEFECT: a monotonic replay. If the landing did not discharge, A would reach 2 across the
    landing and be reported as standing — manufacturing an escalation out of a red that cleared."""
    log = "\n".join(_cycle("01:00", [A]) + _cycle("02:00") + _cycle("03:00", [A]))
    rep = psr.replay(log)
    assert rep["worst_cycles_blocked"] == 1 and rep["escalated_distinct"] == 0


def test_an_unreadable_ledger_reads_as_empty_rather_than_as_a_nameless_escalation(tmp_path):
    """DEFECT: escalating a subject the ledger cannot name. An escalation with no node id in it is
    exactly the wallpaper this register replaces, so the fail direction here is EMPTY -- and the
    next refusal, at most one cycle away, repopulates it."""
    bad = tmp_path / "ledger.json"
    bad.write_text("{ not json")
    assert psr.load_ledger(bad) == psr.empty_ledger()
    bad.write_text(json.dumps(["a", "list", "not", "a", "dict"]))
    assert psr.load_ledger(bad) == psr.empty_ledger()
