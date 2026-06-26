#!/usr/bin/env python3
"""Generate synthetic monthly invoice records for static customer portal."""
import json, sys
from datetime import date, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"

_ELEC_W = {1:1.15,2:1.10,3:1.00,4:0.90,5:0.85,6:0.82,7:0.82,8:0.83,9:0.88,10:0.98,11:1.08,12:1.18}
_GAS_W  = {1:1.45,2:1.35,3:1.15,4:0.75,5:0.60,6:0.50,7:0.48,8:0.48,9:0.55,10:0.80,11:1.15,12:1.35}
_SC = {"electricity":0.28,"gas":0.27,"ic_electricity":1.20}

def _month_end(yr, mo):
    if mo == 12:
        return date(yr+1,1,1) - timedelta(days=1)
    return date(yr,mo+1,1) - timedelta(days=1)

def _months_between(start_str, end_date):
    start = date.fromisoformat(start_str)
    months = []
    yr, mo = start.year, start.month
    while date(yr,mo,1) <= end_date:
        months.append((yr,mo))
        mo += 1
        if mo > 12:
            mo, yr = 1, yr+1
    return months

def _seasonal(total, months, commodity):
    ws = _GAS_W if commodity == "gas" else _ELEC_W
    raw = [ws.get(mo, 1.0) for _,mo in months]
    tw = sum(raw)
    return [total*w/tw for w in raw]

def generate_invoices(cid, cdata):
    segment = cdata.get("segment","resi")
    commodity = cdata.get("commodity","electricity")
    acq = cdata.get("acquisition_date","2016-01-01")
    revenue = cdata.get("revenue_gbp",0.0)
    months = _months_between(acq, min(date.today(), date(2025,12,31)))
    if not months:
        return []
    revs = _seasonal(revenue, months, commodity)
    invoices = []
    for i,(yr,mo) in enumerate(months):
        ps = date(yr,mo,1)
        pe = _month_end(yr,mo)
        days = (pe-ps).days+1
        sc_key = "ic_electricity" if segment == "I&C" else commodity
        sc = _SC.get(sc_key,0.28)*days
        amt = revs[i]+sc
        status = "UNPAID" if i == len(months)-1 else "PAID"
        invoices.append(dict(
            id=cid+"-"+str(yr)+"-"+format(mo,"02d"),
            date=pe.isoformat(),
            period_start=ps.isoformat(),
            period_end=pe.isoformat(),
            amount_gbp=round(amt,2),
            status=status,
            commodity=commodity,
        ))
    return invoices

def generate(run_json_path=None):
    path = Path(run_json_path) if run_json_path else RUN_OUTPUT
    run = json.loads(path.read_text())
    pcl = run.get("per_customer_lifetime",{})
    CUSTOMERS_DIR.mkdir(parents=True, exist_ok=True)
    count = total = 0
    for cid, cdata in pcl.items():
        cust_file = CUSTOMERS_DIR / (cid+".json")
        existing = json.loads(cust_file.read_text()) if cust_file.exists() else {"account_id":cid}
        invs = generate_invoices(cid, cdata)
        existing["invoices"] = invs
        cust_file.write_text(json.dumps(existing, indent=2))
        count += 1
        total += len(invs)
    print("Updated", count, "customers,", total, "invoices")
    return count

if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv)>1 else None)
