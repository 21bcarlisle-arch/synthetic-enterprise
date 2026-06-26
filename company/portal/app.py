"""C2 -- Customer self-service portal.

FastAPI app. Customers log in with their account number and view:
  - Account profile (segment, contract, EAC)
  - Invoice list with payment status
  - Account financial summary (billed, paid, outstanding)

Data sources: saas/customers.py (profile), company/billing/invoice.py (invoices).
No simulation internals are read -- all data is company-layer.
"""

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import json

from company.billing.invoice import invoices_for_account, get_invoice
from company.billing.payments import reconcile_payment
from company.market.price_feed import PriceFeed
from company.billing.consumption import consumption_history, monthly_totals
from company.billing.hh_consumption import get_hh_consumption, recent_hh_periods, is_feed_available
from company.billing.eac_calibration import calibrate_eac, eac_drift
from company.billing.direct_debit import set_mandate, get_mandate, cancel_mandate, is_dd_customer
from company.billing.contract import renewal_summary, contract_end_date, days_until_renewal
from company.pricing.switching_recommendation import switching_recommendation
from company.billing.efficiency_advice import efficiency_summary
from company.billing.collections import get_collections_queue
from company.billing.consumption_forecast import forecast_annual_cost
from company.billing.usage_benchmark import usage_benchmark
from company.market.rate_comparison import market_rate_comparison
from company.crm.service_log import ServiceLog, ServiceEvent, DEFAULT_DB_PATH as _SL_DB_PATH
from company.pricing.tariff_comparison import compare_tariffs
from company.interfaces.sim_interface import LiveSimInterface
from company.regulatory.compliance import (
    smart_meter_target,
    smart_meter_compliance_status,
    annual_turnover_fee,
    generate_css_filing,
)
from company.regulatory.warm_home_discount import whd_summary
from saas.capital.solvency import compute_solvency_signal, MCR_FLOOR_GBP_PER_CUSTOMER

_SIM_INTERFACE = LiveSimInterface()
from saas.customers import CUSTOMERS

_TEMPLATE_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATE_DIR))

_DEFAULT_DB = Path("company/data/invoices.db")
_DD_DB = Path("company/data/direct_debit.db")
_SERVICE_LOG = ServiceLog(db_path=_SL_DB_PATH)
_RUN_OUTPUT = Path("docs/reports/run_output_latest.json")
_PRICE_FEED_PATH = Path("docs/market_data/price_feed.json")
_CONSUMPTION_FEED_PATH = Path("docs/market_data/consumption_feed.json")


def _load_trading_data() -> dict:
    if not _RUN_OUTPUT.exists():
        return {}
    data = json.loads(_RUN_OUTPUT.read_text())
    years = data.get("years", {})
    he_total = data.get("hedge_effectiveness_total", {})
    by_year = [
        {
            "year": yr,
            "actual_net": round(years[yr].get("hedge_effectiveness", {}).get("actual_net_gbp", 0.0), 2),
            "naked_net": round(years[yr].get("hedge_effectiveness", {}).get("naked_net_gbp", 0.0), 2),
            "value_add": round(years[yr].get("hedge_effectiveness", {}).get("hedging_value_add_gbp", 0.0), 2),
        }
        for yr in sorted(years.keys())
        if years[yr].get("hedge_effectiveness")
    ]
    return {
        "by_year": by_year,
        "total_actual_net": round(he_total.get("actual_net_gbp", 0.0), 2),
        "total_naked_net": round(he_total.get("naked_net_gbp", 0.0), 2),
        "total_value_add": round(he_total.get("hedging_value_add_gbp", 0.0), 2),
        "best": he_total.get("best_decision"),
        "worst": he_total.get("worst_decision"),
    }


def _load_spot_prices() -> dict:
    """Return latest spot prices from the M3 price feed."""
    feed = PriceFeed(_PRICE_FEED_PATH)
    if not feed.is_available():
        return {}
    elec = feed.get_latest_spot("electricity")
    gas = feed.get_latest_spot("gas")
    elec_fwd = feed.get_forward_price_estimate("electricity")
    gas_fwd = feed.get_forward_price_estimate("gas")
    return {
        "elec_spot": round(elec, 2) if elec else None,
        "gas_spot": round(gas, 2) if gas else None,
        "elec_forward": round(elec_fwd, 2) if elec_fwd else None,
        "gas_forward": round(gas_fwd, 2) if gas_fwd else None,
        "stale": feed.is_stale(),
        "available": True,
    }




