#!/usr/bin/env python3
"""What a value-pricing supplier would DO with this book, beside what today's supplier does.

REUSE: tools/couple_value_based_pricing.py
CLASS: PATTERN-REUSE
INDEX: searched "couple", "baseline", "arm", "control", "counterfactual", "clv". The COUPLED-
       RUNNER pattern is taken wholesale from `tools/couple_pb3_book_growth.py` and its
       siblings: harness code in `tools/`, outside the wall by design, the only layer allowed to
       hold the company's belief and the world's outcome side by side
       (COUPLED_TRIAD_DESIGN 1.3). The decision itself is
       `company/pricing/value_based_renewal.decide_margin` and nothing is recomputed here.
       `company/analytics/counterfactual_retention.py` was read and is NOT the same thing: it
       scores retention OFFERS against a fixed effectiveness assumption; this compares two
       PRICING RULES on the same book.

WHY IT EXISTS
-------------
Director, 2026-08-25: *"there has to be a baseline to beat. Average behaviour is the control —
the same book run by a supplier applying flat rules with no per-customer view. Without that
comparison, 'it performed well' means nothing."*

The control is free, because today's company IS it: a flat £2.00/MWh for every account. So this
runs both arms over the real book and reports what they would decide differently.

WHAT IT MEASURES, AND WHAT IT CANNOT
------------------------------------
DECISIONS, not earnings. It reports what each arm would OFFER and what each arm BELIEVES that
offer is worth. It does not report what either would earn, and it must not be read as though it
did: the value arm maximises the company's own expected value, so scoring the arms on expected
value lets the value arm win by construction — R15's tautology with money in it.

The honest earnings comparison is REALISED: the same book, the same world, run once per arm,
scored on what actually happened. That needs two full runs and is the next step.

WHAT IT FOUND ON ITS FIRST RUN, which is why the arm is not wired to the renewal desk. See
`value_based_renewal.max_supported_rate_increase_pct` for the mechanism.

Run:  python3 -m tools.couple_value_based_pricing
"""
from __future__ import annotations

import collections
import glob
import json
from pathlib import Path

from company.pricing.value_based_renewal import (
    FLAT_RULES,
    VALUE_BASED,
    MarginDecisionUnavailable,
    decide_margin,
    max_supported_rate_increase_pct,
)
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH

PROJECT = Path(__file__).resolve().parent.parent
BOOK_PATH = PROJECT / "site" / "data" / "customers.json"
OUT_PATH = PROJECT / "docs" / "observability" / "value_based_pricing_arms.json"

#: Renewal year the comparison is struck at. The arms are compared at ONE moment so the
#: difference between them is the RULE and never the calendar.
AS_OF_YEAR = 2025

#: Months per year, for turning a bill count into the years a meter has been on supply. The book
#: publishes `bill_count` and `total_kwh` and not an EAC, so the annualisation is stated here
#: rather than hidden in an expression.
BILLS_PER_YEAR = 12.0


def latest_run_output() -> Path:
    """The newest dated run output. Raises rather than returning None: an arms comparison with
    no book is not an empty comparison, it is one that did not run."""
    dated = [p for p in glob.glob(str(PROJECT / "docs" / "reports" / "run_output_*.json"))
             if "2026" in Path(p).name]
    if not dated:
        raise MarginDecisionUnavailable("no dated run output to read a book from")
    return Path(max(dated, key=lambda p: p.rsplit("_", 1)[-1]))


def _legs(book: dict) -> dict:
    out = {}
    for customer in book.get("customers") or []:
        for leg in (customer.get("legs") or {}).values():
            cid = leg.get("cid")
            if cid:
                out[cid] = leg
    return out


