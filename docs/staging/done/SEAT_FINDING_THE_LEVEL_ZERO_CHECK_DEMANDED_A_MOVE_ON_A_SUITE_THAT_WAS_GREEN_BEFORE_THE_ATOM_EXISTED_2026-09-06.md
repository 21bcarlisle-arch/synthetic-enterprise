**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

**Discharged:** `tests/tools/test_level_zero_contradicted_by_its_own_controls.py::test_a_control_older_than_its_row_is_UNGRADABLE_and_never_a_contradiction` — the check now dates each row against its named controls and reports a control older than its row as UNGRADABLE, so the wrong refusal below cannot recur; `tests/tools/test_level_zero_contradicted_by_its_own_controls.py::test_the_dating_function_reads_real_git_history_in_both_orders` proves the dating itself against real git in both orders, and `tests/tools/test_level_zero_contradicted_by_its_own_controls.py::test_all_six_verdicts_are_reachable_in_one_pass` is the poison round that keeps both new branches reachable.

# The level-zero check demanded a move on a suite that was green before the atom existed

**Found:** 2026-09-06, delivery seat, while actioning the lane-0 item *"the four contradicted rows
move or the check that named them is wrong"*. The item said, in the director's own framing, that a
row turning out to be correctly at zero would be the more valuable outcome. It was.

---

## What the check said, and what was true

`tools/level_zero_contradicted_by_its_own_controls.py` reported three rows CONTRADICTED — at
`level_current: 0`, `loop_stage: build`, with every control their own `file_scope` names passing:

```
  SPINE_1_scenario_world_state    tests/sim/test_scenario_spine.py         15 passed
  H41_the_map_ratchet_...drain    tests/design/test_simplifications_store.py  41 passed
  SITE4_ia_register_and_nav       site/test_ia_register.py                 38 passed
```

For H41 the verdict was wrong, and wrong in the direction that costs: it demanded a level move for
work that has not happened.

**H41's deliverable is an ongoing drain on the map ratchet.** The atom's own title is *"The map
ratchet drains once and refills at mint rate"* and its gain is *"the spine ratchet stops being a
control that goes red every fortnight"*. That drain does not exist — measured, not argued, by
`SEAT_FINDING_THE_SPINE_RATCHET_REFILLED_IN_ELEVEN_DAYS_...`: after the one-off H32 drain took the
map from 521,770 to 393,692 bytes, it was back to 408,540 of a 409,600 ceiling eleven days later,
and a concurrent lane's landing took it over, refusing every lane's next commit.

**And the named suite was green throughout that.** `tests/design/test_simplifications_store.py`
grades the store's mechanics — roll, size bounds, orphans, duplicate tenants — and passes whether or
not a drain is ongoing. It went green through exactly the failure H41 exists to fix, because the
narrative moved into `gain`, a field no tenant holds.

## The structural cause: the check never asked whose evidence it was

The check asked *"does the named set pass"* and read the answer as *"has this atom's work landed"*.
Those are the same question only when the atom's own build wrote the set. Dating settles it, and on
the live map it separates the three cases with no tuning and no appeal to commit-message convention:

```
  atom      row minted            control born            delta
  SPINE_1   2026-07-29 14:43      2026-07-29 17:24        +2h41m   its own build wrote it
  SITE4     2026-08-18 (8a3e002d6)  2026-08-18 (8a3e002d6)  same commit
  H41       2026-08-10 (aab38e6dd)  2026-08-05 (3d2718a57)  -4d08h  already green
```

H41's control predates the row it is evidence for by four days. Its passing today carries no
information about whether H41's work landed. **A control that was green before the atom existed
cannot distinguish the atom's work landing from the atom's work never starting** — which is this
project's `controls_that_cannot_fail` class arriving through a door nobody had watched: not a
control that cannot fail, but a control that cannot fail *about the thing it is cited for*.

## The fix, and the direction it fails in

`assess` now dates every candidate row against its named controls before running anything, and a row
naming a control older than itself is UNGRADABLE **entire** — the same fail-closed reasoning that
already governed an absent path, because grading the remainder publishes a verdict about a set the
row does not describe. Dating is cheap against the thing it gates: ~0.25s per control against
pytest's seconds-to-minutes, so it runs before the run and before the pass budget.

Provenance that cannot be established (a shallow clone, a `git archive` extract, an uncommitted
control) is its own verdict and never degrades to refusing. `--follow` is used so a renamed suite
dates from its birth rather than its rename; its known cost is that rename detection works by
similarity, so a control closely resembling an older file can read as older than it is. **Both error
directions here are silence, never a false demand** — the refusing verdict is the one that asks work
of someone, so it is the one that must be earned.

## What the run left behind

- **SPINE_1** moved L0 → L2, self-certified with the run in the ledger. Not to its L3 target:
  `expert_hour.status` is `not_attempted` and L3 requires HARDEN.
- **SITE4** has its L2 evidence in hand and the move was **refused by OPS11** — lane `H_harness`
  holds 17 live BLOCKING findings. Contradicted *and* correctly frozen is a real state, and the
  check's own docstring already said so. Accepting 17 limitations to push one row through would be
  marking one's own homework at scale; the row keeps its evidence in a `level_hold_note` and waits.
- **H41** stays at zero, which is where it belongs.

## The residual, unfixed and named

The check is silent about the majority of its own partition: 28 of 34 level-0 rows name no control a
runner can execute at all (`SEAT_FINDING_TWENTY_EIGHT_OF_THIRTY_FOUR_LEVEL_ZERO_ROWS_...`). This
finding does not touch that. The fix belongs at the minting path — a new row names a control a
runner can execute, or it is not a row — not in a sweep of the 28.
