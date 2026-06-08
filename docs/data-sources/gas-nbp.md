# Gas Data Reference — NBP Wholesale Prices & AQ/CV Conversion

> Ground truth for the gas data pipeline. Do not research these — use exactly what follows.

## NBP Historical Price Data

**Primary programmatic source:** NGT MIPI API
- Endpoint: https://mipidata.nationalgas.com/api
- Format: JSON or XML
- Key fields: `ApplicableFor` (gas day), `Value` (price in p/kWh), `DataItemName`
- Price series to use: System Average Price (SAP) — the ex-post day-ahead equivalent, highly correlated to NBP day-ahead

**Secondary source (manual CSV, no API):** Ofgem Wholesale Market Indicators
- Format: CSV, fields: Date (DD/MM/YYYY), Price (p/therm or £/MWh)
- Use only if MIPI API is unavailable or incomplete

**Do NOT use:** NESO CKAN portal (api.neso.energy) — contains electricity data only. NGT MIPI is the correct gas operator system.

**Do NOT use:** ICE — paywalled, requires commercial subscription.

## AQ (Annualised Quantity) for Gas

AQ is derived from historical meter reads, not a published regional default table.
- Calculated by Xoserve from measured consumption between valid meter readings
- Weather-corrected using Annual Load Profile (ALP) and Daily Adjustment Factor (DAF) mapped to the supply point's End User Category (EUC)
- Recalculated monthly on a rolling basis when a valid read is submitted

**For simulation:** use a fixed synthetic AQ per customer (same as EAC for electricity). Weather-driven AQ adjustment is a future phase item. Store AQ as a nullable field — do not hardcode.

## CV Conversion Formula (m³ to kWh)

```
kWh = V × CF × CV / 3.6
```

Where:
- `V` = consumed volume in m³ (if imperial meter in hcf, multiply reads by 2.83 first)
- `CF` = Volume Correction Factor = **1.02264** (standard UK legal value, corrects for 15°C / 1013.25 mbar)
- `CV` = Calorific Value in MJ/m³ — fluctuates daily between ~37.5 and ~43.0; provided by National Gas per Local Distribution Zone (LDZ)
- `3.6` = conversion constant MJ → kWh

**For simulation:** use CV = 39.5 MJ/m³ as a fixed assumption initially. CV varies by LDZ and date — store as a configurable field, not a hardcoded constant. Open door for LDZ-specific CV later.

## Licence
MIPI data: publicly accessible, no registration required for basic access. Verify licence terms before any commercial use.
