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

## 5. How a GB supplier handles a deceased customer's account (K8, before the slice (e) build)

**2026-10-19, worker tick (B7 drawn).** Item 1 of §4 asked for this before any code. Regulation
was searched first (K4). No licence condition is written for bereavement, so most of this is
published supplier practice, and the gaps are labelled.

**What a death is, for the supplier.** It is a **credit exit that has a named counterparty**. A
move-out loses its counterparty ("gone away"), and the next user is an unnamed occupier. A death
keeps one: the estate, through an executor or administrator, owes the bill up to the date of death
and the charges at the empty home after it. These are three experiences, and the build keeps them
apart:

| | who owes it | what the supplier sees | when |
|---|---|---|---|
| use up to the date of death | the estate (an unsecured debt of the estate) | a bereavement notice, a death date, usually a read "on or close to the date of death" | days to weeks after the death. **GAP:** no published lag |
| standing charge and any use while the home is empty | the estate, as the owner of the empty home | the account in the estate's name, or still in the deceased's | until the home is sold or let |
| a survivor who lived there (not a sole-occupant death) | the survivor, from the date of death | a change of account holder | at notification. Out of scope for the sole-occupant slice |

**What the rules require.**
- **No bereavement licence condition exists.** The duties that reach it are general: the Standards
  of Conduct (SLC 0, treat each customer fairly), SLC 26's Priority Services Register, whose
  temporary "life changes" category names bereavement (UKPN's published PSR terms, which follow the
  industry needs codes), and the SLC 27 ability-to-pay duties that apply to any arrears. The PSR's
  rules are in `docs/domain_artefact_library/regulatory/psr_eligibility_and_disconnection_protection.md`.
- **The estate's liability is general law, not energy law.** Bills outstanding at death are debts
  of the estate, paid before it is distributed. They come after funeral and testamentary expenses
  and after secured creditors (secondary guides: Willsafe; CPAG's adviser guidance, as the search
  returned it). One guide says utility bills rank above credit cards "by convention". That is not a
  legal ranking, because unsecured debts rank equally, and it is **not taken here**. Family members
  are not liable unless they were joint holders (`debt_and_collections.md` P6).
- **Tell Us Once does not reach energy suppliers.** GOV.UK lists the government bodies it notifies.
  Utilities have to be contacted "separately", so notification is **per supplier and voluntary**.
  Third-party services (Settld, Life Ledger, NotifyNow) have reduced the lag for the suppliers that
  joined them. **GAP:** what share of deaths reaches a supplier through each route, and how fast.

**What published practice says.**
- **A death certificate is enough to notify.** Probate is not needed at that stage. The supplier
  asks for a read near the date of death, closes the account and sends the final bill "to the
  person dealing with the deceased's estate". This comes from search summaries of the ScottishPower,
  So Energy and British Gas help pages. Each page refused the fetch or came back empty this tick, so
  none of it was read at source.
- **Collection waits for probate.** Suppliers "will often be prepared to wait until probate is
  granted before demanding payment" (CPJ Field). There is no published hold length. Probate is the
  clock in practice: HMCTS took **about 12 weeks** from application to grant at the end of 2023,
  **over 8 weeks** at the end of June 2024 and **just over 4 weeks** in December 2024 (GOV.UK press
  release, 14 Feb 2025). The application itself usually follows the death by months. **GAP:** death
  to application.
- **The home stands empty until it is sold or let.** A probate sale averages about **10.5 months**
  against about 6 for an ordinary sale (estate-agent figure, Property Reporter; **secondary, method
  not published**). Standing charges accrue all that time, on the estate.
- **A DD fails on its own.** When the bank is told of the death, the mandate is cancelled, and Bacs
  returns reason code 2, "payer deceased" (ADDACS, ARUDD). The supplier learns of the death even if
  nobody contacts it, though without a death date.

**Unknown, labelled.**
- **GAP: the share of estates that are insolvent** and leave the final bill unpaid. No published
  supplier figure (`debt_and_collections.md` P6 says the same about the scale of deceased-customer
  debt). It is the one number that decides the exit's loss. It is **not** the move-out's gone-away
  rate, because the debtor has not gone away.
