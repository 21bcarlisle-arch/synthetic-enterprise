**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The drawn repair was already landed, and the floor that unblocks the page met its pre-registered rule

**Filed:** 2026-09-19 · **Claim id:** `value-arms-error-bar`
**Closes:** `docs/staging/SEAT_FINDING_THE_PAGE_PAIRED_ITS_ERROR_BAR_ON_A_CURRICULUM_SETTING_AND_CALLED_IT_THE_BOOK_2026-09-18.md` (BLOCKING)

---

## The drawn work was spent before the item was drawn

The item asked for a repair to `_floor_admission` in `tools/generate_value_arms_data.py`: pair on a
realised field that can discriminate, keep the producer's honest-re-run concern answered, prove it
with a whole-partition control, and stop `tests/tools/test_generate_value_arms_data.py` asserting
the defect as correct.

All of it landed in `4edfee275`, which is an ancestor of `origin/main`. Measured at HEAD rather
than inferred from the commit message:

| the item's own "finished when" | measured |
|---|---|
| the repaired admission refuses the real 09-18 pair on the **live feed** | `admitted: False`, refusal names `billing_accounts_settled_in_window is 164 across the floor's seeds against 154-155 across this run's arms` |
| the test file no longer asserts the constant is the right half | `test_the_pairing_is_on_the_DECLARED_half_and_never_on_the_realised_counts` is **gone**; `test_the_realised_counts_ADMIT_an_honest_re_run_and_REFUSE_a_different_book` replaces it |
| the control asserts over the whole partition, not one leg | both legs plus a third: honest re-run ADMITTED, a book nine accounts away REFUSED, and a declared mismatch still refused when the realised counts agree perfectly |

The refusal also reaches the reader: `site/data/value_arms.json` carries it. Built **and** wired.

The item's failure condition — "an admission that now refuses every pair, including an honest
same-book re-run" — does not hold. Leg one of the partition control is exactly that pair, on the
arms' real magnitudes rather than invented ones, and it is admitted.

## What that left owed, and it was not a code repair

The finding this item serves says it closes when the re-run floor "lands and is admitted on the
book rather than waved through on a curriculum setting". That run has landed
(`ffe71e0c5`, `value_cycle_ab_s1_noise_floor_next12_at_18327d977.json`, twelve seeds,
2026-09-19T09:10:27Z) and **nothing was reading it**: `NOISE_FLOOR_PATH` still named the folded
eighteen, so the page was still bounded by the 164-account book its own guard refuses.

The decision rule was fixed before the seeds were readable, in
`docs/staging/records/PREREG_THE_TWELVE_AT_HEAD_OVER_THE_09_18_BOOK_AND_WHAT_WOULD_MAKE_ME_NOT_PUBLISH_THEM_2026-09-18.md`:
move the constant only if predictions 1 AND 2 hold, and the width and the sign gate it in neither
direction. Measured on the landed artefact:

```
1  _staleness_caveat(floor, arms) -> None                                    HOLDS   (gating)
2  all five realised fields overlap the arms:                                HOLDS   (gating)
     settled 154 vs 154-155 · electricity 136 vs 136-137 · gas 90 · dual 72
     · at-end-of-window 54-55 vs 52-55
3  sd GBP5,413.58, pre-registered band GBP3,500-7,500                        holds   (reading)
4  0.17 sems from zero, selection_distinguishable_from_zero: false           holds   (reading)
```

Prediction 3 is the one the pre-registration said it would bet against itself on, and it held: the
3.31x dispersion gap tracks the BOOK, not the instrument. Recorded because it was filed before the
answer, not because it is flattering.

## Why the constant's own block did not block the move

`NOISE_FLOOR_PATH`'s provenance block held the constant on 2026-09-18 with a good reason: swapping
to a wider family that states no sign would be choosing between two instruments **by their
answers**. That was true while the page published a NEGATIVE.

It no longer does. `_floor_admission`'s realised leg — the repair this item was drawn for — refuses
the folded eighteen on the book, so `contrast_bounds.available` was **false** and the page stated
no direction at all. The move therefore withdraws no sign, because there was no sign left to
withdraw. What it restores is the two legs the blanket refusal was withholding alongside the
selection one:

| | before (folded eighteen, 164 book) | after (twelve, 154 book) |
|---|---|---|
| `contrast_bounds.available` | **false** | **true** |
| `staleness_caveat` | FIRES | `None` |
| `floor_admission.admitted` | `False` | `True` |
| value advantage | no direction stateable | GBP7,395.85, sem 996.79 — 7.4 sems |
| level advantage | no direction stateable | GBP7,655.14, sem 1,619.55 — 4.7 sems |
| selection leg | no direction stateable | GBP-259.29, 0.17 sems — **still no sign** |

