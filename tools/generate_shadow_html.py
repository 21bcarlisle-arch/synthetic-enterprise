#!/usr/bin/env python3
"""Generate site/shadow/ static HTML mirror of the SPA site.

Pages: index, customers, supplier, sim, project
"""
import json
from pathlib import Path
from datetime import datetime, timezone

PROJECT = Path(__file__).resolve().parent.parent
SHADOW = PROJECT / "site" / "shadow"
DATA = PROJECT / "site" / "data"
LATEST_MD = PROJECT / "docs" / "status" / "LATEST.md"

NAV_LINKS = [
    ("Overview", "/shadow/"),
    ("Customers", "/shadow/customers/"),
    ("Supplier", "/shadow/supplier/"),
    ("Sim", "/shadow/sim/"),
    ("Project", "/shadow/project/"),
]

CSS = (
    "<style>"
    "body{font-family:monospace;background:#1a1a1a;color:#e0e0e0;margin:0;padding:16px}"
    "h1,h2{color:#aaf}table{border-collapse:collapse;width:100%;margin-bottom:24px}"
    "th{background:#2a2a4a;color:#aaf;text-align:left;padding:6px 10px;border:1px solid #333}"
    "td{padding:5px 10px;border:1px solid #2a2a2a;vertical-align:top}"
    "tr:nth-child(even){background:#1e1e1e}"
    ".pos{color:#4f4}.neg{color:#f44}"
    ".meta{color:#888;font-size:0.85em;margin-bottom:16px}"
    "pre{background:#111;padding:12px;overflow-x:auto;color:#cce;white-space:pre-wrap}"
    "dl{display:grid;grid-template-columns:200px 1fr;gap:4px 16px;margin-bottom:16px}"
    "dt{color:#aaf}dd{margin:0}"
    "</style>"
)


def _nav(active=""):
    parts = []
    for name, href in NAV_LINKS:
        if name == active:
            parts.append('<strong style="color:#fff">' + name + "</strong>")
        else:
            parts.append('<a href="' + href + '" style="color:#88f">' + name + "</a>")
    extras = (
        ' | <a href="/" style="color:#666">Live site</a>'
        ' | <a href="/state/customer_sample.json" style="color:#666">customer_sample.json</a>'
    )
    inner = " &bull; ".join(parts) + extras
    return '<nav style="background:#111;color:#ccc;padding:8px;font-family:monospace">' + inner + "</nav>"


def _gbp(v, d=0):
    if v is None:
        return "&#8212;"
    sign = "-" if v < 0 else ""
    return sign + "&pound;" + format(abs(v), ",." + str(d) + "f")


def _pct(v, d=1):
    if v is None:
        return "&#8212;"
    return format(v * 100, "." + str(d) + "f") + "%"


def _cls(v):
    return "" if v is None else ("pos" if v >= 0 else "neg")


def _page(title, active, body, ts):
    footer = (
        '<p class="meta">Generated: ' + ts
        + ' | <a href="/state/customer_sample.json" style="color:#666">customer_sample.json</a></p>'
    )
    return (
        "<!DOCTYPE html><html lang=en><head><meta charset=UTF-8>"
        + "<title>" + title + " - Synthetic Enterprise</title>" + CSS + "</head>"
        + "<body>" + _nav(active) + body + footer + "</body></html>"
    )


def _row(*cells):
    return "<tr>" + "".join("<td>" + str(c) + "</td>" for c in cells) + "</tr>"


def _hrow(*labels):
    return "<tr>" + "".join("<th>" + str(l) + "</th>" for l in labels) + "</tr>"


def _table(headers, rows_html):
    if not rows_html:
        rows_html = "<tr><td colspan=" + str(len(headers)) + ">No data</td></tr>"
    return "<table>" + _hrow(*headers) + rows_html + "</table>"



