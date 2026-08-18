"""R10 class closure: a STRUCTURAL BLANK may never be folded into an aggregate as a value.

WHY THIS EXISTS (2026-08-18, discharging
`docs/staging/WORKER_FINDING_A_NULL_CLV_ENTERS_THE_PUBLISHED_MEDIAN_AS_THE_NUMBER_ZERO_2026-08-17.md`,
BLOCKING, lane `D_billing_metering`).

Four forward-looking figures in this repo are DELIBERATELY published as `null` rather than as 0.
`tools.generate_customer_data._round_or_none` exists for nothing else, and its own docstring says
why: "`round(x or 0, n)` and `round(d.get(k, 0), n)` both turn 'no value was computed' into the
number 0, and 0 is a value a reader takes as the company's belief." An account that has left has
no lifetime value; publishing £0 for it states a belief the company does not hold.

Consumers then turned the null straight back into 0. Measured, not inferred:

* `saas/reporting/annual_report.py::_section_customer_strategic_value` — seven sites. 5 of 13
  electricity accounts carried a null CLV, so five manufactured zeros sat at the bottom of the
  sorted list and moved the MEDIAN, which is that section's quadrant BOUNDARY. Two accounts
  cleared "High CLV" only because of it (one by being exactly equal to it) and were published to
  the board under "priority intervention" inside a recommendation for immediate retention offers.
  Repairing it moved the published board line from 5 CRITICAL accounts to 1.
* `tools/generate_shadow_html.py` — one site, `s.get("clv_gbp", 0)`, LATENT. The line DIRECTLY
  BELOW it already carried `latest_churn_probability` through as None and rendered `—`. Same
  author, same record, adjacent lines, one right and one wrong.

That adjacency is the whole argument for a guard rather than a pair of fixes. The shape is one
character of inattention, it is invisible at review because it never raises, and R10 forbids
closing an absurdity class with an instance fix.

THE TWO SPELLINGS DO NOT FIRE ON THE SAME CONDITION, and conflating them overstates a finding.
`d.get(k) or 0` substitutes on a null VALUE — live the moment any record carries one, which is
what made the annual report wrong. `d.get(k, 0)` substitutes only on a MISSING KEY; a key present
with `None` comes back as `None`. So the shadow-HTML site was reachable (`s` is
`sample_custs.get(cid, {})`, and `{}` has no key at all) but had an empty triggering population
when it was fixed: 19 of 19 lifetime accounts were present in the sample, and all 11 nulls
already rendered `—`. That repair moved no published pixel and is not claimed to have. Both
spellings are the class; only one of them had shipped a wrong figure.

WHAT IS A VIOLATION: a nullable-published field read out of a record and given a numeric
fallback in the same expression. Three arms, because the same defect has three spellings:

* ARM 1 -- OR-DEFAULT.      `v.get("clv_gbp") or 0.0`      (all seven annual-report sites)
* ARM 2 -- GET-DEFAULT.     `s.get("clv_gbp", 0)`          (the shadow-HTML site)
* ARM 3 -- SUBSCRIPT-OR.    `v["clv_gbp"] or 0`            (not yet seen; the same defect, and
                            cheap to cover, so covering it is not speculation about the future
                            but closure of the class as stated)

What is NOT a violation, stated so the silence is not read as coverage: `v.get("clv_gbp")` with
no fallback (correct — the null survives), an explicit `is None` branch (correct — the blank is
handled), and a non-numeric fallback such as `or "—"` (correct — that IS the render of a blank).
Arithmetic on a value that reached a local by some other route is out of scope; this guard is a
SHAPE check at the read site, which is where every instance so far has lived.

THE FIELD REGISTRY IS DERIVED, NOT DECLARED TWICE. `NULLABLE_FIELDS` below would rot the moment
a fifth nullable figure is added, and a rotted registry passes silently — the fail-open shape.
So `tests/tools/test_structural_blank_guard.py::test_the_registry_matches_the_producer` re-derives
the set from the AST of `tools/generate_customer_data.py` — every key handed to `_round_or_none`
and every keyword it is bound to — and fails if the two disagree. The registry is checked against
the code that creates the nulls, not against itself.

FAIL-CLOSED ON ITS OWN SUBJECT (R15 killer patterns 2 and 3, FAIL-OPEN and FAIL-SILENT). The
guard exits rc=2, never rc=0, when it cannot see what it is guarding: if the producer module is
missing, if the producer no longer calls `_round_or_none` at all (the nulls would have stopped
being produced, so "no violations" would mean nothing), or if a scanned package is absent. A
guard that reports clean because its subject vanished has lost, not passed.

CLI: `python3 -m tools.structural_blank_guard` -- rc 0 clean, rc 1 violations, rc 2 coverage hole.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

ROOT = Path(__file__).resolve().parent.parent

#: The module that CREATES the nulls. If it stops doing so this guard has lost its subject.
PRODUCER_REL_PATH = "tools/generate_customer_data.py"

#: The helper whose existence IS the deliberate-null contract. Named here so the coverage check
#: and the registry derivation cannot hold two different ideas of what the producer is.
PRODUCER_HELPER = "_round_or_none"

#: Fields the tree deliberately publishes as `null`. Both spellings of each are listed because a
#: consumer reads the SOURCE key off `by_billing_account` and the PUBLISHED key off a customer
#: record, and the defect is identical either side. Kept in sync with the producer by
#: `test_the_registry_matches_the_producer` -- do not edit by hand without running it.
NULLABLE_FIELDS = frozenset({
    # source keys, as read off a `by_billing_account` row
    "clv_gbp",
    "latest_churn_probability",
    "expected_lifetime_periods",
    "avg_annual_net_margin_gbp",
    # published keys, as read off a customer record
    "churn_probability",
    "forecast_annual_profit_gbp",
})

#: Packages searched. `sim/` and `simulation/` are in: the guard is about a READ shape, and a
#: world module reading a company record would be a wall breach this would happen to surface,
#: not a false positive.
SCANNED_PACKAGES = ("company", "saas", "sim", "simulation", "tools", "background", "interface")

#: THE RATCHET. Sites that match the shape but are NOT this defect, each named individually with
#: the measurement that cleared it. It may only SHRINK: `scan_tree(include_known=True)` returns
#: everything, and `test_the_ratchet_has_no_stale_entries` fails when an entry stops matching, so
#: deleting a site FORCES deleting its entry. Nothing can be added without editing this file.
#:
#: Both entries are the SAME name collision: `churn_probability` on a `customer_events` record is
#: the WORLD's per-event churn draw, not the company's nullable per-account estimate. Measured on
#: `docs/reports/run_output_latest.json` at the time of writing: 58 events, 0 null and 0 missing
#: for `churn_probability`, `realized_churn_probability` and `company_churn_estimate`. A field
#: that is never blank cannot fold a blank into an aggregate. If that ever stops being true these
#: become real, which is why they are ratcheted rather than filtered out by a record-type
#: predicate the guard has no way to evaluate.
KNOWN_NON_DEFECTS = {
    "company/analytics/counterfactual_retention.py::churn_probability":
        "reads the WORLD's per-event churn draw off a `customer_events` record (name collision "
        "with the company's nullable per-account estimate). 58/58 events populated, 0 null.",
    "tools/generate_dashboard_data.py::churn_probability":
        "same `customer_events` name collision, feeding the dashboard event table. 58/58 "
        "events populated, 0 null.",
}


class CoverageError(RuntimeError):
    """The guard cannot see its own subject -- an rc=2 condition, never a pass."""


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    field: str
    arm: str

    @property
    def key(self) -> str:
        """The ratchet key: path + FIELD, never the line. A ratchet keyed on a line number
        expires the first time anything above it is edited, and expiring silently is exactly
        the failure this project has filed against pinned controls repeatedly."""
        return f"{self.path}::{self.field}"

    @property
    def known(self) -> bool:
        return self.key in KNOWN_NON_DEFECTS

    def render(self) -> str:
        return (
            f"{self.path}:{self.line}: {self.arm} -- `{self.field}` is published as null on "
            f"purpose and is given a numeric fallback here, so a blank enters as a value. "
            f"Carry the None through and branch on it at the render/aggregate site."
        )


def _is_numeric_constant(node: ast.AST) -> bool:
    """True for `0`, `0.0` and `-1.5`; False for strings, names, `None` and expressions.

    `or "—"` and `or None` are CORRECT handling of a blank, so they must not match."""
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        node = node.operand
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    )


def _get_call_field(node: ast.AST, fields: Iterable[str]) -> str | None:
    """The nullable field name for `<expr>.get("<field>"...)`, else None."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
        return None
    if node.func.attr != "get" or not node.args:
        return None
    first = node.args[0]
    if isinstance(first, ast.Constant) and first.value in fields:
        return first.value
    return None


