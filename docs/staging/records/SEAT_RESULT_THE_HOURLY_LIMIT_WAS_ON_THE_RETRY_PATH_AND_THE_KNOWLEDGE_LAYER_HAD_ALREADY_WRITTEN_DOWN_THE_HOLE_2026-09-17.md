# [SEAT RESULT] The hourly limit was on the retry path, and the knowledge layer had already written the hole down

**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_14 (per-cell weather store)
**Filed** 2026-09-17 by the delivery seat, holding the Lane 0 claim
`era5-pull-the-last-23-cells-in-two-passes-an-hour-apart`.

Pre-registration, written before anything was measured, with its results appended beside the
predictions: `docs/staging/records/PREREG_HOW_MANY_OF_THE_LAST_23_ERA5_CELLS_FIT_IN_ONE_HOURLY_BUCKET_2026-09-17.md`.

---

## 1. The drawn premise is SPENT, and another lane spent it

The item asked for the 23 in-book cells still holding temperature only, in two passes an hour
apart. I measured the premise off my own worktree and it held exactly: 221 cells, 190 complete,
31 temperature-only, of which 8 have left the book and `build` structurally cannot reach, leaving
**23 in-book `todo`**.

It held because **my worktree was two commits behind origin**. `7d9eabe49` landed at 07:24 UTC:
all 23 pulled in eleven minutes, none refused, 213/221 now carrying the ERA5 archive. The store is
complete for every cell the book can reach.

A concurrent `claude -p` worker (PID 1730302) was holding the older spelling of the same direction,
`era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets`. **Both items are the same
work under two ids.** This is the third instance of the "another lane may be landing it right now"
shape; the tell that caught it here was not the item, the claim store, or `git log` — it was
`ps`, read for an unrelated reason while looking for my own build's PID.

**No data was landed by this turn and none was owed.** I killed my own pull at cell 2 and restored
my working copy of `daily.csv.gz` from HEAD rather than commit it: my base was the stale 190-cell
store, so landing one cell on top of it would have been a **230,139-value regression** against
`7d9eabe49` wearing the shape of an increment.

## 2. What the ninety seconds of aborted pull found, which is the reason this turn earned a commit

My pass one completed cell 1 and then cell 2 logged `rate limited; waiting 60s (attempt 1)`.
A bare two-day probe against the same key at **07:39 UTC** answered:

```
{"error":true,"reason":"Hourly API request limit exceeded. Please try again in the next hour."}
```

**That reason string matched nothing.** `sim.weather_ingestor._is_daily_quota` tested for
`"daily api request limit exceeded"` only, so the hourly limit fell through to
`WeatherArchiveRefusal` — the retry path — and `_fetch_with_backoff` gave it 60+120+180 = **360
seconds of backoff per cell against a bucket that only the top of the hour refills**, up to
fifty-nine minutes away.

That is **the identical defect `WeatherQuotaExhausted` was minted to close, one axis over**, and
on the limit that actually fires: a 23-cell pull never reaches the daily quota, and the class
docstring, the constant's comment and both existing controls all said "two limits" where there
are three. The sentence that made the third invisible was the one asserting there were two.

### The knowledge layer had already written it down, and nothing pointed at it

`docs/data-sources/weather.md`, landed hours earlier in `1d9c08f94`, consequence 2, verbatim:

> **`tools/build_weather_world.RETRY_BACKOFF_SECONDS` cannot clear an hourly limit.** Four
> attempts at 60/120/180 s is six minutes against a bucket that refills over sixty.

The hole was **identified, published and left open**, described as safe because `build` is
resumable. It is safe for the *store*; it is not safe for the *clock*, and six minutes per cell is
what two previous sessions each lost. This is the `saas/opex_ledger.py` shape again — the sourced
answer and the live defect in one repository, with nothing telling the reader to look.

## 3. The repair

