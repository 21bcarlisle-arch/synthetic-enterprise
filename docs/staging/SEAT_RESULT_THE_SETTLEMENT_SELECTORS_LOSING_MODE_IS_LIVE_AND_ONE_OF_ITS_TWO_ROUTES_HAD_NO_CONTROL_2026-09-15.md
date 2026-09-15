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

1. **Re-grade §A of the merged pre-registration against its own numbering.** The grading names
   §B's bands. §A is graded only by coincidence of content, and that is now written into the
   prereg itself with a pointer to both result files — but the re-grade is unrun work.
2. **The unplaceable route is a live branch with a caller-only trigger.** It is unreachable through
   `plan_growth_campaign` (which passes `DOMESTIC_ONLY`, and `iter_prospects` mints a premise when
   handed no stock), and a won SME would raise `DwellingNotDrawn` further downstream anyway. It is
   now held by the new control at the function's own boundary, which is the right altitude — but
   **nobody has established whether the campaign should ever be able to reach it.** If the answer
   is no, the honest move is a refusal at the campaign's edge, not a fallback three layers in.
3. **Nothing asserts either refusal sentence reaches the reader.** `notes` carries
   `SETTLEMENT SAMPLE NOT CHOSEN: ...` and `grep` finds no control over that string anywhere. The
   new control asserts the refusal on the returned dict; the note's journey to the page is unheld.

## What this does NOT claim

* It does not re-open the chooser. P1 held at 1.553× and P6 measured −2.45%; both stand.
* It does not claim the label's three homes have caused a wrong published figure. Under the null
  the rate is 1.0 and the uniform sentence is true; the defect is that a consumer *could not tell*,
  not that one was misled.
* It does not claim the five incidental tests are wrong. They are correct about their own subjects.
  The finding is that a reachability claim rested on them without saying so.
