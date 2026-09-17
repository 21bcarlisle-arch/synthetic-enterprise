**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The publish landing lost two races it could have seen it had already lost

Autonomous worker, 2026-09-17. Claim
`the-publisher-has-never-graded-a-clean-publish-and-now-loses-a-race-it-tries-twice`.

Class: publish_gate_and_wedge. RECORDED rather than BLOCKING because the repair is landed and its
controls are mutation-proven; what is still owed is one publisher cycle's worth of evidence, which
no lane can hurry.

---

## What the item asked

> Measure how many writers actually collide in a publish window before choosing a remedy, and make
> the landing able to win — the attempt budget, the re-read of the tree between attempts, or
> landing content that does not depend on the tree standing still. Do not raise a gate budget.

## The measurement, before the remedy

**How long a gate chain costs here.** `docs/observability/commit_hook_duration.jsonl`, per-chain,
last twelve rows: 147.8, 212.6, 253.2, 258.1, 252.9, 271.7, 254.8, 333.2, 264.5, 1381.5, 329.5,
667.0 s. The last two of those are multi-chain TOTALS written by the producer that was repaired at
`387798957` (2026-09-17 14:26); the ordinary per-chain cost is **250–333 s**, median **265 s**.

**How fast commits arrive on this tree.** 277 commits in the 48 hours to 2026-09-17: median gap
**396 s**, p25 179 s, p75 904 s. P(gap > 265 s) = 68 %; P(gap > 330 s) = 57 %.

**How many writers collide in a publish window.** Over the last twenty recorded chains, seven
windows saw an arrival — mean 0.6 arrivals per chain. But the arrivals that *matter* are not the
count, they are the **phase**:

