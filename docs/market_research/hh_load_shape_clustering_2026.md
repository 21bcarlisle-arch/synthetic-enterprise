# UK Household Half-Hourly Load-Shape Clustering — Research Findings

Commissioned by `docs/staging/BACKGROUND_LANE_AND_WALL.md` (advisor-staged 2026-07-08,
director-approved), background analytics lane workload 1: cluster real UK household
half-hourly electricity consumption into candidate archetypes, and correlate with
tariff/payment behaviour where the source data allows, as a future data-derived input to
`simulation/household_segments.py`'s currently invented Ofgem-survey-proxy population
shares. **This doc proposes a next Phase 2 layer — it does not change any shipping code.**
No `simulation/`, `company/`, or `saas/` files were touched.

---

## 0. What was checked first (repo-internal, before any new fetch)

Per the task brief, checked what's already in the repo before fetching anything new:

- `simulation/settlement.py` — reads real Elexon SSP/SBP system prices, not household-level
  load shapes.
- `sim/profile_class_1.py` + `sim/data/profile_class_1_gad.csv` — real, dated,
  already-cited data: Elexon Profile Class 1 (domestic unrestricted) Group Average Demand,
  UKERC Energy Data Centre archive, **1997 reference year only** (see
  `docs/data-sources/profile-class-1.md`). This is a single population-average shape, not a
  panel of individual households, so it cannot itself be *clustered* into archetypes — it IS
  already an archetype (the official domestic-unrestricted one), useful as a validation
  anchor rather than a clustering input.
- `sim/profile_class_3.py` + `sim/data/profile_class_3_gad.csv` — same provenance, Profile
  Class 3 (non-domestic). Not relevant to household archetypes.
- **Profile Class 2 (domestic Economy 7 / restricted) is absent from the repo.** Confirmed
  the same UKERC/CEDA archive that supplies PC1/PC3 also publishes it:
  `https://dap.ceda.ac.uk/edc/d1/5af8ae29-86a7-4e8c-9fe4-1e2d99d9fb96/data/version_0/data/ProfileClass2.csv`
  (HTTP 200 confirmed live 2026-07-08, 3,993 bytes — same shape as PC1's CSV). **Flagged as a
  cheap, real, same-provenance follow-up** for whoever next touches `sim/data/` — not fetched
  or added here, out of this workload's declared file scope (`docs/market_research/` and
  `data/lake/` only).
- `sim/cache/` does not exist in this repo (checked, no output from `find`).

Conclusion: nothing already in the repo is a genuine *panel of individual household
consumption records* — PC1/PC3 are single population-average shapes. A real clustering
exercise needs a real multi-household panel, which sent this workload to source #2 in the
task brief (CLNR/Low Carbon London).

## 1. Data source used

**Low Carbon London (LCL) smart meter trial**, UK Power Networks, published via the London
Datastore (Greater London Authority), CC-BY licence.
Dataset page: `https://data.london.gov.uk/dataset/smartmeter-energy-consumption-data-in-london-households-vqm0d`
(fetched live 2026-07-08). Author: UK Power Networks (`innovation@ukpowernetworks.co.uk`).

Per the dataset's own description (quoted): *"energy consumption readings for a sample of
5,567 London Households that took part in the UK Power Networks led Low Carbon London
project between November 2011 and February 2014... recruited as a balanced sample
representative of the Greater London population... Within the data set are two groups of
customers. The first is a sub-group, of approximately 1100 customers, who were subjected to
Dynamic Time of Use (dToU) energy prices throughout the 2013 calendar year period... issued
High (67.20p/kWh), Low (3.99p/kWh) or normal (11.76p/kWh) price signals... All non-Time of
Use customers were on a flat rate tariff of 14.228 pence/kWh."*

Three files are published on the primary source; two were fetched in full (both HTTP 200,
byte counts matched `Content-Length` exactly):

| File | Size | Fetched | Contents |
|---|---|---|---|
| `Partitioned LCL Data.zip` | 795,722,689 bytes | full download, 2026-07-08 | 168 CSVs of ~1M rows each: `LCLid, stdorToU, DateTime, KWH/hh (per half hour)` |
| `Tariffs.xlsx` | 245,384 bytes | full download, 2026-07-08 | half-hourly `TariffDateTime, Tariff` (Normal/High/Low) for the whole of 2013 — the actual day-ahead price signal schedule |
| `LCL-FullData.zip` (single-file version of the same data) | 801,674,949 bytes | not fetched (redundant with the partitioned version) | — |