Keyed to the **property**, not to today's list of limits. The question a caller has is *"can I
wait this out"*, and answering it by enumerating which limits count as quotas is precisely what
put the hourly one on the retry path.

* `sim/weather_ingestor.LIMIT_RESET_SECONDS` — the three reasons mapped to their reset horizons,
  sourced from Open-Meteo's published free-tier limits already recorded in the weather doc.
* `CLEARABLE_BY_BACKOFF_SECONDS = 600.0` — anything resetting slower stops the run. A fourth
  Open-Meteo limit with a minute-scale reset classifies itself; no edit needed.
* `WeatherQuotaExhausted` now carries `reset_seconds`, so `build` names **which** wait it hit.
  Reporting "DAILY QUOTA" for an hourly bucket sends away a session that could have resumed in
  twenty minutes — the surface now says `the HOURLY bucket; resets at the top of the hour`.
* An **unrecognised** reason stays retryable. The asymmetry is deliberate and named at the call
  site: a wrongly retried refusal costs six minutes, a wrongly stopped run costs the whole pull.

**Control:** `tests/sim/test_weather_ingestor.py::test_the_hourly_limit_is_a_stop_and_not_a_retry_like_the_minutely_one`
— one control over the whole partition, all three limits in one test, using the live strings
rather than paraphrases. Mutation-proven in both directions:

| mutation | result |
|---|---|
| drop the hourly entry (the defect as it stood) | **RED** — "an hourly 429 must STOP the run" |
| classify minutely as un-waitable (the fail-closed mirror) | **RED** — "a minutely 429 must stay retryable" |
| unmutated | 22 passed |

Both mirrors fire, so the control cannot pass by stopping on everything or on nothing.

## 4. A correction to the refutation in `7d9eabe49`, and it goes the other way

That commit refuted the 19.2-cells-per-hour ceiling — correctly, it did 23 with zero 429s — and
proposed the suspect term was the per-cell call cost, *"since one cell is one HTTP request"*.

**The per-cell cost is not 1, and my 07:39 probe is the evidence.** Fifteen minutes after that
23-cell run finished, with no other pull in between, a two-day request was refused on the hourly
bucket. If a cell cost one request, 23 requests could not empty a 5,000/hour bucket. The bucket
being empty is direct evidence the cost is of the order the +1.0-per-2-weeks weighting predicts
(~261), which is what the published table already assumed.

The reconciliation, now in the weather doc: the hourly limit is enforced **on the bucket, not on
the request that overdraws it**. A run may spend past 5,000 and only the *next* caller is refused.
So 19.2 is a rate the bucket sustains, not a count any single run is cut off at — which is why a
23-cell pass finished clean and still left nothing for me thirteen minutes later.

Both readings are kept in `docs/data-sources/weather.md` beside the prediction: one refutation and
one rescue, from the same afternoon, and neither collapses into the other.

## 5. What I would do differently, and it is a measurement rule

Prediction 1 assumed this machine's Open-Meteo key was mine alone for the hour. **It is not** —
the bucket is shared across every lane and daemon in this tree. Any pull-rate ceiling measured
from one lane's run is contaminated by whatever else pulled that hour, and the contamination is
invisible in the run's own log. A future rate measurement has to record what else touched the key
or it is not attributable. Filed here rather than as a new rule: the general form is already
CLAUDE.md's *"when a result moves and more than one thing changed, you cannot attribute it."*

## 6. Disposition

* Data work: **done, by `7d9eabe49`, not by this turn.** Nothing owed.
* Hourly-limit classification: **repaired and mutation-proven in this commit.** No work owed.
* Claim `era5-pull-the-last-23-cells-in-two-passes-an-hour-apart`: **released.**
* **Open, and not mine to close:** two Lane 0 ids describe one piece of work. Whatever mints Lane
  0 items produced both spellings, and the premise check passed on both because both cite commits
  that are genuine ancestors. A premise check that asks "are these commits landed" cannot ask
  "is another lane holding this same work", and `ps` is not a mechanism.
