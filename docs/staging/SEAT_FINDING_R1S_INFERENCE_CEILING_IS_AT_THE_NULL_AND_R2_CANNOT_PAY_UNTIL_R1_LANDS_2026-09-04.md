**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** PB4_engagement_separated_from_elasticity

# R1's inference ceiling sits at its own null, and R2 cannot pay until R1 lands

**Found:** 2026-09-04, delivery seat, on the director's instruction to re-rank against
`DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04` and *"take the ceiling measurement before the build,
as you did on EP13."* Measured with `tools/r1_inference_ceiling.py`, written for this question.

---

## The question

The canon's R1 claim is that a household's price sensitivity is **structurally unlearnable** — the
trait reaches the world only where it sets the outcome, so no supplier could recover it. R2 (widening
the decision surface: richer dunning, per-customer acquisition, a wider retention surface) is a
programme that only pays if there is something to condition on.

So: **how much of a household's true elasticity could ANY model recover from the company's own
observables?** Not the model we have — the best possible one.

## The measurement

The best possible function of a coordinate IS the per-cell mean of the target, so the ceiling needs
no estimator and cannot be beaten by one. Fit on even-indexed households, scored on odd. Ground truth
is `price_elasticity_for_customer(customer_id, base_seed)` at the seed the book was actually drawn
at — never the module default, which would give random labels, a ceiling of zero, and a false
confirmation of exactly the claim under test.

```
feature (all households carrying it)      n     held-out   in-sample   null(max/48)  verdict
mean_recent_margin_rate                 214     +0.0874     +0.1840       +0.1829    noise
portfolio_premium_pct                   214     +0.1506     +0.1280       +0.2057    noise
unit_rate_gbp_per_mwh                   102     REFUSED -- degenerate fit
svt_rate_gbp_per_mwh                     71     -0.1594     +0.2086       +0.3479    noise
rate_vs_svt_pct                          71     +0.2619     +0.1053       +0.3775    noise
company_eac_kwh                          71     -0.0558     +0.1324       +0.2320    noise
company_churn_estimate                   71     +0.4581     +0.1197       +0.4980    noise
resentment_score                         71     REFUSED -- degenerate fit
perceived_bill_saving_gbp                71     +0.4291     +0.1566       +0.3163    CLEARS
expected_term_margin_gbp                 64     -0.0521     +0.1932       +0.3989    noise
discount_pct                             45     REFUSED -- degenerate fit

AT FULL COVERAGE (n=214), anything clears the null:  False
```

**The verdict is taken at full coverage only, because that is the only place this book has the power
to tell a ceiling from its own noise floor.** Both features present on all 214 households come out
below their own null. R1's claim survives the measurement.

## The three ways this measurement nearly lied, all caught, all now controls

This is recorded at length because each one produced a confident wrong headline first, and the third
is the one I would not have caught by thinking harder.

1. **A rotation is not a shuffle.** The first null was `ts[n//2:] + ts[:n//2]`, which preserves the
   ordering the features may themselves be ordered by. And it was ONE draw — one sample, not a
   floor. Fixed to 12–48 seeded permutations taken at their maximum, because the quantity a ceiling
   must clear is how high chance REACHES.

2. **Four households per cell is not a population.** At 4×4 cells the instrument reported a ceiling
   of +0.5125 and I nearly filed it. `cells_are_populations` now refuses that resolution.

3. **Held-out above in-sample is the tell, and it was in every row.** A fit cannot genuinely score
   better on data it never saw. At n=71 every pair showed it (+0.57 held-out against +0.17
   in-sample). That signature — not any single figure — is what says the 2-D pair measurement is
   noise, and it is why the verdict is drawn from the 1-D full-coverage rung instead. A pair costs
   every household missing either field: 214 become 71, and at 71 the noise floor (+0.50) sits at
   the level of the best result (+0.57).

A fourth, smaller: three observables scored exactly `0.0000`, and my first guard for it — *refuse a
feature whose spread is zero* — **fired never**, because none of them is constant. They are SKEWED:
an outlier sets the upper bin edge, every remaining household falls in the lower bin, the predictor
emits one value and `_corr` divides by a zero deviation. A silent `0.0` reads exactly like "measured,
found nothing", which is a different claim. The guard is now keyed to the degenerate FIT — the actual
failure — rather than to the constant feature, which was my guess at it.

## What this says about the order of work

**It confirms the map's existing block reason rather than overturning it.**
`C29_decisions_stop_being_lookup_tables` (R2's headline atom) is blocked on the R1 atoms with the
reason already measured: *"a decision surface widened against a flat world produces a better-
instrumented null ... the choosing is worth -£175."* This measurement says why, from the other side:
there is no signal in the observables for a widened surface to condition on, so widening it buys a
more expensive way to reach the same answer.

**So R1 and R2 are one programme, and R1 is the half that has to land first** — not as sequencing
preference but because R2's payoff is bounded by this number, and this number is at the floor. The
build R1 needs is the one that makes households differ *for reasons a supplier could in principle
observe*: an elasticity with observable antecedents, rather than a hash of the customer id.

## What it does NOT say

It does not say elasticity is unlearnable in general — it says it is unlearnable **from these eleven
observables on this book**. Nine of the eleven are carried by 102 households or fewer, and at those
sample sizes this instrument cannot tell a real +0.26 from its own +0.38 null. A book with more
households, or those fields populated on all of them, could move the answer and this instrument
would detect it.

It also does not license reporting the R1 atoms as understood. The ceiling bounds what a supplier
could recover; it says nothing about whether the elasticity the world uses is the right one.

## What would close this

An R1 build that gives elasticity observable antecedents, followed by a re-run of
`tools/r1_inference_ceiling.py` on a book drawn after it. The instrument is the falsifier: if the
build works, full-coverage features clear the null; if it does not, they will not, and the same
verdict line will say so.

Not written as a **Discharged:** field, deliberately — that field is a claim the repair has landed.
