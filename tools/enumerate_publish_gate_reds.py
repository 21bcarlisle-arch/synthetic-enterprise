"""Enumerate EVERY red in the publish gate's blocking scope in ONE pass.

DIRECTOR_PRIORITY_ENUMERATE_THE_STACK_2026-08-10: "run the scoped publish-path suite ONCE
at a clean HEAD checkout WITHOUT -x (full enumeration) ... Capture EVERY red in one pass.
Then fix the complete list as one batch."

WHY THIS EXISTS, and why it is not the gate.
`process_run_complete.publish_gate_pytest_argv` passes `-x`. For a healthy pipeline that is
the right setting -- the verdict is `rc != 0` and stopping at the first red is free. For an
EXCAVATION it is the wrong instrument: it reports the first red in collection order and is
structurally blind to every red behind it, so a stack of N reds reads as N cycles of
"flapping" and costs N serial gate runs (~40 min each) to discover. Measured 2026-08-10
(WORKER_FINDING_THE_ELEVENTH_WEDGE_WAS_A_STACK_NOT_A_BUG): the eleventh wedge was three
reds, and the third could not be seen from any gate log until the first two were fixed.

WHAT IT GUARANTEES.
  * SAME SUBJECT as the gate -- a clean checkout of HEAD built by the publisher's own
    `_materialise_head_into` + `_make_checkout_a_repo` + `_overlay_untracked_data`, so git
    questions answer for HEAD and the working tree's uncommitted lanes cannot judge it.
  * SAME SCOPE as the gate -- `publish_scope.resolve_scope(root=<the checkout>)` and
    `scoped_pytest_argv`, resolved against the tree it runs in (the subject-mismatch guard).
  * SAME DESELECTIONS -- the marker expression and heavy ignores are inherited verbatim
    from `publish_gate_pytest_argv`, never restated here.
  * ONE DIFFERENCE, and only one: `-x` is removed. It is asserted, not assumed --
    `_argv_without_fail_fast` refuses to return an argv that still carries it.

IT IS AN INSTRUMENT, NOT A CONTROL. It never writes the gate's state file, never touches
LAST_TESTED_HASH_FILE, and never decides whether anything publishes. It reads HEAD and
writes a census artefact. A broken census delays a batch; it can never publish a red.

PARALLELISM. The gate's argv is serial (no xdist), so there is no parallelism to halve if
this OOMs -- the director's "halve parallelism before halving scope" resolves to "the scope
is already the floor", and the census says so in its own artefact rather than silently
narrowing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from background import process_run_complete as prc  # noqa: E402
from background import publish_scope  # noqa: E402

# Its own prefix, deliberately NOT `publish-gate-head-`: `_sweep_stale_head_checkouts` owns
# that namespace "and nothing else", and a census tree living inside the publisher's
# lifecycle could be swept by a concurrent publisher mid-run.
CENSUS_CHECKOUT_PREFIX = "publish-gate-census-"
CENSUS_ARTEFACT = PROJECT_DIR / "docs" / "observability" / "publish_gate_red_census.json"

# The census runs the whole scope with no fail-fast, so it is strictly longer than the gate's
# own run. Default well clear of GATE_SUITE_TIMEOUT_SECONDS; overridable from the caller's
# declared budget.
DEFAULT_DEADLINE_SECONDS = 5400

# A timeout is not a green suite. `feedback_a_wrapper_timeout_below_the_work_it_wraps_decides
# _the_verdict`: the census records what it actually observed, and an unfinished census says
# so in its own outcome field rather than reporting the reds it happened to reach as "all".
OUTCOME_COMPLETE = "complete"
OUTCOME_TIMEOUT = "timeout"
OUTCOME_UNAVAILABLE = "unavailable"


def _argv_without_fail_fast(argv):
    """The gate's argv with `-x` removed, and PROVEN removed.

    R15: the single difference between this instrument and the gate is the thing the
    instrument exists for, so it is checked rather than trusted. `-x` also has a long form
    and an `--exitfirst=` spelling; all are stripped, and a survivor raises."""
    stripped = [a for a in argv
                if a not in ("-x", "--exitfirst") and not a.startswith("--exitfirst")]
    if any(a in ("-x", "--exitfirst") or a.startswith("--exitfirst") for a in stripped):
        raise AssertionError("fail-fast survived the strip: {!r}".format(stripped))
    # `-x` is what makes the gate blind to a stack; if it was never there, the premise of
    # this whole instrument has changed and the caller must know.
    if not any(a in ("-x", "--exitfirst") or a.startswith("--exitfirst") for a in argv):
        raise AssertionError(
            "the gate argv carried no fail-fast flag -- publish_gate_pytest_argv has changed "
            "and this census is measuring something other than what it documents: {!r}".format(argv))
    return stripped


# pytest's short summary lines, which is where a no-x run enumerates itself:
#   FAILED tests/foo/test_bar.py::test_baz - AssertionError: ...
#   ERROR tests/foo/test_bar.py - fixture 'x' not found
_RED_LINE = re.compile(r"^(FAILED|ERROR)\s+(\S+?)(?:\s+-\s+(.*))?$")


def parse_reds(stdout: str):
    """Every red node id in a no-x pytest run, in collection order, deduped.

    Parses the short-test-summary lines rather than the progress dots: the summary is the
    only place pytest states the full node id AND its one-line cause together, and `--tb=short`
    (inherited from the gate) keeps the traceback bounded above it."""
    reds, seen = [], set()
    for raw in stdout.splitlines():
        m = _RED_LINE.match(raw.strip())
        if not m:
            continue
        kind, node, cause = m.group(1), m.group(2), (m.group(3) or "").strip()
        if node in seen:
            continue
        seen.add(node)
        reds.append({"kind": kind, "node": node, "cause": cause,
                     "file": node.split("::", 1)[0]})
    return reds


def _materialise_census_checkout(head_sha: str):
    """A clean checkout of HEAD, built exactly the way the gate builds its subject."""
    tmp = Path(tempfile.mkdtemp(prefix=CENSUS_CHECKOUT_PREFIX, dir=str(prc.HEAD_CHECKOUT_ROOT)))
    if not prc._materialise_head_into(tmp, head_sha):
        shutil.rmtree(str(tmp), ignore_errors=True)
        return None
    prc._overlay_untracked_data(tmp)
    return tmp


def run_census(deadline_seconds=DEFAULT_DEADLINE_SECONDS, keep_checkout=False):
    started_wall = time.time()
    head_sha = prc._head_sha()
    if head_sha is None:
        return {"outcome": OUTCOME_UNAVAILABLE, "reason": "HEAD sha unavailable"}

    checkout = _materialise_census_checkout(head_sha)
    if checkout is None:
        return {"outcome": OUTCOME_UNAVAILABLE,
                "reason": "could not materialise a clean checkout of {}".format(head_sha)}

    try:
        base = prc.publish_gate_pytest_argv("tests/")
        scope = publish_scope.resolve_scope(root=checkout)
        gate_argv = publish_scope.scoped_pytest_argv(base, scope, run_root=checkout)
        census_argv = _argv_without_fail_fast(gate_argv)

        env = dict(os.environ)
        env.setdefault("PYTHONDONTWRITEBYTECODE", "0")

        started = time.monotonic()
        timed_out = False
        try:
            result = subprocess.run(census_argv, cwd=str(checkout), env=env,
                                    timeout=deadline_seconds, capture_output=True,
                                    text=True, errors="replace")
            stdout, stderr, rc = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = (exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = (exc.stderr or b"").decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            rc = None
        elapsed = time.monotonic() - started

        reds = parse_reds(stdout)
        return {
            "outcome": OUTCOME_TIMEOUT if timed_out else OUTCOME_COMPLETE,
            "head_sha": head_sha,
            "rc": rc,
            "elapsed_seconds": round(elapsed, 1),
            "deadline_seconds": deadline_seconds,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_wall)),
            "scope_reason": scope.get("reason"),
            "scope_test_files": len(scope.get("tests") or []),
            "scope_full_suite": bool(scope.get("full_suite")),
            "parallelism": 1,
            "parallelism_note": "the gate argv is serial (no xdist); there is no parallelism "
                                "to halve before scope, so scope is the floor.",
            "red_count": len(reds),
            "red_files": sorted({r["file"] for r in reds}),
            "reds": reds,
            "argv": census_argv,
            "stdout_tail": stdout[-20000:],
            "stderr_tail": stderr[-4000:],
            "checkout": str(checkout) if keep_checkout else None,
        }
    finally:
        if not keep_checkout:
            shutil.rmtree(str(checkout), ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--deadline-seconds", type=int, default=DEFAULT_DEADLINE_SECONDS,
                    help="wall-clock budget for the single enumeration run")
    ap.add_argument("--keep-checkout", action="store_true",
                    help="leave the census checkout in place for follow-up diagnosis")
    ap.add_argument("--out", default=str(CENSUS_ARTEFACT))
    args = ap.parse_args(argv)

    census = run_census(deadline_seconds=args.deadline_seconds,
                        keep_checkout=args.keep_checkout)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(census, indent=2, sort_keys=True) + "\n")

    print("census outcome: {}".format(census["outcome"]))
    if census["outcome"] == OUTCOME_UNAVAILABLE:
        print("  {}".format(census.get("reason")))
        return 2
    print("  HEAD {}  rc={}  {}s (deadline {}s)".format(
        census["head_sha"], census["rc"], census["elapsed_seconds"], census["deadline_seconds"]))
    print("  scope: {}".format(census["scope_reason"]))
    print("  {} red(s) across {} file(s):".format(census["red_count"], len(census["red_files"])))
    for r in census["reds"]:
        print("    {} {}".format(r["kind"], r["node"]))
        if r["cause"]:
            print("        {}".format(r["cause"][:160]))
    print("  artefact: {}".format(out))
    if census["outcome"] == OUTCOME_TIMEOUT:
        print("  NOTE: the census hit its deadline -- the red list is a LOWER BOUND, not a census.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
