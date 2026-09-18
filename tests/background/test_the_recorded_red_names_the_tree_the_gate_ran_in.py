"""A red is filed against the tree the gate RAN IN, not the tree the simulation came from.

THE DEFECT THIS CLOSES (measured 2026-09-18 on the live record, not inferred). The publish path
carries one sha, `git_hash`, read off the run MARKER -- the commit the SIMULATION was produced
at. The gate's subject is a different commit: `_head_checkout` extracts `_head_sha()` and
`_make_checkout_a_repo` writes that into the checkout's `.git/HEAD`. A sim run takes ~26 minutes
and other lanes land throughout, so the two agree only when nothing landed meanwhile.

OBSERVED: at 2026-09-18 21:57:27Z `.last_gate_blocking_tests.json` recorded `git_hash: ec14df3c7`
while this module's own log line, at the same instant, read "HEAD is now git=d16c77ea9". The
census ran in a checkout of `d16c77ea9` and was filed against an ancestor 24 commits behind it.

WHAT IT COST, which is the whole reason this is a control and not a tidy-up. `red_at_head_verdict`
answers "was this red at HEAD?" by comparing the recorded sha against HEAD. Fed the marker's, it
can only ever answer `not_established` -- which it did for all 13 failures of that wedge. The
RUNG-1 priority-zero draw then told the seat the red "may ALREADY have been repaired", and an
invocation went to establish by hand what the record exists to state. The cited red WAS repaired,
24 commits earlier; nothing in the machinery could say so.

WHY THE EXISTING CONTROL WAS GREEN THROUGHOUT.
`test_a_recorded_red_says_which_tree_it_was_measured_on.py` puts `red_at_head_verdict` on trial as
a pure function and passes `blocking_hash=HEAD` in itself. Its premise -- that the sha beside the
red names the graded checkout -- is the half that was false, and it is the CALLER's half. This
file tests the caller. (CLAUDE.md: a control keyed to today's answer goes green while the claim
rots; the answer here is "which tree", and only the writer knows it.)

KEYED TO THE PROPERTY, NEVER TO A SHA. Nothing below asserts `ec14df3c7`, or 13, or 24. The
property is: **the attribution reads the sha of the tree the suite ran in, and says so when it
cannot** -- so a record goes quiet about which tree only when the checkout itself would not say.

MUTATIONS (each must fire, and which test catches it):
  (a) drop `graded_sha` from the record -- `..._THE_RECORD_CARRIES_THE_GRADED_TREE`;
  (b) attribute from the MARKER's sha again -- `..._A_RED_GRADED_AT_HEAD_IS_ATTRIBUTED_TO_HEAD`,
      and `..._THE_MARKERS_SHA_STILL_CANNOT_ANSWER` is the poison round proving that leg is not
      passing because the two shas happen to agree;
  (c) re-derive the graded sha from the LIVE repo instead of the checkout --
      `..._THE_GRADED_SHA_IS_THE_CHECKOUTS_OWN_STATEMENT`;
  (d) let an unusable sha through `last_graded_sha` -- `..._A_CHECKOUT_THAT_WILL_NOT_SAY`;
  (e) return the marker's sha from `graded_sha_of` on failure -- same test: `None` is the answer,
      and the fallback must carry `not_established` rather than substitute silently.

THE PARTITION CONTROL COMES FIRST. A `graded_sha_of` that answered `None` for everything, or an
attribution that answered `not_established` for everything, passes every per-branch leg written
separately -- and `not_established`-for-everything is EXACTLY the pre-repair behaviour. So one
statement asserts both verdicts are reachable from one writer.
"""
import json

import pytest

import background.process_run_complete as prc

# Two real-shaped commits that are not each other. Which characters they are is irrelevant and
# deliberately not asserted anywhere below.
GRADED = "d16c77ea9f1c2b3a4d5e6f708192a3b4c5d6e7f8"
MARKER = "ec14df3c7a1b2c3d4e5f60718293a4b5c6d7e8f9"
RED = ("tests/background/test_a_swept_row_names_which_of_the_three_dispositions_it_was.py"
       "::test_A_REDRAWN_ROW_IS_NOT_DONE_AGAIN_and_the_old_credit_does_not_settle_the_new_window")


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


