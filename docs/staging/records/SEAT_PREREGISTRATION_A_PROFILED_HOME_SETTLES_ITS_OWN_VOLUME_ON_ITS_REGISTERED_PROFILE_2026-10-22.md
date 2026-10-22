**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `a-profiled-home-settles-its-own-volume-on-its-registered-profile` (Lane 0 delivery)
**Knowledge:** imbalance-cashout-settlement

# Pre-registration: a profiled home settles its own volume on its registered profile

*Delivery seat, 22 Oct 2026. Written before any code for done-means step 2 of
`docs/staging/SEAT_FINDING_THE_RUN_SETTLES_EACH_HOMES_OWN_HALF_HOURS_WHERE_THE_PERIOD_SETTLED_A_PROFILE_2026-10-22.md`.
The numbers it predicts against are the rows of
`docs/staging/records/SEAT_RESULT_SETTLING_EACH_HOMES_OWN_SHAPE_AGAINST_THE_PROFILE_IS_NEAR_ZERO_FOR_THE_BOOK_AND_TENS_OF_POUNDS_FOR_AN_ELECTRICALLY_HEATED_HOME_2026-10-22.md`
and the PC2 re-run graded in the finding (`tools/profile_settlement_timing_probe` at e5d99e249).*

## What is being built

`hedged_settlement.run_hedged_term` and `run_deemed_term` take an optional `settled_shape`. When
it is given, the wholesale legs (hedged and unhedged volume, and the wholesale cost) are priced on
it, after it is trued up to the home's own volume over the priced periods of the term. Revenue,
levies, network, standing charge and `consumption_kwh` stay on the home's own shape: those are
billed on the meter, and the true-up keeps volume-priced charges equal.

`run_phase2b` passes it on the **fabric branch only**: a non-HH home whose demand is its own
fabric trace settles on `SHAPE_LOADERS[registered_profile_class(...)]`, the raw published GAD
table for its class. Three cases keep their own shape, each a stated choice:

- **HH-metered homes and I&C** (`is_hh_customer`). Their HH settlement was real. `run_flex_term` is
  not changed, because a flex term is an I&C term.
- **Legacy-path homes**, PC3 SMEs included. Their shape is already their class's profile,
  weather-adjusted and levelled. The 1997 GAD table has no temperature regression, which the
  period's profile coefficients did have (a GAP named on the knowledge page). Replacing a
  weather-adjusted profile by the raw table would trade one approximation of the period's
  coefficients for a worse one. **So the probe's PC3 +£100 a year does not move here.** It is the
  difference between the weather adjustment and the raw table, not own-trace timing.
- **A term on a time-of-use offer**, and the one term a mover carries across the move. A supplier
  pricing on time of use needed half-hourly data to settle it, and P300's Measurement Class F
  existed for that (four_front_door_domain_points §1). How many such homes were elected is a GAP.
  The carried term splices two homes' shapes and is left as it was.

## Predictions (P15), written before the build

Δ below is the probe's: own-shape SSP cost minus profiled SSP cost, gross. The build changes the
run's wholesale cost by **−Δ** on the unhedged share, so on a term with hedge fraction *h* by
about −Δ × (1 − *h*). A deemed term has *h* = 0.

- **P15a, wiring (exact).** For any one home and calendar year, `run_deemed_term` with and without
  `settled_shape` differs in total `wholesale_cost_gbp` by the probe's −Δ for that home-year, to
  £0.01. Revenue, every levy, network, standing charge and `consumption_kwh` are identical, row
  for row.
- **P15b, groups (gross, every home-year on a deemed-style full exposure).** Night-heavy
  electrically heated fabric homes, against PC2: wholesale cost **+£16.9** per full home-year
  (Δ −£16.9). Day-heated electrically heated fabric homes, against PC1: **−£37** per full home-year
  (Δ +£37.3). Gas-heated fabric homes: +£1.5 (Δ −£1.5), within ±£4. Legacy homes, HH homes and the
  PC3 SMEs: **£0.00**, exactly.
- **P15c, the book.** The probe's book figure (+0.24%, £3,096 on £1.306m) is NOT what moves in
  the run: about £2.6k of the +0.36% legacy PC1 term and the PC3 accounts' +£3.9k stay. Only the
  fabric groups move, so the run's gross wholesale cost on the non-HH electricity book changes by
  about **+£2,700** (night-heavy +£2,343, gas-heated +£3,453, no-fuel +£298, day-heated −£3,051,
  sum +£3,043, rounded down for the hedged share), between +£1,000 and +£3,100 once hedge
  fractions apply. Under 0.3% of the book's SSP cost in either direction.
- **P15d, direction.** For the per-customer value test this removes timing value the period did
  not settle. Day-heated homes lose about £37 a year of cost the run used to credit them with, and
  night-heavy homes gain about £17. Neither sign favours the thesis on the book.

## How it is graded

P15a and P15b by a through-settlement mode of `tools/profile_settlement_timing_probe` that calls
`run_deemed_term` per home and calendar year with and without `settled_shape`, over the same homes
the probe reads (about 12 minutes). P15c needs a run, and is graded on the first run published
after the build lands, against a control at the parent commit if one is run, else stated as
ungraded.

## Graded (same day, after the build; full book, one seed, 13 minutes)

`python3 -m tools.profile_settlement_timing_probe --through-settlement`, from the repo root, on
the shared tree carrying the build:

- **P15a holds.** 2,472 fabric home-years settled through `run_deemed_term` both ways. The largest
  gap between the writer's cost move and the probe's −Δ is £0.0000, and no row's revenue moved
  (£0.000000). The unit control
  `tests/simulation/test_a_profiled_home_is_billed_on_its_meter_and_bought_on_its_profile.py`
  holds the same contract for `run_hedged_term`.
- **P15b holds** on the three fabric groups: night-heavy electrically heated **+£16.9** per full
  home-year, day-heated electrically heated **−£37.3**, gas-heated **+£1.5**. The £0.00 legs
  (legacy, HH, PC3) are not measured by this mode. They hold by the wiring in `run_phase2b`, where
  only the fabric branch sets `settled_shape_fn`. That is a code reading, not a measurement.
- **P15c, gross part only.** The fabric groups move by +£3,030 gross (electrically heated −£721,
  gas-heated +£3,453, no fuel recorded +£298). The +£3,043 in the prediction summed the two
  electrically heated subgroups and missed the one home between them. The run-level figure, after
  hedge fractions, is **ungraded**: it needs a published run.
- **P15d holds** as stated. The two electric subgroups move in opposite directions and largely
  cancel (−£721 net).