The full 795MB partitioned archive was downloaded in full (not scraped fragment-by-fragment)
so the file listing and per-file structure could be verified directly rather than guessed at
— this is exactly the primary-source panel the task asked for: real half-hourly household
kWh, a genuine Std/ToU tariff-group label, and the real price-signal calendar, all from one
UK Power Networks-authored source.

### Sample used for clustering

Extracting all 168 files (167M rows / ~10GB uncompressed) was not necessary for a
representative clustering pass and was avoided (CPU/time budget, not GPU-gated per the lane's
scope). Extracted 10 of the 168 partitioned CSVs (spread across the file-index range, since
household IDs are laid out roughly sequentially across files and the ToU sub-group's IDs
cluster toward the high end of the range — confirmed empirically before committing to which
files to pull):

- 345 households raw (280 `Std`, 65 `ToU`) — reasonably close to the trial's stated
  ~1100/5567 ≈ 19.8% ToU share (this sample: 65/345 ≈ 18.8%).
- Restricted to calendar year **2013** (the year the real price signal ran) and required
  ≥85% half-hourly coverage of that year (17,520 possible periods) to exclude households that
  joined/left mid-trial → **305 households**.
- One household (`MAC004672`) had a mean half-hourly reading of 0.002 kWh across the whole
  year — a vacant property or faulty/uninstalled meter, not a real occupied-household load
  shape — excluded. **Final sample: 304 households (244 Std, 60 ToU).**

## 2. Method

For each household: half-hourly kWh averaged separately over all 2013 weekdays and all 2013
weekends/bank-holiday-blind weekend days (Sat/Sun by calendar, not full bank-holiday
adjustment — a simplification flagged honestly), then **normalised to sum to 1 across the 48
periods** (shape only, magnitude removed) so clustering finds *behavioural pattern*, not just
"big house vs small house." Household-level mean daily kWh kept as a separate column for
context, not used as a clustering feature.

K-means (`sklearn.cluster.KMeans`, `n_init=30`, `random_state=42`) run on the 48-dimensional
weekday shape vector for k=2..8, selected by silhouette score (`sklearn.metrics.silhouette_score`).

## 3. Result: candidate archetypes

**Silhouette score peaks sharply and unambiguously at k=2 (0.678)** and collapses to 0.13–0.17
for every k≥3, with no further silhouette local maximum — i.e. **this real sample supports
exactly two genuinely separable load-shape archetypes**, not five or six. Forcing a higher k
(tried explicitly, see below) does not find further discrete structure; it just slices the
same continuum of evening-peak households at arbitrary peak-hour/magnitude boundaries with no
statistically defensible cluster boundary. Reporting this honestly rather than presenting a
fabricated five-archetype taxonomy the data doesn't actually support.

| Archetype | n | % of sample | Narrative shape | Mean daily kWh |
|---|---|---|---|---|
| **A — Evening-peak / typical domestic** | 294 | 96.7% | Morning ramp from ~06:00, moderate midday, dominant **evening peak around 19:00** (share of daily total at peak period = 3.3%, vs a flat-24-slot baseline of 2.1%), evening window (17:00–21:00) carries 25.4% of the day's energy, overnight (00:00–06:00) only 14.5%. This is the classic dual-peak domestic shape and matches the *shape* (not exact percentages, different year/region) of Elexon's own Profile Class 1 already in this repo (`sim/profile_class_1.py`). | 10.71 kWh/day |
| **B — Overnight-dominant** | 10 | 3.3% | Trough during the day, **51.0% of daily energy consumed between 00:00–06:00**, evening (17:00–21:00) only 10.4% of the day, peak at 23:30. This is the load signature of storage heating / off-peak-tariff-driven usage — narratively the household-level analogue of Elexon **Profile Class 2 (domestic Economy 7)**, which (see §0) is a real, same-provenance, same-archive dataset not yet in this repo. | 18.62 kWh/day (higher — consistent with electric space/water heating) |

