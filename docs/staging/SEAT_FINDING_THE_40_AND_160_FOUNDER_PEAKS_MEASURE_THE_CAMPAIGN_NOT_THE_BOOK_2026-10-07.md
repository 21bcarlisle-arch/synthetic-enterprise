**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `the-40-and-160-founder-peaks-are-read-and-reported`

# The 40- and 160-founder peaks measure the campaign, not the book, and the peak is not one year held

## Premise, checked when this was drawn (2026-10-07 ~17:40Z)

- **Duplicate-work note:** the live claim it named is this draw's own write (same id, `paths: []`).
  Nobody else holds it, and the session that launched the job (pid 2197437) has not reported.
- **Which run is which, from the bytes and not from line order.** The launch command (that session's
  transcript, 14:51:49Z) was `scale_series.py --founders 40 --end 2019-12-31 --out shape40.json`
  `&&` `... --founders 160 ... --out shape160.json`. Each output file records its own
  `args.founders`, so the attribution does not rest on the order:

| run | `args.founders` | ru_maxrss | wall | accounts | settled cust-years | records | campaign sample rate |
|---|---|---|---|---|---|---|---|
| `shape40.json`  | 40  | **3,353.3 MB** | 563 s | 178 | 308.8 | 112,805 | 0.906 |
| `shape160.json` | 160 | **2,464.7 MB** | 514 s | 192 | 485.9 | 177,487 | 0.076 |

  The larger book has the **smaller** peak, 889 MB lower.

## Why the pair cannot give a per-customer-year slope

**Before dividing: what each number counts.** "Settled customer-years" is customer-days in the run's
records divided by 365.25, counted to `--end 2019-12-31`. The peak is the RSS of one process. The
settlement budget (`SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1750`) is charged in a third unit: customer-years
**to a fixed 2026-01-01 horizon** (`simulation/live_population.py`, `horizon = date(2026, 1, 1)`),
whatever `--end` is.

So each founder costs about 10 budget years. 40 founders leave about 1,350 years of headroom and the
campaign settles 90.6% of its wins. 160 founders use about 1,600 and the campaign settles 7.6%.
**Both runs committed the same budget (1,747.9 and 1,746.7).** Changing the founder count did not make
the book bigger. It moved the book from campaign wins to founders, at a fixed total. That is two
variables moving in opposite directions, so the two-point slope (−888.6 MB over +177.1 settled
customer-years, **−5.0 MB per customer-year**) is not a quantity. I am publishing it only to show it
cannot be used.

## What the series does say

The script samples RSS every 2 s (`rss_series`, 273 and 247 phase-2b samples).

1. **Fixed base, the same in both runs.** Imports and the runner reach about 680 MB. Then, early in
   phase 2b, RSS rises about 800 MB in 6 s: 717→1,558 MB at t=64–70 s for 40 founders, and
   700→1,488 MB at t=96–100 s for 160 founders. **The base is about 1.5 GB** before anything
   accumulates. I have not identified what that step loads.
2. **After the step, RSS grows and never falls.** I found no drop larger than 20 MB anywhere in phase 2b
   in either run, and the peak is the last sample before phase 4c. **So the peak is not one settled
   year held at once.** A year-at-a-time hold would show a sawtooth at the year boundaries. This is
   accumulation across the whole run, so a streamed or chunked settlement would **not** fix it by
   itself. It would fix it only if what accumulates is per-year state that is kept after its year,
   and nothing here shows that it is.
3. **The growth follows the campaign, not the settled records.** Post-step growth is +1,788 MB at 40
   founders (about 1,350 campaign budget years) against +971 MB at 160 founders (about 150), while the
   settled records go the other way (112,805 against 177,487). That fits a cost driven by the
   campaign's wins planned **to 2026**, held even though the run stops at 2019. Two points with two
   variables moving cannot attribute it, so this is a hypothesis, not a finding.

## Verdict

- **Peaks:** 40 founders → 3,353 MB; 160 founders → 2,465 MB.
- **Slope:** none that can be used from this pair. The experiment held the binding variable, committed
  budget years, constant, at 1,747 against 1,750.
- **Shape:** a fixed base of about 1.5 GB, then monotonic accumulation with no year boundary in it.
  This is **not** one-year-at-once, so streaming settlement by year is not shown to be the remedy.
