**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the settlement ceiling was priced on ONE CHILD PROCESS, not the cgroup, and the paragraph holding it at 1,200 was wrong in both directions at once

**Filed:** 2026-09-22. Drawn as Lane 0 delivery,
`the-settlement-ceiling-can-move-now-that-its-curve-has-landed`. Pre-registration:
`SEAT_PREREG_WHICH_MEMORY_LEG_BINDS_THE_SETTLEMENT_CEILING_WHEN_THE_PROBES_PEAK_AND_THE_UNITS_JOURNAL_DISAGREE_2026-09-22.md`,
filed before any of the measurements below.

## 0. The premise, re-measured before the work

The item's cited commit `c4bee75e3` is an ancestor of `origin/main`, but it is the **curve's**
landing, not this work's — an enabling precondition. `SETTLEMENT_CUSTOMER_YEAR_BUDGET` was still
`1200.0` at `origin/main`, so the premise stood. The named duplicate claim is this item's own id.
The named continuation (`widen-membership-guarded-...`) is `conditional_registration_survey`, a
different subject. **Nothing was spent; the work was done.**

## 1. What shipped

`simulation/net_new_acquisition.py::SETTLEMENT_CUSTOMER_YEAR_BUDGET`: **1200.0 → 1250.0**.

```
budget_mb = resource_headroom.sample()["total_mb"] × 0.25          = 6,008.0 MB
ceiling   = 1,200 + (budget_mb − 5,734.4) / 4.3402 MB-per-cy       = 1,263.0 customer-years
shipped   = floored to leave the control off its own boundary      = 1,250.0 customer-years
```