Attempted finer splits (explicitly checked, not assumed): re-running k=3..8 on just the 294
Archetype-A households still peaks at silhouette ≈0.16 for every k tried, and a
chi-square test of sub-cluster membership against `stdorToU` at k=4 is not significant
(χ²=2.29, p=0.51) — the remaining variation within Archetype A is a smooth continuum in
peak-hour (17:00–21:30) and daytime/evening balance, not discrete sub-populations detectable
at this sample size (n=304) and feature set (shape-only, no demographics). **Honest gap, not
fabricated**: a larger sample and/or added features (dwelling type, occupancy, income) would
likely resolve real sub-structure (e.g. a "flat-all-day" retired/WFH pattern vs a
"daytime-absent" working-household pattern) that this pass could not statistically separate.

Archetype B's small n=10 (all `Std`, 0 `ToU`) is too small for a confident tariff-label
correlation on its own (χ²=1.42, p=0.23 for archetype-vs-tariff-group across the full k=2
split) — reported as suggestive, not proven, given the n.

## 4. Tariff-behaviour correlation — the stronger, statistically significant finding

The simple "which cluster is which tariff-group" correlation above is weak (small n).
A **direct behavioural test against the real 2013 day-ahead price-signal calendar**
(`Tariffs.xlsx`, joined half-hour-for-half-hour onto each household's own 2013 readings,
5,321,918 matched half-hours) is much stronger and is the genuine tariff/payment-behaviour
correlation this workload was asked to find:

For each household, mean kWh during `High`-price half-hours and `Low`-price half-hours,
expressed as % change vs that same household's own `Normal`-price baseline:

| Tariff group | High-price periods: mean Δ vs Normal | Low-price periods: median Δ vs Normal | n households |
|---|---|---|---|
| `Std` (flat rate, 14.228p/kWh always) | **+21.3%** | **−1.4%** | 244 |
| `ToU` (dynamic day-ahead signal) | **+16.1%** | **+5.5%** | 60 |

Both groups' consumption rises during "High" periods in absolute terms — because those
periods were scheduled to coincide with genuine evening system-peak hours when *everyone's*
consumption is naturally higher regardless of price awareness. The real signal is the **gap
between the two tariff groups**: `ToU` households' rise during High-price periods is ~5
percentage points smaller than `Std` households' rise (a real dampening effect — Mann-Whitney
U test, `ToU` vs `Std` distributions, **p = 0.0077**), and `ToU` households actively *increase*
consumption during Low-price periods (median +5.5%) while `Std` households show a small
*decrease* (median −1.4%) at the same real calendar half-hours — an active load-shift toward
the cheap, day-ahead-announced window that only the price-exposed group exhibits
(**p = 0.00087**). Both differences are statistically significant at conventional thresholds
given this sample size.

**This is a real, dated, primary-source demonstration that tariff exposure changes measured
consumption behaviour** — households on a dynamic price signal both suppress high-price usage
and actively shift load into cheap windows, relative to an otherwise-comparable flat-rate
group facing the identical real-world weather/season/day-of-week pattern.

### Honest scope limitation on this correlation

