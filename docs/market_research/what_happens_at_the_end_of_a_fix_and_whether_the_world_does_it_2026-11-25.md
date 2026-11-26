# What happens at the end of a fixed term, and does the world do it?

**Knowledge:** acquisition-and-retention-economics

*K8 page for the 25 Nov ruling, s.3 part 2 (director, 12:31: "What should we really expect to happen? … What is
the knowledge here we are seeking replicate?"). Written 25 Nov, before any world change it may lead to.*

## 1. The quantity

At the end of a household's fixed term, three things can happen. The household **rolls onto the default** (standard
variable or capped default) by doing nothing. It **re-fixes with the same supplier** (internal). Or it **switches
away** (external). A supplier's retention offer is an attempt to move a household from "switch away" to
"re-fix". It is paid for by every household that would have re-fixed or rolled over anyway. The thing to replicate
is the split across those three outcomes, by period, and how far a cheaper offer moves it.

## 2. What the published record says

| What | Figure | Source (in the tree) | Read as |
|---|---|---|---|
| End-of-fix outcome, six weeks, inert incumbent book | **external 6%**, internal 14%, default 81% | 2019 end-of-fixed-term trial, control arm (`first_renewal_departure_rate_small_gb_supplier.md` §1) | a FLOOR for a 17-year-tenure book, conditional on no action by T−2 days |
| Same, better notice | internal 23%, **external still 6%** | same trial, treatment arm | better communication moves people to re-fix, not to leave |
| Looked into options after the notice | 32% with own supplier, 25% switching | 2017 end-of-fix consultation ¶2.8 (same page) | an upper bound on intent, not on action |
| Customers on a default tariff | about 70% of the six large firms' customers | CMA 2016 (`what_a_kept_household_is_worth_beyond_one_term_2026-11-24.md` §2) | inertia was the norm, and paid for |
| Switching, all households, six months, 2024 | 13% internal, 6% external active, 4% passive | 2024 tariff-choices survey (`first_renewal_departure_rate…` §2) | an all-household base, not per fix end |
| Switching in 2021–23 | collapsed; "91k switches in May [2022], all-time low"; recovery of 78% in 2023 | ElectraLink market insights (`a_save_offer_against_the_switching_rules_and_the_seam.md` S9) | in 2021–23 there was almost nothing cheaper to switch to |
| Response of P(stay) to a cheaper offer | about 1.3–1.6 pp per £10 a year of saving | Deller et al. 2021 (`retention_slope_per_pound_of_renewal_cut.md` §1) | a small slope: a 3–8% discount moves few households |
| A proactive retention offer can RAISE churn | 10% churn offered against 6% control | Ascarza, Iyengar & Schleicher 2016, JMR (same page) | an offer's sign has to be measured against a held-out twin |
| Who to target | target by the offer's effect (uplift), not by churn risk | Ascarza 2018, "Retention futility" (`a_save_offer_against_the_switching_rules_and_the_seam.md` §1027) | the highest-risk household is often not the saveable one |

**GAP (not verified in the tree this pass).** These were quoted in the ruling and are not yet sourced here: the
53% and 51% shares on default in April 2019, and the CMA's detriment figure of about £1.4bn a year. They are
consistent with the CMA's 70% above and do not change any reading below. The **first-renewal external leave rate for a
small supplier's book** is still unpublished (`FIRST_RENEWAL_DEPARTURE_PRIOR = None`). Every household in a small
supplier's book arrived by switching, so its rate sits above the 6% floor by an unknown amount. Ofgem's 2018 RFI
collected it by supplier and did not publish it. This is trade knowledge, a third-side question.

## 3. The world, set beside it (s.12g records, both seeds, control arm, fix ends with no offer)

| Era (term start) | Left at the fix end | World P(leave) |
|---|---|---|
| pre-cap (to 2018) | 0.37–0.38 | 0.34 |
| cap era before 2021 | 0.41–0.43 | 0.44 |
| 2021–23 *(2021 only: see the correction below)* | 0.44–0.47 | 0.46 |
| 2024–25 | 0.50–0.52 | 0.59 |

Reader: `/var/tmp/vtn-driver/s12g-decomp/defect_share.py`.

**Correction, 26 Nov (§6).** The 2021–23 row holds no 2022 or 2023 decision. In both records, every un-offered fix
end in that bucket falls in 2021. Through 2022 every renewal is crisis-forced passive and goes to the SVT route
(`renewal_engagement.CRISIS_PASSIVE_YEARS`), so no end-of-fix roll fires there. The row is "2021", and the rise in
it comes from 2021 H2.

