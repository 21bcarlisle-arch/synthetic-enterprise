**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# One of the eight became gradable, not two — and my point prediction was right about the number of repairable rows and wrong about which row carried it

Answers `docs/staging/records/SEAT_PREREG_HOW_MANY_OF_THE_EIGHT_NAMES_ONLY_A_SCOPE_ROWS_A_REPOINT_CAN_ACTUALLY_MAKE_GRADABLE_2026-09-25.md`,
written before the repoint was applied and before any row was graded. The predictions are scored
below beside the numbers, as they were filed.

## What was done

Four rows repointed at the controls of modules their own `file_scope` already named — one mechanical
rule, no new tests, no judgement about atom semantics:

| row | controls named | verdict after |
|---|---|---|
| `OPS6_scoped_publish_path_suite` | `test_publish_scope.py`, `test_process_run_complete.py` (+ subject `background/publish_scope.py`) | **GRADED**, consistent |
| `W2_non_dd_miss_vocabulary` | `test_live_payment_triad.py`, `test_sme_credit_risk.py`, `test_payment_seam_adapter.py` | `CONTROL_PREDATES_ROW` |
| `W2_18_the_housing_joint_the_sample_and_the_ceiling` | `test_population_draw.py`, `test_household.py` | `CONTROL_PREDATES_ROW` |
| `W2_19_who_lives_where_money_and_composition` | `test_household_segments.py`, `test_population_draw.py` | `CONTROL_PREDATES_ROW` |

All four delisted from `LEGACY_UNGRADABLE_BUILD_ROWS` (24 → 18), which
`test_ungradable_build_rows_allowlist_has_no_FIXED_entries` requires and which is the half of this
repair that is easy to forget: a repointed row left on the list reds every lane's next commit.

Four rows NOT repointed — `G4`, `SP2_2`, `H40`, `H48` — with the reason in
`docs/staging/SEAT_FINDING_THE_PRESCRIBED_REPOINT_WOULD_SILENCE_FOUR_ROWS_BY_TELLING_THEM_NO_NAMED_FILE_EXISTS_WHILE_ONE_DOES_2026-09-25.md`.

Census effect, one process, before and after: `NAMES_ONLY_A_SCOPE` 8 → 4; rows naming a runnable
control 8 → 12; map +423 bytes (headroom 5844 → 5421, ceiling untouched).

## The predictions, scored

1. **"Fewer than 8 become gradable; my point prediction is 2."** Fewer than 8: right. The number:
   **wrong — it is 1, not 2.** I named `OPS6` and `W2_non_dd_miss_vocabulary`; `OPS6` is right and
   `W2_non_dd_miss_vocabulary` is not. All three of its controls predate its row: born 2026-07-18,
   2026-07-13 and 2026-07-18, row minted 2026-08-03. **The error is that I reasoned about whether a
   control EXISTS and filed a prediction about whether a row becomes GRADABLE, and the dating leg
   sits between the two.** I had read `controls_older_than_the_row` before writing the prediction
   and still wrote the wrong one, which makes this a reasoning slip and not missing information.
2. **`W2_18`/`W2_19` do not become gradable by a repoint.** Right, and for the stated reason. The
   pre-registration's counter-evidence held: `site/knowledge/` holds 7 controls — wholesale prices,
   review dates, the index, consolidated-page rendering, four charts, weather-cell maps — and not one
   is about housing stock, a space-filling sample, a technical ceiling, household composition or
   small-area income. **So the item's instruction to point these two at `site/knowledge/` was not
   followed.** They are pointed at `tests/simulation/`, where the controls of the modules they name
   actually live. That change of target does not change the outcome: both return
   `CONTROL_PREDATES_ROW`.
3. **A controls-only repoint of the four `if not files` rows makes the verdict worse, not better.**
   Right, and **worse than predicted**. I expected `HONESTLY_UNBUILT` from naming a control that
   does not exist. Naming a control that DOES exist produces it too, with the sentence *"no named
   file exists, so the row is RIGHT to read zero"* over a file on disk. Tested rather than left
   standing on a mechanism reading, because testing it cost one synthetic dict and three seconds.
4. **At least one row returns `CONTROL_PREDATES_ROW`.** Right — three of the four repointed rows do.
5. **`graded` ends at 1 or 2 of 28, not 9.** Not answered here and I am not going to imply it was.
   What was measured is the eight rows' own contribution: +1, from `OPS6`. The whole-28 pass was
   started and killed at my own 120s bound before it reported; the other 20 rows were not
   re-measured this turn, and one of them (`KNIFE3_wall_crossing_paydown`) is silenced by a red at
   HEAD in any case. **The item's stated goal — "move graded off 1" — is met by exactly one row, and
   its premise that this class could move it without writing tests is half true: half the class had
   no control to name.**

## Why `OPS6` is graded and NOT contradicted, stated because the null reading is the trap

`graded: 1, contradicted: []` is easy to read as "nothing found". It means the row's controls ran and
did not all pass, so the map's zero and the controls agree. One test is red:
`test_a_root_unavailable_scope_stops_the_gate_instead_of_running_it`, 131 passed / 1 failed / 107s.
That red is a fail-OPEN in the publish gate's own scoping wiring, so `OPS6` sitting at level 0 is
correct and the census can now *demonstrate* it rather than being silent about it. Checked in both
trees: the verdict is the same from this worktree (where the HEAD-red store is absent and
`reds_at_head` falls through to the run) and against the shared tree's store (which reports no reds
in the set, wrongly — see the finding). The conclusion does not rest on the worktree.
