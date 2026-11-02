# National Gas Transmission: daily calorific value per charging area (LDZ), every published version

- **Source:** National Gas Transmission data portal, Find Gas Data, folder "Calorific Value", items
  "Calorific Value, LDZ(XX)" PUBOB4507 to PUBOB4519 (EA, EM, NO, NE, NT, NW, SC, SE, SO, SW, WM, WN, WS).
  Download endpoint `https://data.nationalgas.com/api/find-gas-data-download` with `dateType=GASDAY`,
  `applicableFor=Y`, `latestFlag=N` (all versions), `type=CSV`, one request per item per calendar year.
- **Retrieved:** 2026-11-02, by the delivery seat, with `python3 -m tools.fetch_national_gas_ldz_cv`.
  SHA-256 of the file as written: `42963ad0ef475a622d8df101124773d618babccfc29fa70357565766bccd5fd0`
  (gzip stamps its own time, so a re-fetch of identical rows hashes differently).
- **Licence:** the portal's published operational data; National Gas states its data portal content may be
  reused with attribution. Not personal data (W11): one value per charging area per gas day.
- **What is here:** `ldz_daily_cv.csv.gz`, 53,749 rows: `ldz`, `gas_day`, `cv_mj_per_m3`, `published_at`
  (the portal's "Applicable At", ISO). Every version the portal returns, not only the latest: a gas day
  is published at about 10:30 on the day, again at about 10:30 the day after, often at 16:00, and some
  are republished months later. Gas days 1 Nov 2021 to 31 Dec 2025, every one present for all 13 areas.
- **What is not here (GAP):** 2016-01-01 to 2021-10-31. The same request for any earlier window returns an
  empty body (probed 2026-11-02 for these items and for PUBOB624 and PUBOB3700, which are equally empty
  before Nov 2021). Whether National Gas or Xoserve hold the earlier series in another form was not found.
- **Not established:** which version is the one a supplier must bill at, and what the runs of exactly 38.0
  are (131 of SC's 1,522 final values, 108 of WS's, against almost none at 38.1-38.8). See G1 and G7 of
  `docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md`.
- **Read by:** `sim/ldz_calorific_value.py` only. The company receives what was published by a moment through
  `company.billing.gas_volume_conversion.CalorificValueFeed`, never this file (W6).
