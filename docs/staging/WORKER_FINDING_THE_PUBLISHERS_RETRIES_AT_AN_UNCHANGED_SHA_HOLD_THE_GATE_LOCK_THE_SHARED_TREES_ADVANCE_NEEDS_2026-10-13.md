**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `OPS6_scoped_publish_path_suite` · **Claim:** publish-wedge draw (worker), 2026-10-13 ~18:35 BST

# The publisher's retries at an unchanged sha hold the gate lock the shared tree's advance needs

**Fate (2026-10-15):** ATOM -- folds into `OPS6_scoped_publish_path_suite` (re-pointed 2026-10-15; an ATOM fate names its atom).
**Fate (2026-10-14):** ATOM -- harness, next week: the publisher's retries and the reconciler's advance can still starve each other.

This follows `done/SEAT_FINDING_THE_PUBLISH_IS_HELD_BY_THE_SHARED_TREES_STALE_HEAD_NOT_BY_A_LIVE_RED_2026-10-13.md`.
That finding's diagnosis still holds. The publisher grades a clean checkout of the shared HEAD,
2248e3baf. That HEAD lacks 81c129fe8, so the census test is red there. It is green on disk and at origin.

**What is new: the remedy and the failure starve each other.** `background.origin_reconcile` will not
move the shared tree while the publish gate holds its run lock (`GATE_RUNNING`). The publisher keeps
re-grading at the same sha. Marker `run_complete_20261013T134447Z.md` was graded twice at 2248e3baf
(pid 1448887, then pid 1690774), and each pass ran an `-x` suite and then a full depth census. Today's
reconcile-watch log shows runs of 11-13 consecutive `GATE_RUNNING` ticks, each broken by a single
`NOT_ADVANCED` window. So the advance gets about one 5-minute chance an hour. A re-grade at a sha that
was already refused cannot pass, because nothing it reads has changed. It only uses up that window.

**Measured in this invocation's window (18:33 BST, right after pid 1690774 exited):** `origin_reconcile`
ran and refused. 43 of the 46 blocking paths are now provably lossless (twins or carried). The DD pile
that held the 15:36 window is on origin. The advance is held by **3 live paths**, each written about
0.1 h earlier and conflicting with origin: `docs/direction/DIRECTION.yaml` (7 conflicts),
`docs/direction/decisions.jsonl` (1) and `docs/status/SEAT_STRETCH_LOG.md` (1). They are the delivery
seat's direction-record writes. That seat was live at the time (pid 1911763). I moved none of them.

**Proposed mechanism (not built in this tick):** before it launches a gate, the publisher should compare
the shared HEAD with the `graded_sha` of the last refusal recorded for that marker. If they are equal,
it should defer rather than re-grade. The deferral should say why ("refused at <sha>; waiting for HEAD to
move"). That frees the lock for the advance, which is the only thing that can change the verdict. The
control has to prove the deferral can be taken, and also that a moved HEAD is re-graded.

**Expected to clear without it:** once the delivery seat lands those three paths, the next
reconcile window should fast-forward, and the next publish should grade a HEAD that holds 81c129fe8.
Prediction, filed before it is observed: the census test passes at that HEAD.

No second NTFY. The cause is unchanged from `TCpCYvtpTTm3`.
