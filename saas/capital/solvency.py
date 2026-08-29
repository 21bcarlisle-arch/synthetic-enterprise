"""Ofgem per-customer solvency signal (Minimum Capital Requirement).

Ofgem's supply licence Standard Condition 27 requires licensed suppliers to
maintain net assets sufficient to cover obligations to customers. The default
requirement is approximately £130 per dual-fuel customer (the 'MCR target').

The actual MCR is computed from the supplier's gross revenue and customer
obligations, but for our purposes the per-customer net asset floor is the
key signal. When treasury per customer falls below the MCR floor, the company
is in Ofgem compliance stress.

This module computes annual per-customer solvency metrics from settlement data:
- per_customer_net_assets_gbp: treasury / active_customers at year-end
- mcr_floor_gbp: £130/customer (regulatory minimum; MCR target for dual-fuel)
- solvency_ratio: per_customer_net_assets / mcr_floor
- status: OK / Watch / STRESS

The company can observe these values from its own P&L and treasury — no SIM
internals are read here.

WHAT THE £130 IS MULTIPLIED BY (2026-08-29). Every MCR figure this repository publishes is
`£130 × <a count>`, and until this date no caller said which count. Five populations were live
in the published artefacts at once — the founder roster (13), the settled book (167), the
settled book still on supply (127), the AB run's settled book (210), and the commercial book
the campaign won (587) — and the collateral desk was in fact multiplying by a SIXTH that is
none of them: 24, the per-COMMODITY legs of the static roster, which double-counts every
dual-fuel household and cannot see a single funnel win. `mcr_accounts_on_supply` below is the
one named answer, and it returns the selection alongside the number so a reader of the
artefact never has to re-derive it. See
`docs/design/ACCOUNT_POPULATION_CENSUS_2026-08-29.md`.
"""

from __future__ import annotations

from saas.customer_reaction import _billing_account_id
from saas.enterprise_value import ceased_billing_accounts

MCR_FLOOR_GBP_PER_CUSTOMER: float = 130.0
MCR_WATCH_RATIO: float = 2.0
MCR_STRESS_RATIO: float = 1.0

#: The segments Ofgem's per-account capital requirement is levied on. SLC 27's capital
#: adequacy regime is a DOMESTIC supply obligation; a non-domestic account on the same book
#: carries no £130. Kept as a set rather than a `== "resi"` literal so the exclusion is
#: visible at the one place it is decided, and so `mcr_accounts_on_supply` can report the
#: count it excluded rather than silently dropping it.
MCR_DOMESTIC_SEGMENTS: frozenset[str] = frozenset({"resi"})


