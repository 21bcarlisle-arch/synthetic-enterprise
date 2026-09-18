**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The arms now price one book, six controls refuse the republish, and three were already red

**Filed:** 2026-09-18 · **Claim id:**
`the-two-arms-have-never-priced-the-same-population-and-the-page-says-they-have`
**Pre-registration:** `docs/staging/PREREG_WHAT_PROMOTING_THE_SUPPORT_BOUNDED_RUN_MOVES_ON_THE_ARMS_PAGE_2026-09-18.md`
**Grades:** `b329e702b` (the fix), `e15ccbe3d` (the structural prediction), `49f49dd8e` (the doors)

---

## State in one line

The run **completed and is good**; the republish **is refused by six controls** and is NOT landed.
Three further reds in the same gate run were **already red at HEAD** and are not mine.
The drawn item's "done means" is **not met**, and this says so rather than reporting the half that
worked.

## The run: the arms price one book for the first time

The setsid-detached run `e15ccbe3d` launched at 05:24 completed at **06:43**. World
`39a192ce04c1eda8`, producing commit `b329e702b`, `generated_at` 2026-09-18T05:43:40Z. Landed here
as `docs/observability/value_cycle_ab_s1_three_arm_20260918.json` — the dated, immutable copy — so
that the next invocation does not spend another hour re-deriving it.

| | published (09-10 run, `9cf9d16e`) | this run (`b329e702b`) |
|---|---|---|
| value arm priced / declined | 215 / **65** | 104 / **3** |
| level arm priced / declined | 281 / **0** | 107 / **3** |
| `same_priced_population.answer` | field did not exist | **`true`** |
| net refusals of renewals the other arm priced | 65 | **0** |

**The two arms now price one book.** The remaining 3-renewal gap is entirely roster divergence —
a different price causing a different churn, which is the effect being measured. `b329e702b`'s
corrected prose travels with it: this is the first run to carry it.

## THE REFUSAL: nine controls red on the promoted feed

I promoted the run to `THREE_ARM_PATH`, regenerated `site/data/value_arms.json`, and put the result
through `surgical_land`. **The gate refused: 9 failed, 495 passed.** The feed and the canonical
promotion are reverted in this commit; the measurements below were taken from the generated feed
before reverting, and are the whole point of the exercise.

| control | class | established? |
|---|---|---|
| `test_the_error_bar_bounds_the_FIGURE_THE_HEADLINE_STATES` | presupposes the bar is available; it now correctly refuses, so the reconciliation's operands are `None` | **yes** — keyed to today's answer |
| `test_a_floor_drawn_over_a_DIFFERENT_book_is_refused_however_recent_it_is` | builds its fixture from the live artefact and needs a floor **the stamp rule admits**; the stamp now refuses first, so the book rule is no longer the thing measured — the control says exactly this in its own failure message | **yes** — fixture precondition inverted |
| `test_a_leg_whose_own_redraws_straddle_zero_states_no_direction_however_stable` | same family | likely, not established |
| `test_a_later_run_in_this_world_that_disagrees_about_the_split_refuses_the_composition` | same family | likely, not established |
| `test_a_spread_from_another_world_bounds_nothing_however_it_is_stamped` | same family | likely, not established |
| `test_the_census_counts_what_the_guard_reads_not_whether_the_key_is_there` | **NOT MINE — red at HEAD** | **yes** |
| `test_MUTATION_a_labelled_won_record_makes_the_gate_reachable` | **NOT MINE — red at HEAD** | **yes** |
| `test_a_founder_account_passing_the_gate_is_not_a_found_account_reaching_it` | **NOT MINE — red at HEAD** | **yes** |
| `test_replicating_the_rows_moves_the_null_and_not_the_answer` | `escaped_at` is `None` where `<= 8` was expected | not established |

**Only SIX of the nine are mine.** I first wrote this section attributing all nine to the republish
and drafted a commit message saying so. That was wrong, and the correction is here beside the claim
rather than silently applied: the three `test_the_renewal_funnel.py` legs **fail in a clean
`git archive` extract of HEAD with none of my changes in it** — `3 failed, 21 passed`. I very nearly
landed a false attribution into a permanent commit message; what caught it was checking the
one-variable version instead of trusting the failure list the gate handed me.

**And the found/founder question is SETTLED, against my own first reading.** I had this down as
*"either the bigger book makes the gate reachable or a founder account is being miscounted as a
found one, and the failure cannot tell them apart."* Neither. `simulation/run_phase2b.resolved_tariff_type`
says in its own docstring: *"ONE function, and since 2026-09-16 ONE answer — the commodity split is
gone."* The gas call site was repaired to `or "fixed"` in that commit, so **no leg's world-read
resolves to `None` any more**. All three controls need an unlabelled leg as their subject, and that
subject no longer exists anywhere in the world. The sibling red says the same thing from the other
side: *"every leg carrying the key resolves to `{'fixed'}`."*

This is the third time these controls have lost their subject to a repair — the docstring records
being moved from electricity to gas on 2026-09-07 for exactly this reason, and gas has now gone the
same way. **There is no commodity left to move them to**, so the next repair cannot be another move;
the fixture has to construct an unlabelled record rather than find one.

**That makes HEAD red for every lane whose test selection reaches `test_the_renewal_funnel.py`**,
which is a finding in its own right and is not mine to have caused. It is filed here because
nothing else noticed: the gas repair landed 2026-09-16 and these three have been red since.

