**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — what the three-state run ordering will reach, written before it is built

*Lane 0 delivery, 2026-09-23. Drawn item: `publish-the-corrected-one-book-baseline-comparison`.
Filed BEFORE the code exists and before any artefact pair was read for its stamps.*

## The question

`b36b9cc3d` landed the measurement this item asked for and named the one thing that stopped the
publish: `is_the_later_run` is

```python
is_the_later_run = not (current_at and superseded_at and current_at < superseded_at)
```

a two-valued flag over a three-valued question. `True` on that line means any of *genuinely later*,
*the same instant*, or *a stamp could not be read* — and the first is the flattering one, so a run
that is not later at all is published claiming it is. The publish route the finding measured as
"3 doors red" runs straight through it: promoting the corrected 09-18 book onto the canonical path
makes both panels one artefact, `current_at == superseded_at`, and the flag says **later**.

## What I predict, before building it

**P1 — all four ordering states are reachable from artefacts already on this disk**, without
authoring a fixture run: `later`, `earlier`, `same_stamp`, `unstated`. I predict `same_stamp` is
reachable from two DIFFERENT files — `value_cycle_ab_s1_three_arm.json` against
`value_cycle_ab_s1_three_arm_20260918.json` — because `756a86272` promoted one onto the other and
the finding establishes them byte-identical. If `same_stamp` turns out to need one file compared
with itself, the state is real but the defect is narrower than the finding claims and I will say so.

**P2 — the live feed today is `earlier`**, not `same_stamp`: `site/data/value_arms.json` carries
`is_the_later_run: false`, so the published ordering has a sign and the new field must agree with
it. A disagreement means I changed a verdict rather than split a state, and that is a red.

**P3 — `_against_the_panels_figure` infers run identity from figure equality and is wrong to.**
Its equal branch says "the two panels are one run's figure printed twice" on `point == old` alone.
I predict two genuinely distinct runs, ordered by their stamps, can produce the same advantage and
be told they are one run — the two-shapes-one-state collapse. I predict this is reachable by
construction (the function reads only two floats) and that nothing today refuses it.

**P4 — no site door rung changes colour.** Every reader of the flag gates on `is False` or on
`is not False`; moving the tie and the unreadable stamp from `True` to `None` cannot move either.
If a door reds, my claim that this is a split rather than a widening is refuted.

## What would refute each

P1: a state no artefact pair reaches — then it is an unreachable branch and must not be written.
P2: the new field disagreeing with the feed's published `false`.
P3: an existing control already asserting the sentence against run identity rather than arithmetic.
P4: any rung in `site/test_the_baseline_comparison_reaches_the_reader.py` changing colour.

## What this is NOT

It is not the publish. Moving `CURRENT_WORLD_THREE_ARM_PATH` onto the corrected run is the step
after this one, and the finding measured both routes to it (3 doors red and 7 doors red). This
increment removes the reason the first route publishes a contradiction; it does not take it.
