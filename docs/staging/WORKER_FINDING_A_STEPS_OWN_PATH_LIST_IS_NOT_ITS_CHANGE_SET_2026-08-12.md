# FINDING — a step's own declared path list is not its change set, and landing off it gates the wrong tree

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-12 · **Atom:** `KNIFE3_wall_crossing_paydown` · **Class:** record/code divergence
**Status:** instance landed (`048bc10f8`); the CLASS is filed here, not fixed on sight.

## Observed, with evidence

Landing step 20 (the churn-belief cut, caught uncommitted by the 09:29 host poweroff), the
`map_records` path list in `docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`
declared 6 files:

```
company/crm/churn_desk.py
company/interfaces/churn_estimation.py
tests/company/interfaces/test_churn_estimation_seam.py
simulation/renewal_engagement.py
tests/simulation/test_renewal_engagement.py
tests/architecture/test_static_quality_ratchet.py
```

The actual change set was **12 paths**. The list omits `simulation/run_phase2b.py` (the module
the cut is *performed on*), the register section, the yaml record itself, the two F401 repairs —
and, the one that matters, **`tests/architecture/test_epistemic_wall_ratchet.py`**.

That last omission is not cosmetic. The step DELETES three `LEGACY_SIM_READS_COMPANY` tuples,
because the ratchet's own `test_sim_reads_company_allowlist_has_no_stale_entries` reds when an
allowlist entry names an edge that no longer exists. A landing driven off `map_records` alone
therefore produces a tree with the cut applied and the allowlist still naming the cut edges:

```
FAILED test_sim_reads_company_allowlist_has_no_stale_entries
FAILED test_mutation_injected_company_reads_sim_reds_only_new_crossing
FAILED test_mutation_injected_sim_reads_company_reds_only_new_crossing
FAILED test_baseline_census_is_exactly_as_frozen
[test-gate] ❌ TESTS FAILED -- COMMIT REFUSED.
```

Observed, not inferred: that is the real refusal from the first `surgical_land` attempt.

## Why the working tree could not reveal it

`tests/architecture/test_epistemic_wall_ratchet.py` run **on the working tree** was 12 passed,
and the four-file ratchet/wall set was 91 passed. Green, both times, because the working tree
*had* the allowlist edit. The defect exists only in the tree a `map_records`-driven commit
would create — which no working-tree test run can see.

This is the same shape as `WORKER_FINDING_A_FINISHED_CUT_SAT_UNCOMMITTED_WITH_EVERY_CONTROL_GREEN`
(2026-08-12) seen from the other side: there, every control was green and the code was
uncommitted; here, every control is green and the *path list* is short. In both cases the
working tree agrees with itself and the commit is what disagrees.

## What caught it, and what did not

`tools.surgical_land` caught it, by construction — it gates the tree the commit WOULD create.
Nothing else in the loop would have. `tools.pre_commit_test_gate.tests_for` maps subjects to
tests by NAME STEM, so `run_phase2b.py` selects `tests/simulation/test_run_phase2b*` and never
reaches an allowlist held in `tests/architecture/`. The reach-by-reference gap already filed
against that gate is the same root.

## The class

`map_records` is currently a **hand-kept list**, and clause 2 of
`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12` makes exactly this argument about
counting from a hand-kept list rather than the filesystem. A step's declared paths and its real
change set drift silently because nothing compares them: the yaml is written by the same tick
that writes the code, from memory of what it touched.

## Recommended remedy — NOT applied here

A check that reads a landed KNIFE step's commit and asserts `map_records ⊆ the commit's paths`,
reporting the difference. R15 both ways: a step whose record omits a path it committed is named;
a step whose record lists a path it did not touch is named. Filed rather than fixed, per
self-interrupt discipline — the supply of harness findings is infinite and this one is not
blocking.

Do **not** remedy it by widening `surgical_land` to guess paths. The refusal worked. The record
is what was wrong.
