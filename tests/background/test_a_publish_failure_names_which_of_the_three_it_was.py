"""R15 mutation tests: a publish failure record must name ONE cause, with its evidence.

THE DEFECT, observed with evidence (R9), not inferred. `docs/observability/.publish_gate_state.json`
on 2026-08-30 carried `wedge_since` 05:27:59Z, `episode_failures: 9`, `total_red: 0`, and this
sentence on every failure entry:

    "the publish COMMIT did not land for run_complete_...md -- the publisher's own scoped suite
     was GREEN and the commit was refused/timed out/never reached origin"

Three alternatives in one breath is not a diagnosis, and nine consecutive episodes of it produced
no attribution at all while `origin/main` sat five commits behind HEAD -- including the whole
departure-level anchor. Meanwhile `git_commit_push` had NAMED the outcome in a variable at the
moment it happened, acted on it (the fingerprint decision), and then collapsed all four paths into
`EXIT_PUBLISH_DID_NOT_LAND`. The router runs in a LATER PROCESS and sees only that code, so it
re-invented the disjunction the publisher had already resolved. FAIL-SILENT at the record layer.

WHAT IS UNDER TEST, AND HOW EACH ROW CAN FAIL. `background/publish_cause.py` carries the
attribution across the process boundary, keyed to the commit it is about. Three properties, each
mutated here:

  * THE RECORD NAMES ONE OF THE FOUR, AND THE RIGHT ONE. `test_the_router_names_the_cause_the_
    publisher_recorded` drives all four causes through the same fixture and asserts each names
    ITSELF and not the other three -- so a mutation that hardcodes any single cause reds on three
    of four rows, and one that reads nothing reds on all four.
  * IT CAN NAME THE WRONG ONE, AND IS HELD TO NOT. `test_a_stale_record_from_another_commit_...`
    is the mutation-proof the direction asked for: a record naming `gate_refusal` sits in place,
    in-window, for a DIFFERENT commit, and the reader must refuse it. Delete the git-hash check in
    `read_cause` and the router confidently names `gate_refusal` for a push failure -- which is
    exactly the carried-forward-blocking-list defect wearing a new field name.
  * NO GREEN TEST APPEARS IN A BLOCKING LIST. `test_a_cause_on_which_nothing_was_judged_...`
    seeds a live blocking record naming a test, then fails a cycle attributed to a cause on which
    no test ran. Delete the suppression and the state file names that test as a blocker of a wedge
    it had nothing to do with -- this project's own catalogued class, four clocks paid.

THE NULL CONTROL is `test_an_unattributed_failure_says_so_rather_than_guessing`: with no record
at all the row must read `unattributed` AND carry a sentence saying so. A fix that answered
"gate_refusal" on an absent record would pass every other row in this file and be the same defect
with better grammar.
"""
import json
import time

import pytest

import background.process_run_complete as prc
import background.publish_cause as pc

MARKER_HASH = "b98722cb2"
OTHER_HASH = "0ddba11ed"
MARKER_NAME = "run_complete_20260830T135651Z.md"


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Every file this control touches, redirected -- a test that reads or writes the LIVE wedge
    state would poison the detector it is checking."""
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / ".last_publish_cause.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


@pytest.fixture
def archived_marker(tmp_path, monkeypatch):
    """A marker in `done/` produced at MARKER_HASH -- the state a publish leaves behind whether
    its commit landed or not, which is why the marker's own location proves nothing."""
    done = tmp_path / "staging" / "done"
    done.mkdir(parents=True)
    marker = done / MARKER_NAME
    marker.write_text("# Run complete\n\nGit: {}\n".format(MARKER_HASH))
    monkeypatch.setattr(prc, "DONE_DIR", done)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    return marker


def _state():
    return json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())


def _last_failure():
    return _state()["failures"][-1]


# ── The publisher's side: the mapping from an outcome to a cause ─────────────────────────────

