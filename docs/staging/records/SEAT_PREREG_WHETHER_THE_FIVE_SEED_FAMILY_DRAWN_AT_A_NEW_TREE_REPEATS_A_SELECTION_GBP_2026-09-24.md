**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# PRE-REGISTRATION — whether the five-seed family drawn at a NEW tree repeats a `selection_gbp`

*Lane 0 delivery, 2026-09-24T13:22Z. Drawn item:
`capture-the-five-seed-selection-noise-floor-before-its-only-copy-is-a-scratchpad`. Grades the
repeat claim in `docs/staging/SEAT_FINDING_THE_NARROW_WIDTH_BEHIND_THE_PUBLISHED_SELECTION_SIGN_IS_A_REPEATED_DRAW_2026-09-22.md`.*

## THIS FILE IS WRITTEN AFTER THE RUN FINISHED. Here is exactly what I had read, and what I had not

The run — `tools.run_value_cycle_ab --level-arm --noise-floor-seeds 11,12,13,14,15 --contrast
selection_gbp`, pid 3567620 — **completed at 2026-09-24T12:56:49Z**, before this invocation began.
No pre-registration for it exists anywhere in the tree; I searched `docs/staging/records/`,
`docs/design/` and `docs/observability/` for one and found preregs for the 09-18, 09-22 and 09-23
families only. **So this is not a prediction filed before its run.** Pretending otherwise would be
the exact defect the prereg convention exists to catch, so the honest version is a fence around
what I have actually seen.

**READ before writing this file** — the artefact's top-level summary keys only:

- `selection_gbp_spread`: n=5, **mean 1447.633, stdev 113.025**, min 1252.679, max 1548.263,
  range 295.584
- `level_share_spread`: n=5, mean 0.88972, stdev 0.00832
- `selection_sem_gbp` 50.546; `selection_distinguishable_from_zero` **True**; `sems_from_zero`
  28.64 against 2.776 needed
- `redraw_scope.mode` `all`; `redraw_key` `elasticity`; `producing_commit` `3661d8d4e`;
  `world_identity.digest` `39a192ce04c1eda8`; `book_identity.seeds_reconciled` 5, with
  `seeds_that_recorded_no_book` 0
- the first ~300 characters of `seeds[0]` — seed 11's `draw_calls` 297, `elasticity_redrawn` 297,
  `elasticity_held_fixed` 0, `accounts_redrawn` 69, `billing_accounts_settled_in_window` 164

**NOT READ, and the predictions below turn entirely on it:** *any* `selection_gbp` value for *any*
seed. The per-seed figures are what the repeat test needs and I have not opened them. `stdev`
113.025 is non-zero, so I know the five are not *all* identical — it excludes total degeneracy and
nothing else. Two of five repeating, or three, sits comfortably inside a non-zero spread, which is
precisely the shape the 09-22 finding documented (seeds 3100003/3100012 identical inside a family
whose sd was 1311.96). Nor have I read `value_advantage_gbp` or `level_advantage_gbp` per seed,
which the lockstep test needs.

## The claim being graded

The 09-22 finding's rule, in its own words: **"Every family drawn at an old tree repeats a
`selection_gbp`. Neither family drawn at a new tree does."** Five families, no exceptions — the
three narrow ones repeat, the two wide ones (`a178b56d6`, `18327d977`) do not.

This family was produced at `3661d8d4e`, a tree later than every family in that table. It is the
**sixth** family and the **third** drawn at a new tree. Under the finding's rule it belongs with
the non-repeaters.

## PREDICTION 1 — no `selection_gbp` repeats across the five seeds

**Held iff all five `selection_gbp` values are distinct.** Refuted iff any two are equal (compared
at full recorded precision — the 09-22 repeats agreed to fifteen digits, so no tolerance is
needed or allowed; an exact-equality test is the right one and a near-equality test would be
choosing its own bar after the fact).

**This is the prediction the run was drawn to make.** The finding's rule is a one-line generalisation
over five families and this is the first family drawn since it was written. A repeat here refutes
the rule outright, and that is the outcome that changes what we do next: it would mean the pinning
is not a property of old trees, and the tree-age explanation — the whole basis for expecting the
published sign to be repairable by re-running at HEAD — would be dead.

I expect it HELD, at maybe 70/30. The evidence for is five-for-five and the mechanism story is
coherent. The evidence against is that n=5 families is a thin base for a universal, "new tree" is
not a mechanism, and the finding itself says the code change that removed the lockstep was never
identified — so nothing establishes that whatever removed it at `a178b56d6` is still absent at
`3661d8d4e`.

## PREDICTION 2 — no pinned residual: no two seeds move `value_advantage_gbp` and `level_advantage_gbp` by the identical amount

Mechanism 2 of the finding, which is the serious one. Between seeds 3100003 and 3100006 the two
arms moved by 1,625.897961 each, to the last digit, pinning their difference.

**Held iff, over all ten seed pairs, no pair has `Δvalue_advantage_gbp == Δlevel_advantage_gbp`
exactly.** Refuted by any such pair.

Prediction 2 is the mechanism behind prediction 1 and I expect them to agree. **If they disagree,
the disagreement is the result** and it is more informative than either alone: lockstep without a
repeat means the pinning survives at HEAD but no longer collides, and a family that escapes by
luck rather than by structure will pin again at n=18.

## NOT A PREDICTION — the width, and the sign

I have already read both, so neither can be predicted and both are recorded here as descriptions so
that no later reading can present them as foreseen:

- **stdev 113.03** against 1311.96 for the narrowest family in the finding's table and 5398.31 for
  the widest. This family is **an order of magnitude narrower than the narrow ones** — i.e. further
  in the direction the finding calls suspect, not nearer the wide ones.
- **The mean is POSITIVE, +£1447.63.** The page publishes a NEGATIVE selection sign.

**The first thing the grader must establish is whether this quantity is the published one at all,
and I do not assume it is.** This run carries `--level-arm`, and no family in the finding's table
is recorded as carrying it. A different arm configuration, a different contrast, or a different
book would make both readings above comparisons between two things that are not the same quantity —
this project's named recurring failure, and the one the sign flip should make me suspect first.
`level_share_spread` at 0.890 with sd 0.0083 says the level leg takes ~89% of the move here, which
is a composition claim in its own right and is not one the published floor makes.

So: **both of those readings are withheld from any published comparison until the arm
configuration and the contrast are matched against `NOISE_FLOOR_PATH`'s own.** If they do not
match, the correct statement is that this family does not speak to the published figure, and the
repeat test — which is internal to this family and needs no comparability — is the only thing it
settles. That would still settle the thing it was drawn for.

## What is graded next, mechanically

1. Extract `selection_gbp` for all five seeds; test exact pairwise equality. → prediction 1.
2. Extract `value_advantage_gbp` and `level_advantage_gbp`; test the ten pairwise deltas for exact
   equality. → prediction 2.
3. Read `NOISE_FLOOR_PATH`'s own artefact for arm configuration and contrast, and state whether
   this family is comparable to it before quoting any width or sign beside it.
4. Land the artefact, whichever way it fell.
