**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE4_ia_register_and_nav`

# RESULT — seven of the eleven archivals blocking SITE4 were real discharges, four were not, and SITE4 stays 0 with the four named

**Filed 2026-09-16 by the autonomous worker (scheduled tick)**, against the drawn Lane 0 direction
*"SITE4 reaches L2 once the archival that blocks it is in the record"*. The direction's premise held
exactly as written; its expected outcome did not, and the reason is the thing the direction itself
told the next reader to check first.

## The premise, re-measured before starting

All eleven findings named in SITE4's `level_hold_note` and in the level scan's
`contradicted_but_frozen` block were live in the committed record and archived only in the working
tree. Checked per file rather than by sampling: eleven of eleven succeeded on the HEAD read, eleven
of eleven were absent from the staging root on disk, eleven of eleven were present under the `done/`
room. Also confirmed against `origin/main`, which the previous note did not do — HEAD was one commit
ahead and zero behind, so the archival had not landed by another route either.

The scan's own report agrees and is reproducible: `python3 -m
tools.level_zero_contradicted_by_its_own_controls --atom SITE4_ia_register_and_nav --json` names the
same eleven with the same sentence, *"live at HEAD, archived only in the working tree: an uncommitted
archival is a discharge that has not happened"*.

**The mechanism that makes the `done/` move a discharge, stated because it is what makes the read
load-bearing:** `finding_severity.classifiable_documents` globs `*.md` **non-recursively**. Moving a
document into `done/` removes it from the population `lane_blockers` reads, and nothing checks that
the document earned it — there is no required `**Discharged:**` field on that route, and none of the
eleven carried one. So committing an archival is the one action in this lane that can bury a live
BLOCKING finding while turning every surface green. That is why the direction ordered the read first,
and the read is what this turn spent itself on.

## The seven that were real discharges, each with what was run

Each was judged against the tree, not against the document's own account of itself.

1. **`...THE_PUBLISHERS_REMEDY_REPORTS_LEVEL_ABOUT_THE_WORKTREE_IT_WAS_RUN_FROM...`** —
   `origin_reconcile.shared_tree()` exists and resolves the main worktree from
   `--git-common-dir`; its three mutation-proven legs pass.
2. **`...THE_RECONCILERS_BLOCKING_TEST_ASKS_WHICH_PATHS_DIFFER...`** — `_arriving_paths` now asks the
   merge result's diff against HEAD, keyed to the property ("if the merge result differs from HEAD at
   a path, git must write that path"), fails toward the older wider answer rather than toward
   `None`, and its eight-leg control passes. The fork it was filed against is closed: zero behind.
3. **`...THE_STALE_COPY_REMEDY_HAS_NO_MOVE_FOR_A_RIVAL_COPY_HEAD_ALREADY_SUPERSEDES...`** — both
   moves it asked for are built and **both are firing in today's live census**: the Kind-A door
   (`refresh_to_head`, with the preserve ref and the refusal that stops it being `git checkout` with
   a nicer name) and the pair naming at census time (`landing_pair`, which printed
   *"PAIR: simulation/customer_events.py needs simulation.market_switching_propensity.bill_scale_for,
   which exists ONLY in the UNCOMMITTED copy"* this turn). 27 controls pass.
4. **`...THE_PAIR_MOVE_PARTNER_WAS_HAND_LAUNCHED_INTO_THE_TICKS_OWN_CGROUP...`** — the relaunch
   through `launch_long_job` left the record the finding said a bare `python3 &` cannot leave, and
   the artefact that record names exists and is non-empty. The job it was filed about finished.
5. **`...THE_PUBLISHERS_OWN_REMEDY_CANNOT_CLEAR_ITS_OWN_REFUSAL_AND_THE_REPLACEMENT_RUN_HAS_NO_LEVEL_ARM...`**
   — both halves. `origin_reconcile._landing_clause` now states the landing step **per kind** and
   keyed to the property that makes a landing clear the refusal, which is item 4 of its own "what is
   next". And the pair move landed: the published feed's run is a 2026-09-10 one, its
   `level_vs_selection.available` is true, both `method_skill.fixed_horizon` and
   `method_skill.survivorship` are true, and the error bar is on nine seeds and 27 passes — which is
   every check its item 1 asked for.
6. **`...THE_FORKS_MERGED_FEED_REPUBLISHES_A_SENTENCE_ITS_OWN_RECORD_CALLS_WITHDRAWN...`** — its item
   1 offered two remedies and the second one was taken: the third sign home stopped answering. The
   published feed's `current_world.selection_leg` now carries `resolved: null` and a
   `verdict_withheld_because` that says the verdict would be one draw's. The red it refused to land
   around, `test_the_withdrawn_sentence_is_kept_beside_the_reading_that_replaced_it`, passes, and the
   headline does not contain the withdrawn sentence. Items 2 and 3 followed: the merge relanded.
7. **`...THE_SIGN_DISAGREEMENT_IS_INVARIANT_TO_THE_BAR...`** — same discharge as 6, which is correct:
   it was filed as the diagnosis whose repair was owed, and the withheld-verdict route is that
   repair. **One residual is carried here rather than buried with it**: its §6, a defect it found in
   passing and explicitly did not fix, is still unfixed. `origin_reconcile` truncates its conflict
   `detail` at a 400-character slice, so the refusal can reach the reader one clause before the
   remedy that lives in `surgical_land`. It is a slice width, it is not this lane's path, and it is
   named here so archiving the finding does not take it out of the record.

## The four that were not, and what each one is still live about

None of these four is stale prose. In each case the finding's own named remedy is unbuilt in the
tree today, and in the first case the defect is firing.

1. **`...THE_HOLDER_WORK_RULE_COUNTS_NAMES_SO_A_RENAMED_DRAFT_READS_AS_WORK_TO_LAND...`** —
   `stale_copy_refusal.gains_over` still returns `after - before` and nothing else, so HOLDER WORK
   is still a name count. The REPLACEMENT third state the finding specified does not exist. **And
   this turn's census printed the defect on a live path:** `background/supervisor.py` is reported as
   containing *not one* of the 33 distinctive lines commit `2212d0eed` added — the differentiated-
   staging repair, which is itself the fix for a finding surfaced 3,421 times into an
   undifferentiated channel — and three lines later the same block says it *"supplies 1 name(s) HEAD
   lacks (PUBLISH_GATE_WINDOW_SECONDS), so it is HOLDER WORK"* and names `surgical_land --content`.
   Both halves on one page, exactly as filed: *this copy reverts a landing* and *land this copy*. A
   lane that follows that remedy reverts the repair.
2. **`...THE_DELIVERY_LANE_TRUNCATES_A_CLAIM_ID_AT_A_DECIMAL_POINT...`** — nothing was built.
   `record_landing` is **byte-identical** between `9b7a3bc10` (2026-09-09, two days *before* the
   finding was filed) and HEAD, so no repair was attempted, and the two commits to
   `background/delivery_lane.py` since are about `--release` and swept rows. Measured against a
   fixture store holding `work-p6s-2`: binding `work-p6s-2.45-percent` returns zero paths. The
   normalising remedy is absent; the fallback remedy is unevidenced as a *build* for the same
   byte-identity reason; and the control the finding named — bind with an id containing a `.` and
   assert the drawn claim has non-empty `paths` — exists nowhere under `tests/`. The live compensation
   is a practice ("read the store, bind the key that is there"), and a practice is not a mechanism.
3. **`...THE_R1_COPYS_MISSING_PARTNER_IS_IN_A_SALVAGE_COMMIT...`** — `refresh_to_head --superseded`,
   the third door it proposed, is not built: the string does not appear in the module. Its subject is
   the same gap as 1 — two doors keyed to one name-counting rule, agreeing with each other and both
   wrong on a superseded copy — so discharging it while 1 is live would split one class across two
   verdicts.
4. **`...THE_STALE_COPY_CENSUS_CRASHES_IN_THE_SHARED_TREE_BECAUSE_ITS_OWN_SIBLING_MODULES_NEVER_REACHED_DISK...`**
   — the crash does not reproduce today, and that is the trap rather than the discharge. What cleared
   it was the tree catching up to origin, which is the *condition* passing and not a fix. The
   deferred import inside `door_verdicts` is still bare, so the same composition — tree behind
   origin, a new sibling module not yet arrived — raises `ImportError` again rather than answering
   "paths listed, doors ungraded, and here is why". The finding priced its own remedy at about six
   lines and recorded rather than built it because the file was held dirty by another lane at the
   time. On this project's own rule an instance cleared by its condition is not a class fixed.

## What this means for SITE4, and what it does not

SITE4's L2 evidence is untouched by any of this and remains in hand and re-run. What holds the row is
unchanged in kind and smaller in size: `H_harness` holds **four** live BLOCKING findings in the
committed record instead of eleven, and OPS11 refuses on the tree the commit would create. The row
stays at 0 with the four named, and the `level_hold_note` is rewritten to say so, because the note it
replaces told the next reader that the row *"moves the moment that staging archival lands"* — and
that sentence is now false for four of the eleven and would have sent the next tick to force a move.

The discharge path on offer is still `record_limitation_accepted`, and the 2026-09-06 answer still
holds at a count of four: accepting live BLOCKING findings about this lane's own instruments, to push
one row through, is marking your own homework. Three of the four are about the instrument that
decides whether a landing reverts another lane's work, which is the single most expensive thing to be
wrong about here.

**So the condition is sharp and it is now WORK, not a wait.** The four are not somebody else's
uncommitted archival any more; they are four named, unbuilt repairs, and the largest of them is one
clause:

    holder work  <=>  exists a hunk H such that  symbols_added(H) - HEAD_symbols  is non-empty
                      AND  symbols_deleted(H) & HEAD_symbols  is empty

That clause discharges 1 and 3 together and is computable from the two symbol sets plus the hunk map
`isolate_hunks` already builds. 2 is a one-leg change in `delivery_lane` plus the control it names.
4 is the six lines its own author costed.

## A red found in passing, not caused here and not repaired here

`tests/tools/test_generate_value_arms_data.py` runs 215 passed, 1 failed in the shared tree:
`test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes`. This turn wrote
nothing that any of that file's subjects read — it moved staging documents and one map note — and a
green-or-red reading taken in the shared tree measures several lanes rather than one change. Recorded
so it is not discovered as new, and not diagnosed here because attributing it needs a clean extract.
