**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `founders-only-slope-at-current-code`

# Does the 1.35 MB founders-only slope survive the post-end-wins fix and the array trace?

Follows "What is still open" item 1 in `SEAT_FINDING_THE_FABRIC_TRACE_AT_160_FOUNDERS_2026-10-07.md`.

## Premise, checked when this was drawn (2026-10-07 ~20:20Z)

- Executor worktree HEAD equals origin/main (`9bbc0e751`). Since the ctl legs' code (`318162387`),
  three commits touched `simulation/`: `a21890675` (entry-point memory refusal), `3e752c8f8` (no
  fabric traces for wins a short run never settles), `046c6a9b1` (traces stored as `array('d')`).
- **Duplicate-work note:** the live claim it named is this draw's own id (my process was 9 s old;
  no rival probe or `surgical_land` on this subject in `ps`). Carried on, not a duplicate.

## Pre-registration (written before either run)

Instrument: `/var/tmp/scale-shape-ctl/scale_series_probe.py --end 2019-12-31 --no-extract`, wrapped
by `/var/tmp/scale-shape-ctl/ctl0_wrap.py`, which sets
`simulation.net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET = 0.0` before the probe runs (the
campaign reads it at call time; the probe's `campaign.customer_year_budget` must read 0.0 or the
leg is void). Legs: 40 and 160 founders (`ctl0_40.json`, `ctl0_160.json`), run concurrently — RSS
is per-process, so concurrency moves wall time, not peak. One variable against `ctl40`/`ctl160`:
the code.

- **P1, the book.** Identical to ctl: 37 / 157 accounts, 89.7 / 422.5 settled customer-years.
  None of the three commits touches what a founder settles.
- **P2, the 40 peak.** 1,550–1,800 MB (ctl40: 1,764). Arrays shave whatever traces a 37-account
  book carries; `3e752c8f8` removes nothing when no win settles anyway.
- **P3, the slope.** `(peak160 − peak40) / (422.5 − 89.7)`. I predict **0.8–1.4 MB per settled
  customer-year, central ~1.05**: founders-only trace count should grow with founders (unlike the
  campaign mix in armB), so at list code part of the 1.35 was trace (~1.3 MB per trace-year), and
  arrays cut that part to ~0.56. **The slope "still exists" if ≥ 0.6 MB; it is gone if < 0.3;**
  between, it is diminished and I say so.
- **P4, the trace share.** Traces at 40 ≤ 37 and at 160 between 37 and 157. Trace bytes explain
  ≤ 0.3 MB of the slope at array layout.

**Added after P1–P4 were graded (the two legs gave a ~0.85 MB non-trace residue, ~2.3 KB per
added settled record), before the run that tests it:** `/var/tmp/scale-shape-ctl/ctl0_recsize.py`,
founders-only, deep `sys.getsizeof` over the run result's `all_records` (shared objects counted
once) at 40 and 160 founders.

- **P5.** 1.5–3.5 KB per record, and the record list's 40→160 difference explains **≥ 0.55 MB** of
  the ~0.85 MB per settled customer-year residue. If it explains < 0.3, the records are not the
  owner and I say what the result dict's largest other entries are.

## Result

Outputs: `/var/tmp/scale-shape-ctl/ctl0_40.json`, `ctl0_160.json` (walls 115 s / 399 s) and
`recsize_40.json`, `recsize_160.json`. Both legs read `customer_year_budget: 0.0`, so they are valid.

| | ctl40 (`318162387`) | **ctl0_40 (`9bbc0e751`)** | ctl160 (`318162387`) | **ctl0_160 (`9bbc0e751`)** |
|---|---|---|---|---|
| accounts / settled customer-years | 37 / 89.7 | 37 / 89.7 | 157 / 422.5 | 157 / 422.5 |
| peak (`ru_maxrss`) | 1,764.1 MB | **1,667.7 MB** | 2,214.2 MB | **2,038.4 MB** |
| traces / trace-years | — | 21 / 84.0 | — | 60 / 240.0 |
| trace bytes (arrays) | — | 47.1 MB | — | 134.5 MB |
| `all_records` deep size | — | 43.8 MB (1.37 KB × 32,757) | — | 206.7 MB (1.37 KB × 154,308) |

- **P1 holds exactly:** same accounts, customer-years, record count and event count as ctl.
- **P2 holds:** 1,667.7 MB, −96 MB against ctl40. Converting the 84 trace-years from lists to
  arrays predicts −62 MB. At 160 it predicts −176 MB (240 × 0.735), and the measured change is
  −175.8 MB. **The whole code-change saving is the array layout.**
- **P3 holds, and the slope still exists:** (2,038.4 − 1,667.7) / 332.8 = **1.11 MB per settled
  customer-year** (predicted 0.8–1.4, central 1.05; ctl was 1.35). The implied base at zero settled
  years is about 1,567 MB.
- **P4 holds:** traces go 21 → 60. Unlike the campaign book in armB, the founders-only trace count
  grows with founders. At the array layout the trace is 0.561 × 156 / 332.8 = **0.26 MB** of the
  slope. At the list layout it was 1.296 × 156 / 332.8 = 0.61. So the trace *was* about 45% of the
  old founders-only 1.35. The 160-founder finding ruled it out only for the campaign book, where the
  trace count does not grow.
- **P5 fails narrowly, low on both counts:** 1.37 KB per record (predicted 1.5–3.5), and the record
  list explains (206.7 − 43.8) / 332.8 = **0.49 MB** of the slope (predicted ≥ 0.55). It is the
  largest single owner, not the whole of it. The next largest entry in the returned result is
  `treasury_drawdown_path`, at 0.03 MB per settled customer-year.

**The slope at current code, decomposed** (per settled customer-year):

| owner | MB | how it was established |
|---|---|---|
| `all_records`, held in the result (33 keys, 1.37 KB each, 365 per customer-year) | 0.49 | deep size, both legs |
| fabric trace (`array('d')`) | 0.26 | probe's trace bytes, both legs |
| `treasury_drawdown_path` | 0.03 | deep size, both legs |
| **unattributed** | **~0.33** | RSS minus the three above |

The unattributed 0.33 is not in any object the run returns. **I cannot yet say what it is.**
Candidates, ranked by evidence: pymalloc arena slack from the ~120k extra dicts (RSS is not the
sum of `getsizeof`), transient per-day structures freed before return, or a second copy of the
records (for example a per-account index) that is dropped by the end of phase 2b.

## What this changes, and what is handed on

- The scale finding's 1.35 MB per settled customer-year is now **1.11 at origin/main**, with three
  quarters of it owned: 0.49 records, 0.26 trace, 0.03 treasury. Any extrapolation to thousands of
  founders should use 1.11 and this split, never 1.35.
- **The records are the lever.** 1.37 KB × 365 per customer-year is about 0.5 MB, held for the whole
  run. A narrower record (`__slots__` or tuples instead of 33-key dicts), or folding records into
  per-account aggregates as the run goes, would act on the largest owned share. That is a design
  question about what the downstream report reads from `all_records`, not a number to tune.
- **Open:** the unattributed ~0.33. The one-variable test is `tracemalloc` snapshots at the end
  of phase 2b in both legs, comparing traced-but-unreturned allocations by file and line. If the
  traced total matches the returned objects, the residue is allocator slack.
