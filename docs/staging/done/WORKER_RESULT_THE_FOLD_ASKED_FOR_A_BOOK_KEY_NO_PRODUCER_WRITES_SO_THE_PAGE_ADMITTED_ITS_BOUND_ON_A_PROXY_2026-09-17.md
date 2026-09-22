**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0

# The fold asked for a book key no producer writes, so the page admitted its bound on a proxy

**Filed** 2026-09-17 · worker · lane 0 delivery
**Item** `the-selection-leg-is-six-seeds-short-of-a-sign-and-its-point-estimate-is-negative`

> **The drawn item said the new seeds "must name a book" because the family names none. The seeds
> already name one.** `tools/fold_noise_floor_family._book_identity` took its agreement over
> `book_identity.digest` — a key `run_value_cycle_ab.floor_book_identity`, the only thing that has
> ever written a floor's book block, does not emit and never has. So the success branch was
> unreachable by any real pair, every fold fell through to the disagreement arm, and the published
> page admitted its own error bar on a date-ordering **stamp proxy** while the book sat agreed in
> both members.

---

## What the drawn work was

Take the selection leg from 18 seeds to the 24 its own bound prices, drawing on one tree and naming
a book, then refold and publish whatever comes back — including a negative sign, if that is what it
says.

Two defects were named as things the new family must not inherit: the null `book_identity.digest`,
and `floor_legs_ran_on_one_tree: false`. The first turned out not to be a property of the seeds at
all.

## What was already in flight

A three-seed floor carrying `discrimination_auc` was **already running** when this item was drawn —
`longjob-floor-auc-20260917`, launched 16:21 by a previous seat invocation, seeds
`1234567/2345678/3456789`, disjoint from all 18. It peaks at ~6.6 GB against ~8.7 GB available. A
second concurrent leg would very likely have OOM-killed both, and this guest's `oom_kills_total`
already stands at 43. Starting a rival draw would have cost another lane three hours to save this
one ninety minutes. So this turn did not draw seeds directly — it **chained** them (below) and spent
its own time on the part that was blocking regardless.

## The defect, measured

`floor_book_identity` writes `{declared, seeds_reconciled, seeds_that_recorded_no_book,
unavailable_because, realised_across_seeds, how_a_consumer_should_pair_this}`. There is no
`digest`. The consumer — `generate_value_arms_data._floor_book_admission` — correctly reads
`book_identity["declared"]`, obeying the `how_a_consumer_should_pair_this` sentence the producer
puts on every artefact. **The fold is the only step between them, and it answered the question with
a key neither of them uses.**

Measured, on the two real members of the served 18-seed family:

```
MEMBER book_identity keys: ['declared', 'how_a_consumer_should_pair_this',
                            'realised_across_seeds', 'seeds_reconciled',
                            'seeds_that_recorded_no_book', 'unavailable_because']
MEMBER declared: {'served_segments': ['resi', 'SME'],
                  'served_segments_resolved_from': 'curriculum', ...}
MEMBER has digest?: False

FOLDED book_identity: {"digest": null,
  "unavailable_because": "the folded runs name 1 different books (None), so no
                          single book identity describes these rows."}
folded has 'declared'?: False
```

"name 1 different books" is a sentence whose own count contradicts it, and it has been on
`site/data/value_arms.json` as `floor_admission.rule: "stamp_proxy"`,
`floor_declared_book: null` — the bound admitted **by its date** rather than by the population it
was drawn over. That is the shape `SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_
PAIRING_RULE_IS_A_STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09` was filed to end; the producer
side was repaired then, and the join quietly re-opened it.

### Why no control caught it

Every existing book test asked whether the fold **refuses**, and a guard that answers `unknown` to
everything passes all of them. The one positive fixture wrote `{"digest": "abc123"}` — a shape no
producer emits — so the control was green against a contract that did not exist in the field.
This is CLAUDE.md's own rule (*"when a branch exists to be taken rarely, assert it CAN be
taken"*) and the catalogued FABRICATED-probe mode, in one fixture.

## The repair

