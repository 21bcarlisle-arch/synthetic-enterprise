"""The arms re-run: every leg from ONE session, on one clock, to NEW stamped paths.

WHAT THIS REPLACES, AND WHY IT IS PYTHON NOW. `tools/run_arms_rerun_detached.sh` was a committed
shell script whose name promised a detach it did not perform. Nothing in it launched anything: it
`cd`-ed to a hardcoded absolute path, ran two legs, and appended to a log. The detachment lived
entirely in a wrapper the caller had to remember --

    systemd-run --user --unit=arms-rerun-20260829 tools/run_arms_rerun_detached.sh

-- typed out in a preregistration document, with "the stamp changed" as an instruction to a human.
Three failure modes followed from that, and all three are observed rather than imagined:

  * A HAND-TYPED WRAPPER IS A WRAPPER SOMEONE FORGETS. Every long job in this repo that was
    launched without one died at its launcher's cgroup teardown -- five launches of the
    subject-cost measurement, and three more in September. The script could not make itself safe,
    so its correctness rested on the next reader reading the comment at the top.
  * NO LIVENESS RECORD. An 8-hour run that died was noticed by someone looking at a pid, if at
    all. `background.launch_long_job` writes a record `deadmans_switch` re-asks on a timer, and a
    job whose record could not be written is stopped rather than left running and invisible.
  * THE STAMP WAS A LITERAL IN THE FILE (`STAMP=20260829`), so the artefact paths were correct on
    exactly one day. On 2026-09-03 the instruction was to edit the script before running it. A
    stamp is a decision, so it is now a REQUIRED argument with no default -- there is no value
    this could pick that would be right tomorrow, and a default would be silently stale.

WHAT DID NOT CHANGE, because it is the reason the script existed at all. All legs run from ONE
invocation, sequentially, on one tree. Grading a new contrast against a floor from another day is
the defect `c30b98048` was filed for, and it is what a per-leg launch invites. The legs are
subprocesses, exactly as the shell ran them: a leg is a full A/B pass and must not share
interpreter state with the one before it.

AND THE LEG SET IS NOW SAYABLE. The script ran two legs; the decomposition the floor feeds needs
four (`all`, `only`, `except` and the three-arm run they bound), and `only`/`except` need the
three-arm artefact's priced roster to cut along. That dependency used to live in a human's head
between two launches. Here it is checked before anything runs for eight hours.
"""
from __future__ import annotations

import argparse
import io
import re
import subprocess
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent

#: The seeds the 2026-08-29 and 2026-09-03 floors were run with. Kept as the default so a re-run
#: is comparable to the artefacts already on disk -- a floor drawn with different seeds is a
#: different measurement wearing the same filename.
DEFAULT_SEEDS = "11111,22222,33333"

#: `three-arm` FIRST, always: the two decomposed floors cut along the roster its artefact names,
#: so a run that omits it can only be graded against a roster from another day. `depends_on` is
#: what makes that a refusal instead of a convention.
LEGS = {
    "three-arm": {
        "artefact": "value_cycle_ab_s1_three_arm_{stamp}.json",
        "argv": ["--level-arm"],
        "depends_on": None,
        "what": "three arms (control, value, level), 3 passes",
    },
    "floor-all": {
        "artefact": "value_cycle_ab_s1_noise_floor_{stamp}.json",
        "argv": ["--level-arm", "--redraw-mode", "all"],
        "depends_on": None,
        "what": "undecomposed noise floor, 3 passes per seed",
    },
    "floor-only": {
        "artefact": "value_cycle_ab_s1_noise_floor_only_{stamp}.json",
        "argv": ["--level-arm", "--redraw-mode", "only"],
        "depends_on": "three-arm",
        "what": "noise floor re-drawing ONLY the households the arm priced",
    },
    "floor-except": {
        "artefact": "value_cycle_ab_s1_noise_floor_except_{stamp}.json",
        "argv": ["--level-arm", "--redraw-mode", "except"],
        "depends_on": "three-arm",
        "what": "noise floor re-drawing EVERYBODY ELSE",
    },
}

#: What `run_arms_rerun_detached.sh` ran, preserved as the default so retiring it changes the
#: launch and not the measurement. The decomposition legs are opt-in because they cost ~2h24 each.
DEFAULT_LEGS = ("three-arm", "floor-all")


class RunRefused(RuntimeError):
    """A run that did not start, carrying WHY. Never raised once a leg is under way."""


