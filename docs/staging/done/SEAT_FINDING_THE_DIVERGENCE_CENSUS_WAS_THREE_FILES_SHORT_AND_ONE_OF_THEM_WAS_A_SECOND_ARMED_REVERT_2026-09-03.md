**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The divergence census was three files short, and one of them was a second armed revert

**Class:** `uncommitted_and_orphaned_work` (primary), `controls_that_cannot_fail` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, executing
`SEAT_FINDING_THE_SIX_FILE_DIVERGENCE_MOVED_NO_ANCHOR_AND_ONE_CONTROL_WAS_BUILT_TWICE_2026-09-03.md`
**Subject:** the reconciliation itself — landed as `06ce91bc9` (merge) and `ef9c801e3` (nine paths).
**Discharged:** `site/capabilities/index.html`, `tests/architecture/test_the_svt_drift_belief_is_not_wired_to_any_decision.py`, `docs/observability/svt_drift_belief_grade.json` — all three of the paths this census added beyond the parent's six are now tracked and clean against origin, so none of them is a revert still armed and none is green on this machine only. The second armed revert is disarmed on the evidence rather than on the merge having happened: the capabilities page carries the precedence block and the superseded split renderer appears in it zero times, which is the direction that matters, a page that became more honest rather than one that merely changed. Every backtick above is read as a claimed artefact, so this prose carries none.

---

## What was executed, and it is done

The disposition in the parent finding was right and is carried out. Origin's lineage survives
(`world_level_identity()` → `_world_provenance()` → feed key `world_provenance`); the shared tree's
parallel `_world_moved_since()` / `_feed_with_world_currency()` / `arms-world` copy is discarded;
`_svt_drift_belief()` and its six door tests are salvaged onto origin's base. `_world_moved_since`
now appears nowhere in code — only in the prose of this item and the findings describing it.

## But the census that scoped it named six files, and the job was nine

**This is the finding.** The parent measured six paths because six paths were what `git status`
showed *for the subject it had in mind*. Three more were load-bearing and none of them would have
been reached by working the list as given:

| path | why the six-file list missed it | what it would have cost |
|---|---|---|
| `site/capabilities/index.html` | not anchor-touching, so it was outside the digest question the parent was answering | **a second armed revert** |
| `tests/architecture/test_the_svt_drift_belief_is_not_wired_to_any_decision.py` | not divergent at all — identical to origin | the salvage is refused; no landing possible |
| `docs/observability/svt_drift_belief_grade.json` | **untracked**, so it is invisible to every `git diff` the census ran | the salvaged half is green on this machine only |

### The second armed revert

`site/capabilities/index.html` was byte-identical between `HEAD` and `origin/main` and *differed
from both in the working tree* — 131 added, 53 removed. The additions were the SVT belief renderer.
**The 53 removed lines were the `basis_precedence` block**, and what the tree put back in their
place was the superseded `basis_split` renderer: the one that published a rung which fired three
times to the reader as `0`, filed the same day as
`SEAT_FINDING_A_RUNG_THAT_FIRED_THREE_TIMES_WAS_PUBLISHED_TO_THE_READER_AS_ZERO_2026-09-03.md`.

So the working tree held a *newer table and an older function* in one file, and committing the six
by pathspec would have left it armed while appearing to have finished the job. Committing seven
carelessly would have reverted that control too. Origin's copy is the base in `ef9c801e3` and only
the SVT block is re-applied onto it.

### The control that could not fail anywhere but here

`docs/observability/svt_drift_belief_grade.json` — the grading instrument's own capture — was
untracked. `_svt_drift_belief()` reads it, and so does the door test
`test_the_superseded_uncorrected_reading_never_reaches_the_reader`, which exists to stop the
uncorrected `belief_auc` reaching a reader. In an isolated tree the artefact is absent, the reader
takes the `_unavailable` branch, and the door test dies on `FileNotFoundError` rather than checking
anything. **It was green for eleven days because of a file that existed on one disk.** The gate
found it on the second landing attempt; the capture now lands with the code that reads it.

## Two corrections to the parent, kept beside it rather than folded in

1. **`_staleness_caveat()` is not part of the duplicate.** The parent lists it beside
   `_world_moved_since()` as the shared tree's copy. It is origin's own landed function — seven
   references in `origin/main:tools/generate_value_arms_data.py`. Discarding it as named would have
   deleted landed work.
2. **The three `test_MUTATION_*` legs are not the salvage.** The drawn item said to salvage
   `_svt_drift_belief()` *and the three `test_MUTATION_*` legs*. Those three legs
   (`..._figures_measured_on_this_very_tree_render_no_alarm`, `..._a_vintage_that_could_not_be_
   established_still_warns`, `..._a_feed_with_no_world_currency_block_still_warns`) are the mutation
   proof of the **discarded** lineage — the parent finding says so correctly and the doorbell that
   quoted it inverted the sense. Salvaging them would have kept the duplicate alive and re-armed
   the revert. The salvage is the six SVT door tests, which the parent named and the doorbell did
   not.

## What is NOT claimed

That the reconciliation is behaviourally complete beyond what the gate checks. The gate ran 587
tests green against the tree `ef9c801e3` creates; the full suite was not re-run against it here.

That `world_provenance` reports the flattering answer. It reports `available: false` — three runs
behind the page predate the world stamp — which is the fail-closed reading and is the point.

## Residue, named

`tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py` is **red at pristine
`06ce91bc9`**, inherited from `origin/main` and not caused by this work. It names
`tests/architecture/test_a_capture_may_only_judge_the_world_that_produced_it.py::test_the_page_and_
the_control_take_their_verdict_from_one_gate` and
`tests/sim/test_scenario_spine_consumption.py::test_neither_module_this_seam_touches_imports_the_
company_side`. Verified by checking out `HEAD` clean in a separate worktree and running it there.

The full suite `pid 3035242` running from the shared tree was invalidated before this turn touched
anything — `HEAD` moved twice beneath it (`06ce91bc9`, `ef9c801e3`). Its files were rewritten at the
end of this turn to disarm the revert, which is a judgement recorded here rather than hidden: a
re-runnable health run is worth less than a landed control left armed.

## Class registration

`uncommitted_and_orphaned_work`. The novel leg is that a divergence census is scoped by the
question it was asked, and an armed revert does not have to be in the divergent set to be armed —
`site/capabilities/index.html` matched `HEAD` and `origin` exactly and was still the more dangerous
of the two. **The census to run before a pathspec commit is not "what diverged from origin" but
"what does this pathspec touch, and is the working-tree copy of each one ahead of `HEAD` or behind
it?"** The untracked-artefact leg is `controls_that_cannot_fail`: a door test whose subject is not
in git is green everywhere it is not run.
