# PREREGISTRATION — what stands between the cleared site-lane red and a non-null `last_clean_publish`

**Severity:** RECORDED
**Lane:** Lane 0 delivery
**Written:** 2026-09-17 13:2x BST, BEFORE driving any publish
**Claim:** `the-publisher-has-never-graded-a-clean-publish-and-the-site-lane-is-red-right-now`

---

## Why this is written before the measurement and not after

The drawn item names ONE named cause (the site-lane red) and asks for a non-null
`last_clean_publish`. The gate's own state file records `episode_failures: 59`, so the prior
that one cause was the whole wedge is weak. A prediction filed after the publish runs is not a
prediction, and the item explicitly warns that "a fifth, sharper cause is not progress". So the
honest thing is to say now, in order, what I expect to stand in the way — and to be refutable
about how many of them there are.

## What is already established (not predictions — measured this turn)

1. The three controls existed in no commit on any ref. `git log --all --` was empty for each.
   They were on disk in the shared tree from 12:06–12:12 today, from a prior turn that built and
   never landed them.
2. They are not vacuous. All 8 legs pass against a real chromium in the checkout that has
   `node_modules`, including the positive leg. R15 both ways in this isolated worktree: RED on
   `site/test_the_site_lane_runs_no_untracked_control.py` with the files present and untracked,
   GREEN once staged.
3. They are landed as `7f40070a6` and promoted to `origin/main`, with
   `docs/design/WHAT_THE_VM_DOORS_GRADE.md` which all three cite by path.
4. **The landing is currently INERT against the gate.** The shared tree
   `/home/rich/synthetic-enterprise` is at `08238c7be` — one commit AHEAD of origin and one
   BEHIND — and `git ls-files` there returns NOTHING for the four landed paths. The gate grades
   that tree. So at this instant the site-lane red is still live where it matters, and clearing
   it required a landing I have made plus a reconciliation I have not.

## The predictions

**P1 — the fork, not the site-lane red, is the cause a publish names next.**
Driving a publish against the shared tree as it stands now records a cause about divergence
(`behind_origin` or its divergence sibling), NOT a `gate_refusal` naming
`test_the_site_lane_runs_no_untracked_control.py`.
*Refuted if:* the next recorded failure still names the site-lane control.

**P2 — the reconciler closes the fork without judgement.**
`background/origin_reconcile.py` merges `08238c7be` and `7f40070a6` cleanly, because the two
commits touch disjoint paths (mine: `site/` + one design doc; the other lane's: the delivery-lane
draw ledger and `tests/background/`).
*Refuted if:* it refuses naming a contested path.

**P3 — the one that matters, and the one I expect to be wrong about.**
Once the shared tree carries both commits, a publish STILL does not stamp a non-null
`last_clean_publish` on its first attempt: at least one further independent cause exists.
I put this at **more likely than not**, because 59 failures in a 7.3-day episode is not the
signature of a single blocker, and because the gate's own `red_census: fail_fast_only` means it
stops at the first cause and has never enumerated the rest.
*Refuted if:* the first publish after reconciliation stamps `last_clean_publish`. That refutation
would be the good outcome and I would rather be wrong here.

**P4 — what I will NOT count as progress.**
If P3 holds, naming the next cause is a finding, not a delivery. The item says so and it is
right. The test of this turn is a timestamp in `last_clean_publish`, or an honest statement of
exactly which causes remain and which of them this turn removed — never a sharper description of
the same wedge.

## What "done" means for this turn

One non-null `last_clean_publish` the gate stamped on its own grading. Failing that: the
site-lane red cleared **in the tree the gate actually reads** (not merely on origin), the fork
closed, and the remaining causes enumerated rather than counted.
