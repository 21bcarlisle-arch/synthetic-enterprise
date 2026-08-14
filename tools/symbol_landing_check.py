"""Symbol landing check -- does every first-party reference RESOLVE in the tree the commit creates?

THE CLASS THIS CLOSES (`uncommitted-and-orphaned-work`, R10).
`WORKER_FINDING_A_PATHSPEC_COMMIT_LANDED_THE_CONSUMER_AND_LEFT_THE_SUPPLIER_STAGED_2026-08-14`:
`19d8f94da` committed two READERS of `tools.simplifications_store.atom_name` and did not
commit the function they read. At HEAD the symbol did not exist; in every working tree
anyone looked at, it did. The publish gate found it hours later as a wedge with no
attribution. A pathspec commit names the paths the author EDITED, not the paths their
change CALLS -- and no control in this repo could see the difference, because:

  * the pre-commit gate selects tests from the index and RUNS THEM IN THE WORKING TREE,
    where the supplier was present;
  * the capability index's untracked-row check asks "is this FILE tracked?" and
    `tools/simplifications_store.py` was tracked -- only the new function inside it was
    missing. A file-granularity check cannot see a symbol-granularity omission.

So the subject here is neither the working tree nor HEAD: it is THE TREE THE COMMIT WOULD
CREATE, read straight out of git as blobs. Same subject `tools/surgical_land.py` gates on
and `_wall_crossing_landed_check` reconciles against, for the same reason -- at pre-commit
time HEAD is the tree the commit REPLACES, so a check against HEAD reds on the commit that
repairs a divergence and passes the one that creates it.

WHAT IT RESOLVES. Three reference shapes, all first-party only (stdlib and site-packages
are somebody else's problem and are skipped by name, never by import attempt):

  1. `import a.b.c`                      -> module `a.b.c` must exist in the tree
  2. `from a.b import Y`                 -> `Y` must be a top-level name of `a.b`, or `a.b.Y`
                                            must itself be a module in the tree
  3. `from a import b as m` ... `m.Y`    -> `Y` must be a top-level name of module `a.b`

Shape 3 is the one that would have caught the finding: both broken call sites were
`from tools import simplifications_store as _store` followed by `_store.atom_name(...)`.

R15 -- THE THREE KILLER PATTERNS, EACH ANSWERED IN CODE.

  TAUTOLOGY. Every byte read here comes from `git cat-file` against the tree under
  judgement. Nothing reads the working tree, nothing imports, nothing consults
  `sys.modules`. A check that resolved against the importable process would be asking the
  tree that was already green -- which is precisely how the original defect survived.

  FAIL-OPEN. A first-party module that will not parse is a FINDING, never a skip. A
  reference whose target module is absent from the tree is a FINDING. Dynamic modules --
  those defining a module-level `__getattr__` (PEP 562) -- can resolve anything at runtime,
  so their attribute references are unresolvable BY CONSTRUCTION; they are not silently
  dropped, they are counted and reported in `dynamic_modules` so the population is visible.

  FAIL-SILENT. The entry point is `run_at_tree`, called by the pre-commit gate on every
  commit that stages a `.py` file. A control invoked only by someone typing its name is
  permanently unavailable and therefore permanently passing -- the sibling finding
  (`THE_CLASS_CHECKER_HAS_NO_AUTOMATED_CALLER`) is the same class one rung up.

WHAT IT DELIBERATELY DOES NOT CLAIM. It is a STATIC resolver over module-level names. It
does not see `getattr(mod, name)`, `importlib.import_module` with a computed target, names
injected into a module's globals from outside, or attributes created by import side
effects. Those are not false NEGATIVES it is unaware of -- they are outside the subject,
which is stated here so nobody reads a green result as "every reference in this tree
works". What it does cover is the shape that broke: a statically-spelled reference to a
first-party symbol that no blob in the tree supplies.

Usage:
    python3 -m tools.symbol_landing_check                    # at HEAD, whole tree
    python3 -m tools.symbol_landing_check --at-tree <TREEISH> # the commit-time mode
    python3 -m tools.symbol_landing_check --at-tree T --since-tree P  # only what P->T changed
    python3 -m tools.symbol_landing_check --history 60       # false-positive census
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The first-party module roots. A dotted name whose head is not one of these is somebody
# else's package and is not our business -- decided by NAME, never by trying to import it
# (an import attempt would consult the running process, the tautology this control exists
# to avoid).
FIRST_PARTY_ROOTS = (
    "background", "company", "interface", "saas", "sim", "simulation", "tests", "tools",
)


# Attributes the import machinery puts on EVERY module object. They are supplied by the
# interpreter, not by any blob, so a check that reads them off the source would red on
# `mod.__file__` forever -- measured, not assumed: the first run of the real-history
# falsifier produced three of these and two true positives.
MODULE_DUNDERS = frozenset({
    "__file__", "__name__", "__doc__", "__dict__", "__package__", "__loader__",
    "__spec__", "__path__", "__builtins__", "__cached__", "__all__", "__annotations__",
})


class CheckerError(RuntimeError):
    """The checker could not do its job. Fail-closed: the caller must REFUSE, not pass."""


@dataclass(frozen=True)
class Finding:
    path: str          # the file holding the unresolvable reference
    line: int
    module: str        # the first-party module that should have supplied it
    symbol: str | None  # None => the MODULE itself is missing
    kind: str          # 'missing-module' | 'missing-attribute' | 'unparseable'
    detail: str = ""

    def __str__(self) -> str:
        if self.kind == "unparseable":
            return f"{self.path}: will not parse in this tree -- {self.detail}"
        if self.symbol is None:
            return (f"{self.path}:{self.line}: imports `{self.module}`, which NO BLOB IN "
                    f"THIS TREE supplies")
        return (f"{self.path}:{self.line}: `{self.module}.{self.symbol}` does not exist in "
                f"this tree -- the consumer landed and the supplier did not")


# --------------------------------------------------------------------------- git reads


def _git(*args: str, root: Path = ROOT) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                         check=False)
    if out.returncode != 0:
        raise CheckerError(f"git {' '.join(args[:2])} rc={out.returncode}: "
                           f"{out.stderr.strip()[-300:]}")
    return out.stdout


def tree_python_files(tree: str, root: Path = ROOT) -> list[str]:
    """Every first-party `.py` path in `tree`, read from git and never from disk."""
    names = _git("ls-tree", "-r", "--name-only", tree, root=root).splitlines()
    return sorted(
        p for p in names
        if p.endswith(".py") and p.split("/", 1)[0] in FIRST_PARTY_ROOTS
    )


def _read_blobs(tree: str, paths: list[str], root: Path = ROOT) -> dict[str, str]:
    """Bulk-read blobs with one `git cat-file --batch`, because per-file is ~700 forks."""
    if not paths:
        return {}
    spec = "".join(f"{tree}:{p}\n" for p in paths)
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=str(root), input=spec.encode(),
                          capture_output=True, check=False)
    if proc.returncode != 0:
        raise CheckerError(f"git cat-file --batch rc={proc.returncode}: "
                           f"{proc.stderr.decode(errors='replace')[-300:]}")
    out, sources, pos = proc.stdout, {}, 0
    for path in paths:
        nl = out.find(b"\n", pos)
        if nl < 0:
            raise CheckerError(f"cat-file output ended early at {path}")
        header = out[pos:nl].decode(errors="replace").split()
        if len(header) != 3 or header[1] != "blob":
            raise CheckerError(f"{tree}:{path} is not a blob: {' '.join(header)}")
        size = int(header[2])
        sources[path] = out[nl + 1:nl + 1 + size].decode("utf-8", errors="replace")
        pos = nl + 1 + size + 1  # payload + its trailing newline
    return sources


def path_to_module(path: str) -> str:
    mod = path[:-3].replace("/", ".")
    return mod[:-9] if mod.endswith(".__init__") else mod


# ----------------------------------------------------------------- what a module supplies


def _bound_names(body: list[ast.stmt]) -> set[str]:
    """Every name a module body binds at import time, including inside if/try/with.

    Conditional and guarded bindings COUNT -- `try: from x import y / except ImportError:
    y = None` supplies `y`. Counting only unconditional top-level statements would red on
    the repo's own compatibility shims, which is a false positive, not a finding."""
    names: set[str] = set()
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                names.update(_target_names(target))
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            names.update(_target_names(node.target))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    # A star-import can supply anything. Recording it as a wildcard keeps
                    # this fail-CLOSED-shaped rather than pretending the module is empty.
                    names.add("*")
                else:
                    names.add(alias.asname or alias.name)
        elif isinstance(node, (ast.If, ast.Try, ast.With, ast.For, ast.While)):
            names |= _bound_names(node.body)
            names |= _bound_names(getattr(node, "orelse", []))
            names |= _bound_names(getattr(node, "finalbody", []))
            for handler in getattr(node, "handlers", []):
                names |= _bound_names(handler.body)
        elif isinstance(node, ast.TryStar):  # pragma: no cover -- 3.11+, same shape
            names |= _bound_names(node.body)
    return names