def _load_regulatory_data() -> dict:
    """Build regulatory compliance summary from observable company data."""
    customers = list(_CUSTOMER_INDEX.values())
    resi = [c for c in customers if c.get("segment") == "resi"]
    resi_with_sm = [c for c in resi if c.get("smart_meter") or c.get("metering") == "HH"]
    resi_pen = len(resi_with_sm) / len(resi) if resi else 0.0

    latest_year = 2025
    target = smart_meter_target(latest_year, "resi")
    sm_status = smart_meter_compliance_status(resi_pen, latest_year, "resi")

    # Solvency from run output (observable: company knows its treasury + customer count)
    treasury = 0.0
    n_customers = len(customers)
    total_revenue = 0.0
    if _RUN_OUTPUT.exists():
        run = json.loads(_RUN_OUTPUT.read_text())
        treasury = run.get("final_treasury_gbp", 0.0)
        total_revenue = run.get("total_revenue_gbp", 0.0)
        yrs = run.get("years", {})
        if yrs:
            last_yr = sorted(yrs.keys())[-1]
            ids = yrs[last_yr].get("active_customer_ids", [])
            if ids:
                n_customers = len(ids)

    solvency = compute_solvency_signal(treasury, n_customers)
    mcr_req = n_customers * MCR_FLOOR_GBP_PER_CUSTOMER
    mcr_headroom = treasury - mcr_req
    turnover_fee = annual_turnover_fee(total_revenue)

    from datetime import datetime as _dt
    css_year = _dt.now().year
    css = generate_css_filing(_SERVICE_LOG.as_dicts(), css_year)
    whd = whd_summary(_SERVICE_LOG, css_year)
    return {
        "resi_penetration_pct": round(resi_pen * 100, 1),
        "resi_sm_count": len(resi_with_sm),
        "resi_total": len(resi),
        "sm_target_pct": round(target * 100, 1),
        "sm_status": sm_status,
        "solvency_status": solvency["status"],
        "solvency_ratio": round(solvency["solvency_ratio"], 2),
        "treasury_gbp": round(treasury, 2),
        "mcr_req_gbp": round(mcr_req, 2),
        "mcr_headroom_gbp": round(mcr_headroom, 2),
        "customer_count": n_customers,
        "mcr_floor_per_customer": MCR_FLOOR_GBP_PER_CUSTOMER,
        "total_revenue_gbp": round(total_revenue, 2),
        "annual_turnover_fee_gbp": round(turnover_fee, 2),
        "year": latest_year,
        "css": css,
        "whd": whd,
        "ombudsman_count": _SERVICE_LOG.ombudsman_count(),
    }

app = FastAPI(title="Customer Portal", docs_url=None, redoc_url=None)

_CUSTOMER_INDEX: dict[str, dict] = {c["customer_id"]: c for c in CUSTOMERS}


def _invoice_summary(account_id: str, db_path: Path) -> dict:
    if not db_path.exists():
        return {"count": 0, "billed_gbp": 0.0, "paid_gbp": 0.0, "outstanding_gbp": 0.0}
    invoices = invoices_for_account(account_id, db_path)
    billed = sum(i["total_gbp"] for i in invoices)
    paid = sum(i["total_gbp"] for i in invoices if i["payment_status"] == "paid")
    outstanding = sum(
        i["total_gbp"] for i in invoices
        if i["payment_status"] in ("unpaid", "partially_paid")
    )
    return {
        "count": len(invoices),
        "billed_gbp": round(billed, 2),
        "paid_gbp": round(paid, 2),
        "outstanding_gbp": round(outstanding, 2),
    }



def _tou_band(date_str: str, hour: float) -> str:
    """Determine ToU pricing band from date and hour. Company product definition."""
    from datetime import date as _d
    d = _d.fromisoformat(date_str)
    if d.weekday() >= 5:  # weekends always off-peak
        return "Off-Peak"
    return "Peak" if 7 <= hour < 19 else "Off-Peak"

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, account_id: str = Form(...)):
    acct = account_id.strip().upper()
    if acct not in _CUSTOMER_INDEX:
        return templates.TemplateResponse(
            request, "login.html",
            {"error": f"Account '{acct}' not found."},
            status_code=401,
        )
    return RedirectResponse(f"/account/{acct}", status_code=303)


