**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: what the 16 Nov book grades on INV_DUAL_FUEL_TRADITIONAL_READS_TAKEN_TOGETHER (2026-11-13)

Filed 13 Nov 04:30, before the book exists. The 16 Nov book publishes at 04:00 that day. It is the first book built
on a base that includes b3ff041f0, N30's world fix. Claim `n30-grade-on-post-fix-book` was drawn on 13 Nov, before
there was anything to grade. So this turn files the prediction, and the grading is handed on with a not-before time.

## The quantity

This is the row's own `counts`, unchanged. Take every bill period (matched on `period_end`) that both fuel legs of
one household bill, with `meter_type` Traditional on both legs. Of the periods with an actual read (A, M or C) on
either fuel, the share with an actual read on exactly one fuel. The numerator and the denominator are both bill
periods of one household's traditional pair. Neither is an account count.

## Arithmetic, done before the answer

p is one fuel's monthly actual-read rate, about 0.2 (the cold read's 6,043 / 16,271 pairs with any read gives
2p − p² ≈ 0.37). The register belief is t = 0.8 (`q6_dual_fuel_read_together_share`). Assume the two legs' read
classes coincide.
- any read: t·p + (1−t)(2p − p²) ≈ 0.16 + 0.2·0.36 = 0.232 (was 0.36)
- one only: (1−t)(2p − 2p²) ≈ 0.2·0.32 = 0.064
- s ≈ 0.064 / 0.232 ≈ **0.28**. The world draw measured 0.286 on 480,000 pairs (b3ff041f0).

## Predictions

| # | prediction | refuted if |
|---|---|---|
| P1 | s lies in 0.22–0.36 | outside it |
| P2 | the row grades CLEAN: not BREACHED above 0.5, not FLAGGED below 0.09 | any BREACH or FLAG on this row |
| P3 | traditional pairs billed on both legs stay within ±15% of the 6fe7827ab2 book's 16,271. The fix moves reads, not supply. | outside it |
| P4 | pairs with any read fall to about 0.64× the old 6,043, so 3,000–5,000 | outside it |
| P5 | smart/smart one-only stays near 12%. The fix leaves smart reads alone. | above 20% or below 5% |

## If refuted, in the order to check

1. s near 0.89: the book was not built on a base carrying b3ff041f0. Read the book's build commit first.
2. s in 0.5–0.89: the fix reached the world, but something in the company's or the ledger's read path splits the
   legs again. For example, a C read rejected on one fuel, or the hard-to-read class keyed per leg (the finding's
   second cause, which is still per leg). Measure that share before blaming the belief.
3. P3 or P4 off and P1 holding: the pair matching on `period_end` has moved, not the reads.

## Done means

The runner has graded this row on the 16 Nov book. The result is written beside these predictions, with each P
marked held or refuted. If the row is CLEAN, the N30 staging finding closes as its own status section says.
Leg three of the twelfth cold read is then free to proceed.

## Amendment, 2026-11-14: what the insulation change (e17ebc596) moves, before the book exists

This amendment is about e17ebc596 only. It changes the world's insulation draw after P1–P5 were filed. The one-variable book A/B, e17ebc596^ against e17ebc596, same seed, neither arm carrying ceeefa5960 or 69866925b (`docs/staging/records/SEAT_RECORD_WHAT_THE_INSULATION_CHANGE_CAN_MOVE_IN_THE_16_NOV_PREREGISTRATIONS_2026-11-13.md`).
P1–P5 are kept as filed. **Fabric can move these figures, and on the run it moves each by well inside its band.**

| | e17ebc596^ | e17ebc596 | now predicts |
|---|---:|---:|---|
| P1 s | 0.2706 | 0.2740 | 0.22–0.36, unchanged (shift +0.003) |
| P2 row | CLEAN | CLEAN | CLEAN, unchanged |
| P3 traditional pairs billed both | 16,244 | 16,195 | ±15% of **16,222** (the shift is −49, and the band is unchanged in practice) |
| P4 pairs with a read | 3,873 | 3,843 | 3,000–5,000, unchanged (shift −30) |
| P5 smart/smart one-only | 6.9% (214 of 3,098) | 6.2% (165 of 2,655) | 5–20%, unchanged. Note that the smart pair count falls 12%, because the campaign's replaced homes change who is smart dual fuel |

Neither arm has ever read P5's "near 12%": 6.9% and 6.2%. That is a read, not a grade.

**Reverse.** Delete this file.
