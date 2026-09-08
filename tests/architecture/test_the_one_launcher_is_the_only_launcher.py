"""The launch-shape census is able to fire, and the floor it holds is the real tree's.

THE DEFECT THESE CONTROL. `background/launch_long_job.py` is the one route a long job is launched,
and until `tools/launch_shape_census.py` existed that was a CONVENTION living in three call sites.
A new module with `subprocess.Popen(..., start_new_session=True)`, or a fresh `systemd-run` argv
typed into a script, would pass every gate in this repository and die at the next cgroup teardown —
which is how five launches of one measurement produced four deaths.

THE POISON ROUND COMES FIRST, and the order is the point. "The floor holds" means two opposite
things: the tree has no new launch site, or the detector cannot see one. A census whose regex has
gone blind reports a clean tree and every mutation of it survives. So the first test builds a tree
containing every shape and asserts each one is SEEN, before any test asserts that the real tree is
clean.

ONE CONTROL OVER THE WHOLE PARTITION, not a leg per shape. A detector that fires on nothing passes
a per-shape test suite that only ever asks "does it stay quiet on clean input". `test_the_poison_
tree_fires_every_shape` asserts the set of shapes found EQUALS `ALL_SHAPES`, so a shape that is
added to the enum and never wired to a detector fails here rather than being silently unguarded.
"""
from __future__ import annotations

import ast
import functools
import subprocess
from pathlib import Path

import pytest

from tools import launch_shape_census as census

REPO = Path(__file__).resolve().parents[2]


@functools.lru_cache(maxsize=1)
def _real_tree() -> tuple:
    """The real tree's census, walked ONCE per session.

    This file is on `pre_commit_test_gate.CONTROL_TESTS`, so it is paid on every code commit.
    Three tests need the walk; the cache means they share one. Since the prefilter landed the walk
    is ~0.1s and the cache saves little — kept because it costs nothing and the next test to want
    the real tree should not have to think about it.
    """
    return tuple(census.census(REPO))


