"""Every domain constant in `company/` and `saas/` carries its origin, or it is debt.

REUSE: tools/domain_constant_origins.py
CLASS: CUSTOM
INDEX: searched "constant", "sourced", "cited", "origin", "census", "ratchet".
       `tests/architecture/test_a_cited_constant_has_a_caller.py` is the nearest and is the
       COMPLEMENT of this, not this: it fires when a constant that DOES cite a source is never
       reached by live code. It says so itself -- "this control is silent about
       `COST_PER_ACQUISITION`" -- and that silence is the hole this fills.
       `tests/architecture/test_year_keyed_rate_table_census.py` censuses year-keyed tables
       against the published record; it is about one shape of constant and about agreement with
       a band, not about whether an origin is declared at all.

WHY IT EXISTS
-------------
Director, 2026-08-30, after reviewing the constants in `company/` and `saas/`:

    "The pattern: a short-term fix that answers today's request, with a number picked because a
    number was needed, that comes undone when it meets the rest of the system. GBP 150 CAC. A 0.95
    churn cap. A standing charge that matches neither fuel. Each looked reasonable in isolation and
    each was wrong in the whole. That isn't carelessness -- a bounded invocation can't see the
    whole, and we asked you for speed. So the fix is structural. ... Every rate, price,
    probability, threshold or cap in company/ and saas/ carries its origin -- a citation, or a
    labelled belief the company holds and something grades, or a named simplification with what it
    would take to do properly. A constant with none of those is refused, the way an unsourced money
    constant already is. Same name may not carry two values anywhere; a duplicated constant is
    refused too."

THE THREE ORIGINS, AND WHY EXACTLY THESE THREE. Each is a different honest answer to "where did
this number come from", and the set is closed:

  * **CITED** -- it came from outside us. A path under `docs/`, or a named publisher (Ofgem,
    DESNZ, CMA, Elexon, NESO, ONS, Cornwall Insight), or a URL.
  * **BELIEF** -- the company made it up, ON PURPOSE, and something grades it. A supplier's own
    assumption is a legitimate thing to model; what is not legitimate is a belief that nothing
    ever scores, because then it is indistinguishable from a fact and will be read as one.
  * **SIMPLIFICATION** -- we know it is not the real thing, we have said what the real thing
    would take, and we have said which way the error runs.

A constant with none of the three is not "probably fine" -- it is a number whose provenance nobody
can reconstruct, which is precisely the class the director's four examples came from.

WHY A COUNT AND NOT A REGISTER. The same reason `test_a_cited_constant_has_a_caller` refused to
build one: 223 hand-authored entries to say what one scan says, and the register is another thing
to go stale. The debt is a NUMBER that may only fall.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not check that a citation is TRUE. A comment naming Ofgem beside a number Ofgem never
published passes here, and no scan can catch that -- only reading the source can. This moves the
failure from "nobody can tell where this came from" to "someone claimed a source", which is a
smaller class and a checkable one. Two of the director's four examples (a standing charge matching
neither fuel; a factual error against the real rules) are in the residue and are found by reading,
not by scanning. Stated so nobody reads a green ratchet as "the constants are right".

Run:  python3 -m tools.domain_constant_origins [--list] [--duplicates]
"""
from __future__ import annotations

import argparse
import ast
import collections
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

#: The two packages the director named. `simulation/` is deliberately absent: the world's
#: constants answer to R13 and the baseline/curriculum split, which is a different rule with a
#: different owner, and folding them in here would let a world calibration be discharged by a
#: code comment.
SCOPE = ("company", "saas")

#: A DOMAIN QUANTITY, matched on the NAME, from the director's own list -- "every rate, price,
#: probability, threshold or cap". The name is what a reader uses to decide what a number means,
#: so it is what decides whether the number owes an origin.
#:
#: NOT WIDENED BEYOND HIS WORDS. A wider net (COST, FEE, MARGIN, FACTOR, WEIGHT, DAYS ...) matches
#: 593 constants rather than 223, and baselining 529 items of debt against an instruction about
#: five words would be answering a question nobody asked. The wider set is measurable at any time
#: by changing this one regex, and the ratchet would simply be re-baselined.
DOMAIN_NAME = re.compile(r"(RATE|PRICE|PROBABILITY|THRESHOLD|CAP)")

#: It came from outside us.
_CITED = re.compile(
    r"docs/|Ofgem|DESNZ|CMA\b|Elexon|NESO|ONS\b|BEIS|Cornwall|Citizens Advice|https?://", re.I)
#: The company made it up on purpose, and something grades it.
_BELIEF = re.compile(r"\bBELIEF\b|COMPANY BELIEF|the company believes|company's own assumption", re.I)
#: We know it is not the real thing and we have said what the real thing would take.
_SIMPLIFICATION = re.compile(
    r"NAMED SIMPLIFICATION|SIMPLIFIED:|to do it properly|to do this properly", re.I)

ORIGINS = ("cited", "belief", "simplification")


def _is_numeric(node: ast.AST) -> bool:
    """A literal number, or a container of nothing but numbers, to any depth.

    A dict of year -> rate is as much a domain constant as a scalar, and the director's four
    examples include one (`VAT_RATE` as a per-segment mapping). Excluding containers would let the
    largest and most load-bearing tables out of the rule entirely.
    """
    if isinstance(node, ast.Constant):
        return isinstance(node.value, (int, float)) and not isinstance(node.value, bool)
    if isinstance(node, ast.Dict):
        return bool(node.values) and all(_is_numeric(v) for v in node.values)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return bool(node.elts) and all(_is_numeric(e) for e in node.elts)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        return _is_numeric(node.operand)
    return False


