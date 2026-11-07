**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Two household-page rows have been stranded, uncommitted, on the shared tree since the outage began (2026-11-07)

**What is there.** At 03:07 GMT on Thu 5 Nov, 23 minutes before the host went down, a lane left
these on the shared tree, uncommitted. Nothing of it is on origin.
- In `tools/domain_invariant_runner.py`: the evaluators `ev_page_tariff_label` and
  `ev_page_missed_bill_unsettled`, the cast payment-tally reader in `load_printed`, and
  `ev_dd_collections_equal_to_the_bill`.
- In `docs/design/DOMAIN_INVARIANTS.yaml`: 97 lines of rows after line 4184.
- the test file test_a_household_page_prints_the_billed_term_and_counts_only_unsettled_bills_missed.py under tests/tools
  (untracked).

**What landed from it.** Only the DD evaluator, with its Leg A test, as
`tests/tools/test_a_level_direct_debit_row_grades_leg_a.py`, in the commit that carries this file.
- f874c6836 had landed `INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE` without
  its evaluator. That left `test_every_id_in_the_committed_file_has_a_disposition` red on origin,
  and the red refused every commit whose test selection reaches the runner.
- The code landed is the stranded bytes, unchanged.

**What is still stranded.** `INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM` (N16 on the page) and
`INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED` (N15 on the page): their rows, evaluators and tests.

**Landing them now:**
1. Drop `ev_dd_collections_equal_to_the_bill`, `_wilson` and the DD test from the stranded copies.
   They are on origin.
2. Land the rest with `isolate_hunks --survey` and `surgical_land --content`.

**Reverse:** delete this file.

## It now pins the shared tree, so no book can carry origin's last ten commits (seat, 2026-11-07 19:30 UTC)

- The shared tree last fast-forwarded at 16:21 UTC, to fa915ac0d7. Since 18:21 reconcile-watch has
  refused every pass: "10 behind, 0 ahead ... Refused by 16 path(s)". The stranded copies here are among them:
  `tools/domain_invariant_runner.py` (166 lines from HEAD, 210 from origin), `docs/design/DOMAIN_INVARIANTS.yaml`
  and `tests/tools/test_the_domain_invariant_runner_reads_only_the_raw_export_and_every_evaluator_can_fire.py`.
  Their bytes match no commit, and their mtimes are all 5 Nov 03:07.
- The other differing paths are a stale copy (`docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md`
  holds 6ed871310c's blob, mtime 1 Oct), the stretch log being written live, and the deleted b3ce2a4e73 finding.
  Eight more of the sixteen already equal origin's bytes.
- sim-runner builds from the shared HEAD. The run that started at 18:40 is at fa915ac0d7, and so will be the
  next one unless the tree moves. 8b6316995 (the BSCP504 ceiling) is not in either. So
  `docs/staging/records/WORKER_PREREG_THE_BSCP504_CEILING_ON_THE_NEXT_FRESH_BOOK_2026-11-07.md` cannot be graded, and
  INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL's exception cannot retire, until this finding's landing step is done.
  The same holds for every other grade waiting on origin code after fa915ac0d7.
- Landing the stranded rows does not on its own clear the refusal. The reconciler clears a path only when its bytes
  equal origin's. After landing, the shared copies must be refreshed to origin, and that is a shared-tree action.
  An isolated worktree seat cannot take it.

## Done (delivery seat, 2026-11-07)

Landed on origin's base: both rows, `ev_page_tariff_label`, `ev_page_missed_bill_unsettled`,
`_unsettled_by`, the cast tally reader in `load_printed`, and the test file without its DD leg. The DD
row's stranded `reading:` (its first grade) landed with them. Both rows are named in the runner's
disposition list. The shared tree's stranded copies are now superseded by origin and can be refreshed.
