# What I expect the three-point probe to say, written before it is launched

**Filed 2026-08-29 07:5x BST, before `tools.settlement_ceiling_probe --budgets 1200 2000 2800
--publish-interval 3600 --time-share 0.9` is started.** It is committed ahead of the run so that
its commit provably precedes the result, which is the only thing that makes it a prediction rather
than a description. The run is specified in §6 of `SETTLEMENT_CEILING_REMEASURED_2026-08-29.md`.

The last attempt at this recorded its prediction *after* the fact and got both halves wrong
(§"What I got wrong"). This one goes in first, and is graded beside the result whichever way it
falls.

---

## The two blockers found before the run, and what they say about the existing points

Neither was in the specification; both stopped the run.

1. **`simulation/settlement_clocks.py` was untracked**, and `tools/run_annual_report.py` imports
   it to refuse a run whose figures do not reconcile. So **both existing probe points were taken
   through a control that exists on one box** and no clone has. Landed this morning.

2. **The producer guard counted this agent as the producer.** `a_run_is_in_flight()` ran
   `pgrep -f tools.run_annual_report`; `pgrep -f` matches the whole command line; the autonomous
   worker runs as `claude -p <prompt>` and the prompt commissioning this measurement quotes
   `tools.run_annual_report._run_and_extract`. Verified live — pgrep returned this session's own
   pid. Every budget would have been skipped as "producer in flight", permanently, and the only
   escape was `--force`, which switches the guard off altogether. **A fail-closed guard that
   cannot clear is not conservative; it is a guard whose only remaining use is being bypassed.**

Both are landed before the measurement rather than noted after it.

---

## The premise moved under the direction, and it moved toward the ceiling mattering MORE

The direction states the measurement as *"386 funnel wins, 46 booked, 340 refused"*, with the
settlement engine *"binding in nine years of ten"*. Read live from
`docs/observability/book_growth_campaign.json` at filing, both halves are now different:

| | direction | live record, 2026-08-29 |
|---|---|---|
| funnel wins | 386 | **505** |
| booked | 46 | **90** |
| refused by the settlement budget | 340 | **415** |
| years reporting `binding == settlement_engine` | 9 of 10 | **0 of 10** |

Two changes landed today, from another lane, between the direction being written and this run.
The allocation fix spread the same 1,200 across ten years instead of two. And
`net_new_acquisition.py:663` stopped overwriting `binding` with `settlement_engine`, on the
argument that *"a uniform sample does not stop any year; it scales the whole book"* — the
artefact is now reported as `settlement_sample_rate` (0.1789, identical in all ten years) plus a
per-row `wins_refused_by_settlement_budget`.

**That argument is right about stopping and it should not be read as the ceiling having relaxed.**
It refuses 415 of 505 — **82% of every year's wins, uniformly** — where the direction described
340 of 386. The engine's grip got tighter and its *label* disappeared at the same time, which is
worth saying plainly because those two facts pull a reader in opposite directions.

**One thing I checked and am NOT filing as a defect.** `couple_pb3_book_growth.MACHINE_BINDINGS`
excludes `settlement_engine` years from the belief-vs-truth gap, and now matches zero rows — an
exclusion branch with no producer, which is normally this project's "PASS branch unreachable"
shape. Here it is an EQUIVALENCE, not a defect: `_realised_rate` was moved to `funnel_wins` the
same day, so PB3's truth is measured before the sample the machine applies and needs no exclusion.
Recorded because a mutation that cannot fire must be established as one or the other, and this one
is the flattering answer *and* the correct one.

## The numbers I expect

Anchor: the 2026-08-29 clean point — budget 1,200, **1,018.7 s**, **4,193 MB**. The campaign record
on disk at filing reads `customer_years_all_wins_would_cost = 2393.0`, `customer_years_committed =
1194.9`, `wins = 90`, `settlement_sample_rate = 0.1789` (post-allocation-fix). Guest read live:
`total_mb` 24,032.1, `available_mb` 13,221.1, `oom_kills_total` 161.

**2,393 is the number that matters** — it is what settling every funnel win would cost, so it is
the demand ceiling above which no budget buys anything. The specified top budget of 2,800 is above
it, which is deliberate: a point that refuses nothing is how the tool proves demand rather than
the box is what binds.

| | prediction | why |
|---|---|---|
| **the ceiling moves, upward** | yes, to roughly **2,000–2,400** | not to 2,800 |
| **which bound binds** | **memory, not time** | the falsifiable half |
| point 3 commits | **≈2,393, not 2,800** | demand, not ceiling |
| point 3 refuses | **0 wins** | so it reports `funnel_supply_customer_years` |
| cost at 2,800 | **≈1,600–1,800 s, ≈6,000–6,500 MB** | ≈40% of the run is window-fixed |

**Why memory and not time.** A chosen 3,600 s interval at `--time-share 0.9` allows 3,240 s. I
predict no point costs more than about 1,800 s, so the time bound does not bind at any budget in
this range and the answer is set by `--rss-share` against the 24,032 MB guest. That is the outcome
§3 argues *should* obtain, and it is the specific thing to check: if time binds instead, either my
cost model is wrong or the circularity §3 describes is doing work I have not seen.

**Why 2,800 buys nothing.** 2,393.0 customer-years is the campaign's entire demand. A ceiling above
it refuses nothing. So the useful answer is bounded above by demand, not by the box — and if the
memory bound lands above 2,393, **the correct ceiling is the demand figure and the honest statement
is that the engine has stopped binding at all.**

**What would refute the whole premise.** If the 2,000 point commits ~1,200 and refuses the same
count as the 1,200 point, the funnel and not the ceiling is what bounds this range, and "the
ceiling is real" is the answer. §4 records that this exact reading was produced once already by a
contaminated point, so it is believed only from a point carrying `clean: true`.

**Prediction on cleanliness.** With the producer held down and the guard repaired, I expect three
clean points. I predicted three clean points last time and got one, for a reason I had in front of
me and did not apply. What is different now is not confidence: it is that the producer is held by a
flag for the duration rather than observed to be absent once at the start.

---

## The distinction the result must not blur

Whatever comes back, the published net figure moving is **not** evidence that the method works. The
ceiling is an engineering artefact of this machine with no counterpart in the world; lifting it
removes an artefact and lets more of the book the method already won be settled. Those are two
different claims and a reader will merge them unless the report separates them by name.

The ladder's per-rung populations must be **re-run, not projected** from win counts: rung 2.0 has
no book after 2019, so the two mechanisms compose in a proportion I do not know.
