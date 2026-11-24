**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: how often does the traded price (MID) go negative by the hour, against the day-ahead auction's published counts (2026-11-24)

**Question (electricity page GAP 3, the levy build's proxy).** A CfD's negative-hour rule tests the hourly
day-ahead price. The world holds no day-ahead series; its nearest is Elexon's MID, half-hourly and
within-day. Before a forward levy applies the rule to MID, how wrong is MID at the rule's own unit, the hour?

**What is measured, and what each count counts.** A MID hour is two settlement periods of one hour-start;
its price is the volume-weighted mean of the two (APXMIDP rows with volume > 0; an hour with neither half
traded is "no price"). A negative hour is a MID hour with price < £0 (exactly £0 is not negative, as in
the Terms). A six-hour run is ≥ 6 consecutive negative MID hours. The comparator is the published
day-ahead negative-hour count per year, held on the electricity page §3: none before 9 Dec 2019 (Argus);
29 (2022), 107 (2023), 149 (2024) (Modo); 139 (2024), 149 (2025) (Montel, EPEX); 141, 190 (Electricity
Maps). These are counts of different auctions [press]; the ratio uses the lowest and highest per year.
This is a count-level comparison only. Which hours match cannot be measured without the auction series.

**Data.** `sim/cache/elexon_mid_full.json` (2016-09 to 2020) and the seat-executor caches
`elexon_mid_2021_2023.json`, `elexon_mid_2024_2025.json`, the same files the power grade read.

**Predictions, filed before the probe runs** (priors from the power grade's half-hour counts,
133 / 428 / 495 in 2022-24):

- P1. MID negative hours ÷ published day-ahead negative hours is ≥ 1.5 in each of 2022, 2023 and 2024,
  against every published count for the year.
- P2. For 2023 and 2024 that ratio lies in [1.5, 3.5].
- P3. 2017 and 2018 together have ≥ 10 MID negative hours, where the day-ahead auction had none.
- P4. In 2023-24, at most half of MID's negative hours lie inside six-hour runs.
- P5. MID has a price in ≥ 99% of hours in every full year 2017-2024.

**Decision rule.** (a) If P1 holds, MID is not a usable unadjusted proxy for the rule: GAP 3 records the
measured ratio, and the forward levy must either source the day-ahead auction or carry the ratio as its
stated error. (b) If the ratio sits in [0.8, 1.25] every year 2022-24, MID is usable at the count level,
with hour matching still a GAP. (c) Otherwise the ratio is recorded and no rule is chosen.

Nothing in `sim/`, `company/` or `saas/` changes.
