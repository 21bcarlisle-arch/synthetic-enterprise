**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `fabric-trace-slope-at-160-founders`

# Is the founders slope the fabric trace? The same probe at 160 founders

Follows "What is still open" item 1 in
`SEAT_FINDING_THE_FABRIC_TRACE_AS_ARRAYS_AND_THE_FOUNDERS_SLOPE_2026-10-07.md`.

## Premise, checked when this was drawn (2026-10-07)

- HEAD equals origin/main (`046c6a9b1`): `build_fabric_series` stores days as `array('d')`.
- **Duplicate-work note:** the live claim it named is this draw's own id. No rival probe or
  `surgical_land` on this subject was running (`ps`). Carried on, not a duplicate.

## What the 40-founder reading does and does not fix

The trace is built for the whole window for each fabric-eligible premise, so trace-years are
`traces × window years` (72 × 4.0 = 288 at 40 founders), not tenure. A settled customer-year is
tenure. The two coincided at 40 founders (ratio 0.93); nothing says they coincide at 160.

## Pre-registration (written before the run)

Instrument: `/var/tmp/scale-shape-ctl/scale_series_probe.py --founders 160 --end 2019-12-31
--no-extract`, run once in the executor worktree at `046c6a9b1`. One variable against `armB40`
(same code, same probe): the founder count. The slope reference is 1.35 MB per settled
customer-year, measured founders-only at the old (list) code (`ctl40` → `ctl160`).

- **Q1, trace bytes per trace-year.** 0.55–0.57 MB. The layout does not depend on book size.
- **Q2, settled customer-years.** 420–520 (the pre-array 160 run with the campaign settled 485.9).
- **Q3, trace-years per settled customer-year at 160.** 0.6–1.0. Lower than 0.93 is my lean,
  because a founder churns out while its trace still spans the window, but the eligible share may
  differ between founders and campaign wins, so it may not be.
- **Q4, the verdict.** Convert the trace back to lists at the measured 1.296 MB per trace-year and
  difference it across 40→160: `1.296 × Δtrace-years / Δcustomer-years`. **The slope is the trace
  if this is ≥ 0.9 MB** (two-thirds of 1.35); **it is not the main owner if it is < 0.6 MB**;
  between, it is a part-owner and I say so. I predict 0.7–1.3.
- **Q5, peak.** 1,900–2,700 MB. Not graded beyond the range; the campaign share differs by book
  size, so a peak-to-peak slope across 40→160 mixes two variables and is not attributable.

## Result

Output: `/var/tmp/scale-shape-ctl/armB160.json` (wall 399 s), beside `armB40.json`.

| | 40 founders (`armB40`) | 160 founders (`armB160`) | Δ |
|---|---|---|---|
| accounts / settled customer-years | 178 / 308.8 | 192 / 485.9 | +14 / **+177.1** |
| traces / trace-years | 72 / 288.0 | 75 / 300.0 | +3 / **+12.0** |
| trace bytes (arrays) / MB per trace-year | 161.4 / 0.561 | 168.2 / 0.561 | +6.8 |
| trace-years per settled customer-year | 0.93 | 0.62 | |
| RSS right after the trace build | 1,802.9 MB | 1,744.4 MB | −58 |
| peak (`ru_maxrss`) | 2,099.9 MB | 2,141.2 MB | +41 |

- **Q1 holds:** 0.561 MB per trace-year, the same as at 40.
- **Q2 holds:** 485.9 settled customer-years, the same as the pre-array 160 run. Its record count
  (177,487) and account count (192) are also unchanged, as P5 at 40 founders implied they would be.
- **Q3 holds, only just:** 0.62, inside 0.6–1.0 and on the low side as I expected. But the reason
  is not the one I gave. Founder churn is not what keeps it down. The trace count hardly moves at
  all.
- **Q4 is refuted, below the "not the owner" line:** 1.296 × 12.0 / 177.1 = **0.088 MB per settled
  customer-year**, against the 1.35 slope and my predicted 0.7–1.3. **The fabric trace is not the
  founders slope.** Quadrupling the founders added 3 traces. The 40-founder reading, which put the
  trace at about 90% of the slope, was a coincidence of one book size: 288 trace-years happened
  to be close to 308.8 customer-years. The predecessor finding's own limit ("one book size cannot
  show a slope") was the right caution. This reading corrects that finding's open item 1, and the
  correction goes beside it.
  **Correction (2026-10-07, founders-only re-run):** this holds for the *campaign* book, where the
  trace count barely moves. Founders-only, the trace count grows with founders (21 → 60), and at
  the old list layout the trace was about 0.61 of the 1.35 founders-only slope, roughly 45%. At
  arrays it is 0.26 of 1.11. See `SEAT_FINDING_THE_FOUNDERS_ONLY_SLOPE_AT_CURRENT_CODE_2026-10-07.md`.
- **Q5 holds:** 2,141 MB. At this code the 40→160 peak difference is +41 MB over +177.1
  customer-years, about 0.23 MB each. **I cannot attribute that number.** The campaign settles 138
  wins at 40 founders and 32 at 160, so founder count and campaign share both changed.

**Why the trace count is nearly flat, and what is not yet established.** A trace exists per
fabric-eligible electricity premise. At this book size the eligible set is almost the same at 40
founders (with 138 campaign wins) and at 160 founders (with 32). That means eligibility is not
proportional to accounts. It may be capped by how the fabric path picks premises, which I have not
read. The array change still landed a real 12% peak saving at 40 founders, but it did not move the
slope, because the trace was never the slope.

## What is still open, and handed on

1. **Does a founders slope still exist at current code?** The 1.35 MB figure came from
   founders-only runs (campaign off) at code from before the post-end-wins fix and the arrays.
   Re-measure it founders-only at 40 and 160 on origin/main before looking for its owner. A slope
   that has gone needs no owner.
2. If it still exists, its owner is something that scales with accounts and is not the fabric
   trace. The term-loop locals and the treasury register are the next candidates.
