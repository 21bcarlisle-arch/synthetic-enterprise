# HadUK-Grid as the weather source for household heat-load cells — phase 1 pull

**Status:** source established and validated; the derivation it feeds is not yet done.
**Ruling:** `docs/staging/DIRECTOR_RULING_WEATHER_CELLS_HEAT_LOAD_SEGMENTATION_PHASE1_2026-09-05.md`
**Opened:** 2026-09-05. **Puller:** `tools/fetch_haduk_grid.py`.
**Receipt (machine-readable):** `docs/market_research/haduk_grid_pull_receipt.json`.

This is the working research doc for the data side of phase 1. It records what was pulled,
what the pull proves, and — more usefully for whoever picks this up — the four places where
the data forces a choice that has not been made yet.

---

## 1. The source

| | |
|---|---|
| Dataset | Met Office HadUK-Grid, gridded land-surface observations |
| Version | `v1.3.2.ceda` (June 2026 release, record to end-2025) |
| Release directory | `v20260512`, pinned in the puller |
| Resolution | 1 km |
| Projection | OSGB36 British National Grid (transverse Mercator, central meridian −2°) |
| Grid | 900 × 1450 cells; **245,077 are land** |
| Licence | Open Government Licence v3.0 |
| Host | CEDA Archive (`dap.ceda.ac.uk`), token-authenticated |
| Refresh | **Annual.** HadUK is a once-a-year release; `RELEASE` in the puller moves when the next lands, and the whole pull is re-run. |

Raw grids stay on this machine at `~/.cache/synthetic-enterprise/haduk_grid/` and never enter
the repo — roughly 20 GB. Only the receipt, and later the derived cell definitions and chart
data, are committed.

### What was pulled

| Tier | Content | Files | Purpose |
|---|---|---|---|
| `normals` | `tas`, `sfcWind`, `sun` — 1991–2020 30-year monthly normals | 3 | the **level** half of the question |
| `monthly` | `tas`, `sfcWind`, `sun` — monthly series 1991–2025 | 105 | **shape**, interannual spread, cross-cell synchrony |
| `daily` | `tas` — daily, heating season (Oct–Mar) 1991–2025 | 210 | **persistence** (cold-spell length) |

1991–2020 is the WMO standard normal and also the newest normal every phase-1 variable can
support: `sfcWind`'s record starts in 1969, against 1884 for `tas` and 1910 for `sun`. The
series window starts at 1991 to match.

---

## 2. What the pull proves

The three normals were opened and read before anything was built on them. GB+NI land-cell
unweighted monthly means, 1991–2020:

| Month | J | F | M | A | M | J | J | A | S | O | N | D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Mean air temperature (°C) | 3.9 | 4.1 | 5.7 | 7.9 | 10.6 | 13.3 | 15.3 | 15.1 | 12.9 | 9.7 | 6.5 | 4.2 |
| Wind speed at 10 m (m/s) | 5.6 | 5.5 | 5.3 | 4.8 | 4.5 | 4.2 | 4.1 | 4.1 | 4.3 | 4.8 | 5.0 | 5.2 |
| Sunshine (hours) | 47 | 72 | 109 | 155 | 192 | 172 | 173 | 162 | 128 | 92 | 58 | 43 |

Annual unweighted mean temperature **9.12 °C**; annual sunshine total **1,403 hours**; full
temperature range across cells and months −3.17 °C to 19.27 °C. Winter wind is a third higher
than summer wind, and it is highest in exactly the months temperature is lowest — the
positive winter temperature/wind coupling the ruling's expected-shape block predicts is
visible in the national means before any clustering is done.

These are internally coherent and of the right order for the UK. **They have not yet been
cross-checked against the Met Office's own published UK averages**, which is a different and
stronger test than "looks about right", and it is not done. Nor has the independent
validation the ruling requires — DESNZ sub-national gas consumption, checking that the
derived cells explain real heat demand rather than merely weather. Both are open.

---

## 3. Where the data forces a choice

These are the "one or two places where the data forced a choice" the ruling asks to be
reported. There are four, none of them yet decided, all of them Choice-class claims for the
knowledge page.

### 3.1 There is no irradiance product — only sunshine duration

The ruling anticipated this and it is confirmed: HadUK's `sun` variable is **Sunshine hours**
(`units: hour`), and the 1 km archive publishes no global irradiance. Solar gain and PV yield
both need irradiance (W/m² or kWh/m²), so something has to bridge the two.

The options are a duration→irradiance conversion (Ångström–Prescott is the classical form,
and its coefficients are latitude- and climate-specific — the coefficients are the exposure
here, not the formula), or a second gridded source with direct irradiance, at which point the
weather anchor is no longer single. **Not decided.** Whichever is chosen must be registered as
a Choice with its source and its rejected alternative named; the puller deliberately does not
convert, because a pull that quietly converts is a pull that fabricates.

### 3.2 Northern Ireland is in the grid, and the household weights are what removes it

