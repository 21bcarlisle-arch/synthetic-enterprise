**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `OPS6_scoped_publish_path_suite`

# A re-driven publish keeps its refusal tag, so the frontier under-reads it

**Found by** the worker on 19 Oct 2026, while building the re-arm for
`done/SEAT_FINDING_A_REFUSED_PUBLISH_WHOSE_RED_IS_LATER_ANSWERED_IS_NEVER_RE_ATTEMPTED_2026-10-19.md`.

## What is wrong

The 19 Oct hand re-drive, 2a195224b, landed `docs/staging/done/run_complete_20261019T033010Z.md`
with its 06:35Z `<!-- publish-outcome: did-not-land` tag still in it.
`_stamp_publish_outcome_on_archived_marker` writes nothing on a landed outcome, and nothing
removes an earlier tag. `staging_archive_policy.publish_did_not_land` therefore reads True, and
`background_worker._newest_published_stamp` skips the run. The supersession frontier now names an
older run than the one on origin.

**Consequence today:** leftover markers stamped between the two runs are not retired as
superseded. Ordering is newest-first, so they cannot publish over the 19 Oct figures. They do cost
a publisher cycle each. A re-arm landing (`refused_marker_to_rearm`) would leave the same stale
tag. The re-arm's landed-since guard is what stops it re-opening such a marker.

**Smallest fix, not built:** on a landed outcome for a marker that already carries the tag, the
publisher appends a landed counter-tag before the commit, and `publish_did_not_land` reads the
last outcome tag. Whether it is landed or not must be checked against the R15 argument in that
reader's docstring.

## Carried from the source finding: the delivery leg's cut-off refusal

`origin_reconcile` refused the re-driven publish's merge (`REFUSED_GATE`) in the shared tree,
and its `detail` string is truncated before the red is named. The same merge passed in an origin
worktree (f8f3d0fd5). A re-armed publish can stall on this leg in the same way.
