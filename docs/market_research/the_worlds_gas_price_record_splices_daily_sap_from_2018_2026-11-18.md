# The world's gas price record: splicing GB daily SAP in from 2018-01-01

**Knowledge:** how-gb-gas-and-power-prices-move

K8 page for `world-gas-baseline-splice-daily-sap-from-2018` (delivery seat, 2026-11-18). It is written before the
world's baseline changes. The loader that makes the splice (`sim.gas_prices_history.load_gas_baseline_spliced`) has
landed, but no run reads it yet: DIRECTION.yaml `not_now` holds the switch until the skip pair (skip1, skip0) has
read, so the two arms of that comparison see the same world.

## What the world has now

`sim/gas_data/nbp_sap.csv` is FRED `PNGASEUUSDM`: the IMF monthly European gas price, which is the Dutch TTF hub.
It is converted at a fixed 1.28 $/£ and spread flat over each month's days, from 2015-10-01 to 2025-06-07. The
forward curve, the company's price view through `company/interfaces/sim_interface.py`, gas settlement and every
gas run read it through `load_nbp_history`. Provenance is in `sim/gas_prices_history.py:1-25`.

## What the published record is

- **GB System Average Price (SAP), actual gas day.** National Gas Transmission publishes it, and ONS republishes it
  under OGL v3 ("System Average Price (SAP) of gas", table 1, p/kWh, January 2018 onward). It is held at
  `sim/gas_data/sap_daily.csv`: 2,922 days, 2018-01-01 to 2025-12-31, with no gaps, at the edition pinned by
  sha256 in the loader. SAP is the volume-weighted average of the day's on-the-day commodity market trades. It
  is the GB price a supplier's imbalance and within-day trading actually faces.
- **NBP and TTF are different hubs.** The basis is normally small. In 2022 it was not: GB had LNG it could not
  export, and NBP traded at a $23.29/MMBtu discount to TTF on 15 Jul 2022 (S&P, cited in
  `how_gb_gas_and_power_prices_move_2026-10-25.md` §1).

## What the splice changes (measured 2026-11-18, same months 2018-01..2025-06)

| Year | Proxy £/MWh | SAP monthly mean £/MWh | SAP − proxy |
|---|---|---|---|
| 2018 | 21.10 | 20.79 | −1% |
| 2019 | 11.88 | 12.00 | +1% |
| 2020 | 8.47 | 8.55 | +1% |
| 2021 | 42.40 | 38.80 | −8% |
| 2022 | 100.02 | 71.00 | **−29%** |
| 2023 | 34.34 | 34.48 | 0% |
| 2024 | 29.03 | 28.65 | −1% |
| 2025 H1 | 35.00 | 34.49 | −1% |

The proxy's level is faithful except in the crisis. In 2022 it overstates the GB price by about £29/MWh on
average, and by £58/MWh in August. That is the TTF-NBP basis plus the fixed exchange rate (sterling fell in 2022,
so a fixed 1.28 also understates the £ price of a $ quote; the two partly offset). The before/after on the gas
forward and on daily volatility is in
`docs/staging/records/SEAT_RESULT_SPLICING_DAILY_SAP_INTO_THE_WORLDS_GAS_BASELINE_FROM_2018_2026-11-18.md`.

## Design choices, and why

1. **The seam is 2018-01-01**, the first day ONS publishes. Before it, the proxy stays: the 90-day lookback
   needs a record from 2015-10. The basis was ≤1% in 2018-20, so the step at the seam is the size of a normal
   day's move and not a level jump.
2. **The splice is clipped to the proxy's RECORD_END (2025-06-07)** so it changes the price source alone. SAP runs
   to 2025-12-31. Extending the world's gas record is a separate, one-variable step.
3. **A gap refuses.** A missing SAP day would silently shorten every lookback that touches it.
4. **No smoothing, no outlier removal.** The extreme days are real events: 1 Mar 2018 (the Beast from the East,
   £127/MWh), June 2022 (£4.30/MWh on 10 Jun, when within-day gas collapsed) and October 2022 (the LNG glut).
   Removing them would put a fitted world back in place of the record.

## GAP

- **SAP before 2018.** The NGT MIPI series (PUBOB603) goes back further, but it needs an OAuth login. No free,
  licensed pre-2018 daily GB series has been found, so 2015-10..2017-12 daily gas volatility stays ungradeable.
- **SAP against day-ahead NBP.** A supplier hedges forward and buys day-ahead, not at SAP. The two differ on
  stress days. No free day-ahead NBP daily series has been read.
- **Forward-curve calibration.** `sim.forward_curve`'s gas premium and seasonal table were fitted on the proxy.
  Whether they still hold on SAP has not been checked. It is named in the handoff, not assumed.
