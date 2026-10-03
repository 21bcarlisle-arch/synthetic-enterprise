# For the console seat: a household's payment method now has one home, so re-read B8's per-method slopes on it

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `W2_payment_channel_dd_consistency_invariant` · **Claim:** `one-payment-method-home-in-the-world` (Lane 0 delivery)

**2026-10-03.** This is the hand-off the delivery item asked for. Nothing here touched
`company/pricing/discovered_price_sensitivity.py` or `/var/tmp/se-b8`.

## What changed in the world

`LivePaymentTriad` used to pay the company's ledger by its own payment-method draw. The seam reported
a different one. On the live resi book the two agreed on 112 of 178 supply points. The triad now
reads the seam's draw (`household_segments.payment_channel_for_customer`), and standard credit is
refined into standing order or card on top of it. Ledger = seam on 178 of 178. Details and the
control are in `SEAT_FINDING_THE_LEDGER_PAYS_BY_ONE_METHOD_DRAW_AND_THE_SEAM_REPORTS_ANOTHER_2026-10-03.md`.

The seam's answers, the world's churn response and `arrears_engine` are **unchanged**. They already
read this draw. What changed is which bills fail and which are paid late in the company's own
ledger, for about a third of the book. The world identity carries a new `payment_methods` part:
`8a105ad7c9346758` before, `86560148d7db82b7` after.

## What it means for B8

Any per-method churn slope keyed by `get_payment_method`, and fitted on events from a run before this
commit, paired a method label with arrears and payment history produced under another method for
about a third of households. **Re-fit on a run whose `world_identity.payment_methods.digest` is
`86560148d7db82b7`.** A slope that sharpens after the re-fit was a fidelity defect and not an
inference failure. Weigh the before/after comparison with that in mind. Do not difference a slope
from a run before the change against one from a run after it: the two runs are different worlds.

This is also the prerequisite PB8 L2 was waiting on. `get_payment_method` now has one source, so
making it follow a cancelled mandate is one change in one place.
