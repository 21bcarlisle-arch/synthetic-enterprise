**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The `resolved` verdict is one draw's, and a third of the re-draws reverse it

*Delivery seat, 2026-09-03. Found by grading P8/P9 in
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_LIVE_WORLD_BOUND_MAKES_THE_PAGE_SAY_2026-09-03.md`
the hour the undecomposed floor leg landed and the resolved branch executed against real data for
the first time in its life.*

---

## What is wrong

`_resolvable(value, spread)` returns `abs(value) > spread["stdev_gbp"]`. On the live world it is
handed:

- **value** = £2,335.87 — `value_advantage_gbp` from the current-world three-arm run
  (`producing_commit` `ace28fa44`), which used its own single elasticity draw.
- **stdev** = £991.46 — the standard deviation of `value_advantage_gbp` across the floor's three
  seed re-draws of *the same quantity*.

Both figures are correct and they are keyed to the same contrast, which is the defect this wiring
was built to avoid. The remaining problem is one layer up: **the numerator is a single realisation
and the denominator is the dispersion of realisations.** That comparison does not answer "is this
figure distinguishable from zero"; it answers "did this particular draw land more than one spread
from zero", and the answer moves with the seed.

Substituting each floor seed's own value for the point estimate, against the same £991.46 bound:

| seed | `value_advantage_gbp` | `resolved` |
|---|---:|---|
| 11111 | 1,467.23 | True |
| 22222 | 2,433.70 | True |
| 33333 | **450.99** | **False** |
| *mean of the three* | 1,450.64 | True |

**One of the three re-draws of the same quantity reverses the published verdict.** The page states
`resolved: True` with no indication that it is a property of which draw the three-arm run happened
to make. £2,335.87 is not the central estimate of this quantity — the re-draws put that at
**£1,450.64**, 38% lower, and the published point sits second-highest of the four draws in hand.

Taken as an inference about the mean: SEM = 991.46/√3 = £572.42, t = 2.53 on 2 degrees of freedom.
That clears no conventional threshold. The page's rule and a conventional test disagree, and only
the page's rule is published.

## Why it is not merely conservative

The instinct is that `abs(value) > stdev` is a weak-but-safe bar. It is not safe in the direction
that matters here. It is a **~1σ** bar where the published claim reads as settled, and it is applied
to a *draw* rather than an *estimate*, so its error rate is not the one a reader would assume from
seeing a bound printed beside a figure. It fails toward the flattering answer precisely when the
point-estimate run drew high — which is the case on this page right now.

The pre-registration anticipated the shape of this risk and named the guard against it: *"A result
that moves the advantage the flattering way, unpredicted, is a defect in the re-run and not a win."*
`resolved: True` was predicted (P9 is confirmed), so this is not that defect. But P9 predicted the
verdict, not the verdict's stability, and the stability is what a reader takes from it.

## What makes it invisible

Every control on this block asks whether the bound is the **right** bound — right world, right leg,
right contrast, real timestamp, real seed rows. Five guards, each mutation-proven, and all five are
about the denominator's provenance. **Nothing asks what the numerator is**, so a correct bound
correctly attached to a single draw passes every one of them. The controls were built during the
period when the branch was unreachable, which meant no real numerator had ever passed through them
to make the question concrete.

## The repair, and why it is not in the commit that files this

Three candidate fixes, and choosing between them is a design decision, not a wiring one:

1. **Compare the mean of the re-draws to its own standard error** — the conventional reading, and it
   would flip this page to unresolved.
2. **Publish the point estimate with the re-draw range beside it** (£451–£2,434) and state no binary
   verdict — consistent with "fail closed and say so on the surface".
3. **Keep `abs(value) > stdev` but say on the page that the verdict is one draw's**, and print the
   re-draw spread that reverses it.

`_resolvable` is shared by every contrast this page publishes, not just the current-world block, so
changing its semantics moves figures that are not the subject of this finding and that no
pre-registration currently covers. Doing it inside this tick would be the change nobody predicted,
on the page whose whole discipline is predicting before measuring.

**Recommendation, to be actioned next rather than asked about:** option 2 for the current-world
block, because it is the only one that does not require deciding what the right test is in order to
stop publishing the wrong one. The range is already computed and already in the payload as
`bound.min_gbp`/`bound.max_gbp`.

## What would discharge this

A control whose subject is a floor whose seed rows straddle the bound — where the published point
estimate resolves and the re-draw mean does not — asserting that the page does not state a bare
`resolved: True` off it. The live artefacts are that subject: `value_advantage_gbp` on
`value_cycle_ab_s1_noise_floor_20260903.json` straddles £991.46 at seed 33333 already, so this needs
no new compute leg.

---

## Actioned 2026-09-03 — option 2, scoped to the current-world block

**Discharged:** `tests/tools/test_generate_value_arms_data.py::test_the_verdict_is_withheld_when_the_floors_own_redraws_reverse_it`, `tests/tools/test_generate_value_arms_data.py::test_MUTATION_the_stability_guard_fails_on_its_own_witness_and_only_there`, `site/test_the_baseline_comparison_reaches_the_reader.py::test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved` — the page no longer states a verdict its own floor's re-draws reverse, and the range that reverses it is in the headline.

`_verdict_stability` re-asks the page's own rule of each seed's value through `_resolvable` — the
same function that decides the published verdict, never a second implementation of it — and a split
withholds in either direction. `_resolvable` itself is unchanged and its five other call sites are
untouched, so no figure outside this block moved; that was pre-registered as P5 and graded in
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_WITHHOLDING_THE_ONE_DRAW_VERDICT_DOES_TO_THE_PAGE_2026-09-03.md`.

