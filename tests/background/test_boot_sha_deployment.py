"""PW1 — "is the code this daemon LOADS stale?" (rebuilt 2026-08-09; was OPS1 sub-step 5 G-D1/G-D3).

The predecessor control had BOTH failure modes the director named in
DIRECTOR_STEER_SECOND_PUBLISH_WEDGE_2026-08-09:
  BLIND      — its population was the manifest's `launched_by` field, so the seven rows the
               2026-07-29 cutover left un-flipped were excluded by DECLARATION. sim-runner and
               background-worker — the two daemons that ran pre-cure code through the 10h publish
               wedge — were among the excluded, and the detector reported clean throughout.
  ALWAYS RED — "has HEAD moved?" is true for every daemon minutes after boot on a repo that commits
               every tick. DECIDED #2: "a detector for that failure mode that is always red will be
               ignored exactly as reliably as one that is blind."

So the two halves are tested separately and NEITHER is sufficient alone:
  (a) POPULATION — observed systemd activity, never a declared field. R15 mutation: empty the
      population / re-derive it from `launched_by` and a NAMED test reds.
  (b) SIGNAL     — the daemon's own import closure, never repo HEAD. R15 mutation: revert to
      HEAD-comparison and a NAMED test reds, because a daemon with an untouched closure must read
      GREEN while HEAD moves.
Plus a VACUITY guard: the honest path must evaluate a NON-EMPTY daemon set on the live box.
"""
from __future__ import annotations

import subprocess

import pytest

from background import boot_sha, code_closure
from background import process_reconciler as R
from background.process_reconciler import (
    drift_population,
    launcher_drift,
    loaded_code_drift,
    observed_launched_by,
)


def test_stamp_and_read_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(boot_sha, "BOOT_DIR", tmp_path / "boot")
    monkeypatch.setattr(boot_sha, "current_head", lambda: "deadbeefcafe")
    boot_sha.stamp("sim-runner")
    assert boot_sha.read_boot_sha("sim-runner") == "deadbeefcafe"
    assert boot_sha.read_boot_sha("never-stamped") is None       # absent -> None, never raises


def test_current_head_is_a_sha_or_none():
    h = boot_sha.current_head()
    assert h is None or (len(h) >= 7 and all(c in "0123456789abcdef" for c in h))


# ── (a) POPULATION: observed, never declared ────────────────────────────────────────────────
_MIGRATED = {"session": "mig", "owner": "systemd", "match": "mig.py", "launched_by": "systemd"}
_UNFLIPPED = {"session": "unflipped", "owner": "systemd", "match": "unflipped.py"}  # defaults tmux


def test_drift_population_is_observed_never_declared():
    """THE 2026-07-29 MUTATION, restated as a test: a row that never got its `launched_by` flip is
    STILL in the population, because the population is what systemd is observed to be running.
    Re-add any `launched_by`-based filter and this reds — which is what silently deleted sim-runner
    and background-worker from the answer for ten hours."""
    observed = observed_launched_by(
        [_MIGRATED, _UNFLIPPED],
        unit_states={"mig": {"active": True}, "unflipped": {"active": True}},
        main_pids={"mig": 11, "unflipped": 22},
    )
    assert drift_population(observed) == ["mig", "unflipped"]


def test_population_equals_the_observed_running_set_not_a_subset():
    """The exit criterion, stated directly: population == observed running set. An inactive unit
    drops out (it is not running stale code); every ACTIVE one is present regardless of what the
    manifest says about it."""
    entries = [_MIGRATED, _UNFLIPPED, {"session": "down", "owner": "systemd", "match": "down.py"}]
    unit_states = {"mig": {"active": True}, "unflipped": {"active": True},
                   "down": {"active": False}}
    main_pids = {"mig": 11, "unflipped": 22, "down": 0}
    observed_running = {s for s, st in unit_states.items() if st["active"]}
    pop = set(drift_population(observed_launched_by(entries, unit_states, main_pids)))
    assert pop == observed_running, "population must EQUAL the observed running set, not shrink it"


def test_the_seat_and_non_systemd_owners_are_never_in_the_population():
    """The interactive seat is not a systemd unit and must never be judged as one."""
    entries = [{"session": "claude", "owner": "worker-seat-manager", "match": R.SEAT_MATCH},
               {"session": "other", "owner": "(none)", "match": "other.py"}]
    observed = observed_launched_by(entries, {"claude": {"active": True}}, {"claude": 5})
    assert observed == {}
    assert drift_population(observed) == []


