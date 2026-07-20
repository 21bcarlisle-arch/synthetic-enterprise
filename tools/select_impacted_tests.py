"""Impact-based test SELECTION via a static import graph (director test-throughput steer,
2026-07-20, sharpened priority #1). OPT-IN, additive, wired to NO gate.

WHY THIS, WHY NOW
-----------------
The director's steer: "run the tests a change actually touches, full suite on a cadence as the
net" -- and prioritise it *first* because its benefit grows with suite/population size, which is
exactly the direction the value-frontier/segmentation programme is heading. The existing
convention map (`pre_commit_test_gate.py::tests_for()`: X.py -> test_X.py by filename) is real but
SHALLOW -- it cannot see that `tests/company/billing/test_annual_statement.py` also exercises
`company/interfaces/bitemporal_event_log.py`, so a change to the event log would not select that
test. This tool closes that gap WITHOUT a new dependency: `coverage`/`pytest-cov` are NOT installed
in this environment (verified), so a coverage map is not available; a STATIC import graph is the
dependency-free way to compute "which tests transitively import a changed module."

WHAT IT IS (and is NOT)
-----------------------
IS: a read-only selector. Given a set of changed files (from git, or passed explicitly), it returns
the set of `tests/**` files whose transitive import closure reaches any changed module -- a SUPERSET
of the filename-convention map. With `--run` it invokes pytest on exactly that set; by default it
only prints the selection (and a machine-readable JSON with `--json`).

IS NOT: a replacement for any gate. Nothing in the repo calls this yet. The publish gate, the
pre-commit gate, and the full suite are all unchanged. Selection is a SPEED tool for a fork's own
inner loop ("what should I run after this edit?"); the full suite on a cadence remains the safety
net, per the steer's non-negotiable #6 and R15.

FAIL-SAFE BY DESIGN (never silently under-select)
-------------------------------------------------
Static analysis cannot see dynamic imports (`importlib`, `__import__`, string module names) or
non-Python couplings (a test that reads a JSON ledger). So the tool is deliberately CONSERVATIVE:

  * A changed file that is NOT a mappable repo `.py` module (a JSON/data/config/site file, or a
    `.py` outside the analysed roots) makes the selection UNSAFE-TO-NARROW -> it returns the
    FULL-SUITE sentinel (`full_suite=True`), i.e. "I cannot prove what this touches, run everything."
  * `--run` on a full-suite result runs `tests/` (minus the same `operational` deselection the
    publish gate uses), never a narrowed subset.

So the failure mode is "run too much," never "run too little." That is the only safe direction for
a selection tool whose whole risk is missing a real regression.

R15
---
Mutation-proven in `tests/tools/test_select_impacted_tests.py`: injecting a real regression into a
production module and asking this selector for the impacted set MUST include the test that guards it
(selection does not drop the guard), AND a non-mappable change MUST fall back to the full suite.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Roots whose .py files participate in the import graph. `site/` is EXCLUDED on purpose -- it has
# its own isolated lane (`tools/site_lane_gate.py`) and must never couple to the tests/ selection.
ANALYSED_ROOTS = (
    "background", "company", "saas", "sim", "simulation",
    "interface", "tools", "tests", "functions",
)
TEST_ROOT = "tests"

# Directories never walked (fork worktrees hold stale copies that false-map -- the known
# worktree-scan hazard; venvs/caches are noise).
_SKIP_DIR_PARTS = frozenset({
    ".git", ".claude", "node_modules", "__pycache__",
    ".venv", "venv", "site-packages", ".pytest_cache",
})


def _iter_py_files(root: Path = ROOT):
    for root_name in ANALYSED_ROOTS:
        base = root / root_name
        if not base.is_dir():
            continue
        for p in base.rglob("*.py"):
            if any(part in _SKIP_DIR_PARTS for part in p.relative_to(root).parts):
                continue
            yield p


def _module_name(rel: Path) -> str:
    """repo-relative path -> dotted module name. __init__.py -> its package."""
    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]  # strip .py
    return ".".join(parts)


def _imported_modules(path: Path, root: Path = ROOT) -> set[str]:
    """Dotted names this file imports (absolute imports; relative imports resolved to a dotted
    prefix). Returns raw dotted strings -- resolution to repo files happens against the module map."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    out: set[str] = set()
    pkg_parts = list(path.relative_to(root).parts)[:-1]  # package of this module
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                # relative import: resolve against this file's package
                base = pkg_parts[: len(pkg_parts) - (node.level - 1)]
                mod = ".".join(base + ([node.module] if node.module else []))
                if mod:
                    out.add(mod)
                    for alias in node.names:
                        out.add(f"{mod}.{alias.name}")
            elif node.module:
                out.add(node.module)
                for alias in node.names:
                    out.add(f"{node.module}.{alias.name}")
    return out


