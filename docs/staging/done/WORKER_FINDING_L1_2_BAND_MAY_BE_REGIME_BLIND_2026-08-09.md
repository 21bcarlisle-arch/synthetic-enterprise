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

---

## RESOLVED 2026-08-09 (commit be8774d9c) — the suspicion held, its stated mechanism did not

`observed-with-evidence`. The suspicion above was right about the CLASS and wrong about the
appliance, and both halves are worth keeping.

**Right:** the band was regime-blind, and the deficit decomposes entirely to a load the band
was never written to judge. Day-to-day shape correlation of the HEATING stream, measured by
regime on the drawn population: gas combi 0.9197, gas system 0.9080 — on the GAS meter, where
L1.2 never sees it — against electric storage 0.9133 on the ELECTRICITY meter, where it does.
Behaviour scores 0.21–0.32 in every regime. The generator makes heat equally repeatable and
behaviour equally diverse whatever the machine; the only thing separating a home that breached
L1.2 from one that did not is which meter its heat lands on.

**Wrong:** the proposed mechanism — "a storage heater charges on a fixed overnight timer" — is
not what this model does. `HeatingSystem.ELECTRIC_STORAGE` maps to `ControlMode.ON_OFF_DEADBAND`
and `simulation/premise_trace.py` contains no charge window at all. Step 1 of the proposed atom
asked exactly this question and its answer is the second finding, now registered as W1_12
simplification 8 and filed at
`docs/staging/WORKER_FINDING_THE_MODELS_STORAGE_HEATER_IS_NOT_ONE_2026-08-09.md`.

**How it closed, against this doc's own two prohibitions.** Not by widening 0.85 — the threshold
is untouched. Not by marking L1.2 UNVALIDATED — the cell is live and every one of the 200 homes
is still judged by it (`homes_unjudged` 0). Step 2's fallback (report the storage case unjudged
and counted) was NOT needed, because a third option existed that this doc did not consider:
judge every home on the SAME LOAD SET. The band's anchor text describes a household, so the cell
is computed on the meter net of space heat (`meter_net_of_space_heat`) — a bit-identical no-op
for the 190 of 200 homes heated off the electricity meter, and no new number anywhere. What was
netted out is reported next door as `L1.2h_heating_shape_repeatability`, UNVALIDATED with a NEED
anchor, at 0.9635 on P0197 — this doc's own worst home.

Step 3's R15 requirement is met both ways: a replayed behavioural shape still drives the cell to
1.0 and fails THROUGH the netting, and stripping the split judges the whole meter and goes red
again on the same homes.

**And on the last section:** this doc was right to say a re-derived band "may pass P0197 and may
not", and right that L1.5 had to close on its own. It did, earlier the same day, by fixing the
generator. W1_12 is L3 on the two cells closing separately, not on this one being talked around.
