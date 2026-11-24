# The forward CfD fleet, read from LCCC's contract portfolio

**Knowledge:** electricity-wholesale

This page covers what remains of item 5 in the weather-to-price chain finding
(`docs/staging/WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`):
"the forward CfD fleet and volumes (LCCC publishes them; not yet read, so it is a GAP)". The on-the-record
levy check (`docs/staging/records/WORKER_RESULT_THE_CFD_LEVY_BUILT_FROM_THE_WORLDS_PRICE_MATCHES_THE_RECORD_TO_A_FEW_PERCENT_2026-11-24.md`)
used real generation. A forward levy needs each year's CfD-paying capacity. This page reads it. It
extends §3 of `how_the_gb_electricity_price_forms_2026-11-24.md` and does not repeat it.

Written by the worker, 2026-11-24. **Source:** LCCC Data Portal, dataset `cfd-contract-portfolio-status`,
datastore resource `fdaf09d2-8cff-4799-a5b0-1c59444e492b` (the CSV twin was last modified 2026-11-01),
fetched 2026-11-24. It has 612 contract units, and its fields are: CFD_ID, unit name, allocation round,
technology, T/D connection, Status, Expected_Start_Date and Maximum_Contract_Capacity_MW. It is open
data, and only aggregates are reproduced here. "[calc]" marks arithmetic on that table. "[not re-read]"
marks practitioner or press knowledge that was not checked in this session; each one is a GAP to check,
not a citation.

## 0. What is being counted

- **A CfD unit is a contract, not a plant.** Large projects are split into phases, each with its own
  contract and start date (Dogger Bank A has P1-P3). Capacity is the **Maximum Contract Capacity**:
  the most the contract will pay on. It is not nameplate capacity, and it is not physical first power.
