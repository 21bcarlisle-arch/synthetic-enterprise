**Severity:** MAJOR · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Both blind readers raise 1 finding(s) on 2dbafe2d23 (2026-10-30)

*Written by `background/two_reader_review.py`, the automatic lane of the two-reader trial
(director ruling 28 Oct, review 2026-11-11). Nothing here has been checked. Check each pair at
HEAD like any other finding, and record the outcome for the review. Severity is capped at
MAJOR until a check confirms more.*

- **Commit:** `2dbafe2d23d54e0a5e71a913dc411eb1e1bac29f`, committed 2026-10-30T12:36:22Z.
- **Modules it added:** `tools/blind_worktree.py`.
- **Verdicts:** A NEEDS_WORK, B NEEDS_WORK (trust ledger,
  `reading-review-live-2026-10-30:2dbafe2d23:arm{A,B}`).

## Raised by both (pairs from the tool-less matcher; undo any that do not name one defect)

1. **A#1 (MAJOR) `tools/blind_worktree.py:231`** MANIFEST.json is written inside the blind tree with str(book), str(site), str(ruling), str(brief) as absolute paths; with ruling defaulted, 'ruling' is ROOT/docs/staging/advisor/..., giving the reader the repo root and the book's run-results folder, the path-reading gap the docstring's 'honest limit' names. check() never reads file contents and no test checks the manifest's contents.
   **B#1 (MAJOR) `tools/blind_worktree.py:231`** MANIFEST.json is written inside the blind tree with absolute paths for book, site, ruling and brief; with no --ruling the ruling path is ROOT/docs/staging/advisor/..., i.e. the repo root. That is the path the commit's own 'reads by absolute path' limit needs, handed to the reader, and check() never inspects contents. Input: make with no --ruling, then MANIFEST.json shows "ruling": "<repo>/docs/staging/advisor/DIRECTOR_RULING_...".

## Raised by one reader only (not filed under the vote)

- A#2 (MINOR): copytree(symlinks=False)/copy2 copy what a source symlink points to, so a site file like data/customers/x.json -> ../../../company/billing.py arrives as an ordinary file holding code and check() passes it; the symlink test only covers a link planted after the tree is made.
- A#3 (MINOR): The copytree ignore list (*.py,*.pyc,*.mjs,__pycache__) is a second copy of the forbidden rule that disagrees with FORBIDDEN_* (missing .pkl/.pkl.gz, DONE.json, run_output*, tests/tools dirs, book names); e.g. data/customers/run_output.json is copied, then refused, and the tree is deleted, instead of being filtered out.
- A#4 (MINOR): Forbidden folder, name and suffix matching is case-sensitive: Tests/x.json, Company/x.txt or site/a.PY pass check().
- B#2 (MAJOR): R10: the deny-list covers only .py/.pyc/.pkl/.pkl.gz/.mjs (+__pycache__), yet data/customers is copied whole and the fixture shows build scripts live there. site/data/customers/_render.js, build.sh, x.ipynb, x.pyi, x.PY, or a .parquet/.pickle/.npz result is copied in and check() returns [] (when --book is absent or names differ). Allow only the file types the page reads instead of denying some.
- B#3 (MINOR): The book-name leg is off in the documented check command ('--check <dir>' with no --book, so book_names is empty), and it reads only the book's top level (iterdir), so the 'renamed run result still caught by name' guarantee does not hold where it is documented.
- B#4 (MINOR): The .py and __pycache__ fixtures are planted under explore/, which is never copied as a folder (only explore/index.html is), so the '*.py', '*.pyc' and '__pycache__' entries of ignore_patterns at tools/blind_worktree.py:226 can be removed with every test still passing; only _render.mjs exercises the filter.

## Done

Checked at HEAD 2026-11-02: all eight claims held. Fixed in `tools/blind_worktree.py`, each with a
test in `tests/tools/test_blind_worktree.py` that fails when its fix is reverted (eight mutations,
eight reds):

- **A#1/B#1 (both readers):** MANIFEST.json now names the book and the ruling only (`book.name`,
  `ruling.name`); no site, brief or absolute path. Test asserts the default-ruling manifest holds
  no `/`.
- **B#2, A#3:** copying is by allow-list (`READABLE_SUFFIXES`: html, json, css, svg, md), and
  anything under a forbidden folder or `__pycache__` is skipped at copy time; `check` refuses any
  other file type, so copy and check cannot disagree.
- **A#2:** a symlink in the source site is refused (tree removed), not followed.
- **A#4:** `check` compares folder names, file names and suffixes case-folded.
- **B#3:** the book's names are read recursively; the documented `--check` command now passes
  `--book`.
- **B#4:** the stray-file fixtures now sit in `data/customers`, the folder that is copied whole.
