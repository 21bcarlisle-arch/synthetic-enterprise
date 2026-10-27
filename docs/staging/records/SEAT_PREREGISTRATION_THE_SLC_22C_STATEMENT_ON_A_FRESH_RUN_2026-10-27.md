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

## Grade (written after both runs returned)

**Runs.** The 2016-17 window was `run_phase2b.main(report_end="2017-12-31")` at the landing's code.
The full run was `/var/tmp/fresh-run-scripts/arm.py` from a worktree at 66ac2ec58a plus this item's
uncommitted change, which landed unchanged as 50c14a9dc. It took 3,864 s and skipped no keys. It
wrote `/var/tmp/fresh-run-out-slc22c`. Its ledger was built with `build_ledger.py` and graded with
`python3 -m tools.domain_invariant_runner --ledger /var/tmp/slc22c-grade/ledger.json`
(`/var/tmp/slc22c-grade/report.txt`, `result.json`).

- **P1 held.** 569 statements. Every one was exactly 42 days before its `fixed_term_end`, none was
  dated on a day its term was unsupplied, and none was sent twice. One thing was not predicted:
  measured against the term rows, 575 terms looked "owed" and 6 got no statement. Three of those
  are non-domestic (C5, C6). The other three are rows for terms their household never started,
  because it left at the term's start: a term row is written before the departure roll. So the
  run test grades the window, the supplied day and uniqueness against the rows, and leaves
  completeness to the billed book (`tests/simulation/test_the_run_sends_the_slc_22c_statement.py`,
  3 passed).
- **P2 held.** `INV_RENEWAL_NOTICE_42_TO_49_DAYS` is **CLEAN: 0 of 1,170** domestic fixed terms
  owed a statement (predicted 0 of 1,000-1,400). The 1,338 exception is retired.
- **Control (the evaluator is keyed to the property, not to this answer).** The 2eeb3f0b3 ledger,
  graded by the same evaluator, still **breaches 1,323 of 1,323**. 15 non-domestic terms left the
  count, and on a book with no statements the evaluator falls back to the offer.
- **P3, reported and not attributed.** Exactly one other row moved:
  `INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23`, from 12 to 8 of 2,269. ff937d809e (the occupier EBSS
  fix) landed after 2eeb3f0b3 and predicted 12 -> 5-7, so 8 is just outside its range. A statement
  nothing reads cannot reach a credit, but this run cannot separate the two changes. Every other
  row's checked, breached and flagged counts are identical. Publish gate: 0 unexcepted breaches,
  4 excepted.
