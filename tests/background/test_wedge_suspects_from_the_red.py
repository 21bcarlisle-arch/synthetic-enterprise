"""H42 -- the wedge alarm's suspects are re-derived from the RED, not from the inbox.

THE DEFECT THIS CLOSES. The publish-gate alarm's "also filed and unactioned in staging" block
was built by `filed_findings()`: the eight most recently modified WORKER_FINDING_*.md in
docs/staging/, ranked by mtime and linked to the failure printed above them by NOTHING. Its own
clause had to confess the measurement -- 0/8 named the cause in each of FIVE consecutive episodes
(WORKER_REPORT_{PUBLISH,FIFTH,SIXTH,THIRTEENTH}_WEDGE_SUSPECT_DISPOSITION_*) -- and the director
priced it at twenty minutes of every responder's time per episode, because the drawn worker read
"draw these FIRST" as an instruction and dispositioned eight irrelevant documents before starting.
The tell: the list was near-identical every episode while the cause differed every episode.

WHAT IS ASSERTED HERE, R15 both directions and driven rather than declared:
  * FIRES    -- with a recorded blocking test, the alarm names that test's file, the first-party
                modules it imports, the commits touching them, and only those staged findings
                whose text NAMES something on that trail.
  * MUTATION 1 (reinstate recency) -- recent, unlinked findings must NOT appear. Re-point the
                citation at mtime and `test_mutation_reinstating_the_recency_ranking_dies_here`
                fails.
  * MUTATION 2 (guess when you do not know) -- with NO recorded blocking test there must be no
                suspect block and no citation at all. Emit one anyway and
                `test_mutation_emitting_suspects_with_no_recorded_blocking_test_dies_here` fails.
  * FAIL-SILENT -- unreadable, malformed and STALE gate state each read as UNRECORDED (the
                killer pattern: an unavailable check is a FAILED check), never as "no suspects".
  * MEASURED (R12) -- every closed episode is scored into the hit-rate ledger and the running
                rate rides in the payload, so a re-derivation that is ALSO useless is visible
                rather than assumed better. The rate is a diagnostic; it is not a target, and
                nothing may be archived to move it.
"""
import json

import pytest

import background.process_run_complete as prc


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


class _Sink:
    def __init__(self):
        self.messages = []

    def __call__(self, msg, *a, **k):
        self.messages.append(msg)
        return "sent-id"


T0 = 1_800_000_000.0


def _fire(sink, *, n=3, t0=T0, step=600.0):
    """Drive a real streak through the real recorder and return the alarm text."""
    for i in range(n):
        prc.record_publish_gate_failure("rc=1 on run_complete_%d.md" % i, rc=1,
                                        git_hash="cafe%d" % i, now=t0 + i * step,
                                        send_ntfy_fn=sink)
    assert sink.messages, "the streak should have fired exactly one alarm"
    return sink.messages[-1]


def _record_red(node_ids, *, ts=T0, git_hash="deadbee"):
    prc.GATE_BLOCKING_TESTS_FILE.write_text(json.dumps(
        {"ts": ts, "git_hash": git_hash, "node_ids": node_ids}))


def _fake_project(tmp_path, monkeypatch, *, wedged_imports_module=True):
    """A minimal repo the derivation can actually walk: one test file, one first-party module."""
    root = tmp_path / "repo"
    (root / "tests" / "background").mkdir(parents=True)
    (root / "background").mkdir()
    (root / "background" / "__init__.py").write_text("")
    (root / "background" / "ruff_ratchet.py").write_text("RATCHET = 1\n")
    (root / "background" / "unrelated.py").write_text("X = 1\n")
    body = "import json\nimport pytest\n"
    if wedged_imports_module:
        body += "from background.ruff_ratchet import RATCHET\n"
    body += "\n\ndef test_x():\n    assert True\n"
    (root / "tests" / "background" / "test_wedged.py").write_text(body)
    monkeypatch.setattr(prc, "PROJECT_DIR", root)
    return root


