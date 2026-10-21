**Severity:** RECORDED · **Lane:** 0 delivery · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `exception_queue` (primary)

# Pre-registration: what answering the listing for the hand-authored founder homes releases

**Claim:** `d48-a-ceiling-hold-the-listing-cannot-answer-is-never-worked`
**Written BEFORE the measurement below was run.**

## The question

`simulated_council_tax_listing` answers None for the hand-authored founders and their incoming
occupiers, because it looks only in `live_premises()`. The world does hold a dwelling record for each
of them (`saas/customers.py` home_type, read by `simulation/dwelling_records.py`). A 3-bed Manchester
semi is a dwelling, and every dwelling in GB is on a council tax list. The change: the listing
answers True for an address whose world record is a domestic home type
(`dwelling_records.PROPERTY_TYPE_BY_HOME_TYPE`). Non-domestic founders (SME, I&C) stay None.

## Predictions

Measured on the 44a21e3e8 run's 38,005 bills, with the listing stamped the way the fixed feed would
stamp it (the D48 item-2 method: dwelling taken from the reconstructed occupier link), through
`bill_assembly.held_bills` / `billing_accuracy`. The baseline is the item-2 "after" state.

1. Held bills 44 -> 40. Held actual-read bills 4 -> 0. Held estimates unchanged at 40, because an
   estimate is never released.
2. K1 held actuals read 0 at every month end. K1 kWh falls at every month end from the first
   OCC-d8e674fa38de bill onwards. At 2025-06 it falls by exactly the four bills' kWh plus their
   `read_true_up_kwh`.
3. Every resi supply point in the run's book reads listed True. That covers the founders, their gas
   legs, their occupiers and the drawn book. SME and I&C read None. The resi accounts still
   answering None number 0 among those with a resolvable dwelling. Any that remain are the 12
   accounts whose link item 2's reconstruction could not resolve, not a feed gap.

If (3) holds, no resi hold in this world reaches the queue without a listing answer. The
contact/certificate half of the queue then has no population to work here, and building it would be
a mechanism nothing reaches.

## Graded (after the measurement)

1. CONFIRMED. 2. CONFIRMED: the drop is 8,577 kWh, with no true-ups. 3. REFUTED AS MEASURED, by the
instrument: HEAD draws a different campaign winner set from the run's code. Detail is in the D48
finding, section "Follow-on (founder homes)".
