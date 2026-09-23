"""A citation written into `.publish_gate_state.json` must have been RUN at the HEAD it is
written against -- and a citation that does not reproduce there is recorded as DEAD, not kept.

THE DEFECT THIS CLOSES (measured 2026-09-23, from the live file, not inferred). The state file
carried, in one object:

    "blocking_tests": ["FAILED tests/design/test_atom_notes_store.py::test_declarations_match_the_store"],
    "red_at_head": "not_established",
    "red_at_head_reason": "the red was measured at git=6e984858f and HEAD is now git=5e078b4d8 ..."

The cited test passes in 0.53s. The record already COMPUTED that its citation described a
different commit's tree -- and then wrote the citation out unchanged, beside the disclaimer.
The citation is the concrete part, so the citation is what the next reader acts on: it cost one
seat invocation a diagnosis, and the live refusal was in a different field the whole time.

`red_at_head_verdict` settles WHICH TREE the red was measured on. It never re-asks the
question. This does, through the same `_head_checkout()` the gate's own subject comes through --
re-asking in the shared working tree would answer about whatever the lanes have uncommitted.

R15, both directions:
  * FIRES       -- a citation whose tests all pass at HEAD is recorded `dead` and the node ids
                   leave `blocking_tests`. That is the exact instance above.
  * MUTATION    -- dropping the `blocking = list(citation["live_node_ids"])` assignment in
                   `record_publish_gate_failure` leaves the green test named, and
                   `test_a_dead_citation_does_not_survive_in_the_field_readers_reach_for_first`
                   goes red. Dropping the call itself reds every wiring test here.
  * PARTITION   -- one control asserts all four verdicts are REACHABLE AND DISTINCT. A reading
                   that answered `not_established` to everything would pass every per-branch
                   test in this file and is the shape CLAUDE.md names.
  * FAIL-SAFE   -- an unrunnable entry, an unavailable checkout, a timeout, an id the run gave
                   no verdict for, and a state file predating the field each degrade to
                   `not_established` WITH a reason and KEEP the citation whole. Retiring a
                   citation is the fail-open direction here.
  * NOT THE INVERSE -- `dead` is only ever reached from a POSITIVE reading that every cited id
                   passed. A green GATE must not write it (nothing was re-run), and neither
                   must an empty outcome map.
"""
import json

import pytest

import background.process_run_complete as prc

HEAD = "5e078b4d8a1c4e1f0b2d3c4e5f60718293a4b5c6"
OTHER = "6e984858f19f4da0b3e5e31ba6e6e6397f3f8c67"

# The real entries from the 2026-09-23 file, in the recorded short-summary form. Using the true
# subjects keeps this readable as the incident it is.
DEAD = ("FAILED tests/design/test_atom_notes_store.py"
        "::test_declarations_match_the_store")
LIVE = ("FAILED site/test_the_flat_churn_belief_reaches_the_reader.py"
        "::test_the_belief_is_rendered")


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


def _all(node_ids, still_red):
    """A runner that reports `still_red` for every cited id -- the whole citation, one way."""
    return lambda ids: ({i: still_red for i in ids}, None)


def _record(monkeypatch, reask_fn, node_ids=(DEAD,), census=None, head=HEAD, subject=OTHER):
    """Drive a real failure record through the publisher's own call site."""
    prc._write_blocking_tests(list(node_ids), subject,
                              census=census or prc.CENSUS_HOOK_CHAIN)
    monkeypatch.setattr(prc, "_head_sha", lambda: head)
    prc.record_publish_gate_failure("a refusal", rc=1, git_hash=head,
                                    send_ntfy_fn=lambda *a, **k: None, reask_fn=reask_fn)
    return json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())


# ── FIRES: the instance ──────────────────────────────────────────────────────────────────────

def test_a_dead_citation_does_not_survive_in_the_field_readers_reach_for_first(monkeypatch):
    """THE INCIDENT. The cited test passes at HEAD, so the record must stop citing it -- in
    `blocking_tests`, which is the field the RUNG-1 draw and the seat brief quote, not only in a
    caveat further down the object."""
    st = _record(monkeypatch, _all([DEAD], still_red=False))

    assert st["citation_at_head"] == prc.CITATION_DEAD
    assert st["blocking_tests"] == []
    # The ids are RETIRED, not LOST: a reader must still be able to see what was withdrawn.
    assert DEAD in st["citation_at_head_reason"]
    assert "DEAD" in st["citation_at_head_reason"]


