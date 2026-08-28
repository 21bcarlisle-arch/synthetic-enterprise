# A48 — measuring the METHOD, not the book

**Atom:** `A48_enterprise_value_is_the_method_not_the_book` (lane `A_strategy_governance`, epoch 3, L0→L2)
**Provenance:** the director's mission, 2026-08-28 — *"the enterprise value is the automated method
for finding those customers, not the book itself."*
**Depends on:** `A47_the_score_has_no_household_side` at L2 (landed `039f202ce`), which supplies the
household side the joint figure needs.
**Status:** FRAME. Nothing here is built.

---

## 1. The gap, stated so it can be closed

`saas/enterprise_value.py` computes the discounted net margin of the book. Under the superseded
mission that was the headline. Under this one the book is the *evidence* and the method is the asset,
and **nothing in the repository measures the method.**

Three questions the mission asks that have no instrument:

1. How reliably does the machine **find** an individual customer it can create value for?
2. What does finding one **cost** — search, model, offer, persuade, including compute?
3. Is either **improving**, run over run?

This FRAME proposes an instrument for (1) only. (2) needs a cost-to-acquire ledger that spans
`saas/channel_roi.py` and the compute figures in `docs/observability/`, and (3) is meaningless until
(1) exists and has been run more than once.

## 2. What "finds a customer it can create value for" means as arithmetic

The company's per-customer pricing arm produces, at each renewal, a **signal**: the margin it chose
for that customer, `chosen_margin_gbp_per_mwh`. The distribution is genuinely per-customer — 24
distinct margins across 25 priced renewals in the 2026-08-28 run, against the flat rule's single
£2.00.

The **outcome** the mission cares about is two-sided, and since `A47` it is computable:

```
joint_value = household_saving_gbp + our_net_margin_gbp
```

Normalised, so a large account does not outrank a small one for being large:

```
joint_value_ratio = joint_value / counterfactual_gbp
```

**The method has skill if the signal predicts the outcome** — if the decisions the arm priced highest
are not the ones where the relationship was destroyed. Scored as a rank statistic over the priced
decisions, the same shape as `discrimination_auc` in `tools/run_value_cycle_ab.py`, with the outcome
swapped from *did they stay* to *was value jointly created*.

## 3. Why this is a different question from the AUC already published

`discrimination_auc` asks whether the company's **belief about churn** ranks who leaves. It scored
**0.4653** — below a coin flip, so the belief carries no information about who stays.

The method question is not the same and could come out differently in either direction:

- A company can rank churn badly and still create value, if the accounts it over-prices are ones
  where the household keeps enough that the relationship survives anyway.
- A company can rank churn well and create nothing, if it uses the ranking purely to extract — which
  is the maximiser's behaviour the director's sentence names, and it would show as a **high** churn
  AUC beside a **flat** joint-value curve.

That second case is the one worth being able to see, and no instrument today can.

## 4. The problem that has to be solved first, named rather than deferred

**`A47`'s view aggregates by customer-YEAR. Decisions are per TERM.** Terms are 365 days from an
arbitrary start, so a term straddles two calendar years for most accounts, and a customer-year mixes
the tail of one priced decision with the head of the next. Attributing a year's joint value to one
decision would be wrong in a way that is invisible in the output.

Two candidate resolutions, and this FRAME does not choose between them:

- **(a) Generalise the grouping.** `build_household_value_share` takes a key function over records
  instead of hard-coding the year. The caller supplies `(customer, term_start)` from the arm's own
  decision log. Cleanest, and the change is small — the year is already computed in one place
  (`_year_of`).
- **(b) Attribute proportionally.** Keep the year grouping and split each year's joint value across
  the terms it overlaps, by days. Cheaper to write and introduces an attribution assumption that
  would then have to be defended in every reading.

**(a) is the recommendation.** (b) buys nothing and creates a figure whose caveat is longer than
its derivation.

## 5. The bound, stated before the number rather than after it

**25 priced decisions across 9 accounts.** A rank statistic on 25 points with that much clustering
has a wide confidence interval and every account is potentially influential. This is the same
resolution wall that made the 2026-08-28 chase-on/chase-off churn comparison unreadable
(`WORKER_FINDING_THE_DEFENDING_MARKET_IS_UNMEASURABLE_ON_SEVENTEEN_DECISIONS`), arriving on a
different question.

Two things make it *less* bad here than there:

- **The outcome is continuous.** Joint value in pounds has no 1/17 quantum, so a small effect is
  small rather than invisible.
- **Every priced decision contributes**, not only the ones the world rolled an event for. The 25
  are all matched in the current run (`scored_share_of_priced = 1.0`).

It is still 9 accounts. **`A46` (book depth) is upstream of this being worth much**, and that
remains the director's decision.

## 6. What L2 would be

A figure, published with its bound, answering: *does the arm's own per-customer signal rank joint
value created better than chance?* Plus the null that makes it readable — the same statistic computed
on the flat-rules arm, whose signal is a constant and must therefore score exactly 0.5. A method-skill
number without that null is unfalsifiable.

**What L2 is NOT:** a claim about cost-to-find, or about improvement over time. Both are named in §1
and neither is in scope.

## 7. Why this atom is `build` and not `idle`

It needs no world change, no book change and no decision from the director. It reads artefacts two
existing instruments already produce. The reason it is not built in the same commit as `A47` is §4:
the grouping change is a real design choice on a module that landed an hour earlier, and making it
in the same breath would have meant shipping a generalisation with no second caller to justify its
shape.
