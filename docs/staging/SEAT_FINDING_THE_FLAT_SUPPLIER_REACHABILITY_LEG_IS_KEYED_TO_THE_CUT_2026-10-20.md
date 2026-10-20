**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` · **Claim:** `repair-the-flat-supplier-reachability-leg` (Lane 0 delivery)

# The flat supplier's reachability leg is keyed to the cut, not to an offer

Repairs `SEAT_FINDING_THE_FLAT_SUPPLIER_REACHABILITY_LEG_IS_RED_ON_ORIGIN_BECAUSE_THE_GUARD_NOW_OFFERS_NOTHING_IN_2016_2026-10-20`
(moved to `done/`). Delivery seat, 2026-10-20.

## The inherited diagnosis was half right

That finding said the 2016 window went empty because `c61d8b608` made the guard stop offering.
Pre-registered, then measured on a clean `origin/main` worktree (`711359a8c`):

| window to | arm | renewals | churners withheld by reason | offers |
|---|---|---|---|---|
| 2016-12-31 | current | 3 | below_threshold 2 | 0 |
| 2016-12-31 | flat | 3 | below_threshold 2 | 0 |
| 2017-12-31 | current | 86 | below_threshold 8, uneconomical 23 | 1 (2017-11-15) |
| 2017-12-31 | flat | 86 | below_threshold 8, the_fix_has_no_room_above_its_cost_floor 23 | 0 |

My first prediction ("current reaches the cut in 2016") was refuted. No renewal in 2016 got past
the churn threshold, so the guard was never asked on either arm. The window was too short to test
the flat arm whatever the guard did. `c61d8b608` only removed the offers that had been hiding this.

## The repair

`tests/company/policy/test_the_flat_supplier_policy_makes_no_retention_offer.py` now runs to
2017-12-31, the truncated window `tests/simulation/test_run_phase2b_event_log.py` already uses.
It asserts that each branch was taken before asserting the zero:

- **current reaches the cut**: offers plus churners withheld after the cut, > 0. This does not
  depend on whether the guard finds the offer economic, so a future change to the guard's
  economics does not empty it the way the offer count was emptied.
- **flat stops renewals at the cut**: at least one `the_fix_has_no_room_above_its_cost_floor`.
- **flat offers nothing and sizes no cut**: offers (0, 0), and no withheld reason outside
  `STOPPED_BEFORE_THE_CUT`. That set lists the reasons that stop a renewal before the cut, so
  an unknown new reason counts against flat (fails closed).

Mutation: a "flat" arm with `retention_tiers=((0.0, 0.03),)` (a 3% cut at every belief) reads
`offers (5, 5), past_the_cut 21, no_room 0`: KILLED on all three flat assertions. The repaired
module passes on `711359a8c` (4 passed, 12m19s).

## Cost, and what is still blind

The module now takes ~12 minutes (two 2017 runs), up from ~4. Only churners carry a withheld
reason (`no_offer_churn_log`), so a cut sized on a renewal that rolls is visible only if it
becomes an offer. The control has 23 churners on each arm to read, so this costs no sensitivity
today.
