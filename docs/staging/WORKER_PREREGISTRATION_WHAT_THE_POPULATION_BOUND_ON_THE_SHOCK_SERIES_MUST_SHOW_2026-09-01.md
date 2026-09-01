# [WORKER PREREGISTRATION] What publishing the population bound on the shock series must show

**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Filed:** 2026-09-01, **before the change was written and before the series was recomputed.**
Predecessor: `WORKER_PREREGISTRATION_WHAT_THE_BASELINE_FLOOR_DOES_AND_DOES_NOT_FIX_2026-09-01`,
which bound the next commits to exactly this.

## What this commit is, and what it deliberately is not

The delivery instruction's item **(d)**: *"Publish the population bound beside the figure, per the
standing rule. 2016-02 reads 121% over 12 bills and no floor drops any of them — that is thinness,
not this defect, and it must not be repaired by a floor."*

This is **not** the definition split (item b) and **not** the prepayment decision (item c). Those are
separate commits by explicit instruction, because three changes to one published figure are
unattributable. **This commit moves no existing published figure at all** — it is purely additive,
and D1 below is exactly that claim, stated so it can be falsified.

## What the standing rule actually demands

> *"A figure published without the bound its sample size earns is worse than no figure."* (CLAUDE.md)

`monthly_ops.monthly[]` already carries `shock_count`, so an `n` is technically beside the figure.
That is not the rule being satisfied — it is the raw material for satisfying it. **A reader given
`n = 5` and `315.6%` still has no way to know whether that month differs from a typical one.** The
bound the sample earns is an interval, not a count.

## The choice of bound, and why it is derived rather than picked

**No minimum-`n` threshold is introduced.** A cutoff ("suppress months under 20 events") would be a
number picked because a number was needed, and this project has paid for that shape repeatedly. The
published record establishes no minimum sample size for a bill-shock mean, because no published
source is measuring this quantity at all.

So the bound is computed **from the sample itself**: a deterministic **percentile bootstrap** of the
mean, 2,000 resamples, seeded on the month string. Chosen over a normal-approximation standard error
because the distribution is the thing under complaint — post-floor, p99 is **19.8×** the median — and
a symmetric interval around a mean of five skewed draws would state a precision the sample does not
have. The bootstrap makes no distributional assumption.

**The median is published beside the mean, not instead of it.** Replacing the mean would move the
headline from 108.1% to 49.7% and would be picking the flattering statistic —
`the_robust_statistic_can_also_be_the_flattering_one`. Both, with `n` and the interval, is the honest
package; either alone is a different claim wearing the same label.

## The predictions

**D1 — purely additive.** `avg_shock_pct` and `max_shock_pct` are unchanged to the decimal in all 113
published months. If any month's mean moves, this commit has done something it did not declare and
the result is unattributable.

**D2 — the mean and the median disagree where it matters.** In all twelve months publishing a mean
above 200%, `median_shock_pct < avg_shock_pct` and `mean ÷ median ≥ 1.5`. *(Directional check against
the predecessor's already-measured table; it is here so a coding error that silently emits the mean
twice cannot pass.)*

**D3 — the bound is wide where the sample is thin.** For **2016-08** (`n = 5`, mean 315.6%), the 95%
bootstrap interval is wide enough that its **lower bound falls below the whole-book median of
49.7%** — i.e. the sample cannot distinguish the worst surviving month from a typical one. **If that
interval comes out narrow, D3 is refuted and the bound is not doing its job**, and I would rather
find that here than publish a precise-looking interval.

**D4 — the unknown one.** Across all 113 months, **more than 56 (a majority) will have a 95% interval
that contains the whole-book median of 49.7%** — that is, most published months are not
distinguishable from typical. I do not know this number. If it comes out small, then the series
carries more real signal than I am crediting it with, and the honest conclusion is that the
population bound is a smaller finding than the instruction treats it as.

**D5 — the bound is not the repair for the skew.** After this commit the mean is still a mean over a
skewed distribution. **Nothing here may be cited as having fixed that**, and the predecessor already
bound me to that: *"The floor is not the repair for the surviving months, so nothing below may be
justified by it."* The same applies to the bound.

## The second claim: each field names its population

Two published fields are both called the average bill shock and are means over different populations
(measured in the predecessor, unpredicted):

| field | population | 2016 |
|---|---|---:|
| `financial.annual[].avg_bill_shock_pct` | **every bill with a computable shock** | 30.8% |
| `monthly_ops.monthly[].avg_shock_pct` | **only bills already flagged as a shock (≥20%)** | 110.6% |

**D6.** After this commit each of the two carries its population **on the surface, in the artefact a
reader is served**, not in a source comment. The names are not changed — renaming would break every
existing consumer and that is a different commit — so the population is carried as a sibling field.

## Outcome

Measured on `run_output_b9418ce19_20260901T125311Z.json` — the same artefact the live
`site/data/dashboard.json` was generated from, so D1 is a like-for-like comparison and not a
comparison across runs.

**Three confirmed, two refuted.** The two refutations are the useful part and both are kept.

### D1 — CONFIRMED

