**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The settlement-ceiling curve re-taken at current code (2026-10-08)

**Subject.** `simulation/net_new_acquisition.py::SETTLEMENT_CUSTOMER_YEAR_BUDGET` (1,750) was priced
in `358d59a42` from the curve at `06b7c821a`
(`docs/observability/settlement_ceiling_slope_20261006.json`, 2.69 / 3.00 / 3.06 MB per committed
customer-year). That curve predates the array trace. `ad43a298a` measured current code on two small
legs at 1.22 MB per *settled* cy. This re-takes the curve at `bab18f073` with
`tools.settlement_ceiling_probe`, budgets 1,200 / 2,000 / 2,800 / 3,400 (the 2026-10-06 arguments,
all above the founders' own ~759 committed cy), and a new RssAnon leg: the parent polls the child's
`/proc/<pid>/status` every 0.5 s and keeps peak RssAnon / RssFile / RssShmem beside `ru_maxrss`.

## Pre-registration (written before the first point started)

- **P1.** The 1,200 point peaks at 2,300-2,900 MB `ru_maxrss` (06b7c821a: 4,036.6).
- **P2.** The `ru_maxrss` marginal is 1.0-1.6 MB per committed cy on every clean leg, worst < 2.0.
- **P3.** The RssAnon marginal is within 0.2 MB/cy of the `ru_maxrss` marginal: file pages do not
  grow with the book.
- **P4.** At 25% of the guest (~6,008 MB) the memory bound supports more customer-years than the
  funnel supplies, so the binding bound moves from memory to supply.

## Result

Lower half measured (`docs/observability/settlement_ceiling_slope_20261008.json`, both points
clean, no producer in flight). The arms re-take queued for the same box left ~4 GB of admission
headroom, so 1,200 and 2,000 ran now. 2,800 and 3,400 are queued behind it.

| budget | committed cy | wall s | `ru_maxrss` MB | RssAnon MB | RssFile MB |
|---|---|---|---|---|---|
| 1,200 | 1,194.7 | 1,086.3 | 2,694.5 | 2,563.0 | 139.1 |
| 2,000 | 1,999.3 | 2,315.7 | 3,818.7 | 3,688.7 | 139.2 |

Marginal: **1.397 MB per committed cy** (`ru_maxrss`), **1.399** (RssAnon), 1.53 s.

- **P1 holds.** 2,694.5 MB, in 2,300-2,900.
- **P2 holds on the one leg there is.** The marginal is 1.397, in 1.0-1.6. Whether the *worst* leg is
  under 2.0 waits on the upper points.
- **P3 holds.** The anon and total slopes agree to 0.002 MB/cy, and file pages do not move (139.1
  to 139.2). The whole marginal is anonymous memory the run holds.
- **P4: I cannot yet say.** The loader's cgroup-anchored line (2,921.5 MB at 1,194.7 + 1.397/cy)
  supports **3,404 cy** against 6,008 MB, above the 3,126 the old curve found the funnel exhausts
  at. Both points here still refused wins (413 and 252), so this run has not measured current
  supply. The 3,400 point answers it.

**What this re-prices.** `budgeted_run_peak_mb` at 1,750 falls from ~5,850 MB on the old curve
to 2,921.5 + 555.3 × 1.397 = **3,697 MB**, still above production's measured 3.3-3.4 GB cgroup
peaks (conservative, the right direction). The memory price of the budget moves from 1,770-1,804
to ~3,404. **The constant is NOT moved in this commit.** There are three reasons:
(a) one leg cannot show convexity, and the old curve was convex (2.69 → 3.06);
(b) the journal leg re-keys to bab18f073 and skips until a production lifetime runs that code;
(c) raising it changes the book every value-arms run measures (`run_value_cycle_ab` records the
budget because 1,050 → 1,750 took PROS-* accounts from 52 to 197), and a W2_20 arms re-take is in
flight now. The raise lands once the upper points are in, priced on the steepest leg and floored
to 50, as the 2026-10-07 re-price was.

**The ~460 MB at the 1,200 point is still unattributed.** RssAnon here is 2,563.0 MB, which
matches `ad43a298a`'s 2,563.9. File pages are 139 MB, which is what that finding subtracted. So
this instrument confirms the residual and does not name it. Naming it needs a pair on the old code.

## Upper points (2,800 / 3,400), merged and graded

`longjob-settlement-ceiling-retake-hi` ran both at `a44c436c6` in `/home/rich/wt-ceiling-retake`.
Both points were clean, with no producer in flight. Their rows are merged into
`docs/observability/settlement_ceiling_slope_20261008.json` (their own headroom samples are kept
under `upper_points_from`) and re-analysed with `tools.settlement_ceiling_probe --reanalyse`.

| budget | committed cy | wall s | `ru_maxrss` MB | RssAnon MB | wins | refused |
|---|---|---|---|---|---|---|
| 2,800 | 2,796.7 | 4,215.6 | 4,908.1 | 4,893.2 | 421 | 76 |
| 3,400 | 3,126.1 | 5,037.1 | 5,479.0 | 5,390.2 | 497 | **0** |

| leg | MB/cy (`ru_maxrss`) | MB/cy (RssAnon) | s/cy |
|---|---|---|---|
| 1,194.7 → 1,999.3 | 1.397 | 1.399 | 1.53 |
| 1,999.3 → 2,796.7 | 1.366 | 1.511 | 2.38 |
| 2,796.7 → 3,126.1 | **1.733** | 1.509 | 2.49 |

- **P2 holds.** The worst leg is 1.733 MB/cy, under 2.0. It is the shortest leg (329 cy). Its
  RssAnon slope (1.509) matches the leg below it, so the 0.22 jump in `ru_maxrss` is
  probably sampling noise in the peak, not convexity. I cannot tell that from two points, so I
  price on 1.733 anyway, because that is the conservative direction.
- **P3 weakens but holds within its band.** On the upper two legs the anon slope and the total
  slope differ by 0.145 and 0.224 MB/cy. That is at the edge of the 0.2 band on the last leg.
  File pages stay flat (137, 134).
- **P4: it splits by instrument, and I say which reading is which.** *Measured:* supply binds
  first. 3,400 refused no wins, and the funnel exhausts at **3,126.1 cy / 497 wins**, the same
  3,126 the 2026-10-06 curve found. The run that reached it peaked at 5,479 MB, under the
  6,008 MB that 25% of the guest allows. *Priced:* the probe extrapolates the steepest leg from
  the 1,200 point: 2,694.5 + (cy − 1,194.7) × 1.7332 ≤ 6,008. That supports **3,106.5 cy**, so
  on the conservative price memory binds about 20 cy (0.6%) before supply. That price is what
  `binding_bound: memory` reports. On the number the constant is priced from, P4 fails narrowly.
  On the measured point it holds.
- **Time is convex where memory is not.** s/cy goes 1.53 → 2.38 → 2.49, and a full-window run at
  supply takes 84 min. The time bound stays undecidable (`publish_gate_duration.jsonl` is
  absent). The memory price does not cover it.

**The raise, priced and not yet landed.** Pricing the steepest clean leg against 25% of the
guest and flooring to 50 gives **SETTLEMENT_CUSTOMER_YEAR_BUDGET = 3,100** (from 1,750). Its
`budgeted_run_peak_mb` on the same line is 2,694.5 + 1,905.3 × 1.7332 = 5,997 MB. In practice
3,100 removes the ceiling: it refuses about 26 cy of a 3,126 cy supply. So the book a run
settles becomes the funnel's book, not the box's. The raise is NOT in this commit, because
`longjob-w220-nine-seed-handoff` and `longjob-w220-recov-leg2-handoff` were active at
11:58. Raising the budget changes the book every value-arms run measures, so it would split that
series across two worlds. The raise is handed off with an embargo set to the end of that series.
