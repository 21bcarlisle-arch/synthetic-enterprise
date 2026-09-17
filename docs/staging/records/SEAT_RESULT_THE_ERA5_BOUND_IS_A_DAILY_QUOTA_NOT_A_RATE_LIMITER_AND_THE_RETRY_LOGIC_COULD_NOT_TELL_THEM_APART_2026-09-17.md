# [SEAT RESULT] The ERA5 bound is a DAILY QUOTA, not a rate limiter, and the retry logic could not tell them apart

**Severity:** LATENT · **Lane:** L0_delivery · **Epoch:** 3 · **Atom:** W1_14 (per-cell weather store)
**Filed** 2026-09-17 by the delivery seat, closing the Lane 0 item
`resume-the-era5-pull-for-the-last-31-weather-cells`.

Pre-registration, written before any of this was measured:
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_ERA5_RESUME_FOR_THE_LAST_INCOMPLETE_WEATHER_CELLS_MUST_AND_CANNOT_MOVE_2026-09-17.md`.

---

## 1. The headline

**No weather data was pulled, and that is the result rather than a failure to get one.** Open-Meteo's
daily quota for this machine was already spent when the turn began:

```
$ curl .../v1/archive?...&daily=wind_speed_10m_max
http=429 bytes=86
{"error":true,"reason":"Daily API request limit exceeded. Please try again tomorrow."}
```

`sim/weather_world/daily.csv.gz` is byte-identical to `HEAD` and to the backup taken before the
run. The store stands at **221 cells, 190 with the ERA5 archive, 31 temperature-only**, unchanged.

**The previous turn's result said "the rate limiter is what stopped it". That is true and it is
under-specified, and the difference is the whole of this finding.** A per-request rate limiter is
cleared by waiting inside the run. A daily quota is not. The code treated them as the same thing.

## 2. What the drawn item asked for, and why re-running it could not work

The item directed: re-run `--build`, pull the 31 remaining cells, land the store. I ran exactly
that. It sat for eleven minutes, used 11 seconds of CPU, wrote nothing, and its log was empty
because `print` block-buffers to a file. The store's mtime was the only honest progress signal
(`_write` fires after every successful cell) and it never moved.

`/proc` gave the diagnosis: `wchan = hrtimer_nanosleep`, one socket to Open-Meteo in `CLOSE-WAIT`
with an 86-byte body waiting. It was not fetching. It was serving the backoff.

**Left alone it would have run for about two and a quarter hours and written nothing.**
`_fetch_with_backoff` asks `"429" not in str(exc)` — status only — so a daily quota got the same
four attempts at 60/120/180 s that a burst limit gets: six minutes per cell, 23 cells, against a
limit that resets tomorrow. It would then have reported 23 separate refusals whose single shared
cause appears nowhere in the summary line.

I killed it and verified the store was untouched.

## 3. The predictions, beside their outcomes

**P1 — the round trip is byte-identical. CONFIRMED.** `--build --no-temperature --limit 0`
returned decompressed bytes with md5 `6f5e8dd49e1b1a7ea2002143885990ed`, identical to the backup;
`cells.json` and `regimes.json` matched even as compressed files. So `_write` recomputing
`level_of` does reproduce the stored `level_c` exactly, and **the item's "temperature must stay
byte-identical" constraint is satisfiable by this tool** — which was genuinely open beforehand.

**P2 — the pull completes fewer than 23 cells. CONFIRMED, but for a reason I did not predict, and
the prediction was mis-shaped.** I wrote that the run "either completes all 23 in 10–20 minutes, or
is stopped by 429s partway", and I said `refused` is non-empty iff fewer than 23 complete. **Both
halves are wrong about the live case.** The real outcome was zero cells and zero entries in
`refused`, because the run never reached the end of even the first cell's retry ladder. My frame
assumed the limiter was per-request; it is per-day, and a per-day limiter does not produce the
partial-progress shape I described. The corrected mechanism is section 4.

**P3 — no temperature column changes. VACUOUSLY TRUE and therefore proves nothing.** Nothing was
written at all. Kept rather than deleted because a prediction that survived only because its
subject never ran is not evidence, and scoring it as a pass would be the flattering reading.

**Section 2 of the pre-registration — the 31 is really 23 + 8. CONFIRMED and now enforced.**
`todo` is drawn from `book_cells()` (149 cells), not from the store (221). Eight of the 31
incomplete cells — `E420N0232 E450N0206 E456N0104 E457N0081 E457N0335 E460N0337 E480N0170
E489N0194` — are cells the book no longer occupies. `_write` keeps them on purpose. **This pass can
never fetch them, so the ceiling of a perfect run is 213/221, not 221/221**, and a reader told only
"31 incomplete" would score a flawless run as 8 short.

## 4. What landed

No data. A mechanism, so the next run does not re-derive this by burning two hours.

**`sim/weather_ingestor.py`** — `WeatherQuotaExhausted`, a **subclass** of `WeatherArchiveRefusal`
so the four existing `except WeatherArchiveRefusal` sites keep catching it unchanged. The type is
chosen where the `reason` is read and nowhere else, because a caller re-sniffing the message string
would be a second place to keep in step with Open-Meteo's wording — and the first one already
drifted. `_response_reason`'s docstring has named this exact distinction ("*a wait, and a bad
bounding box is a bug, and an HTTP code alone cannot tell the two apart*") since 2026-09-06; the
knowledge was in the tree and no code consumed it.

**`tools/build_weather_world.py`** — a quota exhaustion is raised straight through
`_fetch_with_backoff` rather than backed off, and `build()` **stops the run** rather than the cell.
The quota is a property of the day, so the first cell to hit it has already answered for every cell
behind it. It is reported on stdout and in the exit code, and `refused` stays empty because a quota
is not a per-cell refusal. The progress surface now also **names** the incomplete cells outside the
book instead of leaving them to look like cells the pull failed on.

**`tests/tools/test_the_weather_pull_stops_on_the_daily_quota_instead_of_retrying_it.py`** (new)
and two legs added to `tests/sim/test_weather_ingestor.py`.

**Mutation-proven in both directions**, because only one direction is the easy one:

| Mutation | Fires |
|---|---|
| Remove the `except WeatherQuotaExhausted: raise` branch (the defect restored) | 2 legs |
| `_is_daily_quota` returns `True` always (stop on *every* 429 — the fail-closed mirror) | 1 leg |

That second mutation is the one worth having. A fix that stopped the pull on any 429 would pass
every quota-only test ever written and would wedge the build on a transient limit that twenty
seconds clears. Every leg asserting the quota path is paired with the burst path through the same
code for that reason.

## 5. What is still open, and what I am NOT claiming

**The 23 in-book cells are still temperature-only, and only the clock fixes that.** Re-running
before the quota resets cannot help, and the tool now says so instead of demonstrating it slowly.

**This costs coverage, not correctness.** `available()` refuses an incomplete cell rather than
answering with a NaN, so no consumer reads a fabricated wind speed. That was established
previously and I did not re-measure it.

**I have not established the quota's size, its reset time, or whether it is per-IP or per-key.**
Open-Meteo's published free-tier limits are a documented number I did not look up, and guessing one
would be exactly the invented constant `CLAUDE.md` forbids. What is established is only that the
limit exists, that it is daily, and that it was spent. **`PAUSE_SECONDS = 20.0` remains correct for
the burst limit it was measured against and is untouched.**

**Whether the 8 departed cells deserve a pull at all is an open judgement I did not make.** They
answer for premises the book held last week. Completing them needs a switch the tool does not have;
minting one today, against an exhausted quota, would be a mechanism nobody could test.

**The next run is not free of me.** It should redirect stdout through `python3 -u`, or read the
store's mtime rather than the log, because the buffering that hid this run's state for eleven
minutes is still there.
