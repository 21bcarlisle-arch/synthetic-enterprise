**Severity:** RECORDED · **Lane:** W_world · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `world-yoy-weather-store-extension-then-regrade`

# Pre-registration: does the prebound channel's dead price input reproduce the 2022 same-household response?

Written 2026-10-11 ~08:30 BST, before any run of the change below. Separate from, and after, the
weather-store step
(`SEAT_PREREG_HOW_MUCH_OF_THE_YEAR_ON_YEAR_GAP_IS_THE_WEATHER_STORE_NOT_REACHING_THE_BOOK_2026-10-11.md`).
A fidelity question about the world, decided blind to company results. This file is not edited
after the run; the result goes beside it in a separate record.

## What the world already has (read, not measured)

`simulation.premise_trace.comfort_constraint_for` already takes `unit_price_p_per_kwh` and adds
`_PRICE_ELASTICITY * max(0, price / 4.0p - 1)` to the household's rationing intensity, which sets the
setpoint cut (up to 3.5 °C) and the comfort hours lost (up to 45%). **No caller passes the price**
(`fabric_demand_path.build_fabric_series` passes only `income_stress` and `prior_year_bill_gbp`,
and prices that bill at the fixed 4.0p), so `price_ratio` is 0 in every year. Its own docstring
registers this: "the household shows no response to the 2021-22 crisis prices it actually paid".

Printed at real inputs, with the household-facing gas rate
(`svt_rates.get_svt_gas_rate_charged_to_household_gbp_per_mwh`, EPG-inclusive), MODERATE stress:

| date | gas p/kWh | intensity, price fed | intensity today | setpoint cut |
|---|---|---|---|---|
| 2021-07 | 3.34 | 0.40 | 0.40 | 1.40 °C |
| 2022-05 | 7.37 | 0.78 | 0.40 | 2.73 °C |
| 2022-11 / 2023-02 | 10.32 | **1.00 (clamped)** | 0.40 | **3.50 °C** |
| 2024-02 | 7.42 | 0.78 | 0.40 | 2.75 °C |
| 2025-02 | 6.34 | 0.66 | 0.40 | 2.32 °C |

Two things are visible before any run:
- **The reference is a fixed price LEVEL, not last winter's price.** The response never decays,
  so the world would show a permanent post-2022 cut sized by the price level.
- **`_PRICE_ELASTICITY = 0.45` has no source** (its comment: "`domain-knowledge`, candidate to
  verify"). SERL's published median short-run gas elasticity is −0.071 (IQR −0.144, −0.010).

## The published target, held out (it grades; it is not written into the world)

`docs/market_research/how_much_a_same_households_use_moves_year_on_year_and_in_2022.md`:
SERL (Zapata-Webborn et al. 2024, N = 5,594, same household, weather held in a per-household
counterfactual), winter Oct 2022–Mar 2023 against the counterfactual from Oct 2021–Mar 2022:

| fuel | median reduction | IQR |
|---|---|---|
| gas | **10.78%** | 1.19% → 22.44% |
| electricity | **8.38%** | −0.48% → 17.56% |

DESNZ ECUK Table C9, annual, temperature-corrected 2021→2022: gas −11.6%, electricity −8.5%.
NEED: cumulative 2021→2024 fall, gas 13%, electricity 9%.

## The one-variable step

Change ONLY the price the constraint's `unit_price_p_per_kwh` leg sees: from the default (equal to
the reference, so no response) to the household-facing gas rate on the segment's date. The
bill-pressure leg (`prior_year_bill_gbp` at 4.0p) is left as it is: feeding both at once would be
two variables.

**The counterfactual is the world's own, and it is cleaner than SERL's**: the same premise, the
same weather days, the same seed, with the price leg on and off. The reduction is
`1 − kWh(on) / kWh(off)` per premise over Oct 2022–Mar 2023, and the same over Oct 2023–Mar 2024
for persistence. Population: the fabric-eligible gas-heated premises of the live book (as many as
the store reaches when this runs; the count is stated with the result).

## Predictions

| # | prediction |
|---|---|
| Q1 | Gas, winter 2022/23: median reduction **20–40%**, i.e. about 2–4× SERL's 10.8%. |
| Q2 | Gas, winter 2022/23: the **lower quartile is above 8%** (SERL's is 1.2%): the mechanism has no household that barely moved, because heterogeneity comes only from three stress bands and the clamp. |
| Q3 | Electricity of the same gas-heated homes, winter 2022/23: median reduction **below 1.5%** (SERL 8.4%): the channel acts on heating only, so the electricity response has no mechanism at all. |
| Q4 | Gas, winter 2023/24: median reduction **15–35%**, above NEED's 13% cumulative 2021→2024 fall: the fixed-level reference makes the response permanent. |
| Q5 | HIGH-stress households cut **least** (they start at 0.80 and clamp at 1.0), LOW-stress cut **most**. SERL Fig. 3 reports poorer households MORE elastic on gas. Predicted: the ordering is inverted against SERL. |

## What each outcome licenses

- **Q1 and Q2 hold (overshoot, no spread):** the existing coefficient is refuted against a
  published same-household distribution and is NOT wired as it stands. The next step is a
  replacement keyed to published evidence: a per-household elasticity drawn from SERL's
  distribution (median −0.071, IQR −0.144 to −0.010), against the PRIOR winter's price, so it
  decays when prices fall. That is a new pre-registration, graded against the same held-out table.
- **Q1 lands inside 8–14% and Q2's lower quartile is below 4%:** I was wrong about the
  saturation's size in kWh; wire the leg as it is and grade Q4.
- **Q3 holds:** the electricity response is a GAP with no mechanism; filed, not invented.

## What would refute the frame

- Price-on and price-off traces differ outside the heating season by more than 1%: then the leg
  reaches something other than heating, and the counterfactual is not one variable.
- The reduction is ~0 everywhere: then the constraint is not reaching `generate_premise_trace` on
  the settlement path, and a second dead input sits between the two.
