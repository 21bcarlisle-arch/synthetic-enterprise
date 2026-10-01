**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4` — Lane 0 delivery

# The PB4 swap lands with its value arms retaken in world D

Claim `promote-pb4-world-d-value-arms-and-land-the-swap`. This lands the swap that
`docs/design/UNLANDED_PB4_SWAP_AND_THIRD_PASS_ANCHOR_2026-10-01.md` held back, in one commit together
with the arms that bound it.

## What landed

- The fenced fourth-pass patch, taken from the locked worktree `/home/rich/wt-pb4-land` that the
  jobs ran from. It applied cleanly at origin, because none of the 38 commits since `0407ce0e3`
  touch its paths.
- Step 4's zero-read-error comment, added above `_p_churn_shock`. It is a comment only, so the
  world digest stays `cf823b185f8ca51c`.
- Both artefacts from world `cf823b185f8ca51c`, produced by `0407ce0e3` plus the patch:
  `value_cycle_ab_s1_three_arm_20261001.json` (17:14Z) and
  `value_cycle_ab_s1_noise_floor_20261001.json` (seeds 11111/22222/33333, `--redraw-mode all`,
  21:02Z). `CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH` were moved together.
- The canonical `THREE_ARM_PATH` and `NOISE_FLOOR_PATH` were NOT moved. The headline still leads
  with its 09-17/18 family and says in words that the family was measured in another world. The
  world-D reading is published beside it, which is what the constants' own comments prescribe.

## What the page says in world D

- **Whole advantage: £7,708.** It clears the £1,697 it moves across 3 re-draws.
- **Level leg: resolved positive.** The re-draws are £8,548, £9,796 and £12,098.
- **Selection leg: no verdict is stated.** All three re-draws are negative (-£4,926, -£2,564,
  -£465), so the sign is determined. But only 2 of the 3 clear the bound, so the verdict is
  withheld as one draw's.
- **The run carries the two-populations repair**, so no downward bias is claimed for it.

This is n=3. A sign stated off three draws is not a finding to quote. A wider floor in this world
(`--fold`, more seeds) is what would make the selection leg's sign publishable.

## The reds, and which ones asserted the old world's answer

The design doc predicted 25 reds in `tests/tools/test_generate_value_arms_data.py`. 24 came up.
None of them was a defect in the generator. Every one was a fixture whose subject was tied to
world `39a192ce04c1eda8` or to that world's answer.

- **16 had an incidental world.** Their witnesses (the `only` leg, the census vantage, the 09-08,
  09-10 and 09-18 runs) had to "name the live world" only so that the guard under test, and not the
  world guard, would be the one to fire. Those witnesses are now stamped onto the live digest
  (`_only_leg_live`, `_world_stamped`). The pattern already existed; `_stamped_after` does the same
  thing for clocks. The selector rungs on the 164- and 154-account runs now ask in the run's own
  world, and assert that both runs share that world.
- **8 asserted today's answer.** These are the signless selection leg, "4 of 9 draws repeat", and
  the "NOT STATEABLE" clause. In world D those branches are not on the live page. Following each
  control's own instruction ("re-point it, never delete it"), they now read the pinned pair that
  has the property: the 09-08 run with the 09-09b floor (`BOOK_SILENT_FLOOR`).

12 more reds were on the site doors:

- **3 here-relative pointer reds were a real defect.** Once world D's composition became
  readable, its sentence "The panel above states X%" rendered in two regions, and in one of them it
  was false. It now names its landmark: "The run behind this page's headline figure states…".
- **3 door rungs needed a signless leg.** They now render
  `_feed_whose_selection_leg_has_no_sign()` through the real door.
- **6 bias-size rungs had lost their subject.** Their subject is a pre-repair run's bias block,
  which is now grafted from the 09-08 run. The live, cleared state stays owned by
  `test_both_sides_of_the_partition_are_reachable`.

## Still open

- The `measure_departure_level.DEFAULT_TABLE` repoint is in the patch as written. The
  `test_switching_rate_commons` capture control was run with the neighbouring suites.
- The SVT exit-route repair was waiting on this landing, and is now unblocked.
- `/home/rich/wt-pb4-land` can be unlocked and removed now that both artefacts are on origin.
