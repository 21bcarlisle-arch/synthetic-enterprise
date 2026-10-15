**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** what-a-house-does-to-its-energy -- `docs/market_research/when_an_electrically_heated_homes_water_heater_runs.md` §1 E2/E6, §6

# The world's storage heater is a direct-acting heater and charges nothing off-peak (2026-10-15)

**Owner:** the delivery seat (world fidelity, W2). Found by the worker on lane-0 draw
`when-an-electrically-heated-homes-water-heater-runs-is-not-established`.

## The defect

`simulation/fabric_physics.py` gives `HeatingSystem.ELECTRIC_STORAGE` the same control as a
direct-acting heater: `ON_OFF_DEADBAND`, modulation floor 1.00, fuel 1:1 in the period the room
calls for heat. `simulation/premise_trace.py::_dhw_fuel_kwh` does the same for its hot water. So a
storage home's meter carries both its space heat and its water heat in the day, at the moments of
demand.

## The evidence that it is wrong

SAP 10.2 Table 12a puts "other storage heaters" at a **0.00** high-rate fraction on a 7-hour tariff;
Table 13 puts a dual-immersion off-peak cylinder at 0.01–0.27 high-rate. Element Energy for BEIS
(2019/021) plans storage heaters at 90/10 and an E7 cylinder at 80/20 off-peak/on-peak, and its
Nottingham CHA trial measured 53–66% of the whole meter off-peak. Full read and GAPs in the
knowledge page.

## Why it matters

Every storage home's half-hourly shape is wrong in its largest stream; the LCL overnight-dominant
cluster (3.3% of homes, 51% of energy 00:00–06:00) cannot be reproduced; the P0033 texture reversal
is measured on a home whose heat lands in the wrong half of the day; and any two-register bill the
company forms for these homes reads a day/night split the real record would not show.

## What done looks like

One mechanism, "a storage home charges off-peak", applied to space heat (charge sized to the next
day's demand, placed in the off-peak window, Table 12a fraction at the high rate) and to hot water
(Table 13 split; electric-shower share carried as a GAP with a range), measured one stream at a
time. It redraws the demand world, so the value-arms re-take is part of the cost. Handed on as a
seat continuation.
