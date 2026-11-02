**Knowledge:** the-customer-needs-framework

# Why behind-on-bills households switched (CIM question C5, Waves 3-6), and what the debt-objection rule is known to say (2026-11-02)

Closes the two gaps left by `revealed_switching_by_age_and_arrears_and_the_needs_tables_in_cim_waves_4_6_2026-11-02.md`
(its sections 5.2, 5.3 and 6: "Reasons. Why a household switched (C5) was not read"; "the objection rule ... not checked").
**Grades:** D derived here from Ofgem's published tables; P reported by Ofgem; S secondary source only.

**No predictions were filed before reading.** The C5 tables were extracted and printed in one pass, so nothing below is a
pre-registered result; the previous page's four candidate causes (age, imposed moves, price search, poor service) were
the hypotheses, and this page reports which the tables touch.

## 1. What the tables are (D)

Workbooks re-fetched 2 Nov 2026; SHA-256 matched `data/lake/ofgem_cim_waves4_6_2023_2025/PROVENANCE.md`. Wave 3 from the
stored workbook. Intervals are 95% normal on the effective base; a contrast is starred only if larger than its interval.

| Wave | Table | Base | Behind on bills (eff.) | No difficulties (eff.) |
|---|---|---|---|---|
| 3 | 89 | switched tariff **or** supplier, past 12m (n=726) | 60 | 161 |
| 5 | 73 | switched, past 6m, C4=2-3 (n=575) | 41 | 172 |
| 6 | 65 (C5b) | switched, past 6m, C4=2-3 (n=754) | 55 | 250 |
| 4 | 95 | compared **or** switched (n=1,313); no switchers-only table | 138 | 316 |

