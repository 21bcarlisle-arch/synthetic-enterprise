"""Epistemic Verifier — scans code changes for SIM/company barrier violations.

Run at phase close: python3 -m tools.epistemic_verifier [--diff | --files file1 file2...]

Checks company/ code for direct reads of SIM internals that bypass the
company/interfaces/sim_interface.py seam.

Exit code 0 = PASS, exit code 1 = FAIL (violations found).
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import warnings
from pathlib import Path

# Imports from these modules are allowed in company/ code (the approved seam)
APPROVED_SEAM = "company/interfaces/sim_interface"

# SIM runner imports allowed in saas/reporting/ (structural orchestration, not epistemic).
# These run the SIM as a data source -- they do not read SIM internals into company state.
APPROVED_ORCHESTRATION = [
    "simulation.run_phase4c_on_phase2b",
    "simulation.run_segments",
]

# Importing directly from these is a violation if found in company/ files
FORBIDDEN_SOURCES = [
    r"^from sim\.",
    r"^from sim import",
    r"^import sim\.",
    r"^from simulation\.",
    r"^from simulation import",
    r"^import simulation\.",
]

# Files and directories that are allowed to cross the seam freely
EXEMPT_PATHS = {
    "tests/",             # tests may import anything
    "background/",        # orchestrator layer
    "simulation/",        # is the simulation
    "company/interfaces/",  # the approved seam itself
    "tools/",             # dev tools
}

# Company-layer paths that must be checked
COMPANY_PATHS = ["company/", "saas/"]


def _get_diff_files() -> list[str]:
    """Get changed company/ files from current git diff (HEAD vs working tree + index).

    `--diff-filter=d` EXCLUDES deletions: a file removed in the diff no longer
    exists on disk, so scanning it would (correctly) find nothing -- but that
    absence must never be conflated with the FAIL-SILENT case of a file that was
    supposed to be scanned and could not be read. Deletions are dropped here so
    that a missing path reaching _scan_file is always a genuine unavailability.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=d", "HEAD"],
        capture_output=True, text=True,
    )
    files = result.stdout.strip().splitlines()
    # Also check staged changes
    result2 = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=d", "--cached"],
        capture_output=True, text=True,
    )
    files += result2.stdout.strip().splitlines()
    return sorted(set(files))


def _is_exempt(path: str) -> bool:
    return any(path.startswith(e) for e in EXEMPT_PATHS)


def _is_company_file(path: str) -> bool:
    return (path.startswith("company/") or path.startswith("saas/")) and path.endswith(".py")


# Root package names whose direct import into company/ code is a wall breach.
_FORBIDDEN_ROOTS = ("sim", "simulation")


def _module_is_forbidden(module: str | None) -> bool:
    """True iff a dotted module name is a forbidden SIM import.

    Matches the package itself (``sim`` / ``simulation``) and any submodule
    (``simulation.weather_engine``), independent of source-text whitespace,
    aliasing, or indentation -- the FAIL-OPEN gaps a line-anchored regex misses
    (``from  simulation.x import y`` with stray spaces, ``import simulation``
    with no dotted tail, ``import os; import simulation.x`` on one physical
    line). The approved orchestration modules are exempt.
    """
    if not module:
        return False
    root = module.split(".", 1)[0]
    if root not in _FORBIDDEN_ROOTS:
        return False
    if any(module == m or module.startswith(m + ".") for m in APPROVED_ORCHESTRATION):
        return False
    return True


def _violation(path: str, lineno: int, code: str, stripped: str) -> dict:
    return {
        "file": path,
        "line": lineno,
        "code": code,
        "description": f"Direct import from SIM internals: {stripped}",
        "why": (
            "Company code must only access sim/ through "
            "company/interfaces/sim_interface.py. "
            "Could a real UK energy supplier know this without reading "
            "simulation internals? No — this bypasses the epistemic boundary."
        ),
    }


def _check_unavailable(path: str, reason: str) -> dict:
    """A file the scanner was ASKED to verify but could not read is an
    UNAVAILABLE check, not a clean one (R15 FAIL-SILENT killer pattern): an
    unavailable control is a FAILED control. Surfaces as a non-empty finding so
    the overall scan cannot silently PASS on a file it never actually inspected.
    Genuine deletions are filtered upstream (_get_diff_files --diff-filter=d) so
    this only fires on a path that was expected to exist.
    """
    return {
        "file": path,
        "line": 0,
        "code": "",
        "kind": "check_unavailable",
        "description": f"Epistemic scan UNAVAILABLE for {path}: {reason}",
        "why": (
            "The verifier was asked to check this file and could not read it. An "
            "unavailable check is a FAILED check (R15 FAIL-SILENT): it must ALARM, "
            "never read as a clean pass."
        ),
    }


