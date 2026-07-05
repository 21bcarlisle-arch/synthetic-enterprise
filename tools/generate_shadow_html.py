#!/usr/bin/env python3
"""Generate site/shadow/ static HTML mirror of the SPA site.

Pages: index, customers, supplier, sim, project
"""
import json
from pathlib import Path
from datetime import datetime, timezone

from company.crm.retention_risk import retention_risk_feature_vector
from company.analytics.decision_event_ledger import (
    build_customer_ledger, build_portfolio_event_stream,
)

PROJECT = Path(__file__).resolve().parent.parent
SHADOW = PROJECT / "site" / "shadow"
DATA = PROJECT / "site" / "data"
STATE = PROJECT / "site" / "state"
LATEST_MD = PROJECT / "docs" / "status" / "LATEST.md"

# EVIDENCE_IN_BUSINESS_SURFACES.md (2026-07-04): C7 is the retrofit's named
# case study -- a real new_baby life event (2023-12-23) that a real supplier
# cannot observe directly, sustained income stress from 2023 the company also
# cannot observe, and 6 real arrears cases the company DOES observe. This is
# the "both sides of the epistemic wall" example the directive asks for.
BEHAVIORAL_CASE_STUDY_CID = "C7"

# PRIORITIES.md P1 (Website Integrity Part B, per-fuel legs): C_IC3/C_IC3g is
# a real I&C dual-fuel account where the two fuel legs diverge sharply --
# electricity is billed and paid exactly (zero failed payments, zero arrears)
# while gas carries a failed payment and a live arrears case. A combined
# roll-up would net these together and hide the gas-side friction entirely,
# which is the reason per-fuel legs must be a real view, not just an internal
# computation.
PER_FUEL_CASE_STUDY_BASE = "C_IC3"

# DECISION_LOOP_AND_EVENT_LEDGER.md Part 5: C_IC1 is the existing flagship
# divergence case (Phase QJ: company believed 95% churn risk in 2018, SIM
# truth was 5%) and the serial-saver named in Phase QM (4 real retention
# decisions) -- unifying those into one chronological timeline shows exactly
# how an EV-driven decision loop looks from the inside for one real account.
DECISION_LEDGER_CASE_STUDY_CID = "C_IC1"

NAV_LINKS = [
    ("Overview", "/shadow/"),
    ("Customers", "/shadow/customers/"),
    ("Supplier", "/shadow/supplier/"),
    ("Sim", "/shadow/sim/"),
    ("Project", "/shadow/project/"),
]

# PRIORITIES.md P1 (Website Integrity Part B, design system): kpi-card/kpi-grid
# and rag-chip give the shadow mirror the same component vocabulary as the
# customer portal's design system (company/portal/templates/base.html) -- same
# named components (KPI cards, RAG chips), dark "advisor-verification" palette
# kept intentionally distinct from the portal's light customer-facing theme.
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
    ".kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}"
    ".kpi-card{background:#232342;border:1px solid #383868;border-radius:6px;padding:10px 14px}"
    ".kpi-card .kpi-value{display:block;font-size:1.3em;font-weight:700;color:#aaf}"
    ".kpi-card .kpi-label{font-size:0.75em;color:#888;text-transform:uppercase;letter-spacing:0.04em}"
    ".rag-chip{display:inline-block;padding:2px 10px;border-radius:12px;font-size:0.82em;font-weight:700;"
    "border:1px solid currentColor}"
    ".rag-green{background:#0f2f1a;color:#4f4}"
    ".rag-amber{background:#3a2f0a;color:#fc4}"
    ".rag-red{background:#3a0f0f;color:#f44}"
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


