**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · found grading `the-held-estimate-fix-is-graded-against-its-pre-registration`

# Two runs at one commit draw different books from February 2016

The director's EP17 ruling holds the population draw fixed "so a change in results means a change
in code". This finding says that premise did not hold on the one test of it we have.

**Arms.** A is the published `run_output_2248e3baf_20261013T134447Z.json` (founder-ruling book).
B is `2248e3baf` plus one hunk (650fdcdd7's `company/billing/monthly_bill_assembly.py`), run by
`background.launch_long_job` as unit `longjob-heldgrade-2248e3baf`. The run went through
`simulation.run_phase4c_on_phase2b.main()` in the scratch worktree `/var/tmp/se-heldgrade-2248e3baf`
and was saved as `run_output_2248e3baf_20261015T114732Z.json` (not committed).

**Measured.**
- The world digests are identical in both runs: `cdba75ebb9197b33`, demand `7d6195c5eb1562ab`.
- Bills: 39,084 in A, 38,431 in B. Customer ids: 171 only in A, 160 only in B.
- The first difference is at acquisition, on **2016-02-13**: PROS-2016-0042 signs only in B, and
  PROS-2016-0054 and -0059 sign only in A. Differing bills by year run from 198 in 2016 to 2,236 in
  2024.
- The hunk can only act once an estimate is held. The first held estimate is 2017-12, 22 months
  after the books part. So **the hunk cannot be the cause**: nothing it touches exists in February
  2016.

**I cannot yet say** which of these causes it. Candidates, ranked by evidence:
- (a) The publisher's process environment differs from a `launch_long_job` unit's. The draw reads
  `SE_DRAW_POPULATION`, `SE_GROW_BOOK`, `SE_SEED` and `SE_SERVED_SEGMENTS`, and an explicit env
  value overrides the curriculum. Neither run records these flags in its output.
- (b) An untracked input the campaign reads. The scratch worktree regenerated
  `docs/observability/book_growth_campaign.json` and `book_subset_verdict.json` as untracked files.
- (c) Nondeterminism inside the run, such as set ordering or a time-seeded draw.

**Prediction, written before the run:** a placebo run of B's recipe *without* the hunk will match B's
book (same 160/171 id split), which points at (a) or (b). If it matches neither A nor B, the cause
is (c).

**One-variable next step.** Run the placebo: the same unit and the same `run.py`, at a clean
`2248e3baf`. Then compare its customer-id set with A and with B. It costs about 108 minutes.

**Why BLOCKING.** The instrument in question, "re-run at a commit and difference against the
published run", cannot hold the book fixed. It already made one pre-registration ungradeable
(`SEAT_PREREG_A_HELD_ESTIMATE_IS_KNOWN_AT_ASSEMBLY_2026-10-15.md`, P1 and five P2 rows). Every
one-variable grade under EP17 relies on it. A two-arm comparison where both arms are fresh runs from
one process recipe is unaffected, so this blocks only gradings against a *published* arm.
