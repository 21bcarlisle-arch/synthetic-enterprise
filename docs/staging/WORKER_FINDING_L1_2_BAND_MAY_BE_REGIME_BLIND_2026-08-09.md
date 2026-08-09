# WORKER FINDING — the L1.2 band may be regime-blind in exactly the way L1.1's was

**Found:** 2026-08-09, first population-scale run of the two-level test after the rate restatement.
**Class:** R10 (suspected recurrence of a class closed once at L1.1 — the SAME class, a different cell).
**Disposition:** QUEUED as an atom. NOT fixed on sight — not blocking, and the supply of harness
findings is infinite (SELF_INTERRUPT_DISCIPLINE).
**Owner atom:** `H_GAP_fabric_belief_truth_gap`.

## Observed, with evidence

`observed-with-evidence`. On the drawn population (n=200, `population_seed=17`, real Open-Meteo
archive 2022-01-01..2022-04-30), `L1.2_day_to_day_shape_correlation` fails with 2 of 200 homes
outside band, and the worst is **P0197 = 0.8868 against `at_most 0.85`**.

P0197 is the same home that produced the L1.1 finding on 2026-08-08: terraced, pre-1919, EPC C,
**`electric_storage`** heating. It is now the worst home in a *second* cell.

## The suspicion, stated as a suspicion

`inferred`, and deliberately not claimed as established. L1.2 is the Pearson correlation between
consecutive days' 48-vectors, normalised to daily total — a measure of how repeatable a home's
daily *shape* is. A storage heater charges on a **fixed overnight timer**. Its shape is supposed to
repeat: that is what the appliance does. A band of 0.85 derived from homes whose heat is demand-led
may simply be the wrong band for an appliance that is clock-led, in the same way the 0.15 texture
floor was the wrong band for a home whose heat is on the electricity meter.

If that is right, this is the L1.1 class recurring at a second cell: **a band keyed on a
population whose heating regime it never names.** The class fix at L1.1 was to make the band a
function of delivered seasonal efficiency rather than a boolean; the analogous question here is
whether L1.2's band should be a function of whether the heating load is *thermostatically* or
*schedule* driven.

## What must NOT be done

Widening 0.85 until P0197 passes. That is the threshold edit R12 forbids, and it would be the
third time this suite was asked to go green by moving a number rather than by naming a mechanism.
Equally, marking L1.2 UNVALIDATED would retire a control that is currently *working* — it caught a
real distinction on its first population run.

## Also not to be done: reading this as a reason to restore W1_12's L3

`W1_12_premise_trace_generator` was corrected 3->2 this tick because its named exit test stopped
reproducing at population scale. **This finding does not undo that**, for two reasons:

1. It touches L1.2 only. The other failing cell, `L1.5_max_multiplicity_share`, is **7 of 200**
   homes and is a structural artefact detector — it has nothing to do with heating regime, and it
   is the cell the spec calls "the sharpest control in the suite ... near-impossible to game".
2. Even on L1.2, the correct outcome if the suspicion holds is a **re-derived** band, which may
   pass P0197 and may not. Until that derivation exists, "the band might be wrong" is not evidence
   that the generator is right.

## Proposed work (the atom)

1. Establish whether `HeatingSystem` distinguishes clock-led from thermostat-led heat at all; if
   it does not, that absence is the finding, not the band.
2. Derive an L1.2 band per regime from published sources, or register the gap as a NEED anchor and
   report the cell as judged-per-regime with the storage case UNVALIDATED **and counted**
   (`homes_unjudged` already exists and already feeds the coverage floor).
3. R15 both ways: the re-derived band must still fire on the replay-a-single-day mutation the
   spec names for L1.2, and must not fire merely because a home is storage-heated.
