**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The world can punish bad service but barely reward good, and which households are eligible for the reward is decided by the sign of a hash

**Found:** 2026-08-30, while measuring the five churn factors ahead of C2 (competing-risks
departures) — a factor that does not vary across the population contributes a constant hazard, so
its "cause share" would be meaningless, and each factor's realised variation had to be measured
before the decomposition was designed.

**Not a claim that any published figure is wrong.** It is a claim about what the world can express,
and it bears directly on the brief of 2026-08-30, which names customer service as the published
SECOND axis of the switching decision.

## The mechanism

`simulation/satisfaction_churn.satisfaction_churn_multiplier` is a three-band step on a 0–1 score:

```
score >= 0.80  ->  x0.85   (protective)
score <  0.50  ->  x1.30   (punitive)
otherwise      ->  x1.00
```

The best/worst spread is **x1.53**, which is a reasonable match to the published per-household
satisfaction spread of 1.46x — the function is well shaped. The problem is which parts of it the
world can reach.

`simulation/sim_satisfaction.sim_satisfaction_score` builds the score as

```
0.70 baseline
  + bill_shock_count x (-0.10)
  + income stress    (0.0 / -0.05 / -0.15)
  + min(tenure_years x 0.02, +0.10)
  + payment channel  (DD 0.0 / standard credit -0.06)
  + individual variation, +/-0.04, from sha256(customer_id)
```

**Every term except tenure and the variation is zero or negative.** The ceiling is therefore
`0.70 + 0.10 + 0.04 = 0.84`, and reaching the protective band at 0.80 requires *simultaneously*
zero bill shocks, maximum tenure (5+ years), low income stress, direct debit, **and** a
non-negative variation term.

## Measured, on the live book

Swept the full input space — 150 live electricity accounts × bill shocks 0–3 × tenure
{0, 2, 5, 9} years × every income-stress level × both payment channels = 19,200 combinations:

| band | combinations | share |
|---|---|---|
| x0.85 protective | 308 | **1.60%** |
| x1.00 neutral | 10,936 | 56.96% |
| x1.30 punitive | 7,956 | 41.44% |

**So satisfaction is a two-state variable in practice: neutral or punitive.** The world can punish
a supplier for bad service and can essentially not reward it for good service.

## The part that is a modelling artefact rather than a fidelity choice

**77 of 150 accounts can EVER reach the protective band. The other 73 cannot, at any tenure, with
any bill history, on any payment method.**

The gate is exact and it is not about the household. Reaching 0.80 requires
`0.70 + 0.10 + variation >= 0.80`, i.e. `variation >= 0`. The eligible set is precisely the
accounts whose `sha256("satisfaction_variation_" + customer_id)` lands in the top half of its
range — **the sign of a hash of the customer id.**

The variation term is not the villain and its own comment is honest about what it is: ±0.04 is *"an
honestly-flagged CALIBRATION CHOICE, not a directly published per-customer standard deviation"*,
added because every customer in the same circumstance cohort previously got an identical score. It
was the right addition. What nobody checked is that its magnitude is the same size as the gap
between the score's ceiling and a behavioural threshold — so a term meant to add texture *within*
bands silently became the gatekeeper *of* a band.

**This is the class where a control keyed to the property would have caught it and a control keyed
to today's answer would not:** every existing test of these two modules asserts the multiplier for
a given score, and the score for a given input. None asks whether the composition can reach its own
thresholds.

## Why it matters, and why it is not fixed here

The brief of 2026-08-30 puts customer service at 32% of the switching decision, second only to
price, with the largest published per-household spread anywhere in that research (1.46x). Service
is also one of the few axes a supplier can both OBSERVE (its own failures) and ACT on — which makes
it, per `WHAT_A_HOUSEHOLD_DECIDES_ON.md` §5 S3, one of the few places genuine inference advantage
could come from.

A world that cannot reward good service systematically understates the return on the company's own
service investment. That biases against the company, so it is not urgent in the R13 sense — but it
is exactly the wrong bias for a project whose thesis is that the company creates value rather than
transferring it.

**Direct consequence for C2**, which is why this was found: with satisfaction effectively
one-sided, a competing-risks decomposition would attribute service-driven departures fairly but
would show service as almost never PREVENTING one. The reason mix would be right about departures
and silent about retention. Recorded in the C2 pre-registration as a known bias in P2 rather than
discovered afterwards in the result.

## What is owed, and the choice inside it

Two candidate repairs, and they are not equivalent:

1. **Raise the ceiling** — a positive term for something (no shocks for N years, a resolved
   complaint, a service recovery). Makes the protective band genuinely reachable and gives the
   company a lever. This is the one that matches the published evidence.
2. **Lower the threshold** — move 0.80 down until the existing ceiling clears it. Cheaper, and it
   would make the band reachable while leaving the score with no way to express "delighted".

**Recommendation: (1).** (2) would produce a green measurement of a world that still cannot
represent a satisfied customer — the shape this project calls a control pinned to today's answer.

Either way the repair moves a simulated output, so it needs a pre-registration and a one-variable
run. It is NOT done here (SELF_INTERRUPT_DISCIPLINE): it was found while measuring inputs for a
different piece of work, and a fidelity change to the churn chain made on the way past is exactly
what R13 exists to stop.

## A correction to my own working, recorded because it nearly became the finding

The first sweep passed satisfaction scores of 1.0 through 10.0 and got `x0.85` for every one,
which reads as *"satisfaction has no effect at all"* — a much bigger and more alarming claim. The
score is on a **0–1** scale, so every one of those inputs was above the 0.80 threshold and the
constant answer was correct behaviour on nonsense input. The real finding is narrower and duller
than the one I nearly filed, and it is the real one.

## The falsifier this is owed

None yet, and that is deliberate — a control asserting "the protective band is reachable" pins
today's answer, and a control asserting "the score's maximum exceeds its highest threshold" is the
property. The second is what the repair should ship, keyed to the composition rather than to any
particular constant, so that lowering the ceiling or raising the threshold in future reds it.
