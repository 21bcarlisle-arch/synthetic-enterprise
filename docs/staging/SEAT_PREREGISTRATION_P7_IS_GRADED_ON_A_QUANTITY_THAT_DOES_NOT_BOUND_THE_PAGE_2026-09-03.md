**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# P7 is graded on a quantity that does not bound the page, and on the right one it flips

*Delivery seat, 2026-09-03 17:46 BST, claim `pick-up-the-relaunched-undecomposed-floor-leg`.
Filed while `se-floor-all-20260903c` is still running and has written nothing — the artefact does not
exist, and none of the figures this predicts are in hand.*

---

## 1. Measured, from artefacts already on disk

`SEAT_PREREGISTRATION_WHAT_THE_UNDECOMPOSED_FLOOR_LEG_MUST_RETURN_IN_THE_LIVE_WORLD_2026-09-03.md`
grades P7 like this:

> The live-world `value_advantage_gbp` is **£2,335.87**. Against a live-world floor near £5,923 that
> is 0.39× — comfortably inside. **Predicted:** `selection_distinguishable_from_zero` stays **false**.

£5,923.04 is the floor's published `selection_gbp_spread.stdev`. **It is not what bounds the page.**
`_current_world_bound` takes its bound from `_spread_for(_seed_spreads(...), PAGE_FIGURE_CONTRAST)`,
and `PAGE_FIGURE_CONTRAST` is `value_advantage_gbp` — the contrast's *own* spread across the seed
rows, derived from them because the producer publishes a spread block for only one of the three.
On the live-world `only` leg those two numbers are:

| contrast | spread across the same 3 seed rows |
|---|---|
| `selection_gbp` (published as `selection_gbp_spread`, and P7's divisor) | **5,923.0446** |
| `value_advantage_gbp` (`PAGE_FIGURE_CONTRAST`, and the actual bound) | **991.4551** |
| `level_advantage_gbp` | 5,167.8795 |

**5.97× apart.** `_current_world_bound`'s own docstring names this exact substitution as the thing it
was written to stop — *"Pairing it with the floor's published `selection_gbp_spread` … would divide
two numbers that count different things: on the 2026-08-29 family they differ by 2.6x … That pairing
was written into this claim's own pre-registration as the support for a prediction, which is how
cheap it is to make."* It has now been written into the successor pre-registration, supporting P7.
On this seed family the gap is not 2.6× but 5.97×, and it is in the direction that matters.

The sibling document half-caught it. Its §2 says £2,335.87 over £5,923.04 *"would* be a quantity —
but it is the wrong leg". The leg objection is right and the quantity objection is the one it
missed: it is **both** the wrong leg **and** the wrong contrast, and only the second changes the
answer.

P7 also names `selection_distinguishable_from_zero` as its verdict key. That is the *producer's*
key in `tools/run_value_cycle_ab.py`, about `selection_gbp`. The page's verdict is `resolved` in
`_current_world_contrast`, about `value_advantage_gbp`. Three quantities are in play and P7 names a
different one in each of its three sentences.

## 2. Why the undecomposed leg should reproduce £991.46 — the mechanism, measured

The `except` leg returns **zero** variance on `value_advantage_gbp`, not merely on `selection_gbp`:

    seed 11111  value_advantage_gbp  2756.4088749999937
    seed 22222  value_advantage_gbp  2756.4088749999937
    seed 33333  value_advantage_gbp  2756.4088749999937   -> stdev 0.0

That is P6's premise holding for the page's own contrast. The unpriced side contributes no variance
to `value_advantage_gbp` either, so the undecomposed leg has nothing to add to the priced one.

## 3. The predictions, filed before the artefact exists

> **P9 — the undecomposed leg's bound is ~£991, not ~£5,923.**
> **Predicted:** `_spread_for(_seed_spreads(all_leg, three_arm), "value_advantage_gbp")["stdev_gbp"]`
> = **991.4551 ± 5%**, while the same artefact's published `selection_gbp_spread.stdev` is ~5,923.
> **Refuted if:** it lands outside 942–1,041, or if the two figures come back equal — which would
> mean `_seed_spreads` is not deriving per-contrast spreads at all and the bound is the published
> scalar under another name.

> **P10 — the page RESOLVES, and P7 is refuted.**
> `_resolvable` is `abs(value) > spread["stdev_gbp"]`. With the live `value_advantage_gbp` of
> **£2,335.8676** against a bound of **£991.4551**, that is `2335.87 > 991.46` → **True**, a ratio
> of **2.36×**, outside rather than comfortably inside.
> **Predicted:** `_current_world_contrast(...)["resolved"]` is **`True`** once the undecomposed leg
> is on the page. Act (d) is therefore *"update the `/capabilities/` headline to the live-world pair
> and bound"*, **not** *"state plainly that the floor still contains the contrast"*.
> **Refuted if:** `resolved` comes back `False` or `None`. `None` would mean a guard in
> `_current_world_bound` still refuses the artefact and the bound never forms — a plumbing failure,
> not a world result, and it must be reported as such rather than as P10 being wrong about the world.

**P9 and P10 are blind with respect to the running leg.** The leg-B journal that makes P8 a
retrodiction printed `selection_gbp` seed values only; no `value_advantage_gbp` seed row from any
`all`-mode run has been observed. These are derived from the decomposition's structure, not read off
a console.

## 4. What must NOT be done with this

**No figure here may be published.** §1 and §2 are computed from the `only` and `except` legs, which
`_current_world_bound` refuses for the page and rightly so. The point of §1 is *which quantity to
divide by*, which is a fact about the instrument; the point of §3 is a prediction. **The grading
still requires this run's artefact and the three-field paste the sibling document specifies** —
`redraw_scope.mode` = `all`, `generated_at` after 16:07 BST today, and the `--out` path — before any
number is read from it. Quoting £991.46 as the live-world bound because it is the one computable
today is the same move as quoting the old world's floor because it is the one on disk.

**The £991.46 bound is not a licence to restate the advantage as a larger claim.** The advantage
itself collapsed from £12,071 to £2,336 between worlds. A resolved verdict says the figure clears
its own draw noise; it says nothing about the figure being large, durable, or the same figure that
was published on 2026-08-31.

**And `resolved: True` on n=3 deserves the reader's caution on the surface.** `_resolvable` compares
a single draw's value against one standard deviation of three re-draws — roughly a one-sigma test,
reported as "distinguishable from zero". The floor's own `value_advantage_gbp` mean is £1,030.10,
not £0, so the floor is not a clean null either. Filed separately as
`SEAT_FINDING_THE_RESOLVED_VERDICT_IS_A_ONE_SIGMA_TEST_ON_THREE_SEEDS_2026-09-03.md`; it does not
change P10, which predicts what the code will do, and it does change what the page should be allowed
to say about it.

**Discharged:** not yet.
