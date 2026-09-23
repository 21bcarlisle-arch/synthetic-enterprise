**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the cost curve was stale, not the box contended, and the ceiling's last leg is still an interval nobody has named

**Filed:** 2026-09-21, 18:45 local. Drawn as Lane 0 delivery,
`the-capacity-that-refuses-the-thesis-book-stands-on-nothing`.

**DO NOT DRAW BEFORE 20:30 on 2026-09-21.** Two of the probe's four points are still running (see
§5). The measurement is in flight, not stalled, and re-drawing this item before the artefact is
written spends an invocation re-deriving what the cache already holds.

---

## What was drawn, and what was already true

The item had two halves. **Both already had a prior invocation's work on this box**, and the first
thing this turn did was establish that rather than start again:

- **(b) the two published denominators.** Already answered, and sitting UNCOMMITTED in the working
  tree — generator, feed, control test and the correction block on
  `WORKER_RESULT_THE_TWO_CEILINGS_SHARE_A_RULER_NOW_...`. Landed by this commit. The answer is that
  **neither denominator was stale**: the staging table multiplied the `current_world` panel's
  multiple (2.8198526, a multiple of the 2026-09-08 book) by the *promoted* 2026-09-18 run's 1,029
  customer-years. The product is a ratio across two runs. The feed's 3,163.9 / 2.64x were right the
  whole time. The item's own framing — *"one denominator is a run stale"* — is the thing that was
  wrong.
- **(a) the measurement.** Already LAUNCHED, at 16:38, behind a `wait_for` on the live producer and
  a `.sim_runner_hold`. Points 1 and 2 of 4 had completed before this turn began.

So this document reports a measurement it did not start. What it adds is the reading of the two
completed points, and two control defects found in the instrument while reading them.

## 1. The question the item said this would settle first, settled

> *"the run completing on this box today took 1,450s at 1,122 customer-years, about 1.5x what that
> curve predicts, so either the curve is stale or the box was contended — which it is, is the first
> thing this measurement settles."*

**The curve is stale. The box was not contended.** Point 1 is a direct replication of the
2026-08-29 point at the same budget, with the live producer held down:

| | date | budget | committed cy | wall clock | producer in flight |
|---|---|---|---|---|---|
| old point | 2026-08-29 | 1,200 | 1,200.0 | 1,018.7s | none |
| **replication** | **2026-09-21** | **1,200** | **1,197.0** | **1,494.1s** | **none** |

**1.467x, on essentially the same book, with nothing else on the box.** The `.sim_runner_hold` flag
has been in place since 16:38 and `a_run_is_in_flight()` returned `None` at both ends of the point.
The 1.5x the item saw in the wild is not contention — it is what this code now costs.

## 2. The curve, and it is convex

| point | committed cy | wall clock | old curve predicts | ratio |
|---|---|---|---|---|
| 1 | 1,197.0 | 1,494.1s | 1,016.7s | 1.470x |
| 2 | 1,995.2 | 2,660.9s | 1,554.0s | 1.712x |

- **Marginal slope, 1,197 → 1,995: 1.462 s per customer-year.** The old curve's slope was
  0.673 s/cy. **2.17x.**
- **The implied intercept is NEGATIVE (−255.8s), which refutes the linear model rather than
  describing the run.** A run with a real fixed component cannot have one. What a negative implied
  intercept means is that the *secant* slope (1.462) exceeds the *average* slope
  (1,494.1 / 1,197 = 1.248): marginal cost is above average cost, so **the curve is convex over this
  range** and every linear extrapolation beyond 1,995 cy is a LOWER BOUND, not an estimate.

The ratio column rising (1.470 → 1.712) is the same fact said the other way.

## 3. What that does to the thesis book — and the answer is not "unreachable"

