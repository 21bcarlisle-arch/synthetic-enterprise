"""R15 proofs for the only legal waiter.

THE INCIDENT THIS FILE EXISTS FOR (2026-08-27, third of its kind in one week). A background
shell ran::

    until ! pgrep -f "pytest tests/simulation/test_live_population" >/dev/null;
    do sleep 15; done

for twelve hours. The pytest it named had finished long before. `pgrep -f` matches the full
command line and a background shell is `bash -c '<the whole loop>'`, so the pattern was
sitting in the waiter's OWN cmdline: the loop was matching itself, and its exit condition
was unreachable from the first second.

The tests below are ordered by what they defend, hardest first:

  1. THE INCIDENT ITSELF, unmocked -- a real subprocess whose command line contains the
     pattern, asserted to terminate in seconds with NEVER_STARTED. If `tools/wait_for.py`
     ever regresses to self-matching, this test hangs and then fails on its own timeout,
     which is the correct shape: the defect IS a hang.
  2. the deadline is not optional and not unbounded;
  3. absent, present-then-gone, and still-running are three different answers -- a waiter
     that called an absent subject "finished" would report success for a run that never
     happened, in the same second, which reads as a fast pass rather than a mistake;
  4. an unreadable probe is NOT an absent subject (the standing lesson about controls that
     refuse on input they never read, applied in the other direction: here the danger is
     reporting DONE because we could not look);
  5. and the partner tests for every narrowing, because a filter that also silences the
     normal shape is worse than the over-trigger it fixed.
"""
from __future__ import annotations

import subprocess
import sys

import pytest

from tools import wait_for as W

# ---------------------------------------------------------------------------
# 1. the incident, reproduced without mocks
# ---------------------------------------------------------------------------

# A token that appears NOWHERE else in the repo or on this box, so the only process whose
# command line contains it is the one the test launches.
_TOKEN = "ZZ_WAITFOR_SELFMATCH_PROBE_8f21c4"


def _waiter_under_a_real_bash(subject: str, deadline: float = 30.0):
    """Launch the waiter the way the incident launched it: under a shell that STAYS.

    The trailing `; exit $?` is load-bearing twice over, and both halves cost a failing
    test to learn. `bash -c "cmd"` with a single simple command execs itself away, so the
    bash disappears and python becomes the direct child -- which would leave the ancestor
    half of the exclusion untested while looking green. A compound command forces bash to
    remain as a real parent carrying the pattern on its own cmdline, which is precisely the
    twelve-hour shape. And it must be `exit $?` rather than `true`: the first draft used
    `true`, which kept bash resident but returned 0 no matter what the waiter said -- so
    the FINISHED assertion below would have passed even against a waiter that reported
    NEVER_STARTED.
    """
    return subprocess.run(
        ["bash", "-c",
         "{} -m tools.wait_for --pattern {} --subject '{}' --deadline {} --poll 0.5; exit $?"
         .format(sys.executable, _TOKEN, subject, deadline)],
        capture_output=True, text=True, timeout=deadline + 25)


def test_a_pattern_that_matches_only_the_waiter_ENDS_instead_of_waiting_forever():
    """THE 2026-08-27 DEFECT, end to end, no fakes.

    Both the shell and the python process under it carry the pattern on their command
    lines. That is exactly the shape that ran for twelve hours. The assertion is that it
    now takes under a second and says the subject is not running, rather than matching
    itself forever.

    If the exclusion regresses this fails by DEADLINE (or by the subprocess timeout) rather
    than hanging the suite -- the correct shape, because the defect IS a hang.
    """
    r = _waiter_under_a_real_bash("a subject that does not exist")
    assert r.returncode == W.EXIT_CODES[W.NEVER_STARTED], r.stdout + r.stderr
    assert W.NEVER_STARTED in r.stdout
    assert "2 matches excluded as this waiter or its ancestors" in r.stdout, (
        "expected BOTH the waiter and its parent shell to be struck out. One match means "
        "the shell exec'd itself away and the ancestor half of the exclusion -- the half "
        "that actually failed in the incident -- was never exercised:\n" + r.stdout)


