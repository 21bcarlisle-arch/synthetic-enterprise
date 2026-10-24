# How GB households respond to a contact from their supplier, including badly

**Knowledge:** how-households-behave-toward-a-supplier

**Read 2026-10-06** for atom `W2_39_households_respond_to_contact_including_badly`. Claim
`households-respond-to-contact-discover-then-first-slice`. The population-level trial table is
already on file in `next_best_action_and_cross_sell.md` §3.1 and is not repeated. This note reads
three primary reports in full for the one question that table cannot answer: **what decides which
households a contact moves, and in which direction**. Each figure below was read from the PDF
text, not from a summary.

## 1. The three primary sources read

| source | design | read from |
|---|---|---|
| Ofgem, *End of Fixed Term Communications Trial* (Sept 2019) | 2-arm RCT, n=19,553 at one supplier (control 9,776), customers ending a 1-year fix, letter or email a few days before term end, switching over 6 weeks | `ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf` |
| Ofgem, *Cheaper Market Offers Communications trials* (Sept 2019) | factorial RCT, ~600,000 default-tariff customers at 5 suppliers, switching over 30 days | `ofgem.gov.uk/system/files/docs/2019/09/cmoc_report_final_updated_template_0.pdf` |
| Ascarza, Iyengar & Schleicher (2016), *The Perils of Proactive Churn Prevention Using Plan Recommendations*, JMR 53(1): 46-60 | RCT, wireless provider, control 10,058, treatment 54,089, churn over 3 months | author PDF, Columbia Business School |

## 2. What is established

**2.1 At a fixed-term end, a supplier's own reminder moves households to re-fix with it. It does
not move them out.** EFTC §4.1 and Fig. 4.1: overall switching was 19% in the control arm and 28%
in the treatment arm (+9 pp, significant at 95%). *"External switching rates were almost identical
in both arms, but internal switching rates much higher in the intervention arm. This implies that
the EFTC drove internal, rather than external, switching."* Internal was 14% → 23% and external was
6% → 6%. About 8 in 10 internal switchers took another 1-year fix (§4.3). The letter framed the
choice as a loss from defaulting onto the SVT, so the cheapest option the letter pointed at was the
supplier's own.

**2.2 In the same kind of contact, the effect is roughly a constant share of the households who
would not otherwise have acted.** EFTC §4.8, Fig. 4.7, split by previous tariff:

| previous tariff | control | treated | woken share (treated − control) / (1 − control) |
|---|---|---|---|
| fixed | 23% | 33% | 0.130 |
| SVT | 14% | 23% | 0.105 |
| unknown | 18% | 23% | 0.061 |
| **all** | **19%** | **28%** | **0.111** |

A single woken share of 0.111 predicts the two named groups at 31.6% (observed 33%) and 23.6%
(observed 23%). The additive form (+9 pp each) and the multiplicative form (×1.47 each) fit those
two groups about as well, so these three cells **do not identify the form**. What they show is
that the effect is not concentrated in the already-engaged or the inert. The effect also held
across PSR and non-PSR customers, online and offline management, and every tenure band (§§4.5-4.7).

**2.3 Where the saving is decides the direction.** In CMOC the cheaper options on the letter
were mostly a competitor's. *"CMOC drove a higher proportion of people to switch supplier
(external switches) than it did to switch to a cheaper tariff with their own supplier"* (§3.37).
The report's own explanation: *"the annual potential savings from switching externally were £260
higher than the potential annual savings from switching internally (from £97, if switching
internally, to £360 from switching externally)"* (§3.39). Put the same instrument (a supplier
letter) at a different relative price position and it moves households the other way from EFTC.

**2.4 How far a contact moves households depends on how much it names.** CMOC §§3.17-3.20, with
each subgroup's mean potential saving from Table 3:

| subgroup | mean potential saving | control | treated | woken share |
|---|---|---|---|---|
| non-prepayment | £278 | 3.2% | 8.4% | 0.054 |
| prepayment | £78 | 1.4% | 1.8% | 0.004 |
| not price-capped | £293 | 3.2% | 8.7% | 0.057 |
| price-capped | £91 | 1.8% | 2.6% | 0.008 |

The report gives two explanations it cannot separate: the smaller saving, or different barriers
for prepayment households (§3.19). The direction is established. **The gradient is not**: these
four cells confound saving with meter type and cap status.

**2.5 A contact can raise loss, and by a lot, for the households its message fits badly.**
Ascarza et al. (2016), Table 3: churn over three months was 6.4% in the control arm and 10.0% in
the treatment arm (+3.6 pp, p<.001). The treatment recommended a cheaper, better-fitting plan.
Table 8 splits the effect by two pre-campaign observables:

| segment | control churn | treated churn | effect |
|---|---|---|---|
| high usage variability, low overage | 7.25% | 15.01% | +7.76 pp |
| high variability, high overage | 6.78% | 14.26% | +7.48 pp |
| low variability, high overage | 7.48% | 9.26% | +1.78 pp |
| **low variability, low overage** | **8.79%** | **8.13%** | **−0.66 pp** |

