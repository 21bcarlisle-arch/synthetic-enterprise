**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# RESULT — the selector's losing mode is LIVE, one of its two routes had no control, and the producer's own proof of reachability never entered the function

**Filed 2026-09-15, delivery seat.** Graded against
`docs/staging/records/SEAT_PREREG_WHETHER_THE_SETTLEMENT_CHOICE_SELECTORS_LOSING_MODE_IS_REACHABLE_AND_WHETHER_ANY_CONTROL_HOLDS_IT_2026-09-15.md`,
landed as `e4c670be1` and promoted to `origin/main` **before** any of the mutations below were run.
Lane 0 delivery, claim `settlement-choice-selector-losing-mode-is-reachable-or-it-is-a-deletion`.

---

## The headline

The drawn item's hypothesis — *"a selector whose losing mode nothing can reach is a deletion
wearing a selector's clothes"* — is **refuted for the selector and correct for its attribution.**

`uniform_count` is not dead code. It is what `settle_within_budget` actually returns whenever the
chooser refuses, and five existing tests reach it. What was wrong is narrower and worse: the
function's own docstring named a control that **never called the function**, so the branch the
module claimed was held had nothing holding it, and `selection == "uniform_count"` was asserted
nowhere in the tree.

```
the mutation, run at HEAD in a clean extract, one leg at a time
  replace the HEADROOM fallback with a raise      →  5 tests fire, 106 passed
  replace the UNPLACEABLE fallback with a raise   →  0 tests fire, 111 passed
```

The five that fire are all in `tests/simulation/test_net_new_acquisition.py`
(`test_a_settlement_bound_year_SAYS_SO_instead_of_publishing_a_smaller_book`,
`test_a_win_refused_by_the_engineering_cap_is_STILL_BILLED`,
`test_the_refused_wins_are_COUNTED_and_not_just_the_first_one_named`,
`test_a_budget_the_OPENING_BOOK_has_already_spent_books_nothing_and_says_so`,
`test_the_company_plans_on_its_FUNNELS_wins_not_on_what_the_machine_would_settle`). Every one of
them is written about the **note** or the **refused-win counts**. None asserts which selection ran.
So the branch was reachable by accident of fixture and unasserted by design.

## The grading

| | prediction | measured | |
|---|---|---|---|
| **P1** | the mutation fires **zero** tests | 5 on the headroom leg, 0 on the unplaceable leg | **FAILS, and the split is the finding** |
| **P2** | the named control survives the mutation | survives both legs | **HOLDS** |
| **P3** | zero headroom reaches `uniform_count` from real inputs, refusal named, **0** booked | `uniform_count`, *"not even the smallest chosen set fits the customer-year headroom"*, 0 booked of 20 wins | **HOLDS** |
| **P4** | the unplaceable route is unreachable through the shipped campaign | 0 of 80 real candidates unplaceable | **HOLDS** |
| **P5** | the remedy is a control, not a deletion | a control, and the deletion is refused | **HOLDS as pre-committed** |

**P1 failed and it failed in the direction that matters.** I predicted the whole losing mode was
unheld. One of its two routes is held five times over and the other is held zero times, and a
single number over both would have hidden that. *Recording plainly that I wrote the prediction as
one band over two routes, which is the same "before measuring a thing, say what it is" error
CLAUDE.md names — the routes are different mechanisms with different reachability and I banded
them as one.*

**P3 is the prediction that decided the item**, and it holds exactly as written: a campaign whose
opening book has already committed the whole customer-year budget gets `headroom_cy == 0.0`,
`sample_rate == 0.0`, a chooser that refuses, and a settled book of nothing — with
`SETTLEMENT SAMPLE NOT CHOSEN: not even the smallest chosen set fits the customer-year headroom`
in `notes`. **So `--drops` was the wrong remedy and P5's pre-committed fork sent the turn the right
way.** It also holds at the other end of the range: at 2% of the campaign's cost the chooser still
refuses and the cull still settles a book, so this is not only the degenerate arm.

