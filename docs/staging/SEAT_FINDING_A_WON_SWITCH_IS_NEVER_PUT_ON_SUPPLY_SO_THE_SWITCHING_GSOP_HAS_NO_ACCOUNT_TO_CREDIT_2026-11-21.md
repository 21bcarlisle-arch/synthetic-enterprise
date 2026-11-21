**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# A won switch is never put on supply, so the switching GSOP has no account to credit (21 Nov 2026)

**What was asked.** Item `world-posts-switching-gsop-credit-and-returns-erroneous-gain`: post each
reg 6ZA/6ZB payment (`switching_gsop_payments`) as a credit on the customer's leg ledger in
`simulation/run_phase4c_on_phase2b.py`, and return an erroneously transferred household to its old
supplier within 21 working days of the agreement.

**What the tree does.** The gains that `gain_registration_log` records are the fresh-market
acquisitions won at `run_phase2b.py` ~5250 (`make_acquired_customer` -> `ACQUIRED_CUSTOMERS`). The
settlement roster is `_ALL_KNOWN_CUSTOMERS = CUSTOMERS + SUCCESSOR_CUSTOMERS` (`run_phase2b.py:445`),
plus admitted incoming occupants. `ACQUIRED_CUSTOMERS` is never in it. A won switch is registered,
its funnel cost is booked, it is written to `company_event_log` as an `acquisition`, and phase 4c
gives it an opening DD and an opening registry kWh. It is never settled, billed or collected.

**Measured** on `docs/reports/run_output_latest.json` (producing commit 6a588a832f, 20 Nov):

| | count |
|---|---|
| fresh acquisitions won (`company_event_log`, `event_type == acquisition`) | 16 |
| of them in `bills` or the billing ledger | 0 |
| won before CSS go-live (18 Jul 2022), so an erroneous transfer can be drawn | 13 |
| won 1 May 2020 to 17 Jul 2022, so reg 6ZB is owed if drawn | 5 |
| expected erroneous transfers in the book (13 x 0.005) | 0.065 |
| P(at least one 6ZB payment in the book) = 1 - 0.995^5 | 2.5% |

Each of the 16 ids appears in exactly three or four places: `acquired_customers`,
`company_event_log`, `opening_dd_by_customer` and `opening_registry_kwh_by_customer`.

**Why it is BLOCKING.** The P&L carries the cost of winning these customers and none of their
margin. K2 applies: leaving it out asserts zero. Every downstream read of acquisition also reads
customers who never took supply: CAC against won count, the growth mandate, and the switching GSOP.
The item's two asks cannot be built honestly on top of this:
1. *Post the credit.* The account has no bills, so there is no ledger to net a credit against. Booking
   the £30 as a P&L line without a ledger would be a cost with no customer behind it.
2. *Return the erroneous gain.* The world has no supply to end. "About 0.5% of pre-CSS gains stay
   on supply" (the item's WHY) is false today. No gain is ever on supply.

Even once both are built, the book's expected number of switching GSOP payments is under one at
today's acquisition volume. The posting still matters because a curriculum with real growth will
draw them. It does not change today's P&L.

**Explanations considered.** (a) A deliberate Phase 8a/12a scope choice: neither
`NEXT_PHASE_12a_complete.md` nor any simplification record says acquired customers are kept off
supply, and `make_acquired_customer` builds a full supply record (location, fabric, EAC, meter).
So this is unbuilt, not chosen. (b) They are settled under another id: no. A search of the run output
for each id finds the three or four places above and nothing else. (c) The run output is stale
against the code: the roster line is unchanged at HEAD f97098c25e.

**What follows.** Put a won switch on supply from its supply start, the same way
`_admit_incoming_occupant` supplies an incoming occupant: join the settlement roster, the adopted
book and the domestic-leg set. That needs the Phase 2b run (about 100 minutes) to grade, and it moves
published figures. After that the switching GSOP item can post its credit and end an erroneous
gain's supply. It is handed on behind this finding.

**Corrected in the same landing.** `simulation/gain_registration.py`'s "Not built" note and the
`run_phase2b.py` output comment both claimed the world "keeps the household on supply". Both now
name this finding.

**Progress, 21 Nov (later the same day).** `run_phase2b._supply_won_switch` now puts a win from an
electricity household on supply from its win date, and `_known_customers()` reads those supplied
wins. On a 2016-2017 probe, SYN-2016-144_3 settled its first term (19 Mar 2017 to 1 Jan 2018,
actual net £100.19). A win from a gas-only household (2 of the 16 on the 20 Nov run:
SYN-2016-163_3, SYN-2016-585_3) stays off supply. Its reason is published in
`won_switches_not_supplied`, because `register_acquired_point` stamps every win electricity and
supplying it as gas is not built. Predictions and P1's refutation:
`records/SEAT_PREREG_A_WON_SWITCH_IS_SUPPLIED_FROM_ITS_WIN_2026-11-21.md`. Still open: the full-run grade,
the gas-only wins, the GSOP credit posting and returning an erroneous gain (reg 6C).
