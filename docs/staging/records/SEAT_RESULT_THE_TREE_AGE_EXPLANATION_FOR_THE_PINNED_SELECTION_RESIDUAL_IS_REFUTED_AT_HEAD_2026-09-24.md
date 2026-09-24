**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# RESULT — the tree-age explanation for the pinned selection residual is REFUTED, and the pinning is WORSE at HEAD than on the tree the page publishes

*Lane 0 delivery, 2026-09-24T13:40Z. Drawn item:
`capture-the-five-seed-selection-noise-floor-before-its-only-copy-is-a-scratchpad`. Predictions:
`SEAT_PREREG_WHETHER_THE_FIVE_SEED_FAMILY_DRAWN_AT_A_NEW_TREE_REPEATS_A_SELECTION_GBP_2026-09-24.md`,
written before the per-seed values were opened and saying so. Grades the rule in
`docs/staging/SEAT_FINDING_THE_NARROW_WIDTH_BEHIND_THE_PUBLISHED_SELECTION_SIGN_IS_A_REPEATED_DRAW_2026-09-22.md`.
Artefact landed by this commit at
`docs/observability/value_cycle_ab_s1_noise_floor_five_seed_head_20260924.json` — eleven hours of
compute whose only copy was a scratchpad in `/tmp`.*

## Both predictions REFUTED, and not narrowly

| | predicted | observed | verdict |
|---|---|---|---|
| 1 — no `selection_gbp` repeats | 5 distinct of 5 | **3 distinct of 5**; one value drawn 3× | **REFUTED** |
| 2 — no lockstep pair | 0 of 10 pairs | **3 of 10 pairs**, Δ equal to the last digit | **REFUTED** |

The repeated value is `1479.0739599999797`, drawn by seeds 12, 14 and 15.

## The finding's rule is dead at the first family that could test it

> *"Every family drawn at an old tree repeats a `selection_gbp`. Neither family drawn at a new tree
> does."* — the 09-22 finding, five families, no exceptions.

This is the sixth family and the third drawn at a new tree — `3661d8d4e`, later than every tree in
that table. Under the rule it should not repeat. It repeats harder than anything on record:

| family | tree | n | distinct | draws inside a repeat | lockstep pairs | mean `selection_gbp` | sd |
|---|---|---|---|---|---|---|---|
| `folded18_single_arm` — **THE PUBLISHED FLOOR** | spliced (old) | 18 | 15 | 5 (**28%**) | 4 of 153 (2.6%) | **−959.78** | 1631.80 |
| **this family** | `3661d8d4e` (HEAD-era) | 5 | **3** | 3 (**60%**) | **3 of 10 (30%)** | **+1447.63** | **113.03** |

**"New tree" was never a mechanism, and it is now not even a correlate.** The finding was explicit
that it had not identified the code change that removed the lockstep between `4e7938f673` and
`a178b56d6`; it handed that on as the next question. The answer available now is that whatever was
different about those two families, it was not tree age — because the newest tree of all pins at
twice the published floor's rate.

## Both mechanisms are present, and mechanism 2 is reproduced exactly

The finding named two. This family carries one of each, which is why the refutation is not a
sampling accident.

**Mechanism 1 — an identical pass.** Seeds 14 and 15 agree in **every recorded field**, not merely
in `selection_gbp`: same `value_advantage_gbp`, same `level_advantage_gbp`, same
`level_share_of_advantage`, same counts. Two seeds, one draw.

**Mechanism 2 — a residual pinned across a pass that genuinely differed.** Seed 12 against seed 14
is a materially different pass — `value_advantage_gbp` 13181.187789 against 13019.106817,
`level_advantage_gbp` 11702.113829 against 11540.032857, and `level_share_of_advantage` differs
too. Yet `selection_gbp` is identical to fifteen digits, because:

```
Δ value_advantage_gbp = 162.0809719999961
Δ level_advantage_gbp = 162.0809719999961
```

The arms move in lockstep and the residual is their difference. This is the 09-22 finding's seed
3100003/3100006 shape, reproduced at HEAD on a different world-draw, and it is the serious one:
over part of its range the selection residual is **structurally unable to vary**.

