**Severity:** BLOCKING · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Forward weather and prices must move together, and spells must last as long as real ones (2026-11-11)

**Type:** STEER, through the advisor channel. The director's words, from chat on Wed 11 Nov:

- 11:52 GMT, on a post about Monte Carlo and the temporal clustering of extreme events: "standard Monte Carlo simulations that sample independently from a marginal probability distribution match the static frequency, mean, and variance of price spikes, but destroy the sequence. In power markets, a 10-day cold-snap cluster causes severe liquidity drawdowns, cash flow strain, and battery/storage depletion, whereas 102 isolated spike hours spread across the year are easily absorbed."
- 11:53 GMT: "Wil it still work when we simualted forward dates and weather?"
- 11:54 GMT: "Huh?! I thought it would simualted weather"
- 11:55 GMT, on the advisor's recommendation below: "Stage it"

## What the advisor found (check it)

- **Historical years are fine.** Weather and prices are both the real record, so they coincide as they did.
- **Forward years replay analogue weather.** `sim/weather_world.py::extended_by_analogue_years` replays one complete year of the record per forward year, the same year in every regime. The record holds **2016–2025 only** (`sim/weather_world/daily.csv.gz`), so every forward year is one of ten real years.
- **Forward weather and forward prices are uncoupled, by the code's own named simplification:** "analogue weather is independent of the synthetic wholesale series it sits beside, so a cold year no longer moves the price the way 2021-22 did. That coupling is the price generator's to model."
- **A statistical weather generator exists** (`sim/weather_engine.py`: AR(1) with seasonal regime-switching covariance, calibrated). It is used by older calibration and demand paths, not by the forward world.
- **The futures fleet is held flat past 2025** (R13). Which future system the company faces stays his.

So the joint episode that drains a supplier, a long cold, still spell with high demand, low wind and high prices **together**, is under-represented in forward years. Weather clusters and prices may cluster, but they do not coincide. Survival and stress results for forward winters are therefore probably optimistic.

## The outcome wanted

1. **Weather and prices move together in forward years,** in multi-day spells as well as single hours, and so do demand, wind output and carbon. Choose the method and justify it with evidence. Two candidates:
   - **Matched-block replay:** a forward year that replays 2018's weather also takes 2018's price shape, rescaled to the forward year's level. Simple, and keeps the real coupling.
   - **Prices generated from the replayed weather** through the existing weather→demand→price chain (`sim/weather_price_chain.py`). More general, and works with a changed future fleet.

   Whichever is chosen, a forward cold-still spell must produce its price consequence. Prove it on a named spell.
2. **Spell length is validated, not only frequency and size.** Count runs of cold-still days and of high-price days, plus their joint runs, in the real record and in generated forward worlds. Compare the run-length distributions with a confidence band from block-resampling the real years. If generated spells are too short or too rare, say so. The remedies are on the table (regime-switching, block bootstrap); choose on the evidence.
3. **The record reaches the rare long spells.** Extend the weather record back to about 1980 from the same two sources (HadUK-Grid temperature, which goes back to the 1880s; ERA5 wind, cloud and precipitation, which go back to 1940), so forward years can draw spells like December 2010, January 1987 or 1962–63 if the extension reaches it. Knowledge page first (K8). Say whether the forward worlds' worst spells change. Prices for pre-2016 years do not exist in our record, so this depends on item 1's method. Say how matched-block replay would handle years with weather but no matching price.
4. **The company's cash and risk tests live through the joint episodes.** Confirm the liquidity, hedging and VaR paths experience multi-day coupled stress in forward years, not just stressed hours. Survival is judged worst-case over the sampled set (23 Jul canon).
5. **Climate drift is a note, not a build.** Whether replayed older years need a warming adjustment for forward dates. UKCP18 is the obvious source. Say how large, with its source. Build nothing unless it matters.

## Rules

- **Baseline, curriculum and R13.** Coupling and record extension are fidelity changes, decided blind to company results. How many stressed worlds are sampled, and the future fleet, stay the director's curriculum.
- **One variable at a time.** Coupling first, measured, then the record extension, measured. Re-baselining is expected and stated.
- **The wall.** The company sees only what a real supplier would: forecasts and outturn as published, never the replayed year's identity or the coming spell.

## Risk

Touches: the forward world (weather replay, price generator), the weather store, and the company's risk and liquidity paths through the seam.
Blast radius: every forward run. Survival and VaR results are expected to worsen. That would be the truth arriving, not a regression.
Probable failure modes:
- **Rescaling a replayed price shape so that the forward level is right but the spike-to-base ratio is wrong.** Validate the shape and the level separately.
- **A coupling that leaks the replay year to the company, for example a price pattern that identifies 2018.** Check it through the epistemic verifier.

Proportionality: contract-touching — implement with the named mitigations.

## A plain correction to three earlier advisor notes

Three steers staged on 10 Nov carry `**Lane:** W`, which is not a lane in `background/finding_severity.py`, so their severity is unclassified. That is the advisor's error. Correct each header to `W2_customer_generator`:

- `DIRECTOR_STEER_A_REAL_RANGE_OF_PV_BATTERY_EV_AND_LOAD_IN_THE_WORLD_INSPIRED_BY_PREDBAT_2026-11-10.md`
- `DIRECTOR_STEER_HOW_EACH_ASSET_IS_RUN_IS_A_SOURCED_MIX_BUILT_ON_THE_EXISTING_PHYSICS_2026-11-10.md`
- `DIRECTOR_STEER_THE_SUPPLIER_CAN_PERSUADE_AND_SUPPORT_GOOD_CANDIDATE_HOMES_TO_CHANGE_AND_INVEST_2026-11-10.md`

— Director steer, 11 Nov 2026, his words above; the code reading and drafting are the advisor's.

## Done

(seat executor, 11 Nov.) **Filed, not built, on his 12:00 ruling** ("Steers already staged, including the 11 Nov
forward-weather steer, are queued for the weekly balance review and not drawn before Mon 16 Nov"). It sits in
`held_behind_the_exit_test` in `docs/direction/priority_order.yaml` with that date on it. The advisor's code reading
was not re-checked this turn; whoever draws it after the reset checks it first (the steer asks for that). The plain
correction at the foot was made now, because it is a factual correction: the three 10 Nov asset steers' headers
read `**Lane:** W2_customer_generator`.
