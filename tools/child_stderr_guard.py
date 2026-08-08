"""H30 — the R10 class closure: a reported child failure must carry its stderr.

THE DEFECT, AND WHY THE INSTANCE FIX IS NOT THE CLOSURE
-------------------------------------------------------
`background/sim_runner.py::run_simulation` launched the simulation with
`subprocess.run(...)` and no stderr capture. Under a daemon, fd 2 is a socket
nobody reads, so the child's traceback was destroyed at the moment it was
written. Eight consecutive failures on 2026-08-08 produced `rc=1` and nothing
else, and the fault (`NameError: _IC_SEGMENTS`) was only found by re-running
the child by hand.

Adding `stderr=subprocess.PIPE` there closes ONE site. The CLASS is "a
background process that tells a human its child FAILED, while having thrown
away the only artefact that says WHY", and its supply is unlimited: not
capturing is the default, so every new launch site starts out defective and
nothing complains until the next unexplained loop. R10 says an
absurdity-class defect may not be closed with an instance fix — so this guard
makes the class fail at commit time instead.

WHAT IT FLAGS
-------------
A launch site is in scope only when BOTH hold inside its enclosing function:

  1. FAILURE-AWARE  -- the function reads a `.returncode`, handles
     `TimeoutExpired`/`CalledProcessError`, or passes `check=True`; and
  2. HUMAN-REPORTING -- the function calls a reporting channel (`log`,
     `notify`, `send_ntfy`, `update_agent_status`, `print`).

Together those mean: this code TELLS SOMEONE the child failed. That report is
what R5 requires to carry a diagnostic payload, and it cannot unless stderr
was captured. A launch whose failure nobody reports is out of scope on
purpose — `subprocess.run(["git", "rev-parse", ...])` inside a helper that
returns a value is not this defect, and a guard that fired on it would be
switched off within a week (which is how controls really die).

`stderr=subprocess.DEVNULL` counts as a VIOLATION, not as an exemption.
Explicitly discarding the payload and then reporting the failure is the same
defect written more deliberately; a site that genuinely wants that must say so
in EXEMPT below, where the reason is reviewable.

SCOPE, AND WHY IT IS NOT AN EXCLUSION
-------------------------------------
The scanned root is `background/` — the UNATTENDED daemons. That is the whole
of the defect's habitat: it exists because the parent's fd 2 is a socket or a
detached tmux pane, so an inherited stderr goes nowhere a human will ever
look. The gate scripts under `tools/` (`pre_commit_test_gate`,
`site_lane_gate`, `select_impacted_tests`) deliberately inherit both streams
and are NOT flagged, because their parent's fd 2 is the committing human's
terminal: the payload reaches a reader by the shortest possible route, and
capturing it would make things worse, not better.

A scope stated only in prose is an exclusion that fails open the moment a new
daemon lands somewhere else. So the scope is CHECKED, not asserted:
`uncovered_declared_entrypoints()` reads `background/process_manifest.yaml`
— the IaC declaration of every process that should be running — and if any
non-retired process's Python entrypoint sits outside the scanned root, the
guard reports rc 2 (COULD NOT RUN). A daemon the guard cannot see is a
coverage hole, and a coverage hole is a failure, not a pass.

FAIL-CLOSED (R15)
-----------------
  - MISSING ROOT     -> rc 2. A control that checked nothing has FAILED.
  - UNPARSEABLE FILE -> rc 2. A violation must not be able to hide behind a
                        SyntaxError.
  - EMPTY SCAN       -> rc 2. Vacuity guard: 0 violations over 0 files is not
                        evidence (the 1557/1557-passed-while-the-field-was-
                        absent shape).
  - rc 2 is distinct from rc 0, so "could not run" can never be read as
    "passed".

Not a tautology: the guard reads SOURCE TEXT for the presence of a capture
argument, while the thing it protects is the runtime content of a log line.
The two come from different places, so the check cannot pass by construction.

Exit code 0 = clean, 1 = violations found, 2 = the guard could not run.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

#: Launcher attributes on the `subprocess` module that start a child whose
#: stderr is inherited unless the caller says otherwise.
LAUNCHERS = {"run", "Popen", "call", "check_call", "check_output"}

#: Calls that put text in front of a human (a log file, a phone, the status
#: board). Matched by bare name or attribute, so `log(...)`, `self.log(...)`
#: and `logging.error(...)` all count.
REPORTERS = {
    "log", "notify", "send_ntfy", "update_agent_status",
    "print", "warning", "error", "critical", "exception",
}

#: Argument names that keep the child's stderr. `capture_output=True` takes
#: both streams; `stderr=` takes it explicitly (PIPE, or a file the caller
#: reads later).
CAPTURE_KWARGS = {"capture_output", "stderr"}

#: Launch sites allowed to discard stderr while still reporting a failure,
#: each with the reason it is not the H30 defect. Keyed "path::function".
#: Deliberately empty at the time of writing: all ten sites the guard found
#: were fixed rather than exempted. An entry here is a claim that a human
#: diagnosing this failure does not need the child's words — which is rarely
#: true, so it should be argued in the value, not just listed.
EXEMPT: dict[str, str] = {}


#: The IaC declaration of the process set the defect lives in.
PROCESS_MANIFEST = Path(__file__).resolve().parent.parent / "background" / "process_manifest.yaml"


def uncovered_declared_entrypoints(root: Path, manifest: Path | None = None) -> list[str]:
    """Declared, non-retired daemons whose Python entrypoint is NOT under `root`.

    Any non-empty result is a COVERAGE HOLE: the guard would report "clean"
    while a live daemon it never read could hold the defect. Raises rather
    than returning [] if the manifest is missing or unreadable — an
    unavailable check is a FAILED check (R15 fail-silent), and a coverage
    check that shrugs is the exact shape that lets a hole through.

    Entries with no `.py` in their command (the tmux seat sentinel, shell
    launchers) are not Python source and cannot carry this defect, so they are
    not required to be under the root.
    """
    path = manifest or PROCESS_MANIFEST
    if not path.is_file():
        raise FileNotFoundError(
            "child_stderr_guard: process manifest %s is missing -- cannot prove the "
            "scanned root covers the declared daemons" % path
        )
    try:
        import yaml
    except ModuleNotFoundError as exc:  # pragma: no cover - env without pyyaml
        raise FileNotFoundError(
            "child_stderr_guard: pyyaml unavailable, cannot read %s -- an "
            "unavailable coverage check is a FAILED check" % path
        ) from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    uncovered: list[str] = []
    for proc in data.get("processes") or []:
        if not isinstance(proc, dict) or proc.get("state") == "retired":
            continue
        command = str(proc.get("command") or "")
        for token in command.split():
            if not token.endswith(".py"):
                continue
            entry = (root.parent / token) if not Path(token).is_absolute() else Path(token)
            try:
                entry.resolve().relative_to(root.resolve())
            except ValueError:
                uncovered.append("%s (%s)" % (proc.get("session", "?"), token))
    return uncovered


def _is_launcher(node: ast.Call) -> bool:
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr in LAUNCHERS:
        # `subprocess.run(...)` — anchored on the module name so an unrelated
        # `pool.run(...)` is not dragged in.
        return isinstance(func.value, ast.Name) and func.value.id == "subprocess"
    return False


def _captures_stderr(node: ast.Call) -> bool:
    for kw in node.keywords:
        if kw.arg is None:
            # `**kwargs` — the capture may be in there. Treat as captured:
            # the guard cannot see through it, and flagging it would be a
            # false positive on code it genuinely cannot judge.
            return True
        if kw.arg not in CAPTURE_KWARGS:
            continue
        if _is_devnull(kw.value):
            # Explicit discard. Reported failure + deliberately destroyed
            # payload is still the defect.
            return False
        return True
    return False


def _is_devnull(node: ast.AST) -> bool:
    return isinstance(node, ast.Attribute) and node.attr == "DEVNULL"


def _calls_a_reporter(body: list[ast.AST]) -> bool:
    for n in body:
        if not isinstance(n, ast.Call):
            continue
        func = n.func
        if isinstance(func, ast.Name) and func.id in REPORTERS:
            return True
        if isinstance(func, ast.Attribute) and func.attr in REPORTERS:
            return True
    return False


def _is_failure_aware(body: list[ast.AST]) -> bool:
    for n in body:
        if isinstance(n, ast.Attribute) and n.attr == "returncode":
            return True
        if isinstance(n, ast.Name) and n.id in {"TimeoutExpired", "CalledProcessError"}:
            return True
        if isinstance(n, ast.Attribute) and n.attr in {"TimeoutExpired", "CalledProcessError"}:
            return True
        if isinstance(n, ast.Call) and any(
            kw.arg == "check" and getattr(kw.value, "value", None) is True
            for kw in n.keywords
        ):
            return True
    return False


def _display_path(path: Path, repo_root: Path) -> str:
    """Repo-relative where possible, absolute otherwise — `--root` may point
    outside the repo (the R15 tests scan a tmp_path)."""
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def scan_file(path: Path, repo_root: Path) -> list[tuple[int, str]]:
    """Violations in one file as (lineno, enclosing function name).

    A file that will not parse raises — see the fail-closed note in the module
    docstring.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    rel = _display_path(path, repo_root)
    violations: list[tuple[int, str]] = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if "%s::%s" % (rel, fn.name) in EXEMPT:
            continue
        body = list(ast.walk(fn))
        if not (_calls_a_reporter(body) and _is_failure_aware(body)):
            continue
        for n in body:
            if isinstance(n, ast.Call) and _is_launcher(n) and not _captures_stderr(n):
                violations.append((n.lineno, fn.name))
    return violations


