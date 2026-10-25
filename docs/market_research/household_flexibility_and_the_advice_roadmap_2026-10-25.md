# Household flexibility in GB, and a scan of the advice topics a supplier could offer

**Knowledge:** household-flexibility-and-the-advice-roadmap

Written 2026-10-25 from the advisor's cited evidence pack
`docs/staging/advisor/done/DIRECTOR_EVIDENCE_HOUSEHOLD_FLEXIBILITY_AND_THE_ADVICE_ROADMAP_2026-10-25.md`,
one of six packs under the director's steer that the advice roadmap needs its knowledge first (25 Oct,
05:37). Part 1 (flexibility) was almost entirely sourced in the pack; Part 2 (the roadmap scan) was
mostly **[unverified]**, and section 7 records what was checked against primary sources while drafting.
**[derived]** is the pack author's arithmetic. The deeper treatment of aggregators, P415 and DNO
payments is on `vpps-and-local-flexibility`; the earlier DFS research note is
`neso_dfs_called_day_response_2026-09-07.md`.

## 0. What this project does today (read from code, not run)

- **Flexibility revenue is DFS only, from the published winter record.**
  `company/market/flexibility_revenue_book.py:97-111` books DFS revenue from 2022 per customer with an
  EV, heat pump or battery, anchored on what DFS paid per registered participant
  (`company/market/dfs_published_record.py`); every year before 2022 books zero, and the Capacity
  Market leg is refused with a reason (`company/market/flexibility_potential.py:147`).
- **The world's dispatch is the system-stress truth** (`sim/flex_dispatch.py:1-13`), seen by the company
  only as dispatch instructions and settlement lines (`company/interfaces/sim_interface.py:293`).
- **Wholesale shaping under half-hourly settlement is not booked as a flexibility value anywhere.**
  The time-of-use desk (`company/pricing/tou_desk.py`) decides who is offered a time-of-use pair; no
  module values a household's shifted kWh against the supplier's own half-hourly purchase cost.
- **No opt-in, notice, incentive response or fatigue is modelled for domestic events.**
- **No rival flexibility agent exists** (P415 VTPs), so no compensation flows.
- **Advice modules exist with no recipient**: EPC-band advice text (`company/billing/efficiency_advice.py`,
  read by the portal), an uncalled measure recommender (`company/crm/decarb_recommender.py`). The map
  holds this as `C30_advice_reaches_a_household` at level 0.

## 1. The Demand Flexibility Service over three winters

| Winter | Registered | Events | Delivered | Cost / price | Source |
|---|---|---|---|---|---|
| 2022/23 | 1.6m households and businesses; 31 providers | 22 (2 live) | >3,300 MWh | £3,000/MWh guaranteed for tests; live bids £3,300–6,500/MWh; "nearly £11m"; ~£3,330/MWh average (Carbon Brief) | NESO; Carbon Brief |
| 2023/24 | 2.6m meters (~99% domestic); 48 providers | 14 tests + 2 live | ~3,760 MWh | £11.9m (£7.1m tests, £4.8m live); average accepted competitive bid £1,110.9/MWh | ESO end-of-year report |
| 2024/25 | 1.98m MPANs; 28 providers | 44 events, 236 settlement periods | 3,917.7 MWh (5,449.6 accepted) | £943,983 paid; average accepted bid £210/MWh; highest £1,290/MWh | NESO winter review |

The 2024/25 row is confirmed in NESO's winter review PDF (https://www.neso.energy/document/363911/download,
fetched 2026-10-25): 28 providers, 1.98m, £943,983 paid, £210/MWh average, 236 settlement periods,
71.90% delivery against bids. The same document gives the accepted-tender total as £1,223,312.

Per unit: ~£3,165/MWh delivered in 2023/24 and ~£241/MWh in 2024/25, a ~13-fold fall **[derived]**;
~£4.58 per registered meter per winter in 2023/24 and ~£0.48 in 2024/25 **[derived]**. In 2024/25
domestic and I&C delivery split ~60/40, and over 99% of MPANs responded manually.

