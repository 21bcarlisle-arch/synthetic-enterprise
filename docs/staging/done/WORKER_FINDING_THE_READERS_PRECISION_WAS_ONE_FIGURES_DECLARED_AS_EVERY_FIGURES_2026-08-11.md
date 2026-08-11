# H27 Expert Hour #16 — the reader's precision was one figure's, declared as every figure's

**Date:** 2026-08-11 · **Atom:** `H27_payment_belief_gap` (HARDEN, self-refill draw 2→3)
**Subject:** `tools/couple_w2_11_d5.py` · **Reshape minted as:**
`D34_the_resolution_floor_covers_two_of_five_figures` (L0)
**Held at L2.** Sixteen Hours, sixteen defects, and #16 changed the instrument again.

---

## The leads this took

Hour #15 left three. This Hour answers **lead 1** with a measurement and takes **lead 2**,
and they turned out to be the same question:

> **1.** Every declared collapse run, saturation edge and band is derived at bit-equality. How
> many of the other declared edges move at the reader's precision has **not** been measured.
> **2.** The four `DIMENSION_DRIFT_RESOLUTION`-sourced cells pass the new subject check because
> their register is keyed by dimension — which proves the *source* is about the right figure,
> **not** that the numbers in their sentences match what the published figure does.

Both need one number: **what precision is the reader actually given?** Hour #15 had installed
exactly that number, one Hour earlier, as `PUBLISHED_GAP_DECIMALS = 4` — "the precision every
consumer renders these gaps at", with an independence re-read so that "a consumer that starts
publishing 6dp fails the control instead of leaving the epsilon stale".

It is not every consumer's precision, and it does not fail.

## Finding (1): the re-read cannot fail on the change it was built to catch

`_consumer_render_decimals` collected **every** `.Nf` in the anchored function and asked only
whether `4` was among them. `format_belief_summary` renders three other rates at `.4f` and the
mean-steps figure at `.2f`, so it already returned `{2, 4}` — a set, not a precision.

Mutated live on a copy of the tree, moving the **belief gap's own** render to `.6f`:

```
after mutating the BELIEF GAP render to 6dp: {'background/gap_metric.py': (2, 4, 6), ...}
does the shipped check still pass? True
```

A membership test over every number in a function is not a check on the one number the figure is.
This is the "grader quoting its own detection marker" shape one register over: the control's
subject was the *function*, and the thing it was defending was one *expression* inside it.

## Finding (2): it is the BELIEF reader's precision, declared as every reader's

The keyset was two hand-typed consumer sites, both BELIEF, while **five** dimensions are
published. Read off the shipped renderers (AST, not grep):

| dimension | how the gap reaches the reader | **dp** |
|---|---|---|
| `belief` | `format(result.gap, ".4f")` | 4 |
| `belief_population_mix` | live writer, `f"{result['belief_population_mix'].gap:.4f}"` | 4 |
| `detection` | `format(result.gap, ".4f")` | 4 |
| **`ageing`** | `_num("balanced_bucket_displacement", ".3f")` — **never renders `.gap` at all** | **3** |
| **`detection_latency`** | `f"detection latency {mean:.2f} days mean"` | **2** |

The one global constant is **ten times too fine** for one published figure and a **hundred times
too fine** for another. And note *how* those two arrive: neither renderer formats `.gap`. The
ageing headline reaches its reader as a component, the latency headline through a local alias
(`mean = c.get("mean_lag_days")`). A walker looking only for `.gap` finds no render for two of the
five figures — and the fallback is the house default, which is the defect.

It is not only latent. `_own_floor_clause` publishes, to the reader of **both** belief numbers:

> "…at the **4dp every consumer renders these gaps at**…"

That sentence is false of two of the five figures this module publishes. It is the same shape as
Hour #15's own defect — one sentence rendered for figures that do not share the number in it —
in the very clause Hour #15 wrote to close it.

And lead 2's own extension would have walked straight into it: measuring the ageing and latency
floors with `published_reading_epsilon()` would have certified them at 10× and 100× the step
their readers are given, **understating those figures' blindness** — the same direction as before.

## What lead 1's measurement actually says (and it is good news)

Re-derived every declared band, edge and collapse run at each dimension's **own** reader
precision — dense book-derived grids, n=300, seeds 7/11/23, both knobs:

* **terms knob**, `DIMENSION_DRIFT_RESOLUTION`: `detection` (4dp), `detection_latency` (2dp) and
  `ageing` (3dp) reproduce their declared runs and edges **exactly**, bit-equality and reader
  precision agreeing.