- **GAP: the notification lag**, and the share of deaths no one ever reports to the supplier.
- **GAP: the empty spell for a rented home** whose sole tenant dies. The landlord ends the tenancy
  and re-lets, so it is probably nearer the W2_40 void than the 10.5-month probate sale. Not
  sourced.

**Choices for the build, and why.**
1. **The death ends the occupancy through the move-out's exit machinery, with three legs swapped**
   (`sim/customer_state_layer.py`). The close, the final read (or an estimate when none is taken)
   and the re-occupation after a void are reused. What changes: (a) the final bill's payer is the
   estate, so the **gone-away leg does not apply**; (b) the unpaid share is the insolvent-estate
   share, which is a GAP, so the code carries it as `None` with its reason and **does not borrow
   the move-out's 0.12**; (c) the empty spell is **not unnamed occupier debt**. The estate is a
   named payer for the standing charge, so it is billed and not booked as W2_12 occupier exposure.
2. **The death date is world truth.** The company sees a bereavement contact, a Bacs code-2 DD
   cancellation and a final read near the date. It does not see the date until it is told, and it
   never sees the cause. The move-out's `FORBIDDEN_TRUTH_FIELDS` discipline applies.
3. **Owner-occupied and rented homes take different empty spells**: the probate sale for an owner
   occupier, and the W2_40 void for a tenant, with the rented case named as an unsourced choice
   (F11: the shorter void errs against the company's revenue, which is the safe direction for a
   void billed to the estate).
4. **The hazard is sole-occupant mortality, on its own named substream** (`customer_state`
   namespace, `sole_occupant_death`). It only reaches households the world has as one person aged
   65 or over. The 0.6-0.7% floor in §2 is a share of all households, not a hazard per eligible
   home, so the build must derive the per-home hazard from the 65+ mortality rate. It must not
   divide the floor by the book's single-pensioner share and call that sourced.

The §4 prediction (35-60 deaths on the founder book) stands as filed.

## 6. The per-home hazard, derived, and the slice (e)1 build (2026-10-19, worker tick)

§5 choice 4 asked for the hazard per eligible home from 65+ mortality, not from the 0.6-0.7%
household floor. It is derived here from two ONS tables, both read at source this tick
(`.xlsx` downloads).

**Method.** ONS *Deaths registered in England and Wales: 2025* (annual reference tables) gives,
for 2016-2025, Table 10 age-specific death rates per 1,000 by five-year band (65-69 ... 90+) and
Table 3 deaths by single year of age. A band's population is its deaths x 1,000 over its rate, so
no separate population file is needed. Check: the implied 65+ population is 10.45m in 2016 and
11.49m in 2023, against Census 2021's 11.1m for England and Wales. From those, q(65-74) and
q(75+) are each band's deaths over its population. They are weighted by the people **living
alone** at 65-74 and at 75+ that year (ONS *Families and households in the UK: 2025*, Table 6;
2023: 1.748m and 2.466m, so 59% of people aged 65+ who live alone are 75 or over).

| year | q(65-74) | q(75+) | living alone, 65-74 / 75+ (000s) | hazard per sole-pensioner home |
|---|---|---|---|---|
| 2016 | 1.53% | 7.56% | 1,592 / 2,052 | **4.92%** |
| 2017 | 1.52% | 7.63% | 1,589 / 2,199 | **5.07%** |
| 2018 | 1.53% | 7.57% | 1,678 / 2,200 | **4.96%** |
| 2019 | 1.49% | 7.20% | 1,647 / 2,376 | **4.87%** |
| 2020 | 1.68% | 8.19% | 1,744 / 2,378 | **5.44%** |
| 2021 | 1.66% | 7.55% | 1,764 / 2,438 | **5.08%** |
| 2022 | 1.57% | 7.23% | 1,784 / 2,454 | **4.85%** |
| 2023 | 1.55% | 7.08% | 1,748 / 2,466 | **4.79%** |
| 2024 | 1.48% | 6.75% | 1,824 / 2,484 | **4.52%** |
| 2025 | 1.44% | 6.68% | 1,732 / 2,522 | **4.54%** |