def test_cgroup_refutes_a_claimed_systemd_launch_but_unreadable_proc_does_not_shrink():
    """/proc is a REFUTER, never a requirement. A pid whose cgroup names a DIFFERENT unit is not
    evidence of this unit running; an UNREADABLE cgroup must leave the daemon in the population
    (making a read failure shrink the population is the exact fail-open shape being closed)."""
    wrong = observed_launched_by([_MIGRATED], {"mig": {"active": True}}, {"mig": 11},
                                 cgroup_of=lambda pid: "0::/user.slice/app.slice/other.service")
    assert wrong["mig"] is None
    unreadable = observed_launched_by([_MIGRATED], {"mig": {"active": True}}, {"mig": 11},
                                      cgroup_of=lambda pid: "")
    assert unreadable["mig"] == "systemd"
    right = observed_launched_by([_MIGRATED], {"mig": {"active": True}}, {"mig": 11},
                                 cgroup_of=lambda pid: "0::/user.slice/app.slice/mig.service")
    assert right["mig"] == "systemd"


def test_a_wrong_manifest_row_fails_loud_instead_of_shrinking_the_population():
    """R10 class closure: the declaration is now the CROSS-CHECK. A row saying tmux for a daemon
    observed under systemd is MISDECLARED_LAUNCHER — loud — and is *still counted*. Before, that
    same row was silent and removed the daemon from the answer."""
    observed = observed_launched_by([_UNFLIPPED], {"unflipped": {"active": True}},
                                    {"unflipped": 22})
    drift = launcher_drift([_UNFLIPPED], observed)
    assert [d["session"] for d in drift] == ["unflipped"]
    assert drift[0]["status"] == "MISDECLARED_LAUNCHER" and drift[0]["alarm"] is True
    assert "unflipped" in drift_population(observed)      # loud AND still watched


def test_a_correctly_declared_row_raises_no_launcher_alarm():
    """R15 fires-on-defect-only half: a truthful manifest is silent, or the alarm is noise."""
    observed = observed_launched_by([_MIGRATED], {"mig": {"active": True}}, {"mig": 11})
    assert launcher_drift([_MIGRATED], observed) == []


def test_the_declaration_derived_population_helper_is_gone():
    """R15 mutation-catch for "empty/shrink the population": the old declaration-derived selector
    is DELETED, not merely unused. Reintroducing `_systemd_owned_sessions` as the population is the
    mutation this pins — and a no-caller survivor would grow a caller again (the no-caller class)."""
    assert not hasattr(R, "_systemd_owned_sessions")
    import inspect
    src = inspect.getsource(R.evaluate_boot_sha_drift)
    # `observed_launched_by` (the OBSERVER) is fine; reading the declared field off a manifest
    # entry is the mutation. Match the read, not the word.
    assert 'get("launched_by"' not in src and "get('launched_by'" not in src, \
        "the live population must not read the declared field"


# ── (b) SIGNAL: the modules the daemon actually loads ───────────────────────────────────────

def test_signal_is_green_when_head_moved_but_nothing_loaded_changed():
    """THE always-red mutation: revert the signal to HEAD-comparison and this reds. The daemon
    booted from an OLD sha, HEAD has moved, and a file changed — but not one it imports. GREEN."""
    d = loaded_code_drift(["a"], {"a": "OLDSHA"}, {"a": {"background/a.py"}},
                          changed_since=lambda sha: {"docs/status/LATEST.md", "background/z.py"})
    assert d["stale"] == {} and d["unresolved"] == {}


def test_signal_is_red_when_a_loaded_module_changed():
    """The half that must still fire: one changed module inside the closure is stale, even though
    only that single file moved."""
    d = loaded_code_drift(["a"], {"a": "OLDSHA"}, {"a": {"background/a.py", "background/b.py"}},
                          changed_since=lambda sha: {"background/b.py"})
    assert d["stale"] == {"a": ["background/b.py"]}


@pytest.mark.parametrize("boot_shas,closures,changed,reason", [
    ({"a": None}, {"a": {"background/a.py"}}, lambda s: set(), "unstamped"),
    ({"a": "OLD"}, {"a": set()}, lambda s: {"background/a.py"}, "closure-unknown"),
    ({"a": "OLD"}, {"a": {"background/a.py"}}, lambda s: None, "sha-unresolved"),
])
def test_an_unanswerable_check_is_unresolved_never_a_silent_green(boot_shas, closures,
                                                                  changed, reason):
    """R15 fail-silent doctrine: unknown must not read as clean. Each of the three ways the
    comparison can fail to produce an answer lands in `unresolved` WITH ITS REASON — including the
    vacuous one (an empty closure compares against nothing and would otherwise always pass)."""
    d = loaded_code_drift(["a"], boot_shas, closures, changed)
    assert d["stale"] == {}
    assert d["unresolved"] == {"a": reason}


def test_import_closure_follows_transitive_and_function_level_imports(tmp_path):
    """The closure must be the modules ACTUALLY loaded, including lazy in-function imports (this
    project's daemons import that way constantly) — an under-approximating closure is fail-open."""
    pkg = tmp_path / "background"       # must be one of the shared graph's analysed roots
    pkg.mkdir()
    (pkg / "entry.py").write_text(
        "from background import mid\ndef go():\n"
        "    from background.lazy import thing\n    return thing\n")
    (pkg / "mid.py").write_text("from background import deep\n")
    (pkg / "deep.py").write_text("x = 1\n")
    (pkg / "lazy.py").write_text("thing = 2\n")
    (pkg / "unrelated.py").write_text("y = 3\n")
    closure = code_closure.import_closure("background/entry.py", tmp_path)
    assert closure == {"background/entry.py", "background/mid.py",
                       "background/deep.py", "background/lazy.py"}


