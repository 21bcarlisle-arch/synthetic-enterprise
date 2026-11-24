# The owed book is not deferred by its own waiting readers: premise spent, 24 Nov 2026 22:40Z

Redrawn after it was done. Re-measured against origin/main:

- **Book building.** sim-runner log 21:59Z: "Starting run — git=f2c6979d01, json=run_output_f2c6979d01_20261124T215935Z.json";
  `git merge-base --is-ancestor 31bf40e03 f2c6979d01` holds. Heartbeats at 22:01Z and 22:31Z.
- **A4 re-armed declaring nothing.** Only `longjob-a4-ep1-dated-rate-value-arm-queued.service` is live
  (behind `--awaits /var/tmp/b11m7/readout.json`); re-arm command and the unit as it was are in
  `A4_STOPPED_AND_REARMED_BEHIND_ITS_ARTEFACT_2026-11-24.md`.
- **Class fix on origin with its mutation.** 9f2afe0c9 (ancestor of origin/main): `--awaits` queue skipped by
  `sim_runner.queued_long_jobs`; `--mark-waiting` / `declared_peaks` skips a running job while its path is absent;
  test `tests/background/test_a_waiting_long_job_cannot_defer_the_book_it_waits_for.py`; dropping
  `not still_waiting(r)` reds it.

Disposition: `--premise-spent ... 9f2afe0c9`, then `--release`. No new work done.
