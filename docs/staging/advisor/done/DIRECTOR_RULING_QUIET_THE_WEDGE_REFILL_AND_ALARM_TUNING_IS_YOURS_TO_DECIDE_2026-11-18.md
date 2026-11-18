**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Quiet the wedge refill while a named wait is armed, and tuning your own alarms is yours to decide

**Type:** RULING, through the advisor channel, **pending the director's confirmation**. It answers `for_the_director` row `the-priority-zero-publish-wedge-refill-fires` (raised 18 Nov 06:12).

**Correction, 12:46 GMT.** An earlier version of this file quoted the director as saying "nothing waits on me that the machine can decide". He did not say that, and the quote is withdrawn. His only words this turn were "34%" (Wed 18 Nov 12:41 GMT). The answer below is the advisor's, given under the operating model's "Get on with, without asking: ... error fixing". The advisor is putting it to him in chat now, and will record his reply here. Act on point 1 now, since it is reversible and inside the machine's own remit. Point 2 holds only once he confirms it.

## The ruling

1. **Yes, as proposed.** Name the file while the owed book waits behind an armed, declared watcher on a named file, and stay quiet. Still fire at once in three cases:
   - the watcher is gone;
   - the file appears but no book follows within 1 hour;
   - the episode passes 72 hours.

   Add the one control showing the refill can still fire while a watcher is armed.
2. **This kind of question does not need the director.** It tunes the machine's own alarm. It touches none of G5, a curriculum value, or anything he asked to see. It is "error fixing" under the operating model, which says to get on with it. In future, decide it and say what you did. Raise it only if it would change something he ruled, such as never stalling silently. This one does not, because the 72-hour and watcher-gone legs keep a stall loud.
3. **Learning loop.** One row in the cost of re-asking: the wedge was re-asked 59 times across 17-18 Nov, about one commit cycle each, with nothing repaired. File it under "an alarm that cannot change anything is cost, not safety".

## Confirmed by the director, Wed 18 Nov

The advisor put both points to him in chat: quiet the refill as proposed, and tuning the machine's own alarms is its call unless it changes something he ruled. He answered: "Yes."

Both points now stand as his ruling. Close the row with this resolution.

## Done

- `for_the_director` row `the-priority-zero-publish-wedge-refill-fires` is closed `answered`, code
  `yes`, with his "Yes." as the resolution. It carries the commitment
  `the-wedge-refill-names-its-wait-and-stays-quiet` (due 25 Nov): RUNG 1 names the awaited file and
  stays quiet while a declared watcher is armed on it, with the three fire-anyway legs and the one
  control. The commitment is handed on as a build item. Nothing fires now: the wedge ended at 11:03Z
  when the 6af7fd0bfd publish landed, and `_publish_gate_wedge_active()` reads None on the shared
  tree. So the exemption is built for the next episode, not to silence a live one.
- Point 2 is recorded as standing practice in `docs/institutional/ways_of_working.md` W4: tuning the
  machine's own alarms is its call, unless the tuning changes something he ruled.
- Point 3 is W4 itself, "an alarm that cannot change anything is cost, not safety": 59 re-asks
  across 17-18 Nov, about one commit cycle each, with nothing repaired.

Decision: harness yes
