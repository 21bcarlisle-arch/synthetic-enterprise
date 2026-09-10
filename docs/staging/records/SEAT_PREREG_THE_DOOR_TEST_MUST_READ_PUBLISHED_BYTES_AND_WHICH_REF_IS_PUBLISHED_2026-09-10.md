# SEAT PREREG — what changes when the baseline-comparison door test stops reading the working tree

**Severity:** RECORDED · **Lane:** H_harness

**Date:** 2026-09-10 (delivery seat, lane 0 draw)
**Claim:** `the-door-test-must-read-committed-bytes-so-an-unlanded-repair-goes-red`
**Subject:** `site/test_the_baseline_comparison_reaches_the_reader.py`
**Written BEFORE the change is made and before any mutation is run.**

---

## The premise, re-measured at draw time

The item cites `d15b7b543`, which is an ancestor of `origin/main`, and the local tree is **0
commits behind origin/main**. That commit landed **one path** — the SEAT RESULT document — and its
own status block says the code did not land. It has since: `tools/generate_value_arms_data.py` at
HEAD has no `RUN_OUTPUT_PATH` and carries `DASHBOARD_PATH` / `PUBLISH_PROVENANCE_PATH`, which is
items one and two. **The premise is spent for items one and two and live for this one** — the door
test still reads the working tree.

Baseline, measured before any edit: `133 passed, 1 skipped in 22.55s`. `git diff` and
`git diff --cached` are both empty for `site/data/value_arms.json` and
`site/capabilities/index.html`, so tree == index == HEAD for both subjects today.

## The one thing the item's wording settles, and the mechanism that agrees with it

The item says the test must be RED when the repair is *"present in the tree and absent from the
INDEX"*. That is not `HEAD`, and the reason it cannot be `HEAD` is in `tools/surgical_land.py`:

* `_make_standalone_repo` (`tools/surgical_land.py:730`) sets the extract's `.git/HEAD` to the
  **PARENT** commit and `read-tree`s the parent.
* `_build_extract` then `git add -A -- <the commit's paths>` (`tools/surgical_land.py:828`), so the
  extract's **index is the parent plus exactly this commit's paths** — i.e. the bytes the commit
  under gate would publish.

So inside the landing gate, `HEAD:site/data/value_arms.json` is the copy **before** the commit.
A control keyed to `HEAD` would go red on the very commit that repairs the feed and green again
only once someone landed the repair past a gate that refuses it — unlandable by construction, and
the flattering reading (a guard that refuses everything) passes every "does it refuse correctly"
test in the file. **The index is the published-bytes question in both contexts**: in a working tree
it equals HEAD unless something is staged, and in the gate it is this commit.

The residual hole is stated rather than hidden: a repair `git add`-ed and never committed reads as
published. Staging is the step immediately before committing and is transient; `HEAD` is not
available as a stricter answer for the reason above.

## Predictions — recorded before running any of them

| # | Prediction | Why I could be wrong |
|---|---|---|
| P1 | With the reader switched to the index and **nothing else changed**, the file is still `133 passed, 1 skipped`. | tree == index today, so the bytes are identical. Wrong if the door path being a temp file changes what the harness resolves. |
| P2 | **M1 (not-the-tree):** poison the WORKING-TREE `site/data/value_arms.json` so a named assertion would red; index untouched → **GREEN**. | Wrong if any read of the feed is left on the working-tree path. |
| P3 | **M2 (reachability):** `git add` that same poison into this worktree's own index → **RED**, and the named assertion is the one that fires. | Wrong if the reader is fail-open and quietly falls back to the tree, or if the poison is not one any assertion keys on. GREEN here means the whole change is vacuous, and a survived M2 is the finding, not a pass. |
| P4 | **M3/M4:** the same pair for `site/capabilities/index.html` (drop the `#arms-split` render) behaves the same way. | The door reaches the harness as a materialised temp file, which is a second mechanism and can fail on its own. |
| P5 | **M5 (fail-closed):** asking the reader for a path absent from the index FAILS with a message naming the path and the reason, and never skips or returns empty. | Wrong if `pytest.fail` is swallowed somewhere in the call chain. |
| P6 | Widening the same reader to the three auxiliary feeds (`dd_opening_arms.json`, `book_growth.json`, `capabilities_door.json`) leaves the file green today. | Wrong if any of the three is untracked or gitignored, in which case the widening is dropped and said so. |

**The figure I am pre-registering as NOT moving:** the door's rendered output on a clean tree.
Every byte read is identical today, so if any assertion's *value* changes, the change is not what
it claims to be and the difference is the finding.

## What done means, decided here rather than after

1. No assertion in the file takes a working-tree read of the two named subjects — enforced by a
   control **in the file** that reads its own source, not by my having looked.
2. The reader is proved live by an M2-shaped mutation, not only by M1.
3. The reader is fail-closed with a named reason.
4. It lands.
