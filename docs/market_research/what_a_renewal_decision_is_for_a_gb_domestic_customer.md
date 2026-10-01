# What is a renewal decision for a GB domestic energy customer?

**Knowledge:** acquisition-and-retention-economics

**Research completed 2026-10-01, delivery seat, Lane 0.** Opened by
`docs/staging/SEAT_FINDING_THE_WORLD_DECIDES_A_RENEWAL_AT_ONE_ANNIVERSARY_IN_FIVE_SO_A_PER_RENEWAL_HAZARD_HAS_NO_AGREED_DENOMINATOR_2026-10-01.md`.
That finding found three readings of EP1's tenure hazard: 0.36 per world decision, 0.09 per
anniversary, and about 0.17 for all-cause annual exit. It asked whether a customer on the default
tariff faces an annual decision at all.

## Answer: the published record settles it, so no NTFY was sent.

**A fixed-term end is a real decision point. The default tariff has none.** A customer who rolls
onto the default tariff is on an evergreen contract. It has no end date and no exit fee, and the
customer may leave on any day. The record gives them no anniversary. Their prompts come from price
changes and from a switching prompt that must arrive at least once in every 12 months. **So a
tenure ends at any time, and the hazard a tenure horizon needs is all-cause exit per unit of
exposure.** It is not a rate per anniversary, and it is not a rate per world decision.

## Source

Ofgem, *Gas Supply Standard Licence Conditions, consolidated to 1 April 2024*:
https://www.ofgem.gov.uk/sites/default/files/2024-07/Gas_Supply_Standard_Consolidated_Licence_Conditions.pdf
(fetched and text-extracted 2026-10-01). The electricity supply licence carries the same
conditions under the same numbers. Ofgem's note on the PDF says the consolidation "should not be
relied on" as the formal register. Paragraph numbers are from this copy.

| What | Where | What it says |
|---|---|---|
| Evergreen contract | SLC 1 definitions | "a Domestic Supply Contract … for a period of an indefinite length and which does not contain a fixed term period" |
| Fixed-term contract | SLC 1 definitions | a contract "with a fixed term period that applies to any of the terms and conditions" |
| No silent extension | 22C.2, 22C.5 | A fixed term may not be extended unless the customer gets a Statement of Renewal Terms and **expressly agrees in Writing**. A domestic fixed tariff cannot auto-renew onto another fix. |
| What doing nothing means | 22C.7, 22C.8 | A customer who does not switch or agree a new contract by the term end becomes subject to the **Relevant Cheapest Evergreen Tariff**, or a Relevant Fixed Term Default Tariff. |
| Notice before the term end | 22C.3 → 31I.1(c), 31I.2 | The end of a fixed term is a Relevant Contract Change. Notice must come "at an appropriate time … designed to prompt" an informed choice. The old fixed 42–49-day notice rule became this principle in Ofgem's 2018 customer-communications decision. |
| Free exit at the term end | 24.8(b), 24.17 | The customer may switch "at any time during or after the Switching Window without having to pay a Termination Fee". The window opens when the Statement of Renewal Terms is given, **or 49 days before the term end, whichever is earlier**. |
| Leave evergreen any day | 24.6, 24.7 | The customer may give notice "at any time", and the notice period is "no longer than 28 days". |
| No exit fee on evergreen | 24.3(a), 24.3(b) | A Termination Fee may not be charged on a contract "of an indefinite length", or during the indefinite-length part of a contract. |
| Prompts on evergreen | 31F.5(b)(ii), 31F.5(c) | Switching Information goes on every Relevant Contract Change Notice, which covers each price increase, and "on at least one occasion in any 12 month period". The date is not fixed, and nothing ties it to the acquisition anniversary. |

From 2019 onward the default tariff's price moves with the Ofgem cap period. That was six-monthly
at first and quarterly from October 2023 (`docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`).
Each cap increase is a contract-change notice that carries switching information. **An evergreen
customer's prompts follow the cap calendar, not their anniversary.**

`docs/market_research/company_customer_comms.md` already gave the 42–49-day notice. It labelled
the conditions SLC 22A/22B, which is the wrong numbering. This note supersedes those rows.

## The world's renewal roll, checked against this record

