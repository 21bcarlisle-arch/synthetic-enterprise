# WORKER FINDING — a decision metric whose choice set has no "do nothing" in it cannot report a loss

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-09 (worker tick)
**Class:** R15 fail-open — an outcome the control is structurally incapable of expressing
**Advances:** C14_thermal_parameter_inference
**Status:** FIXED at the instance; the CLASS question below is open and is the reason this is filed

---

## The observation (`observed-with-evidence`)

The fabric coupled triad's money-consequence metric ranks retrofit measures on the
company's fabric belief, ranks them again on the SIM truth, and charges the premise
when the top choice differs. Probed directly at the ledger's own 7.4 p/kWh gas rate:

```
hlc=0.08 heat=4000  -> [('time_shift', -41), ('solar_pv', -1080), ('insulate', -3336), ('heat_pump', -8721)]
```

Every option loses money, and `time_shift` — the recommendation — loses £41 over its
lifetime: spend £300 to save £259. The truth arm picks the same measure, so
`chosen == best`, and the metric records a **perfect decision**.

The panel's `money_consequence_inferred` had been sitting at `misrank_rate 0.0,
forgone £0.00` and reading as good news.

## Why it happened

The choice set contained only measures. There was no `do_nothing` option, so the
ranking had no zero to compare against and the decision function was structurally
incapable of returning "nothing here is worth buying" — which is the answer a real
supplier gives most of the time. The metric could only ever see *disagreement about
which* value-destroying measure to buy, never *that* one was being bought.

Two further things followed from the same root, and both are the more interesting
half of the finding:

* **The decision lived in the harness that scores it.** No company module made this
  decision at all. C14's `is_actionable` and `interval_95` — the uncertainty model the
  atom was most careful about — were computed by nothing and read by nobody.
* **A refusal cost nothing.** With no do-nothing outcome, "the company declined" was
  unrepresentable, so a company that never acted would have scored flawless.

## What was done

The decision moved to `company/pricing/fabric_intervention.py`, with `DO_NOTHING` a
first-class member of the choice set at exactly £0, and three separately-counted
outcomes: bought-wrong, declined-where-value-existed, and value-destroying. The
harness now calls the company's rule twice — once on the belief, once on the truth
only it can see. Both new counters are R15-proven to fire.

The wall forced a better model on the way through: the harness had made the belief
consequential by scaling the company's demand estimate by `belief / truth`, which
cannot live in company code because it needs the truth. The company instead
attributes part of its own bill to fabric (`HLC × degree days × 24`, capped at the
bill), so insulation saves a share of the *fabric* portion rather than of the bill.

## The result, which disagrees with itself and is reported both ways

| | EPC register belief | C14 posterior |
|---|---|---|
| prediction gap vs truth | **0.2049** | 0.2325 |
| forgone lifetime value | £41,586 | **£16,261** |

The company's own inference is **worse at predicting fabric and 61% cheaper in
decisions**, because narrowing the uncertainty converts refusals into correct
actions. Reporting either number alone would be a lie in one direction or the other.

## The class question — why this is filed rather than just fixed

**Where else is a decision metric scoring a choice set with no null option in it?**

The instance fix does not close the class (R10). Every belief-vs-truth pair in this
codebase that scores a *decision* rather than an *error* is exposed to the same
shape, and the tell is specific and greppable: a ranking function that always
returns a top choice, with no zero row and no caller checking the sign of the winner.
The payment triad's dunning decisions and the cohort coupler are the obvious places
to look next.

Three weaker controls were also corrected in passing, each of the "reads stronger
than it is" kind:

1. A carbon-invariance test guarded on the *count* of misranked premises rather than
   on *which* premises — two flipping opposite ways keeps the count and changes every
   kWh. It now asserts the decision vector, computed independently of the metric.
2. "The money consequence scales **linearly** with the unit rate" was false. Capex
   does not move with price and does not cancel; the relationship is **affine**.
   Doc, printout and test all now say so.
3. The decision fixtures were priced at 25 p/kWh — an *electricity* rate, at which the
   heat pump wins on delivered efficiency whatever the fabric. A belief 85% low cost
   exactly nothing and every fabric-sensitivity test below it was vacuous. That
   saturation is now a standing test in both directions.

## And one thing R15 found that the design had not

Guards 2 (no positive value) and 3 (not robust to the belief's own interval) **overlap**:
a winner negative at the estimate is negative at the pessimistic bound too, so
removing the do-nothing option does *not* resurrect the loss-making sale. A mutation
test asserting it would have been simply false.

The lesson is recorded in the suite: **"the outcome did not change under mutation" is
not evidence that a guard is inert.** Each guard is instead shown firing alone, on an
input the other cannot refuse.
