# Does a household's renewal engagement persist, and is it as widely spread as the world makes it?

**Knowledge:** how-households-choose

**Read and measured 2026-10-05.** Claim `c29-retention-reads-engagement-after-sourcing-the-archetype-spread`.
**Subject:** `simulation/household_segments._ACTIVE_RENEWAL_PROBABILITY_BY_ENGAGEMENT`
(ACTIVE 0.65 / PASSIVE 0.15 / DISENGAGED 0.02 per renewal). Its own docstring calls it "a calibration
CHOICE, NOT independently sourced". The shares it is weighted by (`ENGAGEMENT_POPULATION_SHARE`,
0.45 / 0.35 / 0.20) ARE sourced: the Ofgem RMI Oct-2025 stock split, under the R13 ruling, and
cross-checked against CMA 2016 in `continuous_behavioural_engagement_w2_14.md`. This note is
about the per-renewal probabilities and nothing else.

**Why it matters now.** C29's engagement estimate (`company/crm/engagement_estimate.py`) ranks the
world's trait at ρ 0.73 against the channel's 0.19. That lift can only be as large as the
per-household spread the world plants. If the real spread is narrower, the lift and any value a
decision earns from it are inflated by the world and were not earned by the method.

## 1. What is established

- **A persistent stock tail exists.** In CMA Appendix 9.1 (2014/15, n=6,999), 22% "have never
  switched supplier, never switched tariff with their existing supplier and never considered
  switching". Ofgem RMI Oct-2025 puts 20.3% of non-PPM electricity customers on a default tariff for 3+ years. Both are
  already on file (`continuous_behavioural_engagement_w2_14.md` §1). These are STOCK facts: they
  say how many households sit in the tail, not how often a tail household chooses.
- **The tail is not inert.** The source is Ofgem, *Sustained Engagement: learnings from following up
  customers from Ofgem's Collective Switch trial* (October 2020,
  `ofgem.gov.uk/sites/default/files/docs/2020/10/sustained_engagement_pdf_0.pdf`, fetched and
  text-extracted 2026-10-05). The trial took 55,000 customers of one large supplier who had been on a
  standard variable tariff for **3+ years**, and randomised them in March–April 2018. 25,000 went to
  the supplier group, 25,000 to the Ofgem group and **5,000 to a control group that received no
  letters**. The control group switched at 2.6% during the trial window. **Over the following 17
  months the control group's subsequent switching rate was 33%** (p.16). "Switching" there includes
  internal tariff switches, which matches C29's definition: choosing a new fixed term with us
  counts as CHOSE. **49%** of subsequent switches were internal and 51% external (Annex B, p.22).
  That split is pooled over every group, and the report gives none for the control arm alone.
  *Corrected 2026-10-07. This line read "51% of switches were internal", which reversed the
  split and implied it was the control arm's.*
- **In the control arm, a prior switch did not predict the next one.** Control-group customers who
  switched during the trial window switched again at **31%**, and those who did not switched at **33%**
  (p.16). Only intervention-arm switchers sustained a higher rate (63%), and Ofgem attributes that
  largely to Energy Helpline re-prompting them at their tariff end dates (pp.2, 16). That
  is persistence produced by a prompt, not by a household trait.

## 2. What the world predicts for the same cohort (pre-registered, then measured)

Before the run, I worked the prediction out by hand from the shares and the three per-archetype
probabilities, with no channel factor. It was stated in the session, not written to a file before
the run. A cohort that rolled at three consecutive anniversaries chooses within 17 months at about
**15%**.

Measured over 20,000 synthetic ids, through `active_renewal_probability_for_customer(household_of(id))`
(archetype × channel). Each id was weighted by P(rolled 3 times) = (1−p)³. The 17-month window was
taken as one anniversary for sure plus a second with probability 5/12:

| Quantity | World | Published (Ofgem control arm) |
|---|---|---|
| 3+-year default cohort, chooses within 17 months | **0.149** | **0.33** |
| same cohort, chooses at the next anniversary | 0.114 | — |
| P(choose next \| chose) vs P(choose next \| did not), within the cohort | **0.255 vs 0.096 (×2.7)** | **31% vs 33% (×0.94)** |
| population mean per-renewal p | 0.347 | — |

The prediction held (0.15 predicted, 0.149 measured). The world disagrees with the published record
on both legs:

1. **The world's tail is about 2.2× too sticky.** A household that has sat on the default for three
   years chooses at less than half the rate Ofgem observed.
2. **The world's persistence is far too strong.** Within the tail, the world makes a past choice a
   2.7× predictor of the next. In Ofgem's control arm it predicted nothing. About 130 control
   switchers (2.6% of 5,000) gives a 95% interval of roughly 23–39% around the 31%. A ratio of even
   1.5× (about 50%) falls outside it.

