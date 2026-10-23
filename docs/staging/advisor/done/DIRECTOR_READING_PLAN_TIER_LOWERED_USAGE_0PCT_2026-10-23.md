**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] The plan moved to a lower Max tier; usage reset to 0% on Fri 23 Oct (2026-10-23)

**Type:** usage reading and a change to the budget's size, relayed by the advisor. The director's words, from chat on Fri 23 Oct:

- 06:55 BST: "NB I've moved to a lower tier of max plan. So we may have fewer townen per week. Currently it has reset and is on 0% usage before Monday, so no issue. But we want to measure burn rate and pace accordingly."

## What changed

- **One percentage point is now a smaller amount of work.** The weekly allowance is lower. Your calibration of about USD 26.5 of weighted spend per point (`tools/tick_burn_rate.py`, fitted to his readings of 12–22 Oct) belongs to the old tier and no longer holds. Don't pace from it.
- **The meter reset at the change and reads 0% now.** He says there is "no issue" before Monday, so spend this window on the best work. Do not hold back for Monday.
- **The weekly reset time may have moved with the plan.** Until a reading says otherwise, assume Monday 04:00 BST. If the next reading implies a different reset, say so.

## What to do

1. **Measure the new rate first, from his readings.** Record weighted spend at each reading's timestamp, from 06:55 BST today. Fit USD per point on the new tier as soon as two readings exist. The advisor will relay each reading through this channel and will ask him for one this evening. Put the fitted figure and its band in the stretch log, beside the old one.
2. **Until the fit exists, pace on measured spend, not on the old constant.** Run the normal parallel width. Don't widen further until the first fit shows the headroom. Don't stop or slow to wait for a reading. Keep R1 ("spend more of the week; don't save it") and the reserve of about 6 points at the end of each window.
3. **From the second reading onward, project the week.** At this rate, when does the window hit the reserve? Adjust width to land just short of it at the reset. Report the projection with each relayed reading.
4. **Find what costs the most.** This tier makes cost per landed result matter more. Break down the week's spend by route: worker ticks, seat turns, delivery seat, long jobs, probes. Name the most expensive per landed result, and make one proposal to cut waste there, without making the work shallower (R14: "I'd rather spend the tokens than get shallower work").

— Advisor, relaying the director's reading and his plan change on the director's standing delegation of 15 Oct, with his words quoted above.

## Done

*Worker tick, 2026-10-23 06:20Z.*

- **Step 1, the reading is recorded.** `tools/tick_burn_rate.py` `POINT_READINGS` carries 0% at
  2026-10-23T05:55Z (06:55 BST). A new `TIER_CHANGED_AT` stamp means `usd_per_point` fits only
  readings taken on the current tier. Before this change, the old 12–13 Oct pair would still have
  produced the stale USD 26.6 per point. `--points` now prints "no conversion: fewer than two readings
  on the tier since 2026-10-23T05:55" until the advisor relays a second reading. The control in
  `tests/tools/test_tick_burn_rate.py` reds when the tier filter is removed (mutation run, 1 failed).
- **Weighted spend at the reading's stamp is 0 by construction. By 06:18Z it was USD 3.78** (all
  transcripts and subagents). That gives the next reading its numerator.
- **Step 2, pacing.** No fit exists yet. Width is unchanged and nothing is held for Monday.
- **Step 3, projection.** This is owed from the second reading. It cannot be made from one reading.
- **Step 4, the costliest route per landed result.** Measured over the last 7 days, on the old tier,
  with `python3 -m tools.tick_burn_rate --days 7`:
  - worker_tick: USD 485.04 over 188 turns, 79% landed, so about USD 3.27 per landing.
  - seat_executor: USD 392.68 over 135 turns, 84% landed, so about USD 3.46 per landing.
  - delivery_seat: USD 70.34 over 41 orientations. It does not land.
  - One "other" session cost USD 34.68 on its own, with 81.6M cache-read tokens.

  Cache reads dominate every route. The median tick reads 4.1M cached tokens against 134k fresh. Per
  landing, the seat executor is the costliest route.

  **Proposal.** Find what makes an executor turn read 1.1M more cached tokens than a worker tick at
  the median (5.18M against 4.09M). The likely cause is turn length, meaning more tool round-trips
  that each resend the context, rather than prompt size. Cut round-trips, not depth. This is to be
  measured before any change is made, per R14.
