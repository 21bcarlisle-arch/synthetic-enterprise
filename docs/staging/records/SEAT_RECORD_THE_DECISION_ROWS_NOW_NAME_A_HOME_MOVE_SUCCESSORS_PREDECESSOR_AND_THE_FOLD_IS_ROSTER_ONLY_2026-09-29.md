**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery (`fold-home-move-successors-into-the-decided-set-as-a-labelled-diagnostic`)

# RECORD: the per-account decision rows now name a home-move successor's predecessor, and the diagnostic fold takes roster-only successors only

**Acts on:** `SEAT_FINDING_THE_ROSTER_ONLY_1345_ON_SEED_44444_IS_C5S_HOME_MOVE_SUCCESSOR_AND_A_DECISION_NOT_A_HARNESS_LEAK_2026-09-29.md` (3e608eefc).

## What landed

- `tools/run_value_cycle_ab.py`:
  - `home_move_successor_of()` maps each successor billing account to its predecessor. It reads the registered successor book (`supply_book.successor_supply_points`), which is the book `run_phase2b.SUCCESSOR_MAP` activates from.
  - `_decisions_by_billing_account` now gives every row a `successor_of`. The value is the predecessor's billing account for a successor tenure and `None` otherwise. That row surfaces on each noise-floor row as `value_arm_decisions_by_account` and `level_arm_decisions_by_account`.
  - `fold_by_successor(diff, members, successor_of, roster_only)` is the one-line fold.
- The five-seed grader, `/var/tmp/se-ab5-out/grade5.py`, is **out of tree and not landed**. It gains one line per seed, labelled `[UNGRADED]`, printed beside P1:
  - It reads `successor_of` from the artefact when present.
  - Otherwise it falls back to `saas.customers.SUCCESSOR_CUSTOMERS`. The running legs (`longjob-ab5-runa1`/`runa2`) are pinned to a commit before this field, so their artefacts will take the fallback.
- **Unchanged:** the prereg's D, A and roster-only partition, and P1's grade. The running legs were not touched.

## The definition, decided before any re-grade

**Only a ROSTER-ONLY successor whose predecessor is in D is folded.** The first draft folded any successor of a D account. On `runB.json` it also pulled `C3_2` out of A: C3_2 exists in both arms and its own renewals were decided alike (+£1.17 on 33333, −£1.01 on 44444). A successor tenure that is present in both arms was not caused by the arms deciding differently, because the predecessor left in both. So its money stays where its own renewals put it.

**Not folded, and named:** the runtime market replacements that `saas.customers.make_acquired_customer` also stamps with `successor_of`. There the key names the property profile that a new household was cloned from. Whether a replacement belongs with the churn that freed its slot is not established.

## Reading on run B

| seed | D ex-0098, pre-registered | [UNGRADED] folded | folded in |
|---|---|---|---|
| 33333 | +£1,037.49 | +£1,037.49 | — |
| 44444 | −£559.81 | **+£785.66** | C5_2 |

This reproduces the finding's figure. Tests: `tests/tools/test_a_home_move_successor_row_names_the_predecessor_whose_churn_activated_it.py`. Mutations were run on the field (always `None`) and on the fold (lineage ignored), and both red.
