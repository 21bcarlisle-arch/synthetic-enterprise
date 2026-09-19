# [SEAT RESULT] A weather build that pulled nothing still rewrote the 11 MB store, and git could not tell that from a real pull

**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_14 (per-cell weather store)
**Filed** 2026-09-17 by the delivery seat, holding the Lane 0 claim
`era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets`.

Pre-registration, written before any of this was measured:
`docs/staging/records/SEAT_PREREG_WHAT_THE_EXHAUSTED_QUOTA_CAN_STILL_BE_ASKED_2026-09-17.md`.

---

## 1. The premise, re-measured, and why the drawn work did not run

The item's own gate answered **429** — `{"reason":"Daily API request limit exceeded. Please try
again tomorrow."}` — at 05:45 UTC. The item says do not start, so the pull did not start. The
premise is **NOT spent**: the store still holds 221 cells, 190 with the ERA5 archive, 23 in-book
cells temperature-only, decompressed md5 `6f5e8dd49e1b1a7ea2002143885990ed` unchanged. The claim
stays held and the work is blocked on a clock.

**What the turn did instead is what the clock made available and will not make available again
today: the landed stop-on-quota mechanism against a LIVE refusal rather than a stub.** That run
confirmed the mechanism and exposed a second defect underneath it.

## 2. The finding

**`tools/build_weather_world._write` rewrote all 11 MB of `sim/weather_world/daily.csv.gz` after a
run that fetched zero cells.** `build` calls it unconditionally after the fetch loop. The data was
identical; gzip stamps the wall clock into its header; so the file changed, and:

```
$ git status --short sim/weather_world/
 M sim/weather_world/daily.csv.gz          <- 11 MB modified, zero data changed
```

while the run's own summary read `cells held 221/221, regimes 221, refused 0`.

**Why this is LATENT and not cosmetic.** The next step in this very lane is a pathspec commit of
exactly this path. A quota refusal therefore handed the committer an 11 MB diff carrying no data,
**and nothing in the diff distinguishes it from a real archive pull** — the compressed bytes differ
wholesale either way. The one datum that would settle it, the decompressed hash, is not something
`git status`, a diff, or a reviewer sees. The tree's standing habit of "commit what the run
touched" turns that into a landed claim that weather data arrived when none did.

It is also the fail-open direction of a trap this project has already paid for once: a `.gz`
rewrite with identical data being a non-empty git diff because of the header mtime.

## 3. The predictions, beside their outcomes

**P1 — the stop-on-quota mechanism fires against a live 429 in under 60 s. CONFIRMED, at 17 s.**
`python3 -u -m tools.build_weather_world --build --no-temperature` printed
`[1/23] E480N0263 QUOTA EXHAUSTED, stopping: ... HTTP 429 — Daily API request limit exceeded`,
then `STOPPED ON THE DAILY QUOTA — re-running before it resets cannot help.`, and exited 1.
Against the ~2h15m the pre-fix code would have spent sleeping. `40d133fe3` is proved against the
real service, not only against its fixture.

**P2 — the store is byte-identical afterwards. HALF REFUTED, and the refuted half is this
finding.** I predicted both the data and the files would be unchanged, and flagged that I had not
read `build`'s tail. I was right to flag it. Decompressed md5 held at
`6f5e8dd49e1b1a7ea2002143885990ed` and `cells.json`/`regimes.json` held at
`d52faa6f7de1bab4f1e17b26476b147d`/`da2cfd5609fd6e46f3915112c776faa6` — those two are plain text
and carry no clock. `daily.csv.gz` went `e3b9b633…` → `702b4f00…`. **The leg I was least sure of is
the leg that broke, which is the only reason the defect was found rather than committed.**

**P3 — `_is_daily_quota` matches the live reason string. CONFIRMED**, and worth having written
down even though I expected it: had it failed, the landed type would have been decorative.

**P4/P5 — how many cells one day's quota buys. NOT MEASURED, and they stay open.** Nothing today
could move them: measuring the quota's size requires a quota. They are restated in §6 so the next
holder does not have to re-derive that the question exists.

## 4. What landed

**`tools/build_weather_world.py`** — `_write` renders the series to a buffer, compares it against
the existing file's DECOMPRESSED text, and writes only on a difference; it returns
`series_rewritten`, and `main` prints `daily.csv.gz: REWRITTEN` or
`unchanged, not rewritten (no new data)`.

Keyed to the CONTENT, not to "did we fetch". A `completed == 0` guard would have closed the
observed instance and left the same no-op rewrite in the two other cases that reach it: a book
already complete (`todo` empty) and a re-pull returning what the store already held.

`gzip.open` is kept over `gzip.compress` — they differ in the header's FNAME field, and switching
would move every byte of a file whose byte-comparability the writer's existing comments go to
considerable lengths to preserve.

**`tests/tools/test_the_weather_store_is_not_rewritten_when_no_data_changed.py`** — two tests,
mutation-proven in BOTH directions:

| mutant | result |
|---|---|
| `rewritten = True` (the pre-fix defect) | **both tests fail** |
| `rewritten = _series_text() is None` (fail-closed mirror: creates, never updates) | **fails on the rewrite leg** |
| as landed | 2 passed; 34 passed across the four weather suites |

The second mutant is why the skip leg and the rewrite leg are in **one** test over the partition
rather than two a future narrowing could leave half-green: a `_write` that never writes passes
every unchanged-leg assertion while silently discarding pulls that cost a day of quota each.

The fix was then re-run end to end against the still-live 429: 13 s, exit 1, `git status` clean,
md5 back at `e3b9b633…`, surface line `unchanged, not rewritten (no new data)`.

## 5. What this does NOT establish

That the 23-cell pull works. It has not been run. Nothing here touched the fetch path, and the
only evidence the store can still be written correctly is the rewrite leg of the new control and
the 34 green tests — not a live pull.

## 6. Left open for the next holder of this claim

1. **The pull itself.** Gate on the item's `curl`; 200 means go. The build now refuses in ~15 s
   rather than ~2 h, so a wasted attempt is cheap and re-running it is the correct probe.
2. **P4/P5, unmeasured: how many cells does one day's quota buy?** The item assumes 23 fit in one
   day. The only in-repo datum points the other way — `f94ebb1d2` completed **21 cells and then
   stopped**, on what this lane now knows was very likely this same daily quota rather than the
   burst limiter it was attributed to. If ~21 is the ceiling, **23 cells needs two days and the
   item is not a one-turn item.** Settle it from Open-Meteo's published call-weighting rule first,
   with our 21 as the cross-check and not the other way round; if the published rule cannot be
   established, the sample size of one goes on the face of whatever is written down.
3. **The ceiling is 213/221, not 221/221** — 8 incomplete cells are outside the book and this pass
   cannot reach them. Already named on the build's own surface; repeated here because a reader
   told "23 remaining" will otherwise score a perfect run as 8 short.
