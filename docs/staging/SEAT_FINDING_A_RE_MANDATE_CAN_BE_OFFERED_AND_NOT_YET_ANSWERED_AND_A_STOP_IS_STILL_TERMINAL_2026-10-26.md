**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure`
**Knowledge:** `payments-and-direct-debit` -- `docs/market_research/payments_and_direct_debit_2026-10-25.md`, "Off direct debit and back on"

# The desk can invite an account back onto DD and the world cannot yet answer, so every stop in the run is still terminal

Found taking PB8 to L2 (seat, 26 Oct).

**What was already true.** The map row said L2 was owed because `arrears_engine` and
`get_payment_method` still read a payment channel fixed for life. Both had already moved on 3 Oct:
`dd7bbce0f` was the money side and `065ac54eb` the seam, through `StopNoticeBoard`. The row was never
updated, so the atom was offered twice for work that had landed.

**What this landing adds.**
- ADDACS 1 now reaches the desk. A DD4b or own-reasons cancellation used to stop the household's bills
  going on the rails, but the desk never heard of it. The register showed the mandate as active, and
  neither `supplier_dd_stops` nor the seam's board saw it. Now the desk reads ADDACS 1 on the working
  day after the "instruction cancelled" return and cancels the mandate from that date. So the household
  route reaches the money side and the seam by the same path as the supplier's stop. Both toggles ship
  at 0, so no number moves in the shipped world.
- The desk has a re-mandate policy: invite after `REMANDATE_OFFER_AFTER_PAID_BILLS` (3, a named
  simplification) on-time on-receipt bills, and wait again after a decline. Tests cover a cancelled
  mandate, an invitation, a signed re-mandate and a decline.

**What stays open (LATENT).**
1. `bacs_rails.REMANDATE_ACCEPTANCE_PROBABILITY` is None: no take-up rate is published. So the run
   puts no invitation to a household, and the desk's policy is unreachable in a run. That still asserts
   zero re-mandates, the overstatement of manual payers that `gb_payment_method_migration_rates.md`
   already carries. It is now a GAP in one constant rather than a missing mechanism.
2. When a rate is supplied, `supplier_dd_stops`, `paying_method` and `StopNoticeBoard` must become
   spell lists. Today they hold one terminal stop per customer, and `_run_rails` would also need the
   desk's on-receipt ledger, which it skips today because a non-DD bill is never on the rails. **Do
   not set the rate without this.** Otherwise a re-mandated household would keep paying on receipt in
   the money side while the register shows it back on DD.