def test_a_dead_citation_takes_its_depth_claim_and_its_blame_trail_with_it(monkeypatch):
    """`total_red: 3` beside an empty list is the accusation-with-no-accused shape inverted --
    this module's own words for the defect one field over. And a blame trail derived from a test
    that has gone green sends the reader at that test's imports instead."""
    st = _record(monkeypatch, _all([DEAD], still_red=False))

    assert st["total_red"] == 0
    assert st["suspects"] == {}
    assert st["cited_findings"] == []
    # ...and the attribution is re-asked FROM the withdrawn citation, never left describing
    # node ids this record no longer makes.
    assert st["red_at_head"] == prc.RED_AT_HEAD_NOT_ESTABLISHED
    assert "no red is named" in st["red_at_head_reason"]


def test_a_citation_that_still_reproduces_is_kept_whole(monkeypatch):
    """THE INVERSE MUST SURVIVE. A mechanism that clears every citation would pass the test
    above and would have deleted every real wedge cause we have ever recorded."""
    st = _record(monkeypatch, _all([DEAD], still_red=True))

    assert st["citation_at_head"] == prc.CITATION_REPRODUCES
    assert st["blocking_tests"] == [DEAD]
    assert "still red" in st["citation_at_head_reason"]


def test_a_green_member_is_dropped_and_the_red_one_is_kept(monkeypatch):
    """Two cited ids, one repaired since. "NO GREEN TEST MAY APPEAR IN A BLOCKING LIST" is
    already this module's rule; a whole-list verdict would either keep the green one or discard
    the red one, and both send the reader wrong."""
    def reask(ids):
        return {DEAD: False, LIVE: True}, None

    st = _record(monkeypatch, reask, node_ids=(DEAD, LIVE))

    assert st["citation_at_head"] == prc.CITATION_REPRODUCES
    assert st["blocking_tests"] == [LIVE]
    assert DEAD in st["citation_at_head_reason"]


# ── THE QUESTION IS ONLY PUT WHEN IT IS OPEN ─────────────────────────────────────────────────

def test_a_red_the_scoped_gate_measured_at_head_is_not_re_run(monkeypatch):
    """`RED_AT_HEAD_YES` means the publisher's own gate graded a clean checkout of exactly HEAD,
    so the citation reproduces by construction. Keyed to that PROPERTY, not to a list of causes:
    a re-run here buys nothing and spends the publish path's allowance."""
    asked = []

    def reask(ids):
        asked.append(ids)
        return {i: False for i in ids}, None

    st = _record(monkeypatch, reask, census=prc.CENSUS_COMPLETE, subject=HEAD)

    assert st["red_at_head"] == prc.RED_AT_HEAD_YES
    assert asked == []
    assert st["citation_at_head"] == prc.CITATION_NOT_ASKED
    assert st["blocking_tests"] == [DEAD]


def test_a_failure_naming_no_red_says_there_was_nothing_to_re_ask(monkeypatch):
    """A failure with no citation is the common case (`behind_origin` is one). It must say why
    it cannot answer, not stay silent and not claim HEAD is green."""
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    prc.record_publish_gate_failure("behind origin", rc=77, git_hash=HEAD,
                                    send_ntfy_fn=lambda *a, **k: None,
                                    reask_fn=_all([], still_red=False))
    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())

    assert st["citation_at_head"] == prc.CITATION_NOT_ESTABLISHED
    assert "no red is named" in st["citation_at_head_reason"]


# ── FAIL-SAFE: every refusal keeps the citation ──────────────────────────────────────────────

@pytest.mark.parametrize("outcomes,unavailable,why", [
    ({}, "a clean checkout of HEAD could not be materialised", "checkout"),
    ({}, "the re-run outran its 240s budget", "timeout"),
    ({}, "1 of the 1 recorded entries is not a runnable node id -- `ERROR x.py - E`", "unrunnable"),
    ({}, None, "no verdict returned for the cited id"),
])
def test_a_refused_re_ask_keeps_the_citation_whole(monkeypatch, outcomes, unavailable, why):
    """R15: an unavailable check is a FAILED check. Every one of these is a question nobody
    answered, and answering it `dead` would delete a live wedge cause on the strength of a
    checkout that would not build. The last row is the subtle one -- an EMPTY outcome map with
    no stated reason must read as unknown, never as 'nothing failed'."""
    st = _record(monkeypatch, lambda ids: (outcomes, unavailable))

    assert st["citation_at_head"] == prc.CITATION_NOT_ESTABLISHED, why
    assert st["blocking_tests"] == [DEAD], why
    assert st["citation_at_head_reason"], why


