# Ofgem Default Tariff Cap — the real sub-annual window schedule

**Atom:** `W3_1b_intra_year_price_cap_granularity`. **Sourced:** 2026-08-03.
**Wall:** R13 — this is real published regulatory history. It is sourced blind to company P&L and no
value here may be moved because a simulation result looks wrong. R12 — the cap is an external
constraint, never a margin dial.

Consumed by `company/pricing/ofgem_price_cap.py::_CAP_WINDOWS`.

---

## 1. Why the windows, not the years

The in-sim clamp used to key the cap on `current_date.year`, giving every day of 2022 one full-year
blend (elec 305, gas 95 £/MWh). The real cap does not move on 1 January. It moved:

- **six-monthly** (1 Apr / 1 Oct) from the 1 Jan 2019 launch through 30 Sep 2022;
- **quarterly** (1 Jan / 1 Apr / 1 Jul / 1 Oct) from 1 Oct 2022 onward.

The consequence that matters: **the Oct-2021 cap ran through 31 March 2022**, and the +54% step
(£1,277 → £1,971 typical dual-fuel bill) landed on **1 April 2022**. An annual key puts a Jan–Mar 2022
deemed customer under 305 £/MWh instead of the 208 £/MWh that actually applied — the ceiling is ~£97/MWh
too loose in precisely the quarter the squeeze bit hardest, so in-sim crisis margin comes out *less*
negative than reality. That is the crisis dynamic this part of the simulation exists to reproduce.

## 2. Window boundaries — source

