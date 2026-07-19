#!/usr/bin/env python3
"""Generate site/data/saas_coverage.json -- the SaaS Estate Coverage Map data source.

SAAS_COVERAGE_MAP.md: of the ~20+ SaaS categories a real UK energy supplier
assembles to run its business, how much does Poesys's architecture eliminate
outright (A), recreate natively (B), or still need to interface with as a
real-world boundary (C). Category table content lives here (external market
category -> Poesys module mapping is not something the filesystem can derive
on its own); the headline percentage breakdown and each B/C entry's
file-existence check ARE computed fresh at generation time, so a claimed
mapping can never silently drift stale without a test catching it -- same
discipline as the ADAPTER_REGISTRY pattern (platform page retired 2026-07-19).
"""
import json
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parent.parent
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"
OUT_PATH = PROJECT / "site" / "data" / "saas_coverage.json"


def _get(d, *path):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


CATEGORIES = [
    dict(category="Retail core / CIS (billing, contracts, meter points)",
         market_leaders="Kraken (Octopus), ENSEK, Gentrack",
         modules=["company/billing"], bucket="B",
         note="54+ modules: invoice, contract, meter_points, direct_debit, dual_fuel_bill"),
    dict(category="ETRM / CTRM (trading, hedging, risk)",
         market_leaders="Brady, EnergyOne (Allegro), ION",
         modules=["company/trading", "company/risk", "sim/hedging.py", "sim/risk_committee.py"],
         bucket="B", note="spans retail AND trading, which no vendor does"),
    dict(category="Finance / ERP core",
         market_leaders="NetSuite, SAP, Oracle Fusion",
         modules=["company/finance/double_entry.py", "saas/ledger.py"], bucket="B", note=""),
    dict(category="Collections / arrears workflow",
         market_leaders="Aryza, in-house DCA tooling",
         modules=["simulation/arrears_engine.py", "company/billing/collections.py",
                  "company/billing/debt_referral.py"], bucket="B", note=""),
    dict(category="CX / engagement decisioning",
         market_leaders="Braze, Salesforce Marketing Cloud",
         modules=["saas/contact_model.py", "company/crm", "company/policy/decision_policy.py"],
         bucket="B", note=""),
    dict(category="Regulatory compliance stack",
         market_leaders="Gentrack Regulatory, bespoke in-house",
         modules=["company/regulatory", "company/compliance"], bucket="B",
         note="62 wired schemes, Phase OL"),
    dict(category="ESG / carbon reporting",
         market_leaders="Position Green, Workiva, Diligent ESG",
         modules=["company/sustainability", "company/billing/carbon_footprint.py"], bucket="B", note=""),
    dict(category="Demand response / flexibility",
         market_leaders="Kaluza Flex, Limejump",
         modules=["saas/demand_response.py"], bucket="B", note=""),
    dict(category="Nudge / behavioural engagement physics",
         market_leaders="Opower (social norms), in-house",
         modules=["simulation/nudge_physics.py", "company/analytics/nudge_discovery.py"], bucket="B",
         note="Phase RV"),
    dict(category="ITSM / observability",
         market_leaders="ServiceNow, Datadog, PagerDuty",
         modules=["background/session_watchdog.py", "background/health_check.py"], bucket="B", note=""),
    dict(category="Customer Data Platform (CDP)",
         market_leaders="Segment, Braze CDP, Tealium",
         modules=[], bucket="A",
         note="single event-native data model (site/data/*.json) replaces the stitching problem a CDP solves"),
    dict(category="iPaaS / integration middleware",
         market_leaders="MuleSoft, Boomi, Workato",
         modules=[], bucket="A", note="one codebase, direct module imports, no point-to-point integration surface"),
    dict(category="Process mining",
         market_leaders="Celonis",
         modules=["company/analytics/decision_event_ledger.py"], bucket="A",
         note="native real-time process visibility; nothing to mine after the fact"),
    dict(category="Energy margin analytics / margin intelligence",
         market_leaders="Gorilla Energy (\"Energy Margin Intelligence\")",
         modules=["saas/cost_to_serve.py"], bucket="A",
         note="margin-truth is a property of every decision, not a bolt-on analytics layer"),
    dict(category="BI / data warehouse",
         market_leaders="Snowflake, dbt Labs, Looker/Power BI",
         modules=["tools/generate_dashboard_data.py"], bucket="A",
         note="board-grade analytics computed directly off the operational data model, no separate warehouse/ETL"),
    dict(category="Credit bureau / KYC",
         market_leaders="Experian, Equifax, TransUnion",
         modules=["tools/credit_bureau_port.py"], bucket="C",
         note="LIVE epistemic-boundary adapter, Phase QR"),
    dict(category="Payment service provider (PSP)",
         market_leaders="Stripe, GoCardless, Worldpay",
         modules=[], bucket="C",
         note="adapter PLANNED -- payment behaviour currently modelled directly, not yet via a swappable PSP boundary"),
    dict(category="Smart meter comms (DCC)",
         market_leaders="DCC, Landis+Gyr, Siemens",
         modules=[], bucket="C",
         note="adapter PLANNED -- HH smart-meter data generated directly, not read through a DCC-shaped boundary"),
    dict(category="Market messaging (DTS/DIP)",
         market_leaders="ElectraLink",
         modules=[], bucket="C",
         note="settlement/registration data flows directly from Elexon ingestion, no DTS-shaped boundary modelled"),
    dict(category="Message delivery (email/SMS/post)",
         market_leaders="Twilio, SendGrid, Royal Mail Mailmark",
         modules=[], bucket="C",
         note="comms are logged as decision events, not dispatched through a real delivery rail"),
    dict(category="Debt sale / DCA placement",
         market_leaders="Lowell, Cabot, DCA panels",
         modules=["simulation/arrears_engine.py"], bucket="C",
         note="write-off is the current terminal state; placement/sale economics are backlog"),
    dict(category="Property / EPC data",
         market_leaders="GOV.UK EPC register, Rightmove",
         modules=[], bucket="C",
         note="not yet wired -- backlog (EPC-calibrated consumption distributions)"),
]


def _module_exists(rel):
    p = PROJECT / rel
    return p.exists()


def generate():
    try:
        dashboard = json.loads(DASHBOARD_PATH.read_text())
    except Exception:
        dashboard = {}

    categories = []
    bucket_counts = {"A": 0, "B": 0, "C": 0}
    for c in CATEGORIES:
        entry = dict(c)
        entry["modules_exist"] = [dict(path=m, exists=_module_exists(m)) for m in c["modules"]]
        categories.append(entry)
        bucket_counts[c["bucket"]] += 1

    total = len(categories)
    bucket_pct = {
        k: round(100.0 * v / total, 1) if total else 0.0
        for k, v in bucket_counts.items()
    }

    data = dict(
        generated_at=_get(dashboard, "meta", "generated_at"),
        git_commit=_get(dashboard, "meta", "git_commit"),
        phase=_get(dashboard, "build", "current_phase"),
        test_count=_get(dashboard, "build", "test_count"),
        categories=categories,
        total_categories=total,
        bucket_counts=bucket_counts,
        bucket_pct=bucket_pct,
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return True


if __name__ == "__main__":
    generate()
