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
