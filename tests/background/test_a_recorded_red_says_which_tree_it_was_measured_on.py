"""A failure that NAMES a red must also say WHOSE red it is -- HEAD's, or the commit's.

THE DEFECT THIS CLOSES (measured 2026-09-16, not inferred). The publish episode opened
2026-09-10 recorded thirty-two consecutive failures. Every one of them named a red. Not one of
them said which TREE that red was measured on, so every episode re-derived the same question
from nothing -- and the RUNG-1 draw sent to repair the red recorded against `3346182b6` was sent
at `site/knowledge/test_index_reflects_the_record.py::test_the_card_copy_is_quoted_from_the_record`.

In clean `git archive` extracts that test passes at HEAD (`6a9ead27a`) AND at `3346182b6`
itself. It was never HEAD's red. It was red only on the tree the publish COMMIT would create,
and an invocation was spent hunting it where it is green.

THE ANSWER WAS ALREADY IN THE RECORD. `census` names the producer, and the two producers have
different subjects: the publisher's scoped gate judges a clean checkout of one SHA, the
pre-commit hook chain judges that SHA plus this publish's own writes. R15 FAIL-SILENT -- the
diagnostic was taken and dropped at the record layer, which is this module's recurring shape.

R15, both directions:
  * FIRES      -- each of the three verdicts is reached by the input that earns it, and the
                  reason names the tree.
  * PARTITION  -- one control asserts all three verdicts are REACHABLE (CLAUDE.md: a guard that
                  refuses everything passes every per-branch test). The pre-repair behaviour --
                  no field at all -- fails it.
  * MUTATION   -- reading the hook chain as HEAD's red is asserted to FAIL. That is the exact
                  defect: it is what sent the draw at a green test.
  * NOT THE INVERSE -- `commit_tree_subject` must never be published as "green at HEAD". The
                  subject was a different tree; HEAD is unproven either way.
  * FAIL-SAFE  -- unreadable HEAD, `"unknown"`, a stale subject and no red each degrade to
                  `not_established` WITH a reason, never to a verdict.
"""
import json

import pytest

import background.process_run_complete as prc

HEAD = "6a9ead27a519f4da0b3e5e31ba6e6e6397f3f8c6"
OTHER = "3346182b6aa1c4e1f0b2d3c4e5f60718293a4b5c"
# The real node id the 2026-09-16 draw was sent at, and which is green in a clean extract of
# both commits above. Using the true subject keeps this test readable as the incident it is.
RED = ("site/knowledge/test_index_reflects_the_record.py"
       "::test_the_card_copy_is_quoted_from_the_record")


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


def _verdict(node_ids=(RED,), blocking_hash=HEAD, census=prc.CENSUS_COMPLETE, head=HEAD):
    return prc.red_at_head_verdict(list(node_ids), blocking_hash, census, head)


# ── FIRES ────────────────────────────────────────────────────────────────────────────────────

def test_the_scoped_gates_red_at_this_head_is_recorded_as_at_head():
    """The publisher's own gate judges a clean checkout of the SHA, so its red IS HEAD's."""
    v = _verdict(census=prc.CENSUS_COMPLETE)
    assert v["verdict"] == prc.RED_AT_HEAD_YES
    assert "clean checkout" in v["reason"]
    assert HEAD[:9] in v["reason"]


def test_the_hook_chains_red_is_recorded_against_the_tree_the_commit_would_create():
    """THE INCIDENT. The hook chain judges HEAD PLUS this publish's writes, so its red is not
    established as HEAD's -- and the record must send the reader at the writes, not at HEAD."""
    v = _verdict(census=prc.CENSUS_HOOK_CHAIN)
    assert v["verdict"] == prc.RED_AT_HEAD_COMMIT_TREE_ONLY
    assert "WOULD create" in v["reason"]


def test_the_hook_chain_verdict_is_not_published_as_green_at_head():
    """THE INVERSE MUST NOT BE CLAIMED. `commit_tree_subject` says the subject was a different
    tree. A reader who takes it as 'HEAD is green' has been misled by the same one word that
    caused the incident, in the other direction."""
    v = _verdict(census=prc.CENSUS_HOOK_CHAIN)
    assert v["verdict"] != prc.RED_AT_HEAD_YES
    assert "NOT established as HEAD's red" in v["reason"]
    # It must not assert HEAD is green either -- only that HEAD was not the subject.
    assert "green at HEAD" not in v["reason"]


