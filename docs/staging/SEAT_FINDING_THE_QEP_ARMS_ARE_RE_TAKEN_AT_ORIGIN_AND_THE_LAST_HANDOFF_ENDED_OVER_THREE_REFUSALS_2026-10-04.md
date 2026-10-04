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
