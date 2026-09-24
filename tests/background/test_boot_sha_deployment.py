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

import json
import os
import subprocess
import time

import pytest

from background import boot_sha, code_closure
from background import process_reconciler as R
from background.process_reconciler import (
    drift_population,
    launcher_drift,
    loaded_code_drift,
    observed_launched_by,
)

#: For the cases that are about the OTHER three rules. Both maps empty means "no start time and no
#: stamp time is known for this session", under which the 2026-09-24 rule makes no claim and the
#: older rules decide — spelled out at each call site rather than defaulted, because a rule a
#: caller can silently omit is how the stamper itself went twenty days unnoticed.
_NOT_ABOUT_STAMP_AGE = {"boot_ts": {}, "started_at": {}}


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
                          changed_since=lambda sha, session=None: {"docs/status/LATEST.md", "background/z.py"},
                          **_NOT_ABOUT_STAMP_AGE)
    assert d["stale"] == {} and d["unresolved"] == {}


def test_signal_is_red_when_a_loaded_module_changed():
    """The half that must still fire: one changed module inside the closure is stale, even though
    only that single file moved."""
    d = loaded_code_drift(["a"], {"a": "OLDSHA"}, {"a": {"background/a.py", "background/b.py"}},
                          changed_since=lambda sha, session=None: {"background/b.py"},
                          **_NOT_ABOUT_STAMP_AGE)
    assert d["stale"] == {"a": ["background/b.py"]}


@pytest.mark.parametrize("boot_shas,closures,changed,reason", [
    ({"a": None}, {"a": {"background/a.py"}}, lambda s, sess=None: set(), "unstamped"),
    ({"a": "OLD"}, {"a": set()}, lambda s, sess=None: {"background/a.py"}, "closure-unknown"),
    ({"a": "OLD"}, {"a": {"background/a.py"}}, lambda s, sess=None: None, "sha-unresolved"),
])
def test_an_unanswerable_check_is_unresolved_never_a_silent_green(boot_shas, closures,
                                                                  changed, reason):
    """R15 fail-silent doctrine: unknown must not read as clean. Each of the three ways the
    comparison can fail to produce an answer lands in `unresolved` WITH ITS REASON — including the
    vacuous one (an empty closure compares against nothing and would otherwise always pass)."""
    d = loaded_code_drift(["a"], boot_shas, closures, changed, **_NOT_ABOUT_STAMP_AGE)
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
    d = loaded_code_drift(["a"], {"a": "OLD"}, {"a": set()}, lambda s, sess=None: {"background/a.py"},
                          **_NOT_ABOUT_STAMP_AGE)
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


def test_the_units_own_declared_stamp_command_stamps(tmp_path):
    """THE DEFECT THIS EXISTS FOR, measured 2026-09-24 — and note that the test directly above was
    GREEN throughout it.

    `3ecf355d8` (2026-09-04) deleted `boot_sha.__main__` while fixing an unrelated defect. Ten
    generated units, and their ten installed copies, kept declaring
    `ExecStartPre=-/usr/bin/python3 -m background.boot_sha <session>`; the command kept exiting 0;
    the leading `-` told systemd to ignore it; and it stamped NOTHING for twenty days. Every check
    that existed asked about the DECLARATION — is the line present, is it before ExecStart — and a
    declaration is exactly what had not broken. `stamp()` had no production caller at all, and its
    unit tests all monkeypatched BOOT_DIR, so they proved the function while the invocation was
    dead.

    So this control runs the command itself. The argv is PARSED OUT OF THE GENERATED UNIT rather
    than retyped here, which keys it to the property ("whatever the unit declares, stamps") instead
    of to today's spelling: renaming the module, moving the entrypoint or dropping `__main__` again
    all red this one leg."""
    from background import generate_units as G
    units = G.regenerate()
    fname, text = sorted(units.items())[0]
    session = fname[: -len(".service")]
    line = next(ln for ln in text.splitlines() if ln.startswith("ExecStartPre="))
    argv = line.split("=", 1)[1].lstrip("-+!@").split()

    boot_dir = tmp_path / "boot"
    r = subprocess.run(argv, cwd=G._HERE.parent, capture_output=True, text=True, timeout=120,
                       env={**os.environ, "SE_BOOT_DIR": str(boot_dir)})

    record = boot_dir / f"{session}.json"
    assert record.is_file(), (
        f"the unit's own declared stamp command wrote no boot record.\n"
        f"argv={argv} rc={r.returncode}\nstderr={r.stderr[-800:]}")
    written = json.loads(record.read_text())
    assert written["session"] == session      # it must stamp the session it was ASKED for
    assert written.get("sha")                 # ...with a real SHA, not a None-shaped placeholder
    assert written.get("ts")


