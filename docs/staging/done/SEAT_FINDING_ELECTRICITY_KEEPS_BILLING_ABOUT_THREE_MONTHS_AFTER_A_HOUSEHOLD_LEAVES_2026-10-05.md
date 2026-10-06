# Electricity keeps billing about three months after a household leaves, while its gas stops on the day

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `electricity-bills-after-departure` (Lane 0 delivery)

**2026-10-05.** Found while the gas-closure cause fix (c355822f3) read the published book's departure
records (site/data/customers/*.json). Three households whose run output records a WHOLE-household
departure show it:
- C1;
- PROS-2016-0121;
- PROS-2020-0032.

In each, gas billing stops at the departure date and electricity keeps billing for about three months after it. Two more show the same pattern but are not in that run output, so their cause is not established:
- PROS-2016-0104;
- PROS-2018-0188.

**Why it matters.**
- **Billing accuracy (step 2, D48):** energy billed after a household left is either billed to nobody or billed to the wrong party.
- **Debt:** an account billed after the customer is gone becomes final-account debt that never existed.
- **Carbon:** it is why these households looked like "gas closed while the electricity stayed", the very shape that read as a heat pump.

**Not established:**
- whether the lag is the world's (a final read taken late), the company's (a final bill raised late), or a book-generation artefact;
- whether it is ~90 days by construction or varies.

**Owed:** one-variable measurement first. For each departed account in a fresh run, compare the departure date, the last electricity read, and the final bill date. Then fix where the lag is born. The move-out stream under B7 must produce a final read on the departure date, so this is also B7's acceptance criterion.

## Settled 2026-10-06: the lag was the world's, and it was not only electricity

**Where it was born.** In the world, not in the company's final bill. On slice 4's decade capture,
every account's last bill ends on the same day as its last settlement record. For each renewal or
SVT departure, the departure is dated the start of a term, and that date is exactly the day after
the gas leg's last record. `simulation/run_phase2b.py` books the departure while it processes the
term of the leg the roll is made on, and that leg then went on to settle the whole term. The other
leg's term with the same start is popped afterwards and skipped. Terms are quarterly, so the lag
was about 90 days by construction. The cases with a lag of 0 were home moves, which cut both legs
at the move date.

**It was not electricity-specific.** Over 2016-01 to 2017-09 at HEAD, 5 of 11 departed households
were supplied after leaving. Two of those were gas legs (SYN-2016-005, SYN-2016-024), where gas
is the leg the departure is rolled on.

**The fix.** A departure booked at a term's start now means that term supplies nothing, on the
same skip the other leg already took. The same 11 households depart, so the rolls did not move.
The control is `tests/simulation/test_a_departed_household_is_supplied_on_no_leg_after_it_leaves.py`.
With the skip reverted, it fails on the gas legs.

**What moves downstream, and is not attributed here.** Every renewal or SVT leaver loses one
quarter of revenue, margin and bad-debt exposure on one leg. The headline P&L, the D48
billing-accuracy figures and the value arms all move at the next run. I cannot yet say by how much.

**B7.** B7's acceptance criterion, a final read on the departure date, still stands for the move-out
stream. This fix covers only the switching routes.
