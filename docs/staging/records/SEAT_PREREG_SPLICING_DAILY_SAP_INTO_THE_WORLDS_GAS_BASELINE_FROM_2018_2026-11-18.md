**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `EP16_anchored_generators`
**Knowledge:** how-gb-gas-and-power-prices-move -- `docs/market_research/the_worlds_gas_price_record_splices_daily_sap_from_2018_2026-11-18.md`

# Pre-registration: what splicing daily SAP into the world's gas baseline from 2018 moves (2026-11-18)

*Delivery seat, claim `world-gas-baseline-splice-daily-sap-from-2018`. Written BEFORE the forward-curve and
daily-volatility measurements below were run. One thing was already known when this was written, and it is not
a prediction: the monthly means by year (proxy against SAP monthly mean, same months 2018-01..2025-06) differ by
at most 1% in 2018-20 and 2023-25, by -8% in 2021 (SAP lower) and by -29% in 2022 (proxy £100.0, SAP £71.0/MWh;
worst month Aug 2022, £186.5 against £128.8).*

Decided blind to company results: nothing below reads a book, a margin or a run.

## Predictions

1. **Gas forward, 12-month, risk factor 1.2** (`sim.forward_curve.generate_forward_price`), struck on the 1st of
   every month 2018-04..2025-06 on the proxy record and on the spliced one. Outside acquisition dates in
   2021-08..2023-02 the spliced forward is within ±10% of the proxy's on at least 90% of dates. (The proxy is a
   step function and SAP is not, so a 30-day EWMA can differ by more than the monthly-mean basis near a
   turning point; ±10% is the band, not ±1%.)
2. Inside 2022-01..2022-12 the spliced forward is LOWER on at least 9 of 12 dates, and the largest relative gap
   (spliced below proxy) is at least 25%, at a date in 2022-08..2022-10.
3. **EP16, daily scale.** On the proxy record from 2018, the daily log-return is zero on more than 95% of days
   (by construction). On the spliced record from 2018, it is zero on fewer than 5% of days, its excess kurtosis
   is above 3 (fat tails), and the AR(1) coefficient of the daily log level is below 1 (mean reversion), which
   makes daily and weekly gas volatility gradeable from 2018-01-01. It stays ungradeable for 2015-10..2017-12.

Refuted if any of the three fails as written. The result goes beside this file, with these predictions unedited.
