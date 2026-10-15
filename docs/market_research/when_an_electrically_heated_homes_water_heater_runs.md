**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

**Knowledge:** what-a-house-does-to-its-energy

# When an electrically heated home's water heater runs

**Written 2026-10-15** on the delivery seat's lane-0 draw
`when-an-electrically-heated-homes-water-heater-runs-is-not-established` (K8, knowledge before
build). Asked by `docs/staging/SEAT_FINDING_AN_ELECTRIC_HOMES_WATER_HEATER_ADDS_TEXTURE_UNDER_THE_ACTIVE_USE_COUPLING_2026-10-15.md`:
the P0033 texture reversal is seven daily hot-water draws landing on the meter in the day. If a
real storage-heated home heats its water off-peak, the meter carries a night block instead. Nothing
is built here; §5 is the decision, §6 the second defect this read turned up.

## 1. What the published record establishes

**E1. A storage-heated home needs an off-peak (two-rate) meter, and its cylinder runs on it.**
RdSAP 10 (BRE, 13-02-2024) §11 lists what an off-peak tariff "is needed for the intended operation
of": electric storage heaters (SAP codes 401–409), electric dry-core/water-storage boilers, electric
CPSU, and "dual electric immersion". Where water heating is unknown, "if the electric meter is dual
the immersion heater is also dual, but is a single immersion otherwise" (§11.7), and an immersion
behind an inaccessible cylinder on a dual tariff is assumed dual, at 210 litres (Table 28).

**E2. How much of an off-peak cylinder's electricity falls in the day is published, by cylinder
size, occupancy and immersion type.** SAP 10.2 (17-12-2021) Table 13, "High-rate fraction for
electric DHW heating"; 7-hour tariff formulae (note 2), evaluated at real inputs (N = occupants):

| Cylinder | N=1 | N=2 | N=3 | N=4 | N=5 |
|---|---|---|---|---|---|
| 110 L dual | 0.105 | 0.146 | 0.188 | 0.229 | 0.271 |
| 110 L single | 0.552 | 0.582 | 0.613 | 0.644 | 0.675 |
| 160 L dual | 0.058 | 0.087 | 0.117 | 0.146 | 0.176 |
| 210 L dual | 0.011 | 0.028 | 0.046 | 0.063 | 0.081 |

Dual: `[(6.8 − 0.024V)N + 14 − 0.07V]/100`; single: `[(14530 − 762N)/V − 80 + 10N]/100`, clipped to
[0, 1]. On a 10-hour tariff the fractions are lower again (dual 160 L and 210 L read 0). So a
dual-immersion cylinder in a storage home draws roughly **73–99% of its water-heating electricity in
the night window**; the remainder is the day element topping up after heavy use, which is why it
rises with N. A single off-peak immersion on a small cylinder runs out and is boosted at the high
rate more than half the time.

**E3. An independent planning convention agrees.** Element Energy for BEIS, *Evidence gathering for
electric heating options in off gas grid homes* (Research Paper 2019/021), Table 6-14: hot-water
cylinder on Economy 7, **80% off-peak / 20% on-peak**; storage heaters 90/10. The same report:
"Electric cylinders typically contain two immersion elements: one each for off- and on-peak use."

**E4. Most electrically heated homes have a cylinder.** Same report, Table 5-8 (off-gas dwellings,
England and Wales): electric-heated terraces 83%, semis 86%, detached 94% have a hot-water cylinder.
"Electric dwellings without hot water cylinders are likely to be fitted with instantaneous electric
hot water heaters." (Off-gas stock only; flats are not in that table — see G2.)

**E5. An instantaneous electric shower runs at the draw, at high power, whatever heats the
cylinder.** SAP 10.2 Appendix J step 8: each electric shower present is costed separately on
worksheet (64a) at its rated power (Table J4 default 9.3 kW, floor 9 kW) for 6 minutes per use, and
is NOT part of the cylinder's off-peak load. A storage home with an electric shower therefore has
two water-heating streams: a night block for the cylinder (baths, basins, sinks) and short day spikes
for showers.

**E6. Space heat in a storage home is also night-charged.** SAP 10.2 Table 12a: "Other storage
heaters, 7-hour or 24-hour: space-heating high-rate fraction **0.00**"; integrated storage+direct
0.20; direct-acting electric on a 7-hour tariff 1.00. Element Energy's 90/10 (E3) is the planning
equivalent, and its Nottingham CHA trial measured off-peak share of the whole meter at 53% (old
storage heaters) rising to 66% (new). Typical Economy 7 off-peak hours: "from 12:30 or 1:00 am to
7:30 or 8:00 am" (Element Energy §6).

## 2. What is not established — GAPs

- **G1. Electric-shower share in electrically heated homes.** No primary source read here gives it.
  A secondary figure (Statista, 2010–12, ~35% of UK households' main shower is electric; EFUS 2011
  fuel-poverty reporting 47% vs 35%) is all-tenure and all-heating, and not read at source. The
  share among storage-heated homes is GAP. It decides how much of a storage home's hot water stays
  on the day meter.
- **G2. Cylinder vs point-of-use in electrically heated FLATS.** E4 covers off-gas houses; flats,
  where most direct-electric heating sits, are absent. GAP.
