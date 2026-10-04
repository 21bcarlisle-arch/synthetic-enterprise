**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-current-world-floor-names-the-code-it-ran` (Lane 0 delivery)

# The current-world floor now asks which code drew it

## Premise, re-measured at draw time

The premise still held. `cbe8d18a4` checks the current-world arms against HEAD. It never checks
`CURRENT_WORLD_NOISE_FLOOR_PATH`, the floor whose spread decides `resolved` on all three legs. This
was the open half named in
`SEAT_FINDING_THE_CURRENT_WORLD_ARMS_NOW_ASK_WHICH_CODE_RAN_AND_THE_10_01_RUN_IS_NOT_HEADS_2026-10-02.md`.

The draw's duplicate-work note pointed at this same id in `.seat_work_in_hand.json`. That entry was
the draw's own. It was not a rival claim.

## What changed (`tools/generate_value_arms_data.py`)

- `_floor_code_since_its_runs(floor, head)` runs `_code_since_the_run` on every commit that drew
  the floor. It reads those commits from `_which_code_a_family_was_measured_on`, which covers both
  the single `producing_commit` and folded members.
  - Any commit with an unexempted path refuses the floor, so in a folded family one older member is
    enough.
  - A floor with no commit at all also refuses.
  - The exemption file and its three-key match are the same ones the arms use.
- `_current_world_bound_admitted_on_its_code` publishes `floor_code_since_its_runs` and
  `is_the_bound_heads_code`.
  - On refusal, it sets `resolved` to `None` on the top-level bound, `selection_leg` and
    `level_leg`, and appends a reason that names the paths.
  - The bound, the family and the figures all stay. This is the cut
    `_withdraw_a_verdict_stated_from_a_superseded_run` makes.
  - Legs with no bound are left alone, because this floor decided nothing for them.
- `build` calls it right after the arms guard.

## Measured, real artefacts

| publishing HEAD | arms guard | floor guard | resolved (value / selection / level) |
|---|---|---|---|
| `0407ce0e3` (the floor's own) | admits | admits | True / None (stability) / True |
| `592596b44` | refuses | refuses (15 paths) | None / None / None |

## Controls (tests/tools/test_generate_value_arms_data.py)

1. `test_the_10_01_floor_decides_no_verdict_on_a_page_published_from_later_code` runs through
   `build` at `592596b44`. It checks that the floor is refused and that every leg keeps its bound but
   loses its verdict, with the reason given.
2. `test_the_floor_code_guard_reaches_both_branches_on_one_floor` reaches both branches on the same
   artefacts. It also checks that at least one leg resolves on the admitting branch, which is what
   makes the withdrawal distinguishable. It covers three more shapes: a fold whose older member
   refuses it, a fold of HEAD's code alone that admits, and a floor with no commit that refuses.

Mutations, every one of which reds at least one control:

- removing the call in `build`
- forcing `refused` to False
- leaving `resolved` in place
- asking only the newest folded member
- withdrawing whether or not the floor is refused

## Not done

- The feed is not regenerated here. The publisher's next build carries it.
- Until a retake of both the arms and the floor lands at HEAD, the current-world block keeps its
  figures and states no direction. The arms guard already withholds the headline, so the headline
  does not change.
