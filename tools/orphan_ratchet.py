"""THE ORPHAN RATCHET — a commit may not ADD work that nothing runs.

DIRECTOR_INSTRUCTION (2026-08-12): *"This class stops recurring, and stops being found by
accident. Work that exists but is connected to nothing that runs should be caught by the machine,
at the moment it happens, not by me noticing weeks later."*

Brief: `docs/staging/done/WORKER_REPORT_NO_CALLER_CLASS_CENSUS_2026-08-09.md` — 13 instances in
13 days, 8 found by accident.

WHERE THIS DEPARTS FROM THE CENSUS, DELIBERATELY
------------------------------------------------
The census proposed M1 as *"a reachability census from declared production entrypoints"*. A census
is a REPORT, and the report already exists: `tools/capability_index.py --orphans` has printed a
standing list since 2026-08-08 and prints ~230 rows today. Instance #10 was created on 2026-08-09,
AFTER that report existed, and was still found by accident.

A list of 230 is not a control. It is the shape this project already has a name for — an
always-red detector is as ignored as a blind one — and a disposition register for 258 of them
(`a019ad96d`) is paperwork about the backlog, not prevention of the next one.

So this is a RATCHET, not a census. The standing set is frozen as a baseline nobody has to fix
today; what fails is **the commit that adds a new one**. That is the difference between "found by
accident weeks later" and "refused at the moment it happens", which is the outcome actually asked
for. The census's four requirements are kept in full — they were right about the CONTENT of the
check; this differs only about WHEN it fires and what it does when it does.

REQUIREMENT 1: ENTRYPOINTS COME FROM THE COMMITTED SCHEDULE, NOT `__main__`
--------------------------------------------------------------------------
The load-bearing correction, and the one the current index gets wrong. `capability_index
._is_entrypoint` returns True for any module with an `if __name__ == "__main__"` block, so census
instance #10 -- `forward_attachment_register --write`, a regeneration step NOTHING EVER RUNS --
reads as a legitimate `entrypoint` and can never be reported. **A CLI nothing schedules is an
orphan.** Entrypoints here are derived from what this machine actually executes: the committed
systemd units, the timers, and the git hooks. If it is not scheduled and nothing imports it, it
does not run, whatever its `__main__` block says.

FAIL-CLOSED, TWO WAYS (R15, both proven in tests/tools/test_orphan_ratchet.py)
-----------------------------------------------------------------------------
This control's natural failure is to UNDER-REPORT, and an under-reporting orphan check does not
merely miss things -- it AUTHORISES the thing it exists to prevent, by certifying a tree as clean.
So:

  * VACUITY FLOOR on the entrypoint set, CONDITIONED ON TREE SIZE. If the schedule parser finds
    no entrypoints, every module is "unreachable" and the answer means nothing. Zero always
    fails; the absolute floor of 5 applies only above 100 modules, because a flat floor is right
    for this repo and nonsense for a two-module fixture -- and a floor that callers pass in is a
    floor callers can set to zero.
  * INDEPENDENT COVERAGE ORACLE, over the SAME population. The row set is compared against
    `git ls-files` -- a different substrate from the index's own filesystem walk, because a walk
    that silently stops early looks exactly like a small clean codebase. It counts tracked files
    under the same declared roots minus the same evidence files: the first version compared 904
    rows against every `*.py` in the repo (2202, including ~1300 tests) and fired on every
    commit forever, which is an only-fail control and wedges rather than protects.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import capability_index as ci  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "docs" / "design" / "orphan_baseline.json"

#: Committed files that describe WHAT THIS MACHINE RUNS. Not `__main__` blocks -- see module
#: docstring. Globs are resolved against the repo root.
SCHEDULE_GLOBS = (
    "background/*.service",
    "background/*.timer",
    "background/*.path",
    "tools/git-hooks/*",
    ".claude/hooks/*.py",
)

#: A scheduled unit names its program as `python3 -m background.foo` or `python3 background/foo.py`.
_MODULE_RE = re.compile(r"(?:python3?\s+-m\s+)([A-Za-z_][\w.]*)")
_SCRIPT_RE = re.compile(r"([A-Za-z_][\w/]*\.py)\b")
#: The ASGI form: `-m uvicorn background.file_api:app`. Without this the captured module is
#: `uvicorn` -- a third-party runner -- and the app it serves reads as an orphan. `file_api` is
#: exactly that case and was reported as one until this was added.
_ASGI_RE = re.compile(r"\b([A-Za-z_][\w.]*)\s*:\s*[A-Za-z_]\w*")
#: Third-party runners that are never the program themselves.
_RUNNERS = frozenset({"uvicorn", "gunicorn", "hypercorn", "flask", "celery", "pytest"})
#: Only these directives name a program. Parsing the whole unit sweeps prose out of
#: `Description=` into the entrypoint set, which would quietly make the vacuity floor
#: unfalsifiable -- a floor is only a control if the thing it counts is real.
_EXEC_PREFIXES = ("ExecStart=", "ExecStartPre=", "ExecStartPost=", "ExecReload=", "ExecStop=")

#: Below this the schedule parser is considered broken rather than the machine idle. The real
#: count is ~20; an order of magnitude below that is the vacuity signal, deliberately NOT tuned
#: to today's number (which would red on an ordinary unit rename).
MIN_ENTRYPOINTS = 5
#: Above this many modules, a handful of entrypoints is evidence of a broken parser rather
#: than a small program. Below it, one entrypoint is a perfectly ordinary tree.
LARGE_TREE_MODULES = 100
#: The index must see at least this fraction of tracked python files, measured against git.
MIN_COVERAGE_RATIO = 0.80


def scheduled_entrypoints(root: Path | None = None) -> set[str]:
    """Dotted module names this machine actually executes, from the committed schedule."""
    base = root or ROOT
    found: set[str] = set()
    for glob in SCHEDULE_GLOBS:
        for path in sorted(base.glob(glob)):
            if not path.is_file():
                continue
            try:
                text = path.read_text(errors="replace")
            except OSError:
                continue
            # A unit file names its program only on Exec* lines. A hook is a shell script and
            # every line of it is executable, so it is scanned whole.
            is_unit = path.suffix in {".service", ".timer", ".path"}
            lines = [ln for ln in text.splitlines()
                     if not is_unit or ln.lstrip().startswith(_EXEC_PREFIXES)]
            for line in lines:
                for mod in _MODULE_RE.findall(line):
                    if mod not in _RUNNERS:
                        found.add(mod)
                for mod in _ASGI_RE.findall(line):
                    found.add(mod)
                for script in _SCRIPT_RE.findall(line):
                    rel = script.lstrip("./")
                    if (base / rel).exists():
                        found.add(ci.module_name(rel))
    # A name only counts if it is a module this repo actually has -- a typo in a unit must not
    # silently inflate the entrypoint set past its own vacuity floor.
    known = {ci.module_name(rel) for rel in ci.source_files(base)}
    return {m for m in found if m in known}


#: The index annotates a caller found via a path string rather than an import as
#: `"background.foo (by path)"`. Stripping it is not cosmetic -- see `_import_edges`.
_BY_PATH_SUFFIX = " (by path)"


def _caller_module(caller: str) -> str:
    return caller[:-len(_BY_PATH_SUFFIX)] if caller.endswith(_BY_PATH_SUFFIX) else caller


def _import_edges(rows: list[dict]) -> dict[str, set[str]]:
    """{module: modules it reaches}. Inverted from the index's `callers` (who reaches me), so the
    graph is the index's own and not a second parse that could disagree with it.

    PATH REFERENCES ARE EDGES, and dropping them is the difference between a working control and
    a useless one. This machine runs most of itself by SUBPROCESS, not by import: `sim_runner`
    shells out to `simulation/run_phase2b.py`, the publisher shells out to the generators. The
    index already models that -- it records such a caller as `"background.foo (by path)"` -- and
    the census made it an explicit requirement.

    The first version of this function tested `if caller in imports`, which is False for every
    one of those annotated strings, so it silently discarded EVERY subprocess edge and reported
    550 orphans of 904 modules. The number looked alarming rather than absurd, which is exactly
    how a broken control gets believed.
    """
    imports: dict[str, set[str]] = {r["module"]: set() for r in rows}
    for row in rows:
        for caller in row.get("callers") or []:
            mod = _caller_module(caller)
            if mod in imports:
                imports[mod].add(row["module"])
    return imports


def reachable_from(entrypoints: set[str], rows: list[dict]) -> set[str]:
    """Every module reachable by import from `entrypoints`, entrypoints included."""
    imports = _import_edges(rows)
    seen: set[str] = set()
    queue = deque(m for m in entrypoints if m in imports)
    seen.update(queue)
    while queue:
        mod = queue.popleft()
        for nxt in imports.get(mod, ()):  # noqa: SIM118
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def _tracked_py_count(root: Path) -> int:
    """Tracked production modules per GIT -- a different substrate from the index's own walk.

    SAME POPULATION, DIFFERENT SOURCE. The first version of this oracle asked git for every
    `*.py` in the repo and compared 904 indexed rows against 2202 tracked files, then fired.
    That was a false positive in the control itself: the index indexes DECLARED_ROOTS and
    excludes evidence files by design, while `git ls-files '*.py'` counts ~1300 test modules the
    index never claimed. Comparing a measure to a population it was never taken over is the
    wrong-load-set defect, and it would have made this gate red on every commit forever -- an
    only-fail control, which wedges rather than protects.

    So the oracle keeps its independence (git, not the filesystem walk) and drops the mismatch:
    it counts tracked `.py` under the same declared roots, minus the same evidence files.
    """
    try:
        args = ["git", "ls-files"] + ["{}/*.py".format(r) for r in ci.DECLARED_ROOTS]
        out = subprocess.run(args, cwd=str(root),
                             capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return 0
    return len([ln for ln in out.splitlines()
                if ln.strip() and not ci.is_evidence_file(ln.strip())])


def compute(root: Path | None = None) -> dict:
    """The orphan set plus the two fail-closed guards. Never silently degrades."""
    base = root or ROOT
    rows = ci.build_rows(base)
    entry = scheduled_entrypoints(base)
    problems: list[str] = []

    # THE FLOOR IS CONDITIONED ON THE SIZE OF THE TREE, not a flat number, and not a parameter.
    # A flat floor of 5 is right for this repo and nonsense for a two-module fixture, which is
    # how a floor ends up being passed in by callers -- and a floor a caller can lower to zero
    # is not a floor. Zero entrypoints is ALWAYS vacuous (nothing runs, so everything is
    # unreachable and the answer means nothing); the absolute floor applies only once the tree
    # is big enough for it to be evidence.
    if not entry or (len(rows) >= LARGE_TREE_MODULES and len(entry) < MIN_ENTRYPOINTS):
        problems.append(
            "VACUITY: the schedule parser found {} entrypoint(s) over {} module(s) (floor {} "
            "above {} modules; zero is always vacuous). Near-zero means the parser is broken, "
            "not that the machine runs nothing -- and an orphan check with no entrypoints would "
            "certify the whole tree as unreachable.".format(
                len(entry), len(rows), MIN_ENTRYPOINTS, LARGE_TREE_MODULES))

    tracked = _tracked_py_count(base)
    if tracked and len(rows) < tracked * MIN_COVERAGE_RATIO:
        problems.append(
            "COVERAGE: the index sees {} module(s) but git tracks {} python file(s) (floor {:.0%}). "
            "A walk that stops early looks exactly like a small clean codebase.".format(
                len(rows), tracked, MIN_COVERAGE_RATIO))

    reached = reachable_from(entry, rows)
    orphans = sorted(r["module"] for r in rows
                     if r["module"] not in reached and not ci.is_evidence_file(r["path"]))
    return {"orphans": orphans, "entrypoints": sorted(entry),
            "module_count": len(rows), "tracked_py": tracked, "problems": problems}


def load_baseline(path: Path | None = None) -> dict:
    p = path or BASELINE_PATH
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {"orphans": []}


def new_orphans(state: dict, baseline: dict) -> list[str]:
    return sorted(set(state["orphans"]) - set(baseline.get("orphans") or []))


def freeze(root: Path | None = None, path: Path | None = None) -> dict:
    state = compute(root)
    data = {
        "_doc": "THE RATCHET FLOOR for the no-caller class. Every module here is unreachable "
                "from the committed schedule TODAY and is grandfathered: nobody must fix them to "
                "commit. What the gate refuses is a module that is NOT on this list becoming "
                "unreachable -- i.e. the moment a new one is created. Shrink it freely; growing "
                "it requires saying why in the commit that grows it.",
        "orphans": state["orphans"],
        "entrypoint_count": len(state["entrypoints"]),
        "module_count": state["module_count"],
    }
    (path or BASELINE_PATH).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return data


def run(root: Path | None = None, path: Path | None = None, report: bool = False) -> int:
    state = compute(root)
    baseline = load_baseline(path)

    if state["problems"]:
        for p in state["problems"]:
            print("orphan-ratchet: {}".format(p), file=sys.stderr)
        print("orphan-ratchet: REFUSING to certify this tree -- an unavailable check is a FAILED "
              "check.", file=sys.stderr)
        return 1

    if report:
        print("entrypoints (from the committed schedule): {}".format(len(state["entrypoints"])))
        print("modules indexed: {} | git-tracked .py: {}".format(
            state["module_count"], state["tracked_py"]))
        print("orphans now: {} | baseline: {}".format(
            len(state["orphans"]), len(baseline.get("orphans") or [])))

    added = new_orphans(state, baseline)
    if added:
        print("\norphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS.\n", file=sys.stderr)
        for mod in added[:20]:
            print("  {}".format(mod), file=sys.stderr)
        if len(added) > 20:
            print("  ... and {} more".format(len(added) - 20), file=sys.stderr)
        print(
            "\nNothing imports these, and no committed systemd unit, timer or git hook runs them.\n"
            "This is the no-caller class (13 instances in 13 days, 8 found by accident:\n"
            "docs/staging/done/WORKER_REPORT_NO_CALLER_CLASS_CENSUS_2026-08-09.md).\n"
            "\nWire it to something that runs, or -- if it is deliberately dormant -- say so by\n"
            "adding it with `python3 tools/orphan_ratchet.py --freeze` in the SAME commit, so the\n"
            "decision is on the record instead of in someone's head.\n", file=sys.stderr)
        return 1

    gone = sorted(set(baseline.get("orphans") or []) - set(state["orphans"]))
    if gone and report:
        print("\n{} baseline orphan(s) are now wired -- re-freeze to lower the floor:\n  {}".format(
            len(gone), "\n  ".join(gone[:10])))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The orphan ratchet (no-caller class).")
    ap.add_argument("--freeze", action="store_true",
                    help="rewrite the baseline from the current tree")
    ap.add_argument("--report", action="store_true", help="print the counts as well as gating")
    args = ap.parse_args(argv)
    if args.freeze:
        data = freeze()
        print("froze {} orphan(s) from {} module(s) -> {}".format(
            len(data["orphans"]), data["module_count"], BASELINE_PATH))
        return 0
    return run(report=args.report)


if __name__ == "__main__":
    raise SystemExit(main())
