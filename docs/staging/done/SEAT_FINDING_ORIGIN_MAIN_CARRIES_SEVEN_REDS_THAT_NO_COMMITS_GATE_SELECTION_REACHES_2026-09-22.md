**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

**Discharged:** `tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_the_module_subject_guard_is_selected_by_its_SUBJECT_and_not_by_a_stem`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_a_brand_new_module_selects_every_member_of_the_batch`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_a_staging_record_on_its_own_selects_the_discharge_control`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_an_atom_store_on_its_own_selects_the_store_falsifier_control`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_a_new_test_file_selects_the_ratchet_over_the_whole_test_CORPUS`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_a_commit_that_can_break_nothing_still_selects_nothing`
— re-graded 2026-09-24 against `origin/main == 387a125dd`; see **The re-grade** at the foot.

# origin/main carries seven reds that no commit's gate selection reaches — and one of them landed today

Found while landing an unrelated repair to `tools/generate_value_arms_data.py`. **None of the seven
is mine**, established against `HEAD == origin/main` in a linked worktree. Filed rather than
repaired — see the last section for why.

The clearest instance is a here-relative pointer that entered `_renewal_churn_belief` today, so it
is the one written up first; the seven-red census below is the finding it belongs to.

## The red

```
tests/tools/test_the_value_arms_pages_undriven_pointers.py
  ::test_every_tied_here_relative_pointer_is_true_from_the_region_it_lands_in

