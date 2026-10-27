**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `tou-tariffs` -- `docs/market_research/a_tou_tariff_needs_the_households_choice_not_its_meter.md`

# PRE-REGISTRATION: a meter register keeps one id and one index for the life of its serial

Filed 2026-10-27, before the ledger is rebuilt. This is breach class 3 of
`SEAT_FINDING_THE_BLIND_INVARIANT_SUITE_ON_THE_67A893E749_BOOK_..._2026-10-26.md`.

## What the code does, read before measuring

- **The register count follows the term, not a per-period draw.** `company/pricing/tou_desk.offers_tou`
  makes a ToU offer on a chosen term to a smart or HH meter, and never on a default tariff. So C7, an
  HH meter, prints one register on its 2017 SVT, two on its 2018 fixed term, and one again on its 2019
  roll.
- **That switch is right, so the direction's premise is corrected here.** SLC 28AD defines a
  Multi-Register Tariff as charging on Time of Use Rates "regardless of the metering equipment
  employed" (`docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md`). A smart
  or HH meter is reconfigured for a new tariff remotely. A tariff change is not a meter exchange, so
  "no serial ever reports two register counts" would be a control keyed to the wrong property.
  Smart status is stamped once, at acquisition, so the book contains no mid-account install that
  should have exchanged a serial.
- **The defect is register identity.** `tools/generate_billing_ledger._printed_registers` numbers
  ToU registers `"1"` and `"2"` by position, and the single-rate register is also `"1"`. So under
  one serial, "register 1" is the total index on one bill and the Peak index on the next (18,568.6,
  then 2,140.6). A one-band ToU stub prints the band's label on the TOTAL index.

## The fix

- Each register has a fixed id for the life of the serial: Anytime/total `1`, Peak `2`, Off-peak `3`.
- Every ToU bill, a one-band stub included, reads its bands' own cumulative indices.
- The total index keeps advancing under every tariff, as a meter's total import register does.

## Predictions (67a893e749 arm A, ledger rebuilt by HEAD before and after; only the generator differs)

- P1. Accounts: 1,291 both times. Periods: 52,782 both times.
- P2. `INV_READ_MONOTONIC` breaches: 29 before (± a few, because HEAD's generator differs from
  884eedc669's), **0 after**.
- P3. (serial, register_id) pairs carrying more than one label: > 0 before, **0 after**.
- P4. Serials that print both one-register and two-register periods: about 66 both times. The
  fix does not and should not change this.
- P5. `INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER`: about 501 both times. The suite classes the meter
  per account ("two or more distinct register_id on the account"). The file's own statement and
  SLC 28AD class it per tariff, so these are single-rate SVT spells graded against the
  multi-register cap. They are explained, not fixed, by this change.
