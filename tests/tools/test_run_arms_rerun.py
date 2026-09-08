"""Controls for the arms re-run's LAUNCH and its leg plan.

WHAT THESE FIRE ON IS OBSERVED, not hypothetical. The thing this module replaced,
`tools/run_arms_rerun_detached.sh`, was named for a detach it did not perform: nothing in it
launched anything, and its safety was a `systemd-run --user --unit=...` wrapper typed into a
preregistration document beside the words "with the stamp changed". Every long job in this repo
that was started without such a wrapper died at its launcher's cgroup teardown -- five launches of
the subject-cost measurement, three more in September -- and none of them wrote a liveness record,
so a dead 8-hour run and a live one left the same trace.

So the property under test is not "the legs are right", which the shell script also had. It is:

  1. THE LAUNCH IS PERFORMED BY CODE, through the one launcher, so no caller has to remember it.
  2. THE STAMP IS A DECISION, not a literal that was correct on 2026-08-29 and silently stale
     after.
  3. THE LEG DEPENDENCY IS CHECKED BEFORE EIGHT HOURS ARE SPENT, both ways -- a decomposed floor
     cut along another day's roster is a decomposition of a different book, and it produces a
     healthy-looking artefact.
"""
import subprocess
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools import run_arms_rerun as arms  # noqa: E402


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Point the module at a scratch tree: `run()` appends to a real log in docs/observability."""
    monkeypatch.setattr(arms, "_REPO", tmp_path)
    (tmp_path / "docs" / "observability").mkdir(parents=True)
    return tmp_path


def _ok(*_a, **_k):
    return types.SimpleNamespace(returncode=0)


# ── THE LAUNCH ───────────────────────────────────────────────────────────────────────────────

def test_the_launch_goes_through_the_one_launcher_and_re_enters_this_module(repo, monkeypatch):
    """THE DEFECT: the file this replaces did not launch. It ran two legs in the foreground and
    left detachment to a wrapper a human typed, so a forgotten wrapper was an 8-hour run that died
    at the next cgroup teardown with nothing recording that it had ever started.

    MUTATION: have `launch()` call `subprocess.Popen` (or `run()`) instead, and this reds -- which
    is the whole difference between this module and the script."""
    from background import launch_long_job

    seen = {}

    def _fake_launch(job, command, **kwargs):
        seen["job"], seen["command"] = job, command
        seen.update(kwargs)
        return {"unit": "longjob-" + job, "claim": "c", "log": "/tmp/l"}

    monkeypatch.setattr(launch_long_job, "launch", _fake_launch)
    monkeypatch.setattr(arms, "run", lambda *a, **k: pytest.fail("--launch must not run inline"))

    assert arms.main(["--stamp", "20260910", "--launch"]) == 0
    assert seen["job"] == "arms-rerun-20260910"
    assert seen["command"][1:3] == ["-m", "tools.run_arms_rerun"]
    assert "--launch" not in seen["command"], (
        "the unit must run the LEGS, not another launcher -- a child carrying --launch would fork "
        "forever without measuring anything"
    )
    assert seen["command"].count("--leg") == len(arms.DEFAULT_LEGS), (
        "the unit's command must name the legs explicitly; inheriting the default would make the "
        "record's own command line stop describing what was run the day the default changes"
    )


def test_the_liveness_record_is_settled_against_the_LAST_legs_artefact(repo, monkeypatch):
    """A record settled on the first leg's artefact would read COMPLETE with three legs and six
    hours still to run -- which is precisely the "looks finished, is dead" state the launcher
    exists to abolish."""
    from background import launch_long_job

    seen = {}
    monkeypatch.setattr(launch_long_job, "launch",
                        lambda job, command, **kw: seen.update(kw) or {"unit": "u", "claim": "c"})

    arms.main(["--stamp", "20260910", "--launch",
               "--leg", "three-arm", "--leg", "floor-except"])

    assert seen["artefact"] == str(arms.artefact_path("floor-except", "20260910"))


def test_a_refused_launch_reports_the_reason_rather_than_a_bare_failure(repo, monkeypatch):
    """The launcher refuses by raising with WHY in the message -- no systemd-run, a live unit
    already holding the name, an unwritable record. Swallowing that leaves the next reader
    guessing between "already running" and "systemd is gone", which are opposite remedies."""
    from background import launch_long_job

    said = []

    def _refuse(*_a, **_k):
        raise launch_long_job.LaunchRefused("a live unit already holds `longjob-arms-rerun-x`")

    monkeypatch.setattr(launch_long_job, "launch", _refuse)

    assert arms.launch(["three-arm"], "20260910", out=_Sink(said)) == 1
    assert any("a live unit already holds" in line for line in said)


class _Sink:
    """A file-like that keeps the lines written to it, so a control can read what was said."""

    def __init__(self, lines):
        self.lines = lines

    def write(self, text):
        self.lines.extend(t for t in text.splitlines() if t)

    def flush(self):
        pass


def test_without_the_flag_the_legs_run_in_this_process(repo, monkeypatch):
    """The other direction: no `--launch` means no unit. The re-exec'd child runs the legs, so a
    module that ALWAYS launched would recurse instead of measuring."""
    from background import launch_long_job

    monkeypatch.setattr(launch_long_job, "launch",
                        lambda *a, **k: pytest.fail("launched without --launch"))
    ran = []
    monkeypatch.setattr(arms, "run", lambda legs, stamp: ran.append((legs, stamp)) or 0)

    assert arms.main(["--stamp", "20260910"]) == 0
    assert ran == [(list(arms.DEFAULT_LEGS), "20260910")]


# ── THE STAMP IS A DECISION ──────────────────────────────────────────────────────────────────

def test_the_stamp_is_required_and_shaped(repo):
    """`STAMP=20260829` was a literal in the shell script, so its artefact paths were right on one
    day and the 2026-09-03 instruction was to edit the file before running. There is no value this
    could default to that would be right tomorrow.

    And a malformed stamp must REFUSE rather than run: the stamp is the artefact name, so a typo
    spends eight hours writing a file that nothing looking for the decomposition will ever open."""
    with pytest.raises(SystemExit):
        arms.main([])
    with pytest.raises(arms.RunRefused, match="not YYYYMMDD"):
        arms.check_stamp("tomorrow")
    assert arms.check_stamp("20260830b") == "20260830b", (
        "a single-letter suffix is real and on disk (value_cycle_ab_s1_three_arm_20260830b.json); "
        "a check that refuses it refuses a same-day second run, which is the honest way to avoid "
        "overwriting the first"
    )


def test_a_stamp_that_already_has_artefacts_is_refused(repo):
    """THE PREREGISTERED REFUTATION CONDITION, as a control. P5 of the arms preregistration:
    every leg must come from one session, and no existing artefact may be overwritten in place.
    A floor swapped under a published contrast leaves every file green and the grading wrong --
    the defect `c30b98048` was filed for."""
    arms.artefact_path("three-arm", "20260910").write_text("{}")

    with pytest.raises(arms.RunRefused, match="already has artefacts"):
        arms.plan(["three-arm", "floor-all"], "20260910")


# ── THE LEG DEPENDENCY, BOTH WAYS ────────────────────────────────────────────────────────────

def test_a_decomposed_floor_without_its_roster_is_refused_but_with_one_is_not(repo):
    """BOTH DIRECTIONS IN ONE CONTROL, because a guard that refuses everything passes every
    one-legged test of a guard.

    `floor-only`/`floor-except` cut the book along the accounts the three-arm run priced. Without
    that artefact they would cut along `run_value_cycle_ab`'s default -- a roster from another day,
    and the result would carry a decomposed label over an undecomposed book."""
    with pytest.raises(arms.RunRefused, match="neither in this run nor already written"):
        arms.plan(["floor-only"], "20260910")

    # ...and the same leg is ADMITTED once the roster exists, by either of its two routes.
    assert arms.plan(["floor-only", "three-arm"], "20260910") == ["three-arm", "floor-only"], (
        "a prerequisite named in the SAME run must satisfy the check, and must be ordered first"
    )
    arms.artefact_path("three-arm", "20260911").write_text("{}")
    assert arms.plan(["floor-only"], "20260911") == ["floor-only"], (
        "a prerequisite already on disk FOR THIS STAMP must satisfy it too -- otherwise resuming "
        "a part-run stamp is impossible and the only way forward is a fresh 8-hour run"
    )


def test_a_decomposed_leg_cuts_along_this_stamps_roster_and_not_a_default(repo):
    """The roster is passed EXPLICITLY. `run_value_cycle_ab --redraw-accounts-from` defaults to
    `value_cycle_ab.json`, which is whatever was last written there -- so omitting the flag is not
    an error anyone sees, it is a decomposition of a different book that looks fine."""
    argv = arms.leg_argv("floor-except", "20260910")

    assert "--redraw-accounts-from" in argv
    assert str(arms.artefact_path("three-arm", "20260910")) in argv
    assert "--redraw-accounts-from" not in arms.leg_argv("three-arm", "20260910"), (
        "the three-arm leg has no roster to cut along -- it is the leg that WRITES one"
    )


def test_the_default_legs_are_what_the_retired_script_ran(repo):
    """Retiring the shell script must change the LAUNCH, not the measurement. Its two legs were
    the three-arm run and the undecomposed floor at seeds 11111,22222,33333."""
    assert list(arms.DEFAULT_LEGS) == ["three-arm", "floor-all"]
    assert arms.DEFAULT_SEEDS == "11111,22222,33333"
    assert "--noise-floor-seeds" in arms.leg_argv("floor-all", "20260829")
    assert "--level-arm" in arms.leg_argv("three-arm", "20260829")


def test_the_hand_rolled_shell_launch_is_gone(repo):
    """The retirement itself. A script that runs the legs without launching them is an invitation
    to start an 8-hour job in the foreground of a bounded tick, and it cannot be made safe from
    inside -- which is why it is deleted rather than fixed."""
    root = Path(__file__).resolve().parents[2]
    assert not (root / "tools" / "run_arms_rerun_detached.sh").exists()


# ── A FAILED LEG ─────────────────────────────────────────────────────────────────────────────

def test_a_failed_leg_skips_its_dependants_and_only_its_dependants(repo):
    """ONE CONTROL OVER THE WHOLE PARTITION, because each outcome here is rare and a run in which
    nothing is ever skipped would pass a per-branch test of the skipping.

    The script this replaces ran its legs unconditionally and printed each rc, which is right for
    two independent legs and wrong for four: a `floor-only` started after a dead `three-arm` reads
    the roster off a file that was never written. But an independent leg must still run -- six
    hours of work is not thrown away because a different leg died."""
    attempted = []

    def _runner(argv, **_kw):
        leg = next(a for a in ("three_arm", "noise_floor_only", "noise_floor_except",
                               "noise_floor") if a in argv[argv.index("--out") + 1])
        attempted.append(leg)
        return types.SimpleNamespace(returncode=1 if leg == "three_arm" else 0)

    rc = arms.run(["three-arm", "floor-all", "floor-only", "floor-except"], "20260910",
                  runner=_runner)

    assert rc != 0, "a run with a dead leg and two skipped ones must not report success"
    assert "three_arm" in attempted and "noise_floor" in attempted, (
        "the independent floor leg was not attempted after an unrelated leg failed -- this run "
        "threw away hours of work it could have banked"
    )
    assert "noise_floor_only" not in attempted and "noise_floor_except" not in attempted, (
        "a decomposed floor was started after the leg that writes its roster had failed"
    )

    log = arms.log_path("20260910").read_text()
    assert "SKIP" in log and "THREE_ARM_RC=1" in log, (
        "the log must say which legs were skipped and why -- the next reader is deciding whether "
        "to relaunch, and a missing artefact alone cannot tell a skip from a crash"
    )


def test_a_clean_run_reports_success_and_writes_every_leg_to_the_stamped_log(repo):
    """The counterfactual for the test above: if `run` returned non-zero regardless, the failure
    assertion there would prove nothing."""
    assert arms.run(["three-arm", "floor-all"], "20260910", runner=_ok) == 0

    log = arms.log_path("20260910").read_text()
    assert "LEG 1/2" in log and "LEG 2/2" in log and "SKIP" not in log
    assert "START" in log and "DONE" in log


def test_progress_goes_to_the_log_and_not_also_to_stdout(repo):
    """OBSERVED IN THE DRAFT, by printing the real launch argv before shipping it.

    `launch_long_job` points the unit's StandardOutput at THIS SAME stamped file. So a `record()`
    that also printed to stdout wrote every START/LEG/RC line TWICE into the log the next reader
    uses to tell a live leg from a dead one -- and put two writers on one file, losing the ordering
    the file exists for.

    BOTH DIRECTIONS, because "print nothing at all" would pass a one-legged version of this: a
    foreground run must still say where the log is, or it looks like it did nothing."""
    said = []
    arms.run(["three-arm", "floor-all"], "20260910", runner=_ok, out=_Sink(said))

    log = arms.log_path("20260910").read_text()
    assert log.count("LEG 1/2") == 1 and log.count("START") == 1, (
        "a progress line landed in the log twice -- under the unit, stdout IS this file"
    )
    assert not any("LEG 1/2" in line for line in said), (
        "per-leg progress went to stdout as well; when launched, that stream is the same file"
    )
    assert any(str(arms.log_path("20260910")) in line for line in said), (
        "a foreground run printed nothing that names the log, so it reads as having done nothing"
    )


def test_the_legs_share_one_session_and_one_log(repo, monkeypatch):
    """WHY THE SCRIPT EXISTED AT ALL, kept. Grading a new contrast against a floor run on another
    day is the defect `c30b98048` was filed for, and a per-leg launch invites exactly that. One
    invocation, one working directory, one appended log."""
    cwds, streams = [], []

    def _runner(argv, cwd=None, stdout=None, **_kw):
        cwds.append(cwd)
        streams.append(stdout)
        return types.SimpleNamespace(returncode=0)

    arms.run(["three-arm", "floor-all"], "20260910", runner=_runner)

    assert cwds == [str(repo), str(repo)]
    assert streams[0] is streams[1] and streams[0] is not None, (
        "the legs wrote to different handles (or to nothing) -- the shell script's one property "
        "worth keeping is that both legs land in one file, in order"
    )
    assert streams[0] is not subprocess.DEVNULL
