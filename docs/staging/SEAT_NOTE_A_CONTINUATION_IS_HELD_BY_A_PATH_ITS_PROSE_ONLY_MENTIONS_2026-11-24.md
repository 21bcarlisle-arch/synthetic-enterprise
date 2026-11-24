**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A continuation is held open by a path its prose only mentions as someone else's input

The item `the-owed-book-is-not-deferred-by-its-own-waiting-readers` was drawn again at about 23:00Z on 24 Nov.
It had already been delivered:

- **The book is being built.** The book is `run_output_f2c6979d01` (pid 357583, started 21:59Z).
- **A4 is re-armed without holding memory.** Its unit `longjob-a4-ep1-dated-rate-value-arm-queued` is a queued launch.
- **The class fix is on origin.** It is commit 9f2afe0c9.
- **The spent-premise record is on origin.** It is commit 05559f04aa.

`delivery_lane --release` then refused to retire the continuation:
"the artefact it names does not exist yet: /var/tmp/b11m7/readout.json".
`delivery_lane --premise-spent` recorded nothing. It answered "it DELIVERED".
So the item stayed LIVE, and it would have been drawn a third time once readout.json appeared.

**The defect.** `background/seat_continuation.py::named_artefacts` takes every absolute path under the
artefact roots in `what`/`done_means` and treats it as this item's output. Here, readout.json appears only in
the sentence "A4 ... waits for /var/tmp/b11m7/readout.json". That file is an input to a different job, and
nothing in this item produces it or reads it.
`retirement_hold` is right in direction: unknown holds, as decided on 2026-10-27. But it has no way to tell
"my work's output" apart from "a path I described". `_is_removal_target` already carves out one such prose
role. "Waits for X" is a second one.

**Disposition.** Retired by hand with `seat_continuation --drop`. That is justified because the lane store
records the item as delivered on origin, and the A4 unit owns the wait on readout.json itself.

**Not fixed in this turn.** A fix would carve out paths that follow "waits for"/"waiting on" in the prose, the
same way `_is_removal_target` does. It would also need a test showing that a handoff naming its own
`DONE.json` still holds.

NEXT: none -- filed for H_harness; the drawn item is spent
