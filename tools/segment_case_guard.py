"""W2_sme_segment_case_normalisation -- the R10 class closure.

WHY A GUARD AND NOT JUST A FIX
-------------------------------
The defect this closes was a market-segment string compared in the wrong CASE:

    simulation/arrears_engine.payment_method:   segment == "sme"
    simulation/payment_behaviour_source:        segment in ("ic", "I&C", "sme")

`saas/customers.py` stores segments canonically ("resi", "SME", "I&C"), so a
real SME bill matched NEITHER test and was billed as a household, and a real
I&C bill spelled "IC" did the same. Nothing raised; the customer simply took
the wrong branch for the entire history.

R10 says an absurdity-class defect may not be closed with an instance fix.
Fixing those two lines closes two instances; the CLASS is "any segment
comparison anywhere in `simulation/` that spells a segment non-canonically",
and the supply of that class is infinite because writing `== "sme"` is the
obvious thing to type. This guard is what makes the class structurally unable
to come back: a new non-canonical segment literal fails at commit time rather
than being discovered by a customer being mis-billed.

WHAT IT FLAGS
-------------
A string literal whose casefolded form is a KNOWN segment alias but whose
exact spelling is not the canonical one, appearing in either:

  1. a comparison  -- `seg == "sme"`, `seg in ("ic", "I&C")`, at any depth
     inside the compared tuple/list/set; or
  2. a constant collection of segment labels -- which is how
     `_IC_SEGMENTS = ("ic", "I&C")` re-enters through the back door.

Canonical spellings are not flagged in a COMPARISON: `seg == "resi"` is correct
today. It is still better written `normalise_segment(seg) == RESIDENTIAL`, but
this guard enforces CORRECTNESS, not style -- a guard that also fired on
correct code would be turned off within a week.

AND (W2_15) A DUPLICATED VOCABULARY, EVEN A CANONICAL ONE
----------------------------------------------------------
A collection of two-or-more CANONICAL segment literals outside the vocabulary
module is a second declaration of a vocabulary that already has an owner --
`simulation/sme_distress.BUSINESS_SEGMENTS = ("SME", "I&C")` was one, and the
`in` test against it was case-sensitive, so a lower-case "sme" raised instead
of being recognised.

This is the guard admitting a LIMIT rather than pretending to a coverage it
does not have. The defect there is in the COMPARISON, and an AST scan cannot
see that a name compared with `in` was built from literals three hundred lines
earlier -- that needs dataflow. What the scan CAN see is the private copy that
makes the unsafe comparison possible in the first place. Remove the copy and
the comparison has nothing case-sensitive left to compare against; keep it and
the class regenerates. So the copy is what is flagged, and the limit is stated
here rather than left for a reader to infer from a green run:

  STILL NOT COVERED: a case-sensitive comparison against a vocabulary imported
  by name from somewhere else in the same module. Route segment tests through
  `normalise_segment()`; the guard cannot do it for you.

FAIL-OPEN FOUND AND CLOSED (W2_15)
-----------------------------------
The constant-collection channel above originally visited `ast.Assign` only, so
an ANNOTATED assignment -- `_IC_SEGMENTS: Tuple[str, ...] = ("ic", "I&C")`, a
different AST node -- walked straight past a guard written to catch exactly
that constant. Adding a type hint disabled the control. It was not academic:
the one real segment vocabulary in `simulation/` was annotated, which is why
the guard had never once looked at it. `visit_AnnAssign` closes it, and
`TestAnnotatedAssignment` is the mutation proof.

FAIL-CLOSED (R15)
-----------------
Three ways a checker like this normally fails open, all closed deliberately:

  - MISSING ROOT: if the scanned directory does not exist, that is a FAILURE,
    not "zero violations found". A control that passes because it checked
    nothing is the fail-silent pattern R15 names.
  - UNPARSEABLE FILE: a file that will not parse is a FAILURE, not a skip.
    Skipping it would let a violation hide behind a syntax error.
  - EMPTY SCAN: if the scan visits zero files, that is a FAILURE. This is the
    vacuity guard -- 0 violations over 0 files is not evidence of anything.

Exit code 0 = clean, 1 = violations found, 2 = the guard could not run (which
callers must treat as a failure, never as a pass).
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from simulation.segment_vocabulary import _ALIASES, CANONICAL_SEGMENTS

#: Modules allowed to contain non-canonical segment spellings, with the reason.
#: `segment_vocabulary` IS the alias table -- its lower-case keys are the
#: sanctioned home for every spelling that has ever drifted, and flagging them
#: would make the guard fire on its own single source of truth.
EXEMPT = {
    "simulation/segment_vocabulary.py": "the alias table itself",
}


class SegmentCaseViolation(ast.NodeVisitor):
    """Collect non-canonical segment literals in comparison/constant context."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.violations: list[tuple[int, str]] = []

    def _check(self, node: ast.AST) -> None:
        """Flag every non-canonical alias literal anywhere under `node`."""
        for child in ast.walk(node):
            if not isinstance(child, ast.Constant) or not isinstance(child.value, str):
                continue
            raw = child.value
            key = raw.strip().casefold()
            canonical = _ALIASES.get(key)
            if canonical is not None and raw != canonical:
                self.violations.append((
                    child.lineno,
                    "segment literal %r is not canonical -- use %r (or better, "
                    "simulation.segment_vocabulary.normalise_segment)"
                    % (raw, canonical),
                ))

    def visit_Compare(self, node: ast.Compare) -> None:
        self._check(node)
        self.generic_visit(node)

    def _check_collection(self, value: ast.AST | None) -> None:
        # A hand-rolled collection of segment labels, under ANY name. Keying
        # this on the NAME (`"SEGMENT" in name`) was the guard's own first
        # fail-open: `_IC_SEGMENTS` would have been caught, but the identical
        # hazard spelled `_BUSINESS_LABELS` or `_RAILS` would not. What makes
        # a collection a segment vocabulary is its CONTENTS, so that is what
        # is tested.
        if not isinstance(value, (ast.Tuple, ast.List, ast.Set)):
            return
        elements = value.elts
        all_alias_literals = bool(elements) and all(
            isinstance(e, ast.Constant)
            and isinstance(e.value, str)
            and e.value.strip().casefold() in _ALIASES
            for e in elements
        )
        if not all_alias_literals:
            return
        self._check(value)
        # W2_15: all-canonical is not a pass here -- it is a SECOND copy of a
        # vocabulary that already has an owner, and the `in` test against a
        # private copy is case-sensitive. Two or more, because a single
        # canonical literal in a collection is not a vocabulary.
        spellings = [e.value for e in elements]
        if len(spellings) >= 2 and all(s in CANONICAL_SEGMENTS for s in spellings):
            self.violations.append((
                value.lineno,
                "segment vocabulary %r is re-declared here -- import it from "
                "simulation.segment_vocabulary instead. Every copy drifts, and "
                "a bare `in` against a copy is case-SENSITIVE, so a lower-case "
                "spelling silently is not a member" % (tuple(spellings),),
            ))

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_collection(node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        # `X: Tuple[str, ...] = ("ic", "I&C")` is an AnnAssign, NOT an Assign.
        # Visiting only Assign meant a type annotation switched this control
        # off -- see FAIL-OPEN FOUND AND CLOSED in the module docstring.
        self._check_collection(node.value)
        self.generic_visit(node)


def _display_path(path: Path, repo_root: Path) -> str:
    """Repo-relative where possible, absolute otherwise.

    `--root` may point outside the repo (the R15 mutation tests scan a
    tmp_path), so this must not assume containment.
    """
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def scan_file(path: Path, repo_root: Path) -> list[tuple[int, str]]:
    source = path.read_text(encoding="utf-8")
    # A file that will not parse is a FAILURE, not a skip -- letting a
    # SyntaxError through would let a violation hide behind it.
    tree = ast.parse(source, filename=str(path))
    visitor = SegmentCaseViolation(_display_path(path, repo_root))
    visitor.visit(tree)
    return visitor.violations


def scan(root: Path, repo_root: Path) -> tuple[list[str], int]:
    """Return (violation messages, number of files actually scanned)."""
    if not root.is_dir():
        raise FileNotFoundError(
            "segment_case_guard: scan root %s does not exist -- a control that "
            "checks nothing has FAILED, not passed" % root
        )
    messages: list[str] = []
    scanned = 0
    for path in sorted(root.rglob("*.py")):
        rel = _display_path(path, repo_root)
        if rel in EXEMPT:
            continue
        scanned += 1
        for lineno, detail in scan_file(path, repo_root):
            messages.append("%s:%d: %s" % (rel, lineno, detail))
    return messages, scanned


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(repo_root / "simulation"),
        help="directory to scan (default: simulation/)",
    )
    args = parser.parse_args(argv)

    try:
        messages, scanned = scan(Path(args.root), repo_root)
    except (FileNotFoundError, SyntaxError, UnicodeDecodeError) as exc:
        print("SEGMENT CASE GUARD: COULD NOT RUN -- %s" % exc, file=sys.stderr)
        return 2

    # Vacuity guard: 0 violations over 0 files is not evidence of anything.
    if scanned == 0:
        print(
            "SEGMENT CASE GUARD: COULD NOT RUN -- scanned 0 files under %s"
            % args.root,
            file=sys.stderr,
        )
        return 2

    if messages:
        print("SEGMENT CASE GUARD: %d violation(s)" % len(messages), file=sys.stderr)
        for message in messages:
            print("  " + message, file=sys.stderr)
        return 1

    print("SEGMENT CASE GUARD: clean (%d files scanned)" % scanned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
