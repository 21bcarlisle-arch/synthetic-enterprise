# External anchor: the HIGH TAIL of domestic annual gas consumption (W1_13)

**Atom:** `W1_13_high_tail_gas_anchor` — the named, measured blocker on `W1_11_fabric_physics_core` L2→L3.
**Question it must settle:** is a 43 MWh/yr domestic gas customer a real category, or a modelling artefact?
**Date measured:** 2026-08-03 (worker tick). **Network probed, not assumed** — available.

## Why this had to be external

The fabric seam measured C4 (a 116 m² pre-1919 detached, HLC 0.595 kW/K) at **43,338 kWh/yr gas**, against
`RESI_CONSUMPTION_ENVELOPE_GAS`'s high bound of **40,000**. Both sides of that disagreement were internal:
the bound was set from the *previous* generator's observed maximum (35,913 kWh/yr), and the 43,338 is this
sim's own new physics. Two internal numbers disagreeing is not evidence about the world, and R12 forbids
closing it by moving either side to fit the other.

## Source — the publisher's own tables, not an aggregator

**Publisher:** Department for Energy Security and Net Zero (DESNZ).
**Publication:** National Energy Efficiency Data-Framework (NEED), 2026 release, published **11 June 2026**.
**Coverage:** England and Wales. **Consumption year 2024.** Gas figures are **weather-corrected**
(adjusted to remove year-on-year weather differences) and rounded to the nearest 100 kWh. The gas year is
not a calendar year.

Two artefacts from the same publisher were used, and they answer *different* halves of the question:

| # | Artefact | What it gives | Population |
|---|---|---|---|
| 1 | `Consumption_multiple_attributes_EW_2024.xlsx` — published aggregate | mean / LQ / **median** / UQ by property type × **property age** × bedrooms × region | full NEED population (21.6m properties) |
| 2 | `anon2026_50k.csv` — anonymised record-level sample + `NEED-2026-anonymised-dataset-metadata.ods` | **one row per dwelling**, so any percentile can be computed | stratified random sample, 50,000 dwellings |

Artefact 1 carries an explicit **`Pre 1919`** property-age category — the exact dwelling class this atom
names. Artefact 2's `PROP_AGE_BAND` is coarser (**`1 = before 1930`**, per DESNZ's own metadata), so the
record-level tail below is measured on a class that *includes* 1919–1929 stock. That stock is largely
cavity-walled and therefore cheaper to heat than pre-1919 solid wall, so **every record-level percentile
here is, if anything, an UNDER-estimate of the true pre-1919 solid-wall tail.** The bias direction is
stated because it runs against the conclusion, not with it.

**Lineage check applied (prior lesson: agreeing sources may share lineage).** Artefacts 1 and 2 share the
NEED lineage, so their agreement validates the *sampling*, not the *source*. No secondary aggregator was
used for any figure; every number below comes from a DESNZ file.

## THE CENSORING FACT, which turned out to be the decisive one

DESNZ's own metadata for the anonymised dataset:

> `Gcons2005,…,Gcons2024` — Annual gas consumption rounded to the nearest 100 kWh … Blank values are
> either missing or **removed due to being too large (over 50,000 kWh)** or too small (under 1,000 kWh).

and the validity flag vocabulary: `G = annual consumption over 50,000 kWh`.

So the national statistical authority's **own operational threshold for "too large to be a domestic gas
reading" is 50,000 kWh/yr** — and it publishes a count of the dwellings that exceed it. That is the same
*kind* of object as the company's plausibility envelope: a published cut-off for domestic absurdity.

It also means the data is **right-censored at 50,000**. Any percentile above the censored share is
unmeasurable from this source, and is reported below as such rather than quietly computed on the retained
subset.

## Measurement 1 — the published aggregate, `Pre 1919` **detached**, gas-heated, 2024

n-weighted across all English regions and Wales. Source: artefact 1.

| bedrooms | n | mean | lower quartile | **median** | upper quartile |
|---|---:|---:|---:|---:|---:|
| 1 | 989 | 12,514 | 6,688 | 10,663 | 16,467 |
| 2 | 24,045 | 15,355 | 9,990 | 14,413 | 19,620 |
| **3** | **72,173** | **18,244** | **12,378** | **17,283** | **23,068** |
| 4 | 57,636 | 22,591 | 15,714 | 21,670 | 28,776 |
| 5 or more | 39,195 | 27,705 | 19,919 | 27,654 | 36,090 |
| **all** | **194,038** | | | **~20,292** | |

All figures kWh/year.

## Measurement 2 — the record-level tail (the part an aggregate cannot give)

Source: artefact 2, gas-heated (`MAIN_HEAT_FUEL = 1`), valid readings (`GasValFlag2024 = V`).
"censored" = `GasValFlag2024 = G`, i.e. **above 50,000 kWh/yr**.

| class | n | median | p90 | p95 | p99 | max | **censored >50k** |
|---|---:|---:|---:|---:|---:|---:|---:|
| all gas-heated | 37,400 | 10,000 | 19,500 | 23,500 | 34,300 | 49,900 | **0.57%** |
| Detached (any age) | 6,205 | 13,600 | 25,000 | 30,600 | 41,100 | 49,900 | 1.58% |
| Detached, pre-1930 | 573 | 20,400 | 35,100 | *40,885* | *48,608* | 49,900 | **8.6%** |
| **Detached, pre-1930, 101–150 m²** | **197** | **16,800** | **27,760** | **31,720** | **38,900** | 49,900 | **0.00%** |
| Detached, pre-1930, >150 m² | 335 | 24,600 | *40,260* | *44,010* | *49,528* | 49,900 | **13.3%** |

