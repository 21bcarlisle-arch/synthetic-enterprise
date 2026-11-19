# Prepayment, self-disconnection and the energy-vulnerability observables a supplier sees

**Knowledge:** prepayment-and-self-disconnection

Written 2026-11-19 for the director's steer of that morning
(`docs/staging/advisor/done/DIRECTOR_STEER_PREPAYMENT_AND_SELF_DISCONNECTION_KNOWLEDGE_FIRST_SO_THE_COMFORT_AND_HEALTH_FLOOR_CAN_BE_TESTED_2026-11-19.md`):
knowledge first (K8), so the M3 comfort and health floor can be tested on the population where real
breaches happen. Open sources only; nothing was registered for, applied for or accepted. Confidence:
H = primary document read in full; M = primary web page or a secondary source citing a primary;
L = snippet only. Every number without a source is GAP.

Read beside: `vulnerability_psr_and_ability_to_pay_2026-10-25.md` (PSR, ability to pay, the
involuntary-PPM code), `company_debt_management.md` "Self-disconnection and self-rationing" (SLC 27A
transcribed), the commons `docs/domain_artefact_library/regulatory/psr_eligibility_and_disconnection_protection.md`
§5 (W2_43 supply events, C36 response), `heating_behaviour_comfort_and_health_floors_2026-10-25.md`,
and the companion `sense_dynamic_energy_vulnerability_indices_public_documentation_2026-11-19.md`.

## 0. What the world and company do today (read from code at 4accbb828d, not run)

The steer quoted three `ASSUMPTIONS.md` rows saying fuel poverty, the prepayment split and prepayment
debt were "Not modelled". All three were stale and are corrected beside the claim in this commit:

| Piece | Where | What it does | What it asserts by omission (K2) |
|---|---|---|---|
| Who pays by prepayment | `simulation/household_segments.py` `NON_DD_PREPAYMENT_SHARE` 0.50 | About 13-14% of supply points draw a PREPAYMENT channel (half the non-DD residual, Ofgem 2026 ~13%/13%) | Drawn **independently** of income, tenure, heating fuel and property efficiency (`payment_method_dynamics` simplification 3): no joint structure |
| Fuel poverty | `household_segments.fuel_poverty_for_customer` | A flag at DESNZ's rate by payment channel (PPM 22.3%) read by arrears and final-bill engines | Not coupled to EPC band or income, so not LILEE by construction |
| A stock prepayment household's meter | nowhere | It pays before use; nothing else | **Zero** top-ups, emergency credit, friendly hours, standing-charge accrual, supply interruptions. 27A's "every PPM customer" has no event to identify for ~14% of the book |
| A meter fitted for debt | `payment_method_dynamics` (W2_42/W2_43), `CollectionsJourneyDesk` (C36) | Recovery at Ofgem's 2025 mean weekly rate; weekly self-disconnection draw at 0.019 (derived range 0.019-0.061); company watches and answers with ASC | **Unreached**: `method_prepayment_offer_take_up_share` ships at 0, so no meter moves. Duration and top-ups not drawn |
| Self-rationing | `simulation/self_rationing.py` (W2_8) | A hidden pay-but-don't-heat state with a consumption drop below the TDCV floor | **Twin harness only** (`tools/couple_w2_8_c10.py`); the run's demand never falls for rationing |
| Heating and cold | heating page | Setpoint around 20°C by band; a 1°C turn-down refused below 18°C | No indoor temperature consequence of being off supply; no floor for older/ill households |

**So the world asserts zero prepayment harm.** In the shipped run no household self-disconnects, none
rations, and none is cold because it could not top up. K2: that is the one value we know is wrong
(Ofgem counts 564,191 smart-PPM electricity customers self-disconnecting in Q2 2026 alone). Until it
changes, the M3 comfort-and-health floor cannot be breached by a prepayment household, so the floor
test cannot fail on the population where real breaches happen.

## 1. Prepayment share of GB domestic customers, 2016-2025, and who has it

**This closes the gap in `gb_payment_method_migration_rates.md` (§2: "the SC-vs-PPM split of that
remainder is still NOT ESTABLISHED").** DESNZ QEP tables 2.4.2 (standard electricity), 2.4.3 (Economy
7) and 2.5.2 (gas) give Credit / DD / Prepayment %, GB, annual. Publication 29/09/2026, data to Q2 2026.
Method: a sample of suppliers, uplifted to Ofgem's total customer numbers. The figures are shares of
customers on that meter type, not of households.

