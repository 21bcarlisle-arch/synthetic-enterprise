# Pre-registration: the CfD levy, built from strike against the world's price, checked on the record

**Filed:** 24 Nov 2026, 09:10 GMT, by the worker. Written before the LCCC series were fetched in full. Two
sample rows of each series had been read, to learn the field names. No total, rate or payment had been
summed or compared.

**For:** item 5 of `docs/staging/WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`
("Endogenous CfD levy for forward years. Strike against the simulated reference price, times volumes.
Check it on the record against LCCC's Interim Levy Rate"). This is the on-the-record step only. No world
code changes here.

**Knowledge (K8):** `docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md` §3. Its
GAP 3 names the LCCC data this step reads. That page's correction stands: the ILR has a floor of zero,
so the check is against the **net payment** and LCCC's **reconciled daily levy rate**, which can go
negative. It is not checked against the ILR.

## Data (all LCCC Data Portal, OGL, read 24 Nov 2026 through the CKAN datastore API)

- `actual-cfd-generation-and-avoided-ghg-emissions`: per unit, per day: generation, strike price,
  market reference price and CfD payment.
- `reconciled-daily-levy-rates`: the daily levy rate and eligible demand, by settlement run. The
  latest run per day is used.
- `actual-eligible-demand`.

## Definitions, stated before measuring

- **Net CfD payment** for a day: the sum over units of `CFD_Payments_GBP`. It is positive when LCCC
  pays generators (suppliers pay) and negative when generators pay back.
- **Built payment**: the sum over units of (strike − reference) × generation, from the same rows.
- **Levy rate**: net payment ÷ reconciled eligible demand, in £/MWh. Quarterly figures weight by
  demand, so a quarter's rate is its summed payment over its summed demand.
- **The world's reference price**: the world's own daily mean of its replayed half-hourly price
  (`sim/scenario/data/real_ssp_daily_mean.json`, the Elexon system sell price).

## Three legs, one variable each

- **Leg A, the identity.** The built payment against LCCC's reported payment, and the quarterly levy
  rate from payments against LCCC's reconciled levy rate. This proves the definition before anything
  is swapped.
- **Leg B, the world's price.** For the intermittent units (reference type IMRP), replace the
  reference with the world's daily mean price. Keep the real strike and volume. Baseload units (BMRP)
  keep their real reference. Data runs to the world's last day, 2025-06-07.
- **Leg C, the null.** The same swap with a flat reference: each quarter's mean world price applied
  to every day. This tests whether the world's day-to-day price movement adds anything.

## Predictions

1. **A1.** The built payment matches the reported payment to within 1% in every year 2016-2025.
2. **A2.** The quarterly levy from payments matches LCCC's reconciled levy rate to within 5% (or
   £0.10/MWh where the rate is small), in at least 90% of quarters.
3. **A3.** Net payments are negative in at least four quarters between Q4 2021 and Q1 2023.
4. **B1.** Outside the crisis (2016 to Q2 2021, and 2023 to Q2 2025), the world-price levy is within
   ±15% of the actual levy, year by year. The sign of the error is open. The system sell price runs
   noisier than day-ahead, but a daily mean averages most of that away.
5. **B2.** In 2022 the world-price net payment has the right sign (negative), but its size is off by
   more than £150m, because the system price is not the day-ahead price at crisis levels.
6. **C1.** Leg C sits further from the actual levy than Leg B, in mean absolute quarterly error, in
   both non-crisis spans. Generation-weighting matters: wind and solar earn below the period mean.

**Refutation.** If A1 or A2 fails, the definition is wrong, and Legs B and C mean nothing until it is
fixed. If B1 fails by more than double its band, the world's price cannot serve as the CfD reference,
even on the record. An endogenous levy would then need a day-ahead price the world does not have.
