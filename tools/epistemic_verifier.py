"""Epistemic Verifier — scans code changes for SIM/company barrier violations.

Run at phase close: python3 -m tools.epistemic_verifier [--diff | --files file1 file2...]

Checks company/ code for direct reads of SIM internals that bypass the
company/interfaces/sim_interface.py seam.

Exit code 0 = PASS, exit code 1 = FAIL (violations found).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Imports from these modules are allowed in company/ code (the approved seam)
APPROVED_SEAM = "company/interfaces/sim_interface"

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
COMPANY_PATHS = ["company/"]


def _get_diff_files() -> list[str]:
    """Get changed company/ files from current git diff (HEAD vs working tree + index)."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True,
    )
    files = result.stdout.strip().splitlines()
    # Also check staged changes
    result2 = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
        capture_output=True, text=True,
    )
    files += result2.stdout.strip().splitlines()
    return sorted(set(files))


def _is_exempt(path: str) -> bool:
    return any(path.startswith(e) for e in EXEMPT_PATHS)


def _is_company_file(path: str) -> bool:
    return path.startswith("company/") and path.endswith(".py")


def _scan_file(path: str) -> list[dict]:
    """Return list of violations found in a single file."""
    violations = []
    try:
        content = Path(path).read_text()
    except FileNotFoundError:
        return []

    lines = content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        # Check for forbidden direct imports
        for pattern in FORBIDDEN_SOURCES:
            if re.match(pattern, stripped):
                # Exception: importing through the approved seam
                if APPROVED_SEAM in stripped:
                    break
                violations.append({
                    "file": path,
                    "line": lineno,
                    "code": line.rstrip(),
                    "description": f"Direct import from SIM internals: {stripped}",
                    "why": (
                        "Company code must only access sim/ through "
                        "company/interfaces/sim_interface.py. "
                        "Could a real UK energy supplier know this without reading "
                        "simulation internals? No — this bypasses the epistemic boundary."
                    ),
                })
                break

    return violations


def scan(files: list[str] | None = None) -> tuple[bool, list[dict]]:
    """Run scan. Returns (passed, violations_list).

    If files is None, scans all company/ .py files.
    If files provided, scans only those that are company/ files.
    """
    if files is None:
        # Scan all company/ files
        to_scan = [
            str(p) for p in Path("company").rglob("*.py")
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
            f"Summary: Scanned {files_checked} company/ file(s). No epistemic barrier violations found.\n"
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
            all_company = list(Path("company").rglob("*.py"))
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
        all_company = list(Path("company").rglob("*.py"))
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
