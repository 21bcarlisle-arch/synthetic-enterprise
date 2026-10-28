**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# A successor's page prints a different meter number from the account it succeeded, and one household's estimates ran five times its meter (2026-10-28)

**Found by** the mover slot's work (the closed finding is
`docs/staging/done/SEAT_FINDING_THE_MOVER_SLOT_IS_EMPTY_BY_A_CONSTANT_AND_ITS_REASON_DENIES_A_RECORD_THE_PAGES_CARRY_2026-10-28.md`).
Both are on the 1691ec0ecd pages in `/var/tmp/second-cold-read-1691/tree`. Neither one changes which
household fills the slot.

## 1. The meter point is per account on the page, not per premise

An incoming occupant's page names the account it succeeded "at the same meter point"
(`predecessor_account_id`, `home_moves.md` §8.8, choice 6). Yet in **253 of 253** successions, the
occupant's published MPAN bottom line (or MPRN) differs from its predecessor's. The cause is that
`tools/generate_customer_data.py` (`_mpan` and `_mprn`) and `company/crm/customer_registry.mpan_core`
hash the **account id**. They do not hash the supply point.

An energy reader who opens both pages sees two meters where the record says there is one. The
customer pages and invoices print the number. The Explore cast does not.

**What closes it:** key the meter-point identifier to the supply point, so that a successor carries
its predecessor's identifier. `mpan_core` is also read by the billing ledger, so check what else keys on it.

**Closed 2026-10-28.** `company/crm/customer_registry.supply_point_of` follows `occupier_successions`
(and the registry's `successor_of`) to the account that first held the point. The page, the ledger
and the registry mint from that account. On the 1691ec0ecd run, the ledger rebuilt in a worktree
grades **253 of 253** billed successions as printing their predecessor's MPAN/MPRN and meter serial.
Six successions have one side unbilled. No number is shared across two points.

The MPRN also gets one home (`customer_registry.mprn`). On the same book, all 586 gas page headers
differed from their own invoices: the page and the ledger each minted its own. The ledger's scheme
summed character codes, which put 586 gas accounts on 164 numbers. After the fix, 1,293 of 1,293
accounts' headers match their invoices. Control:
`tests/tools/test_a_successor_prints_its_predecessors_meter_point.py`. The published pages change at
the next publish. Section 2 stays open for the suite owner.

## 2. Estimated bills ran five to ten times the meter, and no check caught it

SYN-2016-565 (electricity, resi):
- Monthly estimates of 1,250 to 2,007 kWh ran from Jul 2023 to Jun 2024.
- An actual read then credited £1,471.52 in July 2024 (277 kWh billed) and found 144 kWh in August.
- The next two estimates went back to 933 kWh and 641 kWh, the latter over 19 days.

The book's use band does not catch this, because the band is drawn over estimated bills too. Before
the mover slot required an actual closing read, it ranked this household first.

**Candidate invariant for the suite.** It must be written blind from the knowledge pages, per the
ruling of 26 Oct, step 4. The candidate: an estimated bill's daily use is consistent with the same
meter's actual reads around it. GAP: no published tolerance is established here, so the invariant's
author must source one or state the belief and its range.

**What closes it:** the suite owner writes the invariant and measures how many households breach it.
The estimate-trap and default-account slots should be re-read under it.