def mcr_accounts_on_supply(
    settlement_records: list[dict],
    segment_of: dict[str, str],
    as_of: str | None = None,
) -> dict:
    """The population an MCR obligation is levied on, named, with the selection that made it.

    THE SELECTION, in the order it is applied, each leg answering "could this supplier's own
    finance function see it?" — because the MCR is a company-side figure and the test is what
    a real supplier has in front of it, not what the sim knows:

      1. Every DISTINCT BILLING ACCOUNT that has settled to us anywhere in `settlement_records`.
         Records are keyed by per-commodity `customer_id`; a dual-fuel household is ONE account
         and one £130, so the legs are collapsed by `_billing_account_id`. Counting legs is the
         defect this function was written to remove.
      2. Less the accounts we can read as no longer on supply (`ceased_billing_accounts`, the
         supplier's own 35-day continuity reading of its own records). A customer who has gone
         obliges no capital.
      3. Less the accounts whose segment is not in `MCR_DOMESTIC_SEGMENTS`. Reported as
         `non_domestic_on_supply` rather than dropped: an excluded population that cannot be
         counted is how an exclusion scoped by one field hides what it mixes.

    `segment_of` maps per-commodity `customer_id` to segment and is the CALLER's roster — the
    supplier's own customer register, which it plainly has. An account whose legs disagree is
    domestic if ANY leg is, which is the conservative direction: it obliges capital rather than
    waiving it. An account absent from `segment_of` is treated as domestic for the same reason —
    an unclassified account must not fall out of the obligation because we failed to label it.

    Returns the count AND the selection, so the caller publishes the name beside the number::

        {"count": int,
         "population": "domestic billing accounts on supply at <as_of>",
         "selection": <the prose above, one line>,
         "settled_accounts_ever": int,
         "ceased_accounts": int,
         "non_domestic_on_supply": int,
         "as_of": str | None}

    Empty in, zero out, and that is NOT fail-open here: a supplier with no settled record has
    no customer book and owes no MCR, so the free equity a zero produces is the whole of net
    assets — which is the true answer for a supplier that has not started trading. The caller
    that must not accept a zero is the one asserting the book is non-empty, and
    `settled_accounts_ever` is the field it checks.
    """
    accounts: dict[str, set[str]] = {}
    for record in settlement_records:
        accounts.setdefault(_billing_account_id(record["customer_id"]), set()).add(
            record["customer_id"]
        )

    ceased = ceased_billing_accounts(settlement_records, as_of=as_of)
    on_supply = {a: legs for a, legs in accounts.items() if a not in ceased}
    domestic = {
        a
        for a, legs in on_supply.items()
        if any(segment_of.get(leg, "resi") in MCR_DOMESTIC_SEGMENTS for leg in legs)
    }
    return {
        "count": len(domestic),
        "population": f"domestic billing accounts on supply at {as_of or 'the last settled day'}",
        "selection": (
            "distinct billing accounts with a settlement record (dual-fuel legs collapsed), "
            "less those read as ceased on the supplier's own 35-day continuity rule, "
            f"less those whose segment is outside {sorted(MCR_DOMESTIC_SEGMENTS)}"
        ),
        "settled_accounts_ever": len(accounts),
        "ceased_accounts": len(accounts) - len(on_supply),
        "non_domestic_on_supply": len(on_supply) - len(domestic),
        "as_of": as_of,
    }


def compute_solvency_signal(
    treasury_gbp: float,
    active_customer_count: int,
    mcr_floor: float = MCR_FLOOR_GBP_PER_CUSTOMER,
) -> dict:
    """Compute Ofgem solvency signal for a given year-end position.

    Parameters
    ----------
    treasury_gbp : year-end treasury balance (£)
    active_customer_count : number of active accounts at year-end
    mcr_floor : minimum net assets per customer (£); defaults to £130

    Returns
    -------
    dict with keys:
        per_customer_net_assets_gbp: treasury / customers
        mcr_floor_gbp: the regulatory floor per customer
        solvency_ratio: per_customer_net_assets / mcr_floor
        status: 'OK' | 'Watch' | 'STRESS'
    """
    if active_customer_count <= 0:
        return {
            "per_customer_net_assets_gbp": 0.0,
            "mcr_floor_gbp": mcr_floor,
            "solvency_ratio": 0.0,
            "status": "STRESS",
        }

    per_customer = treasury_gbp / active_customer_count
    ratio = per_customer / mcr_floor if mcr_floor > 0 else float("inf")

    if ratio < MCR_STRESS_RATIO:
        status = "STRESS"
    elif ratio < MCR_WATCH_RATIO:
        status = "Watch"
    else:
        status = "OK"

    return {
        "per_customer_net_assets_gbp": round(per_customer, 2),
        "mcr_floor_gbp": mcr_floor,
        "solvency_ratio": round(ratio, 3),
        "status": status,
    }


def compute_solvency_by_year(years_data: dict) -> dict:
    """Compute solvency signal for each year from report data.

    years_data: the 'years' dict from extract_report_data(), each entry
    must contain 'treasury_gbp' and either 'active_customer_count'
    or 'active_customer_ids' (list).
    """
    result: dict = {}
    for year, yd in years_data.items():
        # Support both "treasury_gbp" (clean) and "treasury_end_gbp" (annual report dict key)
        treasury = yd.get("treasury_gbp", yd.get("treasury_end_gbp", 0.0))
        customers = yd.get("active_customer_count", 0)
        if customers == 0:
            customers = len(yd.get("active_customer_ids", []))
        result[year] = compute_solvency_signal(treasury, customers)
    return result