def scan(root: Path, repo_root: Path) -> tuple[list[str], int]:
    """Return (violation messages, number of files actually scanned)."""
    if not root.is_dir():
        raise FileNotFoundError(
            "child_stderr_guard: scan root %s does not exist -- a control that "
            "checks nothing has FAILED, not passed" % root
        )
    messages: list[str] = []
    scanned = 0
    for path in sorted(root.rglob("*.py")):
        scanned += 1
        for lineno, fn_name in scan_file(path, repo_root):
            messages.append(
                "%s:%d: %s() reports this child's FAILURE to a human but does not "
                "capture its stderr -- the report cannot carry a diagnostic payload "
                "(R5/H30). Pass stderr=subprocess.PIPE (or capture_output=True) and "
                "log background.child_diagnostics.stderr_tail(result.stderr)."
                % (_display_path(path, repo_root), lineno, fn_name)
            )
    return messages, scanned


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="H30 child-stderr class guard")
    parser.add_argument(
        "--root",
        default=str(repo_root / "background"),
        help="directory to scan (default: background/)",
    )
    args = parser.parse_args(argv)
    root = Path(args.root)
    default_root = repo_root / "background"

    # Coverage check first: proving the scan LOOKS at the declared daemons has
    # to happen before its result means anything. Only meaningful against the
    # real root -- the R15 tests scan fixture trees the manifest knows nothing
    # about, and demanding coverage there would be nonsense.
    if root.resolve() == default_root.resolve():
        try:
            uncovered = uncovered_declared_entrypoints(root)
        except Exception as exc:  # any failure to prove coverage is a FAILURE, not a pass
            print("CHILD STDERR GUARD: COULD NOT RUN -- %s" % exc, file=sys.stderr)
            return 2
        if uncovered:
            print(
                "CHILD STDERR GUARD: COULD NOT RUN -- %d declared daemon(s) sit outside "
                "the scanned root %s, so a clean result would not cover them: %s"
                % (len(uncovered), root, "; ".join(uncovered)),
                file=sys.stderr,
            )
            return 2

    try:
        messages, scanned = scan(root, repo_root)
    except (FileNotFoundError, SyntaxError, UnicodeDecodeError) as exc:
        print("CHILD STDERR GUARD: COULD NOT RUN -- %s" % exc, file=sys.stderr)
        return 2

    if scanned == 0:
        print(
            "CHILD STDERR GUARD: COULD NOT RUN -- scanned 0 files under %s" % args.root,
            file=sys.stderr,
        )
        return 2

    if messages:
        print("CHILD STDERR GUARD: %d violation(s)" % len(messages), file=sys.stderr)
        for message in messages:
            print("  " + message, file=sys.stderr)
        return 1

    print("CHILD STDERR GUARD: clean (%d files scanned)" % scanned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
