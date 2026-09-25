"""The next-step gate, each test named by the defect it exists to catch.

Director console, 2026-09-05: *"When a session names a next step, it becomes work in the queue with
a rank before the session ends. If it isn't worth minting, it wasn't worth saying."*
"""
from __future__ import annotations

from tools import next_step_gate as gate

_OPEN = {"PB4_engagement_separated_from_elasticity", "C29_decisions_stop_being_lookup_tables"}


def test_a_commit_advancing_an_open_atom_without_a_trailer_is_refused():
    """THE DEFECT, exactly as it happened: PB4 landed, its message said the company would need the
    observable to cross the seam, and that sentence was the only place the work existed."""
    msg = (
        "PB4: engagement gains an antecedent\n\n"
        "PB4_engagement_separated_from_elasticity. Making the company able to USE this needs "
        "payment method to reach its observable feed."
    )
    ok, why = gate.verdict(msg, _OPEN)

    assert ok is False
    assert "records no next step" in why


def test_a_trailer_naming_a_queued_atom_passes():
    msg = (
        "PB4_engagement_separated_from_elasticity: the antecedent lands\n\n"
        "NEXT: PB6_the_engagement_observable_crosses_the_seam\n"
    )
    ok, _ = gate.verdict(msg, _OPEN)
    assert ok is True


def test_an_explicit_none_with_a_reason_passes_because_the_escape_is_counted_not_prevented():
    """A reason predicate cannot be written that a person cannot satisfy. Pretending otherwise
    would make this an exhortation wearing a mechanism's clothes, which is this project's own most
    expensive recurring shape. The escape is allowed and LOGGED instead."""
    msg = ("close PB4_engagement_separated_from_elasticity\n\n"
           "NEXT: none -- the atom reaches its target level here and the ceiling re-run is C29's\n")
    ok, _ = gate.verdict(msg, _OPEN)
    assert ok is True


def test_a_bare_none_without_a_reason_is_refused():
    """The other side of that: the escape is deliberate, but it must SAY something, or the count
    it feeds is a count of the word 'none'."""
    ok, why = gate.verdict("advance PB4_engagement_separated_from_elasticity\n\nNEXT: none\n", _OPEN)

    assert ok is False
    assert "none -- <reason>" in why or "neither an atom id" in why


def test_a_trailer_naming_something_unminted_is_refused():
    """THE FAILURE THIS GATE WOULD MOST EASILY HAVE: accepting any text after NEXT:. A trailer
    pointing at something that is not in the queue is still only prose."""
    ok, why = gate.verdict(
        "advance PB4_engagement_separated_from_elasticity\n\nNEXT: wire it into the seam later\n",
        _OPEN,
    )

    assert ok is False
    assert "unminted" in why or "neither an atom id" in why


def test_an_atom_minted_in_the_same_commit_is_accepted_by_shape():
    """Otherwise the gate refuses the exact workflow it exists to produce: the map file is written
    BY the commit being judged, so a successor minted alongside cannot be in the pre-commit map."""
    ok, _ = gate.verdict(
        "advance PB4_engagement_separated_from_elasticity\n\n"
        "NEXT: PB7_a_successor_minted_right_here\n",
        _OPEN,
    )
    assert ok is True


def test_a_commit_naming_no_open_atom_is_left_alone():
    """REACHABILITY OF THE QUIET BRANCH. Most commits in this tree touch no atom, and a gate that
    demanded a trailer from all of them would teach every lane to type `none` reflexively --
    which would destroy the escape count's meaning as surely as removing the count."""
    ok, why = gate.verdict("fix a typo in the publisher's log line\n", _OPEN)

    assert ok is True
    assert "nothing to follow" in why


