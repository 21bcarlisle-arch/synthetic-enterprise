# Citizens Advice energy supplier star rating: seven Ofgem supplier groups, Q3 2023 to Q1 2026

Fetched 2026-11-02 22:08 UTC by the delivery seat from the page
https://www.citizensadvice.org.uk/policy/publications/historic-star-rating-data/ (dated 24 March 2026), whose
"download as a CSV file" links are published Google Sheets. Each was fetched as `pub?output=csv`. The full files are
NOT stored here; `seven_groups_by_quarter.csv` is the extract any page reads. Re-fetch to check:

| Chart | Measure | Sheet id (`https://docs.google.com/spreadsheets/d/e/<id>/pub?output=csv`) | SHA-256 as fetched |
|---|---|---|---|
| 2 | Overall star rating, per supplier, from Q4 2017 | `2PACX-1vTIe3NYT1164W3APEYvzbA5wCjWI_OoK941twTrMsEMqw_sOrHRhMQkJr_gYFS1XVtOocRWf3NjEEMn` | `fb823002189b5c86e80a9bd40ceb4530bb67d9d380b8171297331f7fda5ba16f` |
| 4 | Contact ease star rating (call wait, email response; from Q4 2025 other channels too), from Q3 2020 | `2PACX-1vQraN7m-zK5xTaLItANBGgRSq5VsCL7hnKHLo-UWyx6m5LIgAgT-zFDrXGVs5sO3XRG8zzty5P9PBze` | `f9879989189041eb8a0ce48c4334357fab4a57f532eae29e98c27281b0cc1de4` |
| 5 | Average call wait, seconds, from Q4 2017 | `2PACX-1vTmgaUkvHeN8ZU92hrnvr9FILte56_RU_z3v442AiY2Gaos52ZE-xmaWtpa9ahb0Lw9i8ZF-NWRcVIn` | `064c0b844aaeaeef670d5877101fe3a2d075c15fef9744f5147a3f3285ad6dbe` |
| 12 | Weighted complaints per 10,000 customers (Energy Ombudsman, Citizens Advice consumer service, Extra Help Unit), from Q4 2018 | `2PACX-1vR8Bt_FKLUQMBDcdTuiAxRucHrv6-jfJk8K6yBv3_Ao-XpwD4YsyB1rMRKCA11e-yZ3s-lboLH-JklN` | `986d4e16cef1cdfd694a8fdc0e7a0147f0ccfac9393582619939e2b5a67986b8` |

- The rating covers suppliers with over 25,000 customers and is built from what the supplier did (complaints,
  contact waiting time, customer commitments; from Q4 2025 also billing and metering). It contains no customer
  satisfaction survey.
- **The methodology changed from Q4 2025.** Citizens Advice cautions against comparing overall ratings across it;
  the complaints and call-wait logic did not change. Q4 2025 and Q1 2026 overall stars are on the new method.
