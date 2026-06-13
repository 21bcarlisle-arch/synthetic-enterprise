# Phase 4b Summary — Customer Value Layer

Staged instruction (`docs/staging/PHASE_4b_INSTRUCTION.md`, actioned
2026-06-13): build in order 4b-1 cost to serve, 4b-2 churn model, 4b-3 CLV
(Shifted-BG via PyMC-Marketing), 4b-4 home move win rate, 4b-5 enterprise
value function. Sub-phases are appended below as each clears its
REVIEW_GATE.

---

## 4b-1 — Cost to Serve Model

### What Was Built
- `saas/cost_to_serve.py` — new pure module, `build_cost_to_serve()` and
  `cost_to_serve_for_period()`. Adds an operational-cost layer on top of
  `simulation/portfolio_pnl.py`'s `margin_gbp` (revenue minus wholesale cost
  only), producing `net_margin_gbp = margin_gbp - cost_to_serve_gbp`.
  - **Fixed overhead**: an annual £/account figure (billing/IT/customer
    service + smart-meter operation), divided across
    `SETTLEMENT_PERIODS_PER_YEAR = 17,520` (48 x 365). resi = £55/yr,
    SME = £120/yr.
  - **Bad debt**: a flat percentage of each period's revenue. resi = 2%,
    SME = 1% (SME accounts are credit-checked at acquisition).
  - Each commodity contract (electricity or gas) is costed as its own
    account — a dual-fuel household (e.g. C1 + C1g) carries fixed overhead
    twice, mirroring separate billing/metering relationships even when
    bundled commercially.
- `tests/saas/test_cost_to_serve.py` — 5 tests: per-period arithmetic, resi
  vs SME overhead comparison, empty-input zeroing, multi-period/multi-customer
  aggregation, and unknown-customer KeyError.

### Key Decisions Made
- **Segment-keyed cost tables, not per-customer**: matches the existing
  `saas/customers.py` segment field (`"resi"` / `"SME"`) rather than adding
  new per-customer attributes — keeps the model a thin layer that's easy to
  recalibrate later.
- **Bad debt as a per-period % of revenue, not a year-end true-up**: this
  model has no arrears-ageing concept, so the simplest point-in-time-safe
  approximation is applied every period.
- **Cost-to-serve computed as a standalone aggregation over settlement
  records**, mirroring `simulation/portfolio_pnl.py`'s shape
  (`portfolio` + `by_customer`) so it composes the same way in downstream
  reporting/orchestration.

### Open Questions
- Applying this to the full Phase 2b 9.5-year settlement output (to produce
  headline net-of-cost-to-serve figures alongside the £13,970.60 net margin)
  requires re-running `simulation/run_phase2b.py` to regenerate settlement
  records — not done in this increment to avoid a multi-hour re-run; flagged
  as a follow-up for whoever next runs a full-window simulation.
- Cost figures (£55/£120 overhead, 2%/1% bad debt) are seed estimates based
  on rough UK retail cost-stack proportions, not calibrated against any real
  dataset — a future increment could calibrate against published Ofgem
  default-tariff-cap cost-stack breakdowns.
