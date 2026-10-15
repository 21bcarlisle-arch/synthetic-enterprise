**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · found grading `the-held-estimate-fix-is-graded-against-its-pre-registration`

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

## Placebo, 2026-10-15 (delivery seat, claim `the-book-drift-placebo-run-at-2248e3baf`)

**A cheaper first leg than the 108-minute run.** The book is assembled at import by
`simulation.live_population.live_population()` (founders + trickle + campaign winners, a function
of seed, code and curriculum files). Reading it in-process at a clean `2248e3baf` worktree
(`/var/tmp/se-placebo-2248e3baf`, no hunk, no `SE_*` env) costs seconds and separates
(a)/(b) from (c) as well as the full run would for the *acquisition* layer, which is where the
books first part.

**Prediction, written before the probe:** the in-process id set equals B's 978 ids exactly and
misses A's 171. If it equals neither, the draw itself is nondeterministic (c). If it equals A, the
divergence is born inside the run after assembly, not in the draw.

**Result: the prediction held, and the cause is none of (a), (b) or (c).** The in-process book at clean
`2248e3baf` holds all 143 of B's PROS-only ids and none of A's 139. Two draws gave byte-identical id
lists, so the draw is deterministic. Setting `SE_DRAW_POPULATION` and `SE_GROW_BOOK` to 0 or 1 gives
797, 425, 797 and 397 ids. None of those is A's set. Arms and ids are in `/var/tmp/se-placebo-out/`.

**(d) A's stamp names HEAD, but A's code was the shared tree's disk.** I drew the book in-process at
every origin commit from 2026-10-11 to 2026-10-14 that touches the draw path. The book flips at
exactly one commit:

| Commit | PROS ids | A's 139 drawn | B's 143 drawn |
|---|---|---|---|
| `5cdaca020` and every earlier commit | 400 | 0 | 143 (= B) |
| **`81c129fe8`** ("The capital target is £115, not the £130 consultation figure") and every later commit through `e3b5ed01a` | 395 | **139 (= A)** | 0 |

`81c129fe8` is **not** an ancestor of `2248e3baf`. But `2248e3baf`'s own message is "the shared
tree now holds origin's 81c129fe8 bytes". At 14:44 BST that day the shared tree had HEAD at
`2248e3baf` and a working copy holding `81c129fe8`'s `saas/growth_mandate.py` and
`simulation/net_new_acquisition.py`. The capital target moves the campaign's quote budget, and
that changes who signs on 2016-02-13. The publisher stamped `git rev-parse HEAD` "at process start".
That is true of HEAD and false of the code that drew the figures.

**So EP17's premise holds: a commit fixes the book.** What failed is the instrument that names the
commit. A run published from a shared tree whose disk is ahead of its HEAD carries a stamp for code
it did not run. Re-running at the stamp then differences two commits, not one. **Severity drops to
LATENT for the EP17 rule** and stays a live defect for the stamp. Remedy, not built here: stamp
the content, e.g. refuse or mark the stamp when `git diff --quiet HEAD -- '*.py'` fails at process
start. Handed on as a continuation.

## Re-grading the held-estimate fix on a base that draws A's book (pre-registered before launch)

Two fresh arms from one recipe (`launch_long_job`, the same `run.py` as B). Both run in locked
worktrees at a real commit whose code draws A's book:
- **X0** = `81c129fe8`, clean.
- **X1** = `81c129fe8` plus `650fdcdd7`'s `company/billing/monthly_bill_assembly.py` hunk. That file is
  identical at `2248e3baf`, `81c129fe8` and `650fdcdd7^`.

**Predictions:**
- **Q0 (placebo against A).** X0's bill keys equal A's 39,084. Every bill is equal in
  `total_amount_gbp`. If some differ, the residual is other uncommitted bytes in A's shared tree
  (`2248e3baf` names `simulation/run_phase2b.py` as another lane's staged work). In that case the
  fix is graded X0 against X1 only, never against A.
- **P1.** X1 − X0 = **+£20,335.71 ±£0.11**, all of it on 11 catch-up bills. No other bill changes.
- **P2.** All five PROS-2017-0336 rows (2017, 2018, 2019, 2020, 2023) clear, with the deltas in the
  pre-registration's table. 2023 is the narrowest, at +£177.71 for a £122 clearance.
- **P4.** No catch-up bill is newly held.
