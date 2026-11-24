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
3. **Strike by unit:** not in this table. Live units' strikes are in
   `actual-cfd-generation-and-avoided-ghg-emissions`, and allocation results publish them in 2012
   prices, indexed to CPI (GAP 2: not read for AR4-AR7 here).
4. **The reference price:** the world's own forward price. That price must be graded before a levy is
   built on it (item 4's work, still open).
5. **The negative-hour rules by round:** GAP 3 on the electricity page, still open.

**The interconnection that matters most.** `sim/renewable_capacity_trend` holds the world's fleet
flat after 2025 by design: "the forward window is CURRICULUM (a director-authored buildout scenario)".
A forward levy fed by §2 would therefore grow its CfD volumes on top of a physical fleet that does not
grow. The levy would assert ~24 GW of new wind and solar while the world's price behaves as if it
did not exist. The two must be drawn from **one** capacity path. §2-3 are the sourced evidence for
the CfD-contracted part of that path. Choosing the path stays the director's curriculum, as the steer
says for forward carbon and strikes. This page does not pick one.

## 5. GAPs

1. **Slippage history.** Expected start dates as at each earlier date. Candidates are LCCC's own
   earlier publications and the Wayback Machine. Neither was read.
2. **Strikes for AR4-AR7 units.** Read from the DESNZ allocation-round results, in 2012 prices.
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
