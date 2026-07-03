# UK Household Energy Churn vs. Savings Elasticity 2015-2025

Research completed: 2026-07-03. Source: discovery agent, Ofgem/DESNZ/HoC Library.

## 1. Annual Switching Rates vs. Savings Available

Year, Switches, Rate, Savings, Notes:
2015: 4.2m, 15%, 250-300 GBP -- Moderate competition
2016: 4.82m, 17.5%, 250-350 GBP -- Peak challenger era
2017: 3.84m, 14%, 150-250 GBP -- Market consolidation
2018: 5.54m, 20%, 150-250 GBP -- Pre-cap surge
2019: 5.88m, 21%, 150-200 GBP -- Cap live Jan 2019; media coverage boosted engagement
2020: 6.39m, 23%, 100-150 GBP -- COVID: bill scrutiny; PCW usage peak
2021: 5.06m, 18% (H2 near zero), H1~0 H2 negative -- Suppliers withdrew products H2
2022: 0.8-1.2m, 3-4%, strongly negative -- No viable alternative below SVT
2023: 2.5-3.5m, 9-12%, 50-150 GBP -- Recovery; fairer pricing rule in force
2024: 3.5-4.5m, 13-16%, 100-200 GBP -- New normal post-ban equilibrium
2025: 4.0-5.0m, 15-18%, 100-250 GBP -- Continued normalisation

Sources: DESNZ Quarterly Energy Prices Table 2.1; Energy UK switching stats; Ofgem SotM Jan 2026.

## 2. Crisis Period: The Counterintuitive Collapse

During 2022 bills hit 3,549 GBP/yr (cap) / 2,500 GBP (EPG). Switching collapsed to 3-4%.

Mechanism:
- Wholesale cost for 12-month fix exceeded cap by 500-1,000 GBP/yr
- Fixed deals withdrawn or priced 1,000+ GBP above SVT equivalent
- SVT protected by cap AND Energy Price Guarantee = de facto cheapest tariff
- Some pre-crisis fixed-deal customers paid MORE than SVT customers

CRITICAL FINDING: Rising absolute prices did NOT increase switching propensity.
2022 empirically disconfirms the price-momentum-drives-switching hypothesis.
PRIMARY driver is SAVINGS AVAILABLE (competitor rate vs. current tariff).

## 3. Key Regulatory Events

Date, Event, Effect:
Jan 2019: Default Tariff Cap -- Compressed savings but switching continued (~21%)
Apr 2022: Acquisition Tariff Ban -- No practical effect; market already frozen
Oct 2022: Energy Price Guarantee -- Deepened SVT advantage
~2023: Fairer for existing customers -- PERMANENT: eliminates new-customer exclusives; reduces structural switching ~25-30%

## 4. Savings Elasticity Model (piecewise linear, DESNZ calibrated)

  savings < 0:         3%  (crisis floor; only home movers / SoLR)
  0 <= S < 100:        5% + 2% * (S / 100)
  100 <= S < 250:      7% + 6% * ((S - 100) / 150)
  250 <= S < 400:      13% + 5% * ((S - 250) / 150)
  S >= 400:            22% (saturation)

Post-2023 structural suppression: 0.75x (fairer pricing rule).
Calibration: savings_rate(150) * 0.75 = 9% * 0.75 = 6.75% -- normalised to multiplier 1.0 at 2024.

## 5. SIM Calibration

Year | Savings (GBP) | Post-ban factor | Market multiplier
2016 | 300  | 1.00 | ~2.2
2017 | 200  | 1.00 | ~1.5
2018 | 200  | 1.00 | ~1.5
2019 | 175  | 1.00 | ~1.4
2020 | 125  | 1.00 | ~1.0
2021 |   0  | 1.00 | ~0.7
2022 | -200 | 1.00 | ~0.4
2023 | 100  | 0.85 | ~0.85
2024 | 150  | 0.75 | 1.00
2025 | 175  | 0.75 | ~1.1

NOTE: Do NOT add price-momentum uplift -- 2022 disconfirms that hypothesis.