def test_a_REAL_subject_is_still_seen_through_the_exclusion():
    """THE PARTNER, and the one that matters most.

    Excluding self and ancestors is a narrowing. A narrowing that also hid the genuine
    subject would make every wait return NEVER_STARTED instantly -- the tool would look
    fast and reliable while never waiting for anything at all.

    The sleeper carries the token as a real ARGV ELEMENT rather than a shell comment: a
    comment is consumed by bash and never reaches any command line, so the first draft of
    this test was watching for a process that did not exist under that name.
    """
    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(8)", _TOKEN])
    try:
        r = _waiter_under_a_real_bash("the test sleeper", deadline=40.0)
    finally:
        if sleeper.poll() is None:
            sleeper.kill()
        sleeper.wait()
    assert r.returncode == W.EXIT_CODES[W.FINISHED], r.stdout + r.stderr
    assert "the test sleeper" in r.stdout


def test_MUTATION_excluding_only_self_reproduces_the_incident_and_the_deadline_still_caps_it():
    """R15: the control fired on its own named defect, and both defences are visible.

    Run the real waiter with the exclusion deliberately mutated to `{os.getpid()}` -- the
    obvious wrong version, and the one that would have struck out nothing on 2026-08-27
    because the pattern lived on the PARENT's command line. It duly matches its own parent
    shell and waits, which is Wednesday's twelve hours in miniature.

    And then it stops, at six seconds, saying what it was waiting for. That is the second
    defence doing its job: even with the exclusion wrong, a deadline is the difference
    between a bounded wrong answer and a shell indicator that means nothing for half a day.
    """
    r = subprocess.run(
        ["bash", "-c",
         "{} -c 'import os, sys; from tools import wait_for as W; "
         "print(W.wait(\"the mutated waiter\", 6, "
         "W.pattern_probe(sys.argv[1], exclude={{os.getpid()}}), poll_s=0.5)[\"verdict\"])' "
         "{}; exit $?".format(sys.executable, _TOKEN)],
        capture_output=True, text=True, timeout=60)
    assert W.DEADLINE in r.stdout, (
        "the mutated exclusion should match the parent shell and run to the deadline; if "
        "this says NEVER_STARTED the test is no longer exercising the defect:\n"
        + r.stdout + r.stderr)


def test_self_and_ancestors_includes_the_PARENT_not_just_this_process():
    """The single line that made the fix work.

    A background shell spawns `bash -c '<command>'` and python as its CHILD, so the pattern
    lives on the parent's command line. An exclusion set of `{os.getpid()}` would have
    struck out nothing at all on 2026-08-27.
    """
    chain = {10: 9, 9: 8, 8: 1, 1: None}
    assert W.self_and_ancestors(10, ppid_of=chain.get) == {10, 9, 8, 1}


def test_the_ancestor_walk_is_bounded_so_a_proc_cycle_cannot_hang_the_anti_hang_tool():
    """/proc can be read mid-reparent. A cycle here would hang the tool inside the function
    written to stop hangs, which is the kind of irony that costs another twelve hours."""
    assert len(W.self_and_ancestors(1, ppid_of=lambda _p: 2 if _p == 1 else 1, limit=8)) <= 8


def test_an_unreadable_ppid_stops_the_walk_rather_than_raising():
    """A process that exits mid-walk makes /proc/<pid>/status vanish. The exclusion set
    being short is survivable; the tool crashing before it starts waiting is not."""
    assert W.self_and_ancestors(5, ppid_of=lambda _p: None) == {5}


# ---------------------------------------------------------------------------
# 2. the deadline is not optional
# ---------------------------------------------------------------------------

