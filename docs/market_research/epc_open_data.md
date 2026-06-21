# UK EPC Open Data — Research Findings

## Portal and Access

- **URL:** https://get-energy-performance-data.communities.gov.uk/  
  (old `epc.opendatacommunities.org` retired 30 May 2026; all URLs redirect here)
- **Authentication:** Free GOV.UK One Login account required for bulk download
- **API:** REST/OpenAPI v3, no 10k cap, full pagination supported

## Download Options

- Full domestic bulk ZIP: ~5.6 GB (all ~29.2M certificates, England & Wales)
- County-level ZIPs: useful for development/testing
- Monthly incremental files (last 12 months) + annual files back to 2008
- Each ZIP: one or more CSVs + `schema.json` + `columns.csv` data dictionary

## Coverage

- **Domestic:** ~29.2M certificates (Oct 2008 to Mar 2026); ~400k new/quarter
- **Non-domestic:** ~2M certificates (small — many SMEs have no EPC at all)
- **Geography:** England and Wales only (Scotland: scottishepcregister.org.uk; NI separate)
- **Housing stock:** ~60% of English stock covered; biased toward transacting properties
  (privately rented > owner-occupied; old/unsold stock under-represented)
- Certificates expire after 10 years — filter by `LODGEMENT_DATE` recency

## Key Fields for Consumption Modeling

### Domestic CSV

| Field | Description |
|-------|-------------|
| `PROPERTY_TYPE` | house, flat, maisonette, bungalow, park home |
| `BUILT_FORM` | detached, semi-detached, terraced, enclosed terraced |
| `TOTAL_FLOOR_AREA` | m², internal face of external walls |
| `CURRENT_ENERGY_RATING` | A–G letter rating |
| `CURRENT_ENERGY_EFFICIENCY` | SAP points 1–100 |
| `ENERGY_CONSUMPTION_CURRENT` | **kWh/m²/year** (total: heat + hot water + lighting) |
| `MAINS_GAS_FLAG` | Y/N — whether mains gas connection exists |
| `MAIN_FUEL` | mains gas / electricity / oil / etc. |
| `MAINHEAT_DESCRIPTION` | e.g. "boiler and radiators, mains gas" |
| `CONSTRUCTION_AGE_BAND` | e.g. "1967-1975", "2007 onwards" |
| `NUMBER_HABITABLE_ROOMS` | excludes kitchens, bathrooms, hallways |
| `WALLS_DESCRIPTION` | construction + insulation status |
| `POSTCODE` | for regional calibration |

**Total annual kWh = `ENERGY_CONSUMPTION_CURRENT` × `TOTAL_FLOOR_AREA`**

### Non-Domestic CSV (SME proxy)

| Field | Description |
|-------|-------------|
| `ASSET_RATING` | A–G rating |
| `FLOOR_AREA` | m² |
| `MAIN_HEATING_FUEL` | gas / electricity / oil |
| `BUILDING_ENVIRONMENT` | heating only / air con / etc. |

## Electricity vs Gas Split (No Separate Column)

EPC does NOT publish separate kWh for electricity and gas. Approach:
- **Gas-heated property** (`MAIN_FUEL = mains gas`): ~80% gas (heat + hot water), ~20% electricity (lighting + appliances)
- **All-electric property**: 100% electricity
- **Off-grid** (`MAINS_GAS_FLAG = N`): likely oil or heat pump; treat as electricity-only for sim purposes

This is a SAP methodology heuristic — the 80/20 split varies by property type and efficiency rating.

## Critical Caveat: EPC Overpredicts Metered Consumption

Published research (ScienceDirect 2023) shows EPC primary energy estimates are **50–100% higher** than metered billing consumption. SAP uses standard occupancy and doesn't model actual behaviour. 

**Apply 0.6–0.7 correction factor** to `ENERGY_CONSUMPTION_CURRENT` when calibrating against billing kWh.

## Proposed Integration with Simulation

Replace fixed customer kWh/year constants (C1–C9) with EPC-derived distributions:

1. Download full domestic CSV; filter to valid `TOTAL_FLOOR_AREA` and `ENERGY_CONSUMPTION_CURRENT`; deduplicate by UPRN keeping most recent `LODGEMENT_DATE`
2. Group by `PROPERTY_TYPE` × `CURRENT_ENERGY_RATING` × `MAIN_FUEL`
3. For each customer segment, compute percentile distributions of `TOTAL_FLOOR_AREA` and `ENERGY_CONSUMPTION_CURRENT`
4. At simulation customer creation: sample property segment → draw floor area → compute annual kWh with 0.65 correction factor → split electricity/gas by main fuel
5. For SME (C5, C7-C9): use non-domestic CSV filtered to `FLOOR_AREA < 500 m²`

### Current vs Target Customer kWh Profile

| Customer | Current kWh/yr | EPC-calibrated target |
|----------|----------------|-----------------------|
| C1 (resi, flat) | ~2,800 elec | Band D flat, ~60 m²: ~2,400 elec |
| C2 (resi, semi) | ~3,500 elec | Band D semi, ~90 m²: ~3,100 elec |
| C3 (resi, detached) | ~4,500 elec | Band C detached, ~120 m²: ~3,800 elec |
| C4 (resi, terrace) | ~3,200 elec | Band D terrace, ~80 m²: ~2,800 elec |
| C5 (SME, small office) | ~15,000 elec | Non-dom Band D, ~150 m²: ~12,000 elec |
| C6 (SME, med office) | ~45,000 elec | Non-dom Band C, ~400 m²: ~35,000 elec |
| C7-C9 (HH, large SME) | ~80,000 elec | Non-dom Band D, ~700 m²: ~55,000 elec |

Gas customers (C1g-C9g): multiply electricity estimate by ~4 (gas dominates heating).

## Licensing

- Non-address fields: Open Government Licence v3.0 (freely usable commercially)
- Address fields: sub-licensed from OS/Royal Mail (energy-efficiency purposes only — not a constraint for simulation use)

## Sources

- https://get-energy-performance-data.communities.gov.uk/
- https://www.data.gov.uk/dataset/020403de-af6a-49a2-ae06-3b3a7eff4b97/
- https://mhclgdigital.blog.gov.uk/2024/01/29/changes-to-the-energy-performance-certificates-open-data-service/
