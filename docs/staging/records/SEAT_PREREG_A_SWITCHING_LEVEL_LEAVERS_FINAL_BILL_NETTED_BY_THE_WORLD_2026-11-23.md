**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` s.8.8c (choice 14, GAP G8.15)

# Pre-registration: a switching level leaver's final bill netted by the world (2026-11-23)

Written before the build, for the world half handed on from
`SEAT_FINDING_A_SWITCHING_LEVEL_LEAVER_IS_REFUNDED_SHORT_BECAUSE_THE_WORLD_NETS_THE_FINAL_BILL_FOR_MOVERS_ONLY_2026-11-23.md`.
No code that changes the world exists yet. The baseline is measured on `run_output_6a588a832f_20261120T134224Z.json`.

**The change it grades.** `background/live_payment_triad.record_period`: an ever-level leg's final bill on any
closure, a switch-away included, takes the s.8.8c net (choice 25). Today the net is gated on `moved_out_on`.
The page and the company are unchanged.

## What each figure counts

- **A netted leg** is a leaver on the level schedule whose final bill the walk netted (`credits_applied` of kind
  "credit" under its last level collection). The replay below finds them on the book's own inputs. It must
  reproduce `closing_balances` with 0 mismatches, or the grade is refused.
- **Collected at face** means a netted leg with no `final_month_nets` row, or with a row whose `ask_gbp` exceeds
  face less the page's net by more than 0.01.
- **Money in** is the world's cash on the leg's final bill: `ask_gbp` where a row exists, and otherwise face less
  the credit-bill credit the walk netted earlier.
- **Refund** is `credit_amount_gbp + set_off_gbp` from `credit_refund_log`.

## Baseline (6a588a832f), and predictions on the first book carrying the change

| | Baseline | Prediction (band) |
|---|---|---|
| Netted legs collected at face | 149 legs, GBP 3,673.83 | **0 to 5 legs, GBP 0 to 100** |
| Money in on those legs' final bills | 5,077.71 face, less earlier credit-bill nets | falls by **GBP 3,100 to 4,250** (point 3,673.83) |
| Final DDs on those legs that present nothing (ask 0) | 0 | **70 to 100** (point 85) |
| Refunds on the 149 legs | the book's log, unchanged by the change | total moves by **less than GBP 50** (the page already nets) |
| `final_month_nets.netted_ledger_credit_legs` | 84, GBP 1,768.48 | **200 to 260 legs, GBP 4,700 to 6,200** |
| Reverse legs (world nets more than the page) | 8, GBP 201.03 | **6 to 12, under GBP 300**: not this change's subject |

Money in by year on the baseline, which is the same as the under-refund by year: 2016 85.13 · 2017 806.14 · 2018 231.81 ·
2019 507.43 · 2020 754.33 · 2021 397.08 · 2022 28.77 · 2023 309.02 · 2024 354.73 · 2025 199.39. The prediction
is that each year's under-refund goes to 0 to 25 GBP.

**Refuted** if more than 5 netted legs are still collected at face, or if refunds on the matched legs move by
GBP 50 or more. A move that large would mean the change reached the page or the company, which it must not.
If the leaver set differs from the baseline's 854 legs by more than 10%, the grade reports per-leg means
rather than totals, and says so.

## The method (fixed now)

`/var/tmp/ll-scripts/replay.py`, run from a worktree at the book's producing commit, followed by `table.py` against
the same book's `world_walk_truth_*.json`. Both scripts name the baseline book's two files. The grader swaps in
the new book's two paths and changes nothing else:

```python
"""Replay the close walk on the 6a588a832f book; list level leavers whose final bill was netted."""
import json, sys, datetime as dt
sys.path.insert(0, '.')
from simulation import arrears_engine as ae
from company.interfaces.bill_assembly import issued_bills
d = json.load(open('/home/rich/synthetic-enterprise/docs/reports/run_output_6a588a832f_20261120T134224Z.json'))
bills = d['bills']; beh = d['per_customer_behavioral']; book_close = d['closing_balances']
churned = set(book_close)
level = d['level_dd_collections']
resolved = ae._resolve_bills(issued_bills(bills), beh, 42)
closing, lastc, money_in, later = {}, {}, {}, {}
wo, credited = ae.balance_settlement_from_outcomes(resolved, churned, closing, level_dd_collections=level,
    last_collection_out=lastc, money_in_out=money_in, later_cash_out=later)
