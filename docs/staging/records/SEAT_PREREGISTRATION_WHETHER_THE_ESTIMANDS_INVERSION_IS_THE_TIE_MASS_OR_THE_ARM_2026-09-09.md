**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — attribute the inversion before it is quoted as a fact about the method) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — is the estimand's 0.4210 the tie mass, or the arm?

**Written 2026-09-09, before the discriminating numbers were read.** What I had read when I wrote
this is stated below under "what was already in hand", to the line, so a reader can tell a
prediction from a recital. Everything under "predictions" was unknown to me at the time of
writing and is filed so the arithmetic can refute it.

Commissioned by the Lane 0 delivery item
`attribute-the-inversion-before-it-is-quoted-as-a-fact-about-the-method`, whose hypothesis is:

> `decisions_scored_at_zero_because_the_term_settled_nothing: 37` out of 161 scored — 23% of the
> sample sits tied at one value at the bottom of the ranking, and a rank concordance with a
> quarter of its mass tied at the floor **can read below chance from the tie handling alone, with
> no inversion in the arm at all.**

That is the hypothesis this document predicts against, and it is stated here in the item's own
words so that it can win.

---

## What was already in hand when this was written

Read before writing, from `docs/observability/value_cycle_ab_s1_three_arm_20260909.json` and
`tools/run_value_cycle_ab.py`. None of it is a prediction:

- `method_skill.fixed_horizon.legs.every_priced_decision_pounds_outcome` — **the estimand**:
  `concordance: 0.4210267`, `decisions: 161`, `accounts: 88`, null `[0.4458, 0.5540]`,
  `null_mean: 0.5000819`, `p_two_sided: 0.0045`, `observed_inside_the_null_interval: false`.
- `legs.settled_only_pounds_outcome` — **leg 2**: `concordance: 0.5129503`, `decisions: 124`,
  `accounts: 63`, null `[0.4403, 0.5588]`, `p_two_sided: 0.66645`, inside,
  `comparable_pairs: 7606`, `pairs_tied_on_outcome: 20`.
- `decisions_scored_at_zero_because_the_term_settled_nothing: 37`; `161 = 124 + 37`.
- `_concordance` in `tools/run_value_cycle_ab.py:1275` — **pairs tied on the OUTCOME are excluded
  and counted, never scored**; signal ties score exactly a half.
- `concordance_null_spread` at `:1318` — the null is a **permutation of the observed signal values
  against the FIXED outcomes**, so it reproduces the outcome-tie structure exactly.

I did **not** read `legs.every_priced_decision_pounds_outcome.comparable_pairs` or its
`pairs_tied_on_outcome` before writing this document. Those two numbers are what P1 predicts and
what every later prediction rests on.

## Why the two obvious cuts are not the discriminating cut

The item asks for the concordance re-cut with the 37 zero-settled rows excluded. **That cut
already exists and it is leg 2** — the bridge was built to make exactly that step one variable.
But it does not isolate tie handling: dropping the 37 rows removes the ties *and* the entire
departure population the estimand exists to score, in one move. A move under it cannot be
attributed to either. Reporting it as "the inversion goes away when the ties go" would be the
project's own recurring defect — two things changed, one cause named.

The cut that DOES separate them is a **pair-stratum decomposition**. Every comparable pair in the
n=161 statistic falls in exactly one of three strata:

| stratum | pairs | what it is |
|---|---|---|
| within-settled | C(124,2) = 7626 | leg 2's own population |
| within-zero | C(37,2) = 666 | the tie mass — **both rows score 0.0** |
| cross | 37 × 124 = 4588 | each departure against each survivor |

`_concordance` excludes every pair tied on the outcome. All 666 within-zero pairs are tied at
0.0 by construction. **The tie mass therefore contributes no comparable pairs at all**, and a
stratum contributing zero pairs cannot displace a weighted mean of the other two. If that holds,
the item's hypothesis is refuted by the estimator's construction rather than by a number.

## Predictions

**P1 — the pair counts.** `every_priced_decision_pounds_outcome.comparable_pairs` = **12194**
(7606 + 4588) and its `pairs_tied_on_outcome` = **686** (20 + 666).
*Refuted if either differs.* The most likely way it differs: a settled row whose pounds outcome
is **exactly 0.0**, which would tie against the zero rows and move pairs from cross to tied. Any
such row is itself a finding, because the estimand's zeros are supposed to be the decisions that
settled nothing.

**P2 — the tie mass contributes nothing.** `pairs_tied_on_outcome` ≥ 666.
*Refuted if it is below 666*, which would mean the 37 zero rows do not in fact share one outcome
value and the whole framing is wrong.

**P3 — the cross stratum carries the inversion.** Solving the identity
`c₃ · N₃ = c_within · N_within + c_cross · N_cross` at the P1 counts gives a cross-stratum
concordance of about **0.27**, and I predict the measured value lands in **0.25 – 0.29**.
*Refuted outside that band.* This number is the whole finding: it is the share of
departure-vs-survivor pairs in which the arm gave the DEPARTURE the lower margin. Below 0.5 means
the arm systematically priced HIGHER the decisions that went on to produce nothing.

**P4 — the null is already the tie correction, and it is unbiased.** Under permutation of signals
against fixed outcomes, each comparable pair is equally likely to fall either way, so the null's
expectation is exactly 0.5 whatever the outcome-tie structure. The published `null_mean` of
0.5000819 sits 0.00008 from 0.5, inside the Monte-Carlo error of 20,000 draws (~0.0002). **This
is a reading already in hand, not a prediction** — recorded because it is the load-bearing step:
outcome ties do not bias the statistic, they only remove pairs and therefore *widen* the null.
Consistent with that, the estimand's null SD (0.02763) is wider than leg 0's (0.02593) on more
decisions.

**P5 — the verdict.** The inversion is **not** a tie-handling artefact. It survives, and what it
says is that the arm's per-customer price is anti-correlated with the value the decision produced,
driven entirely by decisions that settled nothing.

**P6 — what would make the item right instead.** Any of: `pairs_tied_on_outcome` < 666 (P2 fails);
a cross-stratum concordance near 0.5 with the departure coming from somewhere unmodelled (P3
fails); or `null_mean` materially off 0.5 (P4 fails, and the estimator is broken).

**P7 — what this does NOT settle, stated now so it is not claimed later.** Even if P5 holds, the
cross stratum is 4588 pairs determined by only 37 rows' signals, drawn from a *different* account
set than leg 2 (88 accounts against 63). That is leverage and clustering, not bias, and the
permutation null assumes exchangeable decisions it does not have. The direction is what this
establishes; the interval remains the one the artefact already publishes, and it is optimistic.

## One variable at a time

**The censoring rule is not touched by this work.** `horizon_open_at_the_end_of_the_settled_book:
47` and `no_published_counterfactual_rate_for_the_term: 6` stay exactly as they are, and the 6 is
restated as a named coverage gap rather than folded in. A cut that moved the censoring in the same
step could not attribute the move, which is the defect leg 0 was added to prevent when it caught
the same error inside this very block on 2026-09-08.

## What "done" means

A result document naming which of the two it is, the decomposition wired into
`tools/run_value_cycle_ab.py` so a future run publishes it rather than a reader deriving it, and
the page's estimand block carrying the answer beside the 0.4210 — not only the figure.
