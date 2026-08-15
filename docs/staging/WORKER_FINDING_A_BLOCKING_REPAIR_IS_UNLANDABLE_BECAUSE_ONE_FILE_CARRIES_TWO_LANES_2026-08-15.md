# WORKER FINDING (QUEUED) — a BLOCKING repair is unlandable alone because one file carries two lanes, and the entanglement is invisible to every check that looks at the file

**Severity:** LATENT · **Lane:** D_billing_metering · **Disposition:** QUEUED (not fixed on sight)

**Found by:** the 2026-08-15 worker tick, attempting to land the read-seam repair that closes
`WORKER_FINDING_THE_MATCHING_BILLS_CONTROL_MEASURES_CARDINALITY_AND_THREE_PUBLISHED_ROWS_DISAGREE_2026-08-15.md`
(BLOCKING, this lane, live at rung 1c). The repair is written, coherent and GREEN — 542 passed,
1 xfailed across `tests/simulation/test_run_phase4c_on_phase2b.py` + `tests/company/compliance/`
at the working tree, run this tick. It still cannot be committed by its own author.

## Observed, with evidence

`python3 -m tools.surgical_land` REFUSED the six-path repair on the resulting tree:

> `simulation/run_phase4c_on_phase2b.py:456`: `simulation.policy_costs.coverage_report` does not
> exist in this tree — the consumer landed and the supplier did not

`git show HEAD:simulation/policy_costs.py | grep -c coverage_report` → **0**. The symbol is
defined only in the working tree, in a 142-line pure addition belonging to a DIFFERENT lane's
work (`WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW_2026-08-14.md`,
the silent-clamp finding). That lane's consumer call already sits in
`run_phase4c_on_phase2b.py` — the one file the read-seam repair must also change.

So one working-tree file carries two lanes' uncommitted changes, and neither lane can land
without the other's supplier. The read-seam lane's pathspec is correct and complete for its own
change; it is defeated by a hunk it did not write and does not own.

## Why this is not just "run the symbol check earlier"

`tools/symbol_landing_check` caught it, correctly and fail-closed — that part worked. The gap is
that **nothing warns a lane that a file in its `file_scope` is already carrying someone else's
in-flight hunks** until the commit is refused. Every cheap check a lane runs first looks right:

* `git status` says the file is modified — which it expects, it modified it.
* `git diff <file>` shows both lanes' hunks with nothing distinguishing them by author.
* the lane's own tests pass, because the working tree has BOTH suppliers.

The failure is only visible at the moment of landing, after the expensive gate.

## The sibling defect this tick also hit, same root, different surface

`git diff docs/design/maturity_map.yaml` showed **one** hunk (mine). The map actually differed
from HEAD at **two** atoms: another lane had STAGED a `simplifications_count` bump for
`D3_catchup_rebilling` while leaving its record unstaged. `git diff` compares the working tree to
the INDEX, so an index-and-worktree-agreeing half-move is invisible to it — only
`git show HEAD:<file>` reveals it. The first landing attempt was refused red on exactly that, and
the diagnosis cost a full gate cycle.

**Both are the same shape:** a lane inspects a shared file with a command whose baseline is not
HEAD, concludes the file carries only its own work, and finds out otherwise from the gate.

## Options, and the recommendation

1. **A pre-landing scope check** — given a pathspec, report for each path whether the
   working-tree diff *against HEAD* contains hunks outside the caller's declared `file_scope`,
   and whether any symbol those paths call is absent from HEAD. Cheap (no gate, no tests), and it
   turns two post-gate refusals into one pre-flight line. The symbol half already exists as
   `tools/symbol_landing_check --at-tree/--since-tree`; what is missing is running it *before*
   the expensive gate and pairing it with the against-HEAD hunk report.
2. **Serialise the shared file** — declare `simulation/run_phase4c_on_phase2b.py` single-writer
   the way `H9_map_write_serialisation` does for the map. Heavier, and it trades a diagnosable
   refusal for a queue.

**Recommendation: 1, and not 2.** The refusal is CORRECT and must stay — the defect is that it
arrives after the gate rather than before it, and that the lane cannot see the entanglement with
any command it would naturally run. 2 would slow every lane to fix a diagnosis problem. Not built
here: this is a harness change outside the drawn work, and SELF-INTERRUPT DISCIPLINE says queue it.

## Not established, flagged rather than asserted (R9)

* Whether the policy-costs lane is *blocked* or merely *unlanded* is **not checked** — this tick
  did not run its tests and makes no claim about its readiness. What is observed is only that its
  supplier is absent from HEAD while its consumer call is present in the working tree.
* Whether landing the two lanes together would be green is **not established**. It was not
  attempted: adopting a third lane's 142-line addition, without its record, is the record/code
  inversion this same tick spent two commits repairing.

## What this tick did land, for the record

`2a9ea1c76` (the D28 caveat repair), `fdcbd91f7` (its record, the map counts, and the DISCHARGED
archive of the caveat finding). The read-seam repair is **not** landed and its blocking finding
stays live and correctly drawing at rung 1c. Its record — D3 note 8, landed in `fdcbd91f7` —
therefore currently describes code that is not in HEAD. That inversion was forced (the map's D3
count was already staged, so no commit naming the map could be coherent without the record) and
is stated here rather than left for the next tick to rediscover.
