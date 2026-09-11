# [WORKER FINDING] The live site publishes an average bill shock of 200%+, and it predates today's work

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-01, by asking whether a defect I had just created had siblings. It did, and the sibling was older and already public.

## Class registration

Belongs to `figures_on_a_superseded_clock`.

## What is live right now

`site/data/dashboard.json`, `monthly_ops.monthly`:

    avg_shock_pct = 205.6
    avg_shock_pct = 266.1
    avg_shock_pct = 203.3

**An average monthly bill shock of 200–266%.** That figure says the typical household's bill more
than trebled, every month. It did not.

The site's own provenance names run `b17d86e3e` — which **predates every change I made today**. This
is not a consequence of moving the bill-shock baseline; the near-zero denominator was reachable
under the old TRUE-bill baseline too, because a stub first bill has a small true total just as it has
a small issued one.

## The measurement

Whole book, on the current run, `mean(bill_shock_pct) * 100` as the dashboard computes it:

| | value | bills |
|---|---:|---:|
| as published | **114.0%** | 11,314 |
| with baselines under £5 excluded | **33.3%** | 11,255 |
| dropped | | **59 (0.5%)** |

**Fifty-nine bills out of 11,314 carry the entire difference between 114% and 33%.** They are
divisions by a near-zero previous bill — a month that settled to a few pence after a credit, or a
stub period.

At year level the same artefact put **2022 at 617%** against 26–38% for every other year; with the
floor, 2022 reads **42% and becomes the highest year**, which is correct — 2022 was the crisis. **The
artefact was not merely adding noise, it was burying the real signal**: while every year's average is
dominated by a handful of divisions by nothing, no year can be compared with any other.

## Already fixed, and by accident

`BILL_SHOCK_BASELINE_FLOOR_GBP` landed in `41cdd5b51` about an hour before this was found, for a
defect I had introduced myself at year level. It fixes this one too, because it is the same defect:
below a £5 baseline no shock is computed at all. **The next publish corrects the live figure with no
further change.**

That is worth saying plainly rather than presenting as foresight. I built the repair for my own bug,
then went looking for whether that bug had siblings — and the sibling turned out to be older, larger
in reach (it is on the public site), and already covered.

## What is NOT fixed by it

The earliest months still read high — 2016-02 at 121% and 2016-03 at 122% with **no** bills dropped
by the floor. That is a **small-n** effect, not this defect: the book is ramping up, those months
hold 12 and 22 bills, and a genuinely volatile early book produces genuinely large percentage
changes. It should not be repaired by a floor and it is not a wrong number; it is a thin one. **What
it needs is a population bound published beside it**, which is this project's standing rule for a
figure whose sample size does not earn it, and which the dashboard does not currently carry for this
field.

## Why it is `figures_on_a_superseded_clock`

Strictly the class is about a summary frozen before its rows were mutated. This is the adjacent
member of the same family: a summary computed over rows whose denominators make the summary
meaningless — a mean over a distribution whose p99 is fifteen times it. In both cases the published
scalar has stopped being a summary of the rows it claims to summarise, and in both cases nothing
downstream can tell.

## What is owed

1. **Publish the population bound beside `avg_shock_pct`**, per the standing rule. A 121% average
   over twelve bills and a 33% average over 1,600 are not the same kind of statement.
2. **Consider a median rather than a mean** for this field. A mean is the wrong summary for a
   distribution this skewed even after the floor, and the median is what a reader thinks they are
   being told.
3. **Neither is done here.** Both change a published figure and belong with the pre-registration
   discipline, not bolted onto a finding.
