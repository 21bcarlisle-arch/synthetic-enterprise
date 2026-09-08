"""The census that finds a control reading PYTHON SOURCE by substring, before it ships.

THE DEFECT THIS EXISTS FOR. A control that walks source files and asks `"token" in text` cannot
tell a line that DOES the thing from a comment that DESCRIBES it, and it is wrong in both
directions at once -- `tools/python_code_text.py` states the two halves and is the remedy. This
file is the part that stops an eleventh instance being written.

WHY A CENSUS AND NOT ANOTHER SWEEP. The population was enumerated by hand three times in one day
(`SEAT_FINDING_A_SOURCE_SCANNING_CONTROL_...`, then two `SEAT_RESULT_...` continuations). Every
pass was wrong in BOTH directions, and each was wrong the way the class itself is wrong:

  * the first screen matched `*.py` as a substring and was blind to `rglob("*")`, which walks
    Python and three other kinds at once -- the aimed-left shape, verbatim;
  * the second returned a verdict per FILE, and the class lives in a TEST: two of its three
    "unfiltered walk" rows were false positives, and its one true positive was true for the wrong
    reason, at a line sixty lines from the one the screen pointed at.

Both results closed with the same recommendation and neither turn built it: **write it as an AST
guard over the scan's SUBJECT expression**. A screen for "a control that reads code as text",
itself written as a substring over test source, is the class screening for itself.

WHAT A MEMBER IS, and each clause is load-bearing:

  1. text is READ FROM A FILE IN THE TREE -- `read_text()` off a path rooted at `Path(__file__)`,
     or the stdout of `git ls-files`. A fixture the test itself planted under `tmp_path` is not a
     member: it is input to a control, not a control.
  2. that text is then matched by SUBSTRING OR REGEX -- `in`, `not in`, or a `re`/pattern-object
     `search|match|findall|finditer|fullmatch`.
  3. the subject can BE Python -- the path evidence names `.py`, or is an unfiltered walk that
     includes it, or says nothing at all (see fail-closed below).
  4. and the text did NOT come through `tools/python_code_text.py` or `ast.parse`.

FAIL-CLOSED IS TOWARDS REPORTING, in three separate places, because a census that goes quiet
reports a clean tree and every mutation of it survives. Source that will not parse is reported as
`UNPARSEABLE` rather than skipped; a scan whose path evidence is absent is `unknown` and counts as
a member; and a scan whose evidence names both Python and non-Python is a member. The cost is
false positives, which a reader retires with a floor row; the alternative is the failure mode this
whole class is made of.

THE FLOOR IS A SET OF ROWS, NOT A COUNT. `tools/launch_shape_census.py` ratchets counts per
(path, shape) because its shapes recur legitimately in one file. Here a member is a specific
control, so the row is (path, function) and a row that stops firing is deleted rather than left
behind -- an exemption nobody can re-examine is how this class survived four instance fixes.
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]

#: The remedy. Text that has been through any of these is CODE, not text, and a substring over it
#: is the intended reading.
ROUTERS = frozenset({"searchable", "code_text", "code_strings", "imported_modules", "parse"})

#: Reading the source as a tree is the other legitimate answer, and `ast.parse` is spelled `parse`
#: once bound, so it shares the set above.

#: Substring-shaped interrogations of a string. `in`/`not in` is the `Compare`; these are calls.
_MATCH_CALLS = frozenset({"search", "match", "findall", "finditer", "fullmatch"})

#: A path expression naming one of these, and nothing Python, has a subject that is not Python --
#: a substring over it is legitimate and is left alone.
_NON_PYTHON_SUFFIXES = (
    ".md", ".json", ".yaml", ".yml", ".html", ".css", ".js", ".txt", ".csv", ".service",
    ".timer", ".toml", ".ini", ".cfg", ".sh", ".lock", ".log", ".jsonl", ".parquet",
)

#: Walk patterns that filter nothing, so Python is inside them.
_UNFILTERED = frozenset({"*", "**/*", "**", "*.*"})

PYTHON = "python"
UNFILTERED = "unfiltered"
UNKNOWN = "unknown"
NON_PYTHON = "non-python"

#: Every subject verdict that makes the scan a member. `UNKNOWN` is here on purpose: no evidence is
#: not evidence of absence, and this census reports rather than assumes.
MEMBER_SUBJECTS = frozenset({PYTHON, UNFILTERED, UNKNOWN})


@dataclass(frozen=True)
class Scan:
    """One substring-shaped read of file text, at the control that performs it."""

    path: str
    function: str
    lineno: int
    subject: str
    evidence: tuple[str, ...]

    @property
    def row(self) -> tuple[str, str]:
        return (self.path, self.function)

    def __str__(self) -> str:
        seen = ", ".join(self.evidence) if self.evidence else "no path evidence"
        return f"{self.path}:{self.lineno} {self.function}() subject={self.subject} [{seen}]"


#: WHERE THE CENSUS LOOKS. `tests/` was the drawn subject; `tools` and `background` were read on
#: 2026-09-08 and added once every member the reading found had been routed or dismissed.
#:
#: THE TWO FILES THE OLD COMMENT HERE NAMED -- `tools/canon_drift_check.py` and
#: `tools/capability_index.py` -- ARE NOT MEMBERS, and the comment was a guess made before the
#: census had ever been run over this scope. Both already read Python through `ast.parse`. Left
#: recorded rather than deleted, because a named prior that the measurement refutes is the only
#: evidence the measurement was not fitted to it.
#:
#: The reading itself held up: most of this scope dismisses. Roughly two thirds are scanners whose
#: subject is Markdown, JSON, a systemd unit or a log, reported only because the census fails
#: closed when path evidence is absent; the rest are container-membership tests (`key not in data`
#: over a dict parsed out of file text, which `_match_sites` cannot tell from a substring) and
#: widening prefilters whose verdict is taken from a parse tree afterwards. Those stay as FLOOR
#: ROWS carrying this reason -- the documented way to retire a false positive -- rather than being
#: excused by narrowing the sweep, which is how this class survived four instance fixes.
SCANNED = ("tests", "tools", "background")


def _scanned_population(root: Path, scope: tuple[str, ...] = SCANNED) -> list[Path]:
    """Committed `*.py`. `git ls-files` and not `rglob`, so a build artefact is never a subject."""
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", *[f"{d}/*.py" for d in scope]],
        capture_output=True, text=True, check=False,
    )
    return [root / p for p in out.stdout.split("\0") if p]


def _walk_own(node: ast.AST):
    """`ast.walk`, but never descending into a NESTED function.

    THE FIRST DRAFT USED `ast.walk` AND WAS THE SECOND HAND PASS AGAIN. A module-scope walk
    reaches every function body, so each scan was reported twice -- once at its own test, once at
    `<module>` carrying every literal in the file as its path evidence. A file-level verdict is
    exactly what the previous sweep got wrong, and writing the census as an AST guard does not
    protect you from it: the scope has to be the test's OWN body or the guard inherits the same
    blindness in a new spelling.
    """
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        for child in ast.iter_child_nodes(current):
            if child is not node and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            stack.append(child)


def _string_constants(node: ast.AST) -> list[str]:
    return [n.value for n in _walk_own(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _attr_names(node: ast.AST) -> set[str]:
    """Every attribute and function name called anywhere under `node`."""
    names: set[str] = set()
    for sub in _walk_own(node):
        if isinstance(sub, ast.Call):
            func = sub.func
            if isinstance(func, ast.Attribute):
                names.add(func.attr)
            elif isinstance(func, ast.Name):
                names.add(func.id)
    return names


def _names_used(node: ast.AST) -> set[str]:
    return {n.id for n in _walk_own(node) if isinstance(n, ast.Name)}


def _reads_a_file(node: ast.AST) -> bool:
    return "read_text" in _attr_names(node) or "read_bytes" in _attr_names(node)


def _routes(node: ast.AST) -> bool:
    """Does this expression put the text through the remedy?

    `ast.parse` counts: a control that walks the tree is asking about code by construction. The
    check is on the CALL NAME rather than on the import, because a module may import both and use
    one -- and it is the use that decides how the text was read.
    """
    return bool(_attr_names(node) & ROUTERS)


def _subject_of(evidence: list[str]) -> str:
    """What kind of file can this path evidence reach?

    The order is not arbitrary. Python FIRST, so a walk that reaches `.py` and `.md` alike is a
    member rather than being excused by its non-Python half -- the direction this census is
    allowed to be wrong in.
    """
    if not evidence:
        return UNKNOWN
    if any(".py" in e for e in evidence):
        return PYTHON
    if any(e in _UNFILTERED for e in evidence):
        return UNFILTERED
    if any(e.endswith(_NON_PYTHON_SUFFIXES) or e.startswith("*.") for e in evidence):
        return NON_PYTHON
    return UNKNOWN


class _Module:
    """One source file, read as code, with the tree-rooted names it defines."""

    def __init__(self, path: Path, tree: ast.Module) -> None:
        self.path = path
        self.tree = tree
        self.roots = self._tree_roots()

    def _tree_roots(self) -> set[str]:
        """Module-level names bound to a path inside the repository.

        `PROJECT = Path(__file__).resolve().parents[2]` and its aliases. This is the discriminator
        between a control (scans the tree) and a test fixture (plants files under `tmp_path` and
        reads them back). Without it the poison round of every control in this class reports as an
        instance of it.
        """
        roots: set[str] = set()
        for node in self.tree.body:
            if not isinstance(node, ast.Assign):
                continue
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if not targets:
                continue
            uses = _names_used(node.value)
            if "__file__" in _string_constants(node.value) or "__file__" in uses:
                roots.update(targets)
            elif uses & roots:
                roots.update(targets)
        return roots


def _path_evidence(scope: ast.AST) -> list[str]:
    """Every literal in `scope` that says something about WHICH files are read.

    Glob and walk patterns, `git ls-files` pathspecs, `endswith`/`suffix` literals, and any bare
    literal carrying a suffix -- a control that reads one named file by name is evidence too.
    Gathered from the enclosing scope rather than the module, because the class lives in a TEST and
    a file-level verdict is what the second hand pass got wrong.
    """
    out: list[str] = []
    for node in _walk_own(scope):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in ("glob", "rglob", "iglob"):
                out.extend(_string_constants(node) or ["*"])
            elif isinstance(func, ast.Attribute) and func.attr in ("endswith", "startswith"):
                out.extend(_string_constants(node))
        elif isinstance(node, ast.Attribute) and node.attr in ("suffix", "suffixes"):
            parent_literals: list[str] = []
            out.extend(parent_literals)
    # Bare literals that look like a file or a suffix. `"background/worker_tick.py"` and `".md"`
    # both say what is being read; a sentence does not.
    for text in _string_constants(scope):
        stripped = text.strip()
        if not stripped or " " in stripped or "\n" in stripped:
            if "ls-files" in text:
                out.append("*")
            continue
        if stripped.startswith(".") or "." in Path(stripped).name:
            out.append(stripped)
    return out


def _scopes(module: _Module) -> list[tuple[str, ast.AST]]:
    """Every function, plus the module body itself, as (name, node)."""
    out: list[tuple[str, ast.AST]] = [("<module>", module.tree)]
    for node in ast.walk(module.tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append((node.name, node))
    return out


def _tainted_names(scope: ast.AST, module: _Module) -> set[str]:
    """Names in `scope` holding file text that has NOT been through the remedy.

    A generous rule on purpose: any binding whose value reads a file, or mentions an
    already-tainted name, is tainted -- so `text = p.read_text()`, `for line in text.splitlines()`
    and `blob = "\\n".join(texts)` are all carried. A binding that ROUTES is dropped from the set
    rather than never added, so `text = searchable(p.read_text())` is clean even though the read
    is right there in the expression.
    """
    tainted: set[str] = set()
    for _ in range(_TAINT_PASSES):
        grown = _taint_pass(scope, tainted)
        if grown == tainted:
            break
        tainted = grown
    return tainted


#: How many times the taint sweep is repeated. `_walk_own` yields in stack order rather than in
#: SOURCE order, so `body = src.split(...)` can be visited before `src = path.read_text()` and a
#: single pass loses the chain -- which is how `tests/hooks/test_pull_next_work.py`, a member found
#: by hand, was absent from the census's own output. Iterating to a fixed point makes the answer
#: independent of traversal order; the cap is a runaway guard and is never the binding constraint,
#: because each pass can only grow the set and the set is bounded by the names in the scope.
_TAINT_PASSES = 8


def _taint_pass(scope: ast.AST, tainted: set[str]) -> set[str]:
    """One sweep of the taint rule over `scope`, starting from what is already known."""
    tainted = set(tainted)
    for node in _walk_own(scope):
        value, targets = None, []
        if isinstance(node, ast.Assign):
            value, targets = node.value, node.targets
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)) and node.value is not None:
            value, targets = node.value, [node.target]
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            value, targets = node.iter, [node.target]
        elif isinstance(node, ast.comprehension):
            value, targets = node.iter, [node.target]
        elif isinstance(node, ast.withitem) and node.optional_vars is not None:
            value, targets = node.context_expr, [node.optional_vars]
        if value is None:
            continue
        names = {n.id for t in targets for n in ast.walk(t) if isinstance(n, ast.Name)}
        if not names:
            continue
        if _routes(value):
            tainted -= names
            continue
        if _reads_a_file(value) or (_names_used(value) & tainted):
            tainted |= names
    return tainted


def _is_tainted(node: ast.AST, tainted: set[str]) -> bool:
    """Is this expression file text? Either an unbound read, or a name holding one."""
    if _routes(node):
        return False
    return _reads_a_file(node) or bool(_names_used(node) & tainted)


def _match_sites(scope: ast.AST, tainted: set[str]) -> list[ast.AST]:
    """`x in text`, `x not in text`, and `PATTERN.search(text)` over tainted text."""
    sites: list[ast.AST] = []
    for node in _walk_own(scope):
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.In, ast.NotIn)) and _is_tainted(comparator, tainted):
                    sites.append(node)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in _MATCH_CALLS:
            if any(_is_tainted(a, tainted) for a in node.args):
                sites.append(node)
    return sites


def _reaches_the_tree(scope: ast.AST, module: _Module, root_param: bool,
                      packages: frozenset[str]) -> bool:
    """Does this scope read the REPOSITORY, rather than files it planted itself?

    A control scans the tree: its paths descend from a `Path(__file__)` root, from `git ls-files`,
    or from a `root`/`_root` parameter that production passes the tree through -- the shape the
    fixed members adopted so their new legs drive the PRODUCTION scan over a planted tree instead
    of re-implementing it.

    THE LAST CLAUSE WAS ADDED BY THE CENSUS BEING WRONG, and the two it missed are the two the
    hand passes missed as well. `tests/saas/test_channel_attribution.py` reads
    `pathlib.Path("saas/channel_attribution.py")` -- a bare relative literal, no `__file__`
    anywhere -- and asserts the wall by substring; `tests/hooks/test_pull_next_work.py` does the
    same off a module-level `HOOK_PATH`. Requiring a `Path(__file__)` root made "scans the tree"
    mean "scans the tree the way most files spell it", which is the aimed-left shape a third time.
    A literal naming a top-level package IS a tree read, and the package set is derived from the
    tree rather than typed here, so a new top-level directory does not silently narrow the census.
    """
    if root_param:
        return True
    if _names_used(scope) & module.roots:
        return True
    literals = _string_constants(scope)
    if any("ls-files" in s for s in literals):
        return True
    return any(s.split("/", 1)[0] in packages and "/" in s for s in literals)


def _top_level_packages(root: Path) -> frozenset[str]:
    """The tree's own top-level directories, so `"saas/x.py"` reads as a tree path.

    Derived, never typed: a hand-kept list narrows the census the day a package is added, and a
    census that narrows silently is the failure this whole class is made of.
    """
    return frozenset(
        p.name for p in root.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name != "__pycache__"
    )


def _root_parameter(scope: ast.AST) -> bool:
    if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    args = scope.args
    named = [a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)]
    return any(a.lstrip("_") in ("root", "tree", "repo", "project") for a in named)


def census(root: Path | None = None, paths: list[Path] | None = None) -> list[Scan]:
    """Every substring-shaped read of Python source in the tree's own controls.

    UNPARSEABLE SOURCE IS A ROW, not a skip: we did not manage to look, and this census is only
    allowed to be wrong towards reporting.
    """
    root = root or _REPO
    subjects = paths if paths is not None else _scanned_population(root)
    packages = _top_level_packages(root)
    found: list[Scan] = []
    for path in subjects:
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        try:
            tree = ast.parse(source)
        except (SyntaxError, ValueError):
            found.append(Scan(rel, "<unparseable>", 1, UNKNOWN, ("UNPARSEABLE",)))
            continue
        module = _Module(path, tree)
        # Module-level bindings are visible inside every function, so a helper that reads the tree
        # once at import time and a test that searches it are ONE scan, not two halves of none.
        module_tainted = _tainted_names(module.tree, module)
        module_evidence = _path_evidence(module.tree)
        for name, scope in _scopes(module):
            tainted = _tainted_names(scope, module) | module_tainted
            sites = _match_sites(scope, tainted)
            if not sites:
                continue
            if not _reaches_the_tree(scope, module, _root_parameter(scope), packages):
                continue
            # THE SCOPE'S OWN EVIDENCE IS THE ONLY EVIDENCE THE VERDICT RESTS ON. Concatenating
            # scope and module evidence made a test that reads `site/capabilities/index.html`
            # report as a Python scan, because some other literal in the same file ends `.py` --
            # the file-level verdict the second hand pass was wrong for, reintroduced through the
            # evidence rather than through the walk.
            #
            # THAT FIX WAS FIRST WRITTEN `or module_evidence`, AND THE FALLBACK WAS FAIL-OPEN. It
            # can only fire when the scope says nothing about what it reads -- which rule 3 above
            # calls `unknown` and REPORTS -- so borrowing the module's evidence there turns a
            # member into a non-member and can never do the reverse. Measured 2026-09-08: dropping
            # it gained 12 rows in `tests/` and 29 in `tools`/`background`, and lost none.
            #
            # The two it hid are the argument for the shape. `canon_drift_check.probe_text_in_file`
            # reads a path named in `docs/design/canon_claims.yaml`, so NO source-level evidence
            # will ever say what its subject is and `unknown` is the whole of the right answer;
            # `generate_evidence_data._count_test_functions` counts `def test_` in Python source by
            # regex for a figure the evidence page PUBLISHES. Module evidence is still carried into
            # the printed row because a reader wants it -- it just no longer decides.
            own = _path_evidence(scope)
            subject = _subject_of(own)
            if subject not in MEMBER_SUBJECTS:
                continue
            evidence = own or module_evidence
            first = min(sites, key=lambda n: n.lineno)
            found.append(Scan(rel, name, first.lineno, subject, tuple(sorted(set(evidence)))))
    return sorted(found, key=lambda s: (s.path, s.lineno))


BASELINE_PATH = _REPO / "docs" / "observability" / "substring_source_scan_baseline.json"


def load_baseline(path: Path = BASELINE_PATH) -> set[tuple[str, str]]:
    """The frozen rows. A missing baseline is an ERROR, never an empty floor."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return {(row["path"], row["function"]) for row in data["rows"]}


