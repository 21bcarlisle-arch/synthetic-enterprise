**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** `EP1_clv_three_horizon` · **Item:** `the-dated-rate-moves-value-arm-margins-up-and-none-reach-a-bill`

# The dated discount rate moves four value-arm margins UP, and none of its 24 moves reaches a bill (25 Nov 2026)

Filed by the delivery seat, grading A4. The grade is on the pre-registration:
`docs/staging/records/SEAT_PREREG_A4_EP1_DATED_RATE_AS_A_VALUE_ARM_2026-11-24.md` §6. The raw output
is `/var/tmp/vte-driver/grade_ep1.out`, and the run is in `/var/tmp/vtn-out/ep1/`.

## What was measured

The run is VALID (V1 and V2 both held).

On book 61118, pair 13131/14141, the value arm priced 324 renewals on or after 2023-10-01. Setting
`renewal_discount_rate_dated=True` (12.3% in place of the flat 0.10) moved 24 of those 324 chosen
margins:

- 20 moved down and **4 moved up**, each by +£0.25/MWh.
- The up-moves:
  - PROS-2023-0273, electricity, 2024-09-25 (seed 13131);
  - PROS-2023-0350, electricity, 2024-11-24 (seed 14141);
  - SYN-2016-550, electricity, 2024-12-18 (seed 14141);
  - PROS-2020-0022, gas, 2024-01-30 (seed 14141).

The pre-registration's §2 argued that a higher rate can only move a margin down. Its reasoning was
that the annuity shrinks while the departure cost and stock loss are undiscounted, and the carrying
cost grows with the rate and with revenue. Four counter-examples refute that.

Not one value-arm household's net moved, to the penny. The ep1 − A gap is £0.000 on 0 moved units,
even though 22 of the 24 moved terms were retained households billed through the term.

## Two defects, or one defect and an equivalence: which has not been established

1. **The upward moves.** Either `decide_margin`'s objective has a term that rises with the discount
   rate and favours a higher margin, or §2 left out a term that legitimately does. Two candidates sit
   in `value_based_renewal._score`:
   - `cost_of_capital_annual=discount_rate` is fed into `expected_annual_costs`, which may enter the
     objective with a sign §2 did not trace;
   - the receivable and stock terms.

   I cannot yet say which. The one-variable probe: call `decide_margin` at the four terms' recorded
   inputs at 0.10 and at 0.123, and print each term of the objective at the two chosen margins.

2. **The zero reaching the bill.** All 24 moved offers are far above any 2023–25 default: 30–44 p/kWh
   for electricity and 15–25 p/kWh for gas, ex VAT.
   - In the world, a stayer offered a fix above its default refuses the fix and is billed the default
     (SLC 22C; see the comment near `company/pricing/value_based_renewal.py:936`).
   - On `VALUE_ARM_POLICY` the arm does not know this. `renewal_stayer_pays_at_most_default` is on
     only for `value_arm_capped` (`company/pricing/decision_policy.py:499`).
   - So the dated rate acts entirely inside the region where the arm scores margin that no stayer
     pays. If that holds term by term, the zero is an **equivalence**: the moved offers are never
     contracted at, so the realised A/B cannot see the switch on this policy.
   - Confirm it from the world's billed rate for the 22 retained terms. That is a read of the run, not
     a new run.

## What this changes

- **No arm takes `renewal_discount_rate_dated=True` until (1) is resolved.** This is the
  pre-registration's own §4 branch for an upward move.
- The knowledge case for the dated rate is unchanged: 12.3% is Ofgem's sourced figure for
  post-Oct-2023 terms, and 0.10 is not sourced.
- (2) applies beyond EP1. Any value-arm switch whose effect sits on above-default offers will grade as
  a zero on `VALUE_ARM_POLICY`. The next grade of such a switch should run on `value_arm_capped`, or
  state why it does not.

## Reverse

Revert this file and §6 of the pre-registration. Nothing on origin's code changed.

## Read beside

`the-retention-result-decomposed-and-checked-against-reality`, the director's 25 Nov puzzle: why
offering less does not make more money. Point (2) above is one candidate for part of the answer. An
arm that believes stayers pay above-default fixes misprices exactly the renewals where, in the world,
an offer above the default is no offer at all.