**The third state is named, not folded in.** `resolved: None` previously meant only "no bound was
read". It can now mean two things, so the withheld case keeps `bound_available: true` and carries
`verdict_withheld_because`; three states a reader can tell apart, which is the conflation this file
refuses elsewhere.

**Two witnesses, because one is an equivalence.** The straddling floor alone is satisfied by a
function that withholds unconditionally. The unanimous floor is the sole witness that the
withholding is a judgement — and it is the mutation that would otherwise have survived.

**What this does NOT do.** It does not settle whether the advantage is real; it stops the page
claiming it is. Whether n=3 is enough seeds to state any verdict is untouched and is the next
measurement — the "what would refute the whole approach" section above stands open.

---

## Closed 2026-09-03 — verified at the reader's end, not at the commit's

The section above was written the hour the repair landed, so its evidence was the tree's. The
repair was re-verified from the consumer's side before this file was archived, because a landed
generator is not a published page: the preceding commit in this lane records the publish daemon
regenerating the page from the shared tree, which is exactly how a correct fix stays unpublished.

- **The generator's fix is on `origin/main`,** not merely local — HEAD is an ancestor of
  `origin/main` and the withholding branch is present in `origin/main`'s own copy of the file.
- **The live site serves the withheld verdict.** `https://poesys.net/data/value_arms.json` fetched
  200 and its `current_world` carries `resolved: null` with the reason and the range, against
  `bound.min_gbp` £450.99 under `stdev_gbp` £991.46. The flattering `true` is gone from what a
  reader actually receives, which is the claim this finding made and the only place it could be
  settled.
- **The rendered door agrees with the feed.** The site control drives the real page through
  `site/_live_harness.mjs` and passes on the withholding branch, so "states no verdict" and both
  re-draw edges reach the DOM — not just the JSON. A grep of the markup would have been blind to
  this, since the page composes the sentence at runtime.
- **The scope constraint held.** `_resolvable` is untouched by the repair commit — its body is
  still the bare `abs(value) > stdev` with the strict-inequality note — so the five other contrasts
  it gates did not move, and no figure outside this block changed without a prediction covering it.

**Why this is archived and not left open.** What remains in this file is a measurement question
(is n=3 enough seeds to state any verdict at all), not an unactioned repair. It is a different
subject from the defect recorded here, which was that the page stated a binary verdict its own
floor's re-draws reverse. That defect is fixed, published and controlled. Leaving the document in
the queue root to carry the open measurement would re-offer the finished repair on every tick —
the shape where a landed disposition is re-drawn indefinitely because the document specifying it
was never discharged. The open question is handed on separately.

---

## Re-verified 2026-09-03 23:41 UTC — the CENTRE, which the closure above does not cover

The section above is sound and its evidence stands, but it attests a **narrower** claim than a
reader of this file would take from it, and the gap is a matter of clock rather than of judgement.
It was written at 21:41 UTC and its live-site bullet names the reason and the RANGE. The re-draw
MEAN did not exist then: it landed at 22:47 UTC in `a3fa61ef4`, an hour after this file was
archived, under its own pre-registration
(`docs/staging/records/SEAT_PREREGISTRATION_WHAT_PUBLISHING_THE_REDRAW_MEAN_MUST_AND_MUST_NOT_MOVE_2026-09-03.md`).
That pre-registration graded P1–P4 against the local door and the mutants; it did **not** re-fetch
the deployed feed, because publishing is a different lane's clock and the page had not regenerated
yet. So the centre — the half that places the surviving £2,336 inside its own family — was landed,
mutation-proven and locally rendered, and never once confirmed at the reader's end.

That is the project's most-repeated shape pointed at its own closure record: a landed generator is
not a published page, and a closure that says "verified at the reader's end" ages into a claim
about figures it never saw.

**Re-fetched now, from the deployed site, not from this tree.** `https://poesys.net/data/value_arms.json`
returned HTTP 200 (81,555 bytes). Its `current_world` carries:

| what a reader receives | value | covered by the 21:41 closure? |
|---|---|---|
| `resolved` | `null` | yes |
| `verdict_stability.redraw_min_gbp` / `max` | 450.99 / 2433.70 | yes |
| `verdict_stability.redraw_mean_gbp` | **1450.6408126666695** | **no — this row is the addition** |
| reason names £451 and £2,434 | present | yes |
| reason names **£1,451** | **present** | **no — this row is the addition** |
| reason names the placement **ABOVE** | **present** | **no — this row is the addition** |

So the centre reaches the reader, and the flattering reading one layer along — a withheld binary
above an unplaced point estimate — is closed on the deployed artefact and not merely in the tree.
The deployed feed's `generated_at` is still `2026-09-03T10:17:07Z` and its `producing_commit`
`ace28fa444c505db44984cdc8f94a4dff8636bbf`: the narrative sentence is composed by the generator and
served as a string in the feed, so the publish daemon regenerating from the shared tree is what
carries it, and the shared tree is at `24b7dc6c1`, which has `a3fa61ef4` as an ancestor and whose
own copy of `tools/generate_value_arms_data.py` contains `redraw_mean_gbp`. Landed, regenerated,
served, and now read back.

**Nothing was rebuilt to establish this.** The repair, both controls and the discharge were already
correct; this section adds only the measurement the closure could not have made because its subject
did not exist yet. Recorded beside the original closure rather than by editing it, because a closure
silently widened after the fact is not evidence that it was verified — it is evidence that someone
later wished it had been.