So the four kinds the uplift literature names (persuadables, sure things, lost causes, sleeping
dogs) all occur in one randomised population. The authors attribute the loss to two mechanisms
and find support for both: the contact *lowered inertia*, and it made past usage salient to
customers whose plan fitted badly. **Contact as such is not the cause.** A different campaign at
the same firm, a handset offer by text, left churn among those who rejected it at 0.54% against
0.41% in its control, not significantly different.

**2.6 A contact leaves a small trace in complaints.** EFTC §4.9: 199 complaints in the treatment
arm against 146 in the control arm over the trial period. With arms of ~9,777 and 9,776, that is
2.04% against 1.49%. The supplier attributed it to *"customers who were surprised they were to be
defaulted on to a more expensive tariff"*.

**2.7 Default-tariff stock between fixed-term boundaries: the woken share depends on the
instrument, and the saving gradient is observational only.** *Read 2026-10-07 for PB4 R6 (claim
`pb4-r6-the-woken-share-for-svt-stock-between-boundaries`), from the CMOL report and technical
annex (Nov 2017), the CMOC report (Sept 2019) and the Collective Switch final report (Sept 2019),
each read from the PDF text.* The woken share is computed the same way as in §2.2: (treated −
control) / (1 − control). Every trial below counts **any** switch, internal or external, so "woken"
here means "acted", as it does at EFTC.

| trial | population | window | control | treated | woken share | mean saving shown |
|---|---|---|---|---|---|---|
| CMOL, Ofgem-branded letter | SVT >1 yr, 2 suppliers, n=137,876 | 30 days | 1.0% | 2.4% | 0.014 | £203-£301 by supplier and tenure (Table 1) |
| CMOL, supplier-branded letter | same | 30 days | 1.0% | 3.4% | 0.024 | same |
| CMOC, all arms | default tariff, 5 suppliers, ~600,000 | 30 days | 2.9% | 6.8% | 0.040 | £231 realised among switchers |
| Collective Switch 1 | SVT 3+ yrs, one large supplier, ~50,000 | three letters over 7 weeks, to tariff close | 2.6% | 22.4% | 0.203 | "over £300" average |

So **the instrument, not the saving, sets the level.** The savings shown are of the same order
(£200-£300) across all three, and the woken share runs from 0.014 to 0.203, a factor of about 14.
What separates them is friction: the Collective Switch added a negotiated exclusive tariff, a
telephone service, a savings letter and a reminder with a deadline. Within CMOC the only design
change with *"any substantive impact"* was the reminder (+27%).

What the record says about the **saving gradient**, and why none of it is causal:

- **CMOL technical annex, §12 (pooled OLS, all three arms, n=137,876).** The coefficient on the
  potential saving shown on the letter is **0.0000522 per £** (s.e. 0.0000039), i.e. **+0.52 pp of
  30-day switching per £100**, with a control mean of 1.0%. Saving enters as a main effect, not
  interacted with treatment, so it describes switching across the whole sample (contacted and not)
  and does not identify how the *woken* share varies with saving. The saving is also not
  randomised: it rises with consumption, which correlates with engagement. CMOL §3.12 attributes the
  supplier difference (£293 vs £203 mean saving) mainly to the saving, from qualitative interviews.
