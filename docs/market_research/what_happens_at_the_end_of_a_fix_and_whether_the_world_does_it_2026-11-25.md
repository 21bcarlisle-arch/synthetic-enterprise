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
| 2021–23 | 0.44–0.47 | 0.46 |
| 2024–25 | 0.50–0.52 | 0.59 |

Reader: `/var/tmp/vtn-driver/s12g-decomp/defect_share.py`.

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
