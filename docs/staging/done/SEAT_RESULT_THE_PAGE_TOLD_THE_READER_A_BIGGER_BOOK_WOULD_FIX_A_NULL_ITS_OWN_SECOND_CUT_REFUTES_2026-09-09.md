**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — discharge the survivorship finding's last open leg) · **Class:** controls_that_cannot_fail

# RESULT — the page told the reader a bigger book would fix a null its own second cut refutes

Item 4 of `SEAT_RESULT_THE_UNSCORED_DECISIONS_ARE_EXACTLY_THE_DEPARTURES_SO_THE_METHOD_CONCORDANCE_CONDITIONS_ON_SURVIVAL_2026-09-08.md`,
which was left open on purpose: *"changing the sentence and adding the block that refutes it in
one commit would leave nothing able to show the two disagreed."* The refuting blocks landed on
09-08 and 09-09. This is the correction, and the disagreement is in the record above it.

## What a reader met

Under the headline concordance, in muted 11.5px, the producer's own words:

> *"The observed value sits INSIDE the interval a random signal produces, so this run does not
> distinguish the method from chance in either direction. **That is a statement about how few
> decisions there are, not about the method.**"*

A few hundred pixels lower, on the same page, from the same run:

| cut | decisions | 95% null interval | half-width | observed | verdict |
|---|---:|---|---:|---:|---|
| headline — survivors, ratio | **168** | 0.4494–0.5504 | 0.0505 | 0.5338 | inside |
| every priced decision, pounds | **161** | 0.4458–0.5540 | **0.0541** | 0.4210 | **OUTSIDE**, p=0.0045 |

**Fewer decisions. A wider interval. And it found something.** An instrument with strictly less
power to detect anything detected something on this book — so however few decisions this book has
earned is not what stops the figure above saying anything. The sentence names a cause the
interval cannot support, and it names the one cause a reader can act on by buying book depth.

That is the same error the survivorship finding was filed for, one sentence further up the page.
`drop_out`'s reading was corrected on 09-08; the headline's own was not, because it is written in
`_null_spread` — a generic helper shared by every leg — and nobody had looked there.

## What landed

1. **`run_value_cycle_ab._null_spread`** no longer attributes an inside-the-null reading to sample
   size. It names the three causes one interval cannot tell apart — too few decisions, no effect,
   a population selected so the effect cannot appear — and says a second cut is what separates
   them. The claim was unsupported on every leg it was ever emitted for, not only this one.
2. **`generate_value_arms_data._skill_sample_size_explanation`** — the verdict, composed from the
   run's own two intervals. **The run's own sentence is published unedited beside it**, for the
   reason the finding gave for leaving it alone: a generator that rewrites what a run said
   destroys the evidence that the two disagreed. Three verdicts, all reachable:
   `refuted_by_this_run`, `not_settled_the_other_cut_had_more_power`, `still_live`.
3. **The refutation reaches the reader** — amber, immediately under the muted sentence it
   qualifies, with both decision counts. `site/capabilities/index.html`, re-published feed.

**The refutation needs BOTH legs of its power comparison** — the second cut scored on no more
decisions AND against an interval no narrower. Either one failing means it simply had more power,
which explains its own verdict and says nothing about the first, and that case reports as
unsettled rather than as a refutation. Both halves are driven separately in the controls, because
widening one predicate of an ANDed pair catches nothing.

**What it does NOT claim.** The two cuts differ in the population *and* the unit, so this block
says only that sample size is not the explanation — it does not attribute the null to the
conditioning. That attribution is the bridge's, one leg at a time, already published beside it.

## Controls

**Poison rounds first**, because "refuted" is the answer this book happens to give and a block
returning it on every input would pass a control written against today's answer: no headline
interval; the headline clearing its own null (no "we cannot tell" is being made, so no explanation
is owed); and no permuted second cut — which reports UNCHECKED, not "the sentence is fine".

- `tests/tools/test_generate_value_arms_data.py::test_the_sample_size_explanation_refuses_before_it_asserts`
- `tests/tools/test_generate_value_arms_data.py::test_the_sample_size_explanation_needs_BOTH_legs_of_its_power_comparison`
- `tests/tools/test_generate_value_arms_data.py::test_the_sample_size_explanation_reads_the_published_runs_own_two_intervals`
  — expectation **derived from the artefact's own intervals**, so it stays green the day an honest
  run changes the verdict and goes red the day the block stops reading the run.
- `tests/tools/test_generate_value_arms_data.py::test_the_page_publishes_the_runs_own_sentence_beside_the_verdict_and_never_instead_of_it`
- `site/test_the_baseline_comparison_reaches_the_reader.py::test_the_refutation_of_the_bigger_book_reading_reaches_the_reader`
  (the lift, on the published feed), plus `..._survives_reads_differently` and
  `..._a_run_that_could_not_check_it_says_so_rather_than_nothing`.

**Mutation battery: 7 mutations, 7 killed** — drop either predicate of the conjunction; `and`→`or`;
invert the distinguishes flag; fail open on each of the two refusal branches; one sentence for
every verdict. **Poison round on the render: the three door controls all red with the block
removed from the page**, so they measure the lift and not the feed.

## The finding's own prediction, graded

It predicted the fixed-horizon estimand would score **~208** of the 09-08 book and the concordance
would **fall**. Scored: **161**. Direction right, count wrong by a quarter — the prediction did not
anticipate the 47 decisions censored for an open horizon, which the estimand names as the
run-length artefact it is. Kept here beside the answer rather than revised.

## What is next

- **The producer's corrected sentence has not been run.** `_null_spread`'s new wording reaches a
  page only on the next A/B run; until then the feed carries the old sentence and the amber line
  refutes it. That is the intended state, not a gap — but the two should agree after the next run,
  and the block is keyed to the numbers so it will still read correctly when they do.
- **One more candidate of the same shape, found by sweeping the feed's own prose and NOT fixed
  here.** `method_skill.what_it_could_have_detected.the_book_this_would_need` publishes
  `the_observed_effect_is_attainable: true` at 376 scored decisions, with
  `why_only_a_larger_book`: *"Only a larger settled book does."* That is power arithmetic on the
  **survivor-conditioned** estimand — so it tells a reader that buying book depth would resolve a
  figure whose sample the same page says is selected. It is a weaker instance than the one closed
  here (it is arithmetic about detectability, not an attribution of the null) and it is a
  different subject, so it is recorded rather than folded in. **Not measured, not fixed:** the
  question is whether that arithmetic should be published on the unconditioned cut instead, where
  a bigger book is not answering a selection.
- The rest of the feed's prose carries no other sample-size attribution — swept over every string
  in `site/data/value_arms.json` for the remedy words, and the remaining hits are the two claims
  already WITHDRAWN on the page and the drop-out classes, which are about widening the sample and
  not about why the figure is silent.
