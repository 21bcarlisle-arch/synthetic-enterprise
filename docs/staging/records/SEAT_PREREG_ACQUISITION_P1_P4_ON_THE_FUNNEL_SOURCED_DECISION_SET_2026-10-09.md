**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `grade-acquisition-p1-p4-on-a-funnel-sourced-decision-set`

# PRE-REGISTRATION: P1-P4 on the funnel-sourced decision set (2026-10-09)

Filed BEFORE the training, noise and fresh sets are built. The test is the one in
`SEAT_PREREG_ACQUISITION_SELECTS_ON_EACH_PROSPECTS_OWN_RESPONSIVENESS_2026-10-08.md`, which is not
changed. This file fixes the instrument and how each P is read off it, because the 2026-10-09 attempt
found B8's original set could not see option 1.

## The instrument

`simulation.coin_drawn_decision_set.build_funnel_decision_set`:

- **Who is in it.** Every domestic electricity household the growth campaign's funnel won at the
  seed (`plan_growth_campaign`'s new `funnel_winners`: all wins, before the settlement ceiling
  samples them), dated the day it was won. *Corrected at landing, 2026-10-09: the wins are now
  read by resolving the campaign with no settlement ceiling (`_resolve_campaign(...,
  customer_year_budget=inf)`), not through a new key. The rows are byte-identical to the graded
  ones on I/101, off/202 and L/1050. The key would have put `net_new_acquisition.py` in this
  commit, and its standing red (the systemd-peak ceiling leg, HEAD_RED_REGISTER since 2026-10-02)
  refuses any commit that touches it.* Beside them is the drawn trickle. Ids are kept, so the
  elasticity and engagement the funnel selected on are the ones the renewal roll reads.
- **The walk.** Renewals follow the run's builder. A fix ends at its anniversary, where the world
  rolls active against passive. That point is a rolled renewal and the company's coin decision:
  default, or default minus £7.5/MWh, with the passive cap. An active stayer takes the offered fix.
  A passive stayer rolls onto the default. A year on the default carries the C1b inertia hazard, and
  an active anniversary converts it back onto a fix with no departure roll.
- **What crosses.** `HOLDOUT_OBSERVABLE_FIELDS` now carries `acquisition_route`, `days_on_default`
  and `ever_actively_renewed`, the company's own records of its own account.

Measured while building it, seed 101, option 1 on, arm I: 501 households (497 campaign wins and 4
trickle), 648 decisions in 5.3 s. Of those, 646 were `campaign_win`, 187 had renewed actively, and
121 had days on the default. **`acquisition_route` is close to constant on this set.** The route is
known before any grading run.

## How each P is read (`tools/grade_acquisition_selection.py`)

This is done once per arm (option 1 off / I / L), per observable, and per margin end
(`MARGIN_SHARE_ENDS` 0.019 and 0.14):

- **Training.** The company learns in its own arm's world, on seeds 1001-1100 pooled, about 65,000
  decisions. The pooled effect needs ~27,700 per arm (`4320ae6a5`), so one seed's ~650 cannot train
  it. A group gets its **own read** only where its smaller arm reaches the decisions the pooled effect
  needs (`effect_for_channel`, unchanged). Days on the default are grouped in whole years: 0, 1, 2+.
- **P1.** At least one group with its own read is offered the cut by the learned decision on the
  fresh seeds 101 and 202.
- **P2.** Every cut lands in an own-read group, and at least one group is offered nothing.
- **P3.** On each of 101 and 202, the learned rule's supplier value per decision, using the world's
  own P(stay), beats the better flat rule by more than 2 SD. The SD is that lead's SD over noise
  seeds 301-320, built fresh in the same arm.
- **P4.** In the option-1-off world, the decision learned there offers no cut on 101 or 202.

## Predictions, written before the runs

1. **P1 fails in both arms (I and L), on all three observables, at both margin ends, on both seeds.**
   This is the prediction already filed on 2026-10-09. The selection the build check measured is
   ~1.00x at the market-average quote. No group except the near-universal `campaign_win` and `0y`
   reaches its own read, so the decision falls back to the pooled effect. At a £7.5 cut the pooled
   effect does not pay (`4320ae6a5`).
