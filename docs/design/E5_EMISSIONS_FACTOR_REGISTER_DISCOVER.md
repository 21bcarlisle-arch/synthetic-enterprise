# E5 emissions-factor register — DISCOVER (doc-only) — 2026-07-20

**Status:** DISCOVER, doc-only. The `CARBON_THREE_LEDGER_DISCOVER.md` named "the emissions-factor
register (anchored to a real published source, R10)" as DISCOVER-workable now — this is it. It
REGISTERS the candidate factors the SPENT ledger needs and FRAMES the director's values-call; it
decides none of them (the emissions-factor SET is director-reserved per `CARBON_NOT_A_TARGET_
CONSTRAINT.md` + the DISCOVER doc — it defines the mission metric). No code. R9: every figure is
labelled either a cited source or **[verify-at-BUILD]** (autonomous = no network to fetch the
current published value; the register names the SOURCE and the shape, not a fabricated number).

## Why this exists

E5 rung 1 (`company/carbon/carbon_ledger.py`) is factor-agnostic: it records `CarbonEvent`s with a
`tco2e` handed in. The **SPENT** side (operational carbon: compute, tokens, people) needs a factor
to convert observed activity → tCO2e. That factor set is the block on the SPENT emitter. This
register makes the choice a clean director pick rather than an agent assumption.

## The factors the SPENT ledger needs

| Activity (observable) | → tCO2e via | Candidate factor / source | Status |
|---|---|---|---|
| **Compute electricity** (kWh) | grid carbon intensity (gCO2e/kWh) | National Grid ESO / DESNZ published GB grid intensity; declining ~2016→2025 | **[verify-at-BUILD]** current value + the marginal-vs-average choice (below) |
| **Tokens / inference** | energy-per-token (kWh) × grid intensity | published ML-inference energy estimates (contested, wide range); the token/compute sensor (`RESOURCE_AWARE_SCHEDULING`, sensor available) gives the USAGE | **[verify-at-BUILD]** the energy-per-unit is the uncertain half; register a range + source, not a point |
| **People** (headcount) | per-FTE operational emissions (office, commute) | DESNZ/GHG-protocol conversion factors; for a ~1-human+AI company this is small vs compute | **[verify-at-BUILD]**; candidate: treat as a small named constant or scope-out with a stated boundary |
| **Cost-side £/tCO2e sanity anchor** | — | £273/tCO2e (2025, 2022 prices, ±50%, UK appraisal) — already cited in the constraint | cited; a **sanity band (R12), never a target** |

## The director values-calls this surfaces (not decided here)

1. **Grid marginal vs average intensity.** Average understates the carbon of *incremental* consumption;
   marginal is higher and time-varying. This choice affects BOTH the SPENT compute figure AND the
   SAVED counterfactual (avoided emissions). The `CARBON_THREE_LEDGER_DISCOVER.md` already flagged it.
2. **The accounting boundary (scope 1/2/3).** Compute electricity is scope 2; embodied hardware +
   upstream cloud is scope 3. Which scopes the ledger counts is a boundary decision that changes the
   headline. Recommend stating the boundary explicitly on every published figure (like the R14 clock).
3. **Time-of-use resolution.** A flat annual grid intensity vs a half-hourly one — the sim already has
   half-hourly settlement, so a ToU factor is feasible and matters (cold-still tail = dirtier grid).
4. **Token energy-per-unit source.** Which published estimate (they span an order of magnitude); or
   defer the token component and count only metered compute kWh until a defensible factor is chosen.

## Boundary honoured (CARBON_NOT_A_TARGET)

Every figure here is a MEASUREMENT input, never an objective. None of these factors, nor any metric
derived from them, may enter the fitness function / draw / risk committee / pricing-personalisation
reward path (the grep-guard `tests/company/test_carbon_not_a_target.py` enforces it). An
unavailable/zero factor must fail LOUD at BUILD, never read as "clean".

## What unblocks the SPENT emitter (the next E5 rung)

A single director values-call — **(a)** grid marginal-vs-average, **(b)** the scope boundary, **(c)**
the token-energy source (or defer tokens to metered-compute-only) — turns this register into concrete
factors, and the SPENT emitter (activity → `CarbonEvent`, using the `RESOURCE_AWARE_SCHEDULING`
compute/token sensor for usage) becomes buildable. The SAVED side still additionally needs the
per-household cost-and-carbon trajectory (personalisation, unbuilt). NET is derivable the moment
either side has one real event.
