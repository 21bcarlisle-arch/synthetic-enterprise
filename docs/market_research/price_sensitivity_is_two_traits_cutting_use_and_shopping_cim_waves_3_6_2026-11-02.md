**Knowledge:** the-customer-needs-framework

# Price sensitivity is two traits: who cuts their use and who shops, in four waves of Ofgem's survey (2026-11-02)

This is page 1 of the customer-needs domain as `docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md` §4 ranks it. It answers
the 30 Oct corpus steer (`docs/staging/advisor/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`),
Ask 1 and the 16:51 data addendum. It also answers the director's 16:44 question: *"Same with price elasticity, (not
cashflow)? Not clear cut and linear correlation to wealth?"*

The advisor's synthesis (point 5 of the steer) says price sensitivity is at least two traits, and that neither
follows wealth in a line:
- **consumption elasticity** = need × headroom, capped by the comfort floor;
- **switching or shopping propensity** = need × capability × trust × hassle, and **anti-correlated with need**;
- the middle-income group responds most.

This page tests that synthesis against Ofgem's own tables.

## 0. What is measured, stated before any number

There are two quantities, and they are different experiences.

- **Trait C, cutting use.** When energy costs more, does the household use less? The survey measure is E20a,
  *"Which of the following actions, if any, have you taken in order to reduce the costs of your energy bills?"*
  (Wave 3 Table 163; Wave 4 Table 178; Wave 5 Table 156; Wave 6 Table 108). Waves 4-6 add "in the past 3 months".
  Wave 3 gives no window, so **levels do not compare between Wave 3 and the later waves. Contrasts within a wave
  do.** The measure is the share who report each action. It is **incidence, not kWh**. How much they cut comes from
  a different source (§3).
- **Trait S, shopping.** Does the household look at other tariffs, and does it move? The survey measure is C4, what
  the household did in the past 12 months: compared but did not switch; switched tariff with the same supplier;
  switched to a new supplier. It is already extracted at
  `data/lake/ofgem_cim_waves4_6_2023_2025/cost_worry_wtp_and_revealed_switching_by_column.csv` and read on
  `revealed_switching_by_age_and_arrears_and_the_needs_tables_in_cim_waves_4_6_2026-11-02.md`.

Both are reported behaviour from one survey of GB bill payers (BMG for Ofgem, about 3,000-3,500 a wave). Neither is
a supplier's record.

**The contrast convention is the sister pages'.** Each figure is a weighted column % difference ± 1.96 × the
standard error from each column's effective base. It is starred (*) when that interval excludes 0. Every figure in
§1-§2 is graded **D**: derived here from the published tables, with the table numbers named above.

**Pre-registration.** `docs/staging/records/WORKER_PREREGISTRATION_THE_TWO_PRICE_SENSITIVITY_TRAITS_ACROSS_CIM_WAVES_4_TO_6_2026-11-02.md`
was written after reading Wave 3 and before any Wave 4-6 E20a contrast was printed. It is graded in §4.

## 1. The two traits run in opposite directions with age (D)

| Contrast, 65-74 minus 16-24 | W3 | W4 | W5 | W6 |
|---|---|---|---|---|
| C: reduced room thermostat | +32.7 ± 6.0* | +22.7 ± 6.3* | +28.4 ± 6.8* | +22.1 ± 6.1* |
| C: turned down radiators in unused rooms | +21.4 ± 6.8* | +19.2 ± 6.8* | +14.0 ± 7.9* | +13.9 ± 6.8* |
| C: reduced boiler flow temperature | +18.9 ± 5.1* | +13.5 ± 5.8* | +10.6 ± 6.1* | +7.6 ± 4.8* |
| C: reduced tumble dryer use | +14.2 ± 6.3* | +10.7 ± 6.3* | +10.7 ± 6.3* | +8.2 ± 5.7* |
| S: compared, did not switch | -7.8 ± 6.2* | -15.9 ± 6.3* | -9.4 ± 7.3* | -19.7 ± 6.2* |
| S: switched to a new supplier | -4.9 ± 4.2* | -7.2 ± 3.8* | -6.4 ± 5.1* | -2.7 ± 3.1 |
| S: switched at all (net) | -19.9 ± 6.4* | -19.9 ± 6.1* | -5.1 ± 6.9 | +0.5 ± 6.0 |

**Every heating curtailment item rises with age in all four waves.** Comparing tariffs falls with age in all four.
Switching to a new supplier falls in three of four. On age, **the two traits are not one dial.** The household that
turns its thermostat down is not the household that shops.

