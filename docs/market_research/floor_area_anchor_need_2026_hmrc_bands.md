**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_18_the_housing_joint_the_sample_and_the_ceiling

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. These are the anchored rows it will be built from; this declaration is replaced when
the page lands.

# Floor area, anchored: HMRC bands and what they do to metered consumption

**Measured 2026-09-05**, delivery seat, `W2_18` stage 1. Source pulled and computed the same day;
raw file stays out of the repo (15 MB, `~/.cache/synthetic-enterprise/need_2026/`), as the weather
grids do.

---

## The source, and why it is not the one the ruling named

The housing ruling names the **EPC register** as the anchor for floor area. That route needs a
GOV.UK One Login account, which is a real-world credential nobody here should mint unilaterally —
and it is the *worse* source anyway, on two counts the ruling itself flags: EPC covers ~60% of
stock and is transaction-biased (rented and recently-sold over-represented), and its consumption
figures are SAP-modelled rather than metered.

**DESNZ's NEED anonymised sample is open, needs no account, and is better on both counts.** It is
`anon2026_50k.csv` — 50,000 dwellings, one row each, published 11 June 2026, the same artefact
this project already used for the high-tail gas anchor (`need_domestic_gas_high_tail.md`), so the
sourcing precedent and its lineage checks are established rather than new.

And the provenance is better than expected: NEED's floor-area band is sourced from **HM Revenue &
Customs**, per DESNZ's own metadata — valuation data over the full 21.6m-property NEED population,
not a modelled certificate over a transacting subset.

## The bands

DESNZ metadata, verbatim: `1 = 50 or less; 2 = 51 - 100; 3 = 101 - 150; 4 = 151 - 200; 5 = over
200 (square metres)`.

## Floor area by property type — and bungalows are a first-class type

Share of the 50,000-dwelling sample:

| band m² | Bungalow | Detached | End terrace | Flat | Mid terrace | Semi detached |
|---|---:|---:|---:|---:|---:|---:|
| ≤50 | 0.4% | 0.0% | 0.0% | **16.2%** | 0.1% | 0.0% |
| 51–100 | 5.8% | 1.7% | 6.0% | 7.4% | **13.0%** | **15.3%** |
| 101–150 | 1.5% | **8.0%** | 2.3% | 0.2% | 5.2% | 8.7% |
| 151–200 | 0.2% | 3.5% | 0.2% | 0.0% | 0.5% | 0.8% |
| >200 | 0.1% | 2.4% | 0.1% | 0.0% | 0.1% | 0.3% |

**Bungalow is 7.9% of the sample and is its own `PROP_TYPE`**, which closes the ruling's
"bungalows are folded into detached" gap with a published share rather than an argument. Its floor
area distribution is nothing like detached: bungalows concentrate in 51–100 m² where detached
concentrates in 101–150.

## What floor area does to METERED consumption

2024, weather-corrected gas, from the same rows:

| band m² | dwellings | median gas kWh | gas rows | **censored** | median elec kWh |
|---|---:|---:|---:|---:|---:|
| ≤50 | 8,375 | 5,700 | 3,878 | **54%** | 2,000 |
| 51–100 | 24,567 | 9,000 | 20,926 | 15% | 2,400 |
| 101–150 | 12,938 | 12,100 | 11,670 | 10% | 2,900 |
| 151–200 | 2,644 | 16,200 | 2,168 | 18% | 3,700 |
| >200 | 1,476 | 23,000 | 860 | **42%** | 5,300 |

Median gas runs 2.56× from the modal band (51–100) to the top band. This is the quantity the
ruling's §3.2 coverage curve is about, and it is now measured rather than assumed.

## THE CENSORING, and it bites at both ends

DESNZ blanks any annual gas reading **under 1,000 or over 50,000 kWh**. That is not missing data
scattered at random — it is a cut at each tail, and the two extreme bands are where it lands:

- **≤50 m²: 54% censored**, overwhelmingly the *lower* cut. The 5,700 median is computed on the
  46% of small flats that use enough gas to be retained, so it **overstates** the band.
- **>200 m²: 42% censored**, overwhelmingly the *upper* cut. The 23,000 median is computed on the
  58% that stay under 50,000 kWh, so it **understates** the band — and understates it exactly where
  the ruling says the money and the risk are.

Both directions are stated because both run against a clean reading. The true spread across floor
area is **wider than 2.56×**, and this source cannot say by how much. A percentile above the
censored share is unmeasurable here and is not computed.

## Gaps this leaves, named rather than filled

- **Roof area, pitch, flat-versus-house.** No source consulted here carries it. The ruling
  anticipated this as the expected gap; it stays a registered gap with its consequence — the PV
  ceiling per house cannot be stated in kWh without it, only bounded by aspect.
- **Current settings — flow temperature, heating and hot-water schedules, thermostat set-point.**
  **Deliberately out of phase 1** (director, 2026-09-05): *"The lever only means something once
  there's a product that could turn it down, and that isn't built. Don't invent hidden state for a
  ceiling nothing can act on."* `flow_temp` has zero occurrences anywhere in `simulation/`, and it
  stays that way until a product exists that would act on it. The consequence is stated so it is
  not rediscovered as an oversight: **the flow-temperature turn-down lever's ceiling is
  unstateable, not merely uncomputed**, and any later claim about it must begin by drawing the
  setting.
- **Floor area is BANDED, not continuous.** Five bands, and the top one is open-ended above 200 m².
  A continuous draw within a band is an interpolation choice, not an anchored quantity, and must be
  registered as a Choice when it is made.
- **England and Wales only.** Scotland has a separate register; the ruling is GB, so Scottish floor
  area is unanchored by this source.

## What this is validated against, and what it is not

Generation and validation from separate sources is the ruling's rule. These rows are **generation**
figures — the joint the draw will be fitted to. They are NOT a validation of the SIM's consumption,
and must not be used as one: NEED is also the source behind the existing high-tail gas anchor, so
checking the SIM's gas against NEED after fitting the SIM's floor area to NEED would be a
tautology. Validation belongs to a source with different lineage.
