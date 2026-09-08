"""A name that resolves only in another UNCOMMITTED file makes that file part of the same landing.

THE DEFECT THIS OWNS, measured 2026-09-08 and recorded in the addendum to
`SEAT_FINDING_THE_STALE_COPY_REMEDY_HAS_NO_MOVE_FOR_A_RIVAL_COPY_HEAD_ALREADY_SUPERSEDES`.
`tools/stale_copy_refusal.py` names eight working copies that would revert a landing, one path at
a time, and its refusal sends each of them to `tools/isolate_hunks.py` -- also one path at a time.
One of the eight, `tests/tools/test_commit_refusal_attribution.py`, calls
`attr.decompose_outage(...)`. `tools/commit_refusal_attribution.py` is present at `origin/main` and
does **not** define that name; it is defined only in the shared tree's *uncommitted* copy of that
module, which is not stale by rule 1 and which therefore no control names. A seat that works the
eight path by path, exactly as instructed, lands the test without the function and reds the tree at
HEAD for every lane.

**A LANE'S WORK IS NOT PATH-SHAPED, AND EVERY TOOL IN THIS ROUTE IS.** That is the whole finding.
The refusal is correct about the eight paths it names; the remedy's GRANULARITY is what is wrong,
and nothing in the route tells you to look for the other half because the other half is invisible
to the control that sent you.

WHY NOT JUST LET `tools/symbol_landing_check.py` CATCH IT. It does catch it -- it is the control
that asks exactly this question, and it is where the definition of "resolves" is taken from here
rather than re-cut. But it is reachable only from the LANDING door, so it fires after a seat has
already surveyed the hunks, selected them, built the bytes and typed the commit. The cost of asking
one pass earlier is one whole-tree blob read; the cost of asking late is the turn.

WHAT IT DOES NOT CLAIM. The supplier search is over the working tree, so it answers "who has this
name RIGHT NOW", and right now moves: another lane may land or drop that file a minute later. It is
a POINTER to the other half, not a proof about it -- which is why the finding is that the pair is
NAMED, and the landing gate still runs. And a name that resolves nowhere at all is reported as
exactly that: an unresolved reference with no known supplier is a worse state than a pair, not a
cleaner one, and folding the two together would read as "no pair found" on the tree's worst case.

ONE BLIND SPOT, INHERITED ON PURPOSE. `from tools import brand_new_module` RESOLVES here even when
no tree has that module, because `tools/` has no `__init__.py` and `unresolved_kind` treats a
namespace package as supplying its submodules. That is the landing gate's own behaviour, and
agreeing with it is worth more than being right alone: a pointer that refuses early where the gate
would pass late teaches a seat to stop believing it. `import tools.brand_new_module` and
`from tools.brand_new_module import name` are both seen. The limit is recorded rather than papered
over, and it belongs to `tools/symbol_landing_check.py` to move.

    python3 -m tools.landing_pair tests/tools/test_commit_refusal_attribution.py
    python3 -m tools.landing_pair --root /elsewhere --content path.py=/tmp/isolated.py path.py
"""
from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path

# REUSED whole, and the reuse IS the argument: "does this reference resolve in the tree the commit
# creates" has exactly one definition in this repo and a second one would be a second answer to the
# question that banked the `uncommitted-and-orphaned-work` class. `references` carries the alias
# handling that took a 12.5% noise floor to 0%; `module_facts` carries the PEP-562 dynamic-module
# case. What is new here is the SUPPLIER side -- looking in the uncommitted working tree, which
# that control deliberately never reads.
from tools.symbol_landing_check import (
    ModuleFacts,
    Reference,
    _is_first_party,
    _read_blobs,
    module_facts,
    path_to_module,
    references,
    tree_python_files,
    unresolved_kind,
)

ROOT = Path(__file__).resolve().parent.parent

#: A reference to the MODULE rather than a name inside it (`import a.b`). Spelled out because the
#: alternative -- `None` in the same set as real symbol names -- sorts and renders as nothing.
WHOLE_MODULE = "(the module itself)"


def _git(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                         check=False)
    return out.stdout if out.returncode == 0 else ""


@dataclass(frozen=True)
class TreeIndex:
    """What a tree supplies, in `unresolved_kind`'s own two shapes. Built ONCE per census -- the
    read is ~700 blobs and the eight paths that ask about it would otherwise pay for it eight
    times.

    A MODULE THAT WILL NOT PARSE IS IN `by_module` AND NOT IN `facts`, exactly as `check_tree`
    leaves it. Adding an empty `facts` entry instead would make its consumers report a
    missing-ATTRIBUTE where the tree's real state is that the module is unreadable, and giving it
    a `dynamic` entry would make every reference into it resolve -- the fail-open shape."""
    by_module: dict[str, str]
    facts: dict[str, ModuleFacts]

    @property
    def modules(self) -> frozenset[str]:
        return frozenset(self.by_module)


