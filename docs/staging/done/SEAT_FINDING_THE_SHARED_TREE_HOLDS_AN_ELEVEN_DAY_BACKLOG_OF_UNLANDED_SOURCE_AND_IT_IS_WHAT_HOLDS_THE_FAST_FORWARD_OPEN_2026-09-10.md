<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared tree holds an eleven-day backlog of unlanded source, and it is what holds the fast-forward open

**Found 2026-09-10 19:40 BST**, delivery seat, while answering a director question about what two
disconnected sessions left behind. It is filed rather than fixed because sweeping it is the exact
move the pathspec discipline exists to prevent, and because part of it is held on purpose.

## The measurement

The shared tree `/home/rich/synthetic-enterprise` at HEAD `21e807e7f` carries, in its **working
directory**, uncommitted:

- **~4,100 insertions across 57 tracked source files** (`git diff --stat -- '*.py'`, excluding this
  turn's own stretch-log repair);
- **11 untracked new modules with their tests** — `tools/inside_the_renewal_rule.py`,
  `tools/renewal_rule_price_response.py`, `tools/book_shape_spread.py`,
  `tools/build_weather_world.py`, `tools/pull_book_weather.py`, `tools/explain_premise_year.py`,
  `sim/weather_world.py`, `tests/tools/test_inside_the_renewal_rule.py`,
  `tests/tools/test_renewal_rule_price_response.py`,
  `tests/architecture/test_no_document_asserts_a_licence_condition_that_does_not_exist.py`,
  `tests/saas/reporting/test_a_departure_route_carries_its_denominator.py`.

**Dated by mtime, oldest first**, this is not one lane's afternoon. It is a backlog:

| written | file |
|---|---|
| 2026-08-30 | `tests/tools/test_settlement_ceiling_probe.py` |
| 2026-08-31 | `tests/saas/reporting/test_a_departure_route_carries_its_denominator.py` |
| 2026-09-03 | eight test modules + `tools/settlement_ceiling_probe.py` (+226), `tools/measure_churn_heterogeneity.py` |
| 2026-09-04 | `background/boot_sha.py` (+32) |
| 2026-09-05 | `tools/generate_maturity_map_data.py`, its test |
| 2026-09-06 | `background/disk_headroom.py` (+64), `tools/ops_repo_contract_battery.py` (+182), four test modules |
| 2026-09-07 | `simulation/weather_cell_siting.py`, `saas/reporting/annual_report.py` (+29), `tools/stock_joint_generator.py` |
| 2026-09-08 | `tools/commit_refusal_attribution.py`, `background/gap_ledger_reconciler.py`, `tools/pull_book_weather.py`, `tools/weather_cell_drivers.py`, `tools/explain_premise_year.py`, `tools/book_shape_spread.py` |
| 2026-09-09 | `tools/level_promotion_gate.py` (+315), `tools/stale_copy_refusal.py` (+111), `tools/demand_vector_coverage.py` (+74), `simulation/customer_events.py`, `simulation/market_switching_propensity.py`, `tools/couple_value_based_pricing.py`, `sim/weather_world.py`, `background/self_clearing_alarm_census.py`, `background/delivery_seat.py` |

The newest is twenty hours old. Nothing here is a live lane mid-write: the two live worktrees
(`se-seat-executor`, `se-floorrun-20260910`) are isolated by construction and write nothing in this
tree.

## Why it is BLOCKING and not LATENT

Three consequences, each independently verified this turn:

1. **It holds the fast-forward open.** `origin_reconcile.paths_blocking_fast_forward()` names seven
   paths as "modified here, and origin changes it too". `background/supervisor.py` and
   `tests/tools/test_fold_noise_floor_family.py` are two of them, and both are in the list above. A
   merge that requires a clean tree cannot run in a tree that is never clean.
2. **The gates read the whole tree, not a pathspec.** An unwired module or an unfiled finding from
   any lane blocks every commit, so this residue is priced into every commit latency figure this
   project has measured — including the "commits take more than ten minutes" note in `CLAUDE.md`.
3. **It is the class the 915 orphaned lines were named for, at four times the size**, and the class
   has recurred often enough to have salvage branches named after it.

## What this finding is NOT claiming

**Not that it should be swept.** Landing 4,100 lines across 57 files in one commit is precisely what
the pathspec rule exists to prevent, eleven of those modules need REUSE blocks nobody has written,
and at least one cluster is **held deliberately**: `e4aa02359` took the head-red pair out of the
index and left it on disk on purpose, and performing the obvious tidy-up on it would destroy what
that commit meant to keep. A remedy that cannot tell held work from abandoned work is worse than the
backlog.

**Not that any of it is wrong.** Nothing here has been read for correctness. The claim is only that
it exists, that it is up to eleven days old, and that it is load-bearing on three other symptoms.

## What would discharge it

A per-cluster adoption pass: for each file, is it (a) finished and landable by pathspec, (b) held on
purpose and needing a recorded reason, or (c) abandoned and to be reverted. That is a decision per
cluster, not a sweep, and the census above is the work list. The population floor is **57 tracked
files + 11 untracked modules at 2026-09-10 19:40 BST** — a remedy that reports fewer without saying
which it dismissed and why has not covered the subject.

## Beside it, one line each, filed here rather than as their own documents

- **A worktree lock has no door for the state after the run ends.** Six of the seven locks read
  *"LIVE RUN … do not remove until inactive"* and **nothing checks whether it went inactive**; one
  said "~2h15m run" and was seven days old. `disk_headroom.reapable()` does not scan `/var/tmp/se-*`
  at all — correctly, because the lock is what protects a running job from a reaper that once
  deleted a landing worktree nine minutes into its gate. The wall is right; there is no door.
  Five dead worktrees were unlocked and removed by hand this turn.
- **Two untracked artefacts are written by every world run and are neither tracked nor ignored** —
  `docs/observability/book_growth_campaign.json` and `docs/observability/book_subset_verdict.json`,
  written by `simulation.live_population._resolve_campaign` and `._record_subset_verdict`. They
  appeared identically in all five dead worktrees, where they read as uncommitted work in
  perpetuity. One `.gitignore` line, and it is not this stretch's subject.
