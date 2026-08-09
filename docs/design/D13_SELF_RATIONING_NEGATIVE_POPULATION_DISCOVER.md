# DISCOVER — the self-rationing pairs need a negative population, and it cannot be borrowed

**Atom:** `D13_self_rationing_negative_population_discover` · **Stage:** DISCOVER (doc-only, no build)
**Minted:** 2026-08-09 by the `D12_detection_cell_grid_is_recall_only` build
**Owns the debt registered against:** `couple_w2_5_c7.detection`, `couple_w2_8_c10.detection`
in `tools.couple_w2_11_d5.DETECTION_DIRECTION_CONTRACT`

## Why this is a DISCOVER and not the other half of D12

D12's mint named two jobs and warned they were not one job. It was right, and the build confirmed
it from the inside:

* **The cell grid** (built, 2026-08-09) needed **no new denominator**. Its negative population is
  the same `never_flaggable` set the payment headline already uses — a payment whose cash arrived
  on or within the reconciliation grace — and that is a **per-record property**, so splitting it by
  regime is arithmetic. Nothing was modelled; a set already in hand was partitioned.
* **The two self-rationing pairs** have no such set. `detection_measures` requires the cases a flag
  would be **wrong** on, and "a household that is **not** self-rationing" is a **continuum the
  harness labels by threshold**. Choosing that threshold *is* choosing the measure.

## The evidence that the choice is worth a DISCOVER

D11 already ran this experiment by accident, and it is the single most useful number here:

| denominator | measured wrongful-dunning rate (seed 7) |
|---|---|
| `universe − truth_set` — "everything that did not fail" | **0.2834** |
| cases a flag would genuinely be **wrong** on | **0.0269** |

Same company, same world, same flagged set — **a factor of ten**, entirely decided by which cases
the denominator was willing to call an error. On the self-rationing pairs that choice is not even
constrained by a settled fact like "the cash arrived"; it is a threshold on a continuum. Inventing
one to empty the register faster would publish a number nobody should believe, and it would land on
a **published** dimension.

D12's own build re-confirmed the direction of the risk: reshaping the payment cells moved the lit
cell from **0.1031 → 0.0584** with no change whatsoever in company behaviour. A measure change moves
a published figure hard. That is survivable when the new denominator is a fact (D12) and is not when
it is a modelling choice made to close an atom (this).

## What this DISCOVER must answer before any build

1. **Is there a settled-fact negative for self-rationing at all?** The payment pair's negative is
   settled because cash either arrived within grace or it did not. Ask whether W2_5/W2_8 have any
   equivalent observable — a household that demonstrably did *not* ration (e.g. consumption at or
   above its own weather-normalised expectation through a cold spell) — rather than a threshold on
   a rationing score.
2. **If the honest answer is "only a threshold exists," does the dimension publish a false-flag
   rate at all?** A defensible outcome of this DISCOVER is **"no second direction is publishable
   here"**, kept as permanent registered debt with that finding as its reason. That is a better
   result than a fabricated denominator, and the register is built to hold it.
3. **Sensitivity before commitment.** Whatever candidate negative population is proposed, measure
   the false-flag rate across its plausible threshold range **first**. If the rate swings the way
   D11's did, the threshold is the measure and must face the director as a curriculum-shaped call
   (R13), not be chosen by the agent that benefits from the atom closing.
4. **Three populations, not two** (the standing finding from D11's build): must-flag, must-not-flag,
   and **neither**. Any proposal that derives the second as the complement of the first is asserting
   no third exists — state explicitly what lands in `n_excluded` and why.

## What already protects this in the meantime

The debt cannot be quietly declared paid.
`tests/tools/test_couple_w2_11_d5.py::test_every_published_detection_dimension_declares_its_error_directions`
scores the **flag-EVERYTHING** degenerate through each register entry's own scorer: an entry
declaring itself two-directional while still handing that degenerate a perfect 0.0 **fails**. Both
self-rationing entries are registered as recall-only with `debt_atom` pointing here, so the control
holds them honest without this DISCOVER being finished.

**R12 note.** Nothing in this DISCOVER may be closed by making a metric look busier. The correct
output is a *finding about what is measurable*, up to and including "not measurable here, and this
is why."
