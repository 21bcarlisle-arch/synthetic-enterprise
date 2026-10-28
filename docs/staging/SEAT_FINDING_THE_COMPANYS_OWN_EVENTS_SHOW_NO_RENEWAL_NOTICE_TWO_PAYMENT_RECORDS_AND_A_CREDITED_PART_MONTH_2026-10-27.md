**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 2 · **Atom:** `unminted`

# The company's own events show no renewal notice, two payment records, and a credited part-month

This came from giving four of the six ungradeable cold-read rows evaluators on the company's dated
acts (item `the-six-cold-read-rows-read-the-companys-own-events`). The grade and the cause behind
every count are in
`docs/staging/records/SEAT_PREREGISTRATION_THE_SIX_COLD_READ_ROWS_ON_THE_2EEB3F0B3_BOOK_2026-10-27.md`.
Each defect is excepted, capped at its count, in `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`.

1. **No end-of-fixed-term notice is ever sent.** `company/crm/renewal_notice_register.py` implements
   SLC 22C's 42-49 day window, and nothing in the run calls it. The company's only dated renewal
   act is the retention offer, made on the day the term ends. On the 2eeb3f0b3 book, all 1,338 of
   1,338 fixed terms breach: 163 offers at 0 days, and 1,173 terms with no act at all. This is the
   class behind O6. The fix is to wire the register into the run, so every fixed term gets a dated
   notice 42-49 days before it ends, and to have the offer precede or accompany that notice.
   **Wired 2026-10-27** (item `the-renewal-notice-is-sent-42-to-49-days-before-a-fixed-term-ends`):
   the run sends the SLC 22C statement on day 42 to each domestic fixed term supplied that day, and
   the export carries it. Text first: `docs/domain_artefact_library/regulatory/slc_22c_end_of_fixed_term_statement.md`.
   On the 2016-17 window, 569 statements, every one at exactly 42 days, none on an unsupplied day.
   **A fresh full run grades the row 0 of 1,170** (the 2eeb3f0b3 book, same evaluator: 1,323 of
   1,323); the 1,338 exception is retired. Grade:
   `docs/staging/records/SEAT_PREREGISTRATION_THE_SLC_22C_STATEMENT_ON_A_FRESH_RUN_2026-10-27.md`.
   **Not done, on purpose:** the offer was NOT moved. On reading the text, 22C dates the statement
   and an offer to extend the same contract (22C.5, inside the statement), and does not date a new
   fixed contract's offer (22C.8(c)). Moving the offer means deciding 42 days earlier, a commercial
   change for its own page. **GAP:** no household in the world reads or reacts to the statement.
2. **The collections desk and the billing ledger keep two payment records.** On 1,987 of 7,151
   occasions (27.8%), a journey opens on "a bill is unpaid past its due date" where the billing
   ledger shows every bill due by then collected. SYN-2016-356 opens on the 29th each month, while
   its bills fall due on the 14th to the 19th. Which record is wrong is not established. The
   prediction is that the desk reads the DD collection book's schedule. The statute bar's 24
   early write-offs look like the same split: a final bill paid after the account closed restarts
   the six years in the billing ledger, but not, apparently, on the desk.
   **Cause established 2026-10-27, and fixed** (item
   `the-collections-desk-and-the-billing-ledger-keep-one-payment-record`). The payment outcome was
   the same in both records. The due date was not. The run posted each month's bill to the
   company's own ledger, which the desk walks, as due on the 28th of the month being billed,
   before that month had ended. The billing ledger dates it period end + generation delay + 14,
   and the engine dated it period end + 14. The desk's record was the wrong one. All 7,151
   journeys opened on a 29th or a 1st. All 25 early statute-bar write-offs fall six years after the
   desk's earlier date for the same payment, so they are the same split. The two never-chased
   failed DDs from O27 (OCC-3c914ee8cef5g, OCC-561d240ea21a) are NOT. They fall in occupier-window
   months, where the ledger draws its own outcome for a bill nobody else bills. Now
   `arrears_engine.bill_due_date` is the one home, and all three read it. The test
   `tests/simulation/test_a_collections_journey_opens_on_the_bill_the_ledger_made_due.py` finds
   482 stray openings on the old code and none on the new. Traces, predictions and the fresh-run
   grade:
   `docs/staging/records/SEAT_PREREGISTRATION_ONE_DUE_DATE_FOR_THE_DESK_AND_THE_LEDGER_ON_A_FRESH_RUN_2026-10-27.md`.
   **Graded 2026-10-28 on a fresh full run at 1691ec0ecd, and closed.** Overdue-within-balance is
   now 4 of 7,380, down from 1,987, and statute-barred write-off age 3 of 64, down from 25. Both
   exceptions are lowered to those counts, each naming its residual. The 4 are bills the billing
   ledger holds for VAT review (its whole `exception_queue`) and the desk still dunns. The 3 are a
   household's first write-off, dated before a final bill's payment that arrived after the leg
   closed. I predicted 0 for the statute bar, and that was wrong. Journeys rose (7,380 against
   7,151), against my prediction of fewer. Openings now bunch on the 15th to the 17th, the ledger's
   due date plus one, against my bound of 15% for any one day. The two residuals are new, smaller
   defects and are not this split.
3. **A joiner's first part-month is credited the EBSS on the named-household path.** Five PROS
   joiners, each traced, were credited for the month they joined mid-way. Guidance 5.4/5.8 gives
   that month's credit only to whoever held the account at 00:00 on the 1st, and the occupier path
   already credits nothing. That is two homes for one rule. The fix is one EBSS eligibility home.

Not done here: the estimate-run check on the generated customer page (point 2 of the source
finding). It is the next increment of the same item.
