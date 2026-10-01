**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# EP1's belief carries no per-account tenure, and no snapshot observable ranks a lifetime margin at n = 66

Claim `ep1-what-ranks-a-lifetime-margin`. The predictions were filed first and the results sit
beside them in
`docs/staging/records/SEAT_PREREGISTRATION_EP1_WHICH_SNAPSHOT_OBSERVABLE_RANKS_A_LIFETIME_MARGIN_2026-10-01.md`.
The population is the 66 graded leavers behind gap 1.066 and Spearman 0.122 after `127c007f0`. No
code changed.

## What was found

1. **The realised lifetime margin ranks on BOTH factors.** Spearman(R, m_r) is 0.895 and
   Spearman(R, T_r) is 0.632. The two factors are correlated (+0.29) because survivors reach the
   2023–24 margins: realised margin per year rises with exit year (+0.46). That was predicted the
   other way round.
2. **The belief has no per-account lifetime term.** Two facts establish it:
   - The life table EP1 multiplies by is one book-wide value per snapshot cohort.
   - The company's own churn probability at the snapshot is the 0.05 floor for every one of the 66
     accounts. Each has one renewal entry and a `bill_shock_count` of 0, because the yoy comparison
     needs twelve months of history.

   So the belief's rank is m_b's rank, and it spends nothing on T_r, which carries much of R's rank.
   This is the company-side twin of `8dd7794bd`'s world-side finding: the bill-shock count is blind
   in a household's first year in the company's churn model too.
3. **None of the eight pre-registered observables clears the ±0.24 noise floor,** against R or
   against either factor. The segment arm was refused because all 66 accounts are resi. The
   strongest arm is the bill-shock count to the snapshot (from `score_experience_signals` directly,
   which can see 2017 against 2016): +0.19 on R, with the sign opposite to the prediction. It is
   not a result at this n.

## What this settles and what it does not

- The 0.12 is **not** a missing constant, and at n = 66 it **cannot be shown** to be a missing
  observable either. "We cannot tell" is the honest grade for every arm.
- The structural gap is real whatever the sample says. A per-account tenure belief cannot rank
  anything while the company's per-account churn estimate is a constant at the moment it values
  the account.
- Do **not** feed A7 into the company's hazard on the strength of +0.19. It is noise-level, it has
  the opposite sign to the prior, and `B8` forbids teaching the company a world artefact while the
  world's own bill-shock base is being re-derived (`rederive-the-worlds-bill-shock-hazard-...`).

## Next (handed on)

Grade with more power before trying any observable. Survivors are right-censored, not ungradable.
A concordance grade over leavers AND survivors on the rebuilt snapshots (Harrell's C on the
company's per-account belief) widens the population from 66 rows to the book. That is the
instrument that would let an arm clear a floor. Then ask why the company's churn estimate is
constant at first valuation. That is a question for the company's model. It is not a reason to
copy the world's hazard.
