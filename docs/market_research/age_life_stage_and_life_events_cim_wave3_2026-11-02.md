**Knowledge:** the-customer-needs-framework

# Age, life stage and life events: what the GB tables say, and whether life stage outweighs income (2026-11-02)

Page 4 of the customer-needs domain, in the order `docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md` §4 ranks them. The
30 Oct steer's advisor synthesis said: *life stage often explains more than income does; worry peaks at 35-54; risk
aversion is U-shaped by age; cash buffers rise steeply with age; single parents are the most exposed group on almost
every need; life events shift the whole needs mix at once.* The parsimony ruling makes life stage one of three
candidate latent factors in the population draw, so the first claim decides whether that factor earns its place.

**Data.** Ofgem, *Consumer Impacts of Market Conditions* (CIM) Wave 3, fieldwork 21 Nov - 11 Dec 2022, unweighted
base 3,457 GB adults responsible for energy bills. Every figure below is derived from
`data/lake/ofgem_cim_wave3_2022/life_stage_crossbreaks_by_column.csv` (weighted column %, effective base as printed;
provenance and a 238-cell cross-check against the sister extract in the same directory's `PROVENANCE.md`). Intervals
are 95% normal on the **effective** base; a contrast is starred only when larger than its own interval. **Grades:**
D derived here; P reported by the body holding the data; S secondary; A assumption with a range.

## 1. Predictions, filed before any life-stage cell was read

Only the banner labels had been seen. Spread = highest band minus lowest band within one crossbreak.

| # | Prediction | Result | Verdict |
|---|---|---|---|
| L1 | Worry and affordability peak in middle age: the top age band is 25-34, 35-44 or 45-54 on at least 5 of the 7 affordability measures | 4 of 7 (any impact, stopped saving, cut necessities, worried behind: general). Took on debt and worried behind: energy peak at 16-24; cut energy peaks at 55-64 | **Refuted** |
| L2 | 75+ is the lowest age band on at least 6 of 7 | 6 of 7; the exception is cut energy, lowest at 16-24 | **Held** |
| L3 | "Life stage outweighs income" does *not* hold for affordability: the income spread exceeds the age spread on at least 4 of 7 | 0 of 7. The age spread is larger on every measure | **Refuted**: the advisor's reading survives, mine did not |
| L4 | It does hold for engagement: the age spread exceeds the income spread on both | Will switch supplier 32.6 vs 12.0; will compare 31.1 vs 17.4 | **Held** |
| L5 | Young children in the household (expecting or under 5) is positive on all 7 affordability measures, starred on at least 4 | Positive on 6, starred on 5; cut energy is -5.0 ± 4.9 | **Refuted** on "all 7" |
| L6 | Renting minus owning is positive and starred on all 7, and larger than the young-children contrast on at least 5 | Starred on 5; stopped saving -2.5 ± 3.3 and cut energy +2.1 ± 3.7 are not. Larger than young children on 3 of 7 | **Refuted** |

The predictions file, timestamped before the extract ran, is kept outside the tree at
`~/.cache/lifestage_predictions_2026-11-02.md`; its text is the table's middle column.

## 2. The age profile (D)

Weighted %, CIM Wave 3. The first seven rows are the affordability and worry measures; the last four are engagement and
stated preference.

| Measure | 16-24 | 25-34 | 35-44 | 45-54 | 55-64 | 65-74 | 75+ | Age spread (95% interval of the extreme contrast) | Income spread, <16k ... 80k+ bands |
|---|---|---|---|---|---|---|---|---|---|
| Any affordability impact | 84.9 | 87.1 | **87.6** | 84.5 | 79.3 | 69.3 | 65.1 | 22.5 ± 6.4\* | 7.7 ± 8.1 |
| Stopped or cut saving | 22.1 | 33.4 | 31.8 | **33.6** | 27.3 | 27.9 | 20.3 | 13.3 ± 6.9\* | 6.2 ± 6.0\* |
| Cut spending on necessities | 29.6 | 35.3 | **37.4** | 36.8 | 30.9 | 21.8 | 15.3 | 22.0 ± 5.9\* | 13.3 ± 8.4\* |
| Took on more household debt | **16.9** | 16.1 | 14.2 | 12.2 | 4.6 | 2.6 | 1.5 | 15.4 ± 4.8\* | 3.8 ± 5.2 |
| Cut energy use because cannot afford | 29.0 | 39.6 | 42.2 | 50.1 | **54.5** | 43.3 | 37.4 | 25.5 ± 6.9\* | 14.0 ± 9.2\* |
| Worried about falling behind: energy cost | **69.1** | 63.8 | 65.2 | 60.7 | 51.2 | 39.3 | 33.5 | 35.6 ± 8.7\* | 11.1 ± 8.3\* |
| Worried about falling behind: general costs | 65.0 | 65.8 | **68.4** | 65.6 | 52.3 | 41.1 | 31.5 | 36.9 ± 7.2\* | 13.2 ± 10.1\* |
| Will switch supplier (next 3 months) | **41.6** | 36.6 | 32.6 | 26.1 | 12.0 | 10.0 | 9.0 | 32.6 ± 6.9\* | 12.0 ± 9.0\* |
| Will compare tariffs | **64.0** | 62.8 | 58.3 | 50.9 | 43.4 | 42.0 | 32.9 | 31.1 ± 8.2\* | 17.4 ± 7.5\* |
| Worried my supplier will fail | 52.5 | 58.5 | 54.5 | 59.5 | 59.0 | 62.7 | **71.9** | 19.4 ± 8.2\* | 6.4 ± 5.6\* |
| Would pay more for green energy | **41.2** | 38.9 | 32.6 | 23.9 | 17.0 | 19.8 | 24.5 | 24.2 ± 6.7\* | 15.3 ± 9.3\* |

Seven age bands against six income bands: the age spread has one more band to reach an extreme, which flatters it a
little. It does not explain a gap of 22 against 8, or 37 against 13.

## 3. The advisor's claims, graded

| Claim (30 Oct synthesis) | Verdict | Grade and evidence |
|---|---|---|
| Life stage often explains more than income | **Confirmed, at the margin.** Age orders every affordability, worry and engagement measure in this survey more strongly than income does | D, §2. One-way tables only: age and income are correlated (retirees sit in the low-income bands with the lowest worry), so this cannot say whether income matters *within* an age band. That needs the joint, which is the Understanding Society row already raised (structure note §6) |
| Worry peaks at 35-54 | **Not confirmed; the two sources conflict on the young.** In CIM Wave 3, worry about falling behind is a plateau from 16 to 54 (61-69%), highest or joint-highest at 16-24, then falls to a third at 75+. The advisor's figure is a different measure at a different date: DESNZ Public Attitudes Tracker, Spring 2025, *very* worried about bills, 25% at 35-54 and 9% at 16-24. Both can be true (intensity against incidence; crisis winter against 2025). Which shape the world uses waits for the PAT age table to be read from the published data | D for CIM (§2); the PAT figure is P as cited by the advisor, not re-read here |
| Risk aversion is U-shaped by age | **Not tested.** CIM has no risk-attitude item. The one adjacent item, worry that the supplier fails, rises with age to 72% at 75+, which is the older half of a U and no more | Stays as the advisor gave it (S) until the Understanding Society risk waves are read |
| Cash buffers rise steeply with age | **Consistent, not tested.** Taking on debt falls from 17% at 16-24 to 1.5% at 75+, the shape a buffer gradient would give; it is not a measure of savings | D for the debt gradient; the buffer itself stays with the Wealth and Assets Survey row (structure note §6) |
| Single parents are the most exposed group | **Cannot be tested here.** Wave 3 has no household-type crossbreak. The nearest, "expecting or under 5 in the household", is +17.9 ± 5.2 on worry about energy cost and +16.6 ± 5.2 on general costs, the largest non-age contrast in the survey | D for the young-children contrast. The advisor's single-parent evidence is fuel poverty (DESNZ fuel poverty statistics: 18-25% against about 5% for couples), P for the comfort floor only; "almost every need" is not shown by any source read |
| Life events shift the whole needs mix at once | **Not tested.** CIM is a cross-section and asks about no event | GAP. See §5 |

## 4. What the tables say that nobody claimed

1. **Cutting energy because you cannot afford it has a different age shape from worry.** It peaks at 55-64 (54.5%)
   and is lowest at 16-24 (29.0%), while worry and debt are highest among the young. Disability in the household adds
   +11.6 ± 3.8; young children *subtract* (-5.0 ± 4.9, not starred); tenure barely moves it (+2.1 ± 3.7). The comfort
   floor's risk sits with older and disabled households, which are not the households that say they are worried.
   This is the same separation the needs-framework page found between worry and cutting use, now located by age.
2. **Tenure loads on debt and worry, not on cutting use or saving.** Renters minus owners: took on debt +8.2 ± 2.4,
   worried about energy cost +15.2 ± 4.1, cut necessities +8.3 ± 3.4; but stopped saving -2.5 ± 3.3 and cut energy
   +2.1 ± 3.7. One "precarity" factor that drives all of these together is not what the margins show.
3. **Young children raise engagement as much as worry.** Will switch supplier +16.9 ± 4.8; will compare +16.0 ± 4.8;
   would pay more for green +9.6 ± 4.8. The household under the most pressure also says it will act most.
   The revealed-switching page found the stated age gap shrinks from about +30 to +3 to +7 in behaviour; the same
   discount should be assumed here until a revealed source by household type is found.
4. **Income's sign flips between needs.** On worry, cutting necessities and cutting energy, low income is higher. On
   switching intent, comparing and willingness to pay for green, high income is higher. Age is monotone (or
   inverted-U) on all of them. That is the margin's case for keeping life stage and affluence as separate factors.

## 5. Life events (GAP, with what is held)

No GB source read so far measures how one household's energy needs change across an event (birth, move, retirement,
bereavement, job loss, illness). What is held:

- **Home moves** are drawn in the world already and have their own Knowledge page; a move is the event a supplier
  observes directly (change of tenancy).
- **The age profile above is a cross-section, not a life course.** Reading "worry falls after 55" as "a household's
  worry falls as it ages" mixes cohort with ageing. The steer's "life events shift the needs mix at once" is a
  within-household claim; a cross-section cannot support it.
- **The source that could:** Understanding Society is a household panel with annual waves, events and energy payment
  method. It is the same licensed dataset already raised for the director (structure note §6); no new row is needed.

## 6. What this changes, and what it does not

- **The parsimony ruling's three factors.** Life stage earns its place: it is the strongest single margin in the
  survey on both the affordability needs and engagement. Precarity, as one factor, is weaker than the synthesis
  says: tenure, young children and disability each load on a *different subset* of the affordability measures (§4.1,
  4.2). The roadmap should carry life stage as a factor and treat "precarity" as a hypothesis to fit on the joint, not
  as a drawn factor, until the Understanding Society joint is available. Until then any precarity loading is an A with
  a range.
- **No world value changes.** Nothing in `simulation/` reads this page. The world additions follow the correctness
  exit test.
- **The supplier.** Age is not held by a supplier unless the customer gives it; tenure is partly observable (change
  of tenancy, landlord accounts); young children are not observable. The comfort-floor shape in §4.1 is the reason a
  supplier's vulnerability signal cannot be "says it is worried".