def test_process_start_time_reads_a_live_process_and_refuses_a_dead_one():
    """The observation the fourth rule rests on. Our own pid must yield a plausible epoch second in
    the past; an impossible pid must yield None, never 0 or now() — a fabricated start time would
    make every stamp look fresh, which is fail-open in the one direction that matters."""
    mine = R.process_start_time(os.getpid())
    assert mine is not None and 1_500_000_000 < mine <= time.time() + 1
    assert R.process_start_time(0) is None
    assert R.process_start_time(2 ** 30) is None


def test_a_stamp_from_a_previous_boot_is_unresolved_not_stale():
    """THE 2h48m WINDOW, as a control. `465a0dfca` landed `reask()` into `staging_watcher` at
    2026-09-23 23:12:02Z; the running watcher only applied it at 2026-09-24 02:00:23Z when
    something restarted it. Nothing could see that, because the session read `stale` on BOTH sides
    of the restart — its stamp was from 2026-09-17 and described a process that no longer existed,
    and a stamp that old makes `changed_paths_since` report the daemon's own source as changed
    whatever it is actually running.

    A stamp older than the process it claims to describe says nothing about the loaded bytes, so
    the honest verdict is a NAMED refusal, not a confident red pointing at the wrong remedy
    (restart it — which had already happened — instead of repair the stamper)."""
    d = loaded_code_drift(["staging-watcher"], {"staging-watcher": "OLDSHA"},
                          {"staging-watcher": {"background/staging_watcher.py"}},
                          lambda sha, session=None: {"background/staging_watcher.py"},
                          boot_ts={"staging-watcher": 1000.0},
                          started_at={"staging-watcher": 2000.0})
    assert d["stale"] == {}, "a stamp describing a dead process must not license a `stale` verdict"
    assert d["unresolved"] == {"staging-watcher": "stamp-predates-process"}


def test_a_stamp_written_at_this_boot_still_reaches_the_stale_verdict():
    """The other half, and the one that stops the new rule swallowing the signal: same inputs, the
    stamp now POSTDATES the process start, and the daemon reads honestly stale. Without this leg a
    rule that returned 'stamp-predates-process' unconditionally would pass the test above — the
    guard-that-refuses-everything shape."""
    d = loaded_code_drift(["staging-watcher"], {"staging-watcher": "OLDSHA"},
                          {"staging-watcher": {"background/staging_watcher.py"}},
                          lambda sha, session=None: {"background/staging_watcher.py"},
                          boot_ts={"staging-watcher": 2000.0},
                          started_at={"staging-watcher": 1000.0})
    assert d["unresolved"] == {}
    assert d["stale"] == {"staging-watcher": ["background/staging_watcher.py"]}


