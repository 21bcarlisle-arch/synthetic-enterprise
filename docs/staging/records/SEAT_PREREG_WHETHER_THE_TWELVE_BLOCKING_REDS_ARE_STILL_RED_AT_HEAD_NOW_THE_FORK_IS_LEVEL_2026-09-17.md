**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Class:** publish_gate_and_wedge · **Atom:** (Lane 0 delivery — close-the-fork-so-the-shared-tree-carries-the-publish-repair)

# Pre-registration: are the 12 `blocking_tests` still red at HEAD, now that `fork_state` reads `level`?

**Filed 2026-09-17, delivery seat, BEFORE running anything.** The drawn item's stated work — close a
3-behind/3-ahead fork — is spent (measured below, and that measurement needed no prediction: it is
four `git merge-base --is-ancestor` calls). What is NOT spent is the item's stated reason:
`last_clean_publish` is still `null`. This pre-registration is for the question that actually decides
whether it can move, whose answer I do not know.

## What the live record says (shared tree, `.publish_gate_state.json`, mtime 2026-09-17T17:28:13Z)

    fork_state        = 'level'          <- the fork the item was drawn to close IS closed
    last_clean_publish= None             <- and it did not move
    episode_failures  = 65
    total_red         = 21 · red_census = 'complete'
    red_at_head       = 'not_established'
    red_at_head_reason= "the red was measured at git=797c3164f and HEAD is now git=5696a3e23 --
                         that record describes a different commit's tree, so it says nothing
                         about HEAD."
    blocking_tests    = 12 node ids, ALL in ONE file:
                        tests/background/test_a_recorded_red_says_how_far_its_tree_stood_from_origin.py

The record is scrupulous — it refuses to claim the reds are at HEAD. So nobody currently knows.

## The question

Is `tests/background/test_a_recorded_red_says_how_far_its_tree_stood_from_origin.py` red at HEAD
(5696a3e23), measured in an isolated worktree at that exact commit?

## Predictions, written before the run

1. **The file is GREEN at HEAD.** Its own module docstring claims a repair landed 2026-09-17
   adopting the `fork_state` name, and 797c3164f (which carries `fork_state_no_red_refusal`, grep
   count 4) is an ancestor of HEAD. If that is true the 12 ids are stale citations against a tree
   that no longer exists, and the publisher is grading a record, not a repository.
2. **If it is green, `last_clean_publish` is held by something OTHER than these 12** — because
   `total_red` is 21, not 12. The 12 `blocking_tests` and the 21 `total_red` are **different
   counts**, and I have not established that the other 9 are the same file. Predicting the gate
   goes clean on the strength of 12 greens would be exactly the error of dividing two numbers
   without saying what each counts.
3. **The 12/12-legs-in-one-file signature is ONE shared cause, not twelve defects** — an import,
   a fixture, or a module-level name. If the file IS red, I expect a single root, and I expect
   fixing it to move all twelve together or none.

## What would refute each

1. Refuted by a non-zero pytest rc on that file at HEAD in a clean isolated worktree.
2. Refuted by `total_red` dropping to 0 on the next cycle after only these 12 turn green.
3. Refuted by the failures having distinct, unrelated causes across the twelve node ids.

## What I will NOT conclude

That a green run in this worktree means the publisher will publish. This worktree is not the tree
the publisher runs on, and a green here measures my HEAD, not its next cycle. The honest output of
a green is "these 12 citations are stale", which is a statement about the RECORD.
