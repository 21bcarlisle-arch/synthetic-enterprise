**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `EP16_anchored_generators`
**Knowledge:** how-gb-gas-and-power-prices-move -- `docs/market_research/the_worlds_gas_price_record_splices_daily_sap_from_2018_2026-11-18.md`

# Result: splicing daily SAP into the world's gas baseline from 2018 (2026-11-18)

*Delivery seat, claim `world-gas-baseline-splice-daily-sap-from-2018`. Predictions:
`SEAT_PREREG_SPLICING_DAILY_SAP_INTO_THE_WORLDS_GAS_BASELINE_FROM_2018_2026-11-18.md`, written before these runs.
Records: `load_nbp_history()` (proxy) against `load_gas_baseline_spliced()`. Both have 3,538 days, 2015-10-01 to
2025-06-07. No company result was read.*

## P1 — HOLDS. Outside the crisis the forward barely moves

Measure: a 12-month gas forward (`generate_forward_price`, risk 1.2), struck on the 1st of each month from
2018-04 to 2025-06. Outside 2021-08..2023-02, 68 of 68 dates are within ±10%. The worst are −9% (2024-09) and
±7% (2019-06, 2019-09/10, 2021-07, 2024-10).

## P2 — DIRECTION AND SIZE HOLD, TIMING REFUTED

The spliced forward is lower on all 12 of 12 dates in 2022, and the largest gap is −44%, above the 25% predicted.
That gap is at **2022-07-01**, not in the predicted window of 2022-08..2022-10. *The prediction was wrong on timing.*
The EWMA at 1 Jul reads April-June 2022, when GB within-day gas fell while TTF stayed high: the forward's lookback
leads the monthly-mean basis peak (August) by one to two months. The whole window, proxy → spliced, £/MWh:

| Struck | Proxy | Spliced | Δ |
|---|---|---|---|
| 2021-10-01 | 52.8 | 47.5 | −10% |
| 2021-12-01 | 76.6 | 70.0 | −9% |
| 2022-04-01 | 100.0 | 88.5 | −11% |
| 2022-06-01 | 85.8 | 53.2 | −38% |
| 2022-07-01 | 87.3 | 49.1 | **−44%** |
| 2022-08-01 | 119.8 | 69.2 | −42% |
| 2022-09-01 | 167.3 | 113.7 | −32% |
| 2022-10-01 | 164.9 | 106.6 | −35% |
| 2022-12-01 | 84.1 | 51.2 | −39% |
| 2023-01-01 | 88.3 | 73.2 | −17% |
| 2023-03-01 | 57.3 | 57.3 | 0% |

So the world's 2022 gas forward is 30-44% too high from June to December. Every gas renewal priced in that half-year,
and every unhedged position marked against it, carries that error. Which way company results move is deliberately not read here.

## P3 — HOLDS. Daily and weekly gas volatility become gradeable from 2018

| Record, 2018-01..2025-06 | Days with a zero daily move | Daily log-return SD | Excess kurtosis | AR(1) of log level | Mean-reversion half-life |
|---|---|---|---|---|---|
| Proxy | 96.7% | 0.040 (month jumps only) | 186 | 0.9988 | 563 d |
| Spliced | 0.0% | 0.106 | 103 | 0.9899 | 68 d |

The spliced record by regime:

| Spliced, by regime | Daily SD | Median \|Δlog\| | 95th pct \|Δlog\| | Weekly SD | Half-life |
|---|---|---|---|---|---|
| 2018-20 | 0.076 | 0.026 | 0.125 | 0.180 | 62 d |
| 2021-22 | 0.176 | 0.044 | 0.285 | 0.459 | 19 d |
| 2023-25 | 0.040 | 0.019 | 0.074 | 0.094 | 38 d |

The SDs and kurtosis come mostly from the tails: 1 Mar 2018, 10-11 Jun 2022 and October 2022 are real within-day
events, not ingest faults (each was checked against the K8 page's account). An EP16 daily-scale grade should
read the median and the 95th percentile, not the SD alone. **EP16's daily and weekly gas scales are gradeable
from 2018-01-01 on this record. They stay ungradeable for 2015-10..2017-12.** The EP16 finding
(`SEAT_FINDING_THE_WORLDS_NBP_IS_A_MONTHLY_TTF_PROXY_SO_EP16_CANNOT_FIT_DAILY_GAS_VOLATILITY_2026-10-25.md`) is
answered for 2018 onward by this record, whether or not the baseline switches.

## Decision (blind to company results)

**Splice.** The proxy is faithful within ~1% except in 2021-22, and in 2022 it is 29% too high on the monthly
mean, and 30-44% too high on the forward, for a reason with a published mechanism (the NBP-TTF basis). That is a
fidelity defect in the one year the thesis is most tested on. The switch, which repoints the world's gas readers
from `load_nbp_history` to `load_gas_baseline_spliced`, is **not** made in this landing. DIRECTION.yaml `not_now`
holds it until skip1 and skip0 have read. It is handed on gated on skip0's output file.
