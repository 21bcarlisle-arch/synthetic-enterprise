# UK Domestic & SME Energy SVT Rates and Active/Passive Renewal Split 2016–2025

Research completed: 2026-06-22. Source: R&D agent, web-sourced from Ofgem, DESNZ, HoC Library.

---

## 1. SVT Unit Rates by Year

### Pre-Cap Period: 2016–2018 (supplier discretion)

| Year | Electricity SVT (p/kWh) | Gas SVT (p/kWh) | Annual Dual-Fuel Bill | Confidence |
|------|------------------------|-----------------|----------------------|------------|
| 2016 | ~13.5–14.5 | ~3.8–4.2 | ~£1,000–£1,100 | M |
| 2017 | ~13.5–14.5 | ~2.1–3.5 (Q4 low: 2.07p) | ~£1,050–£1,150 | M |
| 2018 | ~14.5–16.0 | ~3.5–4.0 | ~£1,100–£1,200 | M |

Rates back-derived from BEIS QEP bills + Ofgem SVT league tables; treat as ±15%. Gas fell to 2.07p/kWh Q4 2017 then recovered.

### Post-Cap Period: 2019–2025 (Ofgem Default Tariff Cap)

| Period | Electricity (p/kWh) | Gas (p/kWh) | Annual Typical Bill | Confidence |
|--------|--------------------|-----------|--------------------|------------|
| Jan 2019 | 16.52 | 3.73 | £1,137 | H |
| Apr 2019 | 18.56 | 4.14 | £1,254 | H |
| Oct 2019 | 17.85 | 3.68 | £1,179 | H |
| Apr 2020 | 17.81 | 3.50 | £1,126 | H |
| Oct 2020 | 17.19 | 3.00 | £1,042 | H |
| Apr 2021 | 18.95 | 3.34 | £1,138 | H |
| Oct 2021 | 20.80 | 4.07 | £1,277 | H |
| Apr 2022 | 28.34 | 7.37 | £1,971 | H |
| Oct 2022 | 51.89 | 14.76 | £3,549 (EPG capped consumer bills at £2,500) | H |
| Jan 2023 | ~67+ | ~17+ | £4,279 cap ceiling; EPG applied | H |
| Jul 2023 | 30.1 | 7.5 | £2,074 | H |
| Oct 2023 | 27.4 | 6.9 | £1,923 | H |
| Apr 2024 | 24.50 | 6.04 | £1,690 | H |
| Jul 2024 | 22.36 | 5.48 | — | H |
| Oct 2024 | 24.50 | 6.24 | — | H |
| Jan 2025 | 24.86 | 6.34 | — | H |
| Apr 2025 | 27.03 | 6.99 | £1,849 | H |
| Jul 2025 | 25.73 | 6.33 | £1,720 | H |
| Oct 2025 | 26.35 | 6.29 | £1,755 | H |

Source: electricityprices.org.uk, Ofgem cap press releases, cross-checked Energy Helpline.

---

## 2. Active/Passive Renewal Split

**Steady-state pre-crisis (~2016–2020):** ~35% actively renew to a new fixed deal; ~65% roll to SVT by default.

- **CMA 2016**: 70%+ Big Six domestic customers on SVT — had never switched or rolled back after fix expired. (H)
- **Ofgem Sep 2017**: ~57% of non-PPM accounts at 10 largest suppliers on SVT; declined only 2pp despite record switching. (H)
- **Ofgem Consumer Engagement Survey 2018**: 29% on SVT 3+ years; 23% on SVT under 3 years; 60%+ switched once or never. (H)
- **Ofgem Consumer Engagement Survey 2019**: 49% never switched or switched once (down from 61% prior year). (H)

The "35/65" framing is inferred from the inverse of the 57–65% SVT share; no Ofgem document states it explicitly in those terms. (M)

### Switching volumes (electricity accounts, annual):
- 2016: ~4.82 million
- 2017: ~3.84 million (market cooling)
- 2018: ~5.54 million
- 2019: ~5.88 million (peak pre-crisis)
- 2020: ~6.39 million
- 2021: ~5.06 million (collapsed H2)
- 2022: near zero (fixed deals withdrawn)

Source: Energy UK / DESNZ quarterly switching statistics.

---

