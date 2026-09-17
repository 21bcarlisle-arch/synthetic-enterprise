# PREREG — how many of the last 23 ERA5 cells fit in one hourly bucket

**Written 2026-09-17, BEFORE pass one was launched.** Filed in `records/` because it is not work:
it is a prediction whose answer I do not have, written so the run can refute it.

## The question

`sim/weather_world/daily.csv.gz` holds 221 cells: 190 complete, 31 carrying temperature only. Of
those 31, **8 have left the book** and `build()` names them `unreachable` on the surface — this
pass structurally cannot reach them — leaving **23 in the book's `todo`**. That is the premise the
drawn item states, and it is confirmed by counting the store rather than by reading the item.

`tools/build_weather_world --build --no-temperature` pulls the three ERA5 columns for those 23.
Open-Meteo weights a request by its window at +1.0 per 2-week period, so one cell of 3,653 days
costs 3653/14 = **260.9 weighted calls**. Against the published **5,000/hour** cap that is
**19.2 cells per hour**; against **10,000/day** it is 38.3 per day. 23 fits in one day and does
not fit in one hour.

## The predictions

1. **Pass one completes 19 cells**, ±2 for whatever the bucket already held when it started.
   (`curl` gate at launch answered 200, so the bucket was not empty; it was not necessarily full.)
2. **The remaining ~4 refuse as BURST 429s, not as `WeatherQuotaExhausted`.** The hourly limit is
   not Open-Meteo's `"daily api request limit exceeded"` reason, so `_is_daily_quota` returns
   False, `_fetch_with_backoff` treats it as a burst limit, and each remaining cell burns
   60+120+180 = **360s of backoff** before landing in `refused[]`. The run therefore does NOT
   stop early: `quota_exhausted` stays `None` and the loop walks every remaining cell.
   *This is the leg most likely to be wrong, and it is the expensive one — 4 cells x 6 min.*
3. **Pass two, an hour later, takes the rest and `refused[]` is empty.** Because 23 - 19 = 4 is far
   inside one bucket, and the daily cap (38.3 cells) is never reached by 23.
4. **`git status` distinguishes the two passes truthfully.** 260169d23 made a build that pulled
   nothing leave the 11 MB store byte-identical, so a pass that completed cells shows
   `daily.csv.gz` modified and a pass that got nothing shows a clean tree. If pass one shows the
   file unmodified, prediction 1 is refuted at zero and the cause is in the bucket, not the code.

## What would refute each

1. A completed count outside 17–21 — the +1.0-per-2-weeks weighting is wrong, or the cap is not
   5,000/hour for this key.
2. `quota_exhausted` non-`None` on pass one — the hourly limit DOES carry the daily reason string,
   and `_is_daily_quota` is matching a superset. That would be better news than the prediction
   (it stops in seconds instead of burning 24 minutes) and it would mean `WeatherQuotaExhausted`'s
   docstring names the wrong distinction.
3. A non-empty `refused[]` on pass two.
4. Either pass rewriting the store with no cell completed.

## Result

**Appended 2026-09-17 07:45 UTC, beside the predictions rather than over them. The experiment was
never run, because the premise was spent while it was being written — and the reason it was spent
is itself the answer to prediction 1.**

`7d9eabe49` landed on origin/main at 07:24 UTC: all 23 in-book cells pulled in eleven minutes,
none refused. My local HEAD was two commits behind, so the 23-cell `todo` I measured off my own
worktree was real but stale. **Premise spent. Claim released.**

What the aborted pass one did establish, in its ninety seconds of life:

1. **Prediction 1 — unanswerable, and refuted as posed.** Pass one completed 1 cell, not ~19, but
   not because 19.2 is wrong: the bucket had been emptied minutes earlier by the landing run.
   A ceiling cannot be measured against a bucket someone else has already spent. **`7d9eabe49`
   separately refutes 19.2 as a hard stop** — it did 23 with zero 429s. Both readings stand; see
   `docs/data-sources/weather.md` for the reconciliation (the limit is enforced on the bucket, not
   on the request that overdraws it).
2. **Prediction 2 — CONFIRMED, and it was the finding worth the turn.** The hourly limit does
   carry its own reason string, *"Hourly API request limit exceeded. Please try again in the next
   hour."*, which `_is_daily_quota` did not match. Cell 2 of my run entered `waiting 60s
   (attempt 1)` — the burst path — against a bucket only the top of the hour could refill. The
   expensive leg I flagged as "most likely to be wrong" was right, and it was live at HEAD.
   **Now closed:** `sim/weather_ingestor.py` classifies by reset horizon, mutation-proven in
   `tests/sim/test_weather_ingestor.py::test_the_hourly_limit_is_a_stop_and_not_a_retry_like_the_minutely_one`.
3. **Prediction 3 — moot.** There was no pass two; the cells were already in.
4. **Prediction 4 — untested.** I killed the run before `_write` could rewrite the store, and
   restored my working copy from HEAD rather than land a one-cell diff on top of a stale
   190-cell base. Landing it would have been a **230,139-value regression** against `7d9eabe49`.

**What I would predict differently next time.** Prediction 1 assumed this machine's key was mine
alone for the hour. It is not: the bucket is shared across every lane and daemon in this tree, so
any ceiling measured from one lane's run is contaminated by whatever else pulled that hour. A
future pull-rate measurement has to record what else touched the key, or it is not attributable.
