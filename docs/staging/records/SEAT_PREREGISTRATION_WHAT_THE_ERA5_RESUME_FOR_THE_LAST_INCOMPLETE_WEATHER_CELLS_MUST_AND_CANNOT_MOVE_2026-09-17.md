# [SEAT PRE-REGISTRATION] What the ERA5 resume for the last incomplete weather cells must move, and what it cannot move

**Severity:** RECORDED · **Lane:** L0_delivery · **Epoch:** 3 · **Atom:** W1_14 (per-cell weather store)
**Filed** 2026-09-17 by the delivery seat, **before the round-trip check is run and before a single
archive is fetched**. Subject: the Lane 0 item
`resume-the-era5-pull-for-the-last-31-weather-cells`, and the store at
`sim/weather_world/daily.csv.gz` as it stands at `337afc848`.

Related: `tools/build_weather_world.py`, `sim/weather_world.py`,
`docs/staging/records/` W1_14 findings from 2026-09-16/17.

---

## 1. What is established by reading, and is NOT in question

Taken before a word of section 3 was written, so nothing below can be mistaken for a prediction
made after its answer was visible.

**The premise commits are spent; the work is not.** All three commits the drawn item cites
(`6e02d6442`, `f94ebb1d2`, `eb5ee25a8`) are ancestors of `origin/main`, and local `HEAD` equals
`origin/main` at `337afc848`. `sim/weather_world/` is clean against `HEAD` — no other lane has the
store uncommitted on this disk. The item's *premise* (machinery landed) is therefore true and
already discharged; the item's *work* (the remaining ERA5 columns) is untouched.

**The gap is still 31, measured just now.** `python3 -m tools.build_weather_world --list` prints
`149 cell(s) the book occupies; 221 in the store (190 with the ERA5 archive, 31 temperature-only)`.
That is the same 190/31 split `f94ebb1d2` recorded, so nothing has filled it since.

**`_has_era5` is the completeness question, and it is the right one.** A cell is complete when any
row carries any of `ERA5_FIELDS` (the three non-`LEVELLED` columns). The temperature pass creates
rows for every cell before a single archive is fetched, so "does this cell have rows" would read
every cell as done.

**The pull is rate-limited by construction, not by accident.** `PAUSE_SECONDS = 20.0`,
`RETRY_ATTEMPTS = 4`, `RETRY_BACKOFF_SECONDS = 60.0`, all carrying a MEASURED origin comment
("a one-second gap got HTTP 429 after five pulls").

**`_write` fires after every cell**, so an interrupted pull keeps everything it got.

---

## 2. THE THING THE DRAWN ITEM GETS WRONG, established before starting

The item says "the 31 of 221 cells that still hold temperature only", and reads as though a
successful `--build` takes the store to 221/221. **It cannot.** `build()` computes

```python
todo = [c for c in cells.values() if not _has_era5(held.get(c["cell_id"], []))]
```

where `cells = book_cells()` — **the 149 cells the book occupies**, not the 221 the store holds.
Splitting the 31 by book membership:

* **23 are in the book** — `E480N0263 E487N0194 E504N0248 E510N0431 E512N0168 E516N0158 E521N0207
  E521N0237 E525N0223 E527N0166 E531N0174 E532N0166 E532N0344 E533N0175 E536N0172 E539N0170
  E544N0187 E549N0179 E558N0173 E558N0182 E592N0174 E604N0120 E614N0242`. These are the `todo`.
* **8 are not** — `E420N0232 E450N0206 E456N0104 E457N0081 E457N0335 E460N0337 E480N0170
  E489N0194`. These are cells the book no longer occupies. `_write` keeps them on purpose (their
  centres are recorded nowhere else), but `build()` will never fetch them.

**So the ceiling of this run is 213/221 with the ERA5 archive, and 8 temperature-only, not 0.**
A later reader seeing `8 temperature-only` after a clean run must not read it as a failed pull.
Whether those 8 are worth a pull at all is a separate judgement (they answer for premises the book
held last week, and `available()` already refuses an incomplete cell rather than returning NaN),
and this turn does not make it.

---

## 3. The predictions, written before the measurements

**P1 — the round trip is byte-identical.** `--build --no-temperature --limit 0` does a pure
read-rewrite: `_existing_rows` adds each cell's stored `level_c` back on, `_write` recomputes
`level_of` from those raw rows and subtracts it again. I predict `daily.csv.gz`'s **decompressed
bytes** come back identical to the backup at `~/.cache/se-weather-backup/`, and that `cells.json`'s
`level_c` values are unchanged.

*Why it could fail, and what each failure would mean:* `_write` recomputes `level_of(rows[cell])`
rather than reusing the stored `level_c`. If the producer that first wrote the store reached the
level by a different arithmetic route, every temperature anomaly in the file shifts by that
difference, and **the item's "temperature must stay byte-identical" constraint is unsatisfiable by
this tool** — which would be a finding about the writer, not about the pull. The gzip container
itself may differ (mtime in the header) without the data differing; that is why the comparison is
on decompressed bytes.

**P2 — the pull completes fewer than 23 cells.** The whole result of the previous turn was that the
bound is the rate limiter. At 20 s between cells plus four 60 s backoffs on a 429, I predict the run
either completes all 23 in roughly 10–20 minutes, or is stopped by 429s partway. I am **not**
predicting which: that is the measurement. What I *do* predict is that **`refused` is non-empty if
and only if the count of completed cells is below 23**, because `_fetch_with_backoff` either returns
records or raises into `refused`.

**P3 — no temperature column changes in the landed diff.** With `--no-temperature`, the HadUK pass
does not run at all, so the only columns that can change are the three ERA5 ones and only on rows
belonging to the 23 `todo` cells. I predict a decompressed diff whose changed lines all belong to
those cells' regime ids, and zero changed lines elsewhere. If P1 fails this prediction is moot and
the finding replaces it.

---

## 4. What "done" means for this item

The item is direction, not an atom, so the seat decides. **Done is: every in-book incomplete cell
that the rate limiter permits is pulled, the store is landed, and the number that remain is stated
with its cause named.** Not "31 becomes 0" — section 2 establishes that is not reachable by this
tool. A partial pull that lands is a discharge; an unlanded complete pull is not.
