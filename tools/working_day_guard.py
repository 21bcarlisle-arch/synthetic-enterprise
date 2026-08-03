"""Working-Day Guard -- fails the build on a SECOND definition of working-day
arithmetic outside the canonical primitive.

`company/compliance/working_days.py` is the one definition (R10 class fix: 22
modules each rolled their own Mon-Fri-only, bank-holiday-blind arithmetic, so every
regulatory deadline the company computed ran early across a bank holiday). Landing
that primitive fixes the instances; only this guard closes the CLASS -- without it
the 23rd copy gets written next month and the defect returns.

Run:
    python3 -m tools.working_day_guard [--all | --files f1 f2 ...]

Exit code 0 = PASS, 1 = FAIL (second definitions found outside the baseline).

Design stance (R15 -- this control must be able to FAIL):
  * NOT NAME-ONLY, so it is not FAIL-OPEN on a rename. Rule 1 matches the helper
    NAMES found in the census; rule 2 independently matches the STRUCTURAL SHAPE
    of the arithmetic -- a function containing both a `timedelta(days=1)` step and
    a `.weekday()` comparison inside a loop. Three of the census modules
    (`bsc_credit_register`, `erroneous_transfer`, `gsop_tracker`) had NO named
    helper at all and are caught only by rule 2; a name-only guard would have
    passed them, which is exactly the fail-open pattern to avoid. A reimplementation
    under a fresh name still trips rule 2.
  * NOT A TAUTOLOGY: the patterns derive from the independent grep/AST census in
    `docs/design/WORKING_DAY_CALCULATOR_DISCOVER.md` s1 over the live tree, NOT
    from the canonical module's own exports. The guard would still fire if
    `working_days.py` were deleted.
  * NOT FAIL-SILENT: an unreadable or unparseable file RAISES; it does not pass
    quietly. A file the guard cannot read is a file it has not checked.
  * NOT FAIL-OPEN ON AN EMPTY SCAN: a scan that matched zero files is a FAILURE,
    not a pass -- a broken path root would otherwise report a confident PASS having
    checked nothing.

BASELINE. The 22 pre-existing definitions are listed in `BASELINE_ALLOWLIST` and
are NOT violations yet: Pass 1 lands the primitive and this guard with call sites
UNCHANGED, Pass 2 migrates the callers. The allowlist is designed to SHRINK -- each
migration deletes its entry, and `test_baseline_allowlist_is_accurate` fails if an
entry names a definition that no longer exists, so it cannot rot into permanent
cover for code that has already gone.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

SCAN_ROOTS = ("company", "sim", "simulation", "saas")

# The canonical primitive itself, and its own tests, are the one place this
# arithmetic is allowed to exist.
CANONICAL_MODULE = "company/compliance/working_days.py"

# Helper names from the census (s1), PLUS the canonical exported names -- so
# copy-pasting the canonical implementation under its own name into another module
# is caught too, not just a renamed private copy.
FLAGGED_NAMES = frozenset(
    {
        "_add_working_days",
        "_working_days_between",
        "add_working_days",
        "working_days_between",
        "working_days_open",
        "working_days_to_pay",
        "is_working_day",
    }
)

# The 25 pre-existing definitions present when this guard landed (2026-08-03), derived
# MECHANICALLY from the live tree, not transcribed from the design doc. Pass 2 deletes
# these one by one.
#
# THE CENSUS WAS WRONG AND THIS GUARD CAUGHT IT. `WORKING_DAY_CALCULATOR_DISCOVER.md` s1
# reports 22, found by grepping for the four known helper names. The structural rule
# found 3 more the name grep could not see:
#   * `transfer_objection_register.py::_add_wd` and
#     `annual_compliance_attestation_register.py::_add_wd` -- the SAME arithmetic under a
#     shortened name. A name-only guard passes both. This is the rename fail-open, found
#     in the live tree rather than hypothesised.
#   * `bsc_credit_register.py::is_cdn_overdue` -- the inline-loop case the doc predicted
#     existed but mis-attributed to a helper that does not exist.
# Recorded here because it is the evidence that rule 2 earns its place.
BASELINE_ALLOWLIST = frozenset(
    {
        "company/billing/credit_refund.py::_working_days_between",
        "company/billing/credit_refund.py::working_days_to_pay",
        "company/billing/dd_indemnity.py::_working_days_between",
        "company/billing/deemed_contract.py::_working_days_between",
        "company/billing/energy_theft_book.py::_working_days_between",
        "company/crm/change_of_tenancy_register.py::_add_working_days",
        "company/crm/onboarding_journey.py::_add_working_days",
        "company/crm/service_log.py::_add_working_days",
        "company/crm/service_ticket.py::_add_working_days",
        "company/market/bsc_performance_assurance_register.py::_add_working_days",
        "company/market/bsc_settlement_dispute_register.py::_add_working_days",
        "company/market/css_performance_register.py::_add_working_days",
        "company/market/dcc_meter_registration.py::_add_working_days",
        "company/market/erroneous_transfer.py::working_days_open",
        "company/market/meter_technical_investigation_register.py::_add_working_days",
        "company/market/mop_appointment_register.py::_add_working_days",
        "company/market/mpas_standing_data_correction_register.py::_add_working_days",
        "company/market/transfer_objection_register.py::_add_wd",
        "company/regulatory/annual_compliance_attestation_register.py::_add_wd",
        "company/regulatory/gsop.py::_add_working_days",
        "company/regulatory/gsop_tracker.py::working_days_open",
        "company/trading/bsc_credit_register.py::is_cdn_overdue",
        "company/trading/emir_reporting_register.py::_add_working_days",
        "simulation/bacs_rails.py::_add_working_days",
        "simulation/credit_refund_events.py::_add_working_days",
    }
)


class GuardError(RuntimeError):
    """Raised when the guard cannot do its job -- never swallowed into a PASS."""


def _has_weekend_skip_shape(node: ast.AST) -> bool:
    """True if this function body contains the structural shape of weekend-skipping
    date arithmetic: a loop containing BOTH a `timedelta(days=1)`-style step AND a
    `.weekday()` comparison. This is the rename-proof half of the guard."""
    for loop in ast.walk(node):
        if not isinstance(loop, (ast.While, ast.For)):
            continue
        has_step = False
        has_weekday = False
        for inner in ast.walk(loop):
            if isinstance(inner, ast.Call):
                func = inner.func
                name = getattr(func, "attr", None) or getattr(func, "id", None)
                if name == "timedelta":
                    has_step = True
                if name == "weekday":
                    has_weekday = True
            if isinstance(inner, ast.Attribute) and inner.attr == "weekday":
                has_weekday = True
        if has_step and has_weekday:
            return True
    return False


def _iter_python_files(roots=SCAN_ROOTS):
    for root in roots:
        base = PROJECT_DIR / root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            yield path


def verify(paths) -> list[str]:
    """Return a list of violation strings. Raises GuardError on an unreadable or
    unparseable file, or on a scan that matched nothing at all."""
    paths = list(paths)
    if not paths:
        raise GuardError(
            "working_day_guard scanned ZERO files -- a scan that checked nothing is a "
            "FAILED check, not a pass. Verify SCAN_ROOTS against the tree."
        )

    violations: list[str] = []
    for path in paths:
        rel = path.relative_to(PROJECT_DIR).as_posix() if path.is_absolute() else Path(path).as_posix()
        if rel == CANONICAL_MODULE:
            continue
        try:
            tree = ast.parse(Path(PROJECT_DIR / rel).read_text())
        except (OSError, SyntaxError) as exc:
            raise GuardError(f"cannot read/parse {rel}: {exc}") from exc

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            by_name = node.name in FLAGGED_NAMES
            by_shape = _has_weekend_skip_shape(node)
            if not (by_name or by_shape):
                continue
            key = f"{rel}::{node.name}"
            if key in BASELINE_ALLOWLIST:
                continue
            why = "name" if by_name else "weekend-skip loop shape"
            violations.append(
                f"{rel}:{node.lineno}: second definition of working-day arithmetic "
                f"in `{node.name}` (matched by {why}). Import from "
                f"`company.compliance.working_days` instead."
            )
    return violations


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="scan all source roots")
    group.add_argument("--files", nargs="+", help="scan specific files")
    args = parser.parse_args(argv)

    paths = [Path(f) for f in args.files] if args.files else list(_iter_python_files())

    try:
        violations = verify(paths)
    except GuardError as exc:
        print(f"WORKING DAY GUARD: ERROR -- {exc}")
        return 1

    if violations:
        print(f"WORKING DAY GUARD: FAIL -- {len(violations)} second definition(s):")
        for v in violations:
            print(f"  {v}")
        return 1
    print(
        f"WORKING DAY GUARD: PASS ({len(paths)} file(s) scanned, "
        f"{len(BASELINE_ALLOWLIST)} baseline definition(s) pending Pass-2 migration)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
