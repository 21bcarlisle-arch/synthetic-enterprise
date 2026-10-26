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

## Item 2 done, 26 Oct (seat, `pb8-re-mandate-spells`)

The readers now hold spells, so item 1 can be answered without splitting the register from the money
side. `_run_rails` returns each household's spells off DD (`supplier_dd_spells` by period_end,
`supplier_dd_spell_notices` by date). It feeds the desk its on-receipt ledger, drawn as
`_resolve_bills` draws the same bill, and puts the desk's invitation to the household when a rate is
set. `paying_method`, the billing ledger and `StopNoticeBoard` read the spells. A DD4b cancellation is
spent once the household signs again, on the rails and in the engine alike. While the rate is None,
the board still caches a stop as final, because none can end.

Tests: `tests/simulation/test_a_dd_stop_is_a_spell.py`, 8 tests. With the rate at 0.5, the register,
the engine, the ledger and the board agree bill by bill and date by date. There is a partition control:
3 of 6 stopped households come back. A re-mandate moves no payment outcome. Five mutants went red: the
board ignoring the back-on date (this survived the first draft, whose expectation used the mutated
helper, so the test was rewritten), `paying_method` ignoring `on_after`, the ledger never being fed,
and each of the two DD4b guards. Prediction kept: on the one-year stressed book I predicted fewer than
half of the stopped households would come back even at rate 1.0. 0 of 5 did, because there were too
few months after a stop.

Named simplification: a leg under one payment truth (`world_payment_truth`, off by default) is not
invited. The triad holds its channel.

**Still open: item 1 (the rate).** That is now the only thing between the desk's policy and a run.

**Item 1 answered (worker, 26 Oct, lane 0 `pb8-re-mandate-take-up-rate`).** No energy figure is
published. `REMANDATE_ACCEPTANCE_PROBABILITY` is now 0.035 per invitation, from an EVIDENCE RANGE of
0.035 to 0.05: Medway Council's 2017 BIT trial of a DD prompt to council tax payers, cross-checked
against Ofgem's 2015 survey and DECC's 2015 payment shares (≤4% of SC payers a year leave pay-on-receipt
while staying with their supplier). The lower edge ships (F11). Evidence and the two GAPs it leaves
(whether a repeated ask pulls as well as the first; how recent leavers differ from the non-DD stock):
`gb_payment_method_migration_rates.md`, "A take-up rate for an invitation back onto DD". Item 2 was
built in bf56dd579. Nothing in this finding stays open except those two GAPs, which the knowledge page
carries.
