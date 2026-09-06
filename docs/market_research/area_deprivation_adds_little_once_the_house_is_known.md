**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_19_who_lives_where_money_and_composition

**Knowledge:** none -- the people knowledge page is deliverable 5 of the people ruling and is not
yet written. This is the row that shapes its central claim; the declaration is replaced when the
page lands.

# Area deprivation looks like a strong driver of consumption, and most of it is the house

**Measured 2026-09-06**, delivery seat, `W2_19`. Source: DESNZ NEED `anon2026_50k.csv`, the 37,606
dwellings carrying both metered 2024 gas and an England IMD quintile.

---

## What the people ruling claims

> *"Geography carries socio-demographics and asset potential together (rural = detached, drive,
> roof, off-gas, older, owner, higher income), so the people joint keyed on small-area geography is
> also how EV and battery potential gets its people-side correlation."*

Small-area geography is made the **coherence key** across all three axes. This tests it on the one
output NEED can measure: metered gas.

## Raw, it looks decisive

Median metered gas by Index of Multiple Deprivation quintile (1 = most deprived):

| IMD | n | median gas |
|---|---:|---:|
| 1 | 7,842 | 8,800 |
| 2 | 7,274 | 9,200 |
| 3 | 6,950 | 9,700 |
| 4 | 7,520 | 10,500 |
| 5 | 8,020 | 12,100 |

Monotonic across all five quintiles, **1.38× from most to least deprived**. On this alone the
ruling's framing looks strongly supported.

## Controlling for the house, most of it disappears

The same comparison **within a single floor-area band**:

| band | n | IMD 1 | IMD 2 | IMD 3 | IMD 4 | IMD 5 | spread |
|---|---:|---:|---:|---:|---:|---:|---:|
| 51–100 m² | 19,989 | 8,900 | 8,900 | 8,900 | 9,200 | 9,700 | **1.09×** |
| 101–150 m² | 10,989 | 11,000 | 11,600 | 11,900 | 12,050 | 13,200 | **1.20×** |

**1.38× becomes 1.09× and 1.20×.** Most of what looks like an area effect is compositional: less
deprived areas hold bigger houses, and floor area is what drives gas. This is the same shape the
project has paid for before — two correct figures whose ratio is not the quantity anybody wanted.

## What this changes, and what it does not

**It supports the housing ruling's H2** ("consumption dominates the upside, and it is house
physics") on the strongest available evidence: house first, area second.

**It does not refute the people ruling.** Geography stays the right coherence key for *which stock
and which households are where* — the compositional effect is real and large, and it is exactly how
the draw should place a big detached house in a less deprived area rather than uniformly. What it
refutes is a stronger claim nobody has yet made but which the raw table invites: that area is an
independent driver of *consumption given the house*. Conditional on floor area it is worth 9–20%,
which is a real term and a small one.

**So the layer-one joint should key geography to the HOUSE**, and carry a modest conditional people
term on top — rather than treating area as a peer driver of usage.

## Limits, and one that runs against the conclusion

- **IMD is the deprivation of the AREA, not the income of the HOUSEHOLD.** An affluent household in
  a deprived LSOA is counted as deprived. That attenuation means the true household-income effect
  conditional on the house is **larger than 9–20%** — the direction runs against the conclusion
  above, and is stated for that reason. What this measurement rules out is area-as-proxy carrying
  it, not the household term existing.
- England only; `IMD_BAND_WALES` is a separate scale and is not pooled here.
- Gas only. Electricity and shape are untested, and the people ruling's phase-2 items (presence,
  working patterns) plausibly land on shape rather than level.
- The censoring at both tails applies as before, so the extremes of each quintile are understated.