**The confound the table cannot remove.** Age travels with tenure and with control over the heating. In Wave 3,
owners reduced the thermostat at 40.5% and private renters at 28.5%. A renter often cannot change the boiler flow
temperature at all. One-way tables cannot say how much of the age gradient is age. That needs the cross-tab or the
microdata (§5).

The sister page found that older households cut energy *because they could not afford it* (E3) more than the young,
and that this did not survive past Wave 4. That is a different question: rationing under hardship. E20a asks about
any action to reduce cost, and its age gradient holds in all four waves. Both readings are true, and they measure
different things.

## 2. Need raises both traits, and income separates only comparing (D)

| Contrast | Measure | W3 | W4 | W5 | W6 |
|---|---|---|---|---|---|
| behind on bills minus no difficulties | C: any action (net) | +11.7 ± 4.3* | +18.1 ± 4.0* | +20.4 ± 4.3* | +16.8 ± 5.0* |
| | C: reduced room thermostat | -3.2 ± 6.2 | +4.1 ± 5.5 | +5.7 ± 6.4 | +1.0 ± 5.8 |
| | S: switched to a new supplier | +3.1 ± 3.5 | +4.9 ± 3.1* | +5.2 ± 3.7* | +4.1 ± 3.5* |
| | S: compared, did not switch | +0.4 ± 5.8 | -2.1 ± 5.0 | -4.2 ± 5.6 | -3.0 ± 5.7 |
| income £80k+ minus under £16k | C: reduced room thermostat | +8.0 ± 9.4 | -3.9 ± 8.8 | -0.2 ± 8.6 | +0.3 ± 6.9 |
| | C: any action (net) | -1.0 ± 6.9 | -5.3 ± 7.5 | -1.0 ± 7.0 | -2.7 ± 6.3 |
| | S: compared, did not switch | +11.5 ± 8.7* | +14.7 ± 8.6* | +11.0 ± 8.1* | +19.1 ± 7.1* |
| | S: switched to a new supplier | +0.8 ± 4.7 | +3.3 ± 4.7 | +1.5 ± 4.4 | -0.8 ± 3.7 |
| income £25-45k minus under £16k | C: any action (net) | +3.4 ± 3.5 | +1.8 ± 3.7 | +2.5 ± 4.0 | +4.5 ± 4.2* |
| | C: reduced tumble dryer use | +7.4 ± 4.8* | +9.2 ± 4.6* | +6.0 ± 4.6* | +6.0 ± 4.3* |
| | C: turned down radiators | +4.9 ± 5.1 | +0.6 ± 5.2 | +7.4 ± 5.3* | +7.1 ± 5.1* |

Wave 3 and 4 bill difficulty is "keeping up with bills". Wave 5 uses the household-bills column and Wave 6 the
other-household-bills column, as on the sister pages.

What the table shows:
- **Need raises cutting use.** Households behind on their bills report taking some action 12-20 points more often in
  every wave.
- **Need raises moving supplier, too.** They report switching supplier 3-5 points more often, starred in three of
  four waves, without comparing more.
- **The thermostat does not move with need.** Those behind on bills turn the thermostat down no more than those with
  no difficulty. This is consistent with the comfort-floor cap: their set-points are already lower. SERL-CW found 24%
  of households struggling to pay below 18°C in 2023, against 15.2% of all homes (P, on
  `heating_behaviour_comfort_and_health_floors_2026-10-25.md` §5). One-way tables cannot establish the cap.
- **Income separates comparing tariffs**, by 11-19 points in every wave. It does not separate cutting use or moving
  supplier. The better-off look more. They do not move more, and they do not cut more.
- **No middle-income peak in taking action.** The middle band (£25-45k) does not take action more than the under-£16k
  band in Waves 3-5. It is starred once, in Wave 6, at +4.5 ± 4.2.
- **Some single actions are lower for the poorest band.** Tumble-dryer use is cut less by the poorest band in every
  wave, and radiators in two. Owning fewer such appliances, and having less left to cut, are both consistent with
  this. The table cannot separate them.

## 3. How much is cut: the magnitude is P, not D

E20a counts who acts, not how many kWh they save. The magnitude on file is from the SERL panel, winter 2022/23, on
`heating_behaviour_comfort_and_health_floors_2026-10-25.md` §5 (graded **P**, primary publications by the panel's
holders):
- median gas cut of 10.8% (IQR 1.2-22.4%, n = 5,594);
- about 3.8% less gas per 1°C set-point reduction;
- a price elasticity of gas demand of -0.071;
- mean set-point down from 20.2 to 19.2°C, with about a quarter not changing.

