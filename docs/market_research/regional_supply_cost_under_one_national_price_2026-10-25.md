**Knowledge:** regional-supply-cost

# Regional supply cost under one national wholesale price: network charges and losses by region, 2016–2025

*Written 2026-10-25 (K8). It closes the knowledge half of
`docs/staging/SEAT_FINDING_REGIONAL_COST_UNDER_ONE_NATIONAL_PRICE_IS_NETWORK_CHARGES_AND_LOSSES_AND_BOTH_ARE_THIN_2026-10-24.md`.
That finding recorded that only London's DUoS had been extracted (`network_charges_uk_2016_2024.md` §9
item 4) and that losses appeared nowhere in the record or the code.*

## 0. What this page is about, before any number

GB has one national wholesale price. The director ruled zonal pricing out on 21 Jul 2026. Even so,
the cost of supplying one metered kWh still differs by **where the meter is**, for two separate
reasons. They are different kinds of cost and are kept apart here:

1. **Network charges** (DUoS, TNUoS, BSUoS). These are use-of-system tariffs, published by the 14 DNO
   licence areas and by NESO, and passed through per customer and per kWh. They are a **charge on a
   meter**.
2. **Losses.** Energy is lost in the transmission and distribution networks, so a supplier must buy
   more energy at the grid than its meters record. This is a **quantity uplift on the energy a
   supplier buys**, priced at the wholesale price. Settlement applies it through Line Loss Factors
   (distribution, set by the DNOs), Transmission Loss Multipliers (zonal since BSC P350) and GSP Group
   Correction.

The region unit for both is the **GSP group**. That is the 14 Charge Restriction Regions in Ofgem's cap,
the same as the 14 DNO licence areas. It is **not** the ONS region the world draws households in (see §5).

## 1. The source, and why it is the right one

Ofgem's price cap **builds its regional network and loss allowances bottom-up from the published
charging statements and loss factors**, and it publishes the build-up for every cap period back to
April 2015 (periods before Jan 2019 are labelled "historical examples, for illustration only"). Two
workbooks were read on 2026-10-25:

| Workbook | URL | sha256 | What was read |
|---|---|---|---|
| Annex 3, network cost allowance methodology, electricity, v1.25 (Oct–Dec 2026 edition) | `https://www.ofgem.gov.uk/sites/default/files/2026-08/Annex-3-network-cost-allowance-methodology-electricity-v1.25.xlsx` | `36bced6c48cf6c63bd5b3d0cc892a855a51c0e588e01d11a0f82fc14552f5ff3` | sheets `2a TNUoS`, `2b DUoS`, `2c BSUoS`, `1a Network Cost Allowance-Elec`, `3b Losses` |
| Supplementary workbook to Annexes 2, 3 and 4, demand and losses, v1.19 | `https://www.ofgem.gov.uk/sites/default/files/2026-08/Supplementary-workbook-to-annex-2-3-and-4-demand-and-losses-v1.19.xlsx` | `ac1c4b36fbf31abc9273b6b0a1392f947fc4e3bc168f2384de6a7ea6f2687e1f` | sheet `1a Loss multipliers` (charging year 2026/27) and its Notes |
| Ofgem consultation, *Energy price cap methodology: group correction factors*, 22 Aug 2025 | `https://www.ofgem.gov.uk/sites/default/files/2025-08/Energy-price-cap-methodology-group-correction-factors.pdf` | — | §1, §3, Appendix GCF table |
| Ofgem cap level model v1.31 (already cached; see `tools/ofgem_cap_unit_rate_composition.py`) | as recorded there | — | `3a DF` and `ElecSingle_Other_Benchmark`, as a cross-check |

