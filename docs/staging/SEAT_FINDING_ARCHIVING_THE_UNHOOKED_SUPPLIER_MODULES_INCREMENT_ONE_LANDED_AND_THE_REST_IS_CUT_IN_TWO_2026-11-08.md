**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# Archiving the unhooked supplier modules: increment 1 landed in 745a5fd27 (42 of 263); what is left and how it is cut (2026-11-08)

The hand-off `archive-the-unhooked-supplier-modules`, from section 6 of the 24 Oct own-code-review
finding (`4e3a978bf5`). This file is the progress record, so the next draw does not have to
re-derive it.

## Re-measured on 8 Nov

- `tools/capability_index.py --dispositions` read **265** company-side orphans against 268 ruled.
  Three rows were STALE because their modules have been wired since: `crm.customer_registry`,
  `crm.renewal_notice_register` and `market.transfer_objection_register`. Their rows are deleted;
  the modules stay live.
- That leaves 263 to archive: 265 less the two kept for C32.
- 83 test files import an archived module AND live company/saas code. Moving one of those whole
  would drop live coverage; leaving it would break its import. These files are why the work comes
  in increments.

## Done means

1. Every one of the 263 is under `archive/unhooked_supplier/`, at its original path, with its
   tests. For a shared test file, the archived part leaves and the live part stays.
2. `--dispositions` reads 0 unhooked, and its register holds only the rows that are not archive
   rows.
3. The orphan `--dispositions` check has its weekly caller. This is still owed (section 3 of the
   finding: 22 s on every commit is the wrong price).

## Increment 1 (landed, 745a5fd27): 42 `company.market` modules, 52 tests

The rule: move a module only if every test touching it is safe to move. A test is safe when all
its other company/saas imports are archived in the same increment, or when the file is named for
the archived module and its live import is a helper. Infrastructure that landed with it:
`archive/` README, MANIFEST and conftest; the ruff exclude with force-exclude; the archive entry
in `capability_index.EXCLUDED_ROOTS`; and exemptions in two architecture tests, each with its
reason.

`company.market.uig_allocation_register` met the rule and was held back.
`docs/design/simplifications/EP10_adapter_uk_link_xoserve.yaml` credits its test as a BUILT
falsifier, and `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py` refuses
a store whose falsifier is in no tree. Archiving it first needs a ruling on that store row: EP10
keeps it and wires it, or the note is corrected. **The next increment runs the same store check
over its own set before moving anything.**

## Increment 2 (next): 148 modules, 175 tests, all packages, by the same rule

The set is the rule above, iterated to a fixed point over the live index. Re-derive it at draw time and do not trust this count.
They are named in many places that load-bear:

- `docs/design/canon_claims.yaml` and `DOMAIN_INVARIANTS.yaml` (two rows each)
- `tests/company/test_carbon_not_a_target.py` (13) and `test_carbon_cannot_reach_the_sim.py`
- `tests/architecture/test_a_company_run_never_reads_the_wall_clock.py`
- the year-keyed census (12 entries; its ratchet comes down again)
- the one-calendar deadline test
- `tests/tools/test_wall_channel_census.py`, `test_internal_seam_verifier.py`,
  `test_canon_drift_check.py` and `test_blind_review.py`
- the `size_ratchet_baseline` and `orphan_baseline` rows

Expect one gate cycle for each control.

Two test paths in the set are credited by atom records, so the same hold may apply to them:
`tests/company/test_carbon_ledger.py`, which `maturity_map.yaml` cites, and
`tests/company/billing/test_credit_balance_control.py`, which the W2_16 store cites.

## Increment 3: the remaining 72, which need surgery to shared test files

These are the 83 mixed test files: the `test_phase_h*/i*/j*_coverage_expansion` family, 18 portal
tests built on `company.portal.app`, `test_control_mutation.py`, and others. Each one gets a
judgement: archive the file, or cut out the archived legs.

## Landing note

The primary checkout refuses a landing while it is behind origin. Build each increment in
`git worktree add --detach <dir> origin/main`, then run `surgical_land` and
`promote_worktree_landing`. The year-keyed census ratchet edit needs `--drops` on that file: the
stale-copy guard reads a ratchet coming down as a revert of the commit that last set it.
