**Severity:** LATENT · **Lane:** H_harness · **Rank:** backlog, after the current delivery-lane item

# The publish gate tests the WORKTREE but the commit takes the INDEX, so a stale staged blob lands unread

## Class registration

Belongs to `publish_gate_and_wedge`. It is the *fail-open* half of that class rather than the
wedge half: nothing here is stuck, which is exactly the problem — the gate goes green and the
payload lands anyway.

**Filed by the worker seat, 2026-08-27, while doing the EP13 tick. QUEUED, not fixed on sight
(SELF-INTERRUPT DISCIPLINE): the live instance was neutralised in seconds by syncing one path,
the drawn work was EP13, and re-cutting how the publish gate chooses its subject is a design
job, not a tick job.**

## Observed, with evidence

`background/process_run_complete.py` (pid 702464, started 10:21, 64 minutes elapsed at the time
of this reading) held 50 staged paths. Forty-nine were its own payload — `site/data/*`,
`site/state/*`, `docs/state/*`, `docs/status/*`, `docs/reports/ANNUAL_REPORT.md`. The fiftieth was
not payload at all:

```
HEAD blob:     fb9aa3a291b4c116b49622d98ecfd22f78dd9a44
INDEX blob:    286112846c89a14a9074324eccb2568d3696df2a     <- the publish would commit THIS
WORKTREE blob: fb9aa3a291b4c116b49622d98ecfd22f78dd9a44
```

for `tests/tools/test_bill_correctness_addendum_defect4.py`. HEAD and the worktree agree. The
**index alone** carried a different, older blob, and `git diff --cached` showed what that blob
was: a clean revert of the dual-fuel billing-account fix landed the same day by

```
d01f1cb38 28 of 28: the gas-leg inversion was the SPLIT, not either side of it --
          all 18 vanish at the billing account
```

— the comparison moved from the supply point to the billing account, the change that takes 18
inverted gas-leg customer-years to zero. The staged blob restores the supply-point comparison.

## The defect, stated so it can be detected

The gate's subject and the commit's subject are **different trees**.

- The gate is `pytest tests/ -q` (observed running as pid 727869 under the publish). `pytest`
  imports modules **from the working tree**. The worktree held the fixed file, so the gate ran
  the *fixed* test and would go green.
- The commit takes the **index**. The index held the reverted file.

So the reverted test is never the thing the gate executes. It lands green and unread, and HEAD
silently loses a fix that was committed four hours earlier — with a passing gate run as its
evidence. This is the FAIL-OPEN shape from R15, with the twist that the checker is not missing or
malformed: it is simply **pointed at a different subject than the artefact it authorises**.

Note the asymmetry that makes it hard to see. Had the staged blob been *broken* rather than
*stale-but-self-consistent*, nothing would have caught it either — the gate would still have been
reading the worktree copy. The defect is not about this file. Any path that is staged and whose
worktree copy differs is outside the gate's field of view entirely.

## Why this is not the already-filed alarm

`WORKER_FINDING_..._CONSISTENCY_GATE_FAILED_GIT_DASHBOARD_TOTALS_...` and the
`..._UNDECLARED_WORKTREE_S_ACCRETION_...` pair are about a gate that *fires*. This one is about a
gate that **passes correctly on the wrong tree**, and it survives every fix to those.

It is also the mechanism behind the `uncommitted_and_orphaned_work` alarms rather than another
instance of them: this is how a concurrent writer's stale `git add` becomes a committed
regression, which is the reverse direction of "work that never got committed".

`tools/surgical_land` is not vulnerable in this way — its whole design is to gate *the tree the
commit would create*. The publish path does not use it.

## What was done now, and what is owed

**Done, and it is an instance fix only (R10 — this does NOT close the class):**

```
git add tests/tools/test_bill_correctness_addendum_defect4.py
INDEX blob now: fb9aa3a291b4c116b49622d98ecfd22f78dd9a44 == HEAD
```

The path drops out of the payload because it now matches HEAD, so the running publish can commit
its 49 state files without carrying the revert. Reversible: the old blob `286112846` is still in
the object store.

**Owed, and it is the class fix:**

1. The publish gate must run against the tree its commit would create, the way
   `tools/surgical_land` already does — not against whatever the worktree happens to hold.
2. Failing that, a cheap pre-commit assertion with real teeth: **every staged path whose index
   blob differs from its worktree blob is a refusal**, unless the publish itself staged it in
   this run. A publish's payload is written by the publish; a divergent third-party path in its
   index is by construction someone else's half-finished work.
3. R15 proof either way: stage a blob that differs from a green worktree copy and assert the
   gate REFUSES. Without that mutation the repair is unproven, and this finding's whole point is
   that a green gate run proved nothing.
