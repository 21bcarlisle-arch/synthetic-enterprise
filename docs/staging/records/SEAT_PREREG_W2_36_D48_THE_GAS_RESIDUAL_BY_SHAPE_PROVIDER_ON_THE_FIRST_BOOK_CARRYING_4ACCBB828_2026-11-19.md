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