From 2024/25 DFS is an all-year "merit-based margin tool" under an Ofgem derogation to 31 Mar 2027;
the day-ahead product was removed; revenue can stack with DNO flexibility, the Capacity Market and the
Local Constraints Market; asset meters no longer need a half-hourly boundary meter (registrations
72 → 5,894). NESO's Dec 2025 routes-to-market review proposes demand turn-up, locational buying and a
0.1 MW minimum unit.

**Implication.** DFS moved from a scarcity price of ~£3/kWh to a merit price of ~£0.20/kWh. It is a
low-margin, occasional stream, not a core earner.

## 2. Octopus Saving Sessions

| | 2022/23 | 2023/24 (to 22 Jan 2024) |
|---|---|---|
| Signed up | >700,000 of 1.4m invited | >1.2m |
| Sessions / hours | 13 / 14.5 | 9 / 10 |
| Turned down | 1.86 GWh | 1.41 GWh |
| Paid out | £5.3m | £4m |
| Average opt-ins per session | 342,272 | 397,000 |

Source: https://octopus.energy/press/price-cap-protect-saving-sessions/. In 2022/23 the average
opted-in customer earned ~£8 (top 5% over £40); incentives £2.25/kWh tests, £3.69/kWh live; peak
reduction 188 MW. About £2.85 per kWh turned down reached customers **[derived]**. Opt-ins fell from
~49% to ~33% of sign-ups per session; turn-down per opt-in ~0.40 kWh per session in 2023/24 **[derived]**.

## 3. Value streams a supplier can capture

| Stream | Evidence | Band |
|---|---|---|
| Wholesale shaping under half-hourly settlement | Ofgem put MHHS benefits at £1.6–4.5bn by 2045; Q4 2025 off-peak shifting could save >£380/MWh for pass-through customers (Drax) | Largest stream; e.g. 1,000 kWh/yr shifted at £50–150/MWh spread = £50–150/household/yr **[derived; assumed spread]** |
| Imbalance avoidance | Balancing, constraint and reserve costs £2bn in 2021, £72 per household (CrowdFlex Discovery) | Not sized per household (gap) |
| DFS | Section 1 | £0.5–5 per meter per winter **[derived]** |
| Balancing Mechanism | Octopus EVs from Sep 2023 (3 MW); relaxed metering; standard domestic devices from Mar 2026 | No £ figure published (gap) |
| Capacity Market | T-4 2029/30 £27.10/kW/yr; T-1 2026/27 £5.00/kW/yr; DSR + storage 3.8 GW of the T-4 | £2.50–13.50/household/yr at an assumed 0.5 kW de-rated **[derived]** |
| DNO flexibility | ENA: 4.6 GW tendered, 1.9 GW contracted 2022/23; UKPN 2020: 123 MW for £14m | ~£23/kW/yr where a constraint exists **[derived]**; zero elsewhere |

Whole-household estimates: up to £137/yr (Element Energy, in CrowdFlex Discovery); ~£206/yr in a
2040 high-electrification scenario (OVO/Imperial 2018); Intelligent Octopus Go cut charging costs by
£343/yr (a tariff saving to the customer, not supplier revenue). National targets: 10–12 GW of
consumer-led flexibility by 2030 (DESNZ SSES response).

P415 (live 7 Nov 2024) lets an independent aggregator trade a household's flexibility in the wholesale
market, compensating the supplier with costs shared across suppliers; the world needs a rival
"flex captor" for this.

## 4. How much households actually shift

