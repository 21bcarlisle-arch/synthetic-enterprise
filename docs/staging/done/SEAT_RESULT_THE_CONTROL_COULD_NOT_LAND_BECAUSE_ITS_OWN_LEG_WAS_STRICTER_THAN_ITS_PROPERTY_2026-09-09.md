**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over` · **Class:** `controls_that_cannot_fail`

# The control could not land because its own leg was stricter than the property it holds, and the blocker it was waiting on was never its to clear

**2026-09-09, scheduled tick, LANE 1 BUILD draw: `W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over`
(lane W2_customer_generator, dial 50, level 0 → 3). Landed: the control at HEAD and the row at level 1.
Every figure below is labelled with the tree it was measured in.**

---

## 1. Where the atom actually stood, and it was not where either prior record said

Two documents described this atom's state and both were wrong in a way that mattered.

The **map row** said the control "is BUILT and passes 14/14 — and is not at HEAD, and could not be
landed with this row", blaming the tenth of ten `reduction_dimension` declarations.

`SEAT_RESULT_W2_28S_STATED_BLOCKER_WAS_NEVER_MEASURED_...` (filed the same day) said the opposite
conclusion: *"W2_28 is at level 1 with the control at HEAD, mutation-proven."*

Measured this turn:

| Claim | Real state |
|---|---|
| "the control is at HEAD" | **No.** `git ls-tree -r HEAD` carries `tools/reduction_dimension.py` and not the control. |
| "the control is not in git" | **Half.** It is `A ` in the shared **index** — staged by a prior turn whose commit was refused, so `git ls-files` reports it and `git ls-tree HEAD` does not. |
| "the row is at level 1" | **No.** `level_current: 0`. |
| "all ten declarations are uncommitted" | **No.** Nine are at HEAD; only `simulation/weather_cell_siting.py`'s is outstanding, and that one is `M` on disk with exactly one hunk, which is the declaration block. |

**The one-line generalisation, and it is the third time it has cost this project a turn: a claim that
a file "is in git" resting on `git ls-files` is a claim about the INDEX.** A staged-and-refused file
reads identically to a committed one there. `git ls-tree -r HEAD` is the instrument for the question
anyone actually means.

## 2. The blocker was real, at pristine HEAD, and belongs to another lane

`git worktree add --detach HEAD`, nothing else applied:

```
tests/simulation/test_weather_cell_siting.py
  1 failed, 13 passed
  FAILED test_derive_reproduces_the_committed_artefact
      {'annual_wind': 0.2062} != {'annual_wind': 0.2782}
      {'annual_sun':  0.2493} != {'annual_sun':  0.1725}
```

The committed `sim/weather_cells/site_cells.json` does not reproduce from the committed grid. That is
lane **W1_market_weather**'s live BLOCKING artefact-cut finding
(`SEAT_FINDING_TWO_LANES_BUILT_W1_14S_ARTEFACT_CUT_TWICE_...`), and naming
`simulation/weather_cell_siting.py` in any pathspec selects that suite, so no commit carrying the
tenth declaration can pass the gate.

The shared tree is red the *other* way — `2 failed, 12 passed`, on
`test_the_accept_branch_is_reachable_and_it_matches_climate_not_proximity` and
`test_one_driver_disagreeing_refuses_the_whole_substitution`, `assert 5 == 10` — because it holds the
uncommitted re-cut. **No state of the tree is 14/14.** Confirmed, not inherited: this is the second
lane to measure it and the counts match the first exactly.

## 3. The actual defect was in the control's specification, not in the blocker

The live leg read:

```python
def test_every_claim_about_the_drawn_population_declares_its_reduction():
    """The live tree. Empty is the only passing state, and the refusal names what is silent."""
    silent = undeclared()
    assert silent == []
```

The file's own docstring states the property two paragraphs above it: *"the CENSUS finds the claims,
so a new one cannot arrive silent."* `== []` is not that property. It is that property **plus** "and
every claim that ever arrived has already spoken" — and the second half is not a statement about this
control's subject at all. It is a statement about the state of nine other lanes' work.

What that cost, measured rather than asserted: **two days in which nine landed declarations were
guarded by nothing**, because the control that would have guarded them was waiting on an artefact
dispute it has no part in. A control that cannot land guards nothing, and the strictness that
prevented it landing was not honesty — it was a specification error that read like rigour.

This is the mirror of a rule already in the record. "Key a control to the property, not to today's
answer" is normally violated by pinning to a number that is *too generous*. Here it was violated by
pinning to a state that is *too strict*, and the failure mode is the opposite one: not a control that
stays green while the claim rots, but a control that stays uncommitted while the claim goes unguarded.
Both are the same error — the assertion is about the tree's current state rather than the property.

## 4. What landed

`tools.reduction_dimension.OUTSTANDING` — one row, `simulation.weather_cell_siting`, carrying the
reason and the document whose discharge deletes it. Three legs replace the one:

- `test_no_claim_about_the_drawn_population_arrives_silent` — `unexpected_silence() == []`. This is
  the property. Green in both trees.
- `test_the_outstanding_debt_is_shrink_only` — `len(OUTSTANDING) <= 1`. Without it the leg above is
  satisfiable by writing the defect down, which is the allowlist failure this repo has hit
  repeatedly. Free in the honest direction: paying the debt shrinks the list and it still passes.
- `test_every_outstanding_row_names_a_document_that_still_exists` — the route out. When
  W1_market_weather's finding is archived the citation stops resolving and this goes red, so the debt
  is re-measured by whoever discharged the blocker rather than inherited by everyone after.

**Keyed to the document and not to the module's disk state, deliberately.** A leg asserting "the
outstanding module is still silent" is green in the extract and red in the shared tree — the exact
two-trees split that produced this list. `stale_outstanding()` reports it and the CLI prints it; no
assertion rests on it, and nothing is capped without saying so.

### The measurement that matters

| Tree | Control |
|---|---|
| shared working tree | **16 passed** |
| clean `--detach HEAD` extract + these two files only | **16 passed** |

**The first state of this control that is green in both.** Being green in only one is the whole
reason it could not land.

R15, four mutations run in the clean extract, one leg killed each and no other:

| Mutation | Killed |
|---|---|
| `unexpected_silence` returns `undeclared()` unfiltered | `test_no_claim_about_the_drawn_population_arrives_silent` |
| a second `OUTSTANDING` row added | `test_the_outstanding_debt_is_shrink_only` |
| the row's citation points at a document not in the tree | `test_every_outstanding_row_names_a_document_that_still_exists` |
| the citation removed entirely | same leg, on `cites no document` |

Restored: 16 passed. `test_the_census_can_see_a_claim_that_declares_nothing` — the poison round —
runs before every green leg, so the census is proved to reach something.

## 5. What is next

1. **Level 2 needs the debt paid**, and paying it needs W1_market_weather's artefact cut settled. It
   is not W2_28's to settle, and the row now says so where a reader will find it. The citation is the
   route: archiving that finding reds this control.
2. **The nine covered declarations are now guarded at HEAD.** Before this commit they were guarded in
   one working tree.
3. **`simulation/weather_cell_siting.py`'s declaration hunk stays on disk, uncommitted and
   attributed.** It is one hunk, it is this atom's, and it lands the day the weather suite is green
   in a clean extract. It is deliberately NOT in this commit's pathspec.
