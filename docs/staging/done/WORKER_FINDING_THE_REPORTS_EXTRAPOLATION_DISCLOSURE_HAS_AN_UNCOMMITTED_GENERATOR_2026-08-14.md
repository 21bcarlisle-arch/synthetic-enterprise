# WORKER FINDING — the annual report's extrapolation disclosure has an UNCOMMITTED generator, untracked and in no tree

**Severity:** LATENT · **Lane:** H_harness
**class:** uncommitted-and-orphaned-work
**found:** 2026-08-14, running the scope brief's disqualification battery on
`EP14_adapter_published_cost_stack` (`docs/design/EP14_PUBLISHED_COST_STACK_BATTERY_2026-08-14.md` §8).
Queued, not adopted — this is another lane's work in that lane's subject area, and the draw that found
it was DISCOVER/FRAME.

## Why LATENT and not BLOCKING

The instrument is not untrustworthy — it works, and what it emits is true and useful. No published
figure is wrong: the disclosure it generates is a correct statement about the rate tables. The defect
is **reproducibility**: the artefact cannot be regenerated from the repository. CLAUDE.md's IaC clause
makes reconstruct-from-repo-alone the test, and this fails it. That is real and it is not "a published
figure may be wrong", so it grades LATENT.

**The asymmetry that argues for treating it promptly anyway**, recorded rather than used to inflate the
grade: `docs/reports/ANNUAL_REPORT.md` is **staged in the index now**. If a lane commits it by pathspec
while the generator stays uncommitted, the report lands carrying a claim no committed code produces —
and a later regeneration from HEAD would silently *drop* the disclosure, leaving a report that
understates. Neither has happened yet, so neither is claimed.

## What was observed (observed-with-evidence)

At HEAD 5975a4e26. The remedy for the silent-clamp finding
(`docs/staging/WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW_2026-08-14.md`,
filed earlier the same day) has been **built and is running**, but exists only in the working tree:

| | at HEAD | in the working tree |
|---|---|---|
| `simulation/policy_costs.table_coverage` | absent | present |
| `simulation/policy_costs.is_extrapolated` | absent | present |
| `simulation/policy_costs.extrapolation_status` | absent | present |
| `simulation/policy_costs.coverage_report` | absent | present |
| `tests/simulation/test_policy_cost_coverage.py` | absent | present, **untracked** |
| `policy_cost_coverage` in `simulation/run_phase4c_on_phase2b.py` | 0 mentions | 2 |
| `policy_cost_coverage` in `saas/reporting/annual_report.py` | 0 mentions | 3 |

`git diff --stat` on the module: **142 insertions, 0 deletions**, all uncommitted.

It has already run. `docs/reports/run_output_latest.json` carries a populated `policy_cost_coverage`
block (`any_extrapolated: true`, `table_count: 13`, `extrapolated_count: 13`, per-table `covers` and
`clamped_from`), and `docs/reports/ANNUAL_REPORT.md` carries the generated sentence at **lines 510 and
537**: *"EXTRAPOLATED RATES — 13 of 13 rate tables… the figure is a CARRIED-FORWARD stand-in, not a
published rate."* No code in any commit can produce either.

## What this is NOT — checked, not assumed

**It is not the consumer/supplier split** whose class closed today
(`docs/staging/WORKER_FINDING_A_PATHSPEC_COMMIT_LANDED_THE_CONSUMER_AND_LEFT_THE_SUPPLIER_STAGED_2026-08-14.md`).
That failure is a landed consumer reading an unlanded supplier. Here **both** are unlanded: the four
new functions and all five consumer mentions are on the same side of the tree, so the symbol resolves
in the working tree and would resolve in a commit that carried the whole set. The commit-time control
that class produced (`tools/symbol_landing_check.py`) is therefore **not** breached, and it was worth
verifying rather than filing a second instance against a control that had just been proven.

The distinct shape is: **not a broken reference, an unreproducible artefact.** The generated document
is downstream of code that exists nowhere in history.

## What discharges it

The instance discharges by landing the set as one commit — module, untracked test, and both consumer
edits together — after which `git ls-tree HEAD` shows the test and `git show HEAD:simulation/policy_costs.py`
shows the four functions. It also discharges the silent-clamp finding, which should be dispositioned in
the same move rather than left in the staging root against a repaired defect.

The class question this raises, and does **not** answer: the existing control proves a *symbol* a commit
references is in the tree. It cannot see a *generated document* whose producer is absent, because the
document references nothing — the report is prose. Whether a control should exist that regenerates a
published artefact from HEAD alone and diffs it against the committed copy is a real design question
with a real cost, and belongs to whoever draws it.

## Not claimed

That the uncommitted work is wrong, incomplete, or abandoned — it was not reviewed here, only located,
and it appears to be a competent repair. That any lane failed to land it deliberately; no cause was
investigated. That the disclosure text is inaccurate — it matches what the tables actually cover. That
`site/data/` publishes this field: **checked, and it does not** — the only `extrapolat` match in
`site/data/simplified.json` is unrelated prose in a different atom's record, so the public site is not
affected and this stays inside the report artefacts.
