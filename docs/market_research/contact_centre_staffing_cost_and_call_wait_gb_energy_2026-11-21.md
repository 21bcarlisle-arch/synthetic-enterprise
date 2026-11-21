# What a GB energy supplier's phone queue costs, and what the wait it buys is

**Knowledge:** communications-sentiment-and-nps

**Written 2026-11-21** by the delivery seat, as the K8 knowledge-first step for the delivery item
`supplier-decides-contact-centre-staffing-against-the-worlds-queue`. That item comes from the
customer-voice theme map (`customer_voice_theme_map_gb_energy_2026-11-21.md` §3, row "Customer
service access"). The world draws queue waits (`simulation/contact_centre.py`), but no company module
decides how many agents answer them. This page covers what the rules require, what the published
record says, what is not published (GAP), and the design choices that follow.

> **In one paragraph.** The regulator prices the wait and not the staffing. Ofgem expects a supplier
> to justify a monthly median wait "significantly or consistently" over **5 minutes**. Citizens
> Advice scores the call wait as 60% of its 30% ease-of-contact weight, with full marks under **30 s**
> and the floor at **over 300 s**. The labour is priced by the market: ONS ASHE gives a median of
> **£8.72 an hour** for call and contact centre occupations in 2016, rising to **£14.26** in 2025. The
> relation between the two is queueing arithmetic (Erlang C), and the arithmetic says three things.
> The wait is close to a cliff, not a slope. Going from a 5-minute wait to 30 s costs **6% more
> agents at 600 calls an hour, about a fifth more at 120, and a third or more at 30**, not five
> times as many. A large book buys short waits proportionally cheaper than a small one. And the input that matters most, **average handle time, is
> not published for GB energy**. That is a GAP the design must carry, not fill.

---

## 1. What the rules require

| Rule | What it says | Source |
|---|---|---|
| SLC 0.3(c) (Standards of Conduct) | "make it easy for a Domestic Customer to contact the licensee"; arrangements "complete, thorough, fit for purpose and transparent" | Ofgem, *Guidance on expectations for consumers to be able to contact their supplier*, Apr 2025, ¶1.50 |
| Call wait | "we would expect a supplier to be able to justify and explain its level of performance if it took, significantly or consistently, longer than a monthly average of 5 minutes to answer phone calls". Footnote 5: the average "is calculated as a median value per calendar month", excluding IVR time "up until the point 'talking to an agent' is chosen" | same, ¶1.53 and fn 5 |
| Abandoned calls | "We want suppliers to minimise the number of abandoned calls". **No GB threshold** | same, ¶1.56 |
| Written channels | to justify falling below Citizens Advice's basic threshold, "eg responding to less than 40% of emails within 2 working days" | same, ¶1.57 |
| Vulnerable callers | SLC 31G.3B: "implement appropriate processes to prioritise enquiries from" customers in vulnerable situations | same, ¶1.59 |
| Northern Ireland, for comparison | average call wait "should not be over 5 minutes"; abandonment "not above 12.5%". Five KPIs were collected monthly from Nov 2021, including average call handling time and FTE agents | Utility Regulator, *Energy Supplier Customer Service Levels* guidance note, Sep 2023, §2.8 and expectations 5(a)-(b) |

**What the rules do not require.** There is no staffing ratio, no agent count and no GB abandonment
cap. The 5-minute line is an expectation to *explain*, not a breach. The Ofgem guidance is dated
April 2025, so for 2016 to early 2025 the only published yardstick is the Citizens Advice rating.

## 2. The published wait series (what the world must reproduce, not what the company may read)

- **Citizens Advice star rating**: average call wait in seconds per supplier per quarter, from Q4
  2017. The extract for seven groups, Q3 2023 to Q1 2026, is in
  `data/lake/citizens_advice_star_rating_2023_2026/` with its provenance and sheet ids. The wider
  series (Q4 2017 to Q2 2024) ran from a **median of supplier means of 82 s to 388 s**, peaking in Q1
  2022 (`docs/institutional/knowledge_map.md`, C31 row). The market averages were 224 s (Q1 2021),
  340 s (Q4 2021) and 391 s (Q1 2022), and one supplier was over 16 minutes.
- **Scoring**: call wait is 60% of the 30% ease-of-contact weight. 5★ is under 30 s and 1★ is over
  300 s (`communications_sentiment_and_nps.md` §5 table).
- **Spread between suppliers**: in Q3 2023, British Gas was at 329 s and EDF at 132 s (the extract
  above). The same quarter, the same price cap and the same wholesale market gave a 2.5× spread in
  waits. That spread is a staffing choice, which is why the decision belongs to the company.

## 3. What the labour costs

**Median gross hourly pay excluding overtime, UK, all employee jobs, "Call and contact centre
occupations" (SOC 7211).** Source: ONS ASHE Table 14.6a, fetched 2026-11-21.

| ASHE year | Median £/h | All-employee median £/h | SOC basis | Edition, SHA-256 of the zip as fetched |
|---|---|---|---|---|
| 2016 | 8.72 | 12.09 | SOC 2010 | 2016 revised, `5af3e966…a8b8a193` |
| 2019 | 9.38 | 13.22 | SOC 2010 | 2019 revised, `97724cd9…fb77d25b` |
| 2022 | 11.27 | 14.74 | SOC 2020 | 2022 revised, `5d300c5b…b2050c15` |
| 2024 | 13.11 | 17.04 | SOC 2020 | 2024 revised, `f071ed03…bcaf69da45` |
| 2025 | 14.26 | 17.90 | SOC 2020 | 2025 revised, `adc021c5…4afa4277ab6c` |

Zip paths are under
`https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/occupation4digitsoc2010ashetable14/`:
`2016revised/table142016revised.zip`, `2019revised/table142019revised.zip`,
`2022revised/ashetable142022revised.zip`, `2024revised/ashetable142024revised.zip` and
`2025revised/ashetable142025revised.zip`. Each was read from sheet `All`, row code `7211`. Sample:
42,000 to 50,000 jobs a year. 2017, 2018, 2020, 2021 and 2023 were not fetched. The 2024 edition's
own annual change (5.0%) puts 2023 near £12.49.

- **The SOC basis changes between 2019 and 2022.** The 2010 and 2020 codes for 7211 are not
  identical, so any year-on-year rate across that break is a reading across two definitions.
- **The occupation's pay sits close to the legal floor.** Its 10th percentile was £7.20 in 2016,
  near the £7.20 National Living Wage, and £12.28 in 2025, against a £12.21 floor. The minimum wage
  path therefore drives most of the series.
- **This is wage, not employer cost.** On top of it sit employer National Insurance and the
  auto-enrolment pension. Employer NI was 13.8% above the secondary threshold to 2024/25, and 15%
  above £5,000 a year from April 2025. The employer pension minimum was 1% of qualifying earnings to
  April 2018, 2% to April 2019 and 3% after. These are HMRC and Pensions Regulator statutory rates,
  restated from the published schedules but **not fetched for this page**. At a full-time (37.5 h)
  median wage they add about 8% in 2016 (NI £1,227 on £17,004, the pension still phasing in) and
  about 15% in 2025 (NI £3,421 and pension £647 on £27,807). Part-time agents pay less NI per hour,
  so the true figure is a range, not a point.
- **Paid hours are not answering hours.** Statutory leave alone (5.6 weeks) is 10.8% of paid time.
  The rest of "shrinkage" (training, coaching, sickness, breaks, after-call work) is **GAP**. It is
  practitioner knowledge, not a published GB energy figure.
- **Seat, telephony, IT and supervision cost per agent hour: GAP.** The cap's operating-cost
  allowance bundles all opex (`the_caps_operating_debt_and_industry_allowance_per_cap_period.md`),
  and the cost of contact handling cannot be separated out of it.

## 4. The relation between staffing and wait (stated belief: queueing arithmetic)

An inbound queue with calls arriving at rate λ an hour, a mean handle time *h* and *N* agents carries
an offered load A = λh in Erlangs. Under Erlang C (Poisson arrivals, nobody abandons), the mean wait
is C(A,N)·h/(N−A), and the wait is infinite when N ≤ A. This is standard telephony arithmetic, not
an energy-sector finding. Its assumptions are wrong in two known directions:

- **Real callers abandon**, which bounds the wait (Erlang A). The 12.5% NI line shows how large
  abandonment is.
- **Real arrivals surge**: Mondays, bill runs, price-cap announcements. A daily mean understates the
  peak-hour load, and the peak hour is what callers wait in.

**At real inputs.** 120 calls an hour, mean wait in seconds; ∞ means N ≤ A:

| AHT (min) | N=10 | N=12 | N=14 | N=16 | N=18 | N=20 | N=24 | agents for ≤300 s | agents for ≤30 s |
|---|---|---|---|---|---|---|---|---|---|
| 4 | 49 | 8 | 2 | 0 | 0 | 0 | 0 | 9 | 11 |
| 6 | ∞ | ∞ | 87 | 18 | 5 | 1 | 0 | 13 | 16 |
| 8 | ∞ | ∞ | ∞ | ∞ | 127 | 31 | 3 | 18 | 21 |
| 10 | ∞ | ∞ | ∞ | ∞ | ∞ | ∞ | 45 | 22 | 25 |
| 12 | ∞ | ∞ | ∞ | ∞ | ∞ | ∞ | ∞ | 26 | 30 |

What the table settles:

1. **The wait is a cliff.** One agent too few near A is the difference between seconds and the
   16-minute supplier. The 2021-22 peak in the CA series reads as demand crossing staffing (the
   crisis, SoLR intake and cap rises), not as staffing being cut.
2. **Five stars costs about a fifth more agents than the Ofgem line at 120 calls an hour**, at
   every AHT in the range: 11 vs 9, 16 vs 13, 21 vs 18, 25 vs 22, 30 vs 26. *Corrected 2026-11-21,
   same day:* this line first said "about a fifth" without the load, and the premium depends on
   scale. Printed through the desk (`company/crm/contact_centre_staffing.py`) at AHT 4 to 12 min,
   it is **+6 to 7% at 600 calls an hour, +14 to 23% at 120, and +25 to 50% at 30**. Queues pool,
   so a small supplier pays proportionally more for a short wait than a large one. The trade-off is
   narrow and steep, and the world must price both sides of it.
3. **Agents needed scale with AHT almost one for one.** AHT is unpublished (§5), so any absolute
   staffing figure carries that GAP inside it.

## 5. What is not published (GAP)

| GAP | Where looked | Why it matters |
|---|---|---|
| **Average handle time for GB energy calls** | Ofgem guidance (none); Ofgem customer-service data portal (complaints and ECSS only); NI Utility Regulator (collected monthly from Nov 2021, published only as charts, no values); supplier annual reports (search, none found) | Sets the agent count almost linearly (§4) |
| **Calls per customer per year** | Same sources; the NI KPI set has total calls and customers but publishes no values | Sets λ. The world draws contacts from its own propensity (`simulation/contact_propensity.py`), and phone is 55% of them, a share already marked provisional in `ASSUMPTIONS.md` |
| **Shrinkage beyond statutory leave** | None published for GB energy | Turns answering hours into paid hours |
| **Non-wage cost per agent hour** (seat, telephony, supervision) | Bundled inside the cap's opex allowance | Cost side of the decision |
| **Abandonment as a function of wait, for GB energy** | NI 12.5% line, Ofgem "minimise" only | The world's bound on the queue |
| **The dose from wait to complaint, rating or departure** | `communications_sentiment_and_nps.md` §7 gap 1 (no published per-unit dose) | What a long wait costs the company beyond the rating |

## 6. Design choices this page makes, and why

1. **The wait is the world's, the staffing is the company's.** The world gets the arrivals (its own
   contact propensity), the handle time and the queue arithmetic. The company chooses agent hours
   and sees only what a real supplier sees: its own answered-call log with waits and handle times.
   It does not see the world's AHT parameter or the propensity behind the arrivals. This puts the
   supplier on the same side of the wall as `simulation/contact_centre.py`, whose trigger was moved
   to the world's own propensity on 2026-08-13 for this reason.
2. **The cost is booked from the ASHE series** by year, as a wage. Employer on-costs and shrinkage
   are named GAPs with stated ranges, not folded into a single loading. The desk books the
   result as a **floor** (ONS median wage × paid hours, grossed up for statutory leave only) and
   names what it leaves out. *Corrected 2026-11-21, same day:* this line first said a wage-only
   cost "errs against the thesis that staffing is cheap". It errs the other way. A floor
   understates the cost of staffing up, so any gain the company finds from more agents is
   overstated on the cost side. That is why it is labelled a floor and not a cost.
3. **AHT is not invented.** Until a source is found, the world's queue takes AHT as a required
   argument with no default, and a run that has not set it refuses with this page's §5 as its reason.
   The theme map's call loops (O1, C3, C9) are repeat contacts, a separate mechanism from wait. They
   are not modelled by this item.
4. **The company's target is the regulator's line, not a star rating.** The decision is staffing to
   a stated wait (5 minutes is Ofgem's justification line, 30 s is CA's 5★), at the cost §3 prices.
   The wait it gets is the world's answer, so it is an outcome and a diagnostic, never a target the
   scorer rewards directly.

## 7. Sources

- Ofgem, *Guidance on expectations for consumers to be able to contact their supplier*, April 2025,
  https://www.ofgem.gov.uk/sites/default/files/2025-04/Guidance-on-Ofgem%E2%80%99s-expectations-for-consumers-to-be-able-to-contact-their-supplier.pdf,
  ¶1.50 to 1.59, read 2026-11-21.
- Utility Regulator (NI), *Guidance Note: Energy Supplier Customer Service Levels*, September 2023,
  https://www.uregni.gov.uk/files/uregni/documents/2023-09/Guidance%20Note%20-%20Energy%20Supplier%20Customer%20Service%20Levels_0.pdf,
  §2.7 to 2.9 and expectations 5, read 2026-11-21.
- ONS, *Annual Survey of Hours and Earnings*, Table 14.6a, 2016/2019/2022/2024/2025 revised
  editions, SOC 7211, as tabled in §3.
- Citizens Advice historic star rating data, via `data/lake/citizens_advice_star_rating_2023_2026/PROVENANCE.md`.
- Ofgem customer service data page (https://www.ofgem.gov.uk/customer-service-data): 67% found
  contact easy in Jul to Aug 2026, 8% difficult. No call-handling metrics are published there.