def test_a_waiter_with_no_deadline_cannot_be_LAUNCHED():
    """`required=True` is the load-bearing word in the whole module. Every one of the three
    incidents this week was a loop that could outlive its subject."""
    with pytest.raises(SystemExit):
        W.build_parser().parse_args(["--pattern", "x", "--subject", "y"])


def test_a_waiter_with_no_subject_cannot_be_launched_either():
    """The director asked for two things: a deadline, and that it SAY what it waits for.
    An unnamed waiter's output file is the thing that told neither of us anything."""
    with pytest.raises(SystemExit):
        W.build_parser().parse_args(["--pattern", "x", "--deadline", "10"])


@pytest.mark.parametrize("bad", [0, -1, -0.5])
def test_a_non_positive_deadline_is_refused(bad):
    with pytest.raises(ValueError, match="positive deadline"):
        W.wait("s", bad, probe=lambda: (True, ""))


def test_a_deadline_past_the_ceiling_is_refused():
    """A week-long deadline is the defect wearing an argument."""
    with pytest.raises(ValueError, match="ceiling"):
        W.wait("s", W.MAX_DEADLINE_SECONDS + 1, probe=lambda: (True, ""))


def test_the_ceiling_is_not_so_tight_it_refuses_real_work():
    """The partner. The slowest legitimate subject in this repo is a full decade sim run;
    a ceiling below that would push callers back to hand-rolled loops, which is the
    mechanism this tool exists to replace."""
    assert W.MAX_DEADLINE_SECONDS >= 3600


def test_the_cli_refuses_a_bad_deadline_with_a_reason_rather_than_a_traceback():
    assert W.main(["--pattern", "x", "--subject", "y", "--deadline", "-3"]) \
        == W.EXIT_CODES[W.UNREADABLE]


def test_pid_and_pattern_are_mutually_exclusive_and_one_is_required():
    with pytest.raises(SystemExit):
        W.build_parser().parse_args(["--subject", "y", "--deadline", "10"])
    with pytest.raises(SystemExit):
        W.build_parser().parse_args(
            ["--pid", "1", "--pattern", "x", "--subject", "y", "--deadline", "10"])


# ---------------------------------------------------------------------------
# 3. absent / finished / still-running are three answers
# ---------------------------------------------------------------------------

class _Clock:
    """A monotonic clock the test drives, so deadline behaviour is asserted rather than
    slept through."""

    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds


def _run(states, deadline=100.0, **kw):
    """Drive `wait` through a scripted sequence of presence readings."""
    clock = _Clock()
    seq = list(states)
    emitted = []

    def probe():
        return (seq.pop(0) if seq else seq_last[0]), "detail"

    seq_last = [states[-1]]
    return W.wait("the subject", deadline, probe, clock=clock, sleep=clock.sleep,
                  emit=emitted.append, poll_s=1.0, heartbeat_s=0, **kw), emitted


def test_a_subject_that_was_never_there_is_NEVER_STARTED_not_FINISHED():
    """THE ORPHAN CASE. Wednesday's shell was waiting for something already over. Calling
    that FINISHED would report success for a run that never happened -- and report it
    instantly, which reads as a very fast pass rather than a mistake."""
    outcome, _ = _run([False])
    assert outcome["verdict"] == W.NEVER_STARTED
    assert outcome["ever_present"] is False
    assert outcome["exit_code"] == 2


def test_a_subject_that_ran_and_stopped_is_FINISHED():
    outcome, _ = _run([True, True, False])
    assert outcome["verdict"] == W.FINISHED
    assert outcome["exit_code"] == 0


def test_a_subject_still_running_at_the_deadline_is_DEADLINE_and_the_loop_ENDS():
    outcome, _ = _run([True], deadline=10.0)
    assert outcome["verdict"] == W.DEADLINE
    assert outcome["exit_code"] == 1
    assert outcome["waited_seconds"] >= 10.0


