**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — what the paired size-term floor will say, written before it is run

*Lane 0 delivery, 2026-09-23. Drawn item:
`the-arms-delta-needs-a-noise-floor-before-634-pounds-means-anything`. Written BEFORE any seed of
the paired family had run, because a prediction filed after the answer is not a prediction.*

## The question, and the ruler it needs

`fc390b918` published a table comparing the churn belief **blind** to household size against the
same belief **seeing** it, one seed each:

| | blind | seeing | move |
|---|---|---|---|
| net margin advantage | £14,074 | £13,440 | **−£634** |
| gross margin advantage | −£9,299 | +£12,152 | +£21,450 |
| enterprise value advantage | £6,143 | £7,642 | +£1,499 |
| bad debt | −£7,508 | −£3 | +£7,505 |

and refused to call the −£634 a change. That refusal was correct and unevidenced: no floor existed
for it. This run supplies the floor.

**The ruler has to be PAIRED, and the ruler already on disk is not.** Every floor artefact in
`docs/observability/` measures the spread of `value_advantage_gbp` across seeds *within one
configuration* — the marginal noise on a single reading. Read off the carried columns, that is
£1,457–£3,453 of standard deviation across the `all`-mode families. But the −£634 is a **difference
of two readings taken at the same seed**, and the seed noise those two readings share cancels out of
it. Grading a paired contrast against a marginal spread is the wrong ruler, and it would
under-claim: it would call £634 unresolvable by arithmetic that never looked at the pairing.

So the instrument is: the same seed list, both configurations, and the spread of the **per-seed
difference** `d_s = X_seeing(s) − X_blind(s)` for every row of `realised_delta`.

## The one variable, and how it is switched

Not two trees. One tree, one rebind: `company.crm.churn_model.SIZE_REFERENCE_KWH_ELEC` and
`SIZE_REFERENCE_KWH_GAS` set to `0.0`, which drives the guard
`segment == "resi" and annual_consumption_kwh > 0 and size_reference_kwh > 0` to its `else` branch
and hands every household `size_scale = 1.0` — which is exactly what blind means, and exactly what
the pre-`fc390b918` tree did. This is a cleaner one-variable switch than the published comparison,
which moved a whole commit (two test files and a docstring correction rode with it).

**The rebind must be OBSERVED TO BITE, per leg, or the run raises.** The two reference constants are
rebound to a `float` subclass that counts its own `>` comparisons and records the ratios taken
against it. Because the guard short-circuits, a counted comparison is exactly a call where the size
term *would* have applied. On the blind leg a count of zero means the rebind reached no call site,
the two legs ran the same world, and the "floor" would read zero — the most flattering answer
available and a measurement of nothing. On the seeing leg, fewer than two distinct scale values
means the belief is flat across this book and there is again no contrast. Both raise.

This witness sits INSIDE the mechanism rather than wrapping `estimate_churn_probability`, because
five modules bind that name with `from ... import` and a wrapper on the module attribute would miss
them and read zero for the flattering reason.

The re-drawn quantity is `churn_roll` — the renewal dice every billing account takes, priced or not.
It is keyed `Random("floor{seed}_{account}_{term}")`, so the same account at the same term gets the
**same roll under both configurations**: genuine common random numbers, which is what makes the
paired difference tighter than the marginal spread rather than merely a second name for it.

## What I predict, before running

1. **The net-margin difference will not clear its own bar.** `mean(d_net)` will sit inside
   `t(n−1) × sd(d_net)/√n`. I expect `|mean(d_net)|` under £2,000 and `sd(d_net)` over £2,000.
   *Confidence: high — this is the prediction the commit's own refusal already implies.*

2. **The gross-margin difference WILL clear its bar.** `mean(d_gross)` should land near the
   published +£21,450 and be several sems from zero. If it does not, the composition claim
   `fc390b918` made — "the arm stopped winning by avoiding bad customers and started winning on
   gross margin" — is itself one seed and must be withdrawn with the same words the headline got.
   *Confidence: moderate. This is the prediction most worth being wrong about.*

3. **Pairing will buy a real reduction: `sd(d_net) < √2 × sd(VA)` on the marginal families**, i.e.
   under about £3,000–£4,900. *Confidence: low.* The size term changes the churn belief, which
   changes prices, which changes who stays — so the two legs' books diverge and much of the common
   randomness is destroyed downstream. It is entirely possible that `sd(d_net)` is as large as, or
   larger than, the marginal sd. **If it is, that is the finding**: the pairing that made the
   published comparison look like a clean one-variable read does not survive the arm's own feedback,
   and no seed budget closes the £634.

4. **The sign of `d_net` will not be stable across seeds.** I predict at least 3 of any 10 seeds
   flip the sign of the net-margin move. *Confidence: moderate-high.*

5. **The blind leg at the base (unpatched) roll will reproduce £14,074 and the seeing leg £13,440**,
   within rounding. *Confidence: moderate.* If it does not, my rebind is not the switch the commit
   made, and everything above measures a different contrast — this is the reconciliation leg and it
   runs first, before any seed.

## What done means

Not "a number". Done is: an artefact carrying, per row of `realised_delta`, the paired mean, sd,
sems-from-zero and the bar its own family size earns, with the witness counts beside it; the
published one-seed move set against it; and a plain statement of which of the four rows in
`fc390b918`'s table this book can resolve and which it cannot. Written incrementally so a killed
run leaves usable seeds.

**If the family is too small to state a sign on any row, that is the answer** and it gets published
as the answer. It is not a cue to re-run until a seed agrees.
