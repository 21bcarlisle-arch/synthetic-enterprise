**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: GB power sat below gas SRMC after the crisis because gas was off the margin more often, and half the gap was the carbon proxy (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is the question the efficiency arm (`3725d0e6b2`) left open: why did the traded price (MID) sit about
£9.80 below gas-plus-carbon SRMC in 2023-25? **Knowledge (K8):** §1a of
`docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md`, written with this record.
**Nothing in `sim/` changes.***

**How the predictions were filed.** They were written to `/var/tmp/srmc_gap/PREDICTIONS.md` at
11:48:15 UTC, with sha256 `671f8cad…15cb16`, before the probe first ran. They were not landed on origin
first, as the earlier arms' were, so the hash and the timestamp are the only proof. The predictions are
copied below as filed. P4 was muddled when filed and is kept that way.

## Definitions, before any number

- **Gap** = MID − SRMC for one half-hour. SRMC = daily SAP ÷ eff + (CPS + UKA) × 0.1829 ÷ eff, with eff from
  DUKES 5.10.C by year (2025 held at 2024, a GAP). Carbon is
  `merit_order_reconstruction.carbon_price_in_month_gbp_per_tonne`, which is the UKA auction VWAP by month.
- **CCGT band** = that half-hour's FUELHH CCGT output, in quintiles within each year. High CCGT output is
  the observable proxy for "gas is the marginal plant". Low output means wind, nuclear and imports cover
  most of residual demand, so something cheaper than gas is more likely to set the price. This is a proxy.
  No marginal-unit series is held (page GAP 4).
- Window: 2018-01-01 (SAP starts) to 2025-06-07 (the MID files' end). 2025 covers only January to June,
  so it is winter-heavy.

## Predictions and outcomes

| # | Filed | Outcome | Held? |
|---|---|---|---|
| P1 | on auction carbon, the post-crisis median monthly gap (2023-07..2024-12) moves from −9.80 to between −8.5 and −5.5 | **−4.89**. The control on the proxy reproduces −9.81 | **missed**: the proxy carried half the gap, more than filed |
| P2 | top CCGT quintile gap > −4 in each post-crisis year; bottom quintile < −25 | top +22.6 / +13.6 / +24.4; bottom −41.5 / −36.7 / −39.4 (2023 / 24 / 25) | **held** |
| P3 | top quintile gap +2..+15 before the crisis (2018-20) | +11.9 / +11.2 / +13.4 | **held** |
| P4 | share of half-hours with CCGT < 5 GW rises monotonically 2023 → 2025 | 0.249 → 0.372 → 0.290 | **missed** (2025 is Jan-Jun only) |
| P5 | if the top quintile's gap is < −6 in 2024 or 2025, CCGT bidding below SRMC is live | +13.6, +24.4 | (c) **not supported** |
| P6 | in the middle CCGT tercile, above-median-import half-hours have a gap ≥ £3 more negative | +1.9 / +5.2 / +2.0 | **missed, wrong sign** |
| P7 | annual mean gap negative in each of 2023-25, largest in magnitude in 2025 | −1.37 / −7.79 / −5.12 | negative **held**; largest in 2025 **missed** (2024 is) |

## The numbers

Mean gap by CCGT-output quintile, £/MWh, low → high (mean CCGT GW in brackets), with the share of
half-hours under 5 GW:

| Year | Q1 | Q2 | Q3 | Q4 | Q5 | mean | < 5 GW |
|---|---|---|---|---|---|---|---|
| 2018 | −7.7 (6.2) | −0.4 | +3.9 | +6.1 | +11.9 (20.5) | +2.74 | 5.2% |
| 2019 | −6.4 (5.6) | −0.2 | +2.4 | +5.7 | +11.2 (20.9) | +2.54 | 7.2% |
| 2020 | −13.2 (4.5) | −1.3 | +2.4 | +5.0 | +13.4 (19.1) | +1.25 | 14.6% |
| 2021 | −22.5 (5.1) | −3.4 | +3.4 | +21.6 | +44.3 (19.5) | +8.67 | 9.2% |
| 2022 | −36.0 (4.4) | +1.5 | +16.2 | +48.1 | +63.0 (19.7) | +18.59 | 13.2% |
| 2023 | −41.5 (3.3) | −3.2 | +4.4 | +10.9 | +22.6 (18.1) | −1.37 | 24.9% |
| 2024 | −36.7 (2.7) | −17.6 | −1.9 | +3.7 | +13.6 (17.3) | −7.79 | 37.2% |
| 2025 H1 | −39.4 (2.8) | −12.8 | −1.0 | +3.2 | +24.4 (20.0) | −5.12 | 29.0% |

## What it says

1. **Half the "£9.80" was the measuring instrument.** The power grade used the civil-penalty carbon proxy,
   which averages futures traded the year before and so missed the UKA's 2023-24 fall. On the auction
   series the post-crisis median gap is −£4.89. **Correction, beside the efficiency record's claim** that the
   −£9.80 "matches the chain's +8.2 in sign and size": the chain already prices with auction carbon, so on a
   like-for-like basis the record's gap is about £5, not £10. That leaves a few pounds of the chain's +8.2
   unexplained by the record at all. I cannot yet say whether that part is in the chain's price leg or in its
   inputs. The same correction applies to the page's §10a line, which is amended beside it.
2. **When gas is plainly running hard, power clears above fleet SRMC, as before the crisis.** The top CCGT
   quintile sits £14-24 above fleet SRMC after the crisis, against £11-13 before it. That is the sign the
   page's §1 expects, because the marginal plant is less efficient than the fleet average. So CCGTs bidding
   below spot SRMC (candidate c) is not what the record shows where gas is marginal.
3. **The gap is a mixture, and what moved is the mix.** Half-hours with CCGT under 5 GW went from 5-7% of
   the year (2018-19) to 25-37% (2023-24). In those half-hours price sits £37-42 below gas SRMC. A
   time-averaged price, set against an SRMC, is a weighted average of two regimes. One is gas marginal,
   with price at or above SRMC. The other is wind, nuclear or imports marginal, with price far below it. As
   the second grows, the average falls below SRMC, even though no single plant bids below its cost. This is
   candidate (b). It is the same thing as the power grade's E8, where the gap falls as the wind share rises.
4. **The ~£40 depth of the low band is larger after the crisis than before (−£6 to −£13).** In £ terms the
   distance from SRMC to a renewable- or import-set price scales with the SRMC level. A £90 SRMC leaves more
   room under it than a £40 one. That is why the same share of non-gas hours costs more pounds after 2021.
   It is also why a reduced form fitted across both levels, with no intercept, will carry a level bias that
   grows with gas.
5. **Imports have no separate signal on this split (P6 wrong in sign).** At given CCGT output, high-import
   half-hours price slightly higher, not lower. Flow follows the spread: GB imports when its price is high
   (Ofgem). So imports are endogenous to price here, and a one-way split cannot separate "imports set the
   price". This candidate stays a GAP, and it needs the cross-border spread series (page GAP 2).

## What this does NOT establish

- CCGT output is a proxy for "gas is marginal", not a marginal-unit series. Published shares of hours with gas
  as the price-setter disagree by definition: 98% in 2024 (Electric Insights), about 85% in 2024 (ECIU), and
  60% "in 2026" against 90%+ in 2021 (Institute for Government explainer). They are counting different things,
  and none of them has been read in full here. Page GAP 4 remains open.
- Nothing here grades the chain. The arm that does is the chain's residual by CCGT band. Its question is
  whether the chain's +8.2 sits in the low-CCGT half-hours, the way the record's gap does.

## Decision

**Nothing ships.** The steer's three candidates are narrowed. (a) The carbon proxy was half the record's gap
and is already fixed in the chain. (b) Gas off the margin more often is what the record shows. (c) Below-SRMC
bidding is not supported where gas is marginal. Imports are not separable on this split. **Next under item
4:** the chain's own residual by CCGT band, with its prediction filed first. If the chain's post-crisis bias sits
in the low-CCGT band, the price leg needs a floor or shape below gas that scales with SRMC, rather than more
inputs.

## The probe

`/var/tmp/srmc_gap/probe.py` (read-only), run from the shared repo root with the worktree path as argv[1]
(origin `3725d0e6b2`). The output is `/var/tmp/srmc_gap/out.json`. The tables above are transcribed from that
output.
