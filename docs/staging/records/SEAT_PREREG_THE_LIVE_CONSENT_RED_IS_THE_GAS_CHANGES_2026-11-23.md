# Pre-registration: is the live Consent red the gas-only win's? (23 Nov 2026, 06:36Z)

```
PRE-REGISTRATION 2026-11-23 (delivery seat, verify-reg-6c-and-gas-only-win-resume-chain)
Question: are test_a_live_run_withholds_the_prepayment_offer_at_the_ninety_day_rung and
test_the_world_counts_every_consent_offer_the_company_made red because of the gas-only win change?
Measurement: run both tests (a) on origin/main 0b4d8ae594 with no gas change, (b) on the same base
plus the gas files from /tmp/seat_gas/files.
Prediction: (a) green, (b) red -- supplying 2 gas wins changes the population in the short
answered window so the one live Consent (prepayment) offer no longer happens. Confidence ~65%.
Alternative: (a) also red -> pre-existing on origin, not the gas change's.
Decision rule: (a) green & (b) red -> the gas change caused it; read why before any edit to the tests.
(a) red -> pre-existing red on origin; file it and do not land the gas change over a red gate.
```

Outcome: the prediction was wrong. (a) origin was red too. See the BLOCKING finding SEAT_FINDING_ORIGIN_IS_RED_ON_THE_LIVE_CONSENT_OFFER_SINCE_7527A2E36_AND_IT_BLOCKS_THE_GAS_ONLY_WIN_2026-11-23.md.
