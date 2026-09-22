**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0

# The eighteen-seed family is spliced across an objective change, and the twenty-four-seed price came off the splice

**Filed** 2026-09-17 · worker · lane 0 delivery
**Item** `the-selection-leg-is-six-seeds-short-of-a-sign-and-its-point-estimate-is-negative`

> **The drawn item's second named defect — `floor_legs_ran_on_one_tree: false` — was treated here
> as a provenance caveat. It is not. Asked what actually differs between the two trees the
> eighteen seeds were drawn on, the answer is `company/pricing/value_based_renewal.py`, and the
> difference is the departure cost: the nine seeds in `...20260909b.json` priced under an objective
> that charged the arm NOTHING for causing a departure, and the nine in `...20260910b.json` priced
> under one that charges it £27.50.** The family is not eighteen draws of one quantity. It is nine
> and nine of two. `selection_gbp` — the value of the choosing — is exactly the quantity that
> change moves.

---

## The two halves, printed

| family | n | mean `selection_gbp` | sd | sem | sems from zero | bar | states a sign |
|---|---|---|---|---|---|---|---|
| `20260909b` — `c066c114b`, **no** departure cost | 9 | **−£1,078.17** | 1,810.50 | 603.50 | 1.787 | 2.306 | no |
| `20260910b` — `9f0ab066f`, **with** departure cost | 9 | **−£170.09** | 931.78 | 310.59 | 0.548 | 2.306 | no |
| pooled — what the page publishes | 18 | −£624.13 | 1,472.89 | 347.16 | 1.798 | 2.110 | no |

The halves' means are £908.08 apart — **1.45 times the pooled mean the item is trying to sign** —
and their spreads differ by a factor of two. A Welch test on 9 and 9 returns p = 0.21, so this
does not establish that the halves differ; it establishes that **nothing here can treat them as one
quantity**, and that the published point estimate is carried by the half drawn under a superseded
objective.

## What that does to the item's own arithmetic

`seeds_needed_to_state_a_sign: 24` is computed from the pooled mean and the pooled deviation. Both
are properties of the splice. Re-priced per half, by the same method the artefact uses (solving for
the n where |mean| / (sd/√n) clears Student's t on n−1):

| the family you are pricing | seeds needed to state a sign |
|---|---|
| pooled 18 (what the page says) | **24** |
| superseded objective alone | 14 |
| **current objective alone** | **118** |

So the six-seeds-short framing is an artefact. On the objective the company actually prices under,
the sign is roughly **a hundred seeds** away, not six — and at ~3.8 hours for three seeds on this
guest that is not a draw anyone is going to finish by adding to the queue.

## PRE-REGISTRATION — written before the fifteen seeds in flight return

Two legs were already drawing when this item was picked up: three seeds (`1234567,2345678,3456789`,
with `discrimination_auc`) at `e63aef075`, and twelve (`3100001`–`3100012`) chained behind them at
`a178b56d6`. Neither had produced a row at the time of writing.

**Prediction: the refolded family will NOT state a sign, at any of the three sizes it could be
folded to.** If the fifteen resemble the current-objective half (mean −£170, sd 932):

| fold | n | sem | sems from zero | bar | states a sign |
|---|---|---|---|---|---|
| new seeds only | 15 | 240.58 | 0.707 | 2.145 | no |
| new + the current-objective nine | 24 | 190.20 | 0.894 | 2.069 | no |
| everything, splice and all | 33 | 162.20 | 1.049 | 2.037 | no |

The prediction is filed here so the result can refute it. If the fifteen come back near −£1,000
instead, this write-up is wrong about which half is representative and that is the finding.

**And the fold to build is the 24 — new seeds plus `20260910b` only.** It is the largest family
that is one objective, it names a book (`floor_book_identity` has written one since `c9bd2eae7`),
and it is the size the item asked for. Folding all 33 buys nine seeds of a different pricing rule.

## The second measurement: the two in-flight trees are NOT a repeat of this

Asked the same question, `e63aef075` and `a178b56d6` differ on exactly one draw-reaching path:

```
paths_that_differ: ["sim/cache"]
```

— an **absolute-path symlink** (`/home/rich/synthetic-enterprise/sim/cache`) that an auto-salvage
commit captured into a fork's tree, not a line of drawing code. The fifteen seeds in flight are
mutually comparable. That is the opposite finding from the eighteen, and only a diff could tell
them apart: both pairs read `false` on a hash comparison.

*Incidentally filed, not chased here: a gitignored cache path committed as an absolute symlink
means that worktree's "isolated" draw reads and writes the shared tree's cache, and the path would
follow the commit onto any machine that merged it.*

## The repair landed with this note

`trees_the_legs_ran_on` names two commits and its own docstring says *"hash equality is not the
property … so this names the commits and lets the consumer weigh them."* No consumer ever did — for
a week the decomposition on disk has read `false` and the reassurance lived in a docstring. It now
publishes `the_difference_between_those_trees`: the diff between the distinct commits restricted to
`company/`, `saas/`, `sim/`, `simulation/` and the runner itself, with the paths named.

- Unresolvable reads `None`, never `False`: `False` is the flattering side here (it says the trees
  agree), and a leg drawn on an unpushed fork is the ordinary case on this machine.
- `docs/`, `background/`, `tests/` and `site/` are filtered out, or every pair of commits taken
  hours apart on this tree would read as a broken partition.
- It calls `background.boot_sha.changed_paths_between`, which was written on 2026-09-04, has sat
  uncommitted and **called by nothing** for thirteen days, and is precisely the two-commit helper
  this needed. It lands here with its first caller.

Three mutations were applied and each was caught: unresolved→`False` (2 tests), the path filter
dropped (1), and the production call never reaching git (1).

## What is owed next

1. **Refold on the 24, not the 33**, when the fifteen land, and publish the result against the
   prediction above — including "still cannot state a sign", which is what this expects.
2. **Re-price `seeds_needed_to_state_a_sign` on a family that is one objective.** The page
   currently tells the director a sign is six seeds away. On the current pricing rule it is not.
3. The fold's own `producing_commit` block says *"drawn by 2 distinct code tree(s)"* and stops
   there — the same gap this note repairs on the decomposition side, one file over in
   `tools/fold_noise_floor_family.py`. Left alone deliberately: another lane was landing in that
   file during this turn.
