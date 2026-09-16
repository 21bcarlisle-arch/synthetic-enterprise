**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the floor decomposition refuses legs from two worlds and never asks which tree drew them

`decompose_floor` (`tools/run_value_cycle_ab.py`) refuses four things and each refusal is a good one:
a leg whose `redraw_scope.mode` does not name its own half; a leg that cannot name its world; legs
whose `world_identity.digest` disagree; legs whose seed sets disagree. The world refusal states its
own reason and the reason is right — *"a variance measured over one departure level is not a
component of a variance measured over another"*.

**The identical argument applies to the code, and nothing makes it.** `world_identity.digest` is the
per-year departure-level anchors and nothing else; it is not a statement about the tree. Three floor
legs that are supposed to **partition one call stream** can be produced by three different trees and
the function will reconcile their variances without a word — and `producing_commit.commit` is
already stamped on every one of them.

**Filed:** 2026-09-10, delivery seat (isolated worktree).

---

## What I first thought, and the check that corrected it

I filed this expecting the live instance to be the published bound: the nine-seed `all` floor
(`c066c114b`) quoted as the error bar on a three-arm contrast drawn at `04361d6c7`, two trees apart
by 2,044 insertions across 15 modules. **That instance is already surfaced.**
`generate_value_arms_data._floor_tree_pairing` asks exactly that question of exactly that pair, on
all three branches including the matching one, and renders a named caveat. It was built on
2026-09-09 for this reason. The page is not short of this.

So the finding is not "the page hides a tree split". It is one cut narrower and it is about the
**artefact**, not the page.

## What is actually unasked

| pair | asked by | verdict on today's data |
|---|---|---|
| floor ↔ the three-arm contrast it bounds | `_floor_tree_pairing`, page-side | asked, rendered, amber |
| the three floor legs against **each other** | **nobody** | — |
| any of it in the machine-readable artefact | **nobody** | — |

The second row is the load-bearing one, because it is a stronger requirement than the first. A
caveat is the right response to a floor and a figure from two trees. It is *not* the right response
to two halves of a partition from two trees: if the code differs, they are not halves of one call
stream and the reconciliation ratio — the control that says they are — is measuring something else.

## Today's instance is benign, and I only know that because I looked by hand

`docs/observability/value_cycle_ab_floor_decomposition.json` is built from legs at **two different
commits** — `all` at `1d821e12b`, `only` and `except` at `416e829c7`. A control keyed to hash
equality would refuse it. It should not: `git diff 1d821e12b..416e829c7 -- simulation/ company/
saas/` is **empty**. The commits differ; the code that drew the variances does not.

That is the whole design constraint. **Key the record to the property, not to today's answer** — and
"same hash" is not the property. So this records and names the commits; it does not refuse.

## Why it is worth one field anyway

Because the tree difference is not hypothetical here — this project has already *measured* what one
costs. `CURRENT_WORLD_NOISE_FLOOR_PATH`'s own comment: on the three seeds two floors share, **the
same seed in the same world returns a `selection_gbp` differing by +38.96 to +61.38 under the two
trees.** A quantity that moves by £39–£61 between trees is being differenced into a variance and
reconciled to two decimal places, and the artefact carrying that reconciliation says nothing about
which trees were involved.

And it bit this turn: choosing to run the two new legs at `c066c114b` rather than at HEAD — HEAD's
`company/pricing/value_based_renewal.py` is a **different arm** (`04a7e5a57` re-drew the choosing leg
with the objective changed) — was a judgement made by hand, off a `git diff` nobody is obliged to
run. Nothing in the tool would have stopped the wrong choice, and the resulting artefact would have
looked identical.

## The remedy — one field, recorded, never a refusal

`decompose_floor` composes the four legs' own `producing_commit.commit` into its output:

```
"trees_the_legs_ran_on": {
  "commits": {"undecomposed": ..., "only": ..., "except": ..., "three_arm": ...},
  "floor_legs_ran_on_one_tree": true | false | null,   # null = at least one leg is unstamped
  "contrast_drawn_by_the_same_tree": true | false | null,
  "unavailable_because": <named reason, or null>,
}
```

Unstamped is `null` and never `true` — a missing stamp is not evidence the trees agree, and
defaulting it to `true` would make the oldest artefacts render as the cleanest provenance on the
page. That is the same rule `_floor_tree_pairing` already applies, moved to where the numbers are.

One field, three booleans, no register. The consumer states it; nothing gates on it.

## What this finding does NOT claim

It does not claim any published figure is wrong. It does not claim two trees give different
variances in general — the one measurement of that (+38.96..+61.38 on `selection_gbp`) is a spread
between two specific trees and is not a coefficient. **The claim is that a function with four
explicit provenance refusals presents its output as provenance-checked along an axis it never
examined, and the data to examine it is already inside every input it reads.**

## What is next

The `only` and `except` legs are being run on this book at `c066c114b` — the `all` leg's own tree,
chosen for this reason — so the three legs do partition one call stream. Pre-registration:
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_TWO_MISSING_FLOOR_LEGS_WILL_SAY_ON_THIS_BOOK_2026-09-10.md`.
The decomposition those legs feed will be the first to carry `trees_the_legs_ran_on`, and it will
read `floor_legs_ran_on_one_tree: true, contrast_drawn_by_the_same_tree: false` — which is the
honest description of it.