## THE CONSEQUENCE NOBODY ASKED FOR: the instrument's confidence is manufactured by its own pinning

The artefact's own headline fields say:

- `selection_distinguishable_from_zero`: **True**
- `sems_from_zero`: **28.64**, against 2.776 needed to state a sign
- `seeds_needed_to_state_a_sign`: **2**

Twenty-eight sems is not a strong result here. It is the defect, reading as a result.

The sem is `sd/√n`, and `sd` is 113.03 — **fourteen times narrower than the published floor's
1631.80** — because three of the five draws are the same draw. A standard deviation taken across
pinned draws estimates how often the instrument pinned, not dispersion in the world. So the
relationship runs the wrong way: **the harder this instrument pins, the more confident it reports
itself to be.** A family that pinned all five would report a sem of zero and infinite confidence.

That is a control that fails in the flattering direction, and it is the reason this result is
worth more than the run that produced it. The 09-22 finding established that the narrow width was
not a property of the world. This adds that the width's *own confidence statistic* is monotonically
rewarded by the pinning, so no reader of `distance_to_a_sign` can detect the problem from the field
that exists to tell them whether to trust it.

## The sign also flipped, and the comparison is legitimate

The published floor's mean `selection_gbp` is **−959.78**. This family's is **+1447.63**. Opposite
signs, both claiming to be the same quantity in the same world.

**I checked comparability before quoting this, because a sign flip is exactly where this project
publishes a difference between two things that are not the same quantity.** They match on every
axis that defines the measurement: `world_identity.digest` `39a192ce04c1eda8` (same world),
`redraw_scope.mode` `all`, `clock` `settled-realised`, `redraw_key` elasticity, same tool, and the
same `--level-arm` split — which is not an optional difference between the two runs but the flag
that *produces* `selection_gbp` at all, so the published family necessarily carries it too.

Two axes do differ: the tree, and the seed set. The seed set is the benign one — the 09-22
one-variable run measured it directly and it does not move the width (F=1.97, df (8,11), p=0.295),
while the tree does (F=16.93, p=4.9e-05). So the tree is where the flip lives.

**The honest reading is not "the sign is really positive".** n=5 with 3 of the 5 pinned is not a
family that can state a sign in either direction, whatever its sem claims. The reading is that the
published NEGATIVE sign and a POSITIVE one are both producible from this instrument on the same
world by changing the tree, and neither is thereby established.

## What this establishes, and what it does not

- **Does:** refute the tree-age rule. Re-running at HEAD does not escape the pinning; it makes it
  worse. Any plan that expected a fresh run at HEAD to repair the published figure is now dead, and
  **that plan's death is the most valuable thing here** — it was the cheapest-looking route and it
  would have cost another eleven hours to discover.
- **Does:** establish that `distance_to_a_sign` is anti-correlated with trustworthiness on this
  instrument, which is a defect in the instrument's reporting surface, not in this run.
- **Does not:** identify what causes the lockstep. Still open, and still the question that matters.
  What this narrows is where to look: not at the tree, but at the arms' shared path through the
  same draw. The two arms moving by identical amounts to the last digit is a strong hint that they
  share a term the re-draw does not reach.
- **Does not:** establish any value for the selection residual. No figure here should reach a page.

## Why nothing is withdrawn from the page in this commit

Same order as 09-22, and for the same reason: publish the evidence, then move the constant. This
commit lands the artefact, the pre-registration and this result. The 09-22 finding stays BLOCKING —
its subject (the published sign rests on a pinned instrument) is not merely unchanged but
strengthened; only its proposed *explanation* is refuted, and a finding is not cleared by refuting
its explanation.

**The hand-off, and it is now narrower than it was:** find the shared term. `selection_gbp` is
`value_advantage_gbp − level_advantage_gbp`, and a re-draw that moves both by exactly the same
amount is re-drawing something both arms consume identically. That is a code question with a
cheap answer, not another eleven-hour run — and the next increment should be that, not more seeds.
More seeds on this instrument buy a narrower sem and no more truth.

**Reversal:** `git revert` of this commit removes one artefact and two staging records. No
published figure moves, because none is changed here.
