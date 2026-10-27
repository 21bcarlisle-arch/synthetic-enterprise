**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 2 · **Atom:** `unminted`

# The eight cold-read rows: six cannot be graded on the raw export, and the occupier window's EBSS credit is sized by the debt

Found while giving the eight rows of 501ef4fcc evaluators (item `the-eight-cold-read-rows-get-evaluators`).
The grade and the cause of every breach are in
`docs/staging/records/SEAT_PREREGISTRATION_THE_EIGHT_COLD_READ_ROWS_ON_THE_2EEB3F0B3_BOOK_2026-10-27.md`.
This file holds only what the item did not close.

1. **Six rows need fields the raw export does not carry**, and each now names them in
   `missing_export_fields`: region and tariff name (one SVT price per region), renewal-notice dates,
   due dates and a dated balance, collections events, and write-offs with their reason. A row the
   suite cannot check is a class it cannot catch. Each wants a decision on whether the field crosses
   into the raw export (as a contracted fact or an event, never a computed amount) or whether the
   class is checked somewhere else.
2. **INV_ESTIMATE_RUN_WITHIN_TENURE holds by construction** on a one-fuel-per-account export. The
   defect behind O14 and O28 is the page's estimate-run counter adding both fuels together. That
   check belongs on the generated customer page, not in the raw-export suite.
3. **The EBSS row's predicate is looser than the guidance.** "On supply on any day of month m" also
   counts a joiner's first part-month. EBSS guidance 5.4 gives that month's credit to whoever held
   the account at 00:00 on the 1st. A proposal for the row's author: replace "supply on any day of
   month m" with "account held at 00:00 on the 1st of m". This file does not edit the row.
4. **The occupier window's EBSS credit is sized by the debt, not the instalment.** After the export
   fix, all 12 residual breaches on the 2eeb3f0b3 ledger are on five `OCC-` accounts. Their credit
   comes from `run_phase2b`'s occupier path (`occupier_scheme_credit`, `_occupier_credit_left`),
   which caps it at the occupier's debt and dates it by the settlement record. Four of the 12 are
   first part-months, which point 3 covers. The other eight are a world defect, and a world change
   needs a new run to show it. Excepted with a ceiling of 12 until then.
5. **IDNO-connected homes:** real MPAN cores carry distributor IDs from 24 upward
   (`docs/domain_artefact_library/regulatory/mpan_core_structure_and_check_digit.md`), and
   INV_MPAN_CORE_FORMAT's 10-23 would breach on them. No book draws one yet.
6. **The world has no region.** `customer_registry.mpan_core` now gives every account a distributor
   from a hash, the scheme the customer pages already used. That is an identifier and not a place,
   so no regional fact may be read from it.
