**Severity:** RECORDED · **Lane:** W_world · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `world-yoy-weather-store-extension-then-regrade`

# Result: the prebound channel's price leg gets the 2022 gas median roughly right and the distribution wrong

Grades `SEAT_PREREG_WHETHER_THE_PREBOUND_CHANNELS_DEAD_PRICE_INPUT_REPRODUCES_THE_2022_SAME_HOUSEHOLD_RESPONSE_2026-10-11.md`.
The predictions were committed (`99aa19ad9`, re-landed `817656d17`) before the run. Nothing was
changed in the world: this is a measurement of what wiring the dead input WOULD do. Decided blind to
company results.

## What was run

The only difference between arms is the `unit_price_p_per_kwh` that `comfort_constraint_for` sees.
- **Off:** the default, which equals the 4.0p reference, so there is no response. This is the world today.
- **On:** the household-facing gas rate (`svt_rates.get_svt_gas_rate_charged_to_household_gbp_per_mwh`,
  including EPG), averaged over the segment's days.

Each arm uses the same premise, the same stored weather days (2021–2024) and the same seed. The
population is every fabric-eligible, gas-heated premise of the live book that the store reaches at
HEAD: **n = 230** (before the store extension). The script is at the end. Reduction is
`1 − kWh(on)/kWh(off)`.

| window | median | IQR | SERL / published |
|---|---|---|---|
| gas, Oct 2022–Mar 2023 | **14.8%** | 12.1 → 16.7 | SERL 10.78%, IQR 1.19 → 22.44 |
| electricity, same homes, same winter | **0.6%** | 0.3 → 1.1 | SERL 8.38%, IQR −0.48 → 17.56 |
| gas, Oct 2023–Mar 2024 | 13.3% | 10.9 → 15.1 | NEED cumulative 2021→2024: 13% |
| gas, Oct 2021–Mar 2022 (price had not yet risen) | **6.3%** | 5.0 → 7.5 | ~0 (the cap rose in April 2022) |
| gas, Jun–Aug 2022 | 1.0% | 0.0 → 7.3 | — |

Winter 2022/23 gas by stress band: HIGH 9.6% (n = 7), LOW 14.9% (n = 176), MODERATE 14.6% (n = 47).

**Frame check.** On 25 premises, non-heating gas (`gas_kwh − gas_space_heating_kwh`) is identical
between arms, in summer and in winter. The summer movement is residual space heating. So the leg
reaches heating and nothing else, and the counterfactual is one variable.

## Grading

| # | predicted | result |
|---|---|---|
| Q1 | gas median 20–40% (2–4× SERL) | **Refuted.** 14.8%: 1.4× SERL's median and inside SERL's IQR. I read the intensity clamp (0.40 → 1.00) as a proportional kWh cut. It is not one: the 3.5 °C setpoint cut and the 45% of comfort hours lost act on space heating only, and space heating fell by roughly 8–27%. |
| Q2 | gas lower quartile above 8% (SERL 1.2%) | **Held.** 12.1%. The IQR is 4.6 points wide against SERL's 21. No household barely moved and no household used more. |
| Q3 | electricity below 1.5% | **Held.** 0.6% against SERL's 8.4%. Electricity has no price response at all. |
| Q4 | gas 2023/24 at 15–35%, above NEED's 13% | **Refuted on the band.** 13.3%. Persistence is real, though: the response barely decays (14.8 → 13.3), because the reference is a fixed price level. |
| Q5 | HIGH cuts least, against SERL's ordering | **Held on the median, weakly.** HIGH 9.6% against LOW 14.9%, but n = 7. LOW and MODERATE are indistinguishable. |

**Not predicted: the response starts before the price moved.** Gas falls 6.3% in Oct 2021–Mar 2022.
The cause is that the mechanism holds one constraint per calendar-year segment. On a segment-average
price, the 2022 constraint carries April's and October's rises back into January–March 2022. Any
wiring at that granularity has this defect, whatever average is chosen. The constraint has to be
re-evaluated when the price changes, not on 1 January.

## What this licenses

The pre-registration named two branches and the result lands in neither. Q1 missed by being closer
to SERL than predicted. Q2's lower quartile is 12%, not below 4%. So the verdict follows the
evidence, not a branch:

- **Do not wire the leg as it stands.** The median is close, but the shape is wrong in four ways
  that each matter to a forecast or a bill:
  - no spread;
  - an anticipatory cut a quarter before the price rose;
  - no decay;
  - no electricity response.
  A forecast ranked against this world would learn that every gas home cut 12–17%. SERL says a
  quarter cut less than 1.2% and a quarter cut more than 22%.
- **`_PRICE_ELASTICITY = 0.45` is not refuted on its median and is still unsourced.** The median is
  what it gets nearly right. The next step replaces it with a mechanism keyed to the published
  distribution. Each household draws an elasticity from SERL's distribution: gas median −0.071,
  IQR −0.144 to −0.010; electricity median −0.099, IQR −0.223 to 0.016. Each responds to the change
  against its own prior-winter price, so the response decays when prices fall, and the constraint
  is re-evaluated at each price change. SERL's 2022/23 reduction table stays held out to grade it.
  That is a new one-variable pre-registration.
- **The electricity response is a GAP with no mechanism.** The comfort constraint is a heating
  lever. SERL's −8.4% on electricity is appliance and lighting behaviour, which nothing in the world
  moves with price. Filed, not invented.

## The script

`/var/tmp/se-price-response/price_on_off.py`, run from a worktree at `68d8f3e27`. Reproduced here
in substance: the comfort constraint is wrapped, and in the `on` arm the wrapper reads the calling
segment's days and passes `mean(gas_rate(d)) / 10` as `unit_price_p_per_kwh`. Each fabric-eligible
gas-heated premise is built with `fabric_demand_path.build_fabric_series` under both arms over
2021–2024 on `WeatherWorldSource.days`, and the windowed sums of `gas_kwh` and
`gross_electricity_kwh` are compared.
