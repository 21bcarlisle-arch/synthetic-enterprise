# WORKER FINDING — the lifetime-value model and the retention policy disagree about churn on 93% of decisions

**Severity:** LATENT · **Lane:** B_commercial

(Lane is `B_commercial`, not `W2_customer_generator`: both estimators are the COMPANY's own
models in `saas/` and `company/policy/` — churn valuation and retention pricing — not the
customer generator's published records. The 2026-08-17 re-homing of two sibling findings
went to `W2_customer_generator` because those were data defects in what the generator
publishes; this one is not.)

Both estimators are real, both are company-side, and neither is a wall breach. No published
figure is currently wrong because of this — the render half that WAS wrong (a page publishing
one estimator under the other's caption) is repaired and controlled, see below. LATENT rather
than BLOCKING is a decision, not a default: declaring it BLOCKING would freeze the saas lane
on a modelling question nobody has scoped, and the defect it could cause is not yet observed
in any artefact.

**Raised:** 2026-08-18, `SITE2_two_sided_wall_exhibit` worker tick (scheduled draw)
**Rank requested (P-1):** backlog
**Why this doc exists:** the render half of `coldwalk:site2_churn_belief_published_as_23_and_5_for_one_decision`
is inside SITE2's `file_scope` and is now built. The half below is not — it lives in `saas/`
and `simulation/`. Re-homing it without writing it down would lose it; leaving it on SITE2
would hold that atom on work it cannot do (the same trap
`WORKER_FINDING_TWO_DEFECTS_THE_WALL_EXHIBIT_SURFACED_ARE_NOT_THE_EXHIBITS_2026-08-17.md`
recorded five days earlier). R9 labels throughout.

---

## The observation

`observed-with-evidence`, measured 2026-08-18 against `docs/reports/run_output_latest.json`:

The company carries **two independent estimates of the same household's churn risk at the
same renewal decision**, produced by different code, consumed by different downstream users:

| | producer | input | consumed by |
|---|---|---|---|
| A | `saas/churn_model.build_churn_risk()` → `churn_risk[acct][i].churn_probability` | count of bill-shock months in the preceding 12 | CLV / enterprise value (`saas/clv_model.py`, `saas/enterprise_value.py`), published as `latest_churn_probability` |
| B | `simulation/run_phase2b.py::estimate_renewal_churn(RenewalObservation(...))` → `company_est` | the renewal observation | `company/policy/decision_policy.py::retention_discount_for_risk()` — **it chose the discount actually offered** |

Paired decision-by-decision over every account with both (`churn_risk` rows zipped against
the `renewed`/`churned` outcome events from `extract_customers`):

**54 of 58 paired decisions diverge by more than 0.005 — 93%.**

Last decision per account, A against B:

```
C1    2021-12  0.23  vs 0.051      C8     2025-03  0.35  vs 0.13
C2    2025-03  0.41  vs 0.158      C9     2025-06  0.14  vs 0.14
C3    2020-06  0.17  vs 0.076      C_IC1  2024-12  0.29  vs 0.95
C4    2024-09  0.17  vs 0.14       C_IC2  2024-12  0.29  vs 0.95
C5    2020-12  0.38  vs 0.095      C_IC3  2024-12  0.41  vs 0.083
C6    2024-03  0.29  vs 0.238      SYN-2021-001 2024-12  0.05 vs 0.05
C7    2024-12  0.38  vs 0.17
```

The worst cases are the I&C accounts: `C_IC1`/`C_IC2` are scored **0.29 by the model that
values them and 0.95 by the policy that priced their offer** — the two disagree about
whether the account was nearly certain to leave.

## Why it may matter (`inferred`, not yet demonstrated)

A supplier whose lifetime-value model and whose retention policy hold different beliefs
about the same customer at the same moment will systematically misprice retention: it
offers against B and books the value against A. On C_IC1 that is a 0.95-probability
departure carried at a 0.29-probability valuation, on an account the exhibit itself
describes as £257k of term margin at risk. **Not asserted as a live defect** — no published
figure has been shown wrong by it, and the divergence has not been traced to any P&L
consequence in the current book. That tracing is the work.

**Explicitly not a wall breach.** Both estimators are company-side and both are built from
observables. This is a company-coherence question, not an epistemic one, and R12 applies:
the divergence is a DIAGNOSTIC. Do not tune either model to close the gap because the gap
looks bad.

## Suggested falsifier (not yet run)

Two beliefs about one quantity are only a defect if something downstream consumes both.
Trace whether any single published figure is computed from A and B together (or from one
while captioned as the other) anywhere outside `site/customers/`. If nothing joins them,
this is two models for two purposes and the honest fix is naming, not reconciliation —
which is exactly what the render half did. If something does join them, that join is the
defect and it has a population to measure.

`inferred`: a null control is needed here. Two estimators built from different inputs will
differ by construction; the question is whether they differ MORE than two reasonable
estimators of the same quantity should, so the divergence needs a baseline before "93%"
means anything. 93% is the rate of *any* divergence above 0.005 — a deliberately weak
threshold, and it should not be quoted as if it were a rate of *material* divergence.

## What was already done (do not redo)

The RENDER half is built and controlled inside `SITE2_two_sided_wall_exhibit`:
`site/customers/index.html` published A under the caption "belief at last renewal decision"
— which describes B — while rendering B verbatim in the reaction chain lower on the same
page. Three blindfolded personas caught the contradiction independently. Both estimates are
now rendered as two tiles, each naming its own producer and decision date. Controls:
`test_the_two_churn_estimates_each_name_their_own_producer`,
`test_the_acted_on_churn_tile_carries_the_chains_belief_not_the_models_score`,
`test_a_household_with_no_recorded_belief_renders_absence_not_a_number`, R15-proven both
ways by `test_mutation_restoring_the_false_caption_kills_a_named_test` and
`test_mutation_publishing_the_models_score_as_the_acted_on_belief_kills_a_named_test`, and
proven to fail against the pre-fix HEAD.
