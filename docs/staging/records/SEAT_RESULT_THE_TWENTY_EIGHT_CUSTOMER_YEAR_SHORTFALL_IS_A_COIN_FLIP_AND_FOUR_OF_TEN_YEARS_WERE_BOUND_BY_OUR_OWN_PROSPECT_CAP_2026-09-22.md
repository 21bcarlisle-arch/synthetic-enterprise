**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the 28-customer-year shortfall is a coin flip, and four of the funnel's ten years were bound by our own prospect cap

**Filed:** 2026-09-22. Drawn as Lane 0 delivery,
`the-twenty-eight-customer-year-shortfall-is-inside-its-own-error`.

## 0. The premise, re-measured, and the item's own description of the instrument was wrong

The draw's premise check said `c4bee75e3` is already an ancestor of `origin/main`. It is — but the
item does not ask for that commit to be landed; it asks whether a **claim inside it** survives. The
premise is the claim, and the claim was live. Not spent.

**The duplicate-work check named `the-ceilings-downstream-still-fits-a-value-that-never-shipped`.**
Read: it holds `A46`, `book_growth.json`, `generate_book_growth_data.py`, and is about fitting the
downstream to the shipped ceiling value. Different work on the same subject. Carried on.

**What the item got wrong, and it mattered.** The item says the 3,163.9 requirement is derived by
`tools/generate_value_arms_data.py` "inverting `inference_claim.detectability` on a permuted
interval's half-width". That is the **household** leg (`_within_year_remedy`). The *smallest* leg is
the **selection** leg, and it is not a permutation at all:

```
required_customer_years_smallest_leg = required_multiple_smallest_leg × this_book_customer_years
                                     = 2.8198526 × 1,122.0 = 3,163.87
required_multiple_smallest_leg       = V / c²   (the price table at share = 1, V_rest ≡ 0)
                                     = 1,810.5008² / 1,078.1657² = 2.8198526
```

`V` is the variance of a **nine-seed** floor re-draw family; `c` is **the mean of those same nine
draws**. Had I priced the permutation the item named, I would have priced the wrong instrument and
got a finite, reassuring interval. The real instrument is worse, and the difference is the whole
finding.

## 1. Say what each number counts — which is what the subtraction never did

| | kind | what it is | n |
|---|---|---|---|
| **3,135.5** | OBSERVATION | one run of a stochastic funnel: 500 wins × 6.271 cy | 1 run, never repeated |
| **3,163.9** | REQUIREMENT | a ratio of two statistics from one nine-seed sample | 9 draws |

They were differenced to one decimal place and the difference — 28.4 cy, **0.9%** — was published as
"the complete answer".

## 2. The requirement's error is UNBOUNDED ABOVE, and it is arithmetic, not pessimism

`V/c²` with both terms from the same sample of n is algebraically **`n/t²`**:

```
t = |c|·√n / s = 1,078.1657 × 3 / 1,810.5008 = 1.786521      df = 8
n/t² = 9 / 3.19165 = 2.8198526   ← reproduces the published multiple exactly
two-sided p = 0.112
```

That p is the leg's sign being undetermined — which is *why the block exists* — restated as
arithmetic. The page already says the centre "is itself an estimate and is not established to be
non-zero". What nobody carried through: **a requirement divided by that centre inherits a
denominator whose interval straddles zero, and therefore has no upper end.** A true effect of zero
needs an infinite book.

Two rulers, because a noncentral-t inversion deserves a second opinion:

| ruler | 2.5% | 50% | 97.5% |
|---|---|---|---|
| noncentral-t inversion for the scale parameter | **670 cy** | 3,164 (point) | **∞** |
| 200,000-draw parametric bootstrap, producer's own iid-normal model | **422 cy** | 2,979 | 413,482 |

Both put the 95% lower bound **below the 1,250 capacity that binds today**.

## 3. The funnel's error alone already swallows the gap ten times over

Grant the requirement as exact and price only the count. 500 wins, 6.271 cy each, exact Poisson:

```
count 95%:  [457.1, 545.8] wins   →   [2,867, 3,423] cy   half-width ±278 cy
the claimed gap, 28.4 cy, is 10.2% of ONE half-width
```

## 4. The number that settles it

**Under the producer's own model, the requirement exceeds the funnel's supply in 48.4% of draws.**
The comparison the claim rests on is a coin flip. And in **21.4%** of draws the requirement falls
*below* current capacity — it is not established that this book is too small, let alone by 28
customer-years.

## 5. A separate and sufficient reason, needing no statistics at all

In **four of ten years** — 2020, 2021, 2024, 2025 — the campaign was bound not by the world but by
`net_new_acquisition.PROSPECTS_PER_YEAR = 400`. `site/data/book_growth.json` states it in its own
`prospect_ceiling_statement`:

