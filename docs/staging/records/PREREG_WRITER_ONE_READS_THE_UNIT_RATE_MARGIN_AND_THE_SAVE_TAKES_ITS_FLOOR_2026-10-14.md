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
  > **GRADE P1 — HELD.** O makes **2** save offers on seed 61109 (038 at 238.30, 227 at 251.06,
  > both on the save's old floor), against 0 at d55598dd6. 7 invitations held, 0 saved.
- **P2 (the basis, on F).** On electricity, the mean realised margin rate writer 1 reads is between
  **-5% and +5%** on at least three quarters of the priced renewals (it read 18-20% on the old
  basis), and the priced-for target it is compared with is between **0.5% and 3%**.
  > **GRADE P2 — FAILED (first half), HELD (second half).** The band: the mean realised rate is
  > in [-5%, +5%] on **26%** of F's electricity fixed terms carrying a position (98 of 375), 27% of all
  > electricity rows with one (1,346 of 4,989) -- not three quarters. It failed WIDE and, on the
  > fixed terms, HIGH: fixed median **8.5%** (25.5% on O), all-rows median 0.15% (18.3% on O), p10
  > -45% and p90 +25% on all rows. By year on fixed terms F reads 14-18% in 2019, 2020, 2023 and
  > 2024. The target: read exactly where the premium is unclamped (target = mean + 2 x premium,
  > `compute_portfolio_premium`, half-life 0.5): median **1.67%** on fixed terms, 230 of 230 in
  > [0.5%, 3%]; 2,848 of 2,966 on all rows. On O it is 8.00% on every unclamped row, the literal.
  > The artefact does not carry `target_margin_rate` (`_STATE_KEYS` omits it), so clamped rows'
  > targets are unread. The fail-high clause below is triggered: see the finding it names.
- **P3 (the discount, on F).** The full -5% (`PORTFOLIO_PREMIUM_MIN`) is taken on **fewer than a
  quarter** of electricity renewals that writer 1 prices, against nearly all of them before.
  > **GRADE P3 — FAILED.** The full -5% is taken on **38%** of F's electricity fixed terms
  > carrying a position (144 of 375), 26% of all electricity rows (1,316 of 4,989) -- not under a
  > quarter on either population. Against O it fell from 80% (306 of 384) and 51% (2,508 of 4,933).
  > It moved the predicted way and stopped short, by the P2 fail-high.
- **P4 (the floor, on F).** Fewer than **half** of the held electricity renewals sit on the floor to
  the penny (21 of 21 at d55598dd6).
  > **GRADE P4 — HELD.** 0 of 4 held electricity renewals on F sit on writer 1's floor
  > (`cost_floor`, now forward + capital + the two locked costs): they sit 1.62 to 13.19 above it.
  > On O, at the same customers and dates, 4 of 4 sat on that same floor to the penny (each O
  > renewal equals F's floor: 196.62, 242.41, 255.54, 214.92). The comparison is on one floor;
  > O's own `cost_floor` is the save's old one (forward + locked costs) and reads 0 of 4 only
  > because it sits capital below. Not predicted, and outside P4's electricity scope: 2 of 3 held
  > GAS renewals sit on the floor on F (045 at a -5% premium on a 13.7% gas margin; 179 at a
  > premium of +0.03% and still 2.8% under its strike, so something other than the premium cut it).
- **P5 (the save, on F).** The save makes **at least as many** offers on F as on O.
  > **GRADE P5 — HELD.** F makes 3 save offers (038 at 242.41, 227 at 255.54, 264 at 221.39)
  > against O's 2. Neither arm saves anyone: 0 of 7 held on both.
- **P6 (the book, F against O).** `total_net` is **higher** on F than on O: the book stops
  discounting 5% into its own cost. Not a target: a direction, stated so it can be wrong.
  > **GRADE P6 — HELD.** `total_net` F 265,429 against O 252,224 (+13,205, +5.2%); gross
  > 781,060 against 764,545. One seed, and two things changed (the basis and the save's floor), so
  > this says the direction, not which change moved it.

If P2 fails high (the unit-basis margin still reads well above its target), something other than
the standing charge is carrying margin the premium reads, and that is the next finding.

## Grade (2026-10-14, seed 61109)

Graded after both arms finished (11:13Z), from `/var/tmp/w1-basis-out/origin-sv-k1-61109.json` (head
58e1e8905) and `fix-sv-k1-61109.json` (head 72ab9d113). The text above each grade is the pre-registered
blob of e3b5ed01a (sha256 be5167a1); the grades are inserted, nothing above them was edited. Read by
`/var/tmp/w1-basis-out/grade.py`; the held rows by `floor_table_f.py` (floor_table.py's columns, with the
forward taken from O's floor because F's floor already carries capital).

**4 of 6 held; P2's band and P3 failed.** The basis did what it was for: the target is what the strike
priced for (about 1-2%, not 8%), the held renewals left the floor, the save offers, and the book nets
more. But the realised unit-rate margin writer 1 reads is still well above that target on fixed terms,
so the full discount still lands on 38% of them. Per this pre-registration's own clause, that is the
next finding: `docs/staging/SEAT_FINDING_THE_UNIT_RATE_MARGIN_STILL_READS_ABOVE_ITS_TARGET_ON_FIXED_TERMS_2026-10-14.md`.

The re-take of the renewal-cut decision (d5ba38b12) and the save on this basis is not filed again
here: it is already running as regrade5 (`/var/tmp/regrade5`, base carries e3b5ed01a) and queued as
the continuation `grade-regrade5-arms-once-finished`. Its save reading also waits on the red stayers
control (focus one).