**Three readings.**
1. **The level is high.** It is five to seven times the 6% external floor of an inert incumbent book. Against a
   small switcher-built book it is not shown wrong, because that rate is the GAP above. The world's level was fitted
   to a published departure band (`year_level_anchor`, 0.45 residential). So this is a disagreement between two
   sources, not a defect. It stays open.
2. **The direction in 2021–23 is wrong.** Real switching collapsed in 2021–22, when fixes were dearer than the
   capped default and few suppliers sold any. The world's leave rate *rises* into that era. A world in which
   households leave fastest exactly when the record says they could not leave overstates every offer's value then.
   Too few renewals fall in that era for it to matter to s.12g (8 per run), but it would matter to any later test.
3. **The offer's effect, as the world states it, matches the record.** The world's own uplift from a 3–8% offer is
   +0.012 to +0.021 in P(stay), across every era. That is the order of Deller's slope. **But the run did not deliver
   that uplift** (§4).

## 4. What the run actually did: the offer was answered on a different die

The member runs that s.12g grades re-draw each household's renewal roll by patching
`simulation.customer_events.churn_roll_for_renewal`. `simulation/retention_offer.py` had imported that function by
name, so the patch reached the household's full-rate decision but not its answer to the offer. An offered
household that was leaving was therefore re-asked on an independent die, and stayed with probability about P(stay).
The world's uplift says it should have stayed with probability about 0.02.

Measured: 52 of the twin's 211 offered renewals, and 23 of rankq's 77, renewed on a roll **above even the offered
P(stay)**. Of the 88 offered renewals that sat above it, 52 renewed: 0.59, against a mean P(stay) of about 0.6. The
fix (both by-name importers now read the module at call time) and its control are in the commit that lands this page.

## 5. What this means for the question

What should we expect at the end of a fix? Most households stay, by inertia. A modest offer moves only a few
percent of the leavers. And a large share of the offer goes to households who were staying anyway. So **offering
less should make more money**, exactly as the director expected. The world's stated physics agrees. Read on the
real die, the offers' expected direct economics are negative in every era. The discount paid to households who
would have stayed is about 8.6 times the margin the offer keeps.

The s.12g run said the opposite only because of §4. The finding
`docs/staging/SEAT_FINDING_AN_OFFERED_LEAVER_IS_ANSWERED_ON_A_DIE_THE_FLOOR_DID_NOT_REDRAW_2026-11-25.md` carries the
decomposition and what it means for the thesis.

## 6. Which hazard input carries the 2021 rise (26 Nov, reading 2 answered; no run launched)

**What was measured.** The s.12g control arms (both seeds, un-offered fix ends), split by half-year. Then the hazard
inputs, row by row, from the latest capture that carries them (`docs/reports/qep_g_second_qep_pass_anchor_departure_factors.json`,
82 renewals, 4 Oct world). The twin and rankq control arms share their households, so the two columns are not
independent samples.

| Half | Fix ends (twin) | World P(leave) | Level anchor | Market opportunity | Price response | Our renewal vs the default |
|---|---|---|---|---|---|---|
| 2019 H1–H2 | 52 | 0.43–0.45 | 8.08 | 2.31 | 0.50–0.77 | −11% to −28% |
| 2020 H1–H2 | 58 | 0.42–0.45 | 8.40 | 2.24 | 0.62–0.78 | −15% to −18% |
| 2021 H1 | 23 | 0.40 | 7.73 | 1.72 | 1.57 | +7% |
| **2021 H2** | 18 | **0.54** (Oct–Dec only: 0.58) | 7.73 | 1.72 | 1.81 | **+21%** |

The anchor, opportunity and price columns come from the capture. The P(leave) column comes from the s.12g records.

**The record, by quarter.** DESNZ QEP 2.7.1, the quarterly sheet of the edition the commons cites, reports domestic
electricity transfers in thousands. 2020 ran at 1,454 / 1,331 / 1,512 / 1,515 a quarter. 2021 ran at 1,375 / 1,325 /
1,223 / **579**. 2022 ran at 225 / 201 / 244 / 223. In the commons (`gb_best_deal_gap_to_default.json`), Ofgem's
cheapest-deal gap to the default is 0.246 in 2021-Q3, then **0.0 in every quarter from 2021-Q4 to 2023-Q2**. No deal
anywhere sat below the default.

