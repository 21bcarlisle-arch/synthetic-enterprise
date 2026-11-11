**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Three of today's four orientations missed origin, and two of them lost to a second writer on DIRECTION.yaml (2026-11-11)

**Measured** from `docs/direction/decisions.jsonl` (the refused rows' `landing_refused`) and the
`delivery-seat` journal.

| Oriented | Landing | Cause |
|---|---|---|
| 09:22 | a82f0f0bb | landed |
| 12:24 | refused | `DirectionNotLanded`: origin's DIRECTION.yaml was edited by another writer during the gate (origin at 53709c683) |
| 15:20 | refused | `LandingRefused`: GATE RED, site tests failed on the tree the commit would create |
| 18:22 | refused | `DirectionNotLanded`: 74badda3a5 (worker tick, "advisor: 44% at Wed 18:10 actioned") edited DIRECTION.yaml at 18:37, while the seat was gating |

**Why the unit read success:** `main()` returned 0 unconditionally, and the refusal reason sat only on the
appended copy of the row. **Fixed at 56b6a626b:** a record that did not reach origin now exits 1, with
`DIRECTION RECORD NOT ON ORIGIN (oriented <at>): <reason>` on stderr. The 18:22 run started before
that fix landed, so it still exited 0.

**Still open, and this is the finding.** The seat takes about 40 minutes from brief to landing, and it
refuses when DIRECTION.yaml moves on origin in that time. That is the right choice: it will not overwrite
an edit it never read. But the advisor-actioning path (the worker tick, acting on a director reading)
writes the same file during that window. At 18:22 the two writers had the same goal: the seat's record
already paused W3_3 and moved it to `not_now`, as 74badda3a5 did. The refusal kept the 09:22 steer on
origin for another three hours, and the steer it protected was the one both writers were replacing.

**Proposal (reversible, harness only):** while `delivery-seat.service` is active, a non-seat writer that
needs to edit DIRECTION.yaml should leave the edit to the seat's next record, or wait on the unit
(`tools/wait_for.py --pid`). It should not land underneath the seat. The other option is for the seat,
on this refusal, to re-run only the write-time check against origin's new copy, and land if every row
origin added is carried. That is more code and a judgement made in code, so I recommend the first.
Until one of them is built, the seat's landing still fails closed and now says so in the unit state.

**Disposition this turn:** the 18:22 record went onto origin by hand from the seat-executor worktree.
The 18:22 record already carries 74badda3a5's edit, so nothing is lost. The append-only files were checked
as pure appends over origin. 204e12734 (the 12:24 record) was not landed, because it is superseded.