**Zero of 113 months moved**, on either `avg_shock_pct` or `max_shock_pct`. A whole-artefact field
diff against the published `dashboard.json` shows added keys only: `median_shock_pct`,
`avg_shock_pct_ci95_low/high` (113 each), the two `financial.annual[]` population fields (10 each),
and the two container notes. Nothing removed, nothing changed but `meta`.

### D2 — REFUTED in one month of twelve

`median < mean` holds in all twelve. The **ratio ≥ 1.5 fails in 2021-01: 224.5% over 155.2% is
1.45×.** The prediction was written from the predecessor's table without dividing the column I was
about to assert on — the ratio was there to be computed and I asserted a bound on it instead of
reading it. Harmless to the build (no control was keyed to 1.5) and worth keeping as the reason the
control that shipped is keyed to *median < mean*, which is the property, rather than to a ratio,
which is today's answer.

### D3 — CONFIRMED, and it is the sharpest number here

**2016-08: mean 315.6%, median 68.3%, 95% interval [40.2%, 788.5%]** off five events.

The lower bound, 40.2%, is **below the whole-book median of 49.7%.** The worst surviving month in the
published series cannot be distinguished from a typical one. That sentence is what the bound exists
to let a reader say, and before this commit the surface said "315.6%" and stopped.

### D4 — REFUTED, and it makes this a smaller finding than the instruction assumed

I predicted **more than 56** of 113 months would have an interval containing the whole-book median.
The answer is **28** — a quarter, not a majority.

| | months |
|---|---:|
| interval wholly **above** the book median (genuinely elevated) | **84** |
| interval **contains** it (cannot be told from typical) | **28** |
| interval wholly below it | 1 |

So the series carries considerably more real signal than I credited it with, and I pre-committed to
saying so: **the population bound is a smaller finding than the delivery instruction treats it as.**
Most published months really are elevated and the reader was not being misled about that.

### And the thinness story in the instruction is wrong

The instruction reads 2016-02's 121%-over-12-bills as *thinness*. The measurement says thinness is
not what makes a month unreadable:

| | months | of which interval contains the book median |
|---|---:|---:|
| n < 20 | 32 | 8 (**25%**) |
| n ≥ 20 | 81 | 20 (**25%**) |

**Identical.** A month with 93 events (2025-06) has an interval 10.5pp wide; a month with 12
(2017-04) has one 10.9pp wide. What makes a month unreadable is the **dispersion inside it**, not the
count — 2016-08's interval is enormous because its five events disagree wildly, not merely because
there are five of them.

This is why no minimum-`n` cutoff was introduced, and it is now measured rather than merely argued:
a suppression threshold on `n` would have hidden 24 thin months that are genuinely elevated while
leaving 20 well-populated months that cannot be told from typical still reading as findings.

### D5 — held

The mean is still a mean over a skewed distribution. Nothing in this commit repairs that, nothing
below may cite it as having done so, and the definition split (item b) remains the thing that decides
whether this series should exist in one piece at all.

### D6 — CONFIRMED

Both fields carry their population in the served artefact. `monthly_ops.avg_shock_pct_population`
names the flagged-only population **and points at `financial.annual[].avg_bill_shock_pct`**;
the annual rows carry `avg_bill_shock_pct_population` pointing back. Naming one would have been
half a repair — a reader finding only one label would read the unlabelled field as the general case.

**The annual field gets its NAME here and not its COUNT, and that is a scope decision made at the
gate rather than a design one.** The count has to come from the run producer,
`saas/reporting/annual_report.py`. That file is carrying **another lane's uncommitted work** (the
SVT departure/decision forwarding of 2026-08-31), which the wall-channel census caught when the
first attempt to land this staged it — two new `F_published_artefact` crossings that are not mine
and that a pathspec commit would have swept. The producer field was backed out rather than carried,
and the consumer field with it: a field that could only ever be null until the producer lands is a
stub, not a bound. The annual mean therefore carries its population name and no `n` until the tree
is clear of that lane's work.

**The bound proper is complete for the field that needed it.** The 200%+ figures the instruction was
drawn for are all in `monthly_ops.monthly[]`, and every one of those 113 rows now carries `n`, a
median, and an interval.

## Two things found by running it that were not predicted

1. **`site/data/dashboard.json` is not reproducible from its own named generator.**
   `tools/generate_dashboard_data.py` does not write `customers.portfolio_event_stream` at all — a
   second tool, `tools/generate_portfolio_event_stream.py`, appends it afterwards in the publish
   lane. Re-rendering with the generator alone **silently deleted 200 published rows**, and nothing
   would have reported it. Caught by diffing the artefact rather than trusting the regeneration —
   the `re_rendering_a_downstream_page_is_not_reproducing_the_run` shape, in the publish lane's own
   output.
2. **That event stream is not deterministically ordered.** Re-running its generator on unchanged
   inputs yields the identical multiset of 200 events in a different order (66 rows differ by
   position alone; verified as a permutation, not a content change). Not repaired here and not this
   commit's subject; recorded so the reorder in this commit's diff is not read as a data change.

*Both are observations about the publish lane, not about bill shock. Neither changes a figure.*
