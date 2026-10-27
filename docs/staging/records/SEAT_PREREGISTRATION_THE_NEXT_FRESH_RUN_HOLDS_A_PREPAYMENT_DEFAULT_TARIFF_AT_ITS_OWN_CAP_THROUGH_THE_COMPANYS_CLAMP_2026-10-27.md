**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION: the next fresh run, graded by the blind suite, after the company's clamp reads the payment method

Filed 2026-10-27, before any run carries the fix. The predictions below are not edited after the run.

## What changed

- **The company's cap clamp** (writer 4, `company.pricing.renewal_rate_chain`) holds a domestic default
  tariff at min(the published level, its payment method's own column). It used to hold the published
  level, which is the DD column. The run loop hands the chain the method the segment was priced on.
- **The standing-charge invariants' tolerance** is a penny over the period as well as 0.0001 GBP/day.
  That is a grading change, so it is already measured on the 871f674a2 book: 735 → 0 and 1,502 → 0.

## Predictions (reference: the 871f674a2 book, 1,291 accounts)

| Invariant | Was | Predicted | Why |
|---|---|---|---|
| INV_UNIT_RATE_SVT_ELEC | 298 | **0** | All 298 are prepayment SVT segments raised by writers 1-2 above the prepayment column. Replaying the run's own `rate_decomposition_log` through the new ceiling moves all 552 breaching term-starts and no DD or standard-credit term. |
| INV_UNIT_RATE_SVT_GAS | 249 | **0** | The same. |
| INV_STANDING_CHARGE_SVT_ELEC | 735 | **0** | Already 0 on the same book under the corrected tolerance. |
| INV_STANDING_CHARGE_SVT_GAS | 1,502 | **0** | The same. |

## What could refute it, named in advance

- **The lesson of 58af1fe57.** Its offline re-price predicted 0 and missed the company's own writers.
  This replay models those writers' recorded output, not their response to the lower revenue that
  follows. Lower prepayment revenue lowers margins and raises later premiums. The clamp bounds any
  premium, so this should not breach, but the replay did not test it.
- **A method change inside a cap window.** The chain prices on the method on the segment's first day.
  The invariant reads the prepayment column if *any* payment in the window was prepayment. A household
  that moves onto prepayment mid-window would breach. None of the 871f674a2 breaches is such a
  household (all are prepayment from their first payment), so this would be a new class.
- **SVT terms that reach no decomposition.** All 547 breaches had one. A term that bypasses
  `decide_renewal` would not be clamped at all.
