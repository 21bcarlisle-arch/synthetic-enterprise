**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

# Not one of the twenty-three uncontrolled rows has a control to be repointed at

**Found:** 2026-09-06, delivery seat, working the lane-0 item
`the-level-zero-check-is-blind-to-twenty-nine-of-the-rows-it-grades`. The item's third clause was
*"give the rows that have controls a `file_scope` that names them"*, and its second was *"repoint
PB5 at the control that exists"*. Both assume a set. **The set is empty, and this is the
measurement that says so** — filed rather than quietly dropped, because a clause abandoned without
a number reads later as a clause nobody got to.

---

## What was measured

Every level-0 / `loop_stage: build` row that names no `test_*.py` a runner can execute (23 of the
30 live candidates). For each, every `test_*.py` on disk that either names the atom id or imports a
non-test module the row's own `file_scope` names — dated with the same rule
`tools/level_zero_contradicted_by_its_own_controls.py` uses (`git log --follow` for the control,
`git log -S<atom id>` over both map halves for the row).

```
  rows examined                                          23
  with a candidate control BORN AFTER the row              2
    C_supply_start_consumer_routing                        rejected -- see below
    H40_full_suite_pollution_bisect                        rejected -- see below
  with a defensible repoint                                0
```

Everything else resolved to one of three shapes, none of which is evidence about the row:

- **Older than the row.** The overwhelming majority. `W2_20_mains_gas_is_drawn_not_inferred_from_
  the_heating_system` has 82 test files importing `simulation/household.py`, and every one of them
  was passing before the row was minted. Their green says nothing about whether W2_20's work
  landed — which is exactly the leg the check already has, and the reason it has it.
- **The map-contract suites.** `tests/design/test_maturity_map_contract.py` and
  `test_maturity_map_facets.py` name every atom id by construction. Pointing a row at them would be
  grading the repository while wearing an atom's name — the same fabrication the directory
  exclusion exists to refuse.
- **A directory, not a control.** Six rows name a scope under `tests/`. Deliberately not graded.

## The two candidates, and why both are refusals

**`C_supply_start_consumer_routing` → `tests/tools/test_couple_supply_start.py`.** It names the
atom id and postdates the row, so the mechanical filter kept it. Read, it is the opposite of
evidence: the suite is the acceptance **oracle** for the routing atom, written by the atom it
depends on, and its own docstring says so — *"that routing atom therefore has a ready-made
acceptance oracle rather than needing a new one"*. `test_the_class_guard_also_catches_the_live_
companys_phantoms` asserts `live["naive_phantoms"] == n_recontracted`: it passes **because the
routing work has not been done**. Naming it in the row would have made the check read
`C_supply_start_consumer_routing` as CONTRADICTED and demand a level move for an atom whose own
control is green on the strength of it being unbuilt. **A passing control is not evidence; a
passing control the atom's build wrote is.** The filter cannot tell those apart and a reader can.

**`H40_full_suite_pollution_bisect` → `tests/tools/test_level_zero_contradicted_by_its_own_
controls.py`.** The hit is this check's own suite citing H40 in a docstring as its worked example
of a directory scope. Not a control of H40; an artefact of grepping for a name.

## PB5 has no control to be repointed at, and is right to read zero

`PB5_pounds_or_percent_resolved` names `tests/simulation/test_the_decision_scale_is_pounds_on_both_
sides.py`, which no commit ever wrote. The lane-0 instruction said to repoint it. There is nothing
to repoint it at:

```
  PB5 row minted            67a258421  2026-08-28 07:58
  the world side landed     9e52d2254  2026-08-27 19:06   -- 13h BEFORE the row
  its control               tests/simulation/test_discoverability_claims_are_enforced.py
                            7af34caa0  2026-08-27 23:06   -- and asserts nothing about pounds
```

The atom's own `gain` says the world half was already done and the deliverable is the **company**
half — *"whether the acquisition and retention decisions on the company side agree"*. No test on
disk asserts the pounds/percent scale on the company side. So PB5's named path is a **planned
name**, which is legitimate, and the row is correctly at `level_current: 0`.

This distinction is now in the check itself. `NAMED_CONTROL_ABSENT` printed one instruction —
*"repoint the row at the control that exists"* — which is right for PB4 and PB6 (a build that
landed and wrote a differently-named file) and wrong for PB5 (a build that has not run). A whole
lane-0 turn was drawn on the single-branch version. The refusal now prints both branches and says
to establish which before writing either.

## D9 was the one real repoint, and it is not the one the item asked for

`D9_worse_than_blind_chip_is_metric_blind` named `site/proof/index.html` and
`site/proof/test_coupled_gaps_panel.py`. **`site/proof/` was deleted at `03dd8c49e`** (eleven pages
folded into five tabs); the coupled-gaps panel now renders on `site/harness/index.html`, and the
panel control at `site/proof/test_coupled_gaps_panel.py` never existed under that name. Repointed
to the live door plus the surviving control.

It does **not** become gradable, and that is the correct outcome:
`tests/tools/test_generate_proof_coupled_gaps.py` was born `cfcae0bc3`, 2026-07-14 — three weeks
before D9's row at `15f44e022`, 2026-08-08. D9 moves from `NAMED_CONTROL_ABSENT` ("go and find a
file that does not exist") to `CONTROL_PREDATES_ROW` ("this control is not about you"). Same
silence, true reason.

## Why the third clause should not be forced

The tempting completion is to give each of the 23 rows *something*. Every candidate on disk is
older than its row, and pointing a row at a control that predates it is worse than leaving the
scope alone: the check's dating leg would catch it and report `CONTROL_PREDATES_ROW`, so the
result is the same silence bought with 23 false claims of evidence in the map. The rows are
uncontrolled because the work is unbuilt. That is the map being right.

`SEAT_FINDING_TWENTY_EIGHT_OF_THIRTY_FOUR_LEVEL_ZERO_ROWS_NAME_NO_CONTROL_A_RUNNER_CAN_EXECUTE_2026-09-06.md`
predicted this in its closing section and its recommendation still stands unbuilt: **require a row
to name a control file that exists at the moment its level is RECORDED as moving** — one row, once,
at the moment the evidence genuinely exists. That is the mechanism; a sweep over 23 unbuilt rows is
not.
