**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — make the page's two selection spreads legible now that they sit at different n) · **Class:** measurements_that_mirror

# RESULT — the drawn premise is spent, and the repair that spent it left a split of its own

The item was drawn to fix this, quoting correction 2 of
`SEAT_RESULT_THE_SELECTION_LEGS_SIGN_WENT_THE_OTHER_WAY_AND_THE_PREREGISTRATIONS_BET_IS_REFUTED_2026-09-09.md`:

> `site/data/value_arms.json` now publishes TWO selection spreads at TWO different n, and the
> current_world leg says 're-drawn 3 times in this same world' beside a bound built from nine
> rows, with nothing on the surface telling a reader they are different artefacts.

**It is spent, and it was spent before the draw.** Measured at HEAD `aac7da7e2`, not argued:

| where | n |
|---|---|
| `contrast_bounds.contrasts.selection_gbp.n` | **9** |
| `current_world.selection_leg.verdict_stability.n` | **9** |
| `current_world.verdict_stability.n` · `current_world.level_leg.*` | **9** |
| `error_bar.seeds` / `passes` | **9 / 27** |

Every selection spread on the feed is at n = 9. A scan of the whole payload for a surviving
`3 times` / `3 seeds` phrase returns exactly one hit, `floor_decomposition.seeds = 3` — the
`only`/`except` partition legs, a different artefact family, and its own reading names its three
seeds in the sentence a reader meets it in. Nothing there is unlabelled.

**Four commits closed it, all on `origin/main` and none of them this lane's:** `afc71ef24` (moved
`CURRENT_WORLD_NOISE_FLOOR_PATH` onto the nine-seed floor), `39065da9d`, `0c91d684a`, `7148b6260`.
The item offered two remedies — run a nine-seed current-world floor as a pair with its own arm, or
make the two n visibly distinct. A third was taken: move the floor constant **alone**, against a
comment that says moving either alone is the defect the pair exists to prevent, with the asymmetry
argued out in the constant's own block. That argument is sound and is not disturbed here.

`generate_value_arms_data.py`'s `today, at three seeds` comment was left alone, as instructed. It
still describes a field driven by a three-row floor.

---

## What the repair left, which is what this turn built

`CURRENT_WORLD_NOISE_FLOOR_PATH` moved and `CURRENT_WORLD_THREE_ARM_PATH` did not. So the floor is
produced by `c066c114b` and the arms it bounds by `04361d6c7`. **Two artefacts, two code trees, one
bound.** Re-measured here from the artefacts rather than taken from the comment that claims it:

| seed (shared by both floors) | `selection_gbp` under `04361d6c7` | under `c066c114b` | delta |
|---|---|---|---|
| 11111 | 1,199.550060 | 1,260.926200 | **+61.376** |
| 22222 | −3,075.215559 | −3,036.254411 | **+38.961** |
| 33333 | 433.071693 | 494.447833 | **+61.376** |

The trees also draw a different number of households: seed 11111 records 310 `elasticity_draws`
under the old tree and 295 under the new. **The constant's claim is confirmed on the artefacts.**

**And the same split is live on the OTHER pairing, which nothing had noticed.** `error_bar` bounds
`THREE_ARM_PATH` (`62334dc76`) with `NOISE_FLOOR_PATH` (`c066c114b`). Two cross-tree pairings, not
one — so this is a class, and it is fixed as one.

**Where that was admitted before this commit: a source comment.** Not the page. The band table's
own lead reads *"Nothing about the company changed between the rows of each family below — same
book, same code, same world"*. That is TRUE of the family's rows among themselves and it sits
directly above a **Published draw** column that is not a member of that family and, since
2026-09-09, is not from that tree either.

### The question none of the seven guards asked

`_current_world_bound` gates on five things and its own docstring says what they share: *"every one
of them is about the DENOMINATOR's provenance"* — this world, this leg, this contrast, a real
timestamp, real seed rows. `_staleness_caveat` asks whether the two runs were contemporaneous.
`_floor_admission` asks whether they were drawn over the same book. **None of the seven asks
whether they were drawn by the same code**, and no diff of the two artefacts can supply it: both
sides of that diff are outputs and the question is about the tree. `_producing_commit` already asks
exactly this question of the artefact against the *publishing* tree, and says so on the surface when
they differ. It was never asked of the two artefacts that get divided into a verdict.

