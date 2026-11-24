**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: on the real GB gas price, the chain's one price leg cannot fit both the crisis and the years after it. The TTF proxy's 2022 premium was hiding that (2026-11-24)

*Autonomous worker, 24 Nov 2026. This is the gas-input arm of the weather-to-price steer, item 4. It is area map C2
(`docs/design/WORLD_POWER_PRICE_AREA_MAP_2026-11-24.md` s.3 and s.7). It was run on origin `6b5b42195e`, in a clean
worktree. **Knowledge:** `docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md` and the gas page
`docs/market_research/the_worlds_gas_price_record_splices_daily_sap_from_2018_2026-11-18.md`. **Nothing in `sim/`
changes.** This record decides not to ship the swap, and says why.*

## The question, and the one variable

Area map C2 says the chain reads the monthly TTF proxy (`load_nbp_history`). The proxy is flat within every month, and
it runs 29% above GB gas in 2022. The real daily GB SAP, spliced from 2018 (`load_gas_baseline_spliced`), exists, and
the chain does not read it. The arm swaps that one input.

- **B** is the shipped chain, on TTF.
- **G1** puts SAP in the call only. A0-A2 stay as fitted on TTF.
- **G2** puts SAP in the call and in the A0-A2 refit. This is the consistent one-variable change.
- **Two nulls.** Each is a daily OLS of SSP on gas with an intercept, fitted over the whole window. One is fitted on
  TTF (`null_T`, which reproduces the steer's 5.4 / 24.5 / 6.7). The other is fitted on SAP (`null_S`).
- "Monthly" means the demand-weighted monthly mean. The regimes are the steer's: pre runs to 2021-06-30, the crisis
  runs from 2021-07-01 to 2023-06-30, and post is after that.

Before 2018 the splice is TTF, so 2016-17 change only through the refit. Before filing, the annual gas means were
printed (an input, not an outcome). They agree within about 1% except in 2021 (42.6 against 39.0) and 2022 (100.3
against 71.2).

## Pre-registration, verbatim, and the outcome beside each line

The predictions were filed in `/var/tmp/gasarm/PREDICTION.txt` (mtime 11:11:14 UTC), before the probe
`/var/tmp/gasarm/measure.py` was written or run. The G2 output's mtime is 11:11:49. **Correction, beside the claim:**
the file says "~11:30 UTC". That was a wrong guess at the clock. The mtimes are the evidence for the order. The file
was not committed before the run. It is quoted here whole.

| Filed | Outcome | Held? |
|---|---|---|
| G1: null_S crisis monthly MAE ≤ 18 (null_T is 24.5) | 17.44 | **held** |
| G2: G1 crisis monthly bias ≤ −20, and G1 crisis MAE > B's 17.20 | −23.16; 27.47 | **held** |
| G3: G2's refit a1 is ≥ 10% above 1.0792 | 0.930, which is **lower**. a0 goes from 0.292 to 0.517, and a2 from 2.824 to 1.394 | **missed** (code). I assumed the refit would raise the slope. It moved level into a0 and halved the scarcity term. |
| G4: G2 crisis monthly MAE in [10, 17.20) | 20.88 | **missed** (domain) |
| G5: G2 pre within ±1.0 of 6.50; G2 post within ±1.5 of 8.19 | 4.77; 13.00 | **missed** (code). The refit is whole-window, so it moves every regime, and I treated it as touching the crisis alone. |
| G6: G2 post monthly bias above B's +1.84 | +12.28 | **held** |
| G7: daily corr(chain, SSP) in the crisis is higher under G2 than under B | 0.791 against 0.747 | **held** |
| G8: G2 does not beat null_S in the crisis | 20.88 against 17.44 | **held** |
| G9: G2 loses to null_S pre and post as well | pre 4.77 against 4.97, a **win**; post 13.00 against 9.84, a loss | **missed** (domain) |

**Five held and four missed (code 2, domain 2).**

## The numbers

Monthly MAE / monthly bias, £/MWh:

| Arm | pre | crisis | post |
|---|---|---|---|
| B, shipped (TTF) | 6.50 / −5.29 | 17.20 / +2.39 | 8.19 / +1.84 |
| G1, SAP in the call only | 6.62 / −5.35 | 27.47 / −23.16 | 8.49 / +1.83 |
| G2, SAP in the call and the refit | **4.77 / −0.35** | 20.88 / −4.09 | 13.00 / **+12.28** |
| null_T | 5.42 / +1.81 | 24.53 / −9.54 | 6.67 / +0.70 |
| null_S | 4.97 / −1.03 | **17.44** / −9.45 | 9.84 / +8.89 |

Each arm's daily MAE and daily correlation with SSP are in `/var/tmp/gasarm/out_{B,G1,G2}.json`. G2 has 2,622 distinct
gas values against B's 112.

**Mean monthly bias by year. This is exploratory and not pre-registered** (`/var/tmp/gasarm/by_year.py`):

| Year | Real SSP | SAP (TTF) | B bias | G2 bias |
|---|---|---|---|---|
| 2016 | 40.2 | 11.3 (11.3) | −9.2 | −5.4 |
| 2019 | 42.3 | 11.9 (11.8) | −3.9 | +1.1 |
| 2021 | 114.7 | 39.5 (43.1) | −8.8 | −1.6 |
| 2022 | 202.5 | 71.7 (101.0) | **+13.2** | **−10.7** |
| 2023 | 96.2 | 34.4 (34.3) | −4.1 | +8.7 |
| 2024 | 71.9 | 28.7 (29.1) | +1.9 | +11.7 |
| 2025 (to 7 Jun) | 87.5 | 35.1 (35.3) | +6.8 | +16.9 |

## What it says

1. **On the real GB gas price, one fitted price leg cannot serve both 2022 and 2023-25.** On SAP, 2022's power price
   sits at a higher markup over the gas-and-carbon floor than the years after it. The whole-window refit splits the
   difference. 2022 comes out £10.7 low, and 2023-25 come out £9-17 high. On TTF, the proxy's 29% premium in 2022
   inflated the floor by about the amount that the markup was missing. So one leg fitted both regimes by accident.
   **The proxy was standing in for a missing mechanism.** This is the steer's "crisis mis-scaling at high gas" and the
   map's "−£8 post-crisis level gap", seen together. Which mechanism it is stays open. Candidates on the electricity
   page include the 2022 exports to France during its nuclear outage, scarcity and the BM, and a post-crisis fleet
   that is more efficient than the 0.50 constant. **I cannot yet say which**, and this arm was not designed to separate
   them.
2. **Correction, beside the claim** (`6b5b42195e`'s title, and the finding's step-B note, "it now beats the gas-only
   null in the crisis"). That is true against a null on TTF (17.20 against 24.53). Against a null on the faithful gas
   price, it is a **tie** (17.20 against 17.44). Most of the "win" was the null's handicap. Against null_S, the shipped
   chain loses pre (6.50 against 4.97) and **beats** it post (8.19 against 9.84). Every chain-against-null figure from
   here should quote both nulls.
3. **Swapping the gas input does help before the crisis.** It is the first arm in which the chain beats any gas-only
   null before the crisis (4.77 against 4.97), and the pre-crisis bias goes from −5.3 to −0.4. That is the within-month
   daily gas move (pre daily MAE 10.37 → 9.03) plus a refit freed of 2022's TTF premium.

## Decision

**The swap does not ship on its own.** G2 is worse than B in the crisis (20.88 against 17.20) and after it (13.00
against 8.19). After the crisis is where forward years start. G1 is worse everywhere. The swap ships with the price-leg
mechanism that lets 2022 carry its own markup, because it needs that mechanism to fit, and the mechanism needs the
faithful gas to be measured at all. Until then, the chain keeps TTF, and every figure from it carries this record's
known error: the post-crisis level is fitted correctly only because TTF mis-states 2022.

**Next, under item 4:** pre-register the arm that names the 2022 markup. It should split the floor's markup by regime,
or test the candidates in item 1 one at a time, and it should run on SAP. Its first step is to read the electricity
page's s.10 candidates against the 2022 record. The map's −£8 post-crisis gap is the same question and closes with it.