**GAP: a GB elasticity of consumption by income band.** None is on file. The 30 Oct pack's claim that the middle
responds most rests on summaries (**S**), and this page does not find it in incidence (§2). The SERL microdata would
settle it. It sits behind a UK Data Service licence, which is reserved to the director (G5), and §5 names it.

## 4. The pre-registration, graded

| # | Prediction (filed before the Wave 4-6 E20a values) | Result |
|---|---|---|
| P1 | Thermostat, 65-74 minus 16-24, positive and starred in Waves 4-6 | **Held**: +22.7*, +28.4*, +22.1* |
| P2 | Thermostat, £80k+ minus under £16k, starred in none of Waves 4-6 | **Held**: -3.9, -0.2, +0.3 |
| P3 | (Not blind.) Revealed switching, young minus old, positive in every wave | **Held for a new supplier** (+4.9 to +7.2, positive in all four, starred in three). **Refuted for net switching in Wave 6** (-0.5): same-supplier tariff moves among the old caught up by 2025 |
| P4 | Any action, behind minus no difficulty, positive and starred in Waves 4-6 | **Held**: +18.1*, +20.4*, +16.8* |
| P5 | Any action, £25-45k minus under £16k, starred in none of Waves 4-6 | **Refuted in Wave 6** (+4.5 ± 4.2*). Held in Waves 4 and 5 |

## 5. What this does to the advisor's synthesis

- **Two traits: confirmed (D).** They have opposite age gradients in four waves and different income gradients.
  One "price sensitivity" dial would be wrong on age.
- **"Shopping propensity is anti-correlated with need": corrected (D).** Households behind on bills move supplier
  more, not less. They do not compare more, and the better-off compare most. So *comparing* follows capability and
  income, and *moving* follows need. The sister page on C5 reasons (`why_households_switched_by_arrears_and_age_c5_waves_3_6_and_the_debt_objection_rule_2026-11-02.md`)
  finds that switchers behind on bills differ from other switchers on supplier reasons, not on price. Shopping
  therefore splits again, into **looking** and **moving**, and they have different drivers.
- **"Consumption elasticity is need × headroom, capped by the floor": consistent, not established.** Need raises
  taking action. The thermostat, the one item that hits the floor, does not rise with need. That is the cap's shape,
  but one-way incidence cannot price it.
- **"The middle-income group responds most": not found in incidence (D).** One wave of four shows it on the net
  measure. Several single actions are lower for the poorest band, which ownership explains as well as response
  does. The magnitude by income is a GAP (§3).
- **Not linear in wealth: confirmed for both traits (D).** Income moves comparing, and barely moves cutting or
  moving supplier.

**What it would change, if the world used it.** This page proposes and builds nothing. The ruled order puts world
additions after the correctness exit test. Today the world draws `population_draw.price_elasticity_for_customer`
as a lognormal weight that is nearly independent of anything a supplier sees, and `self_rationing` keys on budget
stress. Under the parsimony ruling, the evidence here suggests:
- **life stage** loads on cutting use (+) and on looking (-);
- **precarity** loads on cutting use (+) and on moving (+);
- **affluence** loads on looking (+) only.

Whether any of these changes a supplier result is the test the ruling sets before a correlation is added. It goes to
the Ask 2 roadmap, not to code.

**Datasets that would settle what this page cannot (licensed, reserved to the director, G5):**
- SERL, for kWh response by income and tenure;
- Understanding Society, for age against tenure against income;
- EHS microdata, for set-point headroom by tenure.

These go into the steer's single `for_the_director` row for licensed microdata, together with the other pages'
asks.

## 6. Where it is weak

1. Everything here is what people said they did, not metered use, and not a supplier's record.
2. The tables are one-way. Age, tenure, income and arrears are entangled, and no joint table is published.
3. E20a's window changed after Wave 3, and Wave 6 changed the answer list (a fridge-freezer item; warm spaces).
4. The £80k+ band's effective base is about 86-126, so income intervals are wide.
5. The rows read are the ones named in the steer's hypotheses. 4 waves × 5 contrasts × some 15 items were available,
   so a starred cell on its own may be chance. The claims above rest on a sign held across waves, not on a single
   star.

Sources: Ofgem, *Consumer Impacts of Market Conditions* survey data tables, Waves 3 (May 2023), 4 (Nov 2023),
5 (Sep 2024) and 6 (Jul 2025), Open Government Licence v3.0. The raw Wave 3 workbook and the E20a extract are under
`data/lake/`, and the Wave 4-6 workbooks' hashes are in the PROVENANCE there.
