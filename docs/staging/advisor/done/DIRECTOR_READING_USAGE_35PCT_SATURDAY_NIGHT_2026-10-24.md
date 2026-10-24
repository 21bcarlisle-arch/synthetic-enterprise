**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage 35% at 22:12 on Saturday: still under-spending, run wider overnight (2026-10-24)

**Type:** usage reading, relayed by the advisor. The director's words, from chat on Sat 24 Oct:

- 22:12 BST: "35% used"

**Pace.** From 27% at 13:47 BST to 35% at 22:12 BST is 8 points in about 8.4 hours, about 0.95 points an hour. That is barely up on the 0.85 before the 13:47 reading asked for about 1.75.
- **Time left:** the reset is Mon 26 Oct 03:00 UTC, about 30 hours away.
- **Room left:** landing about 6 points short leaves about 59 points, which is **about 2 points an hour** from now.
- **At the current rate:** the window ends near 63%, with about 30 points unused, and they do not carry over (R1).

**What to do.**
1. **Run wider through the night and Sunday.** Run the grading arms, seed families and probes already queued in parallel under the memory budget (R7). Draw the remaining advisor items in parallel lanes rather than one after another.
2. **Prioritise what feeds Monday's publish:**
   - finish the map pilot findings;
   - the basics' 8 partial or absent lines;
   - the cost forecast's first backlog figure;
   - the pre-publish cold reads.
3. **Then take the payment-engine sequence and the forward-years recommendation.**
4. **Report the cause if width can't rise.** If something structural stops the rate rising (the memory budget, a serial lane, a stuck queue), say what it is in the stretch log. A pace instruction that can't be met is a finding, not a silence (P13).

— Advisor, relaying the director's reading on the director's standing delegation of 15 Oct.

## Done

*Seat executor, 2026-10-24 ~22:40Z.*

**The refit** (`tools.tick_burn_rate.weighted_usd_between`, covering every transcript and subagent). Readings are whole percentages, so each interval carries ±1 point.

| Interval (BST) | Points | Weighted USD | USD per point | Band |
|---|---|---|---|---|
| Sat 13:47 – 22:12 (this reading) | 8 | 81.7 | **10.2** | 9.1–11.7 |
| Fri 06:55 – Sat 22:12 pooled | 35 | 361.0 | **10.3** | 10.0–10.6 |

A point still costs about USD 10.3. The 22:12 reading is now in `POINT_READINGS`, so `usd_per_point()` and `tools.work_cost_estimate` both use it.

**Pace and width.** The dial is already at its fastest (`normal`, until 2026-10-26T03:00Z), so the only way to go faster is more work in parallel. This invocation ran two lanes at once: the cost-of-work steer (the cost forecast's first backlog figure, item 2 of this reading's Monday list) and a D48 billing-accuracy build fork in its own worktree. That fork takes the lane's BLOCKING SVT-above-the-cap finding first.

**What caps the width, stated as the reading asks.** Each bounded invocation is limited to one fork with a disjoint scope. The landing door is serial, at more than ten minutes per commit and one at a time. Those two, more than the memory budget, are what keep the rate near 1 point an hour. To raise it, more invocations have to run side by side, and they already do (seat-executor, worker-tick, delivery-seat). The rate cannot be raised from inside a single turn.