def _subscript_field(node: ast.AST, fields: Iterable[str]) -> str | None:
    """The nullable field name for `<expr>["<field>"]`, else None."""
    if not isinstance(node, ast.Subscript):
        return None
    key = node.slice
    if isinstance(key, ast.Constant) and key.value in fields:
        return key.value
    return None


def scan_source(source: str, rel_path: str, fields: Iterable[str] = NULLABLE_FIELDS) -> List[Violation]:
    """All three arms over one module's AST. Walks function bodies -- every instance lived in one."""
    fields = frozenset(fields)
    violations: List[Violation] = []
    tree = ast.parse(source, filename=rel_path)
    for node in ast.walk(tree):
        # ARM 1 -- `d.get("f") or 0` / ARM 3 -- `d["f"] or 0`. Python folds a chained `or` into a
        # single BoolOp, so the fallback is the LAST value and the read is any earlier one.
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            if _is_numeric_constant(node.values[-1]):
                for value in node.values[:-1]:
                    field = _get_call_field(value, fields)
                    if field is not None:
                        violations.append(Violation(rel_path, node.lineno, field, "ARM 1 (or-default)"))
                        continue
                    field = _subscript_field(value, fields)
                    if field is not None:
                        violations.append(Violation(rel_path, node.lineno, field, "ARM 3 (subscript-or)"))

        # ARM 2 -- `d.get("f", 0)`.
        if isinstance(node, ast.Call):
            field = _get_call_field(node, fields)
            if field is not None and len(node.args) == 2 and _is_numeric_constant(node.args[1]):
                violations.append(Violation(rel_path, node.lineno, field, "ARM 2 (get-default)"))

    return sorted(violations, key=lambda v: (v.path, v.line, v.field, v.arm))