### What is on the page now

`_floor_tree_pairing(floor, three_arm)` — one function, both pairings, published as
`error_bar.floor_tree_pairing` and `current_world.bound_tree_pairing`, rendered under the error-bar
caveat stack and under the re-draw band table. Live text today, on both:

> THIS SPREAD AND THE FIGURE IT BOUNDS WERE DRAWN BY DIFFERENT CODE: the floor at c066c114b, the
> run it bounds at 04361d6c7. Neither is thereby wrong and both name the same world — what is not
> true of them is that the width below and the number beside it are two readings of one tree.

**Rendered unconditionally, on all three branches**, following the rule `_floor_admission`'s render
already states: a reader told nothing when the trees match cannot tell that silence from the page
never having asked. Muted when they match, amber when they do not or cannot be told.

**Published ONCE per block, not once per leg.** All three legs share one floor and one arms run, so
the answer is one answer; three copies is the shape `_the_legs_own_regions` refuses.

**It does not size the difference, and the refusal is deliberate.** The +38.96..+61.38 above was
measured by comparing two floors that happen to share three seeds. The page has one floor in hand,
and the superseded floor it can see is read for its date and its world and *never* for a number. A
width derived from whichever second artefact was on disk would be a bound that moves when an
unrelated file lands. So the page states that the width and the figure are not two readings of one
tree, names both trees, and says what would remove the difference — re-running the arms under the
floor's tree — rather than publishing an estimate of it.

**Keyed to the property.** Nothing asserts today's pair is split. The day the arms are re-run under
the floor's tree this goes quiet with nobody editing a string.

### The controls, and the poison round that came first

Ten producer controls and two door controls. Every branch proven reachable **before** the mutation
battery, because *survived* means two opposite things.

| mutation | reds |
|---|---|
| `same_tree` always `False` | 2 (incl. the partition control) |
| unstamped defaults to a match (the fail-open) | 2 |
| `caveat` never published | 2 |
| `current_world` wiring dropped | 1 |
| `error_bar` wiring dropped | 1 |
| the two commits not named in the sentence | 1 |
| **page:** band-table render dropped | 2 |
| **page:** error-bar render dropped | 2 |
| **page:** amber → muted on the split branch (styling only) | 1 |
| **page:** caveat dropped from the band render | 1 |

The wiring control is separate from the arithmetic ones on purpose: every direct-call control is
blind to whether `build()` reaches the function, which is the exact shape that let
`_floor_admission`'s producer-side answer sit built-and-unwired while the defect stayed live.
It builds through `build()` with all four artefacts — the `real` fixture omits the two current-world
ones, so its `current_world` is an **absence**, and a wiring control run against it would have been
green on the day the block was unavailable and every day after.

---

## One thing this commit carries that it did not cause, said here rather than left to be found

Regenerating the feed at HEAD also moved `realised.is_the_published_supplier` from a stated
divergence to a **withheld claim**:

> This feed cannot say whether the baseline arm is the supplier the site publishes. The run
> artefact it reads reports £131,289.34 and the figure the site actually publishes for the company
> reports £147,886.78 — a gap of £16,597.44 — so the two are not the same run and the claim is
> withheld rather than answered from whichever one is nearer.

**That is not this change.** `docs/reports/run_output_latest.json` moved at `fe895db3a`, after
`7148b6260` last regenerated the feed, so the committed feed was already stale against HEAD's own
artefacts and any regeneration surfaces it. The new state is the honest one — it fails closed and
names the gap — but a £16.6k gap between the run this feed reads and the figure the site publishes
for the company **is its own finding and is not closed by this commit.**

---

## What is next

1. **The £16,597.44 gap above.** Two artefacts claiming to be the company's net margin. Nothing
   here establishes which is the company's, and the page correctly refuses to choose.
2. **Sizing the tree difference honestly**, which needs the arms re-run under the floor's tree —
   at which point the pair moves together again and both this disclosure and the asymmetry
   paragraph in the constant block go quiet on their own.
3. The selection sign is **not** settled by any of this and no seed count on this machine will
   settle it. **Do not commission the 116-seed run** — that stands from the document this one
   follows.

---

*Filed beside the result whose correction 2 commissioned the drawn item. The premise is graded
spent on measurement, not on the draw-time git check.*