def test_the_four_unresolved_reasons_are_reachable_AND_DISTINCT():
    """One control over the whole partition, rather than a leg per branch. Four shapes must produce
    four DIFFERENT reasons: asserting only that each is 'unresolved' is blind to two shapes
    collapsing onto one verdict, which is precisely what happened before the fourth rule existed —
    a stale stamp and a current one both reached `stale` and nothing could tell them apart.

    Keyed by SHAPE, not by expected answer, so a collapse shows up as a duplicate reason."""
    live = {"boot_ts": {"a": 2000.0}, "started_at": {"a": 1000.0}}
    shapes = {
        "unstamped": dict(boot_shas={"a": None}, closures={"a": {"background/a.py"}},
                          changed=lambda s, sess=None: set(), **live),
        "stamp-from-a-previous-boot": dict(boot_shas={"a": "OLD"},
                                           closures={"a": {"background/a.py"}},
                                           changed=lambda s, sess=None: set(),
                                           boot_ts={"a": 1000.0}, started_at={"a": 2000.0}),
        "closure-empty": dict(boot_shas={"a": "OLD"}, closures={"a": set()},
                              changed=lambda s, sess=None: {"background/a.py"}, **live),
        "diff-unresolvable": dict(boot_shas={"a": "OLD"}, closures={"a": {"background/a.py"}},
                                  changed=lambda s, sess=None: None, **live),
    }
    seen: dict[str, str] = {}
    for shape, kw in shapes.items():
        d = loaded_code_drift(["a"], kw["boot_shas"], kw["closures"], kw["changed"],
                              boot_ts=kw["boot_ts"], started_at=kw["started_at"])
        assert d["stale"] == {}, shape
        seen[shape] = d["unresolved"]["a"]
    assert len(set(seen.values())) == len(shapes), f"two shapes collapsed onto one reason: {seen}"


def test_an_unknown_start_time_makes_no_new_claim():
    """The degradation rule, stated as a control. A session whose process start time cannot be read
    must fall through to the older rules — the new refusal needs POSITIVE evidence. Inverting this
    would make an unreadable /proc mark every daemon unresolved, which is the always-red failure
    the 2026-08-09 rebuild exists to abolish."""
    for missing in ({"a": None}, {}):
        d = loaded_code_drift(["a"], {"a": "OLD"}, {"a": {"background/a.py"}},
                              lambda s, sess=None: {"background/a.py"},
                              boot_ts={"a": 1000.0}, started_at=missing)
        assert d["unresolved"] == {} and d["stale"] == {"a": ["background/a.py"]}


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
                          {"sim-runner": closure},
                          lambda sha, session=None: boot_sha.changed_paths_since(sha),
                          **_NOT_ABOUT_STAMP_AGE)
    assert "sim-runner" in d["stale"], "the daemon that broke must read RED on its own boot state"
    assert "background/sim_runner.py" in d["stale"]["sim-runner"]


# ── VACUITY: the honest path must evaluate a non-empty set on this box ──────────────────────

#: The states `systemctl --user is-system-running` prints when it REACHED systemd. Anything
#: outside this set means the answer is about the connection, not about the manager.
_SYSTEMD_REACHED_STATES = frozenset({
    "running", "degraded", "starting", "stopping", "maintenance", "initializing", "offline",
})


def _user_systemd_available() -> bool:
    """True only if a `--user` query actually REACHED systemd.

    The returncode alone cannot answer this, and reading it as though it could produced a
    misleading red on 2026-08-20. `is-system-running` exits 1 BOTH when the manager is
    reachable and degraded -- an ordinary, healthy-enough state on this box -- AND when there
    is no bus to talk to at all:

        no XDG_RUNTIME_DIR -> rc=1, stdout ''        ("Failed to connect to user scope bus")
        with the bus       -> rc=1, stdout 'degraded'

    So `returncode in (0, 1)` said "available" in a shell with no bus, the skipif did not fire,
    and the test below ran, found an empty daemon population, and failed with
    "the drift population must not be empty while daemons run" -- while eight daemons were
    running. It reported I COULD NOT ASK as THE ANSWER IS EMPTY, which is the FAIL-SILENT
    pattern R15 names, wearing the costume of a substantive failure.

    stdout is the discriminator, because the bus error goes to stderr and leaves stdout empty.
    """
    try:
        proc = subprocess.run(["systemctl", "--user", "is-system-running"],
                              capture_output=True, text=True)
    except Exception:
        return False
    return (proc.stdout or "").strip() in _SYSTEMD_REACHED_STATES


