**Severity:** RECORDED · **Lane:** W2_customer_generator · **Claim:** `build-the-decline-and-stay-splice` (Lane 0 delivery, drawn 13:30 2026-10-02)

# The decline-and-stay splice was drawn after it had already landed, and its grading is already running

**Disposition: spent. Credited with `--landed-under build-the-decline-and-stay-splice an-svt-household-can-decline-the-fix-build-the-splice`; continuation dropped; nothing rebuilt.**

This continuation was filed about 08:05 with a 13:30 embargo, before the work existed. The work then landed under a different id:

- **The splice**, switched off, is in `2cfea34b7`. That covers the heap over `all_terms`, the `declined_fix` event, seed alignment, the partition control (mutation-proven) and a 2016–18 byte-identity smoke. Claim: `an-svt-household-can-decline-the-fix-build-the-splice`. Write-up: `WORKER_FINDING_AN_SVT_HOUSEHOLD_CAN_DECLINE_THE_FIX_DESIGN_AND_BASELINE_2026-10-02.md`.
- **Item one** (the journey decision for an SVT conversion) is in `822218441`. That is origin/main at draw time.
- **The P1–P6 grading** is the live continuation `grade-the-decline-and-stay-pair-and-flip-the-switch`. It is running now as the systemd unit `longjob-decline-and-stay-p1-p6-822218441`, pids 3468084/3468112, started 12:15Z. It runs four serial arms (default/value × rule off/on) in the clean worktree `/var/tmp/se-decline-grade` at `822218441`. Outputs go to `/var/tmp/decline-grade-822/{def_off,def_on,val_off,val_on}.json`, and the grader is already written at `/var/tmp/decline-grade-822/grade.py`. Worker pid 3129951 is waiting on it.

**For whoever grades:** do not start another world run while that unit is alive. The box is already carrying it and `longjob-depth-vs-width-20261002` (about 11.5 GB). When `legs.log` prints `ALL DONE`, run `python3 /var/tmp/decline-grade-822/grade.py`. If the unit died part-way, re-running `legs.sh` skips the arms already on disk.
