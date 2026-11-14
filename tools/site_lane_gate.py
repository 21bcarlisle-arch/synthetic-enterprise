"""Site-lane pre-commit gate (Campaign A debt E, SITE_TEST_COVERAGE_SEAM_FRAME.md, mechanism B+C).

THE SEAM THIS CLOSES
--------------------
The publish gate (`background/process_run_complete.py::publish_gate_pytest_argv(test_root="tests/")`)
runs `tests/` ONLY. `site/**/test_*.py` live OUTSIDE `tests/`, so a red site-door test CANNOT wedge
the publish gate and slips straight onto the director's window (happened 3x this session: the
8th-pair Proof panel, E2 net-margin, the supplier-count). A gate that cannot see the window's own
tests is a FAIL-OPEN control (R15 doctrine: a control that cannot fire on its own named defect is
worse than none).

This gate closes the seam at COMMIT time: a change that touches the site -- or a value the site
RENDERS -- cannot commit while a `site/**` test is red.

ISOLATED FROM THE PUBLISH GATE ON PURPOSE
-----------------------------------------
It runs `pytest site/` in its OWN pre-commit step, with its OWN alarm -- never folded into the
heavy `tests/` publish root (frame option A, rejected). So a flaky `.mjs` render harness alarms the
site lane WITHOUT ever wedging publishing. `pytest site/` is fast (~6s, ~164 tests): no cost reason
to exclude it, it was simply never wired in.

B -- BROAD trigger (the case that bit this session): a change to `site/data/**`, a site-data
producer (`tools/generate_*_data.py`), or a known site-consumed ledger
(`docs/observability/coupled_gap_ledger.json`) runs the WHOLE `pytest site/` suite -- a derived
value the site renders can break ANY door, not just its own directory's test.

C -- DIRECT-EDIT mapping (the pre-commit changed-file -> test extension): a changed
`site/X/foo.{html,py,js,mjs}` pulls in its sibling `site/X/test_*.py` (targeted; faster than the
full run for a one-door edit). This is the site-lane's OWN changed-file->test map, kept isolated
from `pre_commit_test_gate.py`'s `tests/` map so the two lanes never couple.

R15 -- THE GATE MUST BE ABLE TO FAIL (mutation-proven in
`tests/tools/test_site_lane_gate.py`)
-----------------------------------------------------------------------------------
FAIL-CLOSED on missing node: the `.mjs` render harnesses SKIP (not fail) when `node` is absent, so
a green-with-skips `pytest site/` run is NOT proof the render tests actually ran. If `node` is
missing this gate FAILS LOUD -- an unavailable check is a FAILED check, never a silent pass.
"""
from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:  # run as `python3 tools/site_lane_gate.py`, sys.path[0] is tools/
    sys.path.insert(0, str(ROOT))

from tools.pre_commit_test_gate import MERGE_PARENT_ENV, selection_paths  # noqa: E402

SITE_DATA_PREFIX = "site/data/"
SITE_PREFIX = "site/"

# Source-file suffixes under site/ that can change a rendered surface and so map to a sibling test.
SITE_SOURCE_SUFFIXES = frozenset({".html", ".py", ".js", ".mjs"})

# Values the site RENDERS but that live OUTSIDE site/ -- a change here can silently drift a rendered
# figure without any site/ file being staged (the exact class that bit this session). An explicit,
# documented allowlist (extend as new site-consumed ledgers appear); a change to any of these forces
# the WHOLE site suite because we cannot know which door consumes it.
SITE_CONSUMED_LEDGERS = frozenset({
    "docs/observability/coupled_gap_ledger.json",
    "docs/observability/decision_log.jsonl",
    "docs/observability/fidelity_evidence_ledger.json",
})

# A source OUTSIDE site/ whose feed one door re-derives and compares (a staleness test). Targeted,
# not broad: one door reads it, so one test file guards it. Without this, the commit that edits the
# source passes and the NEXT full-suite run -- anyone's -- inherits the red: db80910fa (13 Nov
# 20:00) edited the reading log, and the seat's direction record was refused for it at 03:54 14 Nov.
SOURCE_DOOR_TESTS = {
    "docs/institutional/reading_log.md": ("site/knowledge/test_the_reading_log_door.py",),
}


