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

## Done (2026-11-11, delivery seat)

*Acted on the signed text in d828276d6. The later unsigned edit (bb69c250d) only corrected the lane header,
and the body is byte-identical.*

1. **Definitions.** Landed in 91a611f13 as §1a of `docs/market_research/household_carbon_and_the_measures_that_save_it.md`.
   Today it is *corrected beside the claim*: "every GB generator" was wrong. NESO's mix leaves out embedded thermal.
2. **Ember check.** This is §1b of the same page, with the basis of each source tabled before any
   differencing. Ember is CC-BY-4.0. Its UK figure is lifecycle CO2e, gross, generation-only, with
   Northern Ireland in, and upscaled to capture captive and small thermal. Rebased to our basis, it agrees
   within a few percent in 2016–18 and runs 13–25% above ours in 2024–25. The leading cause is about
   43 TWh a year of embedded and captive thermal generation that NESO's mix does not count. The GB/NI split
   is a GAP. The "few percent above" fill bias traces to the import term, and the fill fills 0 half hours
   today. **The world series is unchanged.** The what-and-why went to the director first, as asked:
   `docs/staging/SEAT_FINDING_THE_NATIONAL_CARBON_FIGURE_DOES_NOT_COUNT_EMBEDDED_THERMAL_2026-11-11.md`, and
   `for_the_director` row `the-customer-carbon-figure-co1-inherits-neso`.
   Pre-registered: `docs/staging/records/SEAT_PREREG_WHAT_EMBER_SAYS_ABOUT_OUR_GB_CARBON_HISTORY_2026-11-11.md`.
   P2 was refuted for 2023–25, and the miss is kept beside it.
3. **Imports: small, so stopped.** Tranberg et al. 2019, supplementary Table 4: hourly flow tracing moved GB
   +0.9% in 2017, from 346 produced to 349 consumed. That is an order below the embedded-thermal gap. It is
   recorded in §1a. Scarlat et al. was not read: the publisher returned 403.
4. **Reading log.** `docs/institutional/reading_log_against_the_gaps.md` G4 now has rows for Electricity Maps
   ("learn from the method; no data feed"), Ember and Tranberg. *Corrected beside the claim:* the marginal
   withdrawal is **verified** ("Our latest research on Marginal emission factors", 13 May 2024, updated 14 Jan
   2025). The steer had it right, and the seat's 91a611f13 note saying it was not found was wrong.

No fetched byte is a runtime input (W6). Ember's CSV was read once, outside the repository.