2. **P4 holds**: the off world offers nothing, for the same reason.
3. **Not decided by the decision, measured on the truth:** the world's true effect per decision is
   **larger in the ever-actively-renewed group than in the never group**, in all three arms. Active
   renewals are uncapped, and passive ones carry the 0.10 churn cap that a cut cannot move.
4. **Arm L shows a larger true effect in the ever-actively-renewed group than arm I does**, because
   linking the level to engagement puts the most sensitive households in the active group.

A refutation of any of these is recorded beside this file. Nothing above is revised after the runs.

## Result, 2026-10-09. Recorded beside the predictions, which are not revised.

Built at origin `c568a5944` plus this commit. Per arm: 122 seeds, about 650 decisions per seed,
3 s per seed including the campaign. Training was about 64,000 decisions per arm. Cut £7.5/MWh. The
full output is reproducible with `python3 -m tools.grade_acquisition_selection build|grade` and the
seeds above.

**P1 fails in both arms, on all three observables, at both margin ends, on both seeds. P2 and P3
fail with it. P4 holds: the option-1-off world offers nothing.** In every arm the learned decision
offers no cut at all on 101 or 202. Its value equals never offering, and it beats always offering
by about £8 per decision.

| arm | pooled learned effect (95%) | per arm needed | own-read groups | groups short of their own read (learned effect) |
|---|---|---|---|---|
| off | +0.0166 (0.0089, 0.0243) | 14,008 | `campaign_win`, `0y`, never-active | 1y +0.033, 2y+ +0.040, ever-active +0.026 |
| I | +0.0157 (0.0081, 0.0233) | 15,723 | same | 1y +0.014, 2y+ +0.034, ever-active +0.021 |
| L | +0.0160 (0.0084, 0.0236) | 15,127 | same | 1y +0.015, 2y+ +0.036, ever-active +0.022 |

- **Prediction 1 HOLDS.** Why P1 fails is two things, and they are separable:
  1. **Power.** The groups that differ from the pool hold 2k-9k decisions per arm, short of the
     ~15k their own read needs, so the decision reads the pooled effect.
  2. **Economics, which is decisive.** At the 0.14 margin end, the cut pays only where it adds
     about +0.15 of staying (cut ~£20 a year against a lifetime of ~£130). No group's TRUE effect is
     above +0.017. A perfect read would still offer nothing.
- **Prediction 2 HOLDS.**
- **Prediction 3 HOLDS IN DIRECTION ONLY.** The world's true effect is +0.0134 ever-actively-renewed
  against +0.0127 never (arm I). In arm L it is +0.0138 against +0.0128, and in the off world
  +0.0134 against +0.0128. The gap is 5-8%, a twentieth of what would move a decision.
- **Prediction 4 HOLDS IN DIRECTION ONLY.** Arm L's ever-active true effect is +0.0138 against arm
  I's +0.0134, 3%.
- **The groups' own learned effects overstate the truth by about 2x.** 2y+ on default reads +0.034
  to +0.040 against a true +0.016. The power rule (`effect_for_channel`) is what keeps the decision
  from acting on them, and it is right to.
- **`acquisition_route` cannot group this set.** Over 99% of decisions are `campaign_win`. Only 4 of
  ~500 households per seed are trickle, and the campaign has one route, its own funnel. A route the
  company could vary a save by needs a world with more than one acquisition channel. The CMA holds
  channel figures and redacted them (research note §A4), so that is a gap, not a setting.

**The placebo that shows this "offers nothing" is a result, not a guard that cannot offer.** On arm
I's own sets, +0.30 of staying was planted on the ever-actively-renewed rows. The same grader then
gives P1, P2 and P3 all **True** for that observable at the 0.14 end: the cut goes to 383 rows, all in
`True`, leading the best flat rule by £6.43 and £6.15 per decision against a noise SD of £0.17. On
`days_on_default` it correctly gives P1 True and P2 False, because the planted group's rows are
spread across all three years.

**What this means for ruling 2.** On this instrument, selecting on each prospect's own
responsiveness at the market-average quote creates no group a save offer can be targeted at. The
reason is not that the company cannot see the group. The world's per-group response to a £7.5 cut
is about 0.013-0.017 everywhere, an order of magnitude below break-even.
