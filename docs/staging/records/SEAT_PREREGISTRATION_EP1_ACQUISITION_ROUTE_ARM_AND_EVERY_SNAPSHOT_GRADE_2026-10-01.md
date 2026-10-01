**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# Pre-registration: acquisition route as a first-valuation arm, and the belief graded at every account-snapshot

Claim `ep1-acquisition-channel-arm-and-every-snapshot-grade`. This is filed BEFORE any route or
later-snapshot belief is joined to an outcome. Up to filing I have looked at: the route census by
first-valuation year, and the world code that draws each household's dispositions. The
instrument is the one written out in
`SEAT_PREREGISTRATION_EP1_CONCORDANCE_OVER_LEAVERS_AND_SURVIVORS_2026-10-01.md` (Harrell's C on
T_fwd, survivors censored at 2025-06, ties ½). It runs on the same run (`/tmp/ep1bk/run.pkl`) so
that the numbers stay comparable with that grade.

## Say what "channel" is before measuring it

The item's hypothesis is that PCW-acquired switchers leave sooner. **This world has no PCW
route.** `simulation/net_new_acquisition.py` has no marketing-channel draw, and
`_build_company_event_log` emits only `home-move-win` and `market-acquisition`. What a supplier
can actually know here is the **route** each account came in by:
- `FOUND`: the hand-authored founding roster, `C*`
- `PROS`: a prospect the company quoted and won through its own funnel, `PROS-*`
- `SYN`: a curriculum-drawn arrival with no win/lose step, `SYN-*`
- `SUCC`: a successor registration after a home move or a replacement win, `C*_N`

A real supplier knows every one of these about its own book, so the arm is wall-clean. `PROS` is
the nearest thing this world has to "won as a shopper". The predictor is −[route == PROS], so a
C above 0.5 would mean won prospects leave sooner.

**Census (route × first-valuation year, graded population of 120):** 2017 is 50 SYN, 10 PROS,
4 FOUND and 1 SUCC. Every later cohort is all PROS, except one SYN in 2022. A within-year
contrast therefore exists only in 2017, and the arm's real n is 10 against 55.

**The structural prior:** every disposition the world's renewal hazard reads is drawn as
`random.Random(f"<trait>_{customer_id}")` in `simulation/household_segments.py` (engagement,
propensity, payment channel, fuel poverty, tenure, occupancy). None of them reads the route. So
the world carries no route→tenure association by construction. Any within-cohort signal would
be chance, or a composition effect through a trait that differs between routes.

## The every-snapshot grade

**Unit:** an (account, cutoff year y) pair where the account has a numeric H2 belief at
`{y}-12-31` and T_fwd ≥ 0. Each account contributes one row per year it is valued.
**Pairs:** within the same cutoff year only. Each account appears at most once per stratum, so
there are no repeated measures INSIDE a stratum. They exist only across strata.
**Two nulls, both reported:**
- (a) a stratified permutation band: shuffle the predictor among accounts within each cutoff
  year, 1,000 times, seed 0, 95% two-sided;
- (b) a per-account cluster bootstrap CI on C: resample accounts with replacement and keep all of
  each one's snapshots, 1,000 times, seed 0. This is the cluster-aware one.

An arm is graded "ranks" only when C is outside (a) AND (b) excludes 0.5.

