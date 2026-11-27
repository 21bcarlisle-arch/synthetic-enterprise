**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** `EP1_clv_three_horizon` · **Claim:** `ep1-a4-regrade-on-the-fixed-dice-is-queued`

# Pre-registration: the EP1 A4 re-grade on the fixed dice and the refit fix-0 world (27 Nov 2026)

**Filed before the run exists.** At filing time `/var/tmp/se-fix0-anchor-refit-landed.sha` did not exist, the
rankq re-grade (`the-rankq-regrade-launches-on-the-refit-fix-0-world`) had not launched, and nothing had been run
for this record. The void A4 grade is §6 of `SEAT_PREREG_A4_EP1_DATED_RATE_AS_A_VALUE_ARM_2026-11-24.md` (`20b14f3ed`).
It was voided by `SEAT_FINDING_AN_OFFERED_LEAVER_IS_ANSWERED_ON_A_DIE_THE_FLOOR_DID_NOT_REDRAW_2026-11-25.md` §2: under
`noise_floor(redraw_key="churn_roll")`, a retention offer was answered on the un-redrawn roll. The priors below come
from the void files, read as evidence only.

**Correction beside the item's wording.** The item describes A4 as "the forward CLV three-horizon ranking against
realised held-back value". A4 does not measure that. A4 measures one switch, `renewal_discount_rate_dated` (12.3% from
Oct 2023 in place of the flat 0.10), set on the value arm only, as `ep1 − A` on one book. The held-back ranking test
is the EP1 family pre-registered on 1 Oct (`SEAT_PREREGISTRATION_EP1_*_2026-10-01.md`), and the dice fix does not
void it, because it makes no retention offers. This record re-grades A4 as A4 was. The item's per-horizon ranges are
therefore not filed: A4 has no horizons to range.

## For the director, in plain English

On the faulty harness, the newer, sourced discount rate changed 24 renewal prices and not one penny of anyone's
bill. Four of those prices moved the wrong way, which is a defect still open on `decide_margin`. I predict the fixed
harness changes neither result. The dice fault was in how a retention offer is answered, and this switch never
decides whether an offer is made. Its price moves sit on fixes priced above the default, which in the world nobody
contracts at. The re-run is still worth doing, because no number from the old harness may be quoted. It costs one
box slot after the rankq re-grade.

## 1. What is run

- **Two configurations, `A` and `ep1`,** on the refit base. The void `A` (`/var/tmp/vtn-out/A/`, digest
  `cdba75ebb9197b33`) is **not** a comparator. A refit-world file has a different `world_identity.digest`, and
  `SEAT_PREREG_THE_RANKQ_REGRADE_ON_THE_REFIT_FIX0_WORLD_2026-11-27.md` §3 refuses a comparison across digests. The
  rankq re-grade runs only `twin` and `rankq`, so `A` must be re-run here.
- **Same book, same pair, same shape as `20b14f3ed`:** book 61118, churn-roll floor pair 13131/14141, the s.12g
  driver shape. `ep1` = A's switches (`renewal_belief_by_ending_term=True`, `retention_cut_at_the_flips=False`) plus
  `renewal_discount_rate_dated=True` on `VALUE_ARM_POLICY` only. The policy is **not** `value_arm_capped`. This is
  a replication of the void grade. Running on the capped policy would ask a different question, and that is §5's
  successor.
- **The base is the sha in `/var/tmp/se-fix0-anchor-refit-landed.sha`** (or the descendant the rankq launch names),
  in a fresh detached worktree. The base must contain the dice fix:
  `tests/simulation/test_an_offer_is_answered_on_the_roll_the_floor_redrew.py` is present and passes there.
- **The patch is re-ported, then re-pinned before launch.** `/var/tmp/vte-driver/ep1.patch` (`1ca5b5b0…`) was cut
  against `870201d1e7` plus `rankq.patch`, so it will not apply byte-for-byte to the refit base. The launching tick:
  - ports it onto that base, touching only the three decision-path pieces listed in the void record §1;
  - writes the new patch's sha256 into §7 below;
  - lands that line on origin **before** the launch.

  The driver keeps its rule that it refuses any other diff.
- **The grader is `grade_ep1.py`, unchanged** (household unit, 2,000 resamples, seed 20261117, the control arm's
  household-years as the divisor), plus the in-run shadow at 0.10 for every value-arm renewal on or after
  2023-10-01, exactly as before. The one exception: its input directories point at the new output root.
- **Admission.** One long job at a time. The wrapper waits until the rankq re-grade's unit is gone and no land10,
  seed_family, census or value-test unit is live, as `run_ep1.sh`'s `busy()` did. It refuses after 96 h.
  The last ep1 run took about 14 h at a peak of 11.8 GB.

## 2. Why the fix should not move A4 (before any number)

