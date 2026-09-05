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