def artefact_path(leg: str, stamp: str) -> Path:
    return _REPO / "docs" / "observability" / LEGS[leg]["artefact"].format(stamp=stamp)


def log_path(stamp: str) -> Path:
    return _REPO / "docs" / "observability" / "arms_rerun_{}.log".format(stamp)


def check_stamp(stamp: str) -> str:
    """A stamp must be a date-shaped token, optionally suffixed.

    Not cosmetic: the stamp IS the artefact name, and a typo produces a file no reader of the
    decomposition will ever find rather than an error anyone sees. `20260830b` is real and on
    disk, so the suffix is allowed."""
    if not re.fullmatch(r"\d{8}[a-z]?", stamp):
        raise RunRefused(
            "stamp {!r} is not YYYYMMDD (optionally with a single-letter suffix). The stamp is "
            "the artefact name, so a malformed one writes a file nothing looks for.".format(stamp))
    return stamp


def plan(legs, stamp: str) -> list:
    """The legs to run, in order, or a refusal naming what is missing.

    REFUSES BEFORE ANYTHING RUNS FOR HOURS, on both of the two ways this goes wrong silently:

      * AN EXISTING ARTEFACT. Re-running a stamp overwrites a leg in place, and the preregistration
        for this measurement names that as a refutation condition -- a floor swapped under a
        published contrast leaves the file green and the grading wrong.
      * A DECOMPOSED FLOOR WITH NO ROSTER. `only` and `except` cut the book along the accounts the
        three-arm run priced. Without that leg in this session or already on disk for this stamp,
        they would cut along whatever `run_value_cycle_ab`'s default artefact happens to hold --
        which is a roster from another day, wearing a decomposed label.
    """
    unknown = [leg for leg in legs if leg not in LEGS]
    if unknown:
        raise RunRefused("no such leg: {} (have: {})".format(
            ", ".join(sorted(unknown)), ", ".join(LEGS)))
    if not legs:
        raise RunRefused("no legs to run")
    ordered = [leg for leg in LEGS if leg in set(legs)]

    existing = [leg for leg in ordered if artefact_path(leg, stamp).exists()]
    if existing:
        raise RunRefused(
            "stamp {} already has artefacts for {} -- refusing to overwrite a leg in place. "
            "Every leg must come from ONE session on one tree; a re-run under the same stamp "
            "leaves a floor from one clock beside a contrast from another. Use a new stamp "
            "(a letter suffix is fine: {}b).".format(stamp, ", ".join(existing), stamp))

    for leg in ordered:
        need = LEGS[leg]["depends_on"]
        if need and need not in ordered and not artefact_path(need, stamp).exists():
            raise RunRefused(
                "leg `{}` cuts the book along the roster `{}` names, and `{}` is neither in this "
                "run nor already written for stamp {}. Cutting along another day's roster is a "
                "decomposition of a different book.".format(leg, need, need, stamp))
    return ordered


def leg_argv(leg: str, stamp: str) -> list:
    """The `run_value_cycle_ab` command line for one leg. Built here so a test can read it."""
    spec = LEGS[leg]
    argv = [sys.executable, "-m", "tools.run_value_cycle_ab", *spec["argv"],
            "--out", str(artefact_path(leg, stamp))]
    if leg.startswith("floor-"):
        argv += ["--noise-floor-seeds", DEFAULT_SEEDS]
    if spec["depends_on"]:
        argv += ["--redraw-accounts-from", str(artefact_path(spec["depends_on"], stamp))]
    return argv


