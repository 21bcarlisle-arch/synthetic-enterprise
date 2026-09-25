"""Time the pre-commit hook chain STEP BY STEP, because nothing did.

WHY THIS EXISTS (2026-09-17, Lane 0 direction "make the pre-commit hook chain cheaper").
`docs/observability/commit_hook_duration.jsonl` records ONE number per commit -- the whole
chain -- so a chain that grew five-fold (95s -> 667s over nine days) could be seen growing and
could not be attributed to anything. Every discussion of which step was expensive was therefore
a discussion about which step LOOKED expensive. The direction's instruction was explicit:
"time the hooks individually rather than reasoning about which looks expensive".

WHAT IT MEASURES AND WHAT IT CANNOT. Each step is the exact argv `tools/git-hooks/pre-commit`
runs, in the order it runs it. Steps whose subject is the STAGED SET (the test gate's own test
selection, the site lane, the stale-copy refusal) are measured with whatever this tree has
staged, which is usually nothing -- so their reading here is a FLOOR and the report says so per
step rather than in a footnote. The always-run control set is the one part of the test gate that
does NOT depend on staging: it runs on every commit that stages any code file, so it is timed
directly as its own step.

IT NEVER TOUCHES THE INDEX. Staging a file to make the measurement representative would carry
another lane's in-place work into their next commit -- see CLAUDE.md on pathspec vs `-A`. The
floor is honest; a contaminated index is not recoverable.

Read-only on purpose apart from the gates' own incidental artefact writes (the size ratchet's
warning log), which are what they write on every real commit anyway.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: WHERE A READING GOES BY DEFAULT, and the reason it is a tracked series rather than a flag.
#: The first run of this tool (2026-09-17) wrote its numbers to a prose table in a staging
#: document behind an optional `--json` nobody passed. The next turn was then asked to attribute a
#: +6.3%/day trend across two dates and had ONE machine-readable date to do it with -- the second
#: reading had to be re-taken before any comparison could begin, and the first had to be read out
#: of a paragraph. A diagnostic whose readings need a flag to survive is one run forever, so this
#: one appends unless told not to.
SERIES_PATH = ROOT / "docs" / "observability" / "commit_hook_step_timings.jsonl"

#: The chain, in hook order. `staged_subject` marks a step whose cost depends on what is staged,
#: so its reading on an empty index is a LOWER BOUND rather than a measurement.
STEPS: tuple[tuple[str, list[str], bool], ...] = (
    # THE REPORTER THAT RUNS BEFORE EVERY GATE and refuses nothing: does the chain git is about to
    # run match the chain the trunk declares. Two `git show`s and two file reads; it is here
    # because the list must BE the hook, not because its cost is interesting.
    ("live_hook_drift", ["python3", "-m", "tools.live_hook_drift"], False),
    # THE CONDITIONAL FIRST BLOCK. These two run only when `docs/status/LATEST.md` is staged, so
    # most commits pay nothing for them -- but "most" is not "none", and a step nobody times is a
    # step nobody can cut. Found by `test_every_step_the_hook_runs_is_timed` on its first run,
    # which is the whole argument for deriving the list from the hook instead of typing it.
    ("stamp_latest_md", ["python3", "tools/stamp_latest_md.py"], True),
    ("background.status_honesty", ["python3", "-m", "background.status_honesty"], True),
    ("stale_copy_refusal", ["python3", "-m", "tools.stale_copy_refusal", "--staged"], True),
    ("test_gate", ["python3", "tools/pre_commit_test_gate.py"], True),
    ("level_promotion_gate", ["python3", "tools/level_promotion_gate.py"], True),
    ("site_lane_gate", ["python3", "tools/site_lane_gate.py"], True),
    ("startup_anchor_freshness", ["python3", "tools/startup_anchor_freshness.py", "--gate"], True),
    ("knowledge_layer_gate", ["python3", "tools/knowledge_layer_gate.py"], True),
    ("moap_coherence_gate", ["python3", "tools/moap_coherence_gate.py"], False),
    ("ruling_archive_question_gate", ["python3", "tools/ruling_archive_question_gate.py"], True),
    ("consolidation_rhythm", ["python3", "tools/consolidation_rhythm.py", "--gate"], True),
    ("size_ratchet_gate", ["python3", "tools/size_ratchet_gate.py"], True),
    ("orphan_ratchet", ["python3", "tools/orphan_ratchet.py"], False),
    ("company_network_isolation", ["python3", "-m", "tools.company_network_isolation", "--gate"],
     False),
    ("file_scope_generated_paths", ["python3", "-m", "tools.file_scope_generated_paths"], False),
    ("annual_report_import_ratchet", ["python3", "-m", "tools.annual_report_import_ratchet"],
     False),
    ("half_hourly_dependency_ratchet", ["python3", "-m", "tools.half_hourly_dependency_ratchet"],
     False),
    ("running_total_order", ["python3", "-m", "tools.running_total_order", "--gate"], False),
    ("scope_evidence_ratchet", ["python3", "-m", "tools.scope_evidence_ratchet"], False),
    ("commons_source_supersession",
     ["python3", "-m", "tools.commons_source_supersession", "--check"], False),
    ("commons_citation_supports_provenance",
     ["python3", "-m", "tools.commons_citation_supports_provenance", "--check"], False),
    # THE TWENTY-SECOND, added 2026-09-25, and it was RED AT `origin/main` for a day before
    # anybody could see it. `934343669` put this gate into the hook and did not add it here;
    # `test_every_step_the_hook_runs_is_timed` went red on the trunk, and no commit's selection
    # could reach it -- staging `tools/hook_gate_mark.py` selects the mark's OWN test by stem,
    # never this one. Exactly the class `GIT_ORACLED_AND_TEST_CORPUS_SUBJECTS` was written for,
    # in a control that is not on that list. Found while building `tools/live_hook_drift.py`,
    # which reads the same hook through the same parser.
    #
    # IT IS THE ONE STEP THAT WRITES. `--record` drops a mark file in the git dir -- the same
    # write it performs on every real commit -- so the loop below puts back whatever was there
    # before rather than leaving a timing run's mark to be read as a commit's.
    ("hook_gate_mark", ["python3", "-m", "tools.hook_gate_mark", "--record"], False),
)


def _control_set() -> list[str]:
    """The always-run test list, read from the gate itself rather than copied.

    A hand-kept copy of a list whose whole property is "it grows" is the stand-in-fixture
    failure this repo has hit twice: it would read 12 entries while the gate ran 38.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "_pre_commit_test_gate", ROOT / "tools" / "pre_commit_test_gate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.CONTROL_TESTS)


