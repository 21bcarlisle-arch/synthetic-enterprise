# A credit posts behind the collections walk, and no run counted it

**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

Filed by the delivery seat, 2026-11-22, under the direction item
`which-credit-crosses-after-the-journey-walk-passed-its-value-date`.

## What is known

`CollectionsJourneyDesk.advance` is promised a ledger complete for value dates up to each walk's
`through`. On book 61118 (s.12g pin) that broke for ACC-SYN-2016-239: reminder_2 on 2020-12-15 was
lawful when issued, a credit valued by 12-15 posted after the walk passed that day, and the cure on
12-16 re-read 12-15 at GBP -22.53 and stopped the run. e09f1640a judges each step once, at issue,
so the run no longer stops -- and the late credit became silent. `steps_cleared_after_issue` held
the rows but no run output carried them.

**Which route crossed it is NOT yet established.** Read from the code, before any measurement:

- **Plan instalment: ruled out for a step's own day.** `_read_instalments` runs at the start of
  every `_step`, posting every instalment due by that day before the view is read. An instalment can
  post behind `_through` only on a day where no step was taken, so no step read the ledger without
  it. (It can still be counted as "behind the walk" -- the row is honest -- but it cannot cause the
  239 shape.) A plan is also offered only after reminder_2.
- **Held lump (`_settle_held` / `_cross_settlement` / a reader's `force`):** possible. The world-side
  `settlements_behind_the_walk` already counts these; the 61118 run died before writing it.
- **Cash crossing with its bill in `record_period`:** possible on a two-leg account if one leg's
  cash carries a value date at or before another leg's walk.

## What this change adds

Every received credit goes through `PaymentObservationConsumer._post_cash`. It now records each
credit valued on or before its desk's `walked_through` (`credits_behind_the_walk`), once per ledger
event. The triad classifies each row by route (`held_lump`, `plan_instalment`, `with_its_bill`)
and the run publishes, under `credits_behind_the_walk`:

- `count` over `credits_posted` (every PAYMENT_CREDIT on the company ledger), `by_route`;
- `dunning_steps`: `steps_cleared_after_issue` over `dunning_steps_issued` (the stages
  `dunning_of_a_cleared_debt` judges), and how many accounts.

Run output carries counts plus twenty examples; every row goes to the world-walk-truth sidecar.
Controls: `tests/company/billing/test_a_credit_behind_the_walk_is_counted.py` (both sides of the
partition and the inclusive boundary in one control; four mutations each fire),
`tests/background/test_a_lump_crossing_behind_the_desks_walk_is_counted.py` (the route is
`held_lump`; dropping the lump tag makes it `with_its_bill` and fails).

## Pre-registration (filed before any run carries these keys)

On the first full run on origin/main that writes `credits_behind_the_walk`:

1. `count >= 1`. A count of 0 on a book that ran to the end would say the 239 credit was a
   61118-pin-only shape. Confidence 85%.
2. The dominant route is `held_lump`. Confidence 60%; `with_its_bill` 35%; `plan_instalment` 5%
   (counted on non-step days only, per the reading above).
3. `dunning_steps.steps_cleared_after_issue / dunning_steps_issued` is under 1%. Confidence 75%.
4. On book 61118 specifically, ACC-SYN-2016-239 appears with a credit valued 2020-12-15 or earlier
   and `walked_through` >= 2020-12-15.

Wrong predictions stay here beside the result.

## Next

The route that dominates is the next fix: the walk should not pass a day whose cash is still
in flight on that route. That is a build, decided after the count is read, not before.
