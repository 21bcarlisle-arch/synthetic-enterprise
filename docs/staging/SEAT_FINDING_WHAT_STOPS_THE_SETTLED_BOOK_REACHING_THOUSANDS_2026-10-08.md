**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `what-stops-the-everyday-settled-book-reaching-thousands`

# What stops the everyday settled book reaching a few thousand customers, and what each fix costs

Director's item 3. This finding answers from the evidence already landed. **No new run was made.** The sources are:
`SEAT_FINDING_THE_40_AND_160_FOUNDER_PEAKS_MEASURE_THE_CAMPAIGN_NOT_THE_BOOK_2026-10-07.md`,
`…_FOUNDERS_ONLY_SLOPE_AT_CURRENT_CODE_…`, `…_FOUNDERS_SLOPE_UNRETURNED_015_BY_TYPE_…`,
`…_FABRIC_TRACE_ALIVE_AT_THE_FOUNDERS_PEAK_…` (all 2026-10-07),
`SEAT_FINDING_FLOAT32_TRACE_DAYS_HOLD_SETTLEMENT_AND_LOWER_THE_FOUNDERS_PEAK_50_MB_2026-10-08.md`
(the queued float32 result, landed `f12ba4b90`), the live-path curve
`docs/observability/settlement_ceiling_slope_20261006.json`, and the production run
`docs/reports/run_output_latest.json`.

## First, what "the everyday book" is (one correction)

