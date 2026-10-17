"""Energy theft / loss indicator.

A supplier's own consumption analytics are a legitimate theft LEAD source: tip-offs and
suppliers' own analysis gave 85% of suspected gas theft incidents (Ofgem 2015 §1.93, in
`docs/market_research/read_access_and_theft_duties.md` §3.2). Actual kWh far below EAC can mean
tampering -- or a vacant property, a faulty meter, or non-communication (the TEM's H4); it is a
reason to look, not a finding.

Corrected 2026-10-06: this said suppliers "can be penalised by Ofgem for failing to report
suspected energy theft" and told the user to "report to Ofgem". No source read requires reporting
theft to Ofgem. The duties are SLC 12A: investigate where there are reasonable grounds (12A.6),
enter detected theft into settlement, and work through REC Schedule 7 (TRAS risk scores, ETTOS
tip-offs, TDIS) under the Revenue Protection Code of Practice.

This flags customers whose annualised actual consumption deviates from their EAC, using only
company-observable data (invoices + EAC).
"""

from __future__ import annotations

import datetime as dt

#: UNSOURCED, so None. The 0.40 ("investigate") and 0.65 ("watch") ratios this held were typed
#: with no source, and no published actual/EAC screening threshold was found
#: (read_access_and_theft_duties.md §5). A screen tuned to a supplier's own investigation
#: outcomes would be a graded BELIEF; until one exists the caller supplies the cut-offs, and
#: without them a customer is reported "unscreened" rather than classified on an invented number.
_THEFT_THRESHOLD_LOW: float | None = None
_CONCERN_THRESHOLD_LOW: float | None = None


def _consumption_ratio(actual_kwh: float, eac_kwh: float) -> float | None:
    if eac_kwh <= 0:
        return None
    return actual_kwh / eac_kwh


def classify_anomaly(
    actual_kwh: float,
    eac_kwh: float,
    investigate_below: float | None = None,
    watch_below: float | None = None,
) -> dict:
    """Classify consumption anomaly against EAC.

    Returns: status (ok/watch/investigate/no_data/unscreened), ratio, message.
    """
    ratio = _consumption_ratio(actual_kwh, eac_kwh)
    if ratio is None:
        return {"status": "no_data", "ratio": None, "message": "No EAC to compare against."}
    investigate = investigate_below if investigate_below is not None else _THEFT_THRESHOLD_LOW
    watch = watch_below if watch_below is not None else _CONCERN_THRESHOLD_LOW
    if investigate is None or watch is None:
        return {
            "status": "unscreened",
            "ratio": round(ratio, 3),
            "message": (
                f"Actual consumption is {ratio:.0%} of EAC. Not classified: no sourced "
                "screening threshold exists and none was supplied."
            ),
        }
    if investigate > watch:
        raise ValueError(f"investigate_below ({investigate}) must not exceed watch_below ({watch})")
    if ratio < investigate:
        return {
            "status": "investigate",
            "ratio": round(ratio, 3),
            "message": (
                f"Actual consumption is {ratio:.0%} of EAC — significantly below expected. "
                "Possible meter fault, tampering, or vacant property. Where there are reasonable "
                "grounds to suspect theft, investigate under SLC 12A and the Revenue Protection "
                "Code of Practice, alongside the TRAS score (REC Schedule 7)."
            ),
        }
    if ratio < watch:
        return {
            "status": "watch",
            "ratio": round(ratio, 3),
            "message": (
                f"Actual consumption is {ratio:.0%} of EAC — below expected range. "
                "Monitor for further deviation."
            ),
        }
    return {
        "status": "ok",
        "ratio": round(ratio, 3),
        "message": f"Consumption ({ratio:.0%} of EAC) within normal range.",
    }


def screen_portfolio(
    customers_with_actuals: list[dict],
    investigate_below: float | None = None,
    watch_below: float | None = None,
) -> dict:
    """Screen a list of customers for theft/anomaly indicators.

    Each entry must have: customer_id, eac_kwh, actual_kwh_ytd, annualised_actual_kwh.
    Returns: investigate/watch/ok/unscreened counts and the results list.
    """
    results = []
    for c in customers_with_actuals:
        cid = c.get("customer_id", "?")
        eac = float(c.get("eac_kwh", 0))
        actual = float(c.get("annualised_actual_kwh", 0))
        classification = classify_anomaly(actual, eac, investigate_below, watch_below)
        results.append({"customer_id": cid, **classification})

    return {
        "total": len(results),
        "investigate": sum(1 for r in results if r["status"] == "investigate"),
        "watch": sum(1 for r in results if r["status"] == "watch"),
        "ok": sum(1 for r in results if r["status"] == "ok"),
        "unscreened": sum(1 for r in results if r["status"] == "unscreened"),
        "results": sorted(results, key=lambda r: (r.get("ratio") or 9999)),
    }


# --- Structural flags (2026-10-17) -------------------------------------------------------------
# Knowledge: docs/market_research/unbilled_energy_and_revenue_assurance.md §4a. W2_36's probe found
# that a ratio cannot tell a theft from a void; length and the occupier can. Neither flag below
# needs a typed ratio cut.

#: The shortest span read as an annual window. A design choice, not a published one (§4a GAP: no
#: screening window is published): thefts run about two years and voids about a month, and a year
#: cancels the seasonal shape error of a monthly expectation. 360, not 365, so twelve monthly
#: periods that start on the 1st always qualify.
ANNUAL_WINDOW_MIN_DAYS = 360

