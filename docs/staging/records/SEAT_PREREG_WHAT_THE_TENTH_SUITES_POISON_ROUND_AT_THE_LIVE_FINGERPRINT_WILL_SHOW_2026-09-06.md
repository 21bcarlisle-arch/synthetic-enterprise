**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: what the tenth suite's poison round at fingerprint `d7eb36a0b901` will show

**Written 2026-09-06, delivery seat, shared tree at `353d0e910`, claim
`fuel-mix-tenth-suite-reachability`. Typed while the run is in its BASELINE round — no poison cell
exists yet. The run is PID 1675351, launched by me from
`/var/tmp/run_fuel_mix_poison_d7eb36a0b901.sh`.**

## Why a round that has already been bought is being bought again

`/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json` already answers this question. It says
`tests/tools/test_ep13_embedded_generation_bound.py` **never reaches** the subject — `rc=0` in
604.5s under the import-time poison — and its null round says `behaviour only`, so it is not a
text-grader either.

That answer is very probably right, and it is not evidence I can stand on:

- **`95c9da4db380` is the fingerprint of no committed spec.** `a3d446895`, `8bca959fb`,
  `6484bce27`, `177de48c1` and `2eeafa709` all hash to `c6cdcb3babf6`; `b3938b313` and HEAD hash to
  `d7eb36a0b901`. The run was launched from the shared tree at 03:06 while a seat worked in a
  worktree at `e20d5a2dc`, so the spec it graded was an **uncommitted working-tree copy that cannot
  be reconstructed**.
- What poison text that copy actually wrote is therefore an **inference** from its committed
  neighbours (`poison_old`/`poison_new` hash identically across the whole window, and the subject
  has not changed since `177de48c1`), not a record.

Adopting rows from a run whose spec cannot be reproduced is the exact class this instrument exists
to find, and this project has now committed it twice in one day with the instrument itself. Thirty
minutes buys the answer with provenance, and it lands in the results file a later full run would
resume from, so the spend is not wasted even when the answer is the one already on disk.

## The predictions

1. **The tenth suite is NON-REACHING: `reaches_subject: false`, `rc=0`.** It joins the six other
   `ep13_*` suites, which read the subject as text and walk it as an AST rather than executing it.
2. **The null round returns `behaviour only`** — it is not reddened by the behaviour-preserving
   marker either, so its greens are not text-grading artefacts.
3. **Therefore the remaining ~110 minutes is NOT worth buying.** Eleven mutation rounds at ~605s
   would buy eleven cells stamped `UNREACHABLE -- proves nothing`, and the verdict they completed
   would be a verdict over a population one member of which cannot see the subject.
4. **The baseline is green** (`rc=0`, `failed=0`), so no red at HEAD is doing the work of a kill.

## What would refute each

1 is refuted by `reaches_subject: true` — and that is the outcome that WOULD justify the 110
minutes, because a reaching suite's eleven cells are real evidence. 2 is refuted by
`GRADES THE TEXT`. 3 follows from 1 and falls with it. 4 is refuted by any baseline failure, which
would also void the poison cell's meaning and force a re-run after the red is fixed.

## The flattering reading, named before it is available

An unexpected `NEVER REACHES` and a **broken floor** look identical. The floor here is stricter
than on earlier subjects — every caller imports `fuel_mix` lazily inside a function body, so the
poison reddens a suite only if the suite executes the calling path. If prediction 1 holds, what is
established is *"this suite does not run any path that imports the subject"*, and NOT *"this suite
cannot catch the subject failing"*: the spec declares no `hard_poison`, so the second floor does
not exist for `fuel_mix` and the engine says so in its own summary. The control suites staying
green under the poison is what separates a discriminating floor from one that reddens nothing.

---

## ADDENDUM 2026-09-06 04:45 BST — the MECHANISM, established statically before the poison answered

*Added while the poison pass was running: the baseline had returned `rc=0 failed=0 623.1s`,
confirming prediction 4, and no `reaches_subject` value existed yet.*

Prediction 1 above is an inference from a family resemblance — six sibling `ep13_*` suites read the
subject as text, so this one probably does too. That is a prior, and it is weaker than what the
source will simply tell you. Two static facts, checkable in seconds, say the same thing without
running anything:

1. **The suite cannot execute the subject on any path it takes.**
   `tools/ep13_embedded_generation_bound.py` imports `fuel_mix` in exactly one place — inside
   `measure()` at line 521, calling it at 527. The suite's entry points into the module are
   `measure_year`, `day_mean_series`, `fit_surface_nd`, `apply_surface_nd`, `build_coordinates`,
   `verdicts`, `within_day_deviation`, `oracle_is_unreachable_from` and the `held_out` fixture.
   **`measure` is in the transitive call closure of none of them.** It is the rung `main()` runs,
   and no test runs `main`. The suite calls `measure_year`, which is a different function.
2. **Its one reference to the subject reads it as bytes.**
   `tests/tools/test_ep13_embedded_generation_bound.py:289-293` does
   `(bound.PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text()` and hands the
   result to `bound.oracle_is_unreachable_from` — an AST walk asserting the published feed does not
   import the oracle.

This sharpens what a `false` will and will not license. **Poison-green does not imply
mutation-green in general**: a suite that never imports the subject cannot be reddened by anything
done to it, but a suite that reads the subject's TEXT can redden for an edit the poison never made.
This suite is both. What closes the gap here is fact 2 and not the poison round: the only text
assertion is *"the feed does not import the oracle"*, and no mutation in `MUTATIONS` adds such an
import. So the eleven unbought cells are green by construction, and that is a per-mutation argument
against this spec's eleven contracts — not a theorem about blind suites, and it would have to be
re-made for any twelfth.

**And the null round's green is weak evidence, not a clean bill.** A suite that is green in every
round is green in the null round too. `grades_text: false` here says the null marker is not an
import of the oracle; it does not say the suite ignores the subject's bytes, and fact 2 says it
does not.

### Why this addendum exists rather than a second document

A second pre-registration for this same round was written at 04:39 BST from the isolated worktree
`/var/tmp/se-seat-executor` and landed as
`docs/staging/records/SEAT_PREREG_WHAT_THE_TENTH_SUITES_POISON_ROUND_WILL_SHOW_AND_WHAT_I_WILL_DO_WITH_EITHER_ANSWER_2026-09-06.md`.
**This document was invisible to it.** It was committed in the shared tree at `1c9a08792` and never
pushed, so `origin/main` — the only thing an isolated worktree can see — did not carry it, and
neither did the worktree's own `git log`. *Unpushed is still imported, and it is also still
unfindable: a lane that files work locally and does not promote it has not just kept it out of the
record, it has armed the next lane to redo it.* The duplicate is withdrawn and its one novel part
is the section above.
