**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `anchor-the-446-bare-world-constants-in-impact-order`
**Knowledge:** world-constant anchors -- `docs/design/world_constant_impact_ranking.md`

# The cohort's four Census traits contradict observed tables the commons already holds, and nothing published reads them

**What is established.** `simulation/population_draw.py` draws four cohort traits, each from a
"national" table tilted per tenure or region. The tables are `_ACCOMMODATION_*`, `_CARS_*`,
`_NSSEC_*` and `_HEATING_FUEL_*`, eight registered bare constants. Their comments call them
"order-of-magnitude EHS/Census-consistent estimates" and documented SHAPES. The fuel comment says
"E&W has no equivalent row here because TS046 is not in the cache pack".
**That last claim is false.** Since 2026-07-20 the commons has held the observed Census 2021
marginals and every cross-tab the tilts approximate:
`docs/market_research/population_coverage/marginals.json` and `crosstabs.json`. The cross-tabs are
accom x tenure (RM003), tenure x cars (RM131), tenure x NS-SEC (RM138) and heating fuel x region
(TS046), all `observed`.

**How far apart, measured 19 Oct.** The drawn mix, weighted by Census tenure, against Census:

| trait | drawn | Census 2021 E&W |
|---|---|---|
| accommodation: semi / flat | 0.271 / 0.212 | 0.315 / 0.217 |
| cars: 0 / 1 / 2+ | 0.227 / 0.411 / 0.362 | 0.233 / 0.413 / 0.354 |
| fuel, Wales: mains gas / oil | 0.607 / 0.116 | 0.716 / 0.078 |
| fuel, London: heat network | 0.114 | 0.034 |
| fuel, North West: heat network | 0.030 | 0.005 |

Cars are close. Fuel is the worst. The regional tilts were set against a national base that is
itself off: oil 0.02 against 0.035, and heat networks 0.03 against 0.009. Correcting the base alone
would make Wales worse. The remedy is to replace the national-times-tilt construction with the
observed conditional, P(fuel | region) and P(trait | tenure), derived from the cross-tab and the
marginal. That is a re-derivation from the commons. No new evidence is needed. Scotland's measured
UV407 row stands as it is, stated as shares.

**Why it is ranked low, not fixed now.** The direction is impact order. The book-draw instrument
scores all eight at 0.000 (rows 42-49 of the ranking). The only reader of the cohort's
`heating_fuel` outside `population_draw` is `simulation/population_coverage.py`, a coverage
report. The premise's real heating system, the one demand reads, comes from
`simulation/premise_population.py`. **So one fact has two homes.** The cohort draws a Wales that is
61% mains gas, and the premise draws its own. Only one of the two can reach a bill. Unless the
production screen shows `population_draw`'s 0.90% gross move coming from these tables, the
correction waits behind the constants that move published figures. When it is done, also reconcile
the cohort's fuel with the premise's heat system, or delete the cohort trait.

**Also anchored on this claim.** `DD_SHARE_GAS` cited DESNZ QEP June 2026 through `ASSUMPTIONS.md`,
but it sat directly beneath `DD_SHARE_ELEC`, which is the comment reader's known hole. It now
carries its own trailing citation.