def _poison_tree(tmp_path: Path) -> Path:
    """A git repo holding one of each launch shape, plus the two things the census must NOT flag.

    A real `git init` and not a fixture list: the census derives its population from `git ls-files`,
    so a fixture that handed it paths directly would leave the derivation — the part that can
    silently return nothing — untested.
    """
    (tmp_path / "mod_detach.py").write_text(
        "import subprocess\n"
        "subprocess.Popen(['sleep', '1'], start_new_session=True)\n",
        encoding="utf-8")
    (tmp_path / "mod_unit.py").write_text(
        "import subprocess\n"
        "subprocess.run(['systemd-run', '--user', '--unit=x', 'sleep', '1'])\n",
        encoding="utf-8")
    (tmp_path / "mod_shell_string.py").write_text(
        'CMD = "systemd-run --user --unit=y python3 -m tools.x"\n',
        encoding="utf-8")
    (tmp_path / "job.sh").write_text(
        "#!/usr/bin/env bash\n"
        "nohup python3 -m tools.x >log 2>&1 &\n",
        encoding="utf-8")
    (tmp_path / "setsid_job.sh").write_text(
        "#!/usr/bin/env bash\n"
        "setsid python3 -m tools.y\n",
        encoding="utf-8")
    # The two shapes that must stay quiet, carried in the SAME tree as the poison so a detector
    # that fires on everything fails here rather than looking maximally safe.
    (tmp_path / "innocent_prose.py").write_text(
        '"""Launched by hand:\n\n'
        "    systemd-run --user --unit=arms-rerun tools/run_arms_rerun_detached.sh\n\n"
        'That died because setsid does not escape a cgroup.\n"""\n'
        'REASON = "systemd-run unavailable"\n',
        encoding="utf-8")
    (tmp_path / "innocent_shell.sh").write_text(
        "#!/usr/bin/env bash\n"
        "# setsid does not escape a cgroup, and nohup is no better -- see the launcher.\n"
        "python3 -m tools.x >>log 2>&1\n"
        "if [ -f a ] && [ -f b ]; then echo both; fi\n",
        encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return tmp_path


def test_the_poison_tree_fires_every_shape(tmp_path):
    """Fires on: a detector that has gone blind, and on a shape declared in `ALL_SHAPES` that no
    detector implements. Either one makes the real-tree floor below vacuously green."""
    found = census.census(_poison_tree(tmp_path))
    shapes = {s.shape for s in found}
    assert shapes == set(census.ALL_SHAPES), (
        f"the census saw {sorted(shapes)} in a tree built to contain every shape; "
        f"{sorted(set(census.ALL_SHAPES) - shapes)} is undetectable, so a clean report from it "
        f"says nothing about that shape"
    )


def test_the_poison_tree_refuses_and_names_each_new_site(tmp_path):
    """Fires on: a census that SEES a launch site and does not refuse it. Detection and refusal
    are different failures — an earlier draft of the comparison read a brand-new site as a growth
    of a floor row that was not there, and printed a message naming a floor of 0."""
    found = census.census(_poison_tree(tmp_path))
    problems = census.refusals(found, floor={})
    assert problems, "an empty floor and five launch sites produced no refusal"
    assert all("NEW LAUNCH SITE" in p for p in problems), problems
    for expected in ("mod_detach.py", "mod_unit.py", "mod_shell_string.py", "job.sh",
                     "setsid_job.sh"):
        assert any(expected in p for p in problems), f"{expected} was seen but not refused"


def test_all_three_verdicts_are_reachable():
    """Fires on: a verdict branch that cannot be taken. ONE control over the whole partition.

    THIS TEST EXISTS BECAUSE A MUTATION SURVIVED. Replacing the `now < allowed` branch with
    `elif False:` left the suite fully green — the real tree matches its floor exactly, so no row
    is ever unmet and the branch is unreachable from the tree alone. That branch is the one that
    catches a detector going blind, which is the failure this whole file is built around, and it
    was the one thing nothing could test.

    Asserted as a partition rather than a leg apiece on purpose: three separate tests each pass
    against a `refusals` that returns a fixed non-empty list for any input, whereas the set
    equality below does not.
    """
    sighting = census.Sighting("a.py", 1, census.DETACHED_SESSION, "probe")
    reason = ("a floor reason long enough to satisfy the row-states-its-reason control, which is "
              "checked separately and is not what this test is about at all, so it runs on.")
    verdicts = {
        "new site": census.refusals([sighting], floor={}),
        "grew": census.refusals(
            [sighting, census.Sighting("a.py", 9, census.DETACHED_SESSION, "probe")],
            floor={("a.py", census.DETACHED_SESSION): (1, reason)}),
        "unmet": census.refusals(
            [], floor={("a.py", census.DETACHED_SESSION): (1, reason)}),
    }
    unreachable = [name for name, out in verdicts.items() if not out]
    assert not unreachable, f"these verdicts cannot be reached at all: {unreachable}"
    assert "NEW LAUNCH SITE" in verdicts["new site"][0]
    assert "LAUNCH SITE GREW" in verdicts["grew"][0]
    assert "FLOOR ROW UNMET" in verdicts["unmet"][0]
    # And the quiet case is genuinely quiet, or the three above prove nothing.
    assert not census.refusals([sighting],
                               floor={("a.py", census.DETACHED_SESSION): (1, reason)})


def test_prose_about_the_defect_is_not_counted_as_the_defect(tmp_path):
    """Fires on: the substring draft of the detector, which is not hypothetical — it was the first
    one written here, and over the real tree it returned 20 sightings against a hand-counted 8.
    All twelve extras were `reason=`/log strings NAMING the tool. In a repository whose modules are
    largely prose about this exact defect, a census that counts the word measures the history."""
    found = census.census(_poison_tree(tmp_path))
    innocent = [s for s in found if s.path in ("innocent_prose.py", "innocent_shell.sh")]
    assert not innocent, (
        f"prose describing the defect was counted as the defect: {[str(s) for s in innocent]} — "
        f"a census that flags the warning against a hazard is one the next reader silences"
    )


def test_the_prefilter_is_equivalent_to_parsing_everything():
    """Fires on: a prefilter that has become a blind spot.

    `_census_python` skips the AST parse for a file containing neither literal — a 50x speedup
    that is the difference between this being the most expensive entry in the pre-commit gate and
    the cheapest. The argument for equivalence is sound (a keyword argument must be spelled; a
    string constant must contain its own characters) but an argument is not a control, and a
    future detector added to `_census_python` could easily fire on something the prefilter drops.
    So: run the real tree BOTH ways and require identical output.
    """
    prefiltered = list(_real_tree())
    unfiltered = []
    for path in census._tracked(REPO, "*.py"):
        if path == census.THE_LAUNCHER or path in census._BLIND_TO:
            continue
        text = (REPO / path).read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        prose = census._docstring_nodes(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == "start_new_session":
                        unfiltered.append((path, node.lineno, census.DETACHED_SESSION))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if id(node) not in prose and census._is_a_transient_unit_launch(node.value):
                    unfiltered.append((path, node.lineno, census.RAW_TRANSIENT_UNIT))
    seen = sorted((s.path, s.line, s.shape) for s in prefiltered
                  if s.shape != census.SHELL_BACKGROUND)
    assert seen == sorted(unfiltered), (
        "the prefilter changed what the census sees; it is a blind spot, not an optimisation"
    )


def test_the_census_population_is_not_empty(tmp_path):
    """Fires on: a `git ls-files` that returns nothing (wrong cwd, a worktree extract, a rename of
    the census module). Every other assertion about the real tree lives downstream of this
    derivation, so an empty population would make all of them pass while measuring nothing."""
    assert len(census._tracked(REPO, "*.py")) > 500, "the python population collapsed"
    assert len(census._tracked(REPO, "*.sh")) >= 9, "the shell population collapsed"


def test_the_real_tree_holds_the_floor():
    """Fires on: a new committed launch site, an existing one multiplying, and a floor row whose
    site vanished without the floor shrinking in the same commit."""
    problems = census.refusals(list(_real_tree()))
    assert not problems, "\n".join(problems)


def test_the_launcher_is_excluded_and_nothing_else_quietly_joins_it():
    """Fires on: an exclusion set grown to silence a refusal.

    The census cannot read the two files that hold its own trigger strings, and that blindness is
    a real cost — a launch written inside either one is invisible. Pinning the set here is what
    stops the cheapest way past this control being 'add your file to `_BLIND_TO`'."""
    assert census.THE_LAUNCHER == "background/launch_long_job.py"
    assert set(census._BLIND_TO) == {
        "tools/launch_shape_census.py",
        "tests/architecture/test_the_one_launcher_is_the_only_launcher.py",
    }, "the census stopped reading a file without that being argued for"
    for path in (census.THE_LAUNCHER,) + census._BLIND_TO:
        assert (REPO / path).exists(), f"{path} is excluded by name and does not exist"


def test_every_floor_row_states_why_it_is_not_the_launcher():
    """Fires on: a floor row banked to make the gate green with no argument attached. A frozen
    survivor whose reason is 'legacy' is indistinguishable from an unfixed defect, and this floor
    is small enough that every row can afford a sentence."""
    for key, (count, reason) in census.FLOOR.items():
        assert count > 0, f"{key} is on the floor with a count of zero"
        assert len(reason) > 120, f"{key} has no stated reason, only: {reason!r}"
        assert (REPO / key[0]).exists(), f"floor names {key[0]}, which is not in the tree"


def test_the_tick_stays_a_row_with_a_reason_and_not_an_exemption():
    """Fires on: `worker_tick` being deleted from the census rather than explained.

    It blocks until its child exits, so that child is SUPPOSED to be in the tick's cgroup, and a
    census that calls it a defect gets silenced wholesale. But exempt and invisible differ: as a
    row its count is ratcheted, so a SECOND detach in that file is still a refusal. Dropping it to
    an exclusion would lose that, which is why this is pinned rather than left to judgement."""
    key = ("background/worker_tick.py", census.DETACHED_SESSION)
    assert key in census.FLOOR, "the tick left the floor; if it is exempt it is now unratcheted"
    assert "background/worker_tick.py" not in census._BLIND_TO
    seen = census.tally(list(_real_tree()))
    assert seen.get(key) == 1, (
        "the tick's detach count moved; a second one is not covered by the first one's reason"
    )


@pytest.mark.parametrize("text,is_launch", [
    ("systemd-run", True),
    ("/usr/bin/systemd-run", True),
    ("systemd-run --user --unit=x sleep 1", True),
    ("systemd-run unavailable", False),
    ("systemd-run is the mechanism under test", False),
    ("waiting does not grow a systemd-run", False),
    ("  ! systemd-run unavailable -- REFUSING to time an unbounded suite", False),
])
def test_the_discriminator_separates_using_the_tool_from_naming_it(text, is_launch):
    """Fires on: a widening back to a substring match, or a narrowing to bare equality.

    The False rows are verbatim from `measure_publish_gate_subject_cost` and its test — the exact
    strings the substring draft mistook for launches. The True rows include the pathed spelling,
    because a launch written against an absolute path is still a launch."""
    assert census._is_a_transient_unit_launch(text) is is_launch


@pytest.mark.parametrize("line,flagged", [
    ("nohup python3 -m tools.x &", True),
    ("setsid python3 -m tools.y", True),
    ("python3 -m tools.x >> log 2>&1", False),
    ("if [ -f a ] && [ -f b ]; then echo both; fi", False),
    ('echo "start" >> "$LOG" 2>&1', False),
])
def test_the_shell_pattern_does_not_read_a_redirect_as_a_background(line, flagged):
    """Fires on: a `&` pattern that matches `2>&1` or `&&`.

    Not a hypothetical false positive to be tidy about — every committed shell script here
    redirects both streams, so a pattern that reads `2>&1` as backgrounding would flag all nine,
    and a control that flags everything is deleted rather than fixed."""
    found = census._census_shell(line + "\n", "probe.sh")
    assert bool(found) is flagged, found
