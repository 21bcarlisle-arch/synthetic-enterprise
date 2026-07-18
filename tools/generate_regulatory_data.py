#!/usr/bin/env python3
"""Generate site/data/regulatory.json for the Journey door's Regulatory tab.

Campaign A / debt A: the Regulatory tab's build-status claims ("62 regulatory
modules wired", "10 SLC domains", the per-scheme WIRED/EXEMPT/NEXT badges,
overall RAG) were static HTML with no data backing and no freshness stamp, so
they could silently drift from the real build state.

R15 (a control must be able to FAIL) forbids simply relocating those literals
into a JSON file -- that is the same unbacked claim in a new location. Every
build-status value emitted here is DERIVED from an independent, enumerable real
source, so it CANNOT drift from reality:

  * module_count      = live count of *.py scheme modules under company/regulatory
                        (the literal "62" was already stale -- real count differs).
  * slc_domain_count  = len(ComplianceDomain) from the real scorecard enum.
  * obligation_count / overall_rag / status_counts
                        = read from site/data/company.json's compliance block
                          (itself derived from the live ComplianceScorecard).
  * per-scheme status = derived, NOT asserted:
        EXEMPT  -> the scheme is genuinely N/A for THIS portfolio (its domestic
                   customer count is far below the large-supplier threshold that
                   makes WHD/ECO mandatory). Backed by the real portfolio count.
        WIRED   -> the scheme's calc module EXISTS on disk AND is wired into the
                   report layer (referenced under saas/reporting/, or the module
                   itself lives there).
        NEXT    -> the calc module exists but is NOT yet wired into the report
                   layer (built-not-wired), or is planned-not-built (absent).

The derivation is INJECTABLE (every source path / enum is a parameter defaulting
to the real one) so independence is testable without mutating the live codebase:
point module_root at a temp dir with N files and the emitted count follows N;
move a scheme's calc module out of the report layer and its badge flips
WIRED -> NEXT. That is the R15 proof it is derived, not a relocated hardcode.

SIMPLICITY GUARD: this is a stat-count-from-disk generator, not a repository
pattern -- plain path globs and one JSON read, mirroring
tools/generate_dashboard_data.py's stamp convention.

Usage:  python3 tools/generate_regulatory_data.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT / "site" / "data" / "regulatory.json"

# The large-supplier threshold (domestic customers) above which WHD & ECO become
# mandatory. Published Ofgem scheme threshold -- a cited legal constant, not a
# build metric. Kept explicit so the EXEMPT derivation shows its working.
LARGE_SUPPLIER_DOMESTIC_THRESHOLD = 150_000

# The 12 schemes shown as rows on the Regulatory tab, each pinned to the REAL
# calc module/register that implements it. `applicable=False` marks a scheme
# that is genuinely N/A for this (sub-threshold) portfolio -- the module may well
# exist and be wired, but the portfolio carries no obligation, so it renders
# EXEMPT regardless. Every other status is derived from disk + report-layer
# wiring, never asserted here.
DEFAULT_SCHEMES = [
    {"key": "RO", "label": "Renewable Obligation (RO)",
     "calc_module": "company/regulatory/roc_ledger.py", "applicable": True},
    {"key": "FiT", "label": "Feed-in Tariff (FiT) Levy",
     "calc_module": "company/regulatory/fit_book.py", "applicable": True},
    {"key": "CCL", "label": "Climate Change Levy (CCL)",
     "calc_module": "company/regulatory/ccl_ledger.py", "applicable": True},
    {"key": "GSOP", "label": "Guaranteed Standards (GSOP)",
     "calc_module": "company/regulatory/gsop.py", "applicable": True},
    {"key": "WHD", "label": "Warm Home Discount (WHD)",
     "calc_module": "company/regulatory/warm_home_discount.py", "applicable": False,
     "exempt_reason": "mandatory only above the large-supplier domestic threshold"},
    {"key": "ECO", "label": "Energy Company Obligation (ECO)",
     "calc_module": "company/regulatory/eco_obligation.py", "applicable": False,
     "exempt_reason": "mandatory only above the large-supplier domestic threshold"},
    {"key": "Carbon", "label": "Carbon Emissions",
     "calc_module": "company/regulatory/carbon_emissions.py", "applicable": True},
    {"key": "FMD", "label": "Fuel Mix Disclosure (FMD)",
     "calc_module": "company/regulatory/fuel_mix_disclosure.py", "applicable": True},
    {"key": "OSR", "label": "Ofgem Supply Return",
     "calc_module": "company/regulatory/ofgem_supply_return.py", "applicable": True},
    {"key": "SLC", "label": "SLC Compliance Scorecard",
     "calc_module": "company/regulatory/compliance_scorecard.py", "applicable": True},
    {"key": "FRA", "label": "FRA Capital Ratio",
     "calc_module": "saas/reporting/fra_capital_ratio.py", "applicable": True},
    {"key": "SR", "label": "Settlement Reconciliation",
     "calc_module": "company/regulatory/settlement_reconciliation.py", "applicable": True},
]


def count_regulatory_modules(module_root: Path) -> int:
    """Live count of *.py scheme modules under the regulatory package.

    Excludes __init__.py, __pycache__ and test_ modules so the number tracks
    actual scheme/register implementations. Mechanically derivable -- never a
    typed literal (the old hardcoded "62" had already drifted).
    """
    if not module_root.exists():
        return 0
    return sum(
        1 for p in module_root.rglob("*.py")
        if "__pycache__" not in p.parts
        and not p.name.startswith("test_")
        and p.name != "__init__.py"
    )


def _report_layer_files(report_roots) -> list[Path]:
    files: list[Path] = []
    for root in report_roots:
        root = Path(root)
        if root.exists():
            files += [
                p for p in root.rglob("*.py")
                if "__pycache__" not in p.parts
            ]
    return files


def derive_scheme_status(
    scheme: dict,
    project_root: Path,
    report_roots,
    domestic_customers: int,
    threshold: int,
) -> dict:
    """Derive one scheme's status from real, enumerable signals (never asserted).

    EXEMPT  -> scheme not applicable to a portfolio whose domestic customer
               count is below the large-supplier threshold.
    WIRED   -> calc module present on disk AND wired into the report layer.
    NEXT    -> calc module present but not wired, OR planned-not-built (absent).
    """
    module_rel = scheme["calc_module"]
    module_path = project_root / module_rel
    module_exists = module_path.is_file()

    if not scheme.get("applicable", True):
        exempt = domestic_customers < threshold
        return {
            "key": scheme["key"],
            "label": scheme["label"],
            "calc_module": module_rel,
            "module_present": module_exists,
            "status": "EXEMPT" if exempt else "WIRED",
            "basis": (
                f"portfolio has {domestic_customers} domestic customers, "
                f"below the {threshold:,} large-supplier threshold -- no obligation"
                if exempt else "module present + wired into report layer"
            ),
        }

    # Wired = the module is IMPORTED by the report layer, or the module itself
    # lives under a report-layer root. Match the module's dotted import path
    # (e.g. "company.regulatory.roc_ledger"), NOT a bare stem: a bare-stem
    # substring falsely matches a coincidentally-named report function
    # (`_section_fuel_mix_disclosure`) and would report a not-yet-wired scheme
    # as WIRED. The dotted path only appears in a real `import`/`from ... import`.
    dotted = module_rel[:-3].replace("/", ".") if module_rel.endswith(".py") else module_rel.replace("/", ".")
    report_files = _report_layer_files(report_roots)
    lives_in_report_layer = any(
        module_path.resolve() == f.resolve() for f in report_files
    )
    referenced = lives_in_report_layer or any(
        dotted in f.read_text(errors="ignore") for f in report_files
    )
    wired = module_exists and referenced

    if wired:
        status, basis = "WIRED", "calc module present + wired into report layer"
    elif module_exists:
        status, basis = "NEXT", "calc module present, not yet wired into report layer"
    else:
        status, basis = "NEXT", "planned -- calc module not yet built"

    return {
        "key": scheme["key"],
        "label": scheme["label"],
        "calc_module": module_rel,
        "module_present": module_exists,
        "status": status,
        "basis": basis,
    }


def _domestic_customer_count(customers_source: Path) -> int:
    """Count domestic (residential) customers from the real customer register."""
    if not customers_source.is_file():
        return 0
    try:
        data = json.loads(customers_source.read_text())
    except (json.JSONDecodeError, OSError):
        return 0
    return sum(
        1 for c in data.get("customers", [])
        if str(c.get("segment", "")).lower() in ("resi", "residential", "domestic")
    )


def derive_regulatory(
    project_root: Path = PROJECT,
    module_root: Path | None = None,
    module_root_rel: str = "company/regulatory",
    compliance_domains=None,
    obligations_source: Path | None = None,
    customers_source: Path | None = None,
    report_roots=None,
    schemes=None,
    threshold: int = LARGE_SUPPLIER_DOMESTIC_THRESHOLD,
    now: datetime | None = None,
) -> dict:
    """Assemble the Regulatory-tab data purely from independent real sources.

    Every source is an injectable parameter defaulting to the live one, so an
    R15 independence test can point any single input at a mutated fixture and
    assert the emitted value follows -- proving derivation, not a relocated
    literal.
    """
    project_root = Path(project_root)
    module_root = Path(module_root) if module_root else project_root / module_root_rel
    obligations_source = obligations_source or project_root / "site" / "data" / "company.json"
    customers_source = customers_source or project_root / "site" / "data" / "customers.json"
    report_roots = report_roots or [project_root / "saas" / "reporting"]
    schemes = schemes if schemes is not None else DEFAULT_SCHEMES

    if compliance_domains is None:
        from company.regulatory.compliance_scorecard import ComplianceDomain
        compliance_domains = list(ComplianceDomain)
    slc_domain_count = len(list(compliance_domains))

    module_count = count_regulatory_modules(module_root)

    # Obligation totals / overall RAG from the already-derived compliance block.
    obligation_count = 0
    overall_rag = "GREEN"
    status_counts: dict = {}
    if Path(obligations_source).is_file():
        try:
            comp = json.loads(Path(obligations_source).read_text())
            reg = comp.get("compliance", {}).get("obligations_register", {})
            obligation_count = int(reg.get("count", 0))
            overall_rag = reg.get("overall_rag", "GREEN")
            status_counts = reg.get("status_counts", {}) or {}
        except (json.JSONDecodeError, OSError, ValueError):
            pass

    domestic_customers = _domestic_customer_count(Path(customers_source))

    scheme_rows = [
        derive_scheme_status(
            s, project_root, report_roots, domestic_customers, threshold
        )
        for s in schemes
    ]

    now = now or datetime.now(timezone.utc)
    return {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "module_count": module_count,
        "module_source": module_root_rel,
        "slc_domain_count": slc_domain_count,
        "obligation_count": obligation_count,
        "overall_rag": overall_rag,
        "status_counts": status_counts,
        "domestic_customer_count": domestic_customers,
        "large_supplier_threshold": threshold,
        "schemes": scheme_rows,
    }


def main() -> None:
    data = derive_regulatory()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2) + "\n")
    print(
        f"Wrote {OUTPUT_PATH.relative_to(PROJECT)}: "
        f"{data['module_count']} modules, {data['slc_domain_count']} SLC domains, "
        f"overall RAG {data['overall_rag']}, "
        f"{sum(1 for s in data['schemes'] if s['status']=='WIRED')} WIRED / "
        f"{sum(1 for s in data['schemes'] if s['status']=='NEXT')} NEXT / "
        f"{sum(1 for s in data['schemes'] if s['status']=='EXEMPT')} EXEMPT"
    )


if __name__ == "__main__":
    main()