def test_a_closed_atom_does_not_demand_a_successor():
    """`open_atom_ids` excludes atoms already at target: "what comes next" is a question about
    unfinished work. Asserted through the real reader so the exclusion cannot silently invert."""
    atoms = [
        {"id": "A_done_atom_here", "level_current": 3, "level_target": 3},
        {"id": "B_open_atom_here", "level_current": 0, "level_target": 3},
    ]
    import tools.maturity_map_store as store

    original = store.load_live_atoms
    try:
        store.load_live_atoms = lambda *a, **k: atoms  # type: ignore[assignment]
        got = gate.open_atom_ids()
    finally:
        store.load_live_atoms = original  # type: ignore[assignment]

    assert got == {"B_open_atom_here"}


def test_an_unreadable_map_does_not_wedge_every_lane(tmp_path, monkeypatch, capsys):
    """FAIL-OPEN, DELIBERATELY, and asserted because it is the arguable direction.

    This runs on every commit in a tree several lanes write at once. One commit without a trailer
    is recoverable; a gate that wedges all of them on a parse error is the thing that eats days.
    """
    def boom():
        raise RuntimeError("map unreadable")
    monkeypatch.setattr(gate, "open_atom_ids", boom)
    msg = tmp_path / "COMMIT_EDITMSG"
    msg.write_text("advance PB4_engagement_separated_from_elasticity\n")

    assert gate.main(["next_step_gate.py", str(msg)]) == 0
    assert "not blocking" in capsys.readouterr().err


def test_the_escape_count_comes_from_the_commit_record_not_a_store(tmp_path):
    """THE DEFECT THE FIRST VERSION SHIPPED WITH, and it made the measurement flattering.

    Escapes were appended to `docs/observability/next_step_escapes.jsonl` under `PROJECT` --
    `Path(__file__).parent.parent`. The sanctioned landing move runs the hook chain inside a
    `tempfile.mkdtemp(prefix="surgical-land-")` extract which is `rmtree`'d afterwards, so every
    escape from every properly-landed commit was written into a directory that then ceased to
    exist. The file was never tracked. The register read "one escape, ever" -- a number produced
    by counting nothing, and one that reads as "escapes are rare".

    Driven against a real repo whose commits were made in the ordinary way: the point is that the
    count's subject is the durable record, so where the hook happened to run cannot lose it.
    """
    import subprocess

    repo = tmp_path / "r"
    repo.mkdir()
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(("git", "init", "-q", "-b", "main", "."), cwd=repo, check=True, env=env)
    for i, msg in enumerate((
        "advance a thing\n\nNEXT: PB9_a_real_successor_here\n",
        "close another\n\nNEXT: none -- the atom reaches target and nothing follows\n",
        "an ordinary commit naming no atom and carrying no trailer\n",
    )):
        (repo / f"f{i}").write_text(str(i))
        subprocess.run(("git", "add", "-A"), cwd=repo, check=True, env=env)
        subprocess.run(("git", "commit", "-q", "-m", msg), cwd=repo, check=True, env=env)

    original = gate.PROJECT
    try:
        gate.PROJECT = repo
        got = gate.escape_rate(window=50)
    finally:
        gate.PROJECT = original

    assert got["declared"] == 2, "the untrailered commit must not be counted as declaring one"
    assert got["escaped"] == 1
    assert got["rate"] == 0.5
    assert got["reasons"] == ["the atom reaches target and nothing follows"]


