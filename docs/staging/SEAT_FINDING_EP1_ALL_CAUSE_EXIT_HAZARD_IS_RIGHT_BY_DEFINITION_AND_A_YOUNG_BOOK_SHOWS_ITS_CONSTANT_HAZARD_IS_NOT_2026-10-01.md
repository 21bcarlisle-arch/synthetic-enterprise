**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# EP1's all-cause exit hazard is right by definition, and a young book shows its constant hazard is not

**Opened by** the result section of
`docs/staging/records/SEAT_PREREGISTRATION_EP1_TENURE_HORIZON_ON_THE_BOOKS_ALL_CAUSE_EXIT_FREQUENCY_2026-10-01.md`.
It closes the build that
`SEAT_FINDING_THE_WORLD_DECIDES_A_RENEWAL_AT_ONE_ANNIVERSARY_IN_FIVE_SO_A_PER_RENEWAL_HAZARD_HAS_NO_AGREED_DENOMINATOR_2026-10-01.md`
pointed to.

## What landed

H2 `tenure_expected` now values on `BookExitRecord`. That is the book's exits at ANY time (from
`ceased_billing_accounts`) over the account-years it has settled, converted to an annual
probability with `1 − exp(−rate)`. `customer_value_view.observed_book_exits` counts it from the
company's own records, truncated at each snapshot. The per-anniversary `BookRenewalRecord` is still
published beside it as a diagnostic, and H2 never reads it. `clv_gap_selection.lifetime_level` reads
`book_exits` first. Without that order it would publish the renewal hazard as the hazard EP1 used.

The director's answer on what a renewal is does not block this. That answer changes the renewal
reading. A tenure ends at a switch, a mid-term switch or a home move alike.

## What the measurement showed

On the real book at 2025 the hazard is 0.137 (89 exits over 606 account-years), where the
per-anniversary reading gave 0.092. Against HEAD's per-anniversary H2, the one-variable gap arm
moves from **1.437 to 1.558**. Every belief year from 2018 to 2022 improves. 2017 (51 of the 69
graded rows) and 2016 (3 rows) get worse.

- **2017: the constant hazard is the defect.** A one-year-old book's exposure is mostly in-term
  first-year time. Its all-cause rate (0.109) is below its per-anniversary rate (0.145), because
  departures cluster at the first renewal. Valuing a customer's whole tenure at a rate averaged over
  that quiet first year overvalues them.
- **2016: one event.** 1 exit over 61 account-years gives a hazard of 0.016 and a ~61-year tenure.
  The n is on the page (`book_exits` on every snapshot), but no bound is. A minimum-event threshold
  would be a picked number, so none was added.

## Next (handed on)

Value H2 on an all-cause hazard **by tenure year**: exits in the account's k-th year over exposure
in its k-th year, pooled across the book. Survival is then the product of those hazards, not a
geometric series. It is company-observable, it needs no new observable, and it addresses both
readings above: the first-year rate is low, and the first-renewal year carries its spike. Until it
lands, the pooled constant hazard is the honest best and it is labelled as constant.

The ledger row still waits. `run_output_latest.json` is the `b1b4c284e` run, produced before
81977a312. Its snapshots carry the 0.05 belief, so `couple_clv --write-ledger` now would grade the
old H2 under this commit's name. The row needs a fresh run promoted through the ordinary publish
path.
