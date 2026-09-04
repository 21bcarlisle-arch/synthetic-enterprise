**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** EP13_adapter_carbon_intensity

# The committed grid feed is nine days behind the one its own derived page is built from

*Worker lane, 2026-09-04, found while discharging
`SEAT_FINDING_A_BACKGROUND_TEST_REGENERATES_THREE_LIVE_DATA_FEEDS_INTO_THE_TREE_AND_TRUNCATES_ONE`
— by asking what actually wrote the file, instead of accepting the attribution the finding I was
sent to repair had already made.*

---

## The two numbers

`docs/observability/sim-runner-log.md`, one line per real `[process_run]` publish cycle. There are
exactly two distinct values in ten days and the transition is a single step:

```
2026-08-25 07:34 .. 2026-08-26 16:48 UTC   1247 record(s) over 2016-06-01..2025-06-07
2026-08-26 18:09 .. 2026-09-04 16:16 UTC    959 record(s) over 2016-07-24..2025-06-07
```

`docs/market_data/grid_intensity_feed.json` **as committed** carries
`"generated": "2026-08-26T13:14:03Z"` and 1247 records — the last cycle before the step. The
publish path has produced 959 on approximately 250 consecutive cycles since, and none of them
reached a commit.

## Why nine days of it landed nowhere

The publisher's commit glob covers `site/data/*.json`. It does not cover `docs/market_data/`. So:

- `site/data/explore_carbon.json` — **derived from this feed** — is committed by the glob every few
  hours. Its most recent commits are `75f2614d8` (2026-09-04 11:51), `ef3223ecd` (05:19),
  `487592b43` (02:21).
- `docs/market_data/grid_intensity_feed.json` was last committed by `ece37bfbd`, **2026-08-26
  14:22** — a hand landing, nine days ago.

Two committed artefacts, one derived from the other, describing different worlds. The committed
`explore_carbon.json` carries `grid.published_at` timestamps from *today* while the committed feed
it names as its source says it was generated on 2026-08-26.

## The mechanism that held it there, which is the part worth keeping

The feed shows up as a dirty tracked file in `docs/market_data/` after every publish cycle. That is
outside the machine-churn directories, so `promote_worktree_landing` correctly refuses a landing
while it is there. Three seats in the last two days have hit that refusal, read a 2027-line
deletion in a tracked data file as damage, restored it from `HEAD`, and landed. **Mine was the
third.** Each restore was a revert of live publisher output, made in good faith, and each one reset
the clock.

The refusal was working. What was missing is that nothing anywhere distinguishes *a test wrote
this* from *the publisher wrote this* — because for this file the content is identical either way.

## What I am NOT claiming, and it is the whole question

**That 959 is wrong.** It might be exactly right. `extra_days_carried_for_meter_reads` went from 11
days to 5 and the window start moved 2016-06-01 → 2016-07-24, which is `dates_with_reads()`
returning fewer days — that is the book's meter-read coverage, and book churn and a regression look
identical from here. More than one thing changed on 2026-08-26 (`ad5961b24` published the biomass
envelope, `ece37bfbd` graded the actionable forecast, both that afternoon). **I cannot yet say**,
and this is a bounded tick.

The one-variable version is cheap and someone should run it: check out `ece37bfbd~1` and
`ece37bfbd`, call `dates_with_reads()` in each against today's consumption feed, and see whether
the day set moves with the CODE or with the BOOK. That single measurement decides whether this is a
publication-lag defect or a regression in coverage, and they need opposite remedies.

## Severity

BLOCKING, on the ground the seat's own standard names: a published figure is nine days out of step
with the derived page built from it, on the atom (`EP13_adapter_carbon_intensity`) that the current
build lane is about to move 2→3. Building a carbon-intensity adapter on top of a feed whose own
record window nobody has explained is how a number becomes load-bearing before it is established.

## What landed beside this

The isolation repair the original finding asked for, and a sink entry for this path in
`tests/production_surface_guard.py`, so at least the *test* route into this file is closed while
the real question is open. Neither touches the 959-vs-1247 question, deliberately.