def test_the_gate_fires_when_run_THE_WAY_THE_HOOK_RUNS_IT(tmp_path):
    """THE DEFECT THIS SHIPPED WITH FOR ONE WIRING, and the one every other test here missed.

    `tools/git-hooks/commit-msg` runs `python3 tools/next_step_gate.py`, as a SCRIPT -- so the repo
    root is not on `sys.path`, `from tools import maturity_map_store` raises ModuleNotFoundError,
    and this gate's own fail-open branch swallowed it on every commit. Nine controls were green and
    the thing was dead in production, because they all import the module and pytest has already
    fixed the path.

    So this one shells out exactly as the hook does. It is the only test here that can fail for
    that reason.
    """
    import subprocess
    import sys as _sys

    from tools.next_step_gate import PROJECT, open_atom_ids

    open_ids = open_atom_ids()
    assert open_ids, "no open atoms: this control would be vacuous"
    msg = tmp_path / "COMMIT_EDITMSG"
    msg.write_text(f"advance {sorted(open_ids)[0]}\n\nno trailer here\n")

    done = subprocess.run(
        [_sys.executable, "tools/next_step_gate.py", str(msg)],
        cwd=str(PROJECT), capture_output=True, text=True, timeout=120,
    )

    assert done.returncode == 1, (
        f"the gate must REFUSE when run as the hook runs it; got {done.returncode} "
        f"with stderr {done.stderr!r}"
    )
    assert "not blocking" not in done.stderr, (
        "the gate fell through its fail-open branch -- it cannot import its own dependency"
    )

def test_an_atom_named_BY_NUMBER_engages_the_gate():
    """THE DEFECT THAT MADE THIS GATE SILENT FOR FIVE INSTANCES OF ITS OWN SUBJECT.

    Nobody writes `W2_18_the_housing_joint_the_sample_and_the_ceiling` in a subject line; they
    write "W2_18 stage 1". Measured over the 17 commits that carried a NEXT trailer, only FOUR
    named an atom by full id -- so `named` came back empty, `verdict` took its "nothing to follow"
    branch, and the trailer was never examined. Seventeen compliant-looking commits, an empty
    queue, and the director reporting the same failure five times with a different explanation
    each time.
    """
    known = {"W2_18_the_housing_joint_the_sample_and_the_ceiling"}
    ok, why = gate.verdict("W2_18 stage 1: measure the draw before extending it\n", known)

    assert ok is False
    assert "records no next step" in why


def test_a_number_that_is_only_part_of_a_longer_token_does_not_match():
    """The false-positive leg. Without a boundary, `W2_1` matches `W2_18` and every commit
    mentioning one atom engages the gate for another."""
    known = {"W2_1_archetype_layers"}

    assert gate.atoms_named_in("work on W2_18 today", known) == set()
    assert gate.atoms_named_in("work on W2_1 today", known) == known


def test_AN_ATOM_CANNOT_BE_ITS_OWN_SUCCESSOR():
    """THE SECOND HALF, and it is what makes the first half worth having.

    Four of six trailers this seat wrote named `W2_18` -- the atom the commit was already inside.
    A ruling-sized atom is not a queue unit: "the housing joint, the sample and the ceiling" is a
    programme, so a bounded tick reading it has no first move and draws the machinery in front of
    it instead. Naming it as your own successor is true and puts nothing in the queue.
    """
    known = {"W2_18_the_housing_joint_the_sample_and_the_ceiling"}
    msg = ("W2_18 stage 1: measure the draw\n\n"
           "NEXT: W2_18_the_housing_joint_the_sample_and_the_ceiling\n")
    ok, why = gate.verdict(msg, known)

    assert ok is False
    assert "already working on" in why


def test_a_DIFFERENT_atom_is_a_real_successor_and_passes():
    """The negative leg: without it, a gate that refused every trailer would satisfy the test
    above while making the mechanism unusable."""
    known = {"W2_18_the_housing_joint_the_sample_and_the_ceiling",
             "W2_20_mains_gas_is_drawn_not_inferred_from_the_heating_system"}
    msg = ("W2_18 stage 1: measure the draw\n\n"
           "NEXT: W2_20_mains_gas_is_drawn_not_inferred_from_the_heating_system\n")

    assert gate.verdict(msg, known)[0] is True


def test_the_successor_on_the_trailer_does_not_count_as_the_commits_own_subject():
    """The trap the self-succession refusal walks into if `named` is read off the whole message:
    the successor names itself on the NEXT line, so every correct trailer reads as
    self-succession. The trailers are stripped before the subject is computed."""
    known = {"W2_20_mains_gas_is_drawn_not_inferred_from_the_heating_system"}
    msg = "an ordinary machinery commit\n\nNEXT: W2_20_mains_gas_is_drawn_not_inferred_from_the_heating_system\n"

    assert gate.verdict(msg, known)[0] is True


