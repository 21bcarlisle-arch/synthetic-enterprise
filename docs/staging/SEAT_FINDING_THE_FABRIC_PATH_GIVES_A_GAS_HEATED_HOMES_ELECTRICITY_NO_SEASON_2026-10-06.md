**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `d48-slice-4-retire-the-worlds-estimator-and-attribute-the-electricity-residual`

# The fabric path gives a gas-heated home's electricity no season

## What was measured

On the slice 3 decade capture (`/tmp/d48s3/world.pkl`), each electricity household's
winter/summer ratio was computed: Dec–Feb kWh per day over Jun–Aug kWh per day, from its own
actual-read bills of 28 days or more.

| Ratio | Households | Of which gas-heated fabric | Share of billed kWh |
|---|---|---|---|
| < 1.15 | 57 | **56** | 45% |
| 1.15–1.6 | 17 | 1 (15 on the legacy PC1 path) | 14% |
| ≥ 1.6 | 11 | 0 (5 electrically heated fabric) | 31% |
| not established | 20 | 12 | 10% |

The legacy path settles on Elexon's PC1 Group Average Demand (`sim/profile_class_1.load_pc1_shape`).
Its own base shape is 12.49 kWh/day in winter and 8.99 in summer, a ratio of **1.39**. The legacy
households sit there (1.38–1.40). The gas-heated fabric homes sit at **0.93–1.09**.

## Why this is a fidelity question and not a company one

PC1 is the domestic unrestricted class, most of whose homes do not heat with electricity, and
its published profile carries a winter/summer swing of about 1.4. The swing comes from lighting,
occupancy and appliance use, not space heating. A gas-heated home in this world shows none of
it. So the evidence is the published profile against the world's own trace. It is independent
of anything the company does. It surfaced through the D48 grade (slice 4,
`SEAT_FINDING_D48_SLICE_4_…`), and nothing about that grade should decide the remedy.

## What is not established

- Which component of `simulation/premise_trace` / `fabric_demand_path` is missing the swing
  (lighting against daylight, occupancy time indoors, or appliance use). Not opened here.
- The published household-level distribution of the ratio for gas-heated homes, as opposed to
  the class average. PC1 is an average, and some real homes are flat. A remedy needs a source
  for the distribution, not only the mean (the knowledge-first rule).

## What it costs today

Any company estimate shaped by an industry profile mis-bills these homes seasonally. Slice 4
measured that as most of the electricity June gross true-up. The same flatness reaches anything
else that reads a fabric home's seasonal electricity: hedge volume shape and the winter peak of
the book.

## Recommendation

A world-lane DISCOVER pass: find the published seasonal swing of non-electrically-heated
domestic electricity (the PC1 coefficients as an average, and any metered-panel distribution,
for example SERL), then locate the component of the premise trace that should carry it. Decide
blind to D48.

## Discovered (2026-10-06, worker, draw `fabric-electricity-season-discover`)

`docs/market_research/the_seasonal_swing_of_a_gas_heated_homes_electricity.md`. SERL Stats Report
Vol 2 puts the gas-heated, no-PV monthly median at max/min **1.36–1.47** (2021–23). The world's only
seasonal term is lighting (ratio 2.54, about +0.5 kWh/day in winter), and the cold appliances cancel
most of it (0.77). Appliance events and occupancy have no season, and the trace carries no boiler
pump or fan electricity and no supplementary electric heating. Next is a BUILD, sourced term by
term. Boiler auxiliary electricity is the only candidate with a published allowance (SAP Table 4f),
and it must be read at source first.