**MEMORY is the binding leg.** The other two are not close: wall clock against
`publish_freshness.PUBLISH_CADENCE_SECONDS` (604,800s — the interval the director named on
2026-09-04, and the note's sentence calling it unstated is deleted) supports **22,879**
customer-years on the honest convex fit; the funnel's entire demand is **3,135.5**. At 1,250.0 the
run claims **5,951.4 MB = 24.8% of the live guest**.

## 2. The finding: the two numbers were not the same quantity, and the smaller one was the basis

Both of these describe the peak RSS of a value-cycle run at the old ceiling of 1,200:

| figure | what it counts | value |
|---|---|---|
| `settlement_ceiling_slope_20260921.json` point 1 | `ru_maxrss` of the ONE child the probe spawned | 5,507.4 MB |
| `weight_drift("sim_run")`, read 2026-09-22 | systemd `MemoryPeak` — the `sim-runner.service` **cgroup**, 8 runs in 24h | 5,734.4 MB |

They differ by **227.0 MB**, and that is the `sim_runner.py` parent daemon: the probe never spawns
it, and the kernel — and `admit()` — always counts it. `premise_population.load_whole_run_rss_curve`
reads the probe's `peak_rss_mb`, so the memory ceiling the site publishes prices the child and not
the thing that has to fit the box.

**Consequence, and it is the reason the value moved at all.** The published ceiling of **1,312**
customer-years implies a cgroup peak of 6,235 MB against a 6,008 MB budget — **227 MB over the
budget it was derived to respect.** So 1,312 was never admissible, and the paragraph in the
constant's note that declined to move to it "because moving it to 1,312 would spend the last of the
memory headroom" reached a defensible action from a wrong premise. That paragraph is kept stated
and corrected in place, not replaced, because *how* it was wrong is the finding: **two errors
pointing opposite ways — a ceiling 227 MB too generous and a refusal to spend it — read exactly
like caution.**

## 3. The fit, and the three things the artefact forced

**(a) Contaminated x-axis, routed around rather than ignored.** Points 2 and 3 carry
`campaign_record_agrees: false` — another writer rewrote `book_growth_campaign.json` mid-run — so
their `customer_years_committed` is not their own. They contribute **only**
`customer_year_budget_seen` (which the probe set) and `peak_rss_mb` (which the probe measured).

**(b) Point 4 is excluded, and not for being unclean — it is clean.** At budget 3,400 it refused
**0 of 500** funnel wins, so it is funnel-bound, not budget-bound. Its RSS is the RSS of the 3,135.5
customer-years the funnel could supply, not of the 3,400 it was offered; fitting RSS against the
offer would flatten the slope in the flattering direction. **It is not a point about this constant's
ceiling.**

**(c) The guest is read, never quoted.** `sample()["total_mb"]` = 24,032.1 MB at the time of
writing. The 2026-08-12 scale-probe box budget is not used anywhere in this derivation.

**The budget-axis fit, on the three budget-bound points:**

| budget seen (cy) | peak RSS (MB) | wall (s) | refused by the budget |
|---|---|---|---|
| 1,200 | 5,507.4 | 1,499.6 | 419 |
| 2,000 | 8,504.7 | 2,666.5 | 260 |
| 2,800 | 12,501.8 | 4,591.5 | 79 |

```
RSS(x)  = 0.000781094 x² + 1.247125 x + 2,886.075      (a > 0 — convex on the budget axis too)
WALL(x) = 0.000592266 x² − 0.436625 x + 1,170.688
secants: 1,200→2,000 = 3.7466 MB/cy ; 2,000→2,800 = 4.9964 MB/cy
```

**Three admissible fits of one quantity, and I took the narrowest:**

| slope | source | ceiling |
|---|---|---|
| 4.3402 MB/cy | the landed curve's own wide secant | **1,263.0 cy** ← used |
| 3.7466 MB/cy | 1,200→2,000 secant | 1,273.0 cy |
| 3.1217 MB/cy | quadratic marginal at 1,200 | 1,287.7 cy |

## 4. Predictions, scored against what happened

1. **`weight_drift("sim_run")` returns `drifted: True` — REFUTED.** It returned
   `drifted: false, observed_peak_mb: 5734.4, samples: 8`. The declared 13,824 MB comfortably
   covers what the unit actually peaks at. **And the refutation is what made the result:** I filed
   this expecting a drifted weight and instead got an *independent instrument corroborating the
   probe's curve to within 4.1%*, which is what licensed using that curve as a basis at all.
2. **The two figures are not the same quantity — CONFIRMED,** and in the predicted direction: the
   probe's is single-process `ru_maxrss`, systemd's is cgroup-wide `MemoryPeak`.
3. **The budget-axis fit lands ABOVE 1,312 — CONFIRMED** (1,354.4 quadratic, 1,352.6 OLS), for the
   predicted reason (a wide secant on a convex curve overstates the local slope at the bottom).
   **Pre-registered as the flattering direction, and duly not taken.**
4. **The declared `sim_run` weight does not need raising — CONFIRMED.** At 1,250.0 the implied
   cgroup peak is 5,951.4 MB, which the declared 13,824 MB covers at **0.43x**. No re-declaration
   in this commit, and the arithmetic is in the note so the next reader can check rather than
   re-run.

## 5. Owed, and deliberately not fixed here

1. **`load_whole_run_rss_curve` anchors on the probe's single-child RSS.** The fix is to anchor on
   the cgroup, which would move the published 1,312 to 1,263. **Not touched: the item names
   `simulation/premise_population.py` and `tools/generate_value_arms_data.py` as a live lane's
   repair in flight at 21:22/21:24 on 2026-09-21, and a second writer there buys nothing.** Until
   it lands, `site/data/value_arms.json` publishes a ceiling 227 MB over its own budget and the
   constant disagrees with it by 4.7% in the safe direction. **The constant is the conservative
   side of that disagreement, which is the side to be on, but it is a disagreement.**
2. **The 0.25 share of the guest is a CLI default, not established knowledge.** It is
   `--rss-share`'s default in `tools/settlement_ceiling_probe.py`. The admission governor's own
   budget for the same box is `total_mb − RESERVE_FOR_UNDECLARED_MB` = 23,008.1 MB — **3.83x
   larger**. If the share were established properly the memory leg would very likely stop binding
   and the funnel's 3,135.5 would bind instead, at which point this constant stops being
   interesting. **This is the highest-value follow-on and it is a knowledge question, not a
   coding one.**
3. **The artefact's own time leg is 6.7x optimistic** — it reports 154,227.6 customer-years from a
   bare marginal, where the convex fit gives 22,878.7. It does not change any decision (both are
   ~18x above the ceiling) but `settlement_ceiling_probe.py` is using the form its sibling in
   `premise_population` was explicitly re-ruled to stop using.
4. **`CLASS_WEIGHTS_MB["sim_run"] = 13,824` is a stale high-water mark** from the 2026-08-24
   OOM-kill day — 2.41x what the unit peaks at now. Over-declared, therefore **fail-CLOSED** (the
   governor refuses jobs it could admit), therefore not urgent. Named so it is not mistaken for
   agreement.
5. **Two constants still both claim to be THE publish cadence, 112x apart** — carried by the live
   claim `one-publish-cadence-two-constants-112x-apart`, not by this item.

## 6. The control, and the mutation that proves it can fail

`tests/simulation/test_net_new_acquisition.py` (existing home — no new module):

* `test_the_settlement_ceiling_does_not_outrun_the_measured_memory_curve` — the property, as an
  inequality in **one direction only**. Neither side of the comparison is written by the constant:
  the slope comes from the probe's artefact, the guest from `/proc`.
* `test_the_ceiling_still_fits_the_peak_systemds_own_journal_reports_today` — re-prices the whole
  ceiling on whatever peak the journal reports now, so a stale anchor fails **only when it has
  drifted far enough to matter**. No tolerance is invented. An unreadable journal skips with its
  reason named and is not dressed as clean.
* `test_BOTH_verdicts_of_the_memory_ceiling_guard_are_reachable` — one control over the whole
  partition (`admits and refuses_a_smaller_box and refuses_a_bigger_book`), because a guard that
  refuses nothing passes every test of a guard.

**Mutation-proven, not asserted:**

| mutation | verdict |
|---|---|
| ceiling raised to 1,400 | **RED — fired** |
| ceiling raised to 3,400 (the funnel-bound probe point) | **RED — fired** |
| ceiling restored to the historical 1,200 (safe direction) | GREEN — correct: the control keys to the property, not to today's answer |

**Why the value is floored to 1,250.0 rather than shipped at 1,263.0, and it is not a rounding
preference.** At 1,263.0 the control has **0.8 MB of MemTotal** between green and red. MemTotal on
this WSL2 guest is a share of a Windows host and moves between restarts — which is why this repo's
rules say read it and never quote it. A control that reds because the guest came back 1 MB smaller
names a file nobody touched and stops every lane. 1,250.0 buys 13.0 customer-years = 56.6 MB of run
RSS = **226.5 MB of guest drift (0.94%)** before the control has anything to say, and it is the
honest precision on a quantity whose own three fits span 2%.

## 7. What is NOT claimed

The item's FINISHED clause includes "the next producer run completes at it without opening a
`resource_headroom` episode". **That has not been observed and is not claimed here.** The next
`sim-runner.service` cycle is what tests it; the evidence in hand is that the implied cgroup peak
(5,951.4 MB) is 217 MB above the peak the unit has been hitting across its last 8 runs and 0.43x of
its declared weight, so an episode would be a surprise. Handed on rather than assumed.