The date ranges below are **Ofgem's own published cap periods**, taken from the regulator's
[Energy price cap (default tariff) levels](https://www.ofgem.gov.uk/energy-regulation/domestic-and-non-domestic/energy-pricing-rules/energy-price-cap/energy-price-cap-default-tariff-levels)
page, which enumerates them as `1 Jan – 31 Mar 2019`, `1 Apr – 30 Sep 2019`, `1 Oct 2019 – 31 Mar 2020`,
… `1 Oct 2021 – 31 Mar 2022`, `1 Apr – 30 Sep 2022`, `1 Oct – 31 Dec 2022`, and quarterly thereafter.

**Two secondary aggregators were rejected as the date source** and the rejection is worth recording,
because the closed DISCOVER doc for this atom cited one of them as primary. Both
[pricecaprates.co.uk](https://www.pricecaprates.co.uk/history) and
[utilitymatchmaker.co.uk](https://www.utilitymatchmaker.co.uk/tools/price-cap-history) return the same
*levels* but carry **wrong effective dates** — they list `1 Jul 2019` and `1 Feb 2021` for cap changes
Ofgem dates to 1 Apr 2019 and 1 Apr 2021, and they omit the Oct-2019 (£1,179) and Oct-2020 (£1,042)
levels entirely. Their mutual agreement is not independence. Ofgem's own enumeration is the oracle.

## 3. Unit rates — source

Typical-household unit rates per cap period, from
[electricityprices.org.uk's cap history](https://www.electricityprices.org.uk/history-of-the-energy-price-cap/),
converted p/kWh × 10 → £/MWh.

**Independent corroboration for the two crisis windows** (the ones this atom turns on): the House of
Commons Library records electricity rising to **20.8p/kWh for Oct 2021 – Mar 2022** and **28.3p for
Apr – Sep 2022**, and gas **4.1p → 7.4p** over the same two windows
([CBP-9491 / CBP-9714](https://commonslibrary.parliament.uk/research-briefings/cbp-9491/)). Those match
20.80/4.07 and 28.34/7.37 below. They also match the values already carried independently in-repo at
`company/regulatory/price_cap.py::_PRICE_CAP_QUARTERLY` — three sources, one figure.

| Cap window (effective) | Elec p/kWh | Gas p/kWh | Elec £/MWh | Gas £/MWh | Typical dual-fuel bill |
|---|---|---|---|---|---|
| 1 Jan – 31 Mar 2019 | 16.52 | 3.73 | 165.2 | 37.3 | £1,137 |
| 1 Apr – 30 Sep 2019 | 18.56 | 4.14 | 185.6 | 41.4 | £1,254 |
| 1 Oct 2019 – 31 Mar 2020 | 17.85 | 3.68 | 178.5 | 36.8 | £1,179 |
| 1 Apr – 30 Sep 2020 | 17.81 | 3.50 | 178.1 | 35.0 | £1,126 |
| 1 Oct 2020 – 31 Mar 2021 | 17.19 | 3.00 | 171.9 | 30.0 | £1,042 |
| 1 Apr – 30 Sep 2021 | 18.95 | 3.34 | 189.5 | 33.4 | £1,138 |
| **1 Oct 2021 – 31 Mar 2022** | **20.80** | **4.07** | **208.0** | **40.7** | **£1,277** |
| **1 Apr – 30 Sep 2022** | **28.34** | **7.37** | **283.4** | **73.7** | **£1,971 (+54%)** |
| 1 Oct – 31 Dec 2022 | 51.89 | 14.76 | 518.9 | 147.6 | £3,549 (EPG £2,500) |
| 1 Jan – 31 Mar 2023 | 67.47 | 17.08 | 674.7 | 170.8 | £4,279 (EPG £2,500) |
| 1 Apr – 30 Jun 2023 | 50.60 | 12.61 | 506.0 | 126.1 | £3,280 (EPG £2,500) |
| 1 Jul – 30 Sep 2023 | 30.11 | 7.51 | 301.1 | 75.1 | £2,074 |
| 1 Oct – 31 Dec 2023 | 27.35 | 6.89 | 273.5 | 68.9 | £1,923 |
| 1 Jan – 31 Mar 2024 | 28.62 | 7.42 | 286.2 | 74.2 | £1,928 |
| 1 Apr – 30 Jun 2024 | 24.50 | 6.04 | 245.0 | 60.4 | £1,690 |
| 1 Jul – 30 Sep 2024 | 22.36 | 5.48 | 223.6 | 54.8 | £1,568 |
| 1 Oct – 31 Dec 2024 | 24.50 | 6.24 | 245.0 | 62.4 | £1,717 |
| 1 Jan – 31 Mar 2025 | 24.86 | 6.34 | 248.6 | 63.4 | £1,738 |
| 1 Apr – 30 Jun 2025 | 27.03 | 6.99 | 270.3 | 69.9 | £1,849 |
| 1 Jul – 30 Sep 2025 | 25.73 | 6.33 | 257.3 | 63.3 | £1,720 |
| 1 Oct – 31 Dec 2025 | 26.35 | 6.29 | 263.5 | 62.9 | £1,755 |

## 4. The Energy Price Guarantee overlay

Between **1 Oct 2022 and 30 Jun 2023** the EPG held a typical dual-fuel direct-debit bill at **£2,500**,
far below the Ofgem cap (which peaked at £4,279 for Jan–Mar 2023). Nobody paid the full cap in that
window. The binding domestic ceiling there is therefore `min(Ofgem cap, EPG)`.

This is modelled as a **separate overlay column** (`elec_epg` / `gas_epg` = 340.0 / 103.2 £/MWh, the
published EPG-equivalent unit rates already carried in-repo) rather than baked into one number, so the
two instruments — a regulated cap and a subsidy — stay individually legible. Collapsing them would make
the £4,279 Jan-2023 cap disappear from the record entirely.

## 5. Declared simplifications (bounded, not hidden)

1. **Unit rate only, no standing charge.** The real cap has two legs. The in-sim clamp is a £/MWh unit
   ceiling; the standing-charge leg (which itself stepped materially — elec ~25 ppd in 2021 to ~45 ppd
   in 2022) is not modelled. Pre-existing, unchanged by this atom. If it is ever added it inherits this
   same window granularity.
2. **VAT basis.** The published figures above include VAT at 5%. This is the same basis the existing
   annual table and `_PRICE_CAP_QUARTERLY` were already on, so nothing moved — but the
   `ofgem_price_cap.py` docstring previously claimed "excluding VAT", which was wrong about its own
   numbers and is corrected.
3. **No regional variation.** The cap varies by GSP region and payment method (direct debit /
   prepayment / standard credit). Only the typical direct-debit national figure is modelled.
4. **Post-2025 carry-forward.** Dates past 31 Dec 2025 carry the last published window forward rather
   than returning "no cap". A `None` there would silently un-cap every resi customer — the FAIL-OPEN
   pattern R15 names. The cap is a standing statutory instrument: "no published level yet" means the
   last one still stands.

## 6. Measured effect of the correction — and a second defect it exposed

Measured blind to company P&L (R13/R12: this is a fidelity-to-source correction; no value was chosen by
looking at margin). Comparing the old annual blend against the real window for the same date, £/MWh:

| Window | Fuel | Annual blend | Real window | Δ | Effect on the ceiling |
|---|---|---|---|---|---|
| **Jan–Mar 2022** | elec | 305.0 | **208.0** | **−97.0** | ceiling was **far too loose** |
| **Jan–Mar 2022** | gas | 95.0 | **40.7** | **−54.3** | ceiling was **far too loose** |
| Apr–Sep 2022 | elec | 305.0 | 283.4 | −21.6 | too loose |
| Apr–Sep 2022 | gas | 95.0 | 73.7 | −21.3 | too loose |
| Jan–Mar 2021 | elec | 183.0 | 171.9 | −11.1 | too loose |
| 2019–2020, Oct-2022 onward | both | — | — | **+5 to +80** | ceiling was too **tight** |

**The named finding is confirmed and is the largest single deviation in the whole table**: the Jan–Mar
2022 electricity ceiling was 97 £/MWh (47%) too loose and gas 54.3 £/MWh (133%) too loose, in the exact
quarter the crisis bit. In-sim revenue from capped deemed customers there was over-stated and crisis
margin was less negative than reality. Correcting it makes the squeeze bite as it really did.

**A second defect the measurement exposed, which the DISCOVER did not predict.** The annual table is not
merely mis-*timed*; outside the crisis window it is systematically mis-*levelled* — 10 to 80 £/MWh
BELOW the published cap in almost every other period (2025 electricity: 190.0 against a real 248.6–270.3).
It was authored as a hand-built ballpark ("Rich's direction: ballpark + components right, not
year-on-year precision"), and that ballpark drifted low. So the re-thread moves the ceiling in *both*
directions: down in the crisis window, up nearly everywhere else — meaning fewer non-crisis customers
were capped in reality than the sim was clamping. Both moves are toward the published source.

This is the R13 baseline-correction direction (fidelity to real regulatory history), not a curriculum
change and not a response to company results. **Expect published financial figures to move on the next
full run.** That movement is the correction landing, not a regression.

## 7. Known defect left in a sibling table (registered, not fixed here)

`company/regulatory/price_cap.py::_PRICE_CAP_QUARTERLY` is keyed by **calendar quarter** and is offset
against the real windows through the whole six-monthly era: `2022-Q1` carries 28.34/7.37/£1,971, i.e.
the **April** 2022 cap, for a quarter (Jan–Mar 2022) governed by the **October 2021** cap of
20.80/4.17/£1,277. `2022-Q3` likewise carries the October-2022 level for a July–September quarter.

That table's consumer is `PriceCapBook` (regulatory compliance reporting), not the settlement clamp, so
this atom does not touch it — but a naive future re-thread of any clamp to it by calendar quarter would
**re-introduce exactly the defect closed here**. Registered as debt on `W3_1_price_cap_binding`.
The closed DISCOVER doc found the `2022-Q1` instance; the offset is systematic across 2019–Sep-2022, so
the fix when it is drawn is a re-keying of the table, not a row edit.
