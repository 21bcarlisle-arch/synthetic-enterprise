# Item E check — what the weather engine actually provides, and what is missing (2026-08-03)

**Provenance:** director instruction by NTFY, 2026-08-03 09:35 UTC
(`docs/staging/from_rich_20260803_093552.md`): *"Item E from the fabric doc is still open. Do the check now:
what does the weather engine already provide for population-weighted temperature, capacity-weighted wind and
cumulative heating-degree windows, and what's missing? Then build the gaps. Also confirm the per-premise
physics is getting genuinely local weather and per-orientation sun, not a national average — if it isn't,
that's the averaging fault back one layer up."*

Every line below is `observed-with-evidence` from greps and reads against the live tree at commit
`0b370ef22`. Nothing here is recalled.

## 1. Population-weighted temperature — **MISSING**, and the DISCOVER doc is wrong about it

`grep -rniE 'weighted.{0,20}temp|temp.{0,20}weighted' sim/ simulation/ --include=*.py` returns **zero hits**.

What *does* exist is `simulation/premise_demand.py::demand_weighted_aggregate` — which weights **demand**,
not **temperature**. Those are different quantities: a demand-weighted demand aggregate tells you nothing
about the temperature the population actually experienced.

`sim/weather_engine.py::simulate_regional_deviations` genuinely produces Cholesky-correlated regional
deviations around a national front, so the *raw material* for a weighted index is there. It is simply never
weighted back into a national temperature index.

**`PREMISE_FABRIC_PHYSICS_DISCOVER.md` §4 item E states population-weighted temperature is "substantially
built" and should be recorded as "convergence evidence, not new input". That is incorrect** — it conflated
demand-weighting with temperature-weighting. Recorded here rather than quietly built around, because the doc
is the thing a future reader will trust.

## 2. Capacity-weighted wind — **MISSING**, and the error is already quantified

`grep -rniE 'capacity.?weight' sim/ simulation/ --include=*.py` returns **zero hits**.
`sim/weather_price_chain.py` loads `load_national_daily()`'s `wind_speed_mean_ms` — a **national mean** — and
feeds it directly into the power curve (`wind_power_output_fraction`).

This is not a speculative gap. `W1_7_renewable_capacity_trends` already recorded a **wind load-factor
residual of ~4.6–5.1x**, R4-diagnosed as *"the power curve being driven by NATIONAL-MEAN wind speed while
real turbines are sited non-randomly in high-wind locations"* — i.e. this exact defect, measured. It was left
unfixed there because fixing it re-opens the SSP merit-order calibration (R12/S8). That constraint still
holds and governs how the fix lands (see §5).

## 3. Cumulative HDD windows — **MISSING (memoryless)**, as the DISCOVER doc correctly said

`sim/weather_hdd.py` exposes `get_hdd`, `get_monthly_hdd`, `get_weather_factor`, `weather_factor_for_term`.
`grep -nE 'window|cumul|rolling|history|prev'` over that file returns **nothing**. HDD at date D depends only
on temperature at D.

Consequence: the third day of a cold snap draws the same gas as the first at equal temperature. Building
thermal mass and, at system level, storage/linepack drawdown are both unreachable — a real class of gas-demand
behaviour the sim cannot currently produce.

## 4. Per-premise physics — **the director's suspicion is correct on both counts**

**(a) It is running on a national average, not local weather.**
`simulation/fabric_physics.py:105-107` defines `DEFAULT_LATITUDE_DEG = 53.0`, commented in-code as
*"UK population-weighted latitude — an INPUT, not a per-home fabrication: callers with a real location pass
their own."* But
`grep -rn 'reconstruct_ambient_profile\|fabric_physics' --include=*.py simulation/ sim/ company/ tests/`
finds callers **only** in `tests/simulation/test_fabric_physics.py`. There is **no production caller at all**,
so nothing ever passes a real location and every premise gets latitude 53.0. The comment describes an
intention the code has never met — which is exactly "the averaging fault back one layer up".

**(b) There is no per-orientation sun.** The module computes `clear_sky_ghi_kw_per_m2` — global **horizontal**
irradiance — attenuated by observed daily cloud cover. There is no tilt/azimuth → plane-of-array
transposition anywhere in it (`orientation|azimuth|tilt|pitch|poa|plane_of_array` finds only unrelated
adoption-model covariates in `simulation/adoption_geography.py`). So a south-facing and a north-facing home
receive identical solar gain, which removes precisely the between-home diversity the fabric work exists to
create.

**Honest resolution constraint, stated up front so nothing downstream over-claims:** the real weather archive
is `sim/weather_data/C1..C4.csv` — **four sites**, and **daily**, not sub-daily. "Local" can therefore be
honest at 4-site resolution plus solar geometry from the premise's own latitude. It cannot be honest at
per-postcode resolution, and no artefact built on this may imply otherwise.

## 5. What is being built, and the one thing that is deliberately NOT being flipped

Three parallel forks, disjoint file scopes:
1. **Cumulative HDD windows** — `sim/weather_hdd.py`, existing memoryless API kept byte-identical (additive).
2. **Weighted indices** — a new `sim/weather_weighting.py` for population-weighted temperature and
   capacity-weighted wind, with **real sourced weights** (fabricated weights are forbidden; an unavailable
   source fails loud rather than degrading silently to uniform).
3. **Local latitude + per-orientation sun** — `simulation/fabric_physics.py`, with a cited transposition model.

**Not flipped:** the weighted wind index lands **additive and opt-in**. Re-pointing
`sim/weather_price_chain.py` or `sim/price_engine.py` at it re-opens the calibrated SSP merit order (R12/S8),
which is a separate decision on its own evidence — the same pattern W1_7 used, where `year=None` stayed
byte-identical. The national-mean-vs-capacity-weighted difference will be reported as a **diagnostic, never a
target**.