@pytest.mark.real_subprocess   # the WHOLE POINT is the live daemon set, not a stub of it
# "could not REACH", not "does not exist" -- the distinction this guard was fixed to make. A
# shell without XDG_RUNTIME_DIR is the common case here and systemd is present and fine; saying
# it is absent would send the next reader looking for a missing daemon.
@pytest.mark.skipif(not _user_systemd_available(),
                    reason="could not reach --user systemd (no session bus in this environment)")
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


# ── Is the INSTRUMENT alive? (2026-09-24) ──────────────────────────────────────
#
# Everything above derives its verdict FROM the boot stamps, so a dead stamper makes all of it
# vacuous rather than clean -- and that is measured history, not a hypothetical: from 2026-09-04 to
# 2026-09-18 the units' declared ExecStartPre exited 0 and wrote nothing, and `loaded_code_drift`
# read the resulting stamps as valid for twenty days.
#
# `test_the_units_own_declared_stamp_command_stamps` above already proves the REPO's generated unit
# stamps. It cannot prove the BOX's installed unit does, and the box is where daemons boot: on
# 2026-09-24 the repair was at HEAD while the daemons restarted 7m18s before it reached the disk
# they read. These controls cover `probe_declared_stamper`, which asks the installed side, live,
# WITHOUT needing a restart -- because the stamping population (12 long-lived daemons, newest start
# 07:10:34) and the restarting population (7 short jobs, none declaring a stamp line) are disjoint,
# so a restart-triggered signal over them goes dark by construction.


def _unit_dir(tmp_path, command: str, sessions=("sanity-daemon", "supervisor")):
    """Installed-unit fixtures. The command is written into ExecStartPre exactly as systemd would
    hold it, prefix and all, so the parser is tested against the real setting shape."""
    d = tmp_path / "units"
    d.mkdir(exist_ok=True)
    for s in sessions:
        (d / f"{s}.service").write_text(
            "[Service]\n"
            f"ExecStartPre=-{command} {s}\n"
            "ExecStart=/usr/bin/python3 -m background.thing\n")
    return d


def _fake_run(returncode=0, writes=None, raises=None):
    """A stand-in for the subprocess call. `writes` is the record dict the command 'writes' into
    the throwaway SE_BOOT_DIR -- so the oracle under test really is 'did a file appear', not
    'what did the fake return'."""
    def run(argv, env):
        if raises is not None:
            raise raises
        if writes is not None:
            import pathlib
            p = pathlib.Path(env["SE_BOOT_DIR"]) / "sanity-daemon.json"
            p.write_text(writes if isinstance(writes, str) else json.dumps(writes))
        return subprocess.CompletedProcess(argv, returncode, "", "boom\n")
    return run


def test_a_stamper_that_exits_zero_and_writes_nothing_is_named_silent(tmp_path):
    """THE DEFECT THIS EXISTS FOR, and the reason the oracle is a FILE and not an exit code.

    Measured 2026-09-24 by running `3ecf355d8:background/boot_sha.py` exactly as the unit declares
    it: **exit 0, zero files written**. Every check that existed graded the declaration or the exit
    status, and both were healthy for the whole twenty days. `silent` is the verdict that had no
    name, which is why nothing could report it.
    """
    d = _unit_dir(tmp_path, "/usr/bin/python3 -m background.boot_sha")
    r = R.probe_declared_stamper(unit_dir=d, run=_fake_run(returncode=0, writes=None))
    assert r["verdict"] == "silent"
    assert r["ok"] is False, "exit 0 with no stamp is the twenty-day defect, not a pass"


def test_a_stamper_that_writes_a_record_with_a_sha_is_the_only_thing_called_works(tmp_path):
    d = _unit_dir(tmp_path, "/usr/bin/python3 -m background.boot_sha")
    r = R.probe_declared_stamper(unit_dir=d,
                                 run=_fake_run(writes={"session": "sanity-daemon", "sha": "abc123def"}))
    assert (r["verdict"], r["ok"]) == ("works", True)
    # a stamp with no SHA is NOT working: it exists and dates nothing, so every drift verdict
    # derived from it is unanswerable. Distinct verdict, because the remedy differs (git in the
    # daemon's environment, not the stamper).
    r2 = R.probe_declared_stamper(unit_dir=d, run=_fake_run(writes={"session": "x", "sha": None}))
    assert (r2["verdict"], r2["ok"]) == ("sha-unknown", False)


