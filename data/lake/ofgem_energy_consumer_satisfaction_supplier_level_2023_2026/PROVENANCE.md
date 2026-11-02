# Ofgem, Energy Consumer Satisfaction Survey: supplier-level findings, six waves (Aug-Sep 2023 to Jan 2026)

**The PDFs are NOT stored here.** The table below is what any page reads. Re-fetch to check: URLs and SHA-256 of the
files as retrieved on 2026-11-02 by the delivery seat. Licence: Open Government Licence v3.0 (each report says so).

| Wave | Fieldwork | Source | SHA-256 |
|---|---|---|---|
| — | 30 Aug-18 Sep 2023 | https://www.ofgem.gov.uk/sites/default/files/2024-03/Customers%27%20satisfaction%20with%20their%20supplier%20-%20supplier%20level%20findings.pdf | `f5d60a2c06e3a31dfc470ea691543d9544f42afbb4d2b316c7b773806131127c` |
| — | 18 Jan-10 Feb 2024 | https://ofgem.gov.uk/sites/default/files/2024-08/V2_Customers_satisfaction_with_their_supplier-supplier_level_findings_January_February_2024.pdf | `7e42954fe9e92235060ba47ae06665e980ef545adfcd97a0d8ec4ce41d1d5017` |
| — | 10 Jul-1 Aug 2024 | https://www.ofgem.gov.uk/sites/default/files/2024-11/Customers%27%20satisfaction%20with%20their%20supplier%20-%20supplier%20level%20findings%20-%20July%202024.pdf | `73146ad6c1d982886a83e6c5c9324c1ba2a406ddfe3c3dbfbb27fce820f57697` |
| — | 6-30 Jan 2025 | https://www.ofgem.gov.uk/sites/default/files/2025-05/Customers%27%20satisfaction%20with%20their%20supplier%20-%20supplier%20level%20findings%20-%20January%202025.pdf | `2f0e8d88717d507b86611b9382da575b8fff49d00cf540a6ec37d561d0cb9d25` |
| — | 16 Jul-13 Aug 2025 | https://www.ofgem.gov.uk/sites/default/files/2025-12/Customers%27-satisfaction-with-their-supplier-supplier-level-findings-July-to-August-2025.pdf | `b43032bac2aada555d56e4210b0348fe67f4594eaa6864d9a0691a37b992c01b` |
| — | 5 Jan-3 Feb 2026 | https://www.ofgem.gov.uk/sites/default/files/2026-05/Customers%27-satisfaction-with-their-supplier-supplier-level-findings-Jan-2026.pdf | `c9f1b7d3f3efbd2ec3e57e3177f71cc781c38d8cbb91233761f540da03fca4b3` |

