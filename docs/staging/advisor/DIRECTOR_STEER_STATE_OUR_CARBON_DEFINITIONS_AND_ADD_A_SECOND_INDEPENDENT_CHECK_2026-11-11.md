**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

*Header corrected 11 Nov by the worker tick: the lane read `W`, which is no known lane, so the advisor channel refused the file and nothing drew it. It now reads `W1_market_weather`, because the grid-carbon history lives in `sim/`. The body is unchanged.*

# [DIRECTOR-STEER] State our carbon definitions, and add a second independent check (2026-11-11)

**Type:** STEER, through the advisor channel. The director's words, from chat on Wed 11 Nov:

- 07:18 GMT, sharing Electricity Maps: "Is any of this data free? What can we learn from it and the apis?"
- 07:20 GMT: "Can we not also learn from how they model and forecast? What works better or worse than how we do it?"
- 07:22 GMT, on the advisor's recommendation below: "Stage it."

**When:** knowledge work. Rank it yourself. It serves CO1, the one carbon figure the mission promises customers.

## What the advisor found (check it)

- **Electricity Maps** has a free tier "for applications outside of their commercial workplace", paid commercial use, and an open-source collector repository (`electricitymaps-contrib`) with sourced per-fuel emission factors for 200+ zones. Its method: operator data collectors, estimation for missing data, flow tracing across interconnectors (consumption-based), IPCC lifecycle factors by default, and validation against Ember, the IEA and Eurostat. Its forecast method and accuracy were not found published.
- **They built a machine-learned marginal carbon signal** (1,000+ variables, flow-traced) and then withdrew it: "we no longer offer marginal signals", citing "major limitations", including "the incompatibility with regulation".
- **Ours, per `sim/grid_carbon_history.py`:**
  - NESO's published series, aligned to settlement and read as "outturn with hindsight";
  - gaps filled with NESO's own arithmetic, where imports are counted at `import_factor` (one factor, not flow-traced) and ElecLink and Viking are left out because NESO's mix leaves them out;
  - the fill reads "a few percent ABOVE the historic mix", and "which term carries the difference is not established";
  - futures come from `sim/grid_carbon_future.py`, a model fitted on history and driven by the replayed weather year;
  - the plant-by-plant reconstruction (`sim/grid_carbon_intensity.py`) is parked.

## Wanted

1. **State the definitions on the carbon knowledge page,** in plain words, for the figure customers see: average, not marginal; direct, not lifecycle; and how imports are counted, including the two interconnectors left out. Record why marginal is not used, citing Electricity Maps' own withdrawal and the reporting rules (location-based scope 2 uses average). Record that "carbon saved by shifting" measured on average intensity is a stated choice, with the published debate summarised, not hidden.
2. **Add Ember as a second independent check** on the 2016–2025 history. Its GB data is free and openly licensed. The license is to be checked. Report agreement by year, and where they part. Ember should help explain the open "few percent above" bias. This is the "good views" principle from the JEPA reading-log entry: two independent observations of the same thing.
3. **Imports:** say whether one import factor is good enough for GB, given the large share of French nuclear and Norwegian hydro. Say what flow tracing would change, using published estimates rather than building it. If the answer is "small", say so and stop.
4. **Reading log:** add Electricity Maps, with the verdict "learn from the method; no data feed", and the marginal-withdrawal finding.

## Not wanted

- No new paid data. No live API feed. W6 applies: fetched bytes become knowledge and checks, never a runtime input the company reads.
- No change to the series the world uses unless the Ember check finds a real error. If it does, say what and why first.

## Risk

Touches: the carbon knowledge page, a history check, and the reading log.
Blast radius: none to runs unless a correction is found.
Probable failure mode: comparing Ember's annual or monthly figures with our half-hourly series as if they counted the same thing. Say what each counts, including lifecycle or direct and imports in or out, before differencing.
Proportionality: reversible and narrow — just do it.

— Director steer, 11 Nov 2026, his words above; the reading and drafting are the advisor's.
