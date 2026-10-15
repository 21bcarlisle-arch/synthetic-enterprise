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
  **Graded 2026-10-15 18:55: Q0 HELD, exactly.** X0 (`run_output_81c129fe8_20261015T151056Z`, 119.9
  min) and A have the same 39,084 bill keys, and **0 bills differ in any field**. The book totals are
  £2,462,538.19 and £2,462,538.19, and the world and demand digests are equal. So A's uncommitted
  `simulation/run_phase2b.py` residual moved no bill. The fix can be graded X1 against X0, and so
  against A.
- **P1.** X1 − X0 = **+£20,335.71 ±£0.11**, all of it on 11 catch-up bills. No other bill changes.
- **P2.** All five PROS-2017-0336 rows (2017, 2018, 2019, 2020, 2023) clear, with the deltas in the
  pre-registration's table. 2023 is the narrowest, at +£177.71 for a £122 clearance.
- **P4.** No catch-up bill is newly held.

## Which published figures ran code their stamp does not name (delivery seat, claim `no-run-or-publish-imports-code-that-is-not-its-stamp`)

**Part (1) was already on origin before this item was drawn.** `c701d8605` (2026-10-14 00:08Z) takes
`background.code_closure.imports_off_commit` at launch: `git diff <stamp>` plus untracked files over
the run's import closure. `run_annual_report` writes it into `producing_commit.imports_off_commit`,
and marks it unmeasured (`paths: None`, with the reason) when no launcher handed it one or the reading
was taken against another commit. `process_run_complete.imports_off_commit_refusal` refuses a publish
on a non-empty list or on `None`. `sim_runner.code_admission` stops a run from starting at all
unless the closure is clean and the stamp is on origin. The control the item asks for, HEAD at X with
a disk copy from Y, is
`tests/background/test_a_run_whose_imported_bytes_are_off_its_commit_is_not_published.py`
(`test_the_reading_names_modified_and_untracked_imports_and_only_those`,
`test_a_dirty_imported_path_is_not_published_under_a_clean_stamp`). The one missing leg is the
**re-run recipe**. A grader that differences a fresh run against a published arm reads nothing that
would refuse a dirty-stamped arm. That leg is built in this landing.

**The twenty-day edit the director named** is the `tools/demand_vector_coverage.py` working copy
(mtime 2026-09-24 15:02 BST). It dropped `seasonal_swing` from `DISTRIBUTION_AXES`. It was named by
`c701d8605`'s finding and landed by `ac3612a6f` (2026-10-14). That commit argues from the code that no
settlement figure moves, because the settlement choice reaches no function that reads the axes.

**Census population.** Every `Auto-process run complete` publish on origin since 2026-09-21: 21
publishes, 21 distinct stamps, and every run file is still on the shared tree's disk. None carries an
`imports_off_commit` reading, because all 21 predate `c701d8605`. So no reading taken at run time can
say what each one imported. A partial witness that can still be read now is the **book draw**.
`simulation.live_population.live_population()` at a clean checkout of the stamp, in-process with no
`SE_*` env, gives the PROS ids that commit's acquisition code signs. A run whose code was its stamp's
bills no PROS id that its stamp does not draw. Calibrated on arm B (clean `2248e3baf`), billed-not-drawn
is 0 and drawn-not-billed is 4, the never-billed signers. On arm A it is 139 and 147.

**What this witness cannot see.** Dirty bytes downstream of acquisition (billing, hedging,
reporting) leave the book unchanged. So a pass says only that the acquisition code agrees with the
stamp. It does not say the run was clean. The `demand_vector_coverage` edit is one of those
invisible ones, and the census names it on the strength of its mtime, not of the witness.

**Prediction, written before the scan.** `run_output_2248e3baf_20261013T134447Z` fails (it is arm A,
already known). Of the other 20, I expect **at least 18 to pass**. Every one of them also ran the
`demand_vector_coverage` edit (all 19 launched after 2026-09-24 14:02Z, all but `87b25d6da`), but the
book cannot see that edit. A failure means a second dirty acquisition edit that nobody has named.

**Result: the prediction held, 20 of 20.** Only the run already known as arm A fails. Scripts and
per-stamp id lists are in `/var/tmp/se-stampcensus/` (`scan.sh`, `scan.log`).

| Publish | Run file | Stamp | Book witness (billed PROS not drawn / drawn not billed) | Dirty imported paths, and the evidence for them |
|---|---|---|---|---|
| `ed3dadd9d` 10-13 | `run_output_2248e3baf_20261013T134447Z` | `2248e3baf` | **139 / 147, FAIL** | `simulation/net_new_acquisition.py` and `saas/growth_mandate.py` at `81c129fe8`'s bytes (witness above). `tools/demand_vector_coverage.py`, the 09-24 edit (mtime). |
| `a88fb2436` 10-05 | `run_output_998814330_20261005T205247Z` | `998814330` | 0 / 0 | `tools/demand_vector_coverage.py` (mtime) |
| `1526f5267` 09-28 | `run_output_16eeaf2cf_20260928T032442Z` | `16eeaf2cf` | 0 / 0 | same |
| `d28b8021e`, `d75148485`, `bfc64212f`, `cbb11d939`, `65d046034`, `7e7b0332e`, `8e2b20ced` (09-27) | `d110149f0`, `496e41f26`, `32c12e1a7`, `65d046034`, `d678f063a`, `2596867f7`, `fe4bde811` | as file | 0 / 0 each | same |
| `2596867f7`, `d1cb3b90f`, `b77978a40`, `8470c4d44`, `704a7318a`, `b22f47610` (09-26) | `d58c6340a`, `4c31d98a2`, `3a1678638`, `1f3720eeb`, `c64ba1b32`, `833d07a01` | as file | 0 / 0 each | same |
| `82d89003c`, `e8a4aab51`, `4bc282c50`, `19e60c443` (09-25) | `e1736649a`, `5903db01e`, `837a94c8a`, `33650edec` | as file | 0 / 0 each | same |
| `60c8c1d4b` 09-21 (control, before the edit) | `run_output_87b25d6da_20260921T152931Z` | `87b25d6da` | 0 / 0 | none known |

