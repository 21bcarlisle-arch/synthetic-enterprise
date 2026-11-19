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