def freeze(root: Path = _REPO, path: Path = BASELINE_PATH) -> int:
    """Write today's census as the floor. Only ever run deliberately, never by a gate."""
    scans = census(root)
    path.write_text(json.dumps({
        "what": "controls that read Python source as TEXT, one row per (file, function)",
        "scope": list(SCANNED),
        "why": "docs/staging/SEAT_RESULT_THE_CENSUS_FINDS_117_WHERE_THREE_HAND_PASSES_FOUND_NINE_2026-09-08.md",
        "why_this_scope": "docs/staging/SEAT_RESULT_THE_CENSUS_DISMISSAL_RULE_WAS_FAIL_OPEN_AND_THE_SCOPE_IS_NOW_THE_WHOLE_CLASS_2026-09-08.md",
        "a_row_is_not_a_verdict": "most rows outside tests/ are dismissals carrying a reason -- a "
                                  "non-Python subject, a container-membership test, or a widening "
                                  "prefilter whose verdict comes from a parse tree. The floor "
                                  "bounds GROWTH; read the row before routing it.",
        "how_to_shrink": "route the scan through tools/python_code_text.py, then delete its row",
        "rows": [{"path": s.path, "function": s.function, "subject": s.subject}
                 for s in sorted(scans, key=lambda s: s.row)],
    }, indent=2) + "\n", encoding="utf-8")
    return len(scans)


