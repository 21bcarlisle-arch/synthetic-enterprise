#!/usr/bin/env python3
"""A test file may not import a first-party name that does not exist.

THE DEFECT, 2026-09-01 (`WORKER_FINDING_A_TEST_REWRITTEN_AHEAD_OF_ITS_API_DISABLED_413_
ARCHITECTURE_CONTROLS_FOR_NINE_HOURS_2026-09-01`).
`tests/architecture/test_a_departure_reading_declares_its_population.py` was rewritten in the
working tree at 21:32 the previous evening to prove an API that was never written — eight names
that exist nowhere in the repository, on any branch, in any worktree. The implementing lane wrote
the proof and stopped.

WHY THAT IS NOT ONE RED TEST. It is a COLLECTION error, so pytest stops before running anything in
the directory. With the file restored `pytest tests/architecture/` collects 413 tests; with it in
place it collects none and exits. For nine and a half hours every architecture control here — the
population-floor ratchet, the unlanded-falsifier controls, the constant-origin gate — was not
failing but NOT RUNNING. **One unimportable module is not one lost control; it is every control
that shares its directory.** The same mechanism was found inside the commit gate three days earlier
(`..._AN_IMPORTERROR_COSTS_THE_WHOLE_SUITE_2026-08-28`).

WHY NOTHING SAID SO. A red is loud. An uncollectable directory is QUIET, because the thing that
would have complained is inside it. The lane never committed, so no gate ever ran against it.

WHY THIS SHAPE AND NOT A WIDER ONE. The tempting versions are all worse. "Every test must pass" is
not the property — a red test is a working control, and this repo deliberately carries reds.
"Import every test module" executes 400+ modules with their fixtures and side effects to learn one
static fact. "A daemon that watches the working tree" is a control guarding controls, and 117
harness atoms are the evidence of where that ends. The property is narrower than any of them and it
is the one that was violated: **a name imported from a first-party module is bound in that
module.** It is decided by parsing two files and it costs nothing to run.

STATIC, AND THAT IS A LIMITATION WORTH STATING. This reads the target module's AST rather than
importing it, so a name bound by machinery no parser can see — `globals()[...] = x`, a metaclass,
a C extension — would read as absent. Every first-party module in this repository binds its public
names with a plain assignment, `def`, `class` or an import, and the sweep below passes on all of
them; if that ever stops being true the answer is to widen the collector, never to add an
exemption list.

FAIL-CLOSED ON A TARGET THAT CANNOT BE READ. A first-party module named by an import and missing
from the tree, or present and unparseable, is a FAILURE and not a skip — "I could not check
whether this name exists" is not compatible with a test file asserting that it does. (R15 killer
pattern 3, and this project has found the fail-open direction of it three times in one day.)

THE SUBJECT IS THE TRACKED TREE, NOT THE DIRECTORY. As first written this walked
`TESTS.rglob("test_*.py")`, which is the filesystem — so its verdict depended on whichever
scratch files the other lanes happened to have on disk at the moment it ran. That is the ruff
ratchet's failure one level down: a control demanding a property of the SHARED WORKING TREE
refuses every lane's commit whenever any lane is mid-edit, and the lane it blocks is never the
lane that broke it. Measured 2026-09-01: run against a `git archive HEAD` checkout with five
untracked controls copied in, this test failed naming `tests/background/test_class_debt.py`,
whose subject `background/class_debt.py` is untracked — a red manufactured entirely by which
uncommitted files were beside it, on a tree where it is green.

Scoping to `git ls-files` costs nothing that matters. The defect this exists to catch is a test
file that reaches a gate — and the gate grades the commit, where tracked is exactly the
population. An uncommitted broken test still takes its directory out of collection locally, but
it does that to its own author, in their own tree, in the same minute they wrote it; it becomes
everyone's problem only when it lands, which is when this fires.
"""
from __future__ import annotations

import ast
import pathlib
import subprocess

PROJECT = pathlib.Path(__file__).resolve().parents[2]
TESTS = PROJECT / "tests"

#: The top-level packages that are OURS. A name imported from anything else is somebody else's
#: contract and is not this control's business — checking `pytest` or `numpy` statically would
#: report on the environment rather than on the tree.
FIRST_PARTY = ("background", "company", "saas", "simulation", "tools", "tests")