# ── MUTATION: the pre-repair reading, asserted to fail ───────────────────────────────────────

def test_reading_the_hook_chain_as_heads_red_is_the_defect_and_fails_this_control():
    """The mutant: attribute by SHA alone and ignore the census -- i.e. treat 'the record's hash
    equals HEAD' as 'the red is at HEAD'. That is precisely what sent the 2026-09-16 draw at a
    test that is green in a clean extract of both commits."""
    def mutant(node_ids, blocking_hash, census, head_sha):
        if node_ids and prc._sha_agrees(blocking_hash, head_sha):
            return {"verdict": prc.RED_AT_HEAD_YES, "reason": "hash matches HEAD"}
        return {"verdict": prc.RED_AT_HEAD_NOT_ESTABLISHED, "reason": "no"}

    assert mutant([RED], HEAD, prc.CENSUS_HOOK_CHAIN, HEAD)["verdict"] == prc.RED_AT_HEAD_YES
    # ...and the real one refuses to say that. A control the mutant also passes is not a control.
    assert _verdict(census=prc.CENSUS_HOOK_CHAIN)["verdict"] != prc.RED_AT_HEAD_YES


# ── PARTITION: every verdict must be REACHABLE ───────────────────────────────────────────────

def test_all_three_verdicts_are_reachable():
    """CLAUDE.md: a guard that refuses EVERYTHING passes every per-branch test above. One
    control over the whole partition is what catches a verdict that can never be returned."""
    reached = {
        _verdict(census=prc.CENSUS_COMPLETE)["verdict"],
        _verdict(census=prc.CENSUS_HOOK_CHAIN)["verdict"],
        _verdict(node_ids=())["verdict"],
    }
    assert reached == {prc.RED_AT_HEAD_YES,
                       prc.RED_AT_HEAD_COMMIT_TREE_ONLY,
                       prc.RED_AT_HEAD_NOT_ESTABLISHED}


# ── FAIL-SAFE: every refusal names its reason ────────────────────────────────────────────────

@pytest.mark.parametrize("kwargs,needle", [
    ({"node_ids": ()}, "no red is named"),
    ({"head": None}, "git could not say what HEAD is"),
    ({"head": "unknown"}, "git could not say what HEAD is"),
    ({"blocking_hash": "unknown"}, "names no subject commit"),
    ({"blocking_hash": None}, "names no subject commit"),
    ({"blocking_hash": OTHER}, "different commit's tree"),
])
def test_every_refusal_is_not_established_and_names_why(kwargs, needle):
    v = _verdict(**kwargs)
    assert v["verdict"] == prc.RED_AT_HEAD_NOT_ESTABLISHED
    assert needle in v["reason"], v["reason"]


def test_unknown_is_a_recorded_value_and_is_no_commit_rather_than_a_different_one():
    """`"unknown"` is seven characters, so a bare length check admits it and the comparison then
    reports it as a DIFFERENT commit. It is not a different commit; it is no commit."""
    assert not prc._sha_is_usable("unknown")
    assert "different commit" not in _verdict(blocking_hash="unknown")["reason"]


def test_an_abbreviated_subject_still_agrees_with_full_head():
    """The record stores whatever the caller had -- 9 chars in the live file, 40 from
    `_head_sha`. A verdict that turned that into 'a different commit' would refuse every real
    failure this was built for."""
    assert prc._sha_agrees(HEAD[:9], HEAD)
    assert _verdict(blocking_hash=HEAD[:9])["verdict"] == prc.RED_AT_HEAD_YES
    # ...but not so short that a collision could pass for agreement.
    assert not prc._sha_agrees(HEAD[:4], HEAD)


def test_a_head_read_that_raises_costs_the_field_and_never_the_record(monkeypatch):
    """A monitoring failure must not break the pipeline it monitors: losing the whole failure
    record to save an attribution field is the wrong way round."""
    def boom():
        raise RuntimeError("git is wedged")
    monkeypatch.setattr(prc, "_head_sha", boom)
    assert prc._head_sha_for_attribution() is None


