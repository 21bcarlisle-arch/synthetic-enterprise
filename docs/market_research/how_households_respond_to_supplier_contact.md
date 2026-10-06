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
4. **The woken share for default-tariff stock between boundaries** (CMOC, collective switch).
   Their windows (30 days, a negotiated tariff) are not the world's fixed-term decision. The SVT
   departure route (`inertia_hazard_for_term`) is not touched by this slice.
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
