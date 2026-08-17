#!/usr/bin/env python3
"""EVERY entrypoint this repo launches AS A SCRIPT PATH must import in SCRIPT MODE.

THE DEFECT THIS CLOSES (2026-08-17, failure #258 of the publish-gate wedge episode; instance:
`background/process_run_complete.py`). A top-level `from background.publish_step_ledger import
PublishStepLedger` landed in a module that both daemons launch as a script path:

    subprocess.run([sys.executable, ".../background/process_run_complete.py", marker],
                   cwd=PROJECT_DIR)          # sim_runner.py, background_worker.py

Python seeds `sys.path[0]` from the SCRIPT'S DIRECTORY, never from cwd. Inside that process the
root is `background/`, so `import background` cannot resolve and every publish died at the import
line before `main()` was reached. `cwd=PROJECT_DIR` looks like it should prevent this and does
nothing whatsoever.

WHY IT WAS INVISIBLE FOR A DAY (R15, wrong subject). A smoke check did exist --
`start_worker.sh`'s `python3 -c 'import background.process_run_complete'` -- and it was GREEN the
entire time, because `-c` puts cwd on `sys.path` and `-m` puts the root on it. Every entry mode
the repo CHECKED was a mode nothing actually uses to launch these files. The control and the
daemons disagreed about how the module is entered, so the control could not fail.

WHY THIS IS A CLASS CONTROL AND NOT AN INSTANCE TEST (R10). Fixing the one import would have left
15 sibling entrypoints one careless top-level import away from the same wedge -- and the fix
lands in the one file whose breakage stops ALL publishing, so the class is expensive by
construction. The population here is DERIVED, never hand-listed:

  * `background/process_manifest.yaml` -- the committed daemon set. A `command: python3 <x>.py`
    entry is a script-mode launch by definition, so a daemon added to the manifest tomorrow is
    covered by this test the moment it is declared, with nobody remembering to come back here.
  * an AST sweep of `background/` and `tools/` for in-code `subprocess` launches whose argv is
    `[sys.executable, <a .py path>, ...]`. THIS HALF IS THE ONE THAT MATTERS: the module that
    actually broke is NOT in the manifest -- it is a subprocess of two daemons that are. A
    manifest-only population would have been green through the whole outage.

`-m background.foo` launches are deliberately NOT collected: module mode puts the root on
`sys.path` itself and cannot exhibit this defect.

HOW EACH ENTRYPOINT IS EXERCISED. A subprocess reproduces script mode exactly -- `sys.path[0]` =
the script's own directory, cwd somewhere foreign -- and executes the module's TOP LEVEL under a
name that is not `__main__`, so the import block runs (where this defect lives) and the
`if __name__ == "__main__":` body does not (no daemon is started, no marker is processed).

MUTATION-TESTED BOTH WAYS (R15), 2026-08-17: with the `sys.path` bootstrap removed from
`process_run_complete.py` this test fails with `ModuleNotFoundError: No module named 'background'`
against that file by name; with it restored, all 16 discovered entrypoints pass.
"""
import ast
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
PROCESS_MANIFEST = PROJECT_DIR / "background" / "process_manifest.yaml"
SWEPT_DIRS = ("background", "tools")

# The floor the discovery must clear. NOT the population -- a fail-open guard on the two
# discovery halves above (R15: a census that silently finds nothing passes vacuously). If a
# refactor moves the manifest or changes the launch idiom, this test says so instead of going
# quietly green over an empty set. Both named files are load-bearing: the first is the module
# whose breakage wedged publishing, the second is a manifest daemon.
MUST_DISCOVER = (
    "background/process_run_complete.py",   # subprocess half -- absent from the manifest
    "background/supervisor.py",             # manifest half
)
MIN_DISCOVERED = 8

# Executes the module's top level in a faithful script-mode sys.path, under a non-__main__ name.
_SCRIPT_MODE_PROBE = """\
import importlib.util
import pathlib
import sys

target = pathlib.Path(sys.argv[1]).resolve()
# EXACTLY what CPython does for `python3 path/to/script.py`, and the whole point of this test:
# the SCRIPT'S directory, not the cwd, is what lands on sys.path.
sys.path.insert(0, str(target.parent))
spec = importlib.util.spec_from_file_location("_script_mode_probe", str(target))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
"""


def _manifest_script_launches():
    """`command: python3 <x>.py` entries. Parsed with a line scan rather than a YAML load so the
    test states its own dependency surface -- the field is one flat scalar and a parser here
    would be a second thing to keep true."""
    if not PROCESS_MANIFEST.exists():
        return set()
    found = set()
    for raw in PROCESS_MANIFEST.read_text().splitlines():
        line = raw.strip()
        if not line.startswith("command:"):
            continue
        parts = line.split("command:", 1)[1].strip().strip('"').strip("'").split()
        # `python3 -m background.foo` is module mode -- immune, and deliberately not collected.
        if len(parts) >= 2 and parts[0].startswith("python") and parts[1].endswith(".py"):
            found.add(parts[1])
    return found