def test_start_grace_lets_a_subject_that_has_not_launched_yet_appear():
    """The narrowing's partner: refusing instantly is right for an orphan and wrong for a
    subject we raced. `--start-grace` is how a caller says which they expect."""
    outcome, _ = _run([False, False, True, True, False], start_grace_s=5.0)
    assert outcome["verdict"] == W.FINISHED


def test_start_grace_still_EXPIRES_rather_than_waiting_forever():
    outcome, _ = _run([False], start_grace_s=5.0, deadline=100.0)
    assert outcome["verdict"] == W.NEVER_STARTED
    assert outcome["waited_seconds"] >= 5.0


def test_the_wait_uses_a_MONOTONIC_clock():
    """A wall clock going backwards -- NTP correction, DST -- would push the deadline out
    every time it stepped, which is the one failure this tool must not have."""
    import inspect
    assert "monotonic" in inspect.signature(W.wait).parameters["clock"].default.__name__


# ---------------------------------------------------------------------------
# 4. an unreadable probe is not an absent subject
# ---------------------------------------------------------------------------

def test_a_probe_that_cannot_be_RUN_reports_UNREADABLE_not_FINISHED():
    """The dangerous direction for a waiter is the opposite of the usual one: reporting
    DONE because we could not look would tell a caller a run had completed when it had
    not, and the caller's next move is to act on a result that does not exist."""
    def broken():
        raise W.ProbeUnreadable("pgrep is not on this box")

    outcome = W.wait("s", 10.0, broken, clock=_Clock(), sleep=lambda _s: None,
                     emit=lambda _m: None)
    assert outcome["verdict"] == W.UNREADABLE
    assert outcome["exit_code"] == 3
    assert "pgrep" in outcome["detail"]


def test_an_unreadable_probe_is_reported_even_after_the_subject_HAS_been_seen():
    """Mid-wait breakage is the worse case: `ever_present` is true, so a naive reading of
    "not present any more" would call it FINISHED."""
    seen = [True]

    def flaky():
        if seen.pop() if seen else False:
            return True, ""
        raise W.ProbeUnreadable("gone blind")

    outcome = W.wait("s", 10.0, flaky, clock=_Clock(), sleep=lambda _s: None,
                     emit=lambda _m: None)
    assert outcome["verdict"] == W.UNREADABLE
    assert outcome["ever_present"] is True


@pytest.mark.parametrize("rc", [2, 127, -9])
def test_a_pgrep_that_exits_abnormally_is_unreadable(rc):
    with pytest.raises(W.ProbeUnreadable):
        W.matching_pids("x", set(), runner=lambda _p: (rc, ""))


def test_pgrep_exit_1_is_an_ANSWER_not_a_failure():
    """The partner, and the one that would break everything if missed: pgrep exits 1 for
    "no matches", which is the single most common outcome this tool sees."""
    assert W.matching_pids("x", set(), runner=lambda _p: (1, "")) == ([], 0)


def test_an_oserror_from_pgrep_becomes_ProbeUnreadable_rather_than_escaping():
    def boom(_pattern):
        raise OSError("no such binary")

    with pytest.raises(W.ProbeUnreadable, match="could not be run"):
        W.matching_pids("x", set(), runner=boom)


# ---------------------------------------------------------------------------
# 5. matching, and the partners for each narrowing
# ---------------------------------------------------------------------------

def test_excluded_pids_are_struck_out_but_still_COUNTED():
    """The raw count is what lets the detail line say "3 matches excluded as this waiter"
    instead of leaving a reader to wonder whether the probe ran at all."""
    out = "10 python -m thing\n11 python -m thing\n12 python -m thing\n"
    kept, raw = W.matching_pids("thing", {10, 11}, runner=lambda _p: (0, out))
    assert kept == [12]
    assert raw == 3


