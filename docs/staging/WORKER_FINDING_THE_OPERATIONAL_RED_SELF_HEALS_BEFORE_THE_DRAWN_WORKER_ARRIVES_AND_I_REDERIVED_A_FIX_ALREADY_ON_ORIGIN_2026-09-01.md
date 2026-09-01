**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS1_process_manifest_reconstruction`

# The operational-layer red self-heals before the drawn worker arrives, and I re-derived a fix that was already on origin

**Found:** 2026-09-01 02:38–03:00 UTC+1, working the PRIORITY-ZERO operational-layer persistent-red
draw. Not by a control — by doing the drawn work and then checking, late, whether it was already done.

This is the measured sequel to
[`WORKER_FINDING_THE_UNCOMMITTED_GUARD_I_WAS_TOLD_TO_DECIDE_ON_HAD_ALREADY_LANDED_ON_ORIGIN`](WORKER_FINDING_THE_UNCOMMITTED_GUARD_I_WAS_TOLD_TO_DECIDE_ON_HAD_ALREADY_LANDED_ON_ORIGIN_2026-09-01.md).
That finding established that `git status` on this machine answers against a stale base. This one
prices it: **a whole priority-zero turn, spent rebuilding a fix that had been on `origin/main` for
twenty minutes before the turn started.**

## The defect, one line

`background/autonomous_runner._parse_reset_minutes` resolved a bare `HH:MM` onto **today** via
`now.replace(...)`, so a reset time belonging to a neighbouring day was read as the wrong day —
and at 01:27 a limit that lifted two hours ago read as lifting in **twenty-two**.

That is not a daemon-lifecycle regression. The operational-layer alarm text says
*"it is a daemon-lifecycle test regression"* and names the daemons; it was neither.

## Why paging did not fix it — the part that is new

The alarm fired four times and the doorbell says *"past paging, so paging did NOT get it fixed."*
The reason is not that nobody looked. **The red is windowed by the wall clock, and the window had
closed by the time anyone arrived.**

The failing tests build their fixtures from `datetime.now()` (`_in_minutes(-120)`, `_in_minutes(+90)`).
Whether the arithmetic crosses midnight depends on what time the suite runs:

Replaying the stale arithmetic against the three logged checks reproduces them **test for test** —
which is the check that this account is the right one and not merely a plausible one:

| check (UTC) | local | `-120` reads | `+90` reads | tests that fail | logged |
|---|---|---|---|---|---|
| 22:49 | 23:49 | `-120` fine | **`-1350`** | the 4 future-offset tests | 4 ✓ |
| 23:49 | 00:49 | **`+1320`** | `+90` fine | the `-120` test | 1 ✓ |
| 00:54 | 01:54 | **`+1320`** | `+90` fine | the `-120` test | 1 ✓ |
| 02:38 | 03:38 | `-120` fine | `+90` fine | none | — |

The red window is local **22:30 → 02:00**, and nothing else. Outside it the suite is green with the
defect fully present.

I ran the exact signal argv at 02:38 local against the **unrepaired** tree and it returned
`1187 passed, 1 xfailed` — exit 0. A drawn worker arriving any time between ~02:00 and ~22:30 finds
the suite green, finds nothing to fix, and leaves. **The alarm is only true while nobody is awake to
answer it.** That is why four pages produced no repair, and it will recur tonight after ~22:30
against any tree still carrying the old bytes.

## The evidence that the tree was stale: I rebuilt the fix, independently, and it already existed

Before checking origin I diagnosed the defect and wrote a repair: resolve the bare clock time to the
**nearest** of yesterday/today/tomorrow. I printed it across the clock — 42 inputs, 0 misreads — and
was about to write a clock-pinned control for it.

`origin/main` already had that fix, committed at **02:18**, twenty minutes before my turn began. Not
merely the same idea — the same `min(candidates, key=abs difference)` construction, plus two things
my draft lacked: an injectable `now`, and exactly the control I was about to write,
`test_a_reset_time_is_read_the_same_way_at_every_hour_of_the_day`, carrying its own named mutation.

The working-tree copy was strictly the older draft: `git diff origin/main` showed 7 insertions
against 28 deletions, the deletions being origin's fix and its test.

**My re-derivation is the measurement.** Two lanes, hours apart, independently produced the same
repair for the same defect, because the second could not see the first.

## Mutation proof that the repair is load-bearing

Origin's clock-pinned control, run against the stale draft I had in the tree:

```
  01:27  -120 ->   1320  <-- FIRES    +90 ->     90
  09:00  -120 ->   -120               +90 ->     90
  13:45  -120 ->   -120               +90 ->     90
  23:59  -120 ->   -120               +90 ->  -1350  <-- FIRES
  00:00  -120 ->   1320  <-- FIRES    +90 ->     90
  12:00  -120 ->   -120               +90 ->     90
```

3 of 12 assertions fire on the stale draft; 0 of 12 on origin's. `1320` is the twenty-two-hours-out
reading that was live. The control is not a tautology, and it is not keyed to today's answer — it
pins the property at six hours of the day, so it cannot self-heal at 02:00 the way its predecessors did.

## What I did

- Backed both superseded drafts up to `/var/tmp/se-superseded-drafts-20260901/` (recoverable).
- Restored `background/autonomous_runner.py` and `tests/background/test_autonomous_runner.py` to
  `origin/main`'s bytes via `git show origin/main:<path> > <path>` — not `git checkout`, and not a
  new commit. **The code change is already committed; re-committing it is the defect, not the fix.**
  Both files now match origin exactly, so origin's own new `tree_divergence` leg reports them under
  `already_on_origin` rather than as uncommitted work.
- Confirmed: `tests/background/test_autonomous_runner.py` → 23 passed, including the clock-pinned control.

## What I did NOT do, and why it is the director's call

**Local `main` is 23 commits behind `origin/main` and 1 ahead.** The 1 is a daemon auto-process
commit; the 23 include the merge a lane already performed at 01:55 (`82aae13ae`, *"the tree had two
histories for ten hours"*), which itself reported 18 conflicted files. The daemon has since committed
onto the stale local branch and re-diverged, and the publish has been refusing a non-fast-forward
push since 23:51.

44 locally-modified files collide with those 23 commits. I verified two of them are superseded drafts.
**I did not verify the other 42, and I will not merge on that basis in a bounded tick with a live
`process_run_complete` holding the tree** — sweeping another lane's genuine unstaged work is not
reversible. Re-running the merge is the actual repair; it needs the tree quiesced and the daemon
stopped, which is a console action.

## The standing defect this leaves

Restoring two files clears tonight's red. It does not stop the next one. While local `main` sits
behind `origin/main`:

- every lane on this machine draws against a stale premise and can re-derive landed work, as I did;
- the operational-layer alarm keeps naming daemons for defects that are neither in daemons nor in
  the tree that origin publishes;
- and the alarm's own text — *"This is NOT a daemon-lifecycle regression"* — has a `blocked_by` arm
  for uncollectable files but **no arm for "the tree under test is behind the trunk"**. That is the
  arm worth building, and it is one comparison: the signal should refuse, not grade, when
  `origin/main...HEAD` shows the working tree is not the trunk's.
