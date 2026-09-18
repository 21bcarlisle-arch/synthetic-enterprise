**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`the-level-selection-split-cannot-be-read-and-that-is-the-thesis-question`)

**Knowledge:** none new. No domain constant moves. This asks whether a reading an artefact already
computes reaches the surface beside the figure it qualifies.

# PREREG — does the family's discrimination reading reach the page beside the advantage?

Delivery seat, 2026-09-17. Written **before** the measurements below were run and unedited
afterwards. Scored in the RESULT document that cites this one by name.

---

## Why this and not a re-run

The direction's DONE condition has two halves and only one is discharged. Today's
`SEAT_RESULT_THE_LEVEL_LEGS_SIGN_IS_DETERMINED_AND_POSITIVE...` established the level leg's sign at
18 draws, and two worker turns carried the three legs onto the page. The other half is the
direction's own bar, in its own words:

> *`discrimination_auc` must be reported beside the advantage on every run, because the 0.4653
> reading is what makes the advantage unattributable.* … *A re-run that reports a new advantage
> figure without `discrimination_auc` beside it is NOT done and repeats the 08-27 mistake.*

**Measured before writing this, so stated as fact and not predicted:** `site/data/value_arms.json`
`error_bar` carries the 18-draw advantage, all three legs and their verdicts, and **no AUC key of
any kind**. `tools/fold_noise_floor_family.py` computes `discrimination_auc_across_seeds` and the
folded artefact carries it as `available: false` with a written reason.
`tools/generate_value_arms_data.py` **contains no reference to that key** — grep returns nothing.

So the page publishes the advantage bound with no discrimination reading beside it, while the
artefact it is built from carries a declared, reasoned "unavailable" that nothing reads. That is
this project's own recurring shape, one level up from where it was fixed this morning: *a leg
nobody summarises is indistinguishable on the page from a leg with nothing in it.* Here it is a
**refusal** nobody summarises, which is worse — the page reads as though the question was never
asked.

## What I predict, before measuring

| # | prediction | how it is scored |
|---|---|---|
| **P1** | The raw nine-seed floor `value_cycle_ab_s1_noise_floor_20260910.json` carries **no `discrimination_auc_across_seeds` key at all** — the SILENT case — while `folded18` carries the key with `available: false` and a reason — the DECLARED case. | read both artefacts |
| **P2** | A naive publisher reading (`floor.get(key) or {}` → falsy) would render those two states **identically**. They are not the same state: one says "this family was asked and cannot answer", the other says "nothing ever asked". Per R15 they must not collapse. | inspect; assert distinct outputs |
| **P3** | Publishing the block changes **no existing feed field**. Scored by generating the feed before and after in one extract and diffing the keys — added only, nothing moved. | one-variable diff |
| **P4** | No site page renders any AUC beside the three legs today, so the reader-side leg is a genuine addition and not a re-render. | grep the site sources |
| **P5** | The folded family's AUC is unavailable on **18 of 18** rows, so the honest published value is a refusal and **not a number**. No figure I publish this turn will be an AUC. | read the artefact |

**The prediction I expect to be wrong about, registered because it is the one that would cost.**
P3 may fail: if any existing control asserts the exact key set of `error_bar` or
`legs_on_one_bar`, an additive block reddens it. If that happens the control is right to fire and
the fix is to widen it deliberately, not to hide the block one level deeper.

## What would refute the whole item

If a page already states the family's discrimination unavailability beside the advantage — anywhere
a reader of the advantage would meet it — then this is already done and the correct outcome of this
turn is a document saying so and nothing landed. **That is checked first**, before any code is
written. The 08-27 mistake being guarded against is a *number* published without its AUC; a refusal
published without its AUC is the same defect wearing a refusal's clothes.

## What I will NOT do

**I will not run a new floor to get an AUC.** One leg is ~1h10m and 6.4 GB, it cannot finish inside
this turn, and the honest reading of the family already on disk is *unavailable with a reason* —
which is a result, and belongs on the surface as one. Publishing "we cannot tell" is the direction's
own stated alternative to a determined sign. A re-run is the next piece and is handed on, not
faked.

**I will not compute a spread over whichever rows happen to carry an AUC.** `_auc_across_seeds`
already refuses that by name — it would bound a different family from the one whose advantage is
published beside it. The publisher must republish that refusal, never soften it.

## Reversal

Every part is one file plus controls. Reverting the commit drops the block; the artefacts stay on
disk and no other feed field moves, which is P3 restated.
