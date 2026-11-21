"""The GB supplier failures of July 2021 to May 2022, dated, and the SoLR moves they forced.

REUSE: simulation/supplier_failures_2021_22.py
CLASS: CUSTOM
INDEX: searched "supplier failure", "SoLR", "last resort", "failed supplier", "mutualisation",
       "special administration", "transfer". `simulation/policy_costs.py` holds the SoLR levy as a
       COST per MWh and names no failure, no date and no customer. That is the gap this module fills,
       and it does not touch the levy. `simulation/meter_reads.gaining_supplier_first_read` already
       answers "when does the gaining supplier first get an actual read" after a change of supplier.
       The C2 path is that question with a SoLR as the gaining supplier, so it is IMPORTED here. A
       second read model would be a second answer to one question.
       `simulation/market_switching_propensity.published_accounts_millions` is the denominator, read
       from the switching artefact so that one publication gives one count. `simulation/svt_product`
       names the default tariff the moved customer lands on.

WHAT THIS IS
------------
Historical ground truth (CLAUDE.md, "2022 is a fact, not a scenario"). The knowledge page is
`docs/market_research/gb_supplier_failures_and_solr_transfers_2021_22.md`. It covers the 28 firms Ofgem
moved through SoLR between July 2021 and May 2022 (NAO HC 68, §1.13), each with its month of failure
(Oxera for Ofgem, May 2022, Table 3.1), its customers and its SoLR. The customer counts are secondary
figures, accepted only because they reconcile, SoLR by SoLR, with NAO Figure 5. The module's tests hold
that reconciliation. Bulb is a SAR, not a SoLR move, and moves nobody here.

WHAT A WORLD HOUSEHOLD GETS FROM IT
----------------------------------
`solr_transfer_for(household_id, month, arm=...)` answers one question for a household that is NOT
the company's customer: was its supplier one of that month's failures, and if so where did the
household land? A move puts the household on the SoLR's default tariff (NAO Figure 6), with an
opening read the SoLR had to deem unless the customer supplied one. That is account C2's "estimate
after a transfer".

TWO NUMBERS ARE NOT PUBLISHED, SO EACH IS AN ARM, NEVER A PICKED VALUE
------------------------------------------------------------------------
1. The domestic share of the moved customers. NAO gives only the total split: 2.0m domestic, 59k
   non-domestic, 318k unspecified. Arm `lo` counts the 2.0m alone. Arm `hi` counts the 318k
   unspecified as domestic too. Both apply to the firms that were not business-only.
2. The share of moved customers who supplied an opening read: GAP. Arm `lo` returns the opening read
   as `None` with the GAP as its reason. Arm `hi` deems every opening read, which is an upper bound
   on C2 and never an estimate of it.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
- It does not add SoLR moves to the switching rate. Whether DESNZ QEP 2.7.1 counts them as transfers
  is a GAP (knowledge page §"What this means", point 4).
- It does not make the company a SoLR. Whether the company could bid for and win an appointment is a
  supplier capability, and Ofgem's appointment criteria are unread.
- It does not cross the seam. Nothing in `company/` imports it. A household moved here reaches the
  company only through what a real supplier sees: a prospect who arrives later, on whatever tariff
  the world says it is on.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Optional

from simulation.market_switching_propensity import published_accounts_millions
from simulation.meter_reads import gaining_supplier_first_read
from simulation.rng_substream import substream
from simulation.svt_product import SVT_TARIFF_TYPE

DATA_REGIME = "historical"
KNOWLEDGE_PAGE = "docs/market_research/gb_supplier_failures_and_solr_transfers_2021_22.md"

WINDOW = ("2021-07", "2022-05")  # NAO HC 68: "between July 2021 and May 2022"


@dataclass(frozen=True)
class SolrFailure:
    """One failed supplier whose customers Ofgem moved to a SoLR.

    `month` is "YYYY-MM", or None where the record bounds the month without stating it.
    `month_bounds` always holds the first and last month the record allows.
    """
    supplier: str
    month: Optional[str]
    month_bounds: tuple[str, str]
    customers: int          # all customer types; secondary (USE), reconciled to NAO Figure 5
    solr: str
    business_only: bool
    month_source: str


def _f(supplier, month, customers, solr, business_only=False, source="OX Table 3.1"):
    return SolrFailure(supplier, month, (month, month), customers, solr, business_only, source)


# Knowledge page, "The dated list". The order is the record's own.
FAILURES: tuple[SolrFailure, ...] = (
    SolrFailure("Hub Energy", None, ("2021-07", "2021-08"), 15_000, "E.ON Next", False,
                "inside the NAO window and absent from OX's 'since September 2021' table; month GAP"),
    _f("PFP Energy", "2021-09", 82_000, "British Gas"),
    _f("MoneyPlus Energy", "2021-09", 9_000, "British Gas"),
    _f("People's Energy", "2021-09", 350_000, "British Gas"),
    _f("Utility Point", "2021-09", 220_000, "EDF"),
    _f("Avro Energy", "2021-09", 580_000, "Octopus Energy"),
    _f("Green Supplier", "2021-09", 255_000, "Shell Energy"),
    _f("ENSTROGA", "2021-09", 6_000, "E.ON Next"),
    _f("Igloo Energy", "2021-09", 179_000, "E.ON Next"),
    _f("Symbio Energy", "2021-09", 48_000, "E.ON Next"),
    _f("Pure Planet", "2021-10", 235_000, "Shell Energy"),
    _f("Colorado Energy", "2021-10", 15_000, "Shell Energy"),
    _f("Daligas", "2021-10", 9_000, "Shell Energy"),
    _f("GOTO Energy", "2021-10", 22_000, "Shell Energy"),
    _f("Bluegreen Energy Services", "2021-11", 5_900, "British Gas"),
    _f("Omni Energy", "2021-11", 6_000, "Utilita"),
    _f("MA Energy", "2021-11", 300, "SmartestEnergy", business_only=True),
    _f("Zebra Power", "2021-11", 14_800, "British Gas"),
    _f("AmpowerUK", "2021-11", 2_600, "Yü Energy"),
    _f("CNG Energy", "2021-11", 41_000, "Pozitive Energy", business_only=True),
    _f("Neon Reef", "2021-11", 30_000, "British Gas"),
    _f("Social Energy Supply", "2021-11", 5_500, "British Gas"),
    _f("Orbit Energy", "2021-11", 65_000, "Scottish Power"),
    _f("Entice Energy", "2021-11", 5_400, "Scottish Power"),
    _f("Zog Energy", "2021-12", 11_700, "EDF"),
    _f("Together Energy", "2022-01", 176_600, "British Gas"),
    _f("Whoop Energy", "2022-02", 262, "Yü Energy", source="USE, 18 Feb 2022; not in OX"),
    _f("Xcel Power", "2022-02", 270, "Yü Energy", business_only=True,
       source="USE, 18 Feb 2022; not in OX"),
)

# Bulb: special administration, not SoLR (NAO §1.13). Kept beside the list so nobody adds it.
BULB_SAR = {"supplier": "Bulb Energy", "month": "2021-11", "customers_approx": 1_600_000,
            "route": "special administration (SAR), 24 Nov 2021", "moves_anyone_here": False}

# NAO HC 68 §1.13 and note 3, and Figure 5. These are the CHECK the secondary counts must meet.
NAO_SOLR_FIRMS = 28
NAO_BUSINESS_ONLY_FIRMS = 3
NAO_DOMESTIC_CUSTOMERS = 2_000_000
NAO_UNSPECIFIED_CUSTOMERS = 318_000
NAO_FIGURE_5_BY_SOLR = {
    "British Gas": 680_000, "Octopus Energy": 580_000, "Shell Energy": 536_000,
    "E.ON Next": 248_000, "EDF": 232_000, "Scottish Power": 70_000, "Pozitive Energy": 41_000,
    "Utilita": 6_000, "Yü Energy": 3_000, "SmartestEnergy": 300,
}

DOMESTIC_SHARE_ARMS = ("lo", "hi")

# GAP: no source read publishes how many moved customers supplied an opening read.
OPENING_READ_SUPPLIED_SHARE: Optional[float] = None
OPENING_READ_GAP = ("no source read publishes the share of SoLR-moved customers who supplied an "
                    "opening read (knowledge page, Gaps)")


def _mixed_firm_customers() -> int:
    return sum(f.customers for f in FAILURES if not f.business_only)


def domestic_share(arm: str) -> float:
    """Domestic customers over the customers of firms that were not business-only, per arm."""
    if arm not in DOMESTIC_SHARE_ARMS:
        raise ValueError(f"arm {arm!r} is not one of {DOMESTIC_SHARE_ARMS}")
    domestic = NAO_DOMESTIC_CUSTOMERS + (NAO_UNSPECIFIED_CUSTOMERS if arm == "hi" else 0)
    return min(1.0, domestic / _mixed_firm_customers())


def failures_in(month: str) -> tuple[SolrFailure, ...]:
    """The SoLR'd failures dated to `month` ("YYYY-MM"). A failure whose month is a GAP is in none."""
    return tuple(f for f in FAILURES if f.month == month)


