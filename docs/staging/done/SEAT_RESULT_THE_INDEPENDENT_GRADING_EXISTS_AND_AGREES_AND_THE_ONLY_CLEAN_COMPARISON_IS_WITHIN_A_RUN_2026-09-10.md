**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the independent grading exists and agrees, and the only clean comparison is within a run

RECORDED: nothing is refused by this. The A/B pass ran and an artefact carries
`belief_against_control_outcomes.available: true`. The pre-registration filed before the run is
graded below, including the leg it refuted.

**The page does NOT publish the figure yet, and that is a decision rather than an omission.**
Promoting this run to the canonical path costs the page every directional bound, for a reason
measured and written down one day ago. The run stays on disk as a dated artefact and the promotion
waits for a noise floor drawn over the same book — see *The trade that was refused again* below. The
render half of the item is landed and proved, so when the pair moves, the figure appears with no
further code change.

**Filed:** 2026-09-10, delivery seat. Closes
`run-the-ab-pass-and-let-the-independent-grading-reach-the-page`. Prediction:
`docs/design/PREREGISTRATION_THE_BELIEF_GRADED_AGAINST_AN_OUTCOME_ITS_OWN_PRICE_DID_NOT_CAUSE_2026-09-10.md`.

---

## The run

```
python3 -m tools.run_value_cycle_ab --level-arm \
  --out docs/observability/value_cycle_ab_s1_three_arm_20260910.json
```

Full window, three arms, ~33 minutes. Clock audit **PASS** (11 figures, 3 arms). It stays at that
dated path; it is **not** copied to the canonical `value_cycle_ab_s1_three_arm.json`, for the reason
below.

## The trade that was refused again

Copying the run to the canonical path and regenerating the feed was done, and four controls in
`tests/tools/test_generate_value_arms_data.py` went red and refused the commit. They were right, and
all four have one cause: **the published noise floor is now older than the point estimate it
bounds** — floor `2026-09-09T15:17:31Z` against point `2026-09-10T14:04:08Z`. `_staleness_caveat`
fires, `_seed_spreads` refuses a floor it cannot pair, and `contrast_bounds` — which every
directional claim on the page is gated on — empties out.

This is not a new discovery. It is the same trade this seat measured and refused yesterday, in
`SEAT_RESULT_ALL_SIX_LEG_CONDITIONING_PREDICTIONS_HOLD_AND_PUBLISHING_THE_RUN_ALONE_WOULD_COST_THE_PAGE_EVERY_DIRECTIONAL_BOUND_2026-09-09.md`,
whose Q5 predicted 0 bounds lost and measured **10 lost, 3 gained**:

> *"That trade is refused. The run stays on disk; the promotion waits for the nine-seed floor now in
> flight, and then it is a pair move that costs nothing."*

Nothing about the present run changes that arithmetic, so the same answer stands. **Publishing an
independent concordance at the cost of every directional bound on the page would be a bad trade made
twice.** The correct move is the pair move: a floor over this book, then run and floor to the
canonical paths together.

**What the landed render work bought.** Because the door was fixed and proved on both branches
first, the pair move is now a pure data move — copy two artefacts, regenerate, and the grading
appears. Had the render defect stayed, the pair move would have landed the artefact and still shown
the reader nothing.

## The figure

| | value-arm outcome | **control-arm outcome** |
|---|---|---|
| `discrimination_auc` | 0.6148 | **0.6237** |
| population | 85 stayed / 39 left | 87 stayed / 33 left |
| scored decisions | 124 | 120 |
| share of priced renewals | — | 55.8% |
| priced terms with no control-world outcome | — | 95 |

The belief ranks who leaves **very slightly better** when the arm's own price rise is taken out of
the outcome than when it is left in. That is the opposite of the direction a manufactured-outcome
story predicts, and it is far too small to be evidence of anything on its own.

## The pre-registration, graded

**P0 — world digest — HOLDS.** Both runs are `39a192ce04c1eda8`. Had it moved, nothing below would
have been graded.

**P2 — direction — HOLDS.** 0.6237 > 0.5.

**P3 — the join — HOLDS, and it is the thinnest margin on the page.** `scored_share_of_priced` is
0.558 against a predicted floor of 0.5. It clears, so the AUC is worth quoting. But **95 of the 215
priced terms reached no lifecycle event in the control world at all** — they are excluded rather
than counted as retentions, which is the right treatment, and the residue is large enough that it
is the first thing to look at next.

**P1 — the bound — HOLDS, but the comparison I wrote down was the wrong one.** I pre-registered
|AUC − 0.6270| ≤ 0.10 against the 2026-09-09 run. Measured that way: |0.6237 − 0.6270| = **0.0033**.
But that comparison is confounded, for the reason P4 exposed. The comparison that is actually
one-variable is **within this run**: 0.6237 against 0.6148, both from the same pass, the same tree,
the same book, the same 215 priced decisions, differing only in which arm's outcome the belief is
scored against. Δ = **+0.0089**. The prediction holds on both readings; only the second is
attributable, and it is the one that belongs on the page.

**P4 — "these will not move" — REFUTED.**