The page's own published remedy was this exact move, in these words: *"no contrast on this page can
have its direction stated until the noise floor is re-run on the book published above"*.

## What this does NOT settle, and the page still says so

- **The width question is open.** The one-variable run the constant's block waited on — these
  twelve seeds at `4e7938f673` — is not on disk and nothing is in flight. It died with the bounded
  tick that launched it and its recorded command cannot parse at the instrument it names
  (`WORKER_RESULT_THE_ONE_VARIABLE_WIDTH_RUN_DIED_WITH_THE_TICK_THAT_LAUNCHED_IT_...2026-09-18.md`).
  The constant does not claim the move settles which dispersion is right. It changes which question
  the page may answer meanwhile: a bound over the wrong book answers nothing at any width.
- **The trees still differ.** `floor_tree_pairing` reports `same_tree: false` — floor drawn at
  `18327d977`, arms at `b329e702b`. Same book, two trees. That sentence stays on the surface.
- **The selection leg still refuses**, at 0.17 sems against a 2.20 bar. The floor that admits the
  page is not a floor that flatters it.

## Eighteen keys that had never been graded, and three defects in the grader

Making the page answer had a second effect nobody would have predicted from the diff.
`test_NO_TWO_KEYS_in_the_payload_answer_the_clears_zero_question_oppositely` scans the payload for
every boolean whose name carries `distinguishable`, `clears`, `stateable`, `sign` or `agree`, and
demands each be classified. It went red with **eighteen** unclassified keys.

None of them were new. `legs_on_one_bar` has rendered for weeks — its leaves were unreachable **on
the published feed** because the refused floor meant no leg stated anything. The registry read as
complete for as long as the page refused. *A registry only ever exercised on the branch the page
happens to be taking is the unreachable-branch shape this project has paid for repeatedly.*

The classification is where the work was:

- `legs_on_one_bar/legs/selection_gbp/*` is a **genuine second home** for `selection_leg`'s own
  numbers, so it is graded in the same classes and the agreement check now compares the two. They
  agree today — which is the point: it is now asserted rather than assumed.
- the **value** and **level** legs ask the same-shaped question of a **different quantity**, and
  today they answer it oppositely to the selection leg on purpose (7.4 and 4.7 sems against 0.17).
  Filing them STATISTICAL would demand three different quantities give one answer and would red
  this page **for being informative**. They get `ANOTHER_QUANTITY` and are graded by the per-leg
  consistency rule — which had only ever run on `selection_leg`, because it was the only leg that
  ever rendered.

Three latent defects in the control surfaced, each invisible until a key rendered conditionally:

| defect | what it would have done |
|---|---|
| `_ABSENT` is a sentinel **object**, so `value is not None` admitted it | any conditionally-rendered STATISTICAL row reports "one question, two answers" about a question only one key answered |
| the missing-row check could not tell an **unrendered block** from a **deleted key** | reds every honest refusal; the obvious silencing fix (drop the rows) restores the hole in the net |
| `_at` could not walk a **list** | a per-row key can be found by the net and named by no registry row — a permanent blind spot |

Both new helpers are mutation-proven, each by the control written for it and not by a neighbour:
forcing `_its_block_rendered` to a constant reds the sleep/complain partition alone, and making
`_at` take the first row instead of collapsing reds the list-walk control alone.

## A sentence that was only safe while its second home stayed unpublished

The site lane caught one more, and it is the same shape a third time.
`error_bar.reading` ends *"on the OTHER SIDE OF ZERO from the estimate above"* — true where that
sentence was written, directly under the estimate. The identical string is now also published at
`error_bar.legs_on_one_bar.legs.selection_gbp.reading`, where "above" is a different element, and
`test_a_payload_string_with_more_than_one_home_carries_no_here_relative_pointer` refused it on the
first render. The pointer now names what it means — *"from this leg's own mean across those 12"* —
instead of pointing at where it happens to be standing.

**The sibling branch carried the same defect, unfired, and was fixed with it.** The
`is_member is False` branch says *"nothing above bounds it"*; it is not taken on today's feed, so no
control could see it. A pointer that is only safe while its block stays unpublished is the same
defect waiting for the same trigger, and fixing the instance that fired while leaving its twin is
how this page has acquired its recurring shapes.

## The shape worth keeping

The drawn item's premise was spent and its stated work was landed — but the item was not therefore
empty. Two of its three clauses were verification, and the third (`is the reader seeing it?`) is
what surfaced the real gap: **a landed artefact that no constant named.** The guard was repaired on
2026-09-18 and the measurement it was built to admit had been sitting on disk unread since 09:10Z.
A guard that correctly refuses, next to a fact that would clear it, reads on the page exactly like
a guard working.
