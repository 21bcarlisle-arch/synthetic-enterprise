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

*(pending: filled when `longjob-scale-shape-ctl-budget0` finishes)*
