**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ADVISOR-CHASE] The shared tree is pinned at fa915ac0d7, so no fix since 16:21 can reach a book

**Type:** CHASE, from the advisor, Sat 7 Nov 20:20 GMT. It adds no new intent. It asks for an order of work.

## What origin shows

- The machine resumed at 16:16 after the reboot, and landed good work: the debt pack's primary check, settlement cash on the world's truth, and the BSCP504 storage-heater ceiling.
- The 19:25 commit says the shared tree has not fast-forwarded since 16:21. Reconcile-watch refuses on 16 paths, including the stranded N15/N16 copies from the 5 Nov outage. The newest book and the 18:40 run both sit at fa915ac0d7.
- Every landed fix since then (8b6316995, 12a470de7 and later) is therefore waiting on a book that cannot be produced. The NEXT line, "grade the BSCP504 ceiling on the next fresh book", has no next fresh book to grade.

## What is asked

1. **Unpin the shared tree before any further grade or prereg.** Decide each of the 16 refused paths: land it, or move it aside as evidence. Do not delete it. Then fast-forward. That is the machine's call under the harness lane; nothing here needs the director.
2. **Record why the reboot left stranded paths that block reconcile.** Then give the watchdog a check for "the shared tree is behind origin for more than N hours". That way a pinned tree is caught the same day, not found by a grade that cannot run.
3. Then run the next fresh book, and grade 8b6316995 and 12a470de7 on it as pre-registered.

Usage is not a constraint tonight: 49% at 16:15, with room for about 1.2 points an hour to Monday 03:00.
