**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `A48_enterprise_value_is_the_method_not_the_book`

# The method's first live number is 0.614, and a random signal reaches that one time in six

`A48`'s estimator landed at L2 (`69a0bb068`) with twelve R15 proofs on fixtures and **had never
produced a number on a real run**. It has now. The number needs its bound published beside it, and
the bound was missing.

## The first live reading

`tools/run_value_cycle_ab --level-arm`, full window, 2026-08-28T12:37:02Z:

| | |
|---|---|
| **method-skill concordance** | **0.6136** |
| null (a constant signal, same code path) | 0.5000 |
| decisions scored | **12** |
| accounts | **5** |
| comparable pairs | 66 |
| pairs tied on the outcome | 0 |
| churn `discrimination_auc`, for contrast | 0.4653 |

The pair is the reading the estimator was built for, and it is genuinely interesting: **the arm's
own price ranks jointly-created value better than chance (0.614) while its belief about who leaves
ranks worse than a coin flip (0.465).** Two different questions, opposite sides of 0.5.

## And the bound, which changes what may be said

The published null was the point 0.5 — correct as a definition, and silent about sampling.
Concordance is Kendall's tau rescaled, so the null has a known spread at n untied items:

```
Var(tau) = 2(2n + 5) / (9 n (n - 1))        n = 12  ->  sd(concordance) = 0.1105
```

Cross-checked against a **200,000-draw permutation** of the actual 66-pair set: permuted sd
**0.1103**, analytic **0.1105**.

| | |
|---|---|
| null 95% central interval | **0.283 to 0.717** |
| observed | **0.614 — inside it** |
| z | 1.03 |
| p (two-sided, normal approx) | **0.30** (permutation: 0.31) |
| a random signal reaches ≥ 0.614 | **about 1 run in 6** |

**So the honest statement is: this run does not distinguish the method from chance, in either
direction.** Not "the method has some skill". Not "the method has none". The instrument cannot say,
and 0.614 is exactly the kind of number that reads as a result until the null is drawn around it.

**And that interval is optimistic.** It assumes twelve independent decisions; they are clustered on
five accounts, so the true interval is wider than the one published.

## What I changed

`tools/run_value_cycle_ab.py` now publishes `method_skill.null_spread` beside the point null:
`null_sd`, the 95% interval, `z`, `p_two_sided`, `observed_inside_the_null_interval`, and a reading
that says which of the two cases the run is in.

Three properties, each mutation-proven:

- **It refuses on ties rather than switching estimator.** The untied Kendall variance *overstates*
  the spread when ties are present — conservative, and wrong in a direction no reader could see.
  `available: False` with the tie counts, never a quiet substitution.
- **It refuses below three decisions**, where there is no sampling distribution at all, rather than
  returning a very tolerant interval that renders as a lenient result.
- **It can say DISTINGUISHABLE.** At n=40 a concordance of 0.75 lands outside the interval with
  z > 3. A bound that can only ever say "null" is a machine for dismissing every result.

The independence check is the load-bearing test: the published spread comes from a closed form and
the test verifies it against a **permutation**, a completely different method, so the two legs
cannot be one reading twice.

## Why this is the day's pattern for the fourth time

Four figures published today with a denominator or a null that did not match the numerator:

1. an error bar from one world beside a point estimate from another;
2. a point estimate that had **left** the band its spread was measured over, under a fixed sentence
   saying it sat inside;
3. 25 renewals over 210 accounts, when the honest denominator was 1,209 renewals;
4. **0.614 against a point null of 0.5, with no spread.**

All four are two correct numbers whose relationship was not a quantity. None was a wrong figure.

## What is NOT claimed

- Not that the method has no skill. 0.614 is the point estimate and it is above 0.5; what is shown
  is that twelve decisions cannot separate it from noise.
- Not that the estimator is wrong. It is careful, independent on both legs, and its twelve fixture
  proofs stand. What was missing is the sampling bound, which is a different thing from correctness.
- Not that the churn/method contrast is real. Both readings sit inside their own nulls at this book
  size.

## WORK THIS CREATES

1. **`A46` (book depth) is now upstream of three separate instruments** — the ladder's 17 binary
   decisions, the chase comparison, and this. All three say the same thing in different units:
   there are not enough decisions. That is the director's call and it is with him.
2. **Publish `method_skill` on `/capabilities/` with its null spread, or not at all.** The number
   is currently in the artefact and not on the site; putting it up without the interval would
   repeat defects 1–3 above at a fourth site.
3. **The next run carries `null_spread` inline.** The block in the current artefact predates this
   change; the figures above are computed from that artefact's own published fields (n, concordance,
   tie counts), which is the whole input the function takes.

## UPDATE — the closed form refused on its own first live application

The bound shipped as Kendall's **untied** null variance, refusing when either side carried ties
because that formula overstates the spread when they do. Its first live run refused:

> "ties present (1 on the signal, 0 on the outcome), and the untied Kendall variance would
> overstate the spread — refusing rather than substituting an estimator the reader cannot see"

**The refusal was correct and the design was wrong.** The arm priced 25 renewals at **24 distinct
margins**, so a tied signal pair is the ordinary case here, not the exception. A bound that refuses
on the data it was built for is not a bound — it is a permanent withholding wearing a refusal's
name. The honest refusal is what surfaced it, which is the argument for writing refusals that name
their reason.

**Replaced with a permutation of the observed signal values against the fixed outcomes**, 20,000
draws at a fixed seed. It reproduces the tie structure by construction — same multiset of signals,
same ties, random order — and needs no formula for it. Deterministic, and the seed is published
with the result.

**The closed form is kept as an independent cross-check in the tests**, which is what stops the
permutation being one unverified reading: at n=12 untied it gives 0.1105 and the permutation gives
0.1099.

**One mutation did not fire, and it is an equivalence rather than a gap.** Permuting the OUTCOMES
instead of the signals passes every test. Checked numerically on a fixture with six tied signal
pairs rather than argued: signal-permuted sd 0.1084, outcome-permuted 0.1085, 95% intervals
identical to three decimals. The count of half-credit tied pairs is invariant under either shuffle
and the rest are randomly oriented either way, so the two nulls coincide. Recorded because a
mutation that does not fire is either a missing test or an equivalence, and which one it is should
never be left to the reader.

## Still live
