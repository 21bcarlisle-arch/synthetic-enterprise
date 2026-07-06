#!/usr/bin/env python3
"""Generate site/data/platform.json -- the Platform section's data source.

NAV_STORY_PLATFORM_METHOD.md P1 (the CTO/CPO view): architecture layers,
module/domain map, API/adapter registry, synthetic data catalogue. All counts
are computed fresh from the repo filesystem or read from real generated
artifacts at generation time -- nothing here is a hand-typed number that can
drift stale (see docs/PROJECT_OVERVIEW.md's company_modules staleness history,
fixed at the root in tools/generate_dashboard_data.py::count_company_modules
this same phase).
"""
import json
from pathlib import Path as _P

from tools.generate_dashboard_data import count_company_modules

PROJECT = _P(__file__).resolve().parent.parent
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"
OUT_PATH = PROJECT / "site" / "data" / "platform.json"


def _get(d, *path):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _count_py(rel_dir, exclude_tests=True):
    d = PROJECT / rel_dir
    if not d.exists():
        return 0
    n = 0
    for p in d.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        if exclude_tests and p.name.startswith("test_"):
            continue
        n += 1
    return n


def _company_domain_counts():
    company_dir = PROJECT / "company"
    counts = {}
    if not company_dir.exists():
        return counts
    for sub in sorted(company_dir.iterdir()):
        if not sub.is_dir() or sub.name == "__pycache__":
            continue
        n = sum(
            1 for p in sub.rglob("*.py")
            if "__pycache__" not in p.parts and not p.name.startswith("test_")
        )
        if n:
            counts[sub.name] = n
    return counts


COMPANY_DOMAIN_TAGS = {
    "crm": "universal", "finance": "universal", "portal": "universal",
    "analytics": "universal", "core": "universal",
    "billing": "market", "pricing": "market", "market": "market", "trading": "market",
    "risk": "market", "interfaces": "universal",
    "regulatory": "uk", "compliance": "uk", "sustainability": "uk",
}

LAYER_TAGS = {
    "sim": ("uk", "Elexon, NESO and Open-Meteo ingestion plus forward curves -- UK market specific"),
    "simulation": ("market", "Settlement, renewal and customer-event mechanics -- generalizes to other liberalized energy markets"),
    "saas": ("market", "Original Phase 0a business layer: pricing, billing, CLV, churn -- superseded in depth by company/, kept as the founding scaffold"),
    "tools": ("universal", "Site and report generation, data adapters -- no energy-domain logic"),
    "background": ("universal", "Autonomous orchestration daemons -- transferable to any agent-run business"),
    "interface": ("universal", "sim-to-saas data-contract seam, Phase 0a scaffold; contracts directory not yet populated"),
}


ADAPTER_REGISTRY = [
    dict(name="MarketDataPort", file="tools/market_data_port.py", boundary="Market data (spot and forward prices)",
         status="LIVE", description="Structural Protocol adapters satisfy without inheritance. Current: Frozen2025Adapter wraps the live_market.py frozen 2025-12-31 cache."),
    dict(name="CreditBureauPort", file="tools/credit_bureau_port.py", boundary="Credit check (acquisition)",
         status="LIVE", description="Epistemic-boundary adapter: company code only ever reads the noisy bureau read (passed / score_band), never the SIM ground-truth creditworthiness. Wired into the acquisition funnel (Phase QR)."),
    dict(name="sim_interface", file="company/interfaces/sim_interface.py", boundary="SIM to company observables",
         status="LIVE", description="The company-layer epistemic wall: exposes market data, meter reads, customer interactions -- never simulation internals such as churn params, forward-curve construction, or weather-engine outputs."),
    dict(name="interface directory (sim-saas contracts)", file="interface/README.md", boundary="sim to saas data contracts",
         status="SCAFFOLDED", description="Phase 0a original seam design for point-in-time market snapshots and forecast feeds. The contracts subdirectory is still empty -- saas/ has been overtaken in practice by the larger company/ layer's own sim_interface.py seam."),
    dict(name="PSP adapter (payments)", file=None, boundary="Payment service provider",
         status="PLANNED", description="No dedicated adapter yet -- payment behaviour is currently modelled directly, not via a swappable PSP boundary."),
    dict(name="DCC adapter (smart metering)", file=None, boundary="Data Communications Company smart meter reads",
         status="PLANNED", description="No dedicated adapter yet -- smart-meter HH data is generated directly rather than read through a DCC-shaped boundary."),
]