- Dual-fuel double-counting of fixed overhead (4b-1's "Key Decisions") may
  overstate cost-to-serve for C1-C4 vs a real combined-billing relationship —
  same open question raised for billing in Phase 3a, now compounding into
  cost as well as bill-shock perception.

### Token Efficiency
- Frontier (hand-written): `saas/cost_to_serve.py`,
  `tests/saas/test_cost_to_serve.py`, this summary section. Small,
  schema-adjacent pure module — same delegation calculus as
  `saas/customer_reaction.py` (Phase 3a).

---

## 4b-2 — Churn Model

### What Was Built
- `saas/churn_model.py` — new pure module, `build_churn_risk()` and
  `churn_probability()`. `simulation/renewals.py` assumes a 100% renewal
  rate ("no churn modelled yet — that is a later phase's concern"); this is
  that phase.
  - Reuses `saas/customer_reaction.score_experience_signals()` (Phase 3a) to
    get each billing account's monthly `bill_shock_triggered` history.
  - At each annual renewal anniversary of the account's `acquisition_date`
    (365-day contract length, matching `simulation/settlement.py`), counts
    `bill_shock_triggered` months in the preceding 12 months.
  - `churn_probability = BASE_ANNUAL_CHURN_PROBABILITY (5%) +
    bill_shock_count * CHURN_UPLIFT_PER_BILL_SHOCK (3pp)`, capped at
    `MAX_CHURN_PROBABILITY` (95%).
- `tests/saas/test_churn_model.py` — 7 tests: base-rate/uplift/cap
  arithmetic, empty input, accounts with less than a year of data (no
  renewal points), a worked renewal-window bill-shock count, and an unknown
  billing-account KeyError.

### Key Decisions Made
- **Churn is driven purely by bill-shock frequency, not by price fairness or
  margin** — directly encodes the Key Domain Insight (CLAUDE.md): customer
  reaction to bills is non-rational.
- **Renewal points, not settlement periods, are the unit of churn risk**:
  matches `simulation/renewals.py`'s contiguous 365-day term structure, so
  this output can slot directly into a future renewal-schedule consumer
  that decides whether a term renews.
- **Reused `score_experience_signals()` rather than re-deriving bill
  history**: keeps the billing-account mapping (dual-fuel C1+C1g -> "C1")
  and bill-shock threshold (0.15) consistent with Phase 3a rather than a
  second implementation that could drift.

### Open Questions
- `build_churn_risk()` reports a probability per renewal point but does not
  yet *act* on it (e.g. removing a customer from subsequent settlement) —
  wiring this into `simulation/renewals.py` so churned accounts actually
  stop renewing is a natural follow-up, likely alongside 4b-4 (home move
  win rate, which presumably models the inverse — new customer acquisition).
- `BASE_ANNUAL_CHURN_PROBABILITY` (5%) and `CHURN_UPLIFT_PER_BILL_SHOCK` (3pp)
  are seed estimates (Ofgem reports UK switching rates roughly in the
  5-15%/year range historically), not calibrated against any real dataset.
- Applying this to the full Phase 2b settlement output (to see how many of
  the ~9 renewal points per account would be flagged as high-churn-risk,
  especially during 2021-2022) requires re-running
  `simulation/run_phase2b.py` — same multi-hour re-run constraint noted in
  4b-1, deferred to the same follow-up.

### Token Efficiency
- Frontier (hand-written): `saas/churn_model.py`,
  `tests/saas/test_churn_model.py`, this summary section. Small,
  schema-adjacent pure module building directly on Phase 3a's
  `score_experience_signals()`.

---

## 4b-3 — CLV via Shifted Beta-Geometric (PyMC-Marketing)

### What Was Built
- `saas/clv_model.py` — new pure module, `build_clv()`,
  `build_clv_model()`, `build_shifted_beta_geo_data()`,
  `fit_theta_prior_from_churn_probabilities()`, `expected_lifetime_periods()`.
  - `build_shifted_beta_geo_data()` shapes `churn_model.build_churn_risk()`
    output into PyMC-Marketing's `{customer_id, t_churn, T}` convention for
    `ShiftedBetaGeoModelIndividual` — every account is right-censored
    (`t_churn == T`), accounts with no renewal points excluded.
  - `fit_theta_prior_from_churn_probabilities()` derives Beta(alpha, beta)
    hyperparameters for theta (per-renewal churn probability) via
    method-of-moments across every `churn_probability` value in
    `churn_risk`, with a weakly-informative fallback
    (`FALLBACK_PRIOR_PSEUDO_COUNT = 10`) if the spread is degenerate.
  - `build_clv_model()` constructs a `ShiftedBetaGeoModelIndividual`,
    `build_model()`s it against the shaped data, and installs the
    method-of-moments alpha/beta as a fixed "posterior" (`model.idata`,
    `n_draws` repeated point-estimate draws) — see "Key Decisions" below for
    why this bypasses `.fit()`.
  - `expected_lifetime_periods()` calls
    `distribution_customer_churn_time()` against that idata and takes the
    mean over draws, capped at `MAX_PROJECTION_PERIODS` (50 renewal
    periods).
  - `build_clv()` combines `expected_lifetime_periods` with each billing
    account's average annual `net_margin_gbp` (from `cost_to_serve`, summed
    across dual-fuel electricity/gas legs via
    `customer_reaction._billing_account_id`), discounted via an annuity
    factor at `DISCOUNT_RATE_ANNUAL` (10%/year) to produce `clv_gbp`.