def index_tree(root: Path = ROOT, tree: str = "HEAD") -> TreeIndex:
    paths = tree_python_files(tree, root=root)
    sources = _read_blobs(tree, paths, root=root)
    facts: dict[str, ModuleFacts] = {}
    for path, src in sources.items():
        try:
            facts[path_to_module(path)] = module_facts(src)
        except SyntaxError:
            continue
    return TreeIndex({path_to_module(p): p for p in paths}, facts)


def unresolved_in(source: str, index: TreeIndex) -> list[Reference]:
    """The first-party references `source` makes that `index`'s tree does not supply.

    The verdict comes from `symbol_landing_check.unresolved_kind` and not from a rule written
    here: the landing gate and this pre-landing pointer must agree, or a seat is refused early by
    one and passed late by the other."""
    return [ref for ref in references(source, index.modules)
            if unresolved_kind(ref, index.by_module, index.facts) is not None]


# ------------------------------------------------------------------- the uncommitted supplier side


def uncommitted_python(root: Path = ROOT) -> list[str]:
    """Every `.py` path the working tree changes or adds against HEAD -- tracked AND untracked.

    UNTRACKED COUNTS. The supplier half of the original defect
    (`A_PATHSPEC_COMMIT_LANDED_THE_CONSUMER_AND_LEFT_THE_SUPPLIER_STAGED`) was a tracked file with
    an untracked FUNCTION, but a wholly new module is the same pair one file up, and a census that
    only diffed tracked paths would call that one 'no supplier found anywhere' -- the answer that
    looks like a clean result."""
    changed = _git(root, "diff", "--name-only", "HEAD").splitlines()
    added = _git(root, "ls-files", "--others", "--exclude-standard").splitlines()
    return sorted({p.strip() for p in changed + added
                   if p.strip().endswith(".py") and _is_first_party(path_to_module(p.strip()))})


@dataclass(frozen=True)
class Pair:
    consumer: str
    supplier: str | None        # None => nothing in the working tree supplies it either
    module: str
    symbols: tuple[str, ...]

    def render(self) -> str:
        if self.supplier is None:
            return ("      {} references {}.{} -- and NO tree supplies it, committed or "
                    "not.\n      That is not a pair; it is a reference to something that does not "
                    "exist anywhere.".format(
                        self.consumer, self.module, ", ".join(self.symbols)))
        return ("      PAIR: {} needs {}.{},\n      which exists ONLY in the UNCOMMITTED copy of "
                "{}. Landing this path alone\n      reds the tree at HEAD for every lane -- that "
                "file is part of the same landing.".format(
                    self.consumer, self.module, ", ".join(self.symbols), self.supplier))


def pairs_for(source: str, consumer: str, index: TreeIndex,
              root: Path = ROOT, candidates: list[str] | None = None) -> list[Pair]:
    """Every name `source` introduces that the landing tree lacks, and who in the working tree has
    it. `source` is the BYTES BEING LANDED, never the path's working copy -- an isolated
    reconstruction is on no disk, and asking about the file would judge something else."""
    missing = unresolved_in(source, index)
    if not missing:
        return []
    candidates = uncommitted_python(root) if candidates is None else candidates

    by_module: dict[str, set[str]] = {}
    for ref in missing:
        by_module.setdefault(ref.module, set()).add(ref.symbol or WHOLE_MODULE)

    out: list[Pair] = []
    for module, names in sorted(by_module.items()):
        hit = next((p for p in candidates if p != consumer and path_to_module(p) == module), None)
        supplied: frozenset[str] = frozenset()
        if hit is not None:
            try:
                supplied = frozenset(module_facts(
                    (root / hit).read_text(encoding="utf-8", errors="replace")).supplies)
            except (OSError, SyntaxError):
                supplied = frozenset()
        held = sorted(n for n in names if n == WHOLE_MODULE or n in supplied)
        orphaned = sorted(n for n in names if n not in held)
        if held:
            out.append(Pair(consumer, hit, module, tuple(held)))
        if orphaned:
            # Reported SEPARATELY and never folded into the pair: a name no tree supplies is a
            # worse state than a pair, and one row saying "paired" would read as the whole answer.
            out.append(Pair(consumer, None, module, tuple(orphaned)))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="the consumer path(s) about to be landed")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--tree", default="HEAD", help="the tree the landing goes into")
    ap.add_argument("--content", action="append", default=[], metavar="REPOPATH=SRCFILE",
                    help="judge these bytes for REPOPATH instead of its working copy")
    args = ap.parse_args(argv)
    root = Path(args.root)
    supplied = dict(item.split("=", 1) for item in args.content)

    index = index_tree(root, args.tree)
    found = 0
    for path in args.paths:
        src = Path(supplied[path]).read_text() if path in supplied \
            else (root / path).read_text(encoding="utf-8", errors="replace")
        for pair in pairs_for(src, path, index, root):
            print(pair.render())
            found += 1
    if not found:
        print("[landing-pair] {} path(s): every name they introduce resolves in {}.".format(
            len(args.paths), args.tree))
    return 1 if found else 0


if __name__ == "__main__":  # pragma: no cover -- entry point
    raise SystemExit(main())
