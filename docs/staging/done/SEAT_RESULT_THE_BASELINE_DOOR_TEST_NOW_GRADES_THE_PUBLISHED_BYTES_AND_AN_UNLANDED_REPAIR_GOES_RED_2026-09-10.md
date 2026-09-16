# SEAT RESULT — the baseline-comparison door test grades the PUBLISHED bytes, and the index is the only ref that can be the subject

**Severity:** RECORDED · **Lane:** H_harness

**Date:** 2026-09-10 (delivery seat, lane 0 draw)
**Claim:** `the-door-test-must-read-committed-bytes-so-an-unlanded-repair-goes-red`
**Pre-registration:** `docs/staging/records/SEAT_PREREG_THE_DOOR_TEST_MUST_READ_PUBLISHED_BYTES_AND_WHICH_REF_IS_PUBLISHED_2026-09-10.md`
(written before any of this was built or measured; every prediction it carries is graded below)
**Follows:** `docs/staging/SEAT_RESULT_THE_PUBLISHED_SUPPLIER_CHECK_NOW_READS_ONLY_COMMITTED_BYTES_AND_THE_ITEMS_OWN_PAIRING_WOULD_HAVE_REFUSED_ON_EVERY_PUBLISH_2026-09-10.md`

---

## The premise, re-measured before starting

The item's cited commit `d15b7b543` is an ancestor of `origin/main` and the local tree is 0 commits
behind. That commit landed **one path** — the SEAT RESULT document — and its own status block says
the code did not land. **It has since:** `tools/generate_value_arms_data.py` at HEAD carries
`DASHBOARD_PATH` and `PUBLISH_PROVENANCE_PATH` and has no `RUN_OUTPUT_PATH`.

So the premise is **spent for items one and two** and **live for this one**: the door test was
still reading the working tree. Item three was the part left to do, and it is done.

## The question the item's own wording settles, and the mechanism that agrees

The item says RED when the repair is *"present in the tree and absent from the INDEX"*. That is not
`HEAD`, and `tools/surgical_land.py` is why it cannot be:

* `_make_standalone_repo` (`tools/surgical_land.py:730`) sets the gate extract's `.git/HEAD` to the
  **PARENT** commit.
* `_build_extract` then stages exactly the commit's paths (`git add -A -- <paths>`,
  `tools/surgical_land.py:828`).

Inside the landing gate, therefore, `HEAD:site/data/value_arms.json` is the copy from **before** the
commit. A control keyed to `HEAD` **goes red on the very commit that repairs the feed** and can only
be landed past a gate that refuses it — unlandable by construction. It would also pass every "does
it refuse correctly" test in the file, because a guard that refuses everything refuses correctly:
this project's most-entered trap, and it would have been entered again by taking "committed bytes"
at face value.

The index answers the same question in both places — in a working tree it is HEAD unless something
is staged; in the gate it is precisely the bytes this commit publishes. **The residual hole is
stated rather than hidden:** a repair `git add`-ed and never committed reads as published. That is
one transient step wide, against a `HEAD` reading that cannot be landed at all.

## What changed

`site/test_the_baseline_comparison_reaches_the_reader.py`. The five `Path` constants are gone and
are now relative-path strings read through `_published_blob(rel)` → `git show :<rel>`, fail-closed
with the path and git's error in the message. The door is materialised from the index into a scratch
file for the node harness. The widening from the item's two named subjects to all five (the three
auxiliary feeds the door also boots from) was made because the property — *every input to this
control is a published byte* — is one a guard can state, and "two of the five" is not; all three are
tracked, un-ignored and clean, and P6 confirmed it costs nothing.

Four new controls, and the reason each exists rather than a comment saying "read the index":

| control | what it grades |
|---|---|
| `..._returns_the_INDEX_copy_when_the_working_tree_disagrees` | a scratch repo whose index and disk **deliberately disagree**. On this tree they agree almost always, so a control that only ran here would pass whatever the reader read — including the file it exists to stop reading. |
| `..._FAILS_when_there_is_no_published_copy_rather_than_reading_the_file` | the file is on disk and uncommitted — the defect at its most complete. Refusal must name the path, say why, and never hand back the bytes beside it. |
| `test_no_subject_of_this_file_is_read_from_the_working_tree` | the relapse, by AST over this file's own source. Subjects derive from the `*_REL` constants, so a sixth feed is covered the day it is added. Non-vacuity leg runs the scanner over the exact line the file used to carry, **before** reading its silence about the file. |
| `..._the_door_the_harness_boots_is_the_published_one` | plumbing, and named as plumbing: materialised bytes are git's bytes. |

## R15 — six mutations, each run and reverted

The pair is the control. **The first leg of each pair alone is satisfied by a reader that reads
nothing at all**, which is why neither is reported without the other.

| # | mutation | result |
|---|---|---|
| F1 | `available: false` into `site/data/value_arms.json`, **working tree only** | **137 passed** — the tree is not the subject |
| F2 | the same poison `git add`ed so the index carries it | **60 failed, 67 errors** — the index is |
| D1 | blank the `#arms-legs-first` render and rename its element in the door, **working tree only** | **137 passed** |
| D2 | the same poison staged | **9 failed** |
| R1 | `_published_blob` returns `(base / rel).read_text()` | index rung + fail-closed rung red |
| R2 | `_published_blob` falls back to the working tree when git cannot answer | fail-closed rung reds (DID NOT RAISE) — this is the fail-open that would restore the whole defect |
| R3 | empty the AST guard's subject list | its **own non-vacuity leg** reds, not its silence |
| R4 | restore `DOOR = SITE / "capabilities" / "index.html"` | the guard names the line: `line 121 (index.html)` |

Both poisoned files were restored from a pre-run copy and verified by `md5sum -c`; the index was
returned with `git reset HEAD -- <path>`; `git status` is clean for both. The staging was safe to do
at all because a linked worktree has its **own** index (`.git/worktrees/se-seat-executor/index`),
which was checked before anything was staged.

## The predictions, graded

| # | prediction | outcome |
|---|---|---|
| P1 | still `133 passed, 1 skipped`, plus the new controls | **HELD** — 137 passed, 1 skipped (133 + 4) |
| P2 | tree-only feed poison → GREEN | **HELD** |
| P3 | staged feed poison → RED | **HELD** |
| P4 | the door pair behaves the same | **HELD** |
| P5 | fail-closed names the path | **HELD**, and proved by R2 rather than by reading it |
| P6 | widening to the three auxiliary feeds stays green | **HELD** |
| — | *the pre-registered figure that must NOT move:* the door's rendered output on a clean tree | **HELD** — no assertion's value changed; the count moved only by the four new controls |

Nothing was refuted. That is a weaker result than a refutation and is recorded as such: every byte
read was identical on a clean tree, so P1–P6 were the low-information half and F2/D2/R2 are where
the evidence is.

## What this does NOT do

* It does not make the **page** correct. The £67.48 divergence the previous result measured is
  still not what the committed feed says, and this control now says so out loud instead of grading
  a repair nobody has met. **That red, when it appears, is the mechanism working.**
* It covers this door only. Every other `site/test_*_door.py` still takes the working tree as its
  subject, and the same one-line relapse is available in all of them. The reader and its guard were
  written to be liftable, and lifting them is the next piece — handed off.
