**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: did the cadence lever make `pending == 0` OBSERVABLE, or only REACHABLE?

**Written:** 2026-09-04 ~15:50Z, delivery seat, isolated worktree, **before looking at any
post-lever marker or gate record.** The subject period (lever landed ~13:00Z → now) is ~2h50m,
which is ~1.9 producer periods under the new cadence — the first moment the question can be asked
at all.

## Why this exists

`5952aaa4e` landed the cadence lever (`BETWEEN_RUN_PAUSE_SECONDS`, derived: 4685s). Its own
finding states plainly what it did **not** do:

> **`pending == 0` is not yet observed.** This makes it reachable; it does not prove it happened.
> The acceptance test is a `pending == 0` sighting in `.publish_gate_state.json` after one full
> producer period (~90 min). Not verifiable inside this bounded tick.

That is the direction's acceptance test — *"the run queue is empty"* — and it is now inside the
window where it can be checked. A prediction filed after the answer is not a prediction, so it is
filed here first.

## The predictions

**P1 — the lever took effect on the producer.** Median marker interarrival since 13:00Z is
**≥ 78 min** (the pause alone is 4685s = 78.1 min), against 13.2 min measured before it.
*Refuted if* interarrival is still under ~20 min — which would mean the daemon never reloaded the
constant (`PUSHED IS NOT IMPORTED`: nothing restarts the sim runner on a landing, and the running
process holds the old module).

**P2 — this is the one I expect to be uncomfortable.** `pending == 0` has **NOT** been observed in
any record since the lever landed, *and its absence is not evidence the lever failed.* The
mechanism is right and the observation window is tiny:

- producer period = 90.3 min (p90-derived, by construction)
- publisher cycle after a PASS = 88.9 min (p50)
- ⇒ the interval in which zero markers are pending is **~1.4 min per ~90 min cycle — a 1.6% duty**

A sampler that looks once per cycle catches it with p ≈ 0.016. **The acceptance test as written is
therefore nearly unsatisfiable by sampling even when the system is working perfectly**, which is a
different failure from the one the direction set out to fix, and it would be misread as the lever
not working.

*Refuted if* a `pending == 0` sighting exists in the post-lever records — in which case P2 is
simply wrong and the margin is fatter than the p50/p90 arithmetic implies.

**P3 — the depth collapsed even though the backlog did not "drain".** Pending markers observed at
publish instants since the lever are **≤ 2**, against the "3+ newer markers at every success
instant" the direction measured. Note this is *not* drainage: at rho ≈ 0.98 a backlog does not
drain, it stops growing. What removes the backlog is the supersede-retirement sweep
(`Retired 7/7`, already working), not the cadence.

## What follows from each outcome, decided now

- **P1 refuted** → the lever is landed but not *running*; the deliverable is making the sim runner
  pick up its own constant, not any further cadence arithmetic.
- **P2 confirmed** → the deliverable is an **honest acceptance instrument**: `pending == 0` is the
  wrong thing to sample for, and the right one is a continuously-maintained quantity (the observed
  producer:consumer ratio, or a high-water mark of pending that stops rising). Report "we cannot
  tell by sampling" on the surface rather than letting a 1.6%-duty miss read as a failure.
- **P2 refuted** → say so beside this text and close the acceptance.
- **P3 refuted** (depth still 3+) → the cadence did not bind; re-open candidate (c).

## Method, fixed before the data is read

Marker stamps from the shared tree's `docs/staging/` run-complete markers and
`docs/observability/publish_gate_duration.jsonl` (the shared tree's copy — this worktree does not
carry the untracked live ledgers). Interarrival = successive marker mtimes. "Post-lever" =
strictly after the `5952aaa4e` commit instant. Cycle gaps separated by outcome, as the prior
measurement established they must be.

---

# THE ANSWERS, recorded beside the predictions

Measured ~15:50Z, immediately after the text above. Full write-up:
`SEAT_FINDING_THE_CADENCE_LEVER_WAS_LIVE_AND_NEVER_ONCE_SERVED_BECAUSE_A_DEPLOY_RESTART_RESETS_IT_2026-09-04.md`.

**P1 — REFUTED, and neither of the two causes I offered was the right one.** Median post-lever
marker interarrival is **30 min**, not ≥78. I named the failure mode in advance as `PUSHED IS NOT
IMPORTED` — the daemon holding old code. That was wrong: the daemon holds the NEW code and logs
`Waiting 4685s` every cycle. It is restarted by `deploy_restart.py` before the sleep completes, so
the constant is live and the pause is never served. **Five of five post-lever runs began at a
restart instant.** I predicted the right symptom off the wrong mechanism, which is exactly why the
prediction had to be written down to be worth anything.

**P2 — REFUTED, flatly.** `pending == 0` is not a 1.6%-duty rarity; it is TRUE right now, and the
supersede sweep is what holds it there. My duty-cycle arithmetic assumed the queue drains by the
producer/consumer race, and it does not — it is emptied by retirement. The whole "acceptance test
is nearly unsatisfiable by sampling" argument was built on that wrong model and is withdrawn.

**P3 — CONFIRMED, but it proves less than I claimed for it.** Depth is 0, not merely ≤2. I had
already noted this would be retirement rather than drainage; it was, so the confirmation carries
no evidence about the cadence either way.

**The pre-registered decision rule fired correctly even though the reasoning under it was wrong.**
"P1 refuted → the deliverable is making the sim runner honour its own constant, not further
cadence arithmetic." That is what was built. Recorded because a decision rule that survives its
author's mechanism being wrong is the only kind worth writing in advance.

**What none of the three predictions anticipated, and it is the finding that matters:** the
direction's acceptance test is MET and the episode still cannot close, because every publish
refuses at the commit with `behind_origin`. The binding constraint moved off cadence between the
direction being written and this measurement being taken.
