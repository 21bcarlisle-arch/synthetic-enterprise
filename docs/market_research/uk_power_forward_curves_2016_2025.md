# UK Power & Gas Forward Curve Structure (2016–2025)

Research for Phase 41a forward curve reform. Underpins `sim/forward_curve.py`
model assumptions. All figures from public sources (Ofgem, BEIS Energy Trends,
ICE Endex settlement prices, NESO BMRS).

---

## 1. Market structure

**UK electricity forward market:**
- Traded on ICE Endex (N2EX) and EEX/Epex SPOT
- Products: Day-Ahead (DA), Weekend, Week-Ahead, Month-Ahead (MA),
  Quarter-Ahead (QA), Season (Summer Apr–Sep / Winter Oct–Mar), Year-Ahead
- Baseload (all 24 h) and Peakload (Mon–Fri 07:00–23:00) products
- Liquidity thins rapidly beyond 2 years; 1-year baseload is the supplier
  benchmark for residential and SME annual fixed tariffs

**UK gas forward market:**
- NBP (National Balancing Point) on ICE, products from DA to 2 years ahead
- Closely linked to TTF (Dutch hub) and LNG landed prices since 2020
- Storage draw-down in Q4/Q1 → winter premium; injection season Q2/Q3 → discount

---

## 2. Contango vs backwardation — historical patterns

### Pre-crisis (2016–2020): mild contango

| Year | DA mean (£/MWh) | Year+1 forward (£/MWh) | Premium |
|------|----------------|------------------------|---------|
| 2016 | ~45            | ~50                    | +11%    |
| 2017 | ~50            | ~55                    | +10%    |
| 2018 | ~60            | ~65                    | +8%     |
| 2019 | ~47            | ~51                    | +9%     |
| 2020 | ~37            | ~44                    | +19%    |

Mild contango driven by:
- Cost of carry (collateral on forward positions)
- Liquidity premium (Year+1 book is thin; wide bid-offer)
- Demand uncertainty premium (supplier's supply obligation)

**Range: 8–19% above near-term spot for 1-year baseload**

### Crisis onset (2021): contango → super-contango

In H1 2021, gas storage in Europe was low. Forwards ran ahead of spot:
- Q2 2021 spot: ~£65/MWh; Year+1 forward: ~£85/MWh (+31%)
- Market expected continued tightness → contango steepening

### Crisis peak (late 2021 – 2022): backwardation

Once DA prices spiked (Oct 2021: £400+/MWh):
- Year+1 forwards settled ~£250–300/MWh (market expected reversion)
- Spot > Year+1 → backwardation
- This is the critical period where a lookback-SMA model **catastrophically
  under-performs**: a 90-day lookback would include the spike and price
  tariffs at £300+/MWh, whereas the real market was offering Year+1 at £250
  (already discounting reversion)

### Post-crisis (2023–2025): gradual return to contango

- Prices fall from crisis highs; normal risk-premium structure reasserts
- 2024: DA ~£80/MWh; Year+1 ~£90/MWh (+12.5%)

---

## 3. Seasonal shape

UK electricity exhibits a consistent seasonal forward premium:

| Period | Typical multiplier vs annual flat |
|--------|----------------------------------|
| Q1 (Jan–Mar) | +10–15% |
| Q2 (Apr–Jun) | −6–10% |
| Q3 (Jul–Sep) | −8–12% |
| Q4 (Oct–Dec) | +5–10% |

Monthly granularity (annual baseload = 1.000):
- Dec/Jan: peak (+12%)
- Jul: trough (−12%)
- Mar/Sep: shoulder months (~+8% / −5%)

Gas seasonal spread is more pronounced than electricity (heating demand
dominates, storage draw-down risk):
- Q1 gas: +15–20% vs annual flat
- Q3 gas: −8–15% vs annual flat

**Calibrated monthly multipliers (electricity) used in model:**
```
Jan: 1.12  Feb: 1.12  Mar: 1.08
Apr: 0.95  May: 0.92  Jun: 0.88
Jul: 0.88  Aug: 0.90  Sep: 0.95
Oct: 1.02  Nov: 1.08  Dec: 1.12
Annual mean: 1.002 (nearly flat for 12-month contracts)
```

---

## 4. Term structure of uncertainty

Forward price uncertainty grows with tenor, following approximately a square-root
of time law (consistent with random-walk price dynamics subject to mean reversion):

| Tenor | Annualised forward vol (normal mkt) | Risk premium (vs near-term spot) |
|-------|-------------------------------------|----------------------------------|
| Month-Ahead | ~12% | 1–3% |
| Quarter-Ahead | ~15% | 3–5% |
| Year-Ahead | ~18–25% | 6–10% |
| 2-Year | ~22–30% | 8–14% |

**Calibration: BASE_TERM_PREMIUM = 0.06 (electricity)**
- For 1-year contract (tenor_years=1): 6% × sqrt(1) = 6%
- For 6-month contract (tenor_years=0.5): 6% × sqrt(0.5) ≈ 4.2%
- For 2-year contract: 6% × sqrt(2) ≈ 8.5%

Sensitivity to risk_factor parameter: risk_factor / 1.2 scales the premium
(risk_factor=1.2 is calibrated to the 6% baseline above).

---

## 5. EWMA vs SMA for spot expectation

The old model used a simple 90-day arithmetic mean. Problems:
1. **Crisis lag**: 90-day mean during a spike includes 60+ days of pre-spike
   prices, dramatically under-estimating the market forward level
2. **Mean reversion blindness**: during backwardation, the SMA overestimates
   by including the spike in the average

**Chosen approach: 30-day EWMA half-life**
- More weight on recent data → faster adaptation to new regimes
- Still backward-looking (PIT safe)
- During a spike: weights ~75% of the signal from the last 30 days
- Caveat: EWMA still doesn't model backwardation explicitly. During the
  2021-22 crisis, the model will over-estimate forward prices vs the real
  Year+1 market (which priced in reversion). This is noted as a known
  limitation and a candidate for Phase 42+ work (real-curve calibration).

---

## 6. Model limitations and future work

1. **No mean reversion**: the model treats spot_ewma as the unbiased forward
   expectation. In practice, mean-reverting processes (power is strongly
   mean-reverting on 6-12 month horizon) imply forward prices revert toward
   fundamental cost, not follow spot linearly. The EWMA partially addresses
   this but doesn't explicitly model reversion speed.

2. **Crisis backwardation not captured**: When spot spikes, real Year+1
   forwards price in reversion and are BELOW spot. Our model would produce
   contango (forward > spot) regardless. This is the key improvement for a
   future phase — calibrate to real ICE/N2EX forward settlement data.

3. **No tenor-specific term structure**: we model tenor as a single
   sqrt(years) scaling. Real markets have a humped term structure (near
   months thin, far months illiquid) with its own shape.

4. **Gas curve not modelled in sim/forward_curve.py**: Gas forward prices are
   handled by the company's tariff engine and NBP history. The same term
   structure principles apply; the gas forward curve reform is Phase 42.

---

## 7. Sources

- Ofgem Wholesale market indicators (quarterly)
- BEIS Energy Trends, Table 3.1 (quarterly average prices)
- ICE Endex N2EX settlement data (public daily settlement prices)
- NESO BMRS system prices (half-hourly, used as simulation ground truth)
- Cornwall Insight: UK power market outlooks 2016–2024 (industry estimates)
- Statkraft/SSE/Centrica annual reports (forward hedging disclosures)
