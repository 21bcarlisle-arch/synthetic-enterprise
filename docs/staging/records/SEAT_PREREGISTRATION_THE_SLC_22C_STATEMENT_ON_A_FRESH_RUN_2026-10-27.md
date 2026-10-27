# Pre-registration: the SLC 22C statement, wired, on a 2016-17 window and a fresh full run (2026-10-27)

**Item:** `the-renewal-notice-is-sent-42-to-49-days-before-a-fixed-term-ends`, point 1 of
`docs/staging/SEAT_FINDING_THE_COMPANYS_OWN_EVENTS_SHOW_NO_RENEWAL_NOTICE_TWO_PAYMENT_RECORDS_AND_A_CREDITED_PART_MONTH_2026-10-27.md`.
**Text read first:** `docs/domain_artefact_library/regulatory/slc_22c_end_of_fixed_term_statement.md`;
design and GAPs on `docs/market_research/tariffs_and_the_default_tariff_2026-10-25.md`, section
"The end-of-fixed-term statement".

Written before either run returned. What I had already seen: the 2eeb3f0b3 grade (1,338 of 1,338
fixed terms breaching; 163 offers at 0 days, 2 at -9, 1,173 with no act), and that a full run takes
about 56 minutes (`/var/tmp/fresh-run-2eeb3f0b3.log`, 3,351 s).

## What changed, so what can move

1. The run sends a statement for each domestic fixed term supplied on day 42 before its contracted
   end, dated that day (`company/crm/renewal_notice_register.end_of_fixed_term_statement`, through
   `company/interfaces/renewal_offer.send_end_of_term_statement`). It is recorded only: nothing in
   the run reads `renewal_notice_log`.
2. The term row carries `fixed_term_end`; the ledger and the export carry it and the statements.
3. The evaluator grades the statement where a book carries it, and the offer only on a book that
   predates it. It now skips non-domestic accounts (22C binds Domestic Customers) and terms whose
   supply stopped before day 42 (owed none).

## Predictions

- **P1 (window, 2016-17):** `renewal_notice_log` is non-empty, every row's notice is exactly 42 days
  before its `fixed_term_end`, and no row is dated on or after the day its term's supply stopped.
- **P2 (full run, the row):** `INV_RENEWAL_NOTICE_42_TO_49_DAYS` grades **0 breaches**. Checked: fewer
  than 1,338, because non-domestic terms and terms cut before day 42 drop out; I expect
  1,000-1,400 (the book has moved since 2eeb3f0b3 for other reasons, so the base is not identical).
- **P3 (full run, everything else):** no other invariant row's breach count moves *because of this
  change*: the statement is record-only. I cannot test this one-variable, as origin has moved since
  2eeb3f0b3 and no run at this HEAD without the change exists. A row that moves is reported, not
  attributed.
- **P4 (if P2 fails):** the likeliest cause is a term the run and the export see with different ends
  (a follower's term restored after the row was written, or a riding gas leg cut by a departure),
  each to be named, not excepted wholesale.

## What this does not answer

- Whether any household reacts to a statement. No world code reads it (GAP, named on the page).
- Whether a retention offer on the day a fix ends is a defect. The text dates the statement, not an
  offer of a new contract (22C.8(c)); a practitioner question, filed beside the finding.