#: POPULATION FLOOR, dated 2026-09-01. Every scanning control here carries one: without it this
#: test reports "no bad imports" identically whether the tree is clean or the walk found no test
#: files at all — which is precisely how a control keyed to a structure that moved goes quiet
#: instead of loud. Measured at **8,001 first-party import edges across 1,444 test modules** on
#: the day it was written; the floors sit just under those, with only enough slack for ordinary
#: file churn, because both can only rise as tests are added.
FLOOR_MODULES = 1_400
FLOOR_EDGES = 7_800


def _module_path(dotted: str) -> pathlib.Path | None:
    """The `.py` file a dotted first-party name resolves to, or None."""
    base = PROJECT / pathlib.Path(*dotted.split("."))
    if base.is_dir():
        init = base / "__init__.py"
        return init if init.is_file() else None
    module = base.with_suffix(".py")
    return module if module.is_file() else None


def _exports(dotted: str) -> set[str] | None:
    """Every name `from <dotted> import X` may legally bind, or None if that cannot be read.

    A PACKAGE EXPORTS ITS SUBMODULES, and getting that wrong is not a detail — it was the first
    draft's bug and it accused 798 import edges. `from tools import wait_for` names a MODULE,
    not an attribute of `tools/__init__.py`, and four of this repository's five first-party
    packages (`tools`, `background`, `saas`, `simulation`) have no `__init__.py` at all. A
    resolver that only read `__init__.py` therefore reported every one of their submodule
    imports as absent — a control failing loudly on correct code, which is the direction that
    gets a control deleted rather than fixed.
    """
    base = PROJECT / pathlib.Path(*dotted.split("."))
    names: set[str] = set()
    if base.is_dir():
        names.update(p.stem for p in base.glob("*.py") if p.stem != "__init__")
        names.update(p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith("."))
        init = base / "__init__.py"
        if init.is_file():
            try:
                names.update(_bound_names(ast.parse(init.read_text(
                    encoding="utf-8", errors="replace"))))
            except SyntaxError:
                return None
        return names
    module = base.with_suffix(".py")
    if not module.is_file():
        return None
    try:
        return _bound_names(ast.parse(module.read_text(encoding="utf-8", errors="replace")))
    except SyntaxError:
        return None