def _target_names(target: ast.expr) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        out: set[str] = set()
        for elt in target.elts:
            out |= _target_names(elt)
        return out
    return set()


@dataclass
class ModuleFacts:
    supplies: set[str]
    dynamic: bool      # defines module-level __getattr__ -> can supply anything at runtime


def module_facts(source: str) -> ModuleFacts:
    tree = ast.parse(source)
    names = _bound_names(tree.body)
    return ModuleFacts(supplies=names, dynamic="__getattr__" in names or "*" in names)


# ------------------------------------------------------------------ what a module demands


@dataclass(frozen=True)
class Reference:
    module: str
    symbol: str | None
    line: int


def references(source: str, modules: frozenset[str] | set[str] = frozenset()) -> list[Reference]:
    """The first-party references a module makes, in the three resolvable shapes.

    `modules` is the set of module dotted-paths that EXIST in the tree, and it is what
    makes shape 3 safe. `from company.regulatory.compliance_scorecard import
    ComplianceDomain` binds a CLASS, not a module: reading `ComplianceDomain.ENERGY` off
    it is an enum member access and none of this control's business. Binding the alias
    only when the imported name is a real module is the difference between a 12.5%
    noise floor and a 0% one -- measured over 80 commits, both ways round.
    """
    tree = ast.parse(source)
    refs: list[Reference] = []
    aliases: dict[str, str] = {}   # local name -> first-party module it is bound to
    shadowed: set[str] = set()     # local names rebound to something that is not that module
    locally_set: set[tuple[str, str]] = set()  # (alias, attr) assigned in THIS file

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not _is_first_party(alias.name):
                    continue
                refs.append(Reference(alias.name, None, node.lineno))
                if alias.asname:
                    aliases[alias.asname] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.level or not node.module or not _is_first_party(node.module):
                continue  # relative imports are resolved against a package we may not know
            for alias in node.names:
                if alias.name == "*":
                    refs.append(Reference(node.module, None, node.lineno))
                    continue
                refs.append(Reference(node.module, alias.name, node.lineno))
                submodule = f"{node.module}.{alias.name}"
                if submodule in modules:
                    aliases[alias.asname or alias.name] = submodule
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                # `mod.thing = ...` CREATES the attribute (the monkeypatch shape, very
                # common in this repo's tests). Reading it back afterwards is legitimate.
                locally_set.add((node.value.id, node.attr))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            shadowed.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                shadowed |= _target_names(target)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            shadowed |= _target_names(node.target)

    for node in ast.walk(tree):
        if not (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)):
            continue
        if not isinstance(node.ctx, ast.Load):
            continue
        local = node.value.id
        target = aliases.get(local)
        if target is None or local in shadowed or (local, node.attr) in locally_set:
            continue
        if node.attr in MODULE_DUNDERS:
            continue
        refs.append(Reference(target, node.attr, node.lineno))
    return refs


