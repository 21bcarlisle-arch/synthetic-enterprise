**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the prose door is open, and the control that watched it had pinned the fault as its
expected answer

**Filed:** 2026-09-23. Drawn as Lane 0 delivery,
`the-census-names-a-permanently-shut-door-for-seven-of-eighteen-rows`. Landed `4da626379`.

## The premise was live and the measurement reproduced it exactly

`d349176c1` is an ancestor of `origin/main`, as the draw said — but the item was ranked as its
FOLLOW-ON, not as work it contained, so the premise was not spent. Reproduced before touching
anything: **7 of 18 census rows named `refresh_to_head` and got `refused_no_reader` back.** All
seven `.md` or `.yaml`; that tool answers `refused_no_reader` for those suffixes by construction
and can never answer anything else.

## The grader was satisfied by the fault

`Loss.names_the_refresh_door` was cut on 2026-09-22 for this shape and its control asserted
`"SHUT" in out["note.md"]` — the defect PINNED as the expected answer. The grader printed "THE
DOOR THIS REFUSAL NAMES IS SHUT" on every prose row, went green, and nothing made anyone fix it.
A control satisfied by the fault is worse than no control: it converts an open defect into a
passing test. That leg's oracle is now inverted — the row must be graded AND the door must be
open.

## The decision: grow the reader, in the document's own terms

Both halves of the item's either/or, because naming no door is the cheap fake. `PROSE_SUFFIXES`
reads prose as its non-trivial **lines** — the unit `isolate_hunks --keep` selects over and a
reader recognises as theirs, and the conservative direction (a reformat reads as content, so the
copy is refused rather than overwritten). `READABLE` does **not** move: widening it would red
every lane for the ordinary churn of a shared checkout, which is the trade `clock_judge` already
measured and refused. `clock_judge` now reads the gains, so `remedy()` picks the door from the
copy's content rather than from the suffix's silence.

**`isolate_hunks` reaches prose — measured, not assumed.** `--survey docs/institutional/
knowledge_map.md` returns 3 selectable hunks. That is the fact the whole remedy rests on.

## Before and after, same instrument

| | before | after |
|---|---|---|
| census rows naming a SHUT door | **7 of 18** | **0 of 17** |
| prose rows reaching `refreshable` under `--base-wins` | 0 (unreachable) | **5 of 7** |

The two that do not refuse for stated, checkable reasons: `ANNUAL_REPORT_IMPORT_DEBT.md` has
landable hunk 2, so `--keep` takes the work without the revert; `weather.md` is `PARTIAL` at 13 of
29, so the clock does not license discarding it. `base_wins_rules` moved to `stale_copy_refusal`
and is re-exported, because `remedy()` must read the same rule the door reads.

**Stated because "0 rows name a shut door" is satisfiable by naming no door at all:** on today's
tree no copy happens to supply nothing, so the open branch is exercised by
`test_the_three_clock_remedies_are_distinct_and_each_names_a_door_that_answers` rather than by a
live row. That leg asserts all three clock shapes are reachable, distinct, and each hands the
reader a command the named tool will accept.

## Corrections, beside the claims

* Three legs asserted "`.md` has no symbol reader and never will". `.csv` carries the `NO_READER`
  example now; the rule is untouched.
* `test_the_clock_refusal_names_the_commit_and_a_door_that_exists` asserted the **wrong door** and
  went green for it: it required `isolate_hunks` to be ABSENT from a remedy for a copy holding a
  line HEAD lacks. That was an artefact of there being no prose reader, read as a fact about the
  copy.
* Three of my own draft assertions keyed to a substring (`"--base-wins" not in text`) rather than
  to the recommendation, and each would have reddened on the sentence that keeps a reader OUT of
  that door. The leg now parses the `python3 -m ...` command lines, which is what a reader types.

## Mutation battery

The suffix gate, `names_the_refresh_door`, the gains read, and the base-wins fallback each red a
named leg. `PROSE_LINE_FLOOR` was **silent** — established as a missing test rather than an
equivalence, and it now reds in both directions. Raising the floor is the destructive direction: a
line stops being evidence, the copy grades `is_rival`, and the remedy hands it to the door that
overwrites those bytes.

## What this cost, and it is this module's own subject

Two instances of the class, met while repairing it.

1. **I edited a stale copy of `tools/refresh_to_head.py` for the whole build.** The census had
   said `predates_landing` on it in its first output and I read past it. Writing HEAD's bytes over
   it then destroyed another lane's live, uncommitted `--staged-too` work in the shared tree.
   Recovered by reconstructing their pristine copy from a backup, three-way merging at their base
   (`32010eeb2`), and landing only my hunks — their 9 hunks are untouched on disk. **The
   `--staged-too` lane lost nothing, but only because a backup existed; the door I was building
   is the thing that should have stopped me, and it would have if I had run it on that path.**
2. **A usage grep for `rth.CLOCK` returned 0 and the answer was wrong**, because the working copy
   of this tool's own suite predates the landing that added the leg typing it. Asked of HEAD it
   returns 1. The first draft of the import block dropped a live re-export on that reading.

→ Both are the same sentence: *a question about what the tree contains, asked of the working copy,
answers about a tree that no longer exists.*
