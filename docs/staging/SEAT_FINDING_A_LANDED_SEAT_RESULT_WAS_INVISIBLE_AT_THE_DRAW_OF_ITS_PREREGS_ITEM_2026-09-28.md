**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3

# A landed SEAT_RESULT was invisible at the draw of its prereg's item

**What happened.** `grade-the-balance-rule-two-state-diff-against-the-cefd2c04a-baseline` was drawn
at 04:27 on 2026-09-28, but `7dc8f150d` had already landed its graded result at 02:57. The item
named only `SEAT_PREREG_THE_TWO_STATE_DIFF_RERUN_UNDER_THE_BALANCE_AT_CLOSE_RULE_2026-09-27.md`. A
prereg does not change when its grading is done, so neither `premise_note` nor `landed_since_note`
could see that the work was finished.

**What changed.** `background/delivery_lane.result_note` now puts a RESULT CHECK line in the
doorbell whenever an item's `what`/`why` names a `SEAT_PREREG_<stem>_<date>.md` and a
`SEAT_RESULT_<stem>_*.md` exists on origin/main. The result can have any date and sit in any staging
room. The line names the oldest commit that added the result, and gives the exact
`--premise-spent` command to run.

**A departure from the item's wording, and why.** The item asked the draw to *treat* such an item
as premise_spent and not hand it out. I did not build that filter. The counter-example was in the
same store that day: `the-stranded-balance-rule-run-graded-and-the-c1-bracket-run-at-one-commit`
names the same prereg and asks for the grading **and** a three-run C1 bracket, which is the thesis
step. A filter keyed to "the result landed" would have swallowed the bracket. The result spends
only the grading half of an item, and only a reader can tell whether anything else is left. So this
is an annotation carrying the strongest wording the doorbell has, following the module's
annotate-never-withhold rule. The item's "an item whose prereg has no result is still handed out"
control therefore becomes: the partition leg shows the note both firing and staying silent, and a
doorbell leg shows the work is still carried beside the note.

**Control.** `tests/background/test_a_landed_seat_result_is_named_at_the_draw_of_its_preregs_item.py`
runs against a throwaway repo. I ran five mutations and all five fired. Mutation (d), *look only in
`records/`*, first went GREEN. That was a missing test, not an equivalence: the archive leg's first
add was itself in `records/`. The fix is a leg where the result is filed in another room.

**Dispositions.**
- `grade-the-balance-rule-two-state-diff-against-the-cefd2c04a-baseline`: `--premise-spent 7dc8f150d`.
  `disposition_of` now reads `premise_spent`.
- `the-billing-ledger-and-the-pnl-book-one-write-off`: `--landed fcba478b7` refused because the row
  is not claimed. It is also not needed: the row already reads `delivered`, and its `last_landing_at`
  equals fcba478b7's own `%ct` (1790564864), so a bind had already happened.

**Duplicate-work note at the draw.** "Already held under this very id" was the draw's own write. The
`fcba478b7` claim holding `background/delivery_lane.py` is a sha-named claim on the arrears leg, so
it is not this work.
