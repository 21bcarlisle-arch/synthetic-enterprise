**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `loop-local-memory-scales-with-accounts-in-the-book`

# Which structure in phase 2b's term loop grows with the accounts in the book

Follows the third control in
`SEAT_FINDING_THE_40_AND_160_FOUNDER_PEAKS_MEASURE_THE_CAMPAIGN_NOT_THE_BOOK_2026-10-07.md`: at 40
founders and `--end 2019-12-31`, the 461 won legs dated after `--end` add 1,059 MB of peak and 200 s,
with the settled book identical, and the extra is released in one step.

## Premise, checked when this was drawn (2026-10-07)

- **Duplicate-work note:** the live claim it named is this draw's own id. No rival seat or
  `surgical_land` was working on it (`ps`); the only related process was the tracemalloc probe
  `tm_probe.py` (pid 3909292) this item says to read.
- **"Freed when the loop ends" is narrower in the bytes than in the item.** In `bridge40.json` the
  drop (3,218 → 2,262 MB) falls on the sample that also closes phase 2b (`phases.phase2b.end_s`
  504.0). The loop ends and `run_phase2b.main` returns inside the same 3-second window, so the series
  says the structure is held by **`main`'s frame** (a local, or a closure cell over one), not
  necessarily by the loop. Nothing after the loop `del`s anything.
- **The growth is linear in wall time, not back-loaded.** Both legs climb at about 5 MB/s for the
  first 100 s; `postend40` then flattens at ~2,100 MB while `bridge40` keeps climbing to 280 s. The
  post-end legs' terms are popped last (the heap is date-ordered), so if they cost only their own
  terms the extra would sit at the END of the run. It does not, which says the per-term cost of
  EVERY term rises with the number of accounts in the book.

## Pre-registration (written before `locals_probe.py` was launched)

Instrument: `/var/tmp/scale-shape-ctl/locals_probe.py` (first launch sized `main`, a three-local wrapper; relaunched on `_main`, which holds the loop, before any result) — 40 founders, `--end 2019-12-31`, no filter
(the `bridge40` configuration), deep-sizes each local of `run_phase2b.main`'s frame every 45 s.

- **P1.** One local (or two sharing a cause) grows by at least 600 MB between the first sample in the
  term loop and the last, and no other local grows by more than 100 MB.
- **P2.** That local is not `all_records` or the settlement fold (the settled book is identical in
  both legs, so neither can carry the difference).
- **P3.** I cannot say which local it is. Reading gave no candidate that retains per term and per
  account; `monitor.update` keeps a bounded deque only.

## Result: the premise was wrong. The growth is in set-up, not in the term loop

`locals40.json`, five samples. Through 316 s and 3,380 MB, `_main` held **26 locals**, and neither
`all_terms` nor `all_records` existed yet. The term loop had not started. The frame had reached
`_forward` (`run_phase2b.py:1459`) and nothing after it, so the climb is inside the next call that
takes time: **`fabric_providers_for_book`** (`run_phase2b.py:1537`). It builds one fabric demand
trace per structurally eligible electricity premise, and each trace covers the **whole window**
(`REPORT_START` to `effective_end`). The book it is handed is `ELEC_CUSTOMERS +
SUCCESSOR_ELEC_CUSTOMERS`, which includes every campaign win dated after `--end`.

So **P1 to P3 are not graded.** They asked which local of the loop grows, and the loop is not where
the memory goes. The probe slows the run about 1.7× (deep-sizing pauses the main thread), so the
5 MB/s climb in `bridge40` and `postend40` is the trace build at its normal speed. I misread it as
the loop in the previous finding.

**Why it is freed when phase 2b ends.** `fabric_series_by_customer` is a local of `_main`, and
`_main` returns in the same 3-second sample where the drop shows. The loop never frees it.

**What reads a post-end leg's trace.** Only the registry EAC loop (`run_phase2b.py:1731`), which
gives such a leg the basis `OWN_READS_LAST_YEAR_HELD`. Its own docstring says "the join is after the
window ends, so the account never settles here and only a truncated run reaches this". Nothing that
settles reads it. The texture and switch controls sample it, but they judge only whether the switch
moved the book.

**The cost per premise is a cost per window-year.** A trace holds three 48-float lists per day. Its
size grows with the window's length, not with how long the account is supplied. That makes it the
likely owner of the **1.35 MB per settled customer-year founders slope** as well: for a founder, the
window and the supply period are the same span. This is a lead and has not been measured.

## The fix, and its pre-registration (written before the control run)

`fabric_providers_for_book` now refuses a premise whose `acquisition_date` is after the window's
end. It records the refusal as a named verdict (`JOINS_AFTER_WINDOW_REFUSAL`), builds no trace, and
does not count the premise as a coverage refusal. A post-end leg keeps its drawn EAC band in place
of the last-year-held read. Seeding is per customer (`seed` and `customer_id`), so no other premise's
trace can move. The boundary is tested on both sides, and two mutations (`>=`, and the branch
removed) each fail the test.

