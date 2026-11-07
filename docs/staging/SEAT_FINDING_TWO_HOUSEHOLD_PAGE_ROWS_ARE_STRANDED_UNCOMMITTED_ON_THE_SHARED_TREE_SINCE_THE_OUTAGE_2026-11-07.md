**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Two household-page rows have been stranded, uncommitted, on the shared tree since the outage began (2026-11-07)

**What is there.** At 03:07 GMT on Thu 5 Nov, 23 minutes before the host went down, a lane left
these on the shared tree, uncommitted. Nothing of it is on origin.
- In `tools/domain_invariant_runner.py`: the evaluators `ev_page_tariff_label` and
  `ev_page_missed_bill_unsettled`, the cast payment-tally reader in `load_printed`, and
  `ev_dd_collections_equal_to_the_bill`.
- In `docs/design/DOMAIN_INVARIANTS.yaml`: 97 lines of rows after line 4184.
- `tests/tools/test_a_household_page_prints_the_billed_term_and_counts_only_unsettled_bills_missed.py`
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