**It is 80 founders, not about 175.** `docs/design/FOUNDER_BOOK.yaml` sets `founder_accounts: 80`
(the director's ruling of 2026-08-28), with `max_founder_accounts: 120`. "About 175" is an
**account** count: 80 founders plus the ~96 campaign wins the settlement budget lets settle. The
note on `SETTLEMENT_CUSTOMER_YEAR_BUDGET` (`simulation/net_new_acquisition.py`, "~175 founders")
carries the same slip. The latest production run reads 503 funnel wins in ten years, **156 accounts
on supply at the end** (`margin_call_book.accounts_held`) and 302 direct-debit accounts ever booked.

**The units, before dividing.** The budget, the curve and every MB-per-customer-year below are in
**budget customer-years**: supply-leg-years, with electricity and gas counted separately, charged to
the 2026-01-01 horizon. In a full-window run, committed and settled are the same thing. Production
spends 1,750 of them to hold 156 accounts at the end, so this growth shape costs **about 11.2
customer-years per account held at the end**. "A few thousand customers" is taken as 3,000 accounts
on supply at the end of the window, grown the way production grows. That is **about 33,700
customer-years**. For 1,000 accounts it is about 11,200.

## The cost model, and which half of it is understood

The live path (`tools.run_annual_report._run_and_extract`, full window, at `06b7c821a`) was measured at
four budgets:

| committed cy | peak RSS | wall | wins refused by the budget |
|---|---|---|---|
| 1,199.7 | 4,036.6 MB | 1,314.5 s | 412 of 497 |
| 1,986.9 | 6,154.7 MB | 2,808.7 s | 254 |
| 2,794.7 | 8,579.6 MB | 4,876.8 s | 77 |
| 3,126.1 | 9,592.8 MB | 5,558.0 s | **0** |

The marginal cost is **2.69–3.06 MB and 1.9–2.56 s per customer-year**, with 2.884 MB as the average.
Only the **founders-only** slope has been taken apart: 1.11 MB/cy at `9bbc0e751`, about 1.02 after
float32. It splits into records 0.57 (with allocator overhead), the trace 0.227 (now ~0.14), treasury
path 0.03, transient at the peak 0.10, and ~0.07 unnamed. The freed trace's pymalloc slack (0.245)
falls after the peak, so it does not count toward it.

**The live path costs about 1.8 MB per customer-year more than that founders-only path, and I cannot yet
say what that 1.8 is.** *[Answered by step #4 below: it is the curve's old code, mainly the list-based trace. At `20719d272` a campaign customer-year costs 1.22 MB per settled cy, against the founders' ~1.02.]* It is the largest share by far. The candidates, ranked by evidence:

- (a) the term-loop local that grows with *accounts in the book × loop length* and is freed as the
  loop ends. It was 956 MB at 40 founders in `bridge40` and was never named.
- (b) campaign wins costing 4–6.7 MB per settled year against a founder's ~1.1. That is measured,
  but not explained.
- (c) the annual-report extract, which the founders probes skipped (`--no-extract`).
- (d) the curve predating the array and float32 trace. That accounts for ~0.07 of the 1.8 at most:
  the campaign marginal carries ~0.07 trace-years per customer-year. **[Corrected 2026-10-08, step #4 below: measured 1.16 trace-years per settled cy, so (d) owns ~1.07 of the 1.8, and the gap is absent at current code.]**

## The blockers, in the order they bind

| # | blocker | cost per customer-year | fix | fix's cost | customer-years reached (accounts held at the end) |
|---|---|---|---|---|---|
| 1 | **The memory share.** The budget is priced against 0.25 × guest = 6,008 MB, a policy, because other lanes run beside it | — | Run settlement alone, against `available_mb` read live (11,509.6 MB at 2026-10-08T00:00Z) | No code. A scheduling decision: no other large job while it runs | 1,883 → **3,791** cy (168 → ~338). **Every funnel win fits today**: 3,126 cy measured at 9,593 MB |
| 2 | **The budget constant** `SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1750` | — | Re-price it from the same curve against whichever share #1 picks | A constant and its existing control (`test_the_settlement_ceiling_does_not_outrun_the_measured_memory_curve`). Minutes | Same as #1. The budget is a consequence, not a lever |
| 3 | **The funnel and the founder file** (not compute) | — | More accounts to settle. Either `founder_accounts` above the file's cap of 120 (curriculum, the director's), or a campaign that wins ~10× its 503 (company side) | A curriculum act, or a growth design. Not compute work | Past ~3,126 cy **no compute fix adds a single account**. This world's funnel is exhausted at ~280 held |
| 4 | **The unattributed live-path ~1.8 MB/cy** | ~1.8 MB | Name it first. Two type-census legs on the live path (budgets 1,200 and 2,000) with the instrument's own id-set excluded, never tracemalloc | ~70 min wall, peak ~6.2 GB, one leg at a time | If it goes, the slope falls to ~0.44: 5,640 cy (~500) at the share, **18,031 cy (~1,600)** on the free box |
| 5 | **The records** (`all_records`, 365 dicts with 33 keys each per customer-year, held all run; 45% of their allocator bytes are dict key tables) | 0.57 MB | (i) `__slots__` or tuple rows: −0.26. (ii) Fold or spill them like `SettlementFold` already does for the EAC scans: −0.57 | (i) ~1 day. One record type, `rec["k"]` read sites across 45 files. (ii) Several days. Every reader of `all_records` becomes a fold, each with an exactness test against the list scan (the `test_settlement_fold.py` pattern) | (i) 1,972 / 4,126 cy. (ii) 2,078 / 4,530 cy (~185 / ~404) |
| 6 | **The fabric trace** | ~0.07 on the live marginal, 0.14 on founders | Done: arrays (`046c6a9b1`) then float32 (`f12ba4b90`, −49.8 MB at 160 founders) | Spent | 1,900 / 3,855 cy. Making the trace returnable to the OS cannot move the peak, because the trace is freed 0.5 s after it |
| 7 | **"Streamed or chunked settlement"** | — | **Not a fix in itself.** Every leg rises monotonically to the end of the term loop with no year sawtooth, so nothing is one-year-held state. Chunking pays only as the *spill* half of #5(ii) | Counted in #5(ii) | — |
| 8 | **Wall time** | 1.9–2.56 s | None measured | — | Not binding for publishing: the director's 604,800 s interval allows ~118,800 cy. It **is** binding for calibration. 3,000 accounts ≈ 17.5–23.4 h per run, and value-arm passes multiply that |

The projections use `peak = 4,036.6 MB + slope × (cy − 1,199.7)`, the live curve's own first point,
and subtract each lever's saving cumulatively down the table. A founders-measured saving is applied
to the live slope only where it is per record or per trace-year, which is the same whoever settles.

## The answer

*[The projections in this section use the old 2.884 slope. Step #4 below re-prices them at 1.27 per committed cy: 1,000 accounts ≈ 15.3 GB, 3,000 ≈ 44 GB. The conclusion for 3,000 stands; 1,000 no longer depends on #4.]* **A book of a few thousand cannot be carried by any fix measured or priced so far.** 3,000 accounts
held is ~33,700 cy. On the whole free box that needs ≤ 0.23 MB per customer-year, and ≤ 0.06 at
the 6 GB share. With every priced lever taken, including the unnamed 1.8 removed, the slope is still
~0.44. Getting below 0.23 needs the records folded (#5ii) **and** the 1.8 named and removed, and
then a further halving of what is left. 1,000 accounts (~11,200 cy, ≤ 0.75 MB/cy on the free box) is
reachable **only if #4 turns out to be removable**.

**The cheapest step is not compute at all.** Running settlement alone (#1) already holds every win
this world's funnel makes. The book then tops out at ~280 accounts because there is nobody else to
settle. So the director's question splits in two:

1. **Calibration on a realistic book.** That needs more accounts *to settle*: founders above 120 or a
   bigger funnel. That is #3 and is his.
2. **Compute to carry them.** #4 is the next measurement and decides whether 1,000+ is in reach.
   #5(ii) is the build after it.

**Recommendation:** run #4 next, as the one-variable measurement of where the 1.8 lives. Price #3 as
a curriculum menu in the meantime: founder counts of 120, 500 and 1,000 against the projected peak
at the founders-only slope. Do not build #5 until #4 says whether the records are still the largest
owner on the live path.

## Not established

- The 1.8 MB/cy live-path gap (above).
- The note on the budget records "a 4,000-founder book takes 5,363 MB before any campaign settles".
  The founders-only slope says 4,000 × ~9.7 cy × 1.02 ≈ 40 GB. Both cannot hold for a full-window
  run. Either the 5,363 was a shorter window, or the slope is not linear that far. Unresolved; it
  bears directly on #3's menu.
- Every MB figure is one process's `ru_maxrss`. Production `sim-runner.service` peaked at 3.3–3.4 GB
  at budget 1,750 (cgroup), *below* this curve's 5,851 at the same budget. So the curve over-prices
  production, and the reach above is conservative by an amount not yet measured.

## Step #4 on small runs: pre-registration (written 2026-10-08 ~04:00 UTC, before either leg)

The director ordered small runs only. Two legs at `20719d272` (= origin/main), full window,
default 80 founders and default seed, through `_run_and_extract(report_end=None)`, the call
`sim_runner` makes. **F**: budget 0 (founders only). **L**: budget 600. Instrument
`/var/tmp/live-vs-founders/lvf.py`. A 0.5 s sampler reads RssAnon, RssFile, RssShmem and VmSwap
plus the fabric trace days alive. The traces are deep-sized when `fabric_providers_for_book`
returns. A type census runs at the return of `run_phase2b`, with its own containers sized apart.
Both instrument windows are cut out of the peak. No tracemalloc. Headroom at launch:
`available_mb` 14,705.6 of 24,032.1. Settled customer-years = records ÷ 365.

Two facts found while setting this up bear on the predictions:

- **Every fabric trace covers the whole window, whenever its account joined**
  (`simulation/fabric_demand_path.py:733-744`, `start=start`). A win that settles two years
  still carries a ten-year trace. So a campaign customer-year can carry more trace-years than a
  founder's.
- **The live curve was taken at `06b7c821a`, before the trace became arrays** (`046c6a9b1`). A
  trace-year then cost 1.296 MB as lists, against 0.561 as arrays
  (`SEAT_FINDING_THE_FABRIC_TRACE_AS_ARRAYS_AND_THE_FOUNDERS_SLOPE_2026-10-07.md`), and less again
  since float32. Candidate (d) above caps the old-code share at ~0.07 MB/cy, on the assumption of
  ~0.07 trace-years per campaign customer-year. That assumption is now in question.

- **P1.** L's marginal, (peak RssAnon L − F) ÷ (settled cy L − F), is **1.0–2.0 MB/cy** at current
  code. **Refuted, and the gap is not old code, if ≥ 2.5.**
- **P2.** Trace-years per settled customer-year in the campaign increment are **≥ 1.5×** the
  founders' ratio in F.
- **P3.** The peak falls inside phase 2b in both legs, so the extract (candidate c) does not set it.
- **P4.** Of the census increment L − F at the return of phase 2b, record-shaped labels (`dict`,
  `list of dict`, `float`, `str`) make up **≥ 60%**.
- Recorded, not predicted: RssFile + RssShmem at the peak. `ru_maxrss` counts them, but a cgroup
  charges file pages only to the first process that faults them in. Their size bounds how much of
  the curve-vs-production gap is the instrument.

**First pair VOID (kept in `/var/tmp/live-vs-founders/void1/`).** L at budget 600 was identical to F:
the same 79 customers, the same 140,467 records, a peak of 2,007.0 against 2,008.0 MB, and
`customer_years_committed` 758.6 in both. **The budget counts the founders' own customer-years.**
`_resolve_campaign` starts from `existing_cy` for the book it is handed, and 80 founders commit 758.6
to the 2026 horizon on their own. So a budget of 600 admits no win, and so does any budget below
~759. This also re-reads the live curve: its 1,199.7 committed at budget 1,200 is **~759 founder +
~441 campaign**, not 1,200 of campaign. The pre-registration stands as written. L moves to
**budget 1,200**, the curve's own first point, and both legs now record settled customer-years
the earlier probes' way (distinct customer-leg × settlement date ÷ 365.25), not records ÷ 365.

## Step #4 result: the 1.8 MB/cy is the old code's trace, and the gap is gone at current code

Legs `F.json` and `L.json` in `/var/tmp/live-vs-founders/`, both at `20719d272`, run side by side,
with 17.4 GB available at launch and no swap in either.

| | F (budget 0) | L (budget 1,200) | L − F |
|---|---|---|---|
| accounts settled (customer legs) | 79 | 221 | +142 |
| committed cy (budget units) | 758.6 | 1,194.7 | +436.1 |
| **settled** cy (distinct leg × date ÷ 365.25) | 384.6 | 841.3 | +456.7 |
| fabric traces / trace-years | 45 / 424.6 | 101 / 952.9 | +528.3 |
| trace deep size (MB per trace-year 0.377 in both) | 160.2 | 359.7 | +199.5 |
| census at phase-2b return (instrument excluded) | 1,147.3 | 1,406.2 | +258.7 |
| **peak RssAnon** (instrument windows cut out) | 2,008.7 | 2,563.9 | **+555.2** |
| RssFile + RssShmem, max | 138.6 | 138.7 | 0 |
| max RssAnon after phase 2b (the extract) | 1,911.7 | 2,503.8 | |
| wall | 561.5 s | 1,051.3 s | +489.8 s |

**The campaign's marginal at current code is 1.22 MB per settled cy** (1.27 per committed cy). It
is named to within 0.21:

| component | MB per settled cy |
|---|---|
| records: `dict` +245.6 MB, `list of float` +10.7, `list of dict` +1.7 (99.7% of the census increment) | **0.567** |
| fabric trace (1.16 trace-years per settled cy × 0.377 MB) | **0.437** |
| remainder: allocator overhead on the records (≈0.08 by the 1.156 ratio already measured) and transient at the peak | 0.21 |

- **P1 holds** at 1.22 (registered band 1.0–2.0). A founder customer-year costs ~1.02 and a
  campaign customer-year ~1.22, so **the ~1.8 MB/cy that sets them apart in the old curve does
  not exist at current code.**
- **P2 is refuted.** Trace-years per settled cy are 1.10 for founders and 1.16 for the campaign
  increment: 1.05×, not ≥ 1.5×. The whole-window trace does not make a campaign year dearer here.
  The wins this budget admits are early enough to settle about as long as their trace.
- **P3 holds.** Both peaks fall inside phase 2b, 4–5 s before it returns, and the extract never
  reaches them. Candidate (c) is out.
- **P4 holds.** Record-shaped labels carry 99.7% of the census increment. The records cost 0.567
  per settled cy for a campaign win, the same 0.57 measured for founders.
- **Recorded.** File and shmem pages are a flat ~139 MB in both legs. They are part of the
  `ru_maxrss` intercept and none of the slope.

**So who owns the 1.8: the curve's date (candidate d), and the ~0.07 cap on it above was wrong.**
That cap assumed ~0.07 trace-years per campaign customer-year; the measured figure is 1.16. At
`06b7c821a` a trace-year cost 1.296 MB as lists. 1.16 × (1.296 − 0.377) = **~1.07 MB per settled
cy** is the trace layout alone. The same budget point fell from 4,036.6 MB (`ru_maxrss`, old code,
1,199.7 committed) to 2,563.9 MB RssAnon (now, 1,194.7 committed). Of that 1,473 MB, ~876 MB is the
trace (952.9 trace-years × 0.919) and ~139 MB is the file pages the old instrument counted. **The
other ~460 MB I cannot yet say**: 06b7c821a → 20719d272 is many commits, and this pair did not run
the old code. The live curve `settlement_ceiling_slope_20261006.json` is stale as a price of
current code. It over-prices by ~2.3× in slope, which is also why production (3.3–4.0 GB cgroup
at budget 1,750) sat far below it. The current-code line, `peak ≈ 2,009 + 1.27 × (committed −
758.6)`, gives **3,268 MB at 1,750**, the production figure.

**Units, corrected beside the earlier claims.** The budget counts the founders' own committed
years, and **a founder commits ~2× what it settles** (758.6 against 384.6, because founders churn
before the 2026 horizon). A campaign win commits about what it settles (436.1 against 456.7). A
per-settled-cy slope multiplied by committed cy therefore over-prices a founder-heavy book by up
to ~2×. The blocker table above priced every row on the old 2.884 slope. Its reach figures are
conservative by roughly that 2.3×, and **its row #4 is closed**: there is no removable 1.8 to
take out. With the current slope, 1,000 accounts held (~11,200 committed cy, campaign-shaped) projects to
~2,009 + 1.27 × 10,440 ≈ **15.3 GB**, inside the free box but not the 6 GB share. 3,000 accounts
(~33,700 cy) is ~44 GB and still out of reach without #5(ii). The recommendation changes: **#5
(the records, 0.57 of 1.22) and the trace (0.44) are now the two owners. Re-take the ceiling curve at
current code** before re-pricing `SETTLEMENT_CUSTOMER_YEAR_BUDGET` (#2).
