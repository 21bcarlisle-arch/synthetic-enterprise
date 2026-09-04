"""Land YOUR change to a file another lane is editing in place, without landing theirs.

THE DEFECT THIS OWNS. `CLAUDE.md` says commit by pathspec, never `-A`, because "other lanes have
work staged in this tree; the pathspec, not the tree lock, is what stops you sweeping it." That is
true and it protects only against OTHER FILES. A pathspec stages the WORKING-TREE copy of the file
it names, so when another lane has edited that same file in place, their unfinished work rides
inside your commit. On 2026-09-04 this happened twice in one morning on
`tools/generate_proof_data.py` -- a key rename mid-flight -- and cost two full gate cycles and
several hours of waiting for the other lane to land.

Waiting was the wrong answer and the door already existed: `tools/surgical_land.py --content
REPOPATH=SRCFILE` lands bytes you supply instead of the working-tree copy, and never reads the
file. What was missing was the bytes. This builds them.

    python3 -m tools.isolate_hunks --survey tools/generate_proof_data.py
    python3 -m tools.isolate_hunks tools/generate_proof_data.py --keep 2 --keep /_deployment/ \
        --out /tmp/gpd.py
    python3 -m tools.surgical_land tools/generate_proof_data.py --content tools/generate_proof_data.py=/tmp/gpd.py

DEFAULT-DENY, because the two mistakes are not symmetric. A hunk you forget to keep leaves your own
change incomplete, and the gate runs your tests against it. A hunk you keep by accident lands
another lane's half-finished work under your name, and nothing downstream can tell. So nothing is
kept unless it is named, and every dropped hunk is printed with its first changed line -- silence
about what was dropped is how "I landed only mine" becomes a claim nobody checked.

WHAT IT WILL NOT DO. It cannot tell whose hunk is whose; nothing in git records that. You say, it
prints back what it did, and the gate judges the result. It also never touches the working tree:
the other lane's file is read and not written, which is the difference between this and
`git checkout <path>` (forbidden here, and for exactly this reason -- it discards their work).
"""
from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
CONTEXT = 3