def producer_nullable_fields(root: Path = ROOT, producer_rel: str = PRODUCER_REL_PATH) -> set:
    """Re-derive the nullable-field set from the producer's AST.

    Every `_round_or_none(<expr>.get("<key>"), n)` contributes its KEY, and where that call is
    bound to a keyword (`clv_gbp=_round_or_none(...)`) or a name, that contributes too -- the
    source spelling and the published spelling are both things a consumer can read.

    This is what stops `NULLABLE_FIELDS` from being a second, rotting copy of the truth.
    """
    path = root / producer_rel
    if not path.is_file():
        raise CoverageError(
            f"producer {producer_rel} is missing -- the deliberate nulls have no declared "
            f"origin, so 'no violations' means nothing"
        )
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=producer_rel)

    def _is_helper_call(node: ast.AST) -> bool:
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        return name == PRODUCER_HELPER

    found: set = set()
    calls = 0
    # Locals bound to a helper call, e.g. `churn_p = _round_or_none(...)`. A LOCAL NAME IS NOT A
    # PUBLISHED FIELD -- `churn_p` is nothing a consumer can read -- so these are not added to the
    # set. They are collected only to resolve the one level of indirection in the keyword arm
    # below, where the published spelling actually appears (`churn_probability=churn_p`).
    helper_locals: set = set()
    for node in ast.walk(tree):
        # the SOURCE key, from the `.get("k")` handed to the helper
        if _is_helper_call(node):
            calls += 1
            for arg in node.args:
                if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) \
                        and arg.func.attr == "get" and arg.args:
                    first = arg.args[0]
                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                        found.add(first.value)
        if isinstance(node, ast.Assign) and _is_helper_call(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    helper_locals.add(target.id)

    # the PUBLISHED key, from the keyword the helper's result is bound to -- either directly
    # (`expected_lifetime_periods=_round_or_none(...)`) or via one of the locals above
    # (`churn_probability=churn_p`).
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg:
            value = node.value
            if _is_helper_call(value) or (isinstance(value, ast.Name) and value.id in helper_locals):
                found.add(node.arg)

    if not calls:
        raise CoverageError(
            f"producer {producer_rel} no longer calls `{PRODUCER_HELPER}` -- either the "
            f"deliberate-null contract was removed or it moved, and this guard is now watching "
            f"a field set nothing produces"
        )
    return found


def _python_files(root: Path, packages: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for package in packages:
        base = root / package
        if not base.is_dir():
            raise CoverageError(
                f"scanned package `{package}/` does not exist under {root} -- the guard would "
                f"pass by scanning nothing"
            )
        files.extend(p for p in sorted(base.rglob("*.py")) if "__pycache__" not in p.parts)
    if not files:
        raise CoverageError(f"no python files found under {list(packages)} in {root}")
    return files


def scan_tree(
    root: Path = ROOT,
    packages: Iterable[str] = SCANNED_PACKAGES,
    fields: Iterable[str] = NULLABLE_FIELDS,
    include_known: bool = False,
) -> List[Violation]:
    """Structural-blank folds under `packages`. Raises CoverageError on an rc=2 condition.

    `include_known=False` (the default, and what the gate runs) drops the ratcheted sites in
    `KNOWN_NON_DEFECTS`. `include_known=True` returns everything, which is how the ratchet's own
    staleness test can see that an entry has stopped matching and must be deleted.
    """
    packages = tuple(packages)
    if not fields:
        raise CoverageError("the nullable-field set is empty -- the guard would scan for nothing")
    violations: List[Violation] = []
    for path in _python_files(root, packages):
        rel = path.relative_to(root).as_posix()
        try:
            violations.extend(scan_source(path.read_text(encoding="utf-8"), rel, fields))
        except SyntaxError as exc:
            raise CoverageError(f"{rel} does not parse ({exc}) -- the guard cannot read it") from exc
    if include_known:
        return violations
    return [v for v in violations if not v.known]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="R10 class closure: structural blanks in aggregates")
    parser.add_argument("--include-known", action="store_true",
                        help="also report the ratcheted sites in KNOWN_NON_DEFECTS")
    args = parser.parse_args(argv)
    try:
        # ROOT and NULLABLE_FIELDS passed explicitly, not left to the default arguments: a default
        # is bound at def time, so a test that repoints ROOT would silently keep scanning the real
        # tree and pass for free.
        producer_fields = producer_nullable_fields(root=ROOT)
        missing = producer_fields - set(NULLABLE_FIELDS)
        if missing:
            raise CoverageError(
                f"the producer publishes {sorted(missing)} as nullable and NULLABLE_FIELDS does "
                f"not list them -- the registry has rotted behind the code that creates the nulls"
            )
        violations = scan_tree(root=ROOT, fields=NULLABLE_FIELDS, include_known=args.include_known)
    except CoverageError as exc:
        print(f"STRUCTURAL-BLANK GUARD COVERAGE HOLE: {exc}", file=sys.stderr)
        return 2
    if violations:
        print(
            f"STRUCTURAL-BLANK GUARD: {len(violations)} site(s) fold a deliberately-null field "
            f"into an aggregate as a number (R10 class closure)",
            file=sys.stderr,
        )
        for violation in violations:
            print("  " + violation.render(), file=sys.stderr)
        return 1
    print(
        f"STRUCTURAL-BLANK GUARD: clean over {len(NULLABLE_FIELDS)} nullable field(s) in "
        f"{'/, '.join(SCANNED_PACKAGES)}/"
        + (f" (+{len(KNOWN_NON_DEFECTS)} ratcheted, see KNOWN_NON_DEFECTS)"
           if KNOWN_NON_DEFECTS and not args.include_known else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
