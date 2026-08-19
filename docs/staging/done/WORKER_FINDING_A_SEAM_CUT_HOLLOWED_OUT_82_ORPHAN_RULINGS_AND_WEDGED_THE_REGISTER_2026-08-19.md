# WORKER FINDING — a seam cut hollowed out 82 of 258 orphan rulings, and the register has been unlandable ever since

**Severity:** BLOCKING · **Lane:** H_harness
**Date:** 2026-08-19
**Raised by:** the worker tick landing `EP1_clv_three_horizon` pass 9, whose rename needed one
row of `docs/design/ORPHAN_DISPOSITION_REGISTER.md`. `surgical_land` REFUSED on the tree the
commit would create. The red was not the rename's.
**Class:** a ruling outliving the fact it rules on. Sibling of
`feedback_a_no_route_control_red_lists_the_retirements_that_were_deliberate` and of KNIFE's
adopted-residue findings — but this one is a WEDGE, which is why it is filed BLOCKING.
**Discharged:** `tests/tools/test_capability_index.py::test_a_package_losing_its_last_consumer_fires_and_a_render_repairs_it`,
`tests/tools/test_capability_index.py::test_a_package_gaining_its_first_consumer_fires`,
`tests/tools/test_capability_index.py::test_a_seam_cut_that_swaps_one_consumer_for_another_is_deliberately_quiet`,
`tests/tools/test_capability_index.py::test_the_renderer_never_rules_on_a_new_orphan`,
`tests/tools/test_capability_index.py::test_the_renderer_never_retires_a_ruling_whose_subject_left`,
`tools/capability_index.py`, `docs/design/ORPHAN_DISPOSITION_REGISTER.md` — the consumer column
is derived and re-rendered by one command, so a seam cut can no longer hollow out rulings that
only a fresh judgement per row could repair.
**Status:** REPAIRED 2026-08-19 in commit 04839e94b, by option 3 below (the recommendation on
record). The register is landable again — proven by that commit, which touched it and passed the
gate — and its own test went from 87 disposition findings to 0. What the repair gives up is
recorded in section 5 of the register rather than glossed. Cause was CONFIRMED by measurement
against two trees before anything was changed.

Every claim is `observed-with-evidence` unless labelled `inferred` (R9).

---

## The wedge

`docs/design/ORPHAN_DISPOSITION_REGISTER.md` is the only path that selects
`tests/tools/test_capability_index.py` at the pre-commit gate — measured, not guessed, by calling
the selector directly:

```
tools.pre_commit_test_gate.select_targets(['docs/design/ORPHAN_DISPOSITION_REGISTER.md'])
    -> tests/tools/test_capability_index.py
```

That test is **RED at HEAD**. Not red because of any uncommitted work: a detached worktree at
`b98722cb2` with nothing else in it reports **83 findings**, and
`test_the_live_register_rules_on_every_live_orphan` asserts that list is empty.

So the register is unlandable. Any commit that touches one row of it is refused, and a
`--no-verify` route out is a WALL. The row `EP1` needed — renaming
`company.core.three_horizon_clv` to `company.core.commitment_actual_forecast` after that module
was renamed — could not land with the rename it describes.

## What the 83 are

Counted at HEAD, and the shape is one thing 82 times:

| finding | count |
|---|---|
| DECORATIVE REFERENT — nominates `simulation.run_phase2b`, which imports nothing from that package | 82 |
| STALE DISPOSITION — `company.market.tpi_commission_book` is now WIRED, not an orphan | 1 |

The 82 break down by the package the row is about: `company.crm` 52, `company.trading` 20,
`company.risk` 10. Every one of them nominates the same consumer. 258 rulings are declared in
total, so **just under a third of the register is decoration**.

The single non-decorative finding is the happy case the register also failed to follow: someone
wired `tpi_commission_book`, and its row still rules on it as an orphan.

## Why they went hollow, measured on both sides

`simulation/run_phase2b.py` is the nominated consumer in all 82. Its imports FROM the company
side, at the two trees:

