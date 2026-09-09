**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — land the nine-seed floor through the witness path and grade its pre-registration beside it) · **Class:** controls_that_cannot_fail

# A Lane 0 item whose stated work is waiting on its own six-hour run is swept at 100 minutes, by construction

**Filed 2026-09-09T15:30Z, from the turn it happened to.** Both of this turn's commits reached
`origin/main`; the second one's paths are bound to nothing, and this document is why.

---

## What happened, in the order it happened

| time | event |
|---|---|
| ~14:16Z | item drawn. Its WORK section opens *"The run is LIVE and will finish inside this stretch — **do not relaunch it**. PID 704091 … Wait on it with `tools/wait_for.py --pid 704091`"* |
| 14:47Z | first increment landed `58b6cec1f`, promoted, **bound 1 path** — the binding worked |
| 14:47–15:17Z | waiting on PID 704091, which had already been running 5h20m |
| 15:17Z | the run finishes and writes its artefact |
| 15:25Z | second landing `8d7693d92` — the floor, the feed, the grading — 5 paths |
| 15:26Z | promoted to `origin/main` and **bound NOTHING**: *"it is NOT CLAIMED … the claim was swept and you are working unclaimed"* |

The claim store now holds two other seats' claims where mine was. Nothing was lost — the commits are
on origin — but the lane cannot see the five paths that carry the actual deliverable.

## The mechanism, and it is not a race

The item's own hand-out states the sweep interval: *"the claim is swept back into the pool in 100
minutes however much you landed."* The same hand-out instructs the seat to wait on a process that,
at draw time, had been running for five hours and twenty minutes and had one of twenty-seven passes
left. **The item commissioned a wait longer than the deadline it was issued under.**

This is not a scheduling accident that a longer interval fixes. The two numbers are set by different
concerns and neither knows about the other:

- the **sweep interval** bounds how long a seat may hold an item without evidence of progress, which
  is a liveness property about seats;
- the **wait** is a property of the subject the item names, which for a `floor-all` leg is
  ~25 minutes per seed and was known and written down before this item existed
  (`tools/run_arms_rerun.py:279` records the measured per-seed cost).

**A `--landed` inside the window does not reset the clock.** This turn landed and bound at 14:47,
53 minutes into the window, and was still swept — so the one signal a working seat can emit does not
count as the progress the sweep is looking for. That is the part worth fixing: an item whose seat is
demonstrably landing work is being reclaimed as though it were idle.

## Why the obvious remedy is the wrong one

Raising the interval to cover the longest run does not work, and proposing it would be the mistake
this repository has a rule for. The distribution is not bounded: `floor-all` at nine seeds is ~4h,
at 116 seeds it would be ~48h, and the interval has to be short enough to actually reclaim a dead
seat. **A constant cannot separate "waiting on a six-hour run it was told not to relaunch" from
"dead".**

What separates them is already on disk and already required by the walls: **`tools/wait_for.py`
names its subject and carries a deadline, and the item named a PID.** A seat waiting on a named,
live PID is not idle, and that is checkable in one `ps` call rather than inferable from a clock.

## The candidate repair, stated as a candidate

**A `--landed` within the window extends it.** One line, no new mechanism, and it keys the sweep to
the property the sweep exists to detect — *has this seat produced anything* — rather than to elapsed
time, which is today's proxy for it. This turn is the witness: it bound a path at 53 minutes and was
still swept at 100.

That alone would have fixed this instance. It does **not** cover the harder case — a seat that
correctly lands nothing for four hours because its subject has not finished — and this document does
not claim it does. The second leg, if it is wanted, is the item's own named PID: the draw ledger
already carries the note that names it, and a sweep that skips an item whose named PID is alive
would separate the two states directly. **That is a bigger change and it is not obviously worth it**
— it puts a liveness control's correctness in the hands of a PID written into free text by whoever
drafted the item, which is a weaker thing than a timer. Costing it is the next orientation's call,
not this turn's.

**Neither leg is built here.** This turn's remaining budget belongs to the deliverable it was drawn
for, which is landed. The instance is recorded so the class is visible; a fix proposed in the same
breath as a refusal to measure it would be the shape this repository already refuses.

## What is NOT wrong

- **No work was lost.** `58b6cec1f` and `8d7693d92` are both ancestors of `origin/main`; the live
  feed there carries `contrast_bounds.contrasts.selection_gbp.n = 9`.
- **The refusal named its reason and named it correctly**, and it distinguished the two causes it
  could have had (*"this is the expected reading after a `--release`; if you did not, the claim was
  swept"*). It is a good refusal. Nothing about it needs repairing.
- **The item will be re-offered**, which is the designed behaviour on an unbound landing. The next
  seat to draw it should read
  `SEAT_RESULT_THE_SELECTION_LEGS_SIGN_WENT_THE_OTHER_WAY_AND_THE_PREREGISTRATIONS_BET_IS_REFUTED_2026-09-09.md`
  **before doing anything**: the run is finished, the floor is promoted, the feed is published to
  origin and the pre-registration is graded. **Do not relaunch the run.** What remains is the two
  next steps that result document names, neither of which is this item.

## What is next

1. Cost the `--landed`-extends-the-window leg. One line, one control: a claim bound inside the
   window survives past it, driven from a fake clock so the control does not need 100 minutes to
   run.
2. Leave the PID leg parked with its objection written down, above.
3. **Do not raise the interval.** It is the remedy that looks right, works for exactly the run
   length it is tuned to, and hides the class again.
