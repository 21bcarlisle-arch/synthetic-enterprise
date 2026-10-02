**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none · **Claim:** `the-1002c-floor-runs-once-depth-vs-width-has-left-the-box` (Lane 0 delivery)

# The 1002c floor is WAITING behind w125c, and its waiter now counts legs, not units — 2026-10-02 20:44Z

**State:** the 11111/22222/33333 `--redraw-mode all` floor at pin `0cc052102` has NOT run. The three-arm
half (`value_cycle_ab_s1_three_arm_20261002c.json`) is on disk and graded. The 17:16Z refusal is set aside as
`/var/tmp/se-retake-belief/value_cycle_ab_s1_noise_floor_20261002c.REFUSED_1716Z.json`; nothing sits at `--out`.

**Why the old waiter was replaced, not left:** `longjob-value-arms-retake-at-the-belief-floor` had waited for
w125b's pid. When that exited it moved on to `admit_and_run`, which asks `resource_headroom` about DECLARED
long jobs. w125c had relaunched under a fourth name (`longjob-depth-vs-width-w125c-20261002`), so admission was
deferring correctly, but only because w125c happened to declare 14,500 MB. The 17:16Z refusal came from
`run_value_cycle_ab`'s own check, which counts RESIDENT LEGS, so a leg launched under no declaration would
have refused the floor again. That is two oracles. The floor is now gated on the one that refused it.

**Now in flight:** `longjob-value-arms-1002c-floor-serialised` runs `/var/tmp/se-retake-belief/wait_all_then_floor.sh`.
It loops `pgrep -f '^python3 -m tools\.run_value_cycle_ab'` → `tools.wait_for --pid` on each leg, and re-asks
after 60 s until none is resident. After that it still asks `admit_and_run` (11,200 MB). It has a 12h deadline
and names its refusals (89 = legs never left, 88 = the floor refused itself or wrote nothing; a refusal JSON is
moved aside automatically). The pin is unchanged and `9153f5752` is not picked up. The command is identical to `run.sh`'s.
`longjob-value-arms-1002c-floor-handoff-2` hands the grading on via `seat_continuation`
(`grade-the-1002c-floor-and-move-the-current-world-pointers`) when it exits. The old handoff was stopped
first, so it could not fire on the replacement.

**Expected start:** after w125c's last pair (61005,61006), probably several hours. The floor then takes about
2.7h (3 × ~53 min). Until then the current-world pointers stay where they are, and the page's
reading stays withdrawn against `28eb35ec7`.

**To reverse:** `systemctl --user stop longjob-value-arms-1002c-floor-handoff-2 longjob-value-arms-1002c-floor-serialised`.
