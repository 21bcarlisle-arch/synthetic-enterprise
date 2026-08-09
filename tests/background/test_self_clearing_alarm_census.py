"""PW2 -- R15 on the census itself, both ways, plus the vacuity guard.

The fail-open shape for a census is finding NOTHING and reading as clean. A renamed attribute, a
moved scan root, or a regex that quietly stops matching would all produce an empty census that
looks like a healthy tree -- so "the census is non-empty on the LIVE tree" is itself an assertion
here, not an assumption.

  * FIRES  -- the derivation finds the known instance on the live tree, and finds a planted
              self-clearing control in a synthetic tree.
  * SILENT -- it does not tag a control that only reads, only writes, or writes a path no alarm
              reads; and the disposition gate goes RED on an undispositioned hit.
"""
from __future__ import annotations

import json
import textwrap

import pytest

from background import self_clearing_alarm_census as census


@pytest.fixture(scope="module")
def live():
    return census.derive()


# --------------------------------------------------------------- the live tree (vacuity guard)

def test_the_live_census_is_not_vacuous(live):
    """R15 VACUITY GUARD -- the named fail-open shape for this atom. A census that finds nothing
    must be a FAILURE, never a green tick."""
    assert census.census_is_vacuous(live) is None, census.census_is_vacuous(live)


def test_the_live_tree_yields_substantive_writer_and_reader_sets(live):
    """The derivation is an INTERSECTION; if either input set collapses, the intersection is
    empty for a reason that has nothing to do with the tree being clean."""
    assert live["functions_scanned"] > 500
    assert len(live["state_paths"]) > 20
    assert sum(len(p["writers"]) for p in live["state_paths"].values()) > 50
    assert sum(len(p["readers"]) for p in live["state_paths"].values()) > 50


def test_the_known_instance_is_a_hit_with_its_real_writers_and_readers(live):
    """The 2026-08-09 defect must be IN the census. If this ever stops firing, the census has
    gone blind on the one member of the class we know by name."""
    rec = live["state_paths"][".publish_gate_state.json"]
    assert rec["hit"]

    writers = {w["fn"].split("::")[-1] for w in rec["failure_writers"]}
    assert "record_publish_gate_failure" in writers, \
        "the failure path that rewrote the episode clock is not tagged as a failure writer"

    readers = {r["fn"].split("::")[-1] for r in rec["alarm_readers"]}
    assert "_publish_gate_wedge_active" in readers, \
        "the supervisor draw that derives severity from this file is not tagged as an alarm reader"


def test_the_call_graph_closure_is_what_finds_the_instance(live):
    """record_publish_gate_failure contains NO file call at all -- it writes only through
    _write_publish_gate_state. A grep-level analysis would miss it, so this pins the transitive
    closure specifically rather than the outcome it happens to produce."""
    facts = live["state_paths"][".publish_gate_state.json"]
    quals = {w["fn"] for w in facts["failure_writers"]}
    assert any(q.endswith("::record_publish_gate_failure") for q in quals)

    src = (census.PROJECT_DIR / "background" / "process_run_complete.py").read_text()
    body = src.split("def record_publish_gate_failure", 1)[1].split("\ndef ", 1)[0]
    assert "write_text" not in body, \
        "the premise of this test changed: the function now writes the file directly"


def test_every_live_hit_is_dispositioned(live):
    """The teeth. A newly-written control of this shape must land RED, not join the class
    quietly. If this fails, add a row to docs/design/self_clearing_alarm_dispositions.json --
    that is the point, not an obstacle."""
    missing = census.undispositioned(live)
    assert not missing, (
        "undispositioned self-clearing-alarm hits: {}. Disposition each as `real` (and guard the "
        "episode field) or `benign` WITH a reason.".format(", ".join(missing)))


def test_the_publish_gate_is_dispositioned_real_and_guarded():
    disp = census.load_dispositions()
    row = disp[".publish_gate_state.json"]
    assert row["verdict"] == "real" and row["guard"] == "guarded"


# --------------------------------------------------------------- FIRES on a planted control

def _tree(tmp_path, body: str):
    (tmp_path / "background").mkdir(parents=True, exist_ok=True)
    (tmp_path / "background" / "planted.py").write_text(textwrap.dedent(body))
    return census.derive(roots=("background",), project_dir=tmp_path)


def test_fires_on_a_planted_self_clearing_control(tmp_path):
    """The whole class in eight lines: a check whose failure branch rewrites the episode clock
    its own alarm reads."""
    out = _tree(tmp_path, '''
        from pathlib import Path
        STATE = Path("docs/observability/.planted_state.json")

        def record_failure(now):
            state = json.loads(STATE.read_text())
            state["wedge_since"] = now
            STATE.write_text(json.dumps(state))

        def fire_alarm():
            state = json.loads(STATE.read_text())
            send_ntfy("wedged since %s" % state["wedge_since"])
        ''')
    assert ".planted_state.json" in out["hits"]


