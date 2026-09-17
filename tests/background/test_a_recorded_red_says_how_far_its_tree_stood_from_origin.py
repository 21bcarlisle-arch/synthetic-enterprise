"""A failure that NAMES a red must also say how far the tree it was graded on stood from origin.

THE DEFECT THIS CLOSES (measured 2026-09-17, not inferred -- 337afc848). `159a2d4fc` landed on
origin/main 59 minutes AFTER the local fork opened. The publish gate graded `882ef8aad` and cited
twelve blocking node ids. Those twelve are GREEN at origin/main: the fix for them was already on
origin, and the graded tree simply had not seen it. `.last_gate_blocking_tests.json` recorded the
node ids, the subject SHA and the census, and said nothing about the fork -- so the wedge draw,
the alarm and the suspects blame trail each sent a reader at twelve innocent tests with no
caveat. This turn's own drawn item was the proof of cost: it was written to re-grade a gate and
directed the seat at a ref-lock message already superseded.

THE STATE FILE IS ALREADY SCRUPULOUS ABOUT THE ADJACENT QUESTION. `red_at_head` names both
commits and refuses with `not_established` when it cannot place the red. This is that discipline
one field along -- and the two are NOT the same question, which is why they are two fields:
`red_at_head: yes` is a CORRECT attribution to a tree 41 commits behind origin, whose red is
green at origin/main. Collapsing them would make one of the two true answers unsayable.

R15, both directions:
  * FIRES      -- each of the three verdicts is reached by the input that earns it, and
                  `diverged` names the counts in both directions.
  * PARTITION  -- one control asserts all three verdicts are REACHABLE over the whole partition
                  (CLAUDE.md: a guard that refuses everything passes every per-branch test). The
                  pre-repair behaviour -- no field at all -- fails it.
  * MUTATION   -- the fail-open reading, `not isinstance` dropped so `(None, None)` falls through
                  `behind or ahead` to `level`, is asserted to FAIL. That mutant publishes "the
                  tree was level with origin/main" on a question nobody could answer.
  * NOT COLLAPSED -- `red_at_head: yes` and `red_tree_fork: diverged` must be able to stand
                  together, because that pair IS the 2026-09-17 incident.
  * FAIL-SAFE  -- an unreadable origin, a record predating the field, a stale record and a
                  failure naming no red each degrade to `not_established` WITH a reason.
  * THE RECORD -- the field must survive to `.publish_gate_state.json`, which is what the RUNG-1
                  draw and the seat brief actually quote, and survive a liveness write landing
                  between the red and its reader.
"""
import json

import pytest

import background.process_run_complete as prc

HEAD = "882ef8aad3f1c2e4b5a6978869504132abcdef01"
# The commit that landed on origin 59 minutes after the fork opened, carrying the fix for the
# twelve reds the gate then cited.
ON_ORIGIN = "159a2d4fc0e1b2a3948576b5c4d3e2f109876543"
RED = "tests/site/test_publisher_ledger.py::test_the_ledger_names_its_basis"
# Captured BEFORE the autouse fixture pins it, so the two tests that exercise the real
# `fork_state` seam still can. Re-reading `prc._fork_state_for_record` inside them would get the
# fixture's stub and measure nothing.
REAL_FORK_READER = prc._fork_state_for_record


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    # The fork read FETCHES. No control in this file may put a network call on the gate path, and
    # a control whose answer depends on where this machine's origin happens to be is not a
    # control. Every test that wants a specific fork sets it explicitly.
    monkeypatch.setattr(prc, "_fork_state_for_record", lambda: (0, 0))
    yield


def _verdict(node_ids=(RED,), behind=0, ahead=0):
    return prc.red_tree_fork_verdict(list(node_ids), behind, ahead)


# ── FIRES ────────────────────────────────────────────────────────────────────────────────────

def test_a_red_graded_on_a_forked_tree_names_the_divergence():
    """THE INCIDENT. Behind origin is how a fix that already landed reads as a live red."""
    v = _verdict(behind=41, ahead=3)
    assert v["verdict"] == prc.RED_TREE_FORK_DIVERGED
    # Both directions named, with their counts -- "diverged" alone tells the reader nothing about
    # which way to look.
    assert "41" in v["reason"] and "3" in v["reason"]
    assert "behind origin/main" in v["reason"] and "ahead" in v["reason"]