_renewal_churn_belief:7673 'published above' in _renewal_churn_belief is not a pointer this rung
knows what to check, so its direction is unjudged -- register it in `_REFERENTS` with what it
points at
```

The sentence, in the second-grade block's `why_not`:

> "…It also names no world. **The reading published above** is the one with an interval, a ceiling
> on its own rows and a stated population."

## It is on origin/main, and it landed today

- Reproduced in a clean `git archive HEAD` extract with `HEAD == origin/main`
  (`39330677b`) — same rung, same subject, same line. So it is not worktree locality and not
  my diff.
- `git log -S"published above" -- tools/generate_value_arms_data.py` names **`eff979da5`
  (2026-09-22, "the renewal belief does not order who leaves, and the grade was already on disk")**
  as where it entered.
- The detector that catches it is not new either: `da154eaf5` (2026-09-19) taught the rung the words
  `run` and `published`. So the vocabulary was already widened three days before the sentence that
  trips it landed.

## Why nothing stopped it, and this is the part worth keeping

`tools/pre_commit_test_gate.py` selects by subject module stem, and on a commit staging
`tools/generate_value_arms_data.py` it selects 45 files — including
`tests/tools/test_generate_value_arms_data.py` and the site door, and **not**
`tests/tools/test_the_value_arms_pages_undriven_pointers.py`. Verified directly by running the gate
against a staged pathspec containing that very module.

So the rung guards a property of `generate_value_arms_data.py` and is not selected when
`generate_value_arms_data.py` changes. That is why a sentence could land at 10:xx and still be red
hours later with every lane's commits going green over the top of it. The instance is one sentence;
**the mechanism is a guard whose subject and whose selection key disagree**, which is the same shape
as a guard silently scoped to a minority of the tree.

## It is not alone: origin/main is carrying SEVEN reds, and no gate selection reaches any of them

Running the wider suite against this landing turned up seven failures. **All seven reproduce at
`HEAD == origin/main` (39330677b) in a LINKED GIT WORKTREE** — not an archive extract, because six
of them are git-oracled ("cites a falsifier the repository does not have", "names a commit that
really retired it") and a `git archive` extract has no `.git`, which inflated the same run to 30
failures and would have been the wrong ruler.

| file | test |
|---|---|
| `test_the_value_arms_pages_undriven_pointers.py` | `..._tied_here_relative_pointer_is_true_from_the_region_it_lands_in` |
| `test_a_commons_artefact_can_tell_when_its_source_was_revised.py` | `test_every_verdict_can_be_recorded[superseded]` |
| `test_a_commons_artefact_can_tell_when_its_source_was_revised.py` | `test_every_verdict_can_be_recorded[cannot_tell]` |
| `test_a_coverage_claim_declares_what_it_reduces_over.py` | `test_no_claim_about_the_drawn_population_arrives_silent` |
| `test_no_committed_discharge_cites_an_unlanded_falsifier.py` | `..._cites_a_falsifier_the_repository_does_not_have` |
| `test_no_committed_store_claims_an_unlanded_falsifier.py` | `..._credits_a_falsifier_the_repository_does_not_have` |
| `test_no_tree_scan_passes_on_an_empty_population.py` | `test_no_tree_scanning_test_passes_on_an_empty_population` |

None of the seven is in the 45-file selection the gate computes for a commit staging
`tools/generate_value_arms_data.py`, `tests/tools/test_generate_value_arms_data.py` and the site
door. So a lane can land all day, green, on top of all seven.

**This is the finding, and the pointer above is one instance of it.** The mechanism is not "someone
broke something"; it is that the tree has a standing red set that the commit gate's selection cannot
see, so nothing converts a red into pressure on anyone. The instance count is what makes it worth a
document: one stale pointer is a slip, seven simultaneous reds with no owner is a missing control.

## The remedy this repository has already chosen for this exact shape

Not `_REFERENTS` registration, probably. `_redraw_band_clause`'s own docstring records the rule the
last four of these were fixed to: **a name, not a direction** — "the published draw" rather than
"the figure above" — because the sentence has more homes than its producer can know. `why_not` here
is a feed string with at least the same exposure. The likely one-line fix is to name the first
grade rather than point up at it, but which name is right is the owning lane's call, not mine.

## Why I filed instead of fixing

1. It does not block the landing it was found from — the selection above excludes it.
2. `eff979da5` is hours old; the lane that wrote that sentence is the one that knows what the
   reading it points at should be *called*, and a wrong name is worse than a pointer.
3. Repairing a live subject another lane is plausibly still working is how two lanes spend two turns
   on one sentence.

**What done means:** the pointer names its subject, `test_every_tied_here_relative_pointer_is_true_from_the_region_it_lands_in`
is green on origin/main, and — the load-bearing half — the gate's selection reaches the rung, so the
next one of these is caught at the commit that writes it rather than by a passer-by.

---

## The re-grade (2026-09-24, a second seat, re-measured not re-read)

This finding was drawn again on 2026-09-24, two days and two trunk commits after
`SEAT_RESULT_THE_SEVEN_REDS_ARE_GREEN_AND_THREE_WERE_DETECTORS_OVER_MATCHING_2026-09-22.md` claimed
to close it. **That note is a past-tense staging record and is no evidence a commit exists**, so
nothing below is taken from it. Every reading is against a **linked** worktree at
`origin/main == 387a125dd` — linked, not a `git archive` extract, for the reason this finding itself
established: six of the seven are git-oracled and an extract has no `.git`.

**Both halves hold.**

*The seven:* all six files run green — 42 passed, 1 skipped, 0 failed. The single skip is
`test_no_committed_discharge_cites_an_unlanded_falsifier.py:683`, a declared conditional arm
("no live violation is present on disk here") whose sibling arm ran and is the proof. So the skip is
the control working, not a red hiding.

*The selection half,* measured by calling `select_targets` directly at that base:

| commit shape | targets | of the six control files |
|---|---|---|
| the value-arms producer alone | 48 | **6 of 6** |
| producer + its own test + the site door | 52 | **6 of 6** |
| a staging record alone | 1 | the discharge control |
| a pure regenerated-output commit | 0 | none — the fast path is intact |

*And the production layer, which `select_targets` alone does not establish* — the two-layer trap
this repository has filed before, where a conditional reading and a production reading answer
opposite ways. `SUBJECT_TESTS` entered at `9ded3a80e`; since then **nine real commits have staged
`tools/generate_value_arms_data.py`** and reached `targets = select_targets(staged)` at line 2094.
The mechanism has been exercised nine times against real landings, not once against a fixture, and
the rung is green at the end of them. That is what the draw's DONE clause asked for and it is met by
commits that already happened rather than by one written to satisfy it.

Both commits the closing note named are real and ancestral to `origin/main`: `943b9b4f9`,
`b305119b1`.

**Why this document sat BLOCKING for two days with nothing owed.** The work landed on 09-22; the
severity header did not move. `staging_rooms --check` reports *RECORDED findings in the root* as
archivable, and `finding_severity --by-construction` names non-BLOCKING documents whose text says an
instrument is wrong — **neither asks the opposite and more expensive question: is a BLOCKING
document's own cited falsifier set already green?** Under OPS12 clause 3 a live BLOCKING finding
draws ahead of its whole lane, so a stale grade froze `A_strategy_governance` behind finished work
and spent at least one further invocation re-deriving that. The instance is closed by this re-grade;
**the class — a discharged finding whose severity nobody lowered — is filed separately rather than
fixed here**, because a control over it is new work and this document is not the place to mint it.
