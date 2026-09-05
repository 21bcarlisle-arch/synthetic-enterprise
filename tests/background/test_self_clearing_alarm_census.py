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
    """'benign' with an empty why is an assertion, not a disposition.

    THE `null` LEG WAS MISSING UNTIL 2026-09-05 and the gate really was open on it: `why: null`
    went through `str(row.get("why", ""))`, which yields the string "None" — truthy — so a row
    asserting nothing counted as a disposition. Found by mutation-testing the inverse control
    written the same day, which had inherited the identical slip. A blank string and a JSON null
    are different values and only one of them was ever tested.
    """
    for nothing in ("   ", "", None):
        disp = dict(census.load_dispositions())
        disp[".publish_gate_state.json"] = {"verdict": "benign", "why": nothing}
        assert ".publish_gate_state.json" in census.undispositioned(live, disp), (
            "a benign row whose reason is {!r} was accepted as a disposition".format(nothing))


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


# ------------------------------------------------- THE INVERSE: a row whose HIT has disappeared
#
# `undispositioned()` asks "a hit with no row". Nothing asked the other direction until now, and
# that is the door the class walked out of: on 2026-09-05 the loader sweep took five carriers out
# of the census by routing their reads through a shared loader (the key dies at the parameter
# seam), twelve more had gone the same way in earlier eras, and `--check` exited 0 throughout.
#
# MEASURED, and the measurement is the reason these tests exist rather than a plausible story:
# deriving the PRE-REPAIR module over the tree at `c30738d77` and applying `eroded_dispositions`
# to that census and that commit's own dispositions file, **17 rows fire and `undispositioned()`
# returns []** -- sixteen on the no-readers leg (`run_history.json`, `.harden_cooldown.json`,
# `.ntfy_digest_state.json`, `.supervisor_map_exhausted_state.json`, `retired_paths_served.json`
# and eleven others) and one on the declassification leg. That replay needs a git extract of
# another commit and is recorded in the finding, not run here; what is run here is each leg it
# fired on, injected.


def _synthetic(paths: dict, hits: list) -> dict:
    return {"functions_scanned": 999, "state_paths": paths, "hits": hits}


_ROW = {"verdict": "benign", "why": "a latest-value watermark"}


def test_a_row_whose_path_vanished_from_the_census_is_refused():
    """The derivation lost the path entirely -- a moved root, a renamed constant, a deleted
    module. MUTATION: return [] for an absent path and this fires."""
    out = census.eroded_dispositions(_synthetic({}, []), {"gone.json": _ROW})
    assert len(out) == 1 and out[0].startswith("gone.json")
    assert "no longer resolves the path" in out[0]


def test_a_row_whose_readers_all_disappeared_is_refused():
    """THE SHAPE THAT ACTUALLY HAPPENED. `run_history.json` kept three writers and went to ZERO
    recorded readers when its read moved behind `load_list_prior(RUN_HISTORY_PATH)`, while
    `count_run_history_total` read it on every dashboard build. A row still written by somebody
    and read by nobody is the instrument going blind, not a control being repaired."""
    out = census.eroded_dispositions(
        _synthetic({"run_history.json": {"writers": ["a::f", "a::g", "a::h"], "readers": []}}, []),
        {"run_history.json": _ROW})
    assert len(out) == 1 and "NO READERS" in out[0]
    assert "3 function(s)" in out[0], "the refusal must carry what it DID still see"


def test_a_row_whose_writers_all_disappeared_is_refused():
    """The mirror leg. MUTATION: check only readers and this survives."""
    out = census.eroded_dispositions(
        _synthetic({"s.json": {"writers": [], "readers": ["a::g"]}}, []), {"s.json": _ROW})
    assert len(out) == 1 and "NO WRITERS" in out[0]


def test_a_genuine_repair_is_admitted_ONLY_WHEN_THE_ROW_SAYS_WHY():
    """The leg that stops this control being keyed to today's answer.

    A path still written AND read, but no longer a hit, is what a REAL repair looks like: the
    failure path stopped writing what the alarm reads. Refusing that outright would make the
    census go red exactly when the code became more honest, which is this project's named
    backwards-control shape. So it is admitted -- but only in writing, never silently.

    BOTH DIRECTIONS, because a control that only ever refuses is indistinguishable from one that
    refuses everything.
    """
    paths = _synthetic({"r.json": {"writers": ["a::f"], "readers": ["a::g"]}}, [])
    silent = census.eroded_dispositions(paths, {"r.json": _ROW})
    assert len(silent) == 1 and "does not say why" in silent[0]

    for empty in ("", "   ", None):
        row = dict(_ROW, declassified=empty)
        assert census.eroded_dispositions(paths, {"r.json": row}), (
            "an empty `declassified` is an assertion, not a reason -- {!r} was accepted".format(
                empty))

    spoken = dict(_ROW, declassified="2026-09-05: the write moved behind guard_episode, so the "
                                     "failure path no longer touches the episode clock")
    assert census.eroded_dispositions(paths, {"r.json": spoken}) == [], (
        "a repair that is written down must clear -- otherwise the control goes red when the "
        "code gets better")