def test_the_probe_grades_every_way_the_stamper_can_fail_and_they_are_ALL_distinct(tmp_path):
    """ONE control over the WHOLE partition rather than a leg per branch (CLAUDE.md).

    A probe that returned a single refusal for everything would pass each negative leg above --
    and it would collapse 'the command is broken' into 'the command is missing', which have
    different remedies. So assert the partition is genuinely separated, in one place.
    """
    d = _unit_dir(tmp_path, "/usr/bin/python3 -m background.boot_sha")
    verdicts = {
        "works": R.probe_declared_stamper(unit_dir=d, run=_fake_run(writes={"sha": "a1"})),
        "silent": R.probe_declared_stamper(unit_dir=d, run=_fake_run(writes=None)),
        "failed": R.probe_declared_stamper(unit_dir=d, run=_fake_run(returncode=1)),
        "sha-unknown": R.probe_declared_stamper(unit_dir=d, run=_fake_run(writes={"sha": ""})),
        "unreadable": R.probe_declared_stamper(unit_dir=d, run=_fake_run(writes="}not json{")),
        "unprobed": R.probe_declared_stamper(unit_dir=d, run=_fake_run(raises=OSError("no exec"))),
        "undeclared": R.probe_declared_stamper(unit_dir=tmp_path / "empty", run=_fake_run()),
    }
    got = {name: r["verdict"] for name, r in verdicts.items()}
    assert got == {k: k for k in got}, f"the partition collapsed: {got}"
    # …and exactly one of them is a pass. `ok` derived from the OK verdict alone is what makes a
    # verdict added later not-ok BY CONSTRUCTION, instead of fail-open until someone updates a list.
    assert [n for n, r in verdicts.items() if r["ok"]] == ["works"]


def test_an_absent_or_unreadable_unit_directory_is_a_refusal_never_a_pass(tmp_path):
    """FAIL CLOSED. 'No unit declares the stamper' is the deployment having LOST the declaration --
    the loudest possible state -- and an empty dict read as 'no faults found' is exactly the
    fail-silent shape R15 names."""
    for where in (tmp_path / "does-not-exist", tmp_path / "empty"):
        r = R.probe_declared_stamper(unit_dir=where, run=_fake_run(writes={"sha": "a"}))
        assert (r["verdict"], r["ok"]) == ("undeclared", False)
        assert r["declaring_units"] == 0
    assert R.declared_stamp_argv(tmp_path / "does-not-exist") == {}


def test_the_argv_is_parsed_out_of_the_unit_text_with_systemds_prefixes_stripped(tmp_path):
    """Keyed to the PROPERTY ('whatever the unit declares is what gets run'), not to today's
    spelling. A probe that retyped the command would keep passing after a rename -- which is the
    precise shape of the check that stayed green through the twenty days."""
    d = _unit_dir(tmp_path, "-@/opt/py3.13/bin/python3 -m background.boot_sha")
    argv = R.declared_stamp_argv(d)["sanity-daemon.service"]
    assert argv == ["/opt/py3.13/bin/python3", "-m", "background.boot_sha", "sanity-daemon"], argv
    seen = []
    R.probe_declared_stamper(
        unit_dir=d,
        run=lambda a, e: seen.append(a) or subprocess.CompletedProcess(a, 0, "", ""))
    assert seen[0] == argv, "the probe must run the PARSED argv, not a retyped one"
    # a unit with no stamp line contributes nothing -- the population is the declaring units
    (d / "no-stamp.service").write_text("[Service]\nExecStart=/usr/bin/python3 -m background.x\n")
    assert "no-stamp.service" not in R.declared_stamp_argv(d)