def compare(run: dict, book: dict, as_of_year: int = AS_OF_YEAR) -> dict:
    """Both arms over every account the company has enough of its own record to price."""
    legs = _legs(book)
    per_account, skipped = [], collections.Counter()

    for cid, record in (run.get("per_customer_lifetime") or {}).items():
        leg = legs.get(cid) or {}
        total_kwh = float(leg.get("total_kwh") or 0.0)
        avg_rate = float(leg.get("avg_rate_gbp_per_mwh") or 0.0)
        bills = float(leg.get("bill_count") or 0.0)
        years = max(1.0, bills / BILLS_PER_YEAR)
        eac = total_kwh / years
        if eac <= 0.0 or avg_rate <= 0.0:
            # NAMED, not dropped. An account the company cannot price is a fact about its own
            # records, and a comparison that silently covers 200 of 263 accounts is a different
            # claim from one that covers all of them.
            skipped["no consumption or rate on this company's own record"] += 1
            continue
        common = dict(
            customer_id=cid,
            current_rate_gbp_per_mwh=avg_rate,
            base_rate_gbp_per_mwh=avg_rate - TARGET_MARGIN_GBP_PER_MWH,
            eac_kwh=eac,
            tenure_years=years,
            cost_to_serve_gbp_per_year=float(record.get("cost_to_serve_gbp") or 0.0) / years,
            expected_periods=min(6.0, years),
            segment=record.get("segment") or "resi",
            renewal_year=as_of_year,
        )
        try:
            flat = decide_margin(arm=FLAT_RULES, **common)
            value = decide_margin(arm=VALUE_BASED, **common)
        except MarginDecisionUnavailable as exc:
            skipped[str(exc)[:60]] += 1
            continue
        per_account.append({
            "customer_id": cid,
            "segment": common["segment"],
            "eac_kwh": round(eac, 1),
            "flat_margin_gbp_per_mwh": flat.margin_gbp_per_mwh,
            "value_margin_gbp_per_mwh": value.margin_gbp_per_mwh,
            "value_over_flat_multiple": round(
                value.margin_gbp_per_mwh / flat.margin_gbp_per_mwh, 1) if flat.margin_gbp_per_mwh else None,
            "implied_bill_change_pct": round(
                100.0 * (value.margin_gbp_per_mwh - flat.margin_gbp_per_mwh) / avg_rate, 1),
            "endpoint_bound": value.endpoint_bound,
            "ceiling_bound": value.ceiling_bound,
            "extrapolation_bound": value.extrapolation_bound,
            "withheld_reason": value.withheld_reason,
        })

    chosen = collections.Counter(r["value_margin_gbp_per_mwh"] for r in per_account)
    n = len(per_account)
    return {
        "as_of_year": as_of_year,
        "accounts_priced": n,
        "accounts_skipped": dict(skipped),
        "control": {
            "arm": FLAT_RULES,
            "margin_gbp_per_mwh": TARGET_MARGIN_GBP_PER_MWH,
            "what_it_is": (
                "what this company does today: one margin for every account, whoever they are. "
                "Imported from saas/tariff_pricing.py rather than restated, so the control "
                "cannot drift from the supplier it describes."
            ),
        },
        "model_support_bound_pct": round(max_supported_rate_increase_pct(), 1),
        "differs_from_control": sum(
            1 for r in per_account if r["value_margin_gbp_per_mwh"] != TARGET_MARGIN_GBP_PER_MWH),
        "endpoint_bound": sum(1 for r in per_account if r["endpoint_bound"]),
        "extrapolation_bound": sum(1 for r in per_account if r["extrapolation_bound"]),
        "withheld_on_vulnerability": sum(1 for r in per_account if r["withheld_reason"]),
        "chosen_margins": {str(k): v for k, v in sorted(chosen.items())},
        "median_implied_bill_change_pct": (
            sorted(r["implied_bill_change_pct"] for r in per_account)[n // 2] if n else None),
        "verdict": _verdict(per_account),
        "accounts": per_account,
    }


def _verdict(rows: list[dict]) -> dict:
    """The one paragraph a reader needs, DERIVED, so it cannot go stale beside the numbers.

    A comparison that leaves the reader to work out whether the arm is usable will be quoted as
    though it were, and this one is not usable — see the reason it names.
    """
    if not rows:
        return {"fit_to_run": False, "why": "no account could be priced, so nothing was compared"}
    at_edge = sum(1 for r in rows if r["endpoint_bound"])
    median_change = sorted(r["implied_bill_change_pct"] for r in rows)[len(rows) // 2]
    fit = at_edge == 0 and median_change < 25.0
    return {
        "fit_to_run": fit,
        "why": (
            "The value arm chose the highest margin available to it on {} of {} accounts and "
            "would move the median bill by {:+.0f}%. That is not a decision, it is a ceiling: "
            "the company's churn model caps churn at MAX_CHURN_PROBABILITY = 0.95 and saturates "
            "toward it, so a floor of customers is modelled as staying whatever they are "
            "charged, and expected value rises with price across the whole range the model "
            "supports. The arithmetic is doing its job; the belief underneath it cannot carry a "
            "decision. Fix the belief before wiring the decision."
        ).format(at_edge, len(rows), median_change) if not fit else (
            "The value arm found interior optima and moves the median bill by {:+.0f}%."
        ).format(median_change),
    }


def generate(out_path: Path | None = None) -> dict:
    run = json.loads(latest_run_output().read_text(encoding="utf-8"))
    book = json.loads(BOOK_PATH.read_text(encoding="utf-8"))
    data = compare(run, book)
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = generate()
    print("priced {} account(s); {} differ from the control; {} at a grid edge".format(
        d["accounts_priced"], d["differs_from_control"], d["endpoint_bound"]))
    print("fit to run: {} -- {}".format(d["verdict"]["fit_to_run"], d["verdict"]["why"]))