- `overall_satisfaction_a5_by_supplier_group.csv`: question A5 ("Overall, how satisfied or dissatisfied are you with
  [supplier] as your supplier of <FUEL TYPE>?"), % satisfied or very satisfied, weighted, as printed in each report's
  Table 1, with the unweighted base each report prints. Only the seven groups present in all six waves are kept
  (Shell Energy Retail and Utility Warehouse appear in only one or two). The Jul 2024 report's base line says
  "January/February 2024 (3,750)"; the fieldwork paragraph of the same report gives 3,750 for July 2024, so the label
  is Ofgem's typo and the base is July's.
- **Supplier-level reporting starts with the Aug-Sep 2023 wave.** Earlier waves (2018-2023) were published for GB and
  by supplier size only. Ofgem's 2019 archive (https://www.ofgem.gov.uk/publications/customer-satisfaction-indicators-previous-updates)
  holds one per-supplier snapshot, GfK, "correct as of February 2018", and a GB quarterly series 2010-2017 on two
  methodologies. Neither is a per-supplier time series.
- Groups are as Ofgem defines them: OVO includes SSE; Octopus includes Co-op and London Power and, from the Jul 2024
  wave, the Shell Energy Retail book it took over on 1 Dec 2023 (the Feb 2024 report still shows Shell separately).
- Read by: `docs/market_research/reputation_resentment_and_feedback_calibrated_against_the_gb_record_2026-11-02.md` §8.

## The derivation, as run (stdlib, from this CSV's figures)

```python
import math, itertools, random
W=["2023-09","2024-02","2024-07","2025-01","2025-08","2026-01"]
S=["BG","EDF","EON","Octopus","OVO","SP","Utilita"]
GB=[69,73,78,81,82,81]
P={"BG":[67,71,76,80,81,80],"EDF":[61,67,70,74,79,75],"EON":[69,74,76,76,80,81],
   "Octopus":[84,87,87,89,90,90],"OVO":[61,63,72,75,73,70],"SP":[62,65,71,72,74,76],"Utilita":[75,68,85,84,76,77]}
N={"BG":[1063,1056,1015,1165,1168,1170],"EDF":[355,390,371,357,323,369],"EON":[543,518,556,477,481,485],
   "Octopus":[583,713,796,878,876,823],"OVO":[379,389,373,365,314,340],"SP":[267,281,257,254,243,266],"Utilita":[153,108,130,105,112,166]}
GN=[3742,3855,3750,3854,3790,3911]
DEFF=1.5  # assumed design effect for quota+weighting; varied below
def gap(s,t): return P[s][t]-GB[t]
def nv(s,t,deff):  # sampling variance of the gap, points^2 (supplier is part of GB: ignore covariance, conservative)
    p=P[s][t]/100; g=GB[t]/100
    return deff*1e4*(p*(1-p)/N[s][t]+g*(1-g)/GN[t])
print("gaps (pts):")
for s in S: print(f"  {s:8s}", [gap(s,t) for t in range(6)], " se~", [round(math.sqrt(nv(s,t,DEFF)),1) for t in range(6)])
def fit(subset, deff, lag=1):
    xs=[];ys=[];noise=[]
    for s in subset:
        for t in range(6-lag):
            xs.append(gap(s,t)); ys.append(gap(s,t+lag)); noise.append(nv(s,t,deff))
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs)/(n-1); sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/(n-1)
    b=sxy/sxx; lam=max(1e-9,(sxx-sum(noise)/n)/sxx)
    return b, b/lam, lam, n
def hl(rho, months):
    return float("inf") if rho>=1 else (months*math.log(0.5)/math.log(rho) if rho>0 else 0.0)
for deff in (1.0,1.5,2.0):
  for lag in (1,2,4):
    b,bc,lam,n=fit(S,deff,lag)
    print(f"deff {deff} lag {lag} ({6*lag}m) n={n}: raw b={b:.3f} reliability={lam:.2f} corrected rho={bc:.3f}  half-life raw {hl(b,6*lag):.0f}m corrected {hl(bc,6*lag):.0f}m")
# leave-one-supplier-out at deff 1.5 lag1
print("leave-one-out, lag 1, deff 1.5:")
for s in S:
    b,bc,lam,n=fit([x for x in S if x!=s],1.5,1); print(f"  without {s:8s} raw {b:.3f} corr {bc:.3f} hl {hl(bc,6):.0f}m")
# within-supplier (demeaned) persistence: deviations from a supplier's own mean -- the transient part
xs=[];ys=[]
for s in S:
    m=sum(gap(s,t) for t in range(6))/6
    for t in range(5): xs.append(gap(s,t)-m); ys.append(gap(s,t+1)-m)
b=sum(x*y for x,y in zip(xs,ys))/sum(x*x for x in xs)
print(f"within-supplier lag-1 coefficient on demeaned gaps: {b:.3f} (Nickell-biased down by ~-(1+rho)/(T-1) with T=6)")
# variance decomposition: share of gap variance that is a fixed supplier effect
allg=[gap(s,t) for s in S for t in range(6)]; mg=sum(allg)/len(allg)
tot=sum((g-mg)**2 for g in allg)/(len(allg)-1)
between=sum((sum(gap(s,t) for t in range(6))/6-mg)**2 for s in S)/(len(S)-1)
noisebar=sum(nv(s,t,1.5) for s in S for t in range(6))/42
print(f"total gap var {tot:.1f}, var of supplier means {between:.1f} (noise in a 6-wave mean ~{noisebar/6:.1f}), mean noise var per point {noisebar:.1f}")
```