SYNTHETIC_DATA_CATALOGUE = [
    dict(dataset="customer_sample.json", path="/data/customer_sample.json",
         description="Per-customer behavioural trajectories: satisfaction history, income-stress, journey stage, switching propensity -- the population-anchored calibration inputs.",
         calibration="population-anchored against DESNZ and Ofgem benchmarks, Phases NS and PQ through PS"),
    dict(dataset="one JSON per household account under site/data/customers/", path="/data/customers/",
         description="Full Customer 360 record per household or account: accounts, consumption, billing, timeline, reaction chain.",
         calibration="derived from the live sim run, no separate calibration"),
    dict(dataset="dashboard.json", path="/data/dashboard.json",
         description="Full board dataset: portfolio, financial, trading, regulatory, and the portfolio-wide decision and event stream.",
         calibration="real run output, not a calibrated distribution"),
    dict(dataset="sim_data.json", path="/data/sim_data.json",
         description="Market physics: settlement prices, system tightness (Short percent and NIV), gas NBP, negative-price-hour counts, ten years of history.",
         calibration="real Elexon and NESO settlement history, not synthetic"),
    dict(dataset="weather.json", path="/data/weather.json",
         description="Daily and monthly UK temperature and heating-degree-days, ten years of history, chained through to price and system-tightness episodes.",
         calibration="real Open-Meteo history, not synthetic"),
    dict(dataset="billing_ledger.json", path="/state/billing_ledger.json",
         description="Real per-invoice usage, rate and standing-charge breakdown for every bill issued across the run -- the source for the bill-equation and why-different waterfall on Customer 360.",
         calibration="derived from the live sim run"),
    dict(dataset="population_anchoring.json", path="/state/population_anchoring.json",
         description="Churn, switching, complaints and arrears rates benchmarked against real-world population statistics -- the calibration artifact itself, not just an input.",
         calibration="population-anchored, the calibration record itself"),
]


def generate():
    try:
        dashboard = json.loads(DASHBOARD_PATH.read_text())
    except Exception:
        dashboard = {}

    company_counts = _company_domain_counts()
    company_total = count_company_modules()

    layers = []
    for rel_dir, tag_note in LAYER_TAGS.items():
        tag, note = tag_note
        n = _count_py(rel_dir)
        if n == 0 and not (PROJECT / rel_dir).exists():
            continue
        layers.append(dict(name=rel_dir, module_count=n, transferability=tag, note=note))

    company_domains = []
    for name, count in sorted(company_counts.items(), key=lambda kv: -kv[1]):
        company_domains.append(dict(
            name=name, module_count=count,
            transferability=COMPANY_DOMAIN_TAGS.get(name, "market"),
        ))

    adapters = []
    for a in ADAPTER_REGISTRY:
        entry = dict(a)
        if entry["file"]:
            entry["file_exists"] = (PROJECT / entry["file"]).exists()
        else:
            entry["file_exists"] = None
        adapters.append(entry)

    catalogue = []
    for item in SYNTHETIC_DATA_CATALOGUE:
        rel = item["path"].lstrip("/")
        full = PROJECT / "site" / rel
        entry = dict(item)
        if full.is_dir():
            files = [p for p in full.glob("*.json")]
            entry["size_bytes"] = None
            entry["file_count"] = len(files)
            entry["total_bytes"] = sum(p.stat().st_size for p in files)
        elif full.exists():
            entry["size_bytes"] = full.stat().st_size
            entry["file_count"] = None
            entry["total_bytes"] = None
        else:
            entry["size_bytes"] = None
            entry["file_count"] = None
            entry["total_bytes"] = None
        catalogue.append(entry)

    data = dict(
        generated_at=_get(dashboard, "meta", "generated_at"),
        git_commit=_get(dashboard, "meta", "git_commit"),
        phase=_get(dashboard, "build", "current_phase"),
        test_count=_get(dashboard, "build", "test_count"),
        company_module_total=company_total,
        layers=layers,
        company_domains=company_domains,
        adapters=adapters,
        synthetic_data_catalogue=catalogue,
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return True


if __name__ == "__main__":
    generate()
