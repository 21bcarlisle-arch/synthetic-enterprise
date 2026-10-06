**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `the-two-reds-at-clean-origin`

# The two reds at clean origin: a stale pairing rule, and a peak from another program

## Premise, re-measured at draw

The draw's duplicate-work note named this item's own id. The only holder was this invocation's
parent `seat_executor`, and no rival `surgical_land` was running. HEAD equalled origin/main
(`da6d70053`). Both tests were red in that worktree, so the premise was live.

## Red 1 — `test_the_baseline_is_present_exactly_when_the_shock_is`

**Cause: the control was older than the definition.** It asserted baseline-present-iff-shock-present.
`da0431897` made a shock an increase only. Since then a bill that FELL publishes
`bill_shock_baseline_gbp` and the signed `bill_movement_pct`, with `bill_shock_pct` None by design
(`saas.bill_generator.bill_movement`). On the published book (8,742 bills) the partition is:

| shock | baseline | movement | bills |
|---|---|---|---|
| present | present | ≥ 0 | 4,522 |
| None | present | < 0 | 4,015 |
| None | None | None | 205 |

All 4,015 "baseline with no ratio" bills fell. The data is right and the control was wrong.

**Repair (test only, no producer change):** the baseline is now paired with the ratio it actually
divides, `bill_movement_pct`. A baseline without a shock is legal only when movement < 0. One
control asserts that both branches (rose and fell) are reachable. Driven mutations all red: a rising
bill that loses its shock, a movement dropped while the baseline stays, and a book where no shock is
ever published.

## Red 2 — `test_the_ceiling_still_fits_the_peak_systemds_own_journal_reports_today`

**Cause: a production peak from code the curve was not measured on, priced as that curve's
anchor.** The leg took `weight_drift("sim_run")`: the max `sim-runner` cgroup peak in a rolling 24h.
It used that max as the y of the curve's anchor. That max was 8,294.4 MB ("8.1G"), from the unit
lifetime that closed at 2026-10-05 18:39 and ran `4e4637853`. Since `da6d70053` the loader picks the
2026-10-06 curve, measured at `06b7c821a`, after `b8808f4ad` made the treasury register 1.5 GB
lighter. Its anchor is 4,263.6 MB at 1,199.7 customer-years.

Pricing the old program's peak on the new program's curve gives 407 customer-years against 1,050,
which is red on every lane. **Every** run in the window predates the curve, including the runner's
current `aa38800a1`. The red was keyed to the clock as well: it would have cleared by itself when
that lifetime aged out of the window at about 18:39 today. It was not keyed to the 9.5 GB
settlement_ceiling_probe. That probe runs outside `sim-runner.service`, and no probe peak is in
the unit's journal.

**Repair:** a production peak counts as evidence about the curve only if every run its unit
lifetime held carried the curve's `git_head`. Later code is included, because later code growing
heavier is exactly the stale anchor this leg exists for. A lifetime that mixed old and new runs is
excluded, because a cgroup peak belongs to every run that lifetime held. With no eligible peak, the
leg skips with a reason, `UNAVAILABLE, not clean`, and names the runs it saw. One control drives
both branches of the filter on a synthetic journal.

`weight_drift` itself is untouched. The governor's question ("how big is this job, whatever code")
still reads every peak, and it currently says `sim_run` is under-declared: 7,066 MB declared
against the 8,294 MB observed. That is the governor's business and a separate matter.

## What is still open, said plainly

- The leg is **skipping now**, and it stays that way until `sim-runner` runs code that carries
  `06b7c821a`. The current runner is on `aa38800a1`. This is the order `da6d70053` already set
  out: (1) the runner reaches the fixed code, (2) live cycles report their peak, (3) the budget is
  re-priced. When step 2 happens, this leg arms by itself. If the runner never advances, the skip
  turns into a home. The skip reason names the runs it saw, so that state can be read on any test
  run.
- On pre-fix code, the production run held 8.1 GB against a 6,008 MB share (0.25 × 24,032 MB).
  That is a fact about the program the 1,050 budget actually ran under, and it is recorded here
  rather than discarded.
