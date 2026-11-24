**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A lane-0 item whose whole deliverable is a `for_the_director` row cannot be retired, so it will be drawn again

**What happened, 24 Nov.** The item `rankq-equal-volume-question-carried-to-the-director-row` asked for context to be added
beside the director's `s-12g-rank-at-q-run-graded` row. That landed and was promoted as **`49b62d352`**: a `context` field
plus `context_evidence` on the row, with his fields left unchanged. **The work is done. If this id is drawn again, release it.
There is nothing left to build.**

**What the lane said, in order:**
1. promote: `bound NOTHING ... touched only the SEAT'S RECORD ... If recording was the whole deliverable, --release the claim`
   (`background/delivery_lane.py` ~3352).
2. `--release`: `did NOT retire the continuation ... no landing is bound to it and no spent premise is recorded ... it stays offered`.
3. `--landed --commit 49b62d352`, after the release: `NOT CLAIMED`.
4. `--premise-spent <id> 49b62d352 <reason>`: `was never drawn -- neither the ledger nor the claims store has heard of it`.

So the bind leg tells the caller that releasing is enough, and the release leg then refuses to retire without a bind. The
spent-premise leg cannot see an id the executor drew. Any direction item whose deliverable is a seat-record edit gets
re-offered, and the turn that drew it is logged `LANDED NOTHING`.

**Proposed fix, one leg (not built here):** when `record_landing` refuses because the commit is confined to the seat's
record, `--release` should accept that commit on origin/main as the item's DONE. Either that, or the refusal message should
stop saying "--release" is sufficient. Mutation check for the fix: the same seat-record-only commit must still be refused as
*credit* for an item whose DONE names a non-record path.

**Correction, later 24 Nov (the redraw this finding predicted happened).** The executor drew the id again. With the id now
drawn, step 4 no longer holds: `--premise-spent rankq-equal-volume-question-carried-to-the-director-row 49b62d352 <reason>`
was accepted ("window is disposed as premise-spent by 49b62d352"). So the working retirement for a record-only deliverable
is: let the item be redrawn, then `--premise-spent` against the commit that landed it. The defect narrows to the first turn:
the turn that does the work cannot retire it, and one redraw is spent finding that out. The one-leg fix above still stands.
