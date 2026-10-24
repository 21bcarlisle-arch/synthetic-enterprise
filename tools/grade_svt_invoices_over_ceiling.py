"""Count a run's default-tariff invoices above the household's ceiling, with the denominator.

The grade SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_2026-10-23.md
pre-registered for the fresh run: every invoice inside an `account_state_log` term whose recorded
`tariff_type` is a default one, graded by the class invariant
`default_tariff_invoice_excess_p_per_kwh` against min(cap, EPG). It reads the run output alone, so it
needs no published site and can sit behind the run's .rc as a continuation.

The tariff type comes from the term the run recorded, never from "before the first renewal": that
proxy is how 185 fixed-term bills were once counted as SVT.

Known misgrade, stated so the count is read right: a smart-metered home's default term is settled on
a ToU pair (`company/pricing/tou_desk.offers_tou`), and SLC 28AD.4 grades that at its assumed split,
not per bill. A bill can sit a few per cent over a pair struck at the cap. `actual_read_accounts`
counts what lands on accounts billed mostly on actual reads, which is that population's footprint.

`epg_receipt` grades the EPG pre-registration's predictions 3 and 4 on one run. Every pound carved
off a household's bill as the Treasury's share must be booked as a receipt (`carved_gbp` against the
ledger's `booked_gbp`), and none may be carved outside an EPG window. `unit_charge_fall` is the
median share of each bill's unit charge the receipt removed, by quarter and fuel: it should sit at
that quarter's (cap - EPG) / cap, not at one band for the whole crisis.

    python3 -m tools.grade_svt_invoices_over_ceiling docs/reports/run_output_<commit>_<stamp>.json[.gz]
"""

from __future__ import annotations

import gzip
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import median

from company.compliance.domain_invariants import (
    DEFAULT_TARIFF_TYPES,
    default_tariff_invoice_excess_p_per_kwh,
)
from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date


def _load(path: Path) -> dict:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def _in_epg_window(commodity: str, on: date) -> bool:
    epg = get_cap_unit_rate_for_date(commodity, on, net_of_epg=True)
    cap = get_cap_unit_rate_for_date(commodity, on, net_of_epg=False)
    return epg is not None and cap is not None and epg < cap


def grade(run: dict) -> dict:
    terms = defaultdict(list)
    for t in run.get("account_state_log") or []:
        terms[t["customer_id"]].append(t)
    reads = defaultdict(Counter)
    for b in run.get("bills") or []:
        reads[b["customer_id"]][b.get("billing_basis")] += 1

    graded = over = ungradeable = 0
    households, by_year, outside_epg, on_actual_read = set(), Counter(), 0, 0
    for b in run.get("bills") or []:
        iso = str(b["period_start"])[:10]
        term = next((t for t in terms.get(b["customer_id"], ())
                     if t["term_start"] <= iso < t["term_end"]), None)
        if term is None or term["tariff_type"] not in DEFAULT_TARIFF_TYPES:
            continue
        invoice = {**b, "amount_gbp": b.get("total_amount_gbp"),
                   "consumption_kwh": b.get("total_consumption_kwh")}
        excess = default_tariff_invoice_excess_p_per_kwh(invoice, term["tariff_type"])
        if excess is None:
            ungradeable += 1
            continue
        graded += 1
        if not excess:
            continue
        over += 1
        households.add(term.get("billing_account") or b["customer_id"])
        by_year[iso[:4]] += 1
        if not _in_epg_window(b.get("commodity") or "electricity", date.fromisoformat(iso)):
            outside_epg += 1
        r = reads[b["customer_id"]]
        if r["actual"] >= r["estimated"]:
            on_actual_read += 1
    return {
        "producing_commit": (run.get("producing_commit") or {}).get("commit"),
        "default_tariff_invoices_graded": graded,
        "ungradeable": ungradeable,
        "above_household_ceiling": over,
        "share": round(over / graded, 4) if graded else None,
        "households_above": len(households),
        "outside_epg_windows": outside_epg,
        "actual_read_accounts": on_actual_read,
        "by_year": dict(sorted(by_year.items())),
        "epg_receipt": epg_receipt(run),
    }


def _quarter(iso: str) -> str:
    return f"{iso[:4]}-Q{(int(iso[5:7]) - 1) // 3 + 1}"


def epg_receipt(run: dict) -> dict:
    carved, outside, falls = 0.0, 0, defaultdict(list)
    carrying = 0
    for b in run.get("bills") or []:
        receipt = b.get("hmt_epg_receipt_gbp") or 0.0
        if not receipt:
            continue
        carrying += 1
        carved += receipt
        iso = str(b["period_start"])[:10]
        commodity = b.get("commodity") or "electricity"
        if not _in_epg_window(commodity, date.fromisoformat(iso)):
            outside += 1
        unit = (b.get("commodity_amount_gbp") or 0.0) + (b.get("non_commodity_amount_gbp") or 0.0)
        falls[f"{_quarter(iso)} {commodity}"].append(receipt / (unit + receipt))
    booked = (run.get("ledger_pnl") or {}).get("epg_receipt_gbp")
    return {
        "bills_carrying_receipt": carrying,
        "carved_gbp": round(carved, 2),
        "booked_gbp": None if booked is None else round(booked, 2),
        "carved_outside_epg_windows": outside,
        "unit_charge_fall": {k: round(median(v), 3) for k, v in sorted(falls.items())},
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[-1])
        return 2
    print(json.dumps(grade(_load(Path(argv[0]))), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
