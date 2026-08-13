# WORKER REPORT — the per-customer lifetime estimate now follows the belief

**Severity:** RECORDED · **Lane:** B_commercial
**Severity header repaired 2026-08-13** (18th draw of `H_GAP_fabric_belief_truth_gap`): this read
`RESOLVED`, which is outside the `BLOCKING / LATENT / RECORDED` vocabulary and so parsed
UNCLASSIFIED, holding every lane's level recording repo-wide. `RECORDED` is the vocabulary word for
what this document is — completed work, its finding archived, no work owed. No content changed.
**Drawn:** 2026-08-13, RUNG 1c blocking draw (OPS12 clause 3) — the live BLOCKING finding
`WORKER_FINDING_THE_LIFETIME_ESTIMATE_DOES_NOT_MOVE_WHEN_THE_BELIEF_DOES_2026-08-13.md`,
ahead of the general disposition queue in this lane.
**Finding archived to:** `docs/staging/done/WORKER_FINDING_THE_LIFETIME_ESTIMATE_DOES_NOT_MOVE_WHEN_THE_BELIEF_DOES_2026-08-13.md`

## What was wrong

`saas/clv_model.py::build_clv` published a per-account `expected_lifetime_periods` and a
`clv_gbp` derived from it, and **the number was not a function of what the company believed
about that account**. `build_clv_model` installed ONE pooled Beta(alpha, beta) — fitted across
every renewal in the book — as the posterior for every account alike, and the per-account
figure was then read out of `distribution_customer_churn_time`. What survived per account was
the sampler's noise.

Reproduced before acting, not taken on the finding's word: two accounts with identical tenure
and margin, churn beliefs 0.05 and 0.45, then swapped. Both runs returned
`SAFE=14.935 RISKY=23.370`. The estimate stayed with the **name**.

## What changed

- **`fit_theta_posterior_per_account`** (new) — the pooled Beta is kept as the PORTFOLIO
  PRIOR and updated with each account's OWN renewal history by conjugate Beta-Bernoulli with
  **soft counts** (`alpha += sum p_i`, `beta += sum (1 - p_i)`), because the company holds
  churn *probabilities*, not realised churn flags. Distance from the portfolio mean is bought
  with evidence: nine renewals move further than three. The prior is still fitted over the
  whole book including departed accounts — a supplier learns most from the customers who left.
- **`expected_lifetime_periods`** (rewritten) — the sBG expected lifetime in **closed form**,
  `E[min(T,M)] = sum_t E[(1-theta)^t]`, truncated at `MAX_PROJECTION_PERIODS`. Bounded by
  construction where the untruncated mean `(alpha+beta-1)/(alpha-1)` diverges as alpha -> 1 and
  was being clipped by a cap doing load-bearing work. Being exact, it also removes the seed,
  `n_draws` and roster-position dependence the finding called a C-S2 RNG-substream defect.
- **`build_clv_model`** retained as the portfolio-level view, explicitly documented as no
  longer on the CLV path so it cannot be quietly reintroduced as the source of a per-account
  figure.

## Evidence

**R15 both ways — four source mutations, each killing named tests:**

| mutation | tests killed |
|---|---|
| reinstate the pooled posterior (the original defect) | 4, incl. `test_mutation_swapping_two_accounts_churn_beliefs_swaps_their_lifetimes` |
| invert the survival term (wrong sign) | 4, incl. `test_expected_lifetime_matches_a_direct_simulation_of_the_model` |
| re-admit the seed into the per-account estimate | `test_an_accounts_projection_does_not_depend_on_the_seed_or_the_draw_count` |
| let the valued population contaminate a retained account | 4, incl. `test_a_retained_accounts_projection_does_not_depend_on_who_else_is_valued` |

The headline control is written as an **exchange** between the two accounts, not an equality
against a recorded number — the failure mode the finding named ("it cannot be written as an
equality assertion on a fixed seed"). The closed form is checked against an **independently
written Monte-Carlo simulation** of the sBG rather than against itself (R15 tautology guard).

**Suites:** `tests/saas/` + `test_customer_value_seam.py` + `tests/controls/` — 1940 passed,
1 xfailed. `tests/tools/` (customer/company/clv/value) 257 passed. `tools.epistemic_verifier`
PASS. Mutation source restored from a backup copy with md5 verified, never `git checkout --`
(the file carried uncommitted work).

**Measured on the live book** (`docs/reports/run_output_latest.json`):

| | before | after |
|---|---|---|
| corr(account's own churn history, projected lifetime) | +0.093 | **-0.987** |
| mean projected lifetime | ~13.5 yr | ~5.2 yr |
| enterprise value, same 8 accounts | £7,013,265 | £3,526,222 (-49.7%) |

**This is a fidelity correction, not a tuning (R12/R13).** A 13.5-year mean life implies ~7.4%
annual churn; this book's own believed churn probabilities run 0.140–0.410 with a portfolio
mean of 0.240, implying ~4–6 years. The old estimator was biased long, not merely noisy. The
number was not moved toward any target and no band was consulted.

## It also discharged a sibling finding's blocked control

`WORKER_FINDING_THE_BOOK_VALUE_COUNTS_CUSTOMERS_WHO_HAVE_ALREADY_LEFT` asked for "the total
must fall by exactly that account's CLV" and could not have it — this defect meant excluding
one account moved every other account's projection. Its author pinned the coupling with a
deliberate tripwire test instead of tuning the control green. **The tripwire fired on this
change, and only it** (1 failed, 38 passed). Followed its own written instructions: measured
that exact additivity now holds (residual -2.3e-13), tightened
`test_mutation_a_valued_account_marked_ceased_removes_its_value_from_the_total` to the exact
equality, deleted the tripwire, and replaced it with a per-account independence test (a total
can net two offsetting errors). That doc's item 4 is marked discharged; it stays parked in
`in_progress/` because its items 1 and 3 remain open.

## Found on the way — QUEUED, not fixed (SELF_INTERRUPT_DISCIPLINE)

`saas/enterprise_value.py` cited the sibling finding at `docs/staging/done/...` while the doc
was actually in `docs/staging/in_progress/` — a dead path in a source comment. Corrected here
because I was editing that docstring. **The class is not fixed:** there is no control that
checks whether backtick-cited repo paths in source and docs resolve.
`tests/tools/test_site1_proof_citations_resolve.py` does this for SITE1 proof citations only.
Scanning just the files I touched surfaced one further pre-existing dead path
(`docs/staging/PHASE_4b_INSTRUCTION.md`, cited in `PHASE_4b_SUMMARY.md`). This is the known
archiving-breaks-citations class; a repo-wide citation-resolution control is the R10 class fix
and belongs in H_harness, not in this lane's blocking draw.

## What is NOT claimed

- **No live fetch (R11 item 1 still open).** Autonomous runs have no network. Everything above
  is measured in the published artefacts at HEAD and in the render expressions.
- **Published artefacts still carry the old figures.** `run_output_latest.json` and
  `site/data/company.json` do not change until a full simulation run regenerates them. The
  render sites (`site/customers/index.html` "Expected Lifetime",
  `site/company/index.html` "CLV" tile) read the field and are unchanged, so they inherit the
  corrected value at the next run — they were not edited and need no edit.
- **No level moved.** This is a defect discharge in `B_commercial`, not an atom promotion.
