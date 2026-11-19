**Severity:** LATENT · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality` · **Twin:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Pre-registration: the W2_36 ↔ D48 gas gap and its signed winter residual, by shape provider, on the first book carrying 4accbb828 (2026-11-19)

**When this was written, said plainly.** The first book carrying 4accbb828 is `run_output_67d454905c_20261119T184502Z.json`.
It finished on the shared disk at 20:35Z, and it is not on origin. Before this file was committed, I read only that book's
top-level key names, to confirm it exists. None of its values were read. So this commit comes after the book was
generated and before it landed. It is not a prediction written before the run. It is a prediction written before
the run was read.

## The premise, re-measured: 4accbb828 changes no settlement

The direction said this book is "the first chance to show that the gas residual was the world's and is gone".
That does not hold. 4accbb828 only *records* the incoming occupiers' `OCC-` legs in `gas_shape_provider_by_customer`.
Its own message says "No settlement changes: the leg was already on the fallback". The two things that would take
the fallback out are carrying the premise's split onto the occupier's leg and the 0.70 → ~0.85 recalibration.
Both are DIRECTION `not_now`. So the residual cannot be gone on this book.

What the book CAN show for the first time is where the residual sits, read from the run's own record instead of
inferred from absence. Other world changes landed between 6af7fd0bfd and 67d454905c, including ERA5 weather cells
(W1_14), W3_3 and stock-prepayment supply events. A whole-book move therefore cannot be attributed to 4accbb828.
The split by provider is the quantity that can be read.

## The baseline: 6af7fd0bfd, split by the provider each leg settled on

Method: `tools.couple_w2_36_d48.account_errors`, with the book-wide no-skill share s = 0.000379. The unknown last
run is t − b, as in `SEAT_PREREG_W2_36_D48_THE_SIGNED_RESIDUAL_BY_RUN_KIND_AND_MONTH_2026-11-19.md`. The
seasonal reading is Σ(t − b) / Σ run kWh over gas runs closed on an estimated final, split by the calendar month of
the last `period_end` (Dec–May against Jun–Nov). 95% intervals come from an account bootstrap with 4,000 resamples.
On 6af7fd0bfd, every gas account missing from the provider map (113 of 584) is an `OCC-` leg. They settled on the
population split unrecorded, which is exactly what 4accbb828 makes visible.

| gas class (6af7fd0bfd) | n | gap | Dec–May closed-final | Jun–Nov closed-final | open |
|---|---:|---|---|---|---|
| all gas | 584 | 0.255 [0.216, 0.296] | +3.6% [+0.9, +6.4] (102) | −6.3% [−10.3, −2.5] (108) | −4.0% [−6.6, −1.7] |
| fabric seasonal split (fallback out) | 112 | 0.311 [0.229, 0.413] | +0.8% [−3.3, +7.2] (20) | −5.4% [−15.4, +3.1] (22) | −4.5% [−10.3, −0.3] |
| 70/30 fallback, recorded | 359 | 0.238 [0.191, 0.293] | +2.6% [−1.0, +6.1] (64) | −5.6% [−10.0, −1.6] (74) | −4.3% [−8.3, −0.9] |
| 70/30 fallback, unrecorded (`OCC-`) | 113 | 0.247 [0.171, 0.342] | **+11.4% [+7.4, +15.2]** (18) | **−29.2% [−37.4, −23.9]** (12) | −2.5% [−7.0, −0.1] |

Read against its bounds: with the fallback legs out, the winter residual is not distinguishable from zero. With n = 20,
that is weak evidence, not a clean result. The bias that clears its bound is concentrated in the occupier legs.
Those are short tenancies, so an estimated final carries a large share of each one's run.

## Predictions for 67d454905c (graded with the same script, values first read after this commit)

- **P1, the mechanism check.** Every gas account billed appears in `gas_shape_provider_by_customer`, with 0 unmapped.
  The newly recorded legs are `OCC-` ids carrying `SETTLED_WITHOUT_A_SPLIT_OR_A_REFUSAL`.
- **P2, the residual is not gone.** On all gas, the Dec–May closed-final residual is positive, with its point in
  [+1, +7]%, and Jun–Nov is negative, with its point in [−11, −2]%. A Dec–May interval that includes 0 refutes this.
- **P3, the residual sits on the fallback.** On the fallback legs, recorded and `OCC-` together, the Dec–May minus
  Jun–Nov spread is between 6 and 16 points (11.1 on 6af7fd0bfd). That spread exceeds the fabric legs' spread. The
  fabric legs' Dec–May interval includes 0, with its point in [−3, +5]%.
- **P4, the gas gap.** On all gas, it falls in [0.20, 0.31]. On the fabric legs, it falls in [0.22, 0.42].

If P2 holds and P3 fails, the world's 70/30 fallback is not the carrier, and weather or the estimator comes back
into play (the Xoserve ALP record, Q2). If P3 holds, the W2_30 lever stays the one already named: the occupier's
split and the 0.70 → ~0.85 recalibration. Those wait on DIRECTION.

The grade will be appended below once the book lands. After that, the coupled gap ledger row is re-run with
`tools/couple_w2_36_d48.py`.

## Grade (appended after the book was read, 20:45Z, same day)

Book: `run_output_67d454905c_20261119T184502Z.json` (sha256 `c8c5ee97a1553ece…`, `producing_commit` 67d454905c).
I read it after this file's prediction reached origin as 0c1e91449 (20:42:33Z). Same script, same seed, same split.

| gas class (67d454905c) | n | gap | Dec–May closed-final | Jun–Nov closed-final | open |
|---|---:|---|---|---|---|
| all gas | 584 | 0.255 [0.217, 0.297] | +4.1% [+1.3, +6.9] (102) | −6.0% [−10.2, −2.4] (109) | −3.9% [−6.7, −1.6] |
| fabric seasonal split | 153 | 0.309 [0.235, 0.395] | +0.2% [−5.1, +5.9] (32) | −3.4% [−11.8, +3.9] (29) | −3.5% [−9.0, +0.7] |
| 70/30 fallback, all | 431 | 0.235 [0.192, 0.283] | +6.3% [+3.7, +9.0] (70) | −7.1% [−11.5, −2.9] (80) | −4.0% [−7.2, −1.4] |
| of which `OCC-` | 113 | 0.247 | +11.4% [+7.5, +15.6] (18) | −29.2% [−37.6, −23.6] (12) | −2.5% |
| of which not `OCC-` | 318 | 0.231 | +4.4% [+1.4, +7.6] (52) | −6.1% [−10.6, −1.8] (68) | −4.6% |

- **P1 held.** 0 gas accounts are unmapped. All 113 `OCC-` legs are in the map on `population_70_30_split`, and 113
  refusals carry the new reason.
- **P2 held.** The residual is not gone. It reads +4.1% in Dec–May and −6.0% in Jun–Nov, both inside their ranges.
- **P3 held.** The fallback legs' spread is 13.4 points, inside [6, 16]. The fabric legs' spread is 3.6 points. The
  fabric Dec–May point is +0.2%, and its interval includes 0.
- **P4 held.** The all-gas gap is 0.2552, and the fabric-leg gap is 0.3085.

**Seen, not pre-registered.**
- The fabric class grew from 112 legs to 153. So 41 legs that were on the fallback in 6af7fd0bfd now settle on a fitted
  split. I cannot yet say which change between the two commits did that. EPC register and ERA5 cells are the
  candidates. It means the two books do not hold the same legs in each class, and the class-level agreement is
  not a like-for-like comparison.
- The `OCC-` legs' figures are identical on both books. The occupier legs did not move.
- The bias is not only the occupiers. The non-`OCC-` fallback legs alone clear zero: +4.4% [+1.4, +7.6] in Dec–May.
  The fallback carries the residual. The fitted split does not show it at n = 32, which is weak evidence, not
  absence.

**Ledger.** The `W2_36_unbilled_energy_arises_the_way_it_does_in_reality` row of `coupled_gap_ledger.json` was
re-run on this book with HEAD's `tools/couple_w2_36_d48.py`. The overall gap moved from 0.2896 to 0.2873, gas from
0.2546 to 0.2552, and electricity from 0.4074 to 0.3883. Every interval overlaps.

**What follows.** The W2_30 lever is unchanged: carry the premise's split onto the occupier's leg, and recalibrate
0.70 → ~0.85. Both are DIRECTION `not_now`. This grade is the evidence to bring when that is re-opened: the
fallback legs carry a 13-point seasonal swing, and the fitted ones carry none that clears its bound.
