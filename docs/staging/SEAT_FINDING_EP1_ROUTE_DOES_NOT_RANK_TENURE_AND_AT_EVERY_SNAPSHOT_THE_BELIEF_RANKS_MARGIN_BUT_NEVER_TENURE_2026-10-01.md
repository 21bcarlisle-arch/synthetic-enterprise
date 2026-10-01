**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# EP1: acquisition route does not rank tenure, and at every snapshot the belief ranks forward margin but never tenure

Claim `ep1-acquisition-channel-arm-and-every-snapshot-grade`. The duplicate-work note on the draw
named this very id. That was the draw's own write: there was no rival seat or `surgical_land` on
it at draw time, so the work was done rather than disposed of.

The predictions were filed first. The results, the instrument and the wrong predictions sit
beside them in
`docs/staging/records/SEAT_PREREGISTRATION_EP1_ACQUISITION_ROUTE_ARM_AND_EVERY_SNAPSHOT_GRADE_2026-10-01.md`.
No code changed. The predecessor's two open questions (channel; every snapshot) are answered here, so it moves to `docs/staging/done/SEAT_FINDING_EP1_OVER_THE_WHOLE_BOOK_NOTHING_A_SUPPLIER_HOLDS_AT_FIRST_VALUATION_RANKS_TENURE_WITHIN_A_COHORT_2026-10-01.md`.

## What was found

1. **This world has no price-comparison channel, and the route it does have carries no tenure
   signal by construction.**
   - The only routes are founding roster, won prospect (`PROS-*`), curriculum arrival (`SYN-*`)
     and successor.
   - Every disposition the world's renewal hazard reads is a hash of the customer id, so none of
     them reads the route.
   - Within the 2017 cohort, the only cohort with mixed routes, won prospects score C 0.492
     inside [0.443, 0.558].
   - The industry's best-known tenure predictor therefore **cannot be learned here, because the
     world does not hold it**. That is a fidelity question for the world's lane, and it is for
     that lane to weigh blind to this result. It is not a company defect.
2. **At later snapshots the belief's inputs vary per account, and still nothing ranks tenure.**
   - p_c is off the 0.05 floor on 71% of snapshots and scores C 0.503.
   - L_b varies by tenure position and scores 0.516.
   - The belief itself scores 0.479.
   - These are 315 later snapshots, read on a per-account cluster null.
   - **The company's churn model has no within-year ranking power over tenure at any point in an
     account's life.** That holds for the model, not only for EP1's use of it.
3. **The belief DOES rank forward margin.**
   - Its margin term scores within-cutoff Spearman +0.427 against margin settled after the
     cutoff, with cluster CI [+0.28, +0.54].
   - At first valuation it was +0.071 against the whole-life rate. The forward, per-year target
     is the honest one, and it reads +0.257 at first valuation.
   - What the belief knows about an account's value is margin persistence, not tenure.
4. **…and the naive margin rate observed to date ranks forward margin better** than the belief's
   margin term.
   - The gap is +0.084, paired cluster CI [+0.046, +0.128].
   - The two orderings agree at 0.954.
   - The gap is **not yet attributed**. The belief subtracts cost to serve and the target does
     not, and its form also differs. Prediction: the gap is the cost-to-serve subtraction, filed
     before the control.
5. **An instrument lesson.**
   - Tenure position reads C 0.447, outside the stratified permutation band. Its per-account
     cluster CI [0.387, 0.509] contains 0.5.
   - A grade over repeated account-snapshots that used the plain permutation null would have
     published that as a result.

## What this settles

- EP1's tenure-blindness is not confined to first valuation, and it is not a missing input.
  Supplying per-account tenure and churn probability does not make the belief rank tenure,
  because those inputs do not rank it either.
- The remaining lever on the tenure side is world fidelity (PB4's first-year hazard re-derivation,
  and whether acquisition route should carry engagement). It is not company code.
- On the margin side, the belief works. The next question is whether its form costs ranking
  against the naive rate once cost to serve is put on both sides.