* **recon knob**, `ORGAN_QUERY_GRID`: `flagged_via_reconciliation` (−6/+82, 16 runs) and
  `recon_lag_days` (−19, 1 run) likewise reproduce at 4dp.

So the bit-equality divergence **atom D33 owns is confined to the belief cells**. That bounds
D33's blast radius, which was the open question, and it is why **no published number moves here**.
It is also exactly why the control matters: the declared numbers are right today by a property of
this book, and the control that certifies them was reading somebody else's epsilon.

## Closed at the class (R10)

* **`PUBLISHED_GAP_CONSUMERS`** — the precision is now **per dimension**, keyset **DERIVED** from
  `published_dimensions` both ways: a published figure with no entry RAISES (the fallback IS the
  defect), an entry for a figure nobody publishes RAISES.
* **`measure_published_reading_precision`** reads the number off **the format spec that renders
  THAT DIMENSION'S GAP** — through one level of local alias, through the component where the gap
  reaches the reader as one, and through a `Subscript` key so one shared renderer (the live
  writer's `measure_and_write`) cannot lend a sibling's precision to this figure (the D32
  wrong-subject rule, applied at the render site).
* **The component carrier is checked NUMERICALLY.** "`balanced_bucket_displacement` *is* the
  ageing gap" is a claim about arithmetic in another module; it is measured against a real
  scoring (delta 4.1e-7, inside that figure's own 5e-4 step), never taken on the name. A carrier
  with nothing to check it against is a violation — an unavailable check is a failed check.
* **Everything unreadable RAISES.** Absent consumer file, absent renderer, a gap with no
  fixed-point render at all. The pre-Hour version returned `()` for a missing file and its caller
  read that as agreement.
* **`published_reading_epsilon()` REFUSES a caller that names no figure** (the `_own_floor_clause`
  precedent). A default epsilon is how the belief reader's 4dp came to certify a figure published
  at 2dp.
* **The floor takes its epsilon per figure**, and the caveat sentence now states *this* figure's
  consumer's precision.

## R15 both ways — eleven mutations, each firing by name

The gap render moved off its declared precision (**the pre-Hour defect**, on `belief`, and on both
figures the constant was wrong about); one gap rendered at **two** precisions; the consumer **file**
absent (fail-silent); the renderer renamed away; a gap with **no** fixed-point render (fail-open);
a published dimension dropped from the register (raises); an entry for a figure nobody publishes
(raises); a component carrier that is **not** the gap; a component carrier **nothing checked**; a
bare `published_reading_epsilon()`; and a **vacuity guard** — a register giving every figure the
same number would be the pre-Hour constant wearing a dict, so the 2–4dp spread itself is pinned.

## R12

**No published number moved.** All five figures bit-identical before and after (`ageing`
0.11296259117981663, `belief` 0.1518987341772152, mix 0.07999999999999997, `detection`
0.014505119453924915, `detection_latency` 2.343137 at seed 7). What moved is what the instrument
admits about itself — and one published caveat sentence that was false.

## Why still L2

Sixteen Hours, sixteen defects, none predicted by the Hour before it. This one was found *inside
the control the previous Hour built to close the previous defect* — the third time that has
happened in this module. Hour #4's stated-in-advance criterion of **two consecutive clean Hours**
has still not been approached.

## Hour #17 leads, in order

1. **The reshape is D34 and it is unbuilt: the floor covers two of five figures.** Lead 2's
   remaining half is now *answerable* — each figure has a measured reader precision — but
   measuring per-figure resolution floors for `detection`, `detection_latency` and `ageing` at
   their own coarser steps, and stating them, moves published caveat text on three dimensions.
   That is a reshape with real blast radius, not a fix on sight.
2. **The precision is read; the ROUNDING before it is not.** `balanced_bucket_displacement` is
   the ageing gap already rounded to 6dp before any render, and `detection_latency`'s gap arrives
   at 6dp too. Two quantisations sit between the scorer and the reader and only the outer one is
   measured — a component whose own rounding is coarser than its render would make the render
   precision a decoration.
3. **Carried forward, still untaken:** the interior collapses have no owner of their own (Hour
   #11's lead 1, four times deferred); and Hour #8's two — the pinned generated value
   `assert c["n_recon_detected_undated"] == 0`, and whether the other dimensions' normalisation
   notes have the same gap between what they DENY and what they ESTABLISH.
