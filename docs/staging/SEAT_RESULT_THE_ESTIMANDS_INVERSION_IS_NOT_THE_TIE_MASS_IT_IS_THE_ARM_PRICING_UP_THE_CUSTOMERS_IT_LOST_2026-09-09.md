**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — attribute the inversion before it is quoted as a fact about the method) · **Class:** measurements_that_mirror

# RESULT — the estimand's 0.4210 is not a tie-handling artefact. It is the arm pricing up the customers it went on to lose.

Graded against
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_ESTIMANDS_INVERSION_IS_THE_TIE_MASS_OR_THE_ARM_2026-09-09.md`,
landed at `3985636f0` **before** the discriminating counts were read. Every prediction below was
written down first and is reported here whichever way it fell.

Subject: `docs/observability/value_cycle_ab_s1_three_arm_20260909.json`,
`method_skill.fixed_horizon`, world digest `39a192ce04c1eda8`, producing commit `62334dc76`.

---

## The answer, in one paragraph

The Lane 0 item asked whether 37 of 161 decisions tied at 0.0 could push a rank concordance below
chance through tie handling alone. **They cannot, and not as a matter of degree.** `_concordance`
excludes every pair tied on the outcome, and all 666 pairs among the zero rows are tied at 0.0 by
construction — so **the tie mass supplies 0 of the estimand's 12,194 comparable pairs**. A stratum
contributing no pairs cannot move a mean over pairs in either direction. The hypothesis is
answered by the estimator's construction, not by a close number.

What carries the departure is the **cross stratum**: the 4,588 pairs putting each departure
against each survivor, which read **0.2686**. In 73% of departure-against-survivor pairs, the arm
had given the DEPARTURE the higher margin. Kill that stratum's information and the estimand reads
**0.5081** rather than 0.4210 — **inside** the 0.4458–0.5540 a no-information signal reaches on
its 161 decisions. The whole of the estimand's distance from chance is those pairs, and none of it
is the ties.

**So the inversion is real and it is a defect in the per-customer decision rule**, not in the
instrument that found it.

## The pair-stratum split

Every comparable pair falls in exactly one stratum. The partition is an identity over two legs
the bridge already published, so it re-ranks nothing and cannot disagree with the figure it
decomposes.

| stratum | decision pairs | **comparable** pairs | concordance | contribution to (c − 0.5) |
|---|---:|---:|---:|---:|
| within-settled (leg 2's own population) | 7,626 | 7,606 | 0.5130 | **+0.0081** |
| within-zero — **THE TIE MASS** | 666 | **0** | undefined | **0.0000** |
| cross — departure against survivor | 4,588 | 4,588 | **0.2686** | **−0.0871** |
| **the estimand** | | **12,194** | **0.4210** | **−0.0790** |

The three terms sum to the departure exactly, because a concordance is a mean over pairs and this
is that mean's own decomposition.

## The predictions, graded

| | prediction | outcome |
|---|---|---|
| **P1** | `comparable_pairs` = 12194, `pairs_tied_on_outcome` = 686 | **CONFIRMED, both to the unit.** 12194 = 7606 + 37×124; 686 = 20 + C(37,2) |
| **P2** | tie mass ≥ 666, i.e. the zero rows share one outcome | **CONFIRMED.** 686 − 20 = 666 = C(37,2) exactly |
| **P3** | cross-stratum concordance in 0.25–0.29 (≈0.27) | **CONFIRMED.** 0.26864 |
| **P4** | the permutation null is itself the tie correction and is unbiased | Stated as a reading already in hand, not a prediction: `null_mean` 0.5000819, 0.00008 from 0.5, inside the Monte-Carlo error of 20,000 draws |
| **P5** | the inversion is not a tie artefact | **CONFIRMED** |
| **P6** | what would have made the item right | none of the three occurred |
| **P7** | what this does not settle | stands — see the bound below |

Nothing was refuted. That is worth less than it looks: P1–P3 are arithmetic over counts the run
already published, and the reason they were predictable is the reason the answer was available
without a re-run. **The prediction that could have failed was P5**, and it is the one the item was
commissioned on.

## Why "re-cut with the 37 rows excluded" was not the instrument

The item asked for the concordance re-cut with the zero-settled rows dropped. **That cut already
existed** — it is `settled_only_pounds_outcome`, leg 2 of the bridge, at 0.5130 on 124 decisions
against its own null of 0.4403–0.5588, p = 0.666, inside. Both cuts are reported here against
their own permutation nulls at their own n, and neither against the other's, exactly as asked:

* **zero rows excluded** — n = 124, 0.5130, null 0.4403–0.5588, p = 0.666, **inside**
* **zero rows included** — n = 161, 0.4210, null 0.4458–0.5540, p = 0.0045, **outside**

But **that step is not a tie correction and must not be read as one.** Dropping the 37 rows removes
the ties *and* the entire departure population in one move, so a change under it cannot be
attributed to either. "The inversion goes away when the ties go" would have been this project's
own recurring defect — two things changed, one cause named — arriving on the figure the whole
apparatus exists to make attributable.

The tie correction is the **permutation null itself**. It permutes the observed signals against
the FIXED outcomes, so it reproduces the outcome-tie structure exactly; each comparable pair is
equally likely to fall either way under a shuffled signal, whatever the ties do. Outcome ties
therefore do not bias the statistic — they only remove pairs and **widen** the null. Consistent
with that, the estimand's null SD (0.02763) is wider than leg 0's (0.02593) on *more* decisions.

## One variable at a time

**The censoring rule was not touched.** `horizon_open_at_the_end_of_the_settled_book: 47` and
`no_published_counterfactual_rate_for_the_term: 6` are exactly as they were. The 6 remains a named
coverage gap in our own sourced tariff series and is **not** folded in: scoring it would turn a
gap in what we sourced into an outcome the world produced. Nothing in this document rests on the
censoring, and a cut that had moved it in the same step could not have attributed anything.

## The bound on this result, stated here rather than left for a reader

* The cross stratum is 4,588 pairs determined by only **37 rows' signals**, drawn from a wider
  account set than leg 2 (88 accounts against 63). That is **leverage and clustering, not bias**.
  The permutation null assumes exchangeable decisions and these are clustered on accounts, so the
  estimand's published interval is **optimistic**. The direction is what this establishes; the
  magnitude is not.
* The estimand's declared weakness is unchanged: the outcome is in **pounds**, which carry account
  size, and a household that left has no counterfactual over the horizon to normalise by.
* One world, one seed, one book of 88 accounts. `selection_gbp` on the pounds cut still reads
  −£426.96 ± £2,291.98 on 3 seeds and still cannot resolve a sign. **The two cuts agree in
  direction and only one has the power to say so.**

## What landed

* `tools/run_value_cycle_ab.pair_strata` — the split, published by every future run at
  `method_skill.fixed_horizon.pair_strata`. An identity over two legs' published counts, with the
  two arithmetic preconditions **measured** and a refusal when either fails.
* `tools/run_value_cycle_ab.cross_stratum_null_spread` — the interval the cross stratum's own
  pairs earn, by the same permutation every other null here uses.
* `tools/generate_value_arms_data._skill_pair_strata` — the one place that file derives rather
  than reads, and it derives by calling the producer's own function, so the page and the artefact
  cannot carry two answers. It names its provenance when it does.
* `site/capabilities/index.html` — the attribution renders **immediately after** the estimand's
  own verdict sentence, not under the counts below it, because a figure and its attribution have
  to travel together or the figure gets quoted alone.
* Controls: 10 in `tests/tools/test_run_value_cycle_ab.py`, 3 door tests in
  `site/test_the_baseline_comparison_reaches_the_reader.py`. Poison round first on both. Nine
  mutations run, nine killed.

**The page's own whole-feed walker caught this work mid-flight**, and it was right: the first
draft rendered the cross stratum's 0.2686 with no interval computed on its own pairs. It is now
published bounded where the rows exist, and **withheld with its reason** where only the totals do
— with the attribution carried instead on the scale that is bounded (0.5081 against the estimand's
own 0.4458–0.5540). That refusal made the sentence stronger, not weaker.

## What is next, and it is not more measurement of this

1. **The defect is in the arm, and nobody has looked at it.** The value arm gave its departures
   the higher margin in 73% of departure-against-survivor pairs. That is `saas/`'s renewal pricing
   rule choosing highest where it destroys the relationship — the director's own case, named in
   `method_skill.reading` months ago as the thing worth being able to see, now measured. The next
   item is to find WHERE in the rule that happens: which household features the arm is pricing up,
   and whether the churn model it prices against already predicts the departure it is buying.
2. **A second seed and a second world**, to establish the direction is not one book's accident.
   This result is one run. Re-running `tools/run_value_cycle_ab.py` now also publishes
   `pair_strata` with the cross stratum's own interval, which this run could not have.
3. **The 6 uncovered terms stay a coverage gap** and are worth sourcing, but they are not
   load-bearing here: at 6 of 214 they cannot reach the cross stratum's 4,588 pairs.
4. **The clustering bound is real and unaddressed.** An account-clustered permutation would give
   the honest interval on every figure in this block. It is not built, and until it is, every p on
   this page is optimistic — this one included.
