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

from company.billing.invoice import invoices_for_account
from saas.customers import CUSTOMERS

_TEMPLATE_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATE_DIR))

_DEFAULT_DB = Path("company/data/invoices.db")
_RUN_OUTPUT = Path("docs/reports/run_output_latest.json")


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
        {"data": data},
    )
