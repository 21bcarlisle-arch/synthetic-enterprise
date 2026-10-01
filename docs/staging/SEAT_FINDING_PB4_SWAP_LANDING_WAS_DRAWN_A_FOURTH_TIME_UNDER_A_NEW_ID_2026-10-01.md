**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The PB4 swap landing was drawn a fourth time, under a new id

At 16:11 UTC the scheduled worker drew `run-pb4s-swap-with-the-read-error-named-on-the-hazard`. It
is the same work as `promote-pb4-world-d-value-arms-and-land-the-swap`, which is handed off and
embargoed to 22:30. The earlier draws (`SEAT_FINDING_PB4_SWAP_LANDING_WAS_DRAWN_TWICE_AND_THE_WORKER_HOLDS_IT_2026-10-01.md`)
re-used one id. This draw has a different one, so the DUPLICATE-WORK CHECK did not catch it.

**State at the draw.** Both value-arms jobs in world D are live: `launch_liveness --check` shows
`pb4-three-arm-d` and `pb4-floor-d-s123` as RUNNING. The session that launched them (pid 2082292,
the `.se_worktree_owner` of `/home/rich/wt-pb4-land`) has exited, but the systemd units carry the
jobs. Nothing can be promoted until the floor ends, about 8h after the three-arm run.

**Disposition.** This turn built and restarted nothing, and did not touch the worktree. This draw
asked for one thing the held patch lacked: the hazard surface naming the zero-read-error
assumption (gap 4). That comment is now step 4 of
`docs/design/UNLANDED_PB4_SWAP_AND_THIRD_PASS_ANCHOR_2026-10-01.md`. The promote continuation was
re-issued under its own id to carry it. The tenure-1 control in the patch is already keyed to the
property, not to 0.097. This id is released.

**The defect.** A LANE 0 item can be re-minted under a new id while its predecessor sits embargoed.
The embargo stops the old id from being drawn, but not its duplicate. This is the same remedy as
the earlier finding, from the other side: the draw should check a live `longjob-*` unit or
`.se_worktree_owner` naming the subject before it offers the item.