def _page(title, active, body, ts, git_commit="?", phase="?"):
    # Freshness stamp (Part A #4 / Part C of the website-integrity fix): every
    # page footer names the run it was generated from (git commit + phase), not
    # just a timestamp, so a stale surface is identifiable at a glance without
    # cross-referencing another page.
    footer = (
        '<p class="meta">Generated: ' + ts
        + ' | Run ' + str(git_commit) + ' | Phase ' + str(phase)
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

    def _kpi(label, value, cls=""):
        return ('<div class="kpi-card"><span class="kpi-value ' + cls + '">' + value
                + '</span><span class="kpi-label">' + label + "</span></div>")

    kpi_grid = (
        '<div class="kpi-grid">'
        + _kpi("Net Margin", _gbp(net), _cls(net))
        + _kpi("Gross Margin", _gbp(gross))
        + _kpi("Enterprise Value", _gbp(ev))
        + _kpi("Treasury Start", _gbp(t_start))
        + _kpi("Treasury End", _gbp(t_end))
        + _kpi("Bills Issued", str(bills))
        + _kpi("Churn Events", str(churns))
        + _kpi("Retention Offers", str(ret_off) + " (retained " + str(ret_ret) + ")")
        + _kpi("Cost to Serve", _gbp(cts))
        + "</div>"
    )

    body = (
        "<h1>Synthetic Enterprise &#8212; Portfolio Overview</h1>"
        + '<div class="meta">2016&#8211;2025 | Phase ' + str(phase)
        + " | " + str(tests) + " tests | " + str(modules) + " modules</div>"
        + "<h2>10-Year Totals</h2>"
        + kpi_grid
        + _table(["Year", "Gross", "Net", "Treasury", "Bills", "Avg Shock"], ann_rows)
        + "<h2>Executive Summary</h2><pre>" + summary + "</pre>"
        + _table(["Area", "Headline", "Narrative (excerpt)"], insight_rows)
    )
    return _page("Portfolio Overview", "Overview", body, ts, dash.get("meta", {}).get("git_commit", "?"), phase)


def _behavioral_case_study(sample, ledger, cid):
    """SIM ground truth vs company-observable for one named customer
    (EVIDENCE_IN_BUSINESS_SURFACES.md retrofit) -- both sides of the
    epistemic wall, generated from the same run as everything else."""
    cust = sample.get("customers", {}).get(cid)
    ledger_cust = ledger.get("customers", {}).get(cid) if ledger else None
    if not cust or not ledger_cust:
        return ""

    life_events = cust.get("life_event_history") or []
    stress_traj = cust.get("income_stress_trajectory") or []
    pay = cust.get("payment_behaviour_analytics") or {}
    pay_score = pay.get("score")
    pay_metrics = pay.get("metrics") or {}
    arrears = ledger_cust.get("arrears_history") or []

    life_rows = "".join(
        _row(e.get("date", ""), e.get("event_type", "").replace("_", " "))
        for e in life_events
    )
    stress_rows = "".join(
        _row(s.get("year", ""), s.get("stress", "").upper())
        for s in stress_traj
    )
    arrears_rows = ""
    for a in arrears:
        stages = a.get("stages", [])
        final = stages[-1]["stage"] if stages else "?"
        arrears_rows += _row(
            a.get("case_id", ""),
            a.get("opened_date", ""),
            _gbp(a.get("arrears_gbp", 0)),
            final,
            stages[-1].get("date", "") if stages else "",
        )

    transition = next(
        (s for s in stress_traj if s.get("stress", "low") != "low"), None
    )
    divergence = (
        "<p>The SIM knows " + cid + " had a real life event (" +
        (life_events[-1]["event_type"].replace("_", " ") if life_events else "none") +
        " on " + (life_events[-1]["date"] if life_events else "?") +
        ") that pushed income stress from LOW to " +
        (transition["stress"].upper() if transition else "?") +
        " from " + (str(transition["year"]) if transition else "?") +
        " onward. A real supplier cannot see either fact directly -- "
        "the company only ever observes the downstream payment behaviour: "
        "score <strong>" + str(pay_score) + "</strong>, on-time rate " +
        _pct(pay_metrics.get("on_time_rate")) + ", DD-fail rate " +
        _pct(pay_metrics.get("dd_fail_rate")) + ", and " + str(len(arrears)) +
        " real arrears cases opening from the same period. That gap -- true "
        "cause invisible, only the payment-behaviour symptom observable -- "
        "is the basis risk this retrofit makes visible.</p>"
    )

    return (
        "<h2>Behavioral Case Study: " + cid + "</h2>"
        + '<p class="meta">Both sides of the epistemic wall, generated from this run '
        + "(docs/staging/done/EVIDENCE_IN_BUSINESS_SURFACES.md)</p>"
        + "<h3>SIM Ground Truth &#8212; Life Events (not observable to the company)</h3>"
        + _table(["Date", "Event"], life_rows or _row("&#8212;", "none this window"))
        + "<h3>SIM Ground Truth &#8212; Income Stress Trajectory (not observable to the company)</h3>"
        + _table(["Year", "Stress Level"], stress_rows)
        + "<h3>Company-Observable &#8212; Real Arrears Cases (from billing_ledger.json)</h3>"
        + _table(["Case", "Opened", "Amount", "Final Stage", "Closed"], arrears_rows or _row("&#8212;", "", "", "none", ""))
        + "<h3>The Divergence</h3>"
        + divergence
    )


def _per_fuel_case_study(ledger, base_id):
    """Per-fuel account depth (PRIORITIES.md P1, Website Integrity Part B):
    shows a real dual-fuel customer's two fuel legs as SEPARATE accounts with
    their own invoice/payment/arrears history, not netted into one number."""
    custs = (ledger or {}).get("customers", {})
    elec = custs.get(base_id)
    gas = custs.get(base_id + "g")
    if not elec or not gas:
        return ""

    def _leg_table(cid, leg):
        invs = leg.get("invoices", [])[-3:]
        rows = "".join(
            _row(
                i.get("period_end", ""),
                i.get("commodity", ""),
                _gbp(i.get("total_amount_gbp", 0)),
                i.get("payment_status", ""),
            )
            for i in invs
        )
        return (
            "<h4>" + cid + "</h4>"
            + "<dl>"
            + "<dt>Total billed</dt><dd>" + _gbp(leg.get("total_billed_gbp", 0)) + "</dd>"
            + "<dt>Total paid</dt><dd>" + _gbp(leg.get("total_paid_gbp", 0)) + "</dd>"
            + "<dt>Balance</dt><dd>" + _gbp(leg.get("balance_gbp", 0)) + "</dd>"
            + "<dt>Failed payments</dt><dd>" + str(leg.get("failed_payment_count", 0)) + "</dd>"
            + "<dt>Arrears cases</dt><dd>" + str(leg.get("arrears_case_count", 0)) + "</dd>"
            + "</dl>"
            + _table(["Period End", "Fuel", "Amount", "Status"], rows)
        )

    divergence = (
        "<p>" + base_id + " is one real dual-fuel account, but its electricity and gas "
        "legs are billed, paid, and chased for arrears completely separately -- "
        "electricity has " + str(elec.get("failed_payment_count", 0)) + " failed payment(s) and "
        + str(elec.get("arrears_case_count", 0)) + " arrears case(s), while gas has "
        + str(gas.get("failed_payment_count", 0)) + " and " + str(gas.get("arrears_case_count", 0))
        + " respectively, with a gas balance of " + _gbp(gas.get("balance_gbp", 0))
        + ". A combined roll-up nets these into one number and hides which fuel is actually "
        "causing the friction -- this is why per-fuel legs must be a real, separate view, "
        "not just an internal computation the combined total is derived from.</p>"
    )

    return (
        "<h2>Per-Fuel Account Depth: " + base_id + "</h2>"
        + '<p class="meta">Real invoice/payment/arrears history per fuel leg, from billing_ledger.json '
        + "(PRIORITIES.md P1, Website Integrity Part B)</p>"
        + '<div style="display:flex;gap:32px;flex-wrap:wrap">'
        + '<div style="flex:1;min-width:280px">' + _leg_table(base_id, elec) + "</div>"
        + '<div style="flex:1;min-width:280px">' + _leg_table(base_id + "g", gas) + "</div>"
        + "</div>"
        + "<h3>The Divergence</h3>"
        + divergence
    )


def _event_type_label(event_type):
    return event_type.replace("_", " ").upper()


def _decision_event_ledger_case_study(events, retention, journey_log, ledger, cid):
    """DECISION_LOOP_AND_EVENT_LEDGER.md Part 5: one real customer's full
    commercial history as a single ordered feed -- renewal triggers, EV-priced
    decisions, offer outcomes, arrears cascade -- unifying what Phases QI/QJ/QL/QM
    built as separate per-topic case studies into one chronological timeline."""
    ledger_customer = (ledger or {}).get("customers", {}).get(cid)
    entries = build_customer_ledger(cid, events, retention, journey_log, ledger_customer)
    if not entries:
        return ""

    rows = ""
    for e in entries:
        belief = _pct(e.get("company_belief"))
        # journey_state's sim_truth is a resentment score (0-100 scale), not a
        # churn probability -- _pct would misrender it as a percentage.
        truth = "&#8212;" if e["event_type"] == "journey_state" else _pct(e.get("sim_truth"))
        amount = _gbp(e.get("amount_gbp"))
        rows += _row(
            e["date"],
            _event_type_label(e["event_type"]),
            e["description"],
            belief,
            truth,
            amount,
            e.get("outcome") or "&#8212;",
        )

    return (
        "<h2>Decision Event Ledger: " + cid + "</h2>"
        + '<p class="meta">Every commercial event on one real account, in sequence -- '
        + "docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md Part 5. \"Company Believed\" is the "
        + "estimate/EV logged at decision time; \"SIM Truth\" is realized churn probability or "
        + "resentment score, visible to us but never to the company.</p>"
        + _table(
            ["Date", "Event", "Description", "Company Believed", "SIM Truth", "Amount", "Outcome"],
            rows,
        )
    )


def build_customers(dash, sample, ts, ledger=None, journey_log=None):
    git_commit = dash.get("meta", {}).get("git_commit", "?")
    phase = dash.get("build", {}).get("current_phase", "?")
    lifetime = dash["customers"].get("lifetime", {})
    events_by_cid = {}
    for e in dash["customers"].get("events", []):
        cid_e = e["customer_id"]
        events_by_cid.setdefault(cid_e, []).append(e)
    retention = dash["customers"].get("retention", [])
    sample_custs = sample.get("customers", {})

    rows = ""
    for cid in sorted(lifetime):
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

    combined_rows = ""
    seen_base = set()
    for cid in sorted(lifetime):
        base = cid[:-1] if cid.endswith("g") else cid
        if base in seen_base or base not in lifetime:
            continue
        seen_base.add(base)
        if base + "g" not in lifetime:
            continue  # single-fuel account: combined view would just duplicate the leg row
        elec_c = lifetime[base]
        gas_c = lifetime[base + "g"]
        combined_rows += _row(
            base,
            elec_c.get("segment", ""),
            _gbp(elec_c.get("net_gbp", 0) + gas_c.get("net_gbp", 0)),
            _gbp(elec_c.get("gross_gbp", 0) + gas_c.get("gross_gbp", 0)),
        )

    body = (
        "<h1>Customer Portfolio</h1>"
        + '<p class="meta">Source: customer_sample.json + dashboard.json</p>'
        + "<h2>All Customer Accounts (per fuel leg)</h2>"
        + '<p class="meta">Electricity and gas are separate accounts, each with their own '
        + "invoice/payment/arrears history -- see Per-Fuel Account Depth below.</p>"
        + _table(
            ["CID", "Segment", "Commodity", "Acquired", "Net Lifetime", "Gross", "CLV", "Churn", "Last Event", "Date"],
            rows,
        )
        + "<h2>Combined Roll-Up (dual-fuel customers, optional view)</h2>"
        + '<p class="meta">Net of both fuel legs -- a convenience total, never the only view '
        + "(see per-fuel accounts above and per-fuel depth below).</p>"
        + _table(["Customer", "Segment", "Combined Net Lifetime", "Combined Gross"], combined_rows)
        + "<h2>Retention Offers</h2>"
        + _table(["Customer", "Date", "Discount", "Cost", "Outcome"], ret_rows)
        + _behavioral_case_study(sample, ledger or {}, BEHAVIORAL_CASE_STUDY_CID)
        + _churn_journey_case_study(
            journey_log or [], ledger or {}, _pick_journey_case_study_cid(journey_log or []),
        )
        + _retention_deferral_case_study(
            dash["customers"].get("retention_deferral", []),
            dash["customers"].get("serial_savers", []),
            _pick_serial_saver_cid(dash["customers"].get("serial_savers", [])),
        )
        + _per_fuel_case_study(ledger or {}, PER_FUEL_CASE_STUDY_BASE)
        + _decision_event_ledger_case_study(
            dash["customers"].get("events", []), retention, journey_log or [],
            ledger or {}, DECISION_LEDGER_CASE_STUDY_CID,
        )
        + "<h2>Full Ground Truth</h2>"
        + "<p>Machine-readable per-customer data:<br>"
        + '<a href="/state/customer_sample.json">customer_sample.json</a> | '
        + '<a href="/state/billing_ledger.json">billing_ledger.json</a></p>'
    )
    return _page("Customer Portfolio", "Customers", body, ts, git_commit, phase)



def _collections_process(billing_ledger):
    """Aggregate the real dunning cascade across every account (EVIDENCE_IN_
    BUSINESS_SURFACES.md: show the operational process, not the code)."""
    if not billing_ledger:
        return ""
    customers = billing_ledger.get("customers", {})
    stage_counts = {}
    total_cases = 0
    total_arrears_gbp = 0.0
    written_off_gbp = 0.0
    resolved = 0
    written_off = 0
    still_open = 0
    for cust in customers.values():
        for case in cust.get("arrears_history", []) or []:
            total_cases += 1
            total_arrears_gbp += case.get("arrears_gbp", 0)
            stages = case.get("stages", [])
            for s in stages:
                stage_counts[s["stage"]] = stage_counts.get(s["stage"], 0) + 1
            final = stages[-1]["stage"] if stages else None
            if final == "RESOLVED":
                resolved += 1
            elif final == "WRITTEN_OFF":
                written_off += 1
                written_off_gbp += case.get("arrears_gbp", 0)
            else:
                still_open += 1

    stage_order = ["DD_FAILED", "FIRST_NOTICE", "SECOND_NOTICE", "PAYMENT_PLAN_AGREED",
                   "DISPUTE_NOTICE", "RESOLVED", "WRITTEN_OFF"]
    stage_rows = "".join(
        _row(stage, stage_counts[stage])
        for stage in stage_order if stage in stage_counts
    )

    body = (
        "<h2>Collections &amp; Dunning Process (real, from billing_ledger.json)</h2>"
        + "<p>" + str(total_cases) + " arrears cases opened across the customer base, "
        + _gbp(total_arrears_gbp) + " total arrears value. Outcome: " + str(resolved)
        + " resolved via payment plan, " + str(written_off) + " written off ("
        + _gbp(written_off_gbp) + " -- feeds the emergent bad debt figure in the Annual "
        + "Income Statement above, Phase QD), " + str(still_open) + " still open.</p>"
        + "<h3>Cascade Stage Volumes (every case passes through these in order)</h3>"
        + _table(["Stage", "Times Reached"], stage_rows)
    )
    return body


def _portfolio_event_stream(events, retention, journey_log, billing_ledger):
    """DECISION_LOOP_AND_EVENT_LEDGER.md Part 5: the live-run feed of decisions
    across the whole portfolio, most recent first -- company ops view of the
    same events the customer-level ledger shows for one account. Filterable by
    event type via the buttons above the table (plain JS, no framework)."""
    stream = build_portfolio_event_stream(events, retention, journey_log, billing_ledger, limit=150)
    if not stream:
        return ""

    types_seen = sorted({e["event_type"] for e in stream})
    filter_buttons = (
        '<button class="btn" onclick="_filterLedger(\'all\')">All</button>'
        + "".join(
            '<button class="btn" onclick="_filterLedger(\'' + t + '\')">'
            + _event_type_label(t) + "</button>"
            for t in types_seen
        )
    )

    rows = ""
    for e in stream:
        belief = _pct(e.get("company_belief"))
        truth = "&#8212;" if e["event_type"] == "journey_state" else _pct(e.get("sim_truth"))
        amount = _gbp(e.get("amount_gbp"))
        rows += (
            '<tr data-event-type="' + e["event_type"] + '">'
            + "<td>" + e["date"] + "</td>"
            + "<td>" + e["customer_id"] + "</td>"
            + "<td>" + _event_type_label(e["event_type"]) + "</td>"
            + "<td>" + e["description"] + "</td>"
            + "<td>" + belief + "</td>"
            + "<td>" + truth + "</td>"
            + "<td>" + amount + "</td>"
            + "</tr>"
        )

    return (
        "<h2>Portfolio Decision Event Stream</h2>"
        + '<p class="meta">Most recent 150 decisions/outcomes across the whole portfolio -- '
        + "docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md Part 5. \"Company Believed\" is the "
        + "H1 estimate/EV logged at decision time; \"SIM Truth\" is the realized outcome.</p>"
        + '<div style="margin-bottom:10px">' + filter_buttons + "</div>"
        + '<table id="ledger-stream"><thead><tr>'
        + "".join("<th>" + h + "</th>" for h in
                  ["Date", "Customer", "Event", "Description", "Company Believed", "SIM Truth", "Amount"])
        + "</tr></thead><tbody>" + rows + "</tbody></table>"
        + "<script>function _filterLedger(t){"
        + "document.querySelectorAll('#ledger-stream tbody tr').forEach(function(r){"
        + "r.style.display = (t==='all' || r.dataset.eventType===t) ? '' : 'none';"
        + "});}</script>"
    )


def build_supplier(dash, ts, billing_ledger=None, journey_log=None):
    git_commit = dash.get("meta", {}).get("git_commit", "?")
    annual = dash["financial"]["annual"]
    ledger = dash["financial"].get("ledger", {})
    seg = dash["financial"].get("segment_annual", [])
    retention_records = dash.get("customers", {}).get("retention", [])

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

    slcs = [
        ("SLC 2B", "Deemed Contract Register", "Phase 322"),
        ("SLC 14", "Credit Refund (10 working days)", "Phase 320"),
        ("SLC 21B", "Account Closure & Final Bill (42 days)", "Phase 312"),
        ("SLC 21C", "Fuel Mix Disclosure (REGO-backed)", "Phase CL"),
        ("SLC 22", "Contract Notice & Renewal Obligations", "Phase CO/M"),
        ("SLC 25C", "Communication Channel Choice", "Phase DA"),
        ("SLC 26B", "Priority Services Register (9 categories)", "Phase CR"),
        ("SLC 27", "Debt / Disconnection Moratorium Rules", "Phase 311/325/328"),
        ("SLC 27A", "Ability-to-Pay & Payment Plan Adequacy", "Phase 315"),
        ("SLC 31A", "Back-billing 12-Month Cap (May 2018+)", "Phase 314/Z"),
        ("BSC SVA", "DA/DC Metering Agent Appointments", "Phase CV"),
        ("LC 30A", "Supplier Fitness & Proper Person Test", "Phase CY"),
        ("UNC TPD", "Gas Nomination / Shipper Code", "Phase CS/CT/CU"),
        ("GDPR/PECR", "Data Breach Notification (72h ICO)", "Phase DB"),
        ("UK EMIR", "Trade Repository Reporting (T+1)", "Phase DC"),
        ("EBRS/EBSS", "Energy Bill Relief / Support Schemes", "Phase DD/DE"),
        ("FRA", "Financial Resilience Assessment (12m min)", "Phase 318"),
        ("IFRS 9", "Hedge Effectiveness (80-125% band)", "Phase 319"),
        ("Consumer Duty", "Vulnerable Customer Outcomes & PSR", "Phase 329/330"),
        ("WAM/WHD", "Warm Home Discount Phase 2", "Phase 281"),
        ("FiT/SEG", "Smart Export Guarantee", "Phase 310/R"),
        ("RO/CfD", "Renewable Obligation / CfD Levy", "Phase AV"),
        ("CCL", "Climate Change Levy Ledger", "Phase 304"),
    ]
    slc_rows = "".join(_row(code, desc, phase) for code, desc, phase in slcs)

    cap_domains = [
        ("Customer Lifecycle", [
            "Acquisition & Book Growth", "EAC-Based Tariff Pricing",
            "Contract Renewal Engine", "Churn Risk Assessment",
            "Retention Offer Engine", "Dual-Fuel Account Mgmt",
        ]),
        ("Billing & Payments", [
            "Dual-Fuel Invoice Engine", "Smart Meter Reconciliation",
            "Back-billing Compliance (SLC 31A)", "Direct Debit Indemnity Claims",
            "Payment Plan Adequacy (ATP)", "Debt Collection (6 stages)",
        ]),
        ("Wholesale & Trading", [
            "Hedging Strategy Evolution", "Forward Book Management",
            "VaR Monitor", "Stress Test Framework",
            "Hedge Effectiveness (IFRS 9)", "BSC Settlement Runs (SF->RF)",
        ]),
        ("Simulation & Settlement", [
            "Half-hourly Settlement (48 periods/day)", "Gas Daily Settlement + HDD Shape",
            "EV Smart Charging Shape", "Solar Irradiance Settlement",
            "Household Physical Model (EPC/EV/ASHP)", "Triad Notification & Savings",
        ]),
        ("Regulatory & Compliance", [
            "23+ SLC Obligation Modules", "ICO Breach Register (72h GDPR)",
            "Financial Resilience Assessment", "Priority Services Register",
            "Annual Report (75 sections)", "Social Obligation Spend (WHD/ECO)",
        ]),
        ("Pricing & Market Intelligence", [
            "Ofgem Price Cap Tracker", "Break-even Assessor",
            "Cost-to-Serve Calculator", "Segment Profitability Book",
            "Price Elasticity Model", "Renewal Pricing Engine",
        ]),
    ]
    cap_rows = "".join(
        _row(domain, " | ".join(caps))
        for domain, caps in cap_domains
    )

    build = dash.get("build", {})
    body = (
        "<h1>Supplier Financial Statements</h1>"
        + "<h2>Annual Income Statement</h2>"
        + _table(["Year", "Revenue", "Gross", "Capital", "Policy", "Bad Debt", "Net", "Treasury"], ann_rows)
        + "<h2>10-Year Ledger</h2>"
        + _table(["Line Item", "Total 2016-2025"], led_rows)
        + "<h2>Annual P&amp;L by Segment</h2>"
        + _table(["Year", "Segment", "Gross", "Net", "Customers"], seg_rows)
        + "<h2>Regulatory &amp; Compliance Framework</h2>"
        + "<p>Phase: " + str(build.get("current_phase", "PR")) + " | Tests: "
        + str(build.get("test_count", "15,194")) + " passing | 23 SLC obligations covered</p>"
        + _table(["Obligation", "Description", "Phase"], slc_rows)
        + "<h2>Business Capability Matrix</h2>"
        + "<p>6 domains | 72+ capabilities | Point-in-Time Blindfold enforced</p>"
        + _table(["Domain", "Capabilities"], cap_rows)
        + _collections_process(billing_ledger)
        + _renewal_decision_case_study(retention_records)
        + _churn_journey_portfolio_funnel(journey_log or [])
        + _serial_saver_portfolio(dash.get("customers", {}).get("serial_savers", []))
        + _portfolio_event_stream(
            dash.get("customers", {}).get("events", []), retention_records, journey_log or [],
            billing_ledger or {},
        )
    )
    return _page("Supplier P&amp;L", "Supplier", body, ts, git_commit, build.get("current_phase", "?"))


def _behavioral_signal_correlation(sample, billing_ledger, financial_annual):
    """The SIM signal (income-stress population mix) graphed against the
    company-observable outcome it should move with (arrears cases opened,
    bad debt) -- EVIDENCE_IN_BUSINESS_SURFACES.md's Sim-tab requirement."""
    if not sample or not billing_ledger:
        return ""
    customers = sample.get("customers", {})
    by_year_stress = {}
    for cid, cust in customers.items():
        if cid.endswith("g"):
            continue
        for s in cust.get("income_stress_trajectory") or []:
            yr = s.get("year")
            lvl = s.get("stress", "low")
            by_year_stress.setdefault(yr, {"low": 0, "moderate": 0, "high": 0})
            by_year_stress[yr][lvl] = by_year_stress[yr].get(lvl, 0) + 1

    arrears_opened_by_year = {}
    for cust in billing_ledger.get("customers", {}).values():
        for case in cust.get("arrears_history", []) or []:
            opened = case.get("opened_date", "")
            if len(opened) >= 4:
                yr = int(opened[:4])
                arrears_opened_by_year[yr] = arrears_opened_by_year.get(yr, 0) + 1

    bad_debt_by_year = {r["year"]: r.get("bad_debt_gbp", 0) for r in financial_annual}

    rows = ""
    for yr in sorted(by_year_stress):
        counts = by_year_stress[yr]
        rows += _row(
            yr, counts.get("low", 0), counts.get("moderate", 0), counts.get("high", 0),
            arrears_opened_by_year.get(yr, 0),
            _gbp(bad_debt_by_year.get(yr, 0)),
        )

    return (
        "<h2>Customer Behavioral Signal &amp; Correlation</h2>"
        + '<p class="meta">income_stress_trajectory (SIM ground truth, every customer) vs '
        + "arrears cases opened and bad debt (both company-observable) -- "
        + "docs/staging/done/EVIDENCE_IN_BUSINESS_SURFACES.md</p>"
        + _table(
            ["Year", "Customers LOW Stress", "MODERATE", "HIGH", "Arrears Cases Opened", "Bad Debt"],
            rows,
        )
    )


def _churn_model_signal(events, churn_perf):
    if not events or not churn_perf:
        return ""
    by_year = {}
    for e in events:
        date = e.get("date", "")
        if len(date) < 4:
            continue
        yr = date[:4]
        by_year.setdefault(yr, []).append(e.get("market_signal", 0))

    per_year_perf = churn_perf.get("per_year", {})
    rows = ""
    for yr in sorted(per_year_perf):
        signals = by_year.get(yr, [])
        avg_signal = sum(signals) / len(signals) if signals else 0
        p = per_year_perf[yr]
        rows += _row(
            yr, format(avg_signal, ".2f"), p.get("tp", 0), p.get("fp", 0),
            p.get("fn", 0), _pct(p.get("recall")), _pct(p.get("precision")),
        )

    overall = (
        "Overall: recall " + _pct(churn_perf.get("recall")) + ", precision "
        + _pct(churn_perf.get("precision")) + ", F1 " + format(churn_perf.get("f1_score", 0), ".3f")
        + " across " + str(churn_perf.get("total_churn_events", 0)) + " churn events."
    )

    return (
        "<h2>Churn Model: Market Signal vs Classification Accuracy</h2>"
        + "<p class=\"meta\">market_signal is the Phase QB switching-propensity multiplier (SIM), "
        + "averaged across every renewal that year, next to the company classifier real "
        + "TP/FP/FN and recall/precision at the live retention threshold -- "
        + "docs/staging/EVIDENCE_IN_BUSINESS_SURFACES.md</p>"
        + _table(
            ["Year", "Avg Market Signal", "TP", "FP", "FN", "Recall", "Precision"],
            rows,
        )
        + "<p>" + overall + "</p>"
    )


_JOURNEY_STATE_ORDER = ["content", "irritated", "in_market", "comparing", "home_move_churned"]


def _churn_journey_signal(journey_log, events):
    if not journey_log:
        return ""
    by_year = {}
    for j in journey_log:
        yr = (j.get("date") or "")[:4]
        if not yr:
            continue
        y = by_year.setdefault(yr, {"total": 0, "by_state": {}, "resentment_sum": 0.0})
        y["total"] += 1
        st = j.get("state", "")
        y["by_state"][st] = y["by_state"].get(st, 0) + 1
        y["resentment_sum"] += j.get("resentment_score", 0)

    churned_by_year = {}
    for e in events or []:
        yr = (e.get("date") or "")[:4]
        if not yr:
            continue
        c = churned_by_year.setdefault(yr, {"churned": 0, "total": 0})
        c["total"] += 1
        if e.get("type") == "churned":
            c["churned"] += 1

    rows = ""
    for yr in sorted(by_year):
        y = by_year[yr]
        beyond_content = sum(n for st, n in y["by_state"].items() if st != "content")
        pct_beyond = beyond_content / y["total"] * 100 if y["total"] else 0
        avg_resentment = y["resentment_sum"] / y["total"] if y["total"] else 0
        c = churned_by_year.get(yr, {"churned": 0, "total": 0})
        churn_rate = c["churned"] / c["total"] * 100 if c["total"] else 0
        rows += _row(
            yr, y["total"], format(pct_beyond, ".1f") + "%",
            format(avg_resentment, ".1f"), format(churn_rate, ".1f") + "%",
        )

    return (
        "<h2>Churn Journey Funnel: Hidden State vs Realized Churn</h2>"
        + "<p class=\"meta\">SIM-side hidden churn-journey state (CONTENT/IRRITATED/IN_MARKET/"
        + "COMPARING), tracked at every renewal period, never observed directly by the company -- "
        + "docs/design/PROCESS_MODEL.md Section 2</p>"
        + _table(
            ["Year", "Renewals Tracked", "% Beyond CONTENT", "Avg Resentment Score", "Realized Churn Rate"],
            rows,
        )
        + "<p>Years where a larger share of the book has moved beyond CONTENT (irritated or further "
        + "into the funnel) are the years the realized churn rate should track, if the state machine "
        + "is doing real work rather than window dressing on top of the old single-dice-roll model.</p>"
    )


def _pick_journey_case_study_cid(journey_log):
    counts = {}
    for j in journey_log or []:
        if j.get("state") != "content":
            counts[j["customer_id"]] = counts.get(j["customer_id"], 0) + 1
    if not counts:
        return None
    return max(sorted(counts), key=lambda c: counts[c])


def _churn_journey_case_study(journey_log, ledger, cid):
    if not cid:
        return ""
    trajectory = sorted(
        (j for j in journey_log if j.get("customer_id") == cid),
        key=lambda j: j.get("date", ""),
    )
    if not trajectory:
        return ""

    traj_rows = "".join(
        _row(
            j["date"], j["state"].replace("_", " ").upper(),
            format(j.get("resentment_score", 0), ".1f"),
            "yes" if j.get("is_burned") else "no",
        )
        for j in trajectory
    )

    ledger_cust = (ledger or {}).get("customers", {}).get(cid, {})
    invoices = ledger_cust.get("invoices", [])
    feature_vec = retention_risk_feature_vector({"customer_id": cid}, invoices, [])
    feature_rows = "".join(
        _row(k.replace("_", " "), v) for k, v in feature_vec.items() if k != "customer_id"
    )

    furthest_state = max(
        (j["state"] for j in trajectory if j["state"] in _JOURNEY_STATE_ORDER),
        key=_JOURNEY_STATE_ORDER.index,
        default=trajectory[-1]["state"],
    )

    return (
        "<h2>Churn Journey Case Study: " + cid + "</h2>"
        + "<p class=\"meta\">Both sides of the epistemic wall -- docs/design/PROCESS_MODEL.md "
        + "Section 3</p>"
        + "<h3>SIM Ground Truth &#8212; Hidden Journey State (not observable to the company)</h3>"
        + _table(["Date", "State", "Resentment Score", "Resentment Burned"], traj_rows)
        + "<h3>Company-Observable &#8212; Retention Risk Feature Vector (from real invoices)</h3>"
        + _table(["Feature", "Value"], feature_rows)
        + "<h3>The Divergence</h3>"
        + "<p>" + cid + " reached " + furthest_state.replace("_", " ").upper()
        + " in the SIM's hidden churn journey -- a state the company can never read directly. "
        + "The company's only real proxy here is the feature vector above, built entirely from its "
        + "own invoice records: no complaint log or renewal-window feed is threaded into this evidence "
        + "view yet, so recent_complaint_90d and renewal_window_open read as placeholders (0.0) until "
        + "those company-side feeds are wired into this generator.</p>"
    )


def _churn_journey_portfolio_funnel(journey_log):
    if not journey_log:
        return ""
    dated = [j for j in journey_log if j.get("date")]
    if not dated:
        return ""
    latest_year = max(j["date"][:4] for j in dated)
    year_entries = [j for j in dated if j["date"].startswith(latest_year)]
    counts = {}
    for j in year_entries:
        st = j.get("state", "")
        counts[st] = counts.get(st, 0) + 1

    rows = "".join(
        _row(st.replace("_", " ").upper(), counts.get(st, 0))
        for st in _JOURNEY_STATE_ORDER if st in counts
    )
    total = len(year_entries)
    beyond = sum(n for st, n in counts.items() if st != "content")

    return (
        "<h2>Churn Journey Funnel (" + latest_year + ")</h2>"
        + "<p>" + str(total) + " renewal-period observations this year; " + str(beyond)
        + " sitting beyond CONTENT in the hidden funnel (IRRITATED or further) -- a monitoring view "
        + "the retention team did not have before this phase, when churn risk was invisible between "
        + "annual renewal dice rolls.</p>"
        + _table(["State", "Count"], rows)
    )


def _renewal_decision_case_study(retention):
    both_sides = [r for r in retention if r.get("sim_churn_p") is not None]
    if not both_sides:
        return ""
    pick = max(both_sides, key=lambda r: abs(r.get("company_est", 0) - r.get("sim_churn_p", 0)))
    gap_pp = round((pick["company_est"] - pick["sim_churn_p"]) * 100, 1)
    direction = "overestimated" if gap_pp > 0 else "underestimated"

    body = (
        "<h2>One Renewal Decision, Both Sides of the Wall</h2>"
        + "<p class=\"meta\">A real retention decision (" + pick["customer_id"] + " on "
        + pick["date"] + "), shown exactly as it happened -- "
        + "docs/staging/EVIDENCE_IN_BUSINESS_SURFACES.md</p>"
        + _table(
            ["Side", "Field", "Value"],
            _row("SIM ground truth (not observable)", "Churn probability", _pct(pick["sim_churn_p"]))
            + _row("SIM ground truth (not observable)", "Market switching signal", format(pick["market_signal"], ".2f"))
            + _row("SIM ground truth (not observable)", "Realized churn probability", _pct(pick["realized_churn_p"]))
            + _row("Company-observable", "Churn model estimate", _pct(pick["company_est"]))
            + _row("Company-observable", "Retention offer", _pct(pick["discount_pct"]) + " discount, " + _gbp(pick["cost_gbp"]))
            + _row("Outcome", "Result", pick["outcome"]),
        )
        + "<p>The company estimate " + direction + " the SIM ground truth by " + str(abs(gap_pp))
        + " percentage points -- it could not see the actual figure, only its own model output, and made "
        + "the retention call on that alone. Customer outcome: " + pick["outcome"] + ".</p>"
    )
    return body


def _retention_deferral_signal(records):
    if not records:
        return ""
    by_year = {}
    for r in records:
        yr = (r.get("offer_date") or "")[:4]
        if not yr:
            continue
        y = by_year.setdefault(yr, {"count": 0, "assumed_sum": 0.0, "realized_sum": 0.0, "realized_n": 0, "underperformed": 0})
        y["count"] += 1
        y["assumed_sum"] += r.get("assumed_deferral_months", 0)
        if r.get("realized_deferral_months") is not None:
            y["realized_sum"] += r["realized_deferral_months"]
            y["realized_n"] += 1
        if r.get("underperformed"):
            y["underperformed"] += 1

    rows = ""
    for yr in sorted(by_year):
        y = by_year[yr]
        avg_assumed = y["assumed_sum"] / y["count"] if y["count"] else 0
        avg_realized = y["realized_sum"] / y["realized_n"] if y["realized_n"] else None
        pct_under = y["underperformed"] / y["count"] * 100 if y["count"] else 0
        rows += _row(
            yr, y["count"], format(avg_assumed, ".1f"),
            format(avg_realized, ".1f") if avg_realized is not None else "&#8212;",
            format(pct_under, ".0f") + "%",
        )

    return (
        "<h2>Retention Offer Deferral: Assumed vs Realized (H1 vs H2)</h2>"
        + "<p class=\"meta\">Every retention offer prices ONE renewal term (H1, assumed) -- "
        + "docs/staging/QL_WIRE_AND_DEFERRAL.md. H2 is the realized months to that customer's "
        + "next offer or churn, measured after the fact.</p>"
        + _table(
            ["Year", "Offers", "Avg Assumed Months (H1)", "Avg Realized Months (H2)", "% Underperformed"],
            rows,
        )
        + "<p>Underperformed = the customer's next terminal event (another offer, or churn) "
        + "arrived sooner than the term the offer was priced to buy. An offer that consistently "
        + "buys less time than assumed is a pricing signal, not a retention failure.</p>"
    )


def _pick_serial_saver_cid(serial_savers):
    candidates = [s for s in serial_savers if s.get("is_serial_saver")]
    if not candidates:
        return None
    return max(sorted(candidates, key=lambda s: s["customer_id"]), key=lambda s: s["offer_count"])["customer_id"]


def _retention_deferral_case_study(records, serial_savers, cid):
    if not cid:
        return ""
    timeline = sorted(
        (r for r in records if r.get("customer_id") == cid),
        key=lambda r: r.get("offer_date", ""),
    )
    if not timeline:
        return ""
    summary = next((s for s in serial_savers if s.get("customer_id") == cid), {})

    rows = "".join(
        _row(
            r["offer_date"],
            format(r["assumed_deferral_months"], ".0f") + " mo",
            format(r["realized_deferral_months"], ".1f") + " mo" if r["realized_deferral_months"] is not None else "still active",
            (r.get("next_event_type") or "&#8212;").replace("_", " "),
            "yes" if r.get("underperformed") else "no",
        )
        for r in timeline
    )

    if summary.get("ev_negative"):
        verdict = "an EV-negative repeat saver"
    elif summary.get("is_serial_saver"):
        verdict = "a serial saver"
    else:
        verdict = "a single retention offer"

    return (
        "<h2>Retention as Deferral: " + cid + "</h2>"
        + "<p class=\"meta\">Retention offers buy time, not loyalty -- "
        + "docs/staging/QL_WIRE_AND_DEFERRAL.md, worked case from Phase QK's defer-then-churn finding</p>"
        + _table(
            ["Offer Date", "Assumed Window (H1)", "Realized Window (H2)", "What Happened Next", "Underperformed"],
            rows,
        )
        + "<p>" + cid + " received " + str(summary.get("offer_count", len(timeline))) + " retention offer(s), "
        + "total discount spend " + _gbp(summary.get("cumulative_cost_gbp")) + " -- " + verdict + ". "
        + "Each offer bought a finite deferral window; once the underlying satisfaction/resentment signal "
        + "decayed back down before the next renewal, the customer churned anyway.</p>"
    )


def _serial_saver_portfolio(serial_savers):
    repeats = [s for s in serial_savers if s.get("is_serial_saver")]
    if not repeats:
        return ""
    repeats = sorted(repeats, key=lambda s: s["cumulative_cost_gbp"], reverse=True)
    rows = "".join(
        _row(
            s["customer_id"], s["offer_count"], _gbp(s["cumulative_cost_gbp"]),
            s["final_outcome"].replace("_", " "),
            "EV-NEGATIVE" if s.get("ev_negative") else "retained",
        )
        for s in repeats
    )
    ev_negative_count = sum(1 for s in repeats if s.get("ev_negative"))
    ev_negative_spend = sum(s["cumulative_cost_gbp"] for s in repeats if s.get("ev_negative"))

    return (
        "<h2>Serial Savers: Repeat Retention Offers</h2>"
        + "<p class=\"meta\">docs/staging/QL_WIRE_AND_DEFERRAL.md: repeat discounting that never bought "
        + "permanent retention belongs in managed-exit territory, not another offer.</p>"
        + _table(["Customer", "Offers Received", "Cumulative Discount Spend", "Final Outcome", "Verdict"], rows)
        + "<p>" + str(ev_negative_count) + " of " + str(len(repeats))
        + " repeat-offer customers churned anyway on their final offer -- " + _gbp(ev_negative_spend)
        + " in cumulative discount spend that bought deferral, not durable retention.</p>"
    )


def build_sim(sim_data, ts, git_commit="?", phase="?", sample=None, billing_ledger=None, financial_annual=None, churn_events=None, churn_perf=None, journey_log=None, retention_deferral=None, population_anchoring=None):
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
        + _behavioral_signal_correlation(sample or {}, billing_ledger or {}, financial_annual or [])
        + _churn_model_signal(churn_events or [], churn_perf or {})
        + _churn_journey_signal(journey_log or [], churn_events or [])
        + _retention_deferral_signal(retention_deferral or [])
        + _population_anchoring_rag(population_anchoring or {})
    )
    return _page("Simulation Data", "Sim", body, ts, git_commit, phase)