@app.get("/account/{account_id}", response_class=HTMLResponse)
async def dashboard(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    summary = _invoice_summary(account_id, _DEFAULT_DB)
    whd_eligible = account_id in [
        f.customer_id for f in _SERVICE_LOG.vulnerability_register()
    ]
    renewal = renewal_summary(customer)
    switch_rec = switching_recommendation(customer)
    efficiency = efficiency_summary(customer)
    return templates.TemplateResponse(
        request, "dashboard.html",
        {"customer": customer, "summary": summary, "whd_eligible": whd_eligible,
         "renewal": renewal, "switch_rec": switch_rec, "efficiency": efficiency},
    )


@app.get("/account/{account_id}/bills", response_class=HTMLResponse)
async def bills_page(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    inv_list = (
        invoices_for_account(account_id, _DEFAULT_DB)
        if _DEFAULT_DB.exists()
        else []
    )
    return templates.TemplateResponse(
        request, "bills.html",
        {"customer": customer, "invoices": inv_list},
    )

@app.get("/trading", response_class=HTMLResponse)
async def trading_desk(request: Request):
    data = _load_trading_data()
    return templates.TemplateResponse(
        request, "trading.html",
        {"data": data, "spot": _load_spot_prices()},
    )


@app.get("/account/{account_id}/tariff-compare", response_class=HTMLResponse)
async def tariff_compare(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    import json as _json
    _as_of = "2025-01-01"
    if _RUN_OUTPUT.exists():
        _d = _json.loads(_RUN_OUTPUT.read_text())
        _yrs = sorted(_d.get("years", {}).keys())
        if _yrs:
            _as_of = f"{_yrs[-1]}-06-01"
    options = compare_tariffs(
        eac_kwh=customer["eac_kwh"],
        sim_interface=_SIM_INTERFACE,
        as_of_date=_as_of,
        segment=customer.get("segment", "resi"),
    )
    return templates.TemplateResponse(
        request, "tariff_compare.html",
        {"customer": customer, "options": options},
    )


@app.post("/account/{account_id}/switch-tariff", response_class=HTMLResponse)
async def switch_tariff(
    request: Request,
    account_id: str,
    tariff_name: str = Form(...),
    term_months: int = Form(...),
):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    from datetime import date
    import hashlib
    ref = "SW-" + hashlib.sha1(f"{account_id}{tariff_name}{date.today()}".encode()).hexdigest()[:8].upper()
    return templates.TemplateResponse(
        request, "tariff_switch_confirm.html",
        {"customer": customer, "tariff_name": tariff_name, "term_months": term_months, "ref": ref},
    )

@app.get("/account/{account_id}/consumption", response_class=HTMLResponse)
async def consumption_page(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    records = consumption_history(account_id, _DEFAULT_DB)
    data = monthly_totals(records)
    is_hh = customer.get("metering") == "HH"
    total_kwh = sum(r["kwh"] for r in data)
    hh_data: list[dict] = []
    if is_hh and is_feed_available(_CONSUMPTION_FEED_PATH):
        all_hh = get_hh_consumption(account_id, _CONSUMPTION_FEED_PATH)
        hh_data = recent_hh_periods(all_hh, n_periods=48)
    calibrated_eac = calibrate_eac(account_id, _DEFAULT_DB)
    orig_eac = customer.get("eac_kwh") or 0
    drift = eac_drift(orig_eac, calibrated_eac) if calibrated_eac and orig_eac else None
    is_tou = bool(customer.get("smart_meter")) or is_hh
    if hh_data and is_tou:
        for rec in hh_data:
            rec["band"] = _tou_band(str(rec["date"]), float(rec["hour"]))
    # Typical UK residential rates (company knows its own tariff structure)
    _ELEC_UNIT_P = 24.5  # p/kWh approximate current rate
    _ELEC_SC_P = 61.0    # p/day standing charge
    cost_forecast = forecast_annual_cost(
        account_id, _ELEC_UNIT_P, _ELEC_SC_P, _DEFAULT_DB
    )
    rate_cmp = market_rate_comparison(account_id, _DEFAULT_DB)
    return templates.TemplateResponse(
        request, "consumption.html",
        {"customer": customer, "monthly_data": data, "is_hh": is_hh,
         "total_kwh": total_kwh, "hh_data": hh_data, "is_tou": is_tou,
         "calibrated_eac": calibrated_eac, "eac_drift": drift,
         "cost_forecast": cost_forecast, "rate_cmp": rate_cmp},
    )

@app.post("/account/{account_id}/pay", response_class=HTMLResponse)
async def submit_payment(
    request: Request,
    account_id: str,
    invoice_number: int = Form(...),
    amount_gbp: float = Form(...),
):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    if not _DEFAULT_DB.exists():
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice = get_invoice(invoice_number, _DEFAULT_DB)
    if invoice is None or invoice["account_id"] != account_id:
        raise HTTPException(status_code=404, detail="Invoice not found")
    payment_event = {
        "event_type": "payment_received_event",
        "customer_id": account_id,
        "bill_period_end": invoice["billing_period_end"],
        "amount_gbp": amount_gbp,
    }
    result = reconcile_payment(payment_event, _DEFAULT_DB)
    return templates.TemplateResponse(
        request, "payment_confirm.html",
        {
            "customer": customer,
            "invoice": invoice,
            "amount_gbp": amount_gbp,
            "result": result,
        },
    )

@app.get("/regulatory", response_class=HTMLResponse)
async def regulatory_dashboard(request: Request):
    reg = _load_regulatory_data()
    return templates.TemplateResponse(
        request, "regulatory.html",
        {"reg": reg},
    )

def _load_admin_data() -> dict:
    """Aggregate portfolio view for admin dashboard."""
    customers = list(_CUSTOMER_INDEX.values())
    db = _DEFAULT_DB
    rows = []
    total_billed = total_paid = total_outstanding = total_bad_debt = 0.0
    for c in sorted(customers, key=lambda x: x["customer_id"]):
        cid = c["customer_id"]
        summary = _invoice_summary(cid, db)
        rows.append({
            "customer_id": cid,
            "segment": c.get("segment", ""),
            "commodity": c.get("commodity", ""),
            "eac_kwh": c.get("eac_kwh", 0),
            "smart_meter": c.get("smart_meter", False) or c.get("metering") == "HH",
            "invoices": summary["count"],
            "outstanding_gbp": summary["outstanding_gbp"],
            "paid_gbp": summary["paid_gbp"],
        })
        total_billed += summary["billed_gbp"]
        total_paid += summary["paid_gbp"]
        total_outstanding += summary["outstanding_gbp"]
    # bad debt from DB
    if db.exists():
        from company.billing.invoice import _conn, create_schema
        create_schema(db)
        import sqlite3
        with _conn(db) as conn:
            r = conn.execute(
                "SELECT COALESCE(SUM(total_gbp),0) FROM invoices WHERE payment_status='bad_debt'"
            ).fetchone()
            total_bad_debt = r[0] if r else 0.0
    csat = _SERVICE_LOG.csat_summary()
    return {
        "customers": rows,
        "total_customers": len(rows),
        "total_billed_gbp": round(total_billed, 2),
        "total_paid_gbp": round(total_paid, 2),
        "total_outstanding_gbp": round(total_outstanding, 2),
        "total_bad_debt_gbp": round(total_bad_debt, 2),
        "csat": csat,
    }



@app.get("/admin", response_class=HTMLResponse)
async def admin_overview(request: Request):
    data = _load_admin_data()
    return templates.TemplateResponse(
        request, "admin.html",
        {"data": data},
    )

@app.get("/account/{account_id}/statement", response_class=HTMLResponse)
async def account_statement(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    inv_list = (
        invoices_for_account(account_id, _DEFAULT_DB)
        if _DEFAULT_DB.exists()
        else []
    )
    billed = sum(i["total_gbp"] for i in inv_list)
    paid = sum(i["total_gbp"] for i in inv_list if i["payment_status"] == "paid")
    outstanding = sum(
        i["total_gbp"] for i in inv_list
        if i["payment_status"] in ("unpaid", "partially_paid")
    )
    bad_debt = sum(i["total_gbp"] for i in inv_list if i["payment_status"] == "bad_debt")
    return templates.TemplateResponse(
        request, "statement.html",
        {
            "customer": customer,
            "invoices": inv_list,
            "total_billed_gbp": round(billed, 2),
            "total_paid_gbp": round(paid, 2),
            "total_outstanding_gbp": round(outstanding, 2),
            "total_bad_debt_gbp": round(bad_debt, 2),
        },
    )

@app.get("/account/{account_id}/direct-debit", response_class=HTMLResponse)
async def direct_debit_page(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    mandate = get_mandate(account_id, _DD_DB)
    return templates.TemplateResponse(
        request, "direct_debit.html",
        {"customer": customer, "mandate": mandate},
    )


@app.post("/account/{account_id}/direct-debit", response_class=HTMLResponse)
async def set_direct_debit(
    request: Request,
    account_id: str,
    sort_code: str = Form(...),
    account_number: str = Form(...),
    payment_day: int = Form(...),
):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    try:
        mandate = set_mandate(account_id, sort_code, account_number, payment_day, _DD_DB)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return templates.TemplateResponse(
        request, "direct_debit.html",
        {"customer": customer, "mandate": mandate, "success": True},
    )


@app.post("/account/{account_id}/direct-debit/cancel", response_class=HTMLResponse)
async def cancel_direct_debit(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    cancel_mandate(account_id, _DD_DB)
    return templates.TemplateResponse(
        request, "direct_debit.html",
        {"customer": customer, "mandate": None, "cancelled": True},
    )

@app.get("/account/{account_id}/contact", response_class=HTMLResponse)
async def contact_page(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    return templates.TemplateResponse(
        request, "contact.html",
        {"customer": customer},
    )


@app.post("/account/{account_id}/contact", response_class=HTMLResponse)
async def submit_contact(
    request: Request,
    account_id: str,
    contact_reason: str = Form(...),
    notes: str = Form(""),
    complaint: str = Form(""),
):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    from datetime import date
    event = ServiceEvent(
        customer_id=account_id,
        event_date=date.today().isoformat(),
        channel="portal",
        contact_reason=contact_reason,
        outcome="pending",
        agent_type="ai",
        complaint_flag=(complaint == "yes"),
        notes=notes.strip(),
    )
    _SERVICE_LOG.record_contact(event)
    contact_id = _SERVICE_LOG.latest_contact_id(account_id)
    return templates.TemplateResponse(
        request, "contact.html",
        {"customer": customer, "submitted": True, "complaint": complaint == "yes",
         "contact_id": contact_id},
    )

@app.get("/admin/complaints", response_class=HTMLResponse)
async def admin_complaints(request: Request):
    deadlines = _SERVICE_LOG.complaint_deadlines()
    ombudsman = _SERVICE_LOG.ombudsman_eligible()
    return templates.TemplateResponse(
        request, "admin_complaints.html",
        {"deadlines": deadlines, "ombudsman": ombudsman},
    )

@app.get("/admin/collections", response_class=HTMLResponse)
async def admin_collections(request: Request):
    queue = get_collections_queue(_DEFAULT_DB) if _DEFAULT_DB.exists() else []
    return templates.TemplateResponse(
        request, "admin_collections.html",
        {"queue": queue},
    )

@app.get("/admin/renewals", response_class=HTMLResponse)
async def admin_renewals(request: Request):
    from datetime import date
    horizon = 90  # days ahead
    upcoming = []
    for customer in list(_CUSTOMER_INDEX.values()):
        days = days_until_renewal(customer)
        if days is not None and days <= horizon:
            upcoming.append({
                "account_id": customer["customer_id"],
                "segment": customer.get("segment", ""),
                "contract_type": customer.get("contract_type", ""),
                "end_date": contract_end_date(customer).isoformat(),
                "days_remaining": days,
            })
    upcoming.sort(key=lambda x: x["days_remaining"])
    return templates.TemplateResponse(
        request, "admin_renewals.html",
        {"upcoming": upcoming, "horizon": horizon},
    )


@app.get("/account/{account_id}/smart-meter", response_class=HTMLResponse)
async def smart_meter_get(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    already_hh = customer.get("metering") == "HH" or customer.get("smart_meter") is True
    return templates.TemplateResponse(
        request, "smart_meter.html",
        {"customer": customer, "already_hh": already_hh, "submitted": False, "ref": None},
    )


@app.post("/account/{account_id}/smart-meter", response_class=HTMLResponse)
async def smart_meter_post(request: Request, account_id: str):
    from datetime import date as _date
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    form = await request.form()
    contact_pref = str(form.get("contact_pref", "morning"))
    notes = str(form.get("notes", ""))
    today = _date.today().isoformat()
    ref = today.replace("-", "")
    _SERVICE_LOG.record_contact(ServiceEvent(
        customer_id=account_id,
        event_date=today,
        channel="portal",
        contact_reason="smart_meter",
        outcome="upgrade_requested",
        agent_type="self_service",
        complaint_flag=False,
        vulnerability_flag=False,
        notes=f"contact_pref={contact_pref}; {notes}".strip("; "),
    ))
    return templates.TemplateResponse(
        request, "smart_meter.html",
        {"customer": customer, "already_hh": False, "submitted": True, "ref": ref},
    )


@app.post("/account/{account_id}/contact/rate", response_class=HTMLResponse)
async def rate_contact(request: Request, account_id: str):
    customer = _CUSTOMER_INDEX.get(account_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Account not found")
    form = await request.form()
    contact_id = int(form.get("contact_id", 0))
    score_str = form.get("score", "")
    if score_str and score_str.isdigit():
        score = int(score_str)
        if 1 <= score <= 5:
            _SERVICE_LOG.rate_contact(contact_id, score)
    return templates.TemplateResponse(
        request, "contact.html",
        {"customer": customer, "submitted": True, "complaint": False,
         "contact_id": None, "rated": True},
    )
