# The hook chain is GROWING, not stepping, and the room closes in eleven days

**Date:** 2026-09-17
**Lane:** H_harness (drawn as a Lane 0 delivery-seat direction — "fit the hook-chain growth
series because the deadline's room halved in a fortnight and nothing watches it")
**Subject:** `docs/observability/commit_hook_duration.jsonl`; `background/hook_chain_room_watch.py`
(new); `background/daily_self_note.py`
**Severity:** LATENT — nothing is red today. The whole content of this finding is that something
will be, on a date, unless the trend is refuted; a forecast is latent by definition and saying
otherwise would make "blocking" mean "worrying".

---

## The question, and why it was open

`bfbc2b4e9` re-measured the commit hook chain 134 → 333 seconds and explicitly REFUSED to call
that a trend: *"I have not established whether that is a trend or a step and the finding says
so."* Two readings are not a trend. The distinction is not academic — this series has a **proven**
step in it (2026-08-31, 392.6s at 16:35 UTC to 72.7s at 19:28 UTC, a 5.4x drop that then held for
ten days), so "it stepped and will hold" was a live hypothesis with precedent.

It matters because the committed headroom floor rises with the chain **by construction**:
`COMMIT_DEADLINE_HEADROOM * MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17` = 1.25 × 333 = 416s.
The ceiling above it is `PUBLISH_PATH_ALLOWANCE_SECONDS` = 900s, which the director ruled on
2026-08-21 may not grow. The room between them went 732s → 484s in a fortnight. If that is
growth, the two controls intersect emptily a third time; if it is a step, nothing more happens.

## The answer: GROWTH, on four independent counts

Population: the 185 gradeable real-chain rows (bounded by their own ceiling, ≥10s), and for the
fits the 89 of them after the 2026-08-31 step, excluding `b55667741` whose 666.95s is two chains.

**1. A log-linear growth model beats a single step decisively.** BIC over the 89 post-step rows:

| model | params | BIC |
|---|---|---|
| constant | 1 | −172.6 |
| **exponential growth** (0.0611/day) | 2 | **−249.0** |
| best single step (108s → 220s at 09-09) | 3 | −227.2 |

A 22-unit BIC gap is decisive by any convention. On daily medians (n=14, which removes the
within-day clustering entirely): growth −44.2, best step −37.7, constant −22.3.

**2. The growth is present with no data gap to straddle.** The series has a hole from 09-10 to
09-15, and "a step hidden in the gap" would explain the whole move. It does not: fitting
**09-01 to 09-10 alone**, with the step day itself excluded, gives a slope of **+0.0384/day
(×1.31 per week), permutation p = 0.0003** over 20,000 shuffles. A step across the gap cannot
produce a slope measured entirely before the gap.

**3. The best two-step model is a staircase approximating a ramp.** It ties growth on BIC
(−249.3 vs −249.0) while spending five parameters to do it, and its three levels — 102s → 142s →
268s — are themselves monotone increasing. That is not a regime identification.

**4. It does not look like the step this series has already shown.** 2026-08-31 was one interval,
5.4x, then ±13% flat for ten days. The current move is monotone across every daily median from
09-01 to 09-17 bar two, over seventeen days.

**Rate: 0.0611/day, 95% CI 0.0506–0.0717 — ×1.59 per week, doubling every 11.3 days.**

### The prediction, filed before its answer is known

On the fit above, per-chain cost reaches:

| wall | seconds/chain | central | fast end of CI | slow end |
|---|---|---|---|---|
| the staleness leg (`worst > 0.75 × 880`) | 660 | 2026-10-03 | 2026-09-30 | 2026-10-06 |
| the live headroom leg (`1.25 × worst > 880`) | 704 | 2026-10-04 | 2026-10-01 | 2026-10-07 |
| **the empty intersection** (`1.25 × chain > 900`) | **720** | **2026-10-04** | 2026-10-02 | 2026-10-08 |

The watch below, anchored on the more conservative 14-day window and on the fit's level at now
(295s), reports **11 days**. Either this is refuted by 2026-10-08 or the tree wedges a third time.
I have not attributed the growth to any commit and have not tried: the number describes the
machine, and the direction asked whether it is real, not why.

## What I did about it, and what I decided NOT to do

**Decision: the floor does need a watcher, and the thing to watch is NOT the floor.** The floor is
a committed constant; it only moves when a human re-measures it. The obvious control — `room > 0`
— is worthless: it is keyed to today's answer and goes red at the exact moment the tree wedges,
which is the event it exists to prevent. The quantity with value in it is **how much warning is
left**.

**Decision: a watcher, not a gate.** A commit-blocking control here would red every lane to report
that a comment needs re-dating — the exact shape that caused the 2026-09-04 outage. This is a
`note_line()` on the daily self-note plus an R5 transition alarm, so it reaches the seat and the
director without refusing anything.

`background/hook_chain_room_watch.py`: fits log(duration) over a 14-day window of gradeable
real-chain rows, and reports the days until `1.25 × chain` exceeds the allowance.

* **The wall is the one that cannot move.** Two deadline-derived walls bite sooner (704s, 660s)
  and both are buyable by raising 880 — as far as 900 and no further. Past 720s/chain no deadline
  satisfies both controls at any price, because the allowance is the director's. The line names
  all three so a green is never read as "nothing reds first".
* **Fourteen days is the one real judgement**, and it is measured, not picked: at 21 and 28 days
  the window straddles the 08-31 step and the fitted slope goes NEGATIVE — the watch would report
  infinite room while the chain doubles every eleven days. At 7 days, n=11 and the fitted rate is
  ×31 per week. At 14 days n=51 and the rate agrees with the whole post-step regime.
* **The tight band is 14 days because that is how long the last remedy actually took** — the
  staleness refusal named the re-measurement on 2026-09-04 and it landed on 2026-09-17. Warning
  shorter than the remedy has ever taken is not warning.
* **It can fail in both directions.** A flat series reports an infinite lead and renders green; an
  unmeasurable one returns `None` and renders RED, never a fabricated lead. The band partition is
  asserted as a whole before any leg, because a `band()` returning one constant would pass most
  per-leg assertions.

**Twelve mutations, all verified to move the bytes, all fire. Two did not on their first form and
both are recorded beside the leg they belong to rather than quietly rewritten:**

* `empty_intersection_seconds() → return 720.0` **fired nothing**: the leg asserted equality with
  `ALLOWANCE / HEADROOM`, which IS 720.0 today, so a literal satisfied it. A missing test, not an
  equivalence — the assertion was keyed to today's answer. It now moves a constant and checks the
  wall follows.
* `drop the window clause` **fired nothing**: the fixture's old rows were 1600s against an 880s
  ceiling, so the *ceiling* predicate excluded them whether or not the clause under test ran. The
  leg was graded by a filter it was not about. The old regime is 700s now.

## What I found on the way, and did not do

**`bfbc2b4e9` is an ancestor of HEAD and the constant its message is named for is in no commit.**
`git log --all -S EARLY_EXIT_CEILING_SECONDS_2026_09_17` returns nothing on any ref; HEAD's blob
of `process_run_complete.py` carries `REAL_CHAIN_FLOOR_SECONDS_2026_09_17 = 10.0`. The rename
lives only in another lane's **uncommitted** working copy of that file (mtime 18:45 UTC today),
along with ~150 lines of in-place edits to it and ~570 to its test file. So the tree the gate
grades and the tree this machine runs on disagree about the name of one constant, and no single
import satisfies both. The new module resolves either spelling and **raises** if neither exists,
with the deletion condition written on it; that is an accommodation with a date and an end, not a
fallback.

**I did not unify the row filter with the live control**, and that is owed. `row_is_bounded_by_its_
ceiling` is now production code in the watch, and `_hook_chain_window` in
`tests/background/test_process_run_complete.py` still carries its own inline copy of the same
clause — one rule, two implementations, this project's most expensive recurring shape. I wrote the
unification, measured that the file is being edited in place by another lane right now, and
**reverted my own hunks** rather than carry their rename inside my commit. It is a two-line edit
for whoever next finds that file quiet, or for `surgical_land --content`.

## Still owed

1. The unification above.
2. **Nothing has re-run the 2026-08-31 attribution question at the new scale.** The chain has
   doubled twice; six commits landed in the step window and at least two removed exactly the shape
   that would cause it. If the same class of defect is what is growing now, the attribution is the
   repair and the watcher is only the alarm.
3. The `chains` field (landed `8cb9a6b96`) is on 0 of 195 rows. Until twenty rows carry it the
   staleness leg cannot fire at all, and this forecast is the only thing watching that wall.
