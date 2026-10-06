# The statement-walk control's "emptied ledger" floor is one run's size, and it reds every lane that touches statement_export

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `statement-walk-floor-keyed-to-the-property` (Lane 0 delivery)

**2026-10-06.** `tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py` guards against an emptied ledger with literal floors: `accounts >= 240` (line ~260) and `>= 200` (line ~286). The live run ledger the gate overlays holds 175 accounts, so both assertions red.

The test is selected for any commit that changes `company/billing/statement_export.py` (import-derived selection). It refused a comment-only citation fix today (SLC 31A -> 21BA), which was withdrawn from that landing and is still owed.

This is CLAUDE.md's "key a control to the property, not to today's answer". A floor typed from one run's size goes red when a later run is smaller, and says nothing about whether the ledger is empty.

**Owed:**
- Key the floor to the property: the ledger is non-empty and matches the run that produced it, for example its own account count against the run output's manifest. Do not lower the literal.
- Then land the owed citation fix in statement_export.py.
