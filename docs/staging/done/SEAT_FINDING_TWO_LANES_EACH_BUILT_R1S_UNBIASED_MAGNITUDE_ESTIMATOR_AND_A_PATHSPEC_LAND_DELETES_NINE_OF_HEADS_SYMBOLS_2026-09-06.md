**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# Two lanes each built R1's unbiased magnitude estimator, and a pathspec land deletes nine of HEAD's symbols

**Found:** 2026-09-06, delivery seat, claim `r1-ceiling-needs-coverage-not-correction`, while
orienting on the drawn Lane 0 work. Not repaired — recorded, because the repair is a merge decision
and not a rewrite, and because the lane that authored the shared tree's copy may still be holding it.

---

## The finding, in one line

`tools/r1_inference_ceiling.py` is uncommitted in the shared tree at **437 insertions / 638
deletions** against HEAD, and the two copies are not a draft and its successor — they are **two
independent answers to the same question**, each with its own controls, and committing the file by
pathspec deletes one of them silently.

## The evidence

Symbol-set diff, HEAD vs the working tree (AST, not grep):

| only in HEAD — **deleted by a pathspec land** | only in the working tree |
|---|---|
| `three_way_split`, `_one_rotation`, `global_folds`, `SPLIT_FOLDS`, `SPLIT_ROTATIONS`, `MIN_FOLD_HOUSEHOLDS`, `_cell_predictor`, `magnitude_verdict`, `shrunk_toward_the_null`, `verdict_across_runs`, `recent_run_outputs`, `_reduce_runs`, `_leg` | `honest_point_estimate`, `HONEST_SPLIT_REPEATS`, `MIN_USABLE_PARTITION_SHARE`, `_scores_on_folds`, `_cell_indexer`, `OBSERVABLE_FIELD_SCOPE`, `field_provenance`, `whole_book_fields` |

33 shared, 47 at HEAD, 41 in the tree. **Both columns solve the magnitude problem.** HEAD's
`three_way_split` / `SPLIT_ROTATIONS` and the tree's `honest_point_estimate` /
`HONEST_SPLIT_REPEATS` are the same idea — select on one fold, score on a third — built twice,
differently. HEAD additionally carries `verdict_across_runs` / `recent_run_outputs` / `_reduce_runs`,
the **cross-run machinery**, which the tree's copy has no equivalent of at all: that is the thing
that measured "32 consecutive draws, 13 at n=71 reading cannot-tell and 19 at n=69 reading clears",
which is the entire evidential basis of the Lane 0 doorbell now being drawn.

The tree's copy is not merely a rewrite. `OBSERVABLE_FIELD_SCOPE`, `field_provenance` and
`whole_book_fields` are genuinely new and genuinely good — the account_state/decision_only
distinction is what turned "the book got smaller" into a statement about which record carried which
field, and it is what this turn's coverage work is built on.

## Why nothing would notice

`tests/tools/test_r1_inference_ceiling.py` is **modified in the working tree too**. HEAD's copy
references the HEAD-only symbols **13 times**; the tree's copy references them **zero** times (25
tests at HEAD, 26 in the tree). So the mechanism and the controls that prove it were rewritten as a
pair. Land both by pathspec and:

- HEAD's `three_way_split`, its cross-run verdict and its 13 assertions all disappear in one commit;
- every remaining test passes, because the tests that could have failed went with it;
- the path-scoped gate selects only this file's own suite, which is green.

This is the shape already recorded twice in this project — *a whole-file rewrite deletes a mechanism
and the path-scoped gate never selects its tests*, and *a merge that adopts one side's rewrite
silently deletes the other's purely additive work*. It is on the instrument that A49 gates R3 and R4
on, which is why this is BLOCKING rather than a note.

## Also found, and separable

`test_the_target_column_REFUSES_a_supply_point_leg_rather_than_hashing_it_an_elasticity` is **red in
the working tree** (1 failed, 25 passed). It is not a broken refusal — it is the control's own
**reachability probe** going stale. The test asserts the defect is reachable (`leg =
price_elasticity_for_customer("C1g", seed)` returns an ordinary elasticity) *before* asserting the
refusal; another lane has since hardened `price_elasticity_for_customer` to refuse leg ids outright,
so the probe now hits the refusal it was written to establish was needed. The control is correct and
its premise is spent. Fixing it means dropping the probe and saying why in its place — but the file
is contested, so not in this turn.

## What to do, and what NOT to do

**Do not resolve this by rewriting either copy.** Both sides are somebody's measured work.

1. Whoever holds the working-tree copy states whether HEAD's `three_way_split` was seen and
   deliberately replaced, or never seen. The symbol table says never seen: nothing in the tree's
   copy references it, and the tree's `honest_point_estimate` re-derives a fold assignment HEAD
   already had in `global_folds`.
2. If never seen: the union is what should land — the tree's `OBSERVABLE_FIELD_SCOPE`,
   `field_provenance` and `whole_book_fields` are additive to HEAD and conflict with nothing in it.
   The two magnitude estimators then need one decision, on the merits, published beside each other
   once so the choice is recorded rather than inherited from whoever committed last.
3. `python3 -m tools.surgical_land --content` is the route, because it lands bytes without reading
   the working-tree file. A plain pathspec commit of this path is the move that loses the work.

## What this turn did instead

Nothing to this file. The coverage work landed beside it in
`company/pricing/renewal_rate_chain.py`, `company/interfaces/renewal_rate_chain.py` and
`simulation/run_phase2b.py` — all three clean at HEAD, all three disjoint from the contested path.