def head_lines(path: str, root=None) -> list[str]:
    """The committed copy: the base every reconstruction starts from."""
    r = subprocess.run(["git", "-C", str(_REPO if root is None else root), "show", f"HEAD:{path}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"REFUSED: {path} is not in HEAD, so there is no base to isolate against "
                         f"({(r.stderr or '').strip()}). A wholly new file is not contested.")
    return r.stdout.splitlines(keepends=True)


def group_opcodes(base: list[str], work: list[str], context: int = CONTEXT):
    """PURE. Returns (ops, groups) where `groups[i]` is the list of indices into `ops` that make up
    hunk i. A hunk ends where an unchanged run longer than twice the context begins -- the same
    rule `difflib.unified_diff` uses to decide where one @@ block stops and the next starts, so the
    numbering here matches what a reader sees in `git diff`."""
    ops = difflib.SequenceMatcher(None, base, work, autojunk=False).get_opcodes()
    groups: list[list[int]] = []
    current: list[int] = []
    for idx, (tag, i1, i2, _j1, _j2) in enumerate(ops):
        if tag == "equal":
            if current and (i2 - i1) > 2 * context:
                groups.append(current)
                current = []
            continue
        current.append(idx)
    if current:
        groups.append(current)
    return ops, groups


def reconstruct(base: list[str], work: list[str], ops, groups, keep: set[int]) -> list[str]:
    """PURE. Base, with only the kept hunks taken from the working copy.

    The invariant worth more than any test of a particular case: keeping EVERY hunk must reproduce
    the working copy exactly, and keeping NONE must reproduce HEAD exactly. If either fails the
    reconstruction is unsound and no selection in between can be trusted -- so both ends are
    checked at every run, not just in the suite.
    """
    kept_ops = {idx for gid in keep for idx in groups[gid]}
    out: list[str] = []
    for idx, (tag, i1, i2, j1, j2) in enumerate(ops):
        if tag == "equal" or idx in kept_ops:
            out.extend(work[j1:j2])
        else:
            out.extend(base[i1:i2])
    return out


def _matches(selector: str, base: list[str], work: list[str], ops, group: list[int]) -> bool:
    changed = []
    for idx in group:
        _tag, i1, i2, j1, j2 = ops[idx]
        changed.extend(base[i1:i2])
        changed.extend(work[j1:j2])
    pattern = selector[1:-1]
    return any(re.search(pattern, line) for line in changed)


def _describe(base: list[str], work: list[str], ops, group: list[int]) -> str:
    for idx in group:
        tag, i1, i2, j1, j2 = ops[idx]
        if tag in ("replace", "insert") and j2 > j1:
            return "+" + work[j1].rstrip()[:96]
        if i2 > i1:
            return "-" + base[i1].rstrip()[:96]
    return "(empty)"


def survey(path: str) -> int:
    base = head_lines(path)
    work = Path(_REPO / path).read_text().splitlines(keepends=True)
    ops, groups = group_opcodes(base, work)
    if not groups:
        print(f"{path}: identical to HEAD -- nothing to isolate.")
        return 0
    print(f"{path}: {len(groups)} hunk(s) against HEAD. Keep the ones that are YOURS:")
    for gid, group in enumerate(groups, start=1):
        first = ops[group[0]]
        print(f"  {gid:>3}  @@ base line {first[1] + 1:<6} {_describe(base, work, ops, group)}")
    print("\n  --keep N   or  --keep /regex/   (nothing is kept unless named)")
    return 0


def build(path: str, selectors: list[str], out: Path) -> int:
    base = head_lines(path)
    work = Path(_REPO / path).read_text().splitlines(keepends=True)
    ops, groups = group_opcodes(base, work)
    if not groups:
        raise SystemExit(f"REFUSED: {path} is identical to HEAD -- there is nothing to land.")

    # THE SOUNDNESS CHECK, run every time and not only in the suite: if all-in does not reproduce
    # the working copy and none-in does not reproduce HEAD, the reconstruction is wrong and any
    # partial selection is wrong in a way that would land silently.
    everything = set(range(len(groups)))
    if reconstruct(base, work, ops, groups, everything) != work:
        raise SystemExit("REFUSED: keeping every hunk did not reproduce the working copy. The "
                         "reconstruction is unsound; do not land anything built by it.")
    if reconstruct(base, work, ops, groups, set()) != base:
        raise SystemExit("REFUSED: keeping no hunk did not reproduce HEAD. Same conclusion.")

    keep: set[int] = set()
    for sel in selectors:
        if sel.startswith("/") and sel.endswith("/") and len(sel) > 2:
            hit = {gid for gid, g in enumerate(groups) if _matches(sel, base, work, ops, g)}
            if not hit:
                raise SystemExit(f"REFUSED: selector {sel} matched no hunk. A selector that matches "
                                 f"nothing is a typo, and treating it as 'keep nothing' is how the "
                                 f"wrong file gets landed quietly.")
            keep |= hit
        else:
            try:
                gid = int(sel) - 1
            except ValueError:
                raise SystemExit(f"REFUSED: {sel!r} is neither a hunk number nor /regex/.")
            if not 0 <= gid < len(groups):
                raise SystemExit(f"REFUSED: hunk {sel} does not exist ({len(groups)} in this file).")
            keep.add(gid)
    if not keep:
        raise SystemExit("REFUSED: no hunk selected. Landing HEAD's own bytes back over itself is "
                         "an empty change wearing a commit's clothes.")

    out.write_text("".join(reconstruct(base, work, ops, groups, keep)))
    print(f"{path}: kept {len(keep)} of {len(groups)} hunk(s) -> {out}")
    for gid, group in enumerate(groups):
        mark = "KEPT   " if gid in keep else "dropped"
        print(f"  {mark} {gid + 1:>3}  {_describe(base, work, ops, group)}")
    print(f"\n  python3 -m tools.surgical_land {path} --content {path}={out}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", help="repo-relative path")
    ap.add_argument("--survey", metavar="PATH", help="list the hunks and stop")
    ap.add_argument("--keep", action="append", default=[], metavar="N|/regex/")
    ap.add_argument("--out", type=Path, help="where to write the isolated bytes")
    args = ap.parse_args(argv)

    if args.survey:
        return survey(args.survey)
    if not args.path:
        ap.error("give a path, or --survey PATH")
    if not args.out:
        ap.error("--out is required: these bytes are for surgical_land --content")
    return build(args.path, args.keep, args.out)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
