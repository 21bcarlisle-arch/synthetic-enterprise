"""The defect: the learning loop's measures were named in its design and read nowhere the draw is made,
so an area could keep missing predictions with nothing in front of the seat saying so.

MUTATIONS (each must fire): `>= STOP_MISSES` -> `> STOP_MISSES`; count `missed` instead of
code+reader towards the stop; drop a malformed trailer silently; drop `learning_loop` from
`build_brief`; drop the `_render_learning_loop` call from `_prompt`; read the map's existence
alone (or never) instead of which grades came after it; print STOP for a mapped area; accept `Graded: none` with no reason; let `Restates:` erase a refusal
instead of moving it to `restated`; let `Restates:` clear a sha it does not name; drop the
`refuse_message` line from the commit-msg hook.
"""
import inspect
import os
import subprocess
from pathlib import Path

from background import delivery_seat as seat
from background import learning_loop as loop


def _log(*bodies: str) -> str:
    return "".join(f"\x00{i:07x}\x01{b}\n" for i, b in enumerate(bodies))


def test_the_stop_condition_can_be_met_and_can_be_missed():
    m = loop.measures(maps=_no_maps, log_text=_log(
        "fix one\n\nGraded: level-dd held=5 missed=3 code=2 reader=1",
        "fix two\n\nGraded: closing held=1 missed=4 code=2 reader=0 width=0.4",
    ))
    areas = m["by_area"]
    # The partition first: one area over the line, one under it -- a stop that always fires or
    # never fires fails here before any value is read.
    assert areas["level-dd"]["stop_condition_met"] and not areas["closing"]["stop_condition_met"]
    # Misses from other causes (a multi-change book, the domain) do not count towards the stop.
    assert areas["closing"]["code_or_reader"] == 2 and areas["closing"]["missed"] == 4
    assert areas["level-dd"]["hit_rate"] == 0.625 and areas["closing"]["median_width"] == 0.4


def _no_maps(area):
    return None


def test_a_landed_map_spends_the_stop_and_the_line_counts_the_misses_after_it():
    """The defect: the brief printed "STOP: map the area first" for level-dd and repayment-posting
    with both maps on origin, steering every draw to redo finished work."""
    log = _log("a\n\nGraded: level-dd held=0 missed=1 code=1",
               "b\n\nGraded: level-dd held=0 missed=1 reader=1",
               "c\n\nGraded: level-dd held=2 missed=1 code=1")
    unmapped = loop.measures(log_text=log, maps=_no_maps)["by_area"]["level-dd"]
    # Map landed after all three misses: commits 0-2 are not its descendants.
    mapped = loop.measures(log_text=log, maps=lambda area: {
        "path": "docs/design/LEVEL_DD_AREA_MAP_x.md", "sha": "m", "after": set()})["by_area"]
    # Map landed between them: only commit 0000000 (newest in `_log`'s order) came after it.
    between = loop.measures(log_text=log, maps=lambda area: {
        "path": "p", "sha": "m", "after": {"0000000"}})["by_area"]["level-dd"]
    # The partition first: the same three misses read STOP with no map and not with one.
    assert unmapped["stop_condition_met"] and not mapped["level-dd"]["stop_condition_met"]
    assert mapped["level-dd"]["misses_since_map"] == 0
    assert between["misses_since_map"] == 1 and between["graded_since_map"] == 1
    stop = seat._render_learning_loop(loop.measures(log_text=log, maps=_no_maps))
    landed = seat._render_learning_loop({**loop.measures(log_text=log), "by_area": mapped})
    assert "-- STOP" in stop and "map landed" not in stop
    assert "-- STOP" not in landed and "map landed m; misses since: 0 of 0 graded" in landed


def test_the_live_maps_are_found_by_their_convention():
    # HEAD, not origin/main: the commit gate runs in a scratch tree with no remote refs.
    assert loop.area_map("no-such-area-ever", rev="HEAD") is None
    m = loop.area_map("repayment-posting", rev="HEAD")
    assert m and m["path"].startswith("docs/design/REPAYMENT_POSTING_AREA_MAP") and m["sha"]


def test_regressions_and_cold_reads_are_counted_per_fix_and_per_read():
    m = loop.measures(log_text=_log(
        "a\n\nGraded: level-dd held=1 missed=0 regressed=1",
        "b\n\nGraded: level-dd held=1 missed=0\nCold-read: explore new-classes=3",
    ))
    assert m["regressions_per_fix"] == 0.5 and m["fixes_graded"] == 2
    assert m["escapes_per_cold_read"] == [3]


