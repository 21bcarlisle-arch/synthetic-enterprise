**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PREREG — which red actually holds the publisher, measured on a CLEAN tree at HEAD

**Written 2026-09-23, before running anything whose answer is not already in hand.**
**Claim:** `the-publisher-cycle-the-withdrawal-item-still-owes-after-its-continuation-was-retired`

## What is already established, not predicted

The drawn item names
`tests/design/test_atom_notes_store.py::test_declarations_match_the_store` as the cause of the
wedge, citing `total_red 1` in `docs/observability/.publish_gate_state.json`.

That file says so itself, and it also says the citation is void:

```
"red_at_head": "not_established",
"red_at_head_reason": "the red was measured at git=4da626379 and HEAD is now git=2f8f6a8fd --
                       that record describes a different commit's tree, so it says nothing
                       about HEAD."
```

Run on a clean worktree at `2f8f6a8fd`: `tests/design/test_atom_notes_store.py` — **24 passed**.
So the item's named cause is spent. This is not a prediction; the state file pre-declared it and
the run agreed.

## The prediction

The same state file carries a LATER record — `liveness_surface_refusal`, ts 1790145074, and its
`git_hash` is `2f8f6a8fdd805f26d8244d3a1f998090b353b765`, **which is HEAD**. It names a different
red, in a different lane:

```
site/test_the_flat_churn_belief_reaches_the_reader.py::
    test_the_unsourced_threshold_is_MARKED_where_a_reader_meets_it
```

with the site lane's own note that a red `site/**` test can never wedge the `tests/` publish gate
but refuses the COMMIT, which is how it becomes `commit_did_not_land`.

That refusal was measured on the SHARED tree, which the draw's own path check grades **dirty** on
`site/data/value_arms.json` and on `.publish_gate_state.json` itself. A red measured on a dirty
tree can be another lane's uncommitted edit; that is artefact locality, not a HEAD defect.

**I predict: the site test is RED in a clean worktree at `2f8f6a8fd` as well** — i.e. the cause is
in committed bytes, not in a neighbour's dirty file. Confidence: moderate. The competing outcome,
which would refute me, is that it passes here, and the shared tree's red is then somebody's
in-place edit to `site/data/value_arms.json` and none of my business.

**Either way the item's stated cause is wrong**, and re-deriving the four reds the original
withdrawal item enumerated would have measured nothing. Recorded before the run.

## What done means for this claim

Not "the four old reds are green". The publisher cycle completes when a commit made from a tree
level with origin passes the whole hook chain — `tests/` gate AND the site lane — and reaches
origin. One such commit is the deliverable. The result goes beside this file.
