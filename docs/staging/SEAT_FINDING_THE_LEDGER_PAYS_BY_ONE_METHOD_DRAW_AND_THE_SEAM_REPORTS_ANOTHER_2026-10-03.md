# The company's ledger is paid by one payment-method draw and the seam tells it another

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `W2_payment_channel_dd_consistency_invariant` · **Claim:** `the-company-default-belief-is-measured-against-its-own-ledger` (Lane 0 delivery)

**2026-10-03.** Found while measuring the company's default belief against its own ledger.

## What is true

A household's payment method has two homes in the world, and both are live in every run:

| reader | draw | what it decides |
|---|---|---|
| `background/live_payment_triad.LivePaymentTriad._method_for` | `simulation.payment_behaviour_source.generate_payment_method` (DD / standing order / card / prepayment) | the payment events that cross the seam into the company's ledger: which bills fail, which are paid late |
| `SimInterface.get_payment_method` → `simulation.household_segments.payment_channel_for_customer` | a separate stream, `paychannel_{household}_electricity` | the method the company is told it holds, which the renewal price now reads to choose its provision row (`e0370bf94`), and which the engagement antecedent and the world's own `arrears_engine.payment_method` read |

Measured over 300 ids (`PROS-2016-0000`..`0299`, electricity), mapping standing order and card to
standard credit as the seam does: **153 agree, 147 disagree.** Among the disagreements, 28 households
the ledger bills as direct debit are reported to the company as prepayment, and 23 the ledger bills as
prepayment are reported as direct debit. The two draws are independent, and with a 72% DD share each,
51% agreement is about what chance gives.

## Why it matters now and did not before

`docs/staging/done/SEAT_FINDING_THE_ENGAGEMENT_ANTECEDENT_R1_NEEDS_IS_DESTROYED_BY_A_COLLAPSED_PAYMENT_BUCKET_2026-09-05.md`
measured the same disagreement (41% on DD/non-DD) and called it "NOT a live inconsistency today,
precisely because one of the two never runs". **That premise was already false.** The triad has
called `generate_payment_method` since `3bfd4e98c` (2026-07-18). That finding's search covered
`simulation/`, `company/` and `saas/`, and the caller is in `background/`.

Since `e0370bf94` (2026-10-03) the renewal price reads the ledger's unpaid bills and provisions them on
the row for the seam's method. So about half the book is priced on a provision row for a method that
is not the one that produced the debt. Any per-method default rate the company learns from its own
book (`company/pricing/default_belief.py`) is blurred in the same way, because its cells are keyed by
the method the company was told.

## The fix, not done here

Do what the 09-05 finding asked: one definition. Move `payment_channel_for_customer` onto
`generate_payment_method`'s draw, or the reverse. Either way the triad and the seam then read the same
fact. It is a world change. It moves households between buckets and it will move published bad-debt
figures, so it is fidelity work, done deliberately and measured. It is not a refactor. A control that
asserts the triad's method equals `SimInterface.get_payment_method` for every account in a run is the
one leg that catches the class. Not built here, because building it would mean writing the fix.