- **The levy pays from the contract's Start Date, not from first power.** A unit can export
  merchant before its CfD starts. Several AR3-AR4 offshore phases carry 2027-29 expected start dates,
  and some of them are believed to be generating already. Under the AR4 terms, a generator may
  defer the CfD start within its target commissioning window, and in 2022-24 that let it sell at
  crisis prices [not re-read: the AR4 terms and each farm's first-power date]. **So the world's
  physical wind fleet and the CfD-paying fleet are two sets.** A forward levy computed as "a share
  of the world's fleet" is wrong while they differ.
- **Status values in the table:** Live (Post-FIC), Live (Pre-FIC), Pre-Start Date, Pre-MDD and
  Terminated. "Pre-MDD" means the unit has not yet passed its Milestone Delivery Date (the early proof
  of commitment). "Pre-Start Date" means it has passed that milestone, but its contract has not
  started.

## 1. The portfolio today

| Status | Units | Max contract MW |
|---|---:|---:|
| Live (Post-FIC) | 92 | 10,898 |
| Live (Pre-FIC) | 7 | 215 |
| Pre-Start Date | 67 | 11,639 |
| Pre-MDD | 393 | 27,051 |
| Terminated | 53 | 5,733 |

The live fleet is 11.1 GW: offshore wind 7.4, solar 1.3, biomass conversion 1.05 (Investment
Contract), onshore 1.0 and dedicated biomass 0.3 [calc]. **The forward pipeline (Pre-MDD plus
Pre-Start Date) is 38.7 GW**, more than three times the live fleet. It includes Hinkley Point C's
3,287 MW Bespoke nuclear contract, which has no expected start date in the table [calc].

## 2. The forward fleet by expected start year (not yet live, as LCCC holds it)

| Expected start | Offshore | Onshore + remote island | Solar | Other | Year MW | Cumulative MW |
|---|---:|---:|---:|---:|---:|---:|
| 2026 | 0 | 175 | 427 | 0 | 602 | 602 |
| 2027 | 7,310 | 1,180 | 2,710 | 24 | 11,223 | 11,825 |
| 2028 | 4,721 | 1,931 | 5,011 | 38 | 11,700 | 23,526 |
| 2029 | 2,756 | 771 | 1,827 | 18 | 5,372 | 28,897 |
| 2030 | 503 | 260 | 165 | 10 | 938 | 29,835 |
| 2031 | 4,348 | 0 | 0 | 59 | 4,406 | 34,241 |
| 2032 | 1,097 | 0 | 0 | 0 | 1,097 | 35,338 |
| none given | 0 | 34 | 30 | 3,287 (nuclear) | 3,351 | 38,689 |

"Other" is tidal stream and geothermal [calc]. Taken at face value, the CfD-paying fleet roughly
triples between end-2026 and end-2028. This is a schedule as currently expected. It is not a
forecast that it will happen (§3).

## 3. Attrition and slippage: what the table can and cannot say

**Terminated share of capacity awarded, by round [calc]:**

| Round | Awarded MW | Terminated MW | Share |
|---|---:|---:|---:|
| AR1 | 2,021 | 96 | 4.8% |
| AR2 | 3,285 | 142 | 4.3% |
| AR3 | 5,775 | 284 | 4.9% |
| AR4 | 9,328 | 2,465 | 26.4% |
| AR5 | 3,540 | 242 | 6.8% |
| AR6 | 9,522 | 2,504 | 26.3% |
| AR7 | 14,336 | 0 | 0.0% |

Most of AR4's terminations are Norfolk Boreas (1,396 MW over three phases). AR6's are Hornsea Project
Four (2,400 MW). So the attrition comes in single-project lumps, not as a steady rate. **A forward
fleet that applies a flat percentage would be the wrong shape.** The honest form is a band: the
schedule at face value, and the schedule less the largest one or two offshore projects of each
round. AR7 shows 0% only because it is new. It is not evidence that the round will deliver.

**Slippage is not measurable from this table.** Expected_Start_Date holds the *current* expectation,
which developers revise. Only 8 units (245 MW) are past their stated date and still not live [calc].
That is a lower bound on slippage, not an estimate of it. Measuring slippage needs earlier snapshots
of the same table (GAP 1).

## 4. What a forward CfD levy needs, and where each input comes from

The on-the-record check computed (strike − world's daily price) × real generation. Going forward,
each factor needs a source:

1. **CfD-paying capacity by year and technology:** §2 above, with §3's band. This is sourced.
2. **Output per MW:** the world's own weather through the fleet-aggregate curve
   (`sim/weather_price_chain`). This has to be the same curve and the same weather as the world's
   price, or the levy and the price will disagree about the same windy day.
3. **Strike by unit:** not in the portfolio table. §4a reads it for every round, AR1-AR7, from
   DESNZ's allocation results. AR7 is in a different price base from the others in LCCC's table,
   and §4a says how to read it.
4. **The reference price:** the world's own forward price. That price must be graded before a levy is
   built on it (item 4's work, still open).
5. **The negative-hour rules by round:** read 24 Nov (electricity page §3). From AR4, no difference in
   any hour the day-ahead reference is below £0. Before AR4, none only from six consecutive negative
   hours. AR1 and the investment contracts are not read. The world has no hourly day-ahead price to
   test the rule on (GAP 3). Its nearest series, MID, goes negative in 1.6-2.3 times the auction's
   hours in 2022-24 (measured 24 Nov, electricity page §3), so it cannot stand in unadjusted.

**The interconnection that matters most.** `sim/renewable_capacity_trend` holds the world's fleet
flat after 2025 by design: "the forward window is CURRICULUM (a director-authored buildout scenario)".
A forward levy fed by §2 would therefore grow its CfD volumes on top of a physical fleet that does not
grow. The levy would assert ~24 GW of new wind and solar while the world's price behaves as if it
did not exist. The two must be drawn from **one** capacity path. §2-3 are the sourced evidence for
the CfD-contracted part of that path. Choosing the path stays the director's curriculum, as the steer
says for forward carbon and strikes. This page does not pick one.

## 4a. Strikes by round and technology (GAP 2, read)

Added by the worker, 2026-11-24. **Source:** LCCC Data Portal, dataset `auction-outcomes`, datastore
resource `55bd2d1e-d25d-4980-8569-ea27f6ec7217`. It has 569 rows, all `Version = Final`, and was
fetched 2026-11-24 (sha256 of the API response `b3641c4f…`). LCCC transcribes it from DESNZ's
allocation-round results. Its fields are Auction, Project_Name, Developer, Technology_Type,
Capacity_MW, Strike_Price_GBP_Per_MWh, Delivery_Year and Region. The rounds were checked against
the DESNZ results PDFs, each as published on GOV.UK: AR4 (clearing table §E), AR5 and AR6 (each
headed "strike prices are in 2012 prices"), and AR7 and AR7a (both price bases, row by row).

**Read this first: LCCC's strike column is not one price base.** AR1-AR6 are in 2012 prices, as
DESNZ publishes them. AR7 is the first round for which DESNZ printed two columns, 2012 prices and 2024
prices. LCCC carries the **2024** column. Awel y Môr is £65.45 in 2012 prices and £91.20 in 2024
prices. Bettyhill 2 is £51.85 and £72.24. Every AR7 row has the same ratio, 1.3932-1.3934 [calc], so
the factor is DESNZ's own, not a per-technology choice. **Taking the column as one series would
overstate AR7 by 39% against the other rounds.** The table below therefore gives AR7 in both bases,
and the 2012 figure is the one comparable with AR1-AR6.

| Round | Technology | Units | MW offered | Strike, 2012 prices (£/MWh) | Delivery years |
|---|---|---:|---:|---:|---|
| AR4 | Offshore wind | 5 | 6,994 | 37.35 | 2026/27 |
| AR4 | Floating offshore | 1 | 32 | 87.30 | 2026/27 |
| AR4 | Onshore wind | 9 | 838 | 42.47 | 2024/25 |
| AR4 | Remote island wind | 6 | 598 | 46.39 | 2026/27 |
| AR4 | Solar PV | 66 | 2,209 | 45.99 | 2023/24-2024/25 |
| AR4 | Energy from waste (CHP) | 1 | 30 | 45.99 | 2024/25 |
| AR4 | Tidal stream | 4 | 41 | 178.54 | 2025/26-2026/27 |
| AR5 | Onshore wind | 24 | 1,481 | 52.29 | 2025/26-2027/28 |
| AR5 | Remote island wind | 1 | 224 | 52.29 | 2027/28 |
| AR5 | Solar PV | 56 | 1,928 | 47.00 | 2025/26-2027/28 |
| AR5 | Tidal stream | 11 | 53 | 198.00 | 2026/27-2027/28 |
| AR5 | Geothermal | 3 | 12 | 119.00 | 2026/27-2027/28 |
| AR6 | Offshore wind | 9 | 4,942 | 54.23-58.87 (MW-weighted 57.39) | 2027/28-2028/29 |
| AR6 | Floating offshore | 1 | 400 | 139.93 | 2028/29 |
| AR6 | Onshore wind | 22 | 990 | 50.90 | 2026/27-2027/28 |
| AR6 | Solar PV | 93 | 3,288 | 50.07 | 2026/27-2027/28 |
| AR6 | Tidal stream | 6 | 28 | 172.00 | 2027/28-2028/29 |
| AR7 | Offshore wind | 10 | 8,245 | 64.23-65.45 (MW-weighted 65.25; 2024 prices 90.91) | 2028/29-2030/31 |
| AR7 | Floating offshore | 2 | 193 | 155.37 (2024 prices 216.49) | 2029/30 |
| AR7a | Onshore wind | 28 | 1,306 | 51.85 (2024 prices 72.24) | 2027/28-2028/29 |
| AR7a | Solar PV | 157 | 4,905 | 46.82 (2024 prices 65.23) | 2027/28-2028/29 |
| AR7a | Tidal stream | 4 | 21 | 190.19 (2024 prices 265.00) | 2028/29-2029/30 |

LCCC's table labels both AR7 publications "AR7". Pots 3 and 4 (offshore) were published on 14 Jan 2026,
and pots 1 and 2 (AR7a on GOV.UK) on 10 Feb 2026. A delivery year is DESNZ's April-March year, and
LCCC records it as its first calendar year.

**Capacity-weighted strike by round, in 2012 prices [calc]:** AR1 101.85, AR2 62.62, AR3 40.64,
AR4 40.74, AR5 51.84, AR6 57.98 and AR7 59.25 (82.56 in 2024 prices). AR5 has no offshore wind
row: none cleared. In 2012 prices, AR7's offshore wind is 75% above AR4's (65.25 against 37.35)
[calc]. Why offshore strikes rose from AR4 to AR7 is not read here.

**What this does to a forward levy, as a mechanism, not a number.** The levy on a unit is (strike
− reference) × output, with the strike CPI-indexed from its 2012 base. The 2027-29 tranche of §2 is
mostly offshore from rounds whose strikes run 37-59 in 2012 prices (AR3 40.67, AR4 37.35, AR6
54.23-58.87). Which round each unit is waits on GAP 2's join. In 2024 money that is about £52-82
(37.35 and 58.87 × 1.3933) [calc]. Above that, the levy on those units goes negative and generators
pay back. As CPI rises, the band in nominal terms rises with it. AR7's offshore wind, from 2028/29,
strikes at about £91 in 2024 money. At a world price between the two bands, the older units pay
back while AR7's are paid. **So a forward levy is not one strike times one volume.** It
is a sum over vintages, and the vintage mix of §2 decides its sign as much as the world's price
does. This cannot be computed until item 4 grades the forward price. It is stated here so that the
build does not average the strikes first.

**Two counts that differ, stated and not attributed.** Offered MW here (AR4 10,742, AR7 14,670)
is not the portfolio's Maximum Contract Capacity in §3 (AR4 9,328, AR7 14,336). The outcome table
counts contracts *offered*, and the portfolio counts contracts *held*, with capacity revised since
signature. How much of the gap each of those explains is GAP 2's remainder.

**The 2012→nominal factor for other years is not read here.** DESNZ's AR7 columns give one point,
1.3933 for 2012→2024. Each contract indexes by CPI under its own terms. The index series for
forward years is a curriculum input, the same as forward carbon. This page does not pick one.

## 4b. The join from an outcome row to a CFD_ID (GAP 2's remainder, read)

Added by the worker, 2026-11-24. **Sources:** the two LCCC tables above. The portfolio was re-fetched the
same evening (612 rows, sha256 of the saved response `439805f5…`). The join was predicted before it ran:
at least 85% of AR4-AR7 portfolio MW would match an outcome row on round, technology and normalised
name, with most misses being phased offshore units listed as one project. **That held.** AR4 matched
90.0% of MW, and AR5, AR6 and AR7 matched 99.9-100%.

**How the join is made.** Match on the same round and the same technology, and normalise the name: drop
"wind farm", "solar", "phase", "limited" and punctuation. Then take an exact match. Failing that, take the
best SequenceMatcher score of 0.85 or more, and failing that, containment. Taking the *first* candidate
over 0.85, rather than the best, pairs "Unit A Phase 1" with a sibling "Unit B" (score 0.97) and leaves
whole outcome rows unclaimed. That mistake was made in the first pass of this probe and caught by the
capacity split below. Six AR4 units need a hand alias. EA3 Phases 2 and 3 are phases of the outcome row
"EA3 Phase 1" (1,372.34 MW offered, 1,054.53 held across three phases). Four solar units are listed under
their SPV names, matched on capacity: NEXTPOWER CRIFTON ↔ SPV 5, Hatherden ↔ SPV 10, Whitecross ↔ SPV 6,
and Bicker Fen (18.16 MW held) ↔ SPV 11 (15 MW offered). SPV 5 and SPV 10 are both 40 MW, so that pair
cannot be told apart. Both clear at 45.99, so the strike does not depend on it.

**Two portfolio units have no outcome row.** The first is AR4's High Constellation Wind Farm (50 MW,
Terminated). LCCC's AR4 outcome rows hold 9 onshore units and the portfolio holds 10. The same project
won again in AR7 at 72.24 (2024 prices). The second is AR6's Locks Farm Solar (13.1 MW, Pre-MDD). AR6
solar clears at one price, 50.07, so its strike is known without the row.

**What the join settles for the levy: every AR4-AR7 portfolio unit has one strike.** In the outcome
table, a round and technology clear at a single strike, with two exceptions. AR6 offshore is 54.23 for
2027 delivery and 58.87 for 2028. AR7 offshore is 91.20, apart from Berwick Bank Phase B at 89.49
(2024 prices). Every portfolio unit in those two pots matched its own project by name, with a score of
0.92 or more. The 58.87 tranche is Hornsea Four and East Anglia Two. The 54.23 tranche is EA3B,
Hornsea Three AR6 A-C, Inch Cape A-B and Moray West String 9. So a vintage-summed levy can now be
built unit by unit, with no averaged strike.

**Offered MW against held MW, split [calc]:**

| Round | Offered | Offered, no contract in the portfolio | Capacity revised on held units | Held, no outcome row | Portfolio |
|---|---:|---:|---:|---:|---:|
| AR4 | 10,742.1 | −18.5 | −1,445.7 | +50.0 | 9,327.9 |
| AR5 | 3,697.1 | −84.8 | −72.3 | 0 | 3,540.0 |
| AR6 | 9,648.3 | −79.7 | −59.6 | +13.1 | 9,522.0 |
| AR7 | 14,669.6 | −47.5 | −285.7 | 0 | 14,336.4 |

The gap is mostly capacity revised on contracts that were signed. Offers that were never signed in the
portfolio are a small part of it. AR4's −1,446 MW is three offshore projects *(corrected in §4c: four, and they add up to 1,367.2 MW)*: Hornsea Three −705.9, EA3
−317.8 and Inch Cape −270.0. The same three appear in AR6 as new units at 54.23: Hornsea Three AR6 A-C
(1,080 MW), EA3B (158.9) and Inch Cape A-B (266.1). **This is observed, not attributed.** Whether these are
the same turbines re-contracted at a higher strike, extensions, or both is not read here. It is a GAP
(below, 2a). For a forward levy, it means some AR4 offshore capacity is paid at 54.23, not 37.35. AR7's
−285.7 is Norfolk Vanguard East and West Unit A, −165 MW each. The offered-but-unsigned rows (AR5
Bockingfold, Eastgate and Rainsbrook; AR6 Maisemore, Great House and Trinity) are solar only.

The probe is `join.py` and `split.py` (sha256 `b7ad0568…`, `55038c7f…`), run with `python3 -I` against the
saved responses outside the repository. Nothing in `sim/` or `company/` reads any of this.

## 4c. The AR4 capacity in AR6 is the Permitted Reduction route (GAP 2a, read)

Added by the worker, 2026-11-24.

**Rule (primary text).** DESNZ, *Accompanying Note to the Budget Notice for the Sixth Contracts for
Difference Allocation Round, 2024* (6 March 2024, OGL), ¶13: "Permitted Reduction projects are defined
as those that formed part of projects awarded a CfD in a previous Allocation Round and where these
projects have since gone through the Permitted Reduction process in the contract terms. This process
has allowed projects to withdraw a maximum of 25% of their original total project capacity from their
CfD contract and now use that reduced capacity to bid into AR6 as a standalone project." The Budget
Notice of the same date sets a separate Pot 3 Maximum of £800 million for "Offshore Wind Permitted
Reduction" projects. DESNZ's *AR6 results* (3 September 2024) list the category at 1,578.51 MW, £54.23
(2012 prices), delivery year 2027/28. New offshore wind cleared at £58.87 for 2028/29.

**Neither text says where the Permitted Reduction clause sits in the contract terms.** The AR6
Allocation Framework (March 2024), the July 2023 future-rounds response and the March 2024 AR6
contract-changes response were all searched as text, and none contains the phrase.

**The four projects, LCCC offered MW against held MW [calc]:**

| Project | AR4 offered | AR4 held | Withdrawn | % of offered | AR6 won at 54.23 | AR6 − withdrawn |
|---|---:|---:|---:|---:|---:|---:|
| Hornsea Three | 2,852.00 | 2,146.10 | 705.90 | 24.75% | 1,080.00 | +374.10 |
| EA3 | 1,372.34 | 1,054.53 | 317.81 | 23.16% | 158.90 | −158.91 |
| Inch Cape | 1,080.00 | 810.00 | 270.00 | 25.00% | 266.11 | −3.89 |
| Moray West | 294.00 | 220.50 | 73.50 | 25.00% | 73.50 | 0 |

Every withdrawal is within the 25% cap. Two of them sit exactly on it.

**Correction to §4b, beside the claim.** §4b says AR4's −1,445.7 MW of capacity revised "is three
offshore projects". The three it names add up to 1,293.7 MW. Moray West's −73.5 MW is a fourth
Permitted Reduction, and it took the same route into AR6 (String 9). That leaves 78.5 MW of AR4
revisions not attributed here.

**What it settles for a forward levy.** A unit's MW is paid at its own round's strike. The AR4
contracts are paid on what they now hold. Capacity re-won in AR6 is paid at 54.23 from 2027/28. It
counts once, because it left the AR4 contract. Some withdrawn capacity won nothing in AR6: EA3's
158.9 MW is exactly half of its withdrawal, and Inch Cape is 3.9 MW short. That capacity is not
under any CfD on this record (GAP 4).

**Still open (2a-ii).** Hornsea Three's AR6 units are 374.1 MW more than it withdrew. The note's text
("that reduced capacity") does not allow for that. Two readings fit: the project grew after AR4, or
the AR6 bid included capacity that was never under the AR4 contract. Neither is read. The candidate
source is the AR6 application rules on Permitted Reduction applicants: the 2024 Allocation
Regulations amendment, or the AR6 Round Notice. Until it is read, the forward levy carries the 374.1 MW
at 54.23, as LCCC holds it, and says so.

## 5. GAPs

1. **Slippage history.** Expected start dates as at each earlier date. Candidates are LCCC's own
   earlier publications and the Wayback Machine. Neither was read.
2. **Strikes for AR4-AR7 units.** Read in §4a, and the join is made in §4b (24 Nov, worker). Every
   AR4-AR7 portfolio unit has one strike. **Closed.**
   2a. **AR4 offshore capacity that reappears in AR6.** Read in §4c (24 Nov, worker). It is AR6's
   "Offshore Wind Permitted Reduction" category, and the rule is primary text. **Narrowed, not closed.**
   Hornsea Three's AR6 capacity is 374.1 MW more than it withdrew, and that is still unexplained (2a-ii).
3. **First power against CfD start for each phased offshore unit,** and the AR4 rule that allows
   deferral. This decides how far the two fleets of §0 differ in 2022-2026.
4. **Capacity not under any CfD** (RO, merchant, FiT). This is needed to split the curriculum's one
   capacity path into its CfD-paying and non-CfD parts. Not read here.

## Appendix: the probe

Fetch into an empty directory outside the repository, then aggregate. Both scripts are read-only.

```python
# python3 -I fetch.py fdaf09d2-8cff-4799-a5b0-1c59444e492b portfolio.json
import json, sys, urllib.request
rid, out = sys.argv[1], sys.argv[2]
rows, off = [], 0
while True:
    u = f"https://dp.lowcarboncontracts.uk/api/3/action/datastore_search?resource_id={rid}&limit=32000&offset={off}"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "research-client"}), timeout=180))["result"]
    rows += r["records"]; off += len(r["records"])
    if not r["records"] or off >= r["total"]: break
json.dump({"fields": r.get("fields"), "rows": rows}, open(out, "w"))
```

```python
import json
from collections import defaultdict
p = json.load(open("portfolio.json"))["rows"]
mw = lambda r: float(r["Maximum_Contract_Capacity_MW"] or 0)
fwd = [r for r in p if r["Status"] in ("Pre-MDD", "Pre-Start Date")]
by_year = defaultdict(float)
for r in fwd:
    by_year[r["Expected_Start_Date"][:4] or "none"] += mw(r)
terminated = defaultdict(lambda: [0.0, 0.0])
for r in p:
    terminated[r["Allocation_Round"]][0] += mw(r)
    if r["Status"] == "Terminated":
        terminated[r["Allocation_Round"]][1] += mw(r)
```

```python
# Strikes (§4a): fetch resource 55bd2d1e-d25d-4980-8569-ea27f6ec7217 with fetch.py above, then
import json
from collections import defaultdict
rows = json.load(open("outcomes.json"))["rows"]
# DESNZ's own 2012-price column for the AR7 rows, which LCCC carries in 2024 prices
P2012 = {91.20: 65.45, 89.49: 64.23, 216.49: 155.37, 72.24: 51.85, 65.23: 46.82, 265.00: 190.19}
g = defaultdict(lambda: [0, 0.0, 0.0])
for r in rows:
    mw, s = float(r["Capacity_MW"]), float(r["Strike_Price_GBP_Per_MWh"])
    s12 = P2012[s] if r["Auction"] == "AR7" else s
    x = g[(r["Auction"], r["Technology_Type"])]; x[0] += 1; x[1] += mw; x[2] += mw * s12
```
