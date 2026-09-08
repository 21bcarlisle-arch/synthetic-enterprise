**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — a second estimand beside `method_skill.concordance`) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — the fixed-horizon estimand that does not condition on survival

**Written 2026-09-08, before the estimand had been implemented and before any run of it.** Nothing
in this document is a reading of an output, because no output exists yet. It is filed so that the
result can refute it.

Commissioned by the Lane 0 delivery item, and specified by name in
`SEAT_RESULT_THE_UNSCORED_DECISIONS_ARE_EXACTLY_THE_DEPARTURES_SO_THE_METHOD_CONCORDANCE_CONDITIONS_ON_SURVIVAL_2026-09-08.md`,
whose "what is next" §3 says: *pre-register the replacement estimand before building it, and grade
it against this document.* That is what this is.

---

## Why a second estimand and not a fix

`method_skill.concordance` drops every priced decision whose term settled no day. That drop class
was measured — nine artefacts, 144 of 144 sampled drops — to be **exactly the renewals where the
household left**. So the published figure answers *given the household stayed, did the arm's price
rank the joint value it produced?* and is blind by construction to the decisions where the price
is what drove the household away. The bias runs in the direction the mission sentence exists to
catch: over-pricing leaves the sample rather than scoring low.

This is a selection in the estimand. It is not fixable inside the concordance without changing
what the concordance means, and the concordance is a defensible figure for its own narrower
question. **Both cuts stay on the page. A rung reported alone is a rung chosen.**

## What is being built

For every decision the value arm PRICED, the joint value it actually produced within a fixed
horizon of its own `term_start`:

- **Horizon** = `_TERM_DAYS` (365 days), reusing the same constant `_term_period_of` cuts on, so
  the horizon and the attribution boundary cannot drift into two numbers.
- **Outcome** = `household_saving_gbp + our_net_margin_gbp` in **pounds**, summed over the settled
  rows the view attributed to that priced term.
- **A decision whose term settled nothing scores 0.0** — a measured zero, not a missing value.
  Nothing was billed under the chosen price; that is the outcome, and it is a low one.
- **Signal** unchanged: `chosen_margin_gbp_per_mwh`.

### The three properties the item requires, and where each lands

1. **No conditioning on survival.** The denominator is decisions PRICED, not decisions settled.
2. **The horizon is fixed and declared**, and a decision whose horizon is still open at the end of
   the settled book is **censored explicitly and counted as a run-length artefact** — never
   silently dropped and never scored as a zero it did not earn.
3. **`no_published_counterfactual_rate_for_the_term` stays a named coverage gap.** It is excluded
   and counted, and it does not quietly become an outcome of zero. Same for
   `a_settled_row_carried_no_net_margin` and for an account with no settled row anywhere: an
   account we cannot see at all is not an account that produced nothing.

## The declared weakness, stated before the number

**The outcome changes units, from a ratio to pounds, and pounds carry scale.** The concordance
normalises by the counterfactual precisely so a large account does not outrank a small one for
being large. The fixed-horizon estimand cannot: a household that left has no counterfactual over
the horizon, because it has no metered volumes over the horizon. Imputing one from an earlier term
would be an inference the world does not hand us, so it is not done.

That means **two things change at once** between the published figure and the new one — the
population (departures enter) and the unit (ratio becomes pounds) — and by this project's own rule
a result that moves when two things changed cannot be attributed. So the estimand publishes a
**three-leg bridge over nested populations, one variable per step**:

| leg | population | outcome | isolates |
|---|---|---|---|
| 1 `settled_only_ratio_outcome` | decisions that settled within the horizon | ratio | reproduces the concordance's construction |
| 2 `settled_only_pounds_outcome` | *the same* | **pounds** | THE UNIT |
| 3 `every_priced_decision_pounds_outcome` | leg 2 **+ the zero-outcome decisions** | pounds | THE POPULATION |

Leg 1 is a control, not a finding: with no censoring it must reproduce the published concordance
through a different code path, and a disagreement means this estimand's plumbing is wrong rather
than that anything was learned.

## The predictions

Written now, against the 2026-09-08 run (214 priced, 168 scored, concordance **0.5334**, null
interval [0.4492, 0.5503], p = 0.197 — *already indistinguishable from chance*).

**P1 — the scored population rises.** From 168 to roughly 208, being 214 priced less the 6
`no_published_counterfactual_rate_for_the_term`, less whatever censoring takes. **I cannot predict
the censored count** and am not pretending to: it is a function of where the priced terms sit
relative to the end of the settled book, which I have not looked at. If censoring is large, P1 is
wrong and the reason is a run-length artefact, which is exactly what property 2 exists to surface.

**P2 — the fixed-horizon concordance FALLS below 0.5334.** The decisions entering are the ones that
produced least, and if the arm's high margins are part of what drove those households away, high
signal pairs with lowest outcome. **If it RISES, the finding is worse, not better**: it would mean
the arm was over-pricing the households it KEPT, which is a different and more damaging reading
than survivor-blindness.

**P3 — the unit change (leg 1 → leg 2) moves the figure by LESS than the population change
(leg 2 → leg 3).** I have no prediction for the SIGN of the unit effect and will not invent one;
scale confounding can go either way.

**P4 — what will NOT move, and it is independent by construction, not merely conceptually.**
`null_constant_signal_concordance` stays **exactly 0.5** on every leg. A constant signal ties every
pair, and `_concordance` counts a signal tie as a half regardless of the outcomes — so the null is
a function of the signal alone and cannot see the population or the unit. If any leg's null is not
0.5, the estimator is broken and no leg's number may be read.

**P5 — the zero-outcome decisions will be the departures.** Not required by the estimand, but
measured beside it as an independent check: the count of zero-outcome decisions the world recorded
as churned should equal the count of zero-outcome decisions. A residue refutes the survivorship
finding's set identity on a new key and is worth more than agreement.

## How this gets graded

Against `SEAT_RESULT_..._CONDITIONS_ON_SURVIVAL_2026-09-08.md`, which predicted 168 → ~208 and a
FALL, and against the five predictions above, in a result doc that names each as held or refuted
**beside** the number, not in place of it. A prediction filed after the answer is not a prediction.

## What this does not claim

Not that the fixed-horizon figure is the better estimand. It answers a wider question with a
weaker outcome; the concordance answers a narrower question with a scale-free one. Both go on the
page, both carry their bound, and which one a reader should weigh is a judgement this document
does not make for them.
