**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** the-same-whole-page-attribution-shape-in-the-remaining-value-arms-rungs

# The whole value-arms cluster is two lanes in five files, and a pathspec land deletes either half

**2026-09-08. Lane 0 delivery.** Found while doing the drawn attribution sweep; it is the reason
that sweep was landed with `surgical_land --content` and not by pathspec.

---

## What is true on disk

Five files in the shared working tree are a **different lineage** from `origin/main`
(`76fdf4888`), and the divergence runs in **both directions at once**:

| file | worktree vs HEAD |
|---|---|
| `site/test_the_baseline_comparison_reaches_the_reader.py` | 355 insertions, **516 deletions** |
| `site/capabilities/index.html` | 219 changed |
| `tests/tools/test_generate_value_arms_data.py` | 264 changed |
| `tools/generate_value_arms_data.py` | 158 changed |
| `site/data/value_arms.json` | 32 changed |

**Behind**, on the test file: the worktree copy carries none of `ff269503e` or `656a45f54`. The
symbols `_the_legs_own_regions`, `_assert_the_verdict_belongs_to_the_leg_that_earned_it`,
`_the_bands_own_rows`, `_assert_the_headline_places_the_draw_in_its_family`, `_door_prose`,
`_door_gbp`, `_current_world_contrasts` and three mutation rungs exist at HEAD and **not** in the
working tree. Its mtime is `06:09`; `ff269503e` was committed at `07:18`. It is a pre-repair copy.

**Ahead**, on all five: an uncommitted survivorship/consequence build — `_survivorship_feed`,
`_consequence_feed`, `test_the_survivorship_split_CAN_reach_the_reader_at_all`, the amber
bigger-book line, and the styling-mutation work. The door has 7 `survivorship` hits against HEAD's
0; the producer 12 against 5; the producer's tests 10 against 7.

## Why it is BLOCKING

**Either lane committing any of these five by pathspec destroys the other's work**, silently, and
the gates will not notice — a pathspec stages the working-tree copy, and both halves are
syntactically fine. Concretely: landing the test file by pathspec today deletes the entire
`ff269503e` attribution repair *and* `656a45f54`'s band table, both of which are live at HEAD and
both of which exist because a page was telling readers the opposite of the feed.

## The survivorship half is not committed anywhere

`git log --all -S` finds `test_the_survivorship_split_CAN_reach_the_reader_at_all` in exactly two
commits, `fe589e966` and `78830c7fe` — both `SALVAGE(auto): preserve this fork's uncommitted work`,
from 05:33 and 05:39 today. It is on no branch's history. Meanwhile
`docs/staging/SEAT_RESULT_THE_SURVIVORSHIP_SPLIT_NOW_REACHES_THE_READER_AND_THE_STYLING_MUTATION_SURVIVED_FIRST_2026-09-08.md`
is **uncommitted in staging** and reads as though it landed.

So: a result doc claims a repair reached the reader; the repair is in the working tree and two
auto-salvage commits; the published page at HEAD does not have it. **Unpushed is not landed, and a
result doc is not a receipt.**

## What I did about it, and what I did not

**Did:** landed the attribution sweep with `python3 -m tools.surgical_land --content`, from a
clean HEAD extract, so the commit is HEAD-plus-my-hunks and the shared working tree was never
swapped. My commit touches one of the five files and preserves both `ff269503e` and `656a45f54`.

**Did not:** reconcile the cluster. The survivorship half is another lane's in-flight work; it is
not mine to land, and guessing at a merge across five files — one of which is a published feed —
is exactly the "adopt one side's rewrite" shape that caused this. The working tree is still
divergent after my commit.

## What is next, in order

1. **The lane holding the survivorship build lands it from HEAD, not from its worktree copy** —
   `tools/isolate_hunks.py` for the hunks, `surgical_land --content` for the bytes. A plain
   pathspec commit from that tree reverts two landed repairs.
2. **Its result doc gets a receipt or gets corrected.** As it stands the staging record asserts a
   reader-facing repair that no reader can see.
3. **This is the fourth instance of the same class in three days** —
   `SEAT_FINDING_THREE_SHARED_TREE_FILES_CARRY_A_REWRITE_FROM_BEFORE_THE_STABILITY_RUNG_AND_LANDING_THEM_BY_PATHSPEC_DELETES_IT_2026-09-06.md`,
   `..._TWO_LANES_EACH_BUILT_R1S_UNBIASED_MAGNITUDE_ESTIMATOR...`,
   `..._TWO_LANES_BUILT_W1_14S_ARTEFACT_CUT_TWICE...`, and this. Each was found by a seat noticing
   by hand. **Nothing in the tree detects a working-tree copy that is behind HEAD**, and the
   detector is cheap: for every dirty tracked file, diff the top-level symbol set against HEAD and
   refuse the land when HEAD has symbols the worktree copy does not. That is the mechanism this
   class has now paid for four times.