**Arms:** B (H2 value), L_b (life-years at the account's tenure position), m_b = B / L_b,
−p_c (company churn probability), and A0 = tenure position itself, the years on book at the
cutoff. A0 is the trivial baseline any belief should beat.

## Predictions

- **R1 (route, within 2017).** C(−PROS) = **0.50**, inside its band. The band will be about
  ±0.10 because there are only 10 PROS. This follows from the structural prior.
- **R2 (route, pooled).** Composition only, at about 0.45. It is not load-bearing.
- **R3 (route, margin rate within 2017).** Spearman inside ±0.25.
- **S0 (population).** About 450 snapshots over the 120 accounts. Snapshots at tenure position
  ≥ 2 outnumber first valuations.
- **S1 (p_c).** p_c is still at the 0.05 floor on more than 80% of snapshots.
  C(−p_c) within cutoff = 0.52, inside the band.
- **S2 (L_b).** L_b varies per account now. Within cutoff, C(L_b) = **0.55**, at the band edge
  of about ±0.05. The book's life table carries some of the world's tenure shape (the world's
  bill-shock count is blind in year one).
- **S3 (B).** C(B) within cutoff = 0.52, inside the band. The margin term dilutes L_b again.
- **S4 (A0 tenure position).** C(A0) within cutoff = **0.45**. Older accounts leave sooner,
  because the world's first year is protected from bill shock.
- **S5 (m_b).** Spearman(m_b, m_r) within cutoff, cluster CI, = +0.05, inside the band.
- **Headline (SH).** At most one of the per-snapshot arms ranks tenure, and if one does it is
  L_b or A0, never B. The belief does not beat its own tenure-position input.

Results will be written beside these, wrong ones included.

## Results (scripts `/tmp/ep1s/route.py`, `build.py`, `fwd.py`, `snapstats.py`, `base.py`; same run pickle)

### Route

| arm | pooled C(T) [perm] | 2017 stratum C(T) [perm] | 2017 Spearman(m_r) [perm] |
|---|---|---|---|
| −PROS, won prospect | 0.406 BELOW [0.434, 0.570] | **0.492** [0.443, 0.558], 528 informative pairs | +0.032 [±0.24] |
| SYN, curriculum arrival | 0.423 BELOW [0.436, 0.567] | **0.506** [0.433, 0.561], 724 informative pairs | +0.023 [±0.24] |

- **R1 — CONFIRMED.** Within 2017, the route does not rank tenure.
  - The band is ±0.06, narrower than predicted.
  - There is an instrument caveat: the all-years within-year C (0.490) carries ½-ties from the
    single-route cohorts. The 2017 stratum is the reading.
- **Incidence differs, timing does not.** 9 of 10 PROS are leavers, against 37 of 50 SYN. That
  is n = 10 and not significant. The median leaver T is 2.25 years for PROS and 1.33 for SYN.
- **R2 — CONFIRMED in direction.** Pooled C is 0.406, below the band. That is composition only:
  later cohorts are all PROS.
- **R3 — CONFIRMED.**

### Every snapshot

Population:
- 435 account-snapshots over 123 accounts, at cutoffs 2017–2024.
- 120 of them are first valuations. The other 3 accounts are the seeds with no first-valuation
  belief.
- 315 are later snapshots.
- **Instrument correction:** `observed_tenure_positions` reads **2** at first valuation, not 1. A
  "position ≥ 2" filter therefore selects every row. The subset that was meant is "not the first
  valuation", and that is what is graded below.

Tenure, within cutoff year: stratified permutation band, then per-account cluster bootstrap CI.

| arm | all 435: C [perm] [cluster] | **later 315: C [perm] [cluster]** |
|---|---|---|
| A0 tenure position | 0.461 [0.471, 0.528] [0.411, 0.510] | **0.447** [0.461, 0.541] [0.387, 0.509] |
| L_b life-years | 0.505 [0.475, 0.526] [0.476, 0.538] | **0.516** [0.465, 0.534] [0.487, 0.553] |
| B belief H2 | 0.488 [0.457, 0.548] [0.423, 0.557] | **0.479** [0.441, 0.560] [0.386, 0.572] |
| m_b | 0.490 | 0.481 |
| −p_c company churn | 0.521 [0.462, 0.539] [0.486, 0.559] | **0.503** [0.446, 0.559] [0.445, 0.559] |

Margin rate. The forward target f_r is `net_margin_gbp` settled after the cutoff per forward
year. It is **before** cost to serve, because cost to serve is not per-record. The within-cutoff
Spearman takes ranks within each stratum.

| predictor | first valuation, n = 118 | **later, n = 300** | all, n = 418 |
|---|---|---|---|
| m_b, the belief's margin term | +0.257 [perm ±0.24] [cl −0.01, +0.49] | **+0.427** [±0.12] [cl +0.28, +0.54] | +0.358 [cl +0.21, +0.47] |
| naive margin rate observed to date | +0.345 [cl +0.06, +0.57] | **+0.512** [cl +0.37, +0.62] | +0.426 [cl +0.28, +0.54] |
| naive − belief, paired cluster CI | | **+0.084** [+0.046, +0.128] | +0.067 [+0.021, +0.106] |

Within cutoff, m_b and the naive rate rank-correlate at **0.954**.

Against the predictions:
- **S0 — CONFIRMED** (435 against about 450, with later snapshots the majority).
- **S1 — WRONG.** p_c is at the 0.05 floor on only 126 of 435 snapshots (29%), with 13 distinct
  values. It **varies, and still does not rank tenure** (0.503 on later snapshots).
- **S2 — WRONG.** C(L_b) is 0.516 and cannot tell. The life term varies per account now and
  still carries no tenure ranking.
- **S3 — CONFIRMED** (0.479).
- **S4 — direction right, ungraded.** A0 reads 0.447, below the naive permutation band. The
  cluster CI [0.387, 0.509] contains 0.5. **The permutation band alone would have called a
  repeated-measures artefact a result.** The cluster null is the one that counts.
- **S5 — WRONG, by a lot.**
  - The belief's margin term ranks forward margin at +0.427 on later snapshots, and the cluster
    CI excludes 0.
  - It ranks it **worse than the naive observed-to-date rate**, and that rate is 0.954 the
    same ordering.
- **SH — CONFIRMED for tenure.** At no snapshot does any arm, the belief included, rank tenure.

**The +0.084 gap cannot yet be attributed.** Two things differ between the naive rate and m_b:
- the belief subtracts cost to serve (`settled_year_margins(cost_to_serve, …)`), and the target
  does not;
- the belief has its own form (B / L_b, with discounting).

Prediction, filed before the control: **the gap is the cost-to-serve subtraction**. Computing the
naive rate net of cost to serve will close it to within ±0.03. The one-variable control is
handed on.

## The attribution control (`/tmp/ep1s/ctl.py`), run after the first landing

On the 300 later snapshots, the gap decomposes as follows (paired cluster CIs):

| step | effect on Spearman with gross forward margin |
|---|---|
| gross rate over calendar span → over distinct settled months | **+0.000** [0, 0] |
| subtracting cost to serve (I2 → I1, the belief's own input) | **+0.084** [+0.046, +0.128] |
| the belief's form, I1 → m_b = B / L_b | **+0.000** [0, 0] (within-cutoff sp(I1, m_b) = 1.000) |

**The prediction is CONFIRMED.** The whole gap is the cost-to-serve subtraction. The belief's
form costs nothing in ranking: within a cutoff, m_b is its input's ordering exactly.

That makes the gap a **target artefact until shown otherwise**. The target is gross of cost to
serve, so the gross rate shares its basis.

Prediction, filed before the run: with the forward target ALSO net of cost to serve (cumulative
cost to serve at run end minus at the cutoff, per account), I1 ranks it **at least as well as**
I2. The I2 − I1 gap falls to ≤ 0, with its CI covering 0 or below.

**Result: WRONG.** Against a forward target net of cost to serve, on the 300 later snapshots:

| predictor | Spearman | cluster CI |
|---|---|---|
| gross rate I2 | **+0.451** | [+0.29, +0.58] |
| belief input I1 = m_b | **+0.387** | [+0.23, +0.53] |

- The I2 − I1 gap is **+0.062** [+0.031, +0.099]. It persists, so it is **not** a target
  artefact.
- At first valuation (n = 118) the two read +0.291 and +0.224, with overlapping CIs.

Two candidate causes were ruled out by measuring them:
- **Cost to serve is persistent.** Within-cutoff Spearman between cost to serve per year to date
  and per forward year is **0.71** [0.59, 0.78]. It is mostly a flat £55 per leg per year: the
  median is £55, and the upper quartile £109 is the dual-fuel accounts.
- **It is not on a different clock.** The median ratio of the to-date rate to the forward rate is
  1.005–1.04 at tenure positions 3–8. The ratio drifts up with tenure (within-cutoff Spearman
  with position −0.358 on the difference), which is small.

**I cannot yet say why a persistent cost subtracted from a persistent margin makes the ranking
of their persistent difference worse.** The next candidate, not yet measured, is that the
dual-fuel step in cost to serve (£55 against £110) re-orders accounts across the fuel split in a
way the forward net margin does not follow. The one-variable control is to grade I1 and I2
within fuel-split strata. That is handed on.
