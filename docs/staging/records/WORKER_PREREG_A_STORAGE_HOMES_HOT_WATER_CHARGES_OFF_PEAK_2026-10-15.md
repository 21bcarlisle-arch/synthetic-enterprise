**Severity:** ADVISORY · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Knowledge:** what-a-house-does-to-its-energy -- `docs/market_research/when_an_electrically_heated_homes_water_heater_runs.md` §1 E1, E2, E5, §2 G1, G4, G5

# Pre-registration: a storage home's hot water charges off-peak (stream 2 of 2)

**Claim:** `a-storage-homes-hot-water-charges-off-peak`
**Written before the build below was run.** Stream 1 (space heat) is
`WORKER_PREREG_A_STORAGE_HOMES_SPACE_HEAT_CHARGES_OFF_PEAK_2026-10-15.md`, landed in 025ca62ae.

## The one variable

Where an `ELECTRIC_STORAGE` home's hot-water ELECTRICITY lands in the day. The water drawn, its heat
and its gain to the room do not change. The day's `dhw_fuel_kwh` total does not change either. It is
split three ways:

- **Electric shower** (G1, GAP): a share `s` of the day's hot water stays at the draws. The range is
  0 to ~0.35, the all-household secondary figure. The build runs both ends as two arms and publishes
  no midpoint. `draw_dhw_events` does not label showers, so `s` is a fraction of the day's hot-water
  energy, not a count of shower events. The upper end is a share of HOUSEHOLDS read as a share of
  ENERGY. Shower energy is only part of a home's hot water, so as a population mean 0.35 overstates
  what stays at the draw. That makes it the conservative end for any off-peak claim.
- **Cylinder boost**: of the rest, SAP 10.2 Table 13's high-rate fraction stays at the draws. It is
  read with a dual immersion (G4: RdSAP 10 §11.7's dual-when-the-meter-is-dual convention, a belief)
  and a 110 L cylinder (G5: RdSAP's normal-cylinder default, a belief, and the highest-fraction
  size). At N occupants the dual 110 L figure is 0.105 for one person and 0.271 for five. Across 1–5
  people and 110–210 L the table spans 0.011–0.271.
- **Cylinder charge**: the remainder is charged evenly across 00:30–07:30 by
  `fabric_physics.storage_charge_kwh`, the stream-1 mechanism.

## Predictions (drawn 60, seed 17, C1, Jan–Apr 2022, both arms)

Rough sizes from stream 1: net of space, P0033's mean is 0.550 kWh/period, and net of both it is
0.437. So hot water is about 5.4 kWh/day. Space heat is 63% of a meter of about 71 kWh/day. At N=5
the boost is 0.271. So at the draw: s=0 keeps 0.271 of the hot water there, and s=0.35 keeps
0.35 + 0.65×0.271 = 0.526.

1. **Conservation.** Every home's daily total is unchanged to 1e-9. 59 of 60 homes are bit-for-bit
   unchanged in both arms. P0033 is the drawn 60's only storage home.
2. **Net-of-both texture does not move** (0.0556, to 1e-12, both arms). The netting subtracts
   `dhw_fuel_kwh`, and that field moves together with the meter.
3. **The overnight share rises a little.** 11 of the window's 14 periods fall in 00:00–06:00.
   P0033's whole-meter share there goes 0.522 → **0.555–0.580 at s=0** and **0.540–0.565 at s=0.35**.
   Space heat dominates the meter, so water can add only a few points.
4. **The P0033 reversal SURVIVES in both arms.** I am predicting against the item's WHY here. The mean
   net of space is conserved, so net-of-space texture moves only through the median step. The finding
   showed that the median is a RANK effect: the water draws push it over a quiet/active cliff. A draw
   cut to 27% (or 53%) of its size is still a step far above the quiet side's p50 (≈0.024 kWh). The
   charge block also adds two edge steps of ≈0.2–0.3 kWh in quiet hours. So net-of-space texture
   stays in **[0.075, 0.095]** in both arms and stays above 0.0556. The three strict xfails on
   `_P0033_NETTING_REASON` stay XFAIL.

## What would refute it

- (4) is refuted if net-of-space falls below net-of-both in either arm. The xfails then XPASS and
  the reversal really was "hot water in the wrong half of the day".
- (2) is refuted if net-of-both moves. The netting then reads something other than the field.
- (3) is refuted if the overnight share moves more than 0.06. My 5.4 kWh/day size reading would
  then be wrong.

## Results

*(filled in below after the run; nothing above is edited)*

Run 2026-10-15 at origin 855e87e12. One process per arm, from the repo root. The probe was
`generate_premise_trace` over the drawn 60. "Before" was run on the unmodified tree before the build.

| P0033 | before | s = 0 | s = 0.35 (shipped) |
|---|---|---|---|
| hot water kept at the draw | 1.000 | 0.271 | 0.526 |
| net of space | 0.0869 | **0.1096** | **0.1228** |
| net of both | 0.0556 | 0.0556 | 0.0556 |
| whole meter | 0.0488 | 0.0424 | 0.0467 |
| share 00:00–06:00 | 0.522 | **0.566** | **0.551** |
| largest half-hour, kWh | 8.78 | 7.96 | 7.99 |

1. **Holds.** P0033 is the only home that changed in either arm. The largest daily difference
   anywhere is 1.4e-14.
2. **Holds**, bitwise this time: net-of-both moved by 0.0.
3. **Holds.** 0.566 at s=0 and 0.551 at s=0.35, inside both bands. The 5.40 kWh/day size reading
   was right.
4. **Direction holds, number REFUTED, and the mechanism ran the other way.** The reversal survives in
   both arms, as predicted, so the three strict xfails stay XFAIL. But net-of-space ROSE, to 0.1096
   and 0.1228, outside my [0.075, 0.095]. So the reversal WIDENED. Net of space, the mean is
   conserved. The median's rank goes UP: P0033's step distribution has a cliff (p30 0.017, p70
   0.25–0.31). The charge block's two edge steps a day (0.18–0.28 kWh) land on the active side of it.
   The draws, shrunk to 27% or 53%, stay there too. So the median moves 0.0478 → 0.0602 / 0.0675.
   Night steps are unchanged (median 0.015 → 0.016). The day median falls a little (0.134 →
   0.123 / 0.130). I named the edge steps and assumed they would not count. They do.
   s=0.35 reads higher than s=0 because more of the draws stay large.

**What this says about the item's WHY.** The WHY said the P0033 reversal is "hot water in the wrong
half of the day". That is refuted: moving the hot water to the night widens it. By construction,
net-of-both cannot see where hot water lands, because it subtracts the field. Net-of-space can, and
the rank effect at the cliff is what moves it. So the reversal is a property of a median read at a
cliff (the 2026-10-15 finding's own first branch), not of water timing. No re-draw of β is indicated
by this run.

**Downstream.** P0033's meter changed, so the world demand digest moves. The blind-arms re-take
(`retake-the-blind-arms-after-the-storage-streams-land`) is now unblocked: both storage streams are
built.