**What it counts, and why it is a floor.** It assumes a person living alone at 75+ dies at the
rate of everyone aged 75+. People living alone at 75+ are older than that band on average (more
of them are widowed, at 85+), so the true hazard is higher. The deaths are England and Wales and
the weights are UK; the age mix of living alone is taken as the same. **GAP:** deaths by living
arrangement (the Census 2021 linked mortality study). The 2020 COVID year is part of the record and
stays in the table. Checked against §2: 4.2m x 4.8% is about 200k a year, inside §2's 170-210k.

**The world's eligible population is under-drawn.** Measured on the live book (426 domestic
electricity homes, `live_population()` and `build_properties`): 126 are one-person (29.6%,
TS017's 30.1%), and 39 of those have a pensioner present (**9.2% of homes**). The published share
is 4.2m of 28.4m, **14.8%**. The cause: `composition_cuts_for` draws pensioner presence
independently of household size (its docstring names the joint as a gap). But FAH publishes it:
half of the people who live alone are 65+, against the world's 31%. That is a fix to the draw, not
to this hazard. It is not made here, because it moves the daytime demand cut too. It belongs to
`W2_19_who_lives_where_money_and_composition`, whose subject is exactly the people joint the world
draws as independent marginals.

**Built (slice (e)1).** `sim/customer_state_layer.draw_sole_occupant_death`: one credit exit
(`OccupancyEnded`, payer the estate, `insolvent_share` None with its reason) plus one deemed entry
(the next occupant, start None with its reason), on the `sole_occupant_death` and `death_date`
substreams. It reaches only a one-person home with a pensioner present. A year outside 2016-2025
raises. **Not wired into the run**, so it is fail-silent until the wiring slice: that slice needs
the estate's final bill (§5 choice 1(b)) and the empty home billed to the estate (1(c)).

**Prediction, filed before the book is drawn.** Over 2016-2025, with each of the 39 eligible homes
treated as held for the whole decade, the draw gives **12 to 26 deaths** (expected about 19.5;
Poisson ± about 2 sd). Scaled to the 426 homes, §4's 35-60 on 774 is 19-33. So the draw lands at or
under the bottom of §4's band, and the shortfall is the under-drawn eligible share, not the
hazard: at the published 14.8% share it would be about 31.

**Graded (same tick, after the line above was written).** Run seed 20260724, window 2016-01-01 to
2026-01-01: **19 deaths**, one or more in every year except 2024. **Held.** The first draw raised
for 2026 on a window ending on 1 January 2026. A year with no day inside the window was being
asked for its hazard; `first_sole_occupant_death` now stops at the window's last day.

## Sources

- ONS, *Deaths registered in England and Wales: 2025* (annual reference tables,
  `annualdeathregistrations2025.xlsx`): Table 10 age-specific rates and Table 3 deaths by single
  year of age, 2016-2025. Read at source 2026-10-19.
- ONS, *Families and households in the UK: 2025* (`familiesandhouseholdsuk2025.xlsx`), Table 6:
  people living alone by age, 2016-2025. Read at source 2026-10-19.

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
- GOV.UK, *Probate waiting times halved thanks to government push* (press release, 14 Feb 2025):
  12 weeks at the end of 2023, over 8 weeks at the end of June 2024, just over 4 weeks in Dec 2024.
- GOV.UK, *What to do after someone dies: organisations you need to contact and Tell Us Once*: the
  bodies Tell Us Once notifies; utilities are to be contacted separately.
- Bacs reason codes as published by bureaux (Acquired, Nuapay, GoCardless): code 2, "payer
  deceased", in AUDDIS, ADDACS and ARUDD.
- UK Power Networks, *About the Priority Services Register*: temporary registration for life
  changes including bereavement.
- Secondary practice guides, read via search summaries only: Willsafe (*What happens to utility
  bills when someone dies*), CPJ Field (same title), Property Reporter (*Navigating the sale of a
  probate property*: about 10.5 months against about 6).