def staged_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=str(ROOT), capture_output=True, text=True,
    ).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def _is_site_data_producer(path: str) -> bool:
    """`tools/generate_*_data.py` -- regenerates a `site/data/*.json` the doors render."""
    return path.startswith("tools/generate_") and path.endswith("_data.py")


def _is_broad_trigger(path: str) -> bool:
    """A change whose blast radius is any door -> run the WHOLE site suite (mechanism B)."""
    return (
        path.startswith(SITE_DATA_PREFIX)
        or _is_site_data_producer(path)
        or path in SITE_CONSUMED_LEDGERS
    )


def site_tests_for(path: str) -> list[str]:
    """Mechanism C: a changed `site/X/foo.{html,py,js,mjs}` -> its sibling `site/X/test_*.py`.

    A `site/data/*.json` change is NOT a direct source edit (it goes through the broad trigger); a
    changed test file maps to itself.
    """
    if path in SOURCE_DOOR_TESTS:
        return [t for t in SOURCE_DOOR_TESTS[path] if (ROOT / t).exists()]
    if not path.startswith(SITE_PREFIX) or path.startswith(SITE_DATA_PREFIX):
        return []
    p = Path(path)
    if p.suffix not in SITE_SOURCE_SUFFIXES:
        return []
    if p.name.startswith("test_") and p.suffix == ".py" and (ROOT / p).exists():
        return [path]
    sibling_dir = ROOT / p.parent
    return sorted(str(t.relative_to(ROOT)) for t in sibling_dir.glob("test_*.py"))


def _tool_imports(tree: ast.AST) -> set[str]:
    """The `tools.<x>` modules a file imports, read from its syntax tree (a comment naming one is
    not an import)."""
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name.split(".")[1] for a in node.names if a.name.startswith("tools."))
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "tools":
                out.update(a.name for a in node.names)
            elif node.module.startswith("tools."):
                out.add(node.module.split(".")[1])
    return out


def _feed_inputs(tool: Path, root: Path) -> list[str]:
    """The repo files a site-feed tool reads, from its module-level path constants -- or [] when
    the tool writes no `site/data/` feed. Inputs under `site/` are left to mechanisms B and C."""
    try:
        tree = ast.parse(tool.read_bytes())
    except (OSError, SyntaxError, ValueError):
        return []
    consts = []
    for n in tree.body:
        value = n.value if isinstance(n, (ast.Assign, ast.AnnAssign)) else None
        if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Div):
            value = value.right  # `ROOT / "docs/x.md"`
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            consts.append(value.value)
    if not any(c.startswith(SITE_DATA_PREFIX) for c in consts):
        return []
    return [c for c in consts if not c.startswith(SITE_PREFIX) and "/" in c
            and (root / c).is_file()]


def feed_source_tests(root: Path = ROOT) -> dict[str, set[str]]:
    """Mechanism D: a feed tool's INPUT -> the site tests that import that tool.

    14 Nov 2026: db80910fa0 edited `docs/institutional/reading_log.md` and left
    `site/data/reading_log.json` stale. Neither B nor C selects anything for a doc, so the door
    test that says so (`test_the_committed_feed_is_what_the_log_builds_today`) stayed red for 8.5
    hours and refused the next commit that happened to run the whole suite -- the delivery seat's
    direction record, which touched no input of that feed. A feed's door test now runs on the
    commit that edits the feed's input, so the red lands on the writer who caused it."""
    out: dict[str, set[str]] = {}
    inputs_of: dict[str, list[str]] = {}
    for test in sorted((root / "site").rglob("test_*.py")):
        try:
            tree = ast.parse(test.read_bytes())
        except (OSError, SyntaxError, ValueError):
            continue
        rel = str(test.relative_to(root))
        for mod in _tool_imports(tree):
            if mod not in inputs_of:
                tool = root / "tools" / f"{mod}.py"
                inputs_of[mod] = _feed_inputs(tool, root) if tool.is_file() else []
            for src in inputs_of[mod]:
                out.setdefault(src, set()).add(rel)
    return out