# ── The SECOND trigger: the map diff, not the prose (2026-09-25) ─────────────────────────────
# Measured over the last 200 first-parent commits: 110 atoms open, 100 distinct number forms, and
# exactly ONE message naming any of them. The gate refused 1 commit in 200 and was unasked on the
# other 199. These control the leg that asks the MAP instead.

_MAP_BEFORE = """\
- id: PB4_engagement_separated_from_elasticity
  level_current: 0
  level_target: 3
- id: C29_decisions_stop_being_lookup_tables
  level_current: 2   # L0->L2 2026-09-17, recorded in gate_authorizations.jsonl
  level_target: 3
"""


def _map_with(**levels):
    """The same two atoms with the levels named, so a control states only what it varies."""
    text = _MAP_BEFORE
    for atom, (old, new) in levels.items():
        text = text.replace(
            f"- id: {atom}\n  level_current: {old}", f"- id: {atom}\n  level_current: {new}"
        )
    return text


def test_a_commit_whose_MAP_DIFF_moves_a_level_is_asked_even_when_the_prose_names_nothing():
    """THE DEFECT THIS LEG EXISTS FOR, and it is the 199-in-200 case.

    The message leg asks its question of the author's ACCOUNT of the commit. This asks the
    project's RECORD of it. A commit that moves an atom from 0 to 1 while its subject line says
    "stage 1 of the housing joint" names no id, reaches the naming leg's quiet branch, and was
    asked for nothing by anything -- `level_promotion_gate` records the move and does not ask for a
    successor.
    """
    moved = gate.atoms_whose_level_moved(
        _MAP_BEFORE, _map_with(PB4_engagement_separated_from_elasticity=(0, 1))
    )
    assert moved == {"PB4_engagement_separated_from_elasticity": (0, 1)}

    ok, why = gate.verdict("stage 1 of the housing joint, measured\n", _OPEN, moved)

    assert ok is False
    assert "THE MAP SAYS SO" in why, "the refusal must name WHICH leg refused: see the next control"
    assert "0 -> 1" in why


def test_a_comment_rewritten_on_a_level_line_is_NOT_a_move():
    """THE FALSE POSITIVE A LINE-KEYED TRIGGER WOULD PRODUCE, and it is in the real record.

    `2cc924ed9` rewrote the trailing comment on `level_current: 2` and left it at 2. A diff keyed
    to lines containing `level_current` counts 32 of the last 120 map commits; parsing the VALUE
    counts 31, and this is the one. A bookkeeping edit must not be asked for a successor.
    """
    after = _MAP_BEFORE.replace("recorded in gate_authorizations.jsonl", "HELD AT 2 by its lane")
    assert after != _MAP_BEFORE, "this control is vacuous unless the text actually changed"

    assert gate.atoms_whose_level_moved(_MAP_BEFORE, after) == {}
    assert gate.verdict("chore: tidy a note on the map\n", _OPEN, {})[0] is True


def test_a_level_WITHDRAWN_is_a_move_too():
    """REACHABILITY OF A BRANCH HISTORY CANNOT EXERCISE, which makes this control its only witness.

    Nothing in the last 120 map commits moves a level DOWN, so keying this trigger to
    `level_promotion_gate.level_increases` would have looked identical on every commit that has
    ever been made and been silent by construction on the case that matters most -- a claim
    withdrawn is exactly when a reader needs to know what follows. Keyed to the PROPERTY (the value
    changed), not to today's answer (every move so far has been upward).
    """
    down = gate.atoms_whose_level_moved(
        _MAP_BEFORE, _map_with(C29_decisions_stop_being_lookup_tables=(2, 0))
    )

    assert down == {"C29_decisions_stop_being_lookup_tables": (2, 0)}
    assert gate.verdict("withdraw the level\n", _OPEN, down)[0] is False


