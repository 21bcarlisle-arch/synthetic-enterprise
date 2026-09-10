#!/usr/bin/env python3
"""Which tests have a WHOLE-DIRECTORY subject and only a FILENAME-STEM selector?

THE DEFECT THIS MEASURES. `tools/pre_commit_test_gate.py` selects tests two ways: a fixed
`CONTROL_TESTS` list that runs whenever any code file is staged, and otherwise by FILENAME STEM --
a staged `background/X.py` selects `tests/**/test_X.py` and `tests/**/test_X_*.py`. When a test's
subject is *every file in a package*, those two sets never intersect: the commit that breaks the
control is a NEW module, and a new module's stem names no existing test. Subject set = a directory;
selector set = one stem, sometimes the test file itself and nothing else.

That is R15's FAIL-SILENT killer at the SELECTION layer rather than inside an assertion. The
assertions are not wrong and fire correctly the instant anything runs them -- nothing runs them.
Measured cost of two instances: `test_live_ledger_guard.py` drifted 74 -> 86 unguarded writers over
FOURTEEN DAYS, and `test_seat_guard_daemons.py` drifted to nine unguarded entrypoints over nine,
both green at every commit throughout.

WHY THIS FILE EXISTS AT ALL, given the class has been fixed ten times. Each fix added one line to
`CONTROL_TESTS` with a paragraph of rationale, and the count of REMAINING instances was asserted
from a hand pass three times ("nine") before an AST census said 117 for its sibling class. The 27
figure this project currently cites for THIS class came from an uncommitted throwaway script, so it
could not be re-run, disputed, or watched for growth. A number nobody can reproduce is a number that
rots silently -- which is the same shape as the defect being measured.

THE PREDICATE IS THE PRE-REGISTERED ONE, copied here unnarrowed on purpose
(`docs/staging/records/PREREG_HOW_MANY_WHOLE_TREE_RATCHETS_CAN_THE_STEM_SELECTOR_NEVER_REACH_2026-09-10.md`,
fixed BEFORE the first count was run). A test file is an UNREACHABLE WHOLE-TREE RATCHET when:

  1. it globs or walks a NON-`tests/` source directory to build its population -- an AST-visible
     `glob`/`rglob`/`iterdir`/`os.walk`, in a module that names a source root as a literal;
  2. it compares a length or count derived from that population against an INTEGER LITERAL (the
     ratchet bound);
  3. it is absent from `CONTROL_TESTS`.

Leg 3 is the selection defect. Legs 1-2 are what make the defect SILENT rather than merely narrow:
a bound compared to a literal is a claim about a population that grows behind it.

IT OVER-COUNTS, AND THAT IS THE SAFE DIRECTION. Legs 1 and 2 are proximity-in-a-module, not
dataflow: a file that globs `company/` for one reason and asserts `== 3` about something else
counts. Some members also have a legitimate non-stem route (the site lane runs `pytest site/`
separately). The predicate has DELIBERATELY NOT been narrowed after seeing the answer -- a narrowing
added to fix a false positive is asymmetric, and only the false positives ever get a comment.
`--strict-dataflow` prints the subset where the globbed root and the asserted count are provably the
same expression, so the over-count is BOUNDED by measurement rather than by apology.

## THE LOOSE POOL IS DELIBERATELY UNGUARDED BY A REFUSAL. Decision, 2026-09-10, with its price.

`test_the_strict_census_stays_discharged` refuses a new STRICT member at the commit that writes it.
The ~91 LOOSE members have no such refusal, and this is the decision rather than the omission it
would otherwise read as. Read this before proposing a control over them; the argument is measured,
not assumed, and `PREREG_HOW_MANY_LOOSE_CENSUS_MEMBERS_ARE_STRICT_IN_SUBSTANCE_AND_MISSED_BY_THE_
ONE_HOP_RULE_2026-09-10.md` fixed the numbers below before they were visible.

**Promotion-on-change needs no new predicate, and that half of the question is closed.** The strict
control re-runs `census()` over every tracked test file, not over a frozen list. A member that is
loose today and is EDITED into strict form is in the strict pool at that commit, and the control --
itself on `CONTROL_TESTS`, so it runs whenever any code file is staged -- refuses it there. Driven
through `unreachable()` by `test_editing_a_loose_member_into_strict_form_puts_it_back_in_the_
refused_pool`, not argued.

**What was NOT measured until now is the other error direction, and it turned out to be empty.**
Every previous discussion of this boundary reasons about the over-count alone. But `_strict_dataflow`
is a ONE-HOP rule, and a two-hop `rows = DIR.glob(...)` / `names = {p.name for p in rows}` /
`len(names) <= N` is strict in substance while scoring loose -- an UNDER-count, and the dangerous
direction, because "deliberately unguarded" would be covering it. `_transitive_dataflow` is the
fixpoint version and it promotes **ZERO** loose members on this tree. Predicted 14, band 6-30;
measured 0. The shape is nearly absent here, so the over-count really is the only error direction
of any size, and the decision stands on a number instead of an assertion.

**STRICT IS NOT A SUBSET OF TRANSITIVE, and the reason is a defect in the instrument.**
`_strict_dataflow` is scope-BLIND: it merges every binding of a name across the whole module, so a
`rows` walked in one test function taints a `rows` counted in another. Two of the eighteen members
of the always-run batch were earned that way -- `test_the_responder_refuses_to_guess_whose_a_message
_is.py` (walk in `_run`, bound in five test functions) and `test_policy_field_consumption.py` (walk
at line 467, bound at line 339, different functions, the bound textually FIRST).

**And it is recorded here rather than repaired, deliberately.** Narrowing `strict_dataflow` to be
scope-aware would make `test_every_member_still_earns_its_place_by_scanning_a_whole_directory` red
and demand those two lines be DELETED from the always-run list -- on a rule with a known blind spot
in the opposite direction. `_run` returns its walked population and the test functions count what it
returned, so the first of the two is a true member of the class reached through a helper's return
value, which neither rule can see. Deleting it would be a narrowing that only ever heard the
false-positive side. The residual is named in the docstring of `_walk_tainted_names` and stays
named.
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The trees a test can take as a whole-directory subject. `tests` is excluded by leg 1: a test
# whose subject is other tests is reached by staging those tests, which the stem selector does
# handle (a changed test file selects itself).
SOURCE_ROOTS = (
    "background", "company", "saas", "sim", "simulation",
    "tools", "interface", "site", "docs", ".claude", "hooks",
)

_WALK_ATTRS = frozenset({"glob", "rglob", "iterdir"})


def control_tests() -> set[str]:
    """`CONTROL_TESTS` as the gate itself defines it -- imported, never re-typed.

    Re-typing the list here would make this census silently disagree with the gate the moment one
    of them changed, and the disagreement would favour whichever file was edited last. The import
    is the only way the two populations cannot drift apart.
    """
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.pre_commit_test_gate import CONTROL_TESTS

    return set(CONTROL_TESTS)


def _string_constants(tree: ast.AST) -> set[str]:
    return {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def _named_roots(tree: ast.AST) -> set[str]:
    """Source roots this module names as a literal, by first path segment.

    Both spellings the repo actually uses are asked: a bare segment (`ROOT / "background"`) and a
    path-ish literal (`"docs/observability"`, `"background/*.py"`). Asking only the first was how
    an earlier scope regex missed 67 members of its own class -- it matched the concept word and was
    blind to the same concept spelled another way.
    """
    found: set[str] = set()
    for s in _string_constants(tree):
        if not s or s.startswith(("http", "test")):
            continue
        head = s.strip("/").split("/")[0].split("*")[0]
        if head in SOURCE_ROOTS:
            found.add(head)
    return found


def _walks_a_tree(tree: ast.AST) -> bool:
    """Leg 1: an AST-visible directory walk anywhere in the module."""
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Attribute) and f.attr in _WALK_ATTRS:
            return True
        if isinstance(f, ast.Attribute) and f.attr == "walk":
            # os.walk / Path.walk -- both are a whole-tree read
            return True
    return False


def _count_bound_nodes(tree: ast.AST) -> list[ast.Compare]:
    """Leg 2: comparisons of a length/count against an integer literal.

    `len(x) <= 56`, `count == 3`, `assert len(rows) > 0`. The count side is recognised by a `len()`
    call or an identifier whose name carries `count`/`total`/`n_`, which is the repo's own naming.
    """
    out: list[ast.Compare] = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Compare):
            continue
        if not any(isinstance(c, ast.Constant) and isinstance(c.value, int)
                   and not isinstance(c.value, bool) for c in n.comparators):
            continue
        left = n.left
        counts = False
        if isinstance(left, ast.Call) and isinstance(left.func, ast.Name) and left.func.id == "len":
            counts = True
        elif isinstance(left, ast.Name) and any(
            k in left.id.lower() for k in ("count", "total", "n_", "_n", "size", "bound")
        ):
            counts = True
        elif isinstance(left, ast.Attribute) and any(
            k in left.attr.lower() for k in ("count", "total", "size", "bound")
        ):
            counts = True
        if counts:
            out.append(n)
    return out


def _strict_dataflow(tree: ast.AST) -> bool:
    """The BOUNDED over-count: is the walked population provably the counted one?

    True only when a `len(...)`-vs-integer comparison takes, as its argument, a name that is
    assigned from a walk call, or takes the walk call directly. This is the subset where legs 1 and
    2 are the same expression rather than two facts about one file. It is reported ALONGSIDE the
    headline rather than replacing it, so the over-count has a measured size instead of a caveat.
    """
    walked: set[str] = set()
    for n in ast.walk(tree):
        if not isinstance(n, (ast.Assign, ast.AnnAssign)):
            continue
        value = n.value
        if value is None:
            continue
        has_walk = any(
            isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
            and c.func.attr in (_WALK_ATTRS | {"walk"})
            for c in ast.walk(value)
        )
        if not has_walk:
            continue
        targets = n.targets if isinstance(n, ast.Assign) else [n.target]
        for t in targets:
            if isinstance(t, ast.Name):
                walked.add(t.id)
    for cmp_node in _count_bound_nodes(tree):
        left = cmp_node.left
        if not (isinstance(left, ast.Call) and isinstance(left.func, ast.Name)
                and left.func.id == "len" and left.args):
            continue
        arg = left.args[0]
        if isinstance(arg, ast.Name) and arg.id in walked:
            return True
        if any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
               and c.func.attr in (_WALK_ATTRS | {"walk"}) for c in ast.walk(arg)):
            return True
    return False


def _derives_from_walk(value: ast.AST, tainted: set[str]) -> bool:
    """Does this expression contain a walk call, or a name already known to derive from one?"""
    for c in ast.walk(value):
        if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                and c.func.attr in (_WALK_ATTRS | {"walk"})):
            return True
        if isinstance(c, ast.Name) and c.id in tainted:
            return True
    return False


_SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def _scope_index(tree: ast.AST) -> tuple[dict[int, ast.AST | None], dict[int, ast.AST | None]]:
    """`id(node) -> its enclosing scope` and `id(scope) -> its parent scope`. `None` is the module.

    SCOPE IS NOT A REFINEMENT HERE, IT IS CORRECTNESS. Two test functions in one file routinely
    both bind `rows`, `before`, `after`; merging them makes one function's walk taint another
    function's unrelated bound. That is not a conservative over-approximation of Python, it is a
    misreading of it, and it produced this predicate's only live hit on the first run.
    """
    owner: dict[int, ast.AST | None] = {id(tree): None}
    parent: dict[int, ast.AST | None] = {}

    def visit(node: ast.AST, scope: ast.AST | None) -> None:
        for child in ast.iter_child_nodes(node):
            owner[id(child)] = scope
            if isinstance(child, _SCOPE_NODES):
                parent[id(child)] = scope
                visit(child, child)
            else:
                visit(child, scope)

    visit(tree, None)
    return owner, parent


def _walk_tainted_names(tree: ast.AST) -> dict[int, set[str]]:
    """Per-scope fixpoint: for each scope, every name there whose value derives from a walk.

    Flow-INsensitive within a scope and deliberately so -- the question is "could this population
    have come from the directory", not "does it on this path". A scope inherits its ancestors'
    bindings, because a module-level `DIR = ROOT / "background"` really is visible inside every
    function below it.

    `for` targets are excluded: they bind one item, not a population, and admitting them would only
    pretend to cover the accumulate-through-`append` shape this genuinely cannot see.
    """
    owner, parent = _scope_index(tree)
    per_scope: dict[int, list[tuple[list[str], ast.AST]]] = {}
    scopes: dict[int, ast.AST | None] = {0: None}  # key 0 is the module; else id(scope node)

    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            targets, value = n.targets, n.value
        elif isinstance(n, ast.AnnAssign) and n.value is not None:
            targets, value = [n.target], n.value
        else:
            continue
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        if not names:
            continue
        s = owner.get(id(n))
        key = 0 if s is None else id(s)
        scopes.setdefault(key, s)
        per_scope.setdefault(key, []).append((names, value))

    # Every scope that owns a comparison also needs an answer, even with no assignments of its own.
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare):
            s = owner.get(id(n))
            scopes.setdefault(0 if s is None else id(s), s)

    def visible(key: int) -> list[tuple[list[str], ast.AST]]:
        out: list[tuple[list[str], ast.AST]] = []
        s = scopes.get(key)
        while True:
            out.extend(per_scope.get(0 if s is None else id(s), ()))
            if s is None:
                return out
            s = parent.get(id(s))

    result: dict[int, set[str]] = {}
    for key in scopes:
        assigns = visible(key)
        tainted: set[str] = set()
        changed = True
        while changed:
            changed = False
            for names, value in assigns:
                if all(nm in tainted for nm in names):
                    continue
                if _derives_from_walk(value, tainted):
                    tainted.update(names)
                    changed = True
        result[key] = tainted
    return result


def _transitive_dataflow(tree: ast.AST) -> bool:
    """`_strict_dataflow` with the hop limit removed. STRICT IS ITS DEPTH-1 CASE.

    WHY THIS EXISTS, and it is not the reason the strict subset exists. `strict_dataflow` bounds the
    predicate's OVER-count: it is the subset where legs 1 and 2 are provably one expression, so the
    loose pool's false positives have a measured size. Every discussion of the boundary so far --
    the census docstring, the drawn item, `test_the_strict_census_stays_discharged` -- reasons about
    that direction alone.

    The other direction was never measured. One hop is `rows = DIR.glob(...)` then `len(rows) <= N`.
    Two hops is what this repo actually writes:

        rows  = [p for p in DIR.glob("*.py") if _is_writer(p)]
        names = {p.name for p in rows}
        assert len(names) <= 56

    That file is strict in substance -- the walked population IS the counted one and the bound IS a
    claim about a directory that grows behind it -- and the one-hop rule scores it loose. So the
    strict pool UNDER-counts, and "the loose pool is deliberately unguarded" was covering members
    that belong on the guarded side.

    It is reported, never enforced, and `strict_dataflow` is untouched: a predicate that decides an
    always-run cost has to be argued and priced, not swapped in under the same name.
    """
    by_scope = _walk_tainted_names(tree)
    owner, _ = _scope_index(tree)
    for cmp_node in _count_bound_nodes(tree):
        left = cmp_node.left
        if not (isinstance(left, ast.Call) and isinstance(left.func, ast.Name)
                and left.func.id == "len" and left.args):
            continue
        s = owner.get(id(cmp_node))
        tainted = by_scope.get(0 if s is None else id(s), set())
        if _derives_from_walk(left.args[0], tainted):
            return True
    return False


def tracked_test_files() -> list[str]:
    """Committed test files, from the INDEX rather than a working-tree walk.

    A census that walks the working tree answers about whatever three other lanes have on disk
    right now; the subject here is the repository. `git ls-files` is the same choice the gate's own
    `_py_files_naming` makes and for the same reason.
    """
    r = subprocess.run(
        ["git", "ls-files", "--", "tests/*.py", "site/*.py"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git ls-files rc={r.returncode}: {r.stderr.strip()[-200:]}")
    return [ln.strip() for ln in r.stdout.splitlines()
            if ln.strip() and Path(ln.strip()).name.startswith("test_")]


def classify_source(text: str) -> dict | None:
    """Legs 1 and 2 against ONE module's source. `None` = not a whole-directory-subject test.

    The unit is source text rather than a path so the predicate can be driven by planted modules
    in a test. A census whose only input is the live tree can only ever be asserted against today's
    answer, and a control keyed to today's answer goes red when the code becomes more honest.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    if not _walks_a_tree(tree):
        return None
    roots = _named_roots(tree)
    if not roots:
        return None
    if not _count_bound_nodes(tree):
        return None
    return {
        "subject_roots": sorted(roots),
        "strict_dataflow": _strict_dataflow(tree),
        "transitive_dataflow": _transitive_dataflow(tree),
    }