def test_entry_path_handles_both_manifest_launch_forms(tmp_path):
    (tmp_path / "background").mkdir()
    (tmp_path / "background" / "sim_runner.py").write_text("")
    (tmp_path / "background" / "naive_organ.py").write_text("")
    assert code_closure.entry_path("python3 background/sim_runner.py",
                                   tmp_path) == "background/sim_runner.py"
    assert code_closure.entry_path("python3 -m background.naive_organ daemon",
                                   tmp_path) == "background/naive_organ.py"
    assert code_closure.entry_path("python3 -m background.nope", tmp_path) is None


def test_a_missing_entry_yields_an_empty_closure_which_callers_must_treat_as_unresolved(tmp_path):
    """Pinning the contract between the two modules: empty is NOT 'nothing changed'."""
    assert code_closure.import_closure("nope/missing.py", tmp_path) == set()
    d = loaded_code_drift(["a"], {"a": "OLD"}, {"a": set()}, lambda s: {"background/a.py"})
    assert d["unresolved"] == {"a": "closure-unknown"}


def test_generated_units_stamp_boot_sha_before_execstart():
    from background import generate_units as G
    units = G.regenerate()
    assert units, "expected generated systemd units"
    for fname, text in units.items():
        session = fname[: -len(".service")]
        assert f"ExecStartPre=-/usr/bin/python3 -m background.boot_sha {session}" in text
        # G-D3: the stamp must run BEFORE the daemon starts, or it records the wrong SHA
        assert text.index("ExecStartPre") < text.index("ExecStart=")


# ── The named replay: the daemon that actually broke, against the state it actually ran ─────

_WEDGE_BOOT_SHA = "fa9a73c72"   # 2026-08-08 23:44 UTC — the commit sim-runner did NOT have


def _sha_known(sha: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                          capture_output=True).returncode == 0


@pytest.mark.skipif(not _sha_known(_WEDGE_BOOT_SHA),
                    reason="wedge-era commit absent from this checkout (shallow clone)")
def test_sim_runner_replayed_against_the_wedge_boot_state_is_RED():
    """The named exit criterion. sim-runner booted before `fa9a73c72` and ran the pre-cure argv for
    ten hours; `background/sim_runner.py` is inside both that diff and sim-runner's own closure, so
    the rebuilt signal must call it stale. This is the case the OLD detector answered "clean" for,
    because sim-runner was not in its population at all."""
    closure = code_closure.closure_for_session("sim-runner")
    assert closure, "sim-runner must have a resolvable closure (vacuity)"
    d = loaded_code_drift(["sim-runner"], {"sim-runner": _WEDGE_BOOT_SHA},
                          {"sim-runner": closure}, boot_sha.changed_paths_since)
    assert "sim-runner" in d["stale"], "the daemon that broke must read RED on its own boot state"
    assert "background/sim_runner.py" in d["stale"]["sim-runner"]


# ── VACUITY: the honest path must evaluate a non-empty set on this box ──────────────────────

def _user_systemd_available() -> bool:
    try:
        return subprocess.run(["systemctl", "--user", "is-system-running"],
                              capture_output=True).returncode in (0, 1)
    except Exception:
        return False


@pytest.mark.real_subprocess   # the WHOLE POINT is the live daemon set, not a stub of it
@pytest.mark.skipif(not _user_systemd_available(), reason="no --user systemd on this host")
def test_live_evaluation_watches_a_nonempty_daemon_set_and_can_be_green():
    """R15 VACUITY GUARD on the live box: a control whose population is empty cannot fail, so an
    empty answer is a FAILED check, and `evaluate_boot_sha_drift` says so via `vacuous`. It must
    also be able to distinguish — an answer where every observed daemon is stale is the always-red
    disease, so we assert the two halves are not the same set."""
    r = R.evaluate_boot_sha_drift()
    assert r["population"], "the drift population must not be empty while daemons run"
    assert r["vacuous"] is False
    assert set(r["stale"]) <= set(r["population"])
    assert set(r["unresolved"]) <= set(r["population"])
    # LIVE proof the signal is closure-based, not HEAD-based: every red must NAME the loaded files
    # that changed, and each must be inside that daemon's own closure. A HEAD-comparison cannot
    # produce this evidence — it has no per-daemon file list to produce.
    for session, files in r["stale_detail"].items():
        assert files, f"{session} flagged stale with no changed loaded module named"
        assert set(files) <= code_closure.closure_for_session(session)


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
pytestmark = pytest.mark.operational
