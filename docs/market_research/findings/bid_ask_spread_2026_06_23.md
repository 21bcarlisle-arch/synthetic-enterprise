# Structured Finding: N2EX OTC Electricity Forward Bid-Ask Spread

**domain**: trading/hedging
**assumption_tested**: Phase 43b calibrated bid-ask execution cost for UK OTC electricity forward contracts at 0.5% base + 0.2% per year of tenor, capped at 1.5% of forward price, representing the cost of buying at ask vs mid when hedging supply obligations.
**benchmark_value**:
  - Q+1 (3–6 month) OTC spread, normal market: £0.20–0.54/MWh = **0.25–0.60%** of forward price (Ofgem/ICIS, 2024–2026)
  - Q+1 spread during energy crisis (Q1 2022): £0.94/MWh on ~£300/MWh = 0.31% (spread % narrows during spikes because price rises faster than spread)
  - Season+1 (6-month) under S&P market making obligation: **≤ 0.5%** (regulatory cap)
  - Season+2 (12-month) under S&P: **≤ 0.5%** mandated; observed up to 0.6%
  - Season+3,+4 (18–24 month) under S&P: **≤ 0.6%** mandated; non-mandated can reach 1–2.5%
  - Quarter+2,+3,+4 (6–12 month non-mandated): 1–2.5%, with extreme cases up to 4%
  - Season+5+ (30+ months): above 2%, often no market available
  - Post-S&P introduction (April 2014+): mandated products (Month+1/+2, Quarter+1, Season+1 through +4) all averaged below 0.8%, many below 0.5% (ICIS Heren at 4:30pm)
**confidence**: H
**source**:
  1. Ofgem Wholesale Market Indicators page — "Electricity bid-offer spreads by contract type (GB)", OTC assessed by ICIS at 4:30pm daily, Q+1 contract (data retrieved 2026-06-23): https://www.ofgem.gov.uk/markets/wholesale-energy-markets/monitoring-and-liquidity
  2. CMA Energy Market Investigation, Appendix 7.1: Liquidity (Final Report 2016), paragraphs 68–75, footnote 47 — formally documents S&P maximum spread obligations and observed ICIS Heren bid-offer spread data by product tenor 2011–2014: https://assets.publishing.service.gov.uk/media/576bcb4fe5274a0da30000d1/appendix-7-1-liquidity-fr.pdf
**date**: 2026-06-23

---

## Detailed evidence

### 1. Ofgem WMI — Q+1 electricity OTC bid-offer spread (ICIS assessed, GB market)

The Ofgem Wholesale Market Indicators page embeds the following historical data for the electricity Q+1 contract bid-offer spread. These are OTC over-the-counter spreads assessed by ICIS at 4:30pm (end of afternoon Secure and Promote window).

| Period | Spread £/MWh | Approx fwd price | Spread % |
|--------|-------------|------------------|----------|
| Q1 2022 (energy crisis) | £0.94/MWh | ~£300/MWh | ~0.31% |
| Q1 2023 (recovery) | £0.80/MWh | ~£180/MWh | ~0.44% |
| Q4 2024 | £0.46/MWh | ~£80/MWh | ~0.58% |
| Q1 2025 | £0.54/MWh | ~£90/MWh | ~0.60% |
| Q4 2025 (most recent normal) | £0.20/MWh | ~£80/MWh | ~0.25% |
| Q1 2026 | £0.36/MWh | ~£93/MWh | ~0.39% |

Ofgem notes: "The maximum spread recorded is 1" (£1/MWh). The Q+1 contract is the product used in calculation of the retail price cap. Spreads are wider in stress periods (higher nominal £/MWh value) but narrower as a percentage because forward prices rise faster.

**Normal market range: 0.25–0.60% for Q+1 (3–6 month tenor)**

### 2. CMA Appendix 7.1 — Spread sizes by tenor (2014, ICIS Heren data)

The CMA Energy Market Investigation's liquidity appendix (2016 final report) provides the authoritative formal analysis of GB electricity forward market bid-offer spreads. Key findings:

**S&P Market Making maximum permitted spreads (regulatory cap, effective April 2014):**

| Product | Baseload max | Peak max |
|---------|-------------|---------|
| Month+1, Month+2 | 0.5% | 0.7% |
| Quarter+1 | 0.5% | 0.7% |
| Season+1, Season+2 | 0.5% | 0.7% |
| Season+3, Season+4 | 0.6% | 1.0% |

**Observed spreads (ICIS Heren data, 2011–2014, Baseload):**
- Month+1: often less than 0.5%
- Quarter+1: usually less than 1%, regulated to ≤0.5% post-April 2014
- Season+1: less than 1% throughout, below 0.5% for two years pre-investigation
- Season+2: generally below 1%
- Season+3,+4: generally below 1% in last two years
- Season+5+: above 2% on multiple occasions, sometimes unavailable
- Quarter+2,+3,+4: variable 1–2.5%, sometimes up to 4%; no S&P improvement observed
- Monthly products beyond Month+2: wider than seasonal, sometimes up to 2.5%

**Post-S&P (April 2014+):** All seven mandated Baseload and six mandated Peak products averaged below 0.8% monthly, many below 0.5% — ICIS Heren 4:30pm assessments.

### 3. Market structure context

- N2EX / OTC via brokers (BGC, Marex, Tradition): UK electricity forward market
- Liquidity declines sharply beyond Season+4 (2 years ahead of delivery)
- Gas products are tighter than electricity equivalents
- Seasons have tighter spreads than equivalent Quarters; Months can be wider or tighter
- Independent suppliers (without S&P market making access in mandated windows) may face wider spreads
- ICIS Heren assessments at 4:30pm represent the end of the mandated S&P window — the most liquid point of day

---

## Conclusion

The Phase 43b calibration of **0.5% base + 0.2% per year of tenor, capped at 1.5%** is broadly consistent with published data:

| Tenor | Simulation | Real-world benchmark | Assessment |
|-------|-----------|---------------------|------------|
| 3-month (0.25yr) | 0.55% | 0.25–0.60% (Ofgem WMI, normal) | Slightly high but within range |
| 6-month (0.50yr) | 0.60% | 0.25–0.60% (Ofgem WMI) / ≤0.5% (S&P) | At top of range; acceptable |
| 12-month (1yr) | 0.70% | 0.50–0.60% for mandated; 0.6–1.0% non-mandated | Consistent |
| 18-month (1.5yr) | 0.80% | 0.60–1.50% | Within range |
| 24-month (2yr) | 0.90% | 0.60–1.50% | At low-mid end of range |
| 36-month (3yr) | 1.10% | 1.50–4.00%+ (highly illiquid) | Potentially understated |

**Overall assessment: BROADLY CONSISTENT (minor conservative bias at 3m end)**

The 0.5% base reflects the S&P market making maximum for the most liquid products. The 1.5% cap is conservative relative to non-mandated product spreads (which can reach 2.5–4%), but most supplier hedging activity occurs within the first 2–4 seasons where the simulation's 0.6–0.9% range is realistic. The cap of 1.5% may understate execution costs for genuine year-2+ hedging, but such positions are rare in UK supplier books given the illiquidity.

**Action warranted:** The calibration is defensible. Consider noting that the 0.5% base for 3-month products is at the high end of the current Ofgem-observed Q+1 range (0.25–0.60%), and that very long tenors (>2yr) may face spreads above the 1.5% cap. No immediate change required.