def _bound_names(tree: ast.AST) -> set[str]:
    """Every name a module binds at any level of its own body.

    WALKS THE WHOLE TREE rather than the top level only, deliberately: this repository binds
    real public names inside `try/except ImportError` fallbacks and `if TYPE_CHECKING` blocks,
    and a top-level-only collector would report those as absent. Names bound inside a `def` or
    `class` body are NOT module attributes, so those bodies are not descended into.
    """
    names: set[str] = set()

    def visit(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(child.name)
                continue  # its body binds locals, not module attributes
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    names.update(
                        n.id for n in ast.walk(target) if isinstance(n, ast.Name)
                    )
            elif isinstance(child, (ast.AnnAssign, ast.AugAssign)):
                if isinstance(child.target, ast.Name):
                    names.add(child.target.id)
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                for alias in child.names:
                    if alias.name == "*":
                        # A star import re-exports an unknown set, so this module can no longer
                        # be shown NOT to bind a name. Recorded as the wildcard and handled by
                        # the caller, which skips the module rather than accusing it falsely.
                        names.add("*")
                    else:
                        names.add(alias.asname or alias.name.split(".")[0])
            visit(child)

    visit(tree)
    return names


def _tracked_test_modules() -> list[pathlib.Path]:
    """Every `test_*.py` the REPOSITORY holds, not every one on this disk.

    OUTSIDE A REPOSITORY THE FILESYSTEM *IS* THE ANSWER, and that fallback is load-bearing
    rather than a hedge. The publish gate grades HEAD by exporting it with `git archive`, which
    writes the files and no `.git`; there, every file present is by construction a tracked file,
    so walking the directory and listing the index name the same population. Without this branch
    the control would return nothing at exactly the moment it matters, the floors would fire, and
    a control written to stop a wedge would become one.

    Inside a repository the index is the subject, so another lane's uncommitted scratch file
    cannot colour this verdict. Either way an empty population reaches the floors below, which
    turn it into a loud red rather than a clean bill of health.
    """
    try:
        inside = subprocess.run(
            ["git", "-C", str(PROJECT), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=60,
        )
        if inside.returncode == 0 and inside.stdout.strip() == "true":
            out = subprocess.run(
                ["git", "-C", str(PROJECT), "ls-files", "-z", "--", "tests/"],
                capture_output=True, text=True, timeout=60, check=True,
            ).stdout
            return sorted({
                PROJECT / p for p in out.split("\0")
                if p.endswith(".py") and pathlib.Path(p).name.startswith("test_")
            })
    except (subprocess.SubprocessError, OSError):
        pass
    return sorted(TESTS.rglob("test_*.py"))


def _edges() -> tuple[list[tuple[str, str, str]], int, int]:
    """Every `from <first-party> import <name>` in the test tree.

    Returns (offenders, modules_walked, edges_walked). An offender is
    (test file, target module, name).
    """
    offenders: list[tuple[str, str, str]] = []
    cache: dict[str, set[str] | None] = {}
    modules = edges = 0

    for path in _tracked_test_modules():
        modules += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            offenders.append((str(path.relative_to(PROJECT)), "<itself>", "does not parse"))
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.level or not node.module:
                continue
            if not node.module.startswith(FIRST_PARTY):
                continue
            if node.module not in cache:
                cache[node.module] = _exports(node.module)
            bound = cache[node.module]
            rel = str(path.relative_to(PROJECT))
            if bound is None:
                # FAIL-CLOSED: a first-party target that is absent or unparseable.
                offenders.append((rel, node.module, "<target absent or unparseable>"))
                continue
            if "*" in bound:
                continue  # cannot be shown not to bind it
            for alias in node.names:
                edges += 1
                if alias.name != "*" and alias.name not in bound:
                    offenders.append((rel, node.module, alias.name))
    return offenders, modules, edges


def test_no_test_module_imports_a_first_party_name_that_does_not_exist():
    """THE ONE LEG. A test file naming an API that was never written takes its whole directory
    out of collection, silently, for as long as nobody commits."""
    offenders, modules, edges = _edges()
    assert offenders == [], (
        "these test files import first-party names that are bound nowhere in their target "
        "module. An unimportable test module is not one lost control -- pytest stops "
        "collecting the whole directory, so every control beside it stops running too:\n"
        + "".join(f"    {f}: from {m} import {n}\n" for f, m, n in offenders)
        + "\n    Either land the API the test proves, or park the test where pytest cannot "
          "collect it (`docs/staging/in_progress/`, `.py.txt`) and file what is owed. Do NOT "
          "delete the proof to make the suite green."
    )
    assert modules >= FLOOR_MODULES, (
        f"walked {modules} test modules, floor {FLOOR_MODULES} (2026-09-01). A scan that finds "
        "nothing reports a clean tree exactly like a scan whose subject has moved."
    )
    assert edges >= FLOOR_EDGES, (
        f"checked {edges} first-party import edges, floor {FLOOR_EDGES} (2026-09-01). The "
        "offender list being empty means nothing if the population collapsed."
    )


def test_MUTATION_a_name_bound_only_inside_a_try_block_is_still_bound(tmp_path):
    """The fail-LOUD direction, which is the one that gets a control deleted. This repository
    binds real public names inside `try/except ImportError` fallbacks and `if TYPE_CHECKING`
    blocks; a top-level-only collector would accuse every one of them."""
    tree = ast.parse(
        "try:\n    from a import thing\nexcept ImportError:\n    thing = None\n"
        "if TYPE_CHECKING:\n    Alias = int\n"
    )
    assert {"thing", "Alias"} <= _bound_names(tree)


def test_MUTATION_a_name_bound_inside_a_function_is_not_a_module_attribute():
    """The other direction. A collector that walked into function bodies would call every local
    variable an export, and the control would pass on the very import that fails."""
    tree = ast.parse("def f():\n    local_only = 1\n    return local_only\n")
    assert "f" in _bound_names(tree)
    assert "local_only" not in _bound_names(tree)


def test_MUTATION_the_real_defect_is_detected():
    """The founding case, reconstructed: the parked rewrite imported `book_departure_level`
    from `tools.departure_population`, which binds no such name."""
    target = _module_path("tools.departure_population")
    assert target is not None, "the module the founding case named is gone from the tree"
    bound = _bound_names(ast.parse(target.read_text(encoding="utf-8", errors="replace")))
    assert "declare_rows" in bound, "sanity: a name that IS bound must read as bound"
    assert "book_departure_level" not in bound, (
        "`book_departure_level` now exists -- the parked rewrite at "
        "`docs/staging/in_progress/PARKED_test_a_departure_reading_declares_its_population_"
        "2026-09-01.py.txt` can be restored, and this test updated to a name that is still "
        "absent or deleted along with the finding it proves"
    )
