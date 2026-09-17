# [WORKER RESULT] The last 23 in-book cells pulled in eleven minutes, and the hourly ceiling derived from the published rule is refuted

**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_14 (per-cell weather store)
**Filed** 2026-09-17 by the autonomous worker, closing the Lane 0 item
`era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets`.

Prior record this one continues:
`docs/staging/records/SEAT_RESULT_THE_ERA5_BOUND_IS_A_DAILY_QUOTA_NOT_A_RATE_LIMITER_AND_THE_RETRY_LOGIC_COULD_NOT_TELL_THEM_APART_2026-09-17.md`.

---

## 1. The headline

**The store is complete for every cell the book can reach.** `sim/weather_world/daily.csv.gz` goes
from **190 cells with the ERA5 archive to 213**, out of 221 held. All 23 in-book cells that held
temperature only were pulled, none refused, each with all 3,653 days present for all three ERA5
fields. The 8 cells still temperature-only are the ones the book has left; `--build` names them and
cannot reach them, and no run of this tool will ever complete them.

```
149 cell(s) in the book; 221 held; 23 still needing the ERA5 archive
  8 further incomplete cell(s) are NOT in the book and this pass cannot reach them: ...
  [1/23] E480N0263 3653 days (52.263,-0.820)
  ...
  [23/23] E614N0242 3653 days (52.039,1.128)
cells held 221/221, regimes 221, refused 0
```

Quota probe before starting, as the item directed: `200`. The run took **eleven minutes**, 08:07 to
08:18, ~29 s/cell.

Values at real inputs, before landing, new 23 against the 190 already held:

| | n | wind m/s (cell means) | cloud % | precipitation mm/yr |
|---|---|---|---|---|
| newly pulled | 23 | 3.83–5.12 (mean 4.24) | 63.5–68.1 | 680–799 (mean 725) |
| already held | 190 | 3.55–5.53 (mean 4.30) | 63.6–76.8 | 654–1882 (mean 915) |

The 23 are lowland south-east and east England (E480–E614, 50.9°–53.8°N), so sitting at the dry end
of a national spread whose wet tail is upland is what they should do. Nothing is out of range and
no cell has partial day coverage.

## 2. Two stale working copies would have landed a regression, and neither was mine

Before the build, both files this work touches were **older on disk than the commits that repaired
them**, and the tell was the mtime: 02:28 and 02:38, against landings at 05:26 and 06:03.

* `tools/build_weather_world.py` on disk **predated `40d133fe3`** — no `WeatherQuotaExhausted`
  import, no quota branch, no `unreachable` line. Running it would have re-armed the per-cell
  backoff the previous turn's finding exists to remove.
* `sim/weather_world/daily.csv.gz` on disk was the **pre-`f94ebb1d2` store: 169 ERA5 cells, not
  190**. It is a strict subset — HEAD holds **230,139 values it does not have** (21 cells × 3,653
  days × 3 fields) and it holds **none HEAD lacks**, measured field-by-field over all 807,313 rows
  rather than inferred from the byte diff.

A build started on those bytes would have re-pulled 21 cells already in the record, spent that
budget for nothing, and written a store that lost 21 cells' ERA5 unless the pull happened to reach
all 44. **The cheap `git status` reading — "the store is modified, someone is mid-work" — was wrong
in the direction that destroys data.** `tools/refresh_to_head.py` cleared the module (preserved as
`refs/preserved/refresh-to-head/era5-builder-stale-copy-predates-quota-mechanism`); it has no reader
for `.gz`, so the store was measured by hand and restored with `git show HEAD:<path> > <path>`.

## 3. The prediction this run refutes

`1d9c08f94` derived from Open-Meteo's published limits (600/min, 5,000/hour, 10,000/day, at 260.9
call-units per cell for 3,653 days × 6 variables) that a run is bound **hourly at 19.2 cells**, and
a day at 38.3, and recorded P5 — "the next run needs a further day" — as refuted because 23 < 38.3.

**23 cells went through in eleven minutes with zero 429s.** By that same arithmetic that is ~6,000
call-units inside one hour against a stated 5,000/hour ceiling, and 44 cells inside one day
(21 at 05:26 plus 23 now) against a stated 38.3. Both ceilings were passed without a refusal.

So the derivation is not the binding constraint it was written up as. The suspect term is the
per-cell call cost: one cell is **one HTTP request** (`sim/weather_ingestor.get_daily_weather`,
no cache, one `requests.get`), and the "+1.0 per further 2-week period" weighting that turns it
into 260.9 units is the only part of the sum not measured here. What actually refused every cell at
02:38 remains a real exhaustion that cleared with time; the arithmetic that named it does not
survive its own next test.

**Do not carry "19.2 cells/hour" or "38.3 cells/day" forward as established.** This is the third
turn in a row on this subject to name a bound and be wrong about which one fires — a rate limiter,
then a daily quota, now a published-rule sum that today's run walks straight through. The honest
statement is the one the code already implements: an exhausted quota stops the run and says so, the
build resumes by re-running, and the ceiling's value is not established.

## 4. What is left

* 8 non-book cells stay temperature-only, by construction. Nothing to do.
* The knowledge-layer sentence corrected in `1d9c08f94` (`docs/data-sources/weather.md`) now needs
  the §3 correction beside it, not over it. Filed here rather than done here: this turn's pathspec
  is the store, and that file is on the far side of a local/origin fork.