def build_index(dash, ts):
    p = dash["portfolio"]
    ins = dash.get("insights", {})
    build = dash.get("build", {})
    summary = ins.get("executive_summary", "")

    net = p.get("net_margin_gbp", 0)
    gross = p.get("gross_margin_gbp", 0)
    ev = p.get("enterprise_value_gbp", 0)
    t_start = p.get("treasury_start_gbp", 0)
    t_end = p.get("treasury_end_gbp", 0)
    phase = build.get("current_phase", "?")
    tests = build.get("test_count", "?")
    modules = build.get("company_modules", "?")
    bills = p.get("bills_total", "")
    churns = p.get("churn_count", "")
    ret_off = p.get("retention_offers", "")
    ret_ret = p.get("retention_retained", "")
    cts = p.get("cost_to_serve_gbp")

    ann_rows = ""
    for r in dash["financial"]["annual"]:
        yr = r["year"]
        g = r.get("gross_gbp", 0)
        n = r.get("net_gbp", 0)
        tr = r.get("treasury_end_gbp", 0)
        bc = r.get("bills_count", "")
        shock = r.get("avg_bill_shock_pct", 0)
        ann_rows += _row(
            yr,
            '<span class="' + _cls(g) + '">' + _gbp(g) + "</span>",
            '<span class="' + _cls(n) + '">' + _gbp(n) + "</span>",
            _gbp(tr),
            bc,
            format(shock * 100, ".0f") + "%",
        )

    insight_rows = ""
    for i in ins.get("insights", []):
        area = i.get("area", "")
        headline = i.get("headline", "")
        narrative = i.get("narrative", "")[:200]
        insight_rows += _row(area, headline, narrative)

    body = (
        "<h1>Synthetic Enterprise &#8212; Portfolio Overview</h1>"
        + '<div class="meta">2016&#8211;2025 | Phase ' + str(phase)
        + " | " + str(tests) + " tests | " + str(modules) + " modules</div>"
        + "<h2>10-Year Totals</h2><dl>"
        + '<dt>Net Margin</dt><dd class="' + _cls(net) + '">' + _gbp(net) + "</dd>"
        + "<dt>Gross Margin</dt><dd>" + _gbp(gross) + "</dd>"
        + "<dt>Enterprise Value</dt><dd>" + _gbp(ev) + "</dd>"
        + "<dt>Treasury Start</dt><dd>" + _gbp(t_start) + "</dd>"
        + "<dt>Treasury End</dt><dd>" + _gbp(t_end) + "</dd>"
        + "<dt>Bills Issued</dt><dd>" + str(bills) + "</dd>"
        + "<dt>Churn Events</dt><dd>" + str(churns) + "</dd>"
        + "<dt>Retention Offers</dt><dd>" + str(ret_off) + " (retained " + str(ret_ret) + ")</dd>"
        + "<dt>Cost to Serve</dt><dd>" + _gbp(cts) + "</dd>"
        + "</dl>"
        + _table(["Year", "Gross", "Net", "Treasury", "Bills", "Avg Shock"], ann_rows)
        + "<h2>Executive Summary</h2><pre>" + summary + "</pre>"
        + _table(["Area", "Headline", "Narrative (excerpt)"], insight_rows)
    )
    return _page("Portfolio Overview", "Overview", body, ts)


