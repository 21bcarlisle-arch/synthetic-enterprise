#!/usr/bin/env python3
"""R15 proof for the disk governor (director ruling, 2026-08-19).

The ruling named three properties and each is tested as a separate mechanism, because the
failure this replaces was not a missing idea — it was an idea nobody ran. `resource_headroom`
was built on 2026-08-10 after 64 oom-kills and had never executed once: no caller, no unit,
no state file. So the tests that matter most here are the two at the bottom, which assert the
WIRING rather than the logic.

The fail-closed direction is deliberate and asymmetric, and both halves are driven:
  * an unreadable filesystem reads as PRESSURE — a governor that cannot see the disk must
    never certify it healthy;
  * the REAPER is the exception and fails toward KEEPING — it deletes only what it can
    positively identify as this project's own scratch, because a reaper that deletes on
    uncertainty is a worse failure than a full disk.
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from background import disk_headroom as dh


# ---------------------------------------------------------------------------
# Property 2: alarm BEFORE exhaustion
# ---------------------------------------------------------------------------
def test_the_bands_alarm_before_exhaustion_not_at_it():
    """The floor is two publish cycles of warning, not a round number. If this ever drops to
    a few hundred MB the alarm announces the stop instead of predicting it -- the failure the
    RAM governor's own comment names and this one inherited."""
    assert dh.PRESSURE_FLOOR_MB >= 2048
    assert dh.CRITICAL_FLOOR_MB < dh.PRESSURE_FLOOR_MB < dh.RECOVERED_FLOOR_MB
    assert dh.band(dh.PRESSURE_FLOOR_MB + 1) == dh.HEALTHY
    assert dh.band(dh.PRESSURE_FLOOR_MB) == dh.PRESSURE
    assert dh.band(dh.CRITICAL_FLOOR_MB) == dh.CRITICAL


def test_MUTATION_the_hysteresis_gap_stops_a_flapping_alarm():
    """Between the floors, a filesystem that has been in pressure stays in pressure. Without
    this a disk hovering at the boundary alarms every cycle and gets muted."""
    between = (dh.PRESSURE_FLOOR_MB + dh.RECOVERED_FLOOR_MB) // 2
    assert dh.band(between, previous=dh.PRESSURE) == dh.PRESSURE
    assert dh.band(between, previous=dh.HEALTHY) == dh.HEALTHY
    assert dh.band(dh.RECOVERED_FLOOR_MB + 1, previous=dh.PRESSURE) == dh.HEALTHY


def test_MUTATION_FAIL_CLOSED_an_unreadable_filesystem_is_pressure_never_healthy(
        monkeypatch, tmp_path):
    """THE STATE FILE IS REDIRECTED, and it was not until 2026-08-26.

    `observe()` persists its reading, so this test was writing the LIVE
    `docs/observability/.disk_headroom_state.json` -- a test's fixture ("no such filesystem",
    0 MB free, PRESSURE) becoming the machine's record of its own disk. Its neighbour two tests
    down has redirected `STATE_FILE` since the day it was written; this one never did, and
    nothing compared them. Found by `live_ledger_guard` on the day `disk_headroom._save` was
    brought inside it, which is the guard doing exactly its job rather than a new rule.
    """
    monkeypatch.setattr(dh, "STATE_FILE", tmp_path / "state.json")

    def boom(_p):
        raise OSError("no such filesystem")

    monkeypatch.setattr(dh.shutil, "disk_usage", boom)
    reading = dh.observe()
    assert reading["band"] == dh.PRESSURE
    assert reading["free_mb"] == 0


