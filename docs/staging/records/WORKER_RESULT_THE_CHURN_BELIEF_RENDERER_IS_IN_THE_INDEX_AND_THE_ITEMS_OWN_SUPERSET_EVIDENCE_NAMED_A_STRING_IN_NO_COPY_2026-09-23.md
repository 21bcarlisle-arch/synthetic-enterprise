# The churn-belief renderer is in the index, and the item's own superset evidence named a string in no copy

**Severity:** RECORDED · **Lane:** H_harness

`site/test_the_flat_churn_belief_reaches_the_reader.py` was 3 failed / 12 passed at HEAD. It is
15 passed now, and the whole `site/` tree is 925 passed / 38 skipped. The cause was exactly what
the item said: the door boots the INDEX copy via `published_blob`, and the renderer for
`legs_the_belief_hears`, `legs_the_belief_is_deaf_to`, `share_the_belief_hears` and the per-rate
DEAF EDGE was on disk and not in the index.

Paths: `site/capabilities/index.html`, `site/test_the_flat_churn_belief_reaches_the_reader.py`.

## The item's verification instruction would have destroyed this lane's work

The working copy of `site/capabilities/index.html` (mtime 20:34) is **older** than the last landing
on its path (`d08b1b104`, 20:42) — the `predates_landing` shape, where `--content` lands a revert
and the licensed door is `refresh_to_head`. The item said it had checked, and offered the check:

> the landed clearing-verdict text (*"because the styling is a fact about the verdict"*) is present
> in the working copy AND the index

**That string is in neither.** `grep -c` returns 0 against the working copy and 0 against
`HEAD:site/capabilities/index.html`. It is in no copy of the file at all.

The conclusion the item drew from it was nonetheless correct, and this matters: a reader who ran the
offered check would have got 0, read it as *"the clearing verdict is absent, so this copy IS a
revert"*, and reached for `refresh_to_head` — which would have discarded both live hunks. **The
evidence line was wrong in the direction that inverts the verdict it vouches for.**

## What actually establishes the superset

Two measurements, neither of them a string the item invented:

1. **Every line `d08b1b104` added is present in the working copy.** Its 25 added lines, checked
   `grep -Fqx` one at a time: 0 missing. The diff against HEAD is 54 insertions / 19 deletions in
   2 hunks, both confined to the churn-belief block, reverting no clearing-verdict line.
2. **`d08b1b104`'s own commit message says so.** *"Lands two of the four hunks in that file. Hunks 3
   and 4 are the churn-belief lane's live work and are left in the shared tree for them — landing
   the file whole would red four doors of theirs that are still at HEAD."* The landing author
   deliberately left these hunks. `isolate_hunks --survey` agrees: 2 hunks, both this lane's.

This is the memory's *"a copy OLDER than the last commit to its path can be a CONCURRENT FORK, not a
revert"* with the fork's other side having written down that it forked. **When an item vouches for a
superset, ask the landing's own added lines and the landing's own message — not a quoted string,
which is the one form of evidence that can be fabricated without the fabricator noticing.**

## The ratchet red is not this commit's

`tests/architecture/test_static_quality_ratchet.py` is red in the shared worktree: F401 269 against
a 264 baseline. Attributed per path rather than assumed: **neither of this commit's paths contributes
an F401.** The test file is 0 in the worktree and 0 at HEAD's blob; the HTML is not Python. The 5 are
other lanes' dirty files, which is what HEAD's own `8298f6da7` already recorded — *"the red is
worktree-local and blocks no commit"* — and `surgical_land` gates a clean extract of the tree the
commit would create, which does not contain them.

## The renderer was half the commit, and the gate is what said so

The item's DONE clause — *"those three green with the file in the index"* — was satisfied with the
HTML staged and **the gate still refused**, with four reds rather than three. That is not a
contradiction; it is the two oracles disagreeing because they read different trees.

`published_json` reads the INDEX copy, so locally the door saw a `site/data/value_arms.json` that
was staged-but-never-committed. `surgical_land` gates a clean extract of the tree the commit would
create — HEAD plus the named pathspec — and the feed was not in that pathspec, so the extract got
**HEAD's** copy. HEAD carries none of `legs_the_belief_hears`, `what_was_withdrawn_and_why`,
`deaf_edge_by_rate` or `is_there_a_bill_level_at_which_switching_rises`; the index carries all four.
A renderer for fields the feed does not have is four reds, and the fourth
(`test_the_unsourced_threshold_is_MARKED_where_a_reader_meets_it`) never appeared in the local run
at all.

This is the memory's *"a control reading a GENERATED artefact off disk is GREEN in the worktree and
RED in the gate — swap ONLY the artefact"*, met from its other side: the artefact was not stale on
disk, it was **unlanded**, and the local index hid that by being the thing both the producer and the
door happened to agree on. **When a door reads a feed through the index, staging the reader proves
nothing about the commit — the feed is part of the unit or the gate is the first thing that finds
out.** The feed landed here is the 20:24 producer run, not the 13:37 copy that was in the index: it
is the later of the two, carries the same four keys, and additionally states the
`BILL_STRESS_MAX_RATIO` ceiling that the prose beside it now depends on.

## What is still owed

The item's real exit test is the third clause, not the green: *"`last_clean_publish` advances past
2026-09-21 18:15 UTC"*. The three reds were the site lane's refusal and the site lane refuses every
commit touching `site/`, so this landing removes the blocker — but a figure moving on origin is a
separate observation, taken after the publisher runs.