def test_a_skipped_test_is_not_a_live_citation():
    """A reader sent at a skipped test finds nothing. Only FAILED and ERROR are reds -- so a
    citation made entirely of skips is as dead as one made entirely of passes."""
    out = "tests/a.py::test_x SKIPPED (needs a GPU)  [100%]"
    assert prc.parse_citation_outcomes(out, ["FAILED tests/a.py::test_x"]) == {
        "FAILED tests/a.py::test_x": False}


def test_an_id_the_run_never_reported_on_is_unknown_and_never_green():
    """The asymmetry the whole mechanism rests on. A collection error, a rename or a plugin
    refusing the session leaves an id with no verdict; reading that as a pass would retire a
    citation the run never looked at."""
    out = "tests/a.py::test_x PASSED  [100%]"
    outcomes = prc.parse_citation_outcomes(out, ["FAILED tests/a.py::test_x",
                                                 "FAILED tests/b.py::test_y"])
    assert "FAILED tests/b.py::test_y" not in outcomes

    v = prc.citation_at_head_verdict(["FAILED tests/a.py::test_x", "FAILED tests/b.py::test_y"],
                                     prc.RED_AT_HEAD_NOT_ESTABLISHED, outcomes)
    assert v["verdict"] == prc.CITATION_NOT_ESTABLISHED
    assert v["live_node_ids"] == ["FAILED tests/a.py::test_x", "FAILED tests/b.py::test_y"]
    assert "tests/b.py::test_y" in v["reason"]


def test_an_entry_that_is_not_a_runnable_node_id_refuses_instead_of_guessing():
    """`ERROR tests/x.py - ImportError` is a real recorded shape: a collection failure names a
    FILE. Running the file answers a WIDER question than the one cited, so the real runner
    refuses -- without materialising a checkout, which is what makes this cheap to assert."""
    outcomes, unavailable = prc._reask_citation_at_head(
        ["ERROR tests/design/test_atom_notes_store.py - ImportError: no module named x"])

    assert outcomes == {}
    assert "not a runnable node id" in unavailable


# ── THE PARSER READS WHAT PYTEST ACTUALLY PRINTS ─────────────────────────────────────────────

def test_the_parser_reads_a_verbatim_pytest_v_run_and_not_its_own_summary():
    """Verbatim output, because a parser tested only against strings written to satisfy it is a
    parser tested against itself. The short-summary `FAILED <nodeid>` lines start with the
    OUTCOME, so they must not be mistaken for per-test verdict lines -- if they were, a failure
    would be counted twice and a pass beside it could be overwritten."""
    out = (
        "collected 2 items\n"
        "\n"
        "tests/a.py::test_x PASSED                                                [ 50%]\n"
        "tests/a.py::test_y FAILED                                                [100%]\n"
        "\n"
        "=========================== short test summary info ============================\n"
        "FAILED tests/a.py::test_y - assert 0 == 1\n"
        "========================= 1 failed, 1 passed in 0.53s ==========================\n"
    )
    outcomes = prc.parse_citation_outcomes(
        out, ["FAILED tests/a.py::test_x", "FAILED tests/a.py::test_y"])

    assert outcomes == {"FAILED tests/a.py::test_x": False,
                        "FAILED tests/a.py::test_y": True}


def test_the_recorded_form_and_the_bare_node_id_have_one_reader():
    """`blocking_test_files` and the re-ask must not disagree about what was cited -- two
    readings of the recorded form would eventually blame one test and run another."""
    assert prc.bare_node_id(DEAD) == DEAD[len("FAILED "):]
    assert prc.bare_node_id("ERROR tests/a.py - boom") == "tests/a.py"
    assert prc.blocking_test_files([DEAD]) == ["tests/design/test_atom_notes_store.py"]


# ── PARTITION: every verdict is reachable, and they are DISTINCT ─────────────────────────────

