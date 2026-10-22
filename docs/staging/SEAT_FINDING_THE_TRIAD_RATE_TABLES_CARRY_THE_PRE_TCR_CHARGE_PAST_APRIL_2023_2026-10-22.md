**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 4 · **Atom:** `W3_3_the_network_charge_splits_per_unit_and_per_day` · **Claim:** `front-door-four-domain-points-from-the-cold-read` (Lane 0 delivery)

# The Triad rate tables carry the pre-TCR charge past April 2023

**Found by** the delivery seat on 22 Oct 2026, checking the energy cold reader's Triad point
(`docs/market_research/four_front_door_domain_points_from_the_energy_cold_read_2026-10-22.md` §2).

## What is wrong

From April 2023, CMP343 (Ofgem's Targeted Charging Review) took the TNUoS demand residual off
Triad. Only the locational element is still charged on HH Triad demand. For 2023/24 that is an
average of £5.59/kW, £0/kW in zones 1–7, and £7.65/kW at most (NESO *Final TNUoS Tariffs for
2023/24*, Table 9). Our tables do not show the change:

- `company/market/triad_notification_book.py` `_TNUOS_TRIAD_RATE_GBP_PER_KW`: 2023 £66.30, 2024
  £70.10, 2025 £73.50, still rising. That is roughly ten times the published average.
- `company/trading/triad_exposure_register.py` `CustomerTriadExposure.tnu_os_tariff_gbp_per_kw`
  defaults to £80, labelled "typical residential Zone 14". Residential sites were never charged per
  kW of Triad. Its only caller is its test.
- `company/market/tnuos_ledger.py` shows no step at 2023 in either its residual p/kWh or its zone
  factors.

## What it does and does not touch

Industrial and commercial supply is suspended (late August 2026), so no current run reads these
rates through a live account. Nothing published carries them today. The tables matter only if I&C
returns, and then they would overstate the value of Triad avoidance from 2023/24 by about an order
of magnitude. That error would favour the flexibility book.

## What done means

The 2023–2025 rows are replaced with NESO's published HH demand tariffs by zone, each with its
origin. The domestic residual is the single band (£0.119264/site/day for 2023/24). Pre-2023 rows
are checked against the NESO PDFs listed in `network_charges_uk_2016_2024.md` §8. Do this before any
I&C reinstatement, not now.
