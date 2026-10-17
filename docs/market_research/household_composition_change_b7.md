# How often a GB household's membership changes, and what our world does instead

**Knowledge:** home-moves

**2026-10-17, worker tick (B7 drawn; K8 knowledge before build).** This is for B7's open item (e),
composition change (`docs/design/simplifications/B7_customer_state_layer_moves_and_shocks.yaml`,
record of 2026-10-10). The world build waits for the 2026-10-19T03:00Z publish
(`docs/direction/DIRECTION.yaml`). Its lane also carries the BLOCKING crisis bad-debt finding. So only
the knowledge moves this tick, and no code changes here. Item (d), income-shock depth, is in
`income_shock_depth_and_duration_b7.md`.

## 1. What a composition change is, before any figure

A composition change is **a person joining or leaving a household that stays at its address**. A whole
household moving is a home move (`home_moves.md`), not a composition change. That definition splits
into experiences that a supplier meets in different ways:

| change | what the supplier sees | what changes for the bill |
|---|---|---|
| a birth | nothing | usage rises (children are not in NEED's adult table, the W2_13 §3 GAP) |
| a young adult leaves home | nothing | usage falls one adult band |
| a partner joins, or a couple separates and one leaves | nothing, unless the account holder is the one who leaves | usage moves one adult band, in either direction |
| a death in a home of two or more | sometimes a bereavement call, a change of account holder | usage falls one adult band |
| **the death of the only occupant** | a bereavement notification, often weeks late | **the account ends**: a final bill to the estate, and the home stands void until it is sold or let |

The last row is not like the others. It is a **credit exit**, with the same shape as a move-out: a
closing read, a final bill, and a balance that someone other than the customer has to pay. The world
does not generate it today (section 3).

## 2. What the published record says

**All changes together: about one household in six a year.** "About one in six British households
change their composition each year" (*BHPS User Manual, Volume A*, section on household and person
identifiers, UK Data Service SN 6614; text checked against the PDF on 2026-10-17). It is BHPS, which
ran from 1991 to 2008, so it is older than the run window. It counts every join and every leave,
including lodgers, returners and carers.

The separate flows, each as a share of households a year:

| flow | published figure | share of households | how it was derived |
|---|---|---|---|
| births | 0.0107 per person (`life_events._NEW_BABY_ANNUAL_PROB_PER_PERSON`, ONS crude rate) x 2.36 people per household (ONS FAH 2023) | **about 2.5%** | arithmetic |
| deaths | 581,363 deaths registered in England and Wales, 2023 (ONS, *Death registration summary statistics 2023*) over 24,783,116 E&W households (Census 2021, as `dwelling_records` cites it) | **about 2.3%** | arithmetic |
| young adults leaving home | 3.6m people aged 20-34 live with parents (ONS FAH 2023). Living at home falls from about 57% at 20 to about 10% at 30 (ONS, *Young adults living with their parents*, 2023). Half have left by 24 (2021, up from 21 in 2011) | **about 1.4-2.1%**, net of returns | about 4.6 points of each single-year cohort leave a year. The cohort size of about 0.85m is assumed and was not fetched this tick |
| divorce | 0.0036 a household (`life_events._DIVORCE_ANNUAL_PROB`, ONS 2023) | 0.36% | as cited in code. Cohabiting separations are not counted |
| partnering, cohabiting separations, returners, lodgers | **GAP**: no annual GB rate was found this tick | the remainder | BHPS one-in-six less the named flows leaves about 8-9 points |

**Sole-occupant deaths, the one that ends an account: a derived range, not a published figure.**
8.4m people live alone (30% of 28.4m households), and half of them, about 4.2m, are aged 65 or over
(ONS FAH 2023). ONS does not publish deaths by living arrangement in its annual series. If people aged
65+ who live alone die at the all-65+ rate (about 4-5% a year), that is about 170-210k accounts a year
ending by death, **about 0.6-0.7% of households**. That is a floor, because people living alone at 65+
are older on average than all people aged 65+. **GAP:** deaths by living arrangement (the Census 2021
linked mortality study is the likely source). For scale, home moves end about one domestic account in
ten a year (`home_moves.md`), so death is a small exit, but a different one.

**The aggregate is flat.** Average household size was 2.4 in 2016 (27.1m households; ONS FAH 2016,
"remained at 2.4 people over the decade") and 2.36 in 2023 (28.4m; ONS FAH 2023). The flows above
roughly cancel across the book. **Composition dynamics move the spread across households, not the
mean.** A build that drifts the book's mean headcount outside about 2.3-2.45 over 2016-2025 is wrong.

**Each change moves usage by the NEED adult gradient** (`occupancy_consumption_volume_shape_w2_13.md`
§2, DESNZ NEED 2023, medians): going from two adults to one takes electricity from 2,867 to 1,993 kWh
(-30%) and gas from 10,624 to 8,546 kWh (-20%). Going from three adults to two is -14% electricity and
-8% gas. A birth's effect is not in NEED, which counts adults only (W2_13 §3 GAP).