Control run `fix40`: `scale_series_orig.py --founders 40 --end 2019-12-31 --no-extract` (the `bridge40`
harness; `postend.py` filters unconditionally and a first launch on it was stopped before any result), on the fixed code.

- **Q1.** The settled book is identical to `bridge40`: 112,805 records, 178 accounts, 308.8 settled
  customer-years, final treasury 284,184.7176…, 68,263 register points.
- **Q2.** `ru_maxrss` is within 150 MB of `postend40` (2,169 MB). It is not within 150 MB of
  `bridge40` (3,228 MB).
- **Q3.** Wall time is within 60 s of `postend40` (309 s).

## Result of the control: the book is identical, the time is recovered, and 78% of the memory

`fix40.json` (unit `longjob-scale-shape-fix40b`):

| leg | ru_maxrss | wall | records | accounts | settled cy | final treasury |
|---|---|---|---|---|---|---|
| `bridge40` (old code, all 602 won legs) | 3,228.4 MB | 509 s | 112,805 | 178 | 308.8 | 284,184.71764401573 |
| **`fix40` (this fix, all 602 won legs)** | **2,397.4 MB** | **312 s** | 112,805 | 178 | 308.8 | 284,184.71764401573 |
| `postend40` (old code, post-end legs filtered) | 2,169.1 MB | 309 s | 112,805 | 178 | 308.8 | 284,184.71764401573 |

- **Q1 holds exactly.** Records, accounts, settled years, 68,263 register points and the 36
  lifecycle rolls all match. The final treasury matches to the last digit.
- **Q2 fails as written.** The peak fell 831 MB, from 3,228 to 2,397 MB, which is 78% of the
  1,059 MB the post-end legs cost. It is still **228 MB above `postend40`**, outside the 150 MB I
  pre-registered. The traces were most of the cost but not all of it. The 461 legs are still in the
  book, and other per-account set-up structures still cover them: `weather_by_customer` and
  `cloud_cover_by_customer` (about 110 MB across the whole book, so roughly 85 MB for these legs),
  and the cells their premises add to `WeatherWorldSource._days`. **I cannot yet say how the 228 MB
  splits between these.** It is not measured, and the fix leaves it in place.
- **Q3 holds.** 312 s against 309 s. The 200 s were the trace build.

**A correction to the previous finding, made beside its claim.** That finding located the cost in
"something local to the term loop", based on a peak and a drop that fall at the end of phase 2b.
The cost is in set-up: one fabric trace per premise covering the whole window. It is held by
`_main` until `_main` returns. The loop's length was a stand-in for how long the build took.

## What is still open, and handed on

**The founders slope (1.35 MB per settled customer-year) is probably this same trace**, held over the
whole window for every premise that settles. A founder is supplied for the whole window, so its
trace years and its settled years are the same number. A trace stores three Python lists of 48
floats per day, roughly 3 to 4 KB a day, which is about 1.1 to 1.5 MB a year. That is the slope's
order of magnitude, but it is a reading and has not been measured. Two remedies keep every value
identical:

1. Store each day as `array('d')` rather than a list of float objects, about 3.5 times smaller.
   Every consumer reads, zips or sums the values, so this is a change of representation and not of
   number.
2. Start a won leg's trace a year before it joins rather than at the window's start. Its registry
   EAC reads only the trailing year. This one needs care: `OWN_READS_FIRST_YEAR`, the texture
   samples and the incoming-occupant copy all read the trace's start.

Remedy 1 is the one to measure first, because it cannot move a settled number.

**Not caused by this change:**
`tests/simulation/test_every_settling_domestic_premise_reads_a_complete_stored_cell.py::test_every_domestic_non_hh_premise_resolves_to_a_complete_stored_cell`
fails in this worktree with HEAD's copy of `fabric_demand_path.py` as well (86 premises have no
stored cell). It depends on the weather store's environment, and it fails without this change.

## A trunk red this landing met, and what was done about it

The first landing attempt was refused because the gate selected
`test_every_domestic_non_hh_premise_resolves_to_a_complete_stored_cell`: that test imports
`fabric_demand_path`. It is **red on origin/main** as well. The shared tree at `b870dd6c5` gives the
same 86 names, and so does HEAD's copy of the module here. `tools.build_weather_world --list` reports
**164 cells the book occupies that the store never held**, and 239 stored cells the book no longer
occupies. The store was built for an earlier book. This book is the one `b870dd6c5` reports as
doubled, with prospects going from 52 to 197 and the cause unattributed. Until the store catches up,
these premises settle on the legacy shape. That is a fidelity loss on trunk now, and it is not
caused by this change.

It lands **strict-xfail**, the door `a53326372` used for the same control when the pull outran
Open-Meteo's daily quota (8 ERA5 cells before the 429 that time; 164 are needed now). Strict means
the commit that completes the store must delete the marker, so the marker cannot outlive the
defect. **Recommendation, handed on:** attribute the doubled book first, since that is owed under
`b870dd6c5`. Pull the cells only for the book that survives the attribution. A pull for a book that
turns out to be a defect costs days of quota.