def test_twelve_units_declaring_one_command_cost_one_probe_not_twelve(tmp_path):
    """The live box has 12 declaring units and the probe runs the real stamper, which hashes ~430
    dirty blobs per call. Collapsing identical shapes is what keeps this cheap enough to run on
    every health cycle -- and a probe too slow to run on a cadence is a probe that only answers at
    a restart, which is the gap this whole mechanism exists to close."""
    sessions = tuple(f"d{i}" for i in range(12))
    d = _unit_dir(tmp_path, "/usr/bin/python3 -m background.boot_sha", sessions=sessions)
    calls = []
    R.probe_declared_stamper(
        unit_dir=d,
        run=lambda a, e: calls.append(a) or subprocess.CompletedProcess(a, 0, "", ""))
    assert len(calls) == 1, f"expected the 12 spellings to collapse to one shape, ran {len(calls)}"
    # …and a genuinely DIFFERENT command is a different shape, so the collapse cannot hide one.
    (d / "odd.service").write_text(
        "[Service]\nExecStartPre=-/usr/bin/python3.9 -m background.boot_sha odd\nExecStart=/x\n")
    calls.clear()
    R.probe_declared_stamper(
        unit_dir=d,
        run=lambda a, e: calls.append(a) or subprocess.CompletedProcess(a, 0, "", ""))
    assert len(calls) == 2, f"a distinct interpreter must be probed separately, ran {len(calls)}"


def test_a_broken_stamper_reaches_the_health_surface_as_a_PROBLEM_not_a_footnote():
    """The direction's own exit condition: break the stamper deliberately and show the refusal
    surfaces somewhere something READS. `health_check.run_health_check` is that place.

    Anti-tautology: the same report with the stamper WORKING must NOT produce the line, or this
    asserts nothing about the stamper -- it would pass against a health check that printed the
    warning unconditionally.
    """
    from unittest import mock

    from background import health_check

    base = {"head": "abc", "population": ["sanity-daemon"], "stale": [], "stale_detail": {},
            "unresolved": {}, "misdeclared": [], "vacuous": False}

    def surface(stamper):
        report = {**base, "stamper": stamper}
        with mock.patch.object(R, "evaluate_boot_sha_drift", lambda: report):
            _ok, ok_lines, problems = health_check.run_health_check()
        return problems, ok_lines

    problems, ok_lines = surface({"verdict": "silent", "ok": False, "declaring_units": 12,
                                  "probes": [], "detail": "exited 0 and wrote no boot record"})
    hit = [ln for ln in problems if "BOOT STAMPER" in ln]
    assert hit, f"a dead stamper must be a PROBLEM line; problems were {problems}"
    assert "silent" in hit[0] and "exited 0 and wrote no boot record" in hit[0], hit[0]
    assert not [ln for ln in ok_lines if "BOOT STAMPER" in ln]

    problems, ok_lines = surface({"verdict": "works", "ok": True, "declaring_units": 12,
                                  "probes": [], "detail": "stamped at abc123"})
    assert not [ln for ln in problems if "BOOT STAMPER" in ln], "green stamper must not warn"
    assert [ln for ln in ok_lines if "boot stamper" in ln], ok_lines

    # A report from a caller that predates the field must not read as a PASS by its absence --
    # but it must not invent a fault either. It is simply silent, and the `"stamper" in` test
    # (rather than a truthiness test) is what makes that true.
    problems, _ = surface(None)
    del problems  # nothing asserted about content; the assertion is the next line not raising
    with mock.patch.object(R, "evaluate_boot_sha_drift", lambda: dict(base)):
        _ok, _okl, legacy = health_check.run_health_check()
    assert not [ln for ln in legacy if "BOOT STAMPER" in ln]