def _checkout(tmp_path, head_text, name="co"):
    """A directory shaped exactly as `_make_checkout_a_repo` leaves one: a detached `.git/HEAD`."""
    d = tmp_path / name
    (d / ".git").mkdir(parents=True)
    if head_text is not None:
        (d / ".git" / "HEAD").write_text(head_text)
    return d


def _file_a_red(tmp_path, monkeypatch, *, graded, marker=MARKER, census=None):
    """Drive the real writer the way `_run_gate_in` does, and return the record it wrote."""
    monkeypatch.setattr(prc, "_fork_state_for_record", lambda *a, **k: (0, 1))
    result = type("R", (), {"stdout": "FAILED " + RED, "stderr": "", "returncode": 1})()
    prc._log_gate_failure_payload(
        result, marker, census=([RED], census or prc.CENSUS_COMPLETE), graded_sha=graded)
    return json.loads((tmp_path / ".blocking.json").read_text())


# ── THE PARTITION COMES FIRST ────────────────────────────────────────────────────────────────

def test_BOTH_ANSWERS_ARE_REACHABLE_FROM_ONE_WRITER(tmp_path, monkeypatch):
    """A writer that always said `None`, or an attribution that always said `not_established`,
    passes every leg below written separately -- and always-`not_established` IS the pre-repair
    behaviour this file exists to end. One statement over the whole partition, per CLAUDE.md."""
    said = prc.graded_sha_of(_checkout(tmp_path, GRADED + "\n", name="knows"))
    would_not = prc.graded_sha_of(_checkout(tmp_path, None, name="silent"))

    at_head = prc.red_at_head_verdict([RED], GRADED, prc.CENSUS_COMPLETE, GRADED)["verdict"]
    unknown = prc.red_at_head_verdict([RED], MARKER, prc.CENSUS_COMPLETE, GRADED)["verdict"]

    assert said == GRADED and would_not is None, (said, would_not)
    assert at_head == prc.RED_AT_HEAD_YES and unknown == prc.RED_AT_HEAD_NOT_ESTABLISHED, (
        at_head, unknown)


# ── FIRES ────────────────────────────────────────────────────────────────────────────────────

def test_THE_GRADED_SHA_IS_THE_CHECKOUTS_OWN_STATEMENT(tmp_path):
    """Read from the checkout, never re-derived from the live repo -- the question is which tree
    was GRADED, and a fresh `_head_sha()` answers about a HEAD that may since have moved."""
    assert prc.graded_sha_of(_checkout(tmp_path, GRADED + "\n")) == GRADED


def test_THE_RECORD_CARRIES_THE_GRADED_TREE_beside_the_markers_commit(tmp_path, monkeypatch):
    """Both shas, because there are two questions: `record_publish_gate_outcome` is documented to
    key on the marker's, and the attribution needs the one the suite actually ran against."""
    rec = _file_a_red(tmp_path, monkeypatch, graded=GRADED)
    assert rec["graded_sha"] == GRADED
    assert rec["git_hash"] == MARKER, "the marker's commit must survive -- this is additive"
    assert prc.last_graded_sha(now=rec["ts"]) == GRADED


def test_A_RED_GRADED_AT_HEAD_IS_ATTRIBUTED_TO_HEAD(tmp_path, monkeypatch):
    """THE DEFECT, end to end. A marker from an older commit, a gate that graded HEAD, and a red
    that is HEAD's. Before this repair the record said `not_established` and the RUNG-1 draw told
    the seat the red might already be gone."""
    _file_a_red(tmp_path, monkeypatch, graded=GRADED)
    monkeypatch.setattr(prc, "_head_sha_for_attribution", lambda: GRADED)

    res = prc.record_publish_gate_failure(
        "tests failed", rc=1, git_hash=MARKER, now=0, send_ntfy_fn=lambda m: "id")

    state = json.loads((tmp_path / ".publish_gate_state.json").read_text())
    assert state["red_at_head"] == prc.RED_AT_HEAD_YES, (res, state["red_at_head_reason"])


def test_THE_MARKERS_SHA_STILL_CANNOT_ANSWER(tmp_path):
    """The poison round for the leg above: it must pass because the attribution switched inputs,
    not because the two shas happen to name the same commit. Feed the marker's and the verdict
    goes straight back to the refusal the whole wedge was recorded under."""
    v = prc.red_at_head_verdict([RED], MARKER, prc.CENSUS_COMPLETE, GRADED)
    assert v["verdict"] == prc.RED_AT_HEAD_NOT_ESTABLISHED
    assert MARKER[:9] in v["reason"] and GRADED[:9] in v["reason"], v["reason"]