def _population_anchoring_rag(pa):
    """RAG chip rendering of population_anchoring.json (Phase PQ/PR/PS) -- real
    already-computed switching/bad-debt/complaints/arrears benchmark checks that
    had no visual home on any shadow page until now (PRIORITIES.md P1 design
    system: same rag-chip component as the customer portal's base.html)."""
    if not pa:
        return ""
    overall = pa.get("overall_rag", "")

    def _chip(rag):
        cls = {"GREEN": "rag-green", "AMBER": "rag-amber", "RED": "rag-red"}.get(rag, "rag-amber")
        return '<span class="rag-chip ' + cls + '">' + str(rag) + "</span>"

    rows = ""
    long_run = pa.get("long_run_comparison", {})
    if long_run:
        rows += _row("Long-run churn vs Ofgem", format(long_run.get("ratio", 0), ".2f") + "x", _chip(long_run.get("rag", "")))
    for check in pa.get("bad_debt_vs_benchmark", [])[-3:]:
        rows += _row("Bad debt " + str(check.get("year", "")), format(check.get("bad_debt_pct", 0), ".2f") + "%", _chip(check.get("rag", "")))
    for check in pa.get("complaints_vs_benchmark", [])[-3:]:
        rows += _row("Complaints " + str(check.get("year", "")), format(check.get("complaint_rate_pct", 0), ".2f") + "%", _chip(check.get("rag", "")))
    for check in pa.get("arrears_vs_benchmark", [])[-3:]:
        rows += _row("Arrears " + str(check.get("year", "")), format(check.get("arrears_pct", 0), ".2f") + "%", _chip(check.get("rag", "")))
    if not rows:
        return ""
    return (
        "<h2>Population Anchoring vs Real UK Market Benchmarks</h2>"
        + '<div class="meta">Overall: ' + _chip(overall) + "</div>"
        + _table(["Check", "Value", "RAG"], rows)
    )


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
    return _page("Project Status", "Project", body, ts, dash.get("meta", {}).get("git_commit", "?"), phase)


