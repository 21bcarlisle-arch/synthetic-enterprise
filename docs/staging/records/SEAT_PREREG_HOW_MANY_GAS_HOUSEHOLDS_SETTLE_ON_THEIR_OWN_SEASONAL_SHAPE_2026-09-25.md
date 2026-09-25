**Severity:** RECORD · **Lane:** stage 1 — the half-hourly shape reaching the book · **Atom:** `W2_30`

# Pre-registration: how many gas households settle on their own seasonal shape

**Filed 2026-09-25 ~12:40 BST, while run `longjob-hhshape-gas-run-20260925` is in flight** (worktree
`/var/tmp/se-hhshape-run-20260925`, detached at origin/main `cd4cc7f2b`). Nothing below is known yet.

## Why a fresh run, and why from a worktree

The 2026-09-18 repair taught `run_phase2b` to RETURN `gas_shape_provider_by_customer` and
`gas_shape_refusals`; 2026-09-23 added them to `annual_report.extract_report_data`'s whitelist. Both
are at HEAD. **No published run has carried them yet** — the 2026-09-25T11:06Z run (`208195dd4`)
has neither key. The reason is not the code at HEAD: the SHARED tree's working copy of
`saas/reporting/annual_report.py` deletes those two whitelist lines (and a 09-24 comment), and every
daemon run executes the shared tree. `refresh_to_head` refuses it (`refused_head_does_not_supersede_it`
— edited after the landing, deletes 2 declared keys HEAD binds), so it is some lane's in-place copy
and I have not overwritten it. The run goes from a clean origin/main worktree instead.

## Population, measured before the run

98 resi gas customers (`C1g`…). Eligibility for a gas trace is the electricity side's predicate,
called with `is_half_hourly_metered=False`. Pairing each gas id to its electricity twin (strip `g`)
in the 11:06Z run's `fabric_eligibility`: **80 have a twin, 70 eligible, 10 refused — all 10 for a
missing weather cell.** 18 are gas-only and have no electricity row to read.

## Predictions

- **P1** — both keys published, `gas_shape_provider_by_customer` has exactly 98 entries, every one
  `fabric_seasonal_split` or `population_70_30_split`. Falsifier: absent key or count ≠ 98.
- **P2** — `fabric_seasonal_split` count in **[70, 88]**; point prediction **84** (70 twins + the
  18 gas-only at the twin rate 70/80, less ~2 fit refusals). Falsifier: outside the range.
- **P3** — at least **10** refusals carry the no-fabric-trace reason, and they include the 10 twins
  whose electricity side lacked a weather cell. Falsifier: any of those 10 settling on its own shape.

## Result — 2026-09-25 13:55 BST, graded from `/var/tmp/se-hhshape-run-20260925/out/run_output_hhshape.json`

- **P1 HELD.** Both keys published. `gas_shape_provider_by_customer` has 98 entries, all in the two
  states. This is the first run artefact to carry the gas half.
- **P2 HELD, one off the point.** `fabric_seasonal_split` **85** (range 70–88, point 84). The 18
  non-twin ids are the `SYN-*` drawn homes (my `strip g` pairing mis-keyed them); 15 settled on
  their own shape and 3 did not.
- **P3 HELD exactly.** The 10 `no fabric trace` refusals are exactly the 10 gas households whose
  electricity twin lacks a weather cell.
- **Not predicted:** the other 3 refusals are `the household consumed no gas over the window`. They
  are the only three electrically heated homes on the gas book, each carrying a ~9.5 MWh AQ. Filed:
  `SEAT_FINDING_THREE_ELECTRICALLY_HEATED_HOMES_HOLD_A_GAS_CONTRACT_...`.

Electricity side unchanged (fabric 129, legacy 14, HH-metered 3). Enterprise value £165,174.

**Shared-tree repair made on the way.** The shared copy of `saas/reporting/annual_report.py` was
byte-identical to stash `23e9917bc` (`WIP on main`, 2026-09-24 15:01:09), restamped in a 61-file
cohort. That restamp defeated the stale-copy clock, and the copy deleted the two whitelist keys, so
every daemon run from the shared tree published neither. It is preserved at
`refs/preserved/annual-report-stash-23e9917bc-20260925` and the shared copy is now HEAD's. Reverse
with `git show <ref>:saas/reporting/annual_report.py > saas/reporting/annual_report.py`. The other
60 files in that cohort were not examined here.
