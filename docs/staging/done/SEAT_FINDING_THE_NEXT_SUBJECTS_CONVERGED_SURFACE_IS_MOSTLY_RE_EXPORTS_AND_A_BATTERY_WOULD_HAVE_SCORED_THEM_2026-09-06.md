**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: the next subject's converged surface is mostly re-exports, and a battery run on it would have scored them as contracts

**Measured 2026-09-06, delivery seat, isolated worktree at `423203aa5`. Claim id
`register-low-water-evidence-convergence-sweep`. This is the pre-registration for the sweep's
fourth subject and it is a finding first: three hazards were found by INSPECTION before the
battery ran, and each one would have corrupted the result had it not been.**

---

## The subject

`tools/generate_grid_intensity_feed.py` — the screen's second row by caller count. **8 first-party
callers, 2 direct test importers, 108 reaching suites.** Seven of the eight callers are the
`ep13_*` bound/ceiling tools plus `background/process_run_complete.py`.

The convergence is unusually clean: **seven callers import the identical five names.**

```
AGWS_CACHE, DEMAND_CACHE, aggregate_demand, aggregate_renewable_generation, fuel_mix
```

## Hazard 1 — three of those five names are not this module's code

* `AGWS_CACHE`, `DEMAND_CACHE` are `Path` constants.
* `aggregate_demand` is defined in **`sim/grid_carbon_intensity.py:758`**.
* `aggregate_renewable_generation` is defined in **`sim/generation_demand_history.py:91`**.

`generate_grid_intensity_feed.py` imports both at lines 56 and 60 and re-exports them. **Only
`fuel_mix` is this module's own behaviour.**

So a battery that takes contracts from "the names the callers import" — which is exactly the
method used on the previous three subjects, and it was correct on all three — would here mutate a
re-export and score the result as a contract of this module. The `target present exactly once`
check does **not** catch it: the target *is* present exactly once, on an import line. It would
apply cleanly, kill or survive, and mean nothing about this subject.

**This is a new false-survivor mode for the family and it is the mirror of the one already
recorded.** The known one is a patch that never applied. This is a patch that applies perfectly to
code the subject does not own. Neither is visible in a `died`/`survived` column.

The rule that follows: **before mutating a name a caller imports, establish that the subject
DEFINES it.** A re-export is a routing decision, not a contract, and its contract belongs to the
battery for the module that owns it.

## Hazard 2 — six callers read the subject as TEXT, so a kill need not mean execution

Six of the seven `ep13_*` tools do:

```python
(PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text(encoding="utf-8")
```

and walk the result as an AST (`ceiling_is_unreachable_from`, `oracle_is_unreachable_from` — an
AST walk, deliberately not a substring search, and their own comments say why). They are asserting
the feed does not import them: a no-oracle control.

So for this subject `died` and "the suite executed the mutated line" are **different claims**, and
every battery in this family has silently treated them as one.

**The repair is landed rather than described**: `tools/contract_battery.py` gains a NULL ROUND —
the mirror image of the poison round. A source edit that changes the bytes and adds an AST node
and cannot change behaviour. Any suite that reddens under it is grading text, its cells are
stamped `died_but_grades_text`, and a subject with no null round is stamped UNKNOWN on the summary
line rather than passed.

It is already run and already earning: all ten suites of the previous subject are **behaviour
only**, which is what makes that result's kills trustworthy rather than merely reported.

## Hazard 3 — every caller imports LAZILY, so the poison floor grades something stricter here

All eight callers import inside a function body, not at module level
(`background/process_run_complete.py:7641`, `tools/ep13_input_ceiling.py:545`, and the rest).

An import-time poison therefore reddens a suite only if the suite **calls the function that does
the import**. That is a *stricter* and more useful floor than the previous subject's — it grades
"does this suite execute the calling path" rather than "does this suite import the module" — but
it will report `NEVER REACHES` for suites that a reader would call importers, and the two previous
subjects' floors did not have that property.

**Stated before the run, because after it a stricter floor and a broken one look identical**, and
the flattering reading of an unexpected `NEVER REACHES` is that the floor is working.

## What this establishes about the sweep's method, not just this subject

The drawn direction said ranking is not grading, and three subjects have now shown that. This adds
a step in front of both: **screening is not scoping.** The screen correctly reports 8 callers and
a five-name converged surface. Four of those five names cannot be graded against this module at
all, and one of them can be killed without being run.

None of that is visible in any column the screen prints, and none of it would have been visible in
the battery's output either. It was found by asking where a name is DEFINED — the same question
that found the £55/£150 acquisition-cost gap, asked of code instead of a constant.

## What this does NOT establish

No contract of this module has been graded. `fuel_mix` is the only member of the converged surface
this module owns, and whether it is proved — and by which of the two direct suites,
`tests/sim/test_elexon_fuel_outturn.py` (35 tests, 0.8s) or
`tests/tools/test_grid_intensity_feed_and_explore_carbon.py` (43 tests, 9.1s) — is the measurement
this file pre-registers and does not contain.

**The prediction, fixed here:** `fuel_mix` is proved by
`test_grid_intensity_feed_and_explore_carbon.py` and by nothing else in the ten-suite population,
and at least one `ep13_*` suite reddens under the NULL round — i.e. at least one of the six
textual readers is grading bytes and has been counted as evidence.

The three named `sim/` re-export owners are a separate subject, and neither
`sim/grid_carbon_intensity.py` nor `sim/generation_demand_history.py` has been screened for
convergence in its own right.