def test_being_ahead_alone_is_still_a_fork():
    """A tree holding commits origin has never seen did not grade origin/main's tree either. The
    behind direction is the one that was measured; a control that only closed it would be the
    `commits_ahead` defect (origin_reconcile, 2026-09-02) reproduced one module along."""
    assert _verdict(behind=0, ahead=2)["verdict"] == prc.RED_TREE_FORK_DIVERGED


def test_a_red_graded_on_a_level_tree_says_level():
    v = _verdict(behind=0, ahead=0)
    assert v["verdict"] == prc.RED_TREE_FORK_LEVEL
    assert "0 behind, 0 ahead" in v["reason"]


def test_diverged_does_not_claim_the_reds_are_green_at_origin():
    """Establishing THAT needs a run on origin/main's tree, which the alarm path will not do --
    the same rule `red_at_head_verdict` states about shelling out. The record must say the red is
    UNATTRIBUTED between two trees and point at the cheap thing that settles it, not answer a
    question it never measured."""
    reason = _verdict(behind=41, ahead=0)["reason"]
    assert "NOT established as origin/main's" in reason
    assert "Check one of them at origin/main" in reason
    assert "are green at origin/main" not in reason


def test_level_does_not_claim_the_fix_is_absent_from_origin():
    """The inverse refusal. `level` is "nothing origin holds was missing from what was measured",
    never "origin has no fix for this" -- which would be a claim over a tree nobody read."""
    assert "does not explain" in _verdict(behind=0, ahead=0)["reason"]


# ── MUTATION: the fail-open reading, asserted to fail ────────────────────────────────────────

def test_treating_an_unreadable_origin_as_level_is_the_fail_open_and_fails_this_control():
    """The mutant: drop the `isinstance` leg, so `(None, None)` falls straight through
    `behind or ahead` to the LEVEL branch. It publishes "the tree was level with origin/main" on
    a question nobody could answer -- ruling out divergence on the strength of a failed read,
    which is the exact direction that sends the reader back at the innocent tests."""
    def mutant(node_ids, behind, ahead):
        if not node_ids:
            return {"verdict": prc.RED_TREE_FORK_NOT_ESTABLISHED, "reason": "no red"}
        if behind or ahead:
            return {"verdict": prc.RED_TREE_FORK_DIVERGED, "reason": "forked"}
        return {"verdict": prc.RED_TREE_FORK_LEVEL, "reason": "level"}

    assert mutant([RED], None, None)["verdict"] == prc.RED_TREE_FORK_LEVEL
    # ...and the real one refuses to say that. A control the mutant also passes is not a control.
    assert _verdict(behind=None, ahead=None)["verdict"] == prc.RED_TREE_FORK_NOT_ESTABLISHED


def test_a_half_read_fork_is_not_established_rather_than_the_half_that_answered():
    """`fork_state` returns a PAIR and either half can be None on its own -- `commits_behind`
    fetches and `commits_ahead` does not, so the fetch failing gives `(None, 0)`. Reporting that
    as `level` off the half that answered is the same fail-open through a narrower door."""
    assert _verdict(behind=None, ahead=0)["verdict"] == prc.RED_TREE_FORK_NOT_ESTABLISHED
    assert _verdict(behind=0, ahead=None)["verdict"] == prc.RED_TREE_FORK_NOT_ESTABLISHED


def test_a_bool_is_not_a_commit_count():
    """`isinstance(True, int)` is true. `True` reaching this field means something upstream wrote
    a flag where a count belongs, and rendering it as "1 commit behind" would invent a fork."""
    assert _verdict(behind=True, ahead=False)["verdict"] == prc.RED_TREE_FORK_NOT_ESTABLISHED


# ── PARTITION: every verdict must be REACHABLE ───────────────────────────────────────────────

def test_all_three_verdicts_are_reachable():
    """CLAUDE.md: a guard that refuses EVERYTHING passes every per-branch test above. One control
    over the whole partition is what catches a verdict that can never be returned -- and the
    pre-repair behaviour, which returns no verdict at all, fails exactly here."""
    reached = {
        _verdict(behind=41, ahead=3)["verdict"],
        _verdict(behind=0, ahead=0)["verdict"],
        _verdict(node_ids=())["verdict"],
    }
    assert reached == {prc.RED_TREE_FORK_DIVERGED,
                       prc.RED_TREE_FORK_LEVEL,
                       prc.RED_TREE_FORK_NOT_ESTABLISHED}


