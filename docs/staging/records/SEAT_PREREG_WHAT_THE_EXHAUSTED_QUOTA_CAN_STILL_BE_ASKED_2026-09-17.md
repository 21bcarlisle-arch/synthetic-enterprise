# [SEAT PREREGISTRATION] What an exhausted quota can still be asked, before the clock runs

**Severity:** INFO · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_14 (per-cell weather store)
**Written** 2026-09-17 06:45 BST (05:45 UTC) by the delivery seat, BEFORE any of it was measured,
holding the Lane 0 claim `era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets`.

---

## 0. The premise, re-measured at draw time

The drawn item's gate is `curl ... | %{http_code}`, and it answered **429**, body
`{"reason":"Daily API request limit exceeded. Please try again tomorrow.","error":true}`.
So the item's own instruction applies: *do not start*. The store is unchanged — decompressed md5
`6f5e8dd49e1b1a7ea2002143885990ed`, the same hash the previous turn recorded — and the premise is
NOT spent: the 23 in-book cells still hold temperature only.

**The work is blocked on a clock, not on a decision.** What follows is what can be established
while the clock runs, and each of it is a thing that stops being measurable the moment the quota
resets.

## 1. Q1 — does the landed stop-on-quota mechanism fire against a LIVE 429?

`WeatherQuotaExhausted` landed in `40d133fe3` and was proved against a fake. Right now the real
service is returning the real refusal, which is the only condition under which the wiring from
`sim.weather_ingestor.get_daily_weather` through `_fetch_with_backoff` to `build()`'s `break` can
be exercised end-to-end without a stub. **After the reset this cannot be run again today.**

**P1.** `python3 -u -m tools.build_weather_world --build --no-temperature` terminates in **under
60 seconds** (the item claims "seconds rather than hours"; the previous run sat for 11 minutes
before I killed it), prints a line containing `QUOTA EXHAUSTED`, and exits non-zero.

**P2.** The store is byte-identical afterwards: decompressed md5 stays
`6f5e8dd49e1b1a7ea2002143885990ed`, and `cells.json` / `regimes.json` keep md5
`d52faa6f7de1bab4f1e17b26476b147d` / `da2cfd5609fd6e46f3915112c776faa6` as compressed files.
I am NOT confident of this leg: `build()` breaks out of the loop and then falls through to
whatever the function does with `held`, and I have not read that far. If it writes, P2 fails and
that is a defect worth more than the pull.

**P3 — the falsifier I expect to be embarrassed by.** If P1 fails — if it sits and backs off —
then `40d133fe3` classified the reason correctly in a unit test and the live string does not match
`DAILY_QUOTA_REASON`, and the mechanism is decorative. `_is_daily_quota` is a substring test on a
lowercased reason and the live reason is `Daily API request limit exceeded. Please try again
tomorrow.`, so I expect it to match — but a prediction I expect to pass is still worth writing
down, because the previous turn's P2 was also one of those.

## 2. Q2 — how many cells does ONE day's quota actually buy?

This is the question the drawn item does not ask and which decides whether it is a one-turn item
at all. **The item assumes the 23 remaining cells fit inside one day's quota. Nothing has
established that.**

The evidence we already hold points the other way. `f94ebb1d2` took the store from **169 to 190
complete cells — 21 cells — and then stopped**, and the previous turn's finding attributed that
stop to "the rate limiter". If the thing that actually stopped it was the DAILY quota (the same
limit that is refusing now, and the reason string is the same one), then **one day's quota buys
about 21 cells of this shape**, and 23 cells does not fit in one day.

**P4.** One day's quota buys **more than 21 and fewer than 60** cells at this request shape
(10 years × 6 daily variables × 1 location per request). Stated as a range because the only
in-repo datum is the single 21 above and a range I can be wrong about is worth more than a point
estimate I cannot.

**P5.** The next successful run therefore completes **fewer than 23 cells** and stops on a second
quota exhaustion, needing a further day. I would rather be refuted here: being wrong means the
item closes in one turn.

**How Q2 gets settled, and the order matters.** Open-Meteo publishes its own call-weighting rule
(a request is not one "call"; it is weighted by locations × variables × timesteps). That published
rule is the answer and our 21 is the cross-check, **not the other way round** — knowledge first.
If the published rule cannot be established, P4 stays a range with its sample size of one named on
its face, and no point estimate gets written into the code.

## 3. What is NOT being decided here

The pull itself. No amount of measurement moves the clock, and nothing in this document is a
reason to retry the fetch before the gate answers 200.
