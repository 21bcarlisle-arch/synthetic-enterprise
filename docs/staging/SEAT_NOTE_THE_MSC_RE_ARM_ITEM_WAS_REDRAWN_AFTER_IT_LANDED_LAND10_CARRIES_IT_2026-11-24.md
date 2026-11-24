**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The MSC re-arm item was drawn again after it had landed; land10's continuation carries the rest

The item `the-msc-landing-is-re-armed-on-artefacts-not-process-names` was drawn again at about 16:40Z on 24 Nov.
Its work was already done in 971dc97386, which is on origin/main:

- **land9's two deaths are named.** At 07:18Z, worker-tick's cgroup kill took it down. At 13:29Z, the `.` in the
  `--pattern` regex matched `/`, which gave a false FINISHED. That cause is filed as a finding against `tools/wait_for.py`.
- **land10 is armed with artefact-keyed waits.** Its unit `longjob-land10-msc-replacement-win-artefact-waits` was re-read
  as `active` on this draw.
- **land10's dry run reached the gate's door.** The log is `/var/tmp/se-msc-keep/land10-dry.log`.

The remaining work is to read land10's outcome. That belongs to the continuation
`land10-outcome-is-read-and-msc-lands-or-is-re-cut`, which is held until `/var/tmp/se-msc-land10-ended.txt` exists.
Nothing was rebuilt on this draw. The claim is released.