# ── FAIL-SAFE: every refusal names its reason ────────────────────────────────────────────────

@pytest.mark.parametrize("kwargs,needle", [
    ({"node_ids": ()}, "no red is named"),
    ({"behind": None, "ahead": None}, "was not recorded"),
    ({"behind": None, "ahead": 4}, "was not recorded"),
])
def test_every_refusal_is_not_established_and_names_why(kwargs, needle):
    v = _verdict(**kwargs)
    assert v["verdict"] == prc.RED_TREE_FORK_NOT_ESTABLISHED
    assert needle in v["reason"], v["reason"]
    # ...and never the flattering reading of its own silence.
    assert "This is not evidence the tree was level" in v["reason"] or "not settled" in v["reason"]


# ── THE READ SIDE: a record that never carried the field must not appear to ──────────────────

def test_a_blocking_record_predating_the_field_reads_as_unknown_not_level(tmp_path):
    prc.GATE_BLOCKING_TESTS_FILE.write_text(json.dumps(
        {"ts": prc.time.time(), "git_hash": HEAD, "census": prc.CENSUS_COMPLETE,
         "total_red": 1, "node_ids": [RED]}))
    assert prc.last_fork_state() == (None, None)


def test_a_stale_blocking_record_yields_no_fork(monkeypatch):
    """The age bound is the SAME one `last_blocking_tests` and `last_red_census` carry, so the
    three readers can never describe different cycles -- a fork from an hour-old record beside
    this cycle's node ids would be the carried-forward defect this module has paid for twice."""
    prc._write_blocking_tests([RED], HEAD, census=prc.CENSUS_COMPLETE)
    stale = prc.time.time() + prc.GATE_BLOCKING_TESTS_MAX_AGE_SECONDS + 1
    assert prc.last_fork_state(now=stale) == (None, None)


def test_the_recorded_fork_round_trips(monkeypatch):
    monkeypatch.setattr(prc, "_fork_state_for_record", lambda: (41, 3))
    prc._write_blocking_tests([RED], HEAD, census=prc.CENSUS_COMPLETE)
    assert prc.last_fork_state() == (41, 3)


def test_an_unreadable_origin_costs_the_field_and_never_the_record(monkeypatch):
    """A monitoring failure must not break the pipeline it monitors -- `_head_sha_for_attribution`
    beside it carries the same rule. The node ids ARE the record; the fork is a field on it, and
    losing the record to save the field is the wrong way round."""
    import background.origin_reconcile as orc

    def boom(project=None):
        raise RuntimeError("origin is unreachable")

    monkeypatch.setattr(orc, "fork_state", boom)
    monkeypatch.setattr(prc, "_fork_state_for_record", REAL_FORK_READER)
    prc._write_blocking_tests([RED], HEAD, census=prc.CENSUS_COMPLETE)

    node_ids, git_hash = prc.last_blocking_tests()
    assert node_ids == [RED] and git_hash == HEAD
    assert prc.last_fork_state() == (None, None)


def test_the_fork_read_goes_through_the_one_seam(monkeypatch):
    """`origin_reconcile.fork_state` exists BECAUSE a pin against a list of functions is
    fail-open on the next function -- its docstring records 28 assertions that went red twice on
    that. A second door here would fork that history, and `tests/background/conftest.py`'s pin
    would stop steering this read."""
    import background.origin_reconcile as orc
    seen = {}

    def spy(project=None):
        seen["project"] = project
        return 41, 3

    monkeypatch.setattr(orc, "fork_state", spy)
    assert REAL_FORK_READER() == (41, 3)
    assert seen["project"] == prc.PROJECT_DIR


# ── THE RECORD ITSELF: the field must reach the file the RUNG-1 draw reads ───────────────────

