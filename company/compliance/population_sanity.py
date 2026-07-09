"""Population-level statistical sanity checks -- Phase 5 of
DOMAIN_SENSE_AND_COMPLIANCE.md.

Director's principle 3: depth/frequency/visibility follow risk, and the
harness-side sanity daemon "continuously samples rendered artefacts and
data surfaces against the [invariants] library." These are the population-
level tests named in the doc explicitly: "consumption distributions vs
TDCV, revenue/customer vs cap-implied bands, estimated-read rates vs
industry norms." Per-bill checks already exist (company/billing/
pre_bill_validation.py, Phase 3) -- these are AGGREGATE checks across the
whole population, catching a different class of defect: not "this one bill
is wrong" but "the population as a whole doesn't look like a real UK
energy supplier's book" (e.g. everyone's consumption clustered at exactly
one implausible value, a broken read-generation path producing 0% or 100%
estimated reads, or the population's average unit rate drifting off the
real Ofgem cap band for its year).
"""
from __future__ import annotations

from collections import defaultdict

from company.compliance.domain_invariants import (
    check_resi_consumption_plausible,
    check_unit_rate_plausible,
)


def check_consumption_distribution(bills: list) -> list[dict]:
    """Sum each resi customer's own bills into a real annual total and check
    it against the annual TDCV-derived envelope (domain_invariants.
    RESI_CONSUMPTION_ENVELOPE_*) -- catches a population-level version of
    the R10 C6 class that a single bill's per-period check might miss if
    spread thinly across many small anomalies."""
    by_customer_year: dict[tuple[str, int], float] = defaultdict(float)
    commodity_by_customer: dict[str, str] = {}
    segment_by_customer: dict[str, str] = {}
    for bill in bills:
        if bill.get("segment", "resi") != "resi":
            continue
        cid = bill["customer_id"]
        year = int(bill["period_end"][:4])
        by_customer_year[(cid, year)] += bill.get("total_consumption_kwh", 0.0)
        commodity_by_customer[cid] = bill.get("commodity", "electricity")
        segment_by_customer[cid] = "resi"

    findings = []
    for (cid, year), annual_kwh in by_customer_year.items():
        commodity = commodity_by_customer[cid]
        if not check_resi_consumption_plausible(commodity, annual_kwh):
            findings.append({
                "check": "consumption_distribution_vs_tdcv",
                "customer_id": cid,
                "year": year,
                "detail": f"{cid} ({commodity}, resi) annual consumption {annual_kwh:.0f} kWh "
                          f"in {year} is implausible against the TDCV-derived envelope",
            })
    return findings


def check_unit_rate_bands(bills: list) -> list[dict]:
    """Each resi customer's own average unit rate for a year, checked
    against the real Ofgem-cap-derived plausible band for that year
    (domain_invariants.UNIT_RATE_*_RESI_BY_YEAR) -- catches a population
    drifting off real market pricing (e.g. a pricing bug applying a stale
    or wrong-year rate to everyone)."""
    totals: dict[tuple[str, int], list[float]] = defaultdict(lambda: [0.0, 0.0])
    commodity_by_customer: dict[str, str] = {}
    for bill in bills:
        if bill.get("segment", "resi") != "resi":
            continue
        cid = bill["customer_id"]
        year = int(bill["period_end"][:4])
        kwh = bill.get("total_consumption_kwh", 0.0)
        gbp = bill.get("commodity_amount_gbp", 0.0)
        totals[(cid, year)][0] += gbp
        totals[(cid, year)][1] += kwh
        commodity_by_customer[cid] = bill.get("commodity", "electricity")

    findings = []
    for (cid, year), (gbp, kwh) in totals.items():
        if kwh <= 0:
            continue
        avg_rate_gbp_per_mwh = gbp / (kwh / 1000)
        commodity = commodity_by_customer[cid]
        if not check_unit_rate_plausible(commodity, year, avg_rate_gbp_per_mwh):
            findings.append({
                "check": "unit_rate_vs_cap_band",
                "customer_id": cid,
                "year": year,
                "detail": f"{cid} ({commodity}, resi) average unit rate "
                          f"{avg_rate_gbp_per_mwh:.1f} GBP/MWh in {year} is implausible "
                          f"against the Ofgem-cap-derived band for that year",
            })
    return findings


# Wide sanity bound, not a tight target: catches complete breakage of the
# read-generation path (e.g. a bug making every read estimated, or every
# read actual), not fine-grained drift -- the population's true blended
# rate legitimately varies with its smart/traditional meter mix, which this
# check does not have visibility into per-customer.
_ESTIMATED_READ_RATE_SANITY_BAND = (0.02, 0.85)


def check_estimated_read_rate(meter_read_log: list) -> list[dict]:
    """Population-wide estimated-vs-actual read rate, sanity-bounded
    against simulation/meter_reads.py's own anchored constants (10% smart-
    meter non-communication, ~83% traditional non-actual-read rate) --
    if the whole population somehow shows ~0% or ~100% estimated, the
    read-generation mechanism itself is broken, not just one customer's
    data."""
    if not meter_read_log:
        return []
    estimated = sum(1 for r in meter_read_log if r.get("status") == "estimated")
    rate = estimated / len(meter_read_log)
    low, high = _ESTIMATED_READ_RATE_SANITY_BAND
    if low <= rate <= high:
        return []
    return [{
        "check": "estimated_read_rate_vs_industry_norms",
        "customer_id": None,
        "year": None,
        "detail": f"Population estimated-read rate {rate:.1%} is outside the sanity band "
                  f"[{low:.0%}, {high:.0%}] -- the read-generation mechanism may be broken",
    }]


def run_all_population_checks(bills: list, meter_read_log: list) -> list[dict]:
    """Every population-level check, concatenated. Empty list means clean."""
    findings = []
    findings.extend(check_consumption_distribution(bills))
    findings.extend(check_unit_rate_bands(bills))
    findings.extend(check_estimated_read_rate(meter_read_log))
    return findings