def build_graph(root: Path = ROOT):
    """Returns (module_to_file, forward) where forward maps a repo file (relative str) to the set of
    repo files it imports."""
    module_to_file: dict[str, str] = {}
    files: list[Path] = list(_iter_py_files(root))
    for p in files:
        rel = p.relative_to(root)
        module_to_file[_module_name(rel)] = str(rel)

    def resolve(dotted: str) -> str | None:
        """Longest-prefix match of a dotted import to a repo module file (handles
        `from pkg.mod import name` where `pkg.mod.name` isn't itself a module)."""
        parts = dotted.split(".")
        for cut in range(len(parts), 0, -1):
            cand = ".".join(parts[:cut])
            if cand in module_to_file:
                return module_to_file[cand]
        return None

    forward: dict[str, set[str]] = {}
    for p in files:
        rel = str(p.relative_to(root))
        deps: set[str] = set()
        for dotted in _imported_modules(p, root):
            tgt = resolve(dotted)
            if tgt is not None and tgt != rel:
                deps.add(tgt)
        forward[rel] = deps
    return module_to_file, forward


def _is_mappable(changed: str) -> bool:
    """A changed path is graph-mappable iff it is a .py file under an analysed root."""
    return changed.endswith(".py") and changed.split("/", 1)[0] in ANALYSED_ROOTS


def select(changed_files: list[str], root: Path = ROOT):
    """Core selection. Returns a dict:
      { full_suite: bool, reason: str, tests: [sorted test files], unmappable: [changed non-py] }
    full_suite=True means 'cannot safely narrow -- run everything'."""
    changed = [c.strip() for c in changed_files if c.strip()]
    unmappable = [c for c in changed if not _is_mappable(c)]
    if unmappable:
        return {
            "full_suite": True,
            "reason": f"{len(unmappable)} changed path(s) are not graph-mappable "
                      f"(non-.py or outside analysed roots); cannot prove impact -> full suite.",
            "tests": [],
            "unmappable": sorted(unmappable),
        }
    if not changed:
        return {"full_suite": False, "reason": "no changed files", "tests": [], "unmappable": []}

    _module_to_file, forward = build_graph(root)
    # Reverse graph: importee -> importers.
    reverse: dict[str, set[str]] = defaultdict(set)
    for src, deps in forward.items():
        for d in deps:
            reverse[d].add(src)

    # Multi-source BFS from the changed files over reverse edges; any tests/ file reached is impacted.
    # A changed file not present in the graph (e.g. a brand-new file) still seeds correctly: its own
    # importers are found via reverse edges once other files import it; if nothing imports it and it
    # is itself a test, it is included below.
    seen: set[str] = set(changed)
    q: deque[str] = deque(changed)
    impacted_tests: set[str] = set()
    while q:
        node = q.popleft()
        if node.startswith(TEST_ROOT + "/"):
            impacted_tests.add(node)
        for importer in reverse.get(node, ()):
            if importer not in seen:
                seen.add(importer)
                q.append(importer)
    # A changed test file is always its own guard.
    for c in changed:
        if c.startswith(TEST_ROOT + "/"):
            impacted_tests.add(c)

    return {
        "full_suite": False,
        "reason": f"{len(changed)} mappable change(s) -> {len(impacted_tests)} impacted test file(s) "
                  f"via static import graph.",
        "tests": sorted(impacted_tests),
        "unmappable": [],
    }


def _git_changed(base: str | None) -> list[str]:
    if base:
        args = ["git", "diff", "--name-only", "--diff-filter=ACM", base]
    else:
        # default: staged + unstaged working changes
        args = ["git", "diff", "--name-only", "--diff-filter=ACM", "HEAD"]
    out = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--changed", nargs="*", help="explicit changed files (default: git diff vs HEAD)")
    ap.add_argument("--base", help="git ref to diff against (default: HEAD)")
    ap.add_argument("--json", action="store_true", help="emit the selection as JSON")
    ap.add_argument("--run", action="store_true",
                    help="run pytest on the selection (full suite minus 'operational' if unsafe-to-narrow)")
    args = ap.parse_args(argv)

    changed = args.changed if args.changed is not None else _git_changed(args.base)
    result = select(changed)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[impact-select] {result['reason']}")
        if result["full_suite"]:
            for u in result["unmappable"]:
                print(f"  unmappable: {u}")
        else:
            for t in result["tests"]:
                print(f"  {t}")

    if not args.run:
        return 0

    if result["full_suite"]:
        pytest_args = [sys.executable, "-m", "pytest", "tests/", "-q", "-m", "not operational",
                       "-p", "no:cacheprovider"]
    elif not result["tests"]:
        print("[impact-select] nothing to run.")
        return 0
    else:
        pytest_args = [sys.executable, "-m", "pytest", *result["tests"], "-q",
                       "-p", "no:cacheprovider"]
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(pytest_args, cwd=str(ROOT), env=env).returncode


if __name__ == "__main__":
    sys.exit(main())
