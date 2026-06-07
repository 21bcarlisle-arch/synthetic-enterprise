# Elexon Insights Solution — API reference notes

Ground truth for the real endpoint shapes this project depends on, kept here
so that local-model delegation starts from confirmed fact rather than
guessing. Confirmed by direct probing on 2026-06-07; verify against
data.elexon.co.uk if behaviour seems to drift.

- **Base URL:** `https://data.elexon.co.uk/bmrs/api/v1`
- **Auth:** none — key-free public REST API
- **No `/latest` shortcuts.** Settlement data is published per-date with a
  delay; "the most recent record" must be derived by querying a date and
  picking the entry with the highest `settlementPeriod`, falling back to the
  previous day if the requested date has no data yet.

## System Sell Price / System Buy Price (SSP/SBP)

```
GET /balancing/settlement/system-prices/{settlementDate}
```

- `settlementDate` — `YYYY-MM-DD`
- Returns `{"metadata": {...}, "data": [...]}`, where `data` is an array of
  per-settlement-period records (up to 48 per day — half-hourly periods)
- Relevant fields per record: `settlementDate`, `settlementPeriod`,
  `startTime`, `systemSellPrice`, `systemBuyPrice`, `netImbalanceVolume`,
  `priceDerivationCode`, plus various accepted offer/bid/adjustment volumes
- Dataset code in metadata: `DISEBSP`

Example record shape (values illustrative, not to be treated as current):

```json
{
  "settlementDate": "2026-06-07",
  "settlementPeriod": 32,
  "startTime": "2026-06-07T14:30:00Z",
  "systemSellPrice": -14.14,
  "systemBuyPrice": -14.14,
  "netImbalanceVolume": -834.49,
  "priceDerivationCode": "N"
}
```

## Known wrong guesses (don't repeat)

- `/systemprices/latest` — **does not exist**, returns HTTP 404. A local
  model guessed this on first attempt; it's a plausible-looking but
  fabricated shortcut. There is no "latest" endpoint on this API.

## Implementation

See [`sim/system_prices.py`](../../sim/system_prices.py) for the working
retrieval function (`get_latest_system_prices()`).