def test_a_pgrep_process_is_not_a_subject():
    """The act of looking is not the thing looked for."""
    out = "10 pgrep -af pytest\n11 /usr/bin/python3 -m pytest tests/\n"
    kept, _ = W.matching_pids("pytest", set(), runner=lambda _p: (0, out))
    assert kept == [11]


def test_the_noise_filter_only_looks_at_argv0():
    """THE PARTNER FOR THAT NARROWING, and the reason it is written as a basename check
    rather than a substring one. A real subject whose command line merely CONTAINS the word
    grep must stay visible -- filtering it would report FINISHED for a running process,
    which is the most expensive wrong answer this tool can give."""
    out = "11 /usr/bin/python3 -m pytest tests/test_grep_helpers.py\n"
    kept, _ = W.matching_pids("pytest", set(), runner=lambda _p: (0, out))
    assert kept == [11]


def test_a_malformed_pgrep_line_is_skipped_rather_than_crashing_the_wait():
    out = "not-a-pid something\n\n11 python -m thing\n"
    kept, raw = W.matching_pids("thing", set(), runner=lambda _p: (0, out))
    assert kept == [11] and raw == 1


def test_the_exclusion_set_is_computed_ONCE_and_not_per_poll():
    """If this process were reparented to init mid-wait, recomputing the ancestry would
    drop the real ancestor and the waiter could start matching a sibling shell that merely
    carries the same words."""
    calls = []

    def matcher(pattern, exclude):
        calls.append(frozenset(exclude))
        return ([1], 1)

    probe = W.pattern_probe("x", exclude={7, 8}, matcher=matcher)
    for _ in range(3):
        probe()
    assert calls == [frozenset({7, 8})] * 3


# ---------------------------------------------------------------------------
# 6. it says what it is waiting for
# ---------------------------------------------------------------------------

def test_the_first_line_names_the_subject_and_the_deadline():
    """Wednesday's output file was empty. Whoever finds this one should learn what it is
    for from its first line, without reading the command that spawned it."""
    _, emitted = _run([False])
    assert "WAITING for the subject" in emitted[0]
    assert "deadline" in emitted[0]


@pytest.mark.parametrize("states,expected", [([False], W.NEVER_STARTED),
                                             ([True, False], W.FINISHED)])
def test_every_verdict_line_carries_the_subject_and_the_elapsed_time(states, expected):
    _, emitted = _run(states)
    assert expected in emitted[-1]
    assert "the subject" in emitted[-1]
    assert "s waiting for" in emitted[-1]


def test_the_heartbeat_repeats_the_subject_and_the_remaining_budget():
    """A shell indicator that has been spinning for an hour should be answerable by reading
    the last line of its output, not by reconstructing what launched it."""
    clock = _Clock()
    emitted = []
    W.wait("the long thing", 100.0, lambda: (True, "pid 42"), clock=clock,
           sleep=clock.sleep, emit=emitted.append, poll_s=10.0, heartbeat_s=30.0)
    beats = [m for m in emitted if m.startswith("still waiting")]
    assert beats, emitted
    assert "the long thing" in beats[0]
    assert "of 100s" in beats[0]


def test_a_zero_heartbeat_silences_it_without_silencing_the_verdict():
    _, emitted = _run([True, True, False])
    assert not [m for m in emitted if m.startswith("still waiting")]
    assert W.FINISHED in emitted[-1]


# ---------------------------------------------------------------------------
# 7. --pid, the shape that cannot self-match at all
# ---------------------------------------------------------------------------

def test_pid_probe_sees_a_live_process():
    assert W.pid_probe(1)()[0] is True


def test_pid_probe_reports_a_dead_pid_as_absent():
    assert W.pid_probe(4194303)()[0] is False


def test_pid_liveness_uses_proc_rather_than_signal_zero():
    """`os.kill(pid, 0)` raises PermissionError for a live process owned by someone else,
    and a process we may not signal is still very much not finished."""
    import inspect
    assert "/proc/" in inspect.getsource(W.pid_is_alive)
