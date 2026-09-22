**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The AUC fold is refuted on three counts, and the deletion it asks for would blank the only discrimination reading the page has

**Claim:** `fold-the-auc-carrying-family-into-the-advantage-family-once-next12-settles`
**Disposition taken:** `--release`. No fold was performed and no code was changed.

---

## What was drawn

> Fold `docs/observability/value_cycle_ab_s1_noise_floor_auc3_20260917.json` into the published
> advantage family once `longjob-floor-next12-20260917` has settled, using the BOOK-CARRYING route
> (`..._20260910.json` + `..._20260910b.json` + `..._auc3_20260917.json`) rather than folding onto
> `folded18`, which declares no served book. Then delete `AUC_FAMILY_FLOOR_PATH` and the fallback
> branch in `_family_discrimination` that reads it.

The item's reasoning was sound on its own terms: one family carrying both the advantage and the
AUC on every row would move `_family_discrimination` to `state=measured`, the null reading would
follow the family's own seeds, and the second constant would become dead weight. **Every step of
that follows from the fold being legitimate. It is not.**

## Refutation 1 — the precondition was never met

The item is explicitly gated on `longjob-floor-next12-20260917` having settled. It has not.
Measured at 22:0xZ on 2026-09-17, from outside the job's own cgroup:

```
$ python3 -m background.launch_liveness --check
floor-next12-20260917: RUNNING -- the user manager reports `longjob-floor-next12-20260917`
ActiveState=active, which is a verdict from outside the job's own cgroup and therefore survives
the kill it would report
```

PID 3819244, started 19:11, 108 minutes of CPU against a ~11h estimate. On the precondition alone
this item was not startable this turn.

## Refutation 2 — the two families sit on disjoint comparison arms

This is the one that kills the fold outright, and it is not a matter of degree. `level_gbp_per_mwh`
is the rate the comparison arm is held at. Printed at real inputs across all 21 seeds the item
names:

| family | seeds | `level_gbp_per_mwh` | `value_advantage_gbp` range |
|---|---|---|---|
| `..._20260910.json` | 9 | **20.00** on every seed | 13,499.39 – 20,886.69 |
| `..._20260910b.json` | 9 | **20.00** on every seed | 16,656.01 – 21,464.16 |
| `..._auc3_20260917.json` | 3 | **38.50, 38.50, 36.25** | 6,319.59 – 10,217.83 |

The arms do not overlap. Neither do the advantages they produce: the largest advantage in the
AUC-carrying family (10,217.83) sits **£3,281.56 below** the smallest in the eighteen (13,499.39).
Pooling them would not widen a noise family — it would average two operating points and publish
the spread between them as redraw noise.

`run_value_cycle_ab` sets the level arm's flat rate from the value arm's own realised median
margin on that run, so the rate legitimately moves seed to seed. That is exactly why the split
here is not a seed accident: it is a step, and it is a step in *our pricing*, not in the world.

## Refutation 3 — the code already carries a written refusal of this exact fold

`AUC_FAMILY_FLOOR_PATH` documents, in the tree, predating the item:

> **WHAT IT MAY NEVER BE USED FOR.** It bounds nothing else on this page. Its seeds'
> `selection_gbp` must not join the error bar's family, and its spread must not become any
> figure's interval.

The drawn fold is that sentence's prohibited case, named literally. The item is the design the
file already refused.

## And the deletion is not dead-weight removal — it blanks a live reading

This is the part worth keeping. The item treats deleting `AUC_FAMILY_FLOOR_PATH` and the
`elif auc_family:` branch as cleanup that *follows* the fold. Because the fold cannot happen, the
deletion does not remove dead weight — it removes the only branch that fires. Run both ways
against the real artefacts:

```
does the ADVANTAGE family carry its own AUC rows? -> False

TODAY (fallback present)      null available: True
  "Discrimination reads 0.5697 across 3 draw(s), measured over a DIFFERENT family from the one
   the advantage above is bounded over (the 3-seed AUC-carrying floor of 2026-09-17), so it
   bounds nothing on t..."

AFTER the item's deletion     null available: False
  "NOTHING HERE STATES WHETHER THE ARM WON BY KNOWING ANYTHING, and no run reaching this page
   has measured it."
```

The published eighteen carry no `discrimination_auc` on any row, so `own_rows` is empty and the
`elif` is the **only** reachable branch that produces a reading. Deleting it drops straight to the
`else`. That is a direct breach of the direction's own standing bar on this work — that
`discrimination_auc` is reported beside the advantage on every run — executed as tidying, and
nothing on the page would have gone red to say so.

**The general shape, and it is one this repo keeps paying for:** a two-step item where step 2 is
only safe because step 1 happened. When step 1 is refuted, step 2 does not become a no-op — it
becomes the defect, and it still looks like cleanup in the diff.

## Duplicate-work check — the sibling claim is the same question, and it is landing now

The draw named `the-selection-leg-is-six-seeds-short-of-a-sign-and-its-point-estimate-is-negative`
as a possible duplicate. It is not the same *work*, but it answers the same *question*, and it
reached the same answer independently and first. That seat (PID 99148) was mid-`surgical_land`
throughout this turn with:

> *the selection family must not be refolded: the comparison arm moved from 20.00 to 36.25-38.50
> and all four fold refusals pass across it*

— landing a fifth fold refusal keyed to comparison-arm **overlap** in `fold_noise_floor_family`,
and a sixth pairing key `_comparison_arm_pairing` on `_error_bar` in `generate_value_arms_data`.
That landing also repairs the reader-facing half of this item's WHY: the page will state the two
operating points rather than silently pairing an advantage measured against a 20.00 arm with a
discrimination measured against a 36.25–38.50 one.

That land completed during this turn, after 105s of waiting on it, as commit **`091e111ea`**
(5 files, +516/-1, touching both files this item names).

**`--release` remains the correct disposition, not `--landed-under`.** The two are genuinely
different work on one subject, which the draw itself allowed for: the rival *performed* a repair,
whereas this item's work was *refuted* and deliberately not performed. Binding this claim under
theirs would record a fold and a deletion as having landed when neither did, and both must not.

**One thing the next reader should know, and it is not mine to fix:** `091e111ea` is reachable
from no ref — `git branch -a --contains` is empty and it is not an ancestor of `origin/main`,
which is still `0d9ff275d`. It is committed but unpromoted. If that seat's promotion step did not
run, the comparison-arm refusal described above exists only as a dangling commit and the next
`git gc` is what collects it. Flagged here because this document is the only place the two lanes
meet; the owning seat may still have been promoting when this turn ended.

**No code was written this turn by design.** Both files this item names —
`tools/generate_value_arms_data.py` and `tools/fold_noise_floor_family.py` — were being landed by
that rival at the time. Editing either would have put my bytes inside their in-flight gate.

## What should happen next

1. **Do not re-draw this item as written.** Its fold is refuted by the data and by the file's own
   comment; its deletion is refuted by the measurement above.
2. **When the rival's landing is on `origin/main`,** the comment at `AUC_FAMILY_FLOOR_PATH` should
   gain one sentence naming the *deletion* specifically — the prohibition today covers using the
   family's `selection_gbp`, not removing the branch that reads it. That sentence is what the next
   drawer of this item will read. It was not written this turn only because the file was contested.
3. **The reader-facing concern in the item's WHY survives its remedy.** Two families on one page
   is a real cost to a reader. The answer is the rival's — label the operating points — not a
   pooling that makes the two indistinguishable.