def _is_first_party(dotted: str) -> bool:
    return dotted.split(".")[0] in FIRST_PARTY_ROOTS


# ------------------------------------------------------------------------------ the check


def check_tree(tree: str, only: list[str] | None = None,
               root: Path = ROOT) -> tuple[list[Finding], dict]:
    """Resolve every first-party reference in `tree`. `only` narrows the CONSUMER side.

    The SUPPLIER side is always the whole tree -- narrowing it would ask a smaller
    question than "does this reference resolve", and a census is not decomposable by
    pathspec even when its consumers are.
    """
    paths = tree_python_files(tree, root=root)
    sources = _read_blobs(tree, paths, root=root)
    by_module: dict[str, str] = {path_to_module(p): p for p in paths}

    facts: dict[str, ModuleFacts] = {}
    findings: list[Finding] = []
    for path, src in sources.items():
        try:
            facts[path_to_module(path)] = module_facts(src)
        except SyntaxError as e:
            # FAIL-OPEN is the pattern this refuses: a module that will not parse is a
            # finding, not a member of the population we quietly drop.
            findings.append(Finding(path, e.lineno or 0, path_to_module(path), None,
                                    "unparseable", f"{type(e).__name__}: {e.msg}"))

    known_modules = frozenset(by_module)
    consumers = [p for p in paths if only is None or p in set(only)]
    checked = 0
    for path in consumers:
        if path_to_module(path) not in facts:
            continue  # already reported unparseable above
        for ref in references(sources[path], known_modules):
            checked += 1
            if ref.symbol is None:
                if ref.module not in by_module and not _is_package(ref.module, by_module):
                    findings.append(Finding(path, ref.line, ref.module, None,
                                            "missing-module"))
                continue
            supplier = facts.get(ref.module)
            if supplier is None:
                if _is_package(ref.module, by_module):
                    continue  # a namespace package supplies its submodules
                findings.append(Finding(path, ref.line, ref.module, None, "missing-module"))
                continue
            if supplier.dynamic:
                continue  # PEP 562 __getattr__ / star-import: resolvable only at runtime
            if ref.symbol in supplier.supplies:
                continue
            if f"{ref.module}.{ref.symbol}" in by_module:
                continue  # `from pkg import submodule`
            findings.append(Finding(path, ref.line, ref.module, ref.symbol,
                                    "missing-attribute"))

    report = {
        "tree": tree,
        "modules_in_tree": len(paths),
        "consumers_checked": len(consumers),
        "references_resolved": checked,
        "dynamic_modules": sorted(m for m, f in facts.items() if f.dynamic),
        "findings": len(findings),
    }
    return findings, report