def test_BOTH_DIRECTIONS_are_reachable_through_one_control():
    """One control over the whole partition rather than a leg per branch.

    A mover that returned `{}` for everything passes every negative arm above, and a mover that
    returned every atom passes every positive one. This is the shape that catches both: up, down
    and unchanged must be three distinct answers from the same function.
    """
    up = gate.atoms_whose_level_moved(
        _MAP_BEFORE, _map_with(PB4_engagement_separated_from_elasticity=(0, 3))
    )
    down = gate.atoms_whose_level_moved(
        _MAP_BEFORE, _map_with(C29_decisions_stop_being_lookup_tables=(2, 1))
    )
    still = gate.atoms_whose_level_moved(_MAP_BEFORE, _MAP_BEFORE)

    assert up and down and not still
    assert up != down


def test_an_atom_MINTED_by_this_commit_has_not_moved():
    """Minting an atom is not advancing it, and neither is deleting one.

    The trap underneath is the one `_whole_map` exists for: an atom refiled from the live half to
    the closed half is ABSENT from one file and present in the other, so a mover reading one half
    would report every closure as a deletion and every arrival as a mint. The caller reads both
    halves concatenated; this pins the rule the mover itself must hold either way.
    """
    minted = _MAP_BEFORE + "- id: H99_a_brand_new_atom\n  level_current: 0\n  level_target: 2\n"

    assert gate.atoms_whose_level_moved(_MAP_BEFORE, minted) == {}
    assert gate.atoms_whose_level_moved(minted, _MAP_BEFORE) == {}


def test_a_map_move_STILL_cannot_name_itself_as_its_own_successor():
    """The self-succession refusal guards the map leg too, and that is not automatic.

    It was keyed to `named` -- the atoms the MESSAGE names. An atom whose level moved but whose id
    appears nowhere in the prose was not in that set, so `NEXT: <itself>` would have satisfied the
    gate on exactly the commits this leg was added to catch, and put nothing in the queue.
    """
    atom = "PB4_engagement_separated_from_elasticity"
    moved = {atom: (0, 1)}

    ok, why = gate.verdict(f"stage 1 of the joint\n\nNEXT: {atom}\n", _OPEN, moved)

    assert ok is False
    assert "cannot be its own successor" in why


def test_a_map_move_is_satisfied_by_a_DIFFERENT_successor():
    """The anti-tautology arm for the four controls above: this leg must be SATISFIABLE.

    A trigger that refused whatever trailer was offered would pass every refusal control here, and
    the evidence for it would read exactly like the mechanism working.
    """
    moved = {"PB4_engagement_separated_from_elasticity": (0, 1)}
    msg = "stage 1 of the joint\n\nNEXT: C29_decisions_stop_being_lookup_tables\n"

    assert gate.verdict(msg, _OPEN, moved)[0] is True
    assert gate.verdict("stage 1\n\nNEXT: none -- the joint is closed here\n", _OPEN, moved)[0] \
        is True


def test_the_two_legs_give_DISTINGUISHABLE_refusals():
    """Without this, a mutation disabling one leg is caught by the other and read as proof the
    disabled leg works -- the flattering reading of a green mutation, and this project's most
    repeated control defect. The map leg and the message leg must be told apart from the text."""
    atom = "PB4_engagement_separated_from_elasticity"

    _, map_only = gate.verdict("prose naming nothing\n", _OPEN, {atom: (0, 1)})
    _, msg_only = gate.verdict(f"advance {atom}\n", _OPEN, {})

    assert "THE MAP SAYS SO" in map_only and "The message names" not in map_only
    assert "The message names" in msg_only and "THE MAP SAYS SO" not in msg_only


