# [SEAT RESULT] The ERA5 pull is bound HOURLY, not daily, and 23 cells fits in a day but not in an hour

**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_14 (per-cell weather store)
**Filed** 2026-09-17 by the delivery seat, closing P4 and P5 of
`docs/staging/records/SEAT_PREREG_WHAT_THE_EXHAUSTED_QUOTA_CAN_STILL_BE_ASKED_2026-09-17.md`,
which left them open as "cannot be measured without a quota".

They did not need a quota. They needed the published rule, which is the order
`CLAUDE.md` requires and which I reached for second rather than first.

---

## 1. The answer, from the source

Open-Meteo's free tier, from its [pricing](https://open-meteo.com/en/pricing) and
[terms](https://open-meteo.com/en/terms) pages — two pages, figures agreeing, read 2026-09-17:
**600 calls/min · 5,000/hour · 10,000/day · 300,000/month.**

**A request is not one call.** Pricing page, verbatim: *"Requests for data covering more than 10
weather variables or extending over a period of more than 2 weeks for a single location are
considered multiple API calls"* — +1.0 per further 2-week period, +0.1 per variable beyond 10.
Their worked example: 2 weeks × 15 variables = 1.5 calls; 4 weeks = 3.0.

One cell of this project's pull is 2016-01-01..2025-12-31 — **3,653 days at 6 daily variables**.
Six is under ten, so there is no variable surcharge and the whole cost is the window:

```
3653 / 14 = 260.9 calls per cell
```

| window | limit | cells |
|---|---|---|
| minute | 600 | 2.3 |
| hour | 5,000 | **19.2** |
| day | 10,000 | **38.3** |

## 2. The predictions, beside their outcomes

**P4 — one day's quota buys more than 21 and fewer than 60 cells. CONFIRMED at 38.3.** The range
was honest and it contained the answer; a point estimate guessed from the single 21 would have
been wrong by nearly half.

**P5 — the next successful run completes fewer than 23 cells and needs a further DAY. REFUTED,
and I said I would rather be refuted here.** 23 < 38.3, so the remaining pull fits inside one
day's quota. What it does not fit inside is one HOUR: 23 > 19.2.

**The frame, not just the number, was wrong — and this is the second time on this exact subject.**
The previous turn corrected "rate limiter" to "daily quota" and I carried that forward as though
the daily quota were the binding constraint. It is not. It is the ceiling on a *day of runs*.
What ends any *single* run at ~19 cells is the hourly bucket. The 169→190 resume in `f94ebb1d2`
completed **21 cells and stopped** against a predicted hourly ceiling of **19.2** — a ~9% miss,
and nowhere near 38.3. Two successive findings named a limit; neither named the one that was
actually firing, because both reasoned from a refusal string and neither did the arithmetic.

## 3. What this changes for the next holder of the claim

1. **Budget two passes about an hour apart, not two days.** Pass one gets ~19 of the 23; pass two
   gets the rest. Both fit in one day's 38.3.
2. **`RETRY_BACKOFF_SECONDS` cannot clear an hourly limit and is not expected to.** Four attempts
   at 60/120/180 s is six minutes against a bucket that refills over sixty. The ~4 cells past the
   hourly ceiling will be filed as ordinary refusals in `refused`, which is correct and resumable —
   but a reader seeing `refused: 4` should not read it as four broken cells. **No code change is
   proposed for this**: an hour of in-run sleeping is exactly the shape `WeatherQuotaExhausted`
   was created to abolish, and stopping cleanly so a later run resumes is the better behaviour.
3. **`PAUSE_SECONDS = 20.0` sits under the published minutely floor** of `60 / 2.3 = 26.1 s` and is
   **deliberately left there**. 21 consecutive cells went through at 20 s with no minutely refusal,
   so the observation refutes the arithmetic and arithmetic alone is not grounds to slow every
   future pull by 30%. Recorded so the gap reads as known rather than missed.

## 4. Where this went in the knowledge layer

`docs/data-sources/weather.md` — which until today still said *"There were no rate-limit issues
encountered, ensuring smooth data retrieval."* True of the four-location probe that wrote it;
false since the store became a 221-cell pull, and still sitting there while the limits cost two
sessions a combined ~2h20m. **That sentence is why nobody looked.** Corrected in place rather than
deleted, with the figures and the arithmetic.

`docs/institutional/knowledge_map.md` gains the row and the source pointer, because a sourced
figure that nothing points at is the failure mode that file exists to prevent.
