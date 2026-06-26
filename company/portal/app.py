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
from company.pricing.tariff_comparison import compare_tariffs
from company.interfaces.sim_interface import LiveSimInterface

_SIM_INTERFACE = LiveSimInterface()
from saas.customers import CUSTOMERS

_TEMPLATE_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATE_DIR))

_DEFAULT_DB = Path("company/data/invoices.db")
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
    return templates.TemplateResponse(
        request, "dashboard.html",
        {"customer": customer, "summary": summary},
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
    return templates.TemplateResponse(
        request, "consumption.html",
        {"customer": customer, "monthly_data": data, "is_hh": is_hh,
         "total_kwh": total_kwh, "hh_data": hh_data},
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