## The two defects, named separately

**1. THE PRODUCER'S STATED PROOF OF REACHABILITY WAS A TAUTOLOGY PLUS A DUPLICATE.**
`settle_within_budget`'s docstring said `test_both_selections_can_actually_happen_in_the_campaign`
*"is the one that proves the fallback branch is reachable, which is the leg a guard that refuses
everything would otherwise pass."* That test asserted `callable(plan_growth_campaign)` — always
true — and then called `choose_settled_sample` twice, the second call being
`test_an_unplaceable_candidate_refuses_the_whole_sample...` again with index 3 instead of 17. It
never entered `settle_within_budget`. `grep -rn settle_within_budget` over every `.py` in the tree
returns three sites: the definition, one call in `plan_growth_campaign`, and a monkeypatch spy in
`tools/settlement_choice_probe.py`. **No test called it at all.**

This is the R15 shape where a control written *to satisfy CLAUDE.md's own rare-branch rule* did
not reach the branch it was written for — and it is worse than a missing control, because the
docstring told the next reader the leg was covered.

**2. THE LABEL HAS THREE HOMES AND ONLY ONE OF THEM IS A SELECTION.** `selection` is initialised to
`"uniform_count"`, so it is what the function reports for the null case (`sample_rate >= 1.0`, no
selection performed at all), the unplaceable refusal, and the headroom refusal. Measured on one
candidate list of 108 real dwellings with only the budget moving:

```
budget         rate      selection         settled   refusal
x2.00        1.0000   uniform_count           108    (none)
x0.50        0.5000   chosen_weighted          54    (none)
x0.25        0.2500   chosen_weighted          26    (none)
x0.02        0.0200   uniform_count             2    headroom
x0.00        0.0000   uniform_count             0    headroom
x0.50 + one home removed   uniform_count      54    1 of 108 carry no home
```

`choice_refusal` separates the null case from the two refusals, and nothing asserted that either.
`tools/generate_book_growth_data.py:230` branches on `selection == "chosen_weighted"` and defaults
to `"uniform_count"` at line 357, so a reader of the page cannot tell a chooser that refused from a
chooser that was never consulted. Not harmful today — under the null the rate is 1.0 and the
uniform prose is true — but it is one label over three populations, which is this project's most
expensive recurring shape.

## What was landed