The smallest leg of `what_would_settle_the_sign` needs **3,163.9 customer-years** (the feed's
figure, on the panel's own book — see the correction landed with this commit).

| interval | seconds | smallest leg at ≥4,369s | fits? |
|---|---|---|---|
| `PUBLISH_CADENCE_SECONDS` (live) | 1,500 | 4,369s | **no**, by 2.9x |
| 90 minutes | 5,400 | 4,369s | yes |
| daily | 86,400 | 4,369s | yes |
| weekly | 604,800 | 4,369s | yes |

**≥4,369s ≈ 73 minutes** — linear from the secant, so a floor, and point 4 will measure it directly
rather than extrapolate to it (§5).

**The filed prediction is REFUTED on its number and survives on its conclusion, and it is kept here
beside the result rather than revised.** It said *"roughly 2,300s on a quiet box"*. The real figure
is at least 4,369s — **1.9x** the prediction. The item itself named the escape and took it
honestly: *"if the curve is stale my prediction is probably wrong."* It is stale, and it is wrong.

The conclusion it drew — *"wall clock will not bound it either, and 1,200 will turn out to be
bounded by nothing"* — **survives, conditionally, and the condition is the whole point**:

- **memory does not bind** — re-ruled to the records the book actually retains, 38,275 cy, about
  twelve times what the smallest leg needs;
- **external data freshness does not bind** — §7 of `SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md`
  established the requirement is **zero**, because `run_phase2b.REPORT_END` + `RF_MONTHS` reached
  Final Reconciliation on 2026-08-07;
- **wall clock binds only against an interval nobody has named.** The one named interval,
  `PUBLISH_CADENCE_SECONDS = 1,500s`, is defined by its own comment as *a measurement of how often
  runs arrive* — the circular ruler §7 removed from the constant, and the subject of
  `WORKER_FINDING_THE_INTERVAL_THE_CEILING_WAITS_ON_WAS_NAMED_SEVENTEEN_DAYS_AGO_...`.

**And measured, at the current ceiling, the run now consumes 1,494.1s of a 1,500-second cadence —
99.6% of it.** That is not evidence the cadence sets the ceiling; under a definition that moves with
the run it is close to a tautology, and it is reported here as one. What it does establish is that
the comfortable 68% of 2026-08-29 is gone, so *any* argument resting on "the run fits the cycle"
has stopped being true without anything noticing.

**So the answer to the item's "what actually bounds 1,200" is: nothing measurable does.** On a
weekly interval, a daily one, or even a 90-minute one, the book that would sign the choosing is
reachable on this box. The thesis is refused by an interval preference, and the interval is the
director's to name — §7 located it there and this measurement does not move it.

## 4. Two control defects in the instrument, found while reading it

Both are in `tools/settlement_ceiling_probe.cleanliness`. Neither changes §1–§3; both are filed
because the next reader of this probe will hit them.

**4a. At the live budget, the provenance check is STRUCTURALLY UNABLE TO FAIL.** The check compares
the child's in-process `customer_years_committed` against `docs/observability/book_growth_campaign.json`
on disk. Point 1 passed it — 1,197.0 == 1,197.0. But the parent's own snapshot of that file, taken
at **16:42, thirty-seven minutes before point 1 finished**, already read **1,197.0 at budget 1,200**:
that is the live producer's record, at the live ceiling. So the check would have agreed **whether or
not the child ever wrote the file**. It agrees with every answer, which is the shape the catalogue
names. It can only discriminate at a budget the live book is not already at.

**4b. It then over-reads its own disagreement, and the cost is the slope this probe exists for.**
Point 2 is marked **unclean**, reason `campaign_record_agrees: False`, whose message reads *"this
point's committed customer-years are not its own"*. That is not what was established.
`customer_years_committed` is read from `LAST_CAMPAIGN`, an **in-process module global** — it is
definitionally the child's own, and no disk write can touch it. What the disagreement establishes is
that *the shared artefact* was written by somebody else, which is a **contention** signal, not a
**provenance** one. The two are labelled the wrong way round, and because `marginal_costs` filters
on `clean`, the probe's final artefact will decline to report the 1,197 → 1,995 slope — the single
number the whole instrument was built to produce — on evidence that does not bear on it.

The slope in §2 is computed here from the raw points for that reason, and the wall clocks are
untouched by either defect.

**4c, and it is this session's own:** the contamination field watches for **one** kind of neighbour,
the live producer. It cannot see a gate run. Points 3 and 4 overlap this commit's gate chain, so
their wall clocks carry that and must be read with it. Said here rather than left for someone to
infer from a timestamp.

## 5. What is still running, and what it will answer

`tools.settlement_ceiling_probe --budgets 1200 2000 2800 3400 --publish-interval 604800
--menu-intervals 5400 86400 604800`, PID 860819, launched 16:38.

- **Point 3 (budget 2,800)** — in flight since 18:04; the shared record shows it committed 2,799.3,
  so the funnel supplies it and this is a genuine third x. Expected ~18:57.
- **Point 4 (budget 3,400)** — expected to finish ~20:15. **It brackets the smallest leg's 3,163.9
  customer-years directly**, so the next invocation gets a MEASURED cost for the thesis book instead
  of the convex-lower-bound extrapolation in §3.

Points land in `~/.cache/synthetic-enterprise/settlement_ceiling_probe/point_<budget>.json` as they
complete, so the run survives this invocation ending.

## What is left, and it is one thing

**The constant does not yet carry its origin, and that is deliberate, not unfinished.** Writing a
measured cost curve into `SETTLEMENT_CUSTOMER_YEAR_BUDGET`'s note on two of four points — when point
4 measures the load-bearing book size directly and arrives in ninety minutes — would put a figure in
the code that the artefact refutes the same evening. The next invocation on this claim writes it,
from the completed artefact, with the interval menu the probe was launched to price.

**The direction question is unchanged and is now priced.** The ceiling's last leg is an interval,
the interval is a preference and not a measurement, and the menu is: at **90 minutes** the thesis
book is reachable; at the **live 1,500s cadence** it is not, and neither is a book much above
today's, because today's already fills 99.6% of it.
