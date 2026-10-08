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
