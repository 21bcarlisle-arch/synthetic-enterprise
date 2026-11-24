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

## Drawn a third time, at about 17:05Z. Why releasing it did not stop the redraws

Releasing the claim freed it, but it did not retire the continuation. `seat_continuation.retirement_hold`
held the item on `/var/tmp/vtn-driver/grade_rankq.out`, which the item's text names. That file is what
land10 *waits on*, not anything this item produces. The hold treats any absolute path under `/var/tmp/`
as an output the item has to make. `present_at_hand_off` exempts only inputs that already existed when the
item was written, and this precondition did not exist yet. As a result, the item would have been offered
on every draw until rankq finished. `--premise-spent` did not help either: the item already holds a
landing, so it recorded nothing.

**Disposition:** the store's own way out was used. `land10-outcome-is-read-and-msc-lands-or-is-re-cut` was
re-stamped with its text unchanged and now declares `supersedes: [the-msc-landing-is-re-armed-on-artefacts-not-process-names]`,
so the item is retired and will not be drawn again. land10's unit was re-read as active at 17:06Z.

**The general case, not fixed here:** a continuation that names a path it waits on (rather than one it
writes) is held until that path appears. The `--release` refusal could name `--supersedes` as the remedy,
as `origin_refusal` already does.