def test_a_flag_reaching_argv_is_refused_by_name_instead_of_minting_a_junk_session():
    """THE DEFECT THIS EXISTS FOR, found 2026-09-24 in the boot directory itself:
    `docs/observability/.daemon_boot/--report.json`, session `--report`, written 2026-08-14.

    `stamp(sys.argv[1])` accepted anything, so a caller passing a FLAG minted a record that sat
    among the real daemons' for six weeks looking exactly like one of them. A census asking "which
    daemons have stamped" counted it.

    The refusal NAMES its reason (CLAUDE.md): that is how a wrong refusal gets discovered. And it
    stays non-blocking -- the unit's leading `-` means a refusal still never stops a daemon
    booting; it only stops the junk record.
    """
    assert boot_sha.is_session_name("sanity-daemon")
    assert boot_sha.is_session_name("unknown"), "the no-argv fallback must still stamp"
    for junk in ("--report", "-v", "", "../escape", "a/b"):
        assert not boot_sha.is_session_name(junk), junk


@pytest.mark.real_subprocess   # the refusal must hold for the REAL entrypoint, not just the helper
def test_the_entrypoint_itself_refuses_a_flag_and_writes_nothing(tmp_path):
    """The helper above is pure; this is the arm that proves the ENTRYPOINT consults it. Without
    it, `is_session_name` could be correct and uncalled -- which is precisely how `stamp()` sat
    with zero production callers for twenty days while its unit tests stayed green."""
    def run_argv(arg):
        d = tmp_path / arg.replace("/", "_").replace(".", "_") or "x"
        d.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(["/usr/bin/python3", "-m", "background.boot_sha", arg],
                              cwd=os.path.dirname(os.path.dirname(os.path.dirname(
                                  os.path.abspath(__file__)))),
                              capture_output=True, text=True, timeout=180,
                              env={**os.environ, "SE_BOOT_DIR": str(d)})
        return proc, sorted(d.glob("*.json"))

    proc, written = run_argv("sanity-daemon")
    assert proc.returncode == 0 and len(written) == 1, (proc.returncode, proc.stderr)

    proc, written = run_argv("--report")
    assert proc.returncode != 0, "a flag must not be stamped silently"
    assert written == [], f"the junk record was written anyway: {written}"
    assert "--report" in proc.stderr and "not a session name" in proc.stderr, proc.stderr


@pytest.mark.real_subprocess   # the point is the REAL command on the REAL installed units
@pytest.mark.skipif(not _user_systemd_available(),
                    reason="could not reach --user systemd (no session bus in this environment)")
def test_live_the_installed_units_declared_stamper_actually_stamps_on_this_box():
    """The live arm. This is the one that would have gone red on 2026-09-04, the day of the
    regression, instead of twenty days later -- and it needs no daemon restart to say so."""
    r = R.probe_declared_stamper()
    assert r["declaring_units"] > 0, "no installed unit declares the boot stamper on this box"
    assert r["verdict"] == "works", f"the installed units' own stamp command: {r['detail']}"
    assert r["ok"] is True


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
pytestmark = pytest.mark.operational


# ── the boot stamp must describe the TREE, not just the commit ───────────────────────────────────

