"""Epistemic Verifier — scans code changes for SIM/company barrier violations.

Run at phase close: python3 -m tools.epistemic_verifier [--diff | --files file1 file2...]

Checks company/ code for direct reads of SIM internals that bypass the
company/interfaces/sim_interface.py seam. Both literal (`import simulation.x`)
and dynamic (`importlib.import_module("simulation.x")`, `__import__("sim.x")`)
import forms are in scope with a literal string-constant target -- a bypass
via a string-literal dynamic import is the same violation (a forbidden module
name reaching company/saas/), just spelled differently
(W4_2_verifier_timing_extension KL-2b: the AST-based static-import scan added
under H12/KL-2 caught non-canonical *literal* import syntax but not these
dynamic-invocation forms). A non-literal target (a variable, an f-string, a
runtime-built string) cannot be resolved statically and is a documented
heuristic limit, not a false-clear -- see `_dynamic_import_target`.

Scope note (deliberately NOT covered here, per the Tier-1 gate closed
2026-07-10 — docs/review_gates/done/EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md,
a director-ratified decision, not an open question): this tool stays
*import-direction* detection -- does a forbidden module name reach
company/saas/ code, literally or dynamically. It is NOT data-flow/timing-
violation detection (e.g. a function receiving an unbounded historical
dataset with no as-of cut -- the hedge-volatility bug class). That dimension
was explicitly decided NOT to be built into this tool; the practical
detection burden for it is carried by two separate mechanisms instead
(.claude/hooks/block_point_in_time_read.py near-term, the point-in-time
snapshot/as-of interface object permanently, per that gate's own
resolution). Re-opening automated timing/data-flow detection in *this* file
requires the same Tier-1 authentication convention as any other
safety-control change (Rich live in-console, or Rich clearing the gate
file) -- not a build delegation alone.

Exit code 0 = PASS, exit code 1 = FAIL (violations found).
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import warnings
from pathlib import Path

from tools.epistemic_wall import (
    COMPANY_PACKAGES,
    SEAM_PATH_PREFIX,
    SIM_PACKAGES,
    is_sim_module,
)

# ---------------------------------------------------------------------------
# THE PERIMETER IS NOT DEFINED HERE (2026-08-09, KNIFE pass 3 first step).
#
# This scanner used to carry its own forbidden-root tuple, its own seam
# constant and its own exemption registers, alongside the ratchet's and the
# KNIFE ledger's. Three registers of one concept, and they had drifted twice:
#
#   * `APPROVED_ORCHESTRATION` exempted `simulation.run_phase4c_on_phase2b` and
#     `simulation.run_segments` in company-side code -- EXACTLY the two class-(a)
#     edges KNIFE pass 1 deleted. A dead exemption is not inert: it is a
#     pre-authorised re-entry, and it would have waved those imports back in
#     with the reasoning ("structural orchestration, not epistemic") that the
#     pass had just proved false -- both were CLI COMPOSITION, and composition
#     belongs above both layers (tools/run_annual_report.py). DELETED.
#   * `APPROVED_SEAM` was a single FILE ("company/interfaces/sim_interface")
#     while the wall's seam is the PACKAGE (`company.interfaces`). It was
#     consulted as a SUBSTRING of a forbidden import LINE, which no real seam
#     import can ever be (a `from company.interfaces...` line does not match
#     FORBIDDEN_SOURCES at all) -- so it could only ever fire on a SIM import
#     carrying the seam path in a trailing comment. That is not a seam
#     exemption; it is a comment-shaped escape hatch. DELETED. The genuine
#     source-side seam exemption is `EXEMPT_PATHS`, below, and it is now
#     DERIVED from the shared `SEAM_PACKAGE` so it cannot drift again.
#
# Definition: tools/epistemic_wall.py. Gate: the ratchet's frozen
# allowlists. This tool reports at phase close, over a wider (dynamic-import)
# reach than the static ratchet, against the SAME perimeter.
# ---------------------------------------------------------------------------

# Importing directly from these is a violation if found in company/ files.
# Derived from the shared SIM_PACKAGES so a perimeter change reaches this
# scanner without anyone remembering to edit it.
FORBIDDEN_SOURCES = [
    pattern
    for pkg in sorted(SIM_PACKAGES)
    for pattern in (rf"^from {pkg}\.", rf"^from {pkg} import", rf"^import {pkg}\.")
]

# Files and directories that are allowed to cross the seam freely
EXEMPT_PATHS = {
    "tests/",             # tests may import anything
    "background/",        # orchestrator layer
    *(f"{pkg}/" for pkg in sorted(SIM_PACKAGES)),  # the simulation is the simulation
    SEAM_PATH_PREFIX,     # the approved seam itself (the PACKAGE, per the shared definition)
    "tools/",             # dev tools
}

# Company-layer paths that must be checked
COMPANY_PATHS = [f"{pkg}/" for pkg in sorted(COMPANY_PACKAGES)]


# ---------------------------------------------------------------------------
# SEAM-FILE SEGMENT-LABEL GUARD (SEGMENTATION_GENERATOR_BUILD_PLAN.md step 5;
# SEGMENTATION_RECONCILIATION_FRAME.md §0 canonical wall ruling, verbatim: "No
# segment label, attitude, or sensitivity ever crosses the wall directly").
#
# The generic import-direction scan above only catches `simulation.*`/`sim.*`
# IMPORTS -- but `company/interfaces/` is the one path EXEMPT from that scan
# (it IS the approved seam, legitimately allowed to import simulation
# internals to implement `Live*SimInterface`). That means the seam file needs
# a DIFFERENT check: not "does it import simulation" (yes, correctly), but
# "does it ever DEFINE/RETURN a SIM segment label, attitude, or sensitivity".
# This is a closed, curated symbol list -- deliberately not a generic import
# scan, because the seam file's whole job is to touch simulation internals;
# the violation class here is a specific RETURNED symbol, not any import.
# ---------------------------------------------------------------------------
SEAM_FILES = ["company/interfaces/sim_interface.py"]

FORBIDDEN_SEAM_SYMBOLS = {
    # Attitudinal / behavioural cohort truths.
    "green_stance", "price_sensitivity", "channel_pref",
    "cohort_label", "true_cohort", "segment_label",
    "assign_cohort", "Cohort", "nudge_susceptibility", "co2_salience",
    # Demographic segment labels (Cohort dataclass fields). These are SIM-truth
    # census/dwelling latents the company must DISCOVER from EPC/census priors,
    # never read across the seam -- equally "segment labels" under the §0 bright
    # line as the attitudes above. Omitting them was a SUBSET-COVERAGE fail-open:
    # a leaked SIM-true `nssec`/`accommodation`/`cars`/`heating_fuel` passed the
    # scan clean (CA1_cohort_assignment_live red-team, 2026-07-29).
    "nssec", "accommodation", "cars", "heating_fuel",
    # `tenure` and `region` are DELIBERATELY NOT here: `region` is an OBSERVABLE
    # (it is carried in the saas customer dict); `tenure` collides with the
    # legitimate contract `tenure_years` the churn seam legitimately exposes
    # (the two-tenures reconciliation, population_draw.py line ~418). The runtime
    # wall test asserts neither housing-tenure nor region-as-cohort-truth leaks
    # the OBSERVABLE dict; the static scan cannot disambiguate the tenure
    # homonym without false-flagging contract tenure, so it excludes it by name.
    # The class-closure meta-test (test_control_mutation.py) keeps this set in
    # lockstep with the Cohort field set so a NEW field cannot slip in unguarded.
}


def _seam_symbol_violation(path: str, lineno: int, code: str, symbol: str) -> dict:
    return {
        "file": path,
        "line": lineno,
        "code": code,
        "description": f"Seam file exposes a forbidden SIM cohort symbol: {symbol!r}",
        "why": (
            "company/interfaces/sim_interface.py is the ONE approved SIM<->company "
            "seam -- but the CANONICAL WALL RULING (docs/design/SEGMENTATION_"
            "RECONCILIATION_FRAME.md §0) is a bright line even here: no segment "
            "label, attitude, or sensitivity may ever cross it, only interaction "
            f"events. A forbidden symbol ({symbol!r}) appearing in this file is a "
            "wall breach even though the file is otherwise allowed to import "
            "simulation internals to implement its Live* interfaces."
        ),
    }


def _scan_seam_files_for_forbidden_symbols(paths: list[str] | None = None) -> list[dict]:
    """Scan the approved seam file(s) for any `FORBIDDEN_SEAM_SYMBOLS` token,
    as an identifier (a function/attribute/import name), a parameter or
    keyword-argument NAME (`def emit(nssec):` / `make_dict(nssec=hh.raw)`), or
    a string literal (a dict/JSON key) -- each is a real way a segment label
    could cross the seam. The node-type coverage here is itself a control
    surface: omitting `ast.arg`/`ast.keyword` was a SUBSET-COVERAGE fail-open
    one level up from the symbol set (a label crossing purely as a kwarg name
    passed clean; CA1 red-team round 2, 2026-07-29). A missing seam file has
    nothing to violate (not an unavailable
    check -- `company/interfaces/sim_interface.py` not existing yet is not
    this scan's failure mode). An unreadable EXISTING file IS an unavailable
    check (R15 FAIL-SILENT)."""
    targets = paths if paths is not None else SEAM_FILES
    violations: list[dict] = []
    for path in targets:
        p = Path(path)
        if not p.is_file():
            continue
        try:
            source = p.read_text()
        except (OSError, UnicodeDecodeError) as exc:
            violations.append(_check_unavailable(path, type(exc).__name__))
            continue
        lines = source.splitlines()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(source)
        except SyntaxError:
            tree = None

        found: set[tuple[str, int]] = set()
        if tree is not None:
            for node in ast.walk(tree):
                name = None
                lineno = getattr(node, "lineno", 1)
                if isinstance(node, ast.Name):
                    name = node.id
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    name = node.name
                elif isinstance(node, ast.Attribute):
                    name = node.attr
                elif isinstance(node, ast.alias):
                    name = node.name
                elif isinstance(node, ast.arg):
                    # A parameter named for a segment label (`def emit(nssec):`)
                    # is a leak-shaped signature -- the seam is built to take that
                    # field by name.
                    name = node.arg
                elif isinstance(node, ast.keyword):
                    # A keyword-argument NAME (`make_dict(nssec=hh.raw)`) pushes a
                    # segment label across even when the VALUE is an innocent
                    # expression the Attribute/Name branches never see. `.arg` is
                    # None for `**kwargs` splat -- guarded by the set membership.
                    name = node.arg
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    name = node.value
                if name in FORBIDDEN_SEAM_SYMBOLS:
                    found.add((name, lineno))
        else:
            # Unparseable source: fall back to a line-anchored substring scan
            # rather than skipping the file (same discipline as _scan_lines).
            for lineno, line in enumerate(lines, start=1):
                for sym in FORBIDDEN_SEAM_SYMBOLS:
                    if sym in line:
                        found.add((sym, lineno))

        for name, lineno in sorted(found, key=lambda t: t[1]):
            code = lines[lineno - 1].strip() if 0 < lineno <= len(lines) else name
            violations.append(_seam_symbol_violation(path, lineno, code, name))
    return violations


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


def _module_is_forbidden(module: str | None) -> bool:
    """True iff a dotted module name is a forbidden SIM import.

    Matches the package itself (``sim`` / ``simulation``) and any submodule
    (``simulation.weather_engine``), independent of source-text whitespace,
    aliasing, or indentation -- the FAIL-OPEN gaps a line-anchored regex misses
    (``from  simulation.x import y`` with stray spaces, ``import simulation``
    with no dotted tail, ``import os; import simulation.x`` on one physical
    line).

    There is NO per-module exemption. The old `APPROVED_ORCHESTRATION` list is
    deleted (see the header): a SIM module is forbidden in company-side code
    whatever it is called, and the one legitimate exemption -- the seam -- is a
    property of the IMPORTING file, applied in `_is_exempt`, exactly as the
    ratchet applies it to the company-side endpoint of an edge.
    """
    return is_sim_module(module) if module else False


def _violation(path: str, lineno: int, code: str, stripped: str, dynamic: bool = False) -> dict:
    kind = "Dynamic import of SIM internals" if dynamic else "Direct import from SIM internals"
    return {
        "file": path,
        "line": lineno,
        "code": code,
        "description": f"{kind}: {stripped}",
        "why": (
            "Company code must only access sim/ through "
            "company/interfaces/sim_interface.py. "
            "Could a real UK energy supplier know this without reading "
            "simulation internals? No — this bypasses the epistemic boundary."
            + (" (via importlib.import_module()/__import__() rather than a"
               " literal import statement — same bypass, different syntax.)"
               if dynamic else "")
        ),
    }


# Dynamic-import call shapes that can smuggle a forbidden module name past a
# scan that only looks at `ast.Import`/`ast.ImportFrom` nodes: the standard
# `importlib.import_module(...)` (both the fully-qualified attribute form and
# the bare `from importlib import import_module` name form) and the builtin
# `__import__(...)`. Only a LITERAL string-constant first argument is
# resolvable statically -- a variable/f-string/concatenation is a documented
# heuristic limit (KL-2b scope), not a silent false-clear: it simply cannot be
# resolved without real data-flow analysis, which this tool deliberately does
# not attempt (see module docstring's Tier-1 scope note).
def _collect_importlib_aliases(tree: "ast.AST") -> "tuple[set[str], set[str]]":
    """Resolve the local names bound to ``importlib`` and to
    ``importlib.import_module`` in one module (see the identical helper in
    ``tools/internal_seam_verifier.py``).

    WHY (R15 fail-open fix, sibling of the internal-seam fix): the AST dynamic
    detector below matched only the LITERAL spellings ``importlib.import_module``
    / ``import_module``. A one-line alias -- ``import importlib as il;
    il.import_module("simulation.x")`` or ``from importlib import import_module
    as imp; imp("simulation.x")`` -- renamed the call and it was no longer
    recognised as a dynamic import, so a forbidden SIM crossing went INVISIBLE on
    any file that PARSES (the regex belt only runs on the SyntaxError fallback).
    That re-opens the exact "evade via the dynamic form" hole KL-2b closed, by a
    trivial rename -- worse than no check. Resolving the aliases restores it."""
    importlib_names: set[str] = {"importlib"}
    import_module_names: set[str] = {"import_module"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "importlib":
                    importlib_names.add(alias.asname or "importlib")
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module == "importlib":
                for alias in node.names:
                    if alias.name == "import_module":
                        import_module_names.add(alias.asname or "import_module")
    return importlib_names, import_module_names


def _dynamic_import_target(
    node: "ast.Call",
    importlib_names: "set[str] | None" = None,
    import_module_names: "set[str] | None" = None,
) -> str | None:
    """Return the literal module name targeted by a dynamic-import call, or
    None if this call is not a dynamic import or its target is not a literal
    string constant.

    ``importlib_names`` / ``import_module_names`` are the per-module alias sets
    from ``_collect_importlib_aliases``; without them they default to the literal
    names, preserving the original recognise-the-standard-spelling behaviour."""
    if importlib_names is None:
        importlib_names = {"importlib"}
    if import_module_names is None:
        import_module_names = {"import_module"}
    func = node.func
    is_import_module = (
        isinstance(func, ast.Attribute)
        and func.attr == "import_module"
        and isinstance(func.value, ast.Name)
        and func.value.id in importlib_names
    ) or (isinstance(func, ast.Name) and func.id in import_module_names)
    is_dunder_import = isinstance(func, ast.Name) and func.id == "__import__"
    if not (is_import_module or is_dunder_import):
        return None
    if not node.args:
        return None
    first = node.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return None


# Regex fallback for the SyntaxError path (an unparseable file must still be
# inspected, not skipped -- matching the existing literal-import fallback).
# Deliberately narrow (literal quoted string immediately following the call),
# same heuristic-scope tradeoff as the AST version above.
_DYNAMIC_IMPORT_CALL_RE = re.compile(
    r"(?:importlib\.import_module|(?<!\w)import_module|__import__)\s*\(\s*['\"]([^'\"]+)['\"]"
)


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
    importlib_names, import_module_names = _collect_importlib_aliases(tree)
    for node in ast.walk(tree):
        modules: list[str] = []
        dynamic = False
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            # level>0 is a relative import (e.g. `from . import x`) -- never SIM.
            modules = [node.module] if node.level == 0 else []
        elif isinstance(node, ast.Call):
            target = _dynamic_import_target(
                node, importlib_names, import_module_names
            )
            modules = [target] if target else []
            dynamic = True
        else:
            continue
        for module in modules:
            if _module_is_forbidden(module):
                lineno = getattr(node, "lineno", 1)
                code = lines[lineno - 1].rstrip() if 0 < lineno <= len(lines) else module
                violations.append(_violation(path, lineno, code, code.strip() or module, dynamic=dynamic))
                break  # one finding per import statement/call is enough
    return violations


def _scan_lines(content: str, path: str) -> list[dict]:
    """Legacy line-anchored regex scan -- the SyntaxError fallback for a file
    the AST cannot parse. Kept so an unparseable file is still inspected rather
    than skipped.

    No line-TEXT exemptions (2026-08-09, KNIFE pass 3). Both that this loop
    carried were escape hatches rather than seams: a forbidden `from sim...`
    line was waved through if it merely CONTAINED the string
    "company/interfaces/sim_interface" or an approved-orchestration module
    name -- i.e. a trailing comment could clear a real crossing. The seam
    exemption belongs to the importing FILE (`_is_exempt`), which is where the
    ratchet puts it too."""
    violations = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        for pattern in FORBIDDEN_SOURCES:
            if re.match(pattern, stripped):
                violations.append(_violation(path, lineno, line.rstrip(), stripped))
                break
        for match in _DYNAMIC_IMPORT_CALL_RE.finditer(line):
            target = match.group(1)
            if _module_is_forbidden(target):
                violations.append(_violation(path, lineno, line.rstrip(), stripped, dynamic=True))
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

    # Seam-file segment-label guard (always runs, independent of `files`/
    # `--diff` scope -- a wall-critical check for the ONE file the generic
    # scan above deliberately exempts, see the guard's own module-level note).
    all_violations.extend(_scan_seam_files_for_forbidden_symbols())

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