def test_the_reading_can_reach_all_four_verdicts_and_they_are_distinct():
    """A guard that refuses everything passes every per-branch test above. This asserts the
    partition over the whole set of SHAPES -- and asserts the verdicts are distinct, so two
    shapes collapsing onto one answer cannot hide here either."""
    ids = [DEAD]
    shapes = {
        "already graded at HEAD": prc.citation_at_head_verdict(
            ids, prc.RED_AT_HEAD_YES, {}),
        "all cited pass": prc.citation_at_head_verdict(
            ids, prc.RED_AT_HEAD_NOT_ESTABLISHED, {DEAD: False}),
        "still red": prc.citation_at_head_verdict(
            ids, prc.RED_AT_HEAD_NOT_ESTABLISHED, {DEAD: True}),
        "could not ask": prc.citation_at_head_verdict(
            ids, prc.RED_AT_HEAD_NOT_ESTABLISHED, {}, "the checkout would not build"),
        "nothing cited": prc.citation_at_head_verdict(
            [], prc.RED_AT_HEAD_NOT_ESTABLISHED, {}),
    }
    verdicts = {name: v["verdict"] for name, v in shapes.items()}

    assert verdicts["already graded at HEAD"] == prc.CITATION_NOT_ASKED
    assert verdicts["all cited pass"] == prc.CITATION_DEAD
    assert verdicts["still red"] == prc.CITATION_REPRODUCES
    assert verdicts["could not ask"] == prc.CITATION_NOT_ESTABLISHED
    assert verdicts["nothing cited"] == prc.CITATION_NOT_ESTABLISHED
    # Four answers over five shapes, and every reason distinct: the two that share a verdict
    # must still tell a reader which refusal they are.
    assert len(set(verdicts.values())) == 4
    assert len({v["reason"] for v in shapes.values()}) == len(shapes)


# ── THE RECORD ITSELF ────────────────────────────────────────────────────────────────────────

def test_a_liveness_write_does_not_erase_the_re_ask(monkeypatch):
    """`_write_publish_gate_state` builds from a FIXED key list, and this module has paid twice
    for a field being dropped by the next writer. A heartbeat landing between the re-ask and the
    reader must not restore the dead citation's silence."""
    _record(monkeypatch, _all([DEAD], still_red=True))
    prc._record_liveness_surface_refusal(label="Liveness heartbeat", cause="behind_origin",
                                         evidence="origin moved", git_hash=HEAD)

    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["citation_at_head"] == prc.CITATION_REPRODUCES
    assert "still red" in st["citation_at_head_reason"]


def test_a_green_gate_retires_the_re_ask_and_does_not_call_the_citation_dead(monkeypatch):
    """Symmetric with the attribution beside it -- but NOT `dead`. Nothing was re-run here, and
    a citation recorded dead on the strength of a passing gate is exactly the measurement this
    field exists to stop being skipped."""
    _record(monkeypatch, _all([DEAD], still_red=True))
    prc.record_publish_gate_success(markers_pending=0)

    st = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert st["citation_at_head"] == prc.CITATION_NOT_ESTABLISHED
    assert "no citation left to re-ask" in st["citation_at_head_reason"]


def test_a_state_file_predating_the_field_reads_as_not_established(tmp_path):
    """Never `reproduces` -- which tells a reader the citation is safe to act on -- and never
    `not_asked`, which claims the scoped gate graded HEAD. An old record made neither claim."""
    prc.PUBLISH_GATE_STATE_FILE.write_text(json.dumps(
        {"failures": [], "alerted_at": None, "blocking_tests": [DEAD]}))
    st = prc._read_publish_gate_state()

    assert st["citation_at_head"] == prc.CITATION_NOT_ESTABLISHED
    assert "predates" in st["citation_at_head_reason"]
    assert st["blocking_tests"] == [DEAD]


def test_the_entry_carries_the_reading_into_the_history_a_later_episode_reads(monkeypatch):
    """Top level is what the RUNG-1 draw quotes; the ENTRY is what survives into the failure
    history. Both, for the reason the attribution beside it already gives."""
    st = _record(monkeypatch, _all([DEAD], still_red=False))
    entry = st["failures"][-1]

    assert entry["citation_at_head"] == prc.CITATION_DEAD
    assert entry["citation_at_head_reason"] == st["citation_at_head_reason"]