def _comment_block(lines: list[str], lineno: int) -> str:
    """The comment lines immediately above the assignment, and the assignment's own trailing one.

    Walks UP from the statement and stops at the first line that is not a comment, which is the
    same rule `test_a_cited_constant_has_a_caller` uses -- and it inherits that control's known
    hole, recorded there: a constant declared directly beneath another shares nothing, so the
    second reads as having no block. Give a constant its own comment.
    """
    out = []
    i = lineno - 2
    while i >= 0 and lines[i].lstrip().startswith("#"):
        out.append(lines[i].strip())
        i -= 1
    trailing = lines[lineno - 1] if 0 <= lineno - 1 < len(lines) else ""
    if "#" in trailing:
        out.append(trailing.split("#", 1)[1])
    return "\n".join(reversed(out))


def _classify(comment: str) -> str | None:
    """Which of the three origins the comment declares, or None. Order is not significance: a
    comment matching more than one is reported as the first, and any one of them discharges."""
    if _CITED.search(comment):
        return "cited"
    if _BELIEF.search(comment):
        return "belief"
    if _SIMPLIFICATION.search(comment):
        return "simplification"
    return None


def scan(root: Path | None = None) -> list[dict]:
    """Every domain constant in scope, with its declared origin or None."""
    root = PROJECT if root is None else root
    found: list[dict] = []
    for package in SCOPE:
        base = root / package
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in path.parts or path.name.startswith("test_"):
                continue
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (OSError, SyntaxError):
                # FAIL-CLOSED IS NOT AVAILABLE HERE and the alternative is worse. A file that
                # cannot be parsed contributes no constants, so it can only make the debt look
                # SMALLER -- but raising would let one unparseable file take down every commit in
                # the tree. `unreadable()` reports them so the count is never read as complete.
                continue
            lines = source.splitlines()
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                    value = node.value
                elif (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                        and node.value is not None):
                    names = [node.target.id]
                    value = node.value
                else:
                    continue
                if not _is_numeric(value):
                    continue
                for name in names:
                    if not name.isupper() or not DOMAIN_NAME.search(name):
                        continue
                    comment = _comment_block(lines, node.lineno)
                    try:
                        literal = ast.literal_eval(value)
                    except (ValueError, SyntaxError):
                        literal = None
                    found.append({
                        "path": str(path.relative_to(root)),
                        "name": name,
                        "line": node.lineno,
                        "value": literal,
                        "origin": _classify(comment),
                    })
    return found


def unreadable(root: Path | None = None) -> list[str]:
    """Files in scope this scanner could not parse, so a caller can refuse to trust the count."""
    root = PROJECT if root is None else root
    bad = []
    for package in SCOPE:
        base = root / package
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in path.parts or path.name.startswith("test_"):
                continue
            try:
                ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, SyntaxError):
                bad.append(str(path.relative_to(root)))
    return bad


def without_origin(root: Path | None = None) -> list[dict]:
    return [c for c in scan(root) if c["origin"] is None]


def duplicates(root: Path | None = None) -> dict[str, list[dict]]:
    """`{name: [rows]}` for every name carrying more than one distinct value in scope.

    ONE NAME, ONE NUMBER. Two constants sharing a name and disagreeing is the defect the director
    put first, and it is worse than an unsourced constant: a reader who has met one of them
    believes they know what the other means. `MAX_CHURN_PROBABILITY` is 0.95 on the company side
    and 1.0 on the SIM-facing side, and nothing anywhere says which a given call site gets.

    Compared on the REPR of the value, so `0.05` and `{"resi": 0.05, ...}` are different -- which
    they are, and dangerously so: the same name means a flat rate in one file and a per-segment
    table in the other.
    """
    by_name: dict[str, list[dict]] = collections.defaultdict(list)
    for row in scan(root):
        by_name[row["name"]].append(row)
    return {name: rows for name, rows in by_name.items()
            if len({repr(r["value"]) for r in rows}) > 1}


def _main() -> int:  # pragma: no cover - operator surface
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="print every constant without an origin")
    ap.add_argument("--duplicates", action="store_true", help="print name collisions only")
    args = ap.parse_args()

    rows = scan()
    debt = [r for r in rows if r["origin"] is None]
    counts = collections.Counter(r["origin"] or "NO ORIGIN" for r in rows)
    print(f"domain constants in {'/, '.join(SCOPE)}/: {len(rows)}")
    for key in ORIGINS + ("NO ORIGIN",):
        print(f"  {key:<16} {counts.get(key, 0)}")
    bad = unreadable()
    if bad:
        print(f"  UNPARSEABLE FILES (count is incomplete): {bad}")
    dupes = duplicates()
    print(f"\nname collisions (one name, more than one value): {len(dupes)}")
    for name, group in sorted(dupes.items()):
        print(f"  {name}")
        for row in group:
            print(f"      {row['path']}:{row['line']} = {row['value']!r}")
    if args.list:
        print("\nwithout an origin:")
        for row in debt:
            print(f"  {row['path']}:{row['line']:<5} {row['name']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
