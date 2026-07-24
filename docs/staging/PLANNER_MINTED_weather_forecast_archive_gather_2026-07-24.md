# [PLANNER-MINTED] Weather forecast archive — gather NESO/Elexon forecast-vs-outturn pairs, measure σ(horizon) (2026-07-24)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). Rungs 1–6 drew empty this
tick; agenda + staging root empty (bar a routine `run_complete` marker). Minted from a ratified goal.
**Propose-then-proceed.** Lane: **DISCOVER** (read-only research + data ingestion + correlation) —
**NOT** a simulator BUILD; opens no gate, moves no level.

## Ratified goal served
- **DIRECTOR_AXES v1 — Axis 3 (Believability):** *"Weather ... does it feel like the real UK market
  to a 20-year veteran."* Weather is the **first-named** believability item and the tightest-growing
  one (renewables share rises every year → weather's grip on wholesale price tightens every year).
- **`DIRECTOR_STEER_WEATHER_SIM_PURPOSE_2026-07-23.md` §2 — the director's own words: "this is the
  key steer"**: *gather → correlate → select → simulate. Do not pick simulation variables by
  intuition.* §2.1 names the **only genuinely ungathered data** in the chain: *"the forecast
  archive: NESO/Elexon publish day-ahead (and other horizon) wind and demand forecasts alongside
  outturns. Forecast-vs-outturn pairs are the ONLY way to measure error-by-horizon — outturn data
  alone cannot reveal it, however long the record."*

## Why this is drawable NOW (not gated)
The steer §Preamble states plainly: *"It authorizes no BUILD, opens no gate, moves no level."* But
**DISCOVER/FRAME/research/data-gathering are always-available** (epoch-gating gates BUILD, never
thought — `MATURITY_MAP.md` §9). Gathering a public data archive and measuring its error structure
is DISCOVER by definition. It is also the **strict prerequisite** for every downstream weather-lane
decision: you cannot correlate-and-select variables (§2.2) or build the forecast layer (§3) until the
forecast-vs-outturn pairs exist. Two-way-door filter: this mint gathers the upstream data; it does
**not** build the downstream simulator that depends on it.

## Real-world fidelity gained
- **Error-by-horizon becomes measurable.** A real supplier prices weather risk on a fixed tariff off
  *forecasts and their error*, never outturn (steer §3). Today the sim has outturn only, so σ(horizon)
  — the error that shrinks toward delivery — is unmeasured and therefore unmodellable. This gather
  produces the empirical σ(horizon) curve the forecast layer must later be anchored to.
- **The epistemic wall gets a free, honest instrument.** Forecasts are genuinely public
  (company-knowable); outturn arrives only at delivery. Forecast error is the *natural* Point-in-Time
  wall on the future — no artificial blinding needed (steer §3). Gathering real pairs lets the wall be
  measured, not asserted.

## Scope (propose — DISCOVER only)
1. **Locate the sources.** NESO/Elexon day-ahead (and other horizon) **wind** and **demand**
   forecasts alongside outturns (Elexon Insights `data.elexon.co.uk`; NESO CKAN). Pre-load
   ground-truth API context before any local model touches the endpoints (key learning: local models
   confabulate endpoints). PROBE network first — network is per-tick env-dependent, not always blocked;
   if genuinely unreachable this tick, record "drained-pending-network" with the probe evidence and
   the exact endpoints identified, so the next tick with network resumes.
2. **Gather forecast-vs-outturn pairs** into a research artefact under `docs/market_research/`
   (raw pairs + provenance/URLs/pull-date; no fabricated values — cite or leave absent).
3. **Measure σ(horizon):** forecast error as a function of lead time (seasonal-normal months out →
   day-ahead → within-day), per variable (wind, demand). Report the empirical error curve.
4. **FRAME the correlate/select step (§2.2) as the named downstream** — do NOT execute it here (it
   depends on this gather + is itself pre-BUILD): judge candidate variables on **tail explanatory
   power, not average R²** (worst-cell discipline), parsimony as the design test.

## Walls untouched (director-reserved, explicitly)
- **No simulator BUILD.** The forecast layer (§3) and any variable added to the weather engine are
  BUILD, gated behind the §2 selection this mint only *enables*. Not built here.
- **Generator ground truth / curriculum values** stay director-reserved — this gathers *real published
  data* and measures its error; it tunes nothing and decides no difficulty. (R13: the baseline may only
  change for fidelity-to-reality reasons; this mint changes no baseline, it gathers reality.)
- **Anti-marking-own-homework (steer §3, standing rule):** the eventual generator anchor and the
  validator anchor must remain **independent sources** — this gather feeds the *evidence* commons, not
  one side's implementation. No L3 self-promote. No one-way door.

## Propose-then-proceed window
Standing DISCOVER authority (always-available lane); proceed. Nothing here is irreversible (a research
artefact reverts). Escalate nothing unless a source pull hits a platform-admin/credential wall (none
expected — Elexon is key-free, NESO CKAN is open).

## Planner census (why this batch is small, not padded)
Honesty-over-velocity (named-standard): I minted the genuinely **un-covered** ratified work, not a
fixed count. The PRODUCT-FIRST queue is already drawable via open `in_progress/` mints —
`generator_draw_wiring` (item 2), `value_chain_observation_window_cap` (item 3),
`premise_demand_publish` (item 4, built+pushed, awaiting live-pixel); spike-tail (item 5) is CLOSED;
`ssp_negative_lift_cells` and `payment_truth_detection_gap` cover the top fidelity/coupled gaps; the
SITE_V5 campaign is closed and the FRONT_MISSION_BLOCK front-door rebuild is live (verified this tick:
hero = the mission/carbon thesis, £273/tCO₂e yardstick, carbon ledger honestly absent, cost-to-serve
moved to /proof). Re-minting any of those would be padding — the exact pattern that produced NO-BUILD
closures on 2026-07-24. This gather is the one strong genuinely-un-covered ratified item; the WVC
register live-feed is minted alongside it.

— RUNG-7 planner, 2026-07-24 worker tick.