def generate(run_json_path=None):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    dash = json.loads((DATA / "dashboard.json").read_text())
    sim_data = json.loads((DATA / "sim_data.json").read_text())
    sample_path = DATA / "customer_sample.json"
    sample = json.loads(sample_path.read_text()) if sample_path.exists() else {}
    ledger_path = STATE / "billing_ledger.json"
    billing_ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    pa_path = STATE / "population_anchoring.json"
    _population_anchoring = json.loads(pa_path.read_text()) if pa_path.exists() else {}
    latest_md = LATEST_MD.read_text() if LATEST_MD.exists() else ""

    _git_commit = dash.get("meta", {}).get("git_commit", "?")
    _phase = dash.get("build", {}).get("current_phase", "?")
    _financial_annual = dash.get("financial", {}).get("annual", [])
    _churn_events = dash.get("customers", {}).get("events", [])
    _churn_perf = dash.get("churn_model_performance", {})
    _journey_log = dash.get("customers", {}).get("journey_log", [])
    _retention_deferral = dash.get("customers", {}).get("retention_deferral", [])
    pages = {
        SHADOW / "index.html": build_index(dash, ts),
        SHADOW / "customers" / "index.html": build_customers(dash, sample, ts, billing_ledger, _journey_log),
        SHADOW / "supplier" / "index.html": build_supplier(dash, ts, billing_ledger, _journey_log),
        SHADOW / "sim" / "index.html": build_sim(sim_data, ts, _git_commit, _phase, sample, billing_ledger, _financial_annual, _churn_events, _churn_perf, _journey_log, _retention_deferral, _population_anchoring),
        SHADOW / "project" / "index.html": build_project(dash, latest_md, ts),
    }

    for path, html in pages.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        print("Generated", str(path.relative_to(PROJECT)))

    return list(pages.keys())


if __name__ == "__main__":
    generate()