def test_fires_when_the_write_is_one_hop_through_a_helper(tmp_path):
    """The real instance's shape -- the failure path never touches the file itself."""
    out = _tree(tmp_path, '''
        from pathlib import Path
        STATE = Path("docs/observability/.planted_state.json")

        def _save(state):
            STATE.write_text(json.dumps(state))

        def record_failure(now):
            _save({"wedge_since": now})

        def alarm_severity():
            return json.loads(STATE.read_text())["wedge_since"]
        ''')
    assert ".planted_state.json" in out["hits"]


# --------------------------------------------------------------- SILENT where it should be

def test_silent_when_nothing_reads_the_path_for_an_alarm(tmp_path):
    """A failure that writes state NOBODY derives severity from cannot silence an alarm."""
    out = _tree(tmp_path, '''
        from pathlib import Path
        STATE = Path("docs/observability/.planted_state.json")

        def record_failure(now):
            STATE.write_text(json.dumps({"wedge_since": now}))
        ''')
    assert ".planted_state.json" not in out["hits"]


def test_silent_when_the_alarm_reads_a_path_no_failure_writes(tmp_path):
    """An alarm reading state written only by a SUCCESS path is the .last_tested_hash shape --
    the independence that makes a cross-check worth having, not a defect."""
    out = _tree(tmp_path, '''
        from pathlib import Path
        STATE = Path("docs/observability/.planted_state.json")

        def record_pass(sha):
            STATE.write_text(sha)

        def fire_alarm():
            send_ntfy(STATE.read_text())
        ''')
    assert ".planted_state.json" not in out["hits"]


def test_a_markdown_log_is_not_a_state_path(tmp_path):
    """Append-only logs are excluded by construction: appending cannot shorten an episode."""
    out = _tree(tmp_path, '''
        from pathlib import Path
        LOG = Path("docs/observability/some-log.md")

        def record_failure(msg):
            LOG.write_text(msg)

        def fire_alarm():
            send_ntfy(LOG.read_text())
        ''')
    assert out["hits"] == []


# --------------------------------------------------------------- the gate can actually fail

def test_an_undispositioned_hit_makes_the_gate_red(live):
    """MUTATION on the disposition gate itself: drop the instance's row and the census must go
    RED. A gate that passes on an empty disposition file would be fail-open."""
    disp = {k: v for k, v in census.load_dispositions().items()
            if k != ".publish_gate_state.json"}
    assert ".publish_gate_state.json" in census.undispositioned(live, disp)


def test_a_benign_verdict_without_a_reason_does_not_count(live):
    """'benign' with an empty why is an assertion, not a disposition."""
    disp = dict(census.load_dispositions())
    disp[".publish_gate_state.json"] = {"verdict": "benign", "why": "   "}
    assert ".publish_gate_state.json" in census.undispositioned(live, disp)


def test_a_missing_dispositions_file_fails_toward_work(tmp_path, live):
    """Fail-silent (R15): an unreadable dispositions file must make every hit undispositioned,
    never make the gate green."""
    assert census.load_dispositions(tmp_path / "nope.json") == {}
    assert census.undispositioned(live, {}) == live["hits"]


def test_vacuity_guard_fires_on_each_way_the_derivation_can_go_blind():
    """MUTATION on the vacuity guard. Each of these is a real way the census could silently
    stop working, and each must be reported rather than read as a clean tree."""
    assert census.census_is_vacuous({"functions_scanned": 3, "state_paths": {}, "hits": []})
    assert census.census_is_vacuous(
        {"functions_scanned": 999, "state_paths": {}, "hits": []})
    assert census.census_is_vacuous(
        {"functions_scanned": 999,
         "state_paths": {"a.json": {"writers": [], "readers": ["f"]}}, "hits": []})
    assert census.census_is_vacuous(
        {"functions_scanned": 999,
         "state_paths": {"a.json": {"writers": ["f"], "readers": []}}, "hits": []})
    assert census.census_is_vacuous(
        {"functions_scanned": 999,
         "state_paths": {"a.json": {"writers": ["f"], "readers": ["g"]}}, "hits": []}), \
        "zero hits on a tree known to contain the instance is the fail-open shape"


def test_the_artefact_round_trips(tmp_path, live):
    out = census.write_census(live, tmp_path / "census.json")
    assert json.loads(out.read_text())["hits"] == live["hits"]
