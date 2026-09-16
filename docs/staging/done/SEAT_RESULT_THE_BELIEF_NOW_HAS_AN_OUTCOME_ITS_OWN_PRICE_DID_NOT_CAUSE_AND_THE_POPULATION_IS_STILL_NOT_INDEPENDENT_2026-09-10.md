**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the belief now has an outcome its own price did not cause, and the population is still not independent

RECORDED rather than BLOCKING: nothing is refused by this, and the field it adds is written by the
next A/B pass rather than by this commit. Written up because the second half is the part that will
be misread — the block earns the OUTCOME's independence and not the POPULATION's, and those are one
sentence apart on the page.

**Filed:** 2026-09-10, delivery seat. Continues
`what-run-would-settle-the-within-year-concordance-and-can-this-world-supply-it`, whose own *What is
next* named this as the cheapest item on the page.

---

## The premise, re-measured before anything was built

The drawn Lane 0 item is **spent**. Both halves of it landed in `ad7a2f89f` on 2026-09-10: the
within-year remedy priced in its own unit (584 scored decisions, ~314 accounts, 9,062 same-year
pairs, a book of ~1,017 priced renewals out of 9,668 offered, at least 1.16 machine-hours and at
least 6.4 GB peak, attainability `None` and stated as `None`), and the independence answer beside
it. The claim `what-run-would-settle-the-within-year-concordance-and-can-this-world-supply-it` was
bound to that commit at 1789033910 and then re-drawn at 1789038298 — the doorbell is reading a
claim that had already been discharged, not an open one.

So the work of this turn is the successor that landing named, and it is one field.

## What was missing, in the generator's own words

`generate_value_arms_data._independence` already publishes the whole specification and the reason
the answer was `False`:

> the control arm publishes no per-decision rows to score against: `control_arm.renewals_priced_by_the_arm`
> is 0, and its roster reaches this artefact only as account-level totals and the churn roster diff
> above. There is **no (account, term, retained) list on the control side** to put the value arm's
> `believed_p_retain` beside.

And the three conditions any independent population must meet: the outcome must not be a function
of the belief being graded; the belief must still be the value arm's, per (account, term); and the
population must be fixed **before** the outcome is read, because any membership rule that consults
`retained` — including *"the arms agreed"* — reintroduces the defect under a tidier name.

The control arm satisfies the first condition by construction. It rolls churn for the same
households in the same world at a flat level **no per-household belief set**. Both arms already run
in one pass, so this was a field the run did not write, never a run nobody had done.

## What ships

`tools/run_value_cycle_ab.belief_against_control_outcomes(value, control)`, published in the
artefact directly beside `belief_vs_outcome`. The value arm's `believed_p_retain` per
(account, term_start), scored against whether that household stayed **under the control arm**.

Keyed exactly as `belief_vs_outcome` keys its outcome and as `_churned_renewals` keys a departure —
raw `customer_id` against `event_date`. A second idea of the key would make the two gradings
incomparable with nothing saying so, which is the entire value of publishing them side by side.

## THE PART THAT WILL BE MISREAD, and it is on the face of the block

**The outcome is independent. The population is not.** Membership is the set of renewals the VALUE
arm priced — fixed before any outcome is read, so it is not the post-treatment subset the page
already refused. But a household the value arm drove out early reaches fewer later terms, so the
**tail** of that set is still conditioned on value-arm survival.

That residue is not left to prose. `population_terms_absent_from_the_control_world` counts every
priced term the control world logged no lifecycle event at, with a sample, and those rows are
**excluded rather than counted as retained** — the same treatment, for the same reason, as
`belief_vs_outcome.unmatched_decisions`. A reader who takes population independence from outcome
independence draws the stronger conclusion this run cannot support, and the block says so in
`population_basis` rather than in a note.

## R15 — poison round first, then the battery

Reachability was proved before anything was asserted about the live branch, because *survived*
means two opposite things. Three poisons, each reverted, each firing on a **named** test:

* `control_events` read from `value["phase2b"]` instead of `control["phase2b"]` — the copy-paste
  tautology, and the one that would have published "independence" as a bit-identical copy of
  `belief_vs_outcome`. **Four tests red**, including the two that exist for exactly this.
* the absent-term branch replaced by `control_outcome[key] = True` — FAIL-OPEN, a term the control
  world never reached absorbed as a retention. `..._is_counted_not_absorbed` red at 3 == 1.
* the empty-control-log refusal replaced by `control_events = []` — FAIL-OPEN, the most reassuring
  wrong answer this block could carry: a clean AUC over a population nothing was measured on.
  `..._refuses_by_name_rather_than_reporting_retention` red.

The load-bearing control is `test_the_two_gradings_disagree_when_the_arms_outcomes_disagree`: one
belief, two worlds, AUC 0.0 under the value arm and 1.0 under the control. If this block could not
produce a number **different** from `belief_vs_outcome`'s, it would be an expensive restatement and
a reader meeting the two side by side would be told independence by a copy.

192 tests in `tests/tools/test_run_value_cycle_ab.py` green after restore.

## What is next

**The figure does not exist yet and must not be quoted until it does.** This commit adds the field;
the next A/B pass writes it. Nothing on `site/capabilities/` should move until an artefact on disk
carries `belief_against_control_outcomes.available: true` — and when one does, the page's
`is_it_available_today: False` and its `what_would_have_to_be_recorded` clause are the two sentences
that go, in that order.

A prediction, filed before the run rather than after it, so it can refute me: the two AUCs will
**not** be far apart. The four accounts the arms disagreed about are 4 of 40 departures on the
2026-09-09 run, and 12 of the 123 scored rows sit on the five accounts in the disagreement set. A
figure that moves a lot on a 10% population change would be telling us about the sample and not
about the belief. What the block is worth is that it can now be **checked** rather than caveated.
