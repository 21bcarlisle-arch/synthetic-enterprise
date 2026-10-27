**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `price-cap` -- `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`

# PRE-REGISTRATION: the blind suite's gas unit-rate rows take the commons' gas floor and non-DD ceilings

Filed before the amended suite is run.

## What changes, and why it is not a change of intent

`docs/design/DOMAIN_INVARIANTS.yaml` was written blind from the commons on 2026-10-26. At that time
the commons held no gas composition, so three gaps were recorded:

- `INV_UNIT_RATE_SVT_GAS` has `lower: 0.0` (logic only), flagged "no gas commodity component in the
  commons".
- The same rows grade direct debit only: non-DD windows are UNCHECKABLE because "standard-credit and
  prepayment gas cap rates are not in the commons".
- `INV_UNIT_RATE_SVT_GAS_PRE_CAP` has one positive-only row.

The commons now carries the gas composition per payment method, with corroboration:
`ofgem_cap_unit_rate_composition.json#gas_by_payment_method`, landed with the floor commit of
2026-10-27. Each row is filled the way the suite's own electricity rows already are:

- `lower` is the DD commodity allowance, DF+CM, lowest region (`commodity_p_per_kwh_ex_vat_min`).
  Below it is a flag, as for electricity.
- `upper_standard_credit` and `upper_prepayment` are added, and the evaluator uses the electricity
  column rule (`_upper_for_methods`).
- The pre-cap row is split into Ofgem's back-cast half-years, each with its commodity floor, as for
  electricity.
- `lower_source` cites the field. The values come only from the commons; no code under test was read.

## Book

`/tmp/inv/raw_67a893e749_trunk.json`, the book the suite's first run graded. Before the amendment
(re-run 2026-10-27): `INV_UNIT_RATE_SVT_GAS` CLEAN, 0 of 4,713. `INV_UNIT_RATE_SVT_GAS_PRE_CAP`
CLEAN, 0 of 1,768. `INV_UNIT_RATE_SVT_ELEC` BREACHED, 496 (9.2%): prepayment billed at the DD cap.

## Predictions

- G1. Floor: 0 flags on either gas invariant. The world's gas SVT sits at the cap, which is at least
  1.08x DF+CM+NC+PC and so well above DF+CM.
- G2. Ceiling: `INV_UNIT_RATE_SVT_GAS` goes from CLEAN to BREACHED. The breaches are all in
  prepayment windows where the gas PPM cap is under the DD cap by more than 0.5%. That is the
  electricity defect seen on gas, now that the suite can see gas prepayment. Expected share: 3% to
  15% of checked term-windows.
- G3. No standard-credit window breaches, because the SC cap is above DD in every window.
- G4. Checked counts rise: non-DD windows, which were positive-only, now carry a ceiling. The total
  term-window count (4,713) does not change.

## Result (run after filing, same book)

| | before | after |
|---|---|---|
| `INV_UNIT_RATE_SVT_GAS` | CLEAN, 0 of 4,713 | **BREACHED, 462 (9.8%)**, 0 flagged |
| `INV_UNIT_RATE_SVT_GAS_PRE_CAP` | CLEAN, 0 of 1,768 | CLEAN, 0 of 1,768, 0 flagged |

Term-windows by payment method: DD 3,284; standard credit 835; prepayment 581; no payments 13.

- G1 held: 0 floor flags on either invariant.
- G2 held: all 462 breaches are prepayment, 462 of 581 prepayment term-windows. Rate over the
  prepayment cap runs from 1.012 to 1.050.
- G3 held: 0 standard-credit breaches.
- G4 held in half. The term-window count is unchanged at 4,713, but the checked count did not rise.
  The old evaluator already counted a positive-only band as checked. What did rise is the share
  with a ceiling: 1,429 non-DD term-windows now carry one, against none before.
- The pre-cap count is unchanged at 1,768 under seven half-year rows. Each pre-cap SVT term
  therefore sits inside one back-cast half-year.

**What it is:** the same defect as `INV_UNIT_RATE_SVT_ELEC`'s 496, measured on gas. The world prices
every SVT at the GB direct-debit level whatever the payment method. It is added beside item 1 of the
blind suite's 26 Oct finding rather than filed again.