def _staging(tmp_path, monkeypatch, files):
    sd = tmp_path / "staging"
    sd.mkdir(exist_ok=True)
    for name, text in files.items():
        (sd / name).write_text(text)
    monkeypatch.setattr(prc, "STAGING_DIR", sd)
    return sd


# ── the derivation itself ────────────────────────────────────────────────────

def test_blocking_test_files_reads_every_recorded_form():
    assert prc.blocking_test_files([
        "FAILED tests/background/test_a.py::test_one",
        "ERROR tests/background/test_b.py - ImportError: no module named x",
        "tests/background/test_c.py::TestK::test_two",
        "FAILED tests/background/test_a.py::test_three",   # same file, once
        "not a node id at all",
    ]) == ["tests/background/test_a.py", "tests/background/test_b.py",
           "tests/background/test_c.py"]


def test_first_party_imports_are_repo_modules_only(tmp_path, monkeypatch):
    root = _fake_project(tmp_path, monkeypatch)
    mods = prc.first_party_imports("tests/background/test_wedged.py", project_dir=root)
    assert mods == ["background/ruff_ratchet.py"], (
        "json and pytest cannot be the regression the gate is reporting; blaming them is how a "
        "suspect list becomes noise again"
    )


def test_an_unparseable_test_file_yields_an_empty_trail_not_a_guess(tmp_path, monkeypatch):
    root = _fake_project(tmp_path, monkeypatch)
    (root / "tests" / "background" / "broken.py").write_text("def (((:\n")
    assert prc.first_party_imports("tests/background/broken.py", project_dir=root) == []
    assert prc.first_party_imports("tests/background/does_not_exist.py", project_dir=root) == []


def test_blame_commits_on_an_unavailable_git_is_empty_not_invented(tmp_path, monkeypatch):
    root = _fake_project(tmp_path, monkeypatch)  # not a git repo
    assert prc.blame_commits(["background/ruff_ratchet.py"], project_dir=root) == []
    assert prc.blame_commits([], project_dir=root) == []


def test_wedge_suspects_is_empty_when_the_blocking_test_is_unrecorded(tmp_path, monkeypatch):
    root = _fake_project(tmp_path, monkeypatch)
    assert prc.wedge_suspects([], project_dir=root) == {}
    assert prc.wedge_suspects(["no node id here"], project_dir=root) == {}


# ── the alarm FIRES with a trail that came from the red ──────────────────────

def test_the_alarm_names_the_trail_of_the_actual_blocking_test(tmp_path, monkeypatch):
    root = _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {})
    _record_red(["FAILED tests/background/test_wedged.py::test_x"])
    msg = _fire(_Sink())
    assert "SUSPECTS (re-derived from the blocking test above" in msg, msg
    assert "background/ruff_ratchet.py" in msg
    assert "background/unrelated.py" not in msg, (
        "a module the blocking test does not import is not on its blame trail"
    )
    # No git repo behind the fake project -> the honest branch, not a fabricated commit.
    assert "NO commit in the last" in msg
    assert str(root)  # the derivation ran against the patched project dir


def test_only_findings_that_name_the_trail_are_cited(tmp_path, monkeypatch):
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {
        "WORKER_FINDING_THE_RUFF_RATCHET_IS_RED_AT_HEAD_2026-08-10.md":
            "the ratchet in background/ruff_ratchet.py reds at HEAD",
        "WORKER_FINDING_ARREARS_RAG_IS_FAIL_OPEN_2026-08-09.md":
            "the arrears RAG in company/collections/rag.py fails open",
    })
    _record_red(["FAILED tests/background/test_wedged.py::test_x"])
    msg = _fire(_Sink())
    assert "WORKER_FINDING_THE_RUFF_RATCHET_IS_RED_AT_HEAD_2026-08-10.md" in msg
    assert "WORKER_FINDING_ARREARS_RAG" not in msg