def test_the_failure_record_carries_the_divergence(monkeypatch):
    """The state file is the thing that gets quoted -- by the RUNG-1 draw and by the seat brief.
    Recorded at the RECORD layer, not only in the alarm prose, for the reason this module already
    gives about carried-forward blocking lists."""
    monkeypatch.setattr(prc, "_fork_state_for_record", lambda: (41, 3))
    prc._write_blocking_tests([RED], HEAD, census=prc.CENSUS_COMPLETE)
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("a refusal", rc=1, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None)

    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["red_tree_fork"] == prc.RED_TREE_FORK_DIVERGED
    assert "41" in st["red_tree_fork_reason"]
    # ...and on the ENTRY too, which is what survives into the history a later episode reads.
    entry = st["failures"][-1]
    assert entry["red_tree_fork"] == prc.RED_TREE_FORK_DIVERGED
    assert entry["red_tree_fork_reason"] == st["red_tree_fork_reason"]


def test_the_incident_pair_can_both_be_told(monkeypatch):
    """THE TWO QUESTIONS ARE NOT ONE. On 2026-09-17 the red WAS at HEAD -- the publisher's scoped
    gate graded a clean checkout of exactly that SHA -- and was green at origin/main, because the
    fix landed on origin 59 minutes after the fork opened. `red_at_head: yes` was correct and
    read, to every consumer, as "repair this test". A record that could not say both at once
    could not describe the incident it exists for."""
    monkeypatch.setattr(prc, "_fork_state_for_record", lambda: (41, 0))
    prc._write_blocking_tests([RED], HEAD, census=prc.CENSUS_COMPLETE)
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("a refusal", rc=1, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None)

    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["red_at_head"] == prc.RED_AT_HEAD_YES
    assert st["red_tree_fork"] == prc.RED_TREE_FORK_DIVERGED
    assert ON_ORIGIN[:9] not in st["red_tree_fork_reason"]  # it names the counts, not a guess


def test_a_failure_naming_no_red_records_the_refusal_and_its_reason(monkeypatch):
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("behind origin", rc=77, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None)
    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["red_tree_fork"] == prc.RED_TREE_FORK_NOT_ESTABLISHED
    assert "no red is named" in st["red_tree_fork_reason"]


def test_a_liveness_write_does_not_erase_the_divergence(monkeypatch):
    """`_write_publish_gate_state` builds `out` from a FIXED key list, and this module has already
    paid twice for a field being dropped by the next writer. A heartbeat landing between the red
    and the reader must not take the caveat with it."""
    monkeypatch.setattr(prc, "_fork_state_for_record", lambda: (41, 3))
    prc._write_blocking_tests([RED], HEAD, census=prc.CENSUS_COMPLETE)
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("a refusal", rc=1, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None)

    prc._record_liveness_surface_refusal(label="Liveness heartbeat", cause="behind_origin",
                                         evidence="origin moved", git_hash=HEAD)

    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["red_tree_fork"] == prc.RED_TREE_FORK_DIVERGED
    assert "41" in st["red_tree_fork_reason"]


def test_a_green_gate_retires_the_divergence_with_the_red_it_described(monkeypatch):
    """Symmetric with `_clear_blocking_tests` and with `red_at_head`. A fork claim left standing
    after a green gate describes a red that no longer exists."""
    monkeypatch.setattr(prc, "_fork_state_for_record", lambda: (41, 3))
    prc._write_blocking_tests([RED], HEAD, census=prc.CENSUS_COMPLETE)
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("a refusal", rc=1, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None)
    assert json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())["red_tree_fork"] == \
        prc.RED_TREE_FORK_DIVERGED

    prc.record_publish_gate_success(markers_pending=0)
    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["red_tree_fork"] == prc.RED_TREE_FORK_NOT_ESTABLISHED
    assert "the gate passed" in st["red_tree_fork_reason"]


def test_a_state_file_predating_the_field_reads_as_not_established():
    """Never `level`, which would tell the reader divergence is ruled out on the strength of a
    question nobody put."""
    prc.PUBLISH_GATE_STATE_FILE.write_text(json.dumps(
        {"failures": [], "alerted_at": None, "blocking_tests": [RED]}))
    st = prc._read_publish_gate_state()
    assert st["red_tree_fork"] == prc.RED_TREE_FORK_NOT_ESTABLISHED
    assert "predates" in st["red_tree_fork_reason"]
