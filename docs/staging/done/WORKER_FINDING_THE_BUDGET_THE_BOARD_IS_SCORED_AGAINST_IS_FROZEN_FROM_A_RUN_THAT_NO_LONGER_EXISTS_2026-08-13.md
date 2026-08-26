# [WORKER-FINDING] The budget the board is scored against is frozen from a run that no longer exists (2026-08-13)

**Severity:** LATENT · **Lane:** E_finance_treasury

**Status:** measured and reported, not fixed. Every number in the published table is
arithmetically correct given its two inputs — which is why this is LATENT and not BLOCKING — but
the plan side is a hardcoded table whose own stated derivation no longer reproduces, so the
variance and RAG columns measure staleness rather than planning error. Found during the
`EP2_variance_learning_loop` DISCOVER draw: this is the only variance surface the board actually
sees.

## The claim the module makes about itself

`company/finance/budget.py:1`:

> Budget is derived at year-start from prior-year actuals * growth targets:
> revenue * 1.10 (10% growth), opex * 1.05 (5% cost growth).
> 2016 is the baseline year (budget = actuals). Static constants below.

The constants are a literal `_BUDGET_BY_YEAR` dict. Nothing recomputes them.

## The test

Invert the stated rule — `budget(Y) / 1.10` must equal the published actual for `Y−1` — against the
actuals in `docs/reports/ANNUAL_REPORT.md:2652` (**Budget vs Actual**). `observed-with-evidence`:

| Year | Budget revenue | Implied prior actual | Published prior actual | ratio |
|---|---|---|---|---|
| 2017 | £16,138.86 | £14,671.69 | £15,065.68 | 0.9738 |
| 2018 | £386,623.75 | £351,476.14 | £345,709.74 | 1.0167 |
| 2019 | £675,851.95 | £614,410.86 | £600,123.82 | 1.0238 |
| 2020 | £1,816,630.04 | £1,651,481.85 | £1,640,323.85 | 1.0068 |
| 2021 | £2,028,952.42 | £1,844,502.20 | £1,853,676.52 | 0.9951 |
| 2022 | £2,607,611.88 | £2,370,556.25 | £2,407,212.44 | 0.9848 |
| 2023 | £4,508,414.67 | £4,098,558.79 | £4,265,103.60 | 0.9610 |
| 2024 | £3,512,844.39 | £3,193,494.90 | £3,442,531.99 | 0.9277 |
| 2025 | £3,145,356.42 | £2,859,414.93 | £3,007,972.65 | 0.9506 |

**The ratio is never 1.000.** The rule is internally consistent only within the table itself
(2017 = 1.10 × 2016 exactly), i.e. the constants were baked from a *different* run's actuals — one
whose 2017 revenue was £351,476.14 against the current £345,709.74. Drift reaches 7.2% by 2024.

## What the board is shown as a result

`docs/reports/ANNUAL_REPORT.md:2652` — **8 of 10 years RED**, including 2017 at **+2042.1%**
revenue and **+1459.8%** net, which is the 2016 baseline year meeting a company that then scaled by
two orders of magnitude. The RAG (`GREEN <5%, AMBER 5-15%, RED >=15%`) is applied to a variance
that is dominated by table staleness plus a regime change, not by planning performance.

A rating that reads RED in eight years out of ten carries no information — and, being the *only*
expected-vs-realised surface the company publishes, it is the thing standing in for the ex-post
bridge `EP2_variance_learning_loop` exists to build.

## Why LATENT and not BLOCKING

Every number the report renders is arithmetically correct given its two inputs: `variance_pct` is a
true difference between the frozen plan and the real actual, and the section says exactly that it
compares "Annual plan [to] management account actuals". What is false is the module **docstring's**
derivation rule, which is not itself published. Under `background/finding_severity.py` that is "real defect; does not
invalidate anything published or any control's verdict".

It is not RECORDED, because work is owed: a plan that cannot be reproduced from the run it scores
is not a plan, and the RAG derived from it is decorative.

**What would clear it:** either recompute the budget from the current run's prior-year actuals at
report time (making the docstring true), or relabel the table as a fixed external plan and drop the
derivation claim — and in either case exclude or footnote 2016→2017, where the baseline year makes
the ratio meaningless. Sits naturally with the EP2 build
(`docs/design/EP2_VARIANCE_LEARNING_LOOP_DISCOVER_FRAME.md` §5), which needs a defensible expected
side anyway.

Not fixed in this tick: SELF-INTERRUPT DISCIPLINE — queue by default; and choosing between the two
remedies is a reporting-standard decision (E4), not a drive-by edit.
