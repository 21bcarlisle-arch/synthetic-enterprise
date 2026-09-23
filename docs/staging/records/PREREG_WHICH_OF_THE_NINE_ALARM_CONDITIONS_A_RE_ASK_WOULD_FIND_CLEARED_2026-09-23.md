**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: which of the nine alarm conditions a re-ask would find cleared

**Written BEFORE the measurement was run.** The measurement is: for each of the nine live
`WORKER_FINDING_REPEATING_ALARM_*` documents in the staging root, read the `Signature:` line's
key, find that family in `docs/observability/.notify_transitions.json`, and ask how long ago the
condition was last OBSERVED to hold (`last_seen`, which notify stamps on every FIRING and not
only on every send).

## What is already established, and is therefore not what this predicts

Read off the documents' own "Still live" sections, before running anything:

- Seven of the nine carry a still-live line dated **2026-09-22** — so seven fired within roughly
  the last day.
- Two carry no still-live line at all, only a hand-written prose note dated **2026-09-15**:
  `DEADMAN_ORIGIN_FORK` and `SEAT_CLAIM` (`seat-claim:close-the-fork-six-conflict-paths-each-with-a-named-resolution`).
- Every family in the population that is live fires at least once a day: all seven have
  consecutive daily lines. That is the evidence for the quiet bar below, and it was read before
  the bar was chosen rather than after.

## The prediction

**7 STILL HOLDS · 1 NO LONGER HOLDS · 1 CANNOT TELL.**

Reasoning, so that the refutation lands somewhere:

1. The seven that stamped 2026-09-22 will read STILL HOLDS. This is close to a tautology and is
   not the interesting half.
2. The two quiet-since-09-15 families are eight days quiet while the notify contract is
   demonstrably alive (`deadman_commit` fired 1.75h ago, `product-machinery:floor` 0.01h ago), so
   their conditions have almost certainly cleared.
3. **The thing I do not know, and the reason this is written down:** whether those two keys are
   PRESENT in the transitions store under those exact names. `clear_transition()` DELETES a key;
   a key that was cleared, or written under a name the document's `Signature:` line does not
   reproduce, gives a re-ask NO evidence of when the condition last held. The honest answer there
   is CANNOT TELL, not "cleared" — absence of a record is not a record of absence, and a re-ask
   that reads it as one would archive live work. I predict at least one of the two lands there.

## What would refute it

- All nine STILL HOLDS → the store's `last_seen` is not the signal, and the re-ask needs a
  per-family predicate rather than a quiet window.
- Any of the seven reading NO LONGER HOLDS → the quiet bar is too tight and would archive live work.
- Zero CANNOT TELL → the fail-closed third state is unreachable on today's data, and a control
  asserting it would be asserting an unreachable branch (see CLAUDE.md on guards that refuse
  everything).

The answer, and whether this was right, is recorded beside this prediction in the finding filed
with the work.

---

## THE ANSWER, recorded beside the prediction. **The prediction was WRONG on both halves.**

Measured 2026-09-23 22:41Z, over the real population and the real transition store.

**Predicted 7 still_holds / 1 cleared / 1 cannot_tell. Actual: 10 still_holds / 1 cleared / 0
cannot_tell** — over eleven documents, not nine, because the population grew by two while this was
being written (`OPERATIONAL_LAYER_SIGNAL_2026-09-23` arrived in the root, and one document in
`in_progress/` had never been counted at all).

**Both families I predicted would clear are LIVE.** `DEADMAN_ORIGIN_FORK` carries a still-live line
stamped **1.5h** before the measurement, and `SEAT_CLAIM` gained **four** instance lines today. My
"quiet since 2026-09-15" reading came from a `grep | head -8` that truncated above the recent lines
— the documents' own newest lines were never in the evidence I reasoned from.

**The one genuine clear is a document I had not counted:** an old slug-named
`seat-claim` alarm document in `in_progress/`, last observed **2026-08-25**, 29 days quiet. The
2026-08-28 family rule folded all subsequent seat-claims into `SEAT_CLAIM_2026-09-15.md` and left
this orphan behind, where nothing has touched it in a month. That is exactly the sediment the
re-ask is for, and it was invisible to the framing that went looking in the root.

## The mechanism the measurement refuted, which matters more than the count

I predicted CANNOT_TELL for the right reason — absence of a record is not a record of absence — and
the **wrong mechanism**. I guessed `clear_transition()` deleting keys. The real cause for three of
the four store-absent families is that they never reach the store at all: `seat-continuity`,
`seat-claim:*` and `delivery-lane-stranded:*` call `alarm_repetition.escalate()` **directly** and
bypass `notify()` entirely, so they have never written `.notify_transitions.json` and never will.

And the fourth, `deadman_origin_fork`, refutes the store even where the store applies:
`deadmans_switch` calls `clear_transition()` (which DELETES the key) every time the fork closes, so
the condition **oscillates** and its absence from the store is a snapshot, not a clear. It fired
1.5h before I sampled a store that did not contain it.

**So a store-keyed re-ask — the design this pre-registration was written to test — would have
archived four live conditions out of eleven, in the fail-open direction.** The signal that works
for both populations is the documents' own machine-written dated lines, because `_note_still_live`
and `_note_instance` are reached on every call whichever door the caller came through. The store is
still read, but only ever to CONTRADICT a stale-looking document, never to confirm a clear.

Built on that basis: `background/alarm_repetition.reask()`, wired into `staging_watcher.main()`.