def build_customers(dash, sample, ts):
    lifetime = dash["customers"].get("lifetime", {})
    events_by_cid = {}
    for e in dash["customers"].get("events", []):
        cid_e = e["customer_id"]
        events_by_cid.setdefault(cid_e, []).append(e)
    retention = dash["customers"].get("retention", [])
    sample_custs = sample.get("customers", {})

    rows = ""
    for cid in sorted(lifetime):
        if cid.endswith("g"):
            continue
        c = lifetime[cid]
        s = sample_custs.get(cid, {})
        clv = s.get("clv_gbp", 0)
        churn = s.get("latest_churn_probability")
        ev_list = events_by_cid.get(cid, [])
        last_ev = ev_list[-1] if ev_list else {}
        net_lt = c.get("net_gbp", 0)
        gross_lt = c.get("gross_gbp", 0)
        rows += _row(
            cid,
            c.get("segment", ""),
            c.get("commodity", ""),
            c.get("acquisition_date", ""),
            '<span class="' + _cls(net_lt) + '">' + _gbp(net_lt) + "</span>",
            _gbp(gross_lt),
            _gbp(clv),
            _pct(churn) if churn is not None else "&#8212;",
            last_ev.get("type", ""),
            last_ev.get("date", ""),
        )

    ret_rows = ""
    for r in retention:
        disc = r.get("discount_pct", "")
        cost = _gbp(r.get("cost_gbp"))
        outcome = r.get("outcome", "")
        ret_rows += _row(r["customer_id"], r["date"], disc, cost, outcome)

    body = (
        "<h1>Customer Portfolio</h1>"
        + '<p class="meta">Source: customer_sample.json + dashboard.json</p>'
        + "<h2>All Customers (electricity accounts)</h2>"
        + _table(
            ["CID", "Segment", "Commodity", "Acquired", "Net Lifetime", "Gross", "CLV", "Churn", "Last Event", "Date"],
            rows,
        )
        + "<h2>Retention Offers</h2>"
        + _table(["Customer", "Date", "Discount", "Cost", "Outcome"], ret_rows)
        + "<h2>Full Ground Truth</h2>"
        + "<p>Machine-readable per-customer data:<br>"
        + '<a href="/state/customer_sample.json">customer_sample.json</a></p>'
    )
    return _page("Customer Portfolio", "Customers", body, ts)



def build_supplier(dash, ts):
    annual = dash["financial"]["annual"]
    ledger = dash["financial"].get("ledger", {})
    seg = dash["financial"].get("segment_annual", [])

    ann_rows = ""
    for r in annual:
        yr = r["year"]
        rev = r.get("revenue_gbp", 0)
        g = r.get("gross_gbp", 0)
        cap = r.get("capital_gbp", 0)
        pol = r.get("policy_cost_gbp", 0)
        bd = r.get("bad_debt_gbp", 0)
        n = r.get("net_gbp", 0)
        tr = r.get("treasury_end_gbp", 0)
        ann_rows += _row(
            yr,
            _gbp(rev),
            _gbp(g),
            _gbp(cap),
            _gbp(pol),
            _gbp(bd),
            '<span class="' + _cls(n) + '">' + _gbp(n) + "</span>",
            _gbp(tr),
        )

    led_rows = ""
    for k, v in ledger.items():
        if isinstance(v, (int, float)):
            cell = '<span class="' + _cls(v) + '">' + _gbp(v) + "</span>"
        else:
            cell = str(v)
        led_rows += _row(k, cell)

    seg_rows = ""
    for s in seg:
        yr = s.get("year", "")
        seg_name = s.get("segment", "")
        g = s.get("gross_gbp", 0)
        n = s.get("net_gbp", 0)
        cnt = s.get("customer_count", "")
        seg_rows += _row(yr, seg_name, _gbp(g), _gbp(n), cnt)

    body = (
        "<h1>Supplier Financial Statements</h1>"
        + "<h2>Annual Income Statement</h2>"
        + _table(["Year", "Revenue", "Gross", "Capital", "Policy", "Bad Debt", "Net", "Treasury"], ann_rows)
        + "<h2>10-Year Ledger</h2>"
        + _table(["Line Item", "Total 2016-2025"], led_rows)
        + "<h2>Annual P&amp;L by Segment</h2>"
        + _table(["Year", "Segment", "Gross", "Net", "Customers"], seg_rows)
    )
    return _page("Supplier P&amp;L", "Supplier", body, ts)


