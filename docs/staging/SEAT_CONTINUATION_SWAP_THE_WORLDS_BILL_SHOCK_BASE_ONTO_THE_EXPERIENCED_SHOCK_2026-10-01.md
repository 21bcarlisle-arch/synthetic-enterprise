**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Continuation: swap the world's bill-shock base onto the experienced shock, after one run measures it

**2026-10-01, autonomous worker, item `rederive-the-worlds-bill-shock-hazard-so-it-fires-in-year-one`.**

## What landed

`simulation/experienced_bill_shock.py` defines the shock per `docs/market_research/what_bill_shock_is.md`:

- **Direct debit:** the DD reset at the annual review, read through `company.interfaces.dd_review_outcome`.
- **Standard credit:** the year's bills.
- **Prepayment:** out of scope, so `None` with a reason.

The year-one reference is the amount quoted at sign-up, so the shock can now fire at a first renewal. A fall is not a shock. `roll_lifecycle_event` emits it on every renewal event as `sim_experienced_bill_shock`. It is ground truth, and the company must not read it (B8).

**The hazard still reads the old count.** That is deliberate. `year_level_anchor` was fitted against the old month count, so swapping the base moves the departure level as well as its gradients, and two changes in one run cannot be attributed.

PB4's `file_scope` now names the four files the swap touches.

## What is next, in order

1. **Run one world.** Measure the tenure and bill-size gradients of `sim_experienced_bill_shock.shocked` over first and later renewals, using the finding's `analyse.py` shape (`/var/tmp/se-world-terms-out/`). Also count the `None`s by reason. Pre-2019 sign-ups have no quote (the supplier holds no rate to annualise against), so first renewals before 2020 are `None`. That share must be published, not dropped.
2. **Prediction, filed before the run.** The shock rate at tenure 1 is no longer 0. Its tenure gradient is far smaller than the old count's 0 vs 6.86 months. The 2022 first renewals of 2021 sign-ups are the most shocked cohort.
3. **Then swap** `_bill_shock_base` onto one event per year. Re-fit the level against the published band, which is an external anchor and not this tree's own output. Do not patch the yoy window.

## Gaps stated, not filled

- The materiality cut (15%) is inherited from the old count, not sourced. No published measure of what size of change a household notices exists.
- The "balance the household does not understand" half of definition A is a communication property. The world has no record of what the household was told.
- The fixed-versus-variable DD split is unpublished, so every DD household is treated as level-DD.

## Steps 1–2 done (2026-10-01, claim `measure-the-experienced-bill-shock-on-one-world`): the swap waits

One world was measured against a pre-registration (`57b505ca3`). Later renewals work: 32% are
shocked, there is no bill-size gradient (+0.029), and falls are no longer counted. Year one does
not work. The shock is defined at only 4 of 36 first renewals, because the quote is annualised at
a price cap that does not exist before 2019. **Step 3 (the swap) is blocked** until the opening DD
is priced at the rate the supplier sold at:
`SEAT_FINDING_THE_EXPERIENCED_BILL_SHOCK_IS_STILL_BLIND_IN_YEAR_ONE_BECAUSE_THE_QUOTE_IS_PRICED_AT_A_CAP_THAT_DID_NOT_EXIST_2026-10-01.md`.
