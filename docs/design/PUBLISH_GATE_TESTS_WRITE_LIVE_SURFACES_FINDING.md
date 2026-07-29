# FINDING — publish-gate tests that call a production generator against LIVE mutable paths

**Status:** QUEUED (SELF_INTERRUPT_DISCIPLINE — registered, not fixed on sight). The instance
that actually wedged publishing IS fixed; the CLASS below is not, and is what R10 requires.
**Found:** 2026-07-29, unwedging a ~5h publish-gate outage (PRIORITY ZERO self-refill tick).
**Component:** `tests/**` calls into `tools/generate_*.py::generate()`.
**Class label (R9):** observed-with-evidence for the instance and for the sibling enumeration;
`inferred` for the claim that the siblings are *latent* rather than currently-firing.

## The instance (fixed)

`tests/tools/test_generate_dashboard_mgmt.py::test_mgmt_accounts_in_dashboard_json` called the
production `tools.generate_dashboard_data.generate()` with the LIVE
`docs/reports/run_output_latest.json`, wrote the LIVE `site/data/dashboard.json`, and asserted
`generate()`'s return value — which is the *cross-surface consistency gate* result, comparing the
loaded run against `docs/observability/run_insights.json`.

The publish pipeline writes `run_insights.json` from the **queued marker's** run json, while
`run_output_latest.json` is written by the **sim runner** as each run finishes. A sim run
completes every ~462s; one processing cycle takes ~600s (the 391s gate included). So the marker
queue is *structurally* behind and the two files name two different runs:

```
CONSISTENCY GATE FAILED (source=run_output_latest.json): 4 surface(s) disagree --
  net margin:      dashboard=1501000.74 vs insights=1521069.65
  gross margin:    dashboard=6404992.49 vs insights=6429174.28
  enterprise value:dashboard=7359201.5  vs insights=7803339.73
  bills total:     dashboard=1557       vs insights=1588
```

Verified as staleness, not a figure regression: insights matched
`run_output_6b03593b3_20260729T192543Z.json` (the marker) exactly; `run_output_latest.json`
matched `run_output_e2f892e4c_20260729T220622Z.json` (a run that finished 2h41m later).

**Self-sustaining**: gate RED → no commit → queue grows → marker gets staler → gate RED. It could
not recover on its own. Fixed by making the test hermetic (tmp `OUTPUT_PATH`) and dropping the
consistency assert, which was never this test's claim and keeps dedicated coverage elsewhere.

## The class (NOT fixed — this is the R10 debt)

The instance fix is an instance fix. The class is: **a test inside the publish-gate scope that
invokes a production generator against live mutable inputs and/or writes a live publish
surface.** Two distinct harms, only the first of which bit us:

1. **Reds on legitimate progress** (this outage) — when the generator carries an internal gate
   whose precondition the test's own call violates.
2. **Clobbers a published surface mid-pipeline** — the test rewrites the artefact the pipeline
   just published, from a source the pipeline did not publish. Here the RED aborted before
   commit, so nothing wrong was published; had the gate passed, `dashboard.json` would have gone
   live describing a different run than `LATEST.md` and `ANNUAL_REPORT.md`. That is an R14/R11
   hazard sitting one coincidence away.

This is the same shape as the already-named pattern *"live-snapshot gate reds INTERMEDIATE state
on legit progress"* — third occurrence of the family, which is why it wants a mechanism.

### Sibling enumeration (2026-07-29, each call site read — not grep-inferred)

**Hermetic (safe)** — patch the generator's output path before calling it:
`test_website_integrity_fix.py` (patches `OUTPUT_PATH` *and* `RUN_INSIGHTS_PATH` — the model to
copy), `test_query_interface.py`, `test_generate_phases_json.py` (all 3 call sites),
`test_case_study_recommender.py`, `test_generate_premise_demand_data.py`,
`test_generate_customer_data.py`, `test_generate_customers_supplier_pt.py`,
`test_generate_simplified_data.py::test_never_authors_new_text_only_republishes`.
`test_site_structure.py` only asserts `callable(generate)` — never invokes it.

**Writes a live publish surface, latent (does NOT currently red)** — calls `generate()` with no
output-path patch, so the real artefact is rewritten during the gate:

| Test | Live surface written |
|---|---|
| `test_generate_maturity_map_data.py` — `test_generate_produces_valid_json` + ~6 further tests, and 2 unpatched `gen_module.generate()` calls | `site/data/maturity_map.json` |
| `test_generate_simplified_data.py` — `test_generate_produces_valid_json`, `test_only_atoms_with_real_simplifications_are_included`, `test_totals_are_internally_consistent`, `test_atoms_sorted_by_id_within_lane` | `site/data/simplified.json` |
| `test_generate_proof_control_killlist.py::test_generate_writes_control_killlist_to_proof_json` | `site/data/proof.json` |

These survive only because their generators carry no cross-surface gate whose comparison input can
drift, and because their inputs (the maturity map yaml, the control registry) are not rewritten
mid-gate by a concurrent producer the way `run_output_latest.json` is. Both properties are
accidents of current design, not guarantees: adding a consistency gate to any of those three
generators reproduces this outage without touching the test.

### Proposed closure (an invariant, not N patches)

A static harness check over `tests/**`: a module that calls a `tools.generate_*`-module
`generate()` must either patch that module's output path (`OUTPUT_PATH`/`OUT_PATH`) or appear on
an explicit allowlist carrying a written reason. R15-provable both ways by mutation (drop a patch
→ the check must fire), which the instance fix already demonstrates in miniature
(`test_mgmt_accounts_test_does_not_write_the_live_dashboard`).

Deliberately NOT built on this tick: it flags 3 existing modules (~11 test functions), each
needing its own hermetic-isolation decision — real work, and the tick's mandate was PRIORITY ZERO
unwedging. Building it while the queue was 24 markers deep would have been the treadmill, not the
fix.

## Second, separate finding: the wedge alarm under-reported its own age

`docs/observability/.publish_gate_state.json` recorded `wedge_since` = 21:14 UTC and "7 failures
in-window", and the supervisor doorbell therefore said "FAILING for ~65 min". The worker log shows
the first failure of this wedge at **17:26 UTC** on `run_complete_20260729T162844Z.md` — the true
duration was ~5h, roughly 5x the reported figure. A rolling in-window counter that discards older
failures makes a long wedge look young, which is precisely backwards for an alarm whose job is to
convey severity. Worth a look when the class above is built.