def _is_package(dotted: str, by_module: dict[str, str]) -> bool:
    prefix = dotted + "."
    return any(m.startswith(prefix) for m in by_module)


def run_at_tree(tree: str, since_tree: str | None = None,
                root: Path = ROOT) -> tuple[list[str], dict]:
    """The gate's entry point. Returns (human-readable findings, report).

    `since_tree` narrows the CONSUMER population to files this commit changed -- the
    honest scope for a commit-time gate, which must judge what the committer is adding
    and not bill them for a reference that was already unresolvable before they started.
    """
    only = None
    if since_tree is not None:
        changed = _git("diff-tree", "-r", "--name-only", "--no-commit-id",
                       since_tree, tree, root=root).splitlines()
        only = [p for p in changed if p.endswith(".py")]
        if not only:
            return [], {"tree": tree, "skipped": "no python changed between the two trees",
                        "findings": 0}
    findings, report = check_tree(tree, only=only, root=root)
    report["since_tree"] = since_tree
    return [str(f) for f in findings], report


# ------------------------------------------------------------------------------- the CLI


def _history_census(n: int, root: Path = ROOT) -> int:
    """Measure the FALSE-POSITIVE RATE over real history -- what the finding said nobody had.

    For each of the last `n` commits, resolve only the references that commit changed.
    A commit whose own tree is internally inconsistent is a TRUE positive of this class;
    everything else this reds on is the noise floor the gate would impose.
    """
    revs = _git("log", "--format=%H", "-n", str(n), root=root).split()
    total_red = 0
    for rev in revs:
        parents = _git("rev-parse", f"{rev}^@", root=root).split()
        if len(parents) != 1:
            continue  # merges have no single "before"
        try:
            found, rep = run_at_tree(f"{rev}^{{tree}}", f"{parents[0]}^{{tree}}", root=root)
        except CheckerError as e:
            print(f"{rev[:9]}  CHECKER ERROR {e}")
            continue
        if found:
            total_red += 1
            subject = _git("log", "-1", "--format=%s", rev, root=root).strip()
            print(f"{rev[:9]}  {len(found):2d} finding(s)  {subject[:70]}")
            for line in found[:6]:
                print(f"             {line}")
    print(f"\n{total_red} of {len(revs)} commits would have been RED "
          f"({100.0 * total_red / max(len(revs), 1):.1f}%)")
    return total_red


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--at-tree", default="HEAD^{tree}",
                    help="the tree to judge (the commit-time mode passes `git write-tree`)")
    ap.add_argument("--since-tree", default=None,
                    help="narrow the consumer side to what changed between this tree and --at-tree")
    ap.add_argument("--history", type=int, default=0,
                    help="false-positive census over the last N commits")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.history:
        return 1 if _history_census(args.history) else 0

    findings, report = run_at_tree(args.at_tree, args.since_tree)
    if args.json:
        print(json.dumps({**report, "detail": findings}, indent=2))
    else:
        for line in findings:
            print(f"  - {line}")
        print(f"{report['findings']} unresolvable reference(s) over "
              f"{report.get('references_resolved', 0)} resolved in tree {args.at_tree}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