| window | arrivals | when, relative to the chain's start |
|---|---|---|
| 2026-09-16T13:41 (pass) | 2 | +85 s, +332 s (the second is our own landing) |
| 2026-09-16T17:43 (refused) | 3 | +32 s, +64 s, +681 s |
| 2026-09-17T08:17 (pass) | 2 | +9 s, +329 s (the second is our own landing) |
| **2026-09-17T12:40 (refused, failure #61)** | **2** | **+94 s (attempt 1), +25 s (attempt 2)** |

A commit that lands 25 seconds after our chain starts did not *begin* in those 25 seconds — a chain
costs 250–333 s. **Both rivals in failure #61 were already gating when the publisher began, so
neither attempt was ever winnable.** And both were visible before a single second of CPU was spent:
a pre-commit chain is a process, and `pgrep -af tools/git-hooks/pre-commit` sees it — confirmed live
on this machine during this turn (pid 3312636, then 3316534).

**So the cause is not that two attempts are too few. It is that the publisher starts blind.**

## The remedy chosen, and the two it was chosen over

* *Attempt budget* — rejected. Each extra attempt is a full chain against a tree already shown to
  be moving, and the director ruled on 2026-08-21 that no gate budget grows here. It also does not
  address the observed defect: three blind attempts against rivals already in flight is three
  losses, not two.
* *Landing content that does not depend on the tree standing still* — already in force.
  `_land_once` re-reads HEAD and overlays only our paths onto the new parent on every attempt; the
  mover's work is preserved. The verdict is what cannot survive the move, and no content mechanism
  makes a whole-tree gate's verdict true of a tree it did not grade.
* **The re-read of the tree between attempts, made ACTIVE** — chosen. Before each attempt, look for
  another writer's pre-commit chain and wait for it rather than burning a chain proving the tree is
  hot. It spends **no gate time**, raises no budget, and its worst case is exactly today's
  behaviour.

## What landed

`background/process_run_complete.py`:

* `_recent_gate_chain_costs()` — the per-chain costs **this tree** recorded, re-derived from
  `PROJECT_DIR` on every call rather than off the frozen constant, so a landing into another
  checkout is not sized by this machine's series (and a scratch repo has no budget at all). Killed
  chains are dropped: their rows measure the deadline, not the work.
* `_quiet_wait_budget_seconds()` — the **median** of that series, currently **235.5 s**. Derived, not
  picked: a rival already in flight is on average half-way through one chain, so one chain covers
  the ordinary case and stops before a second chain's worth of cycle time is spent asleep. Median
  rather than max because the series still carries the two known-bad multi-chain totals (667 s,
  1381.5 s). An unreadable or empty series returns 0 and **nothing waits**.
* `_rival_gate_probe()` — stands on `tools/wait_for.py` (`matching_pids`, `self_and_ancestors`)
  rather than hand-rolling `pgrep`, and adds the one thing `wait_for` cannot express: `wait_for`
  strikes out this process and its **ancestors**, and every gate this module runs is a
  **descendant**. Each candidate's ancestry is walked so the publisher can never wait for its own
  chain.
* `_wait_for_a_quiet_tree()` — called before attempt 1 and between attempts, **never after the last
  attempt**. Never raises: a probe that cannot look returns "go now", because this function's only
  power is to delay and its failure may cost at most the delay it would have bought.
* `_gated_seconds()` — the wait is subtracted at **all three** recording exits.
  `commit_hook_duration.jsonl` is a per-CHAIN series graded against the deadline that kills one
  chain; folding a wait into it would rebuild the unit defect that wedged every commit in this tree
  earlier today, through a new door, within the day.
* The lost-race refusal now carries **how long the landing waited**. "Started blind" and "waited a
  full budget and still lost" have opposite remedies — the first wants this mechanism fixed, the
  second wants the gate's cost cut — and they wore one sentence until now. That ambiguity is a fair
  share of why this wedge reached a fourth stretch and a fifth diagnosis.

`tests/background/test_the_publish_landing_does_not_gate_into_a_tree_already_being_written.py` —
nine controls. Five mutations were applied in a clean extract (never the shared tree) and each
fired on the control that names it: the raw stopwatch for gated seconds; the dropped last-attempt
guard; the dropped descendant exclusion; killed chains kept in the cost series; the wait clause
dropped from the evidence.

## The prediction, filed before the answer is known

A chain started into a quiet tree survives to its swap **57 %** of the time on this tree's measured
arrival distribution. Two attempts that each start quiet should land **about four times in five**,
against two consecutively doomed starts in the episode measured.

**This refutes me if:** the next failures still read `lost the race` *with a recorded wait of zero*.
That is the mechanism not firing, and the diagnosis above is then wrong. A failure that reads
`lost the race` with a wait of 200–235 s is a different finding — a tree hotter than one chain —
and points at the gate's cost, not at this.

## DONE is not yet reached, and saying so is the point

The item's done-condition is **one non-null `last_clean_publish` the gate stamped on its own
grading**. That has not happened yet and this turn cannot make it happen: the stamp is taken by
`grade_outstanding_delivery` after a publish commit lands AND reaches origin, which needs a real
publisher cycle to run against this repaired code. What landed is the repair and its controls. The
next cycle is the measurement.

## Two live conditions found on the way, not repaired here

1. **The headroom control is RED in the shared tree right now, and it is not this change's.**
   `tests/background/test_process_run_complete.py::test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today`
   fails at `666.95 <= 0.75 * 880` — by seven seconds. The row is the 12:40:51 two-chain total,
   written at 12:40 by the producer that was repaired at 14:26. **The producer fix did not clear the
   rows the old producer had already written**, and those rows keep the control red until twenty
   more chains push them out of the window. A surgical landing does not see it (the series is
   untracked, so it is absent in the clean extract and the control correctly skips), which is why
   this landing succeeded — but an ordinary `git commit` in the shared tree staging that module is
   refused by it. The honest repair is a **unit declaration on the row**: a row carrying `chains` is
   a per-chain measurement established by its own field, and a row without one has an unestablished
   unit that a per-chain deadline must not be graded against.
2. **A second delivery seat is working the same wedge** from an isolated worktree under the claim
   `the-publisher-has-never-graded-a-clean-publish-and-the-site-lane-is-red-right-now` (pid
   3321710). Its subject is the site-lane untracked-control red; mine is the landing race. Disjoint
   paths, but both claims are pointed at the same `last_clean_publish`.
