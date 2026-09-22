**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# The replication census can now attribute its disagreement, and what it attributes it to is the instrument pinning

Drawn as `the-one-variable-floor-run-that-separates-the-instrument-from-the-seed-set`.

## The premise was HALF spent, and the half that remained is the half that reaches a reader

The item asked for two things. The first — run next12's twelve seeds at `4e7938f673` — was
**already done and already landed**, at `312bd55ff`, by the invocation that handed this item on.
Re-running it would have bought eleven hours of compute to re-derive a number on disk.

The second was not done, and that commit says so in its own message: *"No published figure moves
in this commit. The evidence reaches the record first; the census row that carries the repeat
count to the reader is the next increment."* That increment is this commit.

**An already-landed drawn item can still owe its explicit sub-asks.** The premise check said both
cited commits were ancestors of `origin/main` and invited a release; releasing on that alone would
have left the page exactly as silent as the item found it.

## What the fifth family buys, and it is not another data point

Four families each varied **both** the instrument (the tree the floor was drawn at) and the seed
set at once. So the census could say the selection sign is a property of which floor was drawn,
and could say nothing about **which of the two differences does it**. That is this project's own
rule on attribution, live on a published page: when a result moves and more than one thing
changed, you cannot attribute it.

The fifth family holds one variable fixed. It is next12's twelve seeds — the seed set of rows
three and four — drawn at `4e7938f673`, the tree of row one. It shares its seeds with two rows and
its tree with one.

**Its run was not a choice.** `value_cycle_ab_s1_three_arm.json` is refused for this floor by
`_floor_admission` on the books' own counts (70–72 accounts at end of window against 52–55; 164
settled against 154–155), so the 09-10 run is the only one it can be graded against — which is the
run row one is graded against. The tree is therefore the single moving part, and that fell out of
the bounds rule rather than being arranged. Printed at real inputs before the code was written.

## The five families, and the separation is clean

| family | tree | n | distinct | repeat another | choosing bound | sems | states |
|---|---|---|---|---|---|---|---|
| 9-seed 09-10 23:03 | `4e7938f67` | 9 | 8 | 1 | £613 | 2.85 | **negative** |
| 9-seed 09-10 21:34 | `9f0ab066f` | 9 | 7 | 2 | £311 | 0.55 | no sign |
| 12-seed 09-18 11:07 | `a178b56d6` | 12 | 12 | **0** | £1,558 | 0.69 | no sign |
| 12-seed 09-19 09:10 | `18327d977` | 12 | 12 | **0** | £1,563 | 0.17 | no sign |
| **12-seed 09-18 23:49 (NEW)** | `4e7938f67` | 12 | 10 | 2 | £379 | 3.14 | **negative** |

**Every family that repeats a draw is bounded more tightly than every family that repeats none.**
The widest repeating family is £613; the narrowest clean one is £1,558. No overlap, and a gap of
more than a factor of two. Both families that state a sign at all are drawn from the narrow group,
and both were drawn at `4e7938f673`.

This reproduces, independently and through the production grader, the 2026-09-22 finding landed at
`312bd55ff` — the arms move in lockstep, the residual is their difference, and a standard deviation
across pinned draws measures how often the instrument pinned rather than dispersion in the world.

## Why this makes the page say LESS, on purpose

Adding the fifth family alone would have been the wrong increment. It states **negative at 3.14
standard errors on twelve seeds** — the most decisive-looking selection reading on the page, and
narrow for a degenerate reason. Published without the repeat count beside it, the census would
have handed a reader a stronger negative than the evidence supports.

So the repeat count lands in the same commit, on every row including the ungraded ones, and
ambers the rows that repeat. The verdict itself does not move: `not_settled` before, `not_settled`
after. What moved is that the page can now say what the disagreement is **made of**.

## A control keyed to today's answer went red for the right reason, and is repaired

`test_the_strength_of_the_replicating_legs_is_measured_and_not_typed` dropped
`_REPLICATION_PAIRS[1:]` — a literal standing for *"the first family carries the strongest
replicating leg"*. True of the four families of the morning; false by the afternoon, because the
new family reaches 55.97 sems on the level leg against the first family's 49.45.

That is the exact shape the catalogue names: **a control pinned to today's answer goes red when
the code becomes more honest.** It now derives which family carries the strongest leg and drops
that one, so any family set with the property passes.

## What is NOT established

- **Why** the arms move in lockstep at the old tree and not at the new one. The mechanism is
  recorded at `312bd55ff`; the *cause in the pricing code* is not identified, and the trees are
  byte-identical across `simulation/`, `company/`, `saas/` and `tools/run_value_cycle_ab.py`.
- Whether the **wide** families are right and the narrow ones degenerate, or whether both are
  narrow readings of a quantity that genuinely sits near zero. The census reports the separation;
  it does not adjudicate it.
- `NOISE_FLOOR_PATH` — the floor the page's headline publishes — is still the worst case at 5 of
  18 draws repeating, and this commit does **not** move it. Moving the published floor on a width
  disagreement is the defect that block already refused once, and it is not made legitimate by
  this evidence. That remains open.

## Controls

- `tests/tools/test_the_signs_replication_across_families_is_graded_not_asserted.py` — the census
  holds one variable fixed in both directions (drop the new family and both legs red); uncountable
  is not zero repeats; the width comparison reaches **both** its answers and its unanswerable one.
- `site/test_the_baseline_comparison_reaches_the_reader.py` — the counts reach the reader beside
  the sign, and a repeating row ambers where a clean one does not. Both were observed red against
  the unchanged renderer and green after it, through the published-bytes harness.
