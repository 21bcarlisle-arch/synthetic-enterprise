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

`defects` names each property the run breaks, and the grader exits 1 when it names any: carved not
equal to booked, a receipt carved outside the windows, an estimated bill below zero, or a share of
default-tariff bills over the ceiling above `OVER_CEILING_SHARE_BOUND`, or a leg carrying two
`account_state_log` rows that cover one day. Each such row is settled over its own window, so a
month under k rows is billed k times over (063dc4bbd6: 11 gas legs, 33 pairs at 1c30d6c728, priced
at what read as the mean of their rates). The publisher refuses a run
this names a defect on (`process_run_complete.billing_grade_refusal`), so this is the Monday gate. A negative
bill is under every ceiling, so the over-cap count alone passed the void stubs that the folded
`hmt_epg_receipt_gbp_per_mwh` credited at 48 times the Treasury's rate (c5a8090187: GBP 5,898.10
carved and never booked, because `validate_bills` held the five negative bills).

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

#: The share of graded default-tariff bills over the ceiling above which the run is a defect, not
#: the known ToU misgrade above. SIMPLIFICATION, set between two measured regimes rather than from a
#: rule, because the rule (SLC 28AD) is zero and the residual is this grader's own misgrade:
#: after the cap fixes, 88cdf35e48 graded 104 of 24,597 (0.42%, 16 households); before them,
#: 8b6fea024 graded 5,488 of 18,398 (29.8%) and 1044c8fe0d 6,719 of 24,417 (27.5%). Five times the
#: post-fix residual, and fourteen times under the defect. Doing it properly means grading a ToU
#: term at its assumed split; the error runs toward passing a run with a small real breach.
OVER_CEILING_SHARE_BOUND = 0.02


def _load(path: Path) -> dict:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def _in_epg_window(commodity: str, on: date) -> bool:
    epg = get_cap_unit_rate_for_date(commodity, on, net_of_epg=True)
    cap = get_cap_unit_rate_for_date(commodity, on, net_of_epg=False)
    return epg is not None and cap is not None and epg < cap


def terms_by_customer(run: dict) -> dict[str, list[dict]]:
    terms = defaultdict(list)
    for t in run.get("account_state_log") or []:
        terms[t["customer_id"]].append(t)
    return terms


def term_of_bill(terms: dict[str, list[dict]], b: dict) -> dict | None:
    """The recorded term a bill's period starts in; None when the run records none."""
    iso = str(b["period_start"])[:10]
    return next((t for t in terms.get(b["customer_id"], ())
                 if t["term_start"] <= iso < t["term_end"]), None)


def bill_excess(b: dict, tariff_type: str) -> float | None:
    """The class invariant over a run bill's own unrounded amounts (None: not gradeable)."""
    invoice = {**b, "amount_gbp": b.get("total_amount_gbp"),
               "consumption_kwh": b.get("total_consumption_kwh")}
    return default_tariff_invoice_excess_p_per_kwh(invoice, tariff_type)


def grade(run: dict) -> dict:
    terms = terms_by_customer(run)
    reads = defaultdict(Counter)
    for b in run.get("bills") or []:
        reads[b["customer_id"]][b.get("billing_basis")] += 1

    graded = over = ungradeable = 0
    households, by_year, outside_epg, on_actual_read = set(), Counter(), 0, 0
    for b in run.get("bills") or []:
        iso = str(b["period_start"])[:10]
        term = term_of_bill(terms, b)
        if term is None or term["tariff_type"] not in DEFAULT_TARIFF_TYPES:
            continue
        excess = bill_excess(b, term["tariff_type"])
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
        "overlapping_term_legs": overlapping_term_legs(run),
        "negative_estimated_bills": [
            {"customer_id": b["customer_id"], "period_start": str(b["period_start"])[:10],
             "total_amount_gbp": round(b["total_amount_gbp"], 2)}
            for b in run.get("bills") or []
            if b.get("billing_basis") == "estimated" and (b.get("total_amount_gbp") or 0.0) < 0
        ],
    }


def overlapping_term_legs(run: dict) -> dict[str, int]:
    """Each leg whose recorded terms overlap, with its count of overlapping pairs."""
    terms = defaultdict(list)
    for t in run.get("account_state_log") or []:
        terms[t["customer_id"]].append(t)
    out = {}
    for cid, ts in terms.items():
        pairs = sum(1 for i, a in enumerate(ts) for b in ts[i + 1:]
                    if b["term_start"] < a["term_end"] and a["term_start"] < b["term_end"])
        if pairs:
            out[cid] = pairs
    return dict(sorted(out.items()))


def defects(g: dict) -> list[str]:
    """The properties a grade shows broken, each named with its numbers; empty when none is."""
    out = []
    receipt = g["epg_receipt"]
    if receipt["booked_gbp"] is None:
        if receipt["carved_gbp"]:
            out.append(f"GBP {receipt['carved_gbp']:,.2f} carved and the run carries no ledger_pnl")
    elif abs(receipt["carved_gbp"] - receipt["booked_gbp"]) > 0.01:
        out.append(f"carved GBP {receipt['carved_gbp']:,.2f} != booked GBP "
                   f"{receipt['booked_gbp']:,.2f}")
    if receipt["carved_outside_epg_windows"]:
        out.append(f"{receipt['carved_outside_epg_windows']} receipt(s) carved outside the EPG windows")
    if g["share"] is not None and g["share"] > OVER_CEILING_SHARE_BOUND:
        out.append(f"{g['above_household_ceiling']:,} of {g['default_tariff_invoices_graded']:,} "
                   f"default-tariff bills ({g['share']:.1%}) over the household's ceiling, across "
                   f"{g['households_above']:,} households")
    if g["overlapping_term_legs"]:
        legs = g["overlapping_term_legs"]
        out.append(f"{len(legs)} leg(s) carry overlapping account-state terms "
                   f"({sum(legs.values())} pairs), first {next(iter(legs))}")
    if g["negative_estimated_bills"]:
        worst = min(g["negative_estimated_bills"], key=lambda b: b["total_amount_gbp"])
        out.append(f"{len(g['negative_estimated_bills'])} estimated bill(s) below zero, worst "
                   f"{worst['customer_id']} {worst['period_start']} GBP {worst['total_amount_gbp']:,.2f}")
    return out


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
    g = grade(_load(Path(argv[0])))
    g["defects"] = defects(g)
    print(json.dumps(g, indent=2))
    return 1 if g["defects"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