def run(legs, stamp: str, *, runner=subprocess.run, out=None) -> int:
    """Run each leg in turn, in this process's session. Returns 0 only if every leg succeeded.

    A FAILED LEG SKIPS ITS DEPENDANTS AND NOTHING ELSE. The shell script this replaces ran both
    of its legs unconditionally and printed each rc, which was right for two independent legs and
    is wrong for four: a `floor-only` started after a dead `three-arm` would read the roster off
    an absent file, or off a stale one, and produce a decomposition of some other book. Independent
    legs still run -- eight hours of work must not be thrown away because one leg died.

    EVERY PROGRESS LINE GOES TO THE LOG AND NOT TO STDOUT, which is not a style choice. When this
    module is launched, `launch_long_job` points the unit's StandardOutput at THIS SAME FILE, so a
    line written both ways appears twice -- and the first draft of this function did exactly that,
    caught by printing the real launch argv before shipping it. Two writers on one file also lose
    the ordering the file exists for. stdout gets one pointer line at each end, so a foreground
    run says where to look instead of saying nothing (which is what the shell script did)."""
    def say(line: str) -> None:
        print(line, file=out or sys.stdout, flush=True)

    ordered = plan(legs, stamp)
    log = log_path(stamp)
    log.parent.mkdir(parents=True, exist_ok=True)
    failed, skipped = [], []
    say("arms re-run {}: {} leg(s) -> {} (follow it there; this stream stays quiet)".format(
        stamp, len(ordered), log))

    with open(str(log), "a", encoding="utf-8") as handle:
        def record(line: str) -> None:
            handle.write(line + "\n")
            handle.flush()

        record("START {} stamp={} legs={}".format(_now(), stamp, ",".join(ordered)))
        for index, leg in enumerate(ordered, 1):
            need = LEGS[leg]["depends_on"]
            if need in failed:
                skipped.append(leg)
                record("=== SKIP {}/{}: {} -- its prerequisite `{}` failed, and cutting along a "
                       "roster that leg never wrote decomposes a different book ===".format(
                           index, len(ordered), leg, need))
                continue
            argv = leg_argv(leg, stamp)
            record("=== LEG {}/{}: {} ({}) -> {} ===".format(
                index, len(ordered), leg, LEGS[leg]["what"], artefact_path(leg, stamp).name))
            res = runner(argv, cwd=str(_REPO), stdout=handle, stderr=subprocess.STDOUT)
            if res.returncode != 0:
                failed.append(leg)
            record("{}_RC={} at {}".format(leg.upper().replace("-", "_"), res.returncode, _now()))
        done = "DONE {} -- {} ran, {} failed{}".format(
            _now(), len(ordered) - len(skipped), len(failed),
            ", {} skipped".format(len(skipped)) if skipped else "")
        record(done)

    say(done)
    return 1 if (failed or skipped) else 0


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def launch(legs, stamp: str, *, out=None) -> int:
    """Hand the whole session to `background.launch_long_job` and return.

    THE POINT OF THIS FILE. The shell script could not do this for itself, so its detachment was
    a line in a document; here the job's own module performs it, and a launch that cannot be
    recorded is stopped rather than left running unseen. The plan is checked FIRST, in this
    process, so a refusal that costs nothing is not deferred into a unit whose only symptom is a
    log file nobody is watching."""
    ordered = plan(legs, stamp)
    from background import launch_long_job

    def say(line: str) -> None:
        print(line, file=out or sys.stdout, flush=True)

    # The LAST leg's artefact is what the liveness record is settled against: the record must not
    # read as complete while three more legs are still running.
    artefact = artefact_path(ordered[-1], stamp)
    narration = io.StringIO()
    try:
        launch_long_job.launch(
            "arms-rerun-{}".format(stamp),
            [sys.executable, "-m", "tools.run_arms_rerun", "--stamp", stamp,
             *[arg for leg in ordered for arg in ("--leg", leg)]],
            artefact=str(artefact), workdir=str(_REPO), log=str(log_path(stamp)),
            description="arms re-run {} ({} legs, ~{}h)".format(
                stamp, len(ordered), 1 + 2 * (len(ordered) - 1)),
            out=narration)
    except launch_long_job.LaunchRefused as exc:
        say("REFUSED: {}".format(exc))
        return 1
    for line in narration.getvalue().splitlines():
        say(line)
    return 0


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the value-cycle arms comparison, all legs from one session.")
    parser.add_argument("--stamp", required=True,
                        help="YYYYMMDD (optionally +one letter). REQUIRED and never defaulted: "
                             "the stamp is the artefact name, and the literal this replaced was "
                             "correct on exactly one day")
    parser.add_argument("--leg", action="append", dest="legs", choices=sorted(LEGS),
                        help="repeatable; default is {}".format(", ".join(DEFAULT_LEGS)))
    parser.add_argument("--launch", action="store_true",
                        help="hand the session to background.launch_long_job -- a transient user "
                             "unit with a liveness record. THE launch from a bounded tick: an "
                             "in-process background job dies with its launcher's cgroup")
    args = parser.parse_args(argv)

    try:
        stamp = check_stamp(args.stamp)
        legs = args.legs or list(DEFAULT_LEGS)
        if args.launch:
            return launch(legs, stamp)
        return run(legs, stamp)
    except RunRefused as exc:
        print("REFUSED: {}".format(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