- **For "can settlement carry a book of thousands":** this pair does not answer it. The standing
  answer is the 2026-10-06 curve: 2.884 MB per committed customer-year, and 5,363 MB for a
  4,000-founder book before any campaign settles (the note on `SETTLEMENT_CUSTOMER_YEAR_BUDGET`).

## Pre-registration: the one-variable control (written 17:43Z, before launch)

**Control:** the same script and the same `--end 2019-12-31`, with
`SETTLEMENT_CUSTOMER_YEAR_BUDGET = 0.0`. No campaign win settles, so the book is founders only and
founder count is the only variable. Two legs, 40 then 160 founders, run in the executor worktree
(`.scale_shape_ctl/`, not committed).

**Predictions, filed before the answer:**

- P1: the founders-only 40 peak is **below 2,465 MB**, which would mean the campaign drove the 3,353.
- P2: the founders-only 160 peak is **above** the founders-only 40 peak by 300–2,000 MB. That gives a
  positive slope per settled customer-year of the same order as the 2.9 MB curve.
- P3: the same ~800 MB early step appears in both legs, which would make it part of the fixed base.
- P4: no drop larger than 20 MB in phase 2b, so the series is monotonic again.

If P1 fails, the campaign is not what made the 40 run heavier, and hypothesis 3 is refuted.

## Result of the control

Both legs and the bridge are run, with outputs in `/var/tmp/scale-shape-ctl/` (`ctl40.json`,
`ctl160.json`, `bridge40.json`).

| leg | code | founders | budget | ru_maxrss | accounts | settled cy | committed cy (to 2026) |
|---|---|---|---|---|---|---|---|
| ctl40    | 318162387 | 40  | 0     | **1,764.1 MB** | 37  | 89.7  | 377.4 (founders only) |
| ctl160   | 318162387 | 160 | 0     | **2,214.2 MB** | 157 | 422.5 | 1,518.2 (founders only) |
| bridge40 | 318162387 | 40  | 1,750 | **3,228.4 MB** | 178 | 308.8 | 1,747.9 |
| original f40  | 9313d0394 | 40  | 1,750 | 3,353.3 MB | 178 | 308.8 | 1,747.9 |
| original f160 | 9313d0394 | 160 | 1,750 | 2,464.7 MB | 192 | 485.9 | 1,746.7 |

**Graded against the predictions:**

- **P1 holds.** The founders-only 40 peak is 1,764 MB, under 2,465. **The campaign made the 40 run
  heavy.** Hypothesis 3 survives.
- **P2 holds.** 160 minus 40 is +450 MB, inside 300–2,000. Over +332.8 settled customer-years that is
  **1.35 MB per settled customer-year for founders**, or 0.39 per committed customer-year. It is
  **below** the 2026-10-06 curve's 2.884, not "of the same order" in any sense I would defend. The
  base implied at zero settled years is **about 1,640 MB**.
- **P3 partly holds.** The early step is in both legs (881→1,516 and 855→1,506 MB at t=8–10 s), but it
  is about 650 MB, not 800. It is part of the fixed base, and its size depends on the run.
- **P4 fails, narrowly.** ctl160 has one 31 MB drop at t=135 s in 173 phase-2b samples. That is not a
  sawtooth; the other 172 intervals are flat or rising. bridge40's one drop (3,218→2,262 at t=501 s) is
  the run ending phase 2b, not a year boundary.
- **B1 holds.** bridge40 at 3,228 MB is within ±150 of the original 3,353, on a book identical to the
  record (112,805 records). W2_36 does not confound the comparison, and about 125 MB is the run-to-run
  noise between code versions.

**The campaign increment, one code version for 40 and across versions for 160:**

| | campaign committed cy | peak minus founders-only | MB per committed campaign cy | MB per settled campaign cy |
|---|---|---|---|---|
| 40 (bridge40 − ctl40)            | 1,370.5 | +1,464 MB | **1.07** | 6.7 (over 219.1) |
| 160 (original − ctl160, ±125 MB) | 228.5   | +251 MB   | **1.10** (0.55–1.65) | 4.0 (over 63.4) |

