"""Every published count derived from a quotient says whether its denominator can reach zero.

REUSE: tools/unbounded_quotient_census.py
CLASS: CUSTOM
INDEX: searched "quotient", "denominator", "needed", "unbounded", "census", "ratchet", "published".
       `tools/domain_constant_origins.py` is the nearest in SHAPE and is the model this follows --
       an AST census over a tree, a closed set of honest declarations, and a debt count that may
       only fall. It is not this: its subject is a CONSTANT's provenance, and every site here is a
       DERIVED value whose provenance is arithmetic nobody disputes. `tests/architecture/
       test_published_row_scalar_census.py` walks published rows for scalar shape, not for the
       arithmetic behind a scalar. `company/compliance/domain_invariants.py` fixes absurdities as
       classes but over simulation state, and has no reader for `tools/`.

WHY IT EXISTS
-------------
FOUR INSTANCES OF ONE RULE WERE FOUND AND FIXED ONE AT A TIME, and every one of them was found by
a human-ish read of a block that happened to sit next to the last one:

  * `06e316ae4` -- the seed price removed from a page key
  * `5742edb1c` -- and from a second page key, derived rather than copied
  * `964036259` -- bounded at the money leg's producer; its census found the fourth
  * `949f80894` -- bounded at the rank leg's producer

Nothing in the tree could see the shape. That is the VAT shape `CLAUDE.md` names -- one
requirement, several implementations, fixed in some and live in the rest -- and four instances is
no longer evidence of four bugs.

THE RULE, STATED ONCE
---------------------
A count derived as `(bar / estimate) ** 2`, or as any quotient whose DENOMINATOR is a measured
quantity rather than a chosen one, has **no upper bound** in exactly the state where a reader wants
it. Clearing a sign bar IS the statement that the denominator's interval excludes zero; failing it
IS the statement that the interval contains zero; and a denominator that may be zero prices the
question at no finite number. Published under a name whose grammar is a plan -- `*_needed` -- it
tells a reader that buying that many settles the question, which is the claim that is false.

WHAT A SITE MUST DECLARE, AND WHY EXACTLY THESE TWO
---------------------------------------------------
The set is closed because there are only two ways a quotient can be honest:

  * **GATED** -- the count is withheld where its denominator may reach zero, and a sibling key in
    the same published dict NAMES the withholding. This is the form the four fixes established:
    `X_needed` beside `X_needed_unavailable_because` (or `X_needed_interval`, or `X_withheld_*`),
    with the arithmetic kept under `X_at_the_point_estimate` -- a name that is not a plan.
  * **BOUNDED** -- the denominator cannot approach zero, and the site says so. A chosen tolerance
    and a unit-conversion rate are both legitimately bounded; what is not legitimate is leaving the
    reader to work out which kind a denominator is. Declared with a `#: DENOMINATOR BOUNDED:`
    comment on the site, or a sibling key spelling the same thing.

A site with neither is DEBT. Not "probably fine" -- a divergence nobody has looked at, which is
precisely the class the four fixed instances came from.

WHY A COUNT AND NOT A REGISTER. The same reason `domain_constant_origins` refused one: a register
is a second thing to go stale, and the declaration belongs beside the arithmetic where the next
reader meets it. The debt is a NUMBER that may only fall.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not decide whether a denominator's interval ACTUALLY contains zero -- no scan can, because
that is a fact about the data and not about the source. A site declaring `DENOMINATOR BOUNDED`
over an estimate that routinely sits at zero passes here. This moves the failure from "nobody in
the tree can see this shape" to "someone classified this denominator", which is a smaller class and
a checkable one.

It resolves names one function deep. A count assembled across two functions, or through a dict
round-trip, is not reached -- `_auc_against_the_money_legs_price` republishes a count it never
computes and is invisible here. Stated so nobody reads a green ratchet as "every count is bounded".

Run:  python3 -m tools.unbounded_quotient_census [--list] [--debt] [--roots tools saas company]
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

#: THE TREES THIS WALKS. `tools/` produces the published artefacts, `saas/` and `company/` the
#: business figures. `simulation/` is deliberately out: ground truth has no sign bar to fail.
DEFAULT_ROOTS = ("tools", "saas", "company")

#: THE PLAN GRAMMAR. A key matching this promises a reader that buying this many settles the
#: question. `_at_the_point_estimate` is the escape hatch the four fixes established and is
#: excluded by construction -- it is the name a count is MOVED to, so matching it would red the
#: very repair this control exists to ask for.
#:
#: `to_state_a_sign` WAS HERE AND WAS REMOVED, which is a narrowing and so had to be measured
#: rather than argued. It names the QUESTION, not a plan, so it also matched `rosters_to_state_a_
#: sign` -- the key carrying the whole BLOCK, whose own counts are censused separately two keys
#: down. Grading a block by the gate on a count inside it is a category error in both directions.
#: The narrowing costs nothing: every one of the seven keys in `tools/`, `saas/` and `company/`
#: bearing that suffix ALSO carries `needed`, except that one block. Re-check before widening.
PLAN_GRAMMAR = re.compile(r"(?:^|_)(needed|required|must_offer)(?:$|_)")

#: THE WITHHOLDING SIBLINGS. Any of these, on the same key stem OR anywhere in the same published
#: dict, is the GATED declaration. Spelled as a family rather than one name because the four fixed
#: sites each chose a different one and all four are honest.
WITHHOLDING = re.compile(r"unavailable|withheld|_interval$|cannot|not_a_range|no_upper_bound")

#: THE VOCABULARY OF A GRADE. A withholding must be conditioned on a name from this set -- the
#: statement "this estimate failed its own bar" -- and not on a degenerate-input check. Narrow on
#: purpose: `#: DENOMINATOR BOUNDED:` is the escape hatch for a gate spelled some other way, and a
#: gate this cannot read is better read as debt than waved through by a synonym. `available` is
#: NOT here and was considered: it is the commonest key in this tree and admitting it would pass
#: almost every site by accident.
GRADE_VOCAB = re.compile(
    r"clear|stateable|state_a_sign|resolvab|distinguishab|significan|_bar\b|bar_|detectab")

#: THE BOUNDED DECLARATION. A comment anywhere in the site's enclosing function, or a matching
#: sibling key. Upper case because it is a claim about the world and should read like one.
BOUNDED_MARKER = re.compile(r"DENOMINATOR BOUNDED")

#: HOW FAR A VALUE EXPRESSION IS FOLLOWED BACK. Set by MEASUREMENT and not by taste: at six this
#: missed `rosters_needed_to_state_a_sign`, whose chain is `key -> IfExp -> name -> call ->
#: return -> IfExp -> ceil -> pow -> div` -- nine hops, and the site vanished from the census
#: entirely rather than reading DEBT, because a site with no divisor found is a site not walked.
#: Twelve is nine plus room. A hole in this number is SILENT, which is why it is stated here.
RESOLVE_DEPTH = 12


def _names(node: ast.AST) -> set[str]:
    """Every identifier mentioned in an expression, including attribute tails."""
    out: set[str] = set()
    for inner in ast.walk(node) if node is not None else []:
        if isinstance(inner, ast.Name):
            out.add(inner.id)
        elif isinstance(inner, ast.Attribute):
            out.add(inner.attr)
        elif isinstance(inner, ast.Constant) and isinstance(inner.value, str):
            out.add(inner.value)
    return out


def _is_chosen(node: ast.AST) -> bool:
    """Is this denominator a CHOSEN number rather than a measured one?

    A literal, or a name/attribute in the repo's constant case. `DISTRIBUTION_TOLERANCE` is chosen
    and `abs(distance)` is not, and that difference is the whole discriminator: a tolerance the
    author picked cannot drift to zero without someone editing it, and an estimate can do it by
    Tuesday.
    """
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.Name):
        return node.id.lstrip("_").isupper()
    if isinstance(node, ast.Attribute):
        return node.attr.lstrip("_").isupper()
    if isinstance(node, ast.Call):
        # `sqrt(CONST)`, `float(CONST)` -- a chosen number through a pure transform is still chosen.
        return all(_is_chosen(arg) for arg in node.args) and bool(node.args)
    if isinstance(node, ast.BinOp):
        return _is_chosen(node.left) and _is_chosen(node.right)
    if isinstance(node, ast.UnaryOp):
        return _is_chosen(node.operand)
    return False


class _Resolver:
    """Follows a published value back to the arithmetic that produced it, inside one function.

    Deliberately shallow and deliberately loud about it -- see the module docstring's last
    paragraph. What it must reach is the four fixed sites, and it does.
    """

    def __init__(self, scope: ast.AST):
        self.assigns: dict[str, list[ast.AST]] = {}
        self.funcs: dict[str, ast.AST] = {}
        for node in ast.walk(scope):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.funcs.setdefault(node.name, node)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.assigns.setdefault(target.id, []).append(node.value)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.value is not None:
                    self.assigns.setdefault(node.target.id, []).append(node.value)

    def _reach(self, node: ast.AST, depth: int, seen: frozenset, collect):
        """One traversal, two questions. `collect(node)` is called on every expression reached.

        ONE WALK AND NOT TWO, because two walks over the same chain with different stopping rules
        is how the divisor answer and the nullability answer would come to describe different
        expressions -- and the grade is read off BOTH.
        """
        if depth <= 0 or node is None:
            return
        collect(node)
        if isinstance(node, ast.BinOp):
            self._reach(node.left, depth - 1, seen, collect)
            self._reach(node.right, depth - 1, seen, collect)
        elif isinstance(node, (ast.IfExp, ast.BoolOp)):
            for branch in ([node.body, node.orelse] if isinstance(node, ast.IfExp)
                           else node.values):
                self._reach(branch, depth - 1, seen, collect)
        elif isinstance(node, ast.UnaryOp):
            self._reach(node.operand, depth - 1, seen, collect)
        elif isinstance(node, ast.Name):
            if node.id not in seen:
                nxt = seen | {node.id}
                for value in self.assigns.get(node.id, []):
                    self._reach(value, depth - 1, nxt, collect)
        elif isinstance(node, ast.Call):
            for arg in node.args:
                self._reach(arg, depth - 1, seen, collect)
            name = (node.func.id if isinstance(node.func, ast.Name)
                    else node.func.attr if isinstance(node.func, ast.Attribute) else None)
            body = self.funcs.get(name) if name else None
            if body is not None and name not in seen:
                nxt = seen | {name}
                for inner in ast.walk(body):
                    if isinstance(inner, ast.Return):
                        self._reach(inner.value, depth - 1, nxt, collect)

    def divisors(self, node: ast.AST) -> list[ast.AST]:
        """Every DENOMINATOR expression this value is built from. Empty means no quotient."""
        found: list[ast.AST] = []
        self._reach(node, RESOLVE_DEPTH, frozenset(),
                    lambda n: found.append(n.right)
                    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div) else None)
        return found

    def withheld_on_a_grade(self, node: ast.AST) -> bool:
        """Is this value withheld because the DENOMINATOR FAILED ITS BAR -- not merely sometimes?

        THE HALF A SIBLING KEY CANNOT ESTABLISH, and half the reason this exists. `X_needed` beside
        `X_needed_unavailable_because` READS gated; if the count is computed unconditionally the
        reason key is a promise the site cannot keep, and a control that asked only for the sibling
        would go green on exactly the defect it was written for.

        AND "CAN IT BE None" IS NOT THAT QUESTION EITHER -- found by mutation, 2026-09-22, and this
        is why the function is not called `can_be_none` any more. Un-gating the repaired
        `rosters_needed_to_state_a_sign` from `point if clears_bar else None` to a bare `point`
        LEFT THE CONTROL GREEN, because `price_at` returns `None` when the distance is exactly zero
        and that `None` satisfied a mere reachability test. A guard against a degenerate input and
        a withholding on a failed bar are different statements that collapse into the flattering
        one the moment you only ask whether `None` is possible: the first fires on a measure-zero
        input nobody meets, the second across the entire state a reader asks the question in.

        So the condition controlling the `None` must NAME the grade. The vocabulary is deliberately
        narrow -- a site is free to spell its gate `#: DENOMINATOR BOUNDED:` instead, and a gate
        this cannot read is better surfaced as debt than waved through by a synonym.
        """
        witnesses: list[set[str]] = []

        def note(n):
            # A WITHHOLDING WRITTEN AT THE SITE: `count if clears_bar else None`.
            if isinstance(n, ast.IfExp) and any(
                    isinstance(b, ast.Constant) and b.value is None
                    for b in (n.body, n.orelse)):
                witnesses.append(_names(n.test))
            # A WITHHOLDING DELEGATED TO A HELPER, which is how `_seed_price_interval` does it.
            # The grade must be visible in what the CALLER hands over: a helper that decides on its
            # own is a helper whose decision this scan cannot read, and that is debt, not a pass.
            elif isinstance(n, ast.Call):
                name = (n.func.id if isinstance(n.func, ast.Name)
                        else n.func.attr if isinstance(n.func, ast.Attribute) else None)
                body = self.funcs.get(name) if name else None
                returns_none = body is not None and any(
                    isinstance(inner, ast.Return) and (
                        (isinstance(inner.value, ast.Constant) and inner.value.value is None)
                        or (isinstance(inner.value, ast.IfExp) and any(
                            isinstance(b, ast.Constant) and b.value is None
                            for b in (inner.value.body, inner.value.orelse))))
                    for inner in ast.walk(body))
                if returns_none or body is None:
                    args: set[str] = set()
                    for arg in list(n.args) + [k.value for k in n.keywords]:
                        args |= _names(arg)
                    witnesses.append(args)

        self._reach(node, RESOLVE_DEPTH, frozenset(), note)
        return any(any(GRADE_VOCAB.search(name) for name in names) for names in witnesses)


class Site:
    """One published plan-grammar key, and what its site declares about its denominator."""

    def __init__(self, path, line, key, grade, why):
        self.path, self.line, self.key = path, line, key
        self.grade, self.why = grade, why

    def __repr__(self):
        return "{}:{} {} [{}] {}".format(self.path, self.line, self.key, self.grade, self.why)


def _enclosing(tree: ast.AST) -> dict[int, ast.AST]:
    """Map every node id to the function that holds it, so a site can read its own scope."""
    holder: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            for child in ast.walk(node):
                holder.setdefault(id(child), node)
    return holder


class Unparseable(Exception):
    """A file the scan could not read.

    RAISED AND NEVER SWALLOWED. A file that will not parse contributes no sites, so it can only
    make the debt look SMALLER -- which is the fail-quiet shape `test_a_domain_constant_carries_
    its_origin` was caught by and repaired. `census` collects these into a list the control
    asserts is empty rather than letting a returned `[]` read as "this file is clean".
    """


def census_file(path: pathlib.Path, source: str) -> list[Site]:
    """Every published plan-grammar count in one file, graded."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise Unparseable("{}: {}".format(path, exc)) from exc
    holder = _enclosing(tree)
    lines = source.splitlines()
    sites: list[Site] = []
    resolvers: dict[int, _Resolver] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = [k.value for k in node.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        for key, value in zip(node.keys, node.values):
            if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
                continue
            if not PLAN_GRAMMAR.search(key.value):
                continue
            if "at_the_point_estimate" in key.value:
                continue
            scope = holder.get(id(node), tree)
            resolver = resolvers.get(id(scope))
            if resolver is None:
                resolver = resolvers[id(scope)] = _Resolver(scope)
            divisors = resolver.divisors(value)
            if not divisors:
                continue
            if all(_is_chosen(d) for d in divisors):
                grade, why = "BOUNDED", "every denominator is a chosen number, not an estimate"
            elif any(WITHHOLDING.search(k) for k in keys):
                if resolver.withheld_on_a_grade(value):
                    grade, why = "GATED", (
                        "a sibling names the withholding and the value is withheld on a grade")
                else:
                    grade, why = "DEBT", (
                        "a sibling key names a withholding this site cannot perform: the count is "
                        "computed on every path, so the reason key sits reassuringly beside a "
                        "figure that is always published")
            else:
                # THE SITE'S OWN FUNCTION, not the whole file: a marker three functions away is
                # somebody else's claim about somebody else's denominator.
                lo = getattr(scope, "lineno", 1)
                hi = getattr(scope, "end_lineno", len(lines))
                text = "\n".join(lines[lo - 1:hi])
                if BOUNDED_MARKER.search(text):
                    grade, why = "BOUNDED", "the site declares its denominator bounded"
                else:
                    grade, why = "DEBT", (
                        "a measured denominator with no withholding sibling and no bounded "
                        "declaration -- this count has no upper bound where the denominator "
                        "approaches zero, and the key's grammar promises a reader it is a plan")
            sites.append(Site(str(path), key.lineno, key.value, grade, why))
    return sites


def census(roots=DEFAULT_ROOTS, base: pathlib.Path | None = None,
           unreadable: list | None = None) -> list[Site]:
    """Every published plan-grammar count under `roots`, graded. Sorted, so a diff is readable.

    `unreadable`, when passed, collects the files that would not parse. Callers that do not pass it
    get the exception, because silence here reads as a clean tree.
    """
    base = base or pathlib.Path(__file__).resolve().parent.parent
    sites: list[Site] = []
    for root in roots:
        for path in sorted((base / root).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            try:
                sites += census_file(path.relative_to(base), path.read_text(encoding="utf-8"))
            except Unparseable as exc:
                if unreadable is None:
                    raise
                unreadable.append(str(exc))
    return sorted(sites, key=lambda s: (s.path, s.line))


def debt(roots=DEFAULT_ROOTS, base: pathlib.Path | None = None) -> list[Site]:
    """The sites declaring nothing. This is the number that may only fall."""
    return [s for s in census(roots, base) if s.grade == "DEBT"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true", help="every graded site")
    parser.add_argument("--debt", action="store_true", help="only the undeclared sites")
    parser.add_argument("--roots", nargs="*", default=list(DEFAULT_ROOTS))
    args = parser.parse_args(argv)
    sites = census(tuple(args.roots))
    owed = [s for s in sites if s.grade == "DEBT"]
    if args.list or args.debt:
        for site in (owed if args.debt else sites):
            print("{}:{}  {}\n    [{}] {}".format(
                site.path, site.line, site.key, site.grade, site.why))
    counts = {g: sum(1 for s in sites if s.grade == g) for g in ("GATED", "BOUNDED", "DEBT")}
    print("{} published plan-grammar counts from a quotient: {} gated, {} bounded, {} DEBT".format(
        len(sites), counts["GATED"], counts["BOUNDED"], counts["DEBT"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