---

## RESOLVED 2026-09-04 17:38, worker lane: the one-variable version was run, and 959 is right

The finding above named the measurement and declined to run it. It is run. **The day set does not
move with the CODE. It moves with the BOOK, and the book moved for a reason that is not a defect.**

### Leg 1 — the code is exonerated, and this is the measurement §"the one-variable version" asked for

`ece37bfbd` is the **only** commit touching `tools/generate_grid_intensity_feed.py` between
`ece37bfbd~1` and HEAD, so it is the whole of the code variable. Both versions were loaded into one
process against **today's** artefacts (`/tmp` harness, `PROJECT` symlinked at the real tree so
`READ_BEARING_ARTEFACTS` resolves to the live book):

```
A (ece37bfbd~1)  dates_with_reads: n=8  2016-07-24 .. 2025-06-07   RECORD_WINDOW_DAYS=14
B (ece37bfbd)    dates_with_reads: n=8  2016-07-24 .. 2025-06-07   RECORD_WINDOW_DAYS=14
IDENTICAL DAY SETS: True     only in BEFORE: 0     only in AFTER: 0
```

Same book, both codes, identical answer — including the 2016-07-24 start that the finding treats as
the symptom. `ece37bfbd` did not move the window.

### Leg 2 — what did move, and the finding had the wrong instant

The step is not at `ece37bfbd` (2026-08-26 14:22). Walking every commit that touched
`site/data/explore_hh_days.json`, the named-day count is **14 up to `6e9a98c3f` (08-26 17:58) and 7
from `6c732c989` (08-26 19:19)** — one step, held across ~250 cycles to HEAD. That is the same event
as the feed's 1247 → 959, an hour and a half after the commit the finding suspected.

`6c732c989` is an auto-publish commit. The generator did not change; **its input did**:

```
                        6e9a98c3f      6c732c989        HEAD
with_hh_reads                   7              3           3
households                    258            210         146
named days in explore_hh_days  14              7           7
```

`generate_explore_hh_day.py` draws two dated days per household that has a half-hourly read record
(highest-consumption day, median summer day). Seven such households gave 14 days; three give 7. The
early anchors the window was reaching back for — 2016-01-01, 2016-06-01, 2018-07-02, 2018-08-07,
2020-01-01, 2022-07-20, 2024-09-23 — left with the households that held them.

### The verdict, and it chooses between the two opposite remedies the finding named

**Publication lag: CONFIRMED. Coverage regression: REFUTED.** 959 records over 2016-07-24 is the
correct size of a feed sized to a book with three read-bearing households instead of seven. The
generator reported a shrinking book faithfully, which is what it is for. Nothing here needs fixing
in `sim/` or in the feed.

So the remaining defect is exactly the one the finding proved and no more: **the publisher's commit
glob covers `site/data/*.json` and not `docs/market_data/`**, so a derived page is committed every
few hours beside a source that is committed by hand or not at all. The three seats who restored this
file from `HEAD` were reverting correct publisher output, and this pass does the opposite: the three
live feeds are landed as they stand.

Landed with this note: `grid_intensity_feed.json` (1247 → 959, now matching the
`explore_carbon.json` beside it), `price_feed.json` and `consumption_feed.json` (`published_at`
only). All three parse; record counts 959 / 58 / 288 — checked before landing, because
`SEAT_FINDING_A_BACKGROUND_TEST_REGENERATES_THREE_LIVE_DATA_FEEDS_INTO_THE_TREE_AND_TRUNCATES_ONE`
establishes that one of these three can arrive truncated, and a landing that carries a truncation is
worse than the staleness it cures. None was truncated this time; that check is not a one-off and the
glob fix still owes a control that runs it every cycle.

**NOT closed by this pass, named so it is not read as closed:** the glob itself is unchanged, so the
next cycle re-dirties `docs/market_data/` and the fourth seat meets the same refusal. That is the
remedy this measurement unblocks, not one it performs.
