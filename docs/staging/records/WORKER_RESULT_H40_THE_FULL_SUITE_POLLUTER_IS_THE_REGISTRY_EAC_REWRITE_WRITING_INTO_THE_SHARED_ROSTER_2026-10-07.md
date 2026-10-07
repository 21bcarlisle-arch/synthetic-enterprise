**Severity:** INFO · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `H40_full_suite_pollution_bisect`
**Evidence:** `docs/staging/reference/HEAD_RED_REGISTER.md` (census of 2026-10-07 at `27d39e8a9`, 16 owed)

# H40: the full-suite polluter is the registry-EAC rewrite writing into the shared roster

**2026-10-07, autonomous worker.** Every reading below was taken in a locked, detached worktree of
`origin/main` (`5017a63c0`). Nothing was read from the shared tree.

## 1. The bisect: which reds are pollution at all

All 16 owed reds were run in isolation. **12 are red alone**: those are real reds at HEAD, not
pollution, and are not this atom's subject. Two examples are the duplicate `simplifications_count`
key on `SPINE_1_scenario_world_state` and 86 domestic premises with no stored weather cell.
**4 are green alone and red in the census.** They are the whole pollution population:

| test | alone | after the polluter |
|---|---|---|
| `tests/saas/test_customers.py::test_c1_eac_calibrated_to_ofgem_tdcv_medium` | pass | **`1604.4 == 2500`** |
| `tests/simulation/test_phase_c_household_demand.py::TestEACMultiplierComposite::test_c4_solar_reduces_multiplier` | pass | **`0.0 == 0.64 ± 0.01`** |
| `tests/simulation/test_the_registry_eac_rewrite_reaches_the_dd_opening.py` (2 nodes) | pass | see §4 |

They are the same four the 2026-10-04 turning-commit finding
(`done/WORKER_FINDING_THE_HEAD_REDS_TURNING_COMMITS_AND_WHY_THE_GATE_DID_NOT_SELECT_THEM_2026-10-04.md`,
item 2) found green on a direct run. It attributed them to the census's `LaunchRefused x4` as
"likely, not shown". **That attribution is corrected here:** for the first two the cause is an
ordered pair, reproduced below. The third is still open (§4).

## 2. The polluter, NAMED by the ordered pair that reproduces

```
pytest tests/background/test_the_triads_dd_outcomes_follow_the_supplier_stop.py \
       tests/saas/test_customers.py::test_c1_eac_calibrated_to_ofgem_tdcv_medium \
       tests/simulation/test_phase_c_household_demand.py::TestEACMultiplierComposite::test_c4_solar_reduces_multiplier
-> c1 FAILED (1604.4 == 2500), c4 FAILED (0.0 == 0.64)   [149 s, peak RSS 2.0 GB]
```

The same two targets without the predecessor: both pass.

## 3. The mechanism: module-level state, written in place by a run entry point

`simulation/run_phase2b.py` `main()`, at the block headed *A SETTLED HOME'S REGISTRY EAC IS ITS OWN
READS* (3bf64c4e7, 2026-10-01), does `_fab_customer["eac_kwh"] = round(_own_eac, 1)` and
`EFFECTIVE_EAC_KWH[_fab_cid] = ...`. It writes into the dicts of `ELEC_CUSTOMERS`, which are the
**same objects** as `saas.customers.CUSTOMERS`, and it does so on purpose: the comment says the
sign-up quote, the roster and `EFFECTIVE_EAC_KWH` must stay one object. Nothing restores them, so
every later reader in the same process gets the previous run's own-reads EAC in place of the drawn
band. C1 is a fabric premise, so its registry EAC becomes 1604.4. C4's base EAC drops below its
solar generation, and the solar multiplier clamps to 0.

The test is not at fault. The triad test calls `main(report_end="2017-02-28")` in-process with a
correct `MonkeyPatch().undo()`. The state it leaves behind is the production function's own.

