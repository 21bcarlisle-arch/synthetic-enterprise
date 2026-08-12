# WORKER FINDING — the model's `electric_storage` home has no storage heater in it

**Severity:** LATENT · **Lane:** W2_customer_generator

**Found:** 2026-08-09, while decomposing the L1.2 day-to-day shape correlation for W1_12.
**Class:** fidelity gap in the world layer (an appliance the register names and the physics does not model).
**Disposition:** QUEUED as a simplification and a finding. NOT fixed on sight — it is not blocking,
and the supply of these is infinite (SELF_INTERRUPT_DISCIPLINE).
**Owner atom:** `W1_12_premise_trace_generator`.

## Observed, with evidence

`observed-with-evidence`.

- `simulation/fabric_physics.py::_CONTROL_MODE` maps `HeatingSystem.ELECTRIC_STORAGE` to
  `ControlMode.ON_OFF_DEADBAND` — the same control mode as a gas combi and as
  `ELECTRIC_DIRECT`, i.e. a room thermostat with hysteresis following the occupancy
  setpoint schedule.
- `simulation/premise_trace.py` contains no occurrence of the string `storage`
  (grep, this HEAD). There is no charge window, no thermal store, no Economy-7 calendar
  and no charge controller anywhere in the generator.
- `_fuel_for` treats `ELECTRIC_STORAGE` and `ELECTRIC_DIRECT` identically (resistive, 1:1).

So a premise the register calls `electric_storage` is simulated as a panel heater that
runs when the household wants heat.

## Why that is wrong, against a real source already in this repo

`docs/market_research/hh_load_shape_clustering_2026.md`, clustering 304 real households
from the Low Carbon London trial (UK Power Networks, London Datastore, CC-BY), finds a
distinct archetype B — **51.0% of daily energy consumed between 00:00 and 06:00, evening
(17:00-21:00) only 10.4%, peak at 23:30**, mean 18.62 kWh/day — and identifies it as the
storage-heating / off-peak signature, the household-level analogue of Elexon Profile
Class 2 (domestic Economy 7).

The model's storage home puts its heat in the morning and evening occupancy blocks. It is
not that archetype; it is archetype A with a bigger heater.

## What this does and does not affect

It does NOT undermine the 2026-08-09 L1.2 closure, and the direction matters. That work
netted the space-heating machine out of a band written about households, on the measured
grounds that the heating stream repeats day to day at 0.91-0.96 in **every** regime. A
real storage heater charges on a fixed clock, so modelling it properly would make the
heating stream MORE repeatable, not less — the netting would be more necessary, not less.

It DOES affect: any tariff work that turns on Economy 7 / off-peak split (a storage home
is the canonical restricted-meter customer), the shape of this population's contribution
to system peak, and the credibility of `electric_storage` as a register value anywhere
downstream.

## The work, when it is drawn

1. A charge window (published: the Economy 7 off-peak period is a real, dated licence
   artefact) and a thermal store with a discharge characteristic, rather than a deadband
   thermostat.
2. Automatic charge control off the previous day's / forecast ambient — the mechanism by
   which a real storage home's overnight block varies in size while staying in place.
3. The exit test is already sitting in the repo: the LCL archetype-B centroid
   (`data/lake/lcl_household_load_shapes_2013/cluster_centroids_k2_weekday.csv`) is a real
   48-vector to score a modelled storage home's mean weekday shape against. That is an
   anchored test, not a domain-knowledge one.

## What must NOT be done

Adding an overnight block tuned until the modelled shape matches the centroid. The
centroid is the TEST; the charge window and the store are the mechanism. R12 applies with
its usual force — and note that L1.2's band must not be revisited when this lands, since
the netting already means a clock-led heating stream cannot fail a household band.