def test_every_outcome_that_exits_77_maps_to_exactly_one_cause():
    """EXHAUSTIVE OVER THE MODULE'S OWN VOCABULARY, not over a list written beside it.

    The set is DERIVED here: every outcome constant the publisher declares, minus the retryable
    ones (which exit 0) and minus those carrying their own named exit code. Whatever is left
    reports rc=77 and must therefore have a cause, or the router's answer for it is
    `unattributed` -- honest, but a silent regression to the disjunction this closes.

    MUTATION: add a fifth rc=77 outcome without mapping it and this reds by name. Written this
    way rather than as a literal list because a control that draws its cases from a list beside
    the code cannot see its own scope shrink.
    """
    declared = {v for k, v in vars(prc).items()
                if k.isupper() and isinstance(v, str) and v == k.lower()}
    exits_77 = {r for r in declared
                if r not in prc.RETRYABLE_PUBLISH_OUTCOMES
                and r not in prc.NAMED_PUBLISH_EXIT_CODES}
    unmapped = exits_77 - set(prc.PUBLISH_CAUSE_FOR_REASON)
    assert not unmapped, (
        "these outcomes exit 77 and would be recorded with no cause, so their failures read as "
        "unattributed: {}".format(sorted(unmapped)))
    # BOTH PRODUCTION ROUTES, because as of 2026-09-02 there are two (see
    # `PUBLISH_CAUSE_OVERRIDES`). The table is keyed by OUTCOME and one outcome -- COMMIT_REFUSED
    # -- covers two experiences the publisher can tell apart only at the branch: the hook chain
    # named reds, or a non-test gate refused ahead of the test gate and nothing was judged.
    # Widening this to the UNION rather than dropping it keeps the property that matters: a cause
    # NEITHER route can produce is still a branch no reader will ever see, and still reds here.
    producible = set(prc.PUBLISH_CAUSE_FOR_REASON.values()) | set(prc.PUBLISH_CAUSE_OVERRIDES)
    assert producible == set(pc.CAUSES), (
        "the two production routes and the cause vocabulary must be the same closed set in both "
        "directions -- a cause nothing can produce is a branch no reader will ever see")
    assert not (set(prc.PUBLISH_CAUSE_OVERRIDES) & set(prc.PUBLISH_CAUSE_FOR_REASON.values())), (
        "a cause produced by BOTH routes makes the override unfalsifiable: the table would "
        "supply it anyway, so deleting the branch that overrides would not red anything")


def test_a_cause_outside_the_closed_set_is_refused_rather_than_stored(tmp_path):
    """FAIL-CLOSED ON THE WRITE. A reader that switches on `cause` believes the set is closed;
    storing an unrecognised name would hand it a value it has no branch for, and the fallback
    branch is the disjunction. Refusing the write leaves the record ABSENT, which every reader
    already renders as "we cannot tell".

    MUTATION: drop the `cause not in CAUSES` guard and this reds.
    """
    p = tmp_path / "cause.json"
    assert pc.record_cause(p, "probably_the_network", "a guess", MARKER_HASH) is False
    assert not p.exists(), "an unrecognised cause must write NOTHING, not a record"
    assert pc.record_cause(p, pc.DEADLINE_KILL, "killed at 840s", MARKER_HASH) is True
    assert pc.read_cause(p, MARKER_HASH)[0] == pc.DEADLINE_KILL


# ── The reader's side: one name, and the evidence for it ─────────────────────────────────────

@pytest.mark.parametrize("cause,evidence", [
    (pc.GATE_REFUSAL, "`git commit` returned rc=1 and the hook chain named 0 red test(s)"),
    (pc.DEADLINE_KILL, "the hook chain was killed after 843s against its own 840s budget"),
    (pc.PUSH_NEVER_LANDED, "origin/main still at d7d1b07b6 while HEAD is 3e90ae5e1"),
    (pc.PROVENANCE_REFUSED, "the fail-closed provenance check refused the stamp"),
])
def test_the_router_names_the_cause_the_publisher_recorded(archived_marker, cause, evidence):
    """ONE CAUSE, AND THE RIGHT ONE. Four rows, one fixture, only the record differs.

    Each row asserts its own cause IS named and the other three are NOT, so a mutation that
    hardcodes any single cause fails three rows, and one that ignores the record fails all four.
    The evidence must survive to the record too: a cause with no observation behind it is a label,
    and the previous sentence was already a label.
    """
    pc.record_cause(prc.PUBLISH_CAUSE_FILE, cause, evidence, MARKER_HASH)

    assert prc.record_publish_gate_outcome(
        str(archived_marker), prc.EXIT_PUBLISH_DID_NOT_LAND) == "failure"

    entry = _last_failure()
    assert entry["cause"] == cause
    assert evidence in entry["cause_evidence"]
    for other in pc.CAUSES - {cause}:
        assert entry["cause"] != other
        assert other not in entry["reason"], (
            "the reason sentence must name ONE cause -- naming {} as well is the "
            "refused/timed-out/never-reached-origin disjunction returning".format(other))
    assert "refused/timed out/never reached origin" not in entry["reason"], (
        "the three-alternatives-in-one-breath sentence is the defect itself")


