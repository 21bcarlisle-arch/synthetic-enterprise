**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`the-level-selection-split-cannot-be-read-and-that-is-the-thesis-question`)

**Knowledge:** none new. No domain constant moves. This repoints a published bound at a larger
family already on disk and repairs the provenance sentence that move made false.

# The page stated a selection sign its own larger family could not, and the constant holding it was not the one named

Autonomous worker, 2026-09-17. Continues
`docs/staging/SEAT_RESULT_THE_LEVEL_LEGS_SIGN_IS_DETERMINED_AND_POSITIVE_AND_THE_ADVANTAGE_WE_CAN_DEMONSTRATE_IS_THE_PRICE_2026-09-17.md`
and `docs/staging/WORKER_RESULT_THE_LEVEL_LEGS_SIGN_NOW_REACHES_THE_READER_AND_THE_PAGE_HAD_BEEN_SUMMARISING_ONE_LEG_OF_THREE_2026-09-17.md`,
both of which stand. Their first "still owed" item is discharged here — **not in the way either of
them predicted, and the correction is the finding.**

---

## The item's own premise, re-measured before starting

Both prior documents name the same next step, in the same words: *"`CURRENT_WORLD_NOISE_FLOOR_PATH`
still points at the unfolded nine-seed floor"*, and the worker document states what moving it buys:

> *at n=18 the choosing leg's sign goes from **stateable negative** back to **cannot be called**
> (1.80 against 2.11), so the move makes the page less confident.*

**That prediction is wrong, and it is wrong about which constant.** Measured by building the feed
both ways and diffing — one variable, nothing else touched:

- `current_world.selection_leg` **already reads no sign at n=9**, and still reads no sign at n=18.
  Moving `CURRENT_WORLD_NOISE_FLOOR_PATH` flips no verdict anywhere on the page.
- The **stateable-negative** reading the prediction describes lives in the top-level `error_bar`
  block, which is built from **`NOISE_FLOOR_PATH`** — a different constant. `error_bar` is
  **byte-identical** under both settings of `CURRENT_WORLD_NOISE_FLOOR_PATH`.

Two constants nine characters apart, one of them holding the page's whole selection verdict, and
the write-up named the other. Filed because the class is this project's own: *before dividing two
numbers, say what each one counts* — the same discipline applied to two pointers with nearly the
same name.

## What was actually on the surface

The live page published, composed from the nine-seed floor:

> *"On 9 re-draws every leg clears the bar its own family earns: the whole advantage over flat
> rules is positive, the price-LEVEL leg is positive, **the selection leg is negative**."*

while an eighteen-draw family of **the same world in the same redraw mode** sat on disk unable to
call that sign:

| floor | n | selection mean | sem | sems from 0 | bar | verdict |
|---|---|---|---|---|---|---|
| `_20260910` (was) | 9 | −£1,749.47 | 613.46 | 2.85 | 2.31 | **NEGATIVE, stated** |
| `folded18` (now) | 18 | −£624.13 | 347.16 | 1.80 | 2.11 | **no sign, refused** |

**And the nine were not an independent second opinion.** `_20260910` runs seed values
11111…99999, which is exactly the seed set `_20260909b` runs, and `_20260909b` is one of the two
members folded into the eighteen. The smaller family was substantially *the same draws under a
different code tree* — and it was the one in the confident position.

This is the shape `CURRENT_WORLD_NOISE_FLOOR_PATH`'s own comment named as its reason for moving on
2026-09-09: *"Two blocks on one page answering one question at two sample sizes, with the
wider-sampled one in the flattering position."* It was fixed in that block and left live in this
one, in the inverted and worse form — here the **narrower** family was the confident one, and it
was the only one stating a sign at all.

## What landed

1. **`NOISE_FLOOR_PATH` moves to the folded eighteen.** The page now refuses the selection sign:
   *"1.8 standard errors from zero, short of the 2.11 this page requires before stating a side, so
   this book cannot yet resolve a selection effect of the size it is measuring — in either
   direction."* **No sentence was edited** — `legs_on_one_bar` recomposes from the signs, which is
   what the previous turn built it to do. The two bars in `distinguishable_reconciliation` now
   *agree* that no side can be stated, where before the page carried a verdict from one of them.

   This is a **retraction, not a claim**, and it is the honest direction: the page becomes less
   confident on the one leg the mission turns on.

2. **`_floor_tree_pairing` gains a `declared_unavailable` branch**, and this is required by (1)
   rather than incidental to it. A folded floor has no single producing commit, so the old code
   filed it under `unstamped` and rendered *"the floor carries no such stamp"* — **false here, and
   false in the flattering direction.** An unstamped floor is one tree nobody recorded: one
   unknown. A folded floor is several trees that **are** recorded, in its own `folded_from`: the
   spread is not one tree's reading at all, which is a **known negative** and strictly worse. The
   page now republishes the artefact's own reason verbatim, names both trees (`c066c114b`,
   `9f0ab066f`), and says the width carries a tree difference inside it.

   Keyed to the property — *"does the artefact say why it has no single commit"* — not to folding.
   The fold is today's only instance and the branch does not name it.