`_book_identity` now pairs on `declared`, via `run_value_cycle_ab._book_declared` — the producer's
own comparable form, imported and not re-copied, per the module's standing rule. It does **not**
mint a digest to fill the field it stopped reading: a floor's book *is* its declared half, and an
invented identity would be read as established. Three states are now distinct where two were
collapsed: block absent (predates the field), block present but declaring nothing (the producer's
own fail-closed when a seed recorded no book), and books that genuinely disagree. The realised
counts are dropped from the family block with a named reason — each member measured its own range
over its own seeds, and re-publishing the first member's as the family's would state a range
measured over a third of the rows as if it covered all of them. `folded_from` had the same
never-written-`digest` read; it now records each member's declared book.

**Mutation-proven, in a clean `git archive` extract and never in the shared tree.** With the
pre-fix branch restored verbatim, the two new controls fail on their own assertions:

```
assert book["unavailable_because"] is None
E  AssertionError: assert 'the folded runs name 1 different books (None), so no
                          single book identity describes these rows.' is None
2 failed, 15 passed
```

The sentence the mutation produces is the one live on the page today, which is what makes this a
control over the defect rather than over today's answer.

## The finding this turn did not expect: the 24-seed price is not robust

The item's `seeds_needed_to_state_a_sign: 24` is arithmetic over the pooled 18. Split the family at
the seam the book question already draws through it:

| Family | n | mean | sd | sem | sems from 0 | seeds needed | book |
|---|---|---|---|---|---|---|---|
| Served (pooled) | 18 | −£624.13 | 1472.89 | 347.16 | 1.798 | **23** | **none** — one member names none |
| The half that names its book (`_20260910b`) | 9 | −£170.09 | 931.78 | 310.59 | 0.548 | **121** | resi+SME, from curriculum |
| The half that does not (`_20260909b`) | 9 | −£1078.17 | 1810.50 | 603.50 | 1.787 | **12** | none |

Both halves are negative, so the **sign of the point estimate is not in question** — it is negative
on the pooled family and on each half separately. What moves is the price of *stating* it: **23
seeds, 121, or 12, depending on which half you believe**, from one family of 18.

**I cannot attribute that split to the book.** The halves' means differ by £908, which is 1.34
standard errors of their difference — itself unstateable, so pooling is not refuted by this
evidence and I am not proposing the family be cut. The point is narrower and harder: *seeds_needed*
is a ratio of two quantities estimated from the same small draw, and it swings tenfold across
halves of one family. It is a planning figure, not a measurement, and the page should not be read
as though 24 seeds will settle the thesis question. **Prediction, filed before the seeds land: the
refolded family will NOT state a sign at 24, and the negative point estimate will hold.** If the
seeds refute this, that stands in the record beside it.

## What is chained, and why not more

`longjob-floor-next12-20260917` is launched and **waiting on `wait_for --pid 3297762`** — it starts
the moment the AUC leg frees its memory, and not before. Twelve fresh seeds
(`3100001…3100012`), one process, on a **pinned, declared worktree** at `7da627b90`
(`/var/tmp/se-floorrun-20260917b`, owner marker written, `sim/cache` symlinked, lease refreshed at
the moment the long leg actually starts rather than by the tick that made the tree).

Twelve is not arbitrary: 9 (`_20260910b`) + 3 (AUC) + 12 = **24 seeds that can all name their
book**, which is the bound the artefact prices, met without pooling in rows drawn over an unstated
population.

**The honest cost of the other requirement.** "One tree" is *not* met by this, and cannot be
cheaply. The new twelve are one tree; the 24 book-named span three. A 24-seed family on a single
tree means drawing all 24 fresh — about 22 hours at the ~55 min/seed these legs actually cost. That
is the real price, stated rather than quietly dropped, and it is a decision about how much the
one-tree property is worth, not something to imply was delivered.

**Stated risk:** `noise_floor` writes its artefact only at the end, so an 11-hour batch that dies at
hour 10 yields nothing. Two nine-seed batches have survived this route; twelve is an extrapolation
of it.

## What is owed next

1. Fold the AUC three onto the served 18 → n=21, and refold the book-named family when the twelve
   land → n=24. The repaired fold will now carry `declared` on the second one.
2. Publish the refolded family in its own words — **seed count, sem and standard errors from zero
   beside the figure**, per the item; a re-run reported without them is not done.
3. Point `CURRENT_WORLD_NOISE_FLOOR_PATH` at the refolded family (it still names the unfolded
   nine-seed `_20260909b`).

Nothing here re-draws until a seed agrees, and nothing here promotes one half over the other.