def test_a_stale_record_from_another_commit_cannot_name_this_failure(archived_marker):
    """THE MUTATION-PROOF THAT IT CAN NAME THE WRONG ONE.

    A record naming `gate_refusal` sits in place and is IN WINDOW -- only its commit differs. If
    the reader accepted it, the router would state with the same confidence as every row above
    that a hook chain refused this publish, and send its reader to hunt hook output that does not
    exist. That is the carried-forward-blocking-list defect with a new field name, and it is the
    reason `read_cause` is keyed to the commit rather than to the clock.

    MUTATION: delete the `recorded_hash != git_hash` branch in `read_cause` and this reds with
    `gate_refusal`.
    """
    pc.record_cause(prc.PUBLISH_CAUSE_FILE, pc.GATE_REFUSAL,
                    "a refusal that happened on a DIFFERENT commit", OTHER_HASH)

    prc.record_publish_gate_outcome(str(archived_marker), prc.EXIT_PUBLISH_DID_NOT_LAND)

    entry = _last_failure()
    assert entry["cause"] == pc.UNATTRIBUTED, (
        "an in-window record for another commit is evidence about another cycle")
    assert OTHER_HASH[:9] in entry["cause_evidence"], (
        "the refusal must NAME the commit whose record it declined, so a reader can see the "
        "mismatch for themselves rather than take 'unattributed' on trust")


def test_an_unattributed_failure_says_so_rather_than_guessing(archived_marker):
    """THE NULL CONTROL. No record at all -- the state the very first failure after a deploy is
    in, and the state every failure was in before this mechanism existed.

    The row must read `unattributed` and CARRY A SENTENCE saying the cause was not established.
    A fix that answered `gate_refusal` here would pass every other row in this file and be the
    same defect with better grammar.
    """
    assert not prc.PUBLISH_CAUSE_FILE.exists()

    prc.record_publish_gate_outcome(str(archived_marker), prc.EXIT_PUBLISH_DID_NOT_LAND)

    entry = _last_failure()
    assert entry["cause"] == pc.UNATTRIBUTED
    assert "no cause" in entry["cause_evidence"] or "NOT established" in entry["cause_evidence"]
    assert entry["kind"] == "commit_did_not_land", (
        "the kind is unchanged -- the supervisor's WEDGE_KINDS_NO_TEST_JUDGED and three test "
        "modules switch on it, and the attribution is a finer answer beside it, not a rename")


# ── No green test may appear in a blocking list ──────────────────────────────────────────────

def _seed_live_blocking_record(node_id, git_hash):
    """A blocking record from an EARLIER cycle: in window (so age alone will not reject it) and
    naming a test that is, right now, green."""
    prc.GATE_BLOCKING_TESTS_FILE.write_text(json.dumps(
        {"ts": time.time(), "git_hash": git_hash, "census": prc.CENSUS_COMPLETE,
         "total_red": 1, "node_ids": [node_id]}))


@pytest.mark.parametrize("cause", sorted(pc.NO_TEST_JUDGED_CAUSES))
def test_a_cause_on_which_nothing_was_judged_names_no_blocking_test(archived_marker, cause):
    """ITEM (b), AT THE RECORD RATHER THAN IN THE PROSE.

    On a deadline kill the suite was killed mid-verdict; on a push failure the hook chain PASSED
    to get the commit made; on a provenance refusal nothing ran at all. In none of the three did
    a test go red -- so whatever `last_blocking_tests` returns is an earlier cycle's, and the
    state file is the artefact the RUNG-1 draw and the director's brief actually quote. Four
    green tests were named as blockers of a wedge they had nothing to do with.

    MUTATION: delete the `no_test_was_judged` suppression and this reds, naming the seeded test.
    """
    _seed_live_blocking_record("tests/background/test_process_run_complete.py::test_a_green_one",
                               MARKER_HASH)
    pc.record_cause(prc.PUBLISH_CAUSE_FILE, cause, "observed", MARKER_HASH)

    prc.record_publish_gate_outcome(str(archived_marker), prc.EXIT_PUBLISH_DID_NOT_LAND)

    state = _state()
    assert state["blocking_tests"] == [], (
        "a cause on which no test returned a verdict must accuse nobody -- it named {}"
        .format(state["blocking_tests"]))
    assert state["total_red"] == 0, (
        "the census counts the same suppressed record; leaving a depth claim beside an empty "
        "list is the accusation-with-no-accused shape inverted")
    assert state["suspects"] == {}


