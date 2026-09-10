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
    return {"subject_roots": sorted(roots), "strict_dataflow": _strict_dataflow(tree)}


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

    if args.json:
        print(json.dumps({"unreachable": out, "all_matching": rows}, indent=2))
        return 0

    by_root: dict[str, int] = {}
    for r in out:
        for root in r["subject_roots"]:
            by_root[root] = by_root.get(root, 0) + 1

    print(f"whole-directory subject + stem-only selector: {len(out)} test file(s)")
    print(f"  of which the walk IS provably the counted population: "
          f"{sum(1 for r in out if r['strict_dataflow'])}")
    print(f"  already on CONTROL_TESTS (reachable, not counted above): "
          f"{sum(1 for r in rows if r['on_control_tests'])}")
    print()
    for r in out:
        mark = "!" if r["strict_dataflow"] else " "
        print(f"  {mark} {r['test']}  [{', '.join(r['subject_roots'])}]")
    print()
    print("by subject root: " + ", ".join(f"{k} {v}" for k, v in sorted(by_root.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