**The base is not "switched to a new supplier".** It is anyone who switched tariff with their own supplier *or* changed
supplier. The previous page's arrears result was for new-supplier switching only; C5 cannot be restricted to that group
(no table crosses C5 with C4's supplier row). Switcher bases among the behind are 41-60: intervals are 10-17 points, so
most cells are "cannot tell". Wave 6 asked reasons in a new list (C5a compare / C5b switch / C5c did not switch), so
levels across Waves 3/5/6 do not compare; contrasts within a wave do. Wave 6's arrears column is *other household bills,
not energy*.

## 2. Behind minus no-difficulties, reasons for switching (D)

| Reason | W3 T89 | W5 T73 | W6 T65 |
|---|---|---|---|
| To get a cheaper tariff | -0.8 ± 13.2 | +5.9 ± 16.6 | -13.6 ± 14.4 |
| Net financial motivation | n/a | +6.2 ± 14.6 | +3.1 ± 12.1 |
| Offered an incentive / reward | +0.4 ± 7.1 | **+16.0 ± 12.0\*** | **+12.7 ± 11.4\*** |
| Worried previous supplier would fail | +4.3 ± 10.5 | **+14.5 ± 11.6\*** | n/a |
| Moved to a supplier I did not want | -1.5 ± 6.1 | +5.5 ± 8.3 | n/a |
| Issues with / poor service from supplier | n/a | +8.8 / +10.8 (neither starred) | **better-rated service +11.0 ± 9.6\*** |
| Net supplier motivation | n/a | **+22.9 ± 16.4\*** | **+12.8 ± 10.5\*** |

Where the whole compared-or-switched group is used (larger bases; W5 T72, W6 T64): issues with supplier **+13.0 ± 7.9\***,
poor customer service **+10.7 ± 7.7\***, dissatisfied **+10.7 ± 7.1\***, net supplier motivation **+14.5 ± 9.5\*** (W6),
"previous contract expired" **-8.1 ± 6.0\*** (W6). "Cheaper tariff" is flat (W5 T72 +8.4 ± 11.1; W6 T64 -0.6 ± 9.8).

Reading:

- **Price search does not distinguish them.** The cheaper-tariff and net-financial rows never separate behind from
  none in any wave: money is the reason for about three quarters of *both* groups (W5 77% vs 71%; W6 78% vs 75%).
- **The extra is the supplier, not the price.** Wave 5 and Wave 6 agree in sign and in being starred: behind-on-bills
  switchers over-report supplier-side reasons (dissatisfaction, service, incentives) by 11-23 points. Wave 3 shows
  nothing (all within wide intervals), so this is a 2024-2025 finding, not a constant.
- **Imposed moves are not supported.** "Moved to a supplier I did not want" is 4.1% vs 5.6% (W3), 7.4% vs 1.9% (W5) and
  not starred in either. Candidate (b) of the previous page is not ruled out (the Wave 3 Table 90 subset of households whose
  supplier entered administration has only 27 effective behind-on-bills respondents), but nothing here favours it.
- **Contracts ending run the other way.** Behind-on-bills households less often name an expired contract (8.8 vs 16.9, W6):
  they are less likely to be on fixed deals that roll off, consistent with their lower fixed-tariff share (W5 T73: 23.1 vs
  35.9, not starred).
- **Age is not separable.** The young report incentives (W6: 25.9% at 16-24 vs 1.6% at 65-74), green and EV tariffs;
  the same incentive row is what the behind group over-reports, and arrears is concentrated in the young. One-way tables
  and W11 forbid the cross. **Candidate (a), age, remains live for the incentive finding.** It is less plausible for the
  service finding, where the 16-24 gap is small (W5 T73 poor service 10.8 vs 5.4).

**What this does to the previous page.** Of its four candidates: price-driven search (c) has no support as the
difference; imposed moves (b) none; age (a) cannot be separated and fits the incentive row; poor service (d)
is the one that is starred in both of the later waves. Held loosely: the bases are small and the supplier-motivation
nets are constructed by Ofgem from differently-worded lists in W5 and W6.

## 3. The debt-objection rule: what is and is not established

**Established (P, read in this repo's earlier pages from the 2016 primary documents; S/P for continuity):**
- Standard Licence Condition 14 prohibits the losing supplier from blocking a domestic transfer except for debt, and only
  where the supplier has notified the customer in writing and the amount has been outstanding **28 days**
  (`domestic_debt_objection_rates_gb.md` row 17, from Ofgem's July 2016 decision on domestic objections). Ofgem's
  26 Oct 2020 closure of its compliance engagement with iSupply Energy restates the same 28-day test
  ([ofgem.gov.uk/decision/ofgem-closes-compliance-engagement-isupply-energy-relation-transfer-blocking](https://ofgem.gov.uk/decision/ofgem-closes-compliance-engagement-isupply-energy-relation-transfer-blocking)):
  the amount must have been billed at least 28 days before the switching request. That is a primary source dated four years
  after the decision and before CSS go-live.
- Objection is not total: Ofgem's own count was that ~70% of indebted customers who want to switch were allowed to (about
  430,000 allowed against 170,000 blocked a year, 2013-15), so ~28% blocked conditional on debt-and-attempt
  (`domestic_debt_objection_rates_gb.md`). That is why self-reported arrears switching is not a contradiction of the rule.
- Prepayment customers with debt under £500 per fuel can switch via the Debt Assignment Protocol if the new supplier
  agrees (2016 primary; £500 repeated by consumer-advice sources, S).

**Not established (GAP):** the current consolidated text of SLC 14 and the post-CSS (18 July 2022) wording or
thresholds. Searches this session returned secondary sources (comparison and debt-advice sites) that repeat 28 days
and £500, and no Ofgem document announcing a change; that is weak evidence of continuity, not a reading. Whether
a CSS-era objection rate exists was not found (consistent with the earlier page). Not read: the Debt Assignment
Protocol text; the REC schedule on objections.

## 4. For the world and the supplier

1. The world should not give arrears households a *lower* departure propensity because of the rule alone: the rule blocks
   roughly a quarter of attempts at debts above a de minimis, and the 2023-25 survey shows arrears households switching
   about twice as often. Nothing here changes a world value; that is not this page's call.
2. If the world adds a reason for leaving, "supplier dissatisfaction" is the one distinguishing arrears households in the
   two latest waves; price search is not.
3. A supplier sees who leaves and, in some systems, a stated reason. A leaver base over-weighted with arrears and
   service complaints is this table's signature; it does not show the arrears *caused* the departure.

## 5. What this page does not establish

- Cause; the one-way tables cannot separate age, arrears and service experience.
- Anything about new-supplier switchers specifically (C5's base mixes tariff and supplier switches).
- Wave 4 switchers' reasons (only compared-or-switched exists).
- The current licence text.

## Sources

- Ofgem, *Consumer Impacts of Market Conditions survey*, Waves 3-6 data tables, OGL v3.0: Wave 3 Tables 89-90; Wave 4 Table
  95; Wave 5 Tables 72-73; Wave 6 Tables 64-66. Hashes: `data/lake/ofgem_cim_waves4_6_2023_2025/PROVENANCE.md`.
- Ofgem, *Decision on review of domestic objections* (25 July 2016) via `domestic_debt_objection_rates_gb.md`.
- Ofgem, iSupply Energy compliance closure, 26 Oct 2020 (link above).
