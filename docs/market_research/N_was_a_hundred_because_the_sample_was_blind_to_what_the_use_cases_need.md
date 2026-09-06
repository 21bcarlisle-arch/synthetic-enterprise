**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_22_the_sample_is_space_filling_and_rejects_on_outputs

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. This corrects a figure that page would otherwise have published; the declaration is
replaced when the page lands.

# N was 100 because the sample was blind to what the use cases need. It is over 250.

**Measured 2026-09-06**, delivery seat, `W2_22`. **This corrects a figure I landed the same day** in
`coverage_curves_and_N_reject_on_outputs_not_labels.md`.

---

## What I published, and why it was too small

That document reported **N ≈ 100 covers 99.6% of the output space**, and flagged the limit honestly:
the output space was *level only* — annual gas and electricity — with shape and weather gradient
absent from NEED, so "N ≈ 100 is a LOWER bound".

The director's sequencing ruling the same day says why that limit is the whole question:

> *"It tells stage 1 what it is building for, so the samples cover the variation the use cases will
> need rather than variation for its own sake."*

The use-case register names what they need. Reading §2 of it, the output dimensions the use cases
are scored on are: weather **gradient** (1.2 self-rationing, 2.1 budget billing, 3.1 hedging),
half-hourly **shape and presence** (2.2), **per-asset** consumption (4.5), **arrears trajectory**
(1.1) — and **bill-shock exposure** (2.1). Not one of them is level.

## The one extra dimension NEED can supply

NEED carries twenty years of annual gas per dwelling. Over the last six years, per-dwelling
coefficient of variation:

    median 0.147     p90 0.398     max 1.874

A household whose consumption swings year to year is a different customer from one whose does not —
that is bill-shock exposure, which use case 2.1 exists to remove. 35,582 dwellings carry all three
of gas level, electricity level and this volatility.

## Adding it collapses the curve

| N | 2-D (gas, elec) | 3-D (+ volatility) |
|---:|---:|---:|
| 25 | 30.2% | 6.1% |
| 50 | 75.5% | 13.1% |
| **100** | **99.2%** | **32.7%** |
| 150 | 100.0% | 56.5% |
| 200 | 100.0% | 74.1% |
| 250 | 100.0% | 87.7% |

**At N = 100 the sample goes from 99.2% covered to 32.7%.** At 250 it has still not reached 99%.

So the earlier N was not merely a lower bound with a bit of headroom — it was an artefact of
measuring the two dimensions that happened to be easiest to get. The corrected reading:
**N is above 250 on three dimensions, and the register names at least three more** (gradient, shape,
per-asset) that this source cannot measure. Every one of them can only push it higher.

## Why this is the same defect twice, one level up

The earlier document showed that rejecting on **input labels** covers 6.1% of the top-1% tail where
rejecting on **outputs** covers 85.4%, and called the label-based sample dangerous because it reads
92% while being blind to the tail.

This is that shape again with the labels removed: a sample rejecting on *outputs* is still blind, if
the outputs it uses are not the ones anything will be scored on. **"Reject on outputs" is not
sufficient — it has to be the outputs the use cases need**, which is precisely what the director's
ruling supplies and what a sample designed for "variation for its own sake" would miss.

## What this changes for the build

- N is **not settled** and must not be quoted as 100. It is reported per dimension set, with the
  set named, or it is meaningless.
- The similarity test's output vector is defined by the register, not by what the anchor source
  happens to carry. Where a dimension is unavailable it is a **stated gap in the coverage claim**,
  not an omission from it.
- Adding gradient, shape and per-asset is therefore not polish on the sample — it is what makes any
  N defensible at all.

## Limits

The 5% radius is unchanged and remains a Choice; a tighter one raises every number here. Volatility
is computed on **weather-corrected** gas, so it is variation the weather correction did not remove —
occupancy change, tariff change, behaviour — which is the right quantity for bill shock but is not
the weather gradient, and does not substitute for it.
