# A rate-limited weather pull wrote header-only CSVs over ten years of real archive, and exited 0

**Date:** 2026-09-06
**Lane:** W1_market_weather (found under the Lane 0 delivery claim
`the-weather-cells-reach-the-world-or-w1-14-says-why-not`)
**Severity:** BLOCKING — live data-loss path in the world's only real weather archive
**Status:** FIXED in the same commit. The archive-breadth work it was found by is still open.

---

## What happened

W1_14 waits on archive breadth: the derived weather cells cannot drive household heat load for
premises whose cell holds no archive site. I went to close that by pulling the two missing supply-book
locations (Birmingham, Teesside) from Open-Meteo.

The pull printed this, and exited 0:

```
pulling C5 Birmingham 52.4862,-1.8904
  0 records
  wrote sim/weather_data/C5.csv
pulling C6 Teesside 54.5973,-1.1049
  0 records
  wrote sim/weather_data/C6.csv
```

Both files were 125 bytes: a header row and nothing else. The real cause, found only by making the
request by hand:

```
status 429
{"error":true,"reason":"Daily API request limit exceeded. Please try again tomorrow."}
```

## The defect

Two lines, in `sim/weather_ingestor.py`, that compose into data loss:

1. `get_daily_weather` ended `if response.status_code != 200: return []`. **Every** transport
   failure — 429, 503, a bad bounding box — became an empty list indistinguishable from a
   legitimately empty range.
2. `write_weather_csv` opens `mode='w'`, which truncates, and wrote the header unconditionally.

`simulation/run_phase1b_weather_pull.py` iterates the **live supply book** and writes
`sim/weather_data/{customer_id}.csv` for every customer. Run today — during the rate limit that was
live — it would have truncated `C1.csv`, `C2.csv`, `C3.csv` and `C4.csv` to headers. That is the
world's entire real weather record, 2016-01-01 to 2025-06-07, four sites, ~3,400 days each. Silently,
with a success message per file and exit code 0.

Nothing downstream would have raised either: `weather_inputs.load_weather_means` returns `{}` for a
file it cannot parse, and `{}` is also what it returns for a file that does not exist. The world would
have run on no weather at all.

## Why no control caught it

`tests/sim/test_weather_ingestor.py::test_non_200_returns_empty` asserted:

```python
assert result == []
```

It **pinned the fail-silent branch**. It was green before this finding and it was green because of
the defect, not in spite of it — the R15 shape where a control stays green through exactly the
failure it covers. It is now
`test_non_200_refuses_and_names_the_status`, and it asserts the refusal fires and carries the status.

## The fix

- `get_daily_weather` raises `WeatherArchiveRefusal` naming the HTTP status **and Open-Meteo's own
  `reason` string**. The reason is load-bearing: "Daily API request limit exceeded" is a *wait* and a
  bad bounding box is a *bug*, and the status code alone cannot tell them apart.
- `write_weather_csv` refuses twice, because the two catch different failures:
  - **empty** records never reach disk (the 429 path);
  - a **shorter** pull cannot overwrite a longer archive (the 200-carrying-a-truncated-range path,
    which the emptiness check misses entirely).
- `_existing_row_count` counts **data rows, not lines**, so a file already truncated by the old
  behaviour counts 0 and can be repaired. Counting lines would have wedged precisely the files the
  defect created.

Six new controls, all proven by a poison round (each guard reverted in turn; each killed a named
test). One prediction in that round was **wrong and is recorded next to the test**: I expected
line-counting to be caught by the header-only test. It was not — that case passes either way. The
discriminator is an identical-length re-pull (5 data rows = 6 lines), and that is now its own test.

## What is still open

The two pulls. They are blocked by the 429, which is external and time-based and clears on its own.

## The count on W1_14's row was also wrong, and that is the smaller finding

The row said the blocker was "17 more real weather pulls" — 21 cells per driver minus the 4
occupied. **That counts the partition, not the book.** The world's supply book holds six distinct
locations; four have archives. **Two** pulls finish this atom. Seventeen is what W1_23's *generated*
population will need before an arbitrary premise lands in a covered cell.

Both numbers are real and they count different sets, which is the recurring shape this project pays
for: a figure published without saying what it counts. The row now states which one it means and why
they differ. They are not progress against each other.
