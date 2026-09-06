#!/usr/bin/env python3
"""Which tests in a suite ASSERT ON the subject's own API, and which only exercise a caller.

THE QUESTION THIS ANSWERS, and why the obvious one is wrong. `tools/contract_battery.py` scores
`survived_all` over a population of CALLER suites, and the whole verdict turns on which files are
callers. The census at `b3938b313` reached for the obvious discriminator -- *does the suite import
the subject* -- and found it condemns correct specs: all four of `background/direction.py`'s caller
suites import it at module level, and three of them are the legitimate dedicated suite of a module
that CALLS it. That census's conclusion was that the real discriminator, *does the suite name a
contract of the subject*, "is not statically decidable".

**It is not decidable at FILE granularity, which is where the battery scores. It is decidable at
TEST granularity, by a stricter property than naming:** does this test call the subject's own API
and assert on what comes back. That is an AST fact, and it is what this module reports.

THREE CLASSES, because two of them would be the fail-open shape this sweep exists to find:

  ``subject``  every assert in the body touches the subject's API. A kill here is the subject
               grading itself; it says nothing about whether a caller is protected.
  ``caller``   no assert touches the subject's API. A kill here entered through the caller, which
               is the only kind of evidence ``survived_all`` was ever asking for.
  ``mixed``    both, in one body. `test_EXPIRED_direction_offers_NOTHING` asserts
               ``d.unreachable_focus(...) == []`` and ``dl.next_item(...) is None`` two lines
               apart. Deselecting it throws away real caller evidence; keeping it lets a subject
               assert be counted as a caller kill. **Neither is right, and a row whose only kill is
               a mixed test has no caller verdict at all** -- INDETERMINATE, and the caller of this
               module is expected to say so rather than pick the flattering side.

Helper calls are followed. A test whose body is one call to a module-level ``_assert_refused(d, x)``
is a subject test, and a census that only looked at the test body would file it as a caller and
hand back exactly the fabricated evidence this is here to prevent.

Usage:
    python3 -m tools.subject_asserting_tests background/direction.py tests/background/*.py
    python3 -m tools.subject_asserting_tests --spec direction        # every caller suite of a spec
    python3 -m tools.subject_asserting_tests --spec direction --json
"""
from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass, field
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


def module_name(subject: str) -> str:
    """`background/direction.py` -> `background.direction`."""
    return subject.removesuffix(".py").replace("/", ".")


def _aliases(tree: ast.Module, dotted: str) -> tuple[set[str], set[str]]:
    """Module-level names bound to the subject: (module aliases, names imported FROM it).

    Both matter and they read differently in the AST. `from background import direction as d`
    gives an attribute access `d.validate`; `from background.direction import validate` gives a
    bare `validate`. A census that only handled the first would report a suite full of bare-name
    assertions as pure caller.
    """
    package, _, leaf = dotted.rpartition(".")
    mods: set[str] = set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == dotted:
                    # `import background.direction` binds `background`; only the `as` form
                    # gives a usable single name.
                    if a.asname:
                        mods.add(a.asname)
        elif isinstance(node, ast.ImportFrom):
            if node.module == package and node.level == 0:
                for a in node.names:
                    if a.name == leaf:
                        mods.add(a.asname or a.name)
            elif node.module == dotted and node.level == 0:
                for a in node.names:
                    names.add(a.asname or a.name)
    return mods, names


def _touches(node: ast.AST, mods: set[str], names: set[str]) -> bool:
    """Does this subtree reference the subject's API at all."""
    for sub in ast.walk(node):
        if (isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name)
                and sub.value.id in mods):
            return True
        if isinstance(sub, ast.Name) and sub.id in names:
            return True
    return False


def _called_helpers(node: ast.AST) -> set[str]:
    """Bare-name calls in this body -- candidate module-level helpers to follow."""
    return {sub.func.id for sub in ast.walk(node)
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)}


def _functions(tree: ast.Module) -> dict[str, ast.AST]:
    """Every function in the file, keyed by its PYTEST NODE PATH rather than its bare name.

    `TestScan::test_normaliser_based_code_passes`, not `test_normaliser_based_code_passes`. The
    consumer of this census is `--deselect`, and pytest will not deselect a method by bare name --
    it silently deselects nothing and the run reports a full caller population it never had.
    Helpers keep their bare name so the reachability fixpoint can still resolve them.
    """
    out: dict[str, ast.AST] = {}

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                walk(child, f"{prefix}{child.name}::")
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out[f"{prefix}{child.name}" if child.name.startswith("test")
                    else child.name] = child
                walk(child, prefix)

    walk(tree, "")
    return out


def _is_test(qualified: str) -> bool:
    return qualified.rpartition("::")[2].startswith("test")