# ── THE RECORD ITSELF: the field must reach the file the RUNG-1 draw reads ───────────────────

@pytest.mark.parametrize("census,expected", [
    (prc.CENSUS_COMPLETE, prc.RED_AT_HEAD_YES),
    (prc.CENSUS_HOOK_CHAIN, prc.RED_AT_HEAD_COMMIT_TREE_ONLY),
])
def test_the_failure_record_carries_the_attribution(monkeypatch, census, expected):
    """The state file is the thing that gets quoted -- by the RUNG-1 draw and by the seat brief.
    Recorded at the RECORD layer, not only in the alarm prose, for the reason this module already
    gives about carried-forward blocking lists."""
    prc._write_blocking_tests([RED], HEAD, census=census)
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("a refusal", rc=1, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None)

    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["red_at_head"] == expected
    assert st["red_at_head_reason"]
    # ...and on the ENTRY too, which is what survives into the history a later episode reads.
    entry = st["failures"][-1]
    assert entry["red_at_head"] == expected
    assert entry["red_at_head_reason"] == st["red_at_head_reason"]


def test_a_failure_naming_no_red_still_records_the_refusal_and_its_reason(monkeypatch):
    """Thirty-two of thirty-two carried no attribution. A failure with no red is the common case
    -- `behind_origin` is one -- and it must say WHY it cannot attribute, not stay silent."""
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("behind origin", rc=77, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None)
    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["red_at_head"] == prc.RED_AT_HEAD_NOT_ESTABLISHED
    assert "no red is named" in st["red_at_head_reason"]


def test_a_green_gate_retires_the_attribution_with_the_red_it_described(monkeypatch):
    """Symmetric with `_clear_blocking_tests`. An attribution left standing after a green gate is
    a carried-forward claim about a red that no longer exists -- this module's own recurring
    defect, one field along."""
    prc._write_blocking_tests([RED], HEAD, census=prc.CENSUS_HOOK_CHAIN)
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("a refusal", rc=1, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None)
    assert json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())["red_at_head"] == \
        prc.RED_AT_HEAD_COMMIT_TREE_ONLY

    prc.record_publish_gate_success(markers_pending=0)
    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st.get("red_at_head", prc.RED_AT_HEAD_NOT_ESTABLISHED) == \
        prc.RED_AT_HEAD_NOT_ESTABLISHED
    assert "no named red" in st.get("red_at_head_reason", "no named red")


def test_a_liveness_write_does_not_erase_the_attribution(monkeypatch):
    """`_write_publish_gate_state` builds `out` from a FIXED key list, and this module has
    already paid twice for a field being dropped by the next writer -- both carry-forward
    clauses beside `last_clean_publish` exist for it. The liveness writers hand it a full
    `_read_publish_gate_state()` dict, so the setdefault is what makes this round-trip; if that
    default is ever removed, a heartbeat lands between the red and the reader and the
    attribution is gone."""
    prc._write_blocking_tests([RED], HEAD, census=prc.CENSUS_HOOK_CHAIN)
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("a refusal", rc=1, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None)

    prc._record_liveness_surface_refusal(label="Liveness heartbeat", cause="behind_origin",
                                         evidence="origin moved", git_hash=HEAD)

    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["red_at_head"] == prc.RED_AT_HEAD_COMMIT_TREE_ONLY
    assert "WOULD create" in st["red_at_head_reason"]


def test_a_state_file_predating_the_field_reads_as_not_established(tmp_path):
    """Never `yes` (which sends the reader at HEAD) and never `commit_tree_subject` (which sends
    them away from it) -- an old record made neither claim."""
    prc.PUBLISH_GATE_STATE_FILE.write_text(json.dumps(
        {"failures": [], "alerted_at": None, "blocking_tests": [RED]}))
    st = prc._read_publish_gate_state()
    assert st["red_at_head"] == prc.RED_AT_HEAD_NOT_ESTABLISHED
    assert "predates" in st["red_at_head_reason"]