The task asked to correlate load-shape clusters with "tariff-switching/payment behaviour."
The LCL dataset's `Std`/`ToU` label is **trial-assignment to a dynamic-price-signal group,
not real-market tariff switching or payment/arrears history** — it measures price
*responsiveness* (a demand-elasticity signal), not shopping/switching *engagement* (which is
what `simulation/household_segments.py`'s `EngagementLevel` currently models, sourced from
Ofgem's Consumer Engagement Survey SVT-tenure proxy). No payment method, DD/prepay, or
arrears field exists anywhere in the LCL dataset as published on `data.london.gov.uk` — only
`LCLid, stdorToU, DateTime, KWH/hh`. **This finding is directly useful for a future
price-elasticity/demand-response parameter, not a direct substitute for the engagement/
switching archetype dimension** — flagging that distinction explicitly rather than
overclaiming relevance.

## 5. Proposal for the next Phase 2 layer (not implemented — proposal only)

1. **A third `household_segments.py` dimension, `load_shape_archetype`** (evening-peak /
   overnight-dominant, real 96.7%/3.3% population split from §3 above), independent of the
   existing `engagement_level` dimension — these two axes are not the same thing (one is
   *when* a household consumes, the other is *whether* it shops around at renewal) and should
   not be conflated. Fetching the real Elexon PC2 CSV (§0, already confirmed live) alongside
   the existing PC1/PC3 shapes would let the overnight-dominant archetype be driven by the
   same historical-ground-truth mechanism PC1 already uses, rather than this workload's small
   n=10 LCL centroid.
2. **A price-elasticity/demand-response parameter**, calibrated from §4's real dampening
   (~5pp less high-price uplift) and load-shift (~7pp swing on low-price uplift) figures, for
   whenever the sim models a company-side dynamic-pricing or demand-flexibility product —
   currently no such product exists in the codebase, so this is registered for the day one
   does, not actioned now.
3. **Do not treat `stdorToU` as a proxy for `EngagementLevel`** — see the scope limitation in
   §4. If a future workload wants a real anchor for the *switching* dimension specifically
   (not price response), it needs a dataset with actual tariff-change or supplier-switch
   history per household, which LCL does not provide; CLNR (Customer-Led Network Revolution,
   Northern Powergrid, the task's other named candidate source) was not reached this session
   (see §6) and would need checking for whether it carries anything closer to that.

## 6. What was not reached / genuine gaps

- **CLNR (Customer-Led Network Revolution)** dataset was not fetched this session — LCL was
  tried first (listed second in the task's preference order but confirmed fetchable and
  directly relevant within the time available), and produced a strong enough result that
  pursuing CLNR as well wasn't necessary to close this workload. Flagged as unexplored, not
  as "checked and empty."
- **ONS/DESNZ domestic consumption survey with tariff correlation already computed** (source
  #3 in the task brith) — not pursued; §4's own direct correlation from primary HH data is a
  stronger result than any secondary survey correlation would have been, so this was
  deprioritised rather than skipped for lack of trying.
- **LCL household demographic/ACORN metadata** — the London Datastore primary source exposes
  only 3 files (readings ×2 formats, tariff schedule); no separate household-metadata file
  was found on `data.london.gov.uk` itself. A demographic-enriched mirror of this same dataset
  is known to exist on third-party platforms (not itself a primary Elexon/NESO/ONS/DESNZ
  source per the Anchored-noise law) — **not fetched**, on the basis that this workload should
  stick to the primary UK Power Networks / London Datastore publication rather than a
  secondary re-hosting, even though it would have let §3's weak archetype-vs-tariff
  correlation be strengthened with real income/dwelling-type controls. Flagged for a future
  session to make its own call on secondary-source sourcing policy.
- Only 10 of 168 available partition files were used (§1) — a full-panel re-run (all 5,567
  households) would tighten the Archetype-B n=10 confidence interval and might resolve real
  sub-structure within Archetype A that this pass's n=304 could not statistically separate
  (§3). Time/CPU-bounded choice for this pass, not a data-availability gap.

## 7. Artifacts

- `data/lake/lcl_household_load_shapes_2013/household_shapes_and_archetype_2013.csv` — 304
  households × (LCLid, stdorToU, mean_daily_kwh, archetype_k2, 48 normalised weekday shape
  values `wd_0..wd_47`, 48 normalised weekend shape values `we_0..we_47`).
- `data/lake/lcl_household_load_shapes_2013/cluster_centroids_k2_weekday.csv` — the 2
  archetype centroid shapes (48-point weekday vectors) from §3.
- `data/lake/lcl_household_load_shapes_2013/tariff_price_signal_response_by_household.csv` —
  per-household High/Low/Normal mean kWh and % deviation from §4, the raw table the
  significance tests were run on.

All three are derived directly from the real LCL readings and the real 2013 tariff-signal
calendar described in §1 — no synthetic or invented values in any column. Raw downloaded
source files (the 795MB zip, extracted CSVs, and intermediate pickle) were kept in the
session scratchpad, not committed to the repo, per normal data-hygiene practice — the
compact derived CSVs above are sufficient to reproduce every number in this document.

---

*Filed by the background analytics lane (workload 1 of
`docs/staging/BACKGROUND_LANE_AND_WALL.md`), 2026-07-08. Research + a proposal only — no
`simulation/`, `company/`, or `saas/` files touched; `docs/market_research/ASSUMPTIONS.md`
deliberately left unedited per the task's stated concurrent-edit-safety constraint.*
