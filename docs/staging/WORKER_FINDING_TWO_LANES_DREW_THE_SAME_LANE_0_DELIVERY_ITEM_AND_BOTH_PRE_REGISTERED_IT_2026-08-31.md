**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none

# Two lanes drew the same Lane 0 delivery item, and both wrote a pre-registration for it

## What happened

At 2026-08-31 ~22:00 two Claude sessions were live on this machine holding the **same** Lane 0
delivery directive verbatim — *"Make the household's drawn `eac_kwh` set the LEVEL of its
consumption"*:

- **PID 272791**, running in the isolated worktree `/var/tmp/se-seat-executor`, which landed
  `docs/staging/PREREG_THE_DRAWN_EAC_SETS_THE_LEVEL_2026-08-31.md` at `eb76aec7d` (worktree-local,
  not on main at the time of writing) together with a baseline measurement arm
  `tools/eac_level_arm.py` and a control
  `tests/architecture/test_the_drawn_consumption_reaches_the_meter.py`.
- **PID 280063**, a scheduled bounded tick on the **shared tree**, which landed
  `docs/staging/WORKER_PREREGISTRATION_WHAT_SCALING_EACH_HOUSEHOLDS_PROFILE_TO_ITS_OWN_EAC_MUST_SHOW_2026-08-31.md`
  at `d978f949d` on main and then the implementation.

Neither could see the other. The second discovered it only by running `pgrep` before
mutation-proving — a check made for an unrelated reason (`mutation_proving_in_the_shared_tree_
manufactures_another_lanes_red`) — and found the other session's process line quoting the identical
directive text.

## Why the existing guard did not catch it

`background/delivery_lane.py` exists precisely to stop this: it claims a Lane 0 id so two ticks do
not take the same item. It did not, and the reason is visible in its own store —
`docs/observability/.delivery_lane_claims.json` was **empty** when the second session ran
`--landed scale-each-household-s-profile-to-its-own-eac`, which answered:

> `bound NOTHING to scale-each-household-s-profile-to-its-own-eac: it is NOT CLAIMED`

`CLAIM_STALE_SECONDS` is 100 minutes. The first session had held the claim, the claim was swept for
landing nothing inside its deadline while it was still working, and **the sweep returned the item to
the pool without the sweep being visible to the holder**. The second draw was then entirely legal.

So the defect is not that the claim expired. It is that **a swept claim tells the pool and does not
tell the claimant**, so the original worker carries on believing it holds the item, and the
duplicate is invisible from both sides until the two commits collide.

## Why this costs more than the duplicated compute

The two implementations disagreed on scope in a way that would have double-counted if both landed:

- one scoped the levelling to PC1 (domestic) only; the other to every legacy-path customer including
  PC3 SME;
- both wrote the normalisation into `run_phase2b`'s base-shape path.

**A second normalisation on the same path is silent.** The base integral becomes `EAC²/GAD` — 1,589
kWh for a 2,500 kWh household — and every ratio-shaped assertion still passes, because both arms are
scaled twice. `tests/simulation/test_the_drawn_eac_sets_the_settled_level.py::
test_the_level_is_applied_exactly_once_on_the_path_the_book_settles_on` was added for exactly this
reason and measures the LEVEL rather than a ratio, so it goes red on a duplicate. That control is
the instance fix; the class fix is below.

## The one genuinely good outcome, recorded because it is unusual

The two lanes filed **independent** pre-registrations before either result existed, and both
predicted the post-change median in **2,900–3,400** from the same reasoning. The measurement came in
at **2,669.5**. That is a reproducible reasoning error rather than one session's slip — two
independent derivations of the same wrong number, which is worth more than either prediction was.
The error is written up in the result section of the second pre-registration: dividing a median
settled figure by a median drawn figure when the pre-change settled distribution was nearly
constant, so its median was picking out the modal EPC multiplier and not a household.

## What would fix the class, and what is NOT proposed

**Not proposed:** a new register, a longer deadline, or a ceremony on the draw. A file made of rules
breeds rules, and lengthening `CLAIM_STALE_SECONDS` just moves the collision.

**The one-leg fix:** the sweep already knows it is taking an item away from a live holder. Make it
say so where the holder will see it — the claim record keeps the sweep, and `--landed` on a swept
id answers *"this was swept at T and re-drawn"* instead of *"it is NOT CLAIMED"*, which is what the
second session was told and which reads exactly like "you are working unclaimed", not like "someone
else is working this right now".

Recorded as LATENT rather than BLOCKING: nothing is wrong in the tree, the duplicate was caught
before both landed, and the collision control is in place.
