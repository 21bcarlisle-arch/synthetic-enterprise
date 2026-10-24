**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`
**Knowledge:** `docs/market_research/company_debt_management.md`, "One ladder for one act" and "After the last rung"

# The collections desk walks back down its own ladder: a final notice, then a second reminder, on one open journey (2026-10-24)

## What was seen

A live run to 2016-12-31 at 78156b7ac had 502 journeys. 400 were cured and 102 were still open at the
run's end. 35 re-offers were made past the top rung. That run was made to check the published
household record. The deepest journey, on one account, reads in date order:

    02-29 missed_payment · 03-06 reminder · 03-13 reminder_2 · 03-27 repayment_plan_offer
    04-24 final_notice · 05-12 repayment_plan_offer · 05-23 final_notice
    06-26 prepayment_or_debt_agency · 06-29 repayment_plan_reoffer · 07-21 final_notice
    07-25 reminder_2 · 07-26 repayment_plan_offer · 08-23 final_notice · ... · 12-26 repayment_plan_offer

So after the top rung, the household receives a final notice and then a "second reminder", and a plan
offer is made each time the oldest bill crosses day 28 again. This is more than one plan offer per
missed bill.

## Why

`collections_snapshot` selects the furthest rung that the account's *oldest overdue bill* has reached.
On a balance-based account, payment is FIFO. When a part-payment clears the oldest bill, the next
bill becomes the oldest, it is younger, and the rung falls. The desk enters any rung that differs
from its current one, so it re-enters lower rungs. The order check (`lawful_successors`) allows this.

## Why LATENT, not BLOCKING

No money moves on a rung, and every step is lawful: SLC 27.5 is satisfied more often, not less. What
is wrong is what the household reads, and the count of plan offers, which is now visible in the
per-household record (`collections_*` events in `reaction_chain`). I cannot yet say what a real desk
does. Whether a supplier's ladder is monotone within an open case, or restarts per bill, is a
practitioner question. Nothing in the knowledge layer says. **GAP:** to be researched, and asked
only if it is not published.

## What would settle it

The research question first: does published practice (Ofgem's debt and arrears indicators guidance,
Citizens Advice supplier assessments, the Consumer Standards decision) describe the ladder as per case
or per bill? If it is per case, the fix is a monotone rung within an open journey, with the re-offer
keyed to each new missed bill. That is the shape 94b281af7 already gave the step after the top rung.

## Disposition (2026-10-24, actioned)

Researched first (K8): `docs/market_research/company_debt_management.md`, "One case, one climb". No GB
rule says whether the ladder is kept per case or per bill (GAP C1: which setting a GB supplier runs).
SLC 27 keys the plan offer to a fresh reason to believe, which is a newly missed bill, not an old bill
re-crossing day 28. SAP FI-CA, the contract-accounting system that utility billing runs on, holds the
dunning level per group, not per item, and has a "Do not reduce dunning levels" switch. The fix is
the shape this finding named:

- **On a balance-based segment the rung never falls inside an open journey.**
  `collections_journey.climbs_per_case`. A cure closes the case; a later miss starts a new climb.
- **Re-offer on each newly missed bill from the plan-offer rung up**, never on a re-crossing.
- **The order check refuses a walk-back.** Open-item (SME / I&C) ladders are unchanged (GAP C2).

Control: `tests/company/billing/test_the_collections_ladder_climbs_per_case.py`, with its rare branch
asserted taken. Three mutations were run and each fired. The re-measure on a live 2016 book is not run
here. The prediction is on the knowledge page, written before any run.