- The fault changed **whether an offered household stays**. The switch changes **the margin on a value-arm renewal
  quote**. The two meet only when a moved margin changes P(stay) enough to cross the roll. On the void run, the
  moves were ±£0.25 to £0.50/MWh on quotes far above the default. The P(stay) change was of order 0.001 against
  rolls of 0.82 and 0.67 at p ≈ 0.03. Over about 24 moved terms, the expected number of crossings is of order 0.02.
- `decide_margin` is deterministic given its inputs. The upward moves come from its objective, not from the dice.
  They should recur wherever the same household reaches the same renewal.
- The refit moves about 15% of departure decisions (the rankq record's estimate). Those decisions change which
  households reach post-Oct-2023 renewals, so they change the **count** of shadow-priced renewals. They do not
  change the mechanism.

## 3. Predictions

| | Measure | Predicted | Wrong if |
|---|---|---|---|
| **V1** | Control arm `ep1` against `A`, same base: households whose net moved; seeds whose control decisions differ | **0 and 0** | Any non-zero. The run is then VOID as a one-variable arm, and nothing below is graded |
| **V2** | Value-arm renewals and scored decisions dated before 2023-10-01, `ep1` against `A` | **all identical** | Any difference. VOID, as V1 |
| **P0** | Value-arm renewals shadow-priced on or after 2023-10-01, both seeds | **324, in the range 250 to 400** | Outside the range. This is not a refutation: it says the refit changed who renews more than §2 assumes, and P1 to P3 are read with that beside them |
| **P1** | Share of P0 whose chosen margin moves | **0.07 (0.03 to 0.15)** | Above 0.25 (the void rule), or an empty shadow log |
| **P2** | Upward moves among P1's moved margins | **at least 1. Point 4 (range 1 to 8).** Each of the four void up-movers that reaches the same renewal date moves up again | **0 upward moves.** The `decide_margin` defect would then have been a property of the faulty run's states, not of the objective, and the open finding is re-read against this run before its probe |
| **P3 (primary)** | `ep1 − A` whole advantage, £ per household-year, mean of seeds, 95% interval | **+£0.000 on 0 moved units**, interval exactly [0, 0] | Any moved unit. Read `\|point\| ≤ 0.50` as STRADDLE and anything beyond as ABOVE or BELOW by the void record's §4 rules. A moved unit means a dated-rate price reached a bill on this policy, and the "equivalence" reading of the open finding's point (2) is refuted |
| **P4** | Moved terms whose household was billed the default rather than the moved fix (from the world's billed rate) | **all of them** | Any moved term billed at its moved fix. That contradicts the SLC 22C stayer rule the open finding relies on |

P3 is predicted to be vacuous again, as it was on the void run. If it is, the record says so: it is evidence that
this policy cannot see the switch, not that the switch does nothing.

## 4. What each outcome changes

- **As predicted (V holds, P2 at least 1, P3 zero).** The void grade's reading stands on valid code. No arm takes
  `renewal_discount_rate_dated=True` until the open finding
  `seat-finding-the-dated-rate-moves-four-value-arm-margins-up-and-none-of-its-moves-reach-a-bill` is resolved by
  its own probe. The standing switch `EP1_DATED_DISCOUNT_RATE_IN_THE_STANDING_POLICY` stays `False`.
- **P2 refuted (no upward move).** The defect finding is re-read against this run before its probe is spent.
  Nothing is adopted on that alone, because P3 is still blind on this policy.
- **P3 refuted (a moved unit).** The equivalence reading fails. The moved units are listed by billed rate, and the
  open finding's point (2) is re-opened.
- **VOID (V1 or V2 fails).** The patch port is suspect first. Check it before the harness.

## 5. Successor, not part of this run

The question this policy cannot answer is whether the dated rate changes **what a household pays**. That needs the
arm that knows a stayer pays at most the default: `value_arm_capped`, where `renewal_stayer_pays_at_most_default` is
`True` (`company/pricing/decision_policy.py`). It also needs the `decide_margin` defect resolved first. That run gets
its own pre-registration after this one is graded. It is not added here, because one run should answer one stated
question (R5).

## 6. What the reader does

1. Check that both configurations' `producing_commit` is the §1 base, that they share one
   `world_identity.digest`, and that the digest is not `cdba75ebb9197b33`. Check that the patch sha in §7 matches
   the run's.
2. Grade V1 and V2, then P0 to P4, one line each, `held` or `missed`, quoting `grade_ep1.out`.
3. **If the launch came first** (it started before §7's pin line was on origin), this record is graded **void,
   filed late**, and the miss is written here.

## 7. Pin (written by the launching tick, before launch)

- Base sha: *(not yet)*
- Re-ported `ep1.patch` sha256: *(not yet)*

## Reverse

Nothing to reverse yet. This is a record. It changes no code and launches nothing. After a launch:
`systemctl --user stop longjob-<job>`, then remove that run's output root and its worktree.
