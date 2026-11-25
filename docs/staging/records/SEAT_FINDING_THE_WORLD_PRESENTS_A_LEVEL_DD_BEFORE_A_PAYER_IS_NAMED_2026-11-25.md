**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` s.8.8g (choice 31, GAP G8.19)

# Finding and pre-registration: the world presented a level DD in months whose bill names no payer (2026-11-25)

This answers the "reverse legs" row of
`SEAT_RESULT_A_SWITCHING_LEVEL_LEAVERS_FINAL_BILL_NETTED_BY_THE_WORLD_GRADED_2026-11-25.md`.

## What each figure counts

- **The 30 legs, GBP 585.17 (the graded row).** The page's net on the final bill was taken as one row: the
  `credits_applied` entry dated at the last level collection. The world's take was `credit_taken_gbp`. *Correction:*
  the page also nets credit-bill credit on the same final bill. SYN-2016-107g's page nets 31.70 + 14.22 = 45.92,
  which is exactly the world's take. Counted against everything the page nets on a final bill, the row is
  **23 final bills, GBP 675.99**, on which the world takes more than the page. A further 9 go the other way.
  Of those 9, 7 are choice 26 debit-half bills, where the world folds the credit into its ledger debit. The
  other two are SYN-2016-083 and SYN-2016-542.
- **World credit** is `ledger_balance_gbp`: bills at face, less every level collection the world took, less
  credit notes.
- **Page credit** comes from `balance_settlement_from_outcomes`. It reconciles level cash only against bills some
  named payer is asked for.

## Why they disagree

19 of the 23 are `OCC-` legs. On each one, the world collected the level amount in months whose bill lies wholly
inside the unnamed-occupier or void window (`payer_ask_gbp` is None). Take OCC-3c914ee8cef5g: it paid 3 x 39.55 =
118.65 in January to March 2016, which is exactly world credit (162.66) less page credit (44.01). Book-wide,
**137 legs paid GBP 27,134.55** this way. No page balance and no refund ever counts that money.

## Which side is right

The page is right and the world is wrong. A DD is collected under the payer's Instruction. In the window, the
supplier does not know who the payer is (s.1 case B), so no Instruction exists. The world could not have taken
that cash. Fixed as a class at the one writer: `LivePaymentTriad.record_period(names_a_payer=...)`. The run
passes it from `arrears_engine.names_no_payer` over the board's pre-gate bill (`bill_for`), and the row is
withdrawn from the schedule as for a stopped mandate. `payer_ask_gbp` uses the same predicate.

Control: `tests/background/test_no_level_collection_is_presented_before_a_payer_is_named.py`. I deleted
`and names_a_payer` from the triad's `level` line and the control went red:
`presented == {"2016-01": True, ...}` against `False`.

**Not attributed:** SYN-2016-099, SYN-2016-144g, PROS-2017-0293g and PROS-2024-0270g (GBP 74.63 of the 23). They
are G8.19's third bullet.

## Pre-registration (written before any book on this commit exists)

On the first book whose producing commit descends from this landing, graded with `/var/tmp/rev30/allnet.py`
and `noask23.py`, both reproduced below and run from a worktree at the book's commit:

- **P1.** Level cash in no-payer months, book-wide: **0 legs, GBP 0** (from 137, GBP 27,134.55). Any non-zero
  value refutes the wiring.
- **P2.** `OCC-` final bills where the world takes more than the page nets: **0 to 2** (from 19).
- **P3.** Final bills where the world takes more, all legs: **2 to 8**, under GBP 150 (from 23, GBP 675.99). The
  floor is the 4 unattributed legs, less any the trunk has changed.
- **P4.** Closure refunds on `OCC-` legs: unchanged within GBP 50. The page never counted the cash, so its
  closings should not move. If the world's ledger credit was meeting later bills, page and desk may move there.
  A larger move means that cash reached the page somewhere this record did not find.

## The grading scripts (book paths are the f2c6979d01 baseline's; swap them)

```python
# allnet.py
import json, sys
sys.path.insert(0, '.')
from simulation import arrears_engine as ae
from company.interfaces.bill_assembly import issued_bills
R='/home/rich/synthetic-enterprise/docs/reports/'
d=json.load(open(R+'run_output_f2c6979d01_20261124T215935Z.json'))
nw=json.load(open(R+'world_walk_truth_f2c6979d01_20261124T215935Z.json'))
rows={r['leg']:r for r in nw['final_month_nets']['rows']}
res=ae._resolve_bills(issued_bills(d['bills']),d['per_customer_behavioral'],42)
closing={};lc={};mi={};lt={}
wo,cr=ae.balance_settlement_from_outcomes(res,set(d['closing_balances']),closing,level_dd_collections=d['level_dd_collections'],last_collection_out=lc,money_in_out=mi,later_cash_out=lt)
last={}
for r in res: last[r['customer_id']]=r
dis=[]
for c,w in rows.items():
    if not w['ever_level'] or c not in last: continue
    r=last[c]
    pn=round(sum(x['amount_gbp'] for x in cr.get((c,r['period_end'],r['commodity']),()) if x['kind']=='credit'),2)
    if abs(pn-w['credit_taken_gbp'])>0.01 and r['period_end'][:7]==w['bill_month']:
        dis.append((c,w['bill_month'],w['face_gbp'],pn,w['credit_taken_gbp'],w['ledger_balance_gbp'],w['ask_gbp'],w['debit_asked_gbp']))
for x in dis: print(x)
rev=[x for x in dis if x[4]>x[3]]
print('ever-level final rows',sum(1 for w in rows.values() if w['ever_level']),'disagree',len(dis),'world takes more',len(rev),round(sum(x[4]-x[3] for x in rev),2))
json.dump(dis,open('/var/tmp/rev30/dis.json','w'))
```

```python
# noask23.py
import json, sys
sys.path.insert(0, '.')
from simulation import arrears_engine as ae
R='/home/rich/synthetic-enterprise/docs/reports/'
d=json.load(open(R+'run_output_f2c6979d01_20261124T215935Z.json'))
dis=json.load(open('/var/tmp/rev30/dis.json'))
bills={}
for b in d['bills']: bills.setdefault(b['customer_id'],[]).append(b)
tot=0; n=0
for c,m,face,pn,wt,lb,ask,deb in dis:
    if wt<=pn: continue
    lv={x['month']:x['amount_gbp'] for x in d['level_dd_collections'].get(c,[])}
    oc=d['per_customer_behavioral'][c]['world_payment_truth']['outcomes']
    noask=sum(lv[b['period_start'][:7]] for b in bills[c] if ae.payer_ask_gbp(b) is None and b['period_start'][:7] in lv and (oc.get(b['period_start'][:7]) or {}).get('result')=='success')
    n+= noask>0; tot+=noask
    print(c,m,'world-page take',round(wt-pn,2),'no-ask level cash',round(noask,2))
print('legs with no-ask level cash',n,'GBP',round(tot,2))
# whole book: level cash presented in months nobody is asked for
T=0;L=set()
for c,rows in d['level_dd_collections'].items():
    oc=(d['per_customer_behavioral'].get(c) or {}).get('world_payment_truth',{}).get('outcomes',{})
    lv={x['month']:x['amount_gbp'] for x in rows}
    for b in bills.get(c,[]):
        mm=b['period_start'][:7]
        if mm in lv and ae.payer_ask_gbp(b) is None and (oc.get(mm) or {}).get('result')=='success':
            T+=lv[mm]; L.add(c)
print('book-wide: legs',len(L),'GBP',round(T,2))
```

**Reverse.** Revert the landing commit. The schedule then presents the window's level rows again.
