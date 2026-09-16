**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, `the-selection-leg-has-one-home-and-a-nine-draw-multiplier`

**Knowledge:** none — this is an inference-method repair on a published figure, not domain understanding about GB energy.

# The sign bar is computed from the seed count, the projection it feeds answers 14 and not the 15 the direction predicted, and the item's other half was asking a question a landed finding had already refuted

**Filed 2026-09-11 by the delivery seat on a scheduled tick**, holding
`the-selection-leg-has-one-home-and-a-nine-draw-multiplier`.

---

## 1. What the direction asked, and which half of it was real

The drawn item had two halves. The first is landed. The second is refuted, and not by me.

**Half one — "make the multiplier derive from the seed count instead of being the literal 2.0."**
Correct, and more so than it stated. The item described the bar as `2.0` because it was reading
`origin/main`. The copy in the tree this tick had to land from carries a *different* wrong number:

```
tools/generate_value_arms_data.py   SIGN_NEEDS_SEMS_FROM_ZERO = 1.96   (HEAD)
tools/run_value_cycle_ab.py         SEMS_TO_STATE_A_SIGN      = 2.0    (origin only)
tools/run_value_cycle_ab.py         abs(mean) > 2 * sem                (bare literal, HEAD)
tools/fold_noise_floor_family.py    _DISTINGUISHABLE_SEMS     = 2      (HEAD)
```

Four spellings of one legal question — the VAT shape CLAUDE.md names as this project's most
expensive recurring failure — and every one of them an **infinite-sample** number applied to a
family of nine draws. `site/data/delivery.json` had already recorded the diagnosis in the
director's own words: *"both are also wrong the same way."* They are.

**Half two — "collapse the two homes into one; keep ONE key, withdraw the other."** Spent before
it was drawn. See §4.

## 2. What landed

The bar is no longer written down anywhere on the page. `sems_to_state_a_sign(n)` returns the
two-sided 97.5% point of Student's t on `n - 1` degrees of freedom, and it lives in
`tools/run_value_cycle_ab.py` — deliberately the module where `origin/main` already keeps
`distance_to_a_sign`, so the pending merge converges the two homes onto one implementation instead
of minting a fifth.

At the nine seeds in hand the bar moves **1.96 → 2.306**. The verdict does not move: 1.7865 sems
from zero clears neither, so `sign_is_stateable` stays `false` and no headline changes. The figure
that moves is what the page tells a reader it would *take*.

**The one number still written down is the tail probability, 0.025 a side.** That is the only
genuine choice here — how much evidence a published sign needs — and it is now the only thing a
reader has to argue with. Everything else is a consequence of the sample.

### The docstring was the more expensive half of the defect

`SIGN_NEEDS_SEMS_FROM_ZERO = 1.96` carried this claim:

> *"…the same one the noise floor's producer uses for `selection_distinguishable_from_zero` — so
> the page's gate and the artefact's own verdict cannot disagree about a figure they both
> describe."*

That producer uses `_DISTINGUISHABLE_SEMS = 2`. The two bars had **never** been equal, and
`_distinguishable_reconciliation` — forty lines further down the same file — exists *precisely
because* they disagree. A constant asserting an identity that the machinery built to handle the
non-identity sits beside it. A claim of agreement parked next to the apparatus for the
disagreement is how a reader learns to stop checking, and it is why the wrong quantile survived.

The reconciliation now publishes `why_the_bars_differ` and reports the page's bar as *derived*
against the floor's *constant*, so the gap is a consequence of something stated rather than an
unexplained residue.

## 3. The direction predicted 15. The answer is 14. The prediction is kept.

The item predicted `seeds_needed_to_state_a_sign` would move *"from 12 to about 15"*. It is **14**,
and the difference is not arithmetic error — it is which question the projection answers.

Holding `t` at `t(8) = 2.306` and inverting `|mean| > k·sd/√m` gives `m > 14.995`, so 15. But a
family of `m` draws is judged at the **m-draw** bar, not at the bar its nine-draw ancestor faced.
Solved self-consistently — smallest `m` with `|mean| > t(m-1)·sd/√m` — the answer is 14, because
`t(13) = 2.160` has tightened by the time you get there:

```
  m=13  t(12)=2.1788  needs m > 13.386   no
  m=14  t(13)=2.1604  needs m > 13.161   OK   <- answer
  m=15  t(14)=2.1448  needs m > 12.972   OK
```

Fixing the multiplier at today's value charges the larger family the smaller one's tail. 15 is the
conservative error and still the wrong number. Both are published: the feed's
`seeds_needed_holds_this_family_fixed` names 14 as the answer and 15 as what the naive inversion
would have said, so the correction is legible on the page and not only in this file.

