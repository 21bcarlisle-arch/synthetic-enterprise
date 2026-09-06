**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: what the tenth suite's poison round will show, and what I do with either answer

**Written 2026-09-06 04:39 BST, delivery seat, isolated worktree `/var/tmp/se-seat-executor` at
`fc7862de7`, claim id `fuel-mix-tenth-suite-reachability`. Recorded while the run is in its
BASELINE pass — the poison pass had not started and no `reaches_subject` value existed at the live
fingerprint when this was typed.**

The run is not mine to start and I did not start a second one. It is PID 1675351, launched
04:31:00 BST from the SHARED tree (`/home/rich/synthetic-enterprise`) by the previous turn of this
claim, as `--suites test_ep13_embedded_generation_bound --only NONE`: baseline, poison and null
over the tenth suite alone, at the LIVE spec fingerprint `d7eb36a0b901`, three passes at ~605s.

## What is already known, and must not be dressed up as a prediction

`/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json` already records this suite as
`reaches_subject: false` (rc=0, 604.5s) and `grades_text: false` (613.0s). So "NEVER REACHES" is a
**prior, not a blind guess**. It is being re-bought because `95c9da4db380` is the fingerprint of no
committed spec — it was produced by an uncommitted working-tree spec that cannot be reconstructed,
and adopting rows from a run whose spec cannot be reproduced is the exact class this instrument
exists to find.

## The mechanism, established statically before the answer arrives

This is the part the earlier run measured but never explained, and it is checkable in seconds:

1. **The suite never executes the subject.** `tools/ep13_embedded_generation_bound.py` imports
   `fuel_mix` in exactly one place — `measure()`, line 521, calling it at line 527. The suite's
   entry points are `measure_year`, `day_mean_series`, `fit_surface_nd`, `apply_surface_nd`,
   `build_coordinates`, `verdicts`, `within_day_deviation`, `oracle_is_unreachable_from` and the
   `held_out` fixture. **`measure` is not in the transitive call closure of any of them.** The
   suite calls `measure_year`; `measure` is the rung `main()` runs and no test does.
2. **Its one reference to the subject reads it as TEXT.**
   `tests/tools/test_ep13_embedded_generation_bound.py:289-293` does
   `(bound.PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text()` and feeds it to
   `bound.oracle_is_unreachable_from` — an AST walk asserting the published feed does not import
   the oracle. That is the seventh instance of the pattern the spec's null-round comment records
   for six of the eight callers.

## The predictions

1. **`reaches_subject: false` at the live fingerprint**, reproducing `95c9da4db380` — for the
   mechanism above and not merely by inheritance.
2. **Both control suites stay green** under the same poison, so the floor still discriminates.
3. **`grades_text: false`**, and this is a WEAK green rather than a clean bill: the suite reads the
   subject's bytes, so its null-round green says only that the null marker is not an import of the
   oracle. A suite green in every round is green in the null round too, and that is not evidence
   about text-grading.
4. **~605s per pass**, ±10%, so the poison pass ends near 04:51 BST and the whole three-pass run
   near 05:01 BST — ~30 minutes from its 04:31 start.

## What refutes each

1 is refuted by `reaches_subject: true` — which would mean the earlier run's row is wrong and the
static closure above is wrong, and the 2h grading run becomes worth buying immediately. 2 is
refuted by `tests/background/test_delivery_lane.py` or `tests/design/test_atom_notes_store.py`
reddening, which voids the round. 3 is refuted by any red in the null pass. 4 is refuted by a pass
outside 545–665s.

## THE DECISION RULE, stated before the answer

Written now so the answer cannot be read to fit whatever I do next.

- **If `reaches_subject` is FALSE: I do not buy the ~2h grading run**, and I land that refusal in
  the spec beside the evidence rather than in prose that the next lane will not read. Eleven cells
  at 655s each in a suite that cannot execute the subject would each be stamped
  `survived_but_unreachable` on arrival — the engine already knows what they would be worth, and
  paying two hours to write down a value the poison round determines is the purest form of a
  control that cannot fail.
- **If `reaches_subject` is TRUE: I buy it**, because then the tenth column is the only one that
  could carry a caller verdict this subject does not already have, and the eleven rows currently
  barred from `survived_all` become answerable.
- **Either way the row is recorded at a reproducible fingerprint**, which is the thing
  `95c9da4db380` could not offer.

## The bound this does NOT lift

A false `reaches_subject` settles what the tenth COLUMN is worth. It does not settle what
`survived_all` should then mean: `tools/contract_battery.py:374` requires a cell from every one of
the eight declared caller suites, so a column nobody will ever buy leaves all eleven rows without a
verdict permanently. That is a separate question about the engine, it is named here so it is not
mistaken for something this round answered, and it is not what this round is being bought to
decide.
