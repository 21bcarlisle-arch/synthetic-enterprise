**Severity:** INFO · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: is the name-counting gap the two 09-08 freezers describe still live, after `cuts_among` landed on 2026-09-16?

**Written 2026-09-17 by the delivery seat (lane 0), working the drawn item "discharge the six
freezers because archiving is not discharge". Written BEFORE the measurement, because I do not know
the answer and the two candidate answers lead to opposite turns.**

## Why this is asked at all

Two BLOCKING findings freeze `SITE4_ia_register_and_nav` and
`H47_the_orientation_header_states_a_figure_it_computes`:

- `SEAT_FINDING_THE_HOLDER_WORK_RULE_COUNTS_NAMES_SO_A_RENAMED_DRAFT_READS_AS_WORK_TO_LAND_2026-09-08.md`
- `SEAT_FINDING_THE_R1_COPYS_MISSING_PARTNER_IS_IN_A_SALVAGE_COMMIT_AND_HEAD_SUPERSEDED_IT_UNDER_NEW_NAMES_2026-09-08.md`

Both describe ONE defect: `tools/refresh_to_head.judge_copy` grades a copy HOLDER WORK whenever it
supplies a name HEAD lacks, and a **renamed or dead-API draft** supplies names and no work. Both
doors — `isolate_hunks --content` and `refresh_to_head` — are keyed to that same name count, so they
fail in the same direction: one offers to land dead-API tests, the other refuses to discard them.

**All four named instances are now at HEAD on the shared tree** (measured this turn:
`background/self_clearing_alarm_census.py`, `site/test_harness_delivery_record.py`,
`tests/tools/test_r1_inference_ceiling.py`, `site/harness/index.html` — all four `git diff --quiet
HEAD` clean at `882ef8aad`). So the roster is empty. An empty instance list never clears a
RULE-class finding, which is why the question below is about the rule and not about the four paths.

Since the findings were filed, `stale_copy_refusal.cut_of`/`cuts_among` landed (2026-09-16) and
`judge_copy` now subtracts, from `gains`, every name the base **once bound and deliberately
deleted**. That is a real narrowing of the same predicate. The question is whether it is the SAME
narrowing the findings asked for.

## The prediction, recorded before running anything

**I predict the gap is STILL LIVE, and that `cuts_among` does not touch it.**

The reasoning, so it can be wrong in a readable way: `cut_of` asks git whether the base's history
ever BOUND the name and then removed it. The r1 copy's eleven names were never committed by anyone —
they are a working-tree draft written against a module API (`_scores_on_folds`,
`honest_point_estimate`) that lives only in a salvage commit on no branch. A name that was never in
the base's history is not a *cut*; it is an *absence*. So `cuts_among` returns empty for it, `gains`
stays non-empty, and `judge_copy` returns `SUPPLIES_NEW` — the identical refusal the finding quotes
verbatim.

Concretely I predict `judge_copy` returns state `refused_supplies_names_head_lacks` on a copy whose
supplied name is a function that no committed tree ever defined, whose body references a module
attribute that no committed tree defines.

**The falsifier:** if `judge_copy` returns `REFRESHABLE` on that input, `cuts_among` already covers
the class, both findings are discharged by a repair that landed on 09-16 without either being
updated, and this turn is two header lines and a level recording — no new mechanism at all.

## The measurement

A synthetic minimal case, built in a scratch repository rather than against the four real paths,
because the four real paths are at HEAD and a case that cannot be constructed cannot be re-run by
the next reader:

1. A repo with one commit. `m.py` binds `kept`. `t.py` binds `test_new` and calls `m.kept`.
2. A working copy of `t.py` that binds `test_old` instead, and calls `m.gone` — an attribute no
   committed tree in that repo defines.
3. Run `tools.refresh_to_head.judge_copy(root, "t.py")` and read `.state`.

`test_old` is the renamed-draft shape (finding 1) and `m.gone` is the dead-API shape (finding 2), in
one file, because the two findings are one defect and the fixture should say so.

## What each answer makes me do next

- **STILL LIVE (predicted):** build the third door the second finding specifies —
  a copy whose supplied names are *proven dead by running them* is admitted, printed on the surface
  the way `surgical_land --drops` is. Mutation-prove it, land it, discharge both findings against
  that commit, then record H47's level and grade SITE4.
- **ALREADY CLOSED (falsifier):** discharge both findings against the 09-16 `cuts_among` commit,
  note in each header that the repair landed in another lane and neither finding was updated, and
  file that as its own small finding — a defect fixed without its finding being told is exactly the
  shape that leaves a lane frozen for nine days.

Either way the two rows leave `contradicted_but_frozen` this turn.