def test_mutation_reinstating_the_recency_ranking_dies_here(tmp_path, monkeypatch):
    """MUTATION 1. Eight findings filed seconds ago, NONE of them on the blame trail -- the
    exact 0/8 shape measured five episodes running. Re-point the citation at mtime and this
    test fails, which is the whole point of it existing."""
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {
        "WORKER_FINDING_FRESH_%02d_2026-08-10.md" % i: "an unrelated finding about billing"
        for i in range(8)
    })
    _record_red(["FAILED tests/background/test_wedged.py::test_x"])
    msg = _fire(_Sink())
    assert "WORKER_FINDING_FRESH" not in msg, (
        "recency is not evidence: a finding filed today about another subsystem is backlog"
    )
    assert json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())["cited_findings"] == []


def test_mutation_emitting_suspects_with_no_recorded_blocking_test_dies_here(tmp_path, monkeypatch):
    """MUTATION 2. No blocking test on record -> the alarm must say UNRECORDED and stop. Any
    fallback -- recency, a bare module list, 'probably the last commit' -- fails here."""
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {
        "WORKER_FINDING_THE_RUFF_RATCHET_IS_RED_AT_HEAD_2026-08-10.md":
            "background/ruff_ratchet.py reds at HEAD",
    })
    assert not prc.GATE_BLOCKING_TESTS_FILE.exists()
    msg = _fire(_Sink())
    assert "BLOCKING TEST: UNRECORDED" in msg
    assert "SUSPECTS (re-derived" not in msg
    assert "WORKER_FINDING" not in msg, "an unknown red buys no suspects at all"
    assert json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())["suspects"] == {}


@pytest.mark.parametrize("case,content", [
    ("stale", json.dumps({"ts": T0 - 10 * prc.GATE_SUITE_TIMEOUT_SECONDS, "git_hash": "old",
                          "node_ids": ["FAILED tests/background/test_wedged.py::test_x"]})),
    ("malformed", "{not json"),
    ("wrong shape", json.dumps(["FAILED tests/background/test_wedged.py::test_x"])),
])
def test_fail_silent_gate_state_reads_unrecorded_never_no_suspects(tmp_path, monkeypatch,
                                                                   case, content):
    """FAIL-SILENT killer pattern. An unavailable check is a FAILED check: each of these must
    reach the reader as "I do not know", which is actionable, never as a confident silence."""
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {})
    prc.GATE_BLOCKING_TESTS_FILE.write_text(content)
    msg = _fire(_Sink())
    assert "BLOCKING TEST: UNRECORDED" in msg, case
    assert "SUSPECTS (re-derived" not in msg, case


# ── the hit rate is MEASURED, and rides in the payload (R12: diagnostic, not target) ──

def test_the_hit_rate_rides_in_every_alarm(tmp_path, monkeypatch):
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {})
    msg = _fire(_Sink())
    assert "SUSPECT HIT RATE: not yet measured" in msg, (
        "the rate must ride in the payload even before any episode has closed -- an unmeasured "
        "mechanism that says nothing about being unmeasured is how the last one survived five "
        "episodes"
    )


def test_a_closed_episode_scores_the_list_it_emitted(tmp_path, monkeypatch):
    """The repair touched a path the alarm had NAMED -> a hit, recorded and then reported."""
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {})
    _record_red(["FAILED tests/background/test_wedged.py::test_x"])
    _fire(_Sink())
    monkeypatch.setattr(prc, "_paths_changed_since",
                        lambda since, **kw: {"background/ruff_ratchet.py", "docs/x.md"})
    prc.record_publish_gate_success(now=T0 + 3600, markers_pending=0)
    eps = json.loads(prc.WEDGE_SUSPECT_HIT_RATE_FILE.read_text())["episodes"]
    assert [e["hit"] for e in eps] == [True]
    assert "SUSPECT HIT RATE: 1/1" in prc.suspect_hit_rate_phrase()


