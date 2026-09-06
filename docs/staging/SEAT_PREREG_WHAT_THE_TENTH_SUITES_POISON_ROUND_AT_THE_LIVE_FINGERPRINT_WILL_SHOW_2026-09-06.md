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
