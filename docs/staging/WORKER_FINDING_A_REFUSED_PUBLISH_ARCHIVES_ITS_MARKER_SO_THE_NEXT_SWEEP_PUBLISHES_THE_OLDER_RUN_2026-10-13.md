**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** publish-wedge draw (worker), 2026-10-13 ~22:20 BST

# A refused publish archives its marker, so the next sweep publishes the older run

**Fate (2026-10-14):** ATOM -- harness, next week: the mechanism it proposes is unbuilt; the marker was moved back by hand.

**The wedge itself is diagnosed and fixed. This note is about what was left behind.** The publisher
failed at 20:50 UTC on `run_complete_20261013T134447Z.md`, and that run was graded at 2248e3baf. The
`tests/` gate passed. The site-lane gate then refused, with 72 failed and 7 errors. `0d5304e98`
(20:54 UTC) traced that to ENOSPC on /tmp. In this invocation `pytest site/` ran in a clean worktree
at HEAD 93f5b1977: 1228 passed, 87 skipped, 0 failed. /tmp is at 52%. The next gate in the hook
chain is `startup_anchor_freshness --gate`. Its REFUSED lines in the worker log come from the
no-flag publish run. In gate mode a staged anchor is dated today (`true_last_change`, line 441), and
the working tree passes it with rc=0.

**The defect.** `process_run_complete` moves the marker into `done/` BEFORE it commits, so that the
archive lands in the same commit. When the commit is refused, the marker is stamped
`did-not-land` and stays in `done/`. `_newest_published_stamp` reads that stamp correctly, so the
refused run does not become the frontier. But `process_leftover_run_markers` only globs the staging
ROOT, so the refused marker is never re-attempted. The queue then held only the OLDER marker,
`run_complete_20261013T033930Z.md` (2f5c926dc). The next sweep would have published that one,
which is the newest-first rule (OPS3, 2026-08-14) broken from the other side: the newest snapshot
had a fix waiting and was dropped. The publisher's own log line "the next identical run must
re-attempt it" has no route to make that happen.

**What I did (reversible):** I moved `run_complete_20261013T134447Z.md` from `done/` back to the
staging root. `classify_markers` now returns both as pending (frontier 20261011T232758Z), and
134447Z is first. To undo it, move the file back to `done/`. The director was told on NTFY (id
`Rrvtmx3bSAJM`).

**Proposed mechanism (not built in this tick):** the sweep should also collect markers in `done/`
that are stamped `did-not-land` and newer than the frontier, and treat them as pending. That
reuses the existing reader (`staging_archive_policy.publish_did_not_land`). Its control should
plant a refused newer marker in `done/` with an older one queued, and assert that the newer one
is processed first. The partition control should assert that both outcomes can be reached.

**Still owed:** R11, which means reading the live site once the sweep's publish lands.
