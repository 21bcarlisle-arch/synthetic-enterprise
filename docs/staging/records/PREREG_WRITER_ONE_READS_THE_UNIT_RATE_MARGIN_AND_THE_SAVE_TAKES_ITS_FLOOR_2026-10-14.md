**Severity:** ADVISORY · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** none — Lane 0 delivery
**Knowledge:** acquisition-and-retention-economics

# Pre-registration: writer 1 reads the unit-rate margin against its own strike's margin, and the save takes writer 1's floor

**Claim:** `writer-one-margin-basis-and-one-floor-for-the-save`
**Written 2026-10-14 before either run below produced an artefact.** The diagnosis it tests is
`docs/staging/SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_BECAUSE_THE_FLOOR_CARRIES_THE_STANDING_CHARGES_NETWORK_AND_THE_PREMIUM_READS_THE_STANDING_CHARGE_AS_MARGIN_2026-10-14.md`
(d30dafffe). The knowledge page amended first (K8) is `acquisition-and-retention-economics`.

## What changes

1. **The measurement.** A completed term teaches the portfolio premium its margin over revenue with
   its standing-charge revenue taken out of BOTH (`standing_charge_gbp` on electricity rows,
   `gas_standing_charge_gbp` on gas rows). Before, the ratio counted the standing charge as margin
   with no cost against it.
2. **The target.** The 8% literal (`PORTFOLIO_TARGET_MARGIN_RATE`, no source) is replaced, for
   writer 1, by the margin each term's own strike priced for on the same basis:
   `TARGET_MARGIN_GBP_PER_MWH` x the term's MWh over its unit-rate revenue. The premium compares the
   lookback's mean realised rate with the lookback's mean priced-for rate.
3. **One floor.** `run_phase2b._price_match_inputs` hands the save and the renewal cut
   `renewal_desk.pre_margin_unit_rate` (forward + capital + the two locked costs), the floor writer 1
   already stops at, instead of forward + the two locked costs.

The world's network schedule (fix 2) is not touched.

## Runs

Both are `tools.save_on_loss_notice_arms run on ... --scale 1`, seed 61109, 400 founders, budget 0,
to 2025-06-07, through `/var/tmp/regrade/seeded_arm.py` — the same arm and inputs that produced
`/var/tmp/floor-recount-out/sv-k1-61109.json` at d55598dd6 (0 save offers).

- **O** — origin `58e1e8905`, unchanged: `/var/tmp/w1-basis-out/origin-sv-k1-61109.json`.
- **F** — origin + this change: `/var/tmp/w1-basis-out/fix-sv-k1-61109.json`.

## Predictions

- **P1 (the finding's own, graded on O).** On O the save makes **at least 1** offer on seed 61109
  (it made 0 at d55598dd6). If 0, the finding's two-floors account of the inert save is incomplete.
- **P2 (the basis, on F).** On electricity, the mean realised margin rate writer 1 reads is between
  **-5% and +5%** on at least three quarters of the priced renewals (it read 18-20% on the old
  basis), and the priced-for target it is compared with is between **0.5% and 3%**.
- **P3 (the discount, on F).** The full -5% (`PORTFOLIO_PREMIUM_MIN`) is taken on **fewer than a
  quarter** of electricity renewals that writer 1 prices, against nearly all of them before.
- **P4 (the floor, on F).** Fewer than **half** of the held electricity renewals sit on the floor to
  the penny (21 of 21 at d55598dd6).
- **P5 (the save, on F).** The save makes **at least as many** offers on F as on O.
- **P6 (the book, F against O).** `total_net` is **higher** on F than on O: the book stops
  discounting 5% into its own cost. Not a target: a direction, stated so it can be wrong.

If P2 fails high (the unit-basis margin still reads well above its target), something other than
the standing charge is carrying margin the premium reads, and that is the next finding.
