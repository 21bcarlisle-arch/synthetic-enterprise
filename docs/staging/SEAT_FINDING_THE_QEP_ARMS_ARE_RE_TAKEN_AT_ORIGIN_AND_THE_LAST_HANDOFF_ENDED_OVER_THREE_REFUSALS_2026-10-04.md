# The QEP value arms are re-taken at origin, and the last handoff ended over three refusals

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-qep-value-arms-are-retaken-at-origin-one-leg-at-a-time` (Lane 0 delivery)

## Premise, re-measured at draw

The two cited commits (`ba320e2d2`, `24ece7adb`) being on origin does not spend this item. It is about
re-taking the arms on a base that *contains* `ba320e2d2`, and no `20261004*` arm artefact exists on
origin. The duplicate claim the draw named is this item's own id (it was the draw's own write). No
rival seat or `surgical_land` was running (`ps`, 03:20Z).

## What was found

The first attempt's four legs are all dead, and none of them left a finished artefact:

- `longjob-qep-arms-three-arm` stopped at 2023-01 in the decade. It was OOM-killed while sharing
  memory with the term probes.
- `/var/tmp/se-qep-arms-handoff.sh` waited on `systemctl is-active`. It did not ask whether the
  three-arm leg had *succeeded*, so it launched all three floor seeds onto a dead predecessor. The
  floor's own admission refused each one (needs 11,200 MB, 4,680 MB offered). Each wrote a
  `floor_run_refused` artefact and exited 2. The handoff's `until launch_long_job` loop retries only
  a refused **launch**, not a refused **run**. So it moved on, and it printed
  `END all three seeds exited` over three refusals. Its `--peak-mb 6500` was also below the 11,200 MB
  the floor itself prices, which is how the launcher admitted runs the floor then refused.

The latent class: a chain of jobs whose links check "is the unit gone" rather than "is the artefact a
result" reports a finished chain over nothing. The refusal artefact did its job, and it is the
handoff that read it as done.

## What was done

- Fresh worktree `/var/tmp/se-qep-arms2` at origin `96517e68c` (it contains `ba320e2d2`). The refit
  patch applied there with `git apply --3way`, clean. The worktree is locked and its owner file is
  written. The world digest reproduces as `cdba75ebb9197b33`.
- `longjob-qep2-arms-three-arm` (`--level-arm`, peak 11,200 MB) is queued with `--wait-for-pid`
  behind another lane's 4.6 GB, still-growing `channel_blind/measure.py`. Admission would have let
  it start beside that run with about 1 GB of slack, which is the shape that OOM-killed the first
  attempt.
- `longjob-qep2-arms-floor-handoff` (`/var/tmp/se-qep-arms2-handoff.sh`) works as follows:
  - It STOPS unless the three-arm artefact parses and is not a refusal.
  - It runs the seeds one at a time and declares a peak of 11,200 MB.
  - It deletes and retries a `floor_run_refused` artefact (every 5 min, at most 48 times).
  - It stops if a seed exits with no artefact.
- `docs/design/UNLANDED_QEP_LEVEL_ANCHOR_REFIT_2026-10-04.md` now names this run. Its artefacts use
  the suffix `20261004r`.

## Not done

The landing sequence in that doc: fold, regenerate the verdicts, move the pointers, re-key the reds,
and land the refit with its arms in one commit. That waits on all four artefacts, about 9 hours of
runs. It is handed on as a continuation.

## Third attempt (06:31 BST, claim `land-the-qep-level-anchor-refit-with-its-value-arms`): a per-seed floor leg cannot run

### What was found

- **The second attempt's three-arm leg FINISHED.** `/var/tmp/se-qep-arms2/docs/observability/value_cycle_ab_s1_three_arm_20261004r.json`
  is on digest `cdba75ebb9197b33`. It took 68 min with an 8.1 GB peak.
- **Its floor handoff died in 8 seconds.** `/var/tmp/se-qep-arms2-handoff.sh` ran each seed as its
  own process (`--noise-floor-seeds 11111`). `tools/run_value_cycle_ab.py::noise_floor` raises
  `AssertionError: a noise floor needs at least two seeds; got 1`. The refusal is correct, and it is
  the floor's own subject: one seed has no spread. The handoff's stop on "exited with no artefact"
  worked as designed (`STOP s11111 ... later seeds not launched`).
- Both handoffs ran the same way: "one seed per leg, fold afterwards". The landing sequence's
  "fold the three s*.json" step and the first attempt's `-s<seed>` legs inherited it. `--fold` pools
  runs that already exist, and each of those runs needs at least two seeds. A per-seed leg can
  never exist, so it can never be folded.

The latent class: a plan's split into legs was never checked against the tool's own lower bound on
a leg. A five-second dry run of one leg would have shown it. That dry run was skipped because each
leg was priced in hours.

### What was done

- `longjob-qep3-arms-floor` was launched at 05:31:54Z in `/var/tmp/se-qep-arms2`:
  `--noise-floor-seeds 11111,22222,33333 --redraw-mode all`, peak 11,200 MB. Admission was 18.9 of
  23.0 GB. It writes `docs/observability/value_cycle_ab_s1_noise_floor_20261004r.json` directly, so no
  fold is needed. Expected end is about 09:00Z (9 passes at the three-arm's 23 min per pass).
- `docs/design/UNLANDED_QEP_LEVEL_ANCHOR_REFIT_2026-10-04.md` records the outcome and marks landing
  step 1 (the fold) as spent.

### Not done

Landing steps 2–6 wait on the floor. They are handed on as a continuation, embargoed to the floor's
expected end.