- Centre for Net Zero on 2022/23 Saving Sessions: signed-up customers cut 24–26% (0.09–0.10 kWh per
  half-hour); opted-in customers 38–40%; against a natural comparison group (Bulb), 9.4%; use either
  side fell 1–3% (https://www.biee.org/wp-content/uploads/2023/09/46-Saving-Sessions-for-BIEE.pdf).
- The ESO baseline overstated the domestic reduction by 13% (1,863 against 1,642 MWh).
- Opt-in: 91% opted in at least once, 55% six or more times, 7% to all 13; same-day notice 44% against
  63% day-ahead; an SMS plus £1.25 bonus raised opt-in ~23%. CrowdFlex: 36% opt-in with longer notice,
  25% with 2 hours; 80% shifted manually; 64% of EV drivers plugged in more often.
- Delivery against bids, DFS 2024/25: 71.9% overall, 64.8–66.7% Dec–Feb, 82.1% in March.
- Fatigue is measured only indirectly (falling opt-in; thinning participation; Fraser 2023 on
  re-enrolment depending on past success).
- Attitudes: SPEN — 86% would take part in principle, 33% do; average payment threshold £12.70/month.
  Ofgem's 2025 survey (n=4,385) — 16% on a time-of-use tariff they can name (53% of EV users); 26%
  comfortable with a company controlling EV charging (55% of EV users); 16% comfortable with heating
  control, 72% uncomfortable.

**Implication.** Households expect ~£150/yr; event payments are now under £5 per meter. Value has to
come from automated, tariff-embedded shifting, not manual events.

## 5. Control, consent and cybersecurity (SSES)

Two licence roles: Load Controller (creates or changes control signals) and Flexibility Service
Provider (contracts with the consumer). No capacity threshold; unlicensed activity becomes an offence
after transition; exemptions for control that benefits only the consumer and for incentive-only tariff
signals. Regulations laid autumn 2026; applications open March 2027; licence required from March 2028
(the later date replaces CMS's "end-2027"). In scope: EV smart charge points, smart electric heating up
to 45 kW thermal, domestic batteries. Cyber: below 300 MW a Tier 2 CAF check; at or above, NIS under a
Tier 1 CAF. Consumer terms: suitability, no pressure selling, exit fees capped at actual loss,
vulnerability safeguards, Energy Ombudsman.

**Existing EV charger rules**, confirmed against the Electric Vehicles (Smart Charge Points)
Regulations 2021 (SI 2021/1467, https://www.legislation.gov.uk/uksi/2021/1467/made, fetched
2026-10-25): a charge point must incorporate "pre-set default charging hours which are outside of peak
hours", which the owner may accept, remove or change on first use; and it must operate "with a delay
of up to 600 seconds, such delay to be of a random duration", which the owner can cancel.

## 6. How suppliers share the value

Per-kWh pass-through (Saving Sessions £2.25–3.69/kWh in 2022/23); a cheaper tariff for ceding control
(IOG); bill credits per action (Pod); asset-for-service (Octopus Power Pack, free charging for V2G);
pay only for opted-in delivery (CrowdFlex). Octopus paid ~86% of the average DFS cost per kWh in
2022/23 **[derived, indicative]**. SSES caps an FSP's exit fee at its economic loss.

## 7. The roadmap scan (Part 2) and its verification

Ranked by the pack (P1 first): tariff choice; data access and consent; electric storage heating and
Economy 7; prepayment and vulnerability; grants and schemes; then hot water and immersion; trust and
advice regulation; landlord/tenant and MEES; home moves; EPC reform; retrofit sequencing; cooling;
cooking and standby; heat networks.

| Item ([unverified] in the pack) | Outcome | Source, accessed 2026-10-25 |
|---|---|---|
| Smart Charge Points Regulations: off-peak defaults, random delay ≤600 s, security to ETSI EN 303 645 | **corrected** — defaults and 600 s confirmed; the SI does not cite ETSI EN 303 645, its Schedule 1 sets the security requirements itself | legislation.gov.uk SI 2021/1467 |
| ~4m+ homes on Economy 7-type meters | **confirmed** — "Around 4 million out of a total of 29 million domestic electricity customers" have restricted meters (2020) | Ofgem statutory consultation, 1 Sep 2020 |
| 1.5–2m homes rely mainly on electric heating | **still open** (a sibling pack cites EHS 2023-24: 2m households, 8%, in England use electric heating; not re-fetched here) | — |
| RTS switch-off began mid-2025, region by region | **confirmed** — began 30 June 2025; fewer than 154,000 left in Jan 2026; restarted 2 Mar 2026 in England and Wales | Ofgem RTS decision and update, Mar 2026 |
| "Quantum" storage heaters cut running costs | still open | — |
| Hot water ~15–20% of heating energy | still open | — |
| Cylinders removed in combi conversions | still open | — |
| Induction ~85–90% vs gas hob ~40% | still open | — |
| Standby ~£50/yr | still open | — |
| CMA 2016: ~£1.4bn/yr detriment | **confirmed, with its scope** — detriment from high prices to domestic customers of the Six Large Energy Firms, about £1.4bn a year on average 2012–2015, rising to almost £2bn in 2015 | CMA final report summary, 24 Jun 2016 |
| Data access: monthly by default, daily opt-out, half-hourly opt-in | still open (Ofgem page moved) | — |
| About two-thirds of meters smart or advanced | **corrected** — 72% of all meters in homes and small businesses (42m) at end June 2026; 92% of smart meters in smart mode | DESNZ smart meter statistics, June 2026 bulletin |
| 4m+ electricity prepayment meters | still open (vulnerability pack's subject) | — |
| Ofgem tightened involuntary PPM installs in 2023 | still open (Ofgem news page moved) | — |
| Warm Home Discount £150 | **confirmed** — "a one-off £150 discount off your electricity bill" | gov.uk/the-warm-home-discount-scheme |
| Warm Homes Plan ~£13.2bn | still open (plan published 21 Jan 2026 confirmed; figure not on the landing page) | gov.uk Warm Homes Plan |
| MEES: minimum EPC E, £3,500 cap | **confirmed** | gov.uk landlord guidance |
| EPC C by 2030 with a £10,000 cap | **corrected** — the guidance states an aim for "as many as possible" to reach EPC C or equivalent by 2030; no £10,000 cap is stated there | gov.uk landlord guidance |
| Private rented sector ~19% of English households | still open | — |
| ~1m+ housing transactions a year | still open | — |
| EPC required at sale and let | still open | — |
| Home Energy Model replaces SAP ~2026 | still open | — |
| ~14,000 heat networks, ~0.5m consumers; Ofgem regulation from Jan 2026 | still open — Ofgem confirms it regulates GB heat networks, introduced in phases; the counts and start date are not on its page | ofgem.gov.uk/heat-networks |
| AC in ~3–5% of homes | still open | — |
| PAS 2035 mandatory for ECO and GBIS | still open | — |
| Ofgem Standards of Conduct apply | still open here (sourced on the proving-savings page) | — |

Counts: confirmed 5, corrected 3, still open 18 (of 26 [unverified] items). Spot check of a sourced
figure: DFS 2024/25 row confirmed in NESO's PDF.

## 8. Headline bands (candidate world claims; calibration only, never per-home targets)

- DFS cost per MWh delivered: ~£3,330 → ~£3,165 → ~£241 across three winters.
- DFS revenue per registered meter per winter: £4.58 (2023/24) → £0.48 (2024/25) **[derived]**.
- Event response: 24–26% signed-up, 38–40% opted-in, 9.4% against a natural comparison.
- Delivery against bids: 71.9% (64.8–82.1% by month).
- Opt-in per session: ~49% → ~33% of sign-ups; same-day 44% vs day-ahead 63%.
- Comfort with third-party control: EV 26%, heating 16%.
- Whole-household flexibility value: £137–206/yr (modelled studies).

## 9. Named gaps

Imbalance-avoidance value per household; BM revenue for aggregated domestic assets; current DNO
domestic prices (now partly on the VPP page); domestic CM de-rating (0.5 kW is assumed); DFS
2025/26 outturn; Saving Sessions 2024/25 and 2025/26; Axle, OVO Charge Anytime, Piclo, ENA Open
Networks and FES 2025 flexibility GW not fetched; no direct fatigue measurement; Part 2's open items
above. Discrepancies: the SSES date (end-2027 vs March 2028; later used); NESO's 2024/25 accepted
tender total (£1,223,312 in the summary, confirmed here, against £1,233,312 elsewhere in the pack's
reading); CrowdFlex NPV and CO2 disagree between report sections.
