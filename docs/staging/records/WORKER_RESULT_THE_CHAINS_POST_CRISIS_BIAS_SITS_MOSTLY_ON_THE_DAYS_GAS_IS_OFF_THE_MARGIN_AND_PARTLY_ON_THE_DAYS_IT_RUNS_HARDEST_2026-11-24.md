**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the chain's post-crisis bias sits mostly on the days gas is off the margin, and partly on the days it runs hardest (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in `88c69e12a` and landed on origin before the probe ran:
`docs/staging/records/WORKER_PREREG_DOES_THE_CHAINS_POST_CRISIS_BIAS_SIT_ON_THE_DAYS_GAS_IS_OFF_THE_MARGIN_2026-11-24.md`.
The probe is `/var/tmp/mk24/measure.py` (sha256 `9e920ab7…dedd1a9`, unchanged between filing and run), run
in a worktree at origin `11778a0621`. Its output is `/var/tmp/mk24/out.json`. **Nothing in `sim/` changes.***

The definitions are the pre-registration's. Residual is the chain's daily price minus the real daily SSP, on
arm X. The band is the quintile of that day's mean real CCGT output, within each year. The floor is
(SAP + carbon × EF) ÷ 0.50. All 3,337 record days carry a CCGT figure.

## Predictions and outcomes

| # | Filed | Outcome | Held? |
|---|---|---|---|
| C1 | control reproduces X: 4.89 / 17.02 / 10.38, post bias +8.23 | 4.89 / 17.02 / 10.38, +8.23 | **held** |
| C2 | post: Q1 ≥ +12, Q5 ≤ +6, Q1 − Q5 ≥ 8 | Q1 +25.19, Q5 **+9.74**, Q1 − Q5 = 15.45 | **missed** on the Q5 leg |
| C3 | post: residual falls Q1 → Q5, at most one inversion | +25.2, +2.6, +2.8, +1.8, +9.7: a U | **missed** |
| C4 | pre: \|Q1 − Q5\| ≤ 6 | +1.17 against −0.89, 2.06 | **held** |
| C5 | post: record's Q1 gap to floor ≤ −20, Q5 ≥ 0 | −31.23, +13.10 | **held** |
| C6 | post: Q1 + Q2 > 60% of summed residual | 67.5% | **held** |
| C7 | Q1 is the largest band in 2023 H2, 2024 and 2025 H1 | +25.9, +23.5, +28.1, largest in each | **held** |

Five of seven held. The two misses are one fact: the chain also overprices the highest-CCGT days after the
crisis. The prediction expected those days to be close to right.

## The numbers

Mean daily residual (chain − SSP) by CCGT band, low → high, with mean CCGT GW. The record's gap to the floor and
the chain's gap to the floor are shown beside it, £/MWh:

| Regime | | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|---|
| pre | CCGT GW | 8.0 | 10.8 | 12.8 | 15.0 | 18.1 |
| | chain − SSP | +1.2 | −0.8 | −1.3 | −2.5 | −0.9 |
| | SSP − floor | −1.2 | +2.0 | +4.2 | +7.7 | +12.5 |
| | chain − floor | −0.1 | +1.2 | +2.8 | +5.2 | +11.6 |
| crisis | CCGT GW | 5.9 | 9.3 | 12.1 | 14.3 | 17.8 |
| | chain − SSP | +12.1 | +2.2 | −1.4 | −17.7 | +2.2 |
| | SSP − floor | −14.4 | +3.1 | +12.5 | +34.4 | +46.5 |
| | chain − floor | −2.3 | +5.3 | +11.1 | +16.7 | +48.8 |
| post | CCGT GW | 3.7 | 5.7 | 8.3 | 11.0 | 16.3 |
| | chain − SSP | **+25.2** | +2.6 | +2.8 | +1.8 | **+9.7** |
| | SSP − floor | −31.2 | −7.1 | −1.3 | +2.8 | +13.1 |
| | chain − floor | −6.0 | −4.5 | +1.5 | +4.6 | +22.8 |