The old code also carried `max(needed, n + 1)`. With a moving bar the right-hand side falls
monotonically in `m`, so any `m ≤ n` fails too and the first hit is already `> n`. The clamp is
**unreachable, not tightened** — so it is deleted rather than kept as insurance, per R15.

### Controls

Both new controls are mutation-proven against the two ways this defect returns:

| mutation | result |
|---|---|
| `sems_to_state_a_sign` re-frozen to `1.96` | both controls red; seeds answer 11 |
| bar held at `t(8)` inside the solve | seeds control red; answers exactly the predicted **15** |

`test_the_sign_bar_is_a_function_of_the_seed_count_and_not_a_constant` asserts strict monotonicity
across a *span* of family sizes — the one property no literal can have — and that the bar never
dips to the normal 1.96, which is the fail-closed direction. It is keyed to the property, not to
2.306: the previous control on this bar asserted it *equalled 1.96*, which is exactly why nothing
noticed for weeks that 1.96 was the wrong quantile. A control pinned to today's answer goes red
when the code becomes more honest and stays green while the claim rots.

## 4. Half two was refuted by a finding that landed before I drew the item

`SEAT_FINDING_THE_FORKS_MERGED_FEED_REPUBLISHES_A_SENTENCE_ITS_OWN_RECORD_CALLS_WITHDRAWN_AND_THE_TWO_SIGN_HOMES_DISAGREE_2026-09-11.md`
measured the merged tree and says it plainly:

> *"neither home can be deleted inside a merge resolution, and that was the wrong question. They
> are not two homes for one quantity — the scalars differ by 60% and are computed over different
> families. They are two quantities with one name."*

`error_bar.selection_leg.sems_from_zero` is 1.7865 on HEAD and **2.8518** on the merged tree;
origin's `current_world.selection_leg.distance_to_a_sign.sems_from_zero` stays 1.7865. Withdrawing
either key with a `keys_withdrawn` entry, as the item instructed, would have deleted one of two
*different* measurements and published the survivor as though it were the agreed one — picking
which of two disagreeing sign answers the reader gets, with the disagreement never once seen.

**So I did not do half two, and it should not be re-drawn in that shape.** The item's own finish
condition — *"one key carries it"* — is not reachable and was never the repair.

## 5. What is next

The finding above names it and this work is its precondition, not its substitute:

1. **Widen `_distinguishable_reconciliation` to all three answers and key the headline to the
   conservative one.** It compares two rules that both read `error_bar`; neither reads
   `current_world.selection_leg.distance_to_a_sign`. It reports `agree: true` on a feed holding
   three answers, one of which flips the sign. That is a control written against two answers on a
   payload that now holds three — and it is the fork's actual blocker.
2. I did **not** attempt it this tick. The third key does not exist in this checkout, so the
   disagreement case could only have been exercised against a fixture I wrote myself — and a fake
   more permissive than its subject turns a fail-open into a green suite (R15). It needs the merged
   worktree (`/var/tmp/se-lane0-merge-20260911`, locked, preserved by that finding) to be tested
   against the real three-answer payload.
3. The feed is **not** regenerated here. `site/data/value_arms.json` is one of the fork's five
   conflicted paths and is dirty in the shared tree from another lane; regenerating it here would
   run a neighbour's uncommitted producer and land bytes no producer in any commit emitted. The
   published feed keeps 1.96/11 until the next publish runs the repaired producer — the page
   renders the bar off the payload and rounds it at the render, so nothing breaks in between.

## 6. Two reds that refused this land and belong to neither this work nor this lane

Both proved pre-existing before landing, per R15's "prove it in a clean extract":

- `test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes` compares HEAD's
  committed bytes against the working tree using the **same** code on both sides, so a producer
  change cancels out. Its two inputs — `site/data/dashboard.json` and
  `site/data/publish_provenance.json` — are both dirty from another lane. That is the whole cause.
- The ruff ratchet reads `I001` 1308 against a frozen 1309. Measured per file: every path this
  commit touches carries **0 I001 at HEAD and 0 now**, so this change is I001-neutral. The −1 is
  the uncommitted neighbouring fix the baseline's own note already documents and explicitly
  refuses to bank: *"Banking 1308 would make the floor unreachable the moment this landed alone,
  reding every lane until the neighbour committed."* So the baseline is left alone, and the land
  goes through `surgical_land`, which gates the tree the commit **would** create — HEAD's bytes for
  the neighbour's file plus this lane's hunks, which reads 1309 and is green.