def test_the_erosion_check_sees_what_undispositioned_CANNOT():
    """NOT A TAUTOLOGY: on the same census the existing gate is green and this one is red.

    If both controls could only ever agree, the second one is decoration. This is the census as
    it stood at `c30738d77` in miniature -- every hit dispositioned, and the subject set quietly
    a row short."""
    cen = _synthetic({"live.json": {"writers": ["a::f"], "readers": ["a::g"]},
                      "eroded.json": {"writers": ["a::f"], "readers": []}},
                     ["live.json"])
    disp = {"live.json": _ROW, "eroded.json": _ROW}
    assert census.undispositioned(cen, disp) == [], "the OLD gate must be green here"
    assert census.eroded_dispositions(cen, disp), "the NEW gate must be red here"


def test_every_leg_of_the_partition_is_REACHABLE_and_distinct():
    """One control over the whole partition, not a leg per branch.

    A guard that refuses everything passes every test above taken singly, and a guard that refuses
    nothing passes the green ones. This asserts the four refusals fire on the four inputs that
    should produce them, the two green states stay green, and each refusal names its OWN reason --
    a control whose legs all print the same sentence cannot be debugged from its output.
    """
    cen = _synthetic({
        "still_a_hit.json": {"writers": ["a::f"], "readers": ["a::g"]},
        "no_readers.json": {"writers": ["a::f"], "readers": []},
        "no_writers.json": {"writers": [], "readers": ["a::g"]},
        "unexplained.json": {"writers": ["a::f"], "readers": ["a::g"]},
        "declassified.json": {"writers": ["a::f"], "readers": ["a::g"]},
    }, ["still_a_hit.json"])
    disp = {
        "still_a_hit.json": _ROW,
        "vanished.json": _ROW,
        "no_readers.json": _ROW,
        "no_writers.json": _ROW,
        "unexplained.json": _ROW,
        "declassified.json": dict(_ROW, declassified="repaired: the writer is now monotonic"),
    }
    out = census.eroded_dispositions(cen, disp)
    fired = {line.split(" -- ")[0]: line.split(" -- ", 1)[1] for line in out}
    assert set(fired) == {"vanished.json", "no_readers.json", "no_writers.json",
                          "unexplained.json"}, (
        "the partition did not come out whole: {}".format(sorted(fired)))
    assert len(set(fired.values())) == 4, (
        "each leg must name its own reason; got {}".format(sorted(set(fired.values()))))


def test_every_disposition_row_still_has_a_live_subject(live):
    """The live tree. If this fails, either a path has eroded out of the census -- which is the
    finding, not the obstacle -- or a control was genuinely repaired and its row needs
    `declassified` saying so. Never delete the row to make this green without establishing
    which."""
    eroded = census.eroded_dispositions(live)
    assert not eroded, (
        "dispositioned rows whose census hit has disappeared:\n  " + "\n  ".join(eroded))


def test_the_erosion_check_is_WIRED_INTO_the_gate(monkeypatch, capsys):
    """MUTATION-PROVED IS NOT WIRED. The function above can be perfect and never consulted, so
    this drives `main() --check` and asserts the exit code and the banner."""
    monkeypatch.setattr("sys.argv", ["census", "--check"])
    cen = _synthetic({"eroded.json": {"writers": ["a::f"], "readers": []}}, ["live.json"])
    cen["state_paths"]["live.json"] = {"writers": ["a::f"], "readers": ["a::g"]}
    monkeypatch.setattr(census, "derive", lambda *a, **k: cen)
    monkeypatch.setattr(census, "load_dispositions",
                        lambda *a, **k: {"live.json": _ROW, "eroded.json": _ROW})
    assert census.main() == 1
    assert "subject set is shrinking" in capsys.readouterr().out


# ── unasked_loader_rows: the row's ANSWER, not its existence (2026-09-05) ──
#
# The three rungs above guard whether a hit HAS a row (`undispositioned`), whether a `real` row
# names a test (`unguarded_real_hits`), and whether a row still HAS a hit (`eroded_dispositions`).
# None of them guards the row's `loader` field -- the answer to `_scope_of_benign`'s question,
# whether the carrier's loader tells ABSENT from PRESENT-BUT-UNREADABLE.
#
# MEASURED, and it is why these tests exist rather than a plausible story. `c30738d77` annotated
# all 46 rows on 2026-09-05; `9857c0edb` rewrote the file nine hours later from a pre-sweep copy
# and 33 annotations went with it (50 rows, 17 loaders). The merge to origin adopted the rewriting
# side whole -- correctly, it carried a real re-audit -- and diffed its resolution against that
# side's own copy, so the loss was invisible from both sides. `--check` was green at every commit,
# including the one that landed `eroded_dispositions` in the SAME MINUTE as the erosion.