I predicted `belief_vs_outcome.discrimination_auc` would stay at 0.6270 on the grounds that the new
field does not touch it. It came back **0.6148**, and the population moved 83/40 → 85/39.

The half of P4 about the disagreement set **held exactly**: `only_in_value_arm` is still
`C5_2, PROS-2019-0024, PROS-2021-0324, SYN-2016-034` and `only_in_control_arm` is still
`PROS-2018-0137`.

**Why it moved, and what I can and cannot attribute.** The tree moved between the two runs
(`8b846013e` → `9cf9d16ed`, a day of other lanes' landings) and the arm's own behaviour moved with
it: `decision_shape.priced` 214 → 215 and `distinct_margins` **63 → 74**. So the two runs did not
price the same book in the same way. Whether there is *also* run-to-run stochasticity in the churn
roll is **not established by this run** — two things differ, so I cannot separate them, and I am not
going to pick the flattering one. What is established is the consequence:

> **Cross-run AUC comparisons on this page are confounded. The within-run pair is the only clean
> one.**

The block was built to run both arms in one pass because it cost no extra pass. That turns out to
have been the load-bearing property, for a reason the commit that added it did not state.

**What I got wrong in the reasoning, not just the number.** "The new field does not touch
`belief_vs_outcome`" is true and was never the question. *Conceptually separate* is not *invariant*:
a figure recomputed by a fresh pass over a moved tree can move for reasons that have nothing to do
with the change under test. A pre-registered "will not move" has to be argued from what holds the
value fixed, and nothing here did.

## What else this turned up

Two controls were red against the new artefact. Neither was caused by it; both were **exposed** by
it, and both are the same shape as the defect this item existed to fix.

**1. The control proving the un-pinning was itself pinned.**
`test_BOTH_availability_branches_can_be_taken` landed in `1d9e0a85c` to assert both branches of
`_independent_grading_today` are reachable. It read the *refusal* side straight off the live
artefact, on a premise it stated as fact — *"every artefact on disk today takes the refusal
branch"*. This work spent that premise the same day, the unmutated side went to the AVAILABLE
branch, and the control went red **because the code had become more honest**. Fixed by constructing
both sides: the field is removed for one and supplied for the other, so the pair stays a real
partition whichever branch the live run is on.

**2. A control's money formatter could not match its own subject on a negative.**
`site/test_the_baseline_comparison_reaches_the_reader._gbp` rendered −333 as `£-333`. The door
renders `−£333` — sign in front of the £, and U+2212 rather than an ASCII hyphen, both deliberate
and both documented in the render's own comment. Every `_gbp(x) in rendered` assertion was therefore
**incapable of matching on any negative figure**. It never fired because `selection_gbp` had been
positive on every run that reached this page; this is the first published run with a negative
selection leg (−£333, level share 102%). The sign flip did not break it — it made it observable.

Fixed to mirror the door, and pinned with
`test_this_files_own_money_formatter_agrees_with_the_door_on_a_NEGATIVE`, which asserts the rule at
values this file chooses rather than at whatever sign the world produced this week. Without that,
the repair goes unobservable again the first time a run comes back positive.

## Controls

| control | mutation | result |
|---|---|---|
| `test_a_run_that_HAS_the_independent_grading_puts_the_figure_on_the_page` | pre-fix render (available branch emits `""`) | RED |
| `test_a_run_WITHOUT_it_still_says_why_and_does_not_show_a_figure` | grading paragraph rendered unconditionally | RED |
| `test_this_files_own_money_formatter_agrees_with_the_door_on_a_NEGATIVE` | restore `"£{:,}".format(round(v))` | RED |

The formatter mutation also reds `test_the_page_says_WHICH_FIGURE_the_error_bar_is_a_bar_on`, which
is the data-dependent leg it was written to outlive.

## What is next

**1. The pair move, and it is the only thing between the reader and this figure.** Run
`python3 -m tools.run_value_cycle_ab --noise-floor-seeds <seeds> --redraw-mode all` over the book
`value_cycle_ab_s1_three_arm_20260910.json` was drawn on, then copy the run **and** the floor to the
canonical paths together and re-run `generate_value_arms_data`. Nine seeds is 27 full passes (~5
hours on this machine); the previous floor used nine. Everything else is landed and proved, so this
step is data and not code.

**The floor should stamp a book identity while it is being re-run.** The 2026-09-09 finding named
that as owed work and declined it because the floor then in flight would have had to be redone to
carry it. There is no floor in flight now, so the objection has expired: doing it with this re-run
closes both directions of the stamp-proxy defect for one cost instead of two.

**2. The 95 absent terms**, which is the largest unexamined quantity in this block. 44% of the
renewals the value arm priced reached no lifecycle event in the control world, and the block counts
them without characterising them. If they are concentrated in the tail — households the value arm's
own price drove out early, which is precisely the residue
`population_terms_absent_from_the_control_world` exists to name — then the population's remaining
dependence on value-arm survival is larger than a reader would guess from a 55.8% match rate. That
is a distribution to look at, not a number to assert, and it is one query over `scored_decisions`
and the control arm's `customer_events`.

**Do not compare these AUCs across runs** until something holds the book fixed between passes. The
within-run pair is what the page will publish when the pair moves, and it is the only one that means
anything today.
