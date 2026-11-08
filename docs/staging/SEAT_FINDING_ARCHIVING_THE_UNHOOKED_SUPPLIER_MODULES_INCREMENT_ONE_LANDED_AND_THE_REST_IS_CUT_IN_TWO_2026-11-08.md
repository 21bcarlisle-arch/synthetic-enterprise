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

## Increment 2 (built 8 Nov, later the same day): 131 modules, 153 tests

Re-derived at draw time rather than taken from the count above. The rule is the one increment 1
used, run to a fixed point over `capability_index.build_rows()`, with one tightening: a test's
quoted dotted name (`"company.x.y"` in a monkeypatch target or an importlib call) counts as an
import. That is why the set is 131/153 and not the 148/175 filed above. The 17-module gap is the
tests that patch live code by string. Those need increment 3's surgery.

- The store check ran over the set before anything moved. `uig_allocation_register` (EP10) and the
  two C32 keeps stay out. `test_carbon_ledger.py` and `test_credit_balance_control.py` are NOT in
  the set under the rule, so their atom credits stand without a ruling.
  `test_no_committed_store_claims_an_unlanded_falsifier` and its markdown half both pass after
  the move. The stores that name archived module paths name them as subjects, not as falsifiers.
- Controls changed. The wall-clock ratchet loses five entries, and its census floor goes from
  `>= 20` to `>= 10`, because 16 reads remain and the floor only asks that the census sees a tree.
  The year-keyed census loses 9 entries (5 published-unpinned and 4 not-published), and its ratchet
  goes from 28 to 23. `test_carbon_not_a_target` stops naming two surfaces.
  `test_the_live_register_rules_on_every_live_orphan` goes from `> 200` to `> 0`, because the
  archive drives that register toward zero and an empty register is already refused.
- `--dispositions` now reads 92 orphans and 92 ruled.
- Left alone on purpose: `size_ratchet_baseline.json` and `conditional_registration_survey.json`
  (stale rows refuse nothing; increment 1 left them too), `consolidation_ledger.jsonl` (a ledger),
  and `site/data/*` (generated). Prose in the stores, `concepts.yaml`, `DOMAIN_INVARIANTS.yaml`
  blindfold notes and a few live-module docstrings still names archived paths as history.

**Seen on the way, not caused here:** `tests/tools/test_internal_seam_verifier.py::test_current_tree_passes`
is red on a clean `origin/main` (b16a733403). `company/billing/monthly_bill_assembly.py:87` imports
`company.pricing.tou_desk.meter_is_economy_7` across domains, with no seam and no baseline entry.
It has been there since 32ddfa8ca2 (30 Oct). It needs a seam export or a documented baseline row,
and that belongs to the billing lane.

## Increment 3 (what is left): 89 modules

crm 25, market 18 (uig held), finance 10, billing 9 (including C32's ppm_warrant_register),
regulatory 9 (including C32's consumer_vulnerability_register), trading 5, then compliance,
pricing, risk, sustainability, carbon and portal. Each one is held by a test file that also
touches live code, by import or by quoted name. Each of those files needs a judgement.

## Increment 3a (built 8 Nov): 39 modules, 41 whole tests, and the archived legs of 32 coverage files

The 89 split in two. One half is held only by the `test_phase_*_coverage_expansion` and
`*_coverage_depth` family. Those files are concatenated sections, one class per module, so they
split cleanly by section. The other half is held by tests that exercise live code in the same
function, such as `test_control_mutation`, the portal suite, the one-calendar deadline test and
the carbon controls. Those need a judgement per file, and they are increment 3b.

- **The set.** The same fixed point as increment 2, over the same census (an import or a quoted
  dotted name in `tests/`), but the coverage family is allowed as a *surgery* referrer. It gives
  39 modules: crm 15, market 8, finance 7, regulatory 4, billing 2, trading 2, risk 1. Of the
  family, 2 files reach only the set and move whole. 32 are split.
- **The split.** The split is mechanical. A top-level section that names a set module, or uses a
  name imported from one, moves with the helpers it calls. In a class that reaches both sides,
  the methods that reach the set move, along with the `self.` helpers they call. Four files did
  this with imports inside methods: `ja`, `iz`, `jb` and `jc`. Each archived copy sits at the
  file's own path under `archive/unhooked_supplier/`, with a header saying the live legs stay
  where they were. Three checks ran on every file:
  - the live text names no set module;
  - test functions are conserved (live plus archived equals the original);
  - no moved unit reaches live code, so no live leg left with the archive.

  All 32 passed all three. The split moved 559 test functions and kept 432.
- **Kept out on purpose:** `uig_allocation_register` (EP10's store), C32's
  `ppm_warrant_register` and `consumer_vulnerability_register`, and the two atom-credited test
  subjects, `carbon_ledger` and `credit_balance_control`. `hedging_schedule` is held too.
  B4's store cites `tests/company/market/test_hedging_schedule.py` in its 29 Jul DISCOVER entry,
  and `test_no_committed_store_claims_an_unlanded_falsifier` refuses that citation once the file
  moves. The citation is evidence, not a falsifier, so it belongs in `_STALE_CITATION`. That
  register asks for the sha of the commit that retired the file, and no commit can name its own
  sha. 3b has to pick one of two routes:
  - let the register accept the `archive/MANIFEST.txt` row as the retirement record; or
  - add a marked correction to the B4 entry that gives the file's archive path.
- **Registers.** 39 rows leave the disposition register and 39 leave `orphan_baseline`.
  `--dispositions` reads 53 orphans with 53 ruled. The wall-clock ratchet drops
  `contract_exposure_register`. One wall-census member is paid down:
  `enterprise_value_gbp -> company/finance/board_dashboard.py`.
- **Lint.** On the 32 split files, ruff findings fell from 161 to 60, and no file's I001 or E402
  count rose.

- **Two gates met on the way.** The first was the pre-commit test gate. It passed every
  *added* staged test file to pytest by name, and naming a file skips
  `archive/conftest.py`. Increments 1 and 2 passed only because renames never reached the
  selector (`--diff-filter=ACM`). This increment's added leg files failed collection, so the
  gate's `tests_for` now selects nothing under `archive/`, and a mutation-checked test holds
  that. The second was the scope-evidence gate. It refused `capacity_to_pay.py` because closed
  atom C33 lists it in `file_scope`, so that entry now points at the archive path.
  `customer_retention.py` sits in the same row and will meet the same gate in 3b.

## Increment 3b (what is left): 53 orphans

Three of the 53 stay: `uig_allocation_register` and C32's two keeps. `hedging_schedule` waits on
the route above. `carbon_ledger` and `credit_balance_control` need their atom credits read before
they move. The rest are held by 81 test files that reach live code or a held module, and that
count includes the live legs of the 3a split. Most of those files exercise live code beside an
orphan, so they cannot be cut by section. Re-derive the census at draw time. The tool that made the
3a split, an AST splitter with the three checks above, is worth adapting. It will not cover the
cases where one test function exercises both an orphan and live code. Those need a decision for
each function.
