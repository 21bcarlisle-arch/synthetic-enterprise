**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `publish_gate_and_wedge` (primary) · `uncommitted_and_orphaned_work` (secondary)

# The publisher is wedged by an uncommitted test leg whose own producer fix was never regenerated

**Claim:** `the-publisher-cycle-the-withdrawal-item-still-owes-after-its-continuation-was-retired`
**Pre-registration:** `SEAT_PREREG_WHICH_RED_ACTUALLY_HOLDS_THE_PUBLISHER_AT_HEAD_2026-09-23.md`
(same room) — **its prediction was refuted, and the refutation is the finding.**

## Both reds the item named are spent, and neither was ever the live cause

The drawn item named `tests/design/test_atom_notes_store.py::test_declarations_match_the_store`,
citing `total_red: 1` in `docs/observability/.publish_gate_state.json`. Measured on a clean
worktree at `2f8f6a8fd`: **24 passed**. The state file had already said so itself —
`red_at_head: "not_established"`, because the red was recorded at `4da626379`.

The prereg then predicted the *later* refusal in the same file
(`liveness_surface_refusal`, stamped at HEAD, naming
`site/test_the_flat_churn_belief_reaches_the_reader.py::test_the_unsourced_threshold_is_MARKED_where_a_reader_meets_it`)
would reproduce on a clean tree. It does not: **14 passed**. Refuted.

The tell was in the traceback the state file carried: `…py:399: AssertionError`. Line 399 of that
file at HEAD is inside a docstring. **The failing file was never HEAD's.**

## What is actually holding it, read off the shared tree at 07:40

`docs/observability/sim-runner-log.md`, 2026-09-23 06:31 UTC:

> `[process_run] Publish commit REFUSED by the hook chain -- blocking test(s): FAILED
> site/test_the_flat_churn_belief_reaches_the_reader.py::test_the_unsourced_threshold_is_MARKED_where_a_reader_meets_it`

The assertion that fired exists in no commit:

```python
assert "is_there_a_bill_level_at_which_switching_rises" in origin, (
    "the caveat names no reading. A gap filed and then orphaned is a gap nobody can act on…")
```

Four paths, and the shape is in which of them are dirty:

| Path | `git status` | Names the reading? |
|---|---|---|
| `site/test_the_flat_churn_belief_reaches_the_reader.py` | **dirty** — the new third leg | demands it |
| `tools/churn_belief_size_response.py` | **dirty** — the new origin sentence | **yes** |
| `docs/observability/churn_belief_size_response.json` | **clean** | **no** |
| `site/data/value_arms.json` | **dirty** — regenerated 05:40 | **no** |

`tools/generate_value_arms_data.py:15260` reads `knee.get("the_thresholds_own_origin")` from the
**stored** `docs/observability/churn_belief_size_response.json`, not from the producer. So the
producer was edited, its derived artefact was never re-run, and `value_arms.json` was then
regenerated *from the stale intermediate* — carrying the old caveat forward under a fresh
`generated_at`. The lane's own new test leg then fails against the lane's own stale output.

**A red `site/**` test refuses every commit in the site lane.** The publisher commits from the
shared working tree, so it eats a refusal that belongs to nobody's commit. That is why
`episode_clean_publishes` is 0 and `last_clean_publish` has stood at 2026-09-21 19:15 for two days.

## Why no control saw it

`tools/published_feed_regeneration_check.py` is the module built for exactly "a published feed no
longer matches its generator". It **clones the tree at HEAD** and regenerates there — deliberately,
to avoid writing the shared tree. At HEAD every artefact here agrees, because the producer edit is
uncommitted. **The check is blind by construction to a working-tree-only producer edit, which is
precisely the state that wedges the publisher**, because the publisher gates the working tree and
the check gates HEAD. The two look at different trees and only one of them can refuse a commit.

It also does not carry `churn_belief_size` at all (`grep -c churn_belief` → 0), so even a
working-tree variant would need this chain added.

## Disposition — NOT taken, and why

The remedy is one command: re-run `tools/churn_belief_size_response.py` so the stored JSON carries
the sentence its producer already writes, then regenerate `value_arms.json`. **I did not do it.**

Every byte of it belongs to the live claim
`land-the-bill-stress-knee-refutation-before-it-is-lost`, which already holds
`site/data/value_arms.json`. All three files are dirty **in place** in the shared tree; my worktree
carries HEAD's copies, so landing any of them from here would revert that lane's work rather than
complete it. Doing their half-applied change under my id is the two-ids-one-piece-of-work cost the
draw warned about, pointed the other way.

**So this item is blocked, and on something it never named.** One publisher cycle cannot complete
until that claim finishes its change — not because of either red the item enumerated, both of which
were green before I started.

## What done means, restated for whoever takes it next

Not "the named reds are green" — they are, and the publisher is still wedged. It is:
`docs/observability/.publish_gate_state.json` shows `episode_clean_publishes > 0` with
`last_clean_publish` later than 2026-09-23 06:31, from a tree level with origin.