## 3. What this does not establish

- **Regime.** 2018–19 had high switching activity, and the price cap arrived on 1 Jan 2019 within
  the window. A cohort followed through 2022–23 would have switched far less. The world's FTC
  withdrawal window already forces rolls there. The comparison is fair only for a non-crisis year.
- **One supplier, one cohort.** Only the 3+-year default tail was followed. Nothing here measures
  persistence among the engaged.
- **The full spread is not identified.** Two moments cannot pin down three per-renewal probabilities
  and three shares. What the source fixes is a floor on tail mobility and a ceiling on within-tail
  persistence.

## 4. Verdict and gap

**Published evidence does NOT establish 0.65 / 0.15 / 0.02, and the one longitudinal RCT on file
contradicts the tail of that spread.** Persistence is established at the stock level: a never-switch
tail of about 20% exists. At the household level, within that tail, it is not: a past choice did not
predict the next.

**Gap, filed.** No published source gives per-renewal choose rates by household engagement class,
or the within-household correlation of choices across renewals outside the default tail. The next
question to research: Ofgem's other engagement trials (the Database / "Cheaper Market Offers
Letter" trials 2017–19) and the CMA EMI panel data, for a repeat-switching rate among the
engaged. Until then the world's DISENGAGED 0.02 is contradicted by a factor of about 2. That is a
fidelity defect, and it is filed for the world lane rather than fixed here, because moving it
re-levels every run.

## 5. The refit (2026-10-05)

Claim `c29-refit-the-worlds-per-renewal-engagement-to-ofgems-sustained-engagement-control`.
Pre-registered before the fit in
`docs/staging/records/SEAT_PREREGISTRATION_C29_REFIT_THE_WORLDS_PER_RENEWAL_ENGAGEMENT_2026-10-05.md`.
Same instrument as §2, 20,000 ids, archetype × channel. The instrument reproduced §2 first: 0.150,
×2.64, mean 0.349.

Three moments fix the three numbers. The shares stay 0.45 / 0.35 / 0.20 (R13).

1. **Population mean held at ~0.35**, the sourced "fixed at expiry → active switch ~35%"
   (`svt_rates_active_passive_2016_2025.md` §4). The refit moves WHO chooses, not how many.
2. **Cohort 17-month rate ≈ 0.33.**
3. **The lowest within-cohort persistence the first two allow.**

| Triple (A / P / D) | Mean | Cohort, 17 months | Persistence | P(next \| chose) / P(next \| not) |
|---|---|---|---|---|
| 0.65 / 0.15 / 0.02 (old) | 0.349 | 0.150 | ×2.64 | 0.254 / 0.096 |
| **0.50 / 0.24 / 0.20 (adopted)** | **0.349** | **0.338** | **×1.26** | 0.310 / 0.245 |
| Ofgem 2020 control arm | — | 0.33 | ×0.94 (≤ ~×1.18 in its interval) | 31% / 33% |

**The residual, and what sets it.** With the mean held and ACTIVE ≥ PASSIVE ≥ DISENGAGED, no triple
gets persistence below ×1.26. The channel multiplier alone, with all three archetypes flat at 0.349,
gives ×1.07. The adopted triple without the channel gives ×1.23. So the held mean sets the floor. It
keeps ACTIVE near 0.50, and ACTIVE is about a fifth of the 3-year cohort. Let the mean go and the
best fit is flat 0.26 everywhere (×1.05). That deletes the archetypes and lowers the book's choose
rate from 0.35 to 0.26. That is a level move, R13's lever and not a fidelity refit's, so it is not
taken. Before the fit this pre-registration did not know which one the sources would disagree with.

**Graded against the pre-registration.** The instrument replicated. PASSIVE and DISENGAGED ended up
close together, as predicted: 0.24 and 0.20 against "both near 0.20". ACTIVE came in at 0.50, not
the predicted 0.55. **The persistence prediction was wrong.** I predicted ×1.1–1.2 and the floor is
×1.26, just outside the source's interval. So the world still has a little more persistence than
the record allows, and the cause is named: the ~35% aggregate.

**What this moves downstream.** C29's estimate was graded against the old spread (ρ 0.73 vs the
channel's 0.19), and its +0.545 lift was measured there too. Both have to be re-graded in this
world. The value arms predate this commit, so the page's code guard (`_code_since_the_run`) refuses
to call them the world as it is now until they are re-taken. The control is
`tests/simulation/test_the_default_tail_chooses_at_ofgems_control_rate.py`.
