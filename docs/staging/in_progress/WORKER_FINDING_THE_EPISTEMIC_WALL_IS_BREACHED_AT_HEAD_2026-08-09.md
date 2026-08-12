> **PARKED IN `in_progress/` 2026-08-09 by the unwedge tick — one sub-item genuinely open.**
>
> **DONE:** item 1. KNIFE1's cut landed at `7cef2c1d4`; KNIFE2's — the sixteen
> `simulation.* -> saas.customers` edges plus `company/interfaces/supply_book.py` — landed in the
> commit that carries this note. The wall is intact at HEAD, measured on a clean checkout:
> `tests/architecture` 40 passed, `test_no_new_sim_reads_company` green.
>
> **STILL OPEN — the blocking sub-item:** items 2 and 3. The level-promotion gate still accepts
> evidence gathered against the WORKING TREE (`record_level_up_self_certified`), and the atoms
> certified on 2026-08-09 (KNIFE1, KNIFE2, and anything else promoted while its code was
> uncommitted) have not been re-audited against HEAD. **What unblocks it:** re-running each atom's
> own exit measurement inside a `git archive HEAD` checkout and refusing the record if it
> disagrees — the finding's own item 2, which is now cheap because
> `background/process_run_complete.py::_head_checkout` already materialises exactly that checkout
> and makes it a real repo.
>
> Item 4 (do not re-freeze the E402 baseline) was honoured: the baseline was never touched.

# [WORKER-FINDING] The epistemic wall is BREACHED at HEAD, and every measurement that said otherwise was taken against the working tree (2026-08-09)

**Found:** immediately after `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09` moved the publish
gate's subject to a clean checkout of HEAD. This is the ruling's first real yield, and it is worth
more than the outage it was meant to prevent.

**Severity:** the epistemic wall is a **WALL** under Rule 0 — never crossed, no exceptions. The
machine currently believes it is intact. It is not intact in the only place that ships.

## Observed, with evidence

```
$ git show HEAD:saas/reporting/annual_report.py | grep -n '^from simulation'
41:from simulation.run_phase4c_on_phase2b import main as run_phase4c_on_phase2b

$ grep -n '^from simulation' saas/reporting/annual_report.py      # working tree
(nothing)
```

The class-(a) crossing — the business layer reaching into the simulated world's run harness, the
*strictly forbidden* direction — is **present at HEAD** and absent only in an uncommitted
working-tree edit.

Run the gate's own argv against a clean HEAD checkout and the wall control says so plainly:

```
FAILED tests/tools/test_target_design_delta.py::test_the_epistemic_wall_is_currently_intact
```

The same test passes in the working tree. **Wall intact in the tree, breached at HEAD.**

## Why nobody knew

`KNIFE1_reporting_cycle` was self-certified to L2 this morning. Its ledger provenance reads:

> *"All three EXIT clauses measured, not asserted. (1) LEGACY_COMPANY_READS_SIM is now
> frozenset() -- class (a), the strictly-forbidden saas->simulation direction, is at ZERO."*

That measurement was true — **of the working tree**. It was taken with the fix present but
uncommitted, and the wall walker, the ratchets and the gate all read the same tree, so every
control agreed with every other control and all of them were describing something that does not
exist in any commit.

The `E402` ruff baseline is the fingerprint this left behind. KNIFE1 lowered it 194 → 193 on the
strength of deleting that import. At HEAD, `saas/reporting/annual_report.py` still carries 18
E402s, not 17 — so the baseline has been calibrated against uncommitted work ever since, which is
exactly what `WORKER_FINDING_RUFF_BASELINE_IS_CALIBRATED_TO_UNCOMMITTED_WORK_2026-08-09` named
without yet knowing why.

## The class, now with three instances in one day

| Pass | Certified | What is actually in HEAD |
|---|---|---|
| KNIFE1 | L2, "class (a) at ZERO" | the class-(a) import, still there; `tools/run_annual_report.py` was untracked until 83a55b750 |
| KNIFE2 | L2, "16 edges gone" | 19 files in no commit, incl. the new `company/interfaces/supply_book.py` |
| PW2 | (my commit's fault) | `episode_monotonic` imported by committed code, module uncommitted — fixed in ebc2356c8 |

The common shape: **a lane measures the tree, certifies the atom, and exits without committing.**
Every control downstream then measures the same tree and confirms the certification. The map, the
ledger and the ratchets all agree — and all of them are reading a state that no fresh checkout can
reproduce. R16 required the level move to leave an auditable record; it did. The record is
auditable and it is wrong, because what it audited was not committed.

## Why this is not fixable by tightening the ledger

The ledger is honest about what it measured. The defect is that "measured" meant "measured in a
tree that also contains work nobody has committed". Any control that reads the working tree
inherits this, which is why the ruling's change of SUBJECT is the actual fix and a stricter
self-certification form would not have been.

## What closing it looks like

1. **KNIFE1 commits its own pass** — the `annual_report.py` cut is sitting in the tree. Until it
   lands, HEAD ships a wall breach and the E402 baseline is fiction. This is the smallest, most
   urgent item on the list.
2. **The level-promotion gate should measure HEAD, not the tree.** `record_level_up_self_certified`
   currently accepts evidence gathered anywhere. An EXIT clause proven against uncommitted work is
   not proven. The cheapest form: re-run the atom's own exit measurement inside a
   `git archive HEAD` checkout before recording, and refuse the record if it disagrees.
3. **Re-audit the atoms certified today** against HEAD rather than the tree — KNIFE1, KNIFE2, and
   anything else promoted while its code was uncommitted.
4. Do **not** re-freeze the E402 baseline to 194 to go green. I tried it, and reverted it: it makes
   HEAD pass while making the working tree red (the ratchet is subject-relative, so it now measures
   whichever tree it runs in), and it would bank a wall breach as an accepted floor. The number is
   a symptom; the import is the defect.

## Related

* `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09.md` — the change of subject that exposed this.
* `WORKER_FINDING_KNIFE2_IS_ORPHANED_19_FILES_IN_NO_COMMIT_2026-08-09.md` — the sibling instance.
* `WORKER_FINDING_RUFF_BASELINE_IS_CALIBRATED_TO_UNCOMMITTED_WORK_2026-08-09.md` — the fingerprint.
* `WORKER_FINDING_A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED_2026-08-09.md` — the class, filed
  earlier the same day without the wall consequence attached.

— Worker finding, 2026-08-09. No KNIFE file was touched.