def test_the_MAP_LEG_FIRES_WHEN_RUN_THE_WAY_THE_HOOK_RUNS_IT(tmp_path):
    """THE ONLY CONTROL HERE THAT CAN CATCH THE DEFECT THIS GATE ALREADY SHIPPED ONCE.

    Every control above drives `verdict` with a dict a test built. None of them can tell you
    whether `staged_level_moves()` reads the real index, whether the new imports survive being run
    as a SCRIPT (the repo root is not on `sys.path` when the hook runs it), or whether the gate
    falls through its fail-open branch. This gate was dead in production for one wiring for exactly
    that reason, with nine green controls.

    The staged map is built in a THROWAWAY `GIT_INDEX_FILE`, so the caller's index is never opened
    -- this tree has other lanes' work staged in it.
    """
    import os
    import re as _re
    import subprocess
    import sys as _sys
    import tempfile

    from tools.next_step_gate import PROJECT

    head_map = subprocess.run(
        ["git", "show", "HEAD:docs/design/maturity_map.yaml"],
        cwd=str(PROJECT), capture_output=True, text=True, timeout=60,
    )
    if head_map.returncode != 0:
        import pytest
        pytest.skip("no map at HEAD in this checkout")
    moved_text, subs = _re.subn(r"level_current: 0", "level_current: 1", head_map.stdout, count=1)
    assert subs == 1, "no atom at level 0 to move: this control would be vacuous"

    fd, index = tempfile.mkstemp(prefix="test-next-step-idx-")
    os.close(fd)
    os.unlink(index)
    env = dict(os.environ, GIT_INDEX_FILE=index)
    try:
        subprocess.run(["git", "read-tree", "HEAD"], cwd=str(PROJECT), env=env, check=True,
                       capture_output=True, timeout=60)
        blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=str(PROJECT),
                              input=moved_text, capture_output=True, text=True, timeout=60)
        subprocess.run(
            ["git", "update-index", "--cacheinfo",
             f"100644,{blob.stdout.strip()},docs/design/maturity_map.yaml"],
            cwd=str(PROJECT), env=env, check=True, capture_output=True, timeout=60,
        )
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text("chore: prose that names no atom at all\n")
        done = subprocess.run(
            [_sys.executable, "tools/next_step_gate.py", str(msg)],
            cwd=str(PROJECT), env=env, capture_output=True, text=True, timeout=180,
        )
    finally:
        if os.path.exists(index):
            os.unlink(index)

    assert "not blocking" not in done.stderr and "asking the message only" not in done.stderr, (
        f"the gate fell through a fail-open branch: {done.stderr!r}"
    )
    assert done.returncode == 1, (
        f"a staged level move must REFUSE when run as the hook runs it; got {done.returncode} "
        f"with stderr {done.stderr!r}"
    )
    assert "THE MAP SAYS SO" in done.stderr


def test_a_commit_that_does_not_stage_the_map_asks_the_index_for_NOTHING(tmp_path):
    """REACHABILITY OF THE QUIET BRANCH ON THE REAL INDEX, and the cost leg underneath it.

    `:<path>` resolves from the index, which holds EVERY tracked file -- so `_whole_map(":")`
    returns both halves of a 300KB map on every commit in the tree whether or not the commit
    touches it. The gate asks what is STAGED first and stops there.

    THE SECOND ASSERTION IS THE ONE THAT MATTERS AND IT WAS ADDED AFTER A GREEN MUTATION. With the
    first assertion alone, replacing `_map_is_staged` with `return True` left all 26 controls green:
    this worktree's index equals HEAD, so the map is read twice, compared, and found unchanged --
    the right answer by the wrong route. That is a missing control rather than an equivalence, and
    the evidence it is not an equivalence is the clock: the suite went from 1.18s to 2.29s on the
    mutation, which is the two YAML parses it would add to EVERY commit of EVERY lane. So the
    control is keyed to the predicate itself, which a mutation cannot leave standing.
    """
    assert gate.staged_level_moves() == {}, (
        "this worktree stages no map, so the gate must report no move"
    )
    assert gate._map_is_staged() is False, (
        "the map is not staged here, so the gate must not go to the index for it at all"
    )