- `tests/saas/test_clv_model.py` — 9 tests: data-shaping (censoring,
  exclusion of accounts with no renewals), method-of-moments arithmetic and
  its degenerate-variance fallback, dual-fuel net-margin combination,
  positive lifetime/CLV with discounting verified against an undiscounted
  upper bound, and empty-input handling.

### Key Decisions Made
- **Method-of-moments priors installed directly as `model.idata`, not a
  `.fit()`**: this portfolio has only 6 billing accounts, each ~9 annual
  renewal points, **0 observed churns** — every account is right-censored.
  Both approaches tried on this data were unusable:
  - Default MCMC (`draws=50-100`, `chains=1-2`): divergences, NaN r_hat,
    theta collapsing to ~0.001 — `distribution_customer_churn_time`
    projections came out around 1e15 periods (theta -> 0 makes the
    geometric expectation blow up).
  - MAP with informative `HalfNormal` priors on alpha/beta: converged to
    alpha=0 exactly, beta~1816 — degenerate, and
    `distribution_customer_churn_time` errors on a Geometric with p=0.

  Installing alpha/beta as a fixed point-estimate "posterior" (`n_draws`
  identical draws) keeps `ShiftedBetaGeoModelIndividual`'s data-shaping
  convention and its `distribution_customer_churn_time`
  posterior-predictive machinery, while sourcing the actual theta estimate
  from `churn_model`'s bill-shock-driven `churn_probability` — which is
  already calibrated (informally) to this portfolio's behaviour — instead of
  trying to re-derive it from 6 all-censored data points.
- **CLV = avg annual net margin x annuity factor over expected lifetime**:
  a simple, auditable closed form rather than a full discounted
  posterior-predictive simulation — appropriate given the prior itself is a
  point estimate, not a real posterior.
- **`DISCOUNT_RATE_ANNUAL = 0.10`** and **`MAX_PROJECTION_PERIODS = 50`**
  are seed values (10% discount rate is a common UK retail cost-of-capital
  proxy; 50-year cap prevents a near-zero theta from producing an absurd
  horizon) — both are tunable constants, not calibrated against a real
  dataset.

### Open Questions
- **This is a point-estimate prior standing in for a posterior** — `alpha`,
  `beta`, and therefore `expected_lifetime_periods` are method-of-moments
  estimates from `churn_model`'s churn probabilities, not a Bayesian fit on
  observed churn events (because this portfolio has none). If/when a larger
  synthetic portfolio with actual observed churns exists, re-fitting
  `ShiftedBetaGeoModelIndividual` via `.fit(method="mcmc")` on that data
  would produce a genuine posterior and should replace this approach.
- **New runtime dependency**: `pymc-marketing` (and its dependency tree —
  `pymc`, `arviz`, `pytensor`, `scipy`, ~35 packages) was installed via
  `python3 -m pip install --break-system-packages pymc-marketing` into the
  system Python's user site-packages. The repo has no `requirements.txt` to
  record this; whoever next sets up this environment from scratch will need
  to repeat this install. Worth adding a `requirements.txt` (or
  `pyproject.toml` dependency group) in a future increment.
- `DISCOUNT_RATE_ANNUAL` and `MAX_PROJECTION_PERIODS` (see "Key Decisions")
  are seed estimates, not calibrated.
- As with 4b-1/4b-2, applying this to the full Phase 2b 9.5-year settlement
  output requires re-running `simulation/run_phase2b.py` — same multi-hour
  re-run constraint, deferred to the same follow-up.

### Token Efficiency
- Frontier (hand-written): `saas/clv_model.py`,
  `tests/saas/test_clv_model.py`, this summary section, plus exploratory
  investigation of `pymc-marketing`'s `ShiftedBetaGeoModelIndividual` API
  (model_config, `.fit()` methods, `distribution_customer_churn_time`,
  `idata` shape) to find a stable approach for this all-censored portfolio —
  the highest-investigation-cost sub-phase of 4b so far, reflected in the
  "Open Questions" above rather than a clean calibrated result.