## 7. What this page does not establish

- **Cause, or any joint.** One-way column percentages; no cell is controlled for another.
- **Behaviour.** Stated answers in the crisis winter, seven weeks into the Energy Price Guarantee. Only the
  revealed-switching page reads behaviour.
- **Waves 4-6.** The life-stage columns were extracted from Wave 3 only; whether the age shape holds after the crisis
  is the next check, from the Waves 4-6 workbooks named in `data/lake/ofgem_cim_waves4_6_2023_2025/PROVENANCE.md`.
- **The small bands.** 16-24 has an effective base of about 260 and young children about 445 (358 on the worry
  items); a contrast without a star is "cannot tell", not "no effect".

## Sources

- Ofgem, *Consumer Impacts of Market Conditions survey: Wave 3 (Nov/Dec 2022)*, data tables (XLSX), Open Government
  Licence v3.0. Retrieval and hash: `data/lake/ofgem_cim_wave3_2022/PROVENANCE.md`.
- Sister pages: `the_customer_needs_framework_cost_worry_switching_cim_waves_3_6_2026-11-02.md`,
  `revealed_switching_by_age_and_arrears_and_the_needs_tables_in_cim_waves_4_6_2026-11-02.md`,
  `price_sensitivity_is_two_traits_cutting_use_and_shopping_cim_waves_3_6_2026-11-02.md`.
- The advisor's synthesis: `docs/staging/advisor/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`.