**Five of my six are the class `49f49dd8e` named**: a control keyed to today's answer, red when the
page becomes more honest. The repair is to key each to its property and to build its fixture so its
own precondition survives — not to relax the assertion.

## P1 — PARTLY REFUTED, and the refuted half is a live page defect

`e15ccbe3d` predicted, from a probe that bumped only `generated_at` on the old artefact, that all
three bounded legs would go unavailable together. Against the real feed:

| | predicted | measured |
|---|---|---|
| `_staleness_caveat` fires | yes | **yes** ✓ |
| `legs_on_one_bar.available` | `False` | **`False`** ✓ |
| `_floor_admission.rule` | `stamp_proxy` | **`declared_book`** ✗ |
| `_floor_admission.admitted` | `False` | **`true`** ✗ |
| `error_bar.selection_leg` states a sign | no | **yes — `negative`, 2.50 SEMs** ✗ |

The stand-in probe was wrong about the admission because it edited one field of the old artefact
instead of reading a real one. The admission pairs on the **declared** book (`['resi','SME']` both
sides), which the arm fix does not move — `e15ccbe3d` said exactly that in prose and then predicted
against it anyway.

**The half that matters:** on the generated feed the page says both of these, in two blocks a reader
sees together:

> *"on 18 re-draws the selection leg is negative"* — `error_bar.reading`, rendered at
> `site/capabilities/index.html:2238`

> *"no contrast on this page can have its direction stated until the noise floor is re-run on the
> book published above"* — `legs_on_one_bar.why_no_leg_is_graded`, rendered at `:2249`

And two sentences in `_leg_over_its_own_family` (`tools/generate_value_arms_data.py:3779`, `:3874`)
assert `single_run.gbp` **"is one member of the 18"** when the family is pre-fix (09-17) and the run
is post-fix (09-18) — while the same block states `single_run_inside_the_family: false` and
`single_run_on_the_other_side_of_zero: true`.

`b329e702b` predicted *"the guard refuses before that sentence can be published."* **That prediction
is refuted**: the guard refuses in its own block and the sentence composes from another.
`49f49dd8e` anticipated the class — *"none of them could have noticed the far worse state where a
pre-fix seed family silently bounds a post-fix point estimate"* — and this is that state.

The remedy threads the staleness answer into `_leg_over_its_own_family`. All three call sites
(`:1691`, `:2318`, `:10620`) pass positionally, so it must be a **required** parameter: a defaulted
one is the unreachable-mutation shape this project has already paid for.

## P2 — the residual reverses, and it is NOT attributed

| | published (09-10, `9cf9d16e`) | this run (`b329e702b`) |
|---|---|---|
| `level_gbp_per_mwh` | 20.00 | 41.00 |
| `selection_gbp` | **−332.64** | **+4,327.01** |
| `level_share_of_advantage` | 1.020 | 0.055 |

The published sentence — the level explains *all* the advantage, the selection is worth less than
nothing — becomes its opposite. **I cannot attribute it.** Four commits touching the value arm
landed between the runs (`e1895d6c8`, `27c7672f7`, `3088f8c71`, `b329e702b`); the level is *derived*
from the value arm's own realised median and moved 20.00 → 41.00 on its own; the book is a different
size (2,037 → 2,824 offered, 100 → 66 accounts priced). Several things changed at once. The
one-variable run — `b329e702b` with only the support clamp reverted — is a ~20-minute leg and is not
done. I checked the publisher for an attributed cause, as the prereg said I would: it emits none.

## P3 — HELD, after one repair, and the repair IS landed

`site/test_the_baseline_comparison_reaches_the_reader.py::test_a_reading_that_CLEARS_its_null_does_not_say_it`
is a **fifth** instance of the class `49f49dd8e` repaired four of, and it could only appear once a
real run existed — that commit staged a *predicted* feed.

The leg drove ONE reading (`method_skill`) and then read the WHOLE `arms-method` panel for "we
cannot tell". It was green only while `method_skill` was the panel's sole source of the phrase. The
new run's smaller book makes the estimand's cut — a **different population**, 0.440 on 85
decisions — sit inside its own null and say so honestly, and the door reddened on a page that had
become *more* truthful.

Repaired by the partition its sibling has carried since 2026-09-09: scope the absence to the
survivor cut's own region, with the split asserted load-bearing rather than assumed.
**Mutation-proven against the real renderer** — gating the caveat on `msk.inside_the_null` reds it,
citing 0.940 inside the scoped region — and the mutation had to be **staged** to fire, because the
door reads the published copy. It is green on HEAD's feed *and* on the new one, so it is a genuine
scoping repair and not an accommodation of one run.

## P4 — HELD

`_later_runs_in_this_world` fires and names `value_cycle_ab_s1_three_arm_20260918.json`, with
`CURRENT_WORLD_THREE_ARM_PATH` left pinned to `_20260908.json`.

## Owed, in the order it should be taken

1. **Repair the three `test_the_renewal_funnel.py` legs that are red at HEAD** — ahead of anything
   here, because they red every lane that selects that file and they are not waiting on this work.
   The fixture must CONSTRUCT an unlabelled record; there is no commodity left to move it to.
2. **Repair my five keyed-to-today's-answer controls** as a class, fixtures included.
3. **Thread staleness into `_leg_over_its_own_family`** as a required parameter, with its own
   control.
4. **Then promote** the 09-18 run and republish.
5. **The folded-eighteen floor on the post-fix tree** — 54 passes, ~18 hours — which is what
   restores a sign to either leg.
6. **The one-variable run** that would attribute P2's reversal.
