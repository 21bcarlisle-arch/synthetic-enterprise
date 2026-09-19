**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `a-published-site-feed-is-never-compared-against-what-its-generator-would-produce`

# Pre-registration: what a regenerate-and-compare control will find across the published feeds

*Written BEFORE the first extract was built or any generator was re-run. The measurement it
predicts is the one the SLC-27B finding asked for and did not build:
`SEAT_FINDING_A_FALSE_REGULATORY_CITATION_WAS_CORRECTED_IN_THE_RENDERING_AND_NOT_IN_THE_SOURCE_SO_EVERY_REGENERATION_REVERTS_IT_2026-09-19.md`.*

---

## The question

`site/data/` holds 61 published `.json` feeds. Nothing anywhere compares any of them against what
its generator would produce. One divergence is known — the false `Ofgem SLC 27B` citation, repaired
in `1d5642c35` — and it was found by accident, not by a control.

**How many of the other 60 are in the same state right now?**

## The method, fixed before the answer

Build ONE `git archive HEAD` extract of the whole tree into a temp dir. In that extract the
`site/data/*.json` files on disk ARE the committed bytes, and a generator's own
`PROJECT = Path(__file__).resolve().parent.parent` resolves to the extract — so the generator writes
its real relative path and no `OUT_PATH` is redirected. *(This project has burned a turn on the
other route: redirecting a generator's output path writes the shared tree anyway, or raises after a
correct write. The extract avoids the question entirely.)*

For each generator: snapshot the committed bytes, run `python3 -m tools.<generator>` with
`cwd=<extract>`, reload, and compare with `tools.artefact_rerun_diff.compare()` — which already
excludes the clock by name, treats additions as their own category, and tolerates summation-order
float noise. A row is RED if `changed` or `removed` is non-empty.

## The predictions

Each of these is falsifiable and none of the answers is known as this is written.

1. **Runnability.** Fewer than half the 61 feeds will have a generator that runs to completion in a
   HEAD extract. The extract has no `.git`, no untracked Elexon/NESO cache, and no `node_modules`,
   and several generators read artefacts that are themselves generated. **Predicted: 15–30 of ~55
   generators run clean.**
2. **Divergences.** Among the rows that DO run, at least one divergence beyond the repaired
   SLC-27B one will be found. **Predicted: 1–3 feeds diverge.** The reasoning: the SLC-27B edit was
   made by hand to two feeds at once, which is the behaviour of someone fixing what they saw on a
   page rather than the behaviour of someone who knew about the source; there is no reason that
   habit applied only once.
3. **Where.** If a divergence is found it will be in a *copy-style* feed — one whose generator
   transcribes committed prose (`simplified`, `capabilities_door`, `knowledge_*`, `maturity_map`,
   `method`, `proof`) — rather than in a *compute-style* one derived from a run artefact. Prose is
   what a reader notices is wrong and can plausibly hand-edit; a float is not.
4. **Nondeterminism.** At least one generator will differ from its committed bytes for a reason that
   is NOT a hand-edit — a non-clock wall-clock derivation, a set iteration order, or a read of live
   untracked state. **Predicted: 2–6 such rows.** These are a DIFFERENT finding from a hand-edit and
   must not be reported as one.

## What would refute the design rather than the predictions

If the extract cannot be built, or if generators in it fail for reasons that are artefacts of the
extract rather than of the code (the catalogued "a `git archive` extract has no `.git`" trap), then
the row count is measuring the extract and not the tree, and the control is worthless as written.
The tell is a row failing in the extract that passes in the worktree — so every non-running row is
recorded with its actual stderr, and "could not run" is published as a NAMED GAP, never as a pass.

## What done means

A committed control that RUNS every row it claims to cover, REDS on a genuine divergence, names
every feed it does not cover and why, and is mutation-proven: a hand-edit injected into a covered
feed's committed bytes must turn the row red.