def build_sim(sim_data, ts):
    annual = sim_data.get("annual", [])
    monthly = sim_data.get("monthly", [])[:12]
    peaks = sim_data.get("peak_records", [])[:5]
    meta = sim_data.get("metadata", {})
    period_from = meta.get("period_from", "")
    period_to = meta.get("period_to", "")
    total_rec = meta.get("total_records", "")

    ann_rows = ""
    for r in annual:
        ann_rows += _row(r["year"], format(r.get("mean", 0), ".2f"),
                         format(r.get("p95", 0), ".2f"), format(r.get("max", 0), ".2f"))

    mon_rows = ""
    for r in monthly:
        mon_rows += _row(r["month"], format(r.get("mean", 0), ".2f"),
                         format(r.get("p95", 0), ".2f"))

    peak_rows = ""
    for r in peaks:
        peak_rows += _row(
            r.get("date", ""),
            r.get("settlement_period", r.get("period", "")),
            format(r.get("ssp", r.get("mean", 0)), ".2f"),
        )

    body = (
        "<h1>Simulation Data &#8212; Elexon Settlement Prices</h1>"
        + '<div class="meta">Period: ' + period_from + " &#8211; " + period_to
        + " | " + str(total_rec) + " HH records</div>"
        + "<h2>Annual SSP Statistics (GBP/MWh)</h2>"
        + _table(["Year", "Mean SSP", "P95 SSP", "Max SSP"], ann_rows)
        + "<h2>Monthly SSP (most recent 12)</h2>"
        + _table(["Month", "Mean SSP", "P95 SSP"], mon_rows)
        + "<h2>Peak SSP Records</h2>"
        + _table(["Date", "Settlement Period", "SSP (GBP/MWh)"], peak_rows)
    )
    return _page("Simulation Data", "Sim", body, ts)


def build_project(dash, latest_md, ts):
    build = dash.get("build", {})
    run_hist = dash.get("run_history", [])
    phase = build.get("current_phase", "")
    tests = build.get("test_count", "")
    modules = build.get("company_modules", "")
    sim_window = build.get("simulation_window", "")

    hist_rows = ""
    for r in run_hist[:10]:
        git = r.get("git", "")
        date = r.get("date", "")
        n = r.get("net_gbp", 0)
        hist_rows += _row(git, date, '<span class="' + _cls(n) + '">' + _gbp(n) + "</span>")

    body = (
        "<h1>Project Status</h1>"
        + "<dl>"
        + "<dt>Current Phase</dt><dd>" + str(phase) + "</dd>"
        + "<dt>Test Count</dt><dd>" + str(tests) + "</dd>"
        + "<dt>Company Modules</dt><dd>" + str(modules) + "</dd>"
        + "<dt>Simulation Window</dt><dd>" + str(sim_window) + "</dd>"
        + "</dl>"
        + "<h2>LATEST.md</h2>"
        + "<pre>" + latest_md[:3000] + "</pre>"
        + "<h2>Recent Simulation Runs</h2>"
        + _table(["Git Commit", "Date", "Net Margin"], hist_rows)
    )
    return _page("Project Status", "Project", body, ts)


def generate(run_json_path=None):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    dash = json.loads((DATA / "dashboard.json").read_text())
    sim_data = json.loads((DATA / "sim_data.json").read_text())
    sample_path = DATA / "customer_sample.json"
    sample = json.loads(sample_path.read_text()) if sample_path.exists() else {}
    latest_md = LATEST_MD.read_text() if LATEST_MD.exists() else ""

    pages = {
        SHADOW / "index.html": build_index(dash, ts),
        SHADOW / "customers" / "index.html": build_customers(dash, sample, ts),
        SHADOW / "supplier" / "index.html": build_supplier(dash, ts),
        SHADOW / "sim" / "index.html": build_sim(sim_data, ts),
        SHADOW / "project" / "index.html": build_project(dash, latest_md, ts),
    }

    for path, html in pages.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        print("Generated", str(path.relative_to(PROJECT)))

    return list(pages.keys())


if __name__ == "__main__":
    generate()
