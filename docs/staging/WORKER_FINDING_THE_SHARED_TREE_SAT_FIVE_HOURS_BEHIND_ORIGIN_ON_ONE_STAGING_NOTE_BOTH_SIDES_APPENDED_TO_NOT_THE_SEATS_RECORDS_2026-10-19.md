**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Triage:** `a-landing-carries-a-stale-direction-record`

# The shared tree sat five hours behind origin because of one staging note both sides appended to, not because of the seat's records

*Worker, 2026-10-19, drawn as `the-shared-checkout-reaches-origin-after-the-ad8afadc5-run`. Read from
`docs/observability/reconcile-watch-log.md` (09:24Z-14:28Z), `background/origin_reconcile.py`
(`_carry_plan`, `_merge_onto_origin`) and `background/delivery_seat.py` (`commit_direction`,
`settle_shared_copies`).*

## Correction to the drawn item, beside its claim

The 14:22Z record says the shared tree was refused by 13 paths, "including the seat's own
DIRECTION.yaml, decisions.jsonl and SEAT_STRETCH_LOG.md", and files the cause under
`a-landing-carries-a-stale-direction-record`. **The seat's records held nothing.** Every
`NOT_ADVANCED` line from 09:43Z to 12:43Z carries the advance's own verdict, and it is the same
each time: `advance: 1 of N blocking path(s) could NOT be proven lossless or carried`, held by one
path, N rising from 1 to 8 as other paths dirtied around it. The other N-1, the seat's three records
among them, were proven lossless or carriable and would have cleared. The 13-path list is the
census of what is dirty here and changed on origin, not of what holds the advance. Read the
`Held by:` clause, not the list. From 12:48Z the publish run was going and the advance was not
attempted.

## What held it

`docs/staging/WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_AND_C35_CHARGED_IT_TWO_RISES_FOR_ONE_BENEFIT_2026-10-18.md`.

1. 05:13Z: a lane appended `## 7. Item 3, netting across legs: built, default off` (26 lines) to the
   shared copy.
2. 07:54Z: that build landed as `b529875b1` (`company/billing/dd_review.py`,
   `DecisionPolicy.dd_review_offsets_dual_fuel_legs`). The landing did not carry the note's §7, so
   the 26 lines stayed in the shared tree only.
3. 09:30Z: the seat's `230b59831` appended a `**Book note**` paragraph to the same note on origin,
   at the same end of file.
4. Both sides now add at EOF of the same base. `git merge-file` calls that one conflict.
   `_carry_plan` refuses any conflict ("live work, holds the advance untouched"). The note was
   4.8 h old, under the 48 h abandonment line, so it held the whole fast-forward. Nothing else in
   the reconciler can move it, and no page names the lane.

The seat's records do dirty this tree after every orientation. The seat writes them here and lands
them from `/var/tmp/se-direction-seat`, so they read dirty against a lagging HEAD until the tree
advances. But they are origin's twins once the landing is in (`settle_shared_copies` rewrites the
two append-only files, and DIRECTION.yaml is landed from these exact bytes). The advance clears
twins. They block only in the minutes between an orientation's write and its landing.

## The smallest fix

In `background/origin_reconcile._carry_plan`, carry a conflict when **both** sides only append to
HEAD's copy. That means HEAD's bytes are a prefix of the copy here and of origin's copy. Carry it
as origin's copy followed by the local tail. No line is lost. Order is the only judgement made, and
origin first is what a later landing would produce anyway. Every other conflict still holds the
advance, as now. The control: a fixture where the base is a prefix of both sides is carried, with
both tails present. A control over the whole partition checks that a mid-file conflict on that
fixture still holds. A mutation that drops the prefix test must red the second leg.

The other half is a sibling of the orphaned-work class. A landing that builds a capability and
leaves its own staging note's new section in the shared tree strands it. That belongs to
`docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`, not here.

## This instance

Cleared by hand on 2026-10-19. The note's §7 was merged after origin's Book note and landed. The
three W2_36 lines unlanded since 10-17 in
`docs/market_research/read_access_and_theft_duties.md` were landed the same way.
`simulation/meter_reads.py` on origin holds smart mode as a state, so those lines are true. The two
2026-10-17 archive copies in `docs/staging/done/` were removed. Each was HEAD's copy of a finding
that origin has since extended at the root (`c43df1237`). The generated `site/data/delivery.json`
was restored from HEAD.