- Columns kept: the brand that stands for each Ofgem group. E.ON Next for E.ON; Octopus Energy for Octopus (its
  complaints figure is printed identical to Co-op Energy's, so Citizens Advice reports them as one group); Ovo Energy
  for OVO (SSE's book had moved into it). Shell Energy has no column in these files.
- Read by: `docs/market_research/reputation_resentment_and_feedback_calibrated_against_the_gb_record_2026-11-02.md` §9.
  The derivation as run (stdlib) is below; its argument is a directory holding the four fetched files as
  `chart2.csv`, `chart4.csv`, `chart5.csv` and `chart12.csv`.

## The derivation, as run

```python
import csv, math, sys, itertools, random
d = sys.argv[1]
G = ["BG","EDF","EON","Octopus","OVO","SP","Utilita"]
COL = {"BG":["British Gas"],"EDF":["EDF Energy"],"EON":["E.ON Next"],"Octopus":["Octopus Energy"],
       "OVO":["Ovo Energy"],"SP":["ScottishPower","Scottish Power"],"Utilita":["Utilita"]}
Q = ["Q3 2023","Q1 2024","Q3 2024","Q1 2025","Q3 2025","Q1 2026"]   # quarter holding each Ofgem wave's fieldwork
GB=[69,73,78,81,82,81]
P={"BG":[67,71,76,80,81,80],"EDF":[61,67,70,74,79,75],"EON":[69,74,76,76,80,81],
   "Octopus":[84,87,87,89,90,90],"OVO":[61,63,72,75,73,70],"SP":[62,65,71,72,74,76],"Utilita":[75,68,85,84,76,77]}
gap={s:[P[s][t]-GB[t] for t in range(6)] for s in G}
def load(f):
    r=list(csv.reader(open(f"{d}/{f}.csv"))); h=r[0]; rows={x[0].strip():x for x in r[1:] if x}
    out={}
    for s in G:
        i=next(h.index(c) for c in COL[s] if c in h)
        out[s]=[float(rows[q][i]) for q in Q]
    return out
M={"overall stars":load("chart2"),"contact ease stars":load("chart4"),
   "call wait s":load("chart5"),"complaints /10k":load("chart12")}
def r(x,y):
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    sxy=sum((a-mx)*(b-my) for a,b in zip(x,y)); sxx=sum((a-mx)**2 for a in x); syy=sum((b-my)**2 for b in y)
    return sxy/math.sqrt(sxx*syy), sxy/sxx
def perm_p(x,y):  # exact one-sided-free two-sided permutation p over 7! orderings
    r0=abs(r(x,y)[0]); c=0; n=0
    for p in itertools.permutations(y):
        n+=1; c+= abs(r(x,list(p))[0])>=r0-1e-12
    return c/n
def rank(v): o=sorted(range(len(v)),key=lambda i:v[i]); rk=[0]*len(v); [rk.__setitem__(i,j) for j,i in enumerate(o)]; return rk
mg={s:sum(gap[s])/6 for s in G}
print("six-wave mean Ofgem gap:", {s:round(mg[s],1) for s in G})
for name,m in M.items():
  for label,ts in (("all six",range(6)),("old method only (first five)",range(5))):
    mm={s:sum(m[s][t] for t in ts)/len(ts) for s in G}
    x=[mm[s] for s in G]; y=[sum(gap[s][t] for t in ts)/len(ts) for s in G]
    rr,b=r(x,y); rs=r(rank(x),rank(y))[0]
    print(f"{name:20s} {label:28s} means {[round(v,2) for v in x]}  r={rr:+.2f} spearman={rs:+.2f} slope={b:+.2f} pts/unit perm-p={perm_p(x,y):.3f}")
  # within: wave-on-wave changes, demeaned within group
  dx=[];dy=[]
  for s in G:
    for t in range(5):
      dx.append(m[s][t+1]-m[s][t]); dy.append(gap[s][t+1]-gap[s][t])
  print(f"{'':20s} within-group change-on-change r={r(dx,dy)[0]:+.2f} (n={len(dx)})")
  # within, levels demeaned
  dx=[];dy=[]
  for s in G:
    a=sum(m[s])/6; c=mg[s]
    for t in range(6): dx.append(m[s][t]-a); dy.append(gap[s][t]-c)
  print(f"{'':20s} within-group demeaned levels r={r(dx,dy)[0]:+.2f} (n={len(dx)})")
# leave-one-group-out for complaints and overall
for name in ("overall stars","complaints /10k","contact ease stars"):
  m=M[name]
  print(name,"leave-one-out r:",{s:round(r([sum(m[g])/6 for g in G if g!=s],[mg[g] for g in G if g!=s])[0],2) for s in G})
print("post hoc, without Utilita:")
for name,m in M.items():
  gs=[g for g in G if g!="Utilita"]
  print(f"  {name:20s} r={r([sum(m[g])/6 for g in gs],[mg[g] for g in gs])[0]:+.2f}")
print("table (six-quarter means):")
for s in G: print(f"  {s:8s} gap {mg[s]:+5.1f} " + " ".join(f"{k}={sum(M[k][s])/6:.2f}" for k in M))
```