def test_a_malformed_grade_is_reported_not_dropped():
    m = loop.measures(log_text=_log(
        "a\n\nGraded: level-dd held=two missed=1",
        "b\n\nGraded: level-dd held=1 missed=1 code=1 reader=1",
        "c\n\nCold-read: explore classes=1",
    ))
    assert m["by_area"] == {} and len(m["unparsed"]) == 3


def test_the_measures_are_in_the_brief_and_printed_where_the_seat_draws():
    assert '"learning_loop": learning_loop.measures()' in inspect.getsource(seat.build_brief)
    assert "_render_learning_loop(" in inspect.getsource(seat._prompt)
    empty = seat._render_learning_loop(loop.measures(log_text=""))
    assert "NOTHING GRADED" in empty
    met = seat._render_learning_loop(loop.measures(maps=_no_maps,
        log_text=_log("x\n\nGraded: level-dd held=0 missed=3 code=3")))
    assert "STOP" in met and "NOTHING GRADED" not in met


def test_none_is_no_grade_and_a_restated_refusal_moves_beside_its_restatement():
    """The defect: four landed commits wrote `Graded: none -- ...` or a countless grade, read as
    unparsed for a week, and a commit on origin cannot be amended to answer it."""
    m = loop.measures(maps=_no_maps, log_text=_log(
        "restate\n\nGraded: d48 held=1 missed=1\nRestates: 0000002",
        "nothing graded\n\nGraded: none -- a count, not a prediction",
        "countless\n\nGraded: level-dd -- not yet",
        "also countless\n\nGraded: other -- not yet",
        "bare\n\nGraded: none",
    ))
    # The partition first: one refusal restated, one left unparsed, one `none` refused for no reason.
    assert [r.split()[0] for r in m["restated"]] == ["0000002"]
    assert "restated by 0000000" in m["restated"][0]
    assert sorted(r.split()[0] for r in m["unparsed"]) == ["0000003", "0000004"]
    assert m["by_area"]["d48"]["held"] == 1 and "none" not in m["by_area"]


def _run_the_real_chain(tmp_path, message: str) -> subprocess.CompletedProcess:
    """The repo's own commit-msg hook over `message`, with a scratch GIT_DIR whose index is HEAD's
    tree (nothing staged), borrowing this repo's objects read-only. The other gates in the chain
    have nothing to refuse, so the learning-loop leg is the only one that can say no."""
    common = Path(subprocess.run(["git", "rev-parse", "--path-format=absolute",
                                  "--git-common-dir"], cwd=str(loop.PROJECT_DIR),
                                 capture_output=True, text=True, check=True).stdout.strip())
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(loop.PROJECT_DIR),
                          capture_output=True, text=True, check=True).stdout.strip()
    gitdir = tmp_path / "scratch.git"
    subprocess.run(["git", "init", "-q", "--bare", str(gitdir)], check=True)
    (gitdir / "objects" / "info" / "alternates").write_text(str(common / "objects") + "\n")
    (gitdir / "HEAD").write_text(head + "\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_DIR=str(gitdir), GIT_INDEX_FILE=str(tmp_path / "index"))
    subprocess.run(["git", "read-tree", head], cwd=str(loop.PROJECT_DIR), env=env, check=True)
    msg = tmp_path / "COMMIT_EDITMSG"
    msg.write_text(message, encoding="utf-8")
    return subprocess.run(["sh", "tools/git-hooks/commit-msg", str(msg)],
                          cwd=str(loop.PROJECT_DIR), env=env, capture_output=True, text=True,
                          timeout=300)


def test_the_commit_msg_gate_refuses_a_grade_the_loop_cannot_parse(tmp_path):
    # The partition first, through the real chain: the same message refused and passed by its
    # Graded line alone -- a gate that refuses everything, or nothing, fails one of the two.
    bad = _run_the_real_chain(_mk(tmp_path / "a"), "x\n\nGraded: level-dd -- not yet\n")
    good = _run_the_real_chain(_mk(tmp_path / "b"), "x\n\nGraded: none -- read-only count\n")
    assert bad.returncode == 1 and "[learning-loop] trailer refused" in bad.stderr, bad.stderr
    assert good.returncode == 0, good.stderr
    assert loop.check_message("x\n\nGraded: level-dd held=1 missed=0\n# Graded: bad") == []


def _mk(path: Path) -> Path:
    path.mkdir()
    return path