*Italicised percentiles sit above the censored share for their row and are therefore computed on the
retained subset only — they are biased LOW and are not safe anchors. The 101–150 m² row has **zero**
censoring, so its percentiles are reliable; that is the row C4 belongs to.*

**Cross-check of artefact 2 against artefact 1** (validates the 50k sample, not the source): sample
pre-1930 detached median **20,400** vs published Pre-1919 detached all-bedrooms **20,292** (0.5% apart);
sample 101–150 m² median **16,800** vs published 3-bedroom median **17,283** (2.8% apart). The sample
tracks the 21.6m-property aggregate.

## Share of the real stock the company's 40,000 bound calls implausible

Counting censored records as exceedances (they are known to be >50,000):

| class | exceeds **40,000** | exceeds **50,000** |
|---|---:|---:|
| all gas-heated E&W | **1.02%** (1 in 98) | 0.57% |
| Detached, pre-1930 | **14.1%** (1 in 7) | 8.6% |

## VERDICT — which side moves

### Q1. Is a 43 MWh/yr domestic gas customer a real category? **YES, unambiguously.**

It is not a rarity requiring special pleading: **1 in 98** gas-heated homes in England and Wales exceeds
the company's 40,000 bound, and among pre-1930 detached homes — C4's own class — **1 in 7** does. DESNZ
retains domestic gas readings as valid all the way to 50,000 kWh/yr and still finds 0.57% of the national
gas-heated stock above even that.

### Q2. Is 43,338 plausible for **C4 specifically** — 116 m², pre-1919 detached? **Extreme but real: ~p99 of its own size band.**

Against the reliable, uncensored row: median 16,800, p95 31,720, **p99 38,900**, max 49,900. C4 sits above
p99 and at 2.6× its class median. Real dwellings in exactly that age/type/size band reach 49,900. So the
figure is at the top of the observed range rather than outside it — and C4 is the deliberately-worst-fabric
archetype in the book (uninsulated solid wall, single glazing, 1 ach), which is the premise a p99 reading
should belong to.

### THE ENVELOPE MOVES. The fabric parameterisation is FLAGGED, not falsified.

**`RESI_CONSUMPTION_ENVELOPE_GAS.high`: 40,000 → 50,000 kWh/yr**, anchored on DESNZ NEED's own validity
threshold and cited as such.

The justification does **not** depend on C4. An invariant whose entire job is to catch absurdity was
flagging **14.1% of a real, common dwelling class** as implausible. That is not a plausibility band; it is
a false-positive generator, and it was falsified the moment the external distribution was read. It would
have to move even if the fabric model had never been built.

**The R12 defence, stated because the ordering invites the suspicion.** 50,000 is not "43,338 plus
headroom" — it is the number DESNZ itself uses to decide a domestic gas record is too large to publish,
chosen by the publisher, for the same purpose, before this sim existed. The counterfactual is the test:
**had C4 come in at 55,000, this anchor would not have covered it, and the FABRIC would have been the side
that moved.** The anchor was selected by what it is, not by what it clears.

**What is flagged and deliberately NOT acted on:** C4 at ~p99 of its size band is recorded as a named
residual with its measured percentile. One deliberately-worst archetype at p99 is expected. **A second
premise above p99, or any premise above 50,000, is a physics finding** — the candidates named by this
atom's own FRAME, in order: the RdSAP U-value floors for solid walls, the ventilation rate, and the comfort
setpoint for a household in a dwelling this expensive to heat. Damping the generator now would be
goal-seeking a band (R12), and the band is the side the evidence moved.

**R13:** this is a BASELINE fidelity change, decided blind to company P&L. The measurement was taken and
recorded before anyone looked at what it does to margin.

## The finding worth carrying: the bound is the wrong SHAPE, not merely the wrong VALUE

43 MWh/yr is unremarkable for a pre-1919 detached and would be a screaming defect on a 2-bed post-2000
flat. A single national scalar cannot express that, so at 40,000 it was simultaneously **too tight** for
old detached stock (14.1% false positives) and **far too loose** for a modern flat, where the same reading
is roughly 4× the class median and would pass silently. Widening it to 50,000 fixes the false positives
and makes the second problem slightly worse.

The right shape is a **class-conditioned envelope** keyed on dwelling type/age/floor area, for which this
document now supplies the published distribution. That is registered as a finding, not built here
(SELF_INTERRUPT_DISCIPLINE: queue, don't fix on sight — the machine is not blocked).

**Control-set hole found en route:** `RESI_CONSUMPTION_ENVELOPE_GAS` had **no test of its own** — the one
test named for the envelope class (`test_resi_consumption_envelope_catches_gross_implausibility`) exercises
only the *electricity* invariant. The gas bound could have been any number at all and the suite would have
stayed green. Closed here.

## Sources

- [NEED consumption data tables 2026 (DESNZ, 11 June 2026)](https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-consumption-data-tables-2026)
  — `Consumption_multiple_attributes_EW_2024.xlsx`
- [NEED anonymised data 2026 (DESNZ, 11 June 2026)](https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-anonymised-data-2026)
  — `anon2026_50k.csv`, `NEED-2026-anonymised-dataset-metadata.ods`
- [NEED collection page (DESNZ)](https://www.gov.uk/government/collections/national-energy-efficiency-data-framework-need)
