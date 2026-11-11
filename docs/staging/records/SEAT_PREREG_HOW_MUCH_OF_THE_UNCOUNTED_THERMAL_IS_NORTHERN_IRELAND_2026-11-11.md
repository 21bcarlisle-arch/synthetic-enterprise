**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

# Prediction, filed before DESNZ's regional or producer-type tables were read: how much of the ~43 TWh/yr of thermal NESO's mix does not count is Northern Ireland (2026-11-11)

**The question.** `household_carbon` §1b found Ember's UK figures carry about 43 TWh a year more thermal
generation than NESO's GB historic mix (14–19 gas, 16–19 bioenergy and waste, 10–13 other fossil). A GB
household's kWh meets GB embedded and captive thermal; it does not meet Northern Ireland's. Which is it?

**What each side counts.** NI's thermal is wholly outside NESO's mix (different system, SEM), so ALL of it
sits in the 43. GB's share of the 43 is embedded (distribution-connected) and captive (autogenerator) thermal.

**Predictions (seat's priors, no table opened):**
- P1. NI thermal generation is 4–6 TWh/yr in 2016–2022 and 3–5 TWh/yr in 2023–2025 (Ballylumford and Kilroot
  gas, Kilroot coal until 2023), i.e. 8–15% of the 43.
- P2. So GB carries at least 75% of the excess in every year. If true, the "understates by 10–25%" reading
  of §1b mostly stands, scaled down by the NI fraction.
- P3. DESNZ "other generators" (autogenerators + non-MPP) thermal, UK, is 25–40 TWh/yr, the same order as the
  GB part of the excess.
- P4. NESO's historic-mix IMPORTS column definition (data portal) includes ElecLink and Viking, so
  `OUTSIDE_NESO_MIX` is wrong for that file (right only for the Carbon Intensity API mix).

**What would refute.** NI thermal above 10 TWh/yr, or GB under 60% of the excess, refutes P1/P2 and the bound
line should be read as mostly an area-scope artefact instead.

## Result, filed after the read (same day). The predictions above are unedited.

Source: DESNZ *Regional electricity generation and supply timeseries 2004–2025* (29 Sep 2026), which splits
DUKES 5.6 / ET 5.1 by nation and producer type. Full tables: `household_carbon` §1b, "The GB/NI split, read".

- **P1 held for 2023–25 and was slightly exceeded in 2016–17.** NI thermal, all producers, net, was 6.9 / 6.6 TWh
  in 2016 / 2017, 5.6–6.3 TWh in 2018–22 and 4.7–5.2 TWh in 2023–25. As a share of the net excess it was 13–21%,
  against the predicted 8–15%.
- **P2 held.** GB is 79–87% of the excess.
- **P3 was slightly low.** GB other-generator thermal was 28–36 TWh net (29–38 gross), predicted 25–40 TWh UK.
  It closes the excess with 0.5–4 TWh to spare.
- **Unpredicted, and it matters more than the NI split.** About half of GB other-generator output is used on site by
  autogenerators and never reaches public supply. DESNZ does not split the transfer to public supply by fuel. With
  thermal reaching the grid at the all-fuel rate, the 2024 uplift is +5–8%, not the +13–25% §1b first read.
- **P4 held, decisively.** Half-hourly, NESO's IMPORTS equals the sum of ALL Elexon interconnector flows within 1 MW
  on 78–88% of half hours in 2023–25, and on 5–21% without ElecLink and Viking.