def test_a_miss_is_recorded_as_a_miss(tmp_path, monkeypatch):
    """The direction that makes the metric worth having: the repair landed somewhere this
    alarm never mentioned. If a miss could not be recorded the rate would be decoration."""
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {})
    _record_red(["FAILED tests/background/test_wedged.py::test_x"])
    _fire(_Sink())
    monkeypatch.setattr(prc, "_paths_changed_since",
                        lambda since, **kw: {"sim/weather_weighting.py"})
    prc.record_publish_gate_success(now=T0 + 3600, markers_pending=0)
    assert [e["hit"] for e in json.loads(
        prc.WEDGE_SUSPECT_HIT_RATE_FILE.read_text())["episodes"]] == [False]
    assert "SUSPECT HIT RATE: 0/1" in prc.suspect_hit_rate_phrase()


def test_an_episode_with_no_list_is_not_scored_as_a_hit(tmp_path, monkeypatch):
    """An episode where the blocking test was unrecorded emitted no suspects at all. Counting
    that as a hit -- or as a miss -- would let the rate drift on episodes the mechanism never
    spoke to. It is counted separately and said out loud."""
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {})
    _fire(_Sink())  # no blocking record -> no suspects
    prc.record_publish_gate_success(now=T0 + 3600, markers_pending=0)
    eps = json.loads(prc.WEDGE_SUSPECT_HIT_RATE_FILE.read_text())["episodes"]
    assert [e["hit"] for e in eps] == [None]
    assert "not yet measured (1 closed episode(s) emitted no suspect list" in \
        prc.suspect_hit_rate_phrase()


def test_an_unmeasurable_change_set_is_not_a_hit(tmp_path, monkeypatch):
    """FAIL-OPEN proof on the self-measurement: if the landed change set cannot be read, the
    episode is UNMEASURED. A metric that scores itself when it cannot see is the tautology."""
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {})
    _record_red(["FAILED tests/background/test_wedged.py::test_x"])
    _fire(_Sink())
    monkeypatch.setattr(prc, "_paths_changed_since", lambda since, **kw: None)
    prc.record_publish_gate_success(now=T0 + 3600, markers_pending=0)
    eps = json.loads(prc.WEDGE_SUSPECT_HIT_RATE_FILE.read_text())["episodes"]
    assert eps[0]["hit"] is None and eps[0]["unmeasurable"] is True


def test_an_open_episode_is_not_scored(tmp_path, monkeypatch):
    """Markers still queued means the episode has NOT closed (PW2). Scoring there would pad
    the denominator with episodes nobody repaired."""
    _fake_project(tmp_path, monkeypatch)
    _staging(tmp_path, monkeypatch, {})
    _record_red(["FAILED tests/background/test_wedged.py::test_x"])
    _fire(_Sink())
    prc.record_publish_gate_success(now=T0 + 3600, markers_pending=4)
    assert not prc.WEDGE_SUSPECT_HIT_RATE_FILE.exists()


def test_an_unreadable_hit_rate_ledger_reads_as_unmeasured(tmp_path, monkeypatch):
    prc.WEDGE_SUSPECT_HIT_RATE_FILE.write_text("{not json")
    assert prc._load_suspect_hit_rate() == []
    assert "not yet measured" in prc.suspect_hit_rate_phrase()


def test_the_ledger_is_bounded(tmp_path, monkeypatch):
    for i in range(prc.WEDGE_SUSPECT_HIT_RATE_MAX_EPISODES + 7):
        prc._append_suspect_outcome({"closed_at": float(i), "suspects": 1, "hit": True})
    eps = json.loads(prc.WEDGE_SUSPECT_HIT_RATE_FILE.read_text())["episodes"]
    assert len(eps) == prc.WEDGE_SUSPECT_HIT_RATE_MAX_EPISODES
    assert eps[-1]["closed_at"] == float(prc.WEDGE_SUSPECT_HIT_RATE_MAX_EPISODES + 6)