Read on 2026-10-01 at HEAD `d81a86712` in `simulation/renewals.build_renewal_schedule`,
`simulation/run_phase2b.py` (lines ~2323 and ~2097) and `simulation/customer_events.roll_lifecycle_event`:

1. **The first term is never decided.** A renewal is rolled only at `term_index >= 1`. The record
   agrees, because a 12-month fix has no decision before its end, except a mid-term switch with an
   exit fee.
2. **At each later fixed-term end**, `rolls_active_renewal` draws active or passive. The probability
   is the household's engagement archetype, anchored to a population rate of about 35%. Inside the
   FTC withdrawal window (2022-01-01 to 2023-06-30) the draw is always passive.
   - **Active:** a new fixed term is struck and `roll_lifecycle_event` rolls churn or renew. **These
     are the 106 world decisions behind the 0.36.** The population is selected: they are the
     households that shop.
   - **Passive:** the household becomes an SVT stint until its next anniversary. No renewal roll
     fires at the term end. The only exit route is the C1b inertia hazard, rolled per cap segment.
3. **A household on SVT** draws active or passive again at its next anniversary. That anniversary is
   a modelling choice, documented at `renewals.py` ("the HOUSEHOLD's own next look at the market").

**Where it agrees with the record.** The default tariff has no renewal decision, and its exit
hazard is a standing one keyed to cap segments. That matches 24.3(a) and 31F.5(b)(ii). The 0.09 per
anniversary counts each anniversary of an SVT household as a decision the household survived. The
record says those were not decision points at all, so that denominator is wrong by definition.

**Where it does not agree, and this is a world-fidelity question, not EP1's.**

- **The passive term end.** Every fixed-term end is a decision point in law. The customer is served
  a Statement of Renewal Terms and gets a Switching Window of at least 49 days with no exit fee.
  The world gives the 65% who roll passive no departure roll at that point. It starts them on the
  standing inertia hazard instead, which has no spike at the term end. The one published
  route-conditioned number is Ofgem's 2019 trial, with 6% external switching within six weeks of a
  term end on an inert incumbent book (`first_renewal_departure_rate_small_gb_supplier.md`). That is
  above zero on the least mobile book there is.
- **The anniversary for an evergreen customer.** The record has none. The 12-monthly prompt
  (31F.5(c)) is the nearest thing to one, and the supplier picks its date.

Both are filed for the world lane as
`docs/staging/WORKER_FINDING_THE_WORLD_ROLLS_NO_DEPARTURE_AT_A_PASSIVE_FIXED_TERM_END_THOUGH_THE_LICENCE_MAKES_IT_A_DECISION_POINT_2026-10-01.md`.
They change the world's churn, so they are a baseline decision taken blind to company results, and
they are not changed here.

## The reading EP1's H2 needs

**All-cause exit per account-year of exposure, by tenure year.** It already holds that reading.
`company/analytics/clv_three_horizon.BookExitRecord` (landed `627f05756`, then by tenure year in
`7e2503507`) values H2 on every cessation over settled exposure, and `BookRenewalRecord` is
published as a diagnostic that H2 never reads. The control is
`tests/company/analytics/test_clv_book_renewal_hazard.py::test_the_renewal_record_is_published_and_never_valued_on`,
alongside `::test_the_production_view_values_h2_on_the_books_own_exits`.

This note supplies the definition that choice was missing:

- **Per world decision (0.36)** is the rate among households that chose to shop. A supplier cannot
  see that population, and it leaves out every exit from the default tariff.
- **Per anniversary (0.09)** counts non-events as decisions. For an evergreen customer the
  anniversary is not a decision point in law.
- **All-cause per exposure** is the only one of the three whose denominator is the same thing as a
  tenure: time on supply. A switch at the term end, a switch from the default tariff and a home
  move each end it.

The tenure-year life table also carries the one real calendar feature. The fixed-term end is a
decision point, so year-1 exits cluster at the first anniversary for customers on a fix. That
clustering is in the table's year-1 hazard and is not imposed on it.

## What is still open

- How large the departure spike is at a passive term end for a **small** supplier's switched-in
  book. It is still `None` (`FIRST_RENEWAL_DEPARTURE_PRIOR`), for the reasons in
  `first_renewal_departure_rate_small_gb_supplier.md`.
- How much evergreen customers leave per cap-change notice compared with between notices. No
  published series separates the two.
