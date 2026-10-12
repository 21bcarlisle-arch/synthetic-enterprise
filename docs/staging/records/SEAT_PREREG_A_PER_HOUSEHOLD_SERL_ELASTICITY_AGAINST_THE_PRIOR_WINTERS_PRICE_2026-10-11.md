**Severity:** RECORDED · **Lane:** W_world · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `world-2022-price-response-from-serl-elasticity`

# Pre-registration: a per-household SERL elasticity, against the prior winter's price

Written 2026-10-11, before any run of the mechanism below. Follows
`SEAT_RESULT_THE_PREBOUND_PRICE_LEG_GETS_THE_2022_GAS_MEDIAN_ROUGHLY_RIGHT_AND_THE_DISTRIBUTION_WRONG_2026-10-11.md`,
which measured the dead prebound price leg and did not wire it. A fidelity question about the world,
decided blind to company results. This file is not edited after the run; the result goes beside it.

## The mechanism (one variable: the response on or off)

`simulation/price_response.py`, applied inside `fabric_demand_path.build_fabric_series` after the
trace is generated, as a per-day multiplier on each fuel's kWh:

- **Each household draws two elasticities**, one per fuel, from SERL's published per-household
  distribution (Zapata-Webborn et al. 2024, `docs/market_research/how_much_a_same_households_use_moves_year_on_year_and_in_2022.md`):
  gas median −0.071, IQR −0.144 to −0.010; electricity median −0.099, IQR −0.223 to +0.016.
  The draw goes through a split normal fitted to the median and each quartile. **The tails beyond
  the quartiles are not published**, so the split normal is a named shape assumption. **The joint is
  not published either**, so the two fuels are drawn independently. Some households draw a
  positive elasticity and use more, as some of SERL's households did.
- **Response years run April to March.** The price a household reacts to is the cap's
  household-facing unit rate on the day (`svt_rates`, EPG-inclusive), so the response is
  re-evaluated at every cap change, not on 1 January. The reference is the mean rate over the
  household's PRIOR winter (October to March, SERL's window). The response chains:
  `M(d) = L(k−1) × (1 + ε × (p(d) / p̄_winter(k−1) − 1))`, with
  `L(k) = L(k−1) × (1 + ε × (p̄_winter(k) / p̄_winter(k−1) − 1))`. So a level, once cut, is carried
  forward, and a fall in price is answered against the winter just gone, which is where the decay
  comes from.
- **Before response year 2022 there is no response (`M = 1`).** Winter 2021/22 is SERL's
  counterfactual winter. SERL's elasticity is crisis-specific, and the knowledge file says it
  "should not be read as the world's general-purpose elasticity". So it is not applied to
  2016–2021.
- **The lever is the whole fuel, not the heating.** SERL measured whole-fuel kWh. Electricity has no
  heating lever in a gas home, so this is the only lever there is for it. The day's shape is
  preserved; SERL's top quintile cut its thermostat, and a shape-changing response is not modelled.
- The existing prebound leg (`_PRICE_ELASTICITY = 0.45`, dead) is not touched. That would be a
  second variable.

**A check on the form, before running.** If ε is "% change in kWh per % change in price", then the
median gas elasticity × the world's own cap change, winter 21/22 → 22/23 (4.07p → 10.32p,
+153.6%), gives 0.071 × 153.6 = **10.9%**. That is SERL's 10.78% median reduction. So the form
reproduces SERL's gas figure from SERL's own elasticity. **For electricity it does not**:
0.099 × (20.80p → 34.00p, +63.5%) = **6.3%**, against SERL's 8.38%. I cannot yet say why. The
candidates are a different price basis in the paper (a standing charge, or the household's own
tariff) and the median of a ratio not being the ratio of medians. Either way, a predicted miss.

## The harness

`/var/tmp/se-price-response/price_on_off_serl.py`, which is `price_on_off.py` with the arm changed.
It uses the same premise, the same stored weather days (2021–2024) and the same seed. Only
`build_fabric_series(price_response=...)` differs between the arms. The population is every
fabric-eligible, gas-heated premise of the live book that the store reaches. The reduction is
`1 − kWh(on)/kWh(off)`.

## Predictions

| # | window | prediction | held-out published figure |
|---|---|---|---|
| P1 | gas, Oct 2022–Mar 2023 | median **10.9% ± 1.5**, IQR about **(1.5, 22.1)**, each quartile ± 2.5 for sampling | SERL 10.78%, IQR 1.19 → 22.44 |
| P2 | electricity, same homes and winter | median **6.3% ± 1.5**, IQR about **(−1.0, 14.2)**: a ~2-point miss on the median | SERL 8.38%, IQR −0.48 → 17.56 |
| P3 | gas and electricity, Oct 2021–Mar 2022 | **0 for every premise** (\|x\| < 0.01%): the response does not begin before the price moved | ~0 by SERL's design |
| P4 | gas, Oct 2023–Mar 2024 | median **8.8–9.2%**: a partial decay from 10.9% | NEED cumulative 2021→2024: 13% (bundled with turnover) |
| P5 | gas, Jun–Aug 2022 | median **5.8% ± 1** | — |
| P6 | gas vs electricity reduction, per premise, winter 22/23 | Spearman **\|ρ\| < 0.15**: the draws are independent | SERL Fig. 3 implies they are not comonotone; the joint is not published |
| P7 | gas, calendar 2022, whole year | median **4–7%**, a **miss** against ECUK's −11.6% (temperature-corrected 2021→2022): nothing responds in January–March 2022 | DESNZ ECUK C9 −11.6% gas, −8.5% electricity |
| P8 | the off arm | **byte-identical** to `build_fabric_series` at HEAD without the argument | — |

## What each outcome licenses

- **P1, P3 and P8 hold:** the mechanism is correct as built. It is landed with
  `price_response` OFF by default. Turning it on in the settled book is the next one-variable step.
  It moves every gas and electricity volume from April 2022 onward, so it re-takes the world digest
  and the value arms with it.
- **P1 misses:** the wiring is wrong, because P1 is arithmetic. Find out why before anything else.
- **P2 misses as predicted:** the electricity price basis is a GAP to research (the paper's price
  definition), not a number to tune.
- **P7 misses as predicted:** the response before April 2022 (the October 2021 rise, and
  anticipation) is a named gap. ECUK's annual figure carries it and SERL's design cannot see it.

## What would refute the frame

- The on arm differs from the off arm on any day before 2022-04-01. Then the multiplier reaches
  something other than its own window.
- The off arm differs from HEAD. Then the change is more than one variable.
