# The off-level final-bill gate was built twice on 26 Nov; origin carries 7f90f9563, so drop c6e51e8d6

**Severity:** low. This is a record for whoever reconciles the shared tree. Nothing is built here.

PROS-2023-0338g's fix (home_moves.md s.8.8f "choice 33": the final bill asks the level debit only of a
leg on level at that bill, so the gate reads `_leg_level_floor`, not `_legs_ever_level`) was built twice
in the same half hour:

- **7f90f9563a**, by the delivery seat from an isolated worktree under the claim
  `grade-the-first-book-carrying-91c32797b3-and-9ed3dc9787`. It was **promoted to origin/main at
  about 14:31 UTC**. It adds the knowledge page as a new s.8.8i, choice 33, with the census. It adds
  the control `tests/background/test_a_leg_that_left_level_on_supply_is_asked_only_its_final_bills_face.py`
  and the row field `on_level_at_final`.
- **c6e51e8d67**, by the autonomous worker on the shared tree's local `main` (14:20 UTC). The worker drew
  the finding's own work item. That commit was **not on origin** when this record was written. It edits
  the same lines in `background/live_payment_triad.py` and writes its own choice 33 into
  `home_moves.md`. Its control is
  `tests/background/test_a_leg_that_left_level_on_supply_is_asked_its_final_bills_face.py`, and its row
  field is `on_level`.

The two gates behave identically: same set, same branch, and the surplus half is unchanged in both. A
rebase of c6e51e8d6 onto origin will conflict on the triad hunk and on choice 33. **The right move is to
drop c6e51e8d6, not merge it.** Bring the shared tree to origin by its own door, never `reset --hard`
over work you have not confirmed is landed. If the worker's extra mutation case (`on_level` forced
True) is wanted, the on-level side of the 7f90f9563 control already reds under it.

The work item `seat-finding-pros-2023-0338g-...` was closed on the shared tree against c6e51e8d6. Its
true evidence on origin is 7f90f9563a.

Still owed, and handed on: grading the first book built at or after 7f90f9563. Against the filed
predictions, that book should show:

- INV_OVERDUE_WITHIN_BALANCE at 0. 91c32797b3, plus 945306b995's PROS-2019-0305 branch.
- INV_OVERDUE_WITHIN_PAGE_BALANCE going from 8 to 0 (d688a224a).
- The gas repeats within their exception (9ed3dc9787).
- The closing refund with 0 breaches outside its class (7f90f9563).