## 4. What was tried and did NOT reproduce

- **Placebo, a short window.** `tests/company/billing/test_collections_journey.py` calls `main()`
  in-process too, but with `report_end="2016-05-31"`. Before the same targets it gives **32
  passed**. That fits the mechanism: under 365 days of reads the rewrite is skipped and the drawn
  band kept, which is the `continue` branch of the same block. So the polluter is the write itself,
  not "a test that runs main".
- **Collection-time `sys.modules.pop`.** Several `tests/company/interfaces/*_seam.py` modules pop
  `simulation*` from `sys.modules`, and `test_hedge_desk_seam.py:226` does it at import time. A
  full collection of `tests/` that then runs only the two registry-EAC nodes gives **2 passed**
  (38,749 deselected, 42 s, 1.1 GB). Collection does not pollute them.
- **The triad test before the registry-EAC nodes.** Both passed (same run as §2). Whatever reds
  them in the census needs a different predecessor.
- **The 12 in-process `main()` callers in `tests/simulation/` that sort before the registry test,
  as one batch: INCONCLUSIVE.** It hit its 3,500 s timeout with no verdict (58 min, peak RSS
  5.4 GB). Three of the twelve (`test_phase40a_pass_through`, `test_phase40c_deemed_rate`,
  `test_phase41a_flex`) run `main()` over the full ten-year window, which is why.
- **One `run_phase2b.main(report_end="2018-12-31")`, probed in-process** with the registry test's
  own predicate, read before and after (`/tmp/h40_probe.py`, 6 min 26 s, 2.7 GB): `not_shared`
  is 0 before and 0 after, and 261 of 261 rewritten records are read. `ACQUIRED_CUSTOMERS` goes
  from 0 to 1. So a three-year run does not break the identity the first node asserts.

**The registry-EAC pair is NOT explained by this record.** Both nodes going red together suggests
a shared precondition, such as an empty drawn book that trips both `assert drawn` and
`assert opened`. That is a suspicion, not a reproduction. The census keeps no assertion text per
red (`causes` is an exception-type count), so the bisect could not start from the census's own
failure line. That gap is filed separately:
`WORKER_FINDING_THE_HEAD_RED_CENSUS_KEEPS_NO_CRASH_LINE_SO_A_POLLUTION_BISECT_STARTS_BLIND_2026-10-07.md`.
The next step is a full-window run (`main()` with no `report_end`) through the same probe. It
costs about 25 min and 5 GB.

## 5. Memory discipline, and what it cost

Nothing was stopped. Headroom at the start was 11.8 GB available of 24.0 GB, and no full-suite run
was made: the bisect used isolated runs, ordered pairs, one batch and one probe. Peak RSS was
1.1 GB for full collection, 2.0 GB for the ordered pair, 2.7 GB for the probe and 5.4 GB for the
batch. No run went alongside another
full-suite run. One run went alongside another heavy run: the placebo arm, next to the collection
run, with more than 8 GB still free.

## 6. The class fix is drawn as its own atom

`H50_a_run_entry_point_leaves_no_state_behind` (map row, same commit). The class is **a run entry
point that writes into module-level state shared by every importer**. Its first instance is this
one. The diagnosis is not held hostage to the repair, and the repair has a production question
to answer first:

**Prediction, filed before anyone measures it:** `tools/run_value_cycle_ab.py` runs the control
arm and then the value arm through `run_phase4c(...)` in ONE process, so arm 2 starts on arm 1's
rewritten EACs. Inside `main`, the only read of `eac_kwh` before the rewrite is the W1_11
switch-verdict counterfactual (`_base_profile_eac(get_customer(...))`). The code deliberately
runs that on the drawn band, and in arm 2 it reads the own-reads figure instead. I predict the
arms' **settled volumes and margins are unaffected** and only that control's counterfactual
moves. I have not measured it. If the arms do move, the A/B has carried a non-policy difference
since 2026-10-01.