#: UNSOURCED, so None, as the ratio screen's thresholds are: no published actual/expected cut was
#: found (§4a). Without a caller's cut the annual window is reported "unscreened".
_ANNUAL_WINDOW_CUT: float | None = None


def _named_occupier(period: dict) -> bool:
    # A void is the owner's (B7 slice 6) and an unnamed stretch is "the occupier"'s (slice 5); a
    # period wholly either has nobody named. A share below 1 means someone named held part of it.
    return (float(period.get("void_owner_share") or 0.0) < 1.0
            and float(period.get("occupier_share") or 0.0) < 1.0)


def empty_period_flags(periods: list[dict], opening_read_status: str | None = None) -> list[dict]:
    """Spans of zero advance between two consecutive actual reads on a named occupier's account.

    `periods` is one account's billing periods in any order, each with `period_start`,
    `period_end`, `commodity`, `read_status` ("actual"/"estimated"), `registered_kwh` (the
    period's metered advance as the company knows it once read), and the bill's
    `void_owner_share` / `occupier_share` when present. The span runs from the period after one
    actual read to the next actual read, so a meter read twice a year is judged over six months.

    Electricity only: up to 2% of occupied homes use no gas at all (Ofgem, 20 June 2014), so a gas
    empty period is reported "not_screened" rather than flagged. A span before the first actual
    read is judged only if `opening_read_status` is "actual": the read the account opened on. At a
    change of tenancy that is the outgoing account's closing read (`boundary_read_status`). An
    estimated opening read is the company's own guess, so a zero advance from it is not measured.
    """
    rows = sorted(periods, key=lambda p: p["period_start"])
    flags: list[dict] = []
    span: list[dict] = []
    seen_actual = opening_read_status == "actual"
    for p in rows:
        span.append(p)
        if p.get("read_status") != "actual":
            continue
        if seen_actual and sum(float(r.get("registered_kwh") or 0.0) for r in span) == 0.0:
            named = any(_named_occupier(r) for r in span)
            commodity = p.get("commodity")
            if commodity != "electricity":
                status, reason = "not_screened", (
                    "Zero gas advance; up to 2% of occupied homes use no gas (Ofgem 2014), so "
                    "an empty gas period is not a theft lead.")
            elif not named:
                status, reason = "void", (
                    "Zero advance with nobody named: the owner's void or 'the occupier', "
                    "which explains it.")
            else:
                status, reason = "investigate", (
                    "Zero advance between two actual reads while a named occupier was liable. "
                    "A lead, not a finding: investigate where there are reasonable grounds "
                    "(SLC 12A.6), alongside the TRAS score.")
            flags.append({
                "customer_id": p.get("customer_id"), "commodity": commodity,
                "span_start": span[0]["period_start"], "span_end": p["period_end"],
                "periods": len(span), "named_occupier": named,
                "status": status, "message": reason,
            })
        seen_actual = True
        span = []
    return flags


def boundary_read_status(outgoing_periods: list[dict], opened_on: str) -> str | None:
    """The status of the read an incoming account opens on: the outgoing account's closing read.

    With the same supplier a change of tenancy has no industry read process (BSCP504 names it only
    to end a Long Term Vacant period, §4.15.5). The meter does not change, so the one read closes
    one account and opens the next. That read is the outgoing account's last read, if its period
    ends the day before `opened_on`. Otherwise the boundary is unread and this returns None.
    """
    day_before = (dt.date.fromisoformat(opened_on) - dt.timedelta(days=1)).isoformat()
    at_boundary = [p for p in outgoing_periods if p["period_end"] == day_before]
    return at_boundary[-1].get("read_status") if at_boundary else None


def annual_window(registered_kwh: float, expected_kwh: float, days: int,
                  investigate_below: float | None = None) -> dict:
    """A window of at least ANNUAL_WINDOW_MIN_DAYS: registered over the company's own expectation.

    Returns status not_annual / no_data / unscreened / investigate / ok. The cut is the caller's;
    the module holds none (`_ANNUAL_WINDOW_CUT` is None until §4a sources one).
    """
    if days < ANNUAL_WINDOW_MIN_DAYS:
        return {"status": "not_annual", "ratio": None,
                "message": f"{days} days is not an annual window ({ANNUAL_WINDOW_MIN_DAYS} needed)."}
    if expected_kwh <= 0:
        return {"status": "no_data", "ratio": None, "message": "No expectation to compare against."}
    ratio = registered_kwh / expected_kwh
    cut = investigate_below if investigate_below is not None else _ANNUAL_WINDOW_CUT
    if cut is None:
        return {"status": "unscreened", "ratio": round(ratio, 3),
                "message": (f"Registered use over {days} days is {ratio:.0%} of expected. Not "
                            "classified: no sourced annual cut exists and none was supplied.")}
    if ratio < cut:
        return {"status": "investigate", "ratio": round(ratio, 3),
                "message": (f"Registered use over {days} days is {ratio:.0%} of expected. A year "
                            "is too long for a void and too long for the season to explain; "
                            "investigate under SLC 12A.6 alongside the TRAS score.")}
    return {"status": "ok", "ratio": round(ratio, 3),
            "message": f"Registered use over {days} days is {ratio:.0%} of expected."}