HadUK is a **UK** product. 14,565 of the 245,077 land cells fall inside Northern Ireland
(lon −8.17 to −5.43, lat 54.03 to 55.45 — consistent with NI's ~14,100 km²). The ruling is
GB-only: NI is a separate energy market.

The useful observation is that **no explicit geographic mask is needed, and drawing one would
be the worse option**. Household weights come from the England & Wales 2021 and Scotland 2022
censuses, which by construction have no NI postcodes. Weight by households and NI cells take
weight zero automatically — the GB boundary arrives from the same place as the weighting,
rather than from a bounding box somebody drew, which would also clip parts of western
Scotland. This should be *asserted* in the analysis (NI cells carry zero weight), not assumed,
because it is the kind of thing that is true until the weighting changes.

### 3.3 Wind and sunshine have no daily product; temperature does

`tas` publishes `day/`; `sfcWind` and `sun` publish monthly and coarser only. So persistence
in phase 1 is necessarily *temperature* persistence. "Cold and still" — the condition that
actually drives peak heat load — cannot be measured at daily resolution from this source at
all. That is a real limit on the ruling's §2.4 persistence question and it should be stated on
the page rather than absorbed: what we can measure is how long cold spells last, not how often
cold coincides with still.

### 3.4 The daily pull is the heating season only

`HEATING_SEASON_MONTHS = Oct–Mar`, a stated economy: it halves a 15 GB tier and forecloses
summer-persistence questions, which belong to phase 2 (summer load) rather than phase 1. If
phase 2 opens, the daily tier widens and re-runs; the puller is resumable, so that costs only
the new files.

**The unit of coverage is the SEASON, not the file.** A heating season straddles the new year,
so a count of daily files — or a directory listing ordered by calendar year — cannot be read
for it. Fifteen daily files is "two and a half winters", and a cold spell that begins in
December and ends in January is one spell that a calendar year cuts in half. Since the ruling's
§2.4 subject is precisely how long a spell lasts, the file count is the wrong number to publish
and the seasonal count is the right one.

The receipt therefore carries a `daily_heating_seasons` block stating the complete-season count
with its first and last, and a **gap row per incomplete season naming the missing months and
why**. Two of those gaps are structural and permanent rather than defects to chase:

| Season | What is missing | Why |
|---|---|---|
| 1990/91 | Oct–Dec 1990 | before `SERIES_FIRST_YEAR` (1991, set by the 1991–2020 normal) |
| 2025/26 | Jan–Mar 2026 | after `SERIES_LAST_YEAR` (2025, the archive's last complete year) |

So a complete 1991–2025 daily pull yields **34 complete Oct–Mar seasons (1991/92 … 2024/25)**
plus those two half-seasons. Any *other* gap row is a real absence — a file the archive refused
— and carries the fetch status that caused it.

---

## 4. The token: the ruling's premise no longer holds

The ruling recorded CEDA's token-minting API (`https://services.ceda.ac.uk/api/token/create/`)
returning **500** for this account with correct credentials, told us to fall back to the
hand-made `CEDA_TOKEN`, and reserved an NTFY to the director for a fresh token if it expired
mid-pull.

**As of 2026-09-05 that API returns 200.** The puller mints its own token and re-mints when
the current one is within ten minutes of expiry.

This matters beyond convenience. Minted tokens last three days; the pull takes hours but is
resumed across days, and the annual refresh will be run by a session that has no director
attention on it at all. Under the fallback the pull had a hard three-day fuse and a manual
step at the end of it. It now has neither, and **the reserved NTFY is no longer expected to
fire** — the puller still raises it, but only when minting itself fails *and* the fallback
token is spent, which is the case the director actually wanted to be told about.

---

## 5. What is established, and what is not

**Established:** the source, its version, its licence, its grid, its coverage, its units, and
that the three phase-1 variables read correctly and cohere at national scale. The pull is
reproducible from a pinned release directory with a per-file sha256 receipt.

**Not established, and not to be quoted as if it were:** the number of cells that captures 90 /
95 / 99 % of household-weighted variation; how well LDZ, GSP and SAP-21 approximate them;
cold-spell persistence and cross-cell synchrony per cell; the elevation correction to house
height (Ordnance Survey terrain data — not yet pulled); the census household weights by
postcode (not yet pulled); and the DESNZ gas-consumption validation. The curve the director
asked for does not exist yet. Nothing above should be read as a step toward it beyond having
made it possible to compute.

---

## 6. Reproducing the pull

```bash
python3 -m tools.fetch_haduk_grid --manifest-only --tiers normals,monthly,daily  # no creds needed
python3 -m tools.fetch_haduk_grid --tiers normals --verify --receipt
python3 -m tools.fetch_haduk_grid --tiers monthly,daily --verify --receipt
```

Resumable and idempotent: a file already on disk at the archive's declared byte count is
skipped, a part-file resumes by HTTP range, and the receipt merges across runs rather than
being replaced by the last tier pulled. Credentials at
`~/.config/synthetic-enterprise/.env.ceda`.
