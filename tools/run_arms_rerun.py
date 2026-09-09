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

AND SO IS THE SEED COUNT (2026-09-09). `DEFAULT_SEEDS` was reached straight from `leg_argv`, so
running a floor at any n but three meant editing this file -- the same defect as the hardcoded
`STAMP=20260829` above, one field along, and it bound the moment `selection_gbp` was published at
n=3 with a mean of -426.96 against an sd of 2,291.98. The default is unchanged, so a re-run without
the flag is still comparable to every floor on disk; the count is now a REFUSABLE argument, and the
hours estimate the liveness record carries is derived from it rather than from the leg count (see
`_hours`).

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


def check_seeds(seeds: str) -> str:
    """The seed list a floor leg is drawn with, checked before hours are spent on a bad one.

    THE SEED COUNT IS A DECISION AND IT USED TO BE UNSAYABLE. `DEFAULT_SEEDS` was reached directly
    from `leg_argv`, so the only way to run a floor at any n but three was to edit this file --
    which is the same shape as the hardcoded `STAMP=20260829` the module docstring above describes
    retiring, one field along. It became load-bearing on 2026-09-09: `selection_gbp` was published
    at n=3 with a mean of -426.96 against an sd of 2,291.98, and n was the only input that could
    move it.

    TWO REFUSALS, both for defects that produce a HEALTHY-LOOKING artefact rather than an error:

      * FEWER THAN TWO. `run_value_cycle_ab.noise_floor` refuses this itself -- but it refuses it
        an hour in, after `three-arm` has already run, and only for the leg it reaches. Refusing
        here costs nothing and refuses before anything starts.
      * A REPEATED SEED. The spread is taken over the rows, and a duplicated seed is the SAME row
        twice: it inflates `n`, shrinks the SEM by a factor that measures nothing, and every field
        downstream reads as a better-resolved measurement. Nothing further down looks -- the rows
        are well-formed and their arithmetic is consistent -- so this is the one that would have
        been believed.
    """
    tokens = [tok.strip() for tok in seeds.split(",") if tok.strip()]
    try:
        values = [int(tok) for tok in tokens]
    except ValueError:
        raise RunRefused(
            "seeds {!r} is not a comma-separated list of integers. The seeds ARE the "
            "measurement; a malformed list is hours spent drawing something nobody asked "
            "for.".format(seeds)) from None
    if len(values) < 2:
        raise RunRefused(
            "a noise floor needs at least two seeds; got {}. One seed is a run, not a spread, and "
            "the leg would refuse an hour in rather than now.".format(len(values)))
    repeated = sorted({v for v in values if values.count(v) > 1})
    if repeated:
        raise RunRefused(
            "seed(s) {} appear more than once in {!r}. A repeated seed is the same row twice: it "
            "raises `n` and shrinks the SEM without adding an observation, and the artefact it "
            "writes is well-formed, so nothing downstream can tell.".format(
                ", ".join(str(v) for v in repeated), seeds))
    return ",".join(str(v) for v in values)


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


def leg_argv(leg: str, stamp: str, seeds: str = DEFAULT_SEEDS) -> list:
    """The `run_value_cycle_ab` command line for one leg. Built here so a test can read it."""
    spec = LEGS[leg]
    argv = [sys.executable, "-m", "tools.run_value_cycle_ab", *spec["argv"],
            "--out", str(artefact_path(leg, stamp))]
    if leg.startswith("floor-"):
        argv += ["--noise-floor-seeds", seeds]
    if spec["depends_on"]:
        argv += ["--redraw-accounts-from", str(artefact_path(spec["depends_on"], stamp))]
    return argv


