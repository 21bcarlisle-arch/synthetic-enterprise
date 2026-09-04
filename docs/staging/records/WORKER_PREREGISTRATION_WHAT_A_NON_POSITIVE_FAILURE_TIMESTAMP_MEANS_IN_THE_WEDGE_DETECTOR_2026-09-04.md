**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — publish-gate wedge, Rung 1

# Preregistration — what a non-positive `failures[].ts` means to the wedge detector

Written **before** reading the live `.publish_gate_state.json` or running anything against it.
Subject: `background/supervisor._publish_gate_wedge_active`, the age block at
`background/supervisor.py:3789-3794`.

## Why this is preregistered rather than just fixed

The landed repair of 2026-09-04 (`f77705819`) screened non-positive *episode starts* —
`wedge_since` — at the writer and in `episode_monotonic`. The clause it wrote is an argument about
**episode starts**: an instant at or before the epoch is not a start, it is the same fact as
`None`. That argument does not automatically extend to `failures[].ts`, which is a **failure
timestamp**: "when was this failure observed", not "when did the episode open". Whether a
non-positive value there means the same thing has to be decided on its own evidence, and the
evidence is what the writer can actually produce and what is on disk. Hence: say what it is before
measuring it.

## The questions, and what I predict

**Q1 — Does the live state file carry any non-positive / bool / non-finite value in
`failures[].ts`, `wedge_since` or `alerted_at` right now?**
Prediction: **no** for `failures[].ts` and `wedge_since`. `wedge_since` is screened at the writer
by `process_run_complete._is_episode_start` and again by `episode_monotonic._is_start_to_remember`.
`failures[].ts` is stamped from `now` (a `time.time()`) on every append. `alerted_at` is the one I
am least sure of: it is **not** in `PUBLISH_GATE_SINCE_FIELDS`, so no guard screens it, and it is
carried forward across writes. I still predict a positive float or `None`, because the only writer
sets it to `now`.

**Q2 — Is the RUNG-1 unwedge draw firing at this moment?**
Prediction: **no**. If it is, that is a live wedge and it becomes the work ahead of this.

**Q3 — What does the detector DO with a non-orderable `ts`?**
Prediction: for `0`, `False`, or a negative it dates the wedge to 1970 and fires permanently at
priority zero — the same shape as the landed finding, one field over. For `NaN` I predict something
worse and specific: `min()` can return the `NaN`, `age < PUBLISH_GATE_WEDGE_MIN_AGE_SECONDS` is
then `False` (all NaN comparisons are), and `int(age // 60)` on the next line **raises
`ValueError`** — an exception out of the draw ladder, which this function's own docstring promises
under "FAIL-SAFE: ... never an exception into the draw ladder". `json.loads` accepts a bare `NaN`
token, so this is reachable from a file, not only from a caller.

**Q4 — Is the detector the only unscreened copy left?**
Prediction: **no** — I expect to find the screen hand-rolled in at least three places
(`process_run_complete._is_episode_start`, `process_run_complete._episode_phrase`,
`episode_monotonic._is_start_to_remember`) with the supervisor's being the one that lacks the
positivity test. If a fourth exists, it is in scope.

## What each answer changes

* Q1 = yes on any field → the wedge is mis-dated on disk **today**, and the repair is urgent rather
  than structural. Q1 = no → the defect is latent, and the finding must say so plainly rather than
  claim a live outage it cannot show.
* Q3 confirming the `ValueError` → the fix is not merely "add `> 0`": the screen has to cover
  non-finite too, which is exactly what routing through `episode_monotonic._episode_key`
  (`math.isfinite`) gives for free, and hand-rolling `v > 0` would **not**.
* Q4 = a fourth copy → it gets the same call, not a fourth `isinstance`.

## What would refute the repair

If, after the change, a state file whose only orderable timestamp is a real one 90 minutes old no
longer produces a draw, the screen has eaten a genuine wedge and the fail direction is wrong. The
control must therefore assert the **positive** case is still reachable alongside every refusal —
per CLAUDE.md, a guard that refuses everything passes every refusal test.
