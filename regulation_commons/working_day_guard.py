"""AST guard: no module may re-implement working-day arithmetic.

This is the CLASS mechanism (R10). The original defect -- "Bacs rails counting
calendar rather than working days" -- was fixed once as an instance, but 22
modules each carried their own private ``weekday() < 5`` loop, so the same
defect could be reintroduced 22 more ways. Migrating all 22 fixes today; this
guard is what stops tomorrow. Without it this atom is 22 instance fixes
wearing a class fix's clothes.

    python3 -m regulation_commons.working_day_guard

Exit 0 = no second definition. Exit 1 = violations, listed file:line. It is a
standalone entry point with its own exit code, deliberately not folded into a
broad "the tests pass" umbrella where its own crash or absence would be
invisible (R15, fail-silent).

TWO DETECTORS, because a name-only check is fail-open:

1. NAME -- a function/method defined outside the sanctioned module whose name
   matches a known working-day helper, including the canonical names
   themselves so a copy-paste-and-rename cannot dodge the guard.
2. SHAPE -- a loop that walks days one at a time (``timedelta(days=1)`` or an
   ordinal ``+ 1``) while testing ``.weekday()``. This is the structural
   signature of the arithmetic regardless of what anybody calls it. Three of
   the original 22 had no named helper at all and would have sailed past a
   name-only check; a future careless reimplementation under a novel name
   trips this even though it trips nothing in detector 1.

NOT A TAUTOLOGY (R15): neither detector asks
``regulation_commons.working_days`` what it exports. The name list is the
independently-grepped census from the DISCOVER pass, and the shape detector
describes the defect's structure, not the fix's API. The guard would still
fire if this package were deleted entirely -- which is the point: it checks
for the defect, not for agreement with itself.

FAIL-CLOSED (R15): a file that cannot be read or parsed is reported as a
VIOLATION, not skipped. An unparseable module is an unchecked module, and an
unchecked module is a failed check.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterable, List, NamedTuple, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent

#: Trees whose modules must not define working-day arithmetic.
SCANNED_TREES: Sequence[str] = ("company", "sim", "simulation", "saas")

#: The single sanctioned home. Files here are exempt -- this is where the one
#: definition is *supposed* to live.
SANCTIONED = ("regulation_commons",)

#: Helper names from the DISCOVER census, plus the canonical API names so a
#: rename-and-copy is still caught.
BANNED_NAMES = frozenset(
    {
        "_add_working_days",
        "_working_days_between",
        "working_days_open",
        "working_days_to_pay",
        "add_working_days",
        "working_days_between",
        "working_days_elapsed",
        "is_working_day",
        "is_bank_holiday",
        "_is_working_day",
        "_next_working_day",
        "next_working_day",
        "_add_business_days",
        "add_business_days",
        "business_days_between",
    }
)

#: Named exemptions, for domain ACCESSORS that legitimately carry one of the
#: banned names while doing no arithmetic themselves (they delegate to the
#: canonical module). Each entry must carry a reason; an entry without one is a
#: silent hole. Kept deliberately tiny -- an allowlist that grows is a guard
#: being negotiated away.
#:
#: An exemption suppresses the NAME detector ONLY. The SHAPE detector still
#: runs on every allowlisted function, so putting day-walking arithmetic back
#: inside one of these still fails the guard. An allowlist that could disable
#: both detectors would be a fail-open hole with a comment on it.
ALLOWLIST: dict = {
    ("company/billing/credit_refund.py", "working_days_to_pay"): (
        "domain accessor on CreditRefundRecord -- reports this record's own "
        "elapsed-working-days figure by delegating to "
        "regulation_commons.working_days.working_days_elapsed; defines no arithmetic"
    ),
    ("company/market/erroneous_transfer.py", "working_days_open"): (
        "domain accessor on the claim record -- delegates to "
        "regulation_commons.working_days.working_days_between; defines no arithmetic"
    ),
    ("company/regulatory/gsop_tracker.py", "working_days_open"): (
        "domain accessor property on the breach record -- delegates to "
        "regulation_commons.working_days.working_days_between; defines no arithmetic"
    ),
}


class Violation(NamedTuple):
    path: str
    lineno: int
    name: str
    reason: str

    def render(self) -> str:
        return f"{self.path}:{self.lineno}: {self.name} -- {self.reason}"


def _walks_days_by_weekday(node: ast.AST) -> bool:
    """True if this function body steps one day at a time AND tests weekday().

    That pairing is what working-day arithmetic *is*. Either half alone is
    innocent: plenty of code adds a day, plenty of code asks what weekday it
    is. Requiring both keeps the false-positive rate at zero across the tree
    while still catching an unnamed reimplementation.
    """
    has_weekday = False
    has_day_step = False
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr == "weekday":
            has_weekday = True
        # timedelta(days=1) / timedelta(1)
        if isinstance(child, ast.Call):
            func = child.func
            fname = getattr(func, "attr", None) or getattr(func, "id", None)
            if fname == "timedelta":
                for kw in child.keywords:
                    if kw.arg == "days" and isinstance(kw.value, ast.Constant) and kw.value.value == 1:
                        has_day_step = True
                if child.args and isinstance(child.args[0], ast.Constant) and child.args[0].value == 1:
                    has_day_step = True
            # date.fromordinal(x.toordinal() + 1) -- the gsop_tracker shape
            if fname == "fromordinal":
                has_day_step = True
    if not (has_weekday and has_day_step):
        return False
    # Only count it when the stepping happens inside a loop -- a single
    # `d + timedelta(days=1)` next to an unrelated weekday check is not
    # working-day arithmetic.
    for child in ast.walk(node):
        if isinstance(child, (ast.While, ast.For)):
            return True
    return False


def _is_sanctioned(rel: str) -> bool:
    return any(rel == s or rel.startswith(s + "/") for s in SANCTIONED)


def scan_file(path: Path, rel: str) -> List[Violation]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [Violation(rel, 0, "<unreadable>", f"cannot read file ({exc}) -- unchecked means FAILED")]
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [Violation(rel, exc.lineno or 0, "<unparseable>", f"cannot parse file ({exc.msg}) -- unchecked means FAILED")]

    found: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        name_exempt = (rel, node.name) in ALLOWLIST
        if node.name in BANNED_NAMES and not name_exempt:
            found.append(
                Violation(
                    rel,
                    node.lineno,
                    node.name,
                    "re-defines a working-day helper; import it from "
                    "regulation_commons.working_days instead",
                )
            )
        elif _walks_days_by_weekday(node):
            found.append(
                Violation(
                    rel,
                    node.lineno,
                    node.name,
                    "walks days one at a time while testing .weekday() -- that is "
                    "working-day arithmetic under another name; use "
                    "regulation_commons.working_days",
                )
            )
    return found


def iter_python_files(root: Path, trees: Iterable[str]) -> Iterable[tuple]:
    for tree in trees:
        base = root / tree
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            rel = path.relative_to(root).as_posix()
            if _is_sanctioned(rel):
                continue
            yield path, rel


def find_violations(root: Path = REPO_ROOT, trees: Sequence[str] = SCANNED_TREES) -> List[Violation]:
    """Every second definition of working-day arithmetic under ``trees``."""
    scanned = 0
    violations: List[Violation] = []
    for path, rel in iter_python_files(root, trees):
        scanned += 1
        violations.extend(scan_file(path, rel))
    if scanned == 0:
        # A guard that scanned nothing has proven nothing. Reporting green here
        # is the fail-open pattern in its purest form.
        return [
            Violation(
                str(root),
                0,
                "<no-files-scanned>",
                f"guard scanned 0 files under {list(trees)} -- a guard that inspects "
                "nothing cannot pass",
            )
        ]
    return violations


def main(argv: Sequence[str] | None = None) -> int:
    violations = find_violations()
    if violations:
        print("WORKING-DAY GUARD: FAIL -- second definitions of working-day arithmetic found")
        for violation in violations:
            print("  " + violation.render())
        print(
            f"\n{len(violations)} violation(s). There is exactly one working-day "
            "calculator: regulation_commons.working_days."
        )
        return 1
    print("WORKING-DAY GUARD: PASS -- one definition only (regulation_commons.working_days)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