**The campaign's memory follows the customer-years it COMMITTED to 2026, at about 1.1 MB each, in
both runs, not the years it settled by 2019.** Per settled customer-year a campaign win costs 3 to 5
times what a founder does. This is the lead, and it is not yet a mechanism: it fits the campaign
building state for every win it plans to the 2026 horizon, including wins whose in-market date is after
the run's `--end`. I have not read where that state lives.

## Corrected verdict (supersedes the one above where they differ)

- **Peaks, attributed:** 40 founders → 3,353 MB; 160 founders → 2,465 MB. The 40 run is heavier
  because its settlement budget went to campaign wins (sample rate 0.906 against 0.076).
- **Fixed base:** about 1.6 GB (680 MB of imports, then a run-dependent step of 650–800 MB).
- **Slopes:** founders 1.35 MB per settled customer-year (two points, 90–420 settled years). Campaign
  wins about 1.1 MB per customer-year **committed to 2026**.
- **Not one year held at once.** Every leg rises monotonically, so streaming settlement by year is not
  shown to be the remedy.
- **What the two slopes do NOT license:** extrapolating to thousands. The founders slope at 4,000
  founders × 10 years gives tens of GB, while the note on `SETTLEMENT_CUSTOMER_YEAR_BUDGET` records
  5,363 MB for that book before any campaign settles. Both cannot be linear. The curve is not linear in
  that range, or the two measure different windows. **I cannot yet say which.**
- **Consequence for calibration runs:** a run with `--end` before 2026 is charged settlement budget to
  2026 (`live_population.py`, `horizon = date(2026, 1, 1)`). It appears to pay in memory for campaign
  wins it never settles. A short calibration run therefore settles a smaller book than its budget
  suggests, and is not lighter for being short.

**Second pre-registration (17:56Z, before launch). The bridge leg.** The control ran at `318162387`.
The original pair ran at `9313d0394` in `/var/tmp/se-scale`, whose working tree has no changes under
`simulation/`, `sim/`, `company/` or `saas/`. Between the two, `simulation/meter_reads.py` changed: W2_36
makes not-in-smart-mode a state the meter holds. `run_phase2b.py` also changed (the H50 per-run reset),
but that is a no-op when each run is its own process. So the founders-only 40-against-160 comparison is
on one code version, while "original minus control" crosses two. **Bridge:** the original 40-founder
configuration (budget 1,750, unpatched script) at `318162387`. **Prediction B1:** its peak is within
±150 MB of 3,353 MB. If it is not, the campaign increment below is confounded with W2_36.

## Third pre-registration (2026-10-07 ~19:20Z, before launch): do the post-end wins cost memory?

*Claim `campaign-holds-memory-for-wins-past-the-runs-end`.*

**Where the wins are built (read before measuring).** `live_population()` appends
`_won_customer_dicts(_campaign(...))` to the book unconditionally. It has no `report_end`. The
campaign quotes up to `CAMPAIGN_QUOTE_CUTOFF = 2025-06-07`, whatever `--end` is. `run_phase2b`
binds `ELEC_CUSTOMERS`/`GAS_CUSTOMERS` from that book at import, then builds per-customer state over
the whole book: `weather_by_customer`, `cloud_cover_by_customer`, the weather refusals, and a renewal
schedule per account. A won account dated after `--end` produces no settlement records. It is
still a customer for everything that is keyed on the book.

**Census at 40 founders, seed default, same campaign as `bridge40`** (resolved in 5 s): 602 won supply
legs (electricity plus gas). **141 are dated on or before 2019-12-31 and 461 after.** That matches the
settled book: 178 accounts with records, minus founders-only 37, gives 141. Customer-years to 2026
by leg: 1,111.3 before the end and 1,382.6 after (55%).

**One variable.** This is `bridge40` (budget 1,750, `--end 2019-12-31`, 40 founders, the same code
and script), with `_won_customer_dicts` wrapped to drop legs whose `acquisition_date > --end`. The
campaign, its spend and the premise register are untouched. Only book membership changes.

**Predictions, filed before the answer:**

- **Q1 (that it is one variable):** the settled book is identical to `bridge40`: 112,805 records,
  178 accounts, 308.8 settled customer-years. If not, the filter changed something besides
  membership, and Q2 cannot be read.