Post-crisis by year, chain − SSP, Q1 → Q5: 2023 H2 +25.9 / +3.7 / +2.8 / −3.3 / +9.3; 2024 +23.5 / +2.1 /
+0.8 / −0.4 / +10.9; 2025 H1 +28.1 / +2.7 / +7.4 / +12.6 / +7.5.

## What it says

1. **Before the crisis, the chain gets the shape right band by band.** In every band the chain's gap to its
   floor is within £2.5 of the record's. The no-intercept multiple of gas was a good description of 2016-21.
2. **After it, most of the bias is on the days gas is off the margin.** Q1 alone accounts for about £5.3 of the
   £8.64 mean daily residual (+25.19 × 149 of 708 days). On those days the record clears £31 below the floor,
   and the chain clears £6 below it. The chain's lowest band sits only £6 under its floor because its discount is
   a fixed fraction (a0 ≈ 0.52 plus a1·x) of a floor that roughly doubled. The record's depth below gas grew
   with the floor, and the chain's did not grow enough. This is the mechanism §1a of the electricity page names.
3. **About £1.9 of it is on the days gas runs hardest.** In Q5 the chain clears £22.8 above its floor, and the
   record clears £13.1 above it. Before the crisis the two agreed (+11.6 against +12.5). After it, the
   record's premium above SRMC is a smaller fraction of a larger floor. The chain's a1·x and scarcity terms scale
   with the floor, so they overstate that premium. This miss was not predicted. It is the steer's third gap,
   crisis mis-scaling at high gas, now seen after the crisis as well.
   **Corrected 24 Nov, beside the claim** (electricity page §1b): on fixed CCGT-GW bins the record's price
   is the same multiple of the floor in all three regimes, and in the crisis, at the highest floor, the top
   held its pre-crisis ratio (1.25-1.28 at 16-20 GW). So "a smaller fraction of a larger floor" is wrong as a
   rule. Within-year quintiles moved down the CCGT axis after the crisis (post Q5 is 16.3 GW), and that, not
   the floor's level, is what the quintile table showed. The chain's Q5 overprice is real (1.20-1.28 against
   1.06-1.09 at 14-18 GW, 66 days), but it is not attributed.
4. **The crisis bias of −1.5 is a cancellation, not a fit.** Q1 is +12.1 and Q4 is −17.7. A small regime bias here
   says nothing about whether the chain prices the crisis well. Quote the bands beside it.
5. **Both misses point the same way.** The chain's spread across CCGT bands after the crisis is −6 to +23,
   which is 29. The record's is −31 to +13, which is 44, and it sits lower. One multiplier that scales the whole
   leg with the floor cannot produce a deeper bottom and a flatter top at the same time.

## What this does NOT establish

- CCGT output is a proxy for "gas is marginal" (page GAP 4), and a daily mean blurs it. The Q1 depth here (−31)
  is shallower than the half-hourly −37 to −42, as filed.
- Nothing here says which term should carry the depth. It might be an intercept that scales with the floor, a
  low-x shape, or a price set by imports on a cross-border spread (GAP 2). The arm below decides between them on
  the record.
- 2025 is January to June only, so it is winter-heavy. Its Q4 (+12.6) is the one band-year that breaks the
  pattern, and it is not attributed.

## Decision

**The filed rule does not fire (a) as written.** (a) required C2 to hold, and C2 missed on its Q5 leg. (b) and (c)
do not fire either: Q1 − Q5 is 15.45, not under 4, and the residual is largest in Q1, not Q5. So under the
rule this is "reported as it falls, and no build follows from it". **Nothing ships.**

**Superseded 24 Nov, beside it** (§1b): the next arm separates the price leg from the gas-running leg before
any shape is built; a shape arm would refit a leg the record says already has the right form.

The steer orders the rebuild by the largest gap, and that is Q1. **The next arm** therefore follows (a)'s path,
widened by what the miss found. First, a K8 note on what sets the price when gas is not marginal: wind and
nuclear offers, CfD negative bidding, and imports. Then a price-leg shape with a low-x depth scaling with the
floor AND a top that is allowed to flatten. It is refit on the same window, and its prediction is filed and
landed first, bands and regimes both. It must hold the pre-crisis band fit (point 1) as a control.

Reverse: delete this record.