| Year | Std elec C/DD/**PPM** % | E7 elec C/DD/**PPM** % | Gas C/DD/**PPM** % |
|---|---|---|---|
| 2016 | 25.75 / 59.5 / **14.75** | 25.75 / 52.25 / **22** | 25 / 61 / **14** |
| 2017 | 23.5 / 61.5 / **15** | 24.5 / 54 / **21.5** | 22 / 64 / **14** |
| 2018 | 20.5 / 62.75 / **16.75** | 21.75 / 56.5 / **22** | 18 / 66 / **16** |
| 2019 | 19 / 66 / **15** | 20.75 / 57 / **22** | 19 / 67 / **14** |
| 2020 | 17 / 69 / **14** | 19 / 62 / **19** | 16 / 70 / **14** |
| 2021 | 18 / 68 / **15** | 19 / 60 / **21** | 16.25 / 69.75 / **13.75** |
| 2022 | 17 / 69 / **14** | 19 / 62 / **19** | 17 / 70 / **13** |
| 2023 | 17 / 69 / **14** | 19 / 62 / **19** | 17 / 70 / **13** |
| 2024 | 16 / 71 / **13** | 17 / 66 / **17** | 16 / 71 / **13** |
| 2025 | 16 / 72 / **12** | 16 / 71 / **13** | 16 / 73 / **12** |

Sources: <https://assets.publishing.service.gov.uk/media/6ab5405f997a4b2950cceecf/table_242.xlsx>,
`.../6ab54077fe72ed1e2b02f054/table_243.xlsx`, `.../6ab5408bfe72ed1e2b02f055/table_252.xlsx`. Index page:
<https://www.gov.uk/government/statistical-data-sets/quarterly-domestic-energy-price-stastics>. Read
from the XLSX "(Annual)" sheets, GB rows. Confidence H. Each table also has a quarterly sheet
(2005 onward) and a regional split by PES region.

| Figure | Quote | Source | Date | Conf. |
|---|---|---|---|---|
| PPM customer counts, 2017 | "around 4.5 million electricity and 3.5 million gas prepayment meter customers in 2017" | Ofgem, *Prepayment self-disconnection and self-rationing: a call for evidence*, §2.1, <https://www.ofgem.gov.uk/system/files/docs/2018/11/self-disconnection_and_self-rationing_a_call_for_evidence_final.pdf> | Nov 2018 | H |
| PPM customer counts, 2019 | "a reported 4.3 million electricity and 3.4 million gas PPM consumers" | Ofgem, *Self-disconnection and self-rationing decision*, §1.10, <https://www.ofgem.gov.uk/system/files/docs/2020/10/self-disconnection_and_self-rationing_decision.pdf> | 19 Oct 2020 | H |
| Smart share of the PPM stock | 2017: "Of all PPMs installed in 2017, around 23% were smart" (CfE §2.11). 2019: "Of all PPMs currently installed, around 32% are smart" (Ofgem *Vulnerable consumers in the energy market 2019*). 2026: "About two-thirds of PPM customers have smart meters" (debt and arrears indicators page, paraphrased by the fetch tool). Of involuntary-route installs, smart PAYG was "81% during the restart monitoring period between January 2024 and August 2026" (Ofgem *PPM Protections: discussion paper* §3.3) | CfE 2018; <https://www.ofgem.gov.uk/system/files/docs/2019/09/vulnerable_consumers_in_the_energy_market_2019_final.pdf>; <https://www.ofgem.gov.uk/data/debt-and-arrears-indicators>; <https://www.ofgem.gov.uk/sites/default/files/2026-10/PPM-discussion-paper-2026.pdf> | 2018-2026 | H (2017, 2019, 81%); M (two-thirds) |
| Tenure, England 2022-23 | "Social renters were more likely to pay via pre-payment meter (36%) compared to private renters (13%) or owner occupiers (2%)" (electricity and gas together). Social renters' electricity: 41% with no savings against 22% with savings; 44% with dependent children against 32% without; 41% receiving housing support against 29% not | EHS 2022-23 *Affordability and cost of living fact sheet*, Annex Tables 1.7-1.8, <https://www.gov.uk/government/statistics/english-housing-survey-2022-to-2023-affordability-and-cost-of-living-fact-sheet/english-housing-survey-2022-to-2023-affordability-and-cost-of-living-fact-sheet> | 2024 | M |
| Tenure, England 2021-22 | "Within the social rented sector, 38% pay for gas and 40% pay for electricity by pre-payment meter … private rented sector, where 19%". Social renters who find rent very difficult to pay: "56% for electricity, 50% for gas" | EHS 2021-22 *Social rented sector*, <https://www.gov.uk/government/statistics/english-housing-survey-2021-to-2022-social-rented-sector/english-housing-survey-2021-to-2022-social-rented-sector> | 2023 | M |
| Tenure and income, Scotland | "17.9% of households have prepayment meters (421,000 households)"; "42.7% of households in the social sector … 21.3% [private] … (5.4%)" owner-occupied; 21.9% of households on incomes under £199/week | Citizens Advice Scotland, *Frontline perspectives: clients' journeys with prepayment meters* (citing SHCS), <https://www.cas.org.uk/sites/default/files/2025-02/ppm_report_13.02.23.pdf> | Jan 2023 | M (secondary to SHCS) |
| Fuel poverty by electricity payment method, England 2025 | "pre-payment electricity meter was 17.9%, compared with 12.7% for standard credit and 8.1% for direct debit"; PPM households have "the lowest median income of £19,100", an average gap of £395 and a median floor area of 70 m². DESNZ: the gap is "driven by the lower incomes … rather than the tariff itself" | DESNZ, *Annual fuel poverty statistics report 2026 (2025 data)*, §3.4.1, <https://assets.publishing.service.gov.uk/media/6a733816201b38b4dc3c2854/2026-fuel-poverty-statistics-report.pdf> | Mar 2026 (republished Aug 2026) | H |
| Fuel poverty by payment method, England 2022 | "gas – 27.2 % PPM, 9.7 % direct debit, electricity – 27.8 % PPM, 10.5 % direct debit" | Fawcett et al. 2024 (below), citing DESNZ 2022 | 2024 | M |
| Fuel poverty rate by tenure, England 2025 | private rented "17.2%"; owner-occupied with a mortgage 6.5%, outright 6.6%; social-housing median equivalised income £18,900 | DESNZ 2026 report §3.2.1 | Mar 2026 | H |

## 2. Prepayment meter mechanics as a supplier runs them

| Figure | Quote | Source | Date | Conf. |
|---|---|---|---|---|
| Emergency credit amount: not prescribed | "We maintain that we should not prescribe credit amounts … suppliers are best placed to assess the value of emergency credit and we do not want to encourage a potential race to the bottom by setting a minimum amount" | Ofgem 2020 decision §3.11 | Oct 2020 | H |
| Friendly hours: not prescribed | "we are not prescribing the hours of friendly credit, but rather require suppliers to offer this to customers overnight, at weekends and public holidays" | Ofgem 2020 decision §3.11 | Oct 2020 | H |
| ASC definition (SLC 27A.9) | "'Additional Support Credit' means a fixed amount of credit provided to a Domestic Customer in a Vulnerable Situation when that Domestic Customer's Prepayment Meter credit runs low or runs out to ensure continuity of [gas/electricity] supply or return on supply" | Ofgem 2020 decision, p.26 | Oct 2020 | H |
| ASC trigger (SLC 27A.5) | "on each and every occasion on which a licensee identifies that a Domestic Customer who uses a Prepayment Meter and who is in a Vulnerable Situation has Self-Disconnected or is Self-Disconnecting and/or … has Self-Rationed … must offer Additional Support Credit … in a timely manner" | Ofgem 2020 decision, p.26 | Oct 2020 | H |
| Emergency credit actually given, 2018 (supplier RFI) | "on average customers were provided with £55 worth of electricity and £15 worth of gas in emergency credit per customer in 2018 … around 1.6 million electricity and 1.5 million gas customers accessed emergency credit in 2018". That is £4.60 and £1.25 a month; "the vast majority of emergency and friendly-hours credit is repaid upon the customer's next top-up" | Ofgem, *Self-disconnection and self-rationing: final impact assessment*, <https://www.ofgem.gov.uk/system/files/docs/2020/10/self-disconnection_and_self-rationing_final_impact_assessment.pdf> | Oct 2020 | H |
| ASC actually given (RFI) | "average amount of additional support credit provided per customer was £26.81 for electricity and £25 worth of gas credit" | Ofgem final IA 2020 | Oct 2020 | H |
| Friendly credit not available on all meters | "traditional gas PPM's do not provide the friendly-hours credit functionality … some of the older electricity meter types such as KBA and KBB, smartcard and token do not provide friendly-hours credit" | Ofgem final IA 2020, fn 22 | Oct 2020 | H |
| Supplier wait before contacting a non-vending customer (pre-2020) | "suppliers can wait between 14-111 days before contacting a customer" | Ofgem final IA 2020, fn 21 | Oct 2020 | H |
| Emergency credit by supplier, Jan 2026 | British Gas £10/fuel; EDF £10; E.ON Next £10 (£5 on some electricity meters); Octopus smart £10, traditional £20 gas / £10 electricity; OVO £15; **Scottish Power "£10 per fuel in summer and £30 per fuel in winter"**; Utilita £15; E smart £15, traditional £10; UW smart £10, traditional £20 | Which?, *Is a prepayment energy meter right for you*, tables "Information correct at January 2026", <https://www.which.co.uk/reviews/cutting-your-energy-bills/article/is-a-prepayment-energy-meter-right-for-you> | article 3 Nov 2026 | M (secondary compilation) |
| Friendly hours by supplier, Jan 2026 | British Gas "6pm and 9am weekdays, all day at weekends and bank holidays"; E.ON Next smart 4pm-10am; Octopus smart summer 4pm-10am, winter 3pm-9am; OVO smart 9pm-9am weekdays; Scottish Power smart 6pm-11am Nov-Mar, 7pm-midday Apr-Oct (Mon-Sat); Utilita 2pm-10am weekdays and all weekend; EDF smart 5pm-10am in winter. **Traditional gas PPMs at E.ON Next, Octopus, OVO, Scottish Power and UW: "No friendly credit."** | Which? (same) | Jan 2026 | M |
| Utilita friendly hours as used in research | "2 pm to 10 am the next day on weekdays and all day on Saturdays and Sundays, leaving a short 4-h day-time period on weekdays when households could experience self-disconnection" | Fawcett et al. 2024 §4 | 2024 | H |
| ASC bad-debt allowance in the cap | "a temporary ASC allowance into the price cap, worth £8.77 per dual fuel PPM customer per year", from Aug 2023; extended beyond Sept 2024 | Ofgem, *ASC extension decision letter*, <https://www.ofgem.gov.uk/sites/default/files/2024-08/ASC_Extension_Decision_Letter_0.pdf> | Aug 2024 | H |
| Debt recovery through the meter, actual rate | Mean weekly recovery from customers who had a PPM installed to repay debt, Jan-Dec 2025: electricity **£6.01** (range £2.69 Utilita to £17.17 Tru Energy); gas **£4.40** (range £2.57 Utilita to £6.03 ScottishPower). Each supplier's figure is weighted by its new PPMs installed for debt | Ofgem, *Debt and arrears indicators*, <https://www.ofgem.gov.uk/data/debt-and-arrears-indicators> | page carries Q2 2026 data | M (page text read through the fetch tool; values match the repo's existing `company_debt_management.md`) |
| Share of indebted customers repaying through a PPM | Q2 2026: electricity 40% (44% in Q2 2025), gas 36% (39%). The ORE evaluation gives 41% / 38% | Debt and arrears indicators; Ofgem *PPM Process Evaluation Report*, <https://www.ofgem.gov.uk/sites/default/files/2026-10/PPM-Process-Evaluation-Report_0.pdf> | 2026 | M/H |
| How the meter splits a top-up (practice, not rule) | DebtBuffer, 2022: EDF, Octopus, Scottish Power, SSE and E.ON "take 70% of gas top ups and 100% of electricity top ups"; British Gas "90% of gas and 100% of electricity"; Bulb 30% / 100%. British Gas web page: "we'll take 90% to pay towards your debt and leave 10% for your gas". CPAG: suppliers leave "a certain minimum percentage of your credit – typically 30 per cent" | LBC <https://lbc.co.uk/business/6eb0aacb164a4308982c2dbfae900f6c>; askcpag (page now 404) | 2022 | **L, snippet only** |
| Standing charge accrues while off supply | "You still have to pay the daily standing charge even if you don't have any credit on your meter … When you next top up, you'll have to pay back all the standing charges that you owe." Worked example: a £20 top-up cleared £17.64 of owed standing charges, leaving £2.36 | Citizens Advice Scotland, *Decide if prepayment is right for you*, <https://www.citizensadvice.org.uk/scotland/consumer/energy/energy-supply/your-energy-meter/decide-if-a-prepayment-meter-is-right-for-you/> | undated (live 2026) | M |
| Fuel Direct / UC third-party deduction | "an amount equivalent to 5% of the benefit unit's Universal Credit Standard Allowance" per debt, plus an estimate of ongoing consumption; at most three third-party debts; overall cap of 40% of the standard allowance, excluding ongoing fuel. Legacy-benefit figure £3.70/week per fuel (Unison guide; stale) | StepChange background note / Shelter, via search | various | **L, snippet only** |
| Involuntary PPM trigger | debt outstanding "more than 3 months" and at least "£200 per fuel" | Ofgem discussion paper 2026, Annex; Ofgem 2023 decision | 2023/2026 | H |
| Smart PAYG legal basis for debt installs | statutory right to install a PPM to recover debt: "Gas Act 1986 (Schedule 2B) and the Electricity Act 1989 (Schedule 6)"; warrant under the "Rights of Entry (Gas and Electricity Boards) Act 1954" | Ofgem discussion paper §3.13 | 28 Oct 2026 | H |
| PPM price relative to other methods, Oct-Dec 2026 cap | "DD £1,723; PPM £1,678; SC £1,861"; PPM "around £45 cheaper than Direct Debit (DD) and £183 cheaper than Standard Credit" | Ofgem discussion paper §3.2, fn 2 | 28 Oct 2026 | H |

## 3. Self-disconnection: how often, how long, when, and who

**Definitions.** Ofgem: self-disconnection "occurs when PPM customers experience interruption to
their energy supply" (call for evidence §1.1). Ofgem treats an interruption of more than 3 hours as
"severe", and says one "of less than three hours may predominantly be people that had forgotten to top
up" (debt and arrears indicators page). Self-rationing means keeping supply on and cutting
consumption. Ofgem placed **no identification duty** on suppliers for self-rationing (2020 decision).

| Figure | Quote | Source | Date | Conf. |
|---|---|---|---|---|
| Survey prevalence, 2017-2019 | 2018 CES: "one in ten of those with a prepayment meter temporarily disconnected … 350,000 gas and 450,000 electricity customers" (n=556 PPM responses of 4,064 interviews). 2019 CES: "14% of PPM customers self-disconnected at least once last year, an increase on the previous year where 10%" | CfE 2018 §2.10; final IA 2020 p.12-13 | 2018-2020 | H |
| Supplier data, traditional meters, 2018 | "12% of their gas PPM consumers and 8% of their electricity PPM consumers with a traditional meter self-disconnected in 2018" (six suppliers). Non-vending is the usual proxy: "monitoring of self-disconnection remains limited and in most cases uses non-vending as a proxy" | Ofgem VCEM 2019; final IA 2020 fn 16 | 2019-20 | H |
| Smart PPM, 2017 | "14% of smart PPM customers self-disconnecting in 2017" | CfE 2018 §2.11 (citing CA *Switched On*) | 2018 | H |
| **Duration from survey** | share of self-disconnectors off supply for **more than 7 hours: "9% of electricity customers, 18% of gas customers"** | Ofgem final IA 2020, cost section (citing the Consumer Engagement Survey) | Oct 2020 | H |
| Affordability as the reason | "21% of customers or c.140,000 households self-disconnected for affordability reasons in 2017. 88% of these households contained either a child or someone with" a long-term health issue. The main reasons were forgetting or not knowing credit was low | CfE 2018 §2.4 (citing CA 2018) | 2018 | H |
| Seasonal gas self-disconnection | "customers who self-disconnect from their gas supply on a seasonal basis are more likely to do so because of an ongoing affordability issue" | Ofgem final IA 2020 p.16 | Oct 2020 | H (qualitative) |
| **Ofgem smart-PPM monitoring, Q2 2026** | Electricity: 564,191 customers self-disconnected at least once; 368,659 had at least one disconnection over 3 hours; 2,038,289 self-disconnections in total. Gas: 304,428; 245,056; 958,551. Counts cover all suppliers from Q3 2023; "Before Q3 2023 … largest eight PPM suppliers, accounting for 98%". The page's own % changes have an unclear baseline | Ofgem debt and arrears indicators | Q2 2026 | M (fetch-tool summary; chart CSV not pulled) |
| Ofgem smart-PPM, Q1 2023 | over-3-hour self-disconnectors: electricity 269,351 (+25%), gas 534,462 (+13%) | inkl / press report of Ofgem data | 2023 | **L, snippet only** |
| Smart PPM, quarterly rate | "at least one self-disconnection per quarter was 18–28 % for electricity and 16–35 % for gas in the quarters Q4 2021 – Q2 2023" (Ofgem figures as cited) | Fawcett et al. 2024 §2 | 2024 | M |
| Trend after the 2023 rules | "a 36% decrease in severe self-disconnection" ("over 3 hours", smart PPM, since 2023). Electricity "rose during the moratorium but has since stabilised" | Ofgem ORE, *PPM Process Evaluation Report*, Key finding 3 and §3.5-3.6 | 28 Oct 2026 | H (Figure 4 values not in text) |
| **Frequency and duration, smart PPM panel (Utilita, about 10,100 households, 2019/20-2022/23)** | "On average, 63 % of all households self-disconnected in any year, and the households that self-disconnected did so five times each year for a total of 28 h". Median (IQR) hours for those who disconnect: 28 (5.3-164); median events 5 (2-17). Age 18-25: 78%, 51 h, 8 events. Age 65+: 31%, 7.7 h, 2 events. PSR: 66%, 41 h. EPC F-G: 68%, 37 h. "4.1 % have at least 240 h of disconnection per year, with at least four events of 12 h or more. This rose to 6.6 % … in 2022/23". The worst-affected 25%: "10 times in the year for a total of 965 h". An event is counted if it lasts >5 min | Fawcett, Palmer, Terry, Boardman, Narayan, *Using smart energy meter data to design better policy: Prepayment meter customers, fuel poverty and policy targeting in Great Britain*, ERSS 116 (2024) 103666, Table 7, <https://ora.ox.ac.uk/objects/uuid:db708148-c98c-49a4-8be3-c0b00e85123e> | 2024 | H (one supplier, not a population sample; the authors say its rates are "about twice as high as those provided by Ofgem for smart PPMs") |
| **Gas vs electricity duration; cold weather** | "gas disconnections were three to four times longer than electricity, rising to eight times longer in 2022/23". "more homes disconnected from the gas meter during cold periods, compared to before or afterwards". In the 7-21 Dec 2022 cold spell (North West), "Over 20 % of PSR homes self-disconnected … for an average of nearly an hour a day" | Fawcett et al. 2024 §5.3-5.4, Table 8 | 2024 | H |
| Consumption response, 2022/23 | annual gas per household "fell by 20 %, while electricity use fell by 3 %, compared with 2019–20" (smart PPM). Utilita's traditional PPMs: an electricity drop "of 21 % compared to the 3 % for smart PPMs" | Fawcett et al. 2024 | 2024 | H |
| CA survey, 2022 (re-read) | "3.2 million" ran out of credit in 2022, "one person every 10 seconds"; "more than two million … disconnected at least once a month"; "19%" of those cut off "went at least 24 hours"; "18%" of households with a disabled or long-term-ill member who ran out "went two days or more"; 600,000 moved to PPM for debt in 2022 (380,000 in 2021). Yonder, n=4,384, 6-15 Dec 2022, ×2.4 people per household | Citizens Advice press release, <https://www.citizensadvice.org.uk/about-us/about-us1/media/press-releases/millions-left-in-the-cold-and-dark-as-someone-on-a-prepayment-meter-cut-off-every-10-seconds-reveals-citizens-advice/> | 12 Jan 2023 | M |
| The "8,500" figure (an advice-client count, not prevalence) | "More than 8,500 people couldn't afford to top up their prepayment meter in the first two months of 2023 alone, this is three times the number in 2022 and more than the whole of 2021". CA "helped more than 27,000 people in 2022" (27,521 in the CA release) | DCC, *Tackling Fuel Poverty through Smart Metering* v1.0 p.5, citing the "CA cost of living data dashboard" | Jun 2023 | M |
| CA client cases, 2023 | "almost 22,000" PPM self-disconnection cases in 2023, "+42%" on 2022; December the worst month, ">3,500" | Utility Week reporting CA data | 2024 | **L, snippet only** |
| CA 2014 survey (historical) | "One in every six prepayment meter customers has cut off their energy supply because of high costs"; "as little as an hour to as long as several months"; "Most firms contact vulnerable customers a month after their last top-up" | CA press release, *1.62 million prepayment energy consumers cuts off each year*, <https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/1-62-million-prepayment-energy-consumers-cuts-off-each-year/> | 30 Sep 2014 | M |
| Winter seasonality in advice demand (Scotland) | page views on being unable to top up spike in winter: "January 2021 (158% increase from December) and December 2022 (97% increase from November)" | CAS *Frontline perspectives* | Jan 2023 | M (advice proxy, not disconnection) |

## 4. Rationing that does not show as disconnection

| Figure | Quote | Source | Date | Conf. |
|---|---|---|---|---|
| Rationing prevalence, survey | "55% of PPM customers restricted their energy usage; … 37% of non-PPM users". Of these, "30% … severely – restricting their consumption to just a few hours a day, or just a few days within a month"; "8% of users have gone without using their heating for the entire duration of winter" | Ofgem CfE 2018 §2.2, §2.7 (citing Christians Against Poverty 2016) | 2018 | M |
| Mansilla, Gallage, Sanchez-Campos: what is published | Extended conference abstract only. The Trade-off Proxy Variable (TPV) is built from three flags: (1) "energy rationing … consumption significantly falls below a baseline adjusted for weather and property characteristics"; (2) "inefficiency-consumption mismatch … households in poorly rated properties that display unusually low energy consumption" (suppressed demand); (3) "extreme heating self-disconnection … zero gas supply during freezing weather". A household is "acutely vulnerable when two or more signals co-occur". The model is supervised ML with SHAP. The one finding: indicators under-represent "'house-rich but cash-poor' demographics who objectively engage in extreme rationing but underreport subjective hardship". **No thresholds, sample sizes or rates are published**: "At the conference, we will present the complete mathematical formulation of the three behavioural flags" | IJPDS, DOI 10.23889/ijpds.v11i4.37834, <https://ijpds.org/index.php/ijpds/article/view/3784> (PDF header "(2025) 10:4:05", footer "August 2026", landing page 11(4) 2026) | 2026 | H (as to content); the citation's volume and year are inconsistent |
| Low-use group, smart PPM panel | "7 % of households use scarcely any energy, and no gas, for heating" | Fawcett et al. 2024 abstract | 2024 | H |
| SERL by payment method | No SERL statistical release found that splits consumption by payment method. Vol 1 and Vol 2 split by PV and other factors only | SERL Stats Report Vol 2, <https://discovery.ucl.ac.uk/id/eprint/10189780/7/SERL_Stats_Report_Vol_2_rev.pdf> (search result) | 2024 | L |

## 5. Smart-meter events a supplier (or DCC) can see

| Item | Quote | Source | Date | Conf. |
|---|---|---|---|---|
| DCC v1.0: indicators named | "visibility of households on emergency credit and those who have self-disconnected" (Exec summary). System data includes "descriptions and timings of transactions including prepayment top ups, low credit alerts and outages" (§3). Listed "Financial difficulty indicators": "are pre-payment meter top-ups occurring more frequently, are households transferring credit between electricity and gas, volume of low or emergency credit activations or self-disconnections from the system". Also "Payment patterns … scale and frequency of remote switching between states" | DCC, *Tackling Fuel Poverty through Smart Metering*, Version 1.0, June 2023 (live URL now 404; read from the Wayback copy of 18 Jul 2024: <http://web.archive.org/web/20240718192304/https://www.smartdcc.co.uk/media/w4rpfe4g/tackling-fuel-poverty-through-smart-metering-dcc-report.pdf>) | Jun 2023 | H |
| Who sees what | "The letter" is message content such as consumption or "amount added to a pre-payment meter", which is "encrypted and only accessible to energy companies or third-party users to whom consumers have given their consent". "The envelope" is system data: "where it was sent and to which device, at what time and whether it arrived safely", "retained centrally within the DCC's system"; "no mechanism exists for external access" | DCC v1.0, Appendix 2 | Jun 2023 | H |
| Consumption not in system data | "Energy consumption … (N.B. not currently available without consumer consent)" | DCC v1.0 §3.2.2.1 | Jun 2023 | H |
| **Named alert codes (2025 edition)** | Figure 2 shows a household's sequence: **810D** "Combined credit below low credit threshold (Prepayment mode)" → **8119** "Emergency credit has become available (Prepayment mode)" → **81AA** "Emergency credit Exhausted", repeating 9-20 Aug 2023 and "leading to a self-disconnection and spells without any power". Data shared monthly, aggregated to Output Area (~40 households), from five suppliers (EON, Good Energy, Octopus, Utilita, EDF), "~32% of the installed base of pre-payment smart meters" | DCC, *Tackling Fuel Poverty through Smart Metering* (2025 edition), <https://www.smartdcc.co.uk/media/w4rpfe4g/dcc-fuel-poverty-white-paper-25-june-v7_-dig.pdf> | 2025 (article 31 Jul 2025) | H |
| Smart PPM functions monitored by Ofgem | Social Obligations Reporting from 2016 covers "provision of emergency credit, friendly credit, low credit alerts and high consumption alerts" | Ofgem CfE 2018 §2.13 | 2018 | H |
| Supplier practice using smart data | E.ON "Artemis" ranks customers by "how long the customer has been off supply, the level of gas and electricity dependency and if there are any known vulnerabilities" | Ofgem VCEM 2019 | 2019 | H |

## 5a. GAP list (sources)

- GAP: a **population** distribution of self-disconnection duration and frequency. Fawcett covers one
  supplier, Utilita, about 10k smart PPM households. Ofgem publishes only counts of at least once,
  over 3 hours and total. Ofgem's Q2 2026 counts have no published denominator (smart PPM customers
  per fuel), so no per-customer rate can be formed from them. Do not divide them by the QEP shares.
- GAP: Ofgem's smart-PPM self-disconnection series as numbers, Q3 2023 to Q2 2026. The values sit in
  page charts with CSV downloads that were not pulled. The ORE Figure 4 values are not given in text.
  The baseline for the page's own % changes is unclear.
- GAP: **any regulatory cap on the share of a top-up, or the £/week, recovered through a PPM**. Neither
  the 2020 nor the 2023 decision sets a number; SLC 27 ability-to-pay applies. Only the realised means
  (£6.01 / £4.40) and 2022 press figures on supplier split practice (snippet only) exist.
- GAP: the current UC Fuel Direct £/week (5% of the standard allowance; amount not retrieved).
- GAP: whether standing charge accrues during **emergency** credit (as opposed to fully off supply).
  Sources conflict (MSE against WDH, snippet only). It is supplier and meter specific.
- GAP: emergency credit and friendly hours for **2016-2025 as a series**. Only the 2018 RFI averages
  (£55 / £15 a year) and the Jan 2026 Which? table exist.
- GAP: the Mansilla et al. flag thresholds, sample size and prevalence rates. They are unpublished,
  with the formulation reserved for the conference.
- GAP: a SERL release splitting consumption or rationing by payment method. None was found.
- GAP: seasonality of self-disconnection as a monthly or quarterly rate for the whole market. There is
  only Fawcett's cold-spell result, Ofgem's qualitative "seasonal gas" line, and advice-demand
  proxies.
- GAP: a PPM share by income decile or quintile for GB from an official source. This repo's
  `company_debt_management.md` gives "47% … lowest income quintile" without re-verification here. EHS
  (by savings, children and housing support) and SHCS (by weekly income band) are the nearest.
- GAP: the GB 2016-2025 number of PPM customers per year. Only spot counts exist (4.5m/3.5m 2017;
  4.3m/3.4m 2019). QEP gives shares only.
- GAP: *Kept in the dark* (CA, Jan 2023), the full report. The Wales PDF URL returned HTML; only the
  press release was read.

## 6. The gated SENSE indices, from public documentation only

Full reading: the companion note. In brief:
- **Owner and content.** Energy Systems Catapult, published 15 Nov 2026 (status draft). Four datasets,
  not three: three from DCC smart-PPM events (weekly counts of top-ups, low-credit alerts, emergency
  credit and supply disablement; monthly distributions of the delay from an adverse alert to the
  customer's response; an annual count of homes with repeated long delays, classed Occasional,
  Recurring or Persistent) and one from FINDS/NatWest banking data (fuel poverty and fuel stress, 13-week
  rolling). Event codes, delay thresholds and fuel split: GAP (methodology inside the dataset).
- **Area and period.** MSOA (England and Wales), Intermediate Data Zones (Scotland). Calendar 2025 only;
  "One off". Smart meters only.
- **Access and terms.** "Safeguarded (fast-tracked)": an access request from a SENSE account. Licence:
  royalty free, "academic and research purposes only (unless stated otherwise)", UK only, revocable;
  no redistribution; outputs publishable with 14 days' notice and cells over 5; **clause 6.1 needs
  explicit permission to generate synthetic data from it**, which a world calibrated to it may be.
  Whether a commercial applicant qualifies: GAP.
- **Open area-level sources.** Ward, Singleton, Robinson and Rowe (*Regional Studies, Regional Science*,
  2025, open access): eight census and VOA indicators by LSOA, 2011 against 2021; 5,530 LSOAs (15.97%)
  entrenched; no smart-meter or prepayment inputs; data on request. JRC (JRC140609, Dec 2024):
  building-performance gap with adaptive capacity, NUTS1, 22 EU states, no GB data. DESNZ sub-regional
  fuel poverty by LSOA, annual. Ofgem's quarterly smart-PPM counts are GB-only with no area split.
- **Two open papers that cover most of what SENSE would add.** Fawcett et al. 2024 (frequency and
  duration, §3) and Longden 2025, *Energy Economics* 148, 108678 (600,000+ gas PPM customers over seven
  winters; top-ups and self-disconnection respond to cold below about -3.8 to -5.6°C by region).

**Judgement (the steer's step 2).** SENSE fills one gap open sources leave: a market-wide distribution
of how long and how often households stay off supply, by week, for 2025. That gap matters to the floor
test, but it does not block the first version of it: Fawcett's distribution and Ofgem's over-3-hour
share bound duration from two sides (§7.3), and the first build (§7.5) can carry that bound as a named
range. So no access question is raised to the director now. It is raised, as one yes-or-no line with
a recommendation, if a build shows the world's floor result swings across that range; and any
application would need the 6.1 synthetic-data permission and a reading of whether a commercial
company is eligible. Both are G5 decisions, not this seat's.

## 7. What the world needs to put prepayment households and self-disconnection in (a fidelity scope, not a build)

Each part says what this page establishes (E), what it bounds but does not pin (B), and what is GAP.
Any build follows K8 and the baseline/curriculum split (R13); where a part is a population mix, the
mix is the director's.

**7.1 Population share and its joint structure.**
- E: the share. QEP tables 2.4.2/2.4.3/2.5.2 give GB prepayment 2016-2025 by fuel and meter type
  (standard electricity 14.75% → 12%; E7 22% → 13%; gas 14% → 12%). The world's ~13-14% is inside
  the band; it is flat over the decade where the record falls by 2-3 points.
- E: tenure. England 2022-23: social renters 36%, private renters 13%, owner-occupiers 2% (EHS).
- E: fuel poverty by payment method. 17.9% PPM / 12.7% SC / 8.1% DD (DESNZ 2026, 2025 data). The world
  carries the 2024 figures (22.3/18.5/8.8); a dated series is the fidelity fix, not a new number.
- B: income. PPM households have the lowest median income (£19,100, DESNZ 2026); SHCS gives Scotland by
  weekly income band. No GB PPM share by income quintile from an official source.
- GAP: the joint table of payment method × tenure × heating fuel × EPC band × income. Every marginal
  exists; the joint does not, in anything read here. The world draws the method independently of all
  four, which is the one structure we know is wrong: a prepayment household in the world is no more
  likely to rent socially than anyone else.

**7.2 The payment mechanism.**
- E: the rules. Emergency and friendly-hours credit for every PPM customer (27A.2); amounts and hours
  not prescribed (2020 decision §3.11); ASC on each occasion for a vulnerable household (27A.5);
  standing charge keeps accruing off supply and is recovered at the next top-up (Citizens Advice).
- B: the amounts. Emergency credit £55 electricity / £15 gas per customer a year in 2018 (Ofgem RFI);
  £10-15 per fuel at most suppliers in Jan 2026, £30 in winter at one (Which?). Friendly hours roughly
  afternoon-to-morning plus weekends; none on traditional gas PPMs at five suppliers.
- B: debt recovery on the meter. £6.01 / £4.40 a week (2025 means, range £2.69-£17.17). No regulatory
  cap on the share of a top-up taken (GAP); 2022 supplier splits are snippet only.
- B/GAP: top-ups. Longden 2025 (600,000+ gas PPM customers) reports most top-ups are £20 or less; no
  published distribution of top-up amount or interval. The SENSE weekly top-up counts (2025, MSOA)
  are the only population source found, and they are gated.

**7.3 The household's response to cost and cold.**
- E: frequency and duration, one supplier. Fawcett et al. 2024 (Utilita smart PPM, ~10,100 homes,
  2019/20-2022/23): 63% self-disconnect in a year, median 5 events, 28 hours; 4.1% (6.6% in 2022/23)
  off 240+ hours; 18-25s 78%/51h, 65+ 31%/7.7h; PSR 66%/41h; EPC F-G 68%/37h. The authors put these at
  about twice Ofgem's rates.
- E: the market counts. Ofgem smart-PPM, Q2 2026: 564,191 electricity customers at least once, 368,659
  over 3 hours, 2,038,289 events; gas 304,428 / 245,056 / 958,551. No published denominator.
- B: duration across the market. 9% (electricity) and 18% (gas) of self-disconnectors off more than
  7 hours (2019 survey); 65% of electricity and 80% of gas self-disconnectors over 3 hours (Q2 2026,
  derived from the two Ofgem counts, same quarter, same population).
- B: cold. Gas outages run 3-4x longer than electricity (8x in 2022/23); more homes cut gas in cold
  spells; over 20% of PSR homes off for nearly an hour a day in the Dec 2022 cold spell (Fawcett).
  Longden 2025 finds top-ups and self-disconnection respond to cold below about -4 to -6°C (§6).
- B: rationing without disconnection. 55% of PPM customers restricted use, 30% of them severely
  (CAP 2016, via Ofgem 2018); 7% of a smart-PPM panel use scarcely any energy and no gas for heat.
- GAP: the market-wide seasonal shape as a rate (the quarterly Ofgem series exists Q3 2023 on as CSV
  but has no denominator); Mansilla et al.'s rationing thresholds (abstract only); any link from
  disconnection hours to indoor temperature or health outcome.

**7.4 What the company sees (the epistemic wall).**
- E: on a smart PPM, a supplier sees each credit-exhausted interruption, top-ups, low-credit and
  emergency-credit alerts (DCC codes 810D, 8119, 81AA), credit moved between fuels, and mode switches.
  These are its own meters' events, so they are legitimate observables.
- E: on a traditional PPM it sees only gaps between vends ("non-vending as a proxy", Ofgem 2020).
- Never crosses: the household's reason (affordability or forgetting), its indoor temperature, its
  health, its rationing as a state. A drop in consumption crosses; the cause does not.

**7.5 What this means for the floor test.** The world currently asserts zero prepayment harm (§0).
The smallest change that lets the floor fail is not a full meter: it is (1) stock prepayment
households receiving the W2_43 supply-event feed that only debt-fitted meters now have, at a rate
inside the Ofgem/Fawcett band, with a duration drawn so that "over 3 hours" and "over 240 hours"
both exist; (2) gas interruptions coupled to cold, since that is where a breach of the comfort and
health floor is physical; (3) prepayment coupled to tenure, so the breaches land on the households
they land on in life. Each of those has a source above. Top-ups, emergency-credit amounts and
rationing thresholds stay GAP and are carried as named ranges, never filled. Proposal only: the
first build is a world change (fidelity, R13) and gets its own K8 amendment.

## 8. Reading log entries (appended to the site reading log, 19 Nov 2026)

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-19 | SENSE catalogue, "Spatially and temporally granular dynamic energy vulnerability indices" (DCC smart-meter event data; gated) | Director | Points at our largest floor gap: prepayment and self-disconnection are not modelled. Open sources first; gated access is a G5 decision. | KNOWLEDGE FIRST |
| 2026-11-19 | DCC, "Tackling Fuel Poverty through Smart Metering" (v1.0, June 2023) | Advisor, from the above | The list of smart-meter vulnerability events a supplier observes. | SOURCE |
| 2026-11-19 | Another assistant's general answer on dynamic energy-vulnerability indices | Director | Confirms SENSE access is gated. Points to the open 2025 LSOA study (*Regional Studies, Regional Science*) and the JRC work. | POINTER ONLY |