- **CMOC §3.42 and fn. 43.** *"For every additional £100 of potential savings, the probability of
  switching increases by 1.3%"* (1.2% around the mean saving). It is estimated **among contacted
  customers only** (fn. 41: suppliers *"did not generate potential savings data for customers in
  the control group"*), so it cannot separate the saving's effect on the woken from its effect on
  those who would have switched anyway. Ofgem calls the correlation *"relatively modest"*.
- **Collective Switch §5.8.** *"we saw switching at all levels of potential saving, so it is not
  the only driver of switching behaviour observed in these trials."* No gradient is published.

**Conclusion: no source pins how the woken share of default-tariff stock scales with the saving.**
It is carried as a named `None` (`contact_response.WOKEN_SHARE_SAVING_GRADIENT_ON_SVT_STOCK`). The
two observational gradients, 0.5-1.3 pp per £100 over 30 days, are what the composed world can be
**graded against**. They are not inputs: under §3 the saving reaches a woken household through
its own price comparison and its own elasticity. CMOC's prepayment cell (woken 0.004 at £78) shows
a gradient and a barrier together, and it cannot say which is which (§2.4).

## 3. What this says the world mechanism should be

The sources agree on one structure, and it needs **no uplift number planted in the world**:

> A contact **wakes** a share of the households who would otherwise not have chosen at this
> moment. A woken household then chooses by the same price comparison as any household that
> chooses. If the best option it can see is its own supplier's, it re-fixes (EFTC). If it is a
> rival's, it leaves (CMOC, Ascarza).

Under that structure:
- **the sign varies from household to household**, and is negative exactly where waking exposes
  a bad fit (sleeping dogs);
- **the size of an offer acts through the choice.** A deeper retention discount improves the
  option the woken household compares, so its effect scales with its size through price physics
  the world already has, not through a coefficient attached to the contact;
- **heterogeneity comes from two places**: each household's own engagement before the contact,
  and its own price position.

The single magnitude needed is the woken share at a fixed-term end: **0.111, from EFTC**, where
the trial population (customers ending a 1-year fix, mostly letter) is the same population as the
world's fixed-term decision.

## 4. What no source establishes (gaps, carried as gaps)

1. **The form of the woken share across households.** EFTC's subgroups fit a constant share, a
   constant pp and a constant ratio about equally (§2.2). The world uses the constant share
   because it is the only one of the three that stays a probability everywhere (+9 pp passes 1
   above p=0.91 and ×1.47 above p=0.68), and it is a **named
   simplification, not a finding**.
2. **The saving gradient of the woken share at a fixed-term end.** EFTC ran at one saving level.
   CMOC's gradient (§2.4) is from default-tariff stock over 30 days, and its cells confound saving
   with meter type. The first slice therefore does not vary the woken share with the size of what
   the contact names.
3. **Persistence of a contact's effect.** Ofgem's 2020 follow-up (`does_a_households_renewal_engagement_persist.md`)
   found no persistence in its control arm (31% against 33%). It attributed the treatment arm's 63%
   to repeated prompting. The first slice gives a contact no memory beyond the decision it lands on.
4. ~~**The woken share for default-tariff stock between boundaries**~~ **read 2026-10-07, §2.7:**
   it is established per instrument (0.014-0.024 for a letter, 0.040 for CMOC, 0.203 for the
   collective switch). Its **saving gradient** is not, and is carried as a named `None`. The world
   route is `contact_response.svt_departure_after_contact` (§5). It is not wired, because nothing in
   the world sends a contact yet.
5. **Complaints as a world outcome.** §2.6 is sourced, but the world has no complaint process for
   it to feed. It is recorded here and not built.

## 5. What was built from it

`simulation/contact_response.py` (first slice, level 1). It contains the woken share derived from
EFTC's two published rates, the probability that a household engages once contacted, and a coupled
roll. The coupled roll takes each household's contacted outcome on the same uniform draw as its
uncontacted one. Both are therefore defined for every household, which is the true counterfactual
an uplift estimate is graded against (B8, C34). A contact can never put an engaged household to
sleep. The module also gives the composed change in departure probability for a household whose
churn if it chooses and churn if it stays inert are known; its sign is the household's own.

**Not yet wired.** No caller in `run_phase2b` passes a contact to it. Wiring it is level 2, and
it raises a question the wiring must answer first. For resi, the world's passive household rolls
onto the SVT in the schedule builder, and a reached fixed-term decision is always active
(`household_segments.active_renewal_probability_at_a_decision`, PB6). The EFTC choice point is
therefore the schedule builder's roll, not the departure branch's. The question is whether a
woken household's churn at that point can come out below the inert household's. EFTC says that
for a household on a competitive own offer, external loss did not move. Today's passive cap only
ever *lowers* the inert household's churn. That makes waking weakly harmful wherever the active
physics exceeds the cap, unless the offer lowers the active side. Print it at real inputs before
wiring.

**Correction, 2026-10-06 (printed for C34's next slice).** The paragraph above names the wrong
inert comparator for resi. Since PB6 every resi decision the departure branch reaches is active,
so `passive_churn_cap_for` never applies to a resi household at a fixed-term end. The household that
is not woken rolls onto the SVT in the schedule builder and leaves by `inertia_hazard_for_term`. So
the question is the woken household's churn at the decision against its first-year SVT departure.
Printed from `docs/reports/run_output_c6b8217d1_20261006T161729Z.json`: active electricity
decisions' `realized_churn_probability` against 1 − ∏(1 − segment hazard) over each first-year
stint in `svt_decisions`.

| year | n active | mean churn, woken | n stints | mean first-year SVT departure, inert | difference | × 0.111 |
|---|---|---|---|---|---|---|
| 2017 | 22 | 0.274 | 40 | 0.184 | +0.090 | +0.010 |
| 2018 | 26 | 0.105 | 15 | 0.194 | −0.089 | −0.010 |
| 2019 | 17 | 0.153 | 15 | 0.207 | −0.054 | −0.006 |
| 2020 | 20 | 0.167 | 10 | 0.179 | −0.013 | −0.001 |
| 2021 | 16 | 0.183 | 22 | 0.094 | +0.089 | +0.010 |
| 2024 | 16 | 0.074 | — | 0.067 annualised | +0.007 | +0.001 |
| 2025 | 13 | 0.304 | — | 0.074 annualised | +0.230 | +0.026 |

(2016 has one active decision, 2022 has none because FTCs were withdrawn, and 2023 has one stint. All three are left out. In 2024 and 2025 the end of the report cuts short 17 of 19 first-year stints, so the inert column there is the mean SVT segment hazard annualised over the market year. The first draft of this table used the stints as they were cut and read 0.016 for 2025, which is a truncation and not a hazard.)

What this answers: waking is **not structurally harmful**. In four of seven years it lowers
departure or leaves it almost unchanged. For a book where every household is contacted, the change
in departure stays within ±1 pp except in 2025. That is the order of EFTC's unmoved 6% external
loss. 2025 is the exception, at about +2.5 pp: the active side's churn is 30% against an SVT
hazard of 7%. Before wiring, it must be established which of these causes it: the market, the
year's price position, or the active physics.

What it does not answer: **the two columns are different households**. Active rollers are the
engaged archetype, and inert ones are not. The per-household counterfactual needs each passive
household's churn had it engaged. The run does not log that. Producing it is the wiring's first
output, and it comes from `departure_change_from_contact` on the coupled roll. Until it exists, this
table bounds the sign. It does not size it.

**Between boundaries, on default-tariff stock (PB4 R6, 2026-10-07).** The second route is
`svt_departure_after_contact` + `churn_if_choosing_off_svt`. One contact wakes the instrument's
share from §2.7 (`WOKEN_SHARE_OF_SVT_STOCK`). A woken household leaves with the churn of an active
chooser facing our premium over the market's best, felt through its own elasticity and on its own
bill. If it does not leave, it re-fixes with us. On that segment a contact can only add departures.
*Correction (2026-10-23, C30 draw): "re-fixes with us" is the trials' finding, not what the run
does. Nothing in `run_phase2b.py` reads a woken household that stays: its next segment is the same
default at the same rate. See §7.5, "What stopped the interim route".*

Printed at real inputs (2017 level anchor 6.2, bill £1,100), churn of a woken household:

| elasticity | parity | +10% | +20% | +30% |
|---|---|---|---|---|
| 0.3 | 0.169 | 0.181 | 0.193 | 0.205 |
| 1.0 | 0.169 | 0.212 | 0.292 | 0.362 |
| 2.5 | 0.169 | 0.328 | 0.639 | 0.937 |

So a disengaged household's elasticity now reaches its behaviour through this route, once it is
woken. Before this, the SVT drift was the only route and it ignored elasticity.

**Graded against §2.7, not fitted to it.** At CMOC's instrument, the 2018 anchor and a saving of
£131 / £231 / £331, the departure a contact causes rises by **0.09 / 0.19 / 0.63 pp per £100** at
elasticity 0.5 / 1.0 / 2.0. CMOC observed **1.2-1.3 pp per £100**. The two are not the same
quantity: CMOC's counts any switch, internal included, among the contacted only, so it includes
the gradient of those who would have switched anyway. The world's counts external switches caused
by the contact. Even so, the world's figure is below CMOC's at every elasticity except the
highest. That is the direction a flat woken share predicts. If a causal saving gradient for the
woken share is ever published, this gap is what it would close.

**Wired on SVT stock (level 2, 2026-10-07).** The company sends through
`SimInterface.send_contact`. The world records what reached each household in
`contact_response.ContactsReceived`, and the run loop's SVT roll reads that record, never the
company's policy. The one sender today is the flat rule: `DecisionPolicy.svt_contact_instrument`
writes to every default-tariff account at the start of each SVT segment. It is the baseline a
per-account decision (C34) is graded against. With it `None` (every standing policy), nothing is
sent and every roll is unchanged. Control: `tests/simulation/test_a_run_reaches_the_svt_contact_response.py`.

The §5 question, answered for this route before any constant: the woken household's choice is
**the default it is on against the one market reference every renewal is measured against**
(`customer_events._price_differential_vs_market`). That reference is the published default, or a
rival chasing it. It is never the cheapest fix on the market. So where fixes sat far below the
default (2016-2019), a woken household's premium is understated and so is its loss. This errs in
the company's favour, and it is named rather than patched with a second "market".
No constant was added. The woken shares are §2.7's, and the churn is the world's own loss curve.

Printed at real inputs (pre-registered first: about +3 pp per contacted segment for
`collective_switch`, about +0.7 pp for `cmoc_letter`). Same book, 2016-01 to 2017-12, one arm per row:

| arm | SVT segments rolled | drift departures | woken leavers | mean churn of a woken chooser | departure added per contacted segment |
|---|---|---|---|---|---|
| no contact | 274 | 14 | 0 | — | 0 |
| `collective_switch` (woken share 0.203) | 245 | 14 | 7 | 0.233 | +4.6 pp |
| `cmoc_letter` (woken share 0.040) | 271 | 14 | 1 | 0.237 | +0.9 pp |

The pre-registration under-called both arms (3 and 0.7 pp predicted, 4.6 and 0.9 observed) because the
woken chooser's churn averaged 0.233, not the 0.17-0.20 I assumed from the parity column above.
Every paired segment kept its uncontacted roll and probability exactly. A segment is a cap
period, so this flat rule writes about four times a year. The trials each measured one campaign.

Comparisons, never inputs: EFTC's woken share at a fixed-term end is 0.111, and its woken
households re-fixed internally with external loss unmoved. CMOL (0.024) and CMOC (0.040) are
the letter instruments on default stock. In the world, about 23% of the woken leave and about 77%
re-fix with us. Not yet compared: the external share of each trial's switchers. CMOC's 6.8% counts
internal switches too, and no source here splits it.

## 6. What a renewal cut buys, as the company's prior (B8 Q8, 2026-10-20)

**The question.** The director ruled on 12 Oct (canon C8, decision 7) that the company may learn
what a retention offer does from published trials as well as from its own randomised holdout, and
never from the world's truth. B8's run-time holdout cannot decide on its own at the founders' scale
(about 30 considered renewals a year, against about 19,600 per arm to separate the measured effect
from zero). So the decision needs a prior, and the prior has to come from what is published.

**What is published, and its units.** Only two figures relate staying or leaving to the size of a
saving, both in §2.7, both per pound of *annual* saving:

| source | figure | per £ of annual saving | what it counts |
|---|---|---|---|
| CMOL technical annex §12 | 0.0000522 per £ (s.e. 0.0000039) | 0.0000522 | 30-day switching, whole sample, default-tariff stock |
| CMOC §3.42, fn. 43 | +1.3% per £100 | 0.00013 | 30-day switching, contacted only, default-tariff stock |

No trial varies a *retention offer's* size at random. EFTC, the one fixed-term-end trial, ran at
one level of saving (§4 item 2). The knowledge map already records retention-offer depth as
unpublished.

**What the company may take from them.** A renewal cut of £c a year narrows the saving a rival
offers by £c. If staying responds to the saving the way switching does in these two
cross-sections, the cut buys about g × c of staying. Here g is the gradient, between 0.0000522 and
0.00013 per £.

**Which way the evidence leans.** Both gradients are observational, and both lean the same way:
they overstate the causal effect.
- The saving shown rises with consumption, and consumption runs with engagement. CMOL itself
  attributes the supplier difference mainly to the saving (§2.7).
- CMOC's gradient is taken among contacted households only. It includes those who would have
  switched anyway (fn. 41).

So a prior built from them is generous to the offer, which is the safe direction for a claim that
an offer does *not* pay (F11).

**The build's choices, and why.**
1. **The prior is on the gradient, as a normal.** Its mean is the midpoint of the two published
   figures, 0.0000911 per £. **Its standard deviation is a BELIEF, not a published figure: it
   equals the mean**, which is the module's one convention for a spread nothing publishes
   (`PRIOR_DELTA_SD`: "I could be wrong by as much as the whole slope"). The first draft used half
   the two figures' span (0.0000389). Printed, that let 800 rows showing +0.20 of staying move the
   belief by 0.1%. Two figures from a different decision cannot make a company that deaf to its
   own holdout. The spread is never sized from the world's own response, because that is the
   world's truth. Its weight on the company's own rows, at a cut of £22.50 and a held-out stay of
   0.75 (from `stay_per_pound`):

   | own rows per arm, effect | sd 0.43× mean | sd = mean (built) | sd 3× mean |
   |---|---|---|---|
   | 15, +0.05 (the founders' book in a year) | 0.000 | 0.000 | 0.002 |
   | 400, +0.05 | 0.001 | 0.005 | 0.042 |
   | 4,000, +0.05 | 0.009 | 0.046 | 0.303 |
   | 20,000, +0.015 (a national book) | 0.041 | 0.186 | 0.673 |

   **At the founders' scale the decision is the prior's under any of these spreads.** The choice
   bites only at national scale. There a normal prior moves slowly even against a book many times
   off it. A heavier-tailed prior is the named simplification.
2. **The company's own holdout updates it by precision.** The own-book gradient is the pooled
   difference in stay share divided by the mean annual cut on the treated rows. Its variance is
   the Newcombe interval's half-width over z, squared, over that same mean cut. With no rows, or
   one empty arm, the prior stands alone.
3. **The decision is expected value, not significance.** Q8 of the blind Expert Hour (2026-10-11)
   was right that a significance gate keeps a small book passive for good. The cut is offered when
   the posterior mean stay it buys, valued over the household's expected tenure, exceeds what it
   costs. The valuation is L2's own `retention_cut_decision`, unchanged. Its stay share is the
   company's own churn belief for this renewal, because a held-out share from a handful of rows
   is no share at all.
4. **The cut is valued in ex-VAT pounds**, and the published savings are bill pounds. The prior
   therefore reads a cut as about 5% smaller than the household sees it. That is the conservative
   direction for offering, and it is named rather than corrected.

**What no source establishes (GAPs).**
- A causal gradient for a retention offer at a fixed-term end.
- Whether the response is linear in the cut. Both sources fit it as linear.
- The window: both count 30 days, and a renewal is a single decision.

**Printed at real inputs before building** (`docs/reports/run_output_latest.json.gz`,
`retention_log`, 92 offers, the published book's own costs, margins and churn beliefs, valued as
`retention_cut_decision` values them):

| gradient per £100 of annual saving | offers that pay |
|---|---|
| 0.52 pp (CMOL) | 3 of 92 |
| 1.30 pp (CMOC) | 4 of 92 |
| 5.20 pp (10× CMOL, for scale) | 21 of 92 |

The median cut is £14.63 a year and buys 0.08–0.20 pp of staying. The median break-even is about
1.2 pp. The four that pay at CMOC's figure are households the company believes almost certain to
leave (stay belief 0.001–0.05), or with a very large term margin (PROS-2022-0400, I&C-sized).
**On published evidence, the renewal cut pays for almost no one.** That agrees with canon C8,
"blanket renewal discounts are not the lever", and with B8's harness at L2, now reached from
evidence outside the world.

**Run with the holdout on (default roster, 2016-01-01 to 2017-12-31, 349 s).** Prediction, filed
before the run: every coin-flip row is decided, and the company would offer on at most 10% of them.
Result: 52 coin flips (26 per arm), all 52 decided, **0 of 52 would offer**. Held. Before this
build, the standing guard decided all of these and offered on every one.

## 7. How a supplier's tariff advice reaches a household, and why C34's cannot yet (C30 K8, 2026-10-23)

*Drawn as `the-advice-c34-records-reaches-the-household-k8-then-build`. Prereg §17
(`docs/staging/records/SEAT_PREREG_THE_PER_CUSTOMER_SWITCHES_ON_TOGETHER_AGAINST_FLAT_2026-10-21.md`,
1044c8fe0) found that C34 records tariff advice on 325 renewal rows and sends none. This section
says how such advice reaches a real household, and what a household does with it. It then says why
the build stops here: the seam has no moment at which the company could send it to a household
the evidence says it would move.*

**7.1 The channels the licence prescribes.**
- **The renewal notice** (SLC 22C.3 → 31I; §4.5 of `next_best_action_and_cross_sell.md`). Every
  household reaching the end of a fix must get it, "at an appropriate time … designed to prompt" a
  choice. The 42–49-day rule became this principle in Ofgem's 2018 communications decision. The
  notice carries the renewal price and the default the household will roll onto. This is the
  one contact that is **already in the world's baseline**, because every household gets it.
- **The cheapest tariff message (SLC 31A, with 25C).** Bills and annual statements state the
  tariff the household is on, its annual spend, and what it would save on the supplier's own
  cheapest tariff. Ofgem's 2016–17 review of the RMR "simpler choices" rules **kept** the message
  and removed only the prescription behind its annual-cost figure (Ofgem supplier letter,
  *Removal of simpler RMR rules*, 14 Apr 2016). A later Ofgem enforcement notice against SSE
  still cites 31A for it. Like the notice, it reaches everyone, so it is baseline too.
- **What a supplier adds by choice.** Anything beyond those two: an extra letter, an email, a
  reminder. Under SLC 0 it must not mislead. Email or SMS needs PECR consent or the soft opt-in
  (§4.5 of the cross-sell page). **The per-household decision C34 makes is a decision about this
  addition.** It cannot be about the notice, which goes to every household anyway.

**7.2 What a household does with an added contact.** This is the trial evidence in §§2.1–2.7,
nothing new. EFTC's treatment was exactly such an addition: a letter or email a few days before the
term end, *on top of* the statutory notice. It woke 0.111 of the households that would not have
chosen (§2.2). The woken households re-fixed with their own supplier, and external loss did not
move (§2.1). Between boundaries, a letter wakes 0.024–0.040 of default-tariff stock (§2.7).
NUDGE_PHYSICS_BENCHMARKS.md adds nothing specific to energy tariff advice beyond the default-bias
range (15–35%), which the EFTC control arm already embodies. **On this evidence the household that
advice moves is the inert one, and it moves through being woken, not through the advice's content.**
A household that was already going to choose chooses the same way, letter or not. The world already
encodes this: `engaged_probability_after_contact` leaves an engaged household engaged, and the
coupled roll gives a chooser the same outcome contacted or not.

**7.3 Why C34's advice, sent as it stands, would reach no household that can respond.** I read
the code at `0f59944ac` and counted §16's lower-bound arm (`/var/tmp/se-pcs-arms16-out/`, electricity):
- **The world decides who is inert before the company exists in the run.** A resi household's
  term-end engagement roll (`rolls_active_renewal`) is taken in the schedule builders
  (`renewals.build_renewal_schedule`; `_build_gas_renewal_schedule`). They run for every household
  before the main loop (`run_phase2b.py` ~2133). A passive household is written straight onto an
  SVT stint. **427** electricity fixed-term ends went that way in the arm: 187 in 2017, 2–58 in
  other years, and some of them inside the FTC withdrawal window, where no contact could wake them.
- **C34 decides only on the households already choosing.** `RenewalAdviceDesk.observe_roll` is
  reached from the departure branch. Since PB6 that branch is reached only by active resi
  decisions (`active_renewal_probability_at_a_decision`). That is **454** (household, term) decisions
  in the arm, with advice on **128** of them. §17's 325 counts rows, one per stated advice effect
  (three per decision), so it is the same population counted three times.
- So the published response is null on C34's entire population. Its households would have
  chosen anyway (§7.2). The population the evidence says a contact moves, the 427, was settled
  before the notice moment. Even at EFTC's 0.111, that is about **47 wakeable households over ten
  years** (fewer once the FTC window is taken out), and C34 can never see them.

**7.4 THE SEAM GAP that stops the build.** To deliver advice where it can act, the company has to
decide **at the notice**, 42–49 days before the term end, for every fixed-term household. The
world's term-end roll must then read what arrived (`ContactsReceived`), as the SVT roll already
does. Two things are missing:
1. **A notice-time crossing.** The seam has no event saying "this account's fix ends on D, the
   renewal price is R", delivered to the company *before* the world rolls the household's
   engagement. Today the world rolls engagement while building the schedule, and the company first
   hears of the renewal at the roll itself, after it.
2. **The company's state at the notice date.** C34's inputs are the contribution at the offered
   rate, the churn belief, arrears, satisfaction and shock count. All are computed in the main loop
   as it walks each account's terms, after every schedule is built. Moving the term-end roll into
   the loop, or adding an earlier company pass, is a structural change to the run's order. It
   is not a switch.

`send_contact` itself suffices for the send. `ContactsReceived.receive` would also need a
fixed-term-end instrument keyed to `WOKEN_SHARE_AT_FIXED_TERM_END` (sourced, EFTC). That is a
small change, and only useful once item 1 exists. **No build was started**, as the item instructs
where the seam needs a new observable.

**7.5 Design choices this page commits to, for when the crossing exists.**
- The advice is an *added* contact at the notice. The statutory notice and the cheapest-tariff
  message stay in the baseline for every household, and they are not the company's lever.
- The world's answer is EFTC's woken share on the coupled roll (`rolls_active_renewal_after_contact`).
  No new world number is needed: every magnitude here is §2's.
- The company decides **who** to send it to. Its value is household-side (an inert household
  re-fixing instead of paying the default) as well as company-side (the woken re-fix internally,
  §2.1). That is the first act in this book whose household side does not come out of the company's
  side, which is the M2 test the flat-against-per-customer comparison needs.
- The cheaper interim route, if the director prefers it: send C34-style advice per account at the
  **start of a passive household's first SVT segment**, through the wired SVT route (§5, CMOC's
  0.040). That needs no new crossing, only a per-account sender in place of the flat
  `svt_contact_instrument`. It moves a household *after* it has paid at least one segment on the
  default, so it understates what a notice-time advice would create. That understatement errs
  against the thesis (F11). **Recommended next:** build this route first, default off, as C30's
  level-1 build. It answers the M2 question now, conservatively. Leave the notice-time crossing
  until that arm shows the advice creates value worth reaching earlier.

**7.5a What stopped the interim route (C30 draw, 2026-10-23, delivery seat).** The route above
was drawn as C30's level-1 build: one default-off switch and a per-account sender in place of the
flat `svt_contact_instrument`, with a reach test that a contacted passive household can re-fix and
an uncontacted one cannot. Reading the wired route before building it (`run_phase2b.py` at
`505c5f041`, the SVT branch; `contact_response.svt_departure_after_contact` and
`svt_cause_on_the_coupled_roll`) shows **the route has no re-fix**:
- On the coupled roll, a draw below `p_drift` is drift, a draw between `p_drift` and `p_contacted`
  is a woken household that left on price, and **every other draw is "stayed"**. A woken household
  that did not leave is indistinguishable from one the letter never woke. Its next default segment
  is already in the heap, built before the loop, at the same default rate. No code reads its wake.
- So on this route a contact can only **send households away**. The company's side is a loss of
  margin. The household's side is a leaver's saving at a rival, and the world does not record what a
  leaver pays next. The arm pair the draw asks for would therefore grade one side only. It could
  not answer the M2 question it was drawn for, so neither the switch nor the arms were built:
  that is the smallest-run rule (R5) applied to a run that cannot answer its question.
- The household-side act §7.2 and §7.5 rely on is the EFTC one: a woken household **re-fixes with
  its own supplier**. The run does have a route from the default back to a fix: the annual
  anniversary roll (`renewals.build_renewal_schedule`, 2026-09-18). That roll is taken **at schedule
  build**, before the loop, so a contact cannot reach it. It is §7.4's problem again, on SVT stock.
- Making a woken stayer re-fix needs two things, and the second is what stops this turn:
  1. **A fix quoted at a new moment, through an existing door.** The fix price is struck at
     schedule build through `request_renewal_offer` (`renewals.py`, the seam's renewal door). A
     re-fix needs that same door called **inside the loop**, at the segment's start. No new door is
     needed, but the call moves to a new point in the run's order.
  2. **A world splice, in the reverse direction of the declined-fix splice.** On a draw in the
     re-fix band, the world removes the household's remaining default segments up to its next
     scheduled boundary (`_pending_starts`) and pushes one fixed term there, at the quoted rate.
     The next boundary is the anniversary, already decided, and it stays as built. The band needs
     **no new world number**: on the same uniform draw it is
     `[p_contacted, p_contacted + (1 - p_drift) x woken x (1 - churn_if_choosing))`, from §2's
     magnitudes and the existing curve. Cutting the fix at the anniversary rather than giving it
     twelve months understates the household's side (F11). The cost is building a fixed-term
     record inside the loop with everything the schedule builders put on one: locked costs, the
     forward the company priced on, and the notice. That is a run-order change, not a switch, and it
     is more than one turn of work with its controls.
- **Recommended next (the seat's call, not a director question):** build 1 and 2 as one
  default-off increment, with its reach test (a contacted stayer on a re-fix draw is supplied on a
  fix up to its next boundary; an uncontacted one is not; off is byte-identical). Then build the
  per-account sender on top of it, as drawn. The in-loop fixed-term builder it needs is also the
  first half of §7.4's notice-time route, so it is not wasted if that route is chosen later. Until
  it lands, a per-account SVT sender would only choose whom to lose.
- **Built (2026-10-23, default off):** `contact_response.A_WOKEN_SVT_STAYER_REFIXES` and
  `svt_refix_band_top`. With it on, a draw in the band strikes a fix through
  `renewals.price_fixed_term`, the function the electricity builder now calls for every term. The
  fix is quoted as of the contact and runs from the next cap segment to the stint's anniversary. It
  withdraws the default segments in between, and its start rolls no departure and no decline. The
  row says what happened in `sim_refix`, or why not. Choices that understate the household's side
  (F11): the fix starts at the next cap segment, not on the contact date, and a contact in a stint's
  last segment re-fixes nothing. Not built, each a GAP: the riding gas leg of a dual household stays
  on the default, and a gas-only household cannot re-fix, because a gas fix is struck only inside
  the gas builder. The fixed term already built at the anniversary was priced with no prior fixed
  rate, so the company classifies that renewal against nothing.
- **The per-account sender (2026-10-23, default off):** `svt_contact_once_per_stint` sends the
  policy's instrument once per default-tariff stint, at its first segment, in place of every
  segment. The rule is the company's (`contact_programme.sends_at_segment`), read off its own record
  of when the account rolled onto its default. Every household it reaches is passive by
  construction: the company sees only that the fix ended and the account rolled. The first segment
  is chosen because a re-fix struck there runs longest before the anniversary. The rule does not
  pick households by value. C34's `decide` needs the renewal-time state it is fed in the departure
  branch, and SVT stock never reaches that branch. Choosing within SVT stock is the next step if
  the arm pair shows the letter creates value at all. Each re-fix row now carries the default rates
  it withdrew and the EAC, so its household side can be graded. The arm pair and its
  pre-registration:
  `docs/staging/records/SEAT_PREREG_C30_THE_ONCE_PER_STINT_SVT_LETTER_GRADED_ON_BOTH_SIDES_2026-10-23.md`.
- **Graded (2026-10-24):** over the full window, 803 letters drew 20 re-fixes. Households saved
  £1,749 ex VAT on energy, and the company's `total_net` fell £389, so the sum is +£1,360. Why the
  company lost less than households gained is unattributed, and it is not read as value created.
  The world's decline-and-stay rule now reaches the re-fix: a woken stayer never re-fixes above
  the default it pays on the contact day. On the first ungraded arm, 6 did, 5 of them in 2021.
**GAPs.**
- Whether SLC 31A's cheapest tariff message survives today in the form the 2016 letter kept was not
  re-read after the SSE notice.
- No trial isolates the *content* of tariff advice (which tariff it names) from the wake. CMOC's 71%
  of switchers picked a tariff the letter did not list (communications page §3.5). That says
  content matters little, and it is the reason the world answers the wake only.
- The woken share at a fixed-term end for a household already sent the statutory notice by
  *this* supplier is EFTC's single-supplier figure. Supplier-to-supplier variation is unpublished.