_ANSWERED = {"verdict": "benign", "why": "a latest-value watermark",
             "loader": "ASKED: absent and unreadable both answer {}, and the writer overwrites."}


def _answered_census():
    """One live hit, fully visible to every other rung -- so anything that fires here fires on
    the loader question alone."""
    return _synthetic({"s.json": {"writers": ["a::f"], "readers": ["a::g"]}}, ["s.json"])


def test_a_hit_whose_row_carries_no_loader_is_refused():
    """The property leg. MUTATION: drop the `loader` check and this survives."""
    out = census.unasked_loader_rows(_answered_census(), {"s.json": _ROW})
    assert len(out) == 1 and out[0].startswith("s.json")
    assert "ABSENT from PRESENT-BUT-UNREADABLE" in out[0], (
        "a refusal that does not say what was never asked cannot be checked: {}".format(out))


def test_a_hit_whose_row_carries_a_loader_is_SILENT():
    """The negative leg. A rung that refuses everything passes every refusal test, and this is
    the only assertion that can tell the two apart."""
    assert census.unasked_loader_rows(_answered_census(), {"s.json": _ANSWERED}) == []


def test_the_loader_answer_does_not_fall_open_on_a_JSON_NULL():
    """`str(None)` is "None" and truthy, so a mandatory field checked with `str(row.get(f, ""))`
    accepts a row that answers nothing. That slip was live twice in this module and shipped once;
    it is asserted here on all three empties rather than on the blank string alone."""
    for nothing in ("", "   ", None):
        row = dict(_ANSWERED, loader=nothing)
        assert census.unasked_loader_rows(_answered_census(), {"s.json": row}), (
            "a row whose loader answer is {!r} was accepted as asked".format(nothing))


def test_a_hit_with_NO_ROW_AT_ALL_is_left_to_undispositioned():
    """The partition boundary. Two rungs reporting the same hit reads as two defects, and a hit
    with no row is `undispositioned()`'s refusal. Both directions asserted."""
    cen = _answered_census()
    assert census.unasked_loader_rows(cen, {}) == []
    assert census.undispositioned(cen, {}) == ["s.json"]


def test_the_annotation_check_sees_WHAT_THE_OTHER_THREE_RUNGS_CANNOT():
    """THE EROSION, REPLAYED. A row with a verdict, a reason, a guard and a live hit -- exactly
    what the 33 deleted rows looked like the moment after they were deleted. Every existing rung
    is green on it and only the new one fires. If this test ever passes with the new rung removed,
    the rung is redundant and should go."""
    cen = _answered_census()
    disp = {"s.json": _ROW}
    assert census.undispositioned(cen, disp) == []
    assert census.unguarded_real_hits(cen, disp) == []
    assert census.eroded_dispositions(cen, disp) == []
    assert census.unasked_loader_rows(cen, disp), (
        "the erosion that actually happened is invisible to all four rungs")


def test_every_live_disposition_row_carries_ITS_OWN_loader_answer(live):
    """The live tree. If this fails, either an annotation has been deleted -- which is the
    finding, not the obstacle, and `git log -S` on the row's key will name the commit -- or a new
    hit has landed whose loader nobody has opened. Never add an empty `loader` to make it green."""
    unasked = census.unasked_loader_rows(live)
    assert not unasked, (
        "dispositioned hits whose loader question has no answer:\n  " + "\n  ".join(unasked))


def test_the_annotation_check_is_WIRED_INTO_the_gate(monkeypatch, capsys):
    """MUTATION-PROVED IS NOT WIRED. The function can be perfect and never consulted; this drives
    `main() --check` on a census where NOTHING ELSE is wrong and asserts the exit code and the
    banner. `eroded_dispositions` cannot fire here -- the row's path is a live hit."""
    monkeypatch.setattr("sys.argv", ["census", "--check"])
    cen = _answered_census()
    monkeypatch.setattr(census, "derive", lambda *a, **k: cen)
    monkeypatch.setattr(census, "load_dispositions", lambda *a, **k: {"s.json": _ROW})
    assert census.main() == 1
    out = capsys.readouterr().out
    assert "LOADER QUESTION HAS NEVER BEEN ASKED" in out
    assert "subject set is shrinking" not in out, (
        "the banner must name the rung that fired, or a reader repairs the wrong thing")
