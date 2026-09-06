**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_22_cold_spell_persistence_and_cross_cell_synchrony

**Knowledge:** none -- the weather-cells knowledge page is deliverable 1 of the weather ruling and is
not yet written. These are the persistence and synchrony rows it will publish; the declaration is
replaced when the page lands.

# Cold snaps arrive in blocks, and Britain has no second weather to diversify into

**Measured 2026-09-06**, delivery seat, `W1_22`. Reproduce with
`python3 tools/weather_cell_persistence.py --measure`. Source: HadUK-Grid daily `tas`, 1 km,
October–March 1991–2025 — 210 monthly files, 6,379 winter days, sampled at `W1_21`'s 89
representative cells carrying their clusters' full household mass.

`W1_21` answered how many cells resolve the **level** of household heat load. Level is what a tariff
is priced off. **This is what a hedge is priced off**, and none of it is visible in anything measured
so far: a 30-year normal is an average, and an average has no runs in it.

---

## What was measured, said before the answer

**A cold day is cell-relative** — at or below that cell's own 10th percentile of daily mean
temperature across the whole record. Not an absolute threshold. A household's fabric, boiler sizing
and habits are adapted to its own climate; 2 °C is an ordinary January day in the Cairngorms and a
crisis in Cornwall. A fixed threshold measures *where Britain is cold*, which is true and useless.

That Choice was priced rather than argued. Under a fixed 5 °C threshold the share of winter days
counted as cold runs from **10.9% to 53.7%** across the 89 cells — a 4.9× spread — and only **21.2%
of households live in the coldest quartile of cells.** A fixed threshold would concentrate the entire
measurement on a fifth of the book.

**A cold spell is a maximal run of consecutive cold days within one winter half-year.** The archive
holds October–March only, so 31 March and the following 1 October are adjacent rows and six months
apart; runs are not permitted to cross that seam, which would manufacture the longest spells out of
the joins.

## Persistence: half of all cold-day exposure arrives in blocks of five days or more

The null is the **same cold days permuted within the same cell and the same winter** — count held
exactly fixed, so the only thing that varies is whether they clump.

| | observed | if cold days fell independently |
|---|---:|---:|
| cold spells | 18,390 | 49,054 |
| mean spell length | **3.09 days** | 1.16 days |
| longest spell | **29 days** | 7 days |
| spells lasting ≥ 3 days | 40.5% | 2.1% (**19×**) |
| spells lasting ≥ 5 days | **19.4%** | 0.10% (**194×**) |
| spells lasting ≥ 7 days | 10.4% | 0.01% (**1,044×**) |
| spells lasting ≥ 14 days | 2.2% | 0% |
| **share of cold days inside spells of ≥ 5 days** | **51.3%** | **0.45%** |

The ruling's premise — *"a five-day cold snap costs more than the same degree-days spread thin"* —
is not a hypothesis about GB weather. It is the dominant case. **Over half of all cold-decile days
occur inside runs of at least five days**, against under half a percent if the same days fell
independently. A model that draws cold days independently would produce the right annual degree-day
total, the right number of cold days, and essentially none of the demand shocks.

## Synchrony: the cells do not diversify

Joint exceedance, not correlation — two cells correlating at 0.9 can still have independent cold
tails, and the tails are what cost money. **Lift** is P(both cells in their own coldest decile on the
same day) ÷ 0.01. 1.0 is independence; 10.0 is perfect lock.

| separation | pairs | mean lift |
|---|---:|---:|
| under 100 km | 551 | 8.67 |
| 100–250 km | 1,449 | 7.73 |
| 250–500 km | 1,604 | 6.69 |
| 500–1,200 km | 312 | **4.92** |

**Mean lift across all 3,916 pairs: 7.21. The least synchronised pair in Britain scores 2.81.**

There is no pair of GB locations whose cold tails are anything close to independent, and the decay
with distance is shallow: putting a thousand kilometres between two cells — the whole length of the
island — still leaves them five times more likely to be cold together than chance.

> **On 7 February 1991, 100% of the household book was in its own coldest decile on the same day.**
> On **605 of 6,379 winter days — one winter day in ten — more than half the book was.**

That is the answer to *"when Glasgow is cold, is London?"*. Yes. **Geographic spread across GB is
not a hedge.** A portfolio spread evenly over the 89 cells carries very nearly the same cold-snap
exposure as one concentrated in a single city, and any risk model that treats cells as partially
independent will understate the tail — in the flattering direction, which is the direction that gets
a supplier into trouble.

## What this changes

- **For `W1_21`'s cells.** They are the right resolution for *level*, and they buy almost nothing in
  *risk*. Both statements are needed; publishing the first alone would imply the second.
- **For hedging by physics (use case 3.1, stage 3).** The exposure is one national cold-snap factor
  with a modest regional overlay, not 89 partly-independent exposures. This produces the truth that
  will later be scored against; it does not build the hedge.
- **For the SIM's weather draw.** Independent daily draws per cell are refuted by both halves of
  this document — they would destroy the runs and the synchrony at once, and the resulting book
  would look correctly cold on average and never be stressed.
- **For the CLV crisis-year tail.** The reference case treats a crisis year as an extreme draw. This
  says the mechanism is a synchronous multi-day event, which is a different shape and a different
  frequency.

## Limits

- **89 cells, not 121,668.** The representative is the occupied cell nearest each cluster centre,
  carrying its cluster's whole household mass. Within-cluster synchrony is assumed perfect, which
  biases the reported lift **downwards** — the true book-level figure can only be higher.
- **The decile is a Choice.** A 5% or 1% tail would show more clustering still; nothing here
  establishes which threshold a hedge should be written against.
- **Temperature only.** Wind and sunshine have their own persistence, and the cold-and-still joint
  tail (`W1_COUPLED_WEATHER_CASCADE_DISCOVER`, +0.507 in time, 2.34× decile lift) sits on top of
  this. Not measured here.
- **No trend.** Thirty-five winters are pooled. Whether spells are getting shorter or less
  synchronous over the record is a question this data can answer and this measurement does not ask.
- **Demand is not measured.** Every figure here is about weather. What a five-day spell costs in
  kWh, and how the second day differs from the fifth, needs the demand model — `W1_18` and stage 2.
