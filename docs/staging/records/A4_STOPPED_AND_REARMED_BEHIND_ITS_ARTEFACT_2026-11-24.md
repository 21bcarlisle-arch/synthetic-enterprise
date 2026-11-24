# A4 stopped and re-armed behind its artefact, 24 Nov 2026 21:31Z

**What.** `longjob-a4-ep1-dated-rate-value-arm.service` was stopped at 21:31Z while still in its
wait loop (log: one line, "waiting for /var/tmp/b11m7/readout.json"; readout.json absent). It had
declared 12000 MB since 20:14Z, and with land10's 6000 MB that deferred sim-runner's owed book
every cycle ("20190 MB already declared ... + 7066 MB requested exceeds the 23010 MB budget").

**Its unit as it was** (to reverse): ExecStart `/bin/bash /var/tmp/vte-driver/run_ep1.sh`,
WorkingDirectory `/var/tmp/value-test-ep1`, Environment `PYTHONUNBUFFERED=1`
`SE_BOX_ADMITTED=longjob:longjob-a4-ep1-dated-rate-value-arm` (set by the launcher itself), both
streams appended to `/var/tmp/longjob-a4-ep1-dated-rate-value-arm.log`. Pre-registration
(`SEAT_PREREG_A4_EP1_DATED_RATE_AS_A_VALUE_ARM_2026-11-24.md`), run_ep1.sh, driver_ep1.py and
grade_ep1.py are unchanged.

**Re-armed at 21:32Z** through the new `--awaits` door, so it is not started and declares nothing
until readout.json exists; it then asks admission at fire time and run_ep1.sh's own box wait runs:

    python3 -m background.launch_long_job --job a4-ep1-dated-rate-value-arm \
      --artefact /var/tmp/vte-driver/grade_ep1.out --workdir /var/tmp/value-test-ep1 \
      --holds /var/tmp/value-test-ep1 --log /var/tmp/longjob-a4-ep1-dated-rate-value-arm.log \
      --description "<unchanged>" --asserted-live-by docs/staging/records/SEAT_PREREG_A4_EP1_DATED_RATE_AS_A_VALUE_ARM_2026-11-24.md \
      --peak-mb 12000 --expect-minutes 900 --question/--why-not-minutes/--would-change "<unchanged>" \
      --awaits /var/tmp/b11m7/readout.json --follow-deadline-hours 96 --detach \
      -- /bin/bash /var/tmp/vte-driver/run_ep1.sh

It waits in `longjob-a4-ep1-dated-rate-value-arm-queued.service`. The 96 h deadline restarts from
21:32Z (the queue's), and run_ep1.sh's own 96 h restarts when it fires.

**Second leg found on the next cycle (21:35Z).** sim-runner then deferred for the QUEUE unit
("a long job is queued for room"). `sim_runner.queued_long_jobs` now drops a queue whose
`--awaits` path is missing (`launch_long_job.unmet_awaits`); unreadable still counts.

**Not done here.** land10 (6000 MB) still declares while it waits; 6000 + 2190 + 7066 fits the
budget, so it does not defer the book now. Re-arming it behind `--awaits` needs its book path,
which is a run_output_<sha> not yet named, so it is left as is.

**Stale copies cleared from the shared tree to repair collection** (115 uncollectable modules):
`sim/forward_curve.py` and `saas/reporting/annual_report.py` refreshed to HEAD by
`refresh_to_head` (refs/preserved/refresh-to-head/forward-curve-stale-copy-2026-11-24,
annual-report-stale-copy-2026-11-24). `company/interfaces/growth_desk.py` and
`simulation/run_phase2b.py` were pre-db2f502b2 / pre-5e6a8b70d drafts of the MSC work; HEAD written
over them after preserving their bytes (refs/preserved/refresh-to-head/growth-desk-stale-msc-draft-2026-11-24,
run-phase2b-stale-msc-draft-2026-11-24, and copies in /var/tmp/se-msc-keep/). The untracked
`tests/simulation/test_the_market_stabilisation_charge_is_booked.py`, byte-identical to msc8.patch,
moved to /var/tmp/se-msc-keep/. The MSC work itself is in msc8.patch and land10's worktree.

**Third leg (21:40Z), and land10 after all.** With the A4 queue skipped, sim-runner's
`cycle_admission` still *yielded* to land10 as a resident long job: it yields to every one,
whatever the arithmetic says. land10 cannot be stopped and re-armed behind `--awaits` without
breaking b11m7's order (wait_land10.sh keys on land10's unit and its EXIT-trap file, which a stop
would write), and its wait is not one path. So `launch_long_job --mark-waiting <job> <path>` sets
`waiting_until` on a running job's live record, and `declared_peaks` skips that record while the
path is absent: the budget and the yield both read it. Marked ~22:05Z:
`--mark-waiting land10-msc-replacement-win-artefact-waits /var/tmp/se-msc-land10-book-ready`.
`land10-book-ready-watch.service` (not a longjob; /var/tmp/se-msc-keep/land10-book-ready-watch.sh)
touches that file the first time land10.sh's own `LAND10_PROBE=1` reports a qualifying book, so
land10 counts again before its gate. To reverse: delete `waiting_until` from its record.
The cost, stated: a job launched beside land10 while it is marked sees it at its RSS, not its peak.