def run(legs, stamp: str, *, seeds: str = DEFAULT_SEEDS, runner=subprocess.run, out=None) -> int:
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

        # THE SEEDS GO IN THE LOG'S FIRST LINE, beside the legs, because the seed list is the only
        # input to a floor leg that the artefact's FILENAME does not carry -- two runs at the same
        # stamp-shaped name and different n are otherwise told apart only by opening them.
        record("START {} stamp={} legs={} seeds={}".format(
            _now(), stamp, ",".join(ordered), seeds))
        for index, leg in enumerate(ordered, 1):
            need = LEGS[leg]["depends_on"]
            if need in failed:
                skipped.append(leg)
                record("=== SKIP {}/{}: {} -- its prerequisite `{}` failed, and cutting along a "
                       "roster that leg never wrote decomposes a different book ===".format(
                           index, len(ordered), leg, need))
                continue
            argv = leg_argv(leg, stamp, seeds)
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


#: WHAT A LEG ACTUALLY TOOK, from the kill that established it. systemd's own accounting for
#: `se-noise-floor-20260903` (`--redraw-mode all`, three seeds): 1h 09min 07s CPU over 1h 09min 36s
#: wall -- and it was OOM-killed at ~90%, so the full three seeds is ~1h 17m, i.e. ~0.43h per seed.
#: A three-arm leg is three passes and lands near an hour. Quoted here rather than in the format
#: string because the estimate is what a reader plans a day around.
_HOURS_PER_FLOOR_SEED = 0.43
_HOURS_PER_THREE_ARM = 1.0


def _hours(ordered, seeds: str) -> str:
    """Roughly how long this session runs, as a string for the liveness record's description.

    THE OLD ESTIMATE WAS `1 + 2 * (legs - 1)`, which was right only while every floor leg carried
    exactly three seeds -- it counted LEGS and a floor leg's cost is per SEED. A nine-seed floor
    reported as "~1h" is a run that reads as overdue after 90 minutes and gets relaunched on top
    of itself."""
    n = len([tok for tok in seeds.split(",") if tok.strip()])
    total = sum(_HOURS_PER_THREE_ARM if leg == "three-arm" else _HOURS_PER_FLOOR_SEED * n
                for leg in ordered)
    return "{:.1f}".format(total)


def launch(legs, stamp: str, *, seeds: str = DEFAULT_SEEDS, out=None) -> int:
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
            # THE SEEDS ARE NAMED EXPLICITLY for the same reason the legs are: the unit's own
            # command line is the record of what was run, and a child inheriting the default would
            # stop describing its own run the day the default moves.
            [sys.executable, "-m", "tools.run_arms_rerun", "--stamp", stamp, "--seeds", seeds,
             *[arg for leg in ordered for arg in ("--leg", leg)]],
            artefact=str(artefact), workdir=str(_REPO), log=str(log_path(stamp)),
            description="arms re-run {} ({} legs, {} seed(s), ~{}h)".format(
                stamp, len(ordered), len(seeds.split(",")), _hours(ordered, seeds)),
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
    parser.add_argument("--seeds", default=DEFAULT_SEEDS,
                        help="comma-separated seeds for the floor legs; default {} -- the list "
                             "every floor on disk was drawn with, so a re-run at the default is "
                             "comparable to them. Each seed costs three full passes (~{:.0f} min), "
                             "and the seed count is what sets the SEM on the spread the page "
                             "publishes".format(DEFAULT_SEEDS, _HOURS_PER_FLOOR_SEED * 60))
    parser.add_argument("--launch", action="store_true",
                        help="hand the session to background.launch_long_job -- a transient user "
                             "unit with a liveness record. THE launch from a bounded tick: an "
                             "in-process background job dies with its launcher's cgroup")
    args = parser.parse_args(argv)

    try:
        stamp = check_stamp(args.stamp)
        seeds = check_seeds(args.seeds)
        legs = args.legs or list(DEFAULT_LEGS)
        if args.launch:
            return launch(legs, stamp, seeds=seeds)
        return run(legs, stamp, seeds=seeds)
    except RunRefused as exc:
        print("REFUSED: {}".format(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
