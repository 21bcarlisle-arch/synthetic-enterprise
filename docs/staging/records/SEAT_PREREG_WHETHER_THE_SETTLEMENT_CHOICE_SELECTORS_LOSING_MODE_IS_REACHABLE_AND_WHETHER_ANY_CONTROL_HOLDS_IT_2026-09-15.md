**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# PRE-REGISTRATION — is `settle_within_budget`'s `uniform_count` mode reachable, and does any control hold it

**Filed 2026-09-15, delivery seat, BEFORE the mutation is run.** Lane 0 delivery, claim
`settlement-choice-selector-losing-mode-is-reachable-or-it-is-a-deletion`.

Everything in §1 is a READING of the tree at `5e21a5da8` and carries no prediction. Every number
and verdict in §3 is a prediction whose answer I do not have.

---

## 0. The premise, re-measured at draw time

The drawn item cites `760637dd7`. `git merge-base --is-ancestor 760637dd7 origin/main` → yes, and
`git rev-list --count HEAD..origin/main` → 0. The fork is closed and nothing blocks this. **The
premise is live, not spent.**

The item also asks whether the grading against
`SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md` was
ever filed. **It was**, and that part of the item is answered by reading rather than measuring —
see §2. What is NOT answered anywhere is the reachability question, which is what this
pre-registration is for.

## 1. What the tree says, read and not predicted

`simulation/net_new_acquisition.settle_within_budget` (lines 652–795) holds two selection rules
behind one selector:

```python
chosen = None
selection = "uniform_count"
choice_refusal = None
if sample_rate < 1.0:
    ...
    if unplaceable:   choice_refusal = "...no home the demand axes can be evaluated on..."
    else:
        chosen = choose_settled_sample(...)
        if chosen is None: choice_refusal = "...not even the smallest chosen set fits..."
if chosen is not None:
    selection = "chosen_weighted"
```

**`uniform_count` is the initialised value**, so it is the default in three distinct states:
the null case (`sample_rate >= 1.0`, where NO selection happens at all), the unplaceable refusal,
and the headroom refusal. The first of those carries `choice_refusal is None` and is
distinguishable only by a consumer that already knows to look.

The function's own docstring says:

> The controls are `tests/simulation/test_the_settled_book_is_chosen_and_weighted_not_culled_by_count.py`
> — `test_both_selections_can_actually_happen_in_the_campaign` is the one that proves the fallback
> branch is reachable, which is the leg a guard that refuses everything would otherwise pass.

That named test (line 294) does not call `settle_within_budget` or `plan_growth_campaign`. It
asserts `callable(plan_growth_campaign)` and then calls `choose_settled_sample` twice — once
clean, once with `vectors[3] = None` — asserting one returns non-None and the other None. The
second half is the same assertion as `test_an_unplaceable_candidate_refuses_the_whole_sample...`
(line 263) with a different index.

`grep -rn settle_within_budget` over every `.py` in the tree returns exactly three sites: the
definition, the single call in `plan_growth_campaign` (line 1109), and a monkeypatch spy in
`tools/settlement_choice_probe.py`. **No test anywhere calls it.**

The shipped campaign passes `segment_weights or DOMESTIC_ONLY` (line 966), so every prospect is
`resi`, and `iter_prospects` mints a premise when handed no stock.

## 2. The grading question, answered by reading

The item asks whether the two pre-registrations were ever graded. They were, in the same
directory:

* `SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md` — grades ten predictions,
  6 hold / 4 fail. Its header names the prereg file **and the bands it grades are §B's**
  (P1 "≥1.25×, kill below 1.10×", P2 "distinct vectors ≥70"), not §A's (P1 "[1.2×, 2.0×]").
* `SEAT_RESULT_P6_THE_CHOSEN_BOOK_IS_2_45_PERCENT_WORSE_ON_GROSS_MARGIN_2026-09-11.md` — takes
  the one withheld prediction. |Δ| = 2.45%, sign against the change.

So **§B is graded by name; §A is graded only in substance** — §A's P1 band contains the measured
1.553×, §A's P4 is §B's P7, §A's P5 is §B's P4 — and by coincidence of content, not by any
reader-visible pointer. Meanwhile the merged prereg's own header still says *"neither document's
predictions have been graded here"*. True of the merge commit; false as the sentence a reader
meets, because the grading sits two files away with no pointer in either direction. **That is a
record defect, and it is the cheap half of this item.**

## 3. The predictions

**P1 — NO CONTROL HOLDS THE LOSING MODE.** Replacing both fallback-producing paths in
`settle_within_budget` with `raise AssertionError` fires **zero** tests across
`tests/simulation/test_the_settled_book_is_chosen_and_weighted_not_culled_by_count.py`,
`tests/simulation/test_net_new_acquisition.py`, `tests/simulation/test_opening_book_subset.py`
and `tests/tools/test_couple_pb3_book_growth.py`. If **any** test fires, the docstring's claim is
right, P1 is refuted, and I withdraw the finding rather than rewording it.

**P2 — the named control survives the mutation that kills `chosen_weighted`'s only alternative.**
`test_both_selections_can_actually_happen_in_the_campaign` passes under P1's mutation. I am
predicting this because §1 reads that way, and I am filing it as a prediction anyway because a
reading of a control is not a run of it.

**P3 — the losing mode IS reachable from real inputs, by the HEADROOM route and not the
unplaceable one.** A campaign given `customer_years_already_committed >= customer_year_budget`
has `headroom_cy == 0.0`, so `sample_rate == 0.0 < 1.0`, so the chooser is called with zero
headroom and (per the control at line 278) returns `None`. I predict such a campaign returns
`selection == "uniform_count"` with `choice_refusal` naming the headroom, and books **zero**
accounts. **This is the prediction that decides the item**: if it holds, the selector's losing
mode is live code with no control, which is a missing test. If it fails — if the campaign raises,
or reports `chosen_weighted`, or books accounts — then the mode is unreachable and the honest
remedy is `surgical_land --drops`, not a new control.

**P4 — the UNPLACEABLE route is unreachable through the shipped campaign.** Under
`DOMESTIC_ONLY` every drawn prospect carries a premise with a household, so I predict **0 of the
candidates** in a small real campaign (seed 42) yield `demand_vector(...) is None`. It stays
reachable through the `segment_weights` parameter, which is a caller's choice and not the
campaign's default — so the branch is defensive rather than dead, and that distinction is the
finding, not the deletion.

**P5 — the fix is a control, not a deletion, and I am saying so before I know P3's answer.** If
P3 holds I will write ONE control over the whole partition that drives the real
`settle_within_budget` and asserts both `uniform_count` and `chosen_weighted` occur, plus the
refusal string, and correct the docstring's false attribution. If P3 fails I will delete
`uniform_count` and every mention of it. Naming both branches here is what stops the remedy being
fitted to the answer.

## 4. What this does NOT claim

* It does not claim the chooser is wrong. P1 held at 1.553× and P6 measured −2.45%; both stand
  and neither is re-opened here.
* It does not touch the chooser's axes, weights or bands. The subject is the SELECTOR and its
  controls.
* It does not claim the record defect in §2 caused anything. Nothing downstream reads the prereg.