def test_a_gate_refusal_still_carries_the_red_the_hook_chain_named(archived_marker):
    """THE COMPLEMENT, AND THE REASON THE SUPPRESSION IS KEYED TO THE CAUSE.

    `gate_refusal` is the ONE cause where the hook chain did judge, and `_record_commit_refusal_reds`
    writes its reds against the same commit in the same moment. Suppressing there would tell a
    reader not to look for a red that is real -- the unsafe direction. This row is what stops the
    suppression being widened to "any rc=77", which is the tempting simplification.

    MUTATION: move GATE_REFUSAL into NO_TEST_JUDGED_CAUSES and this reds.
    """
    node = "tests/background/test_finding_classes.py::test_consolidation"
    _seed_live_blocking_record(node, MARKER_HASH)
    pc.record_cause(prc.PUBLISH_CAUSE_FILE, pc.GATE_REFUSAL,
                    "`git commit` returned rc=1 and the hook chain named 1 red test(s)",
                    MARKER_HASH)

    prc.record_publish_gate_outcome(str(archived_marker), prc.EXIT_PUBLISH_DID_NOT_LAND)

    assert _state()["blocking_tests"] == [node], (
        "a hook-chain refusal's own red, recorded against this same commit, is real evidence "
        "about THIS cycle and must survive")


def test_an_unattributed_cause_does_not_suppress_the_blocking_list(archived_marker):
    """FAIL-SAFE DIRECTION, PINNED. `no_test_was_judged(UNATTRIBUTED)` is False on purpose:
    hiding a blocking list when a test really IS red would tell a worker not to look for it,
    which is the unsafe error. Showing a stale one is misdirection the surrounding prose now
    labels explicitly.

    MUTATION: make `no_test_was_judged` return True for anything outside GATE_REFUSAL -- an
    easy and plausible simplification -- and this reds.
    """
    node = "tests/background/test_something.py::test_x"
    _seed_live_blocking_record(node, MARKER_HASH)

    prc.record_publish_gate_outcome(str(archived_marker), prc.EXIT_PUBLISH_DID_NOT_LAND)

    assert _last_failure()["cause"] == pc.UNATTRIBUTED
    assert _state()["blocking_tests"] == [node], (
        "an unproven cause must not buy silence -- only a positively attributed no-test-judged "
        "cause suppresses")


def test_the_alarm_prose_carries_the_attribution_not_just_the_field(archived_marker):
    """THE FIELD WITHOUT A READER IS THE SHAPE THIS REPO KEEPS PAYING FOR (supervisor.py's own
    `WEDGE_KINDS_NO_TEST_JUDGED` comment: "the control could not even be heard"). The NTFY is
    what a human reads at 3am, so the attribution has to reach the message, ahead of the
    standing "run that test at HEAD" prose written for a different wedge.

    MUTATION: drop the `ATTRIBUTED CAUSE` clause from `_fire_publish_gate_alert` and this reds.
    """
    sent = []
    pc.record_cause(prc.PUBLISH_CAUSE_FILE, pc.PUSH_NEVER_LANDED,
                    "origin/main still at d7d1b07b6 while HEAD is 3e90ae5e1", MARKER_HASH)
    # Two seeds, so the attributed failure below is the one that MEETS the threshold and fires.
    # Seeding three would fire on the third and leave this one inside the cooldown -- armed but
    # silent, which would make this row a test of the cooldown rather than of the prose.
    now = time.time()
    for offset in (30, 20):
        prc.record_publish_gate_failure("seeded", rc=1, git_hash=MARKER_HASH, now=now - offset,
                                        send_ntfy_fn=lambda _m: "sent")
    prc.record_publish_gate_failure(
        "the publish COMMIT did not land", rc=prc.EXIT_PUBLISH_DID_NOT_LAND,
        git_hash=MARKER_HASH, kind="commit_did_not_land",
        cause=pc.PUSH_NEVER_LANDED, cause_evidence="origin/main still at d7d1b07b6",
        now=now, send_ntfy_fn=lambda m: (sent.append(m), "id")[1])

    assert sent, "the threshold was met, so the alarm must have fired"
    msg = sent[-1]
    assert "ATTRIBUTED CAUSE" in msg and pc.PUSH_NEVER_LANDED in msg
    assert "origin/main still at d7d1b07b6" in msg, (
        "the observation that decided it must reach the phone, not only the label")