def _literal_py_names(node):
    """Every `"...py"` string literal anywhere inside an expression."""
    return {n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and n.value.endswith(".py")}


def _subprocess_script_launches():
    """AST sweep for `subprocess.<run|Popen|check_output>([sys.executable, <script>, ...])`.

    The launched path is usually bound to a local first (`processor = Path(__file__).parent /
    'process_run_complete.py'`), so a bare read of argv[1] sees only a Name. Resolution is
    therefore two-pass: collect every `.py` literal assigned to a Name in the module, then look
    argv[1] up in that table. A `.py` literal that resolves to no file in the swept dirs is
    dropped -- this is a discovery pass, and a wrong guess here would be a phantom red."""
    launched = set()
    for directory in SWEPT_DIRS:
        for source in sorted((PROJECT_DIR / directory).rglob("*.py")):
            try:
                tree = ast.parse(source.read_text())
            except (SyntaxError, UnicodeDecodeError):
                continue

            assigned = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    names = _literal_py_names(node.value)
                    for target in node.targets:
                        if isinstance(target, ast.Name) and len(names) == 1:
                            assigned[target.id] = next(iter(names))

            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                    continue
                if node.func.attr not in ("run", "Popen", "check_output", "check_call"):
                    continue
                if not (node.args and isinstance(node.args[0], ast.List)):
                    continue
                argv = node.args[0].elts
                if len(argv) < 2:
                    continue
                head = argv[0]
                is_python = (
                    (isinstance(head, ast.Attribute) and head.attr == "executable")
                    or (isinstance(head, ast.Constant) and str(head.value).startswith("python"))
                )
                if not is_python:
                    continue

                candidates = _literal_py_names(argv[1])
                for name in ast.walk(argv[1]):
                    if isinstance(name, ast.Name) and name.id in assigned:
                        candidates.add(assigned[name.id])

                for candidate in candidates:
                    basename = Path(candidate).name
                    for directory in SWEPT_DIRS:
                        resolved = PROJECT_DIR / directory / basename
                        if resolved.exists():
                            launched.add(f"{directory}/{basename}")
    return launched


def discovered_script_entrypoints():
    """The union both halves agree to cover, as repo-relative paths."""
    found = set()
    for rel in _manifest_script_launches() | _subprocess_script_launches():
        rel = rel.lstrip("./")
        if (PROJECT_DIR / rel).exists() and rel.startswith(SWEPT_DIRS):
            found.add(rel)
    return sorted(found)


def test_the_discovery_itself_found_the_population():
    """The fail-open guard. A green result below is only evidence if this passed first."""
    found = discovered_script_entrypoints()
    assert len(found) >= MIN_DISCOVERED, (
        "script-mode entrypoint discovery found only {} entrypoint(s) ({}). Both halves -- the "
        "process manifest and the subprocess AST sweep -- are meant to be non-empty; a collapsed "
        "census would let this whole file pass vacuously. Repair the discovery, not this "
        "floor.".format(len(found), ", ".join(found) or "none")
    )
    for required in MUST_DISCOVER:
        assert required in found, (
            "{} is launched as a script path but the discovery no longer sees it. That is the "
            "exact blind spot this test exists for -- the module that wedged publishing for a "
            "day is a SUBPROCESS of two daemons, not a manifest entry, so losing the AST half "
            "would leave the population looking healthy.".format(required)
        )


@pytest.mark.parametrize("rel_path", discovered_script_entrypoints())
def test_entrypoint_imports_when_launched_as_a_script_path(rel_path):
    """Run the module's top level the way the daemons enter it. A top-level `import background`
    with no path bootstrap dies here, before `main()` is ever reached."""
    target = PROJECT_DIR / rel_path
    result = subprocess.run(
        [sys.executable, "-c", _SCRIPT_MODE_PROBE, str(target)],
        cwd=str(PROJECT_DIR.parent),   # deliberately NOT the repo root: cwd must not rescue it
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        "{} FAILED to import when launched as a script path (`python3 {}`), which is exactly how "
        "this repo launches it. sys.path[0] is the script's own directory, so a top-level "
        "`from background...`/`import tools...` cannot resolve and cwd does not help. Add the "
        "repo-root sys.path bootstrap ABOVE the import (see the header of "
        "background/process_run_complete.py) rather than deferring the failure with a bare "
        "try/except -- a swallowed import surfaces thousands of lines later as a NameError with "
        "the true cause long gone.\n\nstderr:\n{}".format(
            rel_path, rel_path, result.stderr[-3000:] or "(empty)")
    )