def _scan_source(source: str, path: str) -> list[dict] | None:
    """AST scan for forbidden SIM imports. Returns a (possibly empty) list of
    violations, or None if the source could not be parsed (caller falls back to
    the line-regex scan -- an unparseable file must not silently read clean)."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(source)
    except SyntaxError:
        return None
    violations: list[dict] = []
    lines = source.splitlines()
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            # level>0 is a relative import (e.g. `from . import x`) -- never SIM.
            modules = [node.module] if node.level == 0 else []
        else:
            continue
        for module in modules:
            if _module_is_forbidden(module):
                lineno = getattr(node, "lineno", 1)
                code = lines[lineno - 1].rstrip() if 0 < lineno <= len(lines) else module
                violations.append(_violation(path, lineno, code, code.strip() or module))
                break  # one finding per import statement is enough
    return violations


def _scan_lines(content: str, path: str) -> list[dict]:
    """Legacy line-anchored regex scan -- the SyntaxError fallback for a file
    the AST cannot parse. Kept so an unparseable file is still inspected rather
    than skipped."""
    violations = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        for pattern in FORBIDDEN_SOURCES:
            if re.match(pattern, stripped):
                if APPROVED_SEAM in stripped:
                    break
                if any(m in stripped for m in APPROVED_ORCHESTRATION):
                    break
                violations.append(_violation(path, lineno, line.rstrip(), stripped))
                break
    return violations


def _scan_file(path: str) -> list[dict]:
    """Return list of findings for a single file.

    A forbidden SIM import -> a violation finding. A file that was requested but
    cannot be read -> a check_unavailable finding (NOT an empty/clean result):
    an unavailable check is a failed check (R15). The AST scan is primary (it
    catches whitespace/alias/bare-import forms the line regex fails open on);
    the line regex is the fallback only when the source will not parse.
    """
    try:
        content = Path(path).read_text()
    except (FileNotFoundError, PermissionError, IsADirectoryError, UnicodeDecodeError) as exc:
        return [_check_unavailable(path, type(exc).__name__)]

    ast_result = _scan_source(content, path)
    if ast_result is None:
        return _scan_lines(content, path)
    return ast_result


def scan(files: list[str] | None = None) -> tuple[bool, list[dict]]:
    """Run scan. Returns (passed, violations_list).

    If files is None, scans all company/ .py files.
    If files provided, scans only those that are company/ files.
    """
    if files is None:
        # Scan all company/ and saas/ files
        to_scan = [
            str(p) for p in Path("company").rglob("*.py")
            if not _is_exempt(str(p))
        ] + [
            str(p) for p in Path("saas").rglob("*.py")
            if not _is_exempt(str(p))
        ]
    else:
        to_scan = [f for f in files if _is_company_file(f) and not _is_exempt(f)]

    all_violations = []
    for path in sorted(to_scan):
        all_violations.extend(_scan_file(path))

    return (len(all_violations) == 0), all_violations


def _format_report(passed: bool, violations: list[dict], files_checked: int) -> str:
    if passed:
        return (
            f"PASS\n"
            f"Summary: Scanned {files_checked} company/ + saas/ file(s). No epistemic barrier violations found.\n"
            f"Files checked: {files_checked}"
        )

    lines = [f"FAIL", f"Violations found: {len(violations)}", ""]
    for i, v in enumerate(violations, start=1):
        lines.append(f"Violation {i}:")
        lines.append(f"  File: {v['file']}")
        lines.append(f"  Line: {v['line']}")
        lines.append(f"  Code: {v['code']}")
        lines.append(f"  Description: {v['description']}")
        lines.append(f"  Why it violates: {v['why']}")
        lines.append("")
    lines.append(f"Recommendation: Replace direct SIM imports with calls through "
                 f"company/interfaces/sim_interface.py")
    return "\n".join(lines)


def main() -> int:
    args = sys.argv[1:]

    if "--diff" in args or not args:
        # Scan files changed since HEAD
        changed = _get_diff_files()
        files_to_scan = [f for f in changed if _is_company_file(f) and not _is_exempt(f)]
        if not files_to_scan:
            # No company files changed — scan all company/ for safety
            passed, violations = scan(files=None)
            all_company = list(Path("company").rglob("*.py")) + list(Path("saas").rglob("*.py")) + list(Path("saas").rglob("*.py"))
            print(_format_report(passed, violations, len(all_company)))
        else:
            passed, violations = scan(files=files_to_scan)
            print(_format_report(passed, violations, len(files_to_scan)))
    elif "--files" in args:
        idx = args.index("--files")
        file_list = args[idx + 1:]
        passed, violations = scan(files=file_list)
        print(_format_report(passed, violations, len(file_list)))
    else:
        passed, violations = scan(files=None)
        all_company = list(Path("company").rglob("*.py")) + list(Path("saas").rglob("*.py"))
        print(_format_report(passed, violations, len(all_company)))

    # Update observability
    try:
        from background.agent_status import update_agent_status
        anomaly = f"FAIL: {len(violations)} violation(s)" if not passed else None
        update_agent_status(
            "epistemic-verifier",
            status="idle",
            last_action=f"Scan complete — {'PASS' if passed else 'FAIL'} ({len(violations)} violations)",
            role="Scans phase-close diffs for SIM/company epistemic barrier violations",
            produces="PASS/FAIL report to stdout",
            anomaly=anomaly,
        )
    except Exception:
        pass

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