- **G3. Whether a direct-electric home on a single-rate meter runs its immersion on a timer or on the
  thermostat.** If thermostat-only, reheat follows the draw by minutes to an hour and "at the draw"
  is a fair approximation; if timed, it is not. No published share read. GAP.
- **G4. Dual vs single immersion share in storage homes.** RdSAP's assumption (dual when the meter is
  dual) is a rating convention, not a survey count. GAP; E2 bounds the consequence (0.03–0.27 dual vs
  0.55–0.68 single at 110 L).
- **G5. Cylinder size distribution in storage homes.** RdSAP defaults (110 L normal; 210 L for an
  inaccessible off-peak dual) are conventions. GAP.

## 3. What the world does today (origin/main, read 2026-10-15)

- `simulation/premise_trace.py::_dhw_fuel_kwh` returns `heat_kwh` 1:1 for every non-gas, non-heat-pump
  home, placed in the period of each draw from `draw_dhw_events` (wake cluster, evening cluster,
  scatter). Storage and direct electric homes are treated alike.
- `simulation/fabric_physics.py`: `ELECTRIC_STORAGE` is controlled `ON_OFF_DEADBAND` with
  modulation floor 1.00 and fuel 1:1 — i.e. **a direct-acting heater**. Its space heat lands when the
  room calls for it, not in the night window. (§6.) **Built 2026-10-15:** the room still calls for
  heat in the day, but the meter now carries the day's space-heat electricity as an even charge
  across 00:30–07:30 at Table 12a's 0.00 high-rate fraction (`fabric_physics.storage_charge_kwh`;
  its simplifications are named beside it). **Built 2026-10-15 (stream 2):** a storage home's hot
  water is split by `premise_trace.storage_dhw_meter_kwh`. An electric-shower share stays at the draws
  (G1, the range 0–0.35, the trace runs the upper end, no midpoint). Of the cylinder's share, Table 13's
  dual 110 L high-rate fraction stays at the draws (G4/G5 as RdSAP beliefs; the table's span,
  0.011–0.271, is printed beside it). The rest is charged across 00:30–07:30. `ELECTRIC_DIRECT` hot water
  stays at the draw (G3).
- `simulation/household.py::HeatingSystem` already separates `ELECTRIC_STORAGE` from
  `ELECTRIC_DIRECT`, so the evidence above maps onto the world's own types without a new axis.

## 4. The design choice this evidence supports

For an `ELECTRIC_STORAGE` home, hot-water electricity should be **the day's DHW energy split: a
high-rate fraction from SAP Table 13 placed at the draws (the boost), the rest placed as a block in
the off-peak window**. The electric-shower fraction (G1) belongs on the draw side and is GAP, so the
build must carry it as a named unknown with a range — 0 to the all-household secondary figure —
never a picked number. For `ELECTRIC_DIRECT` homes "at the draw" stays the stated belief until G3 is
read, recorded as such beside `_dhw_fuel_kwh`.

## 5. Decision on `_dhw_fuel_kwh`

**It should change for storage homes, and not on its own.** Moving the water heater to the night
window while the same home's storage heaters stay direct-acting (§6) would make one stream right and
leave the larger, same-cause stream wrong — and the P0033 measurement would then be attributing a
texture change to one of two moved variables. The build is one mechanism ("a storage home charges
off-peak") applied to both streams, measured one stream at a time, with the value-arms re-take
budgeted because it redraws the demand world. Handed on as a continuation; not built in this turn.

## 6. Second defect turned up by this read

The world's storage heater is a direct-acting heater. Table 12a's 0.00 high-rate fraction and the
Nottingham trial's 53–66% off-peak meter share say a real storage home's meter is dominated by a
night block; the world's carries the space-heat load in the day, at the moments of demand. This
bears on every storage home's half-hourly shape, on any two-register (E7) bill the company builds,
and on the LCL "Overnight-dominant" cluster (`hh_load_shape_clustering_2026.md`, 3.3% of homes,
51% of energy 00:00–06:00) that the world cannot currently reproduce. Filed as
`docs/staging/WORKER_FINDING_THE_WORLDS_STORAGE_HEATER_IS_A_DIRECT_ACTING_HEATER_AND_CHARGES_NOTHING_OFF_PEAK_2026-10-15.md`.

## Sources

- BRE, *SAP 10.2 — The Government's Standard Assessment Procedure for Energy Rating of Dwellings*,
  17-12-2021, Tables 12a and 13, Appendix J step 8, §"Water heating fuel types":
  https://files.bregroup.com/SAP/SAP%2010.2%20-%2017-12-2021.pdf
- BRE, *RdSAP 10 Specification*, 13-02-2024, §11 (Table 28, §11.7, meter rules):
  https://files.bregroup.com/SAP/RdSAP10-dt13.02.2024.pdf
- Element Energy for BEIS, *Evidence gathering for electric heating options in off gas grid homes*,
  Research Paper 2019/021, April 2019, Tables 5-8 and 6-14, §2 and §3:
  https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/831079/Electric_heating_options_in_off-gas_grid_homes.pdf