# ── FAIL-SAFE: AN UNAVAILABLE ANSWER IS NEVER A FLATTERING ONE ───────────────────────────────

@pytest.mark.parametrize("head_text", [None, "ref: refs/heads/main\n", "not-a-sha\n", "",
                                       "unknown"])
def test_A_CHECKOUT_THAT_WILL_NOT_SAY_yields_None_and_never_a_guess(tmp_path, head_text):
    """Absent, symbolic, junk, empty and the literal placeholder this pipeline really records all
    mean the same thing: the tree would not say. Returning the MARKER's sha here would be the
    silent substitution that produced the defect, wearing a repair's name."""
    d = _checkout(tmp_path, head_text, name="q" + str(abs(hash(head_text)) % 9973))
    assert prc.graded_sha_of(d) is None


def test_A_RECORD_WITH_NO_GRADED_TREE_falls_back_WITH_the_refusal(tmp_path, monkeypatch):
    """A record written before this field existed -- or by a cycle whose checkout would not say --
    is a red with no statement of which tree produced it, which is exactly what it was. The
    attribution degrades to the marker's sha AND to `not_established`, so the reader is told the
    question is open rather than handed an answer the record cannot support."""
    _file_a_red(tmp_path, monkeypatch, graded=None)
    assert prc.last_graded_sha(now=0) is None

    monkeypatch.setattr(prc, "_head_sha_for_attribution", lambda: GRADED)
    prc.record_publish_gate_failure(
        "tests failed", rc=1, git_hash=MARKER, now=0, send_ntfy_fn=lambda m: "id")

    state = json.loads((tmp_path / ".publish_gate_state.json").read_text())
    assert state["red_at_head"] == prc.RED_AT_HEAD_NOT_ESTABLISHED
    assert MARKER[:9] in state["red_at_head_reason"], state["red_at_head_reason"]


def test_AN_UNUSABLE_SHA_IN_THE_RECORD_IS_REFUSED_AT_THE_READER_TOO(tmp_path, monkeypatch):
    """The reader re-asks the question the writer already asked, and this is NOT belt-and-braces.

    `graded_sha_of` filters at the write, so under today's writer a record can only ever carry a
    usable sha or `None` -- which makes dropping the reader's check look like an equivalence. It
    is not one, and the difference is what the READER is told: the attribution takes
    `graded_sha or blocking_hash`, so a truthy-but-unusable value (a legacy record, a
    hand-repaired one, the literal `"unknown"` this pipeline really writes elsewhere) would
    DISCARD the marker's commit and put a non-commit in the reason instead. `not_established`
    either way; a reason naming nothing either way is a worse record than one naming the marker.
    """
    rec = _file_a_red(tmp_path, monkeypatch, graded=GRADED)
    rec["graded_sha"] = "unknown"
    (tmp_path / ".blocking.json").write_text(json.dumps(rec))
    assert prc.last_graded_sha(now=rec["ts"]) is None

    monkeypatch.setattr(prc, "_head_sha_for_attribution", lambda: GRADED)
    prc.record_publish_gate_failure(
        "tests failed", rc=1, git_hash=MARKER, now=0, send_ntfy_fn=lambda m: "id")

    state = json.loads((tmp_path / ".publish_gate_state.json").read_text())
    assert state["red_at_head"] == prc.RED_AT_HEAD_NOT_ESTABLISHED
    assert MARKER[:9] in state["red_at_head_reason"], state["red_at_head_reason"]


def test_A_STALE_RECORD_IS_NOT_A_GRADED_TREE(tmp_path, monkeypatch):
    """Staleness reads as unknown for the reason `last_fork_state` gives about the fork: the tree
    this names has moved, so quoting its sha would attribute today's red to yesterday's checkout
    -- the same class of error one layer down."""
    rec = _file_a_red(tmp_path, monkeypatch, graded=GRADED)
    fresh = prc.last_graded_sha(now=rec["ts"])
    stale = prc.last_graded_sha(now=rec["ts"] + prc.GATE_BLOCKING_TESTS_MAX_AGE_SECONDS + 1)
    assert fresh == GRADED and stale is None, (fresh, stale)
