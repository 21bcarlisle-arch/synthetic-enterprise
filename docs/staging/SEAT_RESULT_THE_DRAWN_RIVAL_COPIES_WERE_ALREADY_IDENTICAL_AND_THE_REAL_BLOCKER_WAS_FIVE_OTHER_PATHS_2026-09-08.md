**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** (Lane 0 delivery — two-rival-copies-of-the-stale-copy-refusal-hold-the-tree-behind-origin-and-the-publisher-dark) · **Class:** `publish_gate_and_wedge`

# The drawn rival copies were already identical, and the real fast-forward blocker was five other paths

**Lane 0 claim:** `two-rival-copies-of-the-stale-copy-refusal-hold-the-tree-behind-origin-and-the-publisher-dark`
**Date:** 2026-09-08
**Severity:** RECORDED (the drawn premise; the work it named is spent)
**Class:** `publish_gate_and_wedge`

*(Header line added 2026-09-09: this document stated its severity but carried no `**Lane:**` field,
so `parse_severity_file` read it UNCLASSIFIED — and an unreadable severity shows NO lane clear, so
it was refusing level raises in every lane, including `W2_customer_generator`. The severity it
always stated is RECORDED; the lane is the harness lane its class and its sibling results carry.)*

---

## The premise as drawn, and what it measures now

The item named two paths as rival implementations holding the tree behind origin:

| path | drawn as | measured at draw time (this turn) |
|---|---|---|
| `tools/stale_copy_refusal.py` | working copy +180/-16 vs HEAD; origin's +98/-10 | **identical at worktree, HEAD and `origin/main`** — `git diff` empty both ways |
| `tests/tools/test_stale_copy_refusal.py` | +190 here, +62 on origin | **identical at worktree, HEAD and `origin/main`** |

Both commits the item cites — `a9f3288c8` and `0caf9ab52` — are ancestors of `origin/main`
**and of HEAD**. The repair landed by another route and the shared tree already carries it.
The premise is **spent**: there is no symbol set to discriminate, no hunk to isolate, no
capability that exists only here.

The item was written 11.8 hours before it was drawn. `.publish_gate_state.json` still carries
the refusal that named those two paths — `alerted_at` 1788891958, i.e. the state file is the
stale artefact, not the tree.

## What was actually holding the fast-forward

`HEAD` was **3 behind `origin/main` and 0 ahead** — a pure fast-forward, not a fork. (The
refusal's own evidence says "this tree holds 1 commit(s) of its own"; that commit has since
reached origin, so the fork closed itself and only the blocked FF remained.) The block was
five dirty paths that `origin/main` also touches:

| path | state | what it was | disposition |
|---|---|---|---|
| `docs/staging/SEAT_FINDING_THE_PROOF_PAGE_TOLD_A_READER_A_LARGER_FIGURE_WAS_SMALLER_2026-09-08.md` | untracked | **byte-identical** to origin's incoming copy | removed — origin brings it |
| `docs/staging/SEAT_FINDING_THE_PUBLISHERS_REMEDY_REPORTS_LEVEL_ABOUT_THE_WORKTREE_IT_WAS_RUN_FROM_2026-09-08.md` | untracked | **byte-identical** to origin's | removed — origin brings it |
| `docs/staging/SEAT_PREREGISTRATION_WHAT_PROMOTING_THE_09_08b_RUN_MAKES_THE_PROOF_PAGE_SAY_2026-09-08.md` | untracked | **byte-identical** to origin's | removed — origin brings it |
| `site/data/value_arms.json` | staged + modified | a **re-publish by the OLD generator** | reverted to HEAD bytes; regenerate after FF |
| `site/test_the_baseline_comparison_reaches_the_reader.py` | modified | **+157 lines of unlanded work** | landed |

## The one that mattered, and why reverting it would have been the wrong call

`site/test_the_baseline_comparison_reaches_the_reader.py` is the shape memory calls *a
working copy that would revert a landing*. Against `origin/main` it looks like a reversion:
origin's `4c983635b` replaced the literal `assert "SMALLER advantage" in advantage_region`
with a comparison **derived** from the two figures the feed carries, and the working copy
still asserts the literal. Against **HEAD** it is purely additive — because HEAD does not
have origin's fix yet. Two hunks, both the same lane's work:

```
1  @@ base line 103    +          "arms-composition", "arms-redraw", "arms-legs-first")
2  @@ base line 4037   +   (157 lines: six tests)
```

So the correct move was **land on HEAD and let the three-way merge carry both**, not revert.
Isolating against HEAD and landing there means the merge base is HEAD, my side adds the
panel and the tests, origin's side rewrites the direction block, and the two regions do not
overlap. Reverting would have destroyed 157 lines of a control to avoid a reversion that the
merge was always going to resolve correctly.

**The general form: a working copy that reverts origin can be purely additive against HEAD,
and which of the two you diff against decides whether you preserve the work or destroy it.**
Diff against HEAD to decide what to LAND; diff against origin only to predict the merge.

## The pair, and why it is a pair

The control asserts a panel `arms-legs-first` renders. Neither HEAD nor `origin/main` has
that id in `site/capabilities/index.html`; the shared tree's uncommitted copy does, in three
hunks (+111). Landing the control alone would have committed a red. Landing the renderer
alone would not have cleared the FF block, because origin does not touch `index.html`.
The landable unit is the three files together — renderer, control, and the design note the
control's prose points at (`docs/design/THE_LEVEL_LEG_IS_AVAILABLE_TO_THE_FLAT_RULE_SUPPLIER_2026-09-08.md`,
a reachability edge under the prose-path rule).

This is the cluster `SEAT_FINDING_THE_WHOLE_VALUE_ARMS_CLUSTER_IS_TWO_LANES_IN_FIVE_FILES_AND_A_PATHSPEC_LAND_DELETES_EITHER_HALF_2026-09-08.md`
names. Half of it — `tools/generate_value_arms_data.py`, its test, and the data half — is
already on origin. This lands the reader-facing half.

## `site/data/value_arms.json`: reverted, and it is not a loss

The worktree copy has a **later** `generated_at` (22:44:13Z) than origin's (22:17:15Z) and
**fewer fields**: it lacks `superseded_value_advantage_gbp` and the whole
`differs_from_the_superseded_panel` block, and its `against_the_superseded_panel` prose
asserts "DIFFERENT WORLDS" where origin's derives which attributes differ. It was produced by
the pre-`4c983635b` generator at a later wall clock. Keeping it would have re-armed exactly
the defect origin just fixed — the page telling a reader a larger figure was smaller — and it
is the newest-run-unsatisfies-the-staleness-control shape.

Preserved at `/tmp/value_arms_worktree_republish.json` for this turn only. It is a derived
artefact: the honest recovery is to re-run `tools/generate_value_arms_data.py` from the
merged tree, which is a publisher step, not a salvage.

## What is next

1. `python3 -m background.origin_reconcile` — the gated merge in an isolated worktree, now
   that no incoming path is dirty.
2. Regenerate `site/data/value_arms.json` from the merged tree so the page carries origin's
   derived direction **and** the legs-first split.
3. The FF-blocker set was five paths and the drawn item named none of them. The item was
   built from `.publish_gate_state.json`'s `failures[]`, which is a **historical** array —
   `alerted_at` predates two of the three commits origin has since taken. A draw that reads
   the failure log rather than re-measuring the tree will keep naming spent paths. That is a
   separate finding and is not fixed here.
