**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Prepayment and self-disconnection, knowledge first, so the comfort and health floor can be tested (2026-11-19)

**Type:** STEER, through the advisor channel. The director's words, from chat on Thu 19 Nov:

- 07:54 GMT, sharing https://data.sdr-sense.org.uk/datasets/spatially_and_temporally_granular_dynamic_energy_vulnerability_indices?tab=metadata with no comment.
- 07:55 GMT, sharing another assistant's general answer about energy vulnerability indices, with no comment.
- 07:57 GMT, on the advisor's recommendation below: "Yes"

## What the advisor found (check it)

**The SENSE dataset** (Smart Data Research UK catalogue): "Spatially and temporally granular dynamic energy vulnerability indices".
- The catalogue entry says: "This data product provides 3 datasets derived from Data Communications Company (DCC) smart meter event data", "Aggregated indices to aid research into energy vulnerability and fuel poverty". One appears to be seasonal.
- Area unit, period, access terms and contents are not on the public page.
- The page has a "Request Access" route, so it is gated.

**Which events indicate vulnerability.** DCC's "Tackling Fuel Poverty through Smart Metering" (v1.0, June 2023) lists emergency-credit activations, self-disconnection, prepayment top-up frequency, credit transfers between fuels, and credit/prepayment mode switching. Its figure: "More than 8,500 people couldn't afford to top up their prepayment meter in the first two months of 2023 alone", from Citizens Advice.

**Our gap, in the repo's own words** (`docs/market_research/ASSUMPTIONS.md`):
- fuel poverty: "Not modelled — no income-band or fuel-poverty flag exists per customer";
- payment method mix, prepayment against standard credit: "Not modelled";
- prepayment debt: "Not modelled… Different mechanism entirely".

**Why it matters.** M3 makes comfort and health "a floor, not a weight: no gain in any need, and no gain in utility, justifies a breach." A prepayment household self-disconnecting in cold weather is that floor being breached. Without prepayment households and their events in the world, the company cannot breach the floor or protect it, and the floor cannot be tested.

**Fit with the walls.**
- Emergency credit, self-disconnection, top-ups and mode switches are events a real supplier sees on its own smart meters, so they are legitimate company observables (the epistemic wall).
- Area-level seasonal indices are aggregates (W11).

## The outcome wanted

1. **Knowledge page first (K8): energy-vulnerability observables, from open sources.** Cover:
   - prepayment share and who has it;
   - emergency-credit use;
   - self-disconnection frequency, duration and seasonality, and who it hits;
   - rationing that does not show as disconnection;
   - the supplier's licence obligations: Ofgem's prepayment rules since 2023, involuntary PPM installation, ability to pay, and the Priority Services Register.

   Candidate sources:
   - DCC (above);
   - Ofgem's decisions and data on prepayment and self-disconnection;
   - Citizens Advice;
   - Mansilla, Gallage and Sanchez-Campos, "Operationalising the Lived Experience of Energy Vulnerability" (IJPDS 11(4), 2026; SERL data; flags for rationing, suppressed demand and freezing-weather gas self-disconnection);
   - the small-area energy-vulnerability study of England and Wales in *Regional Studies, Regional Science* (2025, doi 10.1080/21681376.2025.2472069);
   - the JRC's EU multidimensional energy-vulnerability work.

   Write GAP where unpublished. Search Ofgem before asking (K4).
2. **Check the gated SENSE indices from their public documentation only.** Report what the three datasets hold (events, area unit, period), the access route, and the terms. **Do not register, apply or accept any terms.** A data licence is a real-world commitment (G5). Raise it to `for_the_director` as one yes-or-no line, with a recommendation, **only if** the indices fill a gap the open sources leave and that gap matters to the floor test.
3. **State plainly what the world needs** to put prepayment households and self-disconnection in:
   - the population share and its joint structure (income, tenure, heating fuel, property efficiency);
   - the payment mechanism (top-ups, emergency credit, friendly-credit hours, debt recovery on the meter);
   - the household's response to cost and cold (rationing, disconnection);
   - the observable events the company sees.

   Say which parts the knowledge page establishes and which are GAP. **This is a fidelity scope, not a build.** Any build follows K8 and the baseline/curriculum split (R13), with the population mix the director's where it is curriculum.

## Reading-log entries to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-19 | SENSE catalogue, "Spatially and temporally granular dynamic energy vulnerability indices" (DCC smart-meter event data; gated) | Director | Points at our largest floor gap: prepayment and self-disconnection are not modelled. Open sources first; gated access is a G5 decision. | KNOWLEDGE FIRST |
| 2026-11-19 | DCC, "Tackling Fuel Poverty through Smart Metering" (v1.0, June 2023) | Advisor, from the above | The list of smart-meter vulnerability events a supplier observes. | SOURCE |
| 2026-11-19 | Another assistant's general answer on dynamic energy-vulnerability indices | Director | Confirms SENSE access is gated. Points to the open 2025 LSOA study (*Regional Studies, Regional Science*) and the JRC work. | POINTER ONLY |

## Rules

- **No application, registration or terms accepted** for any gated data (G5).
- **No number picked.** A population share or rate with no source is GAP.
- **No personal microdata (W11).** Area-level aggregates only, in the repo.

## Risk

Touches: one knowledge page, a read-only check of public documentation, a fidelity scope note.
Blast radius: none until a build is proposed.
Probable failure mode: **a floor scope that invents prepayment behaviour to fill the gap.** Mitigated by GAP and by K2: an omission asserts zero. State that the world currently asserts zero prepayment harm, and that this is the one value we know is wrong.

Proportionality: knowledge and scope only. Implement directly.

— Director steer, 19 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done (first lane: delivery seat, landed on origin as a8c5978913)

