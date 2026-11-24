**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_2_generate_futures`

# The forward gas draw is independent daily noise, with no season and no persistence

Found by the delivery seat, 24 Nov 2026, grading the forward gas draw against the gas page
(`docs/market_research/how_the_gb_gas_price_forms_nbp_and_sap_2026-11-24.md`). Numbers:
`docs/staging/records/SEAT_RESULT_GRADING_THE_WORLDS_GAS_PRICE_RECORD_AGAINST_THE_GAS_PAGE_BY_REGIME_2026-11-24.md`.

**What.** `sim/scenario/gas_scenario_generator.generate_gas_scenario_prices` draws every day as an
independent Gaussian from one of two regimes, picked by a fresh Bernoulli each day, plus random
"dunkelflaute" days. Against post-crisis GB SAP (`baseline_2025`, 2026-27):

- daily log-return SD 0.501 against 0.037 (13.5×);
- lag-1 autocorrelation 0.005 against 0.984;
- 10.3% of days above 1.5 × their trailing-30-day median, against 0.0%;
- no seasonal term (its 1.07 winter/summer ratio is where its random storm days fell).

**Why it is LATENT, not BLOCKING.** Forward runs are held behind the correctness stretch, and no
published figure reads this draw today. It becomes BLOCKING the day a forward run prices a hedge or
a fixed tariff on it. A supplier would then face daily gas risk that GB does not have, and would
not face the seasonal and cold-spell risk that GB does have.

**What the page says a forward draw must show** (mechanism, not level): persistence (storage and
linepack, lag-1 ≈ 0.9+); a winter premium set by continental storage (§4); cold-spell and supply
shocks that persist for days, and are coupled to the world's own weather and wind (§6); and a hub
basis that can open when the interconnectors saturate (§5). The level and its band are
curriculum, the director's (R13). This finding does not set them.

**Not to be done before the K8 electricity page.** The gas and power draws must share their
weather. The rebuild is one design across both, item 4 of the BLOCKING steer finding. This row puts
the gas half of the evidence on file for it.

**Done means** a forward gas draw whose daily, seasonal and persistence statistics sit within the
post-crisis SAP regime's, graded by the probe in the result record, with its level read from the
curriculum.
