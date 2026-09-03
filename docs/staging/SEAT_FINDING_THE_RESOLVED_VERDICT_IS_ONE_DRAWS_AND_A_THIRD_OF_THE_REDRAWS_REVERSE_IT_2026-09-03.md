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