- **Q2 (the lead):** the peak falls by **at least 500 MB** from `bridge40`'s 3,228 MB. A fall within
  ±130 MB (the bridge-against-original spread) refutes the lead: the post-end wins cost nothing, and
  the campaign increment belongs to the 141 settled wins.
- **Q3 (which unit):** if the cost follows committed-to-2026 years, the fall is about **810 MB**
  (55% of the 1,464 MB increment), to a peak near 2,420. If it is per account in the book, the fall
  is about **1,130 MB** (77%), to a peak near 2,100. If neither is within ±150 MB, I cannot yet say
  which unit it is.

## Result of the third control: yes, the post-end wins are built, and they cost about 1 GB and 200 s

`postend40` (unit `longjob-scale-shape-postend40`, `.scale_shape_postend/` in the executor worktree,
not committed; the filter reported `dropped 461, kept 141`):

| leg | ru_maxrss | wall | records | accounts | settled cy |
|---|---|---|---|---|---|
| `bridge40` (book holds all 602 won legs) | **3,228.4 MB** | 509 s | 112,805 | 178 | 308.8 |
| `postend40` (post-end legs dropped)      | **2,169.1 MB** | 309 s | 112,805 | 178 | 308.8 |
| `ctl40` (founders only, for scale)        | 1,764.1 MB    |  96 s |  32,757 |  37 |  89.7 |

- **Q1 holds.** The settled book is identical (records, accounts, settled years and the 36 lifecycle
  rolls), so book membership is the only thing that moved.
- **Q2 holds.** The peak falls by **1,059 MB (33%)** and the wall time by **200 s (39%)**. The 461
  won legs dated after `--end` settle nothing. They cost more memory than the 141 legs that settle
  everything the campaign contributes (2,169 − 1,764 = 405 MB).
- **Q3: per account, not per committed year.** The result is 69 MB from the per-account prediction
  (2,100) and 360 MB from the committed-years one (2,420). **The "1.1 MB per customer-year committed
  to 2026" in the verdict above is a coincidence of this config, corrected here:** the campaign's
  post-end legs are both most of its accounts and most of its committed years, so the two units could
  not be told apart until membership was moved alone.

**The shape, which the two series show and the prediction did not ask.** The extra memory is **not**
set-up state. Both legs sit at about 1,570 MB a few seconds into phase 2b, so the per-customer weather
and cloud-cover dicts (`weather_by_customer` etc., bounded by reading them at about 0.5 MB per account)
are not where it goes. `bridge40` climbs to 3,228 MB through the term loop (`while all_terms`) and
**drops 956 MB in one 3-second sample (3,218 → 2,262) as the loop ends**. `postend40` climbs only to
2,162 MB and has no such drop. So something local to the term loop grows with the number of accounts
in the book, settled or not, and with the length of the loop. It is released when the loop's frame
goes. **I have not found which structure that is.** The candidates by reading are the per-record sweeps
over the module book (`active_elec = [c for c in ELEC_CUSTOMERS ...]` per committee check,
`_known_customers()` building a fresh whole-book list per call). Neither obviously retains anything, so
neither is established. A tracemalloc probe that snapshots at the peak is written
(`.scale_shape_postend/tm_probe.py`). Admission refused it at 19:25Z: another lane's 11.2 GB
`--level-arm` job was resident.

**Why it matters beyond calibration runs.** The full-window run (`--end` = `REPORT_END`) has no
post-end wins, so this exact cost is zero there. But the mechanism is "a loop-local structure that
scales with accounts in the book times the loop's length". In a full run that is every account, and it
is the most likely owner of the 1.35 MB per settled customer-year founders slope. Finding it is the
lead on whether settlement can carry a larger book. Dropping post-end wins from a short run's book is
the cheap half. It is not yet done: the book is bound at import (`run_phase2b.py:294`, before
`report_end` exists) and feeds about 40 sites, including the import-time treasury EAC sums and the
reporting surfaces, so rebinding it per run is a design change with a blast radius, not a one-line
filter.

**What does not change:** the settlement-budget accounting. The campaign still charges its budget to
2026 whatever `--end` is (`horizon = date(2026, 1, 1)`). Making the campaign a function of `--end` would
make a short run's pre-end book differ from the full run's. That is a calibration-comparability
question for the world's side, and I have left it.
