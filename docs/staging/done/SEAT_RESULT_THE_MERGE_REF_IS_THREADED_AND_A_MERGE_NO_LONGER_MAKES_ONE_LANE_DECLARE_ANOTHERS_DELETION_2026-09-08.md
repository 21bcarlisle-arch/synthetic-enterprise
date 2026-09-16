**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# The merge ref is threaded, and a merge no longer makes one lane declare another lane's deletion

Answers the first of the two **What is next** items in
`SEAT_FINDING_THE_STALE_COPY_GUARD_RE_ASKS_ON_A_MERGE_AND_MAKES_ONE_LANE_DECLARE_ANOTHERS_DELETION_2026-09-08.md`.
The second — the `--drops` census against the commit that actually chose each deletion — is **still
open** and is stated as such at the bottom rather than left to be inferred from silence.

## What changed

`tools/stale_copy_refusal.violations()` now takes `merge_ref`, and `_land_once` passes the other
parent on a `--merge` (the same one call site serves both landing kinds, so there was nothing to
duplicate). The predicate is `adopted_from_merge()`: a path is exempt when it is **unchanged between
`merge-base(parent, ref)` and `parent`** — this side never touched it — **and the ref changed it**.

**The predicate is about this side's history, not the other side's, and that is the whole design.**
The tempting version — *exempt a path whose result blob equals the merged ref's blob* — was written
down and refused: when `parent` carries names the ref does not, `result == ref` **is** the shape of
`a_merge_that_adopts_one_sides_rewrite_silently_deletes_the_other_sides_purely_additive_work`, so it
would exempt precisely the case the guard exists for. That is not an argument left in prose:
`test_the_result_equals_the_ref_predicate_would_have_exempted_the_deletion_this_guard_exists_for`
builds a merge where the result blob **is** byte-identical to the ref's and a name of this side's is
still dropped, asserts the identity so the fixture cannot quietly stop demonstrating it, and asserts
the refusal stands.

`--no-renames` on both diffs, because git's default rename detection reports only the new path, so a
file this side renamed would read as untouched at its old one. No merge-base (unrelated histories)
means no exemption.

## R15 — both legs of the partition are driven, and the poison round came first

* `test_a_merge_over_a_path_this_side_never_touched_lands` — **poison round first**: told nothing
  about the merge, the guard still refuses that tree (`["m.py"]`), so the green below is the ref
  being threaded and not an empty subject. Told the ref: no losses.
* `test_a_merge_over_a_path_this_side_edited_is_still_refused` — both histories changed the file;
  the exemption must not reach it, and does not.
* The merge trees come from `surgical_land.build_merge_tree` on a real git repo, not a hand-built
  result tree. The question is what git's own merge produces; a hand-built tree would be a fake more
  permissive than its subject.
* Wiring is asserted against `searchable()` source, not text, at both ends: `merge_ref=merge_parent`
  reaches `violations()`, and the adopted set is **printed** by the landing. An exemption nobody can
  see is a hole — the print is the merge counterpart of the `--drops` line, and says whose the
  deletion is.

29 tests in `tests/tools/test_stale_copy_refusal.py`, 112 across it and `test_surgical_land.py`,
green. **That count is 29 and not the 26 this document first claimed**, and the difference is the
next section: the copy this was written against was behind origin by three tests and two functions.

## The refusal text was false of every landing it refused, and is now branched

The old text diagnosed *"a pathspec stages the WORKING-TREE copy"* and sent the lane to
`isolate_hunks` + `--content`. On a merge **both sentences are false**: `--merge` opens no
working-tree copy, and it refuses `--content` outright. A refusal whose stated remedy the tool
refuses is pressure toward bypass. `refusal_text(losses, merge_ref=...)` now names `--resolve` for a
conflicted path, rebasing your hunks onto the merge for a silent one, and `--drops` only for a
deletion that is genuinely yours — with the misattribution warned about in the text itself.

## The fix above was correct and still shipped the defect, because another lane moved the remedy

**Written after the landing, beside the claim it qualifies.** This document was drafted against a
working copy that was behind `origin/main`, and the landing is where that showed. Origin had
meanwhile moved the remedy OUT of the refusal prologue and INTO a per-path `Loss.remedy()`, with
`door_verdicts` and `gains_over` deciding which door each path is sent to — good work, and the
reason the prologue no longer names `--content` at all.

**Each change is right alone and together they were broken.** The merge branch above renders each
`Loss`, and `remedy()` names `--content` for holder work and `refresh_to_head` for a rival copy.
Both read a working-tree copy; `--merge` has none and refuses both. So the merge refusal — the one
written *specifically* to stop naming a door the merge door refuses — went on naming one, through a
route that did not exist when it was written. The section above was true of the prologue and false
of the printed refusal.

`Loss.render(merge=)` now drops the per-path line on a merge, where the remedy is a property of the
merge and not of the path, and the merge text states it once. The test was re-keyed from *"the
prologue contains `--content`"* — which had quietly become a property of where the string lived — to
the property itself, and now drives **both** remedy shapes, because holder work and a rival copy
name different doors and testing one left the other free to leak. Removing the suppression and
removing the threading each turn it red; both were run before landing.

**The general shape, which is the part worth keeping.** A control's prose and a control's mechanism
were changed by two lanes in the same week, neither wrong, and the composition reintroduced the
exact defect one of them was built to remove. Nothing in either lane could have seen it: this is the
interconnection question the seat exists to ask, and it was found only because the landing forced a
three-way merge onto origin's copy rather than a pathspec commit of a stale one. A pathspec land
here would have deleted `door_verdicts` and `gains_over` outright and never surfaced it.

## Still open

* **The `--drops` census.** `22df46614` carries a declared drop that belongs to `d3e0e408b`. Nothing
  says how often that has happened, and any census of who deleted what reads the wrong lane wherever
  it did. This fix stops it recurring; it does not repair the record.
* Not attempted here: the pre-commit `--staged` door has no merge ref and did not need one — a plain
  `git merge` is not a legal landing on this tree, so its only merge subject would be one that
  already bypassed the door this fix is in.