```
6156b8b97 (2026-08-10, the last commit at which this control reports 0 findings)
    company.crm 10 · company.trading 3 · company.regulatory 3 · company.pricing 3
    company.risk 2 · company.market 2 · company.interfaces 2 · company.policy 1
    company.finance 1 · company.analytics 1          -- ten packages

b98722cb2 (HEAD, 707 commits later)
    company.interfaces 16                            -- one package
```

Every direct crossing moved behind `company/interfaces/`. That is the seam working exactly as
designed and is not a defect. What it did as a side effect is empty out every ruling whose
justification was *"`run_phase2b` is the consumer that would drive this"* — because after the cut,
`run_phase2b` touches `company.crm`, `company.risk` and `company.trading` **nowhere**. The rulings
did not change; the world underneath them did.

**INFERRED, not asserted:** that the KNIFE3 crossing work is the specific agent of this. The
import census above is measured; attributing it to KNIFE3 rests on `git log` for that file naming
KNIFE3 steps 28, 29 and 38 as the recent commits, which is evidence and not proof, and nothing in
this document depends on the attribution being right. No claim is made that any KNIFE step was
wrong to make the cut — **the cut was correct and the register was simply not carried with it.**

## Why BLOCKING and not LATENT

Named explicitly because the default must be argued, not assumed:

* An instrument in this area states 82 rulings that are false of the tree. A reader taking the
  register at its word would believe 82 orphan modules have a nominated consumer waiting for
  them; not one of those consumers touches their package.
* It is a WEDGE, and it is 707 commits old. A shared design surface no commit can modify is not a
  defect that waits — every future orphan disposition, including correct ones, is blocked behind
  it, and the wedge is invisible until someone needs the file.
* It is self-concealing in the way that matters: the control fires only when someone edits the
  register, so the longer nobody rules on an orphan, the longer nothing reports that ruling is
  impossible.

Nothing published moves — no board figure, dashboard value or gap reading derives from the
register. That is why this is a wedge finding and not a figures finding.

## The stranded edit, named so it is recorded rather than orphaned

`docs/design/ORPHAN_DISPOSITION_REGISTER.md` line 198 currently carries an UNCOMMITTED one-line
edit in the working tree, renaming `company.core.three_horizon_clv` to
`company.core.commitment_actual_forecast` to follow the module rename that landed this tick. It is
correct and it is stranded by this wedge, not by anybody's oversight. It is named here, with its
file and line, precisely so that it is a recorded owed change and not the uncommitted-work class:
**the commit that repairs this wedge should carry it.** It was NOT reverted, because reverting a
correct edit to tidy a working tree destroys work to buy an appearance.

## The repair, named and not taken

Not taken because this is a B_commercial draw and the register is H_harness's, and because
choosing what 82 rulings should now say is a judgement about the seam, not a text substitution
(SELF-INTERRUPT DISCIPLINE).

The population is **every row whose referent is a module that has since been cut off from the
package it names**, not the 82 currently caught, and the instance fix — re-pointing 82 rows at
`company.interfaces.*` — is the one thing that should NOT be done on its own: it would restate the
same nomination one seam further out and go hollow again at the next cut, which is R10's whole
point. Three candidates, and the third is the recommendation:

1. Re-point the 82 referents at whatever imports the package today. Rejected above: it re-arms the
   same decay.
2. Re-rule the 82 as genuinely unconsumed. Honest, and probably true of many of them, but it
   asserts a disposition for 82 modules on no evidence beyond one broken nomination.
3. **Make the referent DERIVED rather than declared.** The register already computes
   `_package_consumers(rows)` to check the nomination; a column the checker can compute is a
   column the register should not be hand-authoring. Rule on the DISPOSITION (the judgement — keep,
   retire, wire) and let the consumer column be rendered. A hand-written referent can go stale
   silently; a rendered one cannot, and a seam cut then shows up as a changed render instead of as
   a wedge discovered 707 commits later by someone renaming an unrelated file.

Whichever is chosen, the `tpi_commission_book` row should be dropped in the same pass: a module
that got WIRED is the outcome the register exists to produce, and a ruling that outlives its own
success is the same shape as the 82.
