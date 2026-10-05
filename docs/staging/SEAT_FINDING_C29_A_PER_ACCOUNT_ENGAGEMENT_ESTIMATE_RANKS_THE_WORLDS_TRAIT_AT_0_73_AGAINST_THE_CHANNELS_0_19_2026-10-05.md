**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables`

# A per-account engagement estimate ranks the world's trait at ρ 0.73. The channel alone gets 0.19.

Claim `c29-build-a-per-account-engagement-estimate-graded-against-the-world`. These are results against
`docs/staging/records/SEAT_PREREGISTRATION_C29_DOES_A_PER_ACCOUNT_ENGAGEMENT_ESTIMATE_RANK_BETTER_THAN_THE_CHANNEL_2026-10-05.md`,
which was written before anything was measured. At draw time the duplicate-work note named this same
id as already held. The only holder was this invocation, so the note was the draw's own write and
not a rival's.

## What was built

- `company/crm/engagement_estimate.py` estimates P(this household enters a choice at a renewal) from
  two things the supplier holds: its payment method, and its own term record at each anniversary.
  At an anniversary the account either started a fixed term or left (it CHOSE), or it went onto the
  default (it ROLLED). The estimator is an empirical-Bayes beta-binomial. Its prior mean is the
  channel's pooled rate on the book. Its prior strength is a method-of-moments fit of the
  within-channel spread beyond noise. With no excess spread the strength is `None` and every account
  sits at its channel rate. No constant is picked, and no decision reads the estimate yet.
- `tools/c29_engagement_ranking.py` provides three arms: the run's own book, a world-roll arm
  (planted), and a channel-rate roll arm (null).
- `tests/company/test_the_per_account_engagement_estimate_ranks_better_than_the_channel_alone.py` is the
  control named on C29's row. It has 8 legs, and every leg's mutation turns red. Two mutations
  stayed green on the first draft and both were missing tests: a no-op shuffle in the book null, and
  a null that flattened the channels. Both now have legs.

## Results (run `run_output_70dee3c7c_20261004T223734Z`, 108 electricity households)

| Prediction | Registered | Measured | Verdict |
|---|---|---|---|
| P1 channel-alone ρ | in [−0.05, +0.25] | +0.189 | held |
| P2 estimate ρ, lift | ≈0.55, lift ≥ 0.25 | **+0.734, lift +0.545** | held; I under-predicted the size |
| P3 share with no anniversary | ≥ 30% | **10 of 108 (9%)** | **refuted.** The book is older than I assumed. |
| P4 null lift | within ±0.10 of 0 | **book null band −0.32 to +0.05, median −0.15** | **refuted as worded.** Shuffling the record does not cancel to zero. It makes the estimate WORSE than the channel, because the shrinkage now pulls accounts toward noise. The real lift sits far above the band, which is the comparison that matters. The world null arm (5 anniversaries at channel rate) gives exactly 0.000: the moment fit finds no spread and collapses onto the channel. |
| P5 planted lift, 5 anniversaries | ≥ 0.30 | +0.740 | held |

The company's channel matched the world's on 108 of 108 households.

## What it means, and what it does not

- The frame's refutation condition (lift < 0.10) is not met. A supplier's own renewal record carries
  a per-account engagement signal well beyond payment channel. Decision #1, the retention discount,
  can be made per-account on engagement. #5, dunning, is not yet needed as the fallback.
- **This is by construction, and the size should be read that way.** The world's archetype
  probabilities (0.65 / 0.15 / 0.02) persist across a household's whole tenure and are re-rolled at
  every anniversary. Any repeated observation of the roll will recover them. The real question is
  whether that persistence is TRUE OF HOUSEHOLDS. Ofgem's own finding is that a minority switch
  repeatedly while most never do, which points the same way. Whether the spread is this wide is not
  established here, and the lift scales with it. Before a decision reads the estimate, the
  per-archetype probabilities need their sources checked in the knowledge layer.
- Elasticity is untouched. The estimate says who will LOOK. Whether a discount moves them once they
  look is the second trait, and the discount size remains a value question (PB5, and the frame's
  ban on per-band discounts).

## Next

C29's next increment is to make the retention decision read engagement. A discount offered to an
account the estimate says will not look is a transfer. The test for that increment must show the
transfer falls without the retained margin falling. Before it, check the sources for the
per-archetype probabilities.
