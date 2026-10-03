# The world lets a debtor switch away, because the domestic debt objection is unmodelled

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

## What is true in the published record

A GB supplier may object to the transfer of a domestic credit customer who owes it money, and an
objection legally stops the transfer (Ofgem, *Decision on review of domestic objections*, 2016;
summarised in `docs/market_research/svt_drift_by_payment_behaviour.md` §"Domestic debt
objections"). So "worse payment record -> less able to leave" is ESTABLISHED in direction. The
2016 impact assessment's objection rates by debt band are NOT extracted: both PDFs returned
compressed streams (same file, line 55).

## What the world does instead

No code path in `simulation/` blocks a household's departure on its own arrears. The departure
draw is the churn roll against the world's P(stay), whatever the account owes, and on departure
`simulation/arrears_engine.compute_emergent_bad_debt` writes off the unpaid balance at close.

## Why it matters now

The value arm's worst seed (61002, selection -GBP 12,726) is dominated by one account,
PROS-2016-0098, which ran to about GBP 12k of arrears. The 2026-10-03 pricing fix made arrears
move the arm's bad-debt cost: money owed is priced at Centrica's live provision rate if the
household stays, and at the final-bill rate if it leaves. Both of the company's leave-branch
beliefs, the churn hazard and the final-bill write-off, assume a debtor CAN leave. Under the real
objection right, a domestic credit debtor mostly cannot, so the world currently rewards a pricing
belief a real supplier would not hold. That is a fidelity gap on the world side, to be decided
blind to company results, and not a reason to change the company's belief.

## What closing it needs

1. The objection rate by debt age or amount: extract the 2016 impact assessment's tables (the
   fetch failed on compression, not on access).
2. Who it applies to: domestic credit (not prepayment, where the Debt Assignment Protocol moves
   the debt), and the 28-day threshold.
3. A world-side draw that blocks a departure the objection would stop, with the household staying
   on supply.

Until then, read any A/B result that turns on a debtor's departure as carrying this gap.