mism = [c for c in book_close if abs(book_close[c] - closing.get(c, 0.0)) > 0.005]
print('replay closing vs book: legs', len(book_close), 'mismatch', len(mism), mism[:10])
lvl = ae.level_collection_difference(resolved, level)
refunds = {e['customer_id']: e for e in d['credit_refund_log']}
by_cid = {}
for r in resolved: by_cid.setdefault(r['customer_id'], []).append(r)
out = []
for cid, rows in by_cid.items():
    if cid not in churned or cid not in level: continue
    lc = lvl.get(cid, (0.0, None))[1]
    if lc is None: continue
    for r in rows:
        for x in credited.get((cid, r['period_end'], r['commodity']), ()):
            if x['kind'] == 'credit' and x['credit_period_end'] == lc.isoformat():
                ev = refunds.get(cid)
                out.append(dict(cid=cid, period_end=r['period_end'], face=round(r['amount_gbp'], 2),
                    netted=x['amount_gbp'], paid_on=str(x['date']), method=r.get('method'),
                    days_late=r.get('days_late'),
                    closing=book_close[cid], held_before=round(book_close[cid] - x['amount_gbp'], 2),
                    refund=(ev or {}).get('credit_amount_gbp'), set_off=(ev or {}).get('set_off_gbp'),
                    refund_paid=(ev or {}).get('paid_date')))
json.dump(out, open('/var/tmp/ll-scripts/netted_legs.json', 'w'), indent=1, default=str)
print('netted legs', len(out), 'GBP', round(sum(o['netted'] for o in out), 2))
```

```python
import json
from collections import defaultdict
d=json.load(open('/home/rich/synthetic-enterprise/docs/reports/run_output_6a588a832f_20261120T134224Z.json'))
w=json.load(open('/home/rich/synthetic-enterprise/docs/reports/world_walk_truth_6a588a832f_20261120T134224Z.json'))
rows={r['leg']:r for r in w['final_month_nets']['rows']}
legs=json.load(open('/var/tmp/ll-scripts/netted_legs.json'))
movers={m['customer_id'] for m in d['home_move_outs']}
by=defaultdict(lambda:[0,0.0,0.0,0.0,0.0]); allu=[]
for L in legs:
    if L['cid'] in rows: continue
    y=L['period_end'][:4]; b=by[y]
    ref=(L['refund'] or 0)+(L['set_off'] or 0)
    b[0]+=1; b[1]+=L['netted']; b[2]+=L['face']; b[3]+=ref; b[4]+=-L['held_before'] if L['held_before']<0 else 0
    allu.append(L)
print('year legs under_refund_gbp final_face_gbp refunded_gbp held_before_net_gbp')
for y in sorted(by): print(y, by[y][0], *(round(x,2) for x in by[y][1:]))
print('TOTAL', len(allu), round(sum(l['netted'] for l in allu),2), round(sum(l['face'] for l in allu),2))
print('netted covers whole face:', sum(1 for l in allu if l['netted']>=l['face']-0.005))
print('no refund event (credit fully absorbed):', sum(1 for l in allu if l['refund'] is None))
print('home movers among them:', [l['cid'] for l in allu if l['cid'] in movers])
for L in legs:
    r=rows.get(L['cid'])
    if r and r['ask_gbp']<L['face']-L['netted']-0.01:
        print('LESS', L['cid'], L['period_end'], 'face',L['face'],'page_net',L['netted'],'world_taken',r['credit_taken_gbp'],'wait',r['waiting_credit_gbp'],'ledger',r['ledger_balance_gbp'],'closing',L['closing'],'refund',L['refund'])
json.dump(allu, open('/var/tmp/ll-scripts/under_refunded_legs.json','w'), indent=1)
```

**Reverse.** Delete this file. No code changed.