def plan(files: list[str]) -> tuple[str | None, list[str] | None]:
    """What the site lane runs for this change set:
      ("full", None)          -- run the whole `pytest site/` (broad trigger, mechanism B)
      ("targeted", [tests])   -- run only the sibling site tests (direct edits, mechanism C)
      (None, None)            -- no site-relevant change; skip
    """
    if any(_is_broad_trigger(f) for f in files):
        return ("full", None)
    targeted: set[str] = set()
    feeds = feed_source_tests()
    for f in files:
        targeted.update(site_tests_for(f))
        targeted.update(feeds.get(f, ()))
    if targeted:
        return ("targeted", sorted(targeted))
    return (None, None)


def _gitless_env(env: dict) -> dict:
    """Strip every GIT_* key -- same H24 hazard as `pre_commit_test_gate.py`: during a `git commit`
    the hook inherits GIT_INDEX_FILE/GIT_DIR/GIT_WORK_TREE pointing at the in-progress commit; a
    subprocess obeying them can corrupt the real index. Site tests spawn a node harness; scrubbing
    keeps any stray git invocation off the commit's index. The merge token goes with them, for the
    test gate's reason: inherited, it would narrow selection inside any test that calls a gate's
    `main()` while a merge is being gated, and nowhere else."""
    return {k: v for k, v in env.items() if not k.startswith("GIT_") and k != MERGE_PARENT_ENV}


def main() -> int:
    # A merge is selected by its combined diff, exactly as the test gate selects it: a base
    # advance that brought in someone else's site/** or generate_*_data change re-ran `pytest
    # site/` (~150 s) on work already gated on origin. Same function, so the lanes cannot drift.
    selected, why = selection_paths(staged_files(), ROOT, label="site-lane")
    if why:
        print(why)
    mode, targets = plan(selected)
    if mode is None:
        return 0  # no site-relevant change -- the site lane has nothing to guard

    # R15 FAIL-CLOSED: the .mjs render harnesses SKIP (do not fail) when node is absent, so a
    # green-with-skips run would be a FALSE pass -- the render tests never ran. An unavailable check
    # is a FAILED check: refuse the commit LOUD rather than let a site change through unverified.
    if shutil.which("node") is None:
        sys.stderr.write(
            "\n[site-lane] ❌ node NOT FOUND -- the site .mjs render harnesses would SILENTLY "
            "SKIP, so `pytest site/` cannot actually verify the doors. COMMIT REFUSED (fail-closed: "
            "an unavailable check is a FAILED check, R15). Install node, then commit.\n"
        )
        return 1

    if mode == "full":
        run_args = [str(ROOT / "site")]
        # NAME THE PATH, not the class (14 Nov): the 03:54 refusal of the seat's record could not
        # say what made a direction landing run the whole suite. It was `site/data/delivery.json`,
        # which the seat regenerates every stretch.
        tripped = [f for f in selected if _is_broad_trigger(f)]
        scope = f"whole site/ suite (broad trigger: {', '.join(tripped[:3])}"
        scope += f" and {len(tripped) - 3} more)" if len(tripped) > 3 else ")"
    else:
        run_args = list(targets or [])
        scope = f"{len(run_args)} sibling site test file(s): {', '.join(run_args)}"

    print(f"[site-lane] running {scope}")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *run_args, "-q", "--no-header",
         "-p", "no:cacheprovider"],
        cwd=str(ROOT),
        env=_gitless_env(os.environ),
    )
    if r.returncode != 0:
        sys.stderr.write(
            "\n[site-lane] ❌ SITE TESTS FAILED -- COMMIT REFUSED.\n"
            "[site-lane] A red site/** test can never wedge the publish gate (it runs tests/ only), "
            "so it is caught HERE instead (Campaign A debt E). Fix the site test, then commit. "
            "This alarms the SITE LANE only -- the tests/ publish gate is untouched.\n"
        )
        return 1
    print("[site-lane] ✓ site tests green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