**Which figures that touches.**
- **Every figure on the live site today comes from the one failing run.** No run has been published
  since `ed3dadd9d`. That publish wrote 47 `site/data` and `site/state` files and 1,000 customer
  pages. Those include the £543,474 net headline (`company.json`, `dashboard.json`,
  `margin_bridge.json`), the book (`customers.json`, `customer_sample.json`, `book_growth.json`,
  `site/data/customers/*`), `billing_accuracy.json`, `billing_ledger.json`, `value_arms.json` and
  `publish_provenance.json`. Their stamp, `2248e3baf`, does not draw that book. The code that did
  draw it is `2248e3baf` with `81c129fe8`'s two acquisition files. `81c129fe8` is now on origin,
  so the figures are not from code that no history holds. They are from a combination that no
  single commit holds. Whether `81c129fe8` alone reproduces them is Q0 of the X0 run above, which
  is running now. Until Q0 reads, those figures have no commit that reproduces them.
  **Q0 has read (2026-10-15): `81c129fe8` alone reproduces every one of A's 39,084 bills in every
  field, but not the whole run.** A full walk of both outputs finds 115 of 124 top-level sections
  identical. The billing figures, the customers and the P&L sections therefore have a commit that
  reproduces them. Nine sections differ (run identity aside):
  - `trading_book`: hedge P&L £97.16 in A, £71,848.92 in X0; bid-ask cost £10,972.76 vs £12,533.98.
  - `wholesale_credit_exposure`: peak £54,142.77 vs £26,757.92.
  - `margin_call_book`: outstanding £344,691.59 vs £631,742.98.
  - `mc2_collateral_death_test`.
  - `scenario_analysis`: read off disk from `site/state/scenario_analysis_latest.json` by design. Its
    `portfolio_as_of` is 10-13 in A and 10-05 in X0, so this one is the tree, not the run.

  The first four come from `simulation/run_phase2b.py`'s hedge desk. Between `2248e3baf` and
  `81c129fe8`, 14 runtime files differ, among them `company/risk/independent_amount.py`,
  `company/risk/counterparty_collateral_desk.py` and `company/finance/treasury.py`. The two commits
  are on diverged lines (4 commits one way, 19 the other). **I cannot yet say which bytes A carried in
  those files**, so the live site's hedge P&L, credit-exposure and margin-call figures still have no
  commit that reproduces them. This does not touch the held-estimate grade, which reads bills only.
- **The 19 publishes from 09-25 to 10-05** each ran the `demand_vector_coverage` edit under a stamp
  that lacks it. The book witness passes on all 19, so their acquisition code was their stamp's.
  The edit's effect on figures is argued, not measured: `ac3612a6f` reads that the settlement choice
  calls no function that reads `DISTRIBUTION_AXES`. Every one of these figures was superseded by
  `ed3dadd9d`.
- **What the census cannot rule out:** a dirty edit downstream of acquisition in any of the 20 that
  left no mtime anyone recorded. The witness is blind there, and no reading was taken at the time.
  From `c701d8605` on, no run can reach the page without that reading. From this landing on, no run
  can stand as a one-variable arm without it either (`python3 -m background.code_closure --arm <file>`).

**What this commit adds (part 1's missing leg).**
- `background/code_closure.one_variable_arm_refusal` / `load_one_variable_arm`, and a door at
  `--arm`. They refuse an arm whose reading is absent, unmeasured or non-empty. The publisher passes
  an absent reading, but an arm check does not, because the absent case is the 2248e3baf case.
- `tools/run_annual_report.main()` now takes its own reading at process start when no launcher
  handed it one. A grader's arm or a hand run stamps its dirty paths instead of reading as
  unmeasured.
- Control: `tests/tools/test_a_run_whose_bytes_were_not_its_stamp_is_not_a_one_variable_arm.py`.
  It builds today's shape (HEAD at X, a disk copy of a `simulation/` file from Y). It was
  mutation-proven four ways: dirty admitted, absent admitted, loader skips the check, and no
  fallback reading. Each one reds.

**Fate:** the stamp defect is closed by `c701d8605`, `code_admission` and this landing. The live
site's provenance gap resolves when Q0 reads, or at Monday 2026-10-19's publish, which must pass
the reading. The continuation `the-run-stamp-names-the-imported-bytes-not-head` is retired as
subsumed.