def test_the_alarm_fires_on_transition_only(monkeypatch, tmp_path):
    """R5. An unchanged status is never re-announced, or the signal becomes noise."""
    monkeypatch.setattr(dh, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(dh, "sample", lambda *a, **k: {
        "free_mb": 100, "used_pct": 99.9, "tightest": "/tmp", "paths": {}})
    first = dh.observe()
    assert first["changed"] and first.get("alarm")
    second = dh.observe()
    assert not second["changed"] and "alarm" not in second


# ---------------------------------------------------------------------------
# Property 1: bounded lifetimes
# ---------------------------------------------------------------------------
def test_every_scratch_pattern_names_a_real_creator():
    """The first draft of SCRATCH_PATTERNS was GUESSED and one entry (`head-checkout-*`)
    matched nothing this project has ever made -- a decorative reaper. Every prefix must be
    one the tooling actually produces."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    sources = " ".join(
        (root / f).read_text(encoding="utf-8")
        for f in ("tools/surgical_land.py", "tools/epistemic_wall.py",
                  "background/process_run_complete.py")
    )
    for pattern, _ttl in dh.SCRATCH_PATTERNS:
        stem = pattern.rstrip("*")
        if stem.startswith("pytest-of"):
            continue  # pytest's own, not ours
        assert stem in sources, (
            f"{pattern!r} matches no prefix any module in this repo creates -- a reaper "
            "pattern that matches nothing is decoration"
        )


def test_both_scratch_roots_are_watched_and_reaped():
    """The two biggest producers default to /var/tmp, not /tmp. A governor watching only the
    volume that failed last time is blind to where most scratch lands."""
    watched = {str(p) for p in dh.WATCHED}
    assert "/tmp" in watched and "/var/tmp" in watched
    assert {str(p) for p in dh.REAP_ROOTS} == {"/tmp", "/var/tmp"}


def test_MUTATION_expired_scratch_is_reaped_and_fresh_scratch_is_not(tmp_path):
    old = tmp_path / "wall-head-old"
    new = tmp_path / "wall-head-new"
    for d in (old, new):
        d.mkdir()
        (d / "payload").write_bytes(b"x" * 2048)
    ancient = time.time() - (9 * 3600)
    import os
    os.utime(old, (ancient, ancient))

    victims = {v["path"] for v in dh.reapable(roots=(tmp_path,))}
    assert str(old) in victims
    assert str(new) not in victims

    dh.reap(roots=(tmp_path,))
    assert not old.exists()
    assert new.exists(), "a fresh scratch dir was reaped -- a live gate run would be shot"


def test_MUTATION_an_unrecognised_directory_is_NEVER_reaped(tmp_path):
    """The reaper fails toward KEEPING. Positive identification only: the 80 directories that
    filled the disk had ad-hoc names and a pattern-matching reaper cannot claim them -- which
    is correct, because a reaper that deletes on uncertainty is worse than a full disk."""
    stranger = tmp_path / "someone-elses-important-data"
    stranger.mkdir()
    ancient = time.time() - (99 * 3600)
    import os
    os.utime(stranger, (ancient, ancient))
    assert dh.reapable(roots=(tmp_path,)) == []
    dh.reap(roots=(tmp_path,))
    assert stranger.exists()


def test_a_directory_in_use_is_never_reaped_however_old(tmp_path, monkeypatch):
    victim = tmp_path / "wall-head-busy"
    victim.mkdir()
    ancient = time.time() - (99 * 3600)
    import os
    os.utime(victim, (ancient, ancient))
    monkeypatch.setattr(dh, "in_use_dirs", lambda: {str(victim)})
    assert dh.reapable(roots=(tmp_path,)) == []


# ---------------------------------------------------------------------------
# Property 3: admission
# ---------------------------------------------------------------------------
def test_admission_refuses_below_the_floor(monkeypatch):
    monkeypatch.setattr(dh, "sample", lambda *a, **k: {
        "free_mb": 300, "used_pct": 99.0, "tightest": "/tmp", "paths": {}})
    monkeypatch.setattr(dh, "reap", lambda *a, **k: {"freed_mb": 0, "removed": []})
    ok, why = dh.admit(need_mb=256)
    assert not ok and "REFUSED" in why


def test_admission_reaps_before_refusing(monkeypatch):
    """The space may already be there. Refusing without trying would stop the machine for
    scratch that expired hours ago."""
    state = {"free": 300}
    monkeypatch.setattr(dh, "sample", lambda *a, **k: {
        "free_mb": state["free"], "used_pct": 50.0, "tightest": "/tmp", "paths": {}})

    def fake_reap(*a, **k):
        state["free"] = 9000
        return {"freed_mb": 8700, "removed": [{"path": "/tmp/wall-head-x"}]}

    monkeypatch.setattr(dh, "reap", fake_reap)
    ok, why = dh.admit(need_mb=256)
    assert ok and "after reaping" in why


# ---------------------------------------------------------------------------
# THE WIRING -- the property whose absence caused both outages
# ---------------------------------------------------------------------------
def test_both_governors_are_called_by_a_running_daemon():
    """THE test. `resource_headroom` was built after 64 oom-kills and never ran: no caller, no
    unit, no state file. A governor nobody calls is not a governor. If this fails, someone has
    unwired the housekeeping and the next exhaustion is only a matter of time."""
    import inspect
    from background import background_worker

    src = inspect.getsource(background_worker.main)
    assert "disk_headroom" in src, "the disk governor is not called by the worker loop"
    assert "resource_headroom" in src, (
        "the MEMORY governor is still unwired -- it has never run once since 2026-08-10"
    )


def test_the_governors_cannot_crash_the_worker():
    """A governor that can take the daemon down is a worse outage than the one it prevents."""
    import inspect
    from background import background_worker

    src = inspect.getsource(background_worker.main)
    head = src.split("process_leftover_run_markers")[0]
    assert "try:" in head and "except Exception" in head, (
        "the headroom calls are not wrapped -- a governor fault would kill the worker"
    )


# ---------------------------------------------------------------------------
# Property 1 again, for the population a TYPED LIST cannot reach (2026-08-21).
#
# The reaper was already caught being decorative once, for one pattern. This is the same
# defect one level up: on 2026-08-21 `/tmp` -- a tmpfs, so this is RAM -- held 6.5 GB, of
# which 3,336 MB was 22 abandoned repo copies, and `reapable()` matched exactly ZERO of
# them. Swap hit 100% and the operational-layer signal went persistently red.
#
# R15: each test below is a MUTATION of the named defect, and the suite is only evidence if
# it FIRES on the real historical population and STAYS SILENT on every keep-case.
# ---------------------------------------------------------------------------
def _make_repo_copy(root, name, *, age_h=48.0, with_git=False, missing=()):
    """A directory shaped like a copy of this repository."""
    d = root / name
    for rel in dh.REPO_SIGNATURE:
        if rel in missing:
            continue
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x" * 32, encoding="utf-8")
    if with_git:
        (d / ".git").mkdir(parents=True, exist_ok=True)
    old = time.time() - age_h * 3600
    import os as _os
    _os.utime(d, (old, old))
    return d


#: The ACTUAL directory names reclaimed by hand on 2026-08-21, from the manifest taken
#: before deletion. This is the population the control must not be blind to again.
THE_2026_08_21_POPULATION = (
    "ep6head.2jxu", "ep6p29.Mlgrmx", "ep6probe", "ep6probe.hafg", "ep6probe.wIsSNa",
    "ep6probe2", "ep6tree.qeTc", "g13head", "g13tree", "kn33", "knife3-step46",
    "tmp.BpEsJAINaZ", "tmp.U4B5Vgh6lA", "tmp.Y9qQoOpprj", "tmp.e5w4C6SbKm",
    "tmp.lxEVAbhl1J", "tmp.qH5eonLsbM", "tmp.xhOLZgQY52", "tmp.yayVcplJR5",
    "wouldbe", "wouldbe2", "wtree",
)


def test_the_typed_list_is_blind_to_the_population_that_filled_the_disk(tmp_path):
    """THE NULL CONTROL, and the reason the derived rule exists.

    Runs the OLD name-based rule over the real 2026-08-21 population. If this ever starts
    passing by matching them, the derived rule below is no longer load-bearing and this
    finding has been fixed some other way -- but as written, a name list scores zero."""
    import fnmatch

    matched = [n for n in THE_2026_08_21_POPULATION
               if any(fnmatch.fnmatch(n, pat) for pat, _ttl in dh.SCRATCH_PATTERNS)]
    assert matched == [], (
        "SCRATCH_PATTERNS now matches {} -- if the fix was to enumerate these names, it is the "
        "same defect again: the next lane invents the next name.".format(matched)
    )


def test_the_derived_rule_catches_every_one_of_them(tmp_path):
    """The mutation the control exists to catch: 22 abandoned repo copies, 0 declared names."""
    for name in THE_2026_08_21_POPULATION:
        _make_repo_copy(tmp_path, name)

    found = {Path(v["path"]).name for v in dh.repo_copy_scratch(roots=(tmp_path,))}
    assert found == set(THE_2026_08_21_POPULATION), (
        "the derived reaper missed {}".format(set(THE_2026_08_21_POPULATION) - found)
    )
    assert all(v["kind"] == "repo-copy" for v in dh.repo_copy_scratch(roots=(tmp_path,)))


def test_reapable_surfaces_them_so_reap_actually_frees_the_space(tmp_path):
    """The derived half must reach `reapable()`, not just exist beside it."""
    _make_repo_copy(tmp_path, "wouldbe")
    paths = {Path(v["path"]).name for v in dh.reapable(roots=(tmp_path,))}
    assert "wouldbe" in paths, "repo-copy scratch never reaches the reaper's candidate list"


# --- the KEEP direction: every one of these must stay untouched ------------
def test_a_checkout_with_git_metadata_is_never_reaped(tmp_path):
    """A worktree/clone can hold committed branches or edits that exist nowhere else. This is
    the exclusion that spares every entry in `git worktree list` without shelling out."""
    _make_repo_copy(tmp_path, "ep6-worktree", with_git=True)
    assert dh.repo_copy_scratch(roots=(tmp_path,)) == []


def test_a_directory_that_is_not_a_repo_copy_is_never_reaped(tmp_path):
    """POSITIVE IDENTIFICATION survives: another program's big old tmp dir is not ours."""
    d = tmp_path / "someone-elses-cache"
    (d / "data").mkdir(parents=True)
    (d / "data" / "blob.bin").write_text("x" * 1024, encoding="utf-8")
    import os as _os
    old = time.time() - 400 * 3600
    _os.utime(d, (old, old))
    assert dh.repo_copy_scratch(roots=(tmp_path,)) == []


def test_a_partial_match_is_not_enough(tmp_path):
    """Every signature file must be present -- three of four is not identification."""
    _make_repo_copy(tmp_path, "half", missing=("docs/PROJECT_OVERVIEW.md",))
    assert dh.repo_copy_scratch(roots=(tmp_path,)) == []


def test_scratch_within_its_ttl_is_never_reaped(tmp_path):
    """A probe that is still running is not abandoned."""
    _make_repo_copy(tmp_path, "ep6probe", age_h=1.0)
    assert dh.repo_copy_scratch(roots=(tmp_path,)) == []


def test_a_live_process_protects_its_tree_at_any_age(tmp_path, monkeypatch):
    """A long gate run must never be shot in the back, however old its checkout looks."""
    d = _make_repo_copy(tmp_path, "ep6_land", age_h=999.0)
    monkeypatch.setattr(dh, "in_use_dirs", lambda: {str(d.resolve())})
    assert dh.repo_copy_scratch(roots=(tmp_path,)) == []


def test_a_process_sitting_deep_inside_the_tree_also_protects_it(tmp_path, monkeypatch):
    """cwd is usually a SUBDIRECTORY of the checkout, not its root -- checking only the root
    would reap a tree with a live pytest inside it."""
    d = _make_repo_copy(tmp_path, "ep6_land", age_h=999.0)
    monkeypatch.setattr(dh, "in_use_dirs", lambda: {str((d / "background").resolve())})
    assert dh.repo_copy_scratch(roots=(tmp_path,)) == []


def test_the_project_itself_can_never_be_reaped(tmp_path):
    """A misconfigured root must not point the reaper at the working tree."""
    d = _make_repo_copy(tmp_path, "live-tree", age_h=999.0)
    assert dh.repo_copy_scratch(roots=(tmp_path,), project_dir=d) == []
    # and a root that IS the project's parent still spares the project
    assert all(Path(v["path"]).resolve() != d.resolve()
               for v in dh.repo_copy_scratch(roots=(tmp_path,), project_dir=d))


# --- the WIRING, which is the half that was actually missing ---------------
def test_the_reaper_has_a_production_caller(tmp_path):
    """`reap()` had NO production caller: `admit()` is its only in-module caller and `admit()`
    is called by nothing, so between them the reaper had never executed outside a test while
    `observe()` -- which only narrates -- ran every worker cycle. The 2026-08-19 ruling forbids
    'reliance on anyone noticing'; an alarm whose remedy is a command in its own text IS that
    reliance."""
    import inspect

    src = inspect.getsource(dh.observe)
    assert "reap()" in src, (
        "observe() no longer reaps -- the governor is back to narrating a command at a human"
    )


def test_the_governor_only_reaps_under_pressure(tmp_path, monkeypatch):
    """A healthy box must not walk shared scratch every cycle."""
    calls = []
    monkeypatch.setattr(dh, "reap", lambda *a, **k: calls.append(1) or {"removed": [], "freed_mb": 0})
    monkeypatch.setattr(dh, "sample", lambda *a, **k: {
        "paths": {}, "tightest": "/tmp", "free_mb": dh.RECOVERED_FLOOR_MB + 5000, "used_pct": 10.0})
    monkeypatch.setattr(dh, "_save", lambda payload: None)
    monkeypatch.setattr(dh, "_state", lambda: {"band": dh.HEALTHY})
    monkeypatch.setattr(dh, "stdlib_shadows", lambda *a, **k: [])
    dh.observe()
    assert calls == [], "the governor reaped while healthy"