def _checks_in(fn: ast.AST) -> list[ast.AST]:
    """Assertions in this body. A `pytest.raises` block is one in every sense that matters here,
    and a suite that proves its refusals that way would otherwise census as caller-only."""
    return [s for s in ast.walk(fn)
            if isinstance(s, ast.Assert)
            or (isinstance(s, ast.With) and any(
                isinstance(i.context_expr, ast.Call) and "raises" in ast.dump(i.context_expr)
                for i in s.items))]


def _bound_targets(node: ast.AST) -> set[str]:
    return {t.id for t in ast.walk(node) if isinstance(t, ast.Name)}


def _tainted_locals(fn: ast.AST, mods: set[str], names: set[str],
                    reaches: dict[str, bool]) -> set[str]:
    """Locals holding a value that CAME FROM the subject.

    THE DEFECT THIS CLOSES, and it is the one that makes a purely syntactic census worse than
    useless. The commonest shape in this tree is

        problems = d.validate(record)
        assert any("target-shaped" in p for p in problems), problems

    -- and the `assert` line does not mention `d` at all. Four of the six kills in
    `direction`'s published caller table land on tests of exactly that shape, so a census that
    read asserts syntactically filed every one of them as CALLER EVIDENCE. That is the flattering
    answer and it is fabricated.

    Fixpoint rather than a single forward pass: `a = d.validate(x)` may follow the assert that
    reads it once a loop or a fixture is in the way, and a census that depends on statement order
    is a census that is right about the file it was written against.
    """
    # OUT-PARAMETERS, and the case that made this census disagree with a hand-built list and be
    # WRONG. `test_the_decision_log_is_APPEND_ONLY` does
    #
    #     d.append_decision({...}, path)
    #     assert len(path.read_text().splitlines()) == 2
    #
    # The assert names `path`, which was bound from `tmp_path` and never from the subject -- so a
    # taint pass that follows only RETURN values reads it as caller evidence and files the test as
    # MIXED. It is not mixed: nothing in it touches the module its file is named for. The subject
    # wrote through the argument, and an argument the subject was handed is a channel out of it
    # exactly as much as a return value is.
    #
    # Deliberately only bare NAMES passed positionally or by keyword -- the shape an out-parameter
    # has. Tainting every expression that appears near a subject call would pull in the shared
    # fixtures a genuine caller test also uses, and turn real caller evidence into the subject's.
    tainted: set[str] = {
        arg.id
        for call in ast.walk(fn)
        if isinstance(call, ast.Call) and _touches(call.func, mods, names)
        for arg in list(call.args) + [kw.value for kw in call.keywords]
        if isinstance(arg, ast.Name)
    }
    binders = [n for n in ast.walk(fn)
               if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.For,
                                 ast.comprehension, ast.withitem, ast.NamedExpr))]
    changed = True
    while changed:
        changed = False
        for node in binders:
            if isinstance(node, ast.Assign):
                value, targets = node.value, node.targets
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
                value, targets = node.value, [node.target]
            elif isinstance(node, ast.For):
                value, targets = node.iter, [node.target]
            elif isinstance(node, ast.comprehension):
                value, targets = node.iter, [node.target]
            else:  # withitem
                value, targets = node.context_expr, ([node.optional_vars]
                                                     if node.optional_vars else [])
            if value is None or not targets:
                continue
            from_subject = (
                _touches(value, mods, names)
                or any(n.id in tainted for n in ast.walk(value) if isinstance(n, ast.Name))
                or any(reaches.get(h) for h in _called_helpers(value))
            )
            if not from_subject:
                continue
            for target in targets:
                new = _bound_targets(target) - tainted
                if new:
                    tainted |= new
                    changed = True
    return tainted


@dataclass
class SuiteCensus:
    suite: str
    imports_subject: bool
    subject: list[str] = field(default_factory=list)
    mixed: list[str] = field(default_factory=list)
    caller: list[str] = field(default_factory=list)

    @property
    def not_caller_evidence(self) -> list[str]:
        """Node id suffixes whose kills are NOT evidence that a caller is protected."""
        return sorted(self.subject)

    def node_ids(self, which: list[str]) -> list[str]:
        return [f"{self.suite}::{n}" for n in sorted(which)]

    def as_dict(self) -> dict:
        return {
            "suite": self.suite,
            "imports_subject": self.imports_subject,
            "subject": sorted(self.subject),
            "mixed": sorted(self.mixed),
            "caller_only": len(self.caller),
            "verdict": self.verdict,
        }

    @property
    def verdict(self) -> str:
        if not self.imports_subject or not (self.subject or self.mixed):
            return "CALLER SUITE"
        if not self.caller and not self.mixed:
            return "THE SUBJECT'S OWN SUITE"
        return "MIXED FILE"


