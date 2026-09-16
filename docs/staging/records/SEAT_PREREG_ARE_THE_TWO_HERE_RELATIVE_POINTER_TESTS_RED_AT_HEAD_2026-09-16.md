# PRE-REGISTRATION — are the two `here-relative pointer` tests red at HEAD, or only in the shared tree?

- **Written:** 2026-09-16, before running anything.
- **Seat:** delivery (isolated worktree `/var/tmp/se-seat-executor`, detached at `c660084bb` == `origin/main`).
- **Claim id:** `the-checkout-must-fast-forward-so-the-publishers-green-commit-can-land`

## Why this measurement exists

`docs/observability/.publish_gate_state.json` records `total_red: 2`, `blocking_tests`:

- `site/test_a_here_relative_pointer_has_one_home.py::test_no_here_relative_pointer_is_composed_into_more_than_one_region`
- `site/test_a_producers_here_relative_pointer_has_one_home.py::test_no_feed_FIELD_that_reaches_two_regions_carries_a_here_relative_sentence`

and, beside them, `red_at_head: "not_established"` with the reason *"the red was measured at git=5238d3461 and HEAD is now git=a1aed184f — that record describes a different commit's tree, so it says nothing about HEAD."*

The record is honest that it does not know. Nothing in the tree can answer it, because the
pre-commit gate runs in the **shared working tree**, which carries three other lanes' uncommitted
edits. This worktree is clean and sits exactly on `origin/main`, so it is the only vantage from
which the question has a single-valued answer.

## The question

Run both tests, unmodified, at `c660084bb` in a clean checkout with no other lane's uncommitted work
present. Are they red?

## Prediction, recorded before the run

**I predict they are RED here too** — i.e. the wedge is a genuine defect at HEAD, not shared-tree
pollution. Confidence: weak-to-moderate (~60/40).

Reasoning: `episode_failures: 40` with `episode_clean_publishes: 0` and `wedge_since` ~23h earlier.
Pollution from a sibling lane is usually transient — it clears when that lane lands or resets. A red
that survives 40 consecutive publish attempts across at least four different HEAD commits
(`5238d3461` → `8fc4b4c02` → `a1aed184f` → `c660084bb`) is more consistent with something committed
than with something uncommitted.

**The named alternative, and it is live:** the reds are shared-tree pollution only, and both tests
are GREEN here. This is a known class in this project — *"the pre-commit test gate runs in the
shared working tree so another lane's test pollution wedges every commit"*. Three of the paths this
item named (`tools/couple_value_based_pricing.py`, its test, and
`test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py`) are **still dirty in the
shared tree right now**, so a pollution explanation has a concrete, named carrier.

## What each outcome means, decided before the answer is known

| Outcome | Reading | What I do next |
|---|---|---|
| Both RED here | Real defect at HEAD. The publisher is correctly refusing. | Fix the defect; that is the work. |
| Both GREEN here | The wedge is shared-tree pollution. The publisher refuses on another lane's uncommitted bytes. | The defect is that the gate's subject is the working tree; file it, and the remedy is `refresh_to_head`/isolation, not a code fix to the site tests. |
| One of each | The two are not one wedge and must not be treated as one. | Split them; measure each separately. |

## The trap I am deliberately avoiding

`red_at_head` is `not_established`, and the flattering reading is "someone else already broke it, so
it is not mine." The unflattering reading is "it is real and 40 publishes have been correctly
refused." I am recording the prediction now so that whichever way it lands, the answer cannot be
back-fitted. Per CLAUDE.md: *a prediction filed after the answer is not a prediction.*
