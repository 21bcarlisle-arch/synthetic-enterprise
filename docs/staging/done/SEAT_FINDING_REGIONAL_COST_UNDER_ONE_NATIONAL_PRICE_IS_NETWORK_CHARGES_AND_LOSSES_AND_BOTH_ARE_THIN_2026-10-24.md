**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 4 · **Atom:** `W3_3_the_network_charge_splits_per_unit_and_per_day`

# Regional cost under one national wholesale price is network charges and losses, and our record of both is thin

**What happened.** The director ruled zonal pricing out on 21 Jul: *"REMA is a waste of time. It isn't
live policy. Why are we researching things that don't exist."*
(`docs/staging/done/DIRECTOR_STEER_FORWARD_DISCOVERY_REGISTER_2026-07-21.md`). The map still carried
`W1_8_zonal_locational_pricing` open at target 3, and `B5_regional_basis_risk` depended on it. The
director-asks ledger found this on 24 Oct. Both atoms are now closed at level 0 with the reason on
the row (target lowered to 0, refiled to `maturity_map_closed.yaml`, as `12b972fb99` did for W4_2).

**Why B5 was closed, not re-pointed.** B5's frame, name and real-world twin all assume settling at
zonal prices while hedging at the national price. Under the one national price GB actually has, no
wholesale basis of that kind exists. Regional cost differences do exist, but they are not a hedge
problem. They are cost lines a supplier passes into regional tariffs, and they already have an atom.
Re-pointing B5 would make a second home for that work.

**What regional cost actually is, and what we know about it:**

1. **Network charges (DUoS), by DNO region.** These are the largest regional cost. The owning atom is
   `W3_3_the_network_charge_splits_per_unit_and_per_day`, and on the supplier side
   `company/market/duos_ledger.py`. **The gap:** `docs/market_research/network_charges_uk_2016_2024.md`
   item 4 says only London's DUoS has been extracted. It records other regions as "30–80% more"
   without a per-region source. A world with regional households and one region's network tariff
   understates regional cost dispersion.
2. **Losses.** Transmission and distribution losses scale the energy a supplier must buy for each
   metered kWh, and they vary by location. **NOT ESTABLISHED in our record.** No market-research
   note, knowledge-map row or module models transmission loss multipliers or line loss factors (grep
   for `TLM`, `transmission_loss`, `LLF` over `company/`, `sim/`, `simulation/` and
   `docs/market_research/`: no hits on 24 Oct). The lead to research first is whether BSC
   transmission losses have been allocated by zone, and from when. That is a published BSC matter
   (Elexon), so it is knowledge work before anything is built.

**What it would take to close:** a knowledge page (K8) on regional supply cost under a national
price. It needs per-DNO-region DUoS for 2016–2025 from the published charging statements, and losses
from Elexon's published loss factors. Then measure, against that page, whether the world's regional
mix makes the book's cost per kWh move outside what one region's charges imply. Until that is
measured, nothing here is a build.

**Reversal:** set both atoms' `level_target` back to 3 and run `maturity_map_store.refile()`.

## Done

2026-10-25. The knowledge half was done and the measurement it asked for was taken from the published record:

- K8 page `site/knowledge/regional-supply-cost/` with research note
  `docs/market_research/regional_supply_cost_under_one_national_price_2026-10-25.md`. It covers per-region DUoS,
  TNUoS and BSUoS, and Ofgem's T&D loss multipliers for all 14 regions, 2016/17-2025/26, read off Ofgem Annex 3
  v1.25 and the demand-and-losses workbook v1.19.
- The lead question is answered. Transmission losses have been allocated by zone since BSC P350, live 1 April
  2018, and the cap prices losses into its regional wholesale allowance.
- **Does the world's regional mix move cost per kWh outside one region's charges?** By construction it cannot.
  The world carries one national network figure, close to the regional median, and no losses. The bigger
  result is that the missing loss uplift is national, about 9-12% of the energy line. That is filed as
  `docs/staging/SEAT_FINDING_THE_WORLD_SETTLES_METERED_KWH_AND_NO_LOSSES_SO_THE_ENERGY_LINE_IS_9_TO_12_PCT_LIGHT_2026-10-25.md`
  under W3_3, with its prediction written before any run.
- The regional spread waits on an address-to-GSP-group mapping, which is not yet sourced (note §5, §6).