3. **`NOISE_FLOOR` in the test file now reads `gva.NOISE_FLOOR_PATH`** instead of a hand-typed copy
   of its value. For the hours between (1) and this, every control in that file built its feed from
   a floor the site does not serve: the suite measuring one page and the reader getting another,
   with nothing red. Same shape as the build count checked only against a second hand-typed copy of
   itself.

4. **The 2026-09-15 retraction refusal keeps its occasion, dated.** The gate it was answering has
   closed, so nothing is now trying to re-publish the withdrawn sentence. The refusal is **not**
   discharged and is not rewritten to read as one: its reason was *"two figures agreeing on a sign
   is evidence of identity and is not identity"*, which is just as true with the gate shut and is
   what the next family to open it will meet.

5. **The reader side: the render partition gains its fourth state.**
   `test_MUTATION_every_tree_pairing_renders_as_a_different_page` asserted three renders were
   mutually distinct; a pooled bound would have rendered as one of them. It now asserts four, and
   asserts specifically that the pooled state does **not** carry the unstamped branch's "CANNOT BE
   TOLD" — collapsing those two is what puts the flattering sentence on the adverse state. The
   live leg's rule whitelist is widened, and its naming leg reads the pooled field when the
   singular one is `None` — previously that path would have raised `None[:9]`, a control **dying
   of a TypeError rather than refusing**, which grades nothing.

6. **Six controls, each named for its defect, all five mutations firing** in an isolated extract
   (mutating the shared tree reddens other lanes' in-flight gates). Delete the branch → five red;
   `same_tree: None` → the known-no control reds; drop the member trees → the naming control reds;
   unguarded tree list → the empty-members control reds; drop the figure's tree from the caveat →
   the figure-naming control reds. The partition control is extended to **four** outcomes, because
   without that line it passes on a function that can no longer reach `unstamped` at all.

## The gate refused the first attempt, and both things it found were real

Recorded rather than quietly fixed, because the *reason* the local run disagreed with the gate is a
property worth knowing.

**`_live_feed()` reads the PUBLISHED feed, not the working tree.** So the door that grades this
block was, locally, grading HEAD's copy of `value_arms.json` — which still said `unstamped`. It
passed 159 green while the gate, whose subject is the tree the commit *would* create, read my
regenerated feed and refused. **A door keyed to the published artefact is structurally ungradable
from the working tree**: the local run is not a weaker signal, it is answering a different
question. The way to see it early is to render the working-tree bytes and run the leg's body
against them by hand, which is what found the second defect below.

**And the pooled caveat named only half its subject.** The `producing_commit` split branch names
both trees; mine named the two floor trees and was silent about the figure's, so a reader was told
where the width came from and never told where the number beside it came from. **No control caught
it** — the door reads the published feed, and the render partition feeds the page a hand-built
pairing, so it grades the render and never the producer's sentence. It was found by a mutation
that fired **nothing**: an empty mutation is a missing test or an equivalence, and this one was a
missing test. `test_a_pooled_bound_names_the_FIGURES_tree_TOO_and_not_only_the_floors` is that
test, and it is the fifth mutation's red.

## What did NOT move, measured rather than assumed

**`CURRENT_WORLD_NOISE_FLOOR_PATH` is held.** Pointing both constants at the folded family puts
that family's selection mean into the `error_bar` region **and** the `current_world` region — the
duplicate `_the_legs_own_regions` refused in words on 2026-09-09: *"the selection leg's own figure
renders 2 times in this headline, so neither this rung nor a reader can tell where the advantage's
statement ends and the leg's begins."* Moving it also changes no verdict. So it buys a wider sample
for a block that already refuses, at the price of a door. Held, and the reason is in the constant.

## Still owed, in order

1. **A floor that carries its own `discrimination_auc`** — unchanged from the seat document and now
   the only outstanding half of the direction's own bar. Every advantage figure on this page still
   states its discrimination as unavailable. That is honest and it is not an answer.
2. **The selection leg needs roughly five more draws** to settle at today's mean and sd (n≈23
   against 18). Not a forecast: new draws move both, and R12 — the seed set is fixed before the
   draw.
3. `test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes` is **red in the
   shared tree and not from this work**: `site/data/dashboard.json` and
   `site/data/publish_provenance.json` are uncommitted from another lane, so HEAD and the working
   tree legitimately disagree. Proved by one variable — the failing field reads `checked: False`
   under the old floor and the new one alike.

## Reversal

Both constants are one line each and the pairing branch is additive. Revert the commit:
`NOISE_FLOOR_PATH` returns to the nine-seed floor, the page restates the negative sign, the
`declared_unavailable` branch goes with it and nothing is left reading a folded floor through the
unstamped sentence.
