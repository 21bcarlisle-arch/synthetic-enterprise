# The run output now stamps how long its world ran for, resolved by the simulation's own predicate

*Seat result, 2026-09-15, LANE 0 delivery. Claim
`the-end-year-flag-truncates-the-simulation-window-and-is-not-stamped-so-two-arms-of-different-lengths-compare-as-equals`.*

---

## The gap, in the producer's own words

`_execution_mode()` in tools/run_annual_report.py named it in its docstring and left it open:

> WHAT THIS DOES NOT COVER, said here so it is not read as covering it: `--end-year` truncates the
> simulation window and is equally fatal to comparability, and it is not stamped. It does not reach
> this function, and threading it is a separate change; the window is currently only inferable from
> the length of `years`.

Comparability had two stamped legs — same world (`world_identity.digest` plus the home digest) and
same machine (`execution_mode.risk_committee`). The window is a third and equally fatal one: every
headline figure in the artefact is an **accumulation over the window**, so a run stopped at 2020 and
a run stopped at 2025 disagree on treasury, net margin and bad debt for a reason that has nothing to
do with the company, and stamped identically.

## What landed

`execution_mode.window`, threaded from the caller's own local rather than re-read:

* simulation/run_phase2b.py — `effective_report_end(report_end)`, the `or REPORT_END` that `_main`
  already used, extracted so it now has two readers instead of two copies.
* tools/run_annual_report.py — `_simulation_window()` publishes `report_end`, `full_window_end`,
  `truncated`, `years_covered` and `unavailable_because`. `main()` passes **the same local** it
  passed to `run_phase4c_on_phase2b`, so the stamp cannot name a window the run did not use.

Two decisions that were forced rather than chosen:

**The full-window boundary is asked for as `effective_report_end(None)`**, never by importing
`REPORT_END`. `from ... import REPORT_END` binds a copy at import time that goes on agreeing after
the constant moves — the same shape as reading `--fast` instead of `fast_mode_enabled()`, which is
exactly what stamped the wrong committee for the launch shape the arms use.

**The unstated case is fail-closed with its own sentinel.** `None` is a LIVE value on this parameter
and means UNTRUNCATED, so defaulting to it would publish "full 2016-2025 window" about a run nobody
asked. `save_run_output_json()` is handed a finished `run_output` and cannot know; it now publishes
nulls with a named reason.

**The window is NOT declared as run identity**, and this is the refusal the drawn item asked for in
its other half. `2020-12-31` is a date inside the simulated world; declared, it goes through the
census's `_RUN_IDENTITY` regex and a sentence about "the 2020-12-31 run" of this promote target
grades as SUPPORTED against a truncation boundary. That is the defect `_artefact_dates` was narrowed
to the declaration list to close on 2026-09-09, and `run_value_cycle_ab._RUN_IDENTITY_FIELDS`
already excludes `report_end` by name for it.

## The controls, and the mutation each one died to

Four legs added to
tests/tools/test_the_published_run_output_names_its_world_and_adds_up.py. Every one was run with its
defect installed and went red:

| leg | mutation | verdict |
|---|---|---|
| two runs of different lengths do not stamp the same window | pin the stamped boundary to the full window | RED |
| the stamp and the simulation resolve one window | hold a second copy of `REPORT_END` in the stamp | RED |
| a caller that did not state its window says so | default the unstated window to `None` | RED |
| the truncation boundary is not gradable as run identity | declare it in `run_identity_fields` | RED |

The first is **one control over the whole partition**, not a leg per mode, for the same reason the
committee leg is: almost every run on this box is untruncated, so a block hard-coded to the full
boundary satisfies any untruncated-only assertion and would have looked right indefinitely.

The second **moves the constant and asserts the stamp follows** — with the full window redefined to
end in 2020, `--end-year 2020` is no longer a truncation and the artefact must stop saying it is.

15 passed in the file.

## What this does NOT cover

The four first-hand blind-envelope arms **predate the stamp** and carry no `window` block. Measured
directly on their cached run outputs today, all four cover 2016–2025, ten years each — so the third
comparability leg holds for them on the delivered span, and the boundary they were *asked* for stays
unstamped for those four artefacts and cannot be recovered. Runs from here on carry it. Writing that
measurement into the arms record, so a future envelope check has evidence to read rather than a
missing field to fail closed on, is the follow-on and is not in this commit.

## Pre-existing reds, not caused by this change and not cleared by it

* `test_no_artefact_on_disk_disagrees_with_its_own_filename` — an **untracked** run artefact from
  2026-09-04 in docs/reports/ names one commit in its filename and another in its stamp. Working
  tree only; not in the tree this commit creates.
* `test_ruff_no_stale_baseline_entries` — I001 is 1308 against a frozen 1309. Traced to a sibling
  lane's uncommitted edit to tests/tools/test_generate_maturity_map_data.py, measured HEAD=1 NOW=0
  on that file. Neither file this commit touches carries an I001 violation at HEAD or now.
* Five F401s and one E741 in run_phase2b.py, all pre-existing and none in the added lines.