def census(subject: str, suite: str) -> SuiteCensus:
    """Classify every test function in `suite` against `subject`'s API."""
    dotted = module_name(subject)
    path = PROJECT / suite
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    mods, names = _aliases(tree, dotted)
    out = SuiteCensus(suite=suite, imports_subject=bool(mods or names))
    if not out.imports_subject:
        # No import path to the subject's API by name, so no body here can assert on it. Every
        # test is caller evidence; the class is still reported so "never imported it" and
        # "imported it and never asserted on it" do not read the same.
        out.caller = [n for n in _functions(tree) if _is_test(n)]
        return out

    functions = _functions(tree)
    # Which module-level helpers reach the subject, to a fixpoint. One pass would miss
    # `test -> _check -> _assert_on(d)`, and this sweep's whole subject is evidence that
    # travelled one hop further than the instrument looked.
    reaches = {name: _touches(fn, mods, names) for name, fn in functions.items()}
    changed = True
    while changed:
        changed = False
        for name, fn in functions.items():
            if reaches[name]:
                continue
            if any(reaches.get(h) for h in _called_helpers(fn) if h != name):
                reaches[name] = True
                changed = True

    # Which helpers CONTAIN an assertion, to a fixpoint. Separate from `reaches`, and both are
    # needed: `reaches` says a helper touches the subject, this says calling it is a CHECK at all.
    asserting = {name: bool(_checks_in(fn)) for name, fn in functions.items()}
    changed = True
    while changed:
        changed = False
        for name, fn in functions.items():
            if asserting[name]:
                continue
            if any(asserting.get(h) for h in _called_helpers(fn) if h != name):
                asserting[name] = True
                changed = True

    def _assert_touches(stmt: ast.AST, tainted: set[str]) -> bool:
        if _touches(stmt, mods, names):
            return True
        if any(n.id in tainted for n in ast.walk(stmt) if isinstance(n, ast.Name)):
            return True
        return any(reaches.get(h) for h in _called_helpers(stmt))

    for name, fn in functions.items():
        if not _is_test(name):
            continue
        tainted = _tainted_locals(fn, mods, names, reaches)
        checks: list[ast.AST] = list(_checks_in(fn))
        on_subject = [c for c in checks if _assert_touches(c, tainted)]
        # A CALL to an assert-bearing helper is itself a check, and until this was here a test
        # whose whole body was `_refuses(record)` had no `ast.Assert` anywhere in it, fell through
        # the "no assertion of any kind" branch and was filed as CALLER EVIDENCE. Found by the
        # control that made the helper branch reachable, not by reading the code.
        for call in (c for c in ast.walk(fn)
                     if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)):
            helper = call.func.id
            if helper == name or not asserting.get(helper):
                continue
            checks.append(call)
            if reaches.get(helper) or _assert_touches(call, tainted):
                on_subject.append(call)
        if not checks:
            # No assertion of any kind: it cannot be evidence about anything. Filed as caller
            # rather than subject, because the fail-open direction here is to credit the
            # subject's own tests with caller evidence.
            out.caller.append(name)
        elif len(on_subject) == len(checks):
            out.subject.append(name)
        elif on_subject:
            out.mixed.append(name)
        else:
            out.caller.append(name)
    return out


def _spec_suites(spec_name: str) -> tuple[str, tuple[str, ...]]:
    """(subject, caller suites) for a battery spec, read from the spec itself."""
    import importlib

    mod = importlib.import_module(f"tools.{spec_name}_contract_battery")
    return mod.SPEC.subject, mod.SPEC.suites


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("subject", nargs="?", help="e.g. background/direction.py")
    ap.add_argument("suites", nargs="*", help="test files to classify")
    ap.add_argument("--spec", help="battery spec slug; takes subject and suites from it")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.spec:
        subject, suites = _spec_suites(args.spec)
    else:
        if not args.subject or not args.suites:
            ap.error("give a subject and at least one suite, or --spec")
        subject, suites = args.subject, tuple(args.suites)

    reports = [census(subject, s) for s in suites]
    if args.json:
        print(json.dumps({"subject": subject,
                          "suites": [r.as_dict() for r in reports]}, indent=2))
        return 0

    print(f"SUBJECT {subject}\n")
    for r in reports:
        print(f"{r.suite}")
        print(f"  {r.verdict}  (imports subject: {r.imports_subject})")
        print(f"  subject-asserting: {len(r.subject)}   mixed: {len(r.mixed)}   "
              f"caller-only: {len(r.caller)}")
        for n in sorted(r.subject):
            print(f"    SUBJECT  {n}")
        for n in sorted(r.mixed):
            print(f"    MIXED    {n}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
