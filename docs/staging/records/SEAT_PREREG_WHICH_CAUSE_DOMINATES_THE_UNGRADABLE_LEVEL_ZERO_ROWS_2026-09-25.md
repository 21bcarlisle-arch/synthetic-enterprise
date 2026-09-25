**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — which of the six causes dominates the still-ungradable level-zero rows, and how much of the 27 is not a defect at all?

Written BEFORE any cause was counted. Drawn on the scheduled tick of 2026-09-25 as LANE 0
DELIVERY, claim
`count-which-of-the-three-ungradable-causes-dominates-the-remaining-27-level-zero-rows`.

Predecessor, read first and not re-derived:
`docs/staging/SEAT_FINDING_THE_MAPS_SILENCE_IS_UNFALSIFIABLE_BECAUSE_THE_RECONCILER_GRADED_28_ROWS_AND_COULD_GRADE_NONE_2026-09-25.md`
— establishes the population (28 of 110 live atoms) and that `contradicted: 0` out of 0 graded
reads exactly like a clean bill of health. `7db38ae47` then moved graded 0 → 1 of 28 by silencing
`KNIFE3_wall_crossing_paydown` from the HEAD-red register instead of spending its 1078s/2.44GB
run. That removed the one cause no budget could have fixed and left 27 where they were.

## Premise, re-measured before the work

* `7db38ae47` IS an ancestor of this worktree's HEAD (`208195dd4`), so the red-at-HEAD
  short-circuit is present in the code I am measuring. The draw's premise note is correct and is
  not "spent" in the sense that would release the claim: the item asks for a census that leg did
  not perform.
* The draw's DUPLICATE-WORK note calls this id already held by another writer. It is this draw's
  own write: `claimed_at` is `1790334348.9000392` in BOTH
  `docs/observability/.seat_work_in_hand.json` and `docs/observability/.delivery_lane_claims.json`,
  identical to the microsecond and 23 seconds old when read. One write, not two writers. Carrying
  on with the work, not the disposition.
* The PATH CHECK grades all three named paths `already landed`. Correct — this item asks for a
  measurement and a repair, not a landing of existing bytes.

## The instrument, named before it is run, and why it costs no pytest run

`ungradable_causes` is a pure function of the row, the disk and `git`. It spends no run. The
expensive part of `assess` is the pytest pass, and the cause of any row that REACHES that pass is
`NOTHING_IN_THE_ROW` by construction (every named path on disk, at least one a runnable control).
So the cause split over the whole candidate partition is computable with **zero** pytest runs, and
the only thing a run would change is whether a given row lands in `ungradable` at all. I will
therefore publish the cause split over the candidate partition and say separately which rows are
pass-decided.

## Predictions

**P1 — population.** `is_candidate` returns **28** rows (the predecessor's figure), ±2 for map
movement since.

**P2 — the dominant cause is `CONTROL_NEVER_WRITTEN`,** at **≥ 9** of the partition. Reasoning:
the module's own docstring records that of 34 candidates only TEN named a test file at all. A row
naming a subject module that exists and no `test_*.py` takes this cause through the
`elif not controls` leg, and that is the ordinary shape of a level-0 row written as a plan.

**P3 — `HONESTLY_UNBUILT` is second, at 4–10,** and it is the part of the count that is not a
defect.

**P4 — the real debt is strictly smaller than 27.** Specifically `HONESTLY_UNBUILT` alone (the
module's `CAUSES_OWING_NO_REPAIR`) removes **≥ 4** rows, so repairable ≤ 23.

**P5 — the item's own claim that TWO causes owe no repair is wrong.** The item names
`HONESTLY_UNBUILT` and `NAMES_ONLY_A_SCOPE`; `CAUSES_OWING_NO_REPAIR` in the module that defines
the vocabulary holds only `HONESTLY_UNBUILT`, and `CAUSE_REPAIR[NAMES_ONLY_A_SCOPE]` is a real
instruction ("name the FILES this atom writes"). I predict the module is right and the item is
wrong, i.e. exactly ONE cause owes no repair.

**P6 — at least one row carries more than one cause** (`A51` is documented as such), and the sum
of the per-cause counts therefore EXCEEDS the row count.

**P7 — `NOTHING_IN_THE_ROW` is between 2 and 5.** The docstring measured five rows carrying no
cause on 2026-09-16 (D27, D9, KNIFE3, H41, W2_31); `KNIFE3` is now silenced and `D9`/`H41` are
documented under other shapes, so I expect this to have shrunk.

**P8 — the census does NOT reproduce in this isolated worktree.**
`docs/observability/.head_red_observed.json` is untracked machine state and is **absent here**
(verified: present in `/home/rich/synthetic-enterprise`, absent in `/var/tmp/se-seat-executor`), so
`reds_at_head` fails closed and `KNIFE3` falls back through to the run. A pass run here will
report ungradable **28**, not 27, and that difference is the environment and not a regression.

**P9 — the repair I expect to do.** Whichever class is largest, I expect the repair to be a
`file_scope` edit against a map ratchet with little headroom, so I expect to have to shrink bytes
elsewhere to pay for it, or to find that the largest class's repair is NOT a map edit at all.

## What would refute the item's framing

If `HONESTLY_UNBUILT` + `NAMES_ONLY_A_SCOPE` together are the MAJORITY of 27, the item's
suspicion is right and "the census is stuck at 27" was mostly never a defect. If
`CONTROL_NEVER_WRITTEN` + `POINTER_ROT` are the majority, the count is real debt and the item's
hopeful reading is refuted.
