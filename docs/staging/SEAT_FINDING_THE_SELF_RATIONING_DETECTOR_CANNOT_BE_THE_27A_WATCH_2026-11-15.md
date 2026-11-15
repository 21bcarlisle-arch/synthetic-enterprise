**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** `C32_one_obligation_one_vulnerability_scorer`

# The self-rationing detector cannot be the 27A watch, and no seam door could feed one (2026-11-15)

Found closing C32 ninth pass, item 1. The item asked for "a run caller for
`company/crm/self_rationing_detector.py` that returns a dated ProtectionRecord to the desk's
`self_disconnection_watch`". **That premise is wrong, so the caller is not built.**

## Why the premise is wrong

- **What the detector watches.** Credit customers, on two annual meter reads. It is clean-payment
  only: it stands aside wherever arrears are open, because "the collections path owns it".
- **Who it would be asked about.** Every household offered a Consent PPM is 90 days in arrears. On
  every one of them the detector stands aside.
- **What 27A needs.** SLC 27A.1 and PPM guidance §9.1 watch a *prepayment* customer's top-up and
  disconnection patterns, "on an ongoing and continuous basis", from the day they are on the meter.
- **What the company can see.** No seam door carries a PPM's top-ups or a credit-exhausted
  interruption (`company/interfaces/sim_interface.py`: only `request_prepayment_move` and
  `get_meter_recoveries`).

A record returned from the detector would publish a watch that cannot see what it watches: a
control that cannot fail. The 27A cell stays covered by refusal: no watch, no offer.

## Corrected beside the claims

- The desk's `self_disconnection_watch` comment (`company/billing/collections_journey.py`).
- Commons §5, the new subsection "The S&RP assessment, and why the self-rationing detector is not
  the 27A watch". It corrects the table's `self_disconnection_support` row in prose. The cell's
  state is unchanged.

## What landed alongside

The S&RP assessment, `company/billing/prepayment_suitability.py`:
- it is a dated record that lapses after 365 days (the SLC 28.3 annual re-check);
- it is negative on any 3.7 ground;
- it leaves any 3.8 or 3.9 ground "for a person to decide";
- it is positive only on a clear, dated conversation;
- the gate now refuses a bare True;
- the run's desk reads it.

Nothing live moves: no door brings back a household's answers.

## What would close item 1

Two world doors, then one company build:
1. **The S&RP conversation.** The household answers the suitability questions from its hidden
   state, disclosing what it chooses. The company records the answers in
   `PaymentObservationConsumer.suitability_answers`.
2. **The PPM's supply events.** Top-ups and credit-exhausted interruptions for a moved account.
3. **The 27A watch, built on door 2.** Its lapse is its own reading cadence.

Then prepayment households exist in the world.

NEXT: C32_one_obligation_one_vulnerability_scorer