def check(root: Path = _REPO, path: Path = BASELINE_PATH) -> tuple[set, set]:
    """`(new, stale)` -- rows the tree grew, and rows the baseline still claims and the tree lost.

    SHRINK-ONLY IN BOTH DIRECTIONS. A new row is the eleventh instance and refuses. A stale row is
    a fixed control whose exemption outlived it, and this repo's own evidence is that a dead
    exemption is a pre-authorised re-entry: it is deleted, not left behind.
    """
    live = {s.row for s in census(root)}
    frozen = load_baseline(path)
    return live - frozen, frozen - live


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=_REPO)
    ap.add_argument("--scope", nargs="+", default=list(SCANNED),
                    help="tree directories to census (default: the drawn subject, tests/)")
    ap.add_argument("--rows", action="store_true", help="print (path, function) rows only")
    ap.add_argument("--check", action="store_true", help="refuse a row the baseline does not hold")
    ap.add_argument("--freeze", action="store_true", help="rewrite the baseline from this tree")
    args = ap.parse_args(argv)
    if args.freeze:
        print(f"froze {freeze(args.root)} row(s) -> {BASELINE_PATH}")
        return 0
    if args.check:
        new, stale = check(args.root)
        for row in sorted(new):
            print(f"NEW  {row[0]}::{row[1]} reads Python source as text -- "
                  f"route it through tools/python_code_text.py")
        for row in sorted(stale):
            print(f"STALE {row[0]}::{row[1]} no longer scans -- delete its baseline row")
        return 1 if (new or stale) else 0
    scans = census(args.root, _scanned_population(args.root, tuple(args.scope)))
    for scan in scans:
        print(f"{scan.row}," if args.rows else scan)
    print(f"-- {len(scans)} scan(s) of Python source read as text", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
