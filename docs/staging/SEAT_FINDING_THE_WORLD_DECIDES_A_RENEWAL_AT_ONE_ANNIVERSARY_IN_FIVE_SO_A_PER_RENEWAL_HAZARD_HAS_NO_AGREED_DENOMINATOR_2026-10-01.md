**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# The world decides a renewal at one anniversary in five, so "per-renewal hazard" has no agreed denominator

**Opened by** the result section of
`docs/staging/records/SEAT_PREREGISTRATION_EP1_TENURE_HORIZON_ON_THE_BOOKS_OWN_OBSERVED_RENEWAL_DEPARTURES_2026-10-01.md`.

## What was measured

EP1's H2 now values on `observed_book_renewals` (landed `81977a312`). That function counts, from the
company's own settled records, every annual anniversary of `acquisition_date` the account went on
settling past (a stay), and every cessation in or just before an anniversary month (a departure).
On a fresh full run this gave **531 decisions, 49 departures, hazard 0.092**. The world's
`customer_events` give **106 decisions, 38 churned, 0.358**: the 0.36 that EP1 pass 20 put on the
record as "realised at renewal".

**The derivation is faithful wherever the world has an event.** Matching on account and month (±1):
37 of 38 world churns are derived departures, and 68 of 68 world renewals are derived stays. The
whole fivefold difference is **414 anniversaries at which the world rolled no decision at all**, plus
12 cessations near an anniversary that the world logged as no renewal churn. 89 accounts ceased
over the run, and only 49 of those cessations sit at an anniversary.

## Why this is a definition question, not a number to tune (CLAUDE.md: say what the thing is)

There are three readings, and they give three different "hazards":

- **Per world-decision** (0.36). This is the rate at the points where the world rolls dice. A
  supplier cannot see which anniversaries those are, because the roster carries `contract_type` for
  only 25 of 256 accounts.
- **Per anniversary** (0.09). This is what the company can count. It treats an anniversary the
  world never decided as a stay, which the customer, in the world, then was.
- **All-cause annual exit** (about 0.17). This is (49 + 40 off-anniversary cessations) over the same
  anniversaries. A TENURE horizon arguably needs this one, because a home move ends a tenure as
  surely as a switch does.

The landed H2 uses the second reading. It is the company's own observation, and it moves the level
from 0.05 toward the record, but it is not yet the reading the tenure horizon needs.

## The question for the third side (director)

On a small supplier's book, which anniversaries are real decision points? In particular, does a
customer who has rolled onto the default tariff face an annual "renewal" at all, or only a standing
monthly hazard? The world answers this one way: it decides at 106 of about 520 anniversaries. It has
not been checked against how the trade works, and nothing here should be built on it until it is.

## Not done here, deliberately

- No ledger row. `couple_clv --write-ledger` waits on the premise-two-level reds, and this frame
  question comes first.
- H2 is not switched to the all-cause reading. That is the build this finding points to, and it
  needs the definition settled before it is written.
