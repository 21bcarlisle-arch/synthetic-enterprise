# WORKER FINDING — the L1.1 band conditions on a BINARY, and the world has three heating regimes

**Found:** 2026-08-09, first run of the two-level test on a drawn population.
**Class:** R10 (the instance fix on 2026-08-08 did not close the class).
**Disposition:** QUEUED as an atom. NOT fixed on sight.
**Owner atom:** `H_GAP_fabric_belief_truth_gap`.

## The recurrence, stated plainly

On 2026-08-08 the L1.1 half-hourly-texture band was found to be **gas-shaped**: a single 0.15
floor, whose own anchor text reasons from a gas premise, was being applied to a heat-pump home
whose heating is 49% of its electricity and contributes almost no period-to-period movement.
The fix conditioned the band on `household.is_gas_heated` and derived an electric band of
0.0705 from published sources.

That fix conditions on a **boolean**. The first drawn population contains a third regime:

| premise | fabric | heating | L1.1 texture | judged by |
|---|---|---|---|---|
| P0197 | terraced, pre-1919, EPC C | `electric_storage` | 0.0414 | `L1.1e` (band 0.0705) |

`L1.1e` was derived from **heat-pump arithmetic**: 9500 kWh gas × 0.825 boiler efficiency ÷ 2.78
SPFH4 = 2,819 kWh of heat-pump electricity against a 2,500 kWh behavioural baseline, giving
53.0% of the mean and hence 0.15 × 0.470 = 0.0705.

A storage heater is **resistive**. Its SPF is ~1.0, not 2.78. The same 9,500 kWh of gas heat
becomes ~7,800 kWh of electricity, not 2,819 — so the behavioural (textured) fraction of its
load is ~24%, not 47%, and the correct band by the band's own derivation is roughly
`0.15 × 0.24 ≈ 0.036`, not 0.0705. **P0197 measures 0.0414, which passes a resistive-heat band
and fails a heat-pump one.** It is being failed by a threshold derived for a different machine.

`observed-with-evidence`: the numbers above are measured. `inferred`: that a correctly-derived
resistive band would pass P0197 — the derivation above is arithmetic on the existing anchors and
has not itself been built or tested.

## The class, not the instance (R10)

The defect is not "storage heaters need a band". It is that **the band is keyed on a boolean
where the physics is keyed on a delivered-efficiency ratio**. Every heating regime with a
different SPF needs its own rescaling of the same behavioural floor, and there are at least
four in `HeatingSystem` (gas boiler, ASHP, GSHP, resistive), plus district heat which meters
neither commodity.

The class fix is a band that is a FUNCTION of the assumed seasonal efficiency of the premise's
heat source, so a heating system added to `HeatingSystem` cannot silently inherit a band derived
for a different one. A fifth `is_x_heated` boolean would be the same defect a third time.

## Why it surfaced only now

The authored panel has one electrically heated home and it is a heat pump. Drawing the
population from published heating shares (EHS AT3_1/AT4) put resistive electric homes into the
measurement for the first time — 9 of 200, which is roughly what England has. A chosen panel
cannot find this; that is the argument for the population, and it found it on the first run.

## What must NOT be done

Marking L1.1 UNVALIDATED, or widening the electric band to 0.0414 so the suite goes green.
Either turns a real physical distinction into a threshold edit (R12).
