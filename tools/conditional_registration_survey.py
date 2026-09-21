"""Which `advance`-like calls can be reached with a key nobody registered?

THE CLASS, AND WHY IT IS A CLASS. `ChurnJourneyRegister.advance` reads `self._journeys[customer_id]`
with no `.get`, so reaching it unregistered raises `KeyError` and kills the caller. On 2026-09-19 a
value-arm pass died 880s in for exactly that reason: the registration at `run_phase2b.py` sat inside
`if old_decision_leg_rate is not None:` and the `advance` sat OUTSIDE it, so the pairing held only
while every account's decision leg opened on a product that struck a rate. An account opening on the
DEFAULT TARIFF never strikes one. That site was repaired at `3a8d15185`; the write-up said plainly
it fixed the pairing and not the class, and this module is the survey it owed.

THE DEFECT IS THE CALL SITE, NOT THE ACCESSOR. A raise-on-missing accessor is a legitimate design —
`policy_costs` says so in as many words, a hard failure on purpose. What is a defect is a caller
whose registration is reachable on strictly fewer paths than its use. So the unit here is a CALL
SITE and the test is a comparison of two guard chains within one function.

THREE BUCKETS, AND THE THIRD IS THE POINT. NARROWER is the defect. PAIRED is a site no enclosing
test can separate. UNSETTLED is a site whose registration is not visible in the enclosing function —
and it is reported as UNSETTLED rather than folded into PAIRED, because a survey that calls what it
cannot see safe is the fail-open shape. Most UNSETTLED sites are ordinary (register at account-open,
use in the loop); the count is a question list, never a defect count.

THE INSTRUMENT IS PROVEN ON THE ONE INSTANCE WE HAVE. `--prove` runs the walk against
`simulation/run_phase2b.py` as of `3a8d15185^` and against the same path at HEAD, and REFUSES unless
the pre-repair tree classifies NARROWER and the repaired tree does not. A survey that reports zero
because it cannot see the defect we know existed is void, not a result — and this repo has shipped
that shape before.

R12: diagnostic. No count here is a target. Driving NARROWER to zero by deleting a guard, or
UNSETTLED to zero by moving a registration somewhere the walk cannot see, makes the number better
and the world worse.
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import subprocess
import sys
from typing import Dict, List, Optional, Sequence, Tuple

#: Roots walked for both accessors and call sites. `tests/` is excluded on purpose: a test that
#: reaches an accessor unregistered is asserting the refusal, which is the opposite of the defect.
SURVEY_ROOTS = ("simulation", "company", "saas", "background", "tools")

#: A method whose name starts with one of these AND which stores into the register dict is taken as
#: the registering call. Matched against the stores found by AST, never on the name alone — the name
#: list only orders the report.
REGISTER_VERBS = ("register", "create", "open", "add", "enrol", "enroll", "record", "submit", "set")


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent


def _membership_guarded(sub: ast.Subscript, fn: ast.AST, book: str) -> bool:
    """Is this `self.<book>[k]` read already protected by a `k in self.<book>` test?

    `{self.symbols[n.id] for n in ... if n.id in self.symbols}` cannot raise, and neither can the
    same shape written as an enclosing `if`. Counting it as a raise-on-missing accessor is how the
    first run of this survey reported `_FunctionScan._keys` as the defect class twice. The test is
    textual on the guard, which is conservative in the safe direction: a guard naming the book keeps
    the accessor OUT of the catalogue only when it is the book being subscripted."""
    needle = f"in self.{book}"
    ancestors: Dict[int, ast.AST] = {}
    for parent in ast.walk(fn):
        for child in ast.iter_child_nodes(parent):
            ancestors[id(child)] = parent
    cur: Optional[ast.AST] = sub
    while cur is not None:
        if isinstance(cur, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for gen in cur.generators:
                for cond in gen.ifs:
                    if needle in ast.unparse(cond):
                        return True
        if isinstance(cur, (ast.If, ast.IfExp)) and needle in ast.unparse(cur.test):
            return True
        cur = ancestors.get(id(cur))
    return False


def _names_its_refusal(sub: ast.Subscript, fn: ast.AST) -> bool:
    """Does this raw read sit inside a `except KeyError: raise <something with a message>`?

    THE DIFFERENCE THIS MEASURES IS WHAT THE 2026-09-19 CRASH COST. `advance` raised bare
    `KeyError: 'SYN-2016-008'` 880s into a value-arm pass: the key, and nothing about which book
    refused or what should have registered it. `HomeRegistry.get_profile` raises
    `KeyError("No property registered for account {}")` from the identical shape, and the same
    failure would have been read off the traceback in seconds. CLAUDE.md asks for refusals that name
    their reason; on a raise-on-missing accessor that is not decoration, it is the whole diagnosis."""
    ancestors: Dict[int, ast.AST] = {}
    for parent in ast.walk(fn):
        for child in ast.iter_child_nodes(parent):
            ancestors[id(child)] = parent
    cur: Optional[ast.AST] = sub
    child: Optional[ast.AST] = None
    while cur is not None:
        if isinstance(cur, ast.Try) and child is not None and any(child is s for s in cur.body):
            for h in cur.handlers:
                names = ast.unparse(h.type) if h.type is not None else "BaseException"
                if "KeyError" not in names and h.type is not None:
                    continue
                for stmt in ast.walk(h):
                    if isinstance(stmt, ast.Raise) and stmt.exc is not None:
                        if isinstance(stmt.exc, ast.Call) and stmt.exc.args:
                            return True
        child = cur
        cur = ancestors.get(id(cur))
    return False


class _ClassScan:
    """Per-class: which `self.<dict>` are written by which methods, and read raw by which."""

    def __init__(self, cls: ast.ClassDef) -> None:
        self.name = cls.name
        self.stores: Dict[str, List[str]] = {}
        self.raw_loads: Dict[str, List[str]] = {}
        self.named_refusal: Dict[str, bool] = {}
        for fn in cls.body:
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for sub in ast.walk(fn):
                if not isinstance(sub, ast.Subscript):
                    continue
                tgt = sub.value
                if not (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name)
                        and tgt.value.id == "self"):
                    continue
                if isinstance(sub.ctx, ast.Store):
                    book = self.stores
                elif _membership_guarded(sub, fn, tgt.attr):
                    continue
                else:
                    book = self.raw_loads
                book.setdefault(tgt.attr, [])
                if fn.name not in book[tgt.attr]:
                    book[tgt.attr].append(fn.name)
                if book is self.raw_loads:
                    key = f"{tgt.attr}:{fn.name}"
                    self.named_refusal[key] = (
                        self.named_refusal.get(key, False) or _names_its_refusal(sub, fn))

    def pairs(self) -> List[Tuple[str, List[str], List[str]]]:
        """(dict name, registering methods, raise-on-missing accessor methods)."""
        out = []
        for d in sorted(set(self.stores) & set(self.raw_loads)):
            writers = sorted(self.stores[d])
            readers = sorted(set(self.raw_loads[d]) - set(writers))
            if readers:
                out.append((d, writers, readers))
        return out


def accessor_catalogue(root: pathlib.Path) -> Dict[str, Dict[str, object]]:
    """register CLASS name -> {owners, registrars, accessors}.

    Keyed by class and not by method name. The first draft keyed on the method name alone, because a
    call site `x.advance(...)` gives the attribute and not the receiver's type -- and it returned
    11,330 "call sites" and 11,324 UNSETTLED, because `get`, `add` and `record` are accessor names on
    these books AND on several thousand unrelated objects. That is not a fail-closed "we cannot
    tell"; it is a question asked so loosely the answer carries no information. Receivers are bound
    to types instead, by `_bindings_in`."""
    cat: Dict[str, Dict[str, object]] = {}
    for rel in SURVEY_ROOTS:
        for path in sorted((root / rel).rglob("*.py")):
            if "test" in path.name:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                continue
            for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
                scan = _ClassScan(cls)
                pairs = scan.pairs()
                if not pairs:
                    continue
                row = cat.setdefault(cls.name, {
                    "owners": [], "registrars": [], "accessors": [],
                    "file": str(path.relative_to(root)),
                })
                for book, writers, readers in pairs:
                    for r in readers:
                        row.setdefault("refusals", {})[f"{cls.name}.{r}"] = (
                            "NAMED" if scan.named_refusal.get(f"{book}:{r}") else "BARE")
                    owner = f"{path.relative_to(root)}::{cls.name}.{book}"
                    if owner not in row["owners"]:
                        row["owners"].append(owner)
                    for w in writers:
                        if w not in row["registrars"]:
                            row["registrars"].append(w)
                    for r in readers:
                        if r not in row["accessors"]:
                            row["accessors"].append(r)
    for row in cat.values():
        row["registrars"] = sorted(row["registrars"])  # type: ignore[index]
        row["accessors"] = sorted(row["accessors"])  # type: ignore[index]
    return cat


def _bindings_in(tree: ast.AST, cat: Dict[str, Dict[str, object]]) -> Dict[str, str]:
    """receiver expression -> register class name, from local evidence only.

    Three kinds of evidence, and nothing weaker: a construction (`_reg = ChurnJourneyRegister(...)`,
    `self._book = PSRBook()`), an annotation (`def f(reg: DSRBook)`), and `self` inside the register
    class itself. A receiver with none of them is UNBOUND and its call sites are not counted at all
    -- they are not evidence of safety and they are not evidence of a defect, and the result says so
    rather than burying them in UNSETTLED."""
    bindings: Dict[str, str] = {}

    def note(target: ast.AST, value: ast.AST) -> None:
        if not (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)):
            return
        if value.func.id not in cat:
            return
        try:
            bindings[ast.unparse(target)] = value.func.id
        except Exception:
            pass

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                note(t, node.value)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            note(node.target, node.value)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in list(node.args.args) + list(node.args.kwonlyargs):
                if arg.annotation is None:
                    continue
                ann = arg.annotation
                name = ann.id if isinstance(ann, ast.Name) else None
                if name is None and isinstance(ann, ast.Constant) and isinstance(ann.value, str):
                    name = ann.value
                if name in cat:
                    bindings[arg.arg] = name
    return bindings


def _guard_chain(node: ast.AST, ancestors: Dict[int, ast.AST], stop: ast.AST) -> List[str]:
    """The `if` tests enclosing `node` up to (not including) `stop`, innermost last.

    An `else` branch is recorded as `not (<test>)` so that the two arms of one `if` are never read
    as the same chain -- without that, a registration in the `if` and a use in the `else` would
    compare equal and be called PAIRED, which is the exact fail-open reading this walk exists to
    avoid."""
    chain: List[str] = []
    cur: Optional[ast.AST] = node
    child: Optional[ast.AST] = None
    while cur is not None and cur is not stop:
        if isinstance(cur, ast.If) and child is not None:
            test = ast.unparse(cur.test)
            in_else = any(child is s for s in cur.orelse)
            chain.append(f"not ({test})" if in_else else test)
        child = cur
        cur = ancestors.get(id(cur))
    chain.reverse()
    return chain


def _is_idempotence_guard(test: str, receiver: str) -> bool:
    """Is this guard the `register only if absent` idiom, on THIS receiver?

    `if _reg.get_journey(acct) is None: _reg.register_customer(acct)` is the repair shape, and a
    naive chain comparison calls it a narrowing guard -- which the P4 proof caught on this module's
    own first draft, reporting the REPAIRED site as the defect. It cannot narrow: it is true exactly
    on the paths where the use would otherwise raise, so registration-under-it is reachable wherever
    the use is. Excluded from the comparison, and only on the accessor's own receiver -- a lookup
    against some OTHER book says nothing about this one and is a real guard."""
    stripped = test.strip()
    if stripped.startswith(f"{receiver}.") and stripped.endswith(" is None"):
        return "(" in stripped
    if f" not in {receiver}" in stripped:
        return True
    return False


def _receiver(call: ast.Call) -> Optional[str]:
    """`_reg.advance(...)` -> `_reg`; `self.x.advance(...)` -> `self.x`. None for anything else."""
    fn = call.func
    if not isinstance(fn, ast.Attribute):
        return None
    try:
        return ast.unparse(fn.value)
    except Exception:
        return None


def _enclosing_functions(tree: ast.AST) -> Tuple[Dict[int, ast.AST], List[ast.AST]]:
    ancestors: Dict[int, ast.AST] = {}
    funcs: List[ast.AST] = []
    for parent in ast.walk(tree):
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            funcs.append(parent)
        for child in ast.iter_child_nodes(parent):
            ancestors[id(child)] = parent
    return ancestors, funcs


def _owning_class(node: ast.AST, ancestors: Dict[int, ast.AST]) -> Optional[str]:
    cur = ancestors.get(id(node))
    while cur is not None:
        if isinstance(cur, ast.ClassDef):
            return cur.name
        cur = ancestors.get(id(cur))
    return None


def _owning_function(node: ast.AST, ancestors: Dict[int, ast.AST]) -> ast.AST:
    cur = ancestors.get(id(node))
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            return cur
        cur = ancestors.get(id(cur))
    raise AssertionError("every node is inside a Module")


def survey_file(path: pathlib.Path, rel: str, cat: Dict[str, Dict[str, object]],
                unbound: Optional[List[dict]] = None) -> List[dict]:
    if unbound is None:
        unbound = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    ancestors, _ = _enclosing_functions(tree)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    bindings = _bindings_in(tree, cat)

    def bound_class(recv: str, node: ast.AST) -> Optional[str]:
        if recv == "self":
            owning = _owning_class(node, ancestors)
            return owning if owning in cat else None
        return bindings.get(recv)

    rows: List[dict] = []
    for call in calls:
        fn = call.func
        if not isinstance(fn, ast.Attribute):
            continue
        recv = _receiver(call)
        if recv is None:
            continue
        cls_name = bound_class(recv, call)
        if cls_name is None:
            # THE BLIND SPOT, COUNTED RATHER THAN DROPPED. A receiver this walk cannot type, whose
            # attribute is nonetheless an accessor name on some register class. Most are unrelated
            # objects that share a common method name; some may be a register arriving as an
            # untyped parameter. The survey cannot tell which, and a survey that silently discards
            # its own uncovered set reads as "covered everything".
            if any(fn.attr in row["accessors"] for row in cat.values()):
                unbound.append({"file": rel, "line": call.lineno,
                                "receiver": recv, "accessor": fn.attr})
            continue
        if fn.attr not in cat[cls_name]["accessors"]:
            continue
        owner = _owning_function(call, ancestors)
        use_chain = _guard_chain(call, ancestors, owner)

        registrars = cat[cls_name]["registrars"]
        reg_chains: List[List[str]] = []
        for other in calls:
            ofn = other.func
            if not isinstance(ofn, ast.Attribute) or ofn.attr not in registrars:
                continue
            if _receiver(other) != recv:
                continue
            if _owning_function(other, ancestors) is not owner:
                continue
            if other.lineno >= call.lineno:
                # A registration BELOW the use cannot make it safe on this pass through the
                # function. It is the look-first idiom -- `for x in self._changes_for(...)` and only
                # then `_open_change` for what the look did not find -- which the first run of this
                # survey reported as the defect at both `observe_move_*` sites. Dropping it here
                # leaves those sites UNSETTLED rather than clean, which is the honest verdict: the
                # key set they read comes from a companion index this walk cannot follow.
                continue
            raw = _guard_chain(other, ancestors, owner)
            reg_chains.append([g for g in raw if not _is_idempotence_guard(g, recv)])

        if not reg_chains:
            verdict, why = "UNSETTLED", "no registration on this receiver in the enclosing function"
        elif any(set(rc) <= set(use_chain) for rc in reg_chains):
            verdict, why = "PAIRED", "a registration sits at or above the use's guard depth"
        else:
            verdict = "NARROWER"
            extra = sorted(set(min(reg_chains, key=len)) - set(use_chain))
            why = "every registration is gated by " + " and ".join(extra) + " and the use is not"

        rows.append({
            "file": rel,
            "line": call.lineno,
            "accessor": fn.attr,
            "receiver": recv,
            "function": getattr(owner, "name", "<module>"),
            "verdict": verdict,
            "why": why,
            "use_guards": use_chain,
            "registration_guards": reg_chains,
            "register_class": cls_name,
            "accessor_defined_in": cat[cls_name]["owners"],
        })
    return rows


def run_survey(root: pathlib.Path, only: Optional[Sequence[str]] = None) -> dict:
    cat = accessor_catalogue(root)
    rows: List[dict] = []
    if only:
        targets = [(root / p, p) for p in only]
    else:
        targets = []
        for r in SURVEY_ROOTS:
            for p in sorted((root / r).rglob("*.py")):
                if "test" not in p.name:
                    targets.append((p, str(p.relative_to(root))))
    unbound: List[dict] = []
    for path, rel in targets:
        if path.exists():
            rows.extend(survey_file(path, rel, cat, unbound))

    counts = {v: sum(1 for r in rows if r["verdict"] == v)
              for v in ("NARROWER", "PAIRED", "UNSETTLED")}
    return {
        "register_classes_in_catalogue": len(cat),
        "register_shaped_owners": sorted({c for row in cat.values() for c in row["owners"]}),
        "call_sites": len(rows),
        "refusals": {k: v for row in cat.values() for k, v in row.get("refusals", {}).items()},
        "unbound_receiver_sites": len(unbound),
        "unbound_receivers": unbound,
        "counts": counts,
        "narrower": [r for r in rows if r["verdict"] == "NARROWER"],
        "rows": rows,
    }


def prove_on_the_known_instance(root: pathlib.Path) -> dict:
    """P4: the walk must call the PRE-repair `run_phase2b` advance NARROWER and the repaired one not.

    The pre-repair text is read from git rather than reconstructed, and the catalogue is taken from
    the live tree: `ChurnJourneyRegister.advance` is unchanged by `3a8d15185`, so the only thing
    that differs between the two runs is the call site's own guard chain -- which is the one
    variable this proof is about."""
    subject = "simulation/run_phase2b.py"
    before = subprocess.run(
        ["git", "show", f"3a8d15185^:{subject}"], cwd=root, capture_output=True, text=True,
    )
    if before.returncode != 0:
        return {"proven": False, "reason": f"git show refused: {before.stderr.strip()[:200]}"}

    scratch = pathlib.Path(subprocess.run(
        ["mktemp", "-d"], capture_output=True, text=True, check=True).stdout.strip())
    pre_path = scratch / "run_phase2b_pre.py"
    pre_path.write_text(before.stdout, encoding="utf-8")

    cat = accessor_catalogue(root)
    pre_rows = [r for r in survey_file(pre_path, subject + "@3a8d15185^", cat)
                if r["accessor"] == "advance"]
    now_rows = [r for r in survey_file(root / subject, subject, cat)
                if r["accessor"] == "advance"]

    pre_bad = [r for r in pre_rows if r["verdict"] == "NARROWER"]
    now_bad = [r for r in now_rows if r["verdict"] == "NARROWER"]
    proven = bool(pre_bad) and not now_bad
    return {
        "proven": proven,
        "pre_repair_narrower": len(pre_bad),
        "post_repair_narrower": len(now_bad),
        "pre_repair_rows": pre_rows,
        "post_repair_rows": now_rows,
        "reason": (
            "the walk separates the pre-repair tree from the repaired one"
            if proven else
            "the walk does NOT separate the two trees; the survey is VOID, not zero"
        ),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prove", action="store_true",
                    help="run P4 only: does the walk fire on the one instance we have?")
    ap.add_argument("--only", nargs="*", default=None, help="restrict to these repo-relative paths")
    ap.add_argument("--out", default=None, help="write the full result as JSON here")
    args = ap.parse_args(argv)

    root = _repo_root()

    if args.prove:
        proof = prove_on_the_known_instance(root)
        print(json.dumps(proof, indent=2))
        return 0 if proof["proven"] else 1

    proof = prove_on_the_known_instance(root)
    result = run_survey(root, only=args.only)
    result["proof"] = proof

    print(f"register classes       : {result['register_classes_in_catalogue']}")
    print(f"call sites (non-test)  : {result['call_sites']}")
    for v in ("NARROWER", "PAIRED", "UNSETTLED"):
        print(f"  {v:<10} {result['counts'][v]}")
    print(f"  {'UNBOUND':<10} {result['unbound_receiver_sites']}  (receiver not typeable; NOT a verdict)")
    bare = sorted(k for k, v in result["refusals"].items() if v == "BARE")
    print(f"accessors raising a BARE KeyError: {len(bare)} of {len(result['refusals'])}")
    print(f"instrument proven      : {proof['proven']} -- {proof['reason']}")
    if result["narrower"]:
        print("\nNARROWER -- the defect class:")
        for r in result["narrower"]:
            print(f"  {r['file']}:{r['line']} {r['receiver']}.{r['accessor']}() in {r['function']}")
            print(f"      {r['why']}")

    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
