**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`
· **Class:** measurements_that_mirror

**Knowledge:** none — this is a machine finding about two of our own implementations. The
domain understanding behind it is already published in `tools/hot_water_base.py`'s sourced
constants; what is new here is that a second, unsourced copy is the one in production.

# The settlement path's hot water is half again the measured value, and I built the second copy

**Found 2026-09-08 at `b1145fe4a`**, by looking for `simulate_premise`'s callers and finding it has
none — then finding what runs instead.

---

## Two implementations of one quantity, and the wrong one is live

| | per person | fixed | ΔT | source stated |
|---|---:|---:|---:|---|
| `simulation/premise_trace.py` (**production**) | 40 L | **0 L** | 45 K | ``domain-knowledge`` — "BS EN 12831 / SAP", no document, no table |
| `tools/hot_water_base.py` (instrument only) | 25 L | 36 L | 37.6 K implied | SAP 2012/BREDEM, corroborated against 45,000 metered homes |

**They agree exactly on volume at the average occupancy and nowhere else.** 40 × 2.4 = 96 L/day;
36 + 25 × 2.4 = 96 L/day. That agreement is why this survived: any check at the mean would pass.

## What production actually emits, against the measured record

`draw_dhw_events` → `premise_trace` → `fabric_shape_fn` → `run_phase2b`. This is the path the
company settles, bills and hedges on, not a side panel.

| occupants | production, metered gas | DESNZ measured (45,000 homes, combi) |
|---:|---:|---|
| 1 | 2.61 kWh/day | — |
| 2 | 5.22 | — |
| **2.4 (average)** | **6.27** | **median 3.9 (Sep) – 4.5 (May)** |
| 4 | 10.45 | IQR upper bound 6.6 – 8.0 |
| 5 | 13.06 | — |

**Production is 1.39× to 1.61× the measured median at the average occupancy**, and a four-person
household is put above the measured *seventy-fifth percentile* of the whole population. Roughly
**+2 kWh/day, or ~730 kWh/year, on every fabric-eligible customer's gas.**

**And it over-disperses across household size.** Being strictly proportional, its four-versus-two
ratio is **2.00**. SAP's own structure — which the comment cites — gives **1.58**, because some
draw-off happens whatever the headcount. The module quotes the standard and implements a
relationship the standard does not contain.

Two errors compound: the volume shape, and a 45 K rise where matching the DESNZ median energy to
the same volume implies 37.6 K (a 10 °C cold main to a 47.6 °C tap). Neither is absurd alone; the
product is half again too much.

## This is my defect too, and that half is worse

`tools/hot_water_base.py` carries a REUSE block I wrote which says:

> *"`simulation/premise_trace.py` … Nothing models the gas base."*

**That is false, and it was false when I wrote it.** `premise_trace` has modelled domestic hot water
since long before, at line 907, under a heading that says so. I searched for "hot water", "base
load", "cooking", "gas base" and "standing loss" and did not search the module I was naming. The
write-time gate asks what the index returned and why new code was written anyway; I answered it with
a claim I had not checked.

So the state I have created is exactly the shape the director named as this project's most expensive
— *"one legal requirement, five implementations, a defect fixed in one of them in July and still
live in another in August, and nothing anywhere able to notice."* There are now two hot-water models
that disagree about the shape of the occupancy relationship, and the sourced one is the one that
does not run.

**The finding is only visible because the duplicate exists.** That is not a defence of the
duplicate: it means the comparison was never made, and building a second copy is a very expensive
way to make it.

## Recommendation

**One implementation, and it should be `premise_trace`'s — corrected, not replaced.** Production
is the right home; the instrument should import it rather than carry its own constants.

1. Move the anchored constants into `premise_trace`: the fixed-plus-per-person volume, and a ΔT
   consistent with the measured energy rather than a nominal 45 K.
2. Have `tools/hot_water_base.py` import them, keeping only what is genuinely its own — the
   DESNZ distribution, the grading, and the sweep. Its REUSE block is corrected as part of this.
3. A control that the two agree, so the next divergence reds rather than waiting to be noticed.

**What I am NOT doing without a decision: changing the production number.** Correcting this moves
every fabric-eligible customer's gas by about 730 kWh a year, which moves consumption, revenue,
margin and every hedging figure derived from them. That is a change to what the world does, and the
baseline/curriculum split makes the world the director's. **It is a fidelity correction — the
model currently disagrees with a 45,000-home measurement — so my recommendation is to make it, and
to re-baseline rather than carry the old number for continuity.** But the re-baseline is his call
and it is filed here rather than made.

## What this does NOT touch

The DESNZ study is **combi-only**, and `_DHW_COMBI_EFFICIENCY` is the combi path, so the comparison
above is like-for-like. Cylinder standing loss remains unmodelled in both implementations and is
still a named gap, not a discrepancy.