def unplaced_failures() -> tuple[SolrFailure, ...]:
    """The failures with only month bounds. They are counted in totals and in no single month."""
    return tuple(f for f in FAILURES if f.month is None)


def solr_move_share(month: str, arm: str) -> float:
    """The chance that a GB domestic account was moved by SoLR in `month`.

    Domestic moves (non-business firms x the arm's domestic share) over the year's published
    domestic electricity accounts. The numerator counts customers of both fuels and the denominator
    counts electricity accounts. That mismatch is declared on the knowledge page and not corrected.
    """
    share = domestic_share(arm)
    moved = sum(f.customers for f in failures_in(month) if not f.business_only) * share
    if not moved:
        return 0.0
    accounts = published_accounts_millions()[int(month[:4])] * 1_000_000
    return moved / accounts


@dataclass(frozen=True)
class SolrTransfer:
    household_id: str
    month: str
    failed_supplier: str
    solr: str
    arrives_on: str
    opening_read: Optional[str]     # "deemed", or None where the GAP leaves it unknown
    opening_read_reason: str
    data_regime: str = DATA_REGIME


def solr_transfer_for(household_id: str, month: str, arm: str,
                      base_seed: int = 0) -> Optional[SolrTransfer]:
    """Whether this non-customer household's supplier failed in `month`, and where it landed.

    One draw from the household's own substream for the month decides membership, at
    `solr_move_share(month, arm)`. A second draw picks the firm, weighted by its non-business
    customers. Under arm `hi` the opening read is deemed, because the SoLR had no read from the
    failed firm (NAO Figure 6, "delays in receiving data"). Under arm `lo` the share who supplied a
    read is a GAP, so the opening read is None and carries the GAP as its reason.
    """
    p = solr_move_share(month, arm)
    if p <= 0.0:
        return None
    rng = substream("solr_transfer", f"{household_id}::{month}", base_seed)
    if rng.random() >= p:
        return None
    firms = [f for f in failures_in(month) if not f.business_only]
    total = sum(f.customers for f in firms)
    pick, acc, chosen = rng.random() * total, 0, firms[-1]
    for f in firms:
        acc += f.customers
        if pick < acc:
            chosen = f
            break
    if arm == "hi":
        read, reason = "deemed", "hi arm: every opening read is deemed (upper bound on C2)"
    elif OPENING_READ_SUPPLIED_SHARE is None:
        read, reason = None, OPENING_READ_GAP
    else:  # pragma: no cover - the share is a GAP today
        supplied = rng.random() < OPENING_READ_SUPPLIED_SHARE
        read, reason = ("customer" if supplied else "deemed"), "drawn at the published share"
    return SolrTransfer(household_id, month, chosen.supplier, chosen.solr,
                        SVT_TARIFF_TYPE, read, reason)


def first_actual_read_after_transfer(transfer: SolrTransfer, meter_type: str,
                                     commodity: str = "electricity") -> Optional[str]:
    """The SoLR's first actual read, from the meter's ordinary cycle (the C2 path).

    The day of the transfer is a GAP, so the move is placed on the month's first day. The first
    period end the read can fall on is then that month's own end, whatever the true day was.
    """
    start = dt.date(int(transfer.month[:4]), int(transfer.month[5:7]), 1).isoformat()
    return gaining_supplier_first_read(transfer.household_id, start, meter_type,
                                       commodity=commodity)
