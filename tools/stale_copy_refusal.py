"""A commit whose copy of a file PREDATES the last landing to that file is refused, by path.

THE DEFECT THIS OWNS, and it is a class with three BLOCKING findings already banked
(`A_REWRITE_DELETED_THE_BINDING_REPAIR`,
`TWO_LANES_EACH_BUILT_R1S_UNBIASED_MAGNITUDE_ESTIMATOR_AND_A_PATHSPEC_LAND_DELETES_NINE_OF_HEADS_SYMBOLS`,
`TWO_LANES_BUILT_W1_14S_ARTEFACT_CUT_TWICE`). `CLAUDE.md` tells every lane to commit by pathspec,
never `-A`, and that is right -- but it protects only against OTHER FILES. **A pathspec stages the
WORKING-TREE copy**, so a lane that opened a file before another lane landed work in it, and then
names that path, silently reverts the landed commit. Nothing downstream can tell: the reverted tree
was a valid tree an hour ago, so it parses, its imports resolve, and its own tests pass.

WHY `tools/symbol_landing_check.py` IS GREEN ON THIS AND ALWAYS WILL BE. That control asks the
opposite question -- *does every first-party reference RESOLVE in the tree the commit creates* --
and a stale copy is INTERNALLY CONSISTENT by construction: the symbol and its callers revert
together, so every reference resolves. Not a gap in its reach; outside its subject. This one asks
the only question that can see a revert: *does this copy show any trace of the last landing?*

TWO RULES, AND THE ORDER THEY WERE ARRIVED AT IS EVIDENCE, SO IT IS RECORDED HERE.

  1. PREDATES-THE-LANDING (the one that fires). Take C, the last commit touching this path. Take
     the lines C ADDED that are DISTINCTIVE -- non-trivial, and appearing exactly once in C's
     version of the file. If the copy about to be committed contains **not one** of them, that copy
     was taken before C landed and committing it reverts C.

  2. STRICT SYMBOL SUBSET. Refuse when the copy supplies strictly fewer names than HEAD and adds
     not one. Cheap, exact, and it catches a deletion that rule 1 misses because the deleted name
     came from an older commit than C.

**RULE 2 WAS THE ONE SPECIFIED, AND MEASURING IT REFUTED IT AS THE PRIMARY.** Pre-registered in
`docs/staging/PREREG_THE_STALE_COPY_CENSUS_IS_A_DIFFERENT_QUESTION_FROM_THE_MTIME_CENSUS_2026-09-08.md`:
I predicted rule 2 would fire on 2-8 of the sixteen mtime-stale paths in the shared tree. It fired
on **zero**, and a poison round proved that was reachability, not blindness -- the control fires on
a hand-made strict subset of the same file. The reason is that `surgical_land` **never writes the
working tree** (by design -- that is what makes it safe for a two-lane file), so a landed commit
leaves every other lane's copy stale-by-mtime while its symbol set stays a SUPERSET of HEAD: the
lane's own additions are still there, the other lane's are simply missing. Symbol-set granularity
cannot see that. Rule 1 fires on 8 of the same 59 paths, including
`tools/promote_worktree_landing.py`, which was missing all fourteen lines of `_bind_to_claim` --
the binding repair, about to be deleted a second time by exactly the mechanism the first finding
named.

WHY "NOT ONE PRESENT" AND NOT A FRACTION. A threshold here would be fitted to today's tree, which
is `feedback_a_synthetic_fixture_you_keep_retuning_until_it_agrees` wearing a constant. "Contains no
trace of that commit at all" is a QUALITATIVE state -- your copy predates it -- and it needs no
number. The DISTINCTIVE filter is what makes the qualitative version hold up: without it, one
coincidentally-repeated line (`return None`, a duplicated assert) reads as "the copy has some of
it" and two genuinely-stale files escaped. Uniqueness in C's own version of the file is a property
of the evidence, not a dial: measured, it moved the population from 5 to 8 and every one of the
three additions is a copy with no trace of the landing.

WHAT THIS DOES NOT CATCH, said plainly so a green result is not read as stronger than it is. A lane
that has ALREADY pulled the landing and then rewrites over it is invisible to rule 1 (it has the
lines) and to rule 2 (it adds names). That is the wider half of
`A_REWRITE_DELETED_THE_BINDING_REPAIR`, and this control **narrows** that class rather than closing
it. The wider rule -- refuse on ANY lost line -- was considered and rejected: deleting code is an
ordinary edit, so it would refuse a large fraction of honest commits through the ONE legal landing
door, and a door that refuses honest work is the pressure toward bypass that `tools/surgical_land.py`
exists to remove. Narrow-and-armed beats wide-and-turned-off.

THE SUBJECT IS THE TREE THE COMMIT WOULD CREATE, never the working tree -- the same subject
`tools/symbol_landing_check.py` and `tools/surgical_land.py` already gate on, and for the same
reason: a `--content` landing supplies bytes that are on no disk anywhere, so a working-tree read
would judge a file the commit is not making.

VACUOUS EXTRACTION IS A REPORTED STATE, NOT A PASS. A path this control has no reader for yields
`None`, and `None` never reaches a comparison. Folded to an empty set instead, both sides would be
empty, the sets equal, and the path waved through **while looking checked** -- a coverage measure
that is useless without ever being fail-open. `--census` prints the no-opinion population in its own
section so what the control cannot see is on the surface rather than absent from it.

BOTH DOORS, SINCE 2026-09-08. `tools/surgical_land.py` calls `violations()` in-process, and
`tools/git-hooks/pre-commit` calls `--staged` -- so a plain `git commit -- <path>` faces this too.
It did not until that date, and the asymmetry was the wrong way round: the careful door was guarded
and the cheap, commoner one was not. See `staged()` for why the hook's subject is `git write-tree`
and why running inside `surgical_land`'s own extract is a paired SKIP rather than a second ask.

Run standalone:

    python3 -m tools.stale_copy_refusal --census        # working tree vs HEAD, both rules
    python3 -m tools.stale_copy_refusal --staged        # the tree this index would commit
    python3 -m tools.stale_copy_refusal --at-tree T --since-tree P

Exit 0 = clean, 1 = a path would revert a landing or lose names.
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# REUSED rather than re-cut: `_bound_names` is the import-time binding walker whose conditional and
# try-guarded cases (`try: from x import y / except ImportError: y = None` supplies `y`) were
# learned by that control reddening on this repo's own compatibility shims. Its batch blob reader
# is deliberately NOT reused -- see `blob_at`.
from tools.symbol_landing_check import _bound_names

ROOT = Path(__file__).resolve().parent.parent

#: Suffixes this control has an opinion about. Anything else yields `None` -- no opinion, reported
#: as such. Generated artefacts are deliberately absent: `site/data/*.json` is REWRITTEN whole on
#: every publish, so "lost a line" is its normal operation and not a finding.
PY_SUFFIXES = (".py",)
PAGE_SUFFIXES = (".html", ".js")
READABLE = PY_SUFFIXES + PAGE_SUFFIXES

#: The name-bearing anchors of a page. NOT "every symbol" -- an id and a function declaration are
#: what another lane's landed work adds to a page and a stale copy silently removes. Narrow on
#: purpose: a looser reader (CSS class names, arbitrary object keys) makes the set churn on
#: reformatting, and churn that ADDS a name defeats the strict-subset rule outright.
_PAGE_ANCHORS = (
    re.compile(r"""\bid\s*=\s*["']([A-Za-z_][\w-]*)["']"""),
    re.compile(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\("),
    re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*="),
)

PREDATES = "predates_landing"
SUBSET = "strict_symbol_subset"
UNPARSEABLE = "unparseable"


class Unparseable(Exception):
    """The blob would not parse. FAIL-CLOSED: an unavailable check is a failed check, and a `.py`
    blob that will not parse is a finding in its own right, never a skip."""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                          check=False)


def _git_text(root: Path, *args: str) -> str:
    out = _git(root, *args)
    if out.returncode != 0:
        raise RuntimeError("git {} rc={}: {}".format(
            " ".join(args[:2]), out.returncode, out.stderr.strip()[-300:]))
    return out.stdout


def blob_at(root: Path, tree: str, path: str) -> str | None:
    """`tree:path`'s text, or `None` when the tree has no such path.

    PER-PATH ON PURPOSE, where `symbol_landing_check._read_blobs` batches. That reader exists to
    keep a ~700-file whole-tree census off one fork per file, and it treats absence as an ERROR
    because at whole-tree scale absence cannot happen. Here absence is the ORDINARY answer at both
    ends -- a new file has no parent blob, a deletion has no result blob -- and the subject is the
    handful of paths one commit stages, where the fork cost is not the bill."""
    out = _git(root, "show", "{}:{}".format(tree, path))
    return out.stdout if out.returncode == 0 else None


# ------------------------------------------------------------------ rule 1: predates the landing


def _trivial(line: str) -> bool:
    """Lines that carry no evidence of WHICH commit they came from. A bare `return None` or a
    closing bracket appears in a thousand files, so its absence proves nothing about staleness and
    its presence proves nothing about freshness."""
    s = line.strip()
    return len(s) < 5 or s.startswith(("#", "//", "*")) or set(s) <= set("{}()[],:\"'")


def last_commit_touching(root: Path, path: str, upto: str = "HEAD") -> str | None:
    sha = _git(root, "log", "-1", "--format=%H", upto, "--", path).stdout.strip()
    return sha or None


def distinctive_lines(root: Path, path: str, commit: str) -> tuple[str, ...]:
    """The stripped lines `commit` ADDED to `path` that are non-trivial and appear exactly once in
    `commit`'s own version of the file.

    UNIQUENESS IS A PROPERTY OF THE EVIDENCE, NOT A DIAL. A line the commit added twice cannot
    distinguish "your copy has the landing" from "your copy happens to contain that line already",
    so it is not evidence either way and is dropped before the question is asked -- not weighted."""
    parent = _git(root, "rev-parse", "--verify", "{}^".format(commit))
    if parent.returncode != 0:
        # The commit that CREATED the file. There is no "before" to have landed over, and a copy
        # containing none of a file's creating commit is a file you have not got at all.
        return ()
    diff = _git(root, "diff", "--unified=0", "{}^".format(commit), commit, "--", path).stdout
    added = [ln[1:].strip() for ln in diff.splitlines()
             if ln.startswith("+") and not ln.startswith("+++")]
    version = blob_at(root, commit, path) or ""
    freq = Counter(ln.strip() for ln in version.splitlines())
    return tuple(ln for ln in added if not _trivial(ln) and freq[ln] == 1)


# ------------------------------------------------------------------ rule 2: strict symbol subset


def _class_members(body: list[ast.stmt], prefix: str = "") -> set[str]:
    """`Class.method` for every class in the body, nesting included.

    METHODS ARE THE POINT, not an extra. `_bound_names` is module-level only, and the landed work a
    stale copy most often drops is a METHOD added to an existing class -- every top-level name
    survives, so a module-level-only reader calls the sets equal and passes it."""
    out: set[str] = set()
    for node in body:
        if isinstance(node, ast.ClassDef):
            qual = prefix + node.name
            for inner in node.body:
                if isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    out.add("{}.{}".format(qual, inner.name))
            out |= _class_members(node.body, qual + ".")
        elif isinstance(node, (ast.If, ast.Try, ast.With)):
            out |= _class_members(node.body, prefix)
            out |= _class_members(getattr(node, "orelse", []), prefix)
            out |= _class_members(getattr(node, "finalbody", []), prefix)
            for handler in getattr(node, "handlers", []):
                out |= _class_members(handler.body, prefix)
    return out


def symbols(text: str, path: str) -> frozenset[str] | None:
    """The names `path`'s content supplies, or `None` when this control has no reader for it.

    `None` IS NOT THE EMPTY SET and the difference is the whole of the vacuity argument: an empty
    set compares equal to an empty set and passes, a `None` refuses to be compared at all."""
    suffix = Path(path).suffix
    if suffix in PY_SUFFIXES:
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            raise Unparseable("{} does not parse: {}".format(path, exc)) from exc
        return frozenset(_bound_names(tree.body) | _class_members(tree.body))
    if suffix in PAGE_SUFFIXES:
        found: set[str] = set()
        for pattern in _PAGE_ANCHORS:
            found.update(pattern.findall(text))
        return frozenset(found)
    return None


# ------------------------------------------------------------------------------- the judgement


@dataclass(frozen=True)
class Loss:
    path: str
    rule: str
    detail: tuple[str, ...]
    commit: str = ""

    def render(self) -> str:
        head = {
            PREDATES: "      your copy contains NOT ONE of the {} distinctive line(s) commit {} "
                      "added here,\n      so it was taken before that landing and this commit "
                      "reverts it:".format(len(self.detail), self.commit[:9]),
            SUBSET: "      would DELETE {} name(s) HEAD has, and adds none:".format(
                len(self.detail)),
            UNPARSEABLE: "      {}".format(self.detail[0] if self.detail else "did not parse"),
        }[self.rule]
        shown = list(self.detail[:6]) if self.rule != UNPARSEABLE else []
        tail = "" if len(self.detail) <= 6 else "        (+{} more)\n".format(len(self.detail) - 6)
        return "  {}  [{}]\n{}\n{}{}".format(
            self.path, self.rule, head,
            "".join("        - {}\n".format(n[:110]) for n in shown), tail)


def judge(root: Path, path: str, head_text: str | None, new_text: str | None,
          parent: str = "HEAD") -> Loss | None:
    """The one judgement for one path. `None` on either side of the content means there is no base
    or no result -- a wholly new file is not contested, a deletion is explicit -- so neither is this
    control's business."""
    if head_text is None or new_text is None or Path(path).suffix not in READABLE:
        return None
    commit = last_commit_touching(root, path, parent)
    if commit:
        distinctive = distinctive_lines(root, path, commit)
        if distinctive:
            present = {ln.strip() for ln in new_text.splitlines()}
            if not any(d in present for d in distinctive):
                return Loss(path, PREDATES, distinctive, commit)
    try:
        before, after = symbols(head_text, path), symbols(new_text, path)
    except Unparseable as exc:
        return Loss(path, UNPARSEABLE, (str(exc),))
    if before is None or after is None:
        return None
    if after < before:  # STRICT subset: loses names and adds not one
        return Loss(path, SUBSET, tuple(sorted(before - after)))
    return None


def violations(root: Path, parent: str, result: str, paths: list[str],
               allow: frozenset[str] = frozenset()) -> list[Loss]:
    """Every path in `paths` whose blob in `result` reverts a landing or loses names.

    Both blobs come out of git. `allow` is the declared-deletion escape hatch; an allowed path is
    dropped here and NAMED by the caller, because a silent exemption is how a control becomes a
    formality."""
    out = []
    for path in sorted(set(paths)):
        if path in allow or Path(path).suffix not in READABLE:
            continue
        loss = judge(root, path, blob_at(root, parent, path), blob_at(root, result, path),
                     parent=parent)
        if loss is not None:
            out.append(loss)
    return out


def refusal_text(losses: list[Loss]) -> str:
    return (
        "\n[stale-copy] ❌ COMMIT REFUSED -- {} path(s) would revert work that has already "
        "landed.\n\nA pathspec stages the WORKING-TREE copy. If you opened one of these files "
        "before another\nlane landed in it, your copy is the OLD one and this commit deletes their "
        "work.\n\n{}\n"
        "  THE FIX, and it is not to wait for them: `python3 -m tools.isolate_hunks --survey "
        "<path>`\n  shows the hunks, `--keep N` builds HEAD-plus-your-hunks-only, and\n"
        "  `surgical_land --content <path>=<file>` lands those bytes without reading the working "
        "copy.\n\n  IF THE DELETION IS YOURS AND DELIBERATE, say so: `--drops <path>`. It is "
        "printed in the\n  landing output, because an exemption nobody can see is not an "
        "exemption, it is a hole.\n".format(
            len(losses), "".join(loss.render() for loss in losses)))


# ------------------------------------------------------------------------------------ the census


def census(root: Path = ROOT) -> tuple[list[Loss], list[str]]:
    """(losses, no_opinion) over everything the working tree changes vs HEAD."""
    changed = [p for p in _git_text(root, "diff", "--name-only", "HEAD").splitlines() if p.strip()]
    losses = []
    for path in sorted(p for p in changed if Path(p).suffix in READABLE):
        try:
            work = (root / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        loss = judge(root, path, blob_at(root, "HEAD", path), work)
        if loss is not None:
            losses.append(loss)
    return losses, sorted(p for p in changed if Path(p).suffix not in READABLE)


# --------------------------------------------------------------------------- the pre-commit door

#: Set by `tools/surgical_land.py` to the sha of the tree it has ALREADY judged, and read by
#: `--staged` running inside that tool's extract. It is the TREE and not a boolean for the reason
#: an allowlist row is never a name: a token that says "trust me" is a bypass, while a token that
#: says "the check already ran on exactly THIS tree" is a claim `--staged` re-derives for itself
#: and discards when it does not hold.
ALREADY_GATED_ENV = "STALE_COPY_ALREADY_GATED_TREE"


def staged(root: Path = ROOT, env: dict | None = None) -> tuple[int, str]:
    """Judge the tree a `git commit` from this index WOULD create. Returns (rc, what to print).

    THE HOLE THIS CLOSES, and it is the commoner half. Until 2026-09-08 this control was reachable
    only from `tools/surgical_land.py`, so it guarded the careful door and left the cheap one open:
    `CLAUDE.md` tells every lane to commit by pathspec, a pathspec stages the WORKING-TREE copy,
    and a plain `git commit -- <path>` reverted a landing with nothing anywhere able to notice. The
    eight copies the census found on the shared tree are what an unguarded cheap door costs.

    THE SUBJECT IS `git write-tree`, NOT THE WORKING TREE. During a pre-commit hook the index IS
    the resulting tree, so writing it out gives the same subject `surgical_land` builds by hand --
    which is what makes a partial commit judged on the half being committed rather than the half
    on disk. A working-tree read here would judge a file the commit is not making.

    FAIL-CLOSED ON AN UNWRITEABLE INDEX and open on NO HEAD. They are different states: an index
    that will not write out is a check that could not run (R15: an unavailable check is a failed
    check), while a repo with no HEAD has no landing to revert and nothing to be stale against.

    THE SKIP IS NOT FAIL-OPEN, and the argument is that it is PAIRED rather than trusted.
    `surgical_land._land_once` calls `violations()` on (parent, result_tree, files) BEFORE it
    materialises the extract and refuses on the result, so by the time the hook runs in there the
    identical question has been answered on the identical tree -- with the `--drops` exemptions the
    hook cannot see. Re-asking it would not add a check; it would silently DELETE the escape hatch,
    refusing a declared deletion at the only legal landing door. So the skip is keyed to the tree
    sha, re-derived here: a token naming any other tree is ignored and the check runs.
    """
    env = os.environ if env is None else env
    if _git(root, "rev-parse", "--verify", "HEAD").returncode != 0:
        return 0, "[stale-copy] no HEAD yet -- a first commit reverts no landing."
    written = _git(root, "write-tree")
    if written.returncode != 0:
        return 1, ("[stale-copy] ❌ COMMIT REFUSED -- the index would not write out as a tree, so "
                   "the check could NOT RUN and an unavailable check is a failed one:\n  {}".format(
                       written.stderr.strip()[-300:]))
    result = written.stdout.strip()
    if env.get(ALREADY_GATED_ENV) == result:
        return 0, ("[stale-copy] already judged on this exact tree ({}) by tools/surgical_land.py, "
                   "which knows this landing's --drops; not re-asking.".format(result[:9]))
    changed = [ln.strip() for ln in _git(
        root, "diff-tree", "-r", "--name-only", "HEAD", result).stdout.splitlines() if ln.strip()]
    losses = violations(root, "HEAD", result, changed)
    if losses:
        return 1, refusal_text(losses)
    return 0, "[stale-copy] {} staged path(s) -- none reverts a landing.".format(len(changed))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--census", action="store_true", help="working tree vs HEAD")
    ap.add_argument("--staged", action="store_true",
                    help="judge the tree this index would commit (the pre-commit hook's door)")
    ap.add_argument("--at-tree", metavar="TREEISH", help="the tree the commit would create")
    ap.add_argument("--since-tree", metavar="TREEISH", default="HEAD")
    ap.add_argument("--root", default=str(ROOT), help="repository to judge (default: this one)")
    args = ap.parse_args(argv)
    root = Path(args.root)

    if args.staged:
        rc, text = staged(root)
        print(text)
        return rc

    if args.at_tree:
        changed = [ln.strip() for ln in _git_text(
            root, "diff-tree", "-r", "--name-only", args.since_tree, args.at_tree).splitlines()
            if ln.strip()]
        losses = violations(root, args.since_tree, args.at_tree, changed)
        if losses:
            print(refusal_text(losses))
            return 1
        return 0

    losses, no_opinion = census(root)
    print("[stale-copy] WOULD REVERT A LANDING: {}".format(len(losses)))
    for loss in losses:
        print(loss.render())
    print("\n[stale-copy] NO OPINION (no reader for this suffix -- NOT a clean verdict): {}".format(
        len(no_opinion)))
    for path in no_opinion[:15]:
        print("  {}".format(path))
    return 1 if losses else 0


if __name__ == "__main__":  # pragma: no cover -- entry point
    raise SystemExit(main())