**Which input carries it.**
- **The level anchor does not.** 8.40 → 7.73 (×0.92), in the right direction.
- **Market opportunity moves the right way but sees the wrong clock.** 2.24 → 1.72 (×0.77) is the record's 2021/2020
  ratio, 15.6% against 20.2%. It is a calendar-year term, so 2021 Q4 inherits the whole year's 1.72. On the record's
  own quarterly shape, that quarter ran at 0.51× its year and 0.40× of 2020.
- **Price position carries the rise.** Its response rises from 0.6–0.8 to 1.6–1.8 (×2.5) because the company's
  renewal went from 11–28% below the default to 7–21% above it. The reference is the household's own capped default
  (`customer_events._reference_level_gbp_per_mwh`). A fix priced above the default is scored as a reason to leave for
  a rival. In real 2021 Q4, that household rolls onto our default: no rival had anything cheaper.

So the cause is two clocks and a reference. The world's market term is annual where the collapse was quarterly.
Its price term measures our renewal against our own default and never asks whether anyone outside undercut that
default.

**Fix 0, the smallest, and the one to build first. Start the FTC withdrawal window on 2021-10-01, not 2022-01-01.**
The world already has the mechanism. `simulation/renewal_engagement.FTC_WITHDRAWAL_WINDOW` sends every fix end
inside it to the default (SVT) route, because "no fixed deal was available to take". It runs from 2022-01-01 to
2023-06-30. Its end comes from Ofgem's statement that fixed deals re-emerged in H2 2023. Its start has no quarterly
source: it is the "2022: near zero" sentence, read as a calendar year. The published gap series in the commons is
0.0 from **2021-Q4** to **2023-Q2** inclusive. Moving the start to 2021-10-01 makes the window *exactly* the
published zero-gap interval. That uses the same class of evidence as its end, and the same series the supplier
already reads for its save offers. It also makes fix 2 below redundant, because the zero-gap quarters and the window
become the same set. Predicted: the s.12g control arms' 29 un-offered 2021-Q4 fix-end rolls (both arms, both seeds)
go to **0**, and those households take the SVT route. The SVT-route hazard is the published 10–20% a year ×
action propensity, with no level anchor, which is about 3% over a quarter, against 0.58 today. 2021 H2's
end-of-fix rate is then the Jul–Sep rows alone (P ≈ 0.4, in a quarter that still ran at 1.09× its year).
**Cost, stated:** the 2021 level anchor was fitted with those rolls in its account-year union, so this is a
capture → refit → capture change, not a one-line edit. The direction runs against the company (R13): fewer
households reach a roll, so the offer reaches fewer households.

**The further fixes, in order, with their predicted moves**, written before fix 0 was found and kept as the
fallback if fix 0 is refused. These figures are filed before any build and before any
run. They are approximations: each row's λ = −ln(1 − P) is split by the realised cause mix (bill shock 0.40, price
0.41, the rest 0.19), because the s.12g records carry the total and not the parts.
1. **Market opportunity reads the quarter.** Use the year's multiplier × that quarter's DESNZ transfers over the
   year's quarterly mean. The year's mean is unchanged, so the anchor fit is disturbed only by where in the year the
   renewals fall. Predicted: 2021 Q4 fix ends 0.58 → **0.44**; 2021 H1 0.40 → 0.45; 2019–20 within ±0.01.
2. **No price motive to leave when nothing outside undercuts the default.** When the quarter's best-deal gap is 0.0,
   the price differential that drives the external price hazard is capped at 0, so the household rolls onto our
   default. Predicted, with (1): 2021 Q4 **0.39**.
3. **The residual, stated.** The record implies about 0.2 for 2021 Q4: the 2019–20 λ × 0.40. Both fixes reach about
   0.39. What is left is dissatisfaction, which is deliberately not opportunity-scaled, and the price term above its
   neutral. The candidate explanation is that in Q4 2021 most suppliers had stopped taking new customers, so even a
   dissatisfied household had nowhere to go. That is a GAP: nothing in the tree says what share of suppliers were
   closed to acquisition by quarter. It is not filled with a number.

**And 2024–25, which the item did not ask about.** The rise there (0.59–0.68 per renewal, against a record at 9–10%,
half of 2019–20) is carried by the **level anchor**: 20.8, fitted on 4 renewal decisions and borrowed by 2025. Its
own note already lists this as rung-1 debt. It is the same disagreement in a different input. It is recorded here
and not proposed as a fix: an anchor refit is capture → refit → capture, and the next capture should run on fixes
1–2.

**What none of this changes.** §5 stands. These fixes lower the world's 2021 Q4 leave rate. That lowers what a
retention offer is worth there, so the conclusion that offering less makes more money gets stronger, not weaker.