def _repo(tmp_path):
    """A real git repo. A fake `git` here would test the fake, and the whole defect lives in what
    `git diff <sha> -- ` counts against a DIRTY tree."""
    import subprocess
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"],
                ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, cwd=tmp_path, check=True)
    (tmp_path / "mod.py").write_text("original\n")
    subprocess.run(["git", "add", "mod.py"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "base", "--no-gpg-sign"], cwd=tmp_path, check=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_an_uncommitted_edit_present_at_boot_is_not_code_the_daemon_is_missing(tmp_path, monkeypatch):
    """THE DEFECT THIS OWNS, measured on the live box 2026-09-04.

    A daemon boots from a WORKING TREE; the stamp could only record a COMMIT. So every uncommitted
    edit already on disk at boot was reported for ever as code the daemon did not have — when the
    daemon had loaded exactly those bytes. On this tree several lanes keep ~185 files dirty, so it
    is not an edge case: ALL THIRTEEN staleness causes across four daemons were of this kind, none
    was a commit any daemon had missed, and a restart cannot clear one of them. G-D2 restarted
    those four every ten minutes for eight hours on it.

    MUTATION: ignore `boot_blobs` in `changed_paths_since` and this fires.
    """
    sha = _repo(tmp_path)
    monkeypatch.setattr(boot_sha, "_REPO", tmp_path)
    (tmp_path / "mod.py").write_text("edited by another lane\n")   # dirty BEFORE the daemon boots
    at_boot = boot_sha.dirty_blobs()
    assert at_boot and "mod.py" in at_boot

    assert boot_sha.changed_paths_since(sha) == {"mod.py"}, "the old, subject-free answer"
    assert boot_sha.changed_paths_since(sha, at_boot) == set(), (
        "the daemon loaded these bytes off the disk and is reported as missing them"
    )


def test_an_edit_made_AFTER_boot_is_still_caught(tmp_path, monkeypatch):
    """THE NULL CONTROL, and the leg that stops the fix becoming a blindfold. The original
    argument for diffing the working tree stands for anything edited after boot — that is the
    caller/callee split which ran ten hours on 2026-08-09. MUTATION: return an empty set whenever
    `boot_blobs` is supplied and this fires."""
    sha = _repo(tmp_path)
    monkeypatch.setattr(boot_sha, "_REPO", tmp_path)
    (tmp_path / "mod.py").write_text("dirty at boot\n")
    at_boot = boot_sha.dirty_blobs()

    (tmp_path / "mod.py").write_text("edited again, after the daemon booted\n")
    assert boot_sha.changed_paths_since(sha, at_boot) == {"mod.py"}, (
        "an edit made after boot is genuinely code the daemon does not have"
    )


def test_a_file_clean_at_boot_and_dirty_now_is_caught(tmp_path, monkeypatch):
    """The other direction: nothing was dirty at boot, so `{}` is recorded, and a later edit must
    still count. `{}` and None mean different things and only one of them is 'cannot tell'."""
    sha = _repo(tmp_path)
    monkeypatch.setattr(boot_sha, "_REPO", tmp_path)
    at_boot = boot_sha.dirty_blobs()
    assert at_boot == {}, "nothing was dirty, which is not the same as not knowing"

    (tmp_path / "mod.py").write_text("edited after boot\n")
    assert boot_sha.changed_paths_since(sha, at_boot) == {"mod.py"}


def test_an_unknown_boot_tree_over_reports_rather_than_under_reports(tmp_path, monkeypatch):
    """A stamp written before this field existed has no `dirty_blobs`. The degradation must be to
    today's noisy answer, never to a quiet one: a needless restart costs a warm daemon, a missed
    one leaves stale code serving. MUTATION: treat None as {} and this fires."""
    sha = _repo(tmp_path)
    monkeypatch.setattr(boot_sha, "_REPO", tmp_path)
    (tmp_path / "mod.py").write_text("dirty\n")
    assert boot_sha.changed_paths_since(sha, None) == {"mod.py"}


def test_the_stamp_distinguishes_nothing_dirty_from_could_not_tell(tmp_path, monkeypatch):
    """THE REACHABILITY LEG: all three states of the boot record must be producible, and the third
    is the one that would otherwise be silently folded into the second."""
    sha = _repo(tmp_path)
    monkeypatch.setattr(boot_sha, "_REPO", tmp_path)
    monkeypatch.setattr(boot_sha, "BOOT_DIR", tmp_path / ".boot")

    boot_sha.stamp("clean-daemon")
    assert boot_sha.read_boot_blobs("clean-daemon") == {}

    (tmp_path / "mod.py").write_text("dirty\n")
    boot_sha.stamp("dirty-daemon")
    assert set(boot_sha.read_boot_blobs("dirty-daemon")) == {"mod.py"}

    monkeypatch.setattr(boot_sha, "dirty_blobs", lambda: None)
    boot_sha.stamp("cannot-tell-daemon")
    assert boot_sha.read_boot_blobs("cannot-tell-daemon") is None
    assert boot_sha.read_boot_sha("cannot-tell-daemon") == sha, (
        "a stamp that could not read the tree must still record the commit"
    )