## 3. Crisis Period: 2021–2022

Active renewal **effectively collapsed**. Suppliers withdrew fixed tariffs — wholesale costs exceeded the Ofgem price cap ceiling so no viable fixed product could be offered.

- 29 energy suppliers failed Jul 2021–May 2022, displacing ~4 million customers into SoLR. All placed on SVT.
- By Apr 2023: ~29 million customers on SVT (~90%), ~3 million on fixed (~10%) — complete inversion of normal structure.
- Customers did not voluntarily churn: no competitive fixed alternatives existed. SVT was de facto the "safe" tariff under EPG protection.
- Some fixed-deal customers paid more than SVT customers (pre-EPG expensive fixes had no subsidy).

Post-2023 recovery: ~one-third of customers on fixed deals by Jul 2025 (Ofgem State of the Market, Jan 2026). Closely matches pre-crisis 35% engaged proportion. (H)

---

## 4. SVT Churn Rates (Structural Inference)

Direct published SVT vs fixed churn rates by tariff type are not available; these are structural inferences:

| Customer type | Estimated annual churn | Basis |
|---|---|---|
| SVT long-stayer (3+ years) | ~5–10% | Ofgem engagement surveys: most inert segment |
| SVT recent (under 3 years) | ~15–20% | Switched once before; some re-engagement |
| Fixed at expiry → active switch | ~35% | Inverse of SVT rollover share at expiry |
| Fixed at expiry → roll to SVT | ~65% | Standard retention assumption |
| All customers (industry avg) | ~20–22% | DESNZ: ~6M switches / ~28M accounts (2019–20) |

Confidence: M on all SVT-specific rates (structural inference, not directly cited).

---

## 5. Price Cap / SVT Regulatory Mechanics

- Cap applies to SVT and deemed/default tariffs (Domestic Gas and Electricity (Tariff Cap) Act 2018, in force Jan 2019).
- Hard ceiling per kWh + standing charge. Suppliers cannot charge above it; may charge below.
- 14 DNO regions have slightly different cap levels.
- Fixed tariffs not capped by the default tariff cap (though Acquisition Tariff Ban Apr–Oct 2022 temporarily prohibited cheaper new-customer deals).
- In normal conditions, cap sits £200–£350 above cheapest available fix, providing strong incentive to switch.

---

## 6. Simulation Implications

### SVT rollover modelling (Phase 33 candidate)
The 65% SVT rollover share means a realistic renewal model should distinguish:
- **Active renewal**: customer proactively picks a new fixed deal — full churn model applies at term end
- **Passive renewal**: customer rolls to SVT automatically — churn probability near zero at that moment, but elevated SVT inertia churn applies ongoing (~10%/year)

In the current model all renewals are treated as fixed → fixed. This over-estimates churn-model engagement and under-estimates sticky SVT rollover. The crisis years (2022) had no fixed deals to roll into, so all rollover was effectively SVT-forced. Phase 33 could introduce an `is_active_renewal` flag and segment churn behaviour accordingly.

### Unit rate calibration
Pre-cap electricity rates (2016–2018): ~14p/kWh at SVT; cheapest fixes ~10–11p/kWh.
The simulation's tariff engine prices off forward curve — if the forward curve is calibrated to wholesale, the tariff should sit above it by the full cost stack (policy + network + margin + working capital). The SVT rates above can be used to sanity-check that simulated unit rates are in the right range.

### Crisis period
2022 oct–jan 2023: SVT capped at ~52–67p/kWh electricity (EPG limited consumer bills). Fixed deals essentially unavailable. The simulation's renewals engine should not be generating new fixed-price contracts in this period with unit rates far below the cap.

---

## Sources

- Ofgem standard variable tariff indicators (historical updates)
- Ofgem SVT latest trends Sep 2017 report
- Ofgem energy price cap / default tariff level history
- electricityprices.org.uk history of the energy price cap
- DESNZ quarterly domestic energy switching statistics
- Ofgem Consumer Engagement Survey 2018, 2019
- Ofgem State of the Market, January 2026
- HoC Library: Gas and electricity prices during the energy crisis (CBP-9714)
- HoC Library: Domestic energy prices (CBP-9491)
- BEIS Quarterly Energy Prices (QEP) collection
- Ofgem retail market indicators data portal