> *"That cap is OURS (net_new_acquisition.PROSPECTS_PER_YEAR = 400, sized when the company could
> afford tens), not the GB switching market — those years understate what this supplier would have
> done."*

So 3,135.5 is a **lower bound on our own instrument's supply**, and a lower bound cannot be the
ceiling a shortfall is measured from. The word "world" was doing work the figure could not support:
40% of the binding was ours. This was readable in a published artefact the whole time, beside the
figure, and the comparison was made anyway.

## 6. What was changed, and what was deliberately not

**Changed** — the correction sits *beside* the original wording in both places, dated, with the
original unedited:

* `simulation/net_new_acquisition.py`, the curve note's point 4.
* `docs/staging/SEAT_RESULT_THE_CEILING_COST_CURVE_IS_CONVEX_..._2026-09-21.md`, §"The one that
  closes the item".

**Not changed, and this is the finding that outlives the turn.** `site/data/value_arms.json`
publishes, on the live page, `what_is_not_established`:

> *"Not whether a book that size can be built — that is now measured, on one ruler, and the answer
> is NO: 2.82x this book is 3,164 customer-years against a capacity of 1,200."*

That is the same unqualified claim on a **public surface**, and it is generated — the string is in
`tools/generate_value_arms_data.py`, whose working copy in this tree is a stale revert (48+/89−).
Repairing it means the block publishes `required_customer_years_smallest_leg` **with its interval**,
and `no_leg_is_reachable` becomes a three-valued answer rather than a boolean, because
`smallest > reachable` is currently a comparison of a point estimate against a capacity and returns
`true` on a coin flip. **That is the next item and it is the one that matters**, because the page is
where a reader meets the number.

**No control is added here** and that is deliberate rather than an omission: nothing in this commit
is code. A control over a comment is the register this repo's own rules say to delete rather than
write. The control that IS owed belongs on the generator — a figure whose interval is unbounded must
not publish a boolean — and it belongs in the commit that changes the generator, not this one.

## 7. What this does and does not establish

It does **not** establish that this world CAN supply the book. It establishes that the two figures
are the same size to within their error, and that the published comparison between them was a
coin flip presented as a measurement.

**It re-points the work.** The withdrawn paragraph licensed stopping on the funnel and continuing on
the compute ceiling. That is backwards: neither of these two errors shrinks by measuring RSS again.
The binding uncertainty is the **nine-seed floor** (n=9, p=0.112) and the **un-repeated funnel**
(n=1 run, 4/10 years artefact-bound). Lifting the prospect cap and repeating the funnel are cheap
next to another ceiling probe, and they are what a signed per-customer arm actually waits on.

## 8. The prediction I am filing before the next run

The nine-seed floor is the binding leg, not the funnel. **I predict that repeating the floor at
36 seeds moves the requirement's point estimate by less than 2x but brings the 97.5% end finite for
the first time, and that the funnel repeated at a lifted `PROSPECTS_PER_YEAR` supplies more than
3,423 customer-years** — i.e. clears the top of its own current Poisson interval, because four of
its ten years were censored. If the second clause fails, the prospect cap was not binding in the way
`prospect_ceiling_statement` says and that statement is the next thing to re-measure.

## 9. Reproduction

```python
import math; from scipy import stats, optimize; import numpy as np
n, mean, sd, book_cy = 9, -1078.1657011111156, 1810.5007782810442, 1122.0
t = abs(mean)*math.sqrt(n)/sd                      # 1.786521, df 8, p 0.112
solve = lambda q: optimize.brentq(lambda d: stats.nct.cdf(t, n-1, d) - q, -20, 20)
n/solve(0.025)**2 * book_cy                        # 670.3  (lower); solve(0.975) < 0 -> no upper
d = np.random.default_rng(20260922).normal(mean, sd, (200_000, n))
m = d.std(1, ddof=1)**2 / d.mean(1)**2
np.quantile(m, [.025,.5,.975])*book_cy             # 422 / 2979 / 413482
(m*book_cy > 3135.5).mean(), (m*book_cy < 1250).mean()   # 0.484, 0.214
per = 3135.5/500
stats.chi2.ppf(.025, 1000)/2*per, stats.chi2.ppf(.975, 1002)/2*per   # 2867, 3423
```

Sources read: `site/data/value_arms.json` (`current_world.selection_leg.what_would_settle_the_sign`),
`site/data/book_growth.json` (`years[].funnel_wins`, `prospect_ceiling_years`,
`prospect_ceiling_statement`), `docs/observability/settlement_ceiling_slope_20260921.json`,
`tools/generate_value_arms_data.py` (`_sign_remedy_buildability`, `_within_year_remedy`).
