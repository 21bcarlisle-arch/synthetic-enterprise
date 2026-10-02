**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none

# The world-D arms retake at 0bac2b8be died overnight, and nothing has relaunched it

Found 2026-10-02 ~04:45Z by the scheduled worker, while it was landing PB4's surface. Nothing
was launched or changed here.

**What happened.** Both jobs that `docs/staging/records/SEAT_PREREG_THE_WORLD_D_VALUE_ARMS_RETAKEN_AT_HEAD_0BAC2B8BE_2026-10-02.md`
waits on are dead. `launch_liveness` recorded both as `died` at 00:42Z. No staging item says so,
and no unit is active now.

- `longjob-arms-d-head-1002` was OOM-killed at 00:41:39Z: `Result=oom-kill`, peak 8,400 MB,
  exactly one hour after launch, with no artefact.
- `longjob-floor-d-head-1002-s123` waited 3,600 s on the arms pid. It then refused cleanly on
  memory: a leg needs 11,200 MB and the guest offered 8,277 MB. It wrote the REFUSAL where its
  artefact would go.

**Why it matters.** `cbe8d18a4` withdrew the current-world headline because the 10-01 arms ran
older code than HEAD. This retake is what puts it back. The prereg's own deadline is
2026-10-05T03:00Z. After that, the world-D reading comes off `site/data/value_arms.json`.

**What has changed since.** `f243bd573` (04:29Z) lowered `SETTLEMENT_CUSTOMER_YEAR_BUDGET`
1,250 -> 1,050 to fit today's 6,451 MB sim peak. A relaunch may now fit. That commit also
rescales the settled sample. So a retake at current HEAD is not the 0bac2b8be subject the prereg
names, and the prereg has to be re-pointed (or graded "not run" and re-filed) before a relaunch.

**What is not established.** Why the arms run died at exactly 3,600 s. That is the same span as
the floor's wait, and the 8.4 GB peak is far below the 24 GB guest. A unit `MemoryMax` from the
launcher is the first thing to read. The worker did not read it.