**Reading rule.** Each charging year is the April cap period that starts it ("April 2016 – September
2016" for 2016/17, and so on, resolved by period label rather than column number). Single-rate meter,
"other" payment method, benchmark 3,100 kWh/yr. "£/MWh" below means the £/customer/yr allowance at
benchmark divided by 3.1 MWh. It is an **all-in per-unit figure that includes the fixed (nil-consumption)
part**, not the unit rate. The bytes were fetched by the harness and read into this document; nothing
here is a runtime input (W6).

**Cross-checks that passed.**
- Annex 3 `2b DUoS` London 2016/17 = £75.70/customer/yr, which is 24.4 £/MWh. That equals the figure
  `network_charges_uk_2016_2024.md` §2a read from the Oct 2019 Annex 3 (£24.42/MWh). Same publisher,
  two editions seven years apart, same number.
- `1a` NC = DUoS + TNUoS + BSUoS to the penny (London 2016/17: 75.70 + 38.68 + 7.27 = 121.65; London
  Apr 2026: 69.28 + 84.94 + 42.71 = 196.93).
- **The cap's wholesale allowance carries losses.** The ratio of cap model `3a DF` region to London,
  April 2015, equals the ratio of the `3b` transmission-and-distribution loss multipliers to four
  decimals: Eastern 1.0122 against 1.0122, East Midlands 0.9899 against 0.9899, Southern Western 0.9767
  against 0.9767, Yorkshire 1.0129 against 1.0129. The demand-and-losses workbook says the same in words.
  Its `1a` table labels the April–March T&D multiplier "Direct fuel costs, Contracts for Difference,
  BSUoS, NCC, Nrab". **So every published regional cap level already prices losses into the energy
  line.**

## 2. Network charges by region (Annex 3, £/MWh all-in at 3,100 kWh, single-rate)

### 2a. Total network cost allowance (DUoS + TNUoS + BSUoS)

| Region | 16/17 | 17/18 | 18/19 | 19/20 | 20/21 | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 |
|---|---|---|---|---|---|---|---|---|---|---|
| Eastern | 40.2 | 41.9 | 41.5 | 44.3 | 44.7 | 48.3 | 64.5 | 66.5 | 64.5 | 63.9 |
| East Midlands | 41.1 | 38.7 | 38.1 | 39.8 | 40.1 | 44.7 | 60.2 | 64.8 | 59.4 | 58.1 |
| London | 39.2 | 34.7 | 35.9 | 39.3 | 41.4 | 45.9 | 59.6 | 63.4 | 56.9 | 51.3 |
| N Wales and Mersey | 49.9 | 48.9 | 47.1 | 53.1 | 54.1 | 56.7 | 74.1 | 87.4 | 83.2 | 95.0 |
| Midlands | 44.3 | 41.6 | 41.9 | 43.0 | 41.8 | 47.0 | 62.7 | 68.6 | 65.9 | 61.8 |
| Northern | 46.7 | 43.2 | 40.5 | 42.8 | 44.6 | 48.1 | 61.5 | 73.1 | 74.4 | 69.9 |
| North West | 43.1 | 39.4 | 40.0 | 43.0 | 41.1 | 43.6 | 60.1 | 72.8 | 64.3 | 73.6 |
| Southern | 42.5 | 41.9 | 41.0 | 41.8 | 40.6 | 46.3 | 63.4 | 69.5 | 74.3 | 60.7 |
| South East | 48.3 | 46.3 | 44.4 | 47.9 | 49.4 | 54.6 | 70.8 | 72.0 | 73.2 | 67.5 |
| South Wales | 50.6 | 46.5 | 45.9 | 47.9 | 48.0 | 53.2 | 67.8 | 75.3 | 72.9 | 70.8 |
| Southern Western | 54.4 | 52.9 | 49.8 | 50.9 | 51.4 | 58.0 | 74.4 | 79.5 | 76.6 | 75.6 |
| Yorkshire | 40.9 | 38.6 | 37.9 | 39.8 | 41.3 | 44.8 | 59.7 | 67.5 | 67.3 | 63.1 |
| Southern Scotland | 45.2 | 40.2 | 40.5 | 42.3 | 42.9 | 45.6 | 63.5 | 77.4 | 67.7 | 65.6 |
| Northern Scotland | 57.7 | 54.8 | 50.1 | 49.8 | 53.1 | 54.7 | 68.8 | 82.9 | 78.8 | 86.9 |

Spread, cheapest to dearest region: £18.4/MWh (16/17), £14–15 (18/19–22/23), £24.0 (23/24),
£26.3 (24/25), **£43.7 (25/26)**. Median region: 44.7, 41.9, 41.3, 43.0, 43.7, 47.6, 63.5, 72.4, 70.3,
66.6. London is the cheapest region in 8 of the 10 years. It is 5th in 2020/21 and 2021/22, when East
Midlands and North West are cheapest.

### 2b. DUoS alone (the part that varies most)

| Region | 16/17 | 17/18 | 18/19 | 19/20 | 20/21 | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 |
|---|---|---|---|---|---|---|---|---|---|---|
| Eastern | 25.5 | 25.5 | 25.1 | 26.9 | 27.6 | 28.9 | 42.4 | 32.1 | 41.4 | 35.5 |
| East Midlands | 26.7 | 24.4 | 23.5 | 24.3 | 24.8 | 27.0 | 40.0 | 30.7 | 36.7 | 30.3 |
| London | 24.4 | 21.6 | 21.5 | 24.3 | 26.6 | 28.3 | 39.9 | 27.8 | 32.7 | 21.6 |
| N Wales and Mersey | 35.0 | 33.5 | 32.8 | 37.9 | 39.0 | 39.4 | 53.9 | 52.7 | 60.3 | 66.8 |
| Midlands | 29.9 | 26.9 | 26.5 | 26.9 | 25.8 | 28.5 | 41.8 | 33.6 | 42.5 | 33.1 |
| Northern | 31.3 | 29.2 | 28.4 | 30.1 | 32.1 | 33.4 | 44.6 | 39.3 | 51.9 | 42.2 |
| North West | 29.8 | 25.5 | 25.9 | 28.2 | 26.5 | 26.8 | 40.8 | 39.0 | 41.7 | 45.7 |
| Southern | 27.9 | 26.1 | 24.5 | 24.6 | 23.5 | 26.5 | 41.3 | 33.8 | 49.7 | 30.9 |
| South East | 33.2 | 29.4 | 27.1 | 29.9 | 31.4 | 34.5 | 48.0 | 36.8 | 49.3 | 38.1 |
| South Wales | 36.1 | 33.0 | 32.8 | 33.9 | 34.0 | 35.7 | 48.1 | 39.7 | 49.1 | 41.4 |
| Southern Western | 39.2 | 36.5 | 33.1 | 33.5 | 33.6 | 36.9 | 51.0 | 43.5 | 51.8 | 45.2 |
| Yorkshire | 25.8 | 24.4 | 24.1 | 25.1 | 26.9 | 28.0 | 40.6 | 33.3 | 44.5 | 35.0 |
| Southern Scotland | 30.8 | 29.5 | 30.2 | 31.6 | 32.6 | 33.3 | 47.9 | 43.1 | 44.9 | 38.2 |
| Northern Scotland | 44.2 | 40.3 | 40.8 | 41.6 | 44.5 | 44.5 | 55.1 | 49.3 | 56.4 | 60.0 |

Dearest-to-cheapest ratio: 1.81, 1.86, 1.90, 1.71, 1.90, 1.68, 1.38, 1.89, 1.85, **3.09**.

**What this corrects.** `network_charges_uk_2016_2024.md` §2b says "most UK regions pay 30–80% more than
London". That holds for the *dearest* regions in most years. It is wrong as a statement about most
regions: in 2016/17, 4 of 13 non-London regions (Eastern, East Midlands, Southern, Yorkshire) were within 15% of London. Its §9 item 4 says "national
average is 20–50% higher than London". For DUoS the median region was 25% above London in 2016/17 and
76% above it in 2025/26. **The ratio is not a constant**, and from April 2022 its shape changes (§2c).

### 2c. The structural breaks a reader must not difference across

- **April 2022, DUoS residual to fixed charges** (Ofgem's Targeted Charging Review, DUoS side). The
  nil-consumption DUoS jumps: Northern Scotland £24.4 to £100.4/yr, N Wales and Mersey £13.4 to
  £92.0/yr. The single-rate DUoS *unit* component falls to 0.99–2.72p/kWh, from 1.83–3.37p in 2019/20.
  From this date the regional difference sits mostly in the **standing charge**, which is why the
  world's lack of a regional standing charge (`simulation/policy_costs.py`, "the world has no regional
  standing charge") is the same gap seen from the other side.
- **April 2023, TNUoS residual to a per-site daily charge** (CMP343). From 2023/24 TNUoS nil is the same
  in every region (£43.53/yr in 2023/24, £38.17 in 2024/25, £49.29 in 2025/26). Only the small locational
  element still varies by region.
- **April 2022, BSUoS 100% on demand.** BSUoS is nearly uniform by region (it is a GB charge scaled by
  the region's loss multiplier), so it adds to the level and hardly at all to the spread.
- **April 2023, RIIO-ED2.** DNO allowed revenue resets. The April 2025 London DUoS (£67.0/yr, down from
  £101.2) is read as published. It has **not** been checked against UKPN's own 2025/26 charging statement
  (GAP, §6).

## 3. Losses by region

### 3a. The mechanism

Settlement scales each supplier's metered volume up to what entered the network:

- **Distribution: Line Loss Factors.** Each DNO publishes these per LLF class, per settlement period,
  per year, and settlement applies them per meter (BSC Section K and BSCP128).
- **Transmission: Transmission Loss Multipliers.** Since **1 April 2018 (BSC P350)** these are
  **zonal**: one Transmission Loss Factor per TLF zone (the 14 GSP groups) per BSC season. That gives
  28 TLMs per settlement period, an offtaking and a delivering one for each GSP group, where before
  there were two. A positive TLF disadvantages suppliers in that zone. P350 was National Grid's
  response to the CMA's 2016 energy market investigation remedy on locational losses (Elexon P350
  modification page; Elexon BSC Insights, "three ways P350 has changed transmission losses").
- **GSP Group Correction.** This scales every supplier's allocated volume in a GSP group, each
  half-hour, so the total matches what entered the group. The same factor applies to every supplier
  in the group, so no supplier's own action moves it much (Ofgem GCF consultation 2025, ¶1.1, ¶1.8).
  Its causes include estimation error, theft and unaccounted losses, LLFs that understate losses, and
  embedded generation (¶1.5–1.7).

### 3b. The size: Ofgem's demand-weighted T&D loss multiplier (Annex 3 `3b`, section 2)

This is the multiplier the cap applies to the energy a single-rate domestic customer's supplier buys:

| Region | 16/17 | 17/18 | 18/19 | 19/20 | 20/21 | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 |
|---|---|---|---|---|---|---|---|---|---|---|
| Eastern | 1.108 | 1.108 | 1.096 | 1.102 | 1.101 | 1.102 | 1.104 | 1.111 | 1.118 | 1.132 |
| East Midlands | 1.084 | 1.084 | 1.083 | 1.081 | 1.083 | 1.084 | 1.084 | 1.095 | 1.098 | 1.113 |
| London | 1.095 | 1.095 | 1.106 | 1.108 | 1.110 | 1.114 | 1.118 | 1.121 | 1.128 | 1.142 |
| N Wales and Mersey | 1.108 | 1.108 | 1.114 | 1.116 | 1.120 | 1.121 | 1.130 | 1.126 | 1.126 | 1.148 |
| Midlands | 1.086 | 1.086 | 1.091 | 1.093 | 1.100 | 1.103 | 1.105 | 1.104 | 1.110 | 1.121 |
| Northern | 1.095 | 1.095 | 1.077 | 1.072 | 1.070 | 1.067 | 1.073 | 1.078 | 1.077 | 1.100 |
| North West | 1.100 | 1.100 | 1.096 | 1.097 | 1.092 | 1.086 | 1.090 | 1.078 | 1.080 | 1.120 |
| Southern | 1.081 | 1.081 | 1.087 | 1.091 | 1.099 | 1.110 | 1.102 | 1.109 | 1.114 | 1.121 |
| South East | 1.093 | 1.093 | 1.090 | 1.093 | 1.100 | 1.104 | 1.104 | 1.112 | 1.113 | 1.124 |
| South Wales | 1.087 | 1.087 | 1.075 | 1.083 | 1.084 | 1.092 | 1.098 | 1.096 | 1.108 | 1.122 |
| Southern Western | 1.069 | 1.069 | 1.070 | 1.082 | 1.086 | 1.091 | 1.087 | 1.085 | 1.094 | 1.108 |
| Yorkshire | 1.109 | 1.109 | 1.091 | 1.092 | 1.099 | 1.095 | 1.097 | 1.102 | 1.103 | 1.137 |
| Southern Scotland | 1.102 | 1.102 | 1.092 | 1.093 | 1.089 | 1.095 | 1.109 | 1.105 | 1.108 | 1.071 |
| Northern Scotland | 1.102 | 1.102 | 1.079 | 1.069 | 1.055 | 1.064 | 1.083 | 1.069 | 1.073 | 1.029 |

Median region: 1.095 (16/17) rising to 1.121 (25/26). For 2026/27, the demand-and-losses v1.19
workbook gives 1.076 (Northern Scotland) to 1.167 (N Wales and Mersey), and that figure includes the
GCF uplift.

**What this says.**
- **A supplier buys about 9–12% more energy than its domestic meters record.** It is never zero. The
  number has risen through the decade. The 2015/16–2017/18 columns are identical within every region
  and the values move from 2018/19. That is consistent with zonal TLFs starting under P350 in April 2018,
  but the workbook does not say so in words.
- **The regional spread is 4–12 percentage points**: 3.9pp in 16/17, 6.6pp in 21/22, 11.9pp in 25/26
  (Northern Scotland's 1.029 there sits at a negative GCF, −0.28%, and a negative zonal TLF). At a
  wholesale cost of £50/MWh that is £2–6/MWh. At the 2022/23 crisis level of several hundred £/MWh it
  is larger than the whole regional DUoS spread.
- **GCF has been added since Nov 2025.** Ofgem's consultation measured two-year GCFs (2023/24 and
  2024/25) of −0.28% (Northern Scotland) to +3.24% (Yorkshire), with a GB average of +1.46%. It found
  "accounting for electrical losses in the cap through LLFs alone is no longer sufficient", and from
  the November 2025 update it applies the **GB-average** two-year GCF uplift to every region's loss
  multiplier.

## 4. What our code does, read 2026-10-25

| Where | What it does | Against this page |
|---|---|---|
| `simulation/policy_costs.py` `_NETWORK_COST_RESI_SME_BY_YEAR` | One national £/MWh per year, from Annex 9's GB NC row (43–75 £/MWh, 2016–2024) | Matches the regional **median** within about £3/MWh. It carries none of the £14–44/MWh spread between regions, and no regional standing charge |
| `company/market/duos_ledger.py` `_DUOS_UNIT_RATE_P_PER_KWH` | One national DUoS unit rate per year, 1.85–2.75p, with a 14-member `DNOArea` enum that does not select a rate | Unsourced and region-blind. From 2022 the real DUoS unit component is 0.99–2.72p, with the residual in the standing charge. The ledger is reached by no production caller (grep 2026-10-25) |
| `company/market/llf_register.py` | A per-MPAN LLF store, reached only by its own test. Its docstring said "typical domestic LLF 1.00–1.05" and that TLMs "are national" | **Both are wrong.** Ofgem's distribution-only demand-weighted multiplier is 1.08–1.15 for single-rate domestic customers (D&L v1.19 §2), and TLMs have been zonal since April 2018. Corrected in the docstring in the same commit as this page |
| World settlement and supplier cost | **No loss uplift anywhere.** No `LLF`, `TLM`, `GCF` or loss-multiplier term in `simulation/`, `sim/`, `company/` or `saas/` outside the unreached register | The world settles metered kWh. A real supplier pays for about 1.09–1.12× those kWh |

**The finding this produces, and its direction.** Losses are not a regional subtlety. They are a
**national ~9–12% uplift on the energy line**, and the world omits all of it. It is published in the
cap: the cap's DF allowance is scaled by the loss multiplier, as shown in §1. So any revenue or price
anchored to the cap includes losses, while the world charges the supplier for none. **That flatters
margin.** At the cap's own allowances, the share of direct fuel that is losses is
(1 − 1/loss multiplier) × DF, because DF already includes the uplift. For London that is about
£13/customer/yr in Apr–Sep 2016 (DF £153.0, multiplier 1.095). At the Jan–Mar 2023 peak it is about
£134/customer/yr, annualised (DF £1,266.7, multiplier 1.118). In Apr–Jun 2025 it is about £44/yr
(DF £353.7, multiplier 1.142). DF is from cap level model v1.31 `3a DF`. This is an estimate from the cap's own figures, **not a measurement of our
book**. The measurement is filed as a finding
(`docs/staging/SEAT_FINDING_THE_WORLD_SETTLES_METERED_KWH_AND_NO_LOSSES_SO_THE_ENERGY_LINE_IS_9_TO_12_PCT_LIGHT_2026-10-25.md`).
It is a fidelity fix to the baseline world (W7: world first). It has not been tuned to company results.

## 5. Choices this page makes for a future build, and why

- **Region key.** Network charges and losses are set per GSP group. The world draws households in 11
  ONS regions (`simulation/population_draw.py`). These do not nest: Scotland is two GSP groups,
  "N Wales and Mersey" crosses the England–Wales line, and South Wales and the North Wales part are
  different DNOs. **A build needs an address-to-GSP-group mapping**, and the published one is MPAN
  distributor ID by postcode. Until that exists, a regional figure applied by ONS region is an
  approximation and must say so.
- **Losses first, regional spread second.** The national loss uplift is the larger error and needs no
  region key: the GB median multiplier per year, from the table above, applied to settled energy. The
  regional DUoS and loss spread needs the mapping.
- **The order of the uplifts.** Use Ofgem's April–March demand-weighted multiplier (T&D) for energy.
  It is the cap's own figure and what a supplier pricing to the cap would use. A per-meter LLF is finer
  and would need LLF classes the world does not draw.

## 6. GAP: what is not established here

1. **Pre-2019 values are Ofgem's "historical examples, for illustration only".** They were built by
   Ofgem with the same method, but they are not cap levels that were ever in force. 2016/17 London
   agrees with an independent 2019 edition (§1).
2. **One cap period per charging year.** The April period is used. Where the cap re-set mid-year
   (Oct 2022 onward, quarterly), BSUoS in particular moves within the year. 2023/24 BSUoS uses the
   Apr–Sep 2023 value (£63.6/yr London), which is not the year's mean.
3. **Not checked against the DNOs' own charging statements.** These figures are Ofgem's reading of
   them. The London 2025/26 DUoS fall (£101.2 to £67.0/yr) in particular has not been checked against
   UKPN's 2025/26 statement.
4. **Multi-rate (Economy 7) meters** are in the same sheets and were not tabulated here.
5. **Actual settled losses against the cap's assumed multiplier.** GCF data (Elexon portal,
   `GSPGCF_YYYY.xls`) is the published measure of how far reality ran from LLFs. Only Ofgem's two-year
   summary was read.
6. **The address-to-GSP-group mapping** (§5) has not been sourced.

## 7. Reproduce

Download the two workbooks above into an empty directory. Read them with openpyxl (`data_only=True`).
In each of `2b DUoS`, `2a TNUoS`, `2c BSUoS`, `1a Network Cost Allowance-Elec` and `3b Losses`, find the
row whose cells begin "April 2015" and take the first column per year whose label begins
`April <year>`. Single-rate benchmark rows are `2b`/`2a` from row 25, `2c` from row 11, `1a` from row
28, and `3b` section 2 from row 53. Region names are in column F (`2a`–`1a`) or D (`3b`).
