**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The level arm had no evidence frontier, so the two arms have never priced the same book

**Filed:** 2026-09-18 · **Claim id:**
`the-two-arms-have-never-priced-the-same-population-and-the-page-says-they-have`
**Pre-registration:** `docs/staging/PREREG_GIVING_THE_LEVEL_ARM_THE_SUPPORT_BOUND_AND_WHAT_IT_MOVES_2026-09-18.md`

---

## The defect

`decide_margin`'s value arm filters its candidate margins through **two** bounds — the lawful
ceiling and `max_supported_rate_increase_pct()`, the churn model's own evidence frontier — and
raises `MarginDecisionUnavailable` when nothing survives either. The `flat_at_level` arm, whose
entire job is to price *the same renewals* so the residual between the two is the choosing and
nothing else, applied the lawful ceiling only. It could clamp, so it could never refuse.

On the published run (`value_cycle_ab_s1_three_arm.json`, 2026-09-10, world `39a192ce04c1eda8`):

| arm | renewals offered | priced | declined |
|---|---|---|---|
| value | 2,037 | 215 | **65** |
| level | 2,050 | **281** | **0** |

65 of the 66-renewal denominator gap is the value arm's own refusals — renewals **both arms
reached**, one refused and the other priced. The level arm's margin on all 65 sits inside
`level_advantage_gbp` with no counterpart in `value_advantage_gbp`, so the whole of it lands in the
published residual `level_vs_selection.selection_gbp` with a negative sign. That residual's own
magnitude is **£333**. The contamination is of order £3,900.

Three sentences in the tree asserted the opposite, and every one of them was load-bearing:
`decision_population`'s docstring ("THE MECHANISM IS SEQUENTIAL-A/B ROSTER DIVERGENCE"),
`declined_renewals`' ("`FLAT_AT_LEVEL` CLAMPS to the ceiling and prices everything it reaches" —
true, and offered as the reason the roster is *only* a diagnostic), and `level_vs_selection`'s
("applies ONE uplift to EXACTLY the renewals the value arm priced"). All three are corrected in
place, with the false version quoted beside the correction.

## The fix, and where it departs from the drawn item

Both arms now refuse through **one function** raised from both branches
(`value_based_renewal._no_lawful_predictable_offer`), and the support ceiling is computed once
above both of them.

The drawn item asked for a refusal *whenever the clamped level exceeds the support ceiling*. That
is not what landed, and the arithmetic is the reason — recorded in the pre-registration before the
code was written:

* the value arm refuses iff `base + min(candidates)=0.50 > ceiling`;
* the literal level rule refuses iff `base + 20 > ceiling`.

The second set strictly contains the first, so the literal rule would make the level arm's priced
population a strict **subset** of the value arm's — the same defect with the sign reversed, on
every renewal whose support headroom falls in [0.50, 20). **The frontier is shared, not the
threshold**: the level is clamped into the supported region exactly as it is already clamped into
the lawful one, and the arm refuses only where the value arm's search also comes back empty. Both
arms now price iff `base + min(candidates) ≤ min(lawful ceiling, support ceiling)` — one predicate,
not two that agree today.

This is deliberately **not** the ladder's treatment. A rung prices above the frontier on purpose
and reports it (`ladder_above_support_bound`): it is an experiment that asks the world to answer at
a price the experimenter set. The level arm is a comparator whose only product is a difference
against the value arm, and a comparator that prices where its subject may not is not measuring its
subject.

## The controls, and what each would have caught

| control | keyed to | reds before the fix |
|---|---|---|
| `test_the_two_arms_price_and_refuse_TOGETHER_across_the_whole_frontier` | the refusal predicate over a 7-row sweep that reaches BOTH answers, no counts pinned | yes (verified by mutation) |
| `test_the_level_arms_refusal_is_the_VALUE_ARMS_OWN_REASON` | one reason string, not two that agree | yes |
| `test_the_support_clamp_is_NOT_reported_as_the_lawful_CEILING` | R15 fail-silent: the company's ignorance published as the regulator's cap | yes |
| `test_same_priced_population_ANSWERS_THE_RESIDUALS_PRECONDITION_over_the_whole_partition` | the artefact's own new boolean, over its whole partition incl. the unanswerable case | n/a (new field) |
| `test_a_level_arm_DECLINE_and_a_renewal_the_level_arm_never_saw_are_not_the_same_MISS` | two opposite facts that had collapsed into one `False` | n/a (new field) |

**`same_priced_population` is deliberately NOT `value.priced == level.priced`.** Two arms of a
sequential A/B run two different worlds: a different price causes a different churn, and an account
that leaves early takes every later renewal with it. The denominators are *expected* to differ and
that difference is the effect being measured — a control pinned to integer equality would go red on
a correct run and could only be satisfied by suppressing the measurement. What the residual
actually needs is narrower: that neither arm **refused** a renewal the other **priced**. That is
what the field answers, from `explained_by_declines`, with the net-count caveat stated and the
renewal-by-renewal answer (`declined_renewals.level_arm_priced_the_same_renewal`) named beside it.

## What is not yet done

The three-arm re-run in world `39a192ce04c1eda8` is in flight
(`docs/observability/value_cycle_ab_s1_three_arm_20260918.json`). Until it lands, **every published
figure on the value-arms page still comes from a run where the two arms priced different books**,
and the page does not know it. The predictions for that run are in the pre-registration, filed
before it started.

A second question falls out and is **not** settled here: the page's error bar is a noise floor
measured on the pre-fix tree. A point estimate from the new run bounded by a floor from the old one
is two trees in one figure, and `_staleness_caveat`/`_later_runs_in_this_world` are the guards that
have to be asked about it rather than worked around. Re-running the folded-eighteen floor is 54
full passes and is a separate piece of work.