*Delivery seat, 19 Nov 2026.*

1. **Knowledge page (K8):** `docs/market_research/energy_vulnerability_observables_prepayment_and_self_disconnection_2026-11-19.md`
   (topic `vulnerability-and-the-psr`). It covers:
   - prepayment share and who has it;
   - self-disconnection frequency (Ofgem smart-prepayment counts, Q2 2026), duration, seasonality and
     who it hits;
   - emergency and friendly credit;
   - rationing that does not show as disconnection (the SERL flags; the IJPDS item is an abstract with
     no prevalence);
   - pointers to the licence obligations the topic already held.

   Each unpublished quantity is marked GAP, and each figure read through a helper is marked
   [secondary].
2. *[Correction, 19 Nov, autonomous worker, resolving the fork: the second lane below read the SENSE public documentation and closed the GAPs this item names -- four datasets, MSOA, 2025 only, Safeguarded, academic-only licence. Its companion note holds the reading. Neither lane raised a `for_the_director` line, so the two agree on that.]*
   **SENSE, from public documentation only. Nothing was registered, applied for or accepted.** The
   catalogue page renders client-side, so its contents, area unit, period and terms are GAP. **No
   `for_the_director` line was raised.** The floor test's open gaps are per-household quantities, and
   area-level indices cannot fill them (page §6). The recommendation is not to apply now.
3. **Fidelity scope:** page §7 gives what is established and what is GAP across population,
   mechanism, response and observables. Its first finding is K2's: **a shipped run asserts zero
   prepayment harm.**
   - The 13-14% label prepayers have no meter mechanics.
   - W2_43's supply events reach only meters moved for debt, and take-up ships at 0.
   - Self-rationing is drawn only in a coupling tool.

   No build was made. The suggested order (supply events for every prepayer, then coupling to cold and
   money, then self-rationing in the run) is fidelity work, K8 first, handed on separately.
4. **A correction made beside the claim.** `vulnerability_psr_and_ability_to_pay_2026-10-25.md` §0
   said the world's payment method is `direct_debit | other`. That had been stale since PB4.
5. **Reading log:** the three rows above are appended to `docs/institutional/reading_log.md`, and the
   feed is regenerated.


## Done (second lane: autonomous worker, a2ed7654e0, the same steer actioned in parallel)

*The two lanes actioned this steer at the same time and neither saw the other. Both stand. Two notes now cover one topic.
`energy_vulnerability_observables_prepayment_and_self_disconnection_2026-11-19.md` (above) is the scope note, filed under topic
`vulnerability-and-the-psr`. `prepayment_and_self_disconnection_observables_2026-11-19.md` (below) is the source behind the
published page `site/knowledge/prepayment-and-self-disconnection/`. They agree on the floor finding: a shipped run asserts
zero prepayment harm. Folding them into one home is owed, and is not done in this merge.*


Actioned 19 Nov 2026 by the autonomous worker, in the commit that moves this file.

1. **Knowledge page (K8), open sources.** Published `site/knowledge/prepayment-and-self-disconnection/`
   (topic entry, graph node and three edges, facets, index card). Research note
   `docs/market_research/prepayment_and_self_disconnection_observables_2026-11-19.md` covers all five
   areas: prepayment share 2016-2025 from DESNZ QEP tables 2.4.2/2.4.3/2.5.2, and who has it (EHS
   tenure, DESNZ fuel poverty by method); meter mechanics (2020 rules, 2018 emergency-credit amounts,
   2026 supplier amounts and friendly hours, meter debt recovery); self-disconnection frequency,
   duration and cold (Ofgem Q2 2026 counts; Fawcett et al. 2024; Longden 2025); rationing; and the
   smart-meter events a supplier sees (DCC 2023 and 2025, with alert codes). GAP written wherever
   nothing is published. Mansilla et al. is an abstract only, with no thresholds or rates.
2. **SENSE, public documentation only.** Nothing was registered, applied for or accepted. Companion
   note `sense_dynamic_energy_vulnerability_indices_public_documentation_2026-11-19.md`. There are four
   datasets, not three (three from DCC events, one from FINDS/NatWest banking data). MSOA; 2025 only;
   "Safeguarded"; academic-only licence; clause 6.1 needs permission to generate synthetic data. **Not
   raised to `for_the_director`**: the indices fill one gap (a market-wide distribution of how long
   households stay off supply), but open sources bound it from two sides, so it does not block a
   first floor test. It is raised as a yes/no line if a build shows the floor result swings across
   that bound.
3. **Fidelity scope.** Note §0 and §7. The shipped world asserts zero prepayment harm:
   - the ~14% prepayment channel has no meter events;
   - only debt-fitted meters self-disconnect, and none is fitted while take-up ships at 0;
   - rationing is drawn in the twin harness only.

   Smallest change that lets the floor fail (a proposal, a world change needing its own K8 amendment):
   - the W2_43 supply-event feed for stock prepayment households, with a duration;
   - gas outages coupled to cold;
   - prepayment coupled to tenure.
4. **Corrections beside the claim.**
   - `ASSUMPTIONS.md`: the three "Not modelled" rows the steer quoted were stale (prepayment split
     since PB4, a fuel-poverty flag since July, meter debt since W2_42/43).
   - `gb_payment_method_migration_rates.md`: the PPM/SC split gap is closed by QEP.
   - `knowledge_map.md`: "3.2M self-disconnect per year" was 3.2m people who ran out of credit.
   - The vulnerability page's two prepayment-mechanics lines.
5. **Reading log.** The three rows, with the papers read, are under G5 in
   `docs/institutional/reading_log_against_the_gaps.md` (part two holds domain research).

Decision: fidelity yes
