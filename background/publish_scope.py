"""THE SCOPED PUBLISH-PATH SUITE — what may block a publish, and what may only annotate it.

DIRECTOR_RULING_PUBLISH_DECOUPLING_2026-08-10, property 2, sequenced to the front by
DIRECTOR_PRIORITY_BUILD_THE_BREATHING_2026-08-10 ("stop winning wedges, change the game").

THE DEFECT THIS NAMES
---------------------
The publish gate conflated two questions — "is the entire repo green at HEAD?" and "may the
site update?" — so ANY red anywhere froze the public surface entirely and silently. Measured
cost: the published stamp sat at 2026-08-09T12:41:51Z for 25 hours while ~18 distinct causes
were each cured with excellence and each re-wedged within the hour. The treadmill is
structurally unwinnable while publishing demands whole-repo perfection: the repo is large
enough that SOMETHING is always red, so "publish iff everything is green" is, in practice,
"publish never" — and the freeze is indistinguishable, from outside, from a dead machine.

WHAT THIS IS
------------
The blocking scope narrows from "every unmarked test in the tree" to "every test that
transitively imports the code which PRODUCES or RENDERS a published number". Everything else
still runs (`remainder_pytest_argv`, on its own cadence, after the publish) but ANNOTATES the
page rather than blocking it — `background/publish_provenance.py` carries that annotation to
the live surface.

WHY DERIVED, NOT LISTED
-----------------------
The scope could have been a hand-written list of test paths. It is not, for a reason this
project has already been bitten by twice (`feedback_control_keyed_to_one_syntactic_form`,
WORKER_FINDING_RULE_3_HAS_THE_SAME_RENAME_BLINDNESS): a name-keyed control goes blind the
moment somebody renames or moves a file, and goes blind SILENTLY — the list still resolves,
just to less than it used to. So the scope is DERIVED every run from a declared list of
SOURCE modules, through the static import graph in `tools/select_impacted_tests.py`. Rename a
test and it stays selected (selection follows imports); add a test that exercises the
dashboard generator and it is selected the day it lands, with nobody remembering to add it.

The declaration that has to be maintained by hand is therefore the SOURCES — the publish
path itself — which is a far smaller, far more stable, and far more reviewable object than
the set of tests that happen to touch it.

R15 — THIS CONTROL CAN FAIL, IN BOTH DIRECTIONS
-----------------------------------------------
A narrowed gate's whole risk is fail-OPEN: shipping a broken surface because the test that
would have caught it fell outside the scope. Three guards, each mutation-proven in
`tests/background/test_publish_scope.py`:

  * UNMAPPABLE SOURCE -> FULL SUITE. If a declared source is not a graph-mappable `.py` under
    an analysed root (a typo, a deleted module, a move to a new root), the selector cannot
    prove impact and this returns the FULL suite. A scope that cannot be computed is a scope
    that does not narrow — never a scope that narrows to whatever is left.
  * VACUITY GUARD -> FULL SUITE. A scope that resolves to fewer than MIN_SCOPED_TEST_FILES
    files is treated as broken, not as good news. This is the fail-open shape that has caught
    this project repeatedly (`feedback_population_control_needs_a_vacuity_guard`): an empty
    population passes every assertion made over it, so a gate over zero tests is green over
    nothing and reads exactly like a green gate over everything.
  * THE SELECTOR ITSELF UNAVAILABLE -> FULL SUITE. An import error, a graph build failure,
    anything: an unavailable check is a FAILED check (R15), and the safe direction for a
    SCOPING check that cannot answer is "do not narrow".

Note the asymmetry that makes those safe: every failure of this module degrades to TODAY'S
behaviour (the full gate). The worst case of the scoping machinery breaking is the wedge we
already have, never a broken surface published quietly.

WHAT IT DELIBERATELY DOES NOT CHANGE
------------------------------------
The heavy ignores (speed) and the `operational`/report-only marker deselections (scope) in
`process_run_complete.py` are untouched and still apply to BOTH runs. This narrows which
tests may BLOCK; it does not silence anything, and it does not touch what the remainder run
reports. Nothing here can turn a red publish-path test green.

REUSE: background/publish_scope.py
CLASS: CUSTOM
INDEX: searched "publish gate", "test selection" -- `tools.select_impacted_tests` is the
       nearest row and this module STANDS ON IT rather than reimplementing it: that tool
       answers "which tests does this change touch?" and says of itself "IS NOT: a
       replacement for any gate". What is new here is the POLICY layer -- which sources
       constitute the publish path, and the fail-closed guards deciding when its answer may
       narrow a gate at all. The deselections stay owned by
       `process_run_complete.publish_gate_pytest_argv` and are composed with, never copied.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

# ── THE DECLARATION: the code that produces or renders a published number ────────────────
#
# Read this as "if this module is wrong, a figure on the live site is wrong". That is the
# whole membership test, and it is the reason each entry is here:
#
#   * saas/reporting/annual_report.py      — renders docs/reports/ANNUAL_REPORT.md
#   * tools/generate_dashboard_data.py     — produces site/data/dashboard.json, the SPA's
#                                            single source for every live figure, and runs
#                                            the cross-surface consistency gate and the R14
#                                            basis-label gate on the way past
#   * tools/generate_insights.py           — produces the exec-summary / run_insights.json
#                                            that the dashboard renders NEXT TO those totals
#   * simulation/publish_market_feed.py    — produces docs/market_data/price_feed.json
#   * simulation/publish_consumption_data.py — produces docs/market_data/consumption_feed.json
#   * background/process_run_complete.py   — the publisher itself: LATEST.md, the site build,
#                                            the commit/push. Its own tests are in scope
#                                            because a broken publisher publishes wrongly.
#
# ADDING TO THIS LIST IS CHEAP AND SAFE (it can only widen what blocks). REMOVING FROM IT IS
# THE DANGEROUS DIRECTION — a removal is a claim that this module can no longer make a
# published figure wrong, and needs the evidence for that claim on the commit.
PUBLISH_PATH_SOURCES = [
    "saas/reporting/annual_report.py",
    "tools/generate_dashboard_data.py",
    "tools/generate_insights.py",
    "simulation/publish_market_feed.py",
    "simulation/publish_consumption_data.py",
    "background/process_run_complete.py",
]

# The vacuity floor. Not tuned to today's count (that would make an ordinary refactor red the
# gate for nothing) — set an order of magnitude below the measured 129 so it fires on a scope
# that has COLLAPSED, which is the failure it exists to catch, and never on one that merely
# moved.
MIN_SCOPED_TEST_FILES = 20


class ScopeUnavailable(Exception):
    """Raised internally when the scope cannot be computed; always caught into full-suite."""


def resolve_scope(sources=None, root: Path = PROJECT_DIR) -> dict:
    """Resolve the blocking scope. Returns:

        {"full_suite": bool, "tests": [test files], "reason": str, "sources": [...]}

    `full_suite=True` means "could not narrow safely — block on everything, exactly as
    before". Never raises: every failure path degrades to the full suite (see module
    docstring, R15).
    """
    declared = list(PUBLISH_PATH_SOURCES if sources is None else sources)

    missing = [s for s in declared if not (root / s).exists()]
    if missing:
        return {
            "full_suite": True,
            "tests": [],
            "sources": declared,
            "reason": "{} declared publish-path source(s) do not exist ({}) -- the declaration "
                      "has rotted; blocking on the FULL suite until it is repaired.".format(
                          len(missing), ", ".join(sorted(missing))),
        }

    try:
        from tools.select_impacted_tests import select
        selection = select(declared, root=root)
    except Exception as exc:  # noqa: BLE001 -- an unavailable check is a FAILED check (R15)
        return {
            "full_suite": True,
            "tests": [],
            "sources": declared,
            "reason": "impact selector unavailable ({}: {}) -- cannot narrow; full suite "
                      "blocks.".format(type(exc).__name__, exc),
        }

    if selection.get("full_suite"):
        return {
            "full_suite": True,
            "tests": [],
            "sources": declared,
            "reason": "selector could not narrow: {}".format(selection.get("reason", "")),
        }

    tests = sorted(selection.get("tests") or [])
    if len(tests) < MIN_SCOPED_TEST_FILES:
        return {
            "full_suite": True,
            "tests": tests,
            "sources": declared,
            "reason": "VACUITY GUARD: scope resolved to {} test file(s), below the floor of {} "
                      "-- a collapsed scope is green over nothing, which is indistinguishable "
                      "from green over everything. Full suite blocks.".format(
                          len(tests), MIN_SCOPED_TEST_FILES),
        }

    return {
        "full_suite": False,
        "tests": tests,
        "sources": declared,
        "reason": "{} publish-path source(s) -> {} blocking test file(s) via the static import "
                  "graph.".format(len(declared), len(tests)),
    }


def scoped_pytest_argv(base_argv, scope=None, run_root: Path = PROJECT_DIR):
    """The argv the BLOCKING gate runs, for a suite that will execute with cwd=`run_root`.

    `base_argv` is `process_run_complete.publish_gate_pytest_argv("tests/")` — passed in
    rather than imported so this module has no import cycle with the publisher, and so the
    heavy-ignore/marker deselections it carries are inherited verbatim rather than restated
    here (one source of truth for what is deselected).

    On a full-suite scope this returns `base_argv` UNCHANGED — the pre-decoupling gate,
    byte-for-byte.

    SUBJECT-MISMATCH GUARD (2026-08-10, the wedge this whole module was built to end, which
    it then re-created one layer up). A narrowed scope names test files by PATH, and a path
    only means something relative to the tree it is run against. The gate resolved its scope
    from the working tree but ran it in a clean HEAD checkout
    (DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09, "the working tree belongs to the
    lanes"), so a test file that existed only as one lane's UNCOMMITTED work was handed to a
    checkout that had never seen it. pytest answers a missing positional with rc=4 and "no
    tests ran" — a usage error, not a red test — and the publisher, which only reads the
    return code, wedged the public surface on it. Measured 2026-08-10: two untracked files
    (`test_publish_gate_blocking_payload.py`, `test_wedge_suspects_from_the_red.py`) made a
    131-file tree scope unrunnable against a 129-file HEAD, and because the publish path
    commits only AFTER a green gate, the commit that would have made those paths exist could
    never land. That is the same lane-couples-the-machine defect the checkout ruling removed,
    reintroduced through the scope.

    The cause is fixed at the caller (the scope is now resolved against the run root). This
    guard is the seam's own control: `scoped_pytest_argv` is the ONE place that knows both
    the scope and the root it will be run against, so it is the one place that can check they
    agree. A disagreement degrades to the FULL suite — the module's standing safe direction
    (an uncomputable scope never narrows) — which is runnable against any root because
    `tests/` exists in all of them. A wedge becomes a slower gate, never a quiet publish.
    """
    scope = resolve_scope(root=run_root) if scope is None else scope
    if scope["full_suite"]:
        return list(base_argv)
    absent = [t for t in scope["tests"] if not (Path(run_root) / t).exists()]
    if absent:
        scope["full_suite"] = True
        scope["reason"] = (
            "SUBJECT MISMATCH: {} scoped test path(s) do not exist under the root this gate "
            "runs against ({}) -- the scope was derived from a different tree than the one "
            "under test, and pytest answers a missing path with a usage error, not a red "
            "test. Falling back to the full suite.".format(
                len(absent), ", ".join(sorted(absent)[:5])))
        return list(base_argv)
    # Replace the test-root positional with the resolved file list; every other flag
    # (-x, -q, --tb, -m, --ignore) is inherited untouched.
    argv = [a for a in base_argv if a != "tests/"]
    # The --ignore flags name paths outside the scope in the common case; harmless, and
    # keeping them means a scoped run and a full run deselect identically.
    return argv + list(scope["tests"])


# The blocking gate's fail-fast flag. Right for the gate (the verdict is the same either way,
# and stopping early is free), WRONG for the pass whose only job is to enumerate.
FAIL_FAST_FLAG = "-x"


def remainder_pytest_argv(base_argv):
    """The argv the NON-BLOCKING annotation run uses: the full gate, MINUS its fail-fast flag.

    Deliberately NOT `full minus scoped`. Two reasons. (1) The remainder only ever runs when
    the scoped gate was GREEN, so the scoped tests re-run green and cannot double-count a red
    into the annotation. (2) `full minus scoped` would need the scope to be correct for the
    ANNOTATION to be complete, which makes one control's blind spot the other's blind spot —
    the shared-lineage failure this project has filed before
    (`feedback_agreeing_sources_may_share_lineage`). The annotation run is independent of the
    scoping entirely, so a scope that is too narrow still shows up here as an annotated red.

    WHY `-x` COMES OUT (2026-08-10, the twelfth publish wedge). Everything above is about
    which TESTS the annotation runs; none of it survives running them under `-x`. pytest stops
    at the FIRST red, so this pass — whose entire contract is "the reds that no longer block
    still have to be SEEN" — could report at most ONE of them, and the caller's `reds[:32]`
    cap could never bind. The same flag, on the same argv, is why the eleventh wedge read as
    four flapping tests across six gate cycles and was actually a STACK of three simultaneous
    reds, each tick paying one layer and reporting it as *the* cause
    (`WORKER_FINDING_THE_ELEVENTH_WEDGE_WAS_A_STACK_NOT_A_BUG_2026-08-10.md`). An enumerator
    that stops at one is not an enumerator: it reports "1 red" identically whether there is
    one or thirty, so the annotation's number carried no information about depth.

    `-x` STAYS ON THE BLOCKING GATE, which is why this is a seam and not an edit to
    `publish_gate_pytest_argv`. There, fail-fast is right — the verdict is `rc != 0` either
    way and stopping early returns the publish path's latency to the lanes. Here the cost of
    running on is one already-throttled, already-non-blocking, post-publish suite.
    """
    return [a for a in base_argv if a != FAIL_FAST_FLAG]
