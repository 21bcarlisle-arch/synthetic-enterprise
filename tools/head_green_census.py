"""Is HEAD actually green? Measure it, instead of inferring it from a scoped gate.

WHY THIS EXISTS
---------------
On 2026-08-12 a full unscoped run of the publish-gate marker expression found EIGHT failing
tests among 24,204, all pre-existing, none of which any routine control was shaped to see:

  * `pre_commit_test_gate` / `surgical_land` select tests by NAME STEM from the changed paths,
    so a change to `background/finding_severity.py` can never reach a census in `tests/design/`.
  * the operational-layer check runs `-m "operational or join_report_only or scale_report_only"`
    -- the exact complement of the set those eight lived in.
  * `process_run_complete`'s publish gate carries `-x`, so it stops at the first failure. That
    day it stopped on an unrelated seat-guard red and left 1,121 tests unrun, reporting one name
    and hiding six.

So "HEAD is green" had never been measured. What was measured was "the tests name-adjacent to
the last diff are green", which is a much weaker claim wearing the same words.

WHAT THIS DOES, AND THE TWO DESIGN CHOICES THAT MATTER
------------------------------------------------------
1. **No `-x`.** Fail-fast is right for a commit gate and wrong for a health measurement. The
   whole value here is the COMPLETE list; stopping at the first red reproduces the defect.

2. **Alarm on the DELTA, not the absolute count.** A standing red set that nobody has
   dispositioned becomes wallpaper within a week, and then the control is decoration. NEW reds
   -- tests failing now that were not in the committed baseline -- are the signal. Tests that
   have started passing are reported too, because a baseline nobody prunes rots into a licence
   to stay red.

The baseline is a COMMITTED file, not a self-updating one. Nothing here writes it: a control
that quietly absorbs its own new failures into its baseline cannot fail, which is the whole
R15 anti-pattern. Updating it is a human act with a commit message attached.

DELIBERATELY NOT A COMMIT GATE. Do not wire this into the pre-commit path: a 25-minute gate
gets bypassed, and hook-bypass is a wall. The per-commit gate being scoped is a legitimate
design; the defect was that nothing else was unscoped.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from background.head_red_baseline import BASELINE_PATH, load_baseline

PROJECT_DIR = Path(__file__).resolve().parent.parent

# The acceptance list is READ from a leaf that cannot write it, and that is the whole point of
# the indirection: `background/head_red_register` needs the same reader, and reaching it through
# THIS module put `process_run_complete` -- a publish-path source -- on the supervisor's import
# graph, wedging every publish. Re-exported rather than moved outright because this module's own
# four uses below, and `test_head_green_census.py`, address it as `head_green_census.load_baseline`
# -- so the NAME stays where its callers already look and the DEFINITION has one home.

# The publish gate's own marker expression, so the DESELECTIONS match -- not a set of our own
# choosing that could drift away from it.
#
# THIS IS NO LONGER THE SAME POPULATION AS THE GATE, and that inversion is deliberate as of
# 2026-08-21. The publish gate now runs `process_run_complete.PUBLISH_GATE_SCOPE` -- roughly
# 1,180 tests that verify the published OUTPUT, in ~39s -- rather than the whole tree, because a
# 21-to-75-minute gate on a repo that changes every 15 minutes reports on the past instead of
# verifying the present.
#
# So this census is now the WIDER of the two, and that is precisely its job: it is the backstop
# that catches whatever the narrowing gets wrong. It runs unscoped, nightly, with no `-x`. If
# the scope split ever drops something that matters, this is what says so -- which is why it
# must keep running `tests/` and must NEVER be narrowed to match the gate. The two populations
# being different is the design, not drift.
MARKER_EXPR = "not operational and not join_report_only and not scale_report_only"

# The heavy modules the publish gate ignores. Kept in step with
# process_run_complete.PUBLISH_GATE_HEAVY_IGNORES deliberately: measuring a DIFFERENT population
# from the gate would make the two incomparable, and the point is to cover the gate's blind spot,
# not to invent a third scope.
HEAVY_IGNORES = (
    "tests/simulation/test_run_phase2b.py",
    "tests/simulation/test_run_phase2b_event_log.py",
    "tests/simulation/test_run_phase4c_on_phase2b.py",
    "tests/simulation/test_phase40b_gas_pass_through.py",
    "tests/simulation/test_phase24a_ic_customer.py",
    "tests/simulation/test_phase40a_pass_through.py",
    "tests/simulation/test_phase40c_deemed_rate.py",
    "tests/simulation/test_phase41a_flex.py",
)

_FAILED_RE = re.compile(r"^FAILED\s+(\S+)", re.MULTILINE)
_SUMMARY_RE = re.compile(r"(\d+)\s+passed")

# THE CAUSE, not just the name (2026-08-22). `--tb=line` already prints one line per failure
# ending in the exception type, and the census threw it away -- so a page said "12 newly failing
# test(s)" and twelve node ids, and the reader had to re-run the suite to learn whether that was
# twelve unrelated bugs or one guard firing twelve times. Director, 2026-08-21: *"Producing a
# number without pinning what produced it is the shared failure."*
#
# A HISTOGRAM, not a per-node map, and deliberately so: `--tb=line` prints the SOURCE location of
# the raise, not the node id, so any per-node attribution would have to be inferred by pairing
# ordered lists -- correct until one failure prints two lines, and silently wrong afterwards. The
# count per cause is the number that answers "is this one class or twelve", which is the question,
# and it is read directly rather than reconstructed.
#
# IT UNDERCOUNTS, KNOWINGLY. A bare `assert x == y` prints as `assert 1 == 2` with no type name, so
# it contributes to no bucket. The histogram is therefore a floor on named causes and NEVER a
# partition of the reds: `ProductionWriteRefused x2` against 3 reds does not license "so 1 red had
# another cause". Verified against real `--tb=line` output on 2026-08-22, not against a fixture
# string -- the fixture would have agreed with whatever the regex did.
_CAUSE_RE = re.compile(r"^\S+\.py:\d+: ([A-Za-z_][\w.]*(?:Error|Exception|Refused|Failed))",
                       re.MULTILINE)


#: Named here rather than imported, so this module keeps working if the register module is
#: unavailable -- the census's own verdict must not depend on the artefact it feeds.
HEAD_RED_REGISTER_NAME = "HEAD_RED_REGISTER.md"


def parse_failures(output: str) -> list[str]:
    """Every `FAILED <nodeid>` line, deduped, in a stable order."""
    return sorted(set(_FAILED_RE.findall(output or "")))


def parse_causes(output: str) -> dict:
    """`{exception type: count}` over the run's own tracebacks, commonest first.

    Empty when the run printed no parseable cause -- which is a fact about the log, never a claim
    that the failures had no cause, so callers report the names they do have and say nothing more.
    """
    counts = {}
    for name in _CAUSE_RE.findall(output or ""):
        counts[name] = counts.get(name, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def summarise_causes(causes: dict) -> str:
    """One line: `ProductionWriteRefused x12, AssertionError x1`. Empty string when unknown."""
    return ", ".join("{} x{}".format(n.rsplit(".", 1)[-1], c) for n, c in causes.items())


def parse_passed_count(output: str):
    """How many tests PASSED, or None if the summary line is unreadable.

    None and 0 are opposite facts and are kept apart: 0 means the run demonstrably passed
    nothing, None means we cannot tell -- and only one of those is compatible with a green.
    """
    matches = _SUMMARY_RE.findall(output or "")
    return int(matches[-1]) if matches else None


def diff_against_baseline(failures, baseline) -> dict:
    """New reds, fixed reds, and still-red -- the whole verdict, from two sets."""
    failures, baseline = set(failures), set(baseline)
    return {
        "new_red": sorted(failures - baseline),
        "fixed": sorted(baseline - failures),
        "still_red": sorted(failures & baseline),
    }


def verdict(delta: dict, passed_count) -> tuple[str, str]:
    """GREEN / NEW_RED / UNPROVEN, with the reason.

    A run that passed NOTHING, or whose summary could not be read, is UNPROVEN rather than
    green: pytest exits 0 when every selected test is skipped or deselected, so "no failures"
    on its own is satisfied by a run that did nothing at all -- the fail-open shape R15 names.
    """
    if passed_count is None:
        return "UNPROVEN", "no pytest summary line -- the run's own output is unreadable"
    if passed_count == 0:
        return "UNPROVEN", "the run passed ZERO tests -- it selected nothing, so it proved nothing"
    if delta["new_red"]:
        # SAY BOTH NUMBERS AND NAME EACH POPULATION (2026-09-02). "830 test(s) newly failing"
        # was false, and had been false in every message this control ever sent: the acceptance
        # list has been `known_red: []` since 2026-08-12, so "not on the list" means "red", and
        # `newly` means nothing at all. The director read four of these messages -- 12, 17, 33,
        # 830 -- as a rising delta when they were absolute counts wearing a delta's word.
        #
        # A count with no subject is also not actionable, so the message now points at the
        # register that names every one of them rather than trying to fit ten into a page.
        #
        # AND IT STATES `passed` (2026-09-02, same day, second finding). This was the ONLY branch
        # of the three that did not, and the omission cost a whole observation. The 04:30 run
        # COMPLETED -- 58:57 wall, exit 1, all 830 names printed -- but its store row was
        # backfilled by hand three hours later from this very string, and the string does not
        # carry the passed count, so the row went in as `"passed": null`. A null there reads as
        # UNPROVEN downstream (`_record_observation` refuses such a run on purpose), so a
        # completed census was permanently indistinguishable from a truncated one.
        #
        # The red count is a NUMERATOR. Published without the denominator that proves the run
        # reached the end of the suite, it cannot be told apart from a partial list -- which is
        # the same defect the `-x` publish gate had, one level up.
        return "NEW_RED", (
            "{owed} test(s) red at HEAD and neither fixed nor accepted "
            "({accepted} more are red but accepted by name, {passed} passed). Every subject is "
            "named in docs/staging/reference/{register}, which is DRAWN as work while this is "
            "non-zero. First few: {sample}".format(
                owed=len(delta["new_red"]), accepted=len(delta["still_red"]),
                passed=passed_count, register=HEAD_RED_REGISTER_NAME,
                sample=", ".join(delta["new_red"][:5])))
    if delta["still_red"]:
        return "GREEN", "no new failures ({} known-red still failing, {} passed)".format(
            len(delta["still_red"]), passed_count)
    return "GREEN", "no failures at all ({} passed)".format(passed_count)


def pytest_argv() -> list:
    argv = [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line", "-m", MARKER_EXPR]
    argv += ["--ignore=" + i for i in HEAVY_IGNORES]
    return argv


# THE CENSUS'S SUBJECT IS A CLEAN CHECKOUT OF HEAD (2026-08-22), for the same reason the publish
# gate's is -- DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09, *"publishing tests committed truth
# only; the working tree belongs to the lanes."*
#
# THE DEFECT THIS CLOSES. Everything about this control said HEAD -- the module name, the opening
# line "Is HEAD actually green?", the unit Description, the page it sends ("[HEAD-GREEN] N newly
# failing test(s) at HEAD") -- and `run_suite` ran `cwd=PROJECT_DIR`, the live shared working tree.
# So the nightly verdict was "the tree happened to be green while N lanes were mid-edit", which is
# a much weaker claim wearing the same words. It is the exact substitution this module's own
# docstring was written to name, one level up: the gate measured name-adjacency and called it HEAD;
# this measured the working tree and called it HEAD. Observed 2026-08-22 01:40Z, while drawing the
# sink guard's blast radius: 214 modified TRACKED paths sat in the tree, so any NEW_RED the 03:30 run
# reported could have been authored by any lane and the page would have named the test, never the
# cause. The director on 2026-08-21: *"Producing a number without pinning what produced it is the
# shared failure."*
#
# NO SILENT FALLBACK. A checkout that cannot be built returns None and the caller reads UNPROVEN.
# Falling back to `cwd=PROJECT_DIR` would restore the defect precisely when the machinery for
# avoiding it is broken -- the fail-open shape R15 names, and worse than never having moved.
CENSUS_SUBJECT_PREFIX = "head-green-census-"


@contextlib.contextmanager
def head_subject_checkout():
    """Yield a clean checkout of HEAD, or None if one cannot be built.

    Built by the publisher's OWN helpers rather than a second implementation, so the census and
    the gate cannot drift apart about what "a checkout of HEAD" means. Its directory prefix is
    deliberately its own: `_sweep_stale_head_checkouts` owns the publisher's prefix, and a census
    tree inside that namespace could be swept by a concurrent publisher mid-run.
    """
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))
    from background import process_run_complete as prc

    head_sha = prc._head_sha()
    if head_sha is None:
        yield None
        return
    # `prc.HEAD_CHECKOUT_ROOT` (/var/tmp), NOT the default temp dir. On this box `/tmp` is a
    # 3.9G tmpfs at 51% -- a ~130MB / 10,432-file checkout there is RAM, and the publisher chose
    # /var/tmp (885G free, real disk) for exactly that reason. Measured 2026-08-22, after writing
    # it the wrong way first.
    tmp = Path(tempfile.mkdtemp(prefix=CENSUS_SUBJECT_PREFIX, dir=str(prc.HEAD_CHECKOUT_ROOT)))
    try:
        if not prc._materialise_head_into(tmp, head_sha):
            yield None
            return
        # The suite contains tests whose subject is a git repo, so the checkout has to be one.
        prc._make_checkout_a_repo(tmp, head_sha)
        prc._overlay_untracked_data(tmp)
        yield tmp
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)


#: THE SUITE'S OWN TIMEOUT, and it must be COMFORTABLY LESS than systemd's `TimeoutStartSec`.
#:
#: MEASURED 2026-09-02: the nightly run took **58:57** against a 3600s unit limit — sixty-three
#: seconds of margin, 1.7%. And this timeout was ALSO 3600, so it could never fire first: systemd
#: SIGTERMs the whole unit at the same instant, which kills the census before
#: `subprocess.TimeoutExpired` can be caught and reported. A slow night therefore produced no
#: verdict at all, and no verdict is SILENT — the one failure mode this control cannot afford,
#: because its whole purpose is to be the thing that notices.
#:
#: Observed directly: a reproduction run under ordinary contention hit exactly this and died
#: with nothing to show for an hour of CPU.
#:
#: THE ORDERING WAS FIXED AND THE HEADROOM WAS SPENT PAYING FOR IT (2026-09-02, same day). 3300
#: put the suite's timeout below systemd's, which is the property this constant exists to hold --
#: and below **3537s, the duration of the run being described one paragraph up**. A bound under
#: the worst duration actually observed does not measure a hang; it aborts a healthy slow night
#: and reports the same silence the reordering was meant to end. The two halves of that finding
#: are one edit apart and only one of them landed.
#:
#: 7200s is this repo's own rule for a suite bound applied to the number in this comment:
#: `bound > 2 x worst measured` (`test_process_run_complete.py`, for GATE_SUITE_TIMEOUT_SECONDS),
#: which against 3537s demands at least 7074s. `TimeoutStartSec=7500` in the unit keeps the same
#: five minutes for the checkout, the teardown and the report, so the suite's own timeout still
#: fires first and the census says UNPROVEN instead of vanishing. The timer fires once every 24h,
#: so 7500s cannot reach the next firing.
#:
#: THIS IS AN ALLOWANCE FOR HOW LONG THE RUN TAKES AND NOTHING ELSE. It forgives no red, it moves
#: no baseline, and raising it can never turn a verdict green -- the only outcome it changes is
#: UNPROVEN into a real answer. `test_the_census_timeout_clears_the_duration_it_has_observed`
#: holds both directions against the unit file, because until it existed the relationship was
#: asserted in this comment and true only by luck.
SUITE_TIMEOUT_SECONDS = 7200

#: The worst COMPLETE census duration on record, transcribed from the run described above so the
#: control can compare against it. Moved by hand when a slower run is observed -- a bound that
#: re-derived itself from the latest run would ratchet upward on its own, which is how a ceiling
#: stops being a decision anyone made.
WORST_OBSERVED_SUITE_SECONDS = 3537.0


def subject_head_sha(subject) -> str | None:
    """The commit the SUBJECT CHECKOUT actually holds, or None if it cannot be read.

    Read back OUT of the tree that was measured rather than taken from the variable that built it:
    the two can only agree, so this cannot drift, and it also catches a checkout that materialised
    something other than what was asked for. None rather than a fallback to the live HEAD -- an
    unattributable measurement must stay unattributable, because a plausible sha is read as
    established and a None cannot be.
    """
    if subject is None:
        return None
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(subject),
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    sha = (proc.stdout or "").strip()
    return sha or None


def run_suite(timeout: int = SUITE_TIMEOUT_SECONDS, observed: dict | None = None) -> str:
    """Run the unscoped suite against a clean checkout of HEAD.

    Returns the run's output, or "" when no subject could be built -- and "" carries no pytest
    summary line, so `verdict()` reads it as UNPROVEN. The absence of a subject is therefore
    expressed through the existing fail-safe rather than through a new branch that could be
    got wrong.

    `observed`, when given, receives `subject_head`: THE COMMIT THIS RUN MEASURED. It is an
    out-parameter rather than a second return value only so that every existing caller keeps
    working; what it carries is not optional detail.

    WHY IT EXISTS (2026-09-02). `_head_sha()` was called TWICE -- once here to build the subject,
    once in `_record_observation` to label the row -- with the whole suite in between. On this box
    that gap is an hour, on a tree five other lanes land into. Observed live the same day: the
    census that started 12:52:44 held `f5b19b43f` in its own subject checkout while the shared
    HEAD had moved on through six commits to `2a84aec8e`, so the row it was about to write would
    have named a commit its suite never ran a single test against. Every downstream comparison --
    "is this red new?", "did the fix work?" -- is keyed to that field, and this census is what
    certifies every other claim here.
    """
    from background import process_run_complete as prc
    with head_subject_checkout() as subject:
        if observed is not None:
            observed["subject_head"] = subject_head_sha(subject)
        if subject is None:
            return ""
        # PYTEST'S TEMP ROOTS GO ON REAL DISK, not on the tmpfs (2026-09-02).
        #
        # This function already puts its SUBJECT on `/var/tmp` and says why: *"on this box `/tmp`
        # is a tmpfs -- a ~130MB / 10,432-file checkout there is RAM"*. The same argument applies
        # with more force to pytest's own scratch, and nothing was making it: `tmp_path` resolves
        # under `tempfile.gettempdir()`, which is `/tmp`, so an unscoped run of ~24,000 tests wrote
        # its every temp directory into RAM.
        #
        # AND THIS DIRECTORY IS WHERE IT LANDS HARDEST. `tests/background/conftest.py` has four
        # autouse fixtures and every one takes `tmp_path`, so every test there allocates one
        # unconditionally -- which is why 820 of the 830 reds on 2026-09-02 were in that one
        # directory, all failing at fixture SETUP. A whole directory dying on an environmental
        # limit reads, in the census's own message, as 820 defects.
        #
        # Measured the same morning: `/tmp` is a 12GB tmpfs on a 24GB box, and `pytest-of-rich`
        # grew 1.67GB -> 3.36GB in one hour under three concurrent runs.
        env = dict(os.environ)
        env.setdefault("TMPDIR", str(prc.HEAD_CHECKOUT_ROOT))
        try:
            proc = subprocess.run(pytest_argv(), cwd=str(subject), env=env,
                                  capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            # "" CARRIES NO PYTEST SUMMARY, so `verdict()` reads it as UNPROVEN through the
            # fail-safe that already exists, and `_record_observation` writes nothing — an
            # incomplete run must never mark standing reds as fixed.
            #
            # THE PARTIAL OUTPUT IS DELIBERATELY DISCARDED. `TimeoutExpired` carries whatever
            # pytest had printed, and it contains real `FAILED` lines; returning it would publish
            # a PARTIAL red list as if it were the complete one, which is a worse answer than
            # "could not measure".
            sys.stderr.write(
                "[head-green-census] the suite did not finish inside {}s -- UNPROVEN. Partial "
                "output discarded: an incomplete failure list reported as complete would mark "
                "every unreached red as fixed.\n".format(timeout))
            sys.stderr.flush()
            return ""
        return (proc.stdout or "") + (proc.stderr or "")


def evaluate(output: str, baseline_path: Path = BASELINE_PATH) -> dict:
    failures = parse_failures(output)
    passed = parse_passed_count(output)
    causes = parse_causes(output)
    delta = diff_against_baseline(failures, load_baseline(baseline_path))
    status, reason = verdict(delta, passed)
    if status == "NEW_RED" and causes:
        reason += " [causes: {}]".format(summarise_causes(causes))
    return {"status": status, "reason": reason, "passed": passed,
            "failures": failures, "causes": causes, **delta}


def _record_observation(result: dict) -> str:
    """Fold this run into the HEAD-red register and re-render it. Returns a one-line note.

    NEVER RAISES INTO THE CENSUS. The census's job is to measure and to page; the register is a
    downstream artefact, and a control that could not publish its own artefact must still deliver
    its verdict. The failure is REPORTED rather than swallowed -- the whole reason this register
    exists is that the census's output went to a journal nobody reads, and a silent failure here
    would recreate that one layer down.

    An UNPROVEN run records nothing. A run whose suite did not execute has observed no test to be
    green, so folding its empty failure list in would mark every standing red as fixed -- a
    control absorbing its own outage as progress, which is precisely the shape the acceptance
    list is kept human to prevent.
    """
    if result.get("status") == "UNPROVEN":
        return "register not updated: the run proved nothing, so it observed nothing"
    try:
        from background import head_red_register as reg
        # THE SUBJECT'S SHA, NOT TODAY'S HEAD. Re-reading `prc._head_sha()` here labelled the row
        # with whatever the shared tree had advanced to by the time the suite finished -- see
        # `run_suite`'s note for the run that was live when this was found. `None` when the run
        # cannot name its subject (`--from-log`, or an unreadable checkout): an unattributed
        # observation is a fact about what we can say, and inventing a sha for it is the defect.
        store = reg.record(result.get("failures") or [], head_sha=result.get("subject_head"),
                           passed=result.get("passed"), causes=result.get("causes"))
        reg.save_observed(store)
        path = reg.write_register(store, load_baseline())
        return "register: {} owed, written to {}".format(
            len(reg.owed(store, load_baseline())), path)
    except Exception as exc:  # noqa: BLE001 -- see NEVER RAISES above
        return "register NOT updated ({}: {}) -- the verdict below still stands".format(
            type(exc).__name__, str(exc).strip()[:160])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from-log", type=Path,
                    help="parse an existing pytest log instead of running the suite")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--notify", action="store_true",
                    help="send one NTFY when the verdict is NEW_RED (transition payload, R5)")
    args = ap.parse_args(argv)

    observed: dict = {}
    output = (args.from_log.read_text(errors="replace") if args.from_log
              else run_suite(observed=observed))
    result = evaluate(output)
    # Stays absent for `--from-log`: a log parsed after the fact cannot name the commit that
    # produced it, and that is exactly how this store's first row came to claim one.
    result["subject_head"] = observed.get("subject_head")
    register = _record_observation(result)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("{}: {}".format(result["status"], result["reason"]))
        print("  " + register)
        if result.get("causes"):
            print("  causes   " + summarise_causes(result["causes"]))
        for name in result["new_red"]:
            print("  NEW RED  " + name)
        for name in result["fixed"]:
            print("  FIXED    " + name + "   (prune it from the baseline)")

    if args.notify and result["status"] == "NEW_RED":
        try:
            from background.notify import notify
            # THE ALARM SENDS THE VERDICT'S OWN SENTENCE, and that is the whole point of this
            # line (2026-09-02). `bc57c8e30` abolished "newly failing" -- the word that made four
            # absolute counts read to the director as a rising delta -- and mechanised the repair
            # in `verdict()` only. This payload was a SECOND, hand-authored copy of the same
            # claim, so it went on saying "830 newly failing test(s) at HEAD" on the one channel
            # he actually reads, while the test pinning the correction passed. One correction,
            # two surfaces, one edited.
            #
            # Composing the payload FROM `result["reason"]` is what stops that recurring: the
            # numbers, their populations and the causes now have exactly one author, so the two
            # surfaces cannot disagree again without the verdict itself being wrong.
            notify(
                "[HEAD-GREEN] {}\n  {}".format(
                    result["reason"], "\n  ".join(result["new_red"][:12])),
                kind="real_alarm",
                headers={"X-Tags": "rotating_light", "X-Priority": "high"},
            )
        except Exception as exc:  # noqa: BLE001 -- a dead channel must not eat the verdict
            print("  ! notify failed: {}".format(type(exc).__name__), file=sys.stderr)

    return 1 if result["status"] == "NEW_RED" else 0


if __name__ == "__main__":
    sys.exit(main())
