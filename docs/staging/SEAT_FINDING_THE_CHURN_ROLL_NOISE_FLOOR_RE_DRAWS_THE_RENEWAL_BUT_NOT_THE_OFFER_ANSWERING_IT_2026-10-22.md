**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `seeds-for-the-ending-term-switch-and-the-save-odds-guard` (Lane 0 delivery)
**Knowledge:** none -- a harness defect in how a seed reaches the world's renewal roll; no domain claim

# The churn-roll noise floor re-draws the renewal but not the offer answering it (2026-10-22)

## What was found

`tools/run_value_cycle_ab.noise_floor(redraw_key="churn_roll")` re-draws the renewal dice by
`setattr(simulation.customer_events, "churn_roll_for_renewal", patched)`. Three modules hold that
function under their own name, imported before the patch is made, and each keeps reading the base
roll:
- `simulation/run_phase2b.py:162` imports it by name. It reads it at the save on loss notice when
  the save scale is not 1 (`:4050`) and at the move-with-us answer (`:4531`).
- `simulation/retention_offer.py:35` imports it by name. `answer_retention_offer` (`:79`) reads it
  to decide whether a household offered a discount stays.

So under that floor, a household's renewal is rolled on the seeded dice, but a retention offer
on the same renewal is answered on the base dice. The offer and the departure it acts on then
disagree about who was leaving. `coin_drawn_decision_set` imports the function inside its
functions, so it reads the patched attribute and is not affected.

Found while building section 14's dice seeds
(`docs/staging/records/SEAT_PREREG_THE_PER_CUSTOMER_SWITCHES_ON_TOGETHER_AGAINST_FLAT_2026-10-21.md`).
`tools/per_customer_switch_arms.renewal_dice_seeded` avoids the defect by replacing every loaded
module whose `churn_roll_for_renewal` is the real function. Its control is
`tests/tools/test_grade_per_customer_switch_seeds.py::test_the_renewal_dice_reach_every_by_name_binding_and_are_restored`.
A hand list I wrote first missed `run_phase2b`. That is the same shape as this defect.

## Why it is LATENT, not BLOCKING

The floor was built under `W2_20`, which is closed; no open atom owns it, hence `unminted`.

The floor's subject is `selection_gbp` on the value arms. There it moves the pricing, not
retention offers. Whether any published floor ran with the retention guard on, the save scale away
from 1, or move-with-us answers armed has not been checked. Until it is, no published spread is
known to be wrong.

## What would close it

`_churn_roll_redraw_patch` is applied by the same every-binding search, or the floor reuses
`renewal_dice_seeded`, with the control asserting that the three bindings read one roll. Then
re-ask which published floors had any of the three consumers on.