**One control over the whole partition, driving the real function.**
`test_all_three_selection_STATES_are_reachable_through_settle_within_budget_and_tellable_apart`
replaces the tautological one. Four arms, one candidate list of 108 real dwellings, only the
budget moving (and in the last arm only one candidate's home). Mutation-proven on six legs:

```
GREEN  baseline
RED    the unplaceable fallback raises        (the leg that fired NOTHING before)
RED    the headroom fallback raises
RED    the chosen_weighted label collapses
RED    the null case carries a refusal        (the three states stop being tellable apart)
RED    the chooser never engages
RED    the cull's weight becomes per-account  (the scalar `1 / rate` claim)
```

**And one leg of my own first draft could not fail.** The distinguishability leg was a set of three
`(selection, refusal-is-None, rate<1)` tuples, with a comment saying `choice_refusal` was what
separated the null case. Mutating `choice_refusal`'s initial value to a non-None string left the
set at three distinct tuples and the leg **green** — because `sample_rate < 1.0` separates the null
case by itself. The comment named the wrong separator and the assertion could not fire on it. The
refusal's absence is now asserted directly; the tuple set is kept behind it for the
two-states-one-label case. *Both the wrong draft and the mutation that caught it are recorded in
the control itself, beside the claim.*

**The docstring is corrected in place, not quietly replaced.** The false sentence is quoted, what
it claimed is stated, and the two mutation counts are given — so the next reader meets the
correction rather than a clean paragraph that was never wrong.

## What is next, in order

1. ~~**Re-grade §A of the merged pre-registration against its own numbering.**~~ **TAKEN
   2026-09-15** — `SEAT_RESULT_SECTION_A_OF_THE_MERGED_PREREGISTRATION_REGRADED_AGAINST_ITS_OWN_
   NUMBERING_2026-09-15.md`, graded from the two 09-11 result files with no new arm: **4 hold, 0
   fail, 1 ungradeable.** The residue is narrower than this item: **§A's P1b** — *"the gain is
   concentrated on the fabric axes rather than on cost"* — cannot be graded from the filed
   evidence, which reports worst-axis KS and not per-axis KS. That needs a per-axis run of both
   arms and is the one prediction in the prereg still open. The re-grade's own finding is that
   §A's better score is §A being **less falsifiable**, not more right.

2. ~~**The unplaceable route is a live branch with a caller-only trigger.**~~ **ESTABLISHED AND
   TAKEN 2026-09-15: the answer is no, and the campaign now refuses at its own edge.** The
   question this item asked — *should the campaign ever be able to reach it* — was settled by
   measuring rather than arguing, and **this item's own premise was half wrong**: it said the
   route is "unreachable through `plan_growth_campaign`", which is true of the DEFAULT and false
   of the function. `segment_weights` is a defaulted parameter, and measured at seed 42 on 20
   prospects, `{"SME": 1.0}` produced **20 of 20** unplaceable candidates against the shipped
   weights' **0 of 20**. So the campaign could be handed a mix that manufactured the state and
   then published *"N of M wins carry no home the demand axes can be evaluated on"* — a sentence
   naming the sampling instrument for a defect in the segment mix.

   `plan_growth_campaign` now raises on any `segment_weights` carrying non-domestic mass, for
   `DOMESTIC_ONLY`'s own already-sourced reasons (the plan is denominated in Ofgem's £130 MCR per
   *domestic* customer; `_draw_dwelling` draws a dwelling only for domestic prospects, so the run
   would die downstream on `DwellingNotDrawn` regardless — this decides *where* and *with what
   message*). Held by
   `test_a_campaign_asked_to_quote_a_NON_DOMESTIC_segment_is_refused_at_its_own_edge`,
   mutation-proven on five legs, **including a leg asserting the refused state is real** (20 of 20)
   and a non-vacuity leg asserting the shipped configuration still settles a book.

   **The fallback in `settle_within_budget` is NOT deleted**, and the partition control at the
   function boundary stands. There are two subjects at two altitudes: a candidate with no home is
   a real state at that function's edge, and what was wrong was only that the CAMPAIGN could
   manufacture it and have it reported as a sampling refusal.
3. ~~**Nothing asserts either refusal sentence reaches the reader.**~~ **TAKEN in the same turn,
   landed as `f4a688367`** — `test_a_sample_the_chooser_REFUSED_says_so_in_the_notes_and_a_chosen_
   one_does_not` in `tests/simulation/test_net_new_acquisition.py`. Two arms straddling the point
   where the chooser starts fitting inside the headroom (measured: 90.0 refuses, 120.0 chooses,
   only the budget differs), mutation-proven red on four legs.

   **AND THE FIRST REASON-MUTATION LEFT IT GREEN, which is how the remaining gap was found rather
   than assumed.** I aimed that leg at the string the *unplaceable* route writes, and this
   fixture cannot reach it: `plan_growth_campaign` passes `DOMESTIC_ONLY`, so no budget makes the
   shipped campaign take that route. So **the unplaceable reason's journey to `notes` still has no
   control at any layer** — the reason itself is held at the function boundary by the partition
   control, and the note it would produce is not. That is the residue, and it is what is left of
   this item rather than the whole of it.

## What this does NOT claim

* It does not re-open the chooser. P1 held at 1.553× and P6 measured −2.45%; both stand.
* It does not claim the label's three homes have caused a wrong published figure. Under the null
  the rate is 1.0 and the uniform sentence is true; the defect is that a consumer *could not tell*,
  not that one was misled.
* It does not claim the five incidental tests are wrong. They are correct about their own subjects.
  The finding is that a reachability claim rested on them without saying so.
