**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# FINDING — the nightly HEAD-green census has timed out four nights running, and systemd records each run as a success

Found by the mothball census of 2026-09-27 (Lane 0, `mothball-census-retire-what-no-longer-runs`),
which asked every unit when it last produced real output rather than when it last exited 0.

**What happens.** `head-green-census.service` (`tools/head_green_census.py --notify`) fired at about
03:33 on each of 2026-09-24, 25, 26 and 27. Each night the journal reads the same three lines:

    [head-green-census] the suite did not finish inside 7200s -- UNPROVEN. ...
    UNPROVEN: no pytest summary line -- the run's own output is unreadable
      register not updated: the run proved nothing, so it observed nothing

`systemctl --user show head-green-census.service` reports `Result=success ExecMainStatus=0`, and
`docs/staging/reference/HEAD_RED_REGISTER.md` was last written 2026-09-24 15:02. The doorbells still
quote it ("observed 2026-09-23").

**Why.** `SUITE_TIMEOUT_SECONDS = 7200` was set on 2026-09-02 as more than twice the worst
measured duration then (3537 s). The collection has grown since then: 38,426 tests at HEAD on
2026-09-27. The comment on the constant says a bound under the true duration "aborts a healthy slow
night and reports the same silence the reordering was meant to end". That is now happening
every night.

**What it is not.** A stale register is not evidence of a red tree. The census fails closed
correctly (UNPROVEN, not green), so the register is only *old*, not wrong.

**What is owed.** A measurement first: how long the unscoped suite takes today, run once
outside the unit. The bound then follows the constant's own rule (`bound > 2 x worst measured`, with
`TimeoutStartSec` above it). If that no longer fits one night, the census has to be split. A
number picked to make tonight pass is the wrong fix. `test_the_census_timeout_clears_the_duration_it_has_observed`
holds the relationship against the unit file.
