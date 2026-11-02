"""A tree for a blind role, with no code in it by construction.

The cold reader has been blind by prompt: its brief says "read only the packet", and nothing
stops it opening `company/`. A reader who can open the code argues from the code instead of
from the page (`docs/design/THE_IMPROVEMENT_LOOP.md` §4, blind roles option (b)). This makes
the reader's tree out of an allow-list — the built pages and cast of a named book, the ruling
it grades against and its brief — and then refuses the tree if any forbidden path is in it.

WHY NOT A SPARSE `git worktree`
-------------------------------
A sparse checkout leaves a `.git` pointer to this repository, and `git show HEAD:company/x.py`
reads any file whatever the sparse pattern says. So the tree is a plain directory with no
`.git`, and `check` refuses one that has it.

THE HONEST LIMIT
----------------
This makes the TREE blind. A process that reads by absolute path can still reach the
repository; blinding the reader's process is a launch decision, not this tree's. The reader is
the same model family as the builder (`independence: false`, as `tools/blind_review.py`).
The page's own files (its HTML comments, its CSS, its carbon feed) name code paths, as the
published page does: names, never contents. A reader that renders the page does not see them.

    python3 -m tools.blind_worktree --book /var/tmp/fresh-run-out-<sha> \
        --site /var/tmp/<pages>/tree/site --brief <brief.md> [--dest <dir>]
    python3 -m tools.blind_worktree --check <dir> --book /var/tmp/fresh-run-out-<sha>
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RULING = "docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md"
RULING_DONE = RULING.replace("/advisor/", "/advisor/done/")

# The code and the tests, wherever they sit in the tree.
FORBIDDEN_DIRS = frozenset({"company", "saas", "sim", "simulation", "tools", "tests", ".git"})
# Source and run results: a book is pickles and a DONE stamp; a run_output is its digest.
FORBIDDEN_SUFFIXES = (".py", ".pyc", ".pkl", ".pkl.gz", ".mjs")
FORBIDDEN_NAMES = frozenset({"DONE.json", "__pycache__"})
FORBIDDEN_PREFIXES = ("run_output",)
# What the pages read, and the ruling and brief beside them. Copying by allow-list means a
# build script or a result format nobody listed (`build.sh`, `.parquet`, `.ipynb`) stays out
# without having to be named; `check` refuses any other type, so the two cannot disagree.
READABLE_SUFFIXES = frozenset({".html", ".json", ".css", ".svg", ".md"})

# What a cold reader may see of a built site: the Explore page, its cast, the per-household
# pages it opens, and exactly what the page fetches and links to render (read off its own
# `fetch(` and `href=` on the 3dc5a92948 build). Not `assets/`: its model-on-a-page pictures name
# code paths and Explore never loads them.
COLD_READER_SITE = (
    "explore/index.html",
    "data/explore_cast.json",
    "data/customers",
    "data/customers.json",
    "data/explore_carbon.json",
    "data/explore_hh_days.json",
    "data/weather.json",
    "brand/brand.css",
    "favicon.svg",
)


def check(tree: Path, book: Path | None = None) -> list[str]:
    """Every path in `tree` a blind reader must not have, each with its reason. Empty is clean.

    With `book`, any file named like one of the book's own files, at any depth of the book, is
    refused too, so a run result renamed past the suffix list is still caught by name. Names are
    compared case-folded: `Company/` and `a.PY` are what a case-insensitive disk serves as
    `company/` and `a.py`."""
    tree = Path(tree)
    if not tree.is_dir():
        return [f"{tree}: no such tree"]
    book_names = {p.name.lower() for p in Path(book).rglob("*") if p.is_file()} if book else set()
    found = []
    for p in sorted(tree.rglob("*")):
        rel = p.relative_to(tree)
        parts = {part.lower() for part in rel.parts}
        name = p.name.lower()
        if p.is_symlink():
            found.append(f"{rel}: a symlink can reach outside the tree")
        elif parts & FORBIDDEN_DIRS:
            found.append(f"{rel}: under {sorted(parts & FORBIDDEN_DIRS)[0]}/, which is code")
        elif parts & {n.lower() for n in FORBIDDEN_NAMES}:
            found.append(f"{rel}: {sorted(parts & {n.lower() for n in FORBIDDEN_NAMES})[0]}"
                         " is source or a run result")
        elif name.endswith(FORBIDDEN_SUFFIXES):
            found.append(f"{rel}: a {p.suffix} file is source or a run result")
        elif name.startswith(FORBIDDEN_PREFIXES):
            found.append(f"{rel}: a run_output is a run result")
        elif p.is_file() and name in book_names:
            found.append(f"{rel}: named like a file of the book")
        elif p.is_file() and p.suffix.lower() not in READABLE_SUFFIXES:
            found.append(f"{rel}: a {p.suffix or 'suffixless'} file is not a type the pages read")
    return found


def _copy_readable(src: Path, out: Path) -> None:
    """Copy `src` to `out`, keeping only the file types the pages read. A symlink in the source
    is refused, not followed: following it copies whatever it points at as an ordinary file."""
    files = sorted(q for q in src.rglob("*")) if src.is_dir() else [src]
    for q in files:
        if q.is_symlink():
            raise SystemExit(f"refused: {q} is a symlink, and copying it copies what it points at")
        inside = {part.lower() for part in q.relative_to(src).parts} if src.is_dir() else set()
        if inside & (FORBIDDEN_DIRS | {n.lower() for n in FORBIDDEN_NAMES}):
            continue
        if q.is_file() and q.suffix.lower() in READABLE_SUFFIXES:
            dst = out / q.relative_to(src) if src.is_dir() else out
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(q, dst)


def make_cold_reader(book: Path, site: Path, brief: Path, dest: Path,
                     ruling: Path | None = None) -> dict:
    """Build the cold reader's tree at `dest` and refuse it, removed, if `check` finds anything."""
    book, site, brief, dest = Path(book), Path(site), Path(brief), Path(dest)
    if not (book / "DONE.json").exists():
        raise SystemExit(f"refused: {book} has no DONE.json, so it is not a finished book")
    if ruling is None:
        ruling = next((ROOT / r for r in (RULING, RULING_DONE) if (ROOT / r).exists()), None)
        if ruling is None:
            raise SystemExit(f"refused: the ruling is at neither {RULING} nor its done/ room")
    if dest.exists():
        raise SystemExit(f"refused: {dest} exists; a blind tree is made once, never topped up")
    missing = [s for s in COLD_READER_SITE if not (site / s).exists()]
    if missing:
        raise SystemExit(f"refused: the built site at {site} lacks {missing}")
    dest.mkdir(parents=True)
    try:
        for s in COLD_READER_SITE:
            _copy_readable(site / s, dest / "site" / s)
    except SystemExit:
        shutil.rmtree(dest)
        raise
    shutil.copy2(ruling, dest / "RULING.md")
    shutil.copy2(brief, dest / "BRIEF.md")
    # Names only: an absolute path here hands the reader the repository root and the book.
    manifest = {"role": "cold_reader", "book": book.name, "ruling": ruling.name,
                "independence": False}
    (dest / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n")
    leaks = check(dest, book)
    if leaks:
        shutil.rmtree(dest)
        raise SystemExit("refused, tree removed: " + "; ".join(leaks[:5]))
    return manifest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="blind_worktree", description=__doc__.split("\n")[0])
    ap.add_argument("--check", type=Path, help="report what a blind reader must not have in a tree")
    ap.add_argument("--book", type=Path)
    ap.add_argument("--site", type=Path, help="the site built from the book")
    ap.add_argument("--brief", type=Path)
    ap.add_argument("--ruling", type=Path)
    ap.add_argument("--dest", type=Path)
    a = ap.parse_args(argv)
    if a.check:
        leaks = check(a.check, a.book)
        print("\n".join(leaks) or f"clean: {a.check}")
        return 1 if leaks else 0
    if not (a.book and a.site and a.brief):
        ap.error("--book, --site and --brief are required to make a tree")
    dest = a.dest or Path("/var/tmp/blind") / f"cold-reader-{a.book.name}"
    make_cold_reader(a.book, a.site, a.brief, dest, a.ruling)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
