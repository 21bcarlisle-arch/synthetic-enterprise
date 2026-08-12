# WORKER FINDING — the ageing dimension graded the company's dating against the company's own dating function

**Severity:** BLOCKING · **Lane:** H_harness

**Date:** 2026-08-10 · **Found by:** worker tick running Expert Hour #5 on `H27_payment_belief_gap` (2→3)
**Advances:** `D21_ageing_truth_side_is_the_organs_own_rule` (minted here, built here)
**Verdict:** **HELD AT L2.** Fifth Hour, fifth defect, and the third of the five sitting in a claim the
instrument makes *about itself*.
**R12:** nothing was tuned. Every published figure is byte-identical before and after —
`mean_bucket_displacement` 0.127451 / 0.287958 / 0.166667 at seeds 7 / 11 / 23, both directional rates
unchanged to six places.
**Discharged:** `tests/tools/test_couple_w2_11_d5.py::test_the_truth_side_of_every_published_dimension_is_harness_owned`, `tests/tools/test_couple_w2_11_d5.py::test_R15_an_organ_only_dating_drift_breaks_the_ageing_residual`, `tools/couple_w2_11_d5.py` — the defect this Hour FOUND (the truth side importing the organ's own bucket rule) was repaired inside this same document: the rule is harness-owned, and TRUTH_SIDE_RULE_OWNERSHIP checks the module of the callable that actually ran, so pointing the ageing entry back at the organ fires by name. Verified by RUNNING both falsifiers at this HEAD rather than by reading the commit: 15 selected nodes across this class, all green. The two honest limits (a uniform boundary drift is invisible on a three-age book; the ordinal side reaches 2 of 4 buckets) are recorded and accepted here, not repaired — clause 2's other release — and are themselves pinned by test_the_ageing_headline_is_entirely_miss_driven_here.

## Why the Hour ran on `ageing`

Hour #4's release named the criterion in advance: *"Next Hour's criterion, stated in advance: two
consecutive clean Hours, starting on `ageing`, the only dimension never given an Hour of its own."*
This is that Hour. It is not clean.

Hour #4 also handed over two leads. Both were checked and **neither was taken** — recorded because a
register that only lists the leads that paid off is not an honest one:

- **The two structurally-zero error directions** (detection's `missed_failure_rate`, belief's
  `overcall_rate`). Hour #4 had already ruled these a property of the book rather than of the measure,
  and re-reading them on the corrected instrument did not change that.
- **The unattributed belief directions** in D8's `_ATTRIBUTED_MEASURES`. Still open, still D8's.

## The finding (observed, R9)

`tools/couple_w2_11_d5.py` built the ageing dimension's **truth** labels with the company organ's own
function:

```python
from company.billing.arrears_engine import age_bucket as company_age_bucket   # module scope
...
true_days_overdue = (as_of - r.due_date).days
true_ageing_labels.append(company_age_bucket(true_days_overdue))
```

and its **belief** labels off `AgedItem.bucket`, which is `age_bucket(days_overdue)` in that same
company module. Not a copy of the rule — the rule.

The input is the same integer too, by construction:

| | due date | days overdue |
|---|---|---|
| world (`build_scenario`) | `due`, with `issue = due − PAYMENT_TERMS_DAYS` (14) | `as_of − due` |
| organ (`age_open_items`) | `oi.issue_date + payment_terms_days` (14) | `as_of − that` |

Same function, same argument. **The two sides could not disagree about the bucket of an invoice they
both held open.**

### Measured

`wrong_bucket` — truly-overdue invoices the company dated into the *wrong overdue* bucket — is **0**:

| seed | n truly-overdue | misses | wrong_bucket | headline |
|---|---|---|---|---|
| 7 | 204 | 15 | **0** | 0.127451 |
| 11 | 191 | 33 | **0** | 0.287958 |
| 23 | 216 | 20 | **0** | 0.166667 |

and it stayed 0 under every drift tried, including an organ-only 15-day boundary shift. So every unit of
the ordinal headline comes from a **miss** — the same cases `understated_arrears_rate` reports, rank-
weighted — and it was 0 **by construction, not by luck**.

The dimension's own docstring says the ordinal measure exists because it *"distinguishes off-by-one from
stone-blind, which an error rate cannot"*. On the shipped instrument there was no off-by-one to
distinguish; the construction forbade one.

### Why that is a defect and not a curiosity

An edit to the organ's `age_bucket` moved the harness's notion of **ground truth** with it. A supplier
ageing its debt from the wrong date is the commonest real ageing-report failure there is, and the
dimension whose entire subject is debt **dating** would have certified the company correct by
definition. That is R15's **TAUTOLOGY** pattern — *checked value derived from the same source it
checks* — in the direction nobody checks. The epistemic wall is enforced company → sim: *could a real
supplier know this?* This is harness → company: *is the ground truth being computed by the thing being
graded?*

It is a worse shape than the one Hour #4 found. D20's belief mirror was a hand-copy, which can drift
apart and be caught. A shared object cannot drift, so the divergence is not merely unmeasured — it is
**unrepresentable**. D20's own build note had rejected exactly this as a design one dimension over:
*"making the harness call the organ's own thresholding function would delete the independence the mirror
exists to provide."* Ageing was already doing it.

### Where it hid — the control believed the exemption over the docstring

`COVERAGE_ONLY_CLAIM_CONTRACT["ageing"]`:

> **EXEMPT.** Truth is a clock fact about the due date and belief is the open-item report; **two
> different rules**, not one rule over two coverages.

The module docstring, four hundred lines up in the same file:

> Both sides use the **IDENTICAL bucket function**.

Both of the exemption's clauses were false, the two declarations contradicted each other inside one
file, and the control was wired to the false one — so D20's control, built one Hour earlier for exactly
this failure mode, was switched off for the dimension with the strongest mirror of the three. The
signature the exemption was covering is the claim's own fingerprint: **residual 0.000000** on the all-DD
counterfactual at seeds 7/11/23, non-vacuous.

## What landed (closed at the class, R10)

**1. The rule is harness-owned.** `_ageing_bucket` is declared in the tool; the company import is gone.
This is the discipline `background/gap_metric.py` had *already written down* for the bucket **ORDER** —
*"Redeclared here rather than imported: `background/` is harness code and must not take a company import
for a constant"*, pinned against the company's by `test_d7_ageing_measures.py` — and which the same
dimension never applied to the bucket **RULE**. Harness-owned does not mean free to drift: the two sides
are *meant* to run the same rule, since that is what makes the residual a coverage measurement. What
they may not do is be the same **object**. So they are pinned across 126 day values and the pin names
the divergence.

**2. `TRUTH_SIDE_RULE_OWNERSHIP` — the class control.** Per published dimension, the callable that
produces its truth labels, with the invariant *no truth-side labelling rule may be owned by `company.*`*,
checked on the `__module__` of the callable that actually ran. It is the **call path**, not a
declaration: `score_triad` resolves through `truth_side_rule("ageing")`, so the register cannot quietly
stop describing the code (the D19 lesson). `rule: None` is the honest entry for a dimension whose truth
is a raw world fact, spelled out rather than omitted because an absent entry is how a register fails
silent; the dimension set is derived from what is published; both fail-open shapes — unregistered
dimension, ruleless dimension asked for a rule — raise at the point of use.

**3. Ageing enrolled in the coverage-only control**, with the corrected reason. Asserted **per
dimension**, because the existing R15 organ-drift test passes on `any()` of the claiming set — with
`belief` in it, `ageing` could have been enrolled and never actually exercised.

### R15, both ways

| mutation | what fires |
|---|---|
| point the ageing register entry back at the organ's `age_bucket` | the ownership control |
| organ-only dating drift, 60-day boundary → 75 | ageing residual 0.0 → **0.3627 / 0.3194 / 0.3333** (seeds 7/11/23) |

And the second assertion in the first of those is the point of the whole build: **reinstating the defect
moves no published number at all.** The two rules are logically identical at HEAD, so no figure was ever
wrong — only unable to become wrong. That is why the control has to be about ownership rather than about
a value, and why nothing caught this for the instrument's life.

## Honest limits, pinned by test rather than buried

- A drift shifting **every** bucket boundary by the same 7 days is **invisible** to the enrolled control
  on this book: `build_scenario` exposes only three distinct debt ages (30, 51 and 72 days) and that
  drift crosses none of their boundaries. The control sees a dating drift only where the book has an
  invoice near the boundary that moved.
- `90+` and `current` are never reachable on the truly-overdue truth side, which is what bounds
  `max_bucket_displacement` at 2 — the ordinal dimension exercises **2 of its 4 buckets**.

Both are asserted by `test_the_ageing_headline_is_entirely_miss_driven_here`, which fails if either
changes. Widening the scenario's age spread would move published numbers on every dimension of the
triad, so it is registered, not fixed on sight (SELF_INTERRUPT_DISCIPLINE).

## Also caught: the Hour log had a gap

`H27.expert_hour.findings` held seven entries ending at Hour #3. **Hour #4 was never appended** — the
Hour landed as atom D20, its commit and its staged finding, and the register that is supposed to be the
Hour log itself was not updated. Recorded late, and marked as recorded late.

## Tests

15 new in `tests/tools/test_couple_w2_11_d5.py`; **417 green** across every suite touching `gap_metric`
and the coupled pairs (`test_couple_w2_11_d5`, `test_gap_metric`,
`test_gap_metric_misapplication_class`, `test_live_payment_triad`, `test_d7_ageing_measures`,
`test_couple_w2_4_c6`, `test_couple_cohort`, `test_couple_w2_5_c7`, `test_couple_fabric`,
`test_couple_supply_start`, `test_couple_w2_7_c9`, `test_couple_w2_9_c11`); 86 green in `tests/design`.
Ledger: `LEVEL_UP_SELF_CERTIFIED` D21 → 2 in `docs/observability/gate_authorizations.jsonl`.

## Why H27 is still at L2, and the criterion for Hour #6

Hour #4 set the release criterion as **two consecutive clean Hours**. This one was not clean, so the
count is still zero. Five Hours, five defects, none predicted by the previous one, and the arrival rate
is not falling. And as in Hour #3 and Hour #4, this is the tick that changed the instrument, which is
the worst-placed tick there is to certify it.

**Hour #6 should start where this one did not go.** Two named leads, both about the ageing dimension's
population rather than its rules:

1. The truly-overdue side reaches **2 of 4 buckets** and the whole book holds **three debt ages**. The
   ordinal dimension is published with a 4-bucket vocabulary it half exercises, and the enrolled control
   inherits that blind spot (a uniform boundary drift is invisible). Whether an L3 dating measure may be
   scored on a three-age book is a real judgement and it is now measured, not assumed.
2. The overstated direction has **no ordinal term at all** — `mean_bucket_displacement` is taken over
   the truly-overdue population only, so a truly-current invoice dated `30-60` and one dated `90+` score
   identically. The off-by-one/stone-blind distinction the headline exists to make is made in one
   direction. That would move a published number, so it is a mint, not a fix on sight.