def _gate_mark_path() -> Path:
    """Where `hook_gate_mark --record` writes, asked of the module rather than reconstructed."""
    from tools import hook_gate_mark

    out = subprocess.run(["git", "rev-parse", "--absolute-git-dir"], cwd=str(ROOT),
                         capture_output=True, text=True)
    return Path(out.stdout.strip()) / hook_gate_mark.MARK_FILENAME


def _gate_mark_bytes() -> bytes | None:
    try:
        return _gate_mark_path().read_bytes()
    except OSError:
        return None


def _restore_gate_mark(before: bytes | None) -> None:
    path = _gate_mark_path()
    try:
        if before is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(before)
    except OSError:
        # A mark that cannot be put back is worth saying so about, loudly, and never worth
        # failing a measurement over.
        print(f"[chain] WARNING: could not restore {path} -- delete it by hand before the next "
              "commit, or its mark will be read as that commit's.")


def _time(argv: list[str]) -> tuple[float, int]:
    started = time.monotonic()
    proc = subprocess.run(argv, cwd=str(ROOT), capture_output=True, text=True)
    return time.monotonic() - started, proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="substring: time only steps whose name contains this")
    parser.add_argument("--control-set", action="store_true",
                        help="time the always-run control set as ONE pytest run and each file "
                             "separately, which is what attributes the test gate")
    parser.add_argument("--json", type=Path, help="write the readings here as JSON")
    parser.add_argument("--no-series", action="store_true",
                        help="do NOT append this reading to the tracked series -- for a run "
                             "taken under known contention, or in a scratch extract, where the "
                             "number would pollute the trend rather than extend it")
    args = parser.parse_args()

    readings: dict[str, object] = {"measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                                time.gmtime())}

    if args.control_set:
        control = _control_set()
        print(f"[chain] always-run control set: {len(control)} file(s)", flush=True)
        whole, rc = _time([sys.executable, "-m", "pytest", *control, "-q", "--no-header",
                           "-p", "no:cacheprovider"])
        print(f"[chain]   ALL {len(control)} in one pytest run: {whole:6.1f}s (rc {rc})",
              flush=True)
        per_file = []
        for path in control:
            seconds, rc = _time([sys.executable, "-m", "pytest", path, "-q", "--no-header",
                                 "-p", "no:cacheprovider"])
            per_file.append({"path": path, "seconds": round(seconds, 2), "returncode": rc})
            print(f"[chain]   {seconds:6.1f}s  rc{rc}  {path}", flush=True)
        per_file.sort(key=lambda r: -r["seconds"])
        readings["control_set"] = {
            "files": len(control),
            "one_run_seconds": round(whole, 2),
            "sum_of_separate_runs_seconds": round(sum(r["seconds"] for r in per_file), 2),
            "per_file": per_file,
        }
        print("\n[chain] DEAREST FIVE of the always-run set:")
        for row in per_file[:5]:
            print(f"[chain]   {row['seconds']:6.1f}s  {row['path']}")

    steps = [s for s in STEPS if not args.only or args.only in s[0]]
    if steps:
        timed = []
        # THE ONE SIDE EFFECT THIS TOOL WOULD OTHERWISE LEAVE BEHIND. `hook_gate_mark --record`
        # writes a mark naming the tree the index currently writes out to, and `commit-msg` later
        # believes a mark whose tree still matches. A timing run is not a commit, so leaving its
        # mark would let a LATER hand-built commit over an unchanged index inherit a gate receipt
        # it never earned. Whatever was there before goes back afterwards, including "nothing".
        before = _gate_mark_bytes()
        try:
            for name, argv, staged_subject in steps:
                seconds, rc = _time(argv)
                timed.append({"step": name, "seconds": round(seconds, 2), "returncode": rc,
                              "reading_is_a_floor": staged_subject})
                floor = "  (FLOOR -- subject is the staged set)" if staged_subject else ""
                print(f"[chain] {seconds:6.1f}s  rc{rc}  {name}{floor}", flush=True)
        finally:
            _restore_gate_mark(before)
        readings["steps"] = timed
        total = sum(r["seconds"] for r in timed)
        print(f"\n[chain] chain total on THIS index: {total:.1f}s")
        print("[chain] steps marked FLOOR read near-zero on an empty index and are NOT the "
              "chain's real cost on a code commit -- the control set is.")

    if args.json:
        args.json.write_text(json.dumps(readings, indent=2) + "\n", encoding="utf-8")
        print(f"[chain] readings -> {args.json}")
    if not args.no_series:
        append_to_series(readings)
        print(f"[chain] appended to the series -> {SERIES_PATH.relative_to(ROOT)}")
    return 0


def append_to_series(readings: dict, path: Path = SERIES_PATH) -> None:
    """Append one reading to the tracked series, flattened to one line per run.

    THE COMMIT IS CARRIED, because a per-step timing is meaningless without the tree it was taken
    on: the whole use of this series is a two-date difference, and a difference between two runs
    that cannot name their commits attributes nothing. It is read from git rather than passed in,
    so a caller cannot get it wrong, and it is `None` with the field still present when git will
    not answer -- an absent commit is a fact about the reading and must not look like an absent
    field.
    """
    commit = None
    try:
        proc = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=30, check=False)
        if proc.returncode == 0:
            commit = proc.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        commit = None
    row = {"measured_at": readings.get("measured_at"), "commit": commit}
    control = readings.get("control_set")
    if control:
        row["control_set_one_run_seconds"] = control.get("one_run_seconds")
        row["control_set_files"] = control.get("files")
        row["control_set_per_file"] = {r["path"]: r["seconds"] for r in control.get("per_file", [])}
    if readings.get("steps"):
        row["steps"] = {s["step"]: s["seconds"] for s in readings["steps"]}
        row["steps_reading_is_a_floor"] = sorted(
            s["step"] for s in readings["steps"] if s["reading_is_a_floor"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    sys.exit(main())
