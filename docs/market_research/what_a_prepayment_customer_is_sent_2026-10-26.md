**Knowledge:** payments-and-direct-debit

# What a prepayment customer is sent, and what it is not

*Seat, 26 Oct 2026. K8 page for the delivery item `a-prepayment-account-is-billed-as-prepayment`,
written before the billing change it supports. It closes the question in
`docs/staging/SEAT_FINDING_A_PREPAYMENT_HOUSEHOLD_IS_SENT_ESTIMATED_CREDIT_BILLS_2026-10-26.md`.*

## What the rules require

1. **A prepayment meter is paid before use.** The customer buys credit (a vend: key, card, token or
   smart top-up), and the meter takes payment from that credit as energy is used. No bill asks for
   payment afterwards. This is already the world's rule (`simulation/arrears_engine.py`,
   `PREPAYMENT_METHOD`: "its 'bill' is a statement of vends, not a demand that can go unpaid").
2. **The twice-yearly bill duty does not apply.** SLC 21B.5 requires "a Bill or statement of account
   to each of its Customers at least twice yearly", and excludes prepayment, smart and unmetered
   supply. Source: `docs/domain_artefact_library/regulatory/slc_21b_21ba_reads_and_back_billing.md`
   (S1, the consolidated licence).
3. **The 21B.4 read duty does not apply to electricity prepayment** (21B.3, same file). UNC TPD
   M5.9.14 still applies the annual gas read to prepayment meters
   (`docs/market_research/unbilled_energy_and_revenue_assurance.md`, K2). That is a duty to obtain a
   *settlement* read, not to bill on one.
4. **The annual statement does apply.** SLC 31A.9 requires every domestic customer to be sent an
   annual statement in the prescribed template, showing the tariff, the year's spend and the saving
   from the supplier's cheapest tariff. Ofgem: communication with prepayment customers "is mainly
   through the annual statement because these customers do not receive energy bills in the same way
   as standard credit and direct debit customers" (Utilita derogation decision, 1 June 2016,
   https://www.ofgem.gov.uk/system/files/docs/2016/06/decision_utilita_derogation_application_01_june_2016.pdf).
   Ofgem investigated SSE under SLC 31A and 25C over annual statements sent to prepayment customers,
   which closed with a £1m redress payment
   (https://www.ofgem.gov.uk/publications-and-updates/investigation-sse-and-its-compliance-its-obligations-under-gas-and-electricity-supply-licences-standard-licence-conditions-31a-and-25c).
5. **Debt on a prepayment meter is recovered at the meter.** A share of each vend goes to the debt,
   set by ability to pay (SLC 27.8). 41% of electricity and 38% of gas repayment plans run through a
   prepayment meter (`docs/market_research/company_debt_management.md` s.3). It is not shown as a
   balance "to pay" on a bill.
6. **The back-billing limit reaches prepayment.** SLC 21BA.1 counts recovery "including via a
   Prepayment Meter". It bites where the meter under-charged (a wrong rate loaded, a fault), and is
   then recovered on the meter, not by a catch-up bill.

## What follows for a period's document

A prepayment household's period is charged on what the meter recorded as used. There is no
estimated read to bill on, so no estimate, no estimated run and no catch-up at the next read. What
it is sent is a statement of what the meter charged, not a bill with a due date. Whether a
settlement read reached the supplier is a separate matter, and it stays in the read log and the read
duty register.

## What is unknown

- **GAP: how often a prepayment customer is sent a statement other than the annual one.** Nothing
  found requires a monthly or quarterly statement, and 21B.5 exempts prepayment. Smart prepayment
  customers commonly see their balance and vends in an app; how many suppliers post a periodic
  statement is not published.
- **GAP: what a statement of vends must contain.** Only the annual statement's content is
  prescribed (31A Schedule 4). The fields of a vend history are practice, not rule.
- **GAP: the licence text of SLC 31A.** Read here through Ofgem decisions that quote it, not from the
  consolidated licence. The gas licence was not read.
- **GAP: legacy prepayment meter reads.** A key or token meter's register is read at inspection or
  on a visit; how often a legacy prepayment meter's read reaches settlement is not published.

## Choices the design makes, and why

1. **The basis is named, not inferred.** A prepayment period carries `billing_basis` =
   `prepayment_meter` (`saas.bill_generator.CHARGED_AT_THE_METER`) and `document` =
   `prepayment_statement`. A third basis rather than `actual`, because no read was taken for the
   charge; the meter charged it.
2. **The channel is the one the company already holds.** `build_monthly_bills` is handed each leg's
   payment channel (`payment_channel_feed`). On the 4ae8da9b0f book it said prepayment for 163 of
   the 164 legs the world's payments recorded as prepayment, and every one of those legs paid by
   prepayment for its whole life, so the per-leg channel is enough. A leg that moves to prepayment
   mid-life (W2_42's offer at the collections step) would need a dated channel; none does today.
3. **The settlement read is kept.** The bill carries `settlement_read_status` and the unread run,
   so the read duty register still records a prepayment leg's unread year (marked outside the duty
   on electricity) and gas prepayment is still instructed under M5.9.14.
4. **The ledger prints read type `M`**, "charged at the prepayment meter", where it printed `E`.
5. **Not built:** a vend record per top-up, the annual statement document, debt loaded on the meter.
   The world records no vends (`PREPAYMENT_METHOD`'s own named gap), so there is nothing to print.
