**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`
**Knowledge:** unbilled-energy-and-revenue-assurance

# Every closing read is actual in the world, but published practice makes a move-out's final read actual only sometimes (2026-10-17)

Found while giving the empty-period flag an opening read at a change of tenancy (direction item
`the-company-holds-an-opening-read-at-a-change-of-tenancy`; pre-registration
`records/WORKER_PREREG_W2_36_THE_OPENING_READ_AT_A_CHANGE_OF_TENANCY_2026-10-17.md`).

**What the code does.** `company/billing/monthly_bill_assembly.py` (around line 620) asks for a
final read when a churned account's last bill would otherwise be estimated. The world's
`simulation/meter_reads.final_read_for` answers with `status="actual"`, unconditionally. The
company code's comment calls this "SLC 21B final-bill-at-closure". The final-bill locus is
SLC 27.17 ("all reasonable steps to send a final Bill … within 6 weeks", `home_moves.md` §8), and
neither condition makes the closing read actual.

**What published practice says.** A move-out's final read is actual "sometimes": if the customer
gives one, or if a smart meter is read remotely on the day. Otherwise it is estimated
(`home_moves.md` §3 and §8.2). The change-of-supplier rule falls back to an estimate when no actual
read is valid within SSD±5 (BSCP504 §4.4.1). **GAP:** the share of change-of-tenancy boundary reads
that are actual.

**Measured on the published run book** (`run_output_latest.json`, 78f77c34e). There are 135
electricity move-outs with a closing read on the day before the move. 91 of those reads were forced
by `final_read_for` (89 traditional, 2 smart), and 44 were ordinary reads that happened to be
actual. Over the whole book, traditional reads are actual 6,944 times in 32,015 (22%). The forced
read makes the boundary actual about four times as often as the meter's own read rate would.

**Who it misleads.** (1) The opening read at a change of tenancy: the empty-period flag now judges
an incoming account's first span from an actual opening read. 6 of the 16 void stubs it judged rest
on a forced read. All 16 file as `void`, so no lead was invented, but the judged count is inflated.
(2) Probably more by value: every churned account's catch-up resolves on an actual read, so the
estimation error at closure never reaches the final bill. That error is the CoT dispute seed in the
scope brief's B3. This second effect is not measured here.

**Proposed remedy (world lane, not built here).** `final_read_for` returns actual only where the
world has a reason: a smart meter in smart mode, or a customer-own read at a sourced rate. Otherwise
it returns an estimated read. The customer-own rate is the GAP above, so until it is sourced the
honest default is to keep the ordinary read's status (`read_for`'s draw) and carry the GAP by name.
Then fix the company comment's licence condition to SLC 27.17.

## End-to-end check

Explanations the evidence allows, ranked: (a) **the world is too generous**, and a final read was
modelled as a certainty to close the estimation run (the comment says so). This is most likely.
(b) Real suppliers do get an actual read at most move-outs. No source read here says so, and the
published guidance tells movers to give a read *because* the supplier may otherwise estimate.
(c) The SLC citation is right under an older numbering. Even so, it would not make the read actual.