## 3. What our code does, set against it

- **Headcount is fixed for the whole run.** `simulation.dwelling_records.people_count_for_area` draws
  it once per `customer_id`, deterministically. The life-event stream reads it
  (`life_events._household_persons`) but never writes it.
- **`new_baby` and `divorce` change only `income_stress`** (`life_events.apply_events`). A birth adds
  no person and no usage. A divorce removes no adult and no usage. Each is a budget event with no
  demand side.
- **Nobody dies.** There is no death event, so no account ends by bereavement, no estate final bill
  is raised, and no home stands void after a death. The world's domestic departures are switches and
  moves only.
- **Young adults never leave**, and nobody joins. The world does not carry ages, only
  `pensioner_present` and `someone_employed` (`composition_cuts_for`) and the build-era proxy that
  retirement reads. So a leaving-home draw has no population to draw from yet. **That is a GAP in the
  world's state, not a missing rate.**

So about one household in six changes membership each year in the real record, and none does in ours.
Because the aggregate is flat, the book's total volume is not much affected. What is affected is the
**year-on-year change in a single household's usage**. `how_much_a_same_households_use_moves_year_on_year_and_in_2022.md`
counts occupancy among the real causes of that spread. A supplier's forecast for one account, and its
DD review, meet that spread. The world gives them none of it from people.

## 4. Choices for the B7 slice (e) build, and the prediction to file with it

These are proposals for after the publish. They are not built.

1. **The sole-occupant death goes first**, because it is a credit exit and the rest only move usage.
   It reuses the move-out's exit (close, final bill through `final_bill_outcome`, void through W2_40)
   with the estate in the occupant's place. **Before that build, research how a GB supplier handles a
   deceased customer's account** (the bereavement notice, the estate's liability, how long the home
   stays void). It is not on any knowledge page yet, so per K8 it is a new page section first, and
   regulation is searched before anyone is asked (K4).
2. **Separations change headcount and usage, not only stress. Births wait for leaving home.** The
   `divorce` event already fires on its own substream, so the build gives it a demand side (one adult
   fewer) and draws nothing new. A birth cannot do the same yet. At about 0.025 people per household a
   year, with nobody leaving, births alone raise the book's mean headcount by about 0.2 over the decade
   (2.36 to about 2.6), against a published mean that stayed flat. So the birth's headcount lands
   together with item 3, the way the spell fix and the scar land together in (d).
3. **Leaving home and joining wait for an age state.** Inventing an age per occupant to have
   someone who can leave would be a number picked to fill a slot. The honest order is the age state
   first (Census 2021 age by household type, published at area level), then the flow.
4. **One control over the whole partition** (CLAUDE.md, a rare branch): on a seeded book over
   2016-2025, at least one of each implemented change fires, and the mean headcount stays inside
   2.3-2.45.

**Prediction for slices 1 and 2 (death and separation), filed before any code.** On the founder book
(774 households) over 2016-2025, sole-occupant deaths end **35 to 60 accounts**. The central figure,
0.6-0.7% of households a year x 774 x 10, is 46-54, and the band allows for a book whose single
pensioner share is not FAH's. Separations take one adult from **about 0.36% of household-years**,
about 28 events. The mean headcount depends on whether the home is re-occupied. If it is, as a move-out's home is
(an incoming household after the W2_40 void), deaths leave the mean where it was, and separations
lower it by about 0.03-0.04 (28 adults out of about 1,830 people). If the home is never re-occupied,
removing about 50 single homes raises the mean by about 0.09 (1,780 people over 724 homes is 2.45).
The build must re-occupy it. A mean that rises by more than 0.05 says the void never ends. If deaths come out under 35, the
world's single pensioner homes are under-drawn against FAH, and that is a finding about the draw and
not a reason to raise the rate. **Corrected beside the claim:** the first draft of this paragraph
(same tick, before landing) predicted that births and divorces together would move the mean by less
than 0.05. Its own birth rate gives about +0.2. That is why item 2 now holds births back.

## Sources

- ISER, *British Household Panel Survey User Manual, Volume A* (UK Data Service SN 6614),
  doc.ukdataservice.ac.uk/doc/6614/mrdoc/pdf/6614_bhps_user_manual_volume_a.pdf. "About one in six
  British households change their composition each year."
- ONS, *Families and households in the UK: 2023*: 28.4m households; 8.4m living alone, 50% aged 65+;
  2.36 residents per household; 3.6m aged 20-34 living with parents; 3.2m lone-parent families.
- ONS, *Families and households in the UK: 2016*: 27.1m households; 2.4 people per household.
- ONS, *Death registration summary statistics, England and Wales: 2023*: 581,363 deaths.
- ONS, *Young adults living with their parents* (dataset, 2023); the share at home by single year of
  age (about 57% at 20, about 10% at 30), as reported from it. Half had left by 24 in 2021 (21 in
  2011), from Census 2021 reporting.
- DESNZ NEED 2023 consumption by number of adults, via `occupancy_consumption_volume_shape_w2_13.md` §2.
