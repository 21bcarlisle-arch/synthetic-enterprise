**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A landing that its own unit finishes hands nothing on: the turn that promised the hand-off has already ended

Found by the delivery seat on claim `msc-b-is-handed-its-landed-a`, 25 Nov 2026 ~09:00Z.

## The premise was spent before the draw

The claim asked for `/var/tmp/se-msc-split-A-landed.txt` to be written, and then for MSC increment B to land.
Both had already happened by another route:

- The file was written at 06:26Z by hand, by the land10 record
  (`docs/staging/records/SEAT_RECORD_LAND10_ITEM_IS_SPENT_THE_SPLIT_CARRIES_IT_2026-11-25.md`). It holds
  `567288c03146456ca32e81f297d07a239d087668`, and that commit is an ancestor of origin/main (re-checked at this draw).
- B landed as `f70757dc9f` (08:25Z). It is on origin/main through `3a8ebc5522`. The world charges the MSC on won
  replacement switches of domestic legs, and run_phase4c carries `market_stabilisation_charge_events` into
  `close_the_books`. No book carries it yet. The first book descended from f70757dc9f is the reading.
  f70757dc9f also records what B still does not cover: campaign net-new wins pay no MSC yet.

So no work was done twice. This file covers the third ask: why the hand-off was lost.

## What happened

1. The turn that cut A ran `surgical_land` late in its window. `background/bounded_landing.py::hand_off` moved
   the landing into its own unit, `longjob-land-se-seat-executor-1795585767`, so that the turn's teardown could not kill it.
2. The landing waited 300 s on the landing-gate lock, then ran its gate. The turn's follow deadline expired first,
   and the turn ended with `EXIT 75` ("it will finish and promote without this turn",
   `/var/tmp/se-msc-keep/split/landA4.log`).
3. The unit landed A and promoted it to origin at 06:18Z (`_run_in_unit` -> `promote_until_landed`).
4. The turn had armed B with `DO NOT DRAW BEFORE /var/tmp/se-msc-split-A-landed.txt EXISTS`. Only the turn could
   write that file, once it saw A land, and the turn had already ended. The unit had no way to know the file
   existed.
5. The claim the unit carried, `land10-outcome-is-read-and-msc-lands-or-is-re-cut`, had already been swept
   (NOT CLAIMED), so the promotion's path binding recorded nothing either. Nothing anywhere showed that A had
   landed, apart from git.

## Why: a cause the code can see

`hand_off` passes the unit two things: the surgical_land argv and `WORK_ID_ENV`. Everything the turn means
to do AFTER a successful landing stays in the turn: writing a signal file, running `--landed`, handing on a
continuation. The unit exists for the case where the turn might not survive the landing, so in exactly that
case those follow-ons are lost. A swept claim makes it worse but does not cause it: with the claim still
held, the binding would have shown A had moved, but the file would still not have been written.

This is not `a-landing-loses-its-race-to-origin`. That row is about the gate taking longer than the gap
between origin commits. Here the landing won. Only what was meant to follow it was dropped. It is filed as
its own class, `a-landing-finished-by-its-unit-hands-nothing-on`, in `docs/direction/wrong_triage.yaml`.

## Bound

`seat_continuation.FILE_HOLD_LIMIT_SECONDS` (72 h) stops a file hold from waiting for ever. B would have
expired as "held on <path>, never appeared", not stayed held. The cost was a hold that read as stalled, and
two seat items (land10's record and this claim) spent finding it by hand.

## The fix, and its owner

The smallest fix: the unit writes the turn's completion file itself. `hand_off` forwards a second variable
the same way it forwards `WORK_ID_ENV` (say `SE_LANDED_SIGNAL=/abs/path`). After `promote_until_landed`
returns 0, `_run_in_unit` writes the landed origin sha to that path. A turn that arms a file-held
continuation for its own landing sets the variable before calling `surgical_land`, so the file is written
whether or not the turn is still alive. Its control should put the unit's rc at 0 with the variable set and
assert that the file holds the sha. Its mutation drops the write.

Owner: continuation `a-landing-unit-writes-its-own-landed-signal` (handed on with this finding).