def census() -> list[dict]:
    """Every test file meeting legs 1 and 2, with leg 3 and the strict subset recorded per row."""
    on_list = control_tests()
    rows: list[dict] = []
    for rel in tracked_test_files():
        p = ROOT / rel
        if not p.is_file():
            continue  # in the index, not on disk -- another lane mid-write
        hit = classify_source(p.read_text(encoding="utf-8", errors="replace"))
        if hit is None:
            continue
        rows.append({"test": rel, "on_control_tests": rel in on_list, **hit})
    return sorted(rows, key=lambda r: r["test"])


def unreachable(rows: list[dict]) -> list[dict]:
    """The census proper: legs 1, 2 AND 3 -- the ones no directory change can select."""
    return [r for r in rows if not r["on_control_tests"]]


def _commit_files(sha: str) -> list[str]:
    r = subprocess.run(
        ["git", "show", "--name-only", "--pretty=format:", "--diff-filter=ACM", sha],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def widening_cost(sample: int = 40, *, strict_only: bool = False) -> dict:
    """What would selecting-by-SUBJECT actually add, on the commits this repo really makes?

    THE WHOLE ARGUMENT AGAINST CHANGING THE SELECTOR IS A COST NOBODY HAD LOOKED AT. The standing
    budget finding is live -- two test files already spend 393s of a 600s hook budget -- so
    "widen selection" is only a proposal once the widening has a number. This is that number, over
    real commits rather than a constructed worst case.

    The widened rule modelled here is the honest reading of "select a test by what it SCANS": a
    staged path under root R selects every censused test that names R as a subject. It is
    deliberately the CRUDE version, because that is what deriving the subject from the source can
    actually support -- see the result document for why the crude version is the one that matters.
    """
    rows = census()
    pool = [r for r in rows if not r["on_control_tests"]]
    if strict_only:
        pool = [r for r in pool if r["strict_dataflow"]]

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.pre_commit_test_gate import select_targets

    log = subprocess.run(
        ["git", "log", f"-{sample}", "--format=%H", "--no-merges"],
        cwd=str(ROOT), capture_output=True, text=True,
    ).stdout.split()

    per_commit = []
    for sha in log:
        files = _commit_files(sha)
        if not files:
            continue
        today = set(select_targets(files))
        staged_roots = {f.split("/")[0] for f in files}
        widened = {r["test"] for r in pool if staged_roots & set(r["subject_roots"])}
        per_commit.append({
            "sha": sha[:9],
            "files_changed": len(files),
            "today": len(today),
            "added": len(widened - today),
        })
    if not per_commit:
        return {"sample": 0}
    added = sorted(c["added"] for c in per_commit)
    today = sorted(c["today"] for c in per_commit)
    return {
        "sample": len(per_commit),
        "pool": len(pool),
        "today_median": today[len(today) // 2],
        "today_max": today[-1],
        "added_median": added[len(added) // 2],
        "added_max": added[-1],
        "added_mean": round(sum(added) / len(added), 1),
        "commits_adding_nothing": sum(1 for a in added if a == 0),
        "per_commit": per_commit,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="machine-readable rows")
    ap.add_argument("--strict-dataflow", action="store_true",
                    help="only rows where the walked population IS the counted one")
    ap.add_argument("--transitive-dataflow", action="store_true",
                    help="only rows where the counted population derives from the walk at ANY depth")
    ap.add_argument("--cost", type=int, metavar="N", default=0,
                    help="model the widening over the last N non-merge commits")
    args = ap.parse_args(argv)

    if args.cost:
        c = widening_cost(args.cost, strict_only=args.strict_dataflow)
        print(f"widening cost over {c['sample']} real commits "
              f"(pool of {c['pool']} censused tests)")
        print(f"  selected today:  median {c['today_median']}, max {c['today_max']} test files")
        print(f"  ADDED by subject-selection: median {c['added_median']}, "
              f"mean {c['added_mean']}, max {c['added_max']}")
        print(f"  commits where it adds nothing: {c['commits_adding_nothing']}/{c['sample']}")
        return 0

    rows = census()
    out = unreachable(rows)
    if args.strict_dataflow:
        out = [r for r in out if r["strict_dataflow"]]
    if args.transitive_dataflow:
        out = [r for r in out if r["transitive_dataflow"]]

    if args.json:
        print(json.dumps({"unreachable": out, "all_matching": rows}, indent=2))
        return 0

    by_root: dict[str, int] = {}
    for r in out:
        for root in r["subject_roots"]:
            by_root[root] = by_root.get(root, 0) + 1

    print(f"whole-directory subject + stem-only selector: {len(out)} test file(s)")
    print(f"  of which the walk IS provably the counted population, in ONE hop: "
          f"{sum(1 for r in out if r['strict_dataflow'])}")
    print(f"  ... and at ANY depth (strict-in-substance, a LOWER bound): "
          f"{sum(1 for r in out if r['transitive_dataflow'])}")
    print(f"  already on CONTROL_TESTS (reachable, not counted above): "
          f"{sum(1 for r in rows if r['on_control_tests'])}")
    print()
    for r in out:
        mark = "!" if r["strict_dataflow"] else ("+" if r["transitive_dataflow"] else " ")
        print(f"  {mark} {r['test']}  [{', '.join(r['subject_roots'])}]")
    print()
    print("by subject root: " + ", ".join(f"{k} {v}" for k, v in sorted(by_root.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
